#!/usr/bin/env python3
"""
Serie "MISTERIOS SIN RESOLVER": motor automático semi-realista.

Cada misterio combina 4 escenas de una biblioteca de "kits" según su tema, con variaciones propias
(colores, cámara, posiciones, titular, año, nombre) + un final que rota entre 4 estilos.
Usa: dibujo realista (LienzoReal), acabado de cine, audio hi-fi y mezcla con la voz por encima.

    python misterios.py 12            # un misterio
    python misterios.py todos         # todos los que tengan voz verificada
"""
from __future__ import annotations

import json
import math
import random
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import pro
from pro import BLANCO, Escena, H, W, chip, dibujar_avion, manuscrita, numero, particulas, relampago
from alcatraz import ficha, maquina, niebla, olas, sello, silueta
from caricatura import ease, pop
from cine import pegar_glow
from dinos import TINTA, _grad, capsula, catmull, elipse, oscuro, claro, radius_ok, sombra_suave
from generar_short import render_emoji
from realista import LienzoReal
from verificar_misterios import cargar_guiones
import mis_reales as R
from mis_kits import DETALLES, KITS_EXTRA, figura, nubes, objeto, personas_de

RAIZ = Path(__file__).resolve().parent
ESTILO = {"modo": "color", "color": (255, 200, 80)}
AMBAR = (255, 200, 80)
CARPETA_SALIDA = RAIZ / "misterios nuevos"

PALETAS = {
    "noche": [(0, (8, 12, 28)), (0.6, (28, 38, 66)), (1, (28, 38, 66))],
    "tormenta": [(0, (16, 18, 26)), (0.6, (50, 56, 68)), (1, (50, 56, 68))],
    "niebla": [(0, (104, 112, 122)), (0.6, (168, 172, 176)), (1, (168, 172, 176))],
    "atardecer": [(0, (46, 36, 74)), (0.5, (196, 104, 86)), (0.62, (236, 166, 108)), (1, (236, 166, 108))],
    "frio": [(0, (60, 80, 120)), (0.55, (176, 170, 184)), (1, (176, 170, 184))],
    "verde": [(0, (8, 22, 20)), (0.6, (28, 56, 50)), (1, (28, 56, 50))],
    "purpura": [(0, (10, 8, 26)), (0.6, (54, 36, 70)), (1, (54, 36, 70))],
    "dia": [(0, (52, 112, 186)), (0.55, (150, 196, 230)), (1, (196, 222, 236))],
}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def full(dib):
    L = LienzoReal(W, H, 0, 0)
    dib(L)
    return L.final()


# =========================================================================== #
# PIEZAS DE DIBUJO
# =========================================================================== #
def mar(L, y0, col):
    L.forma([(0, y0), (W, y0), (W, H), (0, H)], col, suave=False, borde=False, intensidad=0.02, textura=0.08)


def velero(L, x, y, s, col=(24, 22, 26)):
    """Bergantín de tres palos con velas cuadradas, bauprés, foque y jarcia."""
    sil = col[0] > 60  # en niebla: silueta clara y sin detalle
    casco = col if sil else (66, 44, 32)
    vela = claro(col, 0.25) if sil else (206, 200, 182)
    palo = oscuro(casco, 0.7)
    P = lambda a, b: (x + a * s, y + b * s)
    # jarcia (detrás de las velas)
    tops = {-170: -560, 10: -640, 180: -520}
    for mx, top in tops.items():
        for dx in (-150, 150):
            L.linea([P(mx, top + 20), P(mx + dx * 1.3, -40)], oscuro(casco, 0.6), 2.2 * s)
    L.linea([P(10, -640), P(470, -170)], oscuro(casco, 0.6), 2.5 * s)
    L.linea([P(-170, -560), P(10, -640)], oscuro(casco, 0.6), 2.5 * s)
    # palos y bauprés
    for mx, top in tops.items():
        L.linea([P(mx, -40), P(mx, top)], palo, 9 * s)
    L.linea([P(290, -80), P(480, -170)], palo, 8 * s)
    # velas cuadradas (3 por palo, de mayor a menor) algo hinchadas
    for mx, top in tops.items():
        alto_total = -40 - top - 60
        for n in range(3):
            y0 = top + 30 + n * alto_total / 3
            y1 = y0 + alto_total / 3 - 18
            a0 = 70 + n * 22
            a1 = 82 + n * 24
            L.forma([P(mx - a0, y0), P(mx + a0, y0), P(mx + a1 + 6, y1), P(mx + 4, y1 + 10), P(mx - a1, y1)], vela,
                    suave=False, intensidad=0.16, textura=0.1, ancho=3)
            L.linea([P(mx - a0 - 8, y0), P(mx + a0 + 8, y0)], palo, 5 * s)
    # foque triangular
    L.forma([P(30, -600), P(450, -170), P(60, -150)], vela, suave=False, intensidad=0.12, textura=0.08, ancho=3)
    # casco con popa alta y proa afilada
    L.forma([P(-330, -110), P(-250, -60), P(250, -60), P(330, -100), P(270, 20), P(150, 55), P(-250, 55), P(-320, 0)],
            casco, suave=False, intensidad=0.1, textura=0.14)
    L.linea([P(-320, -40), P(300, -40)], claro(casco, 0.25), 4 * s)
    if not sil:
        for k in range(7):
            L.circulo(*P(-200 + k * 60, -10), 7 * s, oscuro(casco, 0.6), borde=False)


def buque(L, x, y, s, col=(30, 32, 38)):
    """Vapor de casco largo: línea de flotación roja, superestructura, chimenea y ojos de buey."""
    sil = col[0] > 60
    casco = col if sil else (34, 36, 44)
    blanco = claro(col, 0.3) if sil else (214, 210, 200)
    P = lambda a, b: (x + a * s, y + b * s)
    for mx in (-260, 300):  # mástiles y cables
        L.linea([P(mx, -70), P(mx, -420)], oscuro(casco, 0.8), 7 * s)
    L.linea([P(-260, -410), P(300, -410)], oscuro(casco, 0.6), 2 * s)
    L.linea([P(-260, -410), P(-440, -80)], oscuro(casco, 0.6), 2 * s)
    L.linea([P(300, -410), P(460, -90)], oscuro(casco, 0.6), 2 * s)
    L.forma([P(-120, -70), P(170, -70), P(160, -190), P(-110, -190)], blanco, suave=False, intensidad=0.1)
    L.forma([P(-70, -190), P(130, -190), P(120, -250), P(-60, -250)], blanco, suave=False, intensidad=0.1)
    L.forma([P(0, -250), P(70, -250), P(64, -380), P(6, -380)], (150, 40, 34) if not sil else oscuro(col, 0.85),
            suave=False, intensidad=0.12)
    L.forma([P(4, -380), P(66, -380), P(66, -360), P(4, -360)], (24, 24, 28), suave=False, borde=False)
    if not sil:
        for k in range(8):
            L.circulo(*P(-90 + k * 32, -130), 7 * s, (240, 210, 130), borde=False)
    L.forma([P(-450, -90), P(470, -95), P(400, 40), P(-400, 40)], casco, suave=False, intensidad=0.08, textura=0.12)
    if not sil:
        L.forma([P(-415, 10), P(415, 10), P(400, 40), P(-400, 40)], (130, 34, 30), suave=False, borde=False)
        for k in range(14):
            L.circulo(*P(-360 + k * 54, -40), 6 * s, (90, 96, 110), borde=False)


def piramide(L, cx, base, ancho, alto, col):
    L.forma([(cx - ancho / 2, base), (cx, base - alto), (cx + ancho / 2, base)], col, suave=False, intensidad=0.12)
    for k in range(1, 8):
        f = k / 8
        L.linea([(cx - ancho / 2 * (1 - f), base - alto * f), (cx + ancho / 2 * (1 - f), base - alto * f)],
                oscuro(col, 0.8), 3)


def pinos(L, base, n, alto, col, r):
    for _ in range(n):
        x, h = r.uniform(-60, W + 60), alto * r.uniform(0.7, 1.25)
        L.forma([(x - h * 0.2, base), (x, base - h), (x + h * 0.2, base)], col, suave=False, intensidad=0.08,
                textura=0.04)


def ojo_brillo(img, x, y, t, col="#ffd060"):
    k = 0.6 + 0.4 * math.sin(t * 3)
    for dx in (-16, 16):
        pegar_glow(img, x + dx, y, 14, col, k)


# =========================================================================== #
# KITS DE ESCENA: cada uno devuelve (fondo, dinamico(img, t, dur))
# =========================================================================== #
def kit_mar(ctx, var):
    r, det = ctx["rnd"], ctx["det"]
    base = det.get("hora")
    paleta = (base if var == 0 and base else ["tormenta", "niebla", "noche", "atardecer", "dia"][(ctx["n"] + var) % 5])
    if base == "frio" or det.get("bar") == "franklin":
        paleta = "frio"
    modelo = det.get("bar") or ("vapor_waratah" if re.search(r"buque|vapor|carguero|transatl", ctx["txt"])
                                else "bergantin")
    agua = {"niebla": (92, 104, 112), "dia": (40, 100, 140), "atardecer": (70, 64, 90), "frio": (150, 170, 186)}
    agua = agua.get(paleta, (22, 34, 46))

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[paleta]))
        mar(L, 1150, agua)
        if paleta == "frio":  # témpanos y hielo del Ártico
            rr = random.Random(ctx["n"])
            for _ in range(7):
                x = rr.uniform(-50, W + 50)
                L.forma([(x - 160, 1180), (x - 120, 1120), (x + 90, 1110), (x + 170, 1180)], (232, 240, 248),
                        suave=False, intensidad=0.12, textura=0.06)
            L.forma([(-50, 1500), (W + 50, 1460), (W + 50, H), (-50, H)], (226, 236, 244), suave=False, borde=False,
                    textura=0.08)
    fondo = full(dib)
    if paleta == "atardecer":
        pegar_glow(fondo, 760, 1130, 300, "#ffb070", 0.8)
    elif paleta == "dia":
        pegar_glow(fondo, 840, 300, 160, "#fff6d0", 0.8)
    barco = R.barco_real(modelo, sil=(84, 88, 94) if paleta == "niebla" else None)
    escala = 0.78
    barco = barco.resize((int(barco.width * escala), int(barco.height * escala)), Image.LANCZOS)
    escora = det.get("escora", 0)
    bx = r.uniform(400, 680)
    deriva = 10 if modelo != "franklin" else 0

    def din(img, t, dur):
        nubes(img, t, paleta, y=560, n=4, semilla=ctx["n"])
        bob = 10 * math.sin(t * 1.4) if modelo != "franklin" else 0
        b = barco.rotate(escora + 2.5 * math.sin(t * 1.1) * (deriva > 0), resample=Image.BICUBIC)
        img.alpha_composite(b, (int(bx - b.width / 2 + t * deriva), int(1185 - b.height * 0.76 + bob)))
        if modelo != "franklin":
            olas(img, t, 1170, col=(120, 150, 180) if paleta not in ("niebla", "dia") else (220, 230, 240), alfa=120)
        if paleta == "tormenta":
            particulas(img, t, "lluvia", 90, viento=-300, alfa=190)
            for t0 in (0.5, dur * 0.6):
                relampago(img, t, t0)
        elif paleta == "frio":
            particulas(img, t, "nieve", 70, viento=-160, alfa=220)
        niebla(img, t, 1100, 0.5 if paleta == "niebla" else 0.2, n=9)
    return fondo, din


def kit_avion(ctx, var):
    r, n, det = ctx["rnd"], ctx["n"], ctx["det"]
    modelo = det.get("av")
    pal = det.get("hora") if (var == 0 and det.get("hora")) else ["noche", "tormenta", "atardecer", "niebla"][(n + var) % 4]
    if var == 1 and pal == "dia":
        pal = "niebla"
    cuantos = det.get("nav", 1)
    izquierda = n % 2 == 1 and modelo != "globo"
    nubes_hora = {"noche": "noche", "tormenta": "noche"}.get(pal, pal)
    fondo_tipo = det.get("fondo", "mar")

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[pal]))
        if fondo_tipo == "andes":
            pro.montanas(L, 1700, [(150, 900, 700), (600, 1000, 820), (1000, 800, 640)], (90, 96, 116), nieve=True,
                         borde=False)
            L.forma([(-50, 1690), (W + 50, 1690), (W + 50, H), (-50, H)], (232, 238, 246), suave=False, borde=False)
        elif fondo_tipo == "desierto":
            L.forma([(-50, 1450), (W + 50, 1420), (W + 50, H), (-50, H)], (206, 168, 124), suave=False, borde=False,
                    textura=0.14)
            pro.montanas(L, 1440, [(200, 600, 200), (800, 700, 240)], (170, 128, 96), nieve=False, borde=False)
        elif fondo_tipo == "artico":
            L.forma([(-50, 1450), (W + 50, 1420), (W + 50, H), (-50, H)], (226, 236, 244), suave=False, borde=False,
                    textura=0.1)
            rr = random.Random(2)
            for _ in range(6):
                x = rr.uniform(0, W)
                L.forma([(x - 100, 1460), (x - 40, 1380), (x + 60, 1400), (x + 110, 1460)], (210, 224, 236),
                        suave=False, intensidad=0.1)
        else:
            agua = {"atardecer": (60, 50, 70), "niebla": (110, 118, 124), "dia": (40, 104, 150)}.get(pal, (14, 22, 34))
            mar(L, 1500, agua)
            if det.get("isla"):  # isla Howland: diminuta y plana en medio del Pacífico
                L.forma(catmull([(380, 1515), (470, 1490), (640, 1490), (720, 1515)], 4), (214, 196, 150),
                        intensidad=0.1)
        if pal in ("noche", "tormenta"):
            rr = random.Random(n)
            for _ in range(110):
                L.circulo(rr.randint(0, W), rr.randint(0, 1100), rr.choice((1.5, 2, 2.5)), (230, 230, 255),
                          borde=False)
    fondo = full(dib)
    if pal == "noche":
        mx = 260 if izquierda else 800
        pegar_glow(fondo, mx, 330, 150, "#dfe8ff", 0.6)
        ImageDraw.Draw(fondo).ellipse((mx - 40, 290, mx + 40, 370), fill=(236, 238, 246))
        pegar_glow(fondo, mx, 1560, 220, "#9fb0d0", 0.35)
    elif pal == "atardecer":
        pegar_glow(fondo, 540, 1450, 380, "#ffb070", 0.7)
    elif pal == "dia":
        pegar_glow(fondo, 860, 260, 170, "#fff6d0", 0.9)
    if modelo:
        av = R.avion_real(modelo)
        ancho_obj = {"globo": 380}.get(modelo, 760 if cuantos == 1 else 330)
    else:
        a_ = int(ctx["anio"] or 1970)
        av = pro.avion("helice" if a_ < 1950 else ("electra" if a_ < 1975 else "727"))
        ancho_obj = 760 if cuantos == 1 else 330
    k = ancho_obj / av.width
    sombra_luz = {"noche": 0.45, "tormenta": 0.5, "niebla": 0.25, "atardecer": 0.3, "dia": 0.0, "frio": 0.1}[pal]
    sil = av.resize((int(av.width * k), int(av.height * k)), Image.LANCZOS)
    if sombra_luz:
        osc = Image.new("RGBA", sil.size, (20, 24, 34, 255))
        osc.putalpha(sil.getchannel("A"))
        sil = Image.blend(sil, osc, sombra_luz)
    if izquierda:
        sil = sil.transpose(Image.FLIP_LEFT_RIGHT)
    y0 = r.uniform(820, 1000) if modelo != "globo" else 760
    formacion = [(0, 0), (-210, -120), (-210, 120), (-420, -240), (-420, 240)][:cuantos]

    def din(img, t, dur):
        nubes(img, t, nubes_hora, y=760, n=5, semilla=n)
        if modelo == "globo":
            x = 540 + 40 * math.sin(t * 0.3)
            yy = y0 + t * 14 + 10 * math.sin(t)
            img.alpha_composite(sil, (int(x - sil.width / 2), int(yy - sil.height / 2)))
        else:
            avance = W * 0.7 * (t / max(dur, 0.1))
            x = (W - 300 - avance) if izquierda else (300 + avance)
            sgn = -1 if izquierda else 1
            for j, (dx, dy) in enumerate(formacion):
                xx, yy = x + dx * sgn, y0 + dy + 8 * math.sin(t * 1.3 + j)
                img.alpha_composite(sil.rotate(2.5 * math.sin(t * 0.9 + j), resample=Image.BICUBIC),
                                    (int(xx - sil.width / 2), int(yy - sil.height / 2)))
                if pal in ("noche", "tormenta", "niebla") and int(t * 2 + j) % 2 == 0:
                    pegar_glow(img, xx + sgn * sil.width * 0.1, yy - sil.height * 0.1, 16, "#ff3030", 1.0)
            if det.get("ovni") == "verde":  # Valentich: una luz verde lo seguía
                pegar_glow(img, x - sgn * 260 + 40 * math.sin(t * 1.7), y0 - 220 + 30 * math.sin(t * 2.3), 90,
                           "#60ff80", 0.85)
            elif det.get("ovni") == "tictac":  # Nimitz: objeto blanco con forma de pastilla
                ox, oy = x + sgn * 360, y0 + 260 + 20 * math.sin(t * 3)
                ImageDraw.Draw(img).rounded_rectangle((ox - 90, oy - 26, ox + 90, oy + 26), radius=26,
                                                      fill=(246, 246, 246), outline=(200, 200, 206), width=3)
                pegar_glow(img, ox, oy, 120, "#ffffff", 0.35)
        if pal == "tormenta":
            particulas(img, t, "lluvia", 80, viento=-400, alfa=160)
            relampago(img, t, dur * 0.5)
        elif pal == "niebla":
            niebla(img, t, 1100, 0.5, n=10)
        elif pal == "frio":
            particulas(img, t, "nieve", 70, viento=-300, alfa=220)
    return fondo, din


def kit_radar(ctx, var):
    n = ctx["n"]
    tono = [((6, 14, 10), (40, 160, 90), (60, 255, 140), "#60ff90"),
            ((16, 10, 4), (170, 110, 30), (255, 180, 60), "#ffc060"),
            ((4, 10, 18), (40, 120, 170), (90, 200, 255), "#80d0ff")][n % 3]
    fondo = _grad(W, H, [(0, tono[0]), (1, oscuro(tono[0], 0.4))])
    r = ctx["rnd"]
    blips = [(r.uniform(-1, 1) * 260, r.uniform(-1, 1) * 260) for _ in range(3 + n % 4)]
    cy = 860 + (n % 3) * 40

    def din(img, t, dur):
        cx, R = 540, 400
        d = ImageDraw.Draw(img)
        for k in range(1, 5):
            d.ellipse((cx - R * k / 4, cy - R * k / 4, cx + R * k / 4, cy + R * k / 4), outline=tono[1], width=3)
        d.line((cx - R, cy, cx + R, cy), fill=oscuro(tono[1], 0.7), width=2)
        d.line((cx, cy - R, cx, cy + R), fill=oscuro(tono[1], 0.7), width=2)
        ang = t * 2.2 * (1 if n % 2 else -1)
        for k in range(18):
            a = ang - k * 0.04 * (1 if n % 2 else -1)
            d.line((cx, cy, cx + R * math.cos(a), cy + R * math.sin(a)), fill=tono[2] + (int(140 * (1 - k / 18)),),
                   width=6)
        for i, (bx, by) in enumerate(blips):
            if not (i == 0 and t > dur * 0.55):
                pegar_glow(img, cx + bx, cy + by, 22, tono[3], 0.6 + 0.4 * math.sin(t * 4 + i))
        d.text((cx, cy + R + 50), f"{(n * 37) % 90 + 10}°{(n * 13) % 60:02d}' N", font=maquina(40), fill=tono[2],
               anchor="mm")
        if t > dur * 0.55:
            d.text((cx, cy - R - 70), "SEÑAL PERDIDA", font=maquina(54), fill=(255, 80, 80), anchor="mm")
    return fondo, din


def kit_radio(ctx, var):
    n = ctx["n"]
    madera = [(92, 58, 34), (70, 44, 30), (110, 80, 50)][n % 3]

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (24, 20, 18)), (1, (10, 8, 8))]))
        L.forma([(0, 1380), (W, 1380), (W, H), (0, H)], oscuro(madera, 0.7), suave=False, borde=False, textura=0.15)
        L.forma([(150, 1390), (930, 1390), (930, 820), (150, 820)], madera, suave=False, intensidad=0.1,
                textura=0.16)
        L.forma([(190, 860), (520, 860), (520, 1340), (190, 1340)], (40, 30, 24), suave=False, intensidad=0.05)
        for y in range(890, 1330, 26):
            L.linea([(205, y), (505, y)], (70, 54, 40), 6)
        L.forma([(570, 870), (890, 870), (890, 1010), (570, 1010)], (60, 44, 30), suave=False)
        for x in (640, 820):
            L.forma(elipse(x, 1200, 62, 62), (40, 34, 30), intensidad=0.25)
            L.forma(elipse(x, 1200, 40, 40), (180, 160, 120), intensidad=0.3)
        L.forma([(260, 560), (820, 560), (820, 780), (260, 780)], (30, 34, 32), suave=False, intensidad=0.08)
    fondo = full(dib)
    texto = ctx["det"].get("radio") or ("· · · — — — · · ·" if var != 1 or not ctx["canva"] else
                                        ctx["canva"].strip("¿?«»").upper()[:18])

    def din(img, t, dur):
        d = ImageDraw.Draw(img)
        fl = 0.8 + 0.2 * math.sin(t * 9)
        d.rectangle((590, 890, 870, 990), fill=(255, 190, 90))
        pegar_glow(img, 730, 940, 200 * fl, "#ffb050", 0.6)
        aguja = 600 + (260 * (0.5 + 0.5 * math.sin(t * 0.7)))
        d.line((aguja, 892, aguja, 988), fill=(150, 20, 20), width=6)
        d.rectangle((280, 580, 800, 760), fill=(10, 24, 16))
        amp = 50 * (0.4 + 0.6 * abs(math.sin(t * 2.3)))
        if t > dur * 0.6:
            amp *= max(0.05, 1 - (t - dur * 0.6) * 1.5)
        pts = [(280 + i * 4, 670 + amp * math.sin(i * 0.35 + t * 12) * math.sin(i * 0.05 + t)) for i in range(131)]
        d.line(pts, fill=(90, 255, 140), width=5)
        pegar_glow(img, 540, 670, 260, "#60ff90", 0.25)
        vis = texto[:max(0, int(t * 7))]
        d.text((540, 470), vis, font=maquina(52), fill=(255, 220, 160), anchor="mm")
    return fondo, din


def kit_faro(ctx, var):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS["tormenta"]))
        mar(L, 1250, (20, 30, 42))
        L.forma(catmull([(160, 1300), (300, 1080), (700, 1040), (900, 1150), (980, 1300)], 4), (50, 48, 50),
                intensidad=0.1, textura=0.1)
        torre = L.forma([(520, 1060), (560, 520), (640, 520), (680, 1060)], (226, 222, 214), suave=False,
                        intensidad=0.1)
        estilo = ctx["det"].get("faro", "rojo")
        if estilo == "espiral":
            for k in range(-3, 6):
                y = 560 + k * 130
                L.forma([(480, y), (720, y - 120), (720, y - 50), (480, y + 70)], (30, 30, 34), suave=False,
                        borde=False, clip=torre, sombra=False)
        elif estilo == "rojo":
            for k in range(3):
                L.forma([(530, 900 - k * 140), (670, 900 - k * 140), (668, 860 - k * 140), (532, 860 - k * 140)],
                        (170, 40, 40), suave=False, borde=False)
        L.forma([(540, 520), (660, 520), (650, 440), (550, 440)], (40, 40, 46), suave=False)
        L.forma([(530, 440), (600, 380), (670, 440)], (60, 60, 66), suave=False)
    fondo = full(dib)

    def din(img, t, dur):
        ang = math.pi + 1.3 * math.sin(t * 0.8)
        capa = Image.new("L", (W // 4, H // 4), 0)
        d4 = ImageDraw.Draw(capa)
        x, y = 600, 480
        d4.polygon([(x / 4, y / 4), ((x + 1500 * math.cos(ang - 0.09)) / 4, (y + 300 * math.sin(ang - 0.09)) / 4),
                    ((x + 1500 * math.cos(ang + 0.09)) / 4, (y + 300 * math.sin(ang + 0.09)) / 4)],
                   fill=0 if (var == 2 and t > dur * 0.5) else 120)
        luz = Image.new("RGBA", (W, H), (255, 246, 210, 0))
        luz.putalpha(capa.filter(ImageFilter.GaussianBlur(4)).resize((W, H)))
        img.alpha_composite(luz)
        if not (var == 2 and t > dur * 0.5):
            pegar_glow(img, x, y, 70, "#fff6d0", 0.9)
        olas(img, t, 1260)
        particulas(img, t, "lluvia", 80, viento=-350, alfa=180)
    return fondo, din


def kit_espacio(ctx, var):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS["purpura"]))
        rr = random.Random(5)
        for _ in range(260):
            L.circulo(rr.randint(0, W), rr.randint(0, 1400), rr.choice((1.5, 2, 3)), (236, 236, 255), borde=False)
        L.forma([(0, 1450), (W, 1420), (W, H), (0, H)], (30, 30, 40), suave=False, borde=False)
        L.forma(elipse(540, 1120, 340, 150, -0.25), (190, 196, 206), intensidad=0.15)
        L.forma([(520, 1200), (560, 1200), (600, 1450), (480, 1450)], (150, 156, 166), suave=False)
        L.linea([(540, 1120), (700, 900)], (170, 176, 186), 10)
    fondo = full(dib)

    def din(img, t, dur):
        for k in range(4):
            f = ((t * 0.35 + k / 4) % 1)
            rr_ = 60 + 700 * f
            d = ImageDraw.Draw(img)
            d.arc((700 - rr_, 900 - rr_, 700 + rr_, 900 + rr_), 200, 320, fill=(200, 160, 255, int(200 * (1 - f))),
                  width=5)
        pegar_glow(img, 700, 900, 40, "#d8b0ff", 0.8)
    return fondo, din


def kit_luces(ctx, var):
    ovni = bool(re.search(r"ovni|objeto|disco|tic tac|nimitz|roswell", ctx["txt"]))
    pal = "purpura" if var else "noche"

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[pal]))
        rr = random.Random(7)
        for _ in range(200):
            L.circulo(rr.randint(0, W), rr.randint(0, 1200), rr.choice((1.5, 2, 2.5)), (230, 230, 255), borde=False)
        pro.montanas(L, 1350, [(200, 800, 380), (800, 700, 300)], (26, 26, 40), nieve=False, borde=False)
        L.forma([(0, 1350), (W, 1340), (W, H), (0, H)], (20, 22, 30), suave=False, borde=False)
    fondo = full(dib)
    r = ctx["rnd"]
    pts = [(r.uniform(150, 930), r.uniform(450, 1000), r.uniform(0, 6)) for _ in range(5)]

    tipo_ovni = ctx["det"].get("ovni")

    def din(img, t, dur):
        if tipo_ovni == "v":  # luces de Phoenix: siete luces en V sobre la ciudad
            for k in range(7):
                dx = (k - 3) * 110
                pegar_glow(img, 540 + dx + t * 10, 600 + abs(dx) * 0.5, 40, "#ffcf80", 0.9)
            for k in range(40):
                pegar_glow(img, 20 + k * 27, 1360 + (k % 3) * 8, 10, "#ffd080", 0.6)
            return
        if tipo_ovni == "verde":
            pegar_glow(img, 540 + 160 * math.sin(t * 0.8), 700 + 60 * math.sin(t * 1.9), 140, "#60ff80", 0.85)
            return
        if tipo_ovni == "tictac":
            x, y = 540 + 220 * math.sin(t * 1.4), 800 + 50 * math.sin(t * 2.2)
            ImageDraw.Draw(img).rounded_rectangle((x - 110, y - 32, x + 110, y + 32), radius=32,
                                                  fill=(246, 246, 246), outline=(200, 200, 206), width=3)
            pegar_glow(img, x, y, 160, "#ffffff", 0.3)
            return
        if ovni:
            x, y = 540 + 200 * math.sin(t * 0.6), 700 + 40 * math.sin(t * 1.3)
            d = ImageDraw.Draw(img)
            d.ellipse((x - 170, y - 30, x + 170, y + 34), fill=(180, 190, 200), outline=(40, 40, 50), width=4)
            d.ellipse((x - 70, y - 80, x + 70, y + 10), fill=(150, 190, 220), outline=(40, 40, 50), width=4)
            for k in range(6):
                pegar_glow(img, x - 140 + k * 56, y + 10, 18, "#9fe8ff", 0.6 + 0.4 * math.sin(t * 6 + k))
            if var:
                capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(capa).polygon([(x - 60, y + 30), (x + 60, y + 30), (x + 260, 1400), (x - 260, 1400)],
                                             fill=(170, 240, 255, 70))
                img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(10)))
        for x, y, f in pts:
            pegar_glow(img, x + 40 * math.sin(t * 0.7 + f), y + 30 * math.sin(t * 0.9 + f), 60, "#ffe7a0",
                       0.5 + 0.4 * math.sin(t * 2 + f))
    return fondo, din


def kit_escritorio(ctx, var):
    modo = ["simbolos", "periodico", "carta"][var % 3]
    if re.search(r"codigo|cifrad|manuscrito|escritura|letras|acertijo|disco|simbol", ctx["txt"]):
        modo = "simbolos" if var != 1 else "periodico"
    if modo == "simbolos" and ctx["tema"] not in ("codigo", "antiguo", "senal"):
        modo = "periodico" if var == 0 else "carta"

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (40, 28, 20)), (1, (18, 12, 8))]))
        rr = random.Random(4)
        for _ in range(30):
            y = rr.randint(0, H)
            L.linea([(0, y), (W, y + rr.randint(-20, 20))], (52, 36, 26), 4)
    fondo = full(dib)
    pegar_glow(fondo, 180, 380, 640, "#ffcf7a", 0.45)
    r = ctx["rnd"]
    hoja = Image.new("RGBA", (760, 980), (238, 226, 196, 255))
    d = ImageDraw.Draw(hoja)
    d.rectangle((0, 0, 759, 979), outline=(140, 120, 90), width=6)
    if modo == "periodico":
        d.text((380, 70), "EL DIARIO", font=maquina(48), fill=(40, 30, 20), anchor="mm")
        d.line((30, 110, 730, 110), fill=(40, 30, 20), width=4)
        tit = ctx["canva"] or ctx["nombre"].upper()
        f = pro.fuente(76)
        while d.textlength(tit, font=f) > 690 and f.size > 36:
            f = pro.fuente(f.size - 6)
        d.text((380, 190), tit, font=f, fill=(150, 20, 20), anchor="mm")
        d.rectangle((40, 260, 400, 600), fill=(200, 190, 170), outline=(60, 50, 40), width=4)
        for k in range(14):
            d.line((430, 270 + k * 24, 720, 270 + k * 24), fill=(150, 140, 120), width=6)
        for k in range(12):
            d.line((40, 640 + k * 26, 720, 640 + k * 26), fill=(150, 140, 120), width=6)
    elif modo == "simbolos":
        glifos = "ΔΣΞΦΨΩΛΠΘ∴ЖЯБДЦ†‡§¶ψλ"
        from PIL import ImageFont
        fg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 50)
        for row in range(11):
            for col in range(9):
                if r.random() < 0.85:
                    d.text((60 + col * 76, 80 + row * 80), r.choice(glifos), font=fg, fill=(60, 40, 30))
    else:
        for k in range(16):
            y = 90 + k * 52
            x = 50
            while x < 700:
                w = r.randint(40, 120)
                d.line([(x + j * w / 8, y + 5 * math.sin(j * 1.7 + k)) for j in range(9)], fill=(40, 50, 90), width=4)
                x += w + 16
    obj_real = ctx["det"].get("obj") if var != 1 else None
    if obj_real:
        o = objeto(obj_real, random.Random(ctx["n"]))
        if o is not None:
            k = min(860 / o.width, 1000 / o.height)
            hoja = o.resize((int(o.width * k), int(o.height * k)), Image.LANCZOS)
            modo = "objeto"
    hoja = hoja.rotate(r.uniform(-6, 6), expand=True, resample=Image.BICUBIC)

    def din(img, t, dur):
        p = ease(t / 0.8)
        y = 1000 + (1 - p) * 700
        sombra_suave(img, (540 - 340, y - 450, 540 + 340, y + 450), radio=10, alfa=140, blur=26)
        img.alpha_composite(hoja, (int(540 - hoja.width / 2), int(y - hoja.height / 2)))
        fl = 1 + 0.1 * math.sin(t * 11)
        pegar_glow(img, 150, 400, 90 * fl, "#ffcf7a", 0.8)
        if modo in ("simbolos", "objeto"):  # lupa recorriendo los símbolos
            lx, ly = 540 + 220 * math.sin(t * 0.7), 1000 + 260 * math.sin(t * 0.5)
            d = ImageDraw.Draw(img)
            d.ellipse((lx - 120, ly - 120, lx + 120, ly + 120), outline=(200, 170, 110), width=14)
            d.line((lx + 85, ly + 85, lx + 200, ly + 200), fill=(90, 60, 40), width=26)
    return fondo, din


def kit_mapa(ctx, var):
    r = ctx["rnd"]

    def dib(L):
        nautica = ctx["n"] % 2 == 0
        L.d.rectangle((0, 0, W * 2, H * 2), fill=(26, 30, 40) if nautica else (40, 30, 22))
        L.forma([(70, 280), (1010, 260), (1030, 1260), (60, 1280)], (196, 214, 222) if nautica else (232, 214, 170),
                intensidad=0.05, textura=0.14)
        if nautica:
            for k in range(1, 6):
                L.linea([(70 + k * 160, 280), (70 + k * 160, 1260)], (150, 170, 186), 2)
                L.linea([(70, 280 + k * 170), (1010, 280 + k * 170)], (150, 170, 186), 2)
        rr = random.Random(ctx["n"])
        costa = [(rr.uniform(150, 450), 380 + i * 110 + rr.uniform(-30, 30)) for i in range(8)]
        L.linea(catmull(costa, 5, cerrado=False), (120, 90, 60), 8)
        for _ in range(16):
            x, y = rr.uniform(500, 950), rr.uniform(380, 1180)
            L.linea([(x, y), (x + 30, y - 10)], (140, 160, 180), 4)
        L.forma(elipse(900, 400, 70, 70), (226, 206, 160), intensidad=0.05)
    fondo = full(dib)
    d = ImageDraw.Draw(fondo)
    d.text((900, 400), "N", font=maquina(50), fill=(120, 80, 50), anchor="mm")
    ruta = catmull([(r.uniform(200, 350), r.uniform(400, 600)), (r.uniform(400, 600), r.uniform(600, 800)),
                    (r.uniform(600, 800), r.uniform(800, 1000)), (r.uniform(700, 900), r.uniform(1000, 1150))], 8,
                   cerrado=False)

    def din(img, t, dur):
        d = ImageDraw.Draw(img)
        n = int(len(ruta) * min(1.0, t / max(dur * 0.7, 0.1)))
        for i in range(0, n, 2):
            x, y = ruta[i]
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(170, 30, 30))
        if n >= len(ruta) - 1:
            x, y = ruta[-1]
            d.line((x - 30, y - 30, x + 30, y + 30), fill=(190, 20, 20), width=12)
            d.line((x + 30, y - 30, x - 30, y + 30), fill=(190, 20, 20), width=12)
        d.text((540, 1210), ctx["nombre"].upper()[:26], font=manuscrita(54), fill=(90, 50, 30), anchor="mm")
    return fondo, din


def kit_cueva(ctx, var):
    def dib(L):
        L.d.rectangle((0, 0, W * 2, H * 2), fill=(26, 20, 18))
        rr = random.Random(11)
        for _ in range(40):
            x, y = rr.randint(-80, W + 80), rr.randint(-80, 1300)
            L.forma(elipse(x, y, rr.randint(90, 200), rr.randint(60, 140), rr.uniform(-1, 1)), (46, 36, 30),
                    intensidad=0.15, textura=0.1, ancho=3)
        L.forma(catmull([(-50, 1400), (W + 50, 1380), (W + 50, H), (-50, H)], 3), (60, 46, 36), borde=False)
        L.forma([(360, 1380), (720, 1380), (700, 1560), (380, 1560)], (110, 70, 34), suave=False, intensidad=0.1)
        L.forma(catmull([(350, 1390), (540, 1290), (730, 1390)], 4, cerrado=False) + [(730, 1390), (350, 1390)],
                (130, 84, 40), intensidad=0.1)
        for k in range(14):
            L.circulo(400 + k * 22, 1370 - (k % 3) * 10, 18, (240, 196, 70), ancho=3)
    fondo = full(dib)

    def din(img, t, dur):
        k = 0.8 + 0.2 * math.sin(t * 7)
        pegar_glow(img, 540, 1360, 380 * k, "#ffc850", 0.55)
        for x in (150, 930):
            fl = 1 + 0.15 * math.sin(t * 13 + x)
            pegar_glow(img, x, 900, 120 * fl, "#ff9a40", 0.8)
            pegar_glow(img, x, 905, 30 * fl, "#ffe9a0", 1)
        for i in range(10):
            f = (t * 0.3 + i / 10) % 1
            pegar_glow(img, 420 + i * 26, 1330 - 200 * f, 8, "#ffe08a", 1 - f)
    return fondo, din


def kit_ruinas(ctx, var):
    txt = ctx["clave"]
    tipo = ctx["det"].get("rui") or ("tumba" if re.search(r"tumba", txt) else "piramide" if re.search(r"piramid|teotihuacan|esfinge|egipto|maya", txt) else
            "esfera" if re.search(r"esfera", txt) else
            "piedras" if re.search(r"stonehenge|piedra|gobekli|pilares", txt) else
            "cabeza" if re.search(r"moai|cabeza|estatua|olmeca", txt) else
            "esfera" if re.search(r"esfera", txt) else "columnas")
    if tipo == "terrazas":
        tipo = "piedras"
    pal = "atardecer" if var != 2 else "noche"

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[pal]))
        pro.montanas(L, 1200, [(150, 700, 260), (850, 700, 300)], (120, 96, 96) if pal != "noche" else (34, 30, 46),
                     nieve=False, borde=False)
        suelo = (190, 150, 104) if pal != "noche" else (60, 52, 50)
        L.forma(catmull([(-50, 1250), (W + 50, 1230), (W + 50, H), (-50, H)], 3), suelo, borde=False, textura=0.14)
        piedra = (176, 150, 120) if pal != "noche" else (90, 84, 90)
        if tipo == "piramide":
            piramide(L, 540, 1260, 900, 620, piedra)
        elif tipo == "escalonada":  # pirámide mesoamericana con escalinata y templo en la cima
            for k in range(6):
                w, y = 860 - k * 120, 1270 - k * 95
                L.forma([(540 - w / 2, y), (540 + w / 2, y), (540 + w / 2 - 30, y - 95), (540 - w / 2 + 30, y - 95)],
                        oscuro(piedra, 1 - k * 0.03), suave=False, intensidad=0.1, textura=0.16)
            L.forma([(490, 1270), (590, 1270), (570, 700), (510, 700)], claro(piedra, 0.1), suave=False)
            for y in range(720, 1270, 22):
                L.linea([(505, y), (575, y)], oscuro(piedra, 0.8), 3)
            L.forma([(460, 700), (620, 700), (610, 590), (470, 590)], oscuro(piedra, 0.9), suave=False)
            L.forma([(515, 700), (565, 700), (565, 630), (515, 630)], (30, 22, 18), suave=False, borde=False)
            if ctx["tema"] in ("selva", "selva_tesoro"):
                rr = random.Random(3)
                for _ in range(10):
                    x = rr.choice((rr.uniform(-60, 220), rr.uniform(860, 1140)))
                    L.forma(elipse(x, rr.uniform(900, 1250), rr.uniform(120, 200), rr.uniform(90, 140)),
                            (40, 90, 54), intensidad=0.1, ancho=3)
        elif tipo == "olmeca":  # cabeza colosal olmeca con casco
            L.forma(catmull([(330, 1280), (310, 900), (380, 700), (540, 650), (700, 700), (770, 900), (750, 1280)], 3),
                    (120, 110, 96), intensidad=0.16, textura=0.2)
            L.forma(catmull([(320, 860), (360, 700), (540, 640), (720, 700), (760, 860), (540, 800)], 3),
                    (104, 96, 84), intensidad=0.12, textura=0.2)
            for x in (440, 640):
                L.forma(elipse(x, 950, 50, 22), (80, 74, 64), intensidad=0.2)
            L.forma(elipse(540, 1050, 60, 45), (110, 100, 88), intensidad=0.2)
            L.forma(elipse(540, 1160, 110, 36), (86, 78, 68), intensidad=0.2)
        elif tipo == "moai":  # moáis sobre su plataforma, mirando tierra adentro con el mar detrás
            L.forma([(-50, 1150), (W + 50, 1150), (W + 50, 1250), (-50, 1250)], (50, 100, 140), suave=False,
                    borde=False)
            L.forma([(60, 1290), (1020, 1290), (1000, 1230), (80, 1230)], (110, 100, 96), suave=False,
                    intensidad=0.1, textura=0.2)
            for k, x in enumerate((220, 430, 640, 850)):
                hh = 560 - (k % 2) * 60
                L.forma([(x - 75, 1230), (x - 85, 1230 - hh * 0.55), (x - 65, 1230 - hh), (x + 65, 1230 - hh),
                         (x + 85, 1230 - hh * 0.55), (x + 75, 1230)], (96, 86, 80), suave=False, intensidad=0.16,
                        textura=0.22)
                L.forma([(x - 70, 1230 - hh + 40), (x + 70, 1230 - hh + 40), (x + 66, 1230 - hh + 100),
                         (x - 66, 1230 - hh + 100)], (70, 62, 58), suave=False, borde=False)
                L.forma([(x - 14, 1230 - hh + 100), (x + 14, 1230 - hh + 100), (x + 22, 1230 - hh * 0.62),
                         (x - 22, 1230 - hh * 0.62)], (110, 100, 92), suave=False)
        elif tipo == "tpilares":  # Göbekli Tepe: pilares en T con relieves de animales
            for k in range(5):
                x = 140 + k * 200
                L.forma([(x - 34, 1290), (x - 34, 900), (x + 34, 900), (x + 34, 1290)], piedra, suave=False,
                        intensidad=0.14, textura=0.18)
                L.forma([(x - 90, 900), (x + 90, 900), (x + 90, 820), (x - 90, 820)], piedra, suave=False,
                        intensidad=0.14, textura=0.18)
                L.linea(catmull([(x - 20, 1100), (x, 1060), (x + 20, 1100), (x, 1140)], 4), oscuro(piedra, 0.6), 4)
        elif tipo == "estepa":  # estepa de Mongolia con yurtas
            L.forma(catmull([(-50, 1250), (W + 50, 1230), (W + 50, H), (-50, H)], 3), (120, 140, 70), borde=False,
                    textura=0.18)
            for x, s_ in ((260, 1.0), (720, 0.7)):
                L.forma([(x - 150 * s_, 1300), (x - 150 * s_, 1200), (x + 150 * s_, 1200), (x + 150 * s_, 1300)],
                        (236, 230, 214), suave=False, intensidad=0.1)
                L.forma([(x - 170 * s_, 1200), (x, 1110 - 20 * s_), (x + 170 * s_, 1200)], (210, 200, 180),
                        suave=False, intensidad=0.1)
                L.forma([(x - 30 * s_, 1300), (x + 30 * s_, 1300), (x + 30 * s_, 1220), (x - 30 * s_, 1220)],
                        (160, 50, 40), suave=False)
        elif tipo == "nazca":  # vista aérea del desierto con el colibrí
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(200, 160, 120))
            for _ in range(60):
                xx, yy = random.uniform(0, W), random.uniform(0, H)
                L.circulo(xx, yy, random.uniform(3, 8), (176, 136, 100), borde=False)
            cuerpo = [(540, 420), (560, 600), (600, 900), (590, 1200), (540, 1500), (490, 1200), (480, 900),
                      (520, 600)]
            L.linea(catmull(cuerpo, 6), (240, 220, 190), 10)
            L.linea([(540, 420), (540, 200)], (240, 220, 190), 10)  # pico
            for lado in (-1, 1):
                ala = [(540 + lado * 40, 820)] + [(540 + lado * (120 + k * 70), 820 - k * 80 + (k % 2) * 60)
                                                  for k in range(6)] + [(540 + lado * 60, 1000)]
                L.linea(ala, (240, 220, 190), 10)
            for k in range(5):
                L.linea([(480 + k * 30, 1500), (420 + k * 50, 1760)], (240, 220, 190), 8)
        elif tipo == "torre":  # Torre de Londres
            L.forma([(330, 1290), (330, 640), (750, 640), (750, 1290)], (196, 184, 160), suave=False,
                    intensidad=0.1, textura=0.18)
            for x in (300, 700):
                L.forma([(x, 640), (x + 80, 640), (x + 80, 460), (x, 460)], (196, 184, 160), suave=False,
                        intensidad=0.12, textura=0.16)
                L.forma([(x - 6, 470), (x + 40, 400), (x + 86, 470)], (60, 70, 80), suave=False)
            for k in range(8):
                L.forma([(330 + k * 54, 640), (360 + k * 54, 640), (360 + k * 54, 600), (330 + k * 54, 600)],
                        (196, 184, 160), suave=False)
            for x, y in ((420, 800), (600, 800), (420, 1000), (600, 1000)):
                L.forma([(x, y), (x + 40, y), (x + 40, y + 90), (x, y + 90)], (30, 26, 24), suave=False, borde=False)
        elif tipo == "piedras":
            for k in range(5):
                x = 160 + k * 190
                L.forma([(x - 50, 1280), (x - 40, 900 - (k % 2) * 60), (x + 40, 900 - (k % 2) * 60), (x + 50, 1280)],
                        piedra, suave=False, intensidad=0.12, textura=0.12)
            L.forma([(120, 900), (620, 880), (620, 840), (120, 860)], piedra, suave=False, intensidad=0.12)
        elif tipo == "cabeza":
            L.forma(catmull([(380, 1280), (360, 760), (440, 640), (640, 640), (720, 760), (700, 1280)], 3), piedra,
                    intensidad=0.14, textura=0.15)
            L.forma([(430, 840), (520, 840), (520, 870), (430, 870)], oscuro(piedra, 0.6), suave=False, borde=False)
            L.forma([(570, 840), (660, 840), (660, 870), (570, 870)], oscuro(piedra, 0.6), suave=False, borde=False)
            L.forma([(520, 900), (570, 900), (580, 1010), (510, 1010)], oscuro(piedra, 0.85), suave=False)
        elif tipo == "esfera":
            for x, rr_ in ((330, 160), (720, 220)):
                L.forma(elipse(x, 1280 - rr_, rr_, rr_), piedra, intensidad=0.2, textura=0.12)
        elif tipo == "tumba":
            L.forma(catmull([(-80, 1300), (200, 900), (540, 820), (880, 900), (W + 80, 1300)], 4), oscuro(suelo, 0.85),
                    intensidad=0.1, textura=0.14)
            L.forma([(380, 1290), (380, 1000), (700, 1000), (700, 1290)], piedra, suave=False, intensidad=0.12,
                    textura=0.15)
            L.forma([(430, 1290), (430, 1060), (650, 1060), (650, 1290)], (18, 14, 12), suave=False, borde=False)
            L.forma([(350, 1000), (730, 1000), (700, 950), (380, 950)], claro(piedra, 0.1), suave=False)
        else:  # columnas clásicas rotas
            rr = random.Random(ctx["n"])
            for k in range(5):
                x = 150 + k * 195
                h = rr.choice((620, 520, 380, 260))
                L.forma([(x - 70, 1290), (x + 70, 1290), (x + 60, 1250), (x - 60, 1250)], claro(piedra, 0.1),
                        suave=False)
                L.forma([(x - 48, 1250), (x - 44, 1290 - h), (x + 44, 1290 - h + rr.randint(0, 40)), (x + 48, 1250)],
                        piedra, suave=False, intensidad=0.16, textura=0.14)
                for f in (-24, 0, 24):
                    L.linea([(x + f, 1245), (x + f * 0.95, 1300 - h)], oscuro(piedra, 0.78), 4)
                if h > 500:
                    L.forma([(x - 75, 1290 - h), (x + 75, 1290 - h), (x + 60, 1250 - h), (x - 60, 1250 - h)],
                            claro(piedra, 0.08), suave=False)
            for _ in range(7):
                x = rr.uniform(80, 1000)
                L.forma(elipse(x, 1330 + rr.uniform(0, 120), rr.uniform(30, 70), rr.uniform(20, 36)), piedra,
                        intensidad=0.2, textura=0.1)
    fondo = full(dib)
    if pal != "noche":
        pegar_glow(fondo, 820, 700, 420, "#ffd9a0", 0.35)

    def din(img, t, dur):
        if pal == "noche":
            for x in (220, 860):
                fl = 1 + 0.15 * math.sin(t * 12 + x)
                pegar_glow(img, x, 1150, 110 * fl, "#ff9a40", 0.75)
        else:
            particulas(img, t, "ceniza", 30, alfa=120)
        niebla(img, t, 1250, 0.18)
    return fondo, din


def kit_calle(ctx, var):
    det = ctx["det"]
    epoca = det.get("epoca", 1950)
    pal = "niebla" if var == 0 else ("frio" if det.get("nieve") else "noche")
    victoriana = epoca < 1915

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[pal]))
        col = (60, 58, 64) if pal == "noche" else (110, 108, 112)
        ladrillo = (104, 62, 50) if victoriana else col
        for lado in (0, 1):
            x0 = 0 if lado == 0 else W - 330
            L.forma([(x0, 1500), (x0, 300), (x0 + 330, 420 if lado == 0 else 300), (x0 + 330, 1500)],
                    oscuro(ladrillo, 0.8) if pal == "noche" else ladrillo, suave=False, intensidad=0.08, textura=0.16)
            if victoriana:
                for y in range(320, 1500, 40):
                    L.linea([(x0, y), (x0 + 330, y)], oscuro(ladrillo, 0.75), 2)
            for k in range(6):
                y = 460 + k * 160
                L.forma([(x0 + 80, y), (x0 + 160, y), (x0 + 160, y + 100), (x0 + 80, y + 100)],
                        (230, 190, 110) if (k + lado) % 3 == 0 else (50, 50, 56), suave=False, borde=False)
        suelo = (226, 230, 238) if pal == "frio" else (52, 50, 56)
        L.forma([(0, 1500), (W, 1500), (W, H), (0, H)], suelo, suave=False, borde=False, textura=0.16)
        if victoriana:  # adoquines
            for y in range(1520, H, 40):
                for x in range(0, W, 70):
                    L.forma(elipse(x + (y // 40 % 2) * 35, y, 30, 14), oscuro(suelo, 0.85) if pal != "frio" else
                            (200, 206, 216), borde=False, sombra=False, brillo=False, textura=0)
        else:
            L.forma([(300, 1500), (780, 1500), (1000, H), (80, H)], oscuro(suelo, 0.9) if pal == "frio" else
                    (66, 64, 70), suave=False, borde=False, textura=0.1)
    fondo = full(dib)
    r = ctx["rnd"]
    lx = r.choice((360, 720))
    coche = R.auto("1920" if epoca < 1950 else "1975", (36, 44, 56) if epoca < 1950 else (110, 34, 30)) \
        if det.get("auto") else None

    def din(img, t, dur):
        d = ImageDraw.Draw(img)
        if victoriana:  # farol de gas
            d.line((lx, 1500, lx, 860), fill=(30, 30, 34), width=12)
            d.polygon([(lx - 34, 860), (lx + 34, 860), (lx + 24, 790), (lx - 24, 790)], fill=(60, 56, 40))
            pegar_glow(img, lx, 825, 170, "#ffb860", 0.85)
        else:
            d.line((lx, 1500, lx, 820), fill=(30, 30, 34), width=14)
            pegar_glow(img, lx, 820, 150, "#fff0c0", 0.8)
        if coche is not None:
            img.alpha_composite(coche, (int(700 - coche.width / 2), int(1640 - coche.height * 0.83)))
        per = personas_de(ctx)
        if per:
            for k, pk in enumerate(per):
                s = max(0.42, 0.62 - t * 0.012)
                figura(img, pk, 470 + k * 170 + 6 * math.sin(t), 1620 - t * 8, s, t, pose="caminar",
                       espejo=(ctx["n"] + k) % 2 == 1, oscuridad=0.45 if pal == "noche" else 0.15)
        else:
            x = 540 + 8 * math.sin(t)
            s = max(0.35, 0.8 - t * 0.04)
            silueta(d, x, 1500 - (0.8 - s) * 300, s, t * 0.6, agachado=False, col=(14, 14, 18))
        niebla(img, t, 1350, 0.55 if pal == "niebla" else 0.35, n=10)
        if pal == "noche":
            particulas(img, t, "lluvia", 70, viento=-120, alfa=150)
        elif pal == "frio":
            particulas(img, t, "nieve", 80, viento=-120, alfa=220)
    return fondo, din


def kit_cartel(ctx, var):
    fondo = full(lambda L: (L.d.rectangle((0, 0, W * 2, H * 2), fill=(70, 66, 62)),
                            [L.linea([(0, y), (W, y)], (60, 56, 52), 3) for y in range(0, H, 90)]))
    hoja = Image.new("RGBA", (680, 920), (240, 232, 210, 255))
    d = ImageDraw.Draw(hoja)
    d.rectangle((0, 0, 679, 919), outline=(120, 100, 70), width=6)
    cab = "SE BUSCA" if re.search(r"asesin|criminal|zodiaco|destripador|hacke", ctx["txt"]) else "DESAPARECIDO"
    d.text((340, 90), cab, font=maquina(70), fill=(150, 20, 20), anchor="mm")
    d.rectangle((140, 170, 540, 620), fill=(200, 196, 186), outline=(60, 50, 40), width=5)
    d.ellipse((260, 230, 420, 400), fill=(60, 56, 54))
    d.rounded_rectangle((210, 390, 470, 620), radius=60, fill=(60, 56, 54))
    d.text((340, 700), ctx["nombre"].upper()[:22], font=maquina(40), fill=TINTA, anchor="mm")
    if ctx["anio"]:
        d.text((340, 790), f"VISTO POR ÚLTIMA VEZ: {ctx['anio']}", font=maquina(28), fill=(80, 60, 40), anchor="mm")
    hoja = hoja.rotate(ctx["rnd"].uniform(-4, 4), expand=True, resample=Image.BICUBIC)

    def din(img, t, dur):
        p = max(0.08, pop(t / 0.5))
        h = hoja.resize((max(1, int(hoja.width * p)), max(1, int(hoja.height * p))))
        sombra_suave(img, (540 - h.width / 2 + 10, 900 - h.height / 2 + 10, 540 + h.width / 2 - 10,
                           900 + h.height / 2 - 10), radio=6, alfa=140)
        img.alpha_composite(h, (int(540 - h.width / 2), int(900 - h.height / 2)))
        particulas(img, t, "lluvia", 40, viento=-60, alfa=120)
    return fondo, din


def kit_nieve(ctx, var):
    from andes import fondo_cordillera
    det = ctx["det"]
    fondo = fondo_cordillera("noche" if var != 1 else "dia")
    carpa = R.carpa_rota() if det.get("carpa") else None

    def din(img, t, dur):
        if carpa is not None:
            img.alpha_composite(carpa, (540 - carpa.width // 2, 1560 - carpa.height))
            d = ImageDraw.Draw(img)
            for k in range(9):  # huellas que se alejan de la carpa, ladera abajo
                d.ellipse((560 + k * 50 - 12, 1600 + k * 30 - 6, 560 + k * 50 + 12, 1600 + k * 30 + 6),
                          fill=(150, 160, 190))
        for k, pk in enumerate(personas_de(ctx)):
            figura(img, pk, 420 + k * 220 + t * 6, 1640 - k * 40, 0.5, t, pose="caminar", espejo=True,
                   oscuridad=0.3 if var != 1 else 0.0, vel=0.5)
        particulas(img, t, "nieve", 110, viento=-260, vel=1.5)
        if var == 2 or det.get("huellas"):
            d = ImageDraw.Draw(img)
            for k in range(12):
                x, y = 200 + k * 60, 1700 - k * 30
                if det.get("huellas"):  # huellas de pezuña (Devon, 1855)
                    d.ellipse((x - 14, y - 10, x + 14, y + 10), fill=(120, 130, 160))
                    d.line((x, y - 10, x, y + 10), fill=(226, 232, 240), width=3)
                else:
                    d.ellipse((x - 12, y - 6, x + 12, y + 6), fill=(150, 160, 190))
    return fondo, din


def kit_selva(ctx, var):
    from juliane import fondo_selva
    fondo = fondo_selva(oscura=var != 1, rio=var == 2, semilla=ctx["n"] + var)

    def din(img, t, dur):
        for k, pk in enumerate(personas_de(ctx)):
            if var != 2:
                figura(img, pk, 380 + k * 200 + t * 10, 1700, 0.55, t, pose="caminar", oscuridad=0.3)
        niebla(img, t, 1200, 0.35)
        for i in range(10):
            bx = 300 + 400 * math.sin(t * 2 + i * 1.7)
            by = 1000 + 200 * math.sin(t * 2.6 + i)
            pegar_glow(img, bx, by, 8, "#d0ff90", 0.5)
    return fondo, din


def kit_lago(ctx, var):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS["frio" if var != 2 else "noche"]))
        pro.montanas(L, 1150, [(200, 800, 340), (850, 700, 300)], (60, 70, 70), nieve=False, borde=False)
        pinos(L, 1160, 18, 220, (30, 44, 40), random.Random(2))
        mar(L, 1150, (40, 56, 66))
    fondo = full(dib)
    cuello = bool(re.search(r"ness|monstruo", ctx["txt"]))
    det = ctx["det"]
    coche = R.auto("1920", (36, 44, 56)) if det.get("auto") else None

    def din(img, t, dur):
        d = ImageDraw.Draw(img)
        if coche is not None:
            img.alpha_composite(coche, (300 - coche.width // 2, int(1300 - coche.height * 0.83)))
            pegar_glow(img, 300 + coche.width * 0.4, 1255, 120, "#fff0b0", 0.7)
        elif det.get("balsa"):  # balsa de oro en la laguna de Guatavita
            x = 540 + 30 * math.sin(t * 0.4)
            d.polygon([(x - 200, 1230), (x + 200, 1230), (x + 170, 1270), (x - 170, 1270)], fill=(150, 110, 40))
            pegar_glow(img, x, 1150, 220, "#ffd050", 0.7 + 0.2 * math.sin(t * 3))
            d.rounded_rectangle((x - 30, 1080, x + 30, 1230), radius=26, fill=(240, 190, 60))
            d.ellipse((x - 26, 1030, x + 26, 1086), fill=(240, 190, 60))
            for k in range(8):
                f = (t * 0.5 + k / 8) % 1
                pegar_glow(img, x - 100 + k * 28, 1240 + 90 * f, 8, "#ffe080", 1 - f)
        elif cuello:
            x = 600 + 20 * math.sin(t * 0.5)
            pts = [(x - 120, 1250), (x - 60, 1000), (x - 10, 880), (x + 40, 860), (x + 60, 900), (x + 10, 920),
                   (x - 10, 1020), (x + 40, 1250)]
            d.polygon(pts, fill=(20, 26, 30))
            d.ellipse((x - 220, 1220, x - 80, 1270), fill=(20, 26, 30))
        else:
            ojo_brillo(img, 300 + 30 * math.sin(t * 0.4), 1080, t)
        olas(img, t, 1160, col=(140, 160, 170), alfa=90)
        niebla(img, t, 1150, 0.5, n=10)
    return fondo, din


def kit_bosque(ctx, var):
    pal = ["noche", "frio", "atardecer"][var % 3]

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[pal]))
        rr = random.Random(ctx["n"] + 31)
        for capa, (col, alto) in enumerate((((40, 50, 60), 520), ((28, 36, 42), 680), ((16, 20, 24), 880))):
            if pal == "atardecer":
                col = oscuro((80, 46, 40), 0.9 - capa * 0.2)
            pinos(L, 1300 + capa * 150, 14 - capa * 3, alto, col, rr)
        L.forma([(0, 1560), (W, 1540), (W, H), (0, H)], (20, 24, 26), suave=False, borde=False, textura=0.12)
        if pal == "atardecer":  # árboles caídos (Tunguska)
            for k in range(9):
                x = 80 + k * 115
                L.linea([(x, 1700), (x + 160, 1640 + (k % 3) * 20)], (40, 28, 22), 16)
    fondo = full(dib)
    if pal == "noche":
        pegar_glow(fondo, 820, 360, 120, "#e8f0ff", 0.7)

    def din(img, t, dur):
        from alcatraz import linterna
        if pal != "frio" and pal != "atardecer":
            for k, pk in enumerate(personas_de(ctx)):  # la persona real entre los árboles
                figura(img, pk, 600 + k * 150, 1650 - t * 8, max(0.36, 0.55 - t * 0.01), t, pose="caminar",
                       espejo=True, oscuridad=0.3, vel=0.6)
        niebla(img, t, 1450, 0.5, n=10)
        if pal == "noche":
            linterna(img, 120, 1900, 540 + 300 * math.sin(t * 0.8), 1300 + 120 * math.sin(t * 1.3), ancho=230,
                     oscuridad=170)
        elif pal == "atardecer":
            k = max(0.0, 1 - abs(t - dur * 0.3) / 0.6)
            pegar_glow(img, 700, 900, 300 + 500 * k, "#ffb060", 0.4 + 0.6 * k)
            particulas(img, t, "ceniza", 50, alfa=170)
        else:
            per = personas_de(ctx)
            if per:  # la persona real se aleja por el sendero (p. ej. Paula Welden con su parka roja)
                for k, pk in enumerate(per):
                    figura(img, pk, 520 + k * 160, 1640 - t * 10, max(0.32, 0.55 - t * 0.012), t, pose="caminar",
                           espejo=True, oscuridad=0.35, vel=0.6)
            else:
                d = ImageDraw.Draw(img)
                silueta(d, 540, 1560 - t * 6, max(0.3, 0.7 - t * 0.03), t * 0.6, agachado=False, col=(10, 12, 16))
            particulas(img, t, "nieve", 50, viento=-80, alfa=200)
    return fondo, din


_ESTATICA = [Image.fromarray(__import__("numpy").random.default_rng(i).integers(20, 235, (120, 160), dtype="uint8"),
                             "L").resize((640, 480), Image.NEAREST).convert("RGBA") for i in range(6)]


def kit_pantalla(ctx, var):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (14, 14, 20)), (1, (6, 6, 10))]))
        L.forma([(150, 1450), (930, 1450), (980, H), (100, H)], (60, 44, 34), suave=False, intensidad=0.06)
        L.forma([(170, 560), (910, 560), (910, 1330), (170, 1330)], (46, 44, 48), suave=False, intensidad=0.08)
        L.forma([(420, 1330), (660, 1330), (700, 1450), (380, 1450)], (36, 34, 38), suave=False)
    fondo = full(dib)
    texto = ctx["canva"].strip("¿?«»").upper()[:16] or ctx["nombre"].upper()[:16]

    def din(img, t, dur):
        k = int(t * 15) % 6
        pantalla = _ESTATICA[k].copy()
        d = ImageDraw.Draw(pantalla)
        obj = ctx["det"].get("obj")
        if obj == "max" and var == 0:  # transmisión pirata: fondo de franjas que giran y figura enmascarada
            for k in range(-8, 16):
                x = k * 50 + (t * 120) % 100
                d.polygon([(x, 0), (x + 25, 0), (x - 95, 480), (x - 120, 480)], fill=(70, 70, 90, 255))
            d.ellipse((240, 110, 400, 300), fill=(220, 210, 200))
            d.rectangle((300 - 70 + 20, 300, 380 + 20, 480), fill=(30, 30, 34))
            d.rectangle((262, 170, 380, 200), fill=(20, 20, 24))
        elif obj == "cigarra" and var == 0:  # imagen con la cigarra
            d.rectangle((0, 0, 640, 480), fill=(10, 10, 12, 255))
            d.ellipse((290, 120, 350, 380), fill=(200, 200, 200))
            for lado in (-1, 1):
                d.polygon([(320, 170), (320 + lado * 200, 140), (320 + lado * 220, 300), (320, 260)],
                          fill=(150, 150, 150))
            d.text((320, 430), "3301", font=maquina(40), fill=(220, 220, 220), anchor="mm")
        elif var == 1 or (var == 0 and int(t * 3) % 5 == 0):
            d.rectangle((0, 0, 640, 480), fill=(14, 30, 16, 255))
            vis = texto[:max(1, int(t * 8))]
            d.text((30, 200), "> " + vis + ("_" if int(t * 3) % 2 else ""), font=maquina(44), fill=(90, 255, 120))
        y = int((t * 160) % 480)
        d.rectangle((0, y, 640, y + 30), fill=(255, 255, 255, 40))
        img.alpha_composite(pantalla, (220, 610))
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(capa).rounded_rectangle((200, 590, 880, 1110), radius=60, outline=(20, 20, 24, 255),
                                                width=40)
        img.alpha_composite(capa)
        pegar_glow(img, 540, 850, 520, "#a0c0ff" if var != 1 else "#80ff9a", 0.25 + 0.1 * math.sin(t * 20))
    return fondo, din


KITS = {"mar": kit_mar, "avion": kit_avion, "radar": kit_radar, "faro": kit_faro, "espacio": kit_espacio,
        "luces": kit_luces, "escritorio": kit_escritorio, "mapa": kit_mapa, "cueva": kit_cueva, "ruinas": kit_ruinas,
        "calle": kit_calle, "cartel": kit_cartel, "nieve": kit_nieve, "selva": kit_selva, "lago": kit_lago, "bosque": kit_bosque, "radio": kit_radio,
        "pantalla": kit_pantalla}
KITS.update(KITS_EXTRA)


def sonidos_kit(kit, var, dur, ctx):
    """Efectos propios de cada escenario (además de la voz, que siempre va por encima)."""
    det = ctx["det"]
    hora = det.get("hora", "")
    ev = []
    if kit == "mar":
        ev += [(0, "olas", dur), (0.3, "crujido", 1.6), (dur * 0.55, "crujido", 1.2)]
        if hora == "dia" and var == 0:
            ev.append((0.5, "gaviotas", 2.0))
        if hora == "niebla" or var == 1:
            ev.append((0.8, "sirena_niebla", 2.5))
    elif kit == "avion":
        modelo = det.get("av", "")
        ev += [(0, "jet" if modelo in ("777", "f18") else ("viento" if modelo == "globo" else "helice"), dur),
               (dur * 0.45, "whoosh", 0.9)]
    elif kit == "radar":
        ev += [(k * 1.4 + 0.2, "ping", 1.0) for k in range(int(dur / 1.4))]
    elif kit == "radio":
        ev += [(0, "estatica", dur), (0.3, "morse", max(0.5, dur - 0.5))]
    elif kit == "faro":
        ev += [(0, "viento", dur), (0, "olas", dur), (0.6, "sirena_niebla", 2.5)]
    elif kit == "espacio":
        ev += [(0, "drone", dur), (0.5, "ping", 1.0), (2.2, "ping", 1.0)]
    elif kit == "luces":
        ev += [(0, "zumbido", dur)]
    elif kit == "escritorio":
        ev += [(0.05, "papel", 0.5), (0.8, "reloj", max(0.5, dur - 0.8))]
    elif kit == "mapa":
        ev += [(0.05, "papel", 0.5), (0.6, "raspado", min(2.0, max(0.5, dur - 0.6)))]
    elif kit == "cueva":
        ev += [(0, "goteo", dur), (0, "drone", dur)]
    elif kit == "ruinas":
        ev += [(0, "viento", dur), (0, "drone", dur)]
    elif kit == "calle":
        ev += [(0.2, "pasos", max(0.5, dur - 0.3))] + ([(0, "lluvia", dur)] if var else [])
    elif kit == "cartel":
        ev += [(0.0, "papel", 0.5), (0, "lluvia", dur)]
    elif kit == "nieve":
        ev += [(0, "viento", dur)]
    elif kit == "selva":
        ev += [(0, "insectos", dur), (0, "rio", dur)]
    elif kit == "lago":
        ev += [(0, "olas", dur), (0.8, "buho", 1.2)]
    elif kit == "bosque":
        ev += [(0, "viento", dur), (0.6, "buho", 1.2), (dur * 0.6, "crujido", 0.8)]
        if var % 3 == 2:
            ev.append((max(0.0, dur * 0.3 - 0.2), "explosion_lejana", 3.0))
    elif kit == "pantalla":
        ev += [(0, "estatica", dur)]
    elif kit == "desierto":
        ev += [(0, "viento", dur), (0, "drone", dur)]
    elif kit == "submarino":
        ev += [(0, "burbujas", dur), (0, "drone", dur)]
    elif kit == "playa":
        ev += [(0, "olas", dur), (0.4, "gaviotas", 2.0)]
    elif kit == "tren":
        ev += [(0, "tren", dur)]
    elif kit == "casa":
        ev += [(0, "fuego", dur)] if var == 1 else [(0, "viento", dur), (0.5, "crujido", 1.0)]
    elif kit == "palacio":
        ev += [(0, "drone", dur), (0.3, "campana", 3.0)]
    return ev

SECUENCIAS = {  # el primero (o el tercero) abre el video; el resto se reparte distinto en cada misterio
    "mar": [("mar", 0), ("mapa", 0), ("mar", 1), ("escritorio", 2), ("radio", 0), ("mar", 2)],
    "aire": [("avion", 0), ("radar", 0), ("radio", 1), ("avion", 1), ("mapa", 0), ("escritorio", 1)],
    "faro": [("faro", 0), ("mar", 0), ("escritorio", 2), ("faro", 2), ("mapa", 0)],
    "espacio": [("espacio", 0), ("escritorio", 0), ("radio", 0), ("radar", 0), ("espacio", 1)],
    "ovni": [("luces", 0), ("radar", 0), ("luces", 1), ("escritorio", 1), ("radio", 1)],
    "codigo": [("escritorio", 0), ("mapa", 0), ("escritorio", 1), ("ruinas", 1), ("escritorio", 2)],
    "tesoro": [("cueva", 0), ("mapa", 0), ("cueva", 1), ("escritorio", 1), ("bosque", 1), ("calle", 1)],
    "antiguo": [("ruinas", 0), ("escritorio", 0), ("ruinas", 2), ("mapa", 0), ("ruinas", 1), ("escritorio", 1)],
    "crimen": [("calle", 0), ("escritorio", 1), ("cartel", 0), ("calle", 1), ("escritorio", 0)],
    "hielo": [("nieve", 0), ("mapa", 0), ("nieve", 1), ("escritorio", 2), ("nieve", 2), ("radio", 1)],
    "selva": [("selva", 0), ("mapa", 0), ("selva", 2), ("ruinas", 2), ("selva", 1)],
    "criatura": [("lago", 0), ("escritorio", 1), ("lago", 2), ("bosque", 0), ("selva", 0)],
    "fenomeno": [("luces", 0), ("escritorio", 1), ("luces", 1), ("mapa", 0), ("bosque", 1), ("radio", 0)],
    "persona": [("calle", 0), ("cartel", 0), ("calle", 1), ("mapa", 0), ("escritorio", 1), ("escritorio", 2)],
    "bosque": [("bosque", 0), ("cartel", 0), ("bosque", 1), ("mapa", 0), ("escritorio", 2)],
    "senal": [("pantalla", 0), ("escritorio", 1), ("pantalla", 1), ("escritorio", 0), ("radio", 0)],
    "cartografia": [("mapa", 0), ("escritorio", 2), ("mar", 1), ("mar", 2), ("radar", 0)],
    "oceano": [("mar", 2), ("radar", 0), ("radio", 0), ("mar", 1), ("escritorio", 1)],
    "joya": [("escritorio", 1), ("cueva", 0), ("calle", 1), ("cueva", 1), ("palacio", 0)],
    "explosion": [("bosque", 2), ("escritorio", 1), ("mapa", 0), ("luces", 0), ("radio", 0)],
    "selva_persona": [("selva", 0), ("mapa", 0), ("selva", 2), ("cartel", 0), ("selva", 1)],
    "selva_tesoro": [("selva", 0), ("mapa", 0), ("cueva", 0), ("selva", 2), ("escritorio", 1)],
}

# tinte propio de cada misterio (sutil) para que dos videos del mismo tema no se vean iguales
TINTES = [(0, 40, 60), (70, 30, 0), (40, 0, 60), (0, 50, 20), (60, 0, 10), (0, 0, 0), (20, 30, 70)]


def completar(abre, tema, n):
    """Escena de apertura fija + 3 escenas distintas del grupo del tema (sin repetir escenario)."""
    r = random.Random(n * 7)
    resto = [(k, (v + n) % 3 if k not in ("mapa", "cartel", "radar") else v) for k, v in SECUENCIAS[tema]
             if k != abre[0]]
    r.shuffle(resto)
    vistos, sec = {abre[0]}, [abre]
    for k in resto:
        if k[0] not in vistos and len(sec) < 4:
            sec.append(k)
            vistos.add(k[0])
    for k in (("mapa", 0), ("escritorio", 2), ("escritorio", 1), ("escritorio", 0)):
        if len(sec) < 4 and k not in sec and (k[0] not in vistos or k[0] == "escritorio"):
            sec.append(k)
            vistos.add(k[0])
    return sec


def secuencia_de(tema, n):
    pool = SECUENCIAS[tema]
    r = random.Random(n * 104729)
    alterno = pool[min(2, len(pool) - 1)]
    debil = alterno[0] in ("mapa", "escritorio", "cartel", "radar", "radio") or tema in ("cartografia", "faro")
    primero = pool[0] if n % 2 == 0 or debil else alterno
    resto = [k for k in pool if k != primero]
    r.shuffle(resto)
    sec = [primero] + resto[:3]
    return [(k, (v + n) % 3 if k not in ("mapa", "cartel", "radar") else v) for k, v in sec]


TEMA_N = {}
for _tema, _nums in {
        "mar": [1, 15, 16, 17, 19, 20, 28, 29, 48, 60, 87, 88, 90], "aire": [2, 3, 4, 14, 18, 26, 27],
        "faro": [5], "bosque": [6, 13, 38], "hielo": [7, 22, 23, 42, 79, 98], "espacio": [8],
        "codigo": [9, 12, 56, 57, 58, 59, 63, 64, 65, 66], "crimen": [10, 11, 39],
        "ovni": [21, 82, 83, 84], "selva": [24, 49, 93], "selva_persona": [31, 91],
        "persona": [25, 30, 32, 33, 34, 35, 36, 37, 89], "senal": [40, 41],
        "antiguo": [43, 44, 45, 46, 47, 50, 51, 52, 53, 54, 55, 62, 92, 96, 97, 100],
        "cartografia": [61, 99], "tesoro": [67, 68, 72, 73, 74], "selva_tesoro": [69, 70, 71],
        "explosion": [75], "fenomeno": [76, 77, 78, 81], "criatura": [80, 85, 86], "oceano": [95], "joya": [94]}.items():
    for _n in _nums:
        TEMA_N[_n] = _tema

TEMAS = [
    ("faro", r"\bfaro\b|fareros"),
    ("espacio", r"senal wow|radiotelescopio|senal del espacio"),
    ("ovni", r"ovni|disco volador|tic tac|nimitz|roswell|phoenix|valentich"),
    ("aire", r"avion|vuelo |aviador|piloto|avioneta|globo|stendec|aeropuerto"),
    ("hielo", r"artico|hielo|glaciar|everest|diatlov|urales|polo norte|franklin"),
    ("mar", r"barco|buque|velero|goleta|catamaran|transatlantico|naufragio|marina|navegando|isla sandy|bloop"),
    ("codigo", r"codigo|cifrad|manuscrito|escritura|acertijo|inscripcion|disco de festo|lineal a|cicada|dorabella|"
               r"rongorongo|max headroom|tamam"),
    ("tesoro", r"tesoro|\boro\b|mina|diamante|ambar|el dorado|paititi|llanganates"),
    ("selva", r"selva|amazon|fawcett|jungla|honduras|nueva guinea"),
    ("criatura", r"monstruo|chupacabras|criatura|ninos verdes|huellas del diablo|ness"),
    ("antiguo", r"templo|piramide|tumba|estatua|piedras|civilizacion|ruinas|moais|esferas|cabezas|lineas de nazca|"
                r"biblioteca|atlantida|esfinge|stonehenge|teotihuacan|mayas|mecanismo|pueblos del mar|yonaguni|"
                r"piri reis|sabana santa|rollo de cobre|otzi"),
    ("fenomeno", r"explosion|zumbido|lluvia de carne|luces|sonido"),
    ("crimen", r"asesin|criminal|destripador|hackeo|zodiaco|mascaras de plomo"),
]

SONIDO = {"bosque": ["viento", "insectos"], "senal": ["estatica"], "cartografia": ["olas"], "oceano": ["olas"],
          "joya": ["reloj"], "selva_persona": ["insectos", "rio"], "explosion": ["viento"], "selva_tesoro": ["insectos", "rio"], "mar": ["olas", "viento"], "aire": ["motor", "viento"], "faro": ["olas", "viento"], "espacio": ["estatica"],
          "ovni": ["viento", "estatica"], "codigo": ["reloj"], "tesoro": ["viento"], "antiguo": ["viento"],
          "crimen": ["lluvia"], "hielo": ["viento"], "selva": ["insectos", "rio"], "criatura": ["viento", "rio"],
          "fenomeno": ["viento"], "persona": ["lluvia"]}


def tema_de(txt):
    for tema, rx in TEMAS:
        if re.search(rx, txt):
            return tema
    return "persona"


# =========================================================================== #
# ESCENAS
# =========================================================================== #
def sello_de(parrafo):
    p = norm(parrafo)
    if re.search(r"falso|fraude|broma|era un juguete|no existia", p):
        return "MITO", (200, 120, 30)
    if re.search(r"respuesta|explicacion|concluyo|resulto", p):
        return "¿RESUELTO?", (40, 130, 70)
    if re.search(r"nunca|nadie|sin explicacion|sigue|misterio", p):
        return "SIN RESOLVER", (200, 30, 40)
    return "CASO ABIERTO", (200, 30, 40)


def crear_escenas(g):
    txt = norm(" ".join([g["nombre"], g["escena"], g["desc"]] + g["parrafos"]))
    tema = TEMA_N.get(g["n"]) or tema_de(txt)
    rnd = random.Random(g["n"] * 7919)
    anio = (re.findall(r"\b(1[0-9]{3}|20[0-2][0-9])\b", g["desc"] + " " + g["titulo"]) or [""])[0]
    det = DETALLES.get(g["n"], {})
    if "anio" in det:
        anio = det["anio"]
    ctx = dict(clave=norm(g["nombre"] + " " + g["escena"]), n=g["n"], nombre=g["nombre"], canva=g["canva"],
               txt=txt, rnd=rnd, anio=anio, tema=tema, det=det)
    secuencia = det.get("seq") or secuencia_de(tema, g["n"])
    if not det.get("seq") and (det.get("av") or det.get("bar")):  # el vehículo real abre el video
        abre = ("avion", 0) if det.get("av") else ("mar", 0)
        secuencia = completar(abre, tema, g["n"])
    elif not det.get("seq") and det.get("obj"):  # el objeto real (manuscrito, disco, diamante...) abre el video
        abre = ("pantalla", 0) if det["obj"] in ("max", "cigarra") else ("escritorio", 0)
        secuencia = completar(abre, tema, g["n"])
    if anio and anio.isdigit() and int(anio) < 1912:  # sin radios ni radares antes de que existieran
        usados = {k for k, _ in secuencia}
        nuevo = []
        for k, v in secuencia:
            if k in ("radio", "radar", "pantalla"):
                k, v = next((c for c in (("escritorio", 2), ("mapa", 0)) if c[0] not in usados),
                            ("escritorio", 1))
                usados.add(k)
            nuevo.append((k, v))
        secuencia = nuevo
    tinte = TINTES[g["n"] % len(TINTES)]
    mayus = re.findall(r"\b[A-ZÁÉÍÓÚÑ]{4,}(?: [A-ZÁÉÍÓÚÑ]{2,})*\b", g["titulo"])
    escenas = {}
    n_par = len(g["parrafos"])
    camaras = [(1.0, 1.12, 0.5, 0.55), (1.12, 1.0, 0.5, 0.6), (1.0, 1.08, 0.45, 0.5), (1.06, 1.0, 0.55, 0.62)]

    for i in range(n_par):
        ultimo = i == n_par - 1
        kit, var = secuencia[min(i, len(secuencia) - 1)] if not ultimo else (secuencia[0][0],
                                                                             (secuencia[0][1] + 1) % 3)
        parrafo = g["parrafos"][i]

        class E(Escena):
            _kit, _var, _i, _ultimo, _parrafo = kit, var, i, ultimo, parrafo
            camara = camaras[(i + g["n"]) % 4]

            def __init__(self):
                super().__init__()
                self.fondo, self.din = KITS[self._kit](ctx, self._var)
                if any(tinte):
                    self.fondo = self.fondo.copy()
                    self.fondo.alpha_composite(Image.new("RGBA", (W, H), tinte + (34,)))
                if self._ultimo:
                    self.fondo = self.fondo.copy()
                    self.fondo.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 8, 120)))

            def mundo(self, t, dur):
                img = self.fondo.copy()
                self.din(img, t, dur)
                return img

            def sacudida(self, t, dur):
                return 0.8 * max(0.0, 1 - t / 0.6) if self._i == 0 else (0.25 if self._i == 2 else 0.0)

            def encima(self, img, t, dur):
                i_, ult = self._i, self._ultimo
                if i_ == 0:
                    chip(img, t, 0.05, "MISTERIOS SIN RESOLVER", y=150, fondo=(20, 20, 26), color=AMBAR, tam=34)
                    if g["canva"]:
                        sello(img, t, 0.35, g["canva"].strip("¿?«»").upper()[:22], W / 2, 780, ang=-8,
                              color=(220, 50, 50), tam=86)
                    ficha(img, t, dur * 0.45, "izq", 250, anio or "expediente", g["nombre"][:24], emoji="🔎")
                elif i_ == 1 and not ult:
                    if anio:
                        numero(img, t, 0.3, anio, g["nombre"][:30], y=380, color=(240, 230, 210), tam=150)
                elif i_ == 2 and not ult and mayus:
                    chip(img, t, dur * 0.3, mayus[0], y=300, fondo=(160, 30, 36), tam=50)
                elif not ult:
                    txt_s, col = sello_de(self._parrafo)
                    sello(img, t, dur * 0.55, txt_s, W / 2, 640, ang=-10, color=col, tam=90)
                if ult:
                    final(img, t, dur, g, self)

            def sonidos(self, dur):
                ev = []
                ev += sonidos_kit(self._kit, self._var, dur, ctx)
                if self._i == 0:
                    ev += [(0.0, "golpe", 0.4), (0.35, "sello", 0.3)]
                if self._i == 2:
                    ev.append((0, "latido", dur))
                if self._ultimo:
                    ev.append((dur * 0.6, "pop", 0.2))
                elif self._i >= 3:
                    ev.append((dur * 0.55, "sello", 0.3))
                return ev

        escenas[f"mis{g['n']:02d}_{i + 1}"] = E
    return escenas, tema


def final(img, t, dur, g, esc):
    """Cuatro finales distintos que rotan según el número del misterio."""
    pregunta = (re.findall(r"[^.?!]*\?", g["parrafos"][-1]) or ["¿Tú qué crees?"])[0].strip()
    estilo = g["n"] % 4
    d = ImageDraw.Draw(img)
    if estilo == 0:  # expediente que se cierra
        sello(img, t, 0.3, "CASO ABIERTO", W / 2, 720, ang=-10, tam=100)
        chip(img, t, 0.8, pregunta[:40], y=420, fondo=(20, 20, 26), color=AMBAR, tam=46)
    elif estilo == 1:  # comentario escribiéndose
        chip(img, t, 0.2, pregunta[:40], y=420, fondo=(20, 20, 26), color=AMBAR, tam=46)
        if t > 0.8:
            caja = (90, 690, W - 90, 830)
            sombra_suave(img, caja, radio=34)
            d.rounded_rectangle(caja, radius=34, fill=(255, 255, 255, 248), outline=TINTA, width=5)
            vis = "Yo creo que..."[:max(0, int((t - 0.8) * 9))]
            d.text((140, 760), vis + ("|" if int(t * 2.5) % 2 == 0 else ""), font=pro.fuente(48), fill=(60, 60, 70),
                   anchor="lm")
    elif estilo == 2:  # dos signos de pregunta gigantes
        for k, x in enumerate((250, 830)):
            p = pop((t - 0.2 - k * 0.15) / 0.3)
            if p > 0.05:
                d.text((x, 640 + 20 * math.sin(t * 3 + k)), "?", font=pro.fuente(int(300 * p)), fill=AMBAR,
                       anchor="mm", stroke_width=10, stroke_fill=TINTA)
        chip(img, t, 0.5, pregunta[:40], y=420, fondo=(20, 20, 26), color=AMBAR, tam=46)
        chip(img, t, 1.0, "COMENTA 👇".replace(" 👇", ""), y=900, fondo=(160, 30, 36), tam=44)
    else:  # logo de la serie entre la niebla
        p = min(1.0, t / 1.2)
        d.text((W / 2, 560), "MISTERIOS", font=pro.fuente(110), fill=(255, 220, 140, int(255 * p)), anchor="mm",
               stroke_width=8, stroke_fill=(20, 16, 10))
        d.text((W / 2, 680), "SIN RESOLVER", font=maquina(64), fill=(240, 240, 240, int(255 * p)), anchor="mm")
        chip(img, t, 0.9, pregunta[:40], y=860, fondo=(20, 20, 26), color=AMBAR, tam=44)
    ts = dur * 0.6
    if t > ts:  # franja de suscripción
        q = ease((t - ts) / 0.4)
        y = H - 240 + (1 - q) * 300
        caja = (110, y, W - 110, y + 120)
        sombra_suave(img, caja, radio=24)
        d.rounded_rectangle(caja, radius=24, fill=(18, 18, 24, 245), outline=AMBAR, width=5)
        d.text((W / 2, y + 60), "SUSCRÍBETE · más misterios reales", font=pro.fuente(42), fill=BLANCO, anchor="mm")


# =========================================================================== #
# MONTAJE POR MISTERIO
# =========================================================================== #
def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", norm(s)).strip("_")[:40]


def producir(n, guiones=None):
    guiones = guiones or cargar_guiones()
    g = guiones[n]
    audio = RAIZ / "audios" / "misterios" / f"misterio_{n:02d}_voz.mp3"
    if not audio.exists():
        print(f"✗ misterio {n:02d}: sin audio")
        return None
    escenas, tema = crear_escenas(g)
    jdir = RAIZ / "historias" / "misterios"
    jdir.mkdir(parents=True, exist_ok=True)
    nombre = f"misterio_{n:02d}_{slug(g['nombre'])}"
    j = jdir / f"{nombre}.json"
    j.write_text(json.dumps({"titulo": g["titulo"], "escenas": [{"texto": p, "visual": k} for p, k in
                                                                 zip(g["parrafos"], escenas)]},
                            ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"▶ {nombre} · tema {tema}")
    pro.generar(j, escenas, ESTILO, str(audio), False, cola=1.6, pad_hz=(46, 69, 92), hifi=True, acabado=True,
                crf=25, salida_dir=RAIZ / "salida" / "misterios")
    hecho = RAIZ / "salida" / "misterios" / f"{nombre}_pro.mp4"
    CARPETA_SALIDA.mkdir(exist_ok=True)
    final_ = CARPETA_SALIDA / f"{nombre}.mp4"
    hecho.replace(final_)
    (RAIZ / "salida" / "misterios" / f"{nombre}.txt").write_text(
        f"TÍTULO: {g['titulo']}\n\nDESCRIPCIÓN:\n{g['desc'].split(' · ')[0]}\n\n¿Tú qué crees? Te leo en los "
        f"comentarios 👇\n🔔 Suscríbete para más historias reales que parecen inventadas.\n\n#shorts #misterio "
        f"#misterios #misteriossinresolver #enigmas #historiasreales #datoscuriosos #sabiasque #historia "
        f"#curiosidades {(g['desc'].split(' · ') + [''])[1]}\n", encoding="utf-8")
    return final_


if __name__ == "__main__":
    gs = cargar_guiones()
    nums = [int(x) for x in sys.argv[1:] if x.isdigit()]
    if not nums and "todos" in sys.argv:
        nums = sorted(int(p.name[9:11]) for p in (RAIZ / "audios" / "misterios").glob("misterio_*_voz.mp3"))
    for n in nums:
        producir(n, gs)
