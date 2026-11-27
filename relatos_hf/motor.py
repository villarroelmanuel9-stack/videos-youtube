#!/usr/bin/env python3
"""
Relatos en HyperFrames: convierte un guion de guiones/historias_100.md + su audio + un plan visual en un video
vertical de 45–46 s.

    python3 relatos_hf/motor.py 30            # usa audios/relatos/relato_030.mp3 y relatos_hf/planes/relato_030.json
    python3 relatos_hf/motor.py 30 --sin-render   # solo arma el proyecto (para revisarlo con snapshot)

Pasos:
  1. Tiempos de cada palabra con faster-whisper (se guardan en <audio>.palabras.json) alineados al guion.
  2. Estira el audio con pausas cortas entre párrafos hasta llegar a ≈45,5 s.
  3. Ancla cada toma del plan a la frase del guion donde empieza («en»).
  4. Escribe el proyecto HyperFrames (HTML + GSAP): fondo animado, tomas (títulos, mapas reales, fechas,
     contadores, sismógrafo, íconos, pregunta final), subtítulos palabra por palabra, barra de progreso.
  5. Mezcla voz + ambiente + barridos en cada corte + efectos del plan (pro.py / mezcla_audio.py).
  6. Renderiza con HyperFrames a 1080×1920, 30 fps, calidad «delivery».
"""
from __future__ import annotations

import argparse
import difflib
import html as H
import json
import math
import random
import re
import shutil
import subprocess
import sys
import unicodedata
import wave
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI))

import mapa  # noqa: E402

GUION = RAIZ / "guiones" / "historias_100.md"
PLANES = AQUI / "planes"
PROYECTOS = AQUI / "proyectos"
AUDIOS = RAIZ / "audios" / "relatos"
SALIDA = RAIZ / "historias nuevas"
HF = "hyperframes@0.9.40"
W, Hh = 1080, 1920
SR = 44100
OBJETIVO = 45.5
INICIO = 0.35
COLA_MIN = 1.2

TEMAS = {  # fondo1, fondo2, acento, partículas
    "historia": ("#2a1a10", "#0c0705", "#FFB627", "#ffd9a0"),
    "tierra": ("#3a1c0c", "#0d0604", "#FF7A1A", "#ffc58a"),
    "terror": ("#0f1a14", "#020403", "#7CFF6B", "#a9c7b5"),
    "misterio": ("#121b33", "#03050b", "#4FD1FF", "#b8c8ee"),
    "ciencia": ("#0b2240", "#020812", "#3DE0FF", "#aee8ff"),
    "cultura": ("#2b1033", "#0a030d", "#FF5FA2", "#f2b8ff"),
    "gamer": ("#1d0b3a", "#05020d", "#B26BFF", "#e0c2ff"),
    "guerra": ("#26261a", "#070705", "#E3C14B", "#d9d3a8"),
}
ROJO, AMARILLO = "#E3141B", "#FFD21F"


# --------------------------------------------------------------------------- guion y tiempos
def norm(p: str) -> str:
    p = unicodedata.normalize("NFD", p.lower())
    return "".join(c for c in p if c.isalnum())


def cargar_guion(n: int):
    txt = GUION.read_text(encoding="utf-8")
    bloques = dict((int(a), (b.strip(), c)) for a, b, c in re.findall(r"\n## (\d+) · (.*?)\n(.*?)(?=\n## \d+ · |\Z)", txt, re.S))
    nombre, cuerpo = bloques[n]
    voz = re.search(r"```\n(.*?)```", cuerpo, re.S).group(1).strip()
    parrafos = []
    for ln in voz.splitlines():
        m = re.match(r"\[([^\]]+)\]\s*(.*)", ln.strip())
        if m:
            parrafos.append((m.group(1).strip().lower(), m.group(2).strip()))
    return nombre, parrafos


def oidas(audio: Path):
    cache = Path(str(audio) + ".palabras.json")
    if cache.exists() and cache.stat().st_mtime >= audio.stat().st_mtime:
        return [tuple(x) for x in json.loads(cache.read_text(encoding="utf-8"))]
    from faster_whisper import WhisperModel
    crudo = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(audio), "-ac", "1", "-ar", "16000", "-f",
                            "f32le", "-"], capture_output=True, check=True).stdout
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(np.frombuffer(crudo, np.float32), language="es", word_timestamps=True)
    res = [(x.word.strip(), float(x.start), float(x.end)) for sg in segs for x in sg.words]
    cache.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    return res


def alinear(palabras: list[str], escuchadas, dur: float):
    t = [None] * len(palabras)
    sm = difflib.SequenceMatcher(None, [norm(w) for w in palabras], [norm(w) for w, _, _ in escuchadas],
                                 autojunk=False)
    for a, b, k in sm.get_matching_blocks():
        for i in range(k):
            t[a + i] = (escuchadas[b + i][1], escuchadas[b + i][2])
    conocidos = [i for i, x in enumerate(t) if x]
    bordes = [(-1, (0.0, 0.0))] + [(i, t[i]) for i in conocidos] + [(len(palabras), (dur, dur))]
    for (ia, ta), (ib, tb) in zip(bordes, bordes[1:]):
        hueco = list(range(ia + 1, ib))
        if not hueco:
            continue
        t0, t1 = ta[1], max(ta[1], tb[0])
        pesos = [len(palabras[i]) + 1 for i in hueco]
        acc, tot = t0, sum(pesos)
        for i, p in zip(hueco, pesos):
            d = (t1 - t0) * p / tot
            t[i] = (acc, acc + d)
            acc += d
    return t


def leer_audio(ruta: Path) -> np.ndarray:
    crudo = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(ruta), "-ac", "2", "-ar", str(SR), "-f", "f32le",
                            "-"], capture_output=True, check=True).stdout
    return np.frombuffer(crudo, np.float32).reshape(-1, 2).copy()


def plan_tiempo(D: float, npar: int):
    """Decide ritmo de la voz, pausas entre párrafos, entrada y cola para cerrar en OBJETIVO s sin forzar la voz."""
    lead, cola_base, pausa_base = 0.4, 1.8, 0.45
    huecos = max(1, npar - 1)
    vt = OBJETIVO - lead - cola_base - pausa_base * huecos
    tempo = min(1.15, max(0.86, D / vt))
    if abs(tempo - 1) < 0.015:
        tempo = 1.0
    V = D / tempo
    resto = OBJETIVO - lead - V - cola_base - pausa_base * huecos
    pausa = min(1.3, max(0.25, pausa_base + resto / huecos))
    cola = min(4.8, max(1.5, OBJETIVO - lead - V - pausa * huecos))
    return tempo, lead, pausa, cola


def compactar_silencios(audio: Path, dir_: Path, maximo=0.5, deja=0.4):
    """Acorta silencios internos largos (los «…» de ElevenLabs) y devuelve (wav, función que mueve tiempos)."""
    x = leer_audio(audio)
    mono = np.abs(x).mean(1)
    win = int(0.02 * SR)
    n = len(mono) // win
    rms = np.sqrt((mono[:n * win].reshape(n, win) ** 2).mean(1) + 1e-12)
    umbral = max(10 ** (-42 / 20), np.percentile(rms, 90) * 0.03)
    quietos = rms < umbral
    cortes, k = [], 0
    while k < n:
        if quietos[k]:
            j = k
            while j < n and quietos[j]:
                j += 1
            if k > 0 and j < n and (j - k) * 0.02 > maximo:
                cortes.append((k * 0.02 + deja / 2, j * 0.02 - deja / 2))
            k = j
        else:
            k += 1
    trozos, prev = [], 0.0
    for a, b in cortes:
        trozos.append(x[int(prev * SR):int(a * SR)])
        prev = b
    trozos.append(x[int(prev * SR):])
    y = np.concatenate(trozos) if trozos else x
    destino = dir_ / "assets" / "voz_compacta.wav"
    escribir_wav(destino, y)

    def mover(t):
        quitado = sum(min(b, max(a, t)) - a for a, b in cortes)
        return t - quitado
    return destino, mover, len(y) / SR


def procesar_voz(audio: Path, tempo: float, dir_: Path) -> np.ndarray:
    """Ritmo con rubberband (sin cambiar el tono), limpieza de graves, presencia y compresión suave."""
    filtros = []
    if tempo != 1.0:
        filtros.append(f"rubberband=tempo={tempo:.4f}:transients=smooth:window=standard")
    filtros += ["highpass=f=75", "equalizer=f=250:t=q:w=1:g=-1.5", "equalizer=f=3200:t=q:w=1.2:g=2",
                "acompressor=threshold=-20dB:ratio=2.2:attack=8:release=140:makeup=2", "deesser=i=0.35"]
    destino = dir_ / "assets" / "voz.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(audio), "-af", ",".join(filtros), "-ac", "2",
                    "-ar", str(SR), str(destino)], check=True)
    return leer_audio(destino)


def estirar(voz: np.ndarray, tiempos, fin_parrafo: list[int], lead: float, pausa: float, cola: float):
    """Inserta la entrada, las pausas entre párrafos y la cola. Devuelve voz, tiempos, total y cortes de párrafo."""
    cortes = []
    for i in fin_parrafo[:-1]:
        a, b = tiempos[i][1], tiempos[i + 1][0]
        cortes.append(min(b - 0.02, a + 0.12))
    trozos, prev = [np.zeros((int(lead * SR), 2), np.float32)], 0
    for c in cortes:
        s = int(c * SR)
        trozos += [voz[prev:s], np.zeros((int(pausa * SR), 2), np.float32)]
        prev = s
    trozos.append(voz[prev:])
    nueva = np.concatenate(trozos)
    total = round(len(nueva) / SR + cola, 2)

    def mover(x):
        return x + lead + pausa * sum(1 for c in cortes if x > c)
    return nueva, [(mover(a), mover(b)) for a, b in tiempos], total, [mover(c) for c in cortes]


# --------------------------------------------------------------------------- piezas visuales
def esc(s) -> str:
    return H.escape(str(s), quote=True)


def txt_borde(px: int, ancho: int | None = None) -> str:
    a = ancho or max(4, round(px / 13))
    return f"-webkit-text-stroke:{a}px #000; paint-order:stroke fill;"


class Toma:
    """Acumula el HTML y las líneas de GSAP de una toma."""

    def __init__(self, i: int, t0: float, dur: float, p: dict, tema, emocion: str):
        self.i, self.t0, self.dur, self.p, self.tema, self.emo = i, t0, dur, p, tema, emocion
        self.estilo = ESTILOS[0]
        self.id = f"t{i}"
        self.html: list[str] = []
        self.js: list[str] = []

    def at(self, dt: float) -> str:
        return f"{self.t0 + dt:.3f}"

    def tw(self, sel, desde, hasta, dt, extra=""):
        self.js.append(f'tl.fromTo("{sel}", {desde}, {{...{hasta}, {extra}}}, {self.at(dt)});' if extra else
                       f'tl.fromTo("{sel}", {desde}, {hasta}, {self.at(dt)});')

    def to(self, sel, props, dt):
        self.js.append(f'tl.to("{sel}", {props}, {self.at(dt)});')


def bloque_texto(id_, lineas, top, tam, acento_idx=None, color="#fff", acento=ROJO):
    out = []
    for k, ln in enumerate(lineas):
        col = acento if k == acento_idx else color
        out.append(f'<div id="{id_}l{k}" class="lin" style="font-size:{tam}px;color:{col};{txt_borde(tam)}">{esc(ln)}</div>')
    return f'<div id="{id_}" class="bloque" style="top:{top}px">{"".join(out)}</div>'


def ajustar(lineas, maximo=230, ancho=960):
    largo = max(len(l) for l in lineas)
    return int(min(maximo, ancho / max(1, largo) * 1.85))


def toma_titulo(t: Toma):
    p = t.p
    lineas = p["lineas"]
    tam = p.get("tam") or ajustar(lineas)
    alto = tam * 1.02 * len(lineas)
    top = int(700 - alto / 2)
    if p.get("icono"):
        t.html.append(f'<div id="{t.id}ico" class="emoji" style="font-size:520px;top:{top - 120}px;opacity:.22">{p["icono"]}</div>')
        t.tw(f"#{t.id}ico", "{scale: 1.3, rotation: -8}", "{scale: 1, rotation: 0, duration: %.2f, ease: 'none'}" % t.dur, 0)
    t.html.append(bloque_texto(f"{t.id}b", lineas, top, tam, p.get("acento"), acento=p.get("color_acento", ROJO)))
    for k in range(len(lineas)):
        t.tw(f"#{t.id}bl{k}", "{scale: 2.4, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.22, ease: 'power4.out'}",
             0.05 + 0.14 * k)
    t.to(f"#{t.id}b", "{scale: 1.06, duration: %.2f, ease: 'none'}" % max(0.3, t.dur - 0.4), 0.4)


def toma_fecha(t: Toma):
    p = t.p
    a = t.tema[2]
    hora = (f'<div id="{t.id}h" class="chipx" style="top:1010px;font-size:58px">🕒 {esc(p["hora"])}</div>'
            if p.get("hora") else "")
    t.html.append(f'''<div id="{t.id}c" class="cal" style="top:330px">
  <div class="calTop" style="background:{ROJO}">{esc(p.get("mes", ""))}</div>
  <div class="calDia">{esc(p.get("dia", ""))}</div>
</div>
<div id="{t.id}a" class="lin solo" style="top:860px;font-size:150px;color:{a};{txt_borde(150)}">{esc(p.get("anio", ""))}</div>{hora}''')
    t.tw(f"#{t.id}c", "{rotationX: -95, opacity: 0, transformPerspective: 900}",
         "{rotationX: 0, opacity: 1, duration: 0.45, ease: 'back.out(1.6)'}", 0.05)
    t.tw(f"#{t.id}a", "{y: 80, opacity: 0}", "{y: 0, opacity: 1, duration: 0.3, ease: 'power3.out'}", 0.3)
    if hora:
        t.tw(f"#{t.id}h", "{scale: 0.5, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.25, ease: 'back.out(2)'}", 0.6)
    t.to(f"#{t.id}c", "{scale: 1.05, duration: %.2f, ease: 'none'}" % max(0.3, t.dur - 0.5), 0.5)


def fmt_num(v: float, dec: int) -> str:
    s = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def toma_contador(t: Toma):
    p = t.p
    dec = int(p.get("decimales", 0))
    hasta, desde = float(p["hasta"]), float(p.get("desde", 0))
    tam = p.get("tam", 300)
    ico = (f'<div id="{t.id}ico" class="emoji" style="font-size:230px;top:300px">{p["icono"]}</div>'
           if p.get("icono") else "")
    top_num = 560 if ico else 430
    t.html.append(f'''{ico}<div id="{t.id}n" class="lin solo" style="top:{top_num}px;font-size:{tam}px;color:{t.tema[2]};{txt_borde(tam)}">{fmt_num(hasta, dec)}</div>
<div id="{t.id}u" class="lin solo" style="top:{top_num + tam * 1.02:.0f}px;font-size:96px;color:#fff;{txt_borde(96)}">{esc(p.get("unidad", ""))}</div>
<div id="{t.id}s" class="chipx" style="top:{top_num + tam * 1.02 + 130:.0f}px">{esc(p.get("sub", ""))}</div>''')
    if ico:
        t.tw(f"#{t.id}ico", "{scale: 0, rotation: -30}", "{scale: 1, rotation: 0, duration: 0.35, ease: 'back.out(2)'}", 0)
    cuenta = min(1.4, max(0.6, t.dur * 0.45))
    t.js.append(f'(() => {{ const o = {{v: {desde}}}; const el = document.getElementById("{t.id}n"); '
                f'const f = (v) => v.toLocaleString("es-CL", {{minimumFractionDigits: {dec}, maximumFractionDigits: {dec}}}); '
                f'tl.fromTo(o, {{v: {desde}}}, {{v: {hasta}, duration: {cuenta:.2f}, ease: "power2.out", '
                f'onUpdate: () => {{ el.textContent = f(o.v); }}}}, {t.at(0.05)}); }})();')
    t.tw(f"#{t.id}n", "{scale: 0.6, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.25, ease: 'back.out(2)'}", 0.02)
    t.to(f"#{t.id}n", "{scale: 1.15, duration: 0.12, yoyo: true, repeat: 1, ease: 'power2.out'}", 0.05 + cuenta)
    t.tw(f"#{t.id}u", "{y: 60, opacity: 0}", "{y: 0, opacity: 1, duration: 0.25}", 0.2)
    if p.get("sub"):
        t.tw(f"#{t.id}s", "{scale: 0.4, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.25, ease: 'back.out(2)'}",
             0.15 + cuenta)


def toma_sismo(t: Toma):
    p = t.p
    rng = random.Random(t.i * 31 + 5)
    pts = []
    for k in range(240):
        x = 40 + k * 4.2
        amp = 8 + 210 * (min(1, k / 140) ** 2) * (1 if k < 200 else max(0.2, 1 - (k - 200) / 40))
        y = 300 + rng.uniform(-1, 1) * amp
        pts.append((round(x), round(y)))
    largo = int(sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))) + 20
    pts = [f"{x},{y}" for x, y in pts]
    t.html.append(f'''<svg id="{t.id}g" class="full" viewBox="0 0 1080 600" style="top:520px;height:600px">
  <rect x="20" y="40" width="1040" height="520" rx="26" fill="rgba(0,0,0,.45)" stroke="rgba(255,255,255,.18)" stroke-width="3"/>
  {"".join(f'<line x1="20" x2="1060" y1="{y}" y2="{y}" stroke="rgba(255,255,255,.08)" stroke-width="2"/>' for y in range(100, 560, 60))}
  <polyline id="{t.id}p" points="{" ".join(pts)}" fill="none" stroke="{t.tema[2]}" stroke-width="7" stroke-linejoin="round"
    stroke-dasharray="{largo}" stroke-dashoffset="{largo}"/>
</svg>
<div id="{t.id}x" class="lin solo" style="top:330px;font-size:150px;color:#fff;{txt_borde(150)}">{esc(p.get("texto", ""))}</div>''')
    t.tw(f"#{t.id}p", "{attr: {'stroke-dashoffset': %d}}" % largo,
         "{attr: {'stroke-dashoffset': 0}, duration: %.2f, ease: 'none'}" % max(0.5, t.dur - 0.3), 0)
    t.tw(f"#{t.id}x", "{scale: 2, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.25, ease: 'power4.out'}", 0.1)


def _vista(lat, lon, zoom, proyectar, cy=760):
    x, y = proyectar(lat, lon)
    s = 0.3 * zoom
    return {"x": round(540 - x * s, 1), "y": round(cy - y * s, 1), "scale": round(s, 4)}


def toma_mapa(t: Toma):
    p = t.p
    lat, lon = p["centro"]
    centro_lon = p.get("centro_lon", lon if abs(lon) > 120 else 0)
    zoom, zoom0 = float(p.get("zoom", 4)), float(p.get("zoom_desde", max(1.0, float(p.get("zoom", 4)) / 3)))
    lat0, lon0 = p.get("centro_desde", [lat, lon])
    resaltar = {n: p.get("color_pais", ROJO) for n in p.get("resaltar", [])}
    paises, proyectar = mapa.svg_mundo(centro_lon, resaltar, "50m" if zoom >= 3.5 else "110m",
                                       tierra=p.get("tierra", "#33476b"))
    v0, v1 = _vista(lat0, lon0, zoom0, proyectar), _vista(lat, lon, zoom, proyectar)
    rejilla = "".join(f'<line x1="0" x2="3600" y1="{y}" y2="{y}"/>' for y in range(0, 1801, 150)) + \
              "".join(f'<line y1="0" y2="1800" x1="{x}" x2="{x}"/>' for x in range(0, 3601, 150))

    def pantalla(la, lo):
        x, y = proyectar(la, lo)
        return round(x * v1["scale"] + v1["x"], 1), round(y * v1["scale"] + v1["y"], 1)

    capas = []
    llegada = 0.75
    # ruta animada (curvas) en coordenadas de pantalla al final del movimiento de cámara
    if p.get("ruta"):
        pts = [pantalla(*q) for q in p["ruta"]]
        d, largo = f"M{pts[0][0]},{pts[0][1]}", 0.0
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            cx, cyy = (x0 + x1) / 2, min(y0, y1) - abs(x1 - x0) * 0.25 - 40
            d += f" Q{cx:.0f},{cyy:.0f} {x1},{y1}"
            prev = (x0, y0)
            for k in range(1, 21):
                u = k / 20
                bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1
                by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cyy + u * u * y1
                largo += math.dist(prev, (bx, by))
                prev = (bx, by)
        largo = int(largo) + 10
        capas.append(f'<path id="{t.id}r" d="{d}" fill="none" stroke="{AMARILLO}" stroke-width="9" stroke-linecap="round" '
                     f'stroke-dasharray="{largo}" stroke-dashoffset="{largo}"/>')
        dur_r = max(0.8, min(t.dur - llegada - 0.3, 2.6))
        t.tw(f"#{t.id}r", "{attr: {'stroke-dashoffset': %d}}" % largo,
             "{attr: {'stroke-dashoffset': 0}, duration: %.2f, ease: 'power1.inOut'}" % dur_r, llegada)
    for k, q in enumerate(p.get("ondas", []) if isinstance(p.get("ondas", [None])[0], list) else
                          ([p["ondas"]] if p.get("ondas") else [])):
        x, y = pantalla(*q)
        for r in range(3):
            capas.append(f'<circle id="{t.id}o{k}{r}" cx="{x}" cy="{y}" r="30" fill="none" stroke="{ROJO}" stroke-width="6"/>')
            veces = max(0, int((t.dur - llegada) / 1.2) - 1)
            t.tw(f"#{t.id}o{k}{r}", "{attr: {r: 20}, opacity: 0.95}",
                 "{attr: {r: 260}, opacity: 0, duration: 1.2, ease: 'power1.out', repeat: %d}" % veces,
                 llegada + 0.4 * r)
    etiquetas = []
    for k, pin in enumerate(p.get("pines", [])):
        x, y = pantalla(pin["lat"], pin["lon"])
        capas.append(f'<g id="{t.id}pin{k}"><circle cx="{x}" cy="{y}" r="20" fill="{ROJO}" stroke="#fff" stroke-width="6"/></g>')
        ly = y - 120 if y > 520 else y + 50
        etiquetas.append(f'<div id="{t.id}lab{k}" class="pinlab" style="left:{x}px;top:{ly}px">{esc(pin["texto"])}</div>')
        dt = llegada + 0.15 + k * float(p.get("paso_pines", 0.35))
        t.tw(f"#{t.id}pin{k}", "{scale: 0, transformOrigin: '50% 50%'}", "{scale: 1, duration: 0.3, ease: 'back.out(3)'}", dt)
        t.tw(f"#{t.id}lab{k}", "{y: 30, opacity: 0, xPercent: -50}", "{y: 0, opacity: 1, xPercent: -50, duration: 0.25}", dt + 0.08)
    t.html.append(f'''<svg id="{t.id}m" class="full" viewBox="0 0 1080 1920" style="top:0;height:1920px">
  <defs><radialGradient id="{t.id}oc" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#16305a"/><stop offset="1" stop-color="#050c1c"/></radialGradient></defs>
  <rect width="1080" height="1920" fill="url(#{t.id}oc)"/>
  <g id="{t.id}cam"><g stroke="rgba(120,170,255,.10)" stroke-width="2">{rejilla}</g>{paises}</g>
  {"".join(capas)}
</svg>{"".join(etiquetas)}''')
    t.js.append(f'(() => {{ const c = {{x: {v0["x"]}, y: {v0["y"]}, s: {v0["scale"]}}}; const g = document.getElementById("{t.id}cam"); '
                f'const pon = () => g.setAttribute("transform", `translate(${{c.x}} ${{c.y}}) scale(${{c.s}})`); pon(); '
                f'tl.fromTo(c, {{x: {v0["x"]}, y: {v0["y"]}, s: {v0["scale"]}}}, {{x: {v1["x"]}, y: {v1["y"]}, s: {v1["scale"]}, '
                f'duration: {llegada}, ease: "power3.inOut", onUpdate: pon}}, {t.at(0)}); }})();')
    for n in resaltar:
        ident = "".join(c for c in n.lower() if c.isalnum())
        veces = max(0, int(t.dur / 0.5) - 2)
        t.tw(f"#pais-{ident}", "{opacity: 1}", "{opacity: 0.55, duration: 0.5, yoyo: true, repeat: %d, ease: 'sine.inOut'}" % veces,
             llegada)
    if p.get("titulo"):
        tam = p.get("tam", 120)
        t.html.append(f'<div id="{t.id}tt" class="lin solo" style="top:330px;font-size:{tam}px;color:#fff;{txt_borde(tam)}">{esc(p["titulo"])}</div>')
        t.tw(f"#{t.id}tt", "{y: -40, opacity: 0}", "{y: 0, opacity: 1, duration: 0.3, ease: 'power3.out'}", 0.2)


MOVS = {
    "pop": ("{scale: 0, rotation: -25}", "{scale: 1, rotation: 0, duration: 0.4, ease: 'back.out(2.2)'}"),
    "caer": ("{y: -900, rotation: -20}", "{y: 0, rotation: 0, duration: 0.5, ease: 'bounce.out'}"),
    "subir": ("{y: 700, opacity: 0}", "{y: 0, opacity: 1, duration: 0.5, ease: 'power3.out'}"),
    "zoom": ("{scale: 3, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.35, ease: 'power4.out'}"),
}


def toma_icono(t: Toma):
    p = t.p
    iconos = p.get("iconos", [])
    n = len(iconos)
    tam = p.get("tam_icono", 400 if n == 1 else 300 if n == 2 else 220)
    top = 330
    cajas = []
    for k, ic in enumerate(iconos):
        x = 540 + (k - (n - 1) / 2) * (tam * 1.1)
        cajas.append(f'<div id="{t.id}i{k}" class="emoji" style="font-size:{tam}px;top:{top}px;left:{x - tam * 0.6:.0f}px;width:{tam * 1.2:.0f}px">{ic}</div>')
    texto_top = top + tam * 1.25 + 20
    extra = ""
    if p.get("tachar"):
        extra = f'<svg id="{t.id}x" class="full" viewBox="0 0 1080 900" style="top:{top - 60}px;height:900px"><line x1="240" y1="120" x2="840" y2="{tam * 1.3:.0f}" stroke="{ROJO}" stroke-width="36" stroke-linecap="round" stroke-dasharray="900" stroke-dashoffset="900"/></svg>'
        t.tw(f"#{t.id}x line", "{attr: {'stroke-dashoffset': 900}}", "{attr: {'stroke-dashoffset': 0}, duration: 0.3, ease: 'power2.in'}",
             p.get("tachar_en", 0.8))
    t.html.append("".join(cajas) + extra)
    if p.get("texto"):
        tam_t = p.get("tam", ajustar([p["texto"]], 150))
        t.html.append(f'<div id="{t.id}t" class="lin solo" style="top:{texto_top:.0f}px;font-size:{tam_t}px;color:{p.get("color", "#fff")};{txt_borde(tam_t)}">{esc(p["texto"])}</div>')
        t.tw(f"#{t.id}t", "{scale: 1.8, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.22, ease: 'power4.out'}", 0.25)
    if p.get("sub"):
        t.html.append(f'<div id="{t.id}s" class="chipx" style="top:{texto_top + p.get("tam", 140) * 1.1 + 10:.0f}px">{esc(p["sub"])}</div>')
        t.tw(f"#{t.id}s", "{scale: 0.4, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.25, ease: 'back.out(2)'}", 0.5)
    mov = p.get("mov", "pop")
    for k in range(n):
        sel = f"#{t.id}i{k}"
        if mov in MOVS:
            a, b = MOVS[mov]
            t.tw(sel, a, b, 0.05 + 0.15 * k)
        elif mov == "hundir":
            t.tw(sel, "{y: 0, rotation: 0}", "{y: 260, rotation: 14, opacity: 0.35, duration: %.2f, ease: 'power2.in'}" % max(0.6, t.dur - 0.6), 0.3)
        elif mov == "erupcion":
            t.tw(sel, "{scale: 0.3, y: 200}", "{scale: 1, y: 0, duration: 0.35, ease: 'back.out(2)'}", 0)
            veces = max(0, int(t.dur / 0.16) - 4)
            t.to(sel, "{x: 10, duration: 0.08, yoyo: true, repeat: %d, ease: 'none'}" % veces, 0.35)
        elif mov == "latir":
            t.tw(sel, "{scale: 0}", "{scale: 1, duration: 0.3, ease: 'back.out(2)'}", 0.05 * k)
            veces = max(0, int(t.dur / 0.45) - 2)
            t.to(sel, "{scale: 1.12, duration: 0.22, yoyo: true, repeat: %d, ease: 'sine.inOut'}" % veces, 0.35)
        if mov in ("pop", "zoom", "caer", "subir") and t.dur > 1.2:
            t.to(sel, "{y: '-=24', duration: %.2f, ease: 'sine.inOut'}" % (t.dur - 0.7), 0.6)
    if p.get("particulas"):
        rng = random.Random(t.i)
        for k in range(18):
            x = 540 + rng.uniform(-160, 160)
            t.html.append(f'<div id="{t.id}pp{k}" class="part" style="left:{x:.0f}px;top:{top + tam * 0.25:.0f}px;background:{p["particulas"]}"></div>')
            t.tw(f"#{t.id}pp{k}", "{x: 0, y: 0, opacity: 1, scale: %.2f}" % rng.uniform(0.6, 1.6),
                 "{x: %.0f, y: %.0f, opacity: 0, duration: %.2f, ease: 'power2.out', repeat: %d}" % (
                     rng.uniform(-380, 380), rng.uniform(-700, -250), rng.uniform(0.9, 1.5),
                     max(0, int(t.dur / 1.2) - 1)), 0.3 + rng.uniform(0, 0.6))


def toma_pregunta(t: Toma):
    p = t.p
    lineas = p["lineas"]
    tam = p.get("tam") or ajustar(lineas, 140)
    t.html.append(bloque_texto(f"{t.id}b", lineas, 330, tam, p.get("acento"), color="#fff", acento=t.tema[2]))
    top = 330 + tam * 1.02 * len(lineas) + 60
    t.html.append(f'''<div id="{t.id}c" class="lin solo" style="top:{top:.0f}px;font-size:110px;color:{AMARILLO};{txt_borde(110)}">COMENTA 👇</div>
<div id="{t.id}sus" class="sus" style="top:{top + 190:.0f}px"><span class="susTxt">SUSCRÍBETE</span></div>
<div id="{t.id}dedo" class="emoji" style="font-size:150px;top:{top + 240:.0f}px;left:640px;width:200px">👆</div>''')
    for k in range(len(lineas)):
        t.tw(f"#{t.id}bl{k}", "{y: 60, opacity: 0}", "{y: 0, opacity: 1, duration: 0.3, ease: 'power3.out'}", 0.05 + 0.12 * k)
    t.tw(f"#{t.id}c", "{scale: 0.3, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(2)'}", 0.6)
    t.tw(f"#{t.id}sus", "{scale: 0.3, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(2)'}", 1.0)
    t.tw(f"#{t.id}dedo", "{x: 200, y: 300, opacity: 0}", "{x: 0, y: 0, opacity: 1, duration: 0.45, ease: 'power3.out'}", 1.4)
    t.to(f"#{t.id}sus", "{scale: 0.92, duration: 0.1, yoyo: true, repeat: 1}", 1.9)
    t.to(f"#{t.id}sus", "{backgroundColor: '#555', duration: 0.05}", 2.0)
    t.js.append(f'tl.set("#{t.id}sus .susTxt", {{textContent: "SUSCRITO ✓"}}, {t.at(2.0)});')


# --------------------------------------------------------------------------- identidad de cada video
ESTILOS = [
    dict(nombre="clasico", activa="#FFD21F", clave="#E3141B", caja=False, chip="caja", dato="ficha", final="boton",
         trans=["barrido", "zoom", "barrido_izq", "flash"], barra="#FFD21F"),
    dict(nombre="neon", activa="#3DF5FF", clave="#FF3DAE", caja=False, chip="pildora", dato="neon", final="chat",
         trans=["zoom", "flash", "zoom", "barrido"], barra="#3DF5FF"),
    dict(nombre="periodico", activa="#FFFFFF", clave="#FFD21F", caja="#B3261E", chip="cinta", dato="sello", final="sello",
         trans=["barrido_izq", "barrido", "flash", "barrido_izq"], barra="#F4EFE4"),
    dict(nombre="calido", activa="#FFB627", clave="#FF5A36", caja=False, chip="pildora", dato="post", final="si_no",
         trans=["zoom", "barrido", "zoom", "barrido_izq"], barra="#FF8A3D"),
    dict(nombre="frio", activa="#9BE7FF", clave="#FFD21F", caja=False, chip="caja", dato="etiqueta", final="chat",
         trans=["barrido", "barrido", "flash", "zoom"], barra="#9BE7FF"),
    dict(nombre="terror", activa="#B8FF6B", clave="#FF2A2A", caja=False, chip="cinta", dato="sello", final="si_no",
         trans=["flash", "zoom", "flash", "barrido_izq"], barra="#B8FF6B"),
    dict(nombre="pop", activa="#FFFFFF", clave="#FFE600", caja="#FF3D7F", chip="pildora", dato="etiqueta", final="sello",
         trans=["zoom", "barrido_izq", "zoom", "barrido"], barra="#FF3D7F"),
    dict(nombre="retro", activa="#FFD21F", clave="#5CFF7A", caja="#2B59FF", chip="caja", dato="neon", final="boton",
         trans=["barrido", "zoom", "barrido_izq", "zoom"], barra="#5CFF7A"),
]


def estilo_de(n: int, plan: dict) -> dict:
    base = dict(ESTILOS[(n * 5 + 3) % len(ESTILOS)])
    if plan.get("estilo"):
        base = dict(next(e for e in ESTILOS if e["nombre"] == plan["estilo"]))
    base.update(plan.get("estilo_extra", {}))
    return base


def overlay_dato(t: "Toma", dato, lado: str, dt: float = 0.35):
    e = t.estilo["dato"]
    lineas = [dato] if isinstance(dato, str) else list(dato)
    x = 70 if lado == "izq" else None
    pos = f"left:{x}px;" if x is not None else "right:70px;"
    filas = "".join(f'<div class="dl{k}">{esc(l)}</div>' for k, l in enumerate(lineas))
    rot = {"ficha": -3, "post": 4, "sello": -7, "neon": 0, "etiqueta": 0}[e] * (1 if lado == "izq" else -1)
    t.html.append(f'<div id="{t.id}d" class="dato dato-{e}" style="{pos}top:330px;transform:rotate({rot}deg)">{filas}</div>')
    if e == "sello":
        t.tw(f"#{t.id}d", "{scale: 2.6, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.18, ease: 'power4.in'}", dt)
    else:
        t.tw(f"#{t.id}d", "{y: -50, opacity: 0}", "{y: 0, opacity: 1, duration: 0.3, ease: 'back.out(2)'}", dt)


def overlay_texto(t: "Toma", lineas, dt=0.15, top=420, acento=None):
    lineas = [lineas] if isinstance(lineas, str) else lineas
    tam = t.p.get("tam") or ajustar(lineas, 150)
    t.html.append(bloque_texto(f"{t.id}tx", lineas, top, tam, acento, acento=t.estilo["clave"]))
    for k in range(len(lineas)):
        t.tw(f"#{t.id}txl{k}", "{scale: 1.9, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.2, ease: 'power4.out'}",
             dt + 0.12 * k)


CAMARAS = {"push": (0, 0, 0.14), "pull": (0, 0, -0.12), "pan_der": (-150, 0, 0.05), "pan_izq": (150, 0, 0.05),
           "sube": (0, 170, 0.04), "baja": (0, -170, 0.04), "fijo": (0, 0, 0.03), "push_fuerte": (0, 0, 0.28)}


def toma_escena(t: "Toma"):
    import ilustra
    import ilustra_mundo  # noqa: F401
    import ilustra_obj  # noqa: F401
    p = t.p
    capas = p["capas"]
    dx, dy, zm = CAMARAS[p.get("camara", "push")]
    partes, zs = [], []
    for k, c in enumerate(capas):
        u = f"{t.id}k{k}"
        z = c.get("z", round(0.1 + 0.9 * k / max(1, len(capas) - 1), 2))
        partes.append(f'<g id="{t.id}z{k}">{ilustra.DIBUJOS[c["d"]](c, u, t)}</g>')
        zs.append(z)
    t.html.append(f'<svg id="{t.id}sv" class="full" viewBox="0 0 1080 1920" style="top:0;height:1920px">{"".join(partes)}</svg>')
    capas_js = ",".join(f'[document.getElementById("{t.id}z{k}"), {z}]' for k, z in enumerate(zs))
    escala = f"1 + {zm} * z * c.v" if zm >= 0 else f"1 + {-zm} * z * (1 - c.v)"
    t.js.append(f'(() => {{ const c = {{v: 0}}; const L = [{capas_js}]; const pon = () => {{ for (const [el, z] of L) '
                f'el.setAttribute("transform", `translate(${{540 + {dx} * z * c.v}} ${{960 + {dy} * z * c.v}}) '
                f'scale(${{{escala}}}) translate(-540 -960)`); }}; pon(); '
                f'tl.fromTo(c, {{v: 0}}, {{v: 1, duration: {max(0.3, t.dur):.2f}, ease: "sine.inOut", onUpdate: pon}}, {t.at(0)}); }})();')
    if p.get("texto"):
        overlay_texto(t, p["texto"], top=p.get("texto_top", 400), acento=p.get("acento"))
    if p.get("dato"):
        overlay_dato(t, p["dato"], p.get("lado", "izq" if t.i % 2 else "der"), p.get("dato_en", 0.35))


def toma_final(t: "Toma"):
    p = t.p
    var = p.get("final") or t.estilo["final"]
    lineas = p["lineas"]
    tam = p.get("tam") or ajustar(lineas, 130)
    if p.get("capas"):  # escena de fondo para el cierre
        orig = t.p
        t.p = {"capas": p["capas"], "camara": p.get("camara", "fijo")}
        toma_escena(t)
        t.p = orig
        t.html.append('<div class="velo"></div>')
    t.html.append(bloque_texto(f"{t.id}b", lineas, 330, tam, p.get("acento", len(lineas) - 1), acento=t.estilo["activa"]))
    for k in range(len(lineas)):
        t.tw(f"#{t.id}bl{k}", "{y: 60, opacity: 0}", "{y: 0, opacity: 1, duration: 0.3, ease: 'power3.out'}", 0.05 + 0.12 * k)
    top = 330 + tam * 1.02 * len(lineas) + 50
    if var == "boton":
        t.html.append(f'<div id="{t.id}c" class="lin solo" style="top:{top:.0f}px;font-size:104px;color:{t.estilo["activa"]};{txt_borde(104)}">COMENTA 👇</div>'
                      f'<div id="{t.id}sus" class="sus" style="top:{top + 180:.0f}px"><span class="susTxt">SUSCRÍBETE</span></div>'
                      f'<div id="{t.id}dedo" class="emoji" style="font-size:140px;top:{top + 230:.0f}px;left:640px;width:200px">👆</div>')
        t.tw(f"#{t.id}c", "{scale: 0.3, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(2)'}", 0.6)
        t.tw(f"#{t.id}sus", "{scale: 0.3, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(2)'}", 1.0)
        t.tw(f"#{t.id}dedo", "{x: 200, y: 300, opacity: 0}", "{x: 0, y: 0, opacity: 1, duration: 0.45, ease: 'power3.out'}", 1.4)
        t.to(f"#{t.id}sus", "{scale: 0.92, duration: 0.1, yoyo: true, repeat: 1}", 1.9)
        t.to(f"#{t.id}sus", "{backgroundColor: '#555', duration: 0.05}", 2.0)
        t.js.append(f'tl.set("#{t.id}sus .susTxt", {{textContent: "SUSCRITO ✓"}}, {t.at(2.0)});')
    elif var == "chat":
        txt = p.get("comentario", "¡No tenía idea!")
        t.html.append(f'<div id="{t.id}ch" class="chat" style="top:{top:.0f}px"><div class="avatar">🙂</div><div class="burbuja">'
                      f'<div class="quien">@tú · ahora</div><div id="{t.id}ct" class="ctexto"></div></div></div>'
                      f'<div id="{t.id}sus" class="sus" style="top:{top + 260:.0f}px"><span class="susTxt">🔔 SUSCRÍBETE</span></div>')
        t.tw(f"#{t.id}ch", "{y: 80, opacity: 0}", "{y: 0, opacity: 1, duration: 0.35, ease: 'power3.out'}", 0.5)
        for k in range(1, len(txt) + 1):
            t.js.append(f'tl.set("#{t.id}ct", {{textContent: {json.dumps(txt[:k] + ("|" if k < len(txt) else ""))}}}, {t.at(0.8 + k * 0.06)});')
        t.tw(f"#{t.id}sus", "{scale: 0.3, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(2)'}", 1.0 + len(txt) * 0.06)
        t.to(f"#{t.id}sus", "{rotation: 4, duration: 0.08, yoyo: true, repeat: 7}", 1.5 + len(txt) * 0.06)
    elif var == "si_no":
        t.html.append(f'<div id="{t.id}si" class="boton_sn si" style="top:{top:.0f}px;left:150px">SÍ</div>'
                      f'<div id="{t.id}no" class="boton_sn no" style="top:{top:.0f}px;left:600px">NO</div>'
                      f'<div id="{t.id}c" class="lin solo" style="top:{top + 230:.0f}px;font-size:88px;color:#fff;{txt_borde(88)}">COMENTA Y SUSCRÍBETE 👇</div>')
        t.tw(f"#{t.id}si", "{scale: 0, rotation: -20}", "{scale: 1, rotation: 0, duration: 0.35, ease: 'back.out(2.5)'}", 0.5)
        t.tw(f"#{t.id}no", "{scale: 0, rotation: 20}", "{scale: 1, rotation: 0, duration: 0.35, ease: 'back.out(2.5)'}", 0.65)
        vaiv = max(1, int((t.dur - 1.2) / 0.5))
        t.to(f"#{t.id}si", "{scale: 1.1, duration: 0.25, yoyo: true, repeat: %d, ease: 'sine.inOut'}" % vaiv, 1.1)
        t.to(f"#{t.id}no", "{scale: 1.1, duration: 0.25, yoyo: true, repeat: %d, ease: 'sine.inOut'}" % vaiv, 1.35)
        t.tw(f"#{t.id}c", "{y: 50, opacity: 0}", "{y: 0, opacity: 1, duration: 0.3}", 0.9)
    else:  # sello
        t.html.append(f'<div id="{t.id}c" class="lin solo" style="top:{top:.0f}px;font-size:96px;color:{t.estilo["activa"]};{txt_borde(96)}">COMENTA 👇</div>'
                      f'<div id="{t.id}st" class="sello_fin" style="top:{top + 170:.0f}px">SUSCRÍBETE</div>'
                      f'<div id="{t.id}bell" class="emoji" style="font-size:130px;top:{top + 330:.0f}px">🔔</div>')
        t.tw(f"#{t.id}c", "{scale: 0.3, opacity: 0}", "{scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(2)'}", 0.5)
        t.tw(f"#{t.id}st", "{scale: 3, opacity: 0, rotation: -20}", "{scale: 1, opacity: 1, rotation: -8, duration: 0.2, ease: 'power4.in'}", 1.0)
        t.tw(f"#{t.id}bell", "{scale: 0}", "{scale: 1, duration: 0.3, ease: 'back.out(2)'}", 1.3)
        t.to(f"#{t.id}bell", "{rotation: 16, duration: 0.08, yoyo: true, repeat: 9, transformOrigin: '50% 10%'}", 1.6)


def mezclar_v2(voz, inicios, sfx, plan, total):
    """Voz siempre adelante: ambientes suaves por toma, barridos discretos en los cortes y pocos golpes."""
    import pro
    from mezcla_audio import mezcla_final
    n = int(total * SR) + SR
    vz = np.zeros((n, 2), np.float32)
    vz[:min(n, len(voz))] = voz[:n]
    mix = np.zeros((n, 2), np.float32)
    rng = np.random.default_rng(7)
    tomas = plan["tomas"]
    for i, t0 in enumerate(inicios):
        t1 = inicios[i + 1] if i + 1 < len(inicios) else total
        amb = tomas[i].get("amb", plan.get("ambiente"))
        if not amb or amb == "ninguno":
            continue
        d = t1 - t0 + 0.8
        xl, xr = pro.sfx(amb, d, rng), pro.sfx(amb, d, rng)
        s = int(max(0, t0 - 0.3) * SR)
        seg = mix[s:s + len(xl)]
        g = float(tomas[i].get("amb_vol", plan.get("amb_vol", 1.6)))
        seg[:, 0] += xl[:len(seg)] * g
        seg[:, 1] += xr[:len(seg)] * g
    for c in inicios[1:]:
        w = pro.sfx("whoosh", 0.45, rng) * 0.35
        s = int(max(0, c - 0.22) * SR)
        mix[s:s + len(w)] += w[:len(mix[s:s + len(w)])][:, None]
    for t0, tipo, d in sfx:
        x = pro.sfx(tipo, d, rng) * 0.7
        s = int(max(0, t0) * SR)
        mix[s:s + len(x)] += x[:len(mix[s:s + len(x)])][:, None]
    mix = pro.reverb(mix, wet=0.14)
    return mezcla_final(vz, mix, nombre=str(plan.get("nombre", "")))



TOMAS = {"titulo": toma_titulo, "fecha": toma_fecha, "contador": toma_contador, "sismo": toma_sismo,
         "mapa": toma_mapa, "icono": toma_icono, "pregunta": toma_final, "final": toma_final, "escena": toma_escena}


# --------------------------------------------------------------------------- composición
def anclar(plan_tomas, palabras, tiempos):
    normas = [norm(w) for w in palabras]
    inicio, res = 0, []
    for tm in plan_tomas:
        buscar = [norm(w) for w in tm["en"].split()]
        buscar = [b for b in buscar if b]
        idx = None
        for i in range(inicio, len(normas) - len(buscar) + 1):
            if normas[i:i + len(buscar)] == buscar:
                idx = i
                break
        if idx is None:
            sys.exit(f"No encuentro «{tm['en']}» en el guion (después de la palabra {inicio}).")
        res.append(idx)
        inicio = idx + 1
    return [max(0.0, tiempos[i][0] - 0.12) for i in res], res


def subtitulos(palabras, tiempos, claves, total, estilo=None):
    estilo = estilo or ESTILOS[0]
    grupos, g = [], []
    for k, w in enumerate(palabras):
        g.append(k)
        if len(g) == 3 or w[-1] in ",.?!…:;" or (k + 1 < len(palabras) and tiempos[k + 1][0] - tiempos[k][1] > 0.35):
            grupos.append(g)
            g = []
    if g:
        grupos.append(g)
    html, js = [], []
    claves_n = {norm(c) for c in claves}
    for i, g in enumerate(grupos):
        ini = tiempos[g[0]][0]
        fin = tiempos[grupos[i + 1][0]][0] if i + 1 < len(grupos) else total
        fin = min(fin, tiempos[g[-1]][1] + 0.9)
        spans = []
        for k in g:
            w = palabras[k]
            limpio = re.sub(r"^[¿¡«\"(]+|[,.?!…:;»\")]+$", "", w).upper()
            es_clave = norm(w) in claves_n
            spans.append(f'<span id="w{k}" class="w">{esc(limpio)}</span>')
            col = estilo["clave"] if es_clave else estilo["activa"]
            if estilo["caja"] and not es_clave:
                fin_w = max(tiempos[k][1], tiempos[k][0] + 0.12)
                js.append(f'tl.set("#w{k}", {{backgroundColor: "{estilo["caja"]}"}}, {tiempos[k][0]:.3f});')
                js.append(f'tl.set("#w{k}", {{backgroundColor: "rgba(0,0,0,0)"}}, {fin_w:.3f});')
            else:
                js.append(f'tl.to("#w{k}", {{color: "{col}", scale: 1.06, duration: 0.07, ease: "power2.out"}}, {tiempos[k][0]:.3f});')
                if not es_clave:
                    js.append(f'tl.to("#w{k}", {{color: "#ffffff", scale: 1, duration: 0.1}}, {tiempos[k][1]:.3f});')
        html.append(f'<div id="cap{i}" class="clip cap" data-start="{ini:.3f}" data-duration="{max(0.2, fin - ini):.3f}" '
                    f'data-track-index="20"><div id="ci{i}" class="capin">{"".join(spans)}</div></div>')
        js.append(f'tl.fromTo("#ci{i}", {{y: 30, scale: 0.88, opacity: 0}}, {{y: 0, scale: 1, opacity: 1, duration: 0.14, ease: "back.out(2)"}}, {ini:.3f});')
    return "\n".join(html), js


def fondo(tema, total):
    rng = random.Random(11)
    polvo = "".join(f'<i style="left:{rng.uniform(0, 1080):.0f}px;top:{rng.uniform(0, 1920):.0f}px;'
                    f'width:{(s := rng.uniform(3, 9)):.0f}px;height:{s:.0f}px;opacity:{rng.uniform(.15, .5):.2f}"></i>'
                    for _ in range(70))
    html = f'''<div id="fondo" class="clip" data-start="0" data-duration="{total}" data-track-index="0">
  <div id="bgA"></div><div id="blob1" class="blob"></div><div id="blob2" class="blob"></div>
  <div id="polvo">{polvo}</div>
</div>'''
    js = [f'tl.fromTo("#blob1", {{x: -200, y: 0}}, {{x: 260, y: 300, duration: {total}, ease: "none"}}, 0);',
          f'tl.fromTo("#blob2", {{x: 200, y: 0}}, {{x: -240, y: -360, duration: {total}, ease: "none"}}, 0);',
          f'tl.fromTo("#polvo", {{y: 0}}, {{y: -260, duration: {total}, ease: "none"}}, 0);']
    return html, js


def css(tema, estilo=None):
    estilo = estilo or ESTILOS[0]
    f1, f2, acento, part = tema
    return f'''@font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.woff") format("woff"); }}
@font-face {{ font-family: "Emoji"; src: url("assets/fonts/NotoColorEmoji.ttf") format("truetype"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:{f2}; }}
#root {{ width:1080px; height:1920px; position:relative; overflow:hidden; font-family:"Anton", "Emoji", sans-serif; }}
#bgA {{ position:absolute; inset:0; background:radial-gradient(110% 70% at 50% 35%, {f1} 0%, {f2} 75%); }}
.blob {{ position:absolute; width:900px; height:900px; border-radius:50%; filter:blur(120px); opacity:.35; }}
#blob1 {{ left:-200px; top:200px; background:{acento}; opacity:.18; }}
#blob2 {{ left:400px; top:1000px; background:{part}; opacity:.12; }}
#polvo {{ position:absolute; inset:0 0 -300px 0; }}
#polvo i {{ position:absolute; border-radius:50%; background:{part}; }}
#cam {{ position:absolute; inset:0; }}
.toma {{ position:absolute; inset:0; }}
.full {{ position:absolute; left:0; width:1080px; }}
.bloque {{ position:absolute; left:40px; right:40px; text-align:center; }}
.lin {{ display:block; line-height:1.02; font-family:"Anton"; text-shadow:0 12px 0 rgba(0,0,0,.45); }}
.solo {{ position:absolute; left:30px; right:30px; text-align:center; }}
.emoji {{ position:absolute; left:0; width:1080px; text-align:center; line-height:1; font-family:"Emoji"; }}
.chipx {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; white-space:nowrap; background:{ROJO}; color:#fff;
  font-size:52px; padding:10px 30px; border-radius:16px; border:5px solid #000; font-family:"Anton","Emoji"; }}
.cal {{ position:absolute; left:290px; width:500px; height:500px; background:#f4efe4; border-radius:40px; overflow:hidden;
  border:8px solid #000; box-shadow:0 30px 0 rgba(0,0,0,.4); }}
.calTop {{ height:130px; color:#fff; font-size:92px; text-align:center; line-height:130px; border-bottom:8px solid #000; }}
.calDia {{ font-size:300px; line-height:350px; text-align:center; color:#111; }}
.pinlab {{ position:absolute; background:#fff; color:#000; font-size:56px; padding:6px 22px; border-radius:14px;
  border:5px solid #000; white-space:nowrap; }}
.part {{ position:absolute; width:26px; height:26px; border-radius:50%; }}
.sus {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; background:{ROJO}; color:#fff; font-size:80px;
  padding:16px 56px; border-radius:60px; border:6px solid #000; white-space:nowrap; }}
#chip {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; top:296px; background:{ROJO}; color:#fff; font-size:40px;
  letter-spacing:2px; padding:8px 24px; border-radius:12px; border:4px solid #000; white-space:nowrap; }}
#barra {{ position:absolute; left:0; top:0; height:14px; width:1080px; background:{estilo["barra"]}; transform-origin:0 50%; }}
.chip-pildora {{ border-radius:40px !important; }}
.chip-cinta {{ border-radius:0 !important; background:{AMARILLO} !important; color:#000 !important; }}
.dato {{ position:absolute; font-family:"Anton","Emoji"; text-align:center; padding:14px 30px; white-space:nowrap; }}
.dato .dl0 {{ font-size:44px; }} .dato .dl1 {{ font-size:84px; line-height:1; }}
.dato-ficha {{ background:#f6f1e6; color:#1b1b1b; border:6px solid #111; border-top:22px solid {ROJO}; border-radius:10px; box-shadow:0 18px 0 rgba(0,0,0,.35); }}
.dato-post {{ background:#ffe66b; color:#222; border-radius:6px; box-shadow:0 16px 24px rgba(0,0,0,.4); }}
.dato-sello {{ color:{ROJO}; border:10px double {ROJO}; border-radius:14px; background:rgba(255,255,255,.05); text-shadow:none; }}
.dato-neon {{ color:#fff; border:5px solid {estilo["activa"]}; border-radius:18px; background:rgba(5,8,20,.78);
  box-shadow:0 0 30px {estilo["activa"]}, inset 0 0 22px {estilo["activa"]}; }}
.dato-etiqueta {{ background:#111; color:{estilo["activa"]}; border-radius:60px; border:5px solid #fff; }}
.velo {{ position:absolute; inset:0; background:rgba(0,0,0,.45); }}
.chat {{ position:absolute; left:90px; right:90px; display:flex; gap:22px; align-items:flex-start; }}
.chat .avatar {{ width:110px; height:110px; border-radius:50%; background:#2f3b55; font-size:76px; line-height:110px;
  text-align:center; font-family:"Emoji"; flex:none; border:5px solid #fff; }}
.chat .burbuja {{ background:#fff; color:#111; border-radius:28px; padding:18px 30px; min-height:150px; flex:1; }}
.chat .quien {{ font-size:34px; color:#666; }} .chat .ctexto {{ font-size:64px; line-height:1.05; }}
.boton_sn {{ position:absolute; width:330px; height:190px; border-radius:40px; font-size:130px; line-height:190px;
  text-align:center; color:#fff; border:8px solid #000; box-shadow:0 18px 0 rgba(0,0,0,.45); }}
.boton_sn.si {{ background:#22b35e; }} .boton_sn.no {{ background:{ROJO}; }}
.sello_fin {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; font-size:120px; color:{ROJO};
  border:14px double {ROJO}; border-radius:20px; padding:0 40px; background:rgba(255,255,255,.92); }}
#handle {{ position:absolute; left:0; right:0; top:1365px; text-align:center; color:rgba(255,255,255,.6); font-size:34px;
  letter-spacing:3px; }}
#flash {{ position:absolute; inset:0; background:#fff; opacity:0; }}
#vineta {{ position:absolute; inset:0; background:radial-gradient(95% 65% at 50% 45%, transparent 55%, rgba(0,0,0,.8)); }}
.cap {{ position:absolute; left:110px; right:160px; top:1150px; display:flex; justify-content:center; }}
.capin {{ text-align:center; font-size:92px; line-height:1.05; color:#fff; {txt_borde(92, 9)} text-shadow:0 8px 0 rgba(0,0,0,.55); }}
.w {{ display:inline-block; margin:0 .2em; padding:0 .1em; border-radius:12px; background-color:rgba(0,0,0,0); }}'''


def componer(n: int, plan: dict, palabras, tiempos, parrafo_de, total, dir_: Path, sfx_eventos: list):
    tema = TEMAS[plan.get("tema", "historia")]
    estilo = estilo_de(n, plan)
    inicios, idx = anclar(plan["tomas"], palabras, tiempos)
    inicios[0] = 0.0
    html_tomas, js = [], []
    entradas = estilo["trans"]
    for i, (tm, t0) in enumerate(zip(plan["tomas"], inicios)):
        t1 = inicios[i + 1] if i + 1 < len(inicios) else total
        emo = parrafo_de[idx[i]]
        toma = Toma(i, t0, t1 - t0, tm, tema, emo)
        toma.estilo = estilo
        TOMAS[tm["tipo"]](toma)
        html_tomas.append(f'<div id="{toma.id}" class="clip toma" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" '
                          f'data-track-index="{10 + i % 2}"><div id="{toma.id}in" class="toma">{"".join(toma.html)}</div></div>')
        js += toma.js
        if i > 0:  # transición de entrada
            e = tm.get("entrada", entradas[i % len(entradas)])
            sel = f"#{toma.id}in"
            if e == "barrido":
                js.append(f'tl.fromTo("{sel}", {{x: 1080, skewX: -12}}, {{x: 0, skewX: 0, duration: 0.24, ease: "power3.out"}}, {t0:.3f});')
            elif e == "barrido_izq":
                js.append(f'tl.fromTo("{sel}", {{x: -1080, skewX: 12}}, {{x: 0, skewX: 0, duration: 0.24, ease: "power3.out"}}, {t0:.3f});')
            elif e == "zoom":
                js.append(f'tl.fromTo("{sel}", {{scale: 0.7, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.25, ease: "power3.out"}}, {t0:.3f});')
            elif e == "flash":
                js.append(f'tl.set("#flash", {{opacity: 0.85}}, {t0:.3f}); tl.to("#flash", {{opacity: 0, duration: 0.3, ease: "power2.out"}}, {t0 + 0.01:.3f});')
        if tm.get("sacudir") or emo == "tenso" and tm.get("sacudir", True) and tm["tipo"] in ("titulo", "sismo"):
            veces = 9 if tm["tipo"] != "sismo" else max(9, int((t1 - t0) / 0.05))
            js.append(f'tl.fromTo("#cam", {{x: 0, y: 0}}, {{x: 14, y: -10, duration: 0.05, yoyo: true, repeat: {veces}, ease: "none"}}, {t0 + 0.08:.3f});')
            js.append(f'tl.set("#cam", {{x: 0, y: 0}}, {t0 + 0.08 + 0.05 * (veces + 1) + 0.01:.3f});')
        if tm.get("sfx"):
            sfx_eventos.append((t0 + float(tm.get("sfx_en", 0.1)), tm["sfx"], float(tm.get("sfx_dur", 1.6))))
    fin_t = inicios[-1] if plan["tomas"][-1]["tipo"] in ("final", "pregunta") else total
    n_fin = next((k for k, (a, b) in enumerate(tiempos) if a >= fin_t - 0.05), len(palabras))
    caps, js_caps = subtitulos(palabras[:n_fin], tiempos[:n_fin], plan.get("claves", []), min(total, fin_t), estilo)
    f_html, f_js = fondo(tema, total)
    etiqueta = plan.get("etiqueta", "HISTORIA REAL")
    doc = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
{css(tema, estilo)}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
{f_html}
<div id="camHost" class="clip" data-start="0" data-duration="{total}" data-track-index="1"><div id="cam">
{chr(10).join(html_tomas)}
</div></div>
<div id="fx" class="clip" data-start="0" data-duration="{total}" data-track-index="2"><div id="flash"></div><div id="vineta"></div></div>
<div id="hud" class="clip" data-start="0" data-duration="{total}" data-track-index="3"><div id="barra"></div><div id="chip" class="chip-{estilo["chip"]}">{esc(etiqueta)}</div><div id="handle">@1MRELATO</div></div>
<div id="capsHost" data-track-kind="captions">
{caps}
</div>
<audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{total}" data-track-index="30"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(f_js)}
tl.fromTo("#barra", {{scaleX: 0}}, {{scaleX: 1, duration: {total}, ease: "none"}}, 0);
tl.fromTo("#chip", {{y: -60, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.3, ease: "back.out(2)"}}, 0);
tl.to("#chip", {{y: -40, opacity: 0, duration: 0.3, ease: "power2.in"}}, {min(3.2, inicios[1] - 0.3) if len(inicios) > 1 else 3.2:.3f});
{chr(10).join(js)}
{chr(10).join(js_caps)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
'''
    (dir_ / "index.html").write_text(doc, encoding="utf-8")
    return inicios


def escribir_wav(ruta: Path, x: np.ndarray):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def preparar_proyecto(dir_: Path):
    (dir_ / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy(RAIZ / "fuentes" / "Anton-Regular.woff", dir_ / "assets" / "fonts" / "Anton-Regular.woff")
    emoji = Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
    if emoji.exists() and not (dir_ / "assets" / "fonts" / "NotoColorEmoji.ttf").exists():
        shutil.copy(emoji, dir_ / "assets" / "fonts" / "NotoColorEmoji.ttf")
    (dir_ / "hyperframes.json").write_text(json.dumps({"name": dir_.name}, indent=2), encoding="utf-8")
    (dir_ / "package.json").write_text(json.dumps({"name": dir_.name, "private": True, "type": "module", "scripts": {
        "check": f"npx --yes {HF} check", "render": f"npx --yes {HF} render"}}, indent=2), encoding="utf-8")


def nombre_video(n: int, nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre.lower()).encode("ascii", "ignore").decode()
    return f"relato_{n:03d}_" + re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--sin-render", action="store_true")
    a = ap.parse_args()
    n = a.n
    nombre, parrafos = cargar_guion(n)
    plan = json.loads((PLANES / f"relato_{n:03d}.json").read_text(encoding="utf-8"))
    audio = AUDIOS / f"relato_{n:03d}.mp3"
    palabras, parrafo_de, fin_parrafo = [], [], []
    for emo, texto in parrafos:
        for w in texto.split():
            palabras.append(w)
            parrafo_de.append(emo)
        fin_parrafo.append(len(palabras) - 1)
    dir_ = PROYECTOS / f"relato_{n:03d}"
    dir_.mkdir(parents=True, exist_ok=True)
    preparar_proyecto(dir_)
    D = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              str(audio)], capture_output=True, text=True).stdout)
    tiempos = alinear(palabras, oidas(audio), D)
    compacta, mover, D = compactar_silencios(audio, dir_)
    tiempos = [(mover(x), mover(y)) for x, y in tiempos]
    tempo, lead, pausa, cola = plan_tiempo(D, len(parrafos))
    voz = procesar_voz(compacta, tempo, dir_)
    tiempos = [(x / tempo, y / tempo) for x, y in tiempos]
    voz, tiempos, total, cortes_parrafo = estirar(voz, tiempos, fin_parrafo, lead, pausa, cola)
    sfx = []
    inicios = componer(n, plan, palabras, tiempos, parrafo_de, total, dir_, sfx)
    mezcla = mezclar_v2(voz, inicios, sfx, plan, total)
    escribir_wav(dir_ / "assets" / "mezcla_bruta.wav", mezcla[:int(total * SR)])
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(dir_ / "assets" / "mezcla_bruta.wav"), "-af",
                    "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(SR), str(dir_ / "assets" / "mezcla.wav")], check=True)
    print(f"relato {n:03d}: {len(plan['tomas'])} tomas · voz {D:.1f} s × {1 / tempo:.2f} · pausas {pausa:.2f} s · "
          f"cola {cola:.1f} s · video {total:.2f} s")
    if a.sin_render:
        return
    SALIDA.mkdir(exist_ok=True)
    destino = SALIDA / f"{nombre_video(n, nombre)}.mp4"
    subprocess.run(["npx", "--yes", HF, "render", "-q", "delivery", "-o", str(destino)], cwd=dir_, check=True)
    print("→", destino)


if __name__ == "__main__":
    main()
