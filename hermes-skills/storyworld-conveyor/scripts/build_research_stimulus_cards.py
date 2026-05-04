#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_'-]{2,}")


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
    return [m.group(0).lower() for m in WORD_RE.finditer(text)]


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


def collect_sources(paths: list[str], max_file_bytes: int) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
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
            docs.append({"path": str(path), "text": text})
    return docs


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


def score_card(card: dict[str, Any]) -> tuple[int, int, int]:
    return (
        len(card.get("topic_overlap", [])) + len(card.get("world_overlap", [])),
        len(card.get("world_overlap", [])),
        -int(card.get("estimated_tokens", 0) or 0),
    )


def write_brief(path: Path, topic: str, cards: list[dict[str, Any]]) -> None:
    lines = [
        "# Research Stimulus Brief",
        "",
        f"Topic: {topic or 'unspecified'}",
        f"Cards: {len(cards)}",
        "",
        "Use these cards as grounded imagination stimulus for bounded storyworld authoring. They are not authority by themselves; verifier and source-specific checks still own correctness.",
        "",
    ]
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


def write_metta(path: Path, topic: str, cards: list[dict[str, Any]]) -> None:
    lines = [f"(research-topic {json.dumps(topic or 'storyworld')})"]
    for card in cards:
        cid = card["card_id"]
        lines.append(f"(research-card {cid})")
        lines.append(f"(research-source {cid} {json.dumps(card.get('source_path', ''))})")
        lines.append(f"(research-token-estimate {cid} {int(card.get('estimated_tokens', 0) or 0)})")
        for kw in card.get("keywords", [])[:8]:
            lines.append(f"(research-keyword {cid} {json.dumps(kw)})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build compact research stimulus cards for MCP-bounded storyworld authoring.")
    parser.add_argument("--source", action="append", default=[], help="Research source file or directory. Repeatable.")
    parser.add_argument("--topic", default="", help="Research topic or authoring brief.")
    parser.add_argument("--storyworld-json", default="", help="Optional storyworld JSON used to rank relevant cards.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-cards", type=int, default=8)
    parser.add_argument("--card-token-budget", type=int, default=220)
    parser.add_argument("--max-file-bytes", type=int, default=500000)
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    topic_terms = set(words(args.topic))
    world_term_set = set(storyworld_terms(args.storyworld_json))
    docs = collect_sources(args.source, args.max_file_bytes)

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

    manifest = {
        "topic": args.topic,
        "storyworld_json": str(Path(args.storyworld_json).expanduser().resolve()) if args.storyworld_json else "",
        "source_count": len(docs),
        "card_count": len(cards),
        "max_cards": args.max_cards,
        "card_token_budget": args.card_token_budget,
        "outputs": {
            "cards_json": str(out_dir / "research_cards.json"),
            "cards_jsonl": str(out_dir / "research_cards.jsonl"),
            "brief": str(out_dir / "research_brief.md"),
            "metta": str(out_dir / "research_facts.metta"),
        },
    }
    write_json(out_dir / "research_cards.json", {"manifest": manifest, "cards": cards})
    write_jsonl(out_dir / "research_cards.jsonl", cards)
    write_brief(out_dir / "research_brief.md", args.topic, cards)
    write_metta(out_dir / "research_facts.metta", args.topic, cards)
    write_json(out_dir / "manifest.json", manifest)
    print(str(out_dir / "research_cards.json"))
    print(str(out_dir / "research_brief.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
