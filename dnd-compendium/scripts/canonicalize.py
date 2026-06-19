#!/usr/bin/env python3
"""
canonicalize.py — capa de identidad cross-book del compendio graphify.

El piloto RHW usó IDs con prefijo de archivo (creature_strahd, bestiary_strahd,
domain-barovia_strahd), así que la misma entidad se fragmentaba en varios nodos y
NO se fusionaba al ingerir otro libro. Esta capa resuelve eso: fusiona nodos que
representan la misma entidad por (label normalizado) en un id canónico estable
`canon:<slug>`, remapea aristas/hyperedges y deduplica.

Esto es lo que hace que el grafo *crezca* en vez de *duplicarse* libro a libro:
"Gothic Horror"/"Vampire"/"Strahd von Zarovich" de RHW colapsan a un nodo, y el
mismo nodo de un libro futuro cae sobre el canónico existente.

Uso:
  python3 canonicalize.py <extract.json> [<out.json>]   # default in-place
"""
import json
import re
import sys
from pathlib import Path


def normalize(label: str) -> str:
    """Clave de fusión: minúsculas, sin cualificadores entre paréntesis, sin
    sufijos de CR/tipo, sin puntuación de borde. 'Strahd von Zarovich (undead
    vampire Darklord, CR 15)' y 'Strahd von Zarovich' → misma clave."""
    s = label or ""
    s = re.sub(r"\s*\([^)]*\)", "", s)          # quita "(undead, CR 15)"
    s = re.sub(r"\s*[—-]\s*CR\s*\S+.*$", "", s, flags=re.I)
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def slug(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def _as_sources(node, stamp_source):
    """Provenance (libro) de un nodo como lista. Si stamp_source está dado, lo
    fuerza (caso ingesta de un libro nuevo); si no, conserva el `source` previo
    (caso unión del compendio ya etiquetado)."""
    if stamp_source:
        return [stamp_source]
    s = node.get("source")
    if isinstance(s, str):
        return [s]
    if isinstance(s, list):
        return list(s)
    return []


def canonicalize(extract: dict, stamp_source: str | None = None) -> tuple[dict, dict]:
    nodes = extract.get("nodes", [])
    edges = extract.get("edges", [])
    hyper = extract.get("hyperedges", [])

    # 1) agrupa nodos por clave normalizada → elige id canónico + mejor label.
    # Acumula la PROVENANCE (qué libro(s) aportaron el nodo) uniendo `source`:
    # un nodo que existe en varios libros termina con source=["EGW","RHW",...].
    key_to_canon = {}     # norm-key -> canon id
    canon_node = {}        # canon id -> node dict (acumulado)
    old_to_canon = {}      # id viejo -> canon id
    for n in nodes:
        key = normalize(n.get("label", n.get("id", "")))
        if not key:
            key = n.get("id", "")
        if key not in key_to_canon:
            cid = f"canon:{slug(key)}" or n["id"]
            key_to_canon[key] = cid
            canon_node[cid] = {**n, "id": cid, "source_files": [], "source": []}
        cid = key_to_canon[key]
        old_to_canon[n["id"]] = cid
        # conserva el label más rico (más largo) y acumula source_files + source
        cn = canon_node[cid]
        if len(n.get("label", "")) > len(cn.get("label", "")):
            cn["label"] = n["label"]
        sf = n.get("source_file")
        if sf and sf not in cn["source_files"]:
            cn["source_files"].append(sf)
        for src in _as_sources(n, stamp_source):
            if src not in cn["source"]:
                cn["source"].append(src)

    # ordena la provenance para diffs estables
    for cn in canon_node.values():
        cn["source"] = sorted(cn["source"])

    merged = len(nodes) - len(canon_node)
    cross_source = sum(1 for cn in canon_node.values() if len(cn["source"]) > 1)

    # 2) remapea aristas y deduplica por (source, target, relation).
    # Un endpoint puede venir como id de nodo O como label (algunos extractores
    # referencian entidades por nombre); resolvemos por id y, si falla, por label
    # normalizado. Lo que no resuelva a un nodo canónico se descarta (dangling).
    def resolve(endpoint):
        if endpoint in old_to_canon:
            return old_to_canon[endpoint]
        k = normalize(endpoint)
        return key_to_canon.get(k)  # None si no existe

    valid = set(canon_node)
    seen = set()
    new_edges = []
    dangling = 0
    for e in edges:
        s = resolve(e["source"])
        t = resolve(e["target"])
        if s is None or t is None or s not in valid or t not in valid:
            dangling += 1
            continue
        if s == t:
            continue  # auto-bucle creado por la fusión
        rel = e.get("relation", "")
        k = (s, t, rel)
        if k in seen:
            continue
        seen.add(k)
        new_edges.append({**e, "source": s, "target": t})

    # 3) remapea hyperedges (resuelve por id o label; descarta endpoints muertos)
    new_hyper = []
    for h in hyper:
        hn = [resolve(x) for x in h.get("nodes", [])]
        hn = [x for x in hn if x in valid]
        hn = list(dict.fromkeys(hn))  # dedup preservando orden
        if len(hn) >= 2:
            new_hyper.append({**h, "nodes": hn})

    out = {
        "nodes": list(canon_node.values()),
        "edges": new_edges,
        "hyperedges": new_hyper,
        "input_tokens": extract.get("input_tokens", 0),
        "output_tokens": extract.get("output_tokens", 0),
    }
    report = {
        "nodes_in": len(nodes),
        "nodes_out": len(canon_node),
        "merged": merged,
        "cross_source_nodes": cross_source,
        "edges_in": len(edges),
        "edges_out": len(new_edges),
        "edges_dropped_dangling": dangling,
        "edges_deduped": len(edges) - len(new_edges) - dangling,
    }
    return out, report


def main():
    # uso: canonicalize.py <extract.json> [out.json] [--source=ID]
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    stamp = next((a.split("=", 1)[1] for a in sys.argv[1:]
                  if a.startswith("--source=")), None)
    if not pos:
        print("uso: python3 canonicalize.py <extract.json> [out.json] [--source=ID]")
        raise SystemExit(1)
    src = Path(pos[0])
    dst = Path(pos[1]) if len(pos) > 1 else src
    extract = json.loads(src.read_text())
    out, report = canonicalize(extract, stamp_source=stamp)
    dst.write_text(json.dumps(out, indent=2))
    stamped = f" [stamped source={stamp}]" if stamp else ""
    print(f"canonicalized{stamped}: {report['nodes_in']}→{report['nodes_out']} nodes "
          f"({report['merged']} merged, {report['cross_source_nodes']} multi-book), "
          f"{report['edges_in']}→{report['edges_out']} edges "
          f"({report['edges_deduped']} deduped) → {dst}")


if __name__ == "__main__":
    main()
