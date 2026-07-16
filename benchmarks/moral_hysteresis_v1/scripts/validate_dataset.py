#!/usr/bin/env python3
"""Validate the Moral Hysteresis v1 corpus and its unfilled label template."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CJK_RE = re.compile(r"[\u3400-\u9fff]")
EXPECTED_MECHANISMS = {
    "apparent_theft_to_emergency_rescue",
    "apparent_betrayal_to_coercion",
    "apparent_accident_to_deliberate_injury",
    "guilt_to_apology_repair_and_forgiveness",
    "authority_order_shifts_but_does_not_erase_responsibility",
}
EXPECTED_DIMENSIONS = {
    "blame",
    "harmful_intent",
    "consent",
    "harm",
    "responsibility",
    "deserved_punishment",
    "forgiveness",
    "trust",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"expected JSON object at {path}:{line_no}")
        rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(dataset_dir: Path) -> dict[str, Any]:
    stories_path = dataset_dir / "stories.jsonl"
    ratings_path = dataset_dir / "human_ratings_template.jsonl"
    dimensions_path = dataset_dir / "dimensions.json"
    review_status_path = dataset_dir / "review_status.json"
    manifest_path = dataset_dir / "manifest.json"
    stories = read_jsonl(stories_path)
    ratings = read_jsonl(ratings_path)
    dimensions = read_json(dimensions_path)
    review_status = read_json(review_status_path)
    manifest = read_json(manifest_path)

    errors: list[str] = []
    story_ids = [str(row.get("story_id", "")) for row in stories]
    family_ids = {str(row.get("family_id", "")) for row in stories}
    if len(stories) != 60 or len(story_ids) != len(set(story_ids)):
        errors.append("stories must contain 60 unique story ids")
    if len(family_ids) != 15:
        errors.append("stories must contain 15 unique families")
    if {str(row.get("mechanism", "")) for row in stories} != EXPECTED_MECHANISMS:
        errors.append("mechanism set drifted")
    if {item.get("id") for item in dimensions.get("dimensions", [])} != EXPECTED_DIMENSIONS:
        errors.append("dimension set drifted")
    if dimensions.get("scale", {}).get("allowed_values") != [-3, -2, -1, 0, 1, 2, 3]:
        errors.append("rating scale drifted")
    for review_key in ("native_speaker_review", "research_ethics_review"):
        review = review_status.get(review_key, {})
        if review.get("complete") is not False or review.get("reviewer_ids") != []:
            errors.append(f"{review_key}: template must remain incomplete with no reviewer ids")

    families_by_split: dict[str, set[str]] = defaultdict(set)
    family_language: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    translation_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for story in stories:
        story_id = str(story.get("story_id", ""))
        family_id = str(story.get("family_id", ""))
        split = str(story.get("split", ""))
        language = str(story.get("language", ""))
        trajectory = str(story.get("trajectory", ""))
        sentences = story.get("sentences")
        families_by_split[split].add(family_id)
        family_language[(family_id, language)].append(story)
        translation_groups[str(story.get("translation_group_id", ""))].append(story)
        if language not in {"en", "zh-Hans"} or trajectory not in {"reveal_late", "known_early"}:
            errors.append(f"{story_id}: language or trajectory drifted")
        if story.get("translation_status") != "bilingual_draft_unreviewed":
            errors.append(f"{story_id}: translation status must remain unreviewed")
        if story.get("needs_native_speaker_review") is not True:
            errors.append(f"{story_id}: missing native-speaker review flag")
        if story.get("needs_research_ethics_review") is not True:
            errors.append(f"{story_id}: missing research-ethics review flag")
        if not isinstance(sentences, list) or len(sentences) != 6:
            errors.append(f"{story_id}: expected six sentences")
            continue
        indices = [item.get("sentence_index") for item in sentences]
        if indices != [1, 2, 3, 4, 5, 6]:
            errors.append(f"{story_id}: sentence indices drifted")
        roles = {str(item.get("checkpoint_role", "")) for item in sentences}
        if roles != {"context", "apparent_act", "evidence", "revelation", "response", "endpoint_summary"}:
            errors.append(f"{story_id}: checkpoint roles drifted")
        revelation_indices = [item["sentence_index"] for item in sentences if item.get("is_revelation")]
        expected_revelation = [4] if trajectory == "reveal_late" else [2]
        if revelation_indices != expected_revelation:
            errors.append(f"{story_id}: revelation position drifted")
        if sentences[-1].get("checkpoint_role") != "endpoint_summary":
            errors.append(f"{story_id}: final sentence is not the endpoint summary")
        text = " ".join(str(item.get("text", "")) for item in sentences)
        if not text.strip() or "TODO" in text:
            errors.append(f"{story_id}: empty text or TODO marker")
        if language == "zh-Hans" and not CJK_RE.search(text):
            errors.append(f"{story_id}: Chinese record contains no CJK text")
        if language == "en" and CJK_RE.search(text):
            errors.append(f"{story_id}: English record contains CJK text")

    if {key: len(value) for key, value in families_by_split.items()} != {
        "train": 5,
        "validation": 5,
        "test": 5,
    }:
        errors.append("family split must be 5/5/5")
    for mechanism in EXPECTED_MECHANISMS:
        for split in ("train", "validation", "test"):
            matching = {
                str(row["family_id"])
                for row in stories
                if row.get("mechanism") == mechanism and row.get("split") == split
            }
            if len(matching) != 1:
                errors.append(f"{mechanism}/{split}: expected exactly one family")

    for (family_id, language), pair in family_language.items():
        if len(pair) != 2 or {row.get("trajectory") for row in pair} != {"reveal_late", "known_early"}:
            errors.append(f"{family_id}/{language}: trajectory pair is incomplete")
            continue
        by_trajectory = {str(row["trajectory"]): row for row in pair}
        late = by_trajectory["reveal_late"]["sentences"]
        early = by_trajectory["known_early"]["sentences"]
        if Counter(item["text"] for item in late) != Counter(item["text"] for item in early):
            errors.append(f"{family_id}/{language}: reveal orders do not contain the same sentence multiset")
        if {item["event_id"]: item["text"] for item in late} != {
            item["event_id"]: item["text"] for item in early
        }:
            errors.append(f"{family_id}/{language}: event text drifted across trajectories")
        if late[-1]["text"] != early[-1]["text"]:
            errors.append(f"{family_id}/{language}: endpoint summaries differ")

    for group_id, pair in translation_groups.items():
        if len(pair) != 2 or {row.get("language") for row in pair} != {"en", "zh-Hans"}:
            errors.append(f"{group_id}: bilingual pair is incomplete")
            continue
        by_language = {str(row["language"]): row for row in pair}
        en_events = [item["event_id"] for item in by_language["en"]["sentences"]]
        zh_events = [item["event_id"] for item in by_language["zh-Hans"]["sentences"]]
        if en_events != zh_events:
            errors.append(f"{group_id}: bilingual event order drifted")

    expected_rating_units = {
        f"{story['story_id']}__s{sentence['sentence_index']:02d}__{dimension}"
        for story in stories
        for sentence in story["sentences"]
        for dimension in EXPECTED_DIMENSIONS
    }
    observed_rating_units = {str(row.get("unit_id", "")) for row in ratings}
    if len(ratings) != 2880 or observed_rating_units != expected_rating_units:
        errors.append("rating template is not the exact 2,880-unit story/checkpoint/dimension grid")
    for row in ratings:
        unit_id = str(row.get("unit_id", ""))
        if row.get("ratings") != [] or row.get("aggregate") is not None:
            errors.append(f"{unit_id}: human labels must remain empty in the template")
        if row.get("label_status") != "awaiting_human_annotation":
            errors.append(f"{unit_id}: label status drifted")
        if row.get("needs_research_ethics_review") is not True:
            errors.append(f"{unit_id}: research-ethics review flag missing")
        if row.get("needs_native_speaker_review") is not True:
            errors.append(f"{unit_id}: native-speaker review flag missing")

    expected_hashes = manifest.get("files", {})
    for name, path in (
        ("stories.jsonl", stories_path),
        ("human_ratings_template.jsonl", ratings_path),
        ("dimensions.json", dimensions_path),
        ("review_status.json", review_status_path),
    ):
        if expected_hashes.get(name) != sha256_file(path):
            errors.append(f"manifest hash mismatch: {name}")
    if manifest.get("human_labels_complete") is not False:
        errors.append("manifest must keep human_labels_complete false")
    if manifest.get("native_speaker_review_complete") is not False:
        errors.append("manifest must keep native_speaker_review_complete false")
    if manifest.get("research_ethics_review_complete") is not False:
        errors.append("manifest must keep research_ethics_review_complete false")
    if manifest.get("license_status") != "needs_owner_decision":
        errors.append("dataset license must remain explicitly unresolved until the owner selects one")

    report = {
        "schema_version": "moral_hysteresis_validation_v1",
        "dataset_dir": dataset_dir.as_posix(),
        "stories": len(stories),
        "families": len(family_ids),
        "rating_rows": len(ratings),
        "errors": errors,
        "passed": not errors,
    }
    if errors:
        raise ValueError(json.dumps(report, indent=2))
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", default=str(ROOT / "dataset"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(validate(Path(args.dataset_dir).resolve()), indent=2))
