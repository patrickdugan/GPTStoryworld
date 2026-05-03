#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import time
from pathlib import Path
from typing import Any


TRM_ROLES: list[dict[str, Any]] = [
    {
        "id": "mcp_context_router",
        "name": "MCP Context Router TRM",
        "purpose": "Select the smallest context packet the LLM needs for one encounter edit.",
        "primary_action": "SELECT_MCP_PACKET",
        "llm_contract": "Do not ask for prose yet; first bound the packet to world card, target encounter, neighbor hops, and ledger keys.",
        "success_metric": "prompt_tokens_within_budget",
    },
    {
        "id": "world_state_summarizer",
        "name": "World State Summarizer TRM",
        "purpose": "Compress MeTTa facts, ledger deltas, character beliefs, and threshold pressure into a state card.",
        "primary_action": "BUILD_STATE_CARD",
        "llm_contract": "Ask the LLM only to resolve ambiguous theme language after deterministic variables are listed.",
        "success_metric": "state_card_covers_gate_variables",
    },
    {
        "id": "llm_prompt_composer",
        "name": "LLM Prompt Composer TRM",
        "purpose": "Turn the state card into a strict bounded authoring request.",
        "primary_action": "ASK_LLM_BOUNDED_DRAFT",
        "llm_contract": "Request only the missing encounter component and demand stable IDs plus JSON/SWMD-safe text.",
        "success_metric": "llm_output_parseable",
    },
    {
        "id": "option_manifold_planner",
        "name": "Option Manifold Planner TRM",
        "purpose": "Choose option archetypes that expose genuine tradeoffs and variable deltas.",
        "primary_action": "ASK_LLM_OPTION_SET",
        "llm_contract": "Ask for 3-5 options with intended variable movement, not final full encounter JSON.",
        "success_metric": "option_delta_coverage",
    },
    {
        "id": "reaction_dynamics_mapper",
        "name": "Reaction Dynamics Mapper TRM",
        "purpose": "Map each option to success, mixed, and failure reactions with character-specific consequences.",
        "primary_action": "ASK_LLM_REACTION_TEXT",
        "llm_contract": "Ask the LLM for local reaction prose under fixed consequence IDs and fixed outcome slots.",
        "success_metric": "reaction_contrast",
    },
    {
        "id": "effect_script_synthesizer",
        "name": "Effect Script Synthesizer TRM",
        "purpose": "Convert narrative intent into effect operators, pValues, p2Values, and non-zero constants.",
        "primary_action": "SYNTHESIZE_EFFECT_SCRIPT",
        "llm_contract": "Ask the LLM for rationale only; generate schema mechanics deterministically.",
        "success_metric": "effect_and_pvalue_alignment",
    },
    {
        "id": "gate_secret_route_designer",
        "name": "Gate And Secret Route Designer TRM",
        "purpose": "Design visibility, performability, clue, and threshold logic for secret or synthesis paths.",
        "primary_action": "DESIGN_GATE_THRESHOLDS",
        "llm_contract": "Ask for clue lines and player-facing foreshadowing, not arbitrary gate values.",
        "success_metric": "secret_route_reachability",
    },
    {
        "id": "validator_repair_critic",
        "name": "Validator Repair Critic TRM",
        "purpose": "Classify validator, quality, Monte Carlo, and authoring-score defects into typed repair targets.",
        "primary_action": "SELECT_REPAIR_TARGET",
        "llm_contract": "Ask the LLM to explain only defects that the deterministic tools cannot classify.",
        "success_metric": "repair_target_matches_metric_delta",
    },
    {
        "id": "commit_veto_controller",
        "name": "Commit/Veto Controller TRM",
        "purpose": "Accept, retry, reroute, or shrink context based on measured deltas and parse stability.",
        "primary_action": "COMMIT_OR_VETO",
        "llm_contract": "Do not ask the LLM to self-certify; use it only for bounded retry instructions after veto.",
        "success_metric": "no_noop_commits",
    },
]


WORLD_ARCHETYPES = [
    "Macbeth court succession crisis",
    "Mu'tazili qadi examination drama",
    "diplomacy coalition betrayal",
    "goblin mountain socio-ecology",
    "Scarlet Letter reputation spiral",
    "noir heist under double-cross pressure",
    "bioethics review board with hidden incentives",
    "faerie business contract trap",
    "space ark constitutional convention",
    "small-town council conspiracy",
    "AI lab red-team airgap exercise",
    "postwar treaty negotiation",
]


ENCOUNTER_INTENTS = [
    "opening pressure",
    "mid-act dilemma",
    "late-act threshold test",
    "secret route clue",
    "character reversal",
    "coalition break",
    "public accusation",
    "repair pass after validator failure",
    "ending basin fork",
    "mechanics-rich exposition",
]


FAILURE_MODES = [
    "context_overflow",
    "option_blandness",
    "reaction_collapse",
    "missing_pvalue_refs",
    "missing_p2value_refs",
    "effect_nudge_monoculture",
    "unreachable_secret",
    "dominant_fallback_ending",
    "dangling_consequence",
    "character_voice_drift",
    "schema_parse_error",
    "no_metric_delta",
    "gate_threshold_unforeshadowed",
    "insufficient_neighbor_context",
    "too_much_llm_freeform",
]


VARIABLES = [
    "legitimacy",
    "trust",
    "ambition",
    "mercy",
    "orthodoxy",
    "coalition_pressure",
    "reputation",
    "ritual_precision",
    "secrecy",
    "public_order",
    "countercraft",
    "loyalty",
]


TOOLS = [
    "READ_MCP_CONTEXT",
    "BUILD_METTA_FACTS",
    "BUILD_STATE_CARD",
    "ASK_LLM_BOUNDED_DRAFT",
    "ASK_LLM_OPTION_SET",
    "ASK_LLM_REACTION_TEXT",
    "ASK_LLM_CLUE_LINES",
    "SYNTHESIZE_EFFECT_SCRIPT",
    "DESIGN_GATE_THRESHOLDS",
    "RUN_VALIDATOR",
    "RUN_MONTE_CARLO",
    "SELECT_REPAIR_TARGET",
    "COMMIT_PATCH",
    "VETO_AND_RETRY",
    "SHRINK_CONTEXT",
]


ACTION_BY_FAILURE = {
    "context_overflow": "SHRINK_CONTEXT",
    "option_blandness": "ASK_LLM_OPTION_SET",
    "reaction_collapse": "ASK_LLM_REACTION_TEXT",
    "missing_pvalue_refs": "SYNTHESIZE_EFFECT_SCRIPT",
    "missing_p2value_refs": "SYNTHESIZE_EFFECT_SCRIPT",
    "effect_nudge_monoculture": "SYNTHESIZE_EFFECT_SCRIPT",
    "unreachable_secret": "DESIGN_GATE_THRESHOLDS",
    "dominant_fallback_ending": "SELECT_REPAIR_TARGET",
    "dangling_consequence": "RUN_VALIDATOR",
    "character_voice_drift": "ASK_LLM_BOUNDED_DRAFT",
    "schema_parse_error": "VETO_AND_RETRY",
    "no_metric_delta": "VETO_AND_RETRY",
    "gate_threshold_unforeshadowed": "ASK_LLM_CLUE_LINES",
    "insufficient_neighbor_context": "READ_MCP_CONTEXT",
    "too_much_llm_freeform": "ASK_LLM_BOUNDED_DRAFT",
}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    return len(rows)


def token_estimate(text: str) -> int:
    return max(1, len(re.findall(r"[A-Za-z0-9_'-]+|[{}\\[\\]:,./>=<-]", text)))


def compact_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def stable_id(payload: Any) -> str:
    return hashlib.sha1(compact_json(payload).encode("utf-8")).hexdigest()[:16]


def choose_action(role: dict[str, Any], failure_mode: str, metrics_before: dict[str, float], metrics_after: dict[str, float]) -> str:
    role_id = str(role["id"])
    if role["id"] == "commit_veto_controller":
        if metrics_after["authoring_score"] > metrics_before["authoring_score"] and failure_mode not in {"schema_parse_error", "no_metric_delta"}:
            return "COMMIT_PATCH"
        return "VETO_AND_RETRY"
    if role_id == "mcp_context_router":
        if failure_mode in {"context_overflow", "insufficient_neighbor_context"}:
            return ACTION_BY_FAILURE[failure_mode]
        return "SELECT_MCP_PACKET"
    if role_id == "world_state_summarizer":
        return "BUILD_STATE_CARD"
    if role_id == "llm_prompt_composer":
        return "ASK_LLM_BOUNDED_DRAFT"
    if role_id == "option_manifold_planner":
        return "ASK_LLM_OPTION_SET"
    if role_id == "reaction_dynamics_mapper":
        return "ASK_LLM_REACTION_TEXT"
    if role_id == "effect_script_synthesizer":
        return "SYNTHESIZE_EFFECT_SCRIPT"
    if role_id == "gate_secret_route_designer":
        if failure_mode == "gate_threshold_unforeshadowed":
            return "ASK_LLM_CLUE_LINES"
        return "DESIGN_GATE_THRESHOLDS"
    if role_id == "validator_repair_critic":
        return "SELECT_REPAIR_TARGET" if failure_mode != "dangling_consequence" else "RUN_VALIDATOR"
    return str(role["primary_action"])


def build_metta_facts(row_seed: dict[str, Any]) -> list[str]:
    enc = row_seed["encounter_id"]
    role = row_seed["role_id"]
    focus = row_seed["focus_variable"]
    failure = row_seed["failure_mode"]
    return [
        f"(Encounter {enc})",
        f"(TRMRole {role})",
        f"(FocusVariable {enc} {focus})",
        f"(FailureMode {enc} {failure})",
        f"(NeedsLLMBoundedInput {role} true)",
        f"(ControlMetric {enc} {row_seed['success_metric']})",
    ]


def build_llm_input_contract(role: dict[str, Any], row_seed: dict[str, Any]) -> dict[str, Any]:
    focus = row_seed["focus_variable"]
    return {
        "call_type": role["primary_action"],
        "max_input_tokens": row_seed["packet_tokens"],
        "max_output_tokens": row_seed["output_tokens"],
        "must_include": [
            "stable_ids",
            "target_encounter_only",
            f"focus_variable:{focus}",
            "no_whole_world_rewrite",
        ],
        "must_not_include": [
            "new_global_schema",
            "unbounded_backstory",
            "self_certification",
        ],
        "expected_shape": {
            "analysis_brief": "one paragraph",
            "patch_intent": "one typed repair target",
            "candidate_content": "bounded component only",
            "risk_flags": ["parse", "continuity", "metric_delta"],
        },
    }


def build_row(index: int, rng: random.Random) -> dict[str, Any]:
    role = TRM_ROLES[index % len(TRM_ROLES)]
    world = rng.choice(WORLD_ARCHETYPES)
    intent = rng.choice(ENCOUNTER_INTENTS)
    failure = rng.choice(FAILURE_MODES)
    focus = rng.choice(VARIABLES)
    neighbor_hops = 0 if failure == "context_overflow" else rng.choice([0, 1, 1, 2])
    packet_tokens = rng.choice([1800, 2400, 3200, 4800, 6400, 9600])
    if failure == "context_overflow":
        packet_tokens = rng.choice([12800, 18000, 26000])
    output_tokens = rng.choice([256, 384, 512, 768])
    encounter_id = f"enc_{index // len(TRM_ROLES):04d}_{role['id'][:4]}"
    metrics_before = {
        "authoring_score": round(rng.uniform(0.42, 0.72), 4),
        "pvalue_alignment": round(rng.uniform(0.0, 0.65), 4),
        "ending_entropy": round(rng.uniform(0.1, 0.8), 4),
        "validator_errors": float(rng.choice([0, 0, 1, 2])),
    }
    improvement = rng.uniform(0.01, 0.09)
    if failure in {"schema_parse_error", "no_metric_delta"}:
        improvement = rng.uniform(-0.02, 0.004)
    metrics_after = {
        "authoring_score": round(max(0.0, min(1.0, metrics_before["authoring_score"] + improvement)), 4),
        "pvalue_alignment": round(max(0.0, min(1.0, metrics_before["pvalue_alignment"] + rng.uniform(0.0, 0.12))), 4),
        "ending_entropy": round(max(0.0, min(1.0, metrics_before["ending_entropy"] + rng.uniform(-0.03, 0.09))), 4),
        "validator_errors": 0.0 if failure not in {"schema_parse_error", "dangling_consequence"} else metrics_before["validator_errors"],
    }
    row_seed = {
        "role_id": role["id"],
        "encounter_id": encounter_id,
        "focus_variable": focus,
        "failure_mode": failure,
        "success_metric": role["success_metric"],
        "packet_tokens": packet_tokens,
        "output_tokens": output_tokens,
    }
    action = choose_action(role, failure, metrics_before, metrics_after)
    metta_facts = build_metta_facts(row_seed)
    llm_contract = build_llm_input_contract(role, row_seed)
    available_tools = sorted(set([role["primary_action"], action, "READ_MCP_CONTEXT", "RUN_VALIDATOR", "VETO_AND_RETRY", "COMMIT_PATCH"]))
    if role["id"] == "gate_secret_route_designer":
        available_tools.append("ASK_LLM_CLUE_LINES")
    state_payload = {
        "trajectory": index,
        "role": role["id"],
        "world": world,
        "encounter_id": encounter_id,
        "intent": intent,
        "failure_mode": failure,
        "focus_variable": focus,
        "mcp": {
            "neighbor_hops": neighbor_hops,
            "packet_tokens": packet_tokens,
            "output_tokens": output_tokens,
        },
        "metta_facts": metta_facts,
        "metrics_before": metrics_before,
        "llm_contract": llm_contract,
    }
    rationale = (
        f"{role['name']} should choose {action} because the active defect is {failure}, "
        f"the encounter intent is {intent}, and the LLM must be used only for bounded input that preserves {focus} mechanics."
    )
    row = {
        "id": stable_id({"i": index, "role": role["id"], "failure": failure, "world": world}),
        "index": index,
        "role": role,
        "world_archetype": world,
        "encounter_id": encounter_id,
        "encounter_intent": intent,
        "failure_mode": failure,
        "focus_variable": focus,
        "available_tools": available_tools,
        "action": action,
        "state": compact_json(state_payload),
        "metta_facts": metta_facts,
        "llm_input_contract": llm_contract,
        "metrics_before": metrics_before,
        "metrics_after": metrics_after,
        "control_rationale": rationale,
        "training_labels": {
            "role_id": role["id"],
            "primary_action": role["primary_action"],
            "chosen_action": action,
            "success_metric": role["success_metric"],
            "commit_expected": action == "COMMIT_PATCH",
            "uses_llm": action.startswith("ASK_LLM") or role["id"] in {"llm_prompt_composer", "reaction_dynamics_mapper"},
            "requires_validator": action in {"RUN_VALIDATOR", "COMMIT_PATCH", "VETO_AND_RETRY"},
        },
    }
    row["token_estimate"] = token_estimate(compact_json(row))
    return row


def to_control_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": row["state"],
        "tools": row["available_tools"],
        "action": row["action"],
        "meta": {
            "trajectory_id": row["id"],
            "role_id": row["role"]["id"],
            "failure_mode": row["failure_mode"],
            "world_archetype": row["world_archetype"],
            "token_estimate": row["token_estimate"],
        },
    }


def to_sft_row(row: dict[str, Any]) -> dict[str, Any]:
    system = (
        "You are a control-plane TRM distillation target inside a Hermes storyworld skill. "
        "Choose the next bounded action for the LLM/tool flow. Return JSON only."
    )
    user = {
        "role": row["role"]["id"],
        "state": json.loads(row["state"]),
        "available_tools": row["available_tools"],
    }
    assistant = {
        "action": row["action"],
        "llm_input_contract": row["llm_input_contract"],
        "rationale": row["control_rationale"],
    }
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": compact_json(user)},
            {"role": "assistant", "content": compact_json(assistant)},
        ],
        "meta": {
            "trajectory_id": row["id"],
            "role_id": row["role"]["id"],
            "format": "chat_sft",
        },
    }


def split_rows(rows: list[dict[str, Any]], train_ratio: float, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    working = list(rows)
    random.Random(seed).shuffle(working)
    split_at = int(len(working) * train_ratio)
    split_at = min(max(split_at, 1), len(working) - 1) if len(working) > 1 else len(working)
    return working[:split_at], working[split_at:]


def write_role_matrix(path: Path, rows: list[dict[str, Any]]) -> None:
    counts: dict[str, dict[str, int]] = {}
    for row in rows:
        role_id = row["role"]["id"]
        action = row["action"]
        counts.setdefault(role_id, {})
        counts[role_id][action] = counts[role_id].get(action, 0) + 1
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role_id", "action", "count"])
        writer.writeheader()
        for role_id in sorted(counts):
            for action, count in sorted(counts[role_id].items()):
                writer.writerow({"role_id": role_id, "action": action, "count": count})


def write_metta(path: Path, rows: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    for role in TRM_ROLES:
        lines.append(f"(TRMRole {role['id']})")
        lines.append(f"(PrimaryAction {role['id']} {role['primary_action']})")
        lines.append(f"(SuccessMetric {role['id']} {role['success_metric']})")
    for row in rows:
        lines.append(f"(Trajectory {row['id']})")
        lines.append(f"(TrajectoryRole {row['id']} {row['role']['id']})")
        lines.append(f"(ChosenAction {row['id']} {row['action']})")
        lines.append(f"(FailureMode {row['id']} {row['failure_mode']})")
        lines.append(f"(FocusVariable {row['id']} {row['focus_variable']})")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_readme(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(
        "# 9-TRM Encounter Assembly Trajectory Library\n\n"
        "This pack trains control-plane TRMs for a Hermes storyworld skill flow. "
        "The LLM is treated as a bounded component that supplies local prose, option candidates, clue lines, or rationale. "
        "The TRMs decide what to ask for, what context to fetch, how to translate prose into mechanics, and when to commit or veto.\n\n"
        "## Nine TRMs\n\n"
        + "\n".join(f"- `{role['id']}`: {role['purpose']}" for role in TRM_ROLES)
        + "\n\n## Files\n\n"
        "- `trajectory_library.jsonl`: full structured rows.\n"
        "- `trm_control_rows.jsonl`: normalized `state/tools/action/meta` rows for router/control training.\n"
        "- `sft_messages.jsonl`: chat-shaped rows for distilling the control policy through an LLM if needed.\n"
        "- `world_control_facts.metta`: compact symbolic control facts.\n"
        "- `train.jsonl` and `val.jsonl`: shuffled control-row split.\n"
        "- `role_action_matrix.csv`: coverage by role and chosen action.\n"
        "- `train_manifest.json`: safe training handoff with caps and checkpoint cadence.\n\n"
        f"Rows: {manifest['rows']}\n\n"
        f"Estimated tokens: {manifest['estimated_tokens']}\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a 9-TRM encounter assembly trajectory library.")
    parser.add_argument("--out-dir", default="hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed")
    parser.add_argument("--trajectory-count", type=int, default=1000)
    parser.add_argument("--target-tokens", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--train-ratio", type=float, default=0.9)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    rows: list[dict[str, Any]] = []
    total_tokens = 0
    index = 0
    while len(rows) < args.trajectory_count or total_tokens < args.target_tokens:
        row = build_row(index, rng)
        rows.append(row)
        total_tokens += int(row["token_estimate"])
        index += 1
        if len(rows) >= args.trajectory_count and total_tokens >= args.target_tokens:
            break

    control_rows = [to_control_row(row) for row in rows]
    sft_rows = [to_sft_row(row) for row in rows]
    train_rows, val_rows = split_rows(control_rows, args.train_ratio, args.seed)

    trajectory_path = out_dir / "trajectory_library.jsonl"
    control_path = out_dir / "trm_control_rows.jsonl"
    sft_path = out_dir / "sft_messages.jsonl"
    train_path = out_dir / "train.jsonl"
    val_path = out_dir / "val.jsonl"
    manifest_path = out_dir / "manifest.json"
    train_manifest_path = out_dir / "train_manifest.json"

    append_jsonl(trajectory_path, rows)
    append_jsonl(control_path, control_rows)
    append_jsonl(sft_path, sft_rows)
    append_jsonl(train_path, train_rows)
    append_jsonl(val_path, val_rows)
    write_role_matrix(out_dir / "role_action_matrix.csv", rows)
    write_metta(out_dir / "world_control_facts.metta", rows)

    role_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for row in rows:
        role_counts[row["role"]["id"]] = role_counts.get(row["role"]["id"], 0) + 1
        action_counts[row["action"]] = action_counts.get(row["action"], 0) + 1

    manifest = {
        "created_at": now_iso(),
        "rows": len(rows),
        "estimated_tokens": total_tokens,
        "target_tokens": args.target_tokens,
        "trajectory_count_requested": args.trajectory_count,
        "seed": args.seed,
        "role_counts": role_counts,
        "action_counts": action_counts,
        "outputs": {
            "trajectory_library": str(trajectory_path),
            "trm_control_rows": str(control_path),
            "sft_messages": str(sft_path),
            "train": str(train_path),
            "val": str(val_path),
            "metta": str(out_dir / "world_control_facts.metta"),
            "role_action_matrix": str(out_dir / "role_action_matrix.csv"),
        },
    }
    dump_json(manifest_path, manifest)

    train_manifest = {
        "training_task_id": f"encounter_assembly_9trm_{args.seed}",
        "status": "corpus_ready_training_not_launched",
        "objective": "Train nine control-plane TRMs to orchestrate bounded LLM calls inside MCP+MeTTa+Hermes storyworld encounter assembly.",
        "data": {
            "train_jsonl": str(train_path),
            "val_jsonl": str(val_path),
            "control_rows_jsonl": str(control_path),
            "sft_messages_jsonl": str(sft_path),
        },
        "resource_caps": {
            "ram_mb": 2048,
            "cpu_pct": 50,
            "io_mb_s": 50,
            "checkpoint_interval_steps": 100,
            "chunk_strategy": "role_sharded_minibatches",
        },
        "recommended_ablation": [
            "all_9_trms",
            "no_commit_veto_controller",
            "no_gate_secret_route_designer",
            "llm_prompt_composer_only",
            "no_metta_facts",
        ],
        "launch_rule": "Do not start training outside a hard-cap wrapper.",
    }
    dump_json(train_manifest_path, train_manifest)
    write_readme(out_dir / "README.md", manifest)

    print(str(out_dir))
    print(str(manifest_path))
    print(str(train_manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
