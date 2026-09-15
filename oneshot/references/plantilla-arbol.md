# El árbol del one-shot — plantilla, JSON y escritura

El plan modular **es** el entregable (spec 007). Esta es su forma para una sesión única, el JSON
listo para pegar y cómo se escribe sin romper nada.

## La forma

Un one-shot de 4 h. Ajusta el número de escenas con la tabla de P2; lo demás no cambia.

```
☑ SEGUIMIENTO — lo que ya pasó en mesa          [checklist]  badge «EN MESA», verde
    · un punto por BEAT de la sesión, en orden — no tareas de preparación
    · «Recibieron el encargo» · «Tienen la Losa» · «Tramo 2 cruzado» · «La puerta cayó»
    · los estados con alternativa, escritos: «Berrío: muerto / preso / huido»

▸ 1 · APERTURA — 20 min                         [texto]   badge «0:00»
    └ dónde estamos · read-aloud literal · gancho común · EL ENCARGO
      (lo de preparación —horas, party, pendientes— va en tres líneas aquí arriba)

▸ 2 · Escena A — 45 min · ✂ costura             [texto]   badge «0:20»
    ├ <Lugar>                                   [lugar]      refId → lugares
    ├ <Plano>                                   [mapa]       mapaId → mapa_nodos
    └ <Encuentro de camino>                     [encuentro]  encuentroId → encuentros

▸ 3 · Escena B — 45 min · ✂ costura             [texto]   badge «1:50»
    ├ ¿De dónde sale <la pieza>?                [rama]
    │   ├ Ruta 1 · <…>              ★ probable  [ruta]
    │   └ Ruta 2 · <…>                          [ruta]
    └ <La pieza>                                [tesoro]     refId → items

▸ 4 · CLÍMAX — 60 min · NO SE CORTA             [texto]   badge «2:50», badgeColor rojo
    ├ <Villano>                                 [npc]        refId → npcs
    ├ <Encuentro final>                         [encuentro]  estrategia `fm`
    │   ├ Villain actions 1 / 2 / 3             [texto]
    │   └ Entorno: <los 1-2 rasgos, copiados>   [texto]   ← el selector NO los guarda
    └ <Plano del clímax>                        [mapa]

▸ 5 · CIERRE — 15 min                           [texto]   badge «3:50»
    └ <Quest>                                   [quest]      refId → quests

▸ 6 · LOS DIEZ SECRETOS — referencia            [texto]   badge «DM · referencia», gris
    └ Cuáles salieron                           [checklist]  10 casillas, una por secreto
```

**El orden importa y cambió.** Los secretos iban arriba y nadie los leía en mesa: el bloque de los
diez es un ALMACÉN y va al final, mientras cada escena lleva al pie su propia sección
`SECRETOS QUE PUEDEN SALIR AQUÍ` con la semilla concreta. Y el checklist de arriba dejó de ser
«qué tengo que preparar» —eso se hace una vez, antes de empezar— para ser **el tracker de lo que la
mesa ya hizo**, que es lo que el DM mira cada veinte minutos.

### Por qué así

- **El reloj vive en el `badge`**, no en un campo nuevo. `badge` y `badgeColor` son libres por
  bloque y el DM los edita desde la tarjeta. La hora de inicio acumulada («0:20», «2:50») es más
  útil en mesa que la duración suelta: se compara con el reloj de pared sin sumar.
- **La costura de corte va en el TÍTULO**, no en el cuerpo. El DM que va tarde no va a abrir el
  bloque a leer: tiene que verlo plegado.
- **Los rasgos de entorno se copian a un `texto` hijo del encuentro.** El selector de la app
  (*Armar → reglamento FM → Entorno*) los enseña pero **no los guarda ni los aplica** (PR #526).
- **No hay tipo `secreto`.** Se retiraron los géneros narrativos a propósito (FR-012b): gancho,
  escena, secreto, pista y pivote eran cinco etiquetas para prosa con título. Los diez hechos son
  un `texto`; las semillas de hoy, un `checklist` hijo para ir marcando las que ya salieron.
- **El planeador NO renderiza markdown.** `**negritas**` sale con los asteriscos puestos. El único
  resaltado que la app entiende es la mención `@[Nombre](seccion:uuid)`, y solo en `texto`/`nota`
  —ni en `checklist`, ni en `titulo`, ni en `rama`/`ruta`—. Ver `alta-en-la-app.md` §Menciones.
- **`rama` para gazetteer también.** En una aventura de salas, la `rama` no es «qué ruta toman»
  sino «por dónde entran»; las salas cuelgan como `lugar` de la escena que las contiene.

## El JSON

Los campos por tipo, verbatim del `data-model.md`. `hijos` **siempre** presente, aunque vacío.

| `tipo` | Campos propios | Vínculo |
|---|---|---|
| `texto` | `texto` | — |
| `checklist` | `items: [{t, ok}]` | — |
| `rama` | `texto`; sus `hijos` son `ruta` | — |
| `ruta` | `texto`, `probable: bool` | — |
| `encuentro` | — | `encuentroId` → `encuentros.id` |
| `mapa` | — | `mapaId` → `mapa_nodos.id` |
| `npc` / `lugar` / `tesoro` / `quest` / `statblock` | — | `refId` |

Comunes a todos: `id` (UUID único en el plan), `tipo`, `titulo`, `hijos`, y los opcionales
`colapsado`, `badge`, `badgeColor`.

Ojo con el `texto`: **es texto plano.** Sin markdown (`**` sale literal) y con `\n` de verdad;
el único marcado que se pinta es la mención `@[Nombre](seccion:uuid)`.

```jsonc
[
  { "id": "…", "tipo": "checklist", "titulo": "SEGUIMIENTO — lo que ya pasó en mesa",
    "badge": "EN MESA", "badgeColor": "var(--green)", "hijos": [],
    "items": [
      { "t": "Recibieron el encargo · cada quien contó cómo llegó", "ok": false },
      { "t": "Tienen la pieza", "ok": false },
      { "t": "El villano: muerto / preso / huido", "ok": false }
    ] },

  { "id": "…", "tipo": "texto", "titulo": "1 · APERTURA — 20 min",
    "badge": "0:00", "hijos": [],
    "texto": "LEE EN VOZ ALTA:\n\n…\n\nEL ENCARGO — esto es lo que arranca la sesión.\n\n@[NPC](npcs:<uuid>) les pide …" },

  { "id": "…", "tipo": "texto", "titulo": "2 · Escena A — 45 min · ✂ costura",
    "badge": "0:20", "hijos": [
      { "id": "…", "tipo": "lugar",     "titulo": "…", "refId": "<uuid de lugares>", "hijos": [] },
      { "id": "…", "tipo": "mapa",      "titulo": "…", "mapaId": "<uuid de mapa_nodos>", "hijos": [] },
      { "id": "…", "tipo": "encuentro", "titulo": "…", "encuentroId": "<uuid>", "hijos": [] }
    ],
    "texto": "QUÉ LA DISPARA: …\nQUÉ QUIEREN: …\nQUÉ SE LLEVAN: …\n\nSI VAS TARDE: … ← la costura\n\nSECRETOS QUE PUEDEN SALIR AQUÍ\n· 3 · … → semilla concreta de esta escena" },

  { "id": "…", "tipo": "texto", "titulo": "3 · Escena B — 45 min · ✂ costura",
    "badge": "1:50", "hijos": [
      { "id": "…", "tipo": "rama", "titulo": "¿De dónde sale la pieza?",
        "texto": "UNA sola. No las dos.", "hijos": [
          { "id": "…", "tipo": "ruta", "titulo": "Ruta 1 · …", "probable": true, "texto": "COSTO: …\nGANA: …", "hijos": [] },
          { "id": "…", "tipo": "ruta", "titulo": "Ruta 2 · …", "texto": "COSTO: …\nGANA: …", "hijos": [] }
        ] },
      { "id": "…", "tipo": "tesoro", "titulo": "…", "refId": "<uuid de items>", "hijos": [] }
    ], "texto": "…" },

  { "id": "…", "tipo": "texto", "titulo": "6 · LOS DIEZ SECRETOS — referencia",
    "badge": "DM · referencia", "badgeColor": "var(--outline)", "colapsado": true, "hijos": [
      { "id": "…", "tipo": "checklist", "titulo": "Cuáles salieron", "hijos": [],
        "items": [{ "t": "1 · …", "ok": false }] }
    ],
    "texto": "1 · El alcalde le debe dinero al gremio.\n    DÓNDE: Escena A …\n    QUÉ CAMBIA: …" }
]
```

**Reglas de la `rama`:** nace con **dos** `ruta`; exactamente **una** hija lleva `probable: true`
(o ninguna); ninguna ruta se borra al elegir otra.

**Plegado:** `colapsado` ausente ⇒ lo decide la profundidad (plegado a partir del nivel 4).
`colapsado` presente ⇒ manda el DM y **persiste en el plan**. Pliega de nacimiento lo que es
consulta (los 10 secretos, los rasgos de entorno) y deja abierto lo que se lee en orden.

## Cómo se escribe

### 1 · El plan nace vacío en P0

```sql
insert into session_plans (campaign_slug, nombre, fecha_sesion, estado, bloques)
values ('one-shots', '<nombre del one-shot>', '<YYYY-MM-DD>', 'borrador', '[]'::jsonb)
returning id;
```

**`'[]'::jsonb` no es cosmético: es lo que lo marca como modular.** El discriminador es
`Array.isArray(bloques)` — sin bandera de versión. Un objeto (o `null`) lo manda al render legacy
de 9 slots, y el árbol no se pinta.

### 2 · El árbol se escribe entero, de una

```sql
update session_plans set bloques = $1::jsonb, updated_at = now() where id = '<uuid>';
```

Genera los `id` con `crypto.randomUUID()` (o `gen_random_uuid()`), **uno por bloque**. Si duplicas
un subárbol, regenera **todos** los ids de la copia: el motor asume pertenencia única.

### 3 · Comprobar antes de dárselo al DM

```sql
select jsonb_typeof(bloques) as forma,            -- debe decir 'array'
       jsonb_array_length(bloques) as raiz
from session_plans where id = '<uuid>';
```

Y que los vínculos resuelvan — **no son claves foráneas**, viven dentro del jsonb y la base no los
valida:

```sql
with refs as (
  select b->>'tipo' as tipo,
         coalesce(b->>'refId', b->>'encuentroId', b->>'mapaId') as ref
  from session_plans p, lateral jsonb_array_elements(p.bloques) b
  where p.id = '<uuid>'
)
select tipo, ref,
       exists(select 1 from lugares    where id::text = ref) as en_lugares,
       exists(select 1 from npcs       where id::text = ref) as en_npcs,
       exists(select 1 from encuentros where id::text = ref) as en_encuentros,
       exists(select 1 from mapa_nodos where id::text = ref) as en_mapas
from refs where ref is not null;
```

> Ese `jsonb_array_elements` solo recorre la **raíz**. Para el árbol completo hazlo recursivo o
> revísalo en Node sobre el JSON que acabas de escribir — que es lo barato, porque lo tienes en la
> mano.

Si una entidad se borra después, el bloque queda huérfano y **la UI lo dice** (FR-011). Es el
comportamiento pedido: el plan no se rompe porque alguien archive un NPC.

## Lo que el Planeador NO tiene, y es a propósito

- **Ni un control de IA.** El planeador modular no genera ni rellena nada (FR-012, SC-001b), y hay
  un test que falla si aparece un botón de generar (`react/prep/sinIA.test.tsx`). El contenido lo
  escribes tú aquí y se guarda por SQL o a mano; la app es para consultarlo y moverlo.
- **Ni `nota` ni `peligro` en el catálogo.** Retirados por decisión del DM (2026-08-26); su
  definición sigue viva solo para que los planes viejos conserven nombre y color. No los uses en un
  plan nuevo.
