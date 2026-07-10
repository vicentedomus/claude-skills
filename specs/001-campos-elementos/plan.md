# Implementation Plan: Rediseño del conjunto de campos por elemento

**Branch**: `claude/dnd-halo-session-skills-uq7orm` (spec dir `001-campos-elementos`) | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-campos-elementos/spec.md` + los 6 `design-*.md`.

## Summary

Rediseñar qué campos produce cada skill (`dnd-worldbuilder`, `halo-session-prep`) por tipo de
elemento, aprovechando la capa dinámica/interactiva de QuestKeep (`entity_schemas` overlay +
`custom_data` + tipos interactivos). Enfoque técnico co-diseñado (ver `design-*.md`): **genoma de
identidad** desde el grafo, **ancla a catálogo ETL** para statblocks/items (con homebrew en Supabase),
**subtipo→perfil** para tipos heterogéneos, **desenterrar blobs** de prosa en campos estructurados, y
**sembrar cross-links** al nacer. Incluye corregir 2 bugs de catálogo (tesoros/monstruos apuntan a
tablas casi vacías en vez del ETL).

## Technical Context

**Language/Version**: Skills en **Markdown** (`SKILL.md` + `references/*.md`) — el "código" son
instrucciones para Claude, no runtime. Datos vía **SQL/PostgreSQL** (Supabase MCP `execute_sql`).
Lectura de **JSON del ETL** (`questkeep/data/5e/bestiary.json`, `items.json`) desde el clon de questkeep.

**Primary Dependencies**: Supabase MCP · CLI `graphify` (el grafo compendio como musa) · clon de
`questkeep` (ETL + `entity-schema.js`/`FORM_SCHEMAS` como contrato de la UI que consume los campos).

**Storage**: Supabase — `entity_schemas` (overlay por `section`), `custom_data` jsonb en las 6 tablas
de entidad (`npcs`, `ciudades`, `establecimientos`, `lugares`, `quests`, `items`), filas homebrew en
`items_catalog`/`monstruos` (`es_homebrew` + `base`).

**Testing**: `evals/evals.json` de cada skill (casos de generación por tipo) + **verificación
end-to-end** (correr el flujo real contra Supabase/ETL e inspeccionar la fila/overlay resultante).

**Target Platform**: Claude Code (skills) + QuestKeep (render). **No se toca el frontend** (alcance
skills+Supabase).

**Project Type**: Claude Code skill pack (docs/instrucciones) sobre datos Supabase. Sin build/compilación.

**Constraints**: coexistencia sin migración forzada (US3) · nada inventado (statblocks/items del
catálogo real) · nunca escribir a BD sin confirmación del DM · convención del proyecto (chrome español
MX; reglas D&D inglés verbatim).

**Scale/Scope**: 2 skills · 6 tipos de elemento · 6 overlays `entity_schemas` · ~7 `references/*.md`.

## Constitution Check

*GATE: pasar antes de Phase 0. Re-check tras Phase 1.*

Adaptación del weave (Artículos I–III) a un repo de **skills** (no hay código de producción clásico):

- **I. TDD (NON-NEGOTIABLE)** → las "pruebas" de una skill son sus **evals** (`evals/evals.json`).
  Se **extienden/escriben los casos de eval por tipo primero** (deben describir el output esperado con
  los campos nuevos), se observa que el estado actual **no** los cumple (RED), se edita el
  `SKILL.md`/`references` hasta cumplir (GREEN), se refina. ✅ vía evals.
- **II. Verificación antes de completar** → correr el **flujo real** (generar un NPC/tesoro de prueba
  vía la skill contra Supabase + ETL) e **inspeccionar la fila/overlay/homebrew** resultante; no basta
  editar el Markdown. Evidencia en `quickstart.md`. ✅
- **III. Code review por severidad** → `/code-review` sobre el diff antes de cerrar; críticos bloquean. ✅
- **IV. YAGNI** → solo los campos co-diseñados; `subtipo→perfil` **solo** donde la heterogeneidad es
  real (Lugar/Ciudad/Establecimiento), no forzado en NPC/Item/Quest; no agregar `custom_data` a
  `items_catalog` salvo que se demuestre necesario. ✅

**Resultado: PASS** (sin violaciones; la adaptación de TDD a evals es la forma de "test" en un repo de
skills, no una excepción a la disciplina).

## Project Structure

### Documentation (this feature)

```text
specs/001-campos-elementos/
├── spec.md              # qué/por qué (fase specify)
├── design-{npc,item,lugar,establecimiento,ciudad,quest}.md  # co-diseño por tipo (el data-model narrativo)
├── plan.md              # este archivo
├── research.md          # Phase 0 — decisión abierta + enfoque técnico
├── data-model.md        # Phase 1 — definiciones de overlay entity_schemas por tipo (el contrato)
├── quickstart.md        # Phase 1 — guía de verificación end-to-end
└── tasks.md             # Phase 2 (/speckit-tasks — no lo crea plan)
```

### Source (repository root — lo que cambia)

```text
dnd-worldbuilder/
├── SKILL.md                        # flujo de escritura: overlay entity_schemas + custom_data + catálogo ETL + homebrew
└── references/
    ├── principles.md               # nota: desenterrar blobs, inspiracion (seed_trail), cross-links al nacer
    ├── npc.md · item.md · location.md · city.md · establishment.md · quest.md   # set de campos rediseñado por tipo

halo-session-prep/
├── SKILL.md                        # consumir las fichas nuevas; FIX bugs de catálogo (tesoros/monstruos → ETL)
└── references/
    ├── learnings.md                # registrar el nuevo modelo
    └── session-structure.md        # alinear plantilla (ya estaba desactualizada)

<cada skill>/evals/evals.json       # casos de generación por tipo (los "tests")
```

**Storage (no en el repo, lo aplica la skill tras OK del DM):** definiciones de overlay en
`entity_schemas` por `section` (ver `data-model.md`); `custom_data` en las 6 tablas; filas homebrew en
`items_catalog`/`monstruos`.

**Structure Decision:** repo de skills; el "modelo de datos" narrativo vive en los `design-*.md`
(por tipo) y su forma técnica (definiciones de campo del overlay) en `data-model.md`.

## Complexity Tracking

Sin violaciones de constitución que justificar (Constitution Check = PASS).
