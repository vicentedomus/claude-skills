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

**Los ids del constructor llevan fuente desde el PR #482:** `srd:<FUENTE>:<Nombre>`. Antes eran
`srd:<Nombre>` a secas, y con los seis libros del brew dentro **36 nombres chocan con XMM**: 57 de
las 2.143 filas compartían identidad y `find` devolvía la que `readdirSync` hubiera puesto primero.
El daño no era cosmético — el Kraken de FM es CR 26 y el de XMM 23, o sea que el generador reserva
un número y el semáforo cobra otro.

Así que **lo que escribas nuevo va cualificado**. `findMonstruo` sigue aceptando el formato viejo
(degrada a búsqueda por nombre) para no romper los encuentros ya guardados, pero no te apoyes en
eso.

```bash
# El pool del constructor. Enseña TODOS los homónimos: elige por fuente, no por orden.
node -e "
const b = require('./data/5e/bestiary.json');
for (const nom of ['Scarecrow','Ankheg','Kraken']) {
  const hits = b.filter(m => m.name === nom);
  console.log(nom, '->', hits.map(m => 'srd:'+m.source+':'+m.name+' (CR '+m.cr+')').join(' | ') || 'NO EXISTE');
}
"
```

Para Flee, Mortals! el filtro es `m.source === 'FleeMortals'`, siempre.

### El camino vanilla sigue en el formato viejo

`bestiarioRowById` (`srd-adapters.js`) resuelve `srd:<Nombre>` **sin** fuente. Lo consumen los
pines y las fichas vanilla, no el constructor de encuentros — así que ahí sí manda el orden de
carga. Si una locación lleva pin a un monstruo con homónimos, compruébalo y **dilo**:

```bash
node -e "
global.window = global;
global.SRD5E = { bestiary: JSON.parse(require('fs').readFileSync('data/5e/bestiary.json','utf8')), items: [] };
global.ccSourceEnabled = () => true;
const A = require('./srd-adapters.js');
for (const id of ['srd:Scarecrow','srd:Specter']) {
  const r = A.bestiarioRowById(id);
  console.log(id, '->', r ? r.nombre + ' (' + r.fuente + ') CR ' + r.cr : 'NO RESUELVE');
}
"
```

**El catálogo se mueve, así que córrelo — no lo cites.** La versión anterior de esta guía decía que
`srd:Scarecrow` resolvía a `WttHC`. Medido el 2026-09-13, `Scarecrow` ya solo está en `XMM` (y en
`MM` dentro de `bestiary-aventuras.json`): la fuente de aquella nota desapareció del pool y la nota
se quedó. Cualquier fuente concreta escrita aquí caduca igual.

**Y `cf_statblock` no es un id**: es `{"kind":"compendium","name":"Wereraven","source":"RHW"}`. Ya
lleva la fuente dentro, así que no tiene el problema — pero escribirlo como string tampoco falla:
se guarda y la ficha sale vacía.

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
