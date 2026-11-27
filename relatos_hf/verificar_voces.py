#!/usr/bin/env python3
"""Transcribe cada audio de «voces nuevas» y lo compara con su guion: detecta audios cambiados o cortados."""
import difflib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent))
import motor
CARPETA = motor.RAIZ / "voces nuevas"
res = {}
for f in sorted(CARPETA.glob("relato_*.mp3")):
    n = int(f.stem.split("_")[1])
    _, parrafos = motor.cargar_guion(n)
    guion = [motor.norm(w) for _, t in parrafos for w in t.split()]
    oido = [motor.norm(w) for w, _, _ in motor.oidas(f)]
    sim = difflib.SequenceMatcher(None, guion, oido, autojunk=False).ratio()
    fin = difflib.SequenceMatcher(None, guion[-8:], oido[-10:], autojunk=False).ratio()
    dur = oido and motor.oidas(f)[-1][2]
    res[n] = dict(similitud=round(sim, 3), final=round(fin, 2), duracion=round(dur, 1), tono=round(motor.tono_medio(f)))
    print(n, res[n], flush=True)
(CARPETA / "verificacion.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
