# [NNN] · [NOMBRE] (fast)

<!--
  Spec fast de speckit-with-superpowers (references/fast.md): qué, cómo, tareas y estado en un
  solo archivo. Se aprueba en un checkpoint antes de escribir código y viaja en el PR.
  Estado: borrador · aprobado · en PR · escalado (al completo: references/fast.md §3).
-->

**Estado**: borrador · **PR**: —

## Qué y por qué

[2-4 frases: qué cambia para quién y por qué.]

**Aceptación**
- [ ] [criterio observable 1]
- [ ] [criterio observable 2]

**Fuera de alcance**: [lo que NO se hace]

## Cómo

- **Archivos**: `[ruta]` ([qué cambia]), `[ruta]` ([qué cambia])
- **Base de datos**: [no | migración `[nombre]`: qué hace] <!-- tablas nuevas o RLS → no es fast -->
- **Reglas del repo que aplican**: [p. ej. web + móvil · fechas en Mérida · montos con formato]
- **Constitution check**: TDD ✓ · simplicidad: [la opción mínima y por qué basta]

## Tareas

<!-- Formato tasks.md. Cada tarea lleva su prueba; la evidencia anota rojo → verde. -->
- [ ] T001 [tarea] → evidencia:
- [ ] T002 [tarea] → evidencia:

## Checks

| Check | Comando | Resultado |
|---|---|---|
| Typecheck | `[npm run typecheck]` | |
| Unit | `[npm test]` | |
| Build | `[npm run build]` | |
| Review | [inline | subagente: motivo] | [hallazgos por severidad] |

## Preguntas (checkpoint)

1. [pregunta de alcance o caso borde]

## Bitácora

<!-- Una línea por evento, la más reciente al final. -->
- [FECHA] · borrador
