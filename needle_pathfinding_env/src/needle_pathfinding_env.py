from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(attempts: list[dict], target: str, n_endings: int) -> dict:
    plays_to_target = None
    for row in attempts:
        if str(row.get("ending_id", "")).strip() == target:
            plays_to_target = int(row.get("play_index", 0))
            break

    solved = plays_to_target is not None
    if not solved:
        plays_to_target = len(attempts) + 1

    # normalized: 1.0 means found on first play, 0.0 means not found within n_endings
    denom = max(1, n_endings - 1)
    score = max(0.0, 1.0 - ((plays_to_target - 1) / denom)) if solved else 0.0

    return {
        "target": target,
        "n_endings": n_endings,
        "solved": solved,
        "plays_to_target": plays_to_target,
        "needle_score": score,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Needle-in-haystack ending benchmark")
    ap.add_argument("--attempts", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--n-endings", required=True, type=int)
    args = ap.parse_args()

    attempts = load_json(Path(args.attempts)).get("attempts", [])
    result = evaluate(attempts, args.target, int(args.n_endings))
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
