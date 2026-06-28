# claude-skills

This repo stores Claude Code skills for use across sessions.

## Structure

Each skill lives in its own top-level folder named after the skill:

```
<skill-name>/
  SKILL.md        ← required: skill definition loaded by Claude Code
  ...             ← any additional assets, references, scripts
```

Example:
```
test-web/
  SKILL.md
huashu-design/
  SKILL.md
  assets/
  references/
  scripts/
```

## Installing a new skill

```bash
npx skills add <github-owner>/<repo>
```

After installation, if the tool placed the skill under `.agents/skills/<name>/`, move it to the root:

```bash
git mv .agents/skills/<name> <name>
# remove .agents/ if now empty
git rm -r .agents/
```

Commit, push to a branch, open a PR, and merge to main.

## Maintain the README skills index

`README.md` carries a table of every skill in the repo. **Whenever a skill is
added, renamed, or removed, update that table in the same PR** — don't leave it
for later. For each new skill, the row should include:

- The skill name linked to its folder (e.g. `[battlemap](battlemap/)`)
- A **one-line purpose**, distilled from the skill's `SKILL.md` frontmatter
  `description` (don't paste the full description — trim to one readable line)
- Any **cross-skill dependency** worth flagging (e.g. `halo-session-prep`
  requires `dnd-worldbuilder` installed alongside)
- Any MCP server the skill requires, if non-obvious

This applies regardless of how the skill arrived: migrated from another
location, installed via `npx skills`, or written from scratch in this repo.
Keep the table alphabetical for easy scanning.

**Excepción — skills de upstream (terceros):** las skills de repos de terceros
(`obra/Superpowers`, `DietrichGebert/ponytail`, …) **no** se vendorizan en este
repo ni entran al índice de skills. Se distribuyen vía el hook-template
`hooks/sync-upstream-skills.sh` (cada repo consumidor lista sus fuentes y skills en
`.claude/upstream-skills.txt`; el hook las baja por tarball en cada sesión de la
nube) y se documentan solo en la sección `hooks/` del README. No agregues filas por
cada una al índice de skills curadas.

## Resumen de PR al mergear

Cuando **tú (Claude) mergeas un PR** vía `mcp__github__merge_pull_request`, un hook
`PostToolUse` (`.claude/hooks/pr-summary-on-merge.sh`) te recuerda automáticamente,
con el número de PR ya resuelto, que actualices ese PR. **El hook no escribe el
resumen** — lo escribes tú, que tienes el contexto. Inmediatamente tras el merge,
**sobrescribe por completo** el título y el cuerpo de ese PR con
`mcp__github__update_pull_request`, en español:

- **Título**: resumen conciso, imperativo y con scope (ej. "hooks: template
  sync-skills repo-agnóstico + doc de cableado").
- **Cuerpo** (Markdown), en este orden:
  1. `## Resumen` — 1-3 frases: qué se hizo y por qué.
  2. `## Índice de implementaciones` — lista **numerada**; cada ítem = feature +
     descripción breve + archivos/commits clave.
  3. `## PRs relacionados` — los `#NNN` que detectes en commits/contexto (GitHub
     los autolinkea). Omite la sección si no hay.
  4. `## Verificación` — `bash -n` de los hooks, validación de SKILL.md, etc.
  - Footer: el enlace de sesión `https://claude.ai/code/session_…` que ya usas en
    commits y PRs.

Reglas: descarta el contenido previo (overwrite total), hazlo sin preguntar salvo
que el merge haya fallado, y aplica a cualquier PR que mergees (normalmente a `main`).

## skills-lock.json

Managed automatically by `npx skills`. Do not edit manually.
