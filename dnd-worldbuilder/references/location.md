# Lugar — Referencia de Entidad

Un Lugar es un **punto de interés definido por su propósito** — lo que puede suceder ahí — no por su
geografía. A menudo **nace atado a una sesión** (se crea *para* una escena). Su columna vertebral es
`cf_proposito`, no el bioma.

## subtipo → perfil (tipo heterogéneo)

Un dungeon, una cueva, un claro y "una zona de una ciudad" tienen campos distintos. Modelo: **núcleo
mínimo + `cf_subtipo` que enciende su perfil** (los `cf_*` de otros perfiles van a `_hidden`).

## Núcleo (todo lugar)

| Campo | Tipo | Ve |
|-------|------|----|
| `nombre` · `tipo`(select) · `region`(select) | base | 👥 |
| `cf_subtipo` (Dungeon/Ruina · Cueva · Naturaleza · Zona urbana · Otro) | custom select | 👥 |
| `ciudad` (rel) · `cf_lugar_padre` (rel lugares, para anidar) | rel | 👥 |
| `cf_proposito` — qué puede suceder / por qué existe (liga a quest/escena) | textarea | 🎩→ |
| `cf_atmosfera` — un gancho sensorial breve | text | 👥 |
| `estado_exploracion` · `mapa_id` · `conocido_jugadores` | base | — |

> `dentro_de` va como **campos separados** (`region` / `ciudad` / `cf_lugar_padre`), uno lleno —
> QuestKeep no soporta relación polimórfica.

**Deprecado:** `descripcion`/`descripcion_exterior`/`descripcion_interior` → `cf_atmosfera` + perfil.

## Perfiles por `cf_subtipo`

| subtipo | campos (`cf_*`) | flavor del grafo |
|---------|-----------------|------------------|
| **Dungeon/Ruina** | estructura · trampas · encuentro (**statblock**) · tesoro (rel item) · misterio 🎩 | temas dungeon/ruina |
| **Cueva** | profundidad_oscuridad · habita (**statblock**) · salida_riesgo | qué habita |
| **Naturaleza** | terreno_clima · criatura (**statblock**, marcas visibles antes) · recurso_peligro · ruta | god-node de bioma |
| **Zona urbana** | controla (rel npc/facción) · actividad · acceso · rumor | comunidad-facción/mercado |

`cf_hazard` = campo libre (menú Encounter Axis como sugerencia). Los campos statblock resuelven contra
el ETL (`catalogos.md`).

## Conexiones (universales)

`npcs` (quién ronda) · `items_magicos` (qué se halla) · `quests` (qué se juega) · la escena/sesión de
origen · `cf_inspiracion`.

## Cómo se genera

1. Parte del **propósito** (qué escena/quest lo pide), no de la geografía.
2. Elige **`cf_subtipo`** → carga su perfil.
3. Saca *flavor* del grafo por subtipo (bioma para naturaleza; facción para zona urbana) — limando setting.
4. Siembra conexiones a la escena/quest/npcs.

Un lugar con `criatura`/`encuentro` + `cf_hazard` **es un semilla de combate** pre-armada → se enchufa
al Encounter Axis (`combate.md`).

## Checklist de calidad

- [ ] `cf_proposito` no vacío (un lugar sin propósito es decorado)
- [ ] solo los `cf_*` del perfil del `subtipo` poblados; el resto en `_hidden`
- [ ] `cf_atmosfera` con ≥2 sentidos (los que generan tensión)
- [ ] si hay criatura residente, sus marcas son visibles antes (statblock del ETL)
- [ ] al menos un elemento interactivo / gancho
- [ ] misterio menor (algo sin explicación inmediata)
