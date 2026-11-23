#!/usr/bin/env python3
"""
Generador de YouTube Shorts animados (1080x1920, 9:16) a partir de un guion JSON.

Hace todo automáticamente:
  1. Narración con voz (edge-tts, gratis y natural; si falla usa gTTS).
  2. Animación: fondo degradado en movimiento, partículas, emoji "personaje"
     que rebota, imágenes con efecto Ken Burns (zoom lento) si las pones.
  3. Subtítulos estilo viral palabra por palabra, con la palabra activa resaltada.
  4. Gancho (título) arriba los primeros segundos y barra de progreso.
  5. Música de fondo opcional con volumen bajo.

Uso:
    python generar_short.py historias/ejemplo_misterio.json
    python generar_short.py historias/*.json          # varios a la vez

Requisitos: Python 3.9+, ffmpeg en el PATH, y:
    pip install -r requirements.txt
"""
from __future__ import annotations

import asyncio
import colorsys
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
RAIZ = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- #
# Fuentes (busca en Linux, macOS y Windows)
# --------------------------------------------------------------------------- #
FUENTES_TEXTO = [
    str(RAIZ / "fuentes" / "texto.ttf"),
    str(RAIZ / "fuentes" / "texto.otf"),
    "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/ariblk.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
FUENTES_EMOJI = [
    str(RAIZ / "fuentes" / "emoji.ttf"),
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "C:/Windows/Fonts/seguiemj.ttf",
]


def _primera_existente(rutas):
    return next((r for r in rutas if os.path.exists(r)), None)


def fuente_texto(tam: int) -> ImageFont.FreeTypeFont:
    ruta = _primera_existente(FUENTES_TEXTO)
    return ImageFont.truetype(ruta, tam) if ruta else ImageFont.load_default(tam)


_cache_emoji: dict[str, Image.Image | None] = {}


def render_emoji(emoji: str) -> Image.Image | None:
    """Devuelve el emoji como imagen RGBA (~400px) o None si no hay fuente."""
    if emoji in _cache_emoji:
        return _cache_emoji[emoji]
    ruta = _primera_existente(FUENTES_EMOJI)
    img = None
    if ruta:
        # Noto Color Emoji solo funciona a tamaño 109 (bitmap); otras escalan libre.
        tam = 109 if "Noto" in ruta else 160
        try:
            f = ImageFont.truetype(ruta, tam)
            lienzo = Image.new("RGBA", (tam * 2, tam * 2), (0, 0, 0, 0))
            ImageDraw.Draw(lienzo).text((tam // 4, tam // 4), emoji, font=f, embedded_color=True)
            caja = lienzo.getbbox()
            if caja:
                rec = lienzo.crop(caja)
                esc = min(400 / rec.width, 460 / rec.height)  # limita emojis altos (📱, 🚪)
                img = rec.resize((int(rec.width * esc), int(rec.height * esc)), Image.LANCZOS)
        except OSError:
            img = None
    _cache_emoji[emoji] = img
    return img


# --------------------------------------------------------------------------- #
# Voz (TTS)
# --------------------------------------------------------------------------- #
@dataclass
class Palabra:
    texto: str
    inicio: float  # segundos relativos a la escena
    fin: float


async def _edge_tts(texto: str, voz: str, velocidad: str, salida: Path) -> list[Palabra]:
    import edge_tts

    com = edge_tts.Communicate(texto, voz, rate=velocidad, boundary="WordBoundary")
    palabras: list[Palabra] = []
    with open(salida, "wb") as fh:
        async for trozo in com.stream():
            if trozo["type"] == "audio":
                fh.write(trozo["data"])
            elif trozo["type"] == "WordBoundary":
                ini = trozo["offset"] / 1e7
                palabras.append(Palabra(trozo["text"], ini, ini + trozo["duration"] / 1e7))
    return palabras


def duracion_audio(ruta: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def tiempos_estimados(texto: str, duracion: float) -> list[Palabra]:
    """Reparte el tiempo entre palabras según su longitud (cuando el TTS no da tiempos)."""
    trozos = texto.split()
    pesos = [len(p) + 2 for p in trozos]
    total = sum(pesos)
    t, res = 0.05, []
    util = max(duracion - 0.15, 0.1)
    for p, w in zip(trozos, pesos):
        d = util * w / total
        res.append(Palabra(p, t, t + d))
        t += d
    return res


def narrar(texto: str, cfg: dict, salida: Path) -> tuple[float, list[Palabra]]:
    voz = cfg.get("voz", "es-MX-JorgeNeural")
    velocidad = cfg.get("velocidad", "+10%")
    palabras: list[Palabra] = []
    try:
        palabras = asyncio.run(_edge_tts(texto, voz, velocidad, salida))
        if not salida.exists() or salida.stat().st_size == 0:
            raise RuntimeError("audio vacío")
    except Exception as e:  # noqa: BLE001
        print(f"   · edge-tts no disponible ({type(e).__name__}); usando gTTS")
        from gtts import gTTS

        crudo = salida.with_suffix(".raw.mp3")
        gTTS(texto, lang="es", tld=cfg.get("acento_gtts", "com.mx")).save(str(crudo))
        # gTTS es lento: lo aceleramos un poco sin cambiar el tono
        factor = cfg.get("acelerar_gtts", 1.2)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(crudo),
                        "-filter:a", f"atempo={factor}", str(salida)], check=True)
        palabras = []
    dur = duracion_audio(salida)
    if not palabras:
        palabras = tiempos_estimados(texto, dur)
    return dur, palabras


# --------------------------------------------------------------------------- #
# Animación
# --------------------------------------------------------------------------- #
def hex_a_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def ease_out_back(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


@dataclass
class Escena:
    texto: str
    emoji: str = ""
    imagen: str = ""
    colores: list = field(default_factory=lambda: ["#1a1a2e", "#16213e"])
    audio: Path | None = None
    duracion: float = 0.0
    palabras: list = field(default_factory=list)
    inicio: float = 0.0


class Fondo:
    """Degradado animado + partículas brillantes. Se precalcula a baja resolución."""

    def __init__(self, semilla: int = 7):
        rnd = random.Random(semilla)
        self.particulas = [
            (rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(4, 16), rnd.uniform(20, 90), rnd.uniform(0, 6.28))
            for _ in range(45)
        ]

    def frame(self, t: float, c1, c2) -> Image.Image:
        # degradado vertical pequeño y escalado (rápido)
        g = Image.new("RGB", (1, 64))
        osc = 0.5 + 0.5 * math.sin(t * 0.6)
        for y in range(64):
            k = min(max(y / 63 + (osc - 0.5) * 0.35, 0), 1)
            g.putpixel((0, y), tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3)))
        img = g.resize((W, H), Image.BILINEAR)

        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        for x0, y0, r, vel, fase in self.particulas:
            y = (y0 - vel * t) % (H + 40) - 20
            x = x0 + 30 * math.sin(t * 0.8 + fase)
            a = int(60 + 50 * math.sin(t * 2 + fase))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, max(a, 0)))
        capa = capa.filter(ImageFilter.GaussianBlur(3))
        img.paste(capa, (0, 0), capa)
        return img


_cache_img: dict[str, Image.Image] = {}


def ken_burns(ruta: str, progreso: float, idx: int) -> Image.Image:
    if ruta not in _cache_img:
        im = Image.open(ruta).convert("RGB")
        # cubrir 1080x1350 (zona central) con margen para el zoom
        objetivo = (W, 1350)
        esc = max(objetivo[0] / im.width, objetivo[1] / im.height) * 1.18
        _cache_img[ruta] = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    im = _cache_img[ruta]
    zoom = 1.0 + 0.15 * progreso if idx % 2 == 0 else 1.15 - 0.15 * progreso
    cw, ch = int(W / zoom * 1.0), int(1350 / zoom)
    cw, ch = min(cw, im.width), min(ch, im.height)
    dx = (im.width - cw) * (0.3 + 0.4 * progreso if idx % 3 else 0.5)
    dy = (im.height - ch) * 0.5
    return im.crop((int(dx), int(dy), int(dx) + cw, int(dy) + ch)).resize((W, 1350), Image.BILINEAR)


def agrupar_palabras(palabras: list[Palabra], max_palabras=3, max_chars=16) -> list[list[Palabra]]:
    grupos, actual = [], []
    for p in palabras:
        largo = sum(len(x.texto) + 1 for x in actual) + len(p.texto)
        if actual and (len(actual) >= max_palabras or largo > max_chars):
            grupos.append(actual)
            actual = []
        actual.append(p)
        if p.texto.endswith((".", "!", "?", ",", "…")):
            grupos.append(actual)
            actual = []
    if actual:
        grupos.append(actual)
    return grupos


def texto_con_borde(d: ImageDraw.ImageDraw, xy, txt, fuente, relleno, borde=10):
    d.text(xy, txt, font=fuente, fill=relleno, stroke_width=borde, stroke_fill=(0, 0, 0))


def dibujar_subtitulos(img: Image.Image, escena: Escena, t_local: float, color_activo):
    grupos = escena._grupos  # type: ignore[attr-defined]
    grupo = None
    for i, g in enumerate(grupos):
        fin = grupos[i + 1][0].inicio if i + 1 < len(grupos) else escena.duracion + 1
        if g[0].inicio - 0.05 <= t_local < fin:
            grupo = g
            break
    if grupo is None:
        return
    pop = ease_out_back((t_local - grupo[0].inicio) / 0.18)
    tam = int(110 * (0.75 + 0.25 * pop))
    f = fuente_texto(tam)
    d = ImageDraw.Draw(img)
    palabras = [p.texto.upper() for p in grupo]
    espacio = tam * 0.28
    anchos = [d.textlength(p, font=f) for p in palabras]
    # si no cabe, partir en 2 líneas
    lineas = [list(range(len(palabras)))]
    if sum(anchos) + espacio * (len(palabras) - 1) > W - 120 and len(palabras) > 1:
        m = len(palabras) // 2 or 1
        lineas = [list(range(m)), list(range(m, len(palabras)))]
    y = 1380 - (len(lineas) - 1) * tam * 0.6
    for linea in lineas:
        total = sum(anchos[i] for i in linea) + espacio * (len(linea) - 1)
        x = (W - total) / 2
        for i in linea:
            activa = grupo[i].inicio <= t_local < grupo[i].fin + 0.05
            color = color_activo if activa else (255, 255, 255)
            texto_con_borde(d, (x, y), palabras[i], f, color, borde=max(6, tam // 11))
            x += anchos[i] + espacio
        y += tam * 1.15


def dibujar_gancho(img: Image.Image, titulo: str, t: float):
    if t > 3.2 or not titulo:
        return
    alfa = 1.0 if t < 2.7 else max(0.0, 1 - (t - 2.7) / 0.5)
    entrada = ease_out_back(t / 0.35)
    f = fuente_texto(68)
    d0 = ImageDraw.Draw(img)
    # envolver
    palabras, lineas, actual = titulo.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d0.textlength(prueba, font=f) > W - 160:
            lineas.append(actual)
            actual = p
        else:
            actual = prueba
    lineas.append(actual)
    alto = len(lineas) * 82 + 50
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    y0 = int(170 - (1 - entrada) * 300)
    d.rounded_rectangle((50, y0, W - 50, y0 + alto), radius=36, fill=(255, 30, 60, int(235 * alfa)))
    y = y0 + 25
    for ln in lineas:
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, y), ln, font=f, fill=(255, 255, 255, int(255 * alfa)))
        y += 82
    img.paste(capa, (0, 0), capa)


def dibujar_emoji(img: Image.Image, emoji: str, t_local: float, tiene_imagen: bool):
    em = render_emoji(emoji) if emoji else None
    if em is None:
        return
    entrada = ease_out_back(t_local / 0.45)
    escala = max(0.05, entrada) * (1 + 0.04 * math.sin(t_local * 5))
    if tiene_imagen:
        escala *= 0.45
    w = int(em.width * escala)
    h = int(em.height * escala)
    if w < 4 or h < 4:
        return
    e = em.resize((w, h), Image.BILINEAR).rotate(6 * math.sin(t_local * 2.2), expand=True, resample=Image.BICUBIC)
    cy = 330 if tiene_imagen else 820
    cx = W - 200 if tiene_imagen else W // 2
    y = int(cy + 25 * math.sin(t_local * 3) - e.height / 2)
    # sombra
    sombra = Image.new("RGBA", e.size, (0, 0, 0, 0))
    sombra.paste((0, 0, 0, 110), (0, 0), e)
    sombra = sombra.filter(ImageFilter.GaussianBlur(14))
    img.paste(sombra, (cx - e.width // 2 + 14, y + 22), sombra)
    img.paste(e, (cx - e.width // 2, y), e)


def dibujar_progreso(img: Image.Image, t: float, total: float, color):
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 14, W, H), fill=(0, 0, 0))
    d.rectangle((0, H - 14, int(W * t / total), H), fill=color)


def componer_frame(t: float, escenas: list[Escena], fondo: Fondo, cfg: dict, total: float) -> Image.Image:
    idx = 0
    for i, e in enumerate(escenas):
        if t >= e.inicio:
            idx = i
    esc = escenas[idx]
    t_local = t - esc.inicio
    c1, c2 = (hex_a_rgb(c) for c in esc.colores[:2])

    # transición de colores suave al cambiar de escena
    if idx > 0 and t_local < 0.4:
        prev = escenas[idx - 1]
        p1, p2 = (hex_a_rgb(c) for c in prev.colores[:2])
        k = t_local / 0.4
        c1 = tuple(int(p1[i] * (1 - k) + c1[i] * k) for i in range(3))
        c2 = tuple(int(p2[i] * (1 - k) + c2[i] * k) for i in range(3))

    img = fondo.frame(t, c1, c2)

    if esc.imagen:
        prog = t_local / max(esc.duracion, 0.1)
        foto = ken_burns(esc.imagen, prog, idx)
        mascara = Image.new("L", foto.size, 0)
        ImageDraw.Draw(mascara).rounded_rectangle((40, 0, W - 40, 1350), radius=50, fill=255)
        # fundido de entrada
        if t_local < 0.3:
            mascara = mascara.point(lambda v: int(v * t_local / 0.3))
        img.paste(foto, (0, 230), mascara)

    dibujar_emoji(img, esc.emoji, t_local, bool(esc.imagen))

    # viñeta oscura abajo para legibilidad de subtítulos
    color_activo = hex_a_rgb(cfg.get("color_resaltado", "#FFE400"))
    dibujar_subtitulos(img, esc, t_local, color_activo)
    dibujar_gancho(img, cfg.get("gancho", ""), t)
    dibujar_progreso(img, t, total, color_activo)

    # flash blanco corto en el corte de escena
    if idx > 0 and t_local < 0.08:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 0.35 * (1 - t_local / 0.08))
    return img


# --------------------------------------------------------------------------- #
# Montaje
# --------------------------------------------------------------------------- #
def generar(ruta_json: Path, carpeta_salida: Path):
    cfg = json.loads(ruta_json.read_text(encoding="utf-8"))
    nombre = ruta_json.stem
    print(f"\n▶ {nombre}: {cfg.get('titulo', '')}")
    paletas = [["#1a1a2e", "#3a0ca3"], ["#2b2d42", "#8d0801"], ["#03045e", "#0077b6"],
               ["#240046", "#ff006e"], ["#0b090a", "#3c096c"], ["#004b23", "#007200"]]

    tmp = Path(tempfile.mkdtemp(prefix="short_"))
    try:
        escenas: list[Escena] = []
        t = 0.0
        pausa = float(cfg.get("pausa_entre_escenas", 0.25))
        for i, s in enumerate(cfg["escenas"]):
            imagen = s.get("imagen", "")
            if imagen and not os.path.isabs(imagen):
                imagen = str((ruta_json.parent / imagen).resolve())
            e = Escena(texto=s["texto"], emoji=s.get("emoji", ""), imagen=imagen,
                       colores=s.get("colores", paletas[i % len(paletas)]))
            e.audio = tmp / f"esc{i:02d}.mp3"
            print(f"   · voz escena {i + 1}/{len(cfg['escenas'])}")
            dur, palabras = narrar(e.texto, cfg, e.audio)
            e.duracion = dur + pausa
            e.palabras = palabras
            e._grupos = agrupar_palabras(palabras)  # type: ignore[attr-defined]
            e.inicio = t
            t += e.duracion
            escenas.append(e)
        total = t
        if total > 60:
            print(f"   ⚠ Dura {total:.1f}s. Los Shorts pueden durar hasta 3 min, pero <60s suele retener mejor.")

        # audio: concatenar narraciones con silencios
        partes = []
        for e in escenas:
            pad = tmp / (e.audio.stem + "_pad.wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(e.audio),
                            "-af", f"apad=whole_dur={e.duracion:.3f}", "-ar", "44100", "-ac", "2", str(pad)],
                           check=True)
            partes.append(pad)
        lista = tmp / "lista.txt"
        lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in partes))
        voz = tmp / "voz.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", str(lista), str(voz)], check=True)

        musica = cfg.get("musica", "")
        if musica and not os.path.isabs(musica):
            musica = str((ruta_json.parent / musica).resolve())
        audio_final = tmp / "audio.m4a"
        if musica and os.path.exists(musica):
            vol = cfg.get("volumen_musica", 0.12)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(voz), "-stream_loop", "-1",
                            "-i", musica, "-filter_complex",
                            f"[1:a]volume={vol}[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
                            "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(audio_final)], check=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(voz),
                            "-c:a", "aac", "-b:a", "192k", str(audio_final)], check=True)

        # video: enviar frames crudos a ffmpeg
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        salida = carpeta_salida / f"{nombre}.mp4"
        n_frames = int(math.ceil(total * FPS))
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(audio_final),
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(salida)],
            stdin=subprocess.PIPE,
        )
        fondo = Fondo()
        for f in range(n_frames):
            frame = componer_frame(f / FPS, escenas, fondo, cfg, total)
            proc.stdin.write(frame.tobytes())
            if f % (FPS * 5) == 0:
                print(f"   · animando {f / FPS:5.1f}s / {total:.1f}s", flush=True)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg falló al codificar el video")

        # miniatura (primer frame tras el gancho) y textos para subir
        componer_frame(min(1.0, total / 2), escenas, fondo, cfg, total).save(carpeta_salida / f"{nombre}_miniatura.jpg",
                                                                              quality=90)
        meta = [f"TÍTULO:\n{cfg.get('titulo', nombre)}\n",
                f"DESCRIPCIÓN:\n{cfg.get('descripcion', '')}\n",
                "HASHTAGS:\n" + " ".join(cfg.get("hashtags", ["#shorts"])) + "\n"]
        (carpeta_salida / f"{nombre}_publicar.txt").write_text("\n".join(meta), encoding="utf-8")
        print(f"   ✔ listo: {salida} ({total:.1f}s)")
        return salida
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if not shutil.which("ffmpeg"):
        sys.exit("Falta ffmpeg. Instálalo: https://ffmpeg.org/download.html")
    for arg in sys.argv[1:]:
        generar(Path(arg), RAIZ / "salida")


if __name__ == "__main__":
    main()
