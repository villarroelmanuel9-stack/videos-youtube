"""
Ilustraciones vectoriales (SVG) para los relatos en HyperFrames.

Cada elemento se registra con @dib("nombre") y recibe (p, u, t):
  p  dict de parámetros del plan (x, y, s, color, hora, mov...)
  u  prefijo único para los id (no se repiten entre tomas)
  t  objeto Toma: t.at(dt) da el segundo absoluto, t.dur la duración, t.js la lista de animaciones GSAP
Devuelve el markup SVG (en coordenadas de 1080×1920). Estilo común: contorno azul tinta, sombreado con degradados,
luz que viene de arriba a la izquierda, borde de luz (rim) del lado iluminado y sombras suaves.
"""
from __future__ import annotations

import math
import random
import re

TINTA = "#151a2e"
DIBUJOS = {}


def dib(nombre):
    def deco(fn):
        DIBUJOS[nombre] = fn
        return fn
    return deco


def g(p, interior, u="", origen=(0, 0)):
    """Coloca un dibujo: x, y (punto de apoyo), s (escala), r (giro), espejo."""
    x, y, s = p.get("x", 540), p.get("y", 1200), p.get("s", 1.0)
    esp = -1 if p.get("espejo") else 1
    r = p.get("r", 0)
    ident = f' id="{u}"' if u else ""
    reflejo = ""
    if p.get("reflejo"):
        copia = re.sub(r'\sid="[^"]*"', "", interior)
        reflejo = (f'<g transform="translate({x} {y}) scale({s * esp} {-s * 0.45}) translate({-origen[0]} {-origen[1]})" '
                   f'opacity="{p.get("reflejo_op", 0.14)}">{copia}</g>')
    return (reflejo + f'<g transform="translate({x} {y}) rotate({r}) scale({s * esp} {s}) translate({-origen[0]} {-origen[1]})">'
            f'<g{ident}>{interior}</g></g>')


def lin(c1, c2, u, ang=90):
    x2, y2 = (0, 1) if ang == 90 else (1, 0) if ang == 0 else (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    return (f'<linearGradient id="{u}" x1="0" y1="0" x2="{x2:.2f}" y2="{y2:.2f}">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')


def rad(stops, u, cx="50%", cy="50%", r="50%"):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<radialGradient id="{u}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def anim(t, sel, desde, hasta, dt=0.0):
    t.js.append(f'tl.fromTo("{sel}", {desde}, {hasta}, {t.at(dt)});')


def vaiven(t, sel, props, periodo=2.0, dt=0.0, ease="sine.inOut"):
    """Movimiento de ida y vuelta durante toda la toma (repeticiones finitas, determinista)."""
    veces = max(1, int((t.dur - dt) / periodo) + 1)
    t.js.append(f'tl.to("{sel}", {{{props}, duration: {periodo / 2:.2f}, yoyo: true, repeat: {veces * 2 - 1}, '
                f'ease: "{ease}"}}, {t.at(dt)});')


def deriva(t, sel, props, dt=0.0, ease="none"):
    t.js.append(f'tl.to("{sel}", {{{props}, duration: {max(0.3, t.dur - dt):.2f}, ease: "{ease}"}}, {t.at(dt)});')


# ============================================================================ cielos
CIELOS = {
    "dia": ("#5fb4f0", "#bfe6ff", "#e8f6ff"),
    "atardecer": ("#2b2a63", "#d1566b", "#ffb36b"),
    "amanecer": ("#3b5a9a", "#f19a86", "#ffe1a8"),
    "noche": ("#050914", "#0d1a38", "#1d3260"),
    "tormenta": ("#0f141f", "#26303f", "#3e4756"),
    "niebla": ("#59636e", "#8b949c", "#b3bac0"),
    "espacio": ("#02030a", "#060a1c", "#0b1430"),
    "sepia": ("#3a2412", "#8a5a2b", "#d9a861"),
    "rojo": ("#1a0505", "#5c0d0d", "#b3261e"),
}


@dib("cielo")
def cielo(p, u, t):
    hora = p.get("hora", "noche")
    a, b, c = CIELOS.get(hora, CIELOS["noche"])
    hz = p.get("horizonte", 1150)
    out = [f'<defs>{lin(a, b, u + "g")}{lin(b, c, u + "g2")}</defs>',
           f'<rect x="-200" y="-200" width="1480" height="{hz + 200}" fill="url(#{u}g)"/>',
           f'<rect x="-200" y="{hz * 0.55:.0f}" width="1480" height="{hz * 0.45 + 60:.0f}" fill="url(#{u}g2)" opacity=".9"/>']
    rng = random.Random(hash(u) % 1000)
    if hora in ("noche", "espacio", "tormenta"):
        n = 150 if hora == "espacio" else 90
        est = []
        for k in range(n):
            x, y = rng.uniform(-150, 1230), rng.uniform(-150, hz * 0.8)
            r = rng.choice([1.2, 1.6, 2.2, 3.0]) if hora != "tormenta" else 1.4
            est.append(f'<circle class="{u}e{k % 3}" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{rng.uniform(.4, 1):.2f}"/>')
        out.append("".join(est))
        for k in range(3):
            vaiven(t, f".{u}e{k}", "opacity: 0.25", periodo=1.2 + k * 0.5, dt=0.1 * k)
    if hora == "espacio":
        out.append(f'<defs>{rad([(0, "#6c3bd1", .35), (1, "#6c3bd1", 0)], u + "n1")}{rad([(0, "#1fb3c9", .25), (1, "#1fb3c9", 0)], u + "n2")}</defs>'
                   f'<ellipse cx="300" cy="500" rx="520" ry="300" fill="url(#{u}n1)"/><ellipse cx="820" cy="1100" rx="460" ry="380" fill="url(#{u}n2)"/>')
    astro = p.get("astro", {"noche": "luna", "dia": "sol", "atardecer": "sol", "amanecer": "sol"}.get(hora))
    if p.get("astro_x") is None and astro and "astro" not in p:
        p = {**p, "astro_x": 820 if astro == "luna" else 790, "astro_y": 360 if hora != "atardecer" else hz - 240,
             "astro_r": 55 if astro == "luna" else 65}
    if astro:
        ax, ay, ar = p.get("astro_x", 800), p.get("astro_y", 380), p.get("astro_r", 70)
        if astro == "luna":
            out.append(f'<defs>{rad([(0, "#fff7d6", .55), (.35, "#fff7d6", .15), (1, "#fff7d6", 0)], u + "h")}'
                       f'{rad([(0, "#fffdf2", 1), (.8, "#e9e2c6", 1), (1, "#cfc6a6", 1)], u + "m", "40%", "38%", "60%")}</defs>'
                       f'<circle cx="{ax}" cy="{ay}" r="{ar * 4}" fill="url(#{u}h)"/>'
                       f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="url(#{u}m)"/>'
                       f'<circle cx="{ax + ar * .3}" cy="{ay - ar * .2}" r="{ar * .18}" fill="#d8cfae" opacity=".7"/>'
                       f'<circle cx="{ax - ar * .35}" cy="{ay + ar * .25}" r="{ar * .12}" fill="#d8cfae" opacity=".6"/>')
        else:
            out.append(f'<defs>{rad([(0, "#fff2c4", .9), (.25, "#ffd27a", .45), (1, "#ff9a3c", 0)], u + "h")}</defs>'
                       f'<circle cx="{ax}" cy="{ay}" r="{ar * 5}" fill="url(#{u}h)"/>'
                       f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="#fff4cf"/>')
    if hora in ("atardecer", "amanecer", "dia", "tormenta", "niebla"):
        col = {"dia": "#ffffff", "tormenta": "#2a3240", "niebla": "#c9cfd4"}.get(hora, "#ffc2a1")
        op = {"dia": .9, "tormenta": .95, "niebla": .6}.get(hora, .55)
        for k in range(5):
            cx, cy = rng.uniform(-100, 1100), rng.uniform(150, hz * 0.6)
            w = rng.uniform(260, 520)
            out.append(f'<g id="{u}nb{k}" opacity="{op}"><ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{w:.0f}" ry="{w * .16:.0f}" fill="{col}"/>'
                       f'<ellipse cx="{cx - w * .25:.0f}" cy="{cy - w * .1:.0f}" rx="{w * .4:.0f}" ry="{w * .17:.0f}" fill="{col}"/>'
                       f'<ellipse cx="{cx + w * .2:.0f}" cy="{cy - w * .07:.0f}" rx="{w * .32:.0f}" ry="{w * .14:.0f}" fill="{col}"/></g>')
            deriva(t, f"#{u}nb{k}", f"x: {rng.choice([-1, 1]) * rng.uniform(40, 110):.0f}")
    return "".join(out)


# ============================================================================ mar y tierra
@dib("mar")
def mar(p, u, t):
    hz = p.get("horizonte", 1150)
    hora = p.get("hora", "noche")
    c1, c2 = {"noche": ("#0b1d3a", "#02060f"), "dia": ("#2f8fd0", "#0b3d6e"), "atardecer": ("#3a3f7a", "#121633"),
              "tormenta": ("#1d2a36", "#070b10"), "niebla": ("#5c6c78", "#27323b"), "amanecer": ("#4a6aa8", "#1a2a52")}.get(
        hora, ("#0b1d3a", "#02060f"))
    brillo = {"noche": "#9fc3ff", "dia": "#ffffff", "atardecer": "#ffb38a", "amanecer": "#ffd1a8"}.get(hora, "#a9b8c4")
    out = [f'<defs>{lin(c1, c2, u + "m")}</defs>', f'<rect x="-300" y="{hz}" width="1680" height="{1920 - hz + 300}" fill="url(#{u}m)"/>']
    rng = random.Random(len(u) * 7 + hz)
    for k in range(7):
        y = hz + 30 + k * k * 16 + k * 22
        amp = 4 + k * 3.2
        lam = 90 + k * 30
        d = f"M-300,{y}" + "".join(f" q{lam / 4:.0f},{-amp:.1f} {lam / 2:.0f},0 t{lam / 2:.0f},0" for _ in range(int(1900 / lam) + 2))
        op = 0.18 + k * 0.05
        out.append(f'<path id="{u}w{k}" d="{d}" fill="none" stroke="{brillo}" stroke-width="{1.5 + k * .7:.1f}" '
                   f'stroke-linecap="round" stroke-dasharray="{rng.randint(40, 120)} {rng.randint(60, 200)}" opacity="{op:.2f}"/>')
        deriva(t, f"#{u}w{k}", f"x: {(-1) ** k * (30 + k * 18)}")
    if p.get("reflejo_x") is not None:
        rx = p["reflejo_x"]
        out.append(f'<defs>{lin(brillo, brillo, u + "r")}</defs><g id="{u}rf" opacity=".55">' + "".join(
            f'<rect x="{rx - 70 + rng.uniform(-30, 30):.0f}" y="{hz + 20 + k * 38}" width="{rng.uniform(40, 150):.0f}" height="5" rx="2.5" fill="{brillo}"/>'
            for k in range(14)) + "</g>")
        vaiven(t, f"#{u}rf", "opacity: 0.25", periodo=0.9)
    return "".join(out)


@dib("montanas")
def montanas(p, u, t):
    hz = p.get("horizonte", 1150)
    cols = p.get("colores", ["#3b4a6b", "#2a3552", "#1a2238"])
    nieve = p.get("nieve", False)
    rng = random.Random(hz)
    out = []
    for k, col in enumerate(cols):
        base = hz + k * 10
        pts = [(-200, base)]
        x = -200
        while x < 1300:
            x += rng.uniform(140, 260)
            pts.append((x, base - rng.uniform(180, 420) * (1 - k * .18)))
            x += rng.uniform(80, 160)
            pts.append((x, base - rng.uniform(40, 140)))
        pts.append((1300, base))
        d = "M" + " L".join(f"{a:.0f},{b:.0f}" for a, b in pts) + " Z"
        out.append(f'<g id="{u}c{k}"><path d="{d}" fill="{col}"/>')
        if nieve:
            for (a, b), (c, d2) in zip(pts[1:-1:2], pts[2:-1:2]):
                out.append(f'<path d="M{a - 40:.0f},{b + 55:.0f} L{a:.0f},{b:.0f} L{a + 45:.0f},{b + 60:.0f} L{a + 15:.0f},{b + 45:.0f} Z" fill="#e8eef7" opacity=".85"/>')
        out.append("</g>")
    return "".join(out)


def _tipo_suelo(c1):
    h = c1.lstrip("#")
    r, g_, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16)
    if g_ > r + 15 and g_ > b:
        return "pasto"
    if min(r, g_, b) > 190:
        return "nieve"
    if r > 170 and g_ > 120 and b < 130:
        return "arena"
    if abs(r - g_) < 14 and abs(g_ - b) < 14:
        return "adoquin"
    return "tierra"


@dib("suelo")
def suelo(p, u, t):
    """Suelo con detalle en perspectiva (más chico y denso cerca del horizonte). tipo: tierra, pasto, adoquin,
    arena, nieve, baldosa, madera, asfalto (si no se indica se deduce del color)."""
    y = p.get("y", 1300)
    c1, c2 = p.get("colores", ["#3d2b1f", "#1a120c"])
    tipo = p.get("tipo") or _tipo_suelo(c1)
    rng = random.Random(int(y) + len(tipo))
    out = [f'<defs>{lin(c1, c2, u + "s")}</defs><rect x="-300" y="{y}" width="1680" height="{2000 - y}" fill="url(#{u}s)"/>']
    alto = 2000 - y

    def prof(f):  # 0 = horizonte, 1 = primer plano
        return y + alto * (f ** 1.7)

    if tipo in ("adoquin", "baldosa", "madera"):
        filas = 16 if tipo == "adoquin" else 11
        for k in range(1, filas):
            yy = prof(k / filas)
            out.append(f'<line x1="-300" x2="1380" y1="{yy:.0f}" y2="{yy:.0f}" stroke="#000" stroke-opacity=".22" stroke-width="{1 + 3 * k / filas:.1f}"/>')
            if tipo != "madera":
                paso = 30 + 110 * (k / filas)
                off = (k % 2) * paso / 2
                x = -300 + off
                y0 = prof((k - 1) / filas)
                while x < 1380:
                    out.append(f'<line x1="{x + (x - 540) * .0:.0f}" x2="{x + (x - 540) * .25:.0f}" y1="{y0:.0f}" y2="{yy:.0f}" stroke="#000" stroke-opacity=".18" stroke-width="{1 + 2 * k / filas:.1f}"/>')
                    x += paso
        if tipo == "madera":
            for k in range(-8, 10):
                out.append(f'<line x1="{540 + k * 40}" y1="{y}" x2="{540 + k * 170}" y2="2000" stroke="#000" stroke-opacity=".2" stroke-width="3"/>')
            for k in range(40):
                fx, fy = rng.uniform(0, 1080), prof(rng.uniform(.1, 1))
                out.append(f'<path d="M{fx:.0f},{fy:.0f} q30,-4 60,0" stroke="#000" stroke-opacity=".12" stroke-width="2" fill="none"/>')
        out.append(f'<rect x="-300" y="{y}" width="1680" height="{alto}" fill="url(#{u}s)" opacity=".0"/>')
    else:
        n = {"tierra": 90, "pasto": 140, "arena": 70, "nieve": 60, "asfalto": 40}.get(tipo, 80)
        for k in range(n):
            f = rng.uniform(0.02, 1)
            yy, xx = prof(f), rng.uniform(-100, 1180)
            esc = .3 + 1.4 * f
            if tipo == "pasto":
                col = rng.choice(["#3f7a32", "#2f5e26", "#5a9a44", "#26481e"])
                out.append(f'<path d="M{xx:.0f},{yy:.0f} l{-4 * esc:.1f},{-18 * esc:.1f} M{xx:.0f},{yy:.0f} l{2 * esc:.1f},{-22 * esc:.1f} M{xx:.0f},{yy:.0f} l{7 * esc:.1f},{-16 * esc:.1f}" '
                           f'stroke="{col}" stroke-width="{1.5 + 1.5 * f:.1f}" stroke-linecap="round"/>')
                if rng.random() < .08:
                    out.append(f'<circle cx="{xx:.0f}" cy="{yy - 14 * esc:.0f}" r="{3 * esc:.1f}" fill="{rng.choice(["#ffd21f", "#ffffff", "#e8649a"])}"/>')
            elif tipo == "tierra":
                if rng.random() < .65:
                    out.append(f'<ellipse cx="{xx:.0f}" cy="{yy:.0f}" rx="{rng.uniform(3, 9) * esc:.1f}" ry="{rng.uniform(2, 5) * esc:.1f}" fill="#000" opacity="{rng.uniform(.12, .25):.2f}"/>'
                               f'<ellipse cx="{xx - 1:.0f}" cy="{yy - 1.5 * esc:.0f}" rx="{rng.uniform(3, 8) * esc:.1f}" ry="{rng.uniform(2, 4) * esc:.1f}" fill="#fff" opacity=".09"/>')
                else:
                    out.append(f'<path d="M{xx:.0f},{yy:.0f} l{20 * esc:.1f},{3 * esc:.1f} l{14 * esc:.1f},{-4 * esc:.1f} l{18 * esc:.1f},{5 * esc:.1f}" stroke="#000" stroke-opacity=".2" stroke-width="{1 + f:.1f}" fill="none"/>')
            elif tipo == "arena":
                out.append(f'<path d="M{xx:.0f},{yy:.0f} q{30 * esc:.0f},{-6 * esc:.1f} {60 * esc:.0f},0" stroke="#fff" stroke-opacity=".18" stroke-width="{1 + 1.5 * f:.1f}" fill="none"/>'
                           f'<path d="M{xx:.0f},{yy + 3 * esc:.0f} q{30 * esc:.0f},{-6 * esc:.1f} {60 * esc:.0f},0" stroke="#000" stroke-opacity=".12" stroke-width="{1 + f:.1f}" fill="none"/>')
            elif tipo == "nieve":
                out.append(f'<ellipse cx="{xx:.0f}" cy="{yy:.0f}" rx="{rng.uniform(10, 30) * esc:.0f}" ry="{rng.uniform(2, 5) * esc:.1f}" fill="#9fb0cc" opacity=".25"/>'
                           f'<circle cx="{xx + 8:.0f}" cy="{yy - 3:.0f}" r="{1.2 + f:.1f}" fill="#fff"/>')
            else:  # asfalto
                out.append(f'<path d="M{xx:.0f},{yy:.0f} l{25 * esc:.0f},{6 * esc:.1f} l{10 * esc:.0f},{-8 * esc:.1f}" stroke="#000" stroke-opacity=".3" stroke-width="{1 + f:.1f}" fill="none"/>')
    out.append(f'<rect x="-300" y="{y}" width="1680" height="40" fill="#000" opacity=".12"/>')
    return "".join(out)


@dib("niebla")
def niebla(p, u, t):
    y = p.get("y", 1150)
    op = p.get("op", 0.5)
    col = p.get("color", "#c9d3de")
    out = [f'<defs>{rad([(0, col, op), (1, col, 0)], u + "f")}</defs>']
    for k in range(4):
        out.append(f'<ellipse id="{u}f{k}" cx="{-100 + k * 400}" cy="{y + (k % 2) * 60}" rx="620" ry="150" fill="url(#{u}f)"/>')
        deriva(t, f"#{u}f{k}", f"x: {180 if k % 2 else -160}")
    return "".join(out)


@dib("lluvia")
def lluvia(p, u, t):
    rng = random.Random(3)
    gotas = "".join(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - 14:.0f}" y2="{y + 60:.0f}" stroke="#c9d6ff" stroke-width="2" opacity="{rng.uniform(.2, .55):.2f}"/>'
                    for x, y in ((rng.uniform(-100, 1250), rng.uniform(-400, 1920)) for _ in range(160)))
    t.js.append(f'tl.fromTo("#{u}l", {{y: -400, x: 0}}, {{y: 400, x: -90, duration: 0.5, ease: "none", repeat: {int(t.dur / 0.5) + 1}}}, {t.at(0)});')
    return f'<g id="{u}l">{gotas}</g>'


@dib("particulas")
def particulas(p, u, t):
    """Brasas, polvo, nieve o ceniza subiendo/bajando."""
    tipo = p.get("tipo", "brasas")
    rng = random.Random(len(u))
    col = {"brasas": "#ffb347", "nieve": "#ffffff", "polvo": "#e9d8b0", "ceniza": "#9a9a9a", "chispas": "#fff2a8",
           "verde": "#8dff9c", "roja": "#ff3b3b", "moscas": "#111111"}.get(tipo, "#ffffff")
    sube = tipo in ("brasas", "chispas", "verde", "roja")
    out = []
    for k in range(p.get("n", 40)):
        x, y = rng.uniform(0, 1080), rng.uniform(300, 1700)
        r = rng.uniform(2, 6)
        out.append(f'<circle id="{u}p{k}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{col}" opacity="{rng.uniform(.4, .9):.2f}"/>')
        dy = -rng.uniform(250, 600) if sube else rng.uniform(250, 600)
        anim(t, f"#{u}p{k}", "{x: 0, y: 0}", f"{{x: {rng.uniform(-80, 80):.0f}, y: {dy:.0f}, duration: {max(0.5, t.dur):.2f}, ease: 'none'}}")
    if sube and tipo not in ("verde", "roja"):
        out = [f'<g style="mix-blend-mode:screen">'] + out + ["</g>"]
    return "".join(out)


@dib("luz")
def luz(p, u, t):
    """Halo de luz (lámpara, fuego, ventana)."""
    x, y, r = p.get("x", 540), p.get("y", 900), p.get("r", 300)
    col = p.get("color", "#ffcf7a")
    out = f'<defs>{rad([(0, col, p.get("op", .7)), (.4, col, p.get("op", .7) * .35), (1, col, 0)], u + "l")}</defs>' \
          f'<circle id="{u}c" cx="{x}" cy="{y}" r="{r}" fill="url(#{u}l)" style="mix-blend-mode:screen"/>'
    if p.get("parpadeo"):
        vaiven(t, f"#{u}c", "opacity: 0.6", periodo=0.35)
    return out


@dib("rayos")
def rayos(p, u, t):
    x, y = p.get("x", 800), p.get("y", 200)
    col = p.get("color", "#fff1c1")
    out = [f'<defs>{lin(col, col, u + "r")}</defs><g id="{u}g" opacity="{p.get("op", .18)}" style="mix-blend-mode:screen">']
    for k in range(7):
        a = -70 + k * 22
        out.append(f'<polygon points="{x},{y} {x + 2200 * math.sin(math.radians(a - 3)):.0f},{y + 2200 * math.cos(math.radians(a - 3)):.0f} '
                   f'{x + 2200 * math.sin(math.radians(a + 3)):.0f},{y + 2200 * math.cos(math.radians(a + 3)):.0f}" fill="{col}"/>')
    out.append("</g>")
    vaiven(t, f"#{u}g", f"opacity: {p.get('op', .18) * .4:.2f}", periodo=3.0)
    return "".join(out)


# ============================================================================ barcos
@dib("transatlantico")
def transatlantico(p, u, t):
    """Transatlántico de 4 chimeneas (Titanic, Olympic, Britannic). color: casco; hospital=True para el Britannic."""
    casco = p.get("casco", "#121418")
    hospital = p.get("hospital", False)
    if hospital:
        casco = "#f2f2ee"
    luces = p.get("luces", True)
    defs = (f'<defs>{lin("#2a2f38" if not hospital else "#ffffff", casco, u + "h")}{lin("#fbf8ef", "#cfc9b8", u + "s")}'
            f'{lin("#e3a65a", "#a86b2c", u + "f")}</defs>')
    cuerpo = [
        defs,
        # casco con proa a la derecha
        f'<path d="M-560,-40 L560,-40 L620,-110 L640,-112 L600,40 Q590,70 560,72 L-520,72 Q-560,70 -570,40 Z" fill="url(#{u}h)" stroke="{TINTA}" stroke-width="5"/>',
        f'<path d="M-566,52 L596,52 L592,66 Q584,72 560,72 L-520,72 Q-556,70 -566,52 Z" fill="#8c1d1d"/>' if not hospital else
        f'<path d="M-566,20 L604,20 L600,32 L-568,32 Z" fill="#2e8b57"/>',
        # superestructura
        f'<path d="M-430,-40 L430,-40 L410,-110 L-410,-110 Z" fill="url(#{u}s)" stroke="{TINTA}" stroke-width="4"/>',
        f'<path d="M-380,-110 L360,-110 L345,-150 L-365,-150 Z" fill="url(#{u}s)" stroke="{TINTA}" stroke-width="4"/>',
        f'<rect x="-430" y="-62" width="860" height="5" fill="#8f8a7c" opacity=".7"/>',
    ]
    # ventanillas iluminadas
    rng = random.Random(7)
    vent = []
    for fila, (y0, x0, x1) in enumerate([(-20, -520, 560), (8, -500, 560), (-88, -400, 395), (-130, -350, 330)]):
        x = x0
        while x < x1:
            on = luces and rng.random() < .8
            vent.append(f'<circle cx="{x}" cy="{y0}" r="5" fill="{"#ffd77a" if on else "#2b2f38"}"/>')
            x += 22
    cuerpo.append(f'<g id="{u}v">{"".join(vent)}</g>')
    # chimeneas
    for k, cx in enumerate([-250, -90, 70, 230]):
        cuerpo.append(f'<g transform="translate({cx} -150) skewX(-12)"><rect x="-34" y="-210" width="68" height="210" rx="6" fill="url(#{u}f)" stroke="{TINTA}" stroke-width="4"/>'
                      f'<rect x="-34" y="-210" width="68" height="44" rx="6" fill="{TINTA}"/></g>')
    # mástiles y cables
    cuerpo.append(f'<line x1="-470" y1="-40" x2="-500" y2="-430" stroke="{TINTA}" stroke-width="6"/><line x1="480" y1="-40" x2="510" y2="-430" stroke="{TINTA}" stroke-width="6"/>'
                  f'<path d="M-500,-430 L510,-430" stroke="{TINTA}" stroke-width="2" opacity=".6"/>')
    if hospital:
        cuerpo.append(f'<g transform="translate(330 -10)"><rect x="-26" y="-8" width="52" height="16" fill="#c41e1e"/><rect x="-8" y="-26" width="16" height="52" fill="#c41e1e"/></g>')
    # humo suave (puffs con borde difuso)
    defs_h = f'<defs>{rad([(0, "#c3c7cf", .55), (.6, "#9aa0aa", .25), (1, "#9aa0aa", 0)], u + "hm")}</defs>'
    humo = defs_h + "".join(f'<circle id="{u}h{k}" cx="{[-250, -90, 70, 230][k % 4] - 40}" cy="-372" r="{46 + (k // 4) * 18}" fill="url(#{u}hm)"/>'
                            for k in range(12))
    for k in range(12):
        anim(t, f"#{u}h{k}", "{x: 0, y: 0, scale: 0.5, opacity: 0.9}",
             f"{{x: {-190 - k * 14}, y: {-90 - (k // 4) * 70}, scale: 2.2, opacity: 0, duration: 2.4, repeat: {int(t.dur / 2.4) + 1}, ease: 'power1.out'}}",
             (k % 6) * 0.4)
    if luces:
        humo = f'<defs>{rad([(0, "#ffd77a", .35), (1, "#ffd77a", 0)], u + "gl")}</defs><ellipse cx="0" cy="-20" rx="700" ry="120" fill="url(#{u}gl)" style="mix-blend-mode:screen"/>' + humo
    inner = humo + "".join(cuerpo)
    mov = p.get("mov", "avanza")
    if mov == "avanza":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 120)}'")
    if mov in ("avanza", "flota"):
        vaiven(t, f"#{u}in", "rotation: 0.6, y: 6", periodo=2.4)
    if mov == "hundir":
        anim(t, f"#{u}in", "{rotation: 0, y: 0}", f"{{rotation: -14, y: 260, duration: {t.dur:.2f}, ease: 'power1.in'}}")
    if luces and p.get("apagar_en") is not None:
        t.js.append(f'tl.to("#{u}v", {{opacity: 0.1, duration: 0.15, repeat: 3, yoyo: true}}, {t.at(p["apagar_en"])});')
        t.js.append(f'tl.to("#{u}v", {{opacity: 0.05, duration: 0.2}}, {t.at(p["apagar_en"] + 0.65)});')
    return g(p, f'<g id="{u}in">{inner}</g>', u)


@dib("iceberg")
def iceberg(p, u, t):
    defs = f'<defs>{lin("#ffffff", "#bfe3f5", u + "a", 0)}{lin("#9cc9e6", "#5d90b8", u + "b")}{lin("#7fb2d6", "#1d4466", u + "c")}</defs>'
    cara_luz = "M-260,0 L-170,-260 L-60,-420 L40,-300 L-20,-120 L-90,0 Z"
    cara_som = "M-90,0 L-20,-120 L40,-300 L-60,-420 L80,-470 L190,-250 L270,0 Z"
    bajo = "M-320,0 L330,0 L260,180 L60,300 L-180,240 L-300,120 Z"
    s = (f'{defs}<path d="{bajo}" fill="url(#{u}c)" opacity=".55"/>'
         f'<path d="{cara_som}" fill="url(#{u}b)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
         f'<path d="{cara_luz}" fill="url(#{u}a)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
         f'<path d="M-60,-420 L-30,-330 L40,-300 M-170,-260 L-120,-180 L-20,-120" stroke="#ffffff" stroke-width="4" fill="none" opacity=".8"/>')
    vaiven(t, f"#{u}", "y: '+=8'", periodo=3.0)
    return g(p, s, u)


@dib("bote")
def bote(p, u, t):
    col = p.get("color", "#f3efe4")
    gente = p.get("gente", 5)
    figs = "".join(f'<g transform="translate({-90 + k * 45} -40)"><circle cx="0" cy="-34" r="14" fill="{TINTA}"/><path d="M-16,0 Q0,-30 16,0 Z" fill="{TINTA}"/></g>' for k in range(gente))
    s = (f'{figs}<path d="M-150,-40 L150,-40 Q140,10 90,22 L-100,22 Q-140,10 -150,-40 Z" fill="{col}" stroke="{TINTA}" stroke-width="5"/>'
         f'<path d="M-146,-28 L146,-28" stroke="#c0392b" stroke-width="6"/>')
    vaiven(t, f"#{u}", "rotation: 3, y: '+=6'", periodo=2.0)
    return g(p, s, u)


# ============================================================================ personas (siluetas con volumen)
ROPA = {
    "traje": ("#2a3142", "#1b202c"), "uniforme": ("#3a4a2c", "#273320"), "blanco": ("#e9e6dc", "#bdb8aa"),
    "enfermera": ("#ffffff", "#d8d8d8"), "camarera": ("#1f1f26", "#141418"), "vestido": ("#6b2d3f", "#4a1d2b"),
    "obrero": ("#5a4632", "#3b2d20"), "bata": ("#f4f4f4", "#cfcfcf"), "romano": ("#b83a2e", "#7d2018"),
    "rojo": ("#b3261e", "#7a1813"), "azul": ("#2f5d9e", "#1e3e6b"), "gris": ("#6d7480", "#4b515a"),
}


@dib("persona")
def persona(p, u, t):
    """Personaje con volumen: cara con ojos, cejas, nariz y mejillas; manos, zapatos, ropa con sombreado y borde de luz.
    ropa (ver ROPA), falda, pelo, pelo_largo, calvo, bigote, barba, sombrero (gorra, copa, fedora, cofia, casco_ww),
    expresion (normal, serio, sorpresa, triste, enojado), mov (camina, saluda, respira, desvanece)."""
    ropa = ROPA.get(p.get("ropa", "traje"), ROPA["traje"])
    piel = p.get("piel", "#e8b98f")
    piel_s = "#c98f66"
    pelo = p.get("pelo", "#3a2a1e")
    som = p.get("sombrero")
    expr = p.get("expresion", "normal")
    falda = p.get("falda", False)
    pantalon = p.get("pantalon", "#2a2f3d" if not falda else piel)
    d = (f'<defs>{lin(ropa[0], ropa[1], u + "r", 0)}{lin(piel, piel_s, u + "p", 0)}'
         f'{rad([(0, "#ff9a9a", .55), (1, "#ff9a9a", 0)], u + "mj")}</defs>')
    sombra = '<ellipse cx="0" cy="2" rx="95" ry="16" fill="#000" opacity=".28"/>'
    # piernas y zapatos
    if falda:
        piernas = (f'<path d="M-30,-60 L-34,-10 L-18,-10 L-14,-60 Z M14,-60 L18,-10 L34,-10 L30,-60 Z" fill="{piel}" stroke="{TINTA}" stroke-width="4"/>'
                   f'<path d="M-46,-12 Q-46,4 -12,4 L-12,-14 Z M12,-14 L12,4 Q46,4 46,-12 Z" fill="#2a1d14" stroke="{TINTA}" stroke-width="4"/>')
        cuerpo = (f'<path d="M-50,-262 Q0,-284 50,-262 L58,-170 L96,-58 Q0,-40 -96,-58 L-58,-170 Z" fill="url(#{u}r)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
                  f'<path d="M-56,-180 Q0,-168 56,-180" stroke="{ropa[1]}" stroke-width="10" fill="none"/>'
                  f'<path d="M-44,-250 Q-50,-160 -84,-70" stroke="#fff" stroke-opacity=".22" stroke-width="7" fill="none"/>')
    else:
        piernas = (f'<path d="M-40,-140 L-38,-14 L-8,-14 L-4,-120 L4,-120 L8,-14 L38,-14 L40,-140 Z" fill="{pantalon}" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
                   f'<path d="M-46,-16 Q-48,4 -6,4 L-6,-18 Z M6,-18 L6,4 Q48,4 46,-16 Z" fill="#1d1510" stroke="{TINTA}" stroke-width="4"/>')
        cuerpo = (f'<path d="M-52,-262 Q0,-286 52,-262 L60,-176 L54,-128 L-54,-128 L-60,-176 Z" fill="url(#{u}r)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
                  f'<path d="M-18,-268 L0,-226 L18,-268" fill="#f4f1ea" stroke="{TINTA}" stroke-width="3"/>'
                  + (f'<path d="M-4,-232 L4,-232 L8,-176 L0,-164 L-8,-176 Z" fill="{p.get("corbata", "#8a1d1d")}" stroke="{TINTA}" stroke-width="2.5"/>'
                     if p.get("ropa", "traje") in ("traje", "gris") else "")
                  + f'<path d="M-18,-268 L-30,-200 L-6,-186" fill="none" stroke="{ropa[1]}" stroke-width="5"/><path d="M18,-268 L30,-200 L6,-186" fill="none" stroke="{ropa[1]}" stroke-width="5"/>'
                  f'<circle cx="0" cy="-160" r="4" fill="{TINTA}"/><circle cx="0" cy="-140" r="4" fill="{TINTA}"/>'
                  f'<path d="M-46,-252 Q-56,-200 -54,-136" stroke="#fff" stroke-opacity=".22" stroke-width="7" fill="none"/>')
    # brazos con manos
    brazos = (f'<g id="{u}bi"><path d="M-50,-256 Q-86,-200 -78,-128" stroke="{TINTA}" stroke-width="32" stroke-linecap="round" fill="none"/>'
              f'<path d="M-50,-256 Q-86,-200 -78,-128" stroke="{ropa[1]}" stroke-width="24" stroke-linecap="round" fill="none"/>'
              f'<circle cx="-78" cy="-118" r="15" fill="url(#{u}p)" stroke="{TINTA}" stroke-width="3.5"/></g>'
              f'<g id="{u}bd"><path d="M50,-256 Q86,-200 78,-128" stroke="{TINTA}" stroke-width="32" stroke-linecap="round" fill="none"/>'
              f'<path d="M50,-256 Q86,-200 78,-128" stroke="{ropa[0]}" stroke-width="24" stroke-linecap="round" fill="none"/>'
              f'<circle cx="78" cy="-118" r="15" fill="url(#{u}p)" stroke="{TINTA}" stroke-width="3.5"/></g>')
    # cabeza
    cejas = {"normal": ("M-30,-352 Q-18,-360 -6,-352", "M6,-352 Q18,-360 30,-352"),
             "serio": ("M-30,-350 L-6,-350", "M6,-350 L30,-350"),
             "sorpresa": ("M-30,-360 Q-18,-372 -6,-360", "M6,-360 Q18,-372 30,-360"),
             "triste": ("M-30,-348 Q-18,-358 -6,-358", "M6,-358 Q18,-358 30,-348"),
             "enojado": ("M-30,-358 L-6,-348", "M6,-348 L30,-358")}[expr]
    boca = {"normal": "M-12,-302 Q0,-294 12,-302", "serio": "M-11,-300 L11,-300", "sorpresa": None,
            "triste": "M-12,-296 Q0,-304 12,-296", "enojado": "M-12,-298 Q0,-304 12,-298"}[expr]
    cab = [f'<rect x="-13" y="-290" width="26" height="30" fill="{piel_s}"/>']
    if p.get("pelo_largo"):
        cab.append(f'<path d="M-46,-344 Q-54,-250 -34,-236 L34,-236 Q54,-250 46,-344 Z" fill="{pelo}" stroke="{TINTA}" stroke-width="4"/>')
    cab += [f'<ellipse cx="-42" cy="-328" rx="8" ry="13" fill="{piel_s}" stroke="{TINTA}" stroke-width="3.5"/>',
            f'<ellipse cx="42" cy="-328" rx="8" ry="13" fill="{piel_s}" stroke="{TINTA}" stroke-width="3.5"/>',
            f'<ellipse cx="0" cy="-330" rx="42" ry="48" fill="url(#{u}p)" stroke="{TINTA}" stroke-width="5"/>']
    if not p.get("calvo"):
        cab.append(f'<path d="M-43,-334 Q-44,-386 0,-384 Q44,-386 43,-334 Q36,-362 8,-362 Q-2,-350 -18,-360 Q-36,-362 -43,-334 Z" fill="{pelo}" stroke="{TINTA}" stroke-width="3.5"/>')
    cab += [f'<path d="{cejas[0]}" stroke="{pelo if pelo != "#ececec" else "#888"}" stroke-width="5" stroke-linecap="round" fill="none"/>',
            f'<path d="{cejas[1]}" stroke="{pelo if pelo != "#ececec" else "#888"}" stroke-width="5" stroke-linecap="round" fill="none"/>',
            f'<ellipse cx="-17" cy="-334" rx="8" ry="9" fill="#fff"/><ellipse cx="17" cy="-334" rx="8" ry="9" fill="#fff"/>',
            f'<circle cx="-16" cy="-333" r="5" fill="{TINTA}"/><circle cx="18" cy="-333" r="5" fill="{TINTA}"/>',
            f'<circle cx="-14" cy="-335" r="1.6" fill="#fff"/><circle cx="20" cy="-335" r="1.6" fill="#fff"/>',
            f'<path d="M0,-326 Q-7,-312 2,-310" stroke="{piel_s}" stroke-width="4" fill="none" stroke-linecap="round"/>',
            f'<circle cx="-26" cy="-312" r="10" fill="url(#{u}mj)"/><circle cx="26" cy="-312" r="10" fill="url(#{u}mj)"/>']
    cab.append(f'<path d="{boca}" stroke="{TINTA}" stroke-width="3.5" fill="none" stroke-linecap="round"/>' if boca else
               f'<ellipse cx="0" cy="-300" rx="7" ry="9" fill="#5a1d1d"/>')
    if p.get("bigote"):
        cab.append(f'<path d="M-20,-306 Q-10,-316 0,-308 Q10,-316 20,-306 Q10,-300 0,-304 Q-10,-300 -20,-306 Z" fill="{pelo}"/>')
    if p.get("barba"):
        cab.append(f'<path d="M-40,-322 Q-38,-272 0,-268 Q38,-272 40,-322 Q30,-292 0,-292 Q-30,-292 -40,-322 Z" fill="{pelo}" opacity=".95"/>')
    if som == "gorra":
        cab.append(f'<path d="M-44,-350 Q0,-398 44,-350 Z" fill="{p.get("color_sombrero", "#2a3142")}" stroke="{TINTA}" stroke-width="4"/><rect x="-6" y="-356" width="64" height="11" rx="5" fill="{TINTA}"/>')
    elif som == "copa":
        cab.append(f'<rect x="-34" y="-436" width="68" height="70" rx="4" fill="#15161c" stroke="#3a3d4a" stroke-width="3"/><rect x="-34" y="-386" width="68" height="10" fill="#6b2d3f"/><rect x="-58" y="-372" width="116" height="12" rx="6" fill="#15161c"/>')
    elif som == "fedora":
        cab.append(f'<path d="M-38,-362 Q-30,-410 0,-408 Q30,-410 38,-362 Z" fill="#4a3d2c" stroke="{TINTA}" stroke-width="3"/><rect x="-38" y="-374" width="76" height="9" fill="#2a2218"/><rect x="-64" y="-366" width="128" height="12" rx="6" fill="#4a3d2c" stroke="{TINTA}" stroke-width="3"/>')
    elif som == "cofia":
        cab.append(f'<path d="M-36,-366 L36,-366 L28,-390 L-28,-390 Z" fill="#ffffff" stroke="{TINTA}" stroke-width="3"/><rect x="-6" y="-388" width="12" height="16" fill="#c41e1e"/>')
    elif som == "casco_ww":
        cab.append(f'<path d="M-52,-338 Q0,-414 52,-338 Z" fill="#4b5a35" stroke="{TINTA}" stroke-width="4"/>')
    s = d + sombra + piernas + brazos + cuerpo + "".join(cab)
    mov = p.get("mov")
    if mov == "camina":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 160)}'")
        vaiven(t, f"#{u}in", "y: -8", periodo=0.5)
        vaiven(t, f"#{u}bi", "rotation: 14, transformOrigin: '50% 0%'", periodo=1.0)
        vaiven(t, f"#{u}bd", "rotation: -14, transformOrigin: '50% 0%'", periodo=1.0)
    elif mov == "saluda":
        vaiven(t, f"#{u}bd", "rotation: -70, transformOrigin: '0% 0%'", periodo=0.6)
    elif mov == "respira":
        vaiven(t, f"#{u}in", "scaleY: 1.015, transformOrigin: '50% 100%'", periodo=2.4)
    elif mov == "desvanece":
        anim(t, f"#{u}in", "{opacity: 1}", f"{{opacity: 0, y: -40, duration: 0.8, ease: 'power2.in'}}", p.get("desvanece_en", 1.0))
    return g(p, f'<g id="{u}in">{s}</g>', u)


@dib("baranda")
def baranda(p, u, t):
    """Baranda de cubierta de barco en primer plano (ancho completo)."""
    y = p.get("y", 1500)
    col = p.get("color", "#d9d2c3")
    postes = "".join(f'<rect x="{x}" y="{y - 160}" width="18" height="190" fill="{col}" stroke="{TINTA}" stroke-width="4"/>' for x in range(-40, 1120, 130))
    return (f'<rect x="-100" y="{y + 20}" width="1300" height="600" fill="#5a3a22"/>' + postes +
            f'<rect x="-100" y="{y - 170}" width="1300" height="22" rx="10" fill="{col}" stroke="{TINTA}" stroke-width="4"/>'
            f'<rect x="-100" y="{y - 80}" width="1300" height="12" fill="{col}" stroke="{TINTA}" stroke-width="3"/>')
