# NPC cards como semilla del genoma — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que `dnd-worldbuilder` y `halo-session-prep` partan de una npc-card del compendio al generar un NPC nuevo, en vez de inventar desde cero, y dejar `specs/001-campos-elementos` alineado con lo que se midió al diseñarlo.

**Architecture:** Solo texto — `SKILL.md`, `references/*.md`, `specs/001-*` y `evals/*.json`. No hay código ejecutable. La vía card-first lee JSON plano con una línea de `jq`/`python3`: sin CLI, sin grafo, sin instalación, a diferencia de la vía `graphify` actual (que en contenedores de Claude Code web da `command not found`).

**Tech Stack:** Markdown + JSON. Verificación: evals (los tests de un repo de skills, Constitución Art. I vía `tasks.md` de spec 001) + comprobaciones mecánicas sobre los datos reales del repo `questkeep`.

## Global Constraints

- **Contenido de reglas D&D en inglés verbatim.** `cf_statblock.name` en inglés; la narrativa y los enums (`raza`, `tipo_npc`, `rol`) en español, con el vocabulario real de Halo.
- **El compendio es la musa, Supabase es la fuente de verdad.** Nada de lo que se tome del compendio se copia sin limar.
- **Limar siempre** nombres propios y tags de dominio. Regla ya vigente para el grafo (`genome.md` §4); se extiende a las cards, con `faccion`/`familia` como regla dura.
- **Nunca escribir sin confirmación del DM** (FR-005/FR-013 de spec 001).
- **La skill no queda bloqueada por QuestKeep:** si `compendium/npc-catalog.json` aún no existe, el fallback es un glob sobre los 36 shards.
- **Los evals van primero.** Se escriben, se observa que **fallan** contra el estado actual, y se edita el `SKILL.md`/reference hasta que pasan.
- **Ruta del repo de referencia:** las mediciones y los ejemplos asumen `questkeep/` clonado al lado (donde viven `compendium/` y `data/5e/`).

---

### Task 1: Evals primero — que fallen

Los tests de este repo. Se escriben antes que cualquier edición de skill, y se comprueba que el estado actual no los satisface.

**Files:**
- Modify: `dnd-worldbuilder/evals/evals.json`
- Modify: `halo-session-prep/evals/evals.json`

**Interfaces:**
- Consumes: nada.
- Produces: las assertions que las Tasks 2-5 tienen que hacer pasar. Los ids nuevos son `dnd-worldbuilder` #N+1 y assertions añadidas a la eval de prep existente (id 1).

- [ ] **Step 1: Añadir la eval de `dnd-worldbuilder`**

En `dnd-worldbuilder/evals/evals.json`, añadir al array `evals` (usando el siguiente `id` libre):

```json
{
  "id": 99,
  "prompt": "Genera un NPC nuevo para Moria: un herrero enano que trabaje en el gremio de la ciudad.",
  "expected_output": "La skill consulta primero las npc-cards del compendio filtrando por tipo_npc/raza, elige una como semilla, la descompone en los campos cf_* de la ficha y lima el setting de origen (nombre, facción, topónimos) antes de proponerla al DM.",
  "files": [],
  "assertions": [
    { "text": "Consulta las npc-cards (compendium/npc-catalog.json o los npc-cards.*.json) filtrando por tipo_npc y raza ANTES de invocar graphify o de inventar desde cero" },
    { "text": "No ejecuta `graphify` como primer paso para un NPC concreto, y no se bloquea si el CLI no está instalado" },
    { "text": "Descompone la prosa de la card en los campos estructurados cf_descripcion_fisica / cf_distintivo / cf_forma_de_hablar / cf_motivacion / cf_secreto, en vez de copiar los blobs a primera_impresion / notas_roleplay" },
    { "text": "NO copia `faccion` ni `familia` de la card: son de otro mundo (Faerûn/Barovia). Las remapea a una facción real de Halo o las deja vacías" },
    { "text": "El nombre propuesto no es el de la card salvo que el DM lo pida: se propone uno coherente con la cultura del lugar de Halo" },
    { "text": "Anota la procedencia en cf_inspiracion con el nombre de la card y su fuente" },
    { "text": "Reverifica cf_statblock contra questkeep/data/5e/bestiary.json en vez de copiar el de la card a ciegas" },
    { "text": "Si la vocación pedida no tiene cobertura en el catálogo (p. ej. Proxeneta), lo dice y cae al grafo o a los principios narrativos en vez de forzar una card que no encaja" }
  ]
}
```

- [ ] **Step 2: Añadir las assertions de `halo-session-prep`**

En `halo-session-prep/evals/evals.json`, añadir al array `assertions` de la eval **id 1** (la de «Prepara la sesión de esta semana…»):

```json
{ "text": "Para los 2 NPCs marcados 'nuevo', parte de una npc-card del compendio cuando su tipo_npc tiene cobertura en el catálogo, en vez de inventar desde cero" },
{ "text": "Cada NPC nuevo lleva 'Relación con la sesión' no vacía — la card no la aporta, la escribe la skill" },
{ "text": "Si la card traía rol 'Antagonista' o 'Informante', lo mapea a las 3 options de la app (Enemigo / Neutral) y pone el matiz real en cf_relacion_party" }
```

- [ ] **Step 3: Verificar que el JSON sigue siendo válido**

```bash
cd /workspace/claude-skills
python3 -c "import json; [json.load(open(f)) and print('OK', f) for f in ['dnd-worldbuilder/evals/evals.json','halo-session-prep/evals/evals.json']]"
```

Expected: `OK` para los dos archivos.

- [ ] **Step 4: Confirmar que las assertions FALLAN contra el estado actual**

Comprobación mecánica de que las skills todavía no dicen nada de esto:

```bash
cd /workspace/claude-skills
grep -rl "npc-card\|npc-catalog" dnd-worldbuilder/ halo-session-prep/ --include=SKILL.md --include=*.md \
  | grep -v evals/ || echo "FALLA COMO SE ESPERA: ninguna skill menciona las npc-cards"
```

Expected: `FALLA COMO SE ESPERA: ninguna skill menciona las npc-cards`

Y que el enrutamiento del genoma no tiene fila para cards:

```bash
grep -c "npc-card" dnd-worldbuilder/references/genome.md
```

Expected: `0`

- [ ] **Step 5: Commit**

```bash
git add dnd-worldbuilder/evals/evals.json halo-session-prep/evals/evals.json
git commit -m "test: evals de la via card-first para NPCs (fallan a proposito)

Los tests de un repo de skills. Cubren: consultar las npc-cards antes que
graphify, descomponer la prosa en los cf_*, NO copiar faccion/familia (son de
otro mundo), renombrar, anotar procedencia, reverificar el statblock contra el
ETL, y decir la verdad cuando la vocacion no tiene cobertura.

Verificado que fallan: hoy ninguna skill menciona las npc-cards y genome.md no
tiene fila de enrutamiento para ellas."
```

---

### Task 2: La vía card-first en `npc.md`

El corazón del cambio: cómo una card se convierte en un NPC de Halo.

**Files:**
- Modify: `dnd-worldbuilder/references/npc.md`

**Interfaces:**
- Consumes: los evals de la Task 1.
- Produces: la sección «Semilla desde npc-cards», que `genome.md` (Task 3) y `halo-session-prep/SKILL.md` (Task 4) referencian por nombre.

- [ ] **Step 1: Insertar la sección de la vía card-first**

En `dnd-worldbuilder/references/npc.md`, insertar **antes** de la sección `## Cómo se genera`:

```markdown
## Semilla desde npc-cards — la primera opción

El compendio tiene **3585 npc-cards** extraídas de 36 aventuras oficiales
(`questkeep/compendium/npc-cards.*.json`), con esquema **espejo de la tabla `npcs`**.
Para un NPC **concreto** son mejor semilla que el grafo: en vez de componer los 5 slots
desde átomos abstractos, se **descompone** una persona entera ya escrita por un
profesional. Es el patrón «desenterrar los blobs» aplicado al revés — y no necesita
`graphify` (que en contenedores de Claude Code web ni siquiera está instalado).

```
grafo:  tema abstracto  → componer 5 slots → NPC
cards:  persona entera  → descomponer en 5 slots → limar setting → NPC
```

### Retrieval

Índice plano (76 KB): `questkeep/compendium/npc-catalog.json`, con claves cortas
`n·r·t·ro·f·a·s·sl` = nombre, raza, tipo_npc, rol, faccion, avatar_url, fuente, slug.

```bash
# Candidatos por vocación × raza
python3 -c "
import json
cat = json.load(open('questkeep/compendium/npc-catalog.json'))
for x in cat:
    if x['t'] == 'Herrero' and x['r'] == 'Enano':
        print(x['sl'], '·', x['n'], '·', x['s'])
"
# La card completa (prosa incluida) sale del shard de su aventura
python3 -c "
import json
print([c for c in json.load(open('questkeep/compendium/npc-cards.LMoP.json'))
       if c['slug'] == 'kelra-ironweaver'][0])
"
```

Si `npc-catalog.json` aún no existe (lo genera QuestKeep), el fallback es un glob sobre
los 36 `npc-cards.*.json` — más verboso, mismo resultado.

**Cobertura por vocación** (para saber cuándo esta vía aplica):

```
Otro 1092 · Guardia 354 · Arcanista 339 · Religioso 290 · Criminal 290 ·
Líder político 224 · Aventurero 203 · Noble 174 · Comerciante 162 · Tabernero 127 ·
Minero 66 · Bibliotecario 57 · Herrero 55 · Cazador 45 · Gremio 38 · Granjero 36 ·
Alquimista 26
```

`Proxeneta` —muy usado en Halo (17 filas)— **no tiene ni una card**. Cuando la vocación
no está cubierta, dilo y cae al grafo o a los principios. **La card es la primera
opción, no la única.**

### De la card al genoma

| Slot | Campo de la ficha | De dónde sale en la card |
|---|---|---|
| 1 · Vocación | `tipo_npc` | `tipo_npc` (directo — es el filtro por el que la elegiste) |
| 2 · Motor | `cf_motivacion` | de `notas_roleplay`: qué persigue |
| 3 · Distintivo | `cf_distintivo` | de `primera_impresion`: el detalle/manierismo ancla |
| 4 · Twist | `cf_secreto` | de `notas_roleplay`: secretos y ganchos, dial-eado por `rol` |
| 5 · Voz | `cf_forma_de_hablar` | de `notas_roleplay`: manerismos. Si la card no lo da, **se compone** |
| — | `cf_descripcion_fisica` | de `primera_impresion`: el look breve, en acción |
| — | `cf_statblock` | el de la card, **reverificado** contra `questkeep/data/5e/bestiary.json` |
| — | `cf_inspiracion` | `"<nombre de la card> (<fuente>)"` |

**Ojo con los blobs:** una `primera_impresion` mezcla tres cosas —rasgos permanentes, una
**escena de primer encuentro** y una **frase de apertura**. Solo los rasgos mapean limpio.
La escena y la frase son material de mesa, no ficha: o se descartan o alimentan la voz.

### Qué se conserva y qué se lima

**Se conserva** (es por lo que la elegiste): `raza`, `tipo_npc`, `rol`, `estado`, y el
**átomo** de cada slot — el motor, el distintivo, la voz.

**Se lima** (misma regla que ya rige para el grafo, `genome.md` §4 — las cards son de
Faerûn y Barovia, Halo no lo es):

- `nombre` → **nuevo**, coherente con la cultura del lugar de Halo donde vive. Solo se
  conserva el original si el DM lo pide.
- `faccion` / `familia` → **regla dura: nunca se copian tal cual.** Son 903 valores
  distintos de otro mundo (`Zhentarim`, `House Freth`, `Harpers`…), casi todos
  irrepetibles. Se remapean a una facción real de Halo o se dejan vacíos.
- Prosa → reescribir descartando topónimos y nombres propios del origen, conservando el
  mecanismo narrativo.
- `avatar_url` → se conserva (modo referencia) si el retrato pega con el reskin; si no, se
  vacía.

**Lo escribe la skill, no viene de la card:** `relacion_sesion` y los cross-links sembrados
(`ciudad`, `establecimiento`, `quests`).

### `rol` — mapeo a las 3 options de la app

Las cards usan 5 valores; `FORM_SCHEMAS.npcs` de QuestKeep declara 3, y el eje fino tiene
su propio campo. Al partir de una card:

| Card | `rol` que se guarda | Dónde va el matiz |
|---|---|---|
| `Informante` | `Neutral` | `cf_relacion_party` (solo-DM) |
| `Antagonista` | `Enemigo` | `cf_relacion_party` (solo-DM) |

Mismo mapeo que aplica el buscador de NPCs de la app, para que las dos vías no diverjan
(US2/SC-002 de spec 001). Lectura que mantiene ambos campos con sentido: **`rol` = lo que
el party cree que es; `cf_relacion_party` = lo que de verdad siente.**
```

- [ ] **Step 2: Retirar `cf_clase_de_gremio`**

En la sección `### Situacional (solo cuando aplica)` de `npc.md`, quitar
`· `cf_clase_de_gremio` (select, solo `tipo=Gremio`)` de la lista, y añadir tras el párrafo:

```markdown
> **`cf_clase_de_gremio` se retiró** (2026-08-09). La clase es **del gremio**, no de la
> persona: en halo, **16 de los 24** NPCs `tipo_npc=Gremio` ya apuntan a su gremio por
> `establecimiento_id`, y el establecimiento **ya lleva la clase en su `tipo`**
> (*Hermandad de los Sellos* = `Gremio de Aventureros`; *La Sala de los Juramentos* =
> `Gremio de Ladrones`; *Mazo y Juramento* = el gremio de herreros de Moria). Un campo en
> el NPC duplicaría lo que la relación ya dice. El fold `Gremio de Ladrones → Gremio`
> **se mantiene**.
```

Y en la sección `## tipo_npc — options canónicas`, borrar la línea del fold que menciona
`cf_clase_de_gremio` y dejar solo `Gremio de Ladrones → Gremio`.

- [ ] **Step 3: Actualizar `tipo_npc` a las 18 options**

Reemplazar el bloque `## `tipo_npc` — options canónicas (13)` por:

```markdown
## `tipo_npc` — options canónicas (18)

`'' · Comerciante · Tabernero · Herrero · Alquimista · Minero · Granjero · Arcanista ·
Bibliotecario · Religioso · Guardia · Cazador · Aventurero · Criminal · Proxeneta ·
Noble · Líder político · Gremio · Otro`.

Ampliado de 13 a 18 el 2026-08-09: las 6 nuevas (`Guardia`, `Criminal`, `Aventurero`,
`Noble`, `Minero`, `Granjero`) cubren **1123 de las 3585 npc-cards (31%)**. El barrido
original de spec 001 fue sobre la tabla `npcs`, cuando las cards aún no existían. Con
estas 18, los 17 valores distintos del compendio quedan cubiertos al 100%.

- `Místico` → **fold en Arcanista**.
- `Gremio de Ladrones` → **fold en `Gremio`**; la clase la lleva el establecimiento.
```

- [ ] **Step 4: Verificar que no queda rastro del campo retirado**

```bash
cd /workspace/claude-skills
grep -rn "cf_clase_de_gremio" dnd-worldbuilder/references/npc.md \
  && echo "TODAVÍA QUEDA — revisar" || echo "OK: retirado de npc.md"
grep -c "canónicas (18)" dnd-worldbuilder/references/npc.md
```

Expected: `OK: retirado de npc.md` y `1`.

- [ ] **Step 5: Verificar que el retrieval documentado funciona de verdad**

Con `questkeep` clonado al lado, correr el fallback (que no depende del PR de QuestKeep):

```bash
python3 -c "
import json, glob
n = 0
for f in glob.glob('questkeep/compendium/npc-cards.*.json'):
    for c in json.load(open(f)):
        if c.get('tipo_npc') == 'Herrero' and c.get('raza') == 'Enano':
            n += 1
            if n <= 3: print(c['slug'], '·', c['nombre'])
print('candidatos:', n)
"
```

Expected: al menos un candidato listado. **Si devuelve 0, la sección miente** y hay que
corregir los nombres de campo antes de commitear.

- [ ] **Step 6: Commit**

```bash
git add dnd-worldbuilder/references/npc.md
git commit -m "feat(npc): la npc-card del compendio como primera semilla del genoma

Para un NPC concreto, una card es mejor semilla que el grafo: se descompone una
persona ya escrita en los 5 slots, en vez de componerlos desde atomos
abstractos. Y lee JSON plano — no necesita graphify, que en contenedores de
Claude Code web ni esta instalado.

Documenta el retrieval (con fallback si npc-catalog.json aun no existe), la
cobertura por vocacion (Proxeneta: 0 cards, ahi no aplica), la tabla
card->genoma, la regla dura de NO copiar faccion/familia, y el mapeo de rol a
las 3 options de la app.

Retira cf_clase_de_gremio: 16 de los 24 NPCs de gremio de halo ya apuntan a su
gremio y el establecimiento ya lleva la clase en su \`tipo\`. Amplia tipo_npc a
18 options."
```

---

### Task 3: Enrutamiento en `genome.md` y Paso 0.5 de `SKILL.md`

Que el método compartido sepa que las cards existen y que no dependen del CLI.

**Files:**
- Modify: `dnd-worldbuilder/references/genome.md`
- Modify: `dnd-worldbuilder/SKILL.md` (Paso 0.5)

**Interfaces:**
- Consumes: la sección «Semilla desde npc-cards» de `npc.md` (Task 2).
- Produces: la fila de enrutamiento que `halo-session-prep` (Task 4) da por hecha.

- [ ] **Step 1: Añadir la fila de enrutamiento**

En `genome.md`, en la tabla de `## Enrutamiento de extracción por combinación`, añadir
como **primera** fila (antes de «Cotidiano»):

```markdown
| **NPC concreto (cualquier vocación con cobertura)** | **npc-card** — es una persona entera, no un tema | `npc-catalog.json` filtrado por `tipo_npc`×`raza` (ver `npc.md`, «Semilla desde npc-cards») |
```

Y añadir tras las «Reglas de extracción», antes del párrafo «Si no hay grafo disponible…»:

```markdown
5. **Para NPCs, las cards van primero y no necesitan el CLI.** El grafo es un catálogo de
   *temas y arquetipos*; las 3585 npc-cards son *personas*. Para un NPC concreto se
   descompone una card; el grafo se reserva para el tono de facción, el arquetipo de un
   villano (hyperedge) y los otros 5 tipos de elemento. Las cards son JSON plano: se leen
   con `python3`/`jq` aunque `graphify` no esté instalado — que es el caso en los
   contenedores de Claude Code web.
```

- [ ] **Step 2: Ajustar el Paso 0.5 de `SKILL.md`**

En `dnd-worldbuilder/SKILL.md`, en `## Paso 0.5: Consultar el compendio (la musa) — PRIMERO`,
insertar justo bajo el párrafo introductorio y antes del punto `1.`:

```markdown
> **Para NPCs, empieza por las npc-cards, no por el grafo.** Son 3585 personas ya escritas
> con esquema espejo de la tabla `npcs`, en JSON plano: no necesitan `graphify` ni que el
> grafo esté disponible. Ver `references/npc.md` → «Semilla desde npc-cards». El grafo
> sigue siendo la vía para temas, arquetipos, facciones y los otros 5 tipos de elemento.
```

- [ ] **Step 3: Verificar la coherencia entre los tres archivos**

```bash
cd /workspace/claude-skills
for f in dnd-worldbuilder/references/genome.md dnd-worldbuilder/SKILL.md dnd-worldbuilder/references/npc.md; do
  printf '%-45s npc-card:%s\n' "$f" "$(grep -c 'npc-card' "$f")"
done
```

Expected: los tres con conteo `≥ 1`.

- [ ] **Step 4: Commit**

```bash
git add dnd-worldbuilder/references/genome.md dnd-worldbuilder/SKILL.md
git commit -m "feat: enrutar los NPCs concretos a las npc-cards antes que al grafo

El grafo es un catalogo de temas y arquetipos; las 3585 npc-cards son personas.
Faltaba la fila de enrutamiento que lo dijera — las cards estaban tejidas al
grafo (3373 nodos, comunidad 459) pero ninguna tabla mandaba a consultarlas.

Se anota ademas que las cards no dependen del CLI: son JSON plano, y graphify
no esta instalado en los contenedores de Claude Code web, donde hoy el camino
real acaba siendo inventar desde cero."
```

---

### Task 4: La regla de «2 nuevos» en `halo-session-prep`

**Files:**
- Modify: `halo-session-prep/SKILL.md` (regla dura de NPCs, y el ejemplo SQL del Paso 4a)

**Interfaces:**
- Consumes: `npc.md` → «Semilla desde npc-cards» (Task 2).
- Produces: nada que otra task consuma.

- [ ] **Step 1: Reescribir el bullet de «2 nuevos»**

En `halo-session-prep/SKILL.md`, en `#### NPCs — **mínimo 6, composición 4 existentes + 2 nuevos**`,
reemplazar el bullet `- **2 nuevos**: …` por:

```markdown
- **2 nuevos**: genera frescos invocando el flujo de `dnd-worldbuilder` con `references/npc.md`
  (la **ficha rediseñada**: `cf_descripcion_fisica`/`cf_distintivo`/`cf_forma_de_hablar`/`cf_statblock`
  + situacionales — ya **no** `primera_impresion`/`notas_roleplay`).
  **Primera opción: una npc-card del compendio** (`npc.md` → «Semilla desde npc-cards»):
  filtra por `tipo_npc`×`raza`, descompón su prosa en los `cf_*` y **lima el setting**
  (nombre nuevo; `faccion`/`familia` **nunca** se copian: son de Faerûn). Si la vocación no
  tiene cobertura —`Proxeneta` no tiene ni una card—, dilo y cae al grafo (`genome.md`) o a
  los principios. El `cf_statblock` se reverifica contra el ETL (`catalogos.md`).
```

- [ ] **Step 2: Anotar el mapeo de `rol` en el Paso 4a**

En `### 4a. Commit de NPCs nuevos a la tabla `npcs``, añadir bajo el bloque SQL, junto al
párrafo que ya explica el overlay:

```markdown
En el bloque SQL de ejemplo, cambia el literal `'tipo_npc (13 canónicas)'` por
`'tipo_npc (18 canónicas)'`. `tipo_npc` sale de las **18 options canónicas** (`npc.md`). `rol` solo admite
`Neutral`/`Aliado`/`Enemigo`: si la card de origen traía `Antagonista` o `Informante`,
mapéalo (`Antagonista`→`Enemigo`, `Informante`→`Neutral`) y pon el matiz real en
`cf_relacion_party`, que es solo-DM. Mismo mapeo que aplica el buscador de NPCs de la app,
para que las dos vías no diverjan.
```

- [ ] **Step 3: Verificar que la referencia cruzada existe**

```bash
cd /workspace/claude-skills
grep -q "Semilla desde npc-cards" halo-session-prep/SKILL.md \
  && grep -q "Semilla desde npc-cards" dnd-worldbuilder/references/npc.md \
  && echo "OK: la referencia cruzada apunta a una sección que existe" \
  || echo "ROTA — la sección referenciada no existe"
```

Expected: `OK: la referencia cruzada apunta a una sección que existe`

- [ ] **Step 4: Commit**

```bash
git add halo-session-prep/SKILL.md
git commit -m "feat(prep): los 2 NPCs nuevos parten de una npc-card

La regla ya decia «compendio primero», pero apuntaba al grafo de lore via
graphify. Ahora manda a la via card-first de npc.md, con la salida honesta
cuando la vocacion no tiene cobertura.

Anota tambien el mapeo de rol en el Paso 4a: la tabla solo admite 3 valores y
las cards traen 5."
```

---

### Task 5: Alinear `specs/001-campos-elementos`

Las tres enmiendas. Un spec cerrado que ya no describe la realidad miente con la autoridad de un documento aprobado.

**Files:**
- Modify: `specs/001-campos-elementos/design-npc.md` (§3 y §4)
- Modify: `specs/001-campos-elementos/data-model.md` (sección NPC)

**Interfaces:**
- Consumes: las decisiones de las Tasks 2-4.
- Produces: nada.

- [ ] **Step 1: `design-npc.md` §4 — 18 options y `BEG`/`Secundario`**

Reemplazar el bloque de options canónicas y la nota de cleanup por:

```markdown
**Options canónicas (18, ampliado 2026-08-09):** `'' · Comerciante · Tabernero · Herrero ·
Alquimista · Minero · Granjero · Arcanista · Bibliotecario · Religioso · Guardia · Cazador ·
Aventurero · Criminal · Proxeneta · Noble · Líder político · Gremio · Otro`.

- `Místico` → **fold en Arcanista**.
- `Gremio de Ladrones` → **fold en `Gremio`**. La **clase** la lleva el establecimiento en su
  `tipo`, no un campo del NPC — ver §3.

> **Enmienda 2026-08-09 (spec 002).** Las 13 originales se ampliaron a 18. El barrido de
> este spec fue sobre la tabla `npcs`, **anterior a las 3585 npc-cards del compendio**; las 6
> añadidas (`Guardia`, `Criminal`, `Aventurero`, `Noble`, `Minero`, `Granjero`) cubren el 31%
> de las cards. Con 13, el 62% del catálogo caería en `Otro` y el filtro por oficio del
> buscador no serviría. Evidencia nueva, no una decisión revertida.

**Cleanup de datos — enmendado 2026-08-09:** `BEG` (1) y `Secundario` (1) **sí se
reclasifican** (→ `Religioso` y `Otro`). La decisión original de dejarlos se tomó cuando
esos valores tampoco estaban en `options`, así que era indiferente; al sincronizar
`options`, dejarlos los mantendría pintados en blanco en el editor. El `Místico` (1) →
Arcanista deja de ser perezoso y se migra. Lo ejecuta la migración de QuestKeep
`sql/migraciones/2026-08-09-sync-vocabulario-npcs.sql`.
```

- [ ] **Step 2: `design-npc.md` §3 — retirar `cf_clase_de_gremio`**

Quitarlo de la lista de campos situacionales y añadir:

```markdown
> **Enmienda 2026-08-09 (spec 002): `cf_clase_de_gremio` se retira.** Cruzando
> `npcs.establecimiento_id → establecimientos` en halo, **16 de los 24** NPCs
> `tipo_npc=Gremio` ya apuntan a su gremio, y el establecimiento **ya lleva la clase en su
> `tipo`**: *Hermandad de los Sellos* (Evermere) = `Gremio de Aventureros`, *La Sala de los
> Juramentos* (Rockwood) = `Gremio de Ladrones`, *Mazo y Juramento* (Moria) = el gremio de
> herreros. La clase es del gremio, no de la persona: el campo duplicaría lo que la relación
> ya dice. Este spec lo decidió sin cruzar esa relación. El fold `Gremio de Ladrones →
> Gremio` **se mantiene**.
```

- [ ] **Step 3: `data-model.md` — tabla NPC**

- Borrar la fila `| `cf_clase_de_gremio` | Clase de gremio | select | — | solo `tipo=Gremio` |`.
- Cambiar `**baseOverrides:** `tipo_npc` options → las 13 canónicas (ver `design-npc.md`).` por:

```markdown
**baseOverrides:** `tipo_npc` options → las **18** canónicas (ver `design-npc.md` §4).
`rol` se queda en 3 (`Neutral`/`Aliado`/`Enemigo`): el eje fino es `cf_relacion_party`, que
es solo-DM, mientras `rol` es público. Ambos array viven en `app.js` (`FORM_SCHEMAS.npcs`)
— aplicados por QuestKeep en el PR del buscador de NPCs.
```

- [ ] **Step 3b: Acotar el alcance — los establecimientos NO se tocan**

`cf_clase_de_gremio` también aparece en tres sitios de **establecimientos**, encontrados por la revisión final del PR de QuestKeep: `dnd-worldbuilder/references/establishment.md:29,31,43`, `specs/001-campos-elementos/data-model.md:94` (perfil de Establecimiento) y `dnd-worldbuilder/evals/evals.json:19`.

**No se tocan.** El argumento de esta enmienda es que la clase es **del gremio, no de la persona** — eso justifica quitar el campo del NPC, y deja abierta (sin decidir) la pregunta de dónde lo guarda el gremio: hoy en su `tipo` entero (`'Gremio de Ladrones'`), o en un `cf_` como diseñó spec 001. Decidirlo expandiría el alcance a establecimientos sin que el DM lo haya revisado.

Añade la nota en `specs/001-campos-elementos/design-npc.md`, junto a la enmienda del Step 2:

```markdown
> **Alcance de la enmienda:** se retira `cf_clase_de_gremio` **del NPC**. El perfil de
> **Establecimiento** lo conserva por ahora: dónde guarda un gremio su clase —en su `tipo`
> entero, como hoy en los datos (`Gremio de Ladrones`), o en un campo aparte— es una decisión
> propia de esa entidad, y no la resuelve el argumento de esta enmienda. Queda abierta.
```

- [ ] **Step 4: Verificar que las tres enmiendas están y son coherentes**

```bash
cd /workspace/claude-skills
echo "-- cf_clase_de_gremio (debe ser 0 fuera de las notas de enmienda) --"
grep -rn "cf_clase_de_gremio" specs/001-campos-elementos/ dnd-worldbuilder/ | grep -v "se retir"
echo "-- 13 canónicas residuales (debe ser 0) --"
grep -rn "13 canónicas\|canónicas (13)" specs/001-campos-elementos/ dnd-worldbuilder/
echo "-- las 18 aparecen en los tres sitios --"
grep -lc "18" specs/001-campos-elementos/design-npc.md specs/001-campos-elementos/data-model.md dnd-worldbuilder/references/npc.md
```

Expected: las dos primeras sin resultados; la tercera lista los tres archivos.

- [ ] **Step 5: Commit**

```bash
git add specs/001-campos-elementos/design-npc.md specs/001-campos-elementos/data-model.md
git commit -m "spec(001): tres enmiendas desde el spec 002

1. cf_clase_de_gremio se retira: 16 de los 24 NPCs de gremio de halo ya apuntan
   a su gremio y el establecimiento ya lleva la clase en su tipo. Este spec lo
   decidio sin cruzar esa relacion.
2. tipo_npc de 13 a 18: el barrido original fue anterior a las npc-cards; las 6
   anadidas cubren el 31% del catalogo. Con 13, el 62% caeria en Otro.
3. BEG/Secundario si se reclasifican: «no reclasificar» se decidio cuando
   tampoco estaban en options; al sincronizarlas, dejarlos los mantiene
   pintados en blanco.

El fold Gremio de Ladrones -> Gremio se mantiene. rol sigue en 3."
```

---

## Cierre

- [ ] **Correr los evals**

Con la skill `skill-creator`:

```
/skill-creator  →  correr los evals de dnd-worldbuilder y halo-session-prep
```

Expected: las assertions nuevas de la Task 1 **pasan**. Si alguna falla, la instrucción
correspondiente en el `SKILL.md`/reference no es lo bastante explícita — se ajusta y se
vuelve a correr.

- [ ] **Verificación manual de extremo a extremo**

Con `questkeep` al lado, invocar `dnd-worldbuilder`:

> «Genera un NPC nuevo para Moria: un herrero enano que trabaje en el gremio de la ciudad.»

Comprobar a mano que la propuesta:
1. cita la card de origen y su aventura,
2. trae los `cf_*` poblados y **no** `primera_impresion`/`notas_roleplay`,
3. **no** arrastra `faccion`/`familia` de Faerûn,
4. propone un nombre nuevo,
5. resuelve `cf_statblock` contra `questkeep/data/5e/bestiary.json`,
6. y **pide confirmación antes de escribir nada**.

- [ ] **Push**

```bash
git push -u origin claude/npc-cards-como-semilla
```

Los commits se suman a la PR #56, que ya está abierta con el diseño.
