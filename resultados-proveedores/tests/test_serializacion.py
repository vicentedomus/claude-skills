import unittest
from ._util import filas
import aggregates as A


class Serializacion(unittest.TestCase):
    def test_js_val_escapa_saltos_comillas_y_cierre_de_script(self):
        texto = 'línea 1\nDice "hola" </script><b>x</b>'
        lit = A.js_val(texto)
        self.assertNotIn("\n", lit)
        self.assertNotIn("<", lit)  # ni </script> ni <!--<script>
        import json
        self.assertEqual(json.loads(lit), texto)

    def test_filas_js_son_json_valido_y_conservan_la_observacion(self):
        import json
        r = [x for x in filas() if x["set"] == "recibido"][0]
        obj = json.loads(A.fila_ticket(r).rstrip(","))
        self.assertEqual(obj["obs"]["texto"], r["obs_texto"])
        self.assertEqual(obj["obs"]["fecha"], "2026-10-20")


if __name__ == "__main__":
    unittest.main()
