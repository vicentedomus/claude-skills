# Rondas — [NNN] [NOMBRE DEL SPEC]

<!--
  Archivo de estado del spec (lo crea el paso 7 de speckit-with-superpowers).
  Es la memoria de la corrida: una sesión nueva retoma leyéndolo. Se comitea en la rama de
  cada ronda (manual) o en la de integración (automode) y se actualiza al cerrar cada ronda.
  Validarlo con: scripts/validar-rondas.sh specs/NNN-…/
-->

**Modo**: [manual | automode] · **Elegido**: [FECHA] por [PERSONA]
**Integración**: [claude/NNN-integracion | — (manual: cada ronda va a main)]
**Hasta**: [Rn | todas] <!-- automode se detiene al cerrar esta ronda -->
**test-web**: [autorizado en rondas con UI (automode) | solo si se pide (manual)]
**Avisos**: [solo al final | por ronda cerrada o bloqueada]

## Checks por ronda

Confirmados en el checkpoint del paso 7. Todos en verde para mergear.

| Check | Comando | Cuándo |
|---|---|---|
| Typecheck | `[npm run typecheck]` | siempre |
| Unit | `[npm test]` | siempre |
| [Base de datos] | `[npx supabase test db]` | siempre |
| Build | `[npm run build]` | siempre |
| test-web | escenarios de `quickstart.md` que toca la ronda, [escritorio + móvil] | si la ronda toca UI |
| Antes/después | mismas pantallas y usuarias con la base y la app de `main` vs las de la ronda, píxel a píxel | si la ronda cambia la base |
| Review | subagente con `requesting-code-review` sobre el diff de la ronda | siempre |

**Preflight** (automode, antes de la primera ronda): [cómo levantar el entorno local], suite
en verde sobre `main`, push a `claude/NNN-*` permitido.

## Tabla

El orden de las filas es el orden de ejecución. `Tareas`: solo IDs y rangos. `Tipo`: `auto` (la
corre Claude) o `humana` (cuentas, costo, ⚠️, decisiones; va a la Ronda H o al final).
`Estado`: pendiente · en curso · en revisión (manual: PR abierto a `main`) · mergeada ·
bloqueada · detenida (depende de una bloqueada) · partida (ver R5a/R5b).

| Ronda | PR | Tareas | Depende de | Tipo | Estado | Enlace |
|---|---|---|---|---|---|---|
| R1 | [título del PR] | T001, T002 | — | auto | pendiente | |
| R2 | [título del PR] | T003–T009 | R1 | auto | pendiente | |
| RH | Ronda humana: decisiones y tareas diferidas | T010 | — | humana | pendiente | |

## Siguiente corrida

<!-- La escribe el cierre parcial (automode.md §6), acordada con la persona. La sesión que retoma la lee
     de aquí: alcance, modo y permiso para las ramas. -->

- **Alcance**: [Rx–Ry] — [por qué ese corte]
- **Modo**: [automode | manual] · **Avisos**: [solo al final | por ronda]
- **Ramas autorizadas**: `claude/NNN-*` (rondas y su merge a `claude/NNN-integracion`; nada a `main`)
- **Antes de empezar**: [nada | decisiones, bloqueos o tareas de la Ronda H]

## Bitácora

<!-- Una línea por evento, la más reciente al final. -->
- [FECHA] · plan · tabla aprobada, modo [manual|automode]

## Decisiones

<!--
  Solo automode. Tipo A = reversible y barata (se asume y se sigue). Tipo B = bloquea pero se
  aísla (va a RH; si otra tarea la necesita, stub marcado `RONDA-H: D-NN` en el código).
  Tipo C (diseño, datos, RLS/seguridad, precio, alcance, spec o constitución) NUNCA se asume:
  va a Bloqueos y detiene las rondas que dependan.
  Estado: pendiente · confirmada · volteada (al revisar con la persona en el cierre).
-->

| ID | Tipo | Ronda | Qué asumí / qué falta | Alternativa y cómo revertir | Afecta a | Estado |
|---|---|---|---|---|---|---|

## Bloqueos

<!-- Ronda · check o decisión que bloquea · intentos · rondas dependientes detenidas. -->
