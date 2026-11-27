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


# ============================================================================ tanda 3 (historias 30 y 47-95)
def _llama(u, x, y, k=1.0, t=None, idn="f"):
    """Llama de vela pequeña con halo; parpadea si se pasa t."""
    s = (f'<g id="{u}{idn}"><ellipse cx="{x}" cy="{y}" rx="{30 * k:.0f}" ry="{30 * k:.0f}" fill="#ffb347" opacity=".35" filter="url(#{u}blur6)"/>'
         f'<path d="M{x},{y - 22 * k:.0f} Q{x + 9 * k:.0f},{y - 4 * k:.0f} {x},{y + 6 * k:.0f} Q{x - 9 * k:.0f},{y - 4 * k:.0f} {x},{y - 22 * k:.0f} Z" fill="#ffd36a"/>'
         f'<path d="M{x},{y - 10 * k:.0f} Q{x + 4 * k:.0f},{y} {x},{y + 4 * k:.0f} Q{x - 4 * k:.0f},{y} {x},{y - 10 * k:.0f} Z" fill="#fff6d0"/></g>')
    if t is not None:
        vaiven(t, f"#{u}{idn}", "scaleY: 1.15, opacity: 0.8, transformOrigin: '50% 100%'", periodo=.35)
    return s


@dib("calabaza")
def calabaza(p, u, t):
    """Linterna tallada con cara y brasa adentro. tipo: nabo (Irlanda, Samhain) | calabaza."""
    nabo = p.get("tipo", "calabaza") == "nabo"
    c1, c2 = ("#efe6d2", "#b9a98a") if nabo else ("#f08a24", "#b0520e")
    s = [f'<defs>{filtros(u)}{rad([(0, c1, 1), (1, c2, 1)], u + "c", "40%", "35%", "70%")}</defs>']
    if nabo:
        s.append(f'<path d="M-130,-20 Q-150,-170 -60,-220 Q0,-240 60,-220 Q150,-170 130,-20 Q60,10 0,8 Q-60,10 -130,-20 Z" fill="url(#{u}c)" {O}/>'
                 f'<path d="M-60,-220 Q-20,-250 0,-232 Q20,-250 60,-220" fill="#a8549a" opacity=".75"/>'
                 f'<path d="M0,-236 Q-10,-300 -40,-330 M0,-236 Q14,-310 40,-340" stroke="#5a7a3a" stroke-width="9" fill="none" stroke-linecap="round"/>')
    else:
        for k, dx in enumerate((-90, -40, 0, 40, 90)):
            s.append(f'<ellipse cx="{dx}" cy="-110" rx="{80 if k in (0, 4) else 70}" ry="112" fill="url(#{u}c)" {O}/>')
        s.append(f'<path d="M0,-218 Q-6,-260 14,-280" stroke="#4a5a2a" stroke-width="16" fill="none" stroke-linecap="round"/>')
    cara = (f'<path d="M-70,-140 L-30,-140 L-50,-100 Z M30,-140 L70,-140 L50,-100 Z M-12,-96 L12,-96 L0,-76 Z '
            f'M-80,-60 L-56,-40 L-36,-56 L-16,-36 L4,-56 L24,-36 L44,-56 L64,-40 L84,-60 Q60,-10 0,-12 Q-60,-10 -80,-60 Z"')
    s.append(f'<path id="{u}cara" {cara[6:]} fill="#ffcf5a" stroke="#4a2a10" stroke-width="3"/>'
             f'<circle cx="0" cy="-90" r="140" fill="#ff9a3c" opacity=".22" filter="url(#{u}blur40)"/>')
    vaiven(t, f"#{u}cara", "opacity: 0.75", periodo=.4)
    return g(p, "".join(s), u)


@dib("muro_piedra")
def muro_piedra(p, u, t):
    """Muro bajo de piedras apiladas (campo irlandés) a lo ancho de la toma, en y."""
    y, rng = p.get("y", 1500), random.Random(3)
    s = [f'<rect x="-20" y="{y - 150}" width="1120" height="170" fill="#4a4a46"/>']
    for fila in range(4):
        x = -40 + fila % 2 * 40
        while x < 1100:
            w = rng.uniform(70, 130)
            c = rng.choice(["#8a8a80", "#7a7a70", "#6a6a62", "#9a968a"])
            s.append(f'<rect x="{x:.0f}" y="{y - 150 + fila * 40:.0f}" width="{w - 6:.0f}" height="36" rx="14" fill="{c}" {O3}/>'
                     f'<path d="M{x + 8:.0f},{y - 142 + fila * 40:.0f} l{w * .5:.0f},0" stroke="#fff" stroke-opacity=".2" stroke-width="3"/>')
            if rng.random() < .25:
                s.append(f'<ellipse cx="{x + w / 2:.0f}" cy="{y - 150 + fila * 40:.0f}" rx="{w * .3:.0f}" ry="7" fill="#4a6a32" opacity=".8"/>')
            x += w
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("torta")
def torta(p, u, t):
    """Torta de cumpleaños de dos pisos con velas encendidas."""
    s = [f'<defs>{filtros(u)}{lin("#f7e1ea", "#d9a9ba", u + "t", 0)}</defs>',
         f'<ellipse cx="0" cy="0" rx="230" ry="26" fill="#e8e4dc" {O}/>',
         f'<path d="M-190,-8 L-190,-140 Q0,-170 190,-140 L190,-8 Q0,20 -190,-8 Z" fill="url(#{u}t)" {O}/>',
         f'<path d="M-190,-140 Q-150,-110 -120,-140 Q-90,-110 -60,-140 Q-30,-110 0,-140 Q30,-110 60,-140 Q90,-110 120,-140 Q150,-110 190,-140" fill="#fff" {O3}/>',
         f'<path d="M-120,-150 L-120,-250 Q0,-270 120,-250 L120,-150" fill="url(#{u}t)" {O}/>',
         f'<ellipse cx="0" cy="-252" rx="120" ry="18" fill="#fbeff4" {O3}/>']
    for k, x in enumerate((-80, -40, 0, 40, 80)):
        s.append(f'<rect x="{x - 6}" y="-320" width="12" height="64" fill="{["#5aa0e0", "#f0c040", "#e05a7a", "#7ac05a", "#a07ae0"][k]}" {O3}/>'
                 + _llama(u, x, -332, 1.0, t if k == 2 else None, f"f{k}"))
    s.append("".join(f'<circle cx="{random.Random(k).uniform(-180, 180):.0f}" cy="{random.Random(k + 9).uniform(-130, -30):.0f}" r="5" fill="{["#e05a7a", "#5aa0e0", "#f0c040"][k % 3]}"/>' for k in range(18)))
    return g(p, "".join(s), u)


@dib("caballete")
def caballete(p, u, t):
    """Caballete con lienzo. cuadro: girasoles | vinedo (rojo) | atletas | vacio."""
    cu = p.get("cuadro", "girasoles")
    s = [f'<path d="M-140,0 L-40,-560 M140,0 L40,-560 M0,-560 L0,0" stroke="#6a4a2a" stroke-width="18" stroke-linecap="round"/>'
         f'<rect x="-170" y="-200" width="340" height="18" fill="#5a3a1e" {O3}/>',
         f'<rect x="-160" y="-520" width="320" height="320" fill="#f2ead8" {O}/>']
    rng = random.Random(7)
    if cu == "girasoles":
        s.append(f'<rect x="-150" y="-510" width="300" height="300" fill="#e6c25a"/><path d="M-60,-220 L-40,-300 L60,-300 L80,-220 Z" fill="#c98a3a" {O3}/>')
        for k in range(7):
            cx, cy = rng.uniform(-110, 110), rng.uniform(-470, -330)
            s.append("".join(f'<ellipse cx="{cx + 26 * math.cos(a):.0f}" cy="{cy + 26 * math.sin(a):.0f}" rx="16" ry="7" transform="rotate({math.degrees(a):.0f} {cx + 26 * math.cos(a):.0f} {cy + 26 * math.sin(a):.0f})" fill="#f4a81c"/>'
                             for a in [i * math.pi / 6 for i in range(12)]) + f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="16" fill="#6a3a12"/>')
    elif cu == "vinedo":
        s.append(f'<rect x="-150" y="-510" width="300" height="120" fill="#f0b040"/><circle cx="60" cy="-450" r="34" fill="#fff2a0"/>'
                 f'<rect x="-150" y="-390" width="300" height="180" fill="#b8321e"/>'
                 + "".join(f'<path d="M{-150 + k * 50},-210 Q{-120 + k * 40},-300 {-60 + k * 30},-390" stroke="#7a1a10" stroke-width="10" fill="none"/>' for k in range(7))
                 + "".join(f'<circle cx="{rng.uniform(-140, 140):.0f}" cy="{rng.uniform(-380, -220):.0f}" r="6" fill="#2a3a8a"/>' for _ in range(16)))
    elif cu == "atletas":
        s.append(f'<rect x="-150" y="-510" width="300" height="300" fill="#c9b48a"/>'
                 + "".join(f'<path d="M{x},-260 L{x + 10},-330 L{x - 10},-380 M{x + 10},-330 L{x + 40},-300 M{x + 10},-330 L{x - 20},-300 M{x - 10},-380 L{x + 30},-400 M{x - 10},-380 L{x - 40},-350" stroke="#5a3a22" stroke-width="10" stroke-linecap="round" fill="none"/>'
                           f'<circle cx="{x - 14}" cy="-398" r="12" fill="#5a3a22"/>' for x in (-80, 20, 110)))
    s.append(f'<rect x="-160" y="-520" width="320" height="320" fill="none" stroke="#2a1a0e" stroke-width="10"/>')
    return g(p, "".join(s), u)


@dib("girasoles")
def girasoles(p, u, t):
    """Campo de girasoles a lo ancho, desde y hacia abajo (las filas cercanas más grandes)."""
    y0, rng = p.get("y", 1350), random.Random(2)
    s = [f'<rect x="-20" y="{y0}" width="1120" height="{1940 - y0}" fill="#4a6a22"/>']
    for fila in range(5):
        yy, k = y0 + 20 + fila * fila * 40, .35 + fila * .3
        for x in range(-40, 1120, int(120 * k)):
            cx = x + rng.uniform(-10, 10)
            r = 30 * k
            s.append(f'<path d="M{cx:.0f},{yy + 140 * k:.0f} L{cx:.0f},{yy:.0f}" stroke="#3a5a1a" stroke-width="{8 * k:.0f}"/>'
                     f'<ellipse cx="{cx - 20 * k:.0f}" cy="{yy + 70 * k:.0f}" rx="{24 * k:.0f}" ry="{10 * k:.0f}" fill="#4f7a22"/>'
                     f'<circle cx="{cx:.0f}" cy="{yy:.0f}" r="{r * 1.7:.0f}" fill="#f4b41c" stroke="#c98a10" stroke-width="2"/>'
                     f'<circle cx="{cx:.0f}" cy="{yy:.0f}" r="{r * .8:.0f}" fill="#5a2e10"/>')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("piano")
def piano(p, u, t):
    """Piano de cola negro, de costado, con la tapa abierta y partitura."""
    s = (f'<defs>{lin("#3a3a40", "#0a0a0e", u + "n", 90)}</defs>'
         f'<path d="M-260,-300 L-260,-180 L240,-180 Q300,-180 300,-240 Q300,-300 200,-310 Z" fill="url(#{u}n)" {O}/>'
         f'<path d="M-250,-300 L160,-520 L200,-505 L-230,-290 Z" fill="#1a1a1e" {O}/>'
         f'<path d="M-30,-410 L-30,-300" stroke="{TIN}" stroke-width="5"/>'
         f'<rect x="-300" y="-250" width="60" height="22" fill="#f6f4ee" {O3}/>'
         + "".join(f'<rect x="{-300 + k * 10}" y="-250" width="5" height="13" fill="#111"/>' for k in range(6))
         + f'<rect x="-280" y="-330" width="70" height="52" fill="#f2ead8" {O3}/><path d="M-274,-318 l58,0 M-274,-306 l58,0 M-274,-294 l58,0" stroke="#555" stroke-width="1.5"/>'
         f'<path d="M-230,-180 L-226,0 M200,-180 L196,0 M-20,-180 L-18,-10" stroke="#111" stroke-width="18" stroke-linecap="round"/>'
         f'<path d="M-240,-292 L180,-300" stroke="#fff" stroke-opacity=".18" stroke-width="4"/>')
    return g(p, s, u)


@dib("trofeo")
def trofeo(p, u, t):
    """Copa dorada con figura alada (estilo Copa Jules Rimet) sobre base."""
    s = (f'<defs>{filtros(u)}{lin("#fff2a0", "#b8860b", u + "o", 0)}</defs>'
         f'<circle cx="0" cy="-200" r="200" fill="#ffd36a" opacity=".25" filter="url(#{u}blur40)"/>'
         f'<path d="M-70,0 L-60,-70 L60,-70 L70,0 Z" fill="#2a5a8a" {O}/>'
         f'<path d="M-24,-70 Q-40,-170 -20,-230 L20,-230 Q40,-170 24,-70 Z" fill="url(#{u}o)" {O}/>'
         f'<path d="M-20,-200 Q-120,-260 -110,-360 Q-60,-300 -18,-280 Z M20,-200 Q120,-260 110,-360 Q60,-300 18,-280 Z" fill="url(#{u}o)" {O}/>'
         f'<path d="M-80,-300 L80,-300 L60,-380 L-60,-380 Z" fill="url(#{u}o)" {O}/>'
         f'<ellipse cx="0" cy="-380" rx="62" ry="12" fill="#e8c24a" {O3}/>'
         f'<path id="{u}b" d="M-40,-340 L-30,-180" stroke="#fff" stroke-opacity=".6" stroke-width="6"/>')
    vaiven(t, f"#{u}b", "opacity: 0.1", periodo=1.2)
    return g(p, s, u)


@dib("medalla")
def medalla(p, u, t):
    """Medalla de oro con cinta."""
    s = (f'<defs>{lin("#fff2a0", "#b8860b", u + "o", 0)}</defs>'
         f'<path d="M-60,-300 L-10,-120 L10,-120 L60,-300 L30,-300 L0,-170 L-30,-300 Z" fill="#1a4a9a" {O}/>'
         f'<circle cx="0" cy="-80" r="80" fill="url(#{u}o)" {O}/><circle cx="0" cy="-80" r="60" fill="none" stroke="#a87a1a" stroke-width="4"/>'
         f'<path d="M-20,-100 L0,-60 L20,-100" stroke="#a87a1a" stroke-width="6" fill="none"/>')
    vaiven(t, f"#{u}", "rotation: 6, transformOrigin: '50% 0%'", periodo=1.6)
    return g(p, s, u)


@dib("podio")
def podio(p, u, t):
    """Podio de tres escalones con números."""
    s = "".join(f'<rect x="{x}" y="{-h}" width="200" height="{h}" fill="{c}" {O}/><text x="{x + 100}" y="{-h + 80}" font-size="70" font-weight="900" text-anchor="middle" fill="#fff" font-family="Anton, sans-serif">{n}</text>'
                for x, h, c, n in ((-300, 150, "#9aa0a8", 2), (-100, 230, "#d9b13a", 1), (100, 110, "#b0703a", 3)))
    return g(p, s, u)


@dib("hadas")
def hadas(p, u, t):
    """Hadas pequeñas de papel con alas, revoloteando alrededor de (x, y)."""
    x0, y0, rng = p.get("x", 540), p.get("y", 1200), random.Random(4)
    s = [f'<defs>{filtros(u)}</defs>']
    for k in range(p.get("n", 4)):
        x, y = x0 + rng.uniform(-260, 260), y0 + rng.uniform(-200, 160)
        s.append(f'<g id="{u}h{k}"><circle cx="{x:.0f}" cy="{y:.0f}" r="50" fill="#fff6c0" opacity=".4" filter="url(#{u}blur18)"/>'
                 f'<path d="M{x:.0f},{y:.0f} q-50,-40 -40,-70 q30,10 40,60 q10,-50 40,-60 q10,30 -40,70 Z" fill="#e8f4ff" opacity=".85" stroke="#8aa0c0" stroke-width="2"/>'
                 f'<path d="M{x - 8:.0f},{y + 4:.0f} L{x + 8:.0f},{y + 4:.0f} L{x + 14:.0f},{y + 50:.0f} L{x - 14:.0f},{y + 50:.0f} Z" fill="#f2e6f2" stroke="{TIN}" stroke-width="2"/>'
                 f'<circle cx="{x:.0f}" cy="{y - 8:.0f}" r="9" fill="#f6dcc4" stroke="{TIN}" stroke-width="2"/></g>')
        vaiven(t, f"#{u}h{k}", f"y: {rng.uniform(-30, -12):.0f}, x: {rng.uniform(-14, 14):.0f}", periodo=rng.uniform(.8, 1.4))
    return "".join(s)


@dib("camara_antigua")
def camara_antigua(p, u, t):
    """Cámara de cajón de madera sobre trípode, con fuelle y lente."""
    s = (f'<path d="M0,-260 L-110,0 M0,-260 L110,0 M0,-260 L10,0" stroke="#5a3a1e" stroke-width="12" stroke-linecap="round"/>'
         f'<rect x="-90" y="-400" width="110" height="140" fill="#6a4a2a" {O}/><path d="M20,-390 L90,-370 L90,-290 L20,-270 Z" fill="#2a2a2e" {O}/>'
         + "".join(f'<path d="M{30 + k * 15},-385 L{30 + k * 15},-275" stroke="#111" stroke-width="2"/>' for k in range(4))
         + f'<circle cx="100" cy="-330" r="26" fill="#1a1a1e" {O}/><circle cx="100" cy="-330" r="14" fill="#3a5a7a"/><circle cx="94" cy="-336" r="5" fill="#fff" opacity=".7"/>'
         f'<rect x="-70" y="-420" width="40" height="20" fill="#c9a24a" {O3}/>')
    return g(p, s, u)


@dib("muneca_trapo")
def muneca_trapo(p, u, t):
    """Muñeca de trapo sonriente con pelo de lana roja y vestido azul (como la Annabelle real)."""
    s = (f'<path d="M-50,-10 L-40,-120 M50,-10 L40,-120" stroke="#f2f2f2" stroke-width="30" stroke-linecap="round"/>'
         + "".join(f'<path d="M{x - 15},-30 l30,0" stroke="#c0392b" stroke-width="6"/>' for x in (-48, 48))
         + f'<path d="M-80,-120 L-50,-260 L50,-260 L80,-120 Z" fill="#3a6aaa" {O}/><path d="M-60,-130 L60,-130 L50,-230 L-50,-230 Z" fill="#f6f4ee" opacity=".9"/>'
         f'<path d="M-50,-250 L-110,-170 M50,-250 L110,-170" stroke="#f2e6dc" stroke-width="26" stroke-linecap="round"/>'
         f'<circle cx="0" cy="-320" r="70" fill="#f6e6da" {O}/>'
         + "".join(f'<circle cx="{70 * math.cos(a):.0f}" cy="{-320 - 60 * math.sin(a):.0f}" r="20" fill="#d6381e" {O3}/>' for a in [i * math.pi / 9 for i in range(-1, 11)])
         + f'<circle cx="-24" cy="-326" r="9" fill="#111"/><circle cx="24" cy="-326" r="9" fill="#111"/>'
         f'<path d="M-6,-306 L6,-306 L0,-296 Z" fill="#d6381e"/><path d="M-34,-290 Q0,-262 34,-290" stroke="#c0392b" stroke-width="5" fill="none"/>'
         f'<circle cx="-40" cy="-296" r="10" fill="#f08a8a" opacity=".6"/><circle cx="40" cy="-296" r="10" fill="#f08a8a" opacity=".6"/>')
    return g(p, s, u)


@dib("mansion")
def mansion(p, u, t):
    """Casa grande. estilo: victoriana (Winchester, torres y añadidos) | amityville (techo holandés con dos ventanas
    de cuarto de luna que parecen ojos). luces=True enciende ventanas."""
    est, luces = p.get("estilo", "victoriana"), p.get("luces", True)
    vl = "#ffcf6a" if luces else "#2a3040"
    s = [f'<defs>{filtros(u)}</defs>']
    if est == "amityville":
        s.append(f'<rect x="-260" y="-360" width="520" height="360" fill="#e6dcc8" {O}/>'
                 f'<path d="M-300,-360 L-220,-560 L220,-560 L300,-360 Z" fill="#3a2a24" {O}/>'
                 f'<path d="M-200,-560 L0,-700 L200,-560 Z" fill="#2a1d18" {O}/>'
                 f'<path d="M-130,-470 Q-80,-530 -30,-470 Z M30,-470 Q80,-530 130,-470 Z" fill="{vl}" {O}/>'
                 f'<circle cx="-80" cy="-480" r="90" fill="#ffb347" opacity="{.3 if luces else 0}" filter="url(#{u}blur40)"/>'
                 f'<circle cx="80" cy="-480" r="90" fill="#ffb347" opacity="{.3 if luces else 0}" filter="url(#{u}blur40)"/>'
                 + "".join(f'<rect x="{x}" y="-300" width="80" height="110" fill="{vl if k % 2 else "#2a3040"}" {O3}/><rect x="{x - 14}" y="-300" width="12" height="110" fill="#1a3a2a"/>'
                           for k, x in enumerate((-210, -60, 130)))
                 + f'<rect x="-40" y="-150" width="80" height="150" fill="#3a2a1e" {O}/><rect x="-300" y="-40" width="600" height="40" fill="#cfc4b0" {O3}/>')
    else:
        for x, w, h in ((-420, 200, 380), (-230, 260, 520), (30, 220, 460), (240, 200, 360)):
            s.append(f'<rect x="{x}" y="{-h}" width="{w}" height="{h}" fill="#8a7a6a" {O}/>'
                     f'<path d="M{x - 20},{-h} L{x + w / 2},{-h - 140} L{x + w + 20},{-h} Z" fill="#3a2a3a" {O}/>'
                     + "".join(f'<rect x="{x + 30 + c * 70}" y="{-h + 50 + r * 120}" width="40" height="70" fill="{vl if (c + r + x) % 3 else "#2a3040"}" {O3}/>'
                               for c in range(int(w // 80)) for r in range(int(h // 140))))
        s.append(f'<rect x="-70" y="-760" width="140" height="240" fill="#7a6a5a" {O}/><path d="M-90,-760 L0,-900 L90,-760 Z" fill="#2a1d2a" {O}/>'
                 f'<rect x="-30" y="-700" width="60" height="90" fill="{vl}" {O3}/>'
                 f'<path d="M-440,0 L-440,-40 L460,-40 L460,0 Z" fill="#5a4a3a" {O3}/>'
                 + "".join(f'<path d="M{x},-40 l0,-60" stroke="#e6dcc8" stroke-width="8"/>' for x in range(-420, 450, 60)))
    return g(p, "".join(s), u)


@dib("osario")
def osario(p, u, t):
    """Pared de calaveras y huesos ordenados (catacumbas), a toda la toma, con túnel al fondo."""
    rng = random.Random(9)
    s = [f'<defs>{filtros(u)}{rad([(0, "#5a4a30", 1), (1, "#0d0a06", 1)], u + "f", "50%", "45%", "70%")}</defs>',
         f'<rect x="0" y="0" width="1080" height="1920" fill="url(#{u}f)"/>',
         f'<path d="M390,1500 L390,980 Q540,860 690,980 L690,1500 Z" fill="#070504"/>']
    for lado in (-1, 1):
        for fila in range(14):
            yy = 500 + fila * 90
            for c in range(5):
                x = (540 + lado * (200 + c * 80 + fila * 4))
                if fila % 3 == 0:
                    s.append(f'<circle cx="{x:.0f}" cy="{yy:.0f}" r="34" fill="#d8cba8" {O3}/><circle cx="{x - 12:.0f}" cy="{yy - 2:.0f}" r="9" fill="#1a140c"/>'
                             f'<circle cx="{x + 12:.0f}" cy="{yy - 2:.0f}" r="9" fill="#1a140c"/><path d="M{x - 4:.0f},{yy + 14:.0f} l4,-8 l4,8 Z" fill="#1a140c"/>')
                else:
                    s.append(f'<rect x="{x - 40:.0f}" y="{yy - 16:.0f}" width="80" height="32" rx="14" fill="{rng.choice(["#c9b88f", "#b8a67e", "#d8c9a4"])}" {O3}/>'
                             f'<circle cx="{x - 40:.0f}" cy="{yy:.0f}" r="18" fill="#cdbd94" {O3}/>')
    s.append(f'<rect x="0" y="1500" width="1080" height="420" fill="#2a2216"/><path d="M0,1500 L1080,1500" stroke="#000" stroke-width="6"/>')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("antorcha")
def antorcha(p, u, t):
    """Antorcha de pared con fuego que titila."""
    s = (f'<defs>{filtros(u)}</defs><circle cx="0" cy="-200" r="220" fill="#ff8a2a" opacity=".3" filter="url(#{u}blur40)"/>'
         f'<path d="M-14,0 L-24,-150 L24,-150 L14,0 Z" fill="#4a3020" {O}/><rect x="-34" y="-170" width="68" height="26" fill="#3a3a3e" {O3}/>'
         f'<path id="{u}f" d="M0,-330 Q50,-240 30,-180 Q0,-160 -30,-180 Q-50,-240 0,-330 Z" fill="#ff9a2a"/>'
         f'<path d="M0,-270 Q24,-220 14,-190 Q0,-180 -14,-190 Q-24,-220 0,-270 Z" fill="#ffe08a"/>')
    vaiven(t, f"#{u}f", "scaleY: 1.15, scaleX: 0.9, transformOrigin: '50% 100%'", periodo=.3)
    return g(p, s, u)


@dib("mothman")
def mothman(p, u, t):
    """Criatura oscura gigante con alas y ojos rojos brillantes."""
    s = (f'<defs>{filtros(u)}</defs>'
         f'<g id="{u}a"><path d="M-40,-420 Q-300,-560 -460,-380 Q-360,-360 -300,-260 Q-220,-300 -140,-220 Q-90,-300 -40,-260 Z" fill="#0d0b10" stroke="#2a2030" stroke-width="3"/>'
         f'<path d="M40,-420 Q300,-560 460,-380 Q360,-360 300,-260 Q220,-300 140,-220 Q90,-300 40,-260 Z" fill="#0d0b10" stroke="#2a2030" stroke-width="3"/></g>'
         f'<path d="M-60,-440 Q0,-500 60,-440 L70,-180 L40,0 L10,0 L0,-150 L-10,0 L-40,0 L-70,-180 Z" fill="#0a090c"/>'
         f'<circle cx="-24" cy="-420" r="60" fill="#ff1a1a" opacity=".45" filter="url(#{u}blur18)"/><circle cx="24" cy="-420" r="60" fill="#ff1a1a" opacity=".45" filter="url(#{u}blur18)"/>'
         f'<ellipse cx="-24" cy="-420" rx="16" ry="11" fill="#ff3030"/><ellipse cx="24" cy="-420" rx="16" ry="11" fill="#ff3030"/>'
         f'<circle cx="-22" cy="-422" r="4" fill="#fff"/><circle cx="26" cy="-422" r="4" fill="#fff"/>')
    vaiven(t, f"#{u}a", "scaleY: 0.85, transformOrigin: '50% 70%'", periodo=1.1)
    return g(p, s, u)


@dib("puente")
def puente(p, u, t):
    """Puente colgante de acero sobre un río, a lo ancho en y. colapso=True lo quiebra al tiempo `en`."""
    y = p.get("y", 1300)
    s = [f'<g id="{u}p">',
         f'<rect x="-20" y="{y}" width="1120" height="30" fill="#5a6068" {O}/>',
         f'<rect x="230" y="{y - 420}" width="40" height="450" fill="#6a7078" {O}/><rect x="810" y="{y - 420}" width="40" height="450" fill="#6a7078" {O}/>',
         f'<path d="M-20,{y - 200} Q120,{y - 30} 250,{y - 420} Q540,{y - 40} 830,{y - 420} Q960,{y - 30} 1100,{y - 200}" stroke="#8a9098" stroke-width="12" fill="none"/>']
    for x in range(0, 1100, 40):
        dy = abs(((x - 250) % 580) - 290) / 290
        s.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y - 60 - 300 * dy ** 2:.0f}" stroke="#8a9098" stroke-width="3"/>')
    s.append('</g>')
    s.append(f'<rect x="-20" y="{y + 160}" width="1120" height="{1940 - y}" fill="#14202a"/>')
    if p.get("colapso"):
        t.js.append(f'tl.to("#{u}p", {{rotation: 8, y: 260, transformOrigin: "50% 100%", duration: 1.2, ease: "power2.in"}}, {t.at(p.get("en", 1.0))});')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("auto_60")
def auto_60(p, u, t):
    """Auto de los años 60 de costado, con faros encendidos (mirando a la derecha)."""
    col = p.get("color", "#2a4a6a")
    s = (f'<defs>{filtros(u)}{lin(col, "#0d1824", u + "c")}</defs>'
         f'<path d="M-300,-60 L-290,-140 L-160,-150 L-90,-230 L120,-230 L200,-150 L310,-130 L320,-60 Z" fill="url(#{u}c)" {O}/>'
         f'<path d="M-80,-216 L110,-216 L170,-152 L-140,-152 Z" fill="#9ab8d0" opacity=".85" {O3}/><path d="M20,-216 L20,-152" stroke="{TIN}" stroke-width="5"/>'
         f'<path d="M-300,-100 L320,-100" stroke="#d8dce0" stroke-width="5"/>'
         f'<circle cx="-180" cy="-50" r="56" fill="#141414" {O}/><circle cx="-180" cy="-50" r="24" fill="#b8bcc0"/>'
         f'<circle cx="200" cy="-50" r="56" fill="#141414" {O}/><circle cx="200" cy="-50" r="24" fill="#b8bcc0"/>'
         f'<path d="M318,-120 L700,-200 L700,0 L318,-80 Z" fill="#fff6c0" opacity=".25" filter="url(#{u}blur18)"/><circle cx="312" cy="-110" r="12" fill="#fff6c0"/>')
    if p.get("mov") == "avanza":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 200)}'")
    return g(p, s, u)


@dib("diablo_jersey")
def diablo_jersey(p, u, t):
    """Criatura alada con cabeza de caballo, cuernos, patas con pezuñas y cola (leyenda de Nueva Jersey)."""
    s = (f'<defs>{filtros(u)}</defs>'
         f'<g id="{u}a"><path d="M-30,-300 Q-260,-460 -380,-300 Q-300,-300 -260,-220 Q-180,-260 -110,-200 Q-70,-260 -30,-230 Z" fill="#1a1012" stroke="#3a2a2a" stroke-width="3"/>'
         f'<path d="M30,-300 Q260,-460 380,-300 Q300,-300 260,-220 Q180,-260 110,-200 Q70,-260 30,-230 Z" fill="#1a1012" stroke="#3a2a2a" stroke-width="3"/></g>'
         f'<path d="M-40,-320 Q0,-340 40,-320 L50,-140 Q0,-120 -50,-140 Z" fill="#2a1a16" {O}/>'
         f'<path d="M20,-320 Q40,-420 90,-430 Q140,-420 150,-380 L110,-360 Q70,-370 50,-330 Z" fill="#2a1a16" {O}/>'
         f'<path d="M70,-430 L60,-480 L84,-436 M100,-432 L110,-484 L114,-432" stroke="#5a4a3a" stroke-width="7" fill="none"/>'
         f'<circle cx="112" cy="-404" r="7" fill="#ff3030"/>'
         f'<path d="M-30,-140 L-50,-40 L-40,0 M30,-140 L50,-40 L40,0" stroke="#2a1a16" stroke-width="16" fill="none" stroke-linecap="round"/>'
         f'<path d="M-50,0 l20,0 M30,0 l20,0" stroke="#111" stroke-width="10"/>'
         f'<path d="M-40,-160 Q-160,-120 -150,-40 Q-140,0 -180,10" stroke="#2a1a16" stroke-width="8" fill="none"/><path d="M-186,4 l-14,-14 l20,-4 Z" fill="#2a1a16"/>')
    vaiven(t, f"#{u}a", "scaleY: 0.8, transformOrigin: '50% 80%'", periodo=.9)
    if p.get("vuela"):
        vaiven(t, f"#{u}", "y: -40", periodo=1.8)
    return g(p, s, u)


@dib("slender")
def slender(p, u, t):
    """Figura altísima y delgada, sin rostro, de traje negro (borrosa al fondo)."""
    s = (f'<defs>{filtros(u)}</defs><g filter="url(#{u}blur2)" opacity="{p.get("op", .85)}">'
         f'<path d="M-14,0 L-10,-460 L10,-460 L14,0 Z" fill="#0b0b0e"/><path d="M-34,-460 L-26,-860 Q0,-880 26,-860 L34,-460 Z" fill="#0b0b0e"/>'
         f'<path d="M-6,-860 L0,-800 L6,-860 Z" fill="#f2f2f2"/><path d="M-2,-850 L2,-850 L3,-780 L-3,-780 Z" fill="#7a1a1a"/>'
         f'<path d="M-30,-850 Q-60,-700 -70,-430 M30,-850 Q60,-700 70,-430" stroke="#0b0b0e" stroke-width="16" fill="none"/>'
         f'<ellipse cx="0" cy="-920" rx="34" ry="46" fill="#ecebe6"/></g>')
    return g(p, s, u)


@dib("gigante_piedra")
def gigante_piedra(p, u, t):
    """Gigante de piedra (yeso) de 3 m acostado en una fosa de tierra."""
    s = (f'<defs>{lin("#bdb6a6", "#7a7466", u + "p")}</defs>'
         f'<ellipse cx="0" cy="-40" rx="470" ry="90" fill="#3a2a1a" {O}/>'
         f'<path d="M-380,-70 Q-420,-110 -380,-140 Q-330,-160 -300,-120 L-250,-110 Q-150,-150 0,-140 Q150,-150 280,-120 L380,-110 Q420,-90 380,-70 L280,-60 Q150,-40 0,-50 Q-150,-40 -280,-60 Z" fill="url(#{u}p)" {O}/>'
         f'<path d="M-120,-130 Q-100,-90 -120,-60 M60,-140 Q80,-100 60,-55 M-300,-120 Q-280,-110 -300,-90" stroke="#5a5448" stroke-width="3" fill="none"/>'
         f'<path d="M-200,-90 Q-140,-80 -60,-90 M120,-90 Q200,-80 260,-90" stroke="#fff" stroke-opacity=".25" stroke-width="5" fill="none"/>')
    return g(p, s, u)


@dib("trigal")
def trigal(p, u, t):
    """Campo de trigo en perspectiva desde y hacia abajo, con círculo gigante (circulo=True)."""
    y0, rng = p.get("y", 1250), random.Random(6)
    noche = p.get("noche", False)
    c1, c2 = ("#6a6a3a", "#2a2a14") if noche else ("#e6c25a", "#a8822a")
    s = [f'<defs>{lin(c1, c2, u + "t")}</defs><rect x="-20" y="{y0}" width="1120" height="{1940 - y0}" fill="url(#{u}t)"/>']
    for k in range(70):
        yy = y0 + (k / 70) ** 1.6 * (1920 - y0)
        s.append(f'<path d="M-20,{yy:.0f} L1100,{yy:.0f}" stroke="#000" stroke-opacity=".08" stroke-width="{1 + k / 20:.1f}"/>')
    if p.get("circulo", True):
        cy = y0 + (1920 - y0) * .45
        for r, op in ((380, .9), (300, 0), (220, .9), (120, 0), (60, .9)):
            s.append(f'<ellipse cx="540" cy="{cy:.0f}" rx="{r}" ry="{r * .3:.0f}" fill="{"#c9a44a" if not noche else "#4a4a26"}" opacity="{op}" stroke="{c2}" stroke-width="3"/>')
        s.append(f'<ellipse cx="540" cy="{cy:.0f}" rx="300" ry="90" fill="none" stroke="{c1}" stroke-width="40"/>')
    for k in range(60):
        x, yy = rng.uniform(0, 1080), rng.uniform(1700, 1920)
        s.append(f'<path d="M{x:.0f},{yy + 120:.0f} Q{x + 6:.0f},{yy + 40:.0f} {x + 12:.0f},{yy:.0f}" stroke="{c2}" stroke-width="3" fill="none"/><ellipse cx="{x + 12:.0f}" cy="{yy - 12:.0f}" rx="5" ry="16" fill="{c1}"/>')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("naipes")
def naipes(p, u, t):
    """Abanico de cartas hanafuda pintadas (flores, luna, grulla)."""
    motivos = ['<circle cx="0" cy="-110" r="34" fill="#f2f2f2"/><rect x="-60" y="-80" width="120" height="70" fill="#c0392b"/>',
               '<path d="M-40,-60 Q0,-170 40,-60" stroke="#2a6a2a" stroke-width="8" fill="none"/><circle cx="-20" cy="-120" r="16" fill="#e05a8a"/><circle cx="20" cy="-100" r="14" fill="#e05a8a"/>',
               '<path d="M-50,-40 L0,-150 L50,-40 Z" fill="#2a3a6a"/><circle cx="0" cy="-160" r="16" fill="#d6381e"/>',
               '<circle cx="-10" cy="-120" r="24" fill="#c0392b"/><path d="M-60,-60 Q0,-90 60,-60" stroke="#111" stroke-width="10"/>']
    s = "".join(f'<g transform="rotate({(k - 1.5) * 16})"><rect x="-70" y="-200" width="140" height="200" rx="10" fill="#f4e8cc" {O}/>'
                f'<rect x="-60" y="-190" width="120" height="180" fill="#1a1a1a"/><g>{m}</g></g>' for k, m in enumerate(motivos))
    return g(p, s, u)


@dib("farol")
def farol(p, u, t):
    """Farol de papel rojo colgante (Japón), con luz cálida y vaivén."""
    s = (f'<defs>{filtros(u)}</defs><line x1="0" y1="-400" x2="0" y2="-240" stroke="#2a1a10" stroke-width="4"/>'
         f'<circle cx="0" cy="-160" r="150" fill="#ff8a3a" opacity=".3" filter="url(#{u}blur40)"/>'
         f'<rect x="-40" y="-250" width="80" height="16" fill="#1a1a1a"/><rect x="-40" y="-70" width="80" height="16" fill="#1a1a1a"/>'
         f'<ellipse cx="0" cy="-160" rx="80" ry="100" fill="#d83a2a" {O}/>'
         + "".join(f'<path d="M-80,{-160 + k * 22} Q0,{-150 + k * 22} 80,{-160 + k * 22}" stroke="#8a1a10" stroke-width="2" fill="none"/>' for k in range(-3, 4))
         + '<text x="0" y="-140" font-size="60" text-anchor="middle" fill="#1a1a1a" font-family="serif">任</text>')
    vaiven(t, f"#{u}", "rotation: 5, transformOrigin: '50% 0%'", periodo=2.0)
    return g(p, s, u, origen=(0, -400))


@dib("tetris")
def tetris(p, u, t):
    """Computadora soviética con pantalla verde y piezas de bloques cayendo (sin marcas)."""
    s = [f'<defs>{filtros(u)}</defs><rect x="-260" y="-520" width="520" height="440" rx="20" fill="#cfc6b0" {O}/>'
         f'<rect x="-210" y="-480" width="420" height="330" rx="16" fill="#0a1a0c" {O3}/>'
         f'<rect x="-210" y="-480" width="420" height="330" rx="16" fill="#2aff6a" opacity=".07"/>'
         f'<rect x="-300" y="-80" width="600" height="80" fill="#b8ae98" {O}/>' + "".join(f'<rect x="{-280 + k * 46}" y="-64" width="38" height="22" fill="#e6dcc8" {O3}/>' for k in range(12))]
    col = "#2aff6a"
    piezas = [[(0, 0), (1, 0), (2, 0), (1, 1)], [(0, 0), (0, 1), (1, 1), (2, 1)], [(0, 0), (1, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (2, 0), (3, 0)]]
    for k, pz in enumerate(piezas):
        x0, y0 = -150 + k * 80, -460
        s.append(f'<g id="{u}p{k}">' + "".join(f'<rect x="{x0 + a * 26}" y="{y0 + b * 26}" width="24" height="24" fill="none" stroke="{col}" stroke-width="3"/>' for a, b in pz) + '</g>')
        anim(t, f"#{u}p{k}", "{y: 0}", f"{{y: {200 - k * 26}, duration: {max(.5, t.dur * (.5 + k * .12)):.2f}, ease: 'steps(8)'}}")
    s.append("".join(f'<rect x="{-200 + c * 26}" y="{-200 + r * 26}" width="24" height="24" fill="none" stroke="{col}" stroke-width="3"/>'
                     for r in range(2) for c in range(15) if (c + r * 3) % 7))
    return g(p, "".join(s), u)


@dib("osciloscopio")
def osciloscopio(p, u, t):
    """Osciloscopio de 1958 con pantalla redonda verde: tenis visto de costado (pelota que rebota) y dos controles."""
    s = (f'<defs>{filtros(u)}</defs><rect x="-260" y="-560" width="520" height="460" rx="20" fill="#5a6068" {O}/>'
         f'<circle cx="-40" cy="-330" r="180" fill="#04140a" {O}/><circle cx="-40" cy="-330" r="180" fill="#2aff6a" opacity=".08"/>'
         f'<path d="M-200,-240 L120,-240 M-40,-240 L-40,-300" stroke="#5cff8a" stroke-width="4"/>'
         f'<circle id="{u}b" cx="-170" cy="-300" r="9" fill="#bfffcf" filter="url(#{u}blur2)"/>'
         + "".join(f'<circle cx="170" cy="{-480 + k * 80}" r="22" fill="#1a1a1e" {O3}/>' for k in range(4))
         + "".join(f'<g transform="translate({x},0)"><rect x="-50" y="-60" width="100" height="60" rx="10" fill="#2a2a2e" {O}/><circle cx="0" cy="-30" r="18" fill="#c9c9c9" {O3}/></g>' for x in (-180, 180)))
    t.js.append(f'tl.to("#{u}b", {{keyframes: [{{x: 120, y: -50, duration: .5}}, {{x: 240, y: 60, duration: .5}}, {{x: 120, y: -50, duration: .5}}, {{x: 0, y: 0, duration: .5}}], repeat: {max(1, int(t.dur / 2))}, ease: "sine.inOut"}}, {t.at(0)});')
    return g(p, s, u)


@dib("tv_tubo")
def tv_tubo(p, u, t):
    """Televisor de tubo. destellos=True alterna rojo y azul muy rápido; si no, muestra `color` de pantalla."""
    s = (f'<defs>{filtros(u)}</defs><rect x="-260" y="-460" width="520" height="400" rx="30" fill="#3a3a40" {O}/>'
         f'<rect id="{u}s" x="-220" y="-420" width="380" height="320" rx="30" fill="{p.get("color", "#2a3a5a")}" {O3}/>'
         f'<rect x="-220" y="-420" width="380" height="320" rx="30" fill="url(#{u}g)" opacity=".0"/>'
         f'<circle cx="210" cy="-380" r="16" fill="#1a1a1e"/><circle cx="210" cy="-330" r="16" fill="#1a1a1e"/>'
         f'<path d="M-200,-60 L-220,0 M180,-60 L200,0" stroke="#2a2a2e" stroke-width="12"/>'
         f'<path d="M-180,-400 Q-100,-410 -60,-380" stroke="#fff" stroke-opacity=".25" stroke-width="6" fill="none"/>')
    if p.get("destellos"):
        s += f'<rect id="{u}h" x="-1000" y="-1600" width="2200" height="2200" fill="#ff2a2a" opacity="0" style="mix-blend-mode:screen"/>'
        n = int(min(5, t.dur) / .12)
        t.js.append(f'tl.to("#{u}s", {{keyframes: [{{fill: "#ff2020", duration: .06}}, {{fill: "#2050ff", duration: .06}}], repeat: {n}}}, {t.at(p.get("en", .3))});')
        t.js.append(f'tl.to("#{u}h", {{keyframes: [{{opacity: .25, fill: "#ff2020", duration: .06}}, {{opacity: .2, fill: "#2050ff", duration: .06}}], repeat: {n}}}, {t.at(p.get("en", .3))});')
    return g(p, s, u)


@dib("notas")
def notas(p, u, t):
    """Notas musicales flotando (distorsion=True las tiñe de morado y las hace temblar)."""
    rng, dist = random.Random(8), p.get("distorsion", False)
    col = "#b47aff" if dist else p.get("color", "#ffffff")
    s = []
    for k in range(p.get("n", 7)):
        x, y = rng.uniform(150, 930), rng.uniform(500, 1300)
        s.append(f'<g id="{u}n{k}"><ellipse cx="{x:.0f}" cy="{y:.0f}" rx="22" ry="16" fill="{col}" transform="rotate(-20 {x:.0f} {y:.0f})"/>'
                 f'<path d="M{x + 20:.0f},{y:.0f} L{x + 20:.0f},{y - 90:.0f} Q{x + 50:.0f},{y - 70:.0f} {x + 48:.0f},{y - 40:.0f}" stroke="{col}" stroke-width="7" fill="none"/></g>')
        vaiven(t, f"#{u}n{k}", f"y: {rng.uniform(-40, -15):.0f}, rotation: {rng.uniform(-14, 14) if dist else 4:.0f}", periodo=rng.uniform(.25, .5) if dist else rng.uniform(1.2, 2))
    return "".join(s)


@dib("torre_lapidas")
def torre_lapidas(p, u, t):
    """Pueblo pixelado morado con torre de lápidas bajo la luna (estilo 8 bits genérico)."""
    px = 30
    s = [f'<rect x="0" y="0" width="1080" height="1920" fill="#2a1a3a"/><rect x="780" y="240" width="150" height="150" fill="#f2e6ff"/>']
    for r in range(12):
        for c in range(7):
            x, y = 330 + c * px * 2, 1500 - r * px * 2
            s.append(f'<rect x="{x}" y="{y}" width="{px * 2 - 4}" height="{px * 2 - 4}" fill="{"#6a4a8a" if (r + c) % 2 else "#5a3a7a"}"/>')
    s.append('<rect x="300" y="620" width="480" height="80" fill="#3a2a4a"/><rect x="420" y="540" width="240" height="80" fill="#3a2a4a"/>')
    for k in range(10):
        x, y = 120 + (k % 5) * 200, 1620 + (k // 5) * 150
        s.append(f'<rect x="{x}" y="{y}" width="60" height="90" fill="#a8a0b8"/><rect x="{x + 20}" y="{y + 20}" width="20" height="40" fill="#6a6078"/>')
    s.append('<rect x="0" y="1590" width="1080" height="12" fill="#4a3a5a"/>')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("chimenea")
def chimenea(p, u, t):
    """Chimenea de ladrillo con fuego, repisa y medias colgadas (Navidad si navidad=True)."""
    s = [f'<defs>{filtros(u)}</defs><rect x="-300" y="-520" width="600" height="520" fill="#8a3a2a" {O}/>']
    s.append("".join(f'<rect x="{-300 + (r % 2) * 30 + c * 60}" y="{-520 + r * 30}" width="56" height="26" fill="#a24a34" opacity=".8"/>' for r in range(17) for c in range(10) if -300 + (r % 2) * 30 + c * 60 < 270))
    s.append(f'<rect x="-340" y="-540" width="680" height="40" fill="#5a3a22" {O}/><path d="M-170,0 L-170,-300 Q0,-380 170,-300 L170,0 Z" fill="#140a06" {O}/>'
             f'<circle cx="0" cy="-100" r="200" fill="#ff8a2a" opacity=".35" filter="url(#{u}blur40)"/>'
             f'<path id="{u}f" d="M-90,-20 Q-100,-120 -40,-180 Q-30,-120 0,-200 Q30,-130 50,-170 Q100,-110 90,-20 Z" fill="#ff9a2a"/>'
             f'<path d="M-50,-20 Q-50,-90 -10,-120 Q20,-80 50,-20 Z" fill="#ffe08a"/>'
             f'<rect x="-110" y="-30" width="220" height="24" rx="10" fill="#4a2a14" {O3}/>')
    vaiven(t, f"#{u}f", "scaleY: 1.12, transformOrigin: '50% 100%'", periodo=.35)
    if p.get("navidad", True):
        for k, x in enumerate((-220, -80, 80, 220)):
            s.append(f'<path d="M{x - 26},-500 L{x + 20},-500 L{x + 20},-400 L{x + 44},-380 L{x + 30},-350 L{x - 26},-380 Z" fill="{["#c0392b", "#2a7a3a", "#c0392b", "#2a7a3a"][k]}" {O3}/>'
                     f'<rect x="{x - 30}" y="-510" width="54" height="20" fill="#f6f4ee" {O3}/>')
    return g(p, "".join(s), u)


@dib("butacas")
def butacas(p, u, t):
    """Primer plano: filas de butacas de cine/teatro vistas de atrás con siluetas de público."""
    rng = random.Random(5)
    s = []
    for fila in range(3):
        y, k = 1560 + fila * 150, 1 + fila * .3
        for x in range(-60, 1140, int(150 * k)):
            s.append(f'<rect x="{x}" y="{y}" width="{130 * k:.0f}" height="{200 * k:.0f}" rx="18" fill="#6a1a22" {O3}/>')
            if rng.random() < .75:
                s.append(f'<circle cx="{x + 65 * k:.0f}" cy="{y - 40 * k:.0f}" r="{38 * k:.0f}" fill="#0b0b0e"/><path d="M{x + 10 * k:.0f},{y + 10:.0f} Q{x + 65 * k:.0f},{y - 20 * k:.0f} {x + 120 * k:.0f},{y + 10:.0f}" fill="#0b0b0e"/>')
    return f'<g id="{u}">{"".join(s)}</g>'


@dib("arbusto")
def arbusto(p, u, t):
    """Arbusto de jardín; paquete=True asoma por delante un paquete envuelto en papel de diario con brillo dorado."""
    s = [f'<defs>{filtros(u)}</defs>']
    rng = random.Random(1)
    for k in range(14):
        a = k / 14 * math.pi
        s.append(f'<circle cx="{-200 + 400 * k / 13 + rng.uniform(-20, 20):.0f}" cy="{-60 - 180 * math.sin(a) + rng.uniform(-20, 20):.0f}" r="{rng.uniform(70, 100):.0f}" fill="{rng.choice(["#2e5a22", "#3a6a2a", "#264a1c"])}"/>')
    s.append("".join(f'<ellipse cx="{rng.uniform(-220, 220):.0f}" cy="{rng.uniform(-280, -40):.0f}" rx="16" ry="8" fill="#5a8a3a" opacity=".7"/>' for _ in range(30)))
    s.append('<path d="M-260,0 L260,0" stroke="#1a2a10" stroke-width="10"/>')
    if p.get("paquete"):
        s.append(f'<circle cx="60" cy="-120" r="60" fill="#ffd36a" opacity=".45" filter="url(#{u}blur18)"/>'
                 f'<path d="M-40,-10 L-50,-110 L90,-120 L100,-10 Z" fill="#d8d2c0" {O}/>'
                 + "".join(f'<path d="M-40,{-100 + k * 16} l130,-4" stroke="#555" stroke-width="2"/>' for k in range(6))
                 + '<path d="M50,-118 L70,-118 L66,-150 L54,-150 Z" fill="#e8c24a"/>')
    return g(p, "".join(s), u)


@dib("ola")
def ola(p, u, t):
    """Ola gigante (tsunami) que avanza desde la izquierda."""
    s = (f'<defs>{lin("#2a6a8a", "#0a2a3a", u + "o")}</defs>'
         f'<path d="M-700,0 L-700,-600 Q-300,-820 0,-700 Q220,-620 180,-480 Q140,-560 40,-540 Q120,-420 60,-300 Q200,-200 400,0 Z" fill="url(#{u}o)" {O}/>'
         f'<path d="M0,-700 Q220,-620 180,-480 Q140,-560 40,-540" stroke="#e6f4ff" stroke-width="22" fill="none" stroke-linecap="round"/>'
         + "".join(f'<circle cx="{random.Random(k).uniform(0, 220):.0f}" cy="{random.Random(k + 1).uniform(-700, -480):.0f}" r="{random.Random(k + 2).uniform(6, 16):.0f}" fill="#fff" opacity=".8"/>' for k in range(16)))
    deriva(t, f"#{u}", f"x: '+={p.get('avance', 300)}'", ease="power1.in")
    return g(p, s, u)


@dib("sabana")
def sabana(p, u, t):
    """Sábana blanca que se levanta sola y flota en el aire (fantasma de la granja Bell)."""
    s = (f'<defs>{filtros(u)}</defs><g id="{u}s"><path d="M-220,0 Q-240,-120 -160,-180 Q0,-240 160,-180 Q240,-120 220,0 Q180,-40 140,0 Q100,-50 60,0 Q20,-50 -20,0 Q-60,-50 -100,0 Q-140,-50 -180,0 Z" '
         f'fill="#f2f0ea" opacity=".92" {O3}/><path d="M-120,-160 Q-60,-60 -80,-10 M80,-170 Q40,-80 60,-10" stroke="#c8c4b8" stroke-width="5" fill="none"/></g>')
    anim(t, f"#{u}s", "{y: 80, rotation: 0}", f"{{y: -160, rotation: -6, duration: {max(.6, t.dur * .7):.2f}, ease: 'sine.inOut'}}", dt=p.get("en", .4))
    return g(p, s, u)


@dib("craneo_fosil")
def craneo_fosil(p, u, t):
    """Cráneo humano marrón con mandíbula de simio (fraude de Piltdown), sobre mesa, con lupa opcional."""
    s = (f'<defs>{lin("#a8784a", "#5a3a1e", u + "c", 0)}</defs>'
         f'<path d="M-140,-120 Q-150,-280 0,-300 Q150,-290 150,-150 Q140,-100 100,-90 L-90,-90 Q-130,-90 -140,-120 Z" fill="url(#{u}c)" {O}/>'
         f'<ellipse cx="-50" cy="-170" rx="34" ry="28" fill="#2a1a0e"/><ellipse cx="50" cy="-170" rx="34" ry="28" fill="#2a1a0e"/>'
         f'<path d="M-10,-140 L0,-112 L10,-140 Z" fill="#2a1a0e"/>'
         f'<path d="M-110,-80 Q-120,-10 -60,0 L80,0 Q140,-10 130,-80 L100,-90 Q80,-40 0,-40 Q-80,-40 -90,-80 Z" fill="#7a4e26" {O}/>'
         + "".join(f'<rect x="{-60 + k * 22}" y="-62" width="16" height="20" fill="#d8c89a" {O3}/>' for k in range(6))
         + '<path d="M-120,-230 Q-60,-260 20,-250" stroke="#fff" stroke-opacity=".2" stroke-width="6" fill="none"/>'
         '<path d="M-150,-200 Q-80,-190 -40,-230 M40,-280 Q60,-230 110,-220" stroke="#3a2210" stroke-width="2" fill="none"/>')
    if p.get("lupa"):
        s += f'<circle cx="230" cy="-140" r="70" fill="#cfe6ff" fill-opacity=".25" stroke="#3a3a3e" stroke-width="12"/><path d="M280,-90 L360,0" stroke="#5a3a1e" stroke-width="20" stroke-linecap="round"/>'
    return g(p, s, u)


@dib("pasaporte")
def pasaporte(p, u, t):
    """Pasaporte antiguo abierto de un país (texto), con sellos."""
    pais = p.get("pais", "TAURED")
    s = (f'<rect x="-260" y="-340" width="520" height="340" rx="14" fill="#5a1a22" {O}/>'
         f'<rect x="-246" y="-326" width="240" height="312" fill="#efe6cf"/><rect x="6" y="-326" width="240" height="312" fill="#f4ecd8"/>'
         f'<text x="-126" y="-250" font-size="34" font-weight="900" text-anchor="middle" fill="#5a1a22" font-family="serif">{pais}</text>'
         f'<rect x="-200" y="-220" width="140" height="170" fill="#c8bca0" {O3}/><circle cx="-130" cy="-170" r="34" fill="#8a7a62"/><path d="M-185,-60 Q-130,-130 -75,-60 Z" fill="#8a7a62"/>'
         + "".join(f'<path d="M30,{-290 + k * 30} l190,0" stroke="#9a8a6a" stroke-width="2"/>' for k in range(8))
         + '<circle cx="130" cy="-100" r="50" fill="none" stroke="#2a4a8a" stroke-width="6" opacity=".7"/><text x="130" y="-90" font-size="22" text-anchor="middle" fill="#2a4a8a" opacity=".8" font-family="sans-serif">1954</text>')
    return g(p, s, u)


@dib("momia_gto")
def momia_gto(p, u, t):
    """Momia natural de pie (Guanajuato), piel reseca y restos de ropa, boca abierta."""
    s = (f'<defs>{lin("#a89070", "#6a5238", u + "p", 0)}</defs>'
         f'<path d="M-40,0 L-34,-200 L-4,-200 L-8,0 Z M8,0 L4,-200 L34,-200 L40,0 Z" fill="url(#{u}p)" {O}/>'
         f'<path d="M-60,-200 L-50,-400 Q0,-420 50,-400 L60,-200 Z" fill="url(#{u}p)" {O}/>'
         + "".join(f'<path d="M-40,{-380 + k * 26} Q0,{-370 + k * 26} 40,{-380 + k * 26}" stroke="#4a3a28" stroke-width="2" fill="none"/>' for k in range(6))
         + f'<path d="M-62,-300 L-56,-200 L60,-200 L64,-300 Q30,-260 0,-290 Q-30,-260 -62,-300 Z" fill="#5a4a6a" opacity=".85" {O3}/>'
         f'<path d="M-50,-390 Q-90,-300 -70,-200 M50,-390 Q90,-300 70,-200" stroke="#7a6248" stroke-width="22" stroke-linecap="round" fill="none"/>'
         f'<ellipse cx="0" cy="-460" rx="44" ry="56" fill="url(#{u}p)" {O}/>'
         f'<ellipse cx="-16" cy="-470" rx="10" ry="12" fill="#1a120a"/><ellipse cx="16" cy="-470" rx="10" ry="12" fill="#1a120a"/>'
         f'<ellipse cx="0" cy="-424" rx="14" ry="20" fill="#1a120a"/><path d="M-40,-500 Q0,-530 40,-500" stroke="#3a2a1a" stroke-width="10" fill="none"/>')
    return g(p, s, u)


@dib("polybius")
def polybius(p, u, t):
    """Máquina arcade negra sin marcas con espirales psicodélicas que giran en la pantalla."""
    s = (f'<defs>{filtros(u)}</defs><path d="M-160,0 L-160,-560 L-120,-640 L120,-640 L160,-560 L160,0 Z" fill="#0d0d10" {O}/>'
         f'<rect x="-120" y="-540" width="240" height="200" fill="#000" {O3}/>'
         f'<g id="{u}e" transform="translate(0,-440)">' + "".join(f'<path d="M0,0 ' + " ".join(f'L{r * math.cos(a + k * 2.1):.0f},{r * math.sin(a + k * 2.1) * .8:.0f}' for r, a in [(i * 4, i * .35) for i in range(1, 26)]) + f'" stroke="{c}" stroke-width="5" fill="none"/>'
                                                                for k, c in enumerate(["#ff3df0", "#3df5ff", "#fff23d"])) + '</g>'
         f'<rect x="-120" y="-540" width="240" height="200" fill="#ff3df0" opacity=".2" filter="url(#{u}blur18)"/>'
         f'<path d="M-160,-320 L160,-320 L180,-260 L-180,-260 Z" fill="#1a1a1e" {O}/><circle cx="-60" cy="-300" r="12" fill="#ff3030"/><circle cx="40" cy="-296" r="10" fill="#3df5ff"/><circle cx="80" cy="-296" r="10" fill="#3df5ff"/>'
         f'<rect x="-40" y="-180" width="80" height="40" fill="#1a1a1e" {O3}/>')
    t.js.append(f'tl.to("#{u}e", {{rotation: 720, svgOrigin: "0 -440", duration: {max(.5, t.dur):.2f}, ease: "none"}}, {t.at(0)});')
    return g(p, s, u)


@dib("disquete")
def disquete(p, u, t):
    """Disquete de 5¼ (negro, con etiqueta)."""
    s = (f'<rect x="-150" y="-300" width="300" height="300" rx="10" fill="#141416" {O}/><circle cx="0" cy="-150" r="40" fill="#5a5a5e" {O3}/>'
         f'<rect x="-14" y="-110" width="28" height="100" rx="12" fill="#3a3a3e"/><rect x="-120" y="-290" width="240" height="70" fill="#f2efe6"/>'
         f'<path d="M-110,-270 l180,0 M-110,-246 l140,0" stroke="#2a4a8a" stroke-width="4"/>')
    return g(p, s, u)
