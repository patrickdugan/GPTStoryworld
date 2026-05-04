#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_'-]{2,}")
STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "also",
    "and",
    "any",
    "another",
    "apparent",
    "are",
    "around",
    "authority",
    "because",
    "become",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "can",
    "could",
    "did",
    "does",
    "every",
    "for",
    "from",
    "had",
    "has",
    "have",
    "her",
    "him",
    "his",
    "how",
    "into",
    "its",
    "not",
    "off",
    "one",
    "only",
    "onto",
    "our",
    "out",
    "own",
    "rather",
    "she",
    "should",
    "tends",
    "than",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "under",
    "use",
    "used",
    "using",
    "was",
    "were",
    "what",
    "when",
    "where",
    "whether",
    "which",
    "while",
    "who",
    "will",
    "with",
    "without",
    "would",
    "www",
    "http",
    "https",
    "com",
    "org",
    "edu",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def script_text(value: Any) -> str:
    if isinstance(value, dict):
        raw = value.get("value")
        if isinstance(raw, str):
            return raw
        return " ".join(script_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(script_text(v) for v in value)
    if isinstance(value, str):
        return value
    return ""


def estimate_tokens(text: str) -> int:
    return max(1, len(text.encode("utf-8")) // 4)


def words(text: str) -> list[str]:
    return [m.group(0).lower() for m in WORD_RE.finditer(text) if m.group(0).lower() not in STOPWORDS]


def chunk_text(text: str, max_chars: int) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for para in paras:
        if size + len(para) > max_chars and current:
            chunks.append("\n\n".join(current))
            current = []
            size = 0
        if len(para) > max_chars:
            for i in range(0, len(para), max_chars):
                chunks.append(para[i : i + max_chars].strip())
            continue
        current.append(para)
        size += len(para)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def stable_term_id(term: str) -> str:
    safe = re.sub(r"[^a-z0-9]+", "_", term.lower()).strip("_")
    return safe or "term"


def source_doc_id(index: int) -> str:
    return f"source_{index:04d}"


def collect_sources(paths: list[str], max_file_bytes: int) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    source_index = 1
    for raw in paths:
        root = Path(raw).expanduser().resolve()
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in candidates:
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".txt", ".json", ".jsonl", ".csv"}:
                continue
            if path.stat().st_size > max_file_bytes:
                continue
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            docs.append({"doc_id": source_doc_id(source_index), "path": str(path), "text": text})
            source_index += 1
    return docs


def build_research_world_model(
    *,
    docs: list[dict[str, str]],
    topic: str,
    storyworld_json: str,
    card_token_budget: int,
    max_term_depth: int,
    neighbor_limit: int,
) -> dict[str, Any]:
    topic_terms = set(words(topic))
    world_term_set = set(storyworld_terms(storyworld_json))
    seed_terms = sorted(topic_terms.union(world_term_set))
    chunks: list[dict[str, Any]] = []
    term_sources: dict[str, Counter[str]] = defaultdict(Counter)
    cooccurrence: dict[str, Counter[str]] = defaultdict(Counter)

    chunk_index = 1
    chunk_chars = max(800, card_token_budget * 5)
    for doc in docs:
        for chunk in chunk_text(doc["text"], max_chars=chunk_chars):
            counts = Counter(words(chunk))
            if not counts:
                continue
            chunk_id = f"chunk_{chunk_index:05d}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "doc_id": doc.get("doc_id", source_doc_id(chunk_index)),
                    "source_path": doc["path"],
                    "terms": counts,
                    "estimated_tokens": estimate_tokens(chunk),
                }
            )
            for term, count in counts.items():
                term_sources[term][chunk_id] += count
            present = set(counts)
            for term in present:
                for other in present:
                    if other != term:
                        cooccurrence[term][other] += min(counts[term], counts[other])
            chunk_index += 1

    frontier = set(seed_terms)
    discovered: dict[str, dict[str, Any]] = {}
    query_nests: list[dict[str, Any]] = []
    term_edges: list[dict[str, Any]] = []

    for depth in range(max(0, max_term_depth) + 1):
        next_frontier: set[str] = set()
        for term in sorted(frontier):
            if term not in cooccurrence and term not in term_sources:
                continue
            source_hits = term_sources.get(term, Counter())
            neighbors = [
                {"term": other, "score": int(score)}
                for other, score in cooccurrence.get(term, Counter()).most_common(max(0, neighbor_limit))
                if other not in {term} and len(other) >= 3
            ]
            role = "seed" if term in seed_terms else "associated"
            discovered.setdefault(
                term,
                {
                    "term": term,
                    "term_id": stable_term_id(term),
                    "role": role,
                    "first_depth": depth,
                    "source_hit_count": int(sum(source_hits.values())),
                    "chunk_count": len(source_hits),
                    "top_chunks": [chunk_id for chunk_id, _ in source_hits.most_common(6)],
                },
            )
            query_nests.append(
                {
                    "term": term,
                    "term_id": stable_term_id(term),
                    "depth": depth,
                    "query": " ".join(dict.fromkeys(words(f"{topic} {term}"))),
                    "associated_terms": neighbors[:neighbor_limit],
                    "source_chunks": [chunk_id for chunk_id, _ in source_hits.most_common(6)],
                    "retrieval_intent": "deepen source grounding before asking a small model for doctrine/storyworld prose",
                }
            )
            for neighbor in neighbors:
                other = neighbor["term"]
                term_edges.append(
                    {
                        "from": term,
                        "to": other,
                        "relation": "cooccurs_with",
                        "score": neighbor["score"],
                        "depth": depth,
                    }
                )
                if depth < max_term_depth and other not in discovered:
                    next_frontier.add(other)
        frontier = next_frontier

    sources = [
        {
            "doc_id": doc.get("doc_id", source_doc_id(index)),
            "source_path": doc["path"],
            "estimated_tokens": estimate_tokens(doc["text"]),
        }
        for index, doc in enumerate(docs, start=1)
    ]
    chunk_index_payload = [
        {
            "chunk_id": chunk["chunk_id"],
            "doc_id": chunk["doc_id"],
            "source_path": chunk["source_path"],
            "estimated_tokens": chunk["estimated_tokens"],
            "top_terms": [term for term, _ in chunk["terms"].most_common(16)],
        }
        for chunk in chunks
    ]
    return {
        "schema": "research_mcp_world_model.v1",
        "topic": topic,
        "storyworld_json": str(Path(storyworld_json).expanduser().resolve()) if storyworld_json else "",
        "seed_terms": seed_terms,
        "term_depth": max_term_depth,
        "neighbor_limit": neighbor_limit,
        "sources": sources,
        "chunks": chunk_index_payload,
        "terms": sorted(discovered.values(), key=lambda row: (row["first_depth"], -row["source_hit_count"], row["term"])),
        "term_edges": sorted(term_edges, key=lambda row: (row["depth"], -row["score"], row["from"], row["to"]))[: max(200, neighbor_limit * 80)],
        "query_nests": query_nests,
        "contract": {
            "role": "generic research MCP world model for source-grounded storyworld authoring",
            "bird_nest_process": "seed terms expand to associated terms through local-source co-occurrence; each associated term creates a bounded follow-up query/card target",
            "not_authority": True,
            "bounded_packet_rule": "inject only cards, term summaries, and source paths into model prompts",
        },
    }


def storyworld_terms(path: str) -> list[str]:
    if not path:
        return []
    p = Path(path).expanduser().resolve()
    if not p.exists() or p.suffix.lower() != ".json":
        return []
    try:
        world = read_json(p)
    except Exception:
        return []
    parts: list[str] = []
    parts.append(str(world.get("storyworld_title") or world.get("title") or ""))
    for char in world.get("characters", []) or []:
        if isinstance(char, dict):
            parts.append(str(char.get("name") or char.get("id") or ""))
    for encounter in (world.get("encounters", []) or [])[:12]:
        if isinstance(encounter, dict):
            parts.append(str(encounter.get("title") or ""))
            parts.append(script_text(encounter.get("text_script"))[:500])
    return words(" ".join(parts))


def card_from_chunk(
    *,
    source_path: str,
    chunk: str,
    index: int,
    topic_terms: set[str],
    world_terms: set[str],
    token_budget: int,
) -> dict[str, Any]:
    chunk_words = words(chunk)
    counts = Counter(chunk_words)
    overlap_topic = sorted(topic_terms.intersection(counts))
    overlap_world = sorted(world_terms.intersection(counts))
    keywords = [word for word, _ in counts.most_common(12)]
    summary = chunk.strip().replace("\r\n", "\n")
    while estimate_tokens(summary) > token_budget and len(summary) > 120:
        summary = summary[: int(len(summary) * 0.85)].rsplit(" ", 1)[0].strip()
    return {
        "card_id": f"research_{index:04d}",
        "source_path": source_path,
        "estimated_tokens": estimate_tokens(summary),
        "keywords": keywords,
        "topic_overlap": overlap_topic[:12],
        "world_overlap": overlap_world[:12],
        "source_excerpt": summary,
        "use_for": [
            "grounding small-model imagination",
            "generating doctrine-aware options and reactions",
            "checking whether poetic inventions preserve source constraints",
        ],
        "small_model_contract": {
            "allowed": [
                "borrow concrete terms",
                "turn source tensions into exam questions",
                "write local clue/reaction prose",
            ],
            "forbidden": [
                "treat excerpt as exhaustive scholarship",
                "invent doctrine as fact",
                "override verifier or schema constraints",
            ],
        },
    }


def attach_world_model_fields(cards: list[dict[str, Any]], world_model: dict[str, Any]) -> None:
    chunks_by_id = {chunk["chunk_id"]: chunk for chunk in world_model.get("chunks", []) if isinstance(chunk, dict)}
    term_by_chunk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for term in world_model.get("terms", []):
        if not isinstance(term, dict):
            continue
        for chunk_id in term.get("top_chunks", []) or []:
            term_by_chunk[str(chunk_id)].append(
                {
                    "term": term.get("term"),
                    "role": term.get("role"),
                    "first_depth": term.get("first_depth"),
                }
            )
    for card in cards:
        source_path = str(card.get("source_path", ""))
        matching_chunks = [
            chunk_id
            for chunk_id, chunk in chunks_by_id.items()
            if str(chunk.get("source_path", "")) == source_path
        ][:4]
        model_terms: list[dict[str, Any]] = []
        for chunk_id in matching_chunks:
            model_terms.extend(term_by_chunk.get(chunk_id, [])[:6])
        seen: set[str] = set()
        deduped: list[dict[str, Any]] = []
        for term in model_terms:
            key = str(term.get("term", ""))
            if key and key not in seen:
                seen.add(key)
                deduped.append(term)
        card["world_model_terms"] = deduped[:12]
        card["research_world_model_role"] = "evidence card selected from a larger term/source graph"


def score_card(card: dict[str, Any]) -> tuple[int, int, int]:
    return (
        len(card.get("topic_overlap", [])) + len(card.get("world_overlap", [])),
        len(card.get("world_overlap", [])),
        -int(card.get("estimated_tokens", 0) or 0),
    )


def write_brief(path: Path, topic: str, cards: list[dict[str, Any]], world_model: dict[str, Any] | None = None) -> None:
    lines = [
        "# Research Stimulus Brief",
        "",
        f"Topic: {topic or 'unspecified'}",
        f"Cards: {len(cards)}",
        "",
        "Use these cards as grounded imagination stimulus for bounded storyworld authoring. They are not authority by themselves; verifier and source-specific checks still own correctness.",
        "",
    ]
    if world_model:
        terms = world_model.get("terms", [])[:16]
        nests = world_model.get("query_nests", [])[:8]
        lines.extend(
            [
                "## Research MCP World Model",
                "",
                f"- Sources: {len(world_model.get('sources', []))}",
                f"- Chunks: {len(world_model.get('chunks', []))}",
                f"- Terms: {len(world_model.get('terms', []))}",
                f"- Term edges: {len(world_model.get('term_edges', []))}",
                "",
                "Top terms:",
                "",
            ]
        )
        for term in terms:
            lines.append(
                f"- `{term.get('term')}` depth={term.get('first_depth')} role={term.get('role')} chunks={term.get('chunk_count')}"
            )
        lines.extend(["", "Query nests for deeper retrieval:", ""])
        for nest in nests:
            assoc = ", ".join(str(row.get("term")) for row in nest.get("associated_terms", [])[:5])
            lines.append(f"- `{nest.get('term')}` -> {assoc}")
        lines.append("")
    for card in cards[:12]:
        lines.extend(
            [
                f"## {card['card_id']}",
                f"- Source: `{card['source_path']}`",
                f"- Keywords: {', '.join(card.get('keywords', [])[:8])}",
                f"- Estimated tokens: {card.get('estimated_tokens')}",
                "",
                card.get("source_excerpt", "")[:700],
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def write_metta(path: Path, topic: str, cards: list[dict[str, Any]], world_model: dict[str, Any] | None = None) -> None:
    lines = [
        "(: ResearchWorldModel Type)",
        "(: ResearchSource Type)",
        "(: ResearchCard Type)",
        "(: ResearchTerm Type)",
        "(: ResearchQueryNest Type)",
        "(: cooccurs-with (-> ResearchTerm ResearchTerm Number))",
        f"(research-topic {json.dumps(topic or 'storyworld')})",
    ]
    if world_model:
        lines.append("(research-world-model research_mcp_world_model_v1)")
        for source in world_model.get("sources", [])[:64]:
            sid = str(source.get("doc_id", "source"))
            lines.append(f"(research-source-node {sid})")
            lines.append(f"(research-source-path {sid} {json.dumps(source.get('source_path', ''))})")
        for term in world_model.get("terms", [])[:160]:
            tid = stable_term_id(str(term.get("term", "")))
            lines.append(f"(research-term {tid} {json.dumps(term.get('term', ''))})")
            lines.append(f"(research-term-role {tid} {json.dumps(term.get('role', 'associated'))})")
            lines.append(f"(research-term-depth {tid} {int(term.get('first_depth', 0) or 0)})")
            lines.append(f"(research-term-chunks {tid} {int(term.get('chunk_count', 0) or 0)})")
        for edge in world_model.get("term_edges", [])[:240]:
            left = stable_term_id(str(edge.get("from", "")))
            right = stable_term_id(str(edge.get("to", "")))
            score = int(edge.get("score", 0) or 0)
            if left and right:
                lines.append(f"(cooccurs-with {left} {right} {score})")
        for index, nest in enumerate(world_model.get("query_nests", [])[:64], start=1):
            nid = f"query_nest_{index:04d}"
            tid = stable_term_id(str(nest.get("term", "")))
            lines.append(f"(research-query-nest {nid})")
            lines.append(f"(query-nest-term {nid} {tid})")
            lines.append(f"(query-nest-query {nid} {json.dumps(nest.get('query', ''))})")
    for card in cards:
        cid = card["card_id"]
        lines.append(f"(research-card {cid})")
        lines.append(f"(research-source {cid} {json.dumps(card.get('source_path', ''))})")
        lines.append(f"(research-token-estimate {cid} {int(card.get('estimated_tokens', 0) or 0)})")
        for kw in card.get("keywords", [])[:8]:
            lines.append(f"(research-keyword {cid} {json.dumps(kw)})")
        for term in card.get("world_model_terms", [])[:8]:
            lines.append(f"(research-card-term {cid} {stable_term_id(str(term.get('term', '')))})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_query_nests(path: Path, world_model: dict[str, Any]) -> int:
    return write_jsonl(path, world_model.get("query_nests", []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build compact research stimulus cards for MCP-bounded storyworld authoring.")
    parser.add_argument("--source", action="append", default=[], help="Research source file or directory. Repeatable.")
    parser.add_argument("--topic", default="", help="Research topic or authoring brief.")
    parser.add_argument("--storyworld-json", default="", help="Optional storyworld JSON used to rank relevant cards.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-cards", type=int, default=8)
    parser.add_argument("--card-token-budget", type=int, default=220)
    parser.add_argument("--max-file-bytes", type=int, default=500000)
    parser.add_argument("--research-term-depth", type=int, default=1, help="Associated-term expansion depth for the research MCP world model.")
    parser.add_argument("--research-neighbor-terms", type=int, default=8, help="Associated terms per seed/nested term.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    topic_terms = set(words(args.topic))
    world_term_set = set(storyworld_terms(args.storyworld_json))
    docs = collect_sources(args.source, args.max_file_bytes)
    world_model = build_research_world_model(
        docs=docs,
        topic=args.topic,
        storyworld_json=args.storyworld_json,
        card_token_budget=args.card_token_budget,
        max_term_depth=max(0, args.research_term_depth),
        neighbor_limit=max(0, args.research_neighbor_terms),
    )

    cards: list[dict[str, Any]] = []
    index = 1
    for doc in docs:
        for chunk in chunk_text(doc["text"], max_chars=max(800, args.card_token_budget * 5)):
            card = card_from_chunk(
                source_path=doc["path"],
                chunk=chunk,
                index=index,
                topic_terms=topic_terms,
                world_terms=world_term_set,
                token_budget=args.card_token_budget,
            )
            cards.append(card)
            index += 1
    cards.sort(key=score_card, reverse=True)
    cards = cards[: max(0, args.max_cards)]
    attach_world_model_fields(cards, world_model)

    manifest = {
        "topic": args.topic,
        "storyworld_json": str(Path(args.storyworld_json).expanduser().resolve()) if args.storyworld_json else "",
        "source_count": len(docs),
        "card_count": len(cards),
        "max_cards": args.max_cards,
        "card_token_budget": args.card_token_budget,
        "research_world_model": {
            "schema": world_model.get("schema"),
            "term_depth": world_model.get("term_depth"),
            "neighbor_limit": world_model.get("neighbor_limit"),
            "term_count": len(world_model.get("terms", [])),
            "term_edge_count": len(world_model.get("term_edges", [])),
            "query_nest_count": len(world_model.get("query_nests", [])),
        },
        "outputs": {
            "cards_json": str(out_dir / "research_cards.json"),
            "cards_jsonl": str(out_dir / "research_cards.jsonl"),
            "brief": str(out_dir / "research_brief.md"),
            "metta": str(out_dir / "research_facts.metta"),
            "world_model": str(out_dir / "research_world_model.json"),
            "query_nests": str(out_dir / "research_query_nests.jsonl"),
        },
    }
    write_json(out_dir / "research_cards.json", {"manifest": manifest, "cards": cards})
    write_jsonl(out_dir / "research_cards.jsonl", cards)
    write_json(out_dir / "research_world_model.json", world_model)
    write_query_nests(out_dir / "research_query_nests.jsonl", world_model)
    write_brief(out_dir / "research_brief.md", args.topic, cards, world_model)
    write_metta(out_dir / "research_facts.metta", args.topic, cards, world_model)
    write_json(out_dir / "manifest.json", manifest)
    print(str(out_dir / "research_cards.json"))
    print(str(out_dir / "research_brief.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
