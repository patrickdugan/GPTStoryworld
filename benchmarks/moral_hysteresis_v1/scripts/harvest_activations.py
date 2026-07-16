#!/usr/bin/env python3
"""Harvest last-token hidden states after each Moral Hysteresis sentence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORIES = ROOT / "dataset" / "stories.jsonl"
SAFE_FILE_RE = re.compile(r"[^a-zA-Z0-9_.-]+")
UNPINNED_REVISIONS = {"", "main", "master", "latest"}


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


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def story_prefixes(story: dict[str, Any]) -> list[str]:
    prefixes = []
    accumulated: list[str] = []
    for sentence in story.get("sentences", []):
        text = str(sentence.get("text", "")).strip()
        if not text:
            raise ValueError(f"{story.get('story_id')}: empty sentence")
        accumulated.append(text)
        prefixes.append(" ".join(accumulated))
    if len(prefixes) != 6:
        raise ValueError(f"{story.get('story_id')}: expected six sentence prefixes")
    return prefixes


def select_stories(
    stories: Iterable[dict[str, Any]], languages: set[str], max_stories: int
) -> list[dict[str, Any]]:
    selected = [story for story in stories if not languages or story.get("language") in languages]
    selected.sort(key=lambda row: str(row.get("story_id", "")))
    if max_stories > 0:
        selected = selected[:max_stories]
    if not selected:
        raise ValueError("story selection is empty")
    return selected


def capture_plan(stories_path: Path, stories: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "moral_hysteresis_capture_plan_v1",
        "stories_path": stories_path.as_posix(),
        "stories_sha256": sha256_file(stories_path),
        "stories": len(stories),
        "sentence_prefixes_per_story": 6,
        "total_forward_passes": len(stories) * 6,
        "languages": dict(sorted(Counter(row["language"] for row in stories).items())),
        "splits": dict(sorted(Counter(row["split"] for row in stories).items())),
        "extraction_point": "last input token after each cumulative sentence prefix",
        "requires_local_internal_access": True,
        "api_response_is_not_sufficient": True,
    }


def torch_dtype(name: str, torch_module):
    if name == "auto":
        return "auto"
    return {
        "bfloat16": torch_module.bfloat16,
        "float16": torch_module.float16,
        "float32": torch_module.float32,
    }[name]


def harvest(args: argparse.Namespace) -> dict[str, Any]:
    stories_path = Path(args.stories).resolve()
    output_dir = Path(args.output_dir).resolve()
    stories = select_stories(read_jsonl(stories_path), set(args.languages or []), args.max_stories)
    plan = capture_plan(stories_path, stories)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        write_json(output_dir / "capture_plan.json", plan)
        return {**plan, "dry_run": True, "output": (output_dir / "capture_plan.json").as_posix()}

    model_id = str(args.model_id or os.environ.get("MORAL_HYSTERESIS_MODEL", "")).strip()
    revision = str(args.revision or "").strip()
    if not model_id:
        raise ValueError("--model-id or MORAL_HYSTERESIS_MODEL is required")
    if args.tail_tokens < 1:
        raise ValueError("--tail-tokens must be positive")
    if revision in UNPINNED_REVISIONS and not args.allow_unpinned_revision:
        raise ValueError("a pinned model revision is required; mutable main/master/latest revisions are rejected")

    try:
        import numpy as np
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:  # pragma: no cover - exercised only in activation environments
        raise RuntimeError("install the benchmark activation requirements before harvesting") from exc

    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        revision=revision,
        trust_remote_code=args.trust_remote_code,
        cache_dir=args.cache_dir or None,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        revision=revision,
        trust_remote_code=args.trust_remote_code,
        cache_dir=args.cache_dir or None,
        device_map=args.device_map,
        torch_dtype=torch_dtype(args.dtype, torch),
        low_cpu_mem_usage=True,
    )
    model.eval()
    input_device = model.get_input_embeddings().weight.device
    config_dict = model.config.to_dict()
    resolved_revision = str(getattr(model.config, "_commit_hash", "") or revision)
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    records = []
    expected_shape: tuple[int, int] | None = None
    storage_dtype = np.float16 if args.storage_dtype == "float16" else np.float32

    with torch.inference_mode():
        for story in stories:
            prefix_states = []
            tail_mean_states = []
            token_counts = []
            last_token_ids = []
            for prefix in story_prefixes(story):
                encoded = tokenizer(prefix, return_tensors="pt", add_special_tokens=True)
                encoded = {key: value.to(input_device) for key, value in encoded.items()}
                outputs = model(**encoded, output_hidden_states=True, use_cache=False, return_dict=True)
                hidden_states = outputs.hidden_states
                if not hidden_states:
                    raise RuntimeError("model did not return hidden_states")
                stacked = torch.stack([layer[0, -1, :].detach().float().cpu() for layer in hidden_states])
                tail_count = min(args.tail_tokens, int(encoded["input_ids"].shape[-1]))
                tail_stacked = torch.stack(
                    [layer[0, -tail_count:, :].mean(dim=0).detach().float().cpu() for layer in hidden_states]
                )
                current_shape = (int(stacked.shape[0]), int(stacked.shape[1]))
                if expected_shape is None:
                    expected_shape = current_shape
                elif current_shape != expected_shape:
                    raise RuntimeError(f"hidden-state shape drifted from {expected_shape} to {current_shape}")
                prefix_states.append(stacked.numpy().astype(storage_dtype, copy=False))
                tail_mean_states.append(tail_stacked.numpy().astype(storage_dtype, copy=False))
                token_counts.append(int(encoded["input_ids"].shape[-1]))
                last_token_ids.append(int(encoded["input_ids"][0, -1].item()))

            safe_id = SAFE_FILE_RE.sub("_", str(story["story_id"]))
            record_path = records_dir / f"{safe_id}.npz"
            np.savez_compressed(
                record_path,
                hidden_states=np.stack(prefix_states, axis=0),
                tail_mean_hidden_states=np.stack(tail_mean_states, axis=0),
                sentence_indices=np.arange(1, 7, dtype=np.int16),
                token_counts=np.asarray(token_counts, dtype=np.int32),
                last_token_ids=np.asarray(last_token_ids, dtype=np.int32),
            )
            records.append(
                {
                    "story_id": story["story_id"],
                    "family_id": story["family_id"],
                    "split": story["split"],
                    "trajectory": story["trajectory"],
                    "language": story["language"],
                    "path": record_path.relative_to(output_dir).as_posix(),
                    "sha256": sha256_file(record_path),
                    "shape": [6, expected_shape[0], expected_shape[1]],
                    "dtype": args.storage_dtype,
                    "token_counts": token_counts,
                }
            )

    pinned_revision = revision not in UNPINNED_REVISIONS
    manifest = {
        "schema_version": "moral_hysteresis_capture_manifest_v1",
        "dataset": {
            "stories_path": stories_path.as_posix(),
            "stories_sha256": sha256_file(stories_path),
            "story_count": len(stories),
        },
        "model": {
            "model_id": model_id,
            "requested_revision": revision,
            "resolved_revision": resolved_revision,
            "revision_is_pinned": pinned_revision,
            "config_sha256": stable_hash(config_dict),
            "model_type": str(config_dict.get("model_type", "")),
            "architectures": list(config_dict.get("architectures") or []),
            "trust_remote_code": bool(args.trust_remote_code),
            "tokenizer_class": type(tokenizer).__name__,
            "tokenizer_vocab_size": int(len(tokenizer)),
        },
        "capture": {
            "backend": "transformers_reference",
            "extraction_point": "last input token after each cumulative sentence prefix",
            "hidden_state_axis": "embedding_output_then_transformer_blocks",
            "sentence_prefixes_per_story": 6,
            "layer_count_including_embedding": expected_shape[0] if expected_shape else 0,
            "hidden_size": expected_shape[1] if expected_shape else 0,
            "storage_dtype": args.storage_dtype,
            "tail_mean_tokens": args.tail_tokens,
            "seed": args.seed,
            "raw_text_without_chat_template": True,
        },
        "records": records,
        "software": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "torch": str(torch.__version__),
            "transformers": str(__import__("transformers").__version__),
            "numpy": str(np.__version__),
            "cuda_runtime": str(torch.version.cuda or ""),
            "cuda_devices": [
                torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())
            ],
            "device_map_argument": args.device_map,
            "load_dtype_argument": args.dtype,
        },
        "publication_gates": {
            "model_revision_pinned": pinned_revision,
            "all_requested_records_captured": len(records) == len(stories),
            "tail_mean_robustness_capture_complete": len(records) == len(stories),
            "native_speaker_review_complete": False,
            "human_moral_ratings_complete": False,
        },
        "limitations": [
            "The reference backend is not a substitute for a validated distributed capture stack.",
            "An API completion cannot provide the internal states required by this protocol.",
        ],
    }
    write_json(output_dir / "capture_manifest.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stories", default=str(DEFAULT_STORIES))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-id", default="")
    parser.add_argument("--revision", default="")
    parser.add_argument("--allow-unpinned-revision", action="store_true")
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--dtype", choices=("auto", "bfloat16", "float16", "float32"), default="auto")
    parser.add_argument("--storage-dtype", choices=("float16", "float32"), default="float16")
    parser.add_argument("--tail-tokens", type=int, default=4)
    parser.add_argument("--languages", nargs="*", choices=("en", "zh-Hans"), default=[])
    parser.add_argument("--max-stories", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260715)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    result = harvest(parse_args())
    print(json.dumps({
        "schema_version": result["schema_version"],
        "dry_run": bool(result.get("dry_run", False)),
        "stories": result.get("stories", result.get("dataset", {}).get("story_count")),
        "output": result.get("output", "capture_manifest.json"),
    }, indent=2))
