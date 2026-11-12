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

**Último mensaje del Historial:** el deck muestra, por ticket, el mensaje escrito más reciente
del panel Historial de la app (`cargarHistorialTicket` / `renderHistorialTicketInner` en
`public/app.js`), con la misma etiqueta que usa la app. Fuentes:
`ticket_observaciones.texto` («Observación»), `ticket_cambios` de los campos de texto
`comentario_rechazo` («Motivo de rechazo»), `comentarios_terminacion` («Comentarios de cierre»)
y `motivo_exclusion` («Motivo (indicadores)»), y `ticket_pausas.motivo` («Pausado por causa del
cliente»). Los cambios sin texto (estatus, fechas, proveedor…) no son mensajes. Sale en la
tarjeta del modal y debajo de la descripción en «Pendientes de Programar».

Campos que viajan al deck además de los de siempre (spec 009): `entrega`
(= `ticket_entrega`, etiqueta «Entrega») y `obs_texto` / `obs_fecha` / `obs_tipo` (último mensaje).
`aggregates.py` los acepta ausentes (JSON viejos), así que una consulta vieja no truena: solo
sale sin etiqueta ni observación.

> **REGLA DE ORO — nunca derives el desarrollo del número de lote.** El lote NO es
> único entre desarrollos (Capri 48 ≠ Adara 48). **Siempre** une `proyectos` y muestra
> `desarrollo + lote` juntos. Este error ya se cometió a mano una vez.

## Los tres conjuntos (definiciones FIJAS)

- **Recibidos** del mes = `fecha_reporte` dentro del mes objetivo (cualquier estatus).
  Alimentan slides de Lote, Zona, análisis cualitativo y el array `TICKETS`.
- **Terminados** del mes = `fecha_terminado` dentro del mes objetivo. Alimentan los
  KPIs (slide 9) y el array `TERMINADOS`.
- **Pendientes** = `estatus = 'Pendiente programacion'` **hoy** (todo el backlog, sin
  importar el mes), **más los pausados por el cliente que estaban pendientes** (salen con la
  etiqueta «Pausado»). Alimentan el slide "Pendientes de Programar".

**Pausas y exclusiones (spec 009):** `pausas` = `[[desde, hasta|null], …]` de `ticket_pausas`;
`aggregates.py` resta sus días hábiles de los tiempos de programación y de trabajo y de los
«días esperando» (una pausa abierta se corta en la fecha de corte). `excluir` = el ticket está
marcado «No cuenta para indicadores»: sigue en lote, zona y análisis cualitativo, pero sale de
los 4 KPIs, de sus modales y del comparativo con el mes anterior.

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
       count(*) filter (where estatus='Pendiente programacion' or (estatus='Pausado' and exists (
         select 1 from ticket_pausas tp where tp.ticket_id = tickets.id and tp.hasta is null
           and tp.estatus_previo = 'Pendiente programacion'))) as pendientes
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
         coalesce(z.nombre,'(sin zona)') as zona,
         t.ticket_entrega as entrega, o.texto as obs_texto, o.tipo as obs_tipo,
         (o.fecha at time zone 'America/Merida')::date as obs_fecha,
         t.excluir_indicadores as excluir,
         (select coalesce(json_agg(json_build_array((tp.desde at time zone 'America/Merida')::date,
                                                    (tp.hasta at time zone 'America/Merida')::date) order by tp.desde), '[]'::json)
            from ticket_pausas tp where tp.ticket_id = t.id) as pausas,
         exists (select 1 from ticket_pausas tp where tp.ticket_id = t.id and tp.hasta is null
                   and tp.estatus_previo = 'Pendiente programacion') as pausado_pendiente
  from tickets t
  join polizas p        on p.id  = t.poliza_id
  join proyectos pr     on pr.id = p.proyecto_id
  join unidades u       on u.id  = p.unidad_id
  left join zonas_garantias z on z.id = t.zona_id
  left join lateral (   -- último mensaje del Historial (mismas fuentes y etiquetas que la app)
    select m.texto, m.fecha, m.tipo from (
      select ob.texto, ob.creado_el as fecha, 'Observación' as tipo
        from ticket_observaciones ob where ob.ticket_id = t.id
      union all
      select c.valor_nuevo, c.cambiado_el,
             case c.campo when 'comentario_rechazo' then 'Motivo de rechazo'
                          when 'comentarios_terminacion' then 'Comentarios de cierre'
                          else 'Motivo (indicadores)' end
        from ticket_cambios c
       where c.ticket_id = t.id and nullif(btrim(c.valor_nuevo), '') is not null
         and c.campo in ('comentario_rechazo', 'comentarios_terminacion', 'motivo_exclusion')
      union all
      select tp.motivo, tp.desde, 'Pausado por causa del cliente'
        from ticket_pausas tp where tp.ticket_id = t.id and nullif(btrim(tp.motivo), '') is not null
    ) m order by m.fecha desc limit 1) o on true
  where t.proveedor_id = :PV
)
select 'recibido' as set, desarrollo, lote, zona, prioridad, recurrencia, estatus,
       fecha_reporte, fecha_programacion, fecha_terminado, descripcion, entrega, obs_texto, obs_fecha, obs_tipo, excluir, pausas
from base where fecha_reporte between :INI and :FIN
union all
select 'terminado', desarrollo, lote, zona, prioridad, recurrencia, estatus,
       fecha_reporte, fecha_programacion, fecha_terminado, descripcion, entrega, obs_texto, obs_fecha, obs_tipo, excluir, pausas
from base where fecha_terminado between :INI and :FIN
union all
select 'pendiente', desarrollo, lote, zona, prioridad, recurrencia, estatus,
       fecha_reporte, fecha_programacion, fecha_terminado, descripcion, entrega, obs_texto, obs_fecha, obs_tipo, excluir, pausas
from base where estatus = 'Pendiente programacion' or (estatus = 'Pausado' and pausado_pendiente)
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
       t.fecha_reporte, t.fecha_programacion, t.fecha_terminado, t.descripcion,
       t.ticket_entrega as entrega, t.excluir_indicadores as excluir,
       (select coalesce(json_agg(json_build_array((tp.desde at time zone 'America/Merida')::date,
                                                  (tp.hasta at time zone 'America/Merida')::date) order by tp.desde), '[]'::json)
          from ticket_pausas tp where tp.ticket_id = t.id) as pausas
from tickets t
join polizas p    on p.id=t.poliza_id
join proyectos pr on pr.id=p.proyecto_id
join unidades u   on u.id=p.unidad_id
left join zonas_garantias z on z.id=t.zona_id
where t.proveedor_id = :PV and t.fecha_terminado between :PREV_INI and :PREV_FIN;
```
