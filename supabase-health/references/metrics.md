# Metrics API de Supabase — infraestructura en vivo

Cada proyecto Supabase expone un endpoint Prometheus con ~200 series de Postgres e
infraestructura. Lo usamos para los números exactos de CPU, disk IO, disco, RAM,
egress y conexiones.

## Endpoint y auth

```
URL:      https://ifqwrtheakkvgezewxqx.supabase.co/customer/v1/privileged/metrics
Auth:     HTTP Basic  →  usuario: service_role   password: $SUPABASE_SERVICE_ROLE_KEY
Formato:  texto Prometheus (una serie por línea)
```

- El `service_role` key NO está en el repo. Debe venir como variable de entorno del
  entorno cloud: `SUPABASE_SERVICE_ROLE_KEY` (Supabase: Project Settings → API keys
  → service_role secret).
- **NUNCA** commitear este key. `scripts/fetch_metrics.sh` lo lee del entorno.
- La Metrics API está en **beta**: los nombres de series pueden cambiar. La primera
  corrida, valida los nombres reales contra esta lista y corrige.

## Series clave (verificar nombres reales en la 1ª corrida)

Nombres aproximados basados en el dashboard `supabase/supabase-grafana`. Ajustar tras
inspeccionar la salida real del endpoint.

| Qué medir | Serie(s) Prometheus aproximadas | Cómo derivar |
|---|---|---|
| **CPU busy %** | `node_cpu_seconds_total{mode="idle"}` | 100 − ratio(idle). Para snapshot, usar también las métricas de carga si existen |
| **Carga** | `node_load1`, `node_load5` | vs nº de vCPU |
| **Disk IO / IOPS** | `node_disk_reads_completed_total`, `node_disk_writes_completed_total`, `node_disk_read_bytes_total`, `node_disk_written_bytes_total` | tasa de IOPS y throughput |
| **Disk burst balance** | (gp3/gp2 burst balance si está expuesto) | % restante; bajo ⇒ throttling de IO |
| **Espacio de disco** | `node_filesystem_avail_bytes`, `node_filesystem_size_bytes` | usado % = 1 − avail/size |
| **RAM** | `node_memory_MemAvailable_bytes`, `node_memory_MemTotal_bytes` | usado % |
| **Swap** | `node_memory_SwapFree_bytes`, `node_memory_SwapTotal_bytes` | swap en uso ⇒ presión de memoria |
| **Egress / red** | `node_network_transmit_bytes_total` | bytes salientes (proxy de egress) |
| **Conexiones** | `pg_stat_database_num_backends`, `pg_settings_max_connections` | uso % de conexiones |
| **Cache hit** | `pg_stat_database_blks_hit`, `pg_stat_database_blks_read` | hit / (hit+read) |

> Nota: el endpoint da un **snapshot** instantáneo (contadores acumulados). Para
> tasas reales (IOPS/seg, egress/seg) se necesitarían dos muestras. Para el chequeo
> matutino basta con: (a) snapshots de gauges (disco usado, RAM, conexiones, burst
> balance) y (b) cruzar las tasas/queries pesadas con `pg_stat_statements` (ver
> `queries.md`), que sí da acumulados por query desde el último reset.

## Extracción

`scripts/fetch_metrics.sh` hace el curl y filtra con grep las series de la tabla a un
resumen compacto, para no volcar las ~200 series al contexto. Si una serie no aparece
con el nombre esperado, inspecciona la salida cruda (el script la deja en un tmp) y
ajusta esta tabla.
