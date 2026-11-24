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
    r, paleta = ctx["rnd"], ("tormenta" if var == 0 else "niebla" if var == 1 else "noche")
    tipo_barco = "buque" if re.search(r"buque|transatl|vapor|marina|carguero|baychimo|cyclops|waratah", ctx["txt"]) \
        else "velero"

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[paleta]))
        mar(L, 1150, (22, 34, 46) if paleta != "niebla" else (92, 104, 112))
    fondo = full(dib)
    bx = r.uniform(380, 700)
    capa = LienzoReal(W, H, 0, 0)
    (buque if tipo_barco == "buque" else velero)(capa, 0 + 540, 640, 0.9 if tipo_barco == "buque" else 1.0,
                                                    (30, 30, 36) if paleta != "niebla" else (70, 72, 78))
    barco = capa.final()

    def din(img, t, dur):
        bob = 10 * math.sin(t * 1.4)
        img.alpha_composite(barco.rotate(2.5 * math.sin(t * 1.1), resample=Image.BICUBIC),
                            (int(bx - 540 + t * 12), int(1160 - 640 + bob)))
        olas(img, t, 1170, col=(120, 150, 180) if paleta != "niebla" else (200, 210, 220), alfa=120)
        if paleta == "tormenta":
            particulas(img, t, "lluvia", 90, viento=-300, alfa=190)
            for t0 in (0.5, dur * 0.6):
                relampago(img, t, t0)
        niebla(img, t, 1100, 0.45 if paleta == "niebla" else 0.25, n=9)
    return fondo, din


def kit_avion(ctx, var):
    r = ctx["rnd"]
    a_ = int(ctx["anio"] or 1970)
    tipo = "helice" if a_ < 1950 or re.search(r"avioneta|helice|aviadora", ctx["txt"]) else \
        ("electra" if a_ < 1975 else "727")
    pal = "tormenta" if var else "noche"

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[pal]))
        mar(L, 1500, (14, 22, 34))
        rr = random.Random(3)
        for _ in range(110):
            L.circulo(rr.randint(0, W), rr.randint(0, 1100), rr.choice((1.5, 2, 2.5)), (230, 230, 255), borde=False)
    fondo = full(dib)
    pegar_glow(fondo, 800, 330, 150, "#dfe8ff", 0.6)
    ImageDraw.Draw(fondo).ellipse((760, 290, 840, 370), fill=(236, 238, 246))
    pegar_glow(fondo, 800, 1560, 220, "#9fb0d0", 0.35)
    av = pro.avion(tipo)
    a = av.convert("LA").convert("RGBA")
    a.putalpha(av.getchannel("A"))
    oscuro_ = Image.new("RGBA", a.size, (20, 24, 34, 255))
    oscuro_.putalpha(av.getchannel("A"))
    sil = Image.blend(av, oscuro_, 0.45)
    sil = sil.resize((int(sil.width * 1.25), int(sil.height * 1.25)), Image.LANCZOS)
    y0 = r.uniform(960, 1120)

    def din(img, t, dur):
        for i in range(5):
            x = (i * 300 - t * 50) % (W + 600) - 300
            pegar_glow(img, x, 700 + (i % 3) * 200, 300, "#3a4054", 0.7)
        x = 260 + W * 0.75 * (t / max(dur, 0.1))
        img.alpha_composite(sil.rotate(3 * math.sin(t * 0.9), resample=Image.BICUBIC),
                            (int(x - sil.width / 2), int(y0 - sil.height / 2)))
        if int(t * 2) % 2 == 0:
            pegar_glow(img, x + sil.width * 0.42, y0, 22, "#ff3030", 1.0)
        pegar_glow(img, x - sil.width * 0.38, y0 - 20, 16, "#ffffff", 0.8)
        if var:
            particulas(img, t, "lluvia", 80, viento=-400, alfa=160)
            relampago(img, t, dur * 0.5)
    return fondo, din


def kit_radar(ctx, var):
    fondo = _grad(W, H, [(0, (6, 14, 10)), (1, (2, 6, 4))])
    r = ctx["rnd"]
    blips = [(r.uniform(-1, 1) * 260, r.uniform(-1, 1) * 260) for _ in range(5)]

    def din(img, t, dur):
        cx, cy, R = 540, 900, 400
        d = ImageDraw.Draw(img)
        for k in range(1, 5):
            d.ellipse((cx - R * k / 4, cy - R * k / 4, cx + R * k / 4, cy + R * k / 4), outline=(40, 160, 90), width=3)
        d.line((cx - R, cy, cx + R, cy), fill=(30, 110, 60), width=2)
        d.line((cx, cy - R, cx, cy + R), fill=(30, 110, 60), width=2)
        ang = t * 2.2
        for k in range(18):
            a = ang - k * 0.04
            d.line((cx, cy, cx + R * math.cos(a), cy + R * math.sin(a)), fill=(60, 255, 140, int(140 * (1 - k / 18))),
                   width=6)
        for i, (bx, by) in enumerate(blips):
            vivo = not (i == 0 and t > dur * 0.55)
            if vivo:
                pegar_glow(img, cx + bx, cy + by, 22, "#60ff90", 0.6 + 0.4 * math.sin(t * 4 + i))
        if t > dur * 0.55:
            d.text((cx, cy - R - 70), "SEÑAL PERDIDA", font=maquina(54), fill=(255, 80, 80), anchor="mm")
    return fondo, din


def kit_faro(ctx, var):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS["tormenta"]))
        mar(L, 1250, (20, 30, 42))
        L.forma(catmull([(160, 1300), (300, 1080), (700, 1040), (900, 1150), (980, 1300)], 4), (50, 48, 50),
                intensidad=0.1, textura=0.1)
        L.forma([(520, 1060), (560, 520), (640, 520), (680, 1060)], (226, 222, 214), suave=False, intensidad=0.1)
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

    def din(img, t, dur):
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
    hoja = hoja.rotate(r.uniform(-6, 6), expand=True, resample=Image.BICUBIC)

    def din(img, t, dur):
        p = ease(t / 0.8)
        y = 1000 + (1 - p) * 700
        sombra_suave(img, (540 - 340, y - 450, 540 + 340, y + 450), radio=10, alfa=140, blur=26)
        img.alpha_composite(hoja, (int(540 - hoja.width / 2), int(y - hoja.height / 2)))
        fl = 1 + 0.1 * math.sin(t * 11)
        pegar_glow(img, 150, 400, 90 * fl, "#ffcf7a", 0.8)
        if modo == "simbolos":  # lupa recorriendo los símbolos
            lx, ly = 540 + 220 * math.sin(t * 0.7), 1000 + 260 * math.sin(t * 0.5)
            d = ImageDraw.Draw(img)
            d.ellipse((lx - 120, ly - 120, lx + 120, ly + 120), outline=(200, 170, 110), width=14)
            d.line((lx + 85, ly + 85, lx + 200, ly + 200), fill=(90, 60, 40), width=26)
    return fondo, din


def kit_mapa(ctx, var):
    r = ctx["rnd"]

    def dib(L):
        L.d.rectangle((0, 0, W * 2, H * 2), fill=(40, 30, 22))
        L.forma([(70, 280), (1010, 260), (1030, 1260), (60, 1280)], (232, 214, 170), intensidad=0.05, textura=0.14)
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
    tipo = ("tumba" if re.search(r"tumba", txt) else "piramide" if re.search(r"piramid|teotihuacan|esfinge|egipto|maya", txt) else
            "esfera" if re.search(r"esfera", txt) else
            "piedras" if re.search(r"stonehenge|piedra|gobekli|pilares", txt) else
            "cabeza" if re.search(r"moai|cabeza|estatua|olmeca", txt) else
            "esfera" if re.search(r"esfera", txt) else "columnas")
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
    pal = "niebla" if var == 0 else "noche"
    victoriana = bool(re.search(r"18\d\d|londres|whitechapel", ctx["txt"]))

    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS[pal]))
        col = (60, 58, 64) if pal == "noche" else (110, 108, 112)
        for lado in (0, 1):
            x0 = 0 if lado == 0 else W - 330
            L.forma([(x0, 1500), (x0, 300), (x0 + 330, 420 if lado == 0 else 300), (x0 + 330, 1500)], col,
                    suave=False, intensidad=0.08, textura=0.12)
            for k in range(6):
                y = 460 + k * 160
                L.forma([(x0 + 80, y), (x0 + 160, y), (x0 + 160, y + 100), (x0 + 80, y + 100)],
                        (230, 190, 110) if (k + lado) % 3 == 0 else (50, 50, 56), suave=False, borde=False)
        L.forma([(0, 1500), (W, 1500), (W, H), (0, H)], (52, 50, 56), suave=False, borde=False, textura=0.16)
        L.forma([(300, 1500), (780, 1500), (1000, H), (80, H)], (66, 64, 70), suave=False, borde=False, textura=0.1)
    fondo = full(dib)
    r = ctx["rnd"]
    lx = r.choice((360, 720))

    def din(img, t, dur):
        d = ImageDraw.Draw(img)
        d.line((lx, 1500, lx, 820), fill=(30, 30, 34), width=14)
        pegar_glow(img, lx, 820, 150, "#ffd890" if victoriana else "#fff0c0", 0.8)
        x = 540 + 8 * math.sin(t)
        s = max(0.35, 0.8 - t * 0.04)
        silueta(d, x, 1500 - (0.8 - s) * 300, s, t * 0.6, agachado=False, col=(14, 14, 18))
        niebla(img, t, 1350, 0.55 if pal == "niebla" else 0.35, n=10)
        if pal == "noche":
            particulas(img, t, "lluvia", 70, viento=-120, alfa=150)
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
        p = pop(t / 0.5)
        h = hoja.resize((max(1, int(hoja.width * p)), max(1, int(hoja.height * p))))
        sombra_suave(img, (540 - h.width / 2 + 10, 900 - h.height / 2 + 10, 540 + h.width / 2 - 10,
                           900 + h.height / 2 - 10), radio=6, alfa=140)
        img.alpha_composite(h, (int(540 - h.width / 2), int(900 - h.height / 2)))
        particulas(img, t, "lluvia", 40, viento=-60, alfa=120)
    return fondo, din


def kit_nieve(ctx, var):
    from andes import fondo_cordillera
    fondo = fondo_cordillera("noche" if var != 1 else "dia")

    def din(img, t, dur):
        particulas(img, t, "nieve", 110, viento=-260, vel=1.5)
        if var == 2:
            d = ImageDraw.Draw(img)
            for k in range(12):
                x, y = 200 + k * 60, 1700 - k * 30
                d.ellipse((x - 12, y - 6, x + 12, y + 6), fill=(150, 160, 190))
    return fondo, din


def kit_selva(ctx, var):
    from juliane import fondo_selva
    fondo = fondo_selva(oscura=var != 1, rio=var == 2, semilla=ctx["n"] + var)

    def din(img, t, dur):
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
    cuello = bool(re.search(r"ness|lago|monstruo", ctx["txt"]))

    def din(img, t, dur):
        d = ImageDraw.Draw(img)
        if cuello:
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
        niebla(img, t, 1450, 0.5, n=10)
        if pal == "noche":
            linterna(img, 120, 1900, 540 + 300 * math.sin(t * 0.8), 1300 + 120 * math.sin(t * 1.3), ancho=230,
                     oscuridad=170)
        elif pal == "atardecer":
            k = max(0.0, 1 - abs(t - dur * 0.3) / 0.6)
            pegar_glow(img, 700, 900, 300 + 500 * k, "#ffb060", 0.4 + 0.6 * k)
            particulas(img, t, "ceniza", 50, alfa=170)
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
        if var == 1 or (var == 0 and int(t * 3) % 5 == 0):
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
        "calle": kit_calle, "cartel": kit_cartel, "nieve": kit_nieve, "selva": kit_selva, "lago": kit_lago, "bosque": kit_bosque,
        "pantalla": kit_pantalla}

SECUENCIAS = {
    "mar": [("mar", 0), ("mar", 1), ("escritorio", 2), ("mar", 2)],
    "aire": [("avion", 0), ("radar", 0), ("avion", 1), ("mapa", 0)],
    "faro": [("faro", 0), ("mar", 0), ("escritorio", 2), ("faro", 2)],
    "espacio": [("espacio", 0), ("escritorio", 0), ("radar", 0), ("espacio", 1)],
    "ovni": [("luces", 0), ("radar", 0), ("luces", 1), ("escritorio", 1)],
    "codigo": [("escritorio", 0), ("escritorio", 1), ("calle", 0), ("escritorio", 0)],
    "tesoro": [("cueva", 0), ("mapa", 0), ("selva", 1), ("cueva", 1)],
    "antiguo": [("ruinas", 0), ("escritorio", 0), ("ruinas", 2), ("mapa", 0)],
    "crimen": [("calle", 0), ("escritorio", 1), ("cartel", 0), ("calle", 1)],
    "hielo": [("nieve", 0), ("nieve", 1), ("mapa", 0), ("nieve", 2)],
    "selva": [("selva", 0), ("mapa", 0), ("selva", 2), ("ruinas", 2)],
    "criatura": [("lago", 0), ("escritorio", 1), ("lago", 2), ("selva", 0)],
    "fenomeno": [("luces", 0), ("escritorio", 1), ("luces", 1), ("mapa", 0)],
    "persona": [("calle", 0), ("cartel", 0), ("calle", 1), ("mapa", 0)],
    "bosque": [("bosque", 0), ("cartel", 0), ("bosque", 1), ("mapa", 0)],
    "senal": [("pantalla", 0), ("escritorio", 1), ("pantalla", 1), ("escritorio", 0)],
    "cartografia": [("mapa", 0), ("escritorio", 2), ("mar", 1), ("mapa", 0)],
    "oceano": [("mar", 2), ("radar", 0), ("mar", 1), ("escritorio", 1)],
    "joya": [("escritorio", 1), ("cueva", 0), ("calle", 1), ("cueva", 1)],
    "explosion": [("bosque", 2), ("escritorio", 1), ("bosque", 2), ("mapa", 0)],
    "selva_persona": [("selva", 0), ("mapa", 0), ("selva", 2), ("cartel", 0)],
    "selva_tesoro": [("selva", 0), ("mapa", 0), ("cueva", 0), ("selva", 2)],
}

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
    ctx = dict(clave=norm(g["nombre"] + " " + g["escena"]), n=g["n"], nombre=g["nombre"], canva=g["canva"], txt=txt, rnd=rnd, anio=anio, tema=tema)
    secuencia = SECUENCIAS[tema]
    mayus = re.findall(r"\b[A-ZÁÉÍÓÚÑ]{4,}(?: [A-ZÁÉÍÓÚÑ]{2,})*\b", g["titulo"])
    escenas = {}
    n_par = len(g["parrafos"])
    camaras = [(1.0, 1.12, 0.5, 0.55), (1.12, 1.0, 0.5, 0.6), (1.0, 1.08, 0.45, 0.5), (1.06, 1.0, 0.55, 0.62)]

    for i in range(n_par):
        ultimo = i == n_par - 1
        kit, var = secuencia[min(i, len(secuencia) - 1)] if not ultimo else secuencia[0]
        parrafo = g["parrafos"][i]

        class E(Escena):
            _kit, _var, _i, _ultimo, _parrafo = kit, var, i, ultimo, parrafo
            camara = camaras[(i + g["n"]) % 4]

            def __init__(self):
                super().__init__()
                self.fondo, self.din = KITS[self._kit](ctx, self._var)
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
                if self._i == 0:
                    ev += [(0.0, "golpe", 0.4), (0.35, "sello", 0.3)]
                    ev += [(0, s, 60.0) for s in SONIDO[tema]]
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
    (CARPETA_SALIDA / f"{nombre}.txt").write_text(
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
