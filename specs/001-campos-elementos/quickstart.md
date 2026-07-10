# Quickstart — Verificación end-to-end del rediseño de campos

Escenarios runnable que prueban que la feature funciona (Artículo II: verificación antes de completar).
No incluye implementación; solo cómo validar.

## Prerrequisitos

- Clon de `questkeep` accesible (ETL `data/5e/{bestiary,items}.json` + `entity-schema.js`/`FORM_SCHEMAS`).
- Supabase MCP (`execute_sql`, proyecto `dwmzchtqjcblupmmklcl`).
- CLI `graphify` + grafo en `questkeep/compendium/graphify-out/`.

## Escenario 1 — NPC nace con la ficha rediseñada (SC-001, US1)

1. Pedir a `dnd-worldbuilder`: "genera un NPC nuevo para Sleh" → confirmar el commit.
2. Verificar en Supabase:
   ```sql
   SELECT nombre, tipo_npc, custom_data FROM npcs WHERE campaign_slug='halo' ORDER BY created_at DESC LIMIT 1;
   ```
   **Esperado:** `custom_data` con `cf_descripcion_fisica`, `cf_distintivo`, `cf_forma_de_hablar`,
   `cf_statblock` (ref `{kind:'official',name,source}` que existe en `bestiary.json`). **0** campos
   interactivos guardados como texto plano.
3. Verificar el overlay: `SELECT * FROM entity_schemas WHERE campaign_slug='halo' AND section='npcs';`
   → contiene las definiciones `cf_*`.

## Escenario 2 — Consistencia entre skills (SC-002, US2)

Generar un NPC vía `halo-session-prep` (los 2 nuevos de la sesión) y otro vía `dnd-worldbuilder`.
**Esperado:** mismo conjunto de `cf_*` (0 divergencias).

## Escenario 3 — Tesoro desde el ETL, no la tabla huérfana (FR-015)

Pedir un tesoro en un prep. **Esperado:** el `item_base` referencia un item de `data/5e/items.json`
(puede ser Common); si hay reskin, hay fila homebrew en `items_catalog` (`es_homebrew=true`, `base`
apuntando al oficial) + instancia en `items` con `cf_item_base`. **NO** debe salir de las 669 filas
`DMG'24` huérfanas.

## Escenario 4 — Lugar subtipo→perfil (FR-016)

Generar un lugar `cf_subtipo='Zona urbana'` (p. ej. unas bodegas). **Esperado:** poblados solo los
`cf_*` del perfil urbano (`cf_controla`, `cf_actividad`, `cf_acceso`, `cf_rumor`); los de otros perfiles
(dungeon/cueva/naturaleza) en `custom_data._hidden`.

## Escenario 5 — Combate usa el bestiario real (FR-014)

Diseñar un combate. **Esperado:** los statblocks salen de `bestiary.json` (711), no de la tabla
`monstruos` (6 filas). La cuenta de XP calibra contra el party real.

## Escenario 6 — Coexistencia / 0 regresiones (SC-003, US3)

Abrir un NPC viejo (sin `custom_data`). **Esperado:** se lee/edita igual que antes; su
`primera_impresion` sigue visible (base no oculto globalmente).

## Escenario 7 — Evals

Correr los `evals/evals.json` de ambas skills. **Esperado:** los casos por tipo (con la ficha
rediseñada) pasan.

## Gate de cierre

- [ ] Escenarios 1–7 verificados con evidencia (fila/overlay/homebrew reales).
- [ ] `/code-review` sobre el diff — 0 críticos.
