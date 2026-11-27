"""Lugares, edificios, vehículos y animales (SVG). Base de cada dibujo: (0, 0) = centro abajo, tamaño ~400 px con s=1."""
from __future__ import annotations

import math
import random

from ilustra import TINTA, anim, deriva, dib, g, lin, rad, vaiven

O = f'stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"'
O3 = f'stroke="{TINTA}" stroke-width="3.5" stroke-linejoin="round"'


def ventanas(x0, y0, cols, filas, w, h, dx, dy, rng, prob=.65, on="#ffd77a", off="#1c2233"):
    """Ventanas iluminadas al azar (de noche) o vidrios celestes (prob<0 = de día)."""
    if prob < 0:
        on, off, prob = "#cfe6f5", "#8fb0c9", .5
    return "".join(f'<rect x="{x0 + c * dx}" y="{y0 + f * dy}" width="{w}" height="{h}" rx="2" fill="{on if rng.random() < prob else off}"/>'
                   for c in range(cols) for f in range(filas))


# ============================================================================ ciudades
@dib("ciudad")
def ciudad(p, u, t):
    """Silueta de ciudad. era: moderna | antigua (casas de madera con techos a dos aguas) | colonial | sovietica."""
    era = p.get("era", "moderna")
    y = p.get("y", 1250)
    rng = random.Random(p.get("semilla", 3))
    capas = []
    de_dia = p.get("hora") in ("dia", "amanecer", "atardecer") and "color" not in p
    paleta_dia = ["#d9a07a", "#c9b28a", "#b98a6a", "#e0c9a6", "#a8b4c4", "#c4a07a", "#9ab0a8"]
    tonos = [(("#8d9bb5" if era == "moderna" else "#b9a48a"), 1.0), (("#a9b4c9" if era == "moderna" else "#d2b48f"), 0.7)] if de_dia else \
        [(p.get("color_lejos", "#1d2540"), 1.0), (p.get("color", "#121829"), 0.7)]
    for k, (col, alto) in enumerate(tonos):
        x = -120 + k * 40
        edif = []
        while x < 1200:
            w = rng.uniform(70, 150) if era == "moderna" else rng.uniform(80, 130)
            h = (rng.uniform(220, 620) if era == "moderna" else rng.uniform(150, 260)) * alto
            if de_dia and era != "moderna":
                col = rng.choice(paleta_dia)
            if era == "moderna":
                edif.append(f'<rect x="{x:.0f}" y="{y - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{col}"' + (f' stroke="{TINTA}" stroke-width="3"' if de_dia else "") + '/>')
                edif.append(ventanas(x + 10, y - h + 14, int((w - 14) // 22), int((h - 20) // 30), 10, 14, 22, 30, rng,
                                     -1 if de_dia else (.45 if k else .25)))
            elif era == "sovietica":
                edif.append(f'<rect x="{x:.0f}" y="{y - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{col}"/>'
                            f'<polygon points="{x + w * .3:.0f},{y - h:.0f} {x + w * .5:.0f},{y - h - 70:.0f} {x + w * .7:.0f},{y - h:.0f}" fill="{col}"/>')
                edif.append(ventanas(x + 10, y - h + 14, int((w - 14) // 24), int((h - 20) // 34), 10, 16, 24, 34, rng, .3))
            else:
                techo = rng.uniform(50, 110)
                colc = col if era == "antigua" else ("#c98b5b" if k else "#a86d45")
                if de_dia:
                    colc = rng.choice(paleta_dia)
                edif.append(f'<path d="M{x:.0f},{y} V{y - h:.0f} L{x + w / 2:.0f},{y - h - techo:.0f} L{x + w:.0f},{y - h:.0f} V{y} Z" fill="{colc}" {O3}/>')
                if era == "antigua":
                    for v in range(int(h // 50)):
                        edif.append(f'<line x1="{x:.0f}" x2="{x + w:.0f}" y1="{y - 40 - v * 50:.0f}" y2="{y - 40 - v * 50:.0f}" stroke="#2a1a10" stroke-width="5"/>')
                    edif.append(f'<line x1="{x + w * .25:.0f}" x2="{x + w * .25:.0f}" y1="{y - h:.0f}" y2="{y}" stroke="#2a1a10" stroke-width="5"/>'
                                f'<line x1="{x + w * .75:.0f}" x2="{x + w * .75:.0f}" y1="{y - h:.0f}" y2="{y}" stroke="#2a1a10" stroke-width="5"/>')
                edif.append(ventanas(x + w * .3, y - h * .7, 2, 2, 18, 22, w * .25, h * .35, rng, -1 if de_dia else .55))
            x += w + (rng.uniform(0, 20) if era == "moderna" else -6)
        capas.append(f'<g id="{u}c{k}">{"".join(edif)}</g>')
    return "".join(capas)


@dib("casa")
def casa(p, u, t):
    """tipo: suburbana | granja | colonial | madera. luces=True enciende ventanas."""
    tipo = p.get("tipo", "suburbana")
    on = "#ffd77a" if p.get("luces", True) else "#1a1f2e"
    pared = p.get("pared", {"suburbana": "#e8dcc4", "granja": "#cfc2a6", "colonial": "#d9a07a", "madera": "#b98a5c"}[tipo])
    techo = p.get("techo", {"suburbana": "#5b3a2c", "granja": "#6e4b33", "colonial": "#8b3a2a", "madera": "#3b2a20"}[tipo])
    d = f'<defs>{lin(pared, "#7d705c", u + "p", 0)}{lin(techo, "#2a1a12", u + "t")}</defs>'
    if tipo == "colonial":
        s = (d + f'<rect x="-210" y="-420" width="420" height="420" fill="url(#{u}p)" {O}/>'
             f'<rect x="-230" y="-440" width="460" height="30" fill="{techo}" {O3}/>'
             f'<rect x="-150" y="-360" width="80" height="120" fill="{on}" {O3}/><rect x="70" y="-360" width="80" height="120" fill="{on}" {O3}/>'
             f'<rect x="-180" y="-240" width="140" height="18" fill="#3b2a20"/><rect x="40" y="-240" width="140" height="18" fill="#3b2a20"/>'
             + "".join(f'<line x1="{-176 + k * 16}" x2="{-176 + k * 16}" y1="-240" y2="-200" stroke="#3b2a20" stroke-width="5"/>' for k in range(9))
             + "".join(f'<line x1="{44 + k * 16}" x2="{44 + k * 16}" y1="-240" y2="-200" stroke="#3b2a20" stroke-width="5"/>' for k in range(9))
             + f'<rect x="-180" y="-204" width="140" height="10" fill="#3b2a20"/><rect x="40" y="-204" width="140" height="10" fill="#3b2a20"/>'
             f'<path d="M-50,0 V-130 Q0,-170 50,-130 V0 Z" fill="#3b2a20" {O3}/>')
    else:
        alto = 300 if tipo != "granja" else 260
        s = (d + f'<rect x="-230" y="{-alto}" width="460" height="{alto}" fill="url(#{u}p)" {O}/>'
             f'<path d="M-270,{-alto + 6} L0,{-alto - 200} L270,{-alto + 6} Z" fill="url(#{u}t)" {O}/>'
             f'<rect x="-170" y="{-alto + 60}" width="90" height="90" fill="{on}" {O3}/><rect x="80" y="{-alto + 60}" width="90" height="90" fill="{on}" {O3}/>'
             f'<line x1="-125" x2="-125" y1="{-alto + 60}" y2="{-alto + 150}" stroke="{TINTA}" stroke-width="4"/><line x1="125" x2="125" y1="{-alto + 60}" y2="{-alto + 150}" stroke="{TINTA}" stroke-width="4"/>'
             f'<rect x="-45" y="-150" width="90" height="150" fill="#4a3020" {O3}/><circle cx="25" cy="-75" r="6" fill="#d9b25b"/>'
             f'<circle cx="0" cy="{-alto - 90}" r="26" fill="{on}" {O3}/>')
        if tipo == "granja":
            s += f'<rect x="230" y="-200" width="260" height="200" fill="#8a3b2a" {O}/><path d="M220,-196 L360,-300 L500,-196 Z" fill="#5a2a1d" {O}/>'
    if p.get("parpadeo"):
        t.js.append(f'tl.to("#{u} rect[fill=\\"{on}\\"]", {{opacity: 0.3, duration: 0.08, yoyo: true, repeat: 5}}, {t.at(p["parpadeo"])});')
    return g(p, s, u)


@dib("catedral")
def catedral(p, u, t):
    """Catedral con cúpula (San Pablo) o con aguja gótica (antigua San Pablo, aguja=True)."""
    c = p.get("color", "#cbbfa6")
    d = f'<defs>{lin(c, "#6f6656", u + "c", 0)}</defs>'
    if p.get("aguja"):
        s = (d + f'<rect x="-320" y="-260" width="640" height="260" fill="url(#{u}c)" {O}/><path d="M-340,-256 L0,-380 L340,-256 Z" fill="#5d5346" {O}/>'
             f'<rect x="-70" y="-520" width="140" height="300" fill="url(#{u}c)" {O}/><path d="M-70,-516 L0,-900 L70,-516 Z" fill="#5d5346" {O}/>'
             + "".join(f'<path d="M{-280 + k * 80},-60 V-170 Q{-255 + k * 80},-210 {-230 + k * 80},-170 V-60 Z" fill="#2b2f45" {O3}/>' for k in range(8)))
    else:
        s = (d + f'<rect x="-330" y="-260" width="660" height="260" fill="url(#{u}c)" {O}/>'
             f'<rect x="-150" y="-430" width="300" height="180" fill="url(#{u}c)" {O}/>'
             f'<path d="M-170,-430 Q0,-720 170,-430 Z" fill="url(#{u}c)" {O}/><rect x="-18" y="-700" width="36" height="80" fill="#d8b04f" {O3}/>'
             + "".join(f'<rect x="{-300 + k * 60}" y="-220" width="24" height="200" fill="#9b917c"/>' for k in range(11)))
    return g(p, s, u)


@dib("castillo")
def castillo(p, u, t):
    """Castillo en un risco (Bran): torres con techos rojos cónicos."""
    s = (f'<defs>{lin("#e7dccb", "#9e8f78", u + "m", 0)}{lin("#a23a2a", "#5e1d14", u + "t")}{lin("#4a4f5e", "#1d2130", u + "r")}</defs>'
         f'<path d="M-360,0 L-300,-160 L-180,-230 L180,-240 L300,-150 L360,0 Z" fill="url(#{u}r)" {O}/>'
         f'<rect x="-200" y="-520" width="400" height="300" fill="url(#{u}m)" {O}/>'
         f'<rect x="-260" y="-640" width="120" height="420" fill="url(#{u}m)" {O}/><path d="M-280,-636 L-200,-820 L-120,-636 Z" fill="url(#{u}t)" {O}/>'
         f'<rect x="120" y="-600" width="110" height="380" fill="url(#{u}m)" {O}/><path d="M100,-596 L175,-770 L250,-596 Z" fill="url(#{u}t)" {O}/>'
         f'<path d="M-210,-516 L0,-640 L210,-516 Z" fill="url(#{u}t)" {O}/>'
         + "".join(f'<rect x="{x}" y="{y}" width="26" height="40" rx="12" fill="#ffd77a" {O3}/>' for x, y in
                   [(-215, -560), (-215, -470), (150, -520), (160, -420), (-120, -440), (-40, -440), (40, -440), (100, -360)]))
    return g(p, s, u)


@dib("isla")
def isla(p, u, t):
    """Isla con árboles y, opcional, campanario y edificios en ruinas (Poveglia) o choza (Xochimilco)."""
    s = [f'<defs>{lin("#3c4a2f", "#1b2416", u + "i")}{lin("#c8b89a", "#7d6f58", u + "e", 0)}</defs>',
         f'<path d="M-420,0 Q-380,-70 -250,-80 L250,-85 Q390,-70 430,0 Z" fill="url(#{u}i)" {O}/>']
    if p.get("campanario"):
        s.append(f'<rect x="-330" y="-320" width="300" height="240" fill="url(#{u}e)" {O}/>'
                 + "".join(f'<rect x="{-310 + k * 56}" y="-280" width="28" height="44" fill="#141824"/>' for k in range(5))
                 + "".join(f'<rect x="{-310 + k * 56}" y="-200" width="28" height="44" fill="#141824"/>' for k in range(5))
                 + f'<rect x="60" y="-520" width="90" height="440" fill="url(#{u}e)" {O}/><path d="M50,-516 L105,-600 L160,-516 Z" fill="#6b5a46" {O}/>'
                 f'<rect x="88" y="-480" width="34" height="50" fill="#141824"/>')
    rng = random.Random(4)
    for k in range(p.get("arboles", 7)):
        x = rng.uniform(-360, 360)
        h = rng.uniform(120, 220)
        s.append(f'<path d="M{x:.0f},-70 L{x:.0f},{-70 - h * .5:.0f}" stroke="#2b2016" stroke-width="10"/>'
                 f'<ellipse cx="{x:.0f}" cy="{-70 - h * .7:.0f}" rx="{h * .38:.0f}" ry="{h * .42:.0f}" fill="#2c3f24" {O3}/>')
    return g(p, "".join(s), u)


@dib("pasillo")
def pasillo(p, u, t):
    """Pasillo infinito en perspectiva (Backrooms): paredes amarillas, alfombra, tubos fluorescentes."""
    pared = p.get("pared", "#c9b458")
    s = [f'<defs>{lin("#e3d27a", "#8f7f31", u + "p", 0)}{lin("#8b8460", "#4a4630", u + "a")}{lin("#f3eed2", "#cfc7a0", u + "t")}</defs>',
         f'<rect width="1080" height="1920" fill="#6e6338"/>',
         f'<polygon points="0,0 1080,0 700,760 380,760" fill="url(#{u}t)"/>',
         f'<polygon points="0,1920 1080,1920 700,1100 380,1100" fill="url(#{u}a)"/>',
         f'<polygon points="0,0 380,760 380,1100 0,1920" fill="url(#{u}p)"/>',
         f'<polygon points="1080,0 700,760 700,1100 1080,1920" fill="url(#{u}p)" opacity=".85"/>',
         f'<rect x="380" y="760" width="320" height="340" fill="#d8c56a"/>',
         f'<rect x="470" y="830" width="140" height="270" fill="#a8973f"/>']
    for k in range(6):
        f = k / 6
        y = 40 + f * 700
        w = 1080 - f * 1080 * 0.7
        s.append(f'<rect id="{u}l{k}" x="{540 - w * .18:.0f}" y="{y:.0f}" width="{w * .36:.0f}" height="{24 - f * 18:.0f}" fill="#fffbe6"/>')
    s.append(f'<defs>{rad([(0, "#fff7c8", .5), (1, "#fff7c8", 0)], u + "g")}</defs><ellipse cx="540" cy="300" rx="700" ry="500" fill="url(#{u}g)"/>')
    t.js.append(f'tl.to("#{u}l2, #{u}l4", {{opacity: 0.2, duration: 0.06, yoyo: true, repeat: 5}}, {t.at(p.get("parpadeo", 1.2))});')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("interior")
def interior(p, u, t):
    """Habitación: pared, piso, zócalo, ventana con vista (noche/dia/tormenta) y luz cálida."""
    pared, piso = p.get("pared", "#5a4a3c"), p.get("piso", "#3a2a1e")
    y = p.get("piso_y", 1250)
    vista = p.get("vista")
    s = [f'<defs>{lin(pared, "#1a140f", u + "p")}{lin(piso, "#120c08", u + "s")}{rad([(0, "#ffcf7a", .35), (1, "#ffcf7a", 0)], u + "l")}</defs>',
         f'<rect x="-200" y="-200" width="1480" height="{y + 200}" fill="url(#{u}p)"/>',
         f'<rect x="-200" y="{y}" width="1480" height="{1920 - y + 200}" fill="url(#{u}s)"/>',
         f'<rect x="-200" y="{y - 30}" width="1480" height="30" fill="#2a1d14"/>']
    if p.get("papel"):
        s.append("".join(f'<line x1="{x}" x2="{x}" y1="0" y2="{y - 30}" stroke="#000" stroke-opacity=".08" stroke-width="22"/>' for x in range(0, 1100, 90)))
    for k in range(9):
        s.append(f'<line x1="{-200 + k * 190}" x2="{-400 + k * 260}" y1="{y}" y2="1920" stroke="#000" stroke-opacity=".18" stroke-width="4"/>')
    if vista:
        vx, vy = p.get("ventana_x", 700), p.get("ventana_y", 420)
        cielo = {"noche": ("#08101f", "#1d3260"), "dia": ("#7cc4f5", "#d8f0ff"), "tormenta": ("#1a2230", "#3a4556"),
                 "nieve": ("#2a3550", "#8a9bb8")}[vista]
        s.append(f'<defs>{lin(*cielo, u + "v")}</defs><rect x="{vx}" y="{vy}" width="300" height="380" fill="url(#{u}v)" {O}/>'
                 f'<line x1="{vx + 150}" x2="{vx + 150}" y1="{vy}" y2="{vy + 380}" stroke="{TINTA}" stroke-width="12"/>'
                 f'<line x1="{vx}" x2="{vx + 300}" y1="{vy + 190}" y2="{vy + 190}" stroke="{TINTA}" stroke-width="12"/>')
        if vista == "noche":
            s.append(f'<circle cx="{vx + 220}" cy="{vy + 90}" r="34" fill="#fff6d8"/>')
        if vista == "tormenta":
            s.append(f'<rect id="{u}rl" x="{vx}" y="{vy}" width="300" height="380" fill="#e6eeff" opacity="0"/>')
            t.js.append(f'tl.to("#{u}rl", {{opacity: 0.8, duration: 0.05, yoyo: true, repeat: 3}}, {t.at(p.get("rayo_en", 1.0))});')
    if p.get("luz", True):
        s.append(f'<ellipse cx="{p.get("luz_x", 300)}" cy="{p.get("luz_y", 500)}" rx="700" ry="700" fill="url(#{u}l)" style="mix-blend-mode:screen"/>')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("estadio")
def estadio(p, u, t):
    """Estadio repleto visto desde el campo: gradas con público (puntos de colores), focos y césped."""
    rng = random.Random(9)
    s = [f'<defs>{lin("#2f7d32", "#174d1a", u + "c")}{lin("#2b2f45", "#141826", u + "g")}</defs>',
         f'<rect x="-200" y="200" width="1480" height="900" fill="url(#{u}g)"/>']
    for fila in range(26):
        y = 260 + fila * 32
        for k in range(46):
            x = -150 + k * 30 + (fila % 2) * 15
            col = rng.choice(["#f2f2f2", "#2f5d9e", "#ffd21f", "#e3141b", "#7fb2d6", "#1d1d1d", "#58c46a"])
            s.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{col}" opacity=".85"/>')
    s.append(f'<rect x="-200" y="1100" width="1480" height="900" fill="url(#{u}c)"/>')
    s.append("".join(f'<rect x="{-200 + k * 120}" y="1100" width="60" height="900" fill="#ffffff" opacity=".05"/>' for k in range(14)))
    s.append(f'<line x1="-200" x2="1280" y1="1450" y2="1450" stroke="#fff" stroke-width="8" opacity=".8"/>')
    for x in (90, 990):
        s.append(f'<rect x="{x - 8}" y="0" width="16" height="260" fill="#9aa0aa"/><rect x="{x - 70}" y="0" width="140" height="60" fill="#e9eef7" {O3}/>'
                 f'<defs>{rad([(0, "#ffffff", .5), (1, "#ffffff", 0)], u + f"f{x}")}</defs><circle cx="{x}" cy="30" r="320" fill="url(#{u}f{x})"/>')
    if p.get("silencio"):
        s.append(f'<rect id="{u}os" x="-200" y="200" width="1480" height="900" fill="#000" opacity="0"/>')
        anim(t, f"#{u}os", "{opacity: 0}", "{opacity: 0.55, duration: 1.2, ease: 'power2.in'}", p.get("silencio_en", 0.6))
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("desierto")
def desierto(p, u, t):
    y = p.get("y", 1180)
    s = (f'<defs>{lin("#e6b980", "#b9824a", u + "a")}{lin("#d29a5e", "#8a5a2f", u + "b")}</defs>'
         f'<path d="M-200,{y} Q200,{y - 70} 560,{y - 10} T1300,{y - 30} V2000 H-200 Z" fill="url(#{u}a)"/>'
         f'<path d="M-200,{y + 220} Q300,{y + 140} 700,{y + 210} T1400,{y + 180} V2000 H-200 Z" fill="url(#{u}b)"/>')
    return s


@dib("arboles")
def arboles(p, u, t):
    """Fila de árboles (bosque). muñecas=True cuelga muñecas viejas de las ramas (Xochimilco)."""
    rng = random.Random(p.get("semilla", 5))
    y = p.get("y", 1250)
    col = p.get("color", "#243520")
    s = []
    for k in range(p.get("n", 6)):
        x = -60 + k * (1200 / p.get("n", 6)) + rng.uniform(-30, 30)
        h = rng.uniform(500, 760)
        s.append(f'<path d="M{x - 24:.0f},{y} L{x - 10:.0f},{y - h:.0f} L{x + 10:.0f},{y - h:.0f} L{x + 24:.0f},{y} Z" fill="#2b2016"/>')
        for r in range(3):
            bx = x + (1 if r % 2 else -1) * rng.uniform(60, 140)
            by = y - h * (0.45 + r * .18)
            s.append(f'<path d="M{x:.0f},{by + 40:.0f} Q{(x + bx) / 2:.0f},{by - 20:.0f} {bx:.0f},{by:.0f}" stroke="#2b2016" stroke-width="12" fill="none"/>')
            if p.get("muñecas"):
                L = rng.uniform(40, 90)
                s.append(f'<g id="{u}m{k}{r}"><line x1="{bx:.0f}" y1="{by:.0f}" x2="{bx:.0f}" y2="{by + L:.0f}" stroke="#9a8a6a" stroke-width="3"/>'
                         f'<circle cx="{bx:.0f}" cy="{by + L + 16:.0f}" r="18" fill="#d8c9b0" {O3}/>'
                         f'<circle cx="{bx - 6:.0f}" cy="{by + L + 14:.0f}" r="3.5" fill="#111"/><circle cx="{bx + 6:.0f}" cy="{by + L + 14:.0f}" r="3.5" fill="#111"/>'
                         f'<path d="M{bx - 16:.0f},{by + L + 32:.0f} L{bx + 16:.0f},{by + L + 32:.0f} L{bx + 22:.0f},{by + L + 80:.0f} L{bx - 22:.0f},{by + L + 80:.0f} Z" fill="{rng.choice(["#b9a58a", "#8a7d6a", "#c7a3a3"])}" {O3}/></g>')
                vaiven(t, f"#{u}m{k}{r}", f"rotation: {rng.choice([-5, 5])}, transformOrigin: '50% 0%'", periodo=rng.uniform(1.6, 2.6))
        s.append(f'<ellipse cx="{x:.0f}" cy="{y - h:.0f}" rx="{rng.uniform(150, 230):.0f}" ry="{rng.uniform(110, 160):.0f}" fill="{col}" opacity=".95"/>')
    return f'<g id="{u}">{"".join(s)}</g>'


# ============================================================================ vehículos
@dib("velero")
def velero(p, u, t):
    """Velero antiguo de tres palos. fantasma=True: luces y fiesta a bordo (Caleuche)."""
    fantasma = p.get("fantasma", False)
    vela = "#e9e2cf" if not fantasma else "#cfe8ff"
    s = [f'<defs>{lin("#5a3a22", "#2a1a10", u + "c")}{lin(vela, "#a89f88", u + "v", 0)}</defs>',
         f'<path d="M-330,-40 L330,-40 L290,40 L-280,40 Z" fill="url(#{u}c)" {O}/>',
         f'<path d="M-330,-40 L-380,-90 L-300,-60 Z" fill="url(#{u}c)" {O3}/>']
    for k, (x, h) in enumerate([(-170, 520), (20, 600), (200, 470)]):
        s.append(f'<line x1="{x}" y1="-40" x2="{x}" y2="{-40 - h}" stroke="{TINTA}" stroke-width="9"/>')
        for j in range(3):
            w = 180 - j * 30
            yv = -80 - j * h * 0.3
            s.append(f'<path id="{u}v{k}{j}" d="M{x - w / 2},{yv - h * .24:.0f} Q{x},{yv - h * .1:.0f} {x + w / 2},{yv - h * .24:.0f} L{x + w / 2 + 10},{yv:.0f} Q{x},{yv + 30:.0f} {x - w / 2 - 10},{yv:.0f} Z" fill="url(#{u}v)" {O3}/>')
    if fantasma:
        s.append("".join(f'<circle id="{u}f{k}" cx="{-280 + k * 46}" cy="-10" r="9" fill="#fff3a6"/>' for k in range(13)))
        s.append(f'<defs>{rad([(0, "#bfe6ff", .45), (1, "#bfe6ff", 0)], u + "g")}</defs><ellipse cx="0" cy="-260" rx="520" ry="420" fill="url(#{u}g)" style="mix-blend-mode:screen"/>')
        t.js.append(f'tl.to("#{u} circle[id^={u}f]", {{opacity: 0.35, duration: 0.3, yoyo: true, repeat: {int(t.dur / 0.3)}, stagger: 0.05}}, {t.at(0)});')
    vaiven(t, f"#{u}", "rotation: 1.2, y: '+=8'", periodo=2.6)
    if p.get("mov") == "avanza":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 100)}'")
    if p.get("hundir_en") is not None:
        anim(t, f"#{u}", "{opacity: 1}", "{y: '+=240', opacity: 0, duration: 1.4, ease: 'power2.in'}", p["hundir_en"])
    return g(p, "".join(s), u)


@dib("barca")
def barca(p, u, t):
    """Trajinera / canoa / bote de pescador."""
    col = p.get("color", "#2e6db0")
    s = (f'<path d="M-260,-30 L260,-30 Q230,30 170,40 L-170,40 Q-230,30 -260,-30 Z" fill="{col}" {O}/>'
         f'<path d="M-250,-20 L250,-20" stroke="#ffd21f" stroke-width="8"/>')
    if p.get("techo"):
        s = (f'<rect x="-200" y="-200" width="400" height="20" fill="{p.get("color_techo", "#d63c3c")}" {O3}/>'
             f'<line x1="-180" y1="-180" x2="-180" y2="-30" stroke="{TINTA}" stroke-width="8"/><line x1="180" y1="-180" x2="180" y2="-30" stroke="{TINTA}" stroke-width="8"/>') + s
    vaiven(t, f"#{u}", "rotation: 2, y: '+=6'", periodo=2.2)
    if p.get("mov") == "avanza":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 120)}'")
    return g(p, s, u)


@dib("avion")
def avion(p, u, t):
    """Bombardero de 4 hélices (Tu-95, plateado) o avión genérico de pasajeros."""
    col = p.get("color", "#c9ced6")
    s = (f'<defs>{lin("#ffffff", col, u + "f")}{lin(col, "#6f7681", u + "a")}</defs>'
         f'<path d="M-420,0 Q-430,-40 -380,-50 L360,-50 Q440,-40 460,-10 Q440,20 360,22 L-380,22 Q-430,20 -420,0 Z" fill="url(#{u}f)" {O}/>'
         f'<path d="M-60,-10 L-260,-260 L-180,-260 L120,-10 Z" fill="url(#{u}a)" {O}/>'
         f'<path d="M-60,10 L-200,200 L-130,200 L100,10 Z" fill="url(#{u}a)" {O}/>'
         f'<path d="M-380,-40 L-440,-190 L-380,-190 L-300,-40 Z" fill="url(#{u}a)" {O}/>'
         + "".join(f'<rect x="{-60 + k * 18}" y="-38" width="10" height="12" rx="3" fill="#2b3a55"/>' for k in range(16))
         + f'<path d="M400,-36 Q430,-30 440,-14 L400,-14 Z" fill="#2b3a55"/>')
    if p.get("estrella"):
        s += f'<polygon points="-330,-6 -322,-28 -314,-6 -336,-20 -308,-20" fill="#c41e1e"/>'
    mov = p.get("mov", "cruza")
    if mov == "cruza":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 380)}'")
    vaiven(t, f"#{u}", "y: '+=10'", periodo=1.8)
    return g(p, s, u)


@dib("tren")
def tren(p, u, t):
    """Tren de época (vapor, 1920s) entrando en la estación."""
    col = p.get("color", "#2f3d2a")
    s = (f'<defs>{lin(col, "#141a12", u + "c")}</defs>'
         f'<rect x="-420" y="-260" width="300" height="220" rx="16" fill="url(#{u}c)" {O}/>'
         f'<rect x="-110" y="-250" width="260" height="210" rx="10" fill="url(#{u}c)" {O}/><rect x="160" y="-250" width="260" height="210" rx="10" fill="url(#{u}c)" {O}/>'
         f'<rect x="-480" y="-180" width="80" height="120" rx="10" fill="#1b1b1b" {O3}/><rect x="-380" y="-330" width="50" height="80" fill="#1b1b1b" {O3}/>'
         + "".join(f'<rect x="{-90 + k * 60}" y="-220" width="44" height="60" rx="5" fill="#ffd77a"/>' for k in range(4))
         + "".join(f'<rect x="{180 + k * 60}" y="-220" width="44" height="60" rx="5" fill="#ffd77a"/>' for k in range(4))
         + "".join(f'<circle id="{u}r{k}" cx="{x}" cy="-30" r="34" fill="#111" stroke="#777" stroke-width="6"/>' for k, x in enumerate([-380, -250, -40, 90, 230, 360])))
    humo = "".join(f'<circle id="{u}h{k}" cx="-355" cy="-350" r="{30 + k * 6}" fill="#cfd3da" opacity=".5"/>' for k in range(6))
    for k in range(6):
        anim(t, f"#{u}h{k}", "{x: 0, y: 0, opacity: 0.6, scale: 0.5}",
             f"{{x: {120 + k * 30}, y: {-160 - k * 40}, opacity: 0, scale: 2, duration: {max(1.0, t.dur):.2f}, ease: 'power1.out'}}", k * 0.2)
    mov = p.get("mov", "llega")
    if mov == "llega":
        anim(t, f"#{u}", "{x: -900}", f"{{x: 0, duration: {min(2.5, t.dur * 0.8):.2f}, ease: 'power2.out'}}")
    elif mov == "parte":
        anim(t, f"#{u}", "{x: 0}", f"{{x: 1200, duration: {t.dur:.2f}, ease: 'power2.in'}}", 0.3)
    return g(p, humo + s, u)


@dib("cohete")
def cohete(p, u, t):
    """Cohete soviético (R-7) despegando con fuego."""
    s = (f'<defs>{lin("#ffffff", "#aeb4bd", u + "c", 0)}{lin("#fff3a6", "#ff6a00", u + "f")}</defs>'
         f'<g id="{u}fu"><path d="M-60,0 Q0,320 60,0 Z" fill="url(#{u}f)"/><path d="M-120,-20 Q-100,200 -70,-10 Z" fill="url(#{u}f)"/><path d="M120,-20 Q100,200 70,-10 Z" fill="url(#{u}f)"/></g>'
         f'<path d="M-55,0 L-55,-520 Q0,-700 55,-520 L55,0 Z" fill="url(#{u}c)" {O}/>'
         f'<path d="M-55,0 L-130,-20 L-110,-260 L-55,-300 Z" fill="url(#{u}c)" {O}/><path d="M55,0 L130,-20 L110,-260 L55,-300 Z" fill="url(#{u}c)" {O}/>'
         f'<rect x="-55" y="-430" width="110" height="26" fill="#c41e1e"/>')
    vaiven(t, f"#{u}fu", "scaleY: 1.15, transformOrigin: '50% 0%'", periodo=0.12)
    if p.get("mov", "despega") == "despega":
        anim(t, f"#{u}", "{y: 0}", f"{{y: -1400, duration: {t.dur:.2f}, ease: 'power2.in'}}", 0.4)
    return g(p, s, u)


@dib("satelite")
def satelite(p, u, t):
    """Sputnik: esfera brillante con 4 antenas largas."""
    s = (f'<defs>{rad([(0, "#ffffff", 1), (.6, "#c9ced6", 1), (1, "#6f7681", 1)], u + "e", "35%", "35%", "70%")}</defs>'
         + "".join(f'<line x1="0" y1="0" x2="{-420 + k * 30}" y2="{160 + k * 50}" stroke="#d9dde3" stroke-width="5"/>' for k in range(4))
         + f'<circle cx="0" cy="0" r="90" fill="url(#{u}e)" {O}/><circle cx="-30" cy="-30" r="18" fill="#fff" opacity=".7"/>')
    deriva(t, f"#{u}", f"x: '+={p.get('avance', 260)}', rotation: 25")
    return g(p, s, u)


@dib("camion")
def camion(p, u, t):
    """Camión de basura / de carga de los 80."""
    col = p.get("color", "#d9d2c3")
    s = (f'<rect x="-360" y="-280" width="460" height="230" rx="8" fill="{col}" {O}/>'
         f'<path d="M110,-200 L260,-200 L320,-120 L320,-50 L110,-50 Z" fill="#c0392b" {O}/><path d="M140,-185 L250,-185 L290,-125 L140,-125 Z" fill="#9cc9e6"/>'
         + "".join(f'<circle cx="{x}" cy="-40" r="44" fill="#111" stroke="#777" stroke-width="7"/>' for x in (-270, -120, 230)))
    if p.get("mov", "llega") == "llega":
        anim(t, f"#{u}", "{x: -1000}", f"{{x: 0, duration: {min(2.2, t.dur * 0.8):.2f}, ease: 'power2.out'}}")
    return g(p, s, u)


# ============================================================================ animales
@dib("perro")
def perro(p, u, t):
    """Perro sentado de perfil mirando a la derecha. raza: akita (canela con pecho blanco, cola enroscada) o laika
    (blanca con manchas canela). collar=True agrega collar rojo."""
    raza = p.get("raza", "akita")
    if raza == "akita":
        c1, c2, c3 = "#e3a865", "#b97a3c", "#f8f1e4"
    elif raza == "crema":  # Hachiko era un akita blanco cremoso
        c1, c2, c3 = "#f3e6cc", "#d2bb92", "#fffaf0"
    else:
        c1, c2, c3 = "#f2ede4", "#cfc5b5", "#ffffff"
    d = (f'<defs>{lin(c1, c2, u + "p", 0)}{lin(c2, "#8a5a2a" if raza == "akita" else "#b8ad9c", u + "s", 0)}'
         f'{lin(c3, "#e3d9c8", u + "b", 0)}</defs>')
    cola = (f'<g id="{u}cola"><path d="M-110,-205 Q-205,-250 -170,-325 Q-120,-370 -92,-300 Q-84,-262 -120,-262" fill="none" stroke="{TINTA}" stroke-width="42" stroke-linecap="round"/>'
            f'<path d="M-110,-205 Q-205,-250 -170,-325 Q-120,-370 -92,-300 Q-84,-262 -120,-262" fill="none" stroke="{c1}" stroke-width="32" stroke-linecap="round"/>'
            f'<path d="M-150,-300 Q-130,-338 -106,-308" fill="none" stroke="{c3}" stroke-width="12" stroke-linecap="round"/></g>')
    cuerpo = (f'<path d="M-150,-4 Q-178,-150 -92,-218 Q-10,-262 64,-240 Q104,-222 104,-168 L100,-10 Q96,4 70,4 L-130,4 Q-148,4 -150,-4 Z" '
              f'fill="url(#{u}p)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
              f'<ellipse cx="-74" cy="-92" rx="82" ry="92" fill="url(#{u}s)" stroke="{TINTA}" stroke-width="4"/>'
              f'<ellipse cx="-22" cy="-8" rx="56" ry="15" fill="{c3}" stroke="{TINTA}" stroke-width="4"/>'
              f'<path d="M62,-238 Q118,-214 104,-138 Q86,-118 64,-138 Z" fill="url(#{u}b)" stroke="{TINTA}" stroke-width="3.5"/>'
              f'<path d="M70,-150 L66,-8 Q68,4 92,4 Q106,4 104,-8 L104,-150 Z" fill="{c2}" stroke="{TINTA}" stroke-width="4"/>'
              f'<path d="M34,-160 L32,-8 Q34,4 58,4 Q74,4 72,-8 L72,-160 Z" fill="url(#{u}p)" stroke="{TINTA}" stroke-width="4"/>'
              f'<path d="M34,-26 L72,-26" stroke="{c3}" stroke-width="16"/>'
              f'<path d="M-132,-170 Q-150,-110 -140,-40" stroke="#fff" stroke-opacity=".25" stroke-width="8" fill="none"/>')
    if raza == "laika":
        cuerpo += (f'<ellipse cx="-60" cy="-150" rx="48" ry="34" fill="#c9a27a" opacity=".85"/>'
                   f'<ellipse cx="-110" cy="-60" rx="30" ry="22" fill="#c9a27a" opacity=".8"/>')
    cabeza = (f'<g id="{u}cab"><path d="M68,-246 Q56,-332 122,-352 Q172,-356 192,-308 Q228,-298 244,-278 Q240,-256 204,-252 L154,-244 Q104,-222 68,-246 Z" '
              f'fill="url(#{u}p)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
              f'<path d="M150,-292 Q200,-296 242,-278 Q236,-258 204,-254 L160,-250 Q138,-266 150,-292 Z" fill="url(#{u}b)"/>'
              f'<path d="M92,-338 L78,-410 L132,-354 Z" fill="{c1}" stroke="{TINTA}" stroke-width="4" stroke-linejoin="round"/>'
              f'<path d="M96,-346 L88,-388 L118,-354 Z" fill="#e8a6a0"/>'
              f'<path d="M128,-352 L148,-416 L170,-342 Z" fill="{c2}" stroke="{TINTA}" stroke-width="4" stroke-linejoin="round"/>'
              f'<ellipse cx="164" cy="-312" rx="8" ry="9" fill="{TINTA}"/><circle cx="167" cy="-315" r="2.6" fill="#fff"/>'
              f'<path d="M150,-326 Q164,-334 178,-326" stroke="{TINTA}" stroke-width="3" fill="none" stroke-linecap="round"/>'
              f'<ellipse cx="240" cy="-278" rx="11" ry="9" fill="{TINTA}"/>'
              f'<path d="M204,-256 Q216,-248 230,-256" stroke="{TINTA}" stroke-width="3" fill="none" stroke-linecap="round"/>'
              f'<path d="M84,-300 Q110,-280 150,-282" stroke="#fff" stroke-opacity=".25" stroke-width="6" fill="none"/></g>')
    collar = (f'<path d="M66,-236 Q100,-212 128,-232" stroke="#b3261e" stroke-width="14" fill="none" stroke-linecap="round"/>'
              f'<circle cx="104" cy="-216" r="9" fill="#e8b830" stroke="{TINTA}" stroke-width="2"/>') if p.get("collar") else ""
    s = d + cola + cuerpo + collar + cabeza
    if p.get("cola", True):
        vaiven(t, f"#{u}cola", "rotation: 7, transformOrigin: '90% 90%'", periodo=0.7)
    vaiven(t, f"#{u}cab", "rotation: -3, transformOrigin: '20% 90%'", periodo=2.6)
    vaiven(t, f"#{u}", "scaleY: 1.012, transformOrigin: '50% 100%'", periodo=2.0)
    return g(p, s, u)


@dib("estatua_perro")
def estatua_perro(p, u, t):
    s = (f'<defs>{lin("#7a8a6a", "#3e4a36", u + "b", 0)}{lin("#9aa0a6", "#5c6268", u + "pd")}</defs>'
         f'<rect x="-220" y="-260" width="440" height="260" fill="url(#{u}pd)" {O}/><rect x="-250" y="-290" width="500" height="40" fill="#8a9096" {O3}/>')
    perro_svg = (perro({"x": 0, "y": -290, "s": 1.05, "cola": False}, u + "pp", t).replace("#e3a865", "#7f9070").replace("#b97a3c", "#5a6a4c")
                 .replace("#f8f1e4", "#9aab8a").replace("#8a5a2a", "#3e4a36").replace("#e3d9c8", "#7f9070").replace("#e8a6a0", "#5a6a4c"))
    return g(p, s + perro_svg, u)


@dib("piramides")
def piramides(p, u, t):
    s = (f'<defs>{lin("#f0c27a", "#b9824a", u + "a", 0)}{lin("#a8743e", "#6b4423", u + "b", 0)}</defs>')
    for x, w, h in [(-260, 300, 260), (120, 460, 400), (420, 220, 180)]:
        s += (f'<polygon points="{x - w / 2},0 {x},{-h} {x},0" fill="url(#{u}a)" {O3}/>'
              f'<polygon points="{x},{-h} {x + w / 2},0 {x},0" fill="url(#{u}b)" {O3}/>')
    return g(p, s, u)


@dib("ejercito")
def ejercito(p, u, t):
    """Multitud de soldados en silueta con lanzas, en filas (ejército enorme)."""
    rng = random.Random(p.get("semilla", 2))
    col = p.get("color", "#1a1d2b")
    s = []
    for fila in range(p.get("filas", 4)):
        y = -fila * 34
        for k in range(28):
            x = -560 + k * 42 + (fila % 2) * 20 + rng.uniform(-6, 6)
            h = 120 - fila * 12
            s.append(f'<circle cx="{x:.0f}" cy="{y - h:.0f}" r="{12 - fila}" fill="{col}"/><rect x="{x - 10:.0f}" y="{y - h + 10:.0f}" width="20" height="{h - 10}" fill="{col}"/>'
                     f'<line x1="{x + 14:.0f}" y1="{y:.0f}" x2="{x + 18:.0f}" y2="{y - h - 60:.0f}" stroke="{col}" stroke-width="3"/>')
    deriva(t, f"#{u}", f"x: '+={p.get('avance', 60)}'")
    return g(p, "".join(s), u)


@dib("callejon")
def callejon(p, u, t):
    """Callejón colonial muy angosto visto desde abajo: dos fachadas con balcones que casi se tocan y escalones."""
    hora = p.get("hora", "noche")
    cielo = ("#0b1430", "#2a3a6a") if hora == "noche" else ("#7cc4f5", "#d8f0ff")
    on = "#ffd77a" if hora == "noche" else "#2a1d14"
    s = [f'<defs>{lin(*cielo, u + "c")}{lin("#d98a5a", "#8a4a2a", u + "a", 0)}{lin("#6fa8c9", "#3a6a8a", u + "b", 0)}</defs>',
         f'<rect x="300" y="0" width="480" height="1920" fill="url(#{u}c)"/>',
         f'<polygon points="0,0 470,0 470,1920 0,1920" fill="url(#{u}a)"/>',
         f'<polygon points="610,0 1080,0 1080,1920 610,1920" fill="url(#{u}b)"/>']
    for k, y in enumerate([300, 720, 1140]):
        s.append(f'<rect x="250" y="{y}" width="160" height="230" fill="{on}" stroke="{TINTA}" stroke-width="5"/>'
                 f'<rect x="670" y="{y}" width="160" height="230" fill="{on}" stroke="{TINTA}" stroke-width="5"/>')
    # balcones que casi se tocan
    s.append(f'<rect x="220" y="520" width="300" height="20" fill="#2a1a10"/><rect x="560" y="520" width="300" height="20" fill="#2a1a10"/>'
             + "".join(f'<line x1="{x}" x2="{x}" y1="440" y2="520" stroke="#2a1a10" stroke-width="6"/>' for x in list(range(230, 520, 28)) + list(range(570, 860, 28)))
             + f'<rect x="220" y="430" width="300" height="12" fill="#2a1a10"/><rect x="560" y="430" width="300" height="12" fill="#2a1a10"/>')
    if p.get("pareja"):
        s.append(f'<g id="{u}a1"><circle cx="470" cy="360" r="34" fill="#e2b48c" stroke="{TINTA}" stroke-width="4"/><path d="M430,440 Q470,380 510,440 Z" fill="#6b2d3f"/>'
                 f'<path d="M436,350 Q440,300 472,300 Q500,300 506,340 Q500,420 480,440 L450,440 Q430,400 436,350 Z" fill="#2a1a10" opacity=".9"/></g>'
                 f'<g id="{u}a2"><circle cx="610" cy="360" r="34" fill="#c99a6e" stroke="{TINTA}" stroke-width="4"/><path d="M570,440 Q610,380 650,440 Z" fill="#3a4a2c"/>'
                 f'<path d="M578,345 Q610,310 642,345 Z" fill="#2a1a10"/></g>')
        anim(t, f"#{u}a1", "{x: -30}", "{x: 0, duration: 1.0, ease: 'power2.inOut'}", .3)
        anim(t, f"#{u}a2", "{x: 30}", "{x: 0, duration: 1.0, ease: 'power2.inOut'}", .3)
    for k in range(6):
        y = 1500 + k * 70
        s.append(f'<rect x="{-50 - k * 30}" y="{y}" width="{1180 + k * 60}" height="70" fill="{"#b9a88a" if k != 2 else p.get("escalon", "#b9a88a")}" stroke="{TINTA}" stroke-width="4"/>')
    if p.get("escalon"):
        s.append(f'<rect id="{u}e" x="-110" y="1640" width="1300" height="70" fill="#ffd21f" opacity=".0"/>')
        vaiven(t, f"#{u}e", "opacity: 0.55", periodo=0.8, dt=.3)
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("templo_azteca")
def templo_azteca(p, u, t):
    """Templo Mayor escalonado con dos santuarios arriba."""
    s = (f'<defs>{lin("#d9b98a", "#8a6a4a", u + "p", 0)}</defs>'
         + "".join(f'<rect x="{-420 + k * 60}" y="{-110 - k * 110}" width="{840 - k * 120}" height="110" fill="url(#{u}p)" {O3}/>' for k in range(5))
         + f'<rect x="-50" y="-550" width="100" height="550" fill="#a8845a" {O3}/>'
         + "".join(f'<line x1="-50" x2="50" y1="{-k * 26}" y2="{-k * 26}" stroke="#6b4a2e" stroke-width="3"/>' for k in range(21))
         + f'<rect x="-220" y="-700" width="160" height="150" fill="#c0392b" {O3}/><rect x="60" y="-700" width="160" height="150" fill="#2f5d9e" {O3}/>'
         f'<path d="M-230,-700 L-140,-760 L-50,-700 Z" fill="#7a1d14" {O3}/><path d="M50,-700 L140,-760 L230,-700 Z" fill="#1e3e6b" {O3}/>')
    return g(p, s, u)


@dib("tripode")
def tripode(p, u, t):
    """Máquina marciana de tres patas con rayo verde (La guerra de los mundos)."""
    s = (f'<defs>{lin("#9aa0a6", "#3e4248", u + "m", 0)}{rad([(0, "#8dff9c", .8), (1, "#8dff9c", 0)], u + "g")}</defs>'
         f'<path d="M-40,-520 L-300,0 M0,-520 L40,0 M40,-520 L320,0" stroke="#3e4248" stroke-width="22" fill="none" stroke-linecap="round"/>'
         f'<ellipse cx="0" cy="-580" rx="220" ry="100" fill="url(#{u}m)" {O}/><ellipse cx="0" cy="-620" rx="140" ry="60" fill="#5c6268" {O3}/>'
         f'<circle cx="120" cy="-560" r="30" fill="#8dff9c"/><circle id="{u}r" cx="120" cy="-560" r="200" fill="url(#{u}g)"/>')
    vaiven(t, f"#{u}r", "scale: 1.4, transformOrigin: '50% 50%'", periodo=0.6)
    vaiven(t, f"#{u}", "y: -14, rotation: 1", periodo=1.8)
    return g(p, s, u)
