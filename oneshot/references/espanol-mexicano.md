# Español mexicano simple — auditar, no confiarse

El destino es **español mexicano simple**. Si escribes de corrido, se cuela español peninsular sin
que lo notes: pasó en la primera pasada completa de *Book of the Raven*, con dos casos peores que
raros — **`coger`** (vulgar en México) y **`esquivaros`**, que ni siquiera es la conjugación que
usa el DM.

Releer no lo encuentra. Un `SELECT` con `ilike` sí, en segundos.

## Comando de auditoría

```sql
with textos as (
  select nombre, coalesce(custom_data->>'cf_lectura','') || ' ' ||
         coalesce(custom_data->>'cf_mecanica','') || ' ' ||
         coalesce(descripcion_exterior,'') || ' ' || coalesce(descripcion_interior,'')
    from lugares where campaign_slug = '<slug>'
  union all select nombre, coalesce(primera_impresion,'') || ' ' || coalesce(notas_roleplay,'')
    from npcs where campaign_slug = '<slug>'
  union all select nombre, coalesce(descripcion,'') from encuentros where campaign_slug = '<slug>'
  union all select nombre, bloques::text from session_plans where campaign_slug = '<slug>'
)
select coalesce(string_agg(distinct w || ' (' || nombre || ')', ' | '), 'NADA PENDIENTE')
from textos, unnest(array[
  'coger','coge ','vosotros','esquivaros','áis ','éis ','jofaina','trastos','hurg','pillar',
  ' ocupas','puchero','mesilla','goznes','zócalo','cuerna','virote','emplumado','tachonado',
  'ganzúa','antaño','encostrad','otomana','armazón','desván','guardería','caserío','nevera',
  'coche','ordenador','fichero','vale,','tío ','chaval','follar','flipar','currar','guay'
]) w
where t ilike '%' || w || '%';
```

Para el artifact, lo mismo con `grep -oiE` sobre el HTML.

## Falsos positivos conocidos

| Patrón | Se dispara con | No es error |
|---|---|---|
| `coger` | **es**`coger`, re`coger` | sí |
| `grifo` | hipo`grifo` | sí |
| `pilla` | Pilla como nombre propio | depende |

**Lee cada coincidencia.** Contar automáticamente exagera los dos lados.

## Tabla de reemplazos

| Peninsular | México |
|---|---|
| coger | agarrar, tomar |
| jofaina | lavamanos |
| armario / ropero alto | clóset, ropero |
| mesilla | buró |
| zócalo (de pared) | moldura |
| goznes | bisagras |
| puchero | olla |
| trastos | cosas viejas, tiliches |
| hurgar | escarbar, buscar |
| pillar | captar, cachar |
| okupas | los que se metieron |
| cuerna | cornamenta |
| virote | flecha de ballesta |
| emplumado | plumas |
| tachonado | con tachuelas |
| ganzúas | herramientas de ladrón |
| desván | ático, tapanco |
| guardería (cuarto) | cuarto de juegos |
| caserío | pueblito |
| cubo (de agua) | cubeta |
| grifo | llave |
| de antaño | de antes |
| chicazo | traviesa |
| camafeo | relicario |
| armazón de cama | base de cama |
| cajón de ventana | banca bajo la ventana |
| candelabro (de mesa) | candelero |
| candelabro (de techo) | candil |
| alfombra | tapete |
| aparcar / coche | estacionar / carro |

## La sintaxis también

Traducir la prosa florida del módulo frase por frase es fiel **y a la vez ilegible** para leer en
voz alta a media partida.

> ❌ «El fantasma de las comidas de antaño sigue rondando esta cocina, atrapado para siempre en la
> madera de sus mesas, el hollín de su hogar y la mugre de sus pucheros.»
>
> ✅ «Esta cocina todavía huele a las comidas de antes: el olor se quedó en la madera de las mesas,
> en el hollín del fogón y en la mugre de las ollas.»

Frases cortas. Una idea por frase. Si tú no lo puedes leer en voz alta de corrido, el DM tampoco.

## Lo que NO se traduce

Nombres propios y términos de reglas van **en inglés verbatim** (regla del repo, `CLAUDE.md`):
Chalet Brantifax, Scarlet Sash, *charm of heroism*, Sacred Flame, Turn Undead, Sunlight
Sensitivity, los epitafios de las lápidas. En D&D el wording exacto importa para las reglas.
