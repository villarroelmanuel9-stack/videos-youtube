#!/usr/bin/env python3
"""
Historia 12: LA FUGA DE ALCATRAZ — producción "pro" (motor de dinos.py) con identidad propia:
  * Paleta fría nocturna, niebla, faro y reflector que barren la escena.
  * Recuadros estilo EXPEDIENTE POLICIAL (papel, clip, máquina de escribir) y SELLOS.
  * Subtítulos con palabra activa en celeste.
  * Sonido temático: raspado de cucharas, taladro, flash de fichas, latidos, olas, sirena, sellos, reja.
  * Final propio: reja que se cierra, carteles "SE BUSCA", sello "CASO ABIERTO" y pregunta para comentar.

Uso:
    python alcatraz.py historias/historia_12_alcatraz.json [--audio audios/historia_12_voz.mp3] [--sin-audio]
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from cine import SR, alinear_audio, escribir_wav, fuente, leer_wav, pegar_glow, ruido_filtrado, _primera_existente
from dinos import (TINTA, VINETA, EscenaDino, Lienzo, Sprite, _grad, barrido, camara, capsula, catmull, chip,
                   claro, elipse, numero_gigante, oscuro, radius_ok, sombra_suave)
from caricatura import ease, pop
from generar_short import FPS, H, W, agrupar_palabras, narrar, render_emoji

RAIZ = Path(__file__).resolve().parent
CELESTE, ROJO, BLANCO, VERDE, AMBAR = (90, 210, 255), (214, 40, 46), (255, 255, 255), (70, 190, 110), (255, 196, 70)
PAPEL = (238, 222, 178)

_MAQ = [str(RAIZ / "fuentes" / "maquina.ttf"), "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "C:/Windows/Fonts/courbd.ttf",
        "/System/Library/Fonts/Courier.dfont"]
_maq_cache: dict = {}


def maquina(tam):
    if tam not in _maq_cache:
        r = _primera_existente(_MAQ)
        _maq_cache[tam] = ImageFont.truetype(r, tam) if r else fuente(tam)
    return _maq_cache[tam]


# =========================================================================== #
# PERSONAJES (retratos con sombreado)
# =========================================================================== #
PEINADOS = {
    "morris": ((70, 52, 38), [(-96, -300), (-92, -362), (-52, -398), (0, -408), (52, -400), (94, -362), (96, -300),
                              (80, -334), (30, -354), (-30, -356), (-82, -334)]),
    "john": ((36, 30, 30), [(-98, -296), (-96, -366), (-60, -404), (-10, -416), (40, -410), (80, -386), (98, -340),
                            (96, -296), (70, -330), (52, -352), (20, -336), (-10, -360), (-50, -340), (-84, -326)]),
    "clarence": ((118, 84, 52), [(-96, -298), (-90, -364), (-40, -404), (20, -410), (70, -392), (96, -350),
                                 (96, -298), (74, -340), (10, -352), (-40, -348), (-84, -330)]),
}


def _retrato(L, f, boca, parp, extra):
    estilo, modo = extra  # modo: 'ficha' | 'cabeza' | 'falsa0'..'falsa3'
    piel = (232, 188, 150)
    plano = modo.startswith("falsa")
    etapa = int(modo[-1]) if plano else 3
    if modo == "ficha":
        L.forma([(-175, 0), (-168, -110), (-95, -165), (95, -165), (168, -110), (175, 0)], (112, 126, 150))
        L.forma([(-40, -165), (0, -110), (40, -165)], (232, 232, 226), ancho=4, suave=False)
        L.forma([(-78, -88), (78, -88), (78, -30), (-78, -30)], (30, 32, 38), suave=False, sombra=False,
                brillo=False, ancho=4)
        num = {"morris": "AZ-1441", "john": "AZ-1476", "clarence": "AZ-1485"}[estilo]
        (x, y), = L.P([(0, -59)])
        L.d.text((x, y), num, font=maquina(int(30 * 2)), fill=BLANCO, anchor="mm")
        L.forma(capsula((0, -150), (0, -205), 72, 70), piel, intensidad=0.06)
    if plano and etapa == 0:
        L.forma(elipse(0, -280, 90, 108), (236, 232, 226), sombra=True, brillo=False, intensidad=0.08)
        for i in range(5):
            L.linea([(-60 + i * 25, -330 + (i % 2) * 20), (-40 + i * 25, -300)], (200, 196, 190), 4)
        return
    col_piel = (226, 186, 160) if plano else piel
    for sx in (-1, 1):
        L.forma(elipse(sx * 90, -272, 22, 32), col_piel, intensidad=0.1, brillo=not plano)
    L.forma(elipse(0, -280, 92, 112), col_piel, intensidad=0.1 if not plano else 0.05, brillo=not plano)
    if plano and etapa == 1:
        for i in range(6):
            L.linea([(-70 + i * 28, -360), (-60 + i * 28, -200)], (205, 170, 145), 3)
        return
    color_pelo, pelo = PEINADOS[estilo]
    if etapa >= 3:
        L.forma(pelo, color_pelo, intensidad=0.09)
    # cejas y ojos
    for sx in (-1, 1):
        L.linea([(sx * 22, -318), (sx * 58, -322 + (4 if modo == "ficha" else 0))], oscuro(color_pelo, 0.8), 7)
    if plano or modo == "cabeza":
        for sx in (-1, 1):
            L.linea(catmull([(sx * 20, -290), (sx * 36, -282), (sx * 52, -290)], 4, cerrado=False), TINTA, 4)
    else:
        for sx in (-1, 1):
            L.ojo(sx * 36, -290, 13, parpadeo=parp, iris=(90, 110, 140), mirar=(0, 0))
    L.linea(catmull([(-4, -275), (-12, -238), (4, -232)], 4, cerrado=False), oscuro(piel, 0.7), 4)
    L.linea([(-24, -205), (24, -205)], (150, 90, 80), 5)
    if plano:
        for sx in (-1, 1):
            L.circulo(sx * 50, -235, 12, (236, 160, 150), borde=False)


def retrato(estilo, modo="ficha"):
    return Sprite(lambda L, f, b, p, e: _retrato(L, f, b, p, (estilo, modo)), 380, 470, 190, 460, fases=1)


RETRATOS = {e: retrato(e) for e in PEINADOS}
CABEZA_FALSA = {i: Sprite(lambda L, f, b, p, e, i=i: _retrato(L, f, b, p, ("john", f"falsa{i}")), 380, 470, 190, 460,
                          fases=1) for i in range(4)}


def silueta(d, x, y, s, t, fase=0.0, agachado=True, col=(8, 10, 16)):
    """Silueta humana corriendo (para el techo y la balsa)."""
    paso = math.sin(t * 9 + fase)
    inc = 0.35 if agachado else 0.0
    cx, cy = x, y - 120 * s
    d.ellipse((cx + 30 * inc * s - 22 * s, cy - 120 * s, cx + 30 * inc * s + 22 * s, cy - 76 * s), fill=col)
    d.line((cx + 25 * inc * s, cy - 80 * s, cx, cy), fill=col, width=int(34 * s))
    for sg in (-1, 1):
        d.line((cx, cy, cx + sg * paso * 35 * s, y), fill=col, width=int(16 * s))
        d.line((cx + 15 * inc * s, cy - 60 * s, cx + 40 * s + sg * paso * 20 * s, cy - 20 * s), fill=col,
               width=int(12 * s))


# =========================================================================== #
# RECUADROS NUEVOS: ficha de expediente y sellos
# =========================================================================== #
def ficha(img, t, t0, lado, y, titulo, valor, dur=None, emoji=None, giro=None):
    if t < t0 or (dur is not None and t > t0 + dur + 0.3):
        return
    p = pop((t - t0) / 0.32)
    salida = 1.0 if dur is None else max(0.0, min(1.0, (t0 + dur + 0.3 - t) / 0.3))
    fv, ft = fuente(62), maquina(30)
    medidor = ImageDraw.Draw(img)
    tx = 150 if emoji else 44
    w = int(max(medidor.textlength(valor, font=fv), medidor.textlength(titulo.upper(), font=ft)) + tx + 50)
    h = 176
    capa = Image.new("RGBA", (w + 40, h + 60), (0, 0, 0, 0))
    cd = ImageDraw.Draw(capa)
    cd.rectangle((20, 30, 20 + w, 30 + h), fill=PAPEL + (255,), outline=(120, 100, 70), width=4)
    cd.line((20 + 30, 30 + 70, 20 + w - 30, 30 + 70), fill=(200, 180, 140), width=2)
    for i in range(3):  # textura de papel
        cd.line((20 + 30, 30 + 120 + i * 18, 20 + w - 30, 30 + 120 + i * 18), fill=(228, 210, 165), width=2)
    cd.rounded_rectangle((44, 6, 74, 76), radius=14, outline=(150, 155, 165), width=6)  # clip
    if emoji:
        em = render_emoji(emoji)
        if em is not None:
            em = em.resize((92, int(92 * em.height / em.width)), Image.LANCZOS)
            capa.alpha_composite(em, (52, int(30 + (h - em.height) / 2)))
    cd.text((20 + tx, 30 + 26), titulo.upper(), font=ft, fill=(90, 70, 50))
    cd.text((20 + tx, 30 + 78), valor, font=fv, fill=TINTA)
    cd.line((20 + tx, 30 + 152, 20 + tx + medidor.textlength(valor, font=fv), 30 + 152), fill=ROJO + (255,), width=6)
    ang = giro if giro is not None else (2.5 if lado == "izq" else -2.5)
    capa = capa.rotate(ang, expand=True, resample=Image.BICUBIC)
    margen = 30
    if lado == "izq":
        x = margen - (1 - p) * (capa.width + 80) - (1 - salida) * (capa.width + 80)
    else:
        x = W - margen - capa.width + (1 - p) * (capa.width + 80) + (1 - salida) * (capa.width + 80)
    sombra_suave(img, (x + 20, y + 30, x + capa.width - 20, y + capa.height - 20), radio=6, alfa=120)
    img.alpha_composite(capa, (int(x), int(y)))


def sello(img, t, t0, txt, x, y, ang=-12, color=ROJO, tam=96):
    if t < t0:
        return
    q = min(1.0, (t - t0) / 0.18)
    esc = 1.8 - 0.8 * q
    f = maquina(tam)
    medidor = ImageDraw.Draw(img)
    w = int(medidor.textlength(txt, font=f)) + 80
    hh = tam + 70
    capa = Image.new("RGBA", (w, hh), (0, 0, 0, 0))
    cd = ImageDraw.Draw(capa)
    cd.rectangle((6, 6, w - 6, hh - 6), outline=color + (255,), width=10)
    cd.rectangle((20, 20, w - 20, hh - 20), outline=color + (255,), width=4)
    cd.text((w / 2, hh / 2), txt, font=f, fill=color + (255,), anchor="mm")
    rnd = random.Random(len(txt))
    for _ in range(int(w * hh / 900)):  # desgaste del sello
        px, py = rnd.randint(0, w), rnd.randint(0, hh)
        cd.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(0, 0, 0, 0))
    capa.putalpha(capa.getchannel("A").point(lambda v: int(v * (0.35 + 0.6 * q))))
    capa = capa.rotate(ang, expand=True, resample=Image.BICUBIC)
    if esc != 1:
        capa = capa.resize((int(capa.width * esc), int(capa.height * esc)), Image.BILINEAR)
    img.alpha_composite(capa, (int(x - capa.width / 2), int(y - capa.height / 2)))


def etiqueta_maquina(img, t, t0, txt, x, y, color=PAPEL):
    if t < t0:
        return
    p = pop((t - t0) / 0.3)
    f = maquina(max(8, int(34 * p)))
    d = ImageDraw.Draw(img)
    w = d.textlength(txt, font=f) + 36
    caja = (x - w / 2, y - 30 * p, x + w / 2, y + 30 * p)
    sombra_suave(img, caja, radio=4, alfa=90, blur=10)
    d.rectangle(caja, fill=color, outline=(110, 90, 60), width=3)
    d.text((x, y), txt, font=f, fill=TINTA, anchor="mm")


def subtitulo(img, grupos, t, y=1365, color=CELESTE):
    grupo = None
    for i, g in enumerate(grupos):
        fin = grupos[i + 1][0].inicio if i + 1 < len(grupos) else 1e9
        if g[0].inicio - 0.04 <= t < fin:
            grupo = g
            break
    if not grupo:
        return
    f, fa = fuente(74), fuente(86)
    d = ImageDraw.Draw(img)
    pal = [p.texto.strip(",.;:«»").upper() for p in grupo]
    activa = max([i for i, p in enumerate(grupo) if t >= p.inicio - 0.03] or [0])
    anchos = [d.textlength(w, font=fa if i == activa else f) for i, w in enumerate(pal)]
    esp = 20
    if sum(anchos) + esp * (len(pal) - 1) > W - 110:
        f, fa = fuente(60), fuente(70)
        anchos = [d.textlength(w, font=fa if i == activa else f) for i, w in enumerate(pal)]
    total = sum(anchos) + esp * (len(pal) - 1)
    x = (W - total) / 2
    yy = y + (1 - pop((t - grupo[0].inicio + 0.04) / 0.15)) * 22
    sombra = Image.new("RGBA", (W, 220), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sombra)
    xs = x
    for i, w in enumerate(pal):
        sd.text((xs, 110), w, font=fa if i == activa else f, fill=(0, 0, 0, 200), anchor="lm", stroke_width=12,
                stroke_fill=(0, 0, 0, 200))
        xs += anchos[i] + esp
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(9)), (0, int(yy - 100)))
    for i, w in enumerate(pal):
        d.text((x, yy - (5 if i == activa else 0)), w, font=fa if i == activa else f,
               fill=color if i == activa else BLANCO, anchor="lm", stroke_width=8, stroke_fill=(10, 14, 24))
        x += anchos[i] + esp


# =========================================================================== #
# FONDOS
# =========================================================================== #
def _full(dib):
    L = Lienzo(W, H, 0, 0)
    dib(L)
    return L.final()


def oscurecer(img, alfa, color=(4, 8, 20)):
    img.alpha_composite(Image.new("RGBA", img.size, color + (int(alfa),)))


def fondo_celda():
    def dib(L):
        L.d.rectangle((0, 0, W * 2, H * 2), fill=(58, 66, 82))
        for y in range(0, 1350, 90):
            for x in range(-((y // 90) % 2) * 90, W, 180):
                L.d.rectangle((x * 2, y * 2, (x + 180) * 2, (y + 90) * 2), outline=(48, 55, 70), width=6)
        L.forma([(0, 1350), (W, 1350), (W, H), (0, H)], (70, 72, 80), suave=False, borde=False)
        L.forma([(760, 760), (980, 760), (980, 900), (760, 900)], (40, 44, 54), suave=False, ancho=5)
        for i in range(6):
            L.linea([(770, 778 + i * 22), (970, 778 + i * 22)], (110, 118, 130), 8)
        L.forma([(110, 1260), (980, 1260), (990, 1330), (100, 1330)], (90, 96, 108), suave=False, ancho=5)
        for x in (120, 960):
            L.forma([(x - 12, 1320), (x + 12, 1320), (x + 12, 1520), (x - 12, 1520)], (80, 84, 96), suave=False)
        L.forma([(110, 1170), (990, 1170), (990, 1270), (110, 1270)], (196, 200, 206), intensidad=0.06)
        L.forma(elipse(250, 1150, 150, 58), (232, 232, 236), intensidad=0.1)
        L.forma(catmull([(330, 1170), (420, 1090), (620, 1070), (840, 1090), (980, 1150), (980, 1200), (330, 1200)],
                        4), (110, 122, 146), intensidad=0.12)
    return _full(dib)


def barrotes(img, t=0.0, alfa=255):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for i in range(9):
        x = 40 + i * 125
        d.rectangle((x - 16, 0, x + 16, H), fill=(28, 30, 36, alfa))
        d.rectangle((x - 9, 0, x - 3, H), fill=(80, 86, 98, alfa))
    for y in (240, 1700):
        d.rectangle((0, y - 22, W, y + 22), fill=(28, 30, 36, alfa))
        d.rectangle((0, y - 16, W, y - 10), fill=(80, 86, 98, alfa))
    img.alpha_composite(capa)


def linterna(img, cx, cy, tx, ty, ancho=230, oscuridad=200):
    """Oscurece la escena salvo un cono de luz de (cx,cy) hacia (tx,ty)."""
    m = Image.new("L", (W // 4, H // 4), oscuridad)
    d = ImageDraw.Draw(m)
    ang = math.atan2(ty - cy, tx - cx)
    nx, ny = -math.sin(ang), math.cos(ang)
    pts = [(cx / 4, cy / 4), ((tx + nx * ancho) / 4, (ty + ny * ancho) / 4),
           ((tx - nx * ancho) / 4, (ty - ny * ancho) / 4)]
    d.polygon(pts, fill=40)
    d.ellipse(((tx - ancho) / 4, (ty - ancho * 0.75) / 4, (tx + ancho) / 4, (ty + ancho * 0.75) / 4), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    capa = Image.new("RGBA", (W, H), (3, 6, 14, 255))
    capa.putalpha(m)
    img.alpha_composite(capa)


def fondo_isla(amanecer=False):
    def dib(L):
        cielo = _grad(W * 2, H * 2, [(0, (6, 10, 26)), (0.5, (22, 34, 64)), (0.56, (40, 56, 86)), (1, (10, 18, 34))]) \
            if not amanecer else _grad(W * 2, H * 2, [(0, (60, 70, 100)), (0.45, (210, 150, 140)),
                                                       (0.56, (240, 190, 160)), (1, (60, 80, 110))])
        L.img.alpha_composite(cielo)
        rnd = random.Random(2)
        if not amanecer:
            for _ in range(160):
                x, y = rnd.randint(0, W), rnd.randint(0, 900)
                L.circulo(x, y, rnd.choice((1.5, 2, 2.5)), (230, 230, 255), borde=False)
            L.circulo(860, 260, 70, (240, 238, 220), borde=False)
        # costa lejana: San Francisco y el puente
        for x in range(640, W, 34):
            h = rnd.randint(40, 160)
            L.forma([(x, 1075), (x, 1075 - h), (x + 28, 1075 - h), (x + 28, 1075)], (30, 40, 62) if not amanecer
                    else (110, 110, 140), suave=False, borde=False, sombra=False, brillo=False)
            if not amanecer:
                for _ in range(3):
                    L.circulo(x + rnd.randint(6, 22), 1075 - rnd.randint(10, h - 5), 2.5, (255, 220, 140),
                              borde=False)
        for px in (80, 330):
            L.forma([(px - 8, 1075), (px - 8, 880), (px + 8, 880), (px + 8, 1075)], (150, 60, 50) if amanecer
                    else (70, 40, 44), suave=False, borde=False, sombra=False, brillo=False)
        L.linea(catmull([(0, 960), (80, 885), (205, 990), (330, 885), (450, 970)], 6, cerrado=False),
                (150, 60, 50) if amanecer else (70, 40, 44), 6)
        # agua
        L.forma([(0, 1075), (W, 1075), (W, H), (0, H)], (16, 30, 54) if not amanecer else (90, 110, 140),
                suave=False, borde=False, sombra=False, brillo=False)
        # isla
        base = 1180
        roca = (64, 60, 62) if not amanecer else (110, 100, 100)
        L.forma([(150, base), (210, 1090), (330, 1040), (720, 1030), (880, 1070), (950, base)], roca,
                intensidad=0.08)
        L.forma([(300, 1045), (760, 1035), (760, 920), (300, 930)], (150, 150, 145) if amanecer else (92, 96, 104),
                suave=False, intensidad=0.05)
        L.forma([(360, 930), (700, 922), (700, 870), (360, 878)], (130, 130, 128) if amanecer else (82, 86, 94),
                suave=False, intensidad=0.05)
        for fila in range(3):
            for i in range(14):
                x = 320 + i * 31
                y = 945 + fila * 30
                L.forma([(x, y), (x + 16, y), (x + 16, y + 16), (x, y + 16)],
                        (255, 210, 120) if not amanecer else (70, 70, 80), suave=False, borde=False, sombra=False,
                        brillo=False)
        L.forma([(780, 1030), (800, 900), (830, 900), (850, 1030)], (90, 90, 96), suave=False, intensidad=0.05)
        L.forma(elipse(815, 885, 45, 30), (100, 100, 108), intensidad=0.08)
        L.forma([(215, 1080), (225, 880), (255, 880), (265, 1080)], (220, 220, 220), suave=False, intensidad=0.06)
        L.forma([(212, 880), (268, 880), (262, 840), (218, 840)], (40, 40, 48), suave=False)
    return _full(dib)


def olas(img, t, y0=1090, col=(90, 130, 180), n=26, alfa=110):
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for i in range(n):
        y = y0 + (i / n) ** 1.5 * (H - y0)
        x = (rnd.uniform(0, W) + t * (20 + 40 * i / n)) % (W + 200) - 100
        w = 40 + 140 * i / n
        d.arc((x - w, y - 10, x + w, y + 10), 200, 340, fill=col + (alfa,), width=max(2, int(2 + 5 * i / n)))


def niebla(img, t, y=1000, alfa=0.35, n=8):
    for i in range(n):
        x = (i * 260 + t * 25) % (W + 600) - 300
        pegar_glow(img, x, y + 60 * math.sin(i), 360, "#a8b4c8", alfa)


def faro(img, t, x=240, y=860, alcance=1400, vel=0.6):
    ang = math.pi + 0.9 * math.sin(t * vel)
    capa = Image.new("L", (W // 4, H // 4), 0)
    d = ImageDraw.Draw(capa)
    a1, a2 = ang - 0.09, ang + 0.09
    d.polygon([(x / 4, y / 4), ((x + alcance * math.cos(a1)) / 4, (y + alcance * math.sin(a1) * 0.25) / 4),
               ((x + alcance * math.cos(a2)) / 4, (y + alcance * math.sin(a2) * 0.25) / 4)], fill=120)
    capa = capa.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    luz = Image.new("RGBA", (W, H), (255, 246, 210, 0))
    luz.putalpha(capa)
    img.alpha_composite(luz)
    pegar_glow(img, x, y, 70, "#fff6d0", 0.9)


def _chaleco(L, col=(176, 156, 80)):
    L.forma([(-95, -110), (-42, -112), (0, -40), (42, -112), (95, -110), (104, -60), (82, -20), (98, 110),
             (-98, 110), (-82, -20), (-104, -60)], col, suave=False, intensidad=0.1)
    L.linea([(0, -40), (0, 110)], TINTA, 5)
    for y in (-10, 40, 85):
        L.linea([(-88, y), (-8, y)], oscuro(col, 0.6), 5)
        L.linea([(8, y), (88, y)], oscuro(col, 0.6), 5)
    for sx in (-1, 1):
        L.forma(elipse(sx * 85, -55, 16, 24), oscuro(col, 0.45), sombra=False, brillo=False, ancho=3)


# =========================================================================== #
# ESCENAS
# =========================================================================== #
class EscenaAlc(EscenaDino):
    def sonidos(self, dur):
        return []


class A1(EscenaAlc):  # gancho: la linterna descubre la cabeza falsa
    camara = (1.0, 1.12, 0.32, 0.62)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_celda()

    def caida(self, t, dur):
        return self.tp("escaparon", 0.3, dur)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        tc = self.caida(t, dur)
        cab = CABEZA_FALSA[3].get(0, 0.62)
        if t < tc:
            x, y, ang = 250, 1150, 0.0
        else:
            q = min(1.0, (t - tc) / 0.7)
            x = 250 - 60 * q
            y = 1150 + 420 * (q ** 2) - 60 * abs(math.sin(min(1.0, (t - tc) / 1.2) * math.pi * 3)) * (1 - q * 0.5)
            ang = -110 * q
        c = cab.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(c, (int(x - c.width / 2), int(y - c.height * 0.62)))
        tx = 300 + 140 * math.sin(t * 1.3) if t < tc else 240
        ty = 1180 if t < tc else min(1580, 1180 + 400 * min(1.0, (t - tc) / 0.7))
        linterna(img, 1250, -100, tx, ty, ancho=250, oscuridad=215)
        barrotes(img)
        tn = self.tp("nunca", 0.85, dur)
        if t > tn:
            a = 0.5 + 0.5 * math.sin((t - tn) * 9)
            img.alpha_composite(Image.new("RGBA", (W, H), (220, 20, 30, int(70 * a))))
            pegar_glow(img, W / 2, 120, 260, "#ff2a2a", 0.6 * a)
        return img

    def sacudida(self, t, dur):
        tc = self.caida(t, dur)
        return 1.2 if tc + 0.55 < t < tc + 0.85 else 0.0

    def encima(self, img, t, dur):
        etiqueta_maquina(img, t, 0.15, "ALCATRAZ · 1962", W / 2, 300)
        ficha(img, t, self.tp("tres", 0.2, dur), "der", 380, "fugitivos", "3 PRESOS", emoji="🔒")
        chip(img, t, self.tp("nunca", 0.85, dur), "¿DÓNDE ESTÁN?", y=760, color=ROJO, tam=56)

    def sonidos(self, dur):
        return [(self.caida(0, dur) + 0.6, "golpe", 0.4), (self.tp("nunca", 0.85, dur), "sirena", 3.0)]


class A2(EscenaAlc):  # la isla
    camara = (1.15, 1.0, 0.5, 0.52)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_isla()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        faro(img, t)
        olas(img, t)
        tc = self.tp("corrientes", 0.55, dur)
        if t > tc:
            d = ImageDraw.Draw(img)
            for i in range(5):
                f = ((t - tc) * 0.6 + i / 5) % 1
                y = 1250 + i * 110
                x0 = -200 + f * (W + 400)
                pts = catmull([(x0 - 160, y), (x0 - 80, y - 25), (x0, y)], 5, cerrado=False)
                d.line(pts, fill=(220, 240, 255, 220), width=8)
                d.polygon([(x0 + 10, y), (x0 - 24, y - 18), (x0 - 20, y + 16)], fill=(220, 240, 255, 220))
        niebla(img, t, 1060, 0.3)
        return img

    def encima(self, img, t, dur):
        etiqueta_maquina(img, t, 0.1, "BAHÍA DE SAN FRANCISCO", W / 2, 300)
        ficha(img, t, self.tp("helada", 0.35, dur), "izq", 400, "agua helada", "10 a 15 °C", emoji="🥶")
        ficha(img, t, self.tp("corrientes", 0.55, dur), "der", 610, "corrientes", "muy fuertes", emoji="🌊")
        sello(img, t, self.tp("imposible", 0.85, dur), "IMPOSIBLE", W / 2, 880, ang=-8, tam=88)

    def sonidos(self, dur):
        return [(0, "olas", dur), (self.tp("imposible", 0.85, dur), "sello", 0.3)]


class A3(EscenaAlc):  # fichas policiales
    camara = (1.0, 1.05, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        img = Image.new("RGBA", (W, H), (205, 208, 212, 255))
        d = ImageDraw.Draw(img)
        for i, y in enumerate(range(560, 1200, 40)):
            d.line((0, y, W, y), fill=(150, 154, 160), width=3 if i % 5 else 6)
            if i % 5 == 0:
                d.text((20, y - 30), f"{7 - i // 5}'", font=maquina(30), fill=(90, 94, 100))
        self.fondo = img
        self.claves = [("frank", "morris", 200, "F. MORRIS"), ("john", "john", 540, "J. ANGLIN"),
                       ("clarence", "clarence", 880, "C. ANGLIN")]

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for palabra, estilo, x, _ in self.claves:
            ta = self.tp(palabra, 0.2, dur)
            if t >= ta:
                RETRATOS[estilo].dibujar(img, x, 1210, 0.88, t, sombra=False)
            else:
                d = ImageDraw.Draw(img)
                d.rounded_rectangle((x - 140, 760, x + 140, 1200), radius=30, outline=(150, 154, 160), width=6)
                d.text((x, 980), "?", font=fuente(120), fill=(150, 154, 160), anchor="mm")
        return img

    def encima(self, img, t, dur):
        for palabra, _, x, nombre in self.claves:
            ta = self.tp(palabra, 0.2, dur)
            if t >= ta:
                etiqueta_maquina(img, t, ta + 0.05, nombre, x, 1250)
                if t - ta < 0.18:
                    img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(230 * (1 - (t - ta) / 0.18)))))
        ficha(img, t, self.tp("meses", 0.85, dur), "izq", 330, "el plan", "durante MESES", emoji="🗓️")

    def sonidos(self, dur):
        s = [(self.tp(p, 0.2, dur), "flash", 0.1) for p, _, _, _ in self.claves]
        return s + [(self.tp("meses", 0.85, dur), "reloj", 2.0)]


class A4(EscenaAlc):  # cucharas y taladro
    camara = (1.0, 1.15, 0.5, 0.48)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(150, 154, 158))
            rnd = random.Random(5)
            for _ in range(900):
                x, y = rnd.randint(0, W), rnd.randint(0, H)
                g = rnd.randint(120, 175)
                L.circulo(x, y, rnd.choice((1.5, 2.5, 3.5)), (g, g + 2, g + 4), borde=False)
            for y in range(0, H, 220):
                L.linea([(0, y), (W, y)], (130, 134, 138), 4)
        self.fondo = _full(dib)

        def mano(L):
            L.forma(capsula((0, 220), (40, 40), 150, 120), (232, 186, 150), intensidad=0.1)
            for i in range(4):
                L.forma(capsula((-40 + i * 28, 70), (-30 + i * 28, -10), 36, 30), (232, 186, 150), ancho=4,
                        intensidad=0.08)
            L.forma(capsula((60, 60), (110, -20), 34, 28), (232, 186, 150), ancho=4, intensidad=0.08)
            L.forma(capsula((0, 30), (-30, -260), 26, 20), (196, 200, 208), intensidad=0.15)
            L.forma(elipse(-34, -290, 34, 46, 0.1), (206, 210, 218), intensidad=0.15)
        Lm = Lienzo(360, 640, 180, 360)
        mano(Lm)
        self.mano = Lm.final()

        def taladro(L):
            L.forma(capsula((-140, 0), (120, 0), 170, 150), (90, 110, 150), intensidad=0.12)
            for i in range(5):
                L.linea([(-90 + i * 40, -50), (-90 + i * 40, 50)], (60, 76, 110), 8)
            L.forma(capsula((120, 0), (190, 0), 70, 60), (70, 70, 80))
            L.forma([(190, -10), (330, -4), (330, 4), (190, 10)], (200, 205, 214), suave=False, ancho=3)
            L.forma(capsula((-60, 70), (-90, 260), 80, 70), (40, 40, 46))
        Lt = Lienzo(560, 460, 230, 180)
        taladro(Lt)
        self.taladro = Lt.final()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        prog = min(1.0, t / dur)
        cx, cy = 540, 860
        d = ImageDraw.Draw(img)
        rw, rh = 230 + 90 * prog, 160 + 70 * prog
        rnd = random.Random(7)
        hueco = [(cx + rw * math.cos(a) * (0.9 + 0.15 * rnd.random()), cy + rh * math.sin(a) * (0.9 + 0.15 * rnd.random()))
                 for a in [i / 16 * 2 * math.pi for i in range(16)]]
        d.polygon(hueco, fill=(28, 26, 26))
        d.line(hueco + [hueco[0]], fill=(100, 100, 102), width=6)
        d.rectangle((cx - 200, cy - 130, cx + 200, cy + 130), fill=(60, 64, 72), outline=TINTA, width=6)
        for i in range(8):
            y = cy - 105 + i * 30
            d.rectangle((cx - 185, y, cx + 185, y + 14), fill=(120, 126, 136), outline=(40, 44, 50), width=2)
        for i in range(int(30 * prog) + 6):  # polvo cayendo
            f = (t * 0.7 + i * 0.137) % 1
            x = cx - rw + (i * 73) % int(2 * rw)
            y = cy + rh + f * 500
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(190, 192, 196, int(255 * (1 - f))))
        t_tal = self.tp("taladro", 0.45, dur)
        if t < t_tal:
            dx = 70 * math.sin(t * 11)
            img.alpha_composite(self.mano, (int(cx + rw - 140 + dx), int(cy + 20)))
        else:
            j = 5 * math.sin(t * 90)
            img.alpha_composite(self.taladro, (int(cx + rw - 60 + j), int(cy + 120 + j)))
            for i in range(8):
                f = (t * 3 + i / 8) % 1
                pegar_glow(img, cx + rw + 10 - 120 * f, cy + 150 - 80 * f + 30 * math.sin(i), 25 + 30 * f, "#c8c8cc",
                           0.7 * (1 - f))
        return img

    def encima(self, img, t, dur):
        ficha(img, t, self.tp("cucharas", 0.1, dur), "izq", 300, "herramienta 1", "cucharas afiladas", emoji="🥄",
              dur=self.tp("taladro", 0.45, dur) - self.tp("cucharas", 0.1, dur) - 0.2)
        ficha(img, t, self.tp("aspiradora", 0.6, dur), "der", 300, "herramienta 2", "motor de aspiradora", emoji="🔌")
        etiqueta_maquina(img, t, self.tp("rejillas", 0.8, dur), "REJILLA DE VENTILACIÓN", W / 2, 1110)

    def sonidos(self, dur):
        t_tal = self.tp("taladro", 0.45, dur)
        return [(0.1, "raspado", t_tal - 0.1), (t_tal, "taladro", dur - t_tal)]


class A5(EscenaAlc):  # cabezas falsas
    camara = (1.0, 1.12, 0.5, 0.52)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (30, 34, 46)), (1, (50, 54, 66))]))
            L.forma([(0, 1150), (W, 1150), (W, H), (0, H)], (120, 84, 54), suave=False, borde=False, intensidad=0.03)
            for y in range(1180, H, 70):
                L.linea([(0, y), (W, y + 12)], (100, 68, 42), 4)
            L.linea([(0, 1150), (W, 1150)], TINTA, 7)
        self.fondo = _full(dib)
        pegar_glow(self.fondo, 540, 500, 500, "#ffe7b0", 0.35)

        def jabon(L):
            L.forma([(-110, -50), (110, -50), (120, 40), (-120, 40)], (240, 232, 236), intensidad=0.12)
            (x, y), = L.P([(0, -5)])
            L.d.text((x, y), "JABÓN", font=maquina(44), fill=(170, 150, 160), anchor="mm")
        Lj = Lienzo(300, 160, 150, 90)
        jabon(Lj)
        self.jabon = Lj.final()

        def papel(L):
            L.forma(elipse(0, 0, 80, 100), (246, 246, 240), intensidad=0.12)
            L.forma(elipse(0, 0, 26, 32), (200, 190, 170), intensidad=0.1)
        Lp = Lienzo(220, 240, 110, 120)
        papel(Lp)
        self.papel = Lp.final()

        def pelo(L):
            for i in range(14):
                L.linea(catmull([(-80 + i * 12, 40), (-60 + i * 12, -10), (-90 + i * 14, -60)], 4, cerrado=False),
                        (40, 32, 30), 6)
        Lh = Lienzo(240, 160, 120, 90)
        pelo(Lh)
        self.pelo = Lh.final()

    def etapa(self, t, dur):
        e = 0
        for i, p in enumerate(("jabon", "papel", "pelo"), 1):
            if t >= self.tp(p, 0.2 + 0.25 * i, dur):
                e = i
        return e

    def mundo(self, t, dur):
        img = self.fondo.copy()
        e = self.etapa(t, dur)
        for i, (obj, x) in enumerate(((self.jabon, 190), (self.papel, 190), (self.pelo, 890))):
            ti = self.tp(("jabon", "papel", "pelo")[i], 0.2 + 0.25 * (i + 1), dur)
            if t >= ti:
                p = pop((t - ti) / 0.3)
                o = obj.resize((max(1, int(obj.width * p)), max(1, int(obj.height * p))), Image.BILINEAR)
                y = 1180 if i != 1 else 980
                img.alpha_composite(o, (int(x - o.width / 2), int(y - o.height / 2)))
        cab = CABEZA_FALSA[e].get(0, 1.15)
        img.alpha_composite(cab, (int(540 - cab.width / 2), int(1180 - cab.height + 30)))
        return img

    def encima(self, img, t, dur):
        ficha(img, t, self.tp("enganar", 0.1, dur), "izq", 280, "objetivo", "engañar a los guardias", emoji="👀")
        for i, (p, txt, x, y) in enumerate((("jabon", "JABÓN", 190, 1290), ("papel", "PAPEL HIGIÉNICO", 230, 1090),
                                            ("pelo", "PELO REAL", 890, 1290))):
            etiqueta_maquina(img, t, self.tp(p, 0.2 + 0.25 * (i + 1), dur) + 0.1, txt, x, y)

    def sonidos(self, dur):
        return [(self.tp(p, 0.2 + 0.25 * i, dur), "pop", 0.2) for i, p in enumerate(("jabon", "papel", "pelo"), 1)]


class A6(EscenaAlc):  # impermeables -> balsa
    camara = (1.0, 1.08, 0.5, 0.55)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (36, 40, 52)), (1, (60, 62, 72))]))
            L.forma([(0, 1450), (W, 1450), (W, H), (0, H)], (82, 84, 92), suave=False, borde=False)
            L.linea([(0, 1450), (W, 1450)], TINTA, 7)
        self.fondo = _full(dib)

        def abrigo(L):
            col = (196, 170, 74)
            L.forma([(-70, -110), (70, -110), (110, 120), (-110, 120)], col, intensidad=0.12)
            L.forma(capsula((-70, -100), (-140, 60), 50, 40), col, intensidad=0.1)
            L.forma(capsula((70, -100), (140, 60), 50, 40), col, intensidad=0.1)
            L.forma(elipse(0, -120, 52, 30), oscuro(col, 0.8), intensidad=0.1)
            L.linea([(0, -90), (0, 115)], oscuro(col, 0.6), 4)
        La = Lienzo(320, 300, 160, 150)
        abrigo(La)
        self.abrigo = La.final()

        def balsa(L):
            col = (176, 156, 80)
            L.forma(catmull([(-330, -40), (-260, -110), (260, -110), (330, -40), (260, 60), (-260, 60)], 4), col,
                    intensidad=0.1)
            L.forma(catmull([(-250, -50), (250, -50), (250, 10), (-250, 10)], 4), oscuro(col, 0.75), sombra=False,
                    brillo=False, ancho=4)
            for x in range(-240, 260, 60):
                L.linea([(x, -100), (x + 6, 50)], oscuro(col, 0.6), 3)
        Lb = Lienzo(720, 260, 360, 140)
        balsa(Lb)
        self.balsa = Lb.final()

        Lc = Lienzo(240, 260, 120, 130)
        _chaleco(Lc)
        self.chaleco = Lc.final()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        tb = self.tp("balsa", 0.6, dur)
        rnd = random.Random(4)
        n = 16
        trans = ease((t - tb) / 0.5) if t > tb else 0.0
        for i in range(n):
            t_i = 0.15 * i
            if t < t_i:
                continue
            f = min(1.0, (t - t_i) / 0.6)
            x = 240 + (i % 5) * 150 + rnd.randint(-30, 30)
            y_fin = 1420 - (i // 5) * 70
            y = -200 + (y_fin + 200) * (f ** 2)
            a = self.abrigo.rotate(rnd.randint(-40, 40) * (1 - f * 0.5), expand=True, resample=Image.BICUBIC)
            if trans > 0:
                a.putalpha(a.getchannel("A").point(lambda v: int(v * (1 - trans))))
            img.alpha_composite(a, (int(x - a.width / 2), int(y - a.height / 2)))
        if trans > 0:
            b = self.balsa.copy()
            b.putalpha(b.getchannel("A").point(lambda v: int(v * trans)))
            img.alpha_composite(b, (int(540 - b.width / 2), int(1330 - b.height / 2)))
        tc = self.tp("chalecos", 0.8, dur)
        for i in range(3):
            if t > tc + i * 0.15:
                p = pop((t - tc - i * 0.15) / 0.3)
                c = self.chaleco.resize((max(1, int(240 * p)), max(1, int(260 * p))), Image.BILINEAR)
                img.alpha_composite(c, (int(280 + i * 260 - c.width / 2), int(1000 - c.height / 2)))
        return img

    def encima(self, img, t, dur):
        numero_gigante(img, t, self.tp("cincuenta", 0.2, dur), "+50", "impermeables robados", y=420, color=AMBAR)
        etiqueta_maquina(img, t, self.tp("balsa", 0.6, dur) + 0.3, "BALSA CASERA", W / 2, 1530)

    def sonidos(self, dur):
        return [(self.tp("balsa", 0.6, dur), "pop", 0.2), (self.tp("chalecos", 0.8, dur), "pop", 0.2)]


class A7(EscenaAlc):  # la noche de la fuga
    camara = (1.0, 1.06, 0.5, 0.55)

    def __init__(self):
        super().__init__()
        self.celda = fondo_celda()
        oscurecer(self.celda, 150)
        self.isla = fondo_isla()

        def techo(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (6, 10, 26)), (1, (26, 36, 62))]))
            rnd = random.Random(8)
            for _ in range(120):
                L.circulo(rnd.randint(0, W), rnd.randint(0, 1100), 2, (230, 230, 255), borde=False)
            L.circulo(200, 300, 80, (240, 238, 220), borde=False)
            L.forma([(0, 1250), (W, 1180), (W, H), (0, H)], (60, 62, 70), suave=False, intensidad=0.04)
            L.forma([(620, 1190), (820, 1180), (820, 1050), (620, 1060)], (80, 84, 94), suave=False, intensidad=0.08)
            L.forma([(900, 1180), (940, 400), (1000, 400), (1040, 1180)], (70, 72, 80), suave=False, intensidad=0.06)
            L.forma([(880, 400), (1060, 400), (1060, 300), (880, 300)], (60, 62, 70), suave=False, intensidad=0.06)
        self.techo = _full(techo)

    def fases(self, dur):
        return self.tp("subieron", 0.45, dur) - 0.15, self.tp("lanzaron", 0.8, dur) - 0.15

    def mundo(self, t, dur):
        t_techo, t_agua = self.fases(dur)
        if t < t_techo:
            img = self.celda.copy()
            cab = CABEZA_FALSA[3].get(0, 0.62)
            img.alpha_composite(cab, (int(250 - cab.width / 2), int(1150 - cab.height * 0.62)))
            barrotes(img)
            return img
        if t < t_agua:
            img = self.techo.copy()
            ang = math.pi * 0.62 + 0.55 * math.sin((t - t_techo) * 1.6)
            capa = Image.new("L", (W // 4, H // 4), 0)
            d4 = ImageDraw.Draw(capa)
            x, y = 970, 350
            d4.polygon([(x / 4, y / 4), ((x + 1800 * math.cos(ang - 0.08)) / 4, (y + 1800 * math.sin(ang - 0.08)) / 4),
                        ((x + 1800 * math.cos(ang + 0.08)) / 4, (y + 1800 * math.sin(ang + 0.08)) / 4)], fill=140)
            capa = capa.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
            luz = Image.new("RGBA", (W, H), (255, 250, 220, 0))
            luz.putalpha(capa)
            img.alpha_composite(luz)
            pegar_glow(img, x, y, 80, "#fff6d0", 0.9)
            d = ImageDraw.Draw(img)
            for i in range(3):
                xx = -150 + (t - t_techo) * 260 + i * 140
                silueta(d, xx, 1230 - xx * 0.065, 1.0, t, fase=i * 1.3)
            return img
        img = self.isla.copy()
        olas(img, t)
        tt = t - t_agua
        d = ImageDraw.Draw(img)
        s = max(0.55, 1.35 - tt * 0.16)
        bx, by = 540 - tt * 30, 1520 - tt * 70
        d.ellipse((bx - 260 * s, by - 45 * s, bx + 260 * s, by + 55 * s), fill=(176, 156, 80), outline=TINTA, width=6)
        d.ellipse((bx - 220 * s, by - 25 * s, bx + 220 * s, by + 25 * s), fill=(140, 122, 60))
        for i in range(3):
            silueta(d, bx - 150 * s + i * 150 * s, by, s * 0.75, t * 0.6, fase=i, agachado=False)
            ang = math.sin(t * 4 + i) * 0.6
            d.line((bx - 150 * s + i * 150 * s, by - 60 * s, bx - 150 * s + i * 150 * s + 90 * s * math.cos(ang),
                    by + 40 * s), fill=(120, 80, 40), width=max(3, int(10 * s)))
        if tt < 0.8:
            for i in range(18):
                a = i / 18 * math.pi
                r = 60 + 300 * tt
                d.ellipse((bx + r * math.cos(a) - 8, by - r * math.sin(a) * 0.6 - 8, bx + r * math.cos(a) + 8,
                           by - r * math.sin(a) * 0.6 + 8), fill=(220, 235, 255, int(255 * (1 - tt / 0.8))))
        niebla(img, t, 1300, 0.4)
        return img

    def encima(self, img, t, dur):
        etiqueta_maquina(img, t, 0.1, "11 DE JUNIO DE 1962", W / 2, 300)
        t_techo, t_agua = self.fases(dur)
        if t < t_techo:
            chip(img, t, self.tp("cabezas", 0.2, dur), "las cabezas, en sus camas", y=720, color=(20, 26, 40), tam=40)
        elif t < t_agua:
            ficha(img, t, t_techo + 0.1, "der", 380, "ruta", "por el techo", emoji="🌙")

    def sonidos(self, dur):
        t_techo, t_agua = self.fases(dur)
        return [(0, "latido", t_agua), (t_agua, "chapuzon", 0.6), (t_agua, "olas", dur - t_agua)]


class A8(EscenaAlc):  # nunca más los vieron
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_isla(amanecer=True)

        def remo(L):
            L.forma(capsula((-260, 0), (120, 0), 22, 22), (150, 104, 60), intensidad=0.15)
            L.forma(elipse(190, 0, 90, 40), (150, 104, 60), intensidad=0.15)
        Lr = Lienzo(600, 140, 300, 70)
        remo(Lr)
        self.remo = Lr.final()

        Lc = Lienzo(240, 260, 120, 130)
        _chaleco(Lc)
        self.chaleco = Lc.final().rotate(70, expand=True, resample=Image.BICUBIC)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        olas(img, t, col=(200, 210, 230), alfa=140)
        for obj, x, y, ph in ((self.remo, 360, 1430, 0), (self.chaleco, 760, 1600, 1.4)):
            ang = 8 * math.sin(t * 1.3 + ph)
            o = obj.rotate(ang, expand=True, resample=Image.BICUBIC)
            img.alpha_composite(o, (int(x - o.width / 2), int(y - o.height / 2 + 12 * math.sin(t * 1.6 + ph))))
        bx = -300 + t * 120
        d = ImageDraw.Draw(img)
        d.polygon([(bx - 150, 1180), (bx + 150, 1180), (bx + 120, 1220), (bx - 130, 1220)], fill=(230, 230, 236),
                  outline=TINTA)
        d.rectangle((bx - 60, 1130, bx + 40, 1180), fill=(210, 214, 222), outline=TINTA, width=4)
        if int(t * 4) % 2 == 0:
            pegar_glow(img, bx - 10, 1120, 60, "#4a7aff", 0.9)
        else:
            pegar_glow(img, bx - 10, 1120, 60, "#ff3a3a", 0.9)
        niebla(img, t, 1150, 0.45, n=10)
        return img

    def encima(self, img, t, dur):
        chip(img, t, 0.15, "NUNCA MÁS LOS VIERON", y=300, color=(20, 26, 40), tam=46)
        ficha(img, t, self.tp("restos", 0.5, dur), "izq", 420, "evidencia", "un remo y un chaleco", emoji="🔍")

    def sonidos(self, dur):
        return [(0, "olas", dur), (0.2, "sirena", 2.5)]


class A9(EscenaAlc):  # la carta de 2013
    camara = (1.0, 1.12, 0.5, 0.5)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (50, 34, 24)), (1, (30, 20, 14))]))
            rnd = random.Random(4)
            for _ in range(40):
                y = rnd.randint(0, H)
                L.linea([(0, y), (W, y + rnd.randint(-20, 20))], (60, 42, 30), 4)
        self.fondo = _full(dib)
        pegar_glow(self.fondo, 300, 300, 700, "#ffd890", 0.4)
        carta = Image.new("RGBA", (700, 900), PAPEL + (255,))
        d = ImageDraw.Draw(carta)
        rnd = random.Random(9)
        for i in range(14):
            y = 150 + i * 48
            x = 60
            while x < 620:
                w = rnd.randint(30, 110)
                pts = [(x + j * w / 8, y + 6 * math.sin(j * 1.7 + i)) for j in range(9)]
                d.line(pts, fill=(40, 50, 90), width=4)
                x += w + 18
        d.text((60, 60), "FBI · San Francisco", font=maquina(30), fill=(90, 70, 50))
        d.line([(380, 820), (430, 790), (470, 830), (520, 780), (580, 820)], fill=(40, 50, 90), width=5)
        self.carta = carta.rotate(-6, expand=True, resample=Image.BICUBIC)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        p = ease(t / 0.8)
        y = 1000 + (1 - p) * 900
        sombra_suave(img, (220, y - 400, 860, y + 470), radio=10, alfa=130, blur=24)
        img.alpha_composite(self.carta, (int(540 - self.carta.width / 2), int(y - self.carta.height / 2)))
        return img

    def encima(self, img, t, dur):
        ficha(img, t, self.tp("carta", 0.2, dur), "izq", 260, "2013 · una carta", "«John Anglin»", emoji="✉️")
        chip(img, t, self.tp("sobrevivido", 0.6, dur), "«Todos lo logramos… por poco»", y=1180,
             color=(20, 26, 40), tam=40)
        sello(img, t, self.tp("comprobar", 0.85, dur), "SIN CONFIRMAR", W / 2, 960, ang=-14, tam=80)

    def sonidos(self, dur):
        return [(self.tp("comprobar", 0.85, dur), "sello", 0.3)]


class A10(EscenaAlc):  # final propio
    camara = (1.0, 1.04, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.celda = fondo_celda()
        oscurecer(self.celda, 120)

        def pared(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (70, 76, 88)), (1, (44, 48, 58))]))
            for y in range(0, H, 110):
                for x in range(-((y // 110) % 2) * 120, W, 240):
                    L.d.rectangle((x * 2, y * 2, (x + 240) * 2, (y + 110) * 2), outline=(58, 63, 74), width=6)
        self.pared = _full(pared)
        self.carteles = []
        for estilo, nombre in (("morris", "FRANK MORRIS"), ("john", "JOHN ANGLIN"), ("clarence", "CLARENCE ANGLIN")):
            c = Image.new("RGBA", (320, 460), PAPEL + (255,))
            d = ImageDraw.Draw(c)
            d.rectangle((0, 0, 319, 459), outline=(120, 100, 70), width=5)
            d.text((160, 52), "SE BUSCA", font=maquina(52), fill=(140, 30, 30), anchor="mm")
            r = RETRATOS[estilo].get(0, 0.6)
            c.alpha_composite(r, (int(160 - r.width / 2), 90))
            d.rectangle((20, 92, 300, 92 + r.height - 4), outline=(80, 60, 40), width=3)
            d.text((160, 405), nombre, font=maquina(26), fill=TINTA, anchor="mm")
            self.carteles.append(c)

    def fases(self, dur):
        return self.tp("caso", 0.35, dur) - 0.2

    def mundo(self, t, dur):
        t_caso = self.fases(dur)
        if t < t_caso:
            img = self.celda.copy()
            q = ease(t / 0.9)
            off = int((1 - q) * W)
            capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            barrotes(capa)
            img.alpha_composite(capa, (off, 0))
            return img
        img = self.pared.copy()
        for i, c in enumerate(self.carteles):
            ti = t_caso + i * 0.15
            if t < ti:
                continue
            p = pop((t - ti) / 0.3)
            cc = c.rotate((-6, 3, -2)[i], expand=True, resample=Image.BICUBIC)
            if p != 1:
                cc = cc.resize((max(1, int(cc.width * p)), max(1, int(cc.height * p))), Image.BILINEAR)
            x, y = (200, 540, 880)[i], (1070, 1010, 1080)[i]
            sombra_suave(img, (x - cc.width / 2 + 10, y - cc.height / 2 + 10, x + cc.width / 2 - 10,
                               y + cc.height / 2 - 10), radio=4, alfa=120)
            img.alpha_composite(cc, (int(x - cc.width / 2), int(y - cc.height / 2)))
        return img

    def sacudida(self, t, dur):
        return 1.0 if 0.8 < t < 1.05 else 0.0

    def encima(self, img, t, dur):
        t_caso = self.fases(dur)
        if t < t_caso:
            etiqueta_maquina(img, t, 0.85, "ALCATRAZ · CERRADA EN 1963", W / 2, 320)
            return
        sello(img, t, t_caso + 0.55, "CASO ABIERTO", W / 2, 1040, ang=-10, tam=100)
        tq = self.tp("crees", 0.55, dur)
        if t > tq:
            p = pop((t - tq) / 0.3)
            d = ImageDraw.Draw(img)
            caja = (W / 2 - 400 * p, 350 - 85 * p, W / 2 + 400 * p, 350 + 85 * p)
            sombra_suave(img, caja, radio=40)
            d.rounded_rectangle(caja, radius=radius_ok(40 * p), fill=(255, 255, 255, 248), outline=TINTA, width=6)
            d.polygon([(W / 2 - 30, 350 + 85 * p - 3), (W / 2 + 30, 350 + 85 * p - 3), (W / 2, 350 + 135 * p)],
                      fill=(255, 255, 255))
            d.text((W / 2, 350), "¿SOBREVIVIERON?", font=fuente(int(70 * p)), fill=TINTA, anchor="mm")
        tc = self.tp("comenta", 0.7, dur)
        if t > tc:
            for i, (txt, col) in enumerate((("SÍ", VERDE), ("NO", ROJO))):
                p = pop((t - tc - i * 0.12) / 0.3)
                if p <= 0.05:
                    continue
                late = 1 + 0.05 * math.sin((t - tc) * 6 + i * 3)
                cx, cy = (330, 750)[i], 600
                r = 95 * p * late
                sombra_suave(img, (cx - r, cy - r, cx + r, cy + r), radio=r, alfa=110)
                d = ImageDraw.Draw(img)
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=BLANCO, width=8)
                d.text((cx, cy), txt, font=fuente(int(72 * p)), fill=BLANCO, anchor="mm", stroke_width=4,
                       stroke_fill=TINTA)
            chip(img, t, tc + 0.3, "COMENTA", y=600, color=(20, 26, 40), tam=34)
        ts = self.tp("suscribete", 0.85, dur)
        if t > ts:
            q = ease((t - ts) / 0.4)
            y = H - 230 + (1 - q) * 300
            d = ImageDraw.Draw(img)
            caja = (90, y, W - 90, y + 130)
            sombra_suave(img, caja, radio=26)
            d.rounded_rectangle(caja, radius=26, fill=(16, 22, 36, 245), outline=CELESTE, width=5)
            em = render_emoji("🔔")
            if em is not None:
                em = em.resize((84, int(84 * em.height / em.width)), Image.LANCZOS)
                em = em.rotate(18 * math.sin((t - ts) * 14) * max(0.0, 1 - (t - ts) / 1.5), expand=True,
                               resample=Image.BICUBIC)
                img.alpha_composite(em, (int(140), int(y + 65 - em.height / 2)))
            d.text((250, y + 65), "SUSCRÍBETE · una historia real cada día", font=fuente(40), fill=BLANCO,
                   anchor="lm")

    def sonidos(self, dur):
        t_caso = self.fases(dur)
        return [(0.8, "reja", 1.0), (t_caso + 0.55, "sello", 0.3), (self.tp("suscribete", 0.85, dur), "pop", 0.2)]


ESCENAS_ALC = {f"alc_{i}": c for i, c in enumerate((A1, A2, A3, A4, A5, A6, A7, A8, A9, A10), 1)}


# =========================================================================== #
# SONIDO
# =========================================================================== #
def _env(m, ataque=0.01, caida=0.2):
    tt = np.arange(m) / SR
    return np.minimum(1, tt / max(ataque, 1e-3)) * np.exp(-tt / max(caida, 1e-3))


def sfx(tipo, dur, rng):
    m = max(1, int(dur * SR))
    tt = np.arange(m) / SR
    if tipo == "golpe":
        x = (np.sin(2 * np.pi * 55 * tt) + ruido_filtrado(m, 30, rng) * 2) * _env(m, 0.003, 0.12) * 0.6
    elif tipo == "sirena":
        f = 650 + 220 * np.sin(2 * np.pi * 0.7 * tt)
        x = np.sin(np.cumsum(2 * np.pi * f / SR)) * 0.06 * np.minimum(1, tt / 0.4) * np.minimum(1, (dur - tt) / 0.6)
    elif tipo == "olas":
        x = ruido_filtrado(m, 40, rng) * 1.6 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.18 * tt)) * 0.12
        x *= np.minimum(1, tt / 0.8) * np.minimum(1, (dur - tt) / 0.8 + 1e-3)
    elif tipo == "sello":
        x = (np.sin(2 * np.pi * 70 * tt) * 0.8 + ruido_filtrado(m, 6, rng) * 0.6) * _env(m, 0.002, 0.07) * 0.55
    elif tipo == "flash":
        m = int(0.25 * SR)
        tt = np.arange(m) / SR
        x = (ruido_filtrado(m, 2, rng) * 0.5 * _env(m, 0.001, 0.02) + np.sin(2 * np.pi * 3200 * tt) * 0.08 *
             _env(m, 0.001, 0.05) + np.sin(2 * np.pi * 900 * tt) * 0.15 * np.exp(-((tt - 0.12) / 0.03) ** 2))
    elif tipo == "reloj":
        x = np.zeros(m)
        for k in range(int(dur * 2)):
            s = int(k * 0.5 * SR)
            n = int(0.03 * SR)
            if s + n < m:
                x[s:s + n] += ruido_filtrado(n, 2, rng) * 0.35 * _env(n, 0.001, 0.008)
    elif tipo == "raspado":
        x = ruido_filtrado(m, 3, rng) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.75 * tt) ** 2) * 0.09
    elif tipo == "taladro":
        f = 140 + 10 * np.sin(2 * np.pi * 7 * tt)
        fase = np.cumsum(2 * np.pi * f / SR)
        x = (2 * (fase / (2 * np.pi) % 1) - 1) * 0.06 + ruido_filtrado(m, 4, rng) * 0.04
        x *= np.minimum(1, tt / 0.15) * np.minimum(1, (dur - tt) / 0.2 + 1e-3)
    elif tipo == "pop":
        m = int(0.18 * SR)
        tt = np.arange(m) / SR
        x = np.sin(2 * np.pi * (500 + 900 * tt / 0.18) * tt) * _env(m, 0.002, 0.05) * 0.25
    elif tipo == "latido":
        x = np.zeros(m)
        for k in range(int(dur / 0.85) + 1):
            for off, amp in ((0.0, 1.0), (0.22, 0.7)):
                s = int((k * 0.85 + off) * SR)
                n = int(0.2 * SR)
                if s + n < m:
                    x[s:s + n] += np.sin(2 * np.pi * 48 * np.arange(n) / SR) * _env(n, 0.005, 0.06) * 0.45 * amp
    elif tipo == "chapuzon":
        x = ruido_filtrado(m, 10, rng) * 2 * _env(m, 0.01, 0.25) * 0.5
    elif tipo == "reja":
        x = sum(np.sin(2 * np.pi * f * tt) * a for f, a in ((523, 0.3), (1187, 0.2), (1729, 0.15), (2410, 0.1)))
        x = x * _env(m, 0.002, 0.35) * 0.5 + np.sin(2 * np.pi * 60 * tt) * _env(m, 0.002, 0.1) * 0.5
    else:
        x = np.zeros(m)
    return x.astype(np.float32)


def mezclar(voz, cortes, eventos, total):
    n = int(total * SR) + SR
    mix = np.zeros((n, 2), np.float32)
    mix[:len(voz)] += voz[:n]
    rng = np.random.default_rng(12)
    tt = np.arange(n) / SR
    pad = (np.sin(2 * np.pi * 49 * tt) + 0.6 * np.sin(2 * np.pi * 73.4 * tt) + 0.35 * np.sin(2 * np.pi * 98 * tt + 1))
    pad *= 0.02 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * tt)) * np.clip(tt / 2, 0, 1)
    mix += pad[:, None]
    for c in cortes:
        m = int(0.45 * SR)
        s = int((c - 0.25) * SR)
        if s >= 0:
            w = ruido_filtrado(m, 5, rng) * np.sin(np.linspace(0, np.pi, m)) ** 2 * 0.13
            mix[s:s + m] += w[:len(mix[s:s + m])][:, None]
    for t0, tipo, dur in eventos:
        s = int(max(0.0, t0) * SR)
        if s >= n or dur <= 0:
            continue
        x = sfx(tipo, dur, rng)
        seg = mix[s:s + len(x)]
        seg += x[:len(seg)][:, None]
    pico = np.abs(mix).max()
    if pico > 0.97:
        mix *= 0.97 / pico
    return mix


# =========================================================================== #
# MONTAJE
# =========================================================================== #
def generar(ruta_json: Path, audio_usuario=None, sin_audio=False):
    cfg = json.loads(ruta_json.read_text(encoding="utf-8"))
    nombre = ruta_json.stem + "_pro"
    print(f"▶ {nombre}")
    tmp = Path(tempfile.mkdtemp(prefix="alc_"))
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
        escenas[-1]["dur"] += 1.8
        total = escenas[-1]["inicio"] + escenas[-1]["dur"]
        eventos = []
        for e in escenas:
            e["grupos"] = agrupar_palabras(e["palabras"], max_palabras=3, max_chars=20)
            e["obj"] = ESCENAS_ALC[e["visual"]]()
            e["obj"].palabras = e["palabras"]
            eventos += [(e["inicio"] + t0, tipo, d) for t0, tipo, d in e["obj"].sonidos(e["dur"])]
        escribir_wav(tmp / "mezcla.wav", mezclar(leer_wav(tmp / "voz.wav"), [e["inicio"] for e in escenas[1:]],
                                                 eventos, total))
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
            a = np.clip(np.asarray(img.convert("RGB"), np.float32) * VINETA, 0, 255).astype(np.uint8)
            if idx > 0 and tl < 0.2:
                a = barrido(a, 1 - tl / 0.2, 1 if idx % 2 else -1)
            for corte in ([o.fases(e["dur"])] if e["visual"] == "alc_10" else
                          list(o.fases(e["dur"])) if e["visual"] == "alc_7" else []):
                if 0 <= tl - corte < 0.2:
                    a = barrido(a, 1 - (tl - corte) / 0.2, -1)
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
