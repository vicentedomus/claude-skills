# claude-skills

Claude Code skills versionadas para usar entre sesiones y en Claude Code web.

## Skills

| Skill | Qué hace | Requiere |
|-------|----------|----------|
| [battlemap](battlemap/) | Genera battlemaps top-down para D&D/TTRPG con Gemini Image (prompt engineering + edición iterativa) | MCP `gemini-image`; opcional Supabase (integración QuestKeep) |
| [dnd-worldbuilder](dnd-worldbuilder/) | Genera y mejora entidades narrativas de campañas D&D (NPCs, ciudades, lugares, quests, combates, items) con principios de narración profesional | MCP `supabase` |
| [halo-session-prep](halo-session-prep/) | Prepara fichas de sesión para la campaña Halo y las guarda en Supabase | MCP `supabase`; **requiere `dnd-worldbuilder` instalada al lado** |
| [halo-post-session](halo-post-session/) | Actualiza las BDs de la campaña Halo después de una sesión jugada | MCP `supabase` |
| [test-web](test-web/) | Tests E2E con Playwright para verificar cambios de frontend en el navegador | — |
| [huashu-design](huashu-design/) | Skill de diseño (instalada vía `npx skills`) | ver su README |

## Notas de uso

- **`halo-session-prep` depende de `dnd-worldbuilder`:** delega la generación narrativa de NPCs nuevos, reskins de items y diseño de combates vía rutas relativas (`../dnd-worldbuilder/references/...`). Instala ambas juntas.
- **Las skills `halo-*` son específicas de la campaña Halo** (project_id de Supabase + `campaign_slug='halo'` hardcoded). `dnd-worldbuilder` y `battlemap` son agnósticas de campaña.
- **MCPs en Claude Code web:** `battlemap` necesita el MCP `gemini-image`, y las skills de D&D el MCP `supabase`, configurados en tu entorno web. Los archivos generados en web viven en el sandbox (efímero) — descarga lo que quieras conservar.

## Estructura

Cada skill vive en su carpeta top-level con `SKILL.md` + `assets/`/`references/`/`evals/` según aplique. Ver [CLAUDE.md](CLAUDE.md) para el flujo de instalación de skills externas.
