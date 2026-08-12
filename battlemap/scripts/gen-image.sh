#!/usr/bin/env bash
# gen-image.sh — Fallback de generación de imágenes por el API directo de Gemini,
# para cuando la tool MCP `mcp__gemini-image__*` NO está disponible (p. ej. en
# sesiones remotas de Claude Code web, donde el entorno solo carga conectores
# remotos y no servers MCP locales stdio). Usa GEMINI_API_KEY del entorno; mismo
# modelo y resultado que el MCP @jimothy-snicket/gemini-image-mcp, cero infra.
#
# Uso:
#   gen-image.sh --prompt-file PROMPT.txt --out mapa.png [opciones]
#   gen-image.sh --prompt "texto del prompt en inglés" --out mapa.png [opciones]
#
# Opciones:
#   --aspect   16:9 (default) | 1:1 | 9:16 | 3:2 | 4:3 | 3:4
#   --model    gemini-2.5-flash-image (default) | gemini-3-pro-image-preview | gemini-3.1-flash-image-preview
#   --edit     IMG.png   imagen adjunta que se pasa al modelo (edición iterativa, Paso 4)
#   --ref      IMG.webp  sinónimo de --edit; úsalo cuando la imagen es semilla estructural
#   --api-key  KEY       (default: $GEMINI_API_KEY)
#
# Requiere: bash, curl, jq, base64, file.
set -euo pipefail

MODEL="gemini-2.5-flash-image"
ASPECT="16:9"
PROMPT=""
PROMPT_FILE=""
OUT=""
EDIT=""
API_KEY="${GEMINI_API_KEY:-}"

while [ $# -gt 0 ]; do
  case "$1" in
    --prompt)      PROMPT="$2"; shift 2;;
    --prompt-file) PROMPT_FILE="$2"; shift 2;;
    --out)         OUT="$2"; shift 2;;
    --aspect)      ASPECT="$2"; shift 2;;
    --model)       MODEL="$2"; shift 2;;
    --edit|--ref)  EDIT="$2"; shift 2;;
    --api-key)     API_KEY="$2"; shift 2;;
    -h|--help)     sed -n '2,19p' "$0"; exit 0;;
    *) echo "Opción desconocida: $1" >&2; exit 2;;
  esac
done

[ -n "$API_KEY" ] || { echo "ERROR: falta GEMINI_API_KEY (env) o --api-key" >&2; exit 1; }
[ -n "$OUT" ]     || { echo "ERROR: falta --out <archivo.png>" >&2; exit 1; }
[ -n "$PROMPT_FILE" ] && PROMPT="$(cat "$PROMPT_FILE")"
[ -n "$PROMPT" ]  || { echo "ERROR: falta --prompt o --prompt-file" >&2; exit 1; }

# CA bundle del proxy del entorno remoto, si existe (TLS hacia la API).
CACERT=()
[ -f /root/.ccr/ca-bundle.crt ] && CACERT=(--cacert /root/.ccr/ca-bundle.crt)

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# Body JSON (jq escapa el prompt). Con --edit, adjunta la imagen base inline.
if [ -n "$EDIT" ]; then
  [ -f "$EDIT" ] || { echo "ERROR: la imagen adjunta no existe: $EDIT" >&2; exit 1; }
  # El base64 va por ARCHIVO, no por --arg: en Linux un solo argumento no puede pasar de
  # ~128 KB (MAX_ARG_STRLEN), y una imagen real da megabytes — con --arg, jq muere con
  # "Argument list too long". Un .webp de semilla de 772 KB son 1.03 MB en base64.
  base64 -w0 "$EDIT" > "$TMP/b64.txt" 2>/dev/null || base64 "$EDIT" | tr -d '\n' > "$TMP/b64.txt"
  MIME="$(file -b --mime-type "$EDIT" 2>/dev/null || echo image/png)"
  jq -n --arg p "$PROMPT" --rawfile d "$TMP/b64.txt" --arg m "$MIME" --arg a "$ASPECT" \
    '{contents:[{parts:[{text:$p},{inlineData:{mimeType:$m,data:($d|rtrimstr("\n"))}}]}],generationConfig:{responseModalities:["IMAGE"],imageConfig:{aspectRatio:$a}}}' \
    > "$TMP/body.json"
else
  jq -n --arg p "$PROMPT" --arg a "$ASPECT" \
    '{contents:[{parts:[{text:$p}]}],generationConfig:{responseModalities:["IMAGE"],imageConfig:{aspectRatio:$a}}}' \
    > "$TMP/body.json"
fi

HTTP="$(curl -sS -w '%{http_code}' -o "$TMP/resp.json" "${CACERT[@]}" \
  -X POST "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent" \
  -H "x-goog-api-key: ${API_KEY}" -H "Content-Type: application/json" \
  --data @"$TMP/body.json")"

if [ "$HTTP" != "200" ]; then
  echo "ERROR HTTP $HTTP:" >&2
  jq -r '.error | "  \(.code) \(.status): \(.message)"' "$TMP/resp.json" 2>/dev/null >&2 \
    || head -c 400 "$TMP/resp.json" >&2
  exit 1
fi

DATA="$(jq -r '.candidates[0].content.parts[]? | select(.inlineData) | .inlineData.data' "$TMP/resp.json" | head -n1)"
if [ -z "$DATA" ] || [ "$DATA" = "null" ]; then
  echo "ERROR: la respuesta no trae imagen (¿bloqueada por safety o cuota?). finishReason:" >&2
  jq -r '.candidates[0].finishReason // "(sin candidates)"' "$TMP/resp.json" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
printf '%s' "$DATA" | base64 -d > "$OUT"
echo "OK: $OUT ($(file -b "$OUT" 2>/dev/null || echo PNG))"
