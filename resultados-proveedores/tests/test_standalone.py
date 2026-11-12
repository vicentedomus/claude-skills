import unittest
from ._util import AQUI  # noqa: F401  (agrega scripts/ al path)
import build_standalone as S


class Standalone(unittest.TestCase):
    def test_embebe_js_con_diagonales_invertidas_intactas(self):
        js = 'const re = /\\d+/; const s = "a\\nb";'
        html = ('<link rel="stylesheet" href="../../styles.css">'
                '<script src="../../deck.js"></script><img src="../../assets/logo.png">')
        out = S.empaquetar(html, "a{content:'\\201C'}", js, "QUJD")
        self.assertIn(js, out)
        self.assertIn("content:'\\201C'", out)
        self.assertIn("data:image/png;base64,QUJD", out)
        self.assertNotIn("../..", out)


if __name__ == "__main__":
    unittest.main()
