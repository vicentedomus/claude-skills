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
| **Swap-out** (MB/min) **+ residencia creciendo** | ≈ 0, o residencia estable/bajando | > 1 **y** creciendo | > 10 y creciendo, o `oom_kill` > 0 |
| Swap en uso (MB) | informativo | — | — |
| Conexiones (% de max) | < 70% | 70–85% | > 85% |
| **Egress promedio de vida** (% de la cuota del plan) | < 40% | 40–70% | > 70% |
| Egress de la muestra de 90s | contexto — nunca dispara status | — | — |

> **Disco — cuál mirar.** El status de disco lo define **`/data`** (datos de Postgres).
> El mount **`/` (OS+WAL)** ronda ~74% por la **imagen base de Supabase**, no por
> nuestros datos (la BD pesa ~22 MB ⇒ `/data` está casi vacío): es **informativo** y
> **no** debe disparar WARN por sí solo. `/` solo es preocupante si un log dice
> "disk full / could not extend file" o si **crece sostenidamente** entre días.
> `fetch_metrics.sh` ya imprime el `% usado` de cada mount etiquetado.

> **Swap y egress — la tasa, nunca el absoluto.** Ambos son **contadores acumulados
> desde el arranque de la instancia**, así que su valor absoluto crece para siempre y
> no dice nada de la salud de hoy. `fetch_metrics.sh` toma dos muestras y publica un
> bloque `# Tasas`: **evalúa el status con ese bloque**. Los MB de swap residentes y
> los GB de egress acumulados son contexto, no señal.
>
> El 2026-08-03 esto disparó un **WARN falso**: 380 MB de swap residual de semanas
> atrás cruzaron el viejo umbral "cualquier uso", cuando `pswpout` era ~0, `oom_kill`
> 0, cache hit 100% y load 0.04 — el swap de hecho estaba **drenando** (380 → 336 MB
> en unas horas). Un `oom_kill > 0` o un swap-out sostenido sí son presión real;
> la residencia no.
>
> Si el bloque de tasas dice **"las dos muestras son idénticas"**, el endpoint no
> refrescó: repite con `METRICS_INTERVAL=120`. **No** interpretes esa corrida como
> tasas en cero.

> **Swap-out: la tasa sola es churn.** El kernel puede paginar de ida y vuelta sin
> que falte memoria. Solo hay presión si el swap-out **y** la residencia crecen a la
> vez. El 2026-08-05 se mandó WARN por 8.9 MB/min mientras la residencia venía
> **bajando** (379 → 336 → 304 MB en dos días): era una ráfaga del pico matutino,
> no acumulación. `oom_kill > 0` es CRIT por sí solo, sin más condiciones.

> **Egress: el status sale del promedio de vida contra la cuota, nunca de la
> muestra.** El promedio se deriva del contador acumulado ÷ uptime (ambos vienen en
> el scrape, cero estado que guardar) y es estable por construcción. La muestra de
> 90s se imprime solo como contexto: se midió su varianza el 2026-08-05 en tres
> momentos igualmente tranquilos y dio **0.52, 1.14 y 11.77 GB/día** — 20× de
> dispersión, hasta 12× el promedio. **No pongas un umbral de "salto" sobre esa
> ventana**: es un generador de falsos WARN, y ya se intentó. Un re-fetch en loop se
> caza en los api logs (`queries.md` #9b), no en un delta de 90s.
>
> Historia de este umbral, para no repetirla: la primera versión era `Egress: sin
> salto vs día previo` (no medible con una muestra). La segunda fue `OK < 1 GB/día`,
> calibrada con **una sola muestra de 316 s** que dio 0.52 — y la base real resultó
> ser 2.36 GB/día, así que habría disparado WARN todos los días. La tercera es esta:
> anclada a la cuota del plan, que es un número estable y con significado real.

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
