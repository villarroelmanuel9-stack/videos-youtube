#!/usr/bin/env python3
"""Historia 16: Juliane Koepcke — estilo selva (libreta de campo, lluvia, recuerdo en sepia, mapa final)."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import pro
from pro import (BLANCO, Escena, H, W, chip, dibujar_avion, full, manuscrita, numero, particulas, relampago,
                 tarjeta)
from alcatraz import maquina
from caricatura import ease, pop
from cine import pegar_glow
from dinos import TINTA, Lienzo, _grad, capsula, catmull, elipse, oscuro, claro, radius_ok, sombra_suave
from generar_short import render_emoji
from humanos import Humano

ESTILO = {"modo": "color", "color": (170, 235, 80)}
VERDE = (60, 130, 70)

JULIANE = Humano(ropa=(232, 226, 206), vestido=True, peinado="largo", pelo=(176, 126, 72), descalzo_der=True)
MADRE = Humano(ropa=(110, 80, 140), vestido=True, peinado="corto", pelo=(150, 110, 70))
PADRE = Humano(ropa=(160, 140, 96), pantalon=(110, 96, 70), barba=True, sombrero="fedora",
               color_sombrero=(180, 160, 110), pelo=(110, 80, 50))
MADEREROS = [Humano(ropa=c, sombrero="chupalla", color_sombrero=(210, 186, 130), pelo=(30, 26, 24),
                    piel=(200, 150, 110)) for c in ((180, 60, 50), (60, 100, 150), (200, 160, 60))]
JULIANE_HOY = Humano(ropa=(100, 120, 80), pantalon=(80, 90, 70), peinado="corto", pelo=(210, 190, 160))


def hoja(L, x, y, largo, ang, col):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(x, y)]
    for k in range(1, 7):
        u = k / 6
        ancho = math.sin(math.pi * u) * largo * 0.22
        px, py = x + c * largo * u, y + s * largo * u
        pts.append((px - s * ancho, py + c * ancho))
    pts += [(x + c * largo, y + s * largo)]
    for k in range(5, 0, -1):
        u = k / 6
        ancho = math.sin(math.pi * u) * largo * 0.22
        px, py = x + c * largo * u, y + s * largo * u
        pts.append((px + s * ancho, py - c * ancho))
    L.forma(pts, col, intensidad=0.1, ancho=4)
    L.linea([(x, y), (x + c * largo * 0.95, y + s * largo * 0.95)], oscuro(col, 0.7), 4)


def fondo_selva(oscura=False, rio=False, semilla=1):
    def dib(L):
        top = (40, 70, 60) if oscura else (150, 200, 170)
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, top), (1, oscuro(top, 0.6))]))
        r = random.Random(semilla)
        for capa, col in enumerate(((50, 100, 70), (40, 86, 56), (30, 70, 46))):
            if oscura:
                col = oscuro(col, 0.6)
            for _ in range(12):
                x, y = r.randint(-100, W + 100), r.randint(150 + capa * 260, 700 + capa * 300)
                L.forma(elipse(x, y, r.randint(140, 240), r.randint(100, 170)), col, intensidad=0.07, ancho=4)
            for _ in range(3):
                x = r.randint(0, W)
                L.forma([(x - 22, 1500), (x - 14, 200 + capa * 200), (x + 14, 200 + capa * 200), (x + 22, 1500)],
                        oscuro((90, 64, 44), 0.8 if not oscura else 0.5), suave=False, intensidad=0.08)
        suelo = (70, 90, 50) if not oscura else (40, 54, 34)
        L.forma(catmull([(-50, 1450), (W + 50, 1420), (W + 50, H), (-50, H)], 3), suelo, borde=False)
        if rio:
            L.forma(catmull([(-50, 1500), (W + 50, 1460), (W + 50, 1800), (-50, 1840)], 3), (70, 120, 110),
                    intensidad=0.05)
        for x0, lado in ((-20, 1), (W + 20, -1)):
            for k in range(4):
                ang = (-0.9 - k * 0.25) if lado > 0 else (math.pi + 0.9 + k * 0.25)
                hoja(L, x0, H - 120 - k * 90, 420 - k * 40, ang, (40, 110, 60) if not oscura else (26, 70, 40))
    return full(dib)


def fila_asientos(rot_deg=0.0, con_juliane=True, s=1.0):
    L = Lienzo(700, 560, 350, 520)
    for i in range(3):
        x = -230 + i * 230
        L.forma([(x - 95, -420), (x + 95, -420), (x + 100, -120), (x - 100, -120)], (60, 90, 150), intensidad=0.1)
        L.forma([(x - 70, -410), (x + 70, -410), (x + 70, -350), (x - 70, -350)], (236, 236, 230), suave=False,
                ancho=3)
        L.forma([(x - 110, -150), (x + 110, -150), (x + 110, -80), (x - 110, -80)], (50, 76, 130), suave=False)
    for x in (-320, 320):
        L.forma(capsula((x, -100), (x, -10), 20, 20), (150, 150, 156))
    img = L.final()
    if con_juliane:
        j = JULIANE.sprite.get(0.0, 0.42, 0, False, ("sentado", "miedo"))
        img.alpha_composite(j, (350 - 126, 520 - 400))
        d = ImageDraw.Draw(img)
        d.line((240, 300, 460, 300), fill=(120, 120, 126), width=10)
    if s != 1:
        img = img.resize((int(img.width * s), int(img.height * s)), Image.BICUBIC)
    if rot_deg:
        img = img.rotate(rot_deg, expand=True, resample=Image.BICUBIC)
    return img


def sepia(img):
    a = np.asarray(img.convert("RGB"), np.float32)
    g = a @ np.array([0.299, 0.587, 0.114], np.float32)
    out = np.stack([g * 1.07 + 20, g * 0.9 + 10, g * 0.7], -1).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out).convert("RGBA")


# --------------------------------------------------------------------------- #
class J1(Escena):
    camara = (1.0, 1.0, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.cielo = _grad(W, H, [(0, (110, 150, 200)), (1, (200, 220, 230))])
        L = Lienzo(W, 900, 0, 0)
        for i in range(16):
            x = i * 75 - 30
            L.forma(elipse(x, 160 + (i % 3) * 40, 120, 110), (40, 110, 60) if i % 2 else (50, 126, 70),
                    intensidad=0.1)
        L.forma([(0, 220), (W, 220), (W, 900), (0, 900)], (30, 90, 50), suave=False, borde=False)
        self.copas = L.final()

    def mundo(self, t, dur):
        img = self.cielo.copy()
        for i in range(6):
            y = (i * 380 - t * 900) % (H + 600) - 300
            pegar_glow(img, (i * 270) % W, y, 260, "#ffffff", 0.8)
        ts = self.tp("sobrevivio", 0.8, dur)
        q = min(1.0, t / max(ts, 0.1))
        fa = fila_asientos(rot_deg=25 * math.sin(t * 3.5), s=0.85)
        img.alpha_composite(fa, (int(540 - fa.width / 2), int(380 + 120 * math.sin(t * 2) - fa.height / 2)))
        img.alpha_composite(self.copas, (0, int(H + 50 - 900 * ease(q))))
        particulas(img, t, "lluvia", 40, viento=-200, vel=1.6, alfa=150)
        return img

    def sacudida(self, t, dur):
        return 0.6

    def encima(self, img, t, dur):
        ts = self.tp("sobrevivio", 0.8, dur)
        alt = int(3000 * (1 - min(1.0, t / max(ts, 0.1))))
        tarjeta(img, t, 0.05, "der", 200, "altura", f"{alt:,} m".replace(",", "."), "diario", emoji="📉")
        chip(img, t, ts, "¡SOBREVIVIÓ!", y=780, fondo=(60, 130, 70), tam=64)

    def sonidos(self, dur):
        return [(0, "viento", dur), (self.tp("sobrevivio", 0.8, dur), "golpe", 0.4)]


class J2(Escena):
    camara = (1.0, 1.1, 0.5, 0.6)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(214, 224, 230))
            L.forma(catmull([(0, 0), (W, 0), (W, 360), (W * 0.5, 420), (0, 360)], 4), (196, 208, 216), borde=False)
            L.forma(catmull([(330, 520), (750, 520), (750, 1000), (330, 1000)], 3), (90, 110, 130), intensidad=0.04)
            L.forma(catmull([(360, 550), (720, 550), (720, 970), (360, 970)], 3), (120, 170, 210), borde=False)
            for i in range(10):
                L.forma(elipse(370 + i * 38, 880 + (i % 3) * 20, 60, 50), (50, 120, 70), borde=False,
                        sombra=False, brillo=False)
            L.forma([(0, 1450), (W, 1450), (W, H), (0, H)], (80, 96, 120), suave=False, borde=False)
        self.fondo = full(dib)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        for x, p, e in ((330, MADRE, "feliz"), (720, JULIANE, "feliz")):
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((x - 130, 1120, x + 130, 1560), radius=40, fill=(60, 90, 150), outline=TINTA, width=6)
            p.dibujar(img, x - 40, 1700, 0.85, t, pose="sentado", expr=e, sombra=False)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.15, "izq", 200, "nochebuena 1971", "Lima → Pucallpa", "diario", emoji="🎄")
        chip(img, t, self.tp("diecisiete", 0.25, dur), "JULIANE · 17 AÑOS", y=430, fondo=VERDE, tam=46, x=760)
        chip(img, t, self.tp("madre", 0.7, dur), "con su madre", y=1060, fondo=(110, 80, 140), tam=38, x=330)

    def sonidos(self, dur):
        return [(0, "motor", dur)]


class J3(Escena):
    camara = (1.0, 1.06, 0.5, 0.5)

    def __init__(self):
        super().__init__()
        self.cielo = _grad(W, H, [(0, (14, 18, 30)), (1, (44, 54, 70))])

    def mundo(self, t, dur):
        img = self.cielo.copy()
        for i in range(8):
            x = (i * 300 - t * 70) % (W + 600) - 300
            pegar_glow(img, x, 300 + (i % 3) * 280, 330, "#2e3346", 0.85)
        tr, tp_ = self.tp("rayo", 0.35, dur), self.tp("partio", 0.75, dur)
        partido = ease((t - tp_) / 1.0) if t > tp_ else 0.0
        dibujar_avion(img, "electra", 540, 860 + 15 * math.sin(t * 2) + partido * 150, 1.05,
                      partido=round(partido * 8) / 8, ang=-10 * partido)
        if tr < t < tr + 0.5:
            d = ImageDraw.Draw(img)
            pts = [(700, 0), (640, 200), (700, 320), (600, 520), (660, 640), (560, 820)]
            d.line(pts, fill=(255, 255, 230), width=14)
            d.line(pts, fill=(170, 200, 255), width=6)
        relampago(img, t, tr, 0.4)
        if t > tp_:
            for i in range(10):
                f = ((t - tp_) * 1.5 + i / 10) % 1
                pegar_glow(img, 560 + 100 * math.cos(i) * f, 860 + 200 * f, 16, "#ffb050", 1 - f)
        particulas(img, t, "lluvia", 110, viento=-400, alfa=200)
        return img

    def sacudida(self, t, dur):
        tr = self.tp("rayo", 0.35, dur)
        return 1.6 if t > tr else 0.2

    def encima(self, img, t, dur):
        chip(img, t, 0.15, "UNA TORMENTA", y=260, fondo=(30, 36, 50), tam=46)

    def sonidos(self, dur):
        tr = self.tp("rayo", 0.35, dur)
        return [(0, "motor", dur), (0, "lluvia", dur), (tr, "trueno", 2.5), (self.tp("partio", 0.75, dur), "derrumbe", 2.0)]


class J4(Escena):
    camara = (1.0, 1.12, 0.5, 0.62)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_selva(semilla=2)
        fa = fila_asientos(rot_deg=-12, con_juliane=False, s=0.9)
        self.fondo.alpha_composite(fa, (480, 1150))

    def mundo(self, t, dur):
        img = self.fondo.copy()
        JULIANE.dibujar(img, 330, 1740, 1.0, t, pose="sentado", expr="cansado" if t < dur * 0.3 else "triste")
        particulas(img, t, "lluvia", 50, viento=-60, alfa=140)
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, 0.15, "izq", 200, "al día siguiente", "Sola en la selva", "diario", emoji="🌿")
        d = ImageDraw.Draw(img)
        for pal, defecto, txt, (x, y), (ax, ay) in (("clavicula", 0.45, "clavícula rota", (760, 760), (400, 1180)),
                                                    ("herida", 0.65, "herida en el brazo", (760, 880), (450, 1320))):
            ti = self.tp(pal, defecto, dur)
            if t > ti:
                d.line((x - 200, y, ax, ay), fill=(255, 255, 255), width=5)
                d.ellipse((ax - 10, ay - 10, ax + 10, ay + 10), fill=(220, 50, 50), outline=BLANCO, width=3)
                chip(img, t, ti, txt, y=y, fondo=(150, 40, 40), tam=38, x=x)
        ts = self.tp("sandalia", 0.85, dur)
        if t > ts:
            chip(img, t, ts, "y una sola sandalia", y=1000, fondo=VERDE, tam=40, x=760)
            em = render_emoji("🩴")
            if em is not None:
                p = pop((t - ts) / 0.3)
                em = em.resize((max(1, int(140 * p)), max(1, int(140 * p * em.height / em.width))))
                img.alpha_composite(em, (int(860 - em.width / 2), int(1110 - em.height / 2)))

    def sonidos(self, dur):
        return [(0, "lluvia", dur), (0, "insectos", dur)]


class J5(Escena):  # recuerdo en sepia
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        base = fondo_selva(rio=True, semilla=3)
        d = ImageDraw.Draw(base)
        d.rectangle((520, 980, 920, 1280), fill=(240, 230, 200), outline=TINTA, width=6)
        d.line([(560, 1020), (640, 1100), (620, 1160), (720, 1200), (800, 1240), (880, 1260)], fill=(60, 120, 200),
               width=10)
        d.line((720, 1280, 720, 1500), fill=(110, 76, 46), width=14)
        self.fondo = base

    def mundo(self, t, dur):
        img = self.fondo.copy()
        PADRE.dibujar(img, 960, 1760, 0.95, t, pose="saludar", expr="feliz")
        JULIANE.dibujar(img, 280, 1760, 0.8, t, expr="normal")
        return sepia(img)

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("biologos", 0.15, dur), "izq", 200, "sus padres", "eran biólogos", "diario",
                emoji="🔬")
        ts = self.tp("sigue", 0.55, dur)
        if t > ts:
            p = pop((t - ts) / 0.35)
            d = ImageDraw.Draw(img)
            d.text((W / 2, 640), "«Sigue el agua»", font=manuscrita(max(8, int(110 * p))), fill=(255, 250, 235),
                   anchor="mm", stroke_width=8, stroke_fill=(60, 40, 20))
        chip(img, t, self.tp("rios", 0.85, dur), "los ríos llevan a las personas", y=790, fondo=(90, 66, 40), tam=40)

    def sonidos(self, dur):
        return [(0, "rio", dur)]


class J6(Escena):
    camara = (1.0, 1.08, 0.5, 0.62)

    def __init__(self):
        super().__init__()
        self.fondo = fondo_selva(rio=True, semilla=4)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        x = 200 + t * 45
        JULIANE.dibujar(img, x, 1720, 0.9, t, pose="caminar", vel=0.6, expr="cansado", sombra=False)
        d = ImageDraw.Draw(img)
        agua = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        da = ImageDraw.Draw(agua)
        da.polygon([(0, 1590), (W, 1560)] + [(W, H), (0, H)], fill=(70, 120, 110, 200))
        for i in range(12):
            yy = 1600 + i * 26
            xx = (i * 120 + t * 60) % W
            da.line((xx, yy, xx + 90, yy), fill=(170, 210, 200, 200), width=4)
        img.alpha_composite(agua)
        tc = self.tp("cocodrilos", 0.55, dur)
        if t > tc:
            for k, cx in enumerate((760, 930)):
                cy = 1640 + 6 * math.sin(t * 2 + k)
                d.ellipse((cx - 60, cy - 16, cx + 60, cy + 16), fill=(70, 90, 50), outline=TINTA, width=4)
                for ex in (-30, -6):
                    d.ellipse((cx + ex - 10, cy - 30, cx + ex + 10, cy - 10), fill=(220, 220, 120), outline=TINTA,
                              width=3)
                    d.ellipse((cx + ex - 3, cy - 24, cx + ex + 3, cy - 16), fill=TINTA)
        for i in range(14):
            bx = 300 + 400 * math.sin(t * 2 + i * 1.7)
            by = 1100 + 200 * math.sin(t * 2.6 + i)
            d.ellipse((bx - 4, by - 4, bx + 4, by + 4), fill=(20, 20, 20))
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("insectos", 0.4, dur), "izq", 200, "peligros", "insectos y cocodrilos", "diario",
                emoji="🐊")
        numero(img, t, self.tp("once", 0.85, dur), "11 DÍAS", "caminando", y=560, color=(170, 235, 80))

    def sonidos(self, dur):
        return [(0, "rio", dur), (0, "insectos", dur)]


class J7(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        base = fondo_selva(rio=True, semilla=5)
        L = Lienzo(W, H, 0, 0)
        L.forma([(560, 1460), (580, 1160), (980, 1160), (1000, 1460)], (150, 110, 70), suave=False, intensidad=0.06)
        L.forma([(520, 1180), (780, 960), (1040, 1180)], (190, 160, 90), suave=False, intensidad=0.1)
        for x in range(560, 1000, 40):
            L.linea([(x, 1160), (x + 8, 1460)], (120, 84, 50), 4)
        L.forma([(700, 1300), (800, 1300), (800, 1460), (700, 1460)], (70, 50, 34), suave=False)
        L.forma([(80, 1560), (420, 1560), (380, 1620), (120, 1620)], (140, 96, 56), suave=False, intensidad=0.1)
        base.alpha_composite(L.final())
        self.fondo = base

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        tg = self.tp("gasolina", 0.3, dur)
        if t > tg:
            p = pop((t - tg) / 0.3)
            d.rounded_rectangle((900 - 60 * p, 1500 - 80 * p, 900 + 60 * p, 1500 + 80 * p), radius=10,
                                fill=(210, 40, 40), outline=TINTA, width=5)
        tm = self.tp("madereros", 0.8, dur)
        JULIANE.dibujar(img, 450, 1740, 0.85, t, pose="sentado" if t < tm else "quieto",
                        expr="cansado" if t < tm else "sorpresa")
        if t > tm:
            for k, m in enumerate(MADEREROS):
                m.dibujar(img, 1180 - (t - tm) * 220 + k * 140, 1760 + (k % 2) * 30, 0.8, t + k, pose="caminar",
                          vel=1.0, espejo=True, expr="sorpresa")
        return img

    def encima(self, img, t, dur):
        tarjeta(img, t, self.tp("cabana", 0.1, dur), "izq", 200, "día 10", "una cabaña", "diario", emoji="🛖")
        chip(img, t, self.tp("limpiar", 0.45, dur), "limpió su herida con gasolina", y=470, fondo=(150, 40, 40),
             tam=40, dur=self.tp("madereros", 0.8, dur) - self.tp("limpiar", 0.45, dur))
        tarjeta(img, t, self.tp("madereros", 0.8, dur), "der", 420, "la encontraron", "unos madereros", "diario",
                emoji="🪓")

    def sonidos(self, dur):
        return [(0, "rio", dur), (self.tp("madereros", 0.8, dur), "pop", 0.2)]


class J8(Escena):
    camara = (1.0, 1.08, 0.5, 0.6)

    def __init__(self):
        super().__init__()
        self.oscura = fondo_selva(oscura=True, semilla=6)
        base = fondo_selva(semilla=7)
        L = Lienzo(W, H, 0, 0)
        L.forma([(560, 1250), (1000, 1250), (1000, 1000), (560, 1000)], (150, 110, 70), suave=False)
        L.forma([(520, 1010), (780, 840), (1040, 1010)], (110, 80, 50), suave=False)
        for x in (600, 960):
            L.forma([(x - 10, 1250), (x + 10, 1250), (x + 10, 1460), (x - 10, 1460)], (100, 70, 44), suave=False)
        base.alpha_composite(L.final())
        self.hoy = base

    def corte(self, dur):
        return self.tp("hoy", 0.6, dur) - 0.1

    def cortes(self, dur):
        return [self.corte(dur)]

    def mundo(self, t, dur):
        if t < self.corte(dur):
            img = self.oscura.copy()
            pegar_glow(img, 540, 1200, 300, "#ffe6a0", 0.3)
            return img
        img = self.hoy.copy()
        JULIANE_HOY.dibujar(img, 320, 1760, 0.95, t, pose="sostener", expr="feliz")
        return img

    def encima(self, img, t, dur):
        c = self.corte(dur)
        if t < c:
            chip(img, t, 0.1, "su madre no sobrevivió", y=420, fondo=(30, 40, 34), tam=44)
            numero(img, t, self.tp("noventa", 0.3, dur), "1 de 92", "la única sobreviviente", y=760,
                   color=(255, 255, 255))
        else:
            tarjeta(img, t, c + 0.15, "izq", 200, "hoy", "bióloga", "diario", emoji="🦋")
            chip(img, t, self.tp("protege", 0.85, dur), "protege esa misma selva", y=520, fondo=VERDE, tam=44)

    def sonidos(self, dur):
        return [(self.corte(dur), "insectos", dur - self.corte(dur))]


class J9(Escena):  # final: mapa con la ruta + brote que crece con "SUSCRÍBETE"
    camara = (1.0, 1.03, 0.5, 0.5)

    def __init__(self):
        super().__init__()

        def dib(L):
            L.d.rectangle((0, 0, W * 2, H * 2), fill=(70, 110, 70))
            L.forma([(70, 300), (1010, 280), (1030, 1240), (60, 1260)], (236, 222, 180), intensidad=0.04)
            r = random.Random(3)
            for _ in range(70):
                x, y = r.randint(110, 980), r.randint(340, 1200)
                L.forma(elipse(x, y, 26, 20), (150, 190, 120), sombra=False, brillo=False, ancho=2)
            L.linea(catmull([(160, 420), (300, 560), (260, 700), (420, 820), (560, 900), (700, 1000), (900, 1150)], 6,
                            cerrado=False), (60, 120, 200), 22)
        self.fondo = full(dib)
        self.ruta = catmull([(240, 520), (300, 600), (270, 700), (420, 810), (560, 890), (700, 990), (860, 1120)], 8,
                            cerrado=False)

    def mundo(self, t, dur):
        img = self.fondo.copy()
        d = ImageDraw.Draw(img)
        d.line((210, 490, 270, 550), fill=(200, 30, 40), width=12)
        d.line((270, 490, 210, 550), fill=(200, 30, 40), width=12)
        n = int(len(self.ruta) * min(1.0, t / max(dur * 0.6, 0.1)))
        for i in range(0, n, 2):
            x, y = self.ruta[i]
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(200, 30, 40))
        if n >= len(self.ruta) - 1:
            d.polygon([(840, 1150), (880, 1100), (920, 1150)], fill=(150, 100, 60), outline=TINTA)
            d.rectangle((850, 1150, 910, 1190), fill=(180, 130, 80), outline=TINTA, width=3)
        return img

    def encima(self, img, t, dur):
        d = ImageDraw.Draw(img)
        p = pop(t / 0.4)
        d.text((W / 2, 200), "¿HABRÍAS SOBREVIVIDO?", font=pro.fuente(max(8, int(66 * p))), fill=BLANCO,
               anchor="mm", stroke_width=8, stroke_fill=(20, 40, 20))
        chip(img, t, self.tp("dejamelo", 0.3, dur), "comenta 👇".replace(" 👇", "") + "  SÍ  o  NO", y=1180 + 0,
             fondo=(40, 90, 50), tam=40)
        ts = self.tp("suscribete", 0.7, dur)
        if t > ts:
            q = ease((t - ts) / 0.8)
            tallo = 1660 - 140 * q
            d.line((W / 2, 1660, W / 2, tallo), fill=(60, 140, 60), width=12)
            if q > 0.6:
                p2 = pop((t - ts - 0.5) / 0.35)
                caja = (W / 2 - 280 * p2, tallo - 120 * p2, W / 2 + 280 * p2, tallo)
                sombra_suave(img, caja, radio=60, alfa=110)
                d.rounded_rectangle(caja, radius=radius_ok(60 * p2), fill=(110, 190, 80), outline=TINTA, width=5)
                d.text((W / 2, tallo - 60 * p2), "SUSCRÍBETE", font=pro.fuente(max(8, int(58 * p2))), fill=BLANCO,
                       anchor="mm", stroke_width=4, stroke_fill=(30, 70, 30))

    def sonidos(self, dur):
        return [(0, "insectos", dur), (self.tp("suscribete", 0.7, dur), "pop", 0.2)]


ESCENAS = {f"16_{i}": c for i, c in enumerate((J1, J2, J3, J4, J5, J6, J7, J8, J9), 1)}
JSON, AUDIO = "historias/historia_16_juliane_koepcke.json", "audios/historia_16_voz.mp3"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--sin-audio", action="store_true")
    a = ap.parse_args()
    if a.preview:
        pro.preview(ESCENAS, JSON, AUDIO, "/tmp/claude-0/prev_16.png")
    else:
        pro.generar(Path(JSON), ESCENAS, ESTILO, AUDIO, a.sin_audio, pad_hz=(52, 78, 104))
