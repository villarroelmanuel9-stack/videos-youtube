#!/usr/bin/env python3
"""
Miniaturas de los relatos: toma un cuadro limpio del proyecto HyperFrames (sin subtítulos ni barra) en la escena
más ilustrada y le pone el titular de la miniatura (campo Canva del guion) y la etiqueta de la serie.

    python3 relatos_hf/miniaturas.py 3 4 5 ...   →  Miniaturas/relato_NNN_<nombre>.jpg
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI))
import generar_textos_historias as GT  # noqa: E402
import motor  # noqa: E402

FUENTE = str(RAIZ / "fuentes" / "Anton-Regular.woff")
W, H = 1080, 1920


def cuadro_limpio(n: int) -> Image.Image:
    proy = motor.PROYECTOS / f"relato_{n:03d}"
    html = (proy / "index.html").read_text(encoding="utf-8")
    plan = json.loads((motor.PLANES / f"relato_{n:03d}.json").read_text(encoding="utf-8"))
    inicios = [float(x) for x in re.findall(r'class="clip toma" data-start="([0-9.]+)"', html)]
    duraciones = [float(x) for x in re.findall(r'class="clip toma" data-start="[0-9.]+" data-duration="([0-9.]+)"', html)]
    elegida = plan.get("miniatura")
    if elegida is None:  # la escena con más capas dibujadas (la más rica visualmente), sin contar el cierre
        cands = [(len(tm.get("capas", [])), -k, k) for k, tm in enumerate(plan["tomas"][:-1]) if tm["tipo"] in ("escena", "mapa")]
        elegida = max(cands)[2] if cands else 0
    t = inicios[elegida] + duraciones[elegida] * 0.7
    tmp = proy.parent / f"_min_{n:03d}"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(proy, tmp, ignore=shutil.ignore_patterns("*.wav", ".hyperframes"))
    limpio = re.sub(r'<div id="capsHost".*?</div>\n</div>', '<div id="capsHost" data-track-kind="captions"></div>', html, flags=re.S)
    limpio = limpio.replace('<div id="hud"', '<div style="display:none" id="hud"')
    limpio = re.sub(r'<div id="t\d+d" class="dato[^>]*>.*?</div></div>', "", limpio)
    limpio = re.sub(r'<div id="t\d+tx" class="bloque".*?</div></div>', "", limpio)
    limpio = re.sub(r'<audio[^>]*></audio>', "", limpio)
    (tmp / "index.html").write_text(limpio, encoding="utf-8")
    salida = tmp / "snap"
    subprocess.run(["npx", "--yes", motor.HF, "snapshot", "--at", f"{t:.2f}", "-o", str(salida)], cwd=tmp, check=True,
                   capture_output=True, env={**__import__("os").environ, "DO_NOT_TRACK": "1"})
    png = sorted(salida.glob("frame-*.png"))[0]
    img = Image.open(png).convert("RGB").resize((W, H))
    shutil.rmtree(tmp)
    return img


def ajustar(draw, txt, ancho, tam_max, tam_min=90):
    tam = tam_max
    while tam > tam_min:
        f = ImageFont.truetype(FUENTE, tam)
        if draw.textlength(txt, font=f) <= ancho:
            return f, [txt]
        tam -= 6
    palabras = txt.split()
    mitad = max(1, len(palabras) // 2)
    lineas = [" ".join(palabras[:mitad]), " ".join(palabras[mitad:])]
    tam = tam_max
    while tam > 70:
        f = ImageFont.truetype(FUENTE, tam)
        if max(draw.textlength(l, font=f) for l in lineas) <= ancho:
            return f, lineas
        tam -= 6
    return ImageFont.truetype(FUENTE, 70), lineas


def miniatura(n: int):
    guiones = GT.cargar()
    g = guiones[n]
    if (RAIZ / "Miniaturas" / f"{GT.nombre_video(n, g['nombre'])}.jpg").exists():
        print("ya hay miniatura (hecha por el usuario):", n)
        return
    etiqueta, _ = GT.categoria(n)
    titular = (g["canva"] or g["nombre"]).strip("«»\"").upper()
    img = cuadro_limpio(n)
    from PIL import ImageEnhance
    img = ImageEnhance.Color(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for y in range(700):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(235 * (1 - y / 700) ** 1.2)))
    for y in range(1350, H):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(200 * ((y - 1350) / (H - 1350)) ** 1.1)))
    img = Image.alpha_composite(img.convert("RGBA"), capa)
    d = ImageDraw.Draw(img)
    color = ["#FFD21F", "#FFFFFF", "#FF8A1F", "#FFD21F"][n % 4]
    f, lineas = ajustar(d, titular, 990, 220)
    y = 120
    for ln in lineas:
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y), ln, font=f, fill=color, stroke_width=12, stroke_fill="black")
        y += int(f.size * 1.05)
    d.rectangle([(W - 760) / 2, y + 22, (W + 760) / 2, y + 38], fill="#E3141B")
    fe = ImageFont.truetype(FUENTE, 78)
    w = d.textlength(etiqueta, font=fe)
    x0, y0 = (W - w) / 2 - 34, 1560
    d.rounded_rectangle([x0, y0, x0 + w + 68, y0 + 118], radius=22, fill="#E3141B", outline="black", width=6)
    d.text((x0 + 34, y0 + 12), etiqueta, font=fe, fill="white", stroke_width=3, stroke_fill="black")
    fh = ImageFont.truetype(FUENTE, 44)
    w = d.textlength("@1MRELATO", font=fh)
    d.text(((W - w) / 2, y0 + 140), "@1MRELATO", font=fh, fill="white", stroke_width=3, stroke_fill="black")
    destino = RAIZ / "Miniaturas" / f"{GT.nombre_video(n, g['nombre'])}.jpg"
    img.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2, percent=60)).save(destino, quality=90)
    print("→", destino.name)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        miniatura(int(a))
