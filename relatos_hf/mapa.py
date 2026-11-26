"""Mapa del mundo en SVG a partir de world-atlas (TopoJSON, licencia ISC), en proyección equirectangular.

    svg_mundo(centro_lon=0, resaltar={"Chile": "#E3141B"})  ->  (markup <g>, función proyectar(lat, lon) -> (x, y))

El mundo mide 3600 × 1800 unidades (10 por grado). `centro_lon` deja ese meridiano en el centro, para que una ruta por
el Pacífico (Chile → Japón) no quede cortada en el borde.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATOS = Path(__file__).parent / "datos"
K = 10.0
ANCHO, ALTO = 360 * K, 180 * K


@lru_cache(maxsize=2)
def _topo(nombre: str):
    d = json.loads((DATOS / nombre).read_text(encoding="utf-8"))
    sx, sy = d["transform"]["scale"]
    tx, ty = d["transform"]["translate"]
    arcos = []
    for arco in d["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arco:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcos.append(pts)
    return d, arcos


def _anillo(indices, arcos):
    pts = []
    for i in indices:
        a = arcos[i] if i >= 0 else arcos[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def proyector(centro_lon: float = 0.0):
    def proyectar(lat: float, lon: float):
        l = (lon - centro_lon + 540.0) % 360.0 - 180.0
        return round((l + 180.0) * K, 1), round((90.0 - lat) * K, 1)
    return proyectar


def _path(anillos, proyectar) -> str:
    partes = []
    for anillo in anillos:
        seg, prev = [], None
        for lon, lat in anillo:
            x, y = proyectar(lat, lon)
            if prev is not None and abs(x - prev) > ANCHO / 2:  # cruza el borde: corta el trazo
                if len(seg) > 2:
                    partes.append("M" + "L".join(f"{a},{b}" for a, b in seg) + "Z")
                seg = []
            seg.append((x, y))
            prev = x
        if len(seg) > 2:
            partes.append("M" + "L".join(f"{a},{b}" for a, b in seg) + "Z")
    return "".join(partes)


def svg_mundo(centro_lon: float = 0.0, resaltar: dict | None = None, detalle: str = "50m",
              tierra="#2b3a55", borde="#0d1424", ids: bool = True):
    """Devuelve (markup de los países como <path>, proyectar). `resaltar`: {nombre en inglés: color}."""
    resaltar = resaltar or {}
    d, arcos = _topo(f"countries-{detalle}.json")
    proyectar = proyector(centro_lon)
    out = []
    for g in d["objects"]["countries"]["geometries"]:
        nombre = g.get("properties", {}).get("name", "")
        if g["type"] == "Polygon":
            anillos = [_anillo(r, arcos) for r in g["arcs"]]
        elif g["type"] == "MultiPolygon":
            anillos = [_anillo(r, arcos) for poly in g["arcs"] for r in poly]
        else:
            continue
        p = _path(anillos, proyectar)
        if not p:
            continue
        color = resaltar.get(nombre, tierra)
        ident = f' id="pais-{"".join(c for c in nombre.lower() if c.isalnum())}"' if ids and nombre in resaltar else ""
        out.append(f'<path{ident} d="{p}" fill="{color}" stroke="{borde}" stroke-width="1.2"/>')
    return "".join(out), proyectar
