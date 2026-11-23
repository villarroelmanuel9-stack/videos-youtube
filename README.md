# Fábrica de Shorts animados 🎬

Escribe una historia en un archivo `.json` → obtienes un Short vertical (1080×1920) listo para subir, con:

- 🎙️ Voz narrada en español (voces neuronales gratis de Microsoft vía `edge-tts`)
- ✨ Animación: fondo en movimiento, partículas, emoji “personaje” que rebota, fotos con zoom tipo documental
- 🔤 Subtítulos virales palabra por palabra con la palabra activa resaltada
- 🪝 Gancho en rojo los primeros 3 segundos y barra de progreso
- 🎵 Música de fondo opcional
- 📝 Miniatura + archivo con título, descripción y hashtags

## 1. Instalación (una sola vez)

1. Instala **Python 3.9+** → https://www.python.org/downloads/ (en Windows marca “Add to PATH”).
2. Instala **ffmpeg** → Windows: `winget install ffmpeg` · Mac: `brew install ffmpeg` · Linux: `sudo apt install ffmpeg`
3. En esta carpeta:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Crear un video

```bash
python generar_short.py historias/ejemplo_misterio.json
```

El resultado aparece en `salida/`: el `.mp4`, la miniatura `.jpg` y el `_publicar.txt` con título, descripción y hashtags.
Tarda ~2 minutos por cada video de 35 s. Para hacer varios: `python generar_short.py historias/*.json`.

## 3. Escribir tus propias historias

Copia un ejemplo de `historias/` y edítalo:

| Campo | Qué es |
|---|---|
| `titulo` | Título para YouTube (máx. ~70 caracteres, termina con `#shorts`) |
| `gancho` | Frase que aparece arriba los primeros 3 s. **Lo más importante del video** |
| `voz` | `es-MX-JorgeNeural`, `es-MX-DaliaNeural`, `es-ES-AlvaroNeural`, `es-ES-ElviraNeural`, `es-AR-TomasNeural`, `es-CO-GonzaloNeural`… |
| `velocidad` | `+10%` suena dinámico; `+0%` para terror lento |
| `color_resaltado` | Color de la palabra activa (`#FFE400` amarillo, `#00F5D4` turquesa) |
| `musica` | Ruta a un `.mp3` (ponlo en `musica/`) y `volumen_musica` 0.08–0.15 |
| `escenas` | Lista de escenas: `texto` (lo que se narra), `emoji`, `colores` (2 colores del fondo) y opcional `imagen` (ruta a una foto; se anima con zoom) |

**Fórmula que funciona en Shorts:** gancho en la 1.ª frase → 4–6 escenas de 1–2 frases → giro/sorpresa → pregunta o “sígueme para la parte 2”. Ideal: 25–50 segundos.

**Atajo con IA:** pídele a Claude/ChatGPT: *“Escríbeme 10 historias originales de terror de 40 segundos en el formato JSON de este ejemplo: (pega el ejemplo)”*. Revisa y corrige siempre lo que te dé (sobre todo datos históricos).

Los números escríbelos en letras en el `texto` (“tres y treinta y tres”) para que la voz los lea bien; en el `gancho` puedes usar cifras.

## 4. Nichos que funcionan con este formato

- **Terror / creepypastas originales** (series con “parte 2” = suscriptores)
- **Historias reales increíbles** y datos curiosos de historia
- **Misterios sin resolver** y casos famosos
- **Psicología / “cosas que tu cerebro hace”**
- **Curiosidades de famosos, películas o series** (contadas por ti, sin usar clips)
- **Historias tipo Reddit / “¿Soy el malo?”** reescritas con tus palabras

Elige **un** nicho por canal. Publica 1–3 Shorts diarios durante al menos 2–3 meses; el algoritmo premia la constancia.

## 5. Monetización — lo que debes saber

### Requisitos del Programa de Socios de YouTube (YPP)
- **Ingresos por anuncios en Shorts:** 1.000 suscriptores **y** 10 millones de vistas válidas de Shorts en los últimos 90 días (o 4.000 horas de reproducción de videos largos en 12 meses).
- **Nivel inicial** (Super Thanks, membresías, compras): 500 suscriptores + 3 videos en los últimos 90 días + 3 millones de vistas de Shorts en 90 días (o 3.000 horas).
- Revisa los números actuales en YouTube Studio → **Ganar dinero**, porque YouTube los ajusta y varían según el país.

### ⚠️ Cómo NO perder la monetización (muy importante con contenido automatizado)
YouTube rechaza canales con **contenido no original / “inauténtico”**: videos producidos en masa, repetitivos o hechos con plantillas sin aporte humano. Para pasar la revisión:

1. **Guiones propios.** No copies historias de otros canales ni pegues textos de Reddit/Wikipedia tal cual: reescríbelos con tu estilo, opinión y giros.
2. **Varía el formato:** cambia colores, voces, música, emojis; mezcla con fotos propias o generadas por ti.
3. **Nada de clips ajenos.** Para temas “mediáticos” (películas, series, noticias, famosos) **no** uses fragmentos de TV, películas u otros youtubers: provocan reclamos de Content ID y rechazo por “contenido reutilizado”. Cuenta la historia tú y usa imágenes propias, de **Pexels/Pixabay/Unsplash** (gratis) o generadas con IA.
4. **Música** solo de la **Biblioteca de audio de YouTube** (Studio → Biblioteca de audio) o con licencia.
5. **Divulgación de IA:** si un video muestra personas, lugares o eventos **realistas** creados o alterados con IA (o una voz que imita a alguien real), marca *“Contenido alterado o sintético”* al subirlo. El estilo emoji/caricatura de este generador normalmente no lo requiere.
6. Considera **grabar tu propia voz** en algunos videos o añadir tu opinión: eso cuenta mucho como “aporte humano”.

### Otras formas de ganar dinero (antes de llegar al YPP)
- **Afiliados** (Amazon, Hotmart) con el enlace en tu perfil y comentario fijado.
- **Llevar tráfico a videos largos** (compilaciones de 10 historias = más horas de reproducción, que pagan mucho más que los Shorts).
- **TikTok, Instagram Reels y Facebook** con el mismo video (sin marca de agua de otra app).

## 6. Al subir el video
1. YouTube Studio → **Crear → Subir video** (o desde la app del celular).
2. Copia el título, la descripción y los hashtags de `salida/<nombre>_publicar.txt`.
3. Responde comentarios la primera hora; fija un comentario con una pregunta.
4. A los 2–3 días revisa en Analytics la **retención** y el **% de “deslizó para ver” vs “deslizó para saltar”**: si la gente se va en el segundo 1–2, mejora el gancho.

## Estructura

```
generar_short.py      # el generador
historias/            # tus guiones .json (ejemplos incluidos)
musica/               # pon aquí tus .mp3 de música libre de derechos
fuentes/              # opcional: texto.ttf / emoji.ttf para cambiar la tipografía
salida/               # videos generados (no se sube a git)
```
