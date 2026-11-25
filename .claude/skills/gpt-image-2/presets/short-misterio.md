# Preset: short-misterio

## Cuándo aplica
Miniaturas (portadas) de los YouTube Shorts de la serie «Misterios sin resolver» del canal *Pasó de Verdad*.
Pedidos como «haz la miniatura del misterio 14» o «portada del Vuelo 19».

## De dónde sale el contenido
1. Buscar el archivo del video en `textos misterios nuevos/misterio_NN_*.md`.
2. Usar su sección **«Prompt de miniatura (ChatGPT)»** como base: ya trae la escena real (modelo y color del avión o
   barco, época, lugar, objeto) y el texto grande en mayúsculas.
3. Traducirlo al inglés siguiendo `PROMPTING_GUIDE.md`, manteniendo el texto de la imagen EN ESPAÑOL entre comillas.

## Size y quality
- **Vertical 9:16**: `1008×1792` (múltiplos de 16, dentro de los límites de gpt-image-2)
- `quality high` (texto grande y nítido)

## Composición
- Elemento real de la historia en el centro, nítido; fondo con niebla, tormenta o rayos de luz.
- Un círculo rojo con flecha marcando el detalle más inquietante.
- Arriba: título enorme en mayúsculas, letra gruesa con borde negro (3–4 palabras).
- Abajo: etiqueta roja pequeña «MISTERIO SIN RESOLVER».
- Dejar libre la franja inferior (~15 %) donde YouTube pone sus botones.

## Constraints obligatorios
```
Cinematic hyperrealistic photo. Historically accurate vehicles, clothing and places for the year. Text exactly as
written, in Spanish. No watermark. No logos. No extra text. Keep the bottom 15% free of important elements.
```

## Salida
`./generated/short-misterio-<slug>-<YYYYMMDD>.png`
