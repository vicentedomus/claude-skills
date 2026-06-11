-- Pendientes estratégicos abiertos de un desarrollo, con responsables.
-- Sustituir :DESARROLLO por el nombre (o patrón ilike) del proyecto, p.ej. '%bosco%'.
-- Proyecto Supabase: BD Domus (ifqwrtheakkvgezewxqx), vía mcp__Supabase__execute_sql.
--
-- Devuelve tareas raíz estratégicas Y sus subtareas (las subtareas heredan la
-- condición vía parent_tarea_id), abiertas (sin fecha_fin_real, avance < 1,
-- no archivadas), con todos los campos que el plan necesita interpretar.
with proy as (select id, nombre from proyectos where nombre ilike :DESARROLLO),
estr as (
  select t.* from tareas t where t.proyecto_id in (select id from proy)
    and (t.es_estrategica = true
         or t.parent_tarea_id in (select id from tareas
                                  where es_estrategica = true
                                    and proyecto_id in (select id from proy)))
    and t.archivada = false
    and t.fecha_fin_real is null
    and coalesce(t.porcentaje_avance, 0) < 1
)
select e.nombre_tarea,
       coalesce(p2.nombre_tarea, '(raíz)') as padre,
       e.porcentaje_avance,
       e.fecha_inicio,                  -- COMPROMISO, no hecho
       e.fecha_fin_programada,          -- COMPROMISO, no hecho
       e.fecha_siguiente_actualizacion, -- cuándo toca revisar/reportar
       e.fecha_ultima_actualizacion,    -- hecho: último reporte
       e.ultimas_observaciones,         -- hechos y acuerdos (con timestamp)
       e.motivo_bloqueo,
       string_agg(per.nombre || ' (' || coalesce(per.rol, '') || ')', '; ') as responsables
from estr e
left join tareas p2 on p2.id = e.parent_tarea_id
join tarea_responsables tr on tr.tarea_id = e.id
join personal per on per.id = tr.personal_id
group by e.id, e.nombre_tarea, p2.nombre_tarea, e.porcentaje_avance,
         e.fecha_inicio, e.fecha_fin_programada, e.fecha_siguiente_actualizacion,
         e.fecha_ultima_actualizacion, e.ultimas_observaciones, e.motivo_bloqueo
order by e.fecha_siguiente_actualizacion nulls last, e.fecha_fin_programada nulls last;
