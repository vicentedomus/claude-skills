# Rondas: agrupar, validar y presentar (paso 7) + modo manual (paso 8)

Una **ronda** es un grupo de tareas de `tasks.md` que se entrega como **un PR**. El paso 7
corre siempre después de `/speckit-tasks`, sea cual sea el modo.

## 7.1 Agrupar

Lee `tasks.md` (fases, `[P]`, sección *Dependencies & Execution Order*) y `plan.md`. Si
`tasks.md` ya trae una tabla de rondas (en prosa o en *Implementation Strategy*), **pártela de
ahí**: es una decisión previa de la persona; solo normalízala al formato de la plantilla y
señala lo que cambies.

Reglas para agrupar:

1. **Respeta las dependencias**: una ronda solo depende de rondas que van antes en la tabla.
   Setup y Fundacional primero; después, una o varias rondas por historia, en el orden de
   prioridad del spec.
2. **Cohesión**: cada ronda es un PR revisable que deja algo verificable (una historia o una
   rebanada de ella, una capa fundacional). Prueba y su implementación van en la misma ronda.
3. **Tamaño**: hasta ~9 tareas. Si una historia es más grande, pártela por capa (base → UI) o
   por subflujo; nunca separes una prueba de su implementación.
4. **Rondas humanas** (`Tipo: humana`): tareas marcadas ⚠️ en `tasks.md` (cuentas, pagos,
   acciones o decisiones de la persona), las que tienen **costo**, el despliegue a producción,
   y las tareas "a pedido". Agrúpalas al final o en la Ronda H (`RH`). Si una tarea ⚠️ se puede
   hacer sin la persona (p. ej. Stripe en modo prueba con llaves vacías), puede ir en una ronda
   `auto`, pero dilo explícitamente al presentar la tabla.
5. **Verificación y review del spec completo** (p. ej. "review integral") van en una ronda
   propia al final de las `auto`.
6. Ninguna tarea pendiente queda sin ronda; ninguna aparece dos veces.

## 7.2 Checks del repo

No los inventes ni los copies de otro repo: sácalos de `plan.md` (Testing / Constitution
Check), `CLAUDE.md`, `package.json` (o equivalente) y la constitución. Anota en la cabecera de
`rondas.md` el comando de cada uno, cuándo aplica (siempre / si hay UI) y el **preflight**
(cómo levantar el entorno local, p. ej. Docker + base local). Respeta las reglas del repo sobre
pruebas de navegador (p. ej. "test-web solo si se pide").

## 7.3 Escribir y validar

1. Copia `assets/rondas-template.md` a `specs/NNN-…/rondas.md` y llénalo.
2. Corre `bash .claude/skills/speckit-with-superpowers/scripts/validar-rondas.sh specs/NNN-…/`
   (la ruta es la de esta skill en el repo consumidor; con `bash` no importa el bit ejecutable).
   **Errores** = arréglalos antes de presentar. **Avisos** = preséntalos con su justificación.

## 7.4 Checkpoint: tabla + modo

Presenta en el chat:

- La tabla (Ronda · PR · Tareas · # · Depende de · Tipo).
- Los checks y el preflight.
- Los avisos del validador con su justificación, y qué cambiaste respecto a una tabla previa.

Luego pregunta: **¿implementación manual o automode?** Explica la diferencia en una línea cada
una (manual: un PR a `main` por ronda, con tu aprobación entre rondas; automode: todas las
rondas `auto` de corrido sobre una rama de integración, decisiones registradas y un Gran merge
final con tu aprobación). En automode pregunta también **Hasta** (todas, o una ronda tope).

Anota el modo en `rondas.md` y agrega la primera línea a la Bitácora.

## Paso 8 en manual: ronda por ronda

Para cada ronda `auto` en orden de la tabla:

1. Rama `claude/NNN-rXX-<slug>` desde `main` actualizado.
2. Marca la ronda `en curso` en `rondas.md`.
3. Invoca `/speckit-implement` **acotado a las tareas de la ronda**: pásale en el argumento la
   lista de IDs ("Implementa solo T008, T009, T010… de tasks.md; no toques las demás").
   Dentro de cada tarea rige la constitución (Art. I TDD con evidencia rojo→verde).
4. Corre los checks de la cabecera (Art. II) y el review (Art. III). Hallazgos críticos se
   corrigen antes de abrir el PR.
5. Marca las tareas `[x]` con su evidencia en `tasks.md`, la ronda `en revisión` y el PR en
   `Enlace`; abre el PR a `main`.
6. **Detente.** La persona revisa y aprueba; entonces mergea (y, si el repo lo pide, reescribe
   título y cuerpo del PR con el resumen). El paso de `en revisión` a `mergeada` se anota en
   el primer commit de la ronda siguiente (no hace falta un PR solo para eso).

Las rondas `humanas` se hacen con la persona cuando toque, igual que una ronda manual.
