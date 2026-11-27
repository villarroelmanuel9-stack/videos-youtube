# Aprendizajes del canal "Pasó de Verdad"

Notas que se aplican a cada video nuevo (se actualizan después de cada historia).

## Producción
- **Probar cada escena en fotogramas sueltos ANTES de generar el video completo** (ahorra re-renders de 10 min).
- Todo texto/recuadro debe **ajustar su ancho automáticamente** (error de la tarjeta cortada en Dinosaurios).
- Sincronizar efectos y recuadros con **la palabra exacta** de la voz (reconocimiento de voz), no con porcentajes.
- Los objetos deben **parecer lo que son**: revisar siluetas (los chalecos de Alcatraz parecían panes).
- Barridos de cámara entre escenas + destellos/sacudidas en momentos fuertes = más dinamismo.
- Fondos en capas (parallax) y primer plano dan profundidad.

- Guardar el reconocimiento de voz en caché (`*.palabras.json`) para previsualizar con los tiempos reales.
- Motor común `pro.py` + personajes `humanos.py`: cada historia solo define sus escenas.
- Revisar símbolos culturales (la estrella de Chile salió como pentágono la primera vez).
- Textos formados con objetos (velas → "PAZ") necesitan un refuerzo visual para leerse.

## Calidad de dibujo (desde Wojtek)
- `realista.LienzoReal`: sombreado degradado, contornos finos del color del objeto, textura suave y `pelaje()`.
- `Humano(realista=True, cabeza=0.86)`: personajes con proporciones algo más reales.
- `pro.generar(..., acabado=True)`: curva de color, bloom en las luces y grano fino en cada fotograma.
- Ojo con el grano: con mucho grano el video pesó 111 MB. Grano suave (1.6) que cambia cada 2 fotogramas y
  entregar comprimido (crf 25) → archivos de ~20-30 MB.

## Audio (corregido tras el aviso del usuario: los efectos tapaban la voz)
- **La voz siempre va en una pista aparte** y se mezcla al final con `mezcla_audio.mezcla_final()`; todos los motores
  (cine, caricatura, dinos, alcatraz, pro) pasan por ahí.
- La voz se normaliza a ≈ -18 dBFS; los efectos se limitan a -10 dBFS y bajan ~10 dB mientras se habla (ducking).
- Nunca normalizar todo junto por el pico: un golpe fuerte bajaba también la voz.
- Cada video imprime un informe: **margen voz/efectos entre 15 y 30 dB**. Si sale "⚠ EFECTOS DEMASIADO ALTOS", no se entrega.
- Para arreglar videos ya hechos sin redibujar: `python remezclar.py N`.
- Desde Wojtek: `pro.generar(..., hifi=True)` → efectos con reverberación, paneo estéreo, ambientes envolventes y
  sonidos nuevos (gruñido, camión, bocina de barco, artillería, ducha, botella, pasos, multitud). La voz no se toca.

## Retención
- Gancho en el primer segundo con un dato que choque + imagen fuerte.
- "Loop abierto" temprano ("y eso no es lo más loco…").
- Cambio visual cada 3–5 s; algún momento sorpresa visual a mitad del video.
- Final con una acción concreta para comentar (palabra o SÍ/NO) y pedir suscripción.

## Identidad: cada video debe ser distinto
| Video | Paleta | Recuadros | Palabra activa | Final |
|---|---|---|---|---|
| Dinosaurios | Cálida, día | Tarjetas blancas con emoji | Amarillo | Botón SUSCRIBIRSE con clic + "Comenta «dino»" |
| Alcatraz | Fría, noche | Fichas de expediente + sellos | Celeste | Reja + carteles SE BUSCA + "CASO ABIERTO" + SÍ/NO |
| D. B. Cooper | Retro años 70 (naranja/verde azulado) | Pases de abordar | Naranja | Tablero de detective + comentario escribiéndose + avioneta con cartel |
| 33 mineros | Industrial, roca | Placas metálicas con franja de peligro + contador DÍA N | Caja amarilla | Bandera de Chile + "33" + pin "¿Dónde estabas?" + placa con lámpara |
| Andes | Nieve, tonos fríos | Notas de cuaderno manuscritas | Coral | Página de diario con casillas + lápiz que escribe "suscríbete" |
| Juliane Koepcke | Selva, lluvia, recuerdo en sepia | Libreta de campo | Verde lima | Mapa con la ruta dibujándose + brote que crece con "SUSCRÍBETE" |
| Tregua de Navidad | Noche nevada, velas | Tarjetas navideñas antiguas | Cinta roja | Velas que escriben "PAZ" + regalo que se abre |
| Wojtek (oso soldado) | Semi-realista: desierto, puerto, Montecassino, Escocia | Libretas militares verde oliva con bandera polaca | Subrayado rojo | Estatua de bronce + huellas + sello de huella "SUSCRÍBETE" |
| Misterios sin resolver (serie, 96 videos) | Nocturna/niebla según tema + acabado de cine | Fichas de expediente + sellos (SIN RESOLVER / MITO / ¿RESUELTO?) | Ámbar | 4 finales que rotan (CASO ABIERTO, comentario escribiéndose, signos «?», logo de la serie) + franja SUSCRÍBETE |

## Serie de misterios (lote automático)
- **Verificar siempre los audios por contenido, no por nombre**: de 98 archivos, 2 eran copias exactas de otros
  (Roanoke = Flannan, Baychimo = Flying Tiger). `verificar_misterios.py` transcribe, identifica y deja el informe en
  `guiones/verificacion_misterios.md`.
- Cobertura 77–85 % con similitud > 0,83 = audio correcto (ElevenLabs cambia números y algunas palabras); revisar solo
  si la similitud baja de 0,8 o falta el final.
- El tema visual se asigna a mano por número (`TEMA_N`): las palabras clave sueltas confunden («mina» en «termina»).
- Glifos raros: usar DejaVu (la fuente de máquina no los tiene y salen cuadrados).
- Lo que se vea en el primer segundo tiene que estar en pantalla desde el fotograma 1 (el avión entraba tarde).
- Render: ~3 min por video de 25–30 s con acabado; 3 en paralelo con 4 núcleos. Peso ~6 MB (crf 25).
- **Basarse en lo real** (pedido del usuario): cada misterio tiene su ficha en `mis_kits.DETALLES` con el modelo y
  color reales del vehículo (Avenger azul marino en formación de 5, Boeing 777 con franjas roja y azul, Lancastrian
  sobre los Andes, goleta de 5 palos con el faro en espiral de Hatteras…), la época de la ropa (parka roja de Paula
  Welden, fedora de los años 40), el lugar (desierto, fondo marino, estación de tren, casa en llamas) y el objeto
  histórico (impresión «6EQUJ5», disco de Festo, diamante Hope). Sprites en `mis_reales.py`.
- El vehículo o el objeto real **abre** el video; dos videos del mismo tema nunca repiten el orden de escenas.
- Sonido por escena (no un ambiente fijo para todo el video): sonar, morse, crujido de madera, gaviotas, bocina de
  niebla, goteo, papel, búho, fuego, tren, burbujas… siempre por debajo de la voz (informe de mezcla «OK»).
- **v3 (pedido: «ninguno igual», «solo información de la historia»)**: los datos en pantalla salen de lo que el
  narrador dice (años y cifras de la transcripción; nombres y lugares del guion, bien escritos) y aparecen justo
  cuando se dicen; el mapa clava alfileres en los lugares nombrados; el titular del diario es el dato de esa parte.
  Cada video tiene su propio color de subtítulos, transición, recorridos de cámara, recuadro, estilo de dato y cierre
  (tablero de corcho, película, carpeta o pantallas con las imágenes del propio video). Nunca dos documentos iguales
  en un mismo video. Textos (título, descripción, prompt de miniatura) en «textos misterios nuevos».
- **v4 (queja: «todos tienen los mismos dibujos: mapa con pista, hoja»)**: se eliminaron los escenarios de relleno.
  Cada uno de los 96 misterios tiene 4 escenas propias escritas en `guion_visual.py`, que dibujan literalmente lo que
  dice cada párrafo (despegue de los Avenger en Florida, cabina con la brújula girando, hidroavión que desaparece,
  triángulo de las Bermudas…). Se componen con `escenario.py` (+ `escenario_obj.py`, `escenario_extra.py`): una
  línea por escena con capas (cielo, lugar, vehículos reales, personajes de época, objetos históricos, efectos).
  Regla: un mapa u hoja solo aparece si la historia trata de ese documento (mapa de Piri Reis, carta «Dear Boss»).

## Publicar en YouTube (Antwork, canal @1mrelato)
- Configuración fija en `publicacion_youtube.json`: público, **no es contenido para niños** (`madeForKids: false`),
  **sin contenido alterado o sintético** (`containsSyntheticMedia: false`), título y descripción tal cual del archivo
  en «textos misterios nuevos», y siempre el MP4 original en Full HD 1080×1920.
- Ubicación: Antwork no la permite todavía; el lugar de cada historia está en `publicacion_youtube.json` para ponerlo
  en YouTube Studio.
- Anotar cada video publicado en `textos misterios nuevos/SUBIDOS.md` para no repetir.

## Serie «100 historias» (relatos: historia, cultura, terror, videojuegos)
- **Duración pedida: 45–46 s por video.** La voz de Cristian Cornejo habla a ≈2,6 palabras/s, así que cada guion
  tiene 110–120 palabras (≈44 s de voz) y la cola final se ajusta en el render para cerrar en 45–46 s.
- Antes de escribir temas nuevos, revisar en Antwork lo ya publicado (YouTube y TikTok) y los 100 misterios para
  no repetir. Guiones en `guiones/historias_100.md`; textos en «textos historias nuevas» (`generar_textos_historias.py`).
- Videojuegos: contar la historia real, pero en dibujos y miniaturas no copiar personajes ni logotipos con derechos.

## Relatos en HyperFrames (desde el 27/11, `relatos_hf/`)
- **Motor**: `relatos_hf/motor.py N` arma un proyecto HyperFrames (HTML + GSAP) y lo renderiza a 1080×1920, 30 fps,
  calidad «delivery» (~3,5 Mbps, -14 LUFS). Planes visuales en `relatos_hf/planes40.py` → `planes/relato_NNN.json`.
  `validar.py` revisa que cada frase «en» exista en el guion, que existan los dibujos y los sonidos.
- **Dibujo** (pedido: «mejora el dibujo»): ilustraciones vectoriales nuevas (`ilustra*.py`, ~100 elementos) con
  degradados, contorno tinta, luz y reflejos, en capas con **profundidad**: la cámara (push, pull, pan, sube, baja)
  mueve cada capa distinto (parallax). Cada elemento trae su propia animación (humo, olas, llamas, colas, luces).
  El motor viejo en PIL se veía de bloques (iceberg cuadrado, edificios rectángulos): no se usa en los relatos.
- **Cada toma dibuja lo que dice esa frase** (mapas reales con world-atlas, fechas, contadores, títulos, escenas).
  Cambio de imagen cada 2–4 s (rea-video midió 4,6 s/toma en los videos viejos: muy lento para Shorts).
- **Cada video distinto**: 8 identidades (`ESTILOS`): color de palabra activa, palabra clave, recuadro de dato
  (ficha, post-it, sello, neón, etiqueta), forma del chip, transiciones y final (botón, chat escribiéndose,
  botones SÍ/NO, sello SUSCRÍBETE + campana). Durante el cierre se ocultan los subtítulos (no duplicar texto).
- **Voz** (pedido: «que la voz se escuche bien»): se acortan los silencios largos de ElevenLabs (los «…»),
  el ritmo se ajusta con rubberband sin cambiar el tono (0,86–1,15), EQ suave (graves fuera, presencia +2 dB),
  compresión ligera y de-esser. Mezcla final normalizada a -14 LUFS (estándar de YouTube).
- **Efectos** (pedido: «no tienen que ser efectos»): sin zumbido sintético de fondo; solo ambientes naturales por
  toma (mar, viento, fuego, multitud, lluvia…), barridos muy suaves en los cortes y pocos golpes. Margen
  voz/efectos 20–30 dB.
- **Duración 45–46 s**: el audio de ElevenLabs v3 salió de 30 a 50 s. Se resuelve con: silencios compactados →
  ritmo → pausas entre párrafos (0,25–1,3 s) → cola final (1,5–4,8 s) con el cierre animado.
- HyperFrames renderiza de a uno (bloqueo por cuenta): ~3,5–5,5 min por video; `lote.sh` deja la cola corriendo.
- GSAP: nunca `fromTo` sobre un elemento compartido (#flash) — el estado inicial se aplica de inmediato y tapaba
  el video; usar `set` + `to`. Las transformaciones de cámara de SVG se aplican con `setAttribute` desde un
  objeto animado (con `svgOrigin` el mapa no se veía en el render).
