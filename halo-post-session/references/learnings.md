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
- **Menciones embebidas:** los recaps usan `@[Nombre](tabla:uuid)` — usar esos `uuid` directamente para el crosscheck en vez de buscar por nombre.
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
