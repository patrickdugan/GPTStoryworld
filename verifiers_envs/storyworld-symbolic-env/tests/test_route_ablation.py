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

from hermes_storyworld import load_config  # noqa: E402
from run_route_ablation import main as run_ablation_main  # noqa: E402


class RouteAblationTest(unittest.TestCase):
    def test_route_ablation_writes_comparison(self) -> None:
        base_cfg = load_config(ENV_ROOT / "examples" / "hermes_storyworld_config.json")
        base_cfg["run_id"] = f"symbolic_ablation_test_{next(tempfile._get_candidate_names())}"
        cfg_path = ENV_ROOT / "examples" / f"{base_cfg['run_id']}.json"
        cfg_path.write_text(json.dumps(base_cfg, indent=2) + "\n", encoding="utf-8")
        try:
            old_argv = sys.argv[:]
            sys.argv = ["run_route_ablation.py", "--config", str(cfg_path)]
            rc = run_ablation_main()
            self.assertEqual(rc, 0)
            comparison_path = (ENV_ROOT / "runs" / f"{base_cfg['run_id']}_trm_hint").parent / "route_ablation_comparison.json"
            self.assertTrue(comparison_path.exists())
        finally:
            sys.argv = old_argv
            cfg_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
