# Taxonomía de extracción — el compendio es un pozo de *flavor*

> **Propósito (leer primero).** Este compendio NO es una referencia mecánica: los statblocks,
> items y reglas viven en el repo (Supabase / `monstruos` / `items_catalog`) y esa es la fuente de
> verdad. El compendio es **la musa**: existe para dar *flavor, tono, atmósfera y arquetipos* al
> mundo. Por eso la extracción prioriza lo **evocador** (qué inspira, qué tono tiene, qué lo hace
> memorable) por encima de lo puramente estructural. Las criaturas/items que aparecen son
> **punteros de flavor** ("este dominio tiene un Wraith") que remiten al repo para los números.

Cada archivo del corpus abre con `> kind: <kind> · source: <ID>`. El `kind` indica qué tipo de
entidad domina el archivo y guía qué extraer.

## La columna vertebral: temas, tono y arquetipos (cross-book)

Lo que conecta libros distintos y dispara inspiración **no son los nombres propios**, sino los
**temas, tonos y patrones** compartidos. Extrae siempre, cuando aplique:

- **`theme`** — el género/tema narrativo, generalizado más allá del horror: *Gothic Horror, Cosmic
  Horror, Body Horror, Folk Horror, Political Intrigue, Frontier Survival, Mythic/Divine, Planar
  Weird, Heist, War*, etc. Son los **hubs cross-book**: una entidad de cualquier libro debe colgar
  de su(s) tema(s) vía `has_theme`/`exemplifies`.
- **`tone`/`motif`** — el sabor sensorial y emocional recurrente: *niebla que aísla, campanas que
  hacen olvidar, putrefacción dulzona, esplendor decadente, paranoia de pueblo pequeño, asombro
  cósmico*. Captúralos como nodos `motif` y conéctalos con `evokes`. Son lo que un DM roba para
  describir una escena.

Si un libro no declara géneros (p. ej. un setting), **infiere igualmente el/los `theme` y los
`motif`** dominantes de cada región/facción/dominio — ahí está el flavor.

## Tipos de nodo por `kind`

| kind | nodos a extraer (con su flavor) |
|------|-----------------|
| `domain` / `region` | el DOMINIO/REGIÓN; su gobernante (DARKLORD/líder); LOCALIZACIONES con su detalle evocador; CRIATURAS referidas; su(s) `theme` y `motif`; (Ravenloft: cartas Tarokka) |
| `theme` / `genre` | el TEMA/género como nodo; sus TROPOS (`has_trope`); el tono que produce; ejemplares que lo encarnan |
| `organization` | la FACCIÓN: su agenda, métodos, estética/tono, líderes, rivalidades; el `theme` que encarna (intriga, culto, crimen…) |
| `design-grammar` | conceptos de DISEÑO reutilizables (Darklord's Past, Dark Bargain, pasos de creación) — andamiaje para inventar |
| `horror-craft` | técnicas de tono/atmósfera/pacing (musa de *cómo* narrar, no qué) |
| `character-option` / `species` | el pueblo/opción y su **cultura, estética y actitud** (el flavor, no las stats) |
| `creature` | una CRIATURA por `##`: su TIPO (`is_type`) y, sobre todo, **qué la hace memorable** (primer signo, comportamiento, motivo que la rodea) |
| `item` | un ITEM: su leyenda/gancho narrativo y a quién/qué evoca (no las stats) |
| `deity` / `setting-grammar` | DEIDADES (portafolio, culto, tono), cosmología, mitos, eras (The Calamity, The Weave) |
| `tarokka` | CARTAS y su simbolismo (oráculo generativo) |
| `adventure` | el ESCENARIO: premisa/gancho, NPCs, criaturas, locación, su `theme`/`tone` (tagline) |

## Relaciones (aristas)

Flavor / cross-book (priorizar):
- `has_theme` (cualquier entidad → theme; EXTRACTED si se declara, si no INFERRED)
- `exemplifies` (entidad → theme; INFERRED — teje arquetipos)
- `has_trope` (theme → tropo)
- `evokes` (entidad → motif/tono)

Estructurales (sirven como punteros de flavor):
- `has_darklord` / `bound_to` (domain↔darklord — la maldición que ata)
- `contains_location`, `home_to`, `operates_in`, `led_by`, `member_of`
- `features_creature` (entidad → criatura referida)
- `is_type` (creature → creature_type), `has_domain` (deity → portafolio)
- `aligned_card` / `opposed_card` (Tarokka)
- `conceptually_related_to`, `semantically_similar_to` (cross-cutting, INFERRED)

## Hyperedges — los arquetipos (lo MÁS valioso de la musa)

Cuando ≥3 nodos comparten un **patrón/arquetipo** que las aristas pareadas no capturan, añade un
hyperedge (máx. 3 por chunk). Son las semillas que la Capa 3 convierte en entidades nuevas.
Pueden ser de cualquier libro/tema:
- *"Darklords de obsesión trágica / anhelo imposible"*, *"objeto sapiente maldito como villano"*,
  *"dominios aislados por niebla con fronteras que se cierran"* (horror)
- *"potencias en guerra fría que se reparten una frontera"*, *"sindicatos criminales en las
  sombras de una ciudad mercante"*, *"orden de magos que corrompe desde dentro"* (intriga/setting)
- *"aberraciones lovecraftianas que rompen la cordura"*, *"transformación corporal como castigo"*
  (tema cross-book)

Prefiere hyperedges que **crucen libros** cuando el patrón se repite en fuentes distintas — ese
cruce es el oro de la inspiración.

## Reglas de confianza

- EXTRACTED: explícito en la fuente → `confidence_score` 1.0
- INFERRED: inferencia razonable (incluye casi todo `has_theme`/`evokes`/`exemplifies`) → 0.4–0.9
- AMBIGUOUS: incierto → 0.1–0.3 (marca, no omitas)

## Reglas de id / canonicalización

- `id` formato `filestem_entityname` (snake_case). **Reusa el MISMO id** para una entidad que
  recurre dentro del chunk (un theme, un tipo de criatura, una criatura/deidad compartida).
- **Labels limpios y consistentes:** para entidades recurrentes (themes, motifs, tipos de criatura,
  criaturas de catálogo, deidades, especies) usa el nombre canónico **sin** sufijos de CR/tipo
  (p. ej. "Vampire", no "Vampire (undead, CR 13)"; "Gothic Horror"; "Body Horror"). `canonicalize.py`
  fusiona por label normalizado → labels consistentes = mejor fusión cross-book. Usa nombres de
  `theme`/`motif` estables y reutilizables entre libros (no inventes sinónimos por libro).

## Prompt para cada subagente de extracción

> Eres un subagente de extracción del **compendio de flavor** de D&D. Lee los archivos listados y
> extrae un fragmento de grafo de conocimiento. El compendio es una *musa*: prioriza lo evocador
> (tema, tono, motivos, qué hace memorable a cada cosa) sobre lo mecánico — las stats viven en otra
> parte. Cada archivo abre con `> kind: <kind> · source: <ID>`; úsalo para decidir los tipos de
> nodo. Escribe SOLO JSON válido al archivo indicado (sin markdown, sin preámbulo) y devuelve un
> resumen de una línea (nodos, aristas).
>
> Prioriza, en orden: (a) nodos `theme` y `motif` y las aristas `has_theme`/`exemplifies`/`evokes`
> hacia ellos — son los hubs cross-book que disparan inspiración; (b) un nodo por entidad nombrada
> con su gancho de flavor; (c) las relaciones estructurales del `kind` (`has_darklord`/`bound_to`,
> `contains_location`/`home_to`/`operates_in`/`led_by`, `features_creature`, `is_type`, `has_domain`);
> (d) **1–3 hyperedges de arquetipos por chunk**, prefiriendo patrones que crucen libros.
> Si el libro no declara géneros, infiere igualmente los `theme`/`motif` dominantes. Reglas de
> confianza e id según arriba. Esquema JSON:
>
> `{"nodes":[{"id","label","file_type":"document","source_file","source_location":null,"source_url":null,"captured_at":null,"author":null,"contributor":null}],"edges":[{"source","target","relation","confidence","confidence_score","source_file","source_location":null,"weight":1.0}],"hyperedges":[{"id","label","nodes":[...],"relation","confidence","confidence_score","source_file"}],"input_tokens":0,"output_tokens":0}`
