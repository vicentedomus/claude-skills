# Item — Referencia de Entidad

## Campos en Supabase

| Campo | Qué es | Quién lo ve |
|-------|--------|-------------|
| `nombre` | Nombre del item | Todos |
| `tipo` | Arma, armadura, poción, objeto maravilloso, etc. | Todos |
| `rareza` | Común, poco común, raro, muy raro, legendario | Todos |
| `descripcion` | Descripción narrativa | Todos |
| `personaje_id` | Personaje jugador que lo posee | Sistema |
| `npc_portador_id` | NPC que lo posee | Sistema |
| `conocido_jugadores` | Si los jugadores lo conocen | Sistema |

## Estructura del output

### Descripción

Tres capas:

1. **Apariencia** — cómo se ve en reposo. No es una ficha de catálogo — es lo que
   notas cuando lo ves por primera vez. El detalle ancla visual.
2. **Sensación** — qué pasa al tocarlo o usarlo. Peso, temperatura, textura, sonido.
   Los items mágicos deben *sentirse* mágicos sin decir "es mágico".
3. **Historia/leyenda** — de dónde viene, quién lo hizo, por qué importa. No toda
   la historia — solo lo que se sabe o se rumorea. Dejar huecos.

**Principios específicos para items:**

- El detalle ancla es sensorial (cómo se siente, qué sonido hace, qué cambia al usarlo)
- El gancho es el costo o la consecuencia inesperada
- La rareza se refleja en la descripción, no se anuncia
- Items legendarios DEBEN conectar con la historia del mundo
- No decir "brilla mágicamente" — describir la manifestación concreta

**Ejemplo:**
> **Apariencia:** Un anillo de hierro sin adornos, excepto por una grieta que lo
> recorre de punta a punta — como si alguien lo hubiera roto y soldado mal.
> La grieta cambia de posición cada vez que lo miras.
>
> **Sensación:** Pesa más de lo que debería. Al ponértelo, el dedo se enfría
> y escuchas un susurro — no palabras, más bien la intención de palabras.
> El susurro se calla si lo ignoras. Se intensifica si prestas atención.
>
> **Historia:** Los enanos de Kord lo llaman "la Opinión". Dicen que perteneció
> a un juez que nunca se equivocó — hasta que lo hizo. Nadie cuenta qué pasó
> después. Lo que sí cuentan es que el anillo gritó "no eres digno" al último
> que intentó ponérselo en la feria de Grimholt.

## Checklist de calidad

- [ ] Detalle ancla sensorial (no solo visual)
- [ ] La magia se siente, no se anuncia
- [ ] Tiene consecuencia o costo al usarlo (gancho)
- [ ] Historia con huecos (invita a investigar)
- [ ] Rareza reflejada en la descripción, no etiquetada
- [ ] Conecta con el mundo (quién lo hizo, de dónde viene)
- [ ] Si es legendario, conecta con lore mayor
