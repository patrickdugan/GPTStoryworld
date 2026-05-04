#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any


ROLE_ORDER = [
    "mcp_context_router",
    "world_state_summarizer",
    "llm_prompt_composer",
    "option_manifold_planner",
    "reaction_dynamics_mapper",
    "effect_script_synthesizer",
    "gate_secret_route_designer",
    "validator_repair_critic",
    "commit_veto_controller",
]


LLM_CALL_BY_ACTION = {
    "ASK_LLM_BOUNDED_DRAFT": "bounded_draft",
    "ASK_LLM_OPTION_SET": "option_set",
    "ASK_LLM_REACTION_TEXT": "reaction_text",
    "ASK_LLM_CLUE_LINES": "clue_lines",
}


OBJECTIVE_BY_FAILURE = {
    "context_overflow": "fit_context_budget",
    "insufficient_neighbor_context": "repair_context_packet",
    "option_blandness": "improve_option_manifold",
    "reaction_collapse": "restore_reaction_contrast",
    "missing_pvalue_refs": "repair_pvalue_alignment",
    "missing_p2value_refs": "repair_p2value_alignment",
    "effect_nudge_monoculture": "diversify_effect_scripts",
    "unreachable_secret": "repair_secret_route_reachability",
    "dominant_fallback_ending": "rebalance_ending_distribution",
    "dangling_consequence": "repair_schema_connectivity",
    "character_voice_drift": "repair_character_voice",
    "schema_parse_error": "repair_parseability",
    "no_metric_delta": "avoid_noop_repair",
    "gate_threshold_unforeshadowed": "foreshadow_gate_threshold",
    "too_much_llm_freeform": "constrain_llm_contract",
}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if raw:
            rows.append(json.loads(raw))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def parse_state(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("state", {})
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw_state": raw}
    return {}


def compact_id(text: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", text.lower()).strip("_")
    return slug[:64] or "episode"


def failure_mode(row: dict[str, Any]) -> str:
    labels = row.get("training_labels", {}) if isinstance(row.get("training_labels"), dict) else {}
    if labels.get("failure_mode"):
        return str(labels["failure_mode"])
    state = parse_state(row)
    return str(state.get("failure_mode") or row.get("failure_mode") or "unknown")


def role_id(row: dict[str, Any]) -> str:
    role = row.get("role", {}) if isinstance(row.get("role"), dict) else {}
    labels = row.get("training_labels", {}) if isinstance(row.get("training_labels"), dict) else {}
    return str(role.get("id") or labels.get("role_id") or "unknown_role")


def choose_objective(chunk: list[dict[str, Any]]) -> str:
    failures = [failure_mode(row) for row in chunk]
    counts = Counter(failures)
    selected = counts.most_common(1)[0][0] if counts else "unknown"
    return OBJECTIVE_BY_FAILURE.get(selected, f"repair_{compact_id(selected)}")


def metrics_before(row: dict[str, Any]) -> dict[str, float]:
    return {str(k): safe_float(v) for k, v in dict(row.get("metrics_before") or {}).items()}


def metrics_after(row: dict[str, Any]) -> dict[str, float]:
    return {str(k): safe_float(v) for k, v in dict(row.get("metrics_after") or {}).items()}


def average_metrics(items: list[dict[str, float]]) -> dict[str, float]:
    keys = sorted({key for item in items for key in item})
    out: dict[str, float] = {}
    for key in keys:
        vals = [item[key] for item in items if key in item]
        out[key] = round(sum(vals) / max(1, len(vals)), 4)
    return out


def context_tokens(row: dict[str, Any]) -> int:
    state = parse_state(row)
    mcp = state.get("mcp", {}) if isinstance(state.get("mcp"), dict) else {}
    contract = row.get("llm_input_contract", {}) if isinstance(row.get("llm_input_contract"), dict) else {}
    return int(safe_float(mcp.get("packet_tokens") or contract.get("max_input_tokens") or 0))


def model_tier_for_budget(context_budget_tokens: int) -> str:
    if context_budget_tokens <= 8192:
        return "9B_Q4"
    if context_budget_tokens <= 32768:
        return "27B_Q4"
    return "large_context_remote"


def llm_call_type(action: str) -> str:
    return LLM_CALL_BY_ACTION.get(action, "none")


def step_accepted(row: dict[str, Any]) -> bool:
    action = str(row.get("action") or "")
    before = metrics_before(row)
    after = metrics_after(row)
    if action == "VETO_AND_RETRY":
        return False
    if action == "COMMIT_PATCH":
        return after.get("validator_errors", 0.0) <= before.get("validator_errors", 0.0) and after.get("authoring_score", 0.0) >= before.get("authoring_score", 0.0)
    return True


def reward_for_episode(initial: dict[str, float], final: dict[str, float], max_packet_tokens: int, context_budget_tokens: int, steps: int) -> float:
    validator_before = initial.get("validator_errors", 0.0)
    validator_after = final.get("validator_errors", 0.0)
    if validator_before > 0 and validator_after <= 0:
        validator_delta = 1.0
    elif validator_after <= 0:
        validator_delta = 0.65
    else:
        validator_delta = 0.0

    authoring_delta = clamp01((final.get("authoring_score", 0.0) - initial.get("authoring_score", 0.0)) / 0.08)
    entropy_delta = clamp01((final.get("ending_entropy", 0.0) - initial.get("ending_entropy", 0.0)) / 0.35)
    alignment_delta = clamp01((final.get("pvalue_alignment", 0.0) - initial.get("pvalue_alignment", 0.0)) / 0.20)
    context_efficiency = clamp01(context_budget_tokens / max(1.0, float(max_packet_tokens or context_budget_tokens)))
    repair_cost_inverse = clamp01(1.0 - (max(0, steps - 3) / 12.0))

    reward = (
        0.25 * validator_delta
        + 0.20 * authoring_delta
        + 0.15 * entropy_delta
        + 0.15 * alignment_delta
        + 0.10 * 0.50
        + 0.10 * context_efficiency
        + 0.05 * repair_cost_inverse
    )
    if validator_after > 0:
        reward = min(reward, 0.20)
    if final.get("authoring_score", 0.0) <= initial.get("authoring_score", 0.0) and validator_after >= validator_before:
        reward = min(reward, 0.30)
    if max_packet_tokens > context_budget_tokens:
        reward = min(reward, 0.40)
    return round(clamp01(reward), 4)


def build_episode(chunk: list[dict[str, Any]], episode_index: int, context_budget_tokens: int) -> dict[str, Any]:
    objective = choose_objective(chunk)
    world = str(chunk[0].get("world_archetype") or parse_state(chunk[0]).get("world") or "synthetic_storyworld")
    initial = average_metrics([metrics_before(row) for row in chunk])
    final = average_metrics([metrics_after(row) for row in chunk])
    max_packet = max([context_tokens(row) for row in chunk] or [context_budget_tokens])
    steps: list[dict[str, Any]] = []
    for step_index, row in enumerate(chunk):
        action = str(row.get("action") or "")
        steps.append(
            {
                "step_index": step_index,
                "role_id": role_id(row),
                "state_ref": str(row.get("id") or f"trajectory_{row.get('index', step_index)}"),
                "chosen_action": action,
                "llm_call_type": llm_call_type(action),
                "context_packet_ref": f"mcp_packet_{episode_index:04d}_{step_index:02d}",
                "output_ref": f"trajectory_output_{row.get('id', step_index)}",
                "verifier_delta_ref": f"verifier_delta_{episode_index:04d}_{step_index:02d}",
                "accepted": step_accepted(row),
                "failure_mode": failure_mode(row),
            }
        )
    reward = reward_for_episode(initial, final, max_packet, context_budget_tokens, len(steps))
    success = reward >= 0.55 and final.get("validator_errors", 0.0) <= initial.get("validator_errors", 0.0)
    failure_class = "none" if success else choose_failure_class(initial, final, max_packet, context_budget_tokens)
    return {
        "episode_id": f"episode_{episode_index:06d}_{compact_id(objective)}",
        "world_id": compact_id(world),
        "model_tier": model_tier_for_budget(context_budget_tokens),
        "context_budget_tokens": context_budget_tokens,
        "objective": objective,
        "initial_metrics": initial,
        "steps": steps,
        "final_metrics": final,
        "episode_label": {
            "success": success,
            "best_next_role": "stop" if success else steps[0]["role_id"],
            "failure_class": failure_class,
            "reward": reward,
        },
    }


def choose_failure_class(initial: dict[str, float], final: dict[str, float], max_packet_tokens: int, context_budget_tokens: int) -> str:
    if max_packet_tokens > context_budget_tokens:
        return "context_overflow"
    if final.get("validator_errors", 0.0) > 0:
        return "validator_failure"
    if final.get("authoring_score", 0.0) <= initial.get("authoring_score", 0.0):
        return "no_metric_delta"
    return "low_reward"


def build_master_rows(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    role_tools = ROLE_ORDER + ["stop"]
    for episode in episodes:
        history: list[dict[str, Any]] = []
        for step in episode["steps"]:
            state = {
                "episode_id": episode["episode_id"],
                "world_id": episode["world_id"],
                "model_tier": episode["model_tier"],
                "context_budget_tokens": episode["context_budget_tokens"],
                "objective": episode["objective"],
                "initial_metrics": episode["initial_metrics"],
                "current_failure_mode": step.get("failure_mode", "unknown"),
            }
            rows.append(
                {
                    "state": json.dumps(state, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
                    "tools": role_tools,
                    "action": step["role_id"],
                    "meta": {
                        "episode_id": episode["episode_id"],
                        "step_index": step["step_index"],
                        "objective": episode["objective"],
                        "chosen_action": step["chosen_action"],
                        "llm_call_type": step["llm_call_type"],
                        "reward": episode["episode_label"]["reward"],
                    },
                }
            )
            history.append(
                {
                    "role_id": step["role_id"],
                    "chosen_action": step["chosen_action"],
                    "accepted": step["accepted"],
                }
            )
    return rows


def split_episodes(episodes: list[dict[str, Any]], val_fraction: float, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    shuffled = list(episodes)
    rng.shuffle(shuffled)
    val_count = max(1, int(round(len(shuffled) * val_fraction))) if shuffled else 0
    return shuffled[val_count:], shuffled[:val_count]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build episode-level master control planner rows from the 9-TRM trajectory library.")
    parser.add_argument("--trajectory-library", default="hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed/trajectory_library.jsonl")
    parser.add_argument("--out-dir", default="hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_seed")
    parser.add_argument("--episode-size", type=int, default=9)
    parser.add_argument("--context-budget-tokens", type=int, default=8192)
    parser.add_argument("--val-fraction", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=41)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.trajectory_library).resolve()
    out_dir = Path(args.out_dir).resolve()
    rows = load_jsonl(source)
    episode_size = max(2, int(args.episode_size))
    chunks = [rows[i : i + episode_size] for i in range(0, len(rows), episode_size)]
    chunks = [chunk for chunk in chunks if len(chunk) >= 2]
    episodes = [build_episode(chunk, ix, int(args.context_budget_tokens)) for ix, chunk in enumerate(chunks)]
    master_rows = build_master_rows(episodes)
    train_episodes, val_episodes = split_episodes(episodes, float(args.val_fraction), int(args.seed))
    train_rows = build_master_rows(train_episodes)
    val_rows = build_master_rows(val_episodes)

    write_jsonl(out_dir / "trajectory_episodes.jsonl", episodes)
    write_jsonl(out_dir / "master_control_rows.jsonl", master_rows)
    write_jsonl(out_dir / "train.jsonl", train_rows)
    write_jsonl(out_dir / "val.jsonl", val_rows)
    write_jsonl(out_dir / "episode_train.jsonl", train_episodes)
    write_jsonl(out_dir / "episode_val.jsonl", val_episodes)
    write_json(out_dir / "sample_episode.json", episodes[0] if episodes else {})
    write_json(out_dir / "sample_master_row.json", master_rows[0] if master_rows else {})
    manifest = {
        "created_at": now_iso(),
        "source": str(source),
        "out_dir": str(out_dir),
        "episode_count": len(episodes),
        "master_control_rows": len(master_rows),
        "train_rows": len(train_rows),
        "val_rows": len(val_rows),
        "episode_train_rows": len(train_episodes),
        "episode_val_rows": len(val_episodes),
        "split_mode": "episode_disjoint",
        "episode_size": episode_size,
        "context_budget_tokens": int(args.context_budget_tokens),
        "model_tier": model_tier_for_budget(int(args.context_budget_tokens)),
        "objective_counts": dict(Counter(ep["objective"] for ep in episodes)),
        "role_counts": dict(Counter(row["action"] for row in master_rows)),
        "success_rate": round(sum(1 for ep in episodes if ep["episode_label"]["success"]) / max(1, len(episodes)), 4),
        "avg_reward": round(sum(float(ep["episode_label"]["reward"]) for ep in episodes) / max(1, len(episodes)), 4),
    }
    write_json(out_dir / "manifest.json", manifest)
    readme = [
        "# Master Control Planner Seed Corpus",
        "",
        "Episode-level curriculum derived from the 9-TRM encounter trajectory library.",
        "",
        f"- Episodes: `{manifest['episode_count']}`",
        f"- Master control rows: `{manifest['master_control_rows']}`",
        f"- Model tier: `{manifest['model_tier']}`",
        f"- Context budget: `{manifest['context_budget_tokens']}` tokens",
        f"- Average reward: `{manifest['avg_reward']}`",
        f"- Success rate: `{manifest['success_rate']}`",
        "",
        "Files:",
        "",
        "- `trajectory_episodes.jsonl`: episode-level planner rows.",
        "- `master_control_rows.jsonl`: per-step `global_state/tools -> next_role` rows.",
        "- `train.jsonl` / `val.jsonl`: row views derived from an episode-disjoint split.",
        "- `episode_train.jsonl` / `episode_val.jsonl`: episode split for sequence-level evaluation.",
        "- `sample_episode.json`: one readable episode.",
        "- `manifest.json`: corpus receipt.",
        "",
        "This is still synthetic bootstrapping data. Because the seed episodes follow the nine-role conveyor order, a tiny baseline is a smoke receipt, not a generalization proof. The next lift comes from appending real Hermes/conveyor histories with skipped, repeated, and failed role transitions.",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(readme), encoding="utf-8", newline="\n")
    print(str(out_dir))
    print(json.dumps(manifest, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
