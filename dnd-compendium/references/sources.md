# Fuentes 5etools — qué archivo por tipo de contenido

El corpus se construye desde un clon de `5etools-mirror-3/5etools-src` (efímero, en `/tmp`).
El texto de los libros **no vive en el repo ni en el entorno** — reclonar cada sesión
(ver `CLAUDE.md` de questkeep).

```bash
git clone --depth 1 https://github.com/5etools-mirror-3/5etools-src.git /tmp/5etools-src
```

## Archivos por tipo

| Contenido | Ruta en el clon |
|-----------|-----------------|
| Prosa del libro (lore, dominios, géneros, diseño, aventuras, apéndices) | `data/book/book-<id>.json` |
| Statblocks de criaturas | `data/bestiary/bestiary-<id>.json` |
| Lore/fluff de criaturas (descripciones narrativas) | `data/bestiary/fluff-bestiary-<id>.json` |
| Magic items (todos los libros en un archivo; filtrar por `source`) | `data/items.json` |
| Texto narrativo de aventuras | `data/adventure/adventure-<id>.json` |

`<id>` es el código de fuente en minúsculas (p. ej. `rhw` para *Ravenloft: The Horrors Within*).
Las fuentes activas de QuestKeep viven en `questkeep/data/5e/meta.json → sources`.

## Notas

- El **constructor de corpus** (`questkeep/scripts/build-compendium-corpus.mjs`) infiere el `kind`
  de cada sección por heurística de capítulo + overrides. Si un libro nuevo tiene una estructura
  de capítulos distinta, revisa el `_corpus-manifest.json` que emite y ajusta los sets
  `EXPLODE`/`SKIP`/`chapterKind` del script (en questkeep) antes de ingerir.
- La sección de bestiary **dentro del libro** suele ser solo punteros a statblocks; la prosa real
  vive en `bestiary-<id>.json` + `fluff-bestiary-<id>.json`. Por eso se pasan aparte.
- El handler `{@area}` del ETL devuelve el ID del área, no el texto; el constructor de corpus ya
  lo corrige (pre-pasa el primer segmento). Cualquier `{@...}` que sobreviva es un bug a reportar.
- El orden de filas de bestiary/items **no es determinista** entre máquinas (depende de
  `readdirSync`); el conjunto de entidades es lo que importa, no el orden.

## Homebrew / 3rd-party (no viven en `5etools-src`)

El contenido homebrew y de terceros vive en un repo aparte, **`TheGiddyLimit/homebrew`**, no en
`5etools-src`. El hash de 5e.tools (`book.html#<id>` / `adventure.html#<id>`) es el `source.json`
del brew. Para ubicar el archivo:

```bash
# sparse-clone (el repo es enorme; solo metadatos + el dir que necesitas)
git clone --depth 1 --filter=blob:none --sparse https://github.com/TheGiddyLimit/homebrew.git /tmp/homebrew
cd /tmp/homebrew && git ls-tree -r HEAD --name-only | grep -i "<título o autor>"   # localizar
git sparse-checkout set adventure book collection                                   # materializar
```

Los brew se nombran `Autor; Título.json` (en `adventure/`, `book/`, `collection/`, …). Su forma
difiere del book oficial: usan wrappers `{adventure, adventureData, book, bookData}` en vez de
`{data:[...]}`. El **constructor de corpus ya los soporta** (`loadChapters`): cada aventura se
emite como una unidad completa `kind: adventure`; el book acompañante se recorre por subsecciones.
Muchos brew **no traen bestiary/items propios** — sus criaturas son refs `{@creature}` al catálogo
oficial, así que el tejido cross-book sale de las criaturas compartidas.

## Ejemplo: RHW (Ravenloft: The Horrors Within)

```bash
node "$QUESTKEEP/scripts/build-compendium-corpus.mjs" \
  --book=/tmp/5etools-src/data/book/book-rhw.json \
  --bestiary=/tmp/5etools-src/data/bestiary/bestiary-rhw.json \
  --fluff=/tmp/5etools-src/data/bestiary/fluff-bestiary-rhw.json \
  --items=/tmp/5etools-src/data/items.json \
  --source=RHW --out=/tmp/compendium-corpus
# → 48 archivos: 17 domain, 10 genre, 8 horror-craft, 4 design-grammar, 3 tarokka,
#   2 setting-grammar, 2 character-option, 1 bestiary (70 statblocks), 1 items (Ebonbane, Harkon's Bite)
```
