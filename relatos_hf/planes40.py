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
    E("Al tercer día,", [C("noche", horizonte=1300), D("montanas", horizonte=1320), D("persona_real", x=540, y=1640, s=1.7, ropa="tunica", piel="media", pelo="#1b1b1b", barba=True, mov="saluda")],
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

# ================================================================ 1 · Pompeya
POMPEYA = [C("dia", horizonte=1250), D("volcan", x=700, y=1250, s=.8, erupcion=False), D("suelo", y=1250, colores=["#b9a888", "#6a5e4a"], tipo="adoquin")]
P[1] = dict(tema="historia", estilo="pop", claves=["día.", "volcán.", "yeso…"], tomas=[
    E("En el año", [C("atardecer", horizonte=1250), D("volcan", x=600, y=1260, s=1.0), D("templo_romano", x=360, y=1500, s=.7), D("suelo", y=1250, colores=["#8a7a66", "#3a3024"]),
      D("particulas", tipo="ceniza", n=70)], "push", dato=["AÑO 79", "D. C."], amb="fuego", sfx="boom"),
    T("en solo un", ["EN SOLO", "UN DÍA"], acento=1, icono="🌋"),
    E("Pompeya era una", POMPEYA + [D("templo_romano", x=540, y=1520, s=.9), D("persona_real", x=200, y=1720, s=1.2, ropa="tunica", piel="media", pelo="#1b1b1b"),
      D("persona_real", x=880, y=1700, s=1.15, ropa="tunica_roja", piel="media", peinado="mono", pelo="#2a1a10")], "pan_der", texto=["TABERNAS Y", "TEMPLOS"], acento=1, amb="multitud", amb_vol=.5),
    E("a los pies", POMPEYA + [D("templo_romano", x=300, y=1480, s=.6)], "pull", texto="EL MONTE VESUBIO", amb="viento", amb_vol=.5),
    M("Nadie sabía que", [40.82, 14.43], 22, zoom_desde=3, centro_desde=[42, 12], resaltar=["Italy"], pines=[{"lat": 40.75, "lon": 14.49, "texto": "POMPEYA"}, {"lat": 40.82, "lon": 14.43, "texto": "VESUBIO"}], paso_pines=.8),
    E("Un mediodía, el", [C("dia", horizonte=1250), D("volcan", x=540, y=1260, s=1.1), D("suelo", y=1250, colores=["#8a7a66", "#3a3024"])], "pull",
      texto="¡EXPLOTÓ!", sacudir=True, sfx="explosion_lejana", sfx_dur=2.5, amb="fuego"),
    E("Primero cayó una", [C("tormenta", horizonte=1250), D("templo_romano", x=540, y=1500, s=.9), D("suelo", y=1250, colores=["#6a6458", "#2a2620"]), D("particulas", tipo="ceniza", n=120)],
      "baja", texto=["PIEDRAS", "Y CENIZA"], acento=1, amb="viento"),
    E("Después, una nube", [C("rojo", horizonte=1250), D("volcan", x=700, y=1260, s=1.0), D("niebla", y=1150, op=.8, color="#8a7060"), D("templo_romano", x=300, y=1480, s=.6)],
      "pan_izq", dato=["+100", "KM/H"], amb="fuego", sfx="derrumbe", sfx_dur=2.5),
    E("Mil ochocientos años", [C("dia", horizonte=1250), D("templo_romano", x=540, y=1480, s=.9, ruinas=True), D("suelo", y=1250, colores=["#9a9488", "#5a564c"]),
      D("persona_real", x=780, y=1700, s=1.4, ropa="obrero", sombrero="fedora", bigote=True)], "push", dato=["1.800 AÑOS", "DESPUÉS"], amb="viento", amb_vol=.5),
    E("Los rellenaron con", [D("interior", pared="#6a6458", piso="#3a3630", luz_x=540, luz_y=900, cuadros=0), D("molde_yeso", x=540, y=1500, s=1.4)], "push",
      texto="MOLDES DE YESO", amb="ninguno"),
    E("y aparecieron las", [C("niebla", horizonte=1200), D("suelo", y=1200, colores=["#8a8478", "#4a463e"]), D("molde_yeso", x=300, y=1500, s=.8), D("molde_yeso", x=760, y=1600, s=1.0, espejo=True)],
      "push", texto=["SU ÚLTIMO", "SEGUNDO"], acento=1, amb="viento", amb_vol=.4),
    FIN("¿Te gustaría visitar", ["¿VISITARÍAS", "POMPEYA?"], final="si_no", capas=POMPEYA + [D("templo_romano", x=540, y=1500, s=.9, ruinas=True)]),
])

# ================================================================ 2 · Tutankamón
VALLE = [C("dia", horizonte=1250), D("montanas", horizonte=1300, colores=["#c9965a", "#a8743e", "#7a5228"]), D("desierto", y=1300)]
TUMBA = dict(pared="#8a6a3a", piso="#4a3620", luz_x=540, luz_y=800, cuadros=0, pared_estilo="liso")
P[2] = dict(tema="historia", estilo="neon", claves=["vela.", "maravillosas».", "cinco", "maldición"], tomas=[
    E("En mil novecientos", [D("interior", **TUMBA), D("puerta_tumba", x=540, y=1500, s=1.0, agujero=True), D("velas", x=260, y=1500, s=.7, n=1)], "push",
      dato="1922", amb="viento", amb_vol=.3),
    T("sellada hacía tres", ["SELLADA HACE", "3.000 AÑOS"], acento=1, icono="🔒"),
    E("Howard Carter llevaba", VALLE + [D("persona_real", x=360, y=1700, s=1.7, ropa="traje_cafe", sombrero="fedora", bigote=True), D("carpa", x=820, y=1420, s=.7)],
      "push", dato=["HOWARD", "CARTER"], amb="viento"),
    M("en el Valle", [25.74, 32.6], 25, zoom_desde=2.5, centro_desde=[27, 30], resaltar=["Egypt"], pines=[{"lat": 25.74, "lon": 32.6, "texto": "VALLE DE LOS REYES"}]),
    E("y su patrocinador,", [D("interior", pared="#4a5a4a", piso="#2a1d14", vista="dia", ventana_x=650), D("persona_real", x=380, y=1550, s=1.6, ropa="traje_gris", bigote=True, peinado="calvo", lentes=True)],
      "push", dato=["LORD", "CARNARVON"], amb="ninguno"),
    E("Entonces encontraron un", VALLE + [D("persona_real", x=540, y=1720, s=1.6, ropa="obrero", piel="morena", pelo="#111", sombrero="gorra", color_sombrero="#f2efe8")],
      "baja", texto=["UN ESCALÓN", "ESCONDIDO"], acento=1, amb="viento"),
    E("Al llegar a", [D("interior", **TUMBA), D("puerta_tumba", x=540, y=1500, s=1.1, agujero=True), D("persona_real", x=200, y=1700, s=1.5, ropa="traje_cafe", sombrero="fedora", bigote=True)],
      "push", texto="¿VES ALGO?", amb="ninguno"),
    T("Carter respondió: «Sí…", ["«SÍ… COSAS", "MARAVILLOSAS»"], acento=1, icono="✨"),
    E("Adentro había oro,", [D("interior", pared="#6a4a20", piso="#3a2410", luz_x=540, luz_y=900, cuadros=0, pared_estilo="liso"), D("tesoro", x=540, y=1550, s=1.1), D("particulas", tipo="chispas", n=40)],
      "pan_der", texto=["ORO, CARROS", "Y ESTATUAS"], acento=0, sfx="ping", sfx_dur=.4),
    N("y más de", 5000, "OBJETOS", "CASI INTACTOS", icono="🏺"),
    E("Meses después, Carnarvon", [D("interior", pared="#2a2a2a", piso="#141414", luz=False), D("velas", x=540, y=1400, s=1.3, n=4)], "push", texto=["MURIÓ POR UNA", "INFECCIÓN"], acento=1),
    T("y así nació", ["LA MALDICIÓN", "DEL FARAÓN"], acento=0, icono="𓂀" if False else "⚱️", sfx="boom"),
    FIN("¿Crees en la", ["¿CREES EN LA", "MALDICIÓN?"], final="si_no", capas=[D("interior", **TUMBA), D("tesoro", x=540, y=1600, s=.9)]),
])

# ================================================================ 6 · Apolo 13
ESPACIO = [C("espacio"), D("planeta", x=860, y=1500, r=260)]
NAVE = [D("interior", pared="#4a5260", piso="#2a2e36", luz_x=540, luz_y=700, cuadros=0, pared_estilo="liso")]
P[6] = dict(tema="ciencia", estilo="frio", claves=["problema».", "aire.", "calcetín", "vivos."], tomas=[
    E("«Houston, hemos tenido", NAVE + [D("pantalla", x=540, y=1350, s=1.4, alarma=True, texto="ALARMA", tam=110), D("luz", x=540, y=700, r=700, color="#ff2a2a", op=.35, parpadeo=True)],
      "push_fuerte", texto=["«HOUSTON, TENEMOS", "UN PROBLEMA»"], acento=1, amb="zumbido", amb_vol=.6, sacudir=True),
    E("camino a la", ESPACIO + [D("planeta", tipo="luna", x=250, y=500, r=120), D("satelite", x=500, y=1000, s=.8, avance=200)], "pan_izq", texto=["CAMINO A", "LA LUNA"], acento=1),
    F("En abril de", "13", "ABRIL", "1970"),
    E("un tanque de", ESPACIO + [D("explosion", x=540, y=950, s=1.2, en=.2), D("satelite", x=540, y=950, s=1.0, avance=40)], "fijo", texto="¡EXPLOTÓ UN TANQUE!", sacudir=True, sfx="boom"),
    N("a más de", 300000, "KILÓMETROS", "DE LA TIERRA", icono="🌍"),
    E("Tuvieron que refugiarse", NAVE + [D("persona_real", x=x, y=1550, s=1.2, ropa="camisa", pelo=c) for x, c in [(250, "#5a3a1e"), (540, "#1b1b1b"), (830, "#8a6a3a")]],
      "pan_der", texto=["MÓDULO PARA 2…", "Y ERAN 3"], acento=1, amb="zumbido", amb_vol=.5),
    E("El dióxido de", NAVE + [D("pantalla", x=540, y=1350, s=1.3, alarma=True, texto="CO₂ ▲", tam=120)], "push", texto=["EL AIRE SE", "ENVENENABA"], acento=1, amb="zumbido"),
    T("y los filtros", ["FILTRO CUADRADO,", "HUECO REDONDO"], acento=1, icono="🔲"),
    E("En la Tierra,", [D("interior", pared="#5a6a7a", piso="#2a323a", vista="dia", ventana_x=680), D("mesa", x=540, y=1500, s=1.2),
      D("persona_real", x=250, y=1520, s=1.2, ropa="camisa", lentes=True), D("persona_real", x=830, y=1520, s=1.2, ropa="camisa", pelo="#8a6a3a")], "push",
      texto=["BOLSAS, CARTÓN", "Y UN CALCETÍN"], acento=1, amb="multitud", amb_vol=.4),
    T("Funcionó. Cuatro días", ["¡VOLVIERON", "VIVOS!"], acento=1, icono="🚀"),
    FIN("¿Tú habrías mantenido", ["¿HABRÍAS MANTENIDO", "LA CALMA?"], final="si_no", capas=ESPACIO),
])

# ================================================================ 8 · Muro de Berlín
BERLIN_N = [C("noche", horizonte=1350), D("ciudad", era="moderna", y=1360, color="#1d2233"), D("suelo", y=1350, colores=["#6a6a6a", "#2a2a2a"])]
P[8] = dict(tema="historia", estilo="periodico", claves=["mal", "inmediatamente».", "abriendo"], tomas=[
    E("El Muro de", BERLIN_N + [D("muro_berlin", x=540, y=1520, s=1.0)], "push", dato="1989", amb="viento"),
    T("por culpa de", ["POR UN PAPEL", "MAL LEÍDO"], acento=1, icono="📄"),
    N("Durante veintiocho años,", 28, "AÑOS", "DIVIDIÓ LA CIUDAD", icono="🧱"),
    M("el muro había", [52.52, 13.40], 30, zoom_desde=3, centro_desde=[52, 10], resaltar=["Germany"], pines=[{"lat": 52.52, "lon": 13.40, "texto": "BERLÍN"}]),
    E("y cientos de", BERLIN_N + [D("muro_berlin", x=540, y=1520, s=1.0), D("haz_luz", x=900, y=500, ang=120, largo=1200)], "push", texto=["CIENTOS", "MURIERON"], acento=1, amb="viento"),
    E("El vocero Günter", [D("interior", pared="#3a4a5a", piso="#1d2530", luz_x=540, luz_y=700, cuadros=0), D("mesa", x=540, y=1560, s=1.3), D("microfono", x=540, y=1320, s=.5),
      D("persona_real", x=540, y=1520, s=1.4, ropa="traje_gris", lentes=True, peinado="calvo")], "push", dato=["GÜNTER", "SCHABOWSKI"], amb="multitud", amb_vol=.4),
    E("Un periodista le", [D("interior", pared="#3a4a5a", piso="#1d2530", luz=False, cuadros=0), D("persona_real", x=300, y=1600, s=1.6, ropa="traje", pelo="#5a3a1e")], "push",
      texto="¿DESDE CUÁNDO?", amb="multitud", amb_vol=.4),
    T("Él revisó sus", ["«QUE YO SEPA…", "INMEDIATAMENTE»"], acento=1, icono="📺"),
    E("Esa misma noche,", BERLIN_N + [D("muro_berlin", x=540, y=1450, s=.8)] + [D("persona_real", x=x, y=1700 + (k % 2) * 40, s=.9, ropa=r) for k, (x, r) in
      enumerate([(120, "abrigo"), (300, "traje_gris"), (480, "abrigo"), (660, "camisa"), (840, "abrigo"), (980, "traje")])], "pan_der", texto=["MILES EN LA", "FRONTERA"], acento=1, amb="multitud", amb_vol=1.2),
    E("Los guardias, sin", BERLIN_N + [D("muro_berlin", x=540, y=1520, s=1.0, abierto=True), D("persona_real", x=540, y=1640, s=1.2, ropa="uniforme", sombrero="gorra", color_sombrero="#3a4a2c")],
      "push", texto=["¡ABRIERON", "LAS PUERTAS!"], acento=1, amb="multitud", amb_vol=1.4, sfx="boom"),
    FIN("¿Sabías esta historia?", ["¿SABÍAS ESTA", "HISTORIA?"], capas=BERLIN_N + [D("muro_berlin", x=540, y=1520, s=1.0, abierto=True)], comentario="¡Por un papel! 😱"),
])

# ================================================================ 9 · Los buzos de Chernóbil
CHERNO = [C("noche", horizonte=1300), D("suelo", y=1300, colores=["#4a4a42", "#1a1a16"])]
P[9] = dict(tema="ciencia", estilo="terror", claves=["mayor", "explosión", "Baranov.", "sobrevivieron."], tomas=[
    E("Después de la", CHERNO + [D("reactor", x=540, y=1420, s=1.0), D("particulas", tipo="ceniza", n=50)], "push", dato=["CHERNÓBIL", "1986"], amb="zumbido", amb_vol=.6),
    T("había un peligro", ["UN PELIGRO", "AÚN MAYOR"], acento=1, icono="☢️"),
    E("Los bomberos habían", CHERNO + [D("reactor", x=540, y=1420, s=.9), D("persona_real", x=230, y=1650, s=1.1, ropa="uniforme", sombrero="casco_ww"),
      D("persona_real", x=850, y=1650, s=1.1, ropa="uniforme", sombrero="casco_ww")], "pan_der", texto=["MILES DE LITROS", "DE AGUA"], acento=1, amb="fuego"),
    E("Mientras tanto, el", CHERNO + [D("reactor", x=540, y=1450, s=1.2), D("luz", x=540, y=1000, r=500, color="#ff6a00", op=.6, parpadeo=True)], "push_fuerte",
      texto=["EL NÚCLEO", "SE DERRETÍA"], acento=1, amb="fuego"),
    E("Si esa lava", [D("tunel"), D("luz", x=540, y=600, r=500, color="#ff6a00", op=.5)], "push", texto=["¿OTRA", "EXPLOSIÓN?"], acento=1, amb="goteo", sfx="boom"),
    T("Había que abrir", ["ABRIR LAS", "VÁLVULAS"], acento=1, icono="🔧"),
    E("Tres trabajadores se", [D("interior", pared="#3a3e44", piso="#1a1c20", luz=False, cuadros=0, pared_estilo="liso")] + [D("persona_real", x=x, y=1600, s=1.3, ropa="obrero", sombrero="casco_ww") for x in (250, 540, 830)],
      "pull", texto=["ANANENKO, BEZPALOV", "Y BARANOV"], acento=0, amb="zumbido", amb_vol=.4),
    E("Entraron por túneles", [D("tunel"), D("haz_luz", x=420, y=1400, ang=-60, largo=900, falla=True, falla_en=1.5), D("haz_luz", x=660, y=1450, ang=-110, largo=800)],
      "push", texto=["A OSCURAS", "Y CON AGUA"], acento=1, amb="goteo"),
    T("Lo lograron. Y,", ["¡LOS TRES", "SOBREVIVIERON!"], acento=1, icono="🦺"),
    FIN("¿Tú te habrías", ["¿TE HABRÍAS", "OFRECIDO?"], final="si_no", capas=CHERNO + [D("reactor", x=540, y=1420, s=1.0)]),
])

# ================================================================ 11 · Vasili Arkhipov
P[11] = dict(tema="guerra", estilo="neon", claves=["no.", "Arkhipov", "votos", "empezó."], tomas=[
    E("En mil novecientos", [D("bajo_agua"), D("submarino", x=540, y=1000, s=.9)], "push", dato="1962", amb="burbujas", amb_vol=.6),
    T("y un solo", ["UN SOLO HOMBRE", "DIJO QUE NO"], acento=1, icono="✋"),
    M("Era la Crisis", [22.5, -79.5], 6, zoom_desde=1.5, centro_desde=[30, -80], resaltar=["Cuba", "United States of America"], color_pais="#b3261e",
      pines=[{"lat": 22.5, "lon": -79.5, "texto": "CUBA"}], titulo="CRISIS DE LOS MISILES"),
    E("El submarino B", [D("bajo_agua"), D("submarino", x=540, y=1100, s=1.1)], "pan_der", dato="B-59", amb="burbujas", amb_vol=.6),
    E("y los barcos", [D("bajo_agua"), D("submarino", x=540, y=1300, s=.8), D("explosion", x=300, y=700, s=.5, en=.4), D("explosion", x=780, y=900, s=.6, en=1.2)], "fijo",
      texto=["CARGAS DE", "PROFUNDIDAD"], acento=1, sacudir=True, sfx="explosion_lejana", sfx_dur=2.0),
    E("Adentro hacía más", [D("interior", pared="#3a3e30", piso="#1a1c14", luz=False, cuadros=0, pared_estilo="liso"), D("luz", x=540, y=800, r=700, color="#ff6a3c", op=.4)] +
      [D("persona_real", x=x, y=1600, s=1.2, ropa="uniforme") for x in (280, 540, 800)], "push", dato=["+40 °C", "SIN AIRE"], amb="zumbido", amb_vol=.5),
    T("El capitán creyó", ["¿YA EMPEZÓ", "LA GUERRA?"], acento=1, icono="☢️"),
    N("Pero para disparar", 3, "VOTOS", "PARA DISPARAR", icono="🗳️"),
    E("Vasili Arkhipov votó", [D("interior", pared="#3a3e30", piso="#1a1c14", luz=False, cuadros=0, pared_estilo="liso"), D("persona_real", x=540, y=1700, s=2.1, ropa="uniforme", sombrero="gorra", color_sombrero="#1d2233", mira="izq")],
      "push_fuerte", dato=["VASILI", "ARKHIPOV"], texto=["VOTÓ EN", "CONTRA"], acento=1),
    E("El submarino salió", [C("dia", horizonte=1100), MAR("dia", horizonte=1100), D("submarino", x=540, y=1150, s=.8, avance=40)], "sube", texto=["LA GUERRA NUNCA", "EMPEZÓ"], acento=1, amb="olas"),
    FIN("¿Conocías su nombre?", ["¿CONOCÍAS", "SU NOMBRE?"], capas=[C("dia", horizonte=1100), MAR("dia", horizonte=1100)], comentario="Un héroe sin fama 🙌"),
])

# ================================================================ 13 · Sarajevo
SARAJEVO = [C("dia", horizonte=1250), D("ciudad", era="antigua", y=1260), D("suelo", y=1250, colores=["#9a9488", "#5a564c"], tipo="adoquin")]
P[13] = dict(tema="historia", estilo="clasico", claves=["equivocada.", "rebotó.", "Princip.", "guerra."], tomas=[
    E("La Primera Guerra", SARAJEVO + [D("auto_1914", x=540, y=1700, s=1.0)], "push", texto=["LA CALLE", "EQUIVOCADA"], acento=1, amb="multitud", amb_vol=.5),
    F("El veintiocho de", "28", "JUNIO", "1914"),
    E("el archiduque Francisco", SARAJEVO + [D("auto_1914", x=540, y=1700, s=1.2)], "push", dato=["FRANCISCO", "FERNANDO"], amb="multitud", amb_vol=.5),
    M("visitaba Sarajevo. Esa", [43.85, 18.41], 18, zoom_desde=3, centro_desde=[46, 15], resaltar=["Bosnia and Herz."], pines=[{"lat": 43.85, "lon": 18.41, "texto": "SARAJEVO"}]),
    E("ya le habían", SARAJEVO + [D("auto_1914", x=540, y=1700, s=1.0), D("explosion", x=300, y=1650, s=.6, en=.4)], "fijo", texto="¡UNA BOMBA… REBOTÓ!", sacudir=True, sfx="boom", sfx_en=.4),
    E("Los conspiradores se", SARAJEVO + [D("persona_real", x=x, y=1700, s=1.1, ropa=r, mov="camina", avance=a) for x, r, a in [(200, "traje", -160), (540, "traje_gris", 120), (850, "abrigo", 160)]],
      "pull", texto="SE DISPERSARON", amb="multitud", amb_vol=.4),
    E("Uno de ellos,", SARAJEVO + [D("persona_real", x=540, y=1750, s=1.9, ropa="traje", pelo="#1b1b1b", sombrero="bombin")], "push_fuerte", dato=["GAVRILO", "PRINCIP"]),
    E("Horas después, el", SARAJEVO + [D("auto_1914", x=540, y=1700, s=1.0, mov="frena")], "pan_der", texto="DOBLÓ MAL", amb="multitud", amb_vol=.4),
    E("Al frenar para", SARAJEVO + [D("auto_1914", x=650, y=1700, s=1.0), D("persona_real", x=200, y=1720, s=1.3, ropa="traje", sombrero="bombin")], "push",
      texto=["JUSTO FRENTE", "A PRINCIP"], acento=1, sfx="crujido", sfx_dur=1.0),
    T("Princip disparó. Un", ["UN MES DESPUÉS:", "GUERRA"], acento=1, icono="💥", sfx="boom"),
    FIN("¿Crees en las", ["¿CREES EN LAS", "CASUALIDADES?"], final="si_no", capas=SARAJEVO + [D("auto_1914", x=540, y=1700, s=1.0)]),
])

# ================================================================ 17 · Karánsebes
CAMPO_NOCHE = [C("noche", horizonte=1300), D("montanas", horizonte=1320), D("suelo", y=1300, colores=["#3a4a2a", "#141a0e"], tipo="pasto")]
P[17] = dict(tema="guerra", estilo="calido", claves=["mismo.", "licor,", "turcos!».", "vacío."], tomas=[
    E("Cuenta la historia", CAMPO_NOCHE + [D("carpa", x=300, y=1450, s=.8), D("carpa", x=760, y=1420, s=.7), D("fogata" if False else "fuego", x=540, y=1600, s=.4, ancho=120)],
      "push", dato="1788", amb="fuego", amb_vol=.6),
    T("perdió una batalla…", ["PERDIÓ CONTRA", "SÍ MISMO"], acento=1, icono="🤦"),
    M("Estaban en guerra", [45.42, 22.22], 10, zoom_desde=2, centro_desde=[45, 20], resaltar=["Romania"], pines=[{"lat": 45.42, "lon": 22.22, "texto": "KARÁNSEBES"}]),
    E("unos soldados de", CAMPO_NOCHE + [D("barril", x=700, y=1650, s=1.0), D("persona_real", x=330, y=1700, s=1.4, ropa="uniforme", sombrero="bombin"),
      D("persona_real", x=860, y=1700, s=1.3, ropa="obrero", bigote=True)], "push", texto=["CAMPESINOS CON", "LICOR"], acento=1, amb="multitud", amb_vol=.5),
    E("Otros soldados llegaron", CAMPO_NOCHE + [D("persona_real", x=x, y=1700, s=1.2, ropa="uniforme", sombrero="bombin") for x in (200, 420, 640, 860)], "pan_der",
      texto="PIDIERON SU PARTE", amb="multitud", amb_vol=.6),
    E("Hubo una discusión,", CAMPO_NOCHE + [D("explosion", x=540, y=1300, s=.4, en=.3), D("persona_real", x=540, y=1720, s=1.7, ropa="uniforme", sombrero="bombin", mira="izq")],
      "push_fuerte", texto="«¡VIENEN LOS TURCOS!»", sacudir=True, sfx="boom"),
    E("En la oscuridad,", [C("noche", horizonte=1300), D("suelo", y=1300, colores=["#2a3a1e", "#0a0e06"], tipo="pasto"), D("ejercito", x=300, y=1500, s=.7, avance=200),
      D("ejercito", x=800, y=1520, s=.7, avance=-200)], "fijo", texto=["SE ATACARON", "ENTRE ELLOS"], acento=1, amb="multitud", amb_vol=1.2),
    E("Según el relato,", [C("dia", horizonte=1300), D("montanas", horizonte=1320), D("suelo", y=1300, colores=["#5a6a3a", "#2a3a1a"], tipo="pasto"), D("carpa", x=540, y=1500, s=1.0), D("barril", x=800, y=1600, s=.7)],
      "pull", texto=["EL CAMPAMENTO", "VACÍO"], acento=1, amb="viento"),
    FIN("¿Crees que pasó", ["¿CREES QUE", "PASÓ ASÍ?"], final="si_no", capas=CAMPO_NOCHE + [D("carpa", x=540, y=1450, s=.8)]),
])

# ================================================================ 18 · Shackleton
ANTARTIDA = [C("dia", horizonte=1150), D("hielo", y=1150)]
P[18] = dict(tema="historia", estilo="frio", claves=["mundo.", "Endurance,", "ninguno.", "intacto,"], tomas=[
    E("En mil novecientos", ANTARTIDA + [D("velero", x=540, y=1230, s=.8), D("particulas", tipo="nieve", n=60)], "push", dato=["ANTÁRTIDA", "1915"], amb="viento"),
    T("y veintiocho hombres", ["28 HOMBRES", "ATRAPADOS"], acento=1, icono="🧊"),
    E("Era el Endurance,", ANTARTIDA + [D("persona_real", x=540, y=1750, s=1.9, ropa="abrigo", bigote=False, pelo="#3a2a1e")], "push", dato=["ERNEST", "SHACKLETON"], amb="viento"),
    E("El barco quedó", ANTARTIDA + [D("velero", x=540, y=1260, s=1.0)], "push_fuerte", texto=["ATRAPADO EN", "EL HIELO"], acento=1, amb="viento", sfx="crujido", sfx_dur=2.0),
    E("hasta que se", [C("niebla", horizonte=1150), D("hielo", y=1150), D("velero", x=540, y=1260, s=1.0, hundir_en=.5)], "fijo", texto="SE HUNDIÓ", sfx="crujido", sfx_dur=2.5),
    E("Acamparon sobre el", ANTARTIDA + [D("carpa", x=300, y=1420, s=.6), D("carpa", x=700, y=1400, s=.5), D("bote", x=540, y=1520, s=.8, gente=0)], "pan_der", texto="ACAMPARON EN EL HIELO"),
    E("Desde ahí, Shackleton", [C("tormenta", horizonte=1100), MAR("tormenta", horizonte=1100), D("bote", x=540, y=1250, s=1.2, gente=6), D("lluvia")], "push",
      texto=["1.300 KM EN", "UN BOTE"], acento=0, amb="olas", amb_vol=1.2),
    M("cruzaron mil trescientos", [-58, -45], 3.5, zoom_desde=1.5, centro_desde=[-60, -50], resaltar=["Falkland Is."],
      ruta=[[-61.1, -55.2], [-54.2, -36.5]], pines=[{"lat": -61.1, "lon": -55.2, "texto": "ISLA ELEFANTE"}, {"lat": -54.2, "lon": -36.5, "texto": "GEORGIA DEL SUR"}], paso_pines=1.2),
    T("Volvió por los", ["NO MURIÓ", "NINGUNO"], acento=1, icono="🙌"),
    E("Y en dos", [D("bajo_agua"), D("velero", x=540, y=1500, s=.9)], "baja", dato=["2022:", "LO ENCONTRARON"], amb="burbujas", amb_vol=.6),
    FIN("¿Tú lo habrías", ["¿LO HABRÍAS", "LOGRADO?"], final="si_no", capas=ANTARTIDA),
])

# ================================================================ 19 · Tsutomu Yamaguchi
JAPON45 = [C("dia", horizonte=1250), D("pueblo_jp", y=1300), D("suelo", y=1300, colores=["#9a8a70", "#4a3e30"])]
P[19] = dict(tema="guerra", estilo="periodico", claves=["dos", "Nagasaki.", "segunda.", "nunca"], tomas=[
    E("Este hombre sobrevivió", JAPON45 + [D("persona_real", x=540, y=1760, s=1.9, ropa="traje", piel="asiatica", pelo="#111", lentes=True)], "push",
      texto=["SOBREVIVIÓ A", "LAS DOS BOMBAS"], acento=1, amb="viento", amb_vol=.4),
    F("El seis de", "6", "AGOSTO", "1945", hora="8:15"),
    M("Tsutomu Yamaguchi estaba", [34.39, 132.45], 10, zoom_desde=2, centro_desde=[35, 136], resaltar=["Japan"], pines=[{"lat": 34.39, "lon": 132.45, "texto": "HIROSHIMA"}]),
    E("Caminaba hacia la", JAPON45 + [D("persona_real", x=300, y=1720, s=1.4, ropa="traje", piel="asiatica", pelo="#111", lentes=True, mov="camina", avance=120)], "pan_der",
      dato=["TSUTOMU", "YAMAGUCHI"], amb="viento", amb_vol=.4),
    E("cuando cayó la", [C("dia", horizonte=1300), D("pueblo_jp", y=1300), D("hongo", x=700, y=1300, s=1.2), D("explosion", x=700, y=1100, s=1.6, en=.05)], "pull",
      texto="A 3 KM", sacudir=True, sfx="boom", sfx_dur=2.0),
    E("Quedó con quemaduras", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz=False, cuadros=0), D("persona_real", x=540, y=1650, s=1.8, ropa="camisa", piel="asiatica", pelo="#111")],
      "push", texto=["QUEMADURAS Y", "OÍDOS DAÑADOS"], acento=1),
    M("Al día siguiente", [32.75, 129.87], 10, zoom_desde=6, centro_desde=[34.39, 132.45], resaltar=["Japan"], ruta=[[34.39, 132.45], [32.75, 129.87]],
      pines=[{"lat": 34.39, "lon": 132.45, "texto": "HIROSHIMA"}, {"lat": 32.75, "lon": 129.87, "texto": "NAGASAKI"}], paso_pines=1.0),
    E("Le estaba contando", [D("interior", pared="#6a5a4a", piso="#3a2a1e", vista="dia", ventana_x=650), D("persona_real", x=300, y=1550, s=1.4, ropa="traje", piel="asiatica", pelo="#111"),
      D("persona_real", x=720, y=1550, s=1.4, ropa="traje_gris", piel="asiatica", pelo="#555", peinado="calvo")], "push", texto="LE CONTABA A SU JEFE"),
    E("cuando cayó la", [C("dia", horizonte=1300), D("pueblo_jp", y=1300, semilla=2), D("hongo", x=400, y=1300, s=1.2), D("explosion", x=400, y=1100, s=1.6, en=.05)], "pull",
      texto="LA SEGUNDA", sacudir=True, sfx="boom", sfx_dur=2.0),
    E("Volvió a sobrevivir.", [C("atardecer", horizonte=1300), D("pueblo_jp", y=1300, hora="atardecer"), D("suelo", y=1300, colores=["#9a8a70", "#4a3e30"]),
      D("persona_real", x=540, y=1760, s=1.9, ropa="traje", piel="asiatica", pelo="#d9d9d9", lentes=True)], "push", dato=["VIVIÓ HASTA", "LOS 93"], amb="viento", amb_vol=.4),
    T("y dedicó su", ["QUE NUNCA MÁS", "SE USEN"], acento=1, icono="🕊️"),
    FIN("¿Conocías su historia?", ["¿CONOCÍAS SU", "HISTORIA?"], capas=[C("atardecer", horizonte=1300), D("pueblo_jp", y=1300, hora="atardecer")], comentario="Increíble y triste 🕊️"),
])

# ================================================================ 20 · Juana de Arco
FRANCIA = [C("dia", horizonte=1250), D("colinas" if False else "montanas", horizonte=1300, colores=["#7a9a6a", "#5a7a4a", "#3a5a2e"]), D("suelo", y=1300, colores=["#6a8a4a", "#2e4a22"], tipo="pasto")]
P[20] = dict(tema="historia", estilo="pop", claves=["ejército.", "voces", "nueve", "hoguera"], tomas=[
    E("Una campesina de", FRANCIA + [D("persona_real", x=540, y=1760, s=1.9, ropa="vestido", peinado="corto", pelo="#5a3a1e")], "push", texto=["CAMPESINA,", "17 AÑOS"], acento=1, amb="insectos", amb_vol=.4),
    T("terminó al mando", ["AL MANDO DE", "UN EJÉRCITO"], acento=1, icono="⚔️"),
    M("Juana de Arco", [48.44, 5.67], 6, zoom_desde=2, centro_desde=[47, 2], resaltar=["France"], pines=[{"lat": 48.44, "lon": 5.67, "texto": "DOMRÉMY"}]),
    E("Decía escuchar voces", FRANCIA + [D("rayos", x=540, y=-100, op=.3), D("persona_real", x=540, y=1760, s=1.8, ropa="vestido", peinado="corto", pelo="#5a3a1e", mira="izq")],
      "push", texto=["ESCUCHABA", "VOCES"], acento=1),
    E("En mil cuatrocientos", [D("interior", pared="#5a2a2a", piso="#2a1410", luz_x=540, luz_y=700), D("trono", x=700, y=1500, s=1.0), D("persona_real", x=700, y=1480, s=1.0, ropa="tunica_roja", pelo="#3a2a1e"),
      D("armadura", x=300, y=1650, s=1.2)], "push", dato="1429", texto=["ARMADURA", "Y TROPAS"], acento=0),
    E("La ciudad de", [C("atardecer", horizonte=1300), D("castillo", x=540, y=1420, s=1.0), D("ejercito", x=540, y=1600, s=.9, color="#2a1d14"), D("suelo", y=1420, colores=["#5a5a3a", "#2a2a1a"])],
      "pan_der", dato=["ORLEANS", "SITIADA"], amb="multitud"),
    E("Con Juana al", FRANCIA + [D("castillo", x=760, y=1350, s=.6), D("armadura", x=380, y=1780, s=1.6)], "push", amb="multitud", amb_vol=.8),
    N("el sitio se", 9, "DÍAS", "PARA ROMPER EL SITIO", icono="🗡️"),
    E("Dos años después", [D("interior", pared="#3a3226", piso="#1a140f", luz=False), D("persona_real", x=540, y=1650, s=1.6, ropa="vestido", peinado="corto", pelo="#5a3a1e", mira="izq")],
      "push", texto=["CAPTURADA Y", "JUZGADA"], acento=1),
    E("Murió en la", [C("rojo", horizonte=1300), D("suelo", y=1300, colores=["#3a2a1e", "#120c08"]), D("hoguera", x=540, y=1600, s=1.1), D("particulas", tipo="brasas", n=60)], "push",
      dato=["A LOS", "19 AÑOS"], amb="fuego"),
    T("Veinticinco años más", ["DECLARADA", "INOCENTE"], acento=1, icono="⚖️"),
    E("Hoy es santa", FRANCIA + [D("armadura", x=540, y=1760, s=1.8)], "sube", texto=["SANTA Y", "HEROÍNA"], acento=1, amb="viento", amb_vol=.4),
    FIN("¿Conocías su historia?", ["¿CONOCÍAS SU", "HISTORIA?"], capas=FRANCIA + [D("armadura", x=540, y=1760, s=1.4)], comentario="¡Qué valiente! ⚔️"),
])

# ================================================================ 21 · Pirámides sin esclavos
GUIZA = [C("dia", horizonte=1250), D("piramides", x=540, y=1280, s=1.3), D("desierto", y=1280)]
OBREROS = [D("persona_real", x=x, y=1720, s=1.0, ropa="tunica", piel="morena", pelo="#111") for x in (160, 380, 700, 920)]
P[21] = dict(tema="historia", estilo="retro", claves=["esclavos.", "honores,", "Keops».", "pagados"], tomas=[
    E("Las pirámides de", GUIZA, "push", texto=["NO LAS HICIERON", "ESCLAVOS"], acento=1, amb="viento", sfx="boom"),
    E("Durante siglos se", GUIZA + [D("bloque" if False else "caja", x=540, y=1650, s=1.4, texto="")] + OBREROS[:2], "pan_der", texto=["¿ESCLAVOS A", "LATIGAZOS?"], acento=1, amb="viento"),
    M("Pero en los", [29.98, 31.13], 30, zoom_desde=3, centro_desde=[27, 31], resaltar=["Egypt"], pines=[{"lat": 29.98, "lon": 31.13, "texto": "GUIZA"}], titulo="AÑOS 90"),
    E("los arqueólogos encontraron", GUIZA + [D("persona_real", x=330, y=1700, s=1.4, ropa="camisa", sombrero="fedora", bigote=True), D("excavadora" if False else "carpa", x=800, y=1500, s=.6)],
      "push", texto=["TUMBAS DE LOS", "TRABAJADORES"], acento=1, amb="viento"),
    E("enterrados con honores,", [D("interior", pared="#a8845a", piso="#5a4430", luz_x=540, luz_y=800, cuadros=0, pared_estilo="liso"), D("sarcofago" if False else "tesoro", x=540, y=1500, s=.8)],
      "push", texto="CON HONORES", amb="ninguno"),
    E("También hallaron panaderías,", [D("interior", pared="#b98a5a", piso="#5a3a22", luz_x=540, luz_y=800, cuadros=0, pared_estilo="liso"), D("barril", x=300, y=1500, s=1.0), D("barril", x=520, y=1520, s=.9),
      D("fuego", x=800, y=1480, s=.5, ancho=160)], "pan_der", texto=["PAN Y", "CERVEZA"], acento=1, amb="fuego", amb_vol=.4),
    E("y huesos con", [D("interior", pared="#1d2233", piso="#0d1018", luz=False, cuadros=0), D("mano_rx", x=540, y=1500, s=1.0)], "push", texto=["¡TENÍAN", "MÉDICOS!"], acento=1),
    E("Y en las", GUIZA + [D("texto_svg", x=540, y=1150, texto="«AMIGOS DE KEOPS»", tam=80, color="#c0392b", borde=4)], "push_fuerte", texto=["GRAFITIS CON", "SUS NOMBRES"], acento=1),
    E("Eran obreros pagados", GUIZA + OBREROS, "pull", texto=["COMIDA, CERVEZA", "Y TECHO"], acento=0, amb="multitud", amb_vol=.5),
    N("que trabajaban por", 3, "MESES", "POR TURNO", icono="🗓️"),
    FIN("¿Tú también creías", ["¿TÚ TAMBIÉN", "LO CREÍAS?"], final="si_no", capas=GUIZA),
])

# ================================================================ 22 · Torre Eiffel
PARIS = [C("dia", horizonte=1350), D("ciudad", era="antigua", y=1380, hora="dia"), D("suelo", y=1380, colores=["#9a9488", "#5a564c"], tipo="adoquin")]
P[22] = dict(tema="historia", estilo="calido", claves=["desmontada", "monstruosa».", "radio.", "seis"], tomas=[
    E("La Torre Eiffel", PARIS + [D("torre_eiffel", x=540, y=1420, s=1.2)], "push", texto=["IBA A SER", "DESMONTADA"], acento=1, amb="viento", amb_vol=.5),
    T("en mil novecientos", ["EN 1909"], icono="🔧"),
    E("Se construyó para", PARIS + [D("torre_eiffel", x=540, y=1420, s=1.1)] + [D("persona_real", x=x, y=1720, s=1.0, ropa=r, sombrero=h) for x, r, h in [(180, "traje", "bombin"), (900, "vestido", None)]],
      "pull", dato=["EXPOSICIÓN", "1889"], amb="multitud", amb_vol=.6),
    N("con un permiso", 20, "AÑOS", "DE PERMISO", icono="📜"),
    E("Muchos artistas de", [D("interior", pared="#6b2d3f", piso="#3a1d14", vista="dia", ventana_x=650), D("carta", x=380, y=1560, s=.8, texto="Inútil y monstruosa", firma="Los artistas")], "push",
      texto=["«INÚTIL Y", "MONSTRUOSA»"], acento=1, sfx="papel", sfx_dur=.6),
    E("Gustave Eiffel buscó", PARIS + [D("persona_real", x=540, y=1760, s=1.9, ropa="traje", bigote=True, barba=True, pelo="#d9d9d9", sombrero="copa")], "push", dato=["GUSTAVE", "EIFFEL"]),
    E("La ofreció para", PARIS + [D("torre_eiffel", x=540, y=1420, s=1.1), D("silbido", x1=560, y1=420, x2=1000, color="#3df5ff")], "sube", texto=["ANTENA", "DE RADIO"], acento=1, sfx="ping", sfx_dur=.4),
    E("Las transmisiones militares", [D("interior", pared="#3a4a3a", piso="#1d251d", luz=False, cuadros=0), D("radio", x=540, y=1450, s=1.3), D("persona_real", x=850, y=1550, s=1.2, ropa="uniforme", sombrero="casco_ww")],
      "push", texto=["DEMASIADO ÚTIL", "PARA DESTRUIRLA"], acento=0, amb="estatica", amb_vol=.4),
    T("En la Primera", ["INTERCEPTÓ", "MENSAJES"], acento=1, icono="📡"),
    N("Hoy es uno", 6, "MILLONES", "DE VISITANTES AL AÑO", icono="🗼"),
    FIN("¿La has visitado", ["¿LA HAS", "VISITADO?"], final="si_no", capas=[C("atardecer", horizonte=1350), D("ciudad", era="antigua", y=1380), D("torre_eiffel", x=540, y=1420, s=1.1)]),
])

# ================================================================ 24 · Explosión de Halifax
PUERTO = [C("dia", horizonte=1200), D("ciudad", era="antigua", y=1200, hora="dia"), MAR("dia", horizonte=1250)]
P[24] = dict(tema="historia", estilo="terror", claves=["Canadá…", "explosivos", "estalló.", "kilómetros."], tomas=[
    E("En mil novecientos", PUERTO + [D("transatlantico", x=330, y=1280, s=.45, luces=False, casco="#5c6268"), D("transatlantico", x=780, y=1300, s=.45, luces=False, espejo=True)],
      "push", dato=["HALIFAX", "1917"], sacudir=True, sfx="crujido", sfx_dur=1.5, amb="olas"),
    T("y provocaron la", ["LA MAYOR EXPLOSIÓN", "ANTES DE LA BOMBA"], acento=0, icono="💥"),
    E("Uno de ellos,", PUERTO + [D("transatlantico", x=540, y=1300, s=.7, luces=False, casco="#4a3a2a")], "push", dato=["MONT", "BLANC"], amb="olas"),
    N("iba cargado con", 3000, "TONELADAS", "DE EXPLOSIVOS", icono="🧨"),
    M("Tras el choque,", [44.67, -63.6], 20, zoom_desde=3, centro_desde=[45, -70], resaltar=["Canada"], pines=[{"lat": 44.67, "lon": -63.6, "texto": "HALIFAX"}]),
    E("La tripulación huyó", PUERTO + [D("transatlantico", x=700, y=1300, s=.6, luces=False, casco="#4a3a2a"), D("fuego", x=700, y=1270, s=.6, ancho=260), D("bote", x=280, y=1340, s=.7, gente=5)],
      "pan_izq", texto=["«¡VA A", "EXPLOTAR!»"], acento=1, amb="fuego"),
    E("La gente se", PUERTO + [D("fuego", x=700, y=1280, s=.6, ancho=260)] + [D("persona_real", x=x, y=1720, s=1.0, ropa=r) for x, r in [(150, "abrigo"), (360, "obrero"), (570, "vestido")]],
      "push", texto=["SE ACERCARON", "A MIRAR"], acento=1, amb="multitud", amb_vol=.5),
    E("Veinte minutos después,", [C("rojo", horizonte=1250), D("ciudad", era="antigua", y=1250), D("hongo", x=600, y=1260, s=1.1), D("explosion", x=600, y=1100, s=2.0, en=.05)],
      "pull", texto="¡ESTALLÓ!", sacudir=True, sfx="boom", sfx_dur=2.5),
    N("Un barrio entero", 2000, "PERSONAS", "MURIERON", icono="🕯️"),
    E("Un trozo del", [C("dia", horizonte=1300), D("suelo", y=1300, colores=["#7a7a6a", "#3a3a2e"]), D("texto_svg", x=540, y=1500, texto="⚓", tam=300, color="#3a3e46", borde=0)],
      "push", dato=["ANCLA A", "+3 KM"], amb="viento"),
    FIN("¿Lo conocías? Comenta", ["¿LO", "CONOCÍAS?"], capas=PUERTO, comentario="Nunca lo había escuchado 😮"),
])

# ================================================================ 25 · Newton en cuarentena
GRANJA_EN = [C("dia", horizonte=1300), D("montanas", horizonte=1320, colores=["#8aa87a", "#6a8a5a", "#4a6a3e"]), D("suelo", y=1300, colores=["#6a9a4a", "#2e5a22"], tipo="pasto")]
P[25] = dict(tema="ciencia", estilo="clasico", claves=["ciencia", "colores", "manzana", "milagroso»."], tomas=[
    E("Durante una pandemia,", [D("interior", pared="#6b5a46", piso="#3a2a1e", vista="dia", ventana_x=650, luz_x=300, luz_y=600), D("velas", x=300, y=1400, s=.8, n=2),
      D("persona_real", x=300, y=1580, s=1.6, ropa="tunica_roja", peinado="largo", pelo="#6a5a4a")], "push", texto=["CAMBIÓ LA", "CIENCIA"], acento=1, amb="ninguno"),
    T("En mil seiscientos", ["1665:", "LA PESTE"], acento=1, icono="☠️"),
    E("y cerró la", [C("niebla", horizonte=1300), D("castillo", x=540, y=1400, s=.9), D("suelo", y=1400, colores=["#6a6a5a", "#2a2a22"], tipo="adoquin")], "pull",
      dato=["CAMBRIDGE", "CERRADA"], amb="viento"),
    E("Isaac Newton, de", GRANJA_EN + [D("casa", tipo="granja", x=540, y=1420, s=.9, luces=False), D("persona_real", x=780, y=1720, s=1.3, ropa="tunica_roja", peinado="largo", pelo="#6a5a4a")],
      "push", dato=["ISAAC NEWTON", "22 AÑOS"], amb="insectos", amb_vol=.4),
    E("En casi dos", [D("interior", pared="#6b5a46", piso="#3a2a1e", luz_x=540, luz_y=700), D("libro", x=540, y=1450, s=1.4)], "push", texto=["LAS BASES DEL", "CÁLCULO"], acento=1),
    E("descubrió con un", [D("interior", pared="#1d1d24", piso="#0d0d12", luz=False, cuadros=0), D("prisma", x=540, y=1100, s=1.2)], "fijo", texto=["LA LUZ TIENE", "TODOS LOS COLORES"], acento=1),
    T("y empezó a", ["LA", "GRAVEDAD"], acento=1, icono="🍎"),
    E("Él mismo contó", GRANJA_EN + [D("manzano", x=600, y=1500, s=1.2, cae_en=.6), D("persona_real", x=250, y=1700, s=1.3, ropa="tunica_roja", peinado="largo", pelo="#6a5a4a", mira="der")],
      "push", texto="UNA MANZANA", amb="insectos", amb_vol=.4),
    E("El árbol todavía", GRANJA_EN + [D("manzano", x=540, y=1500, s=1.3)], "pull", texto=["EL ÁRBOL", "AÚN EXISTE"], acento=1, amb="viento", amb_vol=.4),
    T("Lo llaman su", ["«AÑO", "MILAGROSO»"], acento=1, icono="✨"),
    FIN("¿Y tú qué", ["¿QUÉ HICISTE EN", "TU CUARENTENA?"], capas=GRANJA_EN + [D("manzano", x=540, y=1500, s=1.1)], comentario="Ver series 😅"),
])

# ================================================================ 26 · Mike, el pollo sin cabeza
GRANJA_US = [C("dia", horizonte=1300), D("montanas", horizonte=1320, colores=["#a88a6a", "#8a6a4a", "#6a4a32"]), D("suelo", y=1300, colores=["#a8906e", "#5a4630"], tipo="tierra")]
P[26] = dict(tema="ciencia", estilo="pop", claves=["cabeza.", "coágulo", "gotero,", "festival"], tomas=[
    E("En mil novecientos", GRANJA_US + [D("casa", tipo="granja", x=300, y=1420, s=.7), D("pollo", x=640, y=1720, s=1.6, sin_cabeza=True)], "push",
      texto=["18 MESES", "SIN CABEZA"], acento=1, amb="insectos", amb_vol=.4),
    M("Un granjero de", [39.16, -108.73], 10, zoom_desde=2, centro_desde=[39, -100], resaltar=["United States of America"], pines=[{"lat": 39.16, "lon": -108.73, "texto": "FRUITA, COLORADO"}]),
    E("le cortó la", GRANJA_US + [D("persona_real", x=330, y=1720, s=1.5, ropa="obrero", sombrero="fedora", bigote=True), D("pollo", x=760, y=1720, s=1.1)], "push",
      texto="PARA LA CENA", amb="insectos", amb_vol=.4),
    E("Pero el hacha", [D("interior", pared="#1d2233", piso="#0d1018", luz=False, cuadros=0), D("cerebro", x=540, y=1350, s=.9, zona="trasera")], "push",
      texto=["NO TOCÓ LA BASE", "DEL CEREBRO"], acento=1),
    E("Mike se levantó", GRANJA_US + [D("pollo", x=400, y=1720, s=1.6, sin_cabeza=True, mov="camina", avance=200)], "pan_der", texto="¡SIGUIÓ CAMINANDO!", amb="insectos", amb_vol=.4),
    E("Su dueño lo", [D("interior", pared="#6b5a46", piso="#3a2a1e", vista="dia", ventana_x=650), D("pollo", x=650, y=1600, s=1.3, sin_cabeza=True), D("frasco", x=300, y=1500, s=.7, contenido="liquido", color_liquido="#f4f0e0")],
      "push", texto=["CON UN", "GOTERO"], acento=1),
    E("Se volvió tan", [C("atardecer", horizonte=1350), D("suelo", y=1350, colores=["#8a6a4a", "#3a2a1e"]), D("cartel", x=330, y=1650, s=.8, titulo="¡MIKE!", sub="25 CENTAVOS"),
      D("pollo", x=780, y=1700, s=1.2, sin_cabeza=True)], "push", texto="GIRAS POR EE.UU.", amb="multitud", amb_vol=.6),
    N("y la gente", 25, "CENTAVOS", "POR VERLO", icono="🪙"),
    E("Hoy el pueblo", GRANJA_US + [D("bandera", x=200, y=1500, s=1.0, colores=["#ffd21f", "#e3141b"]), D("pollo", x=640, y=1720, s=1.4, sin_cabeza=True)] +
      [D("persona_real", x=x, y=1720, s=.9, ropa=r) for x, r in [(330, "camisa"), (930, "vestido")]], "pull", texto=["UN FESTIVAL", "CADA AÑO"], acento=1, amb="multitud"),
    FIN("¿Lo puedes creer?", ["¿LO PUEDES", "CREER?"], final="si_no", capas=GRANJA_US + [D("pollo", x=540, y=1720, s=1.3, sin_cabeza=True)]),
])

# ================================================================ 27 · Roy Sullivan
VIRGINIA = [C("tormenta", horizonte=1300), D("montanas", horizonte=1320, colores=["#3a4a3a", "#2a3a2a", "#1a261a"]), D("arboles", y=1320, n=6, color="#1e3a1a"),
            D("suelo", y=1320, colores=["#3a4a2a", "#141a0e"], tipo="pasto")]
P[27] = dict(tema="ciencia", estilo="neon", claves=["siete", "uña", "camioneta.", "Guinness"], tomas=[
    E("A este hombre", VIRGINIA + [D("persona_real", x=540, y=1760, s=1.9, ropa="uniforme", sombrero="fedora"), D("rayo", x=540, y=1000, en=.5), D("lluvia")], "push",
      texto=["7 RAYOS", "Y VIVIÓ"], acento=0, amb="lluvia", sfx="boom", sfx_en=.5),
    E("Roy Sullivan era", [C("dia", horizonte=1300), D("montanas", horizonte=1320, colores=["#5a7a5a", "#3a5a3a", "#2a4a2a"]), D("arboles", y=1320, n=6),
      D("suelo", y=1320, colores=["#5a7a3a", "#2a3a1a"], tipo="pasto"), D("persona_real", x=540, y=1760, s=1.8, ropa="uniforme", sombrero="fedora")], "push", dato=["ROY SULLIVAN", "GUARDAPARQUES"], amb="insectos", amb_vol=.4),
    M("en las montañas", [38.5, -78.4], 8, zoom_desde=2, centro_desde=[39, -95], resaltar=["United States of America"], pines=[{"lat": 38.5, "lon": -78.4, "texto": "VIRGINIA"}]),
    E("Entre mil novecientos", VIRGINIA + [D("calendario", x=540, y=1150, s=1.2, anios=["1942", "1969", "1970", "1972", "1977"]), D("rayo", x=200, y=1400, en=1.0), D("rayo", x=880, y=1300, en=2.0)],
      "fijo", texto="7 VECES", amb="lluvia"),
    E("Le quemaron el", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("persona_real", x=540, y=1760, s=2.0, ropa="uniforme", peinado="calvo")], "push_fuerte",
      texto=["PELO Y CEJAS", "QUEMADOS"], acento=1),
    E("le arrancaron una", VIRGINIA + [D("camion", x=540, y=1600, s=.9, color="#2e5a2a"), D("rayo", x=540, y=1350, en=.4)], "fijo", texto=["¡LO LANZÓ DE SU", "CAMIONETA!"], acento=1, sacudir=True, sfx="boom", sfx_en=.4),
    E("Llegó a tener", VIRGINIA + [D("persona_real", x=300, y=1720, s=1.4, ropa="uniforme", sombrero="fedora")] + [D("persona_real", x=x, y=1720, s=1.1, ropa=r, mov="camina", avance=150) for x, r in [(700, "camisa"), (880, "vestido")]],
      "pan_der", texto=["TODOS SE", "ALEJABAN"], acento=1, amb="lluvia"),
    T("Tiene el récord", ["RÉCORD", "GUINNESS"], acento=1, icono="⚡"),
    E("Dos de sus", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700), D("vitrina", x=540, y=1600, s=1.1), D("texto_svg", x=540, y=1400, texto="🎩", tam=10, color="#000")],
      "push", texto=["SOMBREROS QUEMADOS", "EN MUSEOS"], acento=0),
    FIN("¿Tú saldrías con", ["¿SALDRÍAS CON", "TORMENTA?"], final="si_no", capas=VIRGINIA + [D("rayo", x=540, y=1200, en=1.0)]),
])

# ================================================================ 29 · Togo
ALASKA = [C("niebla", horizonte=1250), D("montanas", horizonte=1260, nieve=True, colores=["#9aa8bf", "#7d8aa6", "#5c6a85"]), D("suelo", y=1260, colores=["#e6edf7", "#9aa8bf"], tipo="nieve"),
          D("particulas", tipo="nieve", n=70)]
P[29] = dict(tema="historia", estilo="frio", claves=["otro.", "difteria", "rompiendo.", "olvidado"], tomas=[
    E("El perro más", [C("dia", horizonte=1350), D("ciudad", era="moderna", y=1360, hora="dia"), D("suelo", y=1350, colores=["#6a8a4a", "#2e4a22"], tipo="pasto"), D("estatua_perro", x=540, y=1640, s=1.0)],
      "push", texto=["ESTATUA EN", "NUEVA YORK"], acento=1, amb="multitud", amb_vol=.4),
    T("pero el verdadero", ["EL VERDADERO HÉROE", "FUE OTRO"], acento=1, icono="🐺"),
    M("En enero de", [64.5, -165.4], 6, zoom_desde=1.6, centro_desde=[60, -150], resaltar=["United States of America"], pines=[{"lat": 64.5, "lon": -165.4, "texto": "NOME, ALASKA"}], titulo="ENERO 1925"),
    E("amenazaba a los", [D("interior", pared="#5a6a7a", piso="#2a323a", vista="nieve", ventana_x=650), D("cama", x=380, y=1500, s=1.0)], "push", texto=["DIFTERIA EN", "LOS NIÑOS"], acento=1, amb="viento", amb_vol=.5),
    N("El medicamento estaba", 1000, "KILÓMETROS", "MÁS DE", icono="💉"),
    E("Veinte equipos de", ALASKA + [D("trineo", x=200, y=1600, s=1.0, perros=5, avance=400)], "pan_der", texto=["20 EQUIPOS", "DE TRINEOS"], acento=0, amb="viento"),
    E("con temperaturas bajo", ALASKA + [D("trineo", x=300, y=1650, s=1.1, perros=4, avance=300)], "push", dato=["-40 °C"], amb="viento", amb_vol=1.2),
    E("Togo, un husky", ALASKA + [D("perro", raza="husky", x=540, y=1700, s=1.6)], "push_fuerte", dato=["TOGO", "12 AÑOS"], amb="viento"),
    E("cruzó un mar", [C("tormenta", horizonte=1200), D("hielo", y=1200), D("trineo", x=200, y=1500, s=.9, perros=5, avance=500), D("particulas", tipo="nieve", n=90)], "pan_der",
      texto=["UN MAR CONGELADO", "QUE SE ROMPÍA"], acento=1, sfx="crujido", sfx_dur=2.0, amb="viento"),
    E("Balto corrió el", ALASKA + [D("perro", raza="husky", x=540, y=1700, s=1.3, espejo=True)], "push", texto=["BALTO SE LLEVÓ", "LA FAMA"], acento=0, amb="viento", amb_vol=.5),
    T("Togo fue casi", ["TOGO, CASI", "OLVIDADO"], acento=1, icono="🐾"),
    FIN("¿Conocías a Togo?", ["¿CONOCÍAS", "A TOGO?"], capas=ALASKA + [D("perro", raza="husky", x=540, y=1700, s=1.2)], comentario="¡Justicia para Togo! 🐺"),
])

# ================================================================ 31 · Robinson Crusoe real
JFERNANDEZ = [C("dia", horizonte=1250), MAR("dia", horizonte=1250)]
P[31] = dict(tema="historia", estilo="calido", claves=["Chile.", "naufragó", "cabras,", "Crusoe."], tomas=[
    E("El verdadero Robinson", JFERNANDEZ + [D("isla", x=540, y=1300, s=1.3, arboles=10)], "push", texto=["EL VERDADERO", "ROBINSON CRUSOE"], acento=1, amb="olas"),
    M("vivió solo en", [-33.64, -78.85], 8, zoom_desde=2, centro_desde=[-33, -72], resaltar=["Chile"], pines=[{"lat": -33.64, "lon": -78.85, "texto": "JUAN FERNÁNDEZ"}]),
    E("En mil setecientos", JFERNANDEZ + [D("velero", x=540, y=1290, s=.8, avance=80, reflejo=True)], "push", dato=["1704", "ALEXANDER SELKIRK"], amb="olas"),
    E("Discutió con el", [C("atardecer", horizonte=1300), MAR("atardecer", horizonte=1300), D("persona_real", x=330, y=1720, s=1.5, ropa="obrero", barba=True, pelo="#5a3a1e"),
      D("persona_real", x=760, y=1720, s=1.5, ropa="traje", sombrero="bombin", bigote=True), D("baranda", y=1740)], "push", texto="¡DÉJENME EN LA ISLA!", amb="olas"),
    E("Cuando se arrepintió,", JFERNANDEZ + [D("velero", x=540, y=1290, s=.7, mov="avanza", avance=500), D("suelo", y=1500, colores=["#e6c98a", "#a88a5a"], tipo="arena"),
      D("persona_real", x=300, y=1760, s=1.4, ropa="obrero", barba=True, pelo="#5a3a1e", mira="der")], "pan_der", texto=["EL BARCO SE", "FUE SIN ÉL"], acento=1, amb="olas"),
    E("Y tenía razón:", [C("tormenta", horizonte=1250), MAR("tormenta", horizonte=1250), D("velero", x=540, y=1290, s=.8, hundir_en=.6), D("lluvia")], "fijo", texto="ESE BARCO NAUFRAGÓ", sfx="crujido", sfx_dur=2.0),
    N("Vivió cuatro años", 4, "AÑOS Y 4 MESES", "SOLO", icono="🏝️"),
    E("Cazaba cabras, se", [C("dia", horizonte=1250), D("montanas", horizonte=1300, colores=["#5a8a4a", "#3e6a32", "#2a4a22"]), D("suelo", y=1300, colores=["#6a8a4a", "#2e4a22"], tipo="pasto"),
      D("cabra", x=780, y=1650, s=1.2), D("persona_real", x=330, y=1720, s=1.5, ropa="obrero", barba=True, pelo="#5a3a1e")], "push", texto=["ROPA DE", "PIEL DE CABRA"], acento=1, amb="viento", amb_vol=.4),
    E("Su historia inspiró", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=800), D("libro", x=540, y=1450, s=1.4)], "push", texto="«ROBINSON CRUSOE»", sfx="papel", sfx_dur=.6),
    T("Hoy esa isla", ["ISLA ROBINSON", "CRUSOE"], acento=1, icono="🇨🇱"),
    FIN("¿Tú aguantarías solo", ["¿AGUANTARÍAS", "SOLO?"], final="si_no", capas=JFERNANDEZ + [D("isla", x=540, y=1300, s=1.2)]),
])

# ================================================================ 33 · Humberstone
HUMBER = [C("dia", horizonte=1250), D("desierto", y=1250)]
P[33] = dict(tema="historia", estilo="periodico", claves=["nadie", "salitre,", "artificial,", "Patrimonio"], tomas=[
    E("En medio del", HUMBER + [D("ciudad", era="colonial", y=1300, semilla=4), D("particulas", tipo="polvo", n=30)], "push", texto=["UN PUEBLO", "VACÍO"], acento=1, amb="viento"),
    T("y nadie vive", ["Y NADIE", "VIVE AHÍ"], acento=1, icono="🏚️"),
    M("Es Humberstone, una", [-20.21, -69.8], 12, zoom_desde=2, centro_desde=[-25, -70], resaltar=["Chile"], pines=[{"lat": -20.21, "lon": -69.8, "texto": "HUMBERSTONE"}], titulo="1872"),
    N("Llegó a tener", 3500, "HABITANTES", "TRABAJANDO EL SALITRE", icono="⛏️"),
    E("que trabajaban extrayendo", HUMBER + [D("persona_real", x=x, y=1700, s=1.1, ropa="obrero", sombrero="fedora", piel="media") for x in (200, 540, 880)], "pan_der",
      texto=["EL ORO BLANCO", "DE CHILE"], acento=1, amb="viento"),
    E("Pero en Alemania", [D("interior", pared="#3a4a4a", piso="#1a2424", luz_x=700, luz_y=600), D("frasco", x=400, y=1450, s=.9, contenido="liquido", color_liquido="#e9f3f6"),
      D("persona_real", x=760, y=1550, s=1.3, ropa="bata", bigote=True, lentes=True)], "push", texto=["SALITRE", "ARTIFICIAL"], acento=1),
    T("En mil novecientos", ["1960:", "SE FUERON TODOS"], acento=1, icono="🚪"),
    E("Las casas, las", HUMBER + [D("ciudad", era="colonial", y=1300, semilla=7), D("particulas", tipo="polvo", n=40)], "pan_izq", texto=["CONGELADO EN", "EL TIEMPO"], acento=1, amb="viento"),
    E("y hasta la", HUMBER + [D("transatlantico", x=540, y=1500, s=.5, luces=False, casco="#6a4a2a")], "push", texto=["PISCINA HECHA DE", "UN BARCO"], acento=1, amb="viento"),
    T("Hoy es Patrimonio", ["PATRIMONIO DE", "LA HUMANIDAD"], acento=1, icono="🏆"),
    FIN("¿Lo has visitado?", ["¿LO HAS", "VISITADO?"], final="si_no", capas=HUMBER + [D("ciudad", era="colonial", y=1300, semilla=4)]),
])

# ================================================================ 35 · Laguna del Inca
PORTILLO = [C("dia", horizonte=1100), D("montanas", horizonte=1400, nieve=True, colores=["#8a9ab8", "#6a7a98", "#4a5a78"])]
LAGUNA = PORTILLO + [MAR("dia", horizonte=1400), D("suelo", y=1650, colores=["#8a8a7a", "#4a4a3e"], tipo="tierra")]
P[35] = dict(tema="cultura", estilo="neon", claves=["imposible.", "Kora-llé,", "vacío.", "esmeralda,"], tomas=[
    E("En la cordillera", LAGUNA, "push", texto=["UN AMOR", "IMPOSIBLE"], acento=1, amb="viento"),
    M("hay una laguna", [-32.83, -70.12], 25, zoom_desde=2.5, centro_desde=[-33, -70], resaltar=["Chile"], pines=[{"lat": -32.83, "lon": -70.12, "texto": "LAGUNA DEL INCA"}]),
    E("Cuentan que el", [C("atardecer", horizonte=1300), D("montanas", horizonte=1350, nieve=True), D("suelo", y=1350, colores=["#8a7a5a", "#3a3020"]),
      D("persona_real", x=330, y=1740, s=1.6, ropa="tunica_roja", piel="morena", peinado="largo", pelo="#111"), D("persona_real", x=760, y=1740, s=1.5, ropa="tunica", piel="morena", peinado="largo", pelo="#111")],
      "push", dato=["ILLI YUPANQUI", "Y KORA-LLÉ"], amb="viento"),
    E("Decidieron casarse en", LAGUNA + [D("persona_real", x=420, y=1820, s=1.0, ropa="tunica_roja", piel="morena", peinado="largo", pelo="#111"),
      D("persona_real", x=620, y=1820, s=1.0, ropa="tunica", piel="morena", peinado="largo", pelo="#111")], "pull", texto=["BODA EN LA", "CUMBRE"], acento=1, amb="viento"),
    E("Al terminar la", [C("dia", horizonte=900), D("montanas", horizonte=1900, nieve=True, colores=["#7a8aa8", "#5a6a88", "#3a4a68"]), D("persona_real", x=540, y=1250, s=1.0, ropa="tunica", piel="morena", peinado="largo", pelo="#111")],
      "baja", texto=["UN CAMINO", "AL BORDE"], acento=1, amb="viento", amb_vol=1.2),
    T("Ella resbaló y", ["RESBALÓ", "AL VACÍO"], acento=1, entrada="flash", sfx="boom"),
    E("El príncipe, destrozado,", [C("niebla", horizonte=1300), D("montanas", horizonte=1350, nieve=True), D("suelo", y=1350, colores=["#6a6a5a", "#2a2a22"]),
      D("persona_real", x=540, y=1760, s=1.9, ropa="tunica_roja", piel="morena", peinado="largo", pelo="#111")], "push", texto=["NO QUISO", "ENTERRARLA"], acento=1, amb="viento"),
    E("La vistió con", LAGUNA + [D("particulas", tipo="chispas", n=30)], "baja", texto=["LA SEPULTÓ EN", "EL AGUA"], acento=1, amb="olas", amb_vol=.5),
    E("Desde ese día,", [C("dia", horizonte=1100), D("montanas", horizonte=1400, nieve=True, colores=["#8a9ab8", "#6a7a98", "#4a5a78"]),
      {"d": "mar_hd", "hora": "dia", "horizonte": 1400, "reflejo_x": 540}, D("luz", x=540, y=1600, r=600, color="#2fd59a", op=.45)], "push", texto=["COLOR", "ESMERALDA"], acento=1, amb="olas", amb_vol=.5),
    FIN("¿Has visitado la", ["¿HAS VISITADO", "LA LAGUNA?"], final="si_no", capas=LAGUNA),
])

# ================================================================ 37 · La Llorona
RIO_NOCHE = [C("noche", horizonte=1250), D("arboles", y=1260, n=6, color="#14200f"), MAR("noche", horizonte=1300), D("niebla", y=1300, op=.5)]
LLORONA = dict(ropa="vestido", peinado="largo", pelo="#111", piel="clara")
P[37] = dict(tema="terror", estilo="terror", claves=["hijos!».", "blanco,", "cerca.", "mexicas:"], tomas=[
    E("«¡Ay, mis hijos!».", RIO_NOCHE, "push", texto="«¡AY, MIS HIJOS!»", amb="viento", sfx="gruñido", sfx_dur=.1),
    E("Dicen que ese", RIO_NOCHE + [D("silbido", x1=300, y1=1000, x2=900, color="#cfe0ff")], "push", texto=["CERCA DE", "LOS RÍOS"], acento=1, amb="rio"),
    T("La Llorona es", ["LA", "LLORONA"], acento=1, icono="👻"),
    E("Cuenta la historia", RIO_NOCHE + [D("persona_real", x=540, y=1500, s=1.5, **{**LLORONA, "ropa": "vestido"}, mira="izq")], "push", texto=["UNA MUJER", "DESESPERADA"], acento=1, amb="rio"),
    E("perdió a sus", RIO_NOCHE + [D("muneca", x=540, y=1330, s=.4)], "baja", texto=["PERDIÓ A SUS", "HIJOS EN EL AGUA"], acento=1, amb="rio"),
    E("Desde entonces, su", [C("noche", horizonte=1250), D("arboles", y=1260, n=6, color="#14200f"), MAR("noche", horizonte=1300), D("niebla", y=1350, op=.7),
      D("persona_real", x=540, y=1520, s=1.5, ropa="camisa", peinado="largo", pelo="#111", mov="desvanece", desvanece_en=2.5), D("luz", x=540, y=1300, r=400, color="#dfe8ff", op=.35)],
      "push", texto=["VESTIDA", "DE BLANCO"], acento=1, amb="viento"),
    E("Dicen que si", RIO_NOCHE + [D("ojos", x=540, y=1150, s=1.0, en=.8, color="#dfe8ff")], "push_fuerte", texto=["SI SE ESCUCHA LEJOS…", "ESTÁ CERCA"], acento=1, amb="viento", sfx="boom", sfx_en=1.5),
    E("Algunos relacionan su", [C("noche", horizonte=1350), D("templo_azteca", x=540, y=1420, s=.9), D("suelo", y=1350, colores=["#5a4a3a", "#1a140e"])], "push", dato=["PRESAGIOS", "MEXICAS"], amb="viento"),
    E("antes de la", [C("noche", horizonte=1350), D("templo_azteca", x=540, y=1420, s=.9), D("suelo", y=1350, colores=["#5a4a3a", "#1a140e"]), D("silbido", x1=200, y1=900, x2=900, color="#dfe8ff")],
      "pan_der", texto=["UNA MUJER LLORABA", "DE NOCHE"], acento=1, amb="viento"),
    FIN("¿En tu país", ["¿EN TU PAÍS", "LA CUENTAN?"], final="si_no", capas=RIO_NOCHE),
])

# ================================================================ 38 · Penicilina
LAB_F = dict(pared="#4a5a5a", piso="#1d2626", vista="dia", ventana_x=680)
P[38] = dict(tema="ciencia", estilo="clasico", claves=["desordenado.", "moho", "penicilina,", "millones"], tomas=[
    E("Uno de los", [D("interior", **LAB_F), D("mesa", x=500, y=1500, s=1.2), D("frasco", x=330, y=1240, s=.5, contenido="liquido", color_liquido="#e8d27a"),
      D("frasco", x=500, y=1240, s=.5), D("libro", x=680, y=1250, s=.4)], "push", texto=["UN LABORATORIO", "DESORDENADO"], acento=1),
    E("En septiembre de", [D("interior", **LAB_F), D("persona_real", x=540, y=1700, s=1.9, ropa="bata", lentes=True, pelo="#8a8a8a")], "push", dato=["ALEXANDER", "FLEMING · 1928"]),
    E("dejó apiladas unas", [D("interior", pared="#4a5a5a", piso="#1d2626", luz_x=540, luz_y=900, cuadros=0), D("mesa", x=540, y=1500, s=1.2), D("placa_petri", x=540, y=1320, s=.6)],
      "push", texto=["PLACAS SIN", "LIMPIAR"], acento=1),
    E("Al volver, notó", [D("interior", pared="#1d2233", piso="#0d1018", luz=False, cuadros=0), D("placa_petri", x=540, y=1300, s=1.5)], "push_fuerte", texto=["UN MOHO", "VERDE"], acento=1),
    T("y alrededor de", ["LAS BACTERIAS", "MURIERON"], acento=1, icono="🦠"),
    E("Ese moho producía", [D("interior", **LAB_F), D("frasco", x=540, y=1450, s=1.4, contenido="liquido", color_liquido="#e8d27a", etiqueta="PENICILINA")], "push",
      texto=["EL PRIMER", "ANTIBIÓTICO"], acento=1),
    T("Pero nadie le", ["NADIE LE HIZO", "CASO POR AÑOS"], acento=1, icono="🤷"),
    E("Recién en la", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz=False, cuadros=0), D("cama", x=380, y=1500, s=1.0), D("persona_real", x=820, y=1550, s=1.3, ropa="bata", sombrero="cofia", peinado="mono")],
      "pan_der", texto=["SALVÓ A LOS", "SOLDADOS"], acento=1),
    N("Desde entonces ha", 200, "MILLONES", "DE VIDAS SALVADAS", icono="💊"),
    FIN("¿Tú eres ordenado?", ["¿TÚ ERES", "ORDENADO?"], final="si_no", capas=[D("interior", **LAB_F), D("placa_petri", x=540, y=1500, s=.9)]),
])

# ================================================================ 39 · Microondas
LAB_R = dict(pared="#3a4a5a", piso="#1d252d", luz_x=540, luz_y=700, cuadros=0)
P[39] = dict(tema="ciencia", estilo="retro", claves=["chocolate", "magnetrón,", "palomitas.", "Radarange,"], tomas=[
    E("El microondas se", [D("interior", **LAB_R), D("microondas", x=540, y=1650, s=1.0)], "push", texto=["POR UN", "CHOCOLATE"], acento=1, amb="zumbido", amb_vol=.4),
    E("En mil novecientos", [D("interior", **LAB_R), D("pantalla", x=760, y=1350, s=.9, texto="RADAR", tam=100), D("persona_real", x=330, y=1650, s=1.7, ropa="traje_gris", lentes=True, peinado="calvo")],
      "push", dato=["PERCY SPENCER", "1945"], amb="zumbido", amb_vol=.4),
    E("Un día, al", [D("interior", **LAB_R), D("computadora", x=700, y=1500, s=.8), D("persona_real", x=330, y=1650, s=1.6, ropa="traje_gris", lentes=True, peinado="calvo", mov="camina", avance=120)],
      "pan_der", texto="UN MAGNETRÓN", amb="zumbido", amb_vol=.5),
    E("notó que su", [D("interior", pared="#3a2a1e", piso="#1a120c", luz_x=540, luz_y=800, cuadros=0), D("texto_svg", x=540, y=1300, texto="🍫", tam=10, color="#000"),
      D("luz", x=540, y=1200, r=400, color="#ff9a3c", op=.4)], "push_fuerte", texto=["¡EL CHOCOLATE SE", "DERRITIÓ!"], acento=1),
    E("Curioso, acercó granos", [D("interior", **LAB_R), D("mesa", x=540, y=1550, s=1.1), D("particulas", tipo="chispas", n=40)], "push", texto=["¡PALOMITAS", "DE MAÍZ!"], acento=1, sfx="pop", sfx_dur=.6),
    E("Después probó con", [D("interior", **LAB_R), D("explosion", x=540, y=1200, s=.6, en=.6), D("persona_real", x=780, y=1650, s=1.5, ropa="camisa", lentes=True)], "fijo",
      texto=["¡EL HUEVO LE", "EXPLOTÓ!"], acento=1, sacudir=True, sfx="boom", sfx_en=.6),
    E("El primer horno", [D("interior", **LAB_R), D("microondas", x=420, y=1700, s=1.1), D("persona_real", x=820, y=1700, s=1.5, ropa="traje_gris", lentes=True, peinado="calvo")],
      "sube", dato=["RADARANGE", "1,8 M"], amb="zumbido", amb_vol=.4),
    N("y pesaba más", 300, "KILOS", "MÁS DE", icono="⚖️"),
    E("Solo lo compraban", [C("dia", horizonte=1200), MAR("dia", horizonte=1200), D("transatlantico", x=540, y=1280, s=.6, luces=False)], "pan_der", texto=["RESTAURANTES", "Y BARCOS"], acento=0, amb="olas"),
    FIN("¿Qué es lo", ["¿QUÉ CALIENTAS", "PRIMERO?"], capas=[D("interior", **LAB_R), D("microondas", x=540, y=1700, s=1.0)], comentario="El café de la mañana ☕"),
])

# ================================================================ 40 · Primera radiografía
LAB_X = dict(pared="#2a2a3a", piso="#121218", luz=False, cuadros=0)
P[40] = dict(tema="ciencia", estilo="neon", claves=["muerte».", "invisibles", "anillo.", "Nobel"], tomas=[
    E("«He visto mi", [D("interior", **LAB_X), D("mano_rx", x=540, y=1550, s=1.2)], "push", texto="«HE VISTO MI MUERTE»", amb="zumbido", amb_vol=.5),
    T("de su propia", ["LA PRIMERA", "RADIOGRAFÍA"], acento=1, icono="🦴"),
    E("En noviembre de", [D("interior", pared="#5a4a3c", piso="#2a1d14", vista="noche", ventana_x=680), D("persona_real", x=330, y=1650, s=1.7, ropa="traje", barba=True, pelo="#3a2a1e")],
      "push", dato=["WILHELM RÖNTGEN", "1895"], amb="ninguno"),
    E("experimentaba con un", [D("interior", **LAB_X), D("mesa", x=540, y=1500, s=1.2), D("frasco", x=540, y=1260, s=.6, contenido="liquido", color_liquido="#bfe6ff"),
      D("luz", x=540, y=1150, r=300, color="#3df5ff", op=.6, parpadeo=True)], "push", texto="UN TUBO DE VIDRIO", amb="zumbido", amb_vol=.5),
    E("Notó que una", [D("interior", **LAB_X), D("pantalla", x=540, y=1400, s=1.2, texto="", color="#5cff7a"), D("luz", x=540, y=1150, r=400, color="#5cff7a", op=.5)], "push_fuerte",
      texto=["¡UNA PANTALLA", "BRILLABA!"], acento=1),
    E("Eran unos rayos", [D("interior", **LAB_X), D("laser", x1=150, y1=900, x2=950, y2=1000, en=.3), D("caja", x=540, y=1500, s=.8)], "fijo", texto=["ATRAVESABAN", "TODO"], acento=1),
    T("Como no sabía", ["LOS LLAMÓ", "RAYOS X"], acento=1, icono="❌"),
    E("Le pidió a", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("persona_real", x=540, y=1700, s=1.8, ropa="vestido", peinado="mono", pelo="#6a4a2e")], "push",
      dato=["ANNA", "BERTHA"]),
    E("Aparecieron sus huesos", [D("interior", **LAB_X), D("mano_rx", x=540, y=1600, s=1.5)], "push_fuerte", texto=["HUESOS", "Y ANILLO"], acento=1, sfx="boom"),
    T("Röntgen ganó el", ["PRIMER NOBEL", "DE FÍSICA"], acento=1, icono="🏅"),
    FIN("¿Cuántas radiografías te", ["¿CUÁNTAS TE", "HAN TOMADO?"], capas=[D("interior", **LAB_X), D("mano_rx", x=540, y=1600, s=1.1)], comentario="Como 5 🦴"),
])

# ================================================================ 30 · Terremoto de Valdivia (rehecho)
VALDIVIA = [C("dia", horizonte=1300), D("montanas", horizonte=1320, nieve=True, colores=["#7a8a9a", "#5a6a7a", "#3a4a5a"]),
            D("ciudad", era="colonial", y=1340, hora="dia", semilla=11), D("suelo", y=1340, colores=["#7a7a6a", "#3a3a2e"], tipo="adoquin")]
P[30] = dict(tema="historia", estilo="terror", claves=["Chile.", "nueve", "Hawái", "volcán"], tomas=[
    E("El terremoto más", VALDIVIA, "push", texto=["EL MÁS FUERTE", "DE LA HISTORIA"], acento=1, sacudir=True, sfx="crujido", sfx_dur=2.0, amb="viento"),
    F("El veintidós de", "22", "MAYO", "1960", hora="15:11"),
    E("la tierra se", VALDIVIA + [D("persona_real", x=x, y=1740, s=1.0, ropa=r, mov="camina", avance=-120) for x, r in [(200, "abrigo"), (420, "vestido"), (700, "obrero")]],
      "fijo", texto="10 MINUTOS", sacudir=True, sfx="crujido", sfx_dur=3.0, amb="multitud", amb_vol=.5),
    {"en": "Midió nueve coma", "tipo": "sismo", "magnitud": "9,5"},
    M("El epicentro estuvo", [-39.8, -73.2], 14, zoom_desde=2, centro_desde=[-35, -71], resaltar=["Chile"], pines=[{"lat": -39.8, "lon": -73.2, "texto": "VALDIVIA"}]),
    E("Partes de la", [C("tormenta", horizonte=1250), MAR("tormenta", horizonte=1250), D("casa", tipo="madera", x=540, y=1420, s=.9, r=-8, luces=False)], "baja",
      texto=["LA COSTA SE", "HUNDIÓ"], acento=1, amb="olas"),
    E("El tsunami cruzó", [C("tormenta", horizonte=1300), MAR("tormenta", horizonte=1300), D("ola", x=200, y=1600, s=1.2, avance=400)], "push_fuerte",
      texto=["CRUZÓ EL", "PACÍFICO"], acento=1, sfx="boom", amb="olas", amb_vol=1.2),
    M("y causó muertes", [20, -170], 2.2, zoom_desde=1.2, centro_desde=[-20, -100], resaltar=["Japan", "Chile"], pines=[{"lat": 19.7, "lon": -155.1, "texto": "HAWÁI"}, {"lat": 38.3, "lon": 141.6, "texto": "JAPÓN"}]),
    E("Dos días más", [C("rojo", horizonte=1350), D("volcan", x=540, y=1400, s=1.0), D("suelo", y=1350, colores=["#4a3a2a", "#1a120c"]), D("particulas", tipo="ceniza", n=60)],
      "pull", dato=["CORDÓN", "CAULLE"], amb="fuego"),
    FIN("¿Tu familia vivió", ["¿TU FAMILIA LO", "VIVIÓ?"], capas=VALDIVIA, comentario="Mi abuela me lo contó 🙏"),
])

# ================================================================ 47 · Nabos de Halloween
IRLANDA = [C("noche", horizonte=1350), D("montanas", horizonte=1360, colores=["#2a3a2a", "#1e2e1e", "#142014"]), D("suelo", y=1500, colores=["#3a4a2a", "#141a0e"], tipo="pasto")]
P[47] = dict(tema="cultura", estilo="terror", claves=["nabos.", "Samhain,", "brasa", "calabazas:"], tomas=[
    E("Antes de las", IRLANDA + [D("muro_piedra", y=1520), D("calabaza", tipo="nabo", x=540, y=1470, s=1.3), D("niebla", y=1450, op=.5)], "push",
      texto=["SE TALLABAN", "NABOS"], acento=1, amb="viento"),
    M("La tradición viene", [53.3, -8.0], 7, zoom_desde=2, centro_desde=[50, 0], resaltar=["Ireland"], pines=[{"lat": 53.3, "lon": -8.0, "texto": "IRLANDA"}]),
    E("y de una", IRLANDA + [D("hoguera", x=540, y=1600, s=1.2)] + [D("persona_real", x=x, y=1720, s=1.0, ropa="tunica", peinado="largo", pelo=c) for x, c in [(220, "#6a3a1a"), (860, "#c0552a")]],
      "push", texto="SAMHAIN", amb="fuego", amb_vol=.6),
    E("Se creía que", IRLANDA + [D("niebla", y=1400, op=.7), D("persona_real", x=540, y=1600, s=1.3, ropa="camisa", peinado="largo", mov="desvanece", desvanece_en=2.0),
      D("luz", x=540, y=1300, r=400, color="#cfe0ff", op=.3)], "push", texto=["LOS MUERTOS SE", "ACERCABAN"], acento=1, amb="viento"),
    E("La gente tallaba", [D("interior", pared="#3a2a1e", piso="#1a120c", luz=False, cuadros=0), D("mesa", x=540, y=1650, s=1.2), D("calabaza", tipo="nabo", x=420, y=1440, s=.8),
      D("calabaza", tipo="nabo", x=680, y=1450, s=.6)], "push", texto=["CARAS", "TERRORÍFICAS"], acento=1),
    E("y les ponía", [D("interior", pared="#1a1410", piso="#0a0806", luz=False, cuadros=0), D("calabaza", tipo="nabo", x=540, y=1500, s=1.8)], "push_fuerte",
      texto=["UNA BRASA", "ADENTRO"], acento=1, amb="fuego", amb_vol=.4),
    E("Según la leyenda,", IRLANDA + [D("persona_real", x=540, y=1720, s=1.5, ropa="obrero", sombrero="fedora", barba=True, mov="camina", avance=200), D("calabaza", tipo="nabo", x=620, y=1500, s=.4)],
      "pan_der", texto=["JACK, CONDENADO", "A VAGAR"], acento=0, amb="viento"),
    E("En el siglo", [C("dia", horizonte=1250), MAR("dia", horizonte=1250), D("velero", x=540, y=1290, s=.9, avance=200, reflejo=True)], "pan_der",
      texto=["EMIGRARON A", "EE.UU."], acento=1, amb="olas"),
    E("y encontraron calabazas:", [C("atardecer", horizonte=1350), D("suelo", y=1350, colores=["#6a5a3a", "#2a2010"], tipo="tierra"),
      D("calabaza", x=320, y=1650, s=1.0), D("calabaza", x=760, y=1700, s=1.3), D("calabaza", tipo="nabo", x=540, y=1600, s=.5)], "push", texto=["MÁS GRANDES", "Y FÁCILES"], acento=1),
    FIN("¿Tú celebras Halloween?", ["¿CELEBRAS", "HALLOWEEN?"], final="si_no", capas=IRLANDA + [D("calabaza", x=540, y=1600, s=1.2)]),
])

# ================================================================ 48 · Papá Noel y Coca-Cola
SALA_NAV = dict(pared="#6b2d2f", piso="#3a1d14", luz_x=540, luz_y=700, pared_estilo="papel")
SANTA = dict(ropa="santa", barba=True, bigote=True, pelo="#f2f2f2", peinado="corto")
P[48] = dict(tema="cultura", estilo="calido", claves=["mito.", "renos.", "rojo", "popularizar"], tomas=[
    E("Dicen que Coca-Cola", [D("interior", **SALA_NAV), D("chimenea", x=330, y=1650, s=.8), D("persona_real", x=780, y=1760, s=1.7, **SANTA)], "push",
      texto="ES UN MITO", amb="fuego", amb_vol=.4),
    E("El personaje viene", [D("catedral", x=540, y=1450, s=.9), C("dia", horizonte=1450), D("suelo", y=1450, colores=["#a89a7a", "#5a4a3a"], tipo="adoquin"),
      D("persona_real", x=540, y=1760, s=1.6, ropa="tunica_roja", barba=True, pelo="#d9d9d9", sombrero="copa")], "push", dato=["SAN NICOLÁS", "SIGLO IV"]),
    E("famoso por hacer", [C("noche", horizonte=1350), D("ciudad", era="antigua", y=1380, hora="noche"), D("suelo", y=1380, colores=["#e6edf7", "#9aa8bf"], tipo="nieve"),
      D("caja", x=540, y=1650, s=.9), D("particulas", tipo="nieve", n=60)], "push", texto=["REGALOS EN", "SECRETO"], acento=1, amb="viento", amb_vol=.4),
    E("En mil ochocientos", [C("noche", horizonte=1500), D("ciudad", era="antigua", y=1550, hora="noche"), D("trineo", x=200, y=900, s=.8, perros=6, avance=500)], "pan_der",
      dato=["1823", "TRINEO Y RENOS"], amb="viento", amb_vol=.4),
    E("Después, el dibujante", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("caballete", x=640, y=1750, s=1.1, cuadro="vacio"),
      D("persona_real", x=300, y=1720, s=1.6, ropa="traje", barba=True, bigote=True, pelo="#3a2a1e")], "push", dato=["THOMAS NAST", "DIBUJANTE"]),
    E("como un hombre", [D("interior", **SALA_NAV), D("persona_real", x=540, y=1800, s=2.2, **SANTA)], "push_fuerte", texto=["GORDO Y", "DE BARBA BLANCA"], acento=1),
    E("Y antes de", [D("interior", pared="#3a2a1e", piso="#1a120c", luz_x=540, luz_y=700), D("cartel", x=540, y=1600, s=1.0, titulo="FELIZ NAVIDAD", sub="1915")],
      "push", texto=["YA ERA ROJO", "ANTES DE 1930"], acento=0, sfx="papel", sfx_dur=.6),
    T("Lo que sí", ["COCA-COLA LO", "POPULARIZÓ"], acento=1, icono="🥤"),
    E("con los dibujos", [D("interior", **SALA_NAV), D("chimenea", x=330, y=1650, s=.8), D("caja", x=780, y=1700, s=.6), D("persona_real", x=760, y=1760, s=1.5, **SANTA)],
      "pull", dato=["HADDON", "SUNDBLOM · 1931"], amb="fuego", amb_vol=.4),
    FIN("¿Tú también creías", ["¿TÚ CREÍAS", "EL MITO?"], final="si_no", capas=[D("interior", **SALA_NAV), D("chimenea", x=540, y=1650, s=.9)]),
])

# ================================================================ 49 · Cumpleaños feliz
CINE = [D("interior", pared="#2a1a1e", piso="#110a0c", luz=False, cuadros=0), D("pantalla", x=540, y=1150, s=1.6, texto="")]
AULA = dict(pared="#6a7a6a", piso="#3a2a1e", vista="dia", ventana_x=700, cuadros=0)
P[49] = dict(tema="cultura", estilo="pop", claves=["pagar.", "alumnos", "Warner.", "todos."], tomas=[
    E("Durante décadas, para", CINE + [D("torta", x=540, y=1500, s=1.0), D("butacas")], "push", texto=["HABÍA QUE", "PAGAR"], acento=1, amb="multitud", amb_vol=.3),
    T("La melodía nació", ["1893"], icono="🎵"),
    E("Dos hermanas profesoras", [D("interior", **AULA), D("persona_real", x=330, y=1720, s=1.6, ropa="vestido", peinado="mono", pelo="#4a3a2a"),
      D("persona_real", x=750, y=1720, s=1.6, ropa="vestido", peinado="mono", pelo="#6a4a2a")], "push", dato=["MILDRED Y", "PATTY HILL"]),
    E("la crearon para", [D("interior", **AULA), D("notas", n=6, color="#3a2a1e")] + [D("persona_real", x=x, y=1800, s=.9, ropa="camisa", peinado="corto") for x in (220, 420, 640, 860)],
      "pull", texto=["«BUENOS DÍAS", "A TODOS»"], acento=1),
    E("Con los años,", [D("interior", pared="#e6c2a4", piso="#6a4a2a", luz_x=540, luz_y=700, pared_estilo="papel"), D("mesa", x=540, y=1650, s=1.3), D("torta", x=540, y=1480, s=.9), D("notas", n=7, color="#ffffff")],
      "push", texto=["CAMBIÓ LA", "LETRA"], acento=1),
    E("Una editorial registró", [D("interior", pared="#3a3a4a", piso="#1a1a24", luz_x=540, luz_y=700), D("carta", x=540, y=1500, s=1.0, texto="Derechos de autor", firma="Warner"),
      D("texto_svg", x=760, y=1400, texto="©", tam=220, color="#c0392b", borde=6)], "push_fuerte", texto=["LOS DERECHOS:", "WARNER"], acento=1, sfx="papel", sfx_dur=.6),
    N("Cobraba alrededor de", 2, "MILLONES", "DE DÓLARES AL AÑO", icono="💵"),
    E("Por eso en", CINE + [D("notas", n=5, color="#ffd36a"), D("butacas")], "pull", texto=["CANTABAN", "OTRA CANCIÓN"], acento=1, amb="multitud", amb_vol=.3),
    E("En dos mil", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("mesa", x=540, y=1650, s=1.3),
      D("persona_real", x=540, y=1500, s=1.4, ropa="traje", peinado="calvo", lentes=True)], "push", dato=["2016", "ES DE TODOS"], sfx="boom", sfx_dur=.5),
    FIN("¿Cuál es tu", ["¿CUÁL ES TU", "CANCIÓN?"], capas=[D("interior", pared="#e6c2a4", piso="#6a4a2a", luz_x=540, luz_y=700, pared_estilo="papel"), D("torta", x=540, y=1600, s=1.1)],
        comentario="Las mañanitas 🎂"),
])

# ================================================================ 50 · Frankenstein y el año sin verano
GINEBRA = [C("tormenta", horizonte=1300), D("montanas", horizonte=1300, nieve=True, colores=["#4a5a6a", "#3a4a5a", "#2a3a4a"]), MAR("tormenta", horizonte=1350)]
P[50] = dict(tema="cultura", estilo="terror", claves=["verano».", "Tambora,", "Byron,", "dieciocho"], tomas=[
    E("Mil ochocientos dieciséis", [C("niebla", horizonte=1300), D("arboles", y=1320, n=6, color="#3a4a3a"), D("suelo", y=1320, colores=["#e6edf7", "#9aa8bf"], tipo="nieve"), D("particulas", tipo="nieve", n=60)],
      "push", texto=["«EL AÑO SIN", "VERANO»"], acento=1, amb="viento"),
    E("Un año antes,", [C("rojo", horizonte=1300), MAR("atardecer", horizonte=1350), D("volcan", x=540, y=1380, s=1.1), D("particulas", tipo="ceniza", n=60)], "pull",
      dato=["VOLCÁN", "TAMBORA · 1815"], sfx="boom", amb="fuego"),
    M("en Indonesia, había", [-8.25, 118.0], 6, zoom_desde=1.5, centro_desde=[0, 60], resaltar=["Indonesia"], pines=[{"lat": -8.25, "lon": 118.0, "texto": "TAMBORA"}]),
    E("Su ceniza enfrió", [C("niebla", horizonte=1300), D("suelo", y=1300, colores=["#c8ced6", "#8a929e"], tipo="nieve"), D("casa", tipo="granja", x=540, y=1450, s=.8, luces=False),
      D("particulas", tipo="nieve", n=80)], "push", texto=["NIEVE EN", "PLENO VERANO"], acento=1, amb="viento"),
    E("En una casa", GINEBRA + [D("mansion", x=540, y=1420, s=.6), D("rayo", x=820, y=1000, en=1.5), D("lluvia")], "push", dato=["LAGO", "DE GINEBRA"], amb="lluvia", sfx="boom", sfx_en=1.5),
    E("un grupo de", [D("interior", pared="#3a2a2a", piso="#1a1010", vista="noche", ventana_x=700, luz=False), D("velas", x=540, y=1500, s=.7, n=3)] +
      [D("persona_real", x=x, y=1760, s=1.3, ropa=r, **k) for x, r, k in [(220, "traje", {"pelo": "#2a1a10"}), (540, "vestido", {"peinado": "largo", "pelo": "#6a3a1a"}), (860, "abrigo", {"bigote": True})]],
      "pull", dato=["LORD BYRON", "Y AMIGOS"], amb="lluvia", amb_vol=.5),
    T("Para pasar el", ["UN DESAFÍO:", "HISTORIAS DE TERROR"], acento=1, icono="🕯️"),
    E("Mary Shelley, de", [D("interior", pared="#3a2a2a", piso="#1a1010", vista="noche", ventana_x=700, luz=False), D("velas", x=380, y=1500, s=.6, n=1),
      D("persona_real", x=620, y=1720, s=1.8, ropa="vestido", peinado="largo", pelo="#6a3a1a"), D("rayo", x=750, y=900, en=2.0)], "push", dato=["MARY SHELLEY", "18 AÑOS"], amb="lluvia"),
    E("tuvo una pesadilla", [D("interior", pared="#1d2620", piso="#0d120e", luz=False, cuadros=0), D("cama", x=540, y=1550, s=1.1), D("rayo", x=540, y=1000, en=1.0),
      D("persona_real", x=820, y=1650, s=1.4, ropa="bata", peinado="alborotado")], "push_fuerte", texto=["DABA VIDA A", "UN CUERPO"], acento=1, sfx="boom", sfx_en=1.0),
    T("Así nació la", ["LA PRIMERA", "CIENCIA FICCIÓN"], acento=1, icono="⚡"),
    FIN("¿Has leído Frankenstein?", ["¿HAS LEÍDO", "FRANKENSTEIN?"], final="si_no", capas=GINEBRA + [D("mansion", x=540, y=1420, s=.6)]),
])

# ================================================================ 52 · Van Gogh
ARLES = [C("atardecer", horizonte=1250), D("girasoles", y=1250)]
VINCENT = dict(ropa="obrero", barba=True, pelo="#c0552a", sombrero="boina")
P[52] = dict(tema="cultura", estilo="calido", claves=["millones…", "novecientos", "rojo»,", "Johanna,"], tomas=[
    E("Hoy sus cuadros", [D("interior", pared="#e6e2da", piso="#8a7a6a", luz_x=540, luz_y=600, cuadros=0), D("caballete", x=540, y=1700, s=1.3, cuadro="girasoles")]
      + [D("persona_real", x=x, y=1800, s=1.1, ropa=r) for x, r in [(200, "traje"), (880, "vestido")]], "push", texto=["CIENTOS DE", "MILLONES"], acento=1, amb="multitud", amb_vol=.3),
    E("pero en vida,", ARLES + [D("persona_real", x=760, y=1800, s=1.6, **VINCENT), D("caballete", x=330, y=1760, s=1.0, cuadro="girasoles")], "push", dato=["VINCENT", "VAN GOGH"], amb="insectos", amb_vol=.4),
    N("Pintó unos novecientos", 900, "CUADROS", "EN 10 AÑOS", icono="🎨"),
    E("Vivía con lo", [D("interior", pared="#5a7aaa", piso="#8a5a2a", vista="dia", ventana_x=700, cuadros=0), D("cama", x=380, y=1550, s=1.0), D("silla", x=760, y=1650, s=.9)],
      "push", texto=["VIVÍA CON", "LO JUSTO"], acento=1),
    E("y su hermano", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("carta", x=540, y=1550, s=1.0, texto="Querido Vincent", firma="Theo")], "push",
      texto=["THEO LE MANDABA", "DINERO"], acento=0, sfx="papel", sfx_dur=.6),
    E("De todos ellos,", [D("interior", pared="#e6e2da", piso="#8a7a6a", luz_x=540, luz_y=600, cuadros=0), D("caballete", x=540, y=1750, s=1.5, cuadro="vinedo")], "push_fuerte",
      texto=["«EL VIÑEDO", "ROJO»"], acento=1),
    N("en mil ochocientos", 400, "FRANCOS", "1890", icono="💰"),
    E("Ese mismo año", [C("niebla", horizonte=1300), D("trigal", y=1300, circulo=False), D("persona_real", x=540, y=1760, s=1.6, **VINCENT)], "pull", texto=["CREÍA HABER", "FRACASADO"], acento=1, amb="viento"),
    E("Fue la esposa", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("caja", x=330, y=1650, s=.8), D("persona_real", x=700, y=1760, s=1.7, ropa="vestido", peinado="mono", pelo="#4a3a2a")],
      "push", dato=["JOHANNA", "VAN GOGH-BONGER"]),
    FIN("¿Cuál es tu", ["¿TU CUADRO", "FAVORITO?"], capas=ARLES + [D("caballete", x=540, y=1760, s=1.1)], comentario="La noche estrellada ✨"),
])

# ================================================================ 53 · Beethoven
TEATRO = dict(pared="#5a1a22", piso="#2a1410", luz_x=540, luz_y=600, pared_estilo="boiserie", cuadros=0)
LUDWIG = dict(ropa="traje", peinado="alborotado", pelo="#5a4a3a", panuelo="#f2efe6")
P[53] = dict(tema="cultura", estilo="clasico", claves=["oír.", "veintiocho", "vibraciones", "alegría»."], tomas=[
    E("Una de las", [D("interior", **TEATRO), D("piano", x=540, y=1650, s=1.1), D("notas", n=7, color="#ffd36a")], "push", texto=["NO PODÍA", "OÍR"], acento=1),
    E("Ludwig van Beethoven", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("piano", x=640, y=1650, s=1.0),
      D("persona_real", x=300, y=1720, s=1.7, **LUDWIG)], "push", dato=["BEETHOVEN", "28 AÑOS"]),
    E("Lo escondió durante", [D("interior", pared="#3a2a1e", piso="#1a120c", luz=False, cuadros=0), D("velas", x=700, y=1500, s=.6, n=2), D("persona_real", x=400, y=1760, s=1.9, **LUDWIG)],
      "push", texto=["¿UN MÚSICO", "SORDO?"], acento=1),
    E("Llegó a escribirle", [D("interior", pared="#3a2a1e", piso="#1a120c", luz_x=540, luz_y=900, cuadros=0), D("carta", x=540, y=1550, s=1.0, texto="A mis hermanos", firma="L. v. B.")],
      "push", texto=["PENSÓ EN", "RENDIRSE"], acento=1, sfx="papel", sfx_dur=.6),
    E("Pero siguió componiendo,", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz=False, cuadros=0), D("piano", x=540, y=1650, s=1.3), D("ondas" if False else "notas", n=6, color="#9ad0ff"),
      D("persona_real", x=230, y=1720, s=1.5, **LUDWIG)], "fijo", texto=["SENTÍA LAS", "VIBRACIONES"], acento=1),
    F("En mil ochocientos", "7", "MAYO", "1824"),
    E("estrenó su Novena", [D("interior", **TEATRO), D("piano", x=780, y=1650, s=.8)] + [D("persona_real", x=x, y=1720, s=1.0, ropa="traje") for x in (180, 330, 480)] +
      [D("persona_real", x=620, y=1700, s=1.5, **LUDWIG)], "pull", texto=["«HIMNO DE", "LA ALEGRÍA»"], acento=1, amb="multitud", amb_vol=.2),
    E("Al terminar, el", [D("interior", **TEATRO), D("butacas"), D("persona_real", x=540, y=1500, s=1.4, **LUDWIG, mira="izq")], "push", texto=["…Y ÉL NO", "LO OÍA"], acento=1, amb="multitud", amb_vol=1.0),
    E("Una cantante tuvo", [D("interior", **TEATRO), D("persona_real", x=380, y=1720, s=1.6, ropa="vestido", peinado="mono", pelo="#4a3a2a"), D("persona_real", x=700, y=1720, s=1.6, **LUDWIG, mira="izq")],
      "push", texto=["VIO LA", "OVACIÓN"], acento=1, amb="multitud"),
    FIN("¿Conoces el Himno", ["¿CONOCES EL", "HIMNO?"], final="si_no", capas=[D("interior", **TEATRO), D("piano", x=540, y=1650, s=1.0)]),
])

# ================================================================ 55 · Medallas olímpicas de arte
P[55] = dict(tema="historia", estilo="retro", claves=["pintar", "Coubertin,", "deporte.", "aficionados."], tomas=[
    E("Hubo una época", [C("dia", horizonte=1300), D("estadio", y=1300), D("podio", x=540, y=1700, s=1.0), D("caballete", x=540, y=1500, s=.6, cuadro="atletas")], "push",
      texto=["MEDALLA POR", "PINTAR"], acento=1, amb="multitud", amb_vol=.5),
    E("El creador de", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("persona_real", x=540, y=1760, s=1.9, ropa="traje", bigote=True, pelo="#d9d9d9")],
      "push", dato=["PIERRE DE", "COUBERTIN"]),
    E("quería unir el", [C("dia", horizonte=1300), D("estadio", y=1300), D("balon", x=300, y=1650, s=.6), D("libro", x=780, y=1650, s=.8)], "push", texto=["DEPORTE Y", "CULTURA"], acento=1, amb="multitud", amb_vol=.4),
    T("Por eso, entre", ["1912 – 1948"], icono="🏅"),
    E("se entregaron medallas", [D("interior", pared="#e6e2da", piso="#8a7a6a", luz_x=540, luz_y=600, cuadros=0), D("caballete", x=280, y=1700, s=.9, cuadro="atletas"),
      D("piano", x=760, y=1700, s=.7), D("libro", x=540, y=1800, s=.6)], "pan_der", texto=["PINTURA, MÚSICA,", "LITERATURA"], acento=0),
    E("La única condición:", [D("interior", pared="#e6e2da", piso="#8a7a6a", luz_x=540, luz_y=600, cuadros=0), D("caballete", x=540, y=1750, s=1.5, cuadro="atletas")], "push",
      texto=["INSPIRADAS EN", "EL DEPORTE"], acento=1),
    E("El propio Coubertin", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("medalla", x=760, y=1250, s=1.0), D("persona_real", x=330, y=1760, s=1.7, ropa="traje", bigote=True, pelo="#d9d9d9")],
      "push", texto=["¡GANÓ UN ORO!"], amb="ninguno"),
    E("con un poema", [D("interior", pared="#3a2a1e", piso="#1a120c", luz_x=540, luz_y=900), D("carta", x=540, y=1550, s=1.0, texto="Oda al deporte", firma="¿?")], "push",
      texto=["CON NOMBRE", "FALSO"], acento=1, sfx="papel", sfx_dur=.6),
    E("Al final se", [C("dia", horizonte=1300), D("estadio", y=1300), D("podio", x=540, y=1700, s=1.0)], "pull", texto=["SOLO", "AFICIONADOS"], acento=1, amb="multitud", amb_vol=.4),
    FIN("¿En qué arte", ["¿EN QUÉ ARTE", "GANARÍAS?"], capas=[D("interior", pared="#e6e2da", piso="#8a7a6a", luz_x=540, luz_y=600, cuadros=0), D("medalla", x=540, y=1400, s=1.2)], comentario="En dormir 😴"),
])

# ================================================================ 56 · Pickles y la Copa
LONDRES66 = [C("dia", horizonte=1300), D("ciudad", era="antigua", y=1330, hora="dia", semilla=3), D("suelo", y=1330, colores=["#5a8a3a", "#2a4a1a"], tipo="pasto")]
P[56] = dict(tema="historia", estilo="pop", claves=["perro.", "Rimet,", "rescate", "Pickles"], tomas=[
    E("En mil novecientos", LONDRES66 + [D("trofeo", x=380, y=1700, s=1.0), D("perro", raza="collie", x=740, y=1720, s=1.1)], "push", texto=["¡ROBARON LA", "COPA!"], acento=1, amb="viento", amb_vol=.4),
    E("Faltaban cuatro meses", [C("dia", horizonte=1300), D("estadio", y=1300)], "pull", dato=["MUNDIAL", "INGLATERRA 66"], amb="multitud"),
    E("El trofeo, la", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("vitrina", x=540, y=1650, s=1.1), D("trofeo", x=540, y=1500, s=.6)],
      "push", dato=["COPA", "JULES RIMET"]),
    E("Un domingo, aprovechando", [D("interior", pared="#3a3226", piso="#1a140f", luz=False, cuadros=0), D("vitrina", x=380, y=1650, s=1.0),
      D("persona_real", x=780, y=1720, s=1.6, ropa="abrigo", sombrero="fedora", mov="camina", avance=200)], "pan_der", texto="¡SE LA LLEVARON!", sfx="crujido", sfx_dur=.6),
    E("Hubo pedidos de", [D("interior", pared="#3a4a5a", piso="#1a222a", luz_x=540, luz_y=700, cuadros=0), D("telefono", x=380, y=1550, s=1.0), D("persona_real", x=760, y=1720, s=1.6, ropa="uniforme", sombrero="casco_ww")],
      "push", texto=["PEDIDOS DE", "RESCATE"], acento=1, amb="estatica", amb_vol=.3),
    E("Una semana después,", LONDRES66 + [D("persona_real", x=330, y=1720, s=1.5, ropa="traje_cafe", mira="der"), D("perro", raza="collie", x=640, y=1740, s=1.0)], "pan_der",
      dato=["PICKLES", "COLLIE"], amb="insectos", amb_vol=.3),
    E("y el perro", LONDRES66 + [D("arbusto", x=700, y=1700, s=1.1, paquete=True), D("perro", raza="collie", x=330, y=1760, s=1.2)], "push", texto=["UN PAQUETE DE", "PAPEL DE DIARIO"], acento=1),
    E("Era la Copa.", [C("dia", horizonte=1300), D("suelo", y=1300, colores=["#5a8a3a", "#2a4a1a"], tipo="pasto"), D("trofeo", x=540, y=1600, s=1.5)], "push_fuerte", texto="¡ERA LA COPA!", sfx="ping", sfx_dur=.6),
    E("Pickles se hizo", [C("dia", horizonte=1300), D("estadio", y=1300), D("perro", raza="collie", x=540, y=1760, s=1.4), D("medalla", x=560, y=1450, s=.5)], "pull",
      texto=["¡INVITADO A LA", "CELEBRACIÓN!"], acento=1, amb="multitud"),
    FIN("¿Tienes un perro", ["¿TU PERRO ES", "ASÍ DE LISTO?"], capas=LONDRES66 + [D("perro", raza="collie", x=540, y=1720, s=1.3)], comentario="El mío solo come 🐶"),
])

# ================================================================ 60 · Hadas de Cottingley
ARROYO = [C("dia", horizonte=1250), D("arboles", y=1270, n=7, color="#2e4a22"), MAR("dia", horizonte=1450), D("suelo", y=1550, colores=["#5a8a3a", "#2a4a1a"], tipo="pasto")]
NINA = dict(ropa="vestido", peinado="largo", pelo="#6a4a2a")
P[60] = dict(tema="misterio", estilo="clasico", claves=["hadas…", "Cottingley.", "Doyle,", "recortados"], tomas=[
    E("En mil novecientos", ARROYO + [D("persona_real", x=380, y=1780, s=1.3, **NINA), D("hadas", x=680, y=1450, n=4)], "push", dato=["1917", "¿HADAS?"], amb="rio"),
    E("Elsie Wright y", ARROYO + [D("persona_real", x=330, y=1780, s=1.4, **NINA), D("persona_real", x=700, y=1800, s=1.15, ropa="vestido", peinado="largo", pelo="#c09a5a")], "push",
      dato=["ELSIE Y", "FRANCES"], amb="rio"),
    E("Para demostrar que", ARROYO + [D("camara_antigua", x=760, y=1800, s=1.1), D("persona_real", x=330, y=1780, s=1.4, **NINA)], "push", texto=["UNA CÁMARA", "PRESTADA"], acento=1, amb="rio"),
    E("y volvieron con", ARROYO + [D("persona_real", x=540, y=1780, s=1.6, ropa="vestido", peinado="largo", pelo="#c09a5a"), D("hadas", x=540, y=1350, n=5)], "push_fuerte",
      texto=["HADAS", "BAILANDO"], acento=1, sfx="ping", sfx_dur=.5, amb="rio"),
    E("Incluso Arthur Conan", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("libro", x=780, y=1600, s=.7),
      D("persona_real", x=380, y=1760, s=1.8, ropa="traje", bigote=True, pelo="#6a5a4a")], "push", dato=["ARTHUR", "CONAN DOYLE"]),
    T("creyó que eran", ["¡CREYÓ QUE", "ERAN REALES!"], acento=1, icono="🧚"),
    F("Recién en mil", "", "AÑO", "1983") if False else T("Recién en mil", ["1983:", "CONFESARON"], acento=1, icono="🗝️"),
    E("eran dibujos recortados", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=900, cuadros=0), D("mesa", x=540, y=1650, s=1.2), D("libro", x=380, y=1450, s=.7),
      D("hadas", x=680, y=1350, n=2)], "push", texto=["RECORTES CON", "ALFILERES"], acento=1, sfx="papel", sfx_dur=.6),
    E("Pero Frances juró", ARROYO + [D("hadas", x=540, y=1400, n=3), D("niebla", y=1450, op=.4)], "push", texto=["LA QUINTA FOTO", "¿ERA REAL?"], acento=1, amb="rio"),
    FIN("¿Tú les habrías", ["¿LES HABRÍAS", "CREÍDO?"], final="si_no", capas=ARROYO + [D("hadas", x=540, y=1350, n=3)]),
])

# ================================================================ 61 · Hombre de Piltdown
MUSEO = dict(pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700, pared_estilo="boiserie")
P[61] = dict(tema="misterio", estilo="periodico", claves=["falso.", "Piltdown,", "África", "orangután,"], tomas=[
    E("Durante cuarenta años,", [D("interior", **MUSEO), D("libro", x=540, y=1500, s=1.4)], "push", texto=["EL «ESLABÓN", "PERDIDO»"], acento=1),
    E("y era falso.", [D("interior", **MUSEO), D("vitrina", x=540, y=1650, s=1.1), D("craneo_fosil", x=540, y=1480, s=.5)], "push_fuerte", texto="¡ERA FALSO!", sfx="boom", sfx_dur=.6),
    M("En mil novecientos", [50.97, 0.07], 30, zoom_desde=3, centro_desde=[50, -2], resaltar=["United Kingdom"], pines=[{"lat": 50.97, "lon": 0.07, "texto": "PILTDOWN"}], titulo="1912"),
    E("el aficionado Charles", [C("niebla", horizonte=1300), D("suelo", y=1300, colores=["#7a6a4a", "#3a3020"], tipo="tierra"), D("persona_real", x=540, y=1760, s=1.8, ropa="traje_cafe", bigote=True, sombrero="bombin")],
      "push", dato=["CHARLES", "DAWSON"], amb="viento"),
    E("un cráneo con", [D("interior", pared="#1d2233", piso="#0d1018", luz=False, cuadros=0), D("craneo_fosil", x=540, y=1500, s=1.4)], "push", texto=["CEREBRO GRANDE,", "MANDÍBULA DE MONO"], acento=1),
    E("Parecía la prueba", [C("dia", horizonte=1300), D("suelo", y=1300, colores=["#7a6a4a", "#3a3020"], tipo="tierra"), D("bandera", x=540, y=1600, s=1.1, colores=["#1a3a8a", "#ffffff", "#c8102e"])],
      "pull", texto=["¿EL ORIGEN EN", "EUROPA?"], acento=1),
    E("Muchos expertos lo", [D("interior", **MUSEO)] + [D("persona_real", x=x, y=1760, s=1.2, ropa=r, bigote=True, lentes=k) for x, r, k in [(200, "traje", True), (540, "traje_gris", False), (880, "traje_cafe", True)]],
      "pan_der", texto=["LOS EXPERTOS", "LO ACEPTARON"], acento=1),
    E("En mil novecientos", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz_x=540, luz_y=700, cuadros=0), D("mesa", x=540, y=1650, s=1.2), D("craneo_fosil", x=540, y=1450, s=.8, lupa=True)],
      "push", dato=["1953", "NUEVAS PRUEBAS"]),
    E("era un cráneo", [D("interior", pared="#1d2233", piso="#0d1018", luz=False, cuadros=0), D("craneo_fosil", x=540, y=1500, s=1.5)], "push_fuerte",
      texto=["CRÁNEO MEDIEVAL +", "MANDÍBULA DE ORANGUTÁN"], acento=1, sfx="boom"),
    T("Nunca se supo", ["¿QUIÉN", "LO HIZO?"], acento=1, icono="🕵️"),
    FIN("¿Conocías este fraude?", ["¿CONOCÍAS", "ESTE FRAUDE?"], capas=[D("interior", **MUSEO), D("craneo_fosil", x=540, y=1600, s=1.0)], comentario="Ni idea 😳"),
])

# ================================================================ 66 · Annabelle real
DEPTO70 = dict(pared="#b8945a", piso="#5a3a22", vista="noche", ventana_x=700, pared_estilo="rombos")
P[66] = dict(tema="terror", estilo="terror", claves=["distinta.", "roja,", "notas", "abrir»."], tomas=[
    E("La Annabelle de", [D("interior", pared="#1a1410", piso="#0a0806", luz=False, cuadros=0), D("muneca", x=540, y=1600, s=1.5)], "push", texto=["LA DE LAS", "PELÍCULAS"], acento=1, amb="viento", amb_vol=.4),
    E("pero la verdadera", [D("interior", pared="#1a1410", piso="#0a0806", luz_x=540, luz_y=900, cuadros=0), D("muneca_trapo", x=540, y=1650, s=1.6)], "push_fuerte", texto="LA VERDADERA", sfx="boom", sfx_dur=.5),
    E("Es una muñeca", [D("interior", **DEPTO70), D("silla", x=540, y=1700, s=1.1), D("muneca_trapo", x=540, y=1500, s=.9)], "push", texto=["DE TRAPO Y", "LANA ROJA"], acento=1),
    T("una «Raggedy Ann»", ["AÑOS", "70"], icono="🧸"),
    E("Según la historia,", [D("interior", **DEPTO70), D("muneca_trapo", x=760, y=1700, s=.8), D("persona_real", x=330, y=1720, s=1.6, ropa="bata", peinado="largo", pelo="#6a4a2a")], "push",
      dato=["ESTUDIANTE DE", "ENFERMERÍA"]),
    E("Ella y su", [D("interior", **DEPTO70), D("cama", x=330, y=1600, s=.9), D("muneca_trapo", x=800, y=1700, s=.8, mov="desvanece")], "pan_der", texto=["CAMBIABA DE", "LUGAR"], acento=1, amb="viento", amb_vol=.3),
    E("y que aparecían", [D("interior", pared="#1d1a14", piso="#0d0a06", luz=False, cuadros=0), D("carta", x=540, y=1550, s=1.0, texto="Ayúdanos", firma="")], "push", texto=["NOTAS ESCRITAS", "A MANO"], acento=1, sfx="papel", sfx_dur=.6),
    E("Los investigadores paranormales", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700), D("persona_real", x=330, y=1740, s=1.6, ropa="traje", peinado="corto"),
      D("persona_real", x=730, y=1740, s=1.6, ropa="vestido", peinado="largo", pelo="#3a2a1e")], "push", dato=["ED Y LORRAINE", "WARREN"]),
    E("y la guardaron", [D("interior", pared="#2a221a", piso="#120e0a", luz=False, cuadros=0), D("vitrina", x=540, y=1700, s=1.3), D("muneca_trapo", x=540, y=1550, s=.6),
      D("cartel", x=540, y=1150, s=.6, titulo="PELIGRO", sub="NO ABRIR")], "push_fuerte", texto=["«PELIGRO,", "NO ABRIR»"], acento=1),
    FIN("¿Tú crees en", ["¿CREES EN", "ESTAS HISTORIAS?"], final="si_no", capas=[D("interior", pared="#2a221a", piso="#120e0a", luz=False, cuadros=0), D("vitrina", x=540, y=1700, s=1.2), D("muneca_trapo", x=540, y=1550, s=.6)]),
])

# ================================================================ 67 · La bruja de Bell
TENNESSEE = [C("noche", horizonte=1300), D("arboles", y=1320, n=6, color="#14200f"), D("suelo", y=1320, colores=["#3a4a2a", "#141a0e"], tipo="pasto")]
CUARTO_BELL = dict(pared="#4a3a2a", piso="#20160e", luz=False, vista="noche", ventana_x=720)
P[67] = dict(tema="terror", estilo="terror", claves=["persona.", "golpes", "Jackson", "frasco"], tomas=[
    E("Es la única", TENNESSEE + [D("casa", tipo="madera", x=540, y=1450, s=.9, luces=True), D("niebla", y=1400, op=.5)], "push", texto=["EL ESPÍRITU", "QUE MATÓ"], acento=1, amb="viento"),
    M("En mil ochocientos", [36.5, -87.0], 7, zoom_desde=2, centro_desde=[39, -95], resaltar=["United States of America"], pines=[{"lat": 36.5, "lon": -87.0, "texto": "TENNESSEE"}], titulo="1817"),
    E("Primero vieron un", TENNESSEE + [D("ojos", x=540, y=1500, s=.8, en=.5, color="#ffcf6a")], "push", texto=["UN ANIMAL", "EXTRAÑO"], acento=1, amb="insectos", amb_vol=.4),
    E("Después empezaron los", [D("interior", **CUARTO_BELL), D("cama", x=420, y=1550, s=1.0), D("velas", x=820, y=1500, s=.5, n=1)], "fijo", texto=["GOLPES EN LAS", "PAREDES"], acento=1,
      sacudir=True, sfx="crujido", sfx_dur=1.0),
    E("y las sábanas", [D("interior", **CUARTO_BELL), D("cama", x=420, y=1550, s=1.0), D("sabana", x=420, y=1400, s=1.0, en=.3)], "push", texto=["SÁBANAS", "ARRANCADAS"], acento=1, amb="viento"),
    E("Con el tiempo,", [D("interior", **CUARTO_BELL), D("silbido", x1=200, y1=1000, x2=900, color="#dfe8ff"), D("persona_real", x=540, y=1760, s=1.8, ropa="obrero", barba=True, pelo="#d9d9d9")],
      "push", texto=["UNA VOZ DE", "MUJER"], acento=1, amb="viento"),
    E("Dicen que hasta", TENNESSEE + [D("persona_real", x=540, y=1760, s=1.8, ropa="uniforme", pelo="#d9d9d9", peinado="alborotado")], "push", dato=["ANDREW", "JACKSON"], amb="insectos", amb_vol=.3),
    T("En mil ochocientos", ["1820:", "JOHN BELL MURIÓ"], acento=1, icono="⚰️"),
    E("Junto a él", [D("interior", pared="#1d1a14", piso="#0d0a06", luz=False, cuadros=0), D("frasco", x=540, y=1500, s=1.3, contenido="liquido", color_liquido="#4a3a5a")], "push_fuerte",
      texto=["UN FRASCO", "EXTRAÑO"], acento=1, sfx="boom", sfx_dur=.5),
    FIN("¿Crees que fue", ["¿FUE", "REAL?"], final="si_no", capas=TENNESSEE + [D("casa", tipo="madera", x=540, y=1450, s=.9, luces=True)]),
])

# ================================================================ 69 · Casa Winchester
SANJOSE = [C("noche", horizonte=1400), D("suelo", y=1450, colores=["#3a4a2a", "#141a0e"], tipo="pasto")]
SARAH = dict(ropa="luto", peinado="mono", pelo="#4a4a4a")
P[69] = dict(tema="misterio", estilo="terror", claves=["nada.", "rifles", "treinta", "espíritus"], tomas=[
    E("En California hay", SANJOSE + [D("mansion", x=540, y=1460, s=1.0)], "push", texto=["PUERTAS A", "LA NADA"], acento=1, amb="viento"),
    E("y puertas que", [D("interior", pared="#5a3a3a", piso="#2a1a1a", luz=False, pared_estilo="papel", cuadros=0), D("pasillo" if False else "puerta_tumba", x=540, y=1600, s=1.0)], "push_fuerte",
      texto=["ESCALERAS AL", "TECHO"], acento=1),
    E("Sarah Winchester heredó", [D("interior", pared="#3a2a2a", piso="#1a1010", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("persona_real", x=540, y=1760, s=1.9, **SARAH)], "push",
      dato=["SARAH", "WINCHESTER"]),
    E("de la empresa", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700), D("vitrina", x=540, y=1650, s=1.1)], "push", texto=["FORTUNA DE", "RIFLES"], acento=1),
    M("En mil ochocientos", [37.32, -121.95], 10, zoom_desde=2, centro_desde=[39, -100], resaltar=["United States of America"], pines=[{"lat": 37.32, "lon": -121.95, "texto": "SAN JOSÉ"}], titulo="1886"),
    N("La construcción no", 38, "AÑOS", "DÍA Y NOCHE", icono="🔨"),
    N("Llegó a tener", 160, "HABITACIONES", "UNAS", icono="🚪"),
    E("pasillos sin salida", [D("pasillo", luz=False), D("persona_real", x=540, y=1500, s=1.0, **SARAH, mov="camina", avance=-60)], "push", texto=["PASILLOS SIN", "SALIDA"], acento=1, amb="viento", amb_vol=.4),
    E("La leyenda dice", SANJOSE + [D("mansion", x=540, y=1460, s=1.0), D("persona_real", x=540, y=1500, s=1.0, ropa="camisa", peinado="largo", mov="desvanece") , D("niebla", y=1400, op=.6)],
      "push", texto=["¿PARA CONFUNDIR", "ESPÍRITUS?"], acento=1, amb="viento"),
    E("Los historiadores creen", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("mesa", x=540, y=1650, s=1.2), D("hoja", x=540, y=1480, s=.8),
      D("persona_real", x=820, y=1720, s=1.5, **SARAH)], "push", texto=["LE GUSTABA", "DISEÑAR"], acento=1),
    FIN("¿Tú cuál crees?", ["¿TÚ CUÁL", "CREES?"], capas=SANJOSE + [D("mansion", x=540, y=1460, s=1.0)], comentario="Los espíritus 👻"),
])

# ================================================================ 70 · Catacumbas de París
P[70] = dict(tema="misterio", estilo="terror", claves=["millones", "canteras", "kilómetros.", "salió."], tomas=[
    E("Bajo las calles", [C("noche", horizonte=1100), D("ciudad", era="antigua", y=1150, hora="noche"), D("torre_eiffel", x=800, y=1160, s=.6), D("suelo", y=1150, colores=["#4a3a2a", "#1a120c"])],
      "baja", texto=["BAJO PARÍS"], amb="viento"),
    N("descansan los restos", 6, "MILLONES", "DE PERSONAS", icono="💀"),
    E("A finales del", [C("niebla", horizonte=1350), D("catedral", x=540, y=1450, s=.8), D("estacas", x=540, y=1700, s=1.0), D("suelo", y=1450, colores=["#5a4a3a", "#2a1d14"], tipo="tierra")],
      "push", texto=["CEMENTERIOS", "LLENOS"], acento=1, amb="viento"),
    E("Así que trasladaron", [C("noche", horizonte=1350), D("ciudad", era="antigua", y=1380, hora="noche"), D("suelo", y=1380, colores=["#6a6a5a", "#2a2a22"], tipo="adoquin"),
      D("carpa" if False else "barril", x=400, y=1700, s=1.0), D("persona_real", x=700, y=1720, s=1.3, ropa="obrero", sombrero="boina")], "pan_der", texto=["DE NOCHE,", "A LAS CANTERAS"], acento=1),
    E("Los acomodaron en", [D("osario")], "push", texto=["PAREDES DE", "CALAVERAS"], acento=1, amb="viento", amb_vol=.4),
    T("que se extienden", ["KILÓMETROS"], acento=0, icono="🗺️"),
    E("En mil setecientos", [D("osario"), D("persona_real", x=540, y=1500, s=1.0, ropa="obrero", mov="camina", avance=-40), D("velas", x=600, y=1350, s=.4, n=1)], "push",
      dato=["PHILIBERT", "ASPAIRT · 1793"], amb="viento", amb_vol=.5),
    E("y nunca salió.", [D("tunel"), D("velas", x=540, y=1500, s=.6, n=1)], "push_fuerte", texto="NUNCA SALIÓ", amb="viento"),
    N("Encontraron sus restos", 11, "AÑOS", "DESPUÉS", icono="⏳"),
    E("Hoy hay una", [D("osario"), D("lapida" if False else "cartel", x=540, y=1550, s=.7, titulo="PHILIBERT", sub="1793")], "push", texto=["UNA TUMBA CON", "SU NOMBRE"], acento=1),
    FIN("¿Te atreverías a", ["¿TE ATREVERÍAS", "A BAJAR?"], final="si_no", capas=[D("osario")]),
])

# ================================================================ 71 · Momias de Guanajuato
GTO = [C("dia", horizonte=1300), D("montanas", horizonte=1320, colores=["#a88a6a", "#8a6a4a", "#6a4a32"]), D("ciudad", era="colonial", y=1350, hora="dia", semilla=21),
       D("suelo", y=1350, colores=["#a8906e", "#5a4630"], tipo="adoquin")]
P[71] = dict(tema="misterio", estilo="calido", claves=["momificar.", "impuesto:", "solos,", "Museo"], tomas=[
    E("En México hay", [D("interior", pared="#3a2a2a", piso="#1a1010", luz=False, cuadros=0), D("momia_gto", x=330, y=1700, s=1.2), D("momia_gto", x=760, y=1700, s=1.1)], "push",
      texto=["NADIE QUISO", "MOMIFICARLAS"], acento=1),
    M("En mil ochocientos", [21.02, -101.26], 12, zoom_desde=2, centro_desde=[23, -102], resaltar=["Mexico"], pines=[{"lat": 21.02, "lon": -101.26, "texto": "GUANAJUATO"}], titulo="1865"),
    E("Guanajuato creó un", GTO + [D("carta", x=540, y=1650, s=.8, texto="Impuesto", firma="Panteón")], "push", texto=["UN IMPUESTO", "A LOS MUERTOS"], acento=1, sfx="papel", sfx_dur=.6),
    E("Si no pagaban,", [C("dia", horizonte=1300), D("suelo", y=1300, colores=["#a8906e", "#5a4630"], tipo="tierra"), D("ataud", x=540, y=1600, s=1.0),
      D("persona_real", x=820, y=1720, s=1.4, ropa="obrero", sombrero="fedora", piel="media")], "push", texto=["LOS", "DESENTERRABAN"], acento=1, amb="viento"),
    E("muchos se habían", [D("interior", pared="#1d1a14", piso="#0d0a06", luz=False, cuadros=0), D("momia_gto", x=540, y=1750, s=1.7)], "push_fuerte", texto=["¡SE MOMIFICARON", "SOLOS!"], acento=1, sfx="boom"),
    E("por el clima", [C("dia", horizonte=1300), D("desierto", y=1300), D("particulas", tipo="polvo", n=40)], "pan_der", texto=["CLIMA SECO", "Y SUELO"], acento=1, amb="viento"),
    E("Las momias se", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700, cuadros=0), D("momia_gto", x=330, y=1650, s=1.0), D("momia_gto", x=760, y=1650, s=1.0)]
      + [D("persona_real", x=x, y=1800, s=1.0, ropa=r) for x, r in [(200, "traje"), (900, "vestido")]], "pull", texto=["PAGABAN POR", "VERLAS"], acento=1, amb="multitud", amb_vol=.3),
    E("Algunas conservan la", [D("interior", pared="#1d1a14", piso="#0d0a06", luz=False, cuadros=0), D("vitrina", x=540, y=1700, s=1.3), D("momia_gto", x=540, y=1640, s=.7)], "push",
      texto=["ROPA, PELO…", "Y SORPRESA"], acento=1),
    N("Hoy el Museo", 1000, "VISITANTES", "MILES AL AÑO", icono="🏛️"),
    FIN("¿Lo visitarías? Comenta", ["¿LO", "VISITARÍAS?"], final="si_no", capas=GTO + [D("catedral", x=540, y=1380, s=.6)]),
])

# ================================================================ 73 · Brujas de Salem
SALEM = [C("niebla", horizonte=1300), D("casa", tipo="colonial", x=300, y=1420, s=.7, luces=False), D("catedral", x=800, y=1420, s=.6), D("suelo", y=1420, colores=["#5a4a3a", "#2a1d14"], tipo="tierra")]
JUICIO = dict(pared="#4a3a2a", piso="#20160e", luz_x=540, luz_y=600, pared_estilo="boiserie", cuadros=0)
PURITANO = dict(ropa="puritano", sombrero="copa")
P[73] = dict(tema="historia", estilo="terror", claves=["brujería.", "diablo.", "Diecinueve", "centeno"], tomas=[
    E("En mil seiscientos", [D("interior", pared="#3a2a1e", piso="#1a120c", luz=False, cuadros=0), D("velas", x=820, y=1500, s=.5, n=2),
      D("persona_real", x=420, y=1740, s=1.7, ropa="vestido", peinado="mono", pelo="#6a4a2a", mira="der")], "fijo", texto=["GRITABAN Y SE", "RETORCÍAN"], acento=1, sacudir=True, amb="viento"),
    T("y acusar a", ["¡BRUJERÍA!"], entrada="flash", sfx="boom"),
    M("Fue en Salem,", [42.52, -70.9], 20, zoom_desde=2, centro_desde=[40, -90], resaltar=["United States of America"], pines=[{"lat": 42.52, "lon": -70.9, "texto": "SALEM"}], titulo="1692"),
    E("Los médicos no", [D("interior", pared="#3a2a1e", piso="#1a120c", luz_x=540, luz_y=900, cuadros=0), D("cama", x=540, y=1550, s=1.0), D("persona_real", x=850, y=1700, s=1.4, **PURITANO, barba=True)],
      "push", texto=["¿OBRA DEL", "DIABLO?"], acento=1),
    N("Más de doscientas", 200, "ACUSADOS", "MÁS DE", icono="⚖️"),
    E("Las pruebas eran", [D("interior", **JUICIO), D("mesa", x=540, y=1600, s=1.4), D("persona_real", x=300, y=1500, s=1.1, **PURITANO), D("persona_real", x=780, y=1500, s=1.1, **PURITANO, barba=True),
      D("persona_real", x=540, y=1820, s=1.4, ropa="luto", peinado="mono")], "push", texto=["SUEÑOS Y", "VISIONES"], acento=1, amb="multitud", amb_vol=.3),
    E("Diecinueve fueron ahorcadas", SALEM + [D("velas", x=540, y=1650, s=.8, n=5)], "pull", dato=["19", "EJECUTADAS"], amb="viento"),
    E("Una teoría dice", [C("dia", horizonte=1300), D("trigal", y=1300, circulo=False), D("particulas", tipo="polvo", n=30)], "push", texto=["¿UN HONGO DEL", "CENTENO?"], acento=1, amb="viento", amb_vol=.4),
    E("Pero muchos historiadores", SALEM + [D("persona_real", x=x, y=1720, s=1.0, ropa=r, **k) for x, r, k in [(200, "puritano", {"sombrero": "copa"}), (420, "luto", {"peinado": "mono"}), (680, "puritano", {}), (900, "vestido", {"peinado": "mono"})]],
      "pan_der", texto=["MIEDO, RENCOR", "Y PÁNICO"], acento=1, amb="multitud", amb_vol=.4),
    FIN("¿Tú qué crees", ["¿QUÉ CREES", "QUE PASÓ?"], capas=SALEM, comentario="Fue el miedo 😨"),
])

# ================================================================ 74 · Condesa Báthory
CACHTICE = [C("tormenta", horizonte=1350), D("montanas", horizonte=1380, colores=["#3a3a4a", "#2a2a3a", "#1a1a2a"]), D("castillo", x=540, y=1420, s=1.0), D("suelo", y=1420, colores=["#3a3a2a", "#141410"], tipo="tierra")]
SALON = dict(pared="#3a3a3e", piso="#1a1a1e", luz=False, cuadros=0)
ISABEL = dict(ropa="luto", peinado="mono", pelo="#2a1a10", piel="clara")
P[74] = dict(tema="historia", estilo="terror", claves=["sangrienta».", "Hungría,", "juicio.", "enemigos,"], tomas=[
    E("La llamaban «la", CACHTICE, "push", texto=["«LA CONDESA", "SANGRIENTA»"], acento=1, amb="viento"),
    T("Pero hay historiadores", ["¿Y SI NO", "FUE ASÍ?"], acento=1, icono="🤔"),
    E("Isabel Báthory fue", [D("interior", **SALON), D("antorcha", x=200, y=1300, s=.8), D("antorcha", x=880, y=1300, s=.8), D("persona_real", x=540, y=1760, s=1.9, **ISABEL)],
      "push", dato=["ISABEL", "BÁTHORY"], amb="fuego", amb_vol=.4),
    E("una de las", [D("interior", **SALON), D("antorcha", x=540, y=1250, s=.8), D("tesoro", x=540, y=1650, s=1.0)], "push", texto=["DE LAS MÁS", "RICAS"], acento=1, amb="fuego", amb_vol=.3),
    E("En mil seiscientos", CACHTICE + [D("persona_real", x=x, y=1740, s=.9, ropa="vestido", peinado="largo") for x in (250, 830)], "push", dato=["1610", "ACUSADA"], amb="viento"),
    E("Nunca tuvo un", [D("interior", **SALON), D("mesa", x=540, y=1650, s=1.3), D("persona_real", x=330, y=1500, s=1.0, ropa="traje", barba=True), D("persona_real", x=760, y=1500, s=1.0, ropa="traje", barba=True)],
      "push", texto=["NUNCA TUVO", "UN JUICIO"], acento=1),
    E("La encerraron en", [D("interior", pared="#2a2a2e", piso="#121214", luz=False, cuadros=0, vista="noche", ventana_x=540), D("velas", x=700, y=1550, s=.5, n=1), D("persona_real", x=420, y=1760, s=1.6, **ISABEL)],
      "push", texto=["ENCERRADA", "4 AÑOS"], acento=1, sfx="crujido", sfx_dur=.8),
    E("Con el tiempo", [D("interior", **SALON), D("antorcha", x=540, y=1250, s=.8), D("barril", x=540, y=1650, s=1.2), D("luz", x=540, y=1600, r=300, color="#c1121f", op=.4)], "push",
      texto=["¿BAÑOS DE", "SANGRE?"], acento=1),
    E("algo que nadie", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=900, cuadros=0), D("libro", x=540, y=1500, s=1.3)], "push", texto=["INVENTADO", "DESPUÉS"], acento=1, sfx="papel", sfx_dur=.6),
    E("Algunos historiadores creen", CACHTICE + [D("persona_real", x=x, y=1760, s=1.0, ropa="traje", barba=True, sombrero="copa") for x in (200, 400, 700, 900)], "pull",
      texto=["¿VÍCTIMA DE", "SUS ENEMIGOS?"], acento=1, amb="viento"),
    FIN("¿Culpable o víctima?", ["¿CULPABLE", "O VÍCTIMA?"], capas=CACHTICE, comentario="Víctima ⚖️"),
])

# ================================================================ 76 · Amityville
AMITY = [C("noche", horizonte=1450), D("arboles", y=1460, n=5, color="#14200f"), D("mansion", estilo="amityville", x=540, y=1520, s=1.0), D("suelo", y=1520, colores=["#3a4a2a", "#141a0e"], tipo="pasto")]
P[76] = dict(tema="terror", estilo="terror", claves=["mentira", "DeFeo", "moscas", "vino»."], tomas=[
    E("La casa embrujada", AMITY, "push", texto=["¿LA CASA MÁS", "EMBRUJADA?"], acento=1, amb="viento"),
    T("podría haber sido", ["¿UNA", "MENTIRA?"], acento=1, icono="🍷"),
    M("En mil novecientos", [40.67, -73.42], 25, zoom_desde=2, centro_desde=[40, -90], resaltar=["United States of America"], pines=[{"lat": 40.67, "lon": -73.42, "texto": "AMITYVILLE"}], titulo="1974"),
    E("Ronald DeFeo mató", AMITY + [D("sirenas_policia", y=1500)], "push", texto=["MATÓ A", "SU FAMILIA"], acento=1, amb="viento"),
    E("Un año después,", [C("dia", horizonte=1450), D("arboles", y=1460, n=5), D("mansion", estilo="amityville", x=540, y=1520, s=1.0, luces=False), D("suelo", y=1520, colores=["#5a8a3a", "#2a4a1a"], tipo="pasto"),
      D("persona_real", x=200, y=1800, s=1.2, ropa="camisa", bigote=True), D("persona_real", x=880, y=1800, s=1.2, ropa="vestido", peinado="largo")], "pull", dato=["LOS LUTZ", "1975"]),
    E("Contaron que escuchaban", [D("interior", pared="#5a4a3a", piso="#2a1d14", luz=False, cuadros=0), D("silbido", x1=200, y1=1000, x2=900, color="#dfe8ff")], "push", texto="VOCES", amb="viento"),
    E("que un enjambre", [D("interior", pared="#5a4a3a", piso="#2a1d14", luz=False, vista="nieve", ventana_x=540, cuadros=0), D("particulas", tipo="moscas", n=80)], "push_fuerte",
      texto=["MOSCAS EN", "PLENO INVIERNO"], acento=1, amb="zumbido", amb_vol=.6),
    N("y que una", 28, "DÍAS", "HUYERON A LOS", icono="🏃"),
    E("Su historia se", [D("interior", pared="#2a1a1e", piso="#110a0c", luz=False, cuadros=0), D("pantalla", x=540, y=1150, s=1.6, texto=""), D("libro", x=540, y=1500, s=.9), D("butacas")],
      "pull", texto=["LIBRO Y", "PELÍCULA"], acento=1),
    E("Pero años después,", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700), D("mesa", x=540, y=1650, s=1.2), D("botella", x=420, y=1450, s=.8), D("botella", x=560, y=1460, s=.7),
      D("persona_real", x=820, y=1700, s=1.5, ropa="traje", bigote=True)], "push", texto=["«CON MUCHAS BOTELLAS", "DE VINO»"], acento=1),
    E("Las familias que", AMITY[:2] + [D("mansion", estilo="amityville", x=540, y=1520, s=1.0, luces=False), D("suelo", y=1520, colores=["#3a4a2a", "#141a0e"], tipo="pasto")], "pull",
      texto=["NO NOTARON", "NADA"], acento=1, amb="insectos", amb_vol=.3),
    FIN("¿Tú qué crees?", ["¿TÚ QUÉ", "CREES?"], capas=AMITY, comentario="Fue el vino 🍷"),
])

# ================================================================ 77 · Hombre Polilla
POINT = [C("noche", horizonte=1100), D("puente", y=1250)]
P[77] = dict(tema="misterio", estilo="neon", claves=["rojos,", "persiguió", "Mothman»,", "cuarenta"], tomas=[
    E("Ojos rojos, brillantes,", [C("noche", horizonte=1300), D("arboles", y=1320, n=6, color="#0d140a"), D("ojos", x=540, y=1100, s=1.2, en=.3, color="#ff3030")], "push_fuerte",
      texto="OJOS ROJOS", amb="viento"),
    E("y unas alas", POINT + [D("mothman", x=540, y=1240, s=1.0)], "push", texto=["ALAS", "ENORMES"], acento=1, amb="viento"),
    M("Fue en Point", [38.84, -82.14], 10, zoom_desde=2, centro_desde=[39, -95], resaltar=["United States of America"], pines=[{"lat": 38.84, "lon": -82.14, "texto": "POINT PLEASANT"}], titulo="NOV. 1966"),
    E("Dos parejas contaron", [D("interior", pared="#3a4a5a", piso="#1a222a", luz_x=540, luz_y=700, cuadros=0), D("persona_real", x=780, y=1720, s=1.5, ropa="uniforme", sombrero="fedora"),
      D("persona_real", x=300, y=1720, s=1.4, ropa="camisa"), D("persona_real", x=470, y=1730, s=1.3, ropa="vestido", peinado="largo")], "push", texto=["FUERON A LA", "POLICÍA"], acento=1),
    E("que una criatura", [C("noche", horizonte=1300), D("arboles", y=1320, n=6, color="#0d140a"), D("suelo", y=1320, colores=["#2a2a2e", "#0d0d10"], tipo="asfalto"),
      D("auto_60", x=300, y=1700, s=1.0, mov="avanza", avance=300), D("mothman", x=200, y=1300, s=.7)], "pan_der", texto=["¡LOS", "PERSIGUIÓ!"], acento=1, sfx="boom", sfx_dur=.6, amb="viento"),
    N("Durante un año", 100, "AVISTAMIENTOS", "DECENAS DE", icono="👁️"),
    E("Los diarios la", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=700), D("periodico", x=540, y=1550, s=1.1, titular="MOTHMAN")], "push", texto="«MOTHMAN»", sfx="papel", sfx_dur=.6),
    E("En diciembre de", [C("noche", horizonte=1100), D("puente", y=1250, colapso=True, en=1.2)], "fijo", texto=["¡EL PUENTE", "COLAPSÓ!"], acento=1, sacudir=True, sfx="crujido", sfx_dur=2.0),
    N("y murieron cuarenta", 46, "PERSONAS", "MURIERON", icono="🕯️"),
    E("Después de eso,", POINT + [D("mothman", x=540, y=1240, s=1.0, mov="desvanece", desvanece_en=1.5)], "pull", texto=["¿VINO A", "ADVERTIR?"], acento=1, amb="viento"),
    FIN("¿Crees en el", ["¿CREES EN EL", "HOMBRE POLILLA?"], final="si_no", capas=POINT + [D("mothman", x=540, y=1240, s=.9)]),
])

# ================================================================ 78 · Diablo de Jersey
PINOS = [C("noche", horizonte=1300), D("arboles", y=1350, n=7, tipo="pino", nieve=True, color="#1e3020"), D("suelo", y=1350, colores=["#e6edf7", "#9aa8bf"], tipo="nieve")]
P[78] = dict(tema="misterio", estilo="terror", claves=["trece…", "diablo».", "huellas", "recompensas"], tomas=[
    E("Según la leyenda,", [D("interior", pared="#4a3a2a", piso="#20160e", luz=False, cuadros=0), D("velas", x=760, y=1500, s=.6, n=2), D("cama", x=420, y=1600, s=1.0)], "push",
      dato=["NUEVA JERSEY", "1735"], amb="viento"),
    T("y nació un", ["EL HIJO", "NÚMERO 13"], acento=1, icono="🌑"),
    E("Cuentan que la", [D("interior", pared="#4a3a2a", piso="#20160e", luz=False, cuadros=0), D("velas", x=760, y=1500, s=.6, n=2), D("persona_real", x=420, y=1760, s=1.8, ropa="vestido", peinado="mono", pelo="#3a2a1e")],
      "push", texto=["«SERÍA EL", "DIABLO»"], acento=1, sfx="boom", sfx_dur=.6),
    E("El bebé se", [D("interior", pared="#1a1410", piso="#0a0806", luz=False, cuadros=0), D("diablo_jersey", x=540, y=1600, s=1.3)], "push_fuerte",
      texto=["ALAS, COLA Y", "PATAS DE CABALLO"], acento=1, amb="viento"),
    E("y escapó volando", PINOS + [D("casa", tipo="madera", x=300, y=1460, s=.7, luces=True), D("diablo_jersey", x=700, y=900, s=.8, vuela=True)], "sube", texto=["POR LA", "CHIMENEA"], acento=1, amb="viento"),
    E("Durante siglos hubo", PINOS + [D("ojos", x=600, y=1300, s=.8, en=1.0, color="#ff3030")], "push", texto=["UNA CRIATURA", "EN LOS BOSQUES"], acento=1, amb="viento"),
    T("Pero lo más", ["ENERO", "1909"], acento=0, icono="❄️"),
    E("en una sola", PINOS + [D("huellas", x=540, y=1600, s=1.0)], "push", texto=["MILES VIERON", "HUELLAS"], acento=1, amb="viento"),
    E("Cerraron escuelas y", [C("dia", horizonte=1350), D("ciudad", era="antigua", y=1380, hora="dia"), D("suelo", y=1380, colores=["#e6edf7", "#9aa8bf"], tipo="nieve"),
      D("cartel", x=540, y=1650, s=.9, titulo="RECOMPENSA", sub="$10.000")], "push", texto=["¡RECOMPENSA!"], amb="viento", amb_vol=.5),
    FIN("¿Qué crees que", ["¿QUÉ CREES", "QUE VIERON?"], capas=PINOS + [D("diablo_jersey", x=540, y=1000, s=.7, vuela=True)], comentario="Un búho 🦉"),
])

# ================================================================ 79 · Hombre de Taured
ADUANA = dict(pared="#8a8a7a", piso="#3a3a32", luz_x=540, luz_y=600, cuadros=0, vista="dia", ventana_x=760)
VIAJERO = dict(ropa="traje_gris", sombrero="fedora", bigote=True)
P[79] = dict(tema="misterio", estilo="retro", claves=["existe.", "Taured.", "Andorra.", "desaparecido…"], tomas=[
    E("Cuenta una leyenda", [C("dia", horizonte=1300), D("avion", x=540, y=900, s=.9, avance=200), D("suelo", y=1300, colores=["#5a5a5e", "#2a2a2e"], tipo="asfalto")], "push",
      dato=["TOKIO", "1954"], amb="viento"),
    T("desde un país", ["UN PAÍS QUE", "NO EXISTE"], acento=1, icono="🌍"),
    E("Según la historia,", [D("interior", **ADUANA), D("pasaporte", x=540, y=1650, s=1.2)], "push", texto="«TAURED»", sfx="papel", sfx_dur=.6),
    E("Decía que estaba", [D("interior", **ADUANA), D("mostrador", x=540, y=1700, s=1.0), D("persona_real", x=330, y=1700, s=1.6, **VIAJERO), D("persona_real", x=780, y=1700, s=1.5, ropa="uniforme", piel="asiatica")],
      "push", texto=["ENTRE FRANCIA", "Y ESPAÑA"], acento=1),
    M("Le mostraron un", [42.5, 1.5], 25, zoom_desde=4, centro_desde=[43, 2], resaltar=["Andorra", "France", "Spain"], pines=[{"lat": 42.5, "lon": 1.5, "texto": "ANDORRA"}]),
    E("Él se enojó:", [D("interior", **ADUANA), D("persona_real", x=540, y=1760, s=2.0, **VIAJERO)], "push_fuerte", texto=["«EXISTE HACE", "MIL AÑOS»"], acento=1),
    E("Lo dejaron en", [D("interior", pared="#6a5a4a", piso="#2a1d14", luz=False, vista="noche", ventana_x=700), D("cama", x=420, y=1600, s=1.0), D("persona_real", x=800, y=1720, s=1.4, ropa="uniforme", piel="asiatica")],
      "push", texto=["EN UN HOTEL,", "VIGILADO"], acento=1),
    E("A la mañana", [D("interior", pared="#6a5a4a", piso="#2a1d14", vista="dia", ventana_x=700), D("cama", x=420, y=1600, s=1.0)], "push", texto=["HABÍA", "DESAPARECIDO"], acento=1, sfx="boom", sfx_dur=.5),
    T("Nunca se ha", ["NINGÚN REGISTRO", "OFICIAL"], acento=1, icono="📁"),
    FIN("¿Viajó de otra", ["¿VINO DE OTRA", "DIMENSIÓN?"], final="si_no", capas=[D("interior", **ADUANA), D("pasaporte", x=540, y=1650, s=1.0)]),
])

# ================================================================ 80 · Slender Man
PARQUE = [C("dia", horizonte=1300), D("arboles", y=1320, n=6)]
P[80] = dict(tema="misterio", estilo="neon", claves=["rostro,", "Photoshop.", "Knudsen,", "internet."], tomas=[
    E("Un hombre altísimo,", PARQUE + [D("slender", x=540, y=1360, s=1.0), D("suelo", y=1320, colores=["#5a7a3a", "#2a3a1a"], tipo="pasto")], "push", texto=["SIN ROSTRO", "Y DE TRAJE"], acento=1, amb="viento"),
    T("Pero nació en", ["NACIÓ EN", "INTERNET"], acento=1, icono="💻"),
    E("En junio de", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("computadora", x=540, y=1550, s=1.2)], "push", dato=["JUNIO", "2009"], amb="zumbido", amb_vol=.3),
    T("crear imágenes paranormales", ["UN CONCURSO DE", "PHOTOSHOP"], acento=1, icono="🖼️"),
    E("Un usuario, Eric", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("computadora", x=540, y=1550, s=1.0), D("persona_real", x=820, y=1720, s=1.5, ropa="sueter")],
      "push", dato=["ERIC", "KNUDSEN"], amb="zumbido", amb_vol=.3),
    E("publicó dos fotos", PARQUE + [D("slender", x=820, y=1350, s=.8, op=.5), D("suelo", y=1320, colores=["#5a7a3a", "#2a3a1a"], tipo="pasto")] +
      [D("persona_real", x=x, y=1720, s=1.0, ropa=r, peinado=pe) for x, r, pe in [(250, "camisa", "corto"), (450, "vestido", "largo"), (620, "overol", "corto")]],
      "push", texto=["¿LA VES AL", "FONDO?"], acento=1, amb="viento"),
    E("Debajo escribió textos", [D("interior", pared="#3a3226", piso="#1a140f", luz_x=540, luz_y=900, cuadros=0), D("carta", x=540, y=1550, s=1.0, texto="Testimonio", firma="1983")],
      "push", texto=["COMO SI FUERAN", "REALES"], acento=1, sfx="papel", sfx_dur=.6),
    E("Otros usuarios empezaron", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("pantalla", tipo="sala", x=540, y=1450, s=1.0)], "pull",
      texto=["HISTORIAS, VIDEOS", "Y JUEGOS"], acento=1),
    E("En pocos años,", PARQUE + [D("niebla", y=1300, op=.6), D("slender", x=540, y=1380, s=1.1), D("suelo", y=1320, colores=["#3a4a2a", "#141a0e"], tipo="pasto")], "push_fuerte",
      texto=["LEYENDA", "MUNDIAL"], acento=1, sfx="boom"),
    FIN("¿Lo conocías? Comenta", ["¿LO", "CONOCÍAS?"], final="si_no", capas=PARQUE + [D("slender", x=760, y=1360, s=.8, op=.6)]),
])

# ================================================================ 82 · Gigante de Cardiff
CARDIFF = [C("dia", horizonte=1300), D("montanas", horizonte=1320, colores=["#7a9a6a", "#5a7a4a", "#3a5a2a"]), D("suelo", y=1300, colores=["#8a7a5a", "#3a3020"], tipo="tierra")]
P[82] = dict(tema="misterio", estilo="periodico", claves=["metros.", "petrificado.", "Hull,", "copia"], tomas=[
    E("En mil ochocientos", CARDIFF + [D("gigante_piedra", x=540, y=1650, s=1.0)] + [D("persona_real", x=x, y=1520, s=.9, ropa="obrero", sombrero="fedora") for x in (200, 880)],
      "push", dato=["1869", "UN GIGANTE"], amb="viento"),
    N("encontraron a un", 3, "METROS", "DE PIEDRA", icono="🗿"),
    E("Fue en una", CARDIFF + [D("casa", tipo="granja", x=540, y=1420, s=.9)], "pull", dato=["CARDIFF", "NUEVA YORK"], amb="insectos", amb_vol=.4),
    E("Miles de personas", CARDIFF + [D("carpa", x=540, y=1500, s=1.0)] + [D("persona_real", x=x, y=1760, s=1.0, ropa=r, sombrero=h) for x, r, h in [(150, "traje", "copa"), (350, "vestido", None), (730, "traje_cafe", "bombin"), (930, "abrigo", "copa")]],
      "pan_der", texto=["PAGABAN POR", "VERLO"], acento=1, amb="multitud"),
    E("y muchos creyeron", [C("dia", horizonte=1300), D("suelo", y=1300, colores=["#8a7a5a", "#3a3020"], tipo="tierra"), D("gigante_piedra", x=540, y=1600, s=1.5)], "push_fuerte",
      texto=["¿UN HOMBRE", "PETRIFICADO?"], acento=1),
    E("En realidad, lo", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("persona_real", x=540, y=1760, s=1.9, ropa="traje", barba=True, sombrero="bombin")], "push",
      dato=["GEORGE HULL", "TABACALERO"]),
    E("después de discutir", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("libro", x=540, y=1550, s=.8),
      D("persona_real", x=260, y=1720, s=1.5, ropa="traje", barba=True), D("persona_real", x=820, y=1720, s=1.5, ropa="puritano", pelo="#d9d9d9")], "push", texto=["¿GIGANTES DE", "LA BIBLIA?"], acento=1),
    E("Lo esculpieron en", [D("interior", pared="#4a4a44", piso="#22221e", luz_x=540, luz_y=700, cuadros=0), D("gigante_piedra", x=540, y=1650, s=1.1), D("frasco", x=900, y=1650, s=.7, contenido="liquido", color_liquido="#c9e86a")],
      "push", texto=["YESO Y", "ÁCIDO"], acento=1),
    E("Lo más loco:", [C("dia", horizonte=1300), D("carpa", x=320, y=1500, s=.8), D("carpa", x=780, y=1500, s=.8), D("suelo", y=1300, colores=["#8a7a5a", "#3a3020"], tipo="tierra"),
      D("cartel", x=540, y=1700, s=.8, titulo="¡EL GIGANTE!", sub="P. T. BARNUM")], "pull", texto=["¡UNA COPIA", "DE LA COPIA!"], acento=1, amb="multitud"),
    FIN("¿Tú habrías pagado", ["¿HABRÍAS PAGADO", "POR VERLO?"], final="si_no", capas=CARDIFF + [D("gigante_piedra", x=540, y=1650, s=1.0)]),
])

# ================================================================ 83 · Círculos en los cultivos
CAMPO_UK = [C("noche", horizonte=1150), D("trigal", y=1150, noche=True)]
DOUG = dict(ropa="abrigo", sombrero="gorra", pelo="#d9d9d9", bigote=True)
P[83] = dict(tema="misterio", estilo="neon", claves=["extraterrestres.", "huellas", "confesaron:", "auténtico»."], tomas=[
    E("Durante años, aparecieron", [C("dia", horizonte=1150), D("trigal", y=1150)], "baja", texto=["FIGURAS", "PERFECTAS"], acento=1, amb="viento"),
    E("Muchos creyeron que", CAMPO_UK + [D("luz", x=540, y=500, r=300, color="#8dff9c", op=.4, parpadeo=True)], "push", texto=["¿MENSAJES", "EXTRATERRESTRES?"], acento=1, amb="zumbido", amb_vol=.4),
    E("Eran círculos enormes,", [C("dia", horizonte=1150), D("trigal", y=1150)], "push", texto=["SIN HUELLAS", "ALREDEDOR"], acento=1, amb="viento"),
    E("Llegaron científicos, curiosos", [C("dia", horizonte=1150), D("trigal", y=1150)] + [D("persona_real", x=x, y=1800, s=1.0, ropa=r, **k) for x, r, k in [(150, "bata", {"lentes": True}), (380, "camisa", {}), (680, "abrigo", {}), (900, "traje", {"sombrero": "fedora"})]],
      "pan_der", texto=["CAZADORES", "DE OVNIS"], acento=1, amb="multitud", amb_vol=.4),
    E("En mil novecientos", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=700), D("persona_real", x=330, y=1740, s=1.6, **DOUG), D("persona_real", x=760, y=1740, s=1.6, ropa="sueter", pelo="#bfbfbf", peinado="calvo")],
      "push", dato=["DOUG Y DAVE", "1991"]),
    T("los hacían ellos", ["¡ERAN ELLOS!", "DESDE 1976"], acento=0, entrada="flash", sfx="boom"),
    E("Usaban una tabla", CAMPO_UK + [D("persona_real", x=400, y=1750, s=1.4, **DOUG, mov="camina", avance=150), D("caja", x=520, y=1780, s=.4)], "pan_der",
      texto=["TABLA, CUERDA", "Y UNA GORRA"], acento=1, amb="viento"),
    E("Lo demostraron frente", [C("dia", horizonte=1150), D("trigal", y=1150), D("microfono", x=820, y=1800, s=.8), D("persona_real", x=330, y=1800, s=1.3, ropa="traje", lentes=True)], "push",
      texto=["«ES", "AUTÉNTICO»"], acento=1, sfx="ping", sfx_dur=.4),
    E("Hoy hay artistas", CAMPO_UK, "baja", texto=["EN UNA", "SOLA NOCHE"], acento=1, amb="viento"),
    FIN("¿Tú creías que", ["¿CREÍAS QUE", "ERAN OVNIS?"], final="si_no", capas=CAMPO_UK),
])

# ================================================================ 86 · Nintendo desde 1889
KIOTO = [C("atardecer", horizonte=1300), D("pueblo_jp", y=1330), D("suelo", y=1330, colores=["#8a7a62", "#3a3024"], tipo="tierra")]
TALLER = dict(pared="#8a6a4a", piso="#4a3420", luz_x=540, luz_y=700, pared_estilo="liso", cuadros=0)
P[86] = dict(tema="ciencia", estilo="pop", claves=["cine.", "hanafuda.", "quiebra.", "Boy."], tomas=[
    E("Nintendo es más", [D("interior", **TALLER), D("farol", x=200, y=800), D("mesa", x=540, y=1650, s=1.2), D("naipes", x=540, y=1450, s=.9)], "push",
      texto=["MÁS ANTIGUA QUE", "EL CINE"], acento=1),
    M("Fue fundada en", [35.01, 135.77], 12, zoom_desde=2, centro_desde=[36, 138], resaltar=["Japan"], pines=[{"lat": 35.01, "lon": 135.77, "texto": "KIOTO"}], titulo="1889"),
    E("por Fusajiro Yamauchi.", KIOTO + [D("farol", x=880, y=900), D("persona_real", x=540, y=1760, s=1.8, ropa="kimono", piel="asiatica", bigote=True, pelo="#2a2a2a")], "push",
      dato=["FUSAJIRO", "YAMAUCHI"], amb="viento", amb_vol=.4),
    E("No hacía videojuegos:", [D("interior", **TALLER), D("farol", x=880, y=800), D("mesa", x=540, y=1650, s=1.3), D("naipes", x=420, y=1450, s=.8),
      D("persona_real", x=760, y=1700, s=1.3, ropa="kimono", piel="asiatica", peinado="calvo")], "push", texto=["NAIPES", "HANAFUDA"], acento=1),
    E("En los años", [C("dia", horizonte=1300), D("ciudad", era="moderna", y=1330, hora="dia"), D("suelo", y=1330, colores=["#5a5a5e", "#2a2a2e"], tipo="asfalto"),
      D("auto_60", x=330, y=1700, s=.9, color="#e0b020")], "pan_der", texto=["TAXIS, ARROZ", "Y HOTELES"], acento=1, amb="multitud", amb_vol=.3),
    E("Casi todos fracasaron,", [D("interior", pared="#3a3a3e", piso="#1a1a1e", luz=False, cuadros=0), D("caja", x=540, y=1600, s=1.2)], "push", texto=["CERCA DE LA", "QUIEBRA"], acento=1),
    E("Entonces empezó a", [D("interior", pared="#2a1a3a", piso="#100a18", luz=False, cuadros=0), D("arcade", x=330, y=1750, s=1.0), D("arcade", x=760, y=1750, s=1.0)], "pull",
      texto=["JUGUETES Y", "ARCADES"], acento=1, amb="zumbido", amb_vol=.4),
    E("Un ingeniero de", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz_x=540, luz_y=700, cuadros=0), D("mesa", x=540, y=1650, s=1.2), D("persona_real", x=780, y=1720, s=1.6, ropa="bata", piel="asiatica", lentes=True)],
      "push", dato=["GUNPEI", "YOKOI"]),
    E("Fue un éxito,", [D("interior", pared="#2a2a3a", piso="#121218", luz_x=540, luz_y=900, cuadros=0), D("mando", x=540, y=1450, s=1.4)], "push_fuerte", texto=["CREÓ LA", "GAME BOY"], acento=1, sfx="ping", sfx_dur=.5),
    FIN("¿Cuál fue tu", ["¿TU PRIMERA", "CONSOLA?"], capas=[D("interior", **TALLER), D("naipes", x=540, y=1500, s=1.0)], comentario="La Game Boy 🎮"),
])

# ================================================================ 89 · Tetris soviético
OFI_MOSCU = dict(pared="#5a6a5a", piso="#2a322a", luz_x=540, luz_y=600, cuadros=0, vista="nieve", ventana_x=780)
ALEKSEI = dict(ropa="sueter", bigote=True, pelo="#3a2a1e", lentes=True)
P[89] = dict(tema="ciencia", estilo="frio", claves=["dinero", "Moscú.", "disquetes", "noventa"], tomas=[
    E("Uno de los", [D("interior", **OFI_MOSCU), D("tetris", x=540, y=1600, s=1.2)], "push", texto=["CREADO EN LA", "UNIÓN SOVIÉTICA"], acento=1, amb="zumbido", amb_vol=.3),
    T("y su creador", ["SU CREADOR", "NO COBRÓ"], acento=1, icono="🚫"),
    E("En mil novecientos", [C("niebla", horizonte=1350), D("ciudad", era="sovietica", y=1380, hora="dia"), D("suelo", y=1380, colores=["#e6edf7", "#9aa8bf"], tipo="nieve"), D("particulas", tipo="nieve", n=50)],
      "push", dato=["MOSCÚ", "1984"], amb="viento"),
    E("Alekséi Pázhitnov trabajaba", [D("interior", **OFI_MOSCU), D("tetris", x=700, y=1600, s=.9), D("persona_real", x=280, y=1720, s=1.6, **ALEKSEI)], "push", dato=["ALEKSÉI", "PÁZHITNOV"], amb="zumbido", amb_vol=.3),
    E("En su tiempo", [D("interior", pared="#0a1a0c", piso="#050a06", luz=False, cuadros=0), D("tetris", x=540, y=1650, s=1.5)], "push_fuerte", texto=["PIEZAS QUE", "CAÍAN"], acento=1),
    E("inspirado en un", [D("interior", pared="#5a4a3c", piso="#2a1d14", luz_x=540, luz_y=900, cuadros=0), D("mesa", x=540, y=1650, s=1.2), D("bloques", x=540, y=1450, s=.8)], "push",
      texto=["UN ROMPECABEZAS", "DE NIÑO"], acento=1),
    E("Se volvió adictivo", [D("interior", **OFI_MOSCU), D("disquete", x=330, y=1600, s=.8), D("disquete", x=560, y=1640, s=.7), D("disquete", x=780, y=1600, s=.8)], "pan_der",
      texto=["COPIAS EN", "DISQUETES"], acento=1),
    E("Pero en la", [C("niebla", horizonte=1350), D("ciudad", era="sovietica", y=1380), D("bandera", x=540, y=1500, s=1.2, colores=["#c8102e"])], "push", texto=["ERA DEL", "ESTADO"], acento=1, amb="viento"),
    E("Empresas de varios", [D("interior", pared="#3a3a4a", piso="#1a1a24", luz_x=540, luz_y=700, pared_estilo="boiserie"), D("mesa", x=540, y=1650, s=1.4)] +
      [D("persona_real", x=x, y=1550, s=1.0, ropa="traje", **k) for x, k in [(250, {"bigote": True}), (540, {"lentes": True}), (830, {"peinado": "calvo"})]], "push", texto=["PELEARON LOS", "DERECHOS"], acento=1),
    N("Pázhitnov recién empezó", 12, "AÑOS", "DESPUÉS COBRÓ", icono="⏳"),
    FIN("¿Eres bueno en", ["¿ERES BUENO", "EN TETRIS?"], final="si_no", capas=[D("interior", **OFI_MOSCU), D("tetris", x=540, y=1600, s=1.1)]),
])

# ================================================================ 90 · Tennis for Two
LAB58 = dict(pared="#6a7a7a", piso="#2a3232", luz_x=540, luz_y=600, cuadros=0)
WILLY = dict(ropa="traje_gris", lentes=True, peinado="calvo", bigote=True)
P[90] = dict(tema="ciencia", estilo="retro", claves=["laboratorio…", "aburridas.", "osciloscopio,", "patentó:"], tomas=[
    E("Uno de los", [D("interior", **LAB58), D("osciloscopio", x=540, y=1700, s=1.3)], "push", texto=["EN UNA PANTALLA", "DE LABORATORIO"], acento=1, amb="zumbido", amb_vol=.4),
    T("en mil novecientos", ["1958"], icono="🎾"),
    E("El físico William", [D("interior", **LAB58), D("persona_real", x=540, y=1760, s=1.9, **WILLY)], "push", dato=["WILLIAM", "HIGINBOTHAM"]),
    M("trabajaba en el", [40.87, -72.87], 20, zoom_desde=2, centro_desde=[40, -95], resaltar=["United States of America"], pines=[{"lat": 40.87, "lon": -72.87, "texto": "BROOKHAVEN"}]),
    E("Cada año abrían", [D("interior", **LAB58), D("mesa", x=540, y=1650, s=1.3), D("frasco", x=400, y=1430, s=.5)] + [D("persona_real", x=x, y=1800, s=1.0, ropa=r) for x, r in [(200, "abrigo"), (880, "vestido")]],
      "pan_der", texto=["EXHIBICIONES", "ABURRIDAS"], acento=1, amb="multitud", amb_vol=.2),
    E("Así que conectó", [D("interior", pared="#1d2620", piso="#0d120e", luz=False, cuadros=0), D("osciloscopio", x=540, y=1700, s=1.6)], "push_fuerte", texto="UN OSCILOSCOPIO", amb="zumbido", amb_vol=.5),
    E("Creó «Tennis for", [D("interior", pared="#1d2620", piso="#0d120e", luz=False, cuadros=0), D("osciloscopio", x=540, y=1600, s=1.3)], "push", texto=["«TENNIS", "FOR TWO»"], acento=1, sfx="pop", sfx_dur=.4),
    E("Los visitantes hicieron", [D("interior", **LAB58), D("osciloscopio", x=800, y=1650, s=.7)] + [D("persona_real", x=x, y=1780 - k * 20, s=1.1 - k * .1, ropa=r) for k, (x, r) in enumerate([(560, "camisa"), (400, "vestido"), (260, "traje"), (130, "abrigo")])],
      "pull", texto=["LARGAS", "FILAS"], acento=1, amb="multitud", amb_vol=.5),
    E("Pero Higinbotham nunca", [D("interior", **LAB58), D("persona_real", x=540, y=1760, s=1.8, **WILLY), D("carta", x=850, y=1600, s=.6, texto="Patente", firma="—")], "push",
      texto=["NUNCA LO", "PATENTÓ"], acento=1),
    FIN("¿Cuál es el", ["¿EL JUEGO MÁS", "ANTIGUO?"], capas=[D("interior", **LAB58), D("osciloscopio", x=540, y=1700, s=1.2)], comentario="El Pong 🏓"),
])

# ================================================================ 91 · Primer easter egg
LIVING = dict(pared="#a8845a", piso="#5a3a22", luz_x=540, luz_y=700, pared_estilo="rombos")
WARREN = dict(ropa="camisa", bigote=True, pelo="#5a3a1e", lentes=True)
P[91] = dict(tema="ciencia", estilo="neon", claves=["creadores.", "injusto.", "píxel", "Pascua»:"], tomas=[
    E("Los secretos escondidos", [D("interior", **LIVING), D("tv_tubo", x=540, y=1650, s=1.2, color="#3a2a6a"), D("pixeles", x=540, y=1350, s=.6)], "push", texto=["SECRETOS EN", "LOS JUEGOS"], acento=1),
    E("A fines de", [D("interior", pared="#3a3a4a", piso="#1a1a24", luz_x=540, luz_y=700, cuadros=0)] + [D("persona_real", x=x, y=1760, s=1.2, ropa=r, bigote=b) for x, r, b in [(200, "camisa", True), (540, "sueter", False), (880, "camisa", True)]],
      "pan_der", texto=["SIN NOMBRES", "DE SUS CREADORES"], acento=1),
    E("Warren Robinett, creador", [D("interior", pared="#3a3a4a", piso="#1a1a24", luz_x=540, luz_y=700, cuadros=0), D("computadora", x=760, y=1600, s=.8), D("persona_real", x=330, y=1760, s=1.8, **WARREN)],
      "push", dato=["WARREN", "ROBINETT"]),
    T("pensó que era", ["¡INJUSTO!"], entrada="flash"),
    E("Así que escondió", [D("interior", pared="#0d0d14", piso="#06060a", luz=False, cuadros=0), D("pixeles", x=540, y=1350, s=1.2), D("luz", x=540, y=1300, r=300, color="#b47aff", op=.4)],
      "push", texto=["UNA HABITACIÓN", "SECRETA"], acento=1, sfx="ping", sfx_dur=.4),
    E("Para llegar, había", [D("interior", pared="#0d0d14", piso="#06060a", luz=False, cuadros=0), D("texto_svg", x=540, y=1300, texto="·", tam=200, color="#9a9a9a", borde=0)], "push_fuerte",
      texto=["UN SOLO", "PÍXEL"], acento=1),
    E("Ahí aparecía el", [D("interior", **LIVING), D("tv_tubo", x=540, y=1650, s=1.3, color="#6a2a8a"), D("texto_svg", x=470, y=1450, texto="CREATED BY", tam=40, color="#fff", borde=0),
      D("texto_svg", x=470, y=1510, texto="ROBINETT", tam=50, color="#ffd36a", borde=0)], "push", texto=["«CREADO POR WARREN", "ROBINETT»"], acento=1),
    E("Un adolescente lo", [D("interior", **LIVING), D("tv_tubo", x=700, y=1650, s=1.0, color="#3a2a6a"), D("mando", x=380, y=1700, s=.6), D("persona_real", x=330, y=1780, s=1.3, ropa="overol")],
      "push", texto=["UN ADOLESCENTE", "LO DESCUBRIÓ"], acento=1),
    E("En vez de", [D("interior", pared="#2a2a3a", piso="#121218", luz_x=540, luz_y=900, cuadros=0), D("texto_svg", x=540, y=1300, texto="🥚", tam=10, color="#000")], "push",
      texto=["«HUEVO DE", "PASCUA»"], acento=1),
    FIN("¿Cuál es tu", ["¿TU EASTER EGG", "FAVORITO?"], capas=[D("interior", **LIVING), D("tv_tubo", x=540, y=1650, s=1.2, color="#3a2a6a")], comentario="El de Minecraft 🥚"),
])

# ================================================================ 92 · Episodio de Pokémon
SALA_JP = dict(pared="#c8b89a", piso="#7a6a4a", luz=False, cuadros=0, pared_estilo="liso", vista="noche", ventana_x=820)
NINO_JP = dict(ropa="camisa", piel="asiatica", peinado="corto", pelo="#111")
P[92] = dict(tema="ciencia", estilo="pop", claves=["hospital…", "destellos", "convulsiones.", "reglas"], tomas=[
    F("El dieciséis de", "16", "DICIEMBRE", "1997"),
    E("cientos de niños", [D("interior", **SALA_JP), D("tv_tubo", x=760, y=1650, s=1.0, color="#3a5a8a"), D("persona_real", x=300, y=1800, s=1.3, **NINO_JP, mira="der")], "push",
      texto=["NIÑOS AL", "HOSPITAL"], acento=1),
    E("Era un capítulo", [D("interior", **SALA_JP), D("tv_tubo", x=540, y=1650, s=1.5, color="#3a5a8a")], "push", texto=["UN DIBUJO", "ANIMADO"], acento=1),
    E("En una escena,", [D("interior", **SALA_JP), D("tv_tubo", x=540, y=1650, s=1.5, destellos=True, en=.3)], "fijo", texto=["DESTELLOS ROJOS", "Y AZULES"], acento=1, sfx="pop", sfx_dur=.3),
    N("durante unos cinco", 5, "SEGUNDOS", "DURANTE", icono="⚡"),
    E("Muchos niños sintieron", [D("interior", **SALA_JP), D("tv_tubo", x=760, y=1650, s=.9, destellos=True, en=.1), D("persona_real", x=330, y=1780, s=1.6, **NINO_JP)], "push",
      texto=["MAREOS Y", "NÁUSEAS"], acento=1, sacudir=True),
    N("Unos seiscientos ochenta", 685, "NIÑOS", "AL HOSPITAL", icono="🚑"),
    E("Algunos sufrieron convulsiones.", [C("noche", horizonte=1350), D("ciudad", era="moderna", y=1380, hora="noche"), D("sirenas_policia", y=1500)], "push", texto="CONVULSIONES", amb="viento", amb_vol=.4),
    E("La serie dejó", [D("interior", **SALA_JP), D("tv_tubo", x=540, y=1650, s=1.4, color="#111")], "push", texto=["4 MESES", "FUERA DEL AIRE"], acento=1),
    E("Desde entonces, en", [D("interior", pared="#3a3a4a", piso="#1a1a24", luz_x=540, luz_y=700, cuadros=0), D("carta", x=540, y=1550, s=1.0, texto="Reglas de TV", firma="")], "push",
      texto=["REGLAS PARA", "LAS LUCES"], acento=1, sfx="papel", sfx_dur=.6),
    FIN("¿Lo sabías? Comenta", ["¿LO", "SABÍAS?"], final="si_no", capas=[D("interior", **SALA_JP), D("tv_tubo", x=540, y=1650, s=1.3, color="#3a5a8a")]),
])

# ================================================================ 93 · Epidemia de World of Warcraft
FANTASIA = [C("atardecer", horizonte=1300), D("castillo", x=540, y=1380, s=.9), D("ciudad", era="antigua", y=1400, hora="atardecer", semilla=8), D("suelo", y=1400, colores=["#8a7a62", "#3a3024"], tipo="adoquin")]
HEROE = [dict(ropa="tunica", barba=True, pelo="#6a4a2a"), dict(ropa="tunica_roja", peinado="largo", pelo="#c09a5a"), dict(ropa="obrero", sombrero="casco_ww"), dict(ropa="kimono", peinado="mono")]
P[93] = dict(tema="ciencia", estilo="neon", claves=["epidemia", "corrupta»,", "mascotas", "epidemiólogos"], tomas=[
    E("En dos mil", FANTASIA + [D("particulas", tipo="roja", n=40)], "push", dato=["2005", "UNA EPIDEMIA"], amb="viento"),
    T("y los científicos", ["¡LA ESTUDIARON", "CIENTÍFICOS!"], acento=1, icono="🔬"),
    E("En el videojuego", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("computadora", x=540, y=1550, s=1.2)], "push", texto=["UN JUEGO", "EN LÍNEA"], acento=1, amb="zumbido", amb_vol=.3),
    E("un jefe lanzaba", [C("rojo", horizonte=1300), D("castillo", x=540, y=1380, s=1.0), D("suelo", y=1380, colores=["#3a2a2a", "#140a0a"]), D("luz", x=540, y=1200, r=500, color="#c1121f", op=.4),
      D("particulas", tipo="roja", n=60)], "push_fuerte", texto=["«SANGRE", "CORRUPTA»"], acento=1, sfx="boom"),
    E("Pero un error", FANTASIA + [D("perro", raza="laika", x=540, y=1720, s=1.0), D("luz", x=540, y=1600, r=200, color="#ff3b3b", op=.5)], "push", texto=["LAS MASCOTAS", "LA LLEVARON"], acento=1),
    E("Se contagió de", FANTASIA + [D("persona_real", x=x, y=1760, s=1.0, **h) for x, h in zip((180, 400, 660, 900), HEROE)] + [D("particulas", tipo="roja", n=70)], "pan_der",
      texto=["MILES", "MURIERON"], acento=1, amb="multitud", amb_vol=.5),
    E("Algunos ayudaban a", FANTASIA + [D("persona_real", x=300, y=1760, s=1.4, **HEROE[0]), D("luz", x=300, y=1500, r=200, color="#8dff9c", op=.5),
      D("persona_real", x=800, y=1760, s=1.3, **HEROE[1], mov="camina", avance=200)], "push", texto=["CURAR O", "HUIR"], acento=1),
    E("y algunos la", FANTASIA + [D("persona_real", x=540, y=1760, s=1.8, **HEROE[2]), D("particulas", tipo="roja", n=80)], "push_fuerte", texto=["¡A", "PROPÓSITO!"], acento=1),
    E("Los desarrolladores tuvieron", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("pantalla", tipo="sala", x=540, y=1450, s=1.0, alarma=True)], "push", texto=["REINICIAR LOS", "SERVIDORES"], acento=1),
    E("Y años después,", [D("interior", pared="#dfe8e6", piso="#9aa8a6", luz_x=540, luz_y=700, cuadros=0), D("libro", x=380, y=1600, s=.8), D("persona_real", x=780, y=1720, s=1.6, ropa="bata", lentes=True, peinado="mono")],
      "push", texto=["¿CÓMO REACCIONA", "LA GENTE?"], acento=1),
    FIN("¿Tú habrías ayudado", ["¿AYUDAR", "O HUIR?"], capas=FANTASIA, comentario="Yo huía 🏃"),
])

# ================================================================ 94 · Polybius
SALON_ARC = dict(pared="#1a0d24", piso="#0a0610", luz=False, cuadros=0)
MIB = dict(ropa="traje", sombrero="fedora", lentes=True)
P[94] = dict(tema="misterio", estilo="neon", claves=["pesadillas…", "Polybius", "negro", "rastro."], tomas=[
    E("Dicen que en", [D("interior", **SALON_ARC), D("polybius", x=540, y=1750, s=1.4)], "push", texto=["CAUSABA", "PESADILLAS"], acento=1, amb="zumbido", amb_vol=.5),
    M("Según la leyenda,", [45.52, -122.68], 12, zoom_desde=2, centro_desde=[40, -100], resaltar=["United States of America"], pines=[{"lat": 45.52, "lon": -122.68, "texto": "PORTLAND"}], titulo="1981"),
    E("Los jugadores se", [D("interior", **SALON_ARC), D("polybius", x=700, y=1750, s=1.1), D("persona_real", x=330, y=1780, s=1.5, ropa="overol", mira="der")], "push", texto=["SE VOLVÍAN", "ADICTOS"], acento=1, amb="zumbido", amb_vol=.5),
    E("Algunos habrían sufrido", [D("interior", pared="#1d1a24", piso="#0d0a12", luz=False, cuadros=0, vista="noche", ventana_x=760), D("cama", x=420, y=1600, s=1.0), D("notas", distorsion=True, n=5)],
      "push", texto=["INSOMNIO Y", "ALUCINACIONES"], acento=1, amb="viento"),
    E("Y cada cierto", [D("interior", **SALON_ARC), D("polybius", x=540, y=1750, s=1.0), D("persona_real", x=230, y=1780, s=1.5, **MIB), D("persona_real", x=850, y=1780, s=1.5, **MIB)], "push",
      texto=["HOMBRES DE", "NEGRO"], acento=1),
    E("y anotaban datos.", [D("interior", **SALON_ARC), D("persona_real", x=540, y=1780, s=2.0, **MIB), D("libro", x=700, y=1450, s=.4)], "push_fuerte", texto=["ANOTABAN", "DATOS"], acento=1, sfx="papel", sfx_dur=.6),
    E("Semanas después, las", [D("interior", **SALON_ARC), D("polybius", x=540, y=1750, s=1.2, mov="desvanece", desvanece_en=1.0)], "push", texto=["DESAPARECIERON", "SIN RASTRO"], acento=1),
    T("Nunca se ha", ["NI UNA", "PRUEBA"], acento=1, icono="❓"),
    E("Pero la leyenda", [D("interior", **SALON_ARC), D("polybius", x=330, y=1750, s=1.0), D("arcade", x=760, y=1750, s=1.0)], "pull", texto=["JUEGOS, SERIES", "Y RÉPLICAS"], acento=1, amb="zumbido", amb_vol=.4),
    FIN("¿Crees que existió?", ["¿CREES QUE", "EXISTIÓ?"], final="si_no", capas=[D("interior", **SALON_ARC), D("polybius", x=540, y=1750, s=1.2)]),
])

# ================================================================ 95 · Pueblo Lavanda
P[95] = dict(tema="misterio", estilo="terror", claves=["niños.", "agudas", "inventado.", "fantasmas."], tomas=[
    E("Una de las", [D("torre_lapidas"), D("notas", distorsion=True, n=6)], "push", texto=["¿UNA MÚSICA", "MALDITA?"], acento=1, amb="viento", amb_vol=.4),
    E("En dos mil", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("computadora", x=540, y=1550, s=1.2)], "push", dato=["2010", "UNA HISTORIA"], amb="zumbido", amb_vol=.3),
    E("que en mil", [D("torre_lapidas")], "baja", texto=["PUEBLO", "LAVANDA"], acento=1),
    E("tenía frecuencias tan", [D("torre_lapidas"), D("notas", distorsion=True, n=9), D("silbido", x1=200, y1=900, x2=900, color="#b47aff")], "push_fuerte",
      texto=["SOLO LOS NIÑOS", "LAS OÍAN"], acento=1),
    E("Según el relato,", [D("interior", pared="#c8b89a", piso="#7a6a4a", luz=False, cuadros=0, pared_estilo="liso"), D("tv_tubo", x=700, y=1650, s=.9, color="#6a3a8a"),
      D("persona_real", x=330, y=1780, s=1.5, ropa="camisa", piel="asiatica", pelo="#111")], "push", texto=["DOLOR DE CABEZA", "Y MIEDO"], acento=1),
    T("Todo era inventado.", ["TODO ERA", "INVENTADO"], acento=1, entrada="flash", sfx="boom"),
    E("Fue una creepypasta,", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("computadora", x=540, y=1550, s=1.1), D("luz", x=540, y=1300, r=300, color="#b47aff", op=.35)],
      "push", texto="«CREEPYPASTA»", amb="zumbido", amb_vol=.3),
    E("Pero se volvió", [D("interior", pared="#2a2a3a", piso="#121218", luz=False, cuadros=0), D("pantalla", tipo="sala", x=540, y=1450, s=1.0)], "pull", texto=["MUCHOS AÚN", "LA CREEN"], acento=1),
    E("Lo cierto: la", [D("torre_lapidas"), D("notas", distorsion=True, n=5), D("ojos", x=540, y=900, s=.6, en=1.0, color="#dfe8ff")], "push", texto=["EL PUEBLO DE", "LOS FANTASMAS"], acento=1, amb="viento"),
    FIN("¿Tú la creías?", ["¿TÚ LA", "CREÍAS?"], final="si_no", capas=[D("torre_lapidas")]),
])


def escribir():
    PLANES.mkdir(exist_ok=True)
    for n, plan in P.items():
        (PLANES / f"relato_{n:03d}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(P), "planes")


if __name__ == "__main__":
    escribir()
