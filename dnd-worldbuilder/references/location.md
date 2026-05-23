# Lugar — Referencia de Entidad

## Campos en Supabase

| Campo | Qué es | Quién lo ve |
|-------|--------|-------------|
| `descripcion` | Descripción narrativa del lugar | Todos |
| `nombre` | Nombre del lugar | Todos |
| `tipo` | Ruina, cueva, bosque, templo, etc. | Todos |
| `region` | Región/zona del mapa | Todos |
| `ciudad_id` | Ciudad asociada (si aplica) | Todos |
| `conocido_jugadores` | Si los jugadores lo conocen | Sistema |

## Estructura del output

### Descripción

Tres capas en orden natural:

1. **Aproximación** — qué perciben antes de llegar (sonidos lejanos, cambio en el aire,
   señales en el terreno)
2. **Interior/exploración** — lo que encuentran al entrar o explorar
3. **Peligros/recompensas implícitas** — señales de lo que habita o se esconde aquí
   (marcas en las paredes, huesos, brillo en la oscuridad)

**Principios específicos para lugares:**

- Los lugares salvajes tienen personalidad propia — el bosque *quiere* algo, la cueva
  *esconde* algo, la ruina *recuerda* algo
- Si un monstruo habita aquí, sus marcas deben ser visibles antes del encuentro
- El peligro se sugiere, no se anuncia
- Incluir al menos un elemento interactivo (altar, mecanismo, inscripción)
- Mínimo 3 sentidos, con énfasis en los que generan tensión

**Ejemplo:**
> El sendero se estrecha y los árboles dejan de hacer ruido. No es silencio — es que
> algo los calló. El suelo tiene marcas de garras que van en una dirección y no vuelven.
> Al fondo del claro, una entrada de piedra cubierta de musgo que huele a cobre
> y algo orgánico. Junto a la entrada, una antorcha apagada — pero el soporte está
> tibio al tacto.

## Checklist de calidad

- [ ] Aproximación establece el tono antes de llegar
- [ ] Mínimo 3 sentidos (priorizando los que generan tensión)
- [ ] Si hay monstruo residente, sus marcas son visibles
- [ ] Tiene al menos un elemento interactivo
- [ ] El peligro se sugiere, no se dice explícitamente
- [ ] Tiene misterio menor (algo sin explicación inmediata)
- [ ] Conecta con el contexto del mundo (quién construyó esto, por qué está abandonado)
