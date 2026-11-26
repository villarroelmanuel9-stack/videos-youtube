# Herramientas externas

Repos de otros proyectos, agregados como **submódulos de git**: el código de cada uno queda en su propia carpeta y
mantiene su licencia. Para bajarlos en otra computadora:

```bash
git submodule update --init --depth 1 herramientas/hyperframes   # solo el que necesites
git submodule update --init --depth 1                            # todos (≈3 GB: three.js y remotion son grandes)
```

Revisados y probados el 26/11/2026 con los videos del canal.

## Sirven para mejorar los videos

| Carpeta | Qué es | Licencia | Prueba | Veredicto |
|---|---|---|---|---|
| `hyperframes` | HeyGen HyperFrames: escribes la escena en HTML, CSS y GSAP y la renderiza a MP4 cuadro a cuadro. Trae linter, revisión de zonas seguras de Shorts, subtítulos y ~450 bloques listos (transiciones, títulos animados, mapas, 3D). | Apache-2.0 | ✅ Renderizó 13,5 s del Faro de Flannan con la voz real (`../pruebas/flannan_hyperframes.mp4`): faro con haz giratorio, lluvia, relámpagos, guardianes que se desvanecen, barco y subtítulos palabra por palabra sincronizados. Tardó 1 min 50 s en CPU. | **La mejor opción** para subir el nivel: animaciones con easing profesional, cámara, textos con rebote y salida a CRF 16 (más nitidez). Gratis y local (no hace falta HeyGen Pro). |
| `GSAP` | La librería de animación que usa HyperFrames (easing, timelines, stagger). | Licencia propia de GreenSock, gratis (incluso uso comercial) | ✅ Se usó en la prueba. | Se usa con HyperFrames, no por separado. |
| `remotion` + `remotion-skills` | Lo mismo que HyperFrames, pero con React. Las skills enseñan a Claude a usarlo (subtítulos, render, mapas). | Remotion License: **gratis para personas y empresas pequeñas** | Lo revisé, no lo rendericé: hace lo mismo que HyperFrames y es más pesado (React). | Alternativa. Si se elige uno, HyperFrames, porque está más pensado para que un agente lo use y trae revisión automática. |
| `three.js` | 3D en el navegador. | MIT | Lo revisé. HyperFrames lo carga como "runtime" 3D. | Útil para escenas 3D (barcos, aviones, planetas) dentro de HyperFrames. |
| `rea-video` | Analiza cualquier video (tuyo o de la competencia) toma por toma: ritmo de cortes, subtítulos, música, efectos de sonido y plan para recrearlo. | Apache-2.0 | ✅ Lo pasé por `misterio_02_vuelo_19`: 7 tomas en 32 s (**4,6 s por toma**), 37 líneas de subtítulos, música a 126 BPM y 6 efectos de sonido. Sin un modelo de visión confunde la animación con "3D/IA" (eso pasa en el modo sin VLM). | Útil para **estudiar Shorts virales** de la competencia y copiar su ritmo, no su contenido. Dato clave: la guía de Shorts recomienda una toma nueva cada 1–2 s y un cambio cada 2–4 s; los nuestros duran 4–7 s por toma. |
| `lemo-opuscar` | 99 estilos de película hechos 100 % en código (explicativos, noticias, cine, 2D, 3D), cada uno con su demo y su prompt. | Varias (MIT, CC-BY, OFL…) | Lo revisé. | Catálogo de **estilos visuales** para elegir uno nuevo para el canal. |
| `awesome-opus5-5-videos` | 703 prompts de videos virales hechos en código (HTML, Canvas, Three.js). | MIT | Lo revisé. | Ideas y prompts de animación. |
| `pixelfx` | 244 efectos pixel art (fuego, explosiones, magia, clima) en código, con su skill. | MIT | Lo revisé. | Para la serie de **videojuegos** (relatos 85–100): explosiones, monedas y power-ups. |
| `effectcraft` | Editor de motion graphics tipo After Effects, de código abierto, con exportación a Lottie. | MIT / Apache-2.0 | Lo revisé: es una app de escritorio en Rust y no corre en este servidor. | Útil solo si alguien edita a mano en su computadora. |

## No mejoran los videos (los dejé porque los pediste)

| Carpeta | Qué es |
|---|---|
| `mcp-for-blender` | Conecta Claude con Blender (3D). Necesita Blender abierto en tu computadora; aquí no hay Blender. |
| `unslop`, `impeccable` | Skills para mejorar el **diseño de páginas web**. No tocan los videos. |
| `anthropic-skills` | Skills oficiales de Anthropic (documentos, diseño, GIF para Slack). Ninguna es de video. |
| `higgsfield` | Para entrenar modelos de lenguaje en servidores con varias GPU. No tiene nada de video. |
| `open-higgsfield` | Página para generar videos con la API **de pago** de Higgsfield (necesita clave con créditos). |
| `open-source-higgsfield` | Solo una lista de enlaces. |

## Otra mejora encontrada (sin herramientas nuevas)

Los misterios se exportan a ~2,2 Mbps y la prueba de HyperFrames a ~4 Mbps (CRF 16). Subir a YouTube con más
bitrate (CRF 16–18 o 8–12 Mbps en 1080p) reduce el "lavado" que hace YouTube al recomprimir.
