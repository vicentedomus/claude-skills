---
name: speckit-with-superpowers
description: >-
  Runbook para arrancar una implementación con el combo spec-kit + superpowers
  cableado en el repo. Úsala cuando el usuario diga "combo spec kit + superpowers",
  "arranquemos/implementemos con spec-kit", o pida una implementación spec-driven
  (con andamiaje formal de specs). Conduce las fases-compuerta de spec-kit
  (specify → plan → tasks → implement) con checkpoint por artefacto, injerta el
  rigor de superpowers (TDD RED-GREEN-REFACTOR, verificación antes de completar,
  code review por severidad) vía el weave de la constitución, y respeta ponytail
  (solución mínima) siempre activo. NO es para trabajo suelto sin specs ni para
  planeación con brainstorming/writing-plans de superpowers a secas.
---

# speckit-with-superpowers

> **Esta skill es NUESTRA (orquestación), no es core de spec-kit.** No es una de las
> 10 skills `speckit-*` vendorizadas — esas se regeneran cada sesión desde
> `claude-skills/speckit-combo/payload/` y son intocables. Este runbook vive en
> `claude-skills` y se materializa vía `.claude/skills.txt` (como cualquier skill
> compartida). Comparte el prefijo `speckit-` solo por afinidad temática.

Conduce una implementación **spec-driven** usando el combo ya cableado en el repo:
**spec-kit** (estructura) + el **weave de superpowers** (rigor) + **ponytail** (tamaño).
El objetivo es que el flujo siempre corra igual: fases-compuerta ordenadas, con el
rigor injertado donde toca.

## Cuándo usarla

El usuario dice **"combo spec kit + superpowers"**, *"arranquemos/implementemos con
spec-kit"*, o pide una implementación con andamiaje formal de specs.

**Cuándo NO:** si pide solo pensar/diseñar sin specs, usa el flujo nativo de superpowers
(`brainstorming` → `writing-plans` → …), no este runbook. No apiles ambos volantes de
planeación.

## Prerequisitos (verifícalos al arrancar)

1. **`.specify/` presente** (lo materializa el hook `sync-speckit.sh` cada sesión). Si
   falta, el combo no está cableado en este repo → avísalo y detente.
2. **`.specify/memory/constitution.md` conserva los Artículos I–III** (TDD, verificación,
   code review). Si los borraron, el weave no aplica → avísalo antes de seguir.
3. **superpowers presente** (`obra/Superpowers` en `.claude/upstream-skills.txt`). Si no
   está, el weave sigue vigente como disciplina inline (degrada con gracia).

## El flujo: fases-compuerta

Conduce las fases **en orden**, con **checkpoint de revisión del artefacto de cada fase**
(no de corrido, salvo que el usuario lo pida). Cada fase deja artefacto en `specs/NNN/`.

1. `/speckit-constitution` — **solo si** aún no está afinada (ya viene sembrada con el
   weave). Nunca borres los Artículos I–III.
2. `/speckit-specify` → `spec.md` (qué y por qué). **Checkpoint.**
3. `/speckit-clarify` → *(opcional)* cierra ambigüedades del spec.
4. `/speckit-plan` → `plan.md` + design artifacts. **Checkpoint.** Aquí el weave empieza a
   gobernar.
5. `/speckit-tasks` → `tasks.md` (lista ordenada por dependencias). **Checkpoint.**
6. `/speckit-analyze` → *(opcional)* chequeo de consistencia spec/plan/tasks.
7. `/speckit-implement` → ejecuta `tasks.md`. Aquí engrana **todo** el rigor.

## Las tres capas y dónde engrana cada una

| Capa | Qué gobierna | Dónde actúa |
|---|---|---|
| **spec-kit** | estructura (spec/plan/tasks/artefactos) | todas las fases |
| **superpowers** (weave de `constitution.md`) | método/rigor: TDD RED-GREEN-REFACTOR, verificación antes de completar, code review por severidad | `plan` y sobre todo `implement` |
| **ponytail** (hook always-on) | tamaño: solución mínima (YAGNI, stdlib-first) | siempre; carve-outs: **tests sagrados**, **no podar en diseño** |

En `specify` es estructura pura (el rigor aún no engrana). El injerto de superpowers se
hace visible en `plan`/`implement`.

## Reglas

- **Gated por default**: pausa en cada checkpoint para que el usuario revise el artefacto.
  Solo encadena de corrido si lo pide explícitamente.
- **No apiles planeación**: no combines `/speckit-specify` + `/speckit-plan` con
  `brainstorming`/`writing-plans` de superpowers — elige un volante.
- **Respeta las convenciones del repo consumidor** (p. ej. en QuestKeep el contenido de
  reglas D&D va en inglés verbatim; en Domus Hub, web + móvil). Este runbook gobierna el
  *método*, no anula el `CLAUDE.md` del repo.
