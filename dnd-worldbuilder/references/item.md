# Item — Referencia de Entidad

Un item = **mecánica prestada de un catálogo** (nunca inventada) + **alma reskin-eada**. Gemelo del
NPC (que ancla a statblock). Ver `catalogos.md` para la resolución ETL/homebrew.

## Arquitectura: tipo vs instancia

| Capa | Qué es | Dónde |
|------|--------|-------|
| **TIPO — oficial** | la lista vigente (mecánica) | ETL `questkeep/data/5e/items.json` (1941) |
| **TIPO — homebrew** | tu item customizado, reutilizable | `items_catalog` (`es_homebrew`, `base`) |
| **INSTANCIA** | lo que un PJ trae en la bolsa | tabla `items` (`personaje_id`/`npc_portador_id`, `custom_data`) |

**Flujo del DM:** catálogo (ETL) → tomas un base → lo modificas (reskin) → se guarda como **homebrew** →
los jugadores lo añaden a su bolsa (instancia) e interactúan.

## Campos

### Identidad del item (el TIPO homebrew → `items_catalog`)

`base` (oficial ETL) · `nombre` (reskin) · `tipo`/`rareza`/`requiere_sintonizacion` (heredados del
base) · y la **narrativa en `descripcion`** como bloque estructurado:

1. **Apariencia** — cómo se ve en reposo. El detalle ancla visual.
2. **Sensación** — qué pasa al tocarlo/usarlo (peso, temperatura, sonido). *Se siente* mágico sin decir
   "es mágico".
3. **Historia** — de dónde viene, con huecos (invita a investigar).
4. **Costo/consecuencia** — el gancho: qué cuesta usarlo.

### Instancia en la bolsa (`items.custom_data`)

`cf_item_base` (ref al catálogo, `catalogos.md`) · `cf_cargas` (number, tracker de usos) ·
`cf_origen_lugar`/`cf_origen_quest` (rel, 🎩) · `cf_inspiracion` (🎩). Base: `personaje_id`/
`npc_portador_id` (portador), `conocido_jugadores`.

**Deprecado (coexistencia):** el blob `descripcion`/`contenido_html` de la instancia → la narrativa vive
en el tipo; la instancia lleva lo interactivo/campaña.

## Flujo de resolución (regla dura)

**match_directo** (item oficial del ETL tal cual) **>** **reskin** (fila homebrew en `items_catalog`,
`es_homebrew=true`, `base`=oficial, **misma mecánica**, flavor nuevo) **>** **nunca inventar**. Si falta
un oficial (raro, el ETL trae commons/artifacts), darlo de alta verbatim primero. Cada tesoro lleva
`flag: match_directo | reskin` + el flavor si aplica.

## Ejemplo (reskin)

Base ETL: *Ring of Protection*. Reskin homebrew:
> **Apariencia:** anillo de hierro con una grieta que lo recorre y cambia de posición al mirarlo.
> **Sensación:** pesa de más; al ponértelo el dedo se enfría y escuchas la *intención* de palabras.
> **Historia:** los enanos de [lugar limado] lo llaman "la Opinión"; perteneció a un juez que nunca
> erró — hasta que erró.
> **Costo:** susurra juicios; si le prestas atención, se intensifican.

Mecánica = idéntica al Ring of Protection (base). Cero stats inventadas.

## Checklist de calidad

- [ ] `base` apunta a un oficial real del ETL (mecánica nunca inventada)
- [ ] Apariencia con detalle ancla sensorial (no solo visual)
- [ ] La magia se siente, no se anuncia
- [ ] Tiene costo/consecuencia (gancho)
- [ ] Historia con huecos
- [ ] `flag` match_directo|reskin correcto; reskin conserva la mecánica del base
- [ ] Instancia: portador/origen/cargas sembrados donde apliquen
