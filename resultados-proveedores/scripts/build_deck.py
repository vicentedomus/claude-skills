#!/usr/bin/env python3
"""
build_deck.py — emite el deck "Análisis de Resultados" completo (11 slides) desde
el JSON de la consulta + un JSON de prosa.

Todo lo mecánico (donas, tablas, KPIs, arrays JS, paginación de pendientes) sale de
los datos con la misma aritmética de aggregates.py; el JSON de prosa solo aporta lo
que hay que redactar (cards por zona, deltas de KPI, callout, siguientes pasos).

  python build_deck.py datos.json --prev prev.json --prosa prosa.json --out ruta.html

Estructura del JSON de prosa:
  {
    "proveedor": "House", "archivo_titulo": "House",
    "mes": "Julio", "anio": "2026", "mes_prev": "junio",
    "zonas": {"Exterior": {"alert": false, "html": "<strong>…</strong>: …"}},
    "kpis": {"trabajo": {"cls": "down", "text": "…"}, …},
    "callout": "…", "footnote_kpi": "…", "pasos": ["…", "…"]
  }
Cualquier zona sin entrada en "zonas" se autogenera desde los tickets.
"""
import argparse, html, json, math, os, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aggregates import CAT, bizdays, d, grupo, jstr, kpis, lote_label, work_days

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
# La BD guarda las zonas sin acentos; el deck las muestra acentuadas.
ZONA_DISPLAY = {
    "Banos": "Baños", "Recamara Principal": "Recámara Principal",
    "Recamaras Secundarias": "Recámaras Secundarias", "Jardin": "Jardín",
    "Areas Comunes": "Áreas Comunes", "Sala/Comedor": "Sala / Comedor",
}
MAXROWS = 14  # filas legibles por slide de pendientes


def zd(z):
    return ZONA_DISPLAY.get(z, z)


def esc(s):
    return html.escape(s or "", quote=True)


def fecha_corta(iso):
    dt = d(iso)
    return f"{dt.day:02d}-{MESES[dt.month - 1]}" if dt else "—"


def donut(pairs, total, sublabel, disp=lambda x: x):
    stops, acc = [], 0.0
    for i, (lab, n) in enumerate(pairs):
        start, acc = acc, acc + n / total * 360
        fin = "360" if i == len(pairs) - 1 else f"{acc:.2f}"
        stops.append(f"            {CAT[i % 9]}  {start:.2f}deg  {fin}deg")
    grad = ",\n".join(stops)
    leg = "\n".join(
        f'          <div class="item"><span class="swatch" style="background:{CAT[i%9]}"></span>'
        f"{esc(disp(lab))} — {n} ({n/total*100:.1f}%)</div>"
        for i, (lab, n) in enumerate(pairs))
    return f"""      <div class="donut-wrap">
        <div class="donut-sublabel">{sublabel}</div>
        <div class="donut-circle" style="
          background: conic-gradient(
{grad}
          );
        ">
          <div class="donut-hole">
            <div class="total-num">{total}</div>
            <div class="total-lbl">Tickets</div>
          </div>
        </div>
        <div class="donut-legend"{' style="font-size:18px;row-gap:6px"' if len(pairs) > 10 else ''}>
{leg}
        </div>
      </div>"""


def card_auto(zona, tickets):
    """Card cualitativa por defecto: agrupa por lote y lista las incidencias."""
    porlote = {}
    for t in tickets:
        porlote.setdefault(lote_label(t), []).append(t)
    partes = []
    for lote, ts in sorted(porlote.items()):
        items = "; ".join(
            f"{esc(t['descripcion'].strip().rstrip('.')[:90])} <em>({esc(t['estatus'].lower())})</em>"
            for t in ts)
        partes.append(f"<strong>{esc(lote)}</strong>: {items}.")
    return " ".join(partes)


def slide_pendientes(pend, hoy, callout, num_from):
    """Devuelve la lista de slides de pendientes (paginados si son muchos)."""
    filas = sorted(((r, bizdays(d(r["fecha_reporte"]), hoy)) for r in pend),
                   key=lambda x: -(x[1] or 0))
    nsl = max(1, math.ceil(len(filas) / MAXROWS))
    per = math.ceil(len(filas) / nsl) if filas else 0
    out = []
    for i in range(nsl):
        cont = i > 0
        cuerpo = "\n".join(
            f'          <tr><td>{esc(lote_label(r))}</td><td>{esc(zd(r["zona"]))}</td>'
            f'<td>{esc(r["descripcion"].strip())}</td>'
            f'<td class="num">{fecha_corta(r["fecha_reporte"])}</td>'
            f'<td class="num{" dias-alto" if (dh or 0) >= 60 else (" dias-medio" if (dh or 0) >= 30 else "")}">{dh}</td></tr>'
            for r, dh in filas[i * per:(i + 1) * per])
        titulo = "Pendientes de Programar" + (" — continuación" if cont else "")
        callout_html = "" if cont else f"""      <div class="pendientes-callout">{callout}</div>
"""
        out.append(f"""  <!-- SLIDE {num_from + i} — Pendientes de Programar{' (cont.)' if cont else ''} -->
  <section class="slide dark">
    <div class="chart-title">{titulo}</div>
    <div class="pendientes-page">
{callout_html}      <table class="deck-table pendientes-table">
        <thead>
          <tr><th>Lote</th><th>Zona</th><th>Descripción</th><th class="num">Reporte</th><th class="num">Días háb.</th></tr>
        </thead>
        <tbody>
{cuerpo}
        </tbody>
      </table>
    </div>
    <div class="footnote">*Días hábiles transcurridos desde la fecha de reporte. Corte al {fecha_corta(hoy.isoformat())}-{hoy.year}.</div>
    <img class="logo br" src="../../assets/logo.png" alt="Domus">
  </section>""")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("datos")
    ap.add_argument("--prev")
    ap.add_argument("--prosa", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hoy")
    a = ap.parse_args()

    rows = json.load(open(a.datos, encoding="utf-8"))
    P = json.load(open(a.prosa, encoding="utf-8"))
    hoy = d(a.hoy) if a.hoy else date.today()
    prov, mes, anio = P["proveedor"], P["mes"], P["anio"]
    periodo = f"{mes} {anio}"
    mes_low = mes.lower()

    recibidos = [r for r in rows if r["set"] == "recibido"]
    terminados = [r for r in rows if r["set"] == "terminado"]
    pendientes = [r for r in rows if r["set"] == "pendiente"]
    k = kpis(terminados)

    dense = lambda pairs: " dense" if len(pairs) > 10 else ""
    porlote = grupo(recibidos, lote_label)
    porzona = grupo(recibidos, lambda r: r["zona"])
    assert sum(n for _, n in porlote) == len(recibidos)
    assert sum(n for _, n in porzona) == len(recibidos)

    filas_lote = "\n".join(
        f'          <tr class="clickable" data-group="lote" data-key="{esc(lab)}">'
        f'<td>{esc(lab.rsplit(" ", 1)[0])}</td><td class="num">{lab.rsplit(" ", 1)[1]}</td>'
        f'<td class="num">{n}</td></tr>' for lab, n in porlote)
    filas_zona = "\n".join(
        f'          <tr class="clickable" data-group="zona" data-key="{esc(lab)}">'
        f'<td>{esc(zd(lab))}</td><td class="num">{n}</td></tr>' for lab, n in porzona)

    # --- slide 7: cards por zona ---
    porzona_t = {z: [r for r in recibidos if r["zona"] == z] for z, _ in porzona}
    cards = []
    for lab, n in porzona:
        cfg = P.get("zonas", {}).get(lab, {})
        cuerpo = cfg.get("html") or card_auto(lab, porzona_t[lab])
        cls = " alert" if cfg.get("alert") else ""
        cards.append(f"""      <div class="zona-card{cls}">
        <div class="zc-head"><span class="zc-name">{esc(zd(lab))}</span><span class="zc-count">{n}</span></div>
        <div class="zc-body">{cuerpo}</div>
      </div>""")
    cols = min(4, max(2, math.ceil(math.sqrt(len(cards)))))
    filas_grid = math.ceil(len(cards) / cols)

    # --- slide 9: KPIs ---
    sev_top = max(k["sev_pct"], key=k["sev_pct"].get) if k["sev_pct"] else "Verde"
    nums = {
        "trabajo": f"{k['trabajo']} DÍAS" if k["trabajo"] is not None else "—",
        "programacion": f"{k['prog']} DÍAS" if k["prog"] is not None else "—",
        "severidad": f"{k['sev_pct'].get(sev_top, 0)}% {sev_top.upper()}",
        "recurrencia": f"{k['rec_pct']}%",
    }
    pills = {"trabajo": "Tiempo Promedio<br>de Trabajo",
             "programacion": "Tiempo Promedio<br>de Programación",
             "severidad": "Porcentaje de<br>Severidad de Garantías",
             "recurrencia": "Tasa de<br>Recurrencia"}
    kpis_html = "\n".join(f"""        <div class="kpi-big" data-kpi="{key}">
          <div class="num">{nums[key]}</div>
          <div class="pill">{pills[key]}</div>
          <div class="delta {P['kpis'][key]['cls']}">{P['kpis'][key]['text']}</div>
        </div>""" for key in ("trabajo", "programacion", "severidad", "recurrencia"))

    # --- arrays JS ---
    arr_term = "\n".join(
        f'  {{lote:"{jstr(lote_label(r))}", zona:"{jstr(r["zona"])}", desc:"{jstr(r["descripcion"])}", '
        f'prioridad:"{r["prioridad"]}", recurrencia:{str(bool(r["recurrencia"])).lower()}, '
        f'reporte:"{r["fecha_reporte"]}", programacion:"{r["fecha_programacion"]}", '
        f'terminado:"{r["fecha_terminado"]}", diasTrabajo:{work_days(r)}, '
        f'diasProg:{bizdays(d(r["fecha_reporte"]), d(r["fecha_programacion"]))}}},'
        for r in terminados)
    def q(v):
        return f'"{v}"' if v else "null"

    arr_tick = "\n".join(
        f'  {{lote:"{jstr(lote_label(r))}", desc:"{jstr(r["descripcion"])}", '
        f'prioridad:"{r["prioridad"]}", recurrencia:{str(bool(r["recurrencia"])).lower()}, '
        f'estatus:"{jstr(r["estatus"])}", reporte:"{r["fecha_reporte"]}", '
        f'programacion:{q(r["fecha_programacion"])}, terminado:{q(r["fecha_terminado"])}, '
        f'zona:"{jstr(r["zona"])}"}},' for r in recibidos)

    pend_slides = slide_pendientes(pendientes, hoy, P["callout"], 10)
    pasos = "\n".join(f"        <li>{p}</li>" for p in P["pasos"])

    doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Análisis de Resultados — {esc(prov)} — {periodo}</title>
<link rel="stylesheet" href="../../styles.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
<div class="deck">

  <!-- SLIDE 1 — PORTADA -->
  <section class="slide light">
    <h1 class="portada-title">
      <span class="lbl">Análisis de resultados</span>
      <span class="mes">{periodo}</span>
      <span class="proveedor">{esc(prov).upper()}</span>
    </h1>
    <div class="portada-shape"></div>
    <img class="logo tr" src="../../assets/logo.png" alt="Domus">
  </section>

  <!-- SLIDE 2 — INTRODUCCIÓN -->
  <section class="slide dark">
    <div class="deco-line top"><span class="dot"></span></div>
    <div class="intro-page">
      <h1 class="intro-title">introducción</h1>
      <p class="intro-body">
        Domus Desarrollos es una marca con más de 15 años de experiencia en el mercado
        de Mérida, un mercado que hoy está cambiando y se vuelve cada día más difícil
        el poder ser competitivo. Por lo tanto, mediante la implementación de tecnología,
        análisis de datos y acercamiento con el cliente enfocado en un modelo cálido y
        con prioridad en su satisfacción, proponemos una actualización a nuestro modelo
        de Postventa.
      </p>
    </div>
    <div class="deco-line bottom"><span class="dot"></span></div>
  </section>

  <!-- SLIDE 3 — Paso 1 intro -->
  <section class="slide light">
    <div class="step-page">
      <div class="step-heading">Paso 1 — Distribución de los Tickets por lote</div>
      <div class="step-text">
        <p>Se analizó la información de los <strong>tickets de garantía recibidos durante {mes_low}</strong>
        para detectar problemas que se repiten por desarrollo y por lote, evitando que casos
        poco comunes influyeran en los resultados.</p>
        <p>Después, los tickets se organizaron por Desarrollo y Lote, contando cuántas
        incidencias correspondían a cada vivienda. Estos datos se mostraron en una gráfica
        de porcentajes, lo que permitió identificar de manera clara en qué casos se
        concentra la mayor cantidad de tickets.</p>
      </div>
    </div>
    <div class="deco-bars">
      <div class="bar" style="height:120px"></div>
      <div class="bar" style="height:200px"></div>
      <div class="bar" style="height:280px"></div>
      <div class="bar" style="height:160px"></div>
    </div>
    <img class="logo tr" src="../../assets/logo.png" alt="Domus">
  </section>

  <!-- SLIDE 4 — Tabla y gráfica de Lote -->
  <section class="slide dark">
    <div class="chart-title">Tickets por Lote</div>
    <div class="chart-page">
{donut(porlote, len(recibidos), f"{esc(prov)} — Distribución de Tickets por Lote ({mes})")}
      <table class="deck-table{dense(porlote)}">
        <thead>
          <tr><th>Desarrollo</th><th>Lote</th><th class="num"># Tickets</th></tr>
        </thead>
        <tbody>
{filas_lote}
          <tr class="total"><td>Total</td><td></td><td class="num">{len(recibidos)}</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- SLIDE 5 — Paso 2 intro -->
  <section class="slide light">
    <div class="step-page">
      <div class="step-heading">Paso 2 — Distribución de los Tickets por zona</div>
      <div class="step-text">
        <p>Primero, se limpió y ordenó la columna Zona de la tabla de datos, ya que originalmente
        estaba capturada como texto libre. Para ello, se agruparon los diferentes nombres en un
        número menor de zonas funcionales, usando reglas basadas en palabras clave.</p>
        <p>Una vez que las zonas quedaron estandarizadas, se contó el número de
        <strong>tickets recibidos por zona durante {mes_low}</strong>. Después, se cruzó la información
        de Proveedor y Zona, lo que permitió identificar zonas donde se concentran más problemas.</p>
      </div>
    </div>
    <div class="deco-bars">
      <div class="bar" style="height:200px"></div>
      <div class="bar" style="height:140px"></div>
      <div class="bar" style="height:260px"></div>
      <div class="bar" style="height:100px"></div>
      <div class="bar" style="height:180px"></div>
    </div>
    <img class="logo tr" src="../../assets/logo.png" alt="Domus">
  </section>

  <!-- SLIDE 6 — Tabla y gráfica de Zona -->
  <section class="slide dark">
    <div class="chart-title">Tickets por Zona</div>
    <div class="chart-page">
{donut(porzona, len(recibidos), f"{esc(prov)} — Distribución de Tickets por Zona ({mes})", zd)}
      <table class="deck-table{dense(porzona)}">
        <thead>
          <tr><th>Zona</th><th class="num"># Tickets</th></tr>
        </thead>
        <tbody>
{filas_zona}
          <tr class="total"><td>Total</td><td class="num">{len(recibidos)}</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- SLIDE 7 — Análisis cualitativo por zona -->
  <section class="slide dark">
    <div class="chart-title">Análisis de Tickets por Zona</div>
    <div class="zona-cards-grid{" dense" if filas_grid >= 3 else ""}" style="grid-template-columns: repeat({cols}, 1fr); grid-template-rows: repeat({filas_grid}, minmax(0, 1fr));">
{chr(10).join(cards)}
    </div>
    <img class="logo br" src="../../assets/logo.png" alt="Domus">
  </section>

  <!-- SLIDE 8 — Paso 3 intro -->
  <section class="slide dark">
    <div style="position:absolute; top:120px; left:100px; right:100px;">
      <div class="step-heading" style="color:var(--text-light);">Paso 3 — Análisis de KPIs</div>
    </div>
    <div class="kpis-intro-grid">
      <div class="kpi-card">
        <div class="name">Tiempo Promedio de Trabajo</div>
        <div class="body"><strong>Fórmula:</strong> Fecha_Terminado − Fecha_Programación<br>
        <strong>Objetivo:</strong> Determinar el tiempo promedio que tardan trabajando los tickets, buscando optimizar este número para disminuir el costo por ticket.</div>
      </div>
      <div class="kpi-card">
        <div class="name">Tiempo Promedio de Programación</div>
        <div class="body"><strong>Fórmula:</strong> Fecha_Programación − Fecha_Reporte<br>
        <strong>Objetivo:</strong> Determinar el tiempo promedio que tardan en entrar a atender un ticket, lo cual impacta fuertemente en la opinión del cliente sobre la desarrolladora.</div>
      </div>
      <div class="kpi-card">
        <div class="name">Porcentaje de Severidad de Garantías</div>
        <div class="body"><strong>Fórmula:</strong> # de tickets por prioridad / # total de tickets<br>
        <strong>Objetivo:</strong> Determinar la gravedad de las garantías, buscando reducir la percepción negativa del cliente (proporción mucho mayor de tickets verdes contra rojos).</div>
      </div>
      <div class="kpi-card">
        <div class="name">Tasa de Recurrencia</div>
        <div class="body"><strong>Fórmula:</strong> # de tickets retrabajados / # total de tickets<br>
        <strong>Objetivo:</strong> Determinar la eficacia con la que trabajan sus garantías, ya que los retrabajos son causa principal de la molestia de los clientes y aumentan el costo de garantías para los proveedores.</div>
      </div>
    </div>
  </section>

  <!-- SLIDE 9 — KPIs grandes -->
  <section class="slide dark">
    <div class="kpis-page">
      <div class="top-title">Análisis de KPIs</div>
      <div class="total-line">{len(terminados)} TICKETS TERMINADOS</div>
      <div class="kpis-row">
{kpis_html}
      </div>
    </div>
    <div class="footnote">{P["footnote_kpi"]}</div>
    <img class="logo br" src="../../assets/logo.png" alt="Domus">
  </section>

{chr(10).join(pend_slides)}

  <!-- SLIDE {10 + len(pend_slides)} — Siguientes pasos -->
  <section class="slide light">
    <div class="next-steps">
      <h1 style="text-transform:none">Siguientes pasos</h1>
      <div class="subhead">Durante el siguiente mes:</div>
      <ul>
{pasos}
      </ul>
    </div>
    <img class="logo tr" src="../../assets/logo.png" alt="Domus">
  </section>

</div>

<!-- MODAL -->
<div class="modal-backdrop" id="ticketsModal" role="dialog" aria-modal="true" aria-labelledby="ticketsModalTitle">
  <div class="modal">
    <div class="modal-head">
      <div>
        <div class="title" id="ticketsModalTitle">—</div>
        <div class="subtitle" id="ticketsModalSubtitle">{esc(prov)} — {periodo}</div>
      </div>
      <button class="modal-close" type="button" aria-label="Cerrar">&times;</button>
    </div>
    <div class="modal-body" id="ticketsModalBody"></div>
  </div>
</div>

<script>
const DECK_META = {{ proveedor: "{jstr(prov)}", periodo: "{periodo}" }};
/* {len(recibidos)} tickets recibidos por {jstr(prov)} en {mes_low} {anio} (fecha_reporte en {mes_low}) */
const TICKETS = [
{arr_tick}
];
/* {len(terminados)} tickets TERMINADOS en {mes_low} {anio} — sustentan el slide de KPIs.
   diasTrabajo = Terminado − Programación, diasProg = Programación − Reporte, ambos en DÍAS HÁBILES. */
const TERMINADOS = [
{arr_term}
];
</script>
<script src="../../deck.js"></script>
</body>
</html>
"""
    open(a.out, "w", encoding="utf-8").write(doc)
    print(f"{a.out}: recibidos={len(recibidos)} terminados={len(terminados)} "
          f"pendientes={len(pendientes)} lotes={len(porlote)} zonas={len(porzona)} "
          f"slides_pend={len(pend_slides)}")


if __name__ == "__main__":
    main()
