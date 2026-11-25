"""
Compositor de escenas a medida para la serie de misterios.

Cada escena se escribe como una línea corta que dice QUÉ se ve en ese momento del relato, por capas:
    "cielo atardecer sol | mar | barco bergantin 540 1180 0.8 | gaviotas"
Cada capa es un elemento dibujado (fondo, lugar, vehículo, persona, objeto, efecto) con su animación.
Números = x, y, escala. palabra = opción. clave=valor = parámetro (los guiones bajos se vuelven espacios).
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import mis_reales as R
import pro
from alcatraz import linterna, maquina, niebla, olas, silueta
from cine import pegar_glow
from dinos import TINTA, _grad, catmull, claro, elipse, oscuro, sombra_suave
from mis_kits import PALETAS, PERSONAS, figura, nubes
from mis_v3 import polvo, rayos
from pro import H, W, manuscrita, particulas, relampago
from realista import LienzoReal

PROPS = {}
SONIDOS = {}


def prop(nombre, tipo="L", sonido=None):
    """tipo: 'L' dibujo fijo con lienzo realista, 'img' fijo sobre la imagen, 'dyn' animado en cada cuadro."""
    def deco(fn):
        PROPS[nombre] = (tipo, fn)
        if sonido:
            SONIDOS[nombre] = sonido
        return fn
    return deco


class Esc:
    """Estado compartido de una escena (hora, línea del horizonte, azar con semilla)."""

    def __init__(self, ctx, semilla):
        self.ctx = ctx
        self.hora = "noche"
        self.horizonte = 1150
        self.r = random.Random(semilla)


def _parse(seg):
    toks = seg.split()
    nombre, nums, flags, kw = toks[0], [], set(), {}
    for t in toks[1:]:
        if "=" in t:
            k, v = t.split("=", 1)
            kw[k] = v.replace("_", " ") if k in ("txt", "firma", "fecha", "cab") else v
        else:
            try:
                nums.append(float(t))
            except ValueError:
                flags.add(t)
    return nombre, nums, flags, kw


def componer(spec, ctx, semilla=0):
    """Devuelve (fondo, din) a partir de una descripción de escena."""
    sc = Esc(ctx, semilla)
    capas = []  # ("img", Image) | ("dyn", fn)
    lienzo = None
    grupo = None

    def volcar():
        nonlocal lienzo, grupo
        if lienzo is not None:
            im = lienzo.final()
            grupo = im if grupo is None else Image.alpha_composite(grupo, im)
            lienzo = None

    for seg in [s.strip() for s in spec.split("|") if s.strip()]:
        nombre, nums, flags, kw = _parse(seg)
        if nombre not in PROPS:
            raise KeyError(f"elemento desconocido: {nombre}")
        tipo, fn = PROPS[nombre]
        if tipo == "L":
            if lienzo is None:
                lienzo = LienzoReal(W, H, 0, 0)
            fn(sc, lienzo, nums, flags, kw)
        elif tipo == "img":
            volcar()
            if grupo is None:
                grupo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fn(sc, grupo, nums, flags, kw)
        else:
            volcar()
            if grupo is not None:
                capas.append(("img", grupo))
                grupo = None
            capas.append(("dyn", fn(sc, nums, flags, kw)))
    volcar()
    if grupo is not None:
        capas.append(("img", grupo))
    if not capas or capas[0][0] != "img":
        capas.insert(0, ("img", Image.new("RGBA", (W, H), (10, 10, 14, 255))))
    fondo = capas[0][1]
    if fondo.getchannel("A").getextrema()[0] < 255:  # el fondo debe ser opaco
        base = Image.new("RGBA", (W, H), (10, 10, 14, 255))
        fondo = Image.alpha_composite(base, fondo)
    resto = capas[1:]

    def din(img, t, dur):
        for tipo, c in resto:
            if tipo == "img":
                img.alpha_composite(c)
            else:
                c(img, t, dur)
    return fondo, din


def sonidos_de(spec, dur):
    ev = []
    for seg in spec.split("|"):
        seg = seg.strip()
        if not seg:
            continue
        nombre, nums, flags, kw = _parse(seg)
        s = SONIDOS.get(nombre)
        if callable(s):
            s = s(flags, kw)
        for k, (tipo, t0, d) in enumerate(s or []):
            ev.append((t0 if t0 >= 0 else 0.0, tipo, d if d > 0 else dur))
    return ev


def _n(nums, i, defecto):
    return nums[i] if len(nums) > i else defecto


def _col(kw, defecto):
    if "col" in kw:
        v = kw["col"].lstrip("#")
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    return defecto


# =========================================================================== #
# CIELO, AGUA Y SUELO
# =========================================================================== #
PALETAS_EXTRA = {
    "amanecer": [(0, (40, 50, 96)), (0.5, (220, 140, 120)), (0.62, (250, 200, 150)), (1, (250, 200, 150))],
    "aurora": [(0, (6, 14, 30)), (0.6, (16, 40, 60)), (1, (16, 40, 60))],
    "interior": [(0, (30, 26, 24)), (1, (30, 26, 24))],
}


@prop("cielo", "L")
def p_cielo(sc, L, nums, flags, kw):
    hora = next((f for f in flags if f in PALETAS or f in PALETAS_EXTRA), "noche")
    sc.hora = hora
    L.img.alpha_composite(_grad(W * 2, H * 2, PALETAS.get(hora) or PALETAS_EXTRA[hora]))
    if hora in ("noche", "tormenta", "aurora") or "estrellas" in flags:
        rr = random.Random(5 + sc.r.randint(0, 99))
        for _ in range(150):
            L.circulo(rr.randint(0, W), rr.randint(0, 1150), rr.choice((1.5, 2, 2.5)), (230, 230, 255), borde=False)


@prop("astro", "img")
def p_astro(sc, img, nums, flags, kw):
    x, y, r = _n(nums, 0, 820), _n(nums, 1, 320), _n(nums, 2, 50)
    if "sol" in flags:
        pegar_glow(img, x, y, r * 6, "#ffd890", 0.8)
        ImageDraw.Draw(img).ellipse((x - r, y - r, x + r, y + r), fill=(255, 244, 210))
    else:
        pegar_glow(img, x, y, r * 4, "#dfe8ff", 0.6)
        ImageDraw.Draw(img).ellipse((x - r, y - r, x + r, y + r), fill=(236, 238, 246))


@prop("aurora", "dyn")
def p_aurora(sc, nums, flags, kw):
    def f(img, t, dur):
        capa = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        for k in range(3):
            pts = [(x, 60 + k * 25 + 18 * math.sin(x * 0.04 + t * 0.6 + k)) for x in range(0, W // 4 + 10, 10)]
            d.line(pts, fill=(80, 255, 160, 60 - k * 12), width=16)
        img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(6)).resize((W, H)))
    return f


@prop("nubes", "dyn")
def p_nubes(sc, nums, flags, kw):
    y = _n(nums, 0, 600)
    def f(img, t, dur):
        nubes(img, t, sc.hora if sc.hora != "tormenta" else "noche", y=y, n=int(_n(nums, 1, 5)), semilla=sc.r.randint(0, 9))
    return f


COLOR_MAR = {"dia": (40, 104, 150), "atardecer": (70, 64, 90), "niebla": (96, 108, 116), "frio": (120, 146, 170),
             "amanecer": (90, 96, 130), "noche": (18, 30, 46), "tormenta": (24, 32, 42), "aurora": (14, 26, 40)}


@prop("mar", "L", sonido=[("olas", 0, 0)])
def p_mar(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1150)
    sc.horizonte = y
    col = _col(kw, COLOR_MAR.get(sc.hora, (22, 34, 46)))
    L.forma([(0, y), (W, y), (W, H), (0, H)], col, suave=False, borde=False, intensidad=0.02, textura=0.08)
    L.img.alpha_composite(_grad(W * 2, int(H * 2 - y * 2), [(0, claro(col, 0.25) + (120,)), (1, col + (0,))])
                          .resize((W * 2, int(H * 2 - y * 2))), (0, int(y * 2)))


@prop("olas", "dyn")
def p_olas(sc, nums, flags, kw):
    y = _n(nums, 0, sc.horizonte + 15)
    col = (220, 230, 240) if sc.hora in ("dia", "niebla", "frio") else (120, 150, 180)
    alfa = 160 if "bravo" in flags else 110
    def f(img, t, dur):
        olas(img, t * (1.8 if "bravo" in flags else 1), y, col=col, alfa=alfa)
    return f


SUELOS = {"arena": (210, 176, 124), "nieve": (230, 236, 244), "hielo": (206, 224, 236), "pasto": (90, 124, 64),
          "tierra": (120, 92, 66), "roca": (96, 90, 88), "asfalto": (54, 54, 60), "adoquin": (80, 74, 72),
          "barro": (86, 70, 52), "madera": (110, 76, 50), "baldosa": (150, 140, 126), "piedra": (130, 122, 112),
          "pantano": (60, 76, 56)}


@prop("suelo", "L")
def p_suelo(sc, L, nums, flags, kw):
    tipo = next((f for f in flags if f in SUELOS), "tierra")
    y = _n(nums, 0, 1300)
    col = SUELOS[tipo]
    if sc.hora in ("noche", "tormenta", "aurora"):
        col = oscuro(col, 0.45)
    elif sc.hora in ("atardecer",):
        col = oscuro(col, 0.85)
    L.forma(catmull([(-60, y + 10), (W * 0.35, y - 12), (W * 0.7, y + 8), (W + 60, y - 6), (W + 60, H), (-60, H)], 4),
            col, borde=False, textura=0.18, intensidad=0.05)
    rr = random.Random(int(y))
    if tipo in ("adoquin", "baldosa"):
        for yy in range(int(y) + 20, H, 44):
            for xx in range(0, W, 80):
                L.forma(elipse(xx + (yy // 44 % 2) * 40, yy, 34, 15), oscuro(col, 0.82), borde=False, sombra=False,
                        brillo=False, textura=0)
    elif tipo in ("arena", "nieve", "pasto", "tierra"):
        for _ in range(26):
            xx, yy = rr.uniform(0, W), rr.uniform(y + 40, H)
            L.forma(elipse(xx, yy, rr.uniform(20, 70), rr.uniform(4, 10)), oscuro(col, 0.88), borde=False,
                    sombra=False, brillo=False, textura=0)


@prop("montanas", "L")
def p_montanas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1150)
    alto = _n(nums, 1, 520)
    col = _col(kw, (70, 76, 96) if sc.hora in ("noche", "tormenta", "aurora") else (110, 116, 136))
    rr = random.Random(int(y + alto))
    picos = [(x, alto * rr.uniform(0.6, 1.0), rr.uniform(240, 380)) for x in (120, 420, 760, 1020)]
    if "volcan" in flags:
        L.forma([(150, y), (480, y - alto), (600, y - alto), (930, y)], col, suave=False, intensidad=0.1,
                textura=0.12)
        L.forma([(430, y - alto * 0.86), (480, y - alto), (600, y - alto), (650, y - alto * 0.86), (560, y - alto * 0.8)],
                (236, 240, 246), suave=False, borde=False)
        return
    pro.montanas(L, y, [(x, h, w) for x, h, w in picos], col, nieve="nevadas" in flags, borde=False)


@prop("colinas", "L")
def p_colinas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1200)
    col = _col(kw, (70, 96, 60) if sc.hora not in ("noche", "tormenta") else (30, 40, 30))
    L.forma(catmull([(-60, y + 40), (200, y - 120), (520, y - 40), (820, y - 160), (W + 60, y - 20), (W + 60, H),
                     (-60, H)], 5), col, borde=False, textura=0.14, intensidad=0.06)


@prop("dunas", "L")
def p_dunas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1200)
    col = SUELOS["arena"] if sc.hora not in ("noche",) else (70, 60, 70)
    for k in range(3):
        L.forma(catmull([(-60, y + k * 90), (300, y - 70 + k * 90), (700, y + 20 + k * 90), (W + 60, y - 50 + k * 90),
                         (W + 60, H), (-60, H)], 5), oscuro(col, 0.92 - k * 0.06), borde=False, textura=0.14)


@prop("mesetas", "L")
def p_mesetas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1180)
    col = (176, 104, 72) if sc.hora != "noche" else (50, 40, 50)
    L.forma([(-50, y), (100, y - 300), (380, y - 310), (450, y)], col, suave=False, intensidad=0.14, textura=0.16)
    L.forma([(560, y), (700, y - 200), (1000, y - 210), (1130, y)], oscuro(col, 0.9), suave=False, intensidad=0.14,
            textura=0.16)


@prop("ciudad", "L")
def p_ciudad(sc, L, nums, flags, kw):
    """Silueta de ciudad: era=1888 (chimeneas), 1910 (edificios), 1970/moderna (rascacielos), adobe, medieval."""
    y = _n(nums, 0, 1200)
    era = kw.get("era", "moderna")
    noche = sc.hora in ("noche", "tormenta", "niebla")
    rr = random.Random(int(y) + len(era))
    col = (34, 36, 46) if noche else (120, 124, 136)
    x = -40
    while x < W + 40:
        if era in ("adobe",):
            w, h = rr.uniform(140, 220), rr.uniform(90, 160)
            L.forma([(x, y), (x, y - h), (x + w, y - h), (x + w, y)], (180, 130, 90) if not noche else (70, 54, 50),
                    suave=False, intensidad=0.08, textura=0.14)
        elif era == "medieval":
            w, h = rr.uniform(120, 180), rr.uniform(140, 220)
            L.forma([(x, y), (x, y - h), (x + w / 2, y - h - 90), (x + w, y - h), (x + w, y)], col, suave=False,
                    intensidad=0.08, textura=0.12)
        else:
            w = rr.uniform(90, 170)
            h = rr.uniform(200, 420) * (1.6 if era in ("1970", "moderna") else 1.0)
            L.forma([(x, y), (x, y - h), (x + w, y - h), (x + w, y)], col, suave=False, intensidad=0.05, textura=0.1)
            if era == "1888" and rr.random() < 0.5:
                L.forma([(x + 20, y - h), (x + 20, y - h - 80), (x + 40, y - h - 80), (x + 40, y - h)], col,
                        suave=False, borde=False)
            for yy in range(int(y - h + 30), int(y - 20), 46):
                for xx in range(int(x + 14), int(x + w - 20), 34):
                    if rr.random() < (0.35 if noche else 0.15):
                        L.forma([(xx, yy), (xx + 16, yy), (xx + 16, yy + 22), (xx, yy + 22)],
                                (250, 214, 130) if noche else (150, 170, 190), suave=False, borde=False, sombra=False,
                                brillo=False, textura=0)
        x += w + rr.uniform(4, 20)


@prop("pinos", "L")
def p_pinos(sc, L, nums, flags, kw):
    y, n = _n(nums, 0, 1250), int(_n(nums, 1, 14))
    rr = random.Random(int(y) + n)
    oscuro_ = sc.hora in ("noche", "tormenta", "aurora", "niebla")
    for capa in range(3):
        col = ((40, 54, 50), (28, 40, 36), (18, 26, 24))[capa] if oscuro_ else ((70, 100, 80), (50, 80, 60),
                                                                                (36, 60, 44))[capa]
        if "nevados" in flags:
            col = claro(col, 0.35)
        for _ in range(max(2, n - capa * 3)):
            x, h = rr.uniform(-60, W + 60), rr.uniform(300, 520) * (1 + capa * 0.3)
            yy = y + capa * 90
            L.forma([(x - h * 0.2, yy), (x, yy - h), (x + h * 0.2, yy)], col, suave=False, intensidad=0.08,
                    textura=0.05, ancho=3)


@prop("selva", "L", sonido=[("insectos", 0, 0)])
def p_selva(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1350)
    rr = random.Random(int(y) + 3)
    oscura = sc.hora in ("noche", "tormenta", "niebla")
    for capa in range(3):
        col = oscuro((60, 120, 70), 0.85 - capa * 0.15) if not oscura else oscuro((30, 60, 40), 0.9 - capa * 0.2)
        for _ in range(9):
            x, yy = rr.uniform(-100, W + 100), rr.uniform(y - 700 + capa * 200, y - 300 + capa * 200)
            L.forma(elipse(x, yy, rr.uniform(150, 250), rr.uniform(100, 170)), col, intensidad=0.08, ancho=3)
        for _ in range(3):
            x = rr.uniform(0, W)
            L.forma([(x - 18, y + 200), (x - 12, y - 600 + capa * 200), (x + 12, y - 600 + capa * 200), (x + 18, y + 200)],
                    oscuro((90, 64, 44), 0.7), suave=False, intensidad=0.06)


@prop("interior", "L")
def p_interior(sc, L, nums, flags, kw):
    """Habitación: pared=madera|piedra|tapiz|metal|ladrillo|yeso ; piso a la altura y."""
    y = _n(nums, 0, 1450)
    pared = kw.get("pared", "madera")
    cols = {"madera": (96, 66, 44), "piedra": (110, 104, 96), "tapiz": (110, 60, 56), "metal": (70, 76, 84),
            "ladrillo": (120, 66, 50), "yeso": (176, 168, 150), "ambar": (200, 130, 40), "oscura": (40, 36, 40)}
    c = cols.get(pared, (96, 66, 44))
    if sc.hora in ("noche", "tormenta"):
        c = oscuro(c, 0.7)
    sc.hora = sc.hora if sc.hora != "noche" else "noche"
    L.forma([(0, 0), (W, 0), (W, y), (0, y)], c, suave=False, borde=False, textura=0.2, intensidad=0.02)
    if pared == "madera":
        for x in range(0, W, 90):
            L.linea([(x, 0), (x, y)], oscuro(c, 0.8), 4)
    elif pared in ("piedra", "ladrillo"):
        for yy in range(0, int(y), 60):
            for xx in range(0, W, 120):
                L.linea([(xx + (yy // 60 % 2) * 60, yy), (xx + (yy // 60 % 2) * 60, yy + 60)], oscuro(c, 0.75), 3)
            L.linea([(0, yy), (W, yy)], oscuro(c, 0.75), 3)
    elif pared == "tapiz":
        for x in range(30, W, 120):
            for yy in range(40, int(y), 140):
                L.forma(elipse(x, yy, 18, 26), claro(c, 0.15), borde=False, sombra=False, brillo=False, textura=0)
    piso = SUELOS.get(kw.get("piso", "madera"), SUELOS["madera"])
    L.forma([(0, y), (W, y), (W, H), (0, H)], oscuro(piso, 0.8), suave=False, borde=False, textura=0.18)
    for x in range(-400, W + 400, 140):
        L.linea([(540 + (x - 540) * 0.3, y), (x, H)], oscuro(piso, 0.65), 3)


@prop("ventana", "L")
def p_ventana(sc, L, nums, flags, kw):
    x, y, w, h = _n(nums, 0, 700), _n(nums, 1, 500), _n(nums, 2, 260), _n(nums, 3, 340)
    vista = kw.get("vista", "noche")
    cols = {"noche": (20, 30, 56), "tormenta": (40, 44, 56), "dia": (150, 196, 230), "mar": (60, 90, 120),
            "nieve": (200, 210, 226), "niebla": (160, 166, 172)}
    L.forma([(x - 14, y - 14), (x + w + 14, y - 14), (x + w + 14, y + h + 14), (x - 14, y + h + 14)], (60, 44, 32),
            suave=False)
    L.forma([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], cols.get(vista, (20, 30, 56)), suave=False, borde=False,
            sombra=False, brillo=False, textura=0)
    if vista == "mar":
        L.forma([(x, y + h * 0.55), (x + w, y + h * 0.55), (x + w, y + h), (x, y + h)], (30, 50, 70), suave=False,
                borde=False, sombra=False, brillo=False, textura=0)
    L.linea([(x + w / 2, y), (x + w / 2, y + h)], (60, 44, 32), 8)
    L.linea([(x, y + h / 2), (x + w, y + h / 2)], (60, 44, 32), 8)


@prop("estante", "L")
def p_estante(sc, L, nums, flags, kw):
    x, y, w, h = _n(nums, 0, 80), _n(nums, 1, 300), _n(nums, 2, 380), _n(nums, 3, 900)
    rr = random.Random(int(x + y))
    L.forma([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], (70, 46, 30), suave=False, intensidad=0.06)
    for k in range(5):
        yy = y + 40 + k * (h - 60) / 5
        L.linea([(x + 10, yy + (h - 60) / 5 - 10), (x + w - 10, yy + (h - 60) / 5 - 10)], (50, 32, 20), 10)
        xx = x + 18
        while xx < x + w - 30:
            if "rollos" in flags:
                r_ = rr.uniform(16, 24)
                L.forma(elipse(xx + r_, yy + (h - 60) / 5 - 12 - r_, r_, r_), (220, 200, 160), intensidad=0.2, ancho=2)
                xx += r_ * 2 + 4
            else:
                bw = rr.uniform(14, 30)
                bh = rr.uniform(0.6, 0.9) * ((h - 60) / 5 - 20)
                L.forma([(xx, yy + (h - 60) / 5 - 12), (xx + bw, yy + (h - 60) / 5 - 12),
                         (xx + bw, yy + (h - 60) / 5 - 12 - bh), (xx, yy + (h - 60) / 5 - 12 - bh)],
                        rr.choice([(120, 40, 40), (40, 70, 110), (60, 90, 50), (140, 110, 60)]), suave=False,
                        intensidad=0.1, ancho=2)
                xx += bw + 2


# =========================================================================== #
# LUGARES Y CONSTRUCCIONES
# =========================================================================== #
@prop("palmera", "L")
def p_palmera(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 200), _n(nums, 1, 1300), _n(nums, 2, 1.0)
    tronco = (110, 80, 54) if sc.hora not in ("noche", "tormenta") else (40, 32, 28)
    hoja = (50, 120, 60) if sc.hora not in ("noche", "tormenta") else (20, 40, 28)
    L.linea(catmull([(x, y), (x + 30 * s, y - 250 * s), (x + 80 * s, y - 480 * s)], 6, cerrado=False), tronco, 22 * s)
    cx, cy = x + 80 * s, y - 480 * s
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.5
        L.forma(catmull([(cx, cy), (cx + math.cos(a - 0.2) * 120 * s, cy + math.sin(a - 0.2) * 80 * s),
                         (cx + math.cos(a) * 240 * s, cy + math.sin(a) * 120 * s + 60 * s),
                         (cx + math.cos(a + 0.2) * 120 * s, cy + math.sin(a + 0.2) * 80 * s)], 4), hoja,
                intensidad=0.1, ancho=2)


@prop("cactus", "L")
def p_cactus(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 200), _n(nums, 1, 1500), _n(nums, 2, 1.0)
    verde = (70, 110, 70) if sc.hora != "noche" else (30, 44, 40)
    L.forma(catmull([(x - 24 * s, y), (x - 24 * s, y - 320 * s), (x, y - 350 * s), (x + 24 * s, y - 320 * s),
                     (x + 24 * s, y)], 3), verde, intensidad=0.18, textura=0.08)
    for lado in (-1, 1):
        L.forma(catmull([(x + lado * 20 * s, y - 150 * s), (x + lado * 80 * s, y - 160 * s),
                         (x + lado * 85 * s, y - 250 * s), (x + lado * 60 * s, y - 250 * s),
                         (x + lado * 58 * s, y - 190 * s), (x + lado * 20 * s, y - 185 * s)], 3), verde, intensidad=0.15)


@prop("arboles_caidos", "L")
def p_caidos(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1500)
    rr = random.Random(7)
    for k in range(26):
        x, yy = rr.uniform(-60, W + 60), y + rr.uniform(0, 380)
        L.linea([(x, yy), (x + 200, yy - 50)], (54, 38, 30), 14)
    for k in range(6):
        x = rr.uniform(0, W)
        L.linea([(x, y + 60), (x + 8, y - 200)], (40, 30, 26), 16)


@prop("casa", "img")
def p_casa(sc, img, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1500), _n(nums, 2, 1.0)
    c = R.casa("fuego" in flags)
    c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
    if sc.hora in ("noche", "tormenta") and "fuego" not in flags:
        osc = Image.new("RGBA", c.size, (14, 18, 30, 255))
        osc.putalpha(c.getchannel("A"))
        c = Image.blend(c, osc, 0.45)
    img.alpha_composite(c, (int(x - c.width / 2), int(y - c.height)))
    if "nieve" in flags:
        d = ImageDraw.Draw(img)
        d.polygon([(x - 190 * s, y - 410 * s), (x, y - 700 * s + 30), (x + 190 * s, y - 410 * s)], fill=None)


@prop("granero", "L")
def p_granero(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 760), _n(nums, 1, 1400), _n(nums, 2, 1.0)
    rojo = (150, 46, 36) if sc.hora not in ("noche",) else (60, 26, 26)
    L.forma([(x - 200 * s, y), (x - 200 * s, y - 260 * s), (x, y - 400 * s), (x + 200 * s, y - 260 * s), (x + 200 * s, y)],
            rojo, suave=False, intensidad=0.1, textura=0.14)
    L.forma([(x - 70 * s, y), (x - 70 * s, y - 170 * s), (x + 70 * s, y - 170 * s), (x + 70 * s, y)], oscuro(rojo, 0.6),
            suave=False)
    L.linea([(x - 70 * s, y - 170 * s), (x + 70 * s, y)], (230, 220, 200), 6 * s)
    L.linea([(x + 70 * s, y - 170 * s), (x - 70 * s, y)], (230, 220, 200), 6 * s)


@prop("cerca", "L")
def p_cerca(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1560)
    col = (120, 96, 70) if sc.hora not in ("noche",) else (50, 40, 34)
    for x in range(0, W + 1, 110):
        L.linea([(x, y), (x, y - 110)], col, 10)
    for dy in (-90, -45):
        L.linea([(0, y + dy), (W, y + dy)], col, 8)


@prop("iglesia", "L")
def p_iglesia(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 300), _n(nums, 1, 1300), _n(nums, 2, 1.0)
    col = (150, 140, 126) if sc.hora not in ("noche",) else (60, 58, 64)
    L.forma([(x - 160 * s, y), (x - 160 * s, y - 220 * s), (x + 160 * s, y - 220 * s), (x + 160 * s, y)], col, suave=False,
            intensidad=0.1, textura=0.16)
    L.forma([(x - 180 * s, y - 220 * s), (x, y - 330 * s), (x + 180 * s, y - 220 * s)], oscuro(col, 0.7), suave=False)
    L.forma([(x + 60 * s, y - 220 * s), (x + 60 * s, y - 520 * s), (x + 140 * s, y - 520 * s), (x + 140 * s, y - 220 * s)],
            col, suave=False, intensidad=0.1)
    L.forma([(x + 50 * s, y - 520 * s), (x + 100 * s, y - 640 * s), (x + 150 * s, y - 520 * s)], oscuro(col, 0.7),
            suave=False)


@prop("torre", "L")
def p_torre(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1300), _n(nums, 2, 1.0)
    col = (196, 184, 160) if sc.hora not in ("noche", "tormenta") else (90, 86, 84)
    L.forma([(x - 220 * s, y), (x - 220 * s, y - 560 * s), (x + 220 * s, y - 560 * s), (x + 220 * s, y)], col,
            suave=False, intensidad=0.1, textura=0.2)
    for dx in (-250, 170):
        L.forma([(x + dx * s, y - 560 * s), (x + (dx + 80) * s, y - 560 * s), (x + (dx + 80) * s, y - 760 * s),
                 (x + dx * s, y - 760 * s)], col, suave=False, intensidad=0.12, textura=0.18)
        L.forma([(x + (dx - 6) * s, y - 760 * s), (x + (dx + 40) * s, y - 840 * s), (x + (dx + 86) * s, y - 760 * s)],
                (60, 70, 80), suave=False)
    for k in range(8):
        L.forma([(x + (-220 + k * 58) * s, y - 560 * s), (x + (-190 + k * 58) * s, y - 560 * s),
                 (x + (-190 + k * 58) * s, y - 600 * s), (x + (-220 + k * 58) * s, y - 600 * s)], col, suave=False)
    for dx, dy in ((-110, -420), (60, -420), (-110, -230), (60, -230)):
        L.forma([(x + dx * s, y + dy * s), (x + (dx + 50) * s, y + dy * s), (x + (dx + 50) * s, y + (dy + 100) * s),
                 (x + dx * s, y + (dy + 100) * s)], (30, 26, 24), suave=False, borde=False)


@prop("faro", "dyn", sonido=[("sirena_niebla", 0.6, 2.5)])
def p_faro(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 600), _n(nums, 1, 1080), _n(nums, 2, 1.0)
    Lz = LienzoReal(W, H, 0, 0)
    torre = Lz.forma([(x - 80 * s, y), (x - 40 * s, y - 540 * s), (x + 40 * s, y - 540 * s), (x + 80 * s, y)],
                     (226, 222, 214), suave=False, intensidad=0.1)
    if "espiral" in flags:
        for k in range(-4, 7):
            yy = y - 500 * s + k * 130 * s
            Lz.forma([(x - 140 * s, yy), (x + 140 * s, yy - 120 * s), (x + 140 * s, yy - 50 * s), (x - 140 * s, yy + 70 * s)],
                     (30, 30, 34), suave=False, borde=False, clip=torre, sombra=False)
    elif "rojo" in flags:
        for k in range(3):
            yy = y - 160 * s - k * 140 * s
            Lz.forma([(x - 70 * s, yy), (x + 70 * s, yy), (x + 68 * s, yy - 40 * s), (x - 68 * s, yy - 40 * s)],
                     (170, 40, 40), suave=False, borde=False, clip=torre)
    Lz.forma([(x - 60 * s, y - 540 * s), (x + 60 * s, y - 540 * s), (x + 50 * s, y - 620 * s), (x - 50 * s, y - 620 * s)],
             (40, 40, 46), suave=False)
    Lz.forma([(x - 70 * s, y - 620 * s), (x, y - 680 * s), (x + 70 * s, y - 620 * s)], (60, 60, 66), suave=False)
    spr = Lz.final()
    apagado = "apagado" in flags
    def f(img, t, dur):
        img.alpha_composite(spr)
        if apagado:
            return
        ang = math.pi + 1.3 * math.sin(t * 0.8)
        cx, cy = x, y - 580 * s
        capa = Image.new("L", (W // 4, H // 4), 0)
        ImageDraw.Draw(capa).polygon([(cx / 4, cy / 4), ((cx + 1500 * math.cos(ang - 0.09)) / 4,
                                                          (cy + 300 * math.sin(ang - 0.09)) / 4),
                                      ((cx + 1500 * math.cos(ang + 0.09)) / 4, (cy + 300 * math.sin(ang + 0.09)) / 4)],
                                     fill=120)
        luz = Image.new("RGBA", (W, H), (255, 246, 210, 0))
        luz.putalpha(capa.filter(ImageFilter.GaussianBlur(4)).resize((W, H)))
        img.alpha_composite(luz)
        pegar_glow(img, cx, cy, 70 * s, "#fff6d0", 0.9)
    return f


@prop("islote", "L")
def p_islote(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1160), _n(nums, 2, 1.0)
    col = (70, 66, 60) if "roca" in flags else (214, 196, 150)
    if sc.hora in ("noche", "tormenta"):
        col = oscuro(col, 0.5)
    alto = 220 if "roca" in flags else 50
    L.forma(catmull([(x - 320 * s, y + 10), (x - 200 * s, y - alto * s), (x + 150 * s, y - alto * 1.1 * s),
                     (x + 330 * s, y + 10)], 4), col, intensidad=0.12, textura=0.14)


@prop("piramide", "L")
def p_piramide(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1260), _n(nums, 2, 1.0)
    piedra = (190, 160, 120) if sc.hora not in ("noche",) else (90, 80, 84)
    if "escalonada" in flags:
        for k in range(6):
            w, yy = (860 - k * 120) * s, y - k * 95 * s
            L.forma([(x - w / 2, yy), (x + w / 2, yy), (x + w / 2 - 30 * s, yy - 95 * s), (x - w / 2 + 30 * s, yy - 95 * s)],
                    oscuro(piedra, 1 - k * 0.03), suave=False, intensidad=0.1, textura=0.16)
        L.forma([(x - 50 * s, y), (x + 50 * s, y), (x + 30 * s, y - 570 * s), (x - 30 * s, y - 570 * s)],
                claro(piedra, 0.1), suave=False)
        L.forma([(x - 80 * s, y - 570 * s), (x + 80 * s, y - 570 * s), (x + 70 * s, y - 680 * s), (x - 70 * s, y - 680 * s)],
                oscuro(piedra, 0.9), suave=False)
    else:
        L.forma([(x - 450 * s, y), (x, y - 620 * s), (x + 450 * s, y)], piedra, suave=False, intensidad=0.12, textura=0.1)
        for k in range(1, 8):
            f = k / 8
            L.linea([(x - 450 * s * (1 - f), y - 620 * s * f), (x + 450 * s * (1 - f), y - 620 * s * f)],
                    oscuro(piedra, 0.8), 3)


@prop("templo_egipcio", "L")
def p_templo(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1320), _n(nums, 2, 1.0)
    piedra = (206, 176, 130) if sc.hora not in ("noche",) else (96, 84, 80)
    for dx in (-1, 1):
        L.forma([(x + dx * 120 * s, y), (x + dx * 420 * s, y), (x + dx * 390 * s, y - 520 * s), (x + dx * 130 * s, y - 520 * s)],
                piedra, suave=False, intensidad=0.12, textura=0.2)
        for k in range(4):
            L.linea([(x + dx * 160 * s, y - 120 * s - k * 90 * s), (x + dx * 380 * s, y - 120 * s - k * 90 * s)],
                    oscuro(piedra, 0.75), 3)
    L.forma([(x - 120 * s, y), (x + 120 * s, y), (x + 120 * s, y - 380 * s), (x - 120 * s, y - 380 * s)],
            (40, 30, 24), suave=False, borde=False)
    L.forma([(x - 140 * s, y - 380 * s), (x + 140 * s, y - 380 * s), (x + 140 * s, y - 430 * s), (x - 140 * s, y - 430 * s)],
            piedra, suave=False)


@prop("columnas", "L")
def p_columnas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1300)
    piedra = _col(kw, (200, 190, 170) if sc.hora not in ("noche",) else (96, 92, 96))
    rr = random.Random(int(y))
    for k in range(5):
        x = 150 + k * 195
        h = rr.choice((640, 560, 420, 300)) if "rotas" in flags else 640
        L.forma([(x - 48, y), (x - 44, y - h), (x + 44, y - h), (x + 48, y)], piedra, suave=False, intensidad=0.16,
                textura=0.14)
        for fx in (-24, 0, 24):
            L.linea([(x + fx, y - 5), (x + fx * 0.95, y - h + 10)], oscuro(piedra, 0.78), 4)
        L.forma([(x - 70, y - h), (x + 70, y - h), (x + 60, y - h - 40), (x - 60, y - h - 40)], claro(piedra, 0.08),
                suave=False)
    if "techo" in flags:
        L.forma([(60, y - 680), (1020, y - 680), (1020, y - 760), (60, y - 760)], piedra, suave=False, intensidad=0.1)


@prop("moai", "L")
def p_moai(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1300), _n(nums, 2, 1.0)
    piedra = (96, 86, 80) if sc.hora not in ("noche",) else (50, 46, 46)
    hh = 560
    L.forma([(x - 75 * s, y), (x - 85 * s, y - hh * 0.55 * s), (x - 65 * s, y - hh * s), (x + 65 * s, y - hh * s),
             (x + 85 * s, y - hh * 0.55 * s), (x + 75 * s, y)], piedra, suave=False, intensidad=0.16, textura=0.22)
    L.forma([(x - 70 * s, y - (hh - 40) * s), (x + 70 * s, y - (hh - 40) * s), (x + 66 * s, y - (hh - 100) * s),
             (x - 66 * s, y - (hh - 100) * s)], oscuro(piedra, 0.7), suave=False, borde=False)
    L.forma([(x - 14 * s, y - (hh - 100) * s), (x + 14 * s, y - (hh - 100) * s), (x + 22 * s, y - hh * 0.62 * s),
             (x - 22 * s, y - hh * 0.62 * s)], claro(piedra, 0.1), suave=False)
    L.linea([(x - 40 * s, y - hh * 0.5 * s), (x + 40 * s, y - hh * 0.5 * s)], oscuro(piedra, 0.6), 6 * s)


@prop("olmeca", "L")
def p_olmeca(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1300), _n(nums, 2, 1.0)
    c = (120, 110, 96)
    P = lambda a, b: (x + a * s, y + b * s)
    L.forma(catmull([P(-210, 0), P(-230, -380), P(-160, -580), P(0, -630), P(160, -580), P(230, -380), P(210, 0)], 3),
            c, intensidad=0.16, textura=0.2)
    L.forma(catmull([P(-220, -420), P(-180, -580), P(0, -640), P(180, -580), P(220, -420), P(0, -480)], 3),
            oscuro(c, 0.88), intensidad=0.12, textura=0.2)
    for dx in (-100, 100):
        L.forma(elipse(x + dx * s, y - 330 * s, 50 * s, 22 * s), oscuro(c, 0.65), intensidad=0.2)
    L.forma(elipse(x, y - 230 * s, 60 * s, 45 * s), oscuro(c, 0.92), intensidad=0.2)
    L.forma(elipse(x, y - 120 * s, 110 * s, 36 * s), oscuro(c, 0.72), intensidad=0.2)


@prop("esferas", "L")
def p_esferas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1500)
    c = (150, 140, 126)
    for x, r in ((260, 120), (640, 200), (930, 90)):
        L.forma(elipse(x, y - r, r, r), c, intensidad=0.25, textura=0.12)


@prop("tpilares", "L")
def p_tpilares(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1350)
    piedra = (186, 160, 124)
    for k in range(5):
        x = 140 + k * 200
        L.forma([(x - 34, y), (x - 34, y - 380), (x + 34, y - 380), (x + 34, y)], piedra, suave=False, intensidad=0.14,
                textura=0.18)
        L.forma([(x - 90, y - 380), (x + 90, y - 380), (x + 90, y - 460), (x - 90, y - 460)], piedra, suave=False,
                intensidad=0.14, textura=0.18)
        # zorro / jabalí / ave tallados
        L.linea(catmull([(x - 22, y - 220), (x, y - 250), (x + 22, y - 220), (x + 10, y - 190), (x - 10, y - 190)], 4),
                oscuro(piedra, 0.6), 4)


@prop("stonehenge", "L")
def p_stonehenge(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1350)
    piedra = (150, 146, 136) if sc.hora not in ("noche",) else (70, 70, 76)
    for k in range(6):
        x = 120 + k * 170
        hh = 360 if k % 2 == 0 else 330
        L.forma([(x - 46, y), (x - 40, y - hh), (x + 40, y - hh), (x + 46, y)], piedra, suave=False, intensidad=0.14,
                textura=0.2)
    for k in range(0, 6, 2):
        x = 120 + k * 170
        L.forma([(x - 50, y - 360), (x + 220, y - 365), (x + 220, y - 410), (x - 50, y - 405)], piedra, suave=False,
                intensidad=0.12, textura=0.2)


@prop("yurtas", "L")
def p_yurtas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1350)
    for x, s in ((260, 1.0), (760, 0.7)):
        L.forma([(x - 150 * s, y), (x - 150 * s, y - 100 * s), (x + 150 * s, y - 100 * s), (x + 150 * s, y)],
                (236, 230, 214), suave=False, intensidad=0.1)
        L.forma([(x - 170 * s, y - 100 * s), (x, y - 190 * s), (x + 170 * s, y - 100 * s)], (210, 200, 180), suave=False)
        L.forma([(x - 30 * s, y), (x + 30 * s, y), (x + 30 * s, y - 80 * s), (x - 30 * s, y - 80 * s)], (160, 50, 40),
                suave=False)


@prop("nazca", "L")
def p_nazca(sc, L, nums, flags, kw):
    figura_ = kw.get("figura", "colibri")
    L.d.rectangle((0, 0, W * 2, H * 2), fill=(200, 160, 120))
    rr = random.Random(3)
    for _ in range(80):
        L.circulo(rr.uniform(0, W), rr.uniform(0, H), rr.uniform(3, 9), (176, 136, 100), borde=False)
    linea = (244, 224, 194)
    if figura_ == "colibri":
        cuerpo = [(540, 420), (560, 600), (600, 900), (590, 1200), (540, 1500), (490, 1200), (480, 900), (520, 600)]
        L.linea(catmull(cuerpo, 6), linea, 10)
        L.linea([(540, 420), (540, 200)], linea, 10)
        for lado in (-1, 1):
            L.linea([(540 + lado * 40, 820)] + [(540 + lado * (120 + k * 70), 820 - k * 80 + (k % 2) * 60)
                                                for k in range(6)] + [(540 + lado * 60, 1000)], linea, 10)
    elif figura_ == "mono":
        L.linea(catmull([(380, 700), (460, 560), (600, 560), (680, 700), (640, 900), (440, 900)], 6), linea, 10)
        L.linea(catmull([(640, 900), (760, 1100), (720, 1300), (600, 1300), (620, 1180), (700, 1160)], 6,
                        cerrado=False), linea, 10)
        for dx in (-120, 120):
            L.linea([(540 + dx * 0.5, 800), (540 + dx * 2, 640), (540 + dx * 2.4, 560)], linea, 10)
    else:  # araña
        L.linea(catmull([(470, 800), (610, 800), (640, 980), (540, 1060), (440, 980)], 6), linea, 10)
        for k in range(4):
            for lado in (-1, 1):
                L.linea([(540 + lado * 80, 860 + k * 50), (540 + lado * 260, 760 + k * 120),
                         (540 + lado * 330, 900 + k * 140)], linea, 8)
    for k in range(5):
        L.linea([(rr.uniform(0, W), rr.uniform(0, H)), (rr.uniform(0, W), rr.uniform(0, H))], linea, 5)


@prop("carpa", "img")
def p_carpa(sc, img, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1560), _n(nums, 2, 1.0)
    c = R.carpa_rota()
    c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
    img.alpha_composite(c, (int(x - c.width / 2), int(y - c.height)))


@prop("fogata", "dyn", sonido=[("fuego", 0, 0)])
def p_fogata(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1600)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        for k in range(5):
            d.line((x - 60 + k * 30, y, x - 30 + k * 15, y - 30), fill=(70, 46, 30), width=12)
        for k in range(6):
            fz = (t * 2 + k / 6) % 1
            pegar_glow(img, x + 20 * math.sin(t * 5 + k), y - 30 - 120 * fz, 50 * (1 - fz) + 10, "#ff9a30", 0.9 * (1 - fz))
        pegar_glow(img, x, y - 40, 300, "#ff8030", 0.35 + 0.1 * math.sin(t * 9))
    return f


@prop("cartel_ruta", "L")
def p_cartel_ruta(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1450)
    txt = kw.get("txt", "")
    L.linea([(x - 200, y), (x - 200, y - 380)], (80, 60, 40), 18)
    L.linea([(x + 200, y), (x + 200, y - 380)], (80, 60, 40), 18)
    L.forma([(x - 300, y - 600), (x + 300, y - 600), (x + 300, y - 340), (x - 300, y - 340)], (236, 226, 200),
            suave=False, intensidad=0.08, textura=0.12)
    sc.ctx.setdefault("_textos", []).append((x, y - 470, txt))


@prop("textos", "img")
def p_textos(sc, img, nums, flags, kw):
    d = ImageDraw.Draw(img)
    for x, y, txt in sc.ctx.pop("_textos", []):
        f = pro.fuente(46)
        while d.textlength(txt, font=f) > 560 and f.size > 24:
            f = pro.fuente(f.size - 4)
        d.text((x, y), txt, font=f, fill=(150, 20, 20), anchor="mm")


@prop("farol", "dyn")
def p_farol(sc, nums, flags, kw):
    x, y = _n(nums, 0, 360), _n(nums, 1, 1500)
    gas = "gas" in flags
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.line((x, y, x, y - 640), fill=(30, 30, 34), width=12)
        d.polygon([(x - 34, y - 640), (x + 34, y - 640), (x + 24, y - 710), (x - 24, y - 710)], fill=(60, 56, 40))
        pegar_glow(img, x, y - 675, 170 * (1 + (0.06 * math.sin(t * 13) if gas else 0)), "#ffb860" if gas else "#fff0c0",
                   0.85)
    return f


@prop("radiotelescopio", "L")
def p_radiotelescopio(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1400), _n(nums, 2, 1.0)
    if "bigear" in flags:  # el «Big Ear»: reflector plano gigante en el campo
        L.forma([(x - 500 * s, y), (x + 500 * s, y - 20 * s), (x + 500 * s, y + 40 * s), (x - 500 * s, y + 70 * s)],
                (180, 190, 200), suave=False, intensidad=0.1)
        L.forma([(x - 480 * s, y - 20), (x - 440 * s, y - 360 * s), (x - 400 * s, y - 360 * s), (x - 400 * s, y - 20)],
                (160, 170, 184), suave=False, intensidad=0.1)
        L.forma([(x + 300 * s, y - 10), (x + 360 * s, y - 300 * s), (x + 480 * s, y - 300 * s), (x + 480 * s, y - 10)],
                (150, 160, 176), suave=False, intensidad=0.1)
        for k in range(10):
            L.linea([(x - 440 * s + k * 90 * s, y - 360 * s), (x - 440 * s + k * 90 * s, y)], (120, 130, 144), 3)
        return
    L.forma(elipse(x, y - 300 * s, 320 * s, 140 * s, -0.3), (200, 206, 216), intensidad=0.15)
    L.forma([(x - 20 * s, y - 220 * s), (x + 20 * s, y - 220 * s), (x + 70 * s, y), (x - 70 * s, y)], (150, 156, 166),
            suave=False)
    L.linea([(x, y - 300 * s), (x + 150 * s, y - 520 * s)], (170, 176, 186), 10 * s)


@prop("estacion", "L")
def p_estacion(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 780), _n(nums, 1, 1450)
    L.forma([(x - 120, y), (x - 120, y - 200), (x + 120, y - 200), (x + 120, y)], (200, 196, 186), suave=False,
            intensidad=0.1)
    L.forma([(x - 140, y - 200), (x, y - 260), (x + 140, y - 200)], (120, 40, 40), suave=False)
    L.linea([(x + 60, y - 260), (x + 60, y - 420)], (120, 120, 126), 8)
    L.forma([(x + 30, y - 440), (x + 110, y - 440), (x + 110, y - 400), (x + 30, y - 400)], (50, 50, 56), suave=False)
    L.forma([(x - 60, y - 130), (x - 10, y - 130), (x - 10, y - 80), (x - 60, y - 80)], (250, 220, 140), suave=False,
            borde=False)


@prop("piscina", "L")
def p_piscina(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1350)
    L.forma([(0, y - 40), (W, y - 40), (W, H), (0, H)], (226, 222, 210), suave=False, borde=False, textura=0.1)
    L.forma([(80, y), (1000, y), (1050, y + 420), (30, y + 420)], (60, 170, 210), suave=False, intensidad=0.06)
    for k in range(1, 6):
        L.linea([(80 + k * 153, y), (30 + k * 170, y + 420)], (240, 240, 240), 4)


@prop("restaurante", "L")
def p_restaurante(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1350)
    L.forma([(x - 380, y), (x - 380, y - 300), (x + 380, y - 300), (x + 380, y)], (120, 70, 50), suave=False,
            intensidad=0.08, textura=0.14)
    L.forma([(x - 400, y - 300), (x + 400, y - 300), (x + 400, y - 360), (x - 400, y - 360)], (60, 40, 34), suave=False)
    for k in range(5):
        L.forma([(x - 320 + k * 140, y - 230), (x - 240 + k * 140, y - 230), (x - 240 + k * 140, y - 120),
                 (x - 320 + k * 140, y - 120)], (250, 210, 130), suave=False, borde=False)
    L.forma([(x - 160, y - 460), (x + 160, y - 460), (x + 160, y - 380), (x - 160, y - 380)], (170, 30, 30), suave=False)
    L.forma([(0, y), (W, y), (W, H), (0, H)], (60, 60, 66), suave=False, borde=False, textura=0.12)
    for k in range(6):
        L.linea([(k * 200 + 40, y + 120), (k * 200 + 40, y + 300)], (230, 220, 140), 6)


@prop("pozo", "dyn", sonido=[("goteo", 0, 0)])
def p_pozo(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1250)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.ellipse((x - 260, y - 70, x + 260, y + 70), fill=(20, 16, 12), outline=(80, 60, 40), width=10)
        for k in range(6):  # tablones de madera del pozo
            yy = y + 120 + k * 90
            d.rectangle((x - 230 + k * 8, yy, x + 230 - k * 8, yy + 26), fill=(90, 64, 40))
        d.rectangle((x - 230, y, x - 200, y + 640), fill=(70, 50, 32))
        d.rectangle((x + 200, y, x + 230, y + 640), fill=(70, 50, 32))
        if "agua" in flags:
            nivel = y + 600 - min(1.0, t / max(dur, 0.1)) * 420
            d.rectangle((x - 200, nivel, x + 200, y + 640), fill=(40, 70, 90))
            for k in range(3):
                d.line([(xx, nivel + 6 * math.sin(xx * 0.05 + t * 4 + k)) for xx in range(int(x - 200), int(x + 200), 10)],
                       fill=(150, 190, 210), width=3)
    return f


@prop("cofre", "img")
def p_cofre(sc, img, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1450), _n(nums, 2, 1.0)
    d = ImageDraw.Draw(img)
    d.rectangle((x - 180 * s, y - 160 * s, x + 180 * s, y), fill=(110, 70, 34), outline=(50, 30, 16), width=6)
    d.rectangle((x - 180 * s, y - 100 * s, x + 180 * s, y - 80 * s), fill=(200, 160, 60))
    if "abierto" in flags:
        d.polygon([(x - 180 * s, y - 160 * s), (x + 180 * s, y - 160 * s), (x + 160 * s, y - 300 * s),
                   (x - 160 * s, y - 300 * s)], fill=(96, 60, 30), outline=(50, 30, 16))
        for k in range(14):
            d.ellipse((x - 150 * s + k * 21 * s, y - 190 * s - (k % 3) * 10 * s, x - 120 * s + k * 21 * s,
                       y - 160 * s - (k % 3) * 10 * s), fill=(240, 196, 70), outline=(150, 110, 30))
        pegar_glow(img, x, y - 180 * s, 260 * s, "#ffcf50", 0.6)


@prop("relieve", "L")
def p_relieve(sc, L, nums, flags, kw):
    """Muro de piedra egipcio con barcos y guerreros tallados (Medinet Habu)."""
    piedra = (206, 180, 140)
    L.forma([(40, 300), (1040, 300), (1040, 1450), (40, 1450)], piedra, suave=False, intensidad=0.06, textura=0.3)
    t = oscuro(piedra, 0.6)
    for fila in range(3):
        y = 520 + fila * 330
        L.linea(catmull([(120, y), (200, y + 60), (500, y + 70), (620, y), (560, y - 40)], 5, cerrado=False), t, 6)
        L.linea([(360, y + 40), (360, y - 160)], t, 5)
        L.forma([(300, y - 150), (420, y - 150), (420, y - 60), (300, y - 60)], claro(piedra, 0.05), suave=False, ancho=3)
        for k in range(4):
            x = 720 + k * 70
            L.circulo(x, y - 110, 18, piedra, ancho=3)
            L.linea([(x, y - 90), (x, y - 10), (x - 20, y + 40)], t, 5)
            L.linea([(x, y - 70), (x + 30, y - 50)], t, 4)
            L.linea([(x - 26, y - 128), (x + 26, y - 128)], t, 4)  # tocado de plumas


@prop("muelle", "L")
def p_muelle(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1500)
    for k in range(7):
        L.forma([(0, y - k * 0), (W, y - 20), (W, y + 40), (0, y + 60)], (110, 80, 54), suave=False, intensidad=0.06) \
            if k == 0 else None
    for x in range(40, W, 160):
        L.linea([(x, y + 50), (x, H)], (70, 50, 34), 18)


# =========================================================================== #
# VEHÍCULOS (animados)
# =========================================================================== #
def _escalar(im, s):
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def _oscurecer(im, k, col=(14, 18, 30)):
    if k <= 0:
        return im
    osc = Image.new("RGBA", im.size, col + (255,))
    osc.putalpha(im.getchannel("A"))
    return Image.blend(im, osc, k)


def _luz_hora(sc):
    return {"noche": 0.45, "tormenta": 0.5, "niebla": 0.3, "atardecer": 0.25, "aurora": 0.45}.get(sc.hora, 0.0)


@prop("avion", "dyn", sonido=lambda f, kw: [("jet" if kw.get("modelo") in ("777", "f18") else "helice", 0, 0),
                                             ("whoosh", 1.5, 0.9)])
def p_avion(sc, nums, flags, kw):
    modelo = kw.get("modelo", "777")
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 900), _n(nums, 2, 0.8)
    n = int(kw.get("n", "1"))
    mov = kw.get("mov", "der")
    spr = _oscurecer(_escalar(R.avion_real(modelo), s * 760 / R.avion_real(modelo).width), _luz_hora(sc))
    izq = mov == "izq"
    if izq:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    form = [(0, 0), (-210, -110), (-210, 110), (-420, -220), (-420, 220)][:n]
    def f(img, t, dur):
        p = t / max(dur, 0.1)
        if mov == "despega":
            xx, yy, ang = x - 300 + 700 * p, y - 380 * max(0.0, p - 0.25) ** 1.4, 8 * min(1.0, max(0.0, p - 0.2) * 3)
        elif mov == "gira":
            xx, yy, ang = x + 200 * math.sin(p * math.pi), y - 60 * math.cos(p * math.pi), -25 * math.sin(p * math.pi * 2)
        elif mov == "cae":
            xx, yy, ang = x + 300 * p, y + 500 * p ** 2, -35 * p
        elif mov == "quieto":
            xx, yy, ang = x, y + 8 * math.sin(t), 2 * math.sin(t * 0.8)
        else:
            sg = -1 if izq else 1
            xx, yy, ang = x + sg * (-250 + 600 * p), y + 10 * math.sin(t * 1.3), 2.5 * math.sin(t * 0.9)
        sg = -1 if izq else 1
        for j, (dx, dy) in enumerate(form):
            im = spr.rotate(ang * (1 if not izq else -1), expand=True, resample=Image.BICUBIC)
            px, py = xx + dx * s * sg, yy + dy * s + 6 * math.sin(t * 1.5 + j)
            img.alpha_composite(im, (int(px - im.width / 2), int(py - im.height / 2)))
            if sc.hora in ("noche", "tormenta", "niebla") and int(t * 2 + j) % 2 == 0:
                pegar_glow(img, px + sg * spr.width * 0.1, py - spr.height * 0.1, 16, "#ff3030", 1.0)
    return f


@prop("hidroavion", "dyn", sonido=[("helice", 0, 0)])
def p_hidroavion(sc, nums, flags, kw):
    """PBM Mariner: hidroavión de alas de gaviota con dos motores y casco de bote."""
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 800), _n(nums, 2, 1.0)
    Lz = LienzoReal(900, 420, 450, 240)
    gris = (90, 104, 122)
    Lz.forma(catmull([(380, -10), (300, -60), (-200, -60), (-400, -100), (-420, -60), (-200, 10), (250, 60), (360, 40)], 4),
             gris, intensidad=0.14)
    Lz.forma(catmull([(-80, -70), (-20, -150), (140, -150), (200, -80)], 4, cerrado=False) + [(200, -60), (-80, -60)],
             oscuro(gris, 0.9), intensidad=0.1)
    for lado, dx in ((-1, -30), (1, 110)):
        Lz.forma(catmull([(dx - 60, -120), (dx + 60, -130), (dx + 60, -90), (dx - 60, -90)], 3), oscuro(gris, 0.8))
        Lz.forma(elipse(dx + 70, -110, 6, 50), (200, 200, 210), borde=False, sombra=False, brillo=False, textura=0)
    Lz.forma([(-410, -100), (-380, -220), (-340, -220), (-340, -90)], gris, suave=False)
    Lz.forma([(-400, -170), (-280, -170), (-280, -150), (-400, -150)], gris, suave=False)
    spr = _oscurecer(_escalar(Lz.final(), s), _luz_hora(sc))
    def f(img, t, dur):
        p = t / max(dur, 0.1)
        img.alpha_composite(spr, (int(x - spr.width / 2 - 200 + 400 * p), int(y - spr.height / 2 + 8 * math.sin(t))))
    return f


@prop("barco", "dyn", sonido=[("crujido", 0.3, 1.6)])
def p_barco(sc, nums, flags, kw):
    modelo = kw.get("modelo", "bergantin")
    x, y, s = _n(nums, 0, 540), _n(nums, 1, sc.horizonte + 35), _n(nums, 2, 0.78)
    sil = (84, 88, 94) if sc.hora == "niebla" else None
    spr = _escalar(R.barco_real(modelo, sil=sil), s)
    spr = _oscurecer(spr, _luz_hora(sc) * 0.7)
    escora = float(kw.get("escora", "0"))
    hundido = "hundido" in flags
    refl = spr.transpose(Image.FLIP_TOP_BOTTOM).resize((spr.width, int(spr.height * 0.45))).filter(
        ImageFilter.GaussianBlur(3))
    refl.putalpha(refl.getchannel("A").point(lambda v: int(v * 0.25)))
    quieto = "quieto" in flags or modelo == "franklin"
    def f(img, t, dur):
        bob = 0 if quieto else 9 * math.sin(t * 1.4)
        deriva = 0 if quieto else t * 10
        b = spr.rotate(escora + (0 if quieto else 2.5 * math.sin(t * 1.1)), resample=Image.BICUBIC)
        base = y + (60 if hundido else 0)
        if not quieto and sc.hora not in ("frio",):
            img.alpha_composite(refl, (int(x - refl.width / 2 + deriva), int(y + bob * 0.5)))
        img.alpha_composite(b, (int(x - b.width / 2 + deriva), int(base - b.height * 0.76 + bob)))
    return f


@prop("bote", "dyn")
def p_bote(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1250), _n(nums, 2, 1.0)
    volcado = "volcado" in flags
    Lz = LienzoReal(520, 260, 260, 180)
    col = _col(kw, (176, 120, 70))
    if volcado:
        Lz.forma(catmull([(-230, 0), (-160, -90), (160, -90), (230, 0)], 4), col, intensidad=0.14, textura=0.12)
    else:
        Lz.forma(catmull([(-240, -60), (-170, 40), (170, 40), (240, -60)], 4, cerrado=False) + [(240, -60), (-240, -60)],
                 col, intensidad=0.14, textura=0.12)
        Lz.linea([(-230, -60), (230, -60)], oscuro(col, 0.6), 8)
        for k in (-80, 80):
            Lz.linea([(k, -60), (k, 10)], oscuro(col, 0.6), 6)
    spr = _oscurecer(_escalar(Lz.final(), s), _luz_hora(sc) * 0.7)
    def f(img, t, dur):
        img.alpha_composite(spr.rotate(4 * math.sin(t * 1.3), resample=Image.BICUBIC),
                            (int(x - spr.width / 2 + t * 6), int(y - spr.height * 0.7 + 8 * math.sin(t * 1.6))))
    return f


@prop("canoa", "dyn")
def p_canoa(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1250), _n(nums, 2, 1.0)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        xx = x + t * 14
        d.polygon([(xx - 300 * s, y), (xx + 300 * s, y), (xx + 260 * s, y + 40 * s), (xx - 260 * s, y + 40 * s)],
                  fill=(80, 50, 30))
        for k in range(5):
            px = xx - 200 * s + k * 100 * s
            d.ellipse((px - 14 * s, y - 70 * s, px + 14 * s, y - 42 * s), fill=(60, 40, 30))
            d.line((px, y - 42 * s, px, y), fill=(60, 40, 30), width=int(14 * s))
            d.line((px, y - 30 * s, px + 50 * s * math.sin(t * 3 + k), y + 50 * s), fill=(90, 60, 30), width=int(6 * s))
    return f


@prop("auto", "img")
def p_auto(sc, img, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1600), _n(nums, 2, 1.0)
    a = _escalar(R.auto(kw.get("era", "1920"), _col(kw, (36, 44, 56))), s)
    if "faros" in flags:
        pegar_glow(img, x + a.width * 0.42, y - a.height * 0.3, 140, "#fff0b0", 0.7)
    img.alpha_composite(_oscurecer(a, _luz_hora(sc) * 0.7), (int(x - a.width / 2), int(y - a.height * 0.83)))


@prop("tren", "dyn", sonido=[("tren", 0, 0)])
def p_tren(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1350), _n(nums, 2, 1.0)
    loco = _oscurecer(_escalar(R.tren(), s), _luz_hora(sc) * 0.6)
    quieto = "quieto" in flags
    tunel = "tunel" in flags
    def f(img, t, dur):
        xx = x if quieto else (x - 300 + t * 110 if not tunel else x + 300 - t * 120)
        im = loco if not tunel else loco.transpose(Image.FLIP_LEFT_RIGHT)
        img.alpha_composite(im, (int(xx - im.width / 2), int(y - im.height * 0.85)))
        cx = xx + (im.width * 0.28 if not tunel else -im.width * 0.28)
        for k in range(6):
            fz = (t * 0.6 + k / 6) % 1
            pegar_glow(img, cx - 60 * fz * 3 * (1 if not tunel else -1), y - im.height * 0.85 - 280 * fz,
                       60 + 120 * fz, "#c8c8cc", 0.5 * (1 - fz))
    return f


@prop("globo", "dyn", sonido=[("viento", 0, 0)])
def p_globo(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 760), _n(nums, 2, 1.0)
    spr = _oscurecer(_escalar(R.avion_real("globo"), s * 0.9), _luz_hora(sc))
    cae = "cae" in flags
    def f(img, t, dur):
        yy = y + (t * 60 if cae else -t * 14) + 10 * math.sin(t)
        img.alpha_composite(spr.rotate(5 * math.sin(t * 0.7) if cae else 0, resample=Image.BICUBIC),
                            (int(x + 40 * math.sin(t * 0.3) - spr.width / 2), int(yy - spr.height / 2)))
    return f


@prop("restos", "L")
def p_restos(sc, L, nums, flags, kw):
    """Restos de avión: fuselaje roto, ala y motor (glaciar o fondo del mar)."""
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1500), _n(nums, 2, 1.0)
    metal = _col(kw, (176, 180, 186))
    L.forma([(x - 300 * s, y), (x - 260 * s, y - 120 * s), (x + 60 * s, y - 130 * s), (x + 90 * s, y - 40 * s),
             (x + 20 * s, y + 10)], metal, suave=False, intensidad=0.14, textura=0.16)
    L.forma([(x + 120 * s, y + 10), (x + 420 * s, y - 40 * s), (x + 430 * s, y), (x + 140 * s, y + 40)], oscuro(metal, 0.85),
            suave=False, intensidad=0.1)
    L.forma(elipse(x - 380 * s, y - 20 * s, 60 * s, 50 * s), oscuro(metal, 0.6), intensidad=0.2)
    for k in range(5):
        L.circulo(x - 220 * s + k * 50 * s, y - 80 * s, 10 * s, (50, 56, 64), borde=False)


# =========================================================================== #
# PERSONAS Y ANIMALES (animados)
# =========================================================================== #
@prop("persona", "dyn")
def p_persona(sc, nums, flags, kw):
    tipo = kw.get("tipo", "traje")
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1650), _n(nums, 2, 0.55)
    pose = kw.get("pose", "quieto")
    mov = float(kw.get("mov", "0"))
    osc = float(kw.get("osc", str(_luz_hora(sc) * 0.7)))
    def f(img, t, dur):
        figura(img, tipo, x + mov * t, y, s, t, pose=pose, espejo="espejo" in flags, oscuridad=osc,
               vel=0.7 if pose == "caminar" else 0.4)
    return f


@prop("grupo", "dyn", sonido=[("multitud", 0, 0)])
def p_grupo(sc, nums, flags, kw):
    tipo = kw.get("tipo", "traje")
    n = int(kw.get("n", "4"))
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1650), _n(nums, 2, 0.4)
    tipos = tipo.split(",")
    pose = kw.get("pose", "quieto")
    def f(img, t, dur):
        for k in range(n):
            xx = x + (k - (n - 1) / 2) * 150 * s / 0.4
            figura(img, tipos[k % len(tipos)], xx, y + (k % 2) * 24, s * (0.96 + (k % 3) * 0.03), t + k * 0.3, pose=pose,
                   espejo=k % 2 == 1, oscuridad=_luz_hora(sc) * 0.7, vel=0.6)
    return f


@prop("siluetas", "dyn")
def p_siluetas(sc, nums, flags, kw):
    n = int(kw.get("n", "3"))
    y, s = _n(nums, 0, 1600), _n(nums, 1, 0.6)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        for k in range(n):
            silueta(d, 200 + k * (700 / max(1, n - 1 or 1)) + t * 10, y, s, t * 0.6 + k, agachado=False, col=(10, 12, 16))
    return f


@prop("jinetes", "dyn", sonido=[("pasos", 0, 0)])
def p_jinetes(sc, nums, flags, kw):
    n = int(kw.get("n", "6"))
    y = _n(nums, 0, 1450)
    jinete = "sin_jinete" not in flags
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        for k in range(n):
            x = (k * 230 + t * 260) % (W + 400) - 200
            yy = y + (k % 3) * 70
            g = 8 * math.sin(t * 12 + k)
            col = (20, 18, 16)
            d.ellipse((x - 70, yy - 70 + g, x + 70, yy - 10 + g), fill=col)
            d.polygon([(x + 50, yy - 60 + g), (x + 110, yy - 120 + g), (x + 130, yy - 100 + g), (x + 80, yy - 40 + g)],
                      fill=col)
            for j, dx in enumerate((-50, -20, 30, 55)):
                a = math.sin(t * 12 + k + j * 1.6) * 30
                d.line((x + dx, yy - 20 + g, x + dx + a, yy + 50), fill=col, width=10)
            d.line((x - 70, yy - 50 + g, x - 110, yy - 20 + g), fill=col, width=8)
            if jinete:
                d.line((x, yy - 70 + g, x - 10, yy - 140 + g), fill=col, width=16)
                d.ellipse((x - 26, yy - 180 + g, x + 6, yy - 148 + g), fill=col)
        particulas(img, t, "ceniza", 40, viento=-300, alfa=120)
    return f


@prop("aves", "dyn", sonido=lambda f, kw: [("gaviotas", 0.4, 2.0)] if "gaviotas" in f else [])
def p_aves(sc, nums, flags, kw):
    n = int(kw.get("n", "6"))
    y = _n(nums, 0, 500)
    grande = "buitres" in flags
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        for k in range(n):
            x = (k * 170 + t * (60 + k * 6)) % (W + 200) - 100
            yy = y + 60 * math.sin(k * 1.7) + 10 * math.sin(t * 2 + k)
            a = 14 * math.sin(t * (4 if grande else 8) + k)
            sz = 46 if grande else 24
            d.line([(x - sz, yy - a), (x, yy), (x + sz, yy - a)], fill=(20, 20, 24), width=6 if grande else 4)
    return f


@prop("cabras", "img")
def p_cabras(sc, img, nums, flags, kw):
    y = _n(nums, 0, 1600)
    d = ImageDraw.Draw(img)
    for k, x in enumerate((220, 480, 820)):
        col = (200, 196, 186) if sc.hora not in ("noche",) else (90, 88, 86)
        d.ellipse((x - 70, y - 60, x + 70, y), fill=col)
        d.ellipse((x + 50, y - 100, x + 100, y - 50), fill=col)
        for dx in (-40, -10, 20, 45):
            d.line((x + dx, y - 10, x + dx, y + 50), fill=oscuro(col, 0.6), width=8)


@prop("criatura", "dyn", sonido=[("gruñido", 1.0, 1.2)])
def p_criatura(sc, nums, flags, kw):
    """Silueta de chupacabras con espinas y ojos rojos."""
    x, y, s = _n(nums, 0, 760), _n(nums, 1, 1620), _n(nums, 2, 1.0)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        xx = x - t * 20
        d.ellipse((xx - 90 * s, y - 200 * s, xx + 70 * s, y - 40 * s), fill=(14, 16, 14))
        d.ellipse((xx - 150 * s, y - 260 * s, xx - 60 * s, y - 170 * s), fill=(14, 16, 14))
        for k in range(6):
            bx = xx - 60 * s + k * 26 * s
            d.polygon([(bx - 12 * s, y - 190 * s + k * 6), (bx, y - 260 * s + k * 8), (bx + 12 * s, y - 190 * s + k * 6)],
                      fill=(14, 16, 14))
        for dx in (-40, 40):
            d.line((xx + dx * s, y - 60 * s, xx + dx * s + 10, y), fill=(14, 16, 14), width=int(16 * s))
        for dx in (-125, -95):
            pegar_glow(img, xx + dx * s, y - 225 * s, 12 * s, "#ff2020", 1.0)
    return f


@prop("nessie", "dyn")
def p_nessie(sc, nums, flags, kw):
    x, y = _n(nums, 0, 600), _n(nums, 1, 1250)
    juguete = "juguete" in flags
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        xx = x + 20 * math.sin(t * 0.5)
        col = (20, 26, 30)
        pts = [(xx - 120, y), (xx - 60, y - 250), (xx - 10, y - 370), (xx + 40, y - 390), (xx + 60, y - 350),
               (xx + 10, y - 330), (xx - 10, y - 230), (xx + 40, y)]
        d.polygon(pts, fill=col)
        d.ellipse((xx - 220, y - 30, xx - 80, y + 20), fill=col)
        if juguete:  # la foto falsa: un submarino de juguete con una cabeza de madera
            d.rectangle((xx - 150, y - 10, xx + 120, y + 26), fill=(80, 80, 86))
            d.text((xx + 150, y - 300), "JUGUETE", font=maquina(40), fill=(220, 60, 60))
    return f


@prop("anguila", "dyn")
def p_anguila(sc, nums, flags, kw):
    y = _n(nums, 0, 1300)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        x0 = -200 + t * 120
        pts = [(x0 + k * 18, y + 40 * math.sin(k * 0.25 - t * 4)) for k in range(40)]
        d.line(pts, fill=(60, 70, 50), width=34, joint="curve")
        d.ellipse((pts[-1][0] - 24, pts[-1][1] - 20, pts[-1][0] + 24, pts[-1][1] + 20), fill=(60, 70, 50))
    return f


# =========================================================================== #
# EFECTOS (animados)
# =========================================================================== #
@prop("lluvia", "dyn", sonido=[("lluvia", 0, 0)])
def p_lluvia(sc, nums, flags, kw):
    return lambda img, t, dur: particulas(img, t, "lluvia", int(_n(nums, 0, 90)), viento=-300, alfa=180)


@prop("nieve", "dyn", sonido=[("viento", 0, 0)])
def p_nieve(sc, nums, flags, kw):
    return lambda img, t, dur: particulas(img, t, "nieve", int(_n(nums, 0, 100)), viento=-250, vel=1.4)


@prop("ceniza", "dyn")
def p_ceniza(sc, nums, flags, kw):
    return lambda img, t, dur: particulas(img, t, "ceniza", int(_n(nums, 0, 50)), viento=80, alfa=180)


@prop("polvo", "dyn")
def p_polvo(sc, nums, flags, kw):
    x, y = _n(nums, 0, 300), _n(nums, 1, 700)
    return lambda img, t, dur: polvo(img, t, x, y, 400, n=16, semilla=int(x))


@prop("niebla", "dyn")
def p_niebla(sc, nums, flags, kw):
    y, a = _n(nums, 0, 1200), _n(nums, 1, 0.4)
    return lambda img, t, dur: niebla(img, t, y, a, n=10)


@prop("rayos", "dyn")
def p_rayos(sc, nums, flags, kw):
    x = _n(nums, 0, 540)
    col = _col(kw, (255, 236, 190))
    return lambda img, t, dur: rayos(img, t, x, col, n=4, alfa=int(_n(nums, 1, 24)))


@prop("relampago", "dyn", sonido=[("trueno", 1.0, 3.0)])
def p_relampago(sc, nums, flags, kw):
    def f(img, t, dur):
        relampago(img, t, 1.0)
        relampago(img, t, dur * 0.65)
    return f


@prop("linterna", "dyn")
def p_linterna(sc, nums, flags, kw):
    x, y, tx, ty = _n(nums, 0, 120), _n(nums, 1, 1900), _n(nums, 2, 540), _n(nums, 3, 1300)
    return lambda img, t, dur: linterna(img, x, y, tx + 200 * math.sin(t * 0.8), ty + 100 * math.sin(t * 1.3),
                                        ancho=230, oscuridad=int(_n(nums, 4, 175)))


@prop("brillo", "dyn")
def p_brillo(sc, nums, flags, kw):
    x, y, r = _n(nums, 0, 540), _n(nums, 1, 900), _n(nums, 2, 200)
    col = kw.get("color", "#ffd890")
    return lambda img, t, dur: pegar_glow(img, x, y, r * (1 + 0.06 * math.sin(t * 5)), col, float(kw.get("a", "0.6")))


@prop("destello", "dyn", sonido=[("explosion_lejana", 1.2, 3.0)])
def p_destello(sc, nums, flags, kw):
    x, y, t0 = _n(nums, 0, 700), _n(nums, 1, 700), _n(nums, 2, 1.2)
    def f(img, t, dur):
        k = max(0.0, 1 - abs(t - t0) / 0.5)
        if k > 0:
            pegar_glow(img, x, y, 200 + 600 * k, "#fff0c0", 0.9 * k)
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 230, int(120 * k ** 2))))
    return f


@prop("explosion", "dyn", sonido=[("explosion_lejana", 0.5, 3.0)])
def p_explosion(sc, nums, flags, kw):
    x, y = _n(nums, 0, 600), _n(nums, 1, 900)
    def f(img, t, dur):
        k = min(1.0, t / 1.5)
        pegar_glow(img, x, y, 300 + 700 * k, "#ffb060", 0.9 * (1 - k * 0.5))
        pegar_glow(img, x, y, 120 + 200 * k, "#fff4d0", 1 - k * 0.6)
        d = ImageDraw.Draw(img)
        r = 200 + 900 * k
        d.ellipse((x - r, y - r * 0.4, x + r, y + r * 0.4), outline=(255, 220, 160, int(160 * (1 - k))), width=12)
    return f


@prop("meteoro", "dyn")
def p_meteoro(sc, nums, flags, kw):
    def f(img, t, dur):
        p = min(1.0, t / max(dur * 0.6, 0.1))
        x, y = 1100 - 900 * p, 200 + 700 * p
        for k in range(12):
            pegar_glow(img, x + k * 30, y - k * 23, 40 - k * 2.5, "#ffd090", 0.8 * (1 - k / 12))
        pegar_glow(img, x, y, 70, "#ffffff", 1.0)
    return f


@prop("ola_gigante", "dyn", sonido=[("avalancha", 0.5, 3.0)])
def p_ola(sc, nums, flags, kw):
    def f(img, t, dur):
        p = min(1.0, t / max(dur * 0.8, 0.1))
        x0 = 1200 - 900 * p
        d = ImageDraw.Draw(img)
        pts = [(x0 - 200, 1500), (x0 - 100, 900), (x0 + 50, 600), (x0 + 250, 560), (x0 + 330, 680), (x0 + 200, 720),
               (x0 + 300, 1100), (W + 200, 1500)]
        d.polygon(pts, fill=(26, 54, 74, 240))
        interior = [(x0 - 40, 1500), (x0 + 20, 1000), (x0 + 120, 760), (x0 + 240, 700), (x0 + 200, 760), (x0 + 260, 1100),
                    (W + 200, 1500)]
        d.polygon(interior, fill=(40, 84, 104, 200))
        d.line(pts[1:6], fill=(236, 244, 250), width=18)
        for k in range(10):
            pegar_glow(img, x0 + 60 + k * 26, 600 + 14 * math.sin(k + t * 6), 40, "#ffffff", 0.5)
        particulas(img, t, "lluvia", 60, viento=-500, alfa=120)
    return f


@prop("ovni", "dyn", sonido=[("zumbido", 0, 0)])
def p_ovni(sc, nums, flags, kw):
    tipo = kw.get("tipo", "disco")
    x, y = _n(nums, 0, 540), _n(nums, 1, 700)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        if tipo == "luz_verde":
            pegar_glow(img, x + 160 * math.sin(t * 0.8), y + 60 * math.sin(t * 1.9), 140, "#60ff80", 0.85)
        elif tipo == "v":
            for k in range(7):
                dx = (k - 3) * 110
                pegar_glow(img, x + dx + t * 12, y + abs(dx) * 0.5, 40, "#ffcf80", 0.9)
        elif tipo == "tictac":
            xx, yy = x + 220 * math.sin(t * 1.4), y + 50 * math.sin(t * 2.2)
            d.rounded_rectangle((xx - 110, yy - 32, xx + 110, yy + 32), radius=32, fill=(246, 246, 246),
                                outline=(200, 200, 206), width=3)
            pegar_glow(img, xx, yy, 160, "#ffffff", 0.3)
        elif tipo == "luces":
            r = random.Random(int(x))
            for k in range(5):
                f_ = r.uniform(0, 6)
                pegar_glow(img, r.uniform(150, 930) + 40 * math.sin(t * 0.7 + f_), y + r.uniform(-200, 200)
                           + 30 * math.sin(t * 0.9 + f_), 60, kw.get("color", "#ffe7a0"), 0.5 + 0.4 * math.sin(t * 2 + f_))
        else:
            xx, yy = x + 200 * math.sin(t * 0.6), y + 40 * math.sin(t * 1.3)
            d.ellipse((xx - 170, yy - 30, xx + 170, yy + 34), fill=(180, 190, 200), outline=(40, 40, 50), width=4)
            d.ellipse((xx - 70, yy - 80, xx + 70, yy + 10), fill=(150, 190, 220), outline=(40, 40, 50), width=4)
            for k in range(6):
                pegar_glow(img, xx - 140 + k * 56, yy + 10, 18, "#9fe8ff", 0.6 + 0.4 * math.sin(t * 6 + k))
    return f


@prop("triangulo", "dyn", sonido=[("drone", 0, 0)])
def p_triangulo(sc, nums, flags, kw):
    """Triángulo de las Bermudas sobre el océano, visto desde arriba, con sus tres vértices."""
    pts = [(300, 640), (880, 820), (420, 1180)]
    nombres = ["MIAMI", "BERMUDAS", "PUERTO RICO"]
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        k = min(1.0, t / 1.5)
        for i in range(3):
            a, b = pts[i], pts[(i + 1) % 3]
            d.line((a[0], a[1], a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), fill=(255, 60, 60), width=8)
        for (x, y), nm in zip(pts, nombres):
            pegar_glow(img, x, y, 40, "#ff5050", 0.8)
            d.text((x, y - 50), nm, font=maquina(40), fill=(255, 230, 230), anchor="mm")
    return f


@prop("lluvia_carne", "dyn")
def p_lluvia_carne(sc, nums, flags, kw):
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        r = random.Random(3)
        for _ in range(34):
            x = r.uniform(0, W)
            y = (r.uniform(0, H) + t * r.uniform(300, 520)) % (H - 300)
            d.ellipse((x - 10, y - 7, x + 10, y + 7), fill=(150, 40, 40))
    return f


@prop("burbujas", "dyn", sonido=[("burbujas", 0, 0)])
def p_burbujas(sc, nums, flags, kw):
    def f(img, t, dur):
        r = random.Random(4)
        d = ImageDraw.Draw(img)
        for i in range(24):
            x = r.uniform(80, 1000) + 10 * math.sin(t * 2 + i)
            y = (r.uniform(0, H) - t * r.uniform(60, 140)) % H
            rr = r.uniform(4, 10)
            d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(200, 240, 255, 150), width=2)
    return f


@prop("bajo_agua", "L")
def p_bajo_agua(sc, L, nums, flags, kw):
    sc.hora = "agua"
    L.img.alpha_composite(_grad(W * 2, H * 2, [(0, (30, 110, 140)), (0.5, (12, 50, 76)), (1, (4, 16, 30))]))
    L.forma(catmull([(-50, 1680), (W + 50, 1660), (W + 50, H), (-50, H)], 3), (60, 70, 60), borde=False, textura=0.2)


@prop("algas", "L")
def p_algas(sc, L, nums, flags, kw):
    rr = random.Random(9)
    for _ in range(12):
        x = rr.uniform(0, W)
        L.linea(catmull([(x, 1720), (x + 20, 1600), (x - 10, 1500), (x + 15, 1400)], 4, cerrado=False), (40, 90, 60), 8)


@prop("terrazas", "L")
def p_terrazas(sc, L, nums, flags, kw):
    piedra = (70, 96, 100)
    for k in range(5):
        y = 1250 + k * 110
        L.forma([(80 + k * 40, y), (1000 - k * 30, y), (1000 - k * 30, y + 120), (80 + k * 40, y + 120)],
                oscuro(piedra, 1 - k * 0.06), suave=False, intensidad=0.08, textura=0.18)


@prop("anforas", "L")
def p_anforas(sc, L, nums, flags, kw):
    for k in range(7):
        x = 250 + k * 90
        L.forma(catmull([(x - 20, 1600), (x - 36, 1520), (x - 12, 1440), (x + 12, 1440), (x + 36, 1520), (x + 20, 1600)], 3),
                (150, 90, 60), intensidad=0.18, textura=0.12)


@prop("buzo", "dyn")
def p_buzo(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 400), _n(nums, 1, 1100), _n(nums, 2, 1.0)
    antiguo = "antiguo" in flags  # buzos de esponjas de 1901
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        xx, yy = x + t * 20, y + 20 * math.sin(t)
        traje = (110, 90, 60) if antiguo else (30, 34, 40)
        d.rounded_rectangle((xx - 120 * s, yy - 40 * s, xx + 120 * s, yy + 40 * s), radius=int(40 * s), fill=traje)
        if antiguo:
            d.ellipse((xx + 100 * s, yy - 60 * s, xx + 190 * s, yy + 30 * s), fill=(170, 130, 60), outline=(90, 60, 30),
                      width=6)
            d.ellipse((xx + 130 * s, yy - 30 * s, xx + 170 * s, yy + 5 * s), fill=(40, 60, 80))
        else:
            d.ellipse((xx + 100 * s, yy - 40 * s, xx + 170 * s, yy + 30 * s), fill=(40, 44, 50))
            d.rectangle((xx - 60 * s, yy - 70 * s, xx + 40 * s, yy - 40 * s), fill=(200, 200, 60))
        for k, dy in enumerate((-20, 20)):
            a = 30 * math.sin(t * 3 + k * 3)
            d.line((xx - 120 * s, yy + dy * s, xx - 220 * s, yy + dy * s + a), fill=traje, width=int(26 * s))
        if not antiguo:
            pegar_glow(img, xx + 220 * s, yy, 140, "#e8f8ff", 0.4)
    return f


@prop("satelite", "dyn")
def p_satelite(sc, nums, flags, kw):
    def f(img, t, dur):
        x, y = 200 + t * 60, 300 + 20 * math.sin(t)
        d = ImageDraw.Draw(img)
        d.rectangle((x - 30, y - 30, x + 30, y + 30), fill=(200, 180, 120), outline=(60, 50, 30), width=3)
        for dx in (-1, 1):
            xa, xb = sorted((x + dx * 40, x + dx * 150))
            d.rectangle((xa, y - 18, xb, y + 18), fill=(40, 60, 120), outline=(160, 170, 200), width=2)
        for k in range(3):  # pulsos de señal hacia la Tierra
            r_ = ((t * 120 + k * 80) % 240)
            d.arc((x - r_, y + 40 - r_ * 0.4, x + r_, y + 40 + r_ * 0.4), 20, 160, fill=(150, 220, 255, int(200 * (1 - r_ / 240))),
                  width=4)
    return f


@prop("iceberg", "dyn", sonido=[("avalancha", 1.5, 3.0)])
def p_iceberg(sc, nums, flags, kw):
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        k = min(1.0, max(0.0, (t - 1.2) / 1.5))
        d.polygon([(80, 1200), (180, 700), (500, 640), (520, 1200)], fill=(226, 240, 250), outline=(150, 190, 210))
        dx, dy = 120 * k, 200 * k ** 2
        d.polygon([(540 + dx, 1200 + dy), (560 + dx, 660 + dy), (900 + dx, 720 + dy), (980 + dx, 1200 + dy)],
                  fill=(206, 230, 244), outline=(150, 190, 210))
        if 0 < k < 1:
            particulas(img, t, "nieve", 60, viento=200, alfa=220)
    return f


@prop("huellas", "img")
def p_huellas(sc, img, nums, flags, kw):
    x0, y0, x1, y1 = _n(nums, 0, 100), _n(nums, 1, 1800), _n(nums, 2, 900), _n(nums, 3, 1300)
    d = ImageDraw.Draw(img)
    n = 14
    for k in range(n):
        f = k / (n - 1)
        x, y = x0 + (x1 - x0) * f + (12 if k % 2 else -12), y0 + (y1 - y0) * f
        r = 14 - 6 * f
        if "pezuna" in flags:
            d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=(120, 130, 160))
            d.line((x, y - r * 0.8, x, y + r * 0.8), fill=(226, 232, 240), width=3)
        else:
            d.ellipse((x - r, y - r * 0.5, x + r, y + r * 0.5), fill=(150, 160, 190))
