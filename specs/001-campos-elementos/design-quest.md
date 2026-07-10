# Diseño — Ficha de Quest (piloto #6)

**Feature**: 001-campos-elementos · **Estado**: co-diseñado con el DM (2026-07-10) · La **espina** que ata entidades al desarrollo de la sesión.

---

## 1. Qué *es* una Quest

De `quest.md`: el gancho **no es** "alguien te pide un favor" — es una **situación donde no actuar tiene
consecuencias visibles**. El **dilema moral** es lo que la hace memorable (sin dilema es fetch quest).
Conecta a **≥2 NPCs** (uno que pide, uno que complica), pistas con **múltiples caminos**, y un
**misterio menor** que enlaza a lore mayor.

**Rol especial — el tejido conectivo:** la premisa referencia NPCs, sus escenas ocurren en lugares, su
recompensa es un item, su antagonista es un statblock. La quest es lo que convierte entidades sueltas en
**desarrollo de sesión** (es la "relación con la sesión" que da sentido a los lugares).

---

## 2. Núcleo — la espina (universal a toda quest)

| Campo | Qué es | Ve |
|---|---|---|
| `nombre` · `estado`(select) | — | 👥 |
| `resumen` (el gancho, 1-2 líneas) | text | 👥 |
| **`premisa`** ✨ (qué está en juego, quién pierde si no actúan) | textarea | 🎩 |
| **`dilema_moral`** ✨ (la decisión sin respuesta fácil) | textarea | 🎩 |
| **`consecuencias`** ✨ (ramas: si ignoran / fallan / eligen lado) | textarea | 🎩 |
| `quest_npcs` (rel-multi: **quien pide + quien complica**) | rel | mixto |
| `conocido` | — | — |

**Fuera:** el blob `contenido_html` → se parte en **premisa / dilema / consecuencias**.

---

## 3. Situacional / conexiones

| Campo | Cambio |
|---|---|
| **`recompensa`** → rel a **item** ✨ | `recompensa_gp`(texto) → item real (+ gp opcional) |
| **`antagonista`** → **statblock**/npc ✨ | quién se opone, con su stat (modelo ETL) |
| `pistas` (múltiples caminos) 🎩 · `misterio_mayor` 🎩→ | estructurados |
| `lugares` · `ciudades` · `establecimientos` · `inspiracion` | conexiones |

---

## 4. Subtipo — **ligero** (el spine pesa más que la actividad)

A diferencia de Lugar/Ciudad, aquí el **spine es universal** y el `subtipo` solo añade 1-2 campos de
énfasis (opcional, cuando aplica):

| subtipo | campos extra |
|---|---|
| Investigación / misterio | sospechosos · verdad oculta · pistas falsas |
| Rescate | cautivo · captor · timer/urgencia |
| Recuperación | objeto · quién lo tiene · por qué importa |
| Eliminación | objetivo(statblock) · complicación moral |
| Escolta / Defensa | qué se protege · ruta/oleadas · recursos |

---

## 5. Cómo la skill la genera

1. Parte de la **premisa con stakes** (no un fetch quest) — qué se pierde si no actúan.
2. Clava el **dilema moral** (la decisión sin respuesta fácil) y las **consecuencias por rama**.
3. Ancla ≥2 NPCs (quien pide / quien complica) y siembra lugares/recompensa(item)/antagonista(statblock).
4. Del grafo saca *flavor* de gancho/dilema (hooks, crime-intrigue, horror pacing) — limando setting.
5. Cierra con pistas de múltiples caminos + un misterio que enlaza a lore mayor.

---

## 6. Decisiones abiertas

1. `recompensa` — ¿solo item(rel), o item + gp opcional en el mismo bloque?
2. Set final de subtipos de quest (¿los 5 + Otro?).
