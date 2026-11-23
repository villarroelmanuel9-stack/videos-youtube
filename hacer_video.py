#!/usr/bin/env python3
"""
Genera cualquier historia en estilo caricatura (incluye las escenas de escenas_extra.py).

    python hacer_video.py historias/historia_05_guerra_de_los_emus.json --audio audios/historia_05_voz.mp3 --sin-audio
"""
import argparse
from pathlib import Path

import caricatura
import escenas_extra  # noqa: F401  (registra las escenas h4..h10)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--audio")
    ap.add_argument("--sin-audio", action="store_true")
    a = ap.parse_args()
    caricatura.generar(Path(a.json), a.audio, a.sin_audio)
