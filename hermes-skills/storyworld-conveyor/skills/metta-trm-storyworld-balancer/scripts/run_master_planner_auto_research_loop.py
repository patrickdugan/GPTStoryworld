#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_MODEL = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "trm_runs" / "master_control_planner_tiny" / "model.json"
DEFAULT_STORYWORLDS = [
    REPO_ROOT / "storyworlds" / "by-week" / "2026-W11" / "validated_macbeth.json",
    REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "working_worlds" / "romeo_sanaa_qwen27b_40enc" / "hermes_qwen27b_packet_storyworld.json",
]

ROLES = [
    "mcp_context_router",
    "world_state_summarizer",
    "llm_prompt_composer",
    "option_manifold_planner",
    "reaction_dynamics_mapper",
    "effect_script_synthesizer",
    "gate_secret_route_designer",
    "validator_repair_critic",
    "commit_veto_controller",
    "stop",
]

READER_OPERATORS = {
    "GreaterThan",
    "GreaterThanOrEqualTo",
    "Arithmetic Comparator",
    "And",
    "Or",
    "Addition",
    "Multiplication",
    "Absolute Value",
    "Nudge",
}

OBJECTIVE_TO_ROLE = {
    "fit_context_budget": "mcp_context_router",
    "repair_context_packet": "mcp_context_router",
    "build_state_card": "world_state_summarizer",
    "compose_bounded_prompt": "llm_prompt_composer",
    "improve_option_manifold": "option_manifold_planner",
    "restore_reaction_contrast": "reaction_dynamics_mapper",
    "diversify_effect_scripts": "effect_script_synthesizer",
    "repair_secret_route_reachability": "gate_secret_route_designer",
    "repair_schema_connectivity": "validator_repair_critic",
    "repair_reader_semantics": "validator_repair_critic",
    "avoid_noop_repair": "commit_veto_controller",
}

FAILURE_TO_ROLE = {
    "context_overflow": "mcp_context_router",
    "insufficient_neighbor_context": "mcp_context_router",
    "dangling_consequence": "validator_repair_critic",
    "unsupported_reader_operator": "validator_repair_critic",
    "schema_parse_error": "validator_repair_critic",
    "unreachable_secret": "gate_secret_route_designer",
    "gate_threshold_unforeshadowed": "gate_secret_route_designer",
    "effect_nudge_monoculture": "effect_script_synthesizer",
    "missing_pvalue_refs": "effect_script_synthesizer",
    "missing_p2value_refs": "effect_script_synthesizer",
    "reaction_collapse": "reaction_dynamics_mapper",
    "option_blandness": "option_manifold_planner",
    "too_much_llm_freeform": "llm_prompt_composer",
    "no_metric_delta": "commit_veto_controller",
}

ROLE_TO_ACTION = {
    "mcp_context_router": "SELECT_MCP_PACKET",
    "world_state_summarizer": "BUILD_STATE_CARD",
    "llm_prompt_composer": "ASK_LLM_BOUNDED_DRAFT",
    "option_manifold_planner": "ASK_LLM_OPTION_SET",
    "reaction_dynamics_mapper": "ASK_LLM_REACTION_TEXT",
    "effect_script_synthesizer": "SYNTHESIZE_EFFECT_SCRIPT",
    "gate_secret_route_designer": "DESIGN_GATE_THRESHOLDS",
    "validator_repair_critic": "SELECT_REPAIR_TARGET",
    "commit_veto_controller": "COMMIT_OR_VETO",
}

ACTION_TO_LLM_CALL = {
    "ASK_LLM_BOUNDED_DRAFT": "bounded_draft",
    "ASK_LLM_OPTION_SET": "option_set",
    "ASK_LLM_REACTION_TEXT": "reaction_text",
}

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def slug(value: Any) -> str:
    text = re.sub(r"[^a-z0-9_]+", "_", str(value).lower()).strip("_")
    return text[:80] or "storyworld"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def token_estimate(text: str) -> int:
    return max(1, len(text.encode("utf-8")) // 4)


def text_blob(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(text_blob(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(text_blob(v) for v in value)
    return ""


def iter_options(encounter: dict[str, Any]) -> list[dict[str, Any]]:
    options = encounter.get("options")
    return options if isinstance(options, list) else []


def iter_reactions(option: dict[str, Any]) -> list[dict[str, Any]]:
    reactions = option.get("reactions")
    return reactions if isinstance(reactions, list) else []


def iter_effects(reaction: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("after_effects", "effects"):
        effects = reaction.get(key)
        if isinstance(effects, list):
            return effects
    return []


def script_operators(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        op = value.get("operator_type")
        if isinstance(op, str) and op:
            found.append(op)
        for child in value.values():
            found.extend(script_operators(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(script_operators(child))
    return found


def consequence_targets(option: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    for node in [option, *iter_reactions(option)]:
        for key in ("consequence_id", "next_encounter", "target", "encounter_id"):
            value = node.get(key)
            if isinstance(value, str) and value:
                targets.append(value)
                break
    return targets


def effect_operator(effect: dict[str, Any]) -> str:
    for key in ("operator", "op", "operation"):
        value = effect.get(key)
        if isinstance(value, str) and value:
            return value
    to_expr = effect.get("to")
    if isinstance(to_expr, dict):
        op = to_expr.get("operator_type")
        if isinstance(op, str) and op:
            return op
    return "unknown_op"


def storyworld_metrics(path: Path, context_budget_tokens: int, *, suppress_context_overflow: bool = False) -> dict[str, Any]:
    raw_text = path.read_text(encoding="utf-8-sig", errors="replace")
    data = read_json(path)
    encounters = data.get("encounters") if isinstance(data.get("encounters"), list) else []
    encounter_ids = [str(e.get("id") or e.get("encounter_id") or f"encounter_{i:04d}") for i, e in enumerate(encounters)]
    id_set = set(encounter_ids)
    inbound: Counter[str] = Counter()
    outbound: Counter[str] = Counter()
    missing_targets: list[dict[str, str]] = []
    option_count = 0
    reaction_count = 0
    effect_count = 0
    reaction_texts: list[str] = []
    secret_options: list[str] = []
    effect_ops: Counter[str] = Counter()
    script_ops: Counter[str] = Counter()

    for encounter_id, encounter in zip(encounter_ids, encounters):
        blob = text_blob(encounter).lower()
        for op in script_operators(encounter):
            script_ops[op] += 1
        for option in iter_options(encounter):
            option_count += 1
            option_id = str(option.get("id") or f"option_{option_count}")
            if any(token in text_blob([encounter, option]).lower() for token in ("secret", "hidden", "synthesis")):
                secret_options.append(f"{encounter_id}:{option_id}")
            for target in consequence_targets(option):
                outbound[encounter_id] += 1
                inbound[target] += 1
                if target not in id_set:
                    missing_targets.append({"encounter": encounter_id, "option": option_id, "target": target})
            for reaction in iter_reactions(option):
                reaction_count += 1
                reaction_texts.append(text_blob(reaction)[:600])
                for effect in iter_effects(reaction):
                    effect_count += 1
                    effect_ops[effect_operator(effect)] += 1
            if "secret" in blob and not secret_options:
                secret_options.append(f"{encounter_id}:encounter_text")

    terminal_count = sum(1 for encounter in encounters if not iter_options(encounter))
    zero_inbound = [eid for eid in encounter_ids[1:] if inbound[eid] == 0]
    dead_nonterminal = [eid for eid, encounter in zip(encounter_ids, encounters) if iter_options(encounter) and outbound[eid] == 0]
    unknown_reader_ops = sorted(op for op in script_ops if op not in READER_OPERATORS)
    reaction_uniqueness = len(set(reaction_texts)) / max(1, len(reaction_texts))
    whole_context_tokens = token_estimate(raw_text)
    nonterminal_count = max(1, len(encounters) - terminal_count)
    avg_options = option_count / nonterminal_count
    avg_reactions = reaction_count / max(1, option_count)
    avg_effects = effect_count / max(1, reaction_count)
    validator_errors_proxy = len(missing_targets) + len(dead_nonterminal)
    authoring_score_proxy = round(
        max(
            0.0,
            min(
                1.0,
                0.20
                + min(avg_options / 3.0, 1.0) * 0.18
                + min(avg_reactions / 2.5, 1.0) * 0.18
                + min(avg_effects / 4.5, 1.0) * 0.18
                + min(len(effect_ops) / 3.0, 1.0) * 0.12
                + min(len(secret_options) / 1.0, 1.0) * 0.08
                + (1.0 if validator_errors_proxy == 0 else 0.0) * 0.06,
            ),
        ),
        4,
    )
    return {
        "path": str(path),
        "world_id": slug(data.get("storyworld_title") or data.get("title") or path.stem),
        "title": data.get("storyworld_title") or data.get("title") or path.stem,
        "whole_context_tokens": whole_context_tokens,
        "context_budget_tokens": context_budget_tokens,
        "context_overflow": (whole_context_tokens > context_budget_tokens) and not suppress_context_overflow,
        "mcp_packet_mode": bool(suppress_context_overflow),
        "encounters": len(encounters),
        "terminal_count": terminal_count,
        "option_count": option_count,
        "reaction_count": reaction_count,
        "effect_count": effect_count,
        "avg_options_per_nonterminal": round(avg_options, 4),
        "avg_reactions_per_option": round(avg_reactions, 4),
        "avg_effects_per_reaction": round(avg_effects, 4),
        "missing_target_count": len(missing_targets),
        "missing_targets": missing_targets[:20],
        "zero_inbound_count": len(zero_inbound),
        "zero_inbound_sample": zero_inbound[:20],
        "dead_nonterminal_count": len(dead_nonterminal),
        "dead_nonterminal_sample": dead_nonterminal[:20],
        "secret_option_count": len(secret_options),
        "secret_option_sample": secret_options[:20],
        "effect_operator_counts": dict(effect_ops),
        "effect_operator_variety": len(effect_ops),
        "script_operator_counts": dict(script_ops),
        "unknown_reader_operators": unknown_reader_ops,
        "reaction_text_uniqueness": round(reaction_uniqueness, 4),
        "initial_metrics": {
            "authoring_score": authoring_score_proxy,
            "validator_errors": float(validator_errors_proxy),
            "ending_entropy": round(min(2.0, math.log(max(1, terminal_count))) / 2.0, 4),
            "pvalue_alignment": round(min(1.0, len(effect_ops) / 4.0), 4),
        },
    }


def diagnose(metrics: dict[str, Any]) -> tuple[str, str]:
    if metrics["context_overflow"]:
        return "fit_context_budget", "context_overflow"
    if metrics["missing_target_count"] or metrics["dead_nonterminal_count"]:
        return "repair_schema_connectivity", "dangling_consequence"
    if metrics["unknown_reader_operators"]:
        return "repair_reader_semantics", "unsupported_reader_operator"
    if metrics["secret_option_count"] == 0:
        return "repair_secret_route_reachability", "unreachable_secret"
    if metrics["effect_operator_variety"] <= 2:
        return "diversify_effect_scripts", "effect_nudge_monoculture"
    if metrics["reaction_text_uniqueness"] < 0.70:
        return "restore_reaction_contrast", "reaction_collapse"
    if metrics["avg_options_per_nonterminal"] < 3.0:
        return "improve_option_manifold", "option_blandness"
    return "avoid_noop_repair", "no_metric_delta"


def state_for(metrics: dict[str, Any], episode_id: str, objective: str, failure_mode: str, model_tier: str) -> dict[str, Any]:
    return {
        "context_budget_tokens": metrics["context_budget_tokens"],
        "current_failure_mode": failure_mode,
        "episode_id": episode_id,
        "initial_metrics": metrics["initial_metrics"],
        "model_tier": model_tier,
        "objective": objective,
        "world_id": metrics["world_id"],
        "diagnostic_counts": {
            "whole_context_tokens": metrics["whole_context_tokens"],
            "missing_target_count": metrics["missing_target_count"],
            "dead_nonterminal_count": metrics["dead_nonterminal_count"],
            "secret_option_count": metrics["secret_option_count"],
            "effect_operator_variety": metrics["effect_operator_variety"],
            "reaction_text_uniqueness": metrics["reaction_text_uniqueness"],
        },
    }


def tokenize(row: dict[str, Any]) -> list[str]:
    text = " ".join([str(row.get("state", "")), " ".join(str(tool) for tool in row.get("tools", []))])
    return [tok.lower() for tok in TOKEN_RE.findall(text)]


def score_label(model: dict[str, Any], tokens: list[str], label: str) -> float:
    labels = list(model["labels"])
    label_count = float(model["label_counts"].get(label, 0))
    total_rows = float(sum(model["label_counts"].values()))
    alpha = float(model["alpha"])
    score = math.log((label_count + alpha) / (total_rows + alpha * max(1, len(labels))))
    vocab_size = max(1, int(model["vocab_size"]))
    total = float(model["total_tokens"].get(label, 0))
    counts = model["token_counts"].get(label, {})
    denom = total + alpha * vocab_size
    for tok in tokens:
        score += math.log((float(counts.get(tok, 0)) + alpha) / denom)
    return score


def predict(model: dict[str, Any], row: dict[str, Any]) -> tuple[str, dict[str, float]]:
    tools = {str(tool) for tool in row.get("tools", [])}
    labels = [label for label in model["labels"] if label in tools] or list(model["labels"])
    tokens = tokenize(row)
    scores = {label: score_label(model, tokens, label) for label in labels}
    return max(scores.items(), key=lambda item: item[1])[0], scores


def parse_row_state(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("state")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw_state": raw}
    return {}


def native_reasoning_predict(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    state = parse_row_state(row)
    objective = str(state.get("objective") or "")
    failure_mode = str(state.get("current_failure_mode") or "")
    counts = state.get("diagnostic_counts", {}) if isinstance(state.get("diagnostic_counts"), dict) else {}
    initial = state.get("initial_metrics", {}) if isinstance(state.get("initial_metrics"), dict) else {}
    tools = {str(tool) for tool in row.get("tools", [])}

    candidates: list[tuple[int, str, str]] = []
    if failure_mode in FAILURE_TO_ROLE:
        candidates.append((100, FAILURE_TO_ROLE[failure_mode], f"failure:{failure_mode}"))
    if objective in OBJECTIVE_TO_ROLE:
        candidates.append((90, OBJECTIVE_TO_ROLE[objective], f"objective:{objective}"))
    whole_context = float(counts.get("whole_context_tokens") or 0)
    context_budget = float(state.get("context_budget_tokens") or 0)
    if context_budget and whole_context > context_budget and str(state.get("research_variant")) != "post_mcp_packet":
        candidates.append((95, "mcp_context_router", "budget:whole_context_exceeds_budget"))
    if int(counts.get("missing_target_count") or 0) > 0 or int(counts.get("dead_nonterminal_count") or 0) > 0:
        candidates.append((85, "validator_repair_critic", "connectivity:defect"))
    if int(counts.get("secret_option_count") or 0) == 0:
        candidates.append((70, "gate_secret_route_designer", "secret:no_candidate"))
    if int(counts.get("effect_operator_variety") or 0) <= 2 and str(state.get("research_variant")) == "post_mcp_packet":
        candidates.append((80, "effect_script_synthesizer", "effects:low_operator_variety"))
    if float(counts.get("reaction_text_uniqueness") or 1.0) < 0.70:
        candidates.append((75, "reaction_dynamics_mapper", "reactions:low_uniqueness"))
    if float(initial.get("validator_errors") or 0.0) > 0:
        candidates.append((65, "validator_repair_critic", "metrics:validator_errors"))

    candidates = [item for item in candidates if item[1] in tools]
    if not candidates:
        fallback = "commit_veto_controller" if "commit_veto_controller" in tools else "stop"
        return fallback, {"rule": "fallback", "candidates": []}
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    priority, role, reason = candidates[0]
    return role, {
        "rule": reason,
        "priority": priority,
        "candidates": [
            {"priority": p, "role": r, "reason": why}
            for p, r, why in candidates
        ],
    }


def select_planner_prediction(
    *,
    planner: str,
    model: dict[str, Any] | None,
    row: dict[str, Any],
) -> tuple[str, dict[str, Any], str | None, dict[str, float], str, dict[str, Any]]:
    native_role, native_trace = native_reasoning_predict(row)
    model_role: str | None = None
    model_scores: dict[str, float] = {}
    if model is not None:
        model_role, model_scores = predict(model, row)
    if planner == "model":
        if model_role is None:
            raise ValueError("--planner model requires --model")
        return model_role, {"model_scores": model_scores}, model_role, model_scores, native_role, native_trace
    if planner == "hybrid":
        selected = native_role
        return selected, {"native_trace": native_trace, "model_role": model_role, "model_scores": model_scores}, model_role, model_scores, native_role, native_trace
    return native_role, {"native_trace": native_trace}, model_role, model_scores, native_role, native_trace


def artifact_for_role(role: str, metrics: dict[str, Any], objective: str, failure_mode: str) -> dict[str, Any]:
    action = ROLE_TO_ACTION.get(role, "STOP")
    base = {
        "role": role,
        "action": action,
        "llm_call_type": ACTION_TO_LLM_CALL.get(action, "none"),
        "objective": objective,
        "failure_mode": failure_mode,
        "storyworld": metrics["path"],
        "title": metrics["title"],
    }
    if role == "mcp_context_router":
        base["packet_spec"] = {
            "max_input_tokens": min(metrics["context_budget_tokens"], 8192),
            "neighbor_hops": 0 if metrics["context_overflow"] else 1,
            "include_world_card": True,
            "include_target_encounter_only": True,
            "whole_context_tokens": metrics["whole_context_tokens"],
        }
    elif role == "world_state_summarizer":
        base["state_card"] = {
            "counts": {k: metrics[k] for k in ("encounters", "option_count", "reaction_count", "effect_count")},
            "operators": metrics["effect_operator_counts"],
            "secret_options": metrics["secret_option_sample"],
            "connectivity_flags": {
                "missing_target_count": metrics["missing_target_count"],
                "zero_inbound_count": metrics["zero_inbound_count"],
                "dead_nonterminal_count": metrics["dead_nonterminal_count"],
            },
        }
    elif role == "llm_prompt_composer":
        base["prompt_contract"] = {
            "use_runtime_prompt": "runtime_prompts/9B_Trajectory_Control_Plane.md",
            "call_type": "ASK_LLM_BOUNDED_DRAFT",
            "must_include": ["stable_ids", "target_encounter_only", "risk_flags"],
            "must_not_include": ["whole_world_rewrite", "self_certification"],
        }
    elif role == "option_manifold_planner":
        base["option_targets"] = {
            "avg_options_per_nonterminal": metrics["avg_options_per_nonterminal"],
            "target_avg_options": 3.2,
            "request": "Ask for 3-5 options with intended variable deltas for the weakest encounter packet.",
        }
    elif role == "reaction_dynamics_mapper":
        base["reaction_targets"] = {
            "reaction_text_uniqueness": metrics["reaction_text_uniqueness"],
            "request": "Ask for success/mixed/failure reaction contrast under fixed consequence IDs.",
        }
    elif role == "effect_script_synthesizer":
        base["effect_targets"] = {
            "operator_counts": metrics["effect_operator_counts"],
            "request": "Translate narrative deltas into varied deterministic effect scripts; ask LLM only for rationale.",
        }
    elif role == "gate_secret_route_designer":
        base["gate_targets"] = {
            "secret_option_count": metrics["secret_option_count"],
            "secret_option_sample": metrics["secret_option_sample"],
            "request": "Design or rebalance secret/synthesis route predicates and foreshadowing.",
        }
    elif role == "validator_repair_critic":
        base["repair_targets"] = {
            "missing_targets": metrics["missing_targets"],
            "dead_nonterminal_sample": metrics["dead_nonterminal_sample"],
            "unknown_reader_operators": metrics["unknown_reader_operators"],
            "request": "Classify defect before any edit; do not ask LLM to self-certify.",
        }
    elif role == "commit_veto_controller":
        base["commit_veto"] = {
            "recommendation": "veto_noop",
            "reason": "Auto-research loop collected diagnostics only; no patch was applied.",
        }
    return base


def model_tier_for_budget(context_budget_tokens: int) -> str:
    if context_budget_tokens <= 8192:
        return "9B_Q4"
    if context_budget_tokens <= 32768:
        return "27B_Q4"
    return "large_context_remote"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a capped auto-research loop for the storyworld master control planner.")
    parser.add_argument("--storyworld", action="append", default=[], help="Storyworld JSON path. Repeatable.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--out-dir", default="hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_auto_research_local_001")
    parser.add_argument("--iterations", type=int, default=8)
    parser.add_argument("--context-budget-tokens", type=int, default=8192)
    parser.add_argument("--planner", choices=["native", "model", "hybrid"], default="native", help="Planner used for predicted_role. Native is the symbolic teacher policy.")
    parser.add_argument("--no-post-mcp-pass", action="store_true", help="Disable the second diagnostic pass that simulates context already being bounded by MCP.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    model_path = Path(args.model).resolve()
    model = read_json(model_path) if model_path.exists() else None
    if args.planner == "model" and model is None:
        raise SystemExit(f"Model planner requested but model file does not exist: {model_path}")
    storyworlds = [Path(p).resolve() for p in args.storyworld] or [p for p in DEFAULT_STORYWORLDS if p.exists()]
    if not storyworlds:
        raise SystemExit("No storyworlds found for auto-research loop.")

    rows: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    episodes: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    model_tier = model_tier_for_budget(int(args.context_budget_tokens))
    for ix in range(int(args.iterations)):
        storyworld = storyworlds[ix % len(storyworlds)]
        variants = [("raw_context", storyworld_metrics(storyworld, int(args.context_budget_tokens)))]
        if not args.no_post_mcp_pass and variants[0][1]["context_overflow"]:
            variants.append(("post_mcp_packet", storyworld_metrics(storyworld, int(args.context_budget_tokens), suppress_context_overflow=True)))
        for variant_name, metrics in variants:
            global_step = len(rows)
            objective, failure_mode = diagnose(metrics)
            oracle_role = OBJECTIVE_TO_ROLE.get(objective, "validator_repair_critic")
            episode_id = f"auto_research_{global_step:04d}_{variant_name}_{metrics['world_id']}_{slug(objective)}"
            state = state_for(metrics, episode_id, objective, failure_mode, model_tier)
            state["research_variant"] = variant_name
            row = {
                "state": json.dumps(state, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
                "tools": ROLES,
                "action": oracle_role,
                "meta": {
                    "episode_id": episode_id,
                    "step_index": 0,
                    "objective": objective,
                    "failure_mode": failure_mode,
                    "storyworld": str(storyworld),
                    "research_variant": variant_name,
                    "source": "auto_research_loop_oracle",
                },
            }
            predicted_role, prediction_trace, model_predicted_role, model_scores, native_predicted_role, native_trace = select_planner_prediction(
                planner=str(args.planner),
                model=model,
                row=row,
            )
            role_artifact = artifact_for_role(oracle_role, metrics, objective, failure_mode)
            role_artifact["research_variant"] = variant_name
            step_dir = out_dir / "steps" / f"{global_step:04d}_{variant_name}_{metrics['world_id']}_{oracle_role}"
            write_json(step_dir / "metrics.json", metrics)
            write_json(step_dir / "role_artifact.json", role_artifact)
            write_json(step_dir / "planner_state.json", state)
            rows.append(row)
            predictions.append(
                {
                    "episode_id": episode_id,
                    "storyworld": str(storyworld),
                    "research_variant": variant_name,
                    "objective": objective,
                    "failure_mode": failure_mode,
                    "oracle_role": oracle_role,
                    "predicted_role": predicted_role,
                    "planner": args.planner,
                    "native_predicted_role": native_predicted_role,
                    "model_predicted_role": model_predicted_role,
                    "planner_agreed": predicted_role == oracle_role,
                    "prediction_trace": prediction_trace,
                    "native_trace": native_trace,
                    "model_scores": model_scores,
                    "artifact_dir": str(step_dir),
                }
            )
            episodes.append(
                {
                    "episode_id": episode_id,
                    "world_id": metrics["world_id"],
                    "model_tier": model_tier,
                    "context_budget_tokens": int(args.context_budget_tokens),
                    "objective": objective,
                    "initial_metrics": metrics["initial_metrics"],
                    "steps": [
                        {
                            "role_id": oracle_role,
                            "state_ref": f"planner_state_{global_step:04d}",
                            "chosen_action": ROLE_TO_ACTION.get(oracle_role, "STOP"),
                            "llm_call_type": ACTION_TO_LLM_CALL.get(ROLE_TO_ACTION.get(oracle_role, ""), "none"),
                            "context_packet_ref": str(step_dir / "planner_state.json"),
                            "output_ref": str(step_dir / "role_artifact.json"),
                            "verifier_delta_ref": str(step_dir / "metrics.json"),
                        "accepted": predicted_role == oracle_role,
                        "predicted_role": predicted_role,
                        "planner": args.planner,
                        "native_predicted_role": native_predicted_role,
                        "model_predicted_role": model_predicted_role,
                    }
                    ],
                    "final_metrics": metrics["initial_metrics"],
                    "episode_label": {
                        "success": predicted_role == oracle_role,
                        "best_next_role": oracle_role,
                        "failure_class": "planner_mismatch" if predicted_role != oracle_role else "none",
                        "reward": 1.0 if predicted_role == oracle_role else 0.0,
                    },
                }
            )
            events.append(
                {
                    "ts": now_iso(),
                    "event": "iteration",
                    "iteration": ix,
                    "global_step": global_step,
                    "research_variant": variant_name,
                    "storyworld": str(storyworld),
                    "objective": objective,
                    "failure_mode": failure_mode,
                    "oracle_role": oracle_role,
                    "predicted_role": predicted_role,
                    "planner": args.planner,
                    "native_predicted_role": native_predicted_role,
                    "model_predicted_role": model_predicted_role,
                    "planner_agreed": predicted_role == oracle_role,
                }
            )

    agreement = sum(1 for p in predictions if p["planner_agreed"])
    summary = {
        "created_at": now_iso(),
        "model": str(model_path),
        "planner": args.planner,
        "out_dir": str(out_dir),
        "storyworlds": [str(p) for p in storyworlds],
        "iterations": int(args.iterations),
        "context_budget_tokens": int(args.context_budget_tokens),
        "model_tier": model_tier,
        "oracle_rows": len(rows),
        "post_mcp_pass_enabled": not args.no_post_mcp_pass,
        "planner_agreement": agreement,
        "planner_agreement_rate": round(agreement / max(1, len(predictions)), 4),
        "objective_counts": dict(Counter(p["objective"] for p in predictions)),
        "oracle_role_counts": dict(Counter(p["oracle_role"] for p in predictions)),
        "predicted_role_counts": dict(Counter(p["predicted_role"] for p in predictions)),
        "native_role_counts": dict(Counter(p["native_predicted_role"] for p in predictions)),
        "model_role_counts": dict(Counter(str(p["model_predicted_role"]) for p in predictions)),
    }
    write_jsonl(out_dir / "auto_research_rows.jsonl", rows)
    write_jsonl(out_dir / "trajectory_episodes.jsonl", episodes)
    write_jsonl(out_dir / "planner_predictions.jsonl", predictions)
    write_jsonl(out_dir / "events.jsonl", events)
    write_json(out_dir / "run_summary.json", summary)
    readme = [
        "# Master Planner Auto-Research Loop",
        "",
        "This run collects real storyworld diagnostic states for the master control planner.",
        "",
        f"- Iterations: `{summary['iterations']}`",
        f"- Context budget: `{summary['context_budget_tokens']}`",
        f"- Model tier: `{summary['model_tier']}`",
        f"- Planner: `{summary['planner']}`",
        f"- Planner agreement: `{summary['planner_agreement']}/{summary['oracle_rows']} = {summary['planner_agreement_rate']}`",
        "",
        "Files:",
        "",
        "- `auto_research_rows.jsonl`: trainable `state/tools -> oracle_role` rows.",
        "- `trajectory_episodes.jsonl`: one-step episode rows compatible with the planner episode schema.",
        "- `planner_predictions.jsonl`: selected planner proposal versus deterministic oracle, with native/model traces.",
        "- `steps/*`: per-iteration metrics, planner state, and role artifact.",
        "",
        "This loop intentionally does not patch storyworld files. It collects supervision for the master planner.",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(readme), encoding="utf-8", newline="\n")
    print(str(out_dir))
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
