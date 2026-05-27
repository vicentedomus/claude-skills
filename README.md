# claude-skills

Skills compartidos de Claude Code (ver `CLAUDE.md` para convenciones).

## `hooks/`

Hooks de shell compartidos y fuente de verdad central. Otros repos los
sincronizan desde aquí vía su propio `sync-hooks.sh` (que descarga cada hook
desde `https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/<archivo>.sh`).

- `post-plan-todos.sh` — PostToolUse (matcher `ExitPlanMode`): al aprobar un
  plan con varios pasos, le inyecta a Claude la instrucción de crear una lista
  `TodoWrite` que lo refleje.
