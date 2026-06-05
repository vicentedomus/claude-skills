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
📐 Grid: 27×15 (TV 32") | [aspecto] | [resolución]
✏️ Sketch: [sí/no]
💰 Costo: ~$0.04
¿Generar? (o ajusta lo que quieras)
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

### Etapa 4: Ensamblar con template

Fórmula de slots:
```
[PERSPECTIVA] [FORMATO] [ESTILO]. [ESCENA + DIMENSIONES]. [PISO]. [PAREDES/LÍMITES]. [ILUMINACIÓN]. [PROPS]. [ATMÓSFERA]. [RESTRICCIONES]. [CALIDAD].
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
→ Grid 27×15, sin tokens
```

---

## Paso 3 — Generación

Llamar al MCP con estos parámetros:

```
mcp__gemini-image__generate_image:
  prompt: [prompt optimizado en inglés]
  filename: "battlemap-[descriptor-corto]"
  subfolder: "battlemaps"
  aspectRatio: [según parámetros, default "16:9"]
  resolution: [según parámetros, default "1K"]
  model: [según parámetros, default "gemini-2.5-flash-image"]
  images: [ruta del sketch si existe]
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
