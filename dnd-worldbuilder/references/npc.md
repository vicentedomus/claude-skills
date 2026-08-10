# NPC — Referencia de Entidad

Un NPC se genera con el **genoma de identidad** (`genome.md`): 5 átomos try-and-tested de una
npc-card o del grafo, limados y fusionados con coherencia. La ficha ya **no** son dos blobs de prosa — son campos
estructurados y glanceables para que el DM **describa e interprete ágil** en mesa.

## Genoma → campos

| Slot | Campo |
|------|-------|
| 1 · Vocación | `tipo_npc` (routea la extracción: card o grafo) |
| 2 · Motor | `cf_motivacion` |
| 3 · Distintivo | `cf_distintivo` |
| 4 · Twist | `cf_secreto` (magnitud según `rol`) |
| 5 · Voz / motif | `cf_forma_de_hablar` |

## Campos de la ficha

### Núcleo (siempre)

| Campo | Capa | Tipo | Ve | Nota |
|-------|------|------|----|------|
| `nombre` `raza` `edad` `avatar_url` | base | text/number/avatar | 👥 | identidad |
| `tipo_npc` | base | select (18, ver abajo) | 👥 | vocación; routea el genoma |
| `rol` | base | select (Neutral/Aliado/Enemigo) | 👥 | disposición; dial del twist |
| `estado` | base | select (Vivo/Muerto) | 👥 | |
| `cf_descripcion_fisica` | custom | text | 👥 | *describir* — el look breve |
| `cf_distintivo` | custom | text | 👥 | *describir* — el detalle/manierismo ancla |
| `cf_forma_de_hablar` | custom | text | 🎩 | *interpretar* — cómo suena |
| `cf_statblock` | custom | statblock (ref) | 🎩 | **siempre**; default por vocación (`catalogos.md`) |
| `ciudad` | base | select-rel | 👥 | vínculo sembrado |
| `conocido_jugadores` | base | checkbox | — | nace `false` |

### Situacional (solo cuando aplica)

`cf_motivacion` (textarea, 🎩) · `cf_secreto` (textarea, 🎩→ `_hidden`) · `cf_relacion_party`
(select Hostil→Desconfía→Neutral→Cordial→Aliado, 🎩) · `cf_inspiracion` (text, 🎩) ·
rels sembradas: `establecimiento`, `faccion`, `familia`, `items_magicos`, `quests`, `lugares`.

> **`cf_clase_de_gremio` se retiró** (2026-08-09). La clase es **del gremio**, no de la
> persona: en halo, **18 de los 24** NPCs `tipo_npc=Gremio` ya apuntan a su gremio por
> `establecimiento_id`, y es el **establecimiento** quien lleva la organización, hoy en
> **`cf_organizacion`** (*Hermandad de los Sellos* = `Gremio de Aventureros`; *La Sala de los
> Juramentos* = `Gremio de Ladrones`; *Mazo y Juramento* = `Gremio de Herreros`). Un campo en
> el NPC duplicaría lo que la relación ya dice. El fold `Gremio de Ladrones → Gremio`
> **se mantiene**.

### Deprecados (coexistencia, no borrar)

`primera_impresion`, `notas_roleplay`, `frase` → su contenido se descompone en los `cf_*`. Los NPCs
viejos los conservan; los nuevos usan los campos estructurados. Migración perezosa al tocar la fila.

## `tipo_npc` — options canónicas (18)

`'' · Comerciante · Tabernero · Herrero · Alquimista · Minero · Granjero · Arcanista ·
Bibliotecario · Religioso · Guardia · Cazador · Aventurero · Criminal · Proxeneta ·
Noble · Líder político · Gremio · Otro`.

Ampliado de 12 a 18 el 2026-08-09: las 6 nuevas (`Guardia`, `Criminal`, `Aventurero`,
`Noble`, `Minero`, `Granjero`) cubren **1123 de las 3585 npc-cards (31%)**. El barrido
original de spec 001 fue sobre la tabla `npcs`, cuando las cards aún no existían. Con
estas 18, los 17 valores distintos del compendio quedan cubiertos al 100%.

- `Místico` → **fold en Arcanista**.
- `Gremio de Ladrones` → **fold en `Gremio`**; la clase la lleva el establecimiento.

## Semilla desde npc-cards — la primera opción

El compendio tiene **3585 npc-cards** extraídas de 36 aventuras oficiales
(`questkeep/compendium/npc-cards.*.json`), con esquema **espejo de la tabla `npcs`**.
Para un NPC **concreto** son mejor semilla que el grafo: en vez de componer los 5 slots
desde átomos abstractos, se **descompone** una persona entera ya escrita por un
profesional. Es el patrón «desenterrar los blobs» aplicado al revés — y no necesita
`graphify` (que en contenedores de Claude Code web ni siquiera está instalado).

```
grafo:  tema abstracto  → componer 5 slots → NPC
cards:  persona entera  → descomponer en 5 slots → limar setting → NPC
```

### Retrieval

Índice plano (478 KB en crudo, 89 KB comprimido): `questkeep/compendium/npc-catalog.json`, con claves cortas
`n·r·t·ro·f·a·s·sl` = nombre, raza, tipo_npc, rol, faccion, avatar_url, fuente, slug.

```bash
# Candidatos por vocación × raza
python3 -c "
import json
cat = json.load(open('questkeep/compendium/npc-catalog.json'))
for x in cat:
    if x['t'] == 'Herrero' and x['r'] == 'Enano':
        print(x['sl'], '·', x['n'], '·', x['s'])
"
# La card completa (prosa incluida) sale del shard de su aventura
python3 -c "
import json
print([c for c in json.load(open('questkeep/compendium/npc-cards.TFTYP-TFOF.json'))
       if c['slug'] == 'durgeddin-the-black'][0])
"
```

Si `npc-catalog.json` aún no existe (lo genera QuestKeep), el fallback es un glob sobre
los 36 `npc-cards.*.json` — más verboso, y **no da el mismo resultado**: los shards traen
variantes sin acentos (p. ej. `Lider politico`, 7 filas) que el catálogo normaliza. Por
glob, `Líder político` da 224; por catálogo, 231 (la cifra de la tabla de abajo).

**Cobertura por vocación** (para saber cuándo esta vía aplica):

```
Otro 1092 · Guardia 354 · Arcanista 339 · Religioso 290 · Criminal 290 ·
Líder político 231 · Aventurero 203 · Noble 174 · Comerciante 162 · Tabernero 127 ·
Minero 66 · Bibliotecario 57 · Herrero 55 · Cazador 45 · Gremio 38 · Granjero 36 ·
Alquimista 26
```

`Proxeneta` —muy usado en Halo (17 filas)— **no tiene ni una card**. Cuando la vocación
no está cubierta, dilo y cae al grafo o a los principios. **La card es la primera
opción, no la única.**

### De la card al genoma

| Slot | Campo de la ficha | De dónde sale en la card |
|---|---|---|
| 1 · Vocación | `tipo_npc` | `tipo_npc` (directo — es el filtro por el que la elegiste) |
| 2 · Motor | `cf_motivacion` | de `notas_roleplay`: qué persigue |
| 3 · Distintivo | `cf_distintivo` | de `primera_impresion`: el detalle/manierismo ancla |
| 4 · Twist | `cf_secreto` | de `notas_roleplay`: secretos y ganchos, dial-eado por `rol` |
| 5 · Voz | `cf_forma_de_hablar` | de `notas_roleplay`: manerismos. Si la card no lo da, **se compone** |
| — | `cf_descripcion_fisica` | de `primera_impresion`: el look breve, en acción |
| — | `cf_statblock` | el de la card, **reverificado** contra `questkeep/data/5e/bestiary.json` |
| — | `cf_inspiracion` | `"<nombre de la card> (<fuente>)"` |

**Ojo con los blobs:** una `primera_impresion` mezcla tres cosas —rasgos permanentes, una
**escena de primer encuentro** y una **frase de apertura**. Solo los rasgos mapean limpio.
La escena y la frase son material de mesa, no ficha: o se descartan o alimentan la voz.

**`cf_statblock`: la card propone, la vocación corrige.** Arriba (§Núcleo) el default es *por
vocación* y aquí es *el de la card*: no es contradicción, es un orden. Parte del de la card
—lo eligió quien escribió a esa persona concreta, y suele ser más fino que el genérico
(*Kavil* el bibliotecario es `Mage`, no `Commoner`)—, **reverifícalo contra el ETL**, y quédate
con el default por vocación de `catalogos.md` solo si el reskin cambió lo que el personaje sabe
hacer. **Di cuál usaste y por qué**: es la línea de la ficha donde el DM detecta que el NPC pega
más fuerte de lo que su descripción sugiere.

### Qué se conserva y qué se lima

**Se conserva** (es por lo que la elegiste): `raza`, `tipo_npc`, `rol`, `estado`, y el
**átomo** de cada slot — el motor, el distintivo, la voz.

**Se lima** (misma regla que ya rige para el grafo, `genome.md` §4 — las cards son de
Faerûn y Barovia, Halo no lo es):

- `nombre` → **nuevo**, coherente con la cultura del lugar de Halo donde vive. Solo se
  conserva el original si el DM lo pide.
- `faccion` / `familia` → **regla dura: nunca se copian tal cual.** Son 903 valores
  distintos de otro mundo (`Zhentarim`, `House Freth`, `Harpers`…), casi todos
  irrepetibles. Se remapean a una facción real de Halo o se dejan vacíos.
- Prosa → reescribir descartando topónimos y nombres propios del origen, conservando el
  mecanismo narrativo.
- `avatar_url` → se conserva (modo referencia) si el retrato pega con el reskin; si no, se
  vacía.

**Lo escribe la skill, no viene de la card:** `relacion_sesion` y los cross-links sembrados
(`ciudad`, `establecimiento`, `quests`).

### `rol` — mapeo a las 3 options de la app

Las cards usan 5 valores; `FORM_SCHEMAS.npcs` de QuestKeep declara 3, y el eje fino tiene
su propio campo. Al partir de una card:

| Card | `rol` que se guarda | Dónde va el matiz |
|---|---|---|
| `Informante` | `Neutral` | `cf_relacion_party` (solo-DM) |
| `Antagonista` | `Enemigo` | `cf_relacion_party` (solo-DM) |

Mismo mapeo que aplica el buscador de NPCs de la app, para que las dos vías no diverjan
(US2/SC-002 de spec 001). Lectura que mantiene ambos campos con sentido: **`rol` = lo que
el party cree que es; `cf_relacion_party` = lo que de verdad siente.**

## Cómo se genera

1. **Semilla**: primero una npc-card (§«Semilla desde npc-cards»); si la vocación no tiene
   cobertura, **o es villano/arquetipo**, cae al grafo por `tipo_npc × rol` (`genome.md`):
   cotidiano → comunidad/god-node de oficio; villano → hyperedge. Limar setting en ambos casos.
2. **Vocación** fija el `tipo_npc` y el **statblock default** (`catalogos.md`).
3. **Fusión coherente:** `cf_motivacion` explica la vocación · `cf_distintivo` la expresa ·
   `cf_secreto` tensiona el `rol` · `cf_forma_de_hablar` la tiñe (humor coherente con la cultura).
4. **Describir vs interpretar:** `cf_descripcion_fisica` + `cf_distintivo` (público, lo que el DM
   narra) vs `cf_forma_de_hablar` + `cf_motivacion` + `cf_secreto` (DM, cómo lo actúa).
5. **Sembrar** ciudad/establecimiento/facción/items/quests desde el nacimiento.
6. Si tomaste una semilla específica, anota `cf_inspiracion`.

### Ejemplo de fusión (comerciante gnomo de Sleh)

Vocación *Magic as Industry* · motor *Innovation Gone Awry* (no puede dejar de "mejorar" su mercancía) ·
distintivo *ajusta un artefacto mientras te habla, nunca lo da por terminado* · secreto (neutral →
pequeño) *esconde el prototipo que sí falló y lastimó a alguien* · voz *gnómica: solemnidad absurda ante
un defecto trivial*. Statblock: Commoner. Ninguna pieza es de Halo; todas son canon.

## Checklist de calidad

- [ ] `cf_distintivo` memorable (lo que los jugadores repiten)
- [ ] `cf_descripcion_fisica` breve, en acción (no retrato estático)
- [ ] `cf_forma_de_hablar` da la voz sin monólogos
- [ ] `cf_statblock` resuelto contra el ETL (nunca inventado), default por vocación
- [ ] humor coherente con cultura/raza · edad coherente con lifespan
- [ ] ≥1 cross-link sembrado (ciudad/establecimiento/quest…)
- [ ] campos sensibles (forma_de_hablar/motivacion/secreto/statblock) marcados `_hidden`
- [ ] lore del lugar reflejado, no dicho
