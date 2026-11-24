#!/usr/bin/env python3
"""
Rehace SOLO el audio de videos ya generados con la mezcla nueva (voz siempre por encima de los efectos).
No vuelve a dibujar los fotogramas: copia el video tal cual y reemplaza la pista de audio.

    python remezclar.py            # todos
    python remezclar.py 5 13 17    # algunos
"""
from __future__ import annotations

import glob
import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import cine
from cine import SR, alinear_audio, escribir_wav, leer_wav

RAIZ = Path(__file__).resolve().parent


def _voz_wav(audio, tmp):
    w = tmp / "voz.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio, "-ar", str(SR), "-ac", "2", str(w)],
                   check=True)
    return leer_wav(w)


def _cortes(escenas):
    return [e["inicio"] for e in escenas[1:]]


def mezcla_cine(cfg, audio, tmp):
    escenas = alinear_audio(audio, cfg["escenas"])
    total = escenas[-1]["inicio"] + escenas[-1]["dur"] + 0.6
    golpes = []
    for e in escenas:
        if e.get("visual") == "barcos":
            golpes += [(e["inicio"] + td, 1.0) for td in cine.DISPAROS if td < e["dur"]]
            golpes += [(e["inicio"] + td + 0.6, 0.5) for td in cine.DISPAROS if td < e["dur"]]
    return cine.disenar_sonido(_voz_wav(audio, tmp), _cortes(escenas), golpes, total)


def mezcla_caricatura(cfg, audio, tmp):
    escenas = alinear_audio(audio, cfg["escenas"])
    escenas[-1]["dur"] += 2.0
    total = escenas[-1]["inicio"] + escenas[-1]["dur"]
    return cine.disenar_sonido(_voz_wav(audio, tmp), _cortes(escenas), [], total)


def mezcla_dinos(cfg, audio, tmp):
    import dinos
    escenas = alinear_audio(audio, cfg["escenas"])
    escenas[-1]["dur"] += 1.8
    total = escenas[-1]["inicio"] + escenas[-1]["dur"]
    eventos = []
    for e in escenas:
        o = dinos.ESCENAS_DINO[e["visual"]]()
        o.palabras = e["palabras"]
        if e["visual"] == "dino_1":
            eventos.append((e["inicio"] + 0.15, "rugido"))
        if e["visual"] == "dino_2":
            eventos.append((e["inicio"] + o.tp("rex", 0.5, e["dur"]) + 0.05, "rugido"))
        if e["visual"] == "dino_6":
            eventos.append((e["inicio"], "retumbo"))
        if e["visual"] == "dino_7":
            eventos.append((e["inicio"], "impacto"))
    return dinos.disenar_sonido(_voz_wav(audio, tmp), _cortes(escenas), eventos, total)


def mezcla_escenas(cfg, audio, tmp, escenas_dict, cola, mezclador, **kw):
    escenas = alinear_audio(audio, cfg["escenas"])
    escenas[-1]["dur"] += cola
    total = escenas[-1]["inicio"] + escenas[-1]["dur"]
    eventos = []
    for e in escenas:
        o = escenas_dict[e["visual"]]()
        o.palabras = e["palabras"]
        eventos += [(e["inicio"] + t0, tipo, d) for t0, tipo, d in o.sonidos(e["dur"])]
    return mezclador(_voz_wav(audio, tmp), _cortes(escenas), eventos, total, **kw)


def mezcla_alcatraz(cfg, audio, tmp):
    import alcatraz
    return mezcla_escenas(cfg, audio, tmp, alcatraz.ESCENAS_ALC, 1.8, alcatraz.mezclar)


PRO = {13: ("cooper", (49, 73.4, 98)), 14: ("mineros", (49, 73.4, 98)), 15: ("andes", (55, 65.4, 82.4)),
       16: ("juliane", (52, 78, 104)), 17: ("tregua", (65.4, 98, 130.8))}


def mezcla_pro(n):
    def f(cfg, audio, tmp):
        import pro
        mod = importlib.import_module(PRO[n][0])
        return mezcla_escenas(cfg, audio, tmp, mod.ESCENAS, 1.9, pro.mezclar, pad_hz=PRO[n][1])
    return f


def video_de(n):
    j = glob.glob(str(RAIZ / f"historias/historia_{n:02d}_*.json"))[0]
    stem = Path(j).stem
    for suf in ("_pro", "_caricatura", "_cine"):
        v = RAIZ / "salida" / f"{stem}{suf}.mp4"
        if v.exists():
            return j, v, suf
    raise FileNotFoundError(stem)


def remezclar(n):
    j, video, suf = video_de(n)
    audio = str(RAIZ / f"audios/historia_{n:02d}_voz.mp3")
    cfg = json.loads(Path(j).read_text(encoding="utf-8"))
    if n >= 13:
        fn = mezcla_pro(n)
    elif n == 12:
        fn = mezcla_alcatraz
    elif n == 11:
        fn = mezcla_dinos
    elif suf == "_cine":
        fn = mezcla_cine
    else:
        fn = mezcla_caricatura
    if n >= 4 and n <= 10:
        import escenas_extra  # noqa: F401  (registra escenas h4..h10, no afecta al audio)
    print(f"▶ historia {n}: {video.name}")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        mezcla = fn(cfg, audio, tmp)
        escribir_wav(tmp / "mezcla.wav", mezcla)
        salida = tmp / "nuevo.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(tmp / "mezcla.wav"),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                        "-movflags", "+faststart", str(salida)], check=True)
        salida.replace(video)
    print(f"   ✔ {video}")


if __name__ == "__main__":
    numeros = [int(x) for x in sys.argv[1:]] or list(range(1, 18))
    for n in numeros:
        remezclar(n)
