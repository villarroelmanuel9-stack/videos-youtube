"""Más elementos para escenas a medida (objetos históricos, lugares y personajes de cada misterio)."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import pro
from alcatraz import maquina
from cine import pegar_glow
from dinos import TINTA, catmull, claro, elipse, oscuro, sombra_suave
from escenario import _col, _escalar, _n, prop
from escenario_obj import _txt
from mis_kits import PERSONAS
from pro import H, W, manuscrita
from realista import LienzoReal

# --------------------------------------------------------------------------- #
# vestuario de época para los personajes de cada historia
# --------------------------------------------------------------------------- #
PERSONAS.update({
    "piloto": dict(ropa=(110, 84, 54), pantalon=(80, 70, 56), sombrero="casco_aviador", bufanda=(236, 232, 220)),
    "marinero": dict(ropa=(40, 50, 80), pantalon=(36, 44, 70), sombrero="gorro_lana", color_sombrero=(40, 50, 80)),
    "capitan": dict(ropa=(30, 36, 60), pantalon=(30, 36, 60), barba=True, pelo=(120, 110, 100), sombrero="fedora",
                    color_sombrero=(30, 36, 60)),
    "cientifico": dict(ropa=(240, 240, 236), pantalon=(80, 84, 96), lentes=True, pelo=(90, 70, 50)),
    "arqueologo": dict(ropa=(186, 164, 120), pantalon=(130, 116, 86), sombrero="chupalla", color_sombrero=(170, 150, 110)),
    "abogada": dict(ropa=(186, 164, 120), vestido=False, pantalon=(120, 110, 90), peinado="largo", pelo=(40, 30, 24),
                    sombrero="chupalla", color_sombrero=(200, 180, 140)),
    "policia": dict(ropa=(30, 36, 60), pantalon=(30, 36, 60), sombrero="gorra_tommy", color_sombrero=(30, 36, 60)),
    "soldado": dict(ropa=(90, 96, 62), pantalon=(80, 86, 56), sombrero="gorra_tommy", color_sombrero=(80, 86, 56)),
    "trabajador": dict(ropa=(60, 90, 140), pantalon=(50, 60, 80), sombrero="gorro_lana", color_sombrero=(170, 60, 40)),
    "cazador": dict(ropa=(110, 70, 50), pantalon=(70, 60, 50), sombrero="gorro_lana", color_sombrero=(90, 70, 50),
                    barba=True),
    "cazador_antiguo": dict(ropa=(120, 90, 60), pantalon=(100, 76, 50), sombrero="gorro_lana", color_sombrero=(110, 80, 50),
                            barba=True, pelo=(60, 40, 30)),
    "nadador": dict(ropa=(214, 170, 136), pantalon=(30, 40, 80), pelo=(90, 80, 70), descalzo_der=True),
    "nino": dict(ropa=(170, 60, 50), pantalon=(60, 70, 100), pelo=(150, 100, 50), cabeza=1.25),
    "nina": dict(ropa=(200, 150, 70), vestido=True, peinado="largo", pelo=(150, 100, 50), cabeza=1.25),
    "principe": dict(ropa=(60, 40, 110), pantalon=(40, 30, 60), pelo=(200, 160, 90), cabeza=1.25, cinturon=True),
    "rey": dict(ropa=(140, 30, 40), pantalon=(60, 30, 30), barba=True, pelo=(90, 60, 40), cinturon=True),
    "reina": dict(ropa=(170, 150, 210), vestido=True, peinado="largo", pelo=(236, 230, 220)),
    "romano": dict(ropa=(170, 40, 40), pantalon=(200, 190, 170), pelo=(60, 44, 30), cinturon=True),
    "sabio": dict(ropa=(226, 220, 200), vestido=True, barba=True, pelo=(220, 220, 214)),
    "monje": dict(ropa=(80, 60, 44), vestido=True, pelo=(120, 100, 80)),
    "guerrero": dict(ropa=(110, 60, 40), pantalon=(70, 50, 40), sombrero="gorro_lana", color_sombrero=(120, 90, 50),
                     barba=True),
    "conquistador": dict(ropa=(150, 150, 156), pantalon=(90, 60, 40), barba=True, cinturon=True),
    "maya": dict(ropa=(200, 60, 80), vestido=True, peinado="largo", pelo=(20, 18, 18), piel=(176, 120, 86)),
    "azteca": dict(ropa=(230, 220, 190), pantalon=(150, 60, 40), piel=(176, 120, 86), pelo=(20, 18, 18)),
    "inca": dict(ropa=(170, 50, 40), pantalon=(200, 160, 60), piel=(176, 120, 86), pelo=(20, 18, 18)),
    "jefe_dorado": dict(ropa=(230, 186, 60), pantalon=(220, 176, 50), piel=(230, 186, 70), pelo=(30, 24, 20)),
    "campesina": dict(ropa=(110, 90, 120), vestido=True, peinado="largo", pelo=(110, 70, 40), bufanda=(236, 230, 210)),
    "indigena": dict(ropa=(170, 120, 80), pantalon=(120, 80, 50), piel=(170, 116, 80), pelo=(20, 18, 18)),
    "turista": dict(ropa=(60, 140, 190), pantalon=(80, 80, 90), lentes=True),
})


def _P(x, y, s):
    return lambda a, b: (x + a * s, y + b * s)


@prop("constelacion", "dyn")
def p_constelacion(sc, nums, flags, kw):
    """Sagitario (la «tetera») con sus estrellas principales."""
    pts = [(380, 760), (520, 700), (620, 780), (560, 900), (420, 900), (680, 620), (760, 700), (300, 840)]
    lineas = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (1, 5), (5, 6), (6, 2), (0, 7)]
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        k = min(1.0, t / 1.5)
        for a, b in lineas:
            (x0, y0), (x1, y1) = pts[a], pts[b]
            d.line((x0, y0, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k), fill=(150, 200, 255, 160), width=3)
        for i, (x, y) in enumerate(pts):
            pegar_glow(img, x, y, 26, "#e0ecff", 0.8 + 0.2 * math.sin(t * 3 + i))
        d.text((540, 1020), "SAGITARIO", font=maquina(48), fill=(170, 210, 255), anchor="mm")
        pegar_glow(img, 620 + 10 * math.sin(t * 9), 760, 40 + 30 * abs(math.sin(t * 4)), "#ff6060", 0.7)
    return f


@prop("plantas_raras", "L")
def p_plantas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1500)
    rr = random.Random(5)
    for k in range(4):
        x = 160 + k * 250
        L.linea(catmull([(x, y), (x + 20, y - 300), (x - 30, y - 520), (x + 10, y - 700)], 5, cerrado=False),
                (90, 120, 60), 14)
        for j in range(5):
            yy = y - 150 - j * 110
            L.forma(elipse(x + (60 if j % 2 else -60), yy, 70, 30, 0.5 if j % 2 else -0.5), (110, 150, 70), intensidad=0.15)
        L.forma(elipse(x + 10, y - 740, 70, 70), rr.choice([(200, 70, 90), (90, 70, 200), (230, 170, 60)]),
                intensidad=0.2, textura=0.1)
        L.forma(elipse(x, y + 30, 90, 40), (150, 100, 70), intensidad=0.1)  # raíces en forma de bulbo


@prop("libro", "img")
def p_libro(sc, img, nums, flags, kw):
    """Libro abierto con un código escrito a mano en la contratapa."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1000)
    d = ImageDraw.Draw(img)
    d.polygon([(x - 420, y - 300), (x, y - 260), (x + 420, y - 300), (x + 420, y + 300), (x, y + 340), (x - 420, y + 300)],
              fill=(80, 50, 30))
    d.polygon([(x - 390, y - 280), (x - 10, y - 240), (x - 10, y + 310), (x - 390, y + 280)], fill=(240, 232, 210))
    d.polygon([(x + 10, y - 240), (x + 390, y - 280), (x + 390, y + 280), (x + 10, y + 310)], fill=(236, 228, 206))
    codigo = kw.get("txt", "WRGOABABD MLIAOI WTBIMPANETP MLIABOAIAQC ITTMTSAMSTGAB").split()
    for k, ln in enumerate(codigo):
        d.text((x + 40, y - 200 + k * 90), ln, font=manuscrita(46), fill=(40, 40, 90))
    for k in range(10):
        d.line((x - 360, y - 200 + k * 46, x - 50, y - 200 + k * 46), fill=(150, 140, 120), width=5)


@prop("humo", "dyn")
def p_humo(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1300)
    def f(img, t, dur):
        for k in range(8):
            fz = (t * 0.25 + k / 8) % 1
            pegar_glow(img, x + 80 * math.sin(fz * 3 + k), y - 700 * fz, 70 + 160 * fz, "#7a7a80", 0.45 * (1 - fz))
    return f


@prop("cuarto_oscuro", "img")
def p_cuarto_oscuro(sc, img, nums, flags, kw):
    """Fotos reveladas colgando: el globo caído sobre el hielo (las fotos de Andrée)."""
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(40, 10, 10))
    pegar_glow(img, 540, 200, 600, "#ff2020", 0.45)
    d.line((0, 520, W, 480), fill=(200, 190, 170), width=4)
    for k in range(3):
        x = 220 + k * 320
        foto = Image.new("RGBA", (260, 340), (226, 214, 186, 255))
        df = ImageDraw.Draw(foto)
        df.rectangle((16, 16, 244, 300), fill=(150, 140, 120))
        df.rectangle((16, 200, 244, 300), fill=(210, 206, 196))
        if k == 1:
            df.ellipse((80, 80, 190, 190), fill=(90, 84, 74))
            df.polygon([(60, 210), (210, 210), (190, 230), (80, 230)], fill=(90, 84, 74))
        else:
            df.rectangle((60 + k * 20, 150, 120 + k * 20, 220), fill=(80, 74, 64))
            df.ellipse((70 + k * 20, 120, 110 + k * 20, 160), fill=(80, 74, 64))
        foto = foto.rotate((k - 1) * 4, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(foto, (int(x - foto.width / 2), 500 - k * 14))
        d.rectangle((x - 14, 480 - k * 14, x + 14, 520 - k * 14), fill=(170, 160, 150))


@prop("pizarra", "L")
def p_pizarra(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 700)
    L.forma([(x - 420, y - 280), (x + 420, y - 280), (x + 420, y + 280), (x - 420, y + 280)], (34, 54, 44), suave=False,
            intensidad=0.04, textura=0.12)
    L.linea([(x - 430, y + 290), (x + 430, y + 290)], (120, 80, 50), 18)
    rr = random.Random(7)
    for k in range(6):
        L.linea([(x - 360 + rr.uniform(0, 80), y - 200 + k * 80), (x + rr.uniform(0, 330), y - 200 + k * 80)],
                (220, 226, 220), 5)
    sc.ctx.setdefault("_textos_pizarra", []).append((x, y))


@prop("formulas", "img")
def p_formulas(sc, img, nums, flags, kw):
    d = ImageDraw.Draw(img)
    for x, y in sc.ctx.pop("_textos_pizarra", []):
        for k, txt in enumerate(("ψ = Σ cₙ φₙ", "E = mc²", "m ν ≠ m ν̄", "Hₙ ψ = E ψ")):
            d.text((x - 360, y - 230 + k * 120), txt, font=manuscrita(64), fill=(236, 240, 236))


@prop("telas", "L")
def p_telas(sc, L, nums, flags, kw):
    """Telas de seda tailandesa colgadas (el «rey de la seda»)."""
    cols = [(200, 40, 80), (240, 170, 30), (40, 120, 180), (120, 50, 150), (30, 150, 110), (220, 90, 40)]
    L.linea([(0, 300), (W, 300)], (90, 60, 40), 16)
    for k, c in enumerate(cols):
        x = 40 + k * 170
        L.forma(catmull([(x, 300), (x + 160, 300), (x + 170, 900), (x + 150, 1400), (x + 10, 1420), (x - 10, 900)], 4), c,
                intensidad=0.18, textura=0.06)


@prop("recepcion", "L")
def p_recepcion(sc, L, nums, flags, kw):
    """Mostrador de hotel de los años 20 con casilleros de llaves."""
    L.forma([(160, 300), (920, 300), (920, 800), (160, 800)], (90, 60, 40), suave=False, intensidad=0.05)
    for k in range(5):
        for j in range(8):
            L.forma([(190 + j * 90, 330 + k * 92), (260 + j * 90, 330 + k * 92), (260 + j * 90, 400 + k * 92),
                     (190 + j * 90, 400 + k * 92)], (60, 40, 26), suave=False, borde=False)
            if (k + j) % 3 == 0:
                L.linea([(225 + j * 90, 350 + k * 92), (225 + j * 90, 385 + k * 92)], (220, 180, 70), 5)
    L.forma([(60, 1250), (1020, 1250), (1020, 1500), (60, 1500)], (120, 80, 50), suave=False, intensidad=0.08, textura=0.14)
    L.forma([(40, 1230), (1040, 1230), (1040, 1260), (40, 1260)], (70, 46, 30), suave=False)
    L.forma(elipse(820, 1215, 34, 20), (220, 180, 70), intensidad=0.3)


@prop("camion", "L")
def p_camion(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1500), _n(nums, 2, 1.0)
    P = _P(x, y, s)
    c = _col(kw, (40, 70, 120))
    L.forma([P(-420, 0), P(220, 0), P(220, -320), P(-420, -320)], (210, 210, 214), suave=False, intensidad=0.08, textura=0.08)
    L.forma([P(230, 0), P(430, 0), P(430, -150), P(380, -260), P(230, -260)], c, suave=False, intensidad=0.12)
    L.forma([P(260, -240), P(370, -240), P(410, -160), P(260, -160)], (140, 170, 200), suave=False)
    for dx in (-330, -200, 320):
        L.forma(elipse(x + dx * s, y + 10 * s, 52 * s, 52 * s), (26, 26, 28), intensidad=0.2)


@prop("corona", "L")
def p_corona(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1000), _n(nums, 2, 1.0)
    P = _P(x, y, s)
    L.forma(elipse(x, y + 60 * s, 260 * s, 70 * s), (130, 30, 50), intensidad=0.2, textura=0.1)
    L.forma([P(-170, 30), P(-200, -170), P(-100, -60), P(0, -220), P(100, -60), P(200, -170), P(170, 30)],
            (230, 186, 60), suave=False, intensidad=0.3)
    for dx, c in ((-120, (200, 30, 40)), (0, (40, 90, 200)), (120, (30, 150, 80))):
        L.circulo(x + dx * s, y - 10 * s, 18 * s, c, ancho=2)


@prop("afiche", "L")
def p_afiche(sc, L, nums, flags, kw):
    """Afiche con una cigarra pegado en un poste (las pistas de Cicada en la calle)."""
    x, y = _n(nums, 0, 700), _n(nums, 1, 1000)
    L.linea([(x, y + 700), (x, y - 500)], (60, 60, 66), 22)
    L.forma([(x - 170, y - 220), (x + 170, y - 230), (x + 175, y + 220), (x - 165, y + 230)], (236, 232, 220), suave=False,
            intensidad=0.05)
    L.forma(elipse(x, y - 20, 34, 110), (40, 40, 44), intensidad=0.1)
    for lado in (-1, 1):
        L.forma([(x, y - 70), (x + lado * 140, y - 110), (x + lado * 150, y + 20), (x, y - 10)], (90, 90, 96), suave=False)
    for k in range(6):
        for j in range(6):
            if (k * 7 + j * 3) % 4:
                L.forma([(x - 120 + j * 28, y + 120 + k * 16), (x - 96 + j * 28, y + 120 + k * 16),
                         (x - 96 + j * 28, y + 134 + k * 16), (x - 120 + j * 28, y + 134 + k * 16)], (20, 20, 20),
                        suave=False, borde=False)


@prop("cigarra", "dyn")
def p_cigarra(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 900)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.ellipse((x - 50, y - 160, x + 50, y + 160), fill=(220, 220, 220))
        for lado in (-1, 1):
            d.polygon([(x, y - 90), (x + lado * 300, y - 150), (x + lado * 330, y + 90), (x, y + 30)], fill=(170, 170, 170, 220))
        d.text((x, y + 260), "3301", font=maquina(70), fill=(230, 230, 230), anchor="mm")
        pegar_glow(img, x, y, 360, "#a0ffa0", 0.15 + 0.1 * math.sin(t * 3))
    return f


@prop("radiografia", "img")
def p_radiografia(sc, img, nums, flags, kw):
    """Negatoscopio con la radiografía del hombro y la punta de flecha de Ötzi."""
    d = ImageDraw.Draw(img)
    d.rectangle((140, 360, 940, 1300), fill=(200, 220, 236))
    pegar_glow(img, 540, 830, 500, "#d8ecff", 0.5)
    d.rectangle((200, 420, 880, 1240), fill=(20, 26, 34))
    hueso = (210, 220, 226)
    d.line((300, 600, 760, 520), fill=hueso, width=26)  # clavícula
    d.ellipse((560, 560, 760, 760), outline=hueso, width=20)  # omóplato
    d.line((660, 760, 640, 1200), fill=hueso, width=40)  # húmero
    for k in range(6):
        d.arc((240, 640 + k * 90, 620, 760 + k * 90), 200, 340, fill=hueso, width=12)
    d.polygon([(600, 700), (660, 660), (640, 730)], fill=(255, 255, 255))
    pegar_glow(img, 630, 700, 60, "#ffffff", 0.7)
    d.ellipse((560, 620, 720, 780), outline=(240, 40, 40), width=8)


@prop("sarcofago", "L")
def p_sarcofago(sc, L, nums, flags, kw):
    x, y, s = _n(nums, 0, 540), _n(nums, 1, 1550), _n(nums, 2, 1.0)
    oro = (220, 176, 70) if "oro" in flags else (190, 176, 150)
    P = _P(x, y, s)
    L.forma([P(-380, 0), P(380, 0), P(360, -240), P(-360, -240)], oscuro(oro, 0.8), suave=False, intensidad=0.12, textura=0.12)
    L.forma(catmull([P(-360, -240), P(-300, -340), P(300, -340), P(360, -240)], 4), oro, intensidad=0.2, textura=0.1)
    L.forma(elipse(x + 260 * s, y - 300 * s, 60 * s, 46 * s), oscuro(oro, 0.9), intensidad=0.2)
    for k in range(6):
        L.linea([P(-300 + k * 100, -230), P(-300 + k * 100, -20)], oscuro(oro, 0.6), 4)


@prop("tunel", "L")
def p_tunel(sc, L, nums, flags, kw):
    c = (110, 90, 70)
    L.d.rectangle((0, 0, W * 2, H * 2), fill=(30, 24, 20))
    for k in range(6):
        f = 1 - k * 0.15
        w, h = 900 * f, 1300 * f
        L.forma(catmull([(540 - w / 2, 1500 - (1 - f) * 300), (540 - w / 2, 1500 - h * 0.6 - (1 - f) * 300),
                         (540, 1500 - h - (1 - f) * 300), (540 + w / 2, 1500 - h * 0.6 - (1 - f) * 300),
                         (540 + w / 2, 1500 - (1 - f) * 300)], 5), oscuro(c, 0.9 - k * 0.12), borde=False, textura=0.2,
                intensidad=0.04)


@prop("grietas", "L")
def p_grietas(sc, L, nums, flags, kw):
    y = _n(nums, 0, 1300)
    rr = random.Random(3)
    for _ in range(40):
        x0, y0 = rr.uniform(0, W), rr.uniform(y + 20, H)
        pts = [(x0, y0)]
        for _k in range(4):
            x0 += rr.uniform(-80, 80)
            y0 += rr.uniform(-40, 40)
            pts.append((x0, y0))
        L.linea(pts, (80, 56, 40), 5)


@prop("balsa", "L")
def p_balsa(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1300)
    for k in range(7):
        L.forma(elipse(x - 300 + k * 100, y, 50, 26), (140, 100, 60), intensidad=0.2, textura=0.2)
    L.linea([(x - 340, y - 10), (x + 340, y - 10)], (90, 60, 40), 8)


@prop("balsa_oro", "dyn")
def p_balsa_oro(sc, nums, flags, kw):
    """Balsa de la ceremonia muisca: el cacique cubierto de oro y ofrendas al agua."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1300)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        xx = x + 30 * math.sin(t * 0.4)
        d.polygon([(xx - 260, y), (xx + 260, y), (xx + 220, y + 50), (xx - 220, y + 50)], fill=(150, 110, 40))
        pegar_glow(img, xx, y - 120, 260, "#ffd050", 0.6 + 0.2 * math.sin(t * 3))
        d.rounded_rectangle((xx - 34, y - 200, xx + 34, y), radius=30, fill=(240, 190, 60))
        d.ellipse((xx - 30, y - 260, xx + 30, y - 196), fill=(240, 190, 60))
        for k in range(8):
            fz = (t * 0.5 + k / 8) % 1
            pegar_glow(img, xx - 120 + k * 34, y + 30 + 110 * fz, 8, "#ffe080", 1 - fz)
    return f


@prop("arrastre", "dyn", sonido=[("raspado", 0.3, 3.0)])
def p_arrastre(sc, nums, flags, kw):
    """Gente tirando de una piedra gigante sobre un trineo de madera."""
    y = _n(nums, 0, 1550)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        xx = 700 - t * 25
        d.polygon([(xx - 160, y), (xx + 160, y), (xx + 140, y - 380), (xx - 130, y - 400)], fill=(140, 136, 126))
        d.rectangle((xx - 200, y, xx + 200, y + 30), fill=(110, 80, 50))
        for k in range(4):
            d.ellipse((xx - 180 + k * 120, y + 30, xx - 140 + k * 120, y + 70), fill=(90, 64, 40))
        for k in range(5):
            px = xx - 300 - k * 110
            d.line((xx - 160, y - 200, px, y - 120), fill=(170, 140, 90), width=5)
            from alcatraz import silueta
            silueta(d, px, y + 40, 0.5, t * 0.7 + k, agachado=True, col=(20, 20, 24))
    return f


@prop("bloque", "L")
def p_bloque(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1500)
    L.forma([(x - 380, y), (x + 380, y - 20), (x + 360, y - 160), (x - 360, y - 150)], (150, 120, 110), suave=False,
            intensidad=0.16, textura=0.24)


@prop("pilar", "L")
def p_pilar(sc, L, nums, flags, kw):
    """Primer plano de un pilar en T de Göbekli Tepe con un zorro y un jabalí tallados."""
    piedra = (196, 170, 132)
    L.forma([(380, 1600), (380, 700), (700, 700), (700, 1600)], piedra, suave=False, intensidad=0.12, textura=0.24)
    L.forma([(220, 700), (860, 700), (860, 480), (220, 480)], piedra, suave=False, intensidad=0.12, textura=0.24)
    t = oscuro(piedra, 0.55)
    L.linea(catmull([(420, 900), (520, 840), (640, 880), (660, 960), (560, 1000), (450, 980)], 5), t, 8)
    L.linea([(640, 880), (680, 830)], t, 8)
    L.linea(catmull([(430, 1200), (530, 1150), (650, 1190), (640, 1290), (450, 1300)], 5), t, 8)
    for x in (460, 520, 590, 630):
        L.linea([(x, 1290), (x, 1360)], t, 7)


@prop("cantera", "L")
def p_cantera(sc, L, nums, flags, kw):
    """Ladera de la cantera Rano Raraku con moáis a medio tallar."""
    L.forma(catmull([(-60, 1500), (200, 900), (600, 800), (W + 60, 1000), (W + 60, H), (-60, H)], 5), (120, 110, 90),
            borde=False, textura=0.2)
    for x, y, s in ((300, 1300, 0.7), (620, 1150, 0.6), (860, 1250, 0.5)):
        L.forma([(x - 60 * s * 1.5, y), (x - 50 * s * 1.5, y - 300 * s * 1.5), (x + 50 * s * 1.5, y - 300 * s * 1.5),
                 (x + 60 * s * 1.5, y)], (96, 86, 80), suave=False, intensidad=0.16, textura=0.2)


@prop("laberinto", "L")
def p_laberinto(sc, L, nums, flags, kw):
    L.d.rectangle((0, 0, W * 2, H * 2), fill=(190, 160, 120))
    c = (110, 80, 54)
    for k in range(7):
        m = 80 + k * 60
        L.linea([(m, m + 300), (W - m, m + 300), (W - m, H - m - 300), (m, H - m - 300), (m, m + 400 + k * 20)], c, 22)
    sc.ctx["_minotauro"] = True


@prop("minoico", "L")
def p_minoico(sc, L, nums, flags, kw):
    """Palacio minoico: columnas rojas que se angostan hacia abajo, con capiteles negros."""
    y = _n(nums, 0, 1350)
    L.forma([(60, y - 760), (1020, y - 760), (1020, y - 660), (60, y - 660)], (226, 210, 170), suave=False, intensidad=0.1)
    L.forma([(60, y - 660), (1020, y - 660), (1020, y - 620), (60, y - 620)], (40, 30, 30), suave=False)
    for k in range(5):
        x = 150 + k * 195
        L.forma([(x - 46, y - 620), (x + 46, y - 620), (x + 32, y), (x - 32, y)], (170, 40, 36), suave=False,
                intensidad=0.14, textura=0.1)
        L.forma(elipse(x, y - 640, 66, 30), (30, 26, 26), intensidad=0.2)
    L.forma([(0, y), (W, y), (W, H), (0, H)], (200, 180, 140), suave=False, borde=False, textura=0.14)


@prop("estampar", "dyn", sonido=[("golpe", 0.6, 0.4), ("golpe", 1.6, 0.4), ("golpe", 2.6, 0.4)])
def p_estampar(sc, nums, flags, kw):
    """Un sello de madera estampa símbolos en arcilla fresca, uno tras otro."""
    signos = "ΨΦΔΩЖЯ†§λΠ"
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        d.ellipse((140, 700, 940, 1500), fill=(196, 146, 96), outline=(120, 80, 50), width=10)
        n = int(t)
        for k in range(n):
            a = k * 0.8
            x, y = 540 + 260 * math.cos(a) * (1 - k * 0.05), 1100 + 260 * math.sin(a) * (1 - k * 0.05)
            d.text((x, y), signos[k % len(signos)], font=pro.fuente(70), fill=(110, 70, 40), anchor="mm")
        a = n * 0.8
        x, y = 540 + 260 * math.cos(a) * (1 - n * 0.05), 1100 + 260 * math.sin(a) * (1 - n * 0.05)
        sube = abs(math.sin((t % 1) * math.pi))
        d.rectangle((x - 50, y - 300 - 200 * sube, x + 50, y - 60 - 200 * sube), fill=(120, 84, 50))
        d.rectangle((x - 70, y - 60 - 200 * sube, x + 70, y - 20 - 200 * sube), fill=(90, 60, 36))
    return f


@prop("mapa_piri", "img")
def p_mapa_piri(sc, img, nums, flags, kw):
    """El mapa de Piri Reis: pergamino de gacela con costas, rosas de los vientos y barcos dibujados."""
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(60, 40, 26))
    d.polygon([(90, 260), (990, 240), (1010, 1500), (70, 1520)], fill=(222, 196, 150))
    d.line([(820, 320), (790, 520), (840, 700), (800, 900), (860, 1100)], fill=(120, 70, 40), width=8)  # África
    d.line([(160, 420), (300, 520), (360, 760), (330, 1000), (420, 1200), (560, 1380), (900, 1400)], fill=(120, 70, 40),
           width=8)  # Sudamérica y la costa del sur
    for cx, cy in ((560, 600), (600, 1100)):
        for k in range(16):
            a = k * math.pi / 8
            d.line((cx, cy, cx + 260 * math.cos(a), cy + 260 * math.sin(a)), fill=(170, 60, 50, 120), width=2)
    for x, y in ((520, 400), (620, 860)):
        d.polygon([(x - 50, y), (x + 50, y), (x + 36, y + 24), (x - 36, y + 24)], fill=(110, 60, 30))
        d.line((x, y, x, y - 60), fill=(110, 60, 30), width=4)
        d.polygon([(x, y - 60), (x + 40, y - 20), (x, y - 10)], fill=(240, 230, 210))
    for k in range(6):
        d.text((200 + k * 120, 300 + (k % 2) * 30), "ﺍﻟﺒﺤﺮ"[:1] if False else "~", font=pro.fuente(40), fill=(120, 70, 40))


@prop("negativo", "img")
def p_negativo(sc, img, nums, flags, kw):
    """Invierte lo dibujado hasta ahora (la imagen de la sábana se ve mejor en negativo)."""
    rgb = ImageOps.invert(img.convert("RGB"))
    img.paste(rgb.convert("RGBA"), (0, 0), img.getchannel("A"))


@prop("cueva_entrada", "L")
def p_cueva_entrada(sc, L, nums, flags, kw):
    L.forma(catmull([(-60, 1500), (100, 600), (500, 520), (1000, 700), (W + 60, 1500)], 5), (170, 130, 96), borde=False,
            textura=0.22, intensidad=0.08)
    L.forma(catmull([(380, 1250), (420, 1000), (560, 960), (680, 1020), (700, 1250)], 5), (30, 22, 18), borde=False)


@prop("declaracion", "img")
def p_declaracion(sc, img, nums, flags, kw):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(70, 50, 34))
    d.rectangle((120, 260, 960, 1500), fill=(226, 208, 168))
    d.text((540, 340), "IN CONGRESS, JULY 4, 1776", font=maquina(40), fill=(60, 44, 30), anchor="mm")
    d.text((540, 440), "The unanimous Declaration", font=manuscrita(60), fill=(60, 44, 30), anchor="mm")
    for k in range(18):
        d.line((180, 540 + k * 44, 900, 540 + k * 44), fill=(150, 130, 100), width=5)
    for k in range(5):
        d.text((260 + k * 140, 1400), "~~", font=manuscrita(60), fill=(60, 44, 30), anchor="mm")


@prop("piano", "L")
def p_piano(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1500)
    L.forma([(x - 400, y), (x + 400, y), (x + 400, y - 560), (x - 400, y - 560)], (30, 24, 22), suave=False, intensidad=0.12)
    L.forma([(x - 380, y - 300), (x + 380, y - 300), (x + 380, y - 250), (x - 380, y - 250)], (240, 236, 226), suave=False)
    for k in range(30):
        L.linea([(x - 370 + k * 25, y - 300), (x - 370 + k * 25, y - 250)], (60, 60, 60), 2)
    L.forma([(x - 140, y - 560), (x + 140, y - 560), (x + 120, y - 740), (x - 120, y - 740)], (236, 230, 214), suave=False)
    for k in range(5):
        L.linea([(x - 110, y - 600 - k * 26), (x + 110, y - 600 - k * 26)], (60, 60, 60), 2)


@prop("flores", "L")
def p_flores(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1450)
    L.forma([(x - 70, y), (x + 70, y), (x + 90, y - 200), (x - 90, y - 200)], (100, 140, 170), suave=False, intensidad=0.2)
    for k in range(6):
        a = -math.pi / 2 + (k - 2.5) * 0.35
        fx, fy = x + 220 * math.cos(a), y - 200 + 220 * math.sin(a)
        L.linea([(x, y - 200), (fx, fy)], (60, 110, 50), 6)
        L.forma(elipse(fx, fy, 40, 34), (200, 40, 60), intensidad=0.3)


@prop("caliz", "dyn")
def p_caliz(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1100)
    def f(img, t, dur):
        pegar_glow(img, x, y - 200, 360, "#ffd870", 0.5 + 0.15 * math.sin(t * 2))
        d = ImageDraw.Draw(img)
        d.polygon([(x - 160, y - 380), (x + 160, y - 380), (x + 90, y - 180), (x - 90, y - 180)], fill=(220, 176, 70))
        d.rectangle((x - 20, y - 180, x + 20, y - 40), fill=(200, 156, 60))
        d.ellipse((x - 130, y - 60, x + 130, y), fill=(200, 156, 60))
    return f


@prop("globo_meteo", "dyn")
def p_globo_meteo(sc, nums, flags, kw):
    """Globo con reflectores de aluminio: el meteorológico o el del proyecto secreto (Mogul)."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 600)
    largo = "mogul" in flags
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        yy = y - t * 10
        n = 6 if largo else 1
        for k in range(n):
            gy = yy + k * 120
            d.ellipse((x - 70, gy - 70, x + 70, gy + 70), fill=(240, 236, 226), outline=(160, 156, 150), width=3)
            d.line((x, gy + 70, x, gy + 120), fill=(200, 200, 200), width=3)
        base = yy + n * 120
        for k in range(3):
            px = x - 80 + k * 80
            d.polygon([(px, base + 40), (px + 60, base + 20), (px + 50, base + 90), (px - 10, base + 100)],
                      fill=(214, 218, 224), outline=(140, 146, 156))
            pegar_glow(img, px + 25, base + 55, 30, "#ffffff", 0.5 + 0.4 * math.sin(t * 5 + k))
    return f


@prop("podio", "L")
def p_podio(sc, L, nums, flags, kw):
    L.forma([(380, 1700), (700, 1700), (680, 1300), (400, 1300)], (90, 60, 40), suave=False, intensidad=0.12, textura=0.12)
    for k in range(3):
        L.linea([(500 + k * 40, 1300), (520 + k * 40, 1220)], (40, 40, 44), 8)
        L.circulo(520 + k * 40, 1210, 14, (40, 40, 44), borde=False)


@prop("bengalas", "dyn")
def p_bengalas(sc, nums, flags, kw):
    def f(img, t, dur):
        for k in range(7):
            x = 200 + k * 110
            y = 500 + k * 15 + t * 40
            pegar_glow(img, x, y, 50, "#ffd080", 0.9)
            pegar_glow(img, x, y - 120, 30, "#ffffff", 0.25)
    return f


@prop("coyote", "dyn")
def p_coyote(sc, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1600)
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        xx = x - t * 30
        c = (120, 100, 80)
        d.ellipse((xx - 140, y - 160, xx + 120, y - 50), fill=c)
        d.polygon([(xx - 120, y - 150), (xx - 230, y - 200), (xx - 250, y - 140), (xx - 150, y - 110)], fill=c)
        d.polygon([(xx - 200, y - 200), (xx - 190, y - 250), (xx - 170, y - 200)], fill=c)
        for dx in (-100, -60, 60, 100):
            d.line((xx + dx, y - 70, xx + dx + 10 * math.sin(t * 8 + dx), y), fill=oscuro(c, 0.7), width=12)
        d.line((xx + 110, y - 120, xx + 200, y - 90), fill=c, width=16)
        for k in range(6):  # calvas de sarna
            d.ellipse((xx - 80 + k * 30, y - 130 + (k % 2) * 30, xx - 60 + k * 30, y - 112 + (k % 2) * 30), fill=(170, 130, 120))
    return f


@prop("postes_asmat", "L")
def p_postes(sc, L, nums, flags, kw):
    """Postes bisj tallados por los asmat."""
    for k, x in enumerate((260, 540, 820)):
        h = 900 - k * 100
        c = (150, 110, 80)
        L.forma([(x - 50, 1600), (x - 40, 1600 - h), (x + 40, 1600 - h), (x + 50, 1600)], c, suave=False, intensidad=0.14,
                textura=0.2)
        for j in range(4):
            y = 1600 - h + 120 + j * (h - 200) / 4
            L.forma(elipse(x, y, 46, 60), oscuro(c, 0.8), intensidad=0.2)
            L.circulo(x - 16, y - 14, 8, (240, 240, 230), borde=False)
            L.circulo(x + 16, y - 14, 8, (240, 240, 230), borde=False)
        L.forma([(x + 40, 1600 - h), (x + 220, 1600 - h - 40), (x + 40, 1600 - h + 60)], c, suave=False, intensidad=0.14)


@prop("lidar", "dyn")
def p_lidar(sc, nums, flags, kw):
    """Barrido láser desde el avión que revela ruinas bajo la selva."""
    def f(img, t, dur):
        d = ImageDraw.Draw(img)
        x = 200 + t * 140
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(capa).polygon([(x, 560), (x - 260, 1600), (x + 260, 1600)], fill=(80, 255, 140, 50))
        img.alpha_composite(capa)
        for k in range(int((x - 200) / 40)):
            px = 260 + k * 40
            if px < x:
                d.line((px - 20, 1500 - (k % 4) * 30, px + 20, 1500 - (k % 4) * 30), fill=(120, 255, 160), width=6)
    return f


@prop("paquete", "L")
def p_paquete(sc, L, nums, flags, kw):
    """El paquete de correo común en que viajó el diamante Hope (1958)."""
    x, y = _n(nums, 0, 540), _n(nums, 1, 1300)
    L.forma([(x - 320, y), (x + 320, y), (x + 360, y - 300), (x - 280, y - 300)], (190, 150, 100), suave=False,
            intensidad=0.12, textura=0.14)
    L.linea([(x - 300, y - 150), (x + 340, y - 150)], (160, 110, 60), 14)
    L.linea([(x + 20, y), (x + 60, y - 300)], (160, 110, 60), 14)
    L.forma([(x - 240, y - 260), (x - 60, y - 260), (x - 60, y - 180), (x - 240, y - 180)], (240, 236, 226), suave=False)
    for k in range(3):
        L.forma([(x + 150 + k * 50, y - 280), (x + 190 + k * 50, y - 280), (x + 190 + k * 50, y - 230),
                 (x + 150 + k * 50, y - 230)], (60, 90, 170) if k % 2 else (190, 40, 40), suave=False, borde=False)


@prop("antena", "L")
def p_antena(sc, L, nums, flags, kw):
    x, y = _n(nums, 0, 540), _n(nums, 1, 1350)
    c = (180, 60, 50)
    L.linea([(x - 120, y), (x, y - 1000)], c, 10)
    L.linea([(x + 120, y), (x, y - 1000)], c, 10)
    for k in range(10):
        yy = y - k * 100
        w = 120 * (1 - k / 10)
        L.linea([(x - w, yy), (x + w, yy - 100)], c, 5)
        L.linea([(x + w, yy), (x - w, yy - 100)], c, 5)


@prop("rejilla_desagues", "L")
def p_desagues(sc, L, nums, flags, kw):
    """Calle de ladrillo de Mohenjo-daro con su canal de desagüe."""
    y = _n(nums, 0, 1350)
    L.forma([(0, y), (W, y), (W, H), (0, H)], (176, 120, 86), suave=False, borde=False, textura=0.2)
    for yy in range(int(y) + 20, H, 40):
        for xx in range(0, W, 90):
            L.linea([(xx + (yy // 40 % 2) * 45, yy), (xx + (yy // 40 % 2) * 45, yy + 40)], (140, 90, 64), 3)
        L.linea([(0, yy), (W, yy)], (140, 90, 64), 3)
    L.forma([(440, y), (640, y), (760, H), (320, H)], (90, 70, 56), suave=False)
    L.forma([(470, y), (610, y), (710, H), (370, H)], (60, 90, 100), suave=False, borde=False)
