# Persistencia, crecimiento incremental y licencia

## Dónde vive

El compendio vive en el repo **questkeep**, bajo `compendium/`:

```
compendium/
  extract.json            # fuente de verdad del grafo: las cuatro capas (lore, map-stub, npc-card, faction)
  sources.json            # registro de ingestas de lore: libro, fecha, corpus, nodos aportados, fusiones
  npc-cards.<ADV>.json    # NPC cards por aventura (100 shards)
  npc-catalog.json        # índice plano de las cards: lo que lee el buscador de NPCs de la app
  npc-cards.md            # esquema y estado de las cards
  pipeline-journal.md     # umbrales, hallazgos y gotchas del pipeline — leer antes de ingerir
  merge-book-extract.py · integrate-*.py · build-adventure-corpus.py · merge-chunk-cards.py · …
  graphify-out/
    graph.json            # derivado de extract.json, + community y norm_label por nodo
    GRAPH_REPORT.md       # lo regenera integrate-book-to-graph.py sin re-clusterizar
    community-labels.json
    graph.html            # desfasada respecto a las capas de encima (pendiente conocido)
```

## Modelo de crecimiento (por qué crece y no se duplica)

La **fuente de verdad** es `compendium/extract.json`. Ingerir el lore del libro N:

1. Construir corpus del libro N (`/tmp`).
2. Extraer su grafo (subagentes) → `book-extract.json`.
3. `canonicalize.py` sobre el libro (fusión **intra-libro** por label normalizado).
4. Revisar las colisiones de labels contra el grafo y renombrar las falsas.
5. `merge-book-extract.py`: fusión **cross-book** contra las capas de lore (`document` + `map-stub`),
   con las capas `npc-card` y `faction` intactas.
6. `integrate-book-to-graph.py`: propagar el **delta** a `graph.json` (comunidades nuevas solo para
   los nodos nuevos).

El paso 5 es la clave: una entidad que ya existe (el género *Gothic Horror*, la criatura *Vampire*,
el lugar *Thay*) **cae sobre el nodo canónico existente** en vez de crear un duplicado. El número de
fusiones cross-book es la métrica de "qué tan tejido" está el compendio.

`canonicalize.py` fusiona por **label normalizado** (minúsculas, sin cualificadores entre
paréntesis ni sufijos de CR). Es conservador pero efectivo, y por eso el paso 4 existe: dos
entidades distintas con el mismo nombre corto se fusionarían (pasó con `The Citadel`, de Thay y de
Spelljammer). La regla es que el label sea la identidad: nada de nombres genéricos para lugares
concretos.

Las NPC cards crecen por otro carril (`integrate-npcs-to-graph.py`, que reconstruye todos los
nodos-NPC desde los shards en cada corrida), pero con la misma filosofía: merge cross-aventura por
nombre, y una colisión card↔lore se resuelve a favor del lore.

### Provenance (`source` por nodo)

Cada nodo lleva un atributo `source`: la lista de libros que lo aportaron (p. ej. `["RHW"]`,
`["EGW"]`, o `["EGW","RHW"]` para una entidad compartida). Se estampa al ingerir con
`canonicalize.py --source=<ID>` y se **une** al fusionar. Así, las fusiones cross-book son
auditables directamente (`len(source) > 1`) — no hay que inferirlas por intersección de labels.
El reporte de `canonicalize.py` imprime `N multi-book` con ese conteo.

## Qué se commitea (y qué no)

- **SÍ:** `extract.json`, `sources.json`, `graphify-out/` (grafo derivado: labels + aristas +
  `source_location`, sin prosa), los `npc-cards.<ADV>.json` y `npc-catalog.json`.
- **NO:** el corpus markdown (`/tmp/corpus-*`), las partes de cards en el scratchpad ni la prosa
  cruda de los libros — son regenerables desde el clon 5etools y caen bajo la regla de licencia
  de `CLAUDE.md` ("no commitear prosa cruda de libros"). Tampoco `graphify-out/cache/` (ignorado).

> **Licencia:** el grafo derivado es estructura transformada, no la prosa del libro. El dueño del
> repo (proyecto de uso particular) asume esta distinción. Si se publicara el repo, revisar.

## Relación con la skill `graphify`

Esta skill **no reimplementa** graphify: usa su clustering (`graphify.cluster`) y su generador de
reporte, pero **ya no** le pasa `extract.json` entero para reconstruir el grafo. Medido el
2026-09-12: re-clusterizar los mismos nodos da 3.614 comunidades donde las commiteadas son 461, y
disuelve las comunidades fijas de las capas de encima (458 map-stub, 459 npc-card, 460 facción).
Por eso `integrate-book-to-graph.py` clusteriza **solo el subgrafo de los nodos nuevos** y numera
sus comunidades a partir de la máxima existente. El rebuild limpio, con su re-etiquetado, es una
ronda propia pendiente.

El flag `--update` de graphify (incremental por archivo) no aplica aquí: el crecimiento entre
libros lo maneja la unión canonicalizada de esta skill.
