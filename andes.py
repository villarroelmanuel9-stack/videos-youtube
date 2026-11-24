#!/usr/bin/env python3
"""Historia 15: La tragedia de los Andes — estilo nieve (notas de cuaderno, viento, tonos fríos)."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import pro
from pro import (BLANCO, Escena, H, W, chip, dibujar_avion, full, manuscrita, montanas, numero, papel_manuscrito,
                 particulas, tarjeta)
from alcatraz import sello
from caricatura import ease, pop
from cine import pegar_glow
from dinos import TINTA, Lienzo, _grad, capsula, catmull, elipse, oscuro, radius_ok, sombra_suave
from generar_short import render_emoji
from humanos import Humano

ESTILO = {"modo": "color", "color": (255, 112, 92)}
CORAL = (255, 112, 92)


def sobreviviente(i):
    ropas = [(150, 60, 50), (60, 90, 140), (90, 110, 80), (120, 100, 80), (70, 70, 90)]
    gorros = [(60, 90, 160), (180, 60, 60), (200, 160, 60), (60, 140, 120), (150, 150, 160)]
    return Humano(ropa=ropas[i % 5], pantalon=(50, 52, 62), bufanda=gorros[(i + 2) % 5], sombrero="gorro_lana",
                  color_sombrero=gorros[i % 5], barba=i % 2 == 0, pelo=(60, 42, 30))


GRUPO = [sobreviviente(i) for i in range(5)]
PARRADO, CANESSA = sobreviviente(1), sobreviviente(0)
ARRIERO = Humano(ropa=(150, 90, 60), sombrero="chupalla", bufanda=(170, 50, 50), barba=True, pelo=(40, 30, 26))


def fondo_cordillera(hora="dia"):
    def dib(L):
        if hora == "dia":
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (140, 180, 220)), (0.55, (220, 232, 242)), (1, (220, 232, 242))]))
            capas = [(180, 196, 214), (150, 168, 192), (120, 140, 168)]
        elif hora == "noche":
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (10, 14, 30)), (0.6, (40, 50, 80)), (1, (40, 50, 80))]))
            capas = [(50, 60, 86), (40, 48, 72), (30, 38, 60)]
            r = random.Random(4)
            for _ in range(150):
                L.circulo(r.randint(0, W), r.randint(0, 900), r.choice((1.5, 2, 3)), (230, 230, 255), borde=False)
        else:  # amanecer
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (80, 100, 160)), (0.45, (250, 190, 160)), (0.6, (255, 220, 190)),
                                                       (1, (255, 220, 190))]))
            capas = [(200, 176, 190), (170, 150, 170), (140, 126, 150)]
        montanas(L, 1000, [(150, 600, 420), (560, 700, 560), (950, 600, 380)], capas[0], borde=False)
        montanas(L, 1150, [(-50, 700, 420), (400, 800, 460), (900, 700, 400)], capas[1], borde=False)
        montanas(L, 1300, [(250, 900, 380), (850, 800, 330)], capas[2])
        nieve = (240, 244, 250) if hora != "noche" else (150, 160, 190)
        L.forma(catmull([(-50, 1350), (300, 1300), (700, 1360), (W + 50, 1320), (W + 50, H), (-50, H)], 3), nieve,
                borde=False, intensidad=0.04)
    return full(dib)


def fuselaje(sepultado=0.0, noche=False):
    L = Lienzo(900, 360, 450, 300)
    col = (225, 228, 232) if not noche else (130, 136, 150)
    L.forma([(-420, -30), (-330, -150), (300, -150), (330, -110), (300, -40), (340, 20), (290, 60), (-360, 60)],
            col, intensidad=0.08)
    L.linea([(-400, -40), (300, -40)], (200, 60, 50), 12)
    for i in range(9):
        L.circulo(-280 + i * 62, -96, 14, (60, 80, 110), ancho=3)
    if sepultado > 0:
        alto = 220 * sepultado
        L.forma(catmull([(-460, 60), (-460, 60 - alto), (-100, 40 - alto * 1.1), (380, 60 - alto * 0.9),
                         (420, 60)], 3), (244, 246, 252), borde=False, intensidad=0.05)
    return L.final()


def helicoptero(img, x, y, s, t):
    d = ImageDraw.Draw(img)
    d.ellipse((x - 90 * s, y - 50 * s, x + 90 * s, y + 50 * s), fill=(220, 120, 40), outline=TINTA, width=5)
    d.ellipse((x + 10 * s, y - 40 * s, x + 80 * s, y + 10 * s), fill=(150, 200, 230), outline=TINTA, width=4)
    d.line((x - 80 * s, y - 10 * s, x - 230 * s, y - 30 * s), fill=TINTA, width=int(16 * s))
    d.line((x - 80 * s, y - 10 * s, x - 230 * s, y - 30 * s), fill=(220, 120, 40), width=int(9 * s))
    a = math.sin(t * 40)
    d.line((x - 200 * s * a, y - 62 * s, x + 200 * s * a, y - 62 * s), fill=(40, 40, 44), width=int(8 * s))
    d.line((x, y - 50 * s, x, y - 62 * s), fill=TINTA, width=int(8 * s))
    d.line((x - 60 * s, y + 60 * s, x + 60 * s, y + 60 * s), fill=TINTA, width=int(6 * s))


# --------------------------------------------------------------------------- #
class A1(Escena):
    camara = (1.0, 1.12, 0.5, 0.55)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_cordillera()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        te = self.tp("estrello", 0.75, dur)
        if t < te:
            q = t / max(te, 0.1)
            dibujar_avion(img, "helice", -200 + 950 * q, 520 + 380 * q * q, 0.75, ang=-12 * q)
        else:
            f = min(1.0, (t - te) / 1.5)
            pegar_glow(img, 760, 1000, 200 + 400 * f, "#ffffff", 0.95 * (1 - f) + 0.05)
        particulas(img, t, "nieve", 60, viento=-180)
        return img

    def sacudida(self, t, dur):
        te = self.tp("estrello", 0.75, dur)
        return 1.5 * max(0.0, 1 - (t - te) / 1.0) if t > te else 0.0

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.2, "izq", 210, "13 de octubre", "1972", "nota", emoji="✈️")
        tarjeta(img, t, self.tp("rugby", 0.45, dur), "der", 420, "equipo de rugby", "Old Christians", "nota",
                emoji="🏉")

    def sonidos(self, dur):
        te = self.tp("estrello", 0.75, dur)
        return [(0, "motor", te), (0, "viento", dur), (te, "impacto" if False else "derrumbe", 2.5)]


class A2(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_cordillera()
        f = fuselaje()
        self.fondo.alpha_composite(f, (90, 1080))

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for i, (p, x) in enumerate(zip(GRUPO[:4], (170, 420, 680, 900))):
            p.dibujar(img, x, 1760 + (i % 2) * 50, 0.72, t, expr="miedo" if i % 2 else "cansado")
        particulas(img, t, "nieve", 90, viento=-260)
        return img

    def encima(self, img, t, dur):
        chip(img, t, self.tp("cuarenta", 0.1, dur), "45 a bordo", y=240, fondo=(40, 50, 70), tam=42)
        numero(img, t, self.tp("tres", 0.5, dur), "+3.000 m", "de altura", y=440, color=(255, 255, 255))
        tarjeta(img, t, self.tp("nieve", 0.85, dur), "der", 640, "temperatura", "bajo cero", "nota", emoji="🥶")

    def sonidos(self, dur):
        return [(0, "viento", dur)]


class A3(Escena):
    camara = (1.0, 1.15, 0.5, 0.62)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(26, 30, 42))
            for x in range(-40, W, 140):
                L.linea(catmull([(x, 0), (x + 60, 700), (x, 1400)], 5, cerrado=False), (44, 50, 66), 26)
            L.forma(catmull([(0, 1350), (W, 1330), (W, H), (0, H)], 3), (60, 64, 80), borde=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        pegar_glow(img, 540, 1240, 380, "#ffcf8a", 0.45)
        for i, (p, x) in enumerate(zip(GRUPO, (150, 330, 750, 930))):
            p.dibujar(img, x, 1720, 0.72, t, pose="sentado", expr="triste" if t > dur * 0.6 else "serio",
                      espejo=x > 540)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((450, 1180, 630, 1290), radius=14, fill=(60, 50, 44), outline=TINTA, width=5)
        d.ellipse((470, 1205, 540, 1270), fill=(120, 110, 100), outline=TINTA, width=3)
        d.line((600, 1180, 640, 1080), fill=(160, 160, 170), width=5)
        for k in range(3):
            r = 60 + ((t * 120 + k * 50) % 150)
            d.arc((540 - r, 1235 - r, 540 + r, 1235 + r), 220, 320, fill=(255, 230, 170, int(200 * (1 - r / 210))),
                  width=5)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.2, "izq", 210, "día", "11", "nota", emoji="📻")
        sello(img, t, self.tp("suspendido", 0.75, dur), "BÚSQUEDA SUSPENDIDA", W / 2, 640, ang=-8, color=(220, 60, 50),
              tam=66)

    def sonidos(self, dur):
        return [(0.3, "estatica", dur - 0.3), (self.tp("suspendido", 0.75, dur), "sello", 0.3)]


class A4(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = A3().fondo

    def mundo(self, t, dur):
        img = self.fondo.copy()
        pegar_glow(img, 540, 1300, 300 + 20 * math.sin(t * 4), "#ffcf8a", 0.4)
        d = ImageDraw.Draw(img)
        d.rectangle((528, 1290, 552, 1350), fill=(240, 236, 220), outline=TINTA, width=3)
        pegar_glow(img, 540, 1280 + 2 * math.sin(t * 9), 26, "#ffe39a", 1.0)
        for i, (p, x) in enumerate(zip(GRUPO, (170, 370, 710, 910))):
            p.dibujar(img, x, 1740, 0.72, t, pose="sentado", expr="triste", espejo=x > 540)
        oscuro_ = Image.new("RGBA", (W, H), (0, 0, 10, 70))
        img.alpha_composite(oscuro_)
        return img

    def encima(self, img, t, dur):
        chip(img, t, self.tp("decision", 0.35, dur), "LA DECISIÓN MÁS DIFÍCIL", y=520, fondo=(30, 34, 46), tam=48)

    def sonidos(self, dur):
        return [(0, "viento", dur), (0, "latido", dur)]


class A5(Escena):
    camara = (1.0, 1.04, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_cordillera("noche")

    def mundo(self, t, dur):
        img = self.fondo.copy()
        ta = self.tp("avalancha", 0.15, dur)
        q = ease((t - ta) / 1.6) if t > ta else 0.0
        img.alpha_composite(fuselaje(sepultado=round(q * 6) / 6, noche=True), (90, 1080))
        if 0 < q < 1:
            d = ImageDraw.Draw(img)
            fx = W + 200 - (W + 600) * q
            pts = [(W + 300, 300), (fx + 300, 600)] + [(fx + 80 * math.sin(i), 900 + i * 60) for i in range(12)] + \
                  [(W + 300, H)]
            d.polygon(pts, fill=(236, 240, 250))
            for i in range(30):
                pegar_glow(img, fx + random.Random(i).uniform(0, 400), 700 + i * 30, 70, "#ffffff", 0.6)
        particulas(img, t, "nieve", 120, viento=-500, vel=2)
        return img

    def sacudida(self, t, dur):
        ta = self.tp("avalancha", 0.15, dur)
        return 1.8 * max(0.0, 1 - (t - ta) / 2.0) if t > ta else 0.0

    def encima(self, img, t, dur):
        chip(img, t, self.tp("murieron", 0.75, dur), "ocho vidas más", y=520, fondo=(30, 34, 46), tam=48)

    def sonidos(self, dur):
        return [(self.tp("avalancha", 0.15, dur), "avalancha", 3.5)]


class A6(Escena):
    camara = (1.0, 1.08, 0.5, 0.58)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_cordillera()

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        avance = t / dur
        for k in range(int(avance * 26)):
            x = 60 + k * 30
            y = 1640 - k * 14 + (8 if k % 2 else -8)
            d.ellipse((x - 9, y - 5, x + 9, y + 5), fill=(190, 200, 220))
        x = 60 + avance * 26 * 30
        PARRADO.dibujar(img, x, 1640 - avance * 26 * 14, 0.6, t, pose="caminar", vel=0.7, expr="cansado")
        CANESSA.dibujar(img, x - 120, 1690 - avance * 26 * 14, 0.6, t + 0.4, pose="caminar", vel=0.7, expr="cansado")
        particulas(img, t, "nieve", 70, viento=-200)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("nando", 0.05, dur), "izq", 210, "perdió a su madre y hermana", "Nando Parrado",
                "nota", emoji="🧗")
        tarjeta(img, t, self.tp("canessa", 0.4, dur), "der", 420, "estudiante de medicina", "Roberto Canessa",
                "nota", emoji="🧗")
        numero(img, t, self.tp("diez", 0.75, dur), "10 DÍAS", "a pie", y=760, color=(255, 255, 255))
        chip(img, t, self.tp("escalada", 0.9, dur), "sin equipo de escalada", y=940, fondo=(160, 50, 40), tam=40)

    def sonidos(self, dur):
        return [(0, "viento", dur)]


class A7(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (120, 180, 230)), (0.6, (220, 236, 240)), (1, (220, 236, 240))]))
            montanas(L, 1000, [(200, 700, 500), (800, 700, 420)], (150, 160, 170))
            L.forma(catmull([(-50, 1000), (W + 50, 980), (W + 50, H), (-50, H)], 3), (110, 170, 90), borde=False)
            L.forma(catmull([(470, 1000), (600, 1000), (640, H), (420, H)], 3), (80, 150, 200), intensidad=0.05)
            r = random.Random(3)
            for _ in range(10):
                x = r.choice((r.randint(0, 380), r.randint(700, W)))
                y = r.randint(1050, 1200)
                L.forma(elipse(x, y - 60, 60, 80), (70, 130, 70), intensidad=0.1)
                L.linea([(x, y), (x, y + 40)], (100, 70, 40), 10)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        for i in range(10):
            y = 1050 + i * 90 + (t * 80) % 90
            d.line((500, y, 580, y + 10), fill=(180, 220, 245), width=5)
        PARRADO.dibujar(img, 180, 1760, 0.8, t, pose="saludar", expr="cansado")
        CANESSA.dibujar(img, 340, 1700, 0.7, t, expr="cansado")
        ARRIERO.dibujar(img, 860, 1720, 0.8, t, pose="saludar" if t < self.tp("lanzo", 0.4, dur) else "quieto",
                        expr="sorpresa")
        tl = self.tp("lanzo", 0.4, dur)
        if tl < t < tl + 1.2:
            q = (t - tl) / 1.2
            x = 820 - 560 * q
            y = 1150 - 400 * math.sin(math.pi * q)
            d.ellipse((x - 22, y - 18, x + 22, y + 18), fill=(130, 126, 120), outline=TINTA, width=4)
            d.rectangle((x - 14, y - 30, x + 14, y - 12), fill=(250, 246, 230), outline=TINTA, width=2)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("arriero", 0.15, dur), "der", 210, "al otro lado del río", "un arriero chileno",
                "nota", emoji="🤠", dur=self.tp("escribio", 0.6, dur) - self.tp("arriero", 0.15, dur) - 0.3)
        papel_manuscrito(img, t, self.tp("escribio", 0.6, dur), ["Vengo de un avión", "que cayó en las",
                                                                 "montañas…"], 540, 640, 640, 290, vel=24, tam=58,
                         color=(40, 50, 110))

    def sonidos(self, dur):
        return [(0, "rio", dur)]


class A8(Escena):
    camara = (1.0, 1.1, 0.5, 0.55)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_cordillera("amanecer")
        self.fondo.alpha_composite(fuselaje(sepultado=0.3), (90, 1080))

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for k in range(2):
            x = -200 + t * 170 + k * 260
            helicoptero(img, min(x, 380 + k * 360), 520 + k * 120 + 10 * math.sin(t * 2 + k), 1.0, t)
        for i, (p, x) in enumerate(zip(GRUPO[:4], (170, 420, 680, 900))):
            p.dibujar(img, x, 1760 + (i % 2) * 50, 0.7, t + i, pose="celebrar" if i % 2 else "saludar", expr="feliz")
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("setenta", 0.1, dur), "izq", 210, "en la montaña", "72 días", "nota", emoji="🏔️")
        numero(img, t, self.tp("dieciseis", 0.6, dur), "16", "sobrevivientes", y=900, color=(255, 255, 255), tam=220)

    def sonidos(self, dur):
        return [(0, "helicoptero", dur)]


class A9(Escena):  # final: página de diario con casillas para marcar y lápiz que escribe "suscríbete"
    camara = (1.0, 1.03, 0.5, 0.5)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(250, 250, 244))
            for y in range(160, H, 64):
                L.linea([(0, y), (W, y)], (180, 205, 235), 3)
            L.linea([(110, 0), (110, H)], (235, 120, 120), 4)
            L.linea(catmull([(160, 960), (330, 640), (430, 760), (600, 500), (720, 640), (900, 440), (990, 580)], 5,
                            cerrado=False), (120, 130, 150), 6)
            for i in range(14):
                x = 200 + i * 55
                y = 910 - i * 22 + (10 if i % 2 else -10)
                L.circulo(x, y, 6, (90, 90, 110), borde=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        return self.fondo.copy()

    def encima(self, img, t, dur):
        d = ImageDraw.Draw(img)
        tq = self.tp("habrias", 0.02, dur)
        if t > tq:
            n = int((t - tq) * 22)
            txt = "¿Habrías tenido la fuerza para cruzar?"
            vis = txt[:n]
            lineas = ["¿Habrías tenido la fuerza", "para cruzar?"]
            y = 230
            for ln in lineas:
                d.text((150, y), vis[:len(ln)], font=manuscrita(66), fill=(40, 50, 110))
                vis = vis[len(ln):].lstrip()
                y += 90
        tc = self.tp("dejamelo", 0.35, dur)
        for k, (txt, col) in enumerate((("Sí, cruzo", (40, 150, 80)), ("No podría", (200, 60, 50)))):
            if t > tc + k * 0.2:
                p = pop((t - tc - k * 0.2) / 0.3)
                y = 1060 + k * 120
                d.rectangle((160, y - 36 * p, 160 + 72 * p, y + 36 * p), outline=(40, 50, 110), width=6)
                d.text((270, y), txt, font=manuscrita(int(64 * p) + 1), fill=(40, 50, 110), anchor="lm")
        if t > tc + 0.6:
            q = pop((t - tc - 0.6) / 0.3)
            d.text((640, 1120), "← comenta", font=manuscrita(int(58 * q) + 1), fill=(200, 60, 50), anchor="lm")
        ts = self.tp("suscribete", 0.7, dur)
        if t > ts:
            n = int((t - ts) * 14)
            palabra = "suscríbete"[:n]
            d.text((540, 1560), palabra, font=manuscrita(96), fill=(200, 60, 50), anchor="mm")
            if n >= 10:
                q = min(1.0, (t - ts - 0.8) / 0.4)
                d.line((300, 1630, 300 + 480 * q, 1625), fill=(200, 60, 50), width=8)
            px = 540 - 230 + min(n, 10) * 46
            d.polygon([(px, 1600), (px + 30, 1520), (px + 50, 1530), (px + 20, 1610)], fill=(240, 190, 60),
                      outline=TINTA)

    def sonidos(self, dur):
        return [(self.tp("habrias", 0.02, dur), "raspado", 1.6), (self.tp("suscribete", 0.7, dur), "raspado", 1.0)]


ESCENAS = {f"15_{i}": c for i, c in enumerate((A1, A2, A3, A4, A5, A6, A7, A8, A9), 1)}
JSON, AUDIO = "historias/historia_15_andes.json", "audios/historia_15_voz.mp3"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--sin-audio", action="store_true")
    a = ap.parse_args()
    if a.preview:
        pro.preview(ESCENAS, JSON, AUDIO, "/tmp/claude-0/prev_15.png")
    else:
        pro.generar(Path(JSON), ESCENAS, ESTILO, AUDIO, a.sin_audio, pad_hz=(55, 65.4, 82.4))
