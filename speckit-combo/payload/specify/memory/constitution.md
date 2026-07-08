# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->
<!--
  SEED — provisto por el combo spec-kit de claude-skills (weave con superpowers).
  Los Artículos I–III y Governance ya vienen concretos (la disciplina de ingeniería
  de superpowers). Completa los tokens [EN_CORCHETES] con lo específico de tu proyecto,
  idealmente corriendo /speckit-constitution, que rellena y propaga a plan/tasks.
  Las skills de superpowers (test-driven-development, verification-before-completion,
  requesting-code-review) se aplican "si están disponibles"; si no, aplica su disciplina
  inline. Se sincronizan aparte vía sync-upstream-skills.sh (obra/Superpowers).
-->

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)
No se escribe código de producción sin un test que falle primero. Ciclo
RED → GREEN → REFACTOR estricto: escribe el test, obsérvalo fallar, implementa el
mínimo para pasarlo, luego refactoriza. Sigue la skill `test-driven-development` si
está disponible; si no, aplica la misma disciplina inline. El código escrito antes de
su test se descarta y se rehace bajo el ciclo.

### II. Verificación antes de completar
Ninguna tarea se marca como hecha sin ejercitar el cambio end-to-end y observar el
comportamiento real (no basta con que compile o pasen los tests unitarios). Sigue la
skill `verification-before-completion` si está disponible. La evidencia de la
verificación se anota al cerrar la tarea.

### III. Code review por severidad
Antes de cerrar una rama de desarrollo, el cambio pasa por review con severidad
graduada (usa `requesting-code-review` si está disponible). Los hallazgos **críticos
bloquean el merge**; los menores se registran o se corrigen. El código generado por
agentes no es excepción.

### IV. Simplicidad primero (YAGNI)
Se elige la solución más simple que cumple la especificación. La complejidad debe
justificarse explícitamente en el plan (sección Constitution Check). Sin abstracciones
especulativas ni features no pedidas.

### [PRINCIPLE_5_NAME]
<!-- Principio específico del proyecto. Example: V. Observability, Versioning, etc. -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Structured logging required; MAJOR.MINOR.BUILD versioning; etc. -->

## [SECTION_2_NAME]
<!-- Restricciones del proyecto. Example: Additional Constraints, Security, Performance -->

[SECTION_2_CONTENT]
<!-- Example: stack tecnológico, estándares de compliance, políticas de deploy, etc. -->

## Development Workflow & Quality Gates
<!-- Puedes extender esta sección con lo específico de tu proyecto. -->

- Todo trabajo procede spec → plan → tasks → implement (flujo spec-kit).
- Los gates de calidad de los Artículos I–III son obligatorios en la fase `implement`.
- Cada PR/review verifica cumplimiento de esta constitución antes del merge.
- [Añade aquí: aprobaciones de deploy, gates de CI, etc.]

## Governance

Esta constitución **prevalece** sobre otras prácticas. Las enmiendas requieren
documentarse con justificación y, si aplica, un plan de migración. Toda revisión de PR
verifica el cumplimiento; la complejidad no justificada se rechaza. Los Artículos I–III
son la disciplina de ingeniería base y no se relajan por conveniencia.

**Version**: 0.1.0 (seed) | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- /speckit-constitution actualizará versión y fechas al ratificar. -->
