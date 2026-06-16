---
name: halo-post-session
description: >
  Actualización de bases de datos de la campaña D&D "Halo" después de una sesión jugada.
  Lee las notas del DM en Supabase, detecta qué cambió en el mundo (NPCs conocidos,
  quests avanzadas, ciudades visitadas, items obtenidos) y propone actualizaciones
  una por una con confirmación del DM.

  Usa esta skill cuando Vicente mencione actualizar registros después de una sesión,
  poner al día la campaña, sincronizar lo que pasó en la partida, o cualquier variación
  de "ya jugamos, hay que actualizar las BDs". También si dice "post-sesión", "update
  después de la sesión", "pon al día los datos", o simplemente pega/describe lo que
  pasó en una sesión reciente. En caso de duda, actívala.
compatibility:
  tools: [Supabase MCP]
---

# Halo — Post-Session Skill

Skill para poner al día las bases de datos de la campaña **Halo** después de una sesión jugada.
El DM no debería tener que ir registro por registro actualizando manualmente — esta skill
detecta qué cambió según las notas y lo ejecuta con confirmación.

Todas las operaciones usan `execute_sql` sobre el proyecto Supabase `dwmzchtqjcblupmmklcl`.

---

## Paso 0: Leer learnings

Antes de cualquier otra acción, lee `references/learnings.md` para aplicar preferencias
y reglas aprendidas de ejecuciones anteriores.

---

## Paso 1 — Identificar la sesión

Pregunta al DM cuál fue la sesión que se jugó. No asumir — puede haber varias notas
recientes y el DM sabe exactamente cuál se jugó.

Una vez que el DM indique la sesión, busca el recap en la **bitácora del DM**. Las notas
post-sesión de Halo ya **no viven en `notas_dm`** (esa tabla solo existe para otras
campañas en su propio schema, p. ej. `tierras_perdidas`). Para Halo, el DM escribe el
recap como mensajes en su bitácora: `public.bitacoras` con `owner_role='dm'` →
`public.bitacora_mensajes`.

```sql
SELECT m.id,
       m.created_at::date AS fecha,
       regexp_replace(m.content_html, '<[^>]+>', ' ', 'g') AS texto
FROM public.bitacora_mensajes m
JOIN public.bitacoras b ON b.id = m.bitacora_id
WHERE b.campaign_slug = 'halo'
  AND b.owner_role = 'dm'
  AND m.deleted_at IS NULL
ORDER BY m.created_at DESC
LIMIT 10;
```

Cada mensaje del DM es el recap de una sesión. El cuerpo (`content_html`) suele abrir con
el título `Sesión DD-MMM-YY`, sigue con la narrativa de lo que ocurrió y cierra con notas
sueltas tipo "Ideas/Notas para la siguiente sesión". Son notas informales que mezclan
narrativa con recordatorios personales del DM — hay que interpretar ambas cosas.

Notas importantes al leer el recap:
- **Una sesión puede ocupar varios mensajes** (p. ej. el arco 08-abr-26 quedó en 3
  mensajes). Agrúpalos por arco narrativo / título, no asumas un mensaje = una sesión.
- **`created_at` puede no coincidir** con la fecha del título `Sesión DD-MMM-YY` (a veces
  el DM captura el recap días después). Confía en el título y en lo que indique el DM, no
  en `created_at`.
- El recap usa **menciones embebidas** `@[Nombre](tabla:uuid)` (npcs, lugares,
  establecimientos, quests, personajes). Esos `uuid` son oro para el crosscheck: dan el id
  exacto de cada entidad tocada sin tener que buscarla por nombre.
- El prep original de la sesión vive en `public.session_plans` (`campaign_slug='halo'`).
  Léelo para contrastar lo planeado vs. lo que realmente pasó.

---

## Paso 2 — Crosscheck contra las BDs

Con las notas de la sesión en mano, consulta el estado actual de las tablas relevantes
para detectar qué necesita actualizarse. Ejecuta estas queries en paralelo:

**NPCs** — ¿alguno fue conocido por primera vez? ¿cambió su estado o relación con el party?
```sql
SELECT n.id, n.nombre, n.conocido_jugadores, n.estado, n.ciudad_id, c.nombre as ciudad
FROM npcs n
LEFT JOIN ciudades c ON n.ciudad_id = c.id
WHERE NOT n.archived;
```

**Quests** — ¿avanzó alguna quest? ¿se completó? ¿surgió una nueva?
```sql
SELECT q.id, q.nombre, q.estado, q.resumen
FROM quests q
WHERE NOT q.archived;
```

**Ciudades** — ¿visitaron una ciudad nueva? ¿descubrieron algo sobre una ciudad?
```sql
SELECT id, nombre, conocida_jugadores
FROM ciudades
WHERE NOT archived;
```

**Establecimientos** — ¿entraron a un establecimiento nuevo?
```sql
SELECT e.id, e.nombre, e.tipo, e.conocido_jugadores, e.ciudad_id, c.nombre as ciudad
FROM establecimientos e
LEFT JOIN ciudades c ON e.ciudad_id = c.id
WHERE NOT e.archived;
```

**Items** — ¿el party consiguió o perdió algún item?
```sql
SELECT id, nombre, conocido_jugadores, personaje_id
FROM items
WHERE NOT archived;
```

**Lugares** — ¿descubrieron un lugar nuevo?
```sql
SELECT l.id, l.nombre, l.conocido_jugadores, l.ciudad_id, c.nombre as ciudad
FROM lugares l
LEFT JOIN ciudades c ON l.ciudad_id = c.id
WHERE NOT l.archived;
```

---

## Paso 3 — Detectar cambios

Contrasta las notas de la sesión contra el estado actual de las BDs. Busca discrepancias
en estas categorías:

### Visibilidad
- NPCs mencionados en las notas que tienen `conocido_jugadores = false`
- Ciudades visitadas que tienen `conocida_jugadores = false`
- Establecimientos visitados que tienen `conocido_jugadores = false`
- Lugares descubiertos que tienen `conocido_jugadores = false`

### Estado
- NPCs cuyo estado cambió (ej: un NPC que murió, que se alió al party, que los traicionó)
- Quests que avanzaron, se completaron, o quedaron en pausa

### Relaciones nuevas
- NPCs que deberían vincularse a quests (via `npcs_quests`)
- Quests que deberían vincularse a ciudades o lugares nuevos

### Registros nuevos
- NPCs nuevos que aparecieron y no existen en la BD
- Items que el party obtuvo
- Lugares o establecimientos nuevos que se mencionan

### Notas del DM
- Recordatorios sueltos en las notas (ej: "desarrollar un poco a Doran") que no son
  actualizaciones de BD sino anotaciones para el futuro. Presentarlas al DM al final
  como recordatorio, sin intentar convertirlas en updates.

---

## Paso 4 — Proponer actualizaciones en tabla

Presenta **todos** los cambios detectados en una sola tabla para que el DM pueda
revisar y aprobar/rechazar de un vistazo. Las notas de una sesión no capturan todos
los matices — la tabla le permite al DM evaluar el conjunto completo y decidir rápido.

Ordenar por categoría: Visibilidad → Estado → Relación → Nuevo registro.

**Formato de la tabla:**

| # | Categoría | Registro | Cambio propuesto | Razón (de las notas) |
|---|-----------|----------|------------------|----------------------|
| 1 | Visibilidad | NPC Fizwick | conocido → true | "comandado por el Capitán Fizwick" |
| 2 | Visibilidad | Ciudad Sleh | conocida → true | "llegan a Sleh, en Gnomalia" |
| 3 | Estado | NPC Valon | estado → Aliado | "Valon ayuda a los aventureros a escapar" |
| 4 | Nuevo | NPC Mivvi | Crear registro | "llama la atención de Mivvi" |

Después de la tabla, preguntar: **"¿Cuáles apruebas? Puedes decir 'todos', 'todos menos X', o indicar ajustes."**

Si el DM pide ajustes a algún registro específico (ej: "el 3 ponlo como Neutral, no Aliado"),
aplicar el ajuste antes de ejecutar.

Para registros nuevos (NPCs, items, etc.), si el DM aprueba la creación, preguntar
si quiere agregar detalles adicionales antes de insertar (ej: raza, rol, ciudad).

---

## Paso 5 — Ejecutar y resumir

Ejecuta solo los cambios aprobados por el DM. Después de ejecutar todos, presenta
la misma tabla con el resultado de cada uno:

| # | Registro | Cambio | Resultado |
|---|----------|--------|-----------|
| 1 | NPC Fizwick | conocido → true | ✅ Hecho |
| 2 | Ciudad Sleh | conocida → true | ✅ Hecho |
| 3 | NPC Valon | estado → Aliado | ❌ DM declinó |
| 4 | NPC Mivvi | Crear registro | ✅ Creado |

Si hubo recordatorios del DM en las notas (cosas que no son updates de BD),
listarlos al final como recordatorio:

> **Recordatorios del DM:**
> - "Relacionar el final al Mac-Fuirmidh Cittern"
> - "Desarrollar un poco a Doran"

---

## Estructura de datos en Supabase

**Proyecto:** `dwmzchtqjcblupmmklcl` · **Schema:** `public` · **Campaign slug:** `halo`

> Los datos de Halo viven en el schema `public` filtrando por `campaign_slug='halo'`. Otras
> campañas viven en schemas separados (p. ej. `tierras_perdidas`) y esas sí tienen su propia
> tabla `notas_dm`. Para Halo, el recap de cada sesión vive en la **bitácora del DM**, no en
> `notas_dm` (que no existe en `public`).

### Tablas principales
| Tabla | Columnas clave | Notas |
|-------|---------------|-------|
| `bitacoras` | campaign_slug, owner_role ('dm'/'player'), personaje_id | La bitácora del DM (`owner_role='dm'`) guarda los recaps de sesión |
| `bitacora_mensajes` | bitacora_id, author_role, content_html, created_at, deleted_at | Cada recap del DM es un mensaje (`content_html`); filtrar `deleted_at IS NULL` |
| `quests` | nombre, estado (Activa/Completada/En pausa), resumen, contenido_html | Misiones |
| `npcs` | nombre, raza, rol, estado, tipo_npc, ciudad_id, establecimiento_id, primera_impresion, notas_roleplay, edad, conocido_jugadores | Personajes no jugadores |
| `ciudades` | nombre, descripcion, lider, poblacion, estado, conocida_jugadores | Ciudades del mapa |
| `establecimientos` | nombre, tipo, ciudad_id, dueno_id, descripcion_exterior, descripcion_interior, conocido_jugadores | Tiendas, tabernas, etc. |
| `items` | nombre, tipo, rareza, personaje_id, npc_portador_id, contenido_html, conocido_jugadores | Items mágicos |
| `personajes` | nombre, clase, raza, jugador, nivel, ac, hp_maximo | PJs del party |
| `lugares` | nombre, tipo, region, ciudad_id, conocido_jugadores | Puntos de interés |

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

### Visibilidad
- Ciudades: `conocida_jugadores` (boolean)
- NPCs, Establecimientos, Lugares, Items: `conocido_jugadores` (boolean)
- Soft delete: `archived = true` (no borrar registros, marcarlos como archivados)

### Jugadores del party
PJs en `public.personajes` (`campaign_slug='halo'`): Pithor, Maverick, Lupin, Doran (+ Zif
como compañero). La asistencia por sesión no se registra en una columna dedicada; si hace
falta, se infiere del recap del DM en la bitácora.

---

## Referencias

- `references/learnings.md` — Memoria del skill (preferencias, reglas aprendidas)
