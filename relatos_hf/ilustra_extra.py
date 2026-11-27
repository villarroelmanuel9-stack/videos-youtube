"""Dibujos para las historias nuevas (lote de 54): lugares, vehículos y objetos de época, con el estilo HD."""
from __future__ import annotations

import math
import random

from ilustra import TINTA, anim, deriva, dib, g, lin, rad, vaiven
from ilustra_hd import TIN, filtros

O = f'stroke="{TIN}" stroke-width="4" stroke-linejoin="round"'
O3 = f'stroke="{TIN}" stroke-width="3" stroke-linejoin="round"'


@dib("volcan")
def volcan(p, u, t):
    """Volcán (Vesubio) con lava, y columna de ceniza si erupcion=True."""
    erup = p.get("erupcion", True)
    s = [f'<defs>{filtros(u)}{lin("#6b5a4a", "#2a2018", u + "m", 0)}{lin("#ff9a3c", "#c1121f", u + "l")}'
         f'{rad([(0, "#6a6058", .95), (.7, "#4a4440", .8), (1, "#2a2624", 0)], u + "c")}</defs>']
    if erup:
        s.append(f'<g id="{u}col" filter="url(#{u}blur6)">' + "".join(
            f'<circle cx="{random.Random(k).uniform(-120, 120):.0f}" cy="{-620 - k * 110}" r="{150 + k * 40}" fill="url(#{u}c)"/>' for k in range(6)) + "</g>"
            f'<circle cx="0" cy="-600" r="230" fill="#ff6a00" opacity=".35" filter="url(#{u}blur40)"/>')
        anim(t, f"#{u}col", "{scaleY: 0.3, transformOrigin: '50% 100%'}", f"{{scaleY: 1, duration: {min(3, t.dur * .8):.2f}, ease: 'power2.out'}}")
    s.append(f'<path d="M-640,0 L-160,-560 Q0,-600 160,-560 L640,0 Z" fill="url(#{u}m)" {O}/>'
             f'<path d="M-160,-560 Q0,-600 160,-560 L120,-520 Q0,-540 -120,-520 Z" fill="#2a1a10"/>')
    if erup:
        s.append(f'<path id="{u}lv" d="M-40,-540 Q-60,-400 -120,-260 Q-150,-150 -200,-40 M40,-540 Q80,-380 60,-220" stroke="url(#{u}l)" stroke-width="22" fill="none" stroke-linecap="round"/>')
        vaiven(t, f"#{u}lv", "opacity: 0.7", periodo=.6)
    s.append("".join(f'<path d="M{x},{-30 - abs(x) * .2:.0f} l{random.Random(x).uniform(-40, 40):.0f},{-random.Random(x + 1).uniform(40, 120):.0f}" stroke="#1a140e" stroke-width="3" opacity=".5"/>'
                     for x in range(-500, 500, 70)))
    return g(p, "".join(s), u)


@dib("templo_romano")
def templo_romano(p, u, t):
    """Templo romano con frontón y columnas; ruinas=True lo muestra parcialmente derrumbado y con ceniza."""
    ruinas = p.get("ruinas", False)
    s = [f'<defs>{lin("#f0e6d0", "#b8aa8a", u + "c", 0)}</defs>',
         f'<rect x="-380" y="-60" width="760" height="60" fill="url(#{u}c)" {O}/><rect x="-340" y="-100" width="680" height="40" fill="url(#{u}c)" {O}/>']
    for k, x in enumerate(range(-300, 320, 100)):
        if ruinas and k in (1, 4):
            s.append(f'<rect x="{x - 26}" y="-200" width="52" height="100" fill="url(#{u}c)" {O}/>')
            continue
        s.append(f'<rect x="{x - 26}" y="-480" width="52" height="380" fill="url(#{u}c)" {O}/>'
                 + "".join(f'<line x1="{x - 14 + j * 9}" x2="{x - 14 + j * 9}" y1="-470" y2="-110" stroke="#9a8a6a" stroke-width="2"/>' for j in range(4))
                 + f'<rect x="{x - 34}" y="-500" width="68" height="22" fill="url(#{u}c)" {O3}/>')
    if not ruinas:
        s.append(f'<rect x="-360" y="-540" width="720" height="40" fill="url(#{u}c)" {O}/><path d="M-380,-540 L0,-700 L380,-540 Z" fill="url(#{u}c)" {O}/>'
                 f'<path d="M-280,-555 L0,-670 L280,-555 Z" fill="none" stroke="#9a8a6a" stroke-width="3"/>')
    else:
        s.append(f'<path d="M-360,-540 L-80,-540 L-140,-500 L-360,-500 Z" fill="url(#{u}c)" {O}/><ellipse cx="0" cy="-20" rx="420" ry="40" fill="#8a8478" opacity=".7"/>')
    return g(p, "".join(s), u)


@dib("molde_yeso")
def molde_yeso(p, u, t):
    """Molde de yeso de una persona acurrucada (Pompeya), sobre ceniza."""
    s = (f'<defs>{lin("#f2ece0", "#b9b2a2", u + "y", 0)}</defs><ellipse cx="0" cy="0" rx="320" ry="40" fill="#8a8478"/>'
         f'<path d="M-260,-20 Q-280,-110 -180,-140 Q-100,-170 -40,-120 Q20,-180 120,-160 Q200,-150 230,-90 Q260,-40 200,-10 Q0,10 -260,-20 Z" fill="url(#{u}y)" {O}/>'
         f'<circle cx="-210" cy="-150" r="50" fill="url(#{u}y)" {O}/>'
         f'<path d="M-180,-100 Q-120,-60 -60,-90 M40,-120 Q100,-90 160,-110 M-240,-150 q20,10 40,0" stroke="#9a9282" stroke-width="4" fill="none"/>')
    return g(p, s, u)


@dib("puerta_tumba")
def puerta_tumba(p, u, t):
    """Puerta de piedra sellada con jeroglíficos y sello; agujero=True muestra el brillo dorado detrás."""
    s = [f'<defs>{filtros(u)}{lin("#c9a26a", "#7a5a32", u + "p", 0)}</defs>',
         f'<rect x="-260" y="-640" width="520" height="640" fill="url(#{u}p)" {O}/>',
         f'<rect x="-300" y="-680" width="600" height="50" fill="#8a6a3a" {O}/>']
    rng = random.Random(3)
    for k in range(40):
        x, y = rng.uniform(-220, 200), rng.uniform(-600, -60)
        sh = rng.choice(["M0,0 l10,-20 l10,20 Z", "M0,0 a8,8 0 1,1 16,0", "M0,0 l0,-22 M-6,-16 l12,0", "M0,0 q8,-14 16,0"])
        s.append(f'<path d="{sh}" transform="translate({x:.0f} {y:.0f})" stroke="#5a3e1e" stroke-width="3" fill="none"/>')
    s.append(f'<ellipse cx="0" cy="-300" rx="70" ry="40" fill="#8a2a1e" {O3}/>')
    if p.get("agujero"):
        s.append(f'<circle cx="60" cy="-420" r="30" fill="#1a1006"/><circle id="{u}br" cx="60" cy="-420" r="120" fill="#ffd27a" opacity=".6" filter="url(#{u}blur18)"/>')
        vaiven(t, f"#{u}br", "opacity: 0.3", periodo=.5)
    return g(p, "".join(s), u)


@dib("tesoro")
def tesoro(p, u, t):
    """Tesoro egipcio: cofres, estatua dorada, carro y objetos con brillo."""
    s = [f'<defs>{filtros(u)}{lin("#ffe08a", "#b8861e", u + "o", 0)}</defs>',
         f'<ellipse cx="0" cy="-200" rx="520" ry="300" fill="#ffd27a" opacity=".35" filter="url(#{u}blur40)"/>',
         f'<rect x="-420" y="-160" width="260" height="160" fill="url(#{u}o)" {O}/><path d="M-430,-160 Q-290,-230 -150,-160 Z" fill="url(#{u}o)" {O}/>',
         f'<path d="M60,0 L90,-380 Q150,-440 210,-380 L240,0 Z" fill="url(#{u}o)" {O}/><ellipse cx="150" cy="-420" rx="55" ry="60" fill="url(#{u}o)" {O}/>'
         f'<path d="M95,-430 L150,-480 L205,-430 L205,-360 L95,-360 Z" fill="#2a4a8a" opacity=".8"/><ellipse cx="150" cy="-410" rx="34" ry="40" fill="url(#{u}o)"/>',
         f'<circle cx="360" cy="-90" r="90" fill="none" stroke="url(#{u}o)" stroke-width="16"/><line x1="360" y1="-90" x2="420" y2="-30" stroke="url(#{u}o)" stroke-width="8"/>',
         "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff8d0" opacity=".9"/>' for x, y, r in [(-300, -170, 6), (130, -470, 7), (180, -300, 5), (380, -170, 6)])]
    return g(p, "".join(s), u)


@dib("muro_berlin")
def muro_berlin(p, u, t):
    """Muro de Berlín: losas de hormigón con grafitis y alambre arriba; abierto=True con una brecha."""
    rng = random.Random(8)
    s = [f'<defs>{lin("#cfcac0", "#8a867c", u + "m", 0)}</defs>']
    for k in range(-4, 6):
        x = k * 160
        if p.get("abierto") and k in (0, 1):
            continue
        s.append(f'<rect x="{x - 80}" y="-460" width="156" height="460" fill="url(#{u}m)" {O}/><path d="M{x - 84},-470 Q{x},-500 {x + 80},-470 L{x + 80},-450 L{x - 84},-450 Z" fill="#b9b4aa" {O3}/>')
        for j in range(3):
            col = rng.choice(["#e3141b", "#2b59ff", "#ffd21f", "#58c46a", "#ff5fa2", "#111"])
            s.append(f'<path d="M{x - 60 + rng.uniform(0, 30):.0f},{-120 - j * 110:.0f} q30,-40 60,0 t50,10" stroke="{col}" stroke-width="{rng.uniform(6, 14):.0f}" fill="none" stroke-linecap="round" opacity=".85"/>')
    return g(p, "".join(s), u)


@dib("submarino")
def submarino(p, u, t):
    """Submarino soviético (clase Foxtrot) bajo el agua, con luces de cabina."""
    s = (f'<defs>{lin("#4a5260", "#1a1e26", u + "c")}</defs>'
         f'<path d="M-560,-20 Q-560,-110 -440,-120 L460,-120 Q600,-110 620,-40 Q600,30 460,40 L-440,40 Q-560,30 -560,-20 Z" fill="url(#{u}c)" {O}/>'
         f'<path d="M-80,-120 L-60,-280 L140,-280 L170,-120 Z" fill="url(#{u}c)" {O}/><line x1="40" y1="-280" x2="40" y2="-380" stroke="{TIN}" stroke-width="8"/>'
         f'<path d="M-560,-20 L-640,-90 L-640,50 Z" fill="#2a2e36" {O3}/>'
         + "".join(f'<circle cx="{x}" cy="-40" r="10" fill="#ffd27a"/>' for x in range(-380, 460, 90))
         + f'<text x="200" y="-60" font-family="Anton" font-size="44" fill="#9aa0aa" opacity=".6">Б-59</text>')
    deriva(t, f"#{u}", f"x: '+={p.get('avance', 60)}'")
    vaiven(t, f"#{u}", "y: '+=8'", periodo=3)
    return g(p, s, u)


@dib("bajo_agua")
def bajo_agua(p, u, t):
    """Fondo submarino oscuro con rayos de luz desde la superficie y burbujas."""
    rng = random.Random(5)
    s = [f'<defs>{lin("#0e3a5a", "#020a14", u + "a")}</defs><rect x="-200" y="-200" width="1480" height="2400" fill="url(#{u}a)"/>']
    for k in range(6):
        x = rng.uniform(0, 1080)
        s.append(f'<polygon points="{x - 40:.0f},-100 {x + 40:.0f},-100 {x + 220:.0f},1400 {x - 60:.0f},1400" fill="#7fd0ff" opacity=".05"/>')
    for k in range(40):
        x, y, r = rng.uniform(0, 1080), rng.uniform(300, 1900), rng.uniform(3, 10)
        s.append(f'<circle id="{u}b{k}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="none" stroke="#bfe6ff" stroke-width="1.6" opacity=".6"/>')
        anim(t, f"#{u}b{k}", "{y: 0}", f"{{y: -{rng.uniform(300, 700):.0f}, duration: {max(.5, t.dur):.2f}, ease: 'none'}}")
    return "".join(s)


@dib("auto_1914")
def auto_1914(p, u, t):
    """Auto descapotable de 1914 (Gräf & Stift) con pasajeros de sombrero emplumado."""
    s = (f'<defs>{lin("#2a2f3a", "#0d1018", u + "c")}</defs>'
         f'<path d="M-380,-60 L-380,-160 L-120,-170 L-60,-230 L120,-230 L180,-170 L380,-160 L400,-60 Z" fill="url(#{u}c)" {O}/>'
         f'<rect x="-390" y="-80" width="800" height="30" rx="10" fill="#1a1e26" {O3}/>'
         f'<path d="M-60,-230 L-40,-300 L-20,-230" stroke="{TIN}" stroke-width="6" fill="none"/>'
         + "".join(f'<g><circle cx="{x}" cy="-40" r="70" fill="#111" stroke="#555" stroke-width="8"/>'
                   + "".join(f'<line x1="{x}" y1="-40" x2="{x + 60 * math.cos(math.radians(a)):.0f}" y2="{-40 + 60 * math.sin(math.radians(a)):.0f}" stroke="#777" stroke-width="3"/>' for a in range(0, 360, 30))
                   + "</g>" for x in (-250, 260))
         + f'<circle cx="-40" cy="-280" r="24" fill="#e8c9a4" {O3}/><path d="M-70,-300 Q-40,-340 -10,-300 Z" fill="#2a4a2a"/><path d="M-20,-330 q30,-40 50,-10" stroke="#3a8a3a" stroke-width="6" fill="none"/>'
           f'<circle cx="60" cy="-280" r="24" fill="#e8c9a4" {O3}/><path d="M30,-300 Q60,-330 90,-300 Z" fill="#f2f2ee"/>')
    if p.get("mov") == "frena":
        anim(t, f"#{u}", "{x: -600}", f"{{x: 0, duration: {min(2.2, t.dur * .7):.2f}, ease: 'power3.out'}}")
    return g(p, s, u)


@dib("reactor")
def reactor(p, u, t):
    """Edificio del reactor de Chernóbil con la chimenea a rayas y el techo destruido humeando."""
    s = (f'<defs>{filtros(u)}{lin("#c9c4b8", "#7a766c", u + "e", 0)}{rad([(0, "#8a8a8a", .8), (1, "#5a5a5a", 0)], u + "h")}</defs>'
         f'<rect x="-460" y="-360" width="920" height="360" fill="url(#{u}e)" {O}/>'
         + "".join(f'<rect x="{x}" y="-300" width="70" height="40" fill="#2a2e36"/>' for x in range(-420, 420, 110))
         + f'<path d="M-160,-360 L-120,-470 L-40,-420 L40,-480 L100,-400 L160,-360 Z" fill="#3a3630" {O}/>'
           f'<rect x="200" y="-760" width="70" height="400" fill="#e8e4da" {O}/>'
         + "".join(f'<rect x="200" y="{-760 + k * 80}" width="70" height="40" fill="#c0392b"/>' for k in range(5))
         + f'<g id="{u}hm" filter="url(#{u}blur18)">' + "".join(f'<circle cx="{-20 + k * 30}" cy="{-520 - k * 90}" r="{90 + k * 30}" fill="url(#{u}h)"/>' for k in range(5)) + "</g>"
         + f'<circle cx="0" cy="-440" r="80" fill="#ff8a3c" opacity=".5" filter="url(#{u}blur18)"/>')
    vaiven(t, f"#{u}hm", "y: -30, scale: 1.05", periodo=3)
    return g(p, s, u)


@dib("tunel")
def tunel(p, u, t):
    """Túnel de hormigón inundado en perspectiva, a oscuras, con tuberías y agua hasta las rodillas."""
    s = [f'<defs>{lin("#3a3e44", "#121418", u + "p")}{lin("#2a4a5a", "#0a1418", u + "a")}</defs>',
         '<rect x="-200" y="-200" width="1480" height="2400" fill="#050608"/>',
         f'<polygon points="0,0 1080,0 700,800 380,800" fill="url(#{u}p)"/>',
         f'<polygon points="0,0 380,800 380,1100 0,1920" fill="#1e2126"/><polygon points="1080,0 700,800 700,1100 1080,1920" fill="#16181c"/>',
         f'<polygon points="380,1000 700,1000 1080,1920 0,1920" fill="url(#{u}a)"/>',
         f'<rect x="380" y="800" width="320" height="300" fill="#050608"/>']
    for k in range(8):
        f = k / 8
        s.append(f'<line x1="{60 + 320 * f:.0f}" y1="{120 + 680 * f:.0f}" x2="{60 + 320 * f:.0f}" y2="{1800 - 700 * f:.0f}" stroke="#2a2e36" stroke-width="{12 - 9 * f:.0f}"/>')
    s.append(f'<path d="M0,300 L380,850 M0,360 L380,880" stroke="#5a4a3a" stroke-width="10"/>')
    for k in range(8):
        y = 1150 + k * 100
        s.append(f'<path id="{u}o{k}" d="M{100 + k * 10},{y} q60,-8 120,0 t120,0 t120,0 t120,0 t120,0 t120,0" stroke="#7fb0c9" stroke-width="2" opacity=".35" fill="none"/>')
        vaiven(t, f"#{u}o{k}", "x: 20", periodo=1.6 + k * .1)
    return "".join(s)


@dib("haz_luz")
def haz_luz(p, u, t):
    """Haz de linterna desde (x, y) hacia la dirección `ang`; parpadea si falla=True."""
    x, y, a, L = p.get("x", 540), p.get("y", 1200), p.get("ang", -90), p.get("largo", 900)
    r = math.radians(a)
    x2, y2 = x + L * math.cos(r), y + L * math.sin(r)
    px, py = -math.sin(r) * L * .25, math.cos(r) * L * .25
    s = (f'<defs><linearGradient id="{u}g" x1="{x}" y1="{y}" x2="{x2:.0f}" y2="{y2:.0f}" gradientUnits="userSpaceOnUse">'
         f'<stop offset="0" stop-color="#fff6d0" stop-opacity=".7"/><stop offset="1" stop-color="#fff6d0" stop-opacity="0"/></linearGradient></defs>'
         f'<polygon id="{u}h" points="{x},{y} {x2 + px:.0f},{y2 + py:.0f} {x2 - px:.0f},{y2 - py:.0f}" fill="url(#{u}g)" style="mix-blend-mode:screen"/>'
         f'<circle cx="{x}" cy="{y}" r="10" fill="#fff6d0"/>')
    if p.get("falla"):
        t.js.append(f'tl.to("#{u}h", {{opacity: 0.1, duration: 0.06, yoyo: true, repeat: 7}}, {t.at(p.get("falla_en", 1.0))});')
    return s


@dib("hielo")
def hielo(p, u, t):
    """Banquisa: placas de hielo flotando hasta el horizonte, con grietas y bordes azules."""
    y = p.get("y", 1150)
    rng = random.Random(9)
    s = [f'<defs>{lin("#f4fbff", "#c4dcec", u + "h", 0)}</defs><rect x="-300" y="{y}" width="1680" height="{2000 - y}" fill="#2a4a6a"/>']
    for fila in range(14):
        f = fila / 14
        yy = y + (2000 - y) * f ** 1.6
        x = -200 + rng.uniform(0, 80)
        while x < 1280:
            w = (60 + 260 * f) * rng.uniform(.7, 1.3)
            h = (8 + 70 * f) * rng.uniform(.8, 1.2)
            s.append(f'<path d="M{x:.0f},{yy:.0f} l{w * .2:.0f},{-h:.0f} l{w * .6:.0f},{-h * .2:.0f} l{w * .2:.0f},{h * 1.2:.0f} Z" fill="url(#{u}h)" stroke="#7fb0d0" stroke-width="{1 + 2 * f:.1f}"/>'
                     f'<path d="M{x:.0f},{yy:.0f} l{w:.0f},0 l0,{h * .4:.0f} l{-w:.0f},0 Z" fill="#9fc8e0" opacity=".8"/>')
            x += w + rng.uniform(5, 40) * (1 + f)
    return "".join(s)


@dib("hoguera")
def hoguera(p, u, t):
    """Poste con leña y llamas (sin figura)."""
    s = (f'<rect x="-12" y="-560" width="24" height="560" fill="#4a3020" {O3}/>'
         + "".join(f'<rect x="{-150 + k * 30}" y="{-40 - (k % 3) * 18}" width="22" height="120" rx="8" fill="#6b4423" transform="rotate({(k - 5) * 8} {-139 + k * 30} 0)" {O3}/>' for k in range(11)))
    from ilustra_obj import fuego
    return g(p, s + fuego({"x": 0, "y": 0, "s": 1.0, "ancho": 320}, u + "f", t), u)


@dib("carpa")
def carpa(p, u, t):
    """Carpa militar de campaña con fogata delante (campamento)."""
    s = (f'<defs>{lin("#d8ccb0", "#9a8c6a", u + "c", 0)}</defs><path d="M-260,0 L0,-300 L260,0 Z" fill="url(#{u}c)" {O}/>'
         f'<path d="M0,-300 L-60,0 L60,0 Z" fill="#2a2014"/><line x1="0" y1="-300" x2="0" y2="-340" stroke="{TIN}" stroke-width="6"/>')
    return g(p, s, u)


@dib("barril")
def barril(p, u, t):
    s = (f'<defs>{lin("#a8693a", "#5a3418", u + "b", 0)}</defs><path d="M-80,0 Q-100,-110 -80,-220 L80,-220 Q100,-110 80,0 Z" fill="url(#{u}b)" {O}/>'
         f'<path d="M-90,-50 Q0,-40 90,-50 M-94,-170 Q0,-160 94,-170" stroke="#2a2a2a" stroke-width="10" fill="none"/>')
    return g(p, s, u)


@dib("armadura")
def armadura(p, u, t):
    """Juana de Arco con armadura de placas, pelo corto y estandarte blanco con flores de lis."""
    s = (f'<defs>{lin("#e6eaf0", "#8a929e", u + "a", 0)}</defs>'
         f'<line x1="120" y1="20" x2="150" y2="-760" stroke="#6b4423" stroke-width="12"/>'
         f'<g id="{u}est"><path d="M150,-760 L420,-720 L390,-600 L420,-480 L150,-520 Z" fill="#f4f1e8" {O}/>'
         + "".join(f'<path d="M{x},{y} q-10,-16 0,-30 q10,14 0,30" fill="#c9a24a"/>' for x, y in [(230, -650), (310, -620), (260, -570)]) + "</g>"
         f'<path d="M-40,-150 L-36,-10 L-6,-10 L-4,-150 Z M4,-150 L6,-10 L36,-10 L40,-150 Z" fill="url(#{u}a)" {O3}/>'
         f'<path d="M-56,-370 Q0,-392 56,-370 L62,-200 L40,-150 L-40,-150 L-62,-200 Z" fill="url(#{u}a)" {O}/>'
         f'<path d="M-56,-300 Q0,-280 56,-300 M-58,-240 Q0,-220 58,-240" stroke="#6a727e" stroke-width="3" fill="none"/>'
         f'<path d="M-50,-360 Q-80,-300 -70,-210" stroke="#8a929e" stroke-width="30" stroke-linecap="round" fill="none"/>'
         f'<path d="M50,-360 Q100,-320 128,-300" stroke="#8a929e" stroke-width="30" stroke-linecap="round" fill="none"/>'
         f'<ellipse cx="0" cy="-418" rx="24" ry="30" fill="#efc9a4" {O3}/>'
         f'<path d="M-25,-420 Q-26,-452 0,-452 Q26,-452 25,-420 Q20,-436 0,-438 Q-20,-436 -25,-420 Z" fill="#5a3a1e"/>'
         f'<ellipse cx="-8" cy="-418" rx="3" ry="2.4" fill="{TIN}"/><ellipse cx="10" cy="-418" rx="3" ry="2.4" fill="{TIN}"/>'
         f'<path d="M-6,-394 Q2,-391 8,-394" stroke="#8a4a3a" stroke-width="2.4" fill="none"/>')
    vaiven(t, f"#{u}est", "skewY: 4", periodo=1.3)
    return g(p, s, u)


@dib("pollo")
def pollo(p, u, t):
    """Pollo de granja (sin_cabeza=True para Mike)."""
    sin = p.get("sin_cabeza", False)
    s = (f'<defs>{lin("#f6efe2", "#cfc3ae", u + "c", 0)}</defs>'
         f'<path d="M-40,-20 L-50,0 M-34,-20 L-30,0 M30,-20 L20,0 M36,-20 L40,0" stroke="#e0a030" stroke-width="6" stroke-linecap="round"/>'
         f'<path d="M-130,-150 Q-180,-220 -120,-250 Q-110,-200 -80,-180 Q-40,-230 40,-220 Q120,-200 110,-120 Q100,-30 0,-20 Q-110,-20 -130,-150 Z" fill="url(#{u}c)" {O}/>'
         f'<path d="M-60,-150 Q0,-110 60,-150 Q20,-100 -40,-110 Z" fill="#e3d8c4"/>'
         f'<path d="M40,-210 Q70,-260 80,-300" stroke="#f0e8d8" stroke-width="40" stroke-linecap="round" fill="none"/>')
    if not sin:
        s += (f'<circle cx="86" cy="-320" r="30" fill="url(#{u}c)" {O3}/><path d="M76,-350 q8,-24 18,0 q8,-20 16,2" fill="#d62d20"/>'
              f'<path d="M112,-318 L140,-310 L112,-302 Z" fill="#e0a030"/><circle cx="96" cy="-326" r="4" fill="{TIN}"/>')
    else:
        s += f'<ellipse cx="84" cy="-302" rx="20" ry="9" fill="#c98a7a" {O3}/>'
    vaiven(t, f"#{u}", "rotation: 3, transformOrigin: '50% 100%'", periodo=.8)
    if p.get("mov") == "camina":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 120)}'")
    return g(p, s, u)


@dib("rayo")
def rayo(p, u, t):
    """Rayo que cae en zigzag desde el cielo hasta (x, y), con destello."""
    x, y = p.get("x", 540), p.get("y", 1400)
    rng = random.Random(x + y)
    pts, cx, cy = [(x + rng.uniform(-200, 200), -100)], 0, 0
    for k in range(1, 9):
        pts.append((x + rng.uniform(-90, 90) * (1 - k / 9), -100 + (y + 100) * k / 9))
    pts.append((x, y))
    d = "M" + " L".join(f"{a:.0f},{b:.0f}" for a, b in pts)
    s = (f'<defs>{filtros(u)}</defs><g id="{u}r" opacity="0"><path d="{d}" stroke="#bfe0ff" stroke-width="26" fill="none" filter="url(#{u}blur6)"/>'
         f'<path d="{d}" stroke="#ffffff" stroke-width="8" fill="none"/></g>')
    en = p.get("en", .5)
    t.js.append(f'tl.to("#{u}r", {{opacity: 1, duration: 0.03}}, {t.at(en)}); tl.to("#{u}r", {{opacity: 0.2, duration: 0.05, yoyo: true, repeat: 3}}, {t.at(en + .05)}); tl.to("#{u}r", {{opacity: 0, duration: 0.3}}, {t.at(en + .4)});')
    return s


@dib("trineo")
def trineo(p, u, t):
    """Trineo de perros: musher abrigado y fila de huskies corriendo."""
    s = []
    for k in range(p.get("perros", 5)):
        x = 120 + k * 120
        s.append(f'<g id="{u}p{k}"><path d="M{x - 50},-60 Q{x},-90 {x + 40},-70 L{x + 60},-90 L{x + 64},-60 Q{x + 40},-40 {x},-44 Q{x - 40},-40 {x - 50},-60 Z" fill="#8a929e" {O3}/>'
                 f'<path d="M{x + 44},-76 L{x + 52},-104 L{x + 60},-80" fill="#5a626e"/><path d="M{x - 40},-50 L{x - 54},-10 M{x - 20},-48 L{x - 10},-10 M{x + 20},-50 L{x + 10},-10 M{x + 36},-56 L{x + 50},-14" stroke="#5a626e" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M{x - 30},-62 Q{x},-50 {x + 30},-62" stroke="#f2f2ee" stroke-width="10" fill="none"/></g>')
        vaiven(t, f"#{u}p{k}", "y: -8", periodo=.32 + k * .01)
    s.append(f'<line x1="-60" y1="-40" x2="{120 + p.get("perros", 5) * 120}" y2="-60" stroke="#3a2a1e" stroke-width="4"/>'
             f'<path d="M-200,-10 L-40,-10 Q-20,-10 -20,-30 M-200,-10 Q-220,-10 -220,-30" stroke="#5a3a22" stroke-width="8" fill="none"/>'
             f'<rect x="-190" y="-90" width="140" height="70" fill="#8a5a2f" {O3}/>')
    from ilustra_hd import persona_real
    s.append(persona_real({"x": -150, "y": -60, "s": .55, "ropa": "abrigo", "sombrero": "boina"}, u + "m", t))
    if p.get("mov", "corre") == "corre":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 300)}'")
    return g(p, "".join(s), u)


@dib("cabra")
def cabra(p, u, t):
    s = (f'<path d="M-90,-80 Q-100,-150 -20,-160 L70,-160 Q110,-150 100,-90 L90,-60 L-80,-60 Z" fill="#c9b89a" {O}/>'
         f'<path d="M-70,-60 L-74,0 M-40,-60 L-36,0 M50,-60 L46,0 M80,-60 L84,0" stroke="#8a7a5a" stroke-width="12" stroke-linecap="round"/>'
         f'<path d="M80,-150 Q110,-210 150,-200 Q170,-180 150,-150 Q130,-140 110,-150 Z" fill="#c9b89a" {O3}/>'
         f'<path d="M120,-200 Q110,-250 80,-260 M130,-200 Q140,-250 110,-270" stroke="#6a5a42" stroke-width="7" fill="none"/>'
         f'<path d="M140,-150 l-6,30 l12,-4 Z" fill="#9a8a6a"/><circle cx="140" cy="-185" r="4" fill="{TIN}"/>')
    vaiven(t, f"#{u}", "rotation: 2, transformOrigin: '50% 100%'", periodo=1.6)
    return g(p, s, u)


@dib("placa_petri")
def placa_petri(p, u, t):
    """Placa de Petri vista desde arriba con colonias de bacterias y un moho verde con halo limpio."""
    rng = random.Random(4)
    s = [f'<defs>{rad([(0, "#f4f0d0", 1), (1, "#d8d2a8", 1)], u + "a")}</defs>',
         f'<ellipse cx="0" cy="-160" rx="320" ry="170" fill="#e9f3f6" opacity=".5" {O}/><ellipse cx="0" cy="-160" rx="300" ry="155" fill="url(#{u}a)"/>']
    for k in range(70):
        a, r = rng.uniform(0, 6.28), rng.uniform(.45, 1) * 280
        xx, yy = r * math.cos(a), -160 + r * math.sin(a) * .52
        s.append(f'<circle cx="{xx:.0f}" cy="{yy:.0f}" r="{rng.uniform(5, 12):.0f}" fill="#e8d27a" stroke="#b8a24a" stroke-width="2"/>')
    s.append(f'<ellipse cx="-40" cy="-170" rx="120" ry="64" fill="#f4f0d0"/><ellipse id="{u}m" cx="-40" cy="-170" rx="60" ry="32" fill="#5a9a4a" stroke="#2e6a2a" stroke-width="3"/>')
    anim(t, f"#{u}m", "{scale: 0.2, transformOrigin: '50% 50%'}", "{scale: 1, duration: 1.4, ease: 'power2.out'}", .3)
    return g(p, "".join(s), u)


@dib("microondas")
def microondas(p, u, t):
    """Radarange de 1947: gabinete metálico enorme (casi 2 m) con puerta y perillas."""
    s = (f'<defs>{lin("#c9ced6", "#7a808a", u + "m", 0)}</defs><rect x="-180" y="-820" width="360" height="820" rx="12" fill="url(#{u}m)" {O}/>'
         f'<rect x="-150" y="-760" width="300" height="300" rx="8" fill="#2a2e36" {O3}/><rect x="-130" y="-740" width="260" height="260" fill="#ffcf7a" opacity=".25"/>'
         + "".join(f'<circle cx="{x}" cy="-400" r="18" fill="#3a3e46" {O3}/>' for x in (-90, 0, 90))
         + f'<text x="0" y="-300" text-anchor="middle" font-family="Anton" font-size="40" fill="#3a3e46">RADARANGE</text>')
    return g(p, s, u)


@dib("mano_rx")
def mano_rx(p, u, t):
    """Radiografía: placa oscura con los huesos de una mano y un anillo."""
    s = [f'<rect x="-280" y="-760" width="560" height="760" fill="#0a0e14" {O}/>']
    dedos = [(-150, -330, 200), (-75, -470, 270), (0, -500, 300), (75, -470, 270), (150, -410, 220)]
    for k, (x, y, L) in enumerate(dedos):
        for j in range(3):
            yy = y + j * L / 3
            s.append(f'<rect x="{x - 14}" y="{yy:.0f}" width="28" height="{L / 3 - 8:.0f}" rx="12" fill="#dfe8f0" opacity=".85"/>')
    s.append(f'<path d="M-170,-200 Q-180,-60 -100,-20 L100,-20 Q180,-60 170,-200 Z" fill="#dfe8f0" opacity=".35"/>'
             + "".join(f'<rect x="{x - 12}" y="-210" width="24" height="170" rx="10" fill="#dfe8f0" opacity=".7"/>' for x in (-130, -60, 10, 80))
             + f'<rect x="-82" y="-360" width="34" height="18" rx="6" fill="#ffffff"/>')
    return g(p, "".join(s), u)


@dib("prisma")
def prisma(p, u, t):
    """Prisma de vidrio que descompone un rayo de luz blanca en arcoíris."""
    cols = ["#ff3b30", "#ff9500", "#ffcc00", "#34c759", "#007aff", "#5856d6", "#af52de"]
    s = [f'<line x1="-520" y1="-260" x2="-60" y2="-200" stroke="#fff" stroke-width="12"/>',
         f'<polygon points="0,-360 -140,-80 140,-80" fill="#cfe8f5" opacity=".6" {O}/>']
    for k, c in enumerate(cols):
        s.append(f'<line x1="60" y1="-190" x2="540" y2="{-280 + k * 40}" stroke="{c}" stroke-width="12" opacity=".9"/>')
    return g(p, "".join(s), u)


@dib("manzano")
def manzano(p, u, t):
    """Manzano con manzanas rojas; una cae (cae_en)."""
    rng = random.Random(7)
    s = [f'<defs>{rad([(0, "#5a9a44", 1), (1, "#2e5a24", 1)], u + "c", "40%", "35%", "70%")}</defs>',
         f'<path d="M-40,0 Q-30,-200 -60,-320 L60,-320 Q30,-200 40,0 Z" fill="#5a3a22" {O}/>',
         f'<ellipse cx="0" cy="-480" rx="300" ry="220" fill="url(#{u}c)" {O}/><ellipse cx="-180" cy="-420" rx="150" ry="120" fill="url(#{u}c)" {O3}/><ellipse cx="190" cy="-410" rx="150" ry="120" fill="url(#{u}c)" {O3}/>']
    for k in range(16):
        s.append(f'<circle cx="{rng.uniform(-260, 260):.0f}" cy="{rng.uniform(-620, -340):.0f}" r="14" fill="#d62d20" {O3}/>')
    s.append(f'<circle id="{u}m" cx="120" cy="-360" r="16" fill="#d62d20" {O3}/>')
    if p.get("cae_en") is not None:
        anim(t, f"#{u}m", "{y: 0}", "{y: 340, duration: 0.7, ease: 'bounce.out'}", p["cae_en"])
    return g(p, "".join(s), u)
