import unittest
from ._util import AQUI  # noqa: F401  (agrega scripts/ al path)
import aggregates as A

C3 = "x" * 300  # callout de 3 líneas


class Paginar(unittest.TestCase):
    def test_reparto_parejo_y_completo(self):
        casos = {0: [0], 9: [9], 10: [5, 5], 12: [6, 6], 19: [9, 10], 25: [9, 8, 8], 40: [8, 8, 8, 8, 8]}
        for n, esperado in casos.items():
            self.assertEqual(A.paginar(n, C3), esperado, n)

    def test_callout_corto_deja_una_fila_mas(self):
        self.assertEqual(A.paginar(10, "corto"), [10])

    def test_callout_largo_empuja_filas(self):
        self.assertEqual(A.paginar(9, "x" * 600), [5, 4])
