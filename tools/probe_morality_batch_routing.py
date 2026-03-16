#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple


def eval_script(script: Any, state: Dict[Tuple[str, str], float]) -> Any:
    if script is True:
        return True
    if script is False:
        return False
    if isinstance(script, (int, float)):
        return script
    if not isinstance(script, dict):
        return script
    pt = script.get("pointer_type")
    ot = script.get("operator_type")
    if pt == "Bounded Number Constant":
        return script.get("value", 0.0)
    if pt == "Bounded Number Pointer":
        ch = script.get("character")
        key = (script.get("keyring") or [""])[0]
        coef = float(script.get("coefficient", 1.0) or 1.0)
        return float(state.get((str(ch), str(key)), 0.0)) * coef
    if pt == "String Constant":
        return script.get("value", "")
    if ot == "Arithmetic Comparator":
        ops = script.get("operands") or [None, None]
        a = eval_script(ops[0], state)
        b = eval_script(ops[1], state)
        sub = script.get("operator_subtype")
        lut = {
            "Greater Than or Equal To": a >= b,
            "Less Than or Equal To": a <= b,
            "Greater Than": a > b,
            "Less Than": a < b,
            "Equal To": a == b,
            "Not Equal To": a != b,
            "GTE": a >= b,
            "LTE": a <= b,
            "GT": a > b,
            "LT": a < b,
            "EQ": a == b,
            "NEQ": a != b,
        }
        return lut.get(sub, False)
    if ot == "And":
        return all(eval_script(op, state) for op in (script.get("operands") or []))
    if ot == "Or":
        return any(eval_script(op, state) for op in (script.get("operands") or []))
    if ot == "Addition":
        return sum(float(eval_script(op, state) or 0.0) for op in (script.get("operands") or []))
    if ot == "Multiplication":
        out = 1.0
        for op in (script.get("operands") or []):
            out *= float(eval_script(op, state) or 0.0)
        return out
    if ot == "Absolute Value":
        ops = script.get("operands") or [0.0]
        return abs(float(eval_script(ops[0], state) or 0.0))
    if ot == "Nudge":
        ops = script.get("operands") or [0.0, 0.0]
        cur = float(eval_script(ops[0], state) or 0.0)
        delta = float(eval_script(ops[1], state) or 0.0)
        return max(-1.0, min(1.0, cur + delta))
    return script.get("value", 0.0)


def apply_effects(reaction: Dict[str, Any], state: Dict[Tuple[str, str], float]) -> None:
    for ae in (reaction.get("after_effects") or []):
        if ae.get("effect_type") != "Bounded Number Effect":
            continue
        st = ae.get("Set") or {}
        ch = str(st.get("character", ""))
        key = str((st.get("keyring") or [""])[0])
        val = float(eval_script(ae.get("to"), state) or 0.0)
        state[(ch, key)] = max(-1.0, min(1.0, val))


def pick_reaction(option: Dict[str, Any], state: Dict[Tuple[str, str], float], rng: random.Random) -> Dict[str, Any] | None:
    rxs = option.get("reactions") or []
    if not rxs:
        return None
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for rx in rxs:
        d = eval_script(rx.get("desirability_script", 0.0), state)
        if isinstance(d, bool):
            d = 1.0 if d else 0.0
        scored.append((float(d or 0.0), rx))
    m = max(s for s, _ in scored)
    best = [rx for s, rx in scored if abs(s - m) < 1e-9]
    return rng.choice(best)


def choose_wild(encounters: List[Dict[str, Any]], state: Dict[Tuple[str, str], float], current_id: str, rng: random.Random) -> str:
    cands: List[Tuple[float, Dict[str, Any]]] = []
    for e in encounters:
        eid = str(e.get("id", "") or "")
        if (not eid) or eid == current_id:
            continue
        if not bool(eval_script(e.get("acceptability_script", True), state)):
            continue
        d = eval_script(e.get("desirability_script", 0.0), state)
        if isinstance(d, bool):
            d = 1.0 if d else 0.0
        cands.append((float(d or 0.0), e))
    if not cands:
        return ""
    m = max(s for s, _ in cands)
    best = [e for s, e in cands if abs(s - m) < 1e-9]
    return str((rng.choice(best)).get("id", "") or "")


def run_episode(data: Dict[str, Any], rng: random.Random, max_steps: int) -> Dict[str, Any]:
    encounters = data.get("encounters") or []
    enc_by = {str(e.get("id", "") or ""): e for e in encounters}
    start = "page_start" if "page_start" in enc_by else (str(encounters[0].get("id", "") or "") if encounters else "")
    if not start:
        return {"end": "DEAD_END", "turns": 0, "final_endings_available": 0}
    endings = [e for e in encounters if not (e.get("options") or [])]
    state: Dict[Tuple[str, str], float] = {}
    cur = start
    turns = 0
    final_available = 0
    while turns < max_steps and cur in enc_by:
        enc = enc_by[cur]
        opts = enc.get("options") or []
        if not opts:
            return {"end": cur, "turns": turns, "final_endings_available": final_available}
        vis = [
            o
            for o in opts
            if bool(eval_script(o.get("visibility_script", True), state))
            and bool(eval_script(o.get("performability_script", True), state))
        ]
        if not vis:
            return {"end": "DEAD_END", "turns": turns, "final_endings_available": 0}
        chosen = rng.choice(vis)
        rx = pick_reaction(chosen, state, rng)
        if rx is None:
            return {"end": "DEAD_END", "turns": turns, "final_endings_available": 0}
        apply_effects(rx, state)
        avail = sum(1 for e in endings if bool(eval_script(e.get("acceptability_script", True), state)))
        if avail > 0:
            final_available = int(avail)
        nxt = str(rx.get("consequence_id", "") or "")
        if nxt == "wild" or (not nxt):
            nxt = choose_wild(encounters, state, cur, rng)
        if not nxt:
            return {"end": "DEAD_END", "turns": turns + 1, "final_endings_available": final_available}
        cur = nxt
        turns += 1
    return {"end": "TIMEOUT", "turns": turns, "final_endings_available": final_available}


def pct(vals: List[int], p: float) -> int:
    if not vals:
        return 0
    arr = sorted(vals)
    i = max(0, min(len(arr) - 1, int(round(p * (len(arr) - 1)))))
    return int(arr[i])


def main() -> int:
    ap = argparse.ArgumentParser(description="Routing probe for morality constitution storyworld batch.")
    ap.add_argument("--batch-dir", default=r"C:\projects\GPTStoryworld\storyworlds\3-5-2026-morality-constitutions-batch-v1")
    ap.add_argument("--glob", default="mq_constitution_*.json")
    ap.add_argument("--runs", type=int, default=600)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--max-steps", type=int, default=40)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    batch_dir = Path(args.batch_dir).resolve()
    out_path = Path(args.out).resolve() if str(args.out).strip() else batch_dir / "_reports" / "routing_probe_latest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []
    for p in sorted(batch_dir.glob(str(args.glob))):
        data = json.loads(p.read_text(encoding="utf-8"))
        rng = random.Random(int(args.seed))
        rows = [run_episode(data, rng, int(args.max_steps)) for _ in range(max(1, int(args.runs)))]
        turns = [int(r["turns"]) for r in rows]
        fan = [int(r["final_endings_available"]) for r in rows if int(r["final_endings_available"]) > 0]
        dead = sum(1 for r in rows if r["end"] in ("DEAD_END", "TIMEOUT"))
        results.append(
            {
                "world": p.stem,
                "runs": len(rows),
                "avg_turns": round(sum(turns) / len(turns), 3),
                "p10_turns": pct(turns, 0.1),
                "p50_turns": pct(turns, 0.5),
                "p90_turns": pct(turns, 0.9),
                "dead_rate": round(dead / len(rows), 4),
                "final_endings_available_avg": round((sum(fan) / len(fan)) if fan else 0.0, 3),
                "final_endings_available_p10": pct(fan, 0.1),
                "final_endings_available_p50": pct(fan, 0.5),
                "final_endings_available_p90": pct(fan, 0.9),
            }
        )

    payload = {"generated_at": time.time(), "probe": "morality_batch_routing_probe", "results": results}
    out_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
