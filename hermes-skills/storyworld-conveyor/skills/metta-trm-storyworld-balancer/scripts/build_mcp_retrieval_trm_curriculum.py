#!/usr/bin/env python3
"""Build MCP-retrieval TRM curriculum rows from storyworld builder runs.

This turns a benchmark artifact into trainable control-plane rows. The target
TRM learns which MCP cards to retrieve before an LLM stage, instead of asking a
small model to hold the whole storyworld and task contract in-context.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]

TOOLS = [
    "LIST_MCP_CARDS",
    "READ_MCP_CONTEXT",
    "SELECT_MCP_PACKET",
    "ASK_LLM_BOUNDED_STAGE",
    "RUN_VALIDATOR",
    "COMMIT_PATCH",
    "VETO_AND_RETRY",
    "SPLIT_BLUEPRINT_STAGE",
]

STAGE_DEFS = [
    {
        "stage": "mcp_preflight",
        "role": "mcp_context_router",
        "action": "SELECT_MCP_PACKET",
        "objective": "Choose a compact MCP packet before any LLM authoring.",
        "cards": ["source_world", "source_cast", "blueprint_contract", "run_outcome_summary"],
        "budget": 1800,
    },
    {
        "stage": "cast_suspect_web",
        "role": "world_state_summarizer",
        "action": "ASK_LLM_BOUNDED_STAGE",
        "objective": "Build detective, victim, culprit, and suspect roles from source characters.",
        "cards": ["source_world", "source_cast", "source_scene_samples", "blueprint_contract"],
        "budget": 2200,
    },
    {
        "stage": "clue_variable_map",
        "role": "option_manifold_planner",
        "action": "ASK_LLM_BOUNDED_STAGE",
        "objective": "Map clue variables and investigative option families to the suspect web.",
        "cards": ["source_cast", "source_scene_samples", "clue_variable_contract", "best_blueprint_summary"],
        "budget": 2400,
    },
    {
        "stage": "encounter_batch_1",
        "role": "llm_prompt_composer",
        "action": "SELECT_MCP_PACKET",
        "objective": "Retrieve the smallest packet needed for encounters 1-4.",
        "cards": ["source_scene_samples", "blueprint_contract", "best_blueprint_summary", "materializer_contract"],
        "budget": 2600,
    },
    {
        "stage": "encounter_batch_2",
        "role": "reaction_dynamics_mapper",
        "action": "SELECT_MCP_PACKET",
        "objective": "Retrieve the smallest packet needed for encounters 5-8 and reaction deltas.",
        "cards": ["source_scene_samples", "clue_variable_contract", "best_blueprint_summary", "materializer_contract"],
        "budget": 2600,
    },
    {
        "stage": "encounter_batch_3",
        "role": "effect_script_synthesizer",
        "action": "SELECT_MCP_PACKET",
        "objective": "Retrieve the smallest packet needed for encounters 9-12 and effect-bearing choices.",
        "cards": ["clue_variable_contract", "best_blueprint_summary", "materializer_contract", "validator_contract"],
        "budget": 2600,
    },
    {
        "stage": "ending_secret_logic",
        "role": "gate_secret_route_designer",
        "action": "ASK_LLM_BOUNDED_STAGE",
        "objective": "Design regular endings and a secret ending that questions the obvious culprit frame.",
        "cards": ["source_world", "clue_variable_contract", "best_blueprint_summary", "ending_secret_contract"],
        "budget": 2400,
    },
    {
        "stage": "truncation_repair",
        "role": "validator_repair_critic",
        "action": "SPLIT_BLUEPRINT_STAGE",
        "objective": "If the model truncates or extracts only a partial object, split the blueprint into staged MCP packets.",
        "cards": ["blueprint_contract", "condition_9b_direct", "run_outcome_summary", "materializer_contract"],
        "budget": 1600,
    },
    {
        "stage": "commit_or_veto",
        "role": "commit_veto_controller",
        "action": "COMMIT_PATCH",
        "objective": "Commit only if extraction, validation, contract score, and materialized score are acceptable.",
        "cards": ["run_outcome_summary", "validator_contract", "scorecard_contract", "best_blueprint_summary"],
        "budget": 1600,
    },
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def normalize(text: Any, limit: int = 1200) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())[:limit]


def token_estimate(payload: Any) -> int:
    text = json.dumps(payload, ensure_ascii=True, separators=(",", ":")) if not isinstance(payload, str) else payload
    return max(1, len(text.encode("utf-8", errors="replace")) // 4)


def short_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()[:16]


def condition_dir(run_dir: Path, condition: str) -> Path:
    return run_dir / condition


def load_condition(run_dir: Path, condition: str) -> dict[str, Any]:
    cdir = condition_dir(run_dir, condition)
    status_path = cdir / "extract_status.json"
    blueprint_path = cdir / "blueprint.json"
    score_path = cdir / "scorecard" / "scorecard.json"
    validator_path = cdir / "validator_output.txt"
    status = read_json(status_path) if status_path.exists() else {}
    blueprint = read_json(blueprint_path) if blueprint_path.exists() else {}
    score = {}
    if score_path.exists():
        scorecard = read_json(score_path)
        ranked = scorecard.get("ranked", [])
        score = ranked[0] if ranked else {}
    validator = validator_path.read_text(encoding="utf-8", errors="replace").strip() if validator_path.exists() else ""
    return {
        "condition": condition,
        "status": status,
        "blueprint": blueprint,
        "score": score,
        "validator": validator,
    }


def blueprint_summary(condition_payload: dict[str, Any]) -> dict[str, Any]:
    blueprint = condition_payload.get("blueprint", {})
    suspects = blueprint.get("suspects", []) if isinstance(blueprint.get("suspects"), list) else []
    encounters = blueprint.get("encounters", []) if isinstance(blueprint.get("encounters"), list) else []
    endings = blueprint.get("endings", []) if isinstance(blueprint.get("endings"), list) else []
    secret = blueprint.get("secret_ending") if isinstance(blueprint.get("secret_ending"), dict) else {}
    return {
        "condition": condition_payload.get("condition"),
        "title": normalize(blueprint.get("title"), 160),
        "premise": normalize(blueprint.get("premise"), 500),
        "detective": normalize(blueprint.get("detective"), 120),
        "victim": normalize(blueprint.get("victim"), 120),
        "culprit": normalize(blueprint.get("culprit"), 120),
        "suspects": [
            {
                "name": normalize(s.get("name"), 100),
                "motive": normalize(s.get("motive"), 180),
                "alibi": normalize(s.get("alibi"), 180),
                "secret": normalize(s.get("secret"), 180),
            }
            for s in suspects
            if isinstance(s, dict)
        ][:6],
        "clue_variables": blueprint.get("clue_variables", []) if isinstance(blueprint.get("clue_variables"), list) else [],
        "encounter_count": len(encounters),
        "three_option_encounters": sum(
            1
            for enc in encounters
            if isinstance(enc, dict) and isinstance(enc.get("options"), list) and len(enc["options"]) >= 3
        ),
        "ending_count": len(endings),
        "secret_ending": {
            "title": normalize(secret.get("title"), 160),
            "threshold_logic": normalize(secret.get("threshold_logic"), 260),
        },
    }


def condition_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    score_row = payload.get("score", {})
    components = score_row.get("components", {}) if isinstance(score_row, dict) else {}
    return {
        "extract_ok": payload.get("status", {}).get("extract_ok"),
        "extract_error": payload.get("status", {}).get("error"),
        "validator_ok": "VALID OK" in str(payload.get("validator", "")),
        "small_model_builder_score": components.get("small_model_builder_score"),
        "weakest_component": score_row.get("weakest_component"),
        "blueprint_summary": blueprint_summary(payload),
    }


def build_cards(run_dir: Path, conditions: list[str]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    source = read_json(run_dir / "source_context.json")
    comparison = read_json(run_dir / "comparison_summary.json") if (run_dir / "comparison_summary.json").exists() else {}
    condition_payloads = {condition: load_condition(run_dir, condition) for condition in conditions}
    condition_summaries = {condition: condition_metrics(payload) for condition, payload in condition_payloads.items()}
    best_condition = max(
        conditions,
        key=lambda condition: (
            condition_summaries[condition]["blueprint_summary"]["encounter_count"],
            len(condition_summaries[condition]["blueprint_summary"]["suspects"]),
            condition_summaries[condition].get("small_model_builder_score") or 0,
        ),
    )
    cards: list[dict[str, Any]] = [
        {
            "card_id": "source_world",
            "card_type": "source_context",
            "title": source.get("source_title"),
            "source_path": source.get("source_path"),
            "about": source.get("about"),
        },
        {
            "card_id": "source_cast",
            "card_type": "cast",
            "characters": source.get("characters", []),
        },
        {
            "card_id": "source_scene_samples",
            "card_type": "scene_samples",
            "sample_scenes": source.get("sample_scenes", []),
        },
        {
            "card_id": "blueprint_contract",
            "card_type": "schema_contract",
            "required_keys": [
                "title",
                "premise",
                "detective",
                "victim",
                "culprit",
                "suspects",
                "clue_variables",
                "encounters",
                "endings",
                "secret_ending",
            ],
            "requirements": {
                "encounters": "12 playable investigation scenes",
                "options_per_encounter": 3,
                "endings": "5 regular endings plus a secret ending object",
                "secret_ending": "question obvious culprit frame, not just evidence maxing",
            },
        },
        {
            "card_id": "clue_variable_contract",
            "card_type": "mechanics_contract",
            "variables": ["Suspicion", "Evidence", "Alibi_Strength", "Trust", "Danger", "Secret_Knowledge"],
            "purpose": "Variables must support investigation, alibis, danger, trust, and hidden synthesis.",
        },
        {
            "card_id": "ending_secret_contract",
            "card_type": "ending_contract",
            "regular_endings": "Obvious conviction, culprit escape, witness pact, archive burn, institutional capture.",
            "secret_ending": "Requires at least two positive epistemic variables and avoids maximizing suspicion alone.",
        },
        {
            "card_id": "materializer_contract",
            "card_type": "tool_contract",
            "purpose": "Materializer converts blueprint into valid SweepWeave JSON; it can normalize structure but cannot recover missing creative design.",
            "risk": "A fallback materialization can validate while hiding a failed blueprint.",
        },
        {
            "card_id": "validator_contract",
            "card_type": "tool_contract",
            "purpose": "Validator checks JSON/schema/reachability but does not score blueprint creativity.",
        },
        {
            "card_id": "scorecard_contract",
            "card_type": "metric_contract",
            "purpose": "Structural builder score measures validity/scale/branching/control/text/readiness/native schema; use blueprint contract score to discriminate design quality.",
        },
        {
            "card_id": "run_outcome_summary",
            "card_type": "benchmark_receipt",
            "comparison_rows": comparison.get("rows", []),
            "condition_summaries": condition_summaries,
        },
        {
            "card_id": "best_blueprint_summary",
            "card_type": "blueprint_reference",
            "source_condition": best_condition,
            "summary": condition_summaries[best_condition]["blueprint_summary"],
        },
    ]
    for condition in conditions:
        cards.append(
            {
                "card_id": f"condition_{condition}",
                "card_type": "condition_receipt",
                "condition": condition,
                "metrics": condition_summaries[condition],
            }
        )
    indexed = {card["card_id"]: card for card in cards}
    for card in cards:
        card["token_estimate"] = token_estimate(card)
    return cards, indexed


def row_for_stage(stage_def: dict[str, Any], cards_by_id: dict[str, dict[str, Any]], conditions: list[str], row_index: int) -> dict[str, Any]:
    selected = [card_id for card_id in stage_def["cards"] if card_id in cards_by_id]
    selected_tokens = sum(int(cards_by_id[card_id].get("token_estimate", 0)) for card_id in selected)
    overflow = selected_tokens > int(stage_def["budget"])
    if overflow and "blueprint_contract" in selected:
        action = "SPLIT_BLUEPRINT_STAGE"
    else:
        action = stage_def["action"]
    condition_focus = conditions[row_index % len(conditions)]
    state = {
        "stage": stage_def["stage"],
        "role": stage_def["role"],
        "objective": stage_def["objective"],
        "condition_focus": condition_focus,
        "available_mcp_cards": [
            {
                "card_id": card_id,
                "card_type": cards_by_id[card_id].get("card_type"),
                "token_estimate": cards_by_id[card_id].get("token_estimate"),
            }
            for card_id in cards_by_id
        ],
        "retrieval_budget_tokens": stage_def["budget"],
        "selected_token_estimate": selected_tokens,
        "overflow": overflow,
        "failure_mode": "context_overflow" if overflow else "stage_needs_context",
        "mcp_query": {
            "need": stage_def["objective"],
            "must_preserve": ["source_character_names", "blueprint_schema", "bounded_stage_output"],
            "must_not_pull": ["whole_storyworld_json", "full_transcript", "unbounded_backstory"],
        },
    }
    target = {
        "action": action,
        "selected_card_ids": selected,
        "next_role": stage_def["role"],
        "stage": stage_def["stage"],
        "packet_budget_tokens": stage_def["budget"],
        "selected_token_estimate": selected_tokens,
        "rationale": (
            f"Retrieve {', '.join(selected)} for {stage_def['stage']} because the LLM should only see the "
            "bounded source, contract, and prior receipts needed for this stage."
        ),
    }
    return {
        "state": json.dumps(state, ensure_ascii=True, separators=(",", ":")),
        "tools": TOOLS,
        "action": action,
        "target": target,
        "meta": {
            "row_id": f"mcp_retrieval_{row_index:04d}_{short_hash(state)}",
            "role_id": stage_def["role"],
            "stage": stage_def["stage"],
            "condition_focus": condition_focus,
            "format": "mcp_retrieval_control",
        },
    }


def sft_message_for_row(row: dict[str, Any]) -> dict[str, Any]:
    state = json.loads(row["state"])
    user_payload = {
        "available_tools": row["tools"],
        "role": state["role"],
        "state": state,
    }
    assistant_payload = {
        "action": row["action"],
        "selected_card_ids": row["target"]["selected_card_ids"],
        "next_role": row["target"]["next_role"],
        "packet_budget_tokens": row["target"]["packet_budget_tokens"],
        "rationale": row["target"]["rationale"],
    }
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are an MCP retrieval TRM inside a Hermes storyworld skill. Select bounded MCP context before any LLM authoring. Return JSON only.",
            },
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=True, separators=(",", ":"))},
            {"role": "assistant", "content": json.dumps(assistant_payload, ensure_ascii=True, separators=(",", ":"))},
        ],
        "meta": {**row["meta"], "format": "chat_sft"},
    }


def metta_lines(cards: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[str]:
    lines = ["; MCP retrieval TRM curriculum facts"]
    for card in cards:
        cid = card["card_id"]
        lines.append(f"(MCPCard {cid})")
        lines.append(f"(CardType {cid} {card.get('card_type', 'unknown')})")
        lines.append(f"(CardTokens {cid} {card.get('token_estimate', 0)})")
    for row in rows:
        meta = row["meta"]
        row_id = meta["row_id"]
        lines.append(f"(RetrievalRow {row_id})")
        lines.append(f"(Stage {row_id} {meta['stage']})")
        lines.append(f"(TRMRole {row_id} {meta['role_id']})")
        lines.append(f"(Action {row_id} {row['action']})")
        for cid in row["target"]["selected_card_ids"]:
            lines.append(f"(SelectsCard {row_id} {cid})")
    return lines


def write_readme(out_dir: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# MCP Retrieval TRM Curriculum",
        "",
        "Purpose: train storyworld control-plane TRMs to pull bounded MCP context before LLM authoring stages.",
        "",
        "This corpus was generated from a murder-mystery storyworld comparison where direct 9B generation, long-output 9B generation, and Hermes 27B skill generation were compared on the same random source adaptation.",
        "",
        "## Outputs",
        "",
        "- `mcp_cards.jsonl`: retrieval cards that can live behind an MCP server or file-backed memory.",
        "- `retrieval_rows.jsonl`: `state/tools/action/target/meta` rows for TRM routing.",
        "- `sft_messages.jsonl`: chat-shaped distillation rows.",
        "- `train.jsonl` / `val.jsonl`: deterministic split of retrieval rows.",
        "- `mcp_retrieval_facts.metta`: symbolic facts connecting stages, roles, cards, and actions.",
        "- `train_manifest.json`: capped-training handoff; actual training must run under resource caps.",
        "",
        "## Key Claim",
        "",
        "The LLM should not be responsible for remembering the entire source, contract, run history, and validator behavior. A small control TRM can learn to retrieve the specific MCP cards needed for each stage, then hand a compact packet to the LLM.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, ensure_ascii=True),
        "```",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MCP retrieval TRM curriculum from storyworld benchmark artifacts.")
    parser.add_argument("--run-dir", required=True, help="Murder-mystery comparison run directory.")
    parser.add_argument("--out-dir", required=True, help="Output corpus directory.")
    parser.add_argument("--conditions", nargs="+", default=["9b_direct", "9b_direct_long", "27b_hermes_skill"])
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = REPO_ROOT / run_dir
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    cards, cards_by_id = build_cards(run_dir, args.conditions)
    rows = [row_for_stage(stage, cards_by_id, args.conditions, index) for index, stage in enumerate(STAGE_DEFS)]

    rng = random.Random(args.seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)
    val_count = max(1, int(round(len(shuffled) * args.val_ratio)))
    val_rows = shuffled[:val_count]
    train_rows = shuffled[val_count:]
    sft_rows = [sft_message_for_row(row) for row in rows]
    train_manifest = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_dir": str(run_dir),
        "rows": len(rows),
        "train_rows": len(train_rows),
        "val_rows": len(val_rows),
        "mcp_cards": len(cards),
        "estimated_tokens": sum(token_estimate(row) for row in rows),
        "resource_caps_required": {"ram_mb": 2048, "cpu_pct": 50, "io_mb_s": 50},
        "checkpoint_interval": "100 steps or 120 seconds",
        "chunk_strategy": "row-level shuffled minibatches; no whole-corpus tensor materialization",
        "status": "corpus_only_not_trained",
        "outputs": {
            "mcp_cards": str(out_dir / "mcp_cards.jsonl"),
            "retrieval_rows": str(out_dir / "retrieval_rows.jsonl"),
            "sft_messages": str(out_dir / "sft_messages.jsonl"),
            "train": str(out_dir / "train.jsonl"),
            "val": str(out_dir / "val.jsonl"),
            "metta": str(out_dir / "mcp_retrieval_facts.metta"),
        },
    }

    write_jsonl(out_dir / "mcp_cards.jsonl", cards)
    write_json(out_dir / "mcp_index.json", {card["card_id"]: card for card in cards})
    write_jsonl(out_dir / "retrieval_rows.jsonl", rows)
    write_jsonl(out_dir / "sft_messages.jsonl", sft_rows)
    write_jsonl(out_dir / "train.jsonl", train_rows)
    write_jsonl(out_dir / "val.jsonl", val_rows)
    (out_dir / "mcp_retrieval_facts.metta").write_text("\n".join(metta_lines(cards, rows)) + "\n", encoding="utf-8", newline="\n")
    write_json(out_dir / "train_manifest.json", train_manifest)
    write_readme(out_dir, train_manifest)
    print(str(out_dir / "train_manifest.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
