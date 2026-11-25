"""Objetos e interiores para el compositor de escenas (se registran en escenario.PROPS)."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import pro
from alcatraz import maquina
from cine import pegar_glow
from dinos import TINTA, catmull, claro, elipse, oscuro, sombra_suave
from escenario import _col, _escalar, _n, prop
from mis_kits import objeto
from pro import H, W, manuscrita
from realista import LienzoReal

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def _txt(d, xy, txt, tam, col, ancho_max=None, fuente=None, anchor="mm"):
    f = (fuente or pro.fuente)(tam)
    if ancho_max:
        while d.textlength(txt, font=f) > ancho_max and tam > 18:
            tam -= 3
            f = (fuente or pro.fuente)(tam)
    d.text(xy, txt, font=f, fill=col, anchor=anchor)


@prop("mesa", "L")
def p_mesa(sc, L, nums, flags, kw):
    x, y, w = _n(nums, 0, 540), _n(nums, 1, 1500), _n(nums, 2, 700)
    madera = (120, 80, 50)
    L.forma([(x - w / 2, y - 60), (x + w / 2, y - 60), (x + w / 2 + 40, y), (x - w / 2 - 40, y)], madera, suave=False,
            intensidad=0.1, textura=0.16)
    for dx in (-w / 2 + 10, w / 2 - 30):
        L.forma([(x + dx, y), (x + dx + 24, y), (x + dx + 24, y + 260), (x + dx, y + 260)], oscuro(madera, 0.8), suave=False)
    if "mantel" in flags:
        L.forma([(x - w / 2, y - 64), (x + w / 2, y - 64), (x + w / 2 + 50, y + 60), (x - w / 2 - 50, y + 60)],
                (236, 230, 216), suave=False, intensidad=0.08, textura=0.06)
    if "comida" in flags:  # platos servidos, tazas y pan: la comida seguía intacta
        for k in range(3):
            px = x - w / 3 + k * w / 3
            L.forma(elipse(px, y - 70, 70, 22), (240, 240, 236), intensidad=0.2, ancho=3)
            L.forma(elipse(px, y - 78, 40, 12), (170, 110, 60), intensidad=0.2, ancho=2)
        L.forma([(x + w / 2 - 90, y - 70), (x + w / 2 - 50, y - 70), (x + w / 2 - 54, y - 130), (x + w / 2 - 86, y - 130)],
                (230, 230, 226), suave=False, ancho=3)
        L.forma(elipse(x - w / 2 + 70, y - 100, 60, 30), (200, 150, 80), intensidad=0.2)


@prop("silla", "L")
def p_silla(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 300), _n(nums, 1, 1650)
    c = (100, 66, 40)
    L.forma([(x - 70, y - 180), (x + 70, y - 180), (x + 70, y - 150), (x - 70, y - 150)], c, suave=False)
    L.forma([(x - 70, y - 180), (x - 50, y - 180), (x - 50, y - 420), (x - 70, y - 420)], c, suave=False)
    for dx in (-70, 50):
        L.forma([(x + dx, y - 150), (x + dx + 20, y - 150), (x + dx + 20, y), (x + dx, y)], oscuro(c, 0.8), suave=False)
    if "caida" in flags:
        pass


@prop("perchero", "L")
def p_perchero(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 860), _n(nums, 1, 1450)
    L.linea([(x, y), (x, y - 640)], (80, 56, 36), 14)
    L.linea([(x - 60, y), (x + 60, y)], (80, 56, 36), 14)
    if "impermeable" in flags:  # el impermeable que quedó colgado
        L.forma(catmull([(x - 20, y - 620), (x - 110, y - 520), (x - 130, y - 220), (x + 40, y - 230), (x + 30, y - 600)], 4),
                (200, 170, 50), intensidad=0.16, textura=0.1)


@prop("radio", "dyn", sonido=[("estatica", 0, 0), ("morse", 0.4, -1)])
def p_radio(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1350), _n(nums, 2, 1.0)
    txt = kw.get("txt", "")
    Lz = LienzoReal(W, H, 0, 0)
    P = lambda a, b: (x + a * s, y + b * s)
    Lz.forma([P(-380, 0), P(380, 0), P(380, -540), P(-380, -540)], (92, 58, 34), suave=False, intensidad=0.1, textura=0.16)
    Lz.forma([P(-340, -40), P(-20, -40), P(-20, -500), P(-340, -500)], (40, 30, 24), suave=False, intensidad=0.05)
    for yy in range(-480, -50, 26):
        Lz.linea([P(-325, yy), P(-35, yy)], (70, 54, 40), 6)
    for xx in (110, 290):
        Lz.forma(elipse(x + xx * s, y - 130 * s, 62 * s, 62 * s), (40, 34, 30), intensidad=0.25)
        Lz.forma(elipse(x + xx * s, y - 130 * s, 40 * s, 40 * s), (180, 160, 120), intensidad=0.3)
    spr = Lz.final()
    def f(img, t, dur):
        img.alpha_composite(spr)
        d = ImageDraw.Draw(img)
        d.rectangle((x + 30 * s, y - 470 * s, x + 350 * s, y - 340 * s), fill=(255, 190, 90))
        pegar_glow(img, x + 190 * s, y - 405 * s, 220 * s, "#ffb050", 0.5 + 0.1 * math.sin(t * 9))
        ag = x + (40 + 300 * (0.5 + 0.5 * math.sin(t * 0.7))) * s
        d.line((ag, y - 468 * s, ag, y - 342 * s), fill=(150, 20, 20), width=6)
        if txt:
            vis = txt[:max(0, int(t * 6))]
            _txt(d, (W / 2, y - 680 * s), "«" + vis + ("_" if int(t * 3) % 2 else "") + "»", 60, (255, 230, 170),
                 ancho_max=980, fuente=maquina)
    return f


@prop("telefono", "L")
def p_telefono(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 760), _n(nums, 1, 1400)
    L.forma([(x - 90, y), (x + 90, y), (x + 70, y - 90), (x - 70, y - 90)], (30, 30, 32), suave=False, intensidad=0.2)
    L.forma(catmull([(x - 120, y - 120), (x - 80, y - 160), (x + 80, y - 160), (x + 120, y - 120), (x + 80, y - 100),
                     (x - 80, y - 100)], 4), (30, 30, 32), intensidad=0.2)
    L.forma(elipse(x, y - 45, 34, 30), (220, 220, 210), intensidad=0.2)


@prop("maquina_escribir", "L", sonido=[("teclas", 0.3, 2.0)])
def p_maquina(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1450)
    L.forma([(x - 260, y), (x + 260, y), (x + 220, y - 150), (x - 220, y - 150)], (40, 42, 46), suave=False, intensidad=0.2)
    L.forma([(x - 240, y - 150), (x + 240, y - 150), (x + 240, y - 200), (x - 240, y - 200)], (60, 62, 66), suave=False)
    L.forma([(x - 180, y - 200), (x + 180, y - 200), (x + 170, y - 420), (x - 170, y - 420)], (240, 236, 222), suave=False,
            intensidad=0.05)
    for k in range(3):
        for j in range(10):
            L.circulo(x - 190 + j * 42, y - 40 - k * 36, 13, (220, 220, 210), ancho=2)


@prop("tv", "dyn", sonido=[("estatica", 0, 0)])
def p_tv(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 900), _n(nums, 2, 1.0)
    modo = kw.get("modo", "estatica")
    txt = kw.get("txt", "")
    import numpy as np
    ruidos = [Image.fromarray(np.random.default_rng(i).integers(20, 235, (120, 160), dtype="uint8"), "L")
              .resize((int(640 * s), int(480 * s)), Image.NEAREST).convert("RGBA") for i in range(5)]
    w, h = int(640 * s), int(480 * s)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x - w / 2 - 50, y - h / 2 - 50, x + w / 2 + 50, y + h / 2 + 90), radius=50, fill=(46, 40, 36))
        if modo == "noticiero" and int(t * 4) % 9:
            pant = Image.new("RGBA", (w, h), (30, 50, 90, 255))
            dp = ImageDraw.Draw(pant)
            dp.rectangle((0, h * 0.72, w, h), fill=(180, 30, 30))
            _txt(dp, (w / 2, h * 0.86), txt or "NOTICIAS", int(40 * s), (255, 255, 255), ancho_max=w - 40)
            dp.ellipse((w * 0.38, h * 0.18, w * 0.62, h * 0.5), fill=(220, 190, 160))
            dp.rectangle((w * 0.32, h * 0.5, w * 0.68, h * 0.72), fill=(40, 40, 60))
        elif modo == "mascara":  # la señal pirata: fondo de franjas que giran y una figura enmascarada
            pant = Image.new("RGBA", (w, h), (40, 40, 50, 255))
            dp = ImageDraw.Draw(pant)
            for k in range(-8, 20):
                xx = k * 50 * s + (t * 120) % (100 * s)
                dp.polygon([(xx, 0), (xx + 25 * s, 0), (xx - 95 * s, h), (xx - 120 * s, h)], fill=(90, 90, 110, 255))
            dp.ellipse((w * 0.36, h * 0.2, w * 0.64, h * 0.62), fill=(230, 220, 205))
            dp.rectangle((w * 0.38, h * 0.33, w * 0.62, h * 0.4), fill=(20, 20, 24))
            dp.rectangle((w * 0.3, h * 0.62, w * 0.7, h), fill=(30, 30, 34))
        elif modo == "flir":  # video infrarrojo del Tic Tac
            pant = Image.new("RGBA", (w, h), (40, 44, 40, 255))
            dp = ImageDraw.Draw(pant)
            ox = w / 2 + 80 * s * math.sin(t * 1.2)
            dp.rounded_rectangle((ox - 60 * s, h / 2 - 18 * s, ox + 60 * s, h / 2 + 18 * s), radius=int(18 * s),
                                 fill=(20, 20, 20))
            dp.line((w / 2 - 40 * s, h / 2, w / 2 - 10 * s, h / 2), fill=(230, 230, 230), width=3)
            dp.line((w / 2 + 10 * s, h / 2, w / 2 + 40 * s, h / 2), fill=(230, 230, 230), width=3)
            _txt(dp, (60 * s, 40 * s), "IR  NAR  1.0", int(26 * s), (230, 230, 230), fuente=maquina, anchor="lm")
        else:
            pant = ruidos[int(t * 15) % 5].copy()
        yy = int((t * 160) % h)
        ImageDraw.Draw(pant).rectangle((0, yy, w, yy + 24), fill=(255, 255, 255, 40))
        img.alpha_composite(pant, (int(x - w / 2), int(y - h / 2)))
        pegar_glow(img, x, y, w * 0.9, "#a0c0ff", 0.22 + 0.06 * math.sin(t * 20))
    return f


@prop("computadora", "dyn", sonido=[("teclas", 0.2, 2.5)])
def p_computadora(sc, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1000), _n(nums, 2, 1.0)
    txt = kw.get("txt", "")
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        w, h = 720 * s, 460 * s
        d.rounded_rectangle((x - w / 2 - 30, y - h / 2 - 30, x + w / 2 + 30, y + h / 2 + 30), radius=24, fill=(30, 30, 34))
        d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=(8, 16, 10))
        d.rectangle((x - 60, y + h / 2 + 30, x + 60, y + h / 2 + 110), fill=(40, 40, 44))
        d.rectangle((x - 300, y + h / 2 + 110, x + 300, y + h / 2 + 140), fill=(50, 50, 54))
        vis = txt[:max(0, int(t * 9))]
        lineas, linea = [], ""
        for pal in vis.split(" "):
            if len(linea + pal) > 22:
                lineas.append(linea)
                linea = ""
            linea += pal + " "
        lineas.append(linea + ("_" if int(t * 3) % 2 else ""))
        for k, ln in enumerate(lineas[-6:]):
            d.text((x - w / 2 + 30, y - h / 2 + 40 + k * 62), ln, font=maquina(44), fill=(90, 255, 130))
        pegar_glow(img, x, y, w * 0.7, "#60ff90", 0.18)
    return f


@prop("cabina", "dyn", sonido=[("helice", 0, 0)])
def p_cabina(sc, nums, flags, kw):
    """Cabina de avión antiguo: parabrisas con la vista exterior, panel de instrumentos y la brújula que gira."""
    vista = kw.get("vista", "mar")
    brujula_loca = "brujula" in flags
    Lz = LienzoReal(W, H, 0, 0)
    cielos = {"mar": [(0, (60, 80, 120)), (0.5, (120, 140, 160)), (1, (120, 140, 160))],
              "noche": [(0, (8, 12, 28)), (1, (30, 40, 70))], "niebla": [(0, (150, 156, 162)), (1, (170, 174, 178))],
              "nieve": [(0, (90, 110, 150)), (1, (200, 206, 220))]}
    from dinos import _grad
    Lz.img.alpha_composite(_grad(W * 2, H * 2, cielos.get(vista, cielos["mar"])))
    if vista == "mar":
        Lz.forma([(0, 820), (W, 820), (W, 1100), (0, 1100)], (30, 50, 70), suave=False, borde=False)
    elif vista == "nieve":
        from pro import montanas
        montanas(Lz, 1000, [(200, 500, 300), (700, 600, 360)], (110, 116, 136), nieve=True, borde=False)
    marco = (40, 44, 50)
    Lz.forma([(0, 0), (W, 0), (W, 260), (0, 260)], marco, suave=False, borde=False)
    Lz.forma([(0, 0), (120, 0), (200, 1100), (0, 1100)], marco, suave=False, borde=False)
    Lz.forma([(W, 0), (W - 120, 0), (W - 200, 1100), (W, 1100)], marco, suave=False, borde=False)
    Lz.forma([(490, 260), (590, 260), (570, 1100), (510, 1100)], marco, suave=False, borde=False)
    Lz.forma([(0, 1050), (W, 1050), (W, H), (0, H)], (36, 38, 42), suave=False, intensidad=0.05, textura=0.12)
    for k, (cx, cy) in enumerate(((180, 1250), (420, 1250), (900, 1250), (180, 1480), (900, 1480))):
        Lz.forma(elipse(cx, cy, 90, 90), (20, 20, 22), intensidad=0.2)
        Lz.forma(elipse(cx, cy, 76, 76), (230, 230, 220), intensidad=0.1)
    spr = Lz.final()
    def f(img, t, dur):
        img.alpha_composite(spr)
        d = ImageDraw.Draw(img)
        for k, (cx, cy) in enumerate(((180, 1250), (420, 1250), (900, 1250), (180, 1480), (900, 1480))):
            a = t * (0.5 + k * 0.3) + k
            d.line((cx, cy, cx + 60 * math.cos(a), cy + 60 * math.sin(a)), fill=(20, 20, 20), width=5)
        # brújula grande al centro
        cx, cy, r = 660, 1460, 150
        d.ellipse((cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16), fill=(30, 30, 32))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(236, 230, 210))
        for k, letra in enumerate("NESO"):
            a = -math.pi / 2 + k * math.pi / 2
            d.text((cx + (r - 34) * math.cos(a), cy + (r - 34) * math.sin(a)), letra, font=maquina(40), fill=TINTA,
                   anchor="mm")
        ang = t * 4.5 if brujula_loca else math.sin(t) * 0.1
        ang += 0.6 * math.sin(t * 7) if brujula_loca else 0
        d.polygon([(cx + (r - 50) * math.cos(ang), cy + (r - 50) * math.sin(ang)),
                   (cx + 16 * math.cos(ang + 1.57), cy + 16 * math.sin(ang + 1.57)),
                   (cx - (r - 50) * math.cos(ang), cy - (r - 50) * math.sin(ang)),
                   (cx + 16 * math.cos(ang - 1.57), cy + 16 * math.sin(ang - 1.57))], fill=(190, 30, 30))
        if brujula_loca:
            pegar_glow(img, cx, cy, 220, "#ff4040", 0.2 + 0.15 * math.sin(t * 8))
    return f


@prop("brujula", "dyn")
def p_brujula(sc, nums, flags, kw):
    x, y, r = _n(nums, 0, 540), _n(nums, 1, 1100), _n(nums, 2, 220)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.ellipse((x - r - 24, y - r - 24, x + r + 24, y + r + 24), fill=(150, 110, 50))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(236, 230, 210))
        ang = t * 3 + 0.8 * math.sin(t * 5)
        d.polygon([(x + (r - 40) * math.cos(ang), y + (r - 40) * math.sin(ang)), (x + 20 * math.cos(ang + 1.57),
                   y + 20 * math.sin(ang + 1.57)), (x - (r - 40) * math.cos(ang), y - (r - 40) * math.sin(ang)),
                   (x + 20 * math.cos(ang - 1.57), y + 20 * math.sin(ang - 1.57))], fill=(190, 30, 30))
    return f


@prop("reloj", "dyn", sonido=[("reloj", 0, 0)])
def p_reloj(sc, nums, flags, kw):
    x, y, r = _n(nums, 0, 540), _n(nums, 1, 700), _n(nums, 2, 160)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.ellipse((x - r - 14, y - r - 14, x + r + 14, y + r + 14), fill=(60, 40, 26))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 234, 216))
        for k in range(12):
            a = k * math.pi / 6
            d.line((x + (r - 24) * math.cos(a), y + (r - 24) * math.sin(a), x + (r - 8) * math.cos(a),
                    y + (r - 8) * math.sin(a)), fill=TINTA, width=5)
        a = -math.pi / 2 + t * 1.2
        d.line((x, y, x + (r - 40) * math.cos(a), y + (r - 40) * math.sin(a)), fill=TINTA, width=6)
        d.line((x, y, x + (r - 80) * math.cos(a / 12 + 1), y + (r - 80) * math.sin(a / 12 + 1)), fill=TINTA, width=10)
    return f


@prop("vitrina", "img")
def p_vitrina(sc, img, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1250), _n(nums, 2, 1.0)
    obj = kw.get("obj")
    d = ImageDraw.Draw(img)
    d.rectangle((x - 300 * s, y, x + 300 * s, y + 380 * s), fill=(40, 30, 26))
    if obj:
        o = objeto(obj, random.Random(len(obj))) if obj not in ("busto", "bota", "pulsera", "calcetin") else _especial(obj)
        if o is not None:
            k = min(500 * s / o.width, 560 * s / o.height)
            o = _escalar(o, k)
            img.alpha_composite(o, (int(x - o.width / 2), int(y - 20 * s - o.height)))
    vid = Image.new("RGBA", (int(620 * s), int(640 * s)), (200, 230, 255, 26))
    ImageDraw.Draw(vid).rectangle((0, 0, vid.width - 1, vid.height - 1), outline=(220, 240, 255, 140), width=4)
    img.alpha_composite(vid, (int(x - vid.width / 2), int(y - vid.height)))
    pegar_glow(img, x, y - 300 * s, 320 * s, "#fff4d8", 0.35)


def _especial(nombre):
    im = Image.new("RGBA", (600, 700), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if nombre == "busto":  # busto de Nefertiti con su corona azul
        d.polygon([(200, 700), (400, 700), (380, 560), (220, 560)], fill=(200, 150, 110))
        d.ellipse((220, 300, 380, 520), fill=(196, 140, 100))
        d.rectangle((265, 480, 335, 580), fill=(196, 140, 100))
        d.polygon([(210, 330), (230, 90), (400, 60), (420, 320)], fill=(40, 70, 140))
        d.rectangle((215, 300, 410, 330), fill=(200, 160, 60))
        d.ellipse((310, 380, 350, 410), fill=(30, 20, 20))
        d.polygon([(180, 600), (420, 600), (460, 700), (140, 700)], fill=(80, 130, 90))
    elif nombre == "bota":
        d.polygon([(200, 200), (330, 200), (340, 520), (520, 560), (520, 640), (200, 640)], fill=(80, 54, 34))
        d.rectangle((210, 560, 500, 600), fill=(150, 130, 100))
        _txt(d, (360, 590), "A.C. IRVINE", 34, (60, 40, 30), fuente=maquina)
    elif nombre == "pulsera":  # pulsera de plata de Saint-Exupéry
        d.ellipse((100, 260, 500, 460), outline=(200, 204, 210), width=26)
        d.rounded_rectangle((200, 320, 400, 400), radius=16, fill=(206, 210, 216))
        _txt(d, (300, 360), "ANTOINE", 30, (60, 60, 70), fuente=maquina)
    return im


@prop("microscopio", "L")
def p_microscopio(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 760), _n(nums, 1, 1450)
    c = (60, 64, 72)
    L.forma([(x - 120, y), (x + 120, y), (x + 100, y - 40), (x - 100, y - 40)], c, suave=False)
    L.linea([(x + 40, y - 40), (x + 70, y - 300)], c, 34)
    L.linea([(x + 70, y - 300), (x - 30, y - 480)], (200, 204, 210), 40)
    L.forma([(x - 90, y - 160), (x + 60, y - 160), (x + 60, y - 140), (x - 90, y - 140)], c, suave=False)


@prop("adn", "dyn")
def p_adn(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 800)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x - 300, y - 360, x + 300, y + 360), radius=30, fill=(10, 20, 34), outline=(80, 160, 220),
                            width=6)
        for k in range(30):
            yy = y - 320 + k * 22
            a = k * 0.45 + t * 2
            x1, x2 = x + 150 * math.sin(a), x - 150 * math.sin(a)
            d.line((x1, yy, x2, yy), fill=(120, 200, 255) if k % 2 else (255, 140, 200), width=4)
            d.ellipse((x1 - 9, yy - 9, x1 + 9, yy + 9), fill=(120, 220, 255))
            d.ellipse((x2 - 9, yy - 9, x2 + 9, yy + 9), fill=(255, 160, 220))
        pegar_glow(img, x, y, 400, "#60b0ff", 0.2)
    return f


@prop("maleta", "L")
def p_maleta(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1500)
    c = (110, 70, 40)
    L.forma([(x - 280, y), (x + 280, y), (x + 280, y - 220), (x - 280, y - 220)], c, suave=False, intensidad=0.12,
            textura=0.16)
    L.forma([(x - 280, y - 220), (x + 280, y - 220), (x + 240, y - 470), (x - 240, y - 470)], oscuro(c, 0.85), suave=False,
            intensidad=0.1)
    if "pelucas" in flags:  # pelucas y documentos falsos
        for k, col in enumerate(((60, 40, 30), (170, 120, 60), (30, 30, 30))):
            L.forma(elipse(x - 170 + k * 170, y - 240, 90, 60), col, intensidad=0.2, textura=0.3)
        for k in range(3):
            L.forma([(x - 220 + k * 160, y - 150), (x - 100 + k * 160, y - 160), (x - 90 + k * 160, y - 80),
                     (x - 210 + k * 160, y - 70)], (236, 226, 200), suave=False, ancho=2)


@prop("escalera", "L")
def p_escalera(sc, L, nums, flags, kw):
    piedra = (110, 104, 96)
    for k in range(8):
        y = 1700 - k * 90
        L.forma([(100 + k * 60, y), (900, y), (900, y - 90), (100 + k * 60, y - 90)], oscuro(piedra, 0.9 - k * 0.03),
                suave=False, intensidad=0.08, textura=0.2)
    if "huesos" in flags:
        for k in range(5):
            L.linea([(220 + k * 40, 1770 - (k % 2) * 20), (300 + k * 40, 1760)], (230, 224, 206), 10)
        L.forma(elipse(200, 1760, 26, 22), (230, 224, 206), intensidad=0.2)
        L.forma(elipse(330, 1780, 22, 18), (230, 224, 206), intensidad=0.2)


@prop("barrotes", "L")
def p_barrotes(sc, L, nums, flags, kw):
    for x in range(60, W, 110):
        L.linea([(x, 0), (x, H)], (50, 52, 58), 22)
    L.linea([(0, 500), (W, 500)], (50, 52, 58), 18)


@prop("cama", "L")
def p_cama(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1550)
    L.forma([(x - 360, y), (x + 360, y), (x + 360, y - 120), (x - 360, y - 120)], (90, 80, 70), suave=False)
    L.forma([(x - 360, y - 120), (x + 360, y - 120), (x + 340, y - 170), (x - 340, y - 170)], (180, 170, 150), suave=False)


@prop("camara_cine", "L")
def p_camara_cine(sc, L, nums, flags, kw):
    """Cámara de cine de 16 lentes de Louis Le Prince sobre su trípode."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1500)
    madera = (130, 90, 54)
    for dx in (-180, 0, 180):
        L.linea([(x, y - 520), (x + dx, y)], (80, 56, 36), 16)
    L.forma([(x - 220, y - 520), (x + 220, y - 520), (x + 220, y - 860), (x - 220, y - 860)], madera, suave=False,
            intensidad=0.12, textura=0.18)
    for k in range(4):
        for j in range(4):
            L.circulo(x - 120 + j * 80, y - 800 + k * 80, 24, (30, 34, 40), ancho=3)
    L.forma(elipse(x + 240, y - 760, 60, 60), (40, 36, 30), intensidad=0.2)
    L.linea([(x + 240, y - 760), (x + 300, y - 700)], (60, 50, 40), 10)


@prop("camara_foto", "L")
def p_camara_foto(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1300), _n(nums, 2, 1.0)
    P = lambda a, b: (x + a * s, y + b * s)
    L.forma([P(-200, 0), P(200, 0), P(200, -220), P(-200, -220)], (40, 38, 36), suave=False, intensidad=0.15, textura=0.14)
    L.forma(elipse(x, y - 110 * s, 90 * s, 90 * s), (20, 22, 26), intensidad=0.25)
    L.forma(elipse(x, y - 110 * s, 50 * s, 50 * s), (60, 80, 110), intensidad=0.3)
    L.forma([P(-160, -220), P(-60, -220), P(-60, -270), P(-160, -270)], (40, 38, 36), suave=False)


@prop("corcho", "img")
def p_corcho(sc, img, nums, flags, kw):
    """Tablero de investigación con retratos de sospechosos e hilo rojo."""
    n = int(kw.get("n", "5"))
    d = ImageDraw.Draw(img)
    d.rectangle((60, 280, 1020, 1320), fill=(150, 108, 66), outline=(90, 60, 34), width=14)
    r = random.Random(n)
    pins = []
    for k in range(n):
        x, y = 180 + (k % 3) * 300 + r.uniform(-30, 30), 430 + (k // 3) * 420 + r.uniform(-20, 20)
        d.rectangle((x - 100, y - 120, x + 100, y + 140), fill=(240, 236, 226))
        d.rectangle((x - 80, y - 100, x + 80, y + 80), fill=(120, 116, 110))
        d.ellipse((x - 40, y - 80, x + 40, y + 10), fill=(60, 56, 54))
        d.rounded_rectangle((x - 64, y + 10, x + 64, y + 80), radius=30, fill=(60, 56, 54))
        d.text((x, y + 112), "?", font=pro.fuente(40), fill=(150, 20, 20), anchor="mm")
        pins.append((x, y - 120))
    for a, b in zip(pins, pins[1:]):
        d.line((a[0], a[1], b[0], b[1]), fill=(200, 20, 30), width=5)
    for x, y in pins:
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(210, 30, 40))


@prop("objeto", "img")
def p_objeto(sc, img, nums, flags, kw):
    nombre = kw.get("nombre", "voynich")
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1000), _n(nums, 2, 1.0)
    o = objeto(nombre, random.Random(len(nombre))) if nombre not in ("busto", "bota", "pulsera") else _especial(nombre)
    if o is None:
        return
    k = min(820 * s / o.width, 980 * s / o.height)
    o = _escalar(o, k).rotate(float(kw.get("giro", "0")), expand=True, resample=Image.BICUBIC)
    sombra_suave(img, (x - o.width / 2 + 16, y - o.height / 2 + 16, x + o.width / 2 - 8, y + o.height / 2 - 8),
                 radio=10, alfa=140, blur=24)
    img.alpha_composite(o, (int(x - o.width / 2), int(y - o.height / 2)))


@prop("lupa", "dyn")
def p_lupa(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1000)
    def f(img, t, dur):
        lx, ly = x + 200 * math.sin(t * 0.7), y + 220 * math.sin(t * 0.5)
        d = ImageDraw.Draw(img)
        d.ellipse((lx - 120, ly - 120, lx + 120, ly + 120), outline=(200, 170, 110), width=14)
        d.line((lx + 85, ly + 85, lx + 200, ly + 200), fill=(90, 60, 40), width=26)
    return f


@prop("carta", "img", sonido=[("papel", 0.1, 0.5)])
def p_carta(sc, img, nums, flags, kw):
    """Carta con texto real de la historia (p. ej. «Dear Boss», «Debemos estar sobre ustedes»)."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1000)
    txt = kw.get("txt", "")
    w, h = 760, 900
    hoja = Image.new("RGBA", (w, h), (238, 226, 196, 255))
    d = ImageDraw.Draw(hoja)
    d.rectangle((0, 0, w - 1, h - 1), outline=(150, 130, 100), width=6)
    palabras, lineas, ln = txt.split(), [], ""
    for p in palabras:
        if len(ln + p) > 18:
            lineas.append(ln)
            ln = ""
        ln += p + " "
    lineas.append(ln)
    tinta = (150, 30, 30) if "roja" in flags else (40, 40, 80)
    for k, l in enumerate(lineas[:8]):
        d.text((60, 90 + k * 96), l, font=manuscrita(66), fill=tinta)
    if "firma" in kw:
        d.text((w - 60, h - 90), kw["firma"], font=manuscrita(58), fill=tinta, anchor="rm")
    hoja = hoja.rotate(float(kw.get("giro", "-4")), expand=True, resample=Image.BICUBIC)
    sombra_suave(img, (x - hoja.width / 2 + 20, y - hoja.height / 2 + 20, x + hoja.width / 2, y + hoja.height / 2),
                 radio=10, alfa=140, blur=26)
    img.alpha_composite(hoja, (int(x - hoja.width / 2), int(y - hoja.height / 2)))


@prop("periodico", "img", sonido=[("papel", 0.1, 0.5)])
def p_periodico(sc, img, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1000)
    tit, fecha = kw.get("txt", ""), kw.get("fecha", "")
    hoja = Image.new("RGBA", (780, 980), (236, 230, 214, 255))
    d = ImageDraw.Draw(hoja)
    d.text((390, 60), kw.get("cab", "EDICIÓN EXTRA"), font=maquina(50), fill=(30, 26, 20), anchor="mm")
    d.text((390, 104), fecha, font=maquina(26), fill=(90, 70, 50), anchor="mm")
    d.line((30, 130, 750, 130), fill=(30, 26, 20), width=4)
    _txt(d, (390, 210), tit, 72, (140, 20, 20), ancho_max=720)
    d.rectangle((40, 280, 420, 640), fill=(196, 190, 176), outline=(60, 50, 40), width=4)
    for k in range(14):
        d.line((440, 290 + k * 25, 740, 290 + k * 25), fill=(150, 140, 120), width=6)
    for k in range(11):
        d.line((40, 670 + k * 26, 740, 670 + k * 26), fill=(150, 140, 120), width=6)
    hoja = hoja.rotate(float(kw.get("giro", "5")), expand=True, resample=Image.BICUBIC)
    img.alpha_composite(hoja, (int(x - hoja.width / 2), int(y - hoja.height / 2)))


@prop("pasaporte", "img")
def p_pasaporte(sc, img, nums, flags, kw):
    """Pasaporte protector sueco (Schutz-Pass) de Wallenberg."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1000)
    d = ImageDraw.Draw(img)
    for k in range(3):
        dx = (k - 1) * 60
        d.rectangle((x - 300 + dx, y - 380 + k * 30, x + 300 + dx, y + 380 + k * 30), fill=(232, 226, 206),
                    outline=(120, 110, 90), width=6)
    d.rectangle((x - 240 + 60, y - 300 + 60, x + 240 + 60, y - 220 + 60), fill=(40, 80, 150))
    d.rectangle((x - 240 + 60, y - 220 + 60, x + 240 + 60, y - 160 + 60), fill=(250, 210, 50))
    _txt(d, (x + 60, y - 90 + 60), "SCHUTZ-PASS", 56, (30, 40, 90), fuente=maquina)
    d.rectangle((x - 200 + 60, y + 60, x - 20 + 60, y + 260), fill=(160, 154, 140))
    for k in range(5):
        d.line((x + 20 + 60, y + 80 + k * 40, x + 220 + 60, y + 80 + k * 40), fill=(120, 110, 90), width=5)


@prop("mascaras", "img")
def p_mascaras(sc, img, nums, flags, kw):
    """Las máscaras de plomo y la nota."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 900)
    d = ImageDraw.Draw(img)
    for k, dx in enumerate((-220, 220)):
        d.rounded_rectangle((x + dx - 170, y - 70, x + dx + 170, y + 70), radius=20, fill=(120, 124, 130),
                            outline=(70, 72, 78), width=6)
        for ox in (-70, 70):
            d.ellipse((x + dx + ox - 40, y - 30, x + dx + ox + 40, y + 30), outline=(80, 82, 88), width=6)
    nota = Image.new("RGBA", (760, 300), (238, 230, 206, 255))
    dn = ImageDraw.Draw(nota)
    dn.text((30, 40), "Tomar cápsulas...", font=manuscrita(56), fill=(40, 40, 80))
    dn.text((30, 130), "protegerse...", font=manuscrita(56), fill=(40, 40, 80))
    dn.text((30, 220), "esperar señal máscara", font=manuscrita(50), fill=(40, 40, 80))
    nota = nota.rotate(-4, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(nota, (int(x - nota.width / 2), int(y + 160)))


@prop("fragmento", "L")
def p_fragmento(sc, L, nums, flags, kw):
    """Pieza de ala (flaperón) varada en la arena."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1600)
    L.forma([(x - 320, y), (x + 300, y - 70), (x + 340, y - 10), (x - 300, y + 70)], (226, 226, 222), suave=False,
            intensidad=0.14, textura=0.2)
    for k in range(6):
        L.linea([(x - 260 + k * 100, y + 50 - k * 12), (x - 250 + k * 100, y - 10 - k * 12)], (150, 150, 150), 3)


@prop("radar", "dyn", sonido=lambda f, kw: [("ping", 0.2 + k * 1.4, 1.0) for k in range(5)])
def p_radar(sc, nums, flags, kw):
    cx, cy, R_ = _n(nums, 0, 540), _n(nums, 1, 900), _n(nums, 2, 380)
    pierde = "pierde" in flags
    gira = "vuelta" in flags
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.ellipse((cx - R_ - 30, cy - R_ - 30, cx + R_ + 30, cy + R_ + 30), fill=(14, 20, 16))
        for k in range(1, 5):
            d.ellipse((cx - R_ * k / 4, cy - R_ * k / 4, cx + R_ * k / 4, cy + R_ * k / 4), outline=(40, 160, 90), width=3)
        ang = t * 2.2
        for k in range(18):
            a = ang - k * 0.04
            d.line((cx, cy, cx + R_ * math.cos(a), cy + R_ * math.sin(a)), fill=(60, 255, 140, int(140 * (1 - k / 18))),
                   width=6)
        p = t / max(dur, 0.1)
        if gira:  # el avión da media vuelta
            bx, by = cx + 200 - 380 * p, cy - 120 + 160 * math.sin(p * math.pi)
        else:
            bx, by = cx - 220 + 300 * p, cy - 80
        if not (pierde and p > 0.5):
            pegar_glow(img, bx, by, 24, "#60ff90", 0.9)
    return f


@prop("velas", "dyn")
def p_velas(sc, nums, flags, kw):
    y = _n(nums, 0, 1450)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        for x in (200, 540, 880):
            d.rectangle((x - 16, y - 120, x + 16, y), fill=(240, 230, 200))
            fl = 1 + 0.15 * math.sin(t * 12 + x)
            pegar_glow(img, x, y - 140, 150 * fl, "#ffb040", 0.7)
            pegar_glow(img, x, y - 140, 22, "#fff0c0", 1)
    return f


@prop("fuego", "dyn", sonido=[("fuego", 0, 0)])
def p_fuego(sc, nums, flags, kw):
    y = _n(nums, 0, 1300)
    def f(img, t, dur):
        for k in range(16):
            fz = (t * 0.8 + k / 16) % 1
            x = 80 + (k * 67) % 920
            pegar_glow(img, x, y - 600 * fz, 110 * (1 - fz) + 30, "#ff8a30", 0.8 * (1 - fz))
        pegar_glow(img, 540, y - 100, 500, "#ff6020", 0.4 + 0.1 * math.sin(t * 9))
    return f


@prop("lingotes", "L")
def p_lingotes(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1500)
    for fila in range(3):
        for k in range(5 - fila):
            xx = x - 220 + fila * 50 + k * 100
            yy = y - fila * 46
            L.forma([(xx - 44, yy), (xx + 44, yy), (xx + 34, yy - 44), (xx - 34, yy - 44)], (230, 186, 60), suave=False,
                    intensidad=0.25, ancho=2)


@prop("hidrofono", "L")
def p_hidrofono(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 300), _n(nums, 1, 1200)
    L.linea([(x, 0), (x, y - 80)], (60, 60, 64), 6)
    L.forma(catmull([(x - 50, y - 80), (x + 50, y - 80), (x + 60, y + 60), (x - 60, y + 60)], 4), (220, 200, 60),
            intensidad=0.2)


@prop("ondas", "dyn")
def p_ondas(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1000)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        for k in range(5):
            r = ((t * 260 + k * 160) % 800)
            d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), outline=(150, 220, 255, int(200 * (1 - r / 800))), width=6)
    return f


@prop("cuerdas_moai", "dyn")
def p_cuerdas(sc, nums, flags, kw):
    """El moái «camina»: se balancea de lado a lado tirado con cuerdas."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1450)
    Lz = LienzoReal(500, 760, 250, 740)
    piedra = (96, 86, 80)
    hh = 560
    Lz.forma([(-75, 0), (-85, -hh * 0.55), (-65, -hh), (65, -hh), (85, -hh * 0.55), (75, 0)], piedra, suave=False,
             intensidad=0.16, textura=0.22)
    Lz.forma([(-70, -hh + 40), (70, -hh + 40), (66, -hh + 100), (-66, -hh + 100)], oscuro(piedra, 0.7), suave=False,
             borde=False)
    spr = Lz.final()
    def f(img, t, dur):
        ang = 7 * math.sin(t * 2.2)
        m = spr.rotate(ang, resample=Image.BICUBIC, center=(250, 740))
        xx = x - 60 + t * 18
        img.alpha_composite(m, (int(xx - 250), int(y - 740)))
        d = ImageDraw.Draw(img)
        for lado, px in ((-1, 120), (1, 960)):
            d.line((xx + lado * 40, y - 420, px, y - 120 + 30 * math.sin(t * 2.2 * lado)), fill=(170, 140, 90), width=6)
    return f


@prop("billetes", "dyn")
def p_billetes(sc, nums, flags, kw):
    def f(img, t, dur):
        r = random.Random(2)
        d = ImageDraw.Draw(img)
        for _ in range(16):
            x = r.uniform(0, W)
            y = (r.uniform(0, H) + t * 180) % H
            d.rectangle((x - 40, y - 20, x + 40, y + 20), fill=(120, 170, 110), outline=(60, 90, 50))
    return f
