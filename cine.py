#!/usr/bin/env python3
"""
Generador de Shorts con look de CINE: escenas ilustradas por código (siluetas,
luces, humo, fuego), movimientos de cámara, grano de película, viñeta,
subtítulos elegantes con sombra (blanco + palabra clave dorada), transiciones
con zoom y diseño de sonido (ambiente, whooshes, cañonazos).

Uso:
    python cine.py historias/historia_01_guerra_mas_corta.json
    python cine.py historias/historia_01_guerra_mas_corta.json --audio mi_voz.mp3

Con --audio usa TU narración (un solo archivo con toda la historia); los
tiempos de cada escena se reparten según la cantidad de texto.

Cada escena del JSON necesita un campo "visual" con uno de:
    reloj, ciudad, palacio, barcos, ruinas, monedas, espacio
y opcional "etiqueta" (texto del recuadro de arriba, ej. "ZANZÍBAR · 1896").
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from generar_short import (FPS, H, W, Palabra, agrupar_palabras, duracion_audio,
                           narrar, tiempos_estimados, _primera_existente)

RAIZ = Path(__file__).resolve().parent
FUENTES = [str(RAIZ / "fuentes" / "texto.ttf"), str(RAIZ / "fuentes" / "texto.otf"),
           "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
           "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]
_fcache: dict[int, ImageFont.FreeTypeFont] = {}


def fuente(t: int):
    if t not in _fcache:
        r = _primera_existente(FUENTES)
        _fcache[t] = ImageFont.truetype(r, t) if r else ImageFont.load_default(t)
    return _fcache[t]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def vgrad(paradas, w=W, h=H) -> Image.Image:
    """Degradado vertical. paradas = [(0..1, '#hex'), ...]"""
    ys = np.linspace(0, 1, h)
    pos = [p for p, _ in paradas]
    cols = np.array([rgb(c) for _, c in paradas], float)
    col = np.stack([np.interp(ys, pos, cols[:, i]) for i in range(3)], 1)
    arr = np.repeat(col[:, None, :], w, 1).astype(np.uint8)
    return Image.fromarray(arr).convert("RGBA")


def radial(c_centro, c_borde, cx, cy, radio) -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.clip(np.hypot(xx - cx, yy - cy) / radio, 0, 1)[..., None]
    a, b = np.array(rgb(c_centro), float), np.array(rgb(c_borde), float)
    return Image.fromarray((a * (1 - d) + b * d).astype(np.uint8)).convert("RGBA")


_glows: dict = {}


def glow(radio, color, fuerza=1.0) -> Image.Image:
    k = (radio, color, fuerza)
    if k not in _glows:
        n = radio * 2
        yy, xx = np.mgrid[0:n, 0:n]
        d = np.clip(np.hypot(xx - radio, yy - radio) / radio, 0, 1)
        a = ((1 - d) ** 2.2 * 255 * fuerza).clip(0, 255).astype(np.uint8)
        arr = np.zeros((n, n, 4), np.uint8)
        arr[..., :3] = rgb(color)
        arr[..., 3] = a
        _glows[k] = Image.fromarray(arr, "RGBA")
    return _glows[k]


def pegar_glow(img, x, y, radio, color, fuerza=1.0):
    radio = int(radio)
    if radio < 2 or fuerza <= 0:
        return
    g = glow(radio, color, round(min(fuerza, 1.0), 2))
    x0, y0 = int(x - radio), int(y - radio)
    sx, sy = max(0, -x0), max(0, -y0)
    ex, ey = min(g.width, img.width - x0), min(g.height, img.height - y0)
    if ex <= sx or ey <= sy:
        return
    img.alpha_composite(g, (x0 + sx, y0 + sy), (sx, sy, ex, ey))


def particulas(seed, n, t, vel=(-20, 20), vy=(-40, -10), zona=(0, 0, W, H)):
    r = random.Random(seed)
    x0, y0, x1, y1 = zona
    out = []
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        vx, vvy = r.uniform(*vel), r.uniform(*vy)
        f = r.uniform(0, 6.28)
        out.append(((x + vx * t + 15 * math.sin(t + f) - x0) % (x1 - x0) + x0,
                    (y + vvy * t - y0) % (y1 - y0) + y0, f, r.random()))
    return out


# =========================================================================== #
# ESCENAS ILUSTRADAS: cada una tiene una parte fija (cache) y una animada
# =========================================================================== #
class EscenaReloj:
    camara = "acercar"

    def __init__(self):
        self.cx, self.cy, self.R = 540, 860, 300
        img = radial("#3a2610", "#050403", self.cx, self.cy, 1100)
        pegar_glow(img, self.cx, self.cy, 560, "#e0a040", 0.55)
        d = ImageDraw.Draw(img)
        cx, cy, R = self.cx, self.cy, self.R
        d.rectangle((cx - 34, cy - R - 120, cx + 34, cy - R - 30), fill=rgb("#c8973a"))
        d.ellipse((cx - 55, cy - R - 190, cx + 55, cy - R - 90), outline=rgb("#d9a647"), width=18)
        for ang in (-45, 45):
            a = math.radians(ang - 90)
            bx, by = cx + (R + 40) * math.cos(a), cy + (R + 40) * math.sin(a)
            d.ellipse((bx - 34, by - 34, bx + 34, by + 34), fill=rgb("#b2832e"))
        for r_, c in ((R + 46, "#5e4114"), (R + 36, "#f0c35a"), (R + 22, "#a77a2a"), (R + 6, "#3b2a12"),
                      (R, "#efe3c4")):
            d.ellipse((cx - r_, cy - r_, cx + r_, cy + r_), fill=rgb(c))
        # sombreado interior de la esfera
        sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ds = ImageDraw.Draw(sombra)
        ds.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(60, 40, 10, 130), width=40)
        img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(25)))
        d = ImageDraw.Draw(img)
        for i in range(60):
            a = math.radians(i * 6 - 90)
            largo = 38 if i % 5 == 0 else 16
            ancho = 8 if i % 5 == 0 else 3
            d.line((cx + (R - 14 - largo) * math.cos(a), cy + (R - 14 - largo) * math.sin(a),
                    cx + (R - 14) * math.cos(a), cy + (R - 14) * math.sin(a)), fill=rgb("#2a1d0e"), width=ancho)
        for n, ang in ((60, -90), (15, 0), (30, 90), (45, 180)):
            a = math.radians(ang)
            tx, ty = cx + (R - 95) * math.cos(a), cy + (R - 95) * math.sin(a)
            f = fuente(54)
            s = str(n)
            d.text((tx - d.textlength(s, font=f) / 2, ty - 32), s, font=f, fill=rgb("#2a1d0e"))
        brillo = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(brillo).chord((cx - R + 20, cy - R + 20, cx + R - 20, cy + R - 20), 200, 300,
                                     fill=(255, 255, 255, 60))
        img.alpha_composite(brillo.filter(ImageFilter.GaussianBlur(6)))
        self.base = img

    def frame(self, t, dur):
        img = self.base.copy()
        d = ImageDraw.Draw(img)
        cx, cy, R = self.cx, self.cy, self.R
        a = t * 2 * math.pi / 1.6 - math.pi / 2
        m = t * 2 * math.pi / 20 - math.pi / 2
        d.line((cx, cy, cx + (R - 110) * math.cos(m), cy + (R - 110) * math.sin(m)), fill=rgb("#2a1d0e"), width=14)
        d.line((cx - 60 * math.cos(a), cy - 60 * math.sin(a), cx + (R - 30) * math.cos(a),
                cy + (R - 30) * math.sin(a)), fill=rgb("#b3141b"), width=7)
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=rgb("#c8973a"))
        for x, y, f, k in particulas(1, 40, t, zona=(0, 200, W, 1700)):
            pegar_glow(img, x, y, 6 + 6 * k, "#ffd890", 0.5 + 0.3 * math.sin(t * 2 + f))
        return img


class EscenaCiudad:
    camara = "paneo"

    def __init__(self):
        hz = 1190
        img = vgrad([(0, "#120c2e"), (.35, "#4a1d4f"), (.55, "#c2412c"), (.62, "#f39a45"), (.621, "#3a1f2a"),
                     (1, "#06101a")])
        pegar_glow(img, 760, hz - 40, 520, "#ff9a3c", 0.7)
        d = ImageDraw.Draw(img)
        d.ellipse((760 - 110, hz - 150, 760 + 110, hz + 70), fill=rgb("#ffd38a"))
        d.rectangle((0, hz, W, H), fill=None)
        img.alpha_composite(vgrad([(0, "#3a1f2a"), (1, "#06101a")], W, H - hz), (0, hz))
        d = ImageDraw.Draw(img)
        r = random.Random(4)
        sil = rgb("#170b1c")
        x = -20
        while x < 700:
            w_, h_ = r.randint(50, 130), r.randint(60, 230)
            d.rectangle((x, hz - h_, x + w_, hz + 4), fill=sil)
            if r.random() < 0.35:
                d.pieslice((x + 5, hz - h_ - w_ // 2, x + w_ - 5, hz - h_ + w_ // 2), 180, 360, fill=sil)
            for _ in range(r.randint(0, 4)):
                wx, wy = r.randint(x + 6, x + w_ - 14), r.randint(hz - h_ + 12, hz - 20)
                d.rectangle((wx, wy, wx + 8, wy + 12), fill=rgb("#ffb14d"))
            x += w_ - r.randint(0, 20)
        d.rectangle((300, hz - 360, 330, hz), fill=sil)
        d.pieslice((290, hz - 400, 340, hz - 340), 180, 360, fill=sil)
        for px in (80, 520, 640):
            self._palmera(d, px, hz, r.uniform(-0.3, 0.3), sil)
        d.polygon([(820, hz + 2), (900, hz - 40), (1000, hz - 55), (1080, hz - 30), (1080, hz + 2)], fill=sil)
        for _ in range(60):
            sx, sy = r.randint(0, W), r.randint(0, 600)
            d.point((sx, sy), fill=(255, 230, 220))
        self.base, self.hz = img, hz

    @staticmethod
    def _palmera(d, x, base, curva, c):
        pts = [(x + curva * 60 * (i / 10) ** 2 * 3, base - i * 26) for i in range(11)]
        d.line(pts, fill=c, width=12)
        tx, ty = pts[-1]
        for ang in range(0, 360, 40):
            a = math.radians(ang)
            ex, ey = tx + 110 * math.cos(a), ty + 45 * math.sin(a) + 25
            d.line([(tx, ty), ((tx + ex) / 2, ty - 25), (ex, ey)], fill=c, width=9)

    def frame(self, t, dur):
        img = self.base.copy()
        d = ImageDraw.Draw(img)
        hz = self.hz
        for i, y in enumerate(range(hz + 8, 1750, 16)):
            ancho = max(10, 170 - (y - hz) * 0.12) * (0.7 + 0.3 * math.sin(t * 3 + i))
            x = 760 + 25 * math.sin(t * 1.5 + i * 0.7)
            d.rounded_rectangle((x - ancho, y, x + ancho, y + 5), 3, fill=(255, 190, 115, 150))
        for k, (bx, by, s) in enumerate(((180, 1420, 1.3), (600, 1300, 0.8), (900, 1600, 1.7))):
            y = by + 8 * math.sin(t * 1.6 + k)
            x = bx + 12 * t
            self._dhow(d, x, y, s, 0.04 * math.sin(t * 1.6 + k + 1))
        for k in range(5):
            x = (100 + k * 70 + t * 60) % (W + 200) - 100
            y = 520 + k * 25 + 10 * math.sin(t * 4 + k)
            d.line([(x - 18, y - 8), (x, y), (x + 18, y - 8)], fill=rgb("#1b0f22"), width=4)
        return img

    @staticmethod
    def _dhow(d, x, y, s, inc):
        c = rgb("#0c0610")
        d.polygon([(x - 120 * s, y - 20 * s), (x + 130 * s, y - 30 * s), (x + 90 * s, y + 25 * s),
                   (x - 90 * s, y + 25 * s)], fill=c)
        mx = x + 10 * s
        d.line([(mx, y - 20 * s), (mx + inc * 200, y - 240 * s)], fill=c, width=max(2, int(5 * s)))
        d.polygon([(mx - 130 * s + inc * 100, y - 60 * s), (mx + 30 * s + inc * 220, y - 270 * s),
                   (mx + 100 * s + inc * 80, y - 40 * s)], fill=c)


def _palacio(d, cx, base, s, col, columnas=None, reloj=None):
    """Silueta del Palacio de las Maravillas (Beit al-Ajaib), en escala s."""
    tiers = [(-450, 0, 450, -320), (-410, -320, 410, -600), (-370, -600, 370, -840)]
    for x0, y0, x1, y1 in tiers:
        d.rectangle((cx + x0 * s, base + y1 * s, cx + x1 * s, base + y0 * s), fill=col)
        if columnas:
            for xx in range(int(x0) + 30, int(x1) - 10, 60):
                d.rectangle((cx + xx * s, base + (y1 + 20) * s, cx + (xx + 10) * s, base + (y0 - 5) * s),
                            fill=columnas)
            d.rectangle((cx + x0 * s, base + (y1 + 4) * s, cx + x1 * s, base + (y1 + 18) * s), fill=columnas)
    d.rectangle((cx - 90 * s, base - 1080 * s, cx + 90 * s, base - 840 * s), fill=col)
    d.polygon([(cx - 110 * s, base - 1080 * s), (cx, base - 1190 * s), (cx + 110 * s, base - 1080 * s)], fill=col)
    if reloj:
        d.ellipse((cx - 55 * s, base - 1015 * s, cx + 55 * s, base - 905 * s), fill=reloj)


class EscenaPalacio:
    camara = "acercar"

    def __init__(self):
        img = vgrad([(0, "#03050d"), (.7, "#16203c"), (.78, "#2a2030"), (1, "#0b0a0f")])
        d = ImageDraw.Draw(img)
        r = random.Random(9)
        for _ in range(160):
            x, y = r.randint(0, W), r.randint(0, 1100)
            v = r.randint(120, 255)
            d.point((x, y), fill=(v, v, v))
        pegar_glow(img, 860, 300, 220, "#cfd8ff", 0.5)
        d = ImageDraw.Draw(img)
        d.ellipse((800, 240, 920, 360), fill=rgb("#f3eedb"))
        pegar_glow(img, 540, 1450, 700, "#ff8a2a", 0.35)
        d = ImageDraw.Draw(img)
        _palacio(d, 540, 1500, 1.0, rgb("#b9ad98"), columnas=rgb("#5e5446"), reloj=rgb("#fff1c4"))
        luz = vgrad([(0, "#000000"), (1, "#000000")])
        a = np.linspace(170, 0, H).astype(np.uint8)
        luz.putalpha(Image.fromarray(np.repeat(a[:, None], W, 1)))
        img.alpha_composite(luz)
        calida = Image.new("RGBA", (W, H), rgb("#ff9a40") + (0,))
        a2 = (np.clip((np.linspace(0, 1, H) - 0.45) * 2.2, 0, 1) * 70).astype(np.uint8)
        calida.putalpha(Image.fromarray(np.repeat(a2[:, None], W, 1)))
        img.alpha_composite(calida)
        pegar_glow(img, 540, 450, 90, "#fff1c4", 0.9)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 1500, W, H), fill=rgb("#0b0a0f"))
        self._persona(d, 540, 1760, 1.5, turbante=True)
        for gx in (330, 750):
            self._persona(d, gx, 1640, 1.0)
            d.line((gx + 45, 1640, gx + 45, 1380), fill=rgb("#07060a"), width=6)
            d.polygon([(gx + 35, 1385), (gx + 45, 1340), (gx + 55, 1385)], fill=rgb("#07060a"))
        for tx in (170, 910):
            d.rectangle((tx - 8, 1360, tx + 8, 1560), fill=rgb("#1a120c"))
        self.base = img

    @staticmethod
    def _persona(d, x, base, s, turbante=False):
        c = rgb("#07060a")
        d.polygon([(x - 70 * s, base), (x - 45 * s, base - 200 * s), (x + 45 * s, base - 200 * s),
                   (x + 70 * s, base)], fill=c)
        d.ellipse((x - 28 * s, base - 262 * s, x + 28 * s, base - 200 * s), fill=c)
        if turbante:
            d.ellipse((x - 36 * s, base - 285 * s, x + 36 * s, base - 240 * s), fill=c)

    def frame(self, t, dur):
        img = self.base.copy()
        d = ImageDraw.Draw(img)
        pts = [(540, 320)]
        for i in range(9):
            pts.append((540 + i * 16, 320 + 8 * math.sin(t * 5 - i * 0.7)))
        for i in range(8, -1, -1):
            pts.append((540 + i * 16, 380 + 8 * math.sin(t * 5 - i * 0.7)))
        d.line((540, 310, 540, 420), fill=rgb("#1a1410"), width=5)
        d.polygon(pts, fill=rgb("#c0141c"))
        for tx in (170, 910):
            fl = 1 + 0.15 * math.sin(t * 17 + tx) + 0.1 * math.sin(t * 29)
            pegar_glow(img, tx, 1340, 160 * fl, "#ff8a2a", 0.6)
            pegar_glow(img, tx, 1345, 40 * fl, "#ffe08a", 1.0)
        for x, y, f, k in particulas(3, 25, t, vy=(-60, -30), zona=(100, 900, 980, 1400)):
            pegar_glow(img, x, y, 4 + 3 * k, "#ffb050", 0.7)
        return img


DISPAROS = [0.5, 1.0, 1.6, 2.1, 2.7, 3.2, 3.8, 4.3, 4.9, 5.5, 6.0, 6.6, 7.2, 7.8, 8.4, 9.0]


class EscenaBarcos:
    camara = "acercar"
    naves = [(250, 1330, 0.95), (620, 1290, 0.7), (330, 1560, 1.35)]

    def __init__(self):
        hz = 1190
        img = vgrad([(0, "#141a30"), (.45, "#5a4466"), (.6, "#e08a5a"), (.62, "#f0a870"), (.621, "#2d2a3a"),
                     (1, "#07090f")])
        pegar_glow(img, 900, hz - 20, 380, "#ffb070", 0.6)
        d = ImageDraw.Draw(img)
        d.polygon([(700, hz + 2), (760, hz - 25), (1080, hz - 30), (1080, hz + 2)], fill=rgb("#120e16"))
        _palacio(d, 930, hz - 20, 0.13, rgb("#120e16"))
        self.base, self.hz = img, hz

    @staticmethod
    def _barco(d, x, y, s):
        c = rgb("#0b0d14")
        d.polygon([(x - 230 * s, y - 40 * s), (x + 250 * s, y - 40 * s), (x + 200 * s, y + 30 * s),
                   (x - 200 * s, y + 30 * s)], fill=c)
        d.rectangle((x - 120 * s, y - 110 * s, x + 110 * s, y - 40 * s), fill=c)
        d.rectangle((x - 70 * s, y - 160 * s, x + 50 * s, y - 110 * s), fill=c)
        for fx in (-60, 10):
            d.rectangle((x + fx * s, y - 240 * s, x + (fx + 36) * s, y - 150 * s), fill=c)
        for mx in (-170, 160):
            d.line((x + mx * s, y - 40 * s, x + mx * s, y - 330 * s), fill=c, width=max(2, int(6 * s)))
            d.line((x + (mx - 50) * s, y - 280 * s, x + (mx + 50) * s, y - 280 * s), fill=c,
                   width=max(2, int(4 * s)))
        d.line((x + 110 * s, y - 80 * s, x + 260 * s, y - 95 * s), fill=c, width=max(3, int(12 * s)))
        return x + 260 * s, y - 95 * s

    def frame(self, t, dur):
        img = self.base.copy()
        d = ImageDraw.Draw(img)
        for i, y in enumerate(range(self.hz + 10, H, 22)):
            x = (i * 137 + t * 30) % W
            d.line((x, y, x + 60 + i * 3, y), fill=(255, 180, 120, 40), width=2)
        bocas = []
        for k, (x, y, s) in enumerate(self.naves):
            bocas.append(self._barco(d, x, y + 6 * math.sin(t * 1.4 + k), s))
        # humo de las chimeneas
        for k, (x, y, s) in enumerate(self.naves):
            for j in range(6):
                edad = (t * 0.6 + j / 6) % 1
                pegar_glow(img, x + (-40 + edad * 160) * s, y - (250 + edad * 260) * s, (30 + 70 * edad) * s * 1.6,
                           "#2a2630", 0.8 * (1 - edad))
        for i, td in enumerate(DISPAROS):
            dt = t - td
            if dt < 0 or dt > 2.2:
                continue
            bx, by = bocas[i % 3]
            s = self.naves[i % 3][2]
            if dt < 0.25:
                pegar_glow(img, bx, by, 160 * s * (1 - dt * 2), "#ffd27a", 1.0)
                pegar_glow(img, bx, by, 60 * s, "#ffffff", 1 - dt * 4 if dt < 0.25 else 0)
            for j in range(4):
                pegar_glow(img, bx + (40 + dt * 90 + j * 30) * s, by - (dt * 50 + j * 12) * s,
                           (40 + dt * 70) * s, "#8a8288", max(0, 0.55 * (1 - dt / 2.2)))
            # impacto en el palacio lejano
            di = dt - 0.6
            if 0 < di < 1.0:
                pegar_glow(img, 930 + (i % 3 - 1) * 30, self.hz - 60, 140 * (1 - di), "#ff7a2a", 1 - di)
                pegar_glow(img, 930 + (i % 3 - 1) * 30, self.hz - 90 - di * 80, 70 + di * 80, "#3a3036", 0.7 * (1 - di))
        return img

    @staticmethod
    def sacudida(t):
        m = 0.0
        for td in DISPAROS:
            if 0 <= t - td < 0.3:
                m = max(m, 1 - (t - td) / 0.3)
        return m


class EscenaRuinas:
    camara = "alejar"

    def __init__(self):
        hz = 1300
        img = vgrad([(0, "#0e0404"), (.45, "#4a1208"), (.66, "#b8380f"), (.68, "#140606"), (1, "#050202")])
        pegar_glow(img, 540, hz - 100, 700, "#ff5a10", 0.5)
        d = ImageDraw.Draw(img)
        c = rgb("#0a0505")
        r = random.Random(2)
        pts = [(60, hz)]
        x = 60
        while x < 1020:
            x += r.randint(30, 80)
            pts.append((x, hz - r.randint(250, 700) * (1 - abs(x - 540) / 900)))
        pts += [(1020, hz)]
        d.polygon(pts, fill=c)
        d.polygon([(470, hz - 300), (500, hz - 820), (560, hz - 760), (600, hz - 860), (620, hz - 300)], fill=c)
        for _ in range(14):
            hx, hy = r.randint(150, 900), r.randint(hz - 450, hz - 120)
            d.rectangle((hx, hy, hx + r.randint(20, 50), hy + r.randint(30, 70)), fill=rgb("#ff6a1a"))
        d.rectangle((0, hz, W, H), fill=rgb("#070303"))
        for _ in range(30):
            rx, ry = r.randint(0, W), r.randint(hz + 20, H)
            d.polygon([(rx, ry), (rx + r.randint(20, 90), ry - r.randint(10, 40)), (rx + r.randint(60, 140), ry)],
                      fill=c)
        self.base, self.hz = img, hz

    def frame(self, t, dur):
        img = self.base.copy()
        for k in range(9):
            x = 120 + k * 105
            fl = 1 + 0.25 * math.sin(t * 11 + k * 2) + 0.15 * math.sin(t * 23 + k)
            pegar_glow(img, x, self.hz - 20, 120 * fl, "#ff6a1a", 0.8)
            pegar_glow(img, x, self.hz - 10, 45 * fl, "#ffd060", 0.9)
        for x, y, f, k in particulas(5, 26, t, vel=(5, 25), vy=(-110, -60), zona=(100, 200, 1000, self.hz)):
            frac = (y - 200) / (self.hz - 200)
            pegar_glow(img, x, y, 90 + 110 * (1 - frac), "#1a1214", 0.65 * frac + 0.15)
        for x, y, f, k in particulas(6, 45, t, vel=(-20, 30), vy=(-160, -80), zona=(80, 300, 1000, self.hz)):
            pegar_glow(img, x, y, 5 + 4 * k, "#ffa040", 0.9)
        # contador de tiempo
        seg = min(38 * 60, int(38 * 60 * min(1.0, t / 1.6) ** 0.7))
        txt = f"00:{seg // 60:02d}:{seg % 60:02d}"
        f = fuente(150)
        capa = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        tw = dc.textlength(txt, font=f)
        dc.text(((W - tw) / 2, 60), txt, font=f, fill=rgb("#ffcf6a"))
        brillo = capa.filter(ImageFilter.GaussianBlur(22))
        img.alpha_composite(brillo, (0, 250))
        img.alpha_composite(brillo, (0, 250))
        img.alpha_composite(capa, (0, 250))
        return img


class EscenaMonedas:
    camara = "acercar"

    def __init__(self):
        mesa = 1250
        img = vgrad([(0, "#0b0705"), (.64, "#1e140c"), (.651, "#3b2414"), (1, "#140b05")])
        d = ImageDraw.Draw(img)
        r = random.Random(11)
        for _ in range(90):
            y = r.randint(mesa + 10, H)
            d.line((0, y, W, y + r.randint(-10, 10)), fill=(0, 0, 0, r.randint(20, 60)), width=r.randint(1, 3))
        pegar_glow(img, 230, 980, 650, "#ffaa50", 0.45)
        d = ImageDraw.Draw(img)
        d.rectangle((195, 1020, 265, mesa + 60), fill=rgb("#e8dcc0"))
        d.ellipse((195, mesa + 40, 265, mesa + 80), fill=rgb("#cbbf9f"))
        papel = Image.new("RGBA", (440, 560), rgb("#e6d6ae") + (255,))
        dp = ImageDraw.Draw(papel)
        dp.rectangle((10, 10, 429, 549), outline=rgb("#8a6a3a"), width=3)
        dp.text((40, 40), "FACTURA", font=fuente(56), fill=rgb("#4a2a10"))
        dp.text((40, 120), "Zanzíbar, 27 ago. 1896", font=fuente(26), fill=rgb("#5a3a1a"))
        for i in range(6):
            dp.line((40, 200 + i * 50, 400, 200 + i * 50), fill=rgb("#a88a5a"), width=2)
        dp.text((40, 220), "Proyectiles disparados", font=fuente(24), fill=rgb("#5a3a1a"))
        dp.text((40, 470), "TOTAL:", font=fuente(40), fill=rgb("#7a1010"))
        papel = papel.rotate(-9, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(papel.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v // 2), (360, 1080))
        img.alpha_composite(papel, (340, 1050))
        d = ImageDraw.Draw(img)
        for sx, n in ((720, 9), (880, 6), (600, 4)):
            base = 1680 if sx != 600 else 1760
            for i in range(n):
                y = base - i * 18
                d.ellipse((sx - 85, y - 24, sx + 85, y + 24), fill=rgb("#8a6418"))
                d.ellipse((sx - 85, y - 30, sx + 85, y + 18), fill=rgb("#e2b03c" if i == n - 1 else "#c4962c"))
            yt = base - (n - 1) * 18
            d.ellipse((sx - 60, yt - 22, sx + 60, yt + 10), outline=rgb("#f7d77a"), width=4)
        for bx, by in ((140, 1640), (230, 1720)):
            d.rounded_rectangle((bx, by, bx + 210, by + 70), 20, fill=rgb("#a8742e"))
            d.polygon([(bx + 200, by), (bx + 290, by + 35), (bx + 200, by + 70)], fill=rgb("#8a5c22"))
            d.line((bx + 20, by + 14, bx + 190, by + 14), fill=rgb("#e0b070"), width=6)
        self.base = img

    def frame(self, t, dur):
        img = self.base.copy()
        fl = 1 + 0.12 * math.sin(t * 13) + 0.08 * math.sin(t * 31)
        pegar_glow(img, 230, 985, 110 * fl, "#ffb050", 0.9)
        pegar_glow(img, 230, 990, 30 * fl, "#fff2c0", 1.0)
        for k, sx in enumerate((720, 880, 600)):
            if math.sin(t * 2 + k * 2) > 0.95:
                pegar_glow(img, sx + 40, 1520, 50, "#fff6d0", 0.9)
        for x, y, f, k in particulas(8, 30, t, zona=(0, 600, W, 1600)):
            pegar_glow(img, x, y, 4 + 4 * k, "#ffd890", 0.4)
        return img


class EscenaEspacio:
    camara = "acercar"

    def __init__(self):
        img = radial("#0e1430", "#000000", 540, 900, 1300)
        d = ImageDraw.Draw(img)
        r = random.Random(1)
        for _ in range(500):
            v = r.randint(80, 255)
            d.point((r.randint(0, W), r.randint(0, H)), fill=(v, v, v))
        self.base = img

    def frame(self, t, dur):
        img = self.base.copy()
        for x, y, f, k in particulas(2, 60, t, vel=(-5, 5), vy=(-5, 5)):
            pegar_glow(img, x, y, 4 + 10 * k, "#b0c8ff", 0.5 + 0.3 * math.sin(t * 3 + f))
        pegar_glow(img, 540, 900, 400 + 30 * math.sin(t), "#6080ff", 0.35)
        return img


VISUALES = {"reloj": EscenaReloj, "ciudad": EscenaCiudad, "palacio": EscenaPalacio, "barcos": EscenaBarcos,
            "ruinas": EscenaRuinas, "monedas": EscenaMonedas, "espacio": EscenaEspacio}


# =========================================================================== #
# CÁMARA, POST-PRODUCCIÓN Y SUBTÍTULOS
# =========================================================================== #
def camara(img, tipo, p, sacudida=0.0, t=0.0):
    p = 0.5 - 0.5 * math.cos(math.pi * min(max(p, 0), 1))  # suavizado
    if tipo == "acercar":
        z, fx = 1.0 + 0.14 * p, 0.5
    elif tipo == "alejar":
        z, fx = 1.14 - 0.14 * p, 0.5
    else:  # paneo
        z, fx = 1.14, 0.15 + 0.7 * p
    cw, ch = W / z, H / z
    x0 = (W - cw) * fx + sacudida * 14 * math.sin(t * 90)
    y0 = (H - ch) * 0.5 + sacudida * 14 * math.cos(t * 77)
    x0 = min(max(x0, 0), W - cw)
    y0 = min(max(y0, 0), H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


yy, xx = np.mgrid[0:H, 0:W]
VINETA = (1 - 0.62 * np.clip((np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.6)) - 0.35) / 0.75, 0, 1)
          ** 1.6)[..., None].astype(np.float32)
del yy, xx
_rng = np.random.default_rng(0)
GRANO = [_rng.normal(0, 4.5, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1) for _ in range(6)]


def post(img: Image.Image, n: int) -> np.ndarray:
    a = np.asarray(img.convert("RGB"), np.float32)
    a = (a - 128) * 1.08 + 128  # contraste
    a = a * VINETA + GRANO[n % len(GRANO)]
    return np.clip(a, 0, 255).astype(np.uint8)


def subtitulos(img, grupos, t, color):
    grupo = None
    for i, g in enumerate(grupos):
        fin = grupos[i + 1][0].inicio if i + 1 < len(grupos) else 1e9
        if g[0].inicio - 0.05 <= t < fin:
            grupo = g
            break
    if not grupo:
        return
    aparece = min(1.0, (t - grupo[0].inicio + 0.05) / 0.12)
    f = fuente(66)
    pal = [p.texto.upper() for p in grupo]
    capa = Image.new("RGBA", (W, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    esp = 18
    anchos = [d.textlength(p, font=f) for p in pal]
    lineas = [list(range(len(pal)))]
    if sum(anchos) + esp * (len(pal) - 1) > W - 220 and len(pal) > 1:
        m = (len(pal) + 1) // 2
        lineas = [list(range(m)), list(range(m, len(pal)))]
    y = 165 - len(lineas) * 42 + (1 - aparece) * 14
    cajas = []
    for ln in lineas:
        total = sum(anchos[i] for i in ln) + esp * (len(ln) - 1)
        x = (W - total) / 2
        for i in ln:
            cajas.append((x, y, i))
            x += anchos[i] + esp
        y += 84
    sombra = Image.new("RGBA", capa.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for x, y, i in cajas:
        ds.text((x, y + 5), pal[i], font=f, fill=(0, 0, 0, 230))
    sombra = sombra.filter(ImageFilter.GaussianBlur(10))
    capa.alpha_composite(sombra)
    capa.alpha_composite(sombra)
    d = ImageDraw.Draw(capa)
    alfa = int(255 * aparece)
    for x, y, i in cajas:
        sig = grupo[i + 1].inicio if i + 1 < len(grupo) else 1e9
        activa = grupo[i].inicio - 0.03 <= t < sig
        c = color if activa and _es_clave(grupo[i].texto) else (255, 255, 255)
        d.text((x, y), pal[i], font=f, fill=c + (alfa,), stroke_width=2, stroke_fill=(0, 0, 0, alfa))
    img.alpha_composite(capa, (0, 1290))


_comunes = set("el la los las un una unos unas de del y a en que con por para su sus se lo al es o mi tu".split())


def _es_clave(p):
    limpio = p.lower().strip(".,;:!?¿¡…\"'")
    return limpio not in _comunes and len(limpio) > 2


def etiqueta(img, txt, color, t):
    if not txt:
        return
    f = fuente(34)
    d = ImageDraw.Draw(img)
    w = d.textlength(txt, font=f)
    a = min(1, t / 0.3)
    capa = Image.new("RGBA", (int(w) + 60, 70), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    dc.rounded_rectangle((0, 0, w + 56, 66), 18, fill=(10, 10, 14, int(170 * a)))
    dc.text((28, 12), txt, font=f, fill=color + (int(255 * a),))
    img.alpha_composite(capa, (48, 150))


def transicion(a: np.ndarray, k: float) -> np.ndarray:
    """Zoom-blur + destello al entrar a una escena (k: 1 -> 0)."""
    if k <= 0:
        return a
    img = Image.fromarray(a)
    acc = a.astype(np.float32)
    for j, z in enumerate((1.04, 1.09, 1.15)):
        cw, ch = W / (1 + (z - 1) * k), H / (1 + (z - 1) * k)
        x0, y0 = (W - cw) / 2, (H - ch) / 2
        acc += np.asarray(img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)), np.float32)
    acc /= 4
    acc = acc + 90 * k ** 2
    return np.clip(acc, 0, 255).astype(np.uint8)


# =========================================================================== #
# SONIDO
# =========================================================================== #
SR = 44100


def leer_wav(ruta):
    with wave.open(str(ruta)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels())


def ruido_filtrado(n, suav, rng):
    x = rng.normal(0, 1, n + suav)
    c = np.cumsum(x)
    return (c[suav:] - c[:-suav]) / suav


def disenar_sonido(voz: np.ndarray, cortes, golpes, total) -> np.ndarray:
    n = int(total * SR) + SR
    mix = np.zeros((n, 2), np.float32)
    mix[:len(voz)] += voz[:n]
    rng = np.random.default_rng(3)
    tt = np.arange(n) / SR
    pad = (np.sin(2 * np.pi * 55 * tt) + 0.6 * np.sin(2 * np.pi * 82.4 * tt) + 0.35 * np.sin(2 * np.pi * 110 * tt))
    pad *= 0.022 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * tt))
    pad *= np.clip(tt / 1.5, 0, 1) * np.clip((total - tt) / 1.5, 0, 1)
    mix += pad[:, None]
    for c in cortes:
        m = int(0.55 * SR)
        s = int((c - 0.3) * SR)
        if s < 0:
            continue
        w = ruido_filtrado(m, 6, rng)
        env = np.sin(np.linspace(0, np.pi, m)) ** 2
        mix[s:s + m] += (0.18 * w * env)[:, None][:len(mix[s:s + m])]
    for g, fuerza in golpes:
        m = int(1.4 * SR)
        s = int(g * SR)
        if s >= n:
            continue
        b = ruido_filtrado(m, 60, rng) * 3
        b += np.sin(2 * np.pi * 48 * np.arange(m) / SR)
        b *= np.exp(-np.arange(m) / SR * 3.5)
        seg = mix[s:s + m]
        seg += (0.3 * fuerza * b[:len(seg)])[:, None]
    pico = np.abs(mix).max()
    if pico > 0.98:
        mix *= 0.98 / pico
    return mix


def escribir_wav(ruta, x):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())



# =========================================================================== #
# SINCRONIZAR CON TU PROPIO AUDIO (reconocimiento de voz con faster-whisper)
# =========================================================================== #
def _norm(p):
    import unicodedata
    p = unicodedata.normalize("NFD", p.lower())
    return "".join(c for c in p if c.isalnum())


def alinear_audio(ruta, escenas_cfg):
    """Devuelve escenas con inicio/dur/palabras sincronizadas a la voz real."""
    import difflib
    dur_total = duracion_audio(Path(ruta))
    guion = []  # (escena, palabra)
    for i, s in enumerate(escenas_cfg):
        guion += [(i, w) for w in s["texto"].split()]
    tiempos = [None] * len(guion)
    try:
        from faster_whisper import WhisperModel
        cache = Path(str(ruta) + ".palabras.json")
        if cache.exists() and cache.stat().st_mtime >= Path(ruta).stat().st_mtime:
            oidas = [tuple(x) for x in json.loads(cache.read_text(encoding="utf-8"))]
        else:
            crudo = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(ruta), "-ac", "1", "-ar", "16000",
                                    "-f", "f32le", "-"], capture_output=True, check=True).stdout
            print("   · reconociendo tu voz para sincronizar subtítulos (puede tardar un minuto)...")
            modelo = WhisperModel("small", device="cpu", compute_type="int8")
            segs, _ = modelo.transcribe(np.frombuffer(crudo, np.float32), language="es", word_timestamps=True)
            oidas = [(x.word.strip(), float(x.start), float(x.end)) for sg in segs for x in sg.words]
            cache.write_text(json.dumps(oidas, ensure_ascii=False), encoding="utf-8")
        sm = difflib.SequenceMatcher(None, [_norm(w) for _, w in guion], [_norm(w) for w, _, _ in oidas],
                                     autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n):
                tiempos[a + k] = (oidas[b + k][1], oidas[b + k][2])
    except Exception as e:  # noqa: BLE001
        print(f"   · sin reconocimiento de voz ({type(e).__name__}); reparto por longitud del texto")
    # rellenar palabras no reconocidas interpolando entre vecinas
    conocidos = [i for i, x in enumerate(tiempos) if x]
    if not conocidos:
        total_chars = sum(len(w) + 1 for _, w in guion)
        t = 0.0
        for i, (_, w) in enumerate(guion):
            d = dur_total * (len(w) + 1) / total_chars
            tiempos[i] = (t, t + d)
            t += d
    else:
        bordes = [(-1, (0.0, 0.0))] + [(i, tiempos[i]) for i in conocidos] + [(len(guion), (dur_total, dur_total))]
        for (ia, ta), (ib, tb) in zip(bordes, bordes[1:]):
            hueco = list(range(ia + 1, ib))
            if not hueco:
                continue
            t0, t1 = ta[1], tb[0]
            pesos = [len(guion[i][1]) + 1 for i in hueco]
            acc = t0
            for i, w in zip(hueco, pesos):
                d = (t1 - t0) * w / sum(pesos)
                tiempos[i] = (acc, acc + d)
                acc += d
    escenas = []
    for i, s in enumerate(escenas_cfg):
        idx = [k for k, (e, _) in enumerate(guion) if e == i]
        ini = 0.0 if i == 0 else tiempos[idx[0]][0] - 0.12
        escenas.append(dict(s, inicio=ini, palabras=[], _idx=idx))
    for i, e in enumerate(escenas):
        fin = escenas[i + 1]["inicio"] if i + 1 < len(escenas) else dur_total + 0.3
        e["dur"] = fin - e["inicio"]
        e["palabras"] = [Palabra(guion[k][1], tiempos[k][0] - e["inicio"], tiempos[k][1] - e["inicio"])
                         for k in e.pop("_idx")]
    return escenas


# =========================================================================== #
# MONTAJE
# =========================================================================== #
def generar(ruta_json: Path, audio_usuario: str | None = None):
    cfg = json.loads(ruta_json.read_text(encoding="utf-8"))
    color = rgb(cfg.get("color_dorado", "#F5B731"))
    nombre = ruta_json.stem + "_cine"
    print(f"▶ {nombre}")
    tmp = Path(tempfile.mkdtemp(prefix="cine_"))
    try:
        escenas = []
        t = 0.0
        if audio_usuario:
            escenas = alinear_audio(audio_usuario, cfg["escenas"])
            t = escenas[-1]["inicio"] + escenas[-1]["dur"]
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio_usuario, "-ar", str(SR), "-ac", "2",
                            str(tmp / "voz.wav")], check=True)
        else:
            partes = []
            pausa = 0.35
            for i, s in enumerate(cfg["escenas"]):
                print(f"   · voz escena {i + 1}")
                a = tmp / f"v{i}.mp3"
                dur, pal = narrar(s["texto"], cfg, a)
                pad = tmp / f"v{i}.wav"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a), "-af",
                                f"apad=whole_dur={dur + pausa:.3f}", "-ar", str(SR), "-ac", "2", str(pad)], check=True)
                partes.append(pad)
                escenas.append(dict(s, inicio=t, dur=dur + pausa, palabras=pal))
                t += dur + pausa
            (tmp / "l.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in partes))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                            str(tmp / "l.txt"), str(tmp / "voz.wav")], check=True)
        total = t + 0.6
        for e in escenas:
            e["grupos"] = agrupar_palabras(e["palabras"], max_palabras=3, max_chars=18)
            e["obj"] = VISUALES[e.get("visual", "espacio")]()

        golpes = []
        for e in escenas:
            if e.get("visual") == "barcos":
                for td in DISPAROS:
                    if td < e["dur"]:
                        golpes += [(e["inicio"] + td, 1.0), (e["inicio"] + td + 0.6, 0.5)]
        mezcla = disenar_sonido(leer_wav(tmp / "voz.wav"), [e["inicio"] for e in escenas[1:]], golpes, total)
        escribir_wav(tmp / "mezcla.wav", mezcla)

        (RAIZ / "salida").mkdir(exist_ok=True)
        salida = RAIZ / "salida" / f"{nombre}.mp4"
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", str(tmp / "mezcla.wav"), "-c:v", "libx264", "-preset", "medium",
             "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
             "-movflags", "+faststart", str(salida)], stdin=subprocess.PIPE)
        nf = int(total * FPS)
        for n in range(nf):
            tg = n / FPS
            e = [x for x in escenas if tg >= x["inicio"]][-1]
            tl = tg - e["inicio"]
            obj = e["obj"]
            img = obj.frame(tl, e["dur"])
            sac = obj.sacudida(tl) if hasattr(obj, "sacudida") else 0.0
            img = camara(img, obj.camara, tl / e["dur"], sac, tg)
            etiqueta(img, e.get("etiqueta", ""), color, tl)
            subtitulos(img, e["grupos"], tl, color)
            a = post(img, n)
            if e is not escenas[0] and tl < 0.3:
                a = transicion(a, 1 - tl / 0.3)
            if tg > total - 0.6:
                a = (a * max(0.0, (total - tg) / 0.6)).astype(np.uint8)
            proc.stdin.write(a.tobytes())
            if n % (FPS * 5) == 0:
                print(f"   · {tg:5.1f}s / {total:.1f}s", flush=True)
        proc.stdin.close()
        proc.wait()
        print(f"   ✔ {salida}")
        return salida
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--audio", help="tu propia narración (mp3/wav) con toda la historia")
    a = ap.parse_args()
    generar(Path(a.json), a.audio)
