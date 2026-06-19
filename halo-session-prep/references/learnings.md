# Learnings — Halo Session Prep

Este archivo es la memoria a largo plazo del skill. Se actualiza automáticamente
después de cada sesión con el feedback del DM. El skill lo lee al inicio de cada
preparación (Paso 0) para aplicar las preferencias aprendidas.

---

## Preferencias del DM

- **Co-diseño sección por sección (preferido):** recorrer las etapas de la sesión una por una y ofrecer **3 opciones** por sección (que difieran en enfoque/tono/consecuencia, no cosméticas). El DM elige/mezcla/ajusta antes de avanzar. No entregar el borrador completo de golpe. Mantener un resumen vivo de lo ya fijado. Si el DM rechaza las 3 y da su propia visión, incorpórala y sigue ofreciendo opciones en la siguiente decisión abierta.
- **Siempre ≥1 combate preparado**, y el DM lo quiere **difícil** (tier High contra el party real). Pieza central temática + apoyos, no enjambre trivial. Mostrar la cuenta de XP.
- **El compendio es la PRIMERA fuente de inspiración (la musa):** para cualquier elemento nuevo (NPC, locación, gancho, tono/atmósfera de escena, darklord/villano), consulta primero el compendio de flavor en `questkeep/compendium/graphify-out/` (`GRAPH_REPORT.md` → hyperedges/arquetipos + "surprising connections", o `/graphify query "<tema>"`). Toma **un** arquetipo/`theme`/`motif` como semilla y **lima los nombres propios** antes de adaptarlo a Halo. Inventar desde cero es el último recurso. El compendio es museo/inspiración; Supabase sigue siendo la fuente de verdad del mundo. (`dnd-worldbuilder` ya lo hace en su Paso 0.5.)
- **Nada inventado:** los secretos/ganchos se anclan a BD o recap; no reciclar flavor de NPC (`notas_roleplay`) como secreto de trama. Si es nuevo, marcarlo como propuesta a aprobar. (Cazado en 17-jun: el "pulso bajo el piso" era flavor de Rammel, no un secreto.)
- **Sin plotholes:** todo lo que un NPC posee/sabe necesita razón in-world. (17-jun: "¿por qué Rammel tiene el libro de Torben?" → es el archivero de Sleh y descifró los manifiestos.)
- **Decisiones morales:** telegrafiar la ruta alternativa, cada rama con su beat/combate, cerrar con escena de Desenlace; cuidar que el "gris" no colapse a "claramente malo" (avisar al DM si pasa).
- **Verbatim desde la fuente:** contenido D&D oficial se extrae de 5etools/fuente, nunca de memoria; si falta en `items_catalog`, darlo de alta primero.
- **Higiene de datos:** ignorar PJs de prueba/animales al contar el party; reportar duplicados (no borrar sin permiso).
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

- **NPCs por sesión:** piso de **6 NPCs** = **4 existentes + 2 nuevos**. El mundo crece cada sesión. Los **2 nuevos** se anclan a un arquetipo del **compendio** (musa) antes de inventar — `dnd-worldbuilder` lo hace en su Paso 0.5.
- **Transición `nuevo → existente`:** ocurre en el Paso 4, al confirmar con el DM. INSERT en `npcs` con `conocido_jugadores=false`, `campaign_slug='halo'`. El flag `nuevo` queda como snapshot histórico del session_plan.
- **Relación con la sesión:** todo NPC y toda locación deben explicar su relación con la sesión (qué rol cumple, por qué aparece). No vale dejarlo vacío.
- **Tesoros:** SOLO items reales del catálogo **`items_catalog`** (global, ≈668 DMG'24, sin campaign_slug). `items` son las instancias de campaña, NO el catálogo. Prioridad: match directo > reskin (solo si nada encaja) > nunca inventar. Si la trama exige un item oficial fuera del catálogo (p. ej. 2014), darlo de alta primero en `items_catalog` con texto verbatim de la fuente.
- **Contrato de bloques (render del planner):** secretos y pivote van ANIDADOS dentro de cada `bloque_escenas[i]` (`secretos[]`, `es_pivote`/`pivote`); `bloque_secretos`/`bloque_pivote` deprecados. Cada monstruo lleva `escena_idx` para ligarlo a su escena de combate (la pestaña Combate muestra Ejes + statblock base vía `monstruo_id`→`monstruos`).
- **Monstruos:** SOLO del catálogo `monstruos` (5e oficial, sin campaign_slug — compartido). Prioridad: match directo > reskin narrativo de 3 capas. Nunca inventar stat blocks.
- **Destino del prep:** tabla `public.session_plans`. Todos los bloques van **anidados dentro de la columna `bloques` (jsonb)** — la UI (`preparador.js`) lee de ahí. Las columnas `bloque_*` sueltas son legacy y la UI las ignora (un plan escrito ahí sale vacío). Ver Paso 4b del SKILL.
- **Auditoría final:** antes de cerrar la skill, un subagente auditor valida reglas + cohesión + calidad. Emite reporte al DM. Si hay issues, el DM decide (UPDATE o dejar como está).

### Reglas de consulta y contexto

- **Última sesión:** preguntar primero al DM cuál fue la última sesión antes de hacer queries. Priorizar siempre lo que dice el DM sobre lo que devuelve la BD.
- **Dónde viven las notas (Halo):** los recaps de sesión están en la **bitácora del DM** (`public.bitacoras` con `owner_role='dm'` → `public.bitacora_mensajes.content_html`), **no** en `notas_dm` (no existe en `public`). El cuerpo incluye "Notas/Ideas para la siguiente sesión" — leerlas siempre y aplicarlas directo al prep (formación de enemigos, comportamiento de jefes, etc.). Las menciones `@[Nombre](tabla:uuid)` dan el id exacto de cada entidad.
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
- **Sesión 17-jun-26** — Sleh/Gnomalia. Objetivo: devolver la mercancía a Mivvi y conocer a Torben Brassworth. 3h. Co-diseñada con 3 opciones. Dilema moral (ayudar a Torben = aliado / robar la cittern = enemigo), encargo gris (intimidar a Rammel), 2 NPCs nuevos gated (Brenna víctima de trata, Pim cómplice), 2 combates difíciles (Coloso de Cintas / Autómata Maestro), tesoro = Mac-Fuirmidh Cittern (alta en items_catalog). Guardada en `session_plans` 7ee42176. Feedback aplicado: quitar secreto inventado, tapar plothole del libro, agregar Desenlace, subir dificultad de combate, no etiquetar "facción del cianuro".
