---
name: resultados-proveedores
description: >-
  Genera el deck "Análisis de Resultados" mensual POR PROVEEDOR de garantías de
  Domus (postventa) — el que se entrega a cada proveedor en su junta mensual —
  leyendo datos en vivo de Supabase. Úsala siempre que el usuario pida la
  presentación/análisis de resultados de un proveedor de garantías (House, Grama,
  Norkes, MH, Kaiter…), el deck mensual de un proveedor, o regenerar/actualizar
  esa presentación con datos frescos — aunque no diga "deck". Frases típicas:
  "arma el análisis de resultados de Grama", "el deck de resultados de House de
  mayo", "la presentación mensual para el proveedor X", "cómo le fue a Norkes
  este mes", "genera los resultados de los proveedores del mes pasado". NO es el
  deck de garantías abiertas para la junta interna (eso es garantias-deck): este
  es UNO por proveedor, con recibidos/terminados/pendientes y KPIs de ese
  proveedor.
---

# Deck "Análisis de Resultados" por proveedor de garantías

Convierte en proceso repetible lo que se afinó a mano para House: leer de Supabase
los tickets de un proveedor, calcular los cortes del mes y producir un deck HTML
(1920×1080, 11 slides, modales interactivos) bajo `juntas/resultados-proveedores/`.

**Audiencia:** el proveedor (postventa). Tono claro, una idea por slide, en español.
**Default temporal:** se trabaja **el mes pasado** (Domus presenta el mes ya cerrado).

## Motor compartido (NO lo dupliques por mes)

El deck NO es autocontenido: usa el motor que vive en `juntas/resultados-proveedores/`:
`styles.css` + `deck.js` + `assets/logo.png`. Cada deck es un `.html` en
`AAAA/<mes>/<proveedor>.html` que referencia el motor con `../../`. El **deck de
referencia (gold)** es `juntas/resultados-proveedores/2026/mayo/house.html`:
cópialo como base estructural y **solo cambia los datos** — ya trae los 11 slides,
el modal, los `data-kpi` y la estructura de los arrays. Lee también el `README.md`
de esa carpeta.

## Recursos de la skill

- `references/queries.md` — modelo de datos, definiciones fijas (recibidos /
  terminados / pendientes), la **regla de oro del join a proyectos**, y el SQL.
  Léelo siempre antes de consultar.
- `scripts/aggregates.py` — el caballo de batalla. Recibe el JSON crudo de la
  consulta combinada y deriva **todo**: donas (conic-gradient + leyenda + filas),
  KPIs en **días hábiles**, severidad/recurrencia, los arrays `TICKETS` y
  `TERMINADOS` listos para pegar, y el slide de pendientes ordenado. Calcula los
  días hábiles en Python (no en SQL) y **arrastra el desarrollo** en cada fila, lo
  que elimina los dos errores clásicos (aritmética de ángulos y confundir el
  desarrollo por el lote).
- `scripts/build_standalone.py` — empaqueta el deck en UN html autocontenido
  (CSS+JS+logo embebidos) para mandarlo por chat / abrir sin servidor. Sin deps.
- `scripts/export_pdf.mjs` — exporta a PDF (508×285.75 mm) con Playwright (donde
  esté instalado; en Claude Code web suele no haber navegador → usa el standalone).

## Proceso (en orden)

Publica un checklist con estos pasos y mantenlo vivo.

### 1. Confirmar proveedor y mes
Por defecto, **el mes pasado**. Confirma proveedor y, si aplica, si es un mes simple
("Mayo 2026") o combinado ("Marzo + Abril") cuando se está poniendo al corriente.

### 2. Sacar los datos (una sola consulta)
Lee `references/queries.md`. Corre el paso 0 (mapear `proveedor_id`, sanity de
estatus), luego la **consulta combinada** (recibidos + terminados + pendientes, con
desarrollo) para `:PV/:INI/:FIN`, y la del **mes anterior** (terminados) para el
baseline. Guarda cada resultado como JSON (`/tmp/<prov>-<mes>.json`,
`/tmp/<prov>-prev.json`). Usa los números **tal cual** vienen de la BD.

### 3. Derivar todo con aggregates.py
```bash
python3 .claude/skills/resultados-proveedores/scripts/aggregates.py \
    /tmp/<prov>-<mes>.json --prev /tmp/<prov>-prev.json
```
De ahí salen, ya calculados: las dos donas (ángulos + leyenda + filas de tabla),
los KPIs en días hábiles y su baseline, y los arrays `TICKETS`/`TERMINADOS`, más el
slide de pendientes. **No rehagas esta aritmética a mano.**

### 4. Construir el deck
Copia el deck gold (`2026/mayo/house.html`) a `AAAA/<mes>/<proveedor>.html` y pega
los bloques que dio `aggregates.py`. Por slide:
- **Portada / intro / pasos**: proveedor y mes.
- **Slide 4 (por lote)** y **6 (por zona)**: dona (`conic-gradient`), leyenda y tabla.
- **Slide 7 (cualitativo)**: redacta las cards por zona **a partir de los recibidos
  reales** (agrupa por zona; resalta riesgos, p. ej. eléctrico, con `.zona-card.alert`
  y `.red`). Ajusta `grid-template-columns/rows` al número de zonas.
- **Slide 9 (KPIs)**: los 4 números grandes + sus `delta` vs. el mes anterior
  (up = subió/peor en tiempos; down = mejoró). Marca cada `.kpi-big` con
  `data-kpi="trabajo|programacion|severidad|recurrencia"` y pega el array
  `TERMINADOS` (incluye `desc`, `diasTrabajo`, `diasProg`) para que los modales
  funcionen. Footnote: "*Tiempos en días hábiles" (+ menciona algún outlier si pesa).
- **Slide Pendientes** (antes de Siguientes pasos): tabla del backlog que dio el
  script; redacta el callout (cuántos, foco más viejo, prioridad inmediata).
  **Auto-paginación:** el slide mide 1080px y ~14 filas es el máximo legible. Si
  `aggregates.py` marca que hay que paginar (>14 pendientes), parte la tabla en los
  slides balanceados que indica: el primero lleva el callout; los de continuación se
  titulan "Pendientes de Programar — continuación" y **sin** callout (solo la tabla).
  Mejor dos páginas legibles que una recortada.
- **Siguientes pasos**: acciones reales del mes (programar pendientes, etc.).
- Pega el array `TICKETS` (recibidos) para los modales de Lote/Zona.

### 5. Validar antes de entregar (made-by-data, sin asumir)
- **Conteos del JSON = `count(*)` de la BD** (paso 0): al capturar el resultado de la
  consulta es fácil soltar una fila. `aggregates.py` imprime recibidos/terminados/
  pendientes — deben cuadrar con la consulta de conteos antes de seguir.
- Los conteos por lote y por zona **suman** el total de recibidos; los ángulos de
  cada dona cierran en 360.
- Cada `data-key` de las tablas de Lote/Zona tiene tickets que coinciden en el array
  `TICKETS` (mismas cadenas de `zona`/`lote`).
- Los promedios del array `TERMINADOS` cuadran con los números grandes del slide 9.
- **Cada prefijo de lote = el desarrollo real de la BD** (viene en el JSON; nunca lo
  inventes). Revisa que no se haya colado un "Adara 48" que en realidad es "Capri 48".
- `python3 - <<'PY'` o `node --check` para confirmar que el HTML/JS no truena.

### 6. Empaquetar, guardar y ENTREGAR (HTML + PDF)

Se entregan **dos formatos**: el standalone HTML (interactivo, para revisar los
modales) y el **PDF** (para compartir/imprimir). El PDF es parte del entregable, no
opcional.

1. **Standalone para revisión:**
   `python3 .claude/skills/resultados-proveedores/scripts/build_standalone.py <ruta.html>`
   → mándalo por chat (SendUserFile).
2. **PDF** (508×285.75 mm, un slide por página):
   `node .claude/skills/resultados-proveedores/scripts/export_pdf.mjs <ruta.html> <misma-ruta>.pdf`
   En Claude Code web el contenedor **no trae navegador**; instálalo una vez por sesión:
   `npm install @playwright/test && npx playwright install chromium` (≈30 s). Verifica
   que el PDF tenga **una página por slide** y MediaBox ~1440×810 pt.
3. **Commitea SIEMPRE** el `.html` **y el `.pdf`** en la carpeta del mes (regla de oro:
   el contenedor web es efímero; lo no commiteado se pierde — así se perdieron los decks
   del 5-may). Entrega ambos al usuario. Push + PR.

## Estructura de slides (fija + editable)

1. Portada · 2. Introducción · 3. Paso 1 (intro lote) · 4. Tickets por Lote ·
5. Paso 2 (intro zona) · 6. Tickets por Zona · 7. Análisis cualitativo por zona ·
8. Paso 3 (intro KPIs) · 9. KPIs (4 grandes, clickeables) · 10. Pendientes de
Programar · 11. Siguientes pasos.

## Convenciones clave

- **Días hábiles** en todo lo temporal (lun–vie, sin festivos). Lo calcula
  `aggregates.py`; no lo rehagas en SQL ni a mano.
- **Baseline = mes anterior en vivo** (misma consulta), salvo que el usuario pida
  respetar un deck previo horneado a mano.
- **Severidad y recurrencia** se calculan sobre los **terminados** del mes.
- **Outliers**: por defecto inclúyelos tal cual y acláralo en el footnote.
- **Regla de oro**: el desarrollo SIEMPRE viene del join a `proyectos`, nunca del lote.

## Perfeccionar / ampliar

Si una corrida revela un mejor corte o un slide más útil, mejora **el deck gold**
(`2026/mayo/house.html`) y, si aplica, el motor (`deck.js`/`styles.css`) — así la
mejora queda para todos los proveedores. Si un cálculo nuevo se repite, agrégalo a
`aggregates.py`.
