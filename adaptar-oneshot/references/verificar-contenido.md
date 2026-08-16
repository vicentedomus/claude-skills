# Verificar que el módulo y sus criaturas resuelven

Antes de prometerle una aventura al DM, comprueba que la app puede servirla. Dos preguntas
distintas: ¿está el **texto**? y ¿resuelven sus **criaturas**?

## 1 · ¿Está el libro en el lector?

```bash
node -p "require('./data/books/index.json').map(l=>l.id+' — '+l.name).join('\n')"
```

Si falta, importarlo son **dos pasos** (`docs/etl-guia.md §4b`), y el segundo es el que se olvida:

1. **El texto** — `scripts/import-books.mjs`, pasando **TODOS** los ids del índice más el nuevo.
   Pasar solo el nuevo **borra el resto del índice**.
2. **El bestiario** — `scripts/import-5etools.mjs` con el flag según la edición del libro
   (`--advSources` si es legacy 2014-2021, `--refSources` si es 2024), y después **siempre**
   `node scripts/patch-5e-data.mjs`.

Medido: importar solo el texto de Candlekeep Mysteries deja **448 de sus 728** `@creature`
muertos. El error no da excepción — da enlaces que no abren.

## 2 · ¿Resuelven las criaturas del capítulo?

```python
import json, re
CAP = "Book of the Raven"   # nombre exacto de la sección
LIB = "data/books/CM.json"

def load(p):
    d = json.load(open(p))
    return d if isinstance(d, list) else (d.get('monstruos') or d.get('items') or d.get('spells') or [])

# El lector resuelve ADV primero (la edición que cita el módulo).
pool = load('data/5e/bestiary-aventuras.json') + load('data/5e/bestiary.json')
spells = load('data/5e/spells.json')

sec = next(s for s in json.load(open(LIB))['data'] if s.get('name') == CAP)
txt = json.dumps(sec, ensure_ascii=False)

for tag, p in (('creature', pool), ('spell', spells)):
    for m in {(x.group(1).strip(), x.group(2)) for x in
              re.finditer(r'\{@'+tag+r' ([^}|]+)(?:\|([^}|]*))?', txt)}:
        nom, src = m
        hit = (src and next((e for e in p if e.get('name','').lower()==nom.lower()
                             and (e.get('source','') or '').lower()==src.lower()), None)) \
              or next((e for e in p if e.get('name','').lower()==nom.lower()), None)
        print(f"  {'OK   ' if hit else 'MUERTO'} @{tag} {nom}"
              f"{' -> '+str(hit.get('source')) if hit else ''}")
```

**Los `@item` NO cuentan como muertos.** `react/books/tags.tsx` los deja fuera de `ENLAZA` a
propósito: se pintan resaltados pero no abren ficha. Reportarlos como rotos es un falso positivo.

## 3 · ¿Resuelven los ids que vas a escribir en `encuentros`?

El constructor busca **solo** en `bestiary.json` y toma la **primera coincidencia por nombre**,
sin fuente (`srd-adapters.js`). Ese orden depende de `readdirSync` y **no es determinista entre
máquinas**, así que compruébalo:

```bash
node -e "
global.window = global;
global.SRD5E = { bestiary: require('fs').readFileSync('data/5e/bestiary.json','utf8'), items: [] };
global.SRD5E.bestiary = JSON.parse(global.SRD5E.bestiary);
global.ccSourceEnabled = () => true;
const A = require('./srd-adapters.js');
for (const id of ['srd:Scarecrow','srd:Specter']) {
  const r = A.bestiarioRowById(id);
  console.log(id, '->', r ? r.nombre + ' (' + r.fuente + ') CR ' + r.cr : 'NO RESUELVE');
}
"
```

Si un nombre tiene homónimos en varias fuentes, **dilo en la ficha del encuentro**: cuál esperabas
y cuál dio.

## 4 · ¿Difieren las dos ediciones?

Cuando la criatura existe en las dos, compara antes de dar el encuentro por bueno. Casos reales de
*Book of the Raven*:

| Criatura | MM 2014 (lector) | 2024 (encuentros) | ¿Importa? |
|---|---|---|---|
| Scarecrow | 36 PV, **False Appearance** | 27 PV, sin ella | **Sí** — pierde la emboscada |
| Crawling Claw | **Turn Immunity** | sin ella | **Sí** — cambia si el clérigo las expulsa |
| Specter | CR 1 · AC 12 · 22 PV | idéntico | No |

Lo que difiera va anotado en `encuentros.descripcion`: el DM va a leer el read-aloud de una
edición y tirar los dados de la otra.
