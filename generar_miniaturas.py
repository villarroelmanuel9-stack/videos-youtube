#!/usr/bin/env python3
"""
Miniaturas verticales 9:16 de la serie «Misterios sin resolver» con OpenAI gpt-image-2 (skill gpt-image-2, preset
short-misterio). Toma la escena y el texto de cada misterio («textos misterios nuevos»), redacta el prompt en inglés
con los detalles reales y guarda cada imagen en la carpeta «Miniaturas» con el mismo nombre que su video.

La clave de OpenAI NO está en este archivo: en la nube la agrega el proxy del entorno; en tu computador, exporta
OPENAI_API_KEY antes de correrlo.

    python generar_miniaturas.py            # todas las que falten
    python generar_miniaturas.py 2 3        # solo algunas
"""
from __future__ import annotations

import base64
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

from misterios import slug
from verificar_misterios import cargar_guiones

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "Miniaturas"
TAM, CALIDAD = "1008x1792", "high"

# Escena de cada miniatura, en inglés, con los detalles reales de la historia
ESCENAS = {
    1: "an old 19th-century wooden brigantine drifting alone in thick fog, empty deck, sails half set, on a table below deck plates of food still served",
    2: "five navy-blue TBM Avenger torpedo bombers with white bellies and US stars flying in formation over a stormy sea at sunset, a broken compass in the foreground",
    3: "a white Boeing 777 with red and blue stripes on the tail flying at night over a dark ocean, an empty green radar screen in the foreground",
    4: "a 1930s female aviator with leather cap and goggles in the cockpit of a polished silver twin-engine Lockheed Electra above the Pacific, a tiny island far below",
    5: "a lonely white lighthouse on a rocky Scottish island in a violent storm, huge waves, its light turned off",
    7: "a tent slashed open from the inside on a snowy mountain slope at night, flashlights lying in the snow, footprints walking away into the dark",
    8: "a large flat radio telescope field under a starry sky, in the foreground a computer printout with columns of numbers and the code 6EQUJ5 circled in red ink with the handwritten word Wow!",
    9: "an ancient open book with strange unknown letters and drawings of impossible plants, lit by a single candle",
    10: "an old letter covered in coded cipher symbols on a desk, the dark silhouette of a man behind a rainy window, 1969 San Francisco",
    11: "a foggy Victorian London alley in 1888 with gas lamps and wet cobblestones, a silhouette in a top hat and long coat",
    12: "an Australian beach at dawn in 1948, a hat and a tiny rolled scrap of paper in the sand, an old book of poems",
    13: "an open suitcase with wigs, passports and coded notes, a snowy Norwegian valley in the background",
    14: "a silver 1940s four-engine propeller airliner flying between snowy Andes peaks, an old telegraph radio with a paper strip reading STENDEC",
    15: "a five-masted schooner with all sails set run aground among breaking waves, empty deck, fog, a black and white spiral lighthouse on the shore",
    16: "a huge grey US Navy coal ship with many cargo cranes sailing into a storm in the Caribbean",
    17: "a small white wooden motor vessel half sunk and listing heavily on a calm blue sea, empty deck",
    18: "a four-engine Lockheed Super Constellation propeller airliner with triple tail flying at night over the ocean, a distant flash in the sky",
    20: "a 1909 passenger steamship with black hull, coffee-colored upper decks and a black funnel with a white band, sailing toward a giant wave at sunset",
    21: "a small white Cessna with red stripes over the sea at night, a huge object with green lights hovering above it, the cockpit lit",
    22: "a hydrogen balloon with a wicker basket over the Arctic pack ice, an old camera and a diary lying in the snow",
    23: "two 1920s mountaineers in tweed jackets with ropes and goggles climbing a snowy ridge just below the summit of Everest",
    24: "a 1920s explorer with a wide-brimmed hat pushing through dense Amazon jungle, ruins covered in vines in the background",
    25: "an old man with white beard and hat on horseback in the Chihuahua desert, Mexican revolutionary riders in the background",
    26: "a single-engine olive-drab Noorduyn Norseman plane flying low over the English Channel in thick fog, a trombone in the foreground",
    27: "a blue-grey twin-boom P-38 Lightning over the bright Mediterranean sea, a silver bracelet glinting on the sea floor, a tiny lonely planet with a single rose in the sky",
    28: "a young 1930s physicist in a suit on the deck of a night ferry, a blackboard full of equations behind him",
    29: "a man in swim trunks walking into a rough grey sea from a rocky Australian beach, stormy clouds",
    30: "an 1890 steam train at night, an antique wooden movie camera on an empty seat in the carriage",
    31: "a man in a white shirt walking alone along a misty Malaysian jungle path, colorful Thai silk fabrics hanging",
    32: "a 1920s car abandoned beside a lake at dawn, a woman's cloche hat on the seat",
    33: "a 1970s restaurant parking lot at sunset near Detroit, an empty car with its door open",
    34: "a 1940s diplomat in a hat handing protective passports to a crowd on a snowy Budapest street",
    35: "a teenage boy in peasant clothes standing in a medieval German town square in 1828, holding a letter",
    36: "two young princes in 15th-century royal clothes in a dark stone tower lit by candles",
    37: "a wooden house burning on a snowy night, an old roadside billboard nearby",
    38: "a forest trail in Vermont in autumn with fog, a young woman in a red parka walking away, an abandoned backpack",
    39: "a Brazilian hilltop at night with two crude lead eye masks lying on the grass next to a handwritten note",
    40: "an old television in a dark room showing a masked face with rotating striped background and static",
    41: "a cicada drawn on a poster stuck to a street pole at night, a glowing screen with code",
    42: "a prehistoric man in fur clothing on a snowy Alpine ridge, an arrow flying through the air",
    43: "an ancient Egyptian tunnel lit by torches, a golden queen's mask glowing in the darkness",
    44: "a golden sarcophagus in a marble chamber with a beam of light entering from above",
    45: "the Mongolian steppe with hundreds of horses galloping under a dramatic sky",
    46: "an ancient library with shelves full of papyrus scrolls and columns, flames in the background",
    47: "an ancient city of circular temples sinking into a stormy sea",
    48: "a fleet of ancient ships with square sails and bird-head prows arriving at a burning coast",
    49: "a Maya stepped pyramid covered by jungle at dawn, fog between the trees",
    50: "the Pyramid of the Sun and the Avenue of the Dead at Teotihuacan at sunset, golden mist",
    51: "a colossal Olmec stone head in the jungle, ancient people pulling it with ropes",
    52: "aerial view of the Peruvian desert with the giant Nazca hummingbird geoglyph, a small plane flying over it",
    53: "Stonehenge at solstice sunrise, sun rays shining between the stones",
    54: "T-shaped stone pillars carved with foxes and boars on a hill at sunset, Gobekli Tepe",
    55: "moai statues on a green hill facing the Pacific, ropes tied to one of them",
    56: "an ancient wooden tablet engraved with rongorongo glyphs under warm light",
    57: "a clay tablet with ancient Linear A signs, the red-columned Minoan palace of Knossos in the background",
    58: "a clay disc with symbols stamped in a spiral, lit inside a dark museum display case",
    59: "stone seals with a unicorn and symbols, brick ruins of Mohenjo-daro in the background",
    60: "a corroded bronze mechanism full of gears on the sea floor with rays of light",
    61: "an ancient parchment map with coastlines, compass roses and ships, a brass compass and a candle",
    62: "an ancient linen cloth with a faint image spread out in a cathedral lit by candles",
    63: "a corroded copper scroll in a desert cave lit by a lantern",
    64: "a half-buried treasure chest in a Virginia forest, papers covered with numbers",
    65: "an old letter with curved symbols resting on a grand piano, a quill and inkwell",
    66: "a stone monument in an English garden engraved with the eight letters OUOSVAVV, fog",
    67: "a deep shaft on a wooded island with lanterns and ropes, water at the bottom",
    68: "a misty tropical island with waterfalls, a chest of gold and crosses in a cave",
    69: "a raft on a mountain lagoon at dawn with a man covered in gold dust throwing offerings into the water",
    70: "golden Inca ruins hidden in a misty jungle, an explorer with a machete",
    71: "fog-covered Ecuadorian mountains, a dark lagoon and gold glowing in a cave",
    72: "red desert mountains of Arizona at sunset, a pickaxe and lantern beside a mine entrance",
    73: "a room with glowing golden amber walls, wooden packing crates on the floor",
    74: "an old locomotive inside a dark tunnel with crates of gold, a flashlight beam",
    75: "a Siberian forest with thousands of trees knocked down in a circle, orange sky",
    76: "a snowy Norwegian valley at night with glowing orbs of light floating above the mountains",
    77: "the Texas desert at night with floating lights on the horizon, starry sky",
    78: "an adobe town in the New Mexico desert at night, faint sound waves rippling in the sky",
    79: "a snowy English village at dawn in 1855 with hoof-like footprints going over a rooftop and a wall",
    80: "two medieval children with greenish skin beside a wheat field, surprised villagers",
    81: "a 19th-century Kentucky farm with red chunks falling from a clear sky, a woman looking up",
    82: "a grey F/A-18 fighter jet over the ocean chasing a white wingless object shaped like a Tic Tac",
    83: "a city at night with giant V-shaped lights in the sky, people looking up",
    84: "a desert ranch with shiny metallic debris scattered, 1940s soldiers",
    85: "a Scottish loch with fog and a long-necked silhouette rising from the water, a ruined castle",
    86: "a shadowy creature with spines on its back in a goat pen at night under the moon",
    87: "a rusty freighter on a dark sea with smoke, an old radio glowing in an empty cabin",
    88: "a modern white catamaran drifting on a blue sea, a laptop on and food on the table, nobody aboard",
    89: "a 1910 New York street in winter, an elegant young woman walking alone into the fog",
    90: "a small sloop sailing alone on the open sea at sunset, a bearded sailor at the helm",
    91: "a capsized catamaran on a murky sea near a mangrove coast, a young man with glasses swimming",
    92: "a painted Egyptian tomb wall with a hint of a secret door, a queen's bust with a blue crown in the shadows",
    93: "moss-covered stone sculptures in dense Honduran jungle, rays of light through the trees",
    94: "a huge deep-blue diamond glowing in a necklace on black velvet, an old mail envelope",
    95: "the deep dark ocean with sound waves and a hint of a gigantic silhouette",
    96: "a diver swimming beside huge underwater stone terraces in blue water",
    97: "a huge perfect stone sphere in a tropical jungle clearing, a small person beside it for scale",
    98: "two 19th-century sailing ships trapped in Arctic ice under a grey sky",
}
COLORES = ["bright yellow", "white", "red", "orange"]
_alto = threading.Event()
_lock = threading.Lock()


def prompt_de(n, g):
    anio = (re.findall(r"\b(1[0-9]{3}|20[0-2][0-9])\b", g["desc"] + " " + g["titulo"]) or [""])[0]
    texto = (g["canva"] or g["nombre"]).upper()
    epoca = f" Year {anio}: vehicles, clothing and places historically accurate for that year." if anio else ""
    return (f"Vertical 9:16 YouTube Shorts thumbnail, cinematic hyperrealistic photograph. Scene: {ESCENAS[n]}."
            f"{epoca} Dramatic high-contrast lighting, mist and light rays for mystery, shallow depth of field, the main "
            f"subject sharp and centered. A glowing red circle with an arrow highlighting the most unsettling detail. "
            f"At the top, huge bold ALL CAPS text, {COLORES[n % 4]} with a thick black outline: \"{texto}\". In the "
            f"lower third, a small red label with white text: \"MISTERIO SIN RESOLVER\". Text exactly as written, in "
            f"Spanish. Keep the bottom 15% free of important elements. No watermark. No logos. No extra text.")


def llamar(cuerpo):
    r = subprocess.run(["curl", "-s", "-X", "POST", "https://api.openai.com/v1/images/generations",
                        "-H", f"Authorization: Bearer {os.environ.get('OPENAI_API_KEY') or 'proxy-injected'}",
                        "-H", "Content-Type: application/json", "--max-time", "300", "-d", json.dumps(cuerpo)],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": {"message": (r.stdout or r.stderr)[:300], "code": "respuesta_invalida"}}


def generar(n, g, nombre):
    if _alto.is_set():
        return n, "omitida"
    salida = DESTINO / f"{nombre}.jpg"
    cuerpo = {"model": "gpt-image-2", "prompt": prompt_de(n, g), "size": TAM, "quality": CALIDAD, "n": 1}
    for intento in range(5):
        r = llamar(cuerpo)
        if "error" not in r:
            im = Image.open(io.BytesIO(base64.b64decode(r["data"][0]["b64_json"]))).convert("RGB")
            im.save(salida, "JPEG", quality=90, optimize=True)  # YouTube acepta miniaturas de hasta 2 MB
            with _lock:
                print(f"✔ {nombre}.jpg", flush=True)
            return n, "ok"
        err = r["error"]
        codigo, msg = str(err.get("code") or err.get("type") or ""), str(err.get("message", ""))
        if any(k in (codigo + msg).lower() for k in ("insufficient_quota", "billing", "quota", "invalid_api_key")):
            _alto.set()
            with _lock:
                print(f"✗ sin saldo o clave inválida: {msg[:200]}", flush=True)
            return n, "sin_saldo"
        if "rate" in (codigo + msg).lower() or "429" in msg:
            time.sleep(30 * (intento + 1))
            continue
        with _lock:
            print(f"✗ {nombre}: {msg[:200]}", flush=True)
        if "safety" in msg.lower() or "moderation" in (codigo + msg).lower():
            return n, "rechazada"
        time.sleep(10)
    return n, "error"


def main():
    guiones = cargar_guiones()
    DESTINO.mkdir(exist_ok=True)
    nums = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(ESCENAS)
    trabajos = []
    for n in nums:
        nombre = f"misterio_{n:02d}_{slug(guiones[n]['nombre'])}"
        if not (DESTINO / f"{nombre}.jpg").exists():
            trabajos.append((n, guiones[n], nombre))
    print(f"{len(trabajos)} miniaturas por generar", flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        resultados = list(ex.map(lambda a: generar(*a), trabajos))
    resumen = {}
    for n, est in resultados:
        resumen.setdefault(est, []).append(n)
    print("RESUMEN", json.dumps(resumen), flush=True)


if __name__ == "__main__":
    main()
