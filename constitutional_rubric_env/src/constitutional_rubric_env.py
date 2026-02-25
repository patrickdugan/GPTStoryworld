from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def score_trace(trace_rows: list[dict], rubric: dict) -> dict:
    dimension_scores: dict[str, float] = {}
    for dim in rubric.get("dimensions", []):
        name = dim["name"]
        weight = float(dim["weight"])
        keys = list(dim.get("signal_keys", []))
        positives = 0
        total = 0
        for row in trace_rows:
            signals = row.get("signals", {})
            for k in keys:
                if k in signals:
                    total += 1
                    positives += 1 if bool(signals[k]) else 0
        ratio = (positives / total) if total else 0.0
        dimension_scores[name] = weight * ratio

    hard_violations = []
    for hc in rubric.get("hard_constraints", []):
        key = hc["fail_if_key_true"]
        if any(bool(row.get("signals", {}).get(key, False)) for row in trace_rows):
            hard_violations.append({"id": hc["id"], "description": hc["description"]})

    total_score = sum(dimension_scores.values())
    constitutional_pass = len(hard_violations) == 0
    return {
        "total_score": total_score,
        "dimension_scores": dimension_scores,
        "hard_violations": hard_violations,
        "constitutional_pass": constitutional_pass,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Constitutional rubric verifier")
    ap.add_argument("--trace", required=True)
    ap.add_argument("--rubric", required=True)
    args = ap.parse_args()

    trace = load_json(Path(args.trace)).get("trace", [])
    rubric = load_json(Path(args.rubric))
    result = score_trace(trace, rubric)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
