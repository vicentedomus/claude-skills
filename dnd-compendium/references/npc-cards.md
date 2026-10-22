# NPC cards — esquema, vocabulario y prompt de extracción

Una **NPC card** es la parte *narrativa* de un NPC de aventura (físico, carácter, manerismos,
ganchos) más una **referencia** a su statblock. Su esquema es **espejo de la tabla `npcs`** de la
campaña Halo, para que una card caiga 1:1 en una fila al instanciarla (con reskin). Hoy hay 5866
cards de 100 aventuras en `questkeep/compendium/npc-cards.<ADV>.json`.

La fuente de verdad del estado (qué aventuras hay, cuántas cards, comparables de tamaño) es
`questkeep/compendium/npc-cards.md`. Este fichero es lo que el subagente necesita para **extraer**.

## Esquema

```json
{
  "nombre": "Delraz",
  "raza": null,
  "tipo_npc": "Arcanista",
  "rol": "Antagonista",
  "estado": "Vivo",
  "edad": null,
  "faccion": "Council of Zulkirs",
  "familia": null,
  "primera_impresion": "Zulkir de Encantamiento, defensor del orden tradicional thayano… La fuente no describe su aspecto ni indica su especie.",
  "notas_roleplay": "Conspirador y manipulador… Úsalo como la cara «legal» de la opresión: no amenaza, legisla.",
  "cf_statblock": { "kind": "compendium", "name": "Enchanter Archmage", "source": "AU" },
  "avatar_url": null,
  "slug": "delraz"
}
```

| Campo | Contenido | Idioma |
|---|---|---|
| `nombre` | Nombre propio tal como lo escribe la fuente | el de la fuente |
| `raza` | Enum de Halo (abajo) o `null` | español |
| `tipo_npc` | Enum de Halo (abajo) | español |
| `rol` | `Aliado` · `Neutral` · `Enemigo` · `Antagonista` · `Informante` | español |
| `estado` | `Vivo` · `Muerto` (al empezar la aventura) | español |
| `edad` | Entero si la fuente la da; si no, `null` | — |
| `faccion` | Organización a la que pertenece, **con el nombre que usa la fuente** (`Zhentarim`, `Red Wizards of Thay`) | el de la fuente |
| `familia` | Casa o linaje si la fuente lo dice | el de la fuente |
| `primera_impresion` | Lo que se ve al conocerlo: físico, porte, ropa. Si la fuente no lo describe, **dilo** («la fuente no describe su aspecto») en vez de inventarlo | español |
| `notas_roleplay` | Carácter, manerismos, motivación, secretos, ganchos, y una línea de cómo usarlo en mesa | español |
| `cf_statblock` | `{kind:"compendium", name, source}` — el statblock que la aventura le asigna, **por referencia**; `null` si no tiene | `name` en **inglés** |
| `avatar_url` | Déjalo `null`: lo rellena `resolve-npc-avatars.py` | — |
| `slug` | `nombre` en minúsculas, ASCII, guiones (`kelra-ironweaver`) | — |

`cf_statblock.source` es la **fuente real** del statblock (`XMM`, `MPMM`, `MPP`, `AU`…), no se fuerza
a `XMM`. Los statblocks **no se copian**: QuestKeep ya los tiene en `data/5e/bestiary.json`.

### Vocabulario cerrado (el de Halo, no uno inventado)

Los enums salieron de los valores reales de la tabla `npcs` en Supabase. **No se amplían sin
decisión del DM.**

- **`raza`:** `Humano` · `Elfo` · `Enano` · `Gnomo` · `Mediano` · `Tiefling` · `Semielfo` · `Orco` ·
  `Dracónido` · `Semiorco` · `Goliath` · `Aasimar`. Cualquier otra (dragón, kobold, goblin, owlin,
  giff, dríade…) → **`null`**. Usa `Semiorco`, no «Medio orco» (el catálogo colapsa las dos, pero
  mejor no generar la variante).
- **`tipo_npc`:** `Comerciante` · `Tabernero` · `Herrero` · `Alquimista` · `Minero` · `Granjero` ·
  `Arcanista` · `Bibliotecario` · `Religioso` · `Guardia` · `Cazador` · `Aventurero` · `Criminal` ·
  `Proxeneta` · `Noble` · `Líder político` · `Gremio` · `Otro`. Con tilde: `Líder político` (sin
  ella el catálogo tiene que corregirlo).

Si hubiera dudas sobre la lista vigente, la manda el overlay de la campaña (`entity_schemas`,
`section='npcs'`), no este documento — ver `dnd-worldbuilder/references/catalogos.md`.

## Prompt del subagente

Un subagente por parte de corpus (≤ ~45k palabras). Plantilla — sustituye `<ADV>`, `<CORPUS>` y
`<SALIDA>`, y pega el esquema y el vocabulario de arriba:

```
Lee el corpus de la aventura <ADV> en <CORPUS> y extrae una NPC card por cada NPC con nombre
que tenga presencia en escena. Escribe un array JSON a <SALIDA> (UTF-8, con acentos) y
devuelve un resumen de una línea: cuántas cards y a quién excluiste y por qué.

Esquema y vocabulario: <pegar §Esquema y §Vocabulario cerrado>.

Reglas:
- Narrativa y enums en ESPAÑOL; cf_statblock.name en INGLÉS (contenido de reglas).
- Escribe CON acentos. El pipeline serializa con ensure_ascii y nunca ha tenido problemas de
  codificación: no te impongas una restricción que nadie pidió.
- Incluye: NPCs con nombre y escena, y criaturas con nombre que tengan diálogo o personalidad
  (raza: null, tipo_npc: "Otro").
- Excluye: monstruos genéricos sin nombre, animales o mascotas con nombre, deidades, PCs
  pregenerados de apéndice y figuras puramente históricas sin escena.
- No rellenes: un elenco corto es un dato, no un fallo. No inventes NPCs ni detalles.
- Si la fuente no describe el físico, dilo en primera_impresion en vez de inventarlo.
- Contradicciones de la fuente (grafías, género inconsistente): anótalas en notas_roleplay; no
  las resuelvas inventando.
- faccion: rellénala siempre que el texto la diga. Con 2+ miembros se convierte en un hub del
  grafo; sin ella el NPC queda aislado.
- Razas fuera del enum → null. tipo_npc fuera del enum → "Otro". No amplíes los enums.
- cf_statblock: el que la aventura le asigna, con su fuente real. null si no tiene ninguno.
- avatar_url: null (lo resuelve otro script).
```

Despacha **todos** los subagentes **en un solo mensaje**. Reparte por **presupuesto de palabras**,
no por aventura: una aventura grande se trocea (`--chunk=45000`) y varias pequeñas se agrupan en un
mismo subagente hasta ~28-38k palabras (las 49 one-shots del corpus se hicieron con 12 subagentes en
vez de 49).

## Validar antes de integrar

1. **Esquema:** todas las cards con `nombre`, `slug`, `primera_impresion` y `notas_roleplay`; el
   integrador usa `.get()` para lo opcional, pero una card sin `slug` se descarta en el merge.
2. **Enums:** `raza`, `tipo_npc`, `rol` y `estado` dentro de su lista.
3. **Calidad del texto, no solo el conteo.** Abre 3-5 cards y léelas: acentos presentes, nombres de
   reglas en inglés, descripción real en vez de resúmenes de una línea. Un JSON válido con 25 cards
   puede traer la prosa degradada (pasó con HOL: 25 cards sin acentos). Si pasa, reenvía al mismo
   subagente.
4. **Un número raro es una pista.** Muy por debajo de lo esperable para el tamaño y el tono de la
   aventura (comparables en `npc-cards.md`) suele ser una extracción truncada. Las urbanas o
   políticas dan muchas más cards por palabra que los dungeon crawls.
