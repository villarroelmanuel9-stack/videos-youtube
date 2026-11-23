"""
Escenas declarativas para las historias 4 a 10 (estilo caricatura).

Cada escena es un diccionario con:
  fondo   : nombre de fondo (ver FONDOS)
  cam     : (zoom_inicial, zoom_final, foco_x, foco_y)
  actores : lista de dicts {p: preset, x, y, s, expr, brazos, mirar, mov, baile, salto, en}
  props   : lista de (nombre, {parámetros}) dibujados en el "mundo" (se mueven con la cámara)
  textos  : lista de overlays fijos en pantalla
Los tiempos "en" son FRACCIONES de la duración de la escena (0 = inicio, 1 = final),
así funcionan con cualquier voz.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

from caricatura import (ESCENAS, ORO, TINTA, Escena, Personaje, _piramide, dato_grande, ease, encuesta,
                        etiqueta, flecha, fondo_artico, fondo_desierto, fondo_egipcio, fondo_luna, fondo_papel,
                        fondo_patio, fondo_salon, fondo_taller, fuente, icono, pildora, pop, suave, texto_sombra)
from generar_short import H, W

# =========================================================================== #
# PERSONAJES PREDEFINIDOS
# =========================================================================== #


def _p(**kw):
    color = kw.pop("color_sombrero", None)
    p = Personaje(**kw)
    p.color_sombrero = color
    return p


PRESETS = {
    "profesor": lambda: _p(ropa="#6a4a3a", pelo="#9a9a9a", bigote=True, semilla=1),
    "estudiante": lambda: _p(ropa="#3a6ab0", pelo="#4a2c1a", semilla=2),
    "estudiante2": lambda: _p(ropa="#b03a5a", pelo="#d0a040", semilla=3),
    "astronauta": lambda: _p(ropa="#f0f0f0", pelo="#2a1a10", sombrero="casco", estilo="astronauta", semilla=4),
    "astro_chino": lambda: _p(ropa="#f0f0f0", pelo="#141018", piel="#f0d4b0", sombrero="casco",
                              estilo="astronauta", semilla=5),
    "soldado_aus": lambda: _p(ropa="#8a7a4a", pelo="#6a4a2a", sombrero="ala_ancha", estilo="militar", semilla=6),
    "soldado_aus2": lambda: _p(ropa="#8a7a4a", pelo="#2a1a10", sombrero="ala_ancha", estilo="militar", semilla=7),
    "meredith": lambda: _p(ropa="#7a6a3a", pelo="#4a3020", sombrero="ala_ancha", estilo="militar", bigote=True,
                           semilla=8),
    "granjero": lambda: _p(ropa="#4a7ab0", pelo="#a06030", sombrero="ala_ancha", color_sombrero=(200, 170, 90),
                           semilla=9),
    "mujer_medieval": lambda: _p(ropa="#8a3a3a", pelo="#6a3a1a", sombrero="panuelo", estilo="vestido_simple",
                                 semilla=10),
    "aldeana": lambda: _p(ropa="#3a6a8a", pelo="#d0a040", sombrero="panuelo", color_sombrero=(220, 200, 160),
                          estilo="vestido_simple", semilla=11),
    "aldeano": lambda: _p(ropa="#6a7a3a", pelo="#4a2c1a", semilla=12),
    "aldeano2": lambda: _p(ropa="#7a5a3a", pelo="#1e1a18", bigote=True, semilla=13),
    "musico": lambda: _p(ropa="#3a6a3a", pelo="#4a2c1a", sombrero="boina", semilla=14),
    "autoridad": lambda: _p(ropa="#2a2a4a", pelo="#9a9a9a", sombrero="boina", color_sombrero=(30, 30, 40),
                            barba=True, semilla=15),
    "historiador": lambda: _p(ropa="#5a5a6a", pelo="#cfcfcf", peinado="normal", bigote=True, semilla=16),
    "oxford": lambda: _p(ropa="#1a1a1a", pelo="#7a4a2a", sombrero="birrete", semilla=17),
    "oxford2": lambda: _p(ropa="#1a1a1a", pelo="#d0a040", sombrero="birrete", semilla=18),
    "prof_oxford": lambda: _p(ropa="#3a1a1a", pelo="#cfcfcf", sombrero="birrete", barba=True, semilla=19),
    "mexica": lambda: _p(ropa="#e8dcc0", piel="#b07850", pelo="#141018", sombrero="penacho", semilla=20),
    "mexica2": lambda: _p(ropa="#d8c8a0", piel="#a86e48", pelo="#141018", semilla=21),
    "cortes": lambda: _p(ropa="#8a8a95", pelo="#3a2416", sombrero="morrion", estilo="armadura", barba=True,
                         semilla=22),
    "onoda": lambda: _p(ropa="#6a7a4a", piel="#e8c8a0", pelo="#141018", sombrero="gorra_militar", estilo="militar",
                        semilla=23),
    "aventurero": lambda: _p(ropa="#c07030", piel="#ecd0aa", pelo="#141018", sombrero="gorra",
                             color_sombrero=(200, 50, 50), semilla=24),
    "comandante": lambda: _p(ropa="#4a4a5a", piel="#ecd0aa", pelo="#cfcfcf", bigote=True, semilla=25),
    "peruggia": lambda: _p(ropa="#f0f0f0", pelo="#2a1a10", bigote=True, semilla=26),
    "picasso": lambda: _p(ropa="#f0f0f0", pelo="#2a1a10", estilo="rayas", peinado="calvo", semilla=27),
    "policia": lambda: _p(ropa="#2a3a6a", pelo="#3a2416", sombrero="kepi", bigote=True, semilla=28),
    "guardia": lambda: _p(ropa="#2a3a6a", pelo="#7a4a2a", sombrero="kepi", semilla=29),
    "comerciante": lambda: _p(ropa="#6a3a2a", pelo="#9a9a9a", bigote=True, semilla=30),
    "visitante": lambda: _p(ropa="#7a3a7a", pelo="#d0a040", semilla=31),
    "visitante2": lambda: _p(ropa="#2a7a6a", pelo="#4a2c1a", sombrero="boina", color_sombrero=(40, 40, 50),
                             semilla=32),
    "bostoniano": lambda: _p(ropa="#5a4a3a", pelo="#4a2c1a", sombrero="gorra", color_sombrero=(80, 70, 60),
                             semilla=33),
    "bostoniana": lambda: _p(ropa="#3a5a8a", pelo="#8a4a2a", sombrero="panuelo", color_sombrero=(230, 220, 200),
                             estilo="vestido_simple", semilla=34),
    "rescatista": lambda: _p(ropa="#3a3a3a", pelo="#4a2c1a", sombrero="kepi", color_sombrero=(30, 30, 30),
                             semilla=35),
    "ingeniero": lambda: _p(ropa="#3a4a6a", pelo="#6a4a2a", bigote=True, semilla=36),
    "pintor": lambda: _p(ropa="#e8e0d0", pelo="#6a4a2a", sombrero="gorra", color_sombrero=(120, 70, 40), semilla=37),
}


# =========================================================================== #
# FONDOS NUEVOS
# =========================================================================== #
def _cielo(d, k, h, arriba, abajo):
    for y in range(0, h, 8):
        f = y / h
        d.rectangle((0, y * k, W * k, (y + 8) * k),
                    fill=tuple(int(arriba[i] + (abajo[i] - arriba[i]) * f) for i in range(3)))


def _nubes(d, k, lista):
    for cx, cy, s in lista:
        for dx, dy, rr in ((-60, 10, 55), (0, -20, 70), (60, 10, 55), (0, 25, 60)):
            d.ellipse(((cx + dx * s - rr * s) * k, (cy + dy * s - rr * s) * k, (cx + dx * s + rr * s) * k,
                       (cy + dy * s + rr * s) * k), fill=(255, 255, 255), outline=(200, 215, 235), width=int(4 * k))


def _suelo(d, k, y0, col, borde=True, ondas=30):
    pts = [(0, H * k)] + [(x * k, (y0 + ondas * math.sin(x / 150)) * k) for x in range(0, W + 40, 40)] + \
          [(W * k, H * k)]
    d.polygon(pts, fill=col)
    if borde:
        d.line(pts[1:-1], fill=TINTA, width=int(7 * k))


def fondo_aula():
    def dib(d, k):
        piso = 1380
        d.rectangle((0, 0, W * k, piso * k), fill=(196, 220, 200))
        d.rectangle((0, 900 * k, W * k, piso * k), fill=(150, 110, 80))
        d.line((0, 900 * k, W * k, 900 * k), fill=TINTA, width=int(6 * k))
        d.rectangle((90 * k, 220 * k, 990 * k, 760 * k), fill=(40, 80, 60), outline=(120, 80, 40), width=int(22 * k))
        d.rectangle((90 * k, 220 * k, 990 * k, 760 * k), outline=TINTA, width=int(6 * k))
        d.ellipse((180 * k, 330 * k, 420 * k, 570 * k), outline=(240, 240, 230), width=int(7 * k))
        d.line((200 * k, 460 * k, 400 * k, 440 * k), fill=(240, 240, 230), width=int(5 * k))
        d.line((560 * k, 320 * k, 900 * k, 320 * k), fill=(240, 240, 230), width=int(5 * k))
        d.line((560 * k, 420 * k, 860 * k, 420 * k), fill=(240, 240, 230), width=int(5 * k))
        d.line((560 * k, 520 * k, 820 * k, 520 * k), fill=(240, 240, 230), width=int(5 * k))
        d.rectangle((0, piso * k, W * k, H * k), fill=(170, 120, 70))
        for i in range(-10, 11):
            d.line(((540 + i * 50) * k, piso * k, (540 + i * 200) * k, H * k), fill=(140, 96, 52), width=int(5 * k))
        d.line((0, piso * k, W * k, piso * k), fill=TINTA, width=int(8 * k))
    return suave(dib, W, H)


def _tierra(d, k, cx, cy, r, noche=False):
    d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k),
              fill=(20, 30, 70) if noche else (60, 120, 220), outline=TINTA, width=int(7 * k))
    rnd = random.Random(3)
    for _ in range(7):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0.15, 0.32) * r
        dist = rnd.uniform(0, 0.55) * r
        x, y = cx + dist * math.cos(a), cy + dist * math.sin(a)
        d.ellipse(((x - rr) * k, (y - rr * 0.7) * k, (x + rr) * k, (y + rr * 0.7) * k),
                  fill=(40, 60, 50) if noche else (70, 170, 90))


def fondo_espacio_orbita():
    def dib(d, k):
        d.rectangle((0, 0, W * k, H * k), fill=(8, 10, 26))
        r = random.Random(9)
        for _ in range(150):
            x, y, rr = r.randint(0, W), r.randint(0, H), r.choice((2, 3))
            d.ellipse(((x - rr) * k, (y - rr) * k, (x + rr) * k, (y + rr) * k), fill=(255, 255, 230))
        _tierra(d, k, 540, 2700, 1350)
    return suave(dib, W, H)


def fondo_nave():
    def dib(d, k):
        d.rectangle((0, 0, W * k, H * k), fill=(190, 195, 205))
        for y in range(0, H, 160):
            d.line((0, y * k, W * k, y * k), fill=(160, 165, 178), width=int(6 * k))
        for x in (60, 1020):
            for y in range(100, H, 160):
                d.ellipse(((x - 10) * k, (y - 10) * k, (x + 10) * k, (y + 10) * k), fill=(140, 145, 158))
        cx, cy, r = 540, 600, 330
        d.ellipse(((cx - r - 40) * k, (cy - r - 40) * k, (cx + r + 40) * k, (cy + r + 40) * k), fill=(120, 125, 140),
                  outline=TINTA, width=int(8 * k))
        d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), fill=(8, 10, 26), outline=TINTA,
                  width=int(8 * k))
        _tierra(d, k, cx + 60, cy + 320, 360)
        d.arc(((cx - r + 30) * k, (cy - r + 30) * k, (cx + r - 30) * k, (cy + r - 30) * k), 200, 250,
              fill=(255, 255, 255, 140), width=int(16 * k))
        d.rectangle((0, 1450 * k, W * k, H * k), fill=(150, 155, 168))
        d.line((0, 1450 * k, W * k, 1450 * k), fill=TINTA, width=int(7 * k))
    return suave(dib, W, H)


def fondo_tierra_noche():
    def dib(d, k):
        d.rectangle((0, 0, W * k, H * k), fill=(4, 6, 16))
        r = random.Random(4)
        for _ in range(120):
            x, y = r.randint(0, W), r.randint(0, 700)
            d.ellipse(((x - 2) * k, (y - 2) * k, (x + 2) * k, (y + 2) * k), fill=(220, 220, 255))
        _tierra(d, k, 540, 1900, 1150, noche=True)
    return suave(dib, W, H)


def fondo_muralla():
    def dib(d, k):
        _cielo(d, k, 1300, (110, 170, 230), (210, 230, 240))
        _nubes(d, k, [(220, 250, 0.9), (820, 200, 1.1)])
        for x0, h, col in ((-200, 520, (120, 150, 120)), (300, 600, (110, 140, 110)), (700, 480, (120, 150, 120))):
            d.polygon([(x0 * k, 1300 * k), ((x0 + 330) * k, (1300 - h) * k), ((x0 + 660) * k, 1300 * k)],
                      fill=col, outline=TINTA)
        _suelo(d, k, 1150, (110, 160, 90))
        # muralla serpenteante
        pts = []
        for i in range(0, 41):
            f = i / 40
            x = -50 + 1180 * f
            y = 1080 - 260 * math.sin(f * 5.5) * (1 - f * 0.4) + 380 * f
            pts.append((x, y))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            d.line((x0 * k, y0 * k, x1 * k, y1 * k), fill=TINTA, width=int(46 * k))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            d.line((x0 * k, y0 * k, x1 * k, y1 * k), fill=(200, 180, 140), width=int(32 * k))
        for i, (x, y) in enumerate(pts):
            if i % 2 == 0:
                d.rectangle(((x - 7) * k, (y - 30) * k, (x + 7) * k, (y - 14) * k), fill=(200, 180, 140),
                            outline=TINTA, width=int(3 * k))
            if i % 8 == 4:
                d.rectangle(((x - 34) * k, (y - 80) * k, (x + 34) * k, (y + 10) * k), fill=(190, 170, 130),
                            outline=TINTA, width=int(5 * k))
                d.polygon([((x - 44) * k, (y - 80) * k), (x * k, (y - 120) * k), ((x + 44) * k, (y - 80) * k)],
                          fill=(170, 60, 50), outline=TINTA)
    return suave(dib, W, H)


def fondo_campo(estanque=False):
    def dib(d, k):
        _cielo(d, k, 1150, (90, 160, 235), (200, 225, 245))
        _nubes(d, k, [(200, 260, 1.0), (800, 180, 1.2)])
        d.ellipse((780 * k, 330 * k, 940 * k, 490 * k), fill=(255, 230, 120), outline=(255, 200, 80), width=int(6 * k))
        _suelo(d, k, 1150, (226, 190, 90), ondas=15)
        r = random.Random(2)
        for _ in range(170):
            x, y = r.randint(0, W), r.randint(1170, H)
            h = 30 + (y - 1150) * 0.08
            d.line((x * k, y * k, x * k, (y - h) * k), fill=(180, 140, 50), width=int(4 * k))
            d.ellipse(((x - 6) * k, (y - h - 16) * k, (x + 6) * k, (y - h + 2) * k), fill=(240, 200, 90))
        if estanque:
            d.ellipse((140 * k, 1330 * k, 940 * k, 1560 * k), fill=(70, 140, 200), outline=TINTA, width=int(7 * k))
            d.ellipse((260 * k, 1380 * k, 560 * k, 1420 * k), fill=(140, 200, 240))
        # cerca
        for x in range(20, W, 120):
            d.rectangle((x * k, 1080 * k, (x + 12) * k, 1170 * k), fill=(140, 90, 50), outline=TINTA, width=int(3 * k))
        d.line((0, 1105 * k, W * k, 1105 * k), fill=(140, 90, 50), width=int(8 * k))
    return suave(dib, W, H)


def _casa_medieval(d, k, x, y_base, w, h, col, techo):
    d.rectangle((x * k, (y_base - h) * k, (x + w) * k, y_base * k), fill=col, outline=TINTA, width=int(6 * k))
    for i in range(1, 4):
        d.line((x * k, (y_base - h * i / 4) * k, (x + w) * k, (y_base - h * i / 4) * k), fill=(90, 60, 40),
               width=int(8 * k))
    d.line((x * k, (y_base - h) * k, (x + w) * k, y_base * k), fill=(90, 60, 40), width=int(7 * k))
    d.polygon([((x - 20) * k, (y_base - h) * k), ((x + w / 2) * k, (y_base - h - w * 0.7) * k),
               ((x + w + 20) * k, (y_base - h) * k)], fill=techo, outline=TINTA)
    d.line(((x - 20) * k, (y_base - h) * k, (x + w / 2) * k, (y_base - h - w * 0.7) * k, (x + w + 20) * k,
            (y_base - h) * k), fill=TINTA, width=int(6 * k))
    for wx in (x + w * 0.2, x + w * 0.6):
        d.rectangle((wx * k, (y_base - h * 0.62) * k, (wx + w * 0.2) * k, (y_base - h * 0.45) * k),
                    fill=(255, 220, 140), outline=TINTA, width=int(4 * k))


def fondo_calle_medieval(oscuro=False):
    def dib(d, k):
        _cielo(d, k, 1250, (100, 160, 230) if not oscuro else (60, 50, 90), (200, 225, 245) if not oscuro
               else (200, 120, 90))
        cols = [(240, 225, 190), (230, 210, 170), (245, 235, 205)]
        techos = [(190, 80, 50), (160, 60, 50), (120, 70, 60)]
        x = -40
        i = 0
        while x < W:
            w = 230 + (i % 3) * 30
            _casa_medieval(d, k, x, 1280, w, 520 + (i % 2) * 120, cols[i % 3], techos[i % 3])
            x += w + 10
            i += 1
        d.rectangle((0, 1280 * k, W * k, H * k), fill=(150, 140, 160))
        r = random.Random(3)
        for y in range(1280, H, 46):
            for x in range(-40 + (y // 46 % 2) * 40, W, 84):
                c = r.randint(-15, 15)
                d.rounded_rectangle(((x + 4) * k, (y + 4) * k, (x + 80) * k, (y + 42) * k), radius=int(16 * k),
                                    fill=(160 + c, 150 + c, 172 + c), outline=(100, 92, 115), width=int(4 * k))
        d.line((0, 1280 * k, W * k, 1280 * k), fill=TINTA, width=int(8 * k))
    return suave(dib, W, H)


def fondo_santuario():
    def dib(d, k):
        _cielo(d, k, 1300, (120, 170, 230), (220, 235, 245))
        for x0, h, col in ((-150, 700, (100, 130, 110)), (350, 820, (90, 120, 100)), (720, 640, (100, 130, 110))):
            d.polygon([(x0 * k, 1300 * k), ((x0 + 380) * k, (1300 - h) * k), ((x0 + 760) * k, 1300 * k)],
                      fill=col, outline=TINTA)
            d.polygon([((x0 + 300) * k, (1300 - h * 0.8) * k), ((x0 + 380) * k, (1300 - h) * k),
                       ((x0 + 460) * k, (1300 - h * 0.8) * k)], fill=(245, 245, 250))
        _suelo(d, k, 1250, (110, 160, 90))
        # capilla
        cx = 760
        d.rectangle(((cx - 140) * k, 900 * k, (cx + 140) * k, 1250 * k), fill=(235, 225, 200), outline=TINTA,
                    width=int(7 * k))
        d.polygon([((cx - 170) * k, 900 * k), (cx * k, 760 * k), ((cx + 170) * k, 900 * k)], fill=(170, 70, 50),
                  outline=TINTA)
        d.rectangle(((cx - 30) * k, 640 * k, (cx + 30) * k, 800 * k), fill=(235, 225, 200), outline=TINTA,
                    width=int(5 * k))
        d.line((cx * k, 560 * k, cx * k, 650 * k), fill=TINTA, width=int(8 * k))
        d.line(((cx - 30) * k, 590 * k, (cx + 30) * k, 590 * k), fill=TINTA, width=int(8 * k))
        d.rounded_rectangle(((cx - 50) * k, 1100 * k, (cx + 50) * k, 1250 * k), radius=int(40 * k),
                            fill=(110, 70, 40), outline=TINTA, width=int(5 * k))
        d.line((0, 1500 * k, 400 * k, 1300 * k, (cx - 60) * k, 1250 * k), fill=(200, 180, 140), width=int(60 * k))
    return suave(dib, W, H)


def fondo_oxford():
    def dib(d, k):
        _cielo(d, k, 1200, (120, 170, 220), (215, 230, 240))
        _nubes(d, k, [(200, 200, 0.9), (870, 260, 1.0)])
        base = 1250
        d.rectangle((40 * k, 560 * k, 1040 * k, base * k), fill=(220, 200, 150), outline=TINTA, width=int(8 * k))
        for x in (40, 960):
            d.rectangle((x * k, 380 * k, (x + 80) * k, base * k), fill=(210, 190, 140), outline=TINTA,
                        width=int(6 * k))
            d.polygon([(x * k, 380 * k), ((x + 40) * k, 250 * k), ((x + 80) * k, 380 * k)], fill=(150, 140, 120),
                      outline=TINTA)
        d.rectangle((460 * k, 300 * k, 620 * k, 560 * k), fill=(210, 190, 140), outline=TINTA, width=int(6 * k))
        d.polygon([(450 * k, 300 * k), (540 * k, 120 * k), (630 * k, 300 * k)], fill=(150, 140, 120), outline=TINTA)
        d.ellipse((500 * k, 360 * k, 580 * k, 440 * k), fill=(250, 245, 230), outline=TINTA, width=int(5 * k))
        for row in range(2):
            for col in range(7):
                x = 140 + col * 120
                y = 640 + row * 280
                d.rectangle((x * k, (y + 40) * k, (x + 60) * k, (y + 190) * k), fill=(80, 110, 160), outline=TINTA,
                            width=int(5 * k))
                d.pieslice((x * k, y * k, (x + 60) * k, (y + 80) * k), 180, 360, fill=(80, 110, 160), outline=TINTA,
                           width=int(5 * k))
        d.rounded_rectangle((470 * k, 1050 * k, 610 * k, base * k), radius=int(60 * k), fill=(110, 70, 40),
                            outline=TINTA, width=int(6 * k))
        _suelo(d, k, base, (100, 170, 80), ondas=8)
        for x in range(0, W, 26):
            d.line((x * k, (base + 20) * k, (x + 8) * k, (base + 2) * k), fill=(80, 140, 60), width=int(3 * k))
    return suave(dib, W, H)


def fondo_lago(ciudad=False):
    def dib(d, k):
        _cielo(d, k, 1050, (100, 170, 230), (220, 235, 240))
        for x0, h in ((-100, 420), (300, 520), (720, 380)):
            d.polygon([(x0 * k, 1050 * k), ((x0 + 300) * k, (1050 - h) * k), ((x0 + 600) * k, 1050 * k)],
                      fill=(110, 140, 120), outline=TINTA)
        d.polygon([(440 * k, 1050 * k), (600 * k, 700 * k), (760 * k, 1050 * k)], fill=(130, 150, 130),
                  outline=TINTA)
        d.polygon([(560 * k, 790 * k), (600 * k, 700 * k), (640 * k, 790 * k)], fill=(245, 245, 250))
        d.rectangle((0, 1050 * k, W * k, H * k), fill=(70, 140, 190))
        for i in range(12):
            y = 1100 + i * 70
            d.line(((100 + i * 61 % 700) * k, y * k, (200 + i * 61 % 700) * k, y * k), fill=(140, 200, 235),
                   width=int(5 * k))
        cx, cy = 540, 1380
        d.ellipse(((cx - 330) * k, (cy - 90) * k, (cx + 330) * k, (cy + 90) * k), fill=(200, 180, 110),
                  outline=TINTA, width=int(7 * k))
        if ciudad:
            for dx in (-230, -130, 130, 230):
                d.rectangle(((cx + dx - 45) * k, (cy - 130) * k, (cx + dx + 45) * k, (cy - 30) * k),
                            fill=(235, 225, 200), outline=TINTA, width=int(5 * k))
            for i in range(4):
                w = 260 - i * 50
                d.rectangle(((cx - w / 2) * k, (cy - 60 - i * 70 - 70) * k, (cx + w / 2) * k, (cy - 60 - i * 70) * k),
                            fill=(225, 215, 190), outline=TINTA, width=int(5 * k))
            for dx, col in ((-35, (40, 90, 170)), (35, (200, 50, 50))):
                d.rectangle(((cx + dx - 28) * k, (cy - 400) * k, (cx + dx + 28) * k, (cy - 340) * k), fill=col,
                            outline=TINTA, width=int(4 * k))
    return suave(dib, W, H)


def fondo_selva(noche=False):
    def dib(d, k):
        if noche:
            d.rectangle((0, 0, W * k, H * k), fill=(14, 30, 30))
        else:
            d.rectangle((0, 0, W * k, H * k), fill=(140, 200, 150))
        r = random.Random(5)
        capas = [(40, 90, 50), (30, 120, 60), (50, 150, 70)] if not noche else [(10, 40, 30), (15, 55, 40),
                                                                                  (20, 70, 45)]
        for li, col in enumerate(capas):
            for _ in range(14):
                x, y = r.randint(-100, W + 100), r.randint(200 + li * 300, 900 + li * 350)
                rr = r.randint(110, 220)
                d.ellipse(((x - rr) * k, (y - rr * 0.7) * k, (x + rr) * k, (y + rr * 0.7) * k), fill=col,
                          outline=TINTA, width=int(4 * k))
        for x in (80, 960):
            d.rectangle(((x - 30) * k, 0, (x + 30) * k, 1500 * k), fill=(90, 60, 40) if not noche else (40, 30, 25),
                        outline=TINTA, width=int(6 * k))
        _suelo(d, k, 1500, (90, 120, 60) if not noche else (30, 45, 30), ondas=10)
        for _ in range(25):
            x, y = r.randint(0, W), r.randint(1520, H)
            for a in (-0.6, 0, 0.6):
                d.line((x * k, y * k, (x + 70 * math.sin(a)) * k, (y - 90) * k),
                       fill=(60, 140, 60) if not noche else (25, 70, 40), width=int(10 * k))
    return suave(dib, W, H)


def fondo_playa():
    def dib(d, k):
        _cielo(d, k, 1000, (80, 170, 235), (200, 235, 250))
        _nubes(d, k, [(250, 250, 1.0), (830, 330, 0.8)])
        d.rectangle((0, 1000 * k, W * k, 1350 * k), fill=(40, 140, 200))
        d.polygon([(250 * k, 1010 * k), (540 * k, 820 * k), (850 * k, 1010 * k)], fill=(60, 140, 70),
                  outline=TINTA)
        _suelo(d, k, 1350, (240, 220, 160), ondas=12)
        for px in (140, 920):
            d.line((px * k, 1500 * k, (px + 40) * k, 1050 * k), fill=(120, 80, 40), width=int(22 * k))
            for a in range(0, 360, 45):
                ex, ey = px + 40 + 150 * math.cos(math.radians(a)), 1050 + 60 * math.sin(math.radians(a)) + 20
                d.line(((px + 40) * k, 1050 * k, ex * k, ey * k), fill=(50, 140, 60), width=int(18 * k))
    return suave(dib, W, H)


def fondo_museo(oscuro=False):
    def dib(d, k):
        piso = 1350
        d.rectangle((0, 0, W * k, piso * k), fill=(150, 40, 45) if not oscuro else (60, 20, 30))
        for x in range(0, W, 180):
            d.line((x * k, 0, x * k, piso * k), fill=(130, 30, 40) if not oscuro else (50, 15, 25), width=int(6 * k))
        d.rectangle((0, 120 * k, W * k, 150 * k), fill=ORO + (255,), outline=TINTA, width=int(4 * k))
        d.rectangle((0, 1250 * k, W * k, piso * k), fill=(110, 70, 40), outline=TINTA, width=int(5 * k))
        d.rectangle((0, piso * k, W * k, H * k), fill=(180, 140, 90) if not oscuro else (80, 60, 45))
        for i in range(0, 12):
            for j in range(0, 8):
                if (i + j) % 2:
                    d.rectangle((i * 100 * k, (piso + j * 75) * k, (i * 100 + 100) * k, (piso + j * 75 + 75) * k),
                                fill=(160, 120, 75) if not oscuro else (70, 50, 38))
        d.line((0, piso * k, W * k, piso * k), fill=TINTA, width=int(8 * k))
    return suave(dib, W, H)


def fondo_boston(frio=False):
    def dib(d, k):
        _cielo(d, k, 1200, (150, 180, 210) if frio else (110, 170, 230), (220, 230, 240))
        cols = [(170, 70, 50), (150, 60, 45), (185, 85, 60)]
        x = -30
        i = 0
        while x < W:
            w, h = 220 + (i % 3) * 40, 520 + (i % 2) * 160
            d.rectangle((x * k, (1250 - h) * k, (x + w) * k, 1250 * k), fill=cols[i % 3], outline=TINTA,
                        width=int(6 * k))
            for yy in range(1250 - h + 40, 1180, 120):
                for xx in range(x + 30, x + w - 50, 80):
                    d.rectangle((xx * k, yy * k, (xx + 45) * k, (yy + 70) * k), fill=(230, 220, 170), outline=TINTA,
                                width=int(4 * k))
            x += w + 10
            i += 1
        d.rectangle((0, 1250 * k, W * k, H * k), fill=(110, 110, 120))
        d.line((0, 1250 * k, W * k, 1250 * k), fill=TINTA, width=int(8 * k))
        for y in (1420, 1440):
            d.line((0, y * k, W * k, y * k), fill=(70, 60, 60), width=int(8 * k))
        for x in range(0, W, 60):
            d.rectangle((x * k, 1410 * k, (x + 30) * k, 1450 * k), fill=(90, 70, 50))
        if frio:
            for x in range(0, W, 30):
                d.ellipse(((x - 30) * k, 1240 * k, (x + 30) * k, 1270 * k), fill=(245, 248, 255))
    return suave(dib, W, H)


def fondo_oficina():
    def dib(d, k):
        d.rectangle((0, 0, W * k, 1250 * k), fill=(200, 210, 220))
        d.rectangle((140 * k, 260 * k, 940 * k, 820 * k), fill=(40, 80, 160), outline=TINTA, width=int(8 * k))
        for i in range(1, 9):
            d.line(((140 + i * 89) * k, 260 * k, (140 + i * 89) * k, 820 * k), fill=(90, 130, 200), width=int(2 * k))
            d.line((140 * k, (260 + i * 62) * k, 940 * k, (260 + i * 62) * k), fill=(90, 130, 200), width=int(2 * k))
        d.ellipse((380 * k, 380 * k, 700 * k, 700 * k), outline=(240, 240, 255), width=int(7 * k))
        d.line((380 * k, 540 * k, 700 * k, 540 * k), fill=(240, 240, 255), width=int(4 * k))
        d.text((540 * k, 760 * k), "TANQUE · CÁLCULOS", font=fuente(34 * k), fill=(240, 240, 255), anchor="mm")
        d.rectangle((0, 1250 * k, W * k, H * k), fill=(120, 80, 50))
        d.rectangle((0, 1230 * k, W * k, 1290 * k), fill=(150, 100, 60), outline=TINTA, width=int(7 * k))
    return suave(dib, W, H)


_FONDOS_CACHE: dict = {}
FONDOS = {
    "aula": fondo_aula, "orbita": fondo_espacio_orbita, "nave": fondo_nave, "tierra_noche": fondo_tierra_noche,
    "muralla": fondo_muralla, "campo": fondo_campo, "estanque": lambda: fondo_campo(True),
    "calle": fondo_calle_medieval, "calle_tarde": lambda: fondo_calle_medieval(True), "santuario": fondo_santuario,
    "oxford": fondo_oxford, "lago": fondo_lago, "ciudad_mexica": lambda: fondo_lago(True), "selva": fondo_selva,
    "selva_noche": lambda: fondo_selva(True), "playa": fondo_playa, "museo": fondo_museo,
    "museo_noche": lambda: fondo_museo(True), "boston": fondo_boston, "boston_frio": lambda: fondo_boston(True),
    "oficina": fondo_oficina, "taller": fondo_taller, "salon": fondo_salon, "patio": fondo_patio,
    "desierto": fondo_desierto, "egipcio": fondo_egipcio, "artico": fondo_artico, "luna": fondo_luna,
    "papel": fondo_papel,
}


def obtener_fondo(nombre):
    if nombre not in _FONDOS_CACHE:
        _FONDOS_CACHE[nombre] = FONDOS[nombre]()
    return _FONDOS_CACHE[nombre].copy()


# =========================================================================== #
# PROPS (objetos animados del mundo)
# =========================================================================== #
def prop_emu(img, t, dur, x=540, y=1600, s=1.0, correr=0.0, casco=False, risa=False, mirar=1):
    paso = math.sin(t * (14 if correr else 3))
    x = x + correr * t

    def dib(d, k):
        ox, oy = 300, 760

        def P(px, py):
            return (ox + px) * k, (oy + py) * k

        def E(x0, y0, x1, y1, fill, ow=7):
            d.ellipse((*P(x0, y0), *P(x1, y1)), fill=fill, outline=TINTA, width=int(ow * k))
        for i, sx in enumerate((-30, 30)):
            off = paso * (40 if correr else 8) * (1 if i else -1)
            d.line((*P(sx, -260), *P(sx + off, -10)), fill=TINTA, width=int(22 * k))
            d.line((*P(sx, -260), *P(sx + off, -10)), fill=(150, 120, 90), width=int(12 * k))
            d.line((*P(sx + off - 25, -6), *P(sx + off + 30, -6)), fill=TINTA, width=int(12 * k))
        E(-170, -450, 150, -210, (110, 90, 75))
        for j in range(9):
            hx = -140 + j * 34
            d.arc((*P(hx - 20, -300), *P(hx + 20, -250)), 0, 180, fill=(80, 60, 50), width=int(5 * k))
        cuello = [P(90, -380), P(130, -480), P(150, -600), P(120, -620), P(95, -500), P(60, -400)]
        d.polygon(cuello, fill=(120, 130, 150))
        d.line(cuello + [cuello[0]], fill=TINTA, width=int(6 * k))
        E(90, -690, 210, -590, (120, 130, 150))
        d.polygon([P(200, -650), P(265, -632), P(200, -615)], fill=(230, 180, 90), outline=TINTA)
        E(140, -670, 178, -628, (255, 255, 255), 5)
        d.ellipse((*P(158, -658), *P(172, -644)), fill=TINTA)
        if risa:
            d.arc((*P(185, -640), *P(225, -610)), 0, 180, fill=TINTA, width=int(5 * k))
        if casco:
            E(95, -720, 215, -650, (110, 120, 70), 6)
            d.rectangle((*P(85, -668), *P(225, -656)), fill=(110, 120, 70), outline=TINTA, width=int(4 * k))
    em = suave(dib, 600, 800)
    if mirar < 0:
        em = em.transpose(Image.FLIP_LEFT_RIGHT)
    if s != 1:
        em = em.resize((int(600 * s), int(800 * s)), Image.BILINEAR)
    img.alpha_composite(em, (int(x - 300 * s), int(y - 760 * s - abs(paso) * 6 * s)))


def prop_ametralladora(img, t, dur, x=600, y=1640, s=1.0, humo=False, atascada=False):
    def dib(d, k):
        def P(px, py):
            return (x + px * s) * k, (y + py * s) * k
        for a, b in (((-60, 0), (0, -110)), ((60, 0), (0, -110)), ((0, 10), (0, -110))):
            d.line((*P(*a), *P(*b)), fill=TINTA, width=int(12 * k * s))
        d.rounded_rectangle((*P(-120, -160), *P(180, -110)), radius=int(14 * k), fill=(60, 60, 55), outline=TINTA,
                            width=int(6 * k))
        d.line((*P(180, -138), *P(300, -138)), fill=TINTA, width=int(20 * k * s))
        d.ellipse((*P(-40, -230), *P(60, -150)), fill=(70, 70, 65), outline=TINTA, width=int(6 * k))
        d.rectangle((*P(-200, -150), *P(-120, -118)), fill=(110, 70, 40), outline=TINTA, width=int(5 * k))
    img.alpha_composite(suave(dib, W, H))
    if humo or atascada:
        d = ImageDraw.Draw(img)
        for j in range(5):
            f = (t * 0.6 + j / 5) % 1
            rr = (25 + 50 * f) * s
            cx, cy = x + (300 + 30 * f) * s, y - (140 + 200 * f) * s
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(200, 200, 200, int(200 * (1 - f))),
                      outline=(60, 60, 60, int(200 * (1 - f))), width=4)


def prop_iss(img, t, dur, x=540, y=600, s=1.0):
    def dib(d, k):
        yy = y + 15 * math.sin(t)

        def P(px, py):
            return (x + px * s) * k, (yy + py * s) * k
        d.rectangle((*P(-300, -12), *P(300, 12)), fill=(200, 200, 210), outline=TINTA, width=int(5 * k))
        for sx in (-1, 1):
            for j in (-1, 1):
                d.rectangle((*P(sx * 300 - 120 * (sx < 0), j * 25 - 60 * (j < 0)),
                             *P(sx * 300 + 120 * (sx > 0), j * 25 + 60 * (j > 0))), fill=(40, 80, 170),
                            outline=TINTA, width=int(5 * k))
        d.rounded_rectangle((*P(-90, -45), *P(90, 45)), radius=int(20 * k), fill=(230, 230, 235), outline=TINTA,
                            width=int(6 * k))
    img.alpha_composite(suave(dib, W, H))


def prop_moneda(img, t, dur, x=540, y=900, s=1.0):
    d = ImageDraw.Draw(img)
    rr = 60 * s * (0.6 + 0.4 * abs(math.cos(t * 2)))
    d.ellipse((x - rr, y - 60 * s, x + rr, y + 60 * s), fill=ORO + (255,), outline=TINTA, width=6)


def prop_libro(img, t, dur, x=540, y=1050, s=1.0, tachado=True):
    def dib(d, k):
        def P(px, py):
            return (x + px * s) * k, (y + py * s) * k
        d.polygon([P(-260, -150), P(0, -120), P(0, 160), P(-260, 130)], fill=(250, 245, 230), outline=TINTA)
        d.polygon([P(260, -150), P(0, -120), P(0, 160), P(260, 130)], fill=(245, 240, 222), outline=TINTA)
        d.line((*P(-260, -150), *P(0, -120), *P(260, -150), *P(260, 130), *P(0, 160), *P(-260, 130),
                *P(-260, -150)), fill=TINTA, width=int(7 * k))
        d.line((*P(0, -120), *P(0, 160)), fill=TINTA, width=int(6 * k))
        for i in range(5):
            d.line((*P(-230, -90 + i * 45), *P(-30, -70 + i * 45)), fill=(150, 140, 120), width=int(5 * k))
            d.line((*P(30, -70 + i * 45), *P(230, -90 + i * 45)), fill=(150, 140, 120), width=int(5 * k))
        if tachado and t > dur * 0.3:
            q = ease((t - dur * 0.3) / 0.5)
            d.line((*P(-220, -110), *P(-220 + 440 * q, -110 + 240 * q)), fill=(220, 30, 40), width=int(22 * k))
            if q >= 1:
                d.line((*P(220, -110), *P(-220, 130)), fill=(220, 30, 40), width=int(22 * k))
    img.alpha_composite(suave(dib, W, H))


def prop_luces(img, t, dur, y0=900):
    d = ImageDraw.Draw(img)
    r = random.Random(11)
    for _ in range(140):
        a = r.uniform(-1.2, 1.2)
        dist = r.uniform(0.2, 0.98)
        x = 540 + 1150 * dist * math.sin(a)
        y = 1900 - 1150 * dist * math.cos(a)
        if y < y0 - 200:
            continue
        b = 0.6 + 0.4 * math.sin(t * 3 + x)
        rr = r.choice((3, 4, 6))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, int(210 * b), 90))


def prop_escenario(img, t, dur, x=540, y=1500):
    def dib(d, k):
        d.rectangle(((x - 330) * k, (y - 140) * k, (x + 330) * k, y * k), fill=(150, 100, 55), outline=TINTA,
                    width=int(7 * k))
        for i in range(1, 6):
            d.line(((x - 330 + i * 110) * k, (y - 140) * k, (x - 330 + i * 110) * k, y * k), fill=(110, 70, 40),
                   width=int(5 * k))
    img.alpha_composite(suave(dib, W, H))


def prop_notas(img, t, dur, x=540, y=900):
    d = ImageDraw.Draw(img)
    for i in range(6):
        f = (t * 0.5 + i / 6) % 1
        nx = x - 300 + i * 120 + 30 * math.sin(t * 2 + i)
        ny = y - 300 * f
        a = int(255 * (1 - f))
        d.ellipse((nx - 18, ny - 12, nx + 18, ny + 12), fill=(20, 20, 30, a))
        d.line((nx + 16, ny, nx + 16, ny - 70), fill=(20, 20, 30, a), width=7)
        d.line((nx + 16, ny - 70, nx + 40, ny - 50), fill=(20, 20, 30, a), width=7)


def prop_zapatos(img, t, dur, x=540, y=1600):
    d = ImageDraw.Draw(img)
    for dx in (-70, 70):
        d.rounded_rectangle((x + dx - 60, y - 30, x + dx + 60, y + 20), radius=22, fill=(210, 30, 40), outline=TINTA,
                            width=6)
        d.ellipse((x + dx - 50, y - 40, x + dx, y - 10), fill=(140, 20, 30), outline=TINTA, width=4)


def prop_nopal(img, t, dur, x=540, y=1300, s=1.0):
    def dib(d, k):
        def P(px, py):
            return (x + px * s) * k, (y + py * s) * k
        for (cx, cy, rw, rh) in ((0, -90, 55, 90), (-70, -200, 45, 70), (60, -210, 45, 75)):
            d.ellipse((*P(cx - rw, cy - rh), *P(cx + rw, cy + rh)), fill=(70, 150, 70), outline=TINTA,
                      width=int(6 * k))
        ay = -300 + 10 * math.sin(t * 3)
        d.ellipse((*P(-60, ay - 50), *P(60, ay + 50)), fill=(110, 70, 40), outline=TINTA, width=int(6 * k))
        for sx in (-1, 1):
            ang = 0.3 * math.sin(t * 6)
            d.polygon([P(sx * 40, ay - 20), P(sx * (170 + 0), ay - 80 - 60 * ang * sx), P(sx * 150, ay + 20)],
                      fill=(90, 55, 30), outline=TINTA)
        d.ellipse((*P(30, ay - 100), *P(100, ay - 30)), fill=(240, 240, 230), outline=TINTA, width=int(5 * k))
        d.polygon([P(95, ay - 70), P(130, ay - 60), P(95, ay - 50)], fill=(240, 190, 50), outline=TINTA)
        d.ellipse((*P(60, ay - 78), *P(76, ay - 62)), fill=TINTA)
        d.line((*P(60, ay - 30), *P(160, ay + 10 * math.sin(t * 5))), fill=(60, 140, 60), width=int(10 * k))
    img.alpha_composite(suave(dib, W, H))


def prop_linea(img, t, dur, puntos=(), y=1050):
    """puntos = [(año, etiqueta, color_hex)]"""
    a0, a1 = puntos[0][0], puntos[-1][0]
    p = ease(t / 0.8)

    def X(a):
        return 110 + (a - a0) / (a1 - a0) * 860

    def dib(d, k):
        d.line((90 * k, y * k, (90 + 900 * p) * k, y * k), fill=TINTA, width=int(12 * k))
        for i, (anio, txt, col) in enumerate(puntos):
            if t > 0.5 + i * 0.45:
                x = X(anio)
                c = tuple(int(col.lstrip("#")[j:j + 2], 16) for j in (0, 2, 4))
                d.ellipse(((x - 24) * k, (y - 24) * k, (x + 24) * k, (y + 24) * k), fill=c, outline=TINTA,
                          width=int(6 * k))
    img.alpha_composite(suave(dib, W, H))
    for i, (anio, txt, col) in enumerate(puntos):
        if t > 0.5 + i * 0.45:
            x = min(max(X(anio), 130), 950)
            arriba = i % 2 == 0
            texto_sombra(img, (x, y + (-150 if arriba else 150)), txt, 38, borde=4,
                         color=tuple(int(col.lstrip("#")[j:j + 2], 16) for j in (0, 2, 4)))
            texto_sombra(img, (x, y + (-95 if arriba else 95)), str(anio), 40, borde=4)


def prop_folletos(img, t, dur):
    d = ImageDraw.Draw(img)
    r = random.Random(6)
    for _ in range(14):
        x0, v, ph = r.uniform(0, W), r.uniform(120, 220), r.uniform(0, 6)
        y = (r.uniform(-400, 1200) + v * t) % 1700 - 100
        x = x0 + 60 * math.sin(t * 2 + ph)
        a = math.sin(t * 3 + ph) * 0.6
        w, h = 70, 50
        pts = [(x + w * math.cos(a) * sx - h * math.sin(a) * sy, y + w * math.sin(a) * sx + h * math.cos(a) * sy)
               for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(pts, fill=(250, 245, 225), outline=TINTA)
        d.line(pts + [pts[0]], fill=TINTA, width=4)


def prop_espada(img, t, dur, x=540, y=1300, ang=-20, s=1.0):
    def dib(d, k):
        a = math.radians(ang)
        x1, y1 = x + math.cos(a) * 420 * s, y + math.sin(a) * 420 * s
        d.line((x * k, y * k, x1 * k, y1 * k), fill=TINTA, width=int(26 * k))
        d.line((x * k, y * k, x1 * k, y1 * k), fill=(220, 225, 235), width=int(14 * k))
        hx, hy = x - math.cos(a) * 140 * s, y - math.sin(a) * 140 * s
        d.line((x * k, y * k, hx * k, hy * k), fill=TINTA, width=int(30 * k))
        d.line((x * k, y * k, hx * k, hy * k), fill=(60, 40, 90), width=int(18 * k))
        d.ellipse(((x - 30) * k, (y - 30) * k, (x + 30) * k, (y + 30) * k), fill=ORO + (255,), outline=TINTA,
                  width=int(5 * k))
    img.alpha_composite(suave(dib, W, H))


def prop_rifle(img, t, dur, x=540, y=1500, s=1.0):
    def dib(d, k):
        d.line(((x - 300 * s) * k, y * k, (x + 260 * s) * k, (y - 20 * s) * k), fill=TINTA, width=int(30 * k))
        d.line(((x - 300 * s) * k, y * k, (x + 100 * s) * k, (y - 10 * s) * k), fill=(140, 90, 50), width=int(18 * k))
        d.line(((x + 100 * s) * k, (y - 10 * s) * k, (x + 260 * s) * k, (y - 20 * s) * k), fill=(70, 70, 75),
               width=int(14 * k))
    img.alpha_composite(suave(dib, W, H))


def _mona(d, k, x0, y0, w, h):
    d.rectangle((x0 * k, y0 * k, (x0 + w) * k, (y0 + h) * k), fill=(90, 110, 80))
    d.rectangle((x0 * k, (y0 + h * 0.55) * k, (x0 + w) * k, (y0 + h) * k), fill=(60, 70, 50))
    cx = x0 + w / 2
    d.chord(((cx - w * 0.3) * k, (y0 + h * 0.5) * k, (cx + w * 0.3) * k, (y0 + h * 1.3) * k), 180, 360,
            fill=(40, 35, 30))
    d.ellipse(((cx - w * 0.2) * k, (y0 + h * 0.12) * k, (cx + w * 0.2) * k, (y0 + h * 0.6) * k), fill=(40, 30, 25))
    d.ellipse(((cx - w * 0.14) * k, (y0 + h * 0.18) * k, (cx + w * 0.14) * k, (y0 + h * 0.52) * k),
              fill=(230, 190, 140))
    d.arc(((cx - w * 0.06) * k, (y0 + h * 0.38) * k, (cx + w * 0.06) * k, (y0 + h * 0.46) * k), 20, 160,
          fill=(120, 60, 40), width=max(1, int(3 * k)))
    d.ellipse(((cx - w * 0.15) * k, (y0 + h * 0.82) * k, (cx + w * 0.15) * k, (y0 + h * 0.92) * k),
              fill=(230, 190, 140))


def prop_marco(img, t, dur, x=540, y=760, w=380, h=520, vacio=False, brillo=False):
    def dib(d, k):
        x0, y0 = x - w / 2, y - h / 2
        if vacio:
            for hx, hy in ((x0 + 40, y0 + 40), (x0 + w - 40, y0 + 40), (x0 + 40, y0 + h - 40),
                           (x0 + w - 40, y0 + h - 40)):
                d.ellipse(((hx - 9) * k, (hy - 9) * k, (hx + 9) * k, (hy + 9) * k), fill=(60, 60, 60))
            d.rectangle((x0 * k, y0 * k, (x0 + w) * k, (y0 + h) * k), outline=(120, 30, 35), width=int(6 * k))
            return
        d.rectangle(((x0 - 40) * k, (y0 - 40) * k, (x0 + w + 40) * k, (y0 + h + 40) * k), fill=ORO + (255,),
                    outline=TINTA, width=int(7 * k))
        _mona(d, k, x0, y0, w, h)
        d.rectangle((x0 * k, y0 * k, (x0 + w) * k, (y0 + h) * k), outline=TINTA, width=int(5 * k))
    img.alpha_composite(suave(dib, W, H))
    if brillo:
        d = ImageDraw.Draw(img)
        for i in range(8):
            a = t * 1.5 + i * math.pi / 4
            r1, r2 = max(w, h) * 0.62, max(w, h) * (0.72 + 0.05 * math.sin(t * 4 + i))
            d.line((x + r1 * math.cos(a), y + r1 * math.sin(a), x + r2 * math.cos(a), y + r2 * math.sin(a)),
                   fill=(255, 230, 90), width=10)


def prop_cuadro_robado(img, t, dur, x=540, y=1300, vx=0):
    """Esquina del cuadro asomando bajo la bata (se dibuja sobre el actor)."""
    x = x + vx * t
    def dib(d, k):
        d.polygon([(x * k, y * k), ((x + 110) * k, (y - 20) * k), ((x + 120) * k, (y + 90) * k)],
                  fill=ORO + (255,), outline=TINTA)
        d.line((x * k, y * k, (x + 110) * k, (y - 20) * k, (x + 120) * k, (y + 90) * k, x * k, y * k), fill=TINTA,
               width=int(5 * k))
    img.alpha_composite(suave(dib, W, H))


def prop_periodico(img, t, dur, x=540, y=820, titular="¡ROBAN LA MONA LISA!", ang=-4):
    p = pop(t / 0.4)
    if p <= 0.05:
        return
    w, h = 820, 620
    pap = Image.new("RGBA", (w, h), (245, 240, 225, 255))
    d = ImageDraw.Draw(pap)
    d.rectangle((0, 0, w - 1, h - 1), outline=TINTA, width=8)
    d.text((w / 2, 60), "PARÍS · 22 DE AGOSTO DE 1911", font=fuente(30), fill=(60, 50, 40), anchor="mm")
    d.line((30, 95, w - 30, 95), fill=TINTA, width=4)
    d.text((w / 2, 170), titular, font=fuente(64), fill=(180, 20, 30), anchor="mm")
    d.rectangle((40, 240, 360, 580), fill=(220, 210, 190), outline=TINTA, width=4)
    _mona(ImageDraw.Draw(pap), 1, 70, 260, 260, 300)
    for i in range(8):
        d.line((400, 260 + i * 40, w - 40, 260 + i * 40), fill=(170, 160, 140), width=6)
    pap = pap.rotate(ang, expand=True, resample=Image.BICUBIC)
    if p != 1:
        pap = pap.resize((max(1, int(pap.width * p)), max(1, int(pap.height * p))), Image.BILINEAR)
    img.alpha_composite(pap, (int(x - pap.width / 2), int(y - pap.height / 2)))


def prop_tanque(img, t, dur, x=760, y=1250, roto=False, gotas=False, pintura=0.0):
    def dib(d, k):
        w, h = 520, 760
        x0, y0 = x - w / 2, y - h
        col = (110, 70, 40) if pintura >= 1 else (150, 150, 155)
        d.rectangle((x0 * k, y0 * k, (x0 + w) * k, y * k), fill=col, outline=TINTA, width=int(8 * k))
        if 0 < pintura < 1:
            d.rectangle((x0 * k, y0 * k, (x0 + w * pintura) * k, y * k), fill=(110, 70, 40))
            d.rectangle((x0 * k, y0 * k, (x0 + w) * k, y * k), outline=TINTA, width=int(8 * k))
        d.chord((x0 * k, (y0 - 70) * k, (x0 + w) * k, (y0 + 70) * k), 180, 360, fill=col, outline=TINTA,
                width=int(8 * k))
        for j in range(1, 6):
            yy = y0 + j * h / 6
            d.line((x0 * k, yy * k, (x0 + w) * k, yy * k), fill=(90, 90, 95) if pintura < 1 else (80, 50, 30),
                   width=int(5 * k))
            for xx in range(int(x0) + 20, int(x0 + w), 40):
                d.ellipse(((xx - 4) * k, (yy - 4) * k, (xx + 4) * k, (yy + 4) * k), fill=TINTA)
        if roto:
            d.polygon([((x0 + 60) * k, (y - 520) * k), ((x0 + 160) * k, (y - 600) * k), ((x0 + 200) * k,
                       (y - 300) * k), ((x0 + 90) * k, (y - 160) * k), ((x0 + 30) * k, (y - 260) * k)],
                      fill=(50, 25, 10), outline=TINTA)
    img.alpha_composite(suave(dib, W, H))
    if gotas:
        d = ImageDraw.Draw(img)
        for i in range(7):
            gx = x - 220 + i * 70
            f = (t * 0.8 + i * 0.37) % 1
            gy = y - 600 + i * 60 + 500 * f
            d.ellipse((gx - 10, gy - 14, gx + 10, gy + 14), fill=(80, 40, 15), outline=TINTA, width=3)


def prop_ola(img, t, dur, avance=0.0, y_max=1250, desde=1100):
    """Ola de melaza que avanza de derecha a izquierda. avance: 0..1 (fracción de pantalla)."""
    f = min(1.0, avance)
    frente = W + 100 - (W + 400) * f
    d = ImageDraw.Draw(img)
    pts = [(W + 50, H)]
    for x in range(int(frente), W + 60, 30):
        alto = y_max - 380 * math.exp(-((x - frente) / 260) ** 2) + 30 * math.sin(x / 50 + t * 6)
        pts.append((x, min(H - 200, alto)))
    pts += [(W + 50, H), (frente, H)]
    if len(pts) > 4:
        d.polygon(pts, fill=(80, 40, 15))
        d.line(pts[1:-2], fill=TINTA, width=7)
        for x in range(int(frente) + 40, W, 120):
            y = y_max - 300 * math.exp(-((x - frente) / 260) ** 2) + 30 * math.sin(x / 50 + t * 6) + 40
            d.arc((x - 40, y - 20, x + 40, y + 20), 200, 340, fill=(170, 100, 50), width=8)


def prop_vagon(img, t, dur, x=300, y=1480, ang=0.0):
    v = Image.new("RGBA", (420, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(v)
    d.rectangle((20, 20, 400, 200), fill=(90, 50, 40), outline=TINTA, width=7)
    for i in range(4):
        d.rectangle((50 + i * 90, 50, 110 + i * 90, 110), fill=(230, 220, 170), outline=TINTA, width=4)
    for wx in (90, 330):
        d.ellipse((wx - 40, 180, wx + 40, 258), fill=(40, 40, 45), outline=TINTA, width=6)
    v = v.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(v, (int(x - v.width / 2), int(y - v.height / 2)))


def prop_nieve(img, t, dur):
    d = ImageDraw.Draw(img)
    r = random.Random(4)
    for _ in range(70):
        x0, y0, v = r.uniform(0, W), r.uniform(0, H), r.uniform(60, 140)
        x = (x0 + 20 * math.sin(t + x0)) % W
        y = (y0 + v * t) % H
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 255, 255))


def prop_icono(img, t, dur, tipo="piramide", x=540, y=600, s=0.8, en=0.0):
    if t < en * dur:
        return
    icono(img, tipo, x, y, s * pop((t - en * dur) / 0.3))


def prop_rotulo(img, t, dur, x=540, y=900, txt="", tam=44, color=(30, 20, 20)):
    ImageDraw.Draw(img).text((x, y), txt, font=fuente(tam), fill=color, anchor="mm")


def prop_planos(img, t, dur, x=540, y=1240):
    d = ImageDraw.Draw(img)
    d.polygon([(x - 300, y - 40), (x + 300, y - 70), (x + 330, y + 30), (x - 280, y + 50)], fill=(60, 100, 180),
              outline=TINTA)
    for i in range(4):
        d.line((x - 250, y - 20 + i * 18, x + 260, y - 45 + i * 18), fill=(200, 220, 255), width=3)


PROPS = {
    "emu": prop_emu, "ametralladora": prop_ametralladora, "iss": prop_iss, "moneda": prop_moneda,
    "libro": prop_libro, "luces": prop_luces, "escenario": prop_escenario, "notas": prop_notas,
    "zapatos": prop_zapatos, "nopal": prop_nopal, "linea": prop_linea, "folletos": prop_folletos,
    "espada": prop_espada, "rifle": prop_rifle, "marco": prop_marco, "cuadro_robado": prop_cuadro_robado,
    "periodico": prop_periodico, "tanque": prop_tanque, "ola": prop_ola, "vagon": prop_vagon, "nieve": prop_nieve,
    "icono": prop_icono, "rotulo": prop_rotulo, "planos": prop_planos,
}


# =========================================================================== #
# ESCENA GENÉRICA
# =========================================================================== #
def _segun_tiempo(valor, f):
    """valor puede ser fijo o lista [(fraccion, valor), ...]"""
    if isinstance(valor, list):
        actual = valor[0][1]
        for fr, v in valor:
            if f >= fr:
                actual = v
        return actual
    return valor


def sello(img, txt, t, t0, color=(220, 30, 40)):
    if t < t0:
        return
    p = pop((t - t0) / 0.25)
    base = 150
    while base > 60 and ImageDraw.Draw(img).textlength(txt, font=fuente(base)) > 760:
        base -= 6
    tam = int(base * (1.6 - 0.6 * p))
    f = fuente(tam)
    w = int(ImageDraw.Draw(img).textlength(txt, font=f)) + 80
    capa = Image.new("RGBA", (w, tam + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle((6, 6, w - 6, tam + 54), radius=24, outline=color + (255,), width=14)
    d.text((w / 2, (tam + 60) / 2), txt, font=f, fill=color + (255,), anchor="mm")
    capa = capa.rotate(-12, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(capa, (int(W / 2 - capa.width / 2), int(560 - capa.height / 2)))


def contador(img, a, b, t, t0, dur_anim=1.5, y=560, sufijo=""):
    if t < t0:
        return
    v = int(a + (b - a) * ease((t - t0) / dur_anim))
    texto_sombra(img, (W / 2, y), f"{v}{sufijo}", 150, color=(255, 214, 40), borde=7)


class EscenaDef(Escena):
    spec: dict = {}

    def __init__(self):
        sp = self.spec
        self.camara = sp.get("cam", (1.0, 1.1, 0.5, 0.6))
        self.fondo = obtener_fondo(sp["fondo"])
        self.actores = [(PRESETS[a["p"]](), a) for a in sp.get("actores", [])]

    def mundo(self, t, dur):
        img = self.fondo.copy()
        f = t / max(dur, 0.1)
        props_delante = []
        for nombre, kw in self.spec.get("props", []):
            kw = dict(kw)
            if kw.pop("delante", False):
                props_delante.append((nombre, kw))
                continue
            if f < kw.pop("en", 0.0):
                continue
            PROPS[nombre](img, t, dur, **kw)
        for p, a in self.actores:
            if f < a.get("en", 0.0):
                continue
            x, y = a.get("x", 540), a.get("y", 1700)
            vx, vy = a.get("mov", (0, 0))
            x, y = x + vx * t, y + vy * t
            brazos = _segun_tiempo(a.get("brazos", "abajo"), f)
            if a.get("baile"):
                x += 30 * math.sin(t * 6 + p.fase)
                y -= abs(math.sin(t * 6 + p.fase)) * 30
                brazos = "arriba" if math.sin(t * 6 + p.fase) > 0 else "abajo"
            if a.get("salto"):
                y -= abs(math.sin(t * 5 + p.fase)) * a["salto"]
            p.dibujar(img, x, y, a.get("s", 1.0), t, expresion=_segun_tiempo(a.get("expr", "normal"), f),
                      mirar=_segun_tiempo(a.get("mirar", (0, 0)), f), brazos=brazos)
        for nombre, kw in props_delante:
            if f < kw.pop("en", 0.0):
                continue
            PROPS[nombre](img, t, dur, **kw)
        return img

    def encima(self, img, t, dur):
        for ov in self.spec.get("textos", []):
            tipo = ov[0]
            if tipo == "dato":
                _, grande, chico, en = ov
                dato_grande(img, grande, chico, t, en * dur, y=330)
            elif tipo == "etiqueta":
                _, x, y, txt, en = ov
                etiqueta(img, x, y, txt, t, en * dur)
            elif tipo == "flecha":
                _, x, y, ang, largo, en = ov
                if t > en * dur:
                    flecha(img, x, y, ang, largo, t)
            elif tipo == "texto":
                _, y, txt, tam, color, en = ov
                if t > en * dur:
                    texto_sombra(img, (W / 2, y), txt, int(tam * pop((t - en * dur) / 0.25)), color=color, borde=5)
            elif tipo == "pildora":
                _, en = ov
                pildora(img, "¡SUSCRÍBETE Y COMENTA!", t, en * dur, 3.5)
            elif tipo == "encuesta":
                _, pregunta, o1, o2, en = ov
                encuesta(img, pregunta, o1, o2, t, en * dur)
            elif tipo == "sello":
                _, txt, en = ov
                sello(img, txt, t, en * dur)
            elif tipo == "contador":
                _, a, b, en, sufijo = ov
                contador(img, a, b, t, en * dur, sufijo=sufijo)


AMARILLO, ROJO, BLANCO, AZUL = (255, 214, 40), (235, 40, 50), (255, 255, 255), (60, 140, 255)


def registrar(prefijo, lista):
    for i, sp in enumerate(lista, 1):
        ESCENAS[f"{prefijo}_{i}"] = type(f"{prefijo}_{i}", (EscenaDef,), {"spec": sp})


# =========================================================================== #
# HISTORIA 4: LA GRAN MURALLA
# =========================================================================== #
registrar("h4", [
    dict(fondo="aula", cam=(1.0, 1.1, 0.5, 0.6),
         actores=[dict(p="profesor", x=300, y=1720, s=1.15, expr="risa", brazos="arriba", mirar=(1, -1)),
                  dict(p="estudiante", x=780, y=1760, s=1.0, expr=[(0, "sorpresa"), (0.6, "serio")], mirar=(-1, 0))],
         textos=[("sello", "¡MITO!", 0.55)]),
    dict(fondo="muralla", cam=(1.1, 1.0, 0.5, 0.55), textos=[("dato", "+20.000 km", "sumando todos sus tramos", 0.2)]),
    dict(fondo="muralla", cam=(1.0, 1.45, 0.62, 0.62),
         actores=[dict(p="estudiante", x=700, y=1215, s=0.16), dict(p="estudiante2", x=740, y=1222, s=0.16)],
         textos=[("dato", "6 metros", "de ancho en muchos tramos", 0.25),
                 ("etiqueta", 720, 980, "se confunde con el paisaje", 0.6)]),
    dict(fondo="orbita", cam=(1.0, 1.08, 0.5, 0.5), props=[("iss", dict(x=540, y=720, s=1.0)),
                                                         ("moneda", dict(x=540, y=1150, s=0.8, en=0.55))],
         textos=[("dato", "400 km", "de altura", 0.15), ("texto", 1300, "= una moneda a 1,5 km", 56, AMARILLO, 0.55)]),
    dict(fondo="nave", cam=(1.0, 1.12, 0.5, 0.5),
         actores=[dict(p="astro_chino", x=540, y=1780, s=1.2, expr=[(0, "serio"), (0.5, "sorpresa")],
                       mirar=(0, -1))],
         textos=[("etiqueta", 540, 230, "yang liwei · 2003", 0.2), ("texto", 1100, "«No la vi»", 80, BLANCO, 0.55)]),
    dict(fondo="aula", cam=(1.0, 1.1, 0.5, 0.55), props=[("libro", dict(x=540, y=1080, s=1.0, tachado=True))],
         actores=[dict(p="profesor", x=860, y=1760, s=1.0, expr="triste", mirar=(-1, -0.5))],
         textos=[("etiqueta", 540, 860, "libros escolares corregidos", 0.2)]),
    dict(fondo="tierra_noche", cam=(1.0, 1.15, 0.5, 0.7), props=[("luces", dict())],
         textos=[("texto", 420, "Lo que SÍ se ve:", 64, BLANCO, 0.1),
                 ("texto", 530, "luces de ciudades", 64, AMARILLO, 0.3)]),
    dict(fondo="aula", cam=(1.0, 1.06, 0.5, 0.6),
         actores=[dict(p="estudiante", x=360, y=1760, s=1.0, expr="risa"),
                  dict(p="estudiante2", x=720, y=1760, s=1.0, expr="sorpresa")],
         textos=[("encuesta", "¿Te lo enseñaron en el colegio?", "SÍ, ME LO\nENSEÑARON", "NO,\nNUNCA", 0.15)]),
])

# =========================================================================== #
# HISTORIA 5: LA GUERRA DE LOS EMÚS
# =========================================================================== #
registrar("h5", [
    dict(fondo="campo", cam=(1.0, 1.1, 0.5, 0.6),
         props=[("emu", dict(x=700, y=1720, s=1.15, risa=True, mirar=-1))],
         actores=[dict(p="soldado_aus", x=260, y=1740, s=1.0, expr=[(0, "serio"), (0.6, "triste")], mirar=(1, 0))],
         textos=[("dato", "1932", "Australia vs. aves", 0.15)]),
    dict(fondo="campo", cam=(1.05, 1.0, 0.5, 0.6),
         props=[("emu", dict(x=200, y=1500, s=0.6)), ("emu", dict(x=480, y=1560, s=0.7, mirar=-1)),
                ("emu", dict(x=780, y=1520, s=0.65)), ("emu", dict(x=330, y=1800, s=0.8, mirar=-1))],
         actores=[dict(p="granjero", x=880, y=1820, s=1.0, expr="enojado", brazos="arriba", mirar=(-1, 0))],
         textos=[("dato", "20.000 emús", "contra los cultivos", 0.15)]),
    dict(fondo="campo", cam=(1.0, 1.1, 0.5, 0.62),
         props=[("ametralladora", dict(x=720, y=1760, s=1.0))],
         actores=[dict(p="meredith", x=300, y=1760, s=1.15, expr="serio", mirar=(1, 0)),
                  dict(p="soldado_aus2", x=560, y=1640, s=0.8, expr="serio")],
         textos=[("etiqueta", 300, 820, "mayor meredith", 0.15), ("flecha", 300, 1000, 90, 120, 0.15),
                 ("dato", "10.000 balas", "y 2 ametralladoras", 0.5)]),
    dict(fondo="campo", cam=(1.0, 1.0, 0.5, 0.6),
         props=[("emu", dict(x=-150, y=1600, s=0.8, correr=240)), ("emu", dict(x=-450, y=1780, s=0.9, correr=290)),
                ("emu", dict(x=-300, y=1500, s=0.7, correr=260))],
         textos=[("dato", "50 km/h", "y en grupos pequeños", 0.15)]),
    dict(fondo="estanque", cam=(1.0, 1.12, 0.6, 0.65),
         props=[("ametralladora", dict(x=640, y=1780, s=1.0, atascada=True)),
                ("emu", dict(x=250, y=1330, s=0.55, risa=True)), ("emu", dict(x=430, y=1300, s=0.5, risa=True,
                                                                                  mirar=-1))],
         actores=[dict(p="soldado_aus", x=380, y=1820, s=1.0, expr=[(0, "serio"), (0.45, "sorpresa")],
                       mirar=(1, 0))],
         textos=[("texto", 520, "¡SE TRABÓ!", 110, ROJO, 0.45)]),
    dict(fondo="campo", cam=(1.0, 1.08, 0.5, 0.6),
         props=[("emu", dict(x=760, y=1650, s=0.9, risa=True, mirar=-1))],
         actores=[dict(p="soldado_aus", x=260, y=1760, s=1.0, expr="triste"),
                  dict(p="soldado_aus2", x=460, y=1780, s=1.0, expr="triste")],
         textos=[("dato", "≈10 balas", "por cada emú abatido", 0.15), ("texto", 600, "Operación cancelada", 60,
                                                                        AMARILLO, 0.6)]),
    dict(fondo="campo", cam=(1.0, 1.1, 0.5, 0.6),
         props=[("emu", dict(x=740, y=1700, s=1.1, casco=True, mirar=-1))],
         actores=[dict(p="meredith", x=280, y=1760, s=1.1, expr="sorpresa", mirar=(1, 0))],
         textos=[("texto", 380, "«Podría enfrentar", 62, BLANCO, 0.2),
                 ("texto", 470, "a cualquier ejército»", 62, AMARILLO, 0.2)]),
    dict(fondo="campo", cam=(1.0, 1.06, 0.5, 0.6),
         props=[("emu", dict(x=730, y=1720, s=1.0, risa=True, mirar=-1))],
         actores=[dict(p="soldado_aus", x=300, y=1760, s=1.0, expr="triste")],
         textos=[("encuesta", "¿Quién ganó?", "LOS\nEMÚS", "EL\nEJÉRCITO", 0.15)]),
])

# =========================================================================== #
# HISTORIA 6: LA EPIDEMIA DEL BAILE
# =========================================================================== #
registrar("h6", [
    dict(fondo="calle", cam=(1.0, 1.12, 0.5, 0.62),
         actores=[dict(p="mujer_medieval", x=540, y=1720, s=1.25, expr="sorpresa", baile=True),
                  dict(p="aldeano", x=150, y=1600, s=0.8, expr="sorpresa", mirar=(1, 0), en=0.4),
                  dict(p="aldeana", x=930, y=1600, s=0.8, expr="sorpresa", mirar=(-1, 0), en=0.5)],
         textos=[("dato", "1518", "Estrasburgo", 0.15)]),
    dict(fondo="calle", cam=(1.1, 1.0, 0.5, 0.62),
         actores=[dict(p="mujer_medieval", x=540, y=1740, s=1.25, expr="triste", baile=True)],
         textos=[("texto", 400, "Sin música…", 76, BLANCO, 0.1), ("texto", 500, "durante días", 76, AMARILLO, 0.5)]),
    dict(fondo="calle", cam=(1.0, 1.06, 0.5, 0.6),
         actores=[dict(p="mujer_medieval", x=540, y=1760, s=0.95, expr="triste", baile=True),
                  dict(p="aldeano", x=200, y=1650, s=0.8, expr="sorpresa", baile=True),
                  dict(p="aldeana", x=880, y=1650, s=0.8, expr="triste", baile=True, en=0.2),
                  dict(p="aldeano2", x=360, y=1560, s=0.65, expr="sorpresa", baile=True, en=0.35),
                  dict(p="aldeana", x=730, y=1540, s=0.62, expr="triste", baile=True, en=0.5)],
         textos=[("dato", "Cientos", "bailando sin parar", 0.3)]),
    dict(fondo="calle", cam=(1.0, 1.1, 0.5, 0.6),
         props=[("escenario", dict(x=540, y=1520)), ("notas", dict(x=540, y=1100))],
         actores=[dict(p="musico", x=380, y=1380, s=0.8, expr="risa"),
                  dict(p="musico", x=700, y=1380, s=0.8, expr="risa"),
                  dict(p="autoridad", x=200, y=1800, s=1.0, expr="serio", mirar=(1, -1)),
                  dict(p="mujer_medieval", x=860, y=1800, s=0.95, expr="triste", baile=True)],
         textos=[("etiqueta", 540, 360, "la «cura»: más baile", 0.2)]),
    dict(fondo="calle_tarde", cam=(1.0, 1.1, 0.5, 0.62),
         actores=[dict(p="aldeano", x=180, y=1640, s=0.75, expr="triste", baile=True),
                  dict(p="aldeana", x=880, y=1640, s=0.75, expr="triste", baile=True),
                  dict(p="aldeano2", x=400, y=1560, s=0.65, expr="triste", baile=True),
                  dict(p="aldeana", x=680, y=1560, s=0.65, expr="triste", baile=True),
                  dict(p="mujer_medieval", x=540, y=1800, s=1.0, expr="triste", baile=True)],
         textos=[("texto", 420, "Fue peor", 110, ROJO, 0.15)]),
    dict(fondo="santuario", cam=(1.0, 1.1, 0.6, 0.55), props=[("zapatos", dict(x=300, y=1640, en=0.4))],
         actores=[dict(p="mujer_medieval", x=520, y=1700, s=0.85, expr="triste", mov=(25, 0)),
                  dict(p="aldeano", x=330, y=1760, s=0.85, expr="triste", mov=(25, 0))],
         textos=[("etiqueta", 760, 480, "santuario de san vito", 0.15), ("etiqueta", 300, 1480, "zapatos rojos", 0.45)]),
    dict(fondo="calle_tarde", cam=(1.0, 1.08, 0.5, 0.6),
         actores=[dict(p="historiador", x=540, y=1760, s=1.15, expr="serio", brazos="arriba")],
         textos=[("etiqueta", 540, 330, "histeria colectiva", 0.05), ("texto", 470, "hambre", 66, AMARILLO, 0.25),
                 ("texto", 560, "enfermedades", 66, AMARILLO, 0.45), ("texto", 650, "miedo", 66, ROJO, 0.65)]),
    dict(fondo="calle", cam=(1.0, 1.06, 0.5, 0.6),
         actores=[dict(p="mujer_medieval", x=540, y=1780, s=1.1, expr="sorpresa", baile=True)],
         textos=[("encuesta", "¿Qué crees que fue?", "UNA\nENFERMEDAD", "ALGO\nMÁS", 0.15)]),
])

# =========================================================================== #
# HISTORIA 7: OXFORD Y LOS AZTECAS
# =========================================================================== #
registrar("h7", [
    dict(fondo="oxford", cam=(1.0, 1.1, 0.5, 0.6),
         actores=[dict(p="oxford", x=320, y=1720, s=1.1, expr="risa", brazos="arriba"),
                  dict(p="mexica", x=780, y=1740, s=1.1, expr="sorpresa", mirar=(-1, 0))],
         textos=[("texto", 380, "OXFORD", 90, AMARILLO, 0.1), ("texto", 480, "más antigua que", 54, BLANCO, 0.3),
                 ("texto", 570, "el Imperio azteca", 70, ROJO, 0.45)]),
    dict(fondo="oxford", cam=(1.1, 1.0, 0.5, 0.6),
         actores=[dict(p="prof_oxford", x=540, y=1720, s=1.1, expr="serio", brazos="arriba"),
                  dict(p="oxford", x=220, y=1800, s=0.85, expr="normal", mirar=(1, -1)),
                  dict(p="oxford2", x=860, y=1800, s=0.85, expr="normal", mirar=(-1, -1))],
         textos=[("dato", "1096", "ya se daban clases", 0.15)]),
    dict(fondo="lago", cam=(1.0, 1.15, 0.5, 0.65), props=[("nopal", dict(x=540, y=1350, s=0.9))],
         actores=[dict(p="mexica", x=240, y=1800, s=1.0, expr="sorpresa", mirar=(1, -1)),
                  dict(p="mexica2", x=860, y=1800, s=0.95, expr="risa", mirar=(-1, -1))],
         textos=[("dato", "1325", "fundación de Tenochtitlan", 0.15)]),
    dict(fondo="ciudad_mexica", cam=(1.05, 1.0, 0.5, 0.6),
         actores=[dict(p="mexica", x=260, y=1800, s=0.95, expr="serio"), dict(p="mexica", x=540, y=1820, s=0.95,
                                                                               expr="serio"),
                  dict(p="mexica", x=820, y=1800, s=0.95, expr="serio")],
         textos=[("dato", "1428", "nace el Imperio azteca", 0.15), ("etiqueta", 540, 560, "triple alianza", 0.5)]),
    dict(fondo="ciudad_mexica", cam=(1.0, 1.1, 0.5, 0.62),
         actores=[dict(p="cortes", x=300, y=1780, s=1.1, expr="serio", mirar=(1, 0)),
                  dict(p="mexica", x=780, y=1780, s=1.05, expr="sorpresa", mirar=(-1, 0))],
         textos=[("dato", "1519", "llega Hernán Cortés", 0.1), ("texto", 600, "Oxford: +400 años", 64, AMARILLO, 0.5)]),
    dict(fondo="oxford", cam=(1.0, 1.0, 0.5, 0.6),
         actores=[dict(p="oxford", x=500, y=1740, s=0.9, expr="sorpresa", mov=(260, 0)),
                  dict(p="oxford2", x=320, y=1780, s=0.9, expr="sorpresa", mov=(260, 0)),
                  dict(p="aldeano2", x=0, y=1760, s=1.0, expr="enojado", brazos="arriba", mov=(220, 0)),
                  dict(p="aldeano", x=-200, y=1780, s=1.0, expr="enojado", mov=(220, 0))],
         textos=[("dato", "1209", "nace Cambridge", 0.15)]),
    dict(fondo="papel", cam=(1.0, 1.0, 0.5, 0.5),
         props=[("linea", dict(puntos=[(1096, "Oxford", "#e8b83c"), (1209, "Cambridge", "#3c8cff"),
                                       (1325, "Tenochtitlan", "#3caa5a"), (1428, "Imperio azteca", "#e04040"),
                                       (1519, "Cortés", "#8a5ac8")]))],
         textos=[("etiqueta", 540, 330, "la línea del tiempo", 0.05)]),
    dict(fondo="oxford", cam=(1.0, 1.06, 0.5, 0.6),
         actores=[dict(p="oxford", x=320, y=1780, s=1.0, expr="risa"), dict(p="mexica", x=760, y=1780, s=1.0,
                                                                             expr="sorpresa")],
         textos=[("encuesta", "¿Lo sabías?", "SÍ, LO\nSABÍA", "NI\nIDEA", 0.15)]),
])

# =========================================================================== #
# HISTORIA 8: HIROO ONODA
# =========================================================================== #
registrar("h8", [
    dict(fondo="selva", cam=(1.0, 1.15, 0.5, 0.65),
         actores=[dict(p="onoda", x=540, y=1760, s=1.2, expr="serio", mirar=[(0, (-1, 0)), (0.5, (1, 0))])],
         textos=[("dato", "29 años", "después de la guerra", 0.2)]),
    dict(fondo="playa", cam=(1.1, 1.0, 0.5, 0.6),
         actores=[dict(p="onoda", x=540, y=1760, s=1.1, expr="serio", mov=(-15, 0))],
         textos=[("dato", "1944", "isla de Lubang, Filipinas", 0.15)]),
    dict(fondo="selva", cam=(1.0, 1.12, 0.5, 0.62),
         actores=[dict(p="onoda", x=540, y=1760, s=1.25, expr="enojado", brazos="arriba")],
         textos=[("texto", 420, "«Nunca rendirse»", 84, AMARILLO, 0.25)]),
    dict(fondo="selva", cam=(1.0, 1.08, 0.5, 0.6), props=[("folletos", dict())],
         actores=[dict(p="onoda", x=540, y=1760, s=1.15, expr=[(0, "sorpresa"), (0.5, "enojado")], mirar=(0, -1))],
         textos=[("etiqueta", 540, 360, "«la guerra terminó»", 0.15), ("sello", "¿PROPAGANDA?", 0.55)]),
    dict(fondo="selva_noche", cam=(1.0, 1.15, 0.5, 0.65),
         actores=[dict(p="onoda", x=540, y=1760, s=1.1, expr="triste")],
         textos=[("contador", 1945, 1974, 0.15, ""), ("texto", 720, "solo en la selva", 64, BLANCO, 0.4)]),
    dict(fondo="selva", cam=(1.0, 1.1, 0.5, 0.62),
         actores=[dict(p="aventurero", x=780, y=1760, s=1.05, expr="sorpresa", mirar=(-1, 0)),
                  dict(p="onoda", x=300, y=1760, s=1.05, expr=[(0, "sorpresa"), (0.5, "enojado")], mirar=(1, 0))],
         textos=[("dato", "1974", "lo encuentra un joven aventurero", 0.1), ("texto", 620, "«Sin orden, no me rindo»",
                                                                              56, AMARILLO, 0.55)]),
    dict(fondo="selva", cam=(1.0, 1.1, 0.5, 0.62),
         actores=[dict(p="comandante", x=760, y=1760, s=1.05, expr="serio", brazos="arriba", mirar=(-1, 0)),
                  dict(p="onoda", x=300, y=1760, s=1.05, expr="sorpresa", mirar=(1, 0))],
         textos=[("etiqueta", 620, 860, "su antiguo comandante", 0.15), ("flecha", 760, 1040, 90, 120, 0.15)]),
    dict(fondo="playa", cam=(1.0, 1.1, 0.5, 0.65),
         props=[("espada", dict(x=420, y=1200, ang=-15, s=1.0, delante=True)),
                ("rifle", dict(x=600, y=1840, s=1.0))],
         actores=[dict(p="onoda", x=330, y=1760, s=1.1, expr="triste", brazos="arriba")],
         textos=[("texto", 400, "Entregó su espada", 66, BLANCO, 0.1),
                 ("texto", 500, "su rifle aún funcionaba", 62, AMARILLO, 0.5)]),
    dict(fondo="selva", cam=(1.0, 1.06, 0.5, 0.6),
         actores=[dict(p="onoda", x=540, y=1780, s=1.1, expr="serio")],
         textos=[("encuesta", "¿Tú habrías aguantado?", "SÍ, YO\nTAMBIÉN", "NI\nLOCO", 0.15)]),
])

# =========================================================================== #
# HISTORIA 9: EL ROBO DE LA MONA LISA
# =========================================================================== #
registrar("h9", [
    dict(fondo="museo", cam=(1.0, 1.12, 0.5, 0.45), props=[("marco", dict(x=540, y=820))],
         actores=[dict(p="visitante", x=300, y=1760, s=1.0, expr="normal", mirar=(1, -1)),
                  dict(p="visitante2", x=780, y=1760, s=1.0, expr="normal", mirar=(-1, -1))],
         textos=[("texto", 1230, "No siempre fue famosa…", 58, AMARILLO, 0.4)]),
    dict(fondo="museo_noche", cam=(1.0, 1.12, 0.5, 0.6), props=[("marco", dict(x=540, y=820))],
         actores=[dict(p="peruggia", x=860, y=1760, s=1.1, expr="serio", mirar=(-1, -1))],
         textos=[("dato", "1911", "museo del Louvre", 0.1), ("etiqueta", 700, 1000, "vincenzo peruggia", 0.4),
                 ("flecha", 860, 1170, 90, 110, 0.4)]),
    dict(fondo="museo_noche", cam=(1.0, 1.05, 0.5, 0.6), props=[("marco", dict(x=540, y=820, vacio=True)),
                                                               ("cuadro_robado", dict(x=330, y=1500, vx=60, delante=True))],
         actores=[dict(p="peruggia", x=300, y=1760, s=1.1, expr="sorpresa", mov=(60, 0))],
         textos=[("texto", 1150, "bajo su bata…", 64, AMARILLO, 0.3)]),
    dict(fondo="museo", cam=(1.0, 1.1, 0.5, 0.5), props=[("marco", dict(x=540, y=820, vacio=True))],
         actores=[dict(p="guardia", x=780, y=1760, s=1.05, expr="normal", mirar=(1, 0))],
         textos=[("texto", 1150, "¡Nadie lo notó!", 90, ROJO, 0.3)]),
    dict(fondo="taller", cam=(1.0, 1.08, 0.5, 0.55), props=[("periodico", dict(x=540, y=760))],
         actores=[dict(p="picasso", x=280, y=1760, s=1.05, expr="sorpresa", mirar=(1, 0), en=0.45),
                  dict(p="policia", x=780, y=1760, s=1.05, expr="enojado", mirar=(-1, 0), en=0.45)],
         textos=[("etiqueta", 280, 1300, "pablo picasso", 0.5)]),
    dict(fondo="museo", cam=(1.0, 1.06, 0.5, 0.55), props=[("marco", dict(x=540, y=820, vacio=True))],
         actores=[dict(p="visitante", x=160, y=1760, s=0.9, expr="sorpresa", mirar=(1, -1)),
                  dict(p="visitante2", x=400, y=1800, s=0.9, expr="sorpresa", mirar=(0, -1)),
                  dict(p="aldeana", x=660, y=1800, s=0.9, expr="sorpresa", mirar=(0, -1)),
                  dict(p="bostoniano", x=900, y=1760, s=0.9, expr="sorpresa", mirar=(-1, -1))],
         textos=[("texto", 380, "Miles hicieron fila…", 62, BLANCO, 0.15),
                 ("texto", 470, "para ver NADA", 70, AMARILLO, 0.45)]),
    dict(fondo="taller", cam=(1.0, 1.1, 0.5, 0.6),
         actores=[dict(p="peruggia", x=300, y=1760, s=1.05, expr=[(0, "risa"), (0.6, "sorpresa")], mirar=(1, 0)),
                  dict(p="comerciante", x=640, y=1760, s=1.05, expr="serio", mirar=(-1, 0)),
                  dict(p="policia", x=900, y=1760, s=1.0, expr="enojado", mirar=(-1, 0), en=0.6)],
         textos=[("dato", "1913", "Florencia, Italia", 0.1)]),
    dict(fondo="museo", cam=(1.0, 1.12, 0.5, 0.45), props=[("marco", dict(x=540, y=820, brillo=True))],
         actores=[dict(p="visitante", x=220, y=1780, s=0.9, expr="risa"), dict(p="visitante2", x=860, y=1780, s=0.9,
                                                                               expr="risa")],
         textos=[("texto", 1230, "la más famosa del mundo", 62, AMARILLO, 0.3)]),
    dict(fondo="museo", cam=(1.0, 1.05, 0.5, 0.55), props=[("marco", dict(x=540, y=1300, w=300, h=410))],
         textos=[("encuesta", "¿La has visto en persona?", "SÍ, LA\nVI", "TODAVÍA\nNO", 0.15)]),
])

# =========================================================================== #
# HISTORIA 10: LA OLA DE MELAZA
# =========================================================================== #
registrar("h10", [
    dict(fondo="boston", cam=(1.0, 1.1, 0.5, 0.6),
         props=[("tanque", dict(x=760, y=1250)), ("ola", dict(avance=0.0))],
         actores=[dict(p="bostoniano", x=260, y=1760, s=1.1, expr=[(0, "normal"), (0.5, "sorpresa")],
                       mirar=(1, -1))],
         textos=[("dato", "1919", "Boston, EE. UU.", 0.1), ("texto", 600, "una ola de MELAZA", 64, AMARILLO, 0.55)]),
    dict(fondo="boston", cam=(1.1, 1.0, 0.6, 0.55), props=[("tanque", dict(x=640, y=1250))],
         actores=[dict(p="bostoniana", x=200, y=1760, s=0.95, expr="sorpresa", mirar=(1, -1))],
         textos=[("dato", "+8 millones", "de litros de melaza", 0.15)]),
    dict(fondo="boston", cam=(1.0, 1.1, 0.6, 0.55),
         props=[("tanque", dict(x=640, y=1250, gotas=True, pintura=0.0))],
         actores=[dict(p="pintor", x=260, y=1760, s=1.0, expr="risa", brazos="arriba", mirar=(1, -1))],
         textos=[("texto", 420, "¿Fugas?", 90, ROJO, 0.1), ("texto", 520, "lo pintaron de café", 62, AMARILLO, 0.45)]),
    dict(fondo="boston", cam=(1.0, 1.0, 0.5, 0.6),
         props=[("tanque", dict(x=760, y=1250, roto=True)), ("ola", dict(avance=0.6))],
         actores=[dict(p="bostoniano", x=300, y=1760, s=1.05, expr="sorpresa", mov=(-60, 0))],
         textos=[("dato", "7 metros", "a 50 km/h", 0.15)]),
    dict(fondo="boston", cam=(1.0, 1.05, 0.5, 0.6),
         props=[("vagon", dict(x=640, y=1450, ang=18)), ("ola", dict(avance=1.0, y_max=1500))],
         actores=[dict(p="bostoniana", x=260, y=1800, s=0.95, expr="sorpresa", mov=(-40, 0))],
         textos=[("texto", 420, "edificios, vagones…", 66, BLANCO, 0.15)]),
    dict(fondo="boston_frio", cam=(1.0, 1.1, 0.5, 0.62), props=[("nieve", dict()), ("ola", dict(avance=1.2,
                                                                                               y_max=1650))],
         actores=[dict(p="rescatista", x=380, y=1720, s=1.0, expr="triste"),
                  dict(p="rescatista", x=720, y=1720, s=1.0, expr="triste")],
         textos=[("dato", "21 víctimas", "y unos 150 heridos", 0.15), ("texto", 600, "el frío la espesó", 60,
                                                                          AMARILLO, 0.55)]),
    dict(fondo="oficina", cam=(1.0, 1.08, 0.5, 0.6), props=[("planos", dict(x=540, y=1240))],
         actores=[dict(p="ingeniero", x=540, y=1760, s=1.1, expr="serio", brazos="arriba")],
         textos=[("etiqueta", 540, 200, "nuevas leyes de construcción", 0.15)]),
    dict(fondo="boston", cam=(1.0, 1.1, 0.5, 0.6),
         actores=[dict(p="bostoniano", x=540, y=1760, s=1.15, expr="sorpresa", mirar=(0, -1))],
         textos=[("texto", 420, "olió a melaza", 76, AMARILLO, 0.2), ("texto", 520, "durante décadas", 66, BLANCO,
                                                                       0.4)]),
    dict(fondo="boston", cam=(1.0, 1.06, 0.5, 0.6),
         actores=[dict(p="bostoniana", x=540, y=1780, s=1.1, expr="sorpresa")],
         textos=[("encuesta", "¿Habías escuchado esta historia?", "SÍ", "NUNCA", 0.15)]),
])
