# Umbrales OK / WARN / CRIT

Valores por defecto. Ajústalos tras 2-3 días de datos reales de `BD Domus`.
El `status` global = el **peor** de todos los hallazgos.

## Infraestructura (Metrics API)

| Métrica | OK | WARN | CRIT |
|---|---|---|---|
| CPU busy sostenido | < 70% | 70–90% | > 90% |
| Disk burst balance | > 50% | 20–50% | < 20% |
| **Disco `/data`** (datos Postgres) | < 75% | 75–90% | > 90% |
| Disco `/` (OS+WAL) | informativo | — | — |
| RAM usada | < 80% | 80–92% | > 92% |
| Swap en uso | 0 | cualquier uso | crecimiento sostenido |
| Conexiones (% de max) | < 70% | 70–85% | > 85% |
| Egress | sin salto vs día previo | salto notable | cerca de la cuota del plan |

> **Disco — cuál mirar.** El status de disco lo define **`/data`** (datos de Postgres).
> El mount **`/` (OS+WAL)** ronda ~74% por la **imagen base de Supabase**, no por
> nuestros datos (la BD pesa ~22 MB ⇒ `/data` está casi vacío): es **informativo** y
> **no** debe disparar WARN por sí solo. `/` solo es preocupante si un log dice
> "disk full / could not extend file" o si **crece sostenidamente** entre días.
> `fetch_metrics.sh` ya imprime el `% usado` de cada mount etiquetado.

## Postgres (introspección)

| Señal | WARN | CRIT |
|---|---|---|
| Cache hit ratio | < 99% | < 95% |
| Query con `mean_exec_time` | > 500 ms con `calls` altos | > 2000 ms con `calls` altos |
| Seq scan en tabla > 100k filas | presente | con `seq_tup_read` en millones |
| `idle in transaction` colgada | `max_tx` > 5 min | `max_tx` > 30 min |
| Índices sin uso grandes | informativo | — |

## Logs y advisors

| Señal | Nivel |
|---|---|
| Log "disk full" / "could not extend file" | CRIT |
| Log OOM / "out of memory" | CRIT |
| Log "too many connections" / límite alcanzado | CRIT |
| 5xx repetidos en api logs | WARN→CRIT según volumen |
| Advisor performance severidad alta (índice faltante en tabla caliente) | WARN |

## Política de notificación (WhatsApp)

- **CRIT / WARN**: manda alerta siempre.
- **OK**: manda un digest breve diario (confirma que todo está sano). Si prefieres
  silencio en OK, el workflow de n8n puede filtrarlo — decisión de configuración.
