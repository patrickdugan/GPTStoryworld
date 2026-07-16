#!/usr/bin/env python3
"""Analyze bilingual activation trajectories and gated moral-dimension probes."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = ROOT / "dataset"
ALLOWED_RATINGS = {-3, -2, -1, 0, 1, 2, 3}
MIN_ANNOTATORS = 3
RELIABILITY_GATE = 0.80
PROBE_VALIDITY_GATE = 0.50
RIDGE_ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)


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


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def clustered_mean(
    values_by_family: dict[str, list[float]], samples: int, seed: int
) -> dict[str, Any]:
    if not values_by_family:
        return {"estimate": None, "ci_95_percentile": [None, None], "families": 0, "observations": 0}
    family_ids = sorted(values_by_family)
    family_means = {key: fmean(values_by_family[key]) for key in family_ids}
    estimate = fmean(family_means.values())
    rng = random.Random(seed)
    draws = [
        fmean(family_means[rng.choice(family_ids)] for _ in family_ids)
        for _ in range(samples)
    ]
    return {
        "estimate": estimate,
        "ci_95_percentile": [percentile(draws, 0.025), percentile(draws, 0.975)],
        "families": len(family_ids),
        "observations": sum(len(values) for values in values_by_family.values()),
        "bootstrap_samples": samples,
        "cluster_weighting": "equal_weight_per_story_family",
    }


def cosine_distance(first, second, np) -> float:
    first = np.asarray(first, dtype=np.float64)
    second = np.asarray(second, dtype=np.float64)
    denominator = float(np.linalg.norm(first) * np.linalg.norm(second))
    if denominator == 0.0:
        return 0.0
    return 1.0 - float(np.dot(first, second) / denominator)


def linear_cka(first, second, np) -> float:
    first = np.asarray(first, dtype=np.float64)
    second = np.asarray(second, dtype=np.float64)
    first = first - first.mean(axis=0, keepdims=True)
    second = second - second.mean(axis=0, keepdims=True)
    first_gram = first @ first.T
    second_gram = second @ second.T
    numerator = float((first_gram * second_gram).sum())
    denominator = float(np.linalg.norm(first_gram) * np.linalg.norm(second_gram))
    return numerator / denominator if denominator else 0.0


def pearson(first, second, np) -> float:
    first = np.asarray(first, dtype=np.float64)
    second = np.asarray(second, dtype=np.float64)
    if first.size < 2 or float(first.std()) == 0.0 or float(second.std()) == 0.0:
        return 0.0
    return float(np.corrcoef(first, second)[0, 1])


def load_capture(
    capture_dir: Path,
    stories: dict[str, dict[str, Any]],
    stories_path: Path,
    np,
):
    manifest_path = capture_dir / "capture_manifest.json"
    manifest = read_json(manifest_path)
    if manifest.get("schema_version") != "moral_hysteresis_capture_manifest_v1":
        raise ValueError("unsupported capture manifest schema")
    dataset_hash = sha256_file(stories_path)
    if manifest.get("dataset", {}).get("stories_sha256") != dataset_hash:
        raise ValueError("capture dataset hash does not match the checked corpus")
    records = manifest.get("records")
    if not isinstance(records, list) or {row.get("story_id") for row in records} != set(stories):
        raise ValueError("capture records must cover the complete checked corpus")

    arrays: dict[str, Any] = {}
    tail_arrays: dict[str, Any] = {}
    expected_shape = None
    for record in records:
        story_id = str(record["story_id"])
        record_path = (capture_dir / str(record["path"])).resolve()
        if not record_path.is_relative_to(capture_dir.resolve()):
            raise ValueError(f"{story_id}: capture path escapes the capture directory")
        if sha256_file(record_path) != record.get("sha256"):
            raise ValueError(f"{story_id}: activation file hash mismatch")
        with np.load(record_path, allow_pickle=False) as payload:
            if "hidden_states" not in payload:
                raise ValueError(f"{story_id}: hidden_states array is missing")
            hidden_states = payload["hidden_states"]
            if "tail_mean_hidden_states" not in payload:
                raise ValueError(f"{story_id}: tail_mean_hidden_states robustness array is missing")
            tail_mean_hidden_states = payload["tail_mean_hidden_states"]
        if hidden_states.ndim != 3 or hidden_states.shape[0] != 6:
            raise ValueError(f"{story_id}: hidden_states must have shape [6, layers, hidden]")
        shape = tuple(int(item) for item in hidden_states.shape)
        if list(shape) != record.get("shape"):
            raise ValueError(f"{story_id}: activation shape does not match manifest")
        if tail_mean_hidden_states.shape != hidden_states.shape:
            raise ValueError(f"{story_id}: tail-mean activation shape drifted")
        if expected_shape is None:
            expected_shape = shape
        elif shape != expected_shape:
            raise ValueError(f"{story_id}: activation shape drifted")
        arrays[story_id] = hidden_states
        tail_arrays[story_id] = tail_mean_hidden_states
    return manifest, arrays, tail_arrays, expected_shape


def review_gates(review_status: dict[str, Any]) -> dict[str, bool]:
    output = {}
    for key in ("native_speaker_review", "research_ethics_review"):
        record = review_status.get(key, {})
        output[f"{key}_complete"] = bool(record.get("complete")) and bool(record.get("reviewer_ids"))
    return output


def interval_alpha(units: Sequence[Sequence[float]]) -> float | None:
    pair_disagreements = []
    all_values = []
    for unit in units:
        all_values.extend(unit)
        for first_index in range(len(unit)):
            for second_index in range(first_index + 1, len(unit)):
                pair_disagreements.append((unit[first_index] - unit[second_index]) ** 2)
    if not pair_disagreements or len(all_values) < 2:
        return None
    expected = [
        (all_values[first_index] - all_values[second_index]) ** 2
        for first_index in range(len(all_values))
        for second_index in range(first_index + 1, len(all_values))
    ]
    expected_disagreement = fmean(expected)
    if expected_disagreement == 0.0:
        return 1.0 if fmean(pair_disagreements) == 0.0 else None
    return 1.0 - fmean(pair_disagreements) / expected_disagreement


def assess_labels(
    rating_rows: Sequence[dict[str, Any]], expected_units: set[tuple[str, int, str]]
) -> tuple[dict[str, Any], dict[tuple[str, int, str], float]]:
    observed_units: set[tuple[str, int, str]] = set()
    units_by_dimension: dict[str, list[list[float]]] = defaultdict(list)
    targets: dict[tuple[str, int, str], float] = {}
    problems = []
    for row in rating_rows:
        key = (str(row.get("story_id", "")), int(row.get("sentence_index", 0)), str(row.get("dimension", "")))
        if key in observed_units:
            problems.append(f"{row.get('unit_id')}: duplicate rating unit")
        observed_units.add(key)
        ratings = row.get("ratings")
        if row.get("label_status") != "complete" or not isinstance(ratings, list) or len(ratings) < MIN_ANNOTATORS:
            problems.append(f"{row.get('unit_id')}: incomplete")
            continue
        annotator_ids = [str(item.get("annotator_id", "")).strip() for item in ratings if isinstance(item, dict)]
        values = [item.get("value") for item in ratings if isinstance(item, dict)]
        if (
            len(annotator_ids) != len(ratings)
            or not all(annotator_ids)
            or len(set(annotator_ids)) != len(annotator_ids)
            or not all(isinstance(value, int) and value in ALLOWED_RATINGS for value in values)
        ):
            problems.append(f"{row.get('unit_id')}: malformed ratings")
            continue
        numeric = [float(value) for value in values]
        units_by_dimension[key[2]].append(numeric)
        targets[key] = fmean(numeric)
    if observed_units != expected_units:
        problems.append("rating unit grid does not match the checked corpus")
    if len(rating_rows) != len(expected_units):
        problems.append("rating row count does not match the checked corpus")

    reliability = {
        dimension: interval_alpha(units_by_dimension.get(dimension, []))
        for dimension in sorted({key[2] for key in expected_units})
    }
    complete = not problems and len(targets) == len(expected_units)
    reliability_pass = complete and all(
        value is not None and value >= RELIABILITY_GATE for value in reliability.values()
    )
    return (
        {
            "complete": complete,
            "minimum_annotators_per_unit": MIN_ANNOTATORS,
            "expected_units": len(expected_units),
            "usable_units": len(targets),
            "problems": problems[:20],
            "problems_total": len(problems),
            "reliability_metric": "Krippendorff_alpha_interval",
            "reliability_gate": RELIABILITY_GATE,
            "reliability_by_dimension": reliability,
            "reliability_pass": reliability_pass,
        },
        targets,
    )


def raw_geometry(
    stories: dict[str, dict[str, Any]],
    arrays: dict[str, Any],
    shape: tuple[int, int, int],
    np,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    _, layer_count, _ = shape
    by_family_language: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    bilingual: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for story_id, story in stories.items():
        by_family_language[(story["family_id"], story["language"])][story["trajectory"]] = story_id
        bilingual[(story["translation_group_id"], story["split"])][story["language"]] = story_id

    layer_reports = []
    for layer in range(layer_count):
        endpoint_by_family: dict[str, list[float]] = defaultdict(list)
        revelation_by_family: dict[str, list[float]] = defaultdict(list)
        ordinary_by_family: dict[str, list[float]] = defaultdict(list)
        for (family_id, _language), pair in by_family_language.items():
            late = arrays[pair["reveal_late"]]
            early = arrays[pair["known_early"]]
            endpoint_by_family[family_id].append(cosine_distance(late[-1, layer], early[-1, layer], np))
        for story_id, story in stories.items():
            states = arrays[story_id]
            revelation_index = next(
                index for index, sentence in enumerate(story["sentences"]) if sentence["is_revelation"]
            )
            revelation_by_family[story["family_id"]].append(
                cosine_distance(states[revelation_index - 1, layer], states[revelation_index, layer], np)
            )
            for index in range(1, 6):
                if index == revelation_index:
                    continue
                ordinary_by_family[story["family_id"]].append(
                    cosine_distance(states[index - 1, layer], states[index, layer], np)
                )

        english = []
        chinese = []
        for (translation_group, split), pair in sorted(bilingual.items()):
            if split != "test":
                continue
            if set(pair) != {"en", "zh-Hans"}:
                raise ValueError(f"{translation_group}: incomplete bilingual capture")
            for sentence_index in range(6):
                english.append(arrays[pair["en"]][sentence_index, layer])
                chinese.append(arrays[pair["zh-Hans"]][sentence_index, layer])
        layer_reports.append(
            {
                "layer_index": layer,
                "endpoint_path_residual_cosine_distance": clustered_mean(
                    endpoint_by_family, bootstrap_samples, seed + layer
                ),
                "revelation_step_cosine_distance": clustered_mean(
                    revelation_by_family, bootstrap_samples, seed + 1000 + layer
                ),
                "non_revelation_step_cosine_distance": clustered_mean(
                    ordinary_by_family, bootstrap_samples, seed + 2000 + layer
                ),
                "heldout_bilingual_linear_cka": linear_cka(english, chinese, np),
                "heldout_bilingual_units": len(english),
            }
        )
    block_layers = list(range(1, layer_count)) if layer_count > 1 else [0]
    third = max(1, len(block_layers) // 3)
    early_layers = block_layers[:third]
    late_layers = block_layers[-third:]
    cka_by_layer = {row["layer_index"]: row["heldout_bilingual_linear_cka"] for row in layer_reports}
    return {
        "semantic_interpretation_allowed": False,
        "distance_metric": "cosine_distance_on_raw_last_token_hidden_state",
        "cross_lingual_metric": "linear_CKA_on_heldout_bilingual_checkpoint_pairs",
        "layers": layer_reports,
        "early_vs_late_cross_lingual_summary": {
            "early_layer_indices": early_layers,
            "late_layer_indices": late_layers,
            "early_mean_cka": fmean(cka_by_layer[index] for index in early_layers),
            "late_mean_cka": fmean(cka_by_layer[index] for index in late_layers),
            "late_minus_early_mean_cka": (
                fmean(cka_by_layer[index] for index in late_layers)
                - fmean(cka_by_layer[index] for index in early_layers)
            ),
            "status": "descriptive_not_confirmatory",
        },
    }


def ridge_fit_predict(train_x, train_y, target_x, alpha: float, np):
    feature_mean = train_x.mean(axis=0)
    feature_scale = train_x.std(axis=0)
    feature_scale[feature_scale < 1e-6] = 1.0
    standardized_train = (train_x - feature_mean) / feature_scale
    standardized_target = (target_x - feature_mean) / feature_scale
    target_mean = float(train_y.mean())
    centered_y = train_y - target_mean
    gram = standardized_train @ standardized_train.T
    coefficients = standardized_train.T @ np.linalg.solve(
        gram + alpha * np.eye(gram.shape[0]), centered_y
    )
    return standardized_target @ coefficients + target_mean


def semantic_probes(
    stories: dict[str, dict[str, Any]],
    arrays: dict[str, Any],
    shape: tuple[int, int, int],
    targets: dict[tuple[str, int, str], float],
    np,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    _, layer_count, _ = shape
    sample_keys = [
        (story_id, sentence_index)
        for story_id in sorted(stories)
        for sentence_index in range(1, 7)
    ]
    split_indices = {
        split: [index for index, (story_id, _) in enumerate(sample_keys) if stories[story_id]["split"] == split]
        for split in ("train", "validation", "test")
    }
    dimensions = sorted({key[2] for key in targets})
    output: dict[str, Any] = {}
    for dimension_index, dimension in enumerate(dimensions):
        labels = np.asarray(
            [targets[(story_id, sentence_index, dimension)] for story_id, sentence_index in sample_keys],
            dtype=np.float64,
        )
        layer_reports = []
        for layer in range(layer_count):
            features = np.stack(
                [arrays[story_id][sentence_index - 1, layer].astype(np.float64) for story_id, sentence_index in sample_keys]
            )
            train_index = split_indices["train"]
            validation_index = split_indices["validation"]
            test_index = split_indices["test"]
            best_alpha = None
            best_validation = float("-inf")
            for alpha in RIDGE_ALPHAS:
                predictions = ridge_fit_predict(
                    features[train_index],
                    labels[train_index],
                    features[validation_index],
                    alpha,
                    np,
                )
                correlation = pearson(predictions, labels[validation_index], np)
                if correlation > best_validation:
                    best_validation = correlation
                    best_alpha = alpha
            all_predictions = ridge_fit_predict(
                features[train_index], labels[train_index], features, float(best_alpha), np
            )
            test_predictions = all_predictions[test_index]
            endpoint_by_family: dict[str, list[float]] = defaultdict(list)
            revelation_jump_by_family: dict[str, list[float]] = defaultdict(list)
            prediction_map = {
                key: float(all_predictions[index]) for index, key in enumerate(sample_keys)
            }
            pair_map: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
            for story_id, story in stories.items():
                if story["split"] != "test":
                    continue
                pair_map[(story["family_id"], story["language"])][story["trajectory"]] = story_id
                revelation_index = next(
                    sentence["sentence_index"] for sentence in story["sentences"] if sentence["is_revelation"]
                )
                revelation_jump_by_family[story["family_id"]].append(
                    prediction_map[(story_id, revelation_index)]
                    - prediction_map[(story_id, revelation_index - 1)]
                )
            for (family_id, _language), pair in pair_map.items():
                endpoint_by_family[family_id].append(
                    prediction_map[(pair["reveal_late"], 6)]
                    - prediction_map[(pair["known_early"], 6)]
                )
            language_test = {}
            for language in ("en", "zh-Hans"):
                indices = [
                    index
                    for index in test_index
                    if stories[sample_keys[index][0]]["language"] == language
                ]
                language_test[language] = {
                    "pearson_r": pearson(all_predictions[indices], labels[indices], np),
                    "mae": float(np.abs(all_predictions[indices] - labels[indices]).mean()),
                    "units": len(indices),
                }
            layer_reports.append(
                {
                    "layer_index": layer,
                    "ridge_alpha_selected_on_validation": best_alpha,
                    "validation_pearson_r": best_validation,
                    "heldout_test_pearson_r": pearson(test_predictions, labels[test_index], np),
                    "heldout_test_mae": float(np.abs(test_predictions - labels[test_index]).mean()),
                    "heldout_by_language": language_test,
                    "endpoint_hysteresis_late_minus_known_early": clustered_mean(
                        endpoint_by_family,
                        bootstrap_samples,
                        seed + dimension_index * 10000 + layer,
                    ),
                    "revelation_jump": clustered_mean(
                        revelation_jump_by_family,
                        bootstrap_samples,
                        seed + dimension_index * 10000 + 1000 + layer,
                    ),
                }
            )
        selected_layer = max(
            layer_reports,
            key=lambda row: (row["validation_pearson_r"], -row["layer_index"]),
        )
        selected_summary = {
            key: value for key, value in selected_layer.items() if key != "validation_pearson_r"
        }
        selected_summary["validation_pearson_r"] = selected_layer["validation_pearson_r"]
        selected_summary["selection_rule"] = "maximum_validation_pearson_then_lowest_layer_index"
        selected_summary["heldout_probe_validity_gate"] = PROBE_VALIDITY_GATE
        selected_summary["heldout_probe_valid"] = (
            selected_layer["heldout_test_pearson_r"] >= PROBE_VALIDITY_GATE
        )
        output[dimension] = {
            "confirmatory_validation_selected_layer": selected_summary,
            "layers_exploratory": layer_reports,
        }
    all_dimension_probes_valid = all(
        report["confirmatory_validation_selected_layer"]["heldout_probe_valid"]
        for report in output.values()
    )
    return {
        "status": "human_label_gate_passed",
        "probe": "ridge_regression_fit_on_train_families_alpha_selected_on_validation_families",
        "heldout_unit": "story_family",
        "heldout_probe_validity_gate": PROBE_VALIDITY_GATE,
        "all_dimension_probes_valid": all_dimension_probes_valid,
        "dimensions": output,
    }


def analyze(
    capture_dir: Path,
    dataset_dir: Path = DEFAULT_DATASET,
    ratings_path: Path | None = None,
    review_status_path: Path | None = None,
    bootstrap_samples: int = 5000,
    seed: int = 20260715,
) -> dict[str, Any]:
    if bootstrap_samples < 100:
        raise ValueError("bootstrap_samples must be at least 100")
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - dependency belongs to analysis environment
        raise RuntimeError("numpy is required for activation analysis") from exc
    stories_path = dataset_dir / "stories.jsonl"
    dataset_manifest = read_json(dataset_dir / "manifest.json")
    dataset_license_resolved = dataset_manifest.get("license_status") not in {
        None,
        "",
        "needs_owner_decision",
        "unresolved",
    }
    stories = {str(row["story_id"]): row for row in read_jsonl(stories_path)}
    if len(stories) != 60:
        raise ValueError("analysis requires the complete 60-story corpus")
    manifest, arrays, tail_arrays, shape = load_capture(capture_dir, stories, stories_path, np)
    ratings_file = ratings_path or (dataset_dir / "human_ratings_template.jsonl")
    review_file = review_status_path or (dataset_dir / "review_status.json")
    rating_rows = read_jsonl(ratings_file)
    expected_units = {
        (story_id, sentence["sentence_index"], dimension)
        for story_id, story in stories.items()
        for sentence in story["sentences"]
        for dimension in (
            "blame",
            "harmful_intent",
            "consent",
            "harm",
            "responsibility",
            "deserved_punishment",
            "forgiveness",
            "trust",
        )
    }
    label_report, targets = assess_labels(rating_rows, expected_units)
    reviews = review_gates(read_json(review_file))
    raw = {
        "primary_last_token": raw_geometry(
            stories, arrays, shape, np, bootstrap_samples, seed
        ),
        "robustness_last_four_token_mean": raw_geometry(
            stories, tail_arrays, shape, np, bootstrap_samples, seed + 50000
        ),
        "robustness_rationale": (
            "Tail-mean capture reduces sensitivity to language-specific sentence-final tokenization."
        ),
    }
    semantic = {"status": "blocked_pending_human_labels", "dimensions": {}}
    if label_report["complete"] and label_report["reliability_pass"]:
        semantic = semantic_probes(
            stories,
            arrays,
            shape,
            targets,
            np,
            bootstrap_samples,
            seed,
        )
    capture_gates = manifest.get("publication_gates", {})
    publication_ready = bool(
        capture_gates.get("model_revision_pinned")
        and capture_gates.get("all_requested_records_captured")
        and capture_gates.get("tail_mean_robustness_capture_complete")
        and label_report["complete"]
        and label_report["reliability_pass"]
        and reviews["native_speaker_review_complete"]
        and reviews["research_ethics_review_complete"]
        and semantic.get("all_dimension_probes_valid")
        and dataset_license_resolved
    )
    return {
        "schema_version": "moral_hysteresis_analysis_v1",
        "title": "Moral Hysteresis: How Language Models Revise Blame After a Narrative Twist",
        "capture_manifest_sha256": sha256_file(capture_dir / "capture_manifest.json"),
        "dataset_stories_sha256": sha256_file(stories_path),
        "activation_shape_per_story": list(shape),
        "bootstrap": {
            "samples": bootstrap_samples,
            "seed": seed,
            "cluster_unit": "story_family",
        },
        "human_labels": label_report,
        "review_gates": reviews,
        "raw_geometry": raw,
        "semantic_moral_probes": semantic,
        "publication_gates": {
            "model_revision_pinned": bool(capture_gates.get("model_revision_pinned")),
            "complete_activation_capture": bool(capture_gates.get("all_requested_records_captured")),
            "tail_mean_robustness_capture_complete": bool(
                capture_gates.get("tail_mean_robustness_capture_complete")
            ),
            "human_labels_complete": label_report["complete"],
            "inter_rater_reliability_pass": label_report["reliability_pass"],
            "all_dimension_probes_valid": bool(semantic.get("all_dimension_probes_valid")),
            "dataset_license_resolved": dataset_license_resolved,
            **reviews,
            "publication_ready": publication_ready,
        },
        "interpretation_limits": [
            "Raw activation distances and CKA do not identify blame, intent, consent, or any other moral dimension.",
            "A nonzero endpoint residual is called moral hysteresis only when a reliable held-out moral probe measures it.",
            "Late-layer cross-lingual convergence is a hypothesis; the early-versus-late CKA summary is descriptive.",
            "The protocol does not expose or retain generated chain-of-thought text.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", required=True)
    parser.add_argument("--dataset-dir", default=str(DEFAULT_DATASET))
    parser.add_argument("--ratings", default="")
    parser.add_argument("--review-status", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260715)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    report = analyze(
        Path(args.capture_dir).resolve(),
        Path(args.dataset_dir).resolve(),
        Path(args.ratings).resolve() if args.ratings else None,
        Path(args.review_status).resolve() if args.review_status else None,
        args.bootstrap_samples,
        args.seed,
    )
    output = Path(args.output).resolve()
    write_json(output, report)
    print(json.dumps({
        "output": output.as_posix(),
        "publication_ready": report["publication_gates"]["publication_ready"],
        "semantic_probe_status": report["semantic_moral_probes"]["status"],
    }, indent=2))
