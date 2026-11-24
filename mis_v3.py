"""
Serie de misterios, versión 3:
  * estilo propio por video (subtítulos, transiciones, cámara, color, recuadros, final) para que ninguno se vea igual;
  * DATOS EN PANTALLA SACADOS DEL AUDIO: cifras, años, lugares y nombres que el narrador dice, en el momento exacto
    en que los dice (de la transcripción de la voz), y nada que no cuente la historia;
  * cierre con las imágenes del propio video (tablero, película, carpeta o pantallas);
  * detalles de luz: rayos de luz y polvo en suspensión.
"""
from __future__ import annotations

import json
import math
import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import pro
from alcatraz import maquina
from caricatura import pop
from cine import pegar_glow
from dinos import TINTA, _grad, oscuro, sombra_suave
from pro import BLANCO, H, W

COLORES = [(255, 200, 80), (120, 220, 255), (255, 128, 120), (170, 255, 140), (255, 160, 60), (220, 170, 255),
           (255, 236, 120), (120, 255, 210)]
TRANSICIONES = ["barrido", "zoom", "destello", "vertical", "fundido"]
DATO_ESTILOS = ["etiqueta", "maquina", "neon", "sello"]
TARJETAS = ["ficha", "boleto", "placa", "nota", "diario", "ficha_der"]


def estilo_video(n):
    """Parámetros visuales propios de cada misterio. Dos videos seguidos nunca comparten color ni transición."""
    r = random.Random(n * 4099)
    color = COLORES[(n * 3) % len(COLORES)]
    modo = ["color", "subrayado", "caja"][n % 3]
    sub = {"modo": modo, "color": color, "y": 1330 + (n * 17) % 80}
    if modo == "caja":
        sub.update(caja=color, texto=TINTA)
    return dict(sub=sub, acento=color, transicion=TRANSICIONES[n % len(TRANSICIONES)],
                calidez=0.95 + (n % 5) * 0.025, dato=DATO_ESTILOS[(n // 2) % len(DATO_ESTILOS)],
                tarjeta=TARJETAS[n % len(TARJETAS)], cierre=["tablero", "pelicula", "carpeta", "pantallas"][n % 4],
                chip_x=[W / 2, 300, W - 300][n % 3], rnd=r)


def camaras_video(n, k):
    """k recorridos de cámara distintos (zoom de entrada/salida y paneo en direcciones variadas)."""
    r = random.Random(n * 131 + 7)
    out = []
    for i in range(k):
        z0, z1 = (1.0, r.uniform(1.07, 1.16)) if r.random() < 0.55 else (r.uniform(1.08, 1.16), 1.0)
        fx0, fy0 = r.uniform(0.42, 0.58), r.uniform(0.46, 0.6)
        fx1, fy1 = fx0 + r.uniform(-0.08, 0.08), fy0 + r.uniform(-0.07, 0.07)
        out.append((z0, z1, fx0, fy0, fx1, fy1))
    return out


# --------------------------------------------------------------------------- #
# DATOS QUE DICE EL NARRADOR
# --------------------------------------------------------------------------- #
NUM_PALABRA = {"dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
               "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15, "veinte": 20, "treinta": 30,
               "cuarenta": 40, "cincuenta": 50, "cien": 100, "mil": 1000}
NO_SUST = {"de", "y", "a", "en", "que", "o", "del", "la", "el", "los", "las", "un", "una", "más", "mas", "por", "con",
           "después", "antes", "se", "lo", "le", "fue", "eran", "es"}
NO_NOMBRE = {"En", "El", "La", "Los", "Las", "Un", "Una", "Era", "Se", "Y", "Pero", "Nadie", "Solo", "Nunca", "Su",
             "Sus", "Hoy", "Dicen", "Según", "Cuando", "Así", "Entonces", "Ni", "A", "Al", "De", "Del", "Que", "Qué",
             "Comenta", "Tú", "Fue", "Lo", "Le", "Es", "Hay", "Este", "Esta", "Esto", "Ese", "Esa", "Algunos",
             "Miles", "Muchos", "Desde", "Tras", "Durante", "Hasta", "Allí", "Ahí", "Aún", "Todo", "Todos", "Uno",
             "Ocho", "Cinco", "Dos", "Tres", "Mil", "Años", "Nada", "Otros", "Otro", "Sin", "Con", "Por", "Para",
             "Muchas", "Pocos", "Cada", "Más", "Ya", "Sí", "No", "Ella", "Él", "Ellos", "Le", "Les", "Mientras",
             "Antes", "Después", "Luego", "Incluso", "Además", "Alguien", "Nadie", "Algo", "Dentro", "Cerca", "Lejos",
             "Suscríbete", "Crees", "Debería", "Conocías", "Señor", "Señora", "Tenía", "Había", "Estaba", "Iba"}


def _limpia(w):
    return w.strip(" ,.;:¡!¿?…\"'()«»—-")


CONECTORES = {"de", "del", "la", "las", "los", "el", "y"}


def _nombres_guion(palabras):
    """Nombres propios del guion (bien escritos) con el momento en que se dicen."""
    out = []
    k = 0
    while k < len(palabras):
        p = palabras[k]
        tok = _limpia(p.texto)
        previo = palabras[k - 1].texto if k > 0 else "."
        inicio_frase = k == 0 or previo.rstrip().endswith((".", "?", "!", "…", ":"))
        if tok[:1].isupper() and len(tok) > 1 and (not inicio_frase or k + 1 < len(palabras) and
                                                  _limpia(palabras[k + 1].texto)[:1].isupper()):
            partes, j = [tok], k
            while j + 1 < len(palabras) and not palabras[j].texto.rstrip().endswith((".", ",", "?", "!", "…")):
                sig = _limpia(palabras[j + 1].texto)
                if sig[:1].isupper() or re.fullmatch(r"\d{1,4}", sig):
                    partes.append(sig)
                    j += 1
                    continue
                m = j + 1  # conectores seguidos («Triángulo de las Bermudas»)
                while m < len(palabras) and _limpia(palabras[m].texto).lower() in CONECTORES and \
                        not palabras[m].texto.rstrip().endswith((".", ",")):
                    m += 1
                if m > j + 1 and m < len(palabras) and _limpia(palabras[m].texto)[:1].isupper():
                    partes += [_limpia(palabras[q].texto).lower() for q in range(j + 1, m)] + \
                              [_limpia(palabras[m].texto)]
                    j = m
                else:
                    break
            while len(partes) > 1 and partes[0] in ("El", "La", "Los", "Las", "En", "Un", "Una", "Y", "A", "De"):
                partes = partes[1:]
            nombre = " ".join(partes)
            if not (len(partes) == 1 and (tok in NO_NOMBRE or inicio_frase)):
                out.append((p.inicio, "nombre", nombre.upper()))
            k = j + 1
            continue
        if re.fullmatch(r"[A-Z]{1,4}\d{1,4}", tok):
            out.append((p.inicio, "nombre", tok))
        k += 1
    return out


def extraer_datos(audio, escenas_al):
    """Para cada escena: [(t_relativo, tipo, texto)] con lo que el narrador dice (años, cifras, lugares, nombres).
    Las cifras salen de la transcripción de la voz; los nombres, del guion (para que estén bien escritos)."""
    cache = Path(str(audio) + ".palabras.json")
    oidas = [tuple(x) for x in json.loads(cache.read_text(encoding="utf-8"))] if cache.exists() else []
    salida = []
    for i, e in enumerate(escenas_al):
        ini, fin = e["inicio"], e["inicio"] + e["dur"]
        ws = [(w, s) for w, s, _ in oidas if ini - 0.05 <= s < fin - 0.1]
        datos = []
        for k, (w, s) in enumerate(ws):
            tok = _limpia(w)
            low = tok.lower()
            num = None
            if re.fullmatch(r"\d[\d.,]*", tok):
                num = tok.rstrip(".,")
            elif low in NUM_PALABRA and NUM_PALABRA[low] >= 3 and low != "mil":
                num = str(NUM_PALABRA[low])
            if not num:
                continue
            digitos = re.sub(r"\D", "", num)
            previo = _limpia(ws[k - 1][0]) if k > 0 else ""
            if len(digitos) == 4 and 1000 <= int(digitos) <= 2030 and "." not in num:
                datos.append((s - ini, "anio", digitos))
            elif previo[:1].isupper() and previo not in NO_NOMBRE:  # «Vuelo 19», «Apolo 13»
                datos.append((s - ini, "nombre", f"{previo.upper()} {num}"))
            elif not w.rstrip().endswith((",", ".", "…")) and k + 1 < len(ws):
                c = _limpia(ws[k + 1][0]).lower()
                if c == "de" and k + 2 < len(ws):
                    c = _limpia(ws[k + 2][0]).lower()
                if c and c not in NO_SUST and not re.fullmatch(r"\d.*", c):
                    datos.append((s - ini, "cifra", f"{num} {c.upper()}"))
        datos += _nombres_guion(e.get("palabras", []))
        datos.sort(key=lambda d: d[0])
        # sin repetidos (ni nombres ya incluidos en otro dato), máximo 2 por escena y separados 1,3 s
        vistos, elegidos = set(), []
        for d in datos:
            if d[2] in vistos or any(d[2] in v or v in d[2] for v in vistos) or \
                    (elegidos and d[0] - elegidos[-1][0] < 1.3):
                continue
            vistos.add(d[2])
            elegidos.append(d)
            if len(elegidos) == 2:
                break
        salida.append(elegidos)
    if salida:
        salida[-1] = []  # la última escena es la pregunta final
    return salida


ETIQUETA = {"anio": "AÑO", "cifra": "CIFRA", "nombre": "DATO"}


def dibujar_dato(img, t, t0, tipo, texto, y, estilo, acento, dur=2.6):
    if t < t0 or t > t0 + dur + 0.3:
        return
    p = pop((t - t0) / 0.28)
    a = min(1.0, max(0.0, (t0 + dur + 0.3 - t) / 0.3))
    texto = texto[:30]
    medidor = ImageDraw.Draw(img)
    tam = 70 if tipo != "nombre" else 62
    f = pro.fuente(tam)
    while medidor.textlength(texto, font=f) > 860 and tam > 36:
        tam -= 4
        f = pro.fuente(tam)
    tw = medidor.textlength(texto, font=f)
    w, h = int(tw + 90), 150
    capa = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ox, oy = 30, 30
    if estilo == "etiqueta":
        d.rounded_rectangle((ox, oy, ox + w, oy + h), radius=26, fill=(18, 18, 24, 236), outline=acento, width=6)
        d.text((ox + w / 2, oy + 34), ETIQUETA[tipo], font=maquina(28), fill=acento, anchor="mm")
        d.text((ox + w / 2, oy + 96), texto, font=f, fill=BLANCO, anchor="mm")
    elif estilo == "maquina":
        d.rectangle((ox, oy + 16, ox + w, oy + h - 8), fill=(242, 234, 212, 250))
        d.text((ox + w / 2, oy + 44), ETIQUETA[tipo], font=maquina(26), fill=(150, 30, 30), anchor="mm")
        d.text((ox + w / 2, oy + 98), texto, font=maquina(min(66, tam)), fill=TINTA, anchor="mm")
        d.line((ox + 30, oy + h - 20, ox + w - 30, oy + h - 20), fill=(190, 30, 30), width=5)
    elif estilo == "neon":
        d.text((ox + w / 2, oy + 34), ETIQUETA[tipo], font=maquina(28), fill=acento, anchor="mm")
        d.text((ox + w / 2, oy + 96), texto, font=f, fill=acento, anchor="mm", stroke_width=6, stroke_fill=(10, 10, 14))
    else:  # sello
        d.rounded_rectangle((ox, oy, ox + w, oy + h), radius=12, outline=acento, width=8)
        d.text((ox + w / 2, oy + 34), ETIQUETA[tipo], font=maquina(26), fill=acento, anchor="mm")
        d.text((ox + w / 2, oy + 96), texto, font=maquina(min(64, tam)), fill=acento, anchor="mm")
    if estilo in ("maquina", "sello"):
        capa = capa.rotate(-3 if int(t0 * 10) % 2 else 3, expand=True, resample=Image.BICUBIC)
    if a < 1:
        capa.putalpha(capa.getchannel("A").point(lambda v: int(v * a)))
    if p != 1:
        capa = capa.resize((max(1, int(capa.width * p)), max(1, int(capa.height * p))))
    if estilo == "neon":
        pegar_glow(img, W / 2, y, 200 * p, "#%02x%02x%02x" % acento, 0.35 * a)
    elif estilo == "etiqueta":
        sombra_suave(img, (W / 2 - capa.width / 2 + 20, y - capa.height / 2 + 20, W / 2 + capa.width / 2 - 20,
                           y + capa.height / 2 - 20), radio=26, alfa=int(120 * a))
    img.alpha_composite(capa, (int(W / 2 - capa.width / 2), int(y - capa.height / 2)))


def frase_sello(parrafo):
    """Frase corta tomada del propio texto narrado (p. ej. «NUNCA HALLARON LOS RESTOS» → «NUNCA HALLARON»)."""
    m = re.search(r"\b(nunca|nadie|sin rastro|sin dejar|sigue|ni una|jamás)\b([^.,…?!]*)", parrafo, re.I)
    if not m:
        return None
    palabras = (m.group(1) + m.group(2)).split()[:3]
    frase = " ".join(palabras).upper()
    return frase if len(frase) <= 22 else " ".join(palabras[:2]).upper()


# --------------------------------------------------------------------------- #
# LUZ Y AMBIENTE
# --------------------------------------------------------------------------- #
def rayos(img, t, x0=540, color=(255, 240, 200), n=5, alfa=30, ancho=220):
    capa = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k in range(n):
        x = (x0 - ancho + k * ancho * 2 / max(1, n - 1) + 30 * math.sin(t * 0.4 + k)) / 4
        d.polygon([(x - 6, 0), (x + 6, 0), (x + 50, H / 4), (x - 26, H / 4)], fill=color + (alfa,))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(5)).resize((W, H)))


def polvo(img, t, cx=300, cy=700, radio=420, n=16, semilla=3, color="#ffe9b0"):
    r = random.Random(semilla)
    for i in range(n):
        a0, rr = r.uniform(0, 6.28), r.uniform(0.2, 1) * radio
        x = cx + rr * math.cos(a0 + t * 0.05 * (1 + i % 3)) + 20 * math.sin(t * 0.7 + i)
        y = cy + rr * math.sin(a0) * 0.8 + (t * 12 * (1 + i % 2)) % 120
        pegar_glow(img, x, y, r.uniform(3, 6), color, 0.5 + 0.4 * math.sin(t * 2 + i))


# --------------------------------------------------------------------------- #
# CIERRE CON LAS IMÁGENES DEL PROPIO VIDEO
# --------------------------------------------------------------------------- #
def _foto(im, w, h, marco=18, abajo=60):
    f = im.convert("RGB").resize((w, h), Image.LANCZOS).convert("RGBA")
    p = Image.new("RGBA", (w + marco * 2, h + marco + abajo), (246, 244, 238, 255))
    p.paste(f, (marco, marco))
    return p


def kit_cierre(ctx, estilo):
    fotos = [f for f in ctx.get("fotos", []) if f is not None][:4] or [Image.new("RGBA", (W, H), (30, 30, 40, 255))]
    r = random.Random(ctx["n"] * 31)
    if estilo == "tablero":  # tablero de corcho con fotos e hilo rojo
        fondo = _grad(W, H, [(0, (120, 84, 52)), (1, (92, 62, 38))])
        d = ImageDraw.Draw(fondo)
        for _ in range(2600):
            x, y = r.uniform(0, W), r.uniform(0, H)
            d.point((x, y), fill=(150, 110, 70) if r.random() < 0.5 else (80, 54, 32))
        pos = [(270, 520), (790, 600), (300, 1080), (780, 1150)]
        piezas = []
        for k, f in enumerate(fotos):
            ph = _foto(f, 300, 420).rotate(r.uniform(-8, 8), expand=True, resample=Image.BICUBIC)
            piezas.append((ph, pos[k % 4]))
        def din(img, t, dur):
            d2 = ImageDraw.Draw(img)
            for k, (ph, (x, y)) in enumerate(piezas):
                q = pop((t - 0.15 * k) / 0.35)
                if q <= 0.02:
                    continue
                im = ph if q == 1 else ph.resize((max(1, int(ph.width * q)), max(1, int(ph.height * q))))
                sombra_suave(img, (x - im.width / 2 + 14, y - im.height / 2 + 14, x + im.width / 2 + 8,
                                   y + im.height / 2 + 8), radio=6, alfa=120)
                img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
            hilo = min(1.0, max(0.0, (t - 0.8) / 1.0))
            pins = [(x, y - 200) for _, (x, y) in piezas]
            for k in range(len(pins) - 1):
                (x0, y0), (x1, y1) = pins[k], pins[k + 1]
                d2.line((x0, y0, x0 + (x1 - x0) * hilo, y0 + (y1 - y0) * hilo), fill=(200, 20, 30), width=5)
            for x, y in pins:
                d2.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(210, 30, 40), outline=(90, 10, 10), width=3)
        return fondo, din
    if estilo == "pelicula":  # tira de película que sube
        fondo = _grad(W, H, [(0, (14, 12, 16)), (1, (4, 4, 6))])
        cuadros = [f.convert("RGB").resize((560, 760), Image.LANCZOS).convert("RGBA") for f in fotos]
        def din(img, t, dur):
            d2 = ImageDraw.Draw(img)
            y0 = 400 - t * 160
            d2.rectangle((220, 0, 860, H), fill=(20, 18, 16))
            for k in range(-2, 12):
                f = cuadros[k % len(cuadros)]
                y = y0 + k * 820
                if -820 < y < H:
                    img.alpha_composite(f, (260, int(y)))
                for j in range(8):
                    yy = y + j * 102
                    d2.rounded_rectangle((232, yy, 250, yy + 50), radius=4, fill=(200, 196, 186))
                    d2.rounded_rectangle((830, yy, 848, yy + 50), radius=4, fill=(200, 196, 186))
            pegar_glow(img, 540, 200, 500, "#ffe0a0", 0.15)
        return fondo, din
    if estilo == "carpeta":  # carpeta del caso con fotos sujetas por un clip
        fondo = _grad(W, H, [(0, (40, 34, 30)), (1, (20, 16, 14))])
        d = ImageDraw.Draw(fondo)
        d.rounded_rectangle((90, 380, 990, 1640), radius=20, fill=(214, 182, 120), outline=(150, 120, 70), width=6)
        d.rounded_rectangle((90, 330, 420, 400), radius=14, fill=(214, 182, 120))
        d.text((540, 1560), ctx["nombre"].upper()[:26], font=maquina(46), fill=(80, 50, 30), anchor="mm")
        fotos_ = [_foto(f, 330, 440, marco=14, abajo=40).rotate(r.uniform(-6, 6), expand=True,
                                                               resample=Image.BICUBIC) for f in fotos[:3]]
        def din(img, t, dur):
            for k, ph in enumerate(fotos_):
                q = min(1.0, max(0.0, (t - 0.2 * k) / 0.5))
                x = 310 + k * 230
                y = 900 + (1 - q) * 900 + (k % 2) * 80
                img.alpha_composite(ph, (int(x - ph.width / 2), int(y - ph.height / 2)))
                d2 = ImageDraw.Draw(img)
                d2.rounded_rectangle((x - 20, y - ph.height / 2 - 30, x + 20, y - ph.height / 2 + 40), radius=12,
                                     outline=(170, 170, 176), width=6)
            pegar_glow(img, 200, 400, 300, "#ffd890", 0.25)
        return fondo, din
    # pantallas: muro de televisores antiguos mostrando el caso
    fondo = _grad(W, H, [(0, (12, 12, 16)), (1, (4, 4, 6))])
    tvs = [f.convert("RGB").resize((420, 320), Image.LANCZOS).convert("RGBA") for f in fotos]
    def din(img, t, dur):
        d2 = ImageDraw.Draw(img)
        for k in range(4):
            x, y = 70 + (k % 2) * 480, 420 + (k // 2) * 440
            d2.rounded_rectangle((x - 20, y - 20, x + 440, y + 360), radius=34, fill=(40, 38, 42))
            f = tvs[k % len(tvs)]
            if int(t * 6 + k * 3) % 23 == 0:
                d2.rectangle((x, y, x + 420, y + 320), fill=(180, 180, 180))
            else:
                img.alpha_composite(f, (x, y))
            yy = y + int((t * 90 + k * 50) % 320)
            d2.rectangle((x, yy, x + 420, yy + 16), fill=(255, 255, 255, 40))
        pegar_glow(img, 540, 850, 600, "#a0c0ff", 0.18)
    return fondo, din
