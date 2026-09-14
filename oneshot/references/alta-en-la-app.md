# Alta en la app — tablas, ids vigentes y la mesa del reskin

El árbol es la chuleta; estas filas son lo que el árbol **lee en vivo**. Un bloque `npc` sin su
fila de `npcs` no pinta nada.

> **Nunca escribas en Supabase sin confirmación del DM.**

## Prerequisito: el overlay

`qkEffectiveSchema` (`app.js`) = `FORM_SCHEMAS[section]` + `overlay.customFields` de
`entity_schemas`. **Un `cf_*` que no esté declarado en el overlay de esa campaña se guarda y no se
ve.** Compruébalo antes de escribir:

```sql
select section, jsonb_pretty(overlay->'customFields')
from entity_schemas where campaign_slug = 'one-shots';
```

En `one-shots` ya existen (no hace falta crearlos):

| Sección | Campo | Tipo | Para qué |
|---|---|---|---|
| `npcs` | `cf_statblock` | `statblock`, dmOnly | el statblock del NPC |
| `npcs` | `cf_rasgos` | `textarea`, dmOnly | Rasgo · Ideal · Vínculo · Defecto |
| `npcs` | `cf_inspiracion` | `text`, dmOnly | de dónde salió (módulo o card del compendio) |
| `lugares` | `cf_lugar_padre` | `select-rel` → `lugares` | el contenedor (gazetteer) |
| `lugares` | `cf_lectura` | `textarea` | para leer en voz alta |
| `lugares` | `cf_mecanica` | `textarea`, dmOnly | mecánica y disparadores |

## Checklist de alta

- [ ] **`lugares`** — para un gazetteer, una fila por locación. El índice de salas lo **deriva el
      motor** (`inverseRelationsHTML`) desde `cf_lugar_padre`; no se mantiene a mano.
- [ ] **`npcs`** — el elenco. Carril A: nombres verbatim. Carril B: reskineados, con
      `cf_inspiracion` diciendo de qué card salieron.
- [ ] **`items`** — los que importan, con lo que hacen.
- [ ] **`quests`** — la quest paraguas del one-shot.
- [ ] **`mapa_nodos`** — carpeta por aventura + versión DM (`players_visible = false`) + versión de
      jugadores (`players_visible = true`). `compendioCrear` nace **todo visible**: el reparto lo
      haces tú.
- [ ] **`mapa_pines`** — un pin por locación. Es lo que vuelve el plano una interfaz.
- [ ] **`encuentros`** — uno por pelea.
- [ ] **`monstruos`** — **solo** si hay reskin con nombre propio (ver abajo).

### Gotchas medidos

**`cf_lugar_padre` es un objeto, no un uuid.** Es `select-rel`, y se guarda como
`{"id": "<uuid>", "nombre": "<nombre>"}`. Escribir el uuid pelado no rompe el `INSERT` y deja la
relación muda.

```jsonc
"cf_lugar_padre": { "id": "17793171-…", "nombre": "Chalet Brantifax" }
```

**`mapa_pines` usa snake_case en la base**, aunque el JS hable en camel: `link_type` (no
`linkType`), `link_id`, `players_visible`, `target_map_id`. Las coordenadas `x`/`y` son
**fracciones 0-1** del contenedor, no píxeles. La forma que ya usa la campaña:

```jsonc
{ "kind": "linked", "link_type": "lugar", "link_id": "<uuid del lugar>",
  "icon": "pin", "color": "#cc88ff", "size": "md", "players_visible": true,
  "x": 0.476, "y": 0.332 }
```

### Los selects rígidos: la base acepta lo que la UI no pinta

**Hay nueve campos con lista cerrada de opciones, y la base no los valida.** Escribes un valor
fuera del enum, el `INSERT` pasa sin una queja, y **el formulario de edición pinta ese campo en
blanco**. Es el mismo modo de fallo que el `cf_*` no declarado: se guarda y no se ve.

Se cometió seis veces en una sola corrida — `rol: 'Antagonista'` (el enum solo tiene
`Neutral/Aliado/Enemigo`), `tipo_npc: 'Intendente'/'Clérigo'/'Minera'/'Oficial'`, y en `items` un
`tipo`/`rareza` escritos **en español** cuando el enum está en inglés. Las cuatro fichas de NPC se
veían perfectas en la vista de detalle; el error solo aparece al abrir el formulario.

**Listas las opciones vigentes antes de escribir, no de memoria:**

```bash
node -e "
const s = require('fs').readFileSync('app.js','utf8');
const m = s.match(/const FORM_SCHEMAS\s*=\s*\{[\s\S]*?\n\};/)[0];
const re = /key:'([^']+)'[^}]*?type:'(select|combo-creatable)'[^}]*?options:\[([^\]]*)\]/g;
let x; while ((x = re.exec(m))) console.log(x[2].padEnd(16), x[1].padEnd(22), x[3].replace(/'/g,''));
"
```

Medido el 2026-09-14:

| Sección · campo | Tipo | Opciones |
|---|---|---|
| `npcs.rol` | `select` | Neutral · Aliado · Enemigo |
| `npcs.estado` | `select` | Vivo · Muerto |
| `npcs.tipo_npc` | `select` | Comerciante · Tabernero · Herrero · Alquimista · Minero · Granjero · Arcanista · Bibliotecario · Religioso · Guardia · Cazador · Aventurero · Criminal · Proxeneta · Noble · Líder político · Gremio · Otro |
| `items.tipo` | `select` | **en inglés**: Armor · Potion · Ring · Rod · Scroll · Staff · Wand · Weapon · Wondrous Item |
| `items.rareza` | `select` | **en inglés**: Common · Uncommon · Rare · Very Rare · Legendary · Artifact |
| `quests.estado` | `select` | Activa · Completada · Fallida · En Pausa |
| `lugares.estado_exploracion` | `select` | Sin explorar · Parcialmente explorado · Explorado |
| `lugares.tipo` · `establecimientos.tipo` | **`combo-creatable`** | sugerencias, **no** lista cerrada: aquí sí puedes inventar |

**Dos reglas que salen de ahí:**

- **`select` es cerrado, `combo-creatable` es abierto.** Sólo esa palabra en el schema decide si tu
  valor sobrevive. Si el campo es `select` y tu concepto no está en la lista, **elige el más
  cercano del enum y mete el matiz en la prosa** — no fuerces un valor nuevo.
- **`items.tipo` y `items.rareza` van en inglés**, como todo contenido de reglas (CLAUDE.md). Es el
  único par de enums que no está en español, y por eso es el que más se escapa.

Y un campo vacío también es una opción legítima: *La Losa* va con `tipo = ''` porque no es mágica y
ninguna de las diez categorías le queda. Eso es una decisión, y se dice (§Reglas duras 3).

## Los ids de monstruo: hay DOS convenciones vivas

No es una inconsistencia que puedas ignorar — cada camino de la app lee el suyo.

| Dónde | Formato | Quién lo resuelve |
|---|---|---|
| `encuentros.monsters[].id` | **`srd:<FUENTE>:<Nombre>`** | `findMonstruo` (`react/encuentros/logic.ts`) |
| Homebrew de campaña | `cat:<uuid de monstruos>` | idem |
| `cf_statblock` de un NPC | **no es un id**: `{kind, name, source}` | `app.js` (vanilla) |
| Pines y fichas vanilla | `srd:<Nombre>` a secas | `bestiarioRowById` (`srd-adapters.js`) |

**Por qué el encuentro lleva fuente y el pin no.** Con los seis libros del brew dentro hay **36
nombres repetidos** con XMM (Owlbear, Lich, Kraken, Ankheg…) y **57 filas compartían identidad**.
Se cualificaron los ids del constructor de encuentros; el camino vanilla se quedó en el formato
viejo. `findMonstruo` **acepta el formato viejo** degradando a búsqueda por nombre, así que los
encuentros ya guardados siguen resolviendo — pero **lo que escribas nuevo va con fuente**.

El daño de no hacerlo no es cosmético: el Kraken de FM es **CR 26** y el de XMM **23**, así que el
presupuesto reserva un número y el semáforo cobra otro.

```jsonc
// encuentros.monsters
[ { "id": "srd:XMM:Goblin Warrior", "count": 4 },
  { "id": "srd:FleeMortals:Ankheg", "count": 1 },
  { "id": "cat:9f1c…", "count": 1 } ]          // reskin propio
```

```jsonc
// npcs.custom_data.cf_statblock
{ "kind": "compendium", "name": "Wereraven", "source": "RHW" }
```

## `encuentros`: las columnas que hay hoy

`id · campaign_slug · nombre · descripcion · link · monsters · party · hazards · companions ·
estrategia · archived · user_id`

- **`estrategia`** — `'dnd2024'` (default) o `'fm'`. **Sin CHECK a propósito**: el conjunto de
  reglamentos lo define el cliente. Se degrada al default si el valor es desconocido
  (`estrategiaDe`).
- **`party`** — array de uuids de `personajes`. Es lo que hace que la dificultad se recalcule
  sola; un encuentro sin party no tiene semáforo.
- **`hazards`**, **`companions`** — arrays; vacíos si no aplican.
- **`descripcion`** — aquí va lo operativo: **si es evitable, qué la dispara, y el presupuesto
  contra el de la party**. Y si las dos ediciones del monstruo difieren, dilo: el DM va a leer el
  read-aloud de una y tirar los dados de la otra.

## La mesa del reskin: `monstruos`

Un reskin con nombre propio («el Xolo de Xibalbá» en vez de «Strahd von Zarovich») necesita fila
propia, o la iniciativa lo va a pintar con el nombre oficial y se rompe la ficción en el peor
momento.

`monstruos` es el bestiario **por campaña** (`campaign_slug`), con las mismas columnas que una
ficha del ETL más tres propias:

| Columna | Qué poner |
|---|---|
| `nombre` | el nombre reskineado |
| `base` | **el nombre oficial del statblock del que salió** — es el rastro |
| `es_homebrew` | `true` |
| `tipo` | el tipo con el **rol de FM en el paréntesis** si el clímax corre en `fm`: `humanoid (Solo)` |

Los números (`ac`, `hp`, `cr`, `rasgos`, `acciones`, `acciones_legendarias`…) se copian **tal cual**
del statblock base. `rolDe()` lee el rol del paréntesis de `tipo` igual en homebrew que en oficial,
así que un reskin conserva su rol y el semáforo de FM sigue funcionando.

El encuentro lo referencia como `cat:<uuid>`, y `normalizeCatalogMonster` lo mete al mismo pool que
los oficiales.

**Cuándo NO hace falta una fila:** si el reskin solo cambia la ficción y no el nombre que ve la
mesa en iniciativa, basta con el NPC (`npcs` + `cf_statblock` apuntando al oficial) y una nota en
`encuentros.descripcion`. Una fila de `monstruos` por cada goblin repintado es trabajo tirado.

## Tirar del compendio antes de escribir a mano

| Capa | Qué da | Dónde |
|---|---|---|
| Mapas | **1.047** mapas (1.942 fichas: cada uno puede traer variante DM y de jugadores) con grid, escala y nº de salas | `compendium/map-catalog.json` · busca con `query-map-index.mjs` |
| Lugares | **1.055** con descripción **y read-aloud** | `compendium/place-index.json` |
| NPCs | **5.866** cards, esquema **espejo de la tabla `npcs`** | `compendium/npc-catalog.json` + shards `npc-cards.<FUENTE>.json` |
| Lore | grafo de 10.488 nodos | `compendium/graphify-out/graph.json` |

Los NPCs y los mapas se importan **desde la app** (`react/npccompendio`, `react/compendium`), que
ya escribe la fila con `cf_inspiracion` puesto. El read-aloud del `place-index` viene **en inglés
verbatim de la fuente**: se parafrasea al español al copiarlo a `cf_lectura`, marcado como
paráfrasis.

> El compendio **nunca** escribe a Supabase por su cuenta: se consulta. Lo que cruza la frontera lo
> escribes tú, con el DM enterado.

### El corpus de mapas es de INTERIORES, y eso limita qué se puede buscar

**Antes de gastar turnos buscando: el catálogo son plantas cenitales de espacios cerrados.** Los
1.047 mapas vienen de aventuras publicadas, y en una aventura publicada los combates pasan *dentro*
de los cuartos. Hay mazmorras, torres, tabernas, criptas, fortalezas por dentro y pueblos vistos
desde arriba.

**Lo que casi no existe: «una plaza abierta mirando la fachada de un edificio».** Se buscó por
faceta (`--tipo=fortaleza --ambiente=urbano`), por palabra (`courtyard`, `granary`, `warehouse`,
`garrison`, `plaza`, `gate`, `siege`) y por forma, y no salió — **no por buscar mal, sino porque
ese tipo de mapa apenas se publica.** Lo mejor que dio fue `Legion Garrison` (GGR): *«el acceso se
limita a dos pasarelas elevadas protegidas por arqueros tras troneras»*, que es la situación
correcta con la piel equivocada.

Lo mismo vale para: un asalto a una muralla desde fuera, una emboscada en campo abierto, una
persecución por tejados, una batalla naval entre dos cubiertas. **Si tu clímax pasa afuera mirando
hacia algo, el catálogo probablemente no lo tiene.**

**Dos gotchas al usar lo que sí hay:**

- **`map-catalog.json` solo trae la variante DM** (`build-map-catalog.mjs` excluye la de jugador a
  propósito). Las imágenes llevan etiquetas y números encima, así que para repartir a la mesa hay
  que taparlos o generar la versión de jugadores aparte.
- **1.047 ≠ 1.942.** `map-index.json` tiene 1.942 **fichas** porque un mismo plano aparece dos
  veces si trae variante DM y de jugadores. Mapas distintos son 1.047.

**Y antes de pedir un mapa, pregúntate si el combate lo necesita.** El Lazy DM §6.2 dice que el
modelo vigente son **zonas**, no cuadrícula. Si tu clímax está escrito en tramos, bandas o «arriba
/ abajo» —y los buenos suelen estarlo— **un mapa con rejilla te obliga a traducirlo a casillas y a
discutir movimiento**, que es justo la fricción que se come los minutos que blindaste para el
final. Ofrece las tres opciones y deja que el DM elija:

1. **Sin mapa**, corriendo por zonas. Un trazo en papel basta.
2. **Generarlo** con la skill `battlemap`, que sale con la forma exacta que pediste.
3. **Un mapa del catálogo** para lo que sí es interior — el después del asalto, no el asalto.
