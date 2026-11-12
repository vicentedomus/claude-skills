import json, os, subprocess, sys, tempfile, unittest
from ._util import AQUI, literal_js
import aggregates as A

BASE = {"desarrollo": "Adara", "zona": "Cocina", "prioridad": "Verde", "recurrencia": False, "descripcion": "x"}
FILAS = [
    # terminado normal: prog vie 2 → mar 6 oct (2 hábiles), trabajo 6→9 (3)
    {**BASE, "set": "terminado", "lote": 1, "estatus": "Terminado", "fecha_reporte": "2026-10-02", "fecha_programacion": "2026-10-06", "fecha_terminado": "2026-10-09"},
    # terminado excluido: no debe pesar en los KPI
    {**BASE, "set": "terminado", "lote": 2, "estatus": "Terminado", "fecha_reporte": "2026-09-01", "fecha_programacion": "2026-10-01", "fecha_terminado": "2026-10-30", "prioridad": "Rojo", "excluir": True},
    # terminado con pausa en su programación: 1→15 oct = 10 hábiles, pausa 5→9 oct quita 4
    {**BASE, "set": "terminado", "lote": 3, "estatus": "Terminado", "fecha_reporte": "2026-10-01", "fecha_programacion": "2026-10-15", "fecha_terminado": "2026-10-15", "pausas": [["2026-10-05", "2026-10-09"]]},
    {**BASE, "set": "recibido", "lote": 2, "estatus": "Terminado", "fecha_reporte": "2026-10-02", "fecha_programacion": None, "fecha_terminado": None, "excluir": True},
    # pendiente pausado: aparece con su etiqueta y sin los días en pausa
    {**BASE, "set": "pendiente", "lote": 4, "estatus": "Pausado", "fecha_reporte": "2026-11-02", "fecha_programacion": None, "fecha_terminado": None, "pausas": [["2026-11-04", None]]},
]
PROSA = {"proveedor": "P", "mes": "Octubre", "anio": "2026", "kpis": {k: {"cls": "neutral", "text": "-"} for k in ("trabajo", "programacion", "severidad", "recurrencia")},
         "callout": "c", "footnote_kpi": "f", "pasos": ["p"]}


class Excluidos(unittest.TestCase):
    def test_kpis_sin_excluidos_y_sin_dias_en_pausa(self):
        k = A.kpis([r for r in FILAS if r["set"] == "terminado"])
        self.assertEqual(k["n"], 2)                     # el excluido no cuenta
        self.assertEqual(k["prog"], round((2 + 6) / 2, 1))   # vie 2 → mar 6 oct = 2; y 10 − 4 de pausa = 6
        self.assertEqual(k["sev_pct"]["Rojo"], 0)       # el rojo era el excluido

    def test_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos, prosa, out = (os.path.join(tmp, n) for n in ("d.json", "p.json", "o.html"))
            json.dump(FILAS, open(datos, "w")); json.dump(PROSA, open(prosa, "w"))
            subprocess.run([sys.executable, os.path.join(AQUI, "..", "scripts", "build_deck.py"), datos, "--prosa", prosa,
                            "--out", out, "--hoy", "2026-11-06"], check=True, capture_output=True)
            html = open(out, encoding="utf-8").read()
        term = literal_js(html, "TERMINADOS")
        self.assertEqual([t["lote"] for t in term], ["Adara 1", "Adara 3"])   # sin el excluido
        self.assertEqual(term[1]["diasProg"], 6)
        tick = literal_js(html, "TICKETS")
        self.assertTrue(tick[0]["excluido"])                 # sigue en lote/zona, marcado
        self.assertIn("2 TICKETS TERMINADOS", html)
        pend = html.split("Pendientes de Programar</div>")[1].split("</table>")[0]
        self.assertIn('<span class="badge pausado">Pausado</span>', pend)
        self.assertIn('<td class="num">2</td>', pend)        # 2→6 nov = 4 hábiles, menos el 5 y el 6 en pausa (abierta, corte 6)


if __name__ == "__main__":
    unittest.main()
