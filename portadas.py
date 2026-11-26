#!/usr/bin/env python3
"""
Portadas verticales (1080x1920) para los videos que no tienen miniatura hecha en ChatGPT: toma el cuadro más nítido y
colorido del propio video y le pone el titular grande arriba y la etiqueta roja abajo, con el mismo estilo de las
miniaturas del canal. Uso: python portadas.py  (genera Miniaturas/<video>.jpg para la lista PORTADAS).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent
FUENTE = str(RAIZ / "fuentes" / "Anton-Regular.woff")
W, H = 1080, 1920
CORTE = int(H * 0.665)  # desde aquí hacia abajo se tapa (ahí van los subtítulos del video)

M, R = "MISTERIO SIN RESOLVER", "HISTORIA REAL"
PORTADAS = {
    # video: (archivo, titular, etiqueta, color del titular)
    "misterio_01_mary_celeste": ("misterios nuevos/misterio_01_mary_celeste.mp4", "NADIE A BORDO", M, "#FFD21F"),
    "misterio_03_mh370": ("misterios nuevos/misterio_03_mh370.mp4", "DESAPARECIÓ", M, "#FFFFFF"),
    "misterio_38_triangulo_de_bennington": ("misterios nuevos/misterio_38_triangulo_de_bennington.mp4", "DESAPARECEN", M, "#FF8A1F"),
    "misterio_41_cicada_3301": ("misterios nuevos/misterio_41_cicada_3301.mp4", "¿QUIÉN LO CREÓ?", M, "#FFD21F"),
    "misterio_16_uss_cyclops": ("misterios nuevos/misterio_16_uss_cyclops.mp4", "306 PERSONAS", M, "#FFFFFF"),
    "historia_01_guerra_mas_corta": ("salida/historia_01_guerra_mas_corta_cine.mp4", "38 MINUTOS", R, "#FFD21F"),
    "historia_02_napoleon_no_era_bajito": ("salida/historia_02_napoleon_no_era_bajito_caricatura.mp4", "NO ERA BAJITO", R, "#FFFFFF"),
    "historia_03_cleopatra_y_la_luna": ("salida/historia_03_cleopatra_y_la_luna_caricatura.mp4", "MÁS CERCA DE TI", R, "#FFD21F"),
    "historia_04_gran_muralla_espacio": ("salida/historia_04_gran_muralla_espacio_caricatura.mp4", "NO SE VE", R, "#FF8A1F"),
    "historia_05_guerra_de_los_emus": ("salida/historia_05_guerra_de_los_emus_caricatura.mp4", "PERDIERON", R, "#FFD21F"),
    "historia_06_plaga_del_baile": ("salida/historia_06_plaga_del_baile_caricatura.mp4", "NO PODÍAN PARAR", R, "#FFFFFF"),
    "historia_07_oxford_y_los_aztecas": ("salida/historia_07_oxford_y_los_aztecas_caricatura.mp4", "MÁS ANTIGUA", R, "#FFD21F"),
    "historia_08_hiroo_onoda": ("salida/historia_08_hiroo_onoda_caricatura.mp4", "29 AÑOS", R, "#FF8A1F"),
    "historia_09_robo_mona_lisa": ("salida/historia_09_robo_mona_lisa_caricatura.mp4", "LA ROBARON", R, "#FFD21F"),
    "historia_10_inundacion_de_melaza": ("salida/historia_10_inundacion_de_melaza_caricatura.mp4", "OLA DE MELAZA", R, "#FFFFFF"),
    "historia_11_dinosaurios": ("salida/historia_11_dinosaurios_pro.mp4", "T. REX", R, "#FFD21F"),
    "historia_12_alcatraz": ("salida/historia_12_alcatraz_pro.mp4", "NUNCA LOS HALLARON", R, "#FFFFFF"),
    "historia_13_db_cooper": ("salida/historia_13_db_cooper_pro.mp4", "DESAPARECIÓ", R, "#FF8A1F"),
    "historia_14_mineros_chile": ("salida/historia_14_mineros_chile_pro.mp4", "LOS 33", R, "#FFD21F"),
    "historia_15_andes": ("salida/historia_15_andes_pro.mp4", "72 DÍAS", R, "#FFFFFF"),
    "historia_18_wojtek": ("salida/historia_18_wojtek_pro.mp4", "OSO SOLDADO", R, "#FFD21F"),
}


def duracion(ruta):
    return float(subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", ruta],
                                capture_output=True, text=True).stdout)


def cuadro(ruta, t):
    crudo = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", ruta, "-frames:v", "1", "-vf",
                            f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return Image.frombytes("RGB", (W, H), crudo)


def mejor_cuadro(ruta):
    """Devuelve el cuadro más nítido y colorido, y la altura (y) donde el video pone sus subtítulos."""
    d = duracion(ruta)
    cuadros, mejor, puntos = [], None, -1
    filas = np.zeros(H)
    for f in np.linspace(0.08, 0.80, 30):
        im = cuadro(ruta, d * f)
        a = np.asarray(im.convert("HSV"), dtype=np.float32)
        gris = np.asarray(im.convert("L"), dtype=np.float32)
        dx = np.abs(np.diff(gris, axis=1))
        nitidez = np.abs(np.diff(gris, axis=0)).mean() + dx.mean()
        # texto: muchos bordes fuertes y píxeles muy claros en la misma fila
        filas += ((gris[:, 1:] > 200) & (dx > 80)).mean(axis=1)
        p = a[..., 1].mean() * 0.6 + gris.std() * 1.2 + nitidez * 6
        if p > puntos:
            mejor, puntos = im, p
    zona = filas[int(H * 0.55):int(H * 0.92)]
    suave = np.convolve(zona, np.ones(60) / 60, mode="same")
    y_sub = int(H * 0.55) + int(np.argmax(suave))
    return mejor, y_sub


def texto_ajustado(draw, txt, ancho_max, tam_max, tam_min=90):
    tam = tam_max
    while tam > tam_min:
        f = ImageFont.truetype(FUENTE, tam)
        if draw.textlength(txt, font=f) <= ancho_max:
            return f, [txt]
        tam -= 6
    # dos líneas
    palabras = txt.split()
    mitad = max(1, len(palabras) // 2)
    lineas = [" ".join(palabras[:mitad]), " ".join(palabras[mitad:])]
    tam = tam_max
    while tam > 60:
        f = ImageFont.truetype(FUENTE, tam)
        if max(draw.textlength(l, font=f) for l in lineas) <= ancho_max:
            return f, lineas
        tam -= 6
    return ImageFont.truetype(FUENTE, 60), lineas


def portada(video, titular, etiqueta, color, destino):
    base, y_sub = mejor_cuadro(str(RAIZ / video))
    base = base.resize((int(W * 1.06), int(H * 1.06))).crop((int(W * 0.03), int(H * 0.03), int(W * 0.03) + W,
                                                              int(H * 0.03) + H))
    base = ImageEnhance.Color(base).enhance(1.25)
    base = ImageEnhance.Contrast(base).enhance(1.12)
    # degradados oscuros arriba y abajo para que el texto se lea
    sombra = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sombra)
    for y in range(H):
        a = 0
        if y < 640:
            a = int(250 * (1 - y / 640) ** 1.1)
        elif abs(y - y_sub) < 150:
            a = int(255 * min(1.0, (150 - abs(y - y_sub)) / 40))
        sd.line([(0, y), (W, y)], fill=a)
    base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), base, sombra)
    d = ImageDraw.Draw(base)
    f, lineas = texto_ajustado(d, titular, 990, 230)
    y = 70
    for l in lineas:
        ancho = d.textlength(l, font=f)
        x = (W - ancho) / 2
        d.text((x, y), l, font=f, fill=color, stroke_width=11, stroke_fill="black")
        y += int(f.size * 1.08)
    # trazo rojo bajo el titular
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(capa)
    cd.polygon([(120, y + 18), (W - 110, y + 4), (W - 130, y + 30), (140, y + 42)], fill=(225, 20, 25, 255))
    base = Image.alpha_composite(base.convert("RGBA"), capa)
    # etiqueta roja abajo
    d = ImageDraw.Draw(base)
    fe = ImageFont.truetype(FUENTE, 84)
    tw = d.textlength(etiqueta, font=fe)
    x0, y0 = (W - tw) / 2 - 46, y_sub - 95
    d.rounded_rectangle([x0, y0, x0 + tw + 92, y0 + 126], radius=26, fill=(214, 18, 24), outline="black", width=6)
    d.text((x0 + 46, y0 + 8), etiqueta, font=fe, fill="white", stroke_width=4, stroke_fill="black")
    fc = ImageFont.truetype(FUENTE, 44)
    marca = "@1MRELATO"
    d.text(((W - d.textlength(marca, font=fc)) / 2, y0 + 138), marca, font=fc, fill=(235, 235, 235))
    base.convert("RGB").filter(ImageFilter.UnsharpMask(1.2, 60, 2)).save(destino, quality=90, optimize=True)


def main():
    for nombre, (video, titular, etiqueta, color) in PORTADAS.items():
        destino = RAIZ / "Miniaturas" / f"{nombre}.jpg"
        portada(video, titular, etiqueta, color, destino)
        print(destino.name)


if __name__ == "__main__":
    main()
