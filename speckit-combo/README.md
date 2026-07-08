# speckit-combo — spec-kit vendorizado + weave con superpowers

Subsistema **vendorizado** de [github/spec-kit](https://github.com/github/spec-kit)
para Spec-Driven Development, pineado a una versión conocida y con un *weave* a la
disciplina de ingeniería de [`obra/Superpowers`](https://github.com/obra/Superpowers).

A diferencia de las skills de terceros (que se bajan en vivo vía
`sync-upstream-skills.sh`), spec-kit **se vendoriza** porque: (a) le montamos un weave
encima —parchear una dependencia viva es frágil—, (b) es un CLI que scaffoldea un
subsistema, no un repo con layout `skills/*/`, y (c) es una base de workflow que
queremos **estable y offline** en la nube efímera. Ver el carve-out en `CLAUDE.md`.

## Qué contiene

```
speckit-combo/
  VERSION                         # versión pineada + separación core/weave
  README.md                       # este archivo
  payload/                        # lo que el hook materializa en el repo destino
    skills/                       # 10 skills speckit-* (CORE, intactas)
    specify/                      # .specify/ (CORE) + el weave
      templates/                  #   *.md core intactos
        overrides/                #   Prioridad 1 — libre para overrides del proyecto
      scripts/bash/*.sh           #   core (bash + git en runtime; sin CLI, sin Python*)
      workflows/ integrations/    #   core
      memory/constitution.md      #   ★ EL WEAVE (Artículos I–III + Governance)
      init-options.json integration.json
```

`*` python3 solo como *fallback* opcional de parseo JSON en `common.sh`.

## El weave

Vive en `payload/specify/memory/constitution.md`: Artículos concretos de
**TDD (RED-GREEN-REFACTOR)**, **verificación antes de completar** y **code review por
severidad**, que referencian las skills de superpowers *"si están disponibles"* (degrada
con gracia si no lo están). `/speckit-constitution`, `/speckit-plan` y
`/speckit-implement` leen la constitución como governance → el weave se propaga por
todas las fases sin tocar ningún archivo core.

Requiere que superpowers esté sincronizado aparte (`sync-upstream-skills.sh` con
`obra/Superpowers`). Sin él, el weave sigue funcionando como disciplina inline.

## Cómo se materializa en un repo destino

Vía el hook `hooks/sync-speckit.sh` (ver la sección de cableado en el `README.md` raíz).
El hook baja este payload de claude-skills cada sesión de la nube y lo copia con una
**partición durable/regenerable**: el core se sobrescribe siempre; `memory/constitution.md`
y `specs/` **nunca** se pisan si ya existen (contenido del proyecto).

## Cómo actualizar la vendorización

```bash
# 1. Regenera el core con la versión nueva en un dir scratch
uvx --from git+https://github.com/github/spec-kit.git@<nuevo-tag> \
    specify init /tmp/sk --integration claude --ignore-agent-tools --force

# 2. Sobrescribe SOLO el core (deja intacto memory/constitution.md = el weave)
cp -a /tmp/sk/.claude/skills/.  speckit-combo/payload/skills/
cp -a /tmp/sk/.specify/templates/. speckit-combo/payload/specify/templates/   # respeta overrides/
cp -a /tmp/sk/.specify/scripts/.   speckit-combo/payload/specify/scripts/
cp -a /tmp/sk/.specify/workflows/. speckit-combo/payload/specify/workflows/
cp -a /tmp/sk/.specify/integrations/. speckit-combo/payload/specify/integrations/
cp /tmp/sk/.specify/*.json speckit-combo/payload/specify/

# 3. Revisa el diff (¿renombraron algún template? ¿cambió el layout?), actualiza VERSION
git diff speckit-combo/

# 4. Commit + push. Cada repo consumidor lo recibe la próxima sesión.
```

Regla de oro: **nunca parchees archivos que spec-kit posee** (skills core, scripts,
templates core). El weave es aditivo y vive en `memory/constitution.md`, así que los
updates son un overwrite mecánico del core + revisar el diff.
