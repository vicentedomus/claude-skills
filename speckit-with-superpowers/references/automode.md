# Automode: todas las rondas de corrido (pasos 8 y 9)

En automode Claude corre las rondas `auto` de la tabla **sin pedir permiso entre rondas**. La
autorización es la elección del modo en el checkpoint del paso 7, anotada en `rondas.md` (modo, fecha,
quién, **Hasta**, test-web autorizado). **Nada llega a `main` sin la persona**: todo se acumula
en una rama de integración y el Gran merge final lo aprueba ella.

`rondas.md` es la memoria de la corrida, no el chat: actualízalo y comitéalo al cerrar cada
ronda, para que una sesión nueva (contenedor reciclado, contexto compactado) pueda retomar.

## 0. Preflight (una vez, antes de R1)

1. `main` actualizado; crea `claude/NNN-integracion` desde `main` y haz push. Si el push a
   `claude/NNN-*` falla por permisos, **no arranques**: avisa. En un clon superficial (la nube
   clona con `--depth 1` y solo sigue `main`), agrega antes el refspec de las ramas de la corrida:
   `git config --add remote.origin.fetch '+refs/heads/claude/*:refs/remotes/origin/claude/*'` y
   `git fetch origin`. Sin esto las ramas de ronda quedan sin seguimiento y los hooks de cierre
   las reportan como "sin subir" aunque ya estén en el remoto.
2. Levanta el entorno local según la cabecera de `rondas.md` (p. ej. Docker + base local).
3. Corre **todos los checks sobre `main`**. Si algo ya está en rojo, no arranques: sin una base
   en verde no se puede saber qué rompió cada ronda. (Un rojo conocido y documentado del repo,
   p. ej. una prueba que depende de la hora, se anota en la cabecera como excepción y se acepta
   solo si la persona ya la conocía.)
4. Primer commit en la integración: `rondas.md` con el plan aprobado.

Si el preflight falla, no hay automode: reporta qué falló y ofrece modo manual.

## 1. Ramas

```
main ─────────────────────────────────────────┐  Gran merge (solo con aprobación)
  └─ claude/NNN-integracion ──●────●────●─────┘
        ├─ claude/NNN-r01-<slug> ── PR → ●
        ├─ claude/NNN-r02-<slug> ── PR → ●
```

- Cada ronda: rama desde la integración, PR **con base en la integración**, merge con **merge
  commit** (no squash) para conservar la historia por ronda.
- Rondas **en serie**, una a la vez (en paralelo chocarían migraciones y `tasks.md`).
- Nunca rebase ni force-push sobre la integración.

## 2. Ciclo de una ronda

Toma la siguiente ronda `auto` en orden de tabla cuyas dependencias estén todas `mergeada`.

1. **Sincroniza**: `git fetch origin main` y mergea `main` a la integración (merge, no rebase).
   Conflicto mecánico (listas que crecieron, docs del spec) → resuélvelo y sigue; los checks de
   la ronda lo validan. Conflicto de fondo → **detén toda la corrida** (afecta a todas) y
   regístralo en Bloqueos.
2. Rama `claude/NNN-rXX-<slug>` desde la integración. `rondas.md`: ronda `en curso` + Bitácora.
3. `/speckit-implement` **acotado a las tareas de la ronda** (lista de IDs en el argumento).
   Rige la constitución: Art. I (TDD, evidencia rojo→verde por tarea).
4. **Checks** (Art. II), en el orden de la cabecera:
   - **Suite completa**, no solo lo de la ronda: la integración acumula cambios y una regresión
     de R2 debe aparecer en R7.
   - **test-web** solo si la ronda toca UI, sobre los escenarios de `quickstart.md` que toca
     la ronda, en las vistas que pida el repo (p. ej. escritorio + móvil). Elegir automode es
     la aceptación explícita que pide la skill `test-web`. No es la suite E2E permanente: esa
     solo si la persona la pide. Prueba inestable: un reintento; si falla dos veces, es real.
   - **Antes/después en el navegador** si la ronda cambia la base (esquema, políticas, FK,
     RPC) aunque no toque pantallas: las pruebas unitarias usan una base falsa y no ven, p. ej.,
     un embed de PostgREST que se vuelve ambiguo. Captura las mismas pantallas con la base y la
     app de `main` (un `git worktree` de `main` + reset de la base local a sus migraciones y su
     semilla) y con las de la ronda, con las mismas usuarias y vistas (escritorio + móvil), y
     compáralas píxel a píxel (p. ej. PIL). Lo esperado es *idéntico* salvo lo que la ronda
     cambia a propósito; cualquier otra diferencia se revisa a ojo antes de mergear.
5. **Review** (Art. III): un subagente **fresco** (sin tu contexto) con
   `requesting-code-review` sobre `git diff claude/NNN-integracion...HEAD`, con el spec, el plan
   y la constitución como referencia y el foco de riesgo del repo (p. ej. fugas entre
   tenants, RLS, datos a terceros). Hallazgos **críticos bloquean**; los demás se corrigen o se
   anotan en la Bitácora. El encargo del subagente dice **explícitamente** que trabaje solo
   contra el entorno local (base local en `BEGIN … ROLLBACK`, sin modificar archivos) y que
   **no** use conectores ni credenciales contra producción (p. ej. el MCP de la base remota),
   aunque los tenga a mano.
6. **Presupuesto de arreglos**: hasta **2 intentos** por check o review en rojo. Nunca saltes,
   desactives ni debilites una prueba para ponerla en verde. Si sigue en rojo → §3.
7. **Cierra**: tareas `[x]` con evidencia en `tasks.md`; `rondas.md` (estado `mergeada`,
   enlace del PR, Bitácora, decisiones nuevas); push; PR con base en la integración; merge.
   Si el repo pide reescribir título y cuerpo del PR al mergear, hazlo también aquí.
8. ¿Se cerró la ronda **Hasta**? → §6. Si no, siguiente ronda.

Si a media ronda resulta mucho más grande de lo previsto: pártela (`R5a` cerrada con lo hecho,
`R5b` nueva en la tabla, misma dependencia), corre `validar-rondas.sh` y anótalo en la Bitácora.

## 3. Ronda bloqueada

- Estado `bloqueada`; en Bloqueos: qué check o decisión, intentos hechos, rama con el trabajo
  parcial (push sin PR, o PR abierto sin mergear).
- Todas las rondas que dependen de ella (directa o transitivamente) pasan a `detenida`.
- **Sigue con las independientes.** Si no queda ninguna ronda `auto` ejecutable → §6.

## 4. Decisiones e input humano

Cada vez que la implementación pide algo que no está en spec/plan/tasks, clasifícalo y
regístralo en la tabla **Decisiones** de `rondas.md` (`D-01`, `D-02`, …), con las rondas a las
que afecta (radio de impacto):

| Tipo | Qué es | Qué hacer |
|---|---|---|
| **A** reversible y barata | texto de UI, nombre interno, orden de una lista, detalle visual | Decide lo más alineado al spec, sigue y regístralo con la alternativa y cómo revertir |
| **B** bloquea pero se aísla | llaves, cuentas, pagos, contenido legal o de terceros, aprobación de costo | La tarea va a la Ronda H (`RH`). Si otra tarea la necesita: stub con la marca `RONDA-H: D-NN` en el código, sin pruebas que den el stub por bueno |
| **C** cambia el diseño | modelo de datos, seguridad/RLS, precio, alcance, cambio al spec o enmienda a la constitución | **Nunca se asume.** Regístrala, marca la ronda `bloqueada` (§3) y sigue con las independientes |

Regla de desempate: si revertir la decisión obligaría a rehacer rondas posteriores (forma de una
tabla, contrato de una API, semántica de permisos), es **C**, no A. Las tareas ⚠️ ya se
mandaron a rondas humanas en el paso 7; esto es para lo que surge al implementar. Respeta las
reglas del repo sobre qué siempre se pregunta (p. ej. textos que ve la clienta).

## 5. Retomar

"Retoma la NNN" en una sesión nueva: `git fetch origin claude/NNN-integracion`, lee `rondas.md`
de esa rama y continúa. Ronda `en curso` → revisa su rama (qué tareas tienen evidencia) y sigue
desde ahí; nunca rehagas una ronda `mergeada`. Repite el preflight del entorno local (no el de
`main`) antes de seguir.

## 6. Cierre

Cuando se cierra la ronda **Hasta** o no quedan rondas `auto` ejecutables:

1. **Verificación sobre la integración**: todos los checks y, si test-web está autorizado, los
   escenarios completos de `quickstart.md`. Si alguna ronda cambió la base, repite el
   antes/después en el navegador contra `main` con la integración completa.
2. **Orden de migraciones** (si el repo usa migraciones con timestamp): ninguna migración nueva
   de la integración puede tener timestamp anterior a la última de `main`. Si pasa, renómbralas
   (no se han aplicado en ningún lado) en un commit de la integración y vuelve a correr los
   checks de base de datos.
3. **Aviso final** (notificación push si hay herramienta, y mensaje en el chat): tabla final
   con estados y PRs, decisiones `pendiente` para revisar (A, B y C con su radio de impacto),
   bloqueos, y lo que sigue. Por defecto es el único aviso de la corrida (ver `Avisos` en la
   cabecera).

Si quedan rondas `auto` sin correr (por **Hasta** o por bloqueos), el cierre es parcial: no hay
Gran PR; la persona decide si se sigue en automode, en manual, o se arregla primero.

Con todas las rondas `auto` mergeadas, con la persona:

4. **Revisión de decisiones**: confirma o voltea cada `D-NN`. Lo volteado se rehace.
5. **Ronda H** en modo manual (PRs a la integración, con aprobación): tareas diferidas,
   decisiones volteadas y stubs. Check final: `grep -rn "RONDA-H:"` sin resultados.
6. Verificación completa otra vez y **Gran PR** `claude/NNN-integracion` → `main`, con merge
   commit, solo con la aprobación de la persona.
7. Las rondas humanas de producción (despliegue, cuentas, costo) van después, en manual.

## 7. Automode nunca

- Toca, mergea o abre PR a `main` (salvo el Gran PR del cierre, aprobado).
- Hace force-push o rebase de la integración.
- Despliega, aplica migraciones en remoto o usa servicios que cuestan (incluidas branches de
  base de datos de pago), ni crea cuentas.
- Edita una migración ya aplicada, enmienda la constitución o cambia el spec.
- Salta, desactiva o debilita pruebas.
- Asume una decisión de tipo C.

## 8. Encaje con superpowers y ponytail

- Usa `test-driven-development`, `verification-before-completion` y `requesting-code-review`
  (los Artículos I–III del weave) dentro de cada ronda.
- **No** usa el motor de ejecución de superpowers (`subagent-driven-development`,
  `executing-plans`): ejecuta `/speckit-implement`. No apiles volantes.
- `finishing-a-development-branch` pregunta si mergear o abrir PR: en automode esa pregunta la
  reemplaza esta política.
- ponytail sigue gobernando el tamaño; las pruebas son sagradas.
