#!/bin/bash
# SessionStart hook — TEMPLATE repo-agnóstico.
# Materializa en .claude/skills/ skills de repos de TERCEROS (layout skills/*/,
# como obra/Superpowers o DietrichGebert/ponytail), bajando cada repo por `git clone`
# vía el relay del entorno, con TARBALL de codeload como fallback. DOS niveles de
# whitelist en UN archivo .claude/upstream-skills.txt:
#
#   # una línea por fuente:  owner/repo[@ref]   [skill1 skill2 ...]
#   #   - sin skills listadas → trae TODAS las del skills/ de ese repo
#   #   - con skills listadas → solo esas (whitelist por fuente)
#   #   - @ref opcional       → rama/tag/commit (sin @ref = main)
#   #   - una LÍNEA = "clona este repo"; sin línea = no lo clones (whitelist de repos)
#   obra/Superpowers          brainstorming test-driven-development writing-skills
#   DietrichGebert/ponytail   ponytail ponytail-review
#
# Cópialo a .claude/hooks/sync-upstream-skills.sh y regístralo como SessionStart en
# .claude/settings.json (ver el README de claude-skills, sección "Cableado de skills
# upstream"). El archivo upstream-skills.txt es el ÚNICO knob per-repo: decide a la
# vez QUÉ repos y QUÉ skills de cada uno.
#
# Doble transporte (la política de red varía entre entornos): primero `git clone`
# vía el relay del entorno, y si falla, TARBALL de codeload como fallback. Se observó
# que algunos entornos autorizan el relay para repos AJENOS pero dan 403 en codeload,
# y otros al revés — probar ambos hace el hook resiliente a cualquiera de las dos.
# (Pin por SHA: `git clone --branch` no acepta SHA; ese caso cae al tarball, que sí.)
# Los plugins están desactivados en la web (SKIP_PLUGIN_MARKETPLACE). Nombres PLANOS
# (sin prefijo), cp -a preserva references/ y scripts/ ejecutables. Colisión de
# nombres entre fuentes → gana la última escrita (el orden del archivo manda).
#
# Solo corre en la nube: en local conviene instalar los plugins nativos. El JSON del
# hook es lo ÚNICO en stdout; los logs van a stderr. Emite reloadSkills:true si
# materializó algo, para cargarlas en ESTA misma sesión.

SKILLS_DIR="$CLAUDE_PROJECT_DIR/.claude/skills"
SOURCES_TXT="$CLAUDE_PROJECT_DIR/.claude/upstream-skills.txt"

LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/.hooks.log"
log() { echo "$(date -u +%FT%TZ) [sync-upstream] $*" | tee -a "$LOG_FILE" >&2; }

log "start (remote=$CLAUDE_CODE_REMOTE)"

# En local no hacemos nada (los plugins nativos son la vía allí).
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  log "no-cloud: skip (usa los plugins nativos en local)"
  exit 0
fi

[ -f "$SOURCES_TXT" ] || { log "sin $SOURCES_TXT; nada que hacer"; exit 0; }

mkdir -p "$SKILLS_DIR"
total=0

# git clone --depth 1 con hasta 3 intentos: el relay puede fallar transitoriamente
# en el cold-start ("no caliente") y ahí el reintento lo rescata. $1=slug $2=ref $3=dst.
clone_retry() {
  local n=0
  until git clone --quiet --depth 1 --branch "$2" "https://github.com/$1.git" "$3" 2>/dev/null; do
    n=$((n + 1)); [ "$n" -ge 3 ] && return 1; sleep "$n"
  done
}

# Lee el archivo: primer token = owner/repo[@ref]; el resto = whitelist de skills.
# grep quita comentarios (#) y líneas en blanco antes del while.
while read -r src wl; do
  [ -n "$src" ] || continue

  # Separa @ref (rama/tag/commit). Sin @ → main.
  case "$src" in
    *@*) ref="${src##*@}"; slug="${src%@*}" ;;
    *)   ref="main";        slug="$src" ;;
  esac

  TMP=$(mktemp -d)
  ROOT=""
  # Transporte 1: git clone (shallow) vía el relay del entorno, con reintento.
  if clone_retry "$slug" "$ref" "$TMP/clone"; then
    ROOT="$TMP/clone"
  # Transporte 2 (fallback): tarball de codeload. Shorthand /tar.gz/<ref> (rama/tag/sha).
  elif curl -sSL --max-time 120 "https://codeload.github.com/$slug/tar.gz/$ref" -o "$TMP/src.tar.gz" \
       && tar -xzf "$TMP/src.tar.gz" -C "$TMP" --strip-components=1 2>/dev/null; then
    ROOT="$TMP"
  else
    log "✗ $slug@$ref: git clone (con reintento) y codeload fallaron; skip"
    rm -rf "$TMP"; continue
  fi
  if [ ! -d "$ROOT/skills" ]; then
    log "✗ $slug@$ref: el árbol no trae skills/; skip"
    rm -rf "$TMP"; continue
  fi

  # Copia una skill del árbol extraído a SKILLS_DIR (cp -a, sin huérfanos).
  copy_skill() {
    local dir="$1" name
    name=$(basename "$dir")
    [ -f "$dir/SKILL.md" ] || { log "  ✗ $name (sin SKILL.md)"; return; }
    rm -rf "$SKILLS_DIR/$name"
    cp -a "$dir" "$SKILLS_DIR/$name"
    total=$((total + 1))
    log "  ✓ $name (de $slug)"
  }

  if [ -z "$wl" ]; then
    # Sin whitelist → todas las skills del repo.
    for d in "$ROOT"/skills/*/; do copy_skill "$d"; done
  else
    # Whitelist por fuente → solo las listadas.
    for name in $wl; do
      if [ -d "$ROOT/skills/$name" ]; then copy_skill "$ROOT/skills/$name"
      else log "  ✗ $name (no está en $slug@$ref)"; fi
    done
  fi

  rm -rf "$TMP"
done < <(grep -vE '^\s*(#|$)' "$SOURCES_TXT")

log "materializadas $total skills upstream"
[ "$total" -gt 0 ] && printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","reloadSkills":true}}\n'
exit 0
