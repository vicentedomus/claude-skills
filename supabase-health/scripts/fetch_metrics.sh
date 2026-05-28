#!/usr/bin/env bash
# Trae las métricas de infraestructura del proyecto Supabase de Domus desde la
# Metrics API (Prometheus) y extrae las series clave a un resumen compacto.
#
# Auth: HTTP Basic  service_role : $SUPABASE_SERVICE_ROLE_KEY
# El key NUNCA se commitea; viene como variable de entorno del entorno cloud.
#
# Uso:   bash scripts/fetch_metrics.sh
# Salida: resumen filtrado en stdout; respuesta cruda completa en $RAW (tmp).

set -uo pipefail

PROJECT_REF="ifqwrtheakkvgezewxqx"
URL="https://${PROJECT_REF}.supabase.co/customer/v1/privileged/metrics"
RAW="$(mktemp -t supabase-metrics.XXXXXX)"

if [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  echo "⚠️  SUPABASE_SERVICE_ROLE_KEY no está definido en el entorno." >&2
  echo "    Omite la sección de métricas de infra y reporta solo introspección de BD." >&2
  exit 3
fi

http_code=$(curl -sS -o "$RAW" -w '%{http_code}' \
  --user "service_role:${SUPABASE_SERVICE_ROLE_KEY}" \
  "$URL")

if [[ "$http_code" != "200" ]]; then
  echo "⚠️  Metrics API devolvió HTTP $http_code (¿key inválido/rotado?)." >&2
  echo "    Respuesta cruda en: $RAW" >&2
  exit 4
fi

echo "# Resumen de métricas de infra — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# Respuesta cruda completa (todas las series): $RAW"
echo

# Series de interés (ver references/metrics.md). grep -E tolerante: si Supabase
# renombró algo, inspecciona $RAW y ajusta el patrón / la tabla del reference.
PATTERN='node_cpu_seconds_total|node_load1|node_load5'
PATTERN+='|node_disk_(reads|writes)_completed_total|node_disk_(read|written)_bytes_total'
PATTERN+='|node_filesystem_(avail|size)_bytes'
PATTERN+='|node_memory_(MemAvailable|MemTotal|SwapFree|SwapTotal)_bytes'
PATTERN+='|node_network_transmit_bytes_total'
PATTERN+='|pg_stat_database_(num_backends|blks_hit|blks_read)'
PATTERN+='|max_connections|burst|balance'

# Excluye comentarios HELP/TYPE para reducir ruido.
grep -E "$PATTERN" "$RAW" | grep -vE '^#' || {
  echo "(no se encontraron las series esperadas; revisa $RAW y ajusta el patrón)"
}

echo
echo "# Total de series en la respuesta: $(grep -vcE '^#' "$RAW")"
