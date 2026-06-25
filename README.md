# claude-skills

Skills compartidos de Claude Code (ver [`CLAUDE.md`](CLAUDE.md) para convenciones).

## Skills

| Skill | Qué hace |
|-------|----------|
| [battlemap](battlemap/) | Genera battlemaps top-down para D&D/TTRPG con Gemini Image (prompt engineering + edición iterativa); fallback por API directo (`scripts/gen-image.sh`) si el MCP no está; integración opcional con QuestKeep |
| [dnd-compendium](dnd-compendium/) | Hace crecer libro a libro un compendio de referencia D&D como grafo graphify persistente (lore, dominios, géneros de horror, darklords, criaturas), fusionando por entidad canónica — la "musa" de inspiración, separada del mundo de campaña — **requiere la skill `graphify` al lado + un clon de `questkeep` (renderers del ETL); el grafo vive en `questkeep/compendium/`** |
| [dnd-worldbuilder](dnd-worldbuilder/) | Genera y mejora entidades narrativas de campañas D&D (NPCs, ciudades, lugares, quests, combates, items) con principios profesionales + framework Encounter Axis — **consulta `dnd-compendium` (la musa) como primera fuente de inspiración (Paso 0.5) si está disponible** |
| [dream](dream/) | Consolidación de memoria estilo "auto-dream": escanea transcripciones de sesiones y fusiona learnings en archivos de memoria persistentes |
| [garantias-deck](garantias-deck/) | Genera el deck HTML+PDF del estado de garantías ABIERTAS de Domus para la junta operativa, con datos en vivo de Supabase |
| [graphify](graphify/) | Convierte cualquier carpeta (código, docs, papers, imágenes) en un grafo de conocimiento con detección de comunidades + audit trail → HTML interactivo, JSON (GraphRAG) y reporte — **requiere el paquete Python `graphifyy` (PyPI), que el SKILL.md auto-instala vía `pip` (necesita egress a PyPI)** |
| [halo-post-session](halo-post-session/) | Actualiza las BDs de la campaña D&D Halo después de una sesión jugada (NPCs conocidos, quests avanzadas, items obtenidos) |
| [halo-session-prep](halo-session-prep/) | Prepara fichas de sesión para la campaña D&D Halo y las guarda en Supabase — **requiere `dnd-worldbuilder` al lado; consulta `dnd-compendium` (la musa) primero para todo elemento nuevo** |
| [huashu-design](huashu-design/) | 花叔Design: hi-fi prototyping en HTML con principios anti-AI-slop (mockups, animaciones, decks, demos, app prototypes) |
| [programa-semanal](programa-semanal/) | Genera el Programa Semanal de coordinación de tareas estratégicas de un desarrollo de Domus (Gran Bosco por defecto): un calendario PDF Lun-Vie por actor (uno por supervisor/gerente) con datos en vivo de Supabase |
| [resultados-proveedores](resultados-proveedores/) | Genera el deck mensual "Análisis de Resultados" por proveedor de garantías de Domus, con datos en vivo de Supabase |
| [supabase-health](supabase-health/) | Monitoreo proactivo de salud del Supabase de Domus (CPU/IO/disco/RAM/queries) con alerta a WhatsApp vía n8n |
| [tareas-deck](tareas-deck/) | Genera el deck HTML+PDF de focos de atraso de tareas de obra de un desarrollo Domus (default Adara) |
| [test-web](test-web/) | Tests E2E con Playwright para verificar cambios de frontend en el navegador (repo-agnóstico) |
| [ui-ux-pro-max](ui-ux-pro-max/) | Design intelligence: 67 estilos, 96 paletas, 57 font pairings, 99 UX guidelines, 25 chart types, 13 stacks |

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
