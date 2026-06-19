# Taxonomía de extracción — compendio centrado en género

Cada archivo del corpus lleva un encabezado `> kind: <kind> · source: <ID>`. El `kind` indica
qué tipo de entidad domina el archivo y guía qué nodos/aristas extraer. La **idea central** es
que los **nodos de género de horror** son los *hubs cross-book*: conectan darklords, dominios y
criaturas de cualquier libro. Extrae siempre las aristas hacia el género.

## Tipos de nodo por `kind`

| kind | nodos a extraer |
|------|-----------------|
| `domain` | el DOMINIO; su DARKLORD (sección nombrada por una persona); LOCALIZACIONES; CRIATURAS referidas (línea "Referenced creatures" + prosa); el GÉNERO declarado; cartas Tarokka aligned/opposed |
| `genre` | el GÉNERO de horror como nodo; sus TROPOS/hallmarks; criaturas/temas ejemplares citados |
| `design-grammar` | conceptos de DISEÑO (Darklord's Past, Birth of a Darklord, Dark Powers, Mist, dark bargain); patrones de creación |
| `horror-craft` | técnicas de narración (pacing, atmósfera, mood); ORGANIZACIONES (cross-domain); Mist Wanderers; modelos de campaña |
| `organization` | la ORGANIZACIÓN; su propósito; dominios/figuras vinculadas |
| `character-option` | DARK GIFTS, subclases, backgrounds, feats temáticos; su mecánica/concepto |
| `creature` | una CRIATURA por `##`; su TIPO (undead, fiend, aberration, fey…) como nodo; CR; rasgos notables |
| `item` | un ITEM mágico por `##`; rareza/tipo; figura/lugar vinculado |
| `tarokka` | CARTAS y su simbolismo; mapeo carta→dominio/darklord |
| `setting-grammar` | conceptos de cosmología (The Mists, Dark Powers, Nightmare Logic) |

## Relaciones (aristas)

- `has_darklord` (domain→darklord, EXTRACTED)
- `bound_to` (darklord→domain — la maldición que lo ata, EXTRACTED)
- `contains_location` (domain→location, EXTRACTED)
- `features_creature` (domain/section→creature, EXTRACTED desde refs)
- `has_genre` (domain/darklord→genre, EXTRACTED si se declara; si no INFERRED)
- `is_type` (creature→creature_type, EXTRACTED)
- `exemplifies` (creature/darklord→genre, INFERRED, para tejer arquetipos)
- `aligned_card` / `opposed_card` (domain→tarokka card, EXTRACTED)
- `member_of` / `operates_in` (figure/org→domain, EXTRACTED)
- `conceptually_related_to`, `semantically_similar_to` (INFERRED, cross-cutting)

## Hyperedges (patrones arquetípicos — alto valor)

Cuando ≥3 nodos comparten un patrón que las aristas pareadas no capturan, añade un hyperedge
(máx. 3 por chunk). Son la materia prima de la "musa": p. ej. *"darklords de obsesión trágica /
anhelo imposible"*, *"dominios bajo catástrofe perpetua"*, *"aberraciones lovecraftianas"*.

## Reglas de confianza

- EXTRACTED: explícito en la fuente → `confidence_score` 1.0
- INFERRED: inferencia razonable → 0.4–0.9
- AMBIGUOUS: incierto → 0.1–0.3 (marca, no omitas)

## Reglas de id / canonicalización

- `id` formato `filestem_entityname` (snake_case). **Reusa el MISMO id** para una entidad que
  recurre dentro del chunk (un género, un tipo de criatura, una criatura compartida).
- **Labels limpios y consistentes:** para entidades que recurren entre archivos/libros (géneros,
  tipos de criatura, criaturas de catálogo, NPCs nombrados) usa el nombre canónico **sin** sufijos
  de CR/tipo (p. ej. label "Vampire", no "Vampire (undead, CR 13)"). La capa `canonicalize.py`
  fusiona por label normalizado, así que labels consistentes = mejor fusión cross-book.

## Prompt para cada subagente de extracción

> Eres un subagente de extracción del compendio D&D. Lee los archivos listados y extrae un
> fragmento de grafo de conocimiento. Cada archivo abre con `> kind: <kind> · source: <ID>` —
> úsalo para decidir los tipos de nodo (tabla de arriba). Escribe SOLO JSON válido al archivo
> indicado (sin markdown, sin preámbulo) y devuelve un resumen de una línea (nodos, aristas).
>
> Prioriza: (a) un nodo por entidad nombrada; (b) aristas `has_genre`/`exemplifies` hacia el
> género (son los hubs cross-book); (c) `has_darklord`/`bound_to`/`features_creature` en dominios;
> (d) `is_type` en criaturas; (e) 1–3 hyperedges de patrones arquetípicos por chunk.
> Reglas de confianza e id según arriba. Esquema JSON:
>
> `{"nodes":[{"id","label","file_type":"document","source_file","source_location":null,"source_url":null,"captured_at":null,"author":null,"contributor":null}],"edges":[{"source","target","relation","confidence","confidence_score","source_file","source_location":null,"weight":1.0}],"hyperedges":[{"id","label","nodes":[...],"relation","confidence","confidence_score","source_file"}],"input_tokens":0,"output_tokens":0}`
