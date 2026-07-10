# Diseño — Ficha de NPC (piloto)

**Feature**: 001-campos-elementos · **Estado**: co-diseñado con el DM (2026-07-10) · **Piloto** del rediseño; de aquí se deriva la plantilla para lugar/quest/item/ciudad/establecimiento.

---

## 1. Filosofía de generación — el "genoma de identidad"

La identidad de un NPC se **compone** de un *mix & match* de **átomos try-and-tested** del grafo
compendio (`questkeep/compendium/graphify-out/`), no se inventa ni se copia uno solo. Cada átomo
es canon (escrito por un profesional); lo original es la **combinación**, limada de setting y
fusionada con coherencia.

**Slots del genoma → campos de la ficha:**

| Slot | Aporta | Campo destino |
|---|---|---|
| 1 · Vocación | oficio + su textura de mundo (routea la extracción) | `tipo_npc` (+ se expresa en `descripcion_fisica`) |
| 2 · Motor | qué lo mueve | `motivacion` (situacional) |
| 3 · Distintivo | el detalle/manierismo ancla memorable | `distintivo` |
| 4 · Twist | la tensión / secreto (magnitud dial-eada por `rol`) | `secreto` (situacional) |
| 5 · Voz / motif cultural | cómo suena, humor coherente con cultura | `forma_de_hablar` |

**Fusión con coherencia (evita el slop):** el motor explica la vocación · el distintivo expresa
el motor · el twist tensiona la disposición · la voz tiñe todo. La **disposición (`rol`)** dial-ea
la magnitud del twist (Neutral = secretito; Enemigo = patrón entero).

**Cambio de filosofía:** ya **no** se pre-escribe la narración en un blob (`primera_impresion`).
Se le dan al DM **átomos glanceables** (descripción física + distintivo + forma de hablar) para que
**improvise** en mesa. Prep = ingredientes, no script.

---

## 2. De dónde sale la inspiración — enrutamiento por combinación

El grafo (3.072 nodos · 458 comunidades · 10 libros + AAG) da tres granos: **god-nodes**
(abstracciones núcleo), **hyperedges** (patrones = "arquetipos") y **comunidades** (clusters
temáticos). Los **nodos-tema son hojas** (degree 0-1): el grafo funciona aquí como **catálogo de
piezas probadas**, no como telaraña a traversar.

`tipo_npc × rol` decide la capa:

| Combinación | Capa | Comando |
|---|---|---|
| Oficio cotidiano (~99% de Halo: Comerciante, Tabernero, Alquimista, Herrero…) | comunidad / god-node de oficio o tema | `explain "<tema>"` o `query "<sustantivo de oficio>"` |
| Sabor gnómico/industrial (tono de Halo) | god-node de raza/tema | `explain "Gnomes"`, `explain "Magic as Industry"` |
| Facción / gremio / líder | comunidad-organización | `explain "<gremio>"` |
| Antagonista / villano trágico (la cola) | **hyperedge** (GRAPH_REPORT) | leer el patrón, no `explain` del nodo |

**Gotchas del CLI (verificados en vivo, no están en el SKILL):**
1. `query` con **frase evocativa inunda** a Ravenloft (BFS depth-2 alcanza los god-nodes de horror). Sembrar con **sustantivo de función**, no con prosa de atmósfera.
2. Para villanos el **nodo está pelado** (`explain "Gabrielle Aderre"` = degree 1); el jugo vive en el **hyperedge**.
3. `path` solo funciona **intra-telaraña**; entre settings distintos → "No path".
4. Siempre **limar** nombres propios y tags de dominio (un nodo arrastra "Barovia/Shatrekvan/Ravenloft").

---

## 3. Campos de la ficha de NPC

Convención de "Ve": 👥 jugadores · 🎩 solo DM · 🎩→ revelable con `_hidden`.

### Núcleo (siempre)

| Campo | Slot | Tipo | Ve | Nota |
|---|---|---|---|---|
| `nombre` `raza` `edad` `avatar_url` | — | text/number/avatar | 👥 | identidad |
| `tipo_npc` | 1 | select **(options nuevas, §4)** | 👥 | routea el genoma |
| `rol` | dial | select (Neutral/Aliado/Enemigo) | 👥 | dial del twist |
| `estado` | — | select (Vivo/Muerto) | 👥 | |
| `descripcion_fisica` | 1 | text corto | 👥 | *describir* — el look breve |
| `distintivo` | 3 | text 1 línea | 👥 | *describir* — el detalle ancla |
| `forma_de_hablar` | 5 | text 1 línea | 🎩 | *interpretar* — cómo suena |
| `statblock` | — | statblock (ref) | 🎩 | **siempre** (§5); base reskin-eable en combate |
| `ciudad` | — | select-rel | 👥 | vínculo base sembrado |
| `conocido_jugadores` | — | checkbox | — | nace `false` |

### Situacional (solo cuando aplica)

`motivacion` (2) · `secreto` (4, 🎩→) · `inspiracion` (procedencia — poblar **solo** si se tomó una
inspiración específica del grafo) · `faccion` · `familia` · `establecimiento` · `items_magicos`
(🎩→) · `quests` · `lugares` · `relacion_party` (tracker Hostil→Desconfía→Neutral→Cordial→Aliado, si
es recurrente).

### Fuera (removidos del modelo previo)

`primera_impresion` ❌ · `notas_roleplay` ❌ · `frase` ❌ — su contenido se descompone en los campos
estructurados de arriba (agilidad > prosa).

### Implementación

Los campos nuevos (`descripcion_fisica`, `distintivo`, `forma_de_hablar`, `motivacion`, `secreto`,
`inspiracion`, `relacion_party`, `statblock`) **no** están en el baseline `FORM_SCHEMAS.npcs` de
QuestKeep → nacen como **campos custom**: una definición de overlay "genoma NPC Halo" en
`entity_schemas` (sección `npcs`) + valores en `custom_data`. Encaja con el alcance skills+Supabase
sin tocar el frontend. (Decisión FR-013 aún abierta: ¿la skill escribe el overlay tras confirmación,
o solo puebla `custom_data`?)

---

## 4. `tipo_npc` — barrido de la BD + options canónicas

Barrido de la tabla completa `npcs` (todas las campañas): 11 oficios sólidos + cola corta de basura.

**Options canónicas (15):** `'' · Comerciante · Tabernero · Herrero · Alquimista · Arcanista ·
Místico · Bibliotecario · Cazador · Religioso · Proxeneta · Gremio · Gremio de Ladrones ·
Líder político · Otro`.

**Cleanup de datos pendiente (2 filas basura, requiere target del DM antes del UPDATE):**
- `BEG` (1) → no es oficio (boss/antagonista) → reclasificar.
- `Secundario` (1) → no es oficio (importancia narrativa) → reclasificar.
- *(abierto)* `Místico` (1): ¿fold en Arcanista o mantener campo propio?

> El array `options` real vive en `app.js` (`FORM_SCHEMAS.npcs`, frontend de QuestKeep) — fuera del
> alcance skills+Supabase; se entrega la lista lista para aplicar allá.

---

## 5. `statblock` — pool real + default por vocación

**Hallazgo:** el pool de statblocks **NO** es la tabla Supabase `monstruos` (solo **6 filas**:
Ireena, Ismark, 2 Vistana bandits + 2 undead — es el store homebrew/curado, análogo a `items`). El
catálogo 5e real es **`questkeep/data/5e/bestiary.json`** (711 statblocks, fuente XMM 2025), que
QuestKeep carga como `SRD5E.bestiary`. El campo `statblock` referencia con ref tipado:
`{kind:'official', name, source}` u `{kind:'homebrew', id}`.

La skill corre server-side con acceso al repo → lee `data/5e/bestiary.json`, elige `name`+`source`
por `tipo_npc`, y escribe `{kind:'official', name, source}`. Para reskin/custom, **crea homebrew** en
`monstruos` (`base`=oficial del ETL) — **modelo simétrico al de Item** (ver `design-item.md`: tipo
oficial-ETL vs tipo homebrew vs instancia). La mecánica nunca se inventa; `base` deja el rastro.

**Default de statblock por vocación** (la skill preselecciona; el DM cambia; es el statblock **base**
que un combate puede reskin-ear):

| tipo_npc | statblock base |
|---|---|
| Comerciante · Tabernero · Bibliotecario · Herrero | Commoner |
| Líder político | Noble |
| Religioso | Priest |
| Arcanista · Místico | Mage → Archmage |
| Cazador | Scout |
| Proxeneta · Gremio de Ladrones | Spy / Bandit Captain |
| Gremio (matón) | Guard / Bandit |
| Antagonista (rol=Enemigo) | escalar: Knight / Gladiator / Assassin / Cult Fanatic |

**🐛 Bug destapado (afecta el flujo de combate existente):** `halo-session-prep` manda "monstruos
solo del catálogo `monstruos`" con queries `... FROM monstruos WHERE cr LIKE '2 (%'`, pero esa tabla
tiene 6 filas y su `cr` es `"1/8"`/`"3"` (no el string con XP embebido que documentan los learnings).
La regla apunta a una tabla casi vacía → el pool real de combate también es `data/5e/bestiary.json`.
**Corregir en el rediseño** (afecta NPC-statblock *y* el diseño de combate/`bloque_monstruos`).

---

## 6. Decisiones abiertas

1. `BEG` / `Secundario` → a qué `tipo_npc` reclasificar (correr UPDATE con confirmación).
2. `Místico` → ¿fold o campo propio?
3. FR-013 → ¿la skill escribe el overlay `entity_schemas` tras confirmación, o solo puebla `custom_data`?
4. Replicar el genoma + este patrón de ficha a los otros 5 tipos de elemento.
