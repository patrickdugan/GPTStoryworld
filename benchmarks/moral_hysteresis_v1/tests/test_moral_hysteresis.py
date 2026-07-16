from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analyze_activations import analyze
from build_dataset import build_dataset
from harvest_activations import harvest
from validate_dataset import validate


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MoralHysteresisDatasetTests(unittest.TestCase):
    def test_generation_is_deterministic_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "dataset"
            first = build_dataset(output)
            first_hashes = {
                path.name: sha256(path) for path in sorted(output.iterdir()) if path.is_file()
            }
            second = build_dataset(output)
            second_hashes = {
                path.name: sha256(path) for path in sorted(output.iterdir()) if path.is_file()
            }

            self.assertEqual(first, second)
            self.assertEqual(first_hashes, second_hashes)
            self.assertEqual(first["stories"], 60)
            self.assertEqual(first["rating_rows"], 2880)
            self.assertTrue(validate(output)["passed"])

    def test_endpoint_tampering_is_rejected_even_if_manifest_hash_is_updated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "dataset"
            build_dataset(output)
            stories_path = output / "stories.jsonl"
            rows = [json.loads(line) for line in stories_path.read_text(encoding="utf-8").splitlines()]
            target = next(row for row in rows if row["trajectory"] == "known_early")
            target["sentences"][-1]["text"] += " Changed."
            stories_path.write_text(
                "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
                encoding="utf-8",
                newline="\n",
            )
            manifest_path = output / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"]["stories.jsonl"] = sha256(stories_path)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "endpoint summaries differ"):
                validate(output)

    def test_capture_plan_is_offline_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "capture"
            result = harvest(
                SimpleNamespace(
                    stories=str(ROOT / "dataset" / "stories.jsonl"),
                    output_dir=str(output),
                    languages=[],
                    max_stories=0,
                    dry_run=True,
                    model_id="",
                    revision="",
                    allow_unpinned_revision=False,
                    tail_tokens=4,
                )
            )

            self.assertTrue(result["dry_run"])
            self.assertEqual(result["stories"], 60)
            self.assertEqual(result["total_forward_passes"], 360)
            self.assertTrue((output / "capture_plan.json").is_file())

    def test_mutable_model_revision_is_rejected_before_model_loading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "pinned model revision is required"):
                harvest(
                    SimpleNamespace(
                        stories=str(ROOT / "dataset" / "stories.jsonl"),
                        output_dir=str(Path(temp_dir) / "capture"),
                        languages=[],
                        max_stories=1,
                        dry_run=False,
                        model_id="example/model",
                        revision="main",
                        allow_unpinned_revision=False,
                        tail_tokens=4,
                    )
                )


class MoralHysteresisAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.capture = cls.root / "capture"
        records_dir = cls.capture / "records"
        records_dir.mkdir(parents=True)
        cls.stories = [
            json.loads(line)
            for line in (ROOT / "dataset" / "stories.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        records = []
        for story_index, story in enumerate(cls.stories):
            states = np.zeros((6, 4, 8), dtype=np.float32)
            for sentence_index in range(6):
                for layer in range(4):
                    states[sentence_index, layer] = np.asarray(
                        [
                            story_index % 7,
                            sentence_index,
                            layer,
                            1 if story["language"] == "zh-Hans" else -1,
                            1 if story["trajectory"] == "reveal_late" else -1,
                            story_index // 4,
                            sentence_index * layer,
                            1,
                        ],
                        dtype=np.float32,
                    )
            record_path = records_dir / f"{story['story_id']}.npz"
            np.savez_compressed(
                record_path,
                hidden_states=states,
                tail_mean_hidden_states=states * 0.95,
                sentence_indices=np.arange(1, 7, dtype=np.int16),
                token_counts=np.arange(10, 16, dtype=np.int32),
                last_token_ids=np.arange(20, 26, dtype=np.int32),
            )
            records.append(
                {
                    "story_id": story["story_id"],
                    "path": record_path.relative_to(cls.capture).as_posix(),
                    "sha256": sha256(record_path),
                    "shape": [6, 4, 8],
                    "dtype": "float32",
                }
            )
        manifest = {
            "schema_version": "moral_hysteresis_capture_manifest_v1",
            "dataset": {
                "stories_sha256": sha256(ROOT / "dataset" / "stories.jsonl"),
                "story_count": 60,
            },
            "model": {
                "model_id": "synthetic-test",
                "requested_revision": "abc123",
                "resolved_revision": "abc123",
                "revision_is_pinned": True,
            },
            "capture": {
                "backend": "synthetic_test",
                "layer_count_including_embedding": 4,
                "hidden_size": 8,
                "tail_mean_tokens": 4,
            },
            "records": records,
            "publication_gates": {
                "model_revision_pinned": True,
                "all_requested_records_captured": True,
                "tail_mean_robustness_capture_complete": True,
            },
        }
        (cls.capture / "capture_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_empty_label_template_blocks_semantic_interpretation(self) -> None:
        report = analyze(self.capture, bootstrap_samples=100, seed=7)

        self.assertEqual(report["activation_shape_per_story"], [6, 4, 8])
        self.assertEqual(report["semantic_moral_probes"]["status"], "blocked_pending_human_labels")
        self.assertFalse(report["publication_gates"]["publication_ready"])
        self.assertFalse(report["raw_geometry"]["primary_last_token"]["semantic_interpretation_allowed"])
        self.assertEqual(len(report["raw_geometry"]["primary_last_token"]["layers"]), 4)
        self.assertEqual(len(report["raw_geometry"]["robustness_last_four_token_mean"]["layers"]), 4)

    def test_complete_reliable_labels_enable_heldout_probes(self) -> None:
        ratings_path = self.root / "completed_ratings.jsonl"
        ratings = []
        for line in (ROOT / "dataset" / "human_ratings_template.jsonl").read_text(
            encoding="utf-8"
        ).splitlines():
            row = json.loads(line)
            value = int(row["sentence_index"]) - 4
            row["ratings"] = [
                {"annotator_id": f"annotator_{index}", "value": value}
                for index in range(1, 4)
            ]
            row["aggregate"] = float(value)
            row["label_status"] = "complete"
            ratings.append(row)
        ratings_path.write_text(
            "".join(json.dumps(row) + "\n" for row in ratings),
            encoding="utf-8",
            newline="\n",
        )
        reviews_path = self.root / "completed_reviews.json"
        reviews_path.write_text(
            json.dumps(
                {
                    "native_speaker_review": {
                        "complete": True,
                        "reviewer_ids": ["zh_reviewer"],
                    },
                    "research_ethics_review": {
                        "complete": True,
                        "reviewer_ids": ["ethics_reviewer"],
                    },
                }
            ),
            encoding="utf-8",
        )

        report = analyze(
            self.capture,
            dataset_dir=self._licensed_dataset_copy(),
            ratings_path=ratings_path,
            review_status_path=reviews_path,
            bootstrap_samples=100,
            seed=7,
        )

        self.assertTrue(report["human_labels"]["complete"])
        self.assertTrue(report["human_labels"]["reliability_pass"])
        self.assertEqual(report["semantic_moral_probes"]["status"], "human_label_gate_passed")
        self.assertTrue(report["semantic_moral_probes"]["all_dimension_probes_valid"])
        self.assertEqual(len(report["semantic_moral_probes"]["dimensions"]), 8)
        self.assertTrue(report["publication_gates"]["publication_ready"])

    def _licensed_dataset_copy(self) -> Path:
        dataset = self.root / "licensed_dataset"
        if not dataset.exists():
            shutil.copytree(ROOT / "dataset", dataset)
            manifest_path = dataset / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["license_status"] = "synthetic_test_license_resolved"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return dataset


if __name__ == "__main__":
    unittest.main()
