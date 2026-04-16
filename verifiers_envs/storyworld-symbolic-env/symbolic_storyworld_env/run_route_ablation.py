from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from .hermes_storyworld import load_config, run_from_config
    from .jsonl_trace import write_json
except ImportError:
    from hermes_storyworld import load_config, run_from_config
    from jsonl_trace import write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run symbolic storyworld route ablations.")
    parser.add_argument("--config", required=True, help="Base config path.")
    return parser.parse_args()


def _load_trace_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _extract_action_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if isinstance(row.get("step"), int)]


def main() -> int:
    args = parse_args()
    base_config = load_config(Path(args.config).resolve())

    outputs: dict[str, Any] = {}
    for route_mode in ("trm_hint", "no_hint"):
        cfg = dict(base_config)
        cfg["run_id"] = f"{base_config.get('run_id', 'symbolic_ablation')}_{route_mode}"
        cfg["route_mode"] = route_mode
        summary = run_from_config(cfg)
        rows = _load_trace_rows(Path(summary.trace_path))
        outputs[route_mode] = {
            "summary": summary.__dict__,
            "action_rows": _extract_action_rows(rows),
        }

    comparison = {
        "modes": outputs,
        "diff": {
            "same_actions": outputs["trm_hint"]["summary"]["actions"] == outputs["no_hint"]["summary"]["actions"],
            "trm_actions": outputs["trm_hint"]["summary"]["actions"],
            "no_hint_actions": outputs["no_hint"]["summary"]["actions"],
        },
    }

    run_dir = Path(outputs["trm_hint"]["summary"]["run_dir"]).parent
    out_path = run_dir / "route_ablation_comparison.json"
    write_json(out_path, comparison)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
