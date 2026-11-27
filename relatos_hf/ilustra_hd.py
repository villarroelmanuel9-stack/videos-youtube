"""
Ilustraciones «HD»: el nivel más pulido. Usan filtros SVG (texturas de ruido, desenfoques para brillo y
profundidad de campo, reflejos ondulados) además de los degradados. Mismo contrato que ilustra.py.
"""
from __future__ import annotations

import math
import random

from ilustra import TINTA, anim, deriva, dib, g, lin, rad, vaiven

TIN = "#0d1120"


def filtros(u):
    """Filtros comunes por toma (se definen una vez por elemento con prefijo propio)."""
    return (f'<filter id="{u}blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>'
            f'<filter id="{u}blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>'
            f'<filter id="{u}blur18" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="18"/></filter>'
            f'<filter id="{u}blur40" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="40"/></filter>')


# ============================================================================ cielo nocturno HD
@dib("cielo_hd")
def cielo_hd(p, u, t):
    hora = p.get("hora", "noche")
    hz = p.get("horizonte", 1150)
    rng = random.Random(7)
    if hora == "noche":
        stops = [("0", "#01030a"), (".45", "#071330"), (".8", "#132a58"), ("1", "#2a4a80")]
    elif hora == "atardecer":
        stops = [("0", "#1d1b4a"), (".4", "#5a2e6a"), (".7", "#d9616b"), (".88", "#ffa35c"), ("1", "#ffd48a")]
    else:
        stops = [("0", "#2f7fd0"), (".6", "#8cc8f2"), ("1", "#e6f4ff")]
    grad = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    out = [f'<defs>{filtros(u)}<linearGradient id="{u}g" x1="0" y1="0" x2="0" y2="1">{grad}</linearGradient>'
           f'<filter id="{u}via" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.006 0.014" numOctaves="5" seed="4"/>'
           f'<feColorMatrix values="0 0 0 0 .78  0 0 0 0 .84  0 0 0 0 1  0 0 0 1.6 -.72"/></filter>'
           f'<radialGradient id="{u}vm" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
           f'<mask id="{u}m"><ellipse cx="540" cy="520" rx="820" ry="190" fill="url(#{u}vm)" transform="rotate(-28 540 520)"/></mask></defs>',
           f'<rect x="-200" y="-200" width="1480" height="{hz + 260}" fill="url(#{u}g)"/>']
    if hora == "noche":
        out.append(f'<rect x="-200" y="-200" width="1480" height="{hz}" filter="url(#{u}via)" mask="url(#{u}m)" opacity=".55"/>')
        est = []
        for k in range(260):
            x, y = rng.uniform(-150, 1230), rng.uniform(-150, hz * .85)
            r = rng.choice([.9, 1.2, 1.5, 1.9, 2.4]) if k > 12 else 3.2
            est.append(f'<circle class="{u}e{k % 4}" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{rng.uniform(.35, 1):.2f}"/>')
            if k <= 12:
                est.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="#cfe0ff" opacity=".45" filter="url(#{u}blur6)"/>'
                           f'<path d="M{x - 14:.0f},{y:.0f} L{x + 14:.0f},{y:.0f} M{x:.0f},{y - 14:.0f} L{x:.0f},{y + 14:.0f}" stroke="#fff" stroke-width="1.2" opacity=".7"/>')
        out.append("".join(est))
        for k in range(4):
            vaiven(t, f".{u}e{k}", "opacity: 0.2", periodo=1.0 + k * .45, dt=.1 * k)
    if p.get("astro") == "luna":
        ax, ay, ar = p.get("astro_x", 800), p.get("astro_y", 400), p.get("astro_r", 70)
        out.append(f'<defs><filter id="{u}lt"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="4" seed="9"/>'
                   f'<feColorMatrix values="0 0 0 0 .55 0 0 0 0 .53 0 0 0 0 .46 0 0 0 .9 -.25"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
                   f'{rad([(0, "#fffdf2", 1), (.75, "#ece4c8", 1), (1, "#bdb396", 1)], u + "mo", "38%", "36%", "64%")}</defs>'
                   f'<circle cx="{ax}" cy="{ay}" r="{ar * 5}" fill="#fff6d6" opacity=".10" filter="url(#{u}blur40)"/>'
                   f'<circle cx="{ax}" cy="{ay}" r="{ar * 2.2}" fill="#fff6d6" opacity=".22" filter="url(#{u}blur40)"/>'
                   f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="url(#{u}mo)"/>'
                   f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="#fff" filter="url(#{u}lt)" opacity=".8"/>')
    if hora == "atardecer" and p.get("astro") == "sol":
        ax, ay, ar = p.get("astro_x", 760), p.get("astro_y", 900), p.get("astro_r", 80)
        out.append(f'<circle cx="{ax}" cy="{ay}" r="{ar * 4}" fill="#ffb35c" opacity=".35" filter="url(#{u}blur40)"/>'
                   f'<circle cx="{ax}" cy="{ay}" r="{ar * 1.6}" fill="#ffe0a0" opacity=".6" filter="url(#{u}blur18)"/>'
                   f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="#fff4d6"/>')
    # nubes suaves cerca del horizonte, iluminadas por la luna o el sol
    col_n = {"noche": "#5b6f9a", "atardecer": "#ff9c7a", "dia": "#ffffff"}.get(hora, "#8a96aa")
    for k in range(p.get("nubes", 6)):
        cx, cy, w = rng.uniform(-150, 1150), rng.uniform(hz * .45, hz * .85), rng.uniform(260, 520)
        out.append(f'<g id="{u}n{k}" opacity="{.35 if hora == "noche" else .7}" filter="url(#{u}blur6)">'
                   f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{w:.0f}" ry="{w * .09:.0f}" fill="{col_n}"/>'
                   f'<ellipse cx="{cx - w * .3:.0f}" cy="{cy - w * .06:.0f}" rx="{w * .45:.0f}" ry="{w * .1:.0f}" fill="{col_n}"/></g>')
        deriva(t, f"#{u}n{k}", f"x: {rng.choice([-1, 1]) * rng.uniform(40, 90):.0f}")
    return "".join(out)


# ============================================================================ mar HD con reflejo de luna
@dib("mar_hd")
def mar_hd(p, u, t):
    hz = p.get("horizonte", 1150)
    hora = p.get("hora", "noche")
    c = {"noche": ("#0e2347", "#030814"), "atardecer": ("#4a3a6a", "#120e24"), "dia": ("#3a8fd0", "#0a3462")}[hora]
    brillo = {"noche": "#dbe8ff", "atardecer": "#ffc49a", "dia": "#ffffff"}[hora]
    rx = p.get("reflejo_x", 800)
    rng = random.Random(3)
    out = [f'<defs>{filtros(u)}{lin(c[0], c[1], u + "m")}'
           f'<filter id="{u}ola" x="0" y="0" width="100%" height="100%"><feTurbulence type="turbulence" baseFrequency="0.0035 0.05" numOctaves="3" seed="2"/>'
           f'<feColorMatrix values="0 0 0 0 .75 0 0 0 0 .85 0 0 0 0 1 0 0 0 2.2 -1.15"/></filter>'
           f'<linearGradient id="{u}mk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".15"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient>'
           f'<mask id="{u}mm"><rect x="-300" y="{hz}" width="1680" height="{2000 - hz}" fill="url(#{u}mk)"/></mask></defs>',
           f'<rect x="-300" y="{hz}" width="1680" height="{2100 - hz}" fill="url(#{u}m)"/>',
           f'<g mask="url(#{u}mm)"><rect id="{u}tx" x="-500" y="{hz}" width="2100" height="{2100 - hz}" filter="url(#{u}ola)" opacity=".35"/></g>',
           f'<rect x="-300" y="{hz - 2}" width="1680" height="5" fill="{brillo}" opacity=".25" filter="url(#{u}blur2)"/>']
    deriva(t, f"#{u}tx", "x: 140")
    if hora != "dia":
        refl = []
        for k in range(46):
            y = hz + 8 + k ** 1.55 * 4.2
            w = rng.uniform(30, 120) * (1 + k / 22)
            refl.append(f'<rect class="{u}r{k % 3}" x="{rx - w / 2 + rng.uniform(-24, 24) * (1 + k / 18):.0f}" y="{y:.0f}" width="{w:.0f}" height="{2 + k / 12:.1f}" rx="2" fill="{brillo}" opacity="{max(.12, .85 - k * .016):.2f}"/>')
        out.append(f'<g filter="url(#{u}blur2)">{"".join(refl)}</g>')
        for k in range(3):
            vaiven(t, f".{u}r{k}", f"x: {(-1) ** k * 14}, opacity: 0.25", periodo=.9 + k * .3)
    return "".join(out)


# ============================================================================ iceberg HD
@dib("iceberg_hd")
def iceberg_hd(p, u, t):
    d = (f'<defs>{filtros(u)}{lin("#ffffff", "#cfeaf7", u + "a", 0)}{lin("#b6dcf0", "#6aa6cf", u + "b", 0)}{lin("#7fb7dc", "#2f6f9f", u + "c", 0)}'
         f'{lin("#5fa8c9", "#0e3b5a", u + "w")}'
         f'<filter id="{u}nv"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="3" seed="5"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .9 -.35"/>'
         f'<feComposite in2="SourceGraphic" operator="in"/></filter></defs>')
    caras = [("M-300,0 L-220,-210 L-130,-300 L-60,-470 L-10,-330 L-80,-150 L-150,0 Z", f"url(#{u}a)"),
             ("M-150,0 L-80,-150 L-10,-330 L40,-360 L20,-200 L-20,0 Z", f"url(#{u}b)"),
             ("M-60,-470 L40,-520 L90,-420 L40,-360 L-10,-330 Z", f"url(#{u}a)"),
             ("M40,-360 L90,-420 L170,-300 L230,-130 L290,0 L-20,0 L20,-200 Z", f"url(#{u}c)"),
             ("M90,-420 L130,-470 L180,-380 L170,-300 Z", f"url(#{u}b)")]
    s = [d,
         f'<path d="M-380,10 Q-200,180 -60,330 Q120,380 300,250 Q400,120 360,10 Z" fill="url(#{u}w)" opacity=".55" filter="url(#{u}blur18)"/>']
    for path, fill in caras:
        s.append(f'<path d="{path}" fill="{fill}" stroke="{TIN}" stroke-width="4" stroke-linejoin="round"/>')
    s.append(f'<path d="M-300,0 L-220,-210 L-130,-300 L-60,-470 L40,-520 L130,-470 L180,-380 L230,-130 L290,0 Z" fill="#fff" filter="url(#{u}nv)" opacity=".35"/>')
    s.append(f'<path d="M-60,-470 L-10,-330 L40,-360 M-130,-300 L-80,-150 M90,-420 L40,-360 L20,-200" stroke="#ffffff" stroke-width="4" fill="none" opacity=".85"/>')
    s.append(f'<path d="M-40,-280 L-20,-200 L-50,-120 M120,-300 L150,-200" stroke="#3f7fb0" stroke-width="3" fill="none" opacity=".6"/>')
    s.append(f'<path d="M-310,2 Q-150,-14 0,2 T300,2" stroke="#e8f6ff" stroke-width="7" fill="none" opacity=".8" filter="url(#{u}blur2)"/>')
    vaiven(t, f"#{u}", "y: '+=7'", periodo=3.2)
    return g(p, "".join(s), u)


# ============================================================================ transatlántico HD
@dib("transatlantico_hd")
def transatlantico_hd(p, u, t):
    rng = random.Random(11)
    luces = p.get("luces", True)
    d = (f'<defs>{filtros(u)}{lin("#2a2f39", "#07090d", u + "h")}{lin("#fffaf0", "#d6cfbd", u + "s")}'
         f'{lin("#f0b36a", "#b0712e", u + "f", 0)}{lin("#ffffff", "#c9c3b2", u + "b", 0)}'
         f'<filter id="{u}rf" x="-10%" y="-10%" width="120%" height="140%"><feTurbulence type="turbulence" baseFrequency="0.01 0.09" numOctaves="2" seed="3"/>'
         f'<feDisplacementMap in="SourceGraphic" scale="30" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="4"/></filter>'
         f'{rad([(0, "#c9ced8", .7), (.6, "#9aa0aa", .3), (1, "#9aa0aa", 0)], u + "hm")}</defs>')
    casco = (f'<path d="M-600,-50 L560,-50 Q610,-56 640,-122 L660,-124 Q650,-40 612,28 Q598,58 560,62 L-540,62 Q-590,58 -606,20 Q-616,-14 -600,-50 Z" fill="url(#{u}h)" stroke="{TIN}" stroke-width="5"/>'
             f'<path d="M-600,-44 L600,-44" stroke="#c9a24a" stroke-width="3" opacity=".9"/>'
             f'<path d="M-602,40 L606,40 Q598,58 560,62 L-540,62 Q-588,58 -602,40 Z" fill="#7a1a16"/>'
             f'<path d="M-580,-40 Q0,-30 620,-50" stroke="#ffffff" stroke-opacity=".12" stroke-width="10" fill="none"/>')
    cubiertas = []
    for k, (y0, x0, x1, alto) in enumerate([(-50, -470, 470, 40), (-90, -440, 430, 36), (-126, -400, 380, 32)]):
        cubiertas.append(f'<path d="M{x0},{y0} L{x1},{y0} L{x1 - 12},{y0 - alto} L{x0 + 8},{y0 - alto} Z" fill="url(#{u}s)" stroke="{TIN}" stroke-width="3.5"/>'
                         f'<line x1="{x0 + 8}" x2="{x1 - 12}" y1="{y0 - alto}" y2="{y0 - alto}" stroke="#8f8a7c" stroke-width="3"/>')
        for x in range(x0 + 16, x1 - 16, 16):
            cubiertas.append(f'<line x1="{x}" x2="{x}" y1="{y0 - alto}" y2="{y0 - alto - 9}" stroke="#d8d2c2" stroke-width="1.6"/>')
        cubiertas.append(f'<line x1="{x0 + 8}" x2="{x1 - 12}" y1="{y0 - alto - 9}" y2="{y0 - alto - 9}" stroke="#d8d2c2" stroke-width="2"/>')
    ventanas, brillo = [], []
    for y0, x0, x1, paso, r in [(-18, -560, 590, 17, 4.2), (10, -540, 590, 17, 4.2), (-74, -440, 440, 15, 4.6), (-112, -410, 400, 15, 4.4), (-146, -380, 370, 16, 4)]:
        x = x0
        while x < x1:
            on = luces and rng.random() < .82
            col = "#ffd27a" if on else "#1b1f28"
            ventanas.append(f'<circle cx="{x}" cy="{y0}" r="{r}" fill="{col}"/>')
            if on:
                brillo.append(f'<circle cx="{x}" cy="{y0}" r="{r * 2.6:.1f}" fill="#ffbf5a"/>')
            x += paso
    botes = "".join(f'<g transform="translate({x} -162)"><path d="M-20,-14 L20,-14 Q18,0 10,4 L-10,4 Q-18,0 -20,-14 Z" fill="url(#{u}b)" stroke="{TIN}" stroke-width="2.5"/>'
                    f'<path d="M-22,-14 Q-24,-36 -14,-40 M22,-14 Q24,-36 14,-40" stroke="{TIN}" stroke-width="2.5" fill="none"/></g>'
                    for x in list(range(-360, -120, 52)) + list(range(140, 360, 52)))
    chimeneas = ""
    for k, cx in enumerate([-250, -90, 70, 230]):
        chimeneas += (f'<g transform="translate({cx} -158) skewX(-10)"><rect x="-36" y="-228" width="72" height="228" rx="8" fill="url(#{u}f)" stroke="{TIN}" stroke-width="4"/>'
                      f'<rect x="-36" y="-228" width="72" height="48" rx="8" fill="{TIN}"/>'
                      f'<rect x="-26" y="-176" width="10" height="170" fill="#fff" opacity=".18"/>'
                      f'<line x1="44" y1="-210" x2="44" y2="0" stroke="{TIN}" stroke-width="3"/></g>')
    mastiles = (f'<line x1="-500" y1="-50" x2="-530" y2="-470" stroke="{TIN}" stroke-width="7"/><line x1="500" y1="-50" x2="530" y2="-470" stroke="{TIN}" stroke-width="7"/>'
                f'<path d="M-530,-470 L530,-470" stroke="{TIN}" stroke-width="1.6" opacity=".7"/>'
                f'<path d="M-530,-470 L-600,-50 M530,-470 L640,-120 M-530,-470 L-300,-160 M530,-470 L300,-160" stroke="{TIN}" stroke-width="1.4" opacity=".6"/>'
                f'<circle cx="530" cy="-462" r="6" fill="#fff6d0"/><circle cx="530" cy="-462" r="20" fill="#fff6d0" opacity=".45" filter="url(#{u}blur6)"/>'
                f'<circle cx="-530" cy="-462" r="5" fill="#fff6d0"/>')
    humo = "".join(f'<circle id="{u}hm{k}" cx="{[-250, -90, 70, 230][k % 4] - 40}" cy="-400" r="{52 + (k // 4) * 20}" fill="url(#{u}hm)"/>' for k in range(12))
    for k in range(12):
        anim(t, f"#{u}hm{k}", "{x: 0, y: 0, scale: 0.5, opacity: 0.95}",
             f"{{x: {-210 - k * 14}, y: {-100 - (k // 4) * 70}, scale: 2.4, opacity: 0, duration: 2.4, repeat: {int(t.dur / 2.4) + 1}, ease: 'power1.out'}}", (k % 6) * .4)
    barco = (casco + "".join(cubiertas) + botes + chimeneas + mastiles + f'<g>{"".join(ventanas)}</g>' +
             (f'<g opacity=".55" filter="url(#{u}blur6)" style="mix-blend-mode:screen">{"".join(brillo)}</g>' if brillo else ""))
    estela = (f'<path id="{u}es" d="M-600,40 Q-900,30 -1300,70 L-1300,110 Q-900,70 -600,62 Z" fill="#e8f2ff" opacity=".45" filter="url(#{u}blur6)"/>'
              f'<path d="M640,-40 Q700,0 720,40 Q680,30 630,10 Z" fill="#e8f2ff" opacity=".55" filter="url(#{u}blur2)"/>')
    reflejo = (f'<g transform="translate(0 124) scale(1 -0.75)" opacity=".16" filter="url(#{u}rf)">{casco}{"".join(cubiertas)}{chimeneas}'
               f'{"".join(b.replace("fill=\"#ffbf5a\"", "fill=\"#ffbf5a\" opacity=\".9\"") for b in brillo)}</g>')
    glow = (f'<ellipse cx="0" cy="-60" rx="760" ry="150" fill="#ffcf7a" opacity=".16" filter="url(#{u}blur40)" style="mix-blend-mode:screen"/>' if luces else "")
    s = d + glow + reflejo + humo + estela + f'<g id="{u}in">{barco}</g>'
    mov = p.get("mov", "avanza")
    if mov == "avanza":
        deriva(t, f"#{u}", f"x: '+={p.get('avance', 120)}'")
        vaiven(t, f"#{u}in", "rotation: 0.5, y: 5", periodo=2.6)
    return g({**p}, s, u)


# ============================================================================ niebla HD
@dib("niebla_hd")
def niebla_hd(p, u, t):
    y = p.get("y", 1150)
    col = p.get("color", "#c9d6e6")
    op = p.get("op", .5)
    return (f'<defs><filter id="{u}f" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.0022 0.011" numOctaves="4" seed="8"/>'
            f'<feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1.7 -.55"/></filter>'
            f'<linearGradient id="{u}mg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".45" stop-color="#fff" stop-opacity="1"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="{u}m"><rect x="-400" y="{y - 260}" width="1900" height="520" fill="url(#{u}mg)"/></mask></defs>'
            f'<g mask="url(#{u}m)" opacity="{op}"><rect id="{u}r" x="-400" y="{y - 260}" width="1900" height="520" filter="url(#{u}f)" style="color:{col}"/>'
            f'<rect x="-400" y="{y - 260}" width="1900" height="520" fill="{col}" opacity=".25"/></g>') + (deriva(t, f"#{u}r", "x: 160") or "")


# ============================================================================ andén de estación HD (perspectiva)
@dib("anden_hd")
def anden_hd(p, u, t):
    """Andén de estación de los años 20 en perspectiva: piso de baldosas, borde amarillo, vías, techo con
    columnas de hierro, faroles encendidos y luz de atardecer que entra de lado."""
    vx, vy = p.get("fuga_x", 640), p.get("fuga_y", 1040)
    luz = p.get("luz", "#ffb35c")
    d = (f'<defs>{filtros(u)}{lin("#8a7a66", "#4a3e30", u + "pi")}{lin("#3a2e24", "#1a140e", u + "te")}{lin("#6b5a48", "#2a2018", u + "co", 0)}'
         f'<linearGradient id="{u}lz" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{luz}" stop-opacity=".55"/><stop offset="1" stop-color="{luz}" stop-opacity="0"/></linearGradient></defs>')
    s = [d]
    # vías a la derecha
    s.append(f'<polygon points="{vx},{vy} 1300,1920 2200,1920" fill="#2a241e"/>')
    for k, off in enumerate((40, 300)):
        s.append(f'<line x1="{vx + 4 + k * 6}" y1="{vy}" x2="{1300 + off}" y2="1920" stroke="#9aa0a6" stroke-width="{6 + k * 4}"/>')
    for k in range(14):
        f = (k / 14) ** 1.8
        y = vy + (1920 - vy) * f
        x0 = vx + (1300 - vx) * f
        x1 = vx + (1700 - vx) * f
        s.append(f'<line x1="{x0:.0f}" y1="{y:.0f}" x2="{x1:.0f}" y2="{y:.0f}" stroke="#5a4636" stroke-width="{2 + 10 * f:.1f}"/>')
    # piso del andén
    s.append(f'<polygon points="{vx},{vy} -600,1920 1300,1920" fill="url(#{u}pi)"/>')
    for k in range(18):
        f = (k / 18) ** 1.9
        y = vy + (1920 - vy) * f
        s.append(f'<line x1="{vx + (-600 - vx) * f:.0f}" y1="{y:.0f}" x2="{vx + (1300 - vx) * f:.0f}" y2="{y:.0f}" stroke="#3a3024" stroke-width="{1 + 3 * f:.1f}" opacity=".6"/>')
    for k in range(-6, 8):
        s.append(f'<line x1="{vx}" y1="{vy}" x2="{vx + k * 170}" y2="1920" stroke="#3a3024" stroke-width="2" opacity=".35"/>')
    s.append(f'<polygon points="{vx},{vy} 1240,1920 1300,1920" fill="#e8b830"/>')
    # techo y columnas
    s.append(f'<polygon points="-200,0 1280,0 {vx + 60},{vy - 260} {vx - 80},{vy - 260}" fill="url(#{u}te)"/>')
    for k in range(10):
        f = (k / 10) ** 1.7
        x = vx - 70 + (-120 - (vx - 70)) * (1 - f)
        ytop = (vy - 255) + (40 - (vy - 255)) * (1 - f)
        ybot = vy + (1700 - vy) * (1 - f)
        w = 6 + 34 * (1 - f)
        s.append(f'<rect x="{x - w / 2:.0f}" y="{ytop:.0f}" width="{w:.0f}" height="{ybot - ytop:.0f}" fill="url(#{u}co)" stroke="{TIN}" stroke-width="{1 + 2 * (1 - f):.1f}"/>')
        if k % 2 == 0:
            lx, ly = x + w * 1.4, ytop + (ybot - ytop) * .25
            r = 10 + 30 * (1 - f)
            s.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="{r * 2.6:.0f}" fill="#ffd27a" opacity=".35" filter="url(#{u}blur18)"/>'
                     f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="{r * .55:.0f}" fill="#fff2c4"/>'
                     f'<rect x="{lx - r * .5:.0f}" y="{ly - r * .9:.0f}" width="{r:.0f}" height="{r * .3:.0f}" fill="{TIN}"/>')
    # luz de atardecer barriendo el andén
    s.append(f'<polygon points="1080,700 1080,1700 -200,1920 -200,1500" fill="url(#{u}lz)" style="mix-blend-mode:screen"/>')
    return "".join(s)


@dib("sombra_larga")
def sombra_larga(p, u, t):
    """Sombra proyectada larga (atardecer) desde el pie de un personaje u objeto."""
    x, y, l, a = p.get("x", 540), p.get("y", 1600), p.get("largo", 420), p.get("angulo", -18)
    return (f'<defs><filter id="{u}b"><feGaussianBlur stdDeviation="6"/></filter></defs>'
            f'<ellipse cx="{x - l / 2}" cy="{y}" rx="{l / 2}" ry="{p.get("ancho", 40)}" fill="#000" opacity=".38" filter="url(#{u}b)" transform="rotate({a} {x} {y})"/>')
