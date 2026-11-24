#!/usr/bin/env python3
"""Historia 14: Los 33 mineros de Chile — estilo industrial (placas metálicas, contador de días)."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import pro
from pro import BLANCO, Escena, H, W, bandera, chip, full, numero, papel_manuscrito, tarjeta
from alcatraz import maquina, sello
from caricatura import ease, pop
from cine import pegar_glow
from dinos import TINTA, _grad, capsula, catmull, elipse, oscuro, radius_ok, sombra_suave
from generar_short import render_emoji
from humanos import Humano

ESTILO = {"modo": "caja", "caja": (250, 200, 30), "texto": (20, 20, 20)}
AMARILLO = (250, 200, 30)


def minero(i, lentes=False):
    cols = [(70, 72, 78), (90, 70, 60), (60, 70, 90), (80, 80, 70)]
    pelos = [(40, 30, 26), (60, 42, 30), (30, 30, 30), (90, 60, 40)]
    return Humano(ropa=cols[i % 4], pantalon=(50, 52, 60), chaleco=(240, 130, 40), sombrero="casco_minero",
                  barba=True, pelo=pelos[i % 4], lentes=lentes)


MINEROS = [minero(i) for i in range(4)]
RESCATADO = minero(1, lentes=True)
FAMILIA = [Humano(ropa=c, pelo=p, peinado=pe) for c, p, pe in (((170, 60, 70), (40, 30, 26), "largo"),
                                                               ((60, 90, 140), (60, 42, 30), "corto"),
                                                               ((200, 150, 60), (30, 26, 24), "trenza"),
                                                               ((90, 130, 90), (120, 80, 50), "rizado"))]


def contador_dia(img, n, t=0.0, pulso=0.0):
    if n is None:
        return
    txt = f"DÍA {int(n)}"
    f = maquina(46)
    d = ImageDraw.Draw(img)
    w = d.textlength(txt, font=f) + 60
    x1, y0 = W - 40, 130
    esc = 1 + 0.12 * pulso
    caja = (x1 - w * esc, y0, x1, y0 + 80 * esc)
    sombra_suave(img, caja, radio=6, alfa=120)
    d.rectangle(caja, fill=(40, 42, 46), outline=AMARILLO, width=5)
    d.text(((caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2), txt, font=f, fill=AMARILLO, anchor="mm")


# --------------------------------------------------------------------------- #
TUNEL = [(300, 400), (820, 520), (250, 660), (830, 800), (240, 940), (820, 1080), (260, 1220), (760, 1360),
         (560, 1480)]
REFUGIO = (560, 1500)


def fondo_corte():
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, 820, [(0, (120, 170, 220)), (1, (240, 210, 170))]))
        pro.montanas(L, 400, [(200, 500, 160), (650, 600, 220), (1000, 500, 150)], (170, 120, 80), nieve=False)
        cols = [(176, 126, 80), (156, 106, 66), (136, 92, 58), (120, 80, 50), (104, 70, 44), (90, 60, 40)]
        y = 400
        for i, h in enumerate((140, 200, 240, 260, 320, 600)):
            L.forma([(0, y), (W, y), (W, y + h), (0, y + h)], cols[i], suave=False, borde=False, sombra=False,
                    brillo=False)
            y += h
        r = random.Random(3)
        for _ in range(350):
            L.circulo(r.randint(0, W), r.randint(420, H), r.choice((3, 5, 7)), (70, 48, 32), borde=False)
        L.linea(TUNEL, (40, 28, 20), 46)
        L.linea(TUNEL, (70, 50, 36), 28)
        L.forma(catmull([(400, 1450), (720, 1450), (740, 1560), (380, 1560)], 3), (60, 44, 32), intensidad=0.05)
        L.forma([(250, 400), (350, 400), (350, 350), (250, 350)], (60, 50, 44), suave=False)
        for k in range(8):  # regla de profundidad
            y = 400 + k * 1100 / 7
            L.linea([(40, y), (80, y)], (250, 240, 220), 5)
        L.linea([(40, 400), (40, 1500)], (250, 240, 220), 5)
    img = full(dib)
    d = ImageDraw.Draw(img)
    for k in range(8):
        y = 400 + k * 1100 / 7
        d.text((90, y), f"{k * 100} m", font=maquina(30), fill=(250, 240, 220), anchor="lm")
    return img


def derrumbe(img, t, t0, base_rocas=True):
    d = ImageDraw.Draw(img)
    r = random.Random(5)
    x0, y0, x1, y1 = 240, 940, 820, 1080
    for i in range(22):
        f = (i + 0.5) / 22
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        caida = 1.0 if t0 is None else min(1.0, max(0.0, (t - t0) * 2 - i * 0.03))
        yy = y - (1 - caida) * 140
        rr = r.randint(30, 46)
        d.polygon([(x - rr, yy), (x - rr * 0.3, yy - rr), (x + rr, yy - rr * 0.6), (x + rr * 0.8, yy + rr * 0.5),
                   (x - rr * 0.6, yy + rr * 0.7)], fill=(150, 126, 104), outline=TINTA)


def lamparas(img, t, n=6):
    for i in range(n):
        x = REFUGIO[0] - 120 + i * 48
        pegar_glow(img, x, REFUGIO[1] - 10 + 4 * math.sin(t * 3 + i), 26, "#fff3b0", 0.9)


class M1(Escena):
    camara = (1.0, 1.0, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_corte()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        td = self.tp("derrumbo", 0.35, dur)
        if t > td:
            derrumbe(img, t, td)
            if t - td < 1.5:
                pegar_glow(img, 530, 1010, 260 * (1 + t - td), "#b89878", 0.8 * (1 - (t - td) / 1.5))
        lamparas(img, t)
        return img

    def sacudida(self, t, dur):
        td = self.tp("derrumbo", 0.35, dur)
        return 1.6 * max(0.0, 1 - (t - td) / 1.2) if t > td else 0.0

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.15, "izq", 200, "5 ago 2010", "Mina San José", "placa", emoji="⛏️")
        numero(img, t, self.tp("treinta", 0.6, dur), "33", "mineros atrapados", y=1150, color=AMARILLO)
        tm = self.tp("setecientos", 0.85, dur)
        if t > tm:
            chip(img, t, tm, "← 700 m bajo tierra", y=1600, fondo=(40, 42, 46), color=AMARILLO, tam=44, x=700)
        if t > self.tp("derrumbo", 0.35, dur):
            contador_dia(img, 1)

    def sonidos(self, dur):
        return [(self.tp("derrumbo", 0.35, dur), "derrumbe", 3.0)]


class M2(Escena):
    camara = (1.0, 1.1, 0.5, 0.62)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(50, 36, 28))
            r = random.Random(7)
            for _ in range(60):
                x, y = r.randint(-50, W), r.randint(-50, 1300)
                L.forma(elipse(x, y, r.randint(60, 160), r.randint(40, 110), r.uniform(-1, 1)),
                        (70 + r.randint(0, 20), 52, 40), sombra=False, brillo=False, ancho=3)
            L.forma(catmull([(0, 1350), (W, 1300), (W, H), (0, H)], 3), (80, 60, 46), borde=False)
            L.forma([(240, 1240), (840, 1240), (860, 1290), (220, 1290)], (140, 100, 60), suave=False)
            for x in (260, 800):
                L.forma([(x, 1290), (x + 20, 1290), (x + 20, 1450), (x, 1450)], (110, 76, 46), suave=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for i, x in enumerate((180, 900)):
            MINEROS[i].dibujar(img, x, 1700, 0.8, t, pose="sentado", expr="cansado", espejo=i == 1)
        for x in (180, 900, 540):
            pegar_glow(img, x + 10, 1060 + 4 * math.sin(t * 3 + x), 160, "#fff3b0", 0.35)
        d = ImageDraw.Draw(img)
        for palabra, defecto, x, emoji in (("atun", 0.45, 380, "🥫"), ("leche", 0.62, 540, "🥛"),
                                           ("galleta", 0.75, 700, "🍪")):
            ti = self.tp(palabra, defecto, dur)
            if t > ti:
                em = render_emoji(emoji)
                if em is not None:
                    p = pop((t - ti) / 0.3)
                    em = em.resize((max(1, int(130 * p)), max(1, int(130 * p * em.height / em.width))))
                    img.alpha_composite(em, (int(x - em.width / 2), int(1240 - em.height)))
        MINEROS[2].dibujar(img, 540, 1780, 0.95, t, pose="sostener", expr="serio")
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("cada", 0.88, dur), "izq", 200, "ración", "cada 48 horas", "placa", emoji="⏱️")
        contador_dia(img, 2 + 14 * min(1.0, t / dur))

    def sonidos(self, dur):
        return [(0, "reloj", dur)]


class M3(Escena):
    camara = (1.0, 1.1, 0.5, 0.62)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (10, 14, 34)), (0.6, (40, 40, 70)), (1, (40, 40, 70))]))
            r = random.Random(2)
            for _ in range(180):
                L.circulo(r.randint(0, W), r.randint(0, 1000), r.choice((1.5, 2, 3)), (240, 240, 255), borde=False)
            pro.montanas(L, 1150, [(200, 600, 260), (800, 700, 320)], (60, 46, 50), nieve=False)
            L.forma([(0, 1150), (W, 1150), (W, H), (0, H)], (120, 90, 66), suave=False, borde=False)
            for x, s in ((150, 1.0), (820, 1.2), (480, 0.8)):
                L.forma([(x - 150 * s, 1250), (x, 1250 - 180 * s), (x + 150 * s, 1250)], (60, 100, 150),
                        suave=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for x, s in ((150, 1.0), (820, 1.2), (480, 0.8)):
            pegar_glow(img, x, 1200, 110 * s, "#ffcf7a", 0.5)
        bandera(img, 980, 760, 160, 110, t, "chile")
        bandera(img, 90, 820, 130, 90, t, "chile", fase=1.0)
        for i, (p, x) in enumerate(zip(FAMILIA, (190, 420, 650, 880))):
            p.dibujar(img, x, 1720 + (i % 2) * 40, 0.8, t, expr="triste" if t < dur * 0.5 else "serio")
        d = ImageDraw.Draw(img)
        for i in range(9):
            x = 120 + i * 105
            d.rectangle((x - 8, 1830, x + 8, 1870), fill=(240, 236, 220), outline=TINTA, width=2)
            pegar_glow(img, x, 1820 + 3 * math.sin(t * 7 + i), 28, "#ffd27a", 0.9)
        te = self.tp("esperanza", 0.8, dur)
        if t > te:
            p = pop((t - te) / 0.35)
            caja = (540 - 360 * p, 520 - 70 * p, 540 + 360 * p, 520 + 70 * p)
            d.rectangle(caja, fill=(150, 104, 60), outline=TINTA, width=6)
            if p > 0.5:
                d.text((540, 520), "CAMPAMENTO ESPERANZA", font=maquina(int(44 * p)), fill=(250, 240, 210),
                       anchor="mm")
            d.line((540, 590, 540, 1100), fill=(110, 76, 46), width=16)
        return img

    def encima(self, img, t, dur):
        chip(img, t, 0.2, "¿ESTARÁN VIVOS?", y=300, fondo=(40, 42, 46), color=AMARILLO, tam=50,
             dur=self.tp("familias", 0.4, dur) - 0.2)
        contador_dia(img, 16)


class M4(Escena):
    camara = (1.0, 1.08, 0.5, 0.58)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (110, 170, 230)), (0.6, (240, 220, 180)), (1, (240, 220, 180))]))
            pro.montanas(L, 1100, [(200, 600, 260), (800, 700, 330)], (170, 120, 80), nieve=False)
            L.forma([(0, 1100), (W, 1100), (W, H), (0, H)], (200, 160, 110), suave=False, borde=False)
            L.forma([(420, 1250), (470, 450), (610, 450), (660, 1250)], (230, 120, 40), suave=False, intensidad=0.06)
            for y in range(500, 1250, 110):
                L.linea([(450, y), (630, y + 100)], (180, 90, 30), 8)
                L.linea([(630, y), (450, y + 100)], (180, 90, 30), 8)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        ts = self.tp("sacaron", 0.4, dur)
        sube = ease((t - ts) / 1.0) if t > ts else 0.0
        d = ImageDraw.Draw(img)
        d.rectangle((525, 1250 - 500 * sube, 555, 1260), fill=(120, 120, 126), outline=TINTA, width=3)
        tp_ = self.tp("papel", 0.55, dur)
        for i, (p, x) in enumerate(zip(FAMILIA + MINEROS[:1], (150, 330, 760, 930, 250))):
            p.dibujar(img, x, 1760 + (i % 2) * 40, 0.75, t, pose="celebrar" if t > tp_ + 1.5 else "quieto",
                      expr="feliz" if t > tp_ + 1.5 else "sorpresa")
        return img

    def encima(self, img, t, dur):
        td = self.tp("diecisiete", 0.1, dur)
        contador_dia(img, 17, pulso=max(0.0, 1 - (t - td) / 0.5) if t > td else 0.0)
        chip(img, t, td, "LA SONDA LLEGÓ", y=300, fondo=(40, 42, 46), color=AMARILLO, tam=46,
             dur=self.tp("papel", 0.55, dur) - td - 0.2)
        papel_manuscrito(img, t, self.tp("papel", 0.55, dur), ["Estamos bien", "en el refugio", "los 33"],
                         540, 700, 600, 300, vel=18, tam=70, color=(200, 20, 30))

    def sonidos(self, dur):
        tp_ = self.tp("papel", 0.55, dur)
        return [(0, "perforadora", self.tp("sacaron", 0.4, dur)), (tp_ + 1.5, "aplausos", 3.0)]


class M5(Escena):
    camara = (1.0, 1.0, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_corte()
        derrumbe(self.fondo, 1, None)
        d = ImageDraw.Draw(self.fondo)
        d.line((760, 400, 640, 1460), fill=(30, 22, 16), width=14)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        prog = min(1.0, t / dur)
        d.line((560, 400, 560, 400 + 1040 * prog), fill=(30, 22, 16), width=46)
        f = (t * 0.45) % 1
        k = f * 2 if f < 0.5 else 2 - f * 2
        px, py = 760 - 120 * k, 400 + 1060 * k
        d.rounded_rectangle((px - 14, py - 50, px + 14, py + 50), radius=10, fill=(200, 200, 206), outline=TINTA,
                            width=3)
        lamparas(img, t)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("palomas", 0.25, dur), "izq", 190, "«palomas»", "tubos de envío", "placa", emoji="📦")
        for i, (pal, txt, y) in enumerate((("comida", "COMIDA", 760), ("cartas", "CARTAS", 860),
                                           ("medicinas", "MEDICINAS", 960))):
            chip(img, t, self.tp(pal, 0.45 + 0.1 * i, dur), txt, y=y, fondo=(40, 42, 46), color=AMARILLO, tam=40,
                 x=880)
        chip(img, t, self.tp("perforaban", 0.8, dur), "PERFORANDO EL RESCATE…", y=1660, fondo=(200, 90, 20), tam=40)
        contador_dia(img, 18 + 50 * min(1.0, t / dur))

    def sonidos(self, dur):
        return [(self.tp("perforaban", 0.8, dur), "perforadora", dur - self.tp("perforaban", 0.8, dur))]


class M6(Escena):
    camara = (1.0, 1.0, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_corte()
        derrumbe(self.fondo, 1, None)
        d = ImageDraw.Draw(self.fondo)
        d.line((560, 400, 560, 1460), fill=(30, 22, 16), width=60)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        f = (t / 2.6) % 1
        y = 1440 - 1040 * ease(f)
        d.rounded_rectangle((536, y - 80, 584, y + 80), radius=20, fill=(245, 245, 245), outline=TINTA, width=4)
        d.rectangle((536, y - 20, 584, y), fill=(214, 40, 50))
        d.rectangle((536, y - 40, 584, y - 20), fill=(40, 60, 160))
        pegar_glow(img, 560, y, 70, "#ffffff", 0.35)
        lamparas(img, t)
        return img

    def encima(self, img, t, dur):
        t69 = self.tp("sesenta", 0.05, dur)
        contador_dia(img, 69, pulso=max(0.0, 1 - (t - t69) / 0.5) if t > t69 else 0.0)
        tarjeta(img, t, self.tp("fenix", 0.35, dur), "izq", 190, "cápsula", "FÉNIX", "placa", emoji="🚀")
        tm = self.tp("millones", 0.7, dur)
        if t > tm:
            chip(img, t, tm, "● EN VIVO · MILLONES DE PERSONAS", y=1660, fondo=(200, 30, 40), tam=40)

    def sonidos(self, dur):
        return [(0, "perforadora", 1.0), (self.tp("millones", 0.7, dur), "aplausos", 2.5)]


class M7(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (8, 12, 28)), (0.6, (30, 34, 60)), (1, (30, 34, 60))]))
            L.forma([(0, 1200), (W, 1200), (W, H), (0, H)], (110, 86, 64), suave=False, borde=False)
            L.forma([(380, 1250), (700, 1250), (680, 1300), (400, 1300)], (90, 90, 96), suave=False)
            L.forma([(520, 1250), (500, 300), (580, 300), (560, 1250)], (230, 120, 40), suave=False)
        self.fondo = full(dib)
        for x in (100, 980):
            pegar_glow(self.fondo, x, 300, 420, "#fff6d0", 0.5)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((470, 900, 610, 1260), radius=40, fill=(245, 245, 245), outline=TINTA, width=6)
        d.rectangle((470, 1060, 610, 1100), fill=(214, 40, 50))
        d.rectangle((470, 1020, 610, 1060), fill=(40, 60, 160))
        tu = self.tp("ultimo", 0.6, dur)
        quien = RESCATADO if t < tu else MINEROS[3]
        quien.dibujar(img, 300 if t < tu else 780, 1760, 1.0, t, pose="celebrar", expr="feliz")
        FAMILIA[0 if t < tu else 1].dibujar(img, 820 if t < tu else 260, 1760, 0.9, t, pose="saludar", expr="feliz")
        return img

    def encima(self, img, t, dur):
        tu = self.tp("ultimo", 0.6, dur)
        tarjeta(img, t, self.tp("primero", 0.1, dur), "izq", 190, "el primero", "Florencio Ávalos", "placa",
                emoji="1️⃣", dur=tu - self.tp("primero", 0.1, dur) - 0.3)
        tarjeta(img, t, tu, "der", 190, "el último · jefe de turno", "Luis Urzúa", "placa", emoji="🏁")
        contador_dia(img, 69)
        chip(img, t, 0.3, "usaban lentes oscuros para proteger los ojos", y=520, fondo=(40, 42, 46), tam=32,
             dur=1.8)

    def sonidos(self, dur):
        return [(0, "aplausos", 2.5), (self.tp("ultimo", 0.6, dur), "aplausos", 3.0)]


class M8(Escena):  # final: bandera + 33 + "¿dónde estabas?" + lámpara que enciende "SUSCRÍBETE"
    camara = (1.0, 1.05, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.fondo = _grad(W, H, [(0, (12, 14, 30)), (1, (40, 34, 50))])

    def mundo(self, t, dur):
        img = self.fondo.copy()
        bandera(img, 140, 300, 800, 520, t, "chile")
        for i in range(4):
            MINEROS[i].dibujar(img, 150 + i * 260, 1910, 0.55, t + i, pose="celebrar", expr="feliz")
        return img

    def encima(self, img, t, dur):
        numero(img, t, 0.1, "33", "vivos", y=950, color=(255, 255, 255), tam=220)
        tq = self.tp("donde", 0.1, dur)
        if t > tq:
            p = pop((t - tq) / 0.3)
            d = ImageDraw.Draw(img)
            caja = (W / 2 - 400 * p, 1220 - 75 * p, W / 2 + 400 * p, 1220 + 75 * p)
            sombra_suave(img, caja, radio=36)
            d.rounded_rectangle(caja, radius=radius_ok(36 * p), fill=(255, 255, 255, 248), outline=TINTA, width=6)
            d.text((W / 2 + 30, 1220), "¿DÓNDE ESTABAS TÚ?", font=pro.fuente(int(56 * p)), fill=TINTA, anchor="mm")
            em = render_emoji("📍")
            if em is not None and p > 0.4:
                caida = min(1.0, (t - tq - 0.2) / 0.4)
                em = em.resize((80, int(80 * em.height / em.width)))
                img.alpha_composite(em, (int(W / 2 - 370), int(1180 - 200 * (1 - max(0.0, caida)))))
        ts = self.tp("suscribete", 0.7, dur)
        if t > ts:
            p = pop((t - ts) / 0.35)
            d = ImageDraw.Draw(img)
            caja = (W / 2 - 300 * p, 1650 - 65 * p, W / 2 + 300 * p, 1650 + 65 * p)
            sombra_suave(img, caja, radio=10, alfa=140)
            d.rectangle(caja, fill=(36, 38, 42), outline=AMARILLO, width=6)
            if p > 0.5:
                d.text((W / 2 + 40, 1650), "SUSCRÍBETE", font=maquina(int(62 * p)), fill=AMARILLO, anchor="mm")
                d.ellipse((W / 2 - 270, 1620, W / 2 - 210, 1680), fill=AMARILLO, outline=TINTA, width=4)
                pegar_glow(img, W / 2 - 240, 1650, 70 + 20 * math.sin(t * 6), "#fff6c0", 0.9)
                barre = (t - ts) * 900 % 1400 - 200
                pegar_glow(img, W / 2 - 300 + barre, 1650, 90, "#fff2a0", 0.35)

    def sonidos(self, dur):
        return [(0, "aplausos", 2.0), (self.tp("suscribete", 0.7, dur), "pop", 0.2)]


ESCENAS = {f"14_{i}": c for i, c in enumerate((M1, M2, M3, M4, M5, M6, M7, M8), 1)}
JSON, AUDIO = "historias/historia_14_mineros_chile.json", "audios/historia_14_voz.mp3"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--sin-audio", action="store_true")
    a = ap.parse_args()
    if a.preview:
        pro.preview(ESCENAS, JSON, AUDIO, "/tmp/claude-0/prev_14.png")
    else:
        pro.generar(Path(JSON), ESCENAS, ESTILO, AUDIO, a.sin_audio)
