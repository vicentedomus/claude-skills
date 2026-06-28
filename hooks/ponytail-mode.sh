#!/bin/bash
# Hook TEMPLATE repo-agnóstico — "modo ponytail" SIEMPRE ACTIVO, tal como plantea
# el SKILL.md de ponytail (DietrichGebert/ponytail, MIT): active every response,
# default full, switch /ponytail lite|full|ultra|off, off con "stop ponytail" /
# "normal mode". Reimplementa en bash la capa de hooks del plugin (camino B): sin
# node, sin código de terceros corriendo en cada prompt — solo inyecta texto vía
# additionalContext, el mismo canal de hook que usa sync-skills.sh.
#
# UN SOLO script, registrado en TRES eventos en .claude/settings.json
# (SessionStart, UserPromptSubmit, SubagentStart). Rama por hook_event_name del
# payload de stdin:
#   - SessionStart  → inyecta el "ladder" como contexto persistente (el always-on).
#   - UserPromptSubmit → cambia el nivel con /ponytail … y apaga con "stop ponytail".
#   - SubagentStart → re-inyecta el ladder en cada subagente (si no, corren ciegos).
#
# FUENTE DE VERDAD del ladder: si la skill ponytail está materializada en
# .claude/skills/ponytail/SKILL.md (vía el sync de skills upstream), inyecta SU
# cuerpo verbatim → cero drift. Si no está, cae a un ladder embebido (faithful,
# atribuido a ponytail/MIT) para que el modo funcione aún sin la skill en disco.
#
# El JSON del hook es lo ÚNICO en stdout; los logs van a stderr. Necesita jq.

DEFAULT_MODE="${PONYTAIL_DEFAULT_MODE:-full}"
MODE_FILE="$CLAUDE_PROJECT_DIR/.claude/.ponytail-mode"
SKILL_MD="$CLAUDE_PROJECT_DIR/.claude/skills/ponytail/SKILL.md"

log() { echo "[ponytail-mode] $*" >&2; }

payload="$(cat)"
event="$(printf '%s' "$payload" | jq -r '.hook_event_name // empty' 2>/dev/null)"

echo "$(date -u +%FT%TZ) [ponytail-mode] event=$event skill=$([ -f "$SKILL_MD" ] && echo yes || echo no)" \
  >> "$CLAUDE_PROJECT_DIR/.claude/.hooks.log" 2>/dev/null

read_mode() { [ -f "$MODE_FILE" ] && cat "$MODE_FILE" 2>/dev/null || echo "$DEFAULT_MODE"; }
set_mode()  { mkdir -p "$(dirname "$MODE_FILE")"; printf '%s' "$1" > "$MODE_FILE"; }

# Emite additionalContext en la forma JSON portable (vale para los tres eventos).
emit() {
  jq -cn --arg e "$event" --arg c "$1" \
    '{hookSpecificOutput:{hookEventName:$e, additionalContext:$c}}'
}

# Cuerpo del ladder: la skill en disco (verbatim, sin su frontmatter YAML) o el
# fallback embebido. El awk salta el bloque de frontmatter (entre los dos primeros
# "---") e imprime el resto.
ladder() {
  if [ -f "$SKILL_MD" ]; then
    awk 'n>=2{print} /^---[[:space:]]*$/{n++}' "$SKILL_MD"
  else
    cat <<'EOF'
# Ponytail — lazy senior dev mode (ladder)
ACTIVE EVERY RESPONSE. Lazy = efficient, not careless. The best code is the code
never written. Stop at the first rung that holds:
1. Does this need to exist at all? Speculative need = skip it, say so in one line. (YAGNI)
2. Already in this codebase? Reuse the helper/util/type/pattern that already lives here.
3. Stdlib does it? Use it.
4. Native platform feature covers it? `<input type="date">` over a picker lib, CSS over JS, DB constraint over app code.
5. Already-installed dependency solves it? Use it. Never add a new dep for what a few lines do.
6. Can it be one line? One line.
7. Only then: the minimum code that works.
Mark intentional simplifications with a `ponytail:` comment. No drift back to
over-building. Still active if unsure. Off only: "stop ponytail" / "normal mode".
(Embedded fallback of DietrichGebert/ponytail, MIT — sync the skill for the verbatim source.)
EOF
  fi
}

case "$event" in
  SessionStart)
    mode="$(read_mode)"
    [ -f "$MODE_FILE" ] || set_mode "$mode"      # fija el default la 1ª vez
    [ "$mode" = "off" ] && exit 0                 # off → no inyecta nada
    emit "PONYTAIL MODE: $mode — active every response. Apply the ladder below to
PRODUCTION code until told 'stop ponytail' / 'normal mode'. Levels: lite (light
touch), full (default), ultra (most aggressive).
SCOPE — tests: test code is never 'unnecessary'. Never trim, skip, or delete tests
to be minimal; the ladder governs production code only.
PHASE — design: while brainstorming, planning, or designing, do NOT prune or
pre-shrink. Explore options first; apply the ladder only when writing the implementation.

$(ladder)"
    ;;

  UserPromptSubmit)
    prompt="$(printf '%s' "$payload" | jq -r '.prompt // empty' 2>/dev/null)"
    norm="$(printf '%s' "$prompt" | tr '[:upper:]' '[:lower:]' | sed 's/[[:space:].!?]*$//')"
    if printf '%s' "$norm" | grep -qE '^[/@$]ponytail'; then
      cmd="$(printf '%s' "$norm" | awk '{print $1}' | sed 's/^[@$]/\//; s/^\/ponytail:ponytail/\/ponytail/')"
      arg="$(printf '%s' "$norm" | awk '{print $2}')"
      if [ "$cmd" = "/ponytail-review" ]; then
        set_mode review; emit "PONYTAIL MODE CHANGED — level: review"
      elif [ "$cmd" = "/ponytail" ]; then
        case "$arg" in
          lite|full|ultra) set_mode "$arg"; emit "PONYTAIL MODE CHANGED — level: $arg" ;;
          off)             set_mode off;    emit "PONYTAIL MODE OFF" ;;
          *)               set_mode "$DEFAULT_MODE"; emit "PONYTAIL MODE CHANGED — level: $DEFAULT_MODE" ;;
        esac
      fi
    elif [ "$norm" = "stop ponytail" ] || [ "$norm" = "normal mode" ]; then
      set_mode off; emit "PONYTAIL MODE OFF"
    fi
    # Sin match → no emite nada; el contexto de SessionStart ya persiste.
    ;;

  SubagentStart)
    mode="$(read_mode)"
    [ "$mode" = "off" ] && exit 0
    emit "PONYTAIL MODE: $mode (inherited). Apply the ladder below to PRODUCTION code.
SCOPE — tests: never trim, skip, or delete tests to be minimal. PHASE — design:
explore before pruning; apply the ladder only to implementation code.

$(ladder)"
    ;;

  *)
    exit 0
    ;;
esac
exit 0
