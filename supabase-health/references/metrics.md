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

## Perfil de la instancia (verificado 2026-05-28)

`BD Domus` corre en una instancia **chica (~1 GB RAM, 2 vCPU)**:
- `node_memory_MemTotal_bytes` ≈ **906 MB**, `SwapTotal` ≈ 1 GB.
- `max_connections_connection_count` = **60** (límite duro de Postgres).
- 2 discos: `/` (nvme0n1, ~9.65 GB, OS+WAL) y `/data` (nvme1n1, ~7.8 GB, datos Postgres).
  **El indicador accionable es `/data`**; `/` ronda ~74% por la imagen base de Supabase
  (no son nuestros datos: la BD pesa ~22 MB ⇒ `/data` está ~0.3% lleno). No confundas el
  74% del SO con un disco lleno. Ver `thresholds.md` (fila de disco).

**Las dos restricciones que tumban la página son CONEXIONES y MEMORIA**, no el tamaño
de datos. Prioriza esas dos en la evaluación.

## Series clave (nombres REALES, verificados contra el endpoint)

El endpoint emite ~740 series. Estas son las que importan:

| Qué medir | Serie(s) Prometheus reales | Cómo derivar |
|---|---|---|
| **Conexiones** 🔴 | `pg_stat_database_num_backends` / `max_connections_connection_count` | uso % = backends / max. **>85% ⇒ riesgo de "too many connections"** |
| **RAM usada** | `node_memory_MemAvailable_bytes` / `node_memory_MemTotal_bytes` | usado % = 1 − avail/total |
| **Swap en uso** 🟡 | `node_memory_SwapTotal_bytes` − `node_memory_SwapFree_bytes` | >0 ⇒ presión de memoria ⇒ más disk IO |
| **Espacio de disco** | `node_filesystem_avail_bytes` / `node_filesystem_size_bytes` (por `mountpoint` `/` y `/data`) | usado % = 1 − avail/size. **Evalúa `/data` contra umbrales; `/` es informativo.** `fetch_metrics.sh` ya imprime ambos etiquetados. |
| **CPU / carga** | `node_load1`, `node_load5`, `node_load15` | vs 2 vCPU: load > 2 ⇒ saturación |
| **CPU detallado** | `node_cpu_seconds_total{mode=...}` (por `cpu` e `idle/user/system/iowait/steal`) | contador acumulado; necesita 2 muestras para % instantáneo |
| **Disk IO** | `node_disk_reads_completed_total`, `node_disk_writes_completed_total`, `node_disk_read_bytes_total`, `node_disk_written_bytes_total` (por `device`) | IOPS/throughput; `mode="iowait"` alto corrobora IO |
| **Egress / red** | `node_network_transmit_bytes_total{device="ens5"}` | bytes salientes (proxy de egress) |
| **Cache hit** | `pg_stat_database_blks_hit_total`, `pg_stat_database_blks_read_total` | hit / (hit+read) |

> No hay serie de **disk burst balance** en este endpoint (es de EBS/AWS). Usa `iowait`
> (en `node_cpu_seconds_total`) + las tasas de `node_disk_*` como proxy de presión de IO.
>
> Nota: el endpoint da un **snapshot** de contadores acumulados, y el de red se refresca
> ~cada 60s. Para tasas reales (IOPS/seg, egress/seg, CPU%) se necesitan 2 muestras
> separadas ≥60s. Para el chequeo matutino basta con los **gauges** instantáneos
> (conexiones, RAM, swap, disco, load) + cruzar con `pg_stat_statements` (`queries.md`).

## Extracción

`scripts/fetch_metrics.sh` hace el curl y filtra con grep las series de la tabla a un
resumen compacto, para no volcar las ~200 series al contexto. Si una serie no aparece
con el nombre esperado, inspecciona la salida cruda (el script la deja en un tmp) y
ajusta esta tabla.
