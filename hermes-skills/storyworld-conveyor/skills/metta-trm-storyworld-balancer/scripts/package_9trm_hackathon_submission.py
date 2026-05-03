#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def copy_if_exists(src: Path, dst: Path) -> str:
    if not src.exists():
        return ""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return str(dst)


def first_jsonl(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if raw:
            return json.loads(raw)
    return {}


def write_readme(path: Path, evidence: dict[str, Any]) -> None:
    corpus = evidence.get("corpus", {})
    training = evidence.get("tiny_training", {})
    demo = evidence.get("storyworld_demo", {})
    path.write_text(
        "# Hermes 9-TRM Creative Skill Mesh Submission Pack\n\n"
        "## One-Sentence Claim\n\n"
        "Hermes skills can make smaller models useful for complex creative-engineering work by decomposing storyworld encounter assembly into MCP memory, MeTTa symbolic state, nine trained control policies, bounded LLM calls, and verifier-backed commit/veto.\n\n"
        "## Evidence\n\n"
        f"- Trajectory rows: {corpus.get('rows')}\n"
        f"- Estimated corpus tokens: {corpus.get('estimated_tokens')}\n"
        f"- Tiny control training accuracy: {training.get('accuracy')}\n"
        f"- Tiny control eval rows: {training.get('total')}\n"
        f"- Whole-context estimate: {demo.get('whole_context_tokens')}\n"
        f"- MCP worst packet tokens: {demo.get('mcp_worst_packet_tokens')}\n"
        f"- MCP overflow count: {demo.get('mcp_overflow_count')}\n"
        f"- Storyworld authoring score delta: {demo.get('authoring_score_delta')}\n\n"
        "## Honest Scope\n\n"
        "The trained model receipt here is a tiny per-role control-policy baseline, not a full neural TRM or QLoRA run. "
        "The important demo is the architecture: small trained control policies decide how to work the LLM inside the skill mesh.\n\n"
        "## Talk Track\n\n"
        "1. A 27B OSS model is too weak and too context-constrained to be the whole storyworld engineer.\n"
        "2. The Hermes skill mesh decomposes the job into nine control roles.\n"
        "3. MCP bounds context, MeTTa gives compact symbolic state, and validators create typed repair targets.\n"
        "4. A tiny trained mesh chooses bounded LLM/tool actions with held-out receipts.\n"
        "5. The result is a viable path for compact models in complex infused skills.\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package the 9-TRM hackathon submission evidence.")
    parser.add_argument("--out-dir", default="hermes-skills/storyworld-conveyor/hackathon_submission/9trm_mesh_current")
    parser.add_argument("--corpus-dir", default="hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed")
    parser.add_argument("--training-dir", default="hermes-skills/storyworld-conveyor/trm_runs/encounter_assembly_9trm_tiny_mesh")
    parser.add_argument("--demo-dir", default="hermes-skills/storyworld-conveyor/tmp/hackathon_storyworld_demo")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    corpus_dir = Path(args.corpus_dir).resolve()
    training_dir = Path(args.training_dir).resolve()
    demo_dir = Path(args.demo_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    corpus_manifest = read_json(corpus_dir / "manifest.json")
    train_manifest = read_json(corpus_dir / "train_manifest.json")
    eval_report = read_json(training_dir / "eval.json")
    demo_summary = read_json(demo_dir / "demo_summary.json")
    demo_baseline = ((demo_summary.get("metta_trm_loop") or {}).get("summary") or {}).get("baseline") or {}
    demo_candidate = ((demo_summary.get("metta_trm_loop") or {}).get("summary") or {}).get("candidate") or {}
    demo_delta = ((demo_summary.get("metta_trm_loop") or {}).get("summary") or {}).get("score_delta") or {}
    budget = (demo_summary.get("mcp_preflight") or {}).get("budget") or {}

    copied = {
        "roadmap": copy_if_exists(REPO_ROOT / "hermes-skills/storyworld-conveyor/HACKATHON_9TRM_DELIVERABLE_ROADMAP.md", out_dir / "roadmap.md"),
        "corpus_readme": copy_if_exists(corpus_dir / "README.md", out_dir / "corpus_README.md"),
        "corpus_manifest": copy_if_exists(corpus_dir / "manifest.json", out_dir / "corpus_manifest.json"),
        "train_manifest": copy_if_exists(corpus_dir / "train_manifest.json", out_dir / "train_manifest.json"),
        "role_action_matrix": copy_if_exists(corpus_dir / "role_action_matrix.csv", out_dir / "role_action_matrix.csv"),
        "training_eval": copy_if_exists(training_dir / "eval.json", out_dir / "tiny_training_eval.json"),
        "training_summary": copy_if_exists(training_dir / "model_summary.json", out_dir / "tiny_model_summary.json"),
        "training_events": copy_if_exists(training_dir / "events.jsonl", out_dir / "tiny_training_events.jsonl"),
        "demo_brief": copy_if_exists(demo_dir / "demo_brief.md", out_dir / "demo_brief.md"),
        "demo_scorecard": copy_if_exists(demo_dir / "demo_scorecard.csv", out_dir / "demo_scorecard.csv"),
        "demo_summary": copy_if_exists(demo_dir / "demo_summary.json", out_dir / "demo_summary.json"),
    }
    write_json(out_dir / "sample_trajectory.json", first_jsonl(corpus_dir / "trajectory_library.jsonl"))
    write_json(out_dir / "sample_prediction.json", first_jsonl(training_dir / "predictions.jsonl"))

    evidence = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "title": "Hermes 9-TRM Creative Skill Mesh",
        "corpus": {
            "rows": corpus_manifest.get("rows"),
            "estimated_tokens": corpus_manifest.get("estimated_tokens"),
            "train_rows": 900,
            "val_rows": 100,
            "neural_trm_manifest_status": train_manifest.get("status"),
        },
        "tiny_training": {
            "model_type": "per_role_multinomial_naive_bayes_control_policy",
            "accuracy": eval_report.get("accuracy"),
            "correct": eval_report.get("correct"),
            "total": eval_report.get("total"),
            "per_role": eval_report.get("per_role"),
        },
        "storyworld_demo": {
            "whole_context_tokens": (demo_summary.get("source_profile") or {}).get("whole_context_token_estimate"),
            "mcp_worst_packet_tokens": budget.get("worst_prompt_tokens"),
            "mcp_overflow_count": budget.get("overflow_count"),
            "baseline_authoring_score": demo_baseline.get("weighted_authoring_verifier_score"),
            "candidate_authoring_score": demo_candidate.get("weighted_authoring_verifier_score"),
            "authoring_score_delta": demo_delta.get("weighted_authoring_verifier_score"),
            "qwen_endpoint": demo_summary.get("qwen_endpoint"),
        },
        "copied_files": copied,
    }
    write_json(out_dir / "evidence_manifest.json", evidence)
    write_readme(out_dir / "README.md", evidence)
    print(str(out_dir))
    print(str(out_dir / "README.md"))
    print(str(out_dir / "evidence_manifest.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
