"""Objetos, símbolos y personajes especiales (SVG). Base: (0, 0) = centro abajo salvo que se indique."""
from __future__ import annotations

import math
import random

from ilustra import TINTA, anim, deriva, dib, g, lin, rad, vaiven

O = f'stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"'
O3 = f'stroke="{TINTA}" stroke-width="3.5" stroke-linejoin="round"'


# ============================================================================ fuego, humo, explosiones
@dib("fuego")
def fuego(p, u, t):
    """Llamas animadas. ancho = ancho total del incendio."""
    ancho = p.get("ancho", 500)
    n = max(3, int(ancho / 90))
    rng = random.Random(len(u))
    s = [f'<defs>{lin("#fff3a6", "#ff6a00", u + "a")}{lin("#ffb347", "#c1121f", u + "b")}'
         f'{rad([(0, "#ff9a3c", .55), (1, "#ff6a00", 0)], u + "g")}</defs>',
         f'<ellipse cx="0" cy="-120" rx="{ancho * .9:.0f}" ry="320" fill="url(#{u}g)" style="mix-blend-mode:screen"/>']
    for k in range(n):
        x = -ancho / 2 + k * ancho / (n - 1)
        h = rng.uniform(160, 300)
        w = rng.uniform(60, 100)
        s.append(f'<path id="{u}f{k}" d="M{x - w:.0f},0 Q{x - w * .9:.0f},{-h * .5:.0f} {x:.0f},{-h:.0f} Q{x + w * .9:.0f},{-h * .5:.0f} {x + w:.0f},0 Z" fill="url(#{u}b)"/>'
                 f'<path id="{u}g{k}" d="M{x - w * .5:.0f},0 Q{x - w * .45:.0f},{-h * .35:.0f} {x:.0f},{-h * .62:.0f} Q{x + w * .45:.0f},{-h * .35:.0f} {x + w * .5:.0f},0 Z" fill="url(#{u}a)"/>')
        vaiven(t, f"#{u}f{k}", f"scaleY: {rng.uniform(1.12, 1.3):.2f}, scaleX: 0.9, transformOrigin: '50% 100%'", periodo=rng.uniform(0.25, 0.45))
        vaiven(t, f"#{u}g{k}", f"scaleY: {rng.uniform(1.15, 1.35):.2f}, transformOrigin: '50% 100%'", periodo=rng.uniform(0.2, 0.35))
    return g(p, "".join(s), u)


@dib("explosion")
def explosion(p, u, t):
    """Destello + bola de fuego + onda expansiva."""
    s = (f'<defs>{rad([(0, "#ffffff", 1), (.3, "#fff3a6", .95), (.6, "#ff9a3c", .7), (1, "#c1121f", 0)], u + "b")}</defs>'
         f'<circle id="{u}o" cx="0" cy="0" r="200" fill="none" stroke="#fff" stroke-width="14" opacity=".8"/>'
         f'<circle id="{u}b" cx="0" cy="0" r="300" fill="url(#{u}b)"/>')
    anim(t, f"#{u}b", "{scale: 0.05, transformOrigin: '50% 50%'}", "{scale: 1.6, duration: 0.6, ease: 'power3.out'}", p.get("en", 0.1))
    anim(t, f"#{u}o", "{scale: 0.2, opacity: 1, transformOrigin: '50% 50%'}", "{scale: 4, opacity: 0, duration: 1.4, ease: 'power2.out'}", p.get("en", 0.1))
    return g(p, s, u)


@dib("hongo")
def hongo(p, u, t):
    """Hongo nuclear que crece desde el suelo."""
    s = (f'<defs>{rad([(0, "#fff3a6", 1), (.5, "#ff9a3c", .95), (1, "#7a2b12", .9)], u + "c", "50%", "60%", "60%")}'
         f'{lin("#ffcf7a", "#8a3b1a", u + "t")}</defs>'
         f'<g id="{u}tallo"><path d="M-70,0 Q-40,-300 -60,-560 L60,-560 Q40,-300 70,0 Z" fill="url(#{u}t)"/></g>'
         f'<g id="{u}cab"><ellipse cx="0" cy="-640" rx="330" ry="180" fill="url(#{u}c)"/>'
         f'<ellipse cx="-160" cy="-600" rx="150" ry="110" fill="url(#{u}c)"/><ellipse cx="170" cy="-600" rx="150" ry="110" fill="url(#{u}c)"/>'
         f'<ellipse cx="0" cy="-560" rx="380" ry="60" fill="#c9561e" opacity=".7"/></g>'
         f'<ellipse cx="0" cy="-10" rx="520" ry="70" fill="#d77a3a" opacity=".6"/>')
    anim(t, f"#{u}tallo", "{scaleY: 0.1, transformOrigin: '50% 100%'}", f"{{scaleY: 1, duration: {min(2.4, t.dur * .7):.2f}, ease: 'power2.out'}}")
    anim(t, f"#{u}cab", "{scale: 0.2, y: 520, transformOrigin: '50% 100%'}", f"{{scale: 1, y: 0, duration: {min(2.6, t.dur * .75):.2f}, ease: 'power2.out'}}")
    return g(p, s, u)


@dib("paracaidas")
def paracaidas(p, u, t):
    s = (f'<path d="M-260,-420 Q0,-640 260,-420 Q200,-450 130,-420 Q65,-460 0,-420 Q-65,-460 -130,-420 Q-200,-450 -260,-420 Z" fill="#f2efe8" {O}/>'
         + "".join(f'<line x1="{x}" y1="-420" x2="0" y2="-60" stroke="#ddd" stroke-width="3"/>' for x in (-260, -130, 0, 130, 260))
         + f'<rect x="-50" y="-60" width="100" height="160" rx="40" fill="#5a6270" {O}/>')
    anim(t, f"#{u}", "{y: -300}", f"{{y: 200, duration: {t.dur:.2f}, ease: 'none'}}")
    vaiven(t, f"#{u}", "rotation: 4", periodo=1.6)
    return g(p, s, u)


# ============================================================================ pantallas, aparatos
@dib("pantalla")
def pantalla(p, u, t):
    """Monitor o consola. texto en la pantalla; alarma=True parpadea en rojo; tipo: crt | sala (pared de pantallas)."""
    texto = p.get("texto", "")
    col = p.get("color", "#ff2a2a" if p.get("alarma") else "#5cff7a")
    w, h = p.get("w", 520), p.get("h", 380)
    s = (f'<defs>{lin("#3a3f4a", "#15181e", u + "m")}{rad([(0, col, .35), (1, col, 0)], u + "g")}</defs>'
         f'<rect x="{-w / 2 - 40}" y="{-h - 80}" width="{w + 80}" height="{h + 80}" rx="30" fill="url(#{u}m)" {O}/>'
         f'<rect x="{-w / 2}" y="{-h - 40}" width="{w}" height="{h}" rx="18" fill="#05110a"/>'
         f'<ellipse cx="0" cy="{-h / 2 - 40}" rx="{w * .7:.0f}" ry="{h * .7:.0f}" fill="url(#{u}g)"/>'
         + "".join(f'<rect x="{-w / 2}" y="{-h - 40 + k * 8}" width="{w}" height="2" fill="#000" opacity=".25"/>' for k in range(int(h / 8)))
         + f'<text id="{u}tx" x="0" y="{-h / 2 - 20}" text-anchor="middle" font-family="Anton" font-size="{p.get("tam", 96)}" fill="{col}">{texto}</text>')
    if p.get("alarma"):
        vaiven(t, f"#{u}tx", "opacity: 0.15", periodo=0.5)
    return g(p, s, u)


@dib("radio")
def radio(p, u, t):
    """Radio de mesa de los años 30 (capilla de madera) con ondas saliendo."""
    s = (f'<defs>{lin("#a8693a", "#4e2c15", u + "m", 0)}{lin("#e9c88f", "#a8845a", u + "t")}</defs>'
         f'<path d="M-200,0 V-260 Q-200,-460 0,-460 Q200,-460 200,-260 V0 Z" fill="url(#{u}m)" {O}/>'
         f'<path d="M-140,-120 V-260 Q-140,-390 0,-390 Q140,-390 140,-260 V-120 Z" fill="url(#{u}t)" {O3}/>'
         + "".join(f'<line x1="{x}" x2="{x}" y1="-380" y2="-125" stroke="#5a3a1e" stroke-width="7"/>' for x in range(-110, 120, 36))
         + f'<circle cx="-80" cy="-60" r="26" fill="#2a1a10" {O3}/><circle cx="80" cy="-60" r="26" fill="#2a1a10" {O3}/>'
         f'<rect x="-40" y="-80" width="80" height="34" rx="6" fill="#ffd77a" {O3}/>'
         + "".join(f'<path id="{u}o{k}" d="M220,{-330 + 0} q40,90 0,180" fill="none" stroke="#ffd77a" stroke-width="8" stroke-linecap="round"/>' for k in range(3)))
    for k in range(3):
        anim(t, f"#{u}o{k}", "{x: 0, opacity: 1}", f"{{x: 160, opacity: 0, duration: 1.2, repeat: {int(t.dur / 1.2)}, ease: 'none'}}", k * 0.4)
    return g(p, s, u)


@dib("microfono")
def microfono(p, u, t):
    s = (f'<defs>{lin("#e8ecf1", "#7d838c", u + "m", 0)}</defs><rect x="-12" y="-420" width="24" height="420" fill="#555" {O3}/>'
         f'<rect x="-120" y="-20" width="240" height="20" rx="10" fill="#444" {O3}/>'
         f'<rect x="-80" y="-640" width="160" height="230" rx="80" fill="url(#{u}m)" {O}/>'
         + "".join(f'<line x1="-70" x2="70" y1="{-600 + k * 26}" y2="{-600 + k * 26}" stroke="#555" stroke-width="4"/>' for k in range(7)))
    return g(p, s, u)


@dib("computadora")
def computadora(p, u, t):
    """PC de los 2000 con código verde que corre (hacker)."""
    rng = random.Random(2)
    lineas = "".join(f'<rect x="{-230 + rng.randint(0, 3) * 20}" y="{-560 + k * 26}" width="{rng.randint(80, 360)}" height="12" fill="#5cff7a" opacity=".85"/>' for k in range(16))
    s = (f'<rect x="-280" y="-620" width="560" height="420" rx="26" fill="#c9c4b5" {O}/><rect x="-240" y="-585" width="480" height="345" rx="12" fill="#04140a"/>'
         f'<g clip-path="inset(0)"><g id="{u}c">{lineas}</g></g>'
         f'<rect x="-60" y="-200" width="120" height="70" fill="#b5b0a2" {O3}/><rect x="-300" y="-130" width="600" height="60" rx="10" fill="#d8d3c4" {O}/>')
    anim(t, f"#{u}c", "{y: 0}", f"{{y: -160, duration: {t.dur:.2f}, ease: 'none'}}")
    return g(p, s, u)


@dib("arcade")
def arcade(p, u, t):
    """Máquina arcade genérica (sin marcas): pantalla con laberinto y puntitos."""
    col = p.get("color", "#2b59ff")
    texto = p.get("texto", "")
    s = (f'<defs>{lin(col, "#0d1a4a", u + "m", 0)}</defs>'
         f'<path d="M-200,0 V-700 L-170,-900 H170 L200,-700 V0 Z" fill="url(#{u}m)" {O}/>'
         f'<rect x="-160" y="-880" width="320" height="90" fill="#ffd21f" {O3}/>'
         f'<text x="0" y="-818" text-anchor="middle" font-family="Anton" font-size="62" fill="#111">{texto}</text>'
         f'<rect x="-150" y="-760" width="300" height="250" rx="10" fill="#050510" {O3}/>'
         + "".join(f'<rect x="{-130 + (k % 6) * 46}" y="{-740 + (k // 6) * 46}" width="30" height="6" fill="#2b59ff"/>' for k in range(30))
         + "".join(f'<circle cx="{-120 + k * 30}" cy="-560" r="5" fill="#ffd9a0"/>' for k in range(9))
         + f'<rect x="-190" y="-480" width="380" height="90" fill="#1a1a2a" {O3}/><circle cx="-80" cy="-440" r="18" fill="#e3141b"/><circle cx="60" cy="-440" r="16" fill="#ffd21f"/><circle cx="110" cy="-440" r="16" fill="#58c46a"/>')
    return g(p, s, u)


@dib("mando")
def mando(p, u, t):
    """Control de consola genérico (cruceta + botones B y A). Las flechas se iluminan en secuencia si secuencia=True."""
    s = [f'<defs>{lin("#d9d9d9", "#9a9a9a", u + "m")}</defs>',
         f'<rect x="-330" y="-240" width="660" height="240" rx="40" fill="url(#{u}m)" {O}/>',
         f'<rect x="-250" y="-160" width="140" height="44" fill="#222"/><rect x="-202" y="-208" width="44" height="140" fill="#222"/>',
         f'<circle id="{u}B" cx="150" cy="-110" r="34" fill="#b3261e" {O3}/><circle id="{u}A" cx="240" cy="-130" r="34" fill="#b3261e" {O3}/>',
         f'<text x="150" y="-50" text-anchor="middle" font-family="Anton" font-size="34" fill="#333">B</text>',
         f'<text x="240" y="-70" text-anchor="middle" font-family="Anton" font-size="34" fill="#333">A</text>',
         f'<polygon id="{u}up" points="-180,-205 -194,-180 -166,-180" fill="#ffd21f" opacity="0"/>',
         f'<polygon id="{u}dn" points="-180,-71 -194,-96 -166,-96" fill="#ffd21f" opacity="0"/>',
         f'<polygon id="{u}lf" points="-246,-138 -222,-152 -222,-124" fill="#ffd21f" opacity="0"/>',
         f'<polygon id="{u}rt" points="-114,-138 -138,-152 -138,-124" fill="#ffd21f" opacity="0"/>']
    if p.get("secuencia"):
        orden = ["up", "up", "dn", "dn", "lf", "rt", "lf", "rt", "B", "A"]
        paso = min(0.32, max(0.15, (t.dur - 0.6) / 10))
        for k, b in enumerate(orden):
            sel = f"#{u}{b}"
            prop = "opacity: 1" if b not in ("A", "B") else "fill: '#ffd21f'"
            back = "opacity: 0" if b not in ("A", "B") else "fill: '#b3261e'"
            t.js.append(f'tl.to("{sel}", {{{prop}, duration: 0.04}}, {t.at(0.3 + k * paso)}); tl.to("{sel}", {{{back}, duration: 0.08}}, {t.at(0.3 + k * paso + paso * .7)});')
    return g(p, "".join(s), u)


@dib("cartucho")
def cartucho(p, u, t):
    """Cartucho de consola de los 80 (genérico, etiqueta sin marca)."""
    col = p.get("color", "#3a3a3a")
    s = (f'<path d="M-130,0 V-300 L-100,-330 H100 L130,-300 V0 Z" fill="{col}" {O}/>'
         f'<rect x="-100" y="-290" width="200" height="200" rx="10" fill="{p.get("etiqueta", "#d97b2b")}" {O3}/>'
         f'<circle cx="0" cy="-190" r="56" fill="#6b4a2e"/><rect x="-80" y="-40" width="160" height="20" fill="#222"/>')
    return g(p, s, u)


@dib("bloques")
def bloques(p, u, t):
    """Cubos de colores apilándose (construcción con bloques)."""
    cols = [("#6fbf4a", "#4e8f33", "#3a6b26"), ("#8a5a2f", "#6b4423", "#4e321a"), ("#9aa0a6", "#767b80", "#55595d")]
    s, k = [], 0
    for fila in range(p.get("filas", 4)):
        for col in range(5 - fila % 2):
            x, y = -320 + col * 140 + (fila % 2) * 70, -fila * 120
            c = cols[(fila + col) % 3]
            s.append(f'<g id="{u}b{k}"><polygon points="{x},{y - 100} {x + 70},{y - 140} {x + 140},{y - 100} {x + 70},{y - 60}" fill="{c[0]}" {O3}/>'
                     f'<polygon points="{x},{y - 100} {x + 70},{y - 60} {x + 70},{y + 20} {x},{y - 20}" fill="{c[1]}" {O3}/>'
                     f'<polygon points="{x + 140},{y - 100} {x + 70},{y - 60} {x + 70},{y + 20} {x + 140},{y - 20}" fill="{c[2]}" {O3}/></g>')
            anim(t, f"#{u}b{k}", "{y: -700, opacity: 0}", "{y: 0, opacity: 1, duration: 0.3, ease: 'bounce.out'}", 0.1 + k * 0.09)
            k += 1
    return g(p, "".join(s), u)


@dib("pizza")
def pizza(p, u, t):
    """Pizza vista desde arriba a la que le falta un trozo."""
    s = (f'<defs>{rad([(0, "#ffd36b", 1), (.85, "#f0a93a", 1), (1, "#c9772a", 1)], u + "q")}</defs>'
         f'<path d="M0,-300 L260,-150 A300,300 0 1,1 260,-450 Z" transform="translate(0 0)" fill="url(#{u}q)" {O}/>'
         + "".join(f'<circle cx="{x}" cy="{y}" r="28" fill="#c0392b"/>' for x, y in [(-120, -380), (-160, -220), (20, -470), (-40, -150), (-200, -320), (60, -260)]))
    return g(p, s, u)


# ============================================================================ objetos de época
@dib("frasco")
def frasco(p, u, t):
    """Frasco de vidrio con contenido (cerebro, píldoras, líquido)."""
    cont = p.get("contenido", "cerebro")
    s = [f'<defs>{lin("#e9f3f6", "#9fc1cc", u + "v", 0)}</defs>',
         f'<rect x="-120" y="-330" width="240" height="330" rx="30" fill="url(#{u}v)" opacity=".45" {O}/>',
         f'<rect x="-100" y="-370" width="200" height="50" rx="12" fill="#7a6a55" {O3}/>']
    if cont == "cerebro":
        s.append(f'<path d="M-90,-80 Q-110,-200 -40,-230 Q0,-260 50,-230 Q110,-200 90,-90 Q60,-40 0,-50 Q-60,-40 -90,-80 Z" fill="#e8a6a0" {O3}/>'
                 f'<path d="M-60,-180 Q-20,-150 -40,-110 M10,-210 Q40,-170 10,-130 M50,-160 Q70,-120 40,-90" stroke="#b56d68" stroke-width="5" fill="none"/>')
        s.append(f'<rect x="-116" y="-250" width="232" height="246" rx="26" fill="#d7c766" opacity=".25"/>')
    elif cont == "liquido":
        s.append(f'<rect x="-116" y="-180" width="232" height="176" rx="26" fill="{p.get("color_liquido", "#5cff7a")}" opacity=".55"/>')
    elif cont == "pildoras":
        s.append("".join(f'<ellipse cx="{-70 + (k % 5) * 35}" cy="{-30 - (k // 5) * 26}" rx="18" ry="11" fill="#c0392b" {O3}/>' for k in range(20)))
    if p.get("etiqueta"):
        s.append(f'<rect x="-90" y="-250" width="180" height="90" fill="#f4efe4" {O3}/><text x="0" y="-195" text-anchor="middle" font-family="Anton" font-size="38" fill="#222">{p["etiqueta"]}</text>')
    s.append('<rect x="-90" y="-310" width="26" height="260" rx="13" fill="#fff" opacity=".35"/>')
    return g(p, "".join(s), u)


@dib("botella")
def botella(p, u, t):
    """Botella de vidrio antigua (farmacia / refresco de 1886, sin marca)."""
    col = p.get("color", "#4a2a14")
    s = (f'<defs>{lin("#ffffff", col, u + "v", 0)}</defs>'
         f'<path d="M-30,-460 H30 V-380 Q90,-330 90,-240 V-20 Q90,0 60,0 H-60 Q-90,0 -90,-20 V-240 Q-90,-330 -30,-380 Z" fill="{col}" {O}/>'
         f'<rect x="-36" y="-490" width="72" height="34" rx="8" fill="#b3261e" {O3}/>'
         f'<rect x="-90" y="-230" width="180" height="120" fill="#f4efe4" {O3}/>'
         f'<text x="0" y="-180" text-anchor="middle" font-family="Anton" font-size="32" fill="#7a1813">{p.get("texto", "TÓNICO")}</text>'
         f'<text x="0" y="-135" text-anchor="middle" font-family="Anton" font-size="24" fill="#333">{p.get("sub", "1886")}</text>'
         f'<rect x="-70" y="-360" width="20" height="320" rx="10" fill="#fff" opacity=".3"/>')
    return g(p, s, u)


@dib("tomate")
def tomate(p, u, t):
    s = (f'<defs>{rad([(0, "#ff7a5c", 1), (.7, "#d62d20", 1), (1, "#8f1a12", 1)], u + "t", "38%", "35%", "70%")}</defs>'
         f'<ellipse cx="0" cy="-130" rx="150" ry="130" fill="url(#{u}t)" {O}/>'
         f'<path d="M0,-250 L-50,-280 L-20,-245 L-70,-230 L-15,-232 L0,-200 L15,-232 L70,-230 L20,-245 L50,-280 Z" fill="#3f8f3a" {O3}/>'
         f'<ellipse cx="-60" cy="-180" rx="30" ry="18" fill="#fff" opacity=".35"/>')
    return g(p, s, u)


@dib("cacao")
def cacao(p, u, t):
    """Vaina de cacao abierta con semillas + taza de chocolate espumoso opcional."""
    s = (f'<defs>{lin("#d9822b", "#7a3e12", u + "v", 0)}</defs>'
         f'<path d="M-260,-120 Q-200,-260 0,-260 Q200,-260 260,-120 Q200,10 0,10 Q-200,10 -260,-120 Z" fill="url(#{u}v)" {O}/>'
         f'<path d="M-200,-120 Q-150,-200 0,-200 Q150,-200 200,-120 Q150,-50 0,-50 Q-150,-50 -200,-120 Z" fill="#f2e6cf" {O3}/>'
         + "".join(f'<ellipse cx="{-140 + k * 40}" cy="{-120 + (k % 2) * 30 - 15}" rx="22" ry="15" fill="#6b3a1e" {O3}/>' for k in range(8)))
    return g(p, s, u)


@dib("semillas")
def semillas(p, u, t):
    """Montón de semillas de cacao (monedas)."""
    rng = random.Random(4)
    s = "".join(f'<ellipse id="{u}s{k}" cx="{rng.uniform(-200, 200):.0f}" cy="{-rng.uniform(0, 140) * (1 - abs(k - 20) / 40):.0f}" rx="30" ry="20" fill="#6b3a1e" {O3} transform="rotate({rng.uniform(-40, 40):.0f})"/>' for k in range(40))
    for k in range(40):
        anim(t, f"#{u}s{k}", "{y: -500, opacity: 0}", "{y: 0, opacity: 1, duration: 0.35, ease: 'bounce.out'}", 0.1 + k * 0.03)
    return g(p, s, u)


@dib("taza")
def taza(p, u, t):
    """Vaso/jarra de barro con bebida espumosa y vapor."""
    s = (f'<defs>{lin("#b5653a", "#6b3014", u + "b", 0)}</defs>'
         f'<path d="M-140,-300 L140,-300 L110,0 L-110,0 Z" fill="url(#{u}b)" {O}/>'
         f'<ellipse cx="0" cy="-300" rx="140" ry="30" fill="#5a2a12" {O3}/>'
         f'<path d="M-130,-310 Q-90,-360 -40,-320 Q0,-370 40,-322 Q90,-360 130,-310 Z" fill="#c69466" {O3}/>'
         + "".join(f'<path id="{u}v{k}" d="M{-60 + k * 60},-360 q-25,-50 0,-100 q25,-50 0,-100" fill="none" stroke="#fff" stroke-width="8" opacity=".5" stroke-linecap="round"/>' for k in range(3)))
    for k in range(3):
        anim(t, f"#{u}v{k}", "{y: 0, opacity: 0.6}", f"{{y: -80, opacity: 0, duration: 1.4, repeat: {int(t.dur / 1.4)}, ease: 'none'}}", k * 0.45)
    return g(p, s, u)


@dib("libro")
def libro(p, u, t):
    """Cuaderno abierto con fórmulas manuscritas. radiactivo=True brilla verde."""
    s = [f'<path d="M-330,-20 L0,0 L330,-20 L330,-340 L0,-320 L-330,-340 Z" fill="#f4ecd8" {O}/>',
         f'<line x1="0" y1="0" x2="0" y2="-320" stroke="{TINTA}" stroke-width="4"/>']
    rng = random.Random(6)
    for lado in (-1, 1):
        for k in range(9):
            y = -300 + k * 30
            x0 = 30 if lado > 0 else -300
            s.append(f'<path d="M{x0},{y} q20,-12 40,0 t40,0 t40,0 t40,0 t40,0 t{rng.randint(10, 60)},0" stroke="#4a3a2a" stroke-width="3" fill="none"/>')
    if p.get("radiactivo"):
        s.insert(0, f'<defs>{rad([(0, "#8dff9c", .6), (1, "#8dff9c", 0)], u + "g")}</defs><ellipse id="{u}g" cx="0" cy="-170" rx="520" ry="360" fill="url(#{u}g)"/>')
        vaiven(t, f"#{u}g", "opacity: 0.4", periodo=1.2)
    return g(p, "".join(s), u)


@dib("caja")
def caja(p, u, t):
    """Caja de madera (embalaje) o caja forrada de plomo (gris)."""
    plomo = p.get("plomo", False)
    c1, c2 = ("#9aa0a6", "#5c6268") if plomo else ("#c99a5e", "#8a6338")
    s = (f'<defs>{lin(c1, c2, u + "c", 0)}</defs><rect x="-200" y="-260" width="400" height="260" fill="url(#{u}c)" {O}/>'
         + ("".join(f'<line x1="-200" x2="200" y1="{-260 + k * 65}" y2="{-260 + k * 65}" stroke="{c2}" stroke-width="5"/>' for k in range(1, 4)) if not plomo else
            f'<polygon points="0,-200 -30,-150 30,-150" fill="#ffd21f" {O3}/><circle cx="0" cy="-130" r="40" fill="none" stroke="#ffd21f" stroke-width="10"/>')
         + (f'<text x="0" y="-110" text-anchor="middle" font-family="Anton" font-size="52" fill="#3a2414">{p["texto"]}</text>' if p.get("texto") else ""))
    if p.get("cae"):
        anim(t, f"#{u}", "{y: -800}", "{y: 0, duration: 0.5, ease: 'bounce.out'}", p.get("cae_en", 0.1))
    return g(p, s, u)


@dib("carta")
def carta(p, u, t):
    """Carta manuscrita que se despliega. texto: primera línea visible."""
    s = (f'<rect x="-280" y="-760" width="560" height="760" fill="#f4efe4" {O}/>'
         f'<text x="-230" y="-680" font-family="Anton" font-size="44" fill="#3a2a1e">{p.get("texto", "")}</text>'
         + "".join(f'<path d="M-230,{-600 + k * 44} q30,-14 60,0 t60,0 t60,0 t60,0 t60,0 t60,0 t40,0" stroke="#3a2a1e" stroke-width="3.5" fill="none" opacity=".75"/>' for k in range(12))
         + f'<text x="230" y="-40" text-anchor="end" font-family="Anton" font-size="40" fill="#7a1813">{p.get("firma", "")}</text>')
    anim(t, f"#{u}", "{scaleY: 0.05, opacity: 0, transformOrigin: '50% 0%'}", "{scaleY: 1, opacity: 1, duration: 0.45, ease: 'power3.out'}", 0.1)
    return g(p, s, u)


@dib("periodico")
def periodico(p, u, t):
    titular = p.get("titular", "EXTRA")
    s = (f'<rect x="-330" y="-860" width="660" height="860" fill="#efe9da" {O}/>'
         f'<text x="0" y="-780" text-anchor="middle" font-family="Anton" font-size="56" fill="#222">{p.get("cabecera", "EL DIARIO")}</text>'
         f'<line x1="-300" x2="300" y1="-760" y2="-760" stroke="#222" stroke-width="4"/>'
         f'<text x="0" y="-650" text-anchor="middle" font-family="Anton" font-size="{p.get("tam", 92)}" fill="#111">{titular}</text>'
         f'<rect x="-300" y="-600" width="290" height="230" fill="#b9b2a2"/>'
         + "".join(f'<rect x="{10 if k < 8 else -300}" y="{-600 + (k % 8) * 30 + (0 if k < 8 else 250)}" width="{290 if k < 8 else 600}" height="12" fill="#9a9384"/>' for k in range(14)))
    anim(t, f"#{u}", "{rotation: -540, scale: 0.1, transformOrigin: '50% 50%'}", "{rotation: -4, scale: 1, duration: 0.7, ease: 'power3.out'}", 0.05)
    return g(p, s, u)


@dib("cartel")
def cartel(p, u, t):
    """Afiche de circo / anuncio antiguo con dibujo y texto."""
    s = (f'<rect x="-300" y="-820" width="600" height="820" fill="#f3e2b8" {O}/><rect x="-270" y="-790" width="540" height="760" fill="none" stroke="#b3261e" stroke-width="10"/>'
         f'<text x="0" y="-700" text-anchor="middle" font-family="Anton" font-size="78" fill="#b3261e">{p.get("titulo", "¡VEA!")}</text>'
         f'<text x="0" y="-80" text-anchor="middle" font-family="Anton" font-size="56" fill="#222">{p.get("sub", "")}</text>')
    if p.get("sirena"):
        s += (f'<circle cx="-30" cy="-520" r="60" fill="#f1c9a5" {O3}/><path d="M-90,-540 Q-120,-380 -60,-300" stroke="#c8782a" stroke-width="30" fill="none"/>'
              f'<path d="M-80,-460 Q-30,-480 20,-460 L10,-340 Q60,-260 140,-250 Q90,-200 0,-250 Q-70,-300 -80,-460 Z" fill="#2fa58a" {O3}/>')
    return g(p, s, u)


@dib("vitrina")
def vitrina(p, u, t):
    """Vitrina de museo con un objeto adentro (muñeco, sirena) y luz cenital."""
    s = (f'<defs>{lin("#e9f3f6", "#9fc1cc", u + "v", 0)}{rad([(0, "#fff2c4", .5), (1, "#fff2c4", 0)], u + "l")}</defs>'
         f'<rect x="-260" y="-200" width="520" height="200" fill="#4a3020" {O}/>'
         f'<ellipse cx="0" cy="-500" rx="300" ry="320" fill="url(#{u}l)"/>'
         f'<rect x="-240" y="-760" width="480" height="560" fill="url(#{u}v)" opacity=".18" {O}/>'
         f'<rect x="-220" y="-740" width="30" height="520" fill="#fff" opacity=".25"/>')
    return g(p, s, u)


@dib("muneco")
def muneco(p, u, t):
    """Muñeco antiguo de paja con traje de marinero (Robert) sentado."""
    s = (f'<path d="M-90,0 L-110,-180 Q-100,-260 0,-270 Q100,-260 110,-180 L90,0 Z" fill="#f2f2ee" {O}/>'
         f'<path d="M-100,-250 L0,-180 L100,-250 L80,-280 L-80,-280 Z" fill="#2b4a8a" {O3}/>'
         f'<circle cx="0" cy="-340" r="80" fill="#d8b98f" {O}/>'
         f'<path d="M-80,-370 Q0,-470 80,-370 Q60,-420 0,-425 Q-60,-420 -80,-370 Z" fill="#f2f2ee" {O3}/>'
         f'<circle cx="-28" cy="-345" r="9" fill="#111"/><circle cx="28" cy="-345" r="9" fill="#111"/>'
         f'<path d="M-24,-305 Q0,-292 24,-305" stroke="#5a2a1e" stroke-width="5" fill="none"/>'
         f'<path d="M-110,-200 L-140,-60" stroke="#f2f2ee" stroke-width="36" stroke-linecap="round"/><path d="M110,-200 L140,-60" stroke="#f2f2ee" stroke-width="36" stroke-linecap="round"/>'
         f'<circle cx="-140" cy="-50" r="20" fill="#d8b98f" {O3}/><circle cx="140" cy="-50" r="20" fill="#d8b98f" {O3}/>')
    if p.get("gira"):
        anim(t, f"#{u}", "{rotation: 0}", "{rotation: 8, duration: 0.3, ease: 'power2.out', transformOrigin: '50% 100%'}", p["gira"])
    return g(p, s, u)


@dib("muneca")
def muneca(p, u, t):
    """Muñeca vieja y gastada (sin un ojo)."""
    s = (f'<circle cx="0" cy="-260" r="80" fill="#e8d6c0" {O}/><path d="M-80,-280 Q-60,-370 0,-360 Q60,-370 80,-280 Q60,-320 0,-320 Q-60,-320 -80,-280 Z" fill="#8a6a3a"/>'
         f'<circle cx="-28" cy="-260" r="13" fill="#111"/><circle cx="28" cy="-260" r="13" fill="#2b2b2b" opacity=".25"/>'
         f'<path d="M-90,-180 L90,-180 L130,0 L-130,0 Z" fill="#c9b5a0" {O}/><path d="M-60,-140 L-90,-60 M50,-120 L70,-40" stroke="#8a7a66" stroke-width="5"/>')
    vaiven(t, f"#{u}", "rotation: 3, transformOrigin: '50% 0%'", periodo=2.4)
    return g(p, s, u)


@dib("silla")
def silla(p, u, t):
    s = (f'<rect x="-120" y="-460" width="24" height="460" fill="#6b4423" {O3}/><rect x="96" y="-200" width="24" height="200" fill="#6b4423" {O3}/>'
         f'<rect x="-120" y="-220" width="240" height="30" fill="#8a5a2f" {O3}/><rect x="-60" y="-200" width="24" height="200" fill="#6b4423" {O3}/>'
         + "".join(f'<rect x="-120" y="{-440 + k * 60}" width="180" height="16" fill="#8a5a2f" {O3}/>' for k in range(3)))
    if p.get("mov") == "desliza":
        anim(t, f"#{u}", "{x: 0}", f"{{x: {p.get('avance', 260)}, duration: 1.4, ease: 'power1.inOut'}}", p.get("en", 0.6))
    if p.get("mov") == "flota":
        anim(t, f"#{u}", "{y: 0, rotation: 0}", "{y: -260, rotation: -18, duration: 1.6, ease: 'sine.inOut'}", p.get("en", 0.4))
    return g(p, s, u)


@dib("cama")
def cama(p, u, t):
    s = (f'<rect x="-300" y="-180" width="600" height="120" rx="10" fill="#6b4423" {O}/><rect x="-300" y="-330" width="40" height="330" fill="#6b4423" {O3}/>'
         f'<rect x="260" y="-260" width="40" height="260" fill="#6b4423" {O3}/><rect x="-260" y="-230" width="520" height="70" rx="20" fill="#e9e2d0" {O3}/>'
         f'<rect x="-250" y="-270" width="130" height="50" rx="20" fill="#fff" {O3}/><path d="M-110,-225 Q100,-280 260,-225 L260,-170 L-110,-170 Z" fill="#7a8fb5" {O3}/>')
    if p.get("tiembla"):
        t.js.append(f'tl.to("#{u}", {{x: 8, duration: 0.05, yoyo: true, repeat: {int(t.dur / 0.05) - 2}, ease: "none"}}, {t.at(0.3)});')
    return g(p, s, u)


@dib("calavera")
def calavera(p, u, t):
    """Calavera elegante con sombrero de plumas (Catrina / Calavera Garbancera)."""
    s = (f'<defs>{lin("#ffffff", "#d8d2c6", u + "c", 0)}</defs>'
         f'<path d="M-140,-200 Q-150,-420 0,-430 Q150,-420 140,-200 Q120,-140 80,-130 L70,-60 L-70,-60 L-80,-130 Q-120,-140 -140,-200 Z" fill="url(#{u}c)" {O}/>'
         f'<ellipse cx="-60" cy="-260" rx="42" ry="48" fill="#1b1b1b"/><ellipse cx="60" cy="-260" rx="42" ry="48" fill="#1b1b1b"/>'
         f'<circle cx="-60" cy="-262" r="12" fill="#e3141b"/><circle cx="60" cy="-262" r="12" fill="#e3141b"/>'
         f'<path d="M0,-210 L-18,-170 L18,-170 Z" fill="#1b1b1b"/>'
         + "".join(f'<rect x="{-56 + k * 16}" y="-120" width="12" height="40" rx="3" fill="#f4f0e6" {O3}/>' for k in range(8))
         + f'<path d="M-130,-330 Q-60,-370 -30,-330 Q0,-370 30,-330 Q60,-370 130,-330" stroke="#e3141b" stroke-width="7" fill="none"/>')
    if p.get("sombrero", True):
        s += (f'<ellipse cx="0" cy="-410" rx="300" ry="60" fill="#3a2a5a" {O}/><path d="M-150,-420 Q-130,-560 0,-560 Q130,-560 150,-420 Z" fill="#4a3a7a" {O}/>'
              f'<path d="M80,-540 Q220,-700 300,-640 Q200,-600 120,-520 Z" fill="#ff5fa2" {O3}/><path d="M40,-560 Q120,-760 220,-740 Q130,-660 70,-550 Z" fill="#ffd21f" {O3}/>'
              f'<path d="M-40,-560 Q-160,-720 -260,-690 Q-150,-640 -80,-545 Z" fill="#3df5ff" {O3}/>')
    return g(p, s, u)


@dib("momia")
def momia(p, u, t):
    """Momia chinchorro: cuerpo cubierto de arcilla con máscara negra o roja, tendida o de pie."""
    col = p.get("color", "#1b1b1b")
    s = (f'<defs>{lin("#7a5a3a", "#3a2614", u + "c", 0)}</defs>'
         f'<path d="M-90,0 L-110,-420 Q-100,-520 0,-540 Q100,-520 110,-420 L90,0 Z" fill="url(#{u}c)" {O}/>'
         f'<ellipse cx="0" cy="-620" rx="90" ry="110" fill="{col}" {O}/>'
         f'<ellipse cx="-34" cy="-630" rx="18" ry="10" fill="#d8c9b0"/><ellipse cx="34" cy="-630" rx="18" ry="10" fill="#d8c9b0"/>'
         f'<ellipse cx="0" cy="-570" rx="22" ry="10" fill="#d8c9b0"/>'
         + "".join(f'<line x1="-100" x2="100" y1="{-400 + k * 70}" y2="{-380 + k * 70}" stroke="#2a1a0e" stroke-width="5"/>' for k in range(5)))
    return g(p, s, u)


@dib("cerebro")
def cerebro(p, u, t):
    s = (f'<defs>{rad([(0, "#ffd0cc", 1), (1, "#d98a85", 1)], u + "c", "40%", "35%", "70%")}</defs>'
         f'<path d="M-240,-140 Q-280,-330 -120,-380 Q0,-440 120,-380 Q280,-330 240,-140 Q200,-40 60,-60 Q0,-20 -60,-60 Q-200,-40 -240,-140 Z" fill="url(#{u}c)" {O}/>'
         f'<path d="M0,-420 Q-20,-250 0,-60" stroke="#b56d68" stroke-width="7" fill="none"/>'
         + "".join(f'<path d="M{x},{y} q30,-30 60,0 t60,0" stroke="#b56d68" stroke-width="6" fill="none"/>' for x, y in [(-200, -280), (-180, -180), (40, -300), (60, -190), (-120, -340), (30, -120)]))
    if p.get("zona"):
        zx, zy = {"frontal": (-150, -260), "trasera": (170, -220)}[p["zona"]]
        s += f'<circle id="{u}z" cx="{zx}" cy="{zy}" r="90" fill="#ffd21f" opacity=".55"/>'
        vaiven(t, f"#{u}z", "opacity: 0.15", periodo=0.8)
    if p.get("corte"):
        s += "".join(f'<line id="{u}l{k}" x1="{-240 + k * 60}" y1="-450" x2="{-240 + k * 60}" y2="-40" stroke="#fff" stroke-width="5" stroke-dasharray="20 14" opacity="0"/>' for k in range(9))
        for k in range(9):
            anim(t, f"#{u}l{k}", "{opacity: 0}", "{opacity: 0.9, duration: 0.15}", 0.4 + k * 0.12)
    return g(p, s, u)


@dib("craneo")
def craneo(p, u, t):
    """Cráneo de perfil atravesado por una barra de hierro (Phineas Gage)."""
    s = (f'<defs>{lin("#f4f0e6", "#c9c2b0", u + "c", 0)}{lin("#8a8f96", "#3e4248", u + "b", 0)}</defs>'
         f'<path d="M-180,-200 Q-200,-430 0,-450 Q190,-440 200,-260 Q205,-170 160,-150 L170,-90 L110,-70 L100,-30 L-40,-30 Q-60,-100 -120,-120 Q-180,-140 -180,-200 Z" fill="url(#{u}c)" {O}/>'
         f'<ellipse cx="80" cy="-250" rx="44" ry="40" fill="#2a2a2a"/>'
         f'<g id="{u}barra"><rect x="-22" y="-900" width="44" height="1100" rx="20" fill="url(#{u}b)" {O} transform="rotate(16)"/></g>')
    anim(t, f"#{u}barra", "{y: 900, opacity: 0}", "{y: 0, opacity: 1, duration: 0.25, ease: 'power4.out'}", p.get("en", 0.3))
    return g(p, s, u)


@dib("casco")
def casco(p, u, t):
    """Casco vikingo real (redondo de hierro con protector de ojos) o el mito con cuernos (cuernos=True)."""
    s = (f'<defs>{lin("#b8bec6", "#5c6268", u + "h", 0)}</defs>'
         f'<path d="M-200,-120 Q-200,-420 0,-430 Q200,-420 200,-120 Z" fill="url(#{u}h)" {O}/>'
         f'<rect x="-210" y="-140" width="420" height="40" rx="10" fill="#8a9096" {O}/>'
         f'<path d="M-150,-100 Q-150,-20 -60,-10 L-20,-60 L20,-60 L60,-10 Q150,-20 150,-100 Z" fill="url(#{u}h)" {O}/>'
         f'<ellipse cx="-80" cy="-60" rx="38" ry="24" fill="#111"/><ellipse cx="80" cy="-60" rx="38" ry="24" fill="#111"/>'
         f'<rect x="-12" y="-430" width="24" height="300" fill="#8a9096"/>')
    if p.get("cuernos"):
        s = (f'<path id="{u}c1" d="M-190,-250 Q-330,-300 -320,-520 Q-270,-360 -170,-330 Z" fill="#efe6cf" {O}/>'
             f'<path id="{u}c2" d="M190,-250 Q330,-300 320,-520 Q270,-360 170,-330 Z" fill="#efe6cf" {O}/>') + s
        if p.get("cuernos_en") is not None:
            anim(t, f"#{u}c1, #{u}c2", "{scale: 0, transformOrigin: '50% 100%'}", "{scale: 1, duration: 0.35, ease: 'back.out(2.5)'}", p["cuernos_en"])
    if p.get("tachar"):
        s += f'<line id="{u}x" x1="-300" y1="-520" x2="300" y2="40" stroke="#e3141b" stroke-width="40" stroke-linecap="round" stroke-dasharray="900" stroke-dashoffset="900"/>'
        anim(t, f"#{u}x", "{attr: {'stroke-dashoffset': 900}}", "{attr: {'stroke-dashoffset': 0}, duration: 0.3, ease: 'power2.in'}", p.get("tachar", 0.8))
    return g(p, s, u)


@dib("espartano")
def espartano(p, u, t):
    """Hoplita espartano: grebas de bronce, túnica roja, capa, brazos con escudo redondo (lambda) y lanza,
    casco corintio con penacho y ojos visibles por la abertura."""
    piel, piel_s = "#d9a06e", "#b07a4c"
    d = (f'<defs>{lin("#e8b85a", "#8a6420", u + "b", 0)}{lin("#c0392b", "#6a1410", u + "c", 0)}{lin(piel, piel_s, u + "p", 0)}'
         f'{rad([(0, "#f2cc70", 1), (.7, "#c89434", 1), (1, "#7a5418", 1)], u + "e", "40%", "35%", "70%")}</defs>')
    capa = f'<path d="M-60,-430 Q-150,-250 -120,-40 L60,-40 Q20,-250 40,-430 Z" fill="#7a1813" stroke="{TINTA}" stroke-width="4"/>'
    lanza = (f'<line x1="150" y1="30" x2="215" y2="-780" stroke="{TINTA}" stroke-width="20" stroke-linecap="round"/>'
             f'<line x1="150" y1="30" x2="215" y2="-780" stroke="#7a5230" stroke-width="12" stroke-linecap="round"/>'
             f'<path d="M205,-770 L232,-868 L246,-772 Z" fill="#cfd5dc" stroke="{TINTA}" stroke-width="4"/>')
    piernas = (f'<path d="M-44,-160 L-48,-8 L-14,-8 L-10,-160 Z M10,-160 L14,-8 L48,-8 L44,-160 Z" fill="url(#{u}p)" stroke="{TINTA}" stroke-width="4"/>'
               f'<path d="M-50,-120 L-46,-24 L-12,-24 L-10,-120 Q-30,-132 -50,-120 Z M10,-120 L12,-24 L46,-24 L50,-120 Q30,-132 10,-120 Z" fill="url(#{u}b)" stroke="{TINTA}" stroke-width="3.5"/>'
               f'<path d="M-54,-10 L-8,-10 L-8,4 L-58,4 Z M8,-10 L54,-10 L58,4 L8,4 Z" fill="#5a3a22" stroke="{TINTA}" stroke-width="3"/>')
    torso = (f'<path d="M-64,-440 Q0,-466 64,-440 L70,-250 L84,-150 L-84,-150 L-70,-250 Z" fill="url(#{u}c)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
             + "".join(f'<rect x="{-80 + k * 20}" y="-176" width="16" height="44" rx="4" fill="url(#{u}b)" stroke="{TINTA}" stroke-width="2.5"/>' for k in range(9))
             + f'<path d="M-58,-430 Q0,-410 58,-430 L54,-330 Q0,-300 -54,-330 Z" fill="url(#{u}b)" stroke="{TINTA}" stroke-width="4"/>'
             f'<path d="M-30,-400 Q0,-380 30,-400" stroke="#7a5418" stroke-width="4" fill="none"/>')
    brazo_der = (f'<path d="M62,-420 Q125,-360 165,-300" stroke="{TINTA}" stroke-width="36" stroke-linecap="round" fill="none"/>'
                 f'<path d="M62,-420 Q125,-360 165,-300" stroke="{piel}" stroke-width="27" stroke-linecap="round" fill="none"/>'
                 f'<circle cx="176" cy="-292" r="20" fill="url(#{u}p)" stroke="{TINTA}" stroke-width="3.5"/>')
    casco = (f'<path d="M-62,-470 Q-70,-610 0,-622 Q70,-610 62,-470 L52,-452 L20,-452 L16,-520 L-16,-520 L-20,-452 L-52,-452 Z" fill="url(#{u}b)" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/>'
             f'<path d="M-16,-520 L16,-520 L14,-470 L-14,-470 Z" fill="#2a1a10"/>'
             f'<ellipse cx="-8" cy="-532" rx="7" ry="5" fill="#fff"/><ellipse cx="22" cy="-532" rx="7" ry="5" fill="#fff"/>'
             f'<circle cx="-6" cy="-532" r="3.5" fill="{TINTA}"/><circle cx="24" cy="-532" r="3.5" fill="{TINTA}"/>'
             f'<path d="M-30,-556 L-8,-548 M48,-556 L26,-548" stroke="#2a1a10" stroke-width="6" stroke-linecap="round"/>'
             f'<path d="M-36,-600 Q-20,-616 0,-618" stroke="#fff" stroke-opacity=".35" stroke-width="6" fill="none"/>'
             f'<g id="{u}pen"><path d="M-80,-600 Q0,-760 90,-610 Q60,-640 0,-650 Q-50,-640 -80,-600 Z" fill="#b3261e" stroke="{TINTA}" stroke-width="4"/>'
             + "".join(f'<path d="M{-60 + k * 18},-{620 + (k % 2) * 10} Q{-50 + k * 18},-{700 - abs(k - 4) * 8} {-40 + k * 18},-{622}" stroke="#7a1813" stroke-width="3" fill="none"/>' for k in range(8))
             + "</g>")
    escudo = (f'<g id="{u}esc"><circle cx="-120" cy="-300" r="176" fill="url(#{u}e)" stroke="{TINTA}" stroke-width="7"/>'
              f'<circle cx="-120" cy="-300" r="150" fill="none" stroke="#7a5418" stroke-width="6"/>'
              f'<path d="M-188,-200 L-120,-392 L-52,-200" stroke="#7a1813" stroke-width="26" fill="none" stroke-linejoin="round"/>'
              f'<path d="M-230,-400 Q-180,-460 -110,-466" stroke="#fff" stroke-opacity=".4" stroke-width="10" fill="none"/></g>')
    s = d + capa + lanza + piernas + torso + brazo_der + casco + escudo
    vaiven(t, f"#{u}", "y: -6", periodo=1.4)
    vaiven(t, f"#{u}pen", "rotation: 3, transformOrigin: '50% 100%'", periodo=1.1)
    return g(p, s, u)


@dib("estatua_libertad")
def estatua_libertad(p, u, t):
    """Estatua de la Libertad. color: cobre (recién llegada) o verde (pátina). cambia_en: segundos para pasar a verde."""
    cobre, verde = ("#d98a4a", "#9a5426"), ("#7fc3a8", "#3f8a72")
    c = verde if p.get("color") == "verde" else cobre
    s = (f'<defs><linearGradient id="{u}g" x1="0" y1="0" x2="1" y2="0"><stop id="{u}s1" offset="0" stop-color="{c[0]}"/><stop id="{u}s2" offset="1" stop-color="{c[1]}"/></linearGradient></defs>'
         f'<rect x="-190" y="-220" width="380" height="220" fill="#b9b2a2" {O}/><rect x="-150" y="-330" width="300" height="110" fill="#cfc8b6" {O}/>'
         f'<path d="M-110,-330 L-80,-760 Q0,-800 80,-760 L110,-330 Z" fill="url(#{u}g)" {O}/>'
         f'<path d="M60,-740 L120,-760 L180,-1000 L140,-1010 L90,-780 Z" fill="url(#{u}g)" {O}/>'
         f'<path d="M140,-1010 L180,-1000 L190,-1060 L130,-1070 Z" fill="url(#{u}g)" {O3}/>'
         f'<path id="{u}ll" d="M160,-1070 Q120,-1140 162,-1190 Q200,-1140 160,-1070 Z" fill="#ffcf4a" {O3}/>'
         f'<circle cx="0" cy="-830" r="62" fill="url(#{u}g)" {O}/>'
         + "".join(f'<path d="M{50 * math.cos(math.radians(a)):.0f},{-860 + 50 * math.sin(math.radians(a)):.0f} L{105 * math.cos(math.radians(a)):.0f},{-860 + 105 * math.sin(math.radians(a)):.0f}" stroke="{c[1]}" stroke-width="16" stroke-linecap="round"/>' for a in range(-160, -10, 25))
         + f'<path d="M-100,-640 L-170,-520 L-110,-500 Z" fill="url(#{u}g)" {O3}/>')
    if p.get("cambia_en") is not None:
        t.js.append(f'tl.to("#{u}s1", {{attr: {{"stop-color": "{verde[0]}"}}, duration: 2.0}}, {t.at(p["cambia_en"])});'
                    f'tl.to("#{u}s2", {{attr: {{"stop-color": "{verde[1]}"}}, duration: 2.0}}, {t.at(p["cambia_en"])});')
    vaiven(t, f"#{u}ll", "scaleY: 1.12, transformOrigin: '50% 100%'", periodo=0.4)
    return g(p, s, u)


@dib("torre_eiffel")
def torre_eiffel(p, u, t):
    s = (f'<path d="M-200,0 Q-80,-300 -30,-700 L-12,-1000 L12,-1000 L30,-700 Q80,-300 200,0 L120,0 Q40,-160 0,-160 Q-40,-160 -120,0 Z" fill="#6b5a46" {O}/>'
         f'<rect x="-110" y="-330" width="220" height="24" fill="#6b5a46" {O3}/><rect x="-60" y="-650" width="120" height="20" fill="#6b5a46" {O3}/>')
    return g(p, s, u)


@dib("estacas")
def estacas(p, u, t):
    """Bosque de estacas en silueta contra el cielo (sin cuerpos)."""
    rng = random.Random(8)
    s = "".join(f'<path d="M{x - 10:.0f},0 L{x - 8:.0f},{-h:.0f} L{x:.0f},{-h - 40:.0f} L{x + 8:.0f},{-h:.0f} L{x + 10:.0f},0 Z" fill="#0d0f16"/>'
                for x, h in ((rng.uniform(-560, 560), rng.uniform(280, 620)) for _ in range(46)))
    return g(p, s, u)


@dib("sirena_fiji")
def sirena_fiji(p, u, t):
    """La «sirena de Fiyi»: torso seco de mono cosido a una cola de pez (marrón, arrugada)."""
    s = (f'<defs>{lin("#8a6a4a", "#3e2a18", u + "m", 0)}{lin("#7a6a4a", "#3a2e1e", u + "c")}</defs>'
         f'<path d="M-40,-200 Q120,-180 220,-80 Q300,-20 360,-60 Q330,0 360,50 Q290,20 210,30 Q60,40 -40,-60 Z" fill="url(#{u}c)" {O}/>'
         + "".join(f'<path d="M{20 + k * 40},-120 q20,20 0,40" stroke="#2a1e12" stroke-width="4" fill="none"/>' for k in range(6))
         + f'<path d="M-160,-60 Q-200,-260 -100,-300 Q-20,-310 0,-220 Q10,-120 -40,-60 Z" fill="url(#{u}m)" {O}/>'
         f'<circle cx="-110" cy="-360" r="78" fill="url(#{u}m)" {O}/>'
         f'<ellipse cx="-140" cy="-372" rx="14" ry="10" fill="#111"/><ellipse cx="-86" cy="-372" rx="14" ry="10" fill="#111"/>'
         f'<path d="M-160,-320 Q-110,-280 -60,-320 L-70,-300 Q-110,-290 -150,-300 Z" fill="#2a1a0e"/>'
         + "".join(f'<path d="M{-150 + k * 12},-318 l5,12 l5,-12" fill="#f4f0e6"/>' for k in range(8))
         + f'<path d="M-180,-200 Q-230,-120 -200,-60" stroke="#5a4028" stroke-width="22" fill="none" stroke-linecap="round"/>')
    return g(p, s, u)


@dib("excavadora")
def excavadora(p, u, t):
    s = (f'<rect x="-260" y="-200" width="360" height="160" rx="10" fill="#f2b51b" {O}/><rect x="-200" y="-320" width="180" height="130" fill="#f2b51b" {O}/>'
         f'<rect x="-180" y="-300" width="140" height="80" fill="#9cc9e6"/><rect x="-300" y="-60" width="440" height="60" rx="30" fill="#333" {O3}/>'
         f'<g id="{u}b"><path d="M90,-170 L320,-380 L360,-340 L140,-140 Z" fill="#f2b51b" {O}/><path d="M320,-380 L430,-220 L340,-180 Z" fill="#555" {O}/></g>')
    vaiven(t, f"#{u}b", "rotation: 10, transformOrigin: '10% 90%'", periodo=1.6)
    return g(p, s, u)


@dib("laser")
def laser(p, u, t):
    """Rayo láser verde desde (x1,y1) hasta (x2,y2) que viaja y rebota."""
    x1, y1, x2, y2 = p["x1"], p["y1"], p["x2"], p["y2"]
    L = int(math.dist((x1, y1), (x2, y2)))
    s = (f'<line id="{u}a" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5cff7a" stroke-width="10" stroke-linecap="round" stroke-dasharray="{L}" stroke-dashoffset="{L}" style="filter:drop-shadow(0 0 12px #5cff7a)"/>'
         f'<line id="{u}b" x1="{x2}" y1="{y2}" x2="{x1}" y2="{y1}" stroke="#bfffc8" stroke-width="6" stroke-linecap="round" stroke-dasharray="{L}" stroke-dashoffset="{L}"/>')
    anim(t, f"#{u}a", f"{{attr: {{'stroke-dashoffset': {L}}}}}", "{attr: {'stroke-dashoffset': 0}, duration: 0.6, ease: 'none'}", p.get("en", 0.2))
    anim(t, f"#{u}b", f"{{attr: {{'stroke-dashoffset': {L}}}}}", "{attr: {'stroke-dashoffset': 0}, duration: 0.6, ease: 'none'}", p.get("en", 0.2) + 0.7)
    return s


@dib("planeta")
def planeta(p, u, t):
    """Tierra o Luna vista desde el espacio (centro x, y; radio r)."""
    x, y, r = p.get("x", 540), p.get("y", 900), p.get("r", 300)
    if p.get("tipo", "tierra") == "luna":
        s = (f'<defs>{rad([(0, "#f4f1e6", 1), (.75, "#bdb6a2", 1), (1, "#6f6a5c", 1)], u + "l", "35%", "35%", "75%")}</defs>'
             f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{u}l)"/>'
             + "".join(f'<circle cx="{x + r * a:.0f}" cy="{y + r * b:.0f}" r="{r * c:.0f}" fill="#9e9784" opacity=".55"/>' for a, b, c in [(-.3, -.2, .16), (.25, .1, .2), (-.1, .45, .12), (.4, -.4, .1), (-.5, .2, .08)]))
    else:
        s = (f'<defs>{rad([(0, "#4aa3ff", 1), (.75, "#1d5fbf", 1), (1, "#0a2a66", 1)], u + "t", "35%", "35%", "75%")}'
             f'{rad([(0, "#7fd0ff", 0), (.85, "#7fd0ff", 0), (1, "#7fd0ff", .55)], u + "a")}</defs>'
             f'<circle cx="{x}" cy="{y}" r="{r * 1.06:.0f}" fill="url(#{u}a)"/><circle cx="{x}" cy="{y}" r="{r}" fill="url(#{u}t)"/>'
             f'<g id="{u}c" opacity=".9"><path d="M{x - r * .5:.0f},{y - r * .5:.0f} q{r * .3:.0f},{-r * .2:.0f} {r * .5:.0f},{r * .1:.0f} t{r * .2:.0f},{r * .5:.0f} t{-r * .4:.0f},{r * .3:.0f} z" fill="#4caf50"/>'
             f'<path d="M{x + r * .1:.0f},{y + r * .1:.0f} q{r * .3:.0f},0 {r * .4:.0f},{r * .3:.0f} t{-r * .2:.0f},{r * .3:.0f} t{-r * .3:.0f},{-r * .2:.0f} z" fill="#4caf50"/></g>'
             f'<ellipse cx="{x - r * .2:.0f}" cy="{y - r * .3:.0f}" rx="{r * .5:.0f}" ry="{r * .12:.0f}" fill="#fff" opacity=".5"/>')
    if p.get("mov") == "aleja":
        deriva(t, f"#{u}", f"x: {p.get('dx', 160)}, y: {p.get('dy', -120)}, scale: 0.85, transformOrigin: '50% 50%'")
    return f'<g id="{u}">{s}</g>'


@dib("espejos")
def espejos(p, u, t):
    """Panel de retrorreflectores sobre el suelo lunar (rejilla de espejos que brillan)."""
    s = (f'<rect x="-220" y="-180" width="440" height="160" fill="#c9ced6" {O}/>'
         + "".join(f'<circle id="{u}e{k}" cx="{-190 + (k % 10) * 42}" cy="{-160 + (k // 10) * 40}" r="16" fill="#7fd0ff" {O3}/>' for k in range(40))
         + f'<line x1="-200" y1="-20" x2="-240" y2="40" stroke="{TINTA}" stroke-width="8"/><line x1="200" y1="-20" x2="240" y2="40" stroke="{TINTA}" stroke-width="8"/>')
    t.js.append(f'tl.to("#{u} circle", {{fill: "#e9fbff", duration: 0.2, stagger: 0.02, yoyo: true, repeat: 1}}, {t.at(p.get("brillo_en", 0.8))});')
    return g(p, s, u)


@dib("astronauta")
def astronauta(p, u, t):
    s = (f'<defs>{lin("#ffffff", "#c9ced6", u + "s", 0)}</defs>'
         f'<rect x="-90" y="-420" width="180" height="230" rx="40" fill="#e9e9e9" {O}/>'
         f'<path d="M-80,-200 L-90,0 L-20,0 L0,-150 L20,0 L90,0 L80,-200 Z" fill="url(#{u}s)" {O}/>'
         f'<circle cx="0" cy="-480" r="110" fill="url(#{u}s)" {O}/><ellipse cx="0" cy="-475" rx="78" ry="62" fill="#d8a23a" {O3}/>'
         f'<path d="M-90,-380 Q-170,-300 -140,-200" stroke="#e9e9e9" stroke-width="56" fill="none" stroke-linecap="round"/>'
         f'<path d="M90,-380 Q170,-300 140,-200" stroke="#e9e9e9" stroke-width="56" fill="none" stroke-linecap="round"/>')
    vaiven(t, f"#{u}", "y: -14", periodo=2.4)
    return g(p, s, u)


@dib("bandera")
def bandera(p, u, t):
    """Bandera en un mástil. colores: lista de franjas horizontales."""
    cols = p.get("colores", ["#ffffff", "#c41e1e"])
    h = 200 / len(cols)
    s = (f'<rect x="-6" y="-520" width="12" height="520" fill="#888" {O3}/>'
         f'<g id="{u}t">' + "".join(f'<rect x="6" y="{-520 + k * h:.0f}" width="300" height="{h:.0f}" fill="{c}"/>' for k, c in enumerate(cols))
         + (f'<rect x="6" y="-520" width="130" height="{h * 3:.0f}" fill="#2b3a7a"/>' + "".join(f'<circle cx="{24 + (k % 5) * 24}" cy="{-504 + (k // 5) * 22}" r="4" fill="#fff"/>' for k in range(25))
            if p.get("canton") else "") + "</g>")
    vaiven(t, f"#{u}t", "skewY: 5", periodo=1.2)
    return g(p, s, u)


@dib("balon")
def balon(p, u, t):
    """Pelota de fútbol antigua (cuero marrón) que entra al arco."""
    s = (f'<circle cx="0" cy="-60" r="60" fill="#8a5a2f" {O}/><path d="M-50,-90 Q0,-60 50,-90 M-55,-40 Q0,-70 55,-40 M0,-120 V0" stroke="#3a2414" stroke-width="5" fill="none"/>')
    if p.get("mov") == "gol":
        anim(t, f"#{u}", "{x: -500, y: 120, rotation: 0}", "{x: 0, y: 0, rotation: 540, duration: 0.6, ease: 'power2.out'}", p.get("en", 0.4))
    return g(p, s, u)


@dib("arco")
def arco(p, u, t):
    s = (f'<rect x="-420" y="-360" width="22" height="360" fill="#fff" {O3}/><rect x="398" y="-360" width="22" height="360" fill="#fff" {O3}/>'
         f'<rect x="-420" y="-380" width="840" height="22" fill="#fff" {O3}/>'
         + "".join(f'<line x1="{x}" y1="-358" x2="{x + 30}" y2="0" stroke="#fff" stroke-opacity=".35" stroke-width="3"/>' for x in range(-398, 400, 40))
         + "".join(f'<line x1="-398" y1="{y}" x2="398" y2="{y}" stroke="#fff" stroke-opacity=".3" stroke-width="3"/>' for y in range(-330, 0, 40)))
    return g(p, s, u)


@dib("ataud")
def ataud(p, u, t):
    """Pequeño féretro con tapa de vidrio y flores (Rosalía), sobriamente."""
    s = (f'<defs>{lin("#e9f3f6", "#9fc1cc", u + "v")}</defs>'
         f'<path d="M-330,0 L-360,-120 L-300,-200 L330,-200 L360,-120 L330,0 Z" fill="#5a3a22" {O}/>'
         f'<path d="M-310,-200 L-290,-300 L290,-300 L310,-200 Z" fill="url(#{u}v)" opacity=".35" {O}/>'
         f'<ellipse cx="-180" cy="-210" rx="70" ry="50" fill="#f1d3b5"/><path d="M-250,-230 Q-180,-290 -110,-230" fill="#c8a24a"/>'
         f'<path d="M-180,-262 Q-160,-290 -140,-262" fill="#c8a24a"/><rect x="-110" y="-240" width="300" height="40" rx="18" fill="#f4efe4"/>'
         + "".join(f'<circle cx="{-260 + k * 60}" cy="-195" r="14" fill="{c}"/>' for k, c in enumerate(["#e3a6b4", "#fff", "#e3a6b4", "#fff", "#e3a6b4", "#fff", "#e3a6b4", "#fff", "#e3a6b4", "#fff"])))
    return g(p, s, u)


@dib("velas")
def velas(p, u, t):
    n = p.get("n", 5)
    s = []
    for k in range(n):
        x = -60 * (n - 1) / 2 + k * 60
        h = 80 + (k % 3) * 40
        s.append(f'<rect x="{x - 14}" y="{-h}" width="28" height="{h}" fill="#f4efe4" {O3}/>'
                 f'<path id="{u}l{k}" d="M{x},{-h - 50} Q{x + 14},{-h - 20} {x},{-h - 4} Q{x - 14},{-h - 20} {x},{-h - 50} Z" fill="#ffcf4a"/>'
                 f'<defs>{rad([(0, "#ffcf7a", .5), (1, "#ffcf7a", 0)], u + f"g{k}")}</defs><circle cx="{x}" cy="{-h - 25}" r="90" fill="url(#{u}g{k})"/>')
        vaiven(t, f"#{u}l{k}", "scaleY: 1.2, scaleX: 0.85, transformOrigin: '50% 100%'", periodo=0.3 + k * 0.05)
    return g(p, "".join(s), u)


@dib("huellas")
def huellas(p, u, t):
    """Huellas en la nieve que avanzan hacia un punto (solo de ida)."""
    s = []
    for k in range(p.get("n", 9)):
        x = (k % 2) * 40 - 20 + k * p.get("dx", 18)
        y = -k * p.get("dy", 70)
        sc = 1 - k * 0.06
        s.append(f'<ellipse id="{u}h{k}" cx="{x:.0f}" cy="{y:.0f}" rx="{18 * sc:.1f}" ry="{30 * sc:.1f}" fill="#8a9bb8" opacity="0"/>')
        anim(t, f"#{u}h{k}", "{opacity: 0}", "{opacity: 0.85, duration: 0.15}", 0.3 + k * 0.22)
    return g(p, "".join(s), u)


@dib("ojos")
def ojos(p, u, t):
    """Par de ojos que se abren en la oscuridad (vigilancia)."""
    col = p.get("color", "#ffd21f")
    s = (f'<g id="{u}o"><ellipse cx="-80" cy="0" rx="50" ry="22" fill="{col}"/><ellipse cx="80" cy="0" rx="50" ry="22" fill="{col}"/>'
         f'<circle cx="-80" cy="0" r="12" fill="#000"/><circle cx="80" cy="0" r="12" fill="#000"/></g>')
    anim(t, f"#{u}o", "{scaleY: 0, transformOrigin: '50% 50%'}", "{scaleY: 1, duration: 0.25, ease: 'power2.out'}", p.get("en", 0.6))
    t.js.append(f'tl.to("#{u}o", {{scaleY: 0.05, duration: 0.08, yoyo: true, repeat: 1}}, {t.at(p.get("en", 0.6) + 1.2)});')
    return g(p, s, u)


@dib("texto_svg")
def texto_svg(p, u, t):
    """Texto grande dentro de la escena (cartel, código, letras P→F...)."""
    s = (f'<text id="{u}t" x="0" y="0" text-anchor="middle" font-family="Anton" font-size="{p.get("tam", 120)}" '
         f'fill="{p.get("color", "#fff")}" stroke="#000" stroke-width="{p.get("borde", 6)}" paint-order="stroke">{p.get("texto", "")}</text>')
    if p.get("aparece"):
        anim(t, f"#{u}t", "{opacity: 0, scale: 1.6, transformOrigin: '50% 50%'}", "{opacity: 1, scale: 1, duration: 0.25, ease: 'power3.out'}", p["aparece"])
    return g(p, s, u)


@dib("observatorio")
def observatorio(p, u, t):
    s = (f'<defs>{lin("#f2f2ee", "#a9adb5", u + "c", 0)}</defs>'
         f'<rect x="-200" y="-260" width="400" height="260" fill="url(#{u}c)" {O}/>'
         f'<path d="M-220,-250 A220,220 0 0,1 220,-250 Z" fill="url(#{u}c)" {O}/>'
         f'<path d="M-30,-460 L30,-460 L30,-250 L-30,-250 Z" fill="#1d2233"/>'
         f'<rect x="-40" y="-170" width="80" height="170" fill="#4a3020" {O3}/>')
    return g(p, s, u)


@dib("capsula")
def capsula(p, u, t):
    """Cápsula metálica pequeña con ventanilla y una perrita mirando (Laika)."""
    calor = p.get("calor", False)
    s = (f'<defs>{lin("#d9dde3", "#7d838c", u + "c", 0)}{rad([(0, "#ff5a36", .6), (1, "#ff5a36", 0)], u + "h")}</defs>'
         + (f'<circle id="{u}h" cx="0" cy="-200" r="330" fill="url(#{u}h)"/>' if calor else "")
         + f'<path d="M-160,0 L-200,-240 Q-160,-400 0,-410 Q160,-400 200,-240 L160,0 Z" fill="url(#{u}c)" {O}/>'
         f'<circle cx="0" cy="-230" r="100" fill="#1d2233" {O}/><circle cx="0" cy="-230" r="80" fill="#8fb8d8"/>'
         f'<path d="M-40,-200 Q-40,-270 0,-280 Q40,-270 40,-200 Z" fill="#f2efe8"/><path d="M-30,-270 L-44,-310 L-14,-282 Z M30,-270 L44,-310 L14,-282 Z" fill="#c9a27a"/>'
         f'<circle cx="-14" cy="-240" r="6" fill="#111"/><circle cx="14" cy="-240" r="6" fill="#111"/><ellipse cx="0" cy="-222" rx="8" ry="6" fill="#111"/>'
         + "".join(f'<circle cx="{x}" cy="-60" r="9" fill="#555"/>' for x in (-110, -55, 0, 55, 110)))
    if calor:
        vaiven(t, f"#{u}h", "opacity: 0.4", periodo=0.8)
    return g(p, s, u)


@dib("telefono")
def telefono(p, u, t):
    """Teléfono rojo de disco."""
    s = (f'<path d="M-180,0 L-140,-200 L140,-200 L180,0 Z" fill="#b3261e" {O}/><circle cx="0" cy="-110" r="70" fill="#f2efe8" {O3}/>'
         + "".join(f'<circle cx="{50 * math.cos(math.radians(a)):.0f}" cy="{-110 + 50 * math.sin(math.radians(a)):.0f}" r="10" fill="#333"/>' for a in range(0, 360, 36))
         + f'<g id="{u}a"><path d="M-200,-230 Q-200,-300 -130,-300 L130,-300 Q200,-300 200,-230 L150,-210 L110,-250 L-110,-250 L-150,-210 Z" fill="#b3261e" {O}/></g>')
    if p.get("suena"):
        t.js.append(f'tl.to("#{u}a", {{y: -14, rotation: 3, duration: 0.06, yoyo: true, repeat: {int(t.dur / 0.06) - 2}, ease: "none"}}, {t.at(0.2)});')
    return g(p, s, u)


@dib("trono")
def trono(p, u, t):
    s = (f'<path d="M-160,0 V-260 H160 V0 Z" fill="#8a1d2a" {O}/><path d="M-150,-260 V-640 Q0,-720 150,-640 V-260 Z" fill="#a8243a" {O}/>'
         f'<path d="M-170,-260 H170 V-200 H-170 Z" fill="#d8b04f" {O3}/><circle cx="0" cy="-560" r="40" fill="#d8b04f" {O3}/>')
    return g(p, s, u)


@dib("corona")
def corona(p, u, t):
    s = (f'<path d="M-200,0 L-220,-220 L-110,-110 L0,-260 L110,-110 L220,-220 L200,0 Z" fill="#e8b830" {O}/>'
         + "".join(f'<circle cx="{x}" cy="-50" r="22" fill="{c}" {O3}/>' for x, c in [(-120, "#c0392b"), (0, "#2f5d9e"), (120, "#2e8b57")]))
    vaiven(t, f"#{u}", "y: -10", periodo=1.6)
    return g(p, s, u)


@dib("mesa")
def mesa(p, u, t):
    col = p.get("color", "#6b4423")
    s = (f'<rect x="-320" y="-260" width="640" height="40" rx="8" fill="{col}" {O}/><rect x="-290" y="-220" width="30" height="220" fill="{col}" {O3}/>'
         f'<rect x="260" y="-220" width="30" height="220" fill="{col}" {O3}/>')
    return g(p, s, u)


@dib("mostrador")
def mostrador(p, u, t):
    """Mostrador de farmacia antigua con estantes de frascos detrás (pared completa)."""
    y = p.get("y", 1300)
    rng = random.Random(3)
    est = "".join(f'<rect x="{x}" y="{yy}" width="44" height="{h}" rx="8" fill="{c}" stroke="{TINTA}" stroke-width="3"/>'
                  for yy in (520, 760, 1000) for x, h, c in
                  [(x, rng.randint(70, 120), rng.choice(["#7a3e12", "#2e6b4a", "#6b2d3f", "#c9b27a", "#3a5a8a"])) for x in range(60, 1040, 70)])
    est = est.replace('y="520"', 'y="520"')
    return (f'<rect x="-200" y="-200" width="1480" height="2400" fill="#3a2a1e"/>'
            + "".join(f'<rect x="0" y="{yy + 130}" width="1080" height="18" fill="#5a3a22"/>' for yy in (520, 760, 1000))
            + est.replace('height="', 'data-h="').replace('data-h="', 'height="')
            + f'<rect x="-100" y="{y}" width="1300" height="700" fill="#6b4423" stroke="{TINTA}" stroke-width="5"/>'
            f'<rect x="-100" y="{y}" width="1300" height="40" fill="#8a5a2f"/>')


@dib("hoja")
def hoja(p, u, t):
    """Hojas de coca (verdes, ovaladas) o de cola."""
    s = "".join(f'<g transform="rotate({a})"><path d="M0,0 Q60,-120 0,-260 Q-60,-120 0,0 Z" fill="#3f8f3a" {O3}/><line x1="0" y1="0" x2="0" y2="-250" stroke="#2a6a28" stroke-width="4"/></g>' for a in (-40, 0, 40))
    vaiven(t, f"#{u}", "rotation: 4", periodo=2.2)
    return g(p, s, u)


@dib("nuez")
def nuez(p, u, t):
    s = (f'<ellipse cx="-70" cy="-90" rx="90" ry="80" fill="#a8693a" {O}/><ellipse cx="80" cy="-80" rx="80" ry="72" fill="#c47f45" {O}/>'
         f'<path d="M-70,-170 Q-60,-90 -70,-12 M80,-150 Q90,-80 80,-10" stroke="#5a3418" stroke-width="5" fill="none"/>')
    return g(p, s, u)


@dib("silbido")
def silbido(p, u, t):
    """Ondas de sonido que viajan de un punto a otro (silbo, radio, grito)."""
    x1, y1, x2 = p.get("x1", 200), p.get("y1", 900), p.get("x2", 880)
    s = "".join(f'<path id="{u}o{k}" d="M{x1},{y1 - 40} q30,40 0,80" fill="none" stroke="{p.get("color", "#ffd21f")}" stroke-width="10" stroke-linecap="round"/>' for k in range(5))
    for k in range(5):
        anim(t, f"#{u}o{k}", "{x: 0, opacity: 1}", f"{{x: {x2 - x1}, opacity: 0.1, duration: 1.4, repeat: {max(0, int(t.dur / 1.4))}, ease: 'none'}}", k * 0.28)
    return s


@dib("calendario")
def calendario(p, u, t):
    """Hojas de calendario que caen (pasa el tiempo)."""
    s = "".join(f'<g id="{u}h{k}"><rect x="-150" y="-360" width="300" height="340" rx="14" fill="#f4efe4" stroke="{TINTA}" stroke-width="5"/>'
                f'<rect x="-150" y="-360" width="300" height="80" rx="14" fill="#c0392b"/>'
                f'<text x="0" y="-110" text-anchor="middle" font-family="Anton" font-size="150" fill="#222">{a}</text></g>'
                for k, a in enumerate(p.get("anios", ["1925", "1930", "1935"])[::-1]))
    n = len(p.get("anios", [1, 2, 3]))
    for k in range(n - 1):
        anim(t, f"#{u}h{n - 1 - k}", "{y: 0, rotation: 0, opacity: 1}", "{y: 600, rotation: 40, opacity: 0, duration: 0.5, ease: 'power2.in'}",
             0.5 + k * max(0.5, (t.dur - 1) / max(1, n - 1)))
    return g(p, s, u)


@dib("pixeles")
def pixeles(p, u, t):
    """Cuadrícula de píxeles de colores que se arma (arte de 8 bits genérico)."""
    rng = random.Random(5)
    cols = p.get("colores", ["#e3141b", "#2b59ff", "#ffd21f", "#58c46a", "#f4efe4", "#8a5a2f"])
    s = []
    n = p.get("n", 12)
    for k in range(n * n):
        if rng.random() < .55:
            x, y = (k % n) * 40 - n * 20, (k // n) * 40 - n * 40
            s.append(f'<rect id="{u}p{k}" x="{x}" y="{y}" width="38" height="38" fill="{rng.choice(cols)}"/>')
            anim(t, f"#{u}p{k}", "{opacity: 0, scale: 0, transformOrigin: '50% 50%'}", "{opacity: 1, scale: 1, duration: 0.12}", 0.1 + rng.uniform(0, 1.2))
    return g(p, "".join(s), u)


@dib("sirenas_policia")
def sirenas_policia(p, u, t):
    s = (f'<defs>{rad([(0, "#ff2a2a", .8), (1, "#ff2a2a", 0)], u + "r")}{rad([(0, "#2b7bff", .8), (1, "#2b7bff", 0)], u + "a")}</defs>'
         f'<circle id="{u}r" cx="-200" cy="0" r="500" fill="url(#{u}r)" style="mix-blend-mode:screen"/>'
         f'<circle id="{u}a" cx="200" cy="0" r="500" fill="url(#{u}a)" style="mix-blend-mode:screen" opacity="0"/>')
    veces = max(1, int(t.dur / 0.5))
    t.js.append(f'tl.to("#{u}r", {{opacity: 0, duration: 0.25, yoyo: true, repeat: {veces * 2}, ease: "steps(1)"}}, {t.at(0)});')
    t.js.append(f'tl.to("#{u}a", {{opacity: 1, duration: 0.25, yoyo: true, repeat: {veces * 2}, ease: "steps(1)"}}, {t.at(0)});')
    return g(p, s, u)
