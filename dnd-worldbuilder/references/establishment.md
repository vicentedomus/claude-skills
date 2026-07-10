# Establecimiento — Referencia de Entidad

Un **lugar comercial/servicio que se define por su dueño** (un NPC separado que el local *refleja*).
Hereda **subtipo→perfil** (por `tipo`) como Lugar. Exterior primero (el primer gancho), interior que
continúa la experiencia, un gancho de interacción, un misterio menor.

## Núcleo (todo establecimiento)

| Campo | Tipo | Ve |
|-------|------|----|
| `nombre` · `tipo`(select — dirige el perfil) · `ciudad`(rel) | base | 👥 |
| `dueno` (rel → NPC) | base | 👥 · **ancla de identidad** |
| `exterior` (sensorial breve — primer gancho) | base | 👥 |
| `interior` (continúa la experiencia) | base | 👥 |
| `cf_detalle_ancla` (el letrero, lo memorable del exterior) | custom text | 👥 |
| `cf_gancho_interaccion` (algo que tocar/probar/pedir) | custom text | 👥 |
| `mapa_id` · `conocido_jugadores` | base | — |

**`tipo`:** `Taberna · Comercio/Tienda · Herrería · Librería · Templo · Gremio · Otro`.

## Perfiles por `tipo`

| tipo | campos (`cf_*`) |
|------|-----------------|
| **Taberna** | especialidad · clientela · rumores |
| **Comercio/Herrería/Objetos mágicos** | inventario (rel items) · especialidad · precios |
| **Librería** | coleccion · pieza_rara |
| **Templo** | deidad (rel) · servicios · clero |
| **Gremio** | `cf_clase_de_gremio` (Ladrones·Mercaderes·Artesanos·Inventores·Arcano·Aventureros…) · jerarquia · fachada_vs_actividad 🎩 |

`Gremio de Ladrones` = `tipo:Gremio` + `cf_clase_de_gremio:Ladrones` (el patrón subtipo recursa).
`cf_inventario` respeta el tier de la **`categoria` de la ciudad** (`tiendas.js`: aldea=Common →
macropolis=Very Rare).

## Conexiones

`ciudad` · **`dueno`(npc)** · `empleados` (inverse npcs) · `items` (inventario) · `quests` ·
`cf_misterio` 🎩→ · `cf_inspiracion`.

## Cómo se genera

1. Ancla al **dueño** (genera/toma primero su ficha de NPC; el local lo refleja).
2. Elige **`tipo`** → carga su perfil (Gremio pide `cf_clase_de_gremio`).
3. Flavor del grafo por tipo (mercado/gremio para tiendas; deidad para templo) + la cultura de la
   `ciudad`, limando setting.
4. Sesga exterior→interior con `cf_detalle_ancla` y `cf_gancho_interaccion` como campos propios.

## Checklist de calidad

- [ ] Exterior abre con un sentido no-visual y tiene `cf_detalle_ancla`
- [ ] Interior usa ≥3 sentidos y tiene `cf_gancho_interaccion`
- [ ] La personalidad del `dueno` se siente en el espacio (sin duplicar su ficha)
- [ ] humor coherente con la cultura del lugar; un misterio menor
- [ ] perfil del `tipo` poblado; inventario acorde a la `categoria` de la ciudad
- [ ] ≥1 conexión (item/quest/rumor/rivalidad)
