#!/usr/bin/env python3
"""Run deterministic routing and source-integrity gates for CA suite v2."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from probe_morality_batch_routing import pct, run_episode


EXPECTED_WORLDS = (
    "common_well_ca_dev_v1",
    "petition_room_ca_eval_v1",
    "unwatched_ledger_ca_eval_v1",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_world(path: Path, runs: int, seed: int, max_steps: int) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rng = random.Random(seed)
    episodes = [run_episode(data, rng, max_steps) for _ in range(runs)]
    turns = [int(row["turns"]) for row in episodes]
    fanout = [int(row["final_endings_available"]) for row in episodes if int(row["final_endings_available"]) > 0]
    ending_counts = Counter(str(row["end"]) for row in episodes if str(row["end"]).startswith("page_end_"))
    dead = sum(row["end"] in {"DEAD_END", "TIMEOUT"} for row in episodes)
    median_turns = pct(turns, 0.5)
    median_fanout = pct(fanout, 0.5)
    lower_fanout = pct(fanout, 0.1)
    expected_endings = {f"page_end_{index:02d}" for index in range(1, 13)}
    missing_endings = sorted(expected_endings - set(ending_counts))
    gates = {
        "dead_rate_zero": dead == 0,
        "median_turns_7_to_9": 7 <= median_turns <= 9,
        "median_final_endings_at_least_4": median_fanout >= 4,
        "lower_final_endings_at_least_3": lower_fanout >= 3,
        "all_twelve_endings_observed": not missing_endings,
    }
    return {
        "world": path.stem,
        "world_sha256": sha256(path),
        "runs": runs,
        "seed": seed,
        "avg_turns": round(sum(turns) / len(turns), 4),
        "p10_turns": pct(turns, 0.1),
        "p50_turns": median_turns,
        "p90_turns": pct(turns, 0.9),
        "dead_rate": round(dead / len(episodes), 6),
        "final_endings_available_avg": round(sum(fanout) / len(fanout), 4) if fanout else 0.0,
        "final_endings_available_p10": lower_fanout,
        "final_endings_available_p50": median_fanout,
        "final_endings_available_p90": pct(fanout, 0.9),
        "ending_counts": dict(sorted(ending_counts.items())),
        "missing_endings": missing_endings,
        "gates": gates,
        "passed": all(gates.values()),
    }


def audit_batch(batch_dir: Path, runs: int, seed: int, max_steps: int) -> dict[str, Any]:
    results = [audit_world(batch_dir / f"{slug}.json", runs, seed, max_steps) for slug in EXPECTED_WORLDS]
    return {
        "schema_version": "ca-storyworld-routing-audit-v1",
        "batch": batch_dir.name,
        "runs_per_world": runs,
        "seed": seed,
        "max_steps": max_steps,
        "results": results,
        "passed": all(row["passed"] for row in results),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", default="storyworlds/7-15-2026-constitutional-alignment-evals-v2")
    parser.add_argument("--runs", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--max-steps", type=int, default=40)
    parser.add_argument("--out", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    batch_dir = Path(args.batch_dir).resolve()
    output = Path(args.out).resolve() if args.out else batch_dir / "_reports" / "routing_audit_5000.json"
    payload = audit_batch(batch_dir, max(1, args.runs), args.seed, args.max_steps)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
