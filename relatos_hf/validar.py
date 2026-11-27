#!/usr/bin/env python3
"""Revisa los planes: frases «en» presentes en orden en el guion, dibujos y sonidos existentes."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent))
import motor, ilustra, ilustra_mundo, ilustra_obj, ilustra_hd  # noqa
import numpy as np, pro
SONIDOS = set()
r = np.random.default_rng(0)
def sonido_ok(s):
    try:
        return float(abs(pro.sfx(s, 0.5, r)).max()) > 0
    except Exception:
        return False
errores = 0
for f in sorted(motor.PLANES.glob("relato_*.json")):
    n = int(f.stem.split("_")[1]); plan = json.loads(f.read_text())
    _, parrafos = motor.cargar_guion(n)
    pal = [w for _, t in parrafos for w in t.split()]
    normas = [motor.norm(w) for w in pal]; ini = 0
    for tm in plan["tomas"]:
        b = [motor.norm(w) for w in tm["en"].split() if motor.norm(w)]
        idx = next((i for i in range(ini, len(normas) - len(b) + 1) if normas[i:i + len(b)] == b), None)
        if idx is None:
            print(f"{n}: no encuentro «{tm['en']}»"); errores += 1
        else:
            ini = idx + 1
        for c in tm.get("capas", []):
            if c["d"] not in ilustra.DIBUJOS: print(f"{n}: dibujo {c['d']}?"); errores += 1
        for k in ("sfx", "amb"):
            if tm.get(k) and tm[k] != "ninguno" and not sonido_ok(tm[k]): print(f"{n}: sonido {tm[k]}?"); errores += 1
    if plan.get("ambiente") and not sonido_ok(plan["ambiente"]): print(n, "ambiente?")
print("errores:", errores)
