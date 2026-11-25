---
name: gpt-image-2
description: Genera imágenes con OpenAI gpt-image-2 via API REST (sin dependencias Python). Soporta generación desde texto y edición con imagen de referencia. Presets para YouTube thumbnail, LinkedIn infografía, y uso genérico. Triggereá cuando el usuario diga 'generá una imagen', 'creá una imagen', 'armá una miniatura', 'hacé una infografía', 'necesito una imagen para...', o variantes.
---

# Skill: gpt-image-2 — Generación de Imágenes via API

Genera imágenes con OpenAI gpt-image-2 llamando directamente a la API REST con `curl`. No requiere instalar ningún paquete adicional.

---

## Step 1 — API key

Verificar si `OPENAI_API_KEY` está disponible en el entorno:

```bash
echo $OPENAI_API_KEY
```

**En una sesión en la nube de Claude Code** (este repositorio): no pedir que peguen la key en el chat. Pedirla con la
herramienta de credenciales del entorno (`request_credential`, host `api.openai.com`, tipo bearer): el proxy la agrega
sola a las llamadas a la API y nunca queda escrita en el chat ni en el repositorio. Después de guardarla, `curl` funciona
aunque `$OPENAI_API_KEY` esté vacía (usar un valor de relleno, p. ej. `sk-proxy`, en el encabezado).

**Si no está seteada o está vacía** (uso local en tu computador), guiar al usuario:

> Para usar este skill necesitás una API key de OpenAI.
> 1. Conseguila en https://platform.openai.com/api-keys (sección "Create new secret key")
> 2. Pegame la key acá y la uso para esta sesión, o exportala con:
>    ```bash
>    export OPENAI_API_KEY=sk-...
>    ```
> 3. Si querés que persista entre sesiones, la guardo en un archivo `.env` en tu directorio actual.

Una vez que el usuario provea la key:
- Validar que empiece con `sk-` o `sk-proj-`
- Si el usuario quiere persistirla: crear o editar `.env` en el CWD con `OPENAI_API_KEY=<key>` (`.env` está en
  `.gitignore`: nunca subirlo a GitHub)
- Usar la key en los comandos curl de los pasos siguientes

---

## Step 2 — Detectar preset

Identificar cuál preset aplica:

| Preset | Cuándo usarlo |
|--------|--------------|
| `yt-thumbnail` | Miniaturas de YouTube, thumbnails de video |
| `linkedin-infografia` | Infografías visuales para LinkedIn |
| `generico` | Cualquier otro asset sin plataforma específica |
| `short-misterio` | Miniaturas verticales 9:16 de la serie «Misterios sin resolver» (canal Pasó de Verdad) |

Si no está claro, preguntar al usuario antes de continuar.

---

## Step 3 — Cargar contexto (OBLIGATORIO antes de redactar el prompt)

Cargar siempre:
1. [PROMPTING_GUIDE.md](PROMPTING_GUIDE.md) — best practices para redactar el prompt
2. El archivo de preset correspondiente en [presets/](presets/)

---

## Step 4 — Decidir parámetros

Basándose en el pedido del usuario y las sugerencias del preset:

- **`size`**: Resolución WxH. Reglas gpt-image-2: ambos lados múltiplos de 16, max edge < 3840px, ratio ≤ 3:1, total 655.360–8.294.400px.
- **`quality`**: `high` para texto fino / identidad a preservar / output final; `medium` para la mayoría de casos; `low` para drafts.
- **`reference`**: Si el usuario menciona "con mi foto", "usando esta imagen", o el preset lo requiere. Preguntar qué archivo si no fue indicado.

---

## Step 5 — Redactar el prompt

Siguiendo `PROMPTING_GUIDE.md`:
1. Orden: background/scene → subject → key details → constraints
2. Siempre en inglés
3. Texto literal en la imagen: entre comillas dobles en el prompt + ALL CAPS para titulares
4. Constraints negativos al final: "no watermark", "no extra text", etc.
5. Con referencia: incluir `"Do not change face, hair, skin tone, body shape"` si hay personas

---

## Step 6 — Resolver paths

- **Output**: `./generated/<preset>-<slug>-<YYYYMMDD>.png` relativo al directorio actual
  - Ejemplo: `./generated/yt-thumbnail-claude-code-errores-20260501.png`
- **Referencias**: el path que indique el usuario

---

## Step 7 — Invocar via API

`gpt-image-2` devuelve `b64_json` por defecto — no hay que pedirlo como parámetro.

### Windows (PowerShell) — sin imagen de referencia

```powershell
$body = @{
  model   = "gpt-image-2"
  prompt  = "<PROMPT>"
  size    = "<WxH>"
  quality = "<low|medium|high>"
  n       = 1
} | ConvertTo-Json

$headers = @{ "Authorization" = "Bearer $env:OPENAI_API_KEY"; "Content-Type" = "application/json" }
$r = Invoke-RestMethod -Uri "https://api.openai.com/v1/images/generations" -Method POST -Headers $headers -Body $body

$outDir = "<OUTPUT_DIR>"
if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
$bytes = [Convert]::FromBase64String($r.data[0].b64_json)
$outPath = Join-Path (Get-Location) "$outDir\<FILENAME>.png"
[IO.File]::WriteAllBytes($outPath, $bytes)
Write-Host "Guardado en:" $outPath
```

### Mac / Linux / WSL — sin imagen de referencia

```bash
curl -s -X POST https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "<PROMPT>",
    "size": "<WxH>",
    "quality": "<low|medium|high>",
    "n": 1
  }' | python3 -c "
import sys, json, base64, os
r = json.load(sys.stdin)
if 'error' in r:
    print('Error:', r['error']['message']); sys.exit(1)
data = r['data'][0]['b64_json']
out = '<OUTPUT_PATH>'
os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
open(out, 'wb').write(base64.b64decode(data))
print('Guardado en:', out)
"
```

### Con imagen de referencia (modo edit — Windows, usando curl.exe)

En Windows usar `curl.exe` (no Invoke-RestMethod) para multipart con archivo:

```powershell
$response = & curl.exe -s -X POST 'https://api.openai.com/v1/images/edits' `
  -H "Authorization: Bearer $env:OPENAI_API_KEY" `
  -F "model=gpt-image-2" `
  -F "image=@`"<PATH_REFERENCIA>`"" `
  -F "prompt=<PROMPT>" `
  -F "size=<WxH>" `
  -F "quality=<low|medium|high>"

$r = $response | ConvertFrom-Json
if ($r.error) { Write-Error $r.error.message; exit 1 }
$bytes = [Convert]::FromBase64String($r.data[0].b64_json)
[IO.File]::WriteAllBytes((Join-Path (Get-Location) "<OUTPUT_PATH>"), $bytes)
Write-Host "Guardado en: <OUTPUT_PATH>"
```

### Con imagen de referencia (Mac/Linux curl)

```bash
curl -s -X POST https://api.openai.com/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "model=gpt-image-2" \
  -F "image=@<PATH_REFERENCIA>" \
  -F "prompt=<PROMPT>" \
  -F "size=<WxH>" \
  -F "quality=<low|medium|high>" \
  | python3 -c "
import sys, json, base64, os
r = json.load(sys.stdin)
if 'error' in r:
    print('Error:', r['error']['message']); sys.exit(1)
data = r['data'][0]['b64_json']
out = '<OUTPUT_PATH>'
os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
open(out, 'wb').write(base64.b64decode(data))
print('Guardado en:', out)
"
```

Detectar el OS del usuario y usar el bloque correspondiente. Reportar el error de la API si el comando falla.

---

## Step 8 — Mostrar resultado

Reportar al usuario:
- Path de la imagen generada
- Parámetros usados (size, quality, modelo)
- Prompt final (para referencia y futuras iteraciones)
- Ofrecer iterar con cambios pequeños (un cambio por vez, según la guía)

---

## Reglas duras

- **Nunca** redactar el prompt sin haber cargado `PROMPTING_GUIDE.md` + el preset
- Prompts siempre en inglés
- Texto literal siempre entre comillas dobles en el prompt
- En iteraciones: repetir siempre los constraints de preservación (evitar drift)
- Nombre de archivo: siempre `<preset>-<slug>-<YYYYMMDD>.png`
