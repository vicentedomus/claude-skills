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

## Paso 0.5 — Verificar graphify (el acceso a la musa)

Antes del co-diseño, confirma que el CLI de graphify y el grafo están disponibles — el compendio
es la **primera fuente de inspiración** para todo elemento nuevo (NPC, locación, gancho, tono):

```bash
graphify --help                                          # ¿responde el CLI?
cd questkeep/compendium && graphify query "test"         # ¿hay graph.json?
```

Si responde, úsalo por la **vía sancionada** (`graphify query "<tema>"`, `graphify explain "<nodo>"`,
`graphify path "A" "B"`) — ver el principio "Compendio primero (la musa)" en el Paso 3. Si NO
responde (no instalado / sin `graph.json`), **avísale al DM** y sigue con los principios narrativos
como fallback.

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
-- Recap de sesión(es) previa(s) — vive en la BITÁCORA DEL DM (ya no en notas_dm,
-- que no existe en el schema public de Halo). El cuerpo abre con "Sesión DD-MMM-YY"
-- y suele cerrar con "Notas/Ideas para la siguiente sesión" — léelas y aplícalas.
-- Las menciones @[Nombre](tabla:uuid) dan el id exacto de cada entidad referida.
SELECT m.id, m.created_at::date AS fecha,
       regexp_replace(m.content_html, '<[^>]+>', ' ', 'g') AS texto
FROM public.bitacora_mensajes m
JOIN public.bitacoras b ON b.id = m.bitacora_id
WHERE b.campaign_slug = 'halo' AND b.owner_role = 'dm' AND m.deleted_at IS NULL
ORDER BY m.created_at DESC
LIMIT 10;

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

**Catálogos de referencia (tesoros y monstruos) — SE RESUELVEN CONTRA EL ETL, no contra Supabase.**

> ⚠️ **Corrección importante.** El catálogo vigente **NO** es la tabla Supabase `items_catalog`
> (669 filas `DMG'24` huérfanas, magic-only, sin commons) ni `monstruos` (~6 filas). El pool real es el
> **ETL** que carga QuestKeep, leído directo del clon:
>
> - **Tesoros** → `questkeep/data/5e/items.json` (1941, XDMG 2024, con Common/Artifact).
> - **Statblocks** → `questkeep/data/5e/bestiary.json` (711, XMM 2025; trae Commoner, Guard, Mage,
>   Bandit Captain, Gladiator…).
>
> Delegar la resolución a `../dnd-worldbuilder/references/catalogos.md` (match_directo · reskin=homebrew
> con `base` · nunca inventar). Las tablas `monstruos`/`items_catalog` quedan **solo** como destino de
> homebrew (`es_homebrew`, `base`). Filtrar el ETL por substring (`cr`/`tipo` son strings compuestos).

```sql
-- Party real (para calibrar combate): nivel/clase de los PJs
SELECT nombre, clase, raza, nivel, ac, hp_maximo
FROM personajes
WHERE campaign_slug = 'halo' AND NOT archived
ORDER BY nombre;
```

**Higiene de datos al leer entidades:** la BD tiene ruido — entradas de prueba (p. ej.
"Fighter Prueba", "Pruebo"), animales/monturas ("Nelly la Yegua", "Altino el Caballo Albino")
y a veces **duplicados** (pasó con un "Dabblewick" repetido). Al contar el party para el
combate, **descarta los que no son PJs reales**. Si detectas duplicados o registros basura
relevantes a la sesión, **repórtalos al DM** (no los borres sin permiso).

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

### Paso 3 — Construir la propuesta (co-diseño sección por sección)

**Modo de trabajo preferido del DM (co-diseño):** no entregar el borrador completo de golpe.
Recorrer las etapas de la sesión **una por una** y, en cada sección, **ofrecer 3 opciones**
distintas (no variaciones cosméticas: deben diferir en enfoque, tono o consecuencia). El DM
elige una, pide mezclar, o pide ajustar; recién entonces se pasa a la siguiente sección. El
prep se va construyendo en conjunto, no se presenta cerrado.

Orden sugerido de las etapas: **Strong Start → Escenas → Combate → Secretos & Pistas → NPCs
(4 existentes + 2 nuevos) → Locaciones → Tesoros → Momento pivote → Notas DM.**

Para cada sección:
1. Presenta **3 opciones** etiquetadas (A/B/C) con 1-2 líneas cada una y, si aplica, su
   gancho/consecuencia. Da una recomendación breve.
2. Espera la decisión del DM (elige / mezcla / ajusta).
3. Fija lo acordado y avanza a la siguiente etapa.

Mantén un **resumen vivo** de lo ya fijado para que el DM no pierda el hilo entre secciones.
Solo cuando todas las secciones estén acordadas se arma el borrador final y se pasa al Paso 4.

Principios guía (aplican a todas las opciones que ofrezcas):

- **Prep = ingredientes, no script**: el DM improvisa sobre esto
- **Strong Start**: la apertura lanza la acción de inmediato, sin preámbulo
- **Escenas posibles**: 3-5 escenas con objetivo + obstáculo cada una
- **Secrets & Clues**: múltiples caminos a la misma información
- **Mundo se sigue expandiendo**: 2 NPCs nuevos por sesión, bien integrados
- **Compendio primero (la musa)**: para cualquier elemento NUEVO (NPC, locación, gancho, tono de
  escena), consulta primero el **compendio de flavor** (`questkeep/compendium/graphify-out/`) por la
  **vía sancionada del CLI**: `graphify query "<tema>"`, `graphify explain "<nodo>"`,
  `graphify path "A" "B"` (o lee `GRAPH_REPORT.md` para hyperedges/arquetipos). Toma un
  arquetipo/`theme`/`motif` como semilla, **limando los nombres propios Y los tags de dominio que no
  encajen**: el grafo es **multi-libro (~3.072 nodos / 377 archivos, NO solo Ravenloft)**, así que
  un nodo puede arrastrar el setting de su libro (p. ej. Batan trae el tag "Dominion of Shatrekvan"
  de Ravenloft, que no pega con goliaths) → quédate con el arquetipo, descarta el setting. Inventar
  desde cero es el último recurso. (El compendio es inspiración; Supabase es la fuente de verdad.)
- **Nada inventado**: todo secreto/gancho/pista nace de un hecho en BD o recap, o se marca como propuesta nueva a aprobar. No disfrazar flavor de NPC (p. ej. una línea de `notas_roleplay`) como secreto de trama.
- **Consistencia causal**: si un NPC posee un objeto o sabe algo, debe haber una razón in-world explícita. Cazar plotholes antes de presentar (¿de dónde sacó X esa prueba/llave/carta?).
- **Decisión con consecuencias**: cuando ofrezcas una elección importante, telegrafía la ruta alternativa para que los jugadores la vean, dale a cada rama su propio beat/combate, y cierra con una escena de Desenlace que enumere los resultados.

**Reglas duras por sección** (se auditan en el Paso 6):

#### NPCs — **mínimo 6, composición 4 existentes + 2 nuevos**

- **4 existentes**: selecciona los más relevantes a la quest, ciudad o lugar objetivo de la sesión.
- **2 nuevos**: genera frescos invocando el flujo de `dnd-worldbuilder` con `references/npc.md`
  (primera_impresion + notas_roleplay, con las capas sensoriales y manierismos de ese formato).
  Ese flujo ya consulta el **compendio** primero (su Paso 0.5) — ánclalos a un arquetipo/`theme`
  del grafo (con nombres propios limados) antes de inventar.
- Cada NPC (existente o nuevo) lleva el campo **"Relación con la sesión"**: qué rol narrativo cumple,
  por qué aparece, cómo se cruza con los objetivos. No vale dejarlo vacío.
- Marca cada NPC con flag `existente` o `nuevo`. Este flag se preserva como snapshot histórico
  de esa sesión.
- La transición `nuevo → existente` en la BD ocurre en el Paso 4 (ver abajo).

#### Locaciones — **cada una explica su relación con la sesión**

- Cada locación lleva campo "Relación con la sesión": qué escena ocurre ahí, qué rol cumple
  (combate, social, revelación, exploración). No vale dejarlo vacío.

#### Secretos & ganchos — **anclados a la fuente, nada inventado**

- Cada secreto sale de (a) un hecho en BD (quest, NPC, item, recap) o (b) se marca como
  **propuesta nueva** para que el DM la apruebe. Nunca presentar como "secreto de sesión" algo
  que en realidad es flavor de un NPC (p. ej. una muletilla de `notas_roleplay`).
- **Múltiples caminos (rule of three):** entidades o info *gated* por investigación (un NPC
  oculto, una prueba) deben tener ≥2-3 vías de descubrimiento, repartidas entre lo social y lo
  de acción, para que el grupo no se quede sin verlo.
- **Plothole check:** antes de presentar, pregunta por cada pieza clave "¿por qué este NPC
  tiene/sabe esto?". Si no hay razón in-world, invéntala con base en el mundo existente o
  recórtala. (Ej. real: "¿por qué Rammel tiene el libro de Torben?" → porque archiva el
  comercio de la ciudad y descifró los manifiestos.)

#### Tesoros — **SOLO items reales del catálogo `items_catalog`**. Regla de prioridad estricta:

> **Fuente correcta:** `items_catalog` es el catálogo global 5e (≈668 items, fuente `DMG'24`),
> análogo a `monstruos`. La tabla `items` son las **instancias** de campaña (lo que alguien posee,
> con `personaje_id`/`npc_portador_id`). Para elegir un tesoro se busca en `items_catalog`.

1. **Primero** busca un item en `items_catalog` que satisfaga la necesidad narrativa tal cual.
   Si encaja (efecto y tono), úsalo sin tocar nada.
2. **Solo si ningún item del catálogo encaja**, aplica **reskin narrativo** invocando `dnd-worldbuilder`
   con `references/item.md`. El reskin cambia flavor (nombre, descripción) pero **mantiene el item
   base como referencia** (mismas stats y efectos).
3. **Nunca inventar** items. Si la trama exige un item oficial que no está en el catálogo (p. ej.
   un item 2014 fuera del DMG'24), **darlo de alta primero en `items_catalog`** con su texto
   oficial verbatim (en inglés, por convención del proyecto) — extraído de la fuente, no de memoria.

Cada tesoro lleva: `item_id` de `items_catalog`, flag `match_directo | reskin`, y si es reskin el flavor aplicado.

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

**Dificultad — calibrar contra el party REAL y mostrar la cuenta:**

1. Lee `personajes` (`campaign_slug='halo'`) y **cuenta los PJs reales**, descartando entradas
   de prueba/animales (p. ej. "Fighter Prueba", "Pruebo", monturas como "Nelly la Yegua"). Usa
   nivel y cantidad reales — no asumas 4.
2. Calcula el presupuesto con la **tabla XP por personaje XDMG 2024** (abajo; Low/Moderate/High,
   sin multiplicador por cantidad) × nº de PJs. Ej.: 5 PJs nivel 4 → Low 1 250 / Moderate 1 875 /
   **High = 2 500**. (Si el DM pide un combate **deadly**, puede gastarse por encima del High
   oficial; eso es caso por caso y suele pedir una mitigación que el DM defina.)

   **Tabla XP budget por personaje (XDMG 2024)** — multiplica por nº de PJs reales:

   | Nivel | Low | Moderate | High | | Nivel | Low | Moderate | High |
   |---|---|---|---|---|---|---|---|---|
   | 1 | 50 | 75 | 100 | | 11 | 1 900 | 2 900 | 4 100 |
   | 2 | 100 | 150 | 200 | | 12 | 2 200 | 3 700 | 4 700 |
   | 3 | 150 | 225 | 400 | | 13 | 2 600 | 4 200 | 5 400 |
   | 4 | 250 | 375 | 500 | | 14 | 2 900 | 4 900 | 6 200 |
   | 5 | 500 | 750 | 1 100 | | 15 | 3 300 | 5 400 | 7 800 |
   | 6 | 600 | 1 000 | 1 400 | | 16 | 3 800 | 6 100 | 9 800 |
   | 7 | 750 | 1 300 | 1 700 | | 17 | 4 500 | 7 200 | 11 700 |
   | 8 | 1 000 | 1 700 | 2 100 | | 18 | 5 000 | 8 700 | 14 200 |
   | 9 | 1 300 | 2 000 | 2 600 | | 19 | 5 500 | 10 700 | 17 200 |
   | 10 | 1 600 | 2 300 | 3 100 | | 20 | 6 400 | 13 200 | 22 000 |
3. **Default del DM: al menos un combate difícil (tier High).** Apunta el total cerca de High.
4. **Composición = pieza central temática + apoyos**, no un enjambre de CR trivial. Una criatura
   ancla con buena economía de acción (boss/coloso, con reskin si hace falta para el tono) +
   minions. Evita rellenar solo con CR 1/8–1/4.
5. **Muestra la cuenta** al presentar el combate: lista monstruos, XP de cada uno, total y tier
   resultante vs. el umbral del party. Detalle del framework en
   `../dnd-worldbuilder/references/combate.md`.

**Otras validaciones antes de presentar el borrador:**

- **Items de personajes:** nunca asumir que un PJ posee un item si no está en la tabla `items`
  con `personaje_id` apuntándolo. "Quiero que X obtenga Y" es quest futura, no hecho actual.
- **Secretos:** crosscheck contra resúmenes de sesiones consultadas en Paso 1b. Si los jugadores
  ya lo saben, no es secreto — busca algo nuevo.

#### Desenlace — **obligatorio si la sesión tiene una decisión bifurcante**

Si el pivote ofrece una elección de peso (p. ej. aliarse vs. traicionar), incluye una **escena
final de Desenlace** en `bloque_escenas` que enumere cada rama y sus consecuencias concretas
(qué gana/pierde el grupo, qué relación queda con los NPCs, qué semilla de futuro). Sin combate
ni ejes; es el aterrizaje de la decisión. Vigila que ambas ramas sigan siendo **tentadoras**:
si un giro vuelve una opción "claramente mala" (ej. la trata volvió a Torben villano puro),
avisa al DM del corrimiento de tono y reajusta qué compra cada rama para que la elección pese.

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

El frontend de QuestKeep (`preparador.js`) lee el plan desde **una sola columna `bloques`**
(jsonb anidado) — `plan.bloques['bloque_strong_start']`, `plan.bloques['bloque_escenas']`, etc. —
más una columna `bloques_committed` (jsonb). **NO leas/escribas las columnas legacy sueltas**
(`bloque_strong_start`, `bloque_escenas`, …): existen por compatibilidad pero la UI las ignora,
y un plan escrito ahí sale **vacío** en el planner. Todos los bloques van anidados dentro de
`bloques`. Hacer un solo INSERT:

```sql
INSERT INTO session_plans (
  nombre, fecha_sesion, estado, campaign_slug,
  bloques,
  bloques_committed,
  input_data
) VALUES (
  'Sesión DD-MMM-YY',
  'YYYY-MM-DD',
  'borrador',
  'halo',
  '{
    "bloque_strong_start": "texto del strong start",
    "bloque_escenas": [{"titulo":"...","descripcion":"...","tipo":"combate|social|exploración|misterio|revelación","tension":1,"objetivo":"...","obstaculo":"...","espacio":"... (solo combate)","secretos":[{"secreto":"...","pistas":["pista A","pista B","pista C"],"quien_sabe":"..."}],"es_pivote":false,"pivote":"texto del pivote SI esta escena es el momento bisagra; si no, null","ejes":{"protein":{"tipo":"...","descripcion":"...","condicion_cierre":"...","retreat_number":null},"optimizers":[{"tipo":"...","descripcion":"...","como_descubrirlo":"..."}],"hazards":[{"tipo":"...","descripcion":"...","stages":["..."]}],"chaos":[{"tipo":"...","descripcion":"...","trigger":"..."}]}}],
    "bloque_npcs": [{"npc_id":"uuid_o_null","nombre":"...","raza":"...","rol":"...","flag":"existente|nuevo","relacion_sesion":"...","motivacion":"...","tono":"...","frase":"...","primera_impresion":"...","notas_roleplay":"..."}],
    "bloque_locaciones": [{"nombre":"...","tipo":"...","region":"...","relacion_sesion":"...","descripcion_sensorial":"..."}],
    "bloque_tesoros": [{"item_id":"uuid_de_items_catalog","nombre":"...","rareza":"...","flag":"match_directo|reskin","reskin_flavor":"... o null","portador_sugerido":"..."}],
    "bloque_monstruos": [{"monstruo_id":"uuid","escena_idx":0,"nombre":"...","cantidad":1,"flag":"match_directo|reskin","contexto_narrativo":"...","reskin_primera_senal":"... o null","reskin_encuentro":"... o null","reskin_comportamiento":"... o null"}],
    "bloque_secretos": [],
    "bloque_pivote": null,
    "bloque_notas_dm": ["nota privada DM 1", "nota privada DM 2"]
  }'::jsonb,
  '{}'::jsonb,
  '{"pregunta_objetivos":"...","duracion_horas":3,"notas_dm":[]}'::jsonb
)
RETURNING id, nombre, fecha_sesion, estado;
```

Captura el `session_plan_id` — lo necesita el Paso 6.

> **Nota de migración:** los bloques viven **dentro** de `bloques` (jsonb), no en columnas
> sueltas. Para verificar/auditar un plan, consulta `bloques->'bloque_npcs'`,
> `bloques->>'bloque_strong_start'`, etc. — no las columnas `bloque_*` legacy.

**Contrato de render del planner (`preparador.js`) — cómo se anidan los bloques:**

- **Secretos y pivote van DENTRO de cada escena** (`bloque_escenas[i].secretos[]` y
  `bloque_escenas[i].es_pivote` / `bloque_escenas[i].pivote`). El planner pinta las escenas
  **en orden** (apoyo narrativo de "qué sigue") y muestra los secretos y el pivote dentro de
  su escena. `bloque_secretos` y `bloque_pivote` quedan **deprecados** (`[]` / `null`): solo
  se usan como fallback para planes viejos. **No** dupliques la info en ambos lados.
- **Cada monstruo lleva `escena_idx`** (índice 0-based dentro de `bloque_escenas`) que lo liga
  a su escena de combate. La pestaña Combate agrupa por encuentro: muestra los **Ejes/Hazards**
  de la escena y el **statblock base** de cada monstruo, leído del catálogo `monstruos` vía
  `monstruo_id` (o por nombre si falta el id). Sin `escena_idx`, el monstruo no se agrupa.
- **Tesoros:** `item_id` referencia el catálogo global **`items_catalog`** (no `items`).
  `items` es el inventario instanciado de la campaña. Si el item no existe en `items_catalog`
  (p. ej. items 2014 fuera del DMG'24), **darlo de alta primero** en `items_catalog` con su
  texto oficial verbatim; al entregarse al party se instancia en `items` con `personaje_id`.

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

> Los bloques se consultan dentro de la columna `bloques` (jsonb): `bloques->'bloque_npcs'`,
> `bloques->>'bloque_strong_start'`, `jsonb_array_length(bloques->'bloque_monstruos')`, etc. Un
> plan con `bloques` NULL o `{}` está vacío para la UI aunque las columnas legacy tengan datos.

**El auditor verifica 3 dimensiones:**

### 1. Cumplimiento de reglas duras (determinístico, verificable contra BD)

- `bloque_npcs` tiene ≥6 entries, con exactamente 2 flag=`nuevo` y ≥4 flag=`existente`.
- Cada NPC tiene `npc_id` apuntando a una fila real en `npcs` (SELECT de verificación). Si un
  NPC flag=`nuevo` no tiene `npc_id`, es issue crítico (la transición no se hizo).
- Cada NPC tiene `relacion_sesion` no vacía.
- Cada locación en `bloque_locaciones` tiene `relacion_sesion` no vacía.
- Cada tesoro en `bloque_tesoros` tiene `item_id` que existe en `items_catalog` (o, si se dio de
  alta un item oficial nuevo, que ya esté insertado en `items_catalog`).
- Cada monstruo en `bloque_monstruos` tiene `monstruo_id` que existe en `monstruos` **y** un
  `escena_idx` válido (índice 0-based dentro de `bloque_escenas`, apuntando a una escena de combate).
- Cada tesoro y monstruo tiene flag `match_directo | reskin`. Si es reskin, flavor/capas completas.
- Cada escena con `tipo='combate'` tiene el campo `ejes` con `protein` + ≥2 ejes adicionales
  (Optimizers/Hazards/Chaos). Regla de Tres cumplida. Si Protein = `Kill Them`, debe tener
  `retreat_number` definido.
- **Dificultad de combate:** la suma de XP de los monstruos (por `escena_idx`) está calibrada
  contra el party real (nº de PJs × tabla XDMG 2024), y por defecto ≥1 combate alcanza tier
  **High**. Combates de puro CR trivial sin pieza central → issue.
- **Secretos y pivote anidados:** los secretos viven en `bloque_escenas[i].secretos[]` y el pivote
  en `bloque_escenas[i].pivote` (+`es_pivote`). `bloque_secretos`/`bloque_pivote` deben estar
  vacíos/null (deprecados). Issue si la info está duplicada en ambos lados o solo en los legacy.
- Secretos no duplican info ya conocida por el party (crosscheck contra los recaps de la
  bitácora del DM consultados en Paso 1b).
- `nombre` en formato `"Sesión DD-MMM-YY"`, `fecha_sesion` ISO, `estado='borrador'`, `campaign_slug='halo'`.

### 2. Cohesión narrativa (cualitativo)

- NPCs referenciados en ≥1 escena, secreto o locación (nadie huérfano).
- Locaciones consistentes con las escenas propuestas.
- Momento pivote (si aplica) conecta con ≥1 escena y ≥1 secreto.
- Tesoros y monstruos encajan en escenas concretas (no cuelgan sueltos).
- Tono uniforme entre secciones.
- **Consistencia causal (plotholes):** cada prueba/objeto/conocimiento que tiene un NPC tiene
  una razón in-world rastreable en el plan. Marca como issue cualquier "¿de dónde sacó esto?"
  sin respuesta (ej. un NPC que tiene un documento incriminatorio sin explicar cómo llegó a él).
- **Nada inventado:** ningún secreto es flavor de NPC reciclado como trama; cada secreto/gancho
  ancla a BD/recap o estaba marcado como propuesta aprobada por el DM.
- **Desenlace:** si hay decisión bifurcante, existe una escena de cierre que enumera las ramas y
  ambas siguen siendo opciones tentadoras (ninguna es obviamente la "correcta").

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

**Proyecto:** `dwmzchtqjcblupmmklcl` · **Schema:** `public` · **Campaign slug:** `halo`

> Halo vive en el schema `public` (`campaign_slug='halo'`). Los recaps de sesión NO están en
> `notas_dm` (esa tabla solo existe en otras campañas, p. ej. el schema `tierras_perdidas`):
> para Halo viven en la **bitácora del DM** (`public.bitacoras` + `public.bitacora_mensajes`).

### Tablas operativas

| Tabla | Columnas clave | Notas |
|-------|----------------|-------|
| `bitacoras` | campaign_slug, owner_role ('dm'/'player'), personaje_id | La del DM (`owner_role='dm'`) guarda los recaps de sesión |
| `bitacora_mensajes` | bitacora_id, author_role, content_html, created_at, deleted_at | Cada recap del DM es un mensaje (`content_html`); filtrar `deleted_at IS NULL` |
| `quests` | nombre, estado (Activa/Completada/En pausa), resumen, contenido_html | Misiones |
| `npcs` | nombre, raza, rol, estado, tipo_npc, ciudad_id, establecimiento_id, primera_impresion, notas_roleplay, edad, campaign_slug | PJs no jugadores |
| `ciudades` | nombre, descripcion, lider, poblacion, estado, conocida_jugadores | Ciudades del mapa |
| `establecimientos` | nombre, tipo, ciudad_id, dueno_id, descripcion_exterior, descripcion_interior | Tiendas, tabernas |
| `items_catalog` | nombre, fuente, rareza, tipo, requiere_sintonizacion, descripcion, valor | **Catálogo global 5e** (≈668, `DMG'24`), sin `campaign_slug` — compartido. **Origen de los tesoros** (`item_id` → aquí) |
| `items` | nombre, tipo, rareza, personaje_id, npc_portador_id, descripcion, requiere_sintonizacion, campaign_slug | **Instancias** de campaña (lo que alguien posee). NO es el catálogo |
| `personajes` | nombre, clase, raza, jugador, nivel, ac, hp_maximo | PJs del party |
| `lugares` | nombre, tipo, region, ciudad_id | Puntos de interés |
| `monstruos` | nombre, tipo, tamano, cr, entorno, hp, ac, rasgos, acciones, … | **Catálogo 5e oficial** — compartido entre campañas (sin `campaign_slug`) |
| `session_plans` | nombre, fecha_sesion, estado, campaign_slug, **bloques** (jsonb), **bloques_committed** (jsonb), input_data | **Destino final del prep**. Bloques anidados dentro de `bloques` (`bloque_strong_start`, `bloque_escenas` —con `secretos[]` y `pivote` anidados por escena—, `bloque_npcs`, `bloque_locaciones`, `bloque_tesoros`, `bloque_monstruos` —con `escena_idx`—, `bloque_notas_dm`). `bloque_secretos`/`bloque_pivote` deprecados. Las columnas `bloque_*` sueltas son legacy y la UI las ignora. |

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

PJs en `public.personajes` (`campaign_slug='halo'`): Pithor, Maverick, Lupin, Doran (+ Zif
como compañero). La asistencia por sesión se infiere del recap del DM en la bitácora.

---

## Referencias

- `references/learnings.md` — Memoria del skill (preferencias, reglas aprendidas, historial)
- `references/session-structure.md` — Plantilla detallada del contenido de sesión
- `../dnd-worldbuilder/references/npc.md` — Formato NPC (primera_impresion + notas_roleplay)
- `../dnd-worldbuilder/references/item.md` — Formato item (3 capas: apariencia, sensación, historia)
- `../dnd-worldbuilder/references/combate.md` — Formato combate (framework Encounter Axis + tabla XP XDMG 2024 + 3 capas sensoriales opcionales del monstruo-Protein)
- `../dnd-worldbuilder/references/location.md` — Formato locación (aproximación, interior, peligros)
- `../dnd-worldbuilder/references/principles.md` — 15 principios narrativos (benchmark Matt Mercer)
