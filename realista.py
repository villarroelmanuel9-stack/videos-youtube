"""
Modo de dibujo "semi-realista" (un paso más allá de la caricatura):
  * sombreado con degradado suave (luz → sombra) en vez de medialunas duras,
  * contornos finos del color oscuro del objeto (no negro puro),
  * textura sutil tipo pintura,
  * pelaje con trazos (para animales),
  * acabado de cine para cada fotograma: curva de color, brillo en las luces (bloom) y grano suave.
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from dinos import SS, Lienzo, catmull, claro, oscuro

_rng = np.random.default_rng(7)
_RUIDO = Image.fromarray((128 + _rng.normal(0, 40, (1024, 1024))).clip(0, 255).astype(np.uint8), "L") \
    .filter(ImageFilter.GaussianBlur(1.2))


def _ruido(w, h, x0=0, y0=0):
    x0, y0 = x0 % 512, y0 % 512
    if w + x0 <= 1024 and h + y0 <= 1024:
        return _RUIDO.crop((x0, y0, x0 + w, y0 + h))
    return _RUIDO.resize((max(w, 1), max(h, 1)))


class LienzoReal(Lienzo):
    def forma(self, pts, col, sombra=True, brillo=True, borde=True, ancho=5, suave=True, clip=None, luz=(-1, -1),
              intensidad=0.11, textura=0.07):
        if suave:
            pts = catmull(pts, 5)
        q = self.P(pts)
        xs, ys = [p[0] for p in q], [p[1] for p in q]
        tam = max(max(xs) - min(xs), max(ys) - min(ys), 1)
        off = max(6, int(tam * intensidad * 1.25))
        pad = off + 30
        x0, y0 = max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad)
        x1, y1 = min(self.img.width, int(max(xs)) + pad), min(self.img.height, int(max(ys)) + pad)
        if x1 <= x0 or y1 <= y0:
            return None
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in q], fill=255)
        if clip is not None:
            m = ImageChops.multiply(m, clip.crop((x0, y0, x1, y1)))
        caja = (x0, y0, x1, y1)
        self.img.paste(col[:3] + (255,), caja, m)
        if sombra:  # degradado: zona alejada de la luz cada vez más oscura
            s = Image.new("L", m.size, 0)
            s.paste(m, (int(luz[0] * off), int(luz[1] * off)))
            s = s.filter(ImageFilter.GaussianBlur(off * 0.7))
            sh = ImageChops.multiply(m, ImageChops.invert(s)).point(lambda v: int(v * 0.85))
            self.img.paste(oscuro(col, 0.62) + (255,), caja, sh)
        if brillo:
            b = Image.new("L", m.size, 0)
            b.paste(m, (int(-luz[0] * off * 0.6), int(-luz[1] * off * 0.6)))
            b = b.filter(ImageFilter.GaussianBlur(off * 0.6))
            hl = ImageChops.multiply(m, ImageChops.invert(b)).point(lambda v: int(v * 0.45))
            self.img.paste(claro(col, 0.38) + (255,), caja, hl)
        if textura > 0:
            r = _ruido(m.width, m.height, x0, y0)
            osc = ImageChops.multiply(m, r.point(lambda v: int(max(0, 128 - v) * 2 * textura * 4)))
            self.img.paste(oscuro(col, 0.7) + (255,), caja, osc)
        if borde:
            self.d.line(q + [q[0]], fill=oscuro(col, 0.38), width=max(2, int(ancho * 0.65 * SS)), joint="curve")
        full = Image.new("L", self.img.size, 0)
        full.paste(m, (x0, y0))
        return full

    def pelaje(self, pts, col, n=140, largo=16, semilla=1, hacia_fuera=1.0):
        """Trazos de pelo a lo largo del contorno de una forma (en coordenadas locales)."""
        pts = catmull(pts, 5)
        r = random.Random(semilla)
        L = len(pts)
        for i in range(n):
            k = int(i / n * L)
            (xa, ya), (xb, yb) = pts[k], pts[(k + 1) % L]
            dx, dy = xb - xa, yb - ya
            nrm = math.hypot(dx, dy) or 1
            nx, ny = dy / nrm * hacia_fuera, -dx / nrm * hacia_fuera
            lg = largo * r.uniform(0.6, 1.3)
            ang = r.uniform(-0.5, 0.5)
            ex = xa + (nx * math.cos(ang) - ny * math.sin(ang)) * lg
            ey = ya + (nx * math.sin(ang) + ny * math.cos(ang)) * lg
            c = oscuro(col, r.uniform(0.55, 0.85)) if i % 3 else claro(col, 0.25)
            self.linea([(xa - nx * 6, ya - ny * 6), (ex, ey)], c, r.uniform(2, 3.5))


# --------------------------------------------------------------------------- #
# Acabado de cine para cada fotograma (numpy)
# --------------------------------------------------------------------------- #
_GRANO = [np.random.default_rng(i).normal(0, 1.6, (960, 540, 1)).astype(np.float32) for i in range(4)]


def acabado(a: np.ndarray, n: int, calidez=1.0, bloom=0.22) -> np.ndarray:
    """a: uint8 (H, W, 3). Curva de color suave, calidez, bloom en luces y grano fino."""
    f = a.astype(np.float32) / 255.0
    f = f * f * (3 - 2 * f) * 0.35 + f * 0.65  # curva S suave (más contraste sin quemar)
    if calidez != 1.0:
        f[..., 0] *= calidez
        f[..., 2] /= calidez
    if bloom > 0:
        peq = Image.fromarray(a).resize((a.shape[1] // 6, a.shape[0] // 6), Image.BILINEAR)
        b = np.asarray(peq, np.float32) / 255.0
        b = np.clip((b - 0.72) / 0.28, 0, 1)
        bi = Image.fromarray((b * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
        bi = np.asarray(bi.resize((a.shape[1], a.shape[0]), Image.BILINEAR), np.float32) / 255.0
        f = f + bi * bloom
    out = f * 255.0
    g = _GRANO[(n // 2) % 4]  # el grano cambia cada 2 fotogramas: más liviano para comprimir
    out = out + np.repeat(np.repeat(g, 2, 0), 2, 1)[:a.shape[0], :a.shape[1]]
    return np.clip(out, 0, 255).astype(np.uint8)
