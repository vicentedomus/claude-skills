---
name: programa-semanal
description: Genera el Programa Semanal de coordinación de TAREAS ESTRATÉGICAS de un desarrollo de Domus (Gran Bosco por defecto) — un calendario PDF Lun-Vie POR ACTOR (cada supervisor/gerente recibe el suyo) con acciones concretas de coordinación, leyendo datos en vivo de Supabase. Úsala siempre que el usuario pida el programa semanal, el plan de la semana de su gente, los pendientes estratégicos por persona/actor/responsable, o ayudar a alguien a coordinar su semana — aunque no diga "programa" ni "calendario". Frases típicas, "arma el programa semanal de Gran Bosco", "qué le toca a Fernando la siguiente semana", "genera los calendarios de la semana para los supervisores", "el plan de la semana de Daniel", "mándale a mi gente sus pendientes estratégicos de la semana". NO es el deck de junta de avance de obra (eso es tareas-deck) ni el de garantías (garantias-deck) — este es un calendario operativo individual, uno por responsable.
---

# Programa Semanal de Tareas Estratégicas (por actor)

Genera un calendario semanal Lun–Vie en PDF (carta apaisada, 1 página) **por cada
responsable** con pendientes estratégicos de un desarrollo, para ayudarle a
**coordinar su semana**: a quién llamar el lunes, qué verificar en sitio el día
del compromiso, qué escalar y cuándo cerrar.

El producto NO es una agenda de reportes ("hoy te toca actualizar X") sino un
**plan de coordinación**: cada pendiente se traduce a la acción que genera
palanca, colocada el día en que la genera.

## Flujo

1. **Parámetros**: desarrollo (default **Gran Bosco**), semana objetivo (default:
   la siguiente semana si hoy es jue/vie, la actual si es lun–mié; confírmalo si
   es ambiguo) y actores (default: todos los responsables con pendientes).
2. **Datos**: corre `references/query.sql` contra la BD Domus
   (`ifqwrtheakkvgezewxqx`) vía `mcp__Supabase__execute_sql`, sustituyendo
   `:DESARROLLO` por el patrón del proyecto (p.ej. `'%bosco%'`).
3. **Interpretación**: construye el plan por actor siguiendo las
   **Reglas de interpretación** de abajo. Este es el paso de criterio — no es
   mecánico.
4. **Render**: escribe `plan.json` (esquema documentado en el encabezado de
   `scripts/render.mjs`) y corre:
   ```bash
   node scripts/render.mjs plan.json <directorio-salida>
   ```
   Requiere `playwright` + chromium (`npm install playwright && npx playwright
   install chromium` si el contenedor es fresco).
5. **Verificación**: cada PDF debe ser de **1 página** (el render auto-escala,
   pero revisa que no haya quedado ilegible: si un actor trae demasiadas
   tarjetas, consolida — p.ej. varios lotes del mismo frente en una tarjeta).
6. **Entrega**: manda los PDFs al usuario y **commitea todo** (plan.json,
   HTML y PDFs) en `juntas/programa-semanal/<desarrollo>/AAAA/<mes>/` del repo
   domus-hub — los contenedores son efímeros; lo que no se commitea se pierde.

## Reglas de interpretación (el corazón de la skill)

**1. Fechas programadas = compromisos; solo el avance y las observaciones son
hechos.** `fecha_inicio` y `fecha_fin_programada` dicen lo que *debería* pasar,
no lo que pasó. Si una fecha de inicio ya pasó pero el avance sigue en 0 y no
hay observación que confirme la entrada, el programa dice "confirmar **si**
entraron", nunca "ya entraron". Las observaciones traen timestamp: úsalo para
distinguir acuerdos ("la fecha tentativa es el 11") de eventos ("terminado el
zanjeado").

**2. Anticipar, no lamentar.** Toda dependencia de un tercero (proveedor,
contratista, constructor) que tenga compromiso esta semana se **asegura el
lunes** con una llamada/confirmación — no se verifica al día siguiente del
incumplimiento, porque ahí ya se perdió la oportunidad. Ejemplo: si Dotec entra
el jueves, el lunes se llama a Dotec para garantizar que van a entrar.

**3. Acciones con verbo, no "dar seguimiento".** Cada tarjeta es una acción
concreta: llamar a X para Y, recorrer estos lotes y acordar fecha de liberación,
verificar en sitio que Z entró, hacer la lista de detalles. Extrae el "a quién"
y el "para qué" de `ultimas_observaciones`.

**4. El día del compromiso se verifica en sitio; lo incumplido se escala el
mismo día.** Las verificaciones caen el día de la fecha comprometida (no
después), y la escalación va como condicional dentro de la tarjeta ("Si no
entró: escalar a Daniel HOY"), nunca como tarea del viernes.

**5. Cada acción dentro del rol.** Supervisor = campo: sitio, recorridos,
recepción, validar listas de detalles con cliente, confirmar entradas de
cuadrillas. Gerente = acuerdos: contratistas a nivel fechas/cuadrillas
comprometidas, convenios con autoridades, anticipos y pagos, créditos de
clientes. Si un dato sugiere una acción fuera del rol del actor, reasígnala al
rol correcto (y si el supervisor detecta el problema, su acción es escalarlo).

**6. La captura en sistema no es tarea aparte.** Actualizar la BD ocurre
*durante* el trabajo de campo ("levantar estatus capturando en sitio"), no como
ítem separado al día siguiente. La única excepción es el **cierre del viernes**:
actualizar todo y re-programar lo incumplido con fecha y acuerdo anotado.

**7. Compartidas con un solo dueño.** Si una tarea tiene 2-3 responsables,
asígnala en el programa al actor cuya cancha es la acción (regla 5) y no la
repitas en los demás; el otro puede aparecer como respaldo si aporta ("estar
disponible para destrabar").

**8. Estructura de la semana.** Lunes = asegurar (llamadas a proveedores,
recorridos de lo vencido); martes-miércoles = amarrar compromisos y
verificaciones intermedias; los días de compromiso = verificar en sitio;
viernes = cortes que vencen + cierre y re-programación. Balancea la carga: si el
lunes pasa de ~3-4 acciones, mueve lo no urgente a martes. Cada día lleva un
`tema` corto que resume su intención.

**9. Atrasados al frente.** Lo que lleva más tiempo sin actualizar o con fecha
vencida no se reporta como "atrasado": se convierte en la acción del lunes que
lo destraba (recorrido, llamada, exigir fecha firme).

**10. Sin emojis.** El PDF usa etiquetas de texto (Coordinar / Recorrido /
Verificar / Actualizar) y colores por frente; nada de emojis.

**11. Inventarios sin fecha se consolidan, no se enumeran.** Cuando un frente
trae muchas subtareas hermanas (recepciones/checklists por lote) sin
`fecha_inicio`/`fecha_fin_programada` y sin observaciones, NO generes una
tarjeta por subtarea: consolida en una tarjeta de coordinación por actor
("revisar la lista, priorizar los próximos a avalúo/entrega, agendar con el
proveedor/constructor"). Si son muchas y el actor las trabaja a diario,
repártelas en bloques por día (p. ej. "4 casas/día de lunes a jueves") en vez de
una sola tarjeta gigante. Para el gerente, consolida por **proveedor** (toda
Dotec en una tarjeta, toda Gidesa en otra), no por obra individual.

**12. "Recepción de claros" es un pipeline de dos etapas, no un duplicado.** Por
lote suele haber dos tareas con nombre parecido: (a) *recibir los claros al
constructor* (para que el proveedor pueda entrar a trabajar) y (b) *recibirle el
trabajo al proveedor* después. NO las trates como duplicado a depurar. La etapa
accionable de la semana es la que trae `fecha_siguiente_actualizacion`; la de
fecha nula es la etapa posterior y no se agenda todavía.

**13. Las tareas raíz no se agendan ni se "refrescan".** Una tarea padre (raíz)
es el plan de trabajo = la suma de sus subtareas; no es una acción. El
seguimiento (incluido el de lo vencido) se le da SIEMPRE a las **subtareas**, no
a la raíz. Al listar pendientes vencidos para el lunes, filtra las raíces.

**14. Vencidos/compartidos cuya palanca es de un proveedor → cancha del
gerente.** Si un lote está frenado por un proveedor externo (muretes de Dotec,
templados, filtración, anticipo, crédito del cliente), el destrabe NO va al
supervisor: va al gerente (regla 5). El supervisor solo conserva la parte de
campo (recibir/verificar en sitio una vez destrabado); si su único pendiente en
ese lote es el destrabe, el lote no aparece en su calendario.

## Frentes y colores

Agrupa las tareas raíz estratégicas en "frentes" con color estable. Paleta de
referencia (reúsala si aplican; inventa claves nuevas para frentes nuevos):
avalúo `#2563eb`, recepción de lotes `#7c3aed`, urbanización `#d97706`,
parques/amenidades `#16a34a`, vialidades/colados `#0d9488`,
convenios/autoridades `#dc2626`, recepción de claros `#be185d`.

## Verificación antes de entregar

- Cada afirmación del PDF debe ser rastreable a un campo u observación de la BD;
  si el dato es tentativo, el texto lo dice ("entrada tentativa", "sin reporte").
- 1 página por actor; tarjetas legibles (consolida lotes del mismo frente si
  hay más de ~4 tarjetas en un día).
- Conteo de acciones del encabezado = suma real de tarjetas.
