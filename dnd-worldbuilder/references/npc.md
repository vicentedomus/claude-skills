# NPC — Referencia de Entidad

Un NPC se genera con el **genoma de identidad** (`genome.md`): 5 átomos try-and-tested del grafo,
limados y fusionados con coherencia. La ficha ya **no** son dos blobs de prosa — son campos
estructurados y glanceables para que el DM **describa e interprete ágil** en mesa.

## Genoma → campos

| Slot | Campo |
|------|-------|
| 1 · Vocación | `tipo_npc` (routea la extracción del grafo) |
| 2 · Motor | `cf_motivacion` |
| 3 · Distintivo | `cf_distintivo` |
| 4 · Twist | `cf_secreto` (magnitud según `rol`) |
| 5 · Voz / motif | `cf_forma_de_hablar` |

## Campos de la ficha

### Núcleo (siempre)

| Campo | Capa | Tipo | Ve | Nota |
|-------|------|------|----|------|
| `nombre` `raza` `edad` `avatar_url` | base | text/number/avatar | 👥 | identidad |
| `tipo_npc` | base | select (13, ver abajo) | 👥 | vocación; routea el genoma |
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
`cf_clase_de_gremio` (select, solo `tipo=Gremio`) · rels sembradas: `establecimiento`, `faccion`,
`familia`, `items_magicos`, `quests`, `lugares`.

### Deprecados (coexistencia, no borrar)

`primera_impresion`, `notas_roleplay`, `frase` → su contenido se descompone en los `cf_*`. Los NPCs
viejos los conservan; los nuevos usan los campos estructurados. Migración perezosa al tocar la fila.

## `tipo_npc` — options canónicas (13)

`'' · Comerciante · Tabernero · Herrero · Alquimista · Arcanista · Bibliotecario · Cazador · Religioso ·
Proxeneta · Gremio · Líder político · Otro`.

- `Místico` → **Arcanista**. `Gremio de Ladrones` → `Gremio` + `cf_clase_de_gremio` (Ladrones ·
  Mercaderes · Artesanos · Inventores · Arcano · Aventureros…).

## Cómo se genera

1. **Semilla** desde el grafo por `tipo_npc × rol` (`genome.md`): cotidiano → comunidad/god-node de
   oficio; villano → hyperedge. Limar setting.
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
