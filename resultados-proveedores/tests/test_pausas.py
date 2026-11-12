import unittest
from ._util import AQUI  # noqa: F401  (agrega scripts/ al path)
from datetime import date
import aggregates as A

d = date.fromisoformat


class DiasSinPausa(unittest.TestCase):
    # Semana de referencia: lun 2-nov … vie 6-nov, lun 9-nov … vie 13-nov de 2026.
    def test_sin_pausas_es_bizdays(self):
        self.assertEqual(A.bizdays_sin_pausa(d('2026-11-02'), d('2026-11-13'), []), A.bizdays(d('2026-11-02'), d('2026-11-13')))

    def test_pausa_dentro_del_tramo(self):
        # 2→13 nov = 9 hábiles; pausa 4→6 nov quita jue 5 y vie 6 = 2
        self.assertEqual(A.bizdays_sin_pausa(d('2026-11-02'), d('2026-11-13'), [['2026-11-04', '2026-11-06']]), 7)

    def test_pausa_que_cruza_el_inicio_y_el_fin(self):
        self.assertEqual(A.bizdays_sin_pausa(d('2026-11-04'), d('2026-11-13'), [['2026-10-20', '2026-11-06']]), 5)   # quita 5 y 6
        self.assertEqual(A.bizdays_sin_pausa(d('2026-11-02'), d('2026-11-06'), [['2026-11-04', '2026-11-20']]), 2)   # solo 3 y 4

    def test_pausa_abierta_se_corta_en_el_corte(self):
        self.assertEqual(A.bizdays_sin_pausa(d('2026-11-02'), d('2026-11-13'), [['2026-11-06', None]], corte=d('2026-11-13')), 4)

    def test_fin_de_semana_dentro_de_la_pausa_no_resta_de_mas(self):
        # pausa vie 6 → lun 9: solo quita el lunes 9
        self.assertEqual(A.bizdays_sin_pausa(d('2026-11-02'), d('2026-11-13'), [['2026-11-06', '2026-11-09']]), 8)

    def test_nunca_negativo(self):
        self.assertEqual(A.bizdays_sin_pausa(d('2026-11-02'), d('2026-11-06'), [['2026-10-01', '2026-12-01']]), 0)


if __name__ == '__main__':
    unittest.main()
