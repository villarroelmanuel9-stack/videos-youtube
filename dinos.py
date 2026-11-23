#!/usr/bin/env python3
"""
Historia 11: DINOSAURIOS — versión "mejor producida".

Mejoras respecto al estilo caricatura básico:
  * Formas orgánicas suavizadas (splines) con sombreado y brillo (cel-shading).
  * Dinosaurios animados: caminan, mueven la cola, parpadean, rugen.
  * Fondos en capas con PARALLAX (profundidad) y plantas en primer plano.
  * Tarjetas informativas que entran por los costados, sincronizadas con PALABRAS de la voz.
  * Subtítulos con la palabra activa resaltada.
  * Transiciones con barrido, destellos y sacudidas; diseño de sonido (rugidos, impacto).
  * Final distinto: botón de suscripción animado + "Comenta «dino»".

Uso:
    python dinos.py historias/historia_11_dinosaurios.json [--audio audios/historia_11_voz.mp3] [--sin-audio]
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from caricatura import ease, pop
from cine import (SR, alinear_audio, escribir_wav, fuente, leer_wav, pegar_glow, ruido_filtrado)
from generar_short import FPS, H, W, agrupar_palabras, narrar, render_emoji

RAIZ = Path(__file__).resolve().parent
SS = 2
TINTA = (28, 24, 30)


# =========================================================================== #
# GEOMETRÍA Y PINTURA CON SOMBREADO
# =========================================================================== #
def catmull(pts, n=6, cerrado=True):
    if len(pts) < 3:
        return pts
    P = list(pts)
    if cerrado:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    if not cerrado:
        out.append(P[-2])
    return out


def elipse(cx, cy, rx, ry, rot=0.0, n=28):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + rx * math.cos(a) * c - ry * math.sin(a) * s, cy + rx * math.cos(a) * s + ry * math.sin(a) * c)
            for a in [2 * math.pi * i / n for i in range(n)]]


def capsula(p0, p1, w0, w1, n=6):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    pts = [(p1[0] + w1 / 2 * (ux * math.cos(a) + nx * math.sin(a)), p1[1] + w1 / 2 * (uy * math.cos(a) + ny * math.sin(a)))
           for a in [-math.pi / 2 + math.pi * i / n for i in range(n + 1)]]
    pts += [(p0[0] + w0 / 2 * (-ux * math.cos(a) - nx * math.sin(a)), p0[1] + w0 / 2 * (-uy * math.cos(a) - ny * math.sin(a)))
            for a in [-math.pi / 2 + math.pi * i / n for i in range(n + 1)]]
    return pts


def rot(p, centro, ang):
    c, s = math.cos(ang), math.sin(ang)
    x, y = p[0] - centro[0], p[1] - centro[1]
    return centro[0] + x * c - y * s, centro[1] + x * s + y * c


def oscuro(col, f=0.72):
    return tuple(int(c * f) for c in col[:3])


def claro(col, f=0.35):
    return tuple(int(c + (255 - c) * f) for c in col[:3])


class Lienzo:
    """Lienzo supermuestreado con utilidades de pintura sombreada."""

    def __init__(self, w, h, ox, oy):
        self.w, self.h, self.ox, self.oy = w, h, ox, oy
        self.img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def P(self, pts):
        return [((self.ox + x) * SS, (self.oy + y) * SS) for x, y in pts]

    def forma(self, pts, col, sombra=True, brillo=True, borde=True, ancho=5, suave=True, clip=None, luz=(-1, -1),
              intensidad=0.11):
        if suave:
            pts = catmull(pts, 5)
        q = self.P(pts)
        xs, ys = [p[0] for p in q], [p[1] for p in q]
        pad = 40
        x0, y0 = max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad)
        x1, y1 = min(self.img.width, int(max(xs)) + pad), min(self.img.height, int(max(ys)) + pad)
        if x1 <= x0 or y1 <= y0:
            return None
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in q], fill=255)
        if clip is not None:
            m = ImageChops.multiply(m, clip.crop((x0, y0, x1, y1)))
        caja = (x0, y0, x1, y1)
        self.img.paste(col[:3] + (255,), caja, m)
        tam = max(x1 - x0, y1 - y0)
        off = max(4, int(tam * intensidad))
        if sombra:
            s = Image.new("L", m.size, 0)
            s.paste(m, (int(luz[0] * off), int(luz[1] * off)))
            sh = ImageChops.subtract(m, s)
            self.img.paste(oscuro(col) + (255,), caja, sh.filter(ImageFilter.GaussianBlur(2)))
        if brillo:
            b = Image.new("L", m.size, 0)
            b.paste(m, (int(-luz[0] * off * 0.55), int(-luz[1] * off * 0.55)))
            hl = ImageChops.subtract(m, b).point(lambda v: int(v * 0.55))
            self.img.paste(claro(col) + (255,), caja, hl.filter(ImageFilter.GaussianBlur(2)))
        if borde:
            self.d.line(q + [q[0]], fill=TINTA, width=int(ancho * SS), joint="curve")
        full = Image.new("L", self.img.size, 0)
        full.paste(m, (x0, y0))
        return full

    def linea(self, pts, col, ancho, suave=False):
        if suave:
            pts = catmull(pts, 5, cerrado=False)
        self.d.line(self.P(pts), fill=col, width=int(ancho * SS), joint="curve")

    def circulo(self, cx, cy, r, col, borde=True, ancho=4):
        (x, y), = self.P([(cx, cy)])
        self.d.ellipse((x - r * SS, y - r * SS, x + r * SS, y + r * SS), fill=col,
                       outline=TINTA if borde else None, width=int(ancho * SS) if borde else 0)

    def ojo(self, cx, cy, r, parpadeo=False, iris=None, mirar=(0.25, 0)):
        if parpadeo:
            self.linea([(cx - r, cy), (cx + r, cy)], TINTA, 4)
            return
        self.circulo(cx, cy, r, (255, 255, 250))
        if iris:
            self.circulo(cx + mirar[0] * r * 0.4, cy + mirar[1] * r * 0.4, r * 0.62, iris, borde=False)
        self.circulo(cx + mirar[0] * r * 0.45, cy + mirar[1] * r * 0.45, r * 0.38, TINTA, borde=False)
        self.circulo(cx + mirar[0] * r * 0.45 - r * 0.15, cy - r * 0.2, r * 0.14, (255, 255, 255), borde=False)

    def final(self, s=1.0):
        im = self.img.resize((self.w, self.h), Image.LANCZOS)
        if s != 1.0:
            im = im.resize((max(1, int(self.w * s)), max(1, int(self.h * s))), Image.LANCZOS)
        return im


# =========================================================================== #
# DINOSAURIOS
# =========================================================================== #
def _pierna(L, cadera, fase, col, largo=1.0, grosor=1.0, lejos=False):
    """Pierna de terópodo (dos patas). Devuelve nada; pinta en L."""
    c = oscuro(col, 0.8) if lejos else col
    fx = cadera[0] + 70 * largo * math.cos(fase)
    fy = -max(0.0, math.sin(fase)) * 45 * largo
    rod = ((cadera[0] + fx) / 2 + 55 * largo, (cadera[1] + fy) / 2 + 10)
    tobillo = (fx - 40 * largo, fy - 75 * largo)
    L.forma(capsula(cadera, rod, 120 * grosor, 70 * grosor), c, intensidad=0.08)
    L.forma(capsula(rod, tobillo, 58 * grosor, 34 * grosor), c, intensidad=0.08)
    L.forma(capsula(tobillo, (fx + 10, fy - 8), 32 * grosor, 26 * grosor), c, intensidad=0.08)
    for dx in (0, 22, 40):
        L.forma([(fx + dx - 6, fy - 14), (fx + dx + 34 * largo, fy - 4), (fx + dx - 2, fy + 4)], (235, 225, 200),
                sombra=False, brillo=False, ancho=3, suave=False)


class Sprite:
    """Cachea los fotogramas de un personaje dibujado con Lienzo."""

    def __init__(self, fn, w, h, ox, oy, fases=16):
        self.fn, self.w, self.h, self.ox, self.oy, self.fases = fn, w, h, ox, oy, fases
        self.cache = {}

    def get(self, fase, s=1.0, boca=0.0, parp=False, extra=None):
        fi = int((fase % (2 * math.pi)) / (2 * math.pi) * self.fases) % self.fases
        bi = round(boca * 4) / 4
        clave = (fi, round(s, 2), bi, parp, extra)
        if clave not in self.cache:
            L = Lienzo(self.w, self.h, self.ox, self.oy)
            self.fn(L, fi / self.fases * 2 * math.pi, bi, parp, extra)
            self.cache[clave] = L.final(s)
        return self.cache[clave]

    def dibujar(self, img, x, y, s, t, vel=1.0, boca=0.0, espejo=False, extra=None, sombra=True, tinte=None,
                alfa=1.0):
        fase = t * 2 * math.pi * 0.9 * vel
        parp = (t * 0.8 + x * 0.001) % 3.3 < 0.11
        im = self.get(fase, s, boca, parp, extra)
        if espejo:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if tinte is not None:
            a = im.getchannel("A")
            im = Image.new("RGBA", im.size, tinte + (0,))
            im.putalpha(a)
        if alfa < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * alfa)))
        ox = (self.w - self.ox if espejo else self.ox) * s
        if sombra:
            sw = int(self.w * s * 0.55)
            sh = Image.new("RGBA", (sw, max(4, int(40 * s))), (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse((0, 0, sw, sh.height), fill=(0, 0, 0, 70))
            img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (int(x - sw / 2), int(y - sh.height / 2)))
        img.alpha_composite(im, (int(x - ox), int(y - self.oy * s)))


def _trex(L, f, boca, parp, extra):
    base, panza = (98, 128, 62), (222, 204, 146)
    sway = math.sin(f) * 0.06
    # pierna lejana
    _pierna(L, (-20, -330), f + math.pi, base, lejos=True)
    # cola
    sup, inf = [], []
    for i in range(9):
        u = i / 8
        x = -110 - 400 * u
        y = -385 + 40 * u + 30 * u * u * math.sin(f + 1.2)
        th = 92 * (1 - u) + 6
        sup.append((x, y - th * 0.55))
        inf.append((x, y + th * 0.45))
    L.forma(sup + inf[::-1], base)
    # brazo lejano
    L.forma(capsula((150, -400), (190, -360), 26, 18), oscuro(base, 0.8), ancho=4)
    # cuerpo
    cuerpo = L.forma(elipse(20, -400 + 3 * math.sin(f * 2), 205, 128, -0.2 + sway * 0.3), base)
    L.forma(elipse(60, -340, 150, 52, -0.2), panza, sombra=False, borde=False, clip=cuerpo)
    for i in range(5):  # rayas
        x = -100 + i * 55
        L.linea([(x, -505 + i * 6), (x + 18, -455), (x + 4, -425)], oscuro(base, 0.6), 9, suave=True)
    # cuello
    L.forma(capsula((150, -440), (255, -515), 150, 112), base)
    # mandíbula inferior y boca
    bis = (250, -525)
    abre = 0.5 * boca
    mand = [rot(p, bis, abre) for p in [(235, -540), (440, -552), (452, -534), (400, -506), (300, -494), (238, -504)]]
    if boca > 0.05:
        L.forma([(250, -540), (455, -560)] + [rot(p, bis, abre) for p in [(440, -548), (300, -500)]] + [(240, -520)],
                (120, 30, 40), sombra=False, brillo=False, borde=False)
        for i in range(6):
            x = 300 + i * 25
            a, b = rot((x, -545), bis, abre), rot((x + 8, -560), bis, abre)
            L.forma([a, (x + 4, -548) if False else rot((x + 4, -548), bis, abre), b], (250, 245, 230), sombra=False,
                    brillo=False, ancho=2, suave=False)
    L.forma(mand, base)
    # cráneo
    craneo = [(215, -600), (300, -632), (400, -620), (458, -596), (466, -560), (400, -548), (300, -543), (225, -528)]
    L.forma(craneo, base)
    for i in range(6):
        x = 300 + i * 26
        L.forma([(x, -548), (x + 14, -548), (x + 7, -528)], (250, 245, 230), sombra=False, brillo=False, ancho=2,
                suave=False)
    L.linea([(330, -612), (395, -606)], oscuro(base, 0.55), 10, suave=False)
    L.ojo(368, -592, 17, parpadeo=parp, iris=(230, 170, 40))
    L.circulo(446, -592, 5, oscuro(base, 0.4), borde=False)
    # brazo cercano
    L.forma(capsula((170, -410), (215, -365), 30, 20), base, ancho=4)
    L.forma(capsula((215, -365), (245, -380), 20, 14), base, ancho=4)
    # pierna cercana
    _pierna(L, (-30, -335), f, base)


def _estego(L, f, boca, parp, extra):
    base, placa = (124, 146, 92), (218, 120, 52)
    # patas lejanas
    for px, ph in ((-130, f + math.pi), (170, f)):
        fx = px + 30 * math.cos(ph)
        fy = -max(0.0, math.sin(ph)) * 30
        L.forma(capsula((px, -260), (fx, fy - 10), 82, 62), oscuro(base, 0.8))
    # placas (detrás del cuerpo)
    for i in range(9):
        u = i / 8
        x = -250 + 470 * u
        ytop = -330 - 150 * math.sin(math.pi * (u * 0.9 + 0.05))
        h = 70 + 70 * math.sin(math.pi * u)
        col = placa if i % 2 == 0 else (190, 85, 50)
        L.forma([(x - 38, ytop + 40), (x - 10, ytop - h), (x + 12, ytop - h + 10), (x + 40, ytop + 40)], col,
                intensidad=0.14)
    # cola con púas
    sup, inf = [], []
    for i in range(9):
        u = i / 8
        x = -200 - 330 * u
        y = -300 + 50 * u + 25 * u * u * math.sin(f + 1)
        th = 100 * (1 - u) + 10
        sup.append((x, y - th * 0.5))
        inf.append((x, y + th * 0.5))
    L.forma(sup + inf[::-1], base)
    for u, ang in ((0.82, -0.9), (0.9, -0.5), (0.86, 2.4), (0.94, 2.8)):
        x = -200 - 330 * u
        y = -300 + 50 * u + 25 * u * u * math.sin(f + 1)
        L.forma([(x - 10, y), (x + 70 * math.cos(ang), y - 70 * abs(math.sin(ang)) - 10), (x + 10, y)],
                (236, 226, 196), sombra=False, ancho=3, suave=False)
    cuerpo = L.forma(catmull([(-260, -250), (-200, -400), (0, -470), (180, -400), (260, -280), (200, -200),
                              (0, -170), (-200, -190)], 3), base)
    L.forma(elipse(0, -205, 220, 45), (214, 204, 150), sombra=False, borde=False, clip=cuerpo)
    L.forma(capsula((220, -300), (340, -230), 96, 66), base)
    L.forma(elipse(380, -232, 62, 40, 0.25), base)
    L.forma([(420, -222), (455, -208), (420, -198)], (90, 90, 70), sombra=False, brillo=False, ancho=3, suave=False)
    L.ojo(385, -245, 10, parpadeo=parp)
    for px, ph in ((-90, f), (210, f + math.pi)):
        fx = px + 30 * math.cos(ph)
        fy = -max(0.0, math.sin(ph)) * 30
        L.forma(capsula((px, -260), (fx, fy - 10), 92, 70), base)


def _raptor(L, f, boca, parp, extra):
    base, pluma = (150, 100, 62), (226, 186, 120)
    if extra == "verde":
        base, pluma = (70, 130, 120), (170, 220, 200)
    # pierna lejana
    _pierna(L, (-10, -205), f + math.pi, base, largo=0.62, grosor=0.5, lejos=True)
    # cola con plumas
    sup, inf = [], []
    for i in range(9):
        u = i / 8
        x = -60 - 260 * u
        y = -250 + 20 * u + 18 * math.sin(f + u * 2)
        th = 58 * (1 - u) + 8
        sup.append((x, y - th * 0.5))
        inf.append((x, y + th * 0.5))
    for i in range(6):
        u = 0.4 + i * 0.12
        x = -60 - 260 * u
        y = -250 + 20 * u + 18 * math.sin(f + u * 2)
        L.forma(elipse(x - 20, y, 48, 14, 0.15 * (i % 3 - 1)), pluma, ancho=3)
    L.forma(sup + inf[::-1], base)
    cuerpo = L.forma(elipse(0, -255, 112, 62, -0.25), base)
    for i in range(6):
        x = -70 + i * 28
        L.linea([(x, -300), (x + 14, -275)], oscuro(base, 0.7), 5)
    L.forma(elipse(20, -225, 70, 22, -0.25), claro(base, 0.5), sombra=False, borde=False, clip=cuerpo)
    # cuello y cabeza
    L.forma(capsula((70, -290), (130, -360), 62, 44), base)
    for i in range(4):
        L.forma(elipse(80 + i * 14, -330 - i * 14, 26, 9, -0.9), pluma, ancho=2)
    abre = 0.35 * boca
    bis = (135, -370)
    L.forma([rot(p, bis, abre) for p in [(130, -372), (238, -368), (236, -358), (140, -352)]], base, ancho=4)
    L.forma([(120, -400), (160, -410), (230, -392), (244, -376), (140, -366), (118, -378)], base, ancho=4)
    L.ojo(165, -392, 10, parpadeo=parp, iris=(240, 200, 40))
    # ala/brazo con plumas
    L.forma(catmull([(40, -275), (110, -255), (125, -215), (70, -205), (20, -240)], 3), pluma, ancho=4)
    for i in range(4):
        L.linea([(60 + i * 15, -250), (55 + i * 18, -212)], oscuro(pluma, 0.7), 3)
    _pierna(L, (-20, -210), f, base, largo=0.62, grosor=0.5)
    fx = -20 + 70 * 0.62 * math.cos(f)
    fy = -max(0.0, math.sin(f)) * 45 * 0.62
    L.linea([(fx + 10, fy - 10), (fx + 22, fy - 38), (fx + 40, fy - 30)], (240, 235, 220), 6, suave=True)


def _gallina(L, f, boca, parp, extra):
    blanco = (248, 246, 238)
    sorpresa = extra == "sorpresa"
    pic = 0.0 if sorpresa else max(0.0, math.sin(f)) ** 3
    for dx in (-40, 20):
        L.linea([(dx, -110), (dx + 4, -18)], TINTA, 18)
        L.linea([(dx, -110), (dx + 4, -18)], (245, 180, 50), 10)
        for ang in (-0.5, 0, 0.6):
            L.linea([(dx + 4, -14), (dx + 4 + 38 * math.cos(ang), -6 + 10 * math.sin(ang))], (245, 180, 50), 9)
    # cola
    for i, (ang, lg) in enumerate(((-2.2, 150), (-1.9, 170), (-1.6, 140))):
        bx, by = -150, -250
        L.forma(elipse(bx + lg * 0.5 * math.cos(ang), by + lg * 0.5 * math.sin(ang), lg * 0.55, 30, ang), blanco,
                ancho=4, intensidad=0.18)
    cuerpo = L.forma(elipse(-20, -210, 150, 118, -0.1), blanco, intensidad=0.13)
    L.forma(catmull([(-90, -230), (10, -250), (50, -200), (0, -160), (-80, -175)], 3), (236, 232, 222), ancho=4,
            clip=cuerpo)
    for i in range(3):
        L.linea([(-60 + i * 30, -225), (-40 + i * 30, -180)], (210, 205, 195), 4)
    # cuello y cabeza (picotea hacia adelante)
    hx, hy = 95 + 40 * pic, -320 + 110 * pic
    L.forma(capsula((40, -230), (hx - 10, hy + 20), 110, 90), blanco, intensidad=0.1)
    for i, (dx, r) in enumerate(((-32, 22), (-6, 27), (22, 22))):
        L.forma(elipse(hx + dx, hy - 70, r, r + 8), (225, 40, 50), ancho=4)
    cab = L.forma(elipse(hx, hy - 8, 72, 68), blanco, intensidad=0.12)
    L.forma(elipse(hx + 52, hy + 52, 17, 26), (225, 40, 50), ancho=4)
    if sorpresa:
        L.forma([(hx + 58, hy - 18), (hx + 118, hy - 8), (hx + 60, hy + 4)], (250, 175, 40), ancho=4, suave=False)
        L.forma([(hx + 58, hy + 10), (hx + 105, hy + 34), (hx + 56, hy + 28)], (230, 150, 30), ancho=4, suave=False)
    else:
        L.forma([(hx + 58, hy - 14), (hx + 112, hy + 2), (hx + 58, hy + 14)], (250, 175, 40), ancho=4, suave=False)
    L.ojo(hx + 22, hy - 22, 22 if sorpresa else 17, parpadeo=parp and not sorpresa, iris=(245, 160, 40),
          mirar=(0.2, -0.3) if sorpresa else (0.35, 0))
    if sorpresa:
        L.linea([(hx + 2, hy - 58), (hx + 40, hy - 64)], TINTA, 5)


def _sauropodo(L, f, boca, parp, extra):
    base = (110, 130, 140)
    for px, ph in ((-150, f + math.pi), (140, f)):
        L.forma(capsula((px, -260), (px + 25 * math.cos(ph), -max(0.0, math.sin(ph)) * 20 - 10), 90, 70),
                oscuro(base, 0.8), brillo=False)
    sup, inf = [], []
    for i in range(8):
        u = i / 7
        x = -200 - 300 * u
        y = -330 + 120 * u + 15 * math.sin(f + u * 3)
        th = 110 * (1 - u) + 8
        sup.append((x, y - th * 0.5))
        inf.append((x, y + th * 0.5))
    L.forma(sup + inf[::-1], base, brillo=False)
    L.forma(elipse(0, -360, 260, 140), base, brillo=False)
    cuello = []
    for i in range(8):
        u = i / 7
        cuello.append((180 + 120 * u + 20 * math.sin(f * 0.5) * u, -400 - 360 * u))
    L.forma(capsula(cuello[0], cuello[-1], 120, 50), base, brillo=False)
    L.forma(elipse(cuello[-1][0] + 30, cuello[-1][1], 52, 30), base, brillo=False)
    L.ojo(cuello[-1][0] + 40, cuello[-1][1] - 8, 7, parpadeo=parp)
    for px, ph in ((-90, f), (200, f + math.pi)):
        L.forma(capsula((px, -260), (px + 25 * math.cos(ph), -max(0.0, math.sin(ph)) * 20 - 10), 100, 76), base,
                brillo=False)


TREX = Sprite(_trex, 1000, 760, 520, 720)
ESTEGO = Sprite(_estego, 1100, 720, 540, 690)
RAPTOR = Sprite(_raptor, 700, 560, 380, 530)
GALLINA = Sprite(_gallina, 520, 560, 270, 530)
SAURO = Sprite(_sauropodo, 1100, 900, 560, 860, fases=12)


# =========================================================================== #
# FONDOS EN CAPAS (PARALLAX)
# =========================================================================== #
def _grad(w, h, paradas):
    ys = np.linspace(0, 1, h)
    pos = [p for p, _ in paradas]
    cols = np.array([c for _, c in paradas], float)
    col = np.stack([np.interp(ys, pos, cols[:, i]) for i in range(3)], 1)
    return Image.fromarray(np.repeat(col[:, None, :], w, 1).astype(np.uint8)).convert("RGBA")


def _cresta(x0, x1, base, alto, rnd, pasos=9, picos=None):
    pts = [(x0, base)]
    for i in range(pasos + 1):
        x = x0 + (x1 - x0) * i / pasos
        pts.append((x, base - alto * (0.4 + 0.6 * rnd.random())))
    pts.append((x1, base))
    return pts


def _capa(w, h, dib):
    c = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    dib(d, SS)
    return c.resize((w, h), Image.LANCZOS)


ANCHO_CAPA = W + 500


def capas_jungla(variante="dia"):
    rnd = random.Random(4)
    if variante == "dia":
        cielo = _grad(W, H, [(0, (92, 160, 220)), (0.5, (180, 210, 225)), (0.68, (250, 222, 170)), (1, (250, 222, 170))])
        pegar_glow(cielo, 800, 820, 420, "#fff2c0", 0.7)
        c_lejos, c_medio, c_suelo, c_frente = (140, 165, 185), (70, 120, 90), (120, 150, 70), (40, 90, 50)
    else:  # amanecer tras el desastre
        cielo = _grad(W, H, [(0, (40, 30, 60)), (0.55, (150, 80, 70)), (0.7, (240, 160, 100)), (1, (240, 160, 100))])
        pegar_glow(cielo, 540, 1000, 500, "#ffcf8a", 0.8)
        c_lejos, c_medio, c_suelo, c_frente = (90, 80, 100), (50, 60, 60), (80, 90, 60), (30, 45, 35)

    def lejos(d, k):
        for i, (x0, alto) in enumerate(((-100, 420), (400, 360), (900, 460))):
            pts = catmull(_cresta(x0, x0 + 800, 1250, alto, rnd), 4, cerrado=False)
            d.polygon([(x * k, y * k) for x, y in pts], fill=c_lejos)
        # volcán
        vx = 1050
        d.polygon([((vx - 330) * k, 1250 * k), ((vx - 80) * k, 760 * k), ((vx + 80) * k, 760 * k),
                   ((vx + 330) * k, 1250 * k)], fill=oscuro(c_lejos, 0.85))
        d.polygon([((vx - 80) * k, 760 * k), ((vx - 40) * k, 800 * k), ((vx), 770 * k), ((vx + 50) * k, 805 * k),
                   ((vx + 80) * k, 760 * k)], fill=(250, 120, 40))
        d.line(((vx - 20) * k, 790 * k, (vx - 70) * k, 950 * k, (vx - 40) * k, 1050 * k), fill=(240, 110, 40),
               width=int(10 * k))
        niebla = Image.new("RGBA", (ANCHO_CAPA * k, 200 * k), (0, 0, 0, 0))
        nd = ImageDraw.Draw(niebla)
        for j in range(200 * k):
            nd.line((0, j, ANCHO_CAPA * k, j), fill=(255, 245, 230, int(110 * j / (200 * k))))
        c_img.alpha_composite(niebla, (0, 1060 * k))

    c_img = Image.new("RGBA", (ANCHO_CAPA * SS, H * SS), (0, 0, 0, 0))
    lejos(ImageDraw.Draw(c_img), SS)
    capa_lejos = c_img.resize((ANCHO_CAPA, H), Image.LANCZOS)

    def medio(d, k):
        for i in range(11):
            x = 40 + i * 150 + rnd.randint(-40, 40)
            base = 1330
            h = rnd.randint(280, 480)
            d.line((x * k, base * k, (x + 15) * k, (base - h) * k), fill=oscuro(c_medio, 0.7), width=int(18 * k))
            for a in range(0, 360, 36):
                ang = math.radians(a)
                ex, ey = x + 15 + 150 * math.cos(ang), base - h + 50 * math.sin(ang) + 30
                pts = catmull([((x + 15), (base - h)), ((x + 15 + ex) / 2, (base - h + ey) / 2 - 30), (ex, ey)], 4,
                              cerrado=False)
                d.line([(px * k, py * k) for px, py in pts], fill=c_medio, width=int(26 * k))
        pts = catmull(_cresta(-50, ANCHO_CAPA + 50, 1350, 60, rnd, 12), 4, cerrado=False)
        d.polygon([(x * k, y * k) for x, y in pts] + [((ANCHO_CAPA + 50) * k, 1500 * k), (-50 * k, 1500 * k)],
                  fill=oscuro(c_suelo, 0.85))
    capa_medio = _capa(ANCHO_CAPA, H, medio)

    def suelo(d, k):
        pts = catmull(_cresta(-50, ANCHO_CAPA + 50, 1420, 40, rnd, 10), 4, cerrado=False)
        d.polygon([(x * k, y * k) for x, y in pts] + [((ANCHO_CAPA + 50) * k, H * k), (-50 * k, H * k)], fill=c_suelo)
        d.line([(x * k, y * k) for x, y in pts], fill=oscuro(c_suelo, 0.7), width=int(6 * k))
        for _ in range(60):
            x, y = rnd.randint(0, ANCHO_CAPA), rnd.randint(1440, H)
            for a in (-0.5, 0, 0.5):
                d.line((x * k, y * k, (x + 30 * math.sin(a)) * k, (y - 40) * k), fill=oscuro(c_suelo, 0.75),
                       width=int(6 * k))
        for _ in range(8):
            x, y = rnd.randint(0, ANCHO_CAPA), rnd.randint(1500, H - 80)
            d.ellipse(((x - 50) * k, (y - 25) * k, (x + 50) * k, (y + 25) * k), fill=(140, 130, 120),
                      outline=TINTA, width=int(4 * k))
            d.ellipse(((x - 35) * k, (y - 22) * k, (x + 10) * k, (y - 5) * k), fill=(175, 165, 155))
    capa_suelo = _capa(ANCHO_CAPA, H, suelo)

    def frente(d, k):
        for x0, lado in ((-40, 1), (W + 40, -1)):
            for j in range(5):
                ang = math.radians(-70 + j * 18) if lado > 0 else math.radians(-110 - j * 18)
                L = 520 - j * 40
                ex, ey = x0 + L * math.cos(ang), H + 40 + L * math.sin(ang)
                pts = catmull([(x0, H + 40), ((x0 + ex) / 2 + 30 * lado, (H + 40 + ey) / 2), (ex, ey)], 5,
                              cerrado=False)
                d.line([(px * k, py * k) for px, py in pts], fill=c_frente, width=int(30 * k))
                for t_ in range(1, 9):
                    px, py = pts[int(len(pts) * t_ / 9)]
                    for sgn in (-1, 1):
                        d.line((px * k, py * k, (px + 60 * math.cos(ang + sgn * 1.2)) * k,
                                (py + 60 * math.sin(ang + sgn * 1.2)) * k), fill=claro(c_frente, 0.15),
                               width=int(14 * k))
    capa_frente = _capa(W, H, frente)
    return dict(cielo=cielo, lejos=capa_lejos, medio=capa_medio, suelo=capa_suelo, frente=capa_frente)


def capas_granja():
    rnd = random.Random(8)
    cielo = _grad(W, H, [(0, (110, 175, 235)), (0.6, (205, 230, 245)), (1, (205, 230, 245))])
    pegar_glow(cielo, 250, 300, 260, "#fff6c8", 0.8)

    def lejos(d, k):
        for x0, alto, col in ((-200, 300, (120, 170, 110)), (500, 360, (110, 160, 100))):
            pts = catmull([(x0, 1250), (x0 + 300, 1250 - alto), (x0 + 700, 1250 - alto * 0.7), (x0 + 1000, 1250)], 6,
                          cerrado=False)
            d.polygon([(x * k, y * k) for x, y in pts], fill=col)
        bx = 650
        d.rectangle(((bx - 260) * k, 820 * k, (bx + 260) * k, 1260 * k), fill=(190, 50, 45), outline=TINTA,
                    width=int(7 * k))
        d.polygon([((bx - 300) * k, 830 * k), (bx * k, 600 * k), ((bx + 300) * k, 830 * k)], fill=(150, 40, 40),
                  outline=TINTA)
        d.line(((bx - 300) * k, 830 * k, bx * k, 600 * k, (bx + 300) * k, 830 * k), fill=TINTA, width=int(7 * k))
        d.rectangle(((bx - 110) * k, 1000 * k, (bx + 110) * k, 1260 * k), fill=(240, 235, 220), outline=TINTA,
                    width=int(6 * k))
        d.line(((bx - 110) * k, 1000 * k, (bx + 110) * k, 1260 * k), fill=(190, 50, 45), width=int(10 * k))
        d.line(((bx + 110) * k, 1000 * k, (bx - 110) * k, 1260 * k), fill=(190, 50, 45), width=int(10 * k))
    c = Image.new("RGBA", (ANCHO_CAPA * SS, H * SS), (0, 0, 0, 0))
    lejos(ImageDraw.Draw(c), SS)
    capa_lejos = c.resize((ANCHO_CAPA, H), Image.LANCZOS)

    def medio(d, k):
        for x in range(0, ANCHO_CAPA, 140):
            d.rectangle((x * k, 1180 * k, (x + 18) * k, 1330 * k), fill=(240, 235, 220), outline=TINTA,
                        width=int(4 * k))
        for y in (1210, 1270):
            d.rectangle((0, y * k, ANCHO_CAPA * k, (y + 16) * k), fill=(240, 235, 220), outline=TINTA,
                        width=int(4 * k))
    capa_medio = _capa(ANCHO_CAPA, H, medio)

    def suelo(d, k):
        pts = catmull(_cresta(-50, ANCHO_CAPA + 50, 1330, 30, rnd, 10), 4, cerrado=False)
        d.polygon([(x * k, y * k) for x, y in pts] + [((ANCHO_CAPA + 50) * k, H * k), (-50 * k, H * k)],
                  fill=(120, 180, 80))
        d.line([(x * k, y * k) for x, y in pts], fill=(80, 130, 60), width=int(6 * k))
        for _ in range(90):
            x, y = rnd.randint(0, ANCHO_CAPA), rnd.randint(1350, H)
            for a in (-0.4, 0, 0.4):
                d.line((x * k, y * k, (x + 25 * math.sin(a)) * k, (y - 34) * k), fill=(90, 150, 60), width=int(5 * k))
    capa_suelo = _capa(ANCHO_CAPA, H, suelo)
    vacio = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return dict(cielo=cielo, lejos=capa_lejos, medio=capa_medio, suelo=capa_suelo, frente=vacio)


def componer(capas, pan, extra_lejos=None, extra_medio=None, actores=None, extra_frente=None, viento=0.0):
    """pan: 0..1 desplazamiento horizontal. Cada capa se mueve a distinta velocidad."""
    img = capas["cielo"].copy()
    rango = ANCHO_CAPA - W
    for nombre, factor in (("lejos", 0.25), ("medio", 0.55), ("suelo", 1.0)):
        x = -int(rango * pan * factor)
        img.alpha_composite(capas[nombre], (x, 0))
        if nombre == "lejos" and extra_lejos:
            extra_lejos(img, x)
        if nombre == "medio" and extra_medio:
            extra_medio(img, x)
    if actores:
        actores(img, -int(rango * pan))
    img.alpha_composite(capas["frente"], (int(viento), 0))
    if extra_frente:
        extra_frente(img)
    return img


# =========================================================================== #
# OVERLAYS NUEVOS: tarjetas laterales, subtítulos, botón de suscripción
# =========================================================================== #
AMARILLO, ROJO, BLANCO, VERDE, AZUL = (255, 210, 50), (232, 52, 60), (255, 255, 255), (60, 190, 110), (70, 140, 250)


def sombra_suave(img, caja, radio=28, alfa=110, blur=16):
    x0, y0, x1, y1 = caja
    pad = blur * 2
    s = Image.new("RGBA", (int(x1 - x0) + pad * 2, int(y1 - y0) + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((pad, pad + 8, pad + x1 - x0, pad + y1 - y0 + 8), radius=radius_ok(radio),
                                        fill=(0, 0, 0, alfa))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)), (int(x0 - pad), int(y0 - pad)))


def radius_ok(r):
    return max(1, int(r))


def tarjeta(img, t, t0, lado, y, titulo, valor, color=AMARILLO, emoji=None, dur=None, ancho=None):
    """Tarjeta que entra deslizándose desde un costado ('izq' o 'der')."""
    if t < t0 or (dur is not None and t > t0 + dur + 0.3):
        return
    p = pop((t - t0) / 0.35)
    salida = 1.0 if dur is None else max(0.0, min(1.0, (t0 + dur + 0.3 - t) / 0.3))
    fv, ft = fuente(68), fuente(30)
    d = ImageDraw.Draw(img)
    w = int(ancho or max(d.textlength(valor, font=fv), d.textlength(titulo, font=ft)) + 90 + (110 if emoji else 0))
    h = 170
    margen = 46
    if lado == "izq":
        x_final = margen
        x = x_final - (1 - p) * (w + 80) - (1 - salida) * (w + 80)
    else:
        x_final = W - margen - w
        x = x_final + (1 - p) * (w + 80) + (1 - salida) * (w + 80)
    caja = (x, y, x + w, y + h)
    sombra_suave(img, caja)
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(capa)
    cd.rounded_rectangle((0, 0, w - 1, h - 1), radius=30, fill=(255, 255, 255, 245), outline=TINTA, width=5)
    cd.rounded_rectangle((0, 0, 22, h - 1), radius=12, fill=color + (255,))
    tx = 50
    if emoji:
        em = render_emoji(emoji)
        if em is not None:
            em = em.resize((96, int(96 * em.height / em.width)), Image.LANCZOS)
            capa.alpha_composite(em, (44, int((h - em.height) / 2)))
        tx = 160
    cd.text((tx, 30), titulo.upper(), font=ft, fill=(110, 110, 120))
    cd.text((tx, 66), valor, font=fv, fill=TINTA, stroke_width=0)
    img.alpha_composite(capa, (int(x), int(y)))


def chip(img, t, t0, txt, y=260, color=(20, 20, 28), color_txt=BLANCO, dur=None, tam=44):
    if t < t0 or (dur is not None and t > t0 + dur):
        return
    p = pop((t - t0) / 0.3)
    f = fuente(max(10, int(tam * p)))
    d = ImageDraw.Draw(img)
    w = d.textlength(txt, font=f) + 70
    h = tam * p + 44
    caja = (W / 2 - w / 2, y - h / 2, W / 2 + w / 2, y + h / 2)
    sombra_suave(img, caja, radio=h / 2, alfa=90)
    d.rounded_rectangle(caja, radius=radius_ok(h / 2), fill=color + (235,), outline=(255, 255, 255), width=4)
    d.text((W / 2, y), txt, font=f, fill=color_txt, anchor="mm")


def numero_gigante(img, t, t0, txt, sub, y=520, color=AMARILLO):
    if t < t0:
        return
    p = pop((t - t0) / 0.35)
    base = 170
    while base > 60 and ImageDraw.Draw(img).textlength(txt, font=fuente(base)) > W - 120:
        base -= 8
    tam = max(10, int(base * p))
    f = fuente(tam)
    capa = Image.new("RGBA", (W, tam + 120), (0, 0, 0, 0))
    cd = ImageDraw.Draw(capa)
    cd.text((W / 2, tam / 2 + 40), txt, font=f, fill=(0, 0, 0, 170), anchor="mm", stroke_width=14,
            stroke_fill=(0, 0, 0, 170))
    capa = capa.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(capa, (0, int(y - tam / 2 - 40)))
    d = ImageDraw.Draw(img)
    d.text((W / 2, y), txt, font=f, fill=color, anchor="mm", stroke_width=10, stroke_fill=TINTA)
    if sub:
        d.text((W / 2, y + tam * 0.62), sub, font=fuente(max(10, int(44 * p))), fill=BLANCO, anchor="mm",
               stroke_width=6, stroke_fill=TINTA)


def subtitulo(img, grupos, t, y=1335):
    grupo = None
    for i, g in enumerate(grupos):
        fin = grupos[i + 1][0].inicio if i + 1 < len(grupos) else 1e9
        if g[0].inicio - 0.04 <= t < fin:
            grupo = g
            break
    if not grupo:
        return
    f = fuente(76)
    fa = fuente(88)
    d = ImageDraw.Draw(img)
    pal = [p.texto.strip(",.;:«»").upper() for p in grupo]
    activa = 0
    for i, p in enumerate(grupo):
        if t >= p.inicio - 0.03:
            activa = i
    anchos = [d.textlength(w, font=fa if i == activa else f) for i, w in enumerate(pal)]
    esp = 22
    total = sum(anchos) + esp * (len(pal) - 1)
    if total > W - 120:
        f, fa = fuente(60), fuente(70)
        anchos = [d.textlength(w, font=fa if i == activa else f) for i, w in enumerate(pal)]
        total = sum(anchos) + esp * (len(pal) - 1)
    x = (W - total) / 2
    entrada = pop((t - grupo[0].inicio + 0.04) / 0.15)
    yy = y + (1 - entrada) * 25
    sombra = Image.new("RGBA", (W, 220), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sombra)
    xs = x
    for i, w in enumerate(pal):
        sd.text((xs, 110), w, font=fa if i == activa else f, fill=(0, 0, 0, 190), anchor="lm", stroke_width=12,
                stroke_fill=(0, 0, 0, 190))
        xs += anchos[i] + esp
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(9)), (0, int(yy - 100)))
    for i, w in enumerate(pal):
        rebote = 1.0
        col = AMARILLO if i == activa else BLANCO
        d.text((x, yy - (6 if i == activa else 0)), w, font=fa if i == activa else f, fill=col, anchor="lm",
               stroke_width=8, stroke_fill=TINTA)
        x += anchos[i] + esp


def boton_suscribir(img, t, t0, y=1080):
    if t < t0:
        return
    tt = t - t0
    p = pop(tt / 0.35)
    clic = tt > 1.2
    w, h = int(560 * p), int(140 * p)
    if w < 20:
        return
    x0 = W / 2 - w / 2
    caja = (x0, y - h / 2, x0 + w, y + h / 2)
    sombra_suave(img, caja, radio=h / 2)
    d = ImageDraw.Draw(img)
    presion = 0.94 if 1.1 < tt < 1.3 else 1.0
    if presion < 1:
        cx, cy = W / 2, y
        caja = (cx - w / 2 * presion, cy - h / 2 * presion, cx + w / 2 * presion, cy + h / 2 * presion)
    d.rounded_rectangle(caja, radius=radius_ok(h / 2), fill=(90, 90, 98) if clic else (225, 30, 40),
                        outline=BLANCO, width=6)
    d.text((W / 2 + (25 if clic else 0), y), "SUSCRITO" if clic else "SUSCRÍBETE", font=fuente(int(58 * p)),
           fill=BLANCO, anchor="mm")
    if clic:
        cx = W / 2 - 150
        d.line((cx - 22, y, cx - 5, y + 18, cx + 25, y - 20), fill=BLANCO, width=10)
        # campana que se sacude
        bx, by = W / 2 + 340, y
        ang = math.sin(tt * 20) * 0.3 * max(0.0, 1 - (tt - 1.2) / 1.2)
        campana = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        cd = ImageDraw.Draw(campana)
        cd.pieslice((25, 20, 115, 120), 180, 360, fill=AMARILLO, outline=TINTA, width=5)
        cd.rectangle((25, 68, 115, 100), fill=AMARILLO, outline=TINTA, width=5)
        cd.rectangle((15, 96, 125, 110), fill=AMARILLO, outline=TINTA, width=5)
        cd.ellipse((58, 106, 82, 128), fill=AMARILLO, outline=TINTA, width=5)
        campana = campana.rotate(math.degrees(ang), resample=Image.BICUBIC)
        img.alpha_composite(campana, (int(bx - 70), int(by - 75)))
    # cursor
    if tt < 1.6:
        q = ease(tt / 1.1)
        cx = W / 2 + 330 - 230 * q
        cy = y + 260 - 230 * q
        cur = [(cx, cy), (cx, cy + 70), (cx + 18, cy + 54), (cx + 32, cy + 84), (cx + 44, cy + 78), (cx + 30, cy + 48),
               (cx + 54, cy + 46)]
        d.polygon(cur, fill=BLANCO, outline=TINTA)
        d.line(cur + [cur[0]], fill=TINTA, width=5)


# =========================================================================== #
# ESCENAS
# =========================================================================== #
def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalnum())


class EscenaDino:
    camara = (1.0, 1.06, 0.5, 0.55)

    def __init__(self):
        self.palabras = []

    def tp(self, palabra, defecto, dur):
        """Momento (en s, relativo a la escena) en que se dice 'palabra'."""
        clave = _norm(palabra)
        for p in self.palabras:
            if _norm(p.texto).startswith(clave):
                return p.inicio
        return defecto * dur

    def mundo(self, t, dur):
        raise NotImplementedError

    def encima(self, img, t, dur):
        pass

    def sacudida(self, t, dur):
        return 0.0


def humo_volcan(img, x_capa, t):
    vx, vy = 1050 + x_capa, 760
    for j in range(9):
        f = (t * 0.12 + j / 9) % 1
        r = 40 + 160 * f
        cx = vx + 60 * f + 25 * math.sin(t + j)
        cy = vy - 40 - 520 * f
        pegar_glow(img, cx, cy, r * 1.6, "#5a5560", 0.75 * (1 - f) + 0.1)


def pterosaurios(img, t, n=3, y0=380):
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = (i * 380 + t * 90) % (W + 300) - 150
        y = y0 + i * 90 + 20 * math.sin(t * 2 + i)
        a = math.sin(t * 8 + i) * 22
        d.polygon([(x - 70, y - a), (x, y + 8), (x + 70, y - a), (x + 10, y - 6), (x - 10, y - 6)],
                  fill=(60, 55, 70))
        d.polygon([(x + 5, y - 6), (x + 40, y - 18), (x + 8, y - 12)], fill=(60, 55, 70))


class D1(EscenaDino):  # gancho
    camara = (1.0, 1.18, 0.62, 0.5)

    def __init__(self):
        super().__init__()
        self.capas = capas_jungla()

    def boca(self, t):
        if 0.15 < t < 1.6:
            return min(1.0, (t - 0.15) / 0.2) * min(1.0, (1.6 - t) / 0.3)
        return 0.0

    def mundo(self, t, dur):
        def actores(img, x):
            ESTEGO.dibujar(img, 120 + x * 0.3, 1450, 0.42, t, vel=0.5, alfa=0.0 if t < dur * 0.45 else 1.0,
                           sombra=t >= dur * 0.45)
            TREX.dibujar(img, 600, 1640, 1.0, t, vel=0.6, boca=self.boca(t))
        return componer(self.capas, 0.15 * ease(t / dur), extra_lejos=lambda im, x: humo_volcan(im, x, t),
                        actores=actores, viento=8 * math.sin(t * 1.5), extra_frente=lambda im: pterosaurios(im, t, 2))

    def sacudida(self, t, dur):
        return self.boca(t) * 0.8

    def encima(self, img, t, dur):
        t_tu = self.tp("ti", 0.25, dur)
        t_est = self.tp("estegosaurio", 0.45, dur)
        tarjeta(img, t, t_tu, "izq", 230, "vivió más cerca de", "TI", AMARILLO, emoji="🦖")
        tarjeta(img, t, t_est, "der", 430, "que del", "ESTEGOSAURIO", VERDE)
        chip(img, t, self.tp("loco", 0.8, dur), "…y eso no es lo más loco 👀".replace(" 👀", ""), y=700,
             color=(225, 30, 40))


class D2(EscenaDino):
    camara = (1.0, 1.0, 0.5, 0.55)

    def __init__(self):
        super().__init__()
        self.capas = capas_jungla()

    def mundo(self, t, dur):
        cambio = self.tp("rex", 0.5, dur) - 0.25
        if t < cambio:
            def actores(img, x):
                ESTEGO.dibujar(img, 150 + t * 70, 1650, 0.95, t, vel=0.8)
            return componer(self.capas, 0.1 + 0.3 * t / dur, extra_lejos=lambda im, x: humo_volcan(im, x, t),
                            actores=actores)

        def actores2(img, x):
            TREX.dibujar(img, 1000 - (t - cambio) * 160, 1660, 0.95, t, vel=1.0, espejo=True,
                         boca=0.6 if 0.3 < t - cambio < 1.0 else 0.0)
        return componer(self.capas, 0.6 + 0.3 * t / dur, extra_lejos=lambda im, x: humo_volcan(im, x, t),
                        actores=actores2, extra_frente=lambda im: pterosaurios(im, t, 2))

    def encima(self, img, t, dur):
        cambio = self.tp("rex", 0.5, dur) - 0.25
        if t < cambio:
            tarjeta(img, t, 0.2, "izq", 240, "estegosaurio", "hace 150 millones", VERDE, emoji="🦕", dur=cambio - 0.5)
        else:
            tarjeta(img, t, cambio + 0.15, "der", 240, "tiranosaurio rex", "hace 68 millones", ROJO, emoji="🦖")
        if 0 < t - cambio < 0.2:
            # barrido (whip pan)
            pass


class D3(EscenaDino):  # línea del tiempo en estratos
    camara = (1.0, 1.0, 0.5, 0.5)
    LARGO = 3000

    def __init__(self):
        super().__init__()
        rnd = random.Random(2)
        L = self.LARGO
        img = Image.new("RGBA", (L, H), (0, 0, 0, 0))
        cielo = _grad(L, 700, [(0, (40, 50, 90)), (1, (90, 120, 170))])
        img.paste(cielo, (0, 0))
        d = ImageDraw.Draw(img)
        cols = [(150, 110, 75), (170, 130, 90), (135, 95, 65), (185, 150, 105), (120, 85, 60), (160, 120, 80)]
        y = 700
        for i, h in enumerate((140, 180, 160, 220, 260, 400)):
            pts = [(x, y + 18 * math.sin(x / 260 + i)) for x in range(0, L + 40, 40)]
            pts2 = [(x, y + h + 18 * math.sin(x / 260 + i + 1)) for x in range(L, -40, -40)]
            d.polygon(pts + pts2, fill=cols[i])
            d.line(pts, fill=oscuro(cols[i], 0.7), width=5)
            y += h
        for _ in range(26):  # fósiles
            x, yy = rnd.randint(60, L - 60), rnd.randint(1000, 1800)
            d.line((x - 30, yy, x + 30, yy), fill=(240, 230, 210), width=12)
            for sx in (-1, 1):
                d.ellipse((x + sx * 30 - 12, yy - 14, x + sx * 30 + 12, yy + 14), fill=(240, 230, 210))
        self.fondo = img
        self.x_est, self.x_rex, self.x_tu = 400, 400 + 82 * 18.0, 400 + 82 * 18.0 + 66 * 18.0

    def pan(self, t, dur):
        t1, t2 = self.tp("ochenta", 0.35, dur), self.tp("sesenta", 0.75, dur)
        objetivo_1 = self.x_rex - W * 0.6
        objetivo_2 = self.x_tu - W * 0.72
        if t < t1:
            return objetivo_1 * ease(t / max(t1, 0.1)) * 0.6
        if t < t2:
            return objetivo_1 * 0.6 + (objetivo_1 * 0.4) * ease((t - t1) / max(t2 - t1, 0.1))
        return objetivo_1 + (objetivo_2 - objetivo_1) * ease((t - t2) / 1.2)

    def mundo(self, t, dur):
        px = self.pan(t, dur)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        img.alpha_composite(self.fondo.crop((int(px), 0, int(px) + W, H)))
        d = ImageDraw.Draw(img)
        y = 900
        d.line((0, y, W, y), fill=(255, 255, 255), width=10)
        for ma in range(150, -1, -10):
            x = 400 + (150 - ma) * 18.0 - px
            if -50 < x < W + 50:
                d.line((x, y - 16, x, y + 16), fill=BLANCO, width=5)
        ESTEGO.dibujar(img, self.x_est - px, y - 20, 0.38, t, vel=0.4)
        TREX.dibujar(img, self.x_rex - px, y - 20, 0.42, t, vel=0.4)
        xt = self.x_tu - px
        if -100 < xt < W + 100:
            em = render_emoji("🧍")
            if em is not None:
                em = em.resize((150, int(150 * em.height / em.width)), Image.LANCZOS)
                img.alpha_composite(em, (int(xt - 75), int(y - 20 - em.height)))
        # llaves
        t1, t2 = self.tp("ochenta", 0.35, dur), self.tp("sesenta", 0.75, dur)
        for a, b, col, tt, yy, txt in ((self.x_est, self.x_rex, VERDE, t1, y + 130, "+80 MILLONES DE AÑOS"),
                                       (self.x_rex, self.x_tu, AMARILLO, t2, y + 300, "66 MILLONES")):
            q = ease((t - tt) / 0.8)
            if q <= 0:
                continue
            xa, xb = a - px, a - px + (b - a) * q
            d.line((xa, yy, xb, yy), fill=col, width=16)
            for xx in (xa, xb):
                d.line((xx, yy - 34, xx, yy + 34), fill=col, width=12)
            cx = (xa + xb) / 2
            if q > 0.5:
                d.text((min(max(cx, 260), W - 260), yy + 70), txt, font=fuente(50), fill=col, anchor="mm",
                       stroke_width=7, stroke_fill=TINTA)
        for x, txt in ((self.x_est, "150 M"), (self.x_rex, "68 M"), (self.x_tu, "HOY")):
            xx = x - px
            if -100 < xx < W + 100:
                d.text((xx, y - 330 if txt != "HOY" else y - 260), txt, font=fuente(46), fill=BLANCO, anchor="mm",
                       stroke_width=7, stroke_fill=TINTA)
        return img

    def encima(self, img, t, dur):
        chip(img, t, 0.1, "LÍNEA DEL TIEMPO", y=230, color=(30, 30, 40), tam=40)


class D4(EscenaDino):  # barras 165 M vs 300 mil
    camara = (1.0, 1.0, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.fondo = _grad(W, H, [(0, (20, 24, 44)), (1, (50, 40, 70))])
        d = ImageDraw.Draw(self.fondo)
        r = random.Random(3)
        for _ in range(120):
            x, y = r.randint(0, W), r.randint(0, H)
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(200, 200, 255))

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        t1 = self.tp("dinosaurios", 0.05, dur)
        t2 = self.tp("humanos", 0.55, dur)
        q = ease((t - t1) / 1.4)
        x0, x1 = 90, 990
        y1 = 820
        d.rounded_rectangle((x0, y1, x1, y1 + 110), radius=26, outline=(255, 255, 255, 80), width=4)
        if q > 0:
            d.rounded_rectangle((x0, y1, x0 + (x1 - x0) * q, y1 + 110), radius=26, fill=VERDE, outline=TINTA, width=5)
            em = render_emoji("🦕")
            if em is not None:
                em = em.resize((130, int(130 * em.height / em.width)), Image.LANCZOS)
                img.alpha_composite(em, (int(x0 + (x1 - x0) * q - 140), y1 - 140))
            d.text((x0, y1 - 50), "DINOSAURIOS · 165 MILLONES DE AÑOS", font=fuente(40), fill=BLANCO, anchor="lm",
                   stroke_width=5, stroke_fill=TINTA)
        y2 = 1120
        if t > t2:
            d.rounded_rectangle((x0, y2, x1, y2 + 110), radius=26, outline=(255, 255, 255, 80), width=4)
            ancho = max(2, (x1 - x0) * 0.3 / 165)
            d.rectangle((x0 + 4, y2 + 4, x0 + 4 + ancho, y2 + 106), fill=AMARILLO)
            d.text((x0, y2 - 50), "HUMANOS · 300 MIL AÑOS", font=fuente(40), fill=BLANCO, anchor="lm",
                   stroke_width=5, stroke_fill=TINTA)
            lupa_t = self.tp("trescientos", 0.75, dur)
            if t > lupa_t:
                p = pop((t - lupa_t) / 0.4)
                R = int(170 * p)
                if R > 10:
                    cx, cy = x0 + 220, y2 + 340
                    zona = img.crop((x0 - 10, y2 - 10, x0 + 30, y2 + 120)).resize((R * 2, R * 2), Image.NEAREST)
                    m = Image.new("L", (R * 2, R * 2), 0)
                    ImageDraw.Draw(m).ellipse((0, 0, R * 2, R * 2), fill=255)
                    img.paste(zona, (cx - R, cy - R), m)
                    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=BLANCO, width=12)
                    d.line((x0 + 10, y2 + 110, cx - R * 0.7, cy - R * 0.7), fill=BLANCO, width=6)
                    d.line((cx + R * 0.7, cy + R * 0.7, cx + R * 1.2, cy + R * 1.2), fill=(150, 100, 60), width=26)
                    d.text((cx + R + 40, cy), "← nosotros", font=fuente(52), fill=AMARILLO, anchor="lm",
                           stroke_width=6, stroke_fill=TINTA)
        return img

    def encima(self, img, t, dur):
        chip(img, t, 0.1, "¿QUIÉN REINÓ MÁS TIEMPO?", y=300, color=(30, 30, 40), tam=40)


class D5(EscenaDino):  # velocirraptor: película vs real
    camara = (1.0, 1.05, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.capas = capas_jungla()

    def mundo(self, t, dur):
        t_real = self.tp("pavo", 0.55, dur) - 0.4
        q = ease((t - t_real) / 0.7) if t > t_real else 0.0
        s = 2.1 - (2.1 - 0.62) * q

        def actores(img, x):
            if q < 1:
                RAPTOR.dibujar(img, 560, 1680, s, t, vel=0.6, boca=0.5 * (1 - q), tinte=(18, 16, 22),
                               alfa=1.0 - q * 0.6, sombra=False)
            if q > 0:
                RAPTOR.dibujar(img, 560, 1680, 0.62 + 0.0 * q, t, vel=0.8, alfa=q)
            # regla
            d = ImageDraw.Draw(img)
            if q > 0.5:
                yb = 1680
                d.rectangle((880, yb - 2 * 330, 930, yb), fill=(250, 235, 180), outline=TINTA, width=5)
                for i in range(11):
                    yy = yb - i * 66
                    d.line((880, yy, 880 + (40 if i % 5 == 0 else 22), yy), fill=TINTA, width=4)
                d.text((960, yb - 330), "1 m", font=fuente(40), fill=BLANCO, anchor="lm", stroke_width=5,
                       stroke_fill=TINTA)
                d.text((960, yb - 660), "2 m", font=fuente(40), fill=BLANCO, anchor="lm", stroke_width=5,
                       stroke_fill=TINTA)
        return componer(self.capas, 0.5, actores=actores, extra_lejos=lambda im, x: humo_volcan(im, x, t))

    def encima(self, img, t, dur):
        t_real = self.tp("pavo", 0.55, dur) - 0.4
        if t < t_real:
            chip(img, t, 0.2, "EN LAS PELÍCULAS", y=260, color=(20, 20, 28))
        else:
            tarjeta(img, t, t_real + 0.2, "izq", 230, "tamaño real", "como un pavo", AMARILLO, emoji="🦃")
            tarjeta(img, t, self.tp("plumas", 0.85, dur), "der", 430, "y tenían", "PLUMAS", AZUL, emoji="🪶")


class D6(EscenaDino):  # asteroide
    camara = (1.0, 1.12, 0.5, 0.65)

    def __init__(self):
        super().__init__()
        img = Image.new("RGBA", (W, H), (6, 8, 20, 255))
        d = ImageDraw.Draw(img)
        r = random.Random(9)
        for _ in range(260):
            x, y, rr = r.randint(0, W), r.randint(0, H), r.choice((1, 2, 3))
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 240))
        pegar_glow(img, 540, 2350, 1300, "#4a8cff", 0.45)
        L = Lienzo(W, H, 0, 0)
        tierra = L.forma(elipse(540, 2250, 1120, 1120, 0, 72), (50, 110, 210), brillo=False, ancho=6,
                         intensidad=0.015)
        tierra_m = tierra.copy()
        L.forma([(-60, 1050), (300, 1060), (430, 1120), (530, 1190), (590, 1228), (640, 1210), (705, 1196),
                 (745, 1232), (725, 1290), (655, 1322), (590, 1350), (520, 1378), (455, 1355), (395, 1290),
                 (300, 1225), (150, 1190), (-60, 1180)], (95, 170, 90), borde=False, clip=tierra_m, intensidad=0.03)
        L.forma([(760, 1150), (1150, 1130), (1150, 1260), (900, 1250), (800, 1215)], (95, 170, 90), borde=False,
                clip=tierra_m, intensidad=0.03)
        L.forma([(440, 1420), (520, 1440), (560, 1520), (480, 1560), (420, 1500)], (95, 170, 90), borde=False,
                clip=tierra_m, intensidad=0.03)
        img.alpha_composite(L.final())
        self.fondo = img

    def mundo(self, t, dur):
        img = self.fondo.copy()
        q = ease(t / dur) ** 1.3
        ax, ay = 1250 - 640 * q, -200 + 1500 * q
        d = ImageDraw.Draw(img)
        for i in range(14):
            f = i / 14
            pegar_glow(img, ax + 70 * i * 0.9, ay - 160 * i * 0.9, 90 - i * 5, "#ff8a2a", 0.85 * (1 - f))
        pegar_glow(img, ax, ay, 180, "#ffd27a", 0.8)
        L = Lienzo(260, 260, 130, 130)
        L.forma([(-80, -40), (-30, -90), (50, -80), (90, -20), (70, 60), (0, 90), (-70, 60)], (110, 95, 85),
                intensidad=0.18)
        for cx, cy, rr in ((-20, -20, 18), (30, 30, 14), (35, -40, 10)):
            L.circulo(cx, cy, rr, (80, 68, 60), ancho=3)
        roca = L.final().rotate(t * 40, resample=Image.BICUBIC)
        img.alpha_composite(roca, (int(ax - 130), int(ay - 130)))
        return img

    def sacudida(self, t, dur):
        return 0.15 * t / dur

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("diez", 0.35, dur), "izq", 230, "asteroide de", "~10 km", ROJO, emoji="☄️")
        ty = self.tp("yucatan", 0.75, dur)
        if t > ty:
            p = pop((t - ty) / 0.35)
            d = ImageDraw.Draw(img)
            px, py = 690, 1240
            d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=ROJO, outline=BLANCO, width=4)
            r = 40 + 30 * ((t * 2) % 1)
            d.ellipse((px - r, py - r, px + r, py + r), outline=ROJO + (int(255 * (1 - (t * 2) % 1)),), width=5)
            chip(img, t, ty, "📍 YUCATÁN, MÉXICO".replace("📍 ", ""), y=1110, color=(225, 30, 40), tam=int(44))


class D7(EscenaDino):  # impacto
    camara = (1.0, 1.04, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.capas = capas_jungla()
        self.oscuras = capas_jungla("amanecer")

    def mundo(self, t, dur):
        osc = ease((t - 1.5) / 2.5)

        def actores(img, x):
            SAURO.dibujar(img, 300 + x * 0.3, 1520, 0.45, t, vel=0.3, tinte=(30, 25, 35))
            TREX.dibujar(img, 760, 1650, 0.7, t, vel=0.3, espejo=True, tinte=(25, 20, 28))
        img = componer(self.capas, 0.4, actores=actores)
        if osc > 0:
            img = Image.blend(img, componer(self.oscuras, 0.4, actores=actores), osc)
            capa = Image.new("RGBA", (W, H), (60, 20, 10, int(120 * osc)))
            img.alpha_composite(capa)
        # bola de fuego en el horizonte
        if t < 3.5:
            f = t / 3.5
            pegar_glow(img, 820, 1150, 200 + 900 * f, "#ff7a1a", 0.9 * (1 - f))
            pegar_glow(img, 820, 1150, 120 + 500 * f, "#fff0b0", 0.9 * (1 - f))
            d = ImageDraw.Draw(img)
            r = 100 + 1500 * f
            d.ellipse((820 - r, 1150 - r * 0.4, 820 + r, 1150 + r * 0.4), outline=(255, 230, 180, int(220 * (1 - f))),
                      width=14)
        if t < 0.25:
            img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 1 - t / 0.25)
        # cenizas
        d = ImageDraw.Draw(img)
        rnd = random.Random(1)
        for _ in range(int(80 * osc)):
            x0, v = rnd.uniform(0, W), rnd.uniform(40, 120)
            y = (rnd.uniform(0, H) + v * t) % H
            x = (x0 + 30 * math.sin(t + x0)) % W
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(210, 200, 190))
        return img

    def sacudida(self, t, dur):
        return max(0.0, 1 - t / 1.5) * 2.2

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("miles", 0.15, dur), "der", 230, "más fuerte que", "MILES DE MILLONES",
                ROJO, emoji="💥", dur=self.tp("tres", 0.6, dur) - self.tp("miles", 0.15, dur) - 0.2)
        t3 = self.tp("tres", 0.6, dur)
        if t > t3:
            numero_gigante(img, t, t3, "3 de cada 4", "especies desaparecieron", y=520, color=AMARILLO)
            for i in range(4):
                em = render_emoji("🦕" if i < 3 else "🐦")
                if em is None:
                    continue
                em = em.resize((150, int(150 * em.height / em.width)), Image.LANCZOS)
                if i < 3 and t > t3 + 0.6 + i * 0.2:
                    em = em.convert("LA").convert("RGBA")
                    em.putalpha(em.getchannel("A").point(lambda v: v // 3))
                img.alpha_composite(em, (150 + i * 210, 760))


class D8(EscenaDino):  # sobrevivientes
    camara = (1.0, 1.12, 0.5, 0.62)

    def __init__(self):
        super().__init__()
        self.capas = capas_jungla("amanecer")

    def mundo(self, t, dur):
        def actores(img, x):
            RAPTOR.dibujar(img, 350 + t * 40, 1660, 0.45, t, vel=1.2, extra="verde")
            RAPTOR.dibujar(img, 720 - t * 30, 1700, 0.4, t + 1.3, vel=1.3, espejo=True)
        return componer(self.capas, 0.3 + 0.2 * t / dur, actores=actores, viento=6 * math.sin(t * 1.2))

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("pequenos", 0.2, dur), "izq", 230, "sobrevivieron los", "pequeños con plumas",
                VERDE, emoji="🪶")
        chip(img, t, self.tp("todos", 0.75, dur), "¿Y HOY DÓNDE ESTÁN? 👀".replace(" 👀", ""), y=700,
             color=(225, 30, 40))


class D9(EscenaDino):  # gallina + sombra del T. rex
    camara = (1.0, 1.15, 0.5, 0.65)

    def __init__(self):
        super().__init__()
        self.capas = capas_granja()

    def mundo(self, t, dur):
        tg = self.tp("gallina", 0.35, dur)

        def actores(img, x):
            if t > tg:
                a = ease((t - tg) / 0.8)
                TREX.dibujar(img, 600, 1340, 1.15, t, vel=0.2, tinte=(30, 20, 30), alfa=0.45 * a, sombra=False,
                             boca=0.4 if t - tg > 1.0 else 0.0)
            GALLINA.dibujar(img, 520, 1720, 1.15, t, vel=0.7)
        return componer(self.capas, 0.3, actores=actores)

    def encima(self, img, t, dur):
        numero_gigante(img, t, self.tp("aves", 0.1, dur), "LAS AVES", "¡son dinosaurios!", y=330, color=AMARILLO)
        tarjeta(img, t, self.tp("pariente", 0.6, dur), "der", 640, "pariente lejana del", "T. REX", ROJO, emoji="🦖")


class D10(EscenaDino):  # final distinto
    camara = (1.0, 1.1, 0.5, 0.55)

    def __init__(self):
        super().__init__()
        self.capas = capas_granja()

    def mundo(self, t, dur):
        def actores(img, x):
            GALLINA.dibujar(img, 540, 1760, 1.35, t, vel=0.0001, extra="sorpresa")
        img = componer(self.capas, 0.35, actores=actores)
        return img

    def encima(self, img, t, dur):
        t_pollo = self.tp("pollo", 0.2, dur)
        if t > t_pollo:
            em = render_emoji("🍗")
            if em is not None:
                p = pop((t - t_pollo) / 0.35)
                em = em.resize((max(1, int(190 * p)), max(1, int(190 * p * em.height / em.width))), Image.LANCZOS)
                img.alpha_composite(em, (int(800 - em.width / 2), int(980 - em.height / 2)))
        numero_gigante(img, t, self.tp("dinosaurio", 0.35, dur), "= DINOSAURIO", None, y=330, color=AMARILLO)
        tc = self.tp("comenta", 0.6, dur)
        if t > tc:
            p = pop((t - tc) / 0.3)
            d = ImageDraw.Draw(img)
            caja = (W / 2 - 360 * p, 560 - 80 * p, W / 2 + 360 * p, 560 + 80 * p)
            sombra_suave(img, caja, radio=40)
            d.rounded_rectangle(caja, radius=40, fill=(255, 255, 255, 245), outline=TINTA, width=6)
            d.polygon([(W / 2 - 40, 560 + 80 * p - 2), (W / 2 + 10, 560 + 80 * p - 2), (W / 2 - 50, 560 + 130 * p)],
                      fill=(255, 255, 255))
            d.text((W / 2 - 40, 560), "Comenta «DINO»", font=fuente(int(58 * p)), fill=TINTA, anchor="mm")
            em = render_emoji("🦖")
            if em is not None and p > 0.3:
                em = em.resize((int(100 * p), int(100 * p * em.height / em.width)), Image.LANCZOS)
                img.alpha_composite(em, (int(W / 2 + 230 * p), int(560 - em.height / 2)))
        boton_suscribir(img, t, self.tp("suscribete", 0.75, dur), y=800)


ESCENAS_DINO = {f"dino_{i}": c for i, c in enumerate((D1, D2, D3, D4, D5, D6, D7, D8, D9, D10), 1)}


# =========================================================================== #
# CÁMARA, SONIDO Y MONTAJE
# =========================================================================== #
def camara(img, cam, p, sac, t):
    z0, z1, fx, fy = cam
    z = z0 + (z1 - z0) * ease(p)
    cw, ch = W / z, H / z
    x0 = W * fx - cw / 2 + sac * 18 * math.sin(t * 83)
    y0 = H * fy - ch / 2 + sac * 18 * math.cos(t * 71)
    x0 = min(max(x0, 0), W - cw)
    y0 = min(max(y0, 0), H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


yy_, xx_ = np.mgrid[0:H, 0:W]
VINETA = (1 - 0.35 * np.clip((np.hypot((xx_ - W / 2) / (W * 0.6), (yy_ - H / 2) / (H * 0.58)) - 0.45) / 0.7, 0, 1)
          ** 2)[..., None].astype(np.float32)
del yy_, xx_


def barrido(a: np.ndarray, k: float, direccion=1) -> np.ndarray:
    """Desenfoque de movimiento horizontal (whip pan) de intensidad k (0..1)."""
    if k <= 0:
        return a
    acc = a.astype(np.float32)
    n = 6
    for i in range(1, n):
        acc += np.roll(a, int(direccion * i * 28 * k), axis=1)
    return (acc / n).astype(np.uint8)


def rugido(n_seg, rng):
    m = int(n_seg * SR)
    tt = np.arange(m) / SR
    f0 = 70 + 25 * np.sin(2 * np.pi * 3 * tt)
    fase = np.cumsum(2 * np.pi * f0 / SR)
    tono = np.sign(np.sin(fase)) * 0.5 + np.sin(fase * 2) * 0.3
    ruido = ruido_filtrado(m, 8, rng) * 4
    env = np.minimum(1, tt / 0.15) * np.exp(-np.maximum(0, tt - 0.4) * 2.2)
    return (tono * 0.6 + ruido * 0.5) * env


def disenar_sonido(voz, cortes, eventos, total):
    n = int(total * SR) + SR
    mix = np.zeros((n, 2), np.float32)
    mix[:len(voz)] += voz[:n] * 1.05
    rng = np.random.default_rng(5)
    tt = np.arange(n) / SR
    pad = (np.sin(2 * np.pi * 55 * tt) + 0.5 * np.sin(2 * np.pi * 82.4 * tt) + 0.3 * np.sin(2 * np.pi * 110 * tt))
    pad *= 0.018 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.12 * tt)) * np.clip(tt / 1.5, 0, 1)
    mix += pad[:, None]
    for c in cortes:
        m = int(0.5 * SR)
        s = int((c - 0.28) * SR)
        if s < 0:
            continue
        w = ruido_filtrado(m, 5, rng) * np.sin(np.linspace(0, np.pi, m)) ** 2 * 0.16
        mix[s:s + m] += w[:len(mix[s:s + m])][:, None]
    for t0, tipo in eventos:
        s = int(t0 * SR)
        if s >= n:
            continue
        if tipo == "rugido":
            x = rugido(1.6, rng) * 0.32
        elif tipo == "impacto":
            m = int(3.0 * SR)
            x = ruido_filtrado(m, 80, rng) * 4 + np.sin(2 * np.pi * 38 * np.arange(m) / SR)
            x *= np.exp(-np.arange(m) / SR * 1.3) * 0.45
        elif tipo == "retumbo":
            m = int(4.0 * SR)
            x = ruido_filtrado(m, 120, rng) * 3 * np.minimum(1, np.arange(m) / SR / 3) * 0.25
        else:
            continue
        seg = mix[s:s + len(x)]
        seg += x[:len(seg)][:, None]
    pico = np.abs(mix).max()
    if pico > 0.97:
        mix *= 0.97 / pico
    return mix


def generar(ruta_json: Path, audio_usuario=None, sin_audio=False):
    cfg = json.loads(ruta_json.read_text(encoding="utf-8"))
    nombre = ruta_json.stem + "_pro"
    print(f"▶ {nombre}")
    tmp = Path(tempfile.mkdtemp(prefix="dino_"))
    try:
        if audio_usuario:
            escenas = alinear_audio(audio_usuario, cfg["escenas"])
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio_usuario, "-ar", str(SR), "-ac", "2",
                            str(tmp / "voz.wav")], check=True)
        else:
            escenas, partes, t = [], [], 0.0
            for i, s in enumerate(cfg["escenas"]):
                a = tmp / f"v{i}.mp3"
                dur, pal = narrar(s["texto"], cfg, a)
                pad = tmp / f"v{i}.wav"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a), "-af",
                                f"apad=whole_dur={dur + 0.25:.3f}", "-ar", str(SR), "-ac", "2", str(pad)], check=True)
                partes.append(pad)
                escenas.append(dict(s, inicio=t, dur=dur + 0.25, palabras=pal))
                t += dur + 0.25
            (tmp / "l.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in partes))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                            str(tmp / "l.txt"), str(tmp / "voz.wav")], check=True)
        escenas[-1]["dur"] += 1.8  # tiempo para ver el botón de suscripción
        total = escenas[-1]["inicio"] + escenas[-1]["dur"]
        eventos = []
        for e in escenas:
            e["grupos"] = agrupar_palabras(e["palabras"], max_palabras=3, max_chars=20)
            e["obj"] = ESCENAS_DINO[e["visual"]]()
            e["obj"].palabras = e["palabras"]
            if e["visual"] == "dino_1":
                eventos.append((e["inicio"] + 0.15, "rugido"))
            if e["visual"] == "dino_2":
                eventos.append((e["inicio"] + e["obj"].tp("rex", 0.5, e["dur"]) + 0.05, "rugido"))
            if e["visual"] == "dino_6":
                eventos.append((e["inicio"], "retumbo"))
            if e["visual"] == "dino_7":
                eventos.append((e["inicio"], "impacto"))
        mezcla = disenar_sonido(leer_wav(tmp / "voz.wav"), [e["inicio"] for e in escenas[1:]], eventos, total)
        escribir_wav(tmp / "mezcla.wav", mezcla)

        (RAIZ / "salida").mkdir(exist_ok=True)
        salida = RAIZ / "salida" / f"{nombre}.mp4"
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", str(tmp / "mezcla.wav"), "-c:v", "libx264", "-preset", "medium",
             "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
             "-movflags", "+faststart", str(salida)], stdin=subprocess.PIPE)
        for n in range(int(total * FPS)):
            tg = n / FPS
            idx = max(i for i, x in enumerate(escenas) if tg >= x["inicio"])
            e = escenas[idx]
            tl = tg - e["inicio"]
            o = e["obj"]
            img = o.mundo(tl, e["dur"])
            img = camara(img, o.camara, tl / e["dur"], o.sacudida(tl, e["dur"]), tg)
            o.encima(img, tl, e["dur"])
            subtitulo(img, e["grupos"], tl)
            a = np.asarray(img.convert("RGB"), np.float32) * VINETA
            a = np.clip(a, 0, 255).astype(np.uint8)
            if idx > 0 and tl < 0.2 and e["visual"] != "dino_7":
                a = barrido(a, 1 - tl / 0.2, 1 if idx % 2 else -1)
            # barrido interno de la escena 2 (Estegosaurio -> T. rex)
            if e["visual"] == "dino_2":
                c = o.tp("rex", 0.5, e["dur"]) - 0.25
                if 0 <= tl - c < 0.2:
                    a = barrido(a, 1 - (tl - c) / 0.2, -1)
            proc.stdin.write(a.tobytes())
            if n % (FPS * 5) == 0:
                print(f"   · {tg:5.1f}s / {total:.1f}s", flush=True)
        proc.stdin.close()
        proc.wait()
        print(f"   ✔ {salida}")
        if sin_audio:
            muda = salida.with_name(salida.stem + "_SIN_AUDIO.mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(salida), "-c:v", "copy", "-an",
                            str(muda)], check=True)
            print(f"   ✔ {muda}")
        return salida
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--audio")
    ap.add_argument("--sin-audio", action="store_true")
    a = ap.parse_args()
    generar(Path(a.json), a.audio, a.sin_audio)
