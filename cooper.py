#!/usr/bin/env python3
"""Historia 13: D. B. Cooper — estilo retro años 70 (naranja, verde azulado, mostaza)."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import pro
from pro import (BLANCO, Escena, H, W, avion, bandera, chip, dibujar_avion, full, manuscrita, numero,
                 papel_manuscrito, particulas, relampago, tarjeta)
from alcatraz import maquina, sello
from caricatura import ease, pop
from cine import pegar_glow
from dinos import TINTA, _grad, capsula, catmull, elipse, oscuro, sombra_suave
from generar_short import render_emoji
from humanos import Humano

NAR, TEAL, MOST, CAFE = (232, 131, 58), (42, 127, 134), (217, 164, 65), (90, 58, 40)
ESTILO = {"modo": "color", "color": (255, 150, 60)}

COOPER = Humano(ropa=(40, 42, 52), pantalon=(35, 36, 44), corbata=(20, 20, 24), lentes=True, pelo=(40, 30, 26))
AZAFATA = Humano(ropa=(40, 120, 130), vestido=True, peinado="largo", pelo=(150, 100, 50), sombrero="azafata")
NINO = Humano(ropa=(220, 90, 60), pantalon=(60, 90, 150), pelo=(160, 110, 60))
AGENTE = Humano(ropa=(70, 70, 74), pantalon=(60, 60, 64), corbata=(30, 30, 34), sombrero="fedora", pelo=(60, 40, 30))
PASAJEROS = [Humano(ropa=c, pelo=p, peinado=pe) for c, p, pe in (((180, 90, 60), (60, 40, 30), "corto"),
                                                                ((60, 110, 90), (150, 100, 50), "largo"),
                                                                ((140, 120, 70), (30, 30, 30), "rizado"))]


# --------------------------------------------------------------------------- #
def _billetes(d, x, y, w=150, h=70, podrido=False):
    col = (120, 160, 110) if not podrido else (110, 120, 80)
    d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=col, outline=TINTA, width=4)
    d.ellipse((x - 20, y - 20, x + 20, y + 20), outline=(60, 90, 60), width=4)
    d.rectangle((x - 12, y - h / 2, x + 12, y + h / 2), fill=(240, 230, 200), outline=TINTA, width=2)
    if podrido:
        r = random.Random(int(x + y))
        for _ in range(5):
            px, py = x + r.uniform(-w / 2, w / 2), y + r.uniform(-h / 2, h / 2)
            d.ellipse((px - 10, py - 7, px + 10, py + 7), fill=(80, 70, 50))


def _paracaidas(d, x, y, s=1.0):
    d.pieslice((x - 70 * s, y - 60 * s, x + 70 * s, y + 60 * s), 180, 360, fill=(230, 120, 50), outline=TINTA,
               width=4)
    for i in range(1, 4):
        d.line((x - 70 * s + i * 35 * s, y, x - 70 * s + i * 35 * s, y - 50 * s), fill=(250, 240, 220), width=4)
    for dx in (-60, -20, 20, 60):
        d.line((x + dx * s, y, x, y + 80 * s), fill=TINTA, width=2)
    d.rectangle((x - 12 * s, y + 80 * s, x + 12 * s, y + 104 * s), fill=CAFE, outline=TINTA, width=3)


def fondo_pista(noche=False):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (40, 30, 70)), (0.45, (190, 90, 80)), (0.6, (240, 160, 90)),
                                                   (1, (240, 160, 90))] if not noche else
                                    [(0, (10, 14, 30)), (0.55, (30, 40, 70)), (1, (30, 40, 70))]))
        rnd = random.Random(3)
        for x in range(0, W, 40):
            h = rnd.randint(30, 120)
            L.forma([(x, 1120), (x, 1120 - h), (x + 32, 1120 - h), (x + 32, 1120)], (50, 40, 60) if not noche
                    else (20, 24, 40), suave=False, borde=False, sombra=False, brillo=False)
            for _ in range(2):
                L.circulo(x + rnd.randint(6, 26), 1120 - rnd.randint(8, max(9, h - 6)), 2.5, (255, 220, 140),
                          borde=False)
        L.forma([(60, 1120), (60, 980), (420, 980), (460, 1120)], (120, 110, 120) if not noche else (50, 54, 70),
                suave=False, intensidad=0.06)
        L.forma([(250, 980), (250, 880), (300, 880), (300, 980)], (100, 96, 110), suave=False)
        L.forma([(230, 880), (320, 880), (320, 850), (230, 850)], (120, 200, 210), suave=False)
        L.forma([(0, 1120), (W, 1120), (W, H), (0, H)], (88, 90, 96) if not noche else (40, 42, 50), suave=False,
                borde=False)
        for y in (1300, 1550, 1820):
            L.linea([(100, y), (300, y)], (240, 200, 70), 10)
            L.linea([(600, y), (800, y)], (240, 200, 70), 10)
    return full(dib)


def fondo_cabina():
    def dib(L):
        L.d.rectangle((0, 0, W * 2, H * 2), fill=(238, 224, 198))
        L.forma(catmull([(0, 0), (W, 0), (W, 380), (W * 0.5, 460), (0, 380)], 4), (220, 200, 170), borde=False)
        L.forma([(0, 380), (W, 380), (W, 470), (0, 470)], (200, 110, 60), suave=False, intensidad=0.05)
        for x in range(80, W, 260):
            L.forma(catmull([(x, 560), (x + 140, 560), (x + 140, 760), (x, 760)], 3), (20, 30, 60), intensidad=0.04)
            for _ in range(3):
                L.circulo(x + random.Random(x).randint(20, 120), random.Random(x + 1).randint(580, 740), 3,
                          (240, 240, 255), borde=False)
        L.forma([(0, 1450), (W, 1450), (W, H), (0, H)], (170, 80, 50), suave=False, borde=False)
        for i in range(0, W, 60):
            L.linea([(i, 1450), (i + 30, H)], (150, 66, 40), 6)
    return full(dib)


def asiento(img, x, y, s=1.0):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x - 120 * s, y - 520 * s, x + 120 * s, y - 120 * s), radius=int(40 * s), fill=(210, 110, 50),
                        outline=TINTA, width=6)
    d.rounded_rectangle((x - 90 * s, y - 500 * s, x + 90 * s, y - 420 * s), radius=int(20 * s), fill=(245, 240, 230),
                        outline=TINTA, width=3)
    d.rectangle((x - 120 * s, y - 140 * s, x + 120 * s, y - 60 * s), fill=(190, 96, 44), outline=TINTA, width=6)


def nubes(img, t, oscuras=True, n=7, y0=200):
    for i in range(n):
        x = (i * 330 - t * (60 + i * 8)) % (W + 700) - 350
        y = y0 + (i % 3) * 260
        pegar_glow(img, x, y, 340, "#3a3f55" if oscuras else "#ffffff", 0.75)


def pinos(L, base, n, alto, col, semilla=1):
    r = random.Random(semilla)
    for i in range(n):
        x = r.uniform(-60, W + 60)
        h = alto * r.uniform(0.7, 1.2)
        L.forma([(x - h * 0.22, base), (x, base - h), (x + h * 0.22, base)], col, suave=False, intensidad=0.08)


# --------------------------------------------------------------------------- #
class C1(Escena):
    camara = (1.0, 1.12, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_pista()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        dibujar_avion(img, "727", 820, 1080, 1.25)
        COOPER.dibujar(img, 200 + t * 50, 1700, 0.95, t, pose="caminar", vel=0.9, expr="serio")
        particulas(img, t, "lluvia", 90, viento=-120)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.2, "izq", 220, "24 nov 1971", "VUELO 305", "boleto", emoji="✈️")
        chip(img, t, self.tp("leyenda", 0.8, dur), "LA LEYENDA DE D. B. COOPER", y=760, fondo=(150, 70, 30), tam=46)

    def sonidos(self, dur):
        return [(0, "lluvia", dur), (0.3, "motor", dur)]


class C2(Escena):
    camara = (1.0, 1.1, 0.45, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_cabina()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        asiento(img, 330, 1690, 1.05)
        COOPER.dibujar(img, 300, 1700, 0.95, t, pose="sentado", expr="serio", sombra=False)
        tb = self.tp("bomba", 0.85, dur)
        AZAFATA.dibujar(img, 800, 1720, 1.0, t, expr="miedo" if t > tb else "normal")
        tn = self.tp("nota", 0.6, dur)
        if tn < t < tb:
            q = ease((t - tn) / 0.8)
            x, y = 430 + 260 * q, 1300 - 80 * q
            d = ImageDraw.Draw(img)
            d.polygon([(x - 40, y - 30), (x + 40, y - 34), (x + 44, y + 26), (x - 36, y + 30)], fill=(250, 246, 230),
                      outline=TINTA)
        asiento(img, 120, 1900, 1.25)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("cooper", 0.15, dur), "izq", 220, "pasajero", "DAN COOPER", "boleto", emoji="🕶️")
        chip(img, t, self.tp("prensa", 0.35, dur), "«D. B.» fue un error de la prensa", y=470, fondo=TEAL, tam=38,
             dur=self.tp("pleno", 0.55, dur) - self.tp("prensa", 0.35, dur))
        papel_manuscrito(img, t, self.tp("bomba", 0.85, dur) - 0.1, ["Tengo una bomba", "en mi maletín."],
                         540, 760, 620, 230, vel=26, tam=60)

    def sonidos(self, dur):
        return [(0, "motor", dur), (self.tp("bomba", 0.85, dur), "golpe", 0.4)]


class C3(Escena):
    camara = (1.05, 1.15, 0.5, 0.62)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (60, 40, 30)), (1, (30, 20, 16))]))
            for i in range(0, W, 50):
                L.linea([(i, 0), (i, H)], (66, 44, 34), 6)
            L.forma([(120, 860), (960, 860), (1000, 980), (80, 980)], (110, 70, 40), suave=False)  # tapa
            L.forma([(80, 1000), (1000, 1000), (1000, 1600), (80, 1600)], (120, 78, 46), suave=False,
                    intensidad=0.05)
            L.forma([(120, 1040), (960, 1040), (960, 1560), (120, 1560)], (40, 34, 30), suave=False,
                    intensidad=0.03)
            for i in range(8):
                x = 200 + i * 80
                L.forma(capsula((x, 1120), (x, 1360), 56, 56), (200, 40, 40), intensidad=0.18)
                L.linea([(x - 28, 1200), (x + 28, 1200)], (240, 200, 70), 6)
            L.forma([(820, 1150), (930, 1150), (930, 1350), (820, 1350)], (30, 30, 34), suave=False)
            L.forma([(840, 1130), (910, 1130), (910, 1152), (840, 1152)], (200, 170, 70), suave=False)
            r = random.Random(4)
            for i in range(9):
                x0 = 200 + i * 80
                pts = [(x0, 1360), (x0 + r.randint(-60, 60), 1450), (870, 1400 + r.randint(-40, 40)), (875, 1350)]
                L.linea(catmull(pts, 6, cerrado=False), [(230, 60, 50), (60, 120, 220), (240, 200, 60)][i % 3], 7)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        tp = self.tp("paracaidas", 0.8, dur)
        if t > tp:
            d = ImageDraw.Draw(img)
            for i in range(4):
                q = ease((t - tp - i * 0.12) / 0.5)
                if q > 0:
                    _paracaidas(d, 180 + i * 240, -150 + 920 * q, 1.0)
        return img

    def encima(self, img, t, dur):
        tm = self.tp("maletin", 0.1, dur)
        chip(img, t, tm, "EL MALETÍN", y=260, fondo=(40, 40, 46), tam=40, dur=self.tp("exigio", 0.5, dur) - tm)
        numero(img, t, self.tp("doscientos", 0.55, dur), "$200.000", "dólares", y=420, color=(140, 220, 120))
        if t > self.tp("paracaidas", 0.8, dur) + 0.6:
            chip(img, t, self.tp("paracaidas", 0.8, dur) + 0.6, "+ 4 PARACAÍDAS", y=1140, fondo=NAR, tam=44)

    def sonidos(self, dur):
        return [(0, "latido", dur), (self.tp("dolares", 0.6, dur), "billetes", 0.8)]


class C4(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_pista(noche=True)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        dibujar_avion(img, "727", 700, 1080, 1.25)
        for i, p in enumerate(PASAJEROS):
            p.dibujar(img, 420 - t * 90 - i * 120, 1650 + i * 30, 0.7, t + i, pose="caminar", vel=1.2, espejo=True)
        tc = self.tp("dinero", 0.45, dur)
        if t > tc - 0.8:
            AGENTE.dibujar(img, 900 - (t - tc + 0.8) * 70, 1700, 0.85, t, pose="sostener", vel=1.0)
            d = ImageDraw.Draw(img)
            bx = 900 - (t - tc + 0.8) * 70
            d.rounded_rectangle((bx - 70, 1300, bx + 70, 1400), radius=24, fill=(190, 170, 110), outline=TINTA, width=5)
            d.text((bx, 1350), "$", font=pro.fuente(60), fill=(60, 90, 50), anchor="mm")
        particulas(img, t, "lluvia", 60, viento=-80, alfa=200)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.2, "izq", 220, "escala", "SEATTLE", "boleto", emoji="🛬")
        tarjeta(img, t, self.tp("mexico", 0.7, dur), "der", 440, "nuevo destino", "MÉXICO", "boleto", emoji="🌵")
        chip(img, t, self.tp("bajo", 0.85, dur), "BAJO Y DESPACIO", y=760, fondo=TEAL, tam=44)

    def sonidos(self, dur):
        return [(0, "motor", dur)]


class C5(Escena):
    camara = (1.0, 1.06, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.cielo = _grad(W, H, [(0, (8, 10, 24)), (1, (34, 40, 66))])

    def tiempos(self, dur):
        return self.tp("abrio", 0.35, dur), self.tp("salto", 0.85, dur)

    def mundo(self, t, dur):
        img = self.cielo.copy()
        nubes(img, t, n=8, y0=300)
        ta, ts = self.tiempos(dur)
        esc = ease((t - ta) / 1.2) if t > ta else 0.0
        dibujar_avion(img, "727", 600, 760 + 12 * math.sin(t * 2), 1.2, escalera=round(esc * 4) / 4)
        if t > ts:
            q = t - ts
            d = ImageDraw.Draw(img)
            x, y = 330 - 60 * q, 900 + 420 * q * q
            from alcatraz import silueta
            silueta(d, x, y, 0.55, t, agachado=False, col=(10, 10, 16))
        particulas(img, t, "lluvia", 110, viento=-500, alfa=220)
        for t0 in (0.6, ts + 0.4, dur - 0.6):
            relampago(img, t, t0)
        return img

    def sacudida(self, t, dur):
        return 0.5 if t > self.tiempos(dur)[0] else 0.15

    def encima(self, img, t, dur):
        chip(img, t, 0.15, "EN PLENA TORMENTA", y=260, fondo=(20, 24, 40), tam=44)
        ta, ts = self.tiempos(dur)
        tarjeta(img, t, ta + 0.1, "der", 1060, "escalera trasera", "ABIERTA", "boleto", emoji="🪜",
                dur=ts - ta - 0.2)

    def sonidos(self, dur):
        ta, ts = self.tiempos(dur)
        return [(0, "motor", dur), (0, "lluvia", dur), (ta, "viento", dur - ta), (0.6, "trueno", 2.0),
                (ts + 0.4, "trueno", 2.0)]


class C6(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (10, 16, 30)), (1, (24, 40, 50))]))
            pinos(L, 1200, 22, 600, (24, 46, 44), 1)
            pinos(L, 1500, 16, 800, (18, 36, 34), 2)
            L.forma([(0, 1500), (W, 1500), (W, H), (0, H)], (20, 32, 28), suave=False, borde=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        pro.particulas(img, t, "lluvia", 40, viento=-60, alfa=140)
        for i in range(3):
            x = 150 + i * 330 + 40 * math.sin(t * 0.8 + i)
            AGENTE.dibujar(img, x, 1760 + (i % 2) * 40, 0.7, t + i, pose="caminar", vel=0.6)
            ang = math.sin(t * 1.3 + i) * 0.5 - 1.2
            capa = Image.new("L", (W // 4, H // 4), 0)
            d4 = ImageDraw.Draw(capa)
            x0, y0 = x + 60, 1500
            d4.polygon([(x0 / 4, y0 / 4), ((x0 + 900 * math.cos(ang - 0.15)) / 4, (y0 + 900 * math.sin(ang - 0.15)) / 4),
                        ((x0 + 900 * math.cos(ang + 0.15)) / 4, (y0 + 900 * math.sin(ang + 0.15)) / 4)], fill=110)
            luz = Image.new("RGBA", (W, H), (255, 245, 200, 0))
            luz.putalpha(capa.filter(ImageFilter.GaussianBlur(4)).resize((W, H)))
            img.alpha_composite(luz)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("busqueda", 0.2, dur), "izq", 220, "búsqueda", "bosques de Washington", "boleto",
                emoji="🔦")
        sello(img, t, self.tp("paracaidas", 0.85, dur), "SIN RASTRO", W / 2, 760, ang=-10, color=(220, 90, 40))

    def sonidos(self, dur):
        return [(0, "lluvia", dur), (self.tp("paracaidas", 0.85, dur), "sello", 0.3)]


class C7(Escena):
    camara = (1.0, 1.12, 0.5, 0.65)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (120, 180, 230)), (0.5, (210, 230, 240)), (1, (210, 230, 240))]))
            pinos(L, 980, 18, 300, (60, 110, 80), 5)
            L.forma([(0, 980), (W, 980), (W, 1300), (0, 1300)], (70, 120, 160), suave=False, borde=False)
            for i in range(14):
                y = 1000 + i * 22
                L.linea([((i * 97) % W, y), ((i * 97) % W + 120, y)], (150, 190, 220), 5)
            L.forma(catmull([(0, 1300), (W, 1280), (W, H), (0, H)], 3), (226, 204, 150), borde=False)
            r = random.Random(2)
            for _ in range(40):
                L.circulo(r.randint(0, W), r.randint(1320, H), r.choice((3, 5)), (200, 176, 120), borde=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        te = self.tp("encontro", 0.4, dur)
        for i in range(5):
            _billetes(d, 560 + (i % 3) * 120 - 60, 1700 + (i // 3) * 60, podrido=True)
        NINO.dibujar(img, 330, 1760, 0.75, t, pose="sostener" if t > te else "quieto",
                     expr="sorpresa" if t > te else "feliz")
        return img

    def encima(self, img, t, dur):
        chip(img, t, 0.15, "9 AÑOS DESPUÉS · 1980", y=260, fondo=(150, 70, 30), tam=42)
        numero(img, t, self.tp("seis", 0.5, dur), "$5.800", "billetes podridos", y=520, color=(140, 220, 120))
        tc = self.tp("coincidian", 0.85, dur)
        if t > tc:
            p = pop((t - tc) / 0.3)
            d = ImageDraw.Draw(img)
            for k, txt in enumerate(("RESCATE  L0071 3 4 8 2", "HALLADO  L0071 3 4 8 2")):
                y = 860 + k * 90
                d.rounded_rectangle((120, y - 36, 960, y + 36), radius=14, fill=(250, 244, 226, int(240 * p)),
                                    outline=TINTA, width=4)
                d.text((150, y), txt, font=maquina(40), fill=TINTA, anchor="lm")
            sello(img, t, tc + 0.4, "COINCIDEN", W / 2, 1100, ang=-8, color=(40, 150, 70), tam=80)

    def sonidos(self, dur):
        return [(0, "rio", dur), (self.tp("coincidian", 0.85, dur) + 0.4, "sello", 0.3)]


class C8(Escena):
    camara = (1.0, 1.1, 0.5, 0.55)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(120, 80, 50))
            for x in range(0, W, 120):
                L.forma([(x, 0), (x + 116, 0), (x + 116, 1300), (x, 1300)], (130, 88, 56), suave=False,
                        intensidad=0.04, borde=False)
            L.forma([(60, 500), (360, 500), (360, 1300), (60, 1300)], (110, 120, 130), suave=False)
            for i in range(4):
                y = 530 + i * 190
                L.forma([(80, y), (340, y), (340, y + 170), (80, y + 170)], (130, 140, 150), suave=False)
                L.forma([(180, y + 70), (240, y + 70), (240, y + 90), (180, y + 90)], (60, 60, 64), suave=False)
            L.forma([(0, 1300), (W, 1300), (W, H), (0, H)], (80, 50, 34), suave=False, borde=False)
            L.forma([(380, 1250), (1040, 1250), (1040, 1320), (380, 1320)], (100, 64, 40), suave=False)
        self.fondo = full(dib)
        pegar_glow(self.fondo, 900, 700, 400, "#ffd890", 0.4)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        tc = self.tp("cerro", 0.45, dur)
        abierta = 1 - ease((t - tc) / 0.5) if t > tc else 1.0
        x0, y0 = 460, 1100
        d.polygon([(x0, y0), (x0 + 500, y0), (x0 + 520, y0 + 150), (x0 - 20, y0 + 150)], fill=(220, 190, 120),
                  outline=TINTA)
        if abierta > 0.05:
            d.polygon([(x0, y0), (x0 + 500, y0), (x0 + 500 - 40 * abierta, y0 - 260 * abierta),
                       (x0 - 40 * abierta, y0 - 260 * abierta)], fill=(236, 206, 140), outline=TINTA)
        d.text((x0 + 250, y0 + 75), "CASO: D. B. COOPER", font=maquina(38), fill=TINTA, anchor="mm")
        AGENTE.dibujar(img, 950, 1780, 0.85, t, expr="cansado" if t > tc else "serio")
        return img

    def encima(self, img, t, dur):
        numero(img, t, self.tp("cuarenta", 0.25, dur), "45 AÑOS", "de búsqueda", y=330, color=MOST)
        sello(img, t, self.tp("resolver", 0.85, dur), "SIN RESOLVER", W / 2, 760, ang=-12, color=(200, 40, 40))

    def sonidos(self, dur):
        return [(self.tp("cerro", 0.45, dur) + 0.4, "golpe", 0.3), (self.tp("resolver", 0.85, dur), "sello", 0.3)]


class C9(Escena):  # final: tablero de detective + comentario escribiéndose + avioneta con cartel
    camara = (1.0, 1.04, 0.5, 0.5)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(170, 120, 80))
            r = random.Random(8)
            for _ in range(500):
                L.circulo(r.randint(0, W), r.randint(0, H), r.choice((2, 3)), (150, 104, 66), borde=False)
        img = full(dib)
        ret = COOPER.sprite.get(0, 0.75, 0, False, ("quieto", "serio")).crop((0, 0, 450, 420))
        g = ret.convert("LA").convert("RGBA")
        poster = Image.new("RGBA", (470, 560), (245, 240, 228, 255))
        dp = ImageDraw.Draw(poster)
        dp.text((235, 40), "F B I  ·  SE BUSCA", font=maquina(36), fill=(140, 30, 30), anchor="mm")
        poster.alpha_composite(g, (10, 90))
        dp.rectangle((0, 0, 469, 559), outline=(120, 100, 70), width=5)
        dp.text((235, 520), "«DAN COOPER»", font=maquina(34), fill=TINTA, anchor="mm")
        poster = poster.rotate(-3, expand=True, resample=Image.BICUBIC)
        sombra_suave(img, (300, 640, 300 + poster.width - 20, 640 + poster.height - 20), radio=6, alfa=130)
        img.alpha_composite(poster, (300, 620))
        self.pines = [(150, 520, "✈"), (930, 560, "$"), (170, 1330, "🪂"), (930, 1320, "?")]
        d = ImageDraw.Draw(img)
        for x, y, s in self.pines:
            d.line((x, y, 540, 900), fill=(200, 30, 30), width=5)
        for x, y, s in self.pines:
            d.rectangle((x - 80, y - 70, x + 80, y + 70), fill=(250, 246, 232), outline=TINTA, width=4)
            em = render_emoji({"✈": "✈️", "$": "💵", "🪂": "🪂", "?": "❓"}[s])
            if em is not None:
                em = em.resize((90, int(90 * em.height / em.width)), Image.LANCZOS)
                img.alpha_composite(em, (int(x - 45), int(y - em.height / 2)))
            d.ellipse((x - 12, y - 82, x + 12, y - 58), fill=(220, 40, 40), outline=TINTA, width=3)
        self.fondo = img

    def mundo(self, t, dur):
        return self.fondo.copy()

    def encima(self, img, t, dur):
        chip(img, t, self.tp("crees", 0.05, dur), "¿SOBREVIVIÓ AL SALTO?", y=260, fondo=(150, 60, 30), tam=54)
        te = self.tp("escribe", 0.3, dur)
        if t > te:
            p = pop((t - te) / 0.3)
            d = ImageDraw.Draw(img)
            caja = (90, 1060 - 70 * p, W - 90, 1060 + 70 * p)
            sombra_suave(img, caja, radio=34)
            d.rounded_rectangle(caja, radius=34, fill=(255, 255, 255, 250), outline=TINTA, width=5)
            txt = "Yo creo que..."
            n = int((t - te - 0.3) * 9)
            vis = txt[:max(0, min(len(txt), n))]
            d.text((150, 1060), vis + ("|" if int(t * 2.5) % 2 == 0 else ""), font=fuente_c(48), fill=(60, 60, 70),
                   anchor="lm")
            em = render_emoji("💬")
            if em is not None:
                em = em.resize((70, int(70 * em.height / em.width)), Image.LANCZOS)
                img.alpha_composite(em, (W - 180, int(1060 - em.height / 2)))
        ts = self.tp("suscribete", 0.7, dur)
        if t > ts:
            q = (t - ts) / 3.0
            x = W + 200 - (W + 900) * q
            y = 480
            d = ImageDraw.Draw(img)
            d.line((x + 120, y, x + 260, y), fill=TINTA, width=3)
            d.rectangle((x + 260, y - 45, x + 760, y + 45), fill=(255, 250, 235), outline=TINTA, width=4)
            d.text((x + 510, y), "SUSCRÍBETE  ✦", font=pro.fuente(46), fill=(200, 80, 30), anchor="mm")
            dibujar_avion(img, "helice", x, y, 0.32)

    def sonidos(self, dur):
        return [(self.tp("escribe", 0.3, dur) + 0.3, "teclas", 1.6), (self.tp("suscribete", 0.7, dur), "motor", 3.0)]


def fuente_c(t):
    return pro.fuente(t)


ESCENAS = {f"13_{i}": c for i, c in enumerate((C1, C2, C3, C4, C5, C6, C7, C8, C9), 1)}
JSON, AUDIO = "historias/historia_13_db_cooper.json", "audios/historia_13_voz.mp3"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--sin-audio", action="store_true")
    a = ap.parse_args()
    if a.preview:
        pro.preview(ESCENAS, JSON, AUDIO, "/tmp/claude-0/prev_13.png")
    else:
        pro.generar(Path(JSON), ESCENAS, ESTILO, AUDIO, a.sin_audio)
