# claude-skills

Skills compartidos de Claude Code (ver `CLAUDE.md` para convenciones).

## `hooks/`

Hooks de shell compartidos y fuente de verdad central. Otros repos los
sincronizan desde aquí vía su propio `sync-hooks.sh` (que descarga cada hook
desde `https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/<archivo>.sh`).

_(Sin hooks compartidos por ahora.)_

### Hooks retirados

- `post-plan-todos.sh` — PostToolUse (matcher `ExitPlanMode`). Retirado: era
  estructuralmente incompatible con extended thinking. El turno con
  `ExitPlanMode` viene precedido de un bloque `thinking`, y al inyectar
  `additionalContext` el harness reescribe ese mensaje; la API lo rechaza con
  `400 … thinking or redacted_thinking blocks in the latest assistant message
  cannot be modified`. La conducta (armar una lista `TodoWrite` al aprobar un
  plan) se movió a una instrucción permanente en el `CLAUDE.md` de cada repo
  consumidor.
