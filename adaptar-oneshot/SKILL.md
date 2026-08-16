---
name: adaptar-oneshot
description: "Adaptar una aventura oficial de D&D ya escrita (one-shot, módulo, capítulo de antología) para dirigirla en una mesa concreta de QuestKeep. Activa cuando el usuario diga: prepara la one-shot, vamos a correr <nombre de módulo>, adapta esta aventura, dirijo <módulo> el <día>, qué one-shot corremos, prepara Book of the Raven / Axeholm / Sunless Citadel, o pida ajustar una aventura oficial a su party. NO es para inventar mundo propio — eso es dnd-worldbuilder y halo-session-prep."
---

# Adaptar one-shot oficial

Toma una aventura **ya escrita por otra persona** y la deja lista para dirigir en una mesa
concreta. Dos entregables, en este orden de importancia:

1. **La guía interactiva (artifact)** — es lo que el DM lee en la mesa. Es EL entregable.
2. **El respaldo en QuestKeep** — encuentros, lugares, NPCs, items y mapas dados de alta, para
   tirar dados y llevar el estado.

Anunciar al iniciar: **"Activando adaptar-oneshot."** Responder siempre en **español mexicano
simple** (ver §6).

## Esto NO es halo-session-prep

`halo-session-prep` **genera** mundo: inventa NPCs, usa el compendio como musa, expande la
campaña. Esta skill **adapta** contenido que ya existe, y varias de sus reglas se invierten:

| | halo-session-prep (generar) | adaptar-oneshot (adaptar) |
|---|---|---|
| Nombres propios | nuevos, coherentes con la cultura local | **verbatim del módulo** |
| `faccion` / `familia` | «nunca se copian tal cual» | **se copian tal cual** |
| Topónimos | se descartan | **son el contenido** |
| NPCs nuevos por sesión | 2, para expandir el mundo | **0** — el módulo trae su elenco |
| Fuente de verdad | el grafo del compendio | **el texto del libro** |

> **La regla de «limar el setting» de `dnd-worldbuilder/references/npc.md` NO aplica aquí.**
> El valor está justo en que sea Candlekeep y el Scarlet Sash. Limarlo destruye el producto.

---

## Paso 0 · Clasificar la fuente — ANTES de tocar nada

**Este es el paso que más caro sale saltarse.** Antes de escribir una fila o una línea de guía,
clasifica la aventura:

| Tipo | Cómo se reconoce | Cómo se dirige |
|---|---|---|
| **Gazetteer** | Locaciones numeradas (C1–C17, A1–A30), un plano, un elenco | **Se navega**: saltas al cuarto donde están los jugadores |
| **Guion** | Escenas encadenadas, «después de esto los personajes…» | **Se avanza**: una escena lleva a la siguiente |
| **Mixto** | Un tramo lineal + una locación con llaves (lo más común) | Guion hasta la locación, gazetteer dentro |

**Imponer la forma equivocada destruye el producto aunque los datos estén perfectos** — y no se
nota revisando la base de datos, solo intentando dirigir la partida.

Para un gazetteer, la unidad es **la sala**, no el acto. El artifact lleva un índice de salas y
un plano clicable; el plan de sesión se queda solo con lo que es global (la espina, los
disparadores, la red de pistas).

**Dilo en voz alta al DM:** «Esta aventura es un gazetteer de N estancias, así que la guía va a
ser un índice navegable, no una secuencia».

---

## Paso 1 · Presupuesto de encuentros — el PRIMER chequeo, no el último

Antes de enamorarte de una aventura, mide si le cabe a la party. **No cites el presupuesto de
memoria: léelo del repo**, que es lo que la app va a pintar.

```bash
grep -n "XP_BUDGET" -A6 react/encuentros/data.ts   # tabla 'XP Budget per Character' (XDMG)
```

Es **por personaje**; multiplícalo por el número de PJs. Nivel 3: Bajo 150 · Medio 225 · **Alto
400** → una party de 2 tiene **300 / 450 / 800**. La etiqueta la calcula
`react/encuentros/logic.ts` (`xpBudget`, `difficulty`), y por encima de Alto pinta **«Sobre
High»**.

**Lee el nivel declarado en el TEXTO de la locación, no del rango del libro.** *Axeholm* está en
un libro de nivel 1-6 y su primera línea dice *«balanced for characters of 5th level»*.

**Ojo con los módulos que escalan por tamaño de party** («one ghoul plus one additional ghoul for
each member of the party»): con 2 PJs dan números distintos a los que uno supone. En *Axeholm*,
forzar la puerta de A1 daba **9 ghouls = 1.800 XP**, 2,3× el presupuesto Alto de una party de 2.

Si no cabe, dilo y ofrece alternativas **antes** de invertir horas. Ese chequeo descartó Axeholm
y validó Book of the Raven en la misma conversación.

---

## Paso 2 · Verificar acceso al contenido

```bash
# ¿está el texto completo en el lector?
node -p "require('./data/books/index.json').map(l=>l.id).join(', ')"
```

Si falta el libro, importarlo son **dos pasos** (`docs/etl-guia.md §4b`): el texto con
`import-books.mjs` Y el bestiario con `import-5etools.mjs` + `patch-5e-data.mjs`. Saltarse el
segundo deja enlaces muertos: solo el texto de Candlekeep deja **448 de sus 728** `@creature` sin
resolver.

Verifica que las criaturas del capítulo resuelvan antes de prometer nada. Detalle y script en
`references/verificar-contenido.md`.

---

## Paso 3 · La guía interactiva — EL entregable

Un artifact autosuficiente. **Contrato de contenido**: la guía tiene estas partes, en este orden.

| # | Parte | Qué lleva |
|---|---|---|
| 1 | **Premisa** | 3-5 líneas: qué creen los jugadores que van a hacer vs. qué es realmente |
| 2 | **Glosario** | TODA palabra de setting o reglas que la guía use después |
| 3 | **Índice fijo** | Rail lateral en pantalla grande, barra pegajosa con chips en celular |
| 4 | **El orden** | Los momentos numerados, cada uno con **el texto literal para leer en voz alta** |
| 5 | **El elenco** | Quién es cada NPC, cómo suena, qué hace |
| 6 | **Las locaciones** | Plano clicable + índice; cada una con su lectura y su mecánica |
| 7 | **Tablas operativas** | Qué dispara qué · la red de pistas · las tablas del módulo (d6, etc.) |
| 8 | **Encaje con la party** | Lo que sale de cruzar el módulo con las hojas de los PJs |

### Tres reglas de contenido, no negociables

**A · Cada momento trae su texto literal.** Una caja «Lee esto en voz alta» con el párrafo
completo. Nunca «lees el gancho» sin el gancho.

**B · Ninguna referencia queda colgando.** Si la guía dice «ese lore», el lore está en la página.
Si dice «vistani», el glosario lo define. Prohibido apoyarse en que el DM ya leyó el módulo.

> **Auto-chequeo obligatorio antes de publicar:** relee la guía preguntándote, en cada
> sustantivo propio y cada referencia deíctica («ese», «el gancho», «la tabla»), *¿esto está
> resuelto en esta página?* Cada «no» es un bug.

**C · Distinguir lo que sabe el DM de lo que sabe la mesa.** Marca explícitamente lo que es
información tuya («Lo que tú sabes y ellos no»).

### Diseño

Hereda el design system del repo (`style.css`: `--bg #131313`, oro `#ffbf00`). **Nunca cargues
fuentes de Google**: el CSP de los artifacts bloquea CDNs y caen en silencio — stacks del sistema.
Si incrustas el plano, va en base64 (el CSP también bloquea imágenes remotas).

**Carga `huashu-design` y `artifact-design`** antes de escribir el HTML.

---

## Paso 4 · Respaldo en QuestKeep

El artifact es para leer; la app es para **tirar dados y llevar estado**. Ambos deben existir.

### Prerequisito silencioso: el overlay

`qkEffectiveSchema` (`app.js`) = `FORM_SCHEMAS[section]` + `overlay.customFields` de
`entity_schemas`. **Un `cf_*` que no esté declarado en el overlay de esa campaña se guarda y no
se ve.** Compruébalo antes de escribir, y crea el overlay si falta.

```sql
select campaign_slug, section from entity_schemas where campaign_slug = '<slug>';
```

### Checklist de alta

- [ ] **`encuentros`** — uno por cada pelea, con `monsters` (`[{"id":"srd:<Name>","count":N}]`),
      `party` con los ids de los PJs, y en `descripcion`: **si es evitable, qué la dispara, y el
      presupuesto XP contra el de la party**
- [ ] **`lugares`** — para un gazetteer, una fila por locación con `cf_lugar_padre` apuntando al
      contenedor. El índice de salas lo **deriva el motor** (`inverseRelationsHTML`), no se
      mantiene a mano
- [ ] **`npcs`** — el elenco del módulo, nombres verbatim, con `cf_statblock` resuelto
- [ ] **`items`** — los que importan, con lo que hacen
- [ ] **`quests`** — la quest paraguas
- [ ] **`mapa_nodos`** — carpeta por módulo + versión DM (`players_visible=false`) + versión de
      jugadores (`players_visible=true`). `compendioCrear` nace todo visible: el reparto lo haces tú
- [ ] **`mapa_pines`** — un pin `kind:'linked'`, `linkType:'lugar'` por locación. Coordenadas en
      fracciones 0-1. Es lo que vuelve el plano una interfaz
- [ ] **`session_plans`** — solo lo global: espina, disparadores, red de pistas, notas de DM

**Nunca escribas en Supabase sin confirmación del DM.**

### Statblocks: 2024 primero, 2014 como respaldo

Decisión del DM (2026-08-15). Resuelve contra `data/5e/bestiary.json`; solo si el monstruo no
está ahí, cae a `bestiary-aventuras.json`.

**Los caminos de la app prefieren ediciones opuestas** y hay que declararlo:

| Camino | Busca en | Prefiere |
|---|---|---|
| Lector de libros | ADV + bestiary | 2014 (la que cita el módulo) |
| `cf_statblock` y encuentros | solo `bestiary` | 2024 |

Cuando las dos versiones existan **y difieran**, anótalo en la ficha del encuentro: el DM va a
leer el read-aloud de una edición y tirar los dados de la otra. Y desambigua por fuente:
`srd:<Name>` toma la primera coincidencia por nombre, y ese orden **no es determinista**.

---

## Reglas duras

### 1 · Idioma: español mexicano simple

Chrome, notas y explicaciones en español mexicano. **Nombres propios y términos de reglas en
inglés verbatim** (Chalet Brantifax, Scarlet Sash, *charm of heroism*, Sacred Flame). Los
read-aloud van como paráfrasis en español, marcada como tal.

**Auditar, no confiarse.** Lista y comando en `references/espanol-mexicano.md`.

Y no es solo vocabulario: **es la sintaxis**. Traducir la prosa florida del módulo frase por
frase es fiel y a la vez ilegible para leer en voz alta. Frases cortas, una idea por frase.

### 2 · Modelar al grano del módulo, no más fino

17 salas → 17 `lugares` con pin. Pero los textos completos NO se duplican en el plan de sesión:
viven en su ficha. Y una locación con 3 cuartos irrelevantes no necesita 3 filas.

### 3 · Un campo vacío puede ser una decisión del autor

El barón de *Book of the Raven* va **sin statblock** porque el módulo dice que su espíritu no
puede manifestarse. Un default por vocación habría convertido un duelo en un encuentro.
**No autocompletes sin decirlo.**

---

## Trampas de verificación

Las tres tumbaron una verificación real y dieron falsos negativos:

| Trampa | Síntoma | Regla |
|---|---|---|
| `text-transform: uppercase` | «la etiqueta no aparece» pero el contenido sí | `innerText` de Chromium **aplica** la transformación: compara insensible a mayúsculas |
| Presencia ≠ visibilidad | «el modal sigue encima» tras arreglarlo | Exige `getBoundingClientRect()` con área > 0: las pestañas ocultas siguen en el DOM |
| Hidratación diferida | `DATA.mapas` devuelve `[]` | Espera con `waitForFunction`, no lo leas justo tras `#app.visible` |

**Verifica contra el motor, no contra tu lectura del motor:**

```bash
node -e "const ES=require('./entity-schema.js'); …ES.effectiveSchema(baseline, overlay, {isDM:true})"
node -e "const A=require('./srd-adapters.js'); A.bestiarioRowById('srd:Scarecrow')"
```

Eso destapó que `srd:Scarecrow` resuelve a `WttHC`, no a `XMM` como yo había escrito.

---

## Señales de que la vas a regar

- Escribiste el plan de sesión antes de clasificar la fuente
- La guía dice «el gancho», «ese lore» o «la tabla» sin que estén en la página
- Usaste una palabra de setting sin definirla en el glosario
- Escribiste `cf_*` sin haber leído el overlay de esa campaña
- Diste por buena una fila porque el `INSERT` no dio error
- Te sonó natural escribir «coger», «vosotros» o «desván»
- Estás inventando un NPC que el módulo ya trae

**Todas significan: regresa al paso que te saltaste.**

## Referencias

- `references/verificar-contenido.md` — comprobar que el módulo y sus criaturas resuelven
- `references/espanol-mexicano.md` — lista de peninsularismos y comando de auditoría
- `references/artifact-guia.md` — contrato del artifact, con el caso de Book of the Raven
- Mapeo real y medido: `questkeep/docs/superpowers/specs/2026-08-15-mapeo-manual-book-of-the-raven.md`
