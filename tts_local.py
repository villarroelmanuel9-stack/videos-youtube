#!/usr/bin/env python3
"""
TTS local con clonación de voz (Chatterbox Multilingual, licencia MIT, sin costo por carácter).

Uso (con el entorno /root/tts_env):
    /root/tts_env/bin/python tts_local.py referencia          # arma la voz de referencia desde voz/mi_voz/
    /root/tts_env/bin/python tts_local.py 1 2 3               # genera relato_001.mp3, ... en audios/relatos/
    /root/tts_env/bin/python tts_local.py todos               # los 100 (salta los que ya existen)

Cada párrafo del guion se genera por separado con la emoción de su etiqueta ([tenso], [cercano]...) y se une con
pausas cortas. Al final informa la duración: la meta es ≈44 s de voz para que el video dure 45–46 s.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent
CARPETA_VOZ = RAIZ / "voz" / "mi_voz"
REFERENCIA = RAIZ / "voz" / "referencia.wav"
SALIDA = RAIZ / "audios" / "relatos"
GUION = RAIZ / "guiones" / "historias_100.md"

# Etiqueta de emoción → (exaggeration, cfg_weight, pausa después en segundos)
EMOCION = {
    "narrador": (0.45, 0.5, 0.30), "cercano": (0.50, 0.5, 0.25), "intrigante": (0.55, 0.45, 0.35),
    "misterioso": (0.55, 0.45, 0.40), "tenso": (0.65, 0.4, 0.35), "sorprendido": (0.70, 0.4, 0.30),
    "susurrando": (0.40, 0.5, 0.40),
}


def leer(ruta: Path, sr: int) -> np.ndarray:
    crudo = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(ruta), "-ac", "1", "-ar", str(sr), "-f",
                            "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(crudo, np.float32).copy()


def armar_referencia(sr: int = 24000) -> Path:
    """Une las grabaciones, quita silencios largos, normaliza y elige el mejor tramo continuo de ~12 s."""
    archivos = sorted(p for p in CARPETA_VOZ.iterdir() if p.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg",
                                                                               ".aac", ".flac", ".opus", ".webm"})
    if not archivos:
        sys.exit(f"No hay grabaciones en {CARPETA_VOZ}")
    tramos = []
    for p in archivos:
        x = leer(p, sr)
        x = x - x.mean()
        win = int(0.05 * sr)
        energia = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same"))
        umbral = max(1e-4, np.percentile(energia, 95) * 0.08)
        voz = energia > umbral
        # mantiene la voz y silencios de hasta 0,3 s
        idx = np.flatnonzero(voz)
        if not len(idx):
            continue
        keep = np.zeros_like(voz)
        for a, b in zip(idx[:-1], idx[1:]):
            keep[a] = True
            if b - a <= int(0.3 * sr):
                keep[a:b] = True
        keep[idx[-1]] = True
        tramos.append(x[keep])
    todo = np.concatenate(tramos)
    todo = todo / (np.max(np.abs(todo)) + 1e-9) * 0.9
    largo = min(len(todo), 12 * sr)
    # el tramo de 12 s con más voz estable
    paso = sr // 2
    mejor, mejor_v = 0, -1
    for i in range(0, max(1, len(todo) - largo), paso):
        seg = todo[i:i + largo]
        v = np.mean(np.abs(seg) > 0.02)
        if v > mejor_v:
            mejor, mejor_v = i, v
    ref = todo[mejor:mejor + largo]
    REFERENCIA.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(ref, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                    str(REFERENCIA)], input=pcm, check=True)
    print(f"Referencia: {REFERENCIA} ({len(ref) / sr:.1f} s de {len(archivos)} grabaciones)")
    return REFERENCIA


def guiones() -> dict[int, list[tuple[str, str]]]:
    txt = GUION.read_text(encoding="utf-8")
    out = {}
    for n, cuerpo in re.findall(r"\n## (\d+) · .*?\n```\n(.*?)```", txt, re.S):
        lineas = []
        for ln in cuerpo.strip().splitlines():
            m = re.match(r"\[([^\]]+)\]\s*(.*)", ln.strip())
            if m:
                lineas.append((m.group(1).strip().lower(), m.group(2).strip()))
        out[int(n)] = lineas
    return out


def generar(nums: list[int]):
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    if not REFERENCIA.exists():
        armar_referencia()
    torch.set_num_threads(4)
    modelo = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    sr = modelo.sr
    todos = guiones()
    SALIDA.mkdir(parents=True, exist_ok=True)
    for n in nums:
        destino = SALIDA / f"relato_{n:03d}.mp3"
        if destino.exists():
            print(f"{destino.name}: ya existe")
            continue
        partes = []
        for emocion, texto in todos[n]:
            exa, cfg, pausa = EMOCION.get(emocion, EMOCION["narrador"])
            wav = modelo.generate(texto, language_id="es", audio_prompt_path=str(REFERENCIA), exaggeration=exa,
                                  cfg_weight=cfg)
            partes.append(wav.squeeze(0).cpu().numpy())
            partes.append(np.zeros(int(pausa * sr), np.float32))
        audio = np.concatenate(partes[:-1])
        audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.89
        pcm = (audio * 32767).astype(np.int16).tobytes()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", str(destino)],
                       input=pcm, check=True)
        print(f"{destino.name}: {len(audio) / sr:.1f} s", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "referencia":
        armar_referencia()
    elif args[0] == "todos":
        generar(sorted(guiones()))
    else:
        generar([int(a) for a in args])
