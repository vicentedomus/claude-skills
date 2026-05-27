#!/usr/bin/env bash
# PostToolUse hook (matcher: ExitPlanMode).
#
# Cuando el usuario APRUEBA un plan en Plan Mode, ExitPlanMode se ejecuta y este
# hook dispara. No crea la lista de tareas él mismo (un hook es solo un comando
# shell): le inyecta a Claude, vía hookSpecificOutput.additionalContext, la
# instrucción de crear una lista TodoWrite que refleje el plan recién aprobado,
# para hacerle seguimiento puntual. Mismo patrón que pr-summary-on-merge.sh.
#
# Solo inyecta cuando el plan tiene VARIOS pasos (>= $MIN_STEPS); en planes
# triviales de un solo paso sale en silencio para no generar ruido.
#
# Entrada: payload JSON del evento PostToolUse por stdin.
# Salida:  JSON con hookSpecificOutput.additionalContext por stdout (no bloquea).
# Umbral de "varios pasos": tunable. >= este número de pasos => crear lista.
MIN_STEPS=2
input="$(cat)"
# ExitPlanMode recibe el plan en tool_input.plan. (Confirmado vía test del payload;
# si algún día cambia el esquema, ajustar este jq.)
plan="$(printf '%s' "$input" | jq -r '.tool_input.plan // empty' 2>/dev/null)"
emit() {
  jq -n --arg c "$1" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
}
multi_step_msg="El usuario acaba de aprobar un plan de trabajo con varios pasos. Antes de \
empezar a ejecutar, crea una lista de tareas dinámica con la herramienta TodoWrite que \
refleje el plan: un ítem por paso accionable, en el mismo orden del plan. Marca el primer \
ítem como in_progress y mantén SIEMPRE exactamente un ítem in_progress a la vez; ve \
marcando completed conforme termines cada paso, y agrega ítems si el plan se ramifica. No \
cierres la tarea con ítems pendientes sin avisarle al usuario. Esta lista es para darle \
seguimiento puntual al plan recién aprobado."
soft_msg="El usuario acaba de aprobar un plan de trabajo. Si el plan tiene varios pasos, \
crea una lista de tareas dinámica con TodoWrite (un ítem por paso accionable, en orden; \
exactamente uno in_progress a la vez; ve actualizando estados) para darle seguimiento. Si \
es un plan trivial de un solo paso, omítela."
# Sin texto de plan (payload inesperado): instrucción suave y dejamos que Claude decida.
if [ -z "$plan" ]; then
  emit "$soft_msg"
  exit 0
fi
# Cuenta de pasos: ítems de lista numerada/viñeta. Si el plan es pura prosa sin
# listas, usamos los encabezados de sección (## / ###) como señal de fases.
items="$(printf '%s' "$plan" | grep -cE '^[[:space:]]*([0-9]+[.)]|[-*+])[[:space:]]+\S')"
if [ "$items" -lt "$MIN_STEPS" ]; then
  headings="$(printf '%s' "$plan" | grep -cE '^[[:space:]]*#{2,}[[:space:]]+\S')"
  [ "$headings" -gt "$items" ] && items="$headings"
fi
# Plan trivial (< MIN_STEPS pasos): no inyectamos nada.
if [ "$items" -lt "$MIN_STEPS" ]; then
  exit 0
fi
emit "$multi_step_msg"
