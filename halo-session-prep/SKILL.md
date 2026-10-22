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
  tools: [Supabase MCP]
---

# Halo — Session Prep Skill

Skill de preparación de sesiones para la campaña **Halo**. Los datos viven en Supabase (PostgreSQL).
Todas las consultas y escrituras se hacen con `execute_sql` sobre el proyecto `dwmzchtqjcblupmmklcl`
y con `campaign_slug = 'halo'` donde aplique.

**Principio central:** cada sesión se **ancla al mundo existente** (reusa NPCs, items y monstruos) y al
mismo tiempo **expande el mundo** (2 NPCs nuevos cada sesión). Los tesoros y statblocks salen del
**catálogo 5e vigente (el ETL)**, no de las tablas Supabase casi vacías — nunca se inventan (ver
`../dnd-worldbuilder/references/catalogos.md`).

**Destino: un plan modular.** El prep es un **árbol de bloques** en el Planeador de la app
(`session_plans.bloques` como array, spec 007 de questkeep). Cada sesión tiene su propia forma: la
skill no impone plantilla, enseña el vocabulario (`references/session-structure.md`) y reusa el
contrato de escritura de la skill `oneshot` (`../oneshot/references/plantilla-arbol.md`).

**Modelo de campos:** las entidades nuevas se generan con la ficha por tipo de `dnd-worldbuilder`
(`references/<tipo>.md`), pero **se escriben en los campos que la app muestra para la campaña**
(overlay `entity_schemas`): un `cf_*` que el overlay no declara no se pinta. Ver Paso 4a.
**Coexistencia:** aditivo — nada de UPDATE masivo, y a una ficha existente se le **añade**, no se le
sobrescribe. **Nunca escribir estructura ni datos sin confirmación del DM.**

---

## Paso 0: Leer learnings (SIEMPRE)

Antes de cualquier otra acción, lee `references/learnings.md`.

Ese archivo contiene preferencias del DM acumuladas de sesiones pasadas. Aplicarlas desde el
inicio evita que el DM tenga que corregir cosas ya aprendidas.

---

## Paso 0.5 — Verificar graphify (el acceso a la musa)

Antes del co-diseño, confirma que el CLI de graphify y el grafo están disponibles — el compendio
es la **primera fuente de inspiración** para todo elemento nuevo (locación, gancho, tono,
villano/arquetipo). **Los NPCs concretos quedan fuera de este gate**: van primero por npc-card
(`dnd-worldbuilder/references/npc.md` → «Semilla desde npc-cards»), JSON plano que no depende de
que este CLI esté instalado.

```bash
graphify --help                                          # ¿responde el CLI?
cd questkeep/compendium && graphify query "test"         # ¿hay graph.json?
```

Si responde, úsalo por la **vía sancionada** (`graphify query "<tema>"`, `graphify explain "<nodo>"`,
`graphify path "A" "B"`) — ver el principio "Compendio primero (la musa)" en el Paso 3. Si NO
responde (no instalado / sin `graph.json`), **avísale al DM** y sigue con los principios narrativos
como fallback (para elementos que no sean NPC concreto).

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
  AND length(regexp_replace(m.content_html, '<[^>]+>', ' ', 'g')) > 300  -- fuera los «mensaje de prueba»
ORDER BY m.created_at DESC
LIMIT 10;

-- Quest mencionada
SELECT q.id, q.nombre, q.estado, q.resumen, q.contenido_html
FROM quests q
WHERE q.campaign_slug = 'halo' AND q.nombre ILIKE '%nombre_quest%' AND NOT q.archived;

-- NPCs vinculados a la quest
SELECT n.id, n.nombre, n.raza, n.rol, n.estado, n.primera_impresion, n.notas_roleplay, n.edad, n.custom_data, c.nombre as ciudad
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
SELECT n.id, n.nombre, n.raza, n.rol, n.estado, n.primera_impresion, n.notas_roleplay, n.edad, n.custom_data
FROM npcs n
WHERE n.ciudad_id = 'uuid_ciudad' AND NOT n.archived AND n.campaign_slug = 'halo';
```

**Catálogos de referencia (tesoros y monstruos) — SE RESUELVEN CONTRA EL ETL, no contra Supabase.**

> ⚠️ **Corrección importante.** El catálogo vigente **NO** es la tabla Supabase `items_catalog`
> (669 filas `DMG'24` huérfanas, magic-only, sin commons) ni `monstruos` (~6 filas). El pool real es el
> **ETL** que carga QuestKeep, leído directo del clon:
>
> - **Tesoros** → `questkeep/data/5e/items.json` (2062, XDMG 2024, con Common/Artifact).
> - **Statblocks** → `questkeep/data/5e/bestiary.json` (1169, XMM 2025; trae Commoner, Guard, Mage,
>   Bandit Captain, Gladiator…).
>
> Delegar la resolución a `../dnd-worldbuilder/references/catalogos.md` (match_directo · reskin=homebrew
> con `base` · nunca inventar). Las tablas `monstruos`/`items_catalog` quedan **solo** como destino de
> homebrew (`es_homebrew`, `base`). Filtrar el ETL por substring (`cr`/`tipo` son strings compuestos).

```sql
-- La mesa: los PJs se agrupan en carpetas (character_folders = «mesas»). La mesa
-- del día es el default del Paso 2, no la lista cruda (que trae pruebas y monturas).
SELECT f.nombre AS mesa, p.id, p.nombre, p.clase, p.subclase, p.raza, p.nivel, p.ac, p.hp_maximo, p.jugador, p.descripcion
FROM personajes p LEFT JOIN character_folders f ON f.id = p.folder_id
WHERE p.campaign_slug = 'halo' AND NOT p.archived
ORDER BY f.nombre NULLS LAST, p.nombre;

-- Fuentes apagadas en la campaña: una criatura de aquí NO resuelve en Encuentros.
SELECT cc_disabled_sources FROM campaigns WHERE slug = 'halo';

-- Planes modulares que el DM ya dirigió (cualquier campaña): de aquí salen sus
-- convenciones de forma (reloj en el badge, costura, SEGUIMIENTO, secretos al final).
SELECT id, nombre, campaign_slug FROM session_plans
WHERE jsonb_typeof(bloques) = 'array' AND jsonb_array_length(bloques) > 0
ORDER BY updated_at DESC LIMIT 5;
```

Repasa a los PJs como pide el manual Lazy DM (§2.1): **backgrounds y descripción**. Un detalle de
la hoja suele ser el arco personal de la sesión (*«un gnomo azul que cree que es un goliath»*).

**Higiene de datos al leer entidades:** la BD tiene ruido — entradas de prueba (p. ej.
"Fighter Prueba", "Pruebo"), animales/monturas ("Nelly la Yegua", "Altino el Caballo Albino")
y a veces **duplicados** (pasó con un "Dabblewick" repetido). Al contar el party para el
combate, **descarta los que no son PJs reales**. Si detectas duplicados o registros basura
relevantes a la sesión, **repórtalos al DM** (no los borres sin permiso).

Si no encuentras algo mencionado por el DM, anótalo como `[no encontrado]` y pregunta después.

### Paso 2 — Preguntas de afinación

Con el contexto de Supabase en mano, haz **solo las preguntas necesarias** — no preguntes lo
que ya encontraste. Agrúpalas en un solo mensaje:

1. ¿Cuándo es la sesión? *(para el nombre y la fecha del plan)*
2. ¿Quién juega? Default: **la mesa** (la carpeta de `character_folders`), nombrando a cada PJ
   con su nivel. *«Los de la mesa Miércoles: Pithor 4, Lupin 4, Maverick 4, Alexios 3, Doran 4.»*
3. ¿Cuál es el objetivo de los jugadores para esa sesión?
4. ¿Cuántas horas tiene la sesión? *(calibrar contenido)*
5. ¿Hay combate? ¿Con quién, y **con qué reglamento: Flee, Mortals! o el XP del DMG 2024?**
   El reglamento **se pregunta en cada sesión** (decisión del DM, 2026-10-21): no hay default.
6. ¿Hay revelación o giro importante que quieras que ocurra?
7. ¿Hay algún NPC nuevo que quieras forzar, o dejamos que la skill proponga los 2 nuevos?

El techo es **7 preguntas** en ese mensaje, y **no se inventan preguntas fuera de esas siete**: si
vas a preguntar algo que tú mismo vas a deducir treinta líneas más abajo, no lo preguntes.

**Cada una se resuelve de una de dos formas, nunca en silencio:**

- **(a) Se omite**, porque el Paso 1b ya la contestó. Al omitirla, **nombra el dato y de dónde
  salió**: *«No te pregunto las horas — las dos últimas sesiones fueron de 3h
  (`session_plans.input_data.duracion_horas`); asumo 3h salvo que digas otra cosa.»* Una frase
  paraguas del tipo «el resto ya lo saqué de Supabase» **no vale**.
- **(b) Se pregunta, con el default ya derivado** de la BD o de `learnings.md`, para que el DM
  confirme en vez de redactar.

**Las que la BD no puede contestar se preguntan igual**: la fecha, el reglamento, el giro y el NPC
forzado no están en ninguna tabla. Ojo con inferir el día de la semana — los planes de halo son
**miércoles**; verifica el día con `date` antes de escribirlo.

**Si el reglamento es Flee, Mortals! y la mesa tiene niveles mezclados, avísalo en el mismo
mensaje.** La app promedia el nivel **hacia abajo** (`react/encuentros/estrategias/fm.ts`, como pide
el libro): con 4·4·4·3 calcula nivel 3, y un encuentro de CR 4 sale «Extremo» en su semáforo.
Pregunta a qué nivel quiere calibrar; si elige otro distinto al de la app, el plan lo dice junto al
encuentro.

**Las alertas de contradicción van aparte y no cuentan para el techo** (el DM dice que el party
está en un lugar y la bitácora dice otro). **Pero una «alerta» que le pide al DM que elija es una
pregunta, y cuenta.**

### Paso 3 — Co-diseñar el árbol

El entregable es un **plan modular**: un árbol de bloques en el Planeador de la app (spec 007).
**No hay plantilla**: cada sesión tiene su propia forma, y la skill enseña vocabulario y criterio
(`references/session-structure.md`), no un formulario.

#### 3a. Acordar la espina antes de llenarla

Propón primero **los bloques raíz** de esta sesión y espera el visto bueno. Mira los planes
modulares que el DM ya dirigió (Paso 1b) y copia sus convenciones. La forma que funciona en mesa:

- **SEGUIMIENTO** arriba: un `checklist` con badge «EN MESA» y un punto por beat de la sesión, con
  los estados con alternativa escritos («La presa: de Cumbre Rota / de Lanza de Ceniza / compartida»).
- **Beats numerados**, cada uno un `texto`, con **el reloj en el badge**: `0:15 · 35 min · ✂`
  (✂ = se puede recortar) o `NO SE CORTA`. El índice del Planeador lee esos badges como escaleta.
- **Un gancho al final**, no un cierre: es una campaña larga, la última escena siembra la siguiente.
- **LOS SECRETOS** al final, plegado, con un `checklist` hijo para tachar los que salieron.

Una sesión de viaje pide lista de beats; una sesión en un sitio pide **situación** (locación +
habitantes con su comportamiento + meta) — `questkeep/docs/lazy-dm-manual.md` §2.3.

#### 3b. Co-diseño sección por sección

**Modo de trabajo preferido del DM:** no entregar el borrador completo de golpe. Recorre las
secciones **una por una** y, en cada decisión abierta, **ofrece 3 opciones** distintas (enfoque,
tono o consecuencia; no variaciones cosméticas), con una recomendación. Si el DM rechaza las 3 y
da su propia visión, incorpórala y sigue ofreciendo opciones en la siguiente decisión abierta.
Mantén un **resumen vivo** de lo ya fijado.

Orden (el del manual Lazy DM, que manda sobre el viejo de esta skill): **strong start → secretos →
locaciones → escenas → NPCs → combate → tesoros.**

Principios guía (aplican a todas las opciones que ofrezcas):

- **Prep = ingredientes, no script**: el DM improvisa sobre esto.
- **Strong Start**: la apertura lanza la acción de inmediato, sin preámbulo.
- **Compendio primero (la musa)**: para cualquier elemento NUEVO (locación, gancho, tono de
  escena, villano, facción), consulta primero el compendio por la vía sancionada del CLI —
  `graphify query "<tema>"`, `graphify explain "<nodo>"` — y las npc-cards y `place-index.json`.
  Toma el arquetipo, **lima nombres propios y tags de setting**, y cita la semilla al proponer.
  El grafo es multi-libro: un nodo puede arrastrar el setting de su libro. Al terminar, borra
  `compendium/graphify-out/cache/` (graphify la deja y ensucia el árbol de git).
- **Nada inventado**: todo secreto, gancho o pista nace de un hecho en BD o recap, o **se marca
  como propuesta** a aprobar. Al presentar, distingue explícitamente *(hecho)* de *(propuesta)*.
- **Consistencia causal**: si un NPC posee un objeto o sabe algo, hay una razón in-world explícita.
- **Decisión con consecuencias**: telegrafía la ruta alternativa y dale a cada rama su beat.

**Las tres reglas del texto** (salieron de rechazos del DM; aplican a todo bloque `texto`):

1. **Cada momento trae su texto literal.** Una sección `LEE EN VOZ ALTA:` con el párrafo completo,
   nunca un puntero («lee su primera impresión» no basta si la escena depende de ella).
2. **Ninguna referencia queda colgando.** Todo término inventado —una institución, una facción,
   una costumbre («el Diván», «la Piedra de las Cuentas»)— se define en el plan, en una línea
   `GLOSARIO —` arriba del bloque donde aparece por primera vez. Auto-chequeo antes de escribir:
   cada sustantivo propio y cada «ese/el/la» deíctico, *¿está resuelto en esta página?*
3. **Separar lo que sabe el DM de lo que sabe la mesa**: sección `LO QUE TÚ SABES Y ELLOS NO`.

**Salidas de escena: pocas y limpias.** Normalmente dos, cada una con su consecuencia escrita para
la **siguiente sesión** (`Siguiente sesión: …`). No ramifiques por cada combinación posible: el DM
improvisa el resto.

#### NPCs — **mínimo 6: 4 existentes + 2 nuevos**

- **4 existentes**: los más relevantes a la quest, ciudad o lugar de la sesión.
- **2 nuevos**: primero una **npc-card** del compendio (`dnd-worldbuilder/references/npc.md` →
  «Semilla desde npc-cards»): filtra por `tipo_npc`×`raza`, lima el setting, nombre nuevo. Si la
  vocación no tiene cobertura, cae al grafo o a los principios. Statblock por vocación contra el
  ETL (`catalogos.md`), reverificado.
- Cada NPC lleva su **relación con la sesión** (qué rol cumple, por qué aparece). No vale vacía.
- `rol` solo admite `Neutral`/`Aliado`/`Enemigo`: `Antagonista`→`Enemigo`, `Informante`→`Neutral`.

#### Locaciones — **todo sitio con nombre es una entidad**

Si el plan nombra un sitio («el libro de salidas de la capitanía del canal»), ese sitio **nace como
fila** en `lugares` (o `establecimientos` si es un negocio con dueño) y se enlaza en el plan con chip
y mención. Se genera con `dnd-worldbuilder/references/location.md`: **propósito** ligado a la
escena, **atmósfera** con ≥2 sentidos, al menos un elemento interactivo y un **misterio menor**.

#### Secretos — **diez hechos, semillas solo en los que salen hoy**

Formato y reglas en `questkeep/docs/lazy-dm-manual.md` §2.4: el hecho abstraído, `semillas`, `QUÉ
CAMBIA` (si no cambia una decisión, una opción táctica o un trato, es relleno) y `DÓNDE` se cuelga
en el árbol. Viven en **dos sitios**: al pie de cada beat, `SECRETOS QUE PUEDEN SALIR AQUÍ` con la
semilla de esa escena, y completos en el bloque final. Crosscheck contra los recaps: si la party
ya lo sabe, no es secreto.

#### Tesoros — **del catálogo 5e vigente (el ETL), nunca inventados**

Prioridad: **match_directo** (oficial del ETL `data/5e/items.json`) > **reskin** (homebrew en
`items_catalog` con `es_homebrew` y `base`, misma mecánica) > nunca inventar. Delegar a
`../dnd-worldbuilder/references/catalogos.md`. Para el bloque `tesoro` hace falta una fila
(`items` o `items_catalog`); si el tesoro solo vive en el ETL, nómbralo en el texto.

#### Combate / Encuentro

**El reglamento es el que el DM eligió en el Paso 2.**

- **Flee, Mortals!** — lee `questkeep/docs/flee-mortals-manual.md` antes de proponer. La
  aritmética la hace `react/encuentros/estrategias/fm.ts`: no la recalcules a mano. **Prefiere
  criaturas del propio libro**: solo ellas traen **rol** (Brute, Controller, Skirmisher…), y la
  composición se arma por roles. Filtra por `source === 'FleeMortals'`: 36 nombres chocan con XMM.
  Para un monstruo único, FM pide un **Solo** (tabla de Solos), no una criatura normal sola.
- **DMG 2024** — tabla de XP por personaje (abajo) × nº de PJs reales.

**Antes de elegir ninguna criatura, comprueba que su fuente está activa en la campaña**
(`campaigns.cc_disabled_sources`, Paso 1b). Una criatura de una fuente apagada **no resuelve** en
la isla de Encuentros: sale el id crudo, «CR ?» y 0 XP.

Reglas que no cambian: **≥1 combate difícil** por default (tier High / Hard); pieza central
temática + apoyos, no enjambre trivial; **muestra la cuenta** (criaturas, CR o XP, total, umbral);
nunca inventar statblocks (match_directo del ETL > reskin homebrew con `base`).

**Llegada por sorpresa** (un refuerzo que cae en la ronda N): marca ese monstruo **oculto** en el
encuentro y añade un **peligro programado** con `revela` apuntando a él (desde questkeep #600).
Tira iniciativa y cuenta para la dificultad, pero la mesa no lo ve hasta que el peligro lo destapa.
Los **peligros** sirven también como recordatorios con ronda (una tirada de sigilo, la llegada de
un NPC); su texto es solo el nombre, así que la regla va completa en él.

**La criatura principal se describe en dos capas** (`dnd-worldbuilder/references/combate.md` §8):
**primera señal** (lo que perciben antes de verla) y **encuentro** con un **detalle ancla** que la
mesa va a repetir, ligado a una acción real de su ficha. La tercera capa, el **comportamiento en
combate**, **solo si el DM la pide**: no la escribas por default.

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

**Items de personajes:** nunca asumas que un PJ posee un item si no está en `items` con
`personaje_id` apuntándolo.

**Presentar el borrador al DM y preguntar:** «¿Quieres algún cambio?». Si aprueba → Paso 4.

---

## Paso 4 — Escribir en Supabase

### 4a. Las entidades primero, con una sola confirmación

Los bloques de la app **apuntan** a filas por id y leen la ficha viva; no guardan copias. Así que
toda entidad que el árbol vaya a referenciar **tiene que existir antes** que el árbol. Lista en un
solo mensaje todo lo que vas a escribir —con las fichas completas de lo nuevo— y pide **una**
confirmación:

| Qué | Dónde | Notas |
|---|---|---|
| NPCs nuevos | `npcs` | `campaign_slug='halo'`, `conocido_jugadores=false` |
| Sitios con nombre | `lugares` / `establecimientos` | `campaign_slug='halo'`, con `ciudad_id` y `region` |
| La quest del arco, si no existe | `quests` | `campaign_slug='halo'`, `estado='Activa'` |
| El encuentro | `encuentros` | `campaign_slug='halo'`, `estrategia` (`'fm'` o `'dnd2024'`), `party` = ids de la mesa, `monsters`, `hazards`, `user_id` del DM |
| Vínculos | `npcs_quests`, `quests_lugares` | la gente y los sitios del arco |
| Fichas existentes | `npcs` (UPDATE) | **se añade al final** de `notas_roleplay`, nunca se sobrescribe |

**Escribe en los campos que la app muestra para la campaña.** Antes de escribir, mira el overlay
(`entity_schemas`, columna `overlay`): un `cf_*` que no esté ahí **no se pinta**. En halo hoy:

- **NPCs**: `primera_impresion` (descripción sensorial en acción) + `notas_roleplay` (voz,
  motivación, secreto, ancla, `Inspiración: <card> (<fuente>)`) + `faccion` + `custom_data.cf_statblock`
  (`{"kind":"compendium","name":"…","source":"XMM"}`).
- **Lugares**: `descripcion` (propósito y qué pasa ahí), `descripcion_exterior` (atmósfera, ≥2
  sentidos), `descripcion_interior` (lo interactivo y el misterio).

**Monstruos del encuentro:** `{"id":"srd:<FUENTE>:<nombre>","count":1}` (p. ej.
`srd:FleeMortals:Griffon`), u `cat:<uuid>` para homebrew; `"oculto": true` para una llegada por
sorpresa. **Peligros:** `{"id","name","type":"always|start|mid|end","round","revela"?}`, con un
`id` corto y único en el encuentro (`h-grifo`). `revela` lleva **el mismo `id` que la entrada del
monstruo oculto** (`srd:FleeMortals:Griffon`), y no vale con `type:"always"`.
El `user_id` del DM es el `owner_user_id` de la bitácora con `owner_role='dm'` de halo (`campaigns.created_by` está vacío).

Captura los ids que devuelve cada INSERT (`RETURNING id`): el árbol los necesita.

### 4b. El árbol

**El contrato de escritura vive en `../oneshot/references/plantilla-arbol.md`. Léelo y síguelo**:
los campos por tipo, `hijos` siempre presente, un `id` uuid por bloque, **texto plano** (sin
markdown: `**` sale literal; lo único que se pinta son las menciones `@[Nombre](seccion:uuid)`, y
solo en `texto`), las reglas de la `rama`, el plegado y cómo comprobar. Esta skill no lo duplica.

Lo propio de halo:

```sql
INSERT INTO session_plans (nombre, fecha_sesion, estado, campaign_slug, bloques)
VALUES ('Sesión DD-mmm-YY', 'YYYY-MM-DD', 'borrador', 'halo', '<array de bloques>'::jsonb)
RETURNING id, jsonb_typeof(bloques) AS forma;   -- forma DEBE ser 'array'
```

- **`bloques` es un ARRAY.** Un objeto (el viejo formato de 9 claves `bloque_strong_start`,
  `bloque_escenas`…) manda el plan a la **vista legacy de solo lectura**. `input_data` va `null`.
- Bajo cada beat, sus entidades como **chips**: un bloque referencial (`npc`, `lugar`, `ciudad`,
  `establecimiento`, `tesoro`, `quest`, `statblock`) vinculado y **sin hijos** se pinta en línea, y
  los consecutivos se agrupan en una fila.
- Bajo el beat del combate, el bloque `encuentro`. Notas tácticas como `texto` hijos **solo si el DM
  las quiere**.
- Genera el árbol con un script (scratchpad) que verifique ids únicos, `hijos` presente y cero `**`
  antes del INSERT.

### 4c. Ediciones después de que el DM abrió el plan

En cuanto el DM abre o edita el plan en la app, el árbol en la base ya no es el que escribiste.
**Nunca vuelvas a escribir `bloques` entero.** Cada cambio es un `jsonb_set` (o `replace` sobre un
texto) a una ruta concreta, **con guarda** y verificación:

```sql
UPDATE session_plans SET bloques = jsonb_set(bloques, '{4,texto}',
  to_jsonb(replace(bloques #>> '{4,texto}', '<frase vieja exacta>', '<frase nueva>'))), updated_at = now()
WHERE id = '<plan>' AND position('<frase vieja exacta>' in bloques #>> '{4,texto}') > 0
RETURNING position('<frase nueva>' in bloques #>> '{4,texto}') > 0 AS ok;
```

La ruta es de índices: `'{4,texto}'` es la 5.ª raíz, `'{3,hijos,1,texto}'` el 2.º hijo de la 4.ª.
Sácala del árbol vivo, nunca de tu copia:

```sql
WITH RECURSIVE t AS (
  SELECT ARRAY[(o-1)::text] AS ruta, b AS blk FROM session_plans p, jsonb_array_elements(p.bloques) WITH ORDINALITY x(b, o) WHERE p.id = '<plan>'
  UNION ALL SELECT t.ruta || ARRAY['hijos', (o-1)::text], h FROM t, jsonb_array_elements(t.blk->'hijos') WITH ORDINALITY y(h, o)
)
SELECT array_to_string(ruta, ',') AS ruta, blk->>'tipo' AS tipo, blk->>'titulo' AS titulo FROM t ORDER BY ruta;
```

Si la guarda no encuentra nada (`RETURNING` vacío), **relee el árbol** con esa consulta: el DM
movió o borró bloques. **Lo que el DM borró no se recrea sin preguntarle.**

---

## Paso 5 — Confirmar creación

Muestra al DM: `id`, `nombre`, `fecha_sesion`, forma (`array`), nº de raíces y de bloques, y la
lista de entidades creadas con su id corto.

---

## Paso 6 — Verificación final *(cierre de la skill)*

Comprobaciones **deterministas**, contra la base, sin subagente:

1. **Forma:** `jsonb_typeof(bloques) = 'array'`.
2. **Vínculos:** recorre el árbol **completo** (no solo la raíz) y resuelve cada `refId`,
   `encuentroId` y cada mención `@[…](seccion:uuid)` de los textos. Cero rotos:

```sql
WITH RECURSIVE t AS (
  SELECT b AS blk FROM session_plans p, jsonb_array_elements(p.bloques) b WHERE p.id = '<plan>'
  UNION ALL SELECT h FROM t, jsonb_array_elements(t.blk->'hijos') h
), refs AS (
  SELECT coalesce(blk->>'refId', blk->>'encuentroId', blk->>'mapaId') AS ref FROM t
  WHERE coalesce(blk->>'refId', blk->>'encuentroId', blk->>'mapaId') IS NOT NULL AND blk->>'tipo' <> 'statblock'
  UNION ALL
  SELECT m[1] FROM t, regexp_matches(coalesce(blk->>'texto',''), '@\[[^\]]+\]\([a-z_]+:([0-9a-f-]{36})\)', 'g') AS m
)
SELECT ref FROM refs WHERE NOT EXISTS (SELECT 1 FROM npcs WHERE id::text = ref)
  AND NOT EXISTS (SELECT 1 FROM lugares WHERE id::text = ref) AND NOT EXISTS (SELECT 1 FROM ciudades WHERE id::text = ref)
  AND NOT EXISTS (SELECT 1 FROM establecimientos WHERE id::text = ref) AND NOT EXISTS (SELECT 1 FROM quests WHERE id::text = ref)
  AND NOT EXISTS (SELECT 1 FROM encuentros WHERE id::text = ref) AND NOT EXISTS (SELECT 1 FROM personajes WHERE id::text = ref)
  AND NOT EXISTS (SELECT 1 FROM items WHERE id::text = ref) AND NOT EXISTS (SELECT 1 FROM items_catalog WHERE id::text = ref)
  AND NOT EXISTS (SELECT 1 FROM mapa_nodos WHERE id::text = ref);
```

Un bloque `statblock` no entra: su `refId` es un id del bestiario (`srd:<FUENTE>:<nombre>`, el
mismo de los monstruos del encuentro) y se comprueba en el punto 3.

3. **Encuentro y statblocks:** cada `monsters[].id` y cada `refId` de un bloque `statblock` existe en el ETL **y su fuente está activa** en la campaña.
   Si el semáforo de la app no coincide con la dificultad elegida (el redondeo de FM), el plan lo
   explica junto al encuentro.
4. **Reglas** (cualitativo, lo revisas tú): ≥6 NPCs (4+2) con su relación con la sesión · todo
   sitio con nombre es entidad · las tres reglas del texto · secretos anclados con `QUÉ CAMBIA` y
   `DÓNDE` · ≥1 combate difícil con la cuenta mostrada.

**Formato del reporte:**

```
📋 Verificación — Sesión [nombre] (id: [uuid])
[FORMA]     ✓ array · N raíces · M bloques
[VÍNCULOS]  ✓ X resuelven · 0 rotos
[ENCUENTRO] ✓ fuentes activas · Hard a nivel 4 (la app dice «Extremo»: explicado en el plan)
[REGLAS]    ⚠ 1 observación
```

Con issues: el DM decide (corregir con ediciones del Paso 4c, o dejar como está). **No re-insertar
el plan ni duplicar entidades.**

### Gotchas operativos de `execute_sql` (MCP de Supabase)

- **Nunca un `;` dentro de un texto**, ni en una cadena: el MCP corta la consulta y se cuelga hasta
  el timeout de 60 s. Escribe la frase con punto o dos puntos.
- **Sin emojis de 4 bytes** (🦅) en los textos: mismo síntoma.
- **Tras un timeout, verifica con un `SELECT` antes de reintentar**: no sabes si entró.
- Textos largos con comillas: dollar-quoting (`$t$ … $t$`).

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
| **Combate / encuentro** | `../dnd-worldbuilder/references/combate.md` (+ `questkeep/docs/flee-mortals-manual.md` si el reglamento es FM) | La mesa, ubicación, quest/tono, reglamento, fuentes activas |
| **Lugar nuevo** (todo sitio con nombre) | `../dnd-worldbuilder/references/location.md` | La escena que lo pide, la ciudad |

**Qué esperar:**
- NPC: la ficha por tipo, **volcada a los campos que la app muestra** (Paso 4a), lista para `npcs`.
- Item (reskin): flavor nuevo con el base preservado, para el bloque `tesoro` o el texto del beat.
- Combate: el diseño (Protein + ejes del Encounter Axis) va **como texto del beat** y, lo que tenga
  ronda, como **peligros** del encuentro. Los monstruos van a `encuentros.monsters`. Ya no hay
  campos `ejes`, `escena_idx` ni `bloque_monstruos`.
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
- **Campos de NPC:** los que la app muestra en la campaña (Paso 4a). En halo: `primera_impresion`,
  `notas_roleplay`, `faccion`, `raza`, `edad` y `cf_statblock`.
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
| `items_catalog` | nombre, fuente, rareza, tipo, requiere_sintonizacion, descripcion, valor, es_homebrew, base | **Store de homebrew** (reskins con `base`). Las 669 filas `DMG'24` sin homebrew son huérfanas: el catálogo real es el ETL |
| `items` | nombre, tipo, rareza, personaje_id, npc_portador_id, descripcion, requiere_sintonizacion, campaign_slug | **Instancias** de campaña (lo que alguien posee). NO es el catálogo |
| `personajes` | nombre, clase, raza, jugador, nivel, ac, hp_maximo | PJs del party |
| `lugares` | nombre, tipo, region, ciudad_id | Puntos de interés |
| `monstruos` | nombre, tipo, tamano, cr, es_homebrew, base, … | **Store de homebrew** (`cat:<uuid>` en encuentros). El catálogo real es el ETL (`srd:<fuente>:<nombre>`) |
| `session_plans` | nombre, fecha_sesion, estado, campaign_slug, **bloques** (jsonb), input_data | **Destino final del prep.** `bloques` **array** = plan modular (árbol). Un **objeto** de 9 claves (`bloque_strong_start`…) = plan legacy, de solo lectura en la app: así quedaron los planes de halo hasta junio de 2026. `input_data` va `null` |
| `encuentros` | nombre, descripcion, estrategia ('fm'/'dnd2024'), monsters, party, hazards, companions, user_id | El encuentro que lee el bloque `encuentro`. RLS por rol de campaña |
| `character_folders` | nombre | Las **mesas** (grupos de jugadores). `personajes.folder_id` apunta aquí |
| `campaigns` | slug, cc_disabled_sources | Matriz de fuentes: qué libros/celdas están apagados en la campaña |
| `entity_schemas` | campaign_slug, section, overlay | Qué campos `cf_*` pinta la app por sección. Si no está, no se ve |

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

PJs en `public.personajes` (`campaign_slug='halo'`), mesa **Miércoles** en `character_folders`:
Pithor, Lupin (+ Zif, su compañero de Beast Master), Maverick, Alexios y Doran. La asistencia de
cada sesión se pregunta (Paso 2).

---

## Referencias

- `references/learnings.md` — Memoria del skill (preferencias, reglas aprendidas, historial)
- `references/session-structure.md` — Vocabulario de bloques y convenciones de halo (no es plantilla)
- `../oneshot/references/plantilla-arbol.md` — **Contrato de escritura del árbol** (JSON, texto plano, menciones, verificación)
- `questkeep/docs/lazy-dm-manual.md` — Método: orden, cantidades, secretos (§2.4), qué no preparar
- `questkeep/docs/flee-mortals-manual.md` — Números y piezas del combate cuando el reglamento es FM
- `../dnd-worldbuilder/references/npc.md` — Formato NPC (primera_impresion + notas_roleplay)
- `../dnd-worldbuilder/references/item.md` — Formato item (3 capas: apariencia, sensación, historia)
- `../dnd-worldbuilder/references/combate.md` — Formato combate (framework Encounter Axis + tabla XP XDMG 2024 + capas sensoriales del monstruo-Protein)
- `../dnd-worldbuilder/references/location.md` — Formato lugar (propósito, atmósfera, interactivo, misterio)
- `../dnd-worldbuilder/references/principles.md` — 15 principios narrativos (benchmark Matt Mercer)
