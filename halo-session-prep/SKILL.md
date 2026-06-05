---
name: halo-session-prep
description: >
  Preparación de sesiones para la campaña D&D "Halo", con datos en Supabase.

  Usa esta skill siempre que Vicente mencione cualquier cosa relacionada con la campaña
  Halo, D&D, sesiones, quests, NPCs, ciudades, items, o preparación de partidas — incluso
  si no dice "session prep" explícitamente. Si el mensaje menciona preparar una sesión,
  generar notas de DM, planear un encuentro, preguntar qué hacer la siguiente sesión,
  o cualquier referencia a quests activas, NPCs específicos, o ciudades del mundo de Halo,
  activa esta skill. En caso de duda sobre si activarla o no, actívala — es mejor tenerla
  disponible y no necesitarla.

  Frases de activación típicas: "prepara la sesión", "session prep", "genera el prep",
  "qué hacemos la próxima sesión", "notas de DM".
compatibility:
  tools: [Supabase MCP, Agent]
---

# Halo — Session Prep Skill

Skill de preparación de sesiones para la campaña **Halo**. Los datos viven en Supabase (PostgreSQL).
Todas las consultas y escrituras se hacen con `execute_sql` sobre el proyecto `dwmzchtqjcblupmmklcl`
y con `campaign_slug = 'halo'` donde aplique.

**Principio central:** cada sesión se **ancla al mundo existente** (reusa NPCs, items y monstruos
de la BD) y al mismo tiempo **expande el mundo** (2 NPCs nuevos cada sesión). Los tesoros salen
siempre de la tabla `items` y los monstruos de la tabla `monstruos` — nunca se inventan.

---

## Paso 0: Leer learnings (SIEMPRE)

Antes de cualquier otra acción, lee `references/learnings.md`.

Ese archivo contiene preferencias del DM acumuladas de sesiones pasadas. Aplicarlas desde el
inicio evita que el DM tenga que corregir cosas ya aprendidas.

---

## Paso 1a — Recibir contexto del DM

El DM da el contexto libre para planear la sesión. Puede incluir:
- Qué notas o sesiones anteriores revisar (ej: "toma las notas del 11 de marzo")
- Qué quests tomar como base (ej: "la quest del componente robado")
- Dirección narrativa deseada (ej: "me gustaría que lleguen a Gnomalia en barco")
- Contexto narrado para one-shots o sesiones no relacionadas

No siempre hay notas previas que revisar — a veces el DM da contexto completamente nuevo.

### Paso 1b — Consultar Supabase (priorizando contexto del DM)

El contexto del DM define QUÉ buscar — Supabase completa con los detalles.

**Queries base:**

```sql
-- Sesión específica mencionada por el DM
SELECT id, nombre, fecha, resumen, contenido_html
FROM notas_dm
WHERE campaign_slug = 'halo' AND nombre ILIKE '%nombre_sesion%' AND NOT archived;

-- Quest mencionada
SELECT q.id, q.nombre, q.estado, q.resumen, q.contenido_html
FROM quests q
WHERE q.campaign_slug = 'halo' AND q.nombre ILIKE '%nombre_quest%' AND NOT q.archived;

-- NPCs vinculados a la quest
SELECT n.id, n.nombre, n.raza, n.rol, n.estado, n.primera_impresion, n.notas_roleplay, n.edad, c.nombre as ciudad
FROM npcs n
JOIN npcs_quests nq ON n.id = nq.npc_id
LEFT JOIN ciudades c ON n.ciudad_id = c.id
WHERE nq.quest_id = 'uuid_quest' AND NOT n.archived AND n.campaign_slug = 'halo';

-- Ciudades mencionadas
SELECT c.id, c.nombre, c.descripcion, c.lider, c.poblacion, c.estado
FROM ciudades c
WHERE c.campaign_slug = 'halo' AND c.nombre ILIKE '%nombre_ciudad%' AND NOT c.archived;

-- Establecimientos de esas ciudades
SELECT e.id, e.nombre, e.tipo, e.descripcion_exterior, e.descripcion_interior, d.nombre as dueno
FROM establecimientos e
LEFT JOIN npcs d ON e.dueno_id = d.id
WHERE e.ciudad_id = 'uuid_ciudad' AND NOT e.archived;

-- NPCs de esas ciudades (para completar los 4 existentes)
SELECT n.id, n.nombre, n.raza, n.rol, n.estado, n.primera_impresion, n.notas_roleplay, n.edad
FROM npcs n
WHERE n.ciudad_id = 'uuid_ciudad' AND NOT n.archived AND n.campaign_slug = 'halo';
```

**Queries nuevas obligatorias (catálogos de referencia):**

```sql
-- Items candidatos para tesoros (filtrar por rareza/tipo según tono de la sesión)
SELECT id, nombre, tipo, rareza, descripcion, requiere_sintonizacion
FROM items
WHERE campaign_slug = 'halo' AND NOT archived
  AND personaje_id IS NULL AND npc_portador_id IS NULL;

-- Monstruos candidatos para combate (ajustar filtro por CR y entorno de la escena)
SELECT id, nombre, tipo, tamano, cr, entorno, hp, ac, rasgos, acciones
FROM monstruos
WHERE NOT archived
  AND cr::text = ANY(ARRAY['1/4','1/2','1','2','3'])  -- ajustar rango según nivel del party
ORDER BY nombre;
```

Nota: `monstruos` no tiene `campaign_slug` — es un catálogo compartido.

Si no encuentras algo mencionado por el DM, anótalo como `[no encontrado]` y pregunta después.

### Paso 2 — Preguntas de afinación

Con el contexto de Supabase en mano, haz **solo las preguntas necesarias** — no preguntes lo
que ya encontraste. Agrúpalas en un solo mensaje:

1. ¿Cuándo es la próxima sesión? *(para el nombre y fecha de la nota)*
2. ¿Cuál es el objetivo de los jugadores para esa sesión?
3. ¿Cuántas horas tiene la sesión? *(calibrar contenido)*
4. ¿Hay combate planeado? ¿Con quién? *(acota la búsqueda de monstruos)*
5. ¿Hay revelación o giro importante que quieras que ocurra?
6. ¿Hay algún NPC nuevo que quieras forzar, o dejamos que la skill proponga los 2 nuevos?

Omite las preguntas cuya respuesta ya esté clara en la BD.

### Paso 3 — Generar propuesta (iterativo con el DM)

Genera un borrador siguiendo la plantilla de `references/session-structure.md`. Los principios guía:

- **Prep = ingredientes, no script**: el DM improvisa sobre esto
- **Strong Start**: la apertura lanza la acción de inmediato, sin preámbulo
- **Escenas posibles**: 3-5 escenas con objetivo + obstáculo cada una
- **Secrets & Clues**: múltiples caminos a la misma información
- **Mundo se sigue expandiendo**: 2 NPCs nuevos por sesión, bien integrados

**Reglas duras por sección** (se auditan en el Paso 6):

#### NPCs — **mínimo 6, composición 4 existentes + 2 nuevos**

- **4 existentes**: selecciona los más relevantes a la quest, ciudad o lugar objetivo de la sesión.
- **2 nuevos**: genera frescos invocando el flujo de `dnd-worldbuilder` con `references/npc.md`
  (primera_impresion + notas_roleplay, con las capas sensoriales y manierismos de ese formato).
- Cada NPC (existente o nuevo) lleva el campo **"Relación con la sesión"**: qué rol narrativo cumple,
  por qué aparece, cómo se cruza con los objetivos. No vale dejarlo vacío.
- Marca cada NPC con flag `existente` o `nuevo`. Este flag se preserva como snapshot histórico
  de esa sesión.
- La transición `nuevo → existente` en la BD ocurre en el Paso 4 (ver abajo).

#### Locaciones — **cada una explica su relación con la sesión**

- Cada locación lleva campo "Relación con la sesión": qué escena ocurre ahí, qué rol cumple
  (combate, social, revelación, exploración). No vale dejarlo vacío.

#### Tesoros — **SOLO items reales de la tabla `items`**. Regla de prioridad estricta:

1. **Primero** busca un item existente que satisfaga la necesidad narrativa tal cual.
   Si encaja (efecto y tono), úsalo sin tocar nada.
2. **Solo si ningún item existente encaja**, aplica **reskin narrativo** invocando `dnd-worldbuilder`
   con `references/item.md`. El reskin cambia flavor (nombre, descripción) pero **mantiene el item
   base como referencia** (mismas stats y efectos).
3. **Nunca inventar** items que no existan en la BD.

Cada tesoro lleva: `item_id` base, flag `match_directo | reskin`, y si es reskin el flavor aplicado.

#### Combate / Encuentro — invocar `dnd-worldbuilder` con `references/combate.md`

Los combates se diseñan como **encuentros multi-dimensionales** (framework Encounter Axis),
no como listas de monstruos. Delegar a `dnd-worldbuilder` con `references/combate.md` pasando:

- Party composition (nivel y clases de `personajes`)
- Ubicación del combate y quest/tono
- Catálogo `monstruos` consultado en Paso 1b (filtrado por CR y `entorno`)

La skill hermana retorna:

1. **1 entrada de `bloque_escenas`** con `tipo: "combate"`, `objetivo`, `obstaculo`, `espacio`
   y el nuevo campo **`ejes`** JSONB (`protein` + `optimizers[]` + `hazards[]` + `chaos[]`).
   Cumple la **Regla de Tres**: 1 Protein + ≥2 ejes adicionales.
2. **N entradas de `bloque_monstruos`**, una por tipo de monstruo del encuentro (con
   `cantidad`, `contexto_narrativo`, y si hay reskin, las 3 capas sensoriales en
   `reskin_primera_senal` / `reskin_encuentro` / `reskin_comportamiento`).

**Reglas estrictas para monstruos:**

1. **Primero** busca un monstruo del catálogo oficial que encaje. Si encaja, úsalo sin reskin.
2. **Solo si nada encaja**, `combate.md` aplica reskin narrativo (cambia flavor, **nunca el
   stat block**).
3. **Nunca inventar** stat blocks.

Cada monstruo lleva: `monstruo_id` base, flag `match_directo | reskin`, cantidad, contexto
narrativo, y si es reskin las 3 capas completas.

**Dificultad:** calibrada con la tabla XP XDMG 2024 (Low / Moderate / High, sin multiplicador
por cantidad). Ver detalle en `../dnd-worldbuilder/references/combate.md`.

**Otras validaciones antes de presentar el borrador:**

- **Items de personajes:** nunca asumir que un PJ posee un item si no está en la tabla `items`
  con `personaje_id` apuntándolo. "Quiero que X obtenga Y" es quest futura, no hecho actual.
- **Secretos:** crosscheck contra resúmenes de sesiones consultadas en Paso 1b. Si los jugadores
  ya lo saben, no es secreto — busca algo nuevo.

**Presentar el borrador al DM y preguntar:** "¿Quieres algún cambio?"
- Si pide cambios → ajustar y volver a presentar.
- Si aprueba → pasar al Paso 4.

---

## Paso 4 — Commit a Supabase (incluye transición `nuevo → existente`)

### 4a. Commit de NPCs nuevos a la tabla `npcs`

Antes de insertar el `session_plan`, pregunta al DM:

> "¿Confirmas guardar los 2 NPCs nuevos ([nombre X], [nombre Y]) en la tabla `npcs`?"

Si el DM aprueba:

```sql
INSERT INTO npcs (nombre, raza, tipo_npc, rol, ciudad_id, primera_impresion, notas_roleplay,
                  edad, conocido_jugadores, campaign_slug)
VALUES ('Nombre', 'Raza', 'tipo', 'Rol', 'uuid_ciudad_o_NULL', 'primera_impresion...',
        'notas_roleplay...', 42, false, 'halo')
RETURNING id;
```

Captura el `id` devuelto por cada INSERT. Usa esos `npc_id` reales en el bloque `bloque_npcs`
del session_plan.

Si el DM rechaza el commit, los NPCs se quedan solo en el bloque del session_plan (sin `npc_id`),
pero no como entidad reutilizable.

**Regla:** todo NPC marcado `nuevo` en un session_plan commiteado debe tener `npc_id` apuntando
a una fila real en `npcs`. El Paso 6 lo audita.

### 4b. Insertar el session_plan

El schema real de `session_plans` tiene **columnas separadas por bloque** (todas jsonb excepto
`bloque_strong_start` que es text). Hacer un solo INSERT que llene todos los bloques:

```sql
INSERT INTO session_plans (
  nombre, fecha_sesion, estado, campaign_slug,
  bloque_strong_start,
  bloque_escenas,
  bloque_secretos,
  bloque_npcs,
  bloque_locaciones,
  bloque_tesoros,
  bloque_monstruos,
  input_data
) VALUES (
  'Sesión DD-MMM-YY',
  'YYYY-MM-DD',
  'borrador',
  'halo',
  'texto del strong start',
  '[{"titulo":"...","descripcion":"...","tipo":"combate|social|exploración|misterio|revelación","tension":1,"objetivo":"...","obstaculo":"...","espacio":"... (solo combate)","ejes":{"protein":{"tipo":"...","descripcion":"...","condicion_cierre":"...","retreat_number":null},"optimizers":[{"tipo":"...","descripcion":"...","como_descubrirlo":"..."}],"hazards":[{"tipo":"...","descripcion":"...","stages":["..."]}],"chaos":[{"tipo":"...","descripcion":"...","trigger":"..."}]}}]'::jsonb,
  '[{"secreto":"...","pistas":["pista A","pista B","pista C"],"quien_sabe":"..."}]'::jsonb,
  '[{"npc_id":"uuid_o_null","nombre":"...","raza":"...","rol":"...","flag":"existente|nuevo","relacion_sesion":"...","motivacion":"...","tono":"...","frase":"...","primera_impresion":"...","notas_roleplay":"..."}]'::jsonb,
  '[{"nombre":"...","tipo":"...","region":"...","relacion_sesion":"...","descripcion_sensorial":"..."}]'::jsonb,
  '[{"item_id":"uuid","nombre":"...","rareza":"...","flag":"match_directo|reskin","reskin_flavor":"... o null","portador_sugerido":"..."}]'::jsonb,
  '[{"monstruo_id":"uuid","nombre":"...","cantidad":1,"flag":"match_directo|reskin","contexto_narrativo":"...","reskin_primera_senal":"... o null","reskin_encuentro":"... o null","reskin_comportamiento":"... o null"}]'::jsonb,
  '{"pregunta_objetivos":"...","duracion_horas":3,"notas_dm":[]}'::jsonb
)
RETURNING id, nombre, fecha_sesion, estado;
```

Captura el `session_plan_id` — lo necesita el Paso 6.

---

## Paso 5 — Confirmar creación

Confirma al DM mostrando: `id`, `nombre`, `fecha_sesion`, `estado`, y un resumen (# de escenas,
# de NPCs por flag, # de tesoros, # de monstruos).

---

## Paso 6 — Auditoría final *(cierre de la skill)*

Este es el **último paso** de la skill. La skill no termina hasta que este reporte se emite.

Lanza un **subagente auditor** (Agent tool, `subagent_type=general-purpose`) con prompt fijo que
incluye la lista de reglas abajo y el `session_plan_id` del Paso 4b. El auditor tiene acceso al
Supabase MCP para verificaciones. **Solo reporta — no edita ni inserta.**

**El auditor verifica 3 dimensiones:**

### 1. Cumplimiento de reglas duras (determinístico, verificable contra BD)

- `bloque_npcs` tiene ≥6 entries, con exactamente 2 flag=`nuevo` y ≥4 flag=`existente`.
- Cada NPC tiene `npc_id` apuntando a una fila real en `npcs` (SELECT de verificación). Si un
  NPC flag=`nuevo` no tiene `npc_id`, es issue crítico (la transición no se hizo).
- Cada NPC tiene `relacion_sesion` no vacía.
- Cada locación en `bloque_locaciones` tiene `relacion_sesion` no vacía.
- Cada tesoro en `bloque_tesoros` tiene `item_id` que existe en `items` con `campaign_slug='halo'`.
- Cada monstruo en `bloque_monstruos` tiene `monstruo_id` que existe en `monstruos`.
- Cada tesoro y monstruo tiene flag `match_directo | reskin`. Si es reskin, flavor/capas completas.
- Cada escena con `tipo='combate'` tiene el campo `ejes` con `protein` + ≥2 ejes adicionales
  (Optimizers/Hazards/Chaos). Regla de Tres cumplida. Si Protein = `Kill Them`, debe tener
  `retreat_number` definido.
- Secretos no duplican info ya conocida por el party (crosscheck contra `resumen` de `notas_dm`
  consultadas en Paso 1b).
- `nombre` en formato `"Sesión DD-MMM-YY"`, `fecha_sesion` ISO, `estado='borrador'`, `campaign_slug='halo'`.

### 2. Cohesión narrativa (cualitativo)

- NPCs referenciados en ≥1 escena, secreto o locación (nadie huérfano).
- Locaciones consistentes con las escenas propuestas.
- Momento pivote (si aplica) conecta con ≥1 escena y ≥1 secreto.
- Tesoros y monstruos encajan en escenas concretas (no cuelgan sueltos).
- Tono uniforme entre secciones.

### 3. Calidad de contenido (cualitativo ligero)

- `bloque_strong_start` es concreto (tiene detalle sensorial), no genérico.
- Cada NPC nuevo tiene `primera_impresion` + `notas_roleplay` según formato dnd-worldbuilder.
- Escenas llevan objetivo + obstáculo explícitos.

**Formato del reporte** (cierre de la skill al DM):

```
📋 Auditoría — Sesión [nombre] (id: [uuid])

[REGLAS]    ✓ 8/8 checks
[COHESIÓN]  ✗ 2 issues
[CALIDAD]   ⚠ 1 observación

Issues:
- [COHESIÓN] NPC "Dona Ferris" no aparece en ninguna escena ni secreto.
- [COHESIÓN] Tesoro "Hilo de plata" no tiene portador en ninguna escena.
- [CALIDAD] bloque_strong_start es genérico ("los jugadores llegan a la taberna").

¿Corrijo y actualizo el plan en Supabase? (S/N)
```

**Flujo post-reporte:**
- Reporte limpio (0 issues) → skill termina con confirmación al DM.
- Con issues → el DM decide: corregir (la skill hace UPDATE sobre los `bloque_*` del plan ya
  insertado), dejar como está, o iterar. **No re-insertar ni duplicar registros.**

---

## Paso 7 — Feedback post-sesión (opcional, desacoplado)

Si Vicente quiere dar feedback rápido después de jugar, máximo 3 preguntas:

1. ¿Qué sección fue más útil?
2. ¿Qué faltó o sobró?
3. ¿Algo específico para recordar la próxima vez?

Guardar en `references/learnings.md` bajo la sección correspondiente.

---

## Integración con `dnd-worldbuilder` (invocación cruzada)

Esta skill **delega a `dnd-worldbuilder`** cuando necesita generar entidades nuevas o reskin.
La worldbuilder vive en `../dnd-worldbuilder/` y tiene las referencias narrativas.

**Cuándo invocar:**

| Necesidad | Referencia a usar | Input mínimo |
|-----------|-------------------|--------------|
| NPC nuevo (2 por sesión) | `../dnd-worldbuilder/references/npc.md` | Ciudad, rol narrativo, conexión a quest/sesión |
| Reskin de item | `../dnd-worldbuilder/references/item.md` | `item_id` base, nuevo contexto/tono |
| **Combate / encuentro** | `../dnd-worldbuilder/references/combate.md` | Party composition, ubicación, quest/tono, catálogo `monstruos` filtrado |

**Qué esperar:**
- NPC: bloque con `primera_impresion` y `notas_roleplay`, listo para commit a tabla `npcs`
  y para `bloque_npcs` del session_plan.
- Item (reskin): flavor nuevo con el `item_id` base preservado, para `bloque_tesoros`.
- Combate: **dos piezas** — una escena tipo `combate` con campo `ejes` JSONB (Protein +
  Optimizers + Hazards + Chaos) para `bloque_escenas`, y N entradas de monstruos para
  `bloque_monstruos` (con reskin opcional de 3 capas sensoriales).
- Coherencia con `../dnd-worldbuilder/references/principles.md` (15 principios narrativos)
  y, en combates, con el framework Encounter Axis + tabla XP XDMG 2024.

La worldbuilder puede leerse directamente desde su `references/` — no es una sub-skill separada
que se active, es un banco de patrones al que esta skill consulta.

---

## Estilo narrativo

- Segunda persona dirigida al DM: "Tus jugadores llegan a...", "Recuerda que Sera..."
- Tono: **cinematic, conciso, directo** — como Matt Mercer habla, no como se escribe un ensayo
- Escenas: listas de lo esencial, no párrafos de prosa
- NPCs: arquetipo claro + qué quieren + cómo suenan. Sin monólogos preparados
- **Campos de NPC visibles en el planner (UI):** `rol`, `motivacion`, `tono`, `frase`, `relacion_sesion`
- **Campos de NPC para Supabase (commit):** `primera_impresion`, `notas_roleplay`, `raza`, `edad`
- `primera_impresion`: descripción sensorial en acción ("mostrar no decir", "NPCs en movimiento
  no en pose"). Lo que el DM narra al presentar al NPC por primera vez.
- `notas_roleplay`: muletillas, patrones de habla, reacciones típicas. Solo para el DM.
- Generar SIEMPRE ambas capas para NPCs nuevos. Para NPCs existentes, no sobreescribir.
- Calibrar cantidad de escenas por duración (**NPCs siguen siendo ≥6**): 2h → 2-3 escenas;
  4h → 4-5 escenas.

---

## Estructura de datos en Supabase

**Proyecto:** `dwmzchtqjcblupmmklcl` · **Campaign slug:** `halo`

### Tablas operativas

| Tabla | Columnas clave | Notas |
|-------|----------------|-------|
| `notas_dm` | nombre, fecha, resumen, contenido_html, jugadores_presentes (text[]) | Sesiones del DM |
| `quests` | nombre, estado (Activa/Completada/En pausa), resumen, contenido_html | Misiones |
| `npcs` | nombre, raza, rol, estado, tipo_npc, ciudad_id, establecimiento_id, primera_impresion, notas_roleplay, edad, campaign_slug | PJs no jugadores |
| `ciudades` | nombre, descripcion, lider, poblacion, estado, conocida_jugadores | Ciudades del mapa |
| `establecimientos` | nombre, tipo, ciudad_id, dueno_id, descripcion_exterior, descripcion_interior | Tiendas, tabernas |
| `items` | nombre, tipo, rareza, personaje_id, npc_portador_id, descripcion, requiere_sintonizacion, campaign_slug | **Catálogo de tesoros** (siempre origen real) |
| `personajes` | nombre, clase, raza, jugador, nivel, ac, hp_maximo | PJs del party |
| `lugares` | nombre, tipo, region, ciudad_id | Puntos de interés |
| `monstruos` | nombre, tipo, tamano, cr, entorno, hp, ac, rasgos, acciones, … | **Catálogo 5e oficial** — compartido entre campañas (sin `campaign_slug`) |
| `session_plans` | nombre, fecha_sesion, estado, campaign_slug, **bloque_strong_start**, **bloque_escenas**, **bloque_secretos**, **bloque_npcs**, **bloque_locaciones**, **bloque_tesoros**, **bloque_monstruos**, input_data | **Destino final del prep**. Bloques en columnas separadas (jsonb). |

### Junction tables (relaciones M2M)

| Junction | Conecta |
|----------|---------|
| `npcs_quests` | NPCs ↔ Quests |
| `npcs_items` | NPCs ↔ Items |
| `npcs_lugares` | NPCs ↔ Lugares |
| `quests_ciudades` | Quests ↔ Ciudades |
| `quests_establecimientos` | Quests ↔ Establecimientos |
| `quests_notas_dm` | Quests ↔ Notas DM |
| `quests_lugares` | Quests ↔ Lugares |
| `personajes_items` | Personajes ↔ Items |

### Visibilidad y soft delete

- Ciudades: `conocida_jugadores` (boolean)
- NPCs, Items, Lugares, Establecimientos: `conocido_jugadores` (boolean)
- Soft delete: `archived = true` (no borrar, marcar como archivado)

### Jugadores del party

Tino, Caco, Leo, Enoch, Hiram. Campo `jugadores_presentes` en `notas_dm` es text array.

---

## Referencias

- `references/learnings.md` — Memoria del skill (preferencias, reglas aprendidas, historial)
- `references/session-structure.md` — Plantilla detallada del contenido de sesión
- `../dnd-worldbuilder/references/npc.md` — Formato NPC (primera_impresion + notas_roleplay)
- `../dnd-worldbuilder/references/item.md` — Formato item (3 capas: apariencia, sensación, historia)
- `../dnd-worldbuilder/references/combate.md` — Formato combate (framework Encounter Axis + tabla XP XDMG 2024 + 3 capas sensoriales opcionales del monstruo-Protein)
- `../dnd-worldbuilder/references/location.md` — Formato locación (aproximación, interior, peligros)
- `../dnd-worldbuilder/references/principles.md` — 15 principios narrativos (benchmark Matt Mercer)
