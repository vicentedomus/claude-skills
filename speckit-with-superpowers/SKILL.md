---
name: speckit-with-superpowers
description: >-
  Runbook para implementaciones spec-driven con el combo spec-kit + superpowers cableado en el
  repo. Dispara con "combo spec kit + superpowers", "arranquemos/implementemos con spec-kit", al
  pedir una implementación con specs formales, o al retomar una corrida ("retoma la 002").
  Conduce specify → plan → tasks con checkpoint, agrupa las tareas en rondas (una ronda = un PR)
  y las ejecuta en modo manual o automode, con TDD, verificación y review por ronda. NO es para
  trabajo suelto sin specs.
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
rigor injertado donde toca, y la entrega en **rondas** (una ronda = un PR).

## Cuándo usarla

El usuario dice **"combo spec kit + superpowers"**, *"arranquemos/implementemos con
spec-kit"*, pide una implementación con andamiaje formal de specs, o pide **retomar** la
implementación de un spec que ya tiene `specs/NNN-…/rondas.md`.

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
7. **Rondas** (siempre, con cualquier modo) → `specs/NNN/rondas.md`. Agrupa las tareas en
   rondas, detecta los checks del repo, valida la tabla con `scripts/validar-rondas.sh` y
   presenta la tabla. **Checkpoint: pregunta si la implementación va en manual o en
   automode.** Detalle: [`references/rondas.md`](references/rondas.md).
8. **Ejecución por ronda**: cada ronda = rama + `/speckit-implement` **acotado a sus tareas**
   + checks (Art. I–III) + PR. Aquí engrana **todo** el rigor.
   - **Manual**: PR a `main` y te detienes en cada ronda hasta que la persona apruebe
     ([`references/rondas.md`](references/rondas.md), *Paso 8 en manual*).
   - **Automode**: todas las rondas `auto` de corrido sobre `claude/NNN-integracion`;
     decisiones registradas, bloqueos que no frenan a las independientes
     ([`references/automode.md`](references/automode.md)).
9. **Cierre** (automode): aviso final y, si quedan rondas, **la siguiente corrida** (alcance
   acordado en `rondas.md` y el prompt completo para arrancarla en una sesión nueva); con todas
   mergeadas, revisión de decisiones, Ronda H y Gran PR a `main` con
   aprobación ([`references/automode.md`](references/automode.md) §6).

**Retomar:** con el prompt que dejó el cierre anterior. Si `specs/NNN/rondas.md` ya existe (en
automode vive en `claude/NNN-integracion`, no en `main`), su sección *Siguiente corrida* dice el
alcance y autoriza las ramas; no
vuelvas a planear: léelo y continúa desde su estado.

## Las tres capas y dónde engrana cada una

| Capa | Qué gobierna | Dónde actúa |
|---|---|---|
| **spec-kit** | estructura (spec/plan/tasks/artefactos) y ejecución de tareas (`/speckit-implement`) | todas las fases |
| **superpowers** (weave de `constitution.md`) | método/rigor: TDD RED-GREEN-REFACTOR, verificación antes de completar, code review por severidad | `plan` y sobre todo cada ronda |
| **ponytail** (hook always-on) | tamaño: solución mínima (YAGNI, stdlib-first) | siempre; carve-outs: **tests sagrados**, **no podar en diseño** |
| **este runbook** | orden, rondas, modo y estado de la corrida (`rondas.md`) | pasos 7, 8 y 9 |

En `specify` es estructura pura (el rigor aún no engrana). El injerto de superpowers se
hace visible en `plan` y en cada ronda.

## Reglas

- **Gated por default**: pausa en cada checkpoint para que el usuario revise el artefacto.
  Solo encadena de corrido si lo pide explícitamente; automode es esa petición, y solo
  cubre la ejecución de rondas `auto`, nunca el merge a `main`.
- **No apiles planeación ni ejecución**: no combines `/speckit-specify` + `/speckit-plan` con
  `brainstorming`/`writing-plans`, ni `/speckit-implement` con `subagent-driven-development`/
  `executing-plans` de superpowers — elige un volante.
- **`rondas.md` es la memoria de la corrida**: actualízalo al cerrar cada ronda; no dependas
  del chat para saber dónde vas.
- **Respeta las convenciones del repo consumidor** (p. ej. en QuestKeep el contenido de
  reglas D&D va en inglés verbatim; en Domus Hub y Grax Vida, web + móvil; reglas sobre
  cuándo correr pruebas de navegador o cómo resumir un PR al mergear). Este runbook gobierna
  el *método*, no anula el `CLAUDE.md` del repo.
