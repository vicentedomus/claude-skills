---
name: tareas-deck
description: >-
  Genera la presentación (deck HTML autocontenido + PDF) del estado y los focos de
  atraso de las TAREAS DE OBRA de un desarrollo de Domus (Adara por defecto) para la
  junta de seguimiento, leyendo datos en vivo de Supabase. Úsala siempre que el usuario
  pida la presentación o el deck de tareas/avance de obra para una junta, el reporte de
  seguimiento de un desarrollo, o actualizar/regenerar esa presentación con datos
  frescos — aunque no diga "deck" explícitamente. Frases típicas: "arma el deck de
  tareas de Adara", "presentación de obra para la junta", "cómo vamos con las tareas de
  Adara", "seguimiento de Adara para la junta de mañana", "el reporte de avance de obra
  con Jorge e Israel", "focos de atraso de la obra". Pensada para Adara hoy, pero su
  estructura (datos → agregados → plantilla de deck → verificación → guardado/PDF) es
  reutilizable para cualquier desarrollo cambiando el proyecto.
---

# Deck de tareas de obra (junta de seguimiento)

Esta skill convierte en un proceso repetible el seguimiento de las tareas de obra de un
desarrollo: leer las tareas activas de Supabase, calcular los mismos cortes con foco en
los **atrasos**, y producir un deck HTML limpio (16:9, autocontenido, adaptable a
cualquier pantalla) + un PDF, guardado bajo la convención `juntas/`.

**Audiencia del deck:** gerentes de obra (Jorge Aguilar, Israel Cárdenas) y dirección.
Tono claro y accionable, números grandes, una idea por slide, en español.

**Ángulo por defecto: focos de atraso** — no es un tablero de todo, es "dónde se atora y
qué destrabamos primero". El **criterio principal de atraso** son las tareas con su
**reporte de avance vencido** (`fecha_siguiente_actualizacion < current_date`), no la
fecha de fin programada (que queda como criterio secundario). Se construyó primero
para **Adara** (`proyecto_id` `38467911-110f-4bb9-818c-a4cc9161f4f0`).

**Regla de alcance (no negociable):** las tareas **archivadas (`archivada = true`) se
excluyen de toda estadística**. Todas las queries de `references/queries.md` ya filtran
`not archivada`; si agregas una nueva, replícalo. La cuenta de archivadas no se muestra
en el deck (no es señal accionable).

**Regla de tareas padre (también fija):** una tarea con subtareas (que aparece en
`parent_tarea_id` de otra) **no recibe reportes propios** — los reportes se cargan en sus
subtareas. Por eso **excluye padres de toda métrica de seguimiento**: reporte vencido
(slides 2/3/5) y frescura (slide 7). **No** los excluyas de las métricas de carga (por
responsable, por área, conteos de activas/en proceso/sin iniciar) ni de "vencidas por
fecha" / "sin fecha de cierre". Ver `references/queries.md` para el CTE reutilizable.

**Filosofía:** la estructura es **fija pero editable** — los 9 slides de abajo son la base
probada; en cada junta puedes agregar o quitar slides si el usuario lo pide, pero conserva
la narrativa (resumen → estado de no-completas → responsable → 3 focos → área → plan) y el
sistema visual.

## Recursos incluidos

- `assets/template.html` — el deck probado y funcionando (corrida Adara · 27-may-2026).
  **Es el punto de partida: cópialo y refresca los datos**, no lo reconstruyas desde cero.
  Ya trae el sistema visual, el escalado adaptable y la navegación (botones + swipe +
  teclado). Comparte el sistema visual con `garantias-deck`.
- `references/queries.md` — el modelo de datos, la escala 0–1 del avance (¡ojo!), la
  definición de "activas" y **todas las consultas SQL canónicas** parametrizadas por
  `:PID` (proyecto). Ejecutar con la tool MCP `execute_sql`, proyecto `ifqwrtheakkvgezewxqx`.
  Léelo siempre antes de consultar.
- `scripts/export_pdf.mjs` — exporta el deck HTML a PDF (un slide = una página horizontal).
  Requiere `@playwright/test` (instala con `npm install` si el contenedor está limpio).
- `scripts/verify.mjs` — recorre todos los slides, captura un PNG de cada uno, detecta
  overflow de contenido y reporta errores de consola/pageerror; además captura el escalado
  en móvil horizontal y vertical. Úsalo en el paso 4.

## Proceso (sigue estos pasos en orden)

Crea una lista de tareas con estos pasos para no saltarte ninguno.

### 1. Confirmar alcance y desarrollo

El corte es **hoy** (`current_date`). Confirma brevemente: qué desarrollo (Adara por
defecto), si solo activas (default) o también completadas/archivadas, y si hay focos extra
para esta junta. Resuelve el `proyecto_id` con la tabla `proyectos`.

### 2. Sacar los datos de Supabase

Lee `references/queries.md` y ejecuta, con `execute_sql`, sustituyendo `:PID`:
1. El **sanity check** (paso 0): confirma que `porcentaje_avance` sigue siendo **0–1**.
   Si aparece algo fuera de escala, detente y avisa.
2. **Resumen/KPIs + frescura** (consulta 1).
3. **Por responsable** (consulta 2) — recuerda que los conteos se traslapan.
4. Los **tres focos**: vencidas + dependencias (3), seguimiento vencido (4), sin fecha de
   cierre (5).
5. **Por área** (consulta 6).

Trabaja con los números **exactamente** como vienen de la BD. Lee las **observaciones** de
las vencidas: el bloqueo real suele estar ahí (p. ej. "sin luz no se puede recibir el
riego") y arma las **cadenas de dependencia** que se destraban juntas.

### 3. Construir el deck (usa la skill huashu-design + la plantilla)

Esta skill se apoya en **huashu-design** para el render. Camino rápido y fiable:

1. Copia `assets/template.html` a la ubicación destino (ver paso 5).
2. **Refresca los datos** en cada slide con los resultados frescos (ver "Estructura" abajo).
   Recalcula anchos/alturas con las fórmulas de `references/queries.md` (sección final).
3. Mapea el contador de slides (`x / N`) y los pies de página si cambia el número de slides.

**Semántica de color (no la cambies):**
- **teal** = completa (100%) · **ámbar** = en proceso (1–99%) · **rojo** = sin iniciar (0%)
  / vencida / atraso.
- En el slide por área, el relleno va al **avance %**: rojo = bajo, ámbar = intermedio,
  teal = alto.

### Popups interactivos (HTML, no aparecen en el PDF)

El template incluye un modal y un objeto global `TASKS` con todas las listas necesarias.
Cada elemento clickable lleva `data-popup="<key>"` + `data-title` + `data-sub`. Las
**keys** que ya están cableadas en la plantilla:

- Slide 4: `jorge_comp`, `jorge_proc`, `jorge_sin`, `eduardo_comp`, `eduardo_proc`,
  `eduardo_sin`, `israel_comp`, `israel_proc`, `israel_sin` — alimentados por la
  **consulta 7** (responsable × estado).
- Slide 5: `cerrar7` (las N tareas al 100% con reporte vencido) — **consulta 8**.
- Slide 7: `fresca_7d`, `fresca_d30`, `fresca_d30plus`, `fresca_nunca` — **consulta 9**.

Cuando refresques el deck con datos nuevos, **regenera el objeto `TASKS`** (es una
asignación literal JSON dentro de un `<script>`). Mantén las keys; cambia solo los arrays.
Asegúrate de que los conteos del popup coincidan con los números visibles en cada barra/
segmento (el script de verificación lo comprueba simulando clicks).

### Estructura base de slides (fija + editable)

1. Portada
2. Resumen ejecutivo (KPIs) — activas, % avance, **pendientes con reporte vencido** (foco
   principal), sin iniciar, sin fecha de cierre. No incluyas archivadas en los KPIs.
3. **Las que requieren atención** (en proceso + sin iniciar) — las completas no aparecen
   aquí; pasan a higiene de cierre. Contexto: reporte vencido, fin programado vencido,
   sin fecha de cierre.
4. Por responsable (barras apiladas, **clickables**; resaltar quién concentra
   sin-iniciar). Cada segmento abre un popup con la lista de tareas de ese responsable +
   ese estado.
5. **Foco 1 · Reportes vencidos** (separar "pendientes reales" del "+N al 100% por
   cerrar"; el +N debe ser clickable y abrir su popup). Lista agrupada por cluster (p.ej.
   Pórtico, Gimnasio, Área verde) con badge de responsable en cada fila.
6. **Foco 2 · Vencidas por fecha** + **cadena de dependencia** que las destraba.
7. **Foco 3 · Sin compromiso + frescura** (sin fecha de cierre + buckets de última
   actualización; los 4 buckets de frescura son **clickables** y abren popup con sus
   tareas).
8. Por área (resaltar la más atrasada; señalar cuántas no tienen área asignada).
9. Plan de trabajo (acciones priorizadas, con dueño).

Agrega/quita slides solo si el usuario lo pide. Mantén el plan de trabajo al final.

### 4. Verificar antes de entregar

Con Playwright (`@playwright/test`), levanta el HTML. Lo más rápido es:
```bash
node .claude/skills/tareas-deck/scripts/verify.mjs <ruta.html> /tmp/verify
```
Luego:
- Revisa los PNG a ojo (que entren completos, sin texto cortado; atiende cualquier
  `⚠ posible overflow` que reporte el script).
- Confirma **0 errores de consola / pageerror**.
- Revisa las capturas `viewport-movil-*` para el escalado y que los botones naveguen.

No declares el deck listo sin haberlo abierto en el navegador (vía Playwright). Si el
contenedor no tiene navegador/instalación y no se puede instalar, entrega el HTML e indícalo
explícitamente.

### 5. Guardar y exportar PDF

- HTML: `juntas/tareas/<desarrollo>/<año>/<mes-en-texto>/<desarrollo>-tareas-<YYYY-MM-DD>.html`
  (ej. `juntas/tareas/adara/2026/mayo/adara-tareas-2026-05-27.html`).
- PDF: mismo nombre con `.pdf`. Genéralo con:
  ```bash
  node .claude/skills/tareas-deck/scripts/export_pdf.mjs <ruta.html> <ruta.pdf>
  ```
- Entrega ambos (el HTML para proyectar/abrir en navegador, el PDF para imprimir/compartir;
  en iPhone el HTML se ve mejor en horizontal).

### 6. Versionar (si el usuario lo pide)

Commitea el HTML (y opcionalmente el PDF) en la rama de trabajo y abre/actualiza el PR.
Sigue el flujo de git del repo. No subas binarios pesados sin confirmar.

## Notas para perfeccionar / ampliar

- Si una corrida revela un mejor corte o un slide más útil, **actualiza también
  `assets/template.html`** para que la mejora quede para la próxima junta.
- Si un agregado nuevo se calcula seguido, agrégalo a `references/queries.md`.
- Comparte `scripts/export_pdf.mjs` y el sistema visual con `garantias-deck`. Para otro
  desarrollo, solo cambia el `proyecto_id` y el nombre en las rutas/portada.
