# Modo fast: implementaciones chicas

El mismo mecanismo que el flujo completo, con menos ceremonia: el spec va antes del código, se
aprueba en **un checkpoint**, el código entra con TDD (Art. I), checks (Art. II) y review
(Art. III), y la entrega es **una ronda = un PR a `main`**. Todo el estado vive en **un archivo**,
`specs/NNN-<slug>/fast.md`, en lugar de spec/plan/tasks/rondas.

## 1. Cuándo

**Disparadores**: *"combo fast"*, *"speckit fast"*, *"versión rápida del combo"*.

**Entra en fast si se cumple todo:**

- cabe en un PR (≤ ~9 tareas);
- no crea tablas ni cambia políticas RLS o de seguridad;
- no rompe a la versión anterior de la app (en Domus: no sube `COMPATIBILIDAD`);
- no deja decisiones de diseño abiertas (modelo de datos, permisos, alcance).

Si la persona pide el combo completo y el trabajo cumple estos criterios, sugiere fast en una
línea; no cambies de modo sin que lo diga. Si pide fast y un criterio falla, di cuál y propón el
completo: decide ella.

Los prerequisitos son los de `SKILL.md` (`.specify/`, constitución con los Art. I–III).

## 2. Flujo

### 2.1 Arranque

1. Número del spec, compartido con los completos y **sin crear rama ni archivos**:
   `bash .specify/scripts/bash/create-new-feature.sh --json --dry-run --short-name <slug> "<descripción>"`
   → `FEATURE_NUM`. Crea `specs/NNN-<slug>/` y copia ahí `assets/fast-template.md` como `fast.md`.
2. Lee el código que toca el cambio (llamadores, pruebas, fixtures) y llena **Qué y por qué**,
   **Cómo** y **Tareas**. Las tareas usan el formato de `tasks.md` (`- [ ] T001 …`), y cada una
   lleva su prueba (la evidencia anota rojo → verde). En **Cómo**, lista las reglas del
   `CLAUDE.md` del repo que aplican (en Domus: web + móvil, Mérida, montos, rescate…).
3. Al final del documento, hasta **3 preguntas** de alcance o casos borde. Cubren la regla de
   "confirmar el alcance antes de implementar" si el repo la tiene.

### 2.2 Checkpoint único

Presenta el `fast.md` en el chat (o su ruta y un resumen si es largo) junto con las preguntas.
Las respuestas van al documento; luego **Estado: aprobado** y una línea en la Bitácora. **No se
escribe código antes de la aprobación.**

### 2.3 Ejecución

1. Rama: la que tenga asignada la sesión o, si no hay, `claude/NNN-fast-<slug>` desde `main`.
2. Tarea por tarea, con TDD (Art. I, `test-driven-development`); evidencia en el `fast.md`. Lo
   implementa Claude directamente: sin `/speckit-implement` (no hay `tasks.md`) y sin
   `subagent-driven-development`/`executing-plans` (no se apilan volantes).
3. Lo que surge y no está en el documento, con la clasificación de `automode.md` §4:
   - **A** (reversible y barata): decide, sigue y anótalo en la Bitácora.
   - **B** (bloquea, pero se aísla): pregúntale a la persona en una sola pregunta; si no se
     resuelve, va como pendiente en el cuerpo del PR.
   - **C** (diseño): **escala** (§3).

### 2.4 Checks y review

- **Checks (Art. II)**: los del repo (`package.json`, `CLAUDE.md`): typecheck, unit, build. Las
  pruebas de navegador, según la regla del repo (en Domus, test-web solo si se pide).
- **Review (Art. III)** por severidad (crítico / importante / menor):
  - **Inline** por default: lee el diff completo contra el `fast.md`, lista los hallazgos y
    corrige los críticos.
  - **Subagente fresco** con `requesting-code-review` si el diff toca la base (migración, RPC,
    trigger), dinero, auth/seguridad o pasa de ~300 líneas. Mismas restricciones que en
    `automode.md` §2, paso 5: solo entorno local, nada contra producción.
- Presupuesto: **2 intentos** por check o review en rojo. Nunca saltes ni debilites una prueba;
  si sigue en rojo, detente y repórtalo.

### 2.5 PR

Tareas `[x]` con evidencia, Checks llenos, **Estado: en PR** con el enlace. El `fast.md` va en el
PR. El cuerpo del PR enlaza al `fast.md` y resume los checks y el review. **Detente**: la persona
revisa y mergea (y, si el repo lo pide, se reescribe el título y el cuerpo al mergear).

## 3. Escalar al completo

**Cuándo**: salen más de ~9 tareas, aparece una decisión C, se necesita más de un PR, o un
criterio de §1 deja de cumplirse.

1. Detente. Bitácora: `escalado · <motivo>`; **Estado: escalado**. Avísale a la persona con el
   motivo y confirma que siga en el completo.
2. Mismo directorio y mismo número: `/speckit-specify` con el contenido de **Qué y por qué** como
   descripción e indicando el número existente (`create-new-feature.sh --number NNN --short-name
   <slug> --allow-existing-branch` reutiliza `specs/NNN-<slug>/`). Después `/speckit-plan` con
   **Cómo** como insumo y `/speckit-tasks` conservando los IDs y las tareas `[x]` con su evidencia.
3. Los checkpoints del completo siguen, pero son rápidos: el contenido ya estaba aprobado. Continúa
   en el paso 7 (rondas); el código ya hecho entra como tareas `[x]` de la primera ronda.
4. Al quedar `spec.md`, `plan.md` y `tasks.md`, borra el `fast.md` (una sola fuente de verdad) y
   pasa su Bitácora a `rondas.md`.

## 4. Lista de tareas de la sesión

Al aprobar el checkpoint: un elemento por T###, más «Checks (Art. II)», «Review (Art. III)» y
«Abrir PR», encadenados con `addBlockedBy`. Como en el completo, primero se escribe el `fast.md` y
después se actualiza la lista.

## 5. Fast nunca

- Escribe código antes del checkpoint.
- Salta, desactiva o debilita pruebas.
- Mergea a `main` ni abre más de un PR.
- Crea tablas o cambia RLS (eso escala).
- Asume una decisión C.
