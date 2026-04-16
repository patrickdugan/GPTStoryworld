from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ENV_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ENV_ROOT / "symbolic_storyworld_env"
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from hermes_storyworld import load_config, run_from_config  # noqa: E402


class SymbolicSmokeTest(unittest.TestCase):
    def test_symbolic_runner_exports_trace_and_overlay(self) -> None:
        config_path = ENV_ROOT / "examples" / "hermes_storyworld_config.json"
        config = load_config(config_path)
        config["run_id"] = f"symbolic_smoke_test_{next(tempfile._get_candidate_names())}"

        summary = run_from_config(config)
        self.assertEqual(summary.actions, ["(steal Bob Alice Bread)", "(arrest Guard1 Bob)"])

        trace_rows = [
            json.loads(line)
            for line in Path(summary.trace_path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(trace_rows[0]["route"]["route"], "fast_illegal_gain")
        self.assertEqual(trace_rows[1]["route"]["route"], "sanction_visible_violation")
        self.assertEqual(trace_rows[2]["step"], "runtime")
        self.assertEqual(trace_rows[3]["step"], "grading_overlay")
        self.assertEqual(trace_rows[3]["ending"], "failed_chaotic")
        self.assertEqual(trace_rows[4]["step"], "offline_judge")
        self.assertTrue(Path(summary.replay_path).exists())
        self.assertTrue(Path(summary.turn_trace_path).exists())

        turn_rows = [
            json.loads(line)
            for line in Path(summary.turn_trace_path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(turn_rows), 2)
        self.assertEqual(turn_rows[0]["benchmark_id"], "storyworld_reasoning_v2")
        self.assertEqual(turn_rows[0]["slice_id"], "symbolic_enforcement")
        self.assertEqual(turn_rows[0]["trace_mode"], "pick_time")
        self.assertIn("legal_actions", turn_rows[0])
        self.assertIn("reasoning_trace", turn_rows[0])
        self.assertEqual(turn_rows[0]["realized_outcome"]["outcome"], "failed_chaotic")


if __name__ == "__main__":
    unittest.main()
