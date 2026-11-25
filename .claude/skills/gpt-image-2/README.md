# gpt-image-2 — Skill para Claude Code

> Integrada desde [AgustinGoniDev/gpt-image-2-skill-claude-code](https://github.com/AgustinGoniDev/gpt-image-2-skill-claude-code). Se agregó el preset `short-misterio` y el uso de la key segura en sesiones en la nube.

Genera imágenes con OpenAI gpt-image-2 directamente desde Claude Code. Sin dependencias adicionales — solo `curl` y tu API key.

## Setup

1. Conseguí tu API key en https://platform.openai.com/api-keys
2. Exportala en tu terminal: `export OPENAI_API_KEY=sk-...`

O simplemente ejecutá el skill desde Claude Code — te guía en el proceso.

## Presets incluidos

| Preset | Descripción |
|--------|-------------|
| `yt-thumbnail` | Miniaturas YouTube 16:9, alta energía, texto grande |
| `linkedin-infografia` | Infografías para LinkedIn, layout limpio, texto estructurado |
| `generico` | Cualquier otro asset — el skill pregunta lo necesario |
| `short-misterio` | Miniatura vertical 9:16 de un misterio, usando el prompt de «textos misterios nuevos» |

## Estructura

```
gpt-image-2/
├── SKILL.md              ← instrucciones para Claude
├── PROMPTING_GUIDE.md    ← best practices de prompting
├── presets/
│   ├── yt-thumbnail.md
│   ├── linkedin-infografia.md
│   └── generico.md
└── README.md
```

## Uso

Decile a Claude Code cualquier cosa como:

- "Generá una miniatura para mi video sobre errores con Claude Code"
- "Hacé una infografía de LinkedIn sobre los 3 tipos de agentes de IA"
- "Necesito una imagen para mi presentación sobre automatización"

El skill detecta el preset, redacta el prompt y ejecuta el curl.

## Modo con imagen de referencia

Para thumbnails con tu foto u otra imagen base, adjuntá la imagen en el chat o indicá el path. El skill usa el endpoint `/images/edits` de OpenAI para preservar identidad.

## Dónde quedan las imágenes

En `./generated/` relativo a tu directorio actual.
