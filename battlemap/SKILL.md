---
name: battlemap
description: "Genera mapas de combate (battlemaps) para D&D y TTRPGs usando Gemini Image. Activa cuando el usuario diga: battlemap, mapa de combate, genera un mapa, mapa para la sesión, mapa de la taberna, mapa del bosque, mapa de la mazmorra, hazme un battlemap, necesito un mapa de combate, mapa para el encuentro, o mencione un lugar de QuestKeep y pida un mapa."
---

# Battlemap — Generador de Mapas de Combate D&D

Genera battlemaps top-down para proyectar en TV 32" con miniaturas, usando Gemini Image MCP. Flujo: captura → sketch opcional → prompt engineering → generación → edición iterativa.

Anunciar al iniciar: **"Activando battlemap — generador de mapas de combate."**

Responder siempre en **español**.

---

## Paso 1 — Captura de escena

El usuario describe lo que necesita en español, de forma libre. Claude **infiere todos los parámetros** sin preguntar uno por uno.

### Defaults

| Parámetro | Default |
|---|---|
| Estilo | D&D Clásico |
| Ambientación | Medieval |
| Hora | Midday |
| Escala | Inferir de la escena |
| Aspecto | 16:9 |
| Resolución | 1K |
| Modelo | gemini-2.5-flash-image |

### Tabla de opciones

| Parámetro | Opciones |
|---|---|
| Estilo | D&D Clásico, Pergamino, Realista, 3D, Inkwash |
| Ambientación | Medieval, Steampunk, Sci-Fi, Modern, Noir, Post-Apocalyptic, Cyberpunk |
| Hora | Dawn, Morning, Midday, Afternoon, Dusk, Night, Midnight |
| Escala | Room, Building, District, City, Region |
| Aspecto | 1:1, 16:9, 9:16, 3:2, 4:3, 3:4 |
| Resolución | 1K, 2K, 4K |
| Modelo | gemini-2.5-flash-image, gemini-3-pro-image-preview, gemini-3.1-flash-image-preview |

### Integración QuestKeep

Si el usuario menciona un lugar por nombre (ej. "Bodegas del Canal Bajo", "La Forja del Martillo"), buscar en Supabase antes de armar el prompt.

**Proyecto Supabase:** `dwmzchtqjcblupmmklcl`

**Query unificada:**
```sql
SELECT nombre, tipo, descripcion_interior, descripcion_exterior, 'establecimiento' as fuente
FROM establecimientos WHERE nombre ILIKE '%{término}%' AND campaign_slug = 'halo'
UNION ALL
SELECT nombre, tipo, descripcion_interior, descripcion_exterior, 'lugar' as fuente
FROM lugares WHERE nombre ILIKE '%{término}%' AND campaign_slug = 'halo'
```

Usar `descripcion_interior` y/o `descripcion_exterior` como base visual del prompt. Estas descripciones son detalladas y visuales — aprovecharlas al máximo.

Default `campaign_slug`: `'halo'`. Si el usuario especifica otra campaña, ajustar.

### Bloque de confirmación

Presentar siempre antes de generar:

```
📍 Escena: [descripción corta]
🎨 Estilo: [estilo] | [ambientación] | [hora]
🗺️ Semilla: [FUENTE] título · N salas · CxF cuadros   ← omitir la línea si no hay
📐 Grid: 27×15 (TV 32") | [aspecto] | [resolución]
✏️ Sketch: [sí/no]
💰 Costo: ~$0.04
¿Generar? (o «sin semilla», o ajusta lo que quieras)
```

Si el usuario no ha mencionado sketch, agregar al final:
`Tip: puedes hacer un sketch primero para controlar el layout.`

---

## Paso 1b — Sketch de layout (opcional)

El sketch le da al usuario control sobre la composición del mapa. Hay dos opciones:

### Opción A: Sketch Tool (integrado)

El sketch-tool es un HTML autocontenido en `assets/sketch-tool.html` (ruta relativa a esta skill). Cómo acceder según el entorno:

- **Claude Code web (default):** describe el layout en palabras (ej. "río de norte a sur, puente al centro, taberna en la esquina noreste") y Claude lo integra al prompt. Si prefieres dibujarlo a mano, usa la Opción B y sube la imagen.
- **Escritorio (cualquier SO):** abre `assets/sketch-tool.html` en tu navegador (doble clic, o arrástralo a una pestaña). No se usa ningún comando de terminal específico del SO.

El sketch-tool tiene:
- Canvas con grid de 27×15 cuadros
- **Paleta predefinida:**
  - 🟢 Verde = bosque/vegetación
  - 🔵 Azul = agua (río, lago, pozo)
  - 🟤 Marrón = tierra/camino
  - ⚪ Gris = piedra/muros
  - 🟫 Marrón oscuro = madera (piso, muebles)
  - 🔴 Rojo = lava/fuego
  - ⬜ Blanco = nieve/hielo
  - ⬛ Negro = vacío/abismo
- **Paleta personalizada:** el usuario puede asignar color = feature arbitrariamente
- Botón "Guardar PNG" que exporta el sketch

### Opción B: Cualquier app

El usuario puede dibujar en cualquier app de dibujo (o tomar una foto de un boceto en papel) y subir la imagen o dar su ruta.

### Usar el sketch en la generación

Cuando hay sketch:
1. Pasar la ruta del PNG en el parámetro `images[]` del MCP
2. Agregar al prompt la leyenda de colores:

**Si paleta predefinida:**
```
Use this color-coded sketch as structural layout guide. Green areas = forest/vegetation, blue = water, brown = earth/paths, gray = stone/walls, dark brown = wood floors/furniture, red = lava/fire, white = snow/ice, black = void/abyss.
```

**Si paleta personalizada** (el sketch-tool exporta un JSON con la asignación):
```
Use this color-coded sketch as structural layout guide. [color] areas = [feature], ...
```

---

## Paso 1c — Semilla oficial (referencia estructural)

Generar desde cero produce mapas plausibles pero sin planta: el modelo inventa cuántas
salas hay y cómo conectan. Este paso le da una **planta real** de un mapa oficial del
compendio como referencia.

**Cuándo entra sola:** cuando la escena es **arquitectónica** — el `tipo` inferido es
`mazmorra`, `templo`, `guarida`, `fortaleza`, `asentamiento`, `taberna`, `tienda`, `casa`,
`cueva`, `ruinas`, `campamento` o `barco`. Se **salta** en paisajes y exteriores abiertos
(`tipo: region`), donde una planta oficial no aporta nada. El DM puede forzarla («con
semilla oficial», «busca una planta real») o saltarla («sin semilla») siempre.

### 1. Mapear la escena a las facetas

Traducir la escena a las claves cerradas de `compendium/map-taxonomy.json` —
13 `tipo` × 10 `ambiente`. No inventar claves: el buscador rechaza las que no existen.

| Eje | Claves válidas |
|---|---|
| `tipo` | templo, mazmorra, guarida, fortaleza, asentamiento, taberna, tienda, casa, cueva, ruinas, campamento, barco, region |
| `ambiente` | bosque, nieve, desierto, pantano, montana, costa, subterraneo, urbano, infernal, acuatico |

Se pueden pasar varias por eje (OR dentro del eje, AND entre ejes). «Almacén portuario de
un canal» → `--tipo=tienda,casa --ambiente=urbano,costa`.

### 2. Buscar candidatos

```bash
node compendium/query-map-index.mjs --tipo=taberna,casa --ambiente=urbano \
  --salas --cuadros=40x25 --top=5
```

- `--salas` descarta los mapas que no declaran salas: sin salas no hay planta que copiar.
- `--cuadros=40x25` es el **techo de cordura**, y no es 27×15 a propósito. La planta se
  reencaja en la pantalla (ver Paso 2), así que filtrar a los que ya caben en 27×15
  descartaría el 75% de los mapas que declaran grid (702 de 936). El techo de 40×25 solo
  deja fuera los pósters de aventura entera, que no se pueden reencajar sin inventar otro
  mapa.

Mirar las miniaturas de los candidatos y **presentar los 3 mejores** al DM (el `--top=5`
da margen para descartar los que no encajen con la escena). Salida real de ese comando
(recortada a 3 — el script imprime también las URLs de imagen y miniatura de cada uno):

```
Semillas candidatas:
1. [WDH] Cassalanter Villa · 38 salas · 15x18 cuadros
2. [WDH] Gralhund Villa · 22 salas · 13x18 cuadros
3. [TOA] Map 1.2: Merchant Prince's Villa · 19 salas · 36x25 cuadros
```

El DM elige un número, pide otros candidatos, o dice «sin semilla».

**Si la búsqueda no devuelve candidatos:** avisar en una línea y seguir sin semilla.
Nunca insistir con otras facetas más de una vez.

### 3. Bajar la semilla

```bash
curl -fsS -o /tmp/seed.webp \
  "https://raw.githubusercontent.com/5etools-mirror-3/5etools-img/main/<path>"
```

**A un temporal, nunca al repo.** Modo referencia: QuestKeep no hospeda binarios © WotC.
Si la descarga falla (404, red, proxy), avisar y ofrecer el siguiente candidato o seguir
sin semilla.

### 4. Extraer el brief estructural (filtro de lore)

El mapa elegido suele traer texto en `compendium/map-descriptions.json` (campo `.d`, 656
de 1028 lo tienen). Es un objeto keyed por `path` (~580 KB), así que se extrae la entrada
suelta en vez de leer el archivo entero.

> **Los dos comandos de abajo usan rutas relativas: córrelos desde la raíz del repo
> questkeep**, igual que `query-map-index.mjs`. Desde otro directorio fallan con
> `Cannot find module`.

```bash
node -e "console.log(require('./compendium/map-descriptions.json')['<path>']?.d || '(sin descripción)')"
```

De ese texto se conserva **solo lo estructural** y se descarta lo narrativo, para que el
lore de Reinos Olvidados no se cuele en un mapa de Halo.

238 mapas tienen además una **lista de salas** — pero solo en `place-index.json`, que pesa
2.5 MB, así que se extrae la entrada suelta en vez de leer el archivo entero:

```bash
node -e "const p=require('./compendium/place-index.json').find(x=>x.path==='<path>');
console.log((p?.salas||[]).map(s=>s.nombre).join(' | ')||'(sin salas)')"
```

De esa lista sobrevive **de qué tipo son** las salas (cocina, cripta, patio, establo), que
es lo que le dice al modelo qué poner dentro de cada una.

**Se conserva:** arquitectura, materiales, número de niveles, disposición, fuentes de luz,
estado de conservación.

**Se descarta siempre:**

- Topónimos (Secomber, Waterdeep, el Delimbiyr…)
- Nombres propios de personas, familias y facciones
- Deidades y referencias religiosas concretas
- Etiquetas de sala completas (`I1. Idyll Road`): sobrevive **cuántas salas hay y de qué
  tipo son** (cocina, cripta, patio), no cómo se llaman ni su código. `I3. Temple of
  Lathander` → «a shrine», no «Lathander»
- Ganchos de trama y read-aloud: son narrativos, no estructurales

Ejemplo del filtro:

> **Original:** «mausoleo de las familias de Secomber, encajado en un acantilado al sur
> del río, tres cámaras y una escalera descendente; los Everlake dejaron de visitarlo»
>
> **Brief:** «stone mausoleum set into a cliff face, three chambers, descending stairway,
> severe disrepair»

El brief se escribe **en inglés**, porque va directo al prompt.

**Si el mapa no tiene descripción** (372 del catálogo, más de un tercio): semilla
solo-imagen, sin brief. No es un error y no hace falta avisar — pasa a menudo.

### 5. Regla de precedencia

**La ficción es de Halo. La arquitectura, de la semilla. El formato, de la TV.**

Si el texto de Supabase y el brief estructural se contradicen, manda Supabase: la semilla
aporta planta, no historia.

### 6. Límites conocidos (medidos el 2026-08-11, aceptados por el DM)

- **Planta simple = más parecido al original.** Con una semilla de ~70 salas el modelo
  recompone de verdad; con una de ~13 la traza casi tal cual. El arte siempre sale propio,
  pero el plano de una semilla sencilla es reconocible. Si el mapa importa que no lo sea,
  prefiere una semilla con muchas salas.
- **Las semillas de varias plantas se leen como una sola.** Los mapas oficiales dibujan los
  pisos lado a lado y el modelo los fusiona en un edificio contiguo. Si la miniatura enseña
  dos o más bloques separados, avísalo al DM: el resultado tendrá todas las salas al mismo
  nivel.
- **La rejilla 27×15 no siempre aparece**, aunque el prompt la pida. Si el mapa es para la TV
  con miniaturas, compruébala antes de darlo por bueno y, si falta, pídela en una edición.

---

## Paso 2 — Optimización del prompt

**Este es el core de la skill.** Pipeline de 4 etapas:

### Etapa 1: Traducir y expandir

Convertir la descripción casual en español a inglés estructurado con detalles visuales específicos.

Ejemplo:
- Input: "taberna medieval, hubo una pelea"
- Output: "A medieval tavern interior after a bar fight, overturned tables and broken chairs scattered across the wooden floor, spilled ale puddles, a cracked wooden bar counter along one wall"

Si hay datos de QuestKeep, integrar las descripciones de Supabase como base.

### Etapa 2: Detectar conflictos

Verificar coherencia:
- Interior + escala Region → conflicto
- Night + "sol brillante" → conflicto
- Nieve + selva tropical → conflicto

Si hay conflicto, avisar al usuario y sugerir corrección antes de generar.

### Etapa 3: Inyectar requisitos battlemap

Agregar SIEMPRE estos elementos al prompt:
- `"Top-down orthographic view, bird's eye perspective"`
- `"Battle map for tabletop RPG"`
- `"No characters, tokens, or miniatures on the map"`
- `"The map should contain a visible grid of exactly 27 columns by 15 rows of equal squares"` (solo si aspecto 16:9 para TV)
- Paleta de colores según hora del día (ver `references/prompt-engineering.md`)

**Si hay semilla (Paso 1c)**, agregar además este bloque, justo antes de `[RESTRICCIONES]`:

```
The attached image is a STRUCTURAL FLOOR-PLAN REFERENCE ONLY. Follow its room count,
adjacency, corridor topology and overall footprint. Do NOT reproduce its art style,
palette, textures, linework, labels, numbers or any text. Recompose the plan onto a
16:9 canvas of exactly 27 by 15 squares: compact wings, merge corridors, drop
peripheral rooms as needed. Do not stretch or letterbox.
```

Este bloque hace dos trabajos a la vez y **no se recorta**:

1. **Fuerza la reinterpretación.** La semilla es arte © WotC; el output tiene que ser
   propio. Si un mapa generado se parece al original, este bloque no está apretando
   bastante y hay que endurecerlo.
2. **Resuelve el choque de escala.** La planta oficial mediana son 23×23 cuadros y la TV
   son 27×15: la mayoría de las semillas cubren más terreno que una pantalla. Manda la TV,
   y la planta se compacta.

El brief estructural del Paso 1c entra en los slots normales (`[ESCENA + DIMENSIONES]`,
`[PISO]`, `[PAREDES/LÍMITES]`), no aquí.

### Etapa 4: Ensamblar con template

Fórmula de slots:
```
[PERSPECTIVA] [FORMATO] [ESTILO]. [ESCENA + DIMENSIONES]. [PISO]. [PAREDES/LÍMITES]. [ILUMINACIÓN]. [PROPS]. [ATMÓSFERA]. [SEMILLA]. [RESTRICCIONES]. [CALIDAD].
```

**Ejemplo ensamblado:**
```
Top-down orthographic view, bird's eye perspective. Battle map for tabletop RPG. Painted fantasy illustration in the style of official D&D module battle maps, rich warm colors, detailed textures. A medieval tavern interior after a bar fight, approximately 30 by 20 feet. Worn wooden plank floor with ale stains. Stone walls with timber frame, wooden bar counter along the east wall. Warm candlelight from iron chandeliers, fireplace glow from the north wall, soft shadows. Overturned tables and broken chairs, spilled ale puddles, a cracked mirror behind the bar, barrel stack in the corner. Smoky, tense atmosphere. No characters or tokens. The map should contain a visible grid of exactly 27 columns by 15 rows of equal squares. High detail, clean edges, suitable for printing.
```

### Mostrar resumen al usuario

Antes de generar, mostrar un resumen EN ESPAÑOL del prompt optimizado. Esto es por transparencia y para que el usuario aprenda cómo funciona el prompt engineering.

```
Prompt optimizado:
→ Perspectiva top-down, estilo D&D Clásico
→ Taberna medieval post-pelea, ~30×20 ft
→ Piso de madera desgastada, muros de piedra con marco de madera
→ Luz de velas y chimenea, sombras suaves
→ Props: mesas volcadas, sillas rotas, charcos de cerveza, espejo roto, barriles
→ Semilla: planta de [WDH] Cassalanter Villa (38 salas), reencajada a 27×15
→ Grid 27×15, sin tokens
```

---

## Paso 3 — Generación

> **Si la tool `mcp__gemini-image__*` NO está disponible** (p. ej. en sesiones remotas de Claude
> Code web, donde el entorno solo carga conectores remotos y no servers MCP locales stdio), salta
> al **Fallback sin MCP** más abajo: genera por el API directo con el mismo modelo y resultado.

Llamar al MCP con estos parámetros:

```
mcp__gemini-image__generate_image:
  prompt: [prompt optimizado en inglés]
  filename: "battlemap-[descriptor-corto]"
  subfolder: "battlemaps"
  aspectRatio: [según parámetros, default "16:9"]
  resolution: [según parámetros, default "1K"]
  model: [según parámetros, default "gemini-2.5-flash-image"]
  images: [ruta del sketch y/o de la semilla del Paso 1c, si existen]
```

**Notas:**
- `outputDir` se omite para usar el default del MCP. En Claude Code web los archivos viven en el sandbox (efímero) — descarga los mapas que quieras conservar.
- `filename` debe ser descriptivo: `battlemap-taberna-medieval`, `battlemap-bosque-nocturno`, `battlemap-mazmorra-trampa`

Después de generar:
1. Reportar la ruta del archivo generado (viene en la respuesta del MCP). En Claude Code web la imagen se visualiza directamente; en escritorio, indicar la ruta para que el usuario la abra. No usar comandos del SO para abrirla.
2. **Guardar el `sessionId`** de la respuesta — se necesita para ediciones
3. Informar el costo real (viene en la respuesta del MCP)
4. Ofrecer opciones:

```
Mapa generado: [ruta]
Costo: $[costo]

¿Qué quieres hacer?
• Editar — describe qué cambiar (ej. "más mesas", "agrega un río")
• Nuevo — generar un mapa diferente
• Procesar — crop, resize, o cambiar formato
• Listo — guardar y terminar
```

**Si Gemini rechaza la generación por safety con la semilla adjunta:** reportarlo y
reintentar **sin semilla**, con el mismo prompt menos el bloque `[SEMILLA]`. La semilla es
un plus, nunca un requisito: ningún fallo de búsqueda, descarga o safety puede dejar al DM
sin mapa.

---

## Paso 3b — Fallback sin MCP (API directo de Gemini)

Cuando la tool `mcp__gemini-image__*` no está presente (sesiones remotas de Claude Code web no
levantan servers MCP locales stdio; solo consumen **conectores remotos** a nivel de cuenta), usa
el script **`scripts/gen-image.sh`**, que llama al **API de Gemini directo** con la `GEMINI_API_KEY`
del entorno — mismo modelo y resultado que el MCP, **cero infraestructura**.

```bash
# Generación (escribe el prompt optimizado a un archivo primero — evita problemas de escaping)
scripts/gen-image.sh --prompt-file prompt.txt --out battlemaps/battlemap-X.png --aspect 16:9

# Edición iterativa (Paso 4) — pasa la imagen base con --edit
scripts/gen-image.sh --prompt "Edit this battle map: <cambio>. Keep everything else the same." \
  --edit battlemaps/battlemap-X.png --out battlemaps/battlemap-X-v2.png --aspect 16:9
```

Con semilla del Paso 1c, se adjunta con `--ref` (sinónimo de `--edit`, mismo camino de
código — la imagen viaja en `inlineData` con su mimeType detectado, así que un `.webp`
pasa sin convertir):

```bash
scripts/gen-image.sh --prompt-file prompt.txt --out battlemaps/battlemap-X.png \
  --aspect 16:9 --ref /tmp/seed.webp
```

**Límite del fallback: una sola imagen adjunta.** `--edit` y `--ref` escriben la misma
variable en el script, así que si hay sketch (Paso 1b) **y** semilla (Paso 1c) a la vez,
gana el que se pase último en la línea de comandos — el otro se ignora en silencio. El MCP
(`images[]`, Paso 3) sí admite las dos. Si ambas existen y hay que usar el fallback, **manda
la semilla** (`--ref`): aporta planta real, el sketch es solo un boceto de layout.

El script construye el body con `jq` (escapado seguro), respeta el CA bundle del proxy si existe,
decodifica el PNG de `inlineData`, y reporta errores de la API (HTTP, safety, cuota). El resto del
flujo es idéntico — **solo cambia el motor de render**: el prompt-engineering del Paso 2, la
edición del Paso 4 (vía `--edit`) y los specs de TV (16:9, grid 27×15) aplican igual. El
`aspectRatio` va en `generationConfig.imageConfig` y funciona con `gemini-2.5-flash-image`.

> **Por qué existe este fallback:** en Claude Code web el entorno cablea MCP como conectores
> remotos (HTTP); un server local stdio como `gemini-image` (npx) no se puede agregar ahí. Para
> tenerlo como MCP nativo en web habría que hostearlo detrás de una URL (bridge tipo
> `supergateway`) y agregarlo como conector remoto — pesado. Este script evita todo eso.

---

## Paso 4 — Edición iterativa

Para ediciones del mapa existente:

1. Usar el `sessionId` guardado del paso anterior
2. Pasar la imagen actual en `images[]`
3. Template de edición:
   ```
   Edit this battle map: [cambio solicitado]. Keep everything else exactly the same. Maintain the same art style, lighting, and top-down perspective.
   ```
4. Versionado automático del filename: el MCP agrega `-v2`, `-v3`, etc. automáticamente si se usa el mismo `filename`
5. Reportar la ruta de la nueva versión (sin comandos del SO)
6. Actualizar el `sessionId` con la nueva respuesta
7. Volver a ofrecer opciones

**Regla:** si el usuario pide algo radicalmente diferente (nueva escena, nuevo estilo completo), sugerir empezar una sesión nueva en vez de editar.

---

## Paso 5 — Post-procesamiento (opcional)

Si el usuario necesita ajustes técnicos, usar `mcp__gemini-image__process_image`:

| Operación | Cuándo |
|---|---|
| Crop | Recortar bordes o ajustar encuadre |
| Resize | Ajustar a resolución específica (ej. 1280×720 exacto para TV) |
| Format | Convertir a PNG/JPEG/WebP según necesidad |
| Trim | Quitar bordes blancos sobrantes |

---

## Specs de proyección (TV 32" 720p)

Por defecto, todos los battlemaps se optimizan para proyectar en TV con miniaturas:

| Spec | Valor |
|---|---|
| TV | 32", 16:9, 720p (1280×720) |
| PPI | ~45.9 |
| Grid | 27 × 15 cuadros (1 cuadro = 1 pulgada física = 5 ft in-game) |
| Área jugable | 135 ft × 75 ft in-game |
| Resolución imagen | 1280 × 720 px |
| Px por cuadro | ~46 px |

**Si el usuario dice que el mapa es para otra cosa** (VTT online, impresión, Roll20, etc.), NO aplicar estos defaults de grid y resolución. Preguntar qué specs necesita.

---

## Referencia rápida de estilos

| Estilo | Prompt en inglés |
|---|---|
| D&D Clásico | Painted fantasy illustration in the style of official D&D module battle maps, rich warm colors, detailed textures, painterly quality similar to Mike Schley or Jared Blando cartography |
| Pergamino | Fantasy cartography on aged parchment, ink outlines with subtle watercolor fills, compass rose, classic RPG world map aesthetic |
| Realista | Photorealistic top-down render with accurate materials, natural lighting, and high-fidelity textures |
| 3D | 3D rendered digital art with volumetric lighting, ambient occlusion, and clean geometric surfaces |
| Inkwash | Black ink and watercolor wash illustration, minimalist with expressive brushstrokes, muted earth tones with selective color accents |

Para catálogos completos de locaciones, materiales e iluminación, consultar `references/prompt-engineering.md`.
