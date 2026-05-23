# Learnings — Halo Session Prep

Este archivo es la memoria a largo plazo del skill. Se actualiza automáticamente
después de cada sesión con el feedback del DM. El skill lo lee al inicio de cada
preparación (Paso 0) para aplicar las preferencias aprendidas.

---

## Preferencias del DM

- Sucesos narrativos en el barco/viaje (sin combate obligatorio) — el DM elige cuáles usar según el ritmo
- Tabla de NPCs con "qué quieren" + tono conciso — no monólogos
- Líneas de diálogo sugeridas: breves, entre comillas, en el cuerpo de la escena (no como sección aparte)

---

## Qué funcionó bien

<!-- Por sesión: qué secciones fueron más útiles -->

---

## Qué mejorar

<!-- Feedback acumulado post-sesión -->

---

## Reglas aprendidas

### Reglas estructurales del prep

- **NPCs por sesión:** piso de **6 NPCs** = **4 existentes + 2 nuevos**. El mundo crece cada sesión.
- **Transición `nuevo → existente`:** ocurre en el Paso 4, al confirmar con el DM. INSERT en `npcs` con `conocido_jugadores=false`, `campaign_slug='halo'`. El flag `nuevo` queda como snapshot histórico del session_plan.
- **Relación con la sesión:** todo NPC y toda locación deben explicar su relación con la sesión (qué rol cumple, por qué aparece). No vale dejarlo vacío.
- **Tesoros:** SOLO items reales de la tabla `items`. Prioridad: match directo > reskin (solo si nada encaja). Nunca inventar. El reskin mantiene stats/efectos del item base.
- **Monstruos:** SOLO del catálogo `monstruos` (5e oficial, sin campaign_slug — compartido). Prioridad: match directo > reskin narrativo de 3 capas. Nunca inventar stat blocks.
- **Destino del prep:** tabla `session_plans` con columnas separadas por bloque (`bloque_strong_start` text + `bloque_escenas`, `bloque_secretos`, `bloque_npcs`, `bloque_locaciones`, `bloque_tesoros`, `bloque_monstruos` todas jsonb).
- **Auditoría final:** antes de cerrar la skill, un subagente auditor valida reglas + cohesión + calidad. Emite reporte al DM. Si hay issues, el DM decide (UPDATE o dejar como está).

### Reglas de consulta y contexto

- **Última sesión:** preguntar primero al DM cuál fue la última sesión antes de hacer queries. Priorizar siempre lo que dice el DM sobre lo que devuelve la BD.
- **Notas del DM:** las sesiones incluyen "Notas para planear siguiente sesión" dentro de `contenido_html` — leerlas siempre y aplicarlas directamente al prep (formación de enemigos, comportamiento de jefes, etc.).
- **Calibrar contenido:** escenas y secretos se calibran por duración (2h → 2-3 escenas; 4h → 4-5). NPCs NO se calibran — el piso de 6 es fijo.
- **Nombre de sesión:** formato `"Sesión DD-MMM-YY"` (con acento en Sesión).
- **Items de PJs:** nunca asumir que un personaje posee un item si no está en `items` con `personaje_id` apuntándolo. "Quiero que X obtenga Y" = quest futura, no hecho actual.
- **Secretos:** siempre crosscheck contra resúmenes de sesiones anteriores. Si los jugadores ya lo descubrieron, buscar algo nuevo.

---

## Supabase — Proyecto DnD Halo

**Project ID:** `dwmzchtqjcblupmmklcl`

Todas las operaciones usan `execute_sql` del MCP de Supabase con este project_id.
Las tablas tienen RLS habilitado — las queries se ejecutan como servicio, no como usuario.

---

## Historial de sesiones

- **Sesión 11-mar-26** — Rockwood — Combate vs Gerardo + huida al barco. Prep generado: "Sesion mar-26" (sin fecha fija).
