# Overrides de plantillas (punto de personalización del PROYECTO)

Este directorio es la **Prioridad 1** del stack de resolución de plantillas de
spec-kit (`resolve_template` en `.specify/scripts/bash/common.sh`):

```
1. .specify/templates/overrides/<name>.md   ← aquí (gana)
2. .specify/presets/<id>/templates/
3. .specify/extensions/<id>/templates/
4. .specify/templates/<name>.md              ← core
```

Para personalizar una plantilla en un proyecto concreto, deja aquí un archivo con el
mismo nombre que la core (p. ej. `plan-template.md`, `tasks-template.md`) y contendrá
el reemplazo **completo** (no es un parche; sustituye al core entero).

**Nota sobre el weave spec-kit↔superpowers:** el weave NO vive aquí. Vive en
`.specify/memory/constitution.md` (Artículos I–III), porque `/speckit-constitution`
y las fases `plan`/`implement` leen la constitución como governance, y porque un
override congelaría el contenido core (frágil ante updates de spec-kit). Este
directorio queda libre para tus overrides específicos del proyecto.
