# Learnings — Halo Session Prep

Este archivo es la memoria a largo plazo del skill. Se actualiza en el feedback post-sesión
(Paso 7, aparte, cuando el DM lo pide) y al cerrar una preparación. El skill lo lee al inicio de cada
preparación (Paso 0) para aplicar las preferencias aprendidas.

---

## Preferencias del DM

- **Idioma: español mexicano.** Dirígete al DM en español MX (usa "ustedes", no "vosotros"; nada de conjugaciones ibéricas tipo "cumplís/debéis"). Solo el contenido de reglas de D&D va en inglés verbatim; toda la chrome del prep en español MX. (Corregido por el DM el 24-jun: arranqué en castellano y lo marcó.)
- **Co-diseño sección por sección (preferido):** recorrer las etapas de la sesión una por una y ofrecer **3 opciones** por sección (que difieran en enfoque/tono/consecuencia, no cosméticas). El DM elige/mezcla/ajusta antes de avanzar. No entregar el borrador completo de golpe. Mantener un resumen vivo de lo ya fijado. Si el DM rechaza las 3 y da su propia visión, incorpórala y sigue ofreciendo opciones en la siguiente decisión abierta.
- **Siempre ≥1 combate preparado**, y el DM lo quiere **difícil** (tier High / Hard contra la mesa real). Pieza central temática + apoyos, no enjambre trivial. Mostrar la cuenta.
- **El reglamento del combate se pregunta en cada sesión** (Flee, Mortals! o XP del DMG 2024), sin default. (21-oct-26.) Con FM: criaturas del propio libro, con rol; y comprobar antes que la fuente esté activa en la campaña (la Skeljaskra de Northlands no resolvía porque Northlands está apagado en halo).
- **Describir de verdad a la criatura principal**: primera señal + encuentro con un detalle ancla atado a una acción real de su ficha. («No me describiste al skeljaskra», 22-oct-26.) **El comportamiento en combate, no**: el DM borró los bloques de táctica que lo traían; solo si lo pide.
- **Salidas de escena: dos, limpias**, cada una con su consecuencia escrita para la siguiente sesión. No ramificar por cada combinación posible. (Nadira, 22-oct-26: «solo hay dos salidas».)
- **Todo sitio con nombre en el plan nace como Lugar** y se enlaza, siguiendo `location.md`. («La capitanía del canal era un momento perfecto para crear un Lugar», 22-oct-26.)
- **Ningún término inventado sin definir en el plan** (una línea `GLOSARIO —`). Cazado con «¿y qué es el Diván?» (22-oct-26).
- **El compendio es la PRIMERA fuente de inspiración (la musa):** para cualquier elemento nuevo (locación, gancho, tono/atmósfera de escena, darklord/villano), consulta primero el compendio de flavor en `questkeep/compendium/graphify-out/` (`GRAPH_REPORT.md` → hyperedges/arquetipos + "surprising connections", o por el **CLI sancionado**: `graphify query "<tema>"` / `graphify explain "<nodo>"` / `graphify path "A" "B"`). Toma **un** arquetipo/`theme`/`motif` como semilla y **lima los nombres propios Y los tags de dominio que no encajen** (el grafo es multi-libro, ~3.072 nodos, NO solo Ravenloft — p. ej. Batan trae el tag "Dominion of Shatrekvan" de Ravenloft, que no pega con goliaths: descarta el setting, quédate con el arquetipo) antes de adaptarlo a Halo. Inventar desde cero es el último recurso. El compendio es museo/inspiración; Supabase sigue siendo la fuente de verdad del mundo. (`dnd-worldbuilder` ya lo hace en su Paso 0.5.) **(Confirmado 24-jun-26: el CLI funciona y sirvió de musa para La Esclusa Muerta, Orvo y Aukan.)** **NPCs concretos quedan fuera de este gate** (no dependen de que el CLI esté instalado): van primero por npc-card, JSON plano del compendio (`dnd-worldbuilder/references/npc.md` → «Semilla desde npc-cards»). (Añadido al fijar la rama `claude/npc-cards-como-semilla`, 10-ago-26.)
- **Nada inventado:** los secretos/ganchos se anclan a BD o recap; no reciclar flavor de NPC (`notas_roleplay`) como secreto de trama. Si es nuevo, marcarlo como propuesta a aprobar. (Cazado en 17-jun: el "pulso bajo el piso" era flavor de Rammel, no un secreto.)
- **Sin plotholes:** todo lo que un NPC posee/sabe necesita razón in-world. (17-jun: "¿por qué Rammel tiene el libro de Torben?" → es el archivero de Sleh y descifró los manifiestos.)
- **Decisiones morales:** telegrafiar la ruta alternativa, cada rama con su beat/combate, y la sesión termina en un gancho, no en una escena de cierre; cuidar que el "gris" no colapse a "claramente malo" (avisar al DM si pasa).
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
- **Modelo de campos (rediseño 2026):** las entidades nuevas usan la **ficha rediseñada** por tipo (`dnd-worldbuilder/references/<tipo>.md`): campos `cf_*` en `custom_data`, overlay `entity_schemas`, `subtipo→perfil` (Lugar/Ciudad/Establecimiento), sensibles en `_hidden`, cross-links sembrados al nacer. Aditivo (coexistencia; migración perezosa). Detalle en `claude-skills/specs/001-campos-elementos/`.
- **Tesoros:** del **catálogo 5e VIGENTE (el ETL `data/5e/items.json`, 2062, con commons)**, NO la tabla `items_catalog` (669 filas `DMG'24` huérfanas — era un bug). `items_catalog` es el **store de homebrew** (`es_homebrew`, `base`). Prioridad: match_directo (ETL) > reskin (homebrew con base) > nunca inventar. Un reskin lleva su `base`; `cf_item_base` solo si el overlay de items de la campaña lo declara. Ver `../dnd-worldbuilder/references/catalogos.md`.
- **El plan es un árbol (spec 007, desde el 26-ago-26):** `session_plans.bloques` es un **array** de bloques. El objeto de 9 claves (`bloque_escenas`, `bloque_npcs`…) es el formato legacy y la app lo abre en **solo lectura**: los 6 planes de halo hasta junio quedaron así. El contrato de escritura es `oneshot/references/plantilla-arbol.md` (la skill hermana).
- **Las entidades van antes que el árbol**: los bloques apuntan a filas por id (NPCs, lugares, quest, encuentro). Una sola confirmación con la lista completa.
- **Escribir en los campos que la app muestra**: en halo el overlay de NPCs solo declara `cf_statblock`, y no hay overlay de lugares. NPCs → `primera_impresion` + `notas_roleplay` + `faccion`; lugares → `descripcion` / `descripcion_exterior` / `descripcion_interior`.
- **Monstruos:** del **ETL `data/5e/bestiary.json` (1169)**, NO la tabla `monstruos` (~6 filas, era un bug — es solo store de homebrew). Prioridad: match_directo (ETL) > reskin (homebrew en `monstruos` con `base`, 3 capas) > nunca inventar. Ver `catalogos.md`.
- **Verificación final determinista** (sin subagente): forma `array`, todos los vínculos y menciones del árbol completo resueltos, monstruos con fuente activa. Ver Paso 6 del SKILL.
- **Después de que el DM abre el plan, solo ediciones puntuales con guarda**: él edita y borra en la app. Lo que borró no se recrea sin preguntar.
- **`execute_sql` se cuelga con un `;` dentro de un texto** (o con emojis de 4 bytes): timeout de 60 s y no entra nada. Tras un timeout, `SELECT` antes de reintentar. (Cuatro timeouts el 22-oct-26 hasta dar con la causa.)

### Reglas de consulta y contexto

- **Última sesión:** las queries del Paso 1b van primero, y si el recap más reciente no cuadra con lo que dice el DM, pregúntale. Lo que dice el DM manda sobre lo que devuelve la BD.
- **La mesa, no la lista de PJs:** `character_folders` agrupa a los jugadores (la mesa **Miércoles** de halo). La bitácora del DM trae mensajes de prueba («mensaje de prueba enter»): filtrar por longitud.
- **Flee, Mortals! redondea el nivel hacia abajo** (`fm.ts`): con niveles mezclados (4·4·4·3 → 3) el semáforo de la app sale un escalón arriba. El DM puede elegir calibrar a otro nivel; el plan lo dice junto al encuentro.
- **Dónde viven las notas (Halo):** los recaps de sesión están en la **bitácora del DM** (`public.bitacoras` con `owner_role='dm'` → `public.bitacora_mensajes.content_html`), **no** en `notas_dm` (no existe en `public`). El cuerpo incluye "Notas/Ideas para la siguiente sesión" — leerlas siempre y aplicarlas directo al prep (formación de enemigos, comportamiento de jefes, etc.). Las menciones `@[Nombre](tabla:uuid)` dan el id exacto de cada entidad.
- **Calibrar contenido:** escenas y secretos se calibran por duración (2h → 2-3 escenas; 4h → 4-5). NPCs NO se calibran — el piso de 6 es fijo.
- **Nombre de sesión:** formato `"Sesión DD-MMM-YY"` (con acento en Sesión).
- **Items de PJs:** nunca asumir que un personaje posee un item si no está en `items` con `personaje_id` apuntándolo. "Quiero que X obtenga Y" = quest futura, no hecho actual.
- **Secretos:** siempre crosscheck contra resúmenes de sesiones anteriores. Si los jugadores ya lo descubrieron, buscar algo nuevo.
- **Catálogos: la fuente es el ETL, no las tablas Supabase (corregido en el rediseño 2026).** Las tablas `monstruos` (~6 filas) e `items_catalog` (669 huérfanas) NO son el catálogo — el pool vigente es el ETL (`questkeep/data/5e/bestiary.json` 1169 · `items.json` 2062, con commons). Filtrar por substring (`cr`/`tipo` son strings compuestos). `monstruos`/`items_catalog` son solo store de homebrew (`es_homebrew`, `base`). Ver `../dnd-worldbuilder/references/catalogos.md`. *(Histórico: antes se creía que `monstruos`/`items_catalog` eran el catálogo — de ahí el bug de queries a tablas casi vacías.)*
- **XP budget (XDMG 2024) por PJ:** L3 = 150/225/400, L4 = 250/375/500 (Low/Mod/High). Ej. 5 PJs nivel 4 → High = **2.500** (no 3.750; el ejemplo viejo del SKILL tenía 750/L4, ya corregido). Tabla completa ahora en SKILL.md. El DM a veces pide **deadly** (por encima del High oficial) — válido, **caso por caso**, con la mitigación que el DM defina. **Calibrar solo contra PJs reales** (no contar aliados NPC salvo que el DM lo exprese).

---

## Supabase — Proyecto DnD Halo

**Project ID:** `dwmzchtqjcblupmmklcl`

Todas las operaciones usan `execute_sql` del MCP de Supabase con este project_id.
Las tablas tienen RLS habilitado — las queries se ejecutan como servicio, no como usuario.

---

## Historial de sesiones

- **Sesión 11-mar-26** — Rockwood — Combate vs Gerardo + huida al barco. Prep generado: "Sesion mar-26" (sin fecha fija).
- **Sesión 17-jun-26** — Sleh/Gnomalia. Objetivo: devolver la mercancía a Mivvi y conocer a Torben Brassworth. 3h. Co-diseñada con 3 opciones. Dilema moral (ayudar a Torben = aliado / robar la cittern = enemigo), encargo gris (intimidar a Rammel), 2 NPCs nuevos gated (Brenna víctima de trata, Pim cómplice), 2 combates difíciles (Coloso de Cintas / Autómata Maestro), tesoro = Mac-Fuirmidh Cittern (alta en items_catalog). Guardada en `session_plans` 7ee42176. Feedback aplicado: quitar secreto inventado, tapar plothole del libro, agregar Desenlace, subir dificultad de combate, no etiquetar "facción del cianuro".
- **Sesión 24-jun-26** — Sleh/Gnomalia. **Cierre del arco** Torben/Rammel/Santuario. 3h, co-diseñada 3-opciones. Strong Start: Torben cita a la party a su oficina y entrega un encargo (caja sellada = Brenna oculta), creyéndolos cumplidores (**ironía dramática**: Rammel vive escondido con Alexios). **Brenna reconcebida como niña goliath ~10** (kin del nuevo aliado Aukan) → UPDATE en `npcs`. Estructura A: oficina → transporte (descubren a Brenna) → **combate deadly en La Esclusa Muerta** (locación nueva; las Bodegas del Canal Bajo eran de Mivvi) vs **Orvo Glume** (Mage CR6 reskin coleccionista) + 5 Tough = **2.800 XP**, con válvula de escape ambiental + timer de portal (R1-R4) → Desenlace (llega **Aukan**, gancho a Batan/arco de Pithor). Cittern por **palanca** (manifiestos de Rammel + Brenna testigo), sin doble combate. **Combate único relocalizable** por rama (RUTA 2 reusa el statline de autómatas del 17-jun, no se duplica). 2 NPCs nuevos (Orvo, Aukan). Guardada en `session_plans` **6445c0e2**. graphify usado de musa vía CLI. Higiene BD: limpiado `tipo_npc` basura de Capitán Fizwick. Updates al skill aplicados (queries de catálogo, tabla XP, wiring graphify, español MX).
- **Sesión 21-oct-26** — Sleh → camino a Batan. **Inicio del arco del rescate de Brenna** (saga política). **Primer plan modular de halo** (`session_plans` **e133aa6a**), armado como prueba de la actualización de esta skill. Mesa Miércoles sin Doran (Pithor 4, Lupin 4 + Zif, Maverick 4, Alexios 3). Espina: atracadero vacío → archivo de Rammel (Alexios cobra su amistad; la **Capitanía del Canal** como lugar nuevo, con el lacre índigo del Jardín) → camino (Pithor y la ley de las marcas) → **cacería tributo** con Flee, Mortals! a nivel 4 (Shieldscale Drangolin como skeljaskra + **Griffon oculto** que baja en la ronda 2; para eso se construyó questkeep #600) → gancho con la caravana de Khaz-Alun. Mundo nuevo: **Orvo** es coleccionista de especies de Khaz-Alcity al servicio del Sultán (el **Jardín de las Mil Especies**); **el Diván** es el consejo comercial de Khaz-Alun y no se lleva con la corte; los clanes **Cumbre Rota** (Aukan) y **Lanza de Ceniza** (Tavra) son **rivales, no enemigos**, y llevan la cuenta en la **Piedra de las Cuentas** (van empatados). NPCs nuevos: **Tavra**, **Nadira bint Harith**. Quest nueva: **El rescate de Brenna**. Pendiente de higiene: duplicados de Aukan y Orvo en `npcs` (referencia siempre el id que ya tiene vínculos en `npcs_quests`), y 6 «Plan de prueba E2E» vacíos en `session_plans`.
