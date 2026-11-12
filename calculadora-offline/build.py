#!/usr/bin/env python3
"""Monta o arquivo unico offline: calculadora_calhas.html
   = template.html + calhas_calc.py (motor Python) + Brython embutido."""
import pathlib
aqui = pathlib.Path(__file__).parent
tpl = (aqui / "template.html").read_text(encoding="utf-8")
py = (aqui / "calhas_calc.py").read_text(encoding="utf-8")
bry = (aqui / "vendor" / "brython-3.12.4.min.js").read_text(encoding="utf-8")
for nome, txt in (("python", py), ("brython", bry)):
    if "</script" in txt.lower():
        raise SystemExit("conteudo %s contem </script>" % nome)
html = (tpl.replace("{{PYTHON}}", py).replace("{{BRYVER}}", "3.12.4")
           .replace("{{BRYTHON}}", bry))
out = aqui / "calculadora_calhas.html"
out.write_text(html, encoding="utf-8")
print("gerado:", out, "(%.0f kB)" % (out.stat().st_size / 1024))
