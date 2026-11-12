#!/usr/bin/env python3
"""
build_standalone.py — empaqueta un deck de resultados-proveedores en UN solo HTML
autocontenido (CSS + deck.js + logo embebidos como data URI), para mandárselo al
usuario por chat y que abra de un doble clic, o para abrir sin servidor.

No requiere dependencias (solo la stdlib). NO necesita navegador.

Uso:
  python build_standalone.py <input.html> [output.html]

<input.html> es el deck modular (referencia ../../styles.css, ../../deck.js,
../../assets/logo.png), p.ej. juntas/resultados-proveedores/2026/mayo/grama.html.
Si no se da output, escribe /tmp/<nombre>-standalone.html.
"""
import base64, os, re, sys



def empaquetar(html, css, js, logo_b64):
    """Inlinea CSS, deck.js y logo. El reemplazo va por lambda: con una cadena, re.sub interpretaría
    cada `\` del motor (p. ej. `\n` o `\d` en deck.js) como escape y corrompería el JS o tronaría."""
    html = re.sub(r'<link rel="stylesheet" href="\.\./\.\./styles\.css">', lambda _: f"<style>\n{css}\n</style>", html)
    html = re.sub(r'<script src="\.\./\.\./deck\.js"></script>', lambda _: f"<script>\n{js}\n</script>", html)
    return html.replace("../../assets/logo.png", f"data:image/png;base64,{logo_b64}")


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python build_standalone.py <input.html> [output.html]")

    inp = os.path.abspath(sys.argv[1])
    # El deck vive en <root>/<año>/<mes>/file.html y referencia el motor con ../../
    root = os.path.abspath(os.path.join(os.path.dirname(inp), "..", ".."))
    out = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/{os.path.splitext(os.path.basename(inp))[0]}-standalone.html"

    html = empaquetar(
        open(inp, encoding="utf-8").read(),
        open(os.path.join(root, "styles.css"), encoding="utf-8").read(),
        open(os.path.join(root, "deck.js"), encoding="utf-8").read(),
        base64.b64encode(open(os.path.join(root, "assets", "logo.png"), "rb").read()).decode())

    leftover = re.findall(r"\.\./\.\.", html)
    if leftover:
        print("⚠ quedaron rutas relativas sin inlinear:", leftover, file=sys.stderr)

    open(out, "w", encoding="utf-8").write(html)
    print(f"OK → {out} ({os.path.getsize(out)//1024} KB)")


if __name__ == "__main__":
    main()
