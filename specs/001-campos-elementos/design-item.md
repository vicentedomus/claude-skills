# Diseño — Ficha de Item (piloto #2)

**Feature**: 001-campos-elementos · **Estado**: co-diseñado con el DM (2026-07-10) · Segundo piloto; comparte el patrón "ancla a catálogo" con NPC.

---

## 1. Filosofía: mecánica prestada del catálogo, alma reskin-eada

Un item = **mecánica try-and-tested de un catálogo** (nunca inventada) + **reskin narrativo** encima.
Es el gemelo mecánico del NPC (bestiary↔statblock). El grafo aporta *flavor*; la mecánica **siempre**
sale del catálogo.

---

## 2. Arquitectura: **tipo vs instancia** (el flujo del DM)

Flujo (modelo del DM): **catálogo (oficial, al día vía ETL) → tomas un base → lo modificas (reskin) →
lo guardas como homebrew → los jugadores lo añaden a su bolsa e interactúan.**

| Capa | Qué es | Dónde vive |
|---|---|---|
| **TIPO — oficial** | la lista vigente (fuente de la mecánica) | **ETL `data/5e/items.json`** (1941, XDMG 2024, incl. Common/Artifact) → `SRD5E.items` |
| **TIPO — homebrew** | tu item customizado, reutilizable | **`items_catalog`** (`es_homebrew=true`, `base=<oficial ETL>`) |
| **INSTANCIA** | lo que un PJ trae en la bolsa | **`items`** (`personaje_id`/`npc_portador_id`, `custom_data` jsonb) |

El catálogo que ve el DM es la **unión** oficial(ETL) + homebrew(`items_catalog`) (`catalogoItemsRows()`
en `srd-adapters.js`). `__homebrewCreate('item')` es justo "tomar base del ETL → guardar homebrew".

---

## 3. Findings de catálogo (aterrizados en BD/ETL)

- **Lista vigente = el ETL** (`data/5e/items.json`, 1941). Las **669 filas `DMG'24` de `items_catalog`
  son huérfanas** (`es_homebrew=false`, `base=null`; el render no las lee).
- `items` (instancia) **tiene `custom_data` jsonb** → ahí caen los campos dinámicos/interactivos. **No**
  tiene FK a `items_catalog`: el enlace al tipo va por **ref** (en `custom_data`), estilo `statblock`.
- `items_catalog` **no** tiene `custom_data`; sí `es_homebrew` + `base` + `descripcion`.
- **🐛 Bug (mismo patrón que `monstruos`):** `halo-session-prep` busca tesoros
  `SELECT … FROM items_catalog WHERE rareza ILIKE 'uncommon'` → lee las 669 huérfanas (magic-only, sin
  commons). **La fuente correcta de tesoros es el ETL.** Corregir en el rediseño.

---

## 4. `item_base` — ref al catálogo (gemelo de `statblock`)

Campo custom en `items.custom_data`, ref tipado:

| Caso (`flag`) | `item_base` apunta a | Escritura de la skill |
|---|---|---|
| **match_directo** | item oficial del **ETL** `{kind:'official', name, source}` | ninguna (solo referencia) |
| **reskin** | fila **homebrew** en `items_catalog` `{kind:'homebrew', id}` (`es_homebrew=true`, `base`=oficial ETL) | INSERT del tipo homebrew tras confirmación del DM |

**Regla dura:** la mecánica **nunca se inventa** — el `base` siempre apunta a un oficial real del ETL,
y el reskin cambia solo flavor (mismas stats). (Hereda la regla de tesoros del SKILL.)

---

## 5. Reparto de campos — tipo vs instancia

### Identidad del item (el TIPO homebrew — `items_catalog`)

`base`(ETL) · `nombre`(reskin) · `tipo` · `rareza` · `requiere_sintonizacion` (heredados del base) ·
**apariencia · sensación · historia · costo_consecuencia** (el reskin narrativo).

> ⚠️ Abierto: `items_catalog` no tiene `custom_data`. Los 4 campos narrativos estructurados van
> (a) dentro de su `descripcion` como texto estructurado, o (b) se le agrega `custom_data` a
> `items_catalog`. Decisión de la fase `plan`.

### Interacción/campaña (la INSTANCIA — `items.custom_data`)

`item_base` (ref) · `portador` (personaje/npc) · `conocido_jugadores` · **tracker de cargas/usos** ·
`lugar`/`quest` de origen · `inspiracion` (procedencia del grafo) · `_hidden`.

**Fuera:** el blob `descripcion`/`contenido_html` → se parte en **apariencia / sensación / historia**.

---

## 6. Cross-links sembrados

`item_base` (catálogo: ETL o homebrew) · `portador` (npc/personaje) · `lugar` (dónde se halló) ·
`quest` (recompensa de).

---

## 7. Decisiones abiertas

1. Dónde viven los 4 campos narrativos del TIPO homebrew (descripcion estructurada vs `custom_data`
   en `items_catalog`) — fase `plan`.
2. Limpieza (opcional) de las 669 filas huérfanas de `items_catalog` una vez migrado el flujo al ETL.
3. Formato exacto del `base` en la fila homebrew (`srd:<name>` vs `{name, source}`).
