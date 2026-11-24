#!/usr/bin/env python3
"""Historia 17: La Tregua de Navidad (1914) — noche nevada, velas, tarjetas navideñas, «Noche de paz»."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import pro
from pro import (BLANCO, Escena, H, W, bandera, chip, full, manuscrita, numero, particulas, tarjeta)
from alcatraz import maquina, sello
from caricatura import ease, pop
from cine import pegar_glow
from dinos import TINTA, Lienzo, _grad, capsula, catmull, elipse, oscuro, radius_ok, sombra_suave
from generar_short import render_emoji
from humanos import Humano

ESTILO = {"modo": "caja", "caja": (200, 30, 40), "texto": (255, 255, 255)}
ROJO = (200, 30, 40)


def britanico(i):
    pelos = [(120, 80, 40), (60, 42, 30), (200, 160, 90)]
    return Humano(ropa=(150, 130, 90), pantalon=(140, 120, 84), cinturon=True, sombrero="gorra_tommy",
                  pelo=pelos[i % 3], barba=i == 2)


def aleman(i):
    pelos = [(60, 42, 30), (180, 140, 80), (40, 30, 26)]
    return Humano(ropa=(110, 118, 100), pantalon=(100, 106, 92), cinturon=True, sombrero="pickelhaube",
                  pelo=pelos[i % 3], barba=i == 1)


BRIT = [britanico(i) for i in range(3)]
GER = [aleman(i) for i in range(3)]
OFICIAL = Humano(ropa=(90, 78, 56), pantalon=(80, 70, 50), cinturon=True, sombrero="gorra_tommy",
                 color_sombrero=(90, 78, 56), barba=True, pelo=(150, 150, 150))


def fondo_frente(hora="noche"):
    def dib(L):
        if hora == "noche":
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (8, 12, 30)), (0.55, (30, 40, 70)), (1, (30, 40, 70))]))
            r = random.Random(5)
            for _ in range(170):
                L.circulo(r.randint(0, W), r.randint(0, 1000), r.choice((1.5, 2, 3)), (240, 240, 255), borde=False)
            nieve = (190, 200, 222)
        elif hora == "amanecer":
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (120, 140, 180)), (0.5, (240, 200, 180)), (1, (240, 200, 180))]))
            nieve = (236, 238, 246)
        else:  # gris lluvia
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (90, 94, 100)), (1, (130, 130, 128))]))
            nieve = (110, 100, 86)
        r = random.Random(2)
        for x in (120, 380, 760, 980):
            h = r.randint(140, 260)
            L.forma([(x - 14, 1150), (x - 10, 1150 - h), (x + 10, 1150 - h - 20), (x + 14, 1150)],
                    (40, 36, 34) if hora != "amanecer" else (90, 80, 76), suave=False)
        L.forma(catmull([(-50, 1150), (W + 50, 1130), (W + 50, H), (-50, H)], 3), nieve, borde=False)
        for cx, cy in ((300, 1500), (760, 1650), (520, 1300)):
            L.forma(elipse(cx, cy, 120, 34), oscuro(nieve, 0.85), sombra=False, brillo=False, ancho=3)
        for lado in (0, 1):
            x0 = 0 if lado == 0 else W - 200
            for k in range(6):
                y = 1200 + k * 110
                L.forma(catmull([(x0, y), (x0 + 200, y - 10), (x0 + 200, y + 50), (x0, y + 60)], 3), (150, 130, 100),
                        intensidad=0.12, ancho=4)
        for x in range(250, 850, 120):
            L.linea([(x, 1180), (x, 1260)], (60, 50, 44), 8)
        L.linea([(250 + k * 20, 1200 + 25 * math.sin(k * 1.3)) for k in range(31)], (80, 76, 74), 3)
    return full(dib)


def vela(img, x, y, t, s=1.0, fase=0.0):
    d = ImageDraw.Draw(img)
    d.rectangle((x - 9 * s, y - 40 * s, x + 9 * s, y), fill=(245, 240, 225), outline=TINTA, width=2)
    fl = 1 + 0.15 * math.sin(t * 11 + fase)
    pegar_glow(img, x, y - 52 * s, 44 * s * fl, "#ffcf6a", 0.85)
    d.ellipse((x - 6 * s, y - 64 * s * fl, x + 6 * s, y - 44 * s), fill=(255, 236, 150))


def arbolito(img, x, y, t, s=1.0):
    d = ImageDraw.Draw(img)
    for k, w in enumerate((90, 70, 50)):
        yy = y - k * 50 * s
        d.polygon([(x - w * s, yy), (x, yy - 80 * s), (x + w * s, yy)], fill=(40, 110, 60), outline=TINTA)
    d.rectangle((x - 10 * s, y, x + 10 * s, y + 24 * s), fill=(110, 76, 46))
    for k in range(5):
        vela(img, x - 60 * s + k * 30 * s, y - 20 * s - (k % 2) * 40 * s, t, 0.45 * s, k)


def notas(img, t, x, y, n=5):
    d = ImageDraw.Draw(img)
    for i in range(n):
        f = (t * 0.45 + i / n) % 1
        nx = x + 60 * math.sin(t * 1.5 + i * 2) + (i - n / 2) * 60
        ny = y - 360 * f
        a = int(255 * (1 - f))
        d.ellipse((nx - 16, ny - 11, nx + 16, ny + 11), fill=(255, 236, 160, a))
        d.line((nx + 14, ny, nx + 14, ny - 60), fill=(255, 236, 160, a), width=6)
        d.line((nx + 14, ny - 60, nx + 36, ny - 44), fill=(255, 236, 160, a), width=6)


def parapeto(img, alemanes=True):
    d = ImageDraw.Draw(img)
    for k in range(9):
        x = -30 + k * 130
        d.rounded_rectangle((x, 1300, x + 150, 1390), radius=34, fill=(150, 130, 100), outline=TINTA, width=5)
    for k in range(8):
        x = 30 + k * 130
        d.rounded_rectangle((x, 1240, x + 150, 1320), radius=34, fill=(160, 140, 110), outline=TINTA, width=5)


# --------------------------------------------------------------------------- #
class T1(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_frente()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for k in range(7):
            vela(img, 60 + k * 30, 1200, t, 0.8, k)
            vela(img, W - 60 - k * 30, 1200, t, 0.8, k + 3)
        q = ease(t / max(self.tp("encontrarse", 0.85, dur), 0.1))
        BRIT[0].dibujar(img, 160 + 230 * q, 1720, 0.95, t, pose="caminar" if q < 1 else "saludar", vel=0.6)
        GER[0].dibujar(img, W - 160 - 230 * q, 1720, 0.95, t, pose="caminar" if q < 1 else "saludar", vel=0.6,
                       espejo=True)
        particulas(img, t, "nieve", 80, viento=-30)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.2, "izq", 220, "noche de navidad", "24 · 12 · 1914", "navidad", emoji="🎄")
        chip(img, t, self.tp("armas", 0.5, dur), "SIN ARMAS", y=520, fondo=ROJO, tam=48)

    def sonidos(self, dur):
        return [(0, "viento", dur), (0, "cajita", dur)]


class T2(Escena):
    camara = (1.0, 1.0, 0.5, 0.5)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, 1200, [(0, (40, 40, 60)), (1, (110, 90, 90))]))
            L.forma([(0, 600), (W, 600), (W, H), (0, H)], (100, 76, 56), suave=False, borde=False)
            for k in range(30):
                r = random.Random(k)
                L.circulo(r.randint(0, W), r.randint(640, H), r.choice((8, 12, 16)), (80, 60, 44), borde=False)
            for x0 in (140, 940):
                L.forma(catmull([(x0 - 110, 600), (x0 - 90, 980), (x0 + 90, 980), (x0 + 110, 600)], 3), (60, 44, 32),
                        intensidad=0.05)
                L.forma([(x0 - 90, 940), (x0 + 90, 940), (x0 + 90, 980), (x0 - 90, 980)], (120, 90, 60),
                        suave=False, borde=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for k in range(3):
            tt = (t + k * 1.3) % 3.2
            if tt < 0.5:
                pegar_glow(img, 200 + k * 320, 420, 160 * (1 - tt * 2) + 40, "#ffb060", 0.8)
        BRIT[1].dibujar(img, 140, 980, 0.55, t, expr="serio")
        GER[1].dibujar(img, 940, 980, 0.55, t, expr="serio", espejo=True)
        bandera(img, 60, 300, 160, 100, t, "reino")
        bandera(img, 880, 300, 160, 100, t, "alemania", fase=1)
        tc = self.tp("cincuenta", 0.85, dur)
        if t > tc:
            q = ease((t - tc) / 0.6)
            d = ImageDraw.Draw(img)
            x0, x1 = 270, 270 + (540 * q)
            d.line((x0, 760, x1, 760), fill=BLANCO, width=10)
            d.polygon([(x1 + 30, 760), (x1, 740), (x1, 780)], fill=BLANCO)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.15, "izq", 140, "1914", "Primera Guerra Mundial", "navidad", emoji="🪖")
        chip(img, t, self.tp("britanicos", 0.3, dur), "BRITÁNICOS", y=1100, fondo=(30, 50, 130), tam=38, x=180)
        chip(img, t, self.tp("alemanes", 0.35, dur), "ALEMANES", y=1100, fondo=(40, 40, 44), tam=38, x=900)
        numero(img, t, self.tp("cincuenta", 0.85, dur), "50 m", "entre trincheras", y=680, color=BLANCO, tam=130)
        chip(img, t, self.tp("barro", 0.7, dur), "trincheras llenas de barro", y=1250, fondo=(90, 66, 44), tam=38)

    def sonidos(self, dur):
        return [(0.6, "explosion_lejana", 2.0), (2.4, "explosion_lejana", 2.0), (4.5, "explosion_lejana", 2.0)]


class T3(Escena):
    camara = (1.0, 1.12, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_frente()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        tc = self.tp("cantar", 0.75, dur)
        for i, x in enumerate((200, 540, 880)):
            GER[i].dibujar(img, x, 1760, 0.9, t, expr="feliz" if t > tc else "normal", boca=0.5 if t > tc else 0)
        parapeto(img)
        tv = self.tp("velas", 0.3, dur)
        for i, x in enumerate((140, 400, 680, 940)):
            if t > tv + i * 0.2:
                arbolito(img, x, 1250, t, 0.8)
        if t > tc:
            notas(img, t, 540, 1100)
        particulas(img, t, "nieve", 60, viento=-20)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.15, "izq", 220, "trincheras alemanas", "velas y árboles", "navidad", emoji="🕯️")
        tarjeta(img, t, self.tp("noche", 0.85, dur) if self.tp("noche", 0.85, dur) > 1 else self.tp("paz", 0.9, dur),
                "der", 430, "cantaron", "«Noche de paz»", "navidad", emoji="🎶")

    def sonidos(self, dur):
        return [(0, "cajita", dur)]


class T4(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_frente()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for i, x in enumerate((200, 540, 880)):
            BRIT[i].dibujar(img, x, 1760, 0.9, t, expr="feliz", boca=0.5)
        parapeto(img)
        notas(img, t, 540, 1100)
        particulas(img, t, "nieve", 60, viento=-20)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.1, "der", 220, "del otro lado", "los británicos", "navidad", emoji="🇬🇧")
        chip(img, t, self.tp("villancicos", 0.7, dur), "♪ respondieron cantando ♪", y=560, fondo=ROJO, tam=42)

    def sonidos(self, dur):
        return [(0, "cajita", dur)]


class T5(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_frente("amanecer")

    def mundo(self, t, dur):
        img = self.fondo.copy()
        te = self.tp("enterraron", 0.85, dur)
        if t > te:
            d = ImageDraw.Draw(img)
            for k, x in enumerate((300, 460, 620, 780)):
                if t > te + k * 0.15:
                    d.rectangle((x - 8, 1080, x + 8, 1200), fill=(110, 80, 50), outline=TINTA, width=3)
                    d.rectangle((x - 36, 1110, x + 36, 1126), fill=(110, 80, 50), outline=TINTA, width=3)
        BRIT[0].dibujar(img, 380, 1740, 1.0, t, pose="saludar", expr="feliz")
        GER[0].dibujar(img, 700, 1740, 1.0, t, pose="saludar", expr="feliz", espejo=True)
        BRIT[2].dibujar(img, 130, 1680, 0.75, t, expr="feliz")
        GER[2].dibujar(img, 950, 1680, 0.75, t, expr="feliz", espejo=True)
        particulas(img, t, "nieve", 40, viento=-10, alfa=180)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.1, "izq", 220, "al amanecer", "tierra de nadie", "navidad", emoji="🤝")
        d = ImageDraw.Draw(img)
        for k, (pal, emoji) in enumerate((("chocolates", "🍫"), ("cigarros", "🚬"), ("botones", "🎖️"))):
            ti = self.tp(pal, 0.45 + 0.1 * k, dur)
            if t > ti:
                em = render_emoji(emoji)
                if em is not None:
                    p = pop((t - ti) / 0.3)
                    em = em.resize((max(1, int(130 * p)), max(1, int(130 * p * em.height / em.width))))
                    img.alpha_composite(em, (int(330 + k * 210 - em.width / 2), int(720 - em.height / 2)))
        chip(img, t, self.tp("enterraron", 0.85, dur), "enterraron juntos a sus muertos", y=880,
             fondo=(60, 60, 70), tam=38)

    def sonidos(self, dur):
        return [(0, "cajita", dur)]


class T6(Escena):
    camara = (1.0, 1.0, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_frente("amanecer")

    def mundo(self, t, dur):
        img = self.fondo.copy()
        bx = 540 + 330 * math.sin(t * 1.3)
        by = 1690 - abs(math.sin(t * 4)) * 240
        for i, base in enumerate((260, 820)):
            x = base + 120 * math.sin(t * 1.3 + i * 0.8)
            (BRIT if i == 0 else GER)[i].dibujar(img, x, 1760, 0.85, t * 1.5, pose="caminar", vel=1.6,
                                                 expr="feliz", espejo=i == 1)
        for i, base in enumerate((420, 660)):
            x = base + 80 * math.sin(t * 1.5 + i)
            (GER if i == 0 else BRIT)[1].dibujar(img, x, 1640, 0.7, t * 1.5 + 1, pose="caminar", vel=1.6,
                                                 expr="feliz", espejo=i == 0)
        d = ImageDraw.Draw(img)
        d.ellipse((bx - 34, by - 34, bx + 34, by + 34), fill=(150, 100, 60), outline=TINTA, width=5)
        d.line((bx - 30, by, bx + 30, by), fill=TINTA, width=3)
        return img

    def encima(self, img, t, dur):
        chip(img, t, self.tp("futbol", 0.2, dur), "⚽ PARTIDOS DE FÚTBOL".replace("⚽ ", ""), y=260, fondo=ROJO, tam=48)
        numero(img, t, self.tp("miles", 0.5, dur), "MILES", "de soldados", y=520, color=(255, 236, 160))
        tarjeta(img, t, self.tp("nuevo", 0.85, dur), "der", 760, "en algunos lugares", "hasta Año Nuevo", "navidad",
                emoji="📅")

    def sonidos(self, dur):
        return [(k * 0.77, "patada", 0.3) for k in range(int(dur / 0.77))]


class T7(Escena):
    camara = (1.0, 1.1, 0.5, 0.58)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(70, 66, 50))
            L.forma(catmull([(0, 0), (W / 2, 260), (W, 0)], 3) + [(W, 0), (0, 0)], (90, 86, 64), borde=False)
            L.forma([(0, 1350), (W, 1350), (W, H), (0, H)], (60, 50, 40), suave=False, borde=False)
            L.forma([(160, 1250), (920, 1250), (920, 1320), (160, 1320)], (110, 80, 50), suave=False)
        self.fondo = full(dib)
        pegar_glow(self.fondo, 540, 900, 420, "#ffd890", 0.35)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        OFICIAL.dibujar(img, 760, 1760, 1.05, t, expr="serio")
        d = ImageDraw.Draw(img)
        d.polygon([(240, 1180), (600, 1170), (610, 1250), (230, 1260)], fill=(244, 238, 220), outline=TINTA)
        for k in range(4):
            d.line((270, 1195 + k * 14, 570, 1190 + k * 14), fill=(150, 140, 120), width=3)
        return img

    def encima(self, img, t, dur):
        chip(img, t, self.tp("comandantes", 0.15, dur), "LOS COMANDANTES", y=300, fondo=(50, 46, 36), tam=46)
        sello(img, t, self.tp("prohibieron", 0.6, dur), "PROHIBIDO", W / 2, 640, ang=-10, color=ROJO, tam=110)
        chip(img, t, self.tp("nunca", 0.85, dur), "nunca volvió a ocurrir", y=900, fondo=(50, 46, 36), tam=42)

    def sonidos(self, dur):
        return [(self.tp("prohibieron", 0.6, dur), "sello", 0.3)]


class T8(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_frente("gris")

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        d.ellipse((500, 1600, 570, 1660), fill=(110, 80, 56), outline=TINTA, width=5)
        particulas(img, t, "lluvia", 90, viento=-100, alfa=200)
        return img

    def encima(self, img, t, dur):
        anio = 1915 + int(min(3, t / max(dur, 0.1) * 4))
        numero(img, t, 0.1, str(anio), "la guerra continuó", y=640, color=(230, 230, 230), tam=190)

    def sonidos(self, dur):
        return [(0, "lluvia", dur), (0.4, "explosion_lejana", 2.0)]


class T9(Escena):  # final: velas que escriben "PAZ" + regalo que se abre con "SUSCRÍBETE"
    camara = (1.0, 1.03, 0.5, 0.5)
    PUNTOS = ([(160, y) for y in (700, 787, 875, 962, 1050)] + [(225, 700), (295, 715), (335, 785), (295, 850),
                                                                  (225, 870)] +
              [(440, 1050), (473, 933), (506, 817), (540, 700), (573, 817), (606, 933), (640, 1050), (490, 935),
               (590, 935)] +
              [(730, 700), (800, 700), (870, 700), (940, 700), (885, 770), (830, 840), (775, 910), (730, 1050),
               (800, 1050), (870, 1050), (940, 1050)])

    def __init__(self):
        super().__init__()
        self.fondo = fondo_frente()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        oscuro_ = Image.new("RGBA", (W, H), (0, 0, 16, 90))
        img.alpha_composite(oscuro_)
        n = len(self.PUNTOS)
        tfin = max(self.tp("comentarios", 0.5, dur), 1.0)
        enc = int(n * min(1.0, t / tfin))
        k = enc / n
        if k > 0:
            capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dc = ImageDraw.Draw(capa)
            dc.text((W / 2, 875), "PAZ", font=pro.fuente(420), fill=(255, 200, 90, int(150 * k)), anchor="mm")
            img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(18)))
            img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(4)))
        for i, (x, y) in enumerate(self.PUNTOS[:enc]):
            vela(img, x, y + 40, t, 0.9, i)
        particulas(img, t, "nieve", 70, viento=-20)
        return img

    def encima(self, img, t, dur):
        chip(img, t, self.tp("escribe", 0.3, dur), "escribe «PAZ» en los comentarios", y=420, fondo=ROJO, tam=42)
        ts = self.tp("suscribete", 0.7, dur)
        d = ImageDraw.Draw(img)
        bx, by = W / 2, 1680
        abre = ease((t - ts) / 0.5) if t > ts else 0.0
        d.rectangle((bx - 170, by - 120, bx + 170, by + 90), fill=ROJO, outline=TINTA, width=6)
        d.rectangle((bx - 22, by - 120, bx + 22, by + 90), fill=(240, 200, 80))
        tapa_y = by - 150 - 140 * abre
        tapa = Image.new("RGBA", (400, 80), (0, 0, 0, 0))
        dt = ImageDraw.Draw(tapa)
        dt.rectangle((10, 20, 390, 70), fill=(220, 50, 60), outline=TINTA, width=6)
        dt.rectangle((178, 20, 222, 70), fill=(240, 200, 80))
        dt.ellipse((150, 0, 200, 30), outline=(240, 200, 80), width=8)
        dt.ellipse((200, 0, 250, 30), outline=(240, 200, 80), width=8)
        tapa = tapa.rotate(-25 * abre, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(tapa, (int(bx - tapa.width / 2 + 60 * abre), int(tapa_y)))
        if abre > 0.3:
            p = pop((t - ts - 0.2) / 0.35)
            y = by - 180 - 120 * p
            caja = (bx - 260 * p, y - 55 * p, bx + 260 * p, y + 55 * p)
            sombra_suave(img, caja, radio=20, alfa=110)
            d.rounded_rectangle(caja, radius=radius_ok(20 * p), fill=(250, 244, 228), outline=ROJO, width=6)
            d.text((bx, y), "SUSCRÍBETE", font=pro.fuente(max(8, int(56 * p))), fill=ROJO, anchor="mm")
            for k in range(10):
                a = k / 10 * 2 * math.pi + t
                pegar_glow(img, bx + 300 * p * math.cos(a), y + 120 * p * math.sin(a), 14, "#ffe39a", 0.8)

    def sonidos(self, dur):
        return [(0, "cajita", dur), (self.tp("suscribete", 0.7, dur), "pop", 0.2)]


ESCENAS = {f"17_{i}": c for i, c in enumerate((T1, T2, T3, T4, T5, T6, T7, T8, T9), 1)}
JSON, AUDIO = "historias/historia_17_tregua_navidad.json", "audios/historia_17_voz.mp3"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--sin-audio", action="store_true")
    a = ap.parse_args()
    if a.preview:
        pro.preview(ESCENAS, JSON, AUDIO, "/tmp/claude-0/prev_17.png")
    else:
        pro.generar(Path(JSON), ESCENAS, ESTILO, AUDIO, a.sin_audio, pad_hz=(65.4, 98, 130.8))
