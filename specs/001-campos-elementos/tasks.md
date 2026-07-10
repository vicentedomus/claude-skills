---
description: "Task list — rediseño de campos por elemento"
---

# Tasks: Rediseño del conjunto de campos por elemento

**Input**: `specs/001-campos-elementos/` (spec.md, plan.md, research.md, data-model.md, quickstart.md + 6 `design-*.md`)

**Tests**: SÍ incluidos. El weave (Constitución Art. I) exige TDD; en un repo de skills los **evals**
(`evals/evals.json`) **son los tests**: se escriben/extienden primero (describen la ficha rediseñada),
se observa que **FALLAN** contra el estado actual, se edita el SKILL/reference hasta que **PASAN**.

**Organización**: por user story. **MVP = US1 con el tipo NPC** (el piloto).

## Format: `[ID] [P?] [Story] Descripción con ruta`

---

## Phase 1: Setup (método compartido)

- [ ] T001 Crear `dnd-worldbuilder/references/genome.md`: genoma de identidad (5 slots) + enrutamiento de extracción por combinación (`tipo×rol` → god-node/comunidad/hyperedge) + gotchas del CLI `graphify` (semilla = sustantivo de función; limar setting).
- [ ] T002 Añadir a `dnd-worldbuilder/references/principles.md` la convención del **modelo de campos**: `cf_*` en `custom_data`, ancla a catálogo ETL, `subtipo→perfil`, coexistencia/aditividad, `inspiracion` (procedencia), visibilidad `_hidden`.

---

## Phase 2: Foundational (bloquea todas las user stories)

**⚠️ CRÍTICO**: nada de US1+ empieza hasta cerrar esta fase.

- [ ] T003 Crear `dnd-worldbuilder/references/catalogos.md`: resolución **ETL** de statblocks (`questkeep/data/5e/bestiary.json`) e items (`items.json`) — filtro por LIKE, ref tipado `{kind:'official',name,source}`, y **reskin = homebrew** (`es_homebrew`,`base`) en `monstruos`/`items_catalog`. (base de FR-014/FR-015)
- [ ] T004 Actualizar `dnd-worldbuilder/SKILL.md` (Paso 5 — escribir): flujo de escritura de **overlay `entity_schemas` (`cf_*`) + `custom_data` + homebrew**, idempotente, **con confirmación del DM** (FR-013).
- [ ] T005 Actualizar `halo-session-prep/SKILL.md`: reemplazar queries de **tesoros** (`FROM items_catalog…`) y **monstruos** (`FROM monstruos…`) por la resolución ETL de `catalogos.md`. (fix FR-014/FR-015)

**Checkpoint**: método + catálogo + escritura listos → las fichas por tipo pueden empezar.

---

## Phase 3: User Story 1 — Elementos nuevos nacen con la ficha rediseñada (P1) 🎯 MVP

**Goal**: cada tipo se genera con su set de campos rediseñado (núcleo/situacional, interactivos, cross-links).

**Independent Test**: generar un elemento de cada tipo y verificar `custom_data`/overlay contra `quickstart.md` (0 campos interactivos como texto plano).

### Tests (evals, escribir primero — deben FALLAR)

- [ ] T006 [P] [US1] Evals de **NPC** (cf_descripcion_fisica/distintivo/forma_de_hablar/statblock, `tipo_npc` 13, `clase_de_gremio`) en `dnd-worldbuilder/evals/evals.json`.
- [ ] T007 [P] [US1] Evals de **Item** (item_base→ETL, apariencia/sensación/historia en tipo homebrew, cf_ instancia) en `dnd-worldbuilder/evals/evals.json`.
- [ ] T008 [P] [US1] Evals de **Lugar** (`cf_subtipo`→perfil, criatura→statblock) en `dnd-worldbuilder/evals/evals.json`.
- [ ] T009 [P] [US1] Evals de **Establecimiento** (`tipo`→perfil, gremios unificados) en `dnd-worldbuilder/evals/evals.json`.
- [ ] T010 [P] [US1] Evals de **Ciudad** (`categoria`, `subtipo`→perfil, lider→NPC) en `dnd-worldbuilder/evals/evals.json`.
- [ ] T011 [P] [US1] Evals de **Quest** (premisa/dilema/consecuencias, recompensa item+gp, antagonista→statblock) en `dnd-worldbuilder/evals/evals.json`.

### Implementación (reescribir cada reference hasta que su eval pase)

- [ ] T012 [US1] Reescribir `dnd-worldbuilder/references/npc.md` con el set rediseñado (núcleo/situacional, statblock default por vocación, seed del grafo) — hace pasar T006. **(MVP: cerrar y validar aquí antes de seguir.)**
- [ ] T013 [P] [US1] Reescribir `dnd-worldbuilder/references/item.md` (tipo vs instancia, item_base→ETL, match_directo|reskin, split apariencia/sensación/historia/costo) — T007.
- [ ] T014 [P] [US1] Reescribir `dnd-worldbuilder/references/location.md` (punto de interés + propósito; núcleo + perfiles por subtipo; `dentro_de` campos separados) — T008.
- [ ] T015 [P] [US1] Reescribir `dnd-worldbuilder/references/establishment.md` (dueño ancla; perfiles por tipo; `clase_de_gremio`) — T009.
- [ ] T016 [P] [US1] Reescribir `dnd-worldbuilder/references/city.md` (`categoria` hexplorer; subtipo→perfil; bioma/escala; `lider`→rel NPC) — T010.
- [ ] T017 [P] [US1] Reescribir `dnd-worldbuilder/references/quest.md` (spine + subtipo ligero; recompensa item+gp; antagonista→statblock) — T011.

**Checkpoint**: los 6 tipos se generan con la ficha rediseñada (evals verdes).

---

## Phase 4: User Story 2 — Consistencia entre ambas skills (P1)

**Goal**: `halo-session-prep` consume las fichas de `dnd-worldbuilder` sin divergencia.

**Independent Test**: NPC vía session-prep == vía worldbuilder (mismos `cf_*`).

- [ ] T018 [US2] Actualizar `halo-session-prep/SKILL.md`: NPCs nuevos / tesoros / locaciones / combate consumen las fichas rediseñadas; `bloque_npcs`/`bloque_tesoros`/`bloque_monstruos` reflejan `cf_*` + ancla ETL.
- [ ] T019 [US2] Actualizar el **subagente auditor** (Paso 6 de `halo-session-prep/SKILL.md`) para verificar `cf_*` y el ancla a catálogo ETL.
- [ ] T020 [P] [US2] Eval de consistencia (NPC session-prep == worldbuilder) en `halo-session-prep/evals/evals.json`.

**Checkpoint**: fichas idénticas entre skills.

---

## Phase 5: User Story 3 — Coexistencia sin migración forzada (P2)

**Goal**: lo viejo sigue operando; los cambios son aditivos; migración perezosa donde se acordó.

**Independent Test**: un elemento viejo sin `custom_data` se lee/edita igual.

- [ ] T021 [US3] Documentar reglas de **coexistencia/aditividad** + **migración perezosa** (`lider`→NPC city-by-city; `Místico`→Arcanista al tocar) en `halo-session-prep/SKILL.md` y `dnd-worldbuilder/SKILL.md`.
- [ ] T022 [P] [US3] Alinear `halo-session-prep/references/session-structure.md` con el modelo nuevo (estaba desactualizado: `items_catalog`→ETL, bloques anidados).
- [ ] T023 [P] [US3] Eval de regresión (elemento viejo sin `custom_data`) documentada en `quickstart.md` / `halo-session-prep/evals/evals.json`.

**Checkpoint**: 0 regresiones sobre datos viejos.

---

## Phase 6: User Story 4 — Confirmación del DM y visibilidad (P2)

**Goal**: nunca escribir sin OK; campos sensibles nacen ocultos.

**Independent Test**: NPC con campo "solo DM" → queda en `_hidden`; nada se escribe sin confirmación.

- [ ] T024 [US4] Documentar en `dnd-worldbuilder/SKILL.md` los **defaults de visibilidad** (`_hidden` para notas/statblock/secreto/motivación) + el **gate de confirmación** antes de escribir overlay/homebrew/valores.

**Checkpoint**: control del DM y gating preservados.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T025 [P] Actualizar `halo-session-prep/references/learnings.md` con el modelo nuevo (cf_*, ETL, subtipo→perfil, gremios, `categoria`).
- [ ] T026 [P] Revisar `README.md` (índice de skills) — ajustar descripciones si cambió el alcance de las skills.
- [ ] T027 Correr **todos los evals** de ambas skills → verde (cierre de TDD).
- [ ] T028 Ejecutar `quickstart.md` (escenarios 1–7) con **evidencia real** (Supabase/ETL) — Art. II verificación.
- [ ] T029 `/code-review` sobre el diff completo — 0 críticos (Art. III).

---

## Dependencies & Execution Order

- **Setup (P1: T001–T002)** → sin deps.
- **Foundational (P2: T003–T005)** → depende de Setup; **BLOQUEA** todas las US.
- **US1 (P3)** → tras Foundational. Tests (T006–T011) antes de implementar (T012–T017). **T012/NPC = MVP**: cerrar y validar antes de paralelizar el resto.
- **US2 (P4)** → tras US1 (consume las fichas). **US3 (P5)** y **US4 (P6)** → tras Foundational; pueden ir en paralelo a US2, testables aparte.
- **Polish (P7)** → tras las US deseadas.

### Paralelizables
- T001‖T002 (archivos distintos). Todos los evals T006–T011 [P]. Las reescrituras T013–T017 [P] (references distintos) una vez cerrado el MVP T012.

---

## Implementation Strategy

### MVP primero (US1 / NPC)
1. Setup (T001–T002) → 2. Foundational (T003–T005) → 3. NPC: T006 (eval RED) → T012 (reference GREEN) → **validar con quickstart Escenario 1**. Demo.

### Entrega incremental
Foundational → NPC (MVP) → resto de tipos (T013–T017) → US2 consistencia → US3 coexistencia → US4 gating → Polish. Cada tipo/US es un incremento testeable que no rompe lo anterior.

---

## Notes
- `[P]` = archivos distintos, sin deps. `[Story]` mapea a la user story del spec.
- Verificar que cada eval **falla** antes de editar el reference.
- Commit tras cada tarea o grupo lógico.
- Nada se escribe a Supabase sin confirmación del DM (regla dura).
- Detalle de campos por tipo: `data-model.md` (overlay `cf_*`) + los `design-*.md` (rationale).
