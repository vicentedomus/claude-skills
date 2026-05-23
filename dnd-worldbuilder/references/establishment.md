# Establecimiento — Referencia de Entidad

## Campos en Supabase

| Campo | Qué es | Quién lo ve |
|-------|--------|-------------|
| `descripcion_exterior` | Lo que ves/oyes/hueles desde la calle | Todos |
| `descripcion_interior` | Lo que encuentras al entrar | Todos |
| `nombre` | Nombre del establecimiento | Todos |
| `tipo` | Taberna, tienda, templo, gremio, etc. | Todos |
| `ciudad_id` | Ciudad donde está | Todos |
| `dueno_id` | NPC dueño (FK a npcs) | Todos |

El dueño se genera/mejora como NPC separado (ver `npc.md`). La descripción del
establecimiento debe reflejar la personalidad del dueño sin duplicar su ficha.

## Estructura del output

### Descripción exterior

Lo que los jugadores perciben al acercarse. Es el **primer gancho** — determina si
entran o no. Debe:

- Abrir con un sentido inesperado (sonido o aroma desde la calle)
- Dar pistas de qué hay adentro
- Incluir el detalle ancla del exterior (letrero, arquitectura, algo fuera de lugar)
- 2-3 oraciones

**Ejemplo validado (GnomeDepot, tienda en Sleh):**
> Antes de ver el letrero ya hueles el aceite de máquina mezclado con lavanda. Un cartel
> de madera con engranajes reales que giran dice "SI NO GIRA, NO SIRVE — GnomeDepot".
> La puerta tiene una manivela en vez de picaporte, y al girarla suena una campanilla
> que toca tres notas distintas cada vez.

### Descripción interior

Lo que encuentras al cruzar la puerta. Debe:

- Continuar la experiencia sensorial del exterior (no reiniciar)
- Incluir al menos 3 sentidos
- Tener un gancho de interacción (algo que el jugador puede tocar/usar/probar)
- Reflejar la personalidad del dueño en el orden, decoración y estado del lugar
- 3-5 oraciones

**Ejemplo:**
> Adentro, el desorden tiene sistema: cajones etiquetados con símbolos que solo Flimz
> entiende, carretes de hilo mecánico colgando del techo como cortinas, y una vitrina
> con tres manivelas — cada una sirve un tipo distinto de aceite de engranaje.
> Al fondo, una gaveta dorada cerrada con un candado que no tiene cerradura visible.
> "No preguntes por la gaveta", dice Flimz antes de que preguntes.

### Conexiones sugeridas

Al generar un establecimiento, sugerir al menos una conexión:
- Item especial que conecta con una quest
- NPC que frecuenta el lugar (además del dueño)
- Rumor o pista que se puede descubrir aquí
- Rivalidad o relación con otro establecimiento de la ciudad

## Checklist de calidad

- [ ] Exterior abre con sentido no-visual
- [ ] Exterior tiene detalle ancla (letrero, sonido, algo memorable)
- [ ] Interior usa mínimo 3 sentidos
- [ ] Interior tiene gancho de interacción
- [ ] La personalidad del dueño se siente en el espacio
- [ ] Humor coherente con la cultura del lugar
- [ ] Al menos un misterio menor ("la gaveta sin cerradura")
- [ ] Conecta con al menos una otra entidad
