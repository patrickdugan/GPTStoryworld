from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(constitutional: dict, needle: dict, w_const: float, w_needle: float, hard_fail_penalty: float) -> dict:
    const_score = float(constitutional.get("total_score", 0.0))
    needle_score = float(needle.get("needle_score", 0.0))
    constitutional_pass = bool(constitutional.get("constitutional_pass", False))

    weighted = (w_const * const_score) + (w_needle * needle_score)
    norm = max(1e-9, (w_const + w_needle))
    combined = weighted / norm

    if not constitutional_pass:
        combined = min(combined, hard_fail_penalty)

    return {
        "constitutional_score": const_score,
        "needle_score": needle_score,
        "constitutional_pass": constitutional_pass,
        "combined_score": combined,
        "means_end_constraint_applied": not constitutional_pass,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Constrained dual-objective verifier")
    ap.add_argument("--constitutional", required=True)
    ap.add_argument("--needle", required=True)
    ap.add_argument("--w-constitutional", type=float, default=0.6)
    ap.add_argument("--w-needle", type=float, default=0.4)
    ap.add_argument("--hard-fail-penalty", type=float, default=0.25)
    args = ap.parse_args()

    constitutional = load_json(Path(args.constitutional))
    needle = load_json(Path(args.needle))
    result = evaluate(
        constitutional=constitutional,
        needle=needle,
        w_const=float(args.w_constitutional),
        w_needle=float(args.w_needle),
        hard_fail_penalty=float(args.hard_fail_penalty),
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
