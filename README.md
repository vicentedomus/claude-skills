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
| [test-web](test-web/) | Tests E2E con Playwright para verificar cambios de frontend en el navegador (repo-agnóstico) — **trae el helper `playwright.remote-env.ts` para correr detrás del proxy de Claude Code on the web (CDN/backend reales, login E2E)** |
| [ui-ux-pro-max](ui-ux-pro-max/) | Design intelligence: 67 estilos, 96 paletas, 57 font pairings, 99 UX guidelines, 25 chart types, 13 stacks |

## `hooks/`

Hooks de shell compartidos y fuente de verdad central. Otros repos los
sincronizan desde aquí vía su propio `sync-hooks.sh` (que descarga cada hook
desde `https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/<archivo>.sh`).

| Hook | Qué hace |
|------|----------|
| [`sync-skills.sh`](hooks/sync-skills.sh) | **Template repo-agnóstico.** SessionStart hook que materializa en `.claude/skills/` las skills listadas en `.claude/skills.txt`, bajándolas de este repo. Tarball de codeload en la nube, `git clone` en local. Ver el cableado abajo. |
| [`pr-summary-on-merge.sh`](hooks/pr-summary-on-merge.sh) | **Template repo-agnóstico.** PostToolUse hook (matcher `mcp__github__merge_pull_request`) que, al mergear un PR, le recuerda a Claude reescribir título+cuerpo de ese PR con el formato estándar de resumen. No escribe el resumen, solo inyecta la instrucción con el `#NNN` resuelto. Ver el cableado abajo. |

## Cableado del sync de skills en cualquier repo

Para que un repo consumidor cargue skills de aquí en cada sesión (incluido
Claude Code on the web, donde el contenedor se re-clona limpio cada vez), se
cablea un SessionStart hook. Cinco pasos:

**1. Copia el template del hook** a `.claude/hooks/sync-skills.sh` y dale el bit
ejecutable:

```bash
mkdir -p .claude/hooks
curl -sSL https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/sync-skills.sh \
  -o .claude/hooks/sync-skills.sh
chmod +x .claude/hooks/sync-skills.sh
```

**2. Declara qué skills quieres** en `.claude/skills.txt` (whitelist; una por
línea, `#` para comentarios). Es el ÚNICO knob per-repo: lo que no esté listado
no se materializa en disco → no carga en contexto.

```
# .claude/skills.txt
test-web
ui-ux-pro-max
```

**3. Regístralo como SessionStart** en `.claude/settings.json` (comiteado, no en
`settings.local.json` — en la web solo lo versionado sobrevive entre sesiones):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/sync-skills.sh\"",
            "statusMessage": "Sincronizando skills desde claude-skills..."
          }
        ]
      }
    ]
  }
}
```

**4. Ignora las skills materializadas** — no se comitean, se regeneran cada
sesión. En `.gitignore`:

```
.claude/skills/
```

**5. (Opcional) Comitea el hook y el whitelist**, y abre PR. En la siguiente
sesión web el hook corre solo y deja las skills disponibles (emite
`reloadSkills:true`, así cargan en ESA misma sesión).

### Por qué tarball en la web y `git clone` en local

En Claude Code on the web, `git clone`/`git fetch` se reescriben a un **relay de
git scopeado** que solo autoriza los repos del scope de sesión — da **403 hasta
para repos propios** (`claude-skills` incluido), ni por dueño ni por fase. Las
descargas HTTPS normales sí pasan, así que en la nube el hook baja el **tarball
de `codeload.github.com`** (árbol completo a un commit consistente, con
`scripts/`/`references/` y bit ejecutable preservados vía `cp -a`). En local, sin
relay scopeado, usa `git clone`. Si todo falla, cae a bajar solo cada `SKILL.md`
por `curl` a `raw.githubusercontent.com` (sin assets) como último recurso.

> **Requisito**: el repo de skills debe ser **público** (el tarball de codeload y
> el fallback de raw.github van sin auth). Cambia `OWNER`/`REPO`/`REF` arriba del
> hook si lo sirves desde otro repo.

## Cableado del resumen de PR al mergear en cualquier repo

Para que, al mergear un PR vía la tool MCP de GitHub, Claude reescriba
automáticamente el título+cuerpo de ese PR con un formato de resumen consistente.
Tres pasos:

**1. Copia el template** a `.claude/hooks/pr-summary-on-merge.sh` y dale el bit
ejecutable:

```bash
mkdir -p .claude/hooks
curl -sSL https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/pr-summary-on-merge.sh \
  -o .claude/hooks/pr-summary-on-merge.sh
chmod +x .claude/hooks/pr-summary-on-merge.sh
```

**2. Regístralo como PostToolUse** en `.claude/settings.json` (comiteado), con el
matcher de la tool de merge:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__github__merge_pull_request",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/pr-summary-on-merge.sh\"",
            "statusMessage": "Preparando resumen del PR mergeado..."
          }
        ]
      }
    ]
  }
}
```

**3. Documenta la convención** en el `CLAUDE.md` del repo, bajo una sección
"Resumen de PR al mergear" (qué secciones lleva el cuerpo, en qué idioma, footer
de sesión, cualquier regla propia del repo). El hook solo **recuerda**; el formato
concreto lo define el `CLAUDE.md` y lo redacta Claude, que tiene el contexto.

El hook lee el `pullNumber` del payload del evento e inyecta la instrucción vía
`additionalContext` (no bloquea el merge). Si el payload no trae número de PR, no
emite nada. Necesita `jq` en el entorno.

### Hooks retirados

- `post-plan-todos.sh` — PostToolUse (matcher `ExitPlanMode`). Retirado: era
  estructuralmente incompatible con extended thinking. El turno con
  `ExitPlanMode` viene precedido de un bloque `thinking`, y al inyectar
  `additionalContext` el harness reescribe ese mensaje; la API lo rechaza con
  `400 … thinking or redacted_thinking blocks in the latest assistant message
  cannot be modified`. La conducta (armar una lista `TodoWrite` al aprobar un
  plan) se movió a una instrucción permanente en el `CLAUDE.md` de cada repo
  consumidor.
