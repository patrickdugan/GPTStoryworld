#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if raw:
            rows.append(json.loads(raw))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def append_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": now_iso(), **payload}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def tokenize(row: dict[str, Any]) -> list[str]:
    meta = row.get("meta", {}) if isinstance(row.get("meta"), dict) else {}
    text = " ".join(
        [
            str(row.get("state", "")),
            " ".join(str(tool) for tool in row.get("tools", []) if str(tool)),
            str(meta.get("role_id", "")),
            str(meta.get("failure_mode", "")),
            str(meta.get("world_archetype", "")),
        ]
    )
    return [tok.lower() for tok in TOKEN_RE.findall(text)]


def role_id(row: dict[str, Any]) -> str:
    meta = row.get("meta", {}) if isinstance(row.get("meta"), dict) else {}
    return str(meta.get("role_id") or "unknown_role")


def train_role_models(rows: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    models: dict[str, Any] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[role_id(row)].append(row)
    for role, role_rows in grouped.items():
        label_counts: Counter[str] = Counter()
        token_counts: dict[str, Counter[str]] = defaultdict(Counter)
        total_tokens: Counter[str] = Counter()
        vocab: set[str] = set()
        for row in role_rows:
            label = str(row.get("action", "") or "")
            label_counts[label] += 1
            tokens = tokenize(row)
            token_counts[label].update(tokens)
            total_tokens[label] += len(tokens)
            vocab.update(tokens)
        models[role] = {
            "row_count": len(role_rows),
            "alpha": alpha,
            "labels": sorted(label_counts),
            "label_counts": dict(label_counts),
            "vocab_size": len(vocab),
            "total_tokens": dict(total_tokens),
            "token_counts": {label: dict(counts) for label, counts in token_counts.items()},
        }
    return models


def score_label(model: dict[str, Any], tokens: list[str], label: str) -> float:
    labels = list(model["labels"])
    label_count = float(model["label_counts"].get(label, 0))
    total_rows = float(sum(model["label_counts"].values()))
    alpha = float(model["alpha"])
    score = math.log((label_count + alpha) / (total_rows + alpha * max(1, len(labels))))
    vocab_size = max(1, int(model["vocab_size"]))
    total = float(model["total_tokens"].get(label, 0))
    counts = model["token_counts"].get(label, {})
    denom = total + alpha * vocab_size
    for tok in tokens:
        score += math.log((float(counts.get(tok, 0)) + alpha) / denom)
    return score


def predict(models: dict[str, Any], row: dict[str, Any]) -> tuple[str, dict[str, float]]:
    role = role_id(row)
    model = models.get(role)
    if not model:
        tools = [str(tool) for tool in row.get("tools", []) if str(tool)]
        return (tools[0] if tools else "WAIT"), {}
    candidate_labels = [label for label in model["labels"] if label in set(row.get("tools", []))]
    if not candidate_labels:
        candidate_labels = list(model["labels"])
    tokens = tokenize(row)
    scores = {label: score_label(model, tokens, label) for label in candidate_labels}
    return max(scores.items(), key=lambda item: item[1])[0], scores


def top_features(model: dict[str, Any], limit: int) -> dict[str, list[list[Any]]]:
    out: dict[str, list[list[Any]]] = {}
    for label, counts in model["token_counts"].items():
        out[label] = [[tok, count] for tok, count in Counter(counts).most_common(limit)]
    return out


def evaluate(models: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    total = 0
    correct = 0
    per_role: dict[str, Counter[str]] = defaultdict(Counter)
    confusion: Counter[str] = Counter()
    predictions: list[dict[str, Any]] = []
    for row in rows:
        gold = str(row.get("action", "") or "")
        pred, scores = predict(models, row)
        ok = pred == gold
        total += 1
        correct += int(ok)
        role = role_id(row)
        per_role[role]["total"] += 1
        per_role[role]["correct"] += int(ok)
        confusion[f"{gold}->{pred}"] += 1
        meta = row.get("meta", {}) if isinstance(row.get("meta"), dict) else {}
        predictions.append(
            {
                "trajectory_id": meta.get("trajectory_id"),
                "role_id": role,
                "gold": gold,
                "predicted": pred,
                "ok": ok,
                "scores": scores,
            }
        )
    per_role_report = {
        role: {
            "total": counts["total"],
            "correct": counts["correct"],
            "accuracy": round(counts["correct"] / max(1, counts["total"]), 4),
        }
        for role, counts in sorted(per_role.items())
    }
    report = {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / max(1, total), 4),
        "per_role": per_role_report,
        "confusion": dict(sorted(confusion.items())),
    }
    return report, predictions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train tiny per-role control classifiers for the 9-TRM mesh corpus.")
    parser.add_argument("--train", default="hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed/train.jsonl")
    parser.add_argument("--val", default="hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed/val.jsonl")
    parser.add_argument("--out-dir", default="hermes-skills/storyworld-conveyor/trm_runs/encounter_assembly_9trm_tiny_mesh")
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--top-features", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = out_dir / "events.jsonl"
    append_event(events_path, {"event": "start", "train": args.train, "val": args.val})
    train_rows = iter_jsonl(Path(args.train).resolve())
    val_rows = iter_jsonl(Path(args.val).resolve())
    append_event(events_path, {"event": "loaded_rows", "train_rows": len(train_rows), "val_rows": len(val_rows)})
    models = train_role_models(train_rows, alpha=float(args.alpha))
    eval_report, predictions = evaluate(models, val_rows)
    model_summary = {
        "created_at": now_iso(),
        "model_type": "per_role_multinomial_naive_bayes_control_policy",
        "train_rows": len(train_rows),
        "val_rows": len(val_rows),
        "roles": {
            role: {
                "row_count": model["row_count"],
                "labels": model["labels"],
                "label_counts": model["label_counts"],
                "vocab_size": model["vocab_size"],
                "top_features": top_features(model, int(args.top_features)),
            }
            for role, model in sorted(models.items())
        },
    }
    write_json(out_dir / "model.json", models)
    write_json(out_dir / "model_summary.json", model_summary)
    write_json(out_dir / "eval.json", eval_report)
    write_jsonl(out_dir / "predictions.jsonl", predictions)
    append_event(events_path, {"event": "completed", "accuracy": eval_report["accuracy"], "correct": eval_report["correct"], "total": eval_report["total"]})
    print(str(out_dir))
    print(str(out_dir / "eval.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
