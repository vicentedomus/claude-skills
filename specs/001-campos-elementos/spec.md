# Feature Specification: Rediseño del conjunto de campos por elemento en las skills

**Feature Branch**: `claude/dnd-halo-session-skills-uq7orm` (spec dir `001-campos-elementos`)

**Created**: 2026-07-10

**Status**: Draft

**Input**: "Quiero rediseñar qué campos tiene cada elemento de campaña al momento de generarlos y guardarlos, en las skills `dnd-worldbuilder` y `halo-session-prep`, aprovechando el sistema de campos dinámicos e interactivos que QuestKeep ya tiene."

---

## Contexto (por qué existe esta feature)

QuestKeep (el frontend de la campaña) **ya construyó** un sistema de campos dinámicos e
interactivos estilo Notion sobre las entidades de campaña:

- `FORM_SCHEMAS` (baseline por tipo) + tabla `entity_schemas` (overlay del DM por
  `campaign_slug` + `section`: `customFields[]` + `baseOverrides[]`) + columna `custom_data`
  JSONB por fila de entidad (valores de los campos custom). Motor: `entity-schema.js`.
- Tipos de campo interactivos disponibles: relación navegable y **bilateral**
  (`select-rel` / `select-rel-multi`), **`statblock`** (chip que abre el viewer del
  bestiario/homebrew), imagen (`avatar`), mapa vinculado (`select-map`), toggles
  (`checkbox`), select, número, texto. Más **visibilidad por elemento** (`_hidden` dentro
  de `custom_data`) para revelar/ocultar partes a los jugadores.
- Diseño y plan ya documentados en QuestKeep
  (`docs/superpowers/specs/2026-07-05-campos-dinamicos-design.md`), con tests.

**El gap:** las skills `dnd-worldbuilder` y `halo-session-prep` **no conocen esta capa**.
Generan y escriben elementos contra el **modelo de columnas fijas** (p. ej. un NPC = `raza`,
`rol`, `primera_impresion`, `notas_roleplay`, `edad`…), produciendo fichas **planas**: no
pueblan `custom_data`, no usan tipos interactivos, y no consideran el schema efectivo
(baseline + overlay) que el DM ya pudo haber personalizado. Resultado: QuestKeep permite
fichas ricas, pero lo que las skills crean llega empobrecido.

Esta feature **rediseña el conjunto de campos que cada skill produce por tipo de elemento**
al generarlo y guardarlo, para que aproveche el modelo dinámico/interactivo existente.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Elementos nuevos nacen con la ficha rediseñada (Priority: P1)

Cuando el DM pide generar un elemento nuevo (NPC, lugar, quest, item, ciudad,
establecimiento) a cualquiera de las dos skills, el elemento se produce con el **conjunto de
campos rediseñado para su tipo** —incluidos los campos interactivos que apliquen (relaciones,
statblock, trackers, toggles)— y se guarda de forma que QuestKeep lo renderiza rico e
interactivo, no como texto plano.

**Why this priority**: es el corazón del rediseño; sin esto la feature no entrega valor.

**Independent Test**: pedir a la skill un NPC nuevo en Halo, confirmar el commit, y verificar
en la BD que la fila trae los campos base correctos **y** `custom_data` poblado con los campos
interactivos definidos para el tipo (p. ej. una relación a la ciudad, un tracker de relación
con el party) — y que QuestKeep lo abre sin campos plano-string donde debería haber
relación/statblock.

**Acceptance Scenarios**:

1. **Given** el DM pide "genera un NPC nuevo para Sleh", **When** la skill lo propone y el DM
   aprueba, **Then** el registro guardado incluye el conjunto de campos rediseñado del tipo
   `npc` (base + custom interactivos aplicables) y no queda ningún dato interactivo guardado
   como texto plano.
2. **Given** el DM pide un lugar/quest/item nuevo, **When** aprueba, **Then** el elemento se
   guarda con los campos rediseñados de su tipo, respetando el schema efectivo del tipo
   (baseline + overlay que el DM ya tenga en `entity_schemas`).

---

### User Story 2 — Consistencia entre ambas skills (Priority: P1)

El conjunto de campos por tipo de elemento es **idéntico entre las dos skills**:
`dnd-worldbuilder` es el banco de patrones que **define** la ficha rediseñada por tipo, y
`halo-session-prep` la **consume** al generar sus NPCs/tesoros/locaciones. Un NPC generado
por session-prep tiene los mismos campos que uno creado/mejorado por worldbuilder.

**Why this priority**: session-prep delega en worldbuilder; si divergen, el prep produce
fichas inconsistentes con el resto del mundo. Es tan crítico como US1.

**Independent Test**: generar un NPC vía session-prep y otro vía worldbuilder directo;
comparar el conjunto de campos producidos — debe ser el mismo (0 divergencias de campos por
tipo).

**Acceptance Scenarios**:

1. **Given** la ficha rediseñada del tipo `npc` vive en `dnd-worldbuilder`, **When**
   `halo-session-prep` genera sus 2 NPCs nuevos de la sesión, **Then** usan exactamente esa
   ficha (mismos campos, mismos tipos interactivos).
2. **Given** el DM mejora un elemento existente con worldbuilder, **When** se guarda,
   **Then** aplica el mismo conjunto de campos que usaría session-prep para ese tipo.

---

### User Story 3 — Coexistencia con lo existente (Priority: P2)

Los elementos ya guardados (fichas planas de columnas fijas) **siguen funcionando**. El
rediseño es aditivo/coexistente: no borra datos, no rompe el render actual, y no exige migrar
lo viejo para que las skills operen. Los campos base se conservan; lo rediseñado se apoya en
la capa `custom_data`/overlay sin destruir el modelo previo.

**Why this priority**: seguridad de datos del mundo de campaña; evita regresiones. No es P1
porque no aporta capacidad nueva, pero bloquea el merge si se viola.

**Independent Test**: abrir un NPC viejo (sin `custom_data`) después del rediseño y confirmar
que se lee/edita igual que antes; generar uno nuevo con la ficha rediseñada y confirmar que
ambos conviven en la misma vista.

**Acceptance Scenarios**:

1. **Given** un elemento previo sin campos custom, **When** el DM lo consulta o la skill lo
   lee, **Then** se comporta como antes (ningún dato perdido, ningún error de schema).
2. **Given** la skill escribe un elemento nuevo, **When** lo guarda, **Then** solo agrega
   datos (base + `custom_data`), nunca reescribe destructivamente columnas existentes de otros
   registros.

---

### User Story 4 — Confirmación del DM y visibilidad (Priority: P2)

La skill **nunca escribe sin confirmación del DM** (regla existente) y el rediseño respeta la
capa de visibilidad por elemento: la skill puede marcar qué campos de un elemento nacen
ocultos a los jugadores (p. ej. las notas de roleplay o un statblock secreto), usando el
mecanismo `_hidden` existente, sin exponer contenido que el DM quiere reservado.

**Why this priority**: preserva las reglas duras de las skills y el control del DM sobre qué
ven los jugadores.

**Independent Test**: generar un NPC con un campo marcado "solo DM"; confirmar que al
guardarlo queda en la lista de ocultos y que la vista de jugador no lo muestra.

**Acceptance Scenarios**:

1. **Given** un elemento con campos sensibles (notas de roleplay, statblock de enemigo),
   **When** la skill lo propone, **Then** marca esos campos como ocultos a jugadores por
   defecto y pide confirmación antes de escribir.

---

### Edge Cases

- **Overlay del DM ya personalizado:** si el DM ya ocultó/reordenó campos base o añadió
  campos custom en `entity_schemas` para ese tipo, la skill debe **respetar el schema
  efectivo** (no pisar el overlay del DM ni duplicar un campo que ya existe).
- **Campo interactivo que referencia una entidad inexistente:** una relación (`select-rel`)
  que apunte a algo aún no creado debe quedar como pendiente/nulo, no como texto plano ni como
  FK rota inventada.
- **Statblock:** si la skill produce un campo statblock, el valor debe resolver contra el
  bestiario/homebrew real (no inventar un statblock) — coherente con la regla dura "monstruos
  solo del catálogo".
- **Tipo sin ficha rediseñada:** un tipo de elemento fuera de los 6 de campaña se sigue
  generando con su modelo actual (sin romper).
- **session_plans:** los bloques del prep (`session_plans.bloques`) son un artefacto distinto
  a las entidades de campaña; el rediseño de campos aplica a las **entidades** (npcs, etc.),
  no reescribe el contrato de bloques del planner (ver Assumptions).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada skill DEBE, al generar/guardar un elemento de los 6 tipos de campaña
  (npcs, ciudades, establecimientos, lugares, quests, items), producir el **conjunto de
  campos rediseñado** para ese tipo, incluidos los campos interactivos aplicables.
- **FR-002**: El conjunto de campos por tipo DEBE definirse en `dnd-worldbuilder` (banco de
  patrones) y ser **consumido sin divergencia** por `halo-session-prep`.
- **FR-003**: Al guardar, la skill DEBE poblar los valores interactivos en la capa correcta
  (`custom_data` para campos custom; columnas base para campos base) de forma que QuestKeep
  los renderice como widgets interactivos, no como texto.
- **FR-004**: La skill DEBE **respetar el schema efectivo** de cada tipo (baseline
  `FORM_SCHEMAS` + overlay `entity_schemas` del DM): no duplicar campos existentes, no pisar
  personalizaciones del DM, no crear conflictos de `key`.
- **FR-005**: Cuando el rediseño requiera un campo custom que aún no existe en el overlay del
  DM, la skill DEBE **proponerlo al DM** (definición del campo + tipo) y solo materializarlo
  tras confirmación — nunca escribir estructura ni datos sin aprobación explícita.
- **FR-006**: La skill DEBE marcar como **ocultos a jugadores** (mecanismo `_hidden`) los
  campos sensibles por defecto (p. ej. notas de roleplay, statblocks de enemigos), y el DM
  puede ajustar antes del commit.
- **FR-007**: Los campos interactivos que sean **relaciones** DEBEN vincularse a entidades
  reales del mundo (patrón "conexiones entre entidades" de `principles.md`), no a texto libre.
- **FR-008**: Los campos interactivos tipo **statblock/tesoro** DEBEN resolver contra los
  catálogos reales (`monstruos`, `items_catalog`) — nunca inventar stat blocks ni items,
  coherente con las reglas duras existentes.
- **FR-009**: El rediseño DEBE ser **aditivo/coexistente**: no borra ni migra
  destructivamente elementos existentes; las fichas planas previas siguen operativas.
- **FR-010**: Ambas skills DEBEN documentar el nuevo conjunto de campos por tipo en sus
  referencias (`dnd-worldbuilder/references/*.md`) y reflejarlo en su flujo de escritura
  (`SKILL.md`), manteniendo la convención del proyecto (chrome en español MX; contenido de
  reglas D&D en inglés verbatim).
- **FR-011**: Los evals de ambas skills (`evals/evals.json`) DEBEN actualizarse para cubrir
  la generación con la ficha rediseñada.

*Requisitos con decisión pendiente (a cerrar en `/speckit-clarify`):*

- **FR-012**: El **catálogo concreto de campos por tipo** se co-diseña **tipo por tipo**,
  arrancando por **NPC como piloto** (resuelto 2026-07-10 — ver `design-npc.md`). El patrón del
  piloto (genoma de identidad + enrutamiento de extracción por combinación + campos núcleo/
  situacional) se replica luego a lugar/quest/item/ciudad/establecimiento.
- **FR-014**: La skill DEBE resolver los statblocks contra el **catálogo 5e real**
  (`questkeep/data/5e/bestiary.json`, 711 statblocks) — **no** contra la tabla Supabase `monstruos`
  (6 filas, store homebrew). Referencia con ref tipado `{kind:'official', name, source}` u
  `{kind:'homebrew', id}`. Esto **corrige un bug existente** del flujo de combate de
  `halo-session-prep` (la regla "monstruos solo del catálogo `monstruos`" apunta a una tabla casi
  vacía) y habilita el `statblock` obligatorio por NPC.
- **FR-013**: **RESUELTO** — la skill **sí escribe estructura** tras confirmación del DM: el overlay
  `entity_schemas` (definición del "genoma" por tipo) **y** las filas homebrew de catálogo
  (`items_catalog`/`monstruos` con `base` al oficial del ETL). Nunca sin aprobación explícita.
- **FR-015**: La fuente de **tesoros** DEBE ser el **catálogo 5e vigente** (`data/5e/items.json`, 1941,
  incl. Common/Artifact) — **no** la tabla `items_catalog` (669 filas `DMG'24` huérfanas, magic-only,
  sin commons). Corrige el mismo bug que FR-014 en el flujo de tesoros de `halo-session-prep`. El
  homebrew de item se guarda en `items_catalog` (`es_homebrew`, `base`); la instancia en `items`
  (`custom_data`). Ver `design-item.md`.
- **FR-016**: Los tipos de elemento **heterogéneos** (empezando por `lugares`) DEBEN modelarse con
  **núcleo mínimo + `subtipo` que activa un perfil de campos**: el overlay define el superset de campos
  de todos los perfiles; la skill puebla solo los del `subtipo` del elemento y marca el resto oculto.
  Ver `design-lugar.md`. Patrón reusable (candidato: `establecimiento`).

### Key Entities

- **Elemento de campaña**: una de las 6 secciones (npcs, ciudades, establecimientos, lugares,
  quests, items). Cada una tiene un **conjunto de campos** = campos base (columnas fijas,
  semántica estable) + campos custom (overlay del DM) + valores en `custom_data`.
- **Campo**: unidad de la ficha. Tiene `key`, `label`, `type` (incl. tipos interactivos:
  relación, statblock, imagen, mapa, toggle) y visibilidad (normal / solo-DM / oculto por
  elemento vía `_hidden`).
- **Ficha rediseñada por tipo**: el conjunto canónico de campos que las skills producen para
  un tipo dado; vive en `dnd-worldbuilder` y es la fuente de verdad compartida por ambas skills.
- **Schema efectivo**: baseline (`FORM_SCHEMAS`) fusionado con el overlay del DM
  (`entity_schemas`); es lo que la skill debe respetar al escribir.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un elemento nuevo generado por cualquiera de las dos skills incluye **el 100% de
  los campos** definidos en la ficha rediseñada de su tipo, con los valores interactivos
  guardados en la capa correcta (0 campos interactivos guardados como texto plano).
- **SC-002**: El conjunto de campos por tipo es **idéntico entre ambas skills** (0 divergencias
  al comparar un elemento del mismo tipo generado por cada una).
- **SC-003**: Tras el rediseño, **0 regresiones** sobre elementos existentes: cada ficha plana
  previa se lee y edita igual que antes (verificado sobre una muestra de registros reales de
  Halo).
- **SC-004**: **Cero escrituras sin confirmación**: toda creación de estructura o datos pasa
  por aprobación explícita del DM antes del commit.
- **SC-005**: Los campos interactivos de relación/statblock/tesoro resuelven a entidades o
  catálogos reales en el **100%** de los casos (0 statblocks/ítems inventados, 0 relaciones a
  texto libre).

---

## Assumptions

- **Alcance = skills (contrato + escritura), no frontend.** QuestKeep ya renderiza la capa
  dinámica/interactiva; esta feature no toca su código. El trabajo vive en las skills
  (`SKILL.md` + `references/*.md` + `evals/`) y en cómo escriben a Supabase.
- **Tocar Supabase está permitido** (vía Supabase MCP) para poblar `custom_data` y, si se cierra
  FR-013 en ese sentido, escribir overlays en `entity_schemas` — siempre tras confirmación del
  DM. La estructura de tablas ya existe (migración `2026-07-05-entity-schemas.sql`).
- **Los 6 tipos de campaña son el alcance.** `personajes`, `notas_*` y `monstruos`/`items_catalog`
  (catálogos) quedan fuera salvo indicación contraria.
- **`session_plans.bloques` no se reescribe** en esta feature: el prep sigue produciendo su
  contrato de bloques; lo que cambia es la ficha de las **entidades** que el prep crea/commitea
  (p. ej. los 2 NPCs nuevos que sí van a la tabla `npcs`).
- **Coexistencia, sin migración forzada** (US3): alinea con la decisión de arquitectura de
  QuestKeep (overlay + JSONB aditivo).
- **Se preservan las reglas duras existentes** de las skills (compendio como musa, nada
  inventado, plothole-check, catálogos reales, español MX / reglas en inglés verbatim).
- **Dependencia:** el repo `questkeep` está en la sesión como referencia del modelo
  (`entity-schema.js`, `FORM_SCHEMAS` en `app.js`, migración `entity_schemas`).

---

## Decisiones abiertas para `/speckit-clarify` (checkpoint)

1. ~~**Piloto vs. big-bang (FR-012):**~~ **RESUELTO** — piloto **NPC** primero, luego replicar
   (ver `design-npc.md`).
2. **¿Las skills crean estructura o solo la proponen (FR-013)?** ¿Escriben `entity_schemas`
   (overlay) tras confirmación, o el DM define los campos en QuestKeep y las skills solo
   pueblan `custom_data` + proponen qué campos convendría añadir? *(sigue abierta)*
3. **Cleanup de datos:** a qué `tipo_npc` reclasificar las filas basura `BEG` y `Secundario`;
   `Místico` ¿fold en Arcanista o campo propio?
4. **Alcance de tipos en v1:** tras el piloto NPC, ¿los 5 restantes de una o por tandas?

## Artefactos de co-diseño

- `design-npc.md` — diseño completo de la ficha de NPC (piloto): genoma de identidad, enrutamiento
  de extracción por combinación, campos núcleo/situacional, `tipo_npc` canónico + barrido,
  `statblock` (pool real + default por vocación + bug de combate destapado).
