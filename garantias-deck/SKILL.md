---
name: garantias-deck
description: >-
  Genera la presentación (deck HTML autocontenido + PDF) del estado de las
  garantías ABIERTAS de Domus para la junta operativa, leyendo datos en vivo de
  Supabase. Úsala siempre que el usuario pida la presentación o el deck de
  garantías para la junta, el reporte de garantías abiertas/pendientes, o
  actualizar/regenerar la presentación de garantías con datos frescos — aunque no
  diga "deck" explícitamente. Frases típicas: "arma el deck de garantías",
  "presentación de garantías para la junta", "cómo vamos con las garantías",
  "actualiza la presentación de garantías", "el reporte quincenal/mensual de
  garantías", "necesito las garantías abiertas para la junta del viernes".
  Está pensada para garantías hoy, pero su estructura (datos → agregados →
  plantilla de deck → verificación → guardado/PDF) es ampliable a otros temas de
  junta (ventas, cobranza) más adelante.
---

# Deck de garantías abiertas (para junta operativa)

Esta skill convierte en un proceso repetible lo que se hizo a mano la primera vez:
leer las garantías abiertas de Supabase, calcular los mismos cortes, y producir un
deck HTML limpio (16:9, autocontenido, adaptable a cualquier pantalla) + un PDF,
guardado bajo la convención `juntas/`.

**Audiencia del deck:** equipo operativo de garantías (no técnico). Tono claro y
accionable, números grandes, una idea por slide, en español.

**Filosofía:** la estructura es **fija pero editable** — los ~10 slides de abajo son
la base probada; en cada junta puedes agregar o quitar slides si el usuario lo pide,
pero conserva la narrativa y el sistema visual.

## Recursos incluidos

- `assets/template.html` — el deck probado y funcionando. **Es el punto de partida:
  cópialo y refresca los datos**, no lo reconstruyas desde cero. Ya trae el sistema
  visual, el escalado adaptable y la navegación táctil (botones + swipe + teclado).
- `references/queries.md` — el modelo de datos, la definición fija de "abiertas" y
  **todas las consultas SQL canónicas** (ejecutar con la tool MCP de Supabase
  `execute_sql`, proyecto `ifqwrtheakkvgezewxqx`). Léelo siempre antes de consultar.
- `scripts/export_pdf.mjs` — exporta el deck HTML a PDF (un slide = una página
  horizontal). Requiere el `@playwright/test` que ya está en el repo.

## Proceso (sigue estos pasos en orden)

Crea una lista de tareas con estos pasos para no saltarte ninguno.

### 1. Confirmar alcance y fecha de corte

El corte es **hoy** (`current_date`). Confirma brevemente con el usuario si hay algo
especial para esta junta (un desarrollo concreto, incluir o no rechazadas, slides
extra). Si no, procede con la definición fija de `references/queries.md`.

### 2. Sacar los datos de Supabase

Lee `references/queries.md` y ejecuta, con la tool `execute_sql`:
1. El **sanity check** de estatus (paso 0). Si aparece un estatus nuevo no previsto,
   detente y pregunta antes de seguir.
2. El **dataset enriquecido** (consulta 1) — lo usarás para las listas de detalle
   (top antiguas sin programar, top vencidas) y para verificar números a mano.
3. Los **agregados** (consulta 2): por desarrollo, proveedor, zona, prioridad, buckets
   de antigüedad y de atraso, recurrentes y viviendas afectadas.

Trabaja con los números **exactamente** como vienen de la BD. No inventes ni redondees
datos; si un agregado se ve raro, vuelve a consultar.

### 3. Construir el deck (usa la skill huashu-design + la plantilla)

Esta skill se apoya en **huashu-design** para el render. El camino rápido y fiable:

1. Copia `assets/template.html` a la ubicación destino (ver paso 5).
2. **Refresca los datos** en cada slide con los resultados frescos:
   - Portada y KPIs: total abiertas, viviendas afectadas, vencidas, estancadas (+90d),
     antigüedad prom/máx.
   - Embudo: pendientes → programadas → vencidas; contexto (terminadas, rechazadas, total).
   - Barras apiladas (desarrollo, proveedor): cada barra se segmenta en
     **pendiente (ámbar) · programada al día (teal) · vencida (rojo)**, donde
     `programada al día = programadas − vencidas`. El ancho de cada `.track` es
     `total_de_la_fila / total_máximo * 100%`, y el ancho de cada `.seg` es el % dentro
     de esa fila. Resalta el cuello de botella (el proveedor con más vencidas).
   - Buckets (atraso y antigüedad): la altura de cada `.bar` es relativa al bucket mayor.
   - Zona: barras horizontales, ancho relativo al máximo.
   - Prioridad: dona Verde/Amarillo/Rojo (suele estar casi todo en Verde → señala que
     la priorización no se usa, si sigue siendo el caso).
   - Focos y plan de trabajo: actualiza las listas top y redacta los hallazgos/acciones
     **a partir de los datos reales de esta corrida** (no copies los del mes pasado).
3. Mapea el contador de slides (`x / N`) y los pies de página si cambia el número de slides.

**Semántica de color (no la cambies):** ámbar = pendiente de programar · teal =
programada al día · rojo = vencida/atrasada. Verde/Amarillo/Rojo solo para el nivel de
prioridad del ticket.

### Estructura base de slides (fija + editable)

1. Portada
2. Resumen ejecutivo (KPIs)
3. Embudo del pipeline (pendientes → programadas → vencidas)
4. Por desarrollo
5. Por proveedor (resaltar el cuello de botella)
6. Foco: atrasos + top vencidas
7. Foco: pendientes estancadas + top antiguas
8. Por zona
9. Recurrentes + uso de prioridades
10. Plan de trabajo (acciones priorizadas)

Agrega/quita slides solo si el usuario lo pide (p. ej. un slide por cliente o por lote).
Mantén el plan de trabajo al final.

### 4. Verificar antes de entregar

Con Playwright (`@playwright/test` del repo), levanta el HTML y:
- Captura los slides y revísalos a ojo (que entren completos, sin texto cortado).
- Confirma **0 errores de consola / pageerror**.
- Verifica que el escalado funcione en 1280×720, móvil horizontal y móvil vertical, y
  que los botones de navegación avancen.

No declares el deck listo sin haberlo abierto en el navegador (vía Playwright).

### 5. Guardar y exportar PDF

- HTML: `juntas/garantias/<año>/<mes-en-texto>/garantias-abiertas-<YYYY-MM-DD>.html`
  (ej. `juntas/garantias/2026/mayo/garantias-abiertas-2026-05-25.html`).
- PDF: mismo nombre con `.pdf`. Genéralo con:
  ```bash
  node .claude/skills/garantias-deck/scripts/export_pdf.mjs <ruta.html> <ruta.pdf>
  ```
- Entrega ambos al usuario (el HTML para proyectar/abrir en el navegador, el PDF para
  imprimir/compartir; en iPhone el HTML se ve mejor en horizontal).

### 6. Versionar (si el usuario lo pide)

Commitea el HTML (y opcionalmente el PDF) en la rama de trabajo y abre/actualiza el PR.
Sigue el flujo de git del repo. No subas binarios pesados sin confirmar.

## Notas para perfeccionar / ampliar

- Si una corrida revela un mejor corte o un slide más útil, **actualiza también
  `assets/template.html`** para que la mejora quede para la próxima junta. Ese es el
  punto de "perfeccionable".
- Si un agregado nuevo se calcula seguido, agrégalo a `references/queries.md`.
- Para ampliar a otro tema de junta (ventas, cobranza): clona este patrón
  (definiciones + queries + plantilla + verificación + guardado) en una skill nueva con
  su propia carpeta en `juntas/<área>/`, reutilizando `scripts/export_pdf.mjs`.
