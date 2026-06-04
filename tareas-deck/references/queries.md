# Consultas canónicas — tareas de obra (deck de seguimiento)

Se ejecutan con la tool MCP de Supabase `execute_sql`.
**Proyecto Supabase de Domus:** `ifqwrtheakkvgezewxqx`.

El corte de la presentación es siempre **hoy** (`current_date`, fecha del servidor).
Toda antigüedad/atraso se calcula contra `current_date`.

## Modelo de datos (relaciones)

```
tareas.proyecto_id        -> proyectos.id      (proyectos.nombre = DESARROLLO; "Adara", etc.)
tareas.parent_tarea_id    -> tareas.id         (null = tarea padre; si no, subtarea)
tarea_responsables        (tarea_id, personal_id)  -> personal.id   (M2M; una tarea puede tener varios)
tarea_dependencias        (tarea_id, depende_de_id, tipo, bloqueante)  predecesoras entre tareas
reportes_avance.tarea_id  -> tareas.id         (bitácora de avances)
reporte_responsables      (reporte_id, personal_id) -> personal.id   (quién reportó)
```

Campos de `tareas` que usamos: `nombre_tarea`, `area` (texto libre, **muy incompleto**),
`prioridad`, `porcentaje_avance`, `fecha_inicio`, `fecha_fin_programada`, `fecha_fin_real`,
`fecha_siguiente_actualizacion`, `fecha_ultima_actualizacion`, `proveedor` (array text),
`ultimas_observaciones`, `motivo_bloqueo`, `archivada`.

### ⚠️ Escala de `porcentaje_avance` (CRÍTICO)

Se guarda como **fracción 0–1** (no 0–100). `0.5` = 50%, `1` = 100%. El slider del
frontend va 0–100 pero al guardar se divide. **Para mostrar en %: `round(porcentaje_avance*100)`.**
- Completa = `porcentaje_avance >= 1`
- En proceso = `porcentaje_avance > 0 and < 1`
- Sin iniciar = `coalesce(porcentaje_avance,0) = 0`

### Definición de "activas" (FIJA)

- **Activas / accionables** = `archivada = false`.
- Las archivadas (`archivada = true`) quedan fuera de **toda** estadística — ni siquiera
  se mencionan como contexto (no es señal accionable). Todas las queries de abajo filtran
  `not archivada`; replícalo si agregas una nueva.
- "Completa sin archivar" (avance=1 pero no archivada) **sí** cuenta como activa, pero es
  candidata a higiene (cerrarla). Sepárala en el slide de reportes vencidos (popup
  "X al 100% por cerrar").

### Definición de "atraso" (FIJA)

- **Criterio principal:** `fecha_siguiente_actualizacion < current_date AND porcentaje_avance < 1`
  → "pendientes con reporte vencido". Es el número que lidera el deck (slide 2 + Foco 1).
- **Criterio secundario:** `fecha_fin_programada < current_date AND porcentaje_avance < 1`
  → "vencidas por fecha". Aparece en Foco 2 y como contexto en el slide de estado, pero
  no es el headline.

### Excluir **tareas padre** de las métricas de seguimiento (FIJA)

Una "tarea padre" es la que tiene subtareas (existe otra fila con `parent_tarea_id = id`).
**Los reportes de avance se cargan a nivel subtarea**, no en el padre — así que el padre
siempre aparece como "sin actualizar" aunque las subtareas estén al día. Es un falso
positivo.

Aplica este filtro a **toda métrica de seguimiento** (reporte vencido y frescura),
pero **no** a las métricas de carga (por responsable, por área, conteo de activas):

```sql
-- CTE reutilizable:
with adara as (select * from tareas where proyecto_id=':PID' and not archivada),
     parents as (select distinct parent_tarea_id as id from adara where parent_tarea_id is not null)
-- y luego: where id not in (select id from parents)
```

**No** apliques este filtro a "vencidas por fecha" (Foco 2) ni a "sin fecha de cierre"
(Foco 3 izquierda) — la fecha de fin sí es significativa para un padre.

## Parámetro del deck

El proyecto objetivo se fija por `proyecto_id`. Para Adara:
`38467911-110f-4bb9-818c-a4cc9161f4f0`. Confírmalo con la tabla `proyectos` por si cambia:

```sql
select id, nombre from proyectos order by nombre;
```

Sustituye `:PID` por el `proyecto_id` en todas las consultas de abajo.

## 0. Sanity check (escala + estados)

Confirma que el avance sigue siendo 0–1 y mira la distribución antes de calcular nada:

```sql
select porcentaje_avance, count(*) n
from tareas where proyecto_id=':PID' and not archivada
group by 1 order by 1;
```

## 1. Resumen ejecutivo (KPIs + frescura)

```sql
with adara as (select * from tareas where proyecto_id=':PID' and not archivada),
     parents as (select distinct parent_tarea_id as id from adara where parent_tarea_id is not null)
select
  count(*) as activas,
  count(*) filter (where porcentaje_avance>=1) as completas,
  count(*) filter (where porcentaje_avance>0 and porcentaje_avance<1) as en_proceso,
  count(*) filter (where coalesce(porcentaje_avance,0)=0) as sin_iniciar,
  round(avg(porcentaje_avance)*100)::int as avance_pct,
  count(*) filter (where fecha_fin_programada < current_date and porcentaje_avance<1) as vencidas,
  count(*) filter (where fecha_fin_programada is null) as sin_fecha_fin,
  count(*) filter (where fecha_fin_programada is null and porcentaje_avance<1) as sin_fecha_fin_pend,
  -- Reporte vencido, FILTRADO: solo hojas (no padres). Es el número que lidera el deck.
  count(*) filter (where fecha_siguiente_actualizacion < current_date and porcentaje_avance<1
                         and id not in (select id from parents)) as rep_venc_pend_hojas,
  count(*) filter (where fecha_siguiente_actualizacion < current_date and porcentaje_avance<1
                         and id in (select id from parents)) as rep_venc_pend_padres,
  count(*) filter (where fecha_siguiente_actualizacion < current_date and porcentaje_avance>=1) as rep_venc_100,
  -- Frescura: solo hojas pendientes
  count(*) filter (where porcentaje_avance<1 and id not in (select id from parents)
                         and fecha_ultima_actualizacion >= current_date-7) as fresca_7d,
  count(*) filter (where porcentaje_avance<1 and id not in (select id from parents)
                         and fecha_ultima_actualizacion < current_date-7
                         and fecha_ultima_actualizacion >= current_date-30) as fresca_8_30,
  count(*) filter (where porcentaje_avance<1 and id not in (select id from parents)
                         and fecha_ultima_actualizacion < current_date-30) as fresca_30plus,
  count(*) filter (where porcentaje_avance<1 and id not in (select id from parents)
                         and fecha_ultima_actualizacion is null) as nunca_act,
  count(*) filter (where porcentaje_avance<1 and id not in (select id from parents)) as elegibles_frescura
from adara;
```

## 2. Por responsable (slide de barras apiladas)

Una tarea puede tener varios responsables → los conteos **se traslapan** (suman > activas).
Decláralo en el pie del slide.

```sql
select coalesce(p.nombre,'(sin responsable)') as responsable,
  count(*) filter (where not t.archivada) as activas,
  count(*) filter (where not t.archivada and t.porcentaje_avance>=1) as completas,
  count(*) filter (where not t.archivada and t.porcentaje_avance>0 and t.porcentaje_avance<1) as en_proceso,
  count(*) filter (where not t.archivada and coalesce(t.porcentaje_avance,0)=0) as sin_iniciar,
  count(*) filter (where not t.archivada and t.fecha_fin_programada < current_date and t.porcentaje_avance<1) as vencidas,
  round(avg(t.porcentaje_avance) filter (where not t.archivada)*100)::int as avance_pct
from tareas t
left join tarea_responsables tr on tr.tarea_id=t.id
left join personal p on p.id=tr.personal_id
where t.proyecto_id=':PID'
group by 1 order by activas desc;
```

## 3. Foco 1 · Vencidas (fin programado pasado y <100%)

```sql
select t.nombre_tarea, coalesce(nullif(t.area,''),'—') as area,
  round(t.porcentaje_avance*100)::int as avance_pct,
  t.fecha_fin_programada, (current_date - t.fecha_fin_programada) as dias_atraso,
  (select string_agg(p.nombre,', ') from tarea_responsables tr join personal p on p.id=tr.personal_id where tr.tarea_id=t.id) as responsable,
  left(coalesce(t.ultimas_observaciones,''),90) as obs
from tareas t
where t.proyecto_id=':PID' and not t.archivada
  and t.fecha_fin_programada < current_date and coalesce(t.porcentaje_avance,0) < 1
order by dias_atraso desc;
```

### Dependencias (para detectar cadenas que se destraban juntas)

```sql
select ta.nombre_tarea as tarea, tb.nombre_tarea as depende_de, td.tipo, td.bloqueante
from tarea_dependencias td
join tareas ta on ta.id=td.tarea_id
join tareas tb on tb.id=td.depende_de_id
where ta.proyecto_id=':PID' or tb.proyecto_id=':PID';
```

> Ojo: a veces el bloqueo real está en las **observaciones** (p. ej. "sin luz no se
> puede recibir el riego"), no en una fila de `tarea_dependencias`. Lee las obs de las
> vencidas para armar la cadena.

## 4. Foco 2 · Seguimiento vencido (siguiente actualización pasada)

Separa las que ya están al 100% (solo cerrar) de las pendientes reales.

```sql
select t.nombre_tarea, coalesce(nullif(t.area,''),'—') as area,
  round(coalesce(t.porcentaje_avance,0)*100)::int as avance_pct,
  t.fecha_siguiente_actualizacion as sig_act,
  (current_date - t.fecha_siguiente_actualizacion) as dias_sig_vencida,
  t.fecha_ultima_actualizacion as ult_act,
  (select string_agg(p.nombre,', ') from tarea_responsables tr join personal p on p.id=tr.personal_id where tr.tarea_id=t.id) as responsable
from tareas t
where t.proyecto_id=':PID' and not t.archivada
  and t.fecha_siguiente_actualizacion < current_date
order by (t.porcentaje_avance>=1), dias_sig_vencida desc;
```

## 5. Foco 3 · Sin fecha de cierre + las pendientes sueltas

```sql
select t.nombre_tarea, coalesce(nullif(t.area,''),'—') as area,
  round(coalesce(t.porcentaje_avance,0)*100)::int as avance_pct,
  (select string_agg(p.nombre,', ') from tarea_responsables tr join personal p on p.id=tr.personal_id where tr.tarea_id=t.id) as responsable,
  t.fecha_ultima_actualizacion as ult_act
from tareas t
where t.proyecto_id=':PID' and not t.archivada
  and t.fecha_fin_programada is null and coalesce(t.porcentaje_avance,0) < 1
order by t.porcentaje_avance asc nulls first, t.fecha_ultima_actualizacion asc nulls first;
```

## 6. Por área (slide de barras horizontales por avance)

`area` es texto libre y está **muy incompleto** (la mayoría sin área). Agrupa y reporta
también cuántas no tienen área (suele ser una señal de proceso para el deck).

```sql
with a as (select *, coalesce(nullif(area,''),'(sin área)') as area_n
           from tareas where proyecto_id=':PID' and not archivada)
select area_n as area,
  count(*) as activas,
  round(avg(porcentaje_avance)*100)::int as avance_pct,
  count(*) filter (where coalesce(porcentaje_avance,0)=0) as sin_iniciar
from a group by 1 order by activas desc;
```

## 7. Por responsable × estado (popups del slide 4)

Devuelve cada tarea repetida por responsable + estado. Para cada uno de los 9 segmentos
del slide 4 (3 responsables × 3 estados), filtra el resultado por la pareja correspondiente
y carga la lista en `TASKS.<resp>_<estado>` del objeto del template.

```sql
select p.nombre as resp,
  case when coalesce(t.porcentaje_avance,0)>=1 then 'comp'
       when t.porcentaje_avance>0 and t.porcentaje_avance<1 then 'proc'
       else 'sin' end as estado,
  t.nombre_tarea as n,
  coalesce(nullif(t.area,''),'—') as a,
  round(coalesce(t.porcentaje_avance,0)*100)::int as p
from tareas t
join tarea_responsables tr on tr.tarea_id=t.id
join personal p on p.id=tr.personal_id
where t.proyecto_id=':PID' and not t.archivada
  and p.nombre in ('Jorge Aguilar','Eduardo Flores','Israel Cardenas')
order by p.nombre, 2, t.nombre_tarea;
```

## 8. Las N tareas al 100% con reporte vencido (popup "+N por cerrar")

Son las "completas sin archivar" que también tienen seguimiento vencido — el "+N por
cerrar" del slide 5. Recuento debe coincidir con el número clickable.

```sql
select t.nombre_tarea as n, coalesce(nullif(t.area,''),'—') as a,
  (current_date - t.fecha_siguiente_actualizacion) as dias,
  (select string_agg(pp.nombre,', ') from tarea_responsables tr join personal pp on pp.id=tr.personal_id where tr.tarea_id=t.id) as r
from tareas t
where t.proyecto_id=':PID' and not t.archivada
  and t.fecha_siguiente_actualizacion < current_date and t.porcentaje_avance >= 1
order by dias desc;
```

## 9. Frescura por bucket (popups del slide 7)

Devuelve **solo las hojas pendientes** (≤25 tareas, no las ~74 totales): excluye completas
(`porcentaje_avance>=1`) y padres (los reportes se cargan en sus subtareas). Filtra por
bucket y carga cada lista en `TASKS.fresca_<bucket>` del template. Sanity: la suma de los
4 buckets = total de elegibles (= consulta 1 `elegibles_frescura`).

```sql
with adara as (select * from tareas where proyecto_id=':PID' and not archivada),
     parents as (select distinct parent_tarea_id as id from adara where parent_tarea_id is not null)
select
  case
    when fecha_ultima_actualizacion is null then 'nunca'
    when fecha_ultima_actualizacion >= current_date - 7 then 'd7'
    when fecha_ultima_actualizacion >= current_date - 30 then 'd30'
    else 'd30plus' end as bucket,
  t.nombre_tarea as n, coalesce(nullif(t.area,''),'—') as a,
  round(coalesce(t.porcentaje_avance,0)*100)::int as p,
  t.fecha_ultima_actualizacion as ult,
  (select string_agg(pp.nombre,', ') from tarea_responsables tr join personal pp on pp.id=tr.personal_id where tr.tarea_id=t.id) as r
from adara t
where t.porcentaje_avance < 1
  and t.id not in (select id from parents)
order by 1, t.fecha_ultima_actualizacion desc nulls last, t.nombre_tarea;
```

### Foco 1 · Reportes vencidos (hojas pendientes)

Para alimentar el slide 5 y el KPI principal. **Excluye padres** por la misma razón.

```sql
with adara as (select * from tareas where proyecto_id=':PID' and not archivada),
     parents as (select distinct parent_tarea_id as id from adara where parent_tarea_id is not null)
select t.nombre_tarea, coalesce(nullif(t.area,''),'—') as area,
  round(t.porcentaje_avance*100)::int as avance_pct,
  (current_date - t.fecha_siguiente_actualizacion) as dias,
  (select string_agg(pp.nombre,', ') from tarea_responsables tr join personal pp on pp.id=tr.personal_id where tr.tarea_id=t.id) as responsable
from adara t
where t.fecha_siguiente_actualizacion < current_date and t.porcentaje_avance < 1
  and t.id not in (select id from parents)
order by dias desc;
```

## Notas de cálculo para los slides

- **Anchos de barras apiladas (slide responsable):** ancho del `.track` = `activas_fila /
  max_activas * 100%`; ancho de cada `.seg` = `count_seg / activas_fila * 100%`.
- **Alturas de buckets (frescura):** altura = `valor / max_bucket * 100%`.
- **Barras por área:** el `.zfill` se llena al `avance_pct` (no al conteo); marca en rojo
  (`.zfill.low`) las áreas con avance bajo y en ámbar (`.zfill.mid`) las intermedias.
- Trabaja con los números **exactos** de la BD. Si un agregado se ve raro, vuelve a consultar.
