# Vocabulario del árbol — bloques y convenciones de halo

El plan de una sesión es un **árbol de bloques** en el Planeador (spec 007 de questkeep). Este
archivo **no es una plantilla**: cada sesión decide su forma en el Paso 3a. Aquí está el vocabulario
—qué hace cada bloque y cuándo conviene— y las convenciones de texto que el DM ya usa en mesa.

**El JSON y cómo se escribe** viven en `../../oneshot/references/plantilla-arbol.md` (campos por
tipo, `hijos` siempre presente, texto plano, menciones, reglas de la rama, verificación). No se
duplican aquí.

## Los bloques

| Tipo | Qué guarda | Úsalo para |
|---|---|---|
| `texto` | `texto` plano con `@[Nombre](seccion:uuid)` | Cada beat de la sesión, y todo lo que se lee o se consulta |
| `checklist` | `items: [{t, ok}]` | El SEGUIMIENTO de arriba y los secretos que salieron |
| `rama` + `ruta` | `texto`; una ruta `probable` | Una decisión con caminos que el DM quiere tener escritos. Nace con dos rutas |
| `encuentro` | `encuentroId` → `encuentros` | El combate. Lee monstruos, mesa y dificultad **en vivo** |
| `mapa` | `mapaId` → `mapa_nodos` | El plano de una escena |
| `npc` · `lugar` · `ciudad` · `establecimiento` · `quest` · `tesoro` · `statblock` | `refId` | La ficha viva de lo que aparece en el beat. Sin hijos se pinta como **chip en línea** |

No uses `nota` ni `peligro`: el DM los retiró del catálogo (2026-08-26). Un peligro de combate va
**en el encuentro** (`encuentros.hazards`), no como bloque.

## La espina que funciona en mesa

Un ejemplo, no un molde (sesión de viaje de 3h, halo 21-oct-26):

```
☑ SEGUIMIENTO — lo que ya pasó en mesa         badge «EN MESA», verde
▸ 1 · APERTURA — El atracadero vacío           badge «0:00 · 15 min»
    └ chips: Aukan · Sleh · El rescate de Brenna
▸ 2 · EL ARCHIVO DE RAMMEL                     badge «0:15 · 35 min · ✂»
    └ chips: Rammel · Torben · Orvo · Pim · Capitanía del Canal
▸ 3 · CAMINO A LAS CUMBRES                     badge «0:50 · 25 min · ✂»
▸ 4 · LA CACERÍA                               badge «1:15 · 60 min · NO SE CORTA», rojo
    └ chips: El Pasto Alto · Tavra  +  [encuentro]
▸ 5 · GANCHO — banderas de Khaz-Alun           badge «2:15 · 20 min»
▸ 6 · LOS SECRETOS — referencia                badge «DM · referencia», gris, plegado
    └ ☑ Cuáles salieron
```

- **El reloj va en el badge** (hora de inicio · duración · `✂` si se puede recortar). El índice
  del Planeador muestra badge + título de cada raíz: se lee como escaleta.
- **En campaña larga el último beat es un gancho**, no un cierre: siembra la siguiente sesión.
- Sesión **de viaje o investigación** → lista de beats. Sesión **en un sitio** (torreón, barco,
  mansión) → una situación: locación + habitantes con su comportamiento + meta.

## Las etiquetas dentro de un `texto`

El texto es plano: lo que estructura un beat son etiquetas en mayúsculas y separadores
(`────────────────────────────────`). Las que el DM ya reconoce:

| Etiqueta | Qué va debajo |
|---|---|
| `GLOSARIO —` | La definición de un término inventado que aparece en este bloque. Arriba del todo |
| `LEE EN VOZ ALTA:` | El párrafo literal, entre «». Nunca un puntero a otra ficha |
| `QUÉ LA DISPARA:` · `QUÉ QUIEREN:` · `QUÉ SE LLEVAN:` | La escena en tres líneas |
| `LO QUE TÚ SABES Y ELLOS NO:` | Lo que es solo del DM |
| `SI VAS TARDE (✂):` | Qué se corta y cómo se resume |
| `MENÚ DE SUCESOS` | En un viaje: 2-3 sucesos para elegir según el ritmo |
| `CÓMO SALE DE ESCENA` | Pocas salidas (normalmente dos), cada una con `Siguiente sesión:` |
| `SECRETOS QUE PUEDEN SALIR AQUÍ` | `· N · <una línea> → <la semilla de esta escena>` |
| `DETALLE ANCLA:` | Lo que la mesa va a repetir de una criatura o un NPC |

Las menciones `@[Nombre](seccion:uuid)` son el único marcado que se pinta. Úsalas para toda
entidad que ya tenga fila (NPCs, PJs como `personajes`, lugares, ciudades, quests).

## El combate en el árbol

El Encounter Axis (`../../dnd-worldbuilder/references/combate.md`) sigue siendo el criterio de
diseño, pero ya no tiene campo propio: el Protein y los ejes se escriben **en el texto del beat**,
y lo que pasa en una ronda concreta va como **peligro** del encuentro (una tirada de sigilo, la
llegada de un NPC, el monstruo oculto que un peligro con `revela` destapa). El bloque `encuentro`
cuelga del beat del combate. Las notas tácticas como `texto` hijos, solo si el DM las quiere.
