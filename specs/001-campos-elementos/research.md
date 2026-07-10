# Research (Phase 0) — Rediseño de campos por elemento

Resuelve la única decisión abierta y fija el enfoque técnico. Formato: Decisión · Razón · Alternativas.

---

## R1. Dónde viven los 4 campos narrativos del tipo homebrew de Item

**Decisión:** el reskin narrativo (apariencia / sensación / historia / costo) vive **en el
`descripcion` de la fila homebrew de `items_catalog`** como bloque estructurado (Markdown con
sub-encabezados). Los campos **interactivos/de campaña** (portador, tracker de cargas, lugar/quest de
origen, `inspiracion`, `_hidden`) viven en **`items.custom_data`** (la instancia).

**Razón:** `items_catalog` **no tiene `custom_data`** (columnas: nombre, fuente, rareza, tipo, dano,
propiedades, peso, valor, descripcion, es_homebrew, base…). Meter la narrativa del *tipo* en su
`descripcion` no requiere cambio de esquema, es reutilizable, y el viewer del catálogo ya la renderiza.
La interactividad (tracker, sintonización) es propia de la *instancia* → `items.custom_data`, que sí es
una de las 6 secciones con `entity_schemas`. Respeta la separación tipo/instancia (`design-item.md`).

**Alternativas:** (a) agregar `custom_data` a `items_catalog` para tener los 4 como campos separados
interactivos — **rechazado por YAGNI** (cambio de esquema a una tabla-catálogo; se puede hacer luego si
se demuestra necesario). (b) poner la narrativa en la instancia — rechazado: perdería reutilización del
tipo homebrew (el DM la guarda una vez).

---

## R2. Cómo la skill lee el catálogo oficial (ETL)

**Decisión:** la skill corre **server-side con acceso al clon de questkeep** → lee
`questkeep/data/5e/bestiary.json` (711 statblocks) e `items.json` (1941 items) **directo del archivo**
para elegir `name`+`source`. Referencia en el campo con ref tipado `{kind:'official', name, source}`.

**Razón:** el ETL es la lista vigente y es un archivo del repo (disponible en sesiones de nube). Evita
depender de la tabla Supabase (que está desactualizada/incompleta). Filtrado: `cr`/`tipo` son strings
compuestos → LIKE, no igualdad exacta.

**Alternativas:** consultar `monstruos`/`items_catalog` en Supabase — **rechazado** (6 y 669-huérfanas
filas; es justo el bug FR-014/FR-015).

---

## R3. Cómo la skill crea estructura (overlay + homebrew) — FR-013 resuelto

**Decisión:** tras confirmación del DM, la skill **escribe**:
1. La **definición de overlay** en `entity_schemas` (`campaign_slug='halo'`, `section`) = el "genoma"
   por tipo: `customFields[]` (con keys `cf_*`) + `baseOverrides[]`. Idempotente: no duplica un `cf_*`
   ya existente; respeta el overlay que el DM ya tenga.
2. Los **valores** en `custom_data` (jsonb) de la fila de entidad.
3. Para reskin de statblock/item: la **fila homebrew** en `monstruos`/`items_catalog`
   (`es_homebrew=true`, `base`=oficial del ETL, misma mecánica).

**Razón:** el DM aprobó que la skill deje la ficha lista end-to-end (FR-013). Los campos custom usan
prefijo **`cf_`** (convención de `entity-schema.js`; los `cf_*` siempre son ocultables por `_hidden`).

**Alternativas:** que el DM defina los campos a mano en QuestKeep y la skill solo poblara `custom_data`
— rechazado por el DM.

---

## R4. subtipo→perfil (tipos heterogéneos)

**Decisión:** el overlay de la sección define el **superset** de campos de todos los perfiles del tipo;
la skill puebla **solo** los del `subtipo` del elemento y marca el resto en `custom_data._hidden`
(ocultos para ese elemento). `subtipo` es un `cf_*` select que dirige el perfil.

**Razón:** `entity_schemas` es por `section`, no por subtipo → un solo overlay con todos los campos +
visibilidad por elemento (`_hidden`) logra el efecto "perfiles" sin multiplicar overlays. Aplica a
Lugar, Ciudad, Establecimiento (y `clase_de_gremio` como sub-perfil).

**Alternativas:** overlays por subtipo — no soportado (overlay es per-section).

---

## R5. Fix de los bugs de catálogo (FR-014/FR-015)

**Decisión:** en `halo-session-prep/SKILL.md`, reemplazar las queries de tesoros
(`… FROM items_catalog WHERE rareza …`) y de monstruos (`… FROM monstruos WHERE cr LIKE …`) por
**resolución contra el ETL** (`data/5e/items.json` / `bestiary.json`), dejando `items_catalog`/
`monstruos` **solo** como destino de homebrew. Actualizar `learnings.md` y `session-structure.md`.

**Razón:** las tablas Supabase están casi vacías/huérfanas; el pool real es el ETL. Es el mismo patrón
para tesoros y statblocks.

---

## R6. Coexistencia (US3) — sin migración forzada

**Decisión:** los elementos viejos (fichas planas, sin `custom_data`) siguen operando; el overlay y
`custom_data` son **aditivos**. Migraciones perezosas donde se acordó: `lider`→NPC de ciudad
(city-by-city en session-prep), `Místico`→Arcanista (al tocar la fila). Nada de UPDATE masivo.

**Razón:** seguridad de datos del mundo (US3, SC-003: 0 regresiones).
