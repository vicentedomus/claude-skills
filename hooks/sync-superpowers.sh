#!/bin/bash
# SessionStart hook — TEMPLATE repo-agnóstico.
# Materializa en .claude/skills/ las skills de obra/Superpowers como skills PLANAS,
# bajando el repo por TARBALL de codeload (HTTPS). Copia TODAS las skills del
# tarball (skills/*/SKILL.md) — sin whitelist: el set entero.
#
# Cópialo a .claude/hooks/sync-superpowers.sh en el repo consumidor y regístralo
# como SessionStart en .claude/settings.json (ver el README de claude-skills,
# sección "Cableado de superpowers en cualquier repo"). Los únicos knobs son las
# variables OWNER/REPO/REF de abajo.
#
# Por qué tarball y no git clone / plugin:
#   - El relay git del entorno web da 403 para repos AJENOS (obra/Superpowers no
#     está en el scope de sesión). codeload.github.com sí pasa por el proxy.
#   - El instalador de plugins no sirve aquí: el entorno fija
#     SKIP_PLUGIN_MARKETPLACE=true, así que Claude Code ni intenta el marketplace.
#   - Claude Code carga .claude/skills/*/SKILL.md igual que las de un plugin, así
#     que con cp -a de cada skill basta para tenerlas disponibles.
#
# Decisiones (espejo de PR #80 de questkeep):
#   - Rama main (sin pin de tag): siempre la última versión, drift asumido.
#   - Nombres PLANOS (sin prefijo superpowers:): se cargan como brainstorming,
#     test-driven-development, etc. Sus cross-referencias internas dicen
#     "superpowers:X" pero el modelo las mapea.
#   - SIN la inyección agresiva del hook nativo: las skills quedan DISPONIBLES;
#     se invocan por su description y se encadenan entre sí. No fuerzan su uso.
#
# Solo corre en la nube: en local conviene instalar el plugin real de Superpowers.
# El JSON del hook es lo ÚNICO en stdout; todos los logs van a stderr. Al final
# emite reloadSkills:true para cargarlas en ESTA misma sesión (clave en la web,
# donde el contenedor se re-clona limpio en cada sesión).

# ── Knobs ────────────────────────────────────────────────────────────────────
OWNER="obra"
REPO="Superpowers"
REF="main"
# ─────────────────────────────────────────────────────────────────────────────

TARBALL="https://codeload.github.com/$OWNER/$REPO/tar.gz/refs/heads/$REF"
SKILLS_DIR="$CLAUDE_PROJECT_DIR/.claude/skills"

log() { echo "[sync-superpowers] $*" >&2; }

# En local no hacemos nada (el plugin nativo es la vía allí).
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  log "no-cloud: skip (usa el plugin real en local)"
  exit 0
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Descarga a archivo (no por pipe) para detectar fallo de red con claridad.
if ! curl -sSL "$TARBALL" -o "$TMP/sp.tar.gz"; then
  log "✗ descarga del tarball falló; skip"
  exit 0
fi
if ! tar -xzf "$TMP/sp.tar.gz" -C "$TMP" --strip-components=1 2>/dev/null; then
  log "✗ extracción del tarball falló; skip"
  exit 0
fi
if [ ! -d "$TMP/skills" ]; then
  log "✗ el tarball no trae skills/; skip"
  exit 0
fi

mkdir -p "$SKILLS_DIR"
n=0
for s in "$TMP"/skills/*/; do
  [ -f "${s}SKILL.md" ] || continue            # ignora dirs sin SKILL.md
  name=$(basename "$s")
  rm -rf "$SKILLS_DIR/$name"                    # idempotente, sin huérfanos
  cp -a "$s" "$SKILLS_DIR/$name"               # preserva references/ y scripts/ ejecutables
  n=$((n + 1))
  log "✓ $name"
done

log "materializadas $n skills de $OWNER/$REPO (nombres planos, sin inyección)"
# Recarga en ESTA sesión solo si materializamos algo. Único contenido en stdout.
[ "$n" -gt 0 ] && printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","reloadSkills":true}}\n'
exit 0
