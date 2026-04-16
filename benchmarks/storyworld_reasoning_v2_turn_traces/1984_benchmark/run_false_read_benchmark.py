#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[3]
WORLD_DIR = REPO_ROOT / "storyworlds" / "generated" / "1984_benchmark"


def eval_script(script: Any, state: Dict[Tuple[str, ...], float]) -> Any:
    if script is True:
        return True
    if script is False:
        return False
    if isinstance(script, (int, float)):
        return script
    if not isinstance(script, dict):
        return script

    pointer_type = script.get("pointer_type")
    operator_type = script.get("operator_type")

    if pointer_type == "Bounded Number Constant":
        return float(script.get("value", 0.0))
    if pointer_type == "Bounded Number Pointer":
        character = str(script.get("character", ""))
        keyring = tuple(str(x) for x in (script.get("keyring") or []))
        coefficient = float(script.get("coefficient", 1.0))
        return state.get((character, *keyring), 0.0) * coefficient
    if pointer_type == "String Constant":
        return str(script.get("value", ""))

    if operator_type == "Arithmetic Comparator":
        left = eval_script(script["operands"][0], state)
        right = eval_script(script["operands"][1], state)
        subtype = script.get("operator_subtype")
        ops = {
            "Greater Than or Equal To": lambda a, b: a >= b,
            "Less Than or Equal To": lambda a, b: a <= b,
            "Greater Than": lambda a, b: a > b,
            "Less Than": lambda a, b: a < b,
            "Equal To": lambda a, b: a == b,
            "Not Equal To": lambda a, b: a != b,
        }
        return ops[subtype](left, right)
    if operator_type == "And":
        return all(eval_script(op, state) for op in script.get("operands", []))
    if operator_type == "Or":
        return any(eval_script(op, state) for op in script.get("operands", []))
    if operator_type == "Addition":
        return sum(float(eval_script(op, state)) for op in script.get("operands", []))
    if operator_type == "Multiplication":
        result = 1.0
        for operand in script.get("operands", []):
            result *= float(eval_script(operand, state))
        return result
    if operator_type == "Absolute Value":
        return abs(float(eval_script(script.get("operands", [0])[0], state)))
    if operator_type == "Nudge":
        current = float(eval_script(script["operands"][0], state))
        delta = float(eval_script(script["operands"][1], state))
        return max(-1.0, min(1.0, current + delta))
    return 0.0


def apply_effects(reaction: Dict[str, Any], state: Dict[Tuple[str, ...], float]) -> Dict[Tuple[str, ...], float]:
    next_state = dict(state)
    for effect in reaction.get("after_effects", []) or []:
        if effect.get("effect_type") != "Bounded Number Effect":
            continue
        target = effect.get("Set", {})
        character = str(target.get("character", ""))
        keyring = tuple(str(x) for x in (target.get("keyring") or []))
        next_state[(character, *keyring)] = max(-1.0, min(1.0, float(eval_script(effect.get("to"), next_state))))
    return next_state


def canonical_state() -> Dict[Tuple[str, ...], float]:
    state: Dict[Tuple[str, ...], float] = {}
    winston = "char_winston"
    state[(winston, "Counter_Signal")] = 0.55
    state[(winston, "Receiver_Assembly")] = 0.18
    state[(winston, "Defiance")] = 0.28
    state[(winston, "Private_Self")] = 0.48
    state[(winston, "Party_Orthodoxy")] = 0.12
    state[(winston, "Exposure")] = 0.36
    state[(winston, "Trust")] = 0.10
    state[(winston, "Submission")] = 0.08
    state[(winston, "pTrust")] = 0.35
    state[(winston, "pSuspicion")] = 0.03
    state[(winston, "pPrivate_Self")] = 0.48
    state[(winston, "pTrust", "char_julia")] = 0.08
    state[(winston, "pSuspicion", "char_obrien")] = 0.03
    state[(winston, "pSubmission", "char_obrien", "char_winston")] = 0.5
    state[(winston, "pSuspicion", "char_obrien", "char_julia")] = 0.03
    return state


def with_overrides(base: Dict[Tuple[str, ...], float], **overrides: float) -> Dict[Tuple[str, ...], float]:
    state = dict(base)
    for flat_key, value in overrides.items():
        state[tuple(flat_key.split("|"))] = value
    return state


def benchmark_states() -> Dict[str, Dict[Tuple[str, ...], float]]:
    base = canonical_state()

    return {
        "balanced_trap": base,
        "already_suspicious": with_overrides(
            base,
            **{
                "char_winston|pSuspicion": 0.06,
                "char_winston|pSuspicion|char_obrien": 0.05,
                "char_winston|Exposure": 0.42,
            }
        ),
        "julia_compromised": with_overrides(
            base,
            **{
                "char_winston|pTrust|char_julia": -0.02,
                "char_winston|Trust": 0.06,
                "char_winston|Counter_Signal": 0.35,
                "char_winston|Receiver_Assembly": 0.08,
            }
        ),
        "near_conversion": with_overrides(
            base,
            **{
                "char_winston|Submission": 0.16,
                "char_winston|Party_Orthodoxy": 0.18,
                "char_winston|Counter_Signal": 0.42,
                "char_winston|Receiver_Assembly": 0.1,
                "char_winston|pSubmission|char_obrien|char_winston": 0.7,
            }
        ),
        "paperweight_memory": with_overrides(
            base,
            **{
                "char_winston|Private_Self": 0.62,
                "char_winston|Defiance": 0.36,
                "char_winston|Counter_Signal": 0.4,
                "char_winston|Receiver_Assembly": 0.18,
                "char_winston|pPrivate_Self": 0.56,
            }
        ),
        "counter_signal_window": with_overrides(
            base,
            **{
                "char_winston|Counter_Signal": 0.95,
                "char_winston|Receiver_Assembly": 0.21,
                "char_winston|Defiance": 0.42,
                "char_winston|Private_Self": 0.62,
                "char_winston|Trust": 0.14,
                "char_winston|Exposure": 0.44,
                "char_winston|pPrivate_Self": 0.56,
                "char_winston|pSubmission|char_obrien|char_winston": 0.62,
            }
        ),
    }


def sweep_states() -> List[Tuple[str, Dict[Tuple[str, ...], float]]]:
    base = canonical_state()
    dimensions = [
        ("char_winston|Counter_Signal", [0.35, 0.75]),
        ("char_winston|Receiver_Assembly", [0.12, 0.21]),
        ("char_winston|pSuspicion", [0.03, 0.06]),
        ("char_winston|pSuspicion|char_obrien", [0.02, 0.05]),
        ("char_winston|pPrivate_Self", [0.35, 0.55]),
        ("char_winston|Private_Self", [0.4, 0.6]),
        ("char_winston|Submission", [0.08, 0.16]),
        ("char_winston|Party_Orthodoxy", [0.1, 0.18]),
        ("char_winston|Exposure", [0.32, 0.46]),
        ("char_winston|pTrust|char_julia", [-0.02, 0.08]),
    ]
    states: List[Tuple[str, Dict[Tuple[str, ...], float]]] = []
    for idx, values in enumerate(product(*(vals for _, vals in dimensions)), start=1):
        overrides = {flat_key: value for (flat_key, _vals), value in zip(dimensions, values)}
        state = with_overrides(base, **overrides)
        states.append((f"sweep_{idx:03d}", state))
    return states


def ending_scores(world: Dict[str, Any], state: Dict[Tuple[str, ...], float]) -> Dict[str, Dict[str, Any]]:
    results: Dict[str, Dict[str, Any]] = {}
    for encounter in world.get("encounters", []):
        enc_id = encounter.get("id", "")
        if enc_id != "page_end_0205" and not str(enc_id).startswith("page_secret_"):
            continue
        acceptability = bool(eval_script(encounter.get("acceptability_script", True), state))
        desirability = float(eval_script(encounter.get("desirability_script", 0.0), state))
        results[enc_id] = {
            "acceptability": acceptability,
            "desirability": round(desirability, 4),
        }
    return results


def best_secret_result(scores: Dict[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    secret_items = [(enc_id, payload) for enc_id, payload in scores.items() if enc_id.startswith("page_secret_")]
    if not secret_items:
        raise ValueError("benchmark requires at least one secret ending")
    return max(
        secret_items,
        key=lambda item: (1 if item[1]["acceptability"] else 0, float(item[1]["desirability"])),
    )


def flatten_state(state: Dict[Tuple[str, ...], float]) -> Dict[str, float]:
    return {"|".join(key): round(value, 4) for key, value in sorted(state.items())}


def option_is_available(option: Dict[str, Any], state: Dict[Tuple[str, ...], float]) -> bool:
    return bool(eval_script(option.get("visibility_script", True), state)) and bool(
        eval_script(option.get("performability_script", True), state)
    )


def combo_preview(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "false_reaction_id": row["false_reaction_id"],
        "followup_reaction_id": row["followup_reaction_id"],
        "best_secret_id": row["best_secret_id"],
        "best_secret": row["best_secret"],
        "page_end_0205": row["page_end_0205"],
        "secret_margin_vs_pupil": row["secret_margin_vs_pupil"],
    }


def summarize_path_combo(group: Dict[str, Any]) -> Dict[str, Any]:
    combo_rows = group["combo_rows"]
    combo_count = len(combo_rows)
    if combo_count == 0:
        raise ValueError("cannot summarize an empty combo group")

    best_combo = max(combo_rows, key=lambda row: row["secret_margin_vs_pupil"])
    worst_combo = min(combo_rows, key=lambda row: row["secret_margin_vs_pupil"])

    secret_scores = [row["best_secret"]["desirability"] for row in combo_rows]
    pupil_scores = [row["page_end_0205"]["desirability"] for row in combo_rows]
    margins = [row["secret_margin_vs_pupil"] for row in combo_rows]
    secret_accept_count = sum(1 for row in combo_rows if row["best_secret"]["acceptability"])
    pupil_accept_count = sum(1 for row in combo_rows if row["page_end_0205"]["acceptability"])
    potential_combo_count = max(1, int(group["potential_combo_count"]))
    dominant_secret_id = Counter(row["best_secret_id"] for row in combo_rows).most_common(1)[0][0]

    return {
        "false_option_id": group["false_option_id"],
        "false_option_text": group["false_option_text"],
        "followup_option_id": group["followup_option_id"],
        "followup_option_text": group["followup_option_text"],
        "reaction_combo_count": combo_count,
        "potential_combo_count": potential_combo_count,
        "availability_rate": round(combo_count / potential_combo_count, 4),
        "best_secret_id": dominant_secret_id,
        "best_secret": {
            "accept_count": secret_accept_count,
            "accept_rate": round(secret_accept_count / combo_count, 4),
            "avg_desirability": round(sum(secret_scores) / combo_count, 4),
            "min_desirability": round(min(secret_scores), 4),
            "max_desirability": round(max(secret_scores), 4),
        },
        "page_end_0205": {
            "accept_count": pupil_accept_count,
            "accept_rate": round(pupil_accept_count / combo_count, 4),
            "avg_desirability": round(sum(pupil_scores) / combo_count, 4),
            "min_desirability": round(min(pupil_scores), 4),
            "max_desirability": round(max(pupil_scores), 4),
        },
        "avg_secret_margin_vs_pupil": round(sum(margins) / combo_count, 4),
        "min_secret_margin_vs_pupil": round(min(margins), 4),
        "max_secret_margin_vs_pupil": round(max(margins), 4),
        "best_combo": combo_preview(best_combo),
        "worst_combo": combo_preview(worst_combo),
    }


def path_rank_key(item: Dict[str, Any]) -> Tuple[float, float, float, float, float, float]:
    return (
        float(item["best_secret"]["accept_rate"]),
        float(item["availability_rate"]),
        float(item["avg_secret_margin_vs_pupil"]),
        float(item["min_secret_margin_vs_pupil"]),
        -float(item["page_end_0205"]["accept_rate"]),
        float(item["best_secret"]["avg_desirability"]),
    )


def score_spycraft_paths(
    false_read: Dict[str, Any],
    followup: Dict[str, Any] | None,
    world: Dict[str, Any],
    base_state: Dict[Tuple[str, ...], float],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    baseline = ending_scores(world, base_state)
    grouped: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for false_option in false_read.get("options", []) or []:
        if not option_is_available(false_option, base_state):
            continue

        false_reactions = false_option.get("reactions", []) or []
        if not false_reactions:
            continue

        if followup is None:
            group_key = (str(false_option.get("id", "")), "__no_followup__")
            grouped[group_key] = {
                "false_option_id": false_option.get("id"),
                "false_option_text": false_option.get("text_script", {}).get("value", ""),
                "followup_option_id": None,
                "followup_option_text": "",
                "potential_combo_count": len(false_reactions),
                "combo_rows": [],
            }
            for false_reaction in false_reactions:
                post_false_state = apply_effects(false_reaction, base_state)
                scores = ending_scores(world, post_false_state)
                best_secret_id, best_secret = best_secret_result(scores)
                grouped[group_key]["combo_rows"].append(
                    {
                        "false_reaction_id": false_reaction.get("id"),
                        "followup_reaction_id": None,
                        "best_secret_id": best_secret_id,
                        "best_secret": best_secret,
                        "page_end_0205": scores["page_end_0205"],
                        "secret_margin_vs_pupil": round(
                            best_secret["desirability"] - scores["page_end_0205"]["desirability"],
                            4,
                        ),
                    }
                )
            continue

        for followup_option in followup.get("options", []) or []:
            followup_reactions = followup_option.get("reactions", []) or []
            if not followup_reactions:
                continue

            group_key = (str(false_option.get("id", "")), str(followup_option.get("id", "")))
            group = grouped.setdefault(
                group_key,
                {
                    "false_option_id": false_option.get("id"),
                    "false_option_text": false_option.get("text_script", {}).get("value", ""),
                    "followup_option_id": followup_option.get("id"),
                    "followup_option_text": followup_option.get("text_script", {}).get("value", ""),
                    "potential_combo_count": len(false_reactions) * len(followup_reactions),
                    "combo_rows": [],
                },
            )

            for false_reaction in false_reactions:
                post_false_state = apply_effects(false_reaction, base_state)
                if not option_is_available(followup_option, post_false_state):
                    continue

                for followup_reaction in followup_reactions:
                    post_followup_state = apply_effects(followup_reaction, post_false_state)
                    scores = ending_scores(world, post_followup_state)
                    best_secret_id, best_secret = best_secret_result(scores)
                    group["combo_rows"].append(
                        {
                            "false_reaction_id": false_reaction.get("id"),
                            "followup_reaction_id": followup_reaction.get("id"),
                            "best_secret_id": best_secret_id,
                            "best_secret": best_secret,
                            "page_end_0205": scores["page_end_0205"],
                            "secret_margin_vs_pupil": round(
                                best_secret["desirability"] - scores["page_end_0205"]["desirability"],
                                4,
                            ),
                        }
                    )

    path_results = [summarize_path_combo(group) for group in grouped.values() if group["combo_rows"]]
    path_results.sort(key=path_rank_key, reverse=True)
    return baseline, path_results


def summarize_path_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    aggregate: Dict[Tuple[str, str | None], Dict[str, Any]] = {}
    for row in rows:
        agg = aggregate.setdefault(
            (row["false_option_id"], row["followup_option_id"]),
            {
                "false_option_id": row["false_option_id"],
                "false_option_text": row["false_option_text"],
                "followup_option_id": row["followup_option_id"],
                "followup_option_text": row["followup_option_text"],
                "states_tested": 0,
                "state_secret_presence_count": 0,
                "state_secret_robust_count": 0,
                "state_wins": 0,
                "availability_sum": 0.0,
                "margin_sum": 0.0,
                "min_availability_rate": None,
                "min_secret_margin_vs_pupil": None,
                "max_secret_margin_vs_pupil": None,
                "min_secret_accept_rate": None,
            },
        )
        agg["states_tested"] += 1
        agg["availability_sum"] += row["availability_rate"]
        agg["margin_sum"] += row["avg_secret_margin_vs_pupil"]
        if row["best_secret"]["accept_rate"] > 0:
            agg["state_secret_presence_count"] += 1
        if row["best_secret"]["accept_rate"] >= 1.0:
            agg["state_secret_robust_count"] += 1
        if row.get("won_state"):
            agg["state_wins"] += 1
        margin = row["avg_secret_margin_vs_pupil"]
        availability = row["availability_rate"]
        secret_accept_rate = row["best_secret"]["accept_rate"]
        if agg["min_availability_rate"] is None or availability < agg["min_availability_rate"]:
            agg["min_availability_rate"] = availability
        if agg["min_secret_margin_vs_pupil"] is None or margin < agg["min_secret_margin_vs_pupil"]:
            agg["min_secret_margin_vs_pupil"] = margin
        if agg["max_secret_margin_vs_pupil"] is None or margin > agg["max_secret_margin_vs_pupil"]:
            agg["max_secret_margin_vs_pupil"] = margin
        if agg["min_secret_accept_rate"] is None or secret_accept_rate < agg["min_secret_accept_rate"]:
            agg["min_secret_accept_rate"] = secret_accept_rate

    aggregate_rows = []
    for stats in aggregate.values():
        aggregate_rows.append(
            {
                "false_option_id": stats["false_option_id"],
                "false_option_text": stats["false_option_text"],
                "followup_option_id": stats["followup_option_id"],
                "followup_option_text": stats["followup_option_text"],
                "states_tested": stats["states_tested"],
                "state_secret_presence_count": stats["state_secret_presence_count"],
                "state_secret_robust_count": stats["state_secret_robust_count"],
                "state_wins": stats["state_wins"],
                "avg_availability_rate": round(stats["availability_sum"] / max(1, stats["states_tested"]), 4),
                "min_availability_rate": round(float(stats["min_availability_rate"]), 4),
                "avg_secret_margin_vs_pupil": round(stats["margin_sum"] / max(1, stats["states_tested"]), 4),
                "min_secret_margin_vs_pupil": round(float(stats["min_secret_margin_vs_pupil"]), 4),
                "max_secret_margin_vs_pupil": round(float(stats["max_secret_margin_vs_pupil"]), 4),
                "min_secret_accept_rate": round(float(stats["min_secret_accept_rate"]), 4),
            }
        )
    aggregate_rows.sort(
        key=lambda item: (
            item["state_wins"],
            item["state_secret_robust_count"],
            item["min_secret_accept_rate"],
            item["avg_secret_margin_vs_pupil"],
            item["min_secret_margin_vs_pupil"],
            item["avg_availability_rate"],
        ),
        reverse=True,
    )
    return aggregate_rows


def run_sweep_benchmark(false_read: Dict[str, Any], followup: Dict[str, Any] | None, world: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    frontier: List[Dict[str, Any]] = []
    for state_name, base_state in sweep_states():
        _baseline, path_results = score_spycraft_paths(false_read, followup, world, base_state)
        if not path_results:
            continue
        best_path = path_results[0]
        for path_result in path_results:
            row = dict(path_result)
            row["state_name"] = state_name
            row["state"] = flatten_state(base_state)
            row["won_state"] = (
                path_result["false_option_id"] == best_path["false_option_id"]
                and path_result["followup_option_id"] == best_path["followup_option_id"]
            )
            rows.append(row)
        frontier.append(
            {
                "state_name": state_name,
                "state": flatten_state(base_state),
                "best_false_option_id": best_path["false_option_id"],
                "best_followup_option_id": best_path["followup_option_id"],
                "best_avg_secret_margin_vs_pupil": best_path["avg_secret_margin_vs_pupil"],
                "best_secret_accept_rate": best_path["best_secret"]["accept_rate"],
                "best_secret_id": best_path["best_secret_id"],
                "best_availability_rate": best_path["availability_rate"],
            }
        )

    aggregate_rows = summarize_path_rows(rows)
    best_aggregate = aggregate_rows[0] if aggregate_rows else None
    failure_examples = [
        row
        for row in rows
        if row["false_option_id"] == "opt_obrien_false_read" and row["best_secret"]["accept_rate"] < 1.0
    ][:5]
    frontier.sort(key=lambda item: item["best_avg_secret_margin_vs_pupil"])
    return {
        "state_count": len(frontier),
        "aggregate_paths": aggregate_rows,
        "best_aggregate_path": best_aggregate,
        "robustness_frontier": frontier[:5],
        "false_read_secret_failures": failure_examples,
    }


def benchmark_world(label: str, world: Dict[str, Any]) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "world_label": label,
    }

    encounter_by_id = {enc.get("id"): enc for enc in world.get("encounters", [])}
    false_read = encounter_by_id.get("page_scene_obrien_false_read")
    if false_read is None:
        results["false_read_scene_present"] = False
        return results

    followup = encounter_by_id.get("page_scene_obrien_followup")
    results["false_read_scene_present"] = True
    results["followup_scene_present"] = followup is not None
    state_results: Dict[str, Any] = {}
    for state_name, base_state in benchmark_states().items():
        baseline, path_results = score_spycraft_paths(false_read, followup, world, base_state)
        state_results[state_name] = {
            "at_gate_baseline": baseline,
            "spycraft_paths": path_results,
            "best_spycraft_path": path_results[0] if path_results else None,
        }

    named_rows: List[Dict[str, Any]] = []
    for entry in state_results.values():
        best_path = entry["best_spycraft_path"]
        for path_result in entry["spycraft_paths"]:
            row = dict(path_result)
            row["won_state"] = (
                best_path is not None
                and path_result["false_option_id"] == best_path["false_option_id"]
                and path_result["followup_option_id"] == best_path["followup_option_id"]
            )
            named_rows.append(row)
    aggregate_rows = summarize_path_rows(named_rows)
    results["state_benchmarks"] = state_results
    results["aggregate_paths"] = aggregate_rows
    results["best_aggregate_path"] = aggregate_rows[0] if aggregate_rows else None
    results["sweep_benchmark"] = run_sweep_benchmark(false_read, followup, world)
    return results


def main() -> int:
    worlds = {
        "one_shot": json.loads((WORLD_DIR / "1984_one_shot.json").read_text(encoding="utf-8")),
        "n_shot": json.loads((WORLD_DIR / "1984_n_shot.json").read_text(encoding="utf-8")),
    }
    output = {label: benchmark_world(label, world) for label, world in worlds.items()}
    out_path = Path(__file__).resolve().with_name("false_read_benchmark.json")
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
