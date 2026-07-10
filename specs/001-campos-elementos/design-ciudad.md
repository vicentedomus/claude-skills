# Diseño — Ficha de Ciudad (piloto #5)

**Feature**: 001-campos-elementos · **Estado**: co-diseñado con el DM (2026-07-10) · Usa subtipo→perfil (como Lugar) con bioma/escala transversales.

---

## 1. Qué *es* una Ciudad

De `city.md`: una **descripción fluida** (llegada/horizonte → calles/vida → **detalle ancla**), con la
**escala calibrada** (aldea ≠ ciudad comercial ≠ capital), el **gobierno/cultura reflejado sin
decirse**, y el **bioma/clima como personaje** (Sleh: columnas de vapor entre pinos nevados, hollín
dulce, la estatua del Inventor Anónimo).

**Es heterogénea:** una portuaria, una capital política y una aldea de pantano tienen campos distintos.
Por eso usa **subtipo→perfil** (como Lugar) — con **bioma y escala como núcleo transversal** (toda
ciudad los tiene) y el **subtipo = su función/carácter** manejando los campos extra.

También es **el contenedor** del mundo: de aquí cuelgan npcs, establecimientos, lugares, quests.

---

## 2. Núcleo (transversal)

| Campo | Qué es | Ve |
|---|---|---|
| `nombre` · `region/reino` (`estado`) | — | 👥 |
| **`escala`** ✨ | aldea → capital (calibra tono) | 👥 |
| **`bioma_clima`** ✨ | pantano/taiga/costa… (clima como personaje) | 👥 |
| `subtipo` | **dirige el perfil** | 👥 |
| `descripcion` (fluida: llegada→calles→ancla) | textarea | 👥 |
| **`detalle_ancla`** ✨ (lo que la define) | text | 👥 |
| **`gobierno_cultura`** ✨ (cómo se *siente* el poder/cultura) | text | 🎩 |
| **`lider` → rel a NPC** ♻️ | el líder es un NPC real | 👥 |
| `mapa_id` · `conocida` | — | — |

**Fuera:** `descripcion_lider` (texto) → se disuelve en la ficha del NPC líder.

---

## 3. Perfiles por `subtipo`

| subtipo | campos del perfil | flavor del grafo |
|---|---|---|
| **Portuaria** | puerto/muelles · rutas marítimas/comercio naval · flota o piratería · quién controla el puerto | mercado/mar |
| **Comercial** | mercados · gremios dominantes · rutas terrestres · riqueza | Immeasurable Market |
| **Fortaleza / Frontera** | defensas/murallas · guarnición · **amenaza externa** · qué protege | frontier/wildlands |
| **Capital política** | corte/gobernante · facciones en pugna · intriga · leyes | intrigue/factions |
| **Religiosa / Peregrinación** | templo mayor(rel) · deidad · peregrinos/clero · dogma | deidad/culto |
| **Minera / Industrial** | recurso explotado · gremios/condiciones · quién se enriquece | Magic as Industry |
| **Aldea rural** (p. ej. de pantano) | aislamiento · recurso local · **superstición/costumbre** · peligro del entorno | folk horror / bioma |

Ejemplo: "una aldea en el pantano" = `escala:Aldea` + `bioma:Pantano` + `subtipo:Aldea rural`; una
portuaria carga puerto/rutas/flota. Misma entidad, perfiles distintos.

---

## 4. Situacional + conexiones

**Situacional:** `tension_latente` 🎩→ (el conflicto que hierve — semilla de quests) · `faccion_dominante`(rel) · `deidad_patrona`(rel) · `rumor` · `inspiracion`.

**Conexiones (contenedor):** `npcs` residentes (inverse) · `establecimientos` (inverse) · `lugares`
(inverse) · `quests` · **`lider`(npc)** · `faccion`.

---

## 5. Cómo la skill la genera

1. Fija **escala** (población) → calibra tono (aldea vs capital).
2. Elige **subtipo** (función) → carga su perfil.
3. Saca cultura/gobierno de una **comunidad-facción** del grafo + bioma de un **god-node**
   (`Magic as Industry` para Sleh) — limando setting.
4. Teje la descripción fluida con el detalle ancla como campo propio; siembra `lider`(npc) y conexiones.

---

## 6. Migración perezosa del `lider`

`lider` = rel a NPC **de aquí en adelante**. Los `descripcion_lider` existentes **no se migran en
masa**: el líder de cada ciudad se vuelve NPC **cuando el session-prep llegue a esa ciudad**
(city-by-city). Coherente con "coexistencia, sin migración forzada" (US3 del spec).

---

## 7. Decisiones abiertas

1. Set final de `subtipo` de ciudad (¿los 7 + Otro, o falta/sobra alguno para Halo?).
2. `escala` como select (Aldea · Pueblo · Ciudad · Ciudad grande · Capital) vs derivarla de `poblacion`.
