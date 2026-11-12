#!/usr/bin/env python3
"""
aggregates.py — deriva TODOS los números del deck "Análisis de Resultados" por
proveedor a partir del JSON crudo de UNA consulta SQL (la del paso 2 de la skill,
que SIEMPRE trae el desarrollo via join a proyectos).

Por qué existe: evita dos clases de error que ya nos mordieron a mano —
  (1) inferir el desarrollo del número de lote (el lote NO es único entre
      desarrollos: Capri 48 ≠ Adara 48). Aquí el desarrollo viaja en cada fila.
  (2) aritmética de los ángulos de la dona y de los promedios de KPI.

Días hábiles = días entre semana (lun–vie), SIN descontar festivos (convención
del deck). bizdays(d1,d2) cuenta los días hábiles en el intervalo (d1, d2]:
mismo día = 0, coherente con la resta de fechas.

Entrada: un archivo JSON = arreglo de filas con estas llaves (de la consulta):
  set            'recibido' | 'terminado' | 'pendiente'
  desarrollo     nombre del proyecto (p.ej. "Adara", "Capri")
  lote           número de lote (int)
  zona           nombre de zona
  prioridad      'Verde' | 'Amarillo' | 'Rojo'
  recurrencia    bool
  estatus        texto
  fecha_reporte / fecha_programacion / fecha_terminado   'YYYY-MM-DD' | null
  descripcion    texto
  id, entrega, obs_texto, obs_fecha   (opcionales; la consulta los trae desde 2026-11, spec 009)

Uso:
  python aggregates.py datos.json [--prev datos_mes_anterior.json] [--hoy YYYY-MM-DD]

--prev: filas (mismas llaves) de los TERMINADOS del mes anterior, para el
        comparativo de KPIs (baseline en vivo).
--hoy:  fecha de corte para "días esperando" de los pendientes (default: hoy).
"""
import argparse, html, json, math, sys
from datetime import date, timedelta

CAT = [f"var(--cat-{i})" for i in range(1, 10)]  # paleta de la dona


def d(s):
    return date.fromisoformat(s) if s else None


def bizdays(d1, d2):
    """Días hábiles (lun-vie) en (d1, d2]. Mismo día = 0. Si faltan datos: None."""
    if not d1 or not d2:
        return None
    step = 1 if d2 >= d1 else -1
    n = 0
    cur = d1
    while cur != d2:
        cur += timedelta(days=step)
        if cur.weekday() < 5:
            n += step
    return n


def bizdays_sin_pausa(d1, d2, pausas, corte=None):
    """Días hábiles en (d1, d2] sin contar los que el ticket estuvo en pausa por causa del cliente (spec 009).
    pausas = [[desde, hasta|None], …] en 'YYYY-MM-DD'; cada pausa quita sus días hábiles (desde, hasta] que caen en el
    tramo. Una pausa abierta (hasta None) se corta en `corte` (la fecha de corte del deck; si falta, en d2)."""
    total = bizdays(d1, d2)
    if total is None or not pausas:
        return total
    for desde, hasta in pausas:
        a = max(d1, d(desde))
        b = min(d2, d(hasta) if hasta else (corte or d2))
        if b > a:
            total -= bizdays(a, b)
    return max(0, total)


def prog_days(r, corte=None):
    """Días hábiles de programación (reporte → programación), sin pausas."""
    return bizdays_sin_pausa(d(r["fecha_reporte"]), d(r["fecha_programacion"]), r.get("pausas") or [], corte)


def cuenta_en_kpis(r):
    """Un ticket marcado «No cuenta para indicadores» (spec 009) sale de los KPI y su comparativo, no de lote/zona."""
    return not r.get("excluir")


def lote_label(r):
    return f"{r['desarrollo']} {r['lote']}"


def jstr(s):
    """Escapa una cadena para literal JS entre comillas dobles (texto corto: nombres, zonas)."""
    return (s or "").replace("\\", "\\\\").replace('"', '\\"').strip()


def js_val(v):
    """Literal JS seguro para cualquier valor: JSON (saltos de línea y comillas escapados) y sin ningún `<`
    (va como \\u003c): un `</script>` o `<!--<script>` en una observación cerraría o desarmaría el <script>
    del deck. JS y JSON.parse lo leen idéntico."""
    return json.dumps(v, ensure_ascii=False).replace("<", "\\u003c")


def extras(r):
    """Campos opcionales de la tarjeta (spec 009): etiqueta de entrega y la última observación."""
    obs = {"texto": r["obs_texto"].strip(), "fecha": r.get("obs_fecha")} if (r.get("obs_texto") or "").strip() else None
    return {"entrega": bool(r.get("entrega")), "obs": obs}


def fila_terminado(r):
    """Una fila del arreglo TERMINADOS (modales de KPI) como literal JS."""
    return js_val({
        "lote": lote_label(r), "zona": r["zona"], "desc": (r["descripcion"] or "").strip(),
        "prioridad": r["prioridad"], "recurrencia": bool(r.get("recurrencia")),
        "reporte": r["fecha_reporte"], "programacion": r["fecha_programacion"],
        "terminado": r["fecha_terminado"], "diasTrabajo": work_days(r),
        "diasProg": prog_days(r), **extras(r),
    }) + ","


def fila_ticket(r):
    """Una fila del arreglo TICKETS (recibidos; modales por lote y zona) como literal JS."""
    return js_val({
        "lote": lote_label(r), "desc": (r["descripcion"] or "").strip(), "prioridad": r["prioridad"],
        "recurrencia": bool(r.get("recurrencia")), "estatus": r["estatus"], "reporte": r["fecha_reporte"],
        "programacion": r["fecha_programacion"] or None, "terminado": r["fecha_terminado"] or None,
        "zona": r["zona"], **extras(r), "excluido": bool(r.get("excluir")),
    }) + ","


def badge_entrega(r):
    """Etiquetas de la fila de «Pendientes de Programar»: Entrega y, si está pausado por el cliente, Pausado."""
    return ((' <span class="badge entrega">Entrega</span>' if r.get("entrega") else "")
            + (' <span class="badge pausado">Pausado</span>' if r.get("estatus") == "Pausado" else ""))


def dias_esperando(r, hoy):
    """Días hábiles desde el reporte hasta el corte, sin los días en pausa."""
    return bizdays_sin_pausa(d(r["fecha_reporte"]), hoy, r.get("pausas") or [], hoy)


def grupo(rows, keyfn):
    g = {}
    for r in rows:
        g.setdefault(keyfn(r), 0)
        g[keyfn(r)] += 1
    # orden por conteo desc, luego alfabético para estabilidad
    return sorted(g.items(), key=lambda kv: (-kv[1], kv[0]))


def dona(pairs, total):
    """Imprime conic-gradient + leyenda para una lista [(label, count)]."""
    print("  conic-gradient:")
    acc = 0.0
    stops = []
    for i, (lab, n) in enumerate(pairs):
        start = acc
        acc += n / total * 360
        stops.append(f"    {CAT[i % 9]}  {start:.2f}deg  {acc:.2f}deg,")
    # último cierra en 360 exacto
    if stops:
        stops[-1] = stops[-1].rsplit("deg", 2)[0] + "deg  360deg,"
    print("\n".join(s.rstrip(",") if i == len(stops) - 1 else s
                     for i, s in enumerate(stops)))
    print("  leyenda:")
    for i, (lab, n) in enumerate(pairs):
        print(f'    <div class="item"><span class="swatch" style="background:{CAT[i%9]}"></span>{lab} — {n} ({n/total*100:.1f}%)</div>')


def work_days(r):
    """Días hábiles de trabajo (programación → terminado), con piso en 0.
    Un tiempo de trabajo negativo no es válido: pasa cuando la fecha de
    programación se capturó DESPUÉS del cierre (dato mal registrado). En ese
    caso se cuenta como 0 (mismo día). Ver footnote del deck."""
    dt = bizdays_sin_pausa(d(r["fecha_programacion"]), d(r["fecha_terminado"]), r.get("pausas") or [])
    return max(0, dt) if dt is not None else None


def kpis(term):
    term = [r for r in term if cuenta_en_kpis(r)]
    trab = [work_days(r) for r in term]
    prog = [prog_days(r) for r in term]
    trab = [x for x in trab if x is not None]
    prog = [x for x in prog if x is not None]
    n = len(term)
    sev = {p: sum(1 for r in term if r["prioridad"] == p) for p in ("Verde", "Amarillo", "Rojo")}
    rec = sum(1 for r in term if r.get("recurrencia"))
    return {
        "n": n,
        "trabajo": round(sum(trab) / len(trab), 1) if trab else None,
        "prog": round(sum(prog) / len(prog), 1) if prog else None,
        "sev_pct": {p: round(100 * c / n) for p, c in sev.items()} if n else {},
        "rec_pct": round(100 * rec / n) if n else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("datos")
    ap.add_argument("--prev")
    ap.add_argument("--hoy")
    a = ap.parse_args()
    rows = json.load(open(a.datos, encoding="utf-8"))
    hoy = d(a.hoy) if a.hoy else date.today()

    recibidos = [r for r in rows if r.get("set") == "recibido"]
    terminados = [r for r in rows if r.get("set") == "terminado"]
    pendientes = [r for r in rows if r.get("set") == "pendiente"]

    print("=" * 70, "\nRECIBIDOS:", len(recibidos), "| TERMINADOS:", len(terminados),
          "| PENDIENTES:", len(pendientes), "\n" + "=" * 70)

    # ---- POR LOTE (slide 4) ----
    print("\n## SLIDE 4 — POR LOTE  (total =", len(recibidos), ")")
    porlote = grupo(recibidos, lote_label)
    dona(porlote, len(recibidos))
    print("  filas tabla:")
    for lab, n in porlote:
        des, lo = lab.rsplit(" ", 1)
        print(f'    <tr class="clickable" data-group="lote" data-key="{lab}"><td>{des}</td><td class="num">{lo}</td><td class="num">{n}</td></tr>')

    # ---- POR ZONA (slide 6) ----
    print("\n## SLIDE 6 — POR ZONA  (total =", len(recibidos), ")")
    porzona = grupo(recibidos, lambda r: r["zona"])
    dona(porzona, len(recibidos))
    print("  filas tabla:")
    for lab, n in porzona:
        print(f'    <tr class="clickable" data-group="zona" data-key="{lab}"><td>{lab}</td><td class="num">{n}</td></tr>')

    # ---- KPIs (slide 9) ----
    print("\n## SLIDE 9 — KPIs (terminados del mes)")
    k = kpis(terminados)
    print(f"  terminados: {k['n']}")
    print(f"  Tiempo de Trabajo (días háb): {k['trabajo']}")
    print(f"  Tiempo de Programación (días háb): {k['prog']}")
    print(f"  Severidad: {k['sev_pct']}")
    print(f"  Recurrencia: {k['rec_pct']}%")
    if a.prev:
        kp = kpis(json.load(open(a.prev, encoding="utf-8")))
        print("  --- baseline mes anterior ---")
        print(f"  trabajo {kp['trabajo']} | prog {kp['prog']} | sev {kp['sev_pct']} | rec {kp['rec_pct']}%")

    # ---- arrays JS ----
    print("\n## ARRAY TERMINADOS (slide 9, modales de KPI)")
    for r in terminados:
        if cuenta_en_kpis(r):
            print("  " + fila_terminado(r))

    print("\n## ARRAY TICKETS (slides 4/6/7, modal por zona/lote — recibidos)")
    for r in recibidos:
        print("  " + fila_ticket(r))

    # ---- PENDIENTES (slide nuevo; auto-pagina si son muchos) ----
    print("\n## SLIDE PENDIENTES (backlog actual, ordenado por antigüedad)")
    pend = [(r, dias_esperando(r, hoy)) for r in pendientes]
    pend.sort(key=lambda x: -(x[1] or 0))
    MAXROWS = 14  # caben ~14 filas legibles en un slide de 1080px
    nslides = max(1, math.ceil(len(pend) / MAXROWS))
    per = math.ceil(len(pend) / nslides) if pend else 0
    if nslides > 1:
        print(f"  ⚠ {len(pend)} pendientes > {MAXROWS}: PAGINAR en {nslides} slides (~{per} c/u).")
        print(f"    Slide 1 lleva el callout; los de continuación van titulados")
        print(f"    'Pendientes de Programar — continuación' y SIN callout.")
    def _row(r, dh):
        cls = " dias-alto" if (dh or 0) >= 60 else (" dias-medio" if (dh or 0) >= 30 else "")
        e = lambda s: html.escape(str(s or "").strip())
        return (f'    <tr><td>{e(lote_label(r))}{badge_entrega(r)}</td><td>{e(r["zona"])}</td><td>{e(r["descripcion"])}</td>'
                f'<td class="num">{r["fecha_reporte"]}</td><td class="num{cls}">{dh}</td></tr>')
    for i in range(nslides):
        if nslides > 1:
            print(f"  --- slide {i+1} de {nslides} ---")
        for r, dh in pend[i * per:(i + 1) * per]:
            print(_row(r, dh))
    print(f"  (corte días esperando = {hoy}, días hábiles)")


if __name__ == "__main__":
    main()
