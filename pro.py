"""
Motor común para los videos "pro" (historias 13 en adelante).

Reúne: subtítulos con varios estilos, recuadros con 5 diseños distintos, texto manuscrito que se escribe solo,
aviones, montañas, clima (lluvia, nieve, relámpagos), efectos de sonido ampliados (incluye una cajita musical)
y el montaje completo sincronizado con la voz.
"""
from __future__ import annotations

import json
import math
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from alcatraz import EscenaAlc, maquina, sfx as sfx_base
from caricatura import ease, pop
from cine import SR, _primera_existente, alinear_audio, escribir_wav, fuente, leer_wav, pegar_glow, ruido_filtrado
from dinos import (TINTA, VINETA, Lienzo, _grad, barrido, camara, capsula, catmull, elipse, oscuro, claro,
                   radius_ok, sombra_suave)
from generar_short import FPS, H, W, agrupar_palabras, narrar, render_emoji

RAIZ = Path(__file__).resolve().parent
BLANCO = (255, 255, 255)

_MAN = [str(RAIZ / "fuentes" / "manuscrita.ttf"), "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf", "C:/Windows/Fonts/segoesc.ttf",
        "C:/Windows/Fonts/georgiaz.ttf", "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf"]
_man_cache: dict = {}


def manuscrita(tam):
    if tam not in _man_cache:
        r = _primera_existente(_MAN)
        _man_cache[tam] = ImageFont.truetype(r, tam) if r else fuente(tam)
    return _man_cache[tam]


class Escena(EscenaAlc):
    """Base: tp(palabra) para sincronizar, sonidos(), cortes() para barridos internos."""

    def cortes(self, dur):
        return []


# =========================================================================== #
# SUBTÍTULOS
# =========================================================================== #
def subtitulo(img, grupos, t, estilo, y=1365):
    grupo = None
    for i, g in enumerate(grupos):
        fin = grupos[i + 1][0].inicio if i + 1 < len(grupos) else 1e9
        if g[0].inicio - 0.04 <= t < fin:
            grupo = g
            break
    if not grupo:
        return
    f, fa = fuente(74), fuente(84)
    d = ImageDraw.Draw(img)
    pal = [p.texto.strip(",.;:«»¿?¡!").upper() for p in grupo]
    activa = max([i for i, p in enumerate(grupo) if t >= p.inicio - 0.03] or [0])
    anchos = [d.textlength(w, font=fa if i == activa else f) for i, w in enumerate(pal)]
    esp = 24
    if sum(anchos) + esp * (len(pal) - 1) > W - 120:
        f, fa = fuente(60), fuente(68)
        anchos = [d.textlength(w, font=fa if i == activa else f) for i, w in enumerate(pal)]
    total = sum(anchos) + esp * (len(pal) - 1)
    x = (W - total) / 2
    yy = y + (1 - pop((t - grupo[0].inicio + 0.04) / 0.15)) * 22
    sombra = Image.new("RGBA", (W, 220), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sombra)
    xs = x
    for i, w in enumerate(pal):
        sd.text((xs, 110), w, font=fa if i == activa else f, fill=(0, 0, 0, 190), anchor="lm", stroke_width=12,
                stroke_fill=(0, 0, 0, 190))
        xs += anchos[i] + esp
    img.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(9)), (0, int(yy - 100)))
    for i, w in enumerate(pal):
        fnt = fa if i == activa else f
        if i == activa and estilo.get("modo") == "caja":
            bx0, bx1 = x - 14, x + anchos[i] + 14
            d.rounded_rectangle((bx0, yy - 52, bx1, yy + 50), radius=16, fill=estilo["caja"], outline=TINTA,
                                width=5)
            d.text((x, yy - 2), w, font=fnt, fill=estilo.get("texto", TINTA), anchor="lm")
        else:
            col = estilo["color"] if i == activa else BLANCO
            d.text((x, yy - (5 if i == activa else 0)), w, font=fnt, fill=col, anchor="lm", stroke_width=8,
                   stroke_fill=(12, 12, 18))
        x += anchos[i] + esp


# =========================================================================== #
# RECUADROS (5 diseños)
# =========================================================================== #
def _cuerpo_tarjeta(estilo, w, h, titulo, valor, emoji):
    capa = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ox, oy = 20, 20
    ft, fv = maquina(28), fuente(60)
    tx = 150 if emoji else 44
    col_t, col_v = (110, 100, 90), TINTA
    if estilo == "boleto":  # pase de abordar años 70
        d.rounded_rectangle((ox, oy, ox + w, oy + h), radius=18, fill=(250, 242, 224), outline=TINTA, width=5)
        d.rounded_rectangle((ox, oy, ox + 34, oy + h), radius=14, fill=(230, 120, 50))
        d.rectangle((ox + 20, oy, ox + 34, oy + h), fill=(230, 120, 50))
        for yy in range(oy + 12, oy + h - 8, 18):
            d.line((ox + w - 120, yy, ox + w - 120, yy + 9), fill=(160, 150, 130), width=3)
        d.text((ox + w - 60, oy + h / 2), "✈" if False else "305", font=maquina(30), fill=(42, 127, 134),
               anchor="mm")
        col_t = (42, 127, 134)
    elif estilo == "placa":  # placa metálica con franja de peligro
        d.rectangle((ox, oy, ox + w, oy + h), fill=(70, 74, 80), outline=TINTA, width=5)
        for i in range(-2, w // 30 + 2):
            x0 = ox + i * 30
            d.polygon([(x0, oy), (x0 + 15, oy), (x0 + 5, oy + 22), (x0 - 10, oy + 22)], fill=(250, 200, 30))
        d.rectangle((ox, oy, ox + w, oy + 22), outline=TINTA, width=3)
        for bx, by in ((ox + 14, oy + 36), (ox + w - 14, oy + 36), (ox + 14, oy + h - 14), (ox + w - 14, oy + h - 14)):
            d.ellipse((bx - 7, by - 7, bx + 7, by + 7), fill=(150, 154, 160), outline=TINTA, width=2)
        col_t, col_v = (250, 200, 30), BLANCO
    elif estilo == "nota":  # hoja de cuaderno arrancada
        pts = [(ox, oy + 8)] + [(ox + x, oy + (8 if (x // 22) % 2 else 0)) for x in range(0, w + 1, 22)] + \
              [(ox + w, oy + h), (ox, oy + h)]
        d.polygon(pts, fill=(250, 250, 244), outline=(150, 150, 150))
        for yy in range(oy + 50, oy + h, 34):
            d.line((ox + 10, yy, ox + w - 10, yy), fill=(170, 200, 235), width=2)
        d.line((ox + 34, oy + 10, ox + 34, oy + h), fill=(235, 120, 120), width=3)
        ft, fv = manuscrita(32), manuscrita(64)
        col_t, col_v = (90, 90, 110), (30, 40, 90)
    elif estilo == "diario":  # libreta de campo de bióloga
        d.rectangle((ox, oy, ox + w, oy + h), fill=(232, 222, 190), outline=(90, 70, 40), width=5)
        for xx in range(ox + 20, ox + w, 26):
            d.line((xx, oy + 6, xx, oy + h - 6), fill=(220, 208, 172), width=2)
        for yy in range(oy + 20, oy + h, 26):
            d.line((ox + 6, yy, ox + w - 6, yy), fill=(220, 208, 172), width=2)
        d.rectangle((ox + w - 46, oy - 14, ox + w - 18, oy + 40), fill=(60, 130, 70), outline=TINTA, width=3)
        fv = manuscrita(60)
        col_t, col_v = (60, 110, 60), (40, 50, 30)
    elif estilo == "navidad":  # tarjeta navideña antigua
        d.rectangle((ox, oy, ox + w, oy + h), fill=(250, 244, 228), outline=(170, 30, 40), width=8)
        d.rectangle((ox + 12, oy + 12, ox + w - 12, oy + h - 12), outline=(200, 170, 90), width=3)
        for cx in (ox + w - 40,):
            for dx, dy in ((-16, 0), (16, 0)):
                d.ellipse((cx + dx - 18, oy + 30 + dy - 10, cx + dx + 18, oy + 30 + dy + 10), fill=(40, 120, 60))
            d.ellipse((cx - 9, oy + 22, cx + 9, oy + 40), fill=(200, 30, 40))
        fv = manuscrita(60)
        col_t, col_v = (170, 30, 40), (40, 30, 30)
    if emoji:
        em = render_emoji(emoji)
        if em is not None:
            em = em.resize((90, int(90 * em.height / em.width)), Image.LANCZOS)
            capa.alpha_composite(em, (ox + 50, int(oy + (h - em.height) / 2)))
    d.text((ox + tx, oy + 34), titulo.upper(), font=ft, fill=col_t)
    d.text((ox + tx, oy + 74), valor, font=fv, fill=col_v)
    return capa


def tarjeta(img, t, t0, lado, y, titulo, valor, estilo, emoji=None, dur=None, giro=None):
    if t < t0 or (dur is not None and t > t0 + dur + 0.3):
        return
    p = pop((t - t0) / 0.32)
    salida = 1.0 if dur is None else max(0.0, min(1.0, (t0 + dur + 0.3 - t) / 0.3))
    medidor = ImageDraw.Draw(img)
    fv = manuscrita(64) if estilo in ("nota", "diario", "navidad") else fuente(60)
    ft = manuscrita(32) if estilo == "nota" else maquina(28)
    tx = 150 if emoji else 44
    extra = 130 if estilo == "boleto" else 40
    w = int(max(medidor.textlength(valor, font=fv), medidor.textlength(titulo.upper(), font=ft)) + tx + extra)
    capa = _cuerpo_tarjeta(estilo, w, 170, titulo, valor, emoji)
    ang = giro if giro is not None else (2 if lado == "izq" else -2)
    capa = capa.rotate(ang, expand=True, resample=Image.BICUBIC)
    margen = 26
    if lado == "izq":
        x = margen - (1 - p) * (capa.width + 80) - (1 - salida) * (capa.width + 80)
    elif lado == "der":
        x = W - margen - capa.width + (1 - p) * (capa.width + 80) + (1 - salida) * (capa.width + 80)
    else:
        x = (W - capa.width) / 2
        y = y - (1 - p) * 300
    sombra_suave(img, (x + 20, y + 20, x + capa.width - 20, y + capa.height - 20), radio=10, alfa=120)
    img.alpha_composite(capa, (int(x), int(y)))


def numero(img, t, t0, txt, sub=None, y=470, color=(255, 210, 60), tam=170):
    if t < t0:
        return
    p = pop((t - t0) / 0.35)
    base = tam
    while base > 60 and ImageDraw.Draw(img).textlength(txt, font=fuente(base)) > W - 110:
        base -= 8
    tm = max(10, int(base * p))
    capa = Image.new("RGBA", (W, tm + 160), (0, 0, 0, 0))
    ImageDraw.Draw(capa).text((W / 2, tm / 2 + 50), txt, font=fuente(tm), fill=(0, 0, 0, 170), anchor="mm",
                              stroke_width=14, stroke_fill=(0, 0, 0, 170))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(10)), (0, int(y - tm / 2 - 50)))
    d = ImageDraw.Draw(img)
    d.text((W / 2, y), txt, font=fuente(tm), fill=color, anchor="mm", stroke_width=10, stroke_fill=TINTA)
    if sub:
        d.text((W / 2, y + tm * 0.64), sub, font=fuente(max(10, int(44 * p))), fill=BLANCO, anchor="mm",
               stroke_width=6, stroke_fill=TINTA)


def chip(img, t, t0, txt, y=300, fondo=(20, 22, 30), color=BLANCO, tam=44, dur=None, x=None):
    if t < t0 or (dur is not None and t > t0 + dur):
        return
    p = pop((t - t0) / 0.3)
    f = fuente(max(8, int(tam * p)))
    d = ImageDraw.Draw(img)
    w = d.textlength(txt, font=f) + 70
    h = tam * p + 44
    cx = W / 2 if x is None else x
    caja = (cx - w / 2, y - h / 2, cx + w / 2, y + h / 2)
    sombra_suave(img, caja, radio=h / 2, alfa=90)
    d.rounded_rectangle(caja, radius=radius_ok(h / 2), fill=fondo + (240,), outline=BLANCO, width=4)
    d.text((cx, y), txt, font=f, fill=color, anchor="mm")


def papel_manuscrito(img, t, t0, lineas, x, y, w, h, vel=22, tam=54, color=(170, 20, 30), fondo=(250, 246, 232),
                     giro=-3, rayado=True):
    """Hoja de papel donde el texto se va escribiendo a mano."""
    if t < t0:
        return
    p = pop((t - t0) / 0.35)
    capa = Image.new("RGBA", (w, h), fondo + (255,))
    d = ImageDraw.Draw(capa)
    d.rectangle((0, 0, w - 1, h - 1), outline=(160, 150, 130), width=4)
    if rayado:
        for yy in range(70, h, 64):
            d.line((20, yy, w - 20, yy), fill=(200, 210, 230), width=2)
    n = int(max(0.0, t - t0 - 0.3) * vel)
    f = manuscrita(tam)
    yy = 30
    for ln in lineas:
        vis = ln[:max(0, n)]
        n -= len(ln)
        d.text((30, yy), vis, font=f, fill=color)
        yy += int(tam * 1.18)
    capa = capa.rotate(giro, expand=True, resample=Image.BICUBIC)
    if p != 1:
        capa = capa.resize((max(1, int(capa.width * p)), max(1, int(capa.height * p))), Image.BILINEAR)
    sombra_suave(img, (x - capa.width / 2 + 10, y - capa.height / 2 + 10, x + capa.width / 2 - 10,
                       y + capa.height / 2 - 10), radio=6, alfa=120, blur=20)
    img.alpha_composite(capa, (int(x - capa.width / 2), int(y - capa.height / 2)))


# =========================================================================== #
# ELEMENTOS COMUNES
# =========================================================================== #
def full(dib):
    L = Lienzo(W, H, 0, 0)
    dib(L)
    return L.final()


def cielo(paradas):
    return _grad(W, H, paradas)


def montanas(L, base, picos, color, nieve=True, borde=True):
    for x0, ancho, alto in picos:
        pts = [(x0 - ancho / 2, base), (x0 - ancho * 0.15, base - alto * 0.85), (x0, base - alto),
               (x0 + ancho * 0.2, base - alto * 0.8), (x0 + ancho / 2, base)]
        L.forma(pts, color, suave=False, borde=borde, intensidad=0.06)
        if nieve:
            L.forma([(x0 - ancho * 0.12, base - alto * 0.86), (x0, base - alto), (x0 + ancho * 0.17, base - alto * 0.83),
                     (x0 + ancho * 0.08, base - alto * 0.78), (x0, base - alto * 0.84), (x0 - ancho * 0.06, base - alto * 0.8)],
                    (246, 248, 252), suave=False, borde=False, sombra=False, brillo=False)


def particulas(img, t, tipo="nieve", n=80, vel=1.0, viento=0.0, semilla=1, alfa=255):
    d = ImageDraw.Draw(img)
    r = random.Random(semilla)
    for _ in range(n):
        x0, y0 = r.uniform(0, W), r.uniform(0, H)
        if tipo == "nieve":
            v = r.uniform(60, 160) * vel
            x = (x0 + viento * t + 25 * math.sin(t + x0)) % W
            y = (y0 + v * t) % H
            rr = r.choice((3, 4, 6))
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 255, alfa))
        elif tipo == "lluvia":
            v = r.uniform(1400, 2000) * vel
            x = (x0 + viento * t) % W
            y = (y0 + v * t) % H
            d.line((x, y, x + viento * 0.02, y + 40), fill=(200, 215, 235, int(alfa * 0.6)), width=3)
        elif tipo == "ceniza":
            v = r.uniform(30, 80) * vel
            x = (x0 + 30 * math.sin(t * 0.7 + x0)) % W
            y = (y0 + v * t) % H
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(200, 190, 180, alfa))


def relampago(img, t, t0, dur=0.35):
    if t0 <= t < t0 + dur:
        k = 1 - (t - t0) / dur
        if int((t - t0) * 30) % 3 != 1:
            img.alpha_composite(Image.new("RGBA", (W, H), (235, 240, 255, int(200 * k))))


_aviones: dict = {}


def avion(tipo, escalera=0.0, roto=False, partido=0.0):
    """Sprite de avión de perfil mirando a la derecha. tipo: '727' | 'helice' | 'electra'."""
    clave = (tipo, round(escalera, 2), roto, round(partido, 2))
    if clave in _aviones:
        return _aviones[clave]
    L = Lienzo(1000, 420, 500, 230)
    col = (232, 234, 238)
    franja = {"727": (230, 120, 50), "helice": (50, 90, 160), "electra": (200, 60, 50)}[tipo]
    off = partido * 60
    # fuselaje (posiblemente partido en dos)
    if tipo == "727":
        L.forma([(-330 + 20, 90), (-330, -250), (-260, -250), (-190, -70)], col, suave=False)  # cola en T
        L.forma([(-360, -250), (-200, -250), (-200, -228), (-360, -228)], col, suave=False)
        for dy in (-70, -10):
            L.forma(capsula((-330, dy), (-180, dy), 56, 56), (200, 204, 210))
    else:
        L.forma([(-330 + 20, 40), (-340, -190), (-280, -190), (-190, -40)], col, suave=False)
        L.forma([(-380, -20), (-220, -20), (-220, 4), (-380, 4)], col, suave=False)
    fus_izq = [(-400, 20), (-300, -60), (40 - off, -70), (40 - off, 60), (-300, 60)]
    fus_der = [(40 + off, -70), (330 + off, -66), (430 + off, -10), (420 + off, 40), (330 + off, 62), (40 + off, 60)]
    if roto or partido > 0:
        L.forma(fus_izq, col, intensidad=0.08)
        L.forma(fus_der, col, intensidad=0.08)
    else:
        L.forma(fus_izq[:2] + [(330, -66), (430, -10), (420, 40), (330, 62)] + fus_izq[-1:], col, intensidad=0.08)
    L.linea([(-380, 8), (420, 8)], franja, 12)
    for i in range(14):
        x = -240 + i * 42
        if abs(x - 40) > 40 or not (roto or partido > 0):
            L.circulo(x + (off if x > 40 else -off), -24, 9, (90, 140, 190), borde=True, ancho=2)
    L.forma([(372 + off, -40), (414 + off, -36), (420 + off, -14), (380 + off, -18)], (70, 110, 160), suave=False,
            ancho=3)
    # ala
    if tipo == "helice":
        L.forma([(-80, -76), (150, -76), (170, -60), (-80, -60)], col, suave=False)
        for ex in (-10, 110):
            L.forma(capsula((ex, -72), (ex + 70, -72), 36, 30), (180, 184, 190))
            L.linea([(ex + 88, -110), (ex + 88, -34)], (60, 60, 64), 6)
    elif tipo == "electra":
        L.forma([(-80, 20), (160, 20), (190, 40), (-80, 40)], col, suave=False)
        for ex in (-40, 40, 110):
            L.forma(capsula((ex, 30), (ex + 60, 30), 34, 30), (180, 184, 190))
            L.linea([(ex + 76, -4), (ex + 76, 64)], (60, 60, 64), 6)
    else:
        L.forma([(-60, 20), (150, 20), (200, 50), (-60, 50)], col, suave=False)
    if escalera > 0:  # escalera trasera del 727 bajando
        a = math.radians(70 * escalera)
        bx, by = -300, 60
        ex, ey = bx - 170 * math.cos(a) * 0.3, by + 170 * math.sin(a)
        L.forma([(bx, by - 8), (bx + 20, by + 2), (ex + 20, ey + 6), (ex, ey)], (150, 154, 160), suave=False, ancho=4)
    _aviones[clave] = L.final()
    return _aviones[clave]


def dibujar_avion(img, tipo, x, y, s=1.0, ang=0.0, **kw):
    a = avion(tipo, **kw)
    if s != 1:
        a = a.resize((max(1, int(a.width * s)), max(1, int(a.height * s))), Image.BICUBIC)
    if ang:
        a = a.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(a, (int(x - a.width / 2), int(y - a.height / 2)))


def bandera(img, x, y, w, h, t, tipo="chile", fase=0.0):
    capa = Image.new("RGBA", (int(w) + 40, int(h) + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    franjas = 24
    for i in range(franjas):
        x0 = 20 + w * i / franjas
        x1 = 20 + w * (i + 1) / franjas
        dy = 12 * math.sin(t * 5 + i * 0.5 + fase) * (i / franjas)
        u = (i + 0.5) / franjas
        if tipo == "chile":
            d.rectangle((x0, 40 + dy, x1 + 1, 40 + dy + h / 2), fill=(245, 245, 245) if u > 1 / 3 else (40, 60, 160))
            d.rectangle((x0, 40 + dy + h / 2, x1 + 1, 40 + dy + h), fill=(214, 40, 50))
            if u <= 1 / 3:
                cx, cy = 20 + w / 6, 40 + h / 4
                if x0 <= cx <= x1 + 1:
                    d.regular_polygon((cx, cy + dy, h / 8), 5, fill=(255, 255, 255))
        elif tipo == "alemania":
            for k, c in enumerate(((20, 20, 20), (245, 245, 245), (214, 40, 50))):
                d.rectangle((x0, 40 + dy + h * k / 3, x1 + 1, 40 + dy + h * (k + 1) / 3), fill=c)
        elif tipo == "reino":
            d.rectangle((x0, 40 + dy, x1 + 1, 40 + dy + h), fill=(30, 50, 130))
            if abs(u - 0.5) < 0.09:
                d.rectangle((x0, 40 + dy, x1 + 1, 40 + dy + h), fill=(245, 245, 245))
            if abs(u - 0.5) < 0.05:
                d.rectangle((x0, 40 + dy, x1 + 1, 40 + dy + h), fill=(210, 30, 40))
            d.rectangle((x0, 40 + dy + h * 0.41, x1 + 1, 40 + dy + h * 0.59), fill=(245, 245, 245))
            d.rectangle((x0, 40 + dy + h * 0.45, x1 + 1, 40 + dy + h * 0.55), fill=(210, 30, 40))
    img.alpha_composite(capa, (int(x - 20), int(y - 40)))
    ImageDraw.Draw(img).line((x - 6, y - 10, x - 6, y + h + 400), fill=(90, 70, 50), width=10)


# =========================================================================== #
# SONIDO AMPLIADO
# =========================================================================== #
NOCHE_DE_PAZ = [("G4", 1.5), ("A4", .5), ("G4", 1), ("E4", 3), ("G4", 1.5), ("A4", .5), ("G4", 1), ("E4", 3),
                ("D5", 2), ("D5", 1), ("B4", 3), ("C5", 2), ("C5", 1), ("G4", 3), ("A4", 2), ("A4", 1), ("C5", 1.5),
                ("B4", .5), ("A4", 1), ("G4", 1.5), ("A4", .5), ("G4", 1), ("E4", 3), ("A4", 2), ("A4", 1),
                ("C5", 1.5), ("B4", .5), ("A4", 1), ("G4", 1.5), ("A4", .5), ("G4", 1), ("E4", 3), ("D5", 2),
                ("D5", 1), ("F5", 1.5), ("D5", .5), ("B4", 1), ("C5", 3), ("E5", 3), ("C5", 1.5), ("G4", .5),
                ("E4", 1), ("G4", 1.5), ("F4", .5), ("D4", 1), ("C4", 6)]
_NOTAS = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def _freq(n):
    return 440 * 2 ** ((_NOTAS[n[0]] + (int(n[1]) - 4) * 12) / 12)


def sfx(tipo, dur, rng):
    m = max(1, int(dur * SR))
    tt = np.arange(m) / SR
    fade = np.minimum(1, tt / 0.4) * np.minimum(1, (dur - tt) / 0.5 + 1e-3)
    if tipo == "motor":
        x = (np.sin(2 * np.pi * 95 * tt) * 0.4 + ruido_filtrado(m, 25, rng) * 1.2) * 0.07 * fade
    elif tipo == "viento":
        x = ruido_filtrado(m, 14, rng) * 1.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * tt)) * 0.14 * fade
    elif tipo == "lluvia":
        x = ruido_filtrado(m, 2, rng) * 0.08 * fade
    elif tipo == "trueno":
        x = (ruido_filtrado(m, 90, rng) * 5 + np.sin(2 * np.pi * 40 * tt)) * np.exp(-tt * 1.2) * \
            np.minimum(1, tt / 0.05) * 0.4
    elif tipo == "billetes":
        x = ruido_filtrado(m, 2, rng) * (np.sin(2 * np.pi * 9 * tt) > 0.3) * 0.18 * fade
    elif tipo == "derrumbe":
        x = (ruido_filtrado(m, 120, rng) * 4 + ruido_filtrado(m, 10, rng)) * np.exp(-tt * 0.7) * 0.4
    elif tipo == "perforadora":
        x = (np.sign(np.sin(2 * np.pi * 38 * tt)) * 0.3 + ruido_filtrado(m, 6, rng)) * 0.07 * fade
    elif tipo == "aplausos":
        x = np.zeros(m)
        for _ in range(int(dur * 60)):
            s = rng.integers(0, max(1, m - 800))
            x[s:s + 800] += ruido_filtrado(800, 2, rng) * np.exp(-np.arange(800) / 120) * 0.25
        x *= fade
    elif tipo == "estatica":
        x = rng.normal(0, 1, m) * 0.05 * (0.5 + 0.5 * (np.sin(2 * np.pi * 3 * tt) > 0)) * fade
    elif tipo == "avalancha":
        x = ruido_filtrado(m, 60, rng) * 4 * np.minimum(1, tt / 0.8) * np.exp(-np.maximum(0, tt - 1.5)) * 0.35
    elif tipo == "rio":
        x = ruido_filtrado(m, 6, rng) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * tt)) * 0.06 * fade
    elif tipo == "insectos":
        x = np.sin(2 * np.pi * 4200 * tt) * (np.sin(2 * np.pi * 28 * tt) > 0.6) * 0.015 * fade
    elif tipo == "helicoptero":
        x = ruido_filtrado(m, 30, rng) * 3 * (np.sin(2 * np.pi * 14 * tt) > 0.2) * 0.12 * fade
    elif tipo == "patada":
        x = np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 30) * 0.5
    elif tipo == "teclas":
        x = np.zeros(m)
        for k in range(int(dur * 9)):
            s = int(k / 9 * SR + rng.integers(0, 1500))
            if s + 600 < m:
                x[s:s + 600] += ruido_filtrado(600, 2, rng) * np.exp(-np.arange(600) / 80) * 0.4
    elif tipo == "cajita":
        x = np.zeros(m)
        beat = 0.42
        pos = 0.0
        i = 0
        while pos < dur:
            nota, dd = NOCHE_DE_PAZ[i % len(NOCHE_DE_PAZ)]
            s = int(pos * SR)
            n = int(min(dd * beat + 1.2, dur - pos) * SR)
            if n > 0:
                ttn = np.arange(n) / SR
                fq = _freq(nota) * 2
                x[s:s + n] += (np.sin(2 * np.pi * fq * ttn) + 0.4 * np.sin(2 * np.pi * fq * 2 * ttn)) * \
                    np.exp(-ttn * 2.5) * 0.06
            pos += dd * beat
            i += 1
        x *= fade
    elif tipo == "explosion_lejana":
        x = ruido_filtrado(m, 150, rng) * 5 * np.exp(-tt * 2) * 0.15
    else:
        return sfx_base(tipo, dur, rng)
    return x.astype(np.float32)


def mezclar(voz, cortes, eventos, total, pad_hz=(49, 73.4, 98)):
    n = int(total * SR) + SR
    mix = np.zeros((n, 2), np.float32)
    mix[:len(voz)] += voz[:n]
    rng = np.random.default_rng(21)
    tt = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * f * tt + i) * a for i, (f, a) in enumerate(zip(pad_hz, (1, 0.6, 0.35))))
    pad *= 0.018 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * tt)) * np.clip(tt / 2, 0, 1)
    mix += pad[:, None]
    for c in cortes:
        m = int(0.45 * SR)
        s = int((c - 0.25) * SR)
        if s >= 0:
            w = ruido_filtrado(m, 5, rng) * np.sin(np.linspace(0, np.pi, m)) ** 2 * 0.12
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
def generar(ruta_json: Path, escenas_dict, estilo_sub, audio_usuario=None, sin_audio=False, cola=1.9,
            pad_hz=(49, 73.4, 98)):
    cfg = json.loads(Path(ruta_json).read_text(encoding="utf-8"))
    nombre = Path(ruta_json).stem + "_pro"
    print(f"▶ {nombre}")
    tmp = Path(tempfile.mkdtemp(prefix="pro_"))
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
        escenas[-1]["dur"] += cola
        total = escenas[-1]["inicio"] + escenas[-1]["dur"]
        eventos = []
        for e in escenas:
            e["grupos"] = agrupar_palabras(e["palabras"], max_palabras=3, max_chars=20)
            e["obj"] = escenas_dict[e["visual"]]()
            e["obj"].palabras = e["palabras"]
            eventos += [(e["inicio"] + t0, tipo, d) for t0, tipo, d in e["obj"].sonidos(e["dur"])]
            e["cortes"] = e["obj"].cortes(e["dur"])
        escribir_wav(tmp / "mezcla.wav", mezclar(leer_wav(tmp / "voz.wav"), [e["inicio"] for e in escenas[1:]],
                                                 eventos, total, pad_hz))
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
            subtitulo(img, e["grupos"], tl, estilo_sub)
            a = np.clip(np.asarray(img.convert("RGB"), np.float32) * VINETA, 0, 255).astype(np.uint8)
            if idx > 0 and tl < 0.2:
                a = barrido(a, 1 - tl / 0.2, 1 if idx % 2 else -1)
            for c in e["cortes"]:
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


def preview(escenas_dict, ruta_json, audio, salida_png, momentos=(0.35, 0.85)):
    """Hoja de prueba con los tiempos REALES de la voz (usa la caché del reconocimiento)."""
    cfg = json.loads(Path(ruta_json).read_text(encoding="utf-8"))
    escenas = alinear_audio(audio, cfg["escenas"])
    ims = []
    for e in escenas:
        o = escenas_dict[e["visual"]]()
        o.palabras = e["palabras"]
        for m in momentos:
            t = e["dur"] * m
            im = o.mundo(t, e["dur"])
            im = camara(im, o.camara, m, o.sacudida(t, e["dur"]), t)
            o.encima(im, t, e["dur"])
            subtitulo(im, agrupar_palabras(e["palabras"], 3, 20), t, ESTILO_PRUEBA)
            ims.append(im.convert("RGB").resize((180, 320)))
    cols = len(momentos) * 5
    filas = math.ceil(len(ims) / cols)
    hoja = Image.new("RGB", (180 * cols, 320 * filas))
    for i, im in enumerate(ims):
        hoja.paste(im, ((i % cols) * 180, (i // cols) * 320))
    hoja.save(salida_png)


ESTILO_PRUEBA = {"modo": "color", "color": (255, 160, 60)}
