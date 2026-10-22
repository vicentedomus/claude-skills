---
name: dnd-compendium
description: >
  Hace crecer el compendio de referencia de D&D de QuestKeep, un grafo de conocimiento graphify
  persistente en `questkeep/compendium/`, por sus dos carriles: (a) ingerir el LORE de una fuente
  oficial (libros y aventuras 5etools: dominios, géneros, facciones, criaturas, items, opciones
  de personaje) fusionándolo por entidad canónica, y (b) extraer las NPC CARDS de una aventura
  (narrativa de cada NPC con esquema espejo de la tabla `npcs`) y tejerlas al grafo con sus
  lugares y facciones. Es la capa de inspiración (la "musa") de las skills de generación.

  Usa esta skill SIEMPRE que el usuario quiera ingerir/agregar un libro o aventura al compendio,
  hacer crecer el grafo de contenido, "consumir un libro", sacar los NPCs de una aventura,
  generar NPC cards, o consultar el grafo de contenido D&D por tema/arquetipo. Frases de
  activación: "ingiere RHW al compendio", "agrega este libro al grafo", "haz crecer el
  compendio", "saca los NPCs de esta aventura", "NPC cards de <aventura>", "consulta el
  compendio por X", "qué arquetipos de darklord tenemos", "alimenta la musa con <libro>".
  Actívala aunque el usuario no diga "compendio" o "graphify" explícitamente, si la intención es
  crecer/consultar el grafo de contenido D&D.

  NO la uses para generar entidades de campaña (eso es dnd-worldbuilder / halo-session-prep);
  esta skill construye y consulta la capa de contenido, separada del mundo de campaña (Supabase).
compatibility:
  tools: [Agent]
---

# D&D Compendium — crecer la musa

Construye y hace crecer un **compendio de referencia** de contenido oficial de D&D como un
grafo graphify **persistente**. Es la **Capa 1** de la arquitectura de 3 capas de QuestKeep:

1. **Capa 1 — Compendio (esta skill):** contenido oficial → grafo navegable que **crece y se
   fusiona** con cada fuente nueva.
2. **Capa 2 — La musa:** consultar el grafo por tema/arquetipo (`graphify query`, ver abajo).
3. **Capa 3 — Generación:** `dnd-worldbuilder` + `halo-session-prep` toman el arquetipo como
   *grounding* y producen una entidad de campaña. **El compendio NUNCA escribe a Supabase.**

## Antes de tocar nada: lee el journal

**`questkeep/compendium/pipeline-journal.md` es lectura obligatoria antes de cualquier ingesta**,
en especial los *Umbrales* y los *Gotchas*. Esta skill dice el camino; el journal dice qué ya
rompió por el camino y cómo se midió. Si una regla de aquí y una del journal chocan, el journal es
más reciente: síguelo y arregla esta skill.

## El grafo hoy: cuatro capas, no una

El compendio empezó siendo solo lore de libros. Hoy `extract.json` (fuente de verdad) y
`graphify-out/graph.json` (derivado) llevan **cuatro capas** (~10.500 nodos), cada una con su
dueño:

| `file_type` | Qué es | Comunidad | Lo escribe |
|---|---|---|---|
| `document` | Lore de los libros (~3.800 nodos, 13 libros) | las que salieron al clusterizar | **carril A** (este) |
| `map-stub` | Lugares con mapa que no existían como lore (~850) | 458 | `integrate-maps-to-graph.py` |
| `npc-card` | Un nodo por NPC de aventura (~5.300) | 459 | **carril B** (`integrate-npcs-to-graph.py`) |
| `faction` | Facciones con 2+ miembros (~490), id `faccion:<slug>` | 460 | `integrate-factions-to-graph.py` |

**Dos consecuencias que no son negociables:**

1. **Nunca reconstruyas el grafo entero con graphify.** Medido: re-clusterizar da **3.614
   comunidades donde hay 461**, solo 69 nodos conservan la suya y se disuelven las comunidades
   fijas de las tres capas de encima (un diff de ~250k líneas). Todo entra por **delta**. El
   rebuild limpio es una ronda propia, con su re-etiquetado de comunidades (journal, gotcha 17).
2. **Nunca pases la unión entera por `canonicalize.py`.** Reasigna ids `canon:<slug>` a todo, y
   perdía **491 ids**: las 486 facciones y 5 npc-cards, que el buscador de NPCs de la app
   referencia. El carril A canonicaliza **solo** `document` + `map-stub` (gotcha 18).

## Dependencias

- **Clon de `questkeep`** (`$QUESTKEEP`): ahí viven `compendium/`, los scripts de los dos carriles y
  el constructor de corpus de lore, que reusa los renderers del ETL (`scripts/import-5etools.mjs`).
- **Esta skill materializada en `$QUESTKEEP/.claude/skills/dnd-compendium/`.**
  `compendium/merge-book-extract.py` llama a `scripts/canonicalize.py` **por esa ruta**. La pone ahí
  el hook `sync-skills.sh` porque `.claude/skills.txt` la lista; si no está (`ls` falla), corre el
  hook o reinicia la sesión antes del carril A.
- **`graphify`** (paquete PyPI `graphifyy`): `integrate-book-to-graph.py` clusteriza los nodos
  nuevos con él y regenera `GRAPH_REPORT.md`. En Claude Code web suele venir instalado; si no,
  skill `graphify`, Paso 1.
- **Fuente 5etools** clonada en `/tmp` (efímera) — ver `references/sources.md`.

## Elegir el carril

| La fuente es… | Carril | Por qué |
|---|---|---|
| Un **libro** (setting, DM guide, suplemento) | **A** — lore | Su valor son temas, facciones, lugares y arquetipos |
| Una **aventura** con elenco | **B** — NPC cards | Su valor son las personas; como lore, sus capítulos de misión son ruido |
| Una aventura que **trae también setting** (p. ej. AUD: Thay + misiones) | **A** con los capítulos de setting, **luego B** con la aventura | Extraer el mismo párrafo por los dos carriles es pagar el subagente dos veces |

**Orden: el lore primero, las cards después.** Así las cards y los map-stubs caen sobre nodos de
lore que ya existen en vez de crear islas (en AUD, el lore conectó 10 de 17 map-stubs y las cards
4 más). La capa de **mapas y lugares** de una aventura nueva tiene su propio pipeline y no es de
esta skill: `questkeep/compendium/map-index.md`.

## Regla de los integradores: control antes de cambiar

Antes de correr cualquier `integrate-*.py` o `merge-book-extract.py` sobre un cambio, córrelo
**sin el cambio** (o con `--dry-run` si lo tiene) y comprueba que el diff sale **vacío** (journal,
gotchas 13 y 23). Hoy la cadena entera es idempotente y da control vacío; si deja de darlo,
algo derivó: no absorbas la corrida limpia junto a tu cambio, aplica solo el delta y anótalo.

Para revisar diffs de `extract.json`/`graph.json` usa `git diff --patience`: con el algoritmo por
defecto el mismo delta parece 3-100 veces más grande (gotcha 20).

---

## Carril A — ingerir el lore de un libro

### A0 · Verificar entorno

```bash
cd "$QUESTKEEP"
python3 -c "import graphify" || echo "falta graphify: skill graphify, Paso 1"
ls scripts/build-compendium-corpus.mjs .claude/skills/dnd-compendium/scripts/canonicalize.py
```

### A1 · Clonar la fuente (efímera)

Sigue `CLAUDE.md` de questkeep: el repo completo, no ficheros sueltos del mirror.

```bash
git clone --quiet --depth 1 --branch main \
  https://github.com/5etools-mirror-3/5etools-src.git /tmp/5etools-src
```

Las fuentes oficiales viven en el clon pelado; las de *brew* (Kobold Press, Roll & Play…) en
`TheGiddyLimit/homebrew` — ver `references/sources.md`.

### A2 · Construir el corpus tipado

```bash
node scripts/build-compendium-corpus.mjs \
  --book=/tmp/5etools-src/data/book/book-<id>.json \
  --bestiary=/tmp/5etools-src/data/bestiary/bestiary-<id>.json \
  --fluff=/tmp/5etools-src/data/bestiary/fluff-bestiary-<id>.json \
  --items=/tmp/5etools-src/data/items.json \
  --source=<ID> --out=/tmp/corpus-<id>
```

Una aventura se pasa igual con `--book=…/data/adventure/adventure-<id>.json`. Emite un markdown por
unidad lógica con cabecera `> kind: <kind> · source: <ID>` y un `_corpus-manifest.json`.

**Mira el reparto por `kind` antes de extraer.** Si capítulos enteros caen en `kind: lore` (la
heurística de capítulo no los reconoció), corrígelo con `--whole-chapters="<título>=<kind>,…"`
en vez de tocar el script. Precedente AU: sin el flag, *Magic Items* y el apéndice de aventura
salían como `lore`; con `--whole-chapters="magic items=item,tomb of the shadow serpents=adventure"`
salieron bien. **Recorta lo que no es de este carril** (los capítulos de misión de una aventura van
al carril B): borrar sus ficheros del directorio del corpus es suficiente.

```bash
grep -rl "{@" /tmp/corpus-<id>/ && echo "BUG: tags sin renderizar" || echo "limpio"
```

Un `{@...}` que sobrevive es un bug del renderer: repórtalo, no lo toleres.

### A3 · Extracción semántica (subagentes en paralelo)

Divide los ficheros en chunks de ~6 y **despacha todos los subagentes EN UN SOLO mensaje**, cada uno
con el prompt de `references/extraction.md`, escribiendo su fragmento a `/tmp/cwork/.chunkN.json` y
devolviendo un resumen de una línea. Merge → `/tmp/cwork/.book-extract.json`.

Instrucción explícita: **labels limpios y específicos**. Sin sufijos de CR ni de fuente (un sufijo
rompe la fusión en silencio) y **sin nombres genéricos** para lugares concretos: `Citadel of
Thaymount`, no `The Citadel`; `Sanctum Library`, no `Library` (gotcha 22). Para un libro con nombres
que deben caer sobre nodos existentes (Thay, Szass Tam…), díselo a los subagentes.

### A4 · Revisar la calidad del texto, no solo el conteo

Abre 2-3 fragmentos y lee la prosa: acentos, nombres de reglas en inglés, descripciones reales en
vez de resúmenes de una línea. Un JSON válido puede traer el texto degradado (gotcha 6).

### A5 · Canonicalizar el libro solo

```bash
SKILL="$QUESTKEEP/.claude/skills/dnd-compendium"
python3 "$SKILL/scripts/canonicalize.py" \
  /tmp/cwork/.book-extract.json /tmp/cwork/.book-canon.json --source=<ID>
```

Fusión **intra-libro** por label normalizado y estampado de provenance (`source: ["<ID>"]`).

### A6 · Revisar las colisiones cross-book ANTES de fusionar

`canonicalize.py` fusiona por label normalizado, así que dos sitios distintos con el mismo nombre
corto colapsan en un nodo (el `The Citadel` de Thay caía sobre el del Rock of Bral, de
Spelljammer). Lista las colisiones y míralas **una a una**:

```bash
python3 - "$SKILL/scripts" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1]); from canonicalize import normalize
e = json.load(open('compendium/extract.json'))
b = json.load(open('/tmp/cwork/.book-canon.json'))
lore = {}
for n in e['nodes']:
    if n.get('file_type') in ('document', 'map-stub'):
        lore.setdefault(normalize(n['label']), []).append(n)
for n in b['nodes']:
    for m in lore.get(normalize(n['label']), []):
        print(f"{n['label']!r:40} ← {m['label']!r} {m.get('source')}")
PY
```

El criterio **no** es «colisión = error»: en AUD, de 4 colisiones con libros de otro setting, 3
debían fusionar (*Espionage*, *Underdark*, *Glabrezu*) y solo una era falsa. Las falsas se arreglan
**renombrando en el fragmento** (`/tmp/cwork/.book-canon.json`) y repitiendo A6.

### A7 · Fusionar y propagar por delta

```bash
python3 compendium/merge-book-extract.py /tmp/cwork/.book-canon.json --source=<ID> --dry-run
python3 compendium/merge-book-extract.py /tmp/cwork/.book-canon.json --source=<ID>
python3 compendium/integrate-book-to-graph.py --source=<ID> --dry-run
python3 compendium/integrate-book-to-graph.py --source=<ID>
```

- `merge-book-extract.py` canonicaliza el libro contra `document` + `map-stub`, vuelve a pegar
  `npc-card` y `faction` verbatim, resuelve las colisiones lore↔card **a favor del lore** heredando
  la `faccion` de la card (si no, el personaje pierde su arista `pertenece_a`: gotchas 19 y 25), y
  **aborta** si desaparece algún id preexistente o queda una arista huérfana.
- `integrate-book-to-graph.py` añade a `graph.json` los nodos nuevos con comunidades propias
  (clusterizando solo el subgrafo del libro), re-espeja los existentes desde `extract.json`
  (gotcha 24), etiqueta las comunidades nuevas y regenera `GRAPH_REPORT.md` sin re-clusterizar.

Los dos son idempotentes: una segunda corrida no añade nada. **Esperable en el `--dry-run`:** el
total de aristas sale 2 por debajo de lo que sumas, porque `canonicalize.py` deduplica dos
`aparece_en` que ya estaban repetidas en el lore (Duvessa Shane y Markham Southwell → Bryn
Shander). No es una pérdida; cualquier otra diferencia sí hay que explicarla.

### A8 · Verificar el delta

```bash
python3 - <<'PY'
import json
e = json.load(open('compendium/extract.json'))
g = json.load(open('compendium/graphify-out/graph.json'))
src = '<ID>'
nuevo = [n for n in e['nodes'] if src in (n.get('source') or [])]
multi = [n for n in nuevo if len(n.get('source', [])) > 1]
print('nodos', src, len(nuevo), '| fusionados cross-book', len(multi))
print([(n['label'], n['source']) for n in multi[:10]])
print('extract vs graph:', len(e['nodes']), len(g['nodes']))
PY
```

- **Fusiones cross-book en 0** = el libro entró como isla. Puede ser real (AAG, Spelljammer, tuvo
  1), pero antes de aceptarlo revisa que los labels no lleven sufijos.
- **`extract.json` y `graph.json` con conteos distintos** = divergieron (gotcha 24).
- Si había **map-stubs aislados** de esa fuente, comprueba que ganaron aristas.

### A9 · Registrar y commitear

- `compendium/sources.json` → entrada nueva en `ingested` (source, título, fecha, `corpus_files`,
  `corpus_words`, nodos aportados, fusiones cross-book con la lista de entidades) y los contadores
  de `compendium`. `integrate-book-to-graph.py` lee de aquí el *Corpus Check* del reporte.
- `compendium/README.md` §*Estado actual*: libros, nodos, aristas y comunidades, y una línea sobre
  qué voz aporta el libro.
- `compendium/pipeline-journal.md`: gotcha nuevo si apareció alguno.

```bash
git add compendium/ && git commit -m "Compendio: ingerir <ID> a la Capa 1"
```

No commitees el corpus markdown ni la prosa cruda (regenerables en `/tmp`).

---

## Carril B — NPC cards de una aventura

Esquema, vocabulario cerrado y prompt del subagente: **`references/npc-cards.md`**. Estado y
comparables: `questkeep/compendium/npc-cards.md`.

### B0 · Control sobre el árbol limpio

Antes de extraer nada, corre la cadena de integración sobre el repo **sin cambios** y comprueba que
no mueve ni una línea (gotcha 13). Es el control del paso B5, hecho cuando todavía es barato:

```bash
python3 compendium/integrate-npcs-to-graph.py
python3 compendium/integrate-factions-to-graph.py
node compendium/build-npc-catalog.mjs
git status --short compendium/        # esperado: vacío
```

Si no sale vacío, algo derivó antes de tu cambio: investígalo (o descártalo con
`git checkout -- compendium/`) antes de seguir, para no mezclarlo con la aventura nueva.

> Hazlo **antes** de crear `npc-cards.<ADV>.json`, no con `git stash`: un fichero nuevo sin trackear
> no se puede stashear por ruta (`git stash push <ruta>` falla con *did not match any file(s) known
> to git*).

### B1 · Corpus de prosa, partido por presupuesto

```bash
python3 compendium/build-adventure-corpus.py <ADV> \
  --src=/tmp/5etools-src/data --chunk=45000 --out=/tmp/corpus-<adv>.md
ls -la /tmp/corpus-<adv>*.md
```

- **≤ ~45k palabras por subagente** (medido: por encima la extracción se degrada). `--chunk` corta
  solo en línea de heading, para no partir la descripción de un NPC. Con `--chunk` la salida es
  siempre `<out>.part<N>.md`, también cuando cabe en una sola parte.
- Lee `<SRC>/adventure/adventure-<adv>.json`. Una aventura del *brew* no está en el clon pelado:
  apunta `--src` al overlay que monta `scripts/brew-a-clon.mjs` (misma forma que `<clon>/data`,
  `docs/etl-brew-guia.md` §6).
- `<ADV>` es el código de 5etools **tal como lo escribe 5etools** (`CoS`, `LMoP`, `AUD`): da nombre
  al fichero `npc-cards.<ADV>.json`.

### B2 · Extraer con subagentes

Un subagente por parte (o varias aventuras cortas por subagente, hasta ~28-38k palabras), **todos
en un solo mensaje**, con el prompt de `references/npc-cards.md`. Cada uno escribe su array a una
ruta **explícita** del scratchpad de esta sesión: `<scratchpad>/npc-cards.<ADV>.part<N>.json`
(aunque haya una sola parte: el merge del paso siguiente fija el formato del fichero).

### B3 · Merge y validación

```bash
python3 compendium/merge-chunk-cards.py <ADV> --parts='<scratchpad>/npc-cards.<ADV>.part*.json'
```

**`--parts` es obligatorio**: el valor por defecto apunta al scratchpad de otra sesión y no existe.
El merge deja **una card por `slug`, la de narrativa más larga**, y escribe
`compendium/npc-cards.<ADV>.json` (`ensure_ascii=False, indent=2`: formato propio de las cards, no el
de `extract.json`). Después valida esquema, enums y **calidad del texto** según
`references/npc-cards.md` §*Validar antes de integrar*.

### B4 · Avatares

```bash
python3 compendium/resolve-npc-avatars.py --src=/tmp/5etools-src/data
```

Apunta `avatar_url` al arte fluff de 5etools (modo referencia): primero por el statblock propio de
la aventura y, si no, por el nombre del NPC. **Un cero sospechoso es un bug, no un dato**: un
`0/153` en CoS era una comparación case-sensitive de códigos de fuente (gotcha 7). Pocos avatares
puede ser real si el fluff de la aventura trae poco arte (AUD: 2 de 148).

### B5 · Integración y catálogo

Con el control del B0 ya vacío, el diff de este paso es solo la aventura nueva:

```bash
python3 compendium/integrate-npcs-to-graph.py
python3 compendium/integrate-factions-to-graph.py
node compendium/build-npc-catalog.mjs
```

- `integrate-npcs-to-graph.py` reconstruye **todos** los nodos-NPC desde todos los
  `npc-cards.*.json` (fuente única, idempotente): merge cross-aventura por nombre, aristas
  `aparece_en` NPC→lugar por co-ocurrencia del label del lugar en la narrativa, **solo** dentro de
  la misma aventura y **solo** contra `document` + `map-stub` (gotchas 26, 27 y 29). No toca lore ni
  map-stubs.
- `integrate-factions-to-graph.py` agrupa el campo `faccion` en nodos `faction` con aristas
  `pertenece_a`, solo para facciones con **2+ miembros**. Cero LLM.
- **`build-npc-catalog.mjs` no es opcional.** La app no lee los `npc-cards.*.json`, lee
  `npc-catalog.json`: sin regenerarlo, el buscador de NPCs no ve la aventura nueva y no da ningún
  error a la vista (pasó con POTA/GoS/JTTRC).

### B6 · Verificar que la app la ve

```bash
node -p "const c=require('./compendium/npc-catalog.json'); \
  [c.length, c.filter(x=>x.s==='<ADV>').length, new Set(c.map(x=>x.s)).size]"
```

Total de cards, cards de la aventura (las del B3) y número de aventuras distintas (sube en 1).

### B7 · Documentar y commitear

- `compendium/npc-cards.md` → fila de la aventura en la tabla y el titular (*N de N aventuras*).
- `compendium/pipeline-journal.md` → gotcha nuevo si apareció, y el delta exacto si el control
  del B0 no salió vacío.

```bash
git add compendium/ && git commit -m "Compendio: NPC cards de <ADV>"
```

---

## Consultar el compendio (la musa)

**Corre `graphify` desde `$QUESTKEEP/compendium/`**: busca `graphify-out/graph.json` relativo al
directorio actual (desde otro sitio, `graph file not found`; o pásale `--graph <ruta>`).

```bash
cd "$QUESTKEEP/compendium"
graphify query "<tema>"            # BFS desde los nodos que casan
graphify explain "<nodo>"          # un nodo y sus conexiones
graphify path "A" "B"              # camino más corto (solo intra-setting)
```

- Si `explain` responde *Ambiguous* (p. ej. `Zhentarim` es lore **y** facción), repite con el id
  completo: `faccion:zhentarim`, `canon:zhentarim`.
- Para arquetipos, lee los **hyperedges** y las comunidades de `graphify-out/GRAPH_REPORT.md`.
- Para un NPC concreto, `compendium/npc-catalog.json` (índice plano, sin CLI) es más rápido que el
  grafo — ver `dnd-worldbuilder/references/npc.md`.
- Cada consulta deja `graphify-out/cache/`; está en el `.gitignore` de questkeep.

Elige UN arquetipo/patrón como semilla y entrégalo a `dnd-worldbuilder`/`halo-session-prep` para
la Capa 3, limando nombres propios y tags de setting. El compendio es la musa; Supabase es la
fuente de verdad del mundo.

---

## Reglas

- **Nunca escribir a Supabase.** El compendio es solo-lectura del lado del mundo.
- **Nunca reconstruir el grafo entero ni canonicalizar la unión entera** (§*El grafo hoy*).
- **Modo referencia:** rutas de imagen y `cf_statblock: {kind,name,source}`; nunca binarios © WotC
  ni statblocks duplicados.
- **Verbatim desde la fuente** en el corpus (inglés, sin parafrasear). En las NPC cards, narrativa
  y enums en español y nombres de reglas en inglés. No commitear prosa cruda.
- **Serialización byte-estable:** `extract.json`/`graph.json` se escriben desde Python con
  `ensure_ascii=True, indent=2`. **Prohibido `JSON.stringify` de Node sobre ellos**: reformatea los
  ~15 MB enteros.
- **Control antes de cambiar** en cada integrador; diffs con `--patience`.
- **Una fuente a la vez.** La extracción por subagentes es el coste recurrente; reparte por
  presupuesto de palabras, no por fichero ni por aventura.
