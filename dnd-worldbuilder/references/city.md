# Ciudad — Referencia de Entidad

Una descripción fluida (llegada → calles → detalle ancla) donde el **gobierno y la cultura se *sienten*,
no se explican**, y el **bioma/clima es personaje**. Es **heterogénea** (usa `subtipo→perfil`) y es el
**contenedor** del mundo (de aquí cuelgan npcs, establecimientos, lugares, quests).

## Núcleo (transversal)

| Campo | Tipo | Ve |
|-------|------|----|
| `nombre` · `region/reino` (`estado`) | base | 👥 |
| `cf_categoria` (**aldea · pueblo · ciudad · macropolis**) | custom select | 👥 |
| `poblacion` (número de sabor; la `categoria` da el tier) | base | 👥 |
| `cf_bioma_clima` (pantano/taiga/costa… — clima como personaje) | custom text | 👥 |
| `cf_subtipo` (dirige el perfil) | custom select | 👥 |
| `descripcion` (fluida: llegada→calles→ancla) | base | 👥 |
| `cf_detalle_ancla` (lo que la define) | custom text | 👥 |
| `cf_gobierno_cultura` (cómo se *siente* el poder/cultura) | custom text | 🎩 |
| `lider` → **rel a NPC** | base (override) | 👥 |
| `mapa_id` · `conocida_jugadores` | base | — |

> **`cf_categoria`** es la taxonomía del hexplorer (`tiendas.js`) y **determina mecánicas**: tier de
> inventario de tiendas (aldea=Common/100gp → macropolis=Very Rare/50 000gp) y radio de seguridad del
> hexplorer. **Cross-link vivo Ciudad→Establecimiento.**
>
> **`lider`** es un NPC real (el roleplay vive en su ficha). **Deprecado:** `descripcion_lider` →
> migración perezosa city-by-city cuando el session-prep llegue a esa ciudad.

## Perfiles por `cf_subtipo`

| subtipo | campos (`cf_*`) |
|---------|-----------------|
| **Portuaria** | puerto · rutas_maritimas · flota_pirateria · control_puerto |
| **Comercial** | mercados · gremios · rutas_terrestres · riqueza |
| **Fortaleza/Frontera** | defensas · guarnicion · amenaza_externa · que_protege |
| **Capital política** | corte · facciones · intriga · leyes |
| **Religiosa** | templo_mayor (rel) · deidad · peregrinos_clero · dogma |
| **Minera/Industrial** | recurso · gremios_condiciones · quien_se_enriquece |
| **Aldea rural** | aislamiento · recurso_local · supersticion · peligro_entorno |

## Situacional + conexiones

`cf_tension_latente` 🎩→ (el conflicto que hierve — semilla de quests) · `cf_faccion_dominante` (rel) ·
`cf_deidad_patrona` (rel) · `cf_inspiracion`. **Contenedor:** npcs/establecimientos/lugares (inverse) ·
quests · `lider`(npc) · facción.

## Cómo se genera

1. Fija **`cf_categoria`** (tamaño) → calibra tono.
2. Elige **`cf_subtipo`** (función) → carga su perfil.
3. Cultura/gobierno de una **comunidad-facción** del grafo + bioma de un **god-node** (`Magic as
   Industry` para Sleh) — limando setting.
4. Teje la descripción fluida con `cf_detalle_ancla` como campo propio; siembra `lider`(npc) + conexiones.
5. **Mapa:** si la campaña ya tiene un mapa de la región, la ciudad es un pin ahí; para la ciudad
   en sí, propón un `asentamiento` del catálogo del compendio con su bioma. Ver `mapas.md`.

## Checklist de calidad

- [ ] `cf_categoria` de la taxonomía del hexplorer (aldea/pueblo/ciudad/macropolis)
- [ ] `cf_subtipo` con su perfil poblado; el resto en `_hidden`
- [ ] descripción fluida (llegada→calles→ancla), ≥3 sentidos abriendo con uno inesperado
- [ ] gobierno/cultura se siente sin decirse; bioma/clima como personaje
- [ ] `lider` es rel a un NPC (no texto)
- [ ] ≥1 conexión (comercio, rivalidad, visitantes)
- [ ] `mapa_id` propuesto desde un mapa existente (campaña o catálogo), o dicho por qué no lo hay
