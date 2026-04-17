#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List

from wiki_card_mcp_server import WikiCardIndex


DEFAULT_SOURCE_CANDIDATES = [
    Path("C:/projects/GPTStoryworld/benchmarks/wiki_card_routerbench/questions.jsonl"),
    Path("/mnt/c/projects/GPTStoryworld/benchmarks/wiki_card_routerbench/questions.jsonl"),
]


def resolve_existing(path_like: str | Path | List[str | Path], fallback: Path | List[Path]) -> Path:
    if isinstance(path_like, list):
        for item in path_like:
            try:
                return resolve_existing(item, fallback)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"Could not resolve any candidate in {path_like}")
    raw = str(path_like or "").strip()
    if raw:
        candidate = Path(raw).expanduser()
        if candidate.exists():
            return candidate.resolve()
        if raw.startswith("C:/"):
            alt = Path(raw.replace("C:/", "/mnt/c/"))
            if alt.exists():
                return alt.resolve()
        if raw.startswith("C:\\"):
            alt = Path(raw.replace("C:\\", "/mnt/c/").replace("\\", "/"))
            if alt.exists():
                return alt.resolve()
    if isinstance(fallback, list):
        for candidate in fallback:
            if candidate.exists():
                return candidate.resolve()
        raise FileNotFoundError(f"Could not resolve {raw or fallback[0]}")
    if fallback.exists():
        return fallback.resolve()
    raise FileNotFoundError(f"Could not resolve {raw or fallback}")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def resolve_benchmark_root(source_path: Path) -> Path:
    if source_path.is_dir():
        return source_path.resolve()
    if source_path.name.lower() in {"questions.jsonl", "cards.jsonl"}:
        return source_path.parent.resolve()
    return source_path.parent.resolve()


def compact_route_plan(route_plan: Dict[str, Any], actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    alias_hits = []
    for row in route_plan.get("alias_hits", [])[:4]:
        if not isinstance(row, dict):
            continue
        alias_hits.append(
            {
                "entity_id": row.get("entity_id"),
                "surface": row.get("surface"),
                "surface_type": row.get("surface_type"),
            }
        )
    relation_hits = []
    for row in route_plan.get("relation_hits", [])[:4]:
        if not isinstance(row, dict):
            continue
        relation_hits.append(
            {
                "entity_id": row.get("entity_id"),
                "relation": row.get("relation"),
                "value": row.get("value"),
            }
        )
    reduced_actions = []
    for row in actions:
        reduced_actions.append(
            {
                "action_id": row.get("action_id"),
                "namespace": row.get("namespace"),
                "tool": row.get("tool"),
                "args": row.get("args"),
                "label": row.get("label"),
            }
        )
    return {
        "type_hint": route_plan.get("type_hint", "entity"),
        "relation_hint": route_plan.get("relation_hint", ""),
        "namespaces": route_plan.get("namespaces", []),
        "alias_hits": alias_hits,
        "relation_hits": relation_hits,
        "actions": reduced_actions,
        "output": {"action_id": "one_of_listed_actions"},
    }


def gold_action_for_question(index: WikiCardIndex, question_row: Dict[str, Any], route_plan: Dict[str, Any]) -> Dict[str, Any]:
    expected_tool = str(question_row.get("expected_tool", "") or "").strip()
    subject_id = str(question_row.get("subject_id", "") or "").strip()
    relation = str(question_row.get("relation", "") or "").strip()
    for row in route_plan.get("actions", []):
        if not isinstance(row, dict):
            continue
        tool = str(row.get("tool", "") or "").strip()
        args = row.get("args", {}) if isinstance(row.get("args"), dict) else {}
        if tool != expected_tool:
            continue
        if str(args.get("entity_id", "") or "").strip() != subject_id:
            continue
        if expected_tool == "get_relation_card" and str(args.get("relation", "") or "").strip() != relation:
            continue
        return row
    if expected_tool == "get_relation_card":
        relation = relation or index.guess_best_relation(subject_id, str(question_row.get("question", "") or ""))
        return {
            "action_id": f"rel::{subject_id}::{relation}",
            "namespace": "relations",
            "tool": "get_relation_card",
            "args": {"entity_id": subject_id, "relation": relation},
            "label": f"relation:{subject_id}.{relation}",
        }
    return {
        "action_id": f"ent::{subject_id}",
        "namespace": "entities",
        "tool": "get_entity_card",
        "args": {"entity_id": subject_id},
        "label": f"entity:{subject_id}",
    }


def permute_actions(actions: List[Dict[str, Any]], question_id: str, variant_idx: int) -> List[Dict[str, Any]]:
    ordered = list(actions)
    if variant_idx == 0:
        return ordered
    if variant_idx == 1:
        return list(reversed(ordered))
    rng = random.Random(sum(ord(ch) for ch in f"{question_id}:{variant_idx}"))
    rng.shuffle(ordered)
    return ordered


def rationale_summary(question_row: Dict[str, Any], gold_action: Dict[str, Any]) -> str:
    expected_tool = str(question_row.get("expected_tool", "") or "").strip()
    relation = str(question_row.get("relation", "") or "").strip()
    bits = [f"expected_tool={expected_tool}", f"namespace={gold_action.get('namespace', '')}"]
    if relation:
        bits.append(f"relation={relation}")
    return "; ".join(bits)


def build_messages(question_row: Dict[str, Any], route_plan: Dict[str, Any], gold_action: Dict[str, Any], actions: List[Dict[str, Any]], system_prompt: str) -> Dict[str, Any]:
    payload = {
        "question_id": question_row.get("question_id"),
        "question": question_row.get("question"),
    }
    payload.update(compact_route_plan(route_plan, actions))
    assistant_payload = {
        "action_id": gold_action.get("action_id"),
        "tool": gold_action.get("tool"),
        "args": gold_action.get("args"),
        "namespace": gold_action.get("namespace"),
        "intent": "trivia_index_routing",
        "rationale_summary": rationale_summary(question_row, gold_action),
    }
    meta = {
        "source_name": "wiki-card-routerbench",
        "world_id": "wiki_card_routerbench",
        "question_id": question_row.get("question_id"),
        "subject_id": question_row.get("subject_id"),
        "expected_tool": question_row.get("expected_tool"),
        "relation": question_row.get("relation", ""),
        "action_id": gold_action.get("action_id"),
        "namespace": gold_action.get("namespace"),
    }
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=True, separators=(",", ":"))},
            {"role": "assistant", "content": json.dumps(assistant_payload, ensure_ascii=True, separators=(",", ":"))},
        ],
        "meta": meta,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a messages JSONL corpus for the wiki-card trivia router.")
    parser.add_argument("--source", default="", help="Benchmark root or questions.jsonl path.")
    parser.add_argument("--out", required=True, help="Output messages JSONL.")
    parser.add_argument(
        "--system-prompt",
        default="You are a TRM router for a tiny trivia MCP. Emit compact JSON only and choose the best action_id.",
        help="System prompt to prepend to each training row.",
    )
    parser.add_argument("--max-records", type=int, default=0, help="Optional cap on question count before variants are expanded.")
    parser.add_argument("--variants-per-question", type=int, default=4, help="How many deterministic action-order variants to emit per question.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve paths and report counts without writing output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = resolve_existing(args.source, DEFAULT_SOURCE_CANDIDATES)
    benchmark_root = resolve_benchmark_root(source_path)
    out_path = Path(args.out).expanduser().resolve()
    index = WikiCardIndex(benchmark_root)
    questions = index.load_questions(max_questions=args.max_records)

    rows: List[Dict[str, Any]] = []
    action_counts: Dict[str, int] = {}
    namespace_counts: Dict[str, int] = {}
    for question_row in questions:
        route_plan = index.plan_query(str(question_row.get("question", "") or ""), candidate_top_k=5, relation_top_k=6, max_actions=10)
        gold_action = gold_action_for_question(index, question_row, route_plan)
        actions = [row for row in route_plan.get("actions", []) if isinstance(row, dict)]
        if gold_action.get("action_id") not in {str(row.get("action_id", "") or "") for row in actions}:
            actions.append(gold_action)
        for variant_idx in range(max(1, int(args.variants_per_question))):
            variant_actions = permute_actions(actions, str(question_row.get("question_id", "") or ""), variant_idx)
            rows.append(build_messages(question_row, route_plan, gold_action, variant_actions, args.system_prompt))
        action_id = str(gold_action.get("action_id", "") or "")
        namespace = str(gold_action.get("namespace", "") or "")
        action_counts[action_id] = action_counts.get(action_id, 0) + 1
        namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1

    manifest = {
        "source": str(source_path),
        "benchmark_root": str(benchmark_root),
        "out": str(out_path),
        "question_count": len(questions),
        "row_count": len(rows),
        "variants_per_question": max(1, int(args.variants_per_question)),
        "system_prompt": args.system_prompt,
        "action_counts": action_counts,
        "namespace_counts": namespace_counts,
    }
    manifest_path = out_path.parent / "wiki_card_router_corpus_manifest.json"
    if args.dry_run:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    count = dump_jsonl(out_path, rows)
    manifest["row_count"] = count
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
