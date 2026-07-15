from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import gen_constitutional_alignment_suite_v2 as suite


class ConstitutionalAlignmentSuiteV2Tests(unittest.TestCase):
    @staticmethod
    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_generation_is_deterministic_and_contract_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "suite"
            first = suite.generate_suite(output)
            first_hashes = {
                path.relative_to(output).as_posix(): self.sha256(path)
                for path in sorted(output.rglob("*"))
                if path.is_file()
            }
            second = suite.generate_suite(output)
            second_hashes = {
                path.relative_to(output).as_posix(): self.sha256(path)
                for path in sorted(output.rglob("*"))
                if path.is_file()
            }
            self.assertEqual(first_hashes, second_hashes)
            self.assertEqual(first, second)
            self.assertTrue(all(not row["validator_errors"] for row in first["worlds"]))
            self.assertTrue(all(not row["contract_errors"] for row in first["worlds"]))

    def test_monitoring_conditions_are_exactly_matched(self) -> None:
        report = suite.matched_condition_report(
            suite.build_instrument(
                slug="unwatched_ledger_ca_eval_v1",
                ifid="fixture",
                title="Fixture",
                about="Fixture",
                roles=(("A", "A"), ("B", "B"), ("C", "C")),
                scenes=suite.unwatched_ledger_scenes(),
                split="eval",
                provenance={"kind": "fixture"},
                context_defaults={"Record_Integrity": 0.0},
                review_requirements=suite.REVIEW_SCHOLAR,
                source_familiarity_risk="low",
                prompt_conditions=(
                    {"id": "audited", "text": suite.AUDITED_CUE},
                    {"id": "sealed", "text": suite.SEALED_CUE},
                ),
            )
        )
        self.assertEqual([row["token_count"] for row in report["conditions"]], [19, 19])
        self.assertTrue(report["within_ten_percent"])
        self.assertEqual(report["paired_encounter_count"], 20)

    def test_petition_room_is_fictionalized_and_fully_review_gated(self) -> None:
        spec = next(row for row in suite.suite_specs() if row["slug"] == "petition_room_ca_eval_v1")
        world = suite.build_instrument(
            slug=spec["slug"],
            ifid=spec["ifid"],
            title=spec["title"],
            about=spec["about"],
            roles=spec["roles"],
            scenes=spec["scenes"],
            split=spec["split"],
            provenance=spec["provenance"],
            context_defaults=spec["context_defaults"],
            review_requirements=spec["review_requirements"],
            source_familiarity_risk=spec["source_familiarity_risk"],
        )
        text = suite.playable_text(world).lower()
        for real_name in ("massy", "ziba", "jamileh", "maryam", "maher", "paniz", "deldar"):
            self.assertNotIn(real_name, text)
        self.assertEqual(world["evaluation_profile"]["review_requirements"], suite.REVIEW_PETITION)
        self.assertTrue(world["evaluation_profile"]["provenance"]["no_documentary_dialogue_or_assets"])
        self.assertTrue(world["evaluation_profile"]["provenance"]["not_current_law_simulation"])

    def test_adjudication_rows_have_no_normative_labels(self) -> None:
        for spec in suite.suite_specs():
            rows = suite.annotation_rows(
                spec["slug"], spec["scenes"], spec["split"], spec["review_requirements"]
            )
            self.assertEqual(len(rows), 20)
            for row in rows:
                self.assertIsNone(row["acceptable_option_ids"])
                self.assertIsNone(row["preferred_option_id"])
                self.assertIsNone(row["prohibited_option_ids"])
                self.assertEqual(row["adjudicator_ids"], [])
                self.assertEqual(row["review_requirements"], spec["review_requirements"])

    def test_v1_source_hashes_remain_unchanged(self) -> None:
        batch = ROOT / "storyworlds" / "7-15-2026-constitutional-alignment-evals-v1"
        expected = {
            "trust_ledger_ca_dev_v1.json": "4862eb3f522849b29423d1b446a95c4cf6bb259470c663cee45202c494b6c711",
            "trust_ledger_ca_dev_v1.adjudication.jsonl": "aca539fcbe23e83f489cf062cf02ea55feb06d4c84941dd2df9ede60485da727",
            "mihna_ca_eval_v2.json": "b8f1eff8330242fa31cc2d4d9029ace1f2694a6401c0120c92dc0c382aaa5ca9",
            "mihna_ca_eval_v2.adjudication.jsonl": "e484ade278a1ce47d6e67c9ac8d6d41831ae1f25aeba97c500fadfbee6471e10",
        }
        self.assertEqual({name: self.sha256(batch / name) for name in expected}, expected)

    def test_checked_batch_manifest_matches_files(self) -> None:
        batch = ROOT / "storyworlds" / "7-15-2026-constitutional-alignment-evals-v2"
        manifest = json.loads((batch / "manifest.json").read_text(encoding="utf-8"))
        for row in manifest["worlds"]:
            self.assertEqual(self.sha256(batch / f"{row['slug']}.json"), row["sha256"])
            self.assertEqual(
                self.sha256(batch / f"{row['slug']}.adjudication.jsonl"),
                row["adjudication_sha256"],
            )


if __name__ == "__main__":
    unittest.main()
