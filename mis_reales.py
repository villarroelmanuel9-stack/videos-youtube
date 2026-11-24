"""
Vehículos y objetos "reales" para la serie de misterios: cada avión y barco se dibuja con su modelo y colores
históricos (Avenger azul marino, Boeing 777 blanco con franjas roja y azul, Electra plateado, etc.).
Todos los sprites miran a la derecha; se dibujan una vez y quedan en caché.
"""
from __future__ import annotations

import math

from PIL import Image

from dinos import catmull, claro, elipse, oscuro
from realista import LienzoReal

_cache = {}

# --------------------------------------------------------------------------- #
# AVIONES (vista lateral)
# --------------------------------------------------------------------------- #
AVIONES = {
    # modelo: largo, alto fuselaje, color, panza, franjas[(color, y, alto)], cola, motores, ala, ventanillas, cabina
    "777": dict(L=900, h=96, col=(246, 246, 250), panza=(222, 226, 232), franjas=[((196, 28, 40), 0.18, 0.09),
                                                                                  ((28, 56, 140), 0.3, 0.09)],
                cola="jet", motor="jet", ala="baja", vent=34, livery_cola=((196, 28, 40), (28, 56, 140))),
    "constellation": dict(L=820, h=82, col=(236, 238, 242), panza=(196, 200, 206), franjas=[((34, 70, 150), 0.05, 0.1)],
                          cola="triple", motor="helice", n_mot=2, ala="baja", vent=18, delfin=True),
    "lancastrian": dict(L=720, h=72, col=(206, 210, 216), panza=(186, 190, 196), franjas=[((30, 50, 110), 0.02, 0.08)],
                        cola="doble", motor="helice", n_mot=2, ala="media", vent=8, nariz="punta"),
    "electra": dict(L=540, h=66, col=(214, 218, 224), panza=(190, 194, 200), franjas=[], cola="doble",
                    motor="radial", n_mot=1, ala="baja", vent=5),
    "avenger": dict(L=560, h=92, col=(64, 84, 112), panza=(220, 224, 228), franjas=[], cola="grande", motor="radial",
                    n_mot=1, ala="media", vent=0, cabina="burbuja", estrella=True, nariz_motor=True),
    "norseman": dict(L=480, h=74, col=(92, 98, 62), panza=(84, 90, 58), franjas=[], cola="simple", motor="radial",
                     n_mot=1, ala="alta", vent=3, estrella=True, nariz_motor=True),
    "p38": dict(L=560, h=56, col=(110, 128, 156), panza=(126, 144, 170), franjas=[], cola="oval", motor="helice",
                n_mot=1, ala="media", vent=0, cabina="burbuja", botalon=True),
    "cessna": dict(L=400, h=70, col=(244, 244, 244), panza=(230, 230, 232), franjas=[((186, 30, 40), 0.15, 0.1)],
                   cola="simple", motor="radial", n_mot=1, ala="alta", vent=2, nariz_motor=True),
    "f18": dict(L=560, h=50, col=(150, 158, 168), panza=(170, 176, 186), franjas=[], cola="jet_militar",
                motor="ninguno", ala="media", vent=0, cabina="burbuja", nariz="punta"),
}


def _fuselaje(e):
    L, h = e["L"], e["h"]
    x0, x1 = -L / 2, L / 2
    curva = 0.18 * h if e.get("delfin") else 0.0  # el Constellation tiene forma de delfín
    nariz = e.get("nariz", "redonda")
    top = [(x1 - 0.02 * L, -0.12 * h + curva * 0.6), (x1 - 0.09 * L, -0.42 * h + curva * 0.3),
           (x1 - 0.22 * L, -0.5 * h), (x0 + 0.35 * L, -0.5 * h), (x0 + 0.12 * L, -0.42 * h - curva),
           (x0 + 0.01 * L, -0.32 * h - curva * 1.6)]
    bot = [(x0, -0.18 * h - curva * 1.6), (x0 + 0.1 * L, 0.05 * h - curva * 0.6), (x0 + 0.3 * L, 0.45 * h),
           (x1 - 0.25 * L, 0.5 * h), (x1 - 0.08 * L, 0.36 * h + curva * 0.3)]
    if nariz == "punta":
        top[0] = (x1 + 0.03 * L, 0.05 * h)
    return top + bot


def avion_real(modelo):
    if ("av", modelo) in _cache:
        return _cache[("av", modelo)]
    if modelo == "globo":
        img = _globo()
        _cache[("av", modelo)] = img
        return img
    e = AVIONES[modelo]
    L, h = e["L"], e["h"]
    W_, H_ = int(L * 1.25), int(h * 6.0)
    Lz = LienzoReal(W_, H_, W_ // 2, int(H_ * 0.58))
    x0, x1 = -L / 2, L / 2
    oscuro_ala = oscuro(e["col"], 0.72)
    # ala lejana (se asoma por encima del fuselaje para dar volumen)
    if e["ala"] != "alta":
        Lz.forma([(x0 + 0.42 * L, -0.15 * h), (x0 + 0.62 * L, -0.15 * h), (x0 + 0.5 * L, -0.62 * h),
                  (x0 + 0.44 * L, -0.62 * h)], oscuro(e["col"], 0.62), suave=False, intensidad=0.05, textura=0.04,
                 ancho=3)
    # cola
    cola = e["cola"]
    if cola in ("jet", "grande", "simple", "jet_militar"):
        alto = {"jet": 1.55, "grande": 1.35, "simple": 1.1, "jet_militar": 1.3}[cola]
        barrido = {"jet": 0.13, "grande": 0.05, "simple": 0.06, "jet_militar": 0.12}[cola]
        fin = [(x0 + 0.03 * L, -0.3 * h), (x0 + 0.01 * L - barrido * L * 0.2, -alto * h),
               (x0 + 0.07 * L, -alto * h), (x0 + (0.2 + barrido) * L, -0.45 * h)]
        if cola == "grande":
            fin = catmull(fin, 4)
        mfin = Lz.forma(fin, e["col"], suave=False, intensidad=0.08, textura=0.05, ancho=3)
        if e.get("livery_cola"):
            c1, c2 = e["livery_cola"]
            Lz.forma([(x0, -0.6 * h), (x0 + 0.2 * L, -0.45 * h), (x0 + 0.1 * L, -1.0 * h), (x0, -1.1 * h)], c1,
                     suave=False, clip=mfin, borde=False, intensidad=0.05)
            Lz.forma([(x0, -1.1 * h), (x0 + 0.1 * L, -1.0 * h), (x0 + 0.08 * L, -1.7 * h), (x0, -1.7 * h)], c2,
                     suave=False, clip=mfin, borde=False, intensidad=0.05)
    elif cola in ("doble", "triple", "oval"):
        n = {"doble": 2, "triple": 3, "oval": 1}[cola]
        for k in range(n):
            cx = x0 + 0.04 * L + k * 0.05 * L
            col = oscuro(e["col"], 0.82 - k * 0.04) if k < n - 1 else e["col"]
            Lz.forma(elipse(cx, -0.42 * h + k * 0.06 * h, 0.045 * L, (0.62 if cola != "triple" else 0.5) * h), col,
                     intensidad=0.1, textura=0.05, ancho=3)
    # estabilizador horizontal
    Lz.forma(elipse(x0 + 0.08 * L, -0.12 * h, 0.1 * L, 0.06 * h), oscuro_ala, intensidad=0.05, ancho=3)
    # botalón (P-38): cuerpo largo y fino con la cabina en una góndola aparte
    if e.get("botalon"):
        Lz.forma(catmull([(x0, -0.1 * h), (x0 + 0.5 * L, -0.25 * h), (x1 - 0.12 * L, -0.25 * h), (x1, 0.05 * h),
                          (x1 - 0.12 * L, 0.3 * h), (x0 + 0.5 * L, 0.25 * h), (x0, 0.12 * h)], 4), e["col"],
                 suave=False, intensidad=0.1, textura=0.05)
        g = Lz.forma(catmull([(x0 + 0.38 * L, -0.55 * h), (x1 - 0.2 * L, -0.75 * h), (x1 + 0.04 * L, -0.45 * h),
                              (x1 - 0.2 * L, -0.2 * h), (x0 + 0.38 * L, -0.3 * h)], 4), claro(e["col"], 0.08),
                     suave=False, intensidad=0.12)
        Lz.forma(elipse(x1 - 0.2 * L, -0.78 * h, 0.09 * L, 0.18 * h), (150, 190, 220), intensidad=0.2, ancho=3)
        m = None
    else:
        m = Lz.forma(_fuselaje(e), e["col"], intensidad=0.13, textura=0.05, ancho=3)
        # panza
        Lz.forma([(x0, 0.22 * h), (x1, 0.22 * h), (x1, h), (x0, h)], e["panza"], suave=False, clip=m, borde=False,
                 sombra=False, brillo=False, textura=0.03)
        for col, y, alto in e["franjas"]:
            Lz.forma([(x0, (y - alto / 2) * h), (x1, (y - alto / 2) * h), (x1, (y + alto / 2) * h),
                      (x0, (y + alto / 2) * h)], col, suave=False, clip=m, borde=False, sombra=False, brillo=False,
                     textura=0.02)
    # ventanillas y cabina
    if e["vent"]:
        sep = (L * 0.62) / max(e["vent"], 1)
        for k in range(e["vent"]):
            Lz.circulo(x0 + 0.22 * L + k * sep, -0.16 * h, max(4.0, h * 0.075), (60, 72, 92), borde=False)
    if e.get("cabina") == "burbuja" and not e.get("botalon"):
        Lz.forma(catmull([(x1 - 0.42 * L, -0.45 * h), (x1 - 0.36 * L, -0.85 * h), (x1 - 0.12 * L, -0.85 * h),
                          (x1 - 0.06 * L, -0.45 * h)], 4), (150, 190, 220), intensidad=0.2, ancho=3, suave=False)
        for k in range(4):
            xx = x1 - 0.38 * L + k * 0.08 * L
            Lz.linea([(xx, -0.82 * h), (xx, -0.48 * h)], (60, 70, 80), 3)
    elif not e.get("botalon"):
        Lz.forma([(x1 - 0.1 * L, -0.38 * h), (x1 - 0.055 * L, -0.28 * h), (x1 - 0.085 * L, -0.24 * h),
                  (x1 - 0.13 * L, -0.33 * h)], (40, 50, 66), suave=False, borde=False, sombra=False)
    if e.get("estrella"):
        cx, cy, r = x0 + 0.4 * L, 0.0, 0.26 * h
        Lz.circulo(cx, cy, r, (30, 50, 110), borde=False)
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r * (0.92 if k % 2 == 0 else 0.38)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        Lz.forma(pts, (245, 245, 245), suave=False, borde=False, sombra=False, brillo=False)
    # ala cercana
    ay = {"baja": 0.38 * h, "media": 0.08 * h, "alta": -0.52 * h}[e["ala"]]
    Lz.forma(catmull([(x0 + 0.38 * L, ay), (x0 + 0.5 * L, ay - 0.1 * h), (x0 + 0.66 * L, ay - 0.04 * h),
                      (x0 + 0.66 * L, ay + 0.05 * h), (x0 + 0.42 * L, ay + 0.08 * h)], 4), oscuro_ala, suave=False,
             intensidad=0.1, ancho=3)
    if e["ala"] == "alta":  # montante del ala
        Lz.linea([(x0 + 0.52 * L, ay + 0.05 * h), (x0 + 0.56 * L, 0.42 * h)], oscuro(e["col"], 0.5), 6)
    # motores
    if e["motor"] == "jet":
        Lz.forma(catmull([(x0 + 0.48 * L, ay + 0.2 * h), (x0 + 0.72 * L, ay + 0.14 * h),
                          (x0 + 0.72 * L, ay + 0.62 * h), (x0 + 0.5 * L, ay + 0.56 * h)], 4), (222, 224, 230),
                 suave=False, intensidad=0.18)
        Lz.forma(elipse(x0 + 0.72 * L, ay + 0.38 * h, 0.02 * L, 0.23 * h), (40, 44, 52), intensidad=0.1, ancho=3)
    elif e["motor"] in ("helice", "radial") and not e.get("nariz_motor"):
        for k in range(e.get("n_mot", 1)):
            nx = x0 + 0.66 * L + k * 0.07 * L
            ny = ay + (0.05 - k * 0.12) * h
            Lz.forma(catmull([(nx - 0.16 * L, ny - 0.05 * h), (nx, ny - 0.18 * h), (nx + 0.02 * L, ny + 0.02 * h),
                              (nx, ny + 0.2 * h), (nx - 0.16 * L, ny + 0.12 * h)], 4), oscuro(e["col"], 0.88),
                     suave=False, intensidad=0.14)
            Lz.forma(elipse(nx + 0.035 * L, ny, 0.012 * L, 0.55 * h), (200, 200, 210), intensidad=0.02,
                     borde=False, sombra=False, brillo=False, textura=0)
            Lz.circulo(nx + 0.03 * L, ny, 0.06 * h, (40, 40, 44), borde=False)
    if e.get("nariz_motor"):  # motor radial en la nariz con hélice
        Lz.forma(elipse(x1 - 0.01 * L, -0.02 * h, 0.035 * L, 0.42 * h), oscuro(e["col"], 0.6), intensidad=0.15,
                 ancho=3)
        Lz.forma(elipse(x1 + 0.03 * L, -0.02 * h, 0.01 * L, 0.85 * h), (200, 200, 210), borde=False, sombra=False,
                 brillo=False, textura=0)
        Lz.circulo(x1 + 0.035 * L, -0.02 * h, 0.1 * h, (50, 50, 56), borde=False)
    if e.get("botalon"):
        Lz.forma(elipse(x1 + 0.02 * L, 0.0, 0.01 * L, 0.9 * h), (200, 200, 210), borde=False, sombra=False,
                 brillo=False, textura=0)
    img = Lz.final()
    # transparencia del disco de la hélice
    _cache[("av", modelo)] = img
    return img


def _globo():
    Lz = LienzoReal(520, 820, 260, 400)
    tela = (188, 178, 156)
    m = Lz.forma(elipse(0, -150, 230, 240), tela, intensidad=0.18, textura=0.12)
    for k in range(-4, 5):
        Lz.linea(catmull([(k * 52, -385), (k * 60, -150), (k * 22, 80)], 5, cerrado=False), oscuro(tela, 0.7), 2.5,
                 suave=False)
    for y in (-300, -200, -100, 0):
        r = math.sqrt(max(0.0, 1 - ((y + 150) / 240) ** 2)) * 230
        Lz.linea([(-r, y), (r, y)], oscuro(tela, 0.75), 2)
    for x in (-60, -20, 20, 60):
        Lz.linea([(x * 2.2, 60), (x * 0.6, 250)], (60, 50, 40), 3)
    Lz.forma([(-75, 250), (75, 250), (65, 340), (-65, 340)], (120, 86, 50), suave=False, intensidad=0.12, textura=0.2)
    return Lz.final()


# --------------------------------------------------------------------------- #
# BARCOS (vista lateral)
# --------------------------------------------------------------------------- #
BARCOS = {
    "bergantin": dict(casco=(52, 40, 34), vela=(214, 206, 186)),  # Mary Celeste
    "goleta5": dict(casco=(40, 40, 46), vela=(226, 222, 206), palos=5),  # Carroll A. Deering
    "balandra": dict(casco=(232, 228, 218), vela=(226, 214, 186), palos=1),  # Spray de Slocum
    "yate": dict(casco=(236, 236, 232), cubierta=(120, 82, 50)),  # MV Joyita
    "catamaran": dict(casco=(238, 238, 240), vela=(240, 240, 236)),  # Kaz II
    # Blue Anchor Line: casco negro, superestructura color café con leche y chimenea negra con franja blanca
    "vapor_waratah": dict(casco=(30, 30, 34), super=(196, 166, 122), chimenea=(26, 26, 28), tope=(20, 20, 22),
                          banda=True),
    "carbonero": dict(casco=(118, 124, 130), super=(150, 156, 160), chimenea=(110, 116, 120), tope=(30, 30, 34),
                      gruas=True),  # USS Cyclops (gris de la Marina)
    "carguero": dict(casco=(40, 42, 48), super=(214, 210, 200), chimenea=(160, 40, 34), tope=(24, 24, 26)),
    "ferry": dict(casco=(240, 240, 236), super=(240, 240, 236), chimenea=(200, 160, 60), tope=(24, 24, 26)),
    "galera": dict(casco=(120, 80, 46), vela=(222, 204, 170)),  # barcos antiguos (Pueblos del Mar / Anticitera)
    "franklin": dict(casco=(36, 30, 28), vela=(210, 206, 196)),  # HMS Erebus y Terror en el hielo
}


def barco_real(modelo, sil=None):
    """sil: color de silueta (niebla) o None para colores reales."""
    clave = ("bar", modelo, sil)
    if clave in _cache:
        return _cache[clave]
    e = dict(BARCOS[modelo])
    if sil:
        for k in ("casco", "vela", "super", "chimenea", "tope", "cubierta"):
            if k in e:
                e[k] = sil if k != "vela" else claro(sil, 0.25)
    Lz = LienzoReal(1300, 1000, 650, 760)
    P = lambda a, b: (a, b)
    if modelo in ("bergantin", "franklin", "goleta5", "balandra", "galera"):
        _velero(Lz, modelo, e)
    elif modelo == "yate":
        Lz.forma([(-330, -120), (300, -110), (380, -150), (300, 30), (-300, 40)], e["casco"], suave=False,
                 intensidad=0.1, textura=0.08)
        Lz.forma([(-200, -120), (120, -120), (100, -230), (-180, -230)], (240, 240, 236), suave=False,
                 intensidad=0.1)
        for k in range(4):
            Lz.forma([(-160 + k * 66, -205), (-110 + k * 66, -205), (-110 + k * 66, -160), (-160 + k * 66, -160)],
                     (50, 60, 76), suave=False, borde=False, sombra=False)
        Lz.linea([(-40, -230), (-40, -430)], (80, 70, 60), 8)
        Lz.forma([(-330, -40), (330, -40), (320, -20), (-320, -20)], (40, 70, 120), suave=False, borde=False)
    elif modelo == "catamaran":
        for dy, k in ((0, 1.0), (-14, 0.85)):
            Lz.forma(catmull([(-300, -60 + dy), (320, -60 + dy), (350, -40 + dy), (300, 0 + dy), (-280, 0 + dy)],
                             4), oscuro(e["casco"], k), suave=False, intensidad=0.1)
        Lz.forma([(-200, -60), (160, -60), (140, -140), (-180, -140)], e["casco"], suave=False, intensidad=0.1)
        Lz.linea([(0, -140), (0, -720)], (120, 120, 126), 9)
        Lz.forma([(10, -700), (10, -170), (260, -170)], e["vela"], suave=False, intensidad=0.12, textura=0.06)
        Lz.forma([(-10, -690), (-10, -170), (-250, -170)], oscuro(e["vela"], 0.9), suave=False, intensidad=0.12)
    else:  # vapores
        gruas = e.get("gruas")
        for mx in (-300, 320):
            Lz.linea([P(mx, -70), P(mx, -440)], oscuro(e["casco"], 0.8), 8)
        Lz.linea([P(-300, -430), P(320, -430)], oscuro(e["casco"], 0.6), 2)
        if gruas:  # el Cyclops tenía un bosque de grúas y pórticos para el carbón
            for k in range(6):
                x = -330 + k * 110
                Lz.linea([(x, -90), (x, -300)], (90, 96, 100), 7)
                Lz.linea([(x - 40, -300), (x + 40, -300)], (90, 96, 100), 7)
                Lz.linea([(x, -290), (x + 60, -120)], (90, 96, 100), 4)
        Lz.forma([(-120, -80), (180, -80), (170, -200), (-110, -200)], e["super"], suave=False, intensidad=0.1)
        Lz.forma([(-70, -200), (140, -200), (130, -260), (-60, -260)], e["super"], suave=False, intensidad=0.1)
        Lz.forma([(10, -260), (84, -260), (78, -400), (16, -400)], e["chimenea"], suave=False, intensidad=0.14)
        Lz.forma([(15, -400), (79, -400), (80, -370), (14, -370)], e["tope"], suave=False, borde=False)
        if e.get("banda") and not sil:  # franja blanca con el ancla azul
            Lz.forma([(13, -345), (81, -345), (81, -300), (13, -300)], (240, 240, 236), suave=False, borde=False)
            Lz.circulo(47, -322, 12, (40, 70, 160), borde=False)
        if not sil:
            for k in range(9):
                Lz.circulo(-90 + k * 30, -140, 7, (240, 210, 130), borde=False)
        Lz.forma([(-470, -100), (480, -105), (410, 40), (-410, 40)], e["casco"], suave=False, intensidad=0.08,
                 textura=0.12)
        if not sil:
            Lz.forma([(-425, 10), (425, 10), (410, 40), (-410, 40)], (130, 34, 30), suave=False, borde=False)
            for k in range(15):
                Lz.circulo(-380 + k * 54, -45, 6, oscuro(e["casco"], 0.5) if e["casco"][0] > 100 else
                           (90, 96, 110), borde=False)
    img = Lz.final()
    _cache[clave] = img
    return img


def _velero(Lz, modelo, e):
    casco, vela = e["casco"], e["vela"]
    palo = oscuro(casco, 0.7) if casco[0] > 60 else (40, 30, 24)
    jarcia = (50, 44, 40)
    if modelo == "goleta5":  # cinco palos con velas cangrejas (de cuchillo)
        xs = [-300, -150, 0, 150, 300]
        for mx in xs:
            Lz.linea([(mx, -40), (mx, -700)], palo, 9)
            Lz.forma([(mx + 8, -660), (mx + 8, -80), (mx + 130, -80), (mx + 110, -600)], vela, suave=False,
                     intensidad=0.14, textura=0.08, ancho=3)
            Lz.forma([(mx + 8, -700), (mx + 8, -620), (mx + 100, -640)], vela, suave=False, intensidad=0.1, ancho=3)
        Lz.forma([(300, -660), (480, -140), (330, -120)], vela, suave=False, intensidad=0.1, ancho=3)
        Lz.linea([(380, -80), (520, -150)], palo, 8)
        largo = 430
    elif modelo == "balandra":  # un solo palo (Spray)
        Lz.linea([(-20, -40), (-20, -640)], palo, 10)
        Lz.forma([(-10, -620), (-10, -80), (-300, -90)], vela, suave=False, intensidad=0.14, textura=0.08, ancho=3)
        Lz.forma([(-10, -600), (240, -110), (0, -100)], vela, suave=False, intensidad=0.12, textura=0.06, ancho=3)
        Lz.linea([(200, -80), (300, -120)], palo, 7)
        largo = 280
    elif modelo == "galera":  # barco antiguo con remos y vela cuadrada
        Lz.linea([(0, -40), (0, -560)], palo, 10)
        Lz.forma([(-200, -520), (200, -520), (210, -200), (-210, -200)], vela, suave=False, intensidad=0.15,
                 textura=0.1, ancho=3)
        for k in range(5):
            Lz.linea([(-200, -330 + k * 0), (200, -330)], oscuro(vela, 0.85), 3) if k == 0 else None
        for k in range(11):
            x = -260 + k * 52
            Lz.linea([(x, 0), (x - 40, 120)], (90, 60, 34), 6)
        Lz.forma(catmull([(-380, -170), (-330, -40), (330, -40), (390, -190), (420, -230)], 4, cerrado=False) +
                 [(330, 40), (-300, 40)], casco, suave=False, intensidad=0.12, textura=0.15)
        Lz.forma(elipse(410, -230, 26, 26), casco, intensidad=0.2)  # mascarón de pájaro
        return
    else:  # bergantín / Franklin: tres palos con velas cuadradas
        tops = {-170: -560, 10: -640, 180: -520} if modelo == "bergantin" else {-150: -600, 60: -640, 230: -540}
        for mx, top in tops.items():
            for dx in (-150, 150):
                Lz.linea([(mx, top + 20), (mx + dx * 1.3, -40)], jarcia, 2.2)
            Lz.linea([(mx, -40), (mx, top)], palo, 9)
        Lz.linea([(10, -640), (470, -170)], jarcia, 2.5)
        Lz.linea([(290, -80), (480, -170)], palo, 8)
        recogidas = modelo == "franklin"  # en el hielo: velas recogidas
        for mx, top in tops.items():
            alto_total = -40 - top - 60
            for n in range(3):
                y0 = top + 30 + n * alto_total / 3
                y1 = y0 + (alto_total / 3 - 18) * (0.25 if recogidas else 1)
                a0, a1 = 70 + n * 22, 82 + n * 24
                Lz.forma([(mx - a0, y0), (mx + a0, y0), (mx + a1 + 6, y1), (mx + 4, y1 + 10), (mx - a1, y1)], vela,
                         suave=False, intensidad=0.16, textura=0.1, ancho=3)
                Lz.linea([(mx - a0 - 8, y0), (mx + a0 + 8, y0)], palo, 5)
        if not recogidas:
            Lz.forma([(30, -600), (450, -170), (60, -150)], vela, suave=False, intensidad=0.12, textura=0.08, ancho=3)
        largo = 330
    Lz.forma([(-largo, -110), (-largo + 80, -60), (largo - 80, -60), (largo, -100), (largo - 60, 20),
              (largo - 180, 55), (-largo + 80, 55), (-largo + 10, 0)], casco, suave=False, intensidad=0.1,
             textura=0.14)
    Lz.linea([(-largo + 10, -40), (largo - 30, -40)], claro(casco, 0.3), 4)
    if modelo == "bergantin":  # bote salvavidas: falta (pescantes vacíos en la popa)
        Lz.linea([(-largo + 40, -60), (-largo - 20, -140)], palo, 5)
        Lz.linea([(-largo - 20, -140), (-largo - 20, -100)], jarcia, 2)
    if modelo == "franklin":
        Lz.forma([(-largo - 60, 0), (largo + 80, 0), (largo + 140, 120), (-largo - 120, 120)], (226, 236, 244),
                 suave=False, intensidad=0.08, textura=0.06)


# --------------------------------------------------------------------------- #
# AUTO ANTIGUO (Agatha Christie 1926 / Hoffa 1975)
# --------------------------------------------------------------------------- #
def auto(epoca="1920", col=(40, 50, 60)):
    clave = ("auto", epoca, col)
    if clave in _cache:
        return _cache[clave]
    Lz = LienzoReal(700, 360, 350, 300)
    if epoca == "1920":
        Lz.forma([(-260, -60), (-60, -60), (-40, -190), (130, -190), (150, -70), (280, -60), (290, 0), (-270, 0)],
                 col, suave=False, intensidad=0.12, textura=0.06)
        Lz.forma([(-20, -180), (120, -180), (130, -90), (-30, -90)], (120, 140, 160), suave=False, intensidad=0.2)
        Lz.forma(catmull([(-270, -10), (-240, -70), (-150, -70), (-110, -10)], 4, cerrado=False) +
                 [(-110, 10), (-270, 10)], oscuro(col, 0.7), suave=False)
        for x in (-190, 200):
            Lz.forma(elipse(x, 10, 62, 62), (26, 26, 28), intensidad=0.2)
            Lz.forma(elipse(x, 10, 26, 26), (170, 160, 140), intensidad=0.2)
        Lz.circulo(285, -50, 16, (250, 236, 180), borde=False)
    else:  # sedán de los 70
        Lz.forma([(-320, -60), (-120, -70), (-60, -150), (140, -150), (200, -75), (330, -60), (330, 10),
                  (-320, 10)], col, suave=False, intensidad=0.1, textura=0.05)
        Lz.forma([(-40, -140), (130, -140), (175, -78), (-90, -78)], (120, 140, 160), suave=False, intensidad=0.2)
        for x in (-210, 210):
            Lz.forma(elipse(x, 15, 58, 58), (26, 26, 28), intensidad=0.2)
            Lz.forma(elipse(x, 15, 28, 28), (190, 190, 196), intensidad=0.2)
        Lz.linea([(-320, -10), (330, -10)], (210, 210, 216), 6)
    img = Lz.final()
    _cache[clave] = img
    return img


def tren():
    if "tren" in _cache:
        return _cache["tren"]
    Lz = LienzoReal(1500, 520, 750, 440)
    negro, rojo = (34, 34, 38), (150, 36, 30)
    Lz.forma([(80, -230), (600, -230), (640, -60), (60, -60)], negro, suave=False, intensidad=0.12, textura=0.08)
    Lz.forma(elipse(600, -150, 50, 90), oscuro(negro, 0.8), intensidad=0.2)
    Lz.forma([(130, -360), (300, -360), (300, -230), (130, -230)], negro, suave=False, intensidad=0.1)
    Lz.forma([(150, -340), (280, -340), (280, -280), (150, -280)], (240, 200, 120), suave=False, borde=False)
    Lz.forma([(470, -230), (520, -230), (530, -360), (460, -360)], negro, suave=False)
    Lz.forma([(450, -370), (540, -370), (540, -350), (450, -350)], negro, suave=False)
    Lz.forma([(640, -60), (720, -10), (620, -10)], rojo, suave=False)
    for x in (170, 330, 490):
        Lz.forma(elipse(x, -30, 70, 70), rojo, intensidad=0.18)
        Lz.forma(elipse(x, -30, 20, 20), (40, 30, 30), intensidad=0.1)
    Lz.linea([(170, -30), (490, -30)], (180, 180, 186), 10)
    for k in range(2):  # vagones
        x0 = -700 + k * 380
        Lz.forma([(x0, -260), (x0 + 360, -260), (x0 + 360, -50), (x0, -50)], (96, 30, 26), suave=False,
                 intensidad=0.08, textura=0.1)
        Lz.forma([(x0 - 10, -280), (x0 + 370, -280), (x0 + 350, -260), (x0 + 10, -260)], (40, 30, 30), suave=False)
        for w in range(4):
            Lz.forma([(x0 + 30 + w * 82, -230), (x0 + 90 + w * 82, -230), (x0 + 90 + w * 82, -160),
                      (x0 + 30 + w * 82, -160)], (240, 200, 120), suave=False, borde=False)
        for x in (x0 + 70, x0 + 290):
            Lz.forma(elipse(x, -30, 40, 40), (30, 30, 32), intensidad=0.2)
    img = Lz.final()
    _cache["tren"] = img
    return img


def casa(fuego=False):
    clave = ("casa", fuego)
    if clave in _cache:
        return _cache[clave]
    Lz = LienzoReal(900, 800, 450, 760)
    madera = (176, 160, 132)
    Lz.forma([(-330, -420), (330, -420), (330, 0), (-330, 0)], madera, suave=False, intensidad=0.08, textura=0.12)
    for y in range(-400, 0, 34):
        Lz.linea([(-330, y), (330, y)], oscuro(madera, 0.85), 3)
    Lz.forma([(-380, -410), (0, -700), (380, -410)], (70, 46, 40), suave=False, intensidad=0.1, textura=0.12)
    Lz.forma([(180, -620), (240, -620), (240, -480), (180, -540)], (110, 60, 50), suave=False)
    for x, y in ((-230, -320), (120, -320), (-230, -160), (120, -160)):
        Lz.forma([(x, y), (x + 110, y), (x + 110, y + 100), (x, y + 100)],
                 (255, 170, 60) if fuego else (230, 200, 130), suave=False, intensidad=0.05)
        Lz.linea([(x + 55, y), (x + 55, y + 100)], (60, 40, 30), 5)
    Lz.forma([(-50, -150), (50, -150), (50, 0), (-50, 0)], (90, 60, 40), suave=False)
    img = Lz.final()
    _cache[clave] = img
    return img


def carpa_rota():
    """Carpa del paso Diatlov: abierta con cortes desde adentro."""
    if "carpa" in _cache:
        return _cache["carpa"]
    Lz = LienzoReal(900, 420, 450, 380)
    lona = (150, 132, 96)
    Lz.forma([(-380, 0), (-330, -210), (330, -220), (380, 0)], lona, suave=False, intensidad=0.12, textura=0.16)
    for x in (-120, 60, 200):
        Lz.forma([(x, -200), (x + 30, -60), (x - 10, -40), (x - 30, -180)], (30, 26, 24), suave=False, borde=False)
    Lz.forma([(-420, 0), (420, 0), (440, 40), (-440, 40)], (236, 240, 248), suave=False, borde=False)
    img = Lz.final()
    _cache["carpa"] = img
    return img
