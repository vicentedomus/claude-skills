# Quest — Referencia de Entidad

La **espina que ata las entidades al desarrollo de la sesión** (su premisa referencia NPCs, sus escenas
ocurren en lugares, su recompensa es un item, su antagonista es un statblock). El gancho **no es**
"alguien te pide un favor" — es una situación donde **no actuar tiene consecuencias visibles**. El
**dilema moral** es lo que la hace memorable; sin dilema es fetch quest.

## Núcleo — la espina (universal)

| Campo | Tipo | Ve |
|-------|------|----|
| `nombre` · `estado`(select) | base | 👥 |
| `resumen` (el gancho, 1-2 líneas) | base | 👥 |
| `cf_premisa` (qué está en juego, quién pierde) | textarea | 🎩 |
| `cf_dilema_moral` (la decisión sin respuesta fácil) | textarea | 🎩 |
| `cf_consecuencias` (ramas: si ignoran / fallan / eligen lado) | textarea | 🎩 |
| `quest_npcs` (rel-multi: **quien pide + quien complica**) | base | mixto |
| `conocido_jugadores` | base | — |

**Deprecado:** el blob `contenido_html` → `cf_premisa`/`cf_dilema_moral`/`cf_consecuencias`.

## Situacional

| Campo | Tipo | Ve |
|-------|------|----|
| `cf_recompensa_item` (rel item) + `cf_recompensa_gp` (number) — **ambos opcionales** | rel/number | — |
| `cf_antagonista` (**statblock** / rel npc; `catalogos.md`) | statblock/rel | 🎩 |
| `cf_pistas` (múltiples caminos) · `cf_misterio_mayor` (enlaza a lore/otra quest) | textarea | 🎩→ |
| `cf_subtipo` (Investigación·Rescate·Recuperación·Eliminación·Escolta/Defensa·Otro) | select | — |
| `cf_inspiracion` | text | 🎩 |
| `lugares` · `ciudades` · `establecimientos` | base rels | mixto |

**Subtipo ligero:** el spine pesa más que la actividad; el `cf_subtipo` solo añade 1-2 campos de énfasis
(p. ej. Investigación → sospechosos/verdad_oculta/pistas_falsas; Rescate → cautivo/captor/timer).

## Cómo se genera

1. Parte de la **premisa con stakes** (no un fetch quest) — qué se pierde si no actúan.
2. Clava el **dilema moral** y las **consecuencias por rama**.
3. Ancla **≥2 NPCs** (quien pide / quien complica); siembra lugares, `cf_recompensa_item`(rel),
   `cf_antagonista`(statblock del ETL).
4. Flavor del grafo (hooks, crime-intrigue, horror pacing) — limando setting.
5. Cierra con `cf_pistas` de múltiples caminos + `cf_misterio_mayor` que enlace a lore mayor.

## Checklist de calidad

- [ ] Premisa con stakes claros (qué se pierde si no actúan)
- [ ] Tiene dilema moral / decisión sin respuesta fácil
- [ ] Conecta ≥2 NPCs (uno pide, uno complica)
- [ ] Consecuencias múltiples (no binario éxito/fracaso)
- [ ] `cf_pistas` con múltiples caminos de descubrimiento
- [ ] `cf_antagonista` resuelto contra el ETL (nunca inventado)
- [ ] `cf_misterio_mayor` conecta con algo mayor
- [ ] No es un fetch quest disfrazado
