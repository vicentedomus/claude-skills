# Diseño — Ficha de Establecimiento (piloto #4)

**Feature**: 001-campos-elementos · **Estado**: co-diseñado con el DM (2026-07-10) · Reutiliza subtipo→perfil (Lugar) + anclaje a un NPC (dueño).

---

## 1. Qué *es* un Establecimiento

Un **lugar comercial/servicio que se define por su dueño**. De `establishment.md`: **exterior primero**
(el primer gancho: entro o no), **interior** que continúa la experiencia sensorial, **refleja la
personalidad del dueño** sin duplicar su ficha, un **gancho de interacción** (algo que tocar/probar) y
un **misterio menor** ("la gaveta sin cerradura").

Es un **Lugar especializado** (edificio) + un **dueño (NPC)** + (a veces) inventario y empleados. Por
eso hereda el patrón **subtipo→perfil**: taberna, herrería, templo y gremio tienen campos distintos.

Se mantiene como **tipo aparte de Lugar** (tiene identidad propia: dueño + comercio + inventario +
empleados, y ya es su sección en la BD).

---

## 2. Núcleo mínimo (todo establecimiento)

| Campo | Qué es | Ve |
|---|---|---|
| `nombre` · `tipo`(select — **dirige el perfil**) · `ciudad`(rel) | — | 👥 |
| **`dueno`** (rel → NPC) | ancla de identidad; el local lo *refleja* | 👥 |
| `exterior` (sensorial breve — primer gancho) | text | 👥 |
| `interior` (continúa la experiencia) | textarea | 👥 |
| **`detalle_ancla`** ✨ (el letrero, lo memorable del exterior) | text | 👥 |
| **`gancho_interaccion`** ✨ (algo que tocar/probar/pedir) | text | 👥 |
| `mapa_id` · `conocido` | — | — |

**`tipo` (limpio):** `Taberna · Comercio/Tienda · Herrería · Librería · Templo · Gremio · Otro`.

---

## 3. Perfiles por `tipo`

| tipo | campos del perfil |
|---|---|
| **Taberna** | especialidad (bebida/plato) · clientela habitual · rumores · ¿cuartos? |
| **Comercio / Herrería / Objetos mágicos** | **inventario** (rel items) · especialidad · rango de precios |
| **Librería** | temática/colección · pieza rara · quién la frecuenta |
| **Templo** | `deidad`(rel) · servicios (curación/bendición) · clero |
| **Gremio** | **`clase_de_gremio`** (Ladrones · Mercaderes · Artesanos · Inventores · Arcano · Aventureros…) · `jerarquia_membresia` · **`fachada_vs_actividad`** 🎩 |

**Gremios unificados:** `Gremio de Ladrones` deja de ser un `tipo` propio → es `tipo:Gremio` +
`clase_de_gremio:Ladrones` + su `fachada_vs_actividad`. Misma ficha, sin multiplicar tipos. El patrón
subtipo recursa (tipo → perfil Gremio → clase).

---

## 4. Conexiones universales

`ciudad` · **`dueno`(npc)** · `empleados`(npcs, inverse-fk) · `items`(inventario) · `quests` ·
`misterio` 🎩→ · `inspiracion`.

---

## 5. Cómo la skill lo genera

1. Ancla al **dueño** (genera/toma primero su ficha de NPC; el local lo refleja).
2. Elige **tipo** → carga su perfil (Gremio pide además `clase_de_gremio`).
3. Flavor del grafo por tipo (comunidad-mercado/gremio para tiendas; deidad para templo) + la cultura
   de la `ciudad`, limando setting.
4. Sesga exterior→interior con `detalle_ancla` y `gancho_interaccion` como campos propios.

---

## 6. Decisiones abiertas

1. **Consistencia de taxonomía con `tipo_npc`:** hoy NPC tiene `Gremio` **y** `Gremio de Ladrones`
   separados. ¿Colapsar también a `Gremio` + una clase, para que NPC y Establecimiento compartan
   taxonomía? (Pendiente de confirmación del DM — no aplicado aún.)
2. Set final de `tipo` de establecimiento (¿falta alguno recurrente en Halo?).
