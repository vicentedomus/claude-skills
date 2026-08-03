#!/usr/bin/env bash
# Trae las métricas de infraestructura del proyecto Supabase de Domus desde la
# Metrics API (Prometheus) y extrae las series clave a un resumen compacto.
#
# Auth: HTTP Basic  service_role : $SUPABASE_SERVICE_ROLE_KEY
# El key NUNCA se commitea; viene como variable de entorno del entorno cloud.
#
# Uso:   bash scripts/fetch_metrics.sh          (toma 2 muestras, tarda ~60s)
#        METRICS_INTERVAL=30 bash scripts/...   (intervalo más corto)
# Salida: resumen filtrado en stdout; respuesta cruda completa en $RAW (tmp).
#
# Toma DOS muestras separadas por $METRICS_INTERVAL segundos porque las series que
# de verdad indican salud son CONTADORES (swap-out, egress, major faults): su valor
# absoluto es residuo acumulado desde el arranque y no dice nada. Lo accionable es
# la TASA. Con una sola muestra, 380 MB de swap residual de hace semanas se leen
# igual que presión de memoria activa (falso WARN del 2026-08-03).

set -uo pipefail

PROJECT_REF="ifqwrtheakkvgezewxqx"
URL="https://${PROJECT_REF}.supabase.co/customer/v1/privileged/metrics"
# 90s y no 60: el endpoint refresca los contadores cada ~60s, así que un intervalo
# más corto devuelve DOS VECES LA MISMA MUESTRA y todas las tasas salen 0.00 — un
# cero falso que se lee como "sin presión". El bloque de tasas lo detecta y avisa.
INTERVAL="${METRICS_INTERVAL:-90}"
RAW_PREV="$(mktemp -t supabase-metrics-prev.XXXXXX)"
RAW="$(mktemp -t supabase-metrics.XXXXXX)"

if [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  echo "⚠️  SUPABASE_SERVICE_ROLE_KEY no está definido en el entorno." >&2
  echo "    Omite la sección de métricas de infra y reporta solo introspección de BD." >&2
  exit 3
fi

scrape() {  # $1 = archivo destino
  local code
  code=$(curl -sS -o "$1" -w '%{http_code}' \
    --user "service_role:${SUPABASE_SERVICE_ROLE_KEY}" \
    "$URL")
  if [[ "$code" != "200" ]]; then
    echo "⚠️  Metrics API devolvió HTTP $code (¿key inválido/rotado?)." >&2
    echo "    Respuesta cruda en: $1" >&2
    exit 4
  fi
}

scrape "$RAW_PREV"
sleep "$INTERVAL"
scrape "$RAW"

echo "# Resumen de métricas de infra — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# Respuesta cruda completa (todas las series): $RAW"
echo

# Series de interés (ver references/metrics.md). grep -E tolerante: si Supabase
# renombró algo, inspecciona $RAW y ajusta el patrón / la tabla del reference.
PATTERN='node_cpu_seconds_total|node_load1|node_load5'
PATTERN+='|node_disk_(reads|writes)_completed_total|node_disk_(read|written)_bytes_total'
PATTERN+='|node_filesystem_(avail|size)_bytes'
PATTERN+='|node_memory_(MemAvailable|MemTotal|SwapFree|SwapTotal)_bytes'
PATTERN+='|node_vmstat_(pswpin|pswpout|pgmajfault|oom_kill)'
PATTERN+='|node_network_transmit_bytes_total'
PATTERN+='|pg_stat_database_(num_backends|blks_hit|blks_read)'
PATTERN+='|max_connections|burst|balance'

# Excluye comentarios HELP/TYPE para reducir ruido.
grep -E "$PATTERN" "$RAW" | grep -vE '^#' || {
  echo "(no se encontraron las series esperadas; revisa $RAW y ajusta el patrón)"
}

# --- Disco por mountpoint (derivado) ---------------------------------------
# La instancia tiene DOS discos (ver references/metrics.md): `/` (OS+WAL, imagen
# base de Supabase, alto ~74% por diseño) y `/data` (datos de Postgres). El status
# de disco se evalúa SOLO contra `/data`; `/` es informativo. Esto evita la falsa
# alarma de reportar el 74% del SO como si fuera la data (que pesa ~22 MB).
echo
echo "# Disco usado por mountpoint (derivado de node_filesystem_*):"
# awk portable (mawk/busybox/gawk): extrae el mountpoint sin la extensión
# match(...,arr) que solo trae gawk.
awk '
  function mp_of(s,   b) {
    b = index(s, "mountpoint=\"")
    if (b == 0) return ""
    s = substr(s, b + 12)
    return substr(s, 1, index(s, "\"") - 1)
  }
  /^node_filesystem_avail_bytes/ { mp = mp_of($0); if (mp != "") avail[mp] = $NF }
  /^node_filesystem_size_bytes/  { mp = mp_of($0); if (mp != "") size[mp]  = $NF }
  END {
    n = split("/ /data", want, " ")
    for (i = 1; i <= n; i++) {
      mp = want[i]
      if (size[mp] > 0) {
        usedpct = 100.0 * (1 - avail[mp] / size[mp])
        if (mp == "/data") label = "Postgres data  -> ACCIONABLE: umbral 75/90"
        else               label = "OS+WAL         -> informativo: alto por diseño"
        printf "  %-7s %5.1f%% usado   (%s)\n", mp, usedpct, label
      }
    }
  }
' "$RAW"

# --- Tasas (delta entre las dos muestras) ----------------------------------
# Lo ACCIONABLE. Los absolutos de arriba son residuo acumulado desde el arranque.
echo
echo "# Tasas — delta en ${INTERVAL}s (esto decide el status, no los absolutos):"
awk -v secs="$INTERVAL" '
  /^#/ { next }
  {
    if      ($0 ~ /^node_vmstat_pswpin\{/)               k = "pswpin"
    else if ($0 ~ /^node_vmstat_pswpout\{/)              k = "pswpout"
    else if ($0 ~ /^node_vmstat_pgmajfault\{/)           k = "majfault"
    else if ($0 ~ /^node_vmstat_oom_kill\{/)             k = "oom"
    else if ($0 ~ /^node_memory_SwapFree_bytes\{/)       k = "swapfree"
    else if ($0 ~ /^node_memory_SwapTotal_bytes\{/)      k = "swaptotal"
    else if ($0 ~ /^node_network_transmit_bytes_total\{/ && $0 ~ /device="ens5"/) k = "tx"
    else next
    if (FNR == NR) a[k] = $NF + 0; else b[k] = $NF + 0
  }
  END {
    MB = 1048576; per_min = 60.0 / secs
    # El egress siempre avanza en una instancia viva (replicación, exporters). Si
    # no se movió, el endpoint sirvió la misma muestra cacheada y TODAS las tasas
    # serían 0.00 falsos: mejor avisar que reportar salud inventada.
    if (b["tx"] == a["tx"]) {
      print "  ⚠️  las dos muestras son idénticas (el endpoint no refrescó en " secs "s)."
      print "      Tasas NO disponibles — repite con METRICS_INTERVAL=120. NO las leas como 0."
      exit
    }
    spo = (b["pswpout"] - a["pswpout"]) * 4096 / MB * per_min
    spi = (b["pswpin"]  - a["pswpin"])  * 4096 / MB * per_min
    tx  = (b["tx"] - a["tx"]) / MB * per_min
    u1  = (a["swaptotal"] - a["swapfree"]) / MB
    u2  = (b["swaptotal"] - b["swapfree"]) / MB
    printf "  swap-out     %7.2f MB/min  -> presion de memoria: %s\n", spo, \
      (spo > 10 ? "CRIT (>10)" : (spo > 1 ? "WARN (>1)" : "NO"))
    printf "  swap-in      %7.2f MB/min  (paginas regresando a RAM)\n", spi
    printf "  swap en uso  %7.0f -> %.0f MB  (%s)  [informativo, NO dispara status]\n", \
      u1, u2, (u2 > u1 ? "creciendo" : "drenando/estable")
    printf "  major faults %7.1f /s\n", (b["majfault"] - a["majfault"]) / secs
    printf "  oom_kill     %7d       -> %s\n", b["oom"], (b["oom"] > 0 ? "CRIT" : "ok")
    printf "  egress       %7.2f MB/min  -> ~%.2f GB/dia\n", tx, tx * 60 * 24 / 1024
  }
' "$RAW_PREV" "$RAW"

echo
echo "# Total de series en la respuesta: $(grep -vcE '^#' "$RAW")"
