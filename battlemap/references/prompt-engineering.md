# Prompt Engineering Reference — Battlemap Skill

Referencia interna que Claude carga al activar la skill. Contiene catálogos de locaciones, keywords de materiales, recetas de iluminación y descriptores de estilo para construir prompts optimizados para Gemini Image.

---

## A. Catálogo de locaciones D&D

Cada entrada incluye dimensiones típicas, materiales, props clave y paleta sugerida. Usar como base cuando el usuario no da detalles específicos.

### Interiores

| Locación | Dimensiones | Piso | Paredes/Límites | Props clave | Paleta |
|---|---|---|---|---|---|
| Taberna | 30×20 ft | Worn wooden planks, ale stains | Stone with timber frame, wooden bar counter | Tables, chairs, barrels, fireplace, chandelier, stairs to upper floor | Warm browns, amber, orange firelight |
| Templo | 40×30 ft | Polished marble or stone tiles | Carved stone columns, stained glass windows | Altar, pews, braziers, holy symbols, offering bowls, tapestries | Gold, white, deep blue or crimson accents |
| Mazmorra (sala) | 30×30 ft | Rough-hewn stone, cracks, moss | Damp stone blocks, iron torch sconces | Chains, bones, rubble, puddles, broken furniture, locked chest | Dark gray, green moss, rust orange |
| Mazmorra (pasillo) | 60×10 ft | Uneven stone slabs | Narrow stone corridor, cobwebs | Torch sconces, arrow slits, pressure plates, debris | Dark gray, flickering orange |
| Sala del trono | 50×30 ft | Polished stone or marble, red carpet runner | Grand stone walls, tall windows, banners | Throne on dais, pillars, guards' alcoves, braziers, tapestries | Royal purple, gold, deep red |
| Prisión/celda | 20×20 ft | Cold stone, straw | Iron bars, stone blocks | Shackles, bucket, rats, straw bedding, locked door | Gray, rust, sickly yellow |
| Biblioteca | 30×25 ft | Dark wood parquet | Floor-to-ceiling bookshelves | Reading tables, ladders, candelabras, scattered scrolls, globe | Rich brown, parchment cream, green leather |
| Laboratorio alquímico | 25×20 ft | Stained stone tiles | Stone walls with shelves of bottles | Workbenches, bubbling flasks, cauldron, ingredient jars, smoke | Purple, green, amber, glass reflections |
| Cocina/almacén | 20×15 ft | Flagstone, grease stains | Stone walls, hooks and shelves | Large hearth, hanging meats, barrels, crates, pots, flour sacks | Warm brown, cream, copper |
| Arena/pit de pelea | 40×40 ft | Sand or packed earth | Wooden walls or stone, spectator seats above | Weapon racks, bloodstains, gates, pillars for cover | Tan, dark red, weathered wood |
| Cueva interior | 35×25 ft | Uneven natural rock, stalagmites | Rough cave walls, crystal deposits | Underground pool, mushrooms, bones, narrow passages | Dark purple-gray, bioluminescent blue-green |
| Barco (cubierta) | 40×15 ft | Wooden deck planks | Ship rails, masts, rigging | Cannons, cargo, helm, stairs to below deck, ropes | Sea-weathered brown, rope tan, brass |
| Barco (bodega) | 35×12 ft | Wooden hull floor, bilge water | Curved wooden hull walls | Cargo crates, hammocks, barrels, rats, lanterns | Dark brown, murky green, dim yellow |

### Exteriores naturales

| Locación | Dimensiones | Terreno | Límites | Props clave | Paleta |
|---|---|---|---|---|---|
| Claro del bosque | 40×30 ft | Grass, fallen leaves, tree roots | Dense treeline, underbrush | Fallen log, mushroom ring, stream, wildflowers, animal tracks | Forest green, dappled gold, earth brown |
| Río/vado | 50×30 ft | Riverbed stones, muddy banks | River through center, trees on banks | Stepping stones, fallen tree bridge, reeds, fish | Blue-green water, muddy brown, gray stone |
| Camino del bosque | 60×20 ft | Dirt path, wheel ruts | Dense forest on both sides | Signpost, wagon tracks, ambush spots behind trees, bridge | Brown path, dark green, shadow |
| Cueva (entrada) | 30×25 ft | Rocky ground, gravel | Cliff face with cave mouth | Boulders, campfire remains, bones, stalactites | Gray rock, dark shadows, warm firelight |
| Pantano | 40×30 ft | Murky water, mud islands, dead grass | Fog, dead trees, deep water edges | Dead trees, lily pads, will-o-wisps, sunken logs, quicksand | Sickly green, murky brown, gray fog |
| Playa/costa | 50×30 ft | Sand, wet sand near water | Ocean on one side, dunes or cliffs other | Tide pools, driftwood, shipwreck debris, rocks, seaweed | Tan sand, turquoise water, white foam |
| Montaña/paso | 40×25 ft | Rocky terrain, scree | Cliff walls, drop-offs | Narrow path, loose rocks, cave entrance, rope bridge | Gray stone, snow white, icy blue |
| Desierto | 50×35 ft | Sand dunes, cracked earth | Endless dunes, heat shimmer | Oasis, ruins, bones, cacti, sandstone formations | Golden sand, bleached white, harsh shadows |
| Ruinas al aire libre | 40×30 ft | Cracked stone, overgrown grass | Broken walls, collapsed pillars | Fallen columns, rubble, vines, altar remains, hidden cellar | Gray stone, green overgrowth, faded gold |

### Exteriores urbanos

| Locación | Dimensiones | Terreno | Límites | Props clave | Paleta |
|---|---|---|---|---|---|
| Plaza de mercado | 50×40 ft | Cobblestone | Buildings on all sides, alley entrances | Market stalls, fountain, crates, cart, awnings, well | Warm stone, colorful awnings, wood |
| Callejón | 40×10 ft | Wet cobblestone | Tall buildings on both sides | Crates, barrels, ladder, clotheslines, sewer grate | Dark stone, dim lantern light, shadows |
| Puerto/muelle | 50×30 ft | Wooden dock planks, water | Waterfront, warehouses behind | Moored boats, cargo, cranes, rope coils, fish crates | Weathered wood, dark water, rope tan |
| Puente | 40×15 ft | Stone or wood bridge surface | River below, roads at each end | Railings, toll booth, broken sections, gargoyles | Stone gray, water blue-green, moss |
| Cementerio | 40×30 ft | Grass, dirt paths | Iron fence, church wall | Headstones, mausoleums, dead tree, open graves, fog | Gray, dark green, pale moonlight |
| Muralla/puerta | 50×20 ft | Stone walkway atop wall | Battlements, towers at ends | Arrow slits, murder holes, siege equipment, guard posts | Gray stone, iron, banner colors |

### Especiales

| Locación | Dimensiones | Terreno | Límites | Props clave | Paleta |
|---|---|---|---|---|---|
| Plano feérico | 40×30 ft | Luminous grass, crystal formations | Giant mushrooms, ethereal mist | Fairy rings, floating lights, color-shifting flowers, mirror pools | Vivid purple, electric blue, gold sparkles |
| Plano infernal | 40×30 ft | Cracked obsidian, lava flows | Lava rivers, bone pillars | Chains, iron cages, sulfur vents, demonic runes, fire geysers | Black, deep red, molten orange |
| Plano astral | 40×30 ft | Translucent crystalline surface | Floating debris, void | Floating rock islands, portals, silver cords, distant stars | Deep purple, silver, cosmic blue |
| Barco volador | 40×15 ft | Wooden deck, glowing runes | Ship rails, clouds below | Arcane engine, navigation crystal, rigging, cargo nets | Sky blue, cloud white, arcane purple |
| Interior de criatura | 30×20 ft | Fleshy, organic tissue | Ribbed organic walls, membrane | Digestive pools, bone fragments, parasites, mucus | Pink, dark red, sickly yellow-green |

---

## B. Keywords de terreno y materiales

Listas de palabras que producen buenos resultados en Gemini. Usar para enriquecer la descripción del piso, paredes y props.

### Piedra
`rough-hewn stone`, `polished marble`, `cracked flagstone`, `moss-covered stone blocks`, `granite slabs`, `cobblestone`, `sandstone`, `obsidian`, `limestone tiles`, `carved stone with runes`, `weathered stone`, `river stone`

### Madera
`worn wooden planks`, `dark oak floorboards`, `splintered timber`, `polished hardwood`, `rotting wood`, `bamboo`, `driftwood`, `carved mahogany`, `pine beams`, `wattle and daub`, `weathered deck planks`

### Suelo natural
`packed earth`, `muddy ground`, `sandy terrain`, `gravel path`, `mossy forest floor`, `fallen leaves`, `snow-covered ground`, `cracked dry earth`, `volcanic ash`, `clay`, `peat bog`, `crystal-studded cave floor`

### Agua
`clear shallow stream`, `murky swamp water`, `deep blue lake`, `rushing rapids`, `frozen ice surface`, `tide pool`, `underground river`, `waterfall mist`, `stagnant pond`, `magical glowing water`, `lava flow` (como contraste)

### Vegetación
`dense forest canopy`, `thick underbrush`, `flowering meadow`, `dead twisted trees`, `hanging vines`, `giant mushrooms`, `seaweed`, `moss and lichen`, `thorny brambles`, `bioluminescent plants`, `ancient gnarled roots`, `bamboo grove`

### Metales y artificiales
`rusted iron bars`, `polished brass fixtures`, `tarnished copper pipes`, `gold inlay`, `silver filigree`, `wrought iron chandelier`, `steel grating`, `bronze statue`, `crystal formations`, `glowing arcane runes`

### Telas y orgánicos
`tattered tapestry`, `silk curtains`, `leather hides`, `woven carpet`, `animal pelts`, `cobwebs`, `bone pile`, `dried herbs hanging`, `straw bedding`, `parchment scrolls`

---

## C. Recetas de iluminación

Mapeo hora del día → descripción de luz + paleta de colores para el prompt.

| Hora | Descripción en inglés para prompt | Paleta dominante |
|---|---|---|
| Dawn | Soft pink and gold light from the east, long purple shadows stretching westward, dewy mist catching the light | Pink, gold, lavender, soft blue |
| Morning | Clear warm sunlight from low angle, crisp shadows, fresh bright colors | Warm yellow, light blue, bright green |
| Midday | Bright overhead sunlight, short sharp shadows directly below objects, vivid saturated colors | Bright and saturated, minimal shadow |
| Afternoon | Rich golden light from the west, warm long shadows, amber tones on surfaces | Golden amber, warm brown, honey |
| Dusk | Deep orange and purple sky, dramatic long shadows, silhouettes against the horizon | Deep orange, purple, dark blue |
| Night | Pale moonlight with deep blue shadows, pools of warm torchlight or candlelight, stars visible | Deep blue, silver moonlight, warm orange pools |
| Midnight | Near-total darkness, faint starlight, isolated light sources create dramatic contrast | Near-black, faint blue, sharp warm highlights |

### Fuentes de luz interior (agregar según contexto)

| Fuente | Descripción |
|---|---|
| Antorchas | `flickering warm torchlight casting dancing shadows on the walls` |
| Chimenea | `warm fireplace glow illuminating the room with orange-red light and deep shadows` |
| Velas | `soft candlelight with gentle warm glow and intimate atmosphere` |
| Mágica | `ethereal arcane glow in [color], pulsing softly, casting no natural shadows` |
| Lava | `harsh red-orange underglow from lava, dramatic upward shadows` |
| Bioluminiscente | `faint blue-green bioluminescent glow from mushrooms/crystals/water` |
| Luz divina | `radiant golden light streaming from above, dust motes visible in the beams` |
| Sin luz | `complete darkness except for [specific light source], extreme contrast` |

---

## D. Descriptores de estilo expandidos

Mapeo completo de cada estilo con su prompt en inglés y notas de uso.

### D&D Clásico (default)
```
Painted fantasy illustration in the style of official D&D module battle maps, rich warm colors, detailed textures, painterly quality similar to Mike Schley or Jared Blando cartography. Clean readable map with clear terrain distinction.
```
**Mejor para:** La mayoría de escenas. Versatil, legible, familiar para jugadores de D&D.

### Pergamino
```
Fantasy cartography on aged parchment, ink outlines with subtle watercolor fills, compass rose, classic RPG world map aesthetic. Sepia tones with muted color accents, hand-drawn quality with visible pen strokes.
```
**Mejor para:** Mapas de exteriores grandes (Region/City scale), mapas de mundo, documentos in-game.

### Realista
```
Photorealistic top-down render with accurate materials, natural lighting, and high-fidelity textures. Architectural floor plan quality with realistic proportions and material detail.
```
**Mejor para:** Escenas modernas, sci-fi, o cuando se busca inmersión visual máxima.

### 3D
```
3D rendered digital art with volumetric lighting, ambient occlusion, and clean geometric surfaces. Isometric-inspired depth with clear elevation differences and sharp material definition.
```
**Mejor para:** Mazmorras con desniveles, escenas con mucha verticalidad, ambientes sci-fi o steampunk.

### Inkwash
```
Black ink and watercolor wash illustration, minimalist with expressive brushstrokes, muted earth tones with selective color accents. Asian ink painting aesthetic with atmospheric depth.
```
**Mejor para:** Escenas atmosféricas, horror, misterio, ambientes orientales, momentos dramáticos.

---

## Tips de prompt engineering para Gemini

1. **Ser específico con materiales** — "worn oak planks with ale stains" > "wooden floor"
2. **Nombrar la perspectiva siempre** — "top-down orthographic view" es obligatorio
3. **Limitar props a 5-7** — Demasiados detalles confunden al modelo
4. **Colores > adjetivos abstractos** — "deep crimson curtains" > "fancy curtains"
5. **Evitar negaciones** — En vez de "no characters", usar "empty map with no figures"... pero incluir "No characters or tokens" como restricción final igual funciona
6. **Grid explícito** — "visible grid of exactly 27 columns by 15 rows of equal squares" da mejores resultados que "add a grid"
7. **Iluminación específica** — Siempre incluir fuente + dirección + color de luz
8. **Calidad al final** — Cerrar con "High detail, clean edges, suitable for printing" mejora consistencia
