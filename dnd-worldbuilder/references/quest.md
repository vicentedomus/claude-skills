# Quest — Referencia de Entidad

## Campos en Supabase

| Campo | Qué es | Quién lo ve |
|-------|--------|-------------|
| `nombre` | Nombre de la quest | Todos |
| `estado` | Activa / Completada / En pausa | Sistema |
| `resumen` | Resumen breve (1-2 oraciones) | Todos |
| `contenido_html` | Descripción completa con detalles narrativos | DM |

## Estructura del output

### Resumen

1-2 oraciones que capturan la esencia. Debe funcionar como gancho — al leerlo,
el DM sabe inmediatamente de qué trata y por qué importa.

### Contenido (para `contenido_html`)

Tres capas:

1. **Premisa** — qué está pasando y por qué los jugadores deberían importarles.
   No "alguien necesita ayuda" — qué está en juego, quién pierde si no actúan.
2. **Tensión/dilema** — la decisión difícil o el conflicto moral. Toda buena quest
   tiene un momento donde no hay respuesta fácil.
3. **Consecuencias implícitas** — qué pasa si lo ignoran, qué pasa si fallan,
   qué pasa si eligen un lado. No las digas todas — deja que el DM las revele.

**Principios específicos para quests:**

- El gancho NO es "alguien te pide un favor" — es una situación donde no actuar
  tiene consecuencias visibles
- El dilema moral es lo que la hace memorable. Sin dilema, es un fetch quest
- Conectar con al menos 2 NPCs (uno que pide, uno que complica)
- Las pistas deben tener múltiples caminos de descubrimiento
- Misterio menor: una pista que conecta con otra quest o con lore mayor

**Ejemplo:**
> **Premisa:** Los pescadores del puerto están desapareciendo de noche. No es el mar
> — los botes amanecen intactos, pero con marcas de garras en la borda. La familia
> del último desaparecido ofrece todo lo que tiene.
>
> **Tensión:** La criatura que los toma resulta ser una madre protegiendo su nido
> bajo los muelles. Los huevos eclosionan en una semana. Matarla resuelve el problema
> inmediato; reubicarla es más difícil pero los pescadores y la criatura sobreviven.
> El líder del gremio de pescadores quiere sangre.
>
> **Consecuencias:** Si matan a la madre, las crías eclosionan solas y son más
> agresivas. Si la reubican, el gremio pierde confianza en el party. Si no hacen
> nada, otro pescador desaparece en 3 días.

## Checklist de calidad

- [ ] Premisa con stakes claros (qué se pierde si no actúan)
- [ ] Tiene dilema moral o decisión sin respuesta fácil
- [ ] Conecta con mínimo 2 NPCs
- [ ] Consecuencias múltiples (no solo éxito/fracaso binario)
- [ ] Tiene misterio menor que conecta con algo mayor
- [ ] Las pistas tienen múltiples caminos de descubrimiento
- [ ] No es un fetch quest disfrazado
