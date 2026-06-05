# Ciudad — Referencia de Entidad

## Campos en Supabase

| Campo | Qué es | Quién lo ve |
|-------|--------|-------------|
| `descripcion` | Descripción narrativa única (no secciones múltiples) | Todos |
| `nombre` | Nombre de la ciudad | Todos |
| `lider` | Nombre del líder | Todos |
| `descripcion_lider` | Primera impresión del líder (misma capa que NPCs) | Todos |
| `conocida_jugadores` | Si los jugadores la conocen | Sistema |

Para notas de roleplay del líder → crear NPC separado vinculado a la ciudad.

## Estructura del output

### Descripción (campo único)

Una sola descripción rica que fluye naturalmente. NO separar en subsecciones.
Debe cubrir tres momentos en orden natural:

1. **Llegada/horizonte** — qué ves y sientes al aproximarte desde lejos
2. **Calles/ambiente** — la vida cotidiana al entrar
3. **Detalle ancla** — el elemento que define esta ciudad y la hace única

**Principios específicos para ciudades:**

- Calibrar escala: aldea ≠ ciudad comercial ≠ capital. La población y el bioma del
  lugar dictan el tono
- El gobierno y la cultura deben *sentirse*, no explicarse
- Mínimo 3 sentidos, abriendo con uno inesperado
- Incluir cómo se mueve la gente, qué se oye, qué se huele
- Si tiene bioma extremo (tundra, desierto, selva), el clima es personaje

**Ejemplo validado (Sleh, capital gnómica en taiga):**
> El primer indicio de Sleh son las columnas de vapor que se alzan entre los pinos
> nevados, como si la montaña respirara. Al cruzar la última colina, no hay murallas
> — solo talleres que empiezan donde termina el bosque, con poleas que suben piezas
> al segundo piso directamente desde barcazas en el río. El aire huele a hollín dulce
> y aceite caliente. En las calles, gnomos con delantales de cuero discuten con las
> manos llenas de tuercas, un autómata barre la plaza central con más dedicación que
> gracia, y junto a la estatua del Inventor Anónimo alguien ha dejado un prototipo
> con una nota: "Si funciona, es mío. Si explota, nunca lo vi."

### Descripción del líder

Misma estructura que `primera_impresion` de NPC (ver `npc.md`). 2-3 oraciones
de primera impresión. Si necesita notas de roleplay, crear NPC separado.

## Checklist de calidad

- [ ] Descripción es un texto fluido, no secciones separadas
- [ ] Cubre llegada → calles → detalle ancla en orden natural
- [ ] Mínimo 3 sentidos (abriendo con uno inesperado)
- [ ] Escala coherente con la población
- [ ] El gobierno/cultura se siente sin mencionarse explícitamente
- [ ] Bioma/clima como personaje (si aplica)
- [ ] Tiene detalle ancla memorable
- [ ] Humor coherente con la cultura dominante
- [ ] Menciona al menos una conexión (comercio, rivalidad, visitantes)
