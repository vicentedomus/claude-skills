import unittest
from ._util import AQUI  # noqa: F401  (agrega scripts/ al path)
import aggregates as A

C3 = "x" * 300  # callout de 3 líneas
FILA = A.ROW_PX


class Paginar(unittest.TestCase):
    def test_usa_el_minimo_de_slides_y_reparte(self):
        casos = {0: [0], 9: [9], 10: [4, 6], 12: [5, 7], 19: [9, 10], 25: [8, 9, 8], 40: [7, 9, 9, 9, 6]}
        for n, esperado in casos.items():
            r = A.paginar([FILA] * n, C3)
            self.assertEqual(sum(r), n, n)
            self.assertEqual(len(r), len(esperado), (n, r))

    def test_nada_se_sale(self):
        for n in range(1, 60):
            r = A.paginar([FILA] * n, C3)
            self.assertLessEqual(r[0] * FILA, A.PAGE_PX - A.THEAD_PX - 3 * 34 - 22)
            for k in r[1:]:
                self.assertLessEqual(k * FILA, A.PAGE_PX - A.THEAD_PX)

    def test_callout_corto_deja_mas_filas(self):
        self.assertEqual(A.paginar([FILA] * 10, "corto"), [10])

    def test_callout_largo_empuja_filas(self):
        self.assertEqual(len(A.paginar([FILA] * 9, "x" * 600)), 2)

    def test_filas_con_mensaje_ocupan_mas(self):
        sin = {"obs_texto": None}
        con = {"obs_texto": "La casa no está habitada, se dejó en espera", "obs_tipo": "Observación"}
        larga = {"obs_texto": "x" * 300, "obs_tipo": "Observación"}
        self.assertEqual(A.alto_fila(sin), FILA)
        self.assertGreater(A.alto_fila(con), FILA)
        self.assertGreater(A.alto_fila(larga), A.alto_fila(con))
        # 9 filas sin mensaje caben en un slide; con mensaje ya no.
        self.assertEqual(len(A.paginar([A.alto_fila(sin)] * 9, C3)), 1)
        self.assertEqual(len(A.paginar([A.alto_fila(con)] * 9, C3)), 2)

    def test_una_fila_enorme_va_sola_sin_ciclarse(self):
        self.assertEqual(A.paginar([5000, FILA], C3), [1, 1])
