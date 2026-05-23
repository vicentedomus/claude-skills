# NPC — Referencia de Entidad

## Campos en Supabase

| Campo | Qué es | Quién lo ve |
|-------|--------|-------------|
| `primera_impresion` | Lo que el DM narra al conocer al NPC | Todos |
| `notas_roleplay` | Comportamientos, muletillas, reacciones | Solo DM |
| `edad` | Edad numérica coherente con lifespan de la raza | Todos |
| `raza` | Raza D&D 5e | Todos |
| `rol` | Función narrativa (aliado, comerciante, antagonista, etc.) | Todos |
| `nombre` | Nombre del NPC | Todos |

## Estructura del output

### Primera impresión

Lo que el DM dice en voz alta cuando los jugadores conocen al NPC. Debe:

- Describir al NPC **en movimiento** — haciendo algo, no posando
- Incluir un detalle ancla (manierismo memorable)
- Reflejar su personalidad a través de acciones, no adjetivos
- Mínimo 2 sentidos (visual + uno más)
- 2-4 oraciones, máximo

**Ejemplo validado (Flimz, gnoma de Sleh):**
> Cuando llegas al mostrador, Flimz no levanta la vista — está desenredando un carrete
> de hilo mecánico con los dientes mientras con la otra mano anota algo en un libro de
> cuentas. Huele a aceite de máquina y lavanda. "Un momento", dice sin soltar el hilo,
> y el momento dura exactamente el tiempo que le toma ganar la pelea contra el carrete.

### Notas de roleplay

Solo para el DM. Incluir:

- **Patrón de habla:** cómo estructura frases, muletillas, ritmo
- **Manierismo físico:** qué hace con las manos, cómo se mueve
- **Reacciones clave:** qué pasa si le preguntan sobre X, si lo amenazan, si le ofrecen algo
- **Relación con otros NPCs:** cómo habla de ellos, qué opina

**Ejemplo:**
> - Habla en oraciones cortas y definitivas. Nunca usa "tal vez" o "quizás".
> - Siempre tiene algo en las manos — hilo, herramienta, moneda. Si no tiene nada,
>   se inquieta visiblemente.
> - Si le mencionan a Bimble: "La presidenta sabe lo que hace. Yo sé lo que hago.
>   Funciona." (orgullo profesional, no político)
> - Si alguien toca la mercancía sin permiso: congela la sonrisa y dice "Eso tiene precio."

### Edad

Coherente con el lifespan de la raza en D&D 5e:
- Humanos: 60-80 años
- Elfos: 700-750 años
- Enanos: 350-400 años
- Gnomos: 350-500 años
- Medianos: 150 años
- Medio-elfos: 180 años
- Medio-orcos: 60-75 años
- Tieflings: 80-100 años
- Dragonborn: 80 años

La edad debe hacer sentido con el rol del NPC. Un gnomo de 45 años es un adolescente;
un humano de 45 es maduro.

## Checklist de calidad

- [ ] Está haciendo algo al conocerlo (no posando)
- [ ] Tiene detalle ancla (manierismo que los jugadores recordarán)
- [ ] Primera impresión usa mínimo 2 sentidos
- [ ] Notas de roleplay incluyen patrón de habla + reacciones
- [ ] Humor coherente con su cultura/raza
- [ ] Edad coherente con lifespan de la raza
- [ ] Conecta con al menos una otra entidad (ciudad, quest, establecimiento)
- [ ] El lore del lugar se refleja en su personalidad
