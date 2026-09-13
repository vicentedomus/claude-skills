# Carril B — la one-shot original: la musa y el reskin

El carril B **no inventa de la nada y no copia**. Toma un arquetipo que ya funciona, le saca los
huesos, y le pone la carne que el DM pidió.

La diferencia con el carril A es dónde está el valor. En el A, el valor es que **sea** Candlekeep:
limarlo destruye el producto. En el B, el valor es que sea **del DM**, y copiar el nombre oficial
destruye el producto igual de rápido.

## El reskin, en una frase

> **El statblock no se toca. Cambia el nombre, la especie, la cultura y la ficción.**

Es el §8 del Lazy DM y el §8 de Flee, Mortals!. Un ejemplo real de petición del DM:

> *«Que nuestro Big Evil Guy sea Strahd pero en hombre-lobo / xoloescuintle, porque es una one-shot
> mexicana.»*

Eso **no** es «un hombre-lobo nivel Strahd». Es Strahd —sus números, su lógica, su relación con su
tierra— con otra piel. Y saber cuál es cuál es todo el trabajo de este carril.

---

## Paso 1 · Sacar los huesos

Antes de reskinear hay que saber qué **no** puede cambiar. El grafo lo dice, porque las aristas
están tipadas:

```bash
node -e "
const g = require('./compendium/graphify-out/graph.json');
const q = /strahd/i;                                   // ← lo que busques
const n = g.nodes.find(x => q.test(x.label || ''));
console.log(n.id, '|', n.label, '|', n.file_type, '|', (n.source||[]).join(','));
for (const l of g.links.filter(l => l.source === n.id || l.target === n.id))
  console.log('  ', l.relation || l.label || l.type, '→', l.source === n.id ? l.target : l.source);
"
```

Salida real para Strahd:

```
canon:strahd-von-zarovich | Strahd von Zarovich | document | AU,RHW
   bound_to                → canon:barovia
   exemplifies             → canon:gothic-horror
   exemplifies             → canon:bound-to-a-place
   exemplifies             → canon:magical-entity
   is_type                 → canon:undead
   aparece_en              → canon:death-house
   conceptually_related_to → canon:priest-of-osybus
```

Los **`exemplifies`** y el **`is_type`** son los huesos: *undead*, *gothic horror*, *atado a un
lugar*, *entidad mágica*. Lo demás (Barovia, Death House, los nombres propios) es la carne.

Un reskin que conserva los huesos sigue siendo el mismo villano y funciona igual en mesa. Uno que
tira los huesos —«Strahd pero es un mercader vivo y simpático»— no es un reskin, es otro NPC, y
entonces el statblock deja de tener sentido.

**Es el paso que se salta:** «Strahd pero xoloescuintle» conserva *undead*, *bound_to* y *gothic
horror* y solo cambia la especie; es un reskin limpio. «Strahd pero es el alcalde corrupto» rompe
`is_type: undead` y hay que decírselo al DM, no maquillarlo.

## Paso 2 · Buscar por tono, no por nombre

Cuando el DM no trae un villano concreto sino un **tono** («algo de terror en un pueblo», «una
one-shot mexicana»), se busca por comunidad. Las etiquetas están en
`compendium/graphify-out/community-labels.json` (*Gothic Horror*, *Magic as Industry*, *The
Weave*, *Calimshan*…):

```bash
node -e "
const g = require('./compendium/graphify-out/graph.json');
const L = require('./compendium/graphify-out/community-labels.json');
const tema = /gothic horror/i;
const ids = Object.entries(L).filter(([,v]) => tema.test(v)).map(([k]) => +k);
for (const n of g.nodes.filter(n => ids.includes(n.community)).slice(0, 25))
  console.log(n.community, '|', n.label, '|', (n.source||[]).join(','));
"
```

Tres capas más, con id propio y comunidad fija, que **no** son lore y se consultan directo del
JSON (no del grafo):

| Capa | Qué da | Fichero |
|---|---|---|
| `map-stub` (com. 458) | **1.047** mapas · 1.942 fichas contando variante DM y de jugadores | `compendium/map-catalog.json` + `map-index.json` |
| `npc-card` (com. 459) | **5.866** NPCs con ficha en español | `compendium/npc-catalog.json` + shards |
| `faction` (com. 460) | **491** facciones | en el propio grafo |
| Lugares | **1.055** con descripción **y read-aloud** | `compendium/place-index.json` |

## Paso 3 · Reskinear

Tres reglas, y la tercera es la que se olvida.

**a · El nombre nuevo sale de la cultura que pidió el DM, no de una lista de fantasía.** Si la
one-shot es mexicana, el villano no se llama «Kaelthor el Sombrío». Carga `dnd-worldbuilder` para
esto: es su terreno.

**b · Los huesos del paso 1 se conservan y se dicen.** Al entregar, nombra qué conservaste: *«es
Strahd: undead, atado a su tierra, gothic horror. Lo que cambia es que es un xoloescuintle y su
Barovia es un pueblo minero»*. Si el DM quiere romper un hueso, que sea su decisión.

**c · El rastro se escribe, no se recuerda.** Dos campos, y sirven para cosas distintas:

- `npcs.custom_data.cf_inspiracion` → `"<nombre de la card> (<FUENTE>)"`, con el nombre
  **original**. Es estable bajo rename, que es justo lo que un reskin provoca.
- `monstruos.base` → el nombre oficial del statblock, si el reskin necesita fila propia.

Sin rastro, dentro de un mes nadie sabe de dónde salieron los números, y el `cf_statblock` apunta a
una criatura que no se llama como el NPC.

> **Cuándo hace falta una fila de `monstruos`:** solo si el nombre reskineado tiene que aparecer en
> la iniciativa. Si no, basta el NPC con `cf_statblock` al oficial. Detalle en
> `alta-en-la-app.md` §La mesa del reskin.

## Paso 4 · Lo que el grafo NO da

El compendio es musa, no autor. Estas cuatro cosas no salen de ahí y son las que hacen la one-shot:

1. **La premisa.** Qué creen los jugadores que van a hacer vs. qué es realmente. Es del DM.
2. **El strong start.** P4b del pipeline.
3. **Los 10 secretos.** P4c. El grafo sugiere hechos del mundo; los secretos de **esta** sesión se
   escriben abstraídos.
4. **La forma de la aventura.** Si el DM no trae una, los nueve frameworks del *Lazy DM's
   Companion* (The Traitor, The Hunger, The Heist, Protect the Village, Invaders, The Keep, Hunt
   for the Relic, Vengeance for Hire, Dungeon of Shadows) están en las páginas 47-55 del PDF, y los
   diez quest templates en la 17. Ver `docs/lazy-dm-manual.md` §12.

## Lo que se hereda del carril A

No lo reinventes: **P2 (el reloj), P3 (el presupuesto), P5 (el clímax), P6 (el alta) y P7 (el
árbol) son idénticos.** Una one-shot original de 4 horas sigue siendo cinco escenas con el clímax
blindado, y se corta del medio igual.

Lo único que cambia de verdad es de dónde sale el contenido y que aquí **sí** aplica la regla de
«limar el setting» de `dnd-worldbuilder`: el mundo es del DM, no de WotC.
