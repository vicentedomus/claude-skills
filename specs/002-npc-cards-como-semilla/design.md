# NPC cards del compendio como semilla del genoma — diseño

**Estado:** diseñado · **Enmienda a:** `specs/001-campos-elementos/`
**Contraparte en QuestKeep:** `docs/superpowers/specs/2026-08-09-compendio-npcs-buscador-design.md`
**Origen:** Propuesta 2 de `questkeep/compendium/app-proposals.md`

## Problema

`halo-session-prep` pide **2 NPCs nuevos por sesión**, y su regla dura dice que salgan del
compendio antes que de la invención. La vía sancionada es el CLI `graphify` sobre el grafo de
lore (`questkeep/compendium/graphify-out/`). Medido, esa vía tiene dos fugas:

**1. El grafo no es lo que mejor sirve para «una persona».** `genome.md` enruta a god-nodes,
comunidades e hyperedges — capas de **tema y arquetipo**. Son excelentes para un villano
trágico o un tono de facción, y muy indirectas para «un herrero enano concreto».

**2. Existen 3585 npc-cards y ninguna tabla de enrutamiento las menciona.** Las cards se
tejieron al grafo (`integrate-npcs-to-graph.py`: 3373 nodos `file_type: "npc-card"`, comunidad
459), pero ni `genome.md` ni `design-npc.md` §2 tienen una fila que diga «para un NPC concreto,
empieza por una card». Son el activo más directamente reusable —**espejo 1:1 de la tabla
`npcs`**, según `npc-cards.md`— y nadie las consulta.

**3. Y el CLI no está instalado donde más se usa la skill.** En un contenedor de Claude Code
web: `graphify: command not found`. El Paso 0.5 lo contempla («si NO responde, avísale al DM y
sigue con los principios narrativos como fallback»), así que el camino real en la nube es
**inventar desde cero** — descartando 3585 personajes escritos por profesionales que están ahí
como JSON plano.

## Solución

Añadir una vía **card-first** para NPCs, que lee JSON plano: **sin CLI, sin grafo, sin
instalación**. El grafo se queda con lo que hace bien (temas, arquetipos, tono de facción); las
cards entran para las personas.

La card no sustituye al genoma — **lo alimenta**. En vez de componer los 5 slots a partir de
átomos abstractos, se parte de una persona entera ya escrita y se **descompone** en los átomos.
Es exactamente el patrón transversal (c) de spec 001: *«desenterrar los blobs de prosa en
campos estructurados»*.

```
grafo:  tema abstracto  → componer 5 slots → NPC
cards:  persona entera  → descomponer en 5 slots → limar setting → NPC
```

### De la card al genoma

Una card trae dos blobs (`primera_impresion`, `notas_roleplay`) más identidad. El mapeo a la
ficha rediseñada de `design-npc.md`:

| Slot del genoma | Campo de la ficha | De dónde sale en la card |
|---|---|---|
| 1 · Vocación | `tipo_npc` | `tipo_npc` (directo — es el filtro por el que la elegiste) |
| 2 · Motor | `cf_motivacion` | de `notas_roleplay` (qué persigue) |
| 3 · Distintivo | `cf_distintivo` | de `primera_impresion` (el detalle ancla) |
| 4 · Twist | `cf_secreto` | de `notas_roleplay` (secretos y ganchos), dial-eado por `rol` |
| 5 · Voz | `cf_forma_de_hablar` | de `notas_roleplay` (manerismos) — **si la card no lo da, se compone** |
| — | `cf_descripcion_fisica` | de `primera_impresion` (el look breve, en acción) |
| — | `cf_statblock` | `cf_statblock` de la card, **reverificado** contra `data/5e/bestiary.json` |
| — | `cf_inspiracion` | `"<nombre de la card> (<fuente>)"` — procedencia, ya prevista en `genome.md` |

### Qué se conserva y qué se lima

**Se conserva** (es por lo que la elegiste): `raza`, `tipo_npc`, `rol`, `estado`, y el
**átomo** de cada slot — el motor, el distintivo, la voz.

**Se lima** (misma regla que ya aplica al grafo, `genome.md` §4): nombres propios, topónimos y
tags de dominio. Las cards son de Faerûn/Barovia; Halo no lo es.

- `nombre` → nuevo, coherente con la cultura del lugar de Halo donde vive.
- `faccion` / `familia` → remapear a una facción real de Halo, o vaciar. Las del compendio son
  de otro mundo (`Zhentarim`, `House Freth`, `Harpers`…): 903 valores distintos, casi todos
  irrepetibles. **Nunca se copian tal cual.**
- Prosa → reescribir descartando el setting de origen, conservando el mecanismo narrativo.
- `avatar_url` → se conserva (modo referencia) si el retrato pega; si no, se vacía.

**Lo escribe la skill, no viene de la card:** `relacion_sesion` (por qué aparece en ESTA
sesión) y los cross-links sembrados (`ciudad`, `establecimiento`, `quests`).

### Retrieval sin CLI

El PR 1 de QuestKeep produce `compendium/npc-catalog.json` — índice plano de las 3585 cards
(**478 KB en crudo, 89 KB gz**; medido) con `nombre · raza · tipo_npc · rol · faccion · avatar ·
fuente · slug`. La skill lo filtra con una línea de `python3`/`jq` por `tipo_npc` × `raza`, y
luego lee la card completa del shard `npc-cards.<FUENTE>.json` (mediana 10 KB gz).

Sin ese catálogo, el fallback es un glob sobre los 36 shards — más verboso y **casi** el mismo
resultado: los shards traen el typo `Lider politico` sin acentos (7 filas) que el builder del
catálogo normaliza, así que por glob esa vocación da 224 y por catálogo 231. **La skill no queda
bloqueada por el trabajo de QuestKeep.**

Cobertura medida por oficio, para saber cuándo la vía card-first tiene material:

```
Otro 1092 · Guardia 354 · Arcanista 339 · Religioso 290 · Criminal 290 · Líder político 231 ·
Aventurero 203 · Noble 174 · Comerciante 162 · Tabernero 127 · Minero 66 · Bibliotecario 57 ·
Herrero 55 · Cazador 45 · Gremio 38 · Granjero 36 · Alquimista 26
```

Halo usa mucho `Proxeneta` (17 filas) y el compendio no lo cubre: ahí la vía card-first no
aplica y se sigue con el grafo o los principios. **La card es la primera opción, no la única.**

## Enmiendas a spec 001

### `cf_clase_de_gremio` se retira

`design-npc.md` §4 cerró que `Gremio de Ladrones` → `Gremio` + un campo `cf_clase_de_gremio`.
Cruzando `npcs.establecimiento_id → establecimientos` en halo, esa decisión se tomó sin ver que
**el dato ya existe**:

- **18 de 24** NPCs de gremio ya apuntan a su gremio (16/24 al medir esto, antes de que
  `sql/migraciones/2026-08-09-sync-vocabulario-npcs.sql` asignara `establecimiento_id` a los
  `Gremio de Ladrones` antes de plegarlos a `Gremio` — más fuerte, no distinto), y el
  establecimiento ~~**ya lleva la clase en su `tipo`**~~ **lleva la clase en `cf_organizacion`**
  (ver «Actualización 2026-08-10» abajo — al escribir esto todavía no existía ese campo):
  *Hermandad de los Sellos* (Evermere) = `Gremio de Aventureros`; *La
  Sala de los Juramentos* (Rockwood) = `Gremio de Ladrones`; *Mazo y Juramento* (Moria) = el
  gremio de herreros de la ciudad; + 13 salas de contrato, una por ciudad.
- La clase es **del gremio**, no de la persona. El NPC la hereda por la relación.

Un campo nuevo duplicaría lo que la relación ya dice. Se retira de `design-npc.md` §3/§4 y de
`data-model.md`, con la razón anotada. El fold `Gremio de Ladrones → Gremio` **se mantiene**.

> **Actualización 2026-08-10 — dónde vive la clase ya está decidido.** Este diseño dejaba
> abierta la pregunta «¿dónde la guarda el gremio, en su `tipo` entero o en un campo aparte?».
> El PR de QuestKeep (#372, Tasks 7-8) la cerró: el establecimiento lleva **`cf_organizacion`**
> (label «Organización») en el overlay `halo`/`establecimientos`, con **9 valores canónicos**
> sacados de los documentos de worldbuilding del DM, no de una taxonomía inventada:
> `Gremio de Aventureros · Gremio de Ladrones · Gremio de Comerciantes · Gremio de Herreros ·
> Gremio de Inventores · Gremio de Magos · Consejo de Sabios Elfos · Cartel de Dobsil ·
> Los Hijos de Shar`. Migración: `sql/migraciones/2026-08-09-organizacion-establecimientos.sql`.
>
> El nombre cambió porque `clase` describe una categoría y *Cartel de Dobsil* no es una
> categoría: el campo dice **a qué organización pertenece la sede**. *Mazo y Juramento* es la
> sede en Moria del Gremio de Herreros.
>
> Consecuencia para este spec: `cf_clase_de_gremio` **ya no existe en la app**, ni en el NPC ni
> en el establecimiento. Los tres sitios del repo de skills que aún lo nombran para
> establecimientos (`establishment.md`, `data-model.md` §Establecimiento, `evals.json`)
> describen una clave muerta con valores inventados — se renombran (Task 6 del plan). No es una
> ampliación de alcance: es que el alcance se resolvió fuera y estos documentos se quedaron
> atrás.

### `tipo_npc` pasa de 13 a 18 options

QuestKeep amplía la lista con las 6 vocaciones que aporta el compendio (`Guardia`, `Criminal`,
`Aventurero`, `Noble`, `Minero`, `Granjero`), que cubren el 31% de las cards. El barrido de
spec 001 fue sobre la tabla `npcs`, cuando las npc-cards aún no existían — es evidencia nueva,
no una decisión revertida. `design-npc.md` §4 y `data-model.md` se actualizan a las 18.

### `BEG` / `Secundario` sí se reclasifican

`design-npc.md` §4 decía «decisión del DM: NO reclasificar por ahora». Se tomó cuando esos
valores tampoco estaban en `options`, así que daba igual. Al sincronizar `options`, dejarlos
significa que **siguen pintándose vacíos** en el editor (`app.js:4169` pinta vacío cualquier
valor fuera de `options`). El DM aprobó reclasificar: `BEG` → `Religioso`, `Secundario` →
`Otro`. Lo ejecuta la migración de QuestKeep.

### `rol` se queda en 3 — y por qué

El compendio usa 5 (`Antagonista` 268, `Informante` 249 sobre los 3 de siempre), y la propia
tabla de halo tiene 2 filas sueltas con esos mismos dos valores: las dos partes reinventaron
los mismos conceptos por separado. Aun así **`rol` no se amplía**: el eje fino de disposición
ya tiene destino en la ficha de spec 001 — `cf_relacion_party`
(`Hostil→Desconfía→Neutral→Cordial→Aliado`, solo-DM). `rol` es **público**; duplicar el eje
crearía dos campos solapados con visibilidades distintas.

Lectura que los mantiene a ambos con sentido: **`rol` = lo que el party cree que es;
`cf_relacion_party` = lo que de verdad siente.**

Al partir de una card `Antagonista` o `Informante`, la skill mapea `rol` hacia abajo
(`Informante`→`Neutral`, `Antagonista`→`Enemigo`) y **pone el matiz real en
`cf_relacion_party`** — mismo mapeo que el import de la app, para que las dos vías no diverjan
(US2/SC-002 de spec 001).

## Archivos que cambian

| Archivo | Cambio |
|---|---|
| `dnd-worldbuilder/references/npc.md` | Nueva sección «Semilla desde npc-cards (primera opción)»: tabla card→genoma, qué se conserva/lima, retrieval. Retirar `cf_clase_de_gremio`. |
| `dnd-worldbuilder/references/genome.md` | Fila nueva en el enrutamiento: *NPC concreto → npc-card (`npc-catalog.json`)*, antes de las capas del grafo. Nota de que las cards no necesitan `graphify`. |
| `dnd-worldbuilder/SKILL.md` | Paso 0.5: para NPCs, las cards van primero y **no dependen del CLI**; el grafo sigue siendo la vía para temas/arquetipos y para los demás tipos. |
| `halo-session-prep/SKILL.md` | Regla de «2 nuevos»: apuntar a la vía card-first. |
| `specs/001-campos-elementos/design-npc.md` | §3/§4: retirar `cf_clase_de_gremio`, 18 options, revertir la nota de `BEG`/`Secundario`. |
| `specs/001-campos-elementos/data-model.md` | Tabla NPC: quitar `cf_clase_de_gremio`, `baseOverrides` → 18. Perfil de Establecimiento: `cf_clase_de_gremio` → `cf_organizacion`. |
| `dnd-worldbuilder/references/establishment.md` | Perfil `Gremio`: `cf_clase_de_gremio` → `cf_organizacion`, con los 9 valores canónicos de Halo en vez de la taxonomía inventada. |
| `dnd-worldbuilder/evals/evals.json` | La eval de establecimientos (id 2) nombra la clave nueva. |
| `dnd-worldbuilder/evals/evals.json` | Eval nueva (abajo). |
| `halo-session-prep/evals/evals.json` | Assertions nuevas (abajo). |

## Verificación

En un repo de skills los **evals son los tests** (Constitución Art. I, vía `tasks.md` de spec
001): se escriben primero, se observa que **fallan** contra el estado actual, se edita hasta que
**pasan**.

**`dnd-worldbuilder`** — eval nueva: *«genera un NPC herrero enano para Moria»*.

- Consulta `npc-catalog.json` (o los shards) filtrando por `tipo_npc`/`raza` **antes** de
  invocar `graphify` o de inventar.
- No copia `faccion`/`familia` de la card (son de otro mundo).
- El nombre propuesto no es el de la card salvo que el DM lo pida.
- `cf_inspiracion` registra la card de origen y su fuente.
- `cf_statblock` reverificado contra `data/5e/bestiary.json`, no copiado a ciegas.
- Los blobs de la card quedan **descompuestos** en `cf_*`; no se escriben en
  `primera_impresion`/`notas_roleplay`.

**`halo-session-prep`** — assertions nuevas sobre la eval existente de prep:

- Los 2 NPCs `nuevo` parten de una card cuando su `tipo_npc` tiene cobertura en el catálogo.
- Cada uno lleva `relacion_sesion` no vacía (regla existente; la card no la aporta).
- `rol` mapeado a las 3 options si la card traía `Antagonista`/`Informante`.

**Verificación manual del mapeo de vocabulario:** que las 18 options cubren los 17 valores
distintos del compendio (medido: cobertura 100%, solo el typo `Lider politico` necesita
normalizarse, y eso lo hace el builder del catálogo en QuestKeep).

## Lo que este spec NO hace

- **No aterriza la ficha `cf_*`.** Sigue siendo perezosa vía FR-013 (la skill escribe el
  overlay tras confirmación del DM). Medido hoy: **0 de 274 NPCs de halo tienen un solo campo
  `cf_*`** — spec 001 está completo en las skills y sin ejecutar en datos. QuestKeep declara
  solo `cf_statblock`.
- **No retira el grafo.** Sigue siendo la vía para temas, arquetipos, facciones y para los
  otros 5 tipos de elemento.
- **No cambia el contrato de `session_plans.bloques`.**
- **No toca la app.** Ese trabajo vive en el spec hermano de QuestKeep.
