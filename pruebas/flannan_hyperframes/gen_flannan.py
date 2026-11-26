"""Genera flannan/index.html: prueba de 13,5 s en HyperFrames (GSAP) con la voz real del misterio del faro."""
import json
import shutil
from pathlib import Path

REPO = Path("/home/user/videos-youtube")
P = Path(__file__).parent
(P / "assets/fonts").mkdir(parents=True, exist_ok=True)
shutil.copy(REPO / "fuentes/Anton-Regular.woff", P / "assets/fonts/Anton-Regular.woff")
DUR = 13.5
import subprocess
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(REPO / "audios/Faro de las islas Flannan  .mp3"),
                "-t", str(DUR), "-af", f"afade=t=out:st={DUR-0.4}:d=0.4", str(P / "assets/voz.mp3")], check=True)

words = [w for w in json.load(open(REPO / "audios/Faro de las islas Flannan  .mp3.palabras.json")) if w[1] < DUR]
# grupos de máx. 3 palabras, cortando en signos de puntuación
grupos, g = [], []
for w in words:
    g.append(w)
    if len(g) == 3 or w[0][-1] in ",.":
        grupos.append(g); g = []
if g:
    grupos.append(g)

KEY = {"1900,", "desaparecieron,", "rastro.", "apagado", "nadie", "cerrada."}
caps, capjs = [], []
for i, g in enumerate(grupos):
    start = g[0][1]
    end = grupos[i + 1][0][1] if i + 1 < len(grupos) else DUR
    spans = []
    for j, (t, a, b) in enumerate(g):
        cls = "w key" if t in KEY else "w"
        spans.append(f'<span id="c{i}w{j}" class="{cls}">{t.upper().rstrip(",.")}</span>')
        capjs.append(f'tl.to("#c{i}w{j}", {{color: "{ "#FF3B30" if t in KEY else "#FFD21F"}", scale: 1.12, duration: 0.08, ease: "power2.out"}}, {a:.2f});')
        capjs.append(f'tl.to("#c{i}w{j}", {{color: "#FFFFFF", scale: 1, duration: 0.12}}, {b:.2f});' if t not in KEY else "")
    caps.append(f'<div id="cap{i}" class="clip cap" data-start="{start:.2f}" data-duration="{end-start:.2f}" '
                f'data-track-index="5"><div class="capin" id="ci{i}">{" ".join(spans)}</div></div>')
    capjs.append(f'tl.from("#ci{i}", {{y: 40, scale: 0.85, opacity: 0, duration: 0.18, ease: "back.out(2)"}}, {start:.2f});')

# lluvia con semilla fija (determinista)
import random
r = random.Random(7)
rain = "".join(f'<i style="left:{r.uniform(-100,1180):.0f}px;top:{r.uniform(-400,1920):.0f}px;'
               f'height:{r.uniform(40,110):.0f}px;opacity:{r.uniform(.15,.45):.2f}"></i>' for _ in range(140))

html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.woff") format("woff"); }}
:root {{ --ground:#05070d; --ink:#fff; --gold:#FFD21F; --red:#E3141B; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:var(--ground); }}
#root {{ width:1080px; height:1920px; position:relative; overflow:hidden; font-family:"Anton", sans-serif; }}
#cam {{ position:absolute; inset:0; transform-origin:50% 55%; }}
#world {{ position:absolute; inset:0; transform-origin:50% 55%; }}
#sky {{ position:absolute; inset:0; background:radial-gradient(120% 70% at 50% 30%, #1d2b4a 0%, #0b1222 55%, #04060b 100%); }}
#moon {{ position:absolute; left:740px; top:330px; width:150px; height:150px; border-radius:50%;
  background:radial-gradient(circle at 40% 40%, #fdf6dc, #c9c2a7 70%); box-shadow:0 0 120px 40px rgba(220,220,180,.18); }}
.cloud {{ position:absolute; height:160px; border-radius:80px; background:rgba(20,28,48,.85); filter:blur(6px); }}
#beam {{ position:absolute; left:540px; top:440px; width:1500px; height:420px; transform-origin:0% 50%;
  background:linear-gradient(90deg, rgba(255,236,160,.75), rgba(255,236,160,0) 85%);
  clip-path:polygon(0 47%, 100% 0, 100% 100%, 0 53%); mix-blend-mode:screen; }}
#halo {{ position:absolute; left:435px; top:545px; width:210px; height:210px; border-radius:50%;
  background:radial-gradient(circle, rgba(255,240,170,1) 0%, rgba(255,220,120,.5) 35%, rgba(255,220,120,0) 70%); }}
#scene {{ position:absolute; left:0; top:0; width:1080px; height:1920px; }}
#sea {{ position:absolute; left:-200px; top:1180px; width:1480px; height:740px; background:linear-gradient(#0d1a30, #02050b); }}
.wave {{ position:absolute; left:-300px; width:1800px; height:60px; }}
#rain {{ position:absolute; inset:-200px 0 0 0; transform:rotate(12deg); }}
#rain i {{ position:absolute; width:2px; background:linear-gradient(transparent, #b8c8ee); }}
#flash {{ position:absolute; inset:0; background:#dfe8ff; opacity:0; }}
#vignette {{ position:absolute; inset:0; background:radial-gradient(90% 60% at 50% 50%, transparent 55%, rgba(0,0,0,.85)); }}
.keeper {{ position:absolute; top:1085px; width:46px; height:96px; }}
#boat {{ position:absolute; left:-520px; top:1085px; width:470px; }}
#chip {{ position:absolute; left:50%; top:300px; transform:translateX(-50%); background:var(--red); color:#fff;
  font-size:42px; letter-spacing:2px; padding:10px 26px; border-radius:14px; border:4px solid #000; white-space:nowrap; }}
#date {{ position:absolute; left:0; right:0; top:390px; text-align:center; color:var(--gold); font-size:230px; line-height:1;
  -webkit-text-stroke:10px #000; paint-order:stroke fill; text-shadow:0 14px 0 rgba(0,0,0,.5); }}
#dateSub {{ position:absolute; left:0; right:0; top:630px; text-align:center; color:#fff; font-size:64px; letter-spacing:3px;
  -webkit-text-stroke:6px #000; paint-order:stroke fill; }}
#big {{ position:absolute; left:0; right:0; top:400px; text-align:center; color:#fff; font-size:150px; line-height:.95;
  -webkit-text-stroke:9px #000; paint-order:stroke fill; }}
#big b {{ color:var(--red); font-weight:400; }}
#counter {{ position:absolute; left:0; right:0; top:420px; text-align:center; color:#fff; font-size:110px;
  -webkit-text-stroke:8px #000; paint-order:stroke fill; }}
.cap {{ position:absolute; left:120px; right:192px; top:1240px; display:flex; justify-content:center; }}
.capin {{ text-align:center; font-size:96px; line-height:1.05; color:#fff; -webkit-text-stroke:9px #000; paint-order:stroke fill;
  text-shadow:0 8px 0 rgba(0,0,0,.55); }}
.w {{ display:inline-block; margin:0 .14em; }}
#handle {{ position:absolute; left:0; right:0; top:1190px; text-align:center; color:rgba(255,255,255,.55); font-size:34px; letter-spacing:3px; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="bg" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0">
    <div id="cam"><div id="world">
      <div id="sky"></div>
      <div id="moon"></div>
      <div class="cloud" id="cl1" style="left:-120px;top:420px;width:620px"></div>
      <div class="cloud" id="cl2" style="left:600px;top:520px;width:700px"></div>
      <div class="cloud" id="cl3" style="left:200px;top:250px;width:520px;opacity:.7"></div>
      <div id="beam"></div>
      <svg id="scene" viewBox="180 345 720 1280">
        <defs><linearGradient id="rock" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#1b2234"/><stop offset="1" stop-color="#070a12"/></linearGradient>
        <linearGradient id="tower" x1="0" x2="1"><stop offset="0" stop-color="#d9d4c6"/><stop offset=".55" stop-color="#f3efe3"/><stop offset="1" stop-color="#8f8a7e"/></linearGradient></defs>
        <path d="M120 1230 C 220 1080, 330 1040, 420 1010 C 470 990, 620 990, 700 1030 C 800 1080, 900 1150, 980 1230 Z" fill="url(#rock)"/>
        <rect x="610" y="975" width="120" height="70" fill="#2a2f3d"/><polygon points="600,978 670,930 740,978" fill="#3a1d1d"/>
        <polygon points="505,1010 575,1010 562,790 518,790" fill="url(#tower)"/>
        <rect x="505" y="900" width="70" height="26" fill="#b3261e"/><rect x="508" y="840" width="64" height="22" fill="#b3261e"/>
        <rect x="508" y="762" width="64" height="32" fill="#22262f"/>
        <rect id="lamp" x="516" y="766" width="48" height="24" fill="#ffe9a0"/>
        <polygon points="500,764 540,726 580,764" fill="#22262f"/><g id="k1" transform="translate(430 948)"><g class="kin"><circle cx="11" cy="6" r="6" fill="#0a0d14"/><path d="M2 15 Q11 9 20 15 L22 50 L0 50 Z" fill="#0a0d14"/></g></g><g id="k2" transform="translate(462 948)"><g class="kin"><circle cx="11" cy="6" r="6" fill="#0a0d14"/><path d="M2 15 Q11 9 20 15 L22 50 L0 50 Z" fill="#0a0d14"/></g></g><g id="k3" transform="translate(640 948)"><g class="kin"><circle cx="11" cy="6" r="6" fill="#0a0d14"/><path d="M2 15 Q11 9 20 15 L22 50 L0 50 Z" fill="#0a0d14"/></g></g><rect x="498" y="790" width="84" height="8" fill="#22262f"/>
      </svg>
      <div id="halo"></div>
      <div id="sea"></div>
      <svg id="boat" viewBox="0 0 330 200"><rect x="150" y="10" width="8" height="120" fill="#0b0f18"/><polygon points="160,18 160,110 250,110" fill="#c9c2a7" opacity=".85"/>
        <path d="M20 130 L310 130 L270 180 L60 180 Z" fill="#0b0f18"/><circle cx="240" cy="148" r="6" fill="#ffd36b"/></svg>
      <svg class="wave" id="wv1" style="top:1200px" viewBox="0 0 1800 60"><path d="M0 30 Q 50 0 100 30 T 200 30 T 300 30 T 400 30 T 500 30 T 600 30 T 700 30 T 800 30 T 900 30 T 1000 30 T 1100 30 T 1200 30 T 1300 30 T 1400 30 T 1500 30 T 1600 30 T 1700 30 T 1800 30 V60 H0Z" fill="#14264a"/></svg>
      <svg class="wave" id="wv2" style="top:1240px" viewBox="0 0 1800 60"><path d="M0 30 Q 60 0 120 30 T 240 30 T 360 30 T 480 30 T 600 30 T 720 30 T 840 30 T 960 30 T 1080 30 T 1200 30 T 1320 30 T 1440 30 T 1560 30 T 1680 30 T 1800 30 V60 H0Z" fill="#0c1934"/></svg>
      <div id="rain">{rain}</div>
    </div></div>
    <div id="flash"></div>
    <div id="vignette"></div>
  </div>

  <div id="chipHost" class="clip" data-start="0" data-duration="{DUR}" data-track-index="1"><div id="chip">MISTERIO SIN RESOLVER</div></div>
  <div id="dateHost" class="clip" data-start="0" data-duration="2.2" data-track-index="2"><div id="date">1900</div><div id="dateSub">ISLAS FLANNAN · ESCOCIA</div></div>
  <div id="bigHost" class="clip" data-start="4.0" data-duration="3.2" data-track-index="2"><div id="big">3 GUARDIANES<br/><b>DESAPARECIDOS</b></div></div>
  <div id="ctrHost" class="clip" data-start="9.4" data-duration="4.1" data-track-index="2"><div id="counter">FARO APAGADO</div></div>
  <div id="handleHost" class="clip" data-start="0" data-duration="{DUR}" data-track-index="3"><div id="handle">@1MRELATO</div></div>
  <div id="capsHost" data-track-kind="captions">
  {"".join(caps)}
  </div>
  <audio id="voz" class="clip" src="assets/voz.mp3" data-start="0" data-duration="{DUR}" data-track-index="9"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
// cámara: empuje lento continuo + golpe en los momentos clave
tl.fromTo("#world", {{scale: 1.0}}, {{scale: 1.18, duration: {DUR}, ease: "none"}}, 0);
tl.fromTo("#cam", {{scale: 1}}, {{scale: 1.07, duration: 0.25, ease: "power3.out", yoyo: true, repeat: 1}}, 4.12);
// haz del faro girando (scaleX simula giro 3D)
tl.fromTo("#beam", {{scaleX: 1, rotation: -8}}, {{scaleX: -1, rotation: 8, duration: 2.4, ease: "sine.inOut", repeat: 3, yoyo: true}}, 0);
tl.fromTo("#halo", {{scale: 0.8}}, {{scale: 1.25, duration: 1.2, ease: "sine.inOut", repeat: 7, yoyo: true}}, 0);
// se apaga en "apagado"
tl.to(["#beam", "#halo"], {{opacity: 0, duration: 0.35, ease: "power2.in"}}, 9.46);
tl.to("#lamp", {{fill: "#2b2f38", duration: 0.35}}, 9.46);
// nubes y olas
tl.to("#cl1", {{x: 160, duration: {DUR}, ease: "none"}}, 0);
tl.to("#cl2", {{x: -200, duration: {DUR}, ease: "none"}}, 0);
tl.to("#cl3", {{x: 120, duration: {DUR}, ease: "none"}}, 0);
tl.to("#wv1", {{x: 200, duration: {DUR}, ease: "none"}}, 0);
tl.to("#wv2", {{x: -240, duration: {DUR}, ease: "none"}}, 0);
tl.fromTo("#rain", {{y: -300}}, {{y: 300, duration: 0.6, ease: "none", repeat: Math.ceil({DUR}/0.6)}}, 0);
// relámpagos
[[1.0, .55], [4.15, .8], [9.5, .5]].forEach(([t, o]) => {{
  tl.to("#flash", {{opacity: o, duration: 0.05}}, t); tl.to("#flash", {{opacity: 0, duration: 0.35, ease: "power2.out"}}, t + 0.06);
}});
// guardianes: aparecen y se desvanecen en "desaparecieron"
tl.from(["#k1 .kin", "#k2 .kin", "#k3 .kin"], {{opacity: 0, y: 20, duration: 0.4, stagger: 0.12}}, 2.3);
tl.to(["#k1 .kin", "#k2 .kin", "#k3 .kin"], {{opacity: 0, y: -40, scaleY: 1.4, filter: "blur(8px)", duration: 0.6, stagger: 0.15, ease: "power2.in"}}, 4.12);
// barco llega en "barco"
tl.to("#boat", {{x: 560, duration: 3.2, ease: "power2.out"}}, 7.4);
tl.fromTo("#boat", {{rotation: -3}}, {{rotation: 3, duration: 0.8, ease: "sine.inOut", repeat: 7, yoyo: true}}, 7.4);
// textos
tl.from("#chip", {{y: -80, opacity: 0, duration: 0.3, ease: "back.out(2)"}}, 0);
tl.from("#date", {{scale: 2.6, opacity: 0, duration: 0.28, ease: "power4.out"}}, 0.85);
tl.from("#dateSub", {{y: 30, opacity: 0, duration: 0.25}}, 1.1);
tl.from("#big", {{scale: 0.6, opacity: 0, duration: 0.25, ease: "back.out(2.5)"}}, 4.12);
tl.to("#big b", {{x: 6, duration: 0.05, repeat: 7, yoyo: true}}, 4.4);
tl.from("#counter", {{y: 60, opacity: 0, duration: 0.25, ease: "back.out(2)"}}, 9.46);
{chr(10).join(c for c in capjs if c)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
"""
(P / "index.html").write_text(html, encoding="utf-8")
print("ok", len(grupos), "grupos")
