import json, os, subprocess, sys, tempfile, unittest
from ._util import AQUI, filas, literal_js
import aggregates as A
import build_deck as B

PROSA = {"proveedor": "Prueba", "mes": "Octubre", "anio": "2026",
         "kpis": {k: {"cls": "neutral", "text": "—"} for k in ("trabajo", "programacion", "severidad", "recurrencia")},
         "callout": "c", "footnote_kpi": "f", "pasos": ["p"]}


def generar():
    with tempfile.TemporaryDirectory() as tmp:
        datos, prosa, out = (os.path.join(tmp, n) for n in ("d.json", "p.json", "o.html"))
        json.dump(filas(), open(datos, "w"))
        json.dump(PROSA, open(prosa, "w"))
        subprocess.run([sys.executable, os.path.join(AQUI, "..", "scripts", "build_deck.py"), datos,
                        "--prosa", prosa, "--out", out, "--hoy", "2026-11-12"], check=True, capture_output=True)
        return open(out, encoding="utf-8").read()


class Campos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = generar()
        js = cls.html
        cls.tickets = literal_js(js, "TICKETS")
        cls.term = literal_js(js, "TERMINADOS")

    def test_tickets_traen_entrega_y_obs(self):
        t1, t2 = self.tickets
        self.assertTrue(t1["entrega"])
        self.assertEqual(t1["obs"], {"texto": filas()[0]["obs_texto"], "fecha": "2026-10-20"})
        self.assertFalse(t2["entrega"])
        self.assertIsNone(t2["obs"])

    def test_terminados_traen_entrega_y_obs_y_toleran_filas_viejas(self):
        self.assertTrue(self.term[0]["entrega"])
        self.assertIsNotNone(self.term[0]["obs"])
        vieja = self.term[1]
        self.assertFalse(vieja["entrega"])
        self.assertIsNone(vieja["obs"])
        self.assertEqual(vieja["diasTrabajo"], 1)  # jue 1-oct → sáb 3-oct: solo el viernes es hábil

    def test_pendientes_con_badge_entrega_solo_si_aplica(self):
        sec = self.html.split("Pendientes de Programar</div>")[1].split("</table>")[0]
        filas_html = [l for l in sec.splitlines() if "<tr><td>" in l]
        self.assertEqual(len(filas_html), 2)
        gb = [l for l in filas_html if "Gran Bosco 150" in l][0]
        capri = [l for l in filas_html if "Capri 48" in l][0]
        self.assertIn('<span class="badge entrega">Entrega</span>', gb)
        self.assertNotIn("badge entrega", capri)

    def test_html_del_deck_no_rompe_el_script(self):
        # El fixture trae "</script>" en una observación: sin escape cerraría el bloque de datos antes de tiempo.
        self.assertEqual(self.html.count("</script>"), 2)  # el bloque de datos + el de deck.js

    def test_aggregates_imprime_los_mismos_campos(self):
        r = [x for x in filas() if x["set"] == "terminado"][0]
        obj = json.loads(A.fila_terminado(r).rstrip(","))
        self.assertTrue(obj["entrega"])
        self.assertIn("diasProg", obj)


if __name__ == "__main__":
    unittest.main()
