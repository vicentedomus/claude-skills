---
name: supabase-health
description: >-
  Revisa de forma proactiva la salud del proyecto Supabase de Domus (BD Domus,
  ifqwrtheakkvgezewxqx) leyendo métricas de infraestructura en vivo (CPU, disk IO
  + burst balance, espacio, RAM, egress, conexiones) vía Metrics API e
  introspección de Postgres (pg_stat_statements, advisors, logs), las evalúa
  contra umbrales y manda un resumen accionable a WhatsApp vía un webhook de n8n.
  Pensada para correr cada mañana como sesión programada, pero úsala también
  cuando el usuario pida revisar el estado/salud de la base, diagnosticar picos de
  CPU/IO/egress, o por qué la página va lenta o se cae. Frases típicas: "revisa la
  BD", "cómo está Supabase", "estado de la base", "monitoreo matutino", "por qué
  está lenta la página", "diagnostica el disk IO / egress / CPU".
---

# Salud de Supabase (monitoreo matutino proactivo)

Esta skill detecta de forma **proactiva** los problemas que tiraron o ralentizaron
la página (disk IO, egress, CPU, RAM, conexiones) **antes** de que se vuelvan una
caída. Lee el estado real de la infraestructura + la causa raíz en Postgres, lo
evalúa contra umbrales fijos, y manda un resumen a WhatsApp por n8n.

**Proyecto Supabase:** `BD Domus` = `ifqwrtheakkvgezewxqx` (Postgres 17, us-east-1).

**Filosofía:** dos capas que se complementan.
1. **Infra real** (Metrics API): los números exactos de CPU/IO/disco/RAM/egress.
2. **Causa raíz** (Postgres): *por qué* — queries lentas, seq scans, índices
   faltantes, conexiones colgadas. Aquí está casi siempre el arreglo accionable.

## Recursos incluidos

- `references/metrics.md` — cómo leer la Metrics API (endpoint, auth) y el catálogo
  de series Prometheus relevantes. **La primera vez, captura los nombres reales** de
  las series (la API está en beta) y fíjalos aquí.
- `references/queries.md` — **todas las consultas SQL canónicas** de diagnóstico
  (ejecutar con la tool MCP `execute_sql`, proyecto `ifqwrtheakkvgezewxqx`). Léelo
  siempre antes de consultar.
- `references/thresholds.md` — los umbrales OK / WARN / CRIT (ajustables).
- `scripts/fetch_metrics.sh` — hace el `curl` al endpoint de métricas con el
  `service_role` key del entorno y extrae las series clave a un resumen compacto.
- `PROMPT.md` — el prompt exacto para la sesión programada de las 8 am.

## Proceso (sigue estos pasos en orden)

Crea una lista de tareas con estos pasos para no saltarte ninguno.

### 1. Métricas de infraestructura (Metrics API)

Corre `bash scripts/fetch_metrics.sh`. Lee el `service_role` key de la variable de
entorno `SUPABASE_SERVICE_ROLE_KEY`.

- **Si el key NO está definido**: NO te detengas. Omite esta sección, sigue con la
  introspección de BD (que ya cubre la causa raíz) y **anótalo en el resumen**
  ("⚠️ faltó SUPABASE_SERVICE_ROLE_KEY: sin métricas de infra").
- Si está: revisa CPU busy %, disk **burst balance** / IOPS, espacio de disco usado
  (**el % de `/data`**; el de `/` (OS+WAL) es informativo, alto por diseño — ver
  `thresholds.md`), RAM/swap, egress (bytes de red), conexiones. Compáralo con
  `references/thresholds.md`.
- La **primera ejecución**: confirma los nombres reales de las series contra
  `references/metrics.md` y corrígelos si Supabase los cambió.

### 2. Introspección de Postgres (causa raíz)

Lee `references/queries.md` y ejecuta con `execute_sql` (en este orden):
1. **Cache hit ratio** — bajo ⇒ disk IO.
2. **Top queries** por tiempo total, por bloques leídos (IO) y por filas devueltas
   (egress) desde `pg_stat_statements`.
3. **Seq scans** sobre tablas grandes.
4. **Conexiones**: activas / idle-in-transaction / long-running.
5. **Tamaños y bloat** de tablas/índices; índices sin uso.

### 3. Advisors y logs

- `get_advisors(project_id, type="performance")` → índices faltantes, FKs sin índice,
  políticas RLS costosas. Incluye el link de remediación.
- `get_logs(project_id, service="postgres")` y `service="api"` → errores, OOM,
  "disk full", límite de conexiones, 5xx en las últimas 24h.
- **Egress** (ver `queries.md` #9): en los api logs busca un mismo endpoint repetido
  muchas veces en segundos (re-fetch en loop), `select=*` sobre vistas grandes, y
  clientes `HeadlessChrome` o WebSockets de Realtime. Es la causa típica de un salto
  súbito de egress.

### 4. Evaluar estado global

Combina todo y asigna `status` global = el peor de los hallazgos:
- **CRIT** si hay error grave en logs (disco lleno, OOM, límite de conexiones), o
  alguna métrica cruzó umbral CRIT.
- **WARN** si hay métricas en zona WARN, advisors de performance importantes, o
  queries claramente problemáticas.
- **OK** si todo está dentro de rango.

Prioriza los **hallazgos accionables** (máx ~5): qué medir → qué hacer (ej. "falta
índice en `reportes_avance.tarea_id` → seq scan de 1.2M filas → crear índice").

### 5. Notificar por WhatsApp (n8n)

Haz `POST` del payload JSON (ver abajo) al webhook de n8n
`https://n8n.vichon8n.tech/webhook/supabase-health`. El workflow
`DomusBot - Alerta Salud Supabase` formatea el resumen como **texto libre** y lo
manda por WhatsApp a través del sub-workflow **Guard CSW** (que respeta la ventana
de 24 h: si está cerrada, encola el mensaje y manda el template de pendientes). No
hay plantilla que aprobar ni credencial que configurar en este flujo.

```bash
curl -sS -X POST https://n8n.vichon8n.tech/webhook/supabase-health \
  -H 'Content-Type: application/json' \
  -d @payload.json
```

**Payload:**
```json
{
  "project": "BD Domus",
  "date": "YYYY-MM-DD",
  "status": "OK|WARN|CRIT",
  "summary": "1-2 frases en español, claras y accionables",
  "metrics": {
    "cpu_pct": 0,
    "disk_io_burst_pct": 0,
    "disk_used_pct": 0,
    "disk_os_pct": 0,
    "ram_pct": 0,
    "egress_note": "",
    "connections": ""
  },
  "findings": ["hallazgo accionable 1", "hallazgo accionable 2"]
}
```

Si una métrica no se pudo leer (p. ej. faltó el key), pon `null` y dilo en `summary`.
`disk_used_pct` = mount **`/data`** (datos Postgres, el accionable); `disk_os_pct` =
mount **`/`** (OS+WAL, informativo). El `status` de disco se decide con `/data`.

> ⚠️ **El `date` define el nombre del archivo del reporte.** El workflow guarda el
> HTML en Supabase Storage como `salud-<date>.html` (con `x-upsert`, sobreescribe) y
> el WhatsApp enlaza a ese archivo vía el `reporte-viewer`. En una corrida **real**
> usa SIEMPRE la fecha de hoy (`YYYY-MM-DD`).
>
> **Para validar/probar el webhook (no es una corrida real), NUNCA uses la fecha de
> hoy:** pon `"date": "TEST"` para que escriba `salud-TEST.html` y **no pise el
> reporte del día**. Un disparo de prueba con la fecha real contamina el reporte de
> producción y, por caché del viewer, puede quedar visible un buen rato. El payload
> de prueba debe ser claramente sintético (p. ej. `summary` que diga "prueba de
> webhook").

### 6. Cerrar

Deja en el chat de la sesión el análisis completo (tablas de queries, números). El
resumen a WhatsApp es el digest; el detalle queda en el historial de la sesión.
