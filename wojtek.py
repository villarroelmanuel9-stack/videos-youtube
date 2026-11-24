#!/usr/bin/env python3
"""Historia 18: Wojtek, el oso soldado — estilo semi-realista (libreta militar, palabra subrayada, audio hi-fi)."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import pro
from pro import (BLANCO, Escena, H, W, chip, full, manuscrita, numero, papel_manuscrito, particulas, tarjeta)
from alcatraz import maquina, sello
from caricatura import ease, pop
from cine import pegar_glow
from dinos import TINTA, Sprite, _grad, capsula, catmull, elipse, oscuro, claro, radius_ok, sombra_suave
from generar_short import render_emoji
from humanos import Humano
from realista import LienzoReal

ESTILO = {"modo": "subrayado", "color": (214, 30, 50)}
ROJO = (214, 30, 50)
PELO, OSC, HOCICO, NARIZ = (150, 108, 70), (100, 70, 46), (200, 164, 122), (34, 26, 24)


# --------------------------------------------------------------------------- #
# EL OSO
# --------------------------------------------------------------------------- #
def _oso_lado(L, f, boca, parp, extra):
    cria = extra
    sw = 34 * math.sin(f)
    for (x0, y0), d in (((-200, -180), sw), ((160, -200), -sw)):  # patas lejanas
        L.forma(capsula((x0, y0), (x0 + 15 + d, -14), 92, 78), OSC, intensidad=0.1)
    cuerpo = [(-300, -190), (-275, -315), (-130, -372), (40, -410), (165, -380), (242, -300), (240, -170),
              (80, -128), (-120, -122), (-282, -140)]
    L.forma(cuerpo, PELO, intensidad=0.14)
    L.pelaje(cuerpo, PELO, n=170, largo=17, semilla=1)
    for (x0, y0), d in (((-165, -175), -sw), ((195, -185), sw)):  # patas cercanas
        L.forma(capsula((x0, y0), (x0 + 10 + d, -10), 112, 92), oscuro(PELO, 0.92), intensidad=0.12)
        L.forma(elipse(x0 + 22 + d, -14, 62, 24), OSC, intensidad=0.1)
    if cria:
        L.tf = (250, -320, 1.35)
    for ex, ey, r in ((246, -420, 32), (300, -432, 30)):
        L.forma(elipse(ex, ey, r, r + 2), PELO, intensidad=0.12)
        L.forma(elipse(ex + 2, ey + 4, r * 0.5, r * 0.55), OSC, borde=False, sombra=False, brillo=False)
    cab = elipse(285, -335, 115, 98)
    L.forma(cab, PELO, intensidad=0.13)
    L.pelaje(cab, PELO, n=70, largo=12, semilla=2)
    L.forma([(330, -350), (420, -338), (446, -308), (424, -276), (340, -268)], HOCICO, intensidad=0.12)
    L.forma(elipse(440, -318, 19, 14), NARIZ, intensidad=0.2, textura=0)
    L.linea([(392, -282), (432, -288)], NARIZ, 4)
    if parp:
        L.linea([(336, -368), (356, -366)], NARIZ, 4)
    else:
        L.circulo(346, -368, 9, (28, 22, 20), borde=False)
        L.circulo(343, -372, 3, (255, 255, 255), borde=False)
    L.tf = None


def _oso_pie(L, f, boca, parp, extra):
    pose, cria = extra
    bob = 6 * math.sin(f)
    for sx in (-1, 1):
        L.forma(capsula((sx * 72, -330), (sx * 82, -50), 122, 108), oscuro(PELO, 0.92), intensidad=0.12)
        L.forma(elipse(sx * 88, -32, 80, 36), OSC, intensidad=0.1)
    hombros = {"abajo": [(-175, -440), (175, -440)], "cargar": [(-120, -560), (120, -560)],
               "lucha": [(-260, -820), (260, -820)], "saludo": [(-175, -440), (110, -880)],
               "cerveza": [(-175, -440), (60, -800)], "ducha": [(-120, -980), (120, -980)]}[pose]
    if pose != "cargar":
        for sx, mano in zip((-1, 1), hombros):
            L.forma(capsula((sx * 140, -690), mano, 104, 86), oscuro(PELO, 0.88), intensidad=0.12)
    cuerpo = [(-172, -420), (-152, -640), (-92, -768), (92, -768), (152, -640), (172, -420), (132, -296),
              (-132, -296)]
    c = L.forma(cuerpo, PELO, intensidad=0.14)
    L.forma(elipse(0, -500, 102, 150), claro(PELO, 0.22), clip=c, borde=False, sombra=False, intensidad=0.05)
    L.pelaje(cuerpo, PELO, n=150, largo=16, semilla=3)
    if pose != "cargar":
        for mano in hombros:
            L.forma(elipse(mano[0], mano[1], 46, 42), OSC, intensidad=0.12)
    if cria:
        L.tf = (0, -760, 1.3)
    for sx in (-1, 1):
        L.forma(elipse(sx * 88, -935 + bob, 34, 36), PELO, intensidad=0.12)
        L.forma(elipse(sx * 88, -930 + bob, 17, 19), OSC, borde=False, sombra=False, brillo=False)
    cab = elipse(0, -852 + bob, 118, 106)
    L.forma(cab, PELO, intensidad=0.13)
    L.pelaje(cab, PELO, n=80, largo=12, semilla=4)
    L.forma(elipse(0, -812 + bob, 62, 48), HOCICO, intensidad=0.12)
    L.forma(elipse(0, -836 + bob, 26, 18), NARIZ, intensidad=0.2, textura=0)
    for sx in (-1, 1):
        if parp:
            L.linea([(sx * 35, -880 + bob), (sx * 55, -880 + bob)], NARIZ, 4)
        else:
            L.circulo(sx * 45, -882 + bob, 10, (28, 22, 20), borde=False)
            L.circulo(sx * 45 - 3, -886 + bob, 3, (255, 255, 255), borde=False)
    if boca > 0.2 or pose in ("lucha",):
        L.forma(elipse(0, -790 + bob, 22, 16), (120, 40, 40), sombra=False, brillo=False, textura=0)
    else:
        L.linea(catmull([(-20, -800 + bob), (0, -792 + bob), (20, -800 + bob)], 4, cerrado=False), NARIZ, 4)
    L.tf = None
    if pose == "cargar":  # caja de proyectiles delante del pecho
        L.forma([(-150, -640), (150, -640), (150, -480), (-150, -480)], (150, 110, 64), suave=False, intensidad=0.08)
        for k in range(3):
            L.linea([(-150, -600 + k * 45), (150, -600 + k * 45)], (110, 78, 44), 4)
        for k in range(4):
            x = -105 + k * 70
            L.forma([(x - 22, -640), (x + 22, -640), (x + 22, -700), (x, -735), (x - 22, -700)], (200, 160, 70),
                    suave=False, intensidad=0.12, textura=0)
        for sx in (-1, 1):
            L.forma(capsula((sx * 140, -690), (sx * 150, -560), 104, 86), oscuro(PELO, 0.88), intensidad=0.12)
            L.forma(elipse(sx * 150, -560, 46, 42), OSC, intensidad=0.12)
    if pose == "cerveza":
        L.forma([(48, -880), (78, -880), (86, -780), (40, -780)], (110, 70, 30), suave=False, intensidad=0.1,
                textura=0)
    if pose == "saludo":
        L.linea([(80, -900), (130, -860)], OSC, 6)


def _oso_sentado(L, f, boca, parp, extra):
    con_botella = extra
    for sx in (-1, 1):
        L.forma(elipse(sx * 120, -80, 86, 62), oscuro(PELO, 0.9), intensidad=0.12)
        L.forma(elipse(sx * 140, -64, 40, 30), OSC, intensidad=0.1)
    cuerpo = elipse(0, -300, 190, 220)
    c = L.forma(cuerpo, PELO, intensidad=0.14)
    L.forma(elipse(0, -260, 110, 140), claro(PELO, 0.22), clip=c, borde=False, sombra=False)
    L.pelaje(cuerpo, PELO, n=120, largo=14, semilla=5)
    if con_botella:
        L.forma([(-24, -620), (24, -620), (34, -420), (-34, -420)], (200, 220, 225), suave=False, intensidad=0.08,
                textura=0)
        L.forma([(-24, -470), (24, -470), (34, -420), (-34, -420)], (245, 245, 240), suave=False, borde=False,
                sombra=False, brillo=False, textura=0)
    for sx in (-1, 1):
        L.forma(elipse(sx * 60, -440, 52, 46), OSC, intensidad=0.12)
    L.tf = (0, -500, 1.25)
    for sx in (-1, 1):
        L.forma(elipse(sx * 95, -715, 36, 38), PELO, intensidad=0.12)
    cab = elipse(0, -630, 125, 112)
    L.forma(cab, PELO, intensidad=0.13)
    L.pelaje(cab, PELO, n=80, largo=11, semilla=6)
    L.forma(elipse(0, -590, 62, 48), HOCICO, intensidad=0.12)
    L.forma(elipse(0, -612, 24, 17), NARIZ, intensidad=0.2, textura=0)
    for sx in (-1, 1):
        L.circulo(sx * 48, -662, 12, (28, 22, 20), borde=False)
        L.circulo(sx * 48 - 4, -667, 4, (255, 255, 255), borde=False)
    L.tf = None


OSO_LADO = Sprite(_oso_lado, 1000, 720, 470, 680, fases=12, lienzo_cls=LienzoReal)
OSO_PIE = Sprite(_oso_pie, 760, 1180, 380, 1120, fases=8, lienzo_cls=LienzoReal)
OSO_SENTADO = Sprite(_oso_sentado, 600, 900, 300, 860, fases=1, lienzo_cls=LienzoReal)


def soldado(i, **kw):
    pelos = [(90, 60, 40), (40, 30, 26), (150, 110, 60), (60, 42, 30)]
    return Humano(ropa=(118, 108, 72), pantalon=(108, 98, 66), cinturon=True, sombrero="gorra_tommy",
                  color_sombrero=(108, 100, 66), pelo=pelos[i % 4], barba=i % 2 == 1, realista=True, cabeza=0.86,
                  **kw)


SOLDADOS = [soldado(i) for i in range(4)]
NINO = Humano(ropa=(230, 220, 196), pantalon=(160, 140, 110), pelo=(30, 24, 20), piel=(206, 160, 120),
              realista=True, cabeza=0.95)
VETERANOS = [Humano(ropa=c, pantalon=(60, 60, 66), sombrero="fedora", color_sombrero=(70, 66, 60),
                    pelo=(200, 200, 200), barba=True, realista=True, cabeza=0.86) for c in ((90, 80, 70),
                                                                                       (60, 70, 90))]


def bronce(im):
    a = im.getchannel("A")
    g = ImageOps.colorize(im.convert("L"), black=(46, 30, 16), white=(222, 176, 112)).convert("RGBA")
    g.putalpha(a)
    return g


# --------------------------------------------------------------------------- #
# FONDOS (pintados, con perspectiva atmosférica)
# --------------------------------------------------------------------------- #
def _full_real(dib):
    from dinos import Lienzo as _L  # noqa
    L = LienzoReal(W, H, 0, 0)
    dib(L)
    return L.final()


def fondo_desierto(atardecer=False):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (120, 160, 205)), (0.55, (236, 214, 180)), (1, (236, 214, 180))]
                                    if not atardecer else
                                    [(0, (70, 70, 120)), (0.5, (230, 150, 110)), (0.6, (250, 200, 140)), (1, (250, 200, 140))]))
        pro.montanas(L, 1080, [(180, 700, 330), (700, 800, 400)], (176, 160, 160) if not atardecer else (150, 110, 120),
                     nieve=False, borde=False)
        pro.montanas(L, 1180, [(0, 700, 260), (560, 700, 300), (1050, 600, 240)], (186, 150, 110), nieve=False,
                     borde=False)
        L.forma(catmull([(-50, 1180), (W + 50, 1160), (W + 50, H), (-50, H)], 3), (214, 180, 130), borde=False,
                intensidad=0.03, textura=0.12)
        L.forma(catmull([(380, 1180), (700, 1180), (1000, H), (100, H)], 3), (196, 164, 120), borde=False,
                intensidad=0.03, textura=0.1)
        r = random.Random(4)
        for _ in range(9):
            x, y = r.randint(0, W), r.randint(1250, H - 60)
            L.forma(elipse(x, y, r.randint(30, 60), r.randint(16, 26)), (150, 130, 110), intensidad=0.2)
    img = _full_real(dib)
    pegar_glow(img, 800, 600, 600, "#fff2d0", 0.35)
    return img


def carpa(L, x, base, w, h, col=(110, 112, 76)):
    L.forma([(x - w / 2, base), (x, base - h), (x + w / 2, base)], col, suave=False, intensidad=0.12)
    L.forma([(x - 40, base), (x, base - h * 0.55), (x + 40, base)], oscuro(col, 0.5), suave=False, borde=False)


def fondo_campamento(atardecer=False):
    base = fondo_desierto(atardecer)
    L = LienzoReal(W, H, 0, 0)
    for x, w, h in ((140, 300, 240), (520, 360, 280), (900, 300, 230)):
        carpa(L, x, 1200, w, h)
    base.alpha_composite(L.final())
    return base


def camion(img, x, y, s=1.0):
    L = LienzoReal(900, 500, 450, 450)
    c = (96, 102, 66)
    L.forma([(-380, -80), (100, -80), (100, -300), (-380, -300)], c, suave=False, intensidad=0.08)
    L.forma([(100, -80), (360, -80), (360, -200), (280, -260), (100, -260)], oscuro(c, 0.92), suave=False)
    L.forma([(200, -240), (290, -240), (330, -200), (200, -200)], (150, 180, 200), suave=False, textura=0)
    for wx in (-260, -120, 260):
        L.forma(elipse(wx, -60, 62, 62), (36, 36, 38), intensidad=0.2, textura=0)
        L.forma(elipse(wx, -60, 26, 26), (120, 120, 110), textura=0)
    im = L.final()
    if s != 1:
        im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
    img.alpha_composite(im, (int(x - 450 * s), int(y - 450 * s)))


def fondo_puerto():
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (120, 170, 210)), (0.5, (230, 226, 210)), (1, (230, 226, 210))]))
        L.forma([(0, 1000), (W, 1000), (W, 1350), (0, 1350)], (70, 120, 150), suave=False, borde=False, textura=0.05)
        L.forma([(-60, 1000), (900, 1000), (860, 1120), (-40, 1120)], (110, 116, 124), suave=False, intensidad=0.06)
        L.forma([(-60, 560), (840, 560), (900, 1000), (-60, 1000)], (130, 136, 146), suave=False, intensidad=0.06)
        for i in range(10):
            L.circulo(40 + i * 80, 860, 14, (60, 70, 90), ancho=3)
        L.forma([(200, 560), (300, 560), (300, 380), (200, 380)], (150, 156, 164), suave=False)
        L.forma([(220, 380), (280, 380), (280, 300), (220, 300)], (40, 40, 44), suave=False)
        L.forma([(0, 1340), (W, 1340), (W, H), (0, H)], (170, 160, 140), suave=False, borde=False, textura=0.1)
        L.forma([(740, 1000), (1000, 1340), (960, 1350), (700, 1010)], (150, 116, 76), suave=False, intensidad=0.08)
        for k, x in enumerate((900, 1010)):
            L.forma([(x - 60, 1400), (x + 60, 1400), (x + 60, 1300), (x - 60, 1300)], (160, 120, 70), suave=False)
    return _full_real(dib)


def fondo_cassino():
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (120, 130, 150)), (0.6, (210, 200, 190)), (1, (210, 200, 190))]))
        pro.montanas(L, 1100, [(300, 900, 520), (900, 700, 360)], (130, 140, 130), nieve=False, borde=False)
        L.forma([(170, 600), (430, 600), (430, 520), (380, 520), (370, 480), (300, 470), (280, 520), (170, 520)],
                (220, 214, 200), suave=False, intensidad=0.08)
        for x in (200, 260, 320, 390):
            L.forma([(x, 600), (x + 30, 600), (x + 30, 560), (x, 560)], (90, 86, 80), suave=False, borde=False)
        L.forma(catmull([(-50, 1150), (W + 50, 1120), (W + 50, H), (-50, H)], 3), (120, 120, 90), borde=False,
                textura=0.12)
        r = random.Random(6)
        for _ in range(14):
            x, y = r.randint(0, W), r.randint(1200, H)
            L.forma(elipse(x, y, r.randint(40, 90), r.randint(16, 30)), (100, 98, 74), intensidad=0.15)
    img = _full_real(dib)
    for i, (x, y) in enumerate(((300, 470), (520, 760), (850, 820))):
        pegar_glow(img, x, y - 80, 200, "#6a6660", 0.6)
    return img


def fondo_zoo():
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (150, 160, 172)), (0.6, (206, 210, 214)), (1, (206, 210, 214))]))
        L.forma([(560, 760), (620, 640), (700, 650), (760, 560), (830, 600), (900, 760)], (120, 124, 130),
                suave=False, borde=False)
        L.forma(catmull([(-50, 900), (W + 50, 880), (W + 50, 1000), (-50, 1000)], 3), (100, 130, 90), borde=False)
        L.forma([(0, 1000), (W, 1000), (W, H), (0, H)], (130, 120, 104), suave=False, borde=False, textura=0.12)
        r = random.Random(3)
        for _ in range(10):
            x, y = r.randint(0, W), r.randint(1040, 1400)
            L.forma(elipse(x, y, r.randint(60, 120), r.randint(30, 60)), (140, 138, 130), intensidad=0.18)
        L.forma(catmull([(560, 1300), (1000, 1290), (1000, 1420), (560, 1430)], 3), (110, 150, 170), textura=0.04)
    return _full_real(dib)


def reja(img):
    d = ImageDraw.Draw(img)
    for x in range(20, W, 70):
        d.rectangle((x, 1500, x + 10, H), fill=(40, 44, 40))
    d.rectangle((0, 1520, W, 1536), fill=(40, 44, 40))
    d.rectangle((0, 1880, W, 1896), fill=(40, 44, 40))


def fondo_parque():
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (160, 170, 186)), (0.6, (220, 222, 224)), (1, (220, 222, 224))]))
        for x in (80, 330, 760, 1000):
            L.forma(elipse(x, 760, 160, 190), (80, 110, 80), intensidad=0.12)
            L.forma([(x - 18, 1000), (x + 18, 1000), (x + 14, 880), (x - 14, 880)], (90, 70, 50), suave=False)
        L.forma([(0, 1000), (W, 1000), (W, H), (0, H)], (110, 150, 90), suave=False, borde=False, textura=0.1)
        L.forma([(240, 1500), (840, 1500), (860, 1640), (220, 1640)], (170, 166, 160), suave=False, intensidad=0.08)
    return _full_real(dib)


# --------------------------------------------------------------------------- #
# ESCENAS
# --------------------------------------------------------------------------- #
class W1(Escena):
    camara = (1.0, 1.1, 0.55, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_campamento()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for i, x in enumerate((150, 360, 570)):
            SOLDADOS[i].dibujar(img, x, 1760, 0.95, t, expr="serio")
        OSO_PIE.dibujar(img, 860, 1780, 1.0, t * 0.6, extra=("saludo", False))
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("soldado", 0.3, dur), "izq", 200, "ejército polaco", "Soldado Wojtek", "militar",
                emoji="🐻")
        for k, (pal, txt) in enumerate((("rango", "RANGO"), ("numero", "NÚMERO"), ("sueldo", "SUELDO"))):
            chip(img, t, self.tp(pal, 0.55 + 0.12 * k, dur), f"✓ {txt}".replace("✓ ", ""), y=460 + k * 100,
                 fondo=(84, 92, 60), tam=42, x=820)

    def sonidos(self, dur):
        return [(0.2, "gruñido", 1.2), (0, "multitud", dur), (0, "viento", dur)]


class W2(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_desierto()
        camion(self.fondo, 260, 1330, 0.8)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        SOLDADOS[0].dibujar(img, 420, 1760, 0.95, t, expr="sorpresa" if t > self.tp("osezno", 0.6, dur) else "feliz",
                            pose="sostener" if t > self.tp("comida", 0.85, dur) else "quieto")
        SOLDADOS[1].dibujar(img, 200, 1720, 0.85, t, expr="feliz")
        NINO.dibujar(img, 840, 1760, 0.75, t, pose="sostener", expr="normal")
        OSO_SENTADO.dibujar(img, 840, 1560, 0.32, t, extra=False, sombra=False)
        tc = self.tp("comida", 0.85, dur)
        if t > tc:
            em = render_emoji("🥫")
            if em is not None:
                q = ease((t - tc) / 0.8)
                em = em.resize((110, int(110 * em.height / em.width)))
                img.alpha_composite(em, (int(480 + 250 * q), int(1320 - 80 * math.sin(math.pi * q))))
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.15, "izq", 200, "1942", "Irán", "militar", emoji="🗺️")
        chip(img, t, self.tp("osezno", 0.6, dur), "un osezno huérfano", y=520, fondo=(84, 92, 60), tam=44)

    def sonidos(self, dur):
        return [(0, "camion", dur), (0, "viento", dur)]


class W3(Escena):
    camara = (1.0, 1.12, 0.5, 0.62)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_campamento(atardecer=True)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        SOLDADOS[2].dibujar(img, 330, 1760, 0.95, t, pose="sentado", expr="feliz")
        OSO_SENTADO.dibujar(img, 700, 1760, 0.75, t, extra=t > self.tp("leche", 0.6, dur))
        return img

    def encima(self, img, t, dur):
        numero(img, t, self.tp("wojtek", 0.1, dur), "WOJTEK", "«guerrero feliz»", y=420, color=(255, 236, 190))
        chip(img, t, self.tp("vodka", 0.85, dur), "leche en una botella de vodka", y=700, fondo=(84, 92, 60), tam=40)

    def sonidos(self, dur):
        return [(0, "multitud", dur), (self.tp("leche", 0.6, dur), "botella", 0.4)]


class W4(Escena):
    camara = (1.0, 1.06, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_campamento()

    def fases(self, dur):
        return self.tp("luchaba", 0.3, dur) - 0.15, self.tp("ducharse", 0.6, dur) - 0.15, \
            self.tp("cerveza", 0.85, dur) - 0.15

    def cortes(self, dur):
        return list(self.fases(dur))

    def mundo(self, t, dur):
        img = self.fondo.copy()
        tl, td, tc = self.fases(dur)
        if t < tl:
            OSO_LADO.dibujar(img, 200 + t * 120, 1720, 1.0, t, vel=0.8, extra=False)
        elif t < td:
            OSO_PIE.dibujar(img, 680, 1780, 1.0, t, extra=("lucha", False), boca=0.5)
            SOLDADOS[3].dibujar(img, 330, 1760, 1.0, t, pose="celebrar", expr="feliz")
        elif t < tc:
            d = ImageDraw.Draw(img)
            d.rectangle((520, 420, 560, 1000), fill=(120, 124, 130), outline=TINTA, width=4)
            d.rectangle((420, 420, 560, 450), fill=(120, 124, 130), outline=TINTA, width=4)
            OSO_PIE.dibujar(img, 480, 1780, 1.0, t, extra=("ducha", False))
            for k in range(40):
                fx = (k * 37) % 120 - 60
                fy = (t * 900 + k * 61) % 900
                d.line((440 + fx, 470 + fy, 440 + fx, 500 + fy), fill=(190, 220, 240), width=4)
        else:
            OSO_PIE.dibujar(img, 560, 1780, 1.0, t, extra=("cerveza", False))
        return img

    def encima(self, img, t, dur):
        tl, td, tc = self.fases(dur)
        if t < tl:
            numero(img, t, self.tp("doscientos", 0.1, dur), "+200 kg", None, y=420, color=(255, 236, 190))
        if tl <= t < td:
            chip(img, t, tl + 0.1, "luchaba con los soldados", y=640, fondo=(84, 92, 60), tam=40)
        elif td <= t < tc:
            chip(img, t, td + 0.1, "le encantaba ducharse", y=640, fondo=(60, 110, 140), tam=40)
        elif t >= tc:
            chip(img, t, tc + 0.1, "¡y tomaba cerveza!", y=640, fondo=(150, 100, 40), tam=44)

    def sonidos(self, dur):
        tl, td, tc = self.fases(dur)
        return [(0, "pasos", tl), (tl, "gruñido", 1.0), (td, "ducha", tc - td), (tc + 0.2, "botella", 0.4)]


class W5(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_puerto()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        SOLDADOS[0].dibujar(img, 240, 1760, 0.9, t, expr="serio")
        OSO_LADO.dibujar(img, 600, 1720, 0.85, t, vel=0.4, extra=False)
        ta = self.tp("alistaron", 0.8, dur)
        if t > ta:
            p = pop((t - ta) / 0.35)
            hoja_ = Image.new("RGBA", (520, 380), (244, 236, 214, 255))
            dh = ImageDraw.Draw(hoja_)
            dh.rectangle((0, 0, 519, 379), outline=(120, 100, 70), width=5)
            dh.text((260, 50), "ALISTAMIENTO", font=maquina(40), fill=TINTA, anchor="mm")
            dh.text((40, 120), "NOMBRE: WOJTEK", font=maquina(32), fill=TINTA)
            dh.text((40, 170), "UNIDAD: 22ª CÍA.", font=maquina(32), fill=TINTA)
            dh.text((40, 220), "SUMINISTRO DE ARTILLERÍA", font=maquina(26), fill=TINTA)
            for k, (dx, dy) in enumerate(((380, 300), (410, 270), (440, 260), (470, 280))):
                dh.ellipse((dx - 14, dy - 14, dx + 14, dy + 14), fill=(110, 70, 40))
            dh.ellipse((390, 290, 470, 350), fill=(110, 70, 40))
            hoja_ = hoja_.rotate(-4, expand=True, resample=Image.BICUBIC)
            hoja_ = hoja_.resize((max(1, int(hoja_.width * p)), max(1, int(hoja_.height * p))))
            img.alpha_composite(hoja_, (int(540 - hoja_.width / 2), int(820 - hoja_.height / 2)))
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("barco", 0.15, dur), "izq", 200, "1944 · en barco", "Egipto → Italia", "militar",
                emoji="🚢")
        ta = self.tp("alistaron", 0.8, dur)
        if t < ta:
            sello(img, t, self.tp("animales", 0.55, dur), "PROHIBIDO ANIMALES", W / 2, 760, ang=-8, tam=70)
        else:
            sello(img, t, ta + 0.5, "ALISTADO", W / 2 + 120, 960, ang=-12, color=(40, 130, 60), tam=80)

    def sonidos(self, dur):
        return [(0, "bocina_barco", 2.2), (0, "olas", dur), (self.tp("animales", 0.55, dur), "sello", 0.3),
                (self.tp("alistaron", 0.8, dur) + 0.5, "sello", 0.3)]


class W6(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_cassino()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for k in range(3):
            tt = (t + k * 1.1) % 2.6
            if tt < 0.4:
                pegar_glow(img, 250 + k * 300, 700 + (k % 2) * 80, 140 * (1 - tt * 2.5) + 40, "#ffb060", 0.9)
        for i, x in enumerate((120, 960)):
            SOLDADOS[i].dibujar(img, x, 1720, 0.85, t, pose="sostener", expr="serio")
        OSO_PIE.dibujar(img, 300 + t * 70, 1790 + 8 * abs(math.sin(t * 4)), 1.0, t, extra=("cargar", False))
        particulas(img, t, "ceniza", 40, alfa=160)
        return img

    def sacudida(self, t, dur):
        return 0.3

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("montecassino", 0.1, dur), "izq", 200, "batalla de", "Montecassino", "militar",
                emoji="💥")
        chip(img, t, self.tp("proyectiles", 0.55, dur), "cajas de proyectiles", y=520, fondo=(84, 92, 60), tam=42)
        chip(img, t, self.tp("caer", 0.9, dur), "¡ni una sola cayó!", y=640, fondo=ROJO, tam=46)

    def sonidos(self, dur):
        return [(k * 1.3 + 0.3, "artilleria", 2.0) for k in range(int(dur / 1.3))] + [(0, "pasos", dur)]


class W7(Escena):
    camara = (1.0, 1.06, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.fondo = _grad(W, H, [(0, (64, 70, 46)), (1, (36, 40, 28))])
        insignia = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
        di = ImageDraw.Draw(insignia)
        di.ellipse((10, 10, 690, 690), fill=(236, 226, 196), outline=(60, 50, 30), width=14)
        di.ellipse((40, 40, 660, 660), outline=(160, 40, 40), width=8)
        oso = OSO_PIE.get(0, 0.5, 0, False, ("cargar", False))
        silu = Image.new("RGBA", oso.size, (70, 46, 26, 255))
        silu.putalpha(oso.getchannel("A"))
        insignia.alpha_composite(silu, (int(350 - silu.width / 2), int(660 - silu.height)))
        self.insignia = insignia

    def mundo(self, t, dur):
        img = self.fondo.copy()
        te = self.tp("emblema", 0.6, dur)
        if t > te:
            p = pop((t - te) / 0.45)
            ins = self.insignia.resize((max(1, int(700 * p)), max(1, int(700 * p))), Image.BICUBIC)
            pegar_glow(img, 540, 860, 520 * p, "#ffe7a0", 0.35)
            img.alpha_composite(ins, (int(540 - ins.width / 2), int(860 - ins.height / 2)))
        else:
            OSO_PIE.dibujar(img, 540, 1760, 1.05, t, extra=("saludo", False))
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("cabo", 0.2, dur), "izq", 200, "ascendido a", "CABO", "militar", emoji="🎖️")
        if t > self.tp("emblema", 0.6, dur):
            chip(img, t, self.tp("emblema", 0.6, dur) + 0.4, "el emblema de su unidad", y=1260, fondo=(84, 92, 60),
                 tam=42)

    def sonidos(self, dur):
        return [(self.tp("cabo", 0.2, dur), "pop", 0.2), (self.tp("emblema", 0.6, dur), "sello", 0.3),
                (self.tp("emblema", 0.6, dur) + 0.3, "aplausos", 2.0)]


class W8(Escena):
    camara = (1.0, 1.08, 0.5, 0.58)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_zoo()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        OSO_LADO.dibujar(img, 300 + 40 * math.sin(t * 0.5), 1300, 0.8, t, vel=0.3, extra=False)
        reja(img)
        for i, (v, x) in enumerate(zip(VETERANOS, (300, 760))):
            v.dibujar(img, x, 1900, 0.9, t + i, pose="saludar", expr="feliz")
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("edimburgo", 0.2, dur), "izq", 200, "1947 – 1963", "Zoo de Edimburgo", "militar",
                emoji="🏴")
        tp_ = self.tp("polaco", 0.85, dur)
        if t > tp_:
            p = pop((t - tp_) / 0.3)
            d = ImageDraw.Draw(img)
            caja = (W / 2 - 280 * p, 720 - 70 * p, W / 2 + 280 * p, 720 + 70 * p)
            sombra_suave(img, caja, radio=34)
            d.rounded_rectangle(caja, radius=radius_ok(34 * p), fill=(255, 255, 255, 246), outline=TINTA, width=5)
            d.text((W / 2, 720), "«Cześć, Wojtek!»", font=manuscrita(max(8, int(60 * p))), fill=(40, 50, 90),
                   anchor="mm")
            chip(img, t, tp_ + 0.3, "(«¡Hola, Wojtek!» en polaco)", y=830, fondo=(60, 60, 66), tam=32)

    def sonidos(self, dur):
        return [(0, "multitud", dur), (0, "viento", dur)]


class W9(Escena):  # final: estatua de bronce + huellas + sello de huella "SUSCRÍBETE"
    camara = (1.0, 1.04, 0.5, 0.55)

    def __init__(self):
        super().__init__()
        img = fondo_parque()
        oso = bronce(OSO_LADO.get(0.6, 0.62, 0, False, False))
        sold = bronce(SOLDADOS[0].sprite.get(0.6, 0.66, 0, False, ("caminar", "serio")))
        img.alpha_composite(oso, (int(300 - 0.62 * 470), int(1500 - 0.62 * 680)))
        img.alpha_composite(sold, (int(720 - 0.66 * 300), int(1500 - 0.66 * 960)))
        d = ImageDraw.Draw(img)
        d.rectangle((420, 1550, 660, 1610), fill=(150, 110, 60), outline=TINTA, width=4)
        d.text((540, 1580), "WOJTEK", font=maquina(40), fill=(250, 230, 180), anchor="mm")
        self.fondo = img

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        for k in range(int(min(12, t * 3))):
            x = 80 + k * 85
            y = 1740 + (25 if k % 2 else -25)
            d.ellipse((x - 22, y - 18, x + 22, y + 22), fill=(80, 60, 40, 200))
            for j, dx in enumerate((-22, -8, 8, 22)):
                d.ellipse((x + dx - 8, y - 40 - (6 if j in (1, 2) else 0), x + dx + 8, y - 26 - (6 if j in (1, 2) else 0)),
                          fill=(80, 60, 40, 200))
        return img

    def encima(self, img, t, dur):
        chip(img, t, 0.1, "SU ESTATUA EN EDIMBURGO", y=240, fondo=(84, 92, 60), tam=40)
        chip(img, t, self.tp("escribe", 0.35, dur), "escribe «WOJTEK» 👇".replace(" 👇", ""), y=380, fondo=ROJO, tam=50)
        ts = self.tp("suscribete", 0.7, dur)
        if t > ts:
            q = min(1.0, (t - ts) / 0.2)
            esc = 1.6 - 0.6 * q
            capa = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
            dc = ImageDraw.Draw(capa)
            dc.ellipse((150, 200, 370, 400), fill=ROJO + (235,))
            for dx, dy in ((-110, -40), (-45, -110), (45, -110), (110, -40)):
                dc.ellipse((260 + dx - 45, 250 + dy - 45, 260 + dx + 45, 250 + dy + 45), fill=ROJO + (235,))
            dc.text((260, 470), "SUSCRÍBETE", font=pro.fuente(58), fill=BLANCO, anchor="mm", stroke_width=6,
                    stroke_fill=ROJO)
            capa = capa.rotate(-10, expand=True, resample=Image.BICUBIC)
            capa = capa.resize((int(capa.width * esc * 0.8), int(capa.height * esc * 0.8)))
            img.alpha_composite(capa, (int(540 - capa.width / 2), int(860 - capa.height / 2)))

    def sonidos(self, dur):
        return [(0, "pasos", min(4.0, dur)), (self.tp("suscribete", 0.7, dur), "sello", 0.3)]


ESCENAS = {f"18_{i}": c for i, c in enumerate((W1, W2, W3, W4, W5, W6, W7, W8, W9), 1)}
JSON, AUDIO = "historias/historia_18_wojtek.json", "audios/historia_18_voz.mp3"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--sin-audio", action="store_true")
    ap.add_argument("--audio", default=AUDIO)
    a = ap.parse_args()
    if a.preview:
        pro.preview(ESCENAS, JSON, a.audio, "/tmp/claude-0/prev_18.png")
    else:
        pro.generar(Path(JSON), ESCENAS, ESTILO, a.audio, a.sin_audio, pad_hz=(55, 82.4, 110), hifi=True,
                    acabado=True)
