# Consultas canónicas — diagnóstico de salud de Postgres

Se ejecutan con la tool MCP de Supabase `execute_sql`.
**Proyecto Supabase de Domus:** `ifqwrtheakkvgezewxqx`.

Estas consultas buscan la **causa raíz** de los picos de disk IO, egress y CPU:
queries pesadas, lecturas a disco por cache misses, seq scans por índices faltantes,
y conexiones colgadas. Ejecútalas en este orden y resume los hallazgos.

> `pg_stat_statements` debe estar habilitado (suele estarlo en Supabase). Si una
> query contra esa vista falla con "relation does not exist", anótalo y omite ese
> bloque; el resto del diagnóstico sigue siendo válido.

## 1. Cache hit ratio (disk IO)

Un hit ratio bajo significa que Postgres está yendo a disco ⇒ disk IO alto.

```sql
select
  sum(blks_hit)  as cache_hits,
  sum(blks_read) as disk_reads,
  round(100.0 * sum(blks_hit) / nullif(sum(blks_hit) + sum(blks_read), 0), 2) as cache_hit_pct
from pg_stat_database
where datname = current_database();
```
Objetivo: `cache_hit_pct` ≥ 99%. Por debajo ⇒ WARN (memoria insuficiente o working
set demasiado grande / queries que escanean de más).

## 2. Top queries por tiempo total (CPU + IO acumulado)

> **Primero, la ventana.** `pg_stat_statements` acumula desde el último reset, que
> pueden ser **meses**. El ranking de abajo NO es "qué dolió hoy": promedia todo el
> período, y una query arreglada hace semanas puede seguir encabezándolo con tráfico
> viejo. **Encabeza siempre la tabla con la ventana** ("acumulado desde YYYY-MM-DD,
> N días") para que nadie la lea como la foto del día.
>
> ```sql
> select stats_reset, now() - stats_reset as ventana from pg_stat_statements_info;
> ```
>
> No resetees en el chequeo diario: se pierde el histórico y no se gana
> comparabilidad (el chequeo no guarda baseline en ningún lado). Un reset manual
> **mensual** es razonable si quieres un ranking por período.

```sql
select
  round(total_exec_time::numeric, 0)              as total_ms,
  calls,
  round(mean_exec_time::numeric, 2)               as mean_ms,
  round((100.0 * total_exec_time / sum(total_exec_time) over ())::numeric, 1) as pct_total,
  rows,
  shared_blks_read                                as disk_blocks_read,
  left(regexp_replace(query, '\s+', ' ', 'g'), 160) as query
from pg_stat_statements
order by total_exec_time desc
limit 15;
```
Las primeras filas son las que más CPU/IO consumen acumulado. `mean_ms` alto +
`calls` alto = candidata a optimizar o cachear.

## 2b. Forma de las lecturas vía API: ¿con embed o ya hidratadas?

**Corre esta ANTES de recomendar "hidratar en cliente".** El marcador de un embed
anidado de PostgREST es `row_to_json` en el texto de la query; si no está, esa
lectura **ya trae solo FKs escalares** y la hidratación ya se hizo.

```sql
select
  case when query ilike '%row_to_json%' then 'EMBED' else 'plana' end as forma,
  substring(query from 'FROM "public"\."([a-z_]+)"')  as tabla,
  calls,
  round(mean_exec_time::numeric, 1)                   as mean_ms,
  round((100.0 * total_exec_time / sum(total_exec_time) over ())::numeric, 1) as pct
from pg_stat_statements
where query ilike '%pgrst_source%'
order by total_exec_time desc
limit 15;
```

Cómo leerla:

- **`plana` cara** (p. ej. `tickets` 241 ms) ⇒ el costo **no** está en el embed.
  Hidratar no la va a arreglar; mira RLS, índices o el plan. Recomendar hidratación
  aquí es mandar a hacer trabajo ya hecho — pasó el 2026-08-05.
- **Una `EMBED` y una `plana` de la MISMA tabla** ⇒ normal después de una migración
  a hidratación en cliente: la `EMBED` es residuo histórico. Confírmalo comparando
  `calls` entre dos corridas: si **no se mueve**, es tráfico muerto que solo infla la
  ventana acumulada y hay que descontarlo del análisis. (`tickets`/`visitas` llevan
  congeladas en 13,168 y 12,860 llamadas desde el 2026-08-03.)
- **`EMBED` con `calls` creciendo** ⇒ esa sí es candidata real a hidratar. Ver el
  patrón en `CLAUDE.md` de domus-hub (`_hydrateTicketRefs`/`_hydratePolizaRefs`).

## 3. Top queries por bloques leídos de disco (disk IO directo)

```sql
select
  shared_blks_read                                as disk_blocks_read,
  round((shared_blks_read * 8192.0)/(1024*1024), 1) as approx_mb_read,
  calls,
  round(mean_exec_time::numeric, 2)               as mean_ms,
  left(regexp_replace(query, '\s+', ' ', 'g'), 160) as query
from pg_stat_statements
where shared_blks_read > 0
order by shared_blks_read desc
limit 10;
```

## 4. Top queries por filas devueltas (egress)

Mucho `rows` por llamada ⇒ payloads grandes ⇒ egress alto. Busca `SELECT *` sin
límite o sin filtros.

```sql
select
  rows,
  calls,
  case when calls > 0 then round((rows::numeric / calls), 1) else 0 end as rows_per_call,
  left(regexp_replace(query, '\s+', ' ', 'g'), 160) as query
from pg_stat_statements
where calls > 0
order by rows desc
limit 10;
```

## 5. Seq scans sobre tablas grandes (causa típica de IO/CPU)

Tablas grandes con muchos `seq_scan` ⇒ falta un índice.

```sql
select
  relname                              as tabla,
  seq_scan,
  seq_tup_read,
  idx_scan,
  n_live_tup                           as filas_aprox,
  pg_size_pretty(pg_total_relation_size(relid)) as tamano
from pg_stat_user_tables
where seq_scan > 0
order by seq_tup_read desc
limit 15;
```

## 6. Conexiones (saturación)

```sql
select
  state,
  count(*)                                              as conns,
  max(now() - state_change)                             as max_en_estado,
  max(now() - xact_start) filter (where xact_start is not null) as max_tx
from pg_stat_activity
where datname = current_database()
group by state
order by conns desc;
```
Revisa `idle in transaction` con `max_tx` alto (conexiones colgadas que retienen
recursos) y el total vs `max_connections`:

```sql
select
  (select count(*) from pg_stat_activity) as conexiones_actuales,
  current_setting('max_connections')::int as max_conexiones;
```

## 7. Tamaños de tablas e índices sin uso

```sql
-- Tablas más grandes
select
  relname as tabla,
  pg_size_pretty(pg_total_relation_size(relid)) as total,
  pg_size_pretty(pg_relation_size(relid))       as solo_datos,
  n_live_tup as filas
from pg_stat_user_tables
order by pg_total_relation_size(relid) desc
limit 10;
```

```sql
-- Índices que nunca se usan (ocupan disco y ralentizan escrituras)
select
  relname as tabla,
  indexrelname as indice,
  idx_scan as usos,
  pg_size_pretty(pg_relation_size(indexrelid)) as tamano
from pg_stat_user_indexes
where idx_scan = 0
order by pg_relation_size(indexrelid) desc
limit 10;
```

## 8. Tamaño total de la BD (vs cuota del plan)

```sql
select pg_size_pretty(pg_database_size(current_database())) as tamano_bd;
```

## 9. Egress (bytes salientes) — diagnóstico

El egress = bytes enviados a los clientes. Cuota free = 5 GB/mes. No hay métrica de
"bytes por query" en `pg_stat_statements`, así que se diagnostica por **tres vías**:

**(a) Proxy por filas devueltas** — lecturas REST que devuelven más datos:
```sql
select
  rows, calls,
  case when calls > 0 then round((rows::numeric / calls), 1) else 0 end as rows_per_call,
  left(regexp_replace(query, '\s+', ' ', 'g'), 100) as query
from pg_stat_statements
where query ilike '%pgrst_source%'      -- solo lecturas vía PostgREST (API)
order by rows desc
limit 15;
```
Sospecha de **vistas con `select=*`** (`ventas_con_estado`, `tareas_con_estado`) y de
selects con joins anidados anchos (`tickets`, `polizas`, `visitas`): payload grande
× muchas llamadas = egress alto.

**(b) Logs de API** — `get_logs(service="api")`. Busca:
- El **mismo endpoint repetido muchas veces en pocos segundos** (re-fetch en loop,
  componente que re-renderiza, varias pestañas) → causa típica de un salto súbito.
- `select=*` sobre vistas/tablas grandes.
- Clientes **`HeadlessChrome`** (tests/automatización/scrapers): si uno corre en loop,
  dispara el egress. Cruza la hora del salto con cuándo se lanzó algo headless.
- `GET /realtime/v1/websocket` (101): Realtime difunde cada cambio a cada cliente
  suscrito; muchas suscripciones = egress sostenido por WebSocket.

**(c) Métrica de red** — la da `fetch_metrics.sh` ya calculada: el bloque `# Tasas`
imprime `egress ... MB/min -> ~N GB/dia`. Evalúa **eso** contra `thresholds.md`; el
absoluto de `node_network_transmit_bytes_total` es acumulado desde el arranque (p. ej.
61 GB en 67 días) y no es una señal de salud. El egress **facturado** del mes se ve en
el dashboard de Supabase (Reports/Usage), no en este endpoint.

> **Ojo con `rows` como proxy de egress** (vías (a) y #4): PostgREST envuelve la
> respuesta en una agregación JSON, así que `pg_stat_statements.rows` es **1 por
> llamada** para toda lectura vía API y `rows_per_call` sale 1.0 siempre. Sirve para
> comparar `calls`, no para estimar el tamaño del payload.
