#!/usr/bin/env python3
"""
Crea la carpeta «textos misterios nuevos»: para cada video, el título, la descripción y un prompt de miniatura
llamativa para ChatGPT, usando los detalles reales de cada historia (modelo y color del avión o barco, época, lugar).
"""
from __future__ import annotations

import re
from pathlib import Path

from mis_kits import DETALLES, PERSONAS
from misterios import slug
from verificar_misterios import cargar_guiones

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "textos misterios nuevos"

AVIONES = {
    "avenger": "cinco bombarderos torpederos TBM Avenger de la Marina de EE. UU., azul marino con la panza blanca y la "
               "estrella blanca, volando en formación",
    "777": "un Boeing 777 blanco con franjas roja y azul en la cola",
    "electra": "un Lockheed Electra 10E bimotor de aluminio plateado brillante",
    "lancastrian": "un avión de pasajeros Avro Lancastrian plateado de cuatro motores de hélice",
    "constellation": "un Lockheed Super Constellation de cuatro hélices, fuselaje en forma de delfín y triple cola",
    "norseman": "una avioneta monomotor Noorduyn Norseman verde oliva del ejército de EE. UU.",
    "p38": "un avión de reconocimiento P-38 Lightning de doble fuselaje, color azul grisáceo",
    "cessna": "una avioneta Cessna 182 blanca con franjas rojas",
    "f18": "un caza F/A-18 gris de la Marina persiguiendo un objeto blanco con forma de pastilla",
    "globo": "un globo de hidrógeno con canasta de mimbre sobre el hielo del Ártico",
}
BARCOS = {
    "bergantin": "un bergantín de madera del siglo XIX con las velas a medio desplegar y sin nadie a bordo",
    "goleta5": "una goleta de cinco palos con todas las velas desplegadas, encallada frente a un faro de franjas "
               "blancas y negras en espiral",
    "balandra": "una pequeña balandra de un solo palo en mar abierto",
    "yate": "un pequeño barco a motor de madera, escorado y medio hundido, sin tripulación",
    "catamaran": "un catamarán blanco a la deriva con las velas desplegadas y nadie a bordo",
    "vapor_waratah": "un vapor de pasajeros de 1909 de casco negro, superestructura color café y chimenea negra con "
                     "franja blanca, en medio de una tormenta",
    "carbonero": "un enorme buque carbonero gris de la Marina de EE. UU. con decenas de grúas",
    "carguero": "un viejo carguero oxidado envuelto en niebla",
    "ferry": "un vapor de pasajeros de noche",
    "galera": "un barco antiguo de remos con una gran vela cuadrada",
    "franklin": "dos barcos de vela del siglo XIX atrapados en el hielo del Ártico",
}
OBJETOS = {
    "wow": "una hoja impresa de computadora antigua con el código «6EQUJ5» encerrado en un círculo rojo y la palabra "
           "«Wow!» escrita a mano",
    "voynich": "una página antigua del manuscrito Voynich con plantas extrañas y escritura desconocida",
    "zodiaco": "una carta cifrada con símbolos y el símbolo de una mira (círculo con cruz)",
    "tamam": "un trozo de papel arrancado de un libro con las palabras «Tamám Shud»",
    "festo": "un disco de arcilla con símbolos estampados en espiral",
    "rongorongo": "una tablilla de madera con jeroglíficos rongorongo",
    "tablilla": "una tablilla de arcilla minoica con escritura Lineal A",
    "indo": "un sello de piedra del valle del Indo con un animal y símbolos",
    "cobre": "un rollo de cobre antiguo y corroído con inscripciones",
    "beale": "una hoja amarillenta llena de números cifrados",
    "dorabella": "una nota con símbolos en forma de semicírculos",
    "monumento": "un monumento de piedra con las letras «O U O S V A V V»",
    "sabana": "una sábana de lino antigua con una figura tenue",
    "engranajes": "un mecanismo de bronce corroído lleno de engranajes",
    "diamante": "un enorme diamante azul profundo brillando en la oscuridad",
    "max": "un televisor antiguo con la señal interrumpida por una figura enmascarada",
    "cigarra": "una pantalla de computadora con la imagen de una cigarra y el número 3301",
}
RUINAS = {
    "escalonada": "una pirámide escalonada en medio de la selva", "olmeca": "una cabeza colosal olmeca de piedra",
    "moai": "los moáis gigantes de la Isla de Pascua frente al océano", "tpilares": "pilares de piedra en forma de T "
    "con animales tallados", "estepa": "la estepa de Mongolia con caballos y yurtas", "nazca": "el colibrí gigante "
    "de Nazca visto desde el aire en el desierto", "torre": "la Torre de Londres de noche", "tumba": "la entrada a una "
    "tumba antigua en el desierto", "columnas": "columnas antiguas en ruinas", "piedras": "un círculo de piedras "
    "gigantes", "esfera": "esferas de piedra perfectas en la selva",
}
COLOR_TEXTO = ["amarilla", "roja", "blanca", "naranja"]


def detalle_visual(n, g):
    det = DETALLES.get(n, {})
    partes = []
    if det.get("av"):
        partes.append(AVIONES[det["av"]])
    if det.get("bar"):
        partes.append(BARCOS[det["bar"]])
    if det.get("obj"):
        partes.append(OBJETOS[det["obj"]])
    if det.get("rui"):
        partes.append(RUINAS.get(det["rui"], ""))
    per = det.get("per")
    if per:
        per = per[0] if isinstance(per, list) else per
        ropa = {"parka_roja": "una joven con parka roja caminando sola hacia el bosque",
                "traje": "un hombre de traje y sombrero fedora de espaldas",
                "mujer1920": "una mujer elegante de los años 20", "mujer1910": "una joven de 1910 con abrigo oscuro",
                "explorador": "un explorador con sombrero y ropa caqui", "anciano": "un anciano de barba blanca con "
                "sombrero", "escalador": "dos alpinistas de 1924 con ropa antigua", "nino_verde": "dos niños de piel "
                "verde en una aldea medieval"}.get(per, "")
        if ropa:
            partes.append(ropa)
    if det.get("carpa"):
        partes.append("una carpa rasgada desde adentro en la nieve, de noche")
    return "; ".join(p for p in partes if p)


def prompt_miniatura(n, g):
    anio = (re.findall(r"\b(1[0-9]{3}|20[0-2][0-9])\b", g["desc"] + " " + g["titulo"]) or [""])[0]
    real = detalle_visual(n, g)
    texto = (g["canva"] or g["nombre"]).upper()
    color = COLOR_TEXTO[n % len(COLOR_TEXTO)]
    escena = g["escena"].rstrip(".")
    if real:
        escena += f". Detalles reales que deben verse: {real}"
    epoca = f" Época: {anio}, con ropa, vehículos y objetos de ese año." if anio else ""
    return (f"Crea una miniatura vertical 9:16 para YouTube Shorts, hiperrealista y cinematográfica, muy llamativa, "
            f"sobre «{g['nombre']}». Escena: {escena}.{epoca} Iluminación dramática con contraste alto, colores "
            f"intensos, niebla o rayos de luz para dar misterio, profundidad de campo y nitidez en el elemento "
            f"principal. Un círculo rojo brillante con una flecha resaltando el detalle más inquietante. Arriba, "
            f"texto enorme en mayúsculas con letra gruesa {color} y borde negro: «{texto}». Abajo, una etiqueta "
            f"pequeña roja que diga «MISTERIO SIN RESOLVER». Sin marcas de agua, sin logotipos y sin más texto.")


def descripcion(g):
    corta, *tags = g["desc"].split(" · ")
    return (f"{corta}\n\n¿Tú qué crees? Te leo en los comentarios 👇\n🔔 Suscríbete para más historias reales que "
            f"parecen inventadas.\n\n#shorts #misterio #misterios #misteriossinresolver #enigmas #historiasreales "
            f"#datoscuriosos #sabiasque #historia #curiosidades {' '.join(tags)}").strip()


def main():
    guiones = cargar_guiones()
    DESTINO.mkdir(exist_ok=True)
    videos = sorted((RAIZ / "misterios nuevos").glob("misterio_*.mp4"))
    hechos = {int(v.name[9:11]): v.stem for v in videos}
    if not hechos:  # aún renderizando: usar los audios verificados
        hechos = {int(p.name[9:11]): f"misterio_{int(p.name[9:11]):02d}_{slug(guiones[int(p.name[9:11])]['nombre'])}"
                  for p in (RAIZ / "audios" / "misterios").glob("misterio_*_voz.mp3")}
    indice = ["# Textos de los misterios nuevos", "",
              "Cada archivo tiene el **título**, la **descripción** y el **prompt de miniatura para ChatGPT** del "
              "video con el mismo nombre en la carpeta «misterios nuevos».", "",
              "| # | Video | Título |", "|---|---|---|"]
    for n in sorted(hechos):
        g = guiones[n]
        nombre = hechos[n]
        (DESTINO / f"{nombre}.md").write_text(
            f"# {n:02d} · {g['nombre']}\n\nVideo: `misterios nuevos/{nombre}.mp4`\n\n"
            f"## Título\n\n{g['titulo']}\n\n## Descripción\n\n{descripcion(g)}\n\n"
            f"## Prompt de miniatura (ChatGPT)\n\n{prompt_miniatura(n, g)}\n", encoding="utf-8")
        indice.append(f"| {n:02d} | {nombre}.mp4 | {g['titulo'].split(' #')[0]} |")
    (DESTINO / "README.md").write_text("\n".join(indice) + "\n", encoding="utf-8")
    print(len(hechos), "textos")


if __name__ == "__main__":
    main()
