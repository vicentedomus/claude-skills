# Data Model (Phase 1) — Definiciones de overlay `entity_schemas` por tipo

El **contrato técnico**: qué campos `cf_*` define la skill en el overlay de cada `section`, para que
QuestKeep los renderice. La narrativa/rationale por tipo vive en los `design-*.md`; aquí va la forma.

## Convenciones

- **Campos custom** → key con prefijo **`cf_`** (convención `entity-schema.js`; los `cf_*` son
  ocultables por `custom_data._hidden`). Valores en `custom_data` de la fila.
- **Tipos interactivos** disponibles: `text · textarea · number · select · checkbox · avatar ·
  select-rel · select-rel-multi · select-map · statblock`.
- **Ref a catálogo** (`statblock` / item_base): `{kind:'official', name, source}` (ETL) o
  `{kind:'homebrew', id}` (Supabase). Nunca inventar mecánica.
- **subtipo→perfil**: el overlay = superset; la skill puebla solo el perfil del `subtipo` y manda el
  resto a `_hidden`.
- **Deprecación de campos base** (coexistencia US3): los blobs base reemplazados (p. ej.
  `primera_impresion`, `notas_roleplay`, `contenido_html`) **no se borran**; se dejan de poblar y se
  migran **perezosamente** a los `cf_*`. No se ocultan globalmente hasta migrar (evita regresión de
  datos viejos).

---

## NPC (`section='npcs'`)

**baseOverrides:** `tipo_npc` options → las **18** canónicas (ver `design-npc.md` §4).
`rol` se queda en 3 (`Neutral`/`Aliado`/`Enemigo`): el eje fino es `cf_relacion_party`, que
es solo-DM, mientras `rol` es público. Ambos array viven en `app.js` (`FORM_SCHEMAS.npcs`)
— aplicados por QuestKeep en el PR del buscador de NPCs.

| cf_ key | label | type | dmOnly | perfil |
|---|---|---|---|---|
| `cf_descripcion_fisica` | Descripción física | text | — | núcleo |
| `cf_distintivo` | Distintivo | text | — | núcleo |
| `cf_forma_de_hablar` | Forma de hablar | text | ✓ | núcleo |
| `cf_statblock` | Statblock | statblock | ✓ | núcleo (default por vocación) |
| `cf_motivacion` | Motivación | textarea | ✓ | situacional |
| `cf_secreto` | Secreto | textarea | ✓ | situacional |
| `cf_relacion_party` | Relación con el party | select (Hostil→Aliado) | ✓ | situacional |
| `cf_inspiracion` | Inspiración | text | ✓ | situacional |

**Deprecados (lazy):** `primera_impresion`, `notas_roleplay`, `frase`. **Rels sembradas:** ciudad,
establecimiento, faccion, familia, items_magicos, quests, lugares (ya en base).

---

## Item — TIPO homebrew (`items_catalog`) + INSTANCIA (`section='items'`)

**TIPO homebrew (`items_catalog`, sin `custom_data`):** la narrativa va en `descripcion` (bloque
estructurado): **Apariencia · Sensación · Historia · Costo/consecuencia**. `es_homebrew=true`,
`base`=oficial ETL, mecánica heredada.

**INSTANCIA (`items.custom_data`):**

| cf_ key | label | type | dmOnly |
|---|---|---|---|
| `cf_item_base` | Item base (catálogo) | statblock (ref item) | ✓ |
| `cf_cargas` | Cargas / usos | number | — |
| `cf_origen_lugar` | Hallado en | select-rel (lugares) | ✓ |
| `cf_origen_quest` | Recompensa de | select-rel (quests) | ✓ |
| `cf_inspiracion` | Inspiración | text | ✓ |

**Base:** tipo/rareza/requiere_sintonizacion (heredados del base), personaje_id/npc_portador_id
(portador), conocido. **Deprecado:** `descripcion`/`contenido_html` blob → a la narrativa del tipo.

---

## Lugar (`section='lugares'`) — subtipo→perfil

**Núcleo cf_:** `cf_subtipo` (select: Dungeon/Ruina·Cueva·Naturaleza·Zona urbana·Otro) ·
`cf_lugar_padre` (select-rel lugares, para anidar) · `cf_proposito` (textarea, dmOnly) ·
`cf_atmosfera` (text). **Base:** tipo, region, ciudad(rel), estado_exploracion, mapa_id, conocido.
**Deprecado:** `descripcion`/`descripcion_exterior`/`descripcion_interior` → atmosfera + perfil.

**Perfiles (cf_ situacionales, poblados según `cf_subtipo`):**
- **Dungeon/Ruina:** `cf_estructura` · `cf_trampas` · `cf_encuentro` (statblock) · `cf_tesoro` (rel item) · `cf_misterio` (dmOnly)
- **Cueva:** `cf_profundidad` · `cf_habita` (statblock) · `cf_salida_riesgo`
- **Naturaleza:** `cf_terreno_clima` · `cf_criatura` (statblock) · `cf_recurso_peligro` · `cf_ruta`
- **Zona urbana:** `cf_controla` (rel npc/faccion) · `cf_actividad` · `cf_acceso` · `cf_rumor`

**Rels universales:** npcs, items_magicos, quests (base). `cf_hazard` = campo libre (menú Encounter
Axis como sugerencia).

---

## Establecimiento (`section='establecimientos'`) — subtipo(`tipo`)→perfil

**baseOverrides:** `tipo` options → `Taberna·Comercio/Tienda·Herrería·Librería·Templo·Gremio·Otro`.
**Núcleo cf_:** `cf_detalle_ancla` (text) · `cf_gancho_interaccion` (text). **Base:** ciudad(rel),
dueno(rel npc), descripcion_exterior→exterior, descripcion_interior→interior, mapa_id, conocido.

**Perfiles por `tipo`:**
- **Taberna:** `cf_especialidad` · `cf_clientela` · `cf_rumores`
- **Comercio/Herrería/Objetos mágicos:** `cf_inventario` (rel items) · `cf_especialidad` · `cf_precios`
- **Librería:** `cf_coleccion` · `cf_pieza_rara`
- **Templo:** `cf_deidad` (rel) · `cf_servicios` · `cf_clero`
- **Gremio:** `cf_organizacion` (select, 9 options canónicas de halo) · `cf_jerarquia` · `cf_fachada_actividad` (dmOnly)

> **Enmienda 2026-08-09 (spec 002):** era `cf_clase_de_gremio`. Renombrado a `cf_organizacion`
> por QuestKeep (`sql/migraciones/2026-08-09-organizacion-establecimientos.sql`): `clase` describe
> una categoría y `Cartel de Dobsil` no es una categoría. El campo dice a qué **organización**
> pertenece la sede, lo que además prepara el terreno para `npcs.faccion` (hoy al 0% en las 274
> filas). Las options son las 9 organizaciones reales de los documentos del DM, no una taxonomía
> inventada.

**Rels:** empleados (inverse npcs), quests. `cf_inventario` respeta el tier de la `categoria` de la
ciudad (`tiendas.js`).

---

## Ciudad (`section='ciudades'`) — subtipo→perfil

**Núcleo cf_:** `cf_categoria` (select: aldea·pueblo·ciudad·macropolis) · `cf_bioma_clima` (text) ·
`cf_subtipo` (select: Portuaria·Comercial·Fortaleza/Frontera·Capital·Religiosa·Minera·Aldea rural·Otro) ·
`cf_detalle_ancla` (text) · `cf_gobierno_cultura` (text, dmOnly). **Base:** region(`estado`),
poblacion, descripcion (fluida), mapa_id, conocida. **`lider` → select-rel npc** (baseOverride; lazy).
**Deprecado:** `descripcion_lider`.

**Perfiles por `cf_subtipo`** (ver `design-ciudad.md`): Portuaria (puerto·rutas·flota·control) ·
Comercial · Fortaleza/Frontera (defensas·guarnición·amenaza) · Capital (corte·facciones·intriga) ·
Religiosa (templo·deidad·peregrinos) · Minera (recurso·gremios) · Aldea rural (aislamiento·superstición·peligro).
**Situacional:** `cf_tension_latente` (dmOnly) · `cf_faccion_dominante` (rel) · `cf_inspiracion`.

---

## Quest (`section='quests'`) — spine universal + subtipo ligero

**baseOverrides:** ninguno crítico. **Núcleo cf_:** `cf_premisa` (textarea, dmOnly) ·
`cf_dilema_moral` (textarea, dmOnly) · `cf_consecuencias` (textarea, dmOnly). **Base:** nombre, estado,
resumen (gancho), conocido. `quest_npcs`, lugares, ciudades, establecimientos (base rels).
**Deprecado:** `contenido_html` → premisa/dilema/consecuencias.

| cf_ situacional | type | dmOnly |
|---|---|---|
| `cf_recompensa_item` (rel item) + `cf_recompensa_gp` (number) | select-rel / number | — |
| `cf_antagonista` | statblock / rel npc | ✓ |
| `cf_pistas` | textarea | ✓ |
| `cf_misterio_mayor` | textarea | ✓ |
| `cf_subtipo` | select (Investigación·Rescate·Recuperación·Eliminación·Escolta/Defensa·Otro) | — |
| `cf_inspiracion` | text | ✓ |

---

## Mapa de relaciones (cross-links sembrados al nacer)

```
Ciudad ──contiene──> NPC · Establecimiento · Lugar · Quest ; Ciudad.lider ─> NPC
Establecimiento.dueno ─> NPC ; .empleados ─> NPC ; .inventario ─> Item
NPC ─> ciudad · establecimiento · faccion · familia · items · quests · lugares ; .statblock ─> ETL/monstruos
Lugar ─> ciudad · npcs · items · quests ; .criatura/encuentro ─> ETL/monstruos
Quest ─> npcs(≥2) · lugares · ciudades · establecimientos ; .recompensa ─> Item ; .antagonista ─> ETL/monstruos
Item.item_base ─> items_catalog/ETL ; .portador ─> NPC/Personaje ; .origen ─> lugar/quest
```
