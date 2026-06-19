# Persistencia, crecimiento incremental y licencia

## Dónde vive

El compendio vive en el repo **questkeep**, bajo `compendium/`:

```
compendium/
  extract.json            # UNIÓN canonicalizada de todos los libros (fuente de verdad del grafo)
  sources.json            # registro de ingestas: libro, fecha, nodos/aristas aportados, fusiones
  graphify-out/
    graph.json            # grafo derivado (se RECONSTRUYE desde extract.json en cada ingesta)
    GRAPH_REPORT.md
    obsidian/ , graph.html
```

## Modelo de crecimiento (por qué crece y no se duplica)

La **fuente de verdad** es `compendium/extract.json`: la unión canonicalizada de los grafos de
todos los libros ingeridos. Ingerir el libro N:

1. Construir corpus del libro N (`/tmp`).
2. Extraer su grafo (subagentes) → `book-extract.json`.
3. `canonicalize.py` sobre el libro (fusión **intra-libro** por label normalizado).
4. Unir con `compendium/extract.json` y `canonicalize.py` la unión (fusión **cross-book**).
5. Reconstruir `graphify-out/` desde la unión.

El paso 4 es la clave: una entidad que ya existe (p. ej. el género *Gothic Horror*, o la criatura
*Vampire*) **cae sobre el nodo canónico existente** en vez de crear un duplicado. El número de
fusiones cross-book es la métrica de "qué tan tejido" está el compendio.

`canonicalize.py` fusiona por **label normalizado** (minúsculas, sin cualificadores entre
paréntesis ni sufijos de CR). Es conservador pero efectivo; si dos entidades distintas comparten
nombre corto (p. ej. una localización "Old Mill" en dos dominios), se fusionarían — aceptable en
v1. Mejora futura: desambiguar por `kind`+source.

### Provenance (`source` por nodo)

Cada nodo lleva un atributo `source`: la lista de libros que lo aportaron (p. ej. `["RHW"]`,
`["EGW"]`, o `["EGW","RHW"]` para una entidad compartida). Se estampa al ingerir con
`canonicalize.py --source=<ID>` y se **une** al fusionar. Así, las fusiones cross-book son
auditables directamente (`len(source) > 1`) — no hay que inferirlas por intersección de labels.
El reporte de `canonicalize.py` imprime `N multi-book` con ese conteo.

## Qué se commitea (y qué no)

- **SÍ:** `extract.json`, `sources.json`, `graphify-out/` (grafo derivado: labels + aristas +
  `source_location`, sin prosa).
- **NO:** el corpus markdown (`/tmp/compendium-corpus/`) ni la prosa cruda del libro — son
  regenerables desde el clon 5etools y caen bajo la regla de licencia de `CLAUDE.md`
  ("no commitear prosa cruda de libros").

> **Licencia:** el grafo derivado es estructura transformada, no la prosa del libro. El dueño del
> repo (proyecto de uso particular) asume esta distinción. Si se publicara el repo, revisar.

## Relación con la skill `graphify`

Esta skill **no reimplementa** graphify: delega en sus pasos de build/cluster/report/visualize
(Pasos 4–6 de su SKILL.md), alimentándolos con `compendium/extract.json` como
`.graphify_extract.json`. Lo propio de esta skill es: construcción de corpus tipado,
taxonomía de extracción centrada en género, canonicalización cross-book y persistencia de la unión.

El flag `--update` de graphify (incremental por archivo) sirve para re-extraer solo archivos
cambiados de **un mismo** libro; el crecimiento **entre libros** lo maneja la unión canonicalizada
de esta skill.
