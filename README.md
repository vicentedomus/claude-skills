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
| [`sync-superpowers.sh`](hooks/sync-superpowers.sh) | **Template repo-agnóstico.** SessionStart hook que materializa en `.claude/skills/` **todas** las skills de [`obra/Superpowers`](https://github.com/obra/Superpowers) vía tarball de codeload (solo en la nube; en local va el plugin nativo). Nombres planos, sin inyección agresiva. Knobs `OWNER/REPO/REF`. Ver el cableado abajo. |
| [`ponytail-mode.sh`](hooks/ponytail-mode.sh) | **Template repo-agnóstico.** Un solo script en TRES eventos (SessionStart/UserPromptSubmit/SubagentStart) que mantiene el "modo ponytail" **siempre activo**, como plantea el SKILL.md de [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) (MIT): inyecta el *ladder* como contexto persistente, conmuta con `/ponytail lite\|full\|ultra\|off` y apaga con "stop ponytail". Bash puro (sin node, sin código de terceros por prompt); lee el ladder de la skill `ponytail` si está sincronizada, o de un fallback embebido. Ver el cableado abajo. |
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

## Cableado de superpowers en cualquier repo

Para cargar **todas** las skills de [`obra/Superpowers`](https://github.com/obra/Superpowers)
(brainstorming, test-driven-development, writing-skills, …) en cada sesión de la
nube. Es un SessionStart hook independiente del de skills compartidas — se cablea
**en paralelo** a `sync-skills.sh` (dos bloques `SessionStart`). Cuatro pasos:

**1. Copia el template del hook** a `.claude/hooks/sync-superpowers.sh` y dale el
bit ejecutable:

```bash
mkdir -p .claude/hooks
curl -sSL https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/sync-superpowers.sh \
  -o .claude/hooks/sync-superpowers.sh
chmod +x .claude/hooks/sync-superpowers.sh
```

**2. Regístralo como SessionStart** en `.claude/settings.json` (comiteado). Si ya
tienes el bloque de `sync-skills.sh`, este es un **segundo** objeto en el array
`SessionStart`:

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
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/sync-superpowers.sh\"",
            "statusMessage": "Materializando skills de Superpowers (tarball)..."
          }
        ]
      }
    ]
  }
}
```

**3. Ignora las skills materializadas** (las comparte el `.gitignore` con
`sync-skills.sh`; si aún no está):

```
.claude/skills/
```

**4. Comitea el hook y abre PR.** En la siguiente sesión web el hook corre solo y
deja las skills disponibles (emite `reloadSkills:true`, así cargan en ESA misma
sesión).

### Notas

- **Solo nube.** El hook corre únicamente con `CLAUDE_CODE_REMOTE=true`. En local
  conviene instalar el **plugin nativo de Superpowers** (la inyección agresiva del
  plugin sí aplica allí); el hook hace `skip`.
- **Sin whitelist:** materializa el set completo de `skills/` del tarball. A
  diferencia de `sync-skills.sh`, no hay `.txt` per-repo — es todo o nada.
- **Rama `main`, sin pin:** trae siempre lo último de upstream (posible drift
  entre sesiones). Cambia `REF` arriba del hook para fijar a un tag/commit.
- **Nombres planos** (`brainstorming`, …; sin prefijo `superpowers:`) y **sin
  inyección agresiva**: quedan disponibles por su `description` y se encadenan por
  sus cross-referencias, pero no se fuerzan en cada mensaje.

## Cableado de ponytail always-on en cualquier repo

A diferencia de una skill "disponible" (opt-in, se activa al invocarla), esto
mantiene el **modo ponytail SIEMPRE ACTIVO** tal como plantea su SKILL.md: lazy
senior dev, *active every response*, default `full`, conmutable y con off-switch.
Lo logra una capa de hooks en bash que **inyecta el ladder como contexto** (mismo
canal `additionalContext` que el resto) — sin node, sin correr código de terceros
en cada prompt. Un solo script registrado en **tres** eventos. Cuatro pasos:

**1. Copia el template del hook** a `.claude/hooks/ponytail-mode.sh` y dale el bit
ejecutable:

```bash
mkdir -p .claude/hooks
curl -sSL https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/ponytail-mode.sh \
  -o .claude/hooks/ponytail-mode.sh
chmod +x .claude/hooks/ponytail-mode.sh
```

**2. Regístralo en `.claude/settings.json`** en **tres** eventos (el mismo script
ramifica por `hook_event_name`):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/ponytail-mode.sh\"",
            "statusMessage": "Activando modo ponytail..."
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/ponytail-mode.sh\""
          }
        ]
      }
    ],
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/ponytail-mode.sh\""
          }
        ]
      }
    ]
  }
}
```

> Si ya tienes bloques `SessionStart` (p. ej. `sync-skills.sh`), añade el de
> ponytail como **otro objeto** del array, no lo reemplaces.

**3. Ignora el flag de estado** en `.gitignore` (lo escribe el hook para recordar
el nivel activo dentro de la sesión):

```
.claude/.ponytail-mode
```

**4. (Recomendado) Sincroniza también la skill `ponytail`** vía el sync de skills
upstream. Si está en `.claude/skills/ponytail/SKILL.md`, el hook inyecta **ese
cuerpo verbatim** (cero drift); si no, usa un ladder embebido de fallback. Así la
skill es la única fuente de verdad y el hook solo la mantiene prendida.

### Uso

- Por defecto arranca en `full` cada sesión. Conmuta el nivel con `/ponytail lite`,
  `/ponytail full`, `/ponytail ultra`. Apaga con `/ponytail off`, `stop ponytail`
  o `normal mode` (frase exacta, para no apagarlo a media tarea por un "normal
  mode" incidental).
- El nivel persiste en `.claude/.ponytail-mode` durante la sesión; en la nube se
  re-clona limpio, así que cada sesión vuelve al default.

### Notas

- **Requiere `jq`** (igual que `pr-summary-on-merge.sh`). Si falta, el hook no
  bloquea: no emite contexto.
- **Cambia el default** con la env var `PONYTAIL_DEFAULT_MODE` (`lite|full|ultra`).
- **Límite honesto:** el hook *inyecta* el ruleset con fuerza, pero no obliga a
  nivel de token — el modelo igual debe honrarlo (misma base que ponytail nativo).
- **Local / fidelidad total:** para statusline + modos del plugin original,
  instala el **plugin nativo de ponytail** en local; este template cubre el
  always-on en la nube, donde los plugins están desactivados.

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
