#!/usr/bin/env python3
"""
Crea la carpeta «textos historias nuevas» a partir de guiones/historias_100.md: para cada relato, el título, la
descripción y un prompt de miniatura llamativa para ChatGPT (mismo formato que «textos misterios nuevos»).
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
GUION = RAIZ / "guiones" / "historias_100.md"
DESTINO = RAIZ / "textos historias nuevas"

# Etiqueta roja de la miniatura y hashtags de la categoría, por rango de relatos.
CATEGORIAS = [
    (range(1, 34), "HISTORIA REAL", "#historia #historiasreales"),
    (range(34, 38), "LEYENDA", "#leyendas #historiasdeterror"),
    (range(38, 51), "HISTORIA REAL", "#ciencia #historia"),
    (range(51, 62), "HISTORIA REAL", "#historia #cultura"),
    (range(62, 82), "HISTORIA DE TERROR", "#terror #historiasdeterror #paranormal"),
    (range(82, 85), "FRAUDE HISTÓRICO", "#historia #fraude"),
    (range(85, 101), "HISTORIA GAMER", "#videojuegos #gamer #retro"),
]
COLOR_TEXTO = ["amarilla", "blanca", "naranja", "roja"]


def categoria(n):
    for rango, etiqueta, tags in CATEGORIAS:
        if n in rango:
            return etiqueta, tags
    return "HISTORIA REAL", "#historia"


def slug(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:40]


def nombre_video(n, nombre):
    return f"relato_{n:03d}_{slug(nombre)}"


def cargar():
    txt = GUION.read_text(encoding="utf-8")
    bloques = re.split(r"\n## (\d+) · ", txt)[1:]
    out = {}
    for i in range(0, len(bloques), 2):
        n, cuerpo = int(bloques[i]), bloques[i + 1]
        nombre = cuerpo.split("\n", 1)[0].strip()
        voz = re.search(r"```\n(.*?)```", cuerpo, re.S).group(1).strip()
        campo = lambda k: (re.search(rf"\*\*{k}:\*\* (.*)", cuerpo) or [None, ""])[1].strip()
        escena, canva = (campo("M").split(" · **Canva:** ") + [""])[:2]
        out[n] = dict(n=n, nombre=nombre, voz=voz, titulo=campo("T"), desc=campo("D"), escena=escena.strip(),
                      canva=canva.strip().strip('"'))
    return out


def prompt_miniatura(g):
    etiqueta, _ = categoria(g["n"])
    anio = (re.findall(r"\b(1[0-9]{3}|20[0-2][0-9])\b", g["desc"] + " " + g["titulo"]) or [""])[0]
    epoca = f" Época: {anio}, con ropa, vehículos y objetos de ese año." if anio else ""
    color = COLOR_TEXTO[g["n"] % len(COLOR_TEXTO)]
    gamer = (" Estilo de ilustración realista, sin personajes ni logotipos de marcas o videojuegos con derechos de "
             "autor.") if g["n"] >= 85 else ""
    return (f"Crea una miniatura vertical 9:16 para YouTube Shorts, hiperrealista y cinematográfica, muy llamativa, "
            f"sobre «{g['nombre']}». Escena: {g['escena'].rstrip('.')}.{epoca}{gamer} Iluminación dramática con "
            f"contraste alto, colores intensos, profundidad de campo y nitidez en el elemento principal. Un círculo "
            f"rojo brillante con una flecha resaltando el detalle más impactante. Arriba, texto enorme en mayúsculas "
            f"con letra gruesa {color} y borde negro: «{(g['canva'] or g['nombre']).upper()}». Abajo, una etiqueta "
            f"pequeña roja que diga «{etiqueta}». Sin marcas de agua, sin logotipos y sin más texto.")


def descripcion(g):
    _, tags_cat = categoria(g["n"])
    corta, *tags = g["desc"].split(" · ")
    todas = f"#shorts {tags_cat} #datoscuriosos #sabiasque #curiosidades {' '.join(tags)}".split()
    etiquetas = " ".join(dict.fromkeys(todas))
    return (f"{corta}\n\n¿Tú qué opinas? Te leo en los comentarios 👇\n🔔 Suscríbete para más historias reales que "
            f"parecen inventadas.\n\n{etiquetas}").strip()


def main():
    guiones = cargar()
    DESTINO.mkdir(exist_ok=True)
    indice = ["# Textos de las 100 historias nuevas", "",
              "Cada archivo tiene el **título**, la **descripción** y el **prompt de miniatura para ChatGPT** del "
              "video con el mismo nombre (carpeta «historias nuevas»). Guiones para ElevenLabs en "
              "`guiones/historias_100.md`.", "",
              "| # | Video | Título |", "|---|---|---|"]
    for n in sorted(guiones):
        g = guiones[n]
        nombre = nombre_video(n, g["nombre"])
        (DESTINO / f"{nombre}.md").write_text(
            f"# {n:03d} · {g['nombre']}\n\nVideo: `historias nuevas/{nombre}.mp4`\n\n"
            f"## Título\n\n{g['titulo']}\n\n## Descripción\n\n{descripcion(g)}\n\n"
            f"## Prompt de miniatura (ChatGPT)\n\n{prompt_miniatura(g)}\n", encoding="utf-8")
        indice.append(f"| {n:03d} | {nombre}.mp4 | {g['titulo'].split(' #')[0]} |")
    (DESTINO / "README.md").write_text("\n".join(indice) + "\n", encoding="utf-8")
    print(len(guiones), "textos")


if __name__ == "__main__":
    main()
