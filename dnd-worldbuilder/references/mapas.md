# Mapas — reutilizar antes de inventar

Ciudades, establecimientos y lugares tienen un campo **`mapa_id`** («Mapa vinculado» en la app) que
apunta a **`mapa_nodos.id`**, el VTT de la campaña. Cuando crees o mejores una de esas tres entidades
—o el espacio de un combate— **propón un mapa que ya exista** antes de dejar el campo vacío o mandar
a generar uno. Es la misma regla que la musa (Paso 0.5) aplicada a la planta: lo ya dibujado por un
profesional es la primera opción, inventar es el último recurso.

## La escalera

Para en el primer peldaño que dé algo que encaje:

1. **Un mapa que la campaña ya tiene.** Si el sitio cae dentro de un mapa existente (la región, la
   ciudad), lo normal es **un pin** en ese mapa, no un mapa propio.
2. **Un mapa del catálogo del compendio:** 1.047 plantas de aventuras publicadas, filtrables por
   facetas (`query-map-index.mjs`).
3. **Generarlo** con la skill `battlemap`, que sale con la forma exacta de la escena (y puede usar un
   mapa del catálogo como semilla estructural).
4. **Sin mapa.** Para un combate, correr por **zonas** suele ser mejor que una rejilla (ver abajo).

### 1 · Lo que ya hay en la campaña

```sql
select id, nombre, img_url, parent_id from mapa_nodos
where campaign_slug = '<slug>' and tipo = 'map' and not archived
order by nombre;
```

Mira también qué entidades lo usan ya (`select nombre, mapa_id from lugares where campaign_slug = '<slug>' and mapa_id is not null`,
ídem `ciudades`/`establecimientos`): un mapa de ciudad ya vinculado a la ciudad padre es justo el
sitio donde va el pin del establecimiento nuevo. **Proponer el pin no es escribirlo**: los pins
(`mapa_pines`, con `link_type`/`link_id`) los coloca el DM en el visor, porque la posición `x/y` sobre
la imagen no se adivina desde aquí.

### 2 · El catálogo del compendio

> **Corre los comandos desde la raíz del clon de questkeep.** Las rutas son relativas; desde otra
> carpeta fallan con `Cannot find module` / `ENOENT`.

Traduce la entidad a las claves **cerradas** de `compendium/map-taxonomy.json` (el script rechaza las
que no existen). OR dentro de un eje, AND entre ejes:

| Eje | Claves válidas |
|---|---|
| `tipo` | templo, mazmorra, guarida, fortaleza, asentamiento, taberna, tienda, casa, cueva, ruinas, campamento, barco, region |
| `ambiente` | bosque, nieve, desierto, pantano, montana, costa, subterraneo, urbano, infernal, acuatico |

Punto de partida por entidad (el `ambiente` sale del bioma de la ciudad/región):

| Entidad | `--tipo` | `--ambiente` |
|---|---|---|
| Establecimiento · Taberna | `taberna` | `urbano` (o el del bioma si es de camino) |
| Establecimiento · Comercio / Herrero / Tienda | `tienda,casa` | `urbano` |
| Establecimiento · Templo | `templo` | `urbano` |
| Establecimiento · Gremio | `casa,fortaleza` | `urbano` |
| Lugar · Dungeon/Ruina | `mazmorra,ruinas` | el del entorno |
| Lugar · Cueva | `cueva,guarida` | el del entorno (+ `subterraneo`) |
| Lugar · Naturaleza | `campamento,ruinas,guarida` | el bioma |
| Lugar · Zona urbana | `casa,tienda,asentamiento` | `urbano` |
| Ciudad | `asentamiento` (+ `region` para el entorno) | el bioma |
| Combate | según el espacio narrado | según el entorno |

```bash
node compendium/query-map-index.mjs --tipo=taberna --ambiente=urbano --top=5
```

Salida real (recortada a dos; ordena por número de salas):

```
[BGDIA] Map 1.2: Elfsong Tavern · Tavern Patrons
   13 salas · 36x18 cuadros · taberna / urbano
   imagen https://raw.githubusercontent.com/5etools-mirror-3/5etools-img/main/adventure/BGDIA/008-awf96-map-1-2-dm.webp
   thumb  https://raw.githubusercontent.com/5etools-mirror-3/5etools-img/main/adventure/BGDIA/thumbnail/008-awf96-map-1-2-dm.webp
[BGDIA] Map 1.4: The Low Lantern · Tavern Patrons
   8 salas · 36x23 cuadros · taberna / urbano
   …
```

Flags útiles: `--salas` (solo plantas con salas declaradas) y `--cuadros=40x25` (techo de tamaño,
para descartar los pósters de aventura entera en un combate). Si no sale nada, **dilo en una línea y
baja al siguiente peldaño**; no reintentes con otras facetas más de una vez.

**De la planta elegida sale también sabor.** `compendium/place-index.json` (2,5 MB: extrae la
entrada suelta por `path`, no lo leas entero) trae la descripción del sitio y, en 169 de las 1.055 fichas,
su **read-aloud**, en inglés verbatim. Sirve de semilla para `cf_atmosfera` / descripción interior: se **parafrasea** al
español y se **lima** como cualquier átomo de la musa (fuera topónimos, nombres propios, deidades).

```bash
node -e "const p=require('./compendium/place-index.json').find(x=>x.path==='<path>');
console.log(p ? JSON.stringify({d:p.descripcion, ra:p.read_aloud}, null, 1) : '(sin ficha)')"
```

## Cómo se propone

En la propuesta (Paso 3), una sección **Mapa** con **hasta 3 candidatos**: fuente, título, salas,
tamaño y el enlace a la miniatura, más una línea de por qué encaja. El DM elige uno, pide otros o dice
«sin mapa».

**Di siempre de qué peldaño salió**, también cuando no salió nada: *«la campaña no tiene un mapa que
sirva y el catálogo no trae plantas de muelle abierto; propongo generarlo con `battlemap`»*. Igual
que con las npc-cards, una vía que degrada en silencio parece que funcionó.

## Cómo se escribe (Paso 5, con confirmación)

Peldaño 1: solo `mapa_id = <id existente>` en la fila de la entidad.

Peldaño 2: el mapa se crea en el VTT **como lo hace el buscador del Compendio de la app**
(`maps.js` → `compendioCrear`) y después se vincula:

```sql
-- 1. ¿Ya está en el VTT? La app lo marca como «ya lo tienes»; no crees el mismo nodo dos veces.
select id from mapa_nodos
where campaign_slug = '<slug>' and tipo = 'map' and img_url = '<url imagen>' and not archived;

-- 2. Si no está: el nodo, OCULTO a los jugadores (la variante del catálogo es la del DM, con
--    etiquetas y números de sala) y con orden = epoch ms, como addNode.
insert into mapa_nodos (campaign_slug, tipo, nombre, parent_id, img_url, players_visible, orden)
values ('<slug>', 'map', '<nombre en la campaña>', <carpeta o null>, '<url imagen>', false,
        (extract(epoch from now()) * 1000)::bigint)
returning id;

-- 3. Vincularlo.
update lugares set mapa_id = '<id>' where id = '<lugar>';   -- o ciudades / establecimientos
```

- **`nombre` es el de la campaña** («Bodegas del canal bajo»), no el del libro («Elfsong Tavern»):
  el nombre del nodo lo ve la mesa.
- **`img_url` es la URL completa** del img repo de 5etools (`imagen` en la salida del script).
  **Modo referencia:** la imagen no se descarga ni se sube a ningún sitio; QuestKeep no hospeda
  binarios © WotC.
- **`parent_id`:** pregunta en qué carpeta del VTT va; `null` es la raíz.
- Alternativa equivalente: que el DM lo importe él desde la app (**Mapas → Compendio**) y tú solo
  pongas `mapa_id`.

## Gotchas

- **El catálogo es de interiores.** Son plantas cenitales de espacios cerrados (mazmorras,
  tabernas, criptas, fortalezas por dentro, pueblos desde arriba). Una plaza abierta frente a una
  fachada, un asalto a una muralla desde fuera, una persecución por tejados o una batalla entre dos
  barcos casi no existen: no gastes turnos buscándolos, baja a `battlemap`.
- **Solo hay variante DM** en `map-catalog.json` (etiquetas y números encima). Por eso el nodo nace
  oculto; para enseñarlo a la mesa hay que tapar las etiquetas o generar la versión de jugadores.
- **Para un combate, pregúntate si necesita rejilla.** El modelo vigente del Lazy DM son **zonas**
  (`questkeep/docs/lazy-dm-manual.md` §6.2). Si el clímax está escrito en tramos o «arriba / abajo»,
  ofrece las opciones (sin mapa · catálogo · `battlemap`) y deja elegir al DM.
- **Un mapa del catálogo arrastra su setting** en el título y en la ficha del `place-index`. Lima
  igual que con el grafo: se reutiliza la planta, no Baldur's Gate.
