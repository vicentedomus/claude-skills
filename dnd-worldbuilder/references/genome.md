# Genoma de Identidad + Extracción de la Musa

Método compartido para generar cualquier entidad: **componer un mix & match de átomos
try-and-tested del grafo compendio** (la musa), limados de setting y fusionados con coherencia.
Cada átomo es canon (lo escribió un profesional); lo original es la **combinación**.

El grafo, para esto, **no es una telaraña a traversar** — es un **catálogo de piezas probadas**
(muchos nodos-tema son hojas, degree 0-1). Se toma una pieza por slot y se funde.

---

## El genoma (5 slots — plantilla base, cada tipo lo adapta)

| Slot | Aporta |
|------|--------|
| 1 · **Vocación/función** | qué *es* (routea de dónde nace el sabor) |
| 2 · **Motor** | qué lo mueve (el "qué quiere") |
| 3 · **Distintivo** | el detalle/manierismo ancla memorable |
| 4 · **Twist** | la tensión/secreto (magnitud según disposición) |
| 5 · **Voz / motif cultural** | cómo suena; humor coherente con la cultura |

**Fusión con coherencia (evita el slop):** el motor explica la vocación · el distintivo expresa el
motor · el twist tensiona la disposición · la voz tiñe todo. Un mix aleatorio da un Frankenstein;
la identidad nace de **encadenar los átomos causalmente**.

**Mix & match:** cambiar el átomo de *un* slot y re-fusionar. La disposición dial-ea la magnitud del
twist (un neutral esconde algo pequeño; un antagonista carga un patrón entero).

---

## Enrutamiento de extracción por combinación

El grafo da tres granos: **god-nodes** (abstracciones núcleo), **hyperedges** (patrones = los
"arquetipos") y **comunidades** (clusters temáticos). Qué capa usar depende del *rol* de la entidad:

| Rol | Capa | Comando |
|-----|------|---------|
| Cotidiano (comerciante, tabernero, oficio) | comunidad / god-node de oficio o tema | `graphify explain "<tema>"` o `query "<sustantivo>"` |
| Sabor de setting (p. ej. gnómico/industrial) | god-node de raza/tema | `explain "Gnomes"`, `explain "Magic as Industry"` |
| Facción / gremio / líder | comunidad-organización | `explain "<gremio>"` |
| Antagonista / villano trágico | **hyperedge** (`GRAPH_REPORT.md`) | leer el patrón (no `explain` del nodo) |

### Reglas de extracción (verificadas contra el CLI)

1. **Sembrar con un sustantivo de función, no con prosa de atmósfera.** `query "merchant with a
   hidden past"` inunda a Ravenloft (BFS depth-2 alcanza los god-nodes de horror); `query "innkeeper"`
   aterriza limpio.
2. Para villanos, el **nodo está pelado** (degree bajo); el jugo vive en el **hyperedge**.
3. `path "A" "B"` solo funciona **intra-telaraña** (mismo setting); entre temas distintos → "No path".
4. **Limar siempre** los nombres propios Y los tags de dominio del átomo (un nodo arrastra
   "Barovia/Shatrekvan/Ravenloft"). El grafo es museo/inspiración; **Supabase es la fuente de verdad**.

Si no hay grafo disponible, seguir con los principios narrativos (`principles.md`). Lo que se tome del
grafo es *grounding de sabor*; el tono final lo dan el lore del mundo + los principios.

**Procedencia:** cuando se tome una inspiración específica, anotarla en el campo `inspiracion` del
elemento (no siempre aplica).
