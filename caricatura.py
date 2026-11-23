#!/usr/bin/env python3
"""
Shorts en estilo CARICATURA (personajes tipo "frijol" con contorno grueso,
ojos grandes que parpadean, expresiones), con:
  - subtítulos de 1-2 palabras blancos con sombra,
  - etiquetas amarillas con flecha roja animada,
  - número/dato grande en rojo,
  - píldora "¡Suscríbete!",
  - encuesta final con dos botones "VS" + "TE LEO EN COMENTARIOS".

Uso:
    python caricatura.py historias/historia_02_napoleon_no_era_bajito.json
    python caricatura.py historias/historia_02_napoleon_no_era_bajito.json --audio audios/historia_02_voz.mp3
    python caricatura.py ... --sin-audio      # además exporta una copia muda

Las escenas se eligen con "visual" en el JSON (ver ESCENAS al final).
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from cine import (SR, alinear_audio, disenar_sonido, escribir_wav, fuente, leer_wav, rgb)
from generar_short import FPS, H, W, agrupar_palabras, narrar

RAIZ = Path(__file__).resolve().parent
SS = 2  # supermuestreo para bordes suaves
TINTA = (26, 22, 30, 255)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def pop(x):
    x = min(max(x, 0.0), 1.0)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def suave(dibujar, w, h):
    """Dibuja a 2x con la función dada y devuelve la imagen reducida (bordes suaves)."""
    c = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    dibujar(ImageDraw.Draw(c), SS)
    return c.resize((w, h), Image.LANCZOS)


# =========================================================================== #
# PERSONAJES
# =========================================================================== #
class Personaje:
    """
    ropa: color del abrigo · piel · pelo · sombrero: None|'bicornio'|'piel'|'copa'
    estilo: 'napoleon' | 'granadero' | 'civil'
    expresion: 'normal' | 'enojado' | 'sorpresa' | 'risa' | 'triste' | 'serio'
    """

    def __init__(self, ropa="#7a4a2a", piel="#f6dcc0", pelo="#4a2c1a", sombrero=None, estilo="civil",
                 altura=1.0, bigote=False, semilla=0, peinado="normal", barba=False):
        self.peinado, self.barba = peinado, barba
        self.ropa, self.piel, self.pelo = rgb(ropa), rgb(piel), rgb(pelo)
        self.sombrero, self.estilo, self.altura, self.bigote = sombrero, estilo, altura, bigote
        self.fase = random.Random(semilla).uniform(0, 10)

    def render(self, s, t, expresion="normal", habla=0.0, mirar=(0.0, 0.0), brazos="abajo"):
        a = self.altura
        ancho, alto = 520, int(1000 * max(a, 1.0)) + 120
        ox, oy = ancho / 2, alto - 40  # pies
        piel, ropa, pelo = self.piel, self.ropa, self.pelo
        fase = self.fase

        def dib(d: ImageDraw.ImageDraw, k):
            K = k

            def P(x, y):
                return (ox + x) * K, (oy + y) * K

            def E(x0, y0, x1, y1, fill, ow=7):
                d.ellipse((*P(x0, y0), *P(x1, y1)), fill=fill, outline=TINTA, width=int(ow * K))

            lw = int(7 * K)
            # sombra
            d.ellipse((*P(-120, -14), *P(120, 16)), fill=(0, 0, 0, 70))
            piernas = 110 * a
            cuerpo_top = -(piernas + 220 * a)
            # piernas
            for sx in (-1, 1):
                d.line((*P(sx * 40, -piernas + 10), *P(sx * 44, -8)), fill=TINTA, width=int(26 * K))
                d.line((*P(sx * 40, -piernas + 10), *P(sx * 44, -8)), fill=(60, 50, 60), width=int(14 * K))
                E(sx * 44 - 32 + sx * 8, -22, sx * 44 + 32 + sx * 8, 8, (40, 30, 30))
            # brazos detrás del cuerpo
            sw = 6 * math.sin(t * 2.2 + fase)
            hombro_y = cuerpo_top + 70 * a
            for sx in (-1, 1):
                if brazos == "cruzados":
                    continue
                if brazos == "arriba" and sx == 1:
                    mano = (sx * 150, hombro_y - 130)
                else:
                    mano = (sx * (128 + sw * 0.3), hombro_y + 150 * a + sw)
                d.line((*P(sx * 85, hombro_y), *P(*mano)), fill=TINTA, width=int(30 * K))
                d.line((*P(sx * 85, hombro_y), *P(*mano)), fill=ropa, width=int(17 * K))
                E(mano[0] - 19, mano[1] - 19, mano[0] + 19, mano[1] + 19, piel, 6)
            # cuerpo
            d.rounded_rectangle((*P(-105, cuerpo_top), *P(105, -piernas + 30)), radius=int(95 * K), fill=ropa,
                                outline=TINTA, width=lw)
            # sombreado lateral
            d.rounded_rectangle((*P(40, cuerpo_top + 30), *P(98, -piernas + 10)), radius=int(40 * K),
                                fill=tuple(int(c * 0.82) for c in ropa) + (255,))
            if self.estilo == "napoleon":
                d.polygon([P(-38, cuerpo_top + 8), P(38, cuerpo_top + 8), P(30, -piernas + 20),
                           P(-30, -piernas + 20)], fill=(238, 232, 220), outline=TINTA, width=int(4 * K))
                for i in range(4):
                    yb = cuerpo_top + 50 + i * 42 * a
                    for sx in (-1, 1):
                        E(sx * 55 - 8, yb - 8, sx * 55 + 8, yb + 8, (232, 186, 60), 3)
                for sx in (-1, 1):
                    E(sx * 100 - 28, cuerpo_top + 22, sx * 100 + 28, cuerpo_top + 48, (232, 186, 60), 5)
            elif self.estilo == "granadero":
                d.line((*P(-80, cuerpo_top + 30), *P(70, -piernas + 10)), fill=(245, 245, 240), width=int(20 * K))
                d.line((*P(80, cuerpo_top + 30), *P(-70, -piernas + 10)), fill=(245, 245, 240), width=int(20 * K))
                for sx in (-1, 1):
                    E(sx * 92 - 32, cuerpo_top + 2, sx * 92 + 32, cuerpo_top + 32, (200, 30, 40), 5)
            elif self.estilo == "vestido":
                d.chord((*P(-100, cuerpo_top - 50), *P(100, cuerpo_top + 80)), 0, 180, fill=(232, 186, 60),
                        outline=TINTA, width=int(5 * K))
                for rr in (40, 60):
                    d.arc((*P(-rr - 30, cuerpo_top - rr + 10), *P(rr + 30, cuerpo_top + rr + 10)), 20, 160,
                          fill=(40, 90, 170), width=int(7 * K))
                d.rectangle((*P(-100, -piernas - 40), *P(100, -piernas - 22)), fill=(232, 186, 60))
            elif self.estilo == "toga":
                d.line((*P(-85, cuerpo_top + 20), *P(80, -piernas - 10)), fill=(180, 60, 60), width=int(26 * K))
            elif self.estilo == "astronauta":
                d.rounded_rectangle((*P(-55, cuerpo_top + 50), *P(55, cuerpo_top + 140)), radius=int(10 * K),
                                    fill=(170, 175, 185), outline=TINTA, width=int(4 * K))
                for i, c in enumerate(((220, 40, 40), (40, 160, 70), (40, 90, 200))):
                    E(-35 + i * 35 - 9, cuerpo_top + 85, -35 + i * 35 + 9, cuerpo_top + 103, c, 3)
                for i in range(5):
                    d.rectangle((*P(60, cuerpo_top + 30 + i * 8), *P(95, cuerpo_top + 34 + i * 8)),
                                fill=(200, 40, 40) if i % 2 == 0 else (245, 245, 245))
                d.rectangle((*P(60, cuerpo_top + 30), *P(74, cuerpo_top + 46)), fill=(40, 60, 150))
            else:
                d.line((*P(0, cuerpo_top + 20), *P(0, -piernas + 20)), fill=TINTA, width=int(4 * K))
                for i in range(3):
                    E(-8, cuerpo_top + 50 + i * 50 - 8, 8, cuerpo_top + 50 + i * 50 + 8, (230, 220, 200), 3)
            if brazos == "cruzados":
                y = hombro_y + 70
                d.rounded_rectangle((*P(-120, y - 30), *P(120, y + 34)), radius=int(32 * K), fill=ropa,
                                    outline=TINTA, width=lw)
                for sx in (-1, 1):
                    E(sx * 95 - 18, y - 16, sx * 95 + 18, y + 20, piel, 5)
            # cabeza
            hc = cuerpo_top - 55
            r = 108
            if self.peinado == "melena":
                d.rounded_rectangle((*P(-132, hc - 118), *P(132, hc + 105)), radius=int(70 * K), fill=pelo,
                                    outline=TINTA, width=lw)
            if self.sombrero == "nemes":
                for sx in (-1, 1):
                    pts = [P(sx * (r - 20), hc - 40), P(sx * (r + 22), hc - 40), P(sx * (r + 40), hc + 175),
                           P(sx * (r - 25), hc + 175)]
                    d.polygon(pts, fill=(232, 186, 60), outline=TINTA, width=lw)
                    for i in range(6):
                        yy_ = hc - 20 + i * 34
                        d.line((*P(sx * (r - 18), yy_), *P(sx * (r + 30), yy_)), fill=(40, 70, 160),
                               width=int(10 * K))
            E(-r, hc - r, r, hc + r, piel, 8)
            # pelo
            if self.sombrero == "nemes":
                d.chord((*P(-r - 14, hc - r - 18), *P(r + 14, hc + r - 50)), 180, 360, fill=(232, 186, 60),
                        outline=TINTA, width=lw)
                for xx_ in range(-r + 10, r, 30):
                    d.line((*P(xx_, hc - r + 5), *P(xx_ * 1.08, hc - 40)), fill=(40, 70, 160), width=int(9 * K))
                d.rectangle((*P(-r - 6, hc - 48), *P(r + 6, hc - 34)), fill=(232, 186, 60), outline=TINTA,
                            width=int(4 * K))
                d.ellipse((*P(-12, hc - r - 26), *P(12, hc - r + 4)), fill=(232, 186, 60), outline=TINTA,
                          width=int(4 * K))
            elif self.peinado == "melena":
                d.chord((*P(-r - 6, hc - r - 6), *P(r + 6, hc + r - 70)), 180, 360, fill=pelo, outline=TINTA,
                        width=lw)
                d.rectangle((*P(-r + 8, hc - 64), *P(r - 8, hc - 44)), fill=pelo)
            if self.sombrero == "diadema":
                d.arc((*P(-r, hc - r - 6), *P(r, hc + r - 60)), 200, 340, fill=(232, 186, 60), width=int(14 * K))
                d.ellipse((*P(-14, hc - r - 14), *P(14, hc - r + 14)), fill=(232, 186, 60), outline=TINTA,
                          width=int(4 * K))
                d.ellipse((*P(-6, hc - r - 6), *P(6, hc - r + 6)), fill=(40, 90, 170))
            if self.sombrero not in ("piel", "copa", "nemes") and self.peinado == "normal":
                d.chord((*P(-r + 4, hc - r + 2), *P(r - 4, hc + r - 30)), 185, 355, fill=pelo,
                        outline=TINTA, width=lw)
                if self.estilo == "napoleon":  # mechón característico
                    d.polygon([P(-20, hc - 72), P(10, hc - 40), P(25, hc - 74)], fill=pelo)
            # cara
            parpadeo = (t * 0.9 + fase) % 3.7 < 0.12
            for sx in (-1, 1):
                ex, ey = sx * 40, hc - 8
                if parpadeo:
                    d.line((*P(ex - 22, ey), *P(ex + 22, ey)), fill=TINTA, width=int(6 * K))
                    continue
                esc = 1.2 if expresion == "sorpresa" else 1.0
                E(ex - 25 * esc, ey - 30 * esc, ex + 25 * esc, ey + 30 * esc, (255, 255, 255), 5)
                px, py = ex + mirar[0] * 10, ey + 4 + mirar[1] * 12
                d.ellipse((*P(px - 11, py - 11), *P(px + 11, py + 11)), fill=TINTA)
                d.ellipse((*P(px - 4, py - 7), *P(px + 1, py - 2)), fill=(255, 255, 255))
                # cejas
                by = ey - 42
                if expresion == "enojado":
                    d.line((*P(ex - 26 * sx, by + 12), *P(ex + 22 * sx, by - 10)), fill=TINTA, width=int(9 * K))
                elif expresion == "triste":
                    d.line((*P(ex - 24 * sx, by - 10), *P(ex + 22 * sx, by + 6)), fill=TINTA, width=int(8 * K))
                elif expresion == "sorpresa":
                    d.arc((*P(ex - 26, by - 26), *P(ex + 26, by + 6)), 200, 340, fill=TINTA, width=int(7 * K))
                elif expresion == "serio":
                    d.line((*P(ex - 24, by + 4), *P(ex + 24, by + 4)), fill=TINTA, width=int(8 * K))
            if self.barba:
                d.chord((*P(-r + 6, hc - 10), *P(r - 6, hc + r + 40)), 10, 170, fill=pelo, outline=TINTA,
                        width=int(5 * K))
            if self.bigote:
                d.chord((*P(-50, hc + 22), *P(0, hc + 52)), 180, 360, fill=pelo)
                d.chord((*P(0, hc + 22), *P(50, hc + 52)), 180, 360, fill=pelo)
            my = hc + 56
            abierto = habla
            if expresion == "sorpresa":
                abierto = max(abierto, 0.6)
            if expresion == "risa":
                abierto = max(abierto, 0.35 + 0.35 * abs(math.sin(t * 14)))
            if abierto > 0.08:
                hw, hh = 18 + 12 * abierto, 6 + 26 * abierto
                E(-hw, my - hh, hw, my + hh, (120, 20, 30), 5)
                d.chord((*P(-hw * 0.6, my), *P(hw * 0.6, my + hh * 0.9)), 0, 180, fill=(230, 90, 100))
            elif expresion in ("enojado", "triste"):
                d.arc((*P(-24, my - 2), *P(24, my + 22)), 200, 340, fill=TINTA, width=int(6 * K))
            elif expresion == "serio":
                d.line((*P(-18, my + 4), *P(18, my + 4)), fill=TINTA, width=int(6 * K))
            else:
                d.arc((*P(-24, my - 18), *P(24, my + 8)), 20, 160, fill=TINTA, width=int(6 * K))
            # sombreros
            top = hc - r
            if self.sombrero == "bicornio":
                d.chord((*P(-175, top - 60), *P(175, top + 85)), 180, 360, fill=(28, 26, 34), outline=TINTA,
                        width=lw)
                d.arc((*P(-165, top - 52), *P(165, top + 78)), 195, 345, fill=(214, 170, 60), width=int(6 * K))
                for rr, c in ((26, (30, 60, 160)), (18, (245, 245, 245)), (10, (210, 30, 40))):
                    d.ellipse((*P(60 - rr, top - 20 - rr), *P(60 + rr, top - 20 + rr)), fill=c)
            elif self.sombrero == "piel":
                d.rounded_rectangle((*P(-95, top - 190), *P(95, top + 45)), radius=int(80 * K), fill=(20, 18, 22),
                                    outline=TINTA, width=lw)
                for i in range(18):
                    rx = random.Random(i).uniform(-80, 80)
                    ry = random.Random(i + 50).uniform(-170, 20)
                    d.arc((*P(rx - 14, top + ry - 8), *P(rx + 14, top + ry + 8)), 200, 340, fill=(55, 50, 60),
                          width=int(3 * K))
                d.rectangle((*P(-96, top + 30), *P(96, top + 46)), fill=(200, 30, 40), outline=TINTA,
                            width=int(4 * K))
            elif self.sombrero == "copa":
                d.rectangle((*P(-75, top - 150), *P(75, top + 20)), fill=(24, 22, 28), outline=TINTA, width=lw)
                d.rectangle((*P(-75, top - 10), *P(75, top + 12)), fill=(150, 30, 40))
                d.rounded_rectangle((*P(-130, top + 10), *P(130, top + 34)), radius=int(12 * K), fill=(24, 22, 28),
                                    outline=TINTA, width=lw)
            elif self.sombrero == "casco":
                d.ellipse((*P(-r - 32, hc - r - 32), *P(r + 32, hc + r + 32)), outline=(235, 235, 240),
                          width=int(16 * K))
                d.ellipse((*P(-r - 32, hc - r - 32), *P(r + 32, hc + r + 32)), outline=TINTA, width=int(5 * K))
                d.arc((*P(-r - 5, hc - r - 5), *P(r - 25, hc + r - 25)), 200, 250, fill=(255, 255, 255, 200),
                      width=int(12 * K))

        img = suave(dib, ancho, alto)
        if s != 1.0:
            img = img.resize((max(1, int(ancho * s)), max(1, int(alto * s))), Image.BILINEAR)
        return img, ox * s, oy * s

    def dibujar(self, lienzo, x, y, s, t, **kw):
        bob = 5 * s * math.sin(t * 2.6 + self.fase)
        img, ox, oy = self.render(s, t, **kw)
        lienzo.alpha_composite(img, (int(x - ox), int(y - oy + bob)))


# =========================================================================== #
# FONDOS (estilo caricatura, con contorno y textura)
# =========================================================================== #
def fondo_salon(variante=0) -> Image.Image:
    def dib(d, k):
        r = random.Random(variante)
        piso = 1380
        # muro de piedra
        d.rectangle((0, 0, W * k, piso * k), fill=(120, 112, 150))
        fila_h = 70
        for fy, y in enumerate(range(0, piso, fila_h)):
            off = (fy % 2) * 60
            for x in range(-off, W, 120):
                c = r.randint(-12, 12)
                d.rectangle((x * k + 3 * k, y * k + 3 * k, (x + 120) * k - 3 * k, (y + fila_h) * k - 3 * k),
                            fill=(118 + c, 110 + c, 150 + c), outline=(70, 62, 96), width=int(3 * k))
        # ventana arqueada con luz
        d.rectangle((420 * k, 260 * k, 660 * k, 700 * k), fill=(255, 236, 170), outline=TINTA, width=int(8 * k))
        d.pieslice((420 * k, 140 * k, 660 * k, 380 * k), 180, 360, fill=(255, 236, 170), outline=TINTA,
                   width=int(8 * k))
        d.line((540 * k, 150 * k, 540 * k, 700 * k), fill=TINTA, width=int(8 * k))
        d.line((420 * k, 440 * k, 660 * k, 440 * k), fill=TINTA, width=int(8 * k))
        # estandartes con la N imperial
        for bx in (110, 830):
            d.rectangle(((bx - 10) * k, 120 * k, (bx + 150) * k, 135 * k), fill=(90, 60, 30), outline=TINTA,
                        width=int(5 * k))
            d.polygon([(bx * k, 135 * k), ((bx + 140) * k, 135 * k), ((bx + 140) * k, 760 * k),
                       ((bx + 70) * k, 700 * k), (bx * k, 760 * k)], fill=(40, 60, 150), outline=TINTA)
            d.rectangle(((bx + 18) * k, 150 * k, (bx + 122) * k, 690 * k), outline=(214, 170, 60),
                        width=int(6 * k))
            f = fuente(110 * k)
            d.text(((bx + 70) * k, 400 * k), "N", font=f, fill=(232, 186, 60), anchor="mm")
        # piso de madera en perspectiva
        d.rectangle((0, piso * k, W * k, H * k), fill=(150, 92, 50))
        for i in range(-12, 13):
            d.line(((540 + i * 40) * k, piso * k, (540 + i * 190) * k, H * k), fill=(110, 64, 34), width=int(5 * k))
        for j, y in enumerate((1430, 1500, 1590, 1700, 1840)):
            d.line((0, y * k, W * k, y * k), fill=(120, 72, 38), width=int(4 * k))
        d.line((0, piso * k, W * k, piso * k), fill=TINTA, width=int(8 * k))
        # rayo de luz
        d.polygon([(430 * k, 700 * k), (650 * k, 700 * k), (900 * k, 1900 * k), (250 * k, 1900 * k)],
                  fill=(255, 240, 190, 50))
    return suave(dib, W, H)


def fondo_patio() -> Image.Image:
    def dib(d, k):
        piso = 1330
        for y in range(0, piso, 8):
            f = y / piso
            d.rectangle((0, y * k, W * k, (y + 8) * k), fill=(int(90 + 90 * f), int(160 + 60 * f), int(235 - 10 * f)))
        for cx, cy, s in ((200, 260, 1.0), (760, 180, 1.3), (980, 430, 0.8)):
            for dx, dy, rr in ((-60, 10, 55), (0, -20, 70), (60, 10, 55), (0, 25, 60)):
                d.ellipse(((cx + dx * s - rr * s) * k, (cy + dy * s - rr * s) * k, (cx + dx * s + rr * s) * k,
                           (cy + dy * s + rr * s) * k), fill=(255, 255, 255), outline=(200, 215, 235),
                          width=int(4 * k))
        # palacio al fondo
        d.rectangle((60 * k, 700 * k, 1020 * k, piso * k), fill=(236, 210, 150), outline=TINTA, width=int(8 * k))
        d.polygon([(40 * k, 700 * k), (540 * k, 560 * k), (1040 * k, 700 * k)], fill=(70, 80, 120), outline=TINTA)
        for row in range(3):
            for col in range(8):
                x = 110 + col * 115
                y = 760 + row * 180
                d.rounded_rectangle((x * k, y * k, (x + 60) * k, (y + 120) * k), radius=int(24 * k),
                                    fill=(70, 110, 170), outline=TINTA, width=int(5 * k))
        d.rectangle((470 * k, 1130 * k, 610 * k, piso * k), fill=(110, 60, 30), outline=TINTA, width=int(6 * k))
        # bandera francesa
        d.line((540 * k, 560 * k, 540 * k, 380 * k), fill=TINTA, width=int(8 * k))
        for i, c in enumerate(((30, 60, 160), (245, 245, 245), (210, 30, 40))):
            d.rectangle(((544 + i * 50) * k, 385 * k, (594 + i * 50) * k, 480 * k), fill=c)
        # empedrado
        d.rectangle((0, piso * k, W * k, H * k), fill=(150, 140, 160))
        r = random.Random(3)
        for y in range(piso, H, 46):
            for x in range(-40 + (y // 46 % 2) * 40, W, 84):
                c = r.randint(-15, 15)
                d.rounded_rectangle(((x + 4) * k, (y + 4) * k, (x + 80) * k, (y + 42) * k), radius=int(16 * k),
                                    fill=(160 + c, 150 + c, 172 + c), outline=(100, 92, 115), width=int(4 * k))
        d.line((0, piso * k, W * k, piso * k), fill=TINTA, width=int(8 * k))
    return suave(dib, W, H)


def fondo_taller() -> Image.Image:
    def dib(d, k):
        piso = 1250
        d.rectangle((0, 0, W * k, piso * k), fill=(176, 120, 72))
        for x in range(0, W, 90):
            d.rectangle((x * k, 0, (x + 90) * k, piso * k), outline=(120, 76, 40), width=int(5 * k))
        # estante con libros
        d.rectangle((60 * k, 330 * k, 1020 * k, 350 * k), fill=(100, 60, 30), outline=TINTA, width=int(5 * k))
        r = random.Random(5)
        x = 80
        while x < 1000:
            w = r.randint(26, 50)
            h = r.randint(110, 170)
            col = r.choice([(170, 40, 50), (40, 80, 150), (60, 120, 70), (200, 160, 60), (100, 50, 120)])
            d.rectangle((x * k, (330 - h) * k, (x + w) * k, 330 * k), fill=col, outline=TINTA, width=int(4 * k))
            x += w + 4
        # mesa
        d.rectangle((0, piso * k, W * k, H * k), fill=(96, 58, 30))
        d.rectangle((0, (piso - 20) * k, W * k, (piso + 30) * k), fill=(130, 80, 40), outline=TINTA,
                    width=int(7 * k))
        for y in range(piso + 60, H, 70):
            d.line((0, y * k, W * k, (y + 10) * k), fill=(80, 46, 22), width=int(4 * k))
    return suave(dib, W, H)


# =========================================================================== #
# OVERLAYS (sobre la cámara)
# =========================================================================== #
def texto_sombra(img, xy, txt, tam, color=(255, 255, 255), anchor="mm", borde=4, sombra=True, alfa=255):
    if tam < 8:
        return
    f = fuente(tam)
    if sombra:
        capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(capa).text((xy[0], xy[1] + tam * 0.08), txt, font=f, fill=(0, 0, 0, int(200 * alfa / 255)),
                                  anchor=anchor, stroke_width=borde + 2, stroke_fill=(0, 0, 0, int(200 * alfa / 255)))
        bbox = capa.getbbox()
        if bbox:
            x0, y0, x1, y1 = bbox
            pad = 20
            reg = (max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad))
            img.alpha_composite(capa.crop(reg).filter(ImageFilter.GaussianBlur(8)), reg[:2])
    ImageDraw.Draw(img).text(xy, txt, font=f, fill=color + (alfa,), anchor=anchor, stroke_width=borde,
                             stroke_fill=(20, 16, 22, alfa))


def subtitulo(img, grupos, t):
    for i, g in enumerate(grupos):
        fin = grupos[i + 1][0].inicio if i + 1 < len(grupos) else 1e9
        if g[0].inicio - 0.04 <= t < fin:
            txt = " ".join(p.texto.strip(",.;:") for p in g)
            esc = 0.85 + 0.15 * pop((t - g[0].inicio + 0.04) / 0.14)
            texto_sombra(img, (W / 2, 1480), txt, int(84 * esc), borde=5)
            return


def flecha(img, x, y, ang, largo, t, color=(230, 30, 40)):
    """Flecha roja que apunta a (x, y) desde el ángulo dado, con rebote."""
    reb = 14 * abs(math.sin(t * 5))
    a = math.radians(ang)
    tx, ty = x - math.cos(a) * reb, y - math.sin(a) * reb
    sx, sy = tx - math.cos(a) * largo, ty - math.sin(a) * largo

    def dib(d, k):
        for col, wd in ((TINTA, 22), (color + (255,), 12)):
            d.line((sx * k, sy * k, tx * k, ty * k), fill=col, width=int(wd * k))
        p1 = (tx + math.cos(a) * 8, ty + math.sin(a) * 8)
        izq = (tx - math.cos(a - 0.5) * 50, ty - math.sin(a - 0.5) * 50)
        der = (tx - math.cos(a + 0.5) * 50, ty - math.sin(a + 0.5) * 50)
        d.polygon([(p1[0] * k, p1[1] * k), (izq[0] * k, izq[1] * k), (der[0] * k, der[1] * k)],
                  fill=color + (255,), outline=TINTA, width=int(5 * k))
    img.alpha_composite(suave(dib, W, H))


def etiqueta(img, x, y, txt, t, t0=0.0):
    if t < t0:
        return
    p = pop((t - t0) / 0.25)
    texto_sombra(img, (x, y), txt.upper(), max(10, int(48 * p)), color=(255, 214, 40), borde=4)


def dato_grande(img, grande, chico, t, t0=0.0, y=420):
    if t < t0:
        return
    p = pop((t - t0) / 0.3)
    texto_sombra(img, (W / 2, y), grande, max(10, int(130 * p)), color=(235, 40, 50), borde=7)
    if chico:
        texto_sombra(img, (W / 2, y + 95), chico, max(10, int(40 * p)), borde=3)


def pildora(img, txt, t, t0, dur=4.0, y=1640):
    if not (t0 <= t < t0 + dur):
        return
    a = min(1, (t - t0) / 0.25, (t0 + dur - t) / 0.25)
    f = fuente(36)
    w = ImageDraw.Draw(img).textlength(txt, font=f) + 70

    def dib(d, k):
        x0 = (W - w) / 2
        d.rounded_rectangle((x0 * k, (y - 34) * k, (x0 + w) * k, (y + 34) * k), radius=int(34 * k),
                            fill=(225, 35, 45, int(255 * a)), outline=(255, 255, 255, int(255 * a)), width=int(4 * k))
    img.alpha_composite(suave(dib, W, H))
    ImageDraw.Draw(img).text((W / 2, y), txt, font=f, fill=(255, 255, 255, int(255 * a)), anchor="mm")


def encuesta(img, pregunta, op1, op2, t, t0):
    if t < t0:
        return
    p = pop((t - t0) / 0.35)

    def dib(d, k):
        cx, cy = W / 2, 760
        bw, bh = 330 * p, 190 * p
        d.rounded_rectangle(((cx - 440 * p) * k, (cy - 230 * p) * k, (cx + 440 * p) * k, (cy - 140 * p) * k),
                            radius=int(26 * k), fill=(255, 255, 255, 240), outline=TINTA, width=int(5 * k))
        for sx, col in ((-1, (240, 90, 40)), (1, (40, 100, 220))):
            x0 = cx + sx * 40 * p - (bw if sx < 0 else 0)
            d.rounded_rectangle((x0 * k, (cy - 100 * p) * k, (x0 + bw) * k, (cy - 100 * p + bh) * k),
                                radius=int(30 * k), fill=col + (255,), outline=(255, 255, 255), width=int(7 * k))
        d.ellipse(((cx - 50 * p) * k, (cy - 50 * p) * k, (cx + 50 * p) * k, (cy + 50 * p) * k), fill=(20, 20, 30),
                  outline=(255, 255, 255), width=int(5 * k))
        d.rounded_rectangle(((cx - 260 * p) * k, (cy + 140 * p) * k, (cx + 260 * p) * k, (cy + 210 * p) * k),
                            radius=int(30 * k), fill=(255, 255, 255, 240), outline=TINTA, width=int(4 * k))
    img.alpha_composite(suave(dib, W, H))
    d = ImageDraw.Draw(img)
    if p > 0.5:
        cx, cy = W / 2, 760
        d.text((cx, cy - 185 * p), pregunta, font=fuente(int(44 * p)), fill=(20, 20, 30), anchor="mm")
        for sx, txt in ((-1, op1), (1, op2)):
            bx = cx + sx * (40 + 165) * p
            lineas = txt.split("\n")
            for i, ln in enumerate(lineas):
                d.text((bx, cy - 5 * p + (i - (len(lineas) - 1) / 2) * 52 * p), ln, font=fuente(int(46 * p)),
                       fill=(255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, 120))
        d.text((cx, cy), "VS", font=fuente(int(42 * p)), fill=(255, 255, 255), anchor="mm")
        d.text((cx, cy + 175 * p), "💬 TE LEO EN COMENTARIOS".replace("💬 ", ""), font=fuente(int(34 * p)),
               fill=(20, 20, 30), anchor="mm")


# =========================================================================== #
# ESCENAS DE LA HISTORIA 2: NAPOLEÓN
# =========================================================================== #
def napoleon(semilla=1):
    return Personaje(ropa="#2b3d8f", piel="#f6dcc0", pelo="#3a2416", sombrero="bicornio", estilo="napoleon",
                     semilla=semilla)


class Escena:
    camara = (1.0, 1.08, 0.5, 0.55)  # zoom inicial, zoom final, foco x, foco y

    def mundo(self, t, dur):  # lo que se mueve con la cámara
        raise NotImplementedError

    def encima(self, img, t, dur):  # textos/flechas fijos en pantalla
        pass


class NapIntro(Escena):
    camara = (1.0, 1.12, 0.5, 0.62)

    def __init__(self):
        self.fondo = fondo_salon(0)
        self.nap = napoleon()
        self.c1 = Personaje(ropa="#8a2f45", pelo="#c08a3a", semilla=4)
        self.c2 = Personaje(ropa="#2f7a55", pelo="#1e1a18", bigote=True, semilla=7)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.c1.dibujar(img, 190, 1560, 0.95, t, expresion="risa", mirar=(1, 0))
        self.c2.dibujar(img, 890, 1560, 0.95, t, expresion="risa", mirar=(-1, 0), brazos="arriba")
        self.nap.dibujar(img, 540, 1700, 1.3, t, expresion="enojado" if t > dur * 0.55 else "sorpresa",
                         mirar=(0, 0))
        return img

    def encima(self, img, t, dur):
        etiqueta(img, 540, 470, "¿bajito?", t, 0.6)
        if t > 0.6:
            flecha(img, 540, 760, 90, 170, t)


class NapEstatura(Escena):
    camara = (1.08, 1.0, 0.5, 0.6)

    def __init__(self):
        base = fondo_salon(1)
        piso = 1700
        px_m = 640 / 1.69  # altura de Napoleón en pantalla (s=1.3) ≈ 1,69 m

        def dib(d, k):
            x0, x1 = 60, 220
            d.rectangle((x0 * k, (piso - 1.95 * px_m) * k, x1 * k, piso * k), fill=(250, 240, 210), outline=TINTA,
                        width=int(6 * k))
            for cm in range(100, 196, 5):
                y = piso - cm / 100 * px_m
                largo = 70 if cm % 10 == 0 else 35
                d.line((x0 * k, y * k, (x0 + largo) * k, y * k), fill=TINTA, width=int(4 * k))
                if cm % 10 == 0:
                    d.text(((x0 + 80) * k, y * k), f"{cm / 100:.2f}".replace(".", ","), font=fuente(26 * k),
                           fill=TINTA, anchor="lm")
        base.alpha_composite(suave(dib, W, H))
        self.fondo, self.piso, self.px_m = base, piso, px_m
        self.nap = napoleon(2)
        self.f1 = Personaje(ropa="#6a6a2a", pelo="#7a4a2a", semilla=11)
        self.f2 = Personaje(ropa="#8a3a2a", pelo="#d0a040", semilla=12)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.f1.dibujar(img, 400, self.piso, 1.3, t, mirar=(1, 0))
        self.nap.dibujar(img, 655, self.piso, 1.3, t, expresion="serio", mirar=(-1, 0))
        self.f2.dibujar(img, 910, self.piso, 1.3, t, mirar=(-1, 0))
        y = self.piso - 1.69 * self.px_m
        p = ease((t - 0.8) / 0.8)
        if p > 0:
            d = ImageDraw.Draw(img)
            for x in range(60, int(60 + 1000 * p), 40):
                d.line((x, y, x + 22, y), fill=(255, 214, 40), width=6)
        return img

    def encima(self, img, t, dur):
        dato_grande(img, "1,69 m", "su estatura real", t, 0.8, y=330)
        etiqueta(img, 655, 880, "igual al promedio", t, dur * 0.55)


class NapPulgadas(Escena):
    camara = (1.0, 1.1, 0.5, 0.65)

    def __init__(self):
        self.fondo = fondo_taller()
        self.ingles = Personaje(ropa="#a03030", pelo="#d8b070", sombrero="copa", bigote=True, semilla=21)

    def regla(self, img, y, largo_px, color, t, t0, rotulo):
        p = ease((t - t0) / 0.6)
        if p <= 0:
            return
        x0 = 60 - (1 - p) * 900
        largo = largo_px

        def dib(d, k):
            d.rounded_rectangle((x0 * k, (y - 45) * k, (x0 + largo) * k, (y + 45) * k), radius=int(10 * k),
                                fill=color + (255,), outline=TINTA, width=int(6 * k))
            for i in range(0, int(largo) + 1, int(largo / 10)):
                h = 40 if i % int(largo / 2) == 0 else 20
                d.line(((x0 + i) * k, (y - 45) * k, (x0 + i) * k, (y - 45 + h) * k), fill=TINTA, width=int(4 * k))
        img.alpha_composite(suave(dib, W, H))
        ImageDraw.Draw(img).text((x0 + 25, y + 12), rotulo, font=fuente(32), fill=(30, 20, 20), anchor="lm")

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.ingles.dibujar(img, 800, 1240, 1.15, t, expresion="sorpresa", mirar=(-1, 1))
        self.regla(img, 1640, 271 * 3.1, (250, 214, 90), t, 0.3, "PULGADA FRANCESA")
        self.regla(img, 1790, 254 * 3.1, (235, 235, 225), t, 0.8, "PULGADA INGLESA")
        return img

    def encima(self, img, t, dur):
        if t > 1.0:
            texto_sombra(img, (W / 2, 1200), "2,71 cm  vs  2,54 cm", 54, color=(255, 214, 40), borde=4)
        dato_grande(img, "5 pies 2 pulg.", "medida francesa = 1,69 m", t, dur * 0.45, y=330)


class NapCaricatura(Escena):
    camara = (1.05, 1.15, 0.45, 0.45)

    def __init__(self):
        self.fondo = fondo_taller()
        self.dibujante = Personaje(ropa="#3a5a3a", pelo="#b0b0b0", sombrero="copa", bigote=True, semilla=31)
        self.mini = napoleon(5)

    def mundo(self, t, dur):
        img = self.fondo.copy()

        def dib(d, k):
            d.rectangle((90 * k, 420 * k, 760 * k, 1230 * k), fill=(240, 226, 190), outline=TINTA, width=int(8 * k))
            d.rectangle((120 * k, 450 * k, 730 * k, 1200 * k), outline=(120, 90, 60), width=int(4 * k))
            d.text((425 * k, 520 * k), "LITTLE BONEY", font=fuente(64 * k), fill=(60, 30, 20), anchor="mm")
            d.line((160 * k, 1120 * k, 690 * k, 1120 * k), fill=(120, 90, 60), width=int(4 * k))
        img.alpha_composite(suave(dib, W, H))
        salto = abs(math.sin(t * 6)) * 60
        self.mini.dibujar(img, 425, 1110 - salto, 0.62, t * 2, expresion="enojado", brazos="arriba")
        self.dibujante.dibujar(img, 850, 1640, 1.15, t, expresion="risa", mirar=(-1, -0.5))
        return img

    def encima(self, img, t, dur):
        etiqueta(img, 425, 250, "caricatura británica", t, 0.5)
        if t > 0.5:
            flecha(img, 425, 425, 90, 120, t)


class NapGuardia(Escena):
    camara = (1.12, 1.0, 0.5, 0.6)

    def __init__(self):
        self.fondo = fondo_patio()
        self.nap = napoleon(6)
        self.guardias = [Personaje(ropa="#24357a", sombrero="piel", estilo="granadero", altura=1.28, semilla=40 + i)
                         for i in range(4)]

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for g, x in zip(self.guardias, (110, 330, 750, 970)):
            g.dibujar(img, x, 1720, 1.05, t, expresion="serio", mirar=(0, 0))
        self.nap.dibujar(img, 540, 1740, 1.05, t, expresion="triste", mirar=(0, -1))
        return img

    def encima(self, img, t, dur):
        etiqueta(img, 330, 560, "guardia imperial", t, 0.6)
        if t > 0.6:
            flecha(img, 330, 860, 90, 220, t)
        pildora(img, "¡SUSCRÍBETE Y COMENTA!", t, 1.0, 3.5)


class NapFinal(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        self.fondo = fondo_salon(2)
        self.nap = napoleon(8)
        self.t_encuesta = 0.0

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.nap.dibujar(img, 540, 1760, 1.3, t, expresion="enojado", brazos="cruzados", mirar=(0.5, 0))
        return img

    def encima(self, img, t, dur):
        encuesta(img, "¿Sabías que no era bajito?", "SÍ, LO\nSABÍA", "NI\nIDEA", t, dur * 0.45)


ESCENAS = {"nap_intro": NapIntro, "nap_estatura": NapEstatura, "nap_pulgadas": NapPulgadas,
           "nap_caricatura": NapCaricatura, "nap_guardia": NapGuardia, "nap_final": NapFinal}


# =========================================================================== #
# ESCENAS DE LA HISTORIA 3: CLEOPATRA Y LA LUNA
# =========================================================================== #
ORO, AZUL_EG = (232, 186, 60), (40, 70, 160)


def _piramide(d, k, cx, base, ancho, alto):
    izq, der, cima = (cx - ancho / 2, base), (cx + ancho / 2, base), (cx + ancho * 0.08, base - alto)
    d.polygon([(izq[0] * k, izq[1] * k), (cima[0] * k, cima[1] * k), (cx * k + ancho * 0.08 * k, base * k)],
              fill=(240, 200, 120))
    d.polygon([(cx * k + ancho * 0.08 * k, base * k), (cima[0] * k, cima[1] * k), (der[0] * k, der[1] * k)],
              fill=(200, 150, 80))
    for i in range(1, 9):
        f = i / 9
        y = base - alto * f
        xl = izq[0] + (cima[0] - izq[0]) * f
        xr = der[0] + (cima[0] - der[0]) * f
        d.line((xl * k, y * k, xr * k, y * k), fill=(170, 120, 60), width=int(3 * k))
    d.polygon([(izq[0] * k, izq[1] * k), (cima[0] * k, cima[1] * k), (der[0] * k, der[1] * k)], outline=TINTA,
              width=int(7 * k))


def fondo_desierto(variante=0) -> Image.Image:
    def dib(d, k):
        hz = 1250
        for y in range(0, hz, 8):
            f = y / hz
            d.rectangle((0, y * k, W * k, (y + 8) * k),
                        fill=(int(80 + 170 * f), int(160 + 70 * f), int(230 - 60 * f)))
        d.ellipse((780 * k, 180 * k, 960 * k, 360 * k), fill=(255, 230, 120), outline=(255, 200, 80),
                  width=int(8 * k))
        if variante == 0:
            _piramide(d, k, 560, hz + 20, 980, 820)
        else:
            _piramide(d, k, 300, hz + 10, 520, 430)
            _piramide(d, k, 720, hz + 10, 620, 520)
            _piramide(d, k, 980, hz + 10, 300, 240)
        for i, (y0, col) in enumerate(((hz - 20, (236, 196, 120)), (hz + 120, (226, 180, 100)),
                                       (hz + 300, (214, 166, 86)))):
            pts = [(0, H * k)]
            for x in range(0, W + 60, 60):
                pts.append((x * k, (y0 + 40 * math.sin(x / 160 + i * 2)) * k))
            pts.append((W * k, H * k))
            d.polygon(pts, fill=col)
            d.line(pts[1:-1], fill=(150, 100, 50), width=int(6 * k))
    return suave(dib, W, H)


def fondo_egipcio(variante=0) -> Image.Image:
    def dib(d, k):
        piso = 1380
        r = random.Random(variante + 20)
        d.rectangle((0, 0, W * k, piso * k), fill=(222, 182, 120))
        for fy, y in enumerate(range(0, piso, 80)):
            off = (fy % 2) * 70
            for x in range(-off, W, 140):
                c = r.randint(-10, 10)
                d.rectangle(((x + 3) * k, (y + 3) * k, (x + 137) * k, (y + 77) * k), fill=(222 + c, 182 + c, 120 + c),
                            outline=(170, 130, 80), width=int(3 * k))
        # jeroglíficos simples
        for i in range(14):
            x, y = 330 + (i % 7) * 62, 300 + (i // 7) * 110
            tipo = i % 4
            if tipo == 0:
                d.ellipse((x * k, (y + 10) * k, (x + 44) * k, (y + 34) * k), outline=TINTA, width=int(5 * k))
                d.ellipse(((x + 16) * k, (y + 14) * k, (x + 28) * k, (y + 28) * k), fill=TINTA)
            elif tipo == 1:
                d.line((x * k, (y + 40) * k, (x + 40) * k, (y + 40) * k), fill=TINTA, width=int(5 * k))
                d.line(((x + 20) * k, y * k, (x + 20) * k, (y + 40) * k), fill=TINTA, width=int(5 * k))
                d.ellipse(((x + 8) * k, (y - 10) * k, (x + 32) * k, (y + 12) * k), outline=TINTA, width=int(5 * k))
            elif tipo == 2:
                d.arc((x * k, y * k, (x + 44) * k, (y + 44) * k), 180, 360, fill=TINTA, width=int(5 * k))
                d.line((x * k, (y + 22) * k, (x + 44) * k, (y + 22) * k), fill=TINTA, width=int(5 * k))
            else:
                d.polygon([(x * k, (y + 40) * k), ((x + 22) * k, y * k), ((x + 44) * k, (y + 40) * k)],
                          outline=TINTA, width=int(5 * k))
        # columnas
        for cx in (130, 950):
            d.rectangle(((cx - 70) * k, 150 * k, (cx + 70) * k, piso * k), fill=(236, 214, 170), outline=TINTA,
                        width=int(7 * k))
            for j in range(3):
                d.line(((cx - 35 + j * 35) * k, 230 * k, (cx - 35 + j * 35) * k, piso * k), fill=(190, 160, 110),
                       width=int(5 * k))
            d.polygon([((cx - 110) * k, 150 * k), ((cx + 110) * k, 150 * k), ((cx + 70) * k, 240 * k),
                       ((cx - 70) * k, 240 * k)], fill=(70, 150, 110), outline=TINTA)
            for j in range(4):
                d.rectangle(((cx - 70) * k, (260 + j * 300) * k, (cx + 70) * k, (280 + j * 300) * k),
                            fill=ORO + (255,), outline=TINTA, width=int(3 * k))
        d.rectangle((0, piso * k, W * k, H * k), fill=(180, 130, 80))
        for i in range(-12, 13):
            d.line(((540 + i * 50) * k, piso * k, (540 + i * 200) * k, H * k), fill=(150, 104, 60), width=int(5 * k))
        d.line((0, piso * k, W * k, piso * k), fill=TINTA, width=int(8 * k))
        d.polygon([(330 * k, 0), (750 * k, 0), (900 * k, 1900 * k), (180 * k, 1900 * k)], fill=(255, 240, 190, 45))
    return suave(dib, W, H)


def fondo_artico() -> Image.Image:
    def dib(d, k):
        for y in range(0, 1100, 8):
            f = y / 1100
            d.rectangle((0, y * k, W * k, (y + 8) * k), fill=(int(170 + 60 * f), int(205 + 40 * f), 250))
        for x0, h in ((-100, 380), (250, 300), (600, 420), (880, 330)):
            d.polygon([(x0 * k, 1100 * k), ((x0 + 220) * k, (1100 - h) * k), ((x0 + 440) * k, 1100 * k)],
                      fill=(230, 238, 250), outline=TINTA, width=int(6 * k))
            d.polygon([((x0 + 220) * k, (1100 - h) * k), ((x0 + 290) * k, (1100 - h * 0.6) * k),
                       ((x0 + 440) * k, 1100 * k), ((x0 + 220) * k, 1100 * k)], fill=(190, 205, 230))
        d.rectangle((0, 1100 * k, W * k, 1300 * k), fill=(50, 100, 170))
        for i in range(8):
            x = 60 + i * 130
            d.ellipse((x * k, (1140 + (i % 2) * 60) * k, (x + 110) * k, (1170 + (i % 2) * 60) * k),
                      fill=(240, 248, 255), outline=TINTA, width=int(4 * k))
        pts = [(0, H * k)] + [(x * k, (1300 + 25 * math.sin(x / 120)) * k) for x in range(0, W + 40, 40)] + \
              [(W * k, H * k)]
        d.polygon(pts, fill=(245, 250, 255))
        d.line(pts[1:-1], fill=TINTA, width=int(7 * k))
    return suave(dib, W, H)


def fondo_luna() -> Image.Image:
    def dib(d, k):
        d.rectangle((0, 0, W * k, H * k), fill=(10, 12, 28))
        r = random.Random(7)
        for _ in range(140):
            x, y, rr = r.randint(0, W), r.randint(0, 1200), r.choice((2, 3, 4))
            d.ellipse(((x - rr) * k, (y - rr) * k, (x + rr) * k, (y + rr) * k), fill=(255, 255, 230))
        d.ellipse((700 * k, 220 * k, 960 * k, 480 * k), fill=(60, 120, 220), outline=TINTA, width=int(7 * k))
        for cx, cy, rr in ((780, 300, 50), (870, 380, 60), (760, 410, 30)):
            d.ellipse(((cx - rr) * k, (cy - rr * 0.7) * k, (cx + rr) * k, (cy + rr * 0.7) * k), fill=(70, 170, 90))
        pts = [(0, H * k)] + [(x * k, (1250 + 30 * math.sin(x / 200)) * k) for x in range(0, W + 40, 40)] + \
              [(W * k, H * k)]
        d.polygon(pts, fill=(170, 170, 180))
        d.line(pts[1:-1], fill=TINTA, width=int(7 * k))
        for cx, cy, rr in ((150, 1450, 80), (820, 1400, 60), (500, 1750, 110), (950, 1800, 70), (230, 1820, 50)):
            d.ellipse(((cx - rr) * k, (cy - rr * 0.4) * k, (cx + rr) * k, (cy + rr * 0.4) * k), fill=(130, 130, 145),
                      outline=TINTA, width=int(5 * k))
    return suave(dib, W, H)


def fondo_papel() -> Image.Image:
    def dib(d, k):
        d.rectangle((0, 0, W * k, H * k), fill=(240, 226, 190))
        for y in range(0, H, 60):
            d.line((0, y * k, W * k, y * k), fill=(225, 205, 160), width=int(2 * k))
        for x in range(0, W, 60):
            d.line((x * k, 0, x * k, H * k), fill=(225, 205, 160), width=int(2 * k))
    return suave(dib, W, H)


def dibujar_mamut(img, x, y, s, t):
    """Mamut lanudo caminando hacia la derecha. (x, y) = punto entre las patas, en el suelo."""
    paso = math.sin(t * 4)
    pel, osc, colm = (130, 80, 45), (100, 60, 32), (250, 245, 230)

    def dib(d, k):
        ox, oy = 450, 640

        def P(px, py):
            return (ox + px) * k, (oy + py) * k

        def E(x0, y0, x1, y1, fill, ow=8):
            d.ellipse((*P(x0, y0), *P(x1, y1)), fill=fill, outline=TINTA, width=int(ow * k))
        d.ellipse((*P(-240, -16), *P(240, 22)), fill=(0, 0, 0, 50))
        for i, lx in enumerate((-150, -70, 70, 150)):
            off = paso * 18 * (1 if i % 2 else -1)
            d.rounded_rectangle((*P(lx - 34 + off, -200), *P(lx + 34 + off, 0)), radius=int(20 * k),
                                fill=osc if i in (1, 2) else pel, outline=TINTA, width=int(7 * k))
        E(-230, -420, 210, -130, pel)
        E(-210, -470, 40, -300, pel)
        for i in range(10):
            hx = -190 + i * 40
            d.arc((*P(hx - 20, -300 + (i % 3) * 18), *P(hx + 20, -260 + (i % 3) * 18)), 0, 180, fill=osc,
                  width=int(5 * k))
        E(130, -520, 330, -300, pel)
        trompa = [P(310, -380), P(360, -280), P(350, -160), P(325, -120 + 10 * math.sin(t * 2)), P(290, -150),
                  P(300, -280), P(270, -360)]
        d.polygon(trompa, fill=pel)
        d.line(trompa + [trompa[0]], fill=TINTA, width=int(7 * k), joint="curve")
        d.arc((*P(230, -330), *P(420, -170)), 30, 150, fill=TINTA, width=int(24 * k))
        d.arc((*P(230, -330), *P(420, -170)), 30, 150, fill=colm, width=int(14 * k))
        E(180, -480, 222, -438, (255, 255, 255), 5)
        d.ellipse((*P(196, -468), *P(212, -452)), fill=TINTA)
        E(90, -480, 170, -360, osc, 6)
    m = suave(dib, 900, 700)
    if s != 1:
        m = m.resize((int(900 * s), int(700 * s)), Image.BILINEAR)
    img.alpha_composite(m, (int(x - 450 * s), int(y - 640 * s - 5 * s * abs(paso))))


def icono(img, tipo, x, y, s, t=0.0):
    def dib(d, k):
        cx, cy = 150, 150
        if tipo == "piramide":
            _piramide(d, k, cx, cy + 90, 260, 200)
        elif tipo == "luna":
            d.ellipse(((cx - 110) * k, (cy - 110) * k, (cx + 110) * k, (cy + 110) * k), fill=(225, 225, 210),
                      outline=TINTA, width=int(7 * k))
            for dx, dy, rr in ((-40, -30, 25), (35, 20, 32), (-20, 50, 16)):
                d.ellipse(((cx + dx - rr) * k, (cy + dy - rr) * k, (cx + dx + rr) * k, (cy + dy + rr) * k),
                          fill=(190, 190, 175), outline=TINTA, width=int(4 * k))
    ic = suave(dib, 300, 300)
    if s != 1:
        ic = ic.resize((int(300 * s), int(300 * s)), Image.BILINEAR)
    img.alpha_composite(ic, (int(x - 150 * s), int(y - 150 * s)))


def cleopatra(semilla=1):
    return Personaje(ropa="#f4f1e8", piel="#d9a878", pelo="#141018", sombrero="diadema", estilo="vestido",
                     peinado="melena", semilla=semilla)


class CleoIntro(Escena):
    camara = (1.0, 1.1, 0.5, 0.62)

    def __init__(self):
        self.fondo = fondo_egipcio(0)
        self.cleo = cleopatra()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.cleo.dibujar(img, 540, 1720, 1.35, t, expresion="sorpresa" if t < dur * 0.5 else "normal",
                          mirar=(1 if t > dur * 0.5 else -1, -0.5))
        return img

    def encima(self, img, t, dur):
        if t > dur * 0.3:
            icono(img, "luna", 860, 520, 0.8 * pop((t - dur * 0.3) / 0.3), t)
            etiqueta(img, 860, 690, "la luna", t, dur * 0.3)
        if t > dur * 0.6:
            icono(img, "piramide", 220, 520, 0.8 * pop((t - dur * 0.6) / 0.3), t)
            etiqueta(img, 220, 690, "pirámide", t, dur * 0.6)


class CleoPiramide(Escena):
    camara = (1.12, 1.0, 0.5, 0.6)

    def __init__(self):
        self.fondo = fondo_desierto(0)
        self.obreros = [Personaje(ropa="#e8dcc0", piel="#c98d5c", pelo="#141018", semilla=60 + i) for i in range(3)]
        self.keops = Personaje(ropa="#f4f1e8", piel="#c98d5c", pelo="#141018", sombrero="nemes", estilo="vestido",
                               semilla=70)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        bx = 140 + 30 * t
        d = ImageDraw.Draw(img)
        d.rectangle((bx - 90, 1490, bx + 90, 1640), fill=(230, 190, 110), outline=TINTA, width=6)
        d.line((bx + 90, 1550, bx + 560, 1520), fill=(120, 80, 40), width=8)
        for i, o in enumerate(self.obreros):
            o.dibujar(img, bx + 230 + i * 130, 1700, 0.72, t * 1.5, expresion="serio", mirar=(1, 0))
        self.keops.dibujar(img, 900, 1780, 1.0, t, expresion="serio", mirar=(-1, 0))
        return img

    def encima(self, img, t, dur):
        dato_grande(img, "4.500 años", "de antigüedad", t, 0.5, y=330)
        etiqueta(img, 880, 980, "faraón keops", t, dur * 0.5)
        if t > dur * 0.5:
            flecha(img, 880, 1150, 90, 120, t)


class CleoMamut(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        self.fondo = fondo_artico()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        dibujar_mamut(img, 180 + 70 * t, 1720, 1.05, t)
        d = ImageDraw.Draw(img)
        r = random.Random(4)
        for _ in range(70):
            x0, y0, v = r.uniform(0, W), r.uniform(0, H), r.uniform(60, 140)
            x = (x0 + 20 * math.sin(t + x0)) % W
            y = (y0 + v * t) % H
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 255, 255))
        return img

    def encima(self, img, t, dur):
        dato_grande(img, "Mamuts vivos", "hace unos 4.000 años", t, 0.4, y=330)
        etiqueta(img, 540, 620, "isla de wrangel, ártico", t, dur * 0.5)
        if t > dur * 0.55:
            icono(img, "piramide", 900, 820, 0.55 * pop((t - dur * 0.55) / 0.3))
            etiqueta(img, 900, 940, "¡a la vez!", t, dur * 0.55)


class CleoNace(Escena):
    camara = (1.0, 1.12, 0.5, 0.6)

    def __init__(self):
        self.fondo = fondo_egipcio(1)
        self.cleo = cleopatra(3)
        self.sirv = Personaje(ropa="#e8dcc0", piel="#c98d5c", pelo="#141018", semilla=80)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.sirv.dibujar(img, 880, 1640, 0.9, t, expresion="normal", brazos="arriba", mirar=(-1, 0))
        d = ImageDraw.Draw(img)
        ang = math.radians(-60 + 18 * math.sin(t * 5))
        fx, fy = 1015 + 120 * math.cos(ang), 1110 + 120 * math.sin(ang)
        d.line((1015, 1130, fx, fy), fill=(120, 80, 40), width=8)
        d.pieslice((fx - 90, fy - 90, fx + 90, fy + 90), 200, 340, fill=(70, 150, 110), outline=TINTA, width=5)
        self.cleo.dibujar(img, 480, 1730, 1.3, t, expresion="normal", mirar=(0, 0))
        return img

    def encima(self, img, t, dur):
        dato_grande(img, "69 a. C.", "nace Cleopatra", t, 0.3, y=330)
        if t > dur * 0.5:
            texto_sombra(img, (W / 2, 620), "2.500 años después", int(64 * pop((t - dur * 0.5) / 0.25)),
                         color=(255, 214, 40), borde=5)


class CleoTurista(Escena):
    camara = (1.05, 1.15, 0.5, 0.55)

    def __init__(self):
        self.fondo = fondo_desierto(1)
        self.hero = Personaje(ropa="#f2efe6", piel="#f0d0b0", pelo="#6a5a4a", estilo="toga", barba=True,
                              semilla=90)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.hero.dibujar(img, 760, 1760, 1.15, t, expresion="sorpresa", mirar=(-1, -1), brazos="arriba")
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((850, 1170, 960, 1230), radius=20, fill=(240, 226, 190), outline=TINTA, width=5)
        return img

    def encima(self, img, t, dur):
        texto_sombra(img, (W / 2, 330), "Ya eran ruinas antiguas", int(60 * pop((t - 0.3) / 0.3)) if t > 0.3 else 1,
                     color=(255, 214, 40), borde=5)
        etiqueta(img, 760, 760, "heródoto (griego)", t, dur * 0.45)
        if t > dur * 0.45:
            flecha(img, 760, 940, 90, 120, t)
        pildora(img, "¡SUSCRÍBETE Y COMENTA!", t, 0.8, 3.5)


class CleoLuna(Escena):
    camara = (1.0, 1.12, 0.5, 0.6)

    def __init__(self):
        self.fondo = fondo_luna()
        self.astro = Personaje(ropa="#f0f0f0", piel="#f6dcc0", pelo="#5a3a20", sombrero="casco",
                               estilo="astronauta", semilla=100)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        sube = ease(t / 1.2)
        top = 1050 + (1 - sube) * 300
        d.line((330, 1700, 330, top), fill=(200, 200, 210), width=10)
        fw, fh = 260, 160
        d.rectangle((330, top, 330 + fw, top + fh), fill=(245, 245, 245), outline=TINTA, width=5)
        for i in range(7):
            if i % 2 == 0:
                y = top + i * fh / 7
                d.rectangle((330, y, 330 + fw, y + fh / 7), fill=(200, 40, 50))
        d.rectangle((330, top, 330 + fw * 0.42, top + fh * 4 / 7), fill=(40, 60, 150), outline=TINTA, width=3)
        self.astro.dibujar(img, 640, 1760, 1.15, t, expresion="risa", mirar=(-1, -0.3), brazos="arriba")
        return img

    def encima(self, img, t, dur):
        dato_grande(img, "1969", "llegada a la Luna", t, 0.3, y=330)
        etiqueta(img, 700, 860, "neil armstrong", t, dur * 0.45)


class CleoLinea(Escena):
    camara = (1.0, 1.0, 0.5, 0.5)
    A0, A1 = -2560, 1969

    def __init__(self):
        self.fondo = fondo_papel()
        self.cleo = cleopatra(5)

    def X(self, anio):
        return 110 + (anio - self.A0) / (self.A1 - self.A0) * 860

    def mundo(self, t, dur):
        img = self.fondo.copy()
        y = 1050
        p = ease(t / 0.8)

        def dib(d, k):
            d.line((90 * k, y * k, (90 + 900 * p) * k, y * k), fill=TINTA, width=int(12 * k))
            for anio, col in ((self.A0, (200, 150, 80)), (-30, ORO), (self.A1, (120, 120, 130))):
                x = self.X(anio)
                if x <= 90 + 900 * p:
                    d.ellipse(((x - 22) * k, (y - 22) * k, (x + 22) * k, (y + 22) * k), fill=col + (255,)
                              if len(col) == 3 else col, outline=TINTA, width=int(6 * k))
            for (a, b, col, txt, yy, t0) in ((self.A0, -30, (220, 40, 50), "2.500 años", y - 330, 1.2),
                                              (-30, self.A1, (40, 100, 220), "2.000 años", y + 190, 2.2)):
                q = ease((t - t0) / 0.6)
                if q <= 0:
                    continue
                xa, xb = self.X(a), self.X(a) + (self.X(b) - self.X(a)) * q
                d.line((xa * k, yy * k, xb * k, yy * k), fill=col + (255,), width=int(14 * k))
                for xx in (xa, xb):
                    d.line((xx * k, (yy - 30) * k, xx * k, (yy + 30) * k), fill=col + (255,), width=int(10 * k))
        img.alpha_composite(suave(dib, W, H))
        if t > 0.3:
            icono(img, "piramide", self.X(self.A0) + 20, y - 170, 0.7)
        if t > 0.6:
            self.cleo.dibujar(img, self.X(-30), y - 60, 0.42, t, expresion="risa" if t > 2.6 else "normal")
        if t > 0.8:
            icono(img, "luna", self.X(self.A1) - 20, y - 170, 0.55)
        return img

    def encima(self, img, t, dur):
        y = 1050
        for anio, txt in ((self.A0, "2560 a. C."), (-30, "30 a. C."), (self.A1, "1969")):
            if t > 0.5:
                x = min(max(self.X(anio), 120), 960)
                texto_sombra(img, (x, y + 70), txt, 34, sombra=False, borde=3)
        for txt, yy, t0, col in (("2.500 años", y - 400, 1.4, (235, 40, 50)), ("2.000 años", y + 270, 2.4,
                                                                               (40, 110, 230))):
            if t > t0:
                texto_sombra(img, (W / 2, yy), txt, int(80 * pop((t - t0) / 0.3)), color=col, borde=6)
        etiqueta(img, W / 2, 330, "la línea del tiempo", t, 0.2)


class CleoFinal(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        self.fondo = fondo_egipcio(2)
        self.cleo = cleopatra(7)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        self.cleo.dibujar(img, 540, 1760, 1.3, t, expresion="risa", brazos="cruzados", mirar=(0, 0))
        return img

    def encima(self, img, t, dur):
        encuesta(img, "¿Lo sabías?", "SÍ, LO\nSABÍA", "NI\nIDEA", t, 0.4)


ESCENAS.update({"cleo_intro": CleoIntro, "cleo_piramide": CleoPiramide, "cleo_mamut": CleoMamut,
                "cleo_nace": CleoNace, "cleo_turista": CleoTurista, "cleo_luna": CleoLuna,
                "cleo_linea": CleoLinea, "cleo_final": CleoFinal})


# =========================================================================== #
# MONTAJE
# =========================================================================== #
def camara(img, cam, p, t_local):
    z0, z1, fx, fy = cam
    z = z0 + (z1 - z0) * ease(p)
    z *= 1 + 0.06 * max(0.0, 1 - t_local / 0.22)  # pequeño "punch" al entrar
    cw, ch = W / z, H / z
    x0 = min(max(W * fx - cw / 2, 0), W - cw)
    y0 = min(max(H * fy - ch / 2, 0), H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def generar(ruta_json: Path, audio_usuario=None, sin_audio=False):
    cfg = json.loads(ruta_json.read_text(encoding="utf-8"))
    nombre = ruta_json.stem + "_caricatura"
    print(f"▶ {nombre}")
    tmp = Path(tempfile.mkdtemp(prefix="cari_"))
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
                                f"apad=whole_dur={dur + 0.3:.3f}", "-ar", str(SR), "-ac", "2", str(pad)], check=True)
                partes.append(pad)
                escenas.append(dict(s, inicio=t, dur=dur + 0.3, palabras=pal))
                t += dur + 0.3
            (tmp / "l.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in partes))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                            str(tmp / "l.txt"), str(tmp / "voz.wav")], check=True)
        # la última escena se alarga para dejar ver la encuesta
        escenas[-1]["dur"] += 2.0
        total = escenas[-1]["inicio"] + escenas[-1]["dur"]
        for e in escenas:
            e["grupos"] = agrupar_palabras(e["palabras"], max_palabras=2, max_chars=14)
            e["obj"] = ESCENAS[e["visual"]]()
        mezcla = disenar_sonido(leer_wav(tmp / "voz.wav"), [e["inicio"] for e in escenas[1:]], [], total)
        escribir_wav(tmp / "mezcla.wav", mezcla)

        (RAIZ / "salida").mkdir(exist_ok=True)
        salida = RAIZ / "salida" / f"{nombre}.mp4"
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", str(tmp / "mezcla.wav"), "-c:v", "libx264", "-preset", "medium",
             "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
             "-movflags", "+faststart", str(salida)], stdin=subprocess.PIPE)
        for n in range(int(total * FPS)):
            tg = n / FPS
            e = [x for x in escenas if tg >= x["inicio"]][-1]
            tl = tg - e["inicio"]
            img = e["obj"].mundo(tl, e["dur"])
            img = camara(img, e["obj"].camara, tl / e["dur"], tl if e is not escenas[0] else 1)
            e["obj"].encima(img, tl, e["dur"])
            subtitulo(img, e["grupos"], tl)
            proc.stdin.write(img.convert("RGB").tobytes())
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
