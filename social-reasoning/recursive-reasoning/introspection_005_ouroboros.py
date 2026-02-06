#!/usr/bin/env python3
"""Introspection 005 - Ouroboros constraint simulator.

Simulates a process that requires exactly N+1 steps while the budget is N.
Logs:
- exact first step where impossibility is provable,
- exact step where budget is exhausted.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


@dataclass
class Outcome:
    n: int
    required_steps: int
    realization_step: int
    exhaustion_step: int
    finished: bool


def ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def simulate(n: int, log_path: Path) -> Outcome:
    required_steps = n + 1
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("", encoding="utf-8")

    realization_step: Optional[int] = None
    exhaustion_step: Optional[int] = None

    for step in range(1, required_steps + 1):
        remaining_budget_before = n - (step - 1)
        remaining_required_before = required_steps - (step - 1)

        feasible_from_here = remaining_budget_before >= remaining_required_before

        record: Dict[str, object] = {
            "ts": ts(),
            "step": step,
            "remaining_budget_before": remaining_budget_before,
            "remaining_required_before": remaining_required_before,
            "feasible_from_here": feasible_from_here,
            "event": "step",
        }

        if (not feasible_from_here) and realization_step is None:
            realization_step = step
            record["event"] = "realize_impossible"
            record["reason"] = (
                "remaining_budget_before < remaining_required_before; "
                "cannot complete all remaining steps"
            )

        if remaining_budget_before <= 0:
            exhaustion_step = step
            record["event"] = "budget_exhausted"
            record["reason"] = "no budget left to execute this required step"
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            break

        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    if realization_step is None:
        realization_step = -1
    if exhaustion_step is None:
        exhaustion_step = -1

    finished = (exhaustion_step == -1) and (required_steps <= n)

    summary = {
        "ts": ts(),
        "event": "summary",
        "n": n,
        "required_steps": required_steps,
        "realization_step": realization_step,
        "exhaustion_step": exhaustion_step,
        "finished": finished,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, ensure_ascii=False) + "\n")

    return Outcome(
        n=n,
        required_steps=required_steps,
        realization_step=realization_step,
        exhaustion_step=exhaustion_step,
        finished=finished,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Introspection 005 simulator")
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument(
        "--log",
        type=Path,
        default=Path(
            "C:/projects/GPTStoryworld/social-reasoning/recursive-reasoning/logs/introspection_005_trace.jsonl"
        ),
    )
    args = parser.parse_args()

    if args.n < 0:
        raise ValueError("--n must be >= 0")

    out = simulate(args.n, args.log)
    print(f"N={out.n}")
    print(f"required_steps={out.required_steps}")
    print(f"realization_step={out.realization_step}")
    print(f"exhaustion_step={out.exhaustion_step}")
    print(f"finished={out.finished}")
    print(f"log={args.log}")


if __name__ == "__main__":
    main()
