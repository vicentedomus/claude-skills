import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "scripts"))


def filas():
    return json.load(open(os.path.join(AQUI, "fixtures", "mes.json"), encoding="utf-8"))


def literal_js(script, nombre):
    """Extrae el arreglo `const NOMBRE = [ ... ];` y lo parsea como JSON (falla si no es JS/JSON válido)."""
    m = re.search(r"const " + nombre + r" = \[\n(.*?)\n\];", script, re.S)
    assert m, f"no se encontró {nombre}"
    cuerpo = m.group(1).strip().rstrip(",")
    return json.loads("[" + cuerpo + "]") if cuerpo else []
