#!/usr/bin/env python3
"""
Verifica los audios de los misterios:
  * transcribe cada archivo (faster-whisper, con caché),
  * identifica a qué misterio corresponde comparando con los 100 guiones,
  * mide cobertura (palabras del guion presentes), duración y si falta el final,
  * copia cada audio a audios/misterios/misterio_NN_voz.mp3,
  * escribe guiones/verificacion_misterios.md con una tabla corta.
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent
ORIGEN = RAIZ / "audios"
DESTINO = RAIZ / "audios" / "misterios"


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9ñ]+", s)


def cargar_guiones():
    txt = (RAIZ / "guiones" / "misterios_100.md").read_text(encoding="utf-8")
    bloques = re.split(r"\n## (\d+) · ", txt)[1:]
    out = {}
    for i in range(0, len(bloques), 2):
        n, cuerpo = int(bloques[i]), bloques[i + 1]
        nombre = cuerpo.split("\n", 1)[0].strip()
        voz = re.search(r"```\n(.*?)```", cuerpo, re.S).group(1).strip()
        parrafos = [re.sub(r"\[[^\]]*\]\s*", "", p).strip() for p in voz.split("\n") if p.strip()]
        campo = lambda k: (re.search(rf"\*\*{k}:\*\* (.*)", cuerpo) or [None, ""])[1].strip()
        m_linea = campo("M")
        escena, canva = (m_linea.split(" · **Canva:** ") + [""])[:2]
        out[n] = dict(n=n, nombre=nombre, voz=voz, parrafos=parrafos, titulo=campo("T"), desc=campo("D"),
                      escena=escena.strip(), canva=canva.strip().strip('"'))
    return out


def transcribir(ruta: Path, modelo):
    cache = Path(str(ruta) + ".palabras.json")
    if cache.exists():
        return [tuple(x) for x in json.loads(cache.read_text(encoding="utf-8"))]
    crudo = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(ruta), "-ac", "1", "-ar", "16000", "-f", "f32le",
                            "-"], capture_output=True, check=True).stdout
    segs, _ = modelo.transcribe(np.frombuffer(crudo, np.float32), language="es", word_timestamps=True)
    oidas = [(w.word.strip(), float(w.start), float(w.end)) for sg in segs for w in sg.words]
    cache.write_text(json.dumps(oidas, ensure_ascii=False), encoding="utf-8")
    return oidas


def duracion(ruta):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(ruta)], capture_output=True, text=True).stdout.strip())


def main():
    from faster_whisper import WhisperModel
    guiones = cargar_guiones()
    gw = {n: norm(" ".join(g["parrafos"])) for n, g in guiones.items()}
    modelo = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
    archivos = sorted(p for p in ORIGEN.iterdir() if p.suffix.lower() in (".mp3", ".wav", ".m4a")
                      and not p.name.startswith("historia_"))
    DESTINO.mkdir(parents=True, exist_ok=True)
    resultados = []
    for i, a in enumerate(archivos, 1):
        oidas = transcribir(a, modelo)
        ow = norm(" ".join(w for w, _, _ in oidas))
        puntajes = sorted(((difflib.SequenceMatcher(None, gw[n], ow, autojunk=False).ratio(), n) for n in gw),
                          reverse=True)
        r, n = puntajes[0]
        sm = difflib.SequenceMatcher(None, gw[n], ow, autojunk=False)
        cubiertas = sum(b.size for b in sm.get_matching_blocks())
        cobertura = cubiertas / max(1, len(gw[n]))
        final_ok = "inventadas" in ow[-25:] or "reales" in ow[-12:] or "suscribete" in ow[-15:]
        dur = duracion(a)
        resultados.append(dict(archivo=a.name, n=n, sim=round(r, 3), segundo=puntajes[1][1], cobertura=round(cobertura, 3),
                               final_ok=final_ok, dur=round(dur, 1)))
        print(f"{i:3d}/{len(archivos)} {a.name[:30]:30s} → {n:3d} {guiones[n]['nombre'][:28]:28s} "
              f"sim {r:.2f} cob {cobertura:.2f} {dur:5.1f}s", flush=True)
    # duplicados y faltantes
    por_n = {}
    for r in resultados:
        por_n.setdefault(r["n"], []).append(r)
    faltan = [n for n in guiones if n not in por_n]
    filas = ["| # | Misterio | Archivo original | Duración | Cobertura | Estado |", "|---|---|---|---|---|---|"]
    for n in sorted(por_n):
        mejor = max(por_n[n], key=lambda r: r["cobertura"])
        estado = "OK"
        if mejor["cobertura"] < 0.85:
            estado = "⚠ incompleto o con cambios"
        elif not mejor["final_ok"]:
            estado = "⚠ falta el final"
        if len(por_n[n]) > 1:
            estado += f" · duplicado ({len(por_n[n])})"
        shutil.copy2(ORIGEN / mejor["archivo"], DESTINO / f"misterio_{n:02d}_voz.mp3")
        cache = ORIGEN / (mejor["archivo"] + ".palabras.json")
        if cache.exists():
            shutil.copy2(cache, DESTINO / f"misterio_{n:02d}_voz.mp3.palabras.json")
        filas.append(f"| {n:02d} | {guiones[n]['nombre']} | {mejor['archivo']} | {mejor['dur']} s | "
                     f"{int(mejor['cobertura'] * 100)} % | {estado} |")
    resumen = [f"# Verificación de audios de misterios", "",
               f"- Audios recibidos: **{len(resultados)}**",
               f"- Misterios identificados: **{len(por_n)}**",
               f"- Faltan: **{', '.join(f'{n:02d} ({guiones[n][chr(110)+chr(111)+chr(109)+chr(98)+chr(114)+chr(101)]})' for n in faltan) or 'ninguno'}**",
               ""] + filas
    (RAIZ / "guiones" / "verificacion_misterios.md").write_text("\n".join(resumen) + "\n", encoding="utf-8")
    json.dump(resultados, open(RAIZ / "guiones" / "verificacion_misterios.json", "w"), ensure_ascii=False, indent=1)
    print("FALTAN:", faltan)


if __name__ == "__main__":
    main()
