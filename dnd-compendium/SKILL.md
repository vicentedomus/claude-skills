---
name: dnd-compendium
description: >
  Hace crecer, libro a libro, un compendio de referencia de D&D como grafo de conocimiento
  graphify: ingiere una fuente oficial (libros 5etools: lore, dominios, géneros de horror,
  darklords, criaturas, organizaciones, items, opciones de personaje) y la fusiona en un grafo
  persistente, navegable y consultable que sirve de capa de inspiración/recuperación (la "musa")
  para generación de contenido de campaña.

  Usa esta skill SIEMPRE que el usuario quiera ingerir/agregar un libro o fuente al compendio,
  hacer crecer el grafo de contenido, "consumir un libro", construir o ampliar el compendio de
  referencia, o consultar el grafo de contenido D&D por tema/arquetipo. Frases de activación:
  "ingiere RHW al compendio", "agrega este libro al grafo", "haz crecer el compendio",
  "consume el siguiente libro", "consulta el compendio por X", "qué arquetipos de darklord
  tenemos", "alimenta la musa con <libro>". Actívala aunque el usuario no diga "compendio" o
  "graphify" explícitamente, si la intención es crecer/consultar el grafo de contenido D&D.

  NO la uses para generar entidades de campaña (eso es dnd-worldbuilder / halo-session-prep);
  esta skill construye y consulta la capa de contenido, que es la fuente de inspiración separada
  del mundo de campaña (Supabase).
compatibility:
  tools: [Agent]
---

# D&D Compendium — crecer la musa libro a libro

Construye y hace crecer un **compendio de referencia** de contenido oficial de D&D como un
grafo graphify **persistente**. Es la **Capa 1** de la arquitectura de 3 capas de QuestKeep:

1. **Capa 1 — Compendio (esta skill):** contenido oficial → grafo navegable de entidades
   (dominios, géneros de horror, darklords, criaturas, organizaciones, items, opciones) y sus
   relaciones, que **crece y se fusiona** con cada libro nuevo.
2. **Capa 2 — La musa:** consultar el grafo por tema/arquetipo (`/graphify query` o esta skill).
3. **Capa 3 — Generación:** `dnd-worldbuilder` + `halo-session-prep` toman el arquetipo como
   *grounding* y producen una entidad de campaña. **El compendio NUNCA escribe a Supabase.**

> El compendio es **museo/musa**, separado de la fuente de verdad del mundo (Supabase). Esta
> skill solo lee fuentes oficiales y escribe el grafo derivado al repo.

## Dependencias

- **skill `graphify`** instalada al lado (provee el paquete Python `graphifyy` y el pipeline
  de build/cluster/report). Esta skill **delega** en sus pasos de construcción de grafo.
- **clon de `questkeep`** disponible: el constructor de corpus reusa los renderers del ETL
  (`render5eTags`/`renderEntries` en `scripts/import-5etools.mjs`) — fuente única, sin drift.
- **fuente 5etools** clonada (efímera, en `/tmp`) — ver `references/sources.md`.

## Dónde vive el compendio (persistencia)

En el repo **questkeep**, bajo `compendium/`:

```
compendium/
  extract.json            # UNIÓN canonicalizada de todos los libros ingeridos (fuente de verdad del grafo)
  sources.json            # qué libros se ingirieron, cuándo, cuántos nodos/aristas aportó cada uno
  graphify-out/
    graph.json            # grafo derivado (se reconstruye desde extract.json)
    GRAPH_REPORT.md       # reporte legible
    obsidian/ , graph.html
```

Se commitea el **grafo derivado** (transformado), no la prosa cruda del libro ni el corpus
markdown (regenerable en `/tmp`). Ver `references/compendium.md`.

---

## Flujo: ingerir un libro

### Paso 0 — Verificar entorno

```bash
python3 -c "import graphify" || { echo "graphify no instalado — ver skill graphify Paso 1"; exit 1; }
ls "$QUESTKEEP/scripts/import-5etools.mjs"   # renderers del ETL (clon de questkeep)
```

`$QUESTKEEP` = ruta al clon de questkeep (donde vive `compendium/` y el constructor de corpus).

### Paso 1 — Clonar la fuente (efímera)

Sigue `CLAUDE.md` de questkeep: clonar el repo fuente completo (no archivos sueltos del mirror).

```bash
git clone --depth 1 https://github.com/5etools-mirror-3/5etools-src.git /tmp/5etools-src
```

Identifica los archivos del libro a ingerir (ver `references/sources.md`): `data/book/book-<id>.json`
y, si aplica, `data/bestiary/bestiary-<id>.json` + `fluff-bestiary-<id>.json` + `data/items.json`.

### Paso 2 — Construir el corpus tipado

```bash
node "$QUESTKEEP/scripts/build-compendium-corpus.mjs" \
  --book=/tmp/5etools-src/data/book/book-<id>.json \
  --bestiary=/tmp/5etools-src/data/bestiary/bestiary-<id>.json \
  --fluff=/tmp/5etools-src/data/bestiary/fluff-bestiary-<id>.json \
  --items=/tmp/5etools-src/data/items.json \
  --source=<ID> --out=/tmp/compendium-corpus
```

Emite **un archivo markdown por unidad lógica** con un encabezado `> kind: <kind> · source: <ID>`.
Los `kind` (domain, genre, darklord/design-grammar, horror-craft, organization, character-option,
creature, item, tarokka, setting-grammar) guían la taxonomía de extracción — ver
`references/extraction.md`. Verifica que no queden tags `{@...}`:

```bash
grep -rl "{@" /tmp/compendium-corpus/ && echo "WARN: tags sin renderizar" || echo "limpio"
```

### Paso 3 — Extracción semántica (subagentes en paralelo)

Sigue el patrón de la skill `graphify` (Paso 3, Part B): detecta archivos, divide en chunks de
~6, y **despacha todos los subagentes de extracción EN UN SOLO mensaje**. Cada subagente recibe
el prompt de extracción de `references/extraction.md` (taxonomía centrada en género), lee el
encabezado `kind:` de cada archivo, escribe su fragmento JSON a `/tmp/cwork/.chunkN.json` y
devuelve un resumen de una línea. Merge → `/tmp/cwork/.book-extract.json`.

**IDs estables:** instruye a los subagentes a usar labels limpios y consistentes (sin sufijos de
CR en entidades que recurren); la canonicalización del Paso 4 fusiona por label normalizado.

### Paso 4 — Canonicalizar y fusionar a la unión

Fusiona los nodos del libro por label normalizado (cross-file), **luego** mézclalo con la unión
existente del compendio y vuelve a canonicalizar (cross-book). **Este paso es lo que hace que el
grafo crezca en vez de duplicarse.** El flag `--source=<ID>` estampa la **provenance** (qué libro
aportó cada nodo); al fusionar, `canonicalize.py` une las listas `source`, así que un nodo presente
en varios libros queda con `source: ["EGW","RHW",...]` — auditable y sin re-extraer.

```bash
SKILL=/ruta/a/dnd-compendium
# 4a. canonicaliza el libro solo (resuelve fragmentación intra-libro) y estampa provenance
python3 "$SKILL/scripts/canonicalize.py" /tmp/cwork/.book-extract.json /tmp/cwork/.book-canon.json --source=<ID>
# 4b. une con el compendio existente (si existe) y canonicaliza la unión (une las listas `source`)
python3 - "$QUESTKEEP/compendium/extract.json" /tmp/cwork/.book-canon.json <<'PY'
import json, sys
from pathlib import Path
base_p, book_p = Path(sys.argv[1]), Path(sys.argv[2])
base = json.loads(base_p.read_text()) if base_p.exists() else {"nodes":[],"edges":[],"hyperedges":[]}
book = json.loads(book_p.read_text())
union = {"nodes": base["nodes"]+book["nodes"], "edges": base["edges"]+book["edges"],
         "hyperedges": base.get("hyperedges",[])+book.get("hyperedges",[])}
Path("/tmp/cwork/.union.json").write_text(json.dumps(union))
PY
python3 "$SKILL/scripts/canonicalize.py" /tmp/cwork/.union.json "$QUESTKEEP/compendium/extract.json"
```

### Paso 5 — Reconstruir el grafo derivado

Reconstruye `graph.json`, comunidades, reporte y vault desde la unión canonicalizada, delegando
en los pasos de build/cluster/report de la skill `graphify` (sus Pasos 4–6), con
`.graphify_extract.json` = `compendium/extract.json` y salida a `compendium/graphify-out/`.
Etiqueta las comunidades (géneros de horror, familias de criaturas, dominios) como en graphify.

### Paso 6 — Reportar el crecimiento y commitear

Actualiza `compendium/sources.json` (libro, fecha, nodos/aristas aportados, cuántos se fusionaron
sobre canónicos existentes) y reporta al usuario el **delta**: nodos/aristas nuevos, comunidades
nuevas, y **conexiones cross-book** (entidades del libro nuevo que cayeron sobre nodos canónicos
de libros previos — la señal de que el compendio se está tejiendo). Luego:

```bash
cd "$QUESTKEEP" && git add compendium/ && git commit -m "compendium: ingest <ID>"
```

No commitees el corpus markdown ni la prosa cruda (regenerables en `/tmp`).

---

## Flujo: consultar el compendio (la musa)

```bash
python3 -c "import json,networkx as nx; from networkx.readwrite import json_graph; \
  print('nodes', len(json.load(open('$QUESTKEEP/compendium/graphify-out/graph.json'))['nodes']))"
```

Usa la consulta de la skill `graphify` (`/graphify query "<tema>"`) sobre
`compendium/graphify-out/graph.json`, o revisa el `GRAPH_REPORT.md` (comunidades + "surprising
connections" + hyperedges arquetípicas). Elige UN arquetipo/patrón como semilla y entrégalo a
`dnd-worldbuilder`/`halo-session-prep` para Capa 3.

---

## Reglas

- **Nunca escribir a Supabase.** El compendio es solo-lectura del lado del mundo.
- **Verbatim desde la fuente** (convención de QuestKeep): el corpus se renderiza del JSON oficial
  en inglés, sin parafrasear. No commitear prosa cruda.
- **Crecer, no duplicar:** toda ingesta pasa por canonicalización contra la unión existente.
- **Escalado:** graphify avisa a >200 archivos / >2M palabras; con biblioteca grande, la
  extracción por libro (subagentes) es el costo recurrente. Ingerir un libro a la vez.
