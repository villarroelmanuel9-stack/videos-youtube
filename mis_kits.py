"""
Detalles REALES de cada misterio (vehículo, época, lugar, hora, personas, objetos) y los escenarios extra
que los usan: desierto, fondo marino, playa, tren, casa, palacio, personas de época y objetos históricos
(la señal Wow!, el manuscrito Voynich, el disco de Festo, el diamante Hope, etc.).
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import mis_reales as R
from alcatraz import maquina, niebla, olas
from cine import pegar_glow
from dinos import TINTA, _grad, catmull, claro, elipse, oscuro, sombra_suave
from humanos import Humano
from pro import H, W, manuscrita, particulas
from realista import LienzoReal

PALETAS = {
    "noche": [(0, (8, 12, 28)), (0.6, (28, 38, 66)), (1, (28, 38, 66))],
    "tormenta": [(0, (16, 18, 26)), (0.6, (50, 56, 68)), (1, (50, 56, 68))],
    "niebla": [(0, (104, 112, 122)), (0.6, (168, 172, 176)), (1, (168, 172, 176))],
    "atardecer": [(0, (46, 36, 74)), (0.5, (196, 104, 86)), (0.62, (236, 166, 108)), (1, (236, 166, 108))],
    "frio": [(0, (60, 80, 120)), (0.55, (176, 170, 184)), (1, (176, 170, 184))],
    "dia": [(0, (52, 112, 186)), (0.55, (150, 196, 230)), (1, (196, 222, 236))],
}
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def full(dib):
    L = LienzoReal(W, H, 0, 0)
    dib(L)
    return L.final()


def cielo(L, hora):
    L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS.get(hora, PALETAS["noche"])))
    if hora in ("noche", "tormenta"):
        rr = random.Random(5)
        for _ in range(140):
            L.circulo(rr.randint(0, W), rr.randint(0, 1150), rr.choice((1.5, 2, 2.5)), (230, 230, 255), borde=False)


def nubes(img, t, hora, y=650, n=6, semilla=1):
    col = {"dia": "#ffffff", "atardecer": "#f0a890", "niebla": "#d8dce0", "frio": "#e0e4ec"}.get(hora, "#3a4054")
    r = random.Random(semilla)
    for i in range(n):
        x = (r.uniform(0, W + 600) - t * r.uniform(15, 40)) % (W + 600) - 300
        yy = y + r.uniform(-250, 250)
        for k in range(4):
            pegar_glow(img, x + k * 90, yy + (k % 2) * 30, r.uniform(110, 170), col, 0.45)


# --------------------------------------------------------------------------- #
# PERSONAS DE ÉPOCA
# --------------------------------------------------------------------------- #
PERSONAS = {
    "traje": dict(ropa=(58, 60, 68), pantalon=(48, 50, 58), corbata=(120, 30, 30), sombrero="fedora", pelo=(50, 40, 30)),
    "traje_claro": dict(ropa=(150, 140, 118), pantalon=(120, 112, 96), corbata=(70, 40, 30), sombrero="fedora"),
    "abrigo": dict(ropa=(46, 44, 50), pantalon=(40, 40, 46), bufanda=(130, 30, 30), sombrero="fedora"),
    "anciano": dict(ropa=(82, 72, 60), pantalon=(62, 56, 48), barba=True, pelo=(232, 232, 226), sombrero="fedora",
                    color_sombrero=(200, 190, 168)),
    "mujer1920": dict(ropa=(110, 80, 96), vestido=True, peinado="corto", pelo=(150, 104, 60)),
    "mujer1910": dict(ropa=(40, 42, 64), vestido=True, peinado="largo", pelo=(60, 40, 30), sombrero="fedora",
                      color_sombrero=(30, 30, 40)),
    "mujer_abrigo": dict(ropa=(70, 60, 54), vestido=True, peinado="largo", pelo=(40, 30, 24), bufanda=(150, 140, 120)),
    "parka_roja": dict(ropa=(196, 36, 36), pantalon=(60, 60, 72), peinado="largo", pelo=(150, 100, 50)),
    "explorador": dict(ropa=(172, 152, 112), pantalon=(132, 118, 88), sombrero="chupalla",
                       color_sombrero=(150, 130, 90), barba=True, pelo=(120, 100, 80)),
    "camisa_blanca": dict(ropa=(236, 236, 230), pantalon=(90, 90, 96), pelo=(210, 210, 210)),
    "escalador": dict(ropa=(112, 92, 70), pantalon=(80, 70, 60), sombrero="gorro_lana", bufanda=(160, 40, 40)),
    "joven": dict(ropa=(92, 72, 60), pantalon=(60, 56, 50), pelo=(170, 120, 60)),
    "joven_lentes": dict(ropa=(204, 194, 164), pantalon=(80, 80, 70), lentes=True, pelo=(60, 44, 30)),
    "nino_verde": dict(ropa=(120, 96, 60), pantalon=(90, 70, 40), piel=(128, 176, 112), pelo=(70, 56, 34)),
    "esquiador": dict(ropa=(60, 72, 112), pantalon=(50, 50, 60), sombrero="gorro_lana", color_sombrero=(170, 50, 50)),
}
_humanos = {}


def figura(img, clave, x, y, s, t, pose="caminar", espejo=False, oscuridad=0.0, vel=0.7):
    """Dibuja un personaje de época. Trabaja sobre un recorte del tamaño del personaje (mucho más rápido)."""
    if clave not in _humanos:
        _humanos[clave] = Humano(realista=True, **PERSONAS[clave])
    w, h = int(680 * s) + 40, int(1100 * s) + 40
    ox, oy = int(x - 340 * s) - 20, int(y - 1040 * s) - 20
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    _humanos[clave].dibujar(capa, x - ox, y - oy, s, t, pose=pose, espejo=espejo, vel=vel)
    if oscuridad > 0:
        a = np.asarray(capa).astype(np.float32)
        a[..., :3] *= (1 - oscuridad)
        a[..., 2] += 18 * oscuridad
        capa = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # pegar recortando lo que quede fuera del cuadro
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(img.width, ox + w), min(img.height, oy + h)
    if x1 <= x0 or y1 <= y0:
        return
    img.alpha_composite(capa.crop((x0 - ox, y0 - oy, x1 - ox, y1 - oy)), (x0, y0))


def personas_de(ctx):
    p = ctx["det"].get("per")
    return [] if not p else (p if isinstance(p, list) else [p])


# --------------------------------------------------------------------------- #
# DETALLES REALES POR MISTERIO
# --------------------------------------------------------------------------- #
DETALLES = {
    1: dict(bar="bergantin", hora="niebla"),
    2: dict(av="avenger", nav=5, hora="atardecer"),
    3: dict(av="777", hora="noche"),
    4: dict(av="electra", hora="dia", isla=True),
    5: dict(faro="blanco", hora="tormenta"),
    7: dict(hora="noche", carpa=True),
    8: dict(obj="wow"),
    9: dict(obj="voynich"),
    10: dict(obj="zodiaco", per="traje", epoca=1969),
    11: dict(per="abrigo", epoca=1888, hora="niebla"),
    12: dict(obj="tamam", per="traje", seq=[("playa", 0), ("escritorio", 0), ("calle", 1), ("playa", 1)]),
    13: dict(per="mujer_abrigo", hora="frio"),
    14: dict(av="lancastrian", hora="frio", fondo="andes", radio="STENDEC"),
    15: dict(bar="goleta5", hora="dia", faro="espiral",
             seq=[("mar", 0), ("faro", 0), ("escritorio", 1), ("mar", 1)]),
    16: dict(bar="carbonero", hora="tormenta"),
    17: dict(bar="yate", hora="dia", escora=14),
    18: dict(av="constellation", hora="noche"),
    20: dict(bar="vapor_waratah", hora="tormenta"),
    21: dict(av="cessna", hora="atardecer", ovni="verde",
             seq=[("avion", 0), ("radio", 1), ("luces", 1), ("mapa", 0)], radio="NO ES UN AVIÓN"),
    22: dict(av="globo", hora="frio", fondo="artico", seq=[("avion", 0), ("nieve", 1), ("mapa", 0), ("escritorio", 2)]),
    23: dict(per=["escalador", "escalador"], hora="frio"),
    24: dict(per="explorador"),
    25: dict(per="anciano", seq=[("desierto", 0), ("escritorio", 2), ("desierto", 1), ("cartel", 0)]),
    26: dict(av="norseman", hora="niebla"),
    27: dict(av="p38", hora="dia"),
    28: dict(bar="ferry", hora="noche", per="traje"),
    29: dict(seq=[("playa", 2), ("escritorio", 1), ("playa", 0), ("mapa", 0)]),
    30: dict(per="traje", seq=[("tren", 0), ("escritorio", 2), ("calle", 1), ("tren", 1)], epoca=1890),
    31: dict(per="camisa_blanca"),
    32: dict(per="mujer1920", auto="1920", seq=[("lago", 1), ("escritorio", 1), ("calle", 0), ("lago", 2)],
             epoca=1926),
    33: dict(per="traje", auto="1975", epoca=1975),
    34: dict(per="abrigo", hora="frio", nieve=True, epoca=1945),
    35: dict(per="joven", epoca=1828),
    36: dict(rui="torre", seq=[("ruinas", 2), ("escritorio", 2), ("ruinas", 0), ("mapa", 0)]),
    37: dict(seq=[("casa", 1), ("escritorio", 1), ("casa", 0), ("cartel", 0)]),
    38: dict(per="parka_roja", hora="frio"),
    39: dict(per=["traje", "traje_claro"], hora="noche"),
    40: dict(obj="max"),
    41: dict(obj="cigarra"),
    43: dict(rui="tumba"), 44: dict(rui="tumba"), 92: dict(rui="tumba"),
    45: dict(rui="estepa"),
    46: dict(rui="columnas"),
    47: dict(seq=[("submarino", 0), ("escritorio", 0), ("ruinas", 1), ("submarino", 1)], rui="columnas"),
    48: dict(bar="galera", hora="dia"),
    49: dict(rui="escalonada"), 50: dict(rui="escalonada"), 70: dict(rui="escalonada"),
    51: dict(rui="olmeca"),
    52: dict(rui="nazca", anio="", av="cessna", hora="dia", fondo="desierto",
             seq=[("ruinas", 0), ("avion", 0), ("escritorio", 1), ("mapa", 0)]),
    53: dict(rui="piedras"),
    54: dict(rui="tpilares"),
    55: dict(rui="moai"),
    56: dict(obj="rongorongo"), 57: dict(obj="tablilla"), 58: dict(obj="festo"), 59: dict(obj="indo"),
    60: dict(obj="engranajes", bar="galera", seq=[("submarino", 0), ("escritorio", 0), ("mar", 0), ("escritorio", 1)]),
    62: dict(obj="sabana"), 63: dict(obj="cobre"), 64: dict(obj="beale"), 65: dict(obj="dorabella"),
    66: dict(obj="monumento"),
    68: dict(bar="bergantin", hora="atardecer"),
    69: dict(balsa=True, seq=[("lago", 1), ("mapa", 0), ("selva", 0), ("lago", 0)]),
    72: dict(seq=[("desierto", 0), ("mapa", 0), ("cueva", 0), ("desierto", 1)]),
    73: dict(seq=[("palacio", 0), ("escritorio", 1), ("palacio", 1), ("tren", 1)]),
    74: dict(seq=[("tren", 1), ("mapa", 0), ("cueva", 0), ("tren", 0)]),
    77: dict(seq=[("desierto", 2), ("luces", 0), ("desierto", 1), ("escritorio", 1)]),
    78: dict(seq=[("desierto", 2), ("escritorio", 1), ("radio", 0), ("desierto", 1)]),
    79: dict(huellas=True, hora="frio", seq=[("nieve", 2), ("escritorio", 1), ("casa", 2), ("nieve", 1)]),
    80: dict(per=["nino_verde", "nino_verde"], seq=[("casa", 2), ("escritorio", 2), ("bosque", 1), ("casa", 0)]),
    81: dict(seq=[("casa", 2), ("escritorio", 1), ("mapa", 0), ("radio", 0)], carne=True),
    82: dict(av="f18", hora="dia", ovni="tictac", seq=[("avion", 0), ("radar", 0), ("luces", 1), ("escritorio", 1)]),
    83: dict(ovni="v", seq=[("luces", 1), ("desierto", 2), ("escritorio", 1), ("luces", 0)]),
    84: dict(seq=[("desierto", 1), ("escritorio", 1), ("luces", 1), ("desierto", 0)], restos=True),
    86: dict(seq=[("casa", 2), ("escritorio", 1), ("lago", 2), ("bosque", 0)], ojos=True),
    87: dict(bar="carguero", hora="niebla"),
    88: dict(bar="catamaran", hora="dia"),
    89: dict(per="mujer1910", epoca=1910),
    90: dict(bar="balandra", hora="tormenta"),
    91: dict(per="joven_lentes", bar="catamaran"),
    94: dict(obj="diamante"),
    95: dict(seq=[("submarino", 0), ("radar", 0), ("radio", 0), ("submarino", 1)]),
    96: dict(seq=[("submarino", 0), ("mapa", 0), ("submarino", 1), ("escritorio", 0)], rui="terrazas"),
    97: dict(rui="esfera"),
    98: dict(bar="franklin", hora="frio", seq=[("mar", 0), ("nieve", 1), ("mapa", 0), ("escritorio", 2)]),
}


# --------------------------------------------------------------------------- #
# ESCENARIOS NUEVOS
# --------------------------------------------------------------------------- #
def kit_desierto(ctx, var):
    hora = ["atardecer", "dia", "noche"][var % 3]

    def dib(L):
        cielo(L, hora)
        arena = {"atardecer": (196, 128, 84), "dia": (214, 176, 120), "noche": (60, 52, 64)}[hora]
        meseta = oscuro(arena, 0.72)
        L.forma([(-50, 1180), (120, 900), (360, 890), (420, 1180)], meseta, suave=False, intensidad=0.12, textura=0.14)
        L.forma([(560, 1180), (680, 980), (980, 970), (1130, 1180)], oscuro(meseta, 0.9), suave=False,
                intensidad=0.12, textura=0.14)
        L.forma(catmull([(-50, 1180), (W + 50, 1160), (W + 50, H), (-50, H)], 3), arena, borde=False, textura=0.16)
        rr = random.Random(ctx["n"])
        verde = (70, 110, 70) if hora != "noche" else (30, 44, 40)
        for _ in range(4):  # cactus saguaro
            x, y, s = rr.uniform(60, 1020), rr.uniform(1300, 1700), rr.uniform(0.6, 1.1)
            L.forma(catmull([(x - 22 * s, y), (x - 22 * s, y - 300 * s), (x, y - 330 * s), (x + 22 * s, y - 300 * s),
                             (x + 22 * s, y)], 3), verde, intensidad=0.18, textura=0.08)
            for lado in (-1, 1):
                L.forma(catmull([(x + lado * 20 * s, y - 140 * s), (x + lado * 75 * s, y - 150 * s),
                                 (x + lado * 80 * s, y - 230 * s), (x + lado * 58 * s, y - 230 * s),
                                 (x + lado * 55 * s, y - 175 * s), (x + lado * 20 * s, y - 170 * s)], 3), verde,
                        intensidad=0.15)
        if ctx["det"].get("restos"):  # Roswell: restos metálicos en el campo
            for _ in range(14):
                x, y = rr.uniform(150, 950), rr.uniform(1250, 1450)
                L.forma([(x, y), (x + rr.uniform(20, 60), y - 10), (x + 40, y + 16)], (200, 204, 210), suave=False,
                        intensidad=0.3, ancho=2)
    fondo = full(dib)
    if hora == "atardecer":
        pegar_glow(fondo, 540, 1120, 420, "#ffb060", 0.8)
    elif hora == "noche":
        pegar_glow(fondo, 260, 300, 120, "#e0e8ff", 0.6)

    def din(img, t, dur):
        per = personas_de(ctx)
        if per:
            figura(img, per[0], 560 - t * 12, 1500, 0.55, t, oscuridad=0.5 if hora == "noche" else 0.1)
        if hora == "noche":
            for i in range(3):
                pegar_glow(img, 300 + i * 220 + 30 * math.sin(t + i), 1050 + 20 * math.sin(t * 1.3 + i), 30,
                           "#ffe0a0", 0.5 + 0.4 * math.sin(t * 2 + i))
        else:
            particulas(img, t, "ceniza", 30, viento=200, alfa=90)
    return fondo, din


def kit_submarino(ctx, var):
    def dib(L):
        L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (30, 110, 140)), (0.5, (12, 50, 76)), (1, (4, 16, 30))]))
        piedra = (70, 96, 100)
        rui = ctx["det"].get("rui")
        if ctx["det"].get("bar") == "galera" or ctx["n"] == 60:  # naufragio antiguo con ánforas
            for k in range(7):
                x = 250 + k * 90
                L.forma(catmull([(x - 20, 1600), (x - 36, 1520), (x - 12, 1440), (x + 12, 1440), (x + 36, 1520),
                                 (x + 20, 1600)], 3), (150, 90, 60), intensidad=0.18, textura=0.12)
            L.forma([(100, 1640), (980, 1600), (1000, 1660), (80, 1700)], (90, 60, 40), suave=False, intensidad=0.1)
        elif rui == "terrazas":  # Yonaguni: escalones de roca
            for k in range(5):
                y = 1250 + k * 110
                L.forma([(80 + k * 40, y), (1000 - k * 30, y), (1000 - k * 30, y + 120), (80 + k * 40, y + 120)],
                        oscuro(piedra, 1 - k * 0.06), suave=False, intensidad=0.08, textura=0.18)
        else:  # ciudad sumergida: columnas caídas
            for k in range(5):
                x, h = 160 + k * 190, [420, 300, 520, 260, 380][k]
                L.forma([(x - 40, 1650), (x - 36, 1650 - h), (x + 36, 1650 - h), (x + 40, 1650)], piedra,
                        suave=False, intensidad=0.14, textura=0.18)
            L.forma([(200, 1700), (900, 1640), (920, 1700), (210, 1760)], piedra, suave=False, intensidad=0.1)
        L.forma(catmull([(-50, 1680), (W + 50, 1660), (W + 50, H), (-50, H)], 3), (60, 70, 60), borde=False,
                textura=0.2)
        rr = random.Random(9)
        for _ in range(12):  # algas
            x = rr.uniform(0, W)
            L.linea(catmull([(x, 1720), (x + 20, 1600), (x - 10, 1500), (x + 15, 1400)], 4, cerrado=False),
                    (40, 90, 60), 8)
    fondo = full(dib)

    def din(img, t, dur):
        capa = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        for k in range(5):  # rayos de luz
            x = (120 + k * 220 + 40 * math.sin(t * 0.4 + k)) / 4
            d.polygon([(x - 8, 0), (x + 8, 0), (x + 60, H / 4), (x - 30, H / 4)], fill=(180, 240, 255, 34))
        img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(4)).resize((W, H)))
        r = random.Random(4)
        for i in range(24):  # burbujas
            x = r.uniform(80, 1000) + 10 * math.sin(t * 2 + i)
            y = (r.uniform(0, H) - t * r.uniform(60, 140)) % H
            d2 = ImageDraw.Draw(img)
            rr = r.uniform(4, 10)
            d2.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(200, 240, 255, 150), width=2)
        if ctx["n"] == 95 and var == 1:  # el Bloop: sombra enorme lejana
            pegar_glow(img, 540 + 80 * math.sin(t * 0.3), 900, 420, "#001018", 0.6)
    return fondo, din


def kit_playa(ctx, var):
    hora = ["atardecer", "niebla", "dia"][var % 3]

    def dib(L):
        cielo(L, hora)
        mar_col = {"atardecer": (70, 70, 96), "niebla": (110, 120, 126), "dia": (40, 110, 150)}[hora]
        L.forma([(0, 1050), (W, 1050), (W, 1400), (0, 1400)], mar_col, suave=False, borde=False, textura=0.05)
        arena = (206, 184, 140) if hora != "atardecer" else (190, 150, 120)
        L.forma(catmull([(-50, 1380), (400, 1340), (W + 50, 1420), (W + 50, H), (-50, H)], 3), arena, borde=False,
                textura=0.16)
        L.forma([(-50, 1560), (W + 50, 1520), (W + 50, 1600), (-50, 1640)], (150, 140, 126), suave=False,
                intensidad=0.08, textura=0.2)  # malecón de piedra
    fondo = full(dib)
    if hora == "atardecer":
        pegar_glow(fondo, 800, 1040, 260, "#ffb070", 0.8)

    def din(img, t, dur):
        olas(img, t, 1060, col=(230, 240, 250), alfa=150 if var == 2 else 100)
        for k in range(3):  # espuma que llega a la orilla
            f = (t * 0.25 + k / 3) % 1
            y = 1360 + 40 * f
            ImageDraw.Draw(img).line([(x, y + 6 * math.sin(x * 0.03 + t)) for x in range(0, W, 20)],
                                     fill=(250, 250, 250, int(200 * (1 - f))), width=6)
        per = personas_de(ctx)
        if per and var != 2:
            figura(img, per[0], 330, 1700, 0.5, t, pose="quieto", espejo=True, oscuridad=0.25)
        if hora == "niebla":
            niebla(img, t, 1200, 0.5)
    return fondo, din


def kit_tren(ctx, var):
    noche = var == 1

    def dib(L):
        cielo(L, "noche" if noche else "niebla")
        if noche:  # montañas y túnel (tren del oro)
            L.forma([(-50, 1300), (200, 700), (500, 650), (800, 760), (W + 50, 1300)], (40, 44, 54), suave=False,
                    intensidad=0.1, textura=0.14)
            L.forma(catmull([(620, 1300), (640, 1120), (760, 1080), (880, 1120), (900, 1300)], 4), (14, 14, 18),
                    borde=False)
        else:  # estación del siglo XIX
            L.forma([(0, 600), (W, 600), (W, 640), (0, 640)], (60, 54, 50), suave=False)
            for x in range(60, W, 240):
                L.linea([(x, 640), (x, 1300)], (60, 54, 50), 14)
        L.forma([(0, 1300), (W, 1300), (W, H), (0, H)], (70, 64, 60), suave=False, borde=False, textura=0.18)
        for k in range(14):
            L.linea([(k * 80, 1330), (k * 80 + 30, 1370)], (90, 70, 50), 10)
        L.linea([(0, 1330), (W, 1330)], (160, 160, 166), 6)
        L.linea([(0, 1372), (W, 1372)], (160, 160, 166), 6)
    fondo = full(dib)
    loco = R.tren()

    def din(img, t, dur):
        x = -300 + t * 120 if not noche else 900 - t * 90
        img.alpha_composite(loco, (int(x - loco.width / 2), int(1350 - loco.height * 0.85)))
        for k in range(6):  # humo
            f = (t * 0.6 + k / 6) % 1
            pegar_glow(img, x + 420 * (loco.width / 1500) - 60 * f * 3, 1020 - 300 * f, 60 + 120 * f,
                       "#c8c8cc", 0.5 * (1 - f))
        pegar_glow(img, x + 640 * loco.width / 1500, 1260, 60, "#fff0b0", 0.9)
        per = personas_de(ctx)
        if per and not noche:
            figura(img, per[0], 780, 1560, 0.5, t, pose="quieto", espejo=True)
        if noche:
            particulas(img, t, "nieve", 60, viento=-100, alfa=200)
        niebla(img, t, 1300, 0.3)
    return fondo, din


def kit_casa(ctx, var):
    fuego = var == 1
    hora = "noche" if var in (0, 1) else "frio"

    def dib(L):
        cielo(L, hora)
        L.forma(catmull([(-50, 1500), (W + 50, 1480), (W + 50, H), (-50, H)], 3),
                (40, 54, 40) if hora == "noche" else (226, 232, 240), borde=False, textura=0.14)
        rr = random.Random(ctx["n"])
        from misterios import pinos
        pinos(L, 1500, 8, 520, (24, 32, 30) if hora == "noche" else (60, 76, 70), rr)
    fondo = full(dib)
    c = R.casa(fuego)

    def din(img, t, dur):
        img.alpha_composite(c, (540 - c.width // 2, 1530 - c.height))
        if fuego:
            for k in range(14):
                f = (t * 0.8 + k / 14) % 1
                x = 300 + (k * 53) % 480
                pegar_glow(img, x, 1150 - 500 * f, 90 * (1 - f) + 30, "#ff8a30", 0.8 * (1 - f))
            pegar_glow(img, 540, 1250, 420, "#ff6020", 0.45 + 0.1 * math.sin(t * 9))
            particulas(img, t, "ceniza", 50, viento=60, alfa=200)
        else:
            pegar_glow(img, 540, 1300, 200, "#ffd890", 0.25)
        det = ctx["det"]
        if det.get("ojos"):
            for i, x in enumerate((180, 900)):
                pegar_glow(img, x - 14, 1600, 10, "#ff2020", 0.9)
                pegar_glow(img, x + 14, 1600, 10, "#ff2020", 0.9)
        if det.get("carne"):
            r = random.Random(3)
            for i in range(30):
                x = r.uniform(0, W)
                y = (r.uniform(0, H) + t * r.uniform(300, 500)) % (H - 300)
                ImageDraw.Draw(img).ellipse((x - 9, y - 6, x + 9, y + 6), fill=(150, 40, 40))
        if det.get("huellas"):
            d = ImageDraw.Draw(img)
            for k in range(10):
                x, y = 120 + k * 90, 1620 - (k % 2) * 30
                d.ellipse((x - 14, y - 10, x + 14, y + 10), fill=(140, 150, 176))
        per = personas_de(ctx)
        for k, p in enumerate(per):
            figura(img, p, 380 + k * 300, 1700, 0.42, t, pose="quieto", espejo=k == 1, oscuridad=0.35)
        if hora == "frio":
            particulas(img, t, "nieve", 60, viento=-80, alfa=200)
    return fondo, din


def kit_palacio(ctx, var):
    """Cámara de Ámbar: paneles dorados iluminados por velas."""
    def dib(L):
        L.d.rectangle((0, 0, W * 2, H * 2), fill=(60, 30, 10))
        ambar = (214, 140, 40)
        for fila in range(3):
            for col in range(3):
                x, y = 80 + col * 320, 200 + fila * 420
                L.forma([(x, y), (x + 280, y), (x + 280, y + 380), (x, y + 380)], ambar, suave=False,
                        intensidad=0.2, textura=0.3)
                L.forma(elipse(x + 140, y + 190, 90, 130), claro(ambar, 0.2), intensidad=0.25, textura=0.2)
        L.forma([(0, 1500), (W, 1500), (W, H), (0, H)], (90, 50, 30), suave=False, borde=False, textura=0.2)
    fondo = full(dib)

    def din(img, t, dur):
        for x in (200, 540, 880):
            fl = 1 + 0.15 * math.sin(t * 12 + x)
            pegar_glow(img, x, 1440, 160 * fl, "#ffb040", 0.7)
            pegar_glow(img, x, 1440, 26, "#fff0c0", 1)
        if var == 1:  # se oscurece: la sala desaparece
            k = min(1.0, t / max(dur, 0.1))
            img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(190 * k))))
    return fondo, din


KITS_EXTRA = {"desierto": kit_desierto, "submarino": kit_submarino, "playa": kit_playa, "tren": kit_tren,
              "casa": kit_casa, "palacio": kit_palacio}


# --------------------------------------------------------------------------- #
# OBJETOS HISTÓRICOS (sobre el escritorio)
# --------------------------------------------------------------------------- #
def objeto(nombre, rnd):
    """Devuelve una imagen RGBA (~760x980) del objeto real del misterio, o None."""
    serif = lambda s: ImageFont.truetype(SERIF, s)
    papel = (238, 226, 196)
    if nombre == "wow":  # impresión de computadora con el 6EQUJ5 marcado en rojo
        im = Image.new("RGBA", (760, 980), (244, 244, 236, 255))
        d = ImageDraw.Draw(im)
        for y in range(0, 980, 60):
            d.rectangle((0, y, 760, y + 30), fill=(214, 236, 214))
        f = maquina(40)
        for k in range(15):
            fila = "".join(rnd.choice("1111112   ") for _ in range(12))
            if k == 7:
                fila = "  6EQUJ5    "
            d.text((140, 40 + k * 60), fila, font=f, fill=(50, 50, 60))
        d.ellipse((150, 440, 420, 530), outline=(210, 30, 30), width=8)
        d.text((470, 470), "Wow!", font=manuscrita(90), fill=(210, 30, 30), anchor="lm")
        return im
    if nombre in ("voynich", "rongorongo", "tablilla", "festo", "indo", "cobre", "beale", "dorabella", "monumento",
                  "tamam", "zodiaco", "sabana", "engranajes", "diamante", "max", "cigarra"):
        pass
    else:
        return None
    if nombre == "voynich":
        im = Image.new("RGBA", (760, 980), (224, 208, 168, 255))
        d = ImageDraw.Draw(im)
        verde, cafe = (96, 130, 70), (110, 70, 40)
        d.line([(380, 700), (370, 500), (390, 300)], fill=cafe, width=10)
        for k in range(6):
            a = -0.9 + k * 0.36
            x, y = 380 + 170 * math.cos(a - 1.57), 380 + 120 * math.sin(a - 1.57)
            d.ellipse((x - 80, y - 36, x + 80, y + 36), fill=verde, outline=cafe, width=3)
        for x in (300, 380, 460):
            d.line([(380, 700), (x, 780)], fill=cafe, width=6)
        f = manuscrita(34)
        for k in range(5):
            d.text((60, 820 + k * 30), "".join(rnd.choice("oaeqdc89") for _ in range(26)), font=f, fill=(80, 50, 30))
        for k in range(4):
            d.text((60, 60 + k * 44), "".join(rnd.choice("oaeqdc89") for _ in range(26)), font=f, fill=(80, 50, 30))
        return im
    if nombre == "festo":  # disco de arcilla con espiral de símbolos
        im = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse((40, 40, 860, 860), fill=(190, 140, 90), outline=(120, 80, 50), width=10)
        f = serif(40)
        for k in range(70):
            a = k * 0.42
            rr = 380 - k * 4.6
            if rr < 40:
                break
            x, y = 450 + rr * math.cos(a), 450 + rr * math.sin(a)
            d.text((x, y), rnd.choice("ΨΦΔΩЖЯ†§λ"), font=f, fill=(90, 56, 30), anchor="mm")
        d.line([(450 + 400 * math.cos(a), 450 + 400 * math.sin(a)) for a in np.linspace(0, 26, 300)
                if 400 - a * 13 > 30], fill=(120, 80, 50), width=3)
        return im
    if nombre in ("tablilla", "indo", "rongorongo", "cobre"):
        col = {"tablilla": (176, 130, 90), "indo": (200, 190, 170), "rongorongo": (110, 72, 44),
               "cobre": (160, 96, 56)}[nombre]
        im = Image.new("RGBA", (760, 820), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if nombre == "indo":
            d.rounded_rectangle((130, 130, 630, 630), radius=30, fill=col, outline=oscuro(col, 0.6), width=10)
            d.text((380, 210), "ᚦ ⋈ ⊥ ‖ ⋔", font=serif(56), fill=oscuro(col, 0.45), anchor="mm")
            d.ellipse((220, 300, 560, 520), outline=oscuro(col, 0.5), width=10)  # animal del sello (estilizado)
            d.line((300, 520, 300, 590), fill=oscuro(col, 0.5), width=10)
            d.line((480, 520, 480, 590), fill=oscuro(col, 0.5), width=10)
            d.line((540, 360, 640, 260), fill=oscuro(col, 0.5), width=10)
            return im
        d.rounded_rectangle((60, 60, 700, 760), radius=40, fill=col, outline=oscuro(col, 0.6), width=10)
        if nombre == "cobre":
            for k in range(8):
                d.arc((60, 60 + k * 86, 700, 160 + k * 86), 180, 360, fill=claro(col, 0.3), width=4)
        f = serif(44)
        for row in range(9):
            for c in range(8):
                g = rnd.choice("ΨΦΔΩЖЯ†§λΠ" if nombre != "rongorongo" else "ψλΨΦ¥ጰᐃ†")
                d.text((110 + c * 72, 110 + row * 70), g, font=f, fill=oscuro(col, 0.45))
        return im
    if nombre == "beale":  # columnas de números
        im = Image.new("RGBA", (760, 980), papel + (255,))
        d = ImageDraw.Draw(im)
        f = maquina(34)
        for k in range(22):
            d.text((50, 40 + k * 42), ", ".join(str(rnd.randint(1, 999)) for _ in range(7)), font=f, fill=(50, 40, 30))
        return im
    if nombre == "dorabella":  # semicírculos en grupos de tres
        im = Image.new("RGBA", (860, 520), papel + (255,))
        d = ImageDraw.Draw(im)
        for row in range(3):
            for k in range(22):
                x, y = 60 + k * 34, 120 + row * 140
                a = rnd.choice((0, 90, 180, 270, 45, 135))
                for j in range(rnd.randint(1, 3)):
                    rr = 10 + j * 7
                    d.arc((x - rr, y - rr, x + rr, y + rr), a, a + 180, fill=(40, 40, 90), width=4)
        return im
    if nombre == "monumento":  # Shugborough: relieve con letras
        im = Image.new("RGBA", (800, 820), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle((40, 40, 760, 780), fill=(196, 190, 176), outline=(120, 114, 100), width=12)
        d.rectangle((120, 110, 680, 520), fill=(170, 164, 150))
        for x in (200, 330, 460, 590):
            d.line((x, 480, x, 260), fill=(120, 114, 100), width=14)
            d.ellipse((x - 30, 200, x + 30, 260), fill=(140, 134, 120))
        d.text((400, 600), "O U O S V A V V", font=serif(50), fill=(70, 66, 60), anchor="mm")
        d.text((400, 700), "D.                M.", font=serif(46), fill=(70, 66, 60), anchor="mm")
        return im
    if nombre == "tamam":  # trozo de papel "Tamám Shud"
        im = Image.new("RGBA", (700, 300), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.polygon([(20, 40), (680, 20), (660, 270), (40, 280)], fill=papel + (255,))
        d.text((350, 150), "Tamám Shud", font=serif(80), fill=(40, 40, 50), anchor="mm")
        return im
    if nombre == "zodiaco":  # cifrado con el símbolo de mira
        im = Image.new("RGBA", (760, 980), (244, 240, 230, 255))
        d = ImageDraw.Draw(im)
        f = serif(48)
        for row in range(12):
            for c in range(9):
                d.text((60 + c * 76, 120 + row * 70), rnd.choice("ΔΣΦΨΩ+KЯ⊥¶◊>"), font=f, fill=(30, 30, 40))
        d.ellipse((560, 20, 720, 180), outline=(20, 20, 30), width=10)
        d.line((640, 0, 640, 200), fill=(20, 20, 30), width=10)
        d.line((540, 100, 740, 100), fill=(20, 20, 30), width=10)
        return im
    if nombre == "sabana":  # lienzo largo con una figura muy tenue
        im = Image.new("RGBA", (560, 1000), (226, 214, 186, 255))
        d = ImageDraw.Draw(im)
        d.ellipse((220, 120, 340, 260), fill=(196, 176, 146))
        d.rounded_rectangle((190, 260, 370, 700), radius=60, fill=(200, 182, 152))
        d.rounded_rectangle((200, 700, 360, 940), radius=40, fill=(204, 186, 158))
        return im.filter(ImageFilter.GaussianBlur(10))
    if nombre == "engranajes":  # mecanismo de Anticitera: bronce corroído
        im = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for cx, cy, r in ((380, 380, 260), (620, 560, 120), (180, 620, 100)):
            dientes = int(r / 6)
            pts = []
            for k in range(dientes * 2):
                a = k * math.pi / dientes
                rr = r if k % 2 == 0 else r - 16
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            d.polygon(pts, fill=(96, 120, 90), outline=(50, 70, 50))
            d.ellipse((cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6), outline=(60, 80, 60), width=8)
        return im
    if nombre == "diamante":  # diamante Hope: azul profundo
        im = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        pts = [(400, 140), (620, 300), (560, 620), (240, 620), (180, 300)]
        d.polygon(pts, fill=(30, 60, 160), outline=(180, 210, 255))
        for p in pts:
            d.line((400, 380, p[0], p[1]), fill=(120, 170, 255), width=4)
        d.polygon([(400, 140), (500, 240), (400, 380), (300, 240)], fill=(70, 110, 210))
        return im
    return None


def objeto_sello_extra(nombre):
    return {"wow": "6EQUJ5", "tamam": "TAMÁM SHUD", "monumento": "D · M"}.get(nombre)
