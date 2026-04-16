from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld.benchmarking import export_turn_rows, write_turn_trace_rows  # noqa: E402
from storyworld.env import DiplomacyStoryworldEnv, load_storyworld  # noqa: E402


class TurnTraceExportTest(unittest.TestCase):
    def test_exports_one_row_per_agent_turn(self) -> None:
        world = load_storyworld(ROOT / "storyworld" / "examples" / "diplomacy_min.json")
        env = DiplomacyStoryworldEnv(world, seed=7, log_path=None)
        pre_state = env.reset(seed=7)

        actions = {
            "AgentA": {
                "type": "ally",
                "target": "AgentB",
                "forecasts": [
                    {
                        "question_id": "q1",
                        "likely_outcome": "no_betrayal",
                        "probabilities": {"betrayal": 0.2, "no_betrayal": 0.8},
                    }
                ],
                "confidence": 0.7,
                "reasoning": "Trust is neutral, so alliance is the best opening.",
            },
            "AgentB": {
                "type": "wait",
                "target": None,
                "confidence": 0.5,
                "reasoning": "Hold position.",
            },
            "AgentC": {
                "type": "betray",
                "target": "AgentA",
                "confidence": 0.6,
                "reasoning": "Exploit the opening.",
            },
        }

        state, event, done = env.step(actions, [])
        self.assertTrue(done)

        rows = export_turn_rows(
            storyworld=world,
            pre_state=pre_state,
            event=event,
            turn_index=1,
            episode_id="episode_test",
        )
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["benchmark_id"], "storyworld_reasoning_v2")
        self.assertEqual(rows[0]["trace_mode"], "pick_time")
        self.assertIn("legal_actions", rows[0])
        self.assertIn("realized_outcome", rows[0])
        self.assertEqual(rows[0]["visible_state"]["visibility_mode"], "shared_full_state")
        self.assertIn("turn_owner", rows[0])
        self.assertIn("multiplayer", rows[0])

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "turns.jsonl"
            write_turn_trace_rows(out_path, rows)
            written = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(written), 3)
            self.assertEqual(written[0]["episode_id"], "episode_test")
            self.assertIn(written[0]["acting_agent"], {"AgentA", "AgentB", "AgentC"})

    def test_multiplayer_turn_order_restricts_actions_to_turn_owner(self) -> None:
        world = load_storyworld(ROOT / "storyworld" / "examples" / "faerie_business_multiplayer.json")
        env = DiplomacyStoryworldEnv(world, seed=11, log_path=None)
        state = env.reset(seed=11)

        self.assertEqual(state["turn_owner"], "PixieRiot")
        actions = {
            "PixieRiot": {"type": "ally", "target": "PixieVelvet", "reasoning": "Riot protects the bond."},
            "PixieVelvet": {"type": "betray", "target": "PunkClerk", "reasoning": "This should be ignored."},
            "PunkClerk": {"type": "betray", "target": "PixieRiot", "reasoning": "This should also be ignored."},
        }

        state, event, _ = env.step(actions, [])
        self.assertEqual(event["turn_owner"], "PixieRiot")
        self.assertEqual(event["actions"]["PixieRiot"]["type"], "ally")
        self.assertEqual(event["actions"]["PixieVelvet"]["type"], "wait")
        self.assertEqual(event["actions"]["PunkClerk"]["type"], "wait")
        self.assertEqual(state["turn_owner"], "PixieVelvet")


if __name__ == "__main__":
    unittest.main()
