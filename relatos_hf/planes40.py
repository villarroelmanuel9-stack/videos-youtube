#!/usr/bin/env python3
"""
Planes visuales de los 40 relatos (más el piloto 30). Cada toma empieza en la frase «en» del guion y dibuja
literalmente lo que se está contando. Ejecutar para escribir relatos_hf/planes/relato_NNN.json.
"""
import json
from pathlib import Path

PLANES = Path(__file__).parent / "planes"


# ---------------------------------------------------------------- atajos
def C(h, **k):
    return {"d": "cielo", "hora": h, **k}


def MAR(h, **k):
    return {"d": "mar", "hora": h, **k}


def D(nombre, **k):
    return {"d": nombre, **k}


def E(en, capas, cam="push", **k):
    return {"en": en, "tipo": "escena", "capas": capas, "camara": cam, **k}


def T(en, lineas, **k):
    return {"en": en, "tipo": "titulo", "lineas": lineas, **k}


def F(en, dia, mes, anio, **k):
    return {"en": en, "tipo": "fecha", "dia": dia, "mes": mes, "anio": anio, **k}


def N(en, hasta, unidad, sub="", **k):
    return {"en": en, "tipo": "contador", "hasta": hasta, "unidad": unidad, "sub": sub, **k}


def M(en, centro, zoom, **k):
    return {"en": en, "tipo": "mapa", "centro": centro, "zoom": zoom, **k}


def FIN(en, lineas, **k):
    return {"en": en, "tipo": "final", "lineas": lineas, **k}


def noche_mar(luna=True, **k):
    c = C("noche", horizonte=1180, **({"astro": "luna", "astro_x": 820, "astro_y": 420, "astro_r": 60} if luna else {}))
    return [c, MAR("noche", horizonte=1180, **({"reflejo_x": 820} if luna else {}))]


P = {}

# ================================================================ 3 · Titanic
P[3] = dict(tema="misterio", claves=["Titanic", "iceberg", "«insumergible».", "quinientas."], tomas=[
    E("La noche del catorce", noche_mar() + [D("iceberg", x=150, y=1190, s=.45, z=.4),
      D("transatlantico", x=620, y=1200, s=.74, avance=150, reflejo=True, z=.8), D("niebla", y=1210, op=.3)],
      dato=["14 DE ABRIL", "1912"], amb="olas"),
    E("recibió varios avisos", [D("interior", pared="#3a3226", vista="noche", ventana_x=90), D("radio", x=640, y=1320, s=.9),
      D("carta", x=330, y=1450, s=.55, texto="¡HIELO!", r=-6)], "push", texto="6 AVISOS DE HIELO", amb="ninguno", sfx="papel", sfx_dur=.6),
    E("y siguió navegando", noche_mar(luna=False) + [D("transatlantico", x=420, y=1230, s=1.05, avance=320, reflejo=True)],
      "pan_der", texto=["CASI A TODA", "VELOCIDAD"], acento=1, amb="olas"),
    E("Era el barco", [C("dia", horizonte=1180), MAR("dia", horizonte=1180), D("transatlantico", x=560, y=1230, s=.95, luces=False, avance=60),
      D("bote", x=930, y=1300, s=.4, gente=2)], "pull", dato=["269 METROS", "DE LARGO"], amb="olas"),
    T("Muchos lo llamaban", ["«INSUMERGIBLE»"], icono="🚢", tam=150),
    E("A las once", noche_mar() + [D("persona", x=540, y=1480, s=1.25, ropa="uniforme", sombrero="gorra", mov="respira"), D("baranda", y=1520)],
      "push", dato=["23:40", "VIGÍA"], amb="viento"),
    E("vieron un iceberg", noche_mar(luna=False) + [D("iceberg", x=540, y=1260, s=1.35), D("niebla", y=1240, op=.4)],
      "push_fuerte", sacudir=True, sfx="boom", amb="viento"),
    E("Alcanzaron a girar", noche_mar(luna=False) + [D("iceberg", x=260, y=1220, s=.8),
      D("transatlantico", x=760, y=1240, s=.8, avance=-80, reflejo=True)], "fijo", texto="¡A BABOR!", sfx="crujido", sfx_dur=2.2, sacudir=True),
    T("El agua entró", ["EL AGUA ENTRÓ", "EN VARIOS", "COMPARTIMENTOS"], acento=0, icono="🌊"),
    E("En menos de", noche_mar() + [D("transatlantico", x=560, y=1240, s=.8, mov="hundir", luces=True, apagar_en=1.2),
      D("bote", x=230, y=1320, s=.55, gente=6)], "fijo", dato=["MENOS DE", "3 HORAS"], amb="olas", sfx="crujido", sfx_dur=2.5),
    E("Había botes salvavidas", noche_mar() + [D("bote", x=300, y=1290, s=.75, gente=6), D("bote", x=760, y=1330, s=.6, gente=5),
      D("niebla", y=1250, op=.3)], "pan_izq", texto=["BOTES PARA", "LA MITAD"], acento=1, amb="olas"),
    N("Murieron más de", 1500, "PERSONAS", "MURIERON", icono="🕯️"),
    FIN("¿Qué habrías hecho", ["¿QUÉ HABRÍAS", "HECHO TÚ?"], capas=noche_mar(), comentario="Me subo al primer bote"),
])

# ================================================================ 4 · Violet Jessop
P[4] = dict(tema="misterio", estilo="calido", claves=["Titanic", "Britannic", "sobrevivir."], tomas=[
    E("Esta mujer sobrevivió", [C("dia", horizonte=1250), MAR("dia", horizonte=1250),
      D("persona", x=540, y=1560, s=1.5, ropa="camarera", falda=True, pelo="#2a1a10", pelo_largo=True, sombrero="cofia", mov="respira"), D("baranda", y=1600)],
      "push", texto=["3 NAUFRAGIOS"], amb="olas"),
    E("y dos de ellos", [C("atardecer", horizonte=1200), MAR("atardecer", horizonte=1200),
      D("transatlantico", x=300, y=1230, s=.5, luces=False, avance=50, reflejo=True), D("transatlantico", x=800, y=1260, s=.55, luces=False, avance=40, reflejo=True)],
      "pull", texto=["EL TITANIC", "Y SU GEMELO"], acento=0, amb="olas"),
    M("Violet Jessop nació", [-38.7, -62.3], 4, centro_desde=[-20, -60], zoom_desde=1.3, resaltar=["Argentina"], pines=[{"lat": -38.7, "lon": -62.3, "texto": "ARGENTINA"}]),
    E("y era camarera", [D("interior", pared="#6b2d3f", piso="#3a1d14", papel=True, vista="dia", ventana_x=650),
      D("persona", x=380, y=1400, s=1.2, ropa="camarera", falda=True, pelo_largo=True, sombrero="cofia", mov="respira"), D("mesa", x=760, y=1460, s=.8, color="#8a5a2f"),
      D("velas", x=760, y=1200, s=.6, n=3)], "push", dato=["CAMARERA", "DE LUJO"], amb="ninguno"),
    E("En mil novecientos once", [C("dia", horizonte=1220), MAR("dia", horizonte=1220),
      D("transatlantico", x=330, y=1250, s=.62, luces=False, avance=60), D("transatlantico", x=850, y=1270, s=.4, casco="#5c6268", luces=False, avance=-90)],
      "fijo", dato=["1911", "OLYMPIC"], sacudir=True, sfx="crujido", sfx_en=1.2, sfx_dur=1.8, amb="olas"),
    E("Al año siguiente", noche_mar() + [D("transatlantico", x=560, y=1240, s=.75, mov="hundir", apagar_en=1.5)], "fijo", dato=["1912", "TITANIC"], amb="olas"),
    E("Esa noche le", noche_mar() + [D("bote", x=540, y=1330, s=1.2, gente=6), D("niebla", y=1300, op=.35)], "push", texto=["LE ENTREGARON", "UN BEBÉ"], acento=1, amb="olas"),
    T("Y eso no", ["Y ESO", "NO ES TODO…"], acento=1, entrada="flash", sfx="riser", sfx_dur=1.0),
    E("En mil novecientos dieciséis", [C("dia", horizonte=1220), MAR("dia", horizonte=1220), D("transatlantico", x=540, y=1260, s=.8, hospital=True, avance=80, reflejo=True)],
      "push", dato=["1916", "BRITANNIC"], amb="olas"),
    E("cuando explotó una", [C("dia", horizonte=1220), MAR("dia", horizonte=1220), D("transatlantico", x=540, y=1260, s=.8, hospital=True, mov="hundir"),
      D("explosion", x=600, y=1250, s=1.0, en=.15)], "fijo", sacudir=True, sfx="boom", texto="¡UNA MINA!"),
    E("Saltó al agua", [C("niebla", horizonte=1150), MAR("niebla", horizonte=1150), D("bote", x=700, y=1260, s=.6, gente=4), D("niebla", y=1200, op=.5)],
      "baja", texto=["SALTÓ", "AL AGUA"], amb="olas"),
    N("y volvió a", 3, "NAUFRAGIOS", "Y SOBREVIVIÓ A LOS 3", icono="⚓"),
    FIN("¿Tú te habrías", ["¿TE SUBIRÍAS", "A OTRO BARCO?"], final="si_no", capas=[C("atardecer", horizonte=1200), MAR("atardecer", horizonte=1200)]),
])

# ================================================================ 5 · Espejos en la Luna
LUNA_SUELO = [C("espacio", horizonte=1300), D("planeta", x=830, y=430, r=110), D("suelo", y=1300, colores=["#9a9688", "#3e3c36"])]
P[5] = dict(tema="ciencia", estilo="frio", claves=["Luna?", "espejos", "láser", "centímetros"], tomas=[
    E("¿Fue real la", [C("espacio"), D("planeta", tipo="luna", x=540, y=960, r=420)], "push", texto=["¿FUE REAL?"], amb="drone", amb_vol=.8),
    E("Hay una prueba", [C("espacio"), D("planeta", x=300, y=1500, r=260), D("planeta", tipo="luna", x=800, y=500, r=120)], "pull", texto=["HAY UNA", "PRUEBA"], acento=1, amb="drone", amb_vol=.8),
    E("En mil novecientos sesenta", LUNA_SUELO + [D("astronauta", x=330, y=1500, s=.8), D("bandera", x=700, y=1500, s=1.1, colores=["#c41e1e", "#ffffff", "#c41e1e", "#ffffff", "#c41e1e", "#ffffff", "#c41e1e"], canton=True)],
      "push", dato=["JULIO", "1969"], amb="ninguno"),
    E("dejaron en la", LUNA_SUELO + [D("espejos", x=540, y=1450, s=1.5, brillo_en=.6), D("astronauta", x=180, y=1520, s=.6)],
      "push_fuerte", texto=["UN PANEL", "DE ESPEJOS"], acento=1, amb="ninguno"),
    E("Desde entonces, observatorios", [C("noche", horizonte=1300, astro="luna", astro_x=820, astro_y=380, astro_r=70), D("montanas", horizonte=1320),
      D("observatorio", x=300, y=1330, s=.9), D("laser", x1=300, y1=920, x2=820, y2=380, en=.8)], "fijo", texto="DISPARAN UN LÁSER", amb="viento", amb_vol=.6),
    E("y la luz", [C("espacio"), D("planeta", x=230, y=1450, r=200), D("planeta", tipo="luna", x=850, y=420, r=90), D("laser", x1=300, y1=1300, x2=820, y2=470, en=.1)],
      "fijo", texto=["REBOTA Y", "VUELVE"], acento=0, amb="ninguno"),
    N("unos dos segundos", 2.5, "SEGUNDOS", "IDA Y VUELTA", decimales=1, icono="⏱️"),
    T("Midiendo ese tiempo", ["PRECISIÓN DE", "CENTÍMETROS"], acento=1, icono="📏"),
    E("Así descubrieron algo", [C("espacio"), D("planeta", x=260, y=1300, r=230), D("planeta", tipo="luna", x=700, y=800, r=110, mov="aleja", dx=200, dy=-260)],
      "fijo", texto="LA LUNA SE ALEJA", amb="drone", amb_vol=.7),
    N("unos cuatro centímetros", 4, "CM POR AÑO", "SE ALEJA DE NOSOTROS", icono="🌙"),
    FIN("¿Tú crees que", ["¿FUIMOS", "A LA LUNA?"], final="si_no", capas=[C("espacio"), D("planeta", tipo="luna", x=540, y=1500, r=600)]),
])

# ================================================================ 7 · Laika
NIEVE_MOSCU = [C("noche", horizonte=1250), D("ciudad", era="sovietica", y=1260), D("suelo", y=1250, colores=["#c9d3e6", "#7d8aa6"]), D("particulas", tipo="nieve", n=60)]
P[7] = dict(tema="ciencia", estilo="neon", claves=["Laika", "Sputnik", "volver.", "calor"], tomas=[
    E("En mil novecientos", NIEVE_MOSCU + [D("perro", raza="laika", x=540, y=1520, s=1.0)], "push", dato=["1957", "MOSCÚ"], amb="viento"),
    E("se convirtió en", [C("espacio"), D("planeta", x=540, y=1650, r=700), D("satelite", x=200, y=600, s=.9, avance=500)],
      "pan_der", texto=["PRIMER SER VIVO", "EN ÓRBITA"], acento=1, amb="ninguno"),
    E("Se llamaba Laika", [D("interior", pared="#2f3b55", piso="#1d2233", luz_x=540, luz_y=900), D("perro", raza="laika", x=520, y=1500, s=1.9)], "push_fuerte", texto="LAIKA", amb="ninguno"),
    E("y viajó en", [C("noche", horizonte=1400), D("suelo", y=1400, colores=["#3a3f4a", "#15181e"]), D("cohete", x=540, y=1420, s=1.0), D("particulas", tipo="chispas", n=30)],
      "fijo", dato="SPUTNIK 2", sfx="riser", sfx_dur=2.0, amb="ninguno"),
    E("Los científicos soviéticos", [D("interior", pared="#3a4550", piso="#1d2228", vista="nieve", ventana_x=680),
      D("persona", x=300, y=1420, s=1.0, ropa="bata", mov="respira"), D("persona", x=560, y=1430, s=.95, ropa="bata", pelo="#7a5a3a"), D("perro", raza="laika", x=820, y=1440, s=.7)],
      "pan_izq", texto="PERROS DE LA CALLE", amb="ninguno"),
    E("porque creían que", NIEVE_MOSCU + [D("perro", raza="laika", x=360, y=1500, s=.8), D("perro", raza="laika", x=760, y=1520, s=.65, espejo=True)],
      "push", texto=["FRÍO", "Y HAMBRE"], acento=1, amb="viento"),
    E("La entrenaron durante", [D("interior", pared="#2f3b55", piso="#1d2233"), D("capsula", x=540, y=1450, s=1.4)], "push_fuerte", texto=["CABINAS", "CADA VEZ MÁS", "PEQUEÑAS"], acento=2, amb="ninguno"),
    T("Pero había un", ["NO ESTABA HECHA", "PARA VOLVER"], acento=1, entrada="flash", sfx="boom"),
    E("Durante décadas, el", [D("interior", pared="#3a2a1e"), D("periodico", x=540, y=1560, s=1.1, cabecera="1957", titular="¡VIVE EN ÓRBITA!", tam=70)], "fijo", amb="ninguno", sfx="papel", sfx_dur=.6),
    T("En dos mil", ["2002:", "LA VERDAD"], acento=1),
    E("murió a las", [C("espacio"), D("planeta", x=540, y=1700, r=600), D("capsula", x=540, y=1050, s=1.0, calor=True)], "push", texto="POR EL CALOR", amb="ninguno"),
    FIN("¿Conocías su historia?", ["¿CONOCÍAS", "SU HISTORIA?"], capas=[C("espacio"), D("planeta", x=540, y=1700, r=600)], comentario="Pobre Laika 💔"),
])

# ================================================================ 10 · Stanislav Petrov
BUNKER = dict(pared="#2a2f2a", piso="#141814", luz_x=540, luz_y=700)
P[10] = dict(tema="guerra", estilo="terror", claves=["misiles", "«ataque»", "falla", "razón."], tomas=[
    F("El veintiséis de", "26", "SEPTIEMBRE", "1983", hora="00:14"),
    E("una alarma anunció", [D("interior", **BUNKER), D("luz", x=540, y=600, r=700, color="#ff2a2a", parpadeo=True), D("pantalla", x=540, y=1300, s=1.4, alarma=True, texto="ALERTA", tam=130)],
      "push_fuerte", sacudir=True, amb="zumbido", sfx="estatica", sfx_dur=1.5),
    M("cinco misiles nucleares", [52, -40], 1.6, zoom_desde=1.0, resaltar=["United States of America", "Russia"], color_pais="#b3261e",
      ruta=[[40, -100], [65, -40], [56, 38]], pines=[{"lat": 40, "lon": -100, "texto": "EE.UU."}, {"lat": 56, "lon": 38, "texto": "URSS"}], paso_pines=1.0, titulo="5 MISILES"),
    T("Era plena Guerra", ["GUERRA", "FRÍA"], acento=1, icono="☢️"),
    E("Stanislav Petrov estaba", [D("interior", **BUNKER), D("pantalla", x=800, y=1300, s=.8, texto="OK", tam=110),
      D("persona", x=380, y=1500, s=1.3, ropa="uniforme", sombrero="gorra", mov="respira")], "push", dato=["STANISLAV", "PETROV"], amb="zumbido"),
    E("Su deber era", [D("interior", **BUNKER), D("telefono", x=540, y=1420, s=1.4, suena=True)], "push", texto=["AVISAR PODÍA", "INICIAR UNA", "GUERRA NUCLEAR"], acento=2, amb="zumbido"),
    E("Las pantallas decían", [D("interior", **BUNKER), D("luz", x=540, y=800, r=800, color="#ff2a2a", parpadeo=True),
      D("pantalla", x=540, y=1400, s=1.8, alarma=True, texto="ATAQUE", tam=120)], "push_fuerte", sacudir=True, amb="zumbido"),
    E("Pero algo no", [D("interior", **BUNKER), D("luz", x=540, y=800, r=700, color="#ff2a2a", op=.35), D("persona", x=540, y=1700, s=2.2, ropa="uniforme", sombrero="gorra")],
      "push", texto=["¿SOLO", "5 MISILES?"], acento=1, amb="zumbido"),
    E("Decidió reportarlo como", [D("interior", **BUNKER), D("pantalla", x=540, y=1350, s=1.5, texto="FALLA", tam=130)], "fijo", dato="FALSA ALARMA", amb="zumbido"),
    E("Tenía razón. Era", [C("dia", horizonte=1500, astro="sol", astro_x=820, astro_y=380, astro_r=80), D("rayos", x=820, y=380, op=.25),
      D("satelite", x=180, y=900, s=.6, avance=300)], "pan_izq", texto=["REFLEJO DEL SOL", "EN LAS NUBES"], acento=0, amb="viento", amb_vol=.5),
    FIN("¿Qué habrías hecho", ["¿QUÉ HABRÍAS", "HECHO TÚ?"], final="si_no"),
])

# ================================================================ 12 · Bomba del Zar
ARTICO = [C("frio", horizonte=1300) if False else C("niebla", horizonte=1300), D("montanas", horizonte=1320, nieve=True, colores=["#9aa8bf", "#7d8aa6", "#5c6a85"]),
          D("suelo", y=1320, colores=["#e6edf7", "#9aa8bf"])]
P[12] = dict(tema="guerra", estilo="pop", claves=["poderosa", "Zar.", "Hiroshima.", "mitad"], tomas=[
    E("La explosión más", ARTICO + [D("hongo", x=540, y=1330, s=1.25), D("explosion", x=540, y=1100, s=1.6, en=.05)], "pull", sacudir=True, sfx="boom", sfx_dur=2.0, amb="viento"),
    E("rompió ventanas a", [D("interior", pared="#4a4f5e", vista="dia", ventana_x=390, luz=False), D("luz", x=540, y=600, r=600, color="#fff3a6", op=.9)],
      "push", sacudir=True, texto="A CIENTOS DE KM", sfx="explosion_lejana", sfx_dur=2.0, amb="viento"),
    F("Fue el treinta", "30", "OCTUBRE", "1961"),
    M("sobre una isla", [73.8, 54.5], 4.5, zoom_desde=1.5, centro_desde=[60, 40], resaltar=["Russia"], pines=[{"lat": 73.8, "lon": 54.5, "texto": "NUEVA ZEMBLA"}], titulo="ÁRTICO"),
    T("La Unión Soviética", ["LA BOMBA", "DEL ZAR"], acento=1, icono="💣"),
    E("Era tan grande", [C("dia", horizonte=1700), D("avion", x=420, y=950, s=1.2, estrella=True, avance=200)], "pan_der", texto=["NO CABÍA EN", "EL AVIÓN"], acento=1, amb="jet"),
    E("La lanzaron con", [C("dia", horizonte=1700), D("paracaidas", x=540, y=1100, s=1.2), D("avion", x=150, y=500, s=.45, estrella=True, avance=900)],
      "baja", texto="PARACAÍDAS GIGANTE", amb="viento"),
    N("Tuvo la fuerza", 50, "MEGATONES", "50 MILLONES DE TONELADAS", icono="💥"),
    N("más de tres", 3000, "VECES HIROSHIMA", "MÁS DE", icono="☢️"),
    E("Su hongo subió", ARTICO + [D("hongo", x=540, y=1330, s=1.5)], "sube", dato=["+60 KM", "DE ALTURA"], amb="viento"),
    T("Y lo más", ["¡SOLO A LA", "MITAD DE SU", "POTENCIA!"], acento=1, entrada="flash", sfx="riser", sfx_dur=1.0),
    FIN("¿Te imaginabas algo", ["¿TE LO", "IMAGINABAS?"], capas=ARTICO),
])

# ================================================================ 14 · Gran Incendio de Londres
LONDRES = [C("noche", horizonte=1300), D("ciudad", era="antigua", y=1320, color="#2a1a10", color_lejos="#3a2416")]
P[14] = dict(tema="historia", estilo="clasico", claves=["panadería…", "madera,", "balde.", "seis"], tomas=[
    E("En mil seiscientos", LONDRES + [D("fuego", x=540, y=1330, s=1.6, ancho=900), D("particulas", tipo="brasas", n=60)], "push", dato="1666", amb="fuego", sfx="boom"),
    M("y destruyó casi", [51.51, -0.09], 22, zoom_desde=3, centro_desde=[50, 5], resaltar=["United Kingdom"], pines=[{"lat": 51.51, "lon": -0.09, "texto": "LONDRES"}]),
    E("Ocurrió en Pudding", [C("noche", horizonte=1350), D("casa", tipo="madera", x=540, y=1450, s=1.4), D("suelo", y=1450, colores=["#3a2a1e", "#120c08"]),
      D("luz", x=540, y=1250, r=350, color="#ff9a3c", parpadeo=True)], "push", dato="PUDDING LANE", amb="viento", amb_vol=.6),
    E("en el horno", [D("interior", pared="#5a2e1e", piso="#2a160e", luz_x=700, luz_y=1100), D("fuego", x=760, y=1350, s=.7, ancho=260),
      D("persona", x=330, y=1450, s=1.2, ropa="blanco", sombrero="gorra", color_sombrero="#f2f2ee")], "push", texto=["EL PANADERO", "DEL REY"], acento=1, amb="fuego"),
    E("Las casas eran", LONDRES + [D("ciudad", era="antigua", y=1500, color="#4a2e1c", color_lejos="#3a2416", semilla=9)], "pan_der", texto=["CASAS DE", "MADERA"], acento=1, amb="viento"),
    E("y soplaba un", LONDRES + [D("fuego", x=300, y=1330, s=1.2, ancho=500), D("particulas", tipo="brasas", n=90)], "pan_der", texto=["VIENTO FUERTE", "Y SECO"], acento=0, amb="fuego"),
    E("El alcalde lo", [C("noche", horizonte=1350), D("ciudad", era="antigua", y=1360), D("fuego", x=820, y=1360, s=.6, ancho=200),
      D("persona", x=380, y=1600, s=1.5, ropa="traje", sombrero="copa")], "push", texto=["«SE APAGA CON", "UN BALDE»"], acento=1, amb="fuego"),
    N("Se equivocó. El", 4, "DÍAS", "DE INCENDIO", icono="🔥"),
    N("quemó más de", 13000, "CASAS", "QUEMADAS", icono="🏠"),
    E("y la antigua", [C("noche", horizonte=1400), D("catedral", aguja=True, x=540, y=1450, s=1.05), D("fuego", x=540, y=1460, s=1.5, ancho=760), D("particulas", tipo="brasas", n=60)],
      "sube", dato=["CATEDRAL DE", "SAN PABLO"], amb="fuego"),
    N("Y lo increíble:", 6, "MUERTOS", "OFICIALMENTE", icono="📜"),
    E("Después, la ciudad", [C("dia", horizonte=1300), D("ciudad", era="colonial", y=1320)], "pan_izq", texto=["PROHIBIDO", "CONSTRUIR CON", "MADERA"], acento=0, amb="multitud", amb_vol=.5),
    FIN("¿Lo habías escuchado?", ["¿LO HABÍAS", "ESCUCHADO?"], capas=LONDRES),
])

# ================================================================ 15 · Termópilas
GRECIA = [C("atardecer", horizonte=1250, astro="sol", astro_x=760, astro_y=820, astro_r=70), D("montanas", horizonte=1260, colores=["#7a4a5a", "#5a3242", "#3a1d2b"]),
          D("suelo", y=1260, colores=["#8a5a3a", "#3a2214"]), D("particulas", tipo="polvo", n=30)]
P[15] = dict(tema="guerra", estilo="calido", claves=["solos.", "siete", "Efialtes", "final."], tomas=[
    E("En la batalla", GRECIA + [D("espartano", x=540, y=1600, s=1.25)], "push", texto=["300", "ESPARTANOS"], acento=0, amb="viento", sfx="boom"),
    E("no estaban solos.", GRECIA + [D("espartano", x=x, y=1500 + (k % 2) * 40, s=.55 + (k % 2) * .05) for k, x in enumerate([120, 300, 480, 660, 840, 1000])],
      "pull", texto=["NO ESTABAN", "SOLOS"], acento=1, amb="multitud", amb_vol=.6),
    T("Fue en el", ["480", "a. C."], acento=0, icono="🏛️"),
    E("El rey Leónidas", GRECIA + [D("espartano", x=480, y=1650, s=1.5), D("corona", x=430, y=620, s=.5)], "push", dato=["REY", "LEÓNIDAS"], amb="viento"),
    M("defendió un paso", [38.8, 22.5], 18, zoom_desde=4, centro_desde=[38, 24], resaltar=["Greece"], pines=[{"lat": 38.8, "lon": 22.5, "texto": "TERMÓPILAS"}]),
    E("entre la montaña", [C("dia", horizonte=1150), MAR("dia", horizonte=1150), D("montanas", horizonte=1300, colores=["#6b7a5a", "#4a5a3e", "#2e3a26"])],
      "pan_der", texto=["UN PASO", "ESTRECHO"], acento=1, amb="olas"),
    E("contra el enorme", GRECIA + [D("ejercito", x=540, y=1500, s=1.1, filas=5, color="#2a1d3a")], "pan_izq", texto=["EJÉRCITO", "PERSA"], acento=1, amb="multitud"),
    N("Pero junto a", 7000, "GRIEGOS", "PELEABAN JUNTO A ELLOS", icono="⚔️"),
    E("Resistieron dos días", GRECIA + [D("calendario", x=540, y=1400, s=1.2, anios=["DÍA 1", "DÍA 2"])], "fijo", texto="RESISTIERON", amb="viento"),
    E("Al tercer día,", [C("noche", horizonte=1300), D("montanas", horizonte=1320), D("persona", x=540, y=1600, s=1.4, ropa="gris", pelo="#1b1b1b", mov="saluda")],
      "push", dato=["EL TRAIDOR", "EFIALTES"], amb="viento"),
    E("un sendero escondido", [C("noche", horizonte=1100), D("montanas", horizonte=1700, colores=["#3b4a6b", "#2a3552", "#1a2238"]), D("huellas", x=300, y=1750, s=1.6, n=12, dx=40, dy=90)],
      "sube", texto=["SENDERO", "ESCONDIDO"], acento=1, amb="viento"),
    E("Rodeados, Leónidas mandó", GRECIA + [D("espartano", x=540, y=1600, s=1.3), D("ejercito", x=540, y=1350, s=.7, filas=3, color="#2a1d3a")],
      "push", texto=["SE QUEDÓ HASTA", "EL FINAL"], acento=1, amb="multitud"),
    FIN("¿Sabías esto? Comenta", ["¿SABÍAS", "ESTO?"], capas=GRECIA),
])

# ================================================================ 16 · Vikingos sin cuernos
FIORDO = [C("niebla", horizonte=1250), D("montanas", horizonte=1260, nieve=True, colores=["#6b7a8a", "#4a5a6b", "#2e3a48"]), MAR("niebla", horizonte=1260)]
P[16] = dict(tema="historia", estilo="retro", claves=["cuernos.", "hierro,", "Wagner.", "siempre."], tomas=[
    E("Los vikingos nunca", [D("interior", pared="#2a3242", piso="#141824", luz_x=540, luz_y=800), D("casco", x=540, y=1450, s=1.6, cuernos=True, tachar=1.2)],
      "push", texto="MITO", sfx="boom", sfx_en=1.2, amb="ninguno"),
    E("Y sabemos de", FIORDO + [D("velero", x=540, y=1290, s=.7, avance=120, reflejo=True)], "pan_der", texto=["¿DE DÓNDE", "SALIÓ?"], acento=1, amb="olas"),
    E("Los arqueólogos solo", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700), D("vitrina", x=540, y=1600, s=1.2), D("casco", x=540, y=1380, s=.8)],
      "push", dato=["SOLO", "1 CASCO"], amb="ninguno"),
    M("en Noruega…", [60.5, 9], 5, zoom_desde=1.6, centro_desde=[50, 10], resaltar=["Norway"], pines=[{"lat": 60.5, "lon": 9, "texto": "NORUEGA"}]),
    E("y es simple,", [D("interior", pared="#2a3242", piso="#141824", luz_x=540, luz_y=900), D("casco", x=540, y=1550, s=2.2)], "push_fuerte",
      texto=["REDONDO", "Y DE HIERRO"], acento=1, amb="ninguno"),
    E("Tiene sentido: los", FIORDO + [D("casco", x=540, y=1350, s=1.4, cuernos=True)], "push", texto=["SE HABRÍAN", "ENGANCHADO"], acento=1, amb="viento"),
    T("y le darían", ["ALGO DE", "DÓNDE AGARRAR"], acento=1, icono="✋"),
    T("La imagen nació", ["1876"], icono="🎭"),
    E("con una ópera", [D("interior", pared="#5a0f1a", piso="#2a0a0e", luz_x=540, luz_y=700), D("luz", x=540, y=900, r=600, color="#fff3c4", op=.5),
      D("persona", x=540, y=1500, s=1.5, ropa="vestido", falda=True, pelo_largo=True, pelo="#d8b04f")], "push", dato=["ÓPERA DE", "WAGNER"], amb="multitud", amb_vol=.4),
    E("El diseñador de", [D("interior", pared="#5a0f1a", piso="#2a0a0e"), D("casco", x=540, y=1450, s=1.7, cuernos=True, cuernos_en=.5)], "push",
      texto=["CUERNOS", "Y ALAS"], acento=0, sfx="whoosh", sfx_en=.5, sfx_dur=.5),
    T("La idea gustó", ["QUEDÓ PARA", "SIEMPRE"], acento=1, icono="🎬"),
    FIN("¿Tú también lo", ["¿TÚ TAMBIÉN", "LO CREÍAS?"], final="si_no", capas=FIORDO),
])

# ================================================================ 23 · Estatua de la Libertad
NY = [C("dia", horizonte=1350), MAR("dia", horizonte=1350)]
P[23] = dict(tema="historia", estilo="frio", claves=["verde.", "Eiffel,", "cobre", "pátina,"], tomas=[
    E("La Estatua de", NY + [D("estatua_libertad", x=540, y=1450, s=1.05, color="verde")], "push", texto=["NO SIEMPRE", "FUE VERDE"], acento=1, amb="olas"),
    E("Cuando llegó a", NY + [D("ciudad", era="moderna", y=1350, color="#4a5a7a", color_lejos="#6b7a9a"), D("estatua_libertad", x=540, y=1480, s=1.05)],
      "pull", dato=["COLOR DE", "MONEDA NUEVA"], amb="olas"),
    M("Fue un regalo", [45, -38], 1.6, zoom_desde=1.0, resaltar=["France", "United States of America"], color_pais="#2f5d9e",
      ruta=[[48.8, 2.3], [40.7, -74]], pines=[{"lat": 48.8, "lon": 2.3, "texto": "FRANCIA"}, {"lat": 40.7, "lon": -74, "texto": "NUEVA YORK"}], paso_pines=1.2),
    E("Viajó en barco,", NY + [D("velero", x=540, y=1380, s=.9, avance=200, reflejo=True)], "pan_der", texto="EN BARCO", amb="olas"),
    N("desarmada en más", 300, "PIEZAS", "MÁS DE", icono="🧩"),
    E("dentro de doscientas", [D("interior", pared="#5a4a3c", piso="#2a1d14"), D("caja", x=300, y=1500, s=.8, cae=True, cae_en=.1), D("caja", x=760, y=1500, s=.8, cae=True, cae_en=.3),
      D("caja", x=530, y=1290, s=.8, cae=True, cae_en=.5), D("caja", x=530, y=1500, s=.8, cae=True, cae_en=.2)], "fijo", texto="214 CAJAS", sfx="patada", sfx_en=.4, sfx_dur=.4),
    E("Por dentro tiene", [C("atardecer", horizonte=1500), D("torre_eiffel", x=300, y=1520, s=1.0), D("estatua_libertad", x=760, y=1520, s=.85)], "push",
      dato=["GUSTAVE", "EIFFEL"], amb="viento", amb_vol=.5),
    E("Por fuera está", [C("dia", horizonte=1900), D("estatua_libertad", x=540, y=2300, s=2.4)], "sube", texto=["LÁMINAS", "DE COBRE"], acento=1, amb="viento", amb_vol=.5),
    T("finas como dos", ["FINAS COMO", "2 MONEDAS"], acento=1, icono="🪙"),
    E("En mil ochocientos", [C("atardecer", horizonte=1350, astro="sol", astro_x=820, astro_y=500, astro_r=70), MAR("atardecer", horizonte=1350),
      D("estatua_libertad", x=480, y=1450, s=1.05)], "push", dato=["1886", "ROJIZA Y DORADA"], amb="olas"),
    E("Con la lluvia", [C("tormenta", horizonte=1350), MAR("tormenta", horizonte=1350), D("estatua_libertad", x=540, y=1450, s=1.05, cambia_en=.4), D("lluvia")],
      "push", texto=["EL COBRE", "SE OXIDÓ"], acento=1, amb="lluvia"),
    N("y en unos", 30, "AÑOS", "PARA QUEDAR VERDE", icono="⏳"),
    E("Esa capa verde,", NY + [D("estatua_libertad", x=540, y=1450, s=1.05, color="verde")], "push", dato=["PÁTINA:", "LA PROTEGE"], amb="olas"),
    FIN("¿Lo sabías? Comenta", ["¿LO", "SABÍAS?"], capas=NY + [D("estatua_libertad", x=540, y=1450, s=1.05, color="verde")], comentario="Siempre pensé que era verde"),
])

# ================================================================ 28 · Hachiko (realista, Tokio años 20)
UENO = dict(ropa="traje", sombrero="fedora", bigote=True, piel="asiatica", pelo="#1b1b1b")
TARDE_JP = [C("atardecer", horizonte=1120, astro="sol", astro_x=820, astro_y=980, astro_r=70, nubes=5), D("pueblo_jp", y=1080, hora="atardecer")]
HACHI = dict(raza="crema", collar=True)
P[28] = dict(tema="cultura", estilo="calido", claves=["diez", "Hachiko", "regresó.", "estatua"], miniatura=0, tomas=[
    E("Este perro esperó", TARDE_JP + [D("anden_hd", fuga_x=700, fuga_y=1080), D("sombra_larga", x=420, y=1660, largo=460, angulo=-14),
      D("perro", x=420, y=1660, s=.95, **HACHI)], "push", dato=["CASI", "10 AÑOS"], amb="viento", amb_vol=.5),
    E("Hachiko era un", TARDE_JP + [D("suelo", y=1120, colores=["#a8906e", "#5a4630"]), D("perro", x=480, y=1700, s=2.1, **HACHI)], "push_fuerte",
      texto="HACHIKO", amb="ninguno"),
    E("Cada día acompañaba", [C("dia", horizonte=1250), D("pueblo_jp", y=1300), D("suelo", y=1300, colores=["#b9a684", "#7a6a50"]),
      D("persona_real", x=330, y=1720, s=1.8, mov="camina", avance=180, **UENO), D("perro", x=620, y=1720, s=.85, **HACHI),
      D("persona_real", x=930, y=1430, s=.9, ropa="kimono", piel="asiatica", pelo="#111")], "pan_der", dato=["PROFESOR", "UENO"], amb="multitud", amb_vol=.5),
    M("a la estación", [35.658, 139.70], 30, zoom_desde=4, centro_desde=[36, 138], resaltar=["Japan"], pines=[{"lat": 35.658, "lon": 139.70, "texto": "SHIBUYA, TOKIO"}]),
    E("y por la", TARDE_JP + [D("estacion_jp", x=540, y=1420, s=1.0), D("suelo", y=1420, colores=["#9a8a70", "#4a3e30"]),
      D("persona_real", x=170, y=1560, s=.9, ropa="kimono_rojo", piel="asiatica", peinado="mono", pelo="#111"),
      D("persona_real", x=900, y=1560, s=.95, ropa="traje_gris", piel="asiatica", sombrero="bombin", pelo="#111"), D("perro", x=560, y=1760, s=1.0, **HACHI)],
      "push", texto=["LO ESPERABA", "A LA SALIDA"], acento=1, amb="multitud", amb_vol=.5),
    F("En mayo de", "21", "MAYO", "1925"),
    E("el profesor sufrió", [D("interior", pared="#6b5040", piso="#3a2a1e", vista="dia", ventana_x=650, papel=True),
      D("persona_real", x=380, y=1560, s=1.9, mov="desvanece", desvanece_en=1.0, **UENO)], "push", texto=["NUNCA", "REGRESÓ"], acento=1, amb="ninguno"),
    E("Hachiko siguió yendo", TARDE_JP + [D("anden_hd", fuga_x=700, fuga_y=1080), D("tren_jp", x=1080, y=1180, s=.55, mov="parte"),
      D("sombra_larga", x=480, y=1700, largo=520, angulo=-14), D("perro", x=480, y=1700, s=1.05, **HACHI)], "fijo", texto="CADA TARDE", amb="tren"),
    E("a la misma", [D("interior", pared="#5a4a3c", piso="#2a1d14"), D("calendario", x=540, y=1180, s=1.3, anios=["1926", "1928", "1930", "1932", "1935"])],
      "fijo", texto="A LA MISMA HORA", sfx="papel", sfx_dur=.6),
    T("hasta su muerte", ["HASTA", "1935"], acento=1, icono="🐾"),
    E("Hoy tiene una", [C("noche", horizonte=1300), D("ciudad", era="moderna", y=1310), D("suelo", y=1300, colores=["#5c6268", "#2a2e33"]),
      D("estatua_perro", x=540, y=1640, s=1.1), D("persona_real", x=200, y=1620, s=1.1, ropa="abrigo", piel="asiatica", pelo="#111"),
      D("persona_real", x=880, y=1620, s=1.05, ropa="camisa", piel="asiatica", pelo="#2a1d14", peinado="largo")], "push", dato=["ESTATUA EN", "SHIBUYA"], amb="multitud", amb_vol=.6),
    FIN("¿Tienes una mascota", ["¿TIENES UNA", "MASCOTA ASÍ?"], capas=TARDE_JP + [D("anden_hd", fuga_x=700, fuga_y=1080), D("perro", x=540, y=1700, s=1.0, **HACHI)],
        comentario="Mi perro me espera siempre 🐶"),
])

# ================================================================ 32 · Momias Chinchorro
ATACAMA = [C("dia", horizonte=1150), MAR("dia", horizonte=1150), D("desierto", y=1250)]
P[32] = dict(tema="historia", estilo="periodico", claves=["Chile.", "siete", "máscara", "Patrimonio"], tomas=[
    E("Las momias más", [C("atardecer", horizonte=1300), D("desierto", y=1300), D("momia", x=540, y=1600, s=1.1)], "push", texto=["LAS MOMIAS", "MÁS ANTIGUAS"], acento=1, amb="viento"),
    E("no están en", [C("dia", horizonte=1350), D("desierto", y=1350), D("piramides", x=540, y=1400, s=1.0)], "pull", texto="NO ESTÁN EN EGIPTO", amb="viento"),
    M("están en Chile.", [-18.48, -70.3], 9, zoom_desde=1.4, centro_desde=[0, -60], resaltar=["Chile"], pines=[{"lat": -18.48, "lon": -70.3, "texto": "ARICA, CHILE"}]),
    E("Los Chinchorro eran", ATACAMA + [D("barca", x=700, y=1170, s=.4, color="#8a6a4a"), D("persona", x=330, y=1560, s=1.1, ropa="obrero", pelo="#111")],
      "pan_der", texto="PESCADORES", amb="olas"),
    N("Momificaban a sus", 7000, "AÑOS", "HACE UNOS", icono="⏳"),
    T("unos dos mil", ["2.000 AÑOS", "ANTES QUE", "EGIPTO"], acento=0),
    E("Y no solo", [C("atardecer", horizonte=1300), D("desierto", y=1300), D("momia", x=300, y=1600, s=.95), D("momia", x=560, y=1600, s=.75, color="#8a1d1d"),
      D("momia", x=780, y=1600, s=.5)], "push", texto=["HOMBRES, MUJERES", "Y NIÑOS"], acento=1, amb="viento"),
    E("Desarmaban el cuerpo,", [D("interior", pared="#5a3a22", piso="#2a1a0e", luz_x=540, luz_y=900), D("momia", x=540, y=1650, s=1.5)], "push",
      texto=["PALOS Y", "FIBRAS"], acento=1, amb="ninguno"),
    E("lo cubrían con", [D("interior", pared="#3a2214", piso="#1a0e08", luz_x=540, luz_y=700), D("momia", x=540, y=1800, s=2.2, color="#8a1d1d")], "push_fuerte",
      texto=["MÁSCARA NEGRA", "O ROJA"], acento=1, amb="ninguno"),
    E("Hoy se siguen", [C("dia", horizonte=1300), D("ciudad", era="colonial", y=1310), D("suelo", y=1300, colores=["#c9a27a", "#8a6a4a"]), D("excavadora", x=540, y=1580, s=1.0)],
      "pan_izq", dato=["AÚN APARECEN", "EN ARICA"], amb="camion", amb_vol=.5),
    T("En dos mil", ["2021:", "PATRIMONIO DE", "LA HUMANIDAD"], acento=0, icono="🏆"),
    FIN("¿Las conocías? Comenta", ["¿LAS", "CONOCÍAS?"], capas=ATACAMA),
])

# ================================================================ 34 · El Caleuche
NIEBLA_NOCHE = [C("noche", horizonte=1200), MAR("noche", horizonte=1200), D("niebla", y=1150, op=.5, color="#9fb4c9")]
P[34] = dict(tema="terror", estilo="neon", claves=["luces…", "Caleuche,", "brujos,", "castigarte."], tomas=[
    E("En las noches", NIEBLA_NOCHE + [D("velero", x=780, y=1220, s=.35, fantasma=True)], "push", amb="olas", texto="CHILOÉ"),
    M("de Chiloé, dicen", [-42.6, -73.9], 10, zoom_desde=1.6, centro_desde=[-30, -70], resaltar=["Chile"], pines=[{"lat": -42.6, "lon": -73.9, "texto": "CHILOÉ"}]),
    E("que aparece un", NIEBLA_NOCHE + [D("velero", x=540, y=1260, s=.9, fantasma=True, avance=80, reflejo=True)], "push", texto=["UN BARCO", "LLENO DE LUCES"], acento=1, amb="olas"),
    T("Es el Caleuche,", ["EL CALEUCHE"], icono="👻"),
    E("Desde la orilla", [C("noche", horizonte=1200), MAR("noche", horizonte=1200), D("velero", x=720, y=1230, s=.5, fantasma=True),
      D("silbido", x1=720, y1=1000, x2=240, color="#3df5ff"), D("suelo", y=1500, colores=["#2a2a1e", "#0d0d08"]), D("persona", x=260, y=1700, s=1.0, ropa="gris")],
      "fijo", texto=["RISAS Y", "ACORDEONES"], acento=1, amb="olas"),
    E("Pero cuando alguien", NIEBLA_NOCHE + [D("velero", x=600, y=1250, s=.8, fantasma=True, hundir_en=.6), D("barca", x=200, y=1290, s=.5, mov="avanza", avance=200)],
      "fijo", texto="SE SUMERGE", amb="olas", sfx="burbujas", sfx_en=.8, sfx_dur=1.5),
    E("Según la leyenda,", NIEBLA_NOCHE + [D("velero", x=540, y=1300, s=1.2, fantasma=True), D("ojos", x=540, y=950, s=1.2, en=.4, color="#3df5ff")],
      "push", texto=["LO TRIPULAN", "BRUJOS"], acento=1, amb="olas"),
    E("y recoge a", [C("noche", horizonte=700), MAR("noche", horizonte=700), D("particulas", tipo="verde", n=50), D("velero", x=540, y=720, s=.6, fantasma=True)],
      "baja", texto=["LOS AHOGADOS", "DEL MAR"], acento=0, amb="burbujas", amb_vol=.6),
    E("en una fiesta", NIEBLA_NOCHE + [D("velero", x=540, y=1280, s=1.1, fantasma=True), D("luz", x=540, y=950, r=600, color="#3df5ff", op=.4, parpadeo=True)],
      "push", texto=["UNA FIESTA", "SIN FIN"], acento=1, amb="olas"),
    E("Algunos pescadores aseguran", NIEBLA_NOCHE + [D("barca", x=300, y=1300, s=.9), D("persona", x=300, y=1260, s=.6, ropa="obrero"), D("velero", x=800, y=1230, s=.4, fantasma=True, avance=-120)],
      "pan_izq", texto="EN SILENCIO", amb="olas"),
    E("Y dicen que,", [C("noche", horizonte=1900), D("niebla", y=1000, op=.6, color="#9fb4c9"), D("ojos", x=540, y=900, s=2.0, en=.5, color="#ff2a2a")],
      "push_fuerte", texto=["NO LO MIRES", "DEMASIADO"], acento=0, amb="viento"),
    FIN("¿Has escuchado esta", ["¿CONOCÍAS", "ESTA LEYENDA?"], capas=NIEBLA_NOCHE + [D("velero", x=540, y=1260, s=.7, fantasma=True)]),
])

# ================================================================ 36 · Callejón del Beso
COLONIAL = dict(pared="#8a4a2a", piso="#3a1d10", papel=True)
P[36] = dict(tema="cultura", estilo="pop", claves=["balcones", "minero", "tragedia.", "siete"], tomas=[
    M("En Guanajuato, México,", [21.02, -101.26], 9, zoom_desde=1.5, centro_desde=[20, -95], resaltar=["Mexico"], pines=[{"lat": 21.02, "lon": -101.26, "texto": "GUANAJUATO"}]),
    E("hay un callejón", [D("callejon")], "sube", texto=["CALLEJÓN", "DEL BESO"], acento=1, amb="viento", amb_vol=.4),
    E("que dos balcones", [D("callejon")], "push_fuerte", texto=["CASI SE", "TOCAN"], acento=1, amb="ninguno"),
    E("Cuenta la leyenda", [D("interior", **COLONIAL, vista="noche", ventana_x=640), D("persona", x=380, y=1450, s=1.3, ropa="vestido", falda=True, pelo_largo=True, pelo="#1b1b1b", mov="respira")],
      "push", dato="CARMEN", amb="ninguno"),
    E("hija de un", [D("interior", **COLONIAL), D("persona", x=540, y=1600, s=1.8, ropa="traje", pelo="#555")], "push_fuerte", texto=["PADRE ESTRICTO", "Y CELOSO"], acento=1, amb="ninguno"),
    E("se enamoró de", [C("noche", horizonte=1400), D("casa", tipo="colonial", x=540, y=1450, s=1.4), D("suelo", y=1450, colores=["#6b5a46", "#2a1d14"]),
      D("persona", x=260, y=1700, s=1.0, ropa="obrero", sombrero="fedora")], "pan_der", dato=["LUIS,", "MINERO"], amb="viento", amb_vol=.4),
    E("Luis alquiló la", [D("callejon")], "push", texto=["LA CASA", "DE ENFRENTE"], acento=1, amb="ninguno"),
    N("Los balcones estaban", 70, "CENTÍMETROS", "DE SEPARACIÓN", icono="📏"),
    E("y desde ahí", [D("callejon", pareja=True)], "push", texto=["BESOS A", "ESCONDIDAS"], acento=0, amb="ninguno"),
    E("Hasta que el", [D("callejon"), D("luz", x=540, y=600, r=800, color="#ff2a2a", op=.45, parpadeo=True)], "push_fuerte", texto=["LOS", "DESCUBRIÓ"], acento=1,
      sfx="boom", sacudir=True),
    E("Por eso, dicen,", [D("callejon", hora="dia", escalon="#b9a88a")], "baja", texto=["EL TERCER", "ESCALÓN"], acento=1, amb="multitud", amb_vol=.4),
    T("tendrán siete años", ["7 AÑOS DE", "FELICIDAD"], acento=1, icono="💋"),
    T("Y las que", ["…O 7 DE", "MALA SUERTE"], acento=1, icono="🐈‍⬛"),
    FIN("¿Te besarías ahí?", ["¿TE BESARÍAS", "AHÍ?"], final="si_no", capas=[D("callejon", pareja=True)]),
])

# ================================================================ 41 · El cerebro de Einstein
OFICINA = dict(pared="#4a5a6a", piso="#1d2530", luz_x=300, luz_y=500)
P[41] = dict(tema="ciencia", estilo="clasico", claves=["permiso.", "doscientos", "sidra", "museos."], tomas=[
    E("Cuando Albert Einstein", [D("interior", **OFICINA, vista="dia", ventana_x=650), D("texto_svg", x=800, y=420, texto="E = mc²", tam=110, color="#f4efe4"),
      D("persona", x=380, y=1450, s=1.3, ropa="gris", pelo="#ececec", mov="respira")], "push", dato=["1955", "EINSTEIN"], amb="ninguno"),
    E("un médico se", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz=False), D("persona", x=330, y=1450, s=1.2, ropa="bata"), D("frasco", x=740, y=1400, s=1.0)],
      "push", texto=["SE LLEVÓ", "SU CEREBRO"], acento=1, amb="ninguno"),
    T("sin permiso.", ["SIN", "PERMISO"], acento=1, icono="🤫", entrada="flash"),
    E("Einstein había pedido", [D("interior", pared="#2a2a2a", piso="#111"), D("velas", x=540, y=1400, s=1.5, n=5)], "push", texto=["PIDIÓ SER", "CREMADO"], acento=1, amb="ninguno"),
    E("Pero el patólogo", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz=False), D("persona", x=540, y=1650, s=2.0, ropa="bata", pelo="#3a2a1e")], "push_fuerte",
      dato=["THOMAS", "HARVEY"], amb="ninguno"),
    E("decidió guardar su", [D("interior", pared="#1d2233", piso="#0d1018"), D("cerebro", x=540, y=1400, s=1.4), D("particulas", tipo="chispas", n=25)],
      "push", texto=["¿QUÉ LO HACÍA", "GENIAL?"], acento=1, amb="ninguno"),
    E("Lo cortó en", [D("interior", pared="#1d2233", piso="#0d1018"), D("cerebro", x=540, y=1400, s=1.4, corte=True)], "fijo", texto="+200 PEDAZOS", amb="ninguno", sfx="crujido", sfx_dur=1.5),
    T("Perdió su trabajo", ["PERDIÓ SU", "TRABAJO"], acento=1, icono="📦"),
    E("Durante décadas guardó", [D("interior", pared="#5a4a3c", piso="#2a1d14"), D("mesa", x=540, y=1500, s=1.2), D("frasco", x=330, y=1240, s=.65),
      D("frasco", x=540, y=1240, s=.65), D("frasco", x=750, y=1240, s=.65)], "pan_der", texto="EN FRASCOS", amb="ninguno"),
    E("y en algún", [D("interior", pared="#3a3a3a", piso="#1d1d1d"), D("caja", x=540, y=1500, s=1.4, texto="SIDRA")], "push", texto=["UNA CAJA", "DE SIDRA"], acento=1,
      sfx="patada", sfx_dur=.4),
    T("Recién en mil", ["1998:", "LO DEVOLVIÓ"], acento=1, icono="🏥"),
    E("Hoy hay partes", [D("interior", pared="#2a3242", piso="#141824", luz_x=540, luz_y=700), D("vitrina", x=540, y=1600, s=1.2), D("frasco", x=540, y=1380, s=.75)],
      "push", dato="EN MUSEOS", amb="ninguno"),
    FIN("¿Lo sabías? Comenta", ["¿LO", "SABÍAS?"], comentario="¡Qué locura! 🧠"),
])

# ================================================================ 42 · Marie Curie
LAB = dict(pared="#3a4a4a", piso="#1a2424", luz_x=700, luz_y=600)
P[42] = dict(tema="ciencia", estilo="terror", claves=["radiactivos…", "Nobel,", "bolsillos.", "plomo,"], tomas=[
    E("Los cuadernos de", [D("interior", pared="#141a18", piso="#0a0e0c", luz=False), D("libro", x=540, y=1450, s=1.4, radiactivo=True), D("particulas", tipo="verde", n=40)],
      "push", texto="RADIACTIVOS", amb="zumbido", amb_vol=.6),
    N("y lo seguirán", 1500, "AÑOS", "MÁS DE", icono="☢️"),
    E("Marie Curie descubrió", [D("interior", **LAB, vista="dia", ventana_x=650), D("persona", x=380, y=1450, s=1.3, ropa="vestido", falda=True, pelo_largo=True, pelo="#6b5a46"),
      D("mesa", x=760, y=1500, s=.7), D("frasco", x=760, y=1250, s=.55, contenido="liquido"), D("luz", x=760, y=1150, r=220, color="#8dff9c", op=.8)],
      "push", dato=["MARIE", "CURIE"], amb="ninguno"),
    T("el polonio y", ["POLONIO", "Y RADIO"], acento=1, icono="⚛️"),
    T("Fue la primera", ["1.ª MUJER CON", "UN NOBEL"], acento=1, icono="🏅"),
    N("y la primera", 2, "PREMIOS NOBEL", "EN CIENCIAS DISTINTAS", icono="🏅"),
    E("En esa época", [D("interior", **LAB), D("mesa", x=540, y=1500, s=1.2), D("frasco", x=360, y=1240, s=.6, contenido="liquido"), D("frasco", x=720, y=1240, s=.6, contenido="liquido"),
      D("luz", x=540, y=1150, r=500, color="#8dff9c", op=.6, parpadeo=True)], "push", texto=["NADIE CONOCÍA", "LOS PELIGROS"], acento=1, amb="zumbido", amb_vol=.5),
    E("guardaba tubos de", [D("interior", **LAB), D("persona", x=540, y=1600, s=1.7, ropa="vestido", falda=True, pelo_largo=True, pelo="#6b5a46"),
      D("luz", x=600, y=1350, r=200, color="#8dff9c", op=.9, parpadeo=True)], "push_fuerte", texto=["TUBOS EN LOS", "BOLSILLOS"], acento=1, amb="zumbido", amb_vol=.5),
    E("Murió en mil", [D("interior", pared="#1a1a1a", piso="#0a0a0a"), D("velas", x=540, y=1400, s=1.4, n=4)], "push", dato="1934", amb="ninguno"),
    E("Hoy sus cuadernos", [D("interior", pared="#2a2f38", piso="#14171c", luz_x=540, luz_y=800), D("caja", x=540, y=1500, s=1.5, plomo=True)], "push",
      texto=["CAJAS DE", "PLOMO"], acento=1, amb="ninguno"),
    M("en París. Para", [48.85, 2.35], 25, zoom_desde=4, centro_desde=[47, 5], resaltar=["France"], pines=[{"lat": 48.85, "lon": 2.35, "texto": "PARÍS"}]),
    E("hay que firmar", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz=False), D("persona", x=330, y=1450, s=1.2, ropa="bata", sombrero="cofia"), D("carta", x=760, y=1450, s=.55, texto="PERMISO", firma="FIRMA")],
      "push", texto=["ROPA", "PROTECTORA"], acento=1, amb="ninguno", sfx="papel", sfx_dur=.6),
    FIN("¿Te atreverías a", ["¿TE ATREVERÍAS", "A LEERLOS?"], final="si_no", capas=[D("interior", pared="#141a18", piso="#0a0e0c", luz=False), D("libro", x=540, y=1500, s=1.2, radiactivo=True)]),
])

# ================================================================ 43 · Phineas Gage
VIA = [C("dia", horizonte=1250), D("montanas", horizonte=1260, colores=["#6b7a5a", "#4a5a3e", "#2e3a26"]), D("suelo", y=1260, colores=["#8a6a4a", "#4a3222"])]
P[43] = dict(tema="ciencia", estilo="periodico", claves=["hablando.", "cráneo", "Gage»:", "cerebro"], tomas=[
    E("En mil ochocientos", [D("interior", pared="#1d2233", piso="#0d1018", luz_x=540, luz_y=800), D("craneo", x=540, y=1450, s=1.4, en=.4)], "push", dato="1848",
      sfx="boom", sfx_en=.4, sacudir=True),
    T("y siguió hablando.", ["¡Y SIGUIÓ", "HABLANDO!"], acento=1, entrada="flash"),
    E("Phineas Gage era", VIA + [D("persona", x=540, y=1600, s=1.5, ropa="obrero", sombrero="fedora", mov="respira")], "push", dato=["PHINEAS", "GAGE"], amb="viento", amb_vol=.5),
    E("en la construcción", VIA + [D("tren", x=540, y=1400, s=1.0)], "pan_der", texto="FERROCARRIL", amb="tren"),
    E("La explosión lanzó", VIA + [D("explosion", x=540, y=1250, s=1.4, en=.1), D("particulas", tipo="polvo", n=50)], "fijo", sacudir=True, sfx="explosion_lejana", sfx_dur=2.0,
      texto="¡EXPLOSIÓN!"),
    N("una barra de", 6, "KILOS", "MÁS DE 1 METRO DE HIERRO", icono="🔩"),
    E("Le entró por", [D("interior", pared="#1d2233", piso="#0d1018"), D("craneo", x=540, y=1500, s=1.7, en=.2)], "push_fuerte", texto=["ATRAVESÓ", "SU CRÁNEO"], acento=1),
    E("Gage sobrevivió, habló", VIA + [D("persona", x=300, y=1600, s=1.3, ropa="obrero", sombrero="fedora", mov="camina", avance=260)], "pan_der", texto="¡SOBREVIVIÓ!", amb="viento", amb_vol=.5),
    T("Pero sus amigos", ["«YA NO", "ERA GAGE»"], acento=1),
    E("el hombre amable", [D("interior", pared="#3a1d1d", piso="#1a0d0d"), D("luz", x=540, y=800, r=700, color="#ff2a2a", op=.35), D("persona", x=540, y=1700, s=2.1, ropa="obrero", sombrero="fedora")],
      "push_fuerte", texto=["IMPACIENTE", "Y GROSERO"], acento=1, sacudir=True),
    E("Su caso ayudó", [D("interior", pared="#1d2233", piso="#0d1018"), D("cerebro", x=540, y=1450, s=1.5, zona="frontal")], "push",
      texto=["CADA PARTE", "TIENE SU FUNCIÓN"], acento=1, amb="ninguno"),
    FIN("¿Conocías este caso?", ["¿CONOCÍAS", "ESTE CASO?"], capas=[D("interior", pared="#1d2233", piso="#0d1018"), D("cerebro", x=540, y=1500, s=1.2)]),
])

# ================================================================ 44 · Coca y cocaína
P[44] = dict(tema="historia", estilo="retro", claves=["cocaína.", "coca,", "cola,", "cafeína."], tomas=[
    E("La Coca-Cola original", [D("mostrador", y=1350), D("botella", x=540, y=1380, s=1.4)], "push", texto=["TENÍA", "COCAÍNA"], acento=1, amb="ninguno", sfx="boom"),
    T("Fue creada en", ["1886"], icono="🥤"),
    M("en Atlanta, por", [33.75, -84.39], 9, zoom_desde=1.5, centro_desde=[38, -95], resaltar=["United States of America"], pines=[{"lat": 33.75, "lon": -84.39, "texto": "ATLANTA"}]),
    E("el farmacéutico John", [D("mostrador", y=1400), D("persona", x=540, y=1420, s=1.3, ropa="bata", pelo="#555")], "push", dato=["JOHN", "PEMBERTON"], amb="ninguno"),
    E("un veterano de", [C("atardecer", horizonte=1300), D("suelo", y=1300, colores=["#6b5a46", "#2a1d14"]), D("persona", x=540, y=1650, s=1.6, ropa="gris", sombrero="gorra", color_sombrero="#555")],
      "push", texto=["VETERANO", "DE GUERRA"], acento=1, amb="viento", amb_vol=.5),
    E("Se vendía en", [D("mostrador", y=1350), D("botella", x=360, y=1380, s=1.0), D("botella", x=720, y=1380, s=1.0, texto="NERVIOS")], "pan_der",
      texto=["TÓNICO PARA", "LOS NERVIOS"], acento=1, amb="ninguno"),
    E("Su receta incluía", [D("interior", pared="#2e4a2a", piso="#141f12", luz_x=540, luz_y=800), D("hoja", x=540, y=1450, s=1.6)], "push", texto=["HOJAS", "DE COCA"], acento=1, amb="ninguno"),
    E("La otra parte", [D("interior", pared="#4a3020", piso="#21140c", luz_x=540, luz_y=800), D("nuez", x=540, y=1400, s=1.8)], "push", texto=["NUEZ", "DE COLA"], acento=1, amb="ninguno"),
    T("que aportaba cafeína.", ["CAFEÍNA"], icono="☕"),
    E("Al principio se", [D("mostrador", y=1350), D("taza", x=540, y=1380, s=1.1)], "push", texto=["CON AGUA", "CON GAS"], acento=1, sfx="burbujas", sfx_dur=1.5),
    T("A comienzos del", ["SIGLO XX:", "SIN COCAÍNA"], acento=1, icono="🚫"),
    FIN("¿Lo sabías? Comenta", ["¿LO", "SABÍAS?"], capas=[D("mostrador", y=1350)], comentario="¡No tenía idea! 😮"),
])

# ================================================================ 45 · Kétchup medicinal
FARMACIA = [D("mostrador", y=1350)]
P[45] = dict(tema="historia", estilo="calido", claves=["medicina.", "venenoso.", "pastillas", "escándalo,"], tomas=[
    E("En el siglo", FARMACIA + [D("botella", x=540, y=1380, s=1.4, color="#a81d14", texto="KÉTCHUP", sub="MEDICINAL")], "push", texto=["SE VENDÍA EN", "FARMACIAS"], acento=1, amb="ninguno"),
    T("como medicina.", ["COMO", "MEDICINA"], acento=1, icono="💊", entrada="flash"),
    T("Antes, el kétchup", ["NI SIQUIERA ERA", "DE TOMATE"], acento=1, icono="🍅"),
    E("se hacía con", [D("interior", pared="#5a3a22", piso="#2a1a0e"), D("mesa", x=540, y=1500, s=1.2), D("nuez", x=380, y=1240, s=.7), D("frasco", x=700, y=1240, s=.6, contenido="liquido")],
      "pan_der", texto=["PESCADO, NUECES", "Y HONGOS"], acento=0, amb="ninguno"),
    E("En Estados Unidos", [D("interior", pared="#1d2a1d", piso="#0d140d", luz=False), D("tomate", x=540, y=1400, s=1.8), D("luz", x=540, y=1100, r=500, color="#8dff9c", op=.4)],
      "push", texto="¿VENENOSO?", amb="ninguno"),
    E("En mil ochocientos", FARMACIA + [D("persona", x=540, y=1420, s=1.3, ropa="traje", sombrero="copa")], "push", dato=["1834", "DR. BENNETT"], amb="ninguno"),
    E("aseguró que el", [D("interior", pared="#5a1d14", piso="#2a0e0a", luz_x=540, luz_y=900), D("tomate", x=540, y=1400, s=1.6), D("particulas", tipo="chispas", n=30)],
      "push_fuerte", texto="¡CURA TODO!", amb="ninguno"),
    E("Empezó a vender", FARMACIA + [D("frasco", x=540, y=1380, s=1.3, contenido="pildoras", etiqueta="TOMATE")], "push", texto=["PASTILLAS", "DE TOMATE"], acento=1, amb="ninguno"),
    E("y tuvieron tanto", FARMACIA + [D("frasco", x=x, y=1380, s=.7, contenido="pildoras", etiqueta="TOMATE") for x in (220, 430, 650, 860)], "pan_izq", texto="¡ÉXITO!", amb="multitud", amb_vol=.5),
    E("que aparecieron imitadores", FARMACIA + [D("frasco", x=360, y=1380, s=.9, contenido="pildoras", etiqueta="FALSO"), D("frasco", x=720, y=1380, s=.9, contenido="pildoras", etiqueta="FALSO")],
      "push", texto=["PÍLDORAS", "FALSAS"], acento=1),
    E("El negocio terminó", [D("interior", pared="#3a2a1e", piso="#1a120c"), D("periodico", x=540, y=1560, s=1.1, cabecera="1840", titular="¡ESCÁNDALO!")], "fijo", sfx="papel", sfx_dur=.6),
    E("y el kétchup", [D("interior", pared="#7a3a2a", piso="#3a1a10", vista="dia", ventana_x=650), D("mesa", x=540, y=1500, s=1.2), D("botella", x=540, y=1240, s=.9, color="#a81d14", texto="KÉTCHUP", sub="")],
      "push", texto=["SOLO UNA", "SALSA"], acento=1, amb="ninguno"),
    FIN("¿Con qué comes", ["¿CON QUÉ", "LO COMES TÚ?"], comentario="Con papas fritas 🍟"),
])

# ================================================================ 46 · Cacao como dinero
SELVA = [C("dia", horizonte=1300), D("arboles", y=1320, n=7, color="#2e5a2a"), D("suelo", y=1320, colores=["#5a4a2a", "#2a2214"])]
TENOCH = [C("atardecer", horizonte=1350, astro="sol", astro_x=820, astro_y=600, astro_r=70), D("suelo", y=1350, colores=["#a8845a", "#5a4430"])]
P[46] = dict(tema="cultura", estilo="frio", claves=["dinero.", "tributo.", "cien,", "Europa."], tomas=[
    E("Para los aztecas,", TENOCH + [D("templo_azteca", x=540, y=1400, s=1.05)], "push", texto="LOS AZTECAS", amb="viento", amb_vol=.5),
    E("el chocolate no", [D("interior", pared="#6b3a1e", piso="#2a160a", luz_x=540, luz_y=900), D("taza", x=540, y=1450, s=1.6)], "push", texto=["NO SE COMÍA:", "SE BEBÍA"], acento=1),
    E("y las semillas", [D("interior", pared="#4a2e1a", piso="#21140c", luz_x=540, luz_y=900), D("semillas", x=540, y=1500, s=1.6)], "fijo", texto=["ERAN", "DINERO"], acento=1, sfx="billetes", sfx_dur=1.0),
    M("El cacao no", [19.43, -99.13], 12, zoom_desde=2, centro_desde=[22, -100], resaltar=["Mexico"], pines=[{"lat": 19.43, "lon": -99.13, "texto": "VALLE DE MÉXICO"}]),
    E("llegaba desde tierras", SELVA + [D("cacao", x=540, y=1600, s=1.2), D("particulas", tipo="polvo", n=20)], "push", texto=["DE TIERRAS", "CÁLIDAS"], acento=1, amb="insectos"),
    T("Por eso era", ["MUY", "VALIOSO"], acento=1, icono="💰"),
    E("Con unas pocas", [D("interior", pared="#4a2e1a", piso="#21140c"), D("semillas", x=330, y=1500, s=.8), D("tomate", x=760, y=1500, s=1.0)], "pan_der",
      texto=["FRUTA O", "UN TAMAL"], acento=1),
    N("y con unas", 100, "SEMILLAS", "= 1 GUAJOLOTE", icono="🦃"),
    E("Había hasta falsificadores,", [D("interior", pared="#2a1a10", piso="#120c06", luz_x=540, luz_y=700), D("cacao", x=540, y=1450, s=1.4)], "push",
      texto="FALSIFICADORES", sacudir=True, sfx="boom"),
    E("que vaciaban las", [D("interior", pared="#2a1a10", piso="#120c06"), D("semillas", x=540, y=1500, s=1.4)], "push", texto=["RELLENAS DE", "TIERRA O CERA"], acento=1),
    E("La bebida era", [D("interior", pared="#6b3a1e", piso="#2a160a", luz_x=540, luz_y=900), D("taza", x=540, y=1450, s=1.4)], "push", texto=["AMARGA Y", "ESPUMOSA"], acento=0),
    E("y la tomaban", TENOCH + [D("templo_azteca", x=540, y=1400, s=.8), D("persona", x=300, y=1650, s=1.2, ropa="rojo", pelo="#111"), D("persona", x=780, y=1650, s=1.2, ropa="azul", pelo="#111")],
      "pull", texto=["NOBLES Y", "GUERREROS"], acento=1, amb="multitud", amb_vol=.4),
    E("El azúcar se", [C("dia", horizonte=1250), MAR("dia", horizonte=1250), D("velero", x=540, y=1290, s=.9, avance=180, reflejo=True)], "pan_der", texto=["EL AZÚCAR:", "EN EUROPA"], acento=1, amb="olas"),
    FIN("¿Lo prefieres dulce", ["¿DULCE O", "AMARGO?"], comentario="Dulce, obvio 🍫"),
])

# ================================================================ 51 · Drácula real
NOCHE_CASTILLO = [C("noche", horizonte=1350, astro="luna", astro_x=800, astro_y=420, astro_r=80), D("montanas", horizonte=1380, colores=["#2a2f45", "#1d2135", "#121526"])]
P[51] = dict(tema="terror", estilo="terror", claves=["vampiro.", "dragón».", "Empalador.", "estacas."], tomas=[
    E("Drácula existió… pero", NOCHE_CASTILLO + [D("castillo", x=540, y=1420, s=1.0), D("niebla", y=1380, op=.4)], "push", texto=["DRÁCULA", "EXISTIÓ"], acento=0, amb="viento"),
    T("pero no era", ["NO ERA UN", "VAMPIRO"], acento=1, icono="🦇", entrada="flash"),
    E("Se llamaba Vlad", [D("interior", pared="#3a1d1d", piso="#1a0d0d", luz_x=540, luz_y=700), D("trono", x=540, y=1500, s=1.1),
      D("persona", x=540, y=1480, s=1.15, ropa="rojo", pelo="#111", pelo_largo=True)], "push", dato=["VLAD", "III"], amb="ninguno"),
    M("y gobernó Valaquia,", [44.7, 25.5], 7, zoom_desde=1.6, centro_desde=[48, 15], resaltar=["Romania"], pines=[{"lat": 44.7, "lon": 25.5, "texto": "VALAQUIA"}]),
    T("en el siglo", ["SIGLO XV"], icono="🏰"),
    T("Su padre pertenecía", ["ORDEN DEL", "DRAGÓN"], acento=1, icono="🐉"),
    T("por eso lo", ["DRÁCULA:", "«HIJO DEL DRAGÓN»"], acento=1),
    E("Era famoso por", NOCHE_CASTILLO + [D("castillo", x=540, y=1420, s=1.1), D("luz", x=540, y=900, r=800, color="#ff2a2a", op=.35)], "push_fuerte", texto="CRUEL", amb="viento"),
    T("Le decían Vlad", ["VLAD EL", "EMPALADOR"], acento=1),
    E("Se cuenta que,", [C("atardecer", horizonte=1300), D("suelo", y=1300, colores=["#4a3a2a", "#1a120c"]), D("ejercito", x=540, y=1500, s=1.0, avance=-260, color="#1a1020")],
      "pan_izq", texto=["DIERON MEDIA", "VUELTA"], acento=1, amb="multitud"),
    E("al ver un", [C("rojo", horizonte=1350), D("estacas", x=540, y=1450, s=1.0), D("suelo", y=1420, colores=["#1a0d0d", "#0a0505"])], "pan_der",
      texto=["UN BOSQUE", "DE ESTACAS"], acento=1, amb="viento"),
    E("Cuatrocientos años después,", [D("interior", pared="#2a2218", piso="#120e0a", luz_x=540, luz_y=900), D("velas", x=800, y=1300, s=.8, n=3), D("libro", x=460, y=1400, s=1.0)],
      "push", dato=["BRAM STOKER", "1897"], amb="ninguno"),
    E("Curiosamente, Vlad nunca", [C("dia", horizonte=1350), D("montanas", horizonte=1380, colores=["#6b7a5a", "#4a5a3e", "#2e3a26"]), D("castillo", x=540, y=1420, s=1.0)],
      "pull", texto=["NUNCA VIVIÓ", "EN BRAN"], acento=1, amb="viento", amb_vol=.5),
    FIN("¿Sabías que Drácula", ["¿SABÍAS QUE", "FUE REAL?"], final="si_no", capas=NOCHE_CASTILLO + [D("castillo", x=540, y=1420, s=1.0)]),
])

# ================================================================ 54 · La Catrina
MUERTOS = [D("interior", pared="#3a1d4a", piso="#1a0d22", luz_x=540, luz_y=900), D("particulas", tipo="chispas", n=25)]
P[54] = dict(tema="cultura", estilo="neon", claves=["burla.", "Garbancera».", "muerte.", "«Catrina»."], tomas=[
    E("La Catrina, el", MUERTOS + [D("calavera", x=540, y=1500, s=1.4), D("velas", x=540, y=1700, s=1.0, n=7)], "push", texto="LA CATRINA", amb="ninguno"),
    T("nació como una", ["NACIÓ COMO", "UNA BURLA"], acento=1, icono="😏"),
    E("A comienzos del", [D("interior", pared="#5a4a3c", piso="#2a1d14", vista="dia", ventana_x=650), D("mesa", x=600, y=1500, s=1.0),
      D("persona", x=330, y=1450, s=1.25, ropa="traje", pelo="#2a1a10"), D("libro", x=620, y=1250, s=.5)], "push", dato=["JOSÉ GUADALUPE", "POSADA"], amb="ninguno"),
    E("dibujaba calaveras para", [D("interior", pared="#3a2a1e", piso="#1a120c"), D("periodico", x=540, y=1560, s=1.1, cabecera="1910", titular="CALAVERAS", tam=86)], "fijo",
      texto="PARA CRITICAR", sfx="papel", sfx_dur=.6),
    E("Una de ellas", MUERTOS + [D("calavera", x=540, y=1600, s=1.9)], "push_fuerte", texto=["SOMBRERO", "DE PLUMAS"], acento=1),
    T("Se llamaba «La", ["«LA CALAVERA", "GARBANCERA»"], acento=1, icono="💀"),
    E("Se burlaba de", [D("interior", pared="#6b2d3f", piso="#2a0e14", papel=True), D("persona", x=360, y=1500, s=1.3, ropa="traje", sombrero="copa"),
      D("persona", x=720, y=1500, s=1.3, ropa="vestido", falda=True, pelo_largo=True)], "push", texto=["QUERÍAN PARECER", "EUROPEOS"], acento=1),
    E("El mensaje era", MUERTOS + [D("calavera", x=280, y=1500, s=.8, sombrero=False), D("calavera", x=540, y=1500, s=.95), D("calavera", x=800, y=1500, s=.8, sombrero=False)],
      "pull", texto=["TODOS IGUALES", "EN LA MUERTE"], acento=1),
    E("Años después, el", [D("interior", pared="#c98b5b", piso="#5a3a22", luz=False), D("calavera", x=540, y=1350, s=1.0), D("persona", x=540, y=1700, s=1.0, ropa="vestido", falda=True)],
      "pan_der", dato=["MURAL DE", "DIEGO RIVERA"]),
    T("y la llamó", ["«CATRINA»"], icono="🌼"),
    FIN("¿Tú celebras el", ["¿CELEBRAS EL", "DÍA DE MUERTOS?"], capas=MUERTOS + [D("velas", x=540, y=1700, s=1.0, n=7)], comentario="¡Sí, cada año! 🕯️"),
])

# ================================================================ 57 · Maracanazo
P[57] = dict(tema="cultura", estilo="pop", claves=["campeón", "empate", "Ghiggia", "«Maracanazo»."], tomas=[
    F("El dieciséis de", "16", "JULIO", "1950"),
    E("unas doscientas mil", [D("estadio")], "pan_der", texto="200.000 PERSONAS", amb="multitud", amb_vol=1.4),
    M("para ver a", [-22.912, -43.23], 20, zoom_desde=1.5, centro_desde=[-15, -50], resaltar=["Brazil"], pines=[{"lat": -22.912, "lon": -43.23, "texto": "MARACANÁ"}]),
    T("A Brasil le", ["LE BASTABA", "UN EMPATE"], acento=1, icono="🇧🇷"),
    E("contra Uruguay en", [C("dia", horizonte=1500), D("suelo", y=1500, colores=["#2f7d32", "#174d1a"]), D("bandera", x=250, y=1500, s=1.2, colores=["#1e9b3a", "#ffdf00", "#1e9b3a"]),
      D("bandera", x=640, y=1500, s=1.2, colores=["#ffffff", "#4f8fd8", "#ffffff", "#4f8fd8", "#ffffff"])], "push", texto=["BRASIL", "VS URUGUAY"], acento=1, amb="multitud"),
    E("Los diarios ya", [D("interior", pared="#3a2a1e", piso="#1a120c"), D("periodico", x=540, y=1560, s=1.1, cabecera="1950", titular="¡CAMPEONES!")], "fijo", sfx="papel", sfx_dur=.6),
    T("y hasta había", ["MEDALLAS CON", "SUS NOMBRES"], acento=0, icono="🥇"),
    E("Brasil se puso", [D("estadio")], "push", texto=["1 - 0"], amb="multitud", amb_vol=1.6),
    E("Pero Uruguay empató,", [D("estadio"), D("arco", x=540, y=1600, s=.9), D("balon", x=540, y=1580, s=1.0, mov="gol", en=.3)], "push", texto="1 - 1", amb="multitud", amb_vol=1.2),
    N("y a once", 11, "MINUTOS", "DEL FINAL", icono="⏱️"),
    E("Alcides Ghiggia disparó", [D("estadio"), D("arco", x=540, y=1600, s=1.0), D("balon", x=640, y=1560, s=1.2, mov="gol", en=.5)], "push_fuerte", dato="GHIGGIA", amb="multitud"),
    T("y marcó el", ["2 - 1"], icono="⚽", tam=300, sfx="boom"),
    E("El estadio quedó", [D("estadio", silencio=True)], "pull", texto=["SILENCIO", "TOTAL"], acento=0, amb="viento", amb_vol=.4),
    T("y ese día", ["«EL", "MARACANAZO»"], acento=1, icono="🇺🇾"),
    FIN("¿De qué país", ["¿DE QUÉ PAÍS", "ERES HINCHA?"], capas=[D("estadio")], comentario="¡Arriba Chile! 🇨🇱"),
])

# ================================================================ 58 · Silbo gomero
GOMERA = [C("dia", horizonte=1200), D("montanas", horizonte=1600, colores=["#5a7a4a", "#3e5a32", "#2a3e22"])]
P[58] = dict(tema="cultura", estilo="clasico", claves=["silbando.", "Gomera,", "kilómetros", "UNESCO"], tomas=[
    E("En una isla", [C("dia", horizonte=1250), MAR("dia", horizonte=1250), D("isla", x=540, y=1280, s=1.1, arboles=9)], "push", texto=["UNA ISLA", "DE ESPAÑA"], acento=1, amb="olas"),
    E("la gente puede", GOMERA + [D("persona", x=180, y=1350, s=.8, ropa="blanco"), D("persona", x=900, y=1450, s=.8, ropa="rojo", espejo=True),
      D("silbido", x1=240, y1=1080, x2=850)], "fijo", texto="¡SILBANDO!", sfx="campana", sfx_dur=.4, amb="viento", amb_vol=.5),
    T("Es el silbo", ["EL SILBO", "GOMERO"], acento=1, icono="😙"),
    M("de la isla", [28.1, -17.23], 40, zoom_desde=4, centro_desde=[30, -10], resaltar=["Spain"], pines=[{"lat": 28.1, "lon": -17.23, "texto": "LA GOMERA"}]),
    E("La isla está", [C("dia", horizonte=900), D("montanas", horizonte=1900, colores=["#4a6a3a", "#2e4a26", "#1a2e16"])], "baja", texto=["BARRANCOS", "PROFUNDOS"], acento=1, amb="viento"),
    E("y gritar de", GOMERA + [D("persona", x=200, y=1380, s=.9, ropa="blanco", mov="saluda"), D("silbido", x1=250, y1=1100, x2=520, color="#ff5a36")], "fijo",
      texto=["GRITAR", "NO SERVÍA"], acento=1, amb="viento"),
    E("Los pastores aprendieron", GOMERA + [D("persona", x=540, y=1600, s=1.5, ropa="obrero", sombrero="fedora", mov="respira")], "push", dato="PASTORES", amb="viento", amb_vol=.5),
    E("cambiando el tono", GOMERA + [D("silbido", x1=120, y1=900, x2=960, color="#ffd21f"), D("silbido", x1=120, y1=1050, x2=960, color="#3df5ff")], "fijo",
      texto=["VOCALES Y", "CONSONANTES"], acento=0),
    N("Así pueden enviarse", 2, "KILÓMETROS", "MÁS DE", icono="📢"),
    E("Casi desaparece en", [D("interior", pared="#5a4a3c", piso="#2a1d14"), D("telefono", x=540, y=1450, s=1.4, suena=True)], "push", texto=["LLEGARON LOS", "TELÉFONOS"], acento=1, sfx="campana", sfx_dur=.6),
    E("Pero desde mil", [D("interior", pared="#3a5a4a", piso="#1d2d24", vista="dia", ventana_x=680), D("texto_svg", x=330, y=500, texto="SILBO", tam=120, color="#f4efe4"),
      D("persona", x=300, y=1450, s=.8, ropa="azul"), D("persona", x=540, y=1450, s=.8, ropa="rojo"), D("persona", x=780, y=1450, s=.8, ropa="blanco")], "pan_der", dato=["1999:", "EN LA ESCUELA"]),
    T("y la UNESCO", ["PROTEGIDO POR", "LA UNESCO"], acento=1, icono="🏆"),
    FIN("¿Te imaginas hablar", ["¿TE IMAGINAS", "HABLAR ASÍ?"], final="si_no", capas=GOMERA),
])

# ================================================================ 59 · La guerra de los mundos
CAMPO = [C("noche", horizonte=1350, astro="luna", astro_x=820, astro_y=380, astro_r=60), D("suelo", y=1350, colores=["#2a3a22", "#0d140a"])]
P[59] = dict(tema="misterio", estilo="periodico", claves=["Jersey».", "Halloween.", "ficción,", "competencia."], tomas=[
    E("«Los marcianos están", CAMPO + [D("casa", tipo="granja", x=300, y=1400, s=.7), D("tripode", x=740, y=1450, s=1.0), D("luz", x=740, y=900, r=500, color="#8dff9c", op=.5)],
      "push", texto="«¡MARCIANOS!»", amb="viento", sfx="zumbido", sfx_dur=2.5),
    E("Eso escucharon miles", [D("interior", pared="#5a4a3c", piso="#2a1d14", vista="noche", ventana_x=680), D("radio", x=360, y=1450, s=1.1),
      D("persona", x=760, y=1500, s=1.1, ropa="vestido", falda=True, pelo_largo=True)], "push", dato=["RADIO", "1938"], amb="estatica", amb_vol=.4),
    T("Era la víspera", ["VÍSPERA DE", "HALLOWEEN"], acento=1, icono="🎃"),
    E("Orson Welles adaptó", [D("interior", pared="#2a2a3a", piso="#121218", luz_x=540, luz_y=600), D("microfono", x=540, y=1450, s=1.1),
      D("persona", x=300, y=1550, s=1.2, ropa="traje", pelo="#1b1b1b")], "push", dato=["ORSON", "WELLES"], amb="ninguno"),
    E("como si fueran", [D("interior", pared="#2a2a3a", piso="#121218"), D("radio", x=540, y=1450, s=1.6)], "push_fuerte", texto=["NOTICIAS", "«EN VIVO»"], acento=1, amb="estatica", amb_vol=.5),
    T("Al principio se", ["AVISARON:", "ES FICCIÓN"], acento=1, icono="📻"),
    E("pero muchos sintonizaron", [D("interior", pared="#5a4a3c", piso="#2a1d14"), D("radio", x=700, y=1450, s=1.0), D("persona", x=330, y=1500, s=1.3, ropa="traje", sombrero="fedora")],
      "push", texto=["SINTONIZARON", "TARDE"], acento=1, amb="estatica", amb_vol=.4),
    E("Al día siguiente,", [D("interior", pared="#3a2a1e", piso="#1a120c"), D("periodico", x=540, y=1560, s=1.1, cabecera="31 OCT 1938", titular="¡PÁNICO!")], "fijo", sfx="papel", sfx_dur=.6),
    E("Hoy los historiadores", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=800), D("libro", x=540, y=1450, s=1.4)], "push", texto=["EL PÁNICO FUE", "MUCHO MENOR"], acento=1),
    E("que querían mostrar", [D("interior", pared="#2a2a3a", piso="#121218"), D("radio", x=300, y=1450, s=.9), D("periodico", x=760, y=1600, s=.6, titular="¡PELIGRO!", tam=70)],
      "fijo", texto=["LA RADIO: SU", "COMPETENCIA"], acento=1),
    FIN("¿Tú te lo", ["¿TÚ TE LO", "HABRÍAS CREÍDO?"], final="si_no", capas=CAMPO + [D("tripode", x=740, y=1450, s=.8)]),
])

# ================================================================ 62 · The Watcher
SUBURBIO_NOCHE = [C("noche", horizonte=1400), D("suelo", y=1400, colores=["#22301e", "#0a0e08"])]
P[62] = dict(tema="terror", estilo="terror", claves=["paredes?».", "Observador».", "joven»", "escribía."], tomas=[
    E("«¿Ya encontraron lo", [D("interior", pared="#1d1d24", piso="#0d0d12", luz=False), D("luz", x=540, y=900, r=500, color="#fff3c4", op=.4), D("carta", x=540, y=1500, s=1.0, texto="¿Ya encontraron...?", firma="")],
      "push", texto=["«LO QUE HAY EN", "LAS PAREDES»"], acento=1, amb="zumbido", amb_vol=.4),
    E("Eso decía una", SUBURBIO_NOCHE + [D("casa", x=540, y=1450, s=1.4), D("niebla", y=1450, op=.4)], "push", texto="UNA CARTA", amb="viento"),
    E("En dos mil", [C("dia", horizonte=1400), D("suelo", y=1400, colores=["#4a7a3a", "#22381c"]), D("casa", x=540, y=1450, s=1.3, luces=False),
      D("persona", x=250, y=1700, s=.9, ropa="azul"), D("persona", x=830, y=1700, s=.9, ropa="vestido", falda=True, pelo_largo=True)], "pull", dato=["2014", "CASA SOÑADA"], amb="insectos", amb_vol=.4),
    M("en Westfield, Nueva", [40.65, -74.35], 30, zoom_desde=2, centro_desde=[40, -90], resaltar=["United States of America"], pines=[{"lat": 40.65, "lon": -74.35, "texto": "WESTFIELD"}]),
    E("A los pocos", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=800), D("carta", x=540, y=1560, s=1.05, texto="Querida familia:", firma="El Observador")],
      "push", texto="LLEGÓ UNA CARTA", sfx="papel", sfx_dur=.6, amb="ninguno"),
    T("«El Observador».", ["«EL", "OBSERVADOR»"], acento=1, icono="👁️", entrada="flash"),
    E("Decía que su", SUBURBIO_NOCHE + [D("casa", x=540, y=1450, s=1.4), D("ojos", x=540, y=780, s=1.4, en=.5, color="#ffd21f")], "push_fuerte",
      texto=["VIGILABAN", "LA CASA"], acento=1, amb="viento"),
    E("y preguntaba por", [D("interior", pared="#3a3a5a", piso="#1d1d2e", vista="noche", ventana_x=700), D("cama", x=380, y=1500, s=1.0)], "push",
      texto=["PREGUNTABA POR", "LOS NIÑOS"], acento=1, amb="ninguno"),
    T("y por «la", ["«LA SANGRE", "JOVEN»"], acento=1, sfx="boom", sacudir=True),
    E("Llegaron más cartas.", [D("interior", pared="#2a2a2a", piso="#141414"), D("carta", x=330, y=1500, s=.7, r=-8, texto="..."), D("carta", x=750, y=1520, s=.7, r=7, texto="..."),
      D("carta", x=540, y=1560, s=.75, texto="Te vigilo")], "fijo", texto="MÁS CARTAS", sfx="papel", sfx_dur=.6),
    E("La familia nunca", [C("niebla", horizonte=1400), D("suelo", y=1400, colores=["#4a5a3a", "#22301e"]), D("casa", x=540, y=1450, s=1.3, luces=False)], "pull",
      texto=["NUNCA SE", "MUDARON"], acento=1, amb="viento"),
    E("La policía investigó", SUBURBIO_NOCHE + [D("casa", x=540, y=1450, s=1.3), D("sirenas_policia", x=540, y=1500)], "push", texto=["NUNCA SUPIERON", "QUIÉN FUE"], acento=1, amb="viento"),
    FIN("¿Tú vivirías en", ["¿VIVIRÍAS EN", "ESA CASA?"], final="si_no", capas=SUBURBIO_NOCHE + [D("casa", x=540, y=1450, s=1.3)]),
])

# ================================================================ 63 · Hinterkaifeck
GRANJA_NIEVE = [C("noche", horizonte=1350), D("suelo", y=1350, colores=["#d8e0ee", "#8a9bb8"]), D("particulas", tipo="nieve", n=60)]
P[63] = dict(tema="terror", estilo="frio", claves=["escondido…", "saliera.", "llaves", "resolvió."], tomas=[
    E("En mil novecientos", GRANJA_NIEVE + [D("casa", tipo="granja", x=420, y=1420, s=1.0)], "push", dato="1922", amb="viento"),
    M("en una granja", [48.6, 11.4], 7, zoom_desde=2, centro_desde=[50, 5], resaltar=["Germany"], pines=[{"lat": 48.6, "lon": 11.4, "texto": "BAVIERA"}]),
    E("alguien vivió escondido…", [D("interior", pared="#3a2a1e", piso="#1a120c", luz=False), D("ojos", x=540, y=900, s=1.3, en=.6, color="#ffd77a")], "push",
      texto=["ALGUIEN", "ESCONDIDO"], acento=1, amb="viento", amb_vol=.5),
    E("En Hinterkaifeck vivía", [C("dia", horizonte=1350), D("suelo", y=1350, colores=["#e6edf7", "#9aa8bf"]), D("casa", tipo="granja", x=380, y=1420, s=1.0, luces=False)],
      "pull", dato=["HINTERKAIFECK", "6 PERSONAS"], amb="viento", amb_vol=.5),
    E("el granjero vio", GRANJA_NIEVE + [D("casa", tipo="granja", x=540, y=1200, s=.6), D("huellas", x=520, y=1800, s=1.3, n=10, dx=0, dy=60)], "push",
      texto=["HUELLAS QUE", "ENTRABAN"], acento=1, amb="viento"),
    T("pero ninguna que", ["NINGUNA QUE", "SALIERA"], acento=1, icono="👣", entrada="flash"),
    E("Escucharon pasos en", [D("interior", pared="#4a3020", piso="#21140c", luz=False), D("luz", x=540, y=300, r=400, color="#ffd77a", op=.25)], "sube",
      texto=["PASOS EN", "EL ÁTICO"], acento=1, sfx="pasos", sfx_dur=2.0),
    E("y encontraron un", [D("interior", pared="#3a2a1e", piso="#1a120c"), D("mesa", x=540, y=1500, s=1.2), D("periodico", x=540, y=1260, s=.45, titular="1922", tam=80)],
      "push", texto=["UN PERIÓDICO", "QUE NADIE COMPRÓ"], acento=1),
    T("Las llaves de", ["LAS LLAVES", "DESAPARECIERON"], acento=1, icono="🔑"),
    E("Una noche, los", GRANJA_NIEVE + [D("casa", tipo="granja", x=420, y=1420, s=1.0, luces=False), D("luz", x=540, y=900, r=900, color="#ff2a2a", op=.25)],
      "push", texto="UNA NOCHE…", amb="viento", sfx="boom"),
    E("Y lo más", [C("niebla", horizonte=1350), D("suelo", y=1350, colores=["#d8e0ee", "#8a9bb8"]), D("casa", tipo="granja", x=420, y=1420, s=1.0, luces=True)],
      "push", texto=["ALGUIEN SIGUIÓ", "EN LA GRANJA"], acento=1, amb="viento"),
    E("El caso nunca", [D("interior", pared="#2a2a2a", piso="#141414"), D("periodico", x=540, y=1560, s=1.1, cabecera="1922", titular="SIN RESOLVER", tam=80)], "fijo", sfx="papel", sfx_dur=.6),
    FIN("¿Quién crees que", ["¿QUIÉN CREES", "QUE FUE?"], capas=GRANJA_NIEVE + [D("casa", tipo="granja", x=420, y=1420, s=1.0, luces=False)], comentario="Alguien que conocían 🤔"),
])

# ================================================================ 64 · Isla de las muñecas
CANAL = [C("niebla", horizonte=1300), MAR("niebla", horizonte=1300)]
P[64] = dict(tema="terror", estilo="periodico", claves=["muñecas", "voz.", "cientos:", "niña."], tomas=[
    E("En los canales", CANAL + [D("arboles", y=1320, n=5, color="#2c3f24"), D("barca", x=540, y=1380, s=1.1, techo=True, avance=120, mov="avanza")], "pan_der",
      texto="XOCHIMILCO", amb="olas", amb_vol=.6),
    M("en México, hay", [19.29, -99.1], 25, zoom_desde=2, centro_desde=[22, -100], resaltar=["Mexico"], pines=[{"lat": 19.29, "lon": -99.1, "texto": "XOCHIMILCO"}]),
    E("hay una isla", CANAL + [D("arboles", y=1350, n=6, muñecas=True, color="#2c3f24"), D("niebla", y=1300, op=.5)], "push", texto=["UNA ISLA DE", "MUÑECAS"], acento=1, amb="viento"),
    E("colgadas de los", [C("niebla", horizonte=1900), D("arboles", y=2300, n=4, muñecas=True, color="#2c3f24", semilla=8)], "push_fuerte", texto="COLGADAS", amb="viento"),
    E("Su cuidador, Julián", CANAL + [D("isla", x=540, y=1330, s=1.1, arboles=5), D("persona", x=540, y=1270, s=.8, ropa="blanco", pelo="#9a9a9a", sombrero="fedora")],
      "push", dato=["JULIÁN", "SANTANA"], amb="olas", amb_vol=.5),
    N("vivió ahí solo", 50, "AÑOS", "SOLO EN LA ISLA", icono="🏝️"),
    E("Contaba que una", [C("noche", horizonte=1300), MAR("noche", horizonte=1300), D("niebla", y=1300, op=.6)], "baja", texto=["UNA NIÑA", "SE AHOGÓ"], acento=1, amb="olas"),
    E("y que empezó", [C("noche", horizonte=1350), D("arboles", y=1360, n=6, color="#1a2616"), D("silbido", x1=540, y1=900, x2=1000, color="#ffffff")], "push",
      texto=["ESCUCHABA", "SU VOZ"], acento=1, amb="viento"),
    E("Para calmar su", CANAL + [D("muneca", x=540, y=1420, s=.9)], "push", texto=["LA PRIMERA", "MUÑECA"], acento=1, amb="olas", amb_vol=.5),
    E("Después siguió con", [C("niebla", horizonte=1350), D("arboles", y=1360, n=8, muñecas=True, color="#2c3f24", semilla=3)], "pan_der", texto="CIENTOS", amb="viento"),
    E("sin ojos, sin", [D("interior", pared="#2a2a24", piso="#121210", luz=False), D("luz", x=540, y=900, r=500, color="#e9e2cf", op=.4), D("muneca", x=540, y=1500, s=2.2)],
      "push_fuerte", texto=["SIN OJOS,", "SIN BRAZOS"], acento=0),
    T("En dos mil", ["2001"], icono="🕯️"),
    E("cerca del lugar", [C("noche", horizonte=1300), MAR("noche", horizonte=1300), D("niebla", y=1280, op=.6), D("muneca", x=540, y=1330, s=.5)], "push",
      texto=["EN EL MISMO", "LUGAR"], acento=1, amb="olas"),
    FIN("¿Te atreverías a", ["¿TE ATREVERÍAS", "A IR?"], final="si_no", capas=CANAL + [D("arboles", y=1350, n=6, muñecas=True)]),
])

# ================================================================ 65 · Robert, el muñeco
MUSEO = dict(pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700)
P[65] = dict(tema="terror", estilo="retro", claves=["permiso", "Robert.", "Robert».", "perdón"], tomas=[
    E("En un museo", [D("interior", **MUSEO), D("vitrina", x=540, y=1600, s=1.2), D("muneco", x=540, y=1380, s=.75)], "push", texto=["UN MUSEO", "DE FLORIDA"], acento=1, amb="ninguno"),
    T("debes pedirle permiso", ["PÍDELE PERMISO", "ANTES DE LA FOTO"], acento=0, icono="📷"),
    E("Se llama Robert.", [D("interior", pared="#2a2218", piso="#120e0a", luz_x=540, luz_y=800), D("muneco", x=540, y=1600, s=1.8, gira=1.4)], "push_fuerte", texto="ROBERT"),
    E("A comienzos del", [D("interior", pared="#6b5a46", piso="#3a2a1e", vista="dia", ventana_x=650), D("persona", x=360, y=1450, s=.85, ropa="azul", pelo="#3a2a1e"),
      D("muneco", x=640, y=1450, s=.55)], "push", dato=["SIGLO XX", "UN REGALO"]),
    M("a un niño", [24.55, -81.78], 25, zoom_desde=2, centro_desde=[30, -85], resaltar=["United States of America"], pines=[{"lat": 24.55, "lon": -81.78, "texto": "KEY WEST"}]),
    E("que lo llevaba", [C("dia", horizonte=1350), D("casa", tipo="colonial", x=540, y=1380, s=1.0, pared="#f2efe8"), D("suelo", y=1380, colores=["#d8c9a8", "#9a8a6a"]),
      D("persona", x=330, y=1650, s=.85, ropa="azul", mov="camina", avance=200), D("muneco", x=470, y=1650, s=.45)], "pan_der", texto="A TODAS PARTES", amb="insectos", amb_vol=.4),
    E("La familia contaba", [D("interior", pared="#2f3b55", piso="#1d2233", vista="noche", ventana_x=680), D("cama", x=400, y=1500, s=1.0), D("muneco", x=420, y=1300, s=.45)],
      "push", texto=["HABLABA", "CON ÉL"], acento=1, amb="ninguno"),
    E("y que se", [D("interior", pared="#1d1d24", piso="#0d0d12", luz=False), D("ojos", x=540, y=950, s=1.1, en=.4)], "push", texto=["RISAS EN", "SU CUARTO"], acento=1, amb="viento", amb_vol=.4),
    T("Cuando algo se", ["«FUE", "ROBERT»"], acento=1, entrada="flash", sfx="boom"),
    E("Hoy está en", [D("interior", **MUSEO), D("vitrina", x=540, y=1600, s=1.2), D("muneco", x=540, y=1380, s=.75)], "pull", dato=["FORT EAST", "MARTELLO"]),
    E("Las paredes están", [D("interior", pared="#4a3a2a", piso="#1a140f")] + [D("carta", x=x, y=y, s=.35, r=r, texto="Perdón") for x, y, r in
      [(160, 900, -8), (420, 820, 5), (700, 880, -4), (930, 840, 9), (280, 1300, 6), (560, 1260, -7), (840, 1320, 4)]], "pan_izq", texto=["CARTAS PIDIENDO", "PERDÓN"], acento=1, sfx="papel", sfx_dur=.6),
    FIN("¿Tú le pedirías", ["¿LE PEDIRÍAS", "PERMISO?"], final="si_no", capas=[D("interior", **MUSEO), D("vitrina", x=540, y=1600, s=1.2), D("muneco", x=540, y=1380, s=.75)]),
])

# ================================================================ 68 · Poltergeist de Enfield
CASA_ENFIELD = dict(pared="#5a4a5a", piso="#2a1d2a", papel=True)
P[68] = dict(tema="terror", estilo="neon", claves=["solos.", "temblaban.", "Janet,", "todas."], tomas=[
    E("En mil novecientos", [C("noche", horizonte=1400), D("suelo", y=1400, colores=["#2a2a22", "#0d0d08"]), D("casa", x=540, y=1450, s=1.3, pared="#8a4a3a", techo="#3a2a2a")],
      "push", dato="1977", amb="viento"),
    M("en una casa", [51.65, -0.08], 30, zoom_desde=3, centro_desde=[51, 3], resaltar=["United Kingdom"], pines=[{"lat": 51.65, "lon": -0.08, "texto": "ENFIELD, LONDRES"}]),
    E("los muebles empezaron", [D("interior", **CASA_ENFIELD), D("mesa", x=760, y=1500, s=.8), D("silla", x=360, y=1500, s=1.0, mov="flota", en=.5)], "push",
      texto=["SE MOVÍAN", "SOLOS"], acento=1, sfx="crujido", sfx_dur=1.5),
    E("Una madre y", [D("interior", **CASA_ENFIELD, vista="noche", ventana_x=700), D("persona", x=250, y=1500, s=1.1, ropa="vestido", falda=True, pelo_largo=True)] + [D("persona", x=x, y=1500, s=.65, ropa=r) for x, r in [(450, "azul"), (590, "rojo"), (730, "gris"), (870, "azul")]], "pan_der", texto=["UNA MADRE", "Y 4 HIJOS"], acento=1),
    E("Una noche, dos", [D("interior", pared="#2f3b55", piso="#1d2233", vista="noche", ventana_x=680), D("cama", x=300, y=1500, s=.8, tiembla=True), D("cama", x=760, y=1550, s=.8, tiembla=True)],
      "push", texto=["LAS CAMAS", "TEMBLABAN"], acento=1, sfx="crujido", sfx_dur=2.0),
    E("Luego, una silla", [D("interior", **CASA_ENFIELD), D("silla", x=300, y=1500, s=1.0, mov="desliza", avance=280, en=.3),
      D("persona", x=830, y=1500, s=1.1, ropa="azul", falda=True, sombrero="gorra")], "fijo", texto=["FRENTE A UNA", "POLICÍA"], acento=1, sfx="crujido", sfx_en=.3, sfx_dur=1.4),
    E("Investigadores pasaron meses", [D("interior", **CASA_ENFIELD), D("microfono", x=700, y=1500, s=.8), D("persona", x=330, y=1500, s=1.2, ropa="traje", pelo="#6b5a46")],
      "push", texto=["MESES", "INVESTIGANDO"], acento=0),
    E("Grabaron golpes, juguetes", [D("interior", **CASA_ENFIELD), D("muneca", x=320, y=1000, s=.6), D("bloques", x=760, y=1300, s=.4, filas=2), D("particulas", tipo="polvo", n=30)],
      "push", texto=["JUGUETES", "VOLANDO"], acento=1, sfx="patada", sfx_dur=.6, sacudir=True),
    E("a una de", [D("interior", pared="#1d2a1d", piso="#0d140d", luz=False), D("luz", x=540, y=900, r=600, color="#8dff9c", op=.35), D("persona", x=540, y=1650, s=1.7, ropa="rojo", pelo_largo=True, pelo="#6b4a2e")],
      "push", dato="JANET", amb="zumbido", amb_vol=.5),
    T("hablando con la", ["LA VOZ DE", "UN ANCIANO"], acento=1, icono="👴", sfx="gruñido", sfx_dur=1.2),
    T("Años después, Janet", ["ADMITIÓ QUE", "FINGIERON ALGO"], acento=1, icono="🤫"),
    T("pero insistió en", ["…PERO", "NO TODO"], acento=1, entrada="flash", sfx="boom"),
    FIN("¿Crees que algo", ["¿PASÓ ALGO", "EN ESA CASA?"], final="si_no", capas=[D("interior", **CASA_ENFIELD), D("silla", x=540, y=1500, s=1.0)]),
])

# ================================================================ 72 · Poveglia
LAGUNA = [C("atardecer", horizonte=1300, astro="sol", astro_x=820, astro_y=900, astro_r=60), MAR("atardecer", horizonte=1300)]
P[72] = dict(tema="terror", estilo="clasico", claves=["prohibido", "peste", "pruebas", "derrumban."], tomas=[
    M("Muy cerca de", [45.38, 12.33], 40, zoom_desde=3, centro_desde=[44, 12], resaltar=["Italy"], pines=[{"lat": 45.38, "lon": 12.33, "texto": "POVEGLIA"}]),
    E("hay una isla", LAGUNA + [D("isla", x=540, y=1330, s=1.2, campanario=True), D("niebla", y=1320, op=.35)], "push", texto=["PROHIBIDO", "IR"], acento=0, amb="olas"),
    E("Poveglia se usó", [C("dia", horizonte=1300), MAR("dia", horizonte=1300), D("isla", x=540, y=1330, s=1.0, campanario=True)], "pull", dato=["SIGLOS DE", "CUARENTENA"], amb="olas"),
    E("Los barcos que", [C("niebla", horizonte=1300), MAR("niebla", horizonte=1300), D("isla", x=800, y=1320, s=.6), D("velero", x=300, y=1330, s=.6, avance=200, mov="avanza")],
      "pan_der", texto=["ENFERMOS DE", "PESTE"], acento=1, amb="olas"),
    E("dejaban ahí a", [C("noche", horizonte=1300), MAR("noche", horizonte=1300), D("isla", x=540, y=1330, s=1.0), D("velas", x=540, y=1260, s=.5, n=3), D("niebla", y=1300, op=.5)],
      "push", texto=["LEJOS DE", "LA CIUDAD"], acento=1, amb="olas"),
    E("A comienzos del", [C("dia", horizonte=1350), MAR("dia", horizonte=1350), D("isla", x=540, y=1380, s=1.4, campanario=True)], "push", texto=["UN ASILO PARA", "ANCIANOS"], acento=1, amb="olas"),
    E("La leyenda dice", [D("interior", pared="#2a3a3a", piso="#121a1a", luz=False), D("luz", x=540, y=800, r=600, color="#8dff9c", op=.3, parpadeo=True),
      D("persona", x=540, y=1650, s=1.7, ropa="bata", pelo="#3a3a3a")], "push", texto=["¿UN MÉDICO", "CRUEL?"], acento=1, amb="zumbido", amb_vol=.5),
    T("pero no hay", ["NO HAY", "PRUEBAS"], acento=1, icono="🔍"),
    T("El asilo cerró", ["CERRÓ EN", "1968"], acento=1, icono="🔒"),
    E("Desde entonces, la", [C("noche", horizonte=1300, astro="luna", astro_x=800, astro_y=420, astro_r=60), MAR("noche", horizonte=1300), D("isla", x=540, y=1330, s=1.2, campanario=True, arboles=11),
      D("niebla", y=1300, op=.5)], "push", texto="ABANDONADA", amb="viento"),
    E("y con edificios", [C("niebla", horizonte=1700), D("isla", x=540, y=1800, s=2.2, campanario=True, arboles=4), D("particulas", tipo="polvo", n=40)], "baja",
      texto=["SE", "DERRUMBAN"], acento=1, sfx="derrumbe", sfx_dur=2.0),
    FIN("¿Te atreverías a", ["¿PASARÍAS UNA", "NOCHE AHÍ?"], final="si_no", capas=[C("noche", horizonte=1300), MAR("noche", horizonte=1300), D("isla", x=540, y=1330, s=1.0, campanario=True)]),
])

# ================================================================ 75 · Rosalía Lombardo
CATACUMBA = dict(pared="#3a3428", piso="#1a160f", luz=False)
P[75] = dict(tema="misterio", estilo="calido", claves=["dormida…", "Rosalía", "moño.", "mira."], tomas=[
    E("En unas catacumbas", [D("interior", **CATACUMBA), D("velas", x=200, y=1300, s=.8, n=3), D("velas", x=880, y=1300, s=.8, n=3), D("ataud", x=540, y=1500, s=.9)],
      "push", texto="CATACUMBAS", amb="viento", amb_vol=.4),
    M("de Italia hay", [38.12, 13.36], 30, zoom_desde=3, centro_desde=[42, 12], resaltar=["Italy"], pines=[{"lat": 38.12, "lon": 13.36, "texto": "PALERMO"}]),
    E("una niña que", [D("interior", **CATACUMBA), D("luz", x=540, y=1250, r=500, color="#ffcf7a", op=.5), D("ataud", x=540, y=1550, s=1.4)], "push_fuerte",
      texto=["PARECE", "DORMIDA"], acento=1, amb="ninguno"),
    N("desde hace más", 100, "AÑOS", "MÁS DE", icono="🕯️"),
    T("Se llama Rosalía", ["ROSALÍA", "LOMBARDO"], acento=0, icono="🌸"),
    F("Murió en mil", "6", "DICIEMBRE", "1920"),
    E("Su padre, destrozado,", [D("interior", **CATACUMBA), D("velas", x=820, y=1350, s=.9, n=3), D("persona", x=420, y=1500, s=1.3, ropa="traje", pelo="#3a2a1e")], "push",
      texto=["PIDIÓ QUE LA", "CONSERVARAN"], acento=1),
    E("El resultado fue", [D("interior", **CATACUMBA), D("luz", x=540, y=1250, r=520, color="#ffcf7a", op=.55), D("ataud", x=540, y=1600, s=1.7)], "push",
      texto=["PIEL, PESTAÑAS", "Y PELO"], acento=1),
    E("Su fórmula secreta", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=800), D("carta", x=540, y=1550, s=1.0, texto="Fórmula:", firma="A. Salafia")], "push",
      dato=["DESCUBIERTA", "EN 2009"], sfx="papel", sfx_dur=.6),
    E("Muchos visitantes juran", [D("interior", **CATACUMBA), D("ataud", x=540, y=1550, s=1.4), D("ojos", x=360, y=1310, s=.35, en=1.0, color="#3a2a1e")], "push_fuerte",
      texto=["¿ABRE LOS", "OJOS?"], acento=1),
    E("En realidad es", [D("interior", **CATACUMBA), D("luz", x=300, y=1200, r=450, color="#ffcf7a", op=.6, parpadeo=True), D("ataud", x=540, y=1550, s=1.3)], "pan_der",
      texto=["UN EFECTO", "DE LA LUZ"], acento=1),
    FIN("¿Te atreverías a", ["¿TE ATREVERÍAS", "A VERLA?"], final="si_no", capas=[D("interior", **CATACUMBA), D("velas", x=540, y=1500, s=1.2, n=5)]),
])

# ================================================================ 81 · Backrooms
P[81] = dict(tema="terror", estilo="retro", claves=["amarillos…", "fluorescentes.", "solo.", "viral."], tomas=[
    E("Si «te sales", [D("pasillo")], "push", texto=["«TE SALES DE", "LA REALIDAD»"], acento=1, amb="zumbido", amb_vol=1.0),
    E("terminas en un", [D("pasillo", parpadeo=.6)], "push_fuerte", texto=["PASILLOS", "INFINITOS"], acento=1, amb="zumbido", amb_vol=1.0),
    T("Así empezó la", ["LOS", "BACKROOMS"], acento=1, icono="🚪"),
    E("En mayo de", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("computadora", x=540, y=1500, s=1.4)], "push", dato=["MAYO", "2019"]),
    E("alguien publicó en", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("pantalla", x=540, y=1350, s=1.4, texto="ANÓNIMO", tam=90)], "push", texto="FORO ANÓNIMO"),
    E("una foto de", [D("pasillo")], "fijo", texto=["UNA SALA", "VACÍA"], acento=1, amb="zumbido", amb_vol=1.0, sfx="ping", sfx_dur=.4),
    E("con alfombra húmeda,", [D("pasillo")], "baja", texto=["ALFOMBRA", "HÚMEDA"], acento=1, amb="zumbido", amb_vol=1.0),
    E("Otro usuario respondió", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("computadora", x=540, y=1500, s=1.4)], "push", texto=["«LOS CUARTOS", "TRASEROS»"], acento=1),
    E("millones de habitaciones", [D("pasillo")], "pan_der", texto=["MILLONES DE", "HABITACIONES"], acento=0, amb="zumbido", amb_vol=1.0),
    E("con el zumbido", [D("pasillo", parpadeo=.3)], "push", texto=["ZUMBIDO", "ETERNO"], acento=1, amb="zumbido", amb_vol=1.4),
    E("y que no", [D("pasillo"), D("ojos", x=540, y=930, s=.5, en=.3, color="#111")], "push_fuerte", texto=["NO ESTÁS", "SOLO"], acento=1, sfx="boom", sacudir=True, amb="zumbido"),
    T("La idea se", ["SE VOLVIÓ", "VIRAL"], acento=1, icono="📈"),
    E("Hoy hay cientos", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("arcade", x=330, y=1500, s=.75, texto="NIVEL 0"), D("computadora", x=780, y=1500, s=.8)],
      "pan_izq", texto=["NIVELES, JUEGOS", "Y VIDEOS"], acento=0),
    FIN("¿Te dan miedo", ["¿TE DAN", "MIEDO?"], final="si_no", capas=[D("pasillo")]),
])

# ================================================================ 84 · Sirena de Fiyi
NY1842 = [C("dia", horizonte=1350), D("ciudad", era="antigua", y=1360, color="#6b4a3a", color_lejos="#8a6a5a"), D("suelo", y=1350, colores=["#9a8a6a", "#5a4a3a"])]
P[84] = dict(tema="historia", estilo="pop", claves=["sirena", "Barnum", "horrible:", "incendio."], tomas=[
    E("En mil ochocientos", NY1842 + [D("cartel", x=540, y=1500, s=.9, titulo="¡VEA!", sub="SIRENA REAL", sirena=True)], "push", dato=["NUEVA YORK", "1842"], amb="multitud", amb_vol=.5),
    E("miles de personas", NY1842 + [D("persona", x=x, y=1650, s=.8, ropa=r, sombrero=h) for x, r, h in
      [(150, "traje", "copa"), (330, "vestido", None), (510, "traje", "fedora"), (690, "gris", "copa"), (870, "vestido", None)]], "pan_der", texto=["PAGARON", "POR VERLA"], acento=1, amb="multitud"),
    T("una sirena de", ["¡UNA SIRENA", "DE VERDAD!"], acento=0, icono="🧜‍♀️"),
    E("El empresario P.", [D("interior", pared="#6b2d3f", piso="#2a0e14", papel=True), D("persona", x=540, y=1650, s=1.7, ropa="traje", sombrero="copa", mov="saluda")], "push",
      dato=["P. T.", "BARNUM"]),
    E("anunció en los", [D("interior", pared="#3a2a1e", piso="#1a120c"), D("periodico", x=540, y=1560, s=1.1, cabecera="1842", titular="¡SIRENA!")], "fijo", sfx="papel", sfx_dur=.6),
    M("cerca de las", [-17.7, 178.0], 6, zoom_desde=1.5, centro_lon=178, centro_desde=[-10, 160], resaltar=["Fiji"], pines=[{"lat": -17.7, "lon": 178.0, "texto": "ISLAS FIYI"}]),
    E("con dibujos de", [D("interior", pared="#3a2a1e", piso="#1a120c"), D("cartel", x=540, y=1600, s=1.1, titulo="¡LA SIRENA!", sub="CAPTURADA EN FIYI", sirena=True)], "push",
      texto=["UNA MUJER", "HERMOSA"], acento=1),
    E("Pero lo que", [D("interior", pared="#2a2218", piso="#120e0a", luz_x=540, luz_y=700), D("vitrina", x=540, y=1600, s=1.2), D("sirena_fiji", x=540, y=1380, s=.55)],
      "push", texto=["SECA Y", "HORRIBLE"], acento=1),
    E("con la cara", [D("interior", pared="#2a2218", piso="#120e0a", luz_x=540, luz_y=800), D("sirena_fiji", x=600, y=1550, s=1.4)], "push_fuerte",
      texto=["BOCA LLENA", "DE DIENTES"], acento=1, sfx="boom"),
    T("Era el torso", ["MONO", "+ PEZ"], acento=1, icono="🐒"),
    M("Estas «sirenas» las", [25, 120], 2.2, zoom_desde=1.2, centro_desde=[20, 140], resaltar=["Japan", "Indonesia", "Thailand", "Vietnam", "Philippines"],
      pines=[{"lat": 36, "lon": 138, "texto": "JAPÓN"}, {"lat": 10, "lon": 108, "texto": "SUDESTE ASIÁTICO"}], paso_pines=.8),
    T("Aun así, fue", ["¡ÉXITO", "ENORME!"], acento=0, icono="🎟️"),
    E("La original se", [C("noche", horizonte=1350), D("ciudad", era="antigua", y=1360, color="#2a1a10"), D("fuego", x=540, y=1370, s=1.3, ancho=700), D("particulas", tipo="brasas", n=50)],
      "push", texto=["SE PERDIÓ EN", "UN INCENDIO"], acento=1, amb="fuego"),
    FIN("¿Tú habrías pagado", ["¿HABRÍAS PAGADO", "POR VERLA?"], final="si_no", capas=[D("interior", pared="#2a2218", piso="#120e0a"), D("vitrina", x=540, y=1600, s=1.2), D("sirena_fiji", x=540, y=1380, s=.55)]),
])

# ================================================================ 85 · Cartuchos enterrados
DESIERTO_NOCHE = [C("noche", horizonte=1250), D("desierto", y=1250)]
P[85] = dict(tema="gamer", estilo="neon", claves=["secreto", "semanas", "colapsó.", "cartuchos."], tomas=[
    E("En mil novecientos", DESIERTO_NOCHE + [D("camion", x=540, y=1500, s=1.2)], "push", dato="1983", amb="camion"),
    E("camiones llenos de", [D("interior", pared="#2a2218", piso="#120e0a"), D("caja", x=540, y=1600, s=1.3)] + [D("cartucho", x=x, y=1420, s=.6, r=r, etiqueta=c) for x, r, c in
      [(330, -12, "#d97b2b"), (540, 4, "#2b59ff"), (750, 14, "#e3141b")]], "push", texto=["LLENOS DE", "VIDEOJUEGOS"], acento=1),
    E("fueron enterrados en", DESIERTO_NOCHE + [D("excavadora", x=400, y=1450, s=1.0), D("cartucho", x=760, y=1450, s=.5), D("cartucho", x=860, y=1460, s=.45, r=20)], "fijo",
      texto=["ENTERRADOS", "EN SECRETO"], acento=1, amb="viento"),
    E("Atari había hecho", [D("interior", pared="#1d2233", piso="#0d1018", luz_x=540, luz_y=800), D("cartucho", x=540, y=1500, s=1.8, etiqueta="#58c46a")], "push_fuerte",
      texto=["EL JUEGO DE", "LA PELÍCULA"], acento=1),
    T("la película más", ["LA PELÍCULA", "MÁS EXITOSA"], acento=1, icono="🎬"),
    N("Pero lo desarrollaron", 5, "SEMANAS", "PARA HACERLO", icono="⏱️"),
    T("para que estuviera", ["LISTO PARA", "NAVIDAD"], acento=1, icono="🎄"),
    E("El juego era", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("pantalla", x=540, y=1350, s=1.4, texto="???", tam=160, color="#ffd21f")], "push", texto="CONFUSO"),
    E("las tiendas devolvieron", [D("interior", pared="#3a3a3a", piso="#1d1d1d")] + [D("caja", x=x, y=y, s=.6, cae=True, cae_en=k * .12, texto="JUEGOS") for k, (x, y) in
      enumerate([(250, 1600), (540, 1600), (830, 1600), (390, 1440), (690, 1440), (540, 1280)])], "fijo", texto=["MILLONES DE", "DEVOLUCIONES"], acento=1, sfx="patada", sfx_dur=.6),
    T("Ese año, toda", ["LA INDUSTRIA", "COLAPSÓ"], acento=1, icono="📉", sacudir=True),
    E("Durante décadas, el", DESIERTO_NOCHE + [D("niebla", y=1250, op=.5)], "push", texto=["UNA LEYENDA", "URBANA"], acento=1, amb="viento"),
    M("Hasta que en", [32.9, -105.96], 12, zoom_desde=2, centro_desde=[38, -98], resaltar=["United States of America"], pines=[{"lat": 32.9, "lon": -105.96, "texto": "ALAMOGORDO"}], titulo="2014"),
    E("y encontraron los", [C("dia", horizonte=1250), D("desierto", y=1250), D("excavadora", x=330, y=1450, s=1.0)] + [D("cartucho", x=x, y=1520, s=.55, r=r, etiqueta=c) for x, r, c in
      [(640, -15, "#d97b2b"), (780, 8, "#58c46a"), (900, -4, "#2b59ff")]], "push", texto=["¡LOS", "ENCONTRARON!"], acento=1, sfx="boom", amb="viento"),
    FIN("¿Sabías esta historia?", ["¿SABÍAS ESTA", "HISTORIA?"], capas=DESIERTO_NOCHE + [D("cartucho", x=540, y=1500, s=.8)], comentario="¡Increíble! 🎮"),
])

# ================================================================ 87 · El nombre de Mario
P[87] = dict(tema="gamer", estilo="clasico", claves=["casero", "píxeles,", "Segale,", "carpintero."], tomas=[
    E("El personaje más", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1600, s=1.25, texto="ARCADE")], "push",
      texto=["NO SE LLAMABA", "MARIO"], acento=1),
    T("y su nombre", ["SE LO DEBE A UN", "CASERO ENOJADO"], acento=1, icono="😠"),
    E("En mil novecientos", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=330, y=1550, s=.9, texto="1981", color="#e3141b"),
      D("arcade", x=780, y=1550, s=.9, texto="ARCADE")], "pan_der", dato="1981"),
    T("como «Jumpman», el", ["«JUMPMAN»", "EL QUE SALTA"], acento=1, icono="🕹️"),
    E("Su bigote y", [D("interior", pared="#121226", piso="#08080f", luz=False), D("pixeles", x=540, y=1300, s=1.2, n=12)], "push", texto=["POCOS", "PÍXELES"], acento=1),
    T("era más fácil", ["BIGOTE Y GORRA:", "MÁS FÁCILES"], acento=0, icono="👨"),
    M("Ese año, Nintendo", [47.6, -122.3], 10, zoom_desde=2, centro_desde=[40, -100], resaltar=["United States of America"], pines=[{"lat": 47.6, "lon": -122.3, "texto": "SEATTLE"}]),
    E("arrendaba un depósito", [D("interior", pared="#5a5a5a", piso="#2a2a2a", luz_x=540, luz_y=500)] + [D("caja", x=x, y=y, s=.7) for x, y in [(240, 1600), (520, 1600), (800, 1600), (380, 1420), (660, 1420)]],
      "pan_izq", texto="UN DEPÓSITO"),
    E("El dueño, Mario", [D("interior", pared="#5a5a5a", piso="#2a2a2a"), D("persona", x=540, y=1650, s=1.8, ropa="traje", pelo="#2a1a10")], "push_fuerte",
      dato=["MARIO", "SEGALE"], sacudir=True),
    E("entró a reclamar", [D("interior", pared="#5a5a5a", piso="#2a2a2a"), D("carta", x=540, y=1560, s=1.0, texto="ARRIENDO", firma="ATRASADO")], "push",
      texto=["ATRASADOS CON", "EL ARRIENDO"], acento=1, sfx="papel", sfx_dur=.6),
    E("Cuando se fue,", [D("interior", pared="#4a4a5a", piso="#22222a")] + [D("persona", x=x, y=1550, s=1.0, ropa=r) for x, r in [(270, "azul"), (540, "gris"), (810, "rojo")]],
      "pull", texto=["LE PUSIERON", "SU NOMBRE"], acento=1),
    T("Al principio, además,", ["NO ERA PLOMERO:", "ERA CARPINTERO"], acento=1, icono="🔨"),
    FIN("¿Lo sabías? Comenta", ["¿LO", "SABÍAS?"], capas=[D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1700, s=1.0, texto="ARCADE")]),
])

# ================================================================ 88 · Puck-Man
P[88] = dict(tema="gamer", estilo="calido", claves=["vándalos.", "pizza", "grosería.", "Pac-Man."], tomas=[
    E("Pac-Man se llamó", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1600, s=1.25, texto="PUCK-MAN", color="#ffd21f")], "push",
      texto=["SE LLAMABA", "PUCK-MAN"], acento=1),
    T("y le cambiaron", ["POR MIEDO A", "LOS VÁNDALOS"], acento=1, icono="🖍️"),
    M("Fue creado en", [35.68, 139.69], 6, zoom_desde=1.8, centro_desde=[35, 125], resaltar=["Japan"], pines=[{"lat": 35.68, "lon": 139.69, "texto": "JAPÓN, 1980"}]),
    E("por Toru Iwatani.", [D("interior", pared="#4a5a6a", piso="#1d2530"), D("computadora", x=760, y=1500, s=.8), D("persona", x=330, y=1500, s=1.2, ropa="traje", pelo="#111")],
      "push", dato=["TORU", "IWATANI"]),
    T("El nombre venía", ["«PAKU", "PAKU»"], acento=1, icono="😋"),
    E("Iwatani contó que", [D("interior", pared="#7a3a2a", piso="#3a1a10", luz_x=540, luz_y=900), D("pizza", x=540, y=1450, s=1.4)], "push",
      texto=["UNA PIZZA SIN", "UN TROZO"], acento=1),
    E("Y quería un", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1550, s=.9, texto="PUCK-MAN", color="#ffd21f"),
      D("persona", x=250, y=1600, s=1.0, ropa="vestido", falda=True, pelo_largo=True), D("persona", x=830, y=1600, s=1.0, ropa="azul")], "pull", texto=["PARA TODOS", "SIN VIOLENCIA"], acento=1),
    M("Cuando llegó a", [38, -160], 1.7, zoom_desde=1.2, centro_lon=-170, resaltar=["Japan", "United States of America"], color_pais="#ffd21f",
      ruta=[[35.68, 139.69], [37.8, -122.4]], pines=[{"lat": 35.68, "lon": 139.69, "texto": "JAPÓN"}, {"lat": 39, "lon": -100, "texto": "EE.UU."}], paso_pines=1.0),
    E("temieron que alguien", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1600, s=1.25, texto="PUCK-MAN", color="#ffd21f"),
      D("texto_svg", x=540, y=520, texto="P → ?", tam=170, color="#ff3d3d", aparece=.6)], "push", texto=["CAMBIAR", "LA P"], acento=1, sfx="crujido", sfx_dur=.8),
    T("y formara una", ["…Y FORMARA", "UNA GROSERÍA"], acento=1, icono="🤬"),
    E("Así que lo", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1600, s=1.25, texto="PAC-MAN", color="#ffd21f")], "push_fuerte", texto="PAC-MAN", sfx="ping", sfx_dur=.4),
    T("Hoy es uno", ["DE LOS MÁS", "RECONOCIDOS"], acento=1, icono="🌎"),
    FIN("¿Lo jugaste alguna", ["¿LO JUGASTE", "ALGUNA VEZ?"], final="si_no", capas=[D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1700, s=1.0, texto="PAC-MAN", color="#ffd21f")]),
])

# ================================================================ 96 · Minecraft
P[96] = dict(tema="gamer", estilo="frio", claves=["persona.", "incompleta.", "dólares.", "cuadrados."], tomas=[
    E("El videojuego más", [C("dia", horizonte=1500), D("suelo", y=1500, colores=["#6fbf4a", "#3a6b26"]), D("bloques", x=540, y=1500, s=1.2, filas=4)], "push",
      texto=["EL MÁS", "VENDIDO"], acento=1, sfx="patada", sfx_dur=.4),
    E("empezó como el", [D("interior", pared="#2f3b55", piso="#1d2233", vista="noche", ventana_x=700), D("computadora", x=420, y=1500, s=.9), D("persona", x=780, y=1500, s=1.0, ropa="gris", sombrero="fedora")],
      "push", texto=["UNA SOLA", "PERSONA"], acento=1),
    M("En dos mil", [59.33, 18.07], 6, zoom_desde=1.6, centro_desde=[55, 10], resaltar=["Sweden"], pines=[{"lat": 59.33, "lon": 18.07, "texto": "SUECIA, 2009"}]),
    E("Markus Persson creó", [D("interior", pared="#3a4a5a", piso="#1d252d"), D("computadora", x=540, y=1500, s=1.3)], "push", dato=["MARKUS", "PERSSON"]),
    T("La primera versión", ["EN UNOS", "POCOS DÍAS"], acento=1, icono="⏱️"),
    E("La empezó a", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("pantalla", x=540, y=1350, s=1.4, texto="ALPHA", tam=130, color="#5cff7a")], "push",
      texto=["A LA VENTA…", "INCOMPLETO"], acento=1),
    E("Los jugadores la", [C("dia", horizonte=1350), D("suelo", y=1350, colores=["#6fbf4a", "#3a6b26"]), D("persona", x=200, y=1600, s=.9, ropa="azul"),
      D("persona", x=540, y=1600, s=.9, ropa="rojo"), D("persona", x=880, y=1600, s=.9, ropa="gris"), D("silbido", x1=260, y1=1250, x2=820, color="#ffd21f")], "fijo",
      texto=["DE BOCA", "EN BOCA"], acento=1),
    T("En dos mil", ["2014"], icono="🤝"),
    N("compró su empresa", 2500, "MILLONES", "DE DÓLARES", icono="💵"),
    N("Hoy Minecraft ha", 300, "MILLONES", "DE COPIAS VENDIDAS", icono="🎮"),
    E("Y todo, con", [C("dia", horizonte=1500), D("suelo", y=1500, colores=["#6fbf4a", "#3a6b26"]), D("bloques", x=540, y=1600, s=1.7, filas=5)], "push_fuerte",
      texto=["CON BLOQUES", "CUADRADOS"], acento=1, sfx="patada", sfx_dur=.4),
    FIN("¿Qué es lo", ["¿QUÉ HAS", "CONSTRUIDO?"], capas=[C("dia", horizonte=1500), D("suelo", y=1500, colores=["#6fbf4a", "#3a6b26"]), D("bloques", x=540, y=1600, s=1.0, filas=3)],
        comentario="¡Un castillo gigante! 🏰"),
])

# ================================================================ 97 · Código Konami
P[97] = dict(tema="gamer", estilo="periodico", claves=["jugando.", "secreto", "borrarlo", "treinta"], tomas=[
    E("«Arriba, arriba, abajo,", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("mando", x=540, y=1400, s=1.4, secuencia=True)], "push",
      texto=["EL CÓDIGO", "SECRETO"], acento=1),
    T("El truco más", ["EL TRUCO", "MÁS FAMOSO"], acento=1, icono="🎮"),
    T("nació porque un", ["UN PROGRAMADOR", "MALO JUGANDO"], acento=1, icono="😅"),
    E("A mediados de", [D("interior", pared="#4a5a6a", piso="#1d2530"), D("computadora", x=760, y=1500, s=.8), D("persona", x=330, y=1500, s=1.2, ropa="traje", pelo="#111")],
      "push", dato=["KAZUHISA", "HASHIMOTO"]),
    E("adaptaba el juego", [C("espacio"), D("planeta", x=860, y=1500, r=250), D("satelite", x=200, y=800, s=.7, avance=400)], "pan_der", texto=["UN JUEGO", "DE NAVES"], acento=1),
    T("Le parecía tan", ["DEMASIADO", "DIFÍCIL"], acento=1, icono="😵"),
    E("Así que creó", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("mando", x=540, y=1400, s=1.4, secuencia=True), D("particulas", tipo="chispas", n=30)],
      "push", texto=["TODAS LAS", "MEJORAS"], acento=1),
    T("Y se le", ["¡OLVIDÓ", "BORRARLO!"], acento=1, icono="🤦", entrada="flash"),
    E("Los jugadores lo", [D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("arcade", x=540, y=1550, s=.9, texto="1986"), D("persona", x=230, y=1600, s=.9, ropa="azul"),
      D("persona", x=850, y=1600, s=.9, ropa="rojo")], "pull", texto=["LO", "DESCUBRIERON"], acento=1),
    N("como Contra, donde", 30, "VIDAS", "EN OTRO JUEGO", icono="❤️"),
    E("Hoy aparece escondido", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("computadora", x=540, y=1500, s=1.3)], "push", texto=["HASTA EN", "PÁGINAS WEB"], acento=1),
    FIN("¿Lo sabías de", ["¿LO SABÍAS DE", "MEMORIA?"], final="si_no", capas=[D("interior", pared="#1d1d3a", piso="#0d0d1d", luz=False), D("mando", x=540, y=1500, s=1.0)]),
])

# ================================================================ 100 · Robo de Half-Life 2
HACKER = [D("interior", pared="#121a14", piso="#070a08", luz=False), D("luz", x=540, y=1100, r=600, color="#5cff7a", op=.25)]
P[100] = dict(tema="gamer", estilo="terror", claves=["trabajo", "Valve", "FBI", "detuvo"], tomas=[
    E("En dos mil", HACKER + [D("computadora", x=540, y=1500, s=1.3), D("persona", x=830, y=1600, s=1.1, ropa="gris", sombrero="gorra", color_sombrero="#222")], "push",
      dato=["2003", "UN ROBO"], amb="zumbido", amb_vol=.4),
    T("y luego pidió", ["…Y PIDIÓ", "TRABAJO"], acento=1, icono="💼"),
    M("Un hacker alemán", [51.2, 10.4], 5, zoom_desde=1.8, centro_desde=[50, 0], resaltar=["Germany"], pines=[{"lat": 51.2, "lon": 10.4, "texto": "ALEMANIA"}]),
    E("entró a los", HACKER + [D("computadora", x=540, y=1500, s=1.5)], "push_fuerte", texto=["ENTRÓ A LOS", "SISTEMAS"], acento=1, sfx="teclas", sfx_dur=1.5),
    E("y filtró el", HACKER + [D("pantalla", x=540, y=1350, s=1.4, alarma=True, texto="FILTRADO", tam=110)], "push", texto="EL CÓDIGO", sfx="estatica", sfx_dur=1.0),
    T("El juego terminó", ["+1 AÑO DE", "RETRASO"], acento=0, icono="⏳"),
    E("El director de", [D("interior", pared="#4a5a6a", piso="#1d2530", vista="dia", ventana_x=680), D("persona", x=380, y=1500, s=1.3, ropa="azul", pelo="#3a2a1e")], "push",
      dato=["GABE", "NEWELL"]),
    E("pidió ayuda a", [D("interior", pared="#1d2233", piso="#0d1018", luz=False), D("pantalla", x=540, y=1350, s=1.4, texto="AYUDA", tam=130, color="#ffd21f")], "push",
      texto=["PIDIÓ AYUDA", "A LOS FANS"], acento=1),
    E("Meses después, el", HACKER + [D("carta", x=540, y=1560, s=1.0, texto="Quiero trabajar", firma="El hacker")], "push", texto=["LE ESCRIBIÓ", "EL HACKER"], acento=1, sfx="ping", sfx_dur=.4),
    T("Valve le siguió", ["UNA ENTREVISTA", "TRAMPA"], acento=1, icono="🎣"),
    E("con el FBI", [D("interior", pared="#3a3a4a", piso="#1d1d26")] + [D("persona", x=x, y=1550, s=1.1, ropa="traje", sombrero="fedora") for x in (270, 540, 810)], "pull",
      texto=["EL FBI", "ESPERABA"], acento=0),
    E("Pero la policía", [C("noche", horizonte=1400), D("suelo", y=1400, colores=["#2a2a2a", "#0d0d0d"]), D("casa", x=540, y=1450, s=1.2), D("sirenas_policia", x=540, y=1450)],
      "push", texto=["DETENIDO EN", "ALEMANIA"], acento=1, amb="viento", sfx="boom"),
    FIN("¿Lo conocías? Comenta", ["¿LO", "CONOCÍAS?"], capas=HACKER + [D("computadora", x=540, y=1600, s=1.0)], comentario="¡Qué historia! 😂"),
])


def escribir():
    PLANES.mkdir(exist_ok=True)
    for n, plan in P.items():
        (PLANES / f"relato_{n:03d}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(P), "planes")


if __name__ == "__main__":
    escribir()
