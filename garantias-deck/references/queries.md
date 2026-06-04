# Consultas canónicas — garantías abiertas

Se ejecutan con la tool MCP de Supabase `execute_sql`.
**Proyecto Supabase de Domus:** `ifqwrtheakkvgezewxqx`.

Todas las fechas de antigüedad/atraso se calculan contra `current_date` (la fecha
del servidor = "hoy"). El corte de la presentación es siempre el día en que se corre.

## Modelo de datos (relaciones)

```
tickets.poliza_id    -> polizas.id
polizas.proyecto_id  -> proyectos.id      (proyectos.nombre = DESARROLLO)
polizas.unidad_id    -> unidades.id       (unidades.numero_lote = LOTE, integer)
tickets.zona_id      -> zonas_garantias.id (nombre = ZONA)
tickets.proveedor_id -> proveedores.id    (bigint; nombre = PROVEEDOR)
```

Campos de `tickets` que usamos: `estatus`, `prioridad`, `fecha_reporte` (date),
`fecha_programacion` (date), `recurrencia` (bool), `ticket_entrega` (bool),
`descripcion`.

## Definición de "abiertas" (FIJA)

Los valores reales de `estatus` en la BD (sin acentos) son:
`Terminado`, `Pendiente programacion`, `Programado`, `Rechazado`.

- **Abiertas / accionables** = `estatus IN ('Pendiente programacion','Programado')`
- **Fuera de alcance**: `Terminado` (cerradas) y `Rechazado` (no procedían).
  Se mencionan solo como contexto en el slide del embudo.
- "Vencida / atrasada" = `Programado` con `fecha_programacion < current_date`.

> Si en el futuro aparece un estatus nuevo (p. ej. `No validado`), confírmalo con
> el usuario antes de incluirlo en "abiertas".

## 0. Verificación previa (sanity check)

Confirma que los valores de estatus siguen siendo los esperados antes de calcular nada:

```sql
select estatus, count(*) as n from tickets group by estatus order by n desc;
```

## 1. Tickets abiertos enriquecidos (dataset base)

Devuelve la fila por garantía abierta con todo lo que necesitan los slides de detalle
(top antiguas / top vencidas) y permite recomputar a mano cualquier agregado.

```sql
select
  t.estatus,
  t.prioridad,
  coalesce(pr.nombre,'(sin desarrollo)') as desarrollo,
  u.numero_lote as lote,
  coalesce(z.nombre,'(sin zona)') as zona,
  coalesce(pv.nombre,'(sin proveedor)') as proveedor,
  t.fecha_reporte,
  t.fecha_programacion,
  t.recurrencia,
  t.ticket_entrega,
  (current_date - t.fecha_reporte) as dias_abierto,
  case when t.estatus='Programado' and t.fecha_programacion < current_date
       then (current_date - t.fecha_programacion) else null end as dias_atraso,
  left(coalesce(t.descripcion,''),140) as descripcion
from tickets t
left join polizas p          on p.id  = t.poliza_id
left join proyectos pr       on pr.id = p.proyecto_id
left join unidades u         on u.id  = p.unidad_id
left join zonas_garantias z  on z.id  = t.zona_id
left join proveedores pv     on pv.id = t.proveedor_id
where t.estatus in ('Pendiente programacion','Programado')
order by t.estatus, dias_atraso desc nulls last, dias_abierto desc;
```

## 2. Agregados para los slides

### Por desarrollo (slide 4)
```sql
select coalesce(pr.nombre,'(sin)') as desarrollo,
  count(*) as abiertas,
  count(*) filter (where t.estatus='Pendiente programacion') as pendientes,
  count(*) filter (where t.estatus='Programado') as programados,
  count(*) filter (where t.estatus='Programado' and t.fecha_programacion < current_date) as atrasados
from tickets t
left join polizas p on p.id=t.poliza_id
left join proyectos pr on pr.id=p.proyecto_id
where t.estatus in ('Pendiente programacion','Programado')
group by 1 order by abiertas desc;
```

### Por proveedor (slide 5)
```sql
select coalesce(pv.nombre,'(sin proveedor)') as proveedor,
  count(*) as abiertas,
  count(*) filter (where t.estatus='Pendiente programacion') as pendientes,
  count(*) filter (where t.estatus='Programado') as programados,
  count(*) filter (where t.estatus='Programado' and t.fecha_programacion < current_date) as atrasados
from tickets t
left join proveedores pv on pv.id=t.proveedor_id
where t.estatus in ('Pendiente programacion','Programado')
group by 1 order by abiertas desc;
```

### Por zona (slide 8)
```sql
select coalesce(z.nombre,'(sin zona)') as zona, count(*) as abiertas
from tickets t left join zonas_garantias z on z.id=t.zona_id
where t.estatus in ('Pendiente programacion','Programado')
group by 1 order by abiertas desc;
```

### Prioridad (slide 9)
```sql
select t.prioridad,
  count(*) filter (where t.estatus='Pendiente programacion') as pendientes,
  count(*) filter (where t.estatus='Programado') as programados
from tickets t where t.estatus in ('Pendiente programacion','Programado')
group by 1 order by 1;
```

### Buckets de antigüedad de PENDIENTES (slide 7)
```sql
with p as (select (current_date - fecha_reporte) d from tickets where estatus='Pendiente programacion')
select
  count(*) filter (where d <= 30) as d_0_30,
  count(*) filter (where d > 30 and d <= 60) as d_31_60,
  count(*) filter (where d > 60 and d <= 90) as d_61_90,
  count(*) filter (where d > 90) as d_90_plus,
  round(avg(d)) as prom_dias, max(d) as max_dias
from p;
```

### Buckets de atraso de PROGRAMADAS (slide 6)
```sql
with g as (select (current_date - fecha_programacion) atr from tickets where estatus='Programado')
select
  count(*) filter (where atr <= 0) as al_dia_o_futuro,
  count(*) filter (where atr > 0 and atr <= 7) as atr_1_7,
  count(*) filter (where atr > 7 and atr <= 30) as atr_8_30,
  count(*) filter (where atr > 30) as atr_30_plus,
  round(avg(atr) filter (where atr > 0)) as prom_atraso, max(atr) as max_atraso
from g;
```

### Recurrentes + viviendas afectadas (resumen)
```sql
select
  count(*) filter (where t.recurrencia) as recurrentes,
  count(distinct (p.proyecto_id::text || '-' || coalesce(u.numero_lote::text,'?'))) as viviendas_afectadas
from tickets t
left join polizas p on p.id=t.poliza_id
left join unidades u on u.id=p.unidad_id
where t.estatus in ('Pendiente programacion','Programado');
```

## Métricas de portada/resumen (derivadas)

- **Abiertas** = pendientes + programadas.
- **Viviendas afectadas** = `viviendas_afectadas`.
- **Vencidas** = suma de `atrasados` (= programadas con fecha pasada).
- **Estancadas (+90 días)** = `d_90_plus`.
- **Antigüedad prom. / máx para programar** = `prom_dias` / `max_dias`.
