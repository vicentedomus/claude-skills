# Catálogos — Resolución de statblocks e items (ETL + homebrew)

**Regla de oro: la mecánica nunca se inventa.** Todo statblock y todo item base sale de un **catálogo
oficial vigente** (el ETL) o de una fila **homebrew** derivada de uno. El grafo aporta *flavor*, jamás
stats.

---

## Dónde vive cada catálogo (¡no en las tablas Supabase que parecían!)

| | Oficial (vigente) | Homebrew (derivado) |
|---|---|---|
| **Statblocks** | ETL `questkeep/data/5e/bestiary.json` (**711**, XMM 2025) → `SRD5E.bestiary` | tabla `monstruos` (`es_homebrew`, `base`) |
| **Items** | ETL `questkeep/data/5e/items.json` (**1941**, XDMG 2024; incl. **Common/Artifact**) → `SRD5E.items` | `items_catalog` (`es_homebrew=true`, `base`) |

> ⚠️ **No usar** la tabla `monstruos` (solo ~6 filas) ni las 669 filas `DMG'24` de `items_catalog`
> (huérfanas, magic-only, sin commons) como *fuente*: son stores de homebrew/curado, no el catálogo.
> El pool real es el **ETL**. (Esto corrige los bugs de tesoros/monstruos del prep.)

La skill corre server-side con acceso al clon de questkeep → **lee los JSON del ETL directo** para
elegir. `bestiary.json` trae los statblocks NPC cotidianos: Commoner, Noble, Guard, Priest, Spy, Bandit,
Bandit Captain, Cultist, Mage, Archmage, Scout, Knight, Gladiator, Berserker, Assassin, Druid…

---

## Cómo referenciar (ref tipado)

El campo (`cf_statblock`, `cf_item_base`, monstruos de combate) guarda un ref:

- **Oficial:** `{ "kind": "official", "name": "Mage", "source": "XMM" }`
- **Homebrew:** `{ "kind": "homebrew", "id": "<uuid de monstruos/items_catalog>" }`

Filtrado del ETL: `cr` (monstruos) y `tipo` (items) son **strings compuestos**
(`"Weapon (Greatsword), Martial Weapon…"`) → filtrar por substring, no igualdad.

---

## Flujo: match_directo · reskin · alta

1. **match_directo** — hay un oficial del ETL que encaja tal cual → referenciarlo (`kind:official`).
   Sin escribir nada.
2. **reskin** — la mecánica encaja pero el flavor no → **crear fila homebrew** (`es_homebrew=true`,
   `base`=oficial del ETL, **misma mecánica**), flavor nuevo en `nombre`/`descripcion` (item) o en las
   3 capas sensoriales (statblock). Referenciar `kind:homebrew`. **Tras confirmación del DM.**
3. **falta** — se necesita un oficial que no está en el ETL (raro; el ETL ya trae commons/artifacts) →
   dar de alta la fila con su texto oficial **verbatim** (inglés) primero.

**Prioridad estricta:** match_directo > reskin > alta. Nunca inventar.

## Default de statblock por vocación (NPC)

| tipo_npc | statblock base (ETL) |
|---|---|
| Comerciante · Tabernero · Bibliotecario · Herrero | Commoner |
| Líder político | Noble |
| Religioso | Priest |
| Arcanista (incl. Místico) | Mage → Archmage |
| Cazador | Scout |
| Proxeneta · Gremio (clase Ladrones) | Spy / Bandit Captain |
| Gremio (matón) | Guard / Bandit |
| Antagonista (rol=Enemigo) | escalar: Knight / Gladiator / Assassin / Cult Fanatic |

La skill preselecciona; el DM cambia. Es el statblock **base** que un combate puede reskin-ear.
