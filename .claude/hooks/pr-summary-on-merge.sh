#!/usr/bin/env bash
# PostToolUse hook (matcher: mcp__github__merge_pull_request) — TEMPLATE repo-agnóstico.
#
# Tras mergear un PR vía la herramienta MCP de GitHub, le recuerda a Claude que
# reescriba el título y el cuerpo de ESE PR con el formato estándar de resumen
# (ver el CLAUDE.md del repo → sección "Resumen de PR al mergear"). El hook NO
# genera el resumen — eso lo hace Claude, que tiene el contexto del PR—; solo
# inyecta la instrucción (con el número de PR ya resuelto) vía additionalContext.
#
# Cópialo a .claude/hooks/pr-summary-on-merge.sh en el repo consumidor y
# regístralo como PostToolUse en .claude/settings.json con el matcher de arriba
# (ver el README de claude-skills, "Cableado del resumen de PR al mergear").
#
# Entrada: payload JSON del evento PostToolUse por stdin.
# Salida:  JSON con hookSpecificOutput.additionalContext por stdout (no bloquea).

input="$(cat)"

# El número de PR viene en tool_input. El servidor MCP usa "pullNumber";
# aceptamos "pull_number" por robustez ante cambios de esquema.
pr="$(printf '%s' "$input" | jq -r '.tool_input.pullNumber // .tool_input.pull_number // empty' 2>/dev/null)"

# Sin número de PR (payload inesperado): no inyectamos nada.
[ -z "$pr" ] && exit 0

msg="$(cat <<EOF
Acabas de mergear el PR #${pr}. Política del repo ("Resumen de PR al mergear", en CLAUDE.md): ahora reescribe POR COMPLETO el título y el cuerpo de ese PR con mcp__github__update_pull_request usando la plantilla estándar: ## Resumen (1-3 frases), ## Índice de implementaciones (lista numerada con archivos/commits clave), ## PRs relacionados (autolinkea los #NNN que detectes en commits/contexto; omite si no hay) y ## Verificación. El título debe ser un resumen conciso, imperativo y con scope. Hazlo directamente, sin preguntar, salvo que el merge haya fallado.
EOF
)"

jq -n --arg c "$msg" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
