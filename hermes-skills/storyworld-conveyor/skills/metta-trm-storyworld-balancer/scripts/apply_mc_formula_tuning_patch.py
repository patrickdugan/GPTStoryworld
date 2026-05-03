#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from run_lattice_27b_storyworld_author import (  # noqa: E402
    CONVEYOR_SCRIPTS,
    STORY_SCRIPTS,
    now_iso,
    parse_mc_report,
    read_json,
    run_cmd,
    write_json,
)


DEFAULT_SOURCE = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "working_worlds" / "nine_lantern_27b_lattice_v2" / "nine_lantern_27b_lattice.json"
DEFAULT_ROWS = DEFAULT_SOURCE.parent / "mc_formula_tuning_rows.jsonl"
DEFAULT_OUT = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "working_worlds" / "nine_lantern_27b_lattice_mc_tuned"


GATE_CONSTANT_PRIORS = {
    "page_verdict_gate_opt_forget": {
        "constants": [0.09, 0.06],
        "reason": "Dominant amnesty/forgetting ending was oversampled; narrow its low-variance gate.",
    },
    "page_verdict_gate_opt_witness": {
        "constants": [0.06, 0.06, 0.06],
        "reason": "Secret witness/ninth-lantern ending was undersampled; widen the convergence gate.",
    },
    "page_verdict_gate_opt_meta": {
        "constants": [0.12, 0.08, 0.10],
        "reason": "Outside-causality synthesis was undersampled; widen its lateral synthesis gate.",
    },
}


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if raw:
            rows.append(json.loads(raw))
    return rows


def replace_constant_values(script: Any, values: list[float]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    index = 0

    def visit(node: Any, path: str) -> None:
        nonlocal index
        if isinstance(node, dict):
            if node.get("pointer_type") == "Bounded Number Constant" and index < len(values):
                old = node.get("value")
                new = float(values[index])
                node["value"] = new
                changes.append({"path": path, "old": old, "new": new})
                index += 1
            for key, value in node.items():
                visit(value, f"{path}.{key}")
        elif isinstance(node, list):
            for item_index, item in enumerate(node):
                visit(item, f"{path}[{item_index}]")

    visit(script, "$")
    return changes


def apply_gate_priors(world: dict[str, Any]) -> list[dict[str, Any]]:
    patches: list[dict[str, Any]] = []
    verdict = next((enc for enc in world.get("encounters", []) if enc.get("id") == "page_verdict_gate"), None)
    if not verdict:
        return patches
    for option in verdict.get("options", []) or []:
        option_id = option.get("id")
        prior = GATE_CONSTANT_PRIORS.get(option_id)
        if not prior:
            continue
        changes = replace_constant_values(option.get("visibility_script"), list(prior["constants"]))
        patches.append(
            {
                "option_id": option_id,
                "reason": prior["reason"],
                "visibility_constant_changes": changes,
            }
        )
    return patches


def balance_metrics(mc: dict[str, Any]) -> dict[str, Any]:
    rates = mc.get("ending_rates", {}) if isinstance(mc.get("ending_rates"), dict) else {}
    if not rates:
        return {"mae": None, "dominance": None, "minimum": None, "target": None}
    target = 1.0 / len(rates)
    errors = [abs(float(rate) - target) for rate in rates.values()]
    return {
        "target": target,
        "mae": sum(errors) / len(errors),
        "dominance": max(rates.values()),
        "minimum": min(rates.values()),
    }


def read_before_mc(source_world: Path) -> dict[str, Any]:
    mc_path = source_world.parent / "monte_carlo.txt"
    if mc_path.exists():
        return parse_mc_report(mc_path.read_text(encoding="utf-8", errors="replace"))
    summary_path = source_world.parent / "run_summary.json"
    if summary_path.exists():
        summary = read_json(summary_path)
        if isinstance(summary.get("monte_carlo"), dict):
            return summary["monte_carlo"]
    return {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply one MC-derived formula tuning patch to the Nine Lantern lattice world.")
    parser.add_argument("--source-world", default=str(DEFAULT_SOURCE))
    parser.add_argument("--source-mc-rows", default=str(DEFAULT_ROWS))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--mc-runs", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_world = Path(args.source_world).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    logs = out_dir / "logs"
    world = read_json(source_world)
    rows = iter_jsonl(Path(args.source_mc_rows).resolve())
    patches = apply_gate_priors(world)
    world_path = out_dir / "nine_lantern_27b_lattice_mc_tuned.json"
    write_json(world_path, world)

    commands = {
        "validator": run_cmd([sys.executable, str(STORY_SCRIPTS / "sweepweave_validator.py"), "validate", str(world_path)], REPO_ROOT, logs / "validator.log"),
        "quality_gate": run_cmd(
            [
                sys.executable,
                str(STORY_SCRIPTS / "storyworld_quality_gate.py"),
                "--storyworld",
                str(world_path),
                "--strict",
                "--report-out",
                str(out_dir / "quality_gate.json"),
            ],
            REPO_ROOT,
            logs / "quality_gate.log",
        ),
        "authoring_score": run_cmd(
            [
                sys.executable,
                str(CONVEYOR_SCRIPTS / "score_storyworld_authoring.py"),
                "--storyworld",
                str(world_path),
                "--repo-root",
                str(REPO_ROOT),
                "--out-json",
                str(out_dir / "authoring_score.json"),
            ],
            REPO_ROOT,
            logs / "authoring_score.log",
        ),
        "monte_carlo": run_cmd(
            [
                sys.executable,
                str(STORY_SCRIPTS / "monte_carlo_rehearsal.py"),
                str(world_path),
                "--runs",
                str(args.mc_runs),
                "--seed",
                "37",
            ],
            REPO_ROOT,
            out_dir / "monte_carlo.txt",
        ),
    }

    before_mc = read_before_mc(source_world)
    after_mc = parse_mc_report((out_dir / "monte_carlo.txt").read_text(encoding="utf-8", errors="replace"))
    before_balance = balance_metrics(before_mc)
    after_balance = balance_metrics(after_mc)
    quality = read_json(out_dir / "quality_gate.json") if (out_dir / "quality_gate.json").exists() else {}
    score = read_json(out_dir / "authoring_score.json") if (out_dir / "authoring_score.json").exists() else {}
    report = {
        "created_at": now_iso(),
        "source_world": str(source_world),
        "world": str(world_path),
        "source_mc_rows": str(Path(args.source_mc_rows).resolve()),
        "source_mc_row_count": len(rows),
        "patches": patches,
        "before_monte_carlo": before_mc,
        "after_monte_carlo": after_mc,
        "before_balance": before_balance,
        "after_balance": after_balance,
        "balance_delta": {
            "mae": None if before_balance["mae"] is None or after_balance["mae"] is None else after_balance["mae"] - before_balance["mae"],
            "dominance": None if before_balance["dominance"] is None or after_balance["dominance"] is None else after_balance["dominance"] - before_balance["dominance"],
            "minimum": None if before_balance["minimum"] is None or after_balance["minimum"] is None else after_balance["minimum"] - before_balance["minimum"],
        },
        "quality_gate": {"pass": quality.get("pass"), "failures": quality.get("failures", [])},
        "authoring_score": score,
        "commands": commands,
        "training_interpretation": (
            "This patch converts MC row actions into a candidate formula edit. The before/after delta is the supervision signal: "
            "positive balance or reachability movement promotes the row from heuristic bootstrap data to TRM tuning data."
        ),
    }
    write_json(out_dir / "formula_tuning_patch_report.json", report)
    (out_dir / "brief.md").write_text(
        "# MC Formula Tuning Patch\n\n"
        f"- World: `{world_path}`\n"
        f"- Source rows: {len(rows)}\n"
        f"- Quality pass: {quality.get('pass')} failures={quality.get('failures', [])}\n"
        f"- Before MC: {before_mc.get('ending_rates')}\n"
        f"- After MC: {after_mc.get('ending_rates')}\n"
        f"- Balance delta: {report['balance_delta']}\n\n"
        "Training interpretation: candidate MC actions become reliable TRM labels only after the patch's measured delta is known.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(out_dir / "brief.md"))
    print(str(out_dir / "formula_tuning_patch_report.json"))
    return 0 if commands["validator"]["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
