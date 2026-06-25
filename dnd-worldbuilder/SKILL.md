---
name: dnd-worldbuilder
description: >
  Genera y mejora entidades narrativas para campañas D&D: NPCs, establecimientos, ciudades,
  lugares, quests, combates/encuentros e items. Aplica principios de narración profesional
  (sentidos, humor cultural, detalle ancla, ganchos de interacción) y el framework Encounter
  Axis para combates, transformando contenido genérico en experiencias memorables.

  Usa esta skill siempre que el usuario quiera crear, mejorar, enriquecer o reescribir
  cualquier entidad del mundo D&D — incluso si no dice "worldbuilding" explícitamente.
  Frases como "mejora este NPC", "hazlo más interesante", "dale más vida a esta taberna",
  "enriquece las locaciones", "mejora la descripción", "esto está muy genérico",
  "aplica los principios narrativos", o cualquier referencia a mejorar calidad narrativa
  de elementos del mundo, deben activar esta skill. También se activa en modo batch:
  "mejora todos los NPCs de [ciudad]", "enriquece los establecimientos".

  Triggers específicos de **combate**: "diseña un combate", "encuentro para la sesión",
  "pelea contra X", "prepara un encuentro", "haz un combate más interesante",
  "combate con más opciones", "aplica el framework de axis".

  Si el session planner generó un plan y el usuario quiere profundizar en los elementos
  individuales, esta es la skill correcta.
compatibility:
  tools: [Supabase MCP]
---

# D&D Worldbuilder

Skill para generar y mejorar entidades narrativas de campañas D&D con calidad de narrador
profesional. Los datos viven en Supabase (PostgreSQL). Todas las consultas usan `execute_sql`.

---

## Paso 0: Cargar contexto

1. Lee `references/principles.md` — los principios narrativos que guían toda generación.
2. Identifica el **tipo de entidad** que el usuario quiere crear/mejorar.
3. Lee la referencia correspondiente:
   - NPC → `references/npc.md`
   - Establecimiento → `references/establishment.md`
   - Ciudad → `references/city.md`
   - Lugar → `references/location.md`
   - Quest → `references/quest.md`
   - **Combate / Encuentro** → `references/combate.md` (incluye framework Encounter Axis + tabla XP XDMG 2024)
   - Item → `references/item.md`

---

## Paso 0.5: Consultar el compendio (la musa) — PRIMERO

**Antes de inventar nada, busca inspiración en el compendio de flavor.** Si hay un grafo de la
skill `dnd-compendium` disponible (en este proyecto vive en `questkeep/compendium/graphify-out/`),
es la **primera fuente de inspiración** — inventar desde cero es el último recurso.

1. Identifica el tema/arquetipo de lo que vas a crear (p. ej. "villano trágico atado a un lugar",
   "facción de intriga", "bosque con algo antiguo y hambriento").
2. Consúltalo por la **vía sancionada del CLI**: `graphify query "<tema>"`,
   `graphify explain "<nodo>"`, `graphify path "A" "B"` (o lee `GRAPH_REPORT.md` para comunidades,
   **hyperedges/arquetipos** y "surprising connections").
3. Toma **un** arquetipo + sus `theme`/`motif` como **semilla de flavor**, **limando los nombres
   propios Y los tags de dominio que no encajen**: el grafo es multi-libro (~3.072 nodos, NO solo
   Ravenloft), así que un nodo puede arrastrar el setting de su libro (p. ej. el tag "Dominion of
   Shatrekvan" de Ravenloft sobre un lugar goliath) → descarta el setting de origen y quédate con
   el arquetipo (nada de "Strahd"/"Barovia"/"Shatrekvan" directo). El compendio es
   museo/inspiración; el mundo de la campaña (Supabase) es la fuente de verdad.

Si no hay compendio disponible, sigue con los principios narrativos. Lo que tomes del compendio es
*grounding* de sabor; el tono final y la coherencia los dan el lore del mundo (Paso 1) + los
principios (`principles.md`).

---

## Paso 1: Consultar Supabase

Proyecto: obtenerlo del contexto de la campaña activa.

### 1a. Datos de la entidad

Si la entidad ya existe, consultar su estado actual. Si es nueva, reunir el input del DM.

### 1b. Contexto relacional

Las entidades no existen aisladas. Consultar entidades relacionadas para tejer conexiones:

- **NPC** → ciudad donde vive, establecimiento que maneja, quests vinculadas, items que posee
- **Establecimiento** → ciudad, dueño (NPC), items disponibles
- **Ciudad** → NPCs residentes, establecimientos, quests activas, líder
- **Lugar** → ciudad/región, quests vinculadas, monstruos cercanos
- **Quest** → NPCs involucrados, lugares, items de recompensa
- **Combate** → party composition (nivel y clases desde `personajes`), ubicación / entorno, quest/tono de la escena, catálogo de `monstruos` disponibles filtrado por CR
- **Item** → portador (NPC o personaje), lugar donde se encuentra, quest vinculada

### 1c. Lore del mundo

Consultar el lore relevante para coherencia narrativa. La cultura, gobierno, bioma y religión
del lugar deben *sentirse* en la descripción sin mencionarse explícitamente.

Tablas de lore (si existen en la campaña):
- Estados/naciones — gobierno, cultura, bioma, conflictos
- Organizaciones — gremios, cultos, hermandades
- Deidades — panteón, dominios, manifestación en vida cotidiana

Si la campaña no tiene lore estructurado, trabajar con lo que haya en la descripción
de la ciudad/región y preguntar al DM lo que falte.

---

## Paso 2: Auditoría narrativa

Evaluar la entidad actual contra los principios de `principles.md`. Presentar una tabla:

| Principio | Estado | Observación |
|-----------|--------|-------------|
| Mostrar, no decir | Falta | Usa adjetivos directos en vez de acciones |
| Sentidos | Parcial | Solo visual, falta olfato y sonido |
| Detalle ancla | Falta | Nada memorable que los jugadores repitan |
| ... | ... | ... |

Si la entidad es **nueva** (no tiene descripción previa), saltar la auditoría y pasar
directo a la propuesta — pero seguir aplicando todos los principios.

---

## Paso 3: Propuesta

Generar la entidad siguiendo el formato de la referencia del tipo correspondiente.

Presentar en **tabla comparativa** (original vs propuesta) cuando hay original.
Si es entidad nueva, presentar la propuesta directamente.

Cada propuesta debe incluir al final una nota breve de las **conexiones sugeridas**
con otras entidades del mundo (NPCs que mencionan este lugar, items que conectan
con quests, etc.).

> **Combate (flujo especializado):** Cuando la entidad es `Combate`, el paso de propuesta
> sigue el proceso de 8 pasos descrito en `references/combate.md` (pedir dificultad,
> calcular budget XP, proponer 2-3 combos de monstruos, 3 opciones de Protein, 4 ejes
> adicionales, narrar el espacio, ofrecer las 3 capas sensoriales). El output se divide
> en 2 piezas: una escena tipo `combate` con campo `ejes` JSONB + N entradas de monstruos.

---

## Paso 4: Feedback loop

Preguntar al DM: "¿Qué ajustas?" — iterar hasta aprobación.

Si el DM aprueba, confirmar exactamente qué se va a escribir en la BD antes de ejecutar.

---

## Paso 5: Escribir a Supabase

Ejecutar el UPDATE o INSERT según corresponda. Los campos específicos por entidad están
documentados en cada referencia.

Confirmar la escritura al DM con un resumen de lo que se guardó.

---

## Modo batch

Cuando el usuario pide mejorar múltiples entidades ("todos los NPCs de Sleh"):

1. Consultar todas las entidades del tipo solicitado en la ubicación indicada
2. Presentar la lista con estado actual (1 línea por entidad)
3. Preguntar: "¿Las proceso todas o quieres seleccionar?"
4. Procesar una por una, con pausa para feedback entre cada una
5. Usar el contexto de las anteriores para mantener coherencia (que se referencien entre sí)

---

## Integración con session planner

Cuando el session planner genera un plan con elementos genéricos, esta skill puede
profundizar cada elemento individualmente. El flujo es:

1. Session planner genera el plan (escenas, secretos, estructura)
2. El DM pide enriquecer elementos específicos
3. Esta skill toma cada elemento y le aplica el tratamiento completo

No se duplica trabajo — el session planner da la estructura, esta skill da la profundidad.

---

## Reglas generales

- **Nunca escribir a la BD sin confirmación explícita del DM**
- **El compendio es la primera fuente de inspiración (la musa):** consúltalo en el Paso 0.5 antes
  de inventar; inventar desde cero es el último recurso. Lima los nombres propios de la fuente.
- El lore es fundamento, no decoración: si el lore dice X, la descripción lo hace sentir sin decirlo
- Humor coherente con la cultura, nunca random
- Cada entidad necesita al menos un detalle ancla memorable
- Los NPCs están *haciendo algo*, no posando para un retrato
- Mínimo 3 sentidos por descripción de lugar (y abrir con uno inesperado)
- Las conexiones entre entidades hacen que el mundo se sienta vivo
