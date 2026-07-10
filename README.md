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
| [speckit-with-superpowers](speckit-with-superpowers/) | Runbook always-on que dispara el flujo **spec-driven** del combo spec-kit + superpowers cableado en el repo: conduce las fases-compuerta (`specify → plan → tasks → implement`) con checkpoint por artefacto, injerta el rigor de superpowers (TDD/verificación/review) vía el weave de la constitución y respeta ponytail — **complementa el combo vendorizado en [`speckit-combo/`](speckit-combo/) + su hook `sync-speckit.sh`** |
| [supabase-health](supabase-health/) | Monitoreo proactivo de salud del Supabase de Domus (CPU/IO/disco/RAM/queries) con alerta a WhatsApp vía n8n |
| [tareas-deck](tareas-deck/) | Genera el deck HTML+PDF de focos de atraso de tareas de obra de un desarrollo Domus (default Adara) |
| [test-web](test-web/) | Tests E2E con Playwright para verificar cambios de frontend en el navegador (repo-agnóstico); tests **siempre efímeros** (crear→correr→borrar, nunca se guardan), lo único que persiste son **gotchas en dos niveles** (generales en `references/gotchas.md`; repo-específicos en `tests/QA-NOTES.md` del repo consumidor) — **trae el helper `playwright.remote-env.ts` para correr detrás del proxy de Claude Code on the web (CDN/backend reales, login E2E)** |
| [ui-ux-pro-max](ui-ux-pro-max/) | Design intelligence: 67 estilos, 96 paletas, 57 font pairings, 99 UX guidelines, 25 chart types, 13 stacks |

## `hooks/`

Hooks de shell compartidos y fuente de verdad central. Otros repos los
sincronizan desde aquí vía su propio `sync-hooks.sh` (que descarga cada hook
desde `https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/<archivo>.sh`).

> **Requisito de entorno (clave en Claude Code on the web): la sesión debe
> rootear en el repo, no en un padre.** Claude Code carga los hooks de
> `.claude/settings.json` solo desde `$CLAUDE_PROJECT_DIR` (el repo rooteado). Si
> el entorno rootea en un **padre multi-repo** (p. ej. `/home/user` con varios
> repos al lado), esos repos entran como *additional directories*: se carga su
> `CLAUDE.md` pero **no sus hooks** → los SessionStart **no disparan** (ni sync ni
> ponytail). Diagnóstico: revisa `.claude/.hooks.log`; si no existe, el hook no
> corrió. Fix: rootear el environment en el repo. (Para trabajo cruzado entre
> repos, ese entorno multi-repo sirve, pero ahí los hooks per-repo no corren.)

| Hook | Qué hace |
|------|----------|
| [`sync-skills.sh`](hooks/sync-skills.sh) | **Template repo-agnóstico.** SessionStart hook que materializa en `.claude/skills/` las skills listadas en `.claude/skills.txt`, bajándolas de este repo. `git clone` vía relay (con reintento) primero, tarball de codeload como fallback de nube, `raw` SKILL.md como último recurso. Ver el cableado abajo. |
| [`sync-upstream-skills.sh`](hooks/sync-upstream-skills.sh) | **Template repo-agnóstico.** SessionStart hook que materializa en `.claude/skills/` skills de repos de **terceros** con layout `skills/*/` ([`obra/Superpowers`](https://github.com/obra/Superpowers), [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail), …) vía `git clone` con fallback a tarball de codeload (solo nube; en local, plugins nativos). Manejado por `.claude/upstream-skills.txt`: **doble whitelist** — qué repos clonar y qué skills de cada uno. Nombres planos, sin inyección agresiva. Ver el cableado abajo. |
| [`ponytail-mode.sh`](hooks/ponytail-mode.sh) | **Template repo-agnóstico.** Un solo script en TRES eventos (SessionStart/UserPromptSubmit/SubagentStart) que mantiene el "modo ponytail" **siempre activo**, como plantea el SKILL.md de [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) (MIT): inyecta el *ladder* como contexto persistente, conmuta con `/ponytail lite\|full\|ultra\|off` y apaga con "stop ponytail". Bash puro (sin node, sin código de terceros por prompt); lee el ladder de la skill `ponytail` si está sincronizada, o de un fallback embebido. Ver el cableado abajo. |
| [`pr-summary-on-merge.sh`](hooks/pr-summary-on-merge.sh) | **Template repo-agnóstico.** PostToolUse hook (matcher `mcp__github__merge_pull_request`) que, al mergear un PR, le recuerda a Claude reescribir título+cuerpo de ese PR con el formato estándar de resumen. No escribe el resumen, solo inyecta la instrucción con el `#NNN` resuelto. Ver el cableado abajo. |
| [`sync-speckit.sh`](hooks/sync-speckit.sh) | **Template repo-agnóstico.** SessionStart hook que materializa el **combo spec-kit vendorizado** ([`speckit-combo/`](speckit-combo/): [github/spec-kit](https://github.com/github/spec-kit) pineado + weave con superpowers) — skills `speckit-*` + scaffold `.specify/`. Mismo transporte (git clone→codeload). **Partición durable/regenerable:** el core se refresca siempre; `.specify/memory/constitution.md` y `specs/` no se pisan (contenido del proyecto). Knob per-repo `.claude/speckit.txt`. Ver el cableado abajo. |

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

### Transporte: `git clone` primero, codeload de fallback, `raw` último recurso

La política de red **varía entre entornos de Claude Code on the web** y la premisa
vieja ("el relay git da 403, codeload pasa") quedó **invertida** en varios: se
observó que el **relay git autoriza el clone** (incluso repos ajenos) mientras
`codeload.github.com` da **403 host-wide** (hasta para tu propio `claude-skills`).
Por eso el hook usa **triple cascada**:

1. **`git clone` (shallow) vía el relay, con reintento** — trae el árbol completo
   con `scripts/`/`references/` (preservados vía `cp -a`). El reintento cubre el
   *flake* transitorio del relay en el cold-start de la sesión.
2. **Fallback de nube: tarball de `codeload.github.com`** — para entornos donde el
   relay sí esté scopeado y codeload pase.
3. **Último recurso: cada `SKILL.md` por `curl` a `raw.githubusercontent.com`**
   (sin assets), para que la skill siga cargando aunque 1 y 2 fallen.

> **Requisito**: el repo de skills debe ser **público** (el tarball de codeload y
> el fallback de raw.github van sin auth). Cambia `OWNER`/`REPO`/`REF` arriba del
> hook si lo sirves desde otro repo.

## Cableado de skills upstream (terceros, con whitelist) en cualquier repo

Para cargar skills de repos **de terceros** con layout `skills/*/` (Superpowers,
ponytail, …) en cada sesión de la nube. Un solo SessionStart hook genérico
manejado por `.claude/upstream-skills.txt`, que es **doble whitelist**: qué repos
clonar y qué skills de cada uno. Se cablea **en paralelo** a `sync-skills.sh` (el
de nuestro propio repo). Cuatro pasos:

**1. Copia el template del hook** a `.claude/hooks/sync-upstream-skills.sh` y dale
el bit ejecutable:

```bash
mkdir -p .claude/hooks
curl -sSL https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/sync-upstream-skills.sh \
  -o .claude/hooks/sync-upstream-skills.sh
chmod +x .claude/hooks/sync-upstream-skills.sh
```

**2. Declara las fuentes** en `.claude/upstream-skills.txt`. Una línea por repo;
los nombres tras el repo son el whitelist de skills (sin nombres = todas). **Una
línea = "clona este repo"; sin línea = no se clona** (whitelist de repos):

```
# .claude/upstream-skills.txt
#   owner/repo[@ref]   [skill1 skill2 ...]
obra/Superpowers          brainstorming test-driven-development writing-skills
DietrichGebert/ponytail   ponytail ponytail-review
```

Si este repo solo quiere ponytail, deja **solo** su línea (Superpowers no se
menciona → no se baja). `@ref` opcional fija rama/tag/commit (sin él, `main`).

**3. Regístralo como SessionStart** en `.claude/settings.json` (comiteado). Si ya
tienes el bloque de `sync-skills.sh`, este es un **segundo** objeto en el array:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/sync-skills.sh\"",
            "statusMessage": "Sincronizando skills desde claude-skills...",
            "timeout": 300
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/sync-upstream-skills.sh\"",
            "statusMessage": "Materializando skills upstream (tarball)...",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

> **`timeout: 300`** en los hooks de sync: bajan tarballs por el proxy, y el
> default (~60s) puede cortarse a media descarga y abortar la cadena `SessionStart`
> (síntoma típico: unas skills sí, otras no, y los hooks siguientes no corren). El
> hook ya acota cada `curl` con `--max-time`, pero dale aire al hook igual.

> **Transporte (doble, resiliente a la política de red).** El hook intenta primero
> `git clone` vía el relay del entorno y, si falla, el tarball de
> `codeload.github.com`. La política de egress **varía entre entornos**: algunos
> autorizan el relay para repos **ajenos** (Superpowers/ponytail no están en el
> scope de la sesión) pero dan **403 en codeload**, y otros al revés. Probar ambos
> evita tener que reconfigurar la política de red del environment. Síntoma del bug
> que esto resuelve: `.hooks.log` con `materializadas 0 skills upstream` pese a que
> el resto del cableado (sync-skills propio, ponytail-mode) sí levantó.

**4. Ignora las skills materializadas** (lo comparte con `sync-skills.sh`; si aún
no está) y **comitea el hook + el `.txt`**:

```
.claude/skills/
```

En la siguiente sesión web el hook corre solo y deja las skills disponibles
(emite `reloadSkills:true`, así cargan en ESA misma sesión).

### Notas

- **Solo nube.** Corre únicamente con `CLAUDE_CODE_REMOTE=true`. En local conviene
  instalar los **plugins nativos** (la inyección agresiva del plugin sí aplica
  allí); el hook hace `skip`.
- **Doble whitelist en un archivo:** la lista de líneas decide los repos; los
  nombres por línea, las skills. Skill pedida que no existe en el repo → log a
  stderr y sigue (no rompe la sesión).
- **Rama `main` por defecto, pin por fuente** con `@ref` (posible drift si sigues
  `main`).
- **Colisión de nombres** entre fuentes (o con las de `sync-skills.sh`) → gana la
  última escrita; el orden del archivo manda.
- **Nombres planos** y **sin inyección agresiva**: quedan disponibles por su
  `description` y se encadenan por sus cross-referencias, pero no se fuerzan en
  cada mensaje. (Para el modo *always-on* de ponytail, ver la sección siguiente.)

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
- **Carve-outs automáticos** (vienen en el contexto inyectado, sin togglear): el
  modo acota la escalera a **código de producción** — los **tests nunca** se
  recortan/omiten para ser mínimos, y en **fase de diseño** (brainstorm/plan) no
  poda: explora primero y aplica la escalera solo al implementar. Resuelve de raíz
  las dos fricciones de combinar ponytail con skills de proceso (Superpowers).

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

## Cableado de spec-kit (combo vendorizado) en cualquier repo

Para dar a un repo el flujo **Spec-Driven Development** de spec-kit **ya tejido** con la
disciplina de superpowers (TDD, verificación, code review), sin correr `specify init` ni
tejer nada a mano. El combo vive vendorizado en [`speckit-combo/`](speckit-combo/) (ver su
README) y se materializa por hook cada sesión de la nube. Cuatro pasos:

**1. Copia el template del hook** a `.claude/hooks/sync-speckit.sh` y dale el bit
ejecutable:

```bash
mkdir -p .claude/hooks
curl -sSL https://raw.githubusercontent.com/vicentedomus/claude-skills/main/hooks/sync-speckit.sh \
  -o .claude/hooks/sync-speckit.sh
chmod +x .claude/hooks/sync-speckit.sh
```

**2. Crea el knob** `.claude/speckit.txt` (su sola existencia activa el combo; vacío =
versión vendorizada por defecto; una línea `@<tag>` pinea otra versión del combo desde
claude-skills):

```
# .claude/speckit.txt — vacío usa el combo de main; @v0.12.8 pinea una versión
```

**3. Regístralo como SessionStart** en `.claude/settings.json` (comiteado). Si ya tienes
un bloque `SessionStart` (p. ej. `sync-skills.sh`), añade este `command` a la misma lista:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/sync-speckit.sh\"",
            "statusMessage": "Materializando combo spec-kit..."
          }
        ]
      }
    ]
  }
}
```

**4. Separa durable de regenerable** en `.gitignore` — el core se regenera cada sesión;
la constitución y las specs son contenido del proyecto y **se comitean**:

```
# regenerable (lo refresca el hook cada sesión)
.claude/skills/
.specify/templates/
.specify/scripts/
.specify/workflows/
.specify/integrations/
.specify/init-options.json
.specify/integration.json
# NO ignorar (contenido del proyecto, se comitea):
#   .specify/memory/constitution.md   ← sembrada con el weave la 1ª vez, luego tuya
#   specs/
```

> **Dependencia del weave (opcional pero recomendada):** los Artículos I–III de la
> constitución referencian skills de superpowers *"si están disponibles"*. Para tenerlas,
> cablea también `sync-upstream-skills.sh` con una línea en `.claude/upstream-skills.txt`:
> ```
> obra/Superpowers   test-driven-development verification-before-completion requesting-code-review
> ```
> Sin superpowers el weave sigue vigente como disciplina inline (degrada con gracia).

Tras esto, en cualquier repo nuevo basta decir *"quiero cablear spec-kit en este repo
desde claude-skills"*: Claude sigue esta receta. Uso: `/speckit-constitution` (completa la
constitución sembrada) → `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` →
`/speckit-implement`. Actualizar la vendorización: ver [`speckit-combo/README.md`](speckit-combo/README.md).

### Hooks retirados

- `post-plan-todos.sh` — PostToolUse (matcher `ExitPlanMode`). Retirado: era
  estructuralmente incompatible con extended thinking. El turno con
  `ExitPlanMode` viene precedido de un bloque `thinking`, y al inyectar
  `additionalContext` el harness reescribe ese mensaje; la API lo rechaza con
  `400 … thinking or redacted_thinking blocks in the latest assistant message
  cannot be modified`. La conducta (armar una lista `TodoWrite` al aprobar un
  plan) se movió a una instrucción permanente en el `CLAUDE.md` de cada repo
  consumidor.
