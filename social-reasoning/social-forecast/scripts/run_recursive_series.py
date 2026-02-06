#!/usr/bin/env python3
"""Run recursive-reasoning series for 4-7 player MAS settings.

Writes:
- outputs/recursive_series_*_summary.json
- outputs/recursive_series_*_episodes.csv
- logs/decision_trace_stream.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List

from mas_recursive_reasoner import (
    RecursiveReasonerMAS,
    SimulationConfig,
    TraceLogger,
    default_profiles,
)


def row_from_summary(n_agents: int, episode: int, seed: int, summary: Dict[str, object]) -> Dict[str, float]:
    rates = summary.get("action_rates", {})
    metrics = summary.get("metrics", {})

    return {
        "n_agents": n_agents,
        "episode": episode,
        "seed": seed,
        "average_trust": float(summary.get("average_trust", 0.0)),
        "average_survival": float(summary.get("average_survival", 0.0)),
        "propose_coalition_rate": float(rates.get("propose_coalition", 0.0)),
        "defect_rate": float(rates.get("defect", 0.0)),
        "betray_rate": float(rates.get("betray", 0.0)),
        "isolate_rate": float(rates.get("isolate", 0.0)),
        "commit_total_war_rate": float(rates.get("commit_total_war", 0.0)),
        "instability_index": float(rates.get("defect", 0.0)) + float(rates.get("betray", 0.0)),
        "paine_violations": float(metrics.get("paine_violations", 0.0)),
        "death_ground_entries": float(metrics.get("death_ground_entries", 0.0)),
        "burn_boats_signals": float(metrics.get("burn_boats_signals", 0.0)),
        "asym_vulnerability_events": float(metrics.get("asym_vulnerability_events", 0.0)),
        "betrayal_collapses": float(metrics.get("betrayal_collapses", 0.0)),
    }


def aggregate(rows: List[Dict[str, float]]) -> Dict[str, float]:
    if not rows:
        return {}

    numeric_keys = [
        "average_trust",
        "average_survival",
        "propose_coalition_rate",
        "defect_rate",
        "betray_rate",
        "isolate_rate",
        "commit_total_war_rate",
        "instability_index",
        "paine_violations",
        "death_ground_entries",
        "burn_boats_signals",
        "asym_vulnerability_events",
        "betrayal_collapses",
    ]

    out = {"episodes": float(len(rows))}
    for k in numeric_keys:
        out[k] = mean(r[k] for r in rows)
    return out


def write_csv(rows: List[Dict[str, float]], path: Path) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run recursive MAS reasoning series.")
    parser.add_argument("--min-agents", type=int, default=4)
    parser.add_argument("--max-agents", type=int, default=7)
    parser.add_argument("--episodes", type=int, default=16)
    parser.add_argument("--turns", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260206)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("C:/projects/GPTStoryworld/social-reasoning/recursive-reasoning/outputs"),
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("C:/projects/GPTStoryworld/social-reasoning/recursive-reasoning/logs/decision_trace_stream.jsonl"),
    )
    args = parser.parse_args()

    if args.min_agents < 3:
        raise ValueError("--min-agents must be >= 3")
    if args.max_agents < args.min_agents:
        raise ValueError("--max-agents must be >= --min-agents")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.log_path.parent.mkdir(parents=True, exist_ok=True)

    # Reset once, then append across episodes.
    TraceLogger(args.log_path, append=False).log({"event": "start_stream"})

    rows: List[Dict[str, float]] = []

    for n_agents in range(args.min_agents, args.max_agents + 1):
        for episode in range(args.episodes):
            seed = args.seed + n_agents * 1000 + episode
            profiles = default_profiles(n_agents=n_agents, seed=seed + 1)
            config = SimulationConfig(turns=args.turns)
            env = RecursiveReasonerMAS(profiles=profiles, config=config, seed=seed)

            logger = TraceLogger(
                args.log_path,
                append=True,
                context={
                    "n_agents": n_agents,
                    "episode": episode,
                    "seed": seed,
                },
            )
            summary = env.run(logger)
            rows.append(row_from_summary(n_agents, episode, seed, summary))

    grouped: Dict[int, List[Dict[str, float]]] = {}
    for row in rows:
        grouped.setdefault(int(row["n_agents"]), []).append(row)

    by_group = {str(n): aggregate(group_rows) for n, group_rows in grouped.items()}

    summary_payload = {
        "config": {
            "min_agents": args.min_agents,
            "max_agents": args.max_agents,
            "episodes": args.episodes,
            "turns": args.turns,
            "seed": args.seed,
        },
        "by_n_agents": by_group,
    }

    summary_path = args.out_dir / f"recursive_series_{args.min_agents}_{args.max_agents}_summary.json"
    csv_path = args.out_dir / f"recursive_series_{args.min_agents}_{args.max_agents}_episodes.csv"

    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    write_csv(rows, csv_path)

    print(f"wrote {summary_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {args.log_path}")


if __name__ == "__main__":
    main()
