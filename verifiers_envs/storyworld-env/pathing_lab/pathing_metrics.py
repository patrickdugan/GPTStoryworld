#!/usr/bin/env python3
"""Experimental pathing metrics for gated multi-path narrative worlds."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


def _is_true_script(script: Any) -> bool:
    if script is True or script is None:
        return True
    if isinstance(script, dict):
        if script.get("pointer_type") == "Boolean Constant":
            return bool(script.get("value", False))
    return False


def _collect_props(node: Any, out: Set[str]) -> None:
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Pointer":
            keyring = node.get("keyring") or []
            if isinstance(keyring, list) and keyring:
                out.add(str(keyring[0]))
        for v in node.values():
            _collect_props(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_props(v, out)


def _eval_script(script: Any, state: Dict[Tuple[str, str], float]) -> Any:
    if script is True:
        return True
    if script is False:
        return False
    if isinstance(script, (int, float, bool)):
        return script
    if not isinstance(script, dict):
        return script

    pt = script.get("pointer_type")
    ot = script.get("operator_type")

    if pt == "Boolean Constant":
        return bool(script.get("value", False))
    if pt == "Bounded Number Constant":
        return float(script.get("value", 0.0))
    if pt == "Bounded Number Pointer":
        char = str(script.get("character", ""))
        keyring = script.get("keyring") or []
        prop = str(keyring[0]) if keyring else ""
        coeff = float(script.get("coefficient", 1.0))
        return state.get((char, prop), 0.0) * coeff

    if ot == "Arithmetic Comparator":
        subtype = script.get("operator_subtype", "")
        left = _eval_script(script.get("operands", [0, 0])[0], state)
        right = _eval_script(script.get("operands", [0, 0])[1], state)
        if subtype in ("Greater Than or Equal To", "GTE"):
            return left >= right
        if subtype in ("Less Than or Equal To", "LTE"):
            return left <= right
        if subtype in ("Greater Than", "GT"):
            return left > right
        if subtype in ("Less Than", "LT"):
            return left < right
        if subtype in ("Equal To", "EQ"):
            return left == right
        if subtype in ("Not Equal To", "NEQ"):
            return left != right
        return False
    if ot == "And":
        return all(bool(_eval_script(x, state)) for x in script.get("operands", []))
    if ot == "Or":
        return any(bool(_eval_script(x, state)) for x in script.get("operands", []))
    if ot == "Addition":
        return sum(float(_eval_script(x, state) or 0.0) for x in script.get("operands", []))
    if ot == "Multiplication":
        r = 1.0
        for x in script.get("operands", []):
            r *= float(_eval_script(x, state) or 0.0)
        return r
    if ot == "Arithmetic Mean":
        vals = [float(_eval_script(x, state) or 0.0) for x in script.get("operands", [])]
        return sum(vals) / len(vals) if vals else 0.0
    if ot == "Absolute Value":
        ops = script.get("operands", [0.0])
        return abs(float(_eval_script(ops[0], state) or 0.0))
    if ot == "Nudge":
        ops = script.get("operands", [0.0, 0.0])
        cur = float(_eval_script(ops[0], state) or 0.0)
        delta = float(_eval_script(ops[1], state) or 0.0)
        return max(-1.0, min(1.0, cur + delta))
    return script.get("value", 0.0)


def _choose_reaction(option: Dict[str, Any], state: Dict[Tuple[str, str], float]) -> Optional[Dict[str, Any]]:
    reactions = option.get("reactions", []) or []
    best = None
    best_score = -1e9
    for rxn in reactions:
        score = _eval_script(rxn.get("desirability_script", 0.0), state)
        if isinstance(score, bool):
            score = 1.0 if score else 0.0
        score = float(score or 0.0)
        if score > best_score:
            best = rxn
            best_score = score
    return best


def _apply_effects(reaction: Dict[str, Any], state: Dict[Tuple[str, str], float], deltas: Dict[str, float]) -> None:
    for eff in reaction.get("after_effects", []) or []:
        if eff.get("effect_type") != "Bounded Number Effect":
            continue
        set_obj = eff.get("Set", {})
        char = str(set_obj.get("character", ""))
        keyring = set_obj.get("keyring") or []
        if not keyring:
            continue
        prop = str(keyring[0])
        old = state.get((char, prop), 0.0)
        new = _eval_script(eff.get("to", old), state)
        try:
            new_val = float(new)
        except Exception:
            new_val = float(old)
        new_val = max(-1.0, min(1.0, new_val))
        state[(char, prop)] = new_val
        deltas[prop] = deltas.get(prop, 0.0) + (new_val - old)


def _is_terminal(encounter: Dict[str, Any], encounter_ids: Set[str], consequence_ids: Set[str]) -> bool:
    eid = str(encounter.get("id", ""))
    if not eid:
        return True
    if encounter.get("is_ending") is True or eid.startswith("page_end_") or eid.startswith("page_secret_"):
        return True
    if not (encounter.get("options", []) or []):
        return True
    # Do not infer terminality from "unreferenced by others" because entry pages
    # (e.g. page_0000) are often intentionally unreferenced.
    return False


def _path_signature(path: List[str]) -> str:
    if not path:
        return ""
    if len(path) <= 8:
        return "->".join(path)
    return "->".join(path[:4] + ["..."] + path[-3:])


def simulate_pathing(data: Dict[str, Any], rollouts: int = 120, seed: int = 42, max_steps: int = 200) -> Dict[str, Any]:
    rng = random.Random(seed)
    encounters = data.get("encounters", []) or []
    enc_by_id = {e.get("id"): e for e in encounters if e.get("id")}
    encounter_ids = set(enc_by_id.keys())
    consequence_ids: Set[str] = set()
    for enc in encounters:
        for opt in enc.get("options", []) or []:
            for rxn in opt.get("reactions", []) or []:
                cid = rxn.get("consequence_id")
                if isinstance(cid, str) and cid:
                    consequence_ids.add(cid)

    start_id = "page_0000" if "page_0000" in enc_by_id else (encounters[0].get("id") if encounters else "")

    authored_props = [p.get("property_name") for p in data.get("authored_properties", []) if p.get("property_name")]
    chars = [c.get("id") for c in data.get("characters", []) if c.get("id")]
    base_state = {}
    for c in chars:
        for p in authored_props:
            if p.startswith("p"):
                continue
            base_state[(str(c), str(p))] = 0.0

    gated_total = 0
    for enc in encounters:
        for opt in enc.get("options", []) or []:
            if not _is_true_script(opt.get("visibility_script", True)):
                gated_total += 1

    gate_hits = 0
    terminal_hits = 0
    reversal_hits = 0
    unique_gate_paths: Set[str] = set()
    unique_terminal_paths: Set[str] = set()
    reached_gate_props: Set[str] = set()

    for _ in range(max(1, rollouts)):
        state = dict(base_state)
        deltas: Dict[str, float] = {}
        current_id = start_id
        path: List[str] = []
        saw_gate = False
        reversal_found = False
        last_dir: Dict[str, int] = {}

        for _step in range(max_steps):
            enc = enc_by_id.get(current_id)
            if not enc:
                break
            path.append(current_id)

            if _is_terminal(enc, encounter_ids, consequence_ids):
                terminal_hits += 1
                unique_terminal_paths.add(_path_signature(path))
                if reversal_found:
                    reversal_hits += 1
                break

            options = []
            for opt in enc.get("options", []) or []:
                vis_ok = bool(_eval_script(opt.get("visibility_script", True), state))
                perf_ok = bool(_eval_script(opt.get("performability_script", True), state))
                if vis_ok and perf_ok:
                    options.append(opt)
                if not _is_true_script(opt.get("visibility_script", True)) and vis_ok:
                    saw_gate = True
                    props = set()
                    _collect_props(opt.get("visibility_script"), props)
                    reached_gate_props.update(props)

            if not options:
                break

            chosen = rng.choice(options)
            rxn = _choose_reaction(chosen, state)
            if not rxn:
                break
            _apply_effects(rxn, state, deltas)

            # Reversal detection: sign flip on cumulative property deltas with sufficient magnitude.
            for prop, delta_sum in deltas.items():
                if abs(delta_sum) < 0.08:
                    continue
                d = 1 if delta_sum > 0 else -1
                prev = last_dir.get(prop)
                if prev is not None and prev != d:
                    reversal_found = True
                last_dir[prop] = d

            next_id = rxn.get("consequence_id", "")
            if not isinstance(next_id, str) or not next_id or next_id == "wild":
                break
            current_id = next_id

        if saw_gate:
            gate_hits += 1
            unique_gate_paths.add(_path_signature(path))

    gate_reach_rate = gate_hits / max(1, rollouts)
    terminal_path_diversity = len(unique_terminal_paths) / max(1, min(rollouts, 50))
    gate_var_diversity = len(reached_gate_props) / max(1, len([p for p in authored_props if not str(p).startswith("p")]))
    darth_vader_reversal_factor = reversal_hits / max(1, terminal_hits)

    # Experimental blend emphasizing path diversity + strategic reversals.
    pathing_composite = (
        0.26 * min(1.0, gate_reach_rate / 0.2)
        + 0.18 * min(1.0, len(unique_gate_paths) / 8.0)
        + 0.16 * min(1.0, gate_var_diversity / 0.6)
        + 0.20 * min(1.0, terminal_path_diversity / 0.5)
        + 0.20 * min(1.0, darth_vader_reversal_factor / 0.35)
    )

    return {
        "rollouts": rollouts,
        "seed": seed,
        "gate_option_count": gated_total,
        "gate_reach_rate": round(gate_reach_rate, 4),
        "unique_gate_paths": len(unique_gate_paths),
        "gate_var_diversity": round(gate_var_diversity, 4),
        "terminal_path_diversity": round(terminal_path_diversity, 4),
        "darth_vader_reversal_factor": round(darth_vader_reversal_factor, 4),
        "pathing_composite": round(pathing_composite, 4),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prototype multi-pathing metrics")
    p.add_argument("--storyworld", required=True, help="Storyworld JSON file")
    p.add_argument("--rollouts", type=int, default=120)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="", help="Optional output JSON")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.storyworld).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    out = simulate_pathing(data, rollouts=args.rollouts, seed=args.seed)
    out["storyworld"] = str(path)
    text = json.dumps(out, indent=2, ensure_ascii=True)
    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8", newline="\n")
        print(str(out_path))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
