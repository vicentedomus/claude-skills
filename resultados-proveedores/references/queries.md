# Consultas canónicas — Análisis de Resultados por proveedor

Se ejecutan con la tool MCP de Supabase `execute_sql`.
**Proyecto Supabase de Domus:** `ifqwrtheakkvgezewxqx`.

## Modelo de datos

```
tickets.poliza_id    -> polizas.id
polizas.proyecto_id  -> proyectos.id       (proyectos.nombre = DESARROLLO)
polizas.unidad_id    -> unidades.id        (unidades.numero_lote = LOTE, int)
tickets.zona_id      -> zonas_garantias.id (nombre = ZONA)
tickets.proveedor_id -> proveedores.id     (bigint; nombre = PROVEEDOR)
```

Campos de `tickets`: `estatus`, `prioridad`, `recurrencia` (bool), `fecha_reporte`,
`fecha_programacion`, `fecha_terminado` (todas `date`), `descripcion`, `ticket_entrega`.

> **REGLA DE ORO — nunca derives el desarrollo del número de lote.** El lote NO es
> único entre desarrollos (Capri 48 ≠ Adara 48). **Siempre** une `proyectos` y muestra
> `desarrollo + lote` juntos. Este error ya se cometió a mano una vez.

## Los tres conjuntos (definiciones FIJAS)

- **Recibidos** del mes = `fecha_reporte` dentro del mes objetivo (cualquier estatus).
  Alimentan slides de Lote, Zona, análisis cualitativo y el array `TICKETS`.
- **Terminados** del mes = `fecha_terminado` dentro del mes objetivo. Alimentan los
  KPIs (slide 9) y el array `TERMINADOS`.
- **Pendientes** = `estatus = 'Pendiente programacion'` **hoy** (todo el backlog, sin
  importar el mes). Alimentan el slide "Pendientes de Programar".

Los días (trabajo/programación, y "días esperando" de pendientes) se calculan en
**días hábiles** (lun–vie, sin descontar festivos). **No los calcules en SQL**:
`scripts/aggregates.py` los deriva en Python desde las fechas crudas, junto con
las donas, los promedios y los arrays JS. SQL solo trae las filas.

## 0. Proveedores (mapear nombre → id) + sanity de estatus

```sql
select id, nombre from proveedores order by nombre;
select estatus, count(*) from tickets group by 1 order by 2 desc;
```
Confirma el `proveedor_id` y que los estatus sigan siendo los esperados
(`Terminado`, `Pendiente programacion`, `Programado`, `Rechazado`, `No validado`).

### Conteos esperados (verifica tu JSON contra esto)

Al capturar el resultado de la consulta 1 en un archivo, es fácil soltar una fila.
Corre esto y confirma que `aggregates.py` reporta los mismos totales por `set`:

```sql
select count(*) filter (where fecha_reporte between :INI and :FIN) as recibidos,
       count(*) filter (where fecha_terminado between :INI and :FIN) as terminados,
       count(*) filter (where estatus='Pendiente programacion') as pendientes
from tickets where proveedor_id = :PV;
```

## 1. Dataset combinado del mes (LA consulta principal)

Reemplaza `:PV` (proveedor_id), `:INI` y `:FIN` (primer y último día del mes objetivo,
`'YYYY-MM-DD'`). Devuelve recibidos + terminados + pendientes en un solo arreglo, con
`set` y **desarrollo**. Guarda el JSON resultante (p. ej. `/tmp/<prov>-<mes>.json`) y
pásalo a `scripts/aggregates.py`.

```sql
with base as (
  select t.*, pr.nombre as desarrollo, u.numero_lote as lote,
         coalesce(z.nombre,'(sin zona)') as zona
  from tickets t
  join polizas p        on p.id  = t.poliza_id
  join proyectos pr     on pr.id = p.proyecto_id
  join unidades u       on u.id  = p.unidad_id
  left join zonas_garantias z on z.id = t.zona_id
  where t.proveedor_id = :PV
)
select 'recibido' as set, desarrollo, lote, zona, prioridad, recurrencia, estatus,
       fecha_reporte, fecha_programacion, fecha_terminado, descripcion
from base where fecha_reporte between :INI and :FIN
union all
select 'terminado', desarrollo, lote, zona, prioridad, recurrencia, estatus,
       fecha_reporte, fecha_programacion, fecha_terminado, descripcion
from base where fecha_terminado between :INI and :FIN
union all
select 'pendiente', desarrollo, lote, zona, prioridad, recurrencia, estatus,
       fecha_reporte, fecha_programacion, fecha_terminado, descripcion
from base where estatus = 'Pendiente programacion'
order by set, lote, fecha_reporte;
```

## 2. Baseline: terminados del mes ANTERIOR (para el comparativo de KPIs)

Mismo patrón, acotado al mes previo. Guárdalo aparte (p. ej. `/tmp/<prov>-prev.json`)
y pásalo a `aggregates.py --prev`. El comparativo mes-vs-mes se calcula **en vivo**
(reproducible). Excepción: si el mes anterior tiene un deck previo horneado a mano y
el usuario prefiere respetar esos números, úsalos y anótalo.

```sql
select 'terminado' as set, pr.nombre as desarrollo, u.numero_lote as lote,
       coalesce(z.nombre,'(sin zona)') as zona, t.prioridad, t.recurrencia, t.estatus,
       t.fecha_reporte, t.fecha_programacion, t.fecha_terminado, t.descripcion
from tickets t
join polizas p    on p.id=t.poliza_id
join proyectos pr on pr.id=p.proyecto_id
join unidades u   on u.id=p.unidad_id
left join zonas_garantias z on z.id=t.zona_id
where t.proveedor_id = :PV and t.fecha_terminado between :PREV_INI and :PREV_FIN;
```
