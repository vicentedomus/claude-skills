# Learnings — Halo Post-Session

Este archivo es la memoria a largo plazo del skill. Se actualiza con el feedback
del DM después de cada uso. El skill lo lee al inicio (Paso 0) para aplicar
las preferencias aprendidas.

---

## Preferencias del DM

<!-- Preferencias sobre cómo presentar las propuestas, nivel de detalle, etc. -->

---

## Qué funcionó bien

- **Sesión 25-mar-26:** Formato de tabla única para propuestas fue fácil y ágil de revisar. El DM aprobó todo en un solo mensaje.

---

## Qué mejorar

<!-- Feedback acumulado -->

---

## Reglas aprendidas

- **Identificar sesión:** Siempre preguntar al DM cuál fue la sesión antes de buscar en la BD. No asumir que la más reciente es la correcta.
- **Dónde viven las notas (Halo):** el recap de cada sesión está en la **bitácora del DM** (`public.bitacoras` con `owner_role='dm'` → `public.bitacora_mensajes.content_html`), **no** en `notas_dm` (esa tabla no existe en `public`; solo en otras campañas como `tierras_perdidas`). Una sesión puede ocupar varios mensajes, y `created_at` puede no coincidir con la fecha del título `Sesión DD-MMM-YY`.
- **Menciones embebidas:** los recaps usan `@[Nombre](tabla:uuid)` — usar esos `uuid` directamente para el crosscheck en vez de buscar por nombre. **Pero ojo con duplicados:** el `uuid` puede caer en un registro archivado/vacío mientras el bueno es otro activo (pasó con Rammel `408f81d9` vs `a2007cab` y Dabblewick `b2793b34` vs `0e25561b`). Si el id apunta a un registro `archived` o sin datos, reconciliar por nombre para hallar el activo.
- **Leer el plan de sesión (`session_plans`):** el contenido vive en la columna **`bloques`** (jsonb) y en **`input_data`** (jsonb), **no** en las columnas escalares `bloque_*`/`input_*` del mismo nombre (esas son legacy y vienen vacías/null). Consultar `bloques->'bloque_escenas'`, `bloques->>'bloque_strong_start'`, etc. Nunca declarar un plan "vacío" sin mirar `bloques`. Las entidades del plan con `flag:"nuevo"` (Brenna, Pim) ya fueron creadas en `conocido=false`; el crosscheck decide cuáles alcanzó el party.
- **Notas informales:** el cuerpo del recap mezcla narrativa con recordatorios personales del DM (ej: "desarrollar un poco a Doran"). Interpretar ambas cosas.
- **Confirmación obligatoria:** Nunca ejecutar un UPDATE sin confirmación explícita del DM.

---

## Supabase — Proyecto DnD Halo

**Project ID:** `dwmzchtqjcblupmmklcl`

Todas las operaciones usan `execute_sql` del MCP de Supabase con este project_id.

---

## Historial de ejecuciones

- **Sesión 25-mar-26** — 4 updates ejecutados (Fizwick conocido, Linna conocida+muerta, Valon aliado, quest en pausa). Sleh y GnomeDepot ya estaban al día. Feedback: "todo bien y fácil".
- **Sesión 08-abr-26** (arco Sleh/Mivvi) — recap leído desde la bitácora del DM (ya no `notas_dm`). 2 updates de visibilidad ejecutados (Dabblewick conocido, Bodegas del Canal Bajo conocido). El DM declinó crear la quest "El Encargo de Mivvi" y sus vínculos. Pendientes (recordatorios): cittern de Mac Fuirmid, desarrollar a Torben, definir contenido de "la mercancía".
- **Sesión 17-jun-26** (arco Torben/Rammel/Santuario) — 3 updates ejecutados: Santuario del Pulso Eterno `conocido→true`, Rammel (`a2007cab`) `conocido→true` y `rol→Aliado` (el party lo secuestró para protegerlo de Torben). El party divergió del plan: tomó una tercera vía (proteger a Rammel) en vez de las ramas AYUDAR/ROBAR, no alcanzó a Brenna/Pim (siguen ocultos) y no obtuvo la cittern (Torben la difirió a "trato futuro"). El DM volvió a declinar crear quest del arco. Lecciones aplicadas a la skill: (1) leí mal el plan al consultar columnas escalares en vez de `bloques` jsonb; (2) el `uuid` de Rammel en el recap apuntaba a un dupe archivado vacío. Recordatorios: importar a Alexios (PC de Tino) desde D&D Beyond, hilo de la cittern, trata de blancas (Brenna/cautivos sin rescatar), limpiar dupes archivados de Rammel/Dabblewick.
- **Nota QuestKeep:** `personajes` no tiene columna de XP — la progresión es por `nivel` (milestone). Ni `ddb_data.currentXp` ni `sheet_data` traen XP. Si el DM quisiera XP, requiere cambio de schema (PR aparte en QuestKeep).
