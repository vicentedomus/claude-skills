#!/usr/bin/env bash
# validar-rondas.sh — valida la tabla de rondas de un spec contra su tasks.md.
#
# Uso:  validar-rondas.sh <dir-del-spec>            (usa <dir>/tasks.md y <dir>/rondas.md)
#       validar-rondas.sh <tasks.md> <rondas.md>
#
# Errores (exit 1):
#   - una tarea pendiente de tasks.md no está en ninguna ronda
#   - una tarea aparece en más de una ronda, o la tabla nombra una tarea que no existe
#   - una ronda depende de otra que no existe o que va después en la tabla
#   - Tipo distinto de auto|humana, ronda repetida, token no reconocido en Tareas
# Avisos (exit 0): tarea con ⚠️ en una ronda auto; ronda auto que depende de una humana;
#   ronda con más de MAX_TAREAS (9) tareas.
#
# La tabla es la primera de rondas.md cuya cabecera empieza con "| Ronda |"; necesita las
# columnas Ronda, Tareas, Depende de y Tipo (el orden de las filas = orden de ejecución).
# En Tareas van solo IDs separados por coma y rangos (T036–T044 o T036-T044).
# Las tareas ya marcadas [x] en tasks.md pueden quedar fuera de la tabla.
# Solo bash + awk (POSIX/mawk), como los scripts de spec-kit.
set -euo pipefail

if [ $# -eq 1 ] && [ -d "$1" ]; then
  tasks="$1/tasks.md"; rondas="$1/rondas.md"
elif [ $# -eq 2 ]; then
  tasks="$1"; rondas="$2"
else
  echo "uso: validar-rondas.sh <dir-del-spec> | <tasks.md> <rondas.md>" >&2; exit 2
fi
for f in "$tasks" "$rondas"; do
  [ -f "$f" ] || { echo "ERROR: no existe $f" >&2; exit 2; }
done

awk -v MAX="${MAX_TAREAS:-9}" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function err(m) { print "ERROR: " m; nerr++ }
function warn(m) { print "AVISO: " m; nwarn++ }
function asignar(id, r, tipo) {
  if (!(id in existe)) { err(r ": " id " no existe en tasks.md"); return }
  if (id in ronda_de) { err(id " está en " ronda_de[id] " y en " r); return }
  ronda_de[id] = r; tam[r]++
  if (tipo == "auto" && (id in flag)) warn(r " (auto) incluye " id ", marcada con ⚠️ en tasks.md: justifícalo o muévela a una ronda humana")
}

# ---- 1.ª pasada: tasks.md ----
FNR == NR {
  if ($0 ~ /^[ \t]*- \[[ xX]\] T[0-9]+/) {
    linea = $0; sub(/^[ \t]*- \[[ xX]\] /, "", linea)
    match(linea, /^T[0-9]+/); id = substr(linea, 1, RLENGTH)
    existe[id] = 1; orden[++n] = id
    hecha[id] = ($0 ~ /^[ \t]*- \[[xX]\]/)
    if (index($0, "⚠")) flag[id] = 1
  }
  next
}

# ---- 2.ª pasada: rondas.md ----
estado == 0 && /^\|[ \t]*Ronda[ \t]*\|/ {
  estado = 1; nc = split($0, h, "|")
  for (i = 1; i <= nc; i++) {
    c = trim(h[i])
    if (c == "Ronda") cR = i; else if (c == "Tareas") cT = i
    else if (c ~ /^Depende/) cD = i; else if (c == "Tipo") cY = i
  }
  if (!cR || !cT || !cD || !cY) { err("la tabla necesita las columnas Ronda, Tareas, Depende de y Tipo"); abort = 1; exit }
  next
}
estado == 1 && /^\|[ \t:|-]+$/ { next }
estado == 1 && /^\|/ {
  split($0, f, "|"); r = trim(f[cR]); gsub(/[*`]/, "", r)
  if (r == "") next
  if (r in pos) { err("ronda " r " repetida"); next }
  pos[r] = ++m; nombre[m] = r
  tipo = trim(f[cY]); gsub(/[*`]/, "", tipo)
  if (tipo != "auto" && tipo != "humana") err(r ": Tipo \"" tipo "\" (debe ser auto o humana)")
  tipo_de[r] = tipo

  # Depende de: IDs de ronda separados por coma, o un rango R1–R12 (se validan sus extremos).
  d = f[cD]; gsub(/[*`]/, " ", d); gsub(/—/, " ", d); gsub(/–/, "-", d)
  nd = split(d, ds, /[ ,;]+/)
  for (i = 1; i <= nd; i++) {
    if (ds[i] == "" || ds[i] == "-") continue
    ne = split(ds[i], ext, "-")
    for (j = 1; j <= ne; j++) {
      if (ext[j] == r) err(r " depende de sí misma")
      else if (!(ext[j] in pos)) err(r " depende de " ext[j] ", que no existe o va después en la tabla")
      else if (tipo == "auto" && tipo_de[ext[j]] == "humana") warn(r " (auto) depende de " ext[j] " (humana): en automode no podrá correr hasta la Ronda H")
    }
  }

  t = f[cT]; gsub(/[*`]/, "", t); gsub(/–/, "-", t); gsub(/—/, " ", t)
  nt = split(t, ts, /[ ,;]+/)
  for (i = 1; i <= nt; i++) {
    tok = ts[i]
    if (tok == "") continue
    if (tok ~ /^T[0-9]+-T?[0-9]+$/) {
      split(tok, ab, "-"); a = ab[1]; b = ab[2]; sub(/^T/, "", a); sub(/^T/, "", b)
      w = length(a); fmt = "T%0" w "d"
      if (b + 0 < a + 0) { err(r ": rango al revés " tok); continue }
      for (k = a + 0; k <= b + 0; k++) asignar(sprintf(fmt, k), r, tipo)
    } else if (tok ~ /^T[0-9]+$/) {
      asignar(tok, r, tipo)
    } else {
      err(r ": token no reconocido en Tareas: \"" tok "\" (solo IDs y rangos)")
    }
  }
  if (tipo == "auto" && tam[r] > MAX) warn(r " tiene " tam[r] " tareas (tope sugerido: " MAX "); considera partirla")
  next
}
estado == 1 && !/^\|/ { estado = 2 }

END {
  if (abort) { }
  else if (!estado) { err("no encontré la tabla (cabecera \"| Ronda |\") en rondas.md") }
  else {
    for (i = 1; i <= n; i++) {
      id = orden[i]
      if (!hecha[id] && !(id in ronda_de)) err(id " está pendiente en tasks.md y no tiene ronda")
    }
  }
  asignadas = 0; for (id in ronda_de) asignadas++
  printf "%s: %d rondas, %d tareas asignadas de %d en tasks.md, %d errores, %d avisos\n", \
    (nerr ? "FALLA" : "OK"), m, asignadas, n, nerr, nwarn
  exit (nerr ? 1 : 0)
}
' "$tasks" "$rondas"
