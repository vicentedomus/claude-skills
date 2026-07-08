#!/bin/bash
# SessionStart hook — TEMPLATE repo-agnóstico.
# Materializa el COMBO spec-kit vendorizado (spec-kit + weave con superpowers) que vive
# en claude-skills/speckit-combo/payload/. A diferencia de sync-upstream-skills.sh (que
# baja skills de terceros con layout skills/*/ en VIVO), este trae un subsistema
# vendorizado y pineado: skills speckit-* + el scaffold .specify/ (templates, scripts
# bash, workflows, integrations) + la constitución sembrada con el weave.
#
# Knob per-repo (whitelist de UN archivo): .claude/speckit.txt
#   - existe            → materializa el combo
#   - contiene @<ref>   → baja el payload desde esa rama/tag/commit de claude-skills
#                         (sin @ref = main). Útil para pinear otra versión del combo.
#   - no existe         → no hace nada
#
# Cópialo a .claude/hooks/sync-speckit.sh y regístralo como SessionStart en
# .claude/settings.json (ver el README de claude-skills, sección "Cableado de spec-kit").
#
# PARTICIÓN durable/regenerable (clave): el core se sobrescribe SIEMPRE (regenerable);
# .specify/memory/constitution.md y specs/ NUNCA se pisan si ya existen (contenido del
# proyecto, comiteado). La constitución se siembra solo la primera vez (write-if-absent).
#
# Doble transporte (la política de red varía entre entornos): primero `git clone` vía el
# relay del entorno, y si falla, TARBALL de codeload como fallback. Solo corre en la nube
# (en local usa `specify init` nativo). El JSON del hook es lo ÚNICO en stdout; los logs
# van a stderr. Emite reloadSkills:true si materializó skills, para cargarlas en ESTA sesión.

# Repo fuente del combo (este repo). Cambia el slug si forkeas claude-skills.
COMBO_REPO="vicentedomus/claude-skills"
COMBO_SUBDIR="speckit-combo/payload"

SKILLS_DIR="$CLAUDE_PROJECT_DIR/.claude/skills"
SPECIFY_DIR="$CLAUDE_PROJECT_DIR/.specify"
KNOB="$CLAUDE_PROJECT_DIR/.claude/speckit.txt"

LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/.hooks.log"
log() { echo "$(date -u +%FT%TZ) [sync-speckit] $*" | tee -a "$LOG_FILE" >&2; }

log "start (remote=$CLAUDE_CODE_REMOTE)"

# En local no hacemos nada (usa `specify init` nativo allí).
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  log "no-cloud: skip (usa 'specify init' nativo en local)"
  exit 0
fi

[ -f "$KNOB" ] || { log "sin $KNOB; nada que hacer"; exit 0; }

# Ref del combo: primera línea no-comentario del knob, o 'main'.
REF=$(grep -vE '^\s*(#|$)' "$KNOB" 2>/dev/null | head -1 | tr -d '[:space:]')
case "$REF" in @*) REF="${REF#@}" ;; "") REF="main" ;; esac
log "combo ref = $REF"

# git clone --depth 1 con hasta 3 intentos (el relay puede fallar en cold-start).
clone_retry() {
  local n=0
  until git clone --quiet --depth 1 --branch "$2" "https://github.com/$1.git" "$3" 2>/dev/null; do
    n=$((n + 1)); [ "$n" -ge 3 ] && return 1; sleep "$n"
  done
}

TMP=$(mktemp -d)
ROOT=""
# Transporte 1: git clone (shallow) vía el relay del entorno, con reintento.
if clone_retry "$COMBO_REPO" "$REF" "$TMP/clone"; then
  ROOT="$TMP/clone"
# Transporte 2 (fallback): tarball de codeload. Shorthand /tar.gz/<ref> (rama/tag/sha).
elif curl -sSL --max-time 120 "https://codeload.github.com/$COMBO_REPO/tar.gz/$REF" -o "$TMP/src.tar.gz" \
     && tar -xzf "$TMP/src.tar.gz" -C "$TMP" --strip-components=1 2>/dev/null; then
  ROOT="$TMP"
else
  log "✗ $COMBO_REPO@$REF: git clone (con reintento) y codeload fallaron; skip"
  rm -rf "$TMP"; exit 0
fi

PAYLOAD="$ROOT/$COMBO_SUBDIR"
if [ ! -d "$PAYLOAD/skills" ] || [ ! -d "$PAYLOAD/specify" ]; then
  log "✗ $COMBO_REPO@$REF: el árbol no trae $COMBO_SUBDIR/{skills,specify}; skip"
  rm -rf "$TMP"; exit 0
fi

# ---- 1) Skills speckit-* → .claude/skills/  (REGENERABLE: sobrescribe siempre) ----
mkdir -p "$SKILLS_DIR"
skills_n=0
for d in "$PAYLOAD"/skills/*/; do
  [ -f "$d/SKILL.md" ] || continue
  name=$(basename "$d")
  rm -rf "$SKILLS_DIR/$name"
  cp -a "$d" "$SKILLS_DIR/$name"
  skills_n=$((skills_n + 1))
done
log "  ✓ $skills_n skills speckit-* materializadas"

# ---- 2) Scaffold .specify/  (REGENERABLE core + DURABLE protegido) ----
mkdir -p "$SPECIFY_DIR"
# Core regenerable: sobrescribe siempre.
for item in templates scripts workflows integrations init-options.json integration.json; do
  [ -e "$PAYLOAD/specify/$item" ] || continue
  rm -rf "$SPECIFY_DIR/$item"
  cp -a "$PAYLOAD/specify/$item" "$SPECIFY_DIR/$item"
done
# Asegura bit ejecutable de los scripts bash (por si el transporte lo perdió).
chmod +x "$SPECIFY_DIR"/scripts/bash/*.sh 2>/dev/null
log "  ✓ .specify core (templates/scripts/workflows/integrations) refrescado"

# DURABLE: la constitución se siembra SOLO si no existe. Nunca se pisa contenido propio.
mkdir -p "$SPECIFY_DIR/memory"
if [ -f "$SPECIFY_DIR/memory/constitution.md" ]; then
  log "  = memory/constitution.md ya existe → intacto (contenido del proyecto)"
elif [ -f "$PAYLOAD/specify/memory/constitution.md" ]; then
  cp "$PAYLOAD/specify/memory/constitution.md" "$SPECIFY_DIR/memory/constitution.md"
  log "  ✓ memory/constitution.md sembrado con el weave (primera vez)"
fi
# specs/ jamás se toca (ni se crea): es 100% contenido del proyecto.

rm -rf "$TMP"
log "combo materializado (skills=$skills_n)"
[ "$skills_n" -gt 0 ] && printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","reloadSkills":true}}\n'
exit 0
