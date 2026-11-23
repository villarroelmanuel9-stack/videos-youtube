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
                 altura=1.0, bigote=False, semilla=0):
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
            E(-r, hc - r, r, hc + r, piel, 8)
            # pelo
            if self.sombrero not in ("piel", "copa"):
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
