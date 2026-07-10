# Diseño — Ficha de Lugar (piloto #3)

**Feature**: 001-campos-elementos · **Estado**: co-diseñado con el DM (2026-07-10) · Introduce el patrón **subtipo → perfil de campos** para tipos heterogéneos.

---

## 1. Qué *es* un Lugar

Un **punto de interés definido por lo que puede suceder ahí** — no por su geografía. Su columna
vertebral es el **propósito / relación con la sesión** ("Las Bodegas del Canal Bajo" importan porque
*ahí pasa algo*, no por ser bodegas). Un lugar sin propósito es decorado.

**Ciclo de vida distinto:** a diferencia de NPC/ciudad (entidades persistentes del mundo), muchos
lugares **nacen atados a una sesión** — se crean *para* una escena. A menudo son session-scoped.

---

## 2. El problema de la variedad → **subtipo activa perfil**

Un dungeon, una cueva, un claro del bosque y "una zona de una ciudad" son estructuralmente distintos.
Una ficha fija los rompe. Solución (y *el* caso que justifica los campos dinámicos):
**núcleo mínimo + `subtipo` que enciende un perfil de campos.** La skill llena **solo** el perfil que
aplica; el resto queda vacío/oculto para ese elemento.

Implementación: el overlay `entity_schemas` de `lugares` define el **superset** de todos los campos de
todos los perfiles; el `subtipo` del elemento dicta cuáles se pueblan (los demás → `_hidden`).

---

## 3. Núcleo mínimo (todo lugar)

| Campo | Qué es | Ve |
|---|---|---|
| `nombre` | — | 👥 |
| `subtipo` | Dungeon/Ruina · Cueva · Naturaleza · Zona urbana · Otro (**dirige el perfil**) | 👥 |
| **`dentro_de`** ✨ | polimórfico: región / ciudad(rel) / **otro lugar(rel)** — una zona vive *dentro* de algo | 👥 |
| **`proposito`** ✨ | qué puede suceder / por qué existe (**la espina**; se liga a quest/escena) | 🎩→ |
| **`atmosfera`** ✨ | un gancho sensorial breve (describir rápido) | 👥 |
| `estado_exploracion` · `conocido` · `mapa_id` | — | — |

**Fuera:** `descripcion`/`descripcion_exterior`/`descripcion_interior` (blobs legacy) → `atmosfera` +
campos del perfil.

---

## 4. Perfiles por subtipo (campos situacionales que activa el `subtipo`)

| subtipo | campos del perfil | flavor del grafo |
|---|---|---|
| **Dungeon / Ruina** | `estructura` (salas/niveles) · `trampas_peligros` (hazard) · `encuentro` (**statblock**+hazard) · `tesoro` (rel item) · `misterio` (lo que *recuerda*) | temas dungeon/ruina |
| **Cueva** | `profundidad_oscuridad` · `habita` (**statblock**) · `salida_riesgo` | qué habita (bestiary) |
| **Naturaleza / bosque** | `terreno_clima` · `criatura_marcas` (**statblock**; marcas visibles antes) · `recurso_peligro` · `ruta_viaje` | god-node de bioma (`Forest`, `Frozen Frontier`) |
| **Zona urbana** (bodegas del canal bajo) | `controla` (facción/npc rel) · `actividad` (comercio/crimen/culto) · `acceso` (quién entra, cómo) · `rumor` | comunidad-facción / mercado / crime-intrigue |

Los campos `encuentro`/`habita`/`criatura_marcas` usan el **statblock ref** con el modelo corregido
ETL/homebrew (ver `design-item.md`/`design-npc.md`): oficial desde `data/5e/bestiary.json`, reskin como
homebrew en `monstruos` con `base`.

---

## 5. Conexiones universales (todo lugar)

`npcs` (quién ronda) · `quests` (qué se juega aquí) · `items` (qué se halla) · **la escena/sesión** que
lo hizo nacer · `inspiracion` (procedencia del grafo, situacional).

---

## 6. Cómo la skill genera un Lugar

1. Parte del **propósito** (qué escena/quest lo pide) — no de la geografía.
2. Elige **subtipo** → carga su perfil de campos.
3. Saca *flavor* del grafo **por subtipo** (bioma para naturaleza; facción para zona urbana; tema
   dungeon para dungeon) — limando setting.
4. Siembra conexiones a la escena/quest/npcs desde el nacimiento.

Ejemplo: "Las Bodegas del Canal Bajo" nacen como **zona urbana** con `controla`=Mivvi, `actividad`,
`proposito`=su rol en la sesión; un dungeon nace con `estructura`+`encuentro`. **Misma entidad,
perfiles distintos.**

---

## 7. Patrón que generaliza

`subtipo → perfil de campos` sirve para cualquier tipo heterogéneo. Candidato claro a reusarlo:
`establecimiento` (taberna vs herrería vs templo vs gremio tienen campos distintos). Lo evaluamos al
diseñar ese tipo.

## 8. Decisiones abiertas

1. Set final de `subtipo` (¿los 4 + Otro, o falta alguno recurrente en Halo?).
2. `encuentro`/`peligro` — ¿tipifico el hazard con el menú del Encounter Axis (No-Go/Vats/Frogger/Thin
   Ice) o campo libre?
3. `dentro_de` polimórfico — confirmar que la UI de QuestKeep soporta rel a región **o** ciudad **o**
   lugar en un mismo campo (si no, 3 campos con uno lleno).
