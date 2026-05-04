#!/usr/bin/env python3
"""
Run a bounded SWMD/MCP secret-route repair probe against a local llama.cpp server.

The job is intentionally control-plane heavy:
- retrieve one encounter target table at a time from an existing valid JSON world
- ask the model for target-only SWMD lines
- sanitize exact ids and allowed consequence targets
- patch only complete, verified consequence lines
- run the existing storyworld validators when available
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ALLOWED_TARGETS = {
    "page_019_rooftop_race",
    "page_020_council_false_order",
    "page_021_final_silence",
    "page_022_under_village_route",
    "page_end_village_witness",
    "page_end_shadow_rank",
    "page_end_council_tool",
    "page_end_merciful_failure",
    "page_end_silent_veil",
}

TARGET_ENCOUNTERS = [
    "page_019_rooftop_race",
    "page_020_council_false_order",
    "page_021_final_silence",
    "page_022_under_village_route",
]

RXN_RE = re.compile(r"^\s*RXN\s+(\S+)\s*->\s*(\S+)\s*$")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ptr_string(text: str) -> dict[str, str]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": text}


def encounter_by_id(world: dict[str, Any], encounter_id: str) -> dict[str, Any]:
    for encounter in world.get("encounters", []) or []:
        if encounter.get("id") == encounter_id:
            return encounter
    raise KeyError(encounter_id)


def make_target_table(encounter: dict[str, Any]) -> str:
    lines = [f"## ENC {encounter['id']} | {encounter.get('title', '')} | turn=19..30"]
    for option in encounter.get("options", []) or []:
        option_text = (option.get("text_script") or {}).get("value", "")
        lines.append(f"OPT {option['id']}: {option_text}")
        for reaction in option.get("reactions", []) or []:
            lines.append(f"  RXN {reaction['id']} -> {reaction.get('consequence_id', '')}")
    return "\n".join(lines)


def make_prompt(encounter: dict[str, Any]) -> str:
    encounter_id = encounter["id"]
    if encounter_id == "page_022_under_village_route":
        rule = (
            "Exactly one reaction may target page_end_silent_veil: the clean vulnerable-witness "
            "reaction. No self-loops. Everything else should terminate in non-secret endings."
        )
    elif encounter_id == "page_021_final_silence":
        rule = (
            "Only clean silence/mercy-preserving reactions may route to page_022_under_village_route. "
            "Do not directly target page_end_silent_veil from this encounter."
        )
    else:
        rule = (
            "Foreshadow the secret route but do not broaden it. Ordinary/compliance/spectacle "
            "failures should terminate or continue through non-secret routes."
        )
    allowed = ", ".join(sorted(ALLOWED_TARGETS))
    return f"""Return ONLY one SWMD target-only patch block. No prose. No T lines.

Allowed targets: {allowed}.

Objective: structurally narrow the overexposed secret path while preserving playability.
Rules:
- Preserve exact ENC, OPT, and RXN ids.
- Emit the encounter header and all OPT/RXN lines below with revised targets.
- Use only allowed targets.
- {rule}

Source:
{make_target_table(encounter)}
"""


def call_model(endpoint: str, model: str, prompt: str, max_tokens: int, temperature: float) -> tuple[str, dict[str, Any]]:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    start = time.time()
    with urllib.request.urlopen(request, timeout=1200) as response:
        raw = response.read()
    elapsed = time.time() - start
    data = json.loads(raw.decode("utf-8"))
    content = data["choices"][0]["message"]["content"].strip()
    data["wall_seconds"] = elapsed
    return content, data


def sanitize_patch(text: str, encounter: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    exact_rxn_ids = {
        reaction["id"]
        for option in encounter.get("options", []) or []
        for reaction in option.get("reactions", []) or []
    }
    kept: list[str] = [f"## ENC {encounter['id']} | {encounter.get('title', '')} | turn=19..30"]
    report = {"kept_reactions": 0, "dropped_lines": 0, "bad_rxn_ids": [], "bad_targets": []}
    for option in encounter.get("options", []) or []:
        option_text = (option.get("text_script") or {}).get("value", "")
        kept.append(f"OPT {option['id']}: {option_text}")
        for reaction in option.get("reactions", []) or []:
            current = reaction.get("consequence_id", "")
            proposed = current
            for line in text.splitlines():
                match = RXN_RE.match(line)
                if not match:
                    continue
                rxn_id, target = match.groups()
                if rxn_id == reaction["id"] and target in ALLOWED_TARGETS:
                    proposed = target
                    break
            kept.append(f"  RXN {reaction['id']} -> {proposed}")
            report["kept_reactions"] += 1

    for line in text.splitlines():
        match = RXN_RE.match(line)
        if not match:
            if line.strip() and not line.startswith(("## ENC ", "OPT ")):
                report["dropped_lines"] += 1
            continue
        rxn_id, target = match.groups()
        if rxn_id not in exact_rxn_ids:
            report["bad_rxn_ids"].append(rxn_id)
        if target not in ALLOWED_TARGETS:
            report["bad_targets"].append(target)
    return "\n".join(kept) + "\n", report


def apply_consequence_patch(world: dict[str, Any], patch_text: str) -> dict[str, Any]:
    targets: dict[str, str] = {}
    for line in patch_text.splitlines():
        match = RXN_RE.match(line)
        if match:
            rxn_id, target = match.groups()
            targets[rxn_id] = target

    report = {"reaction_consequence": 0}
    for encounter in world.get("encounters", []) or []:
        for option in encounter.get("options", []) or []:
            for reaction in option.get("reactions", []) or []:
                target = targets.get(reaction.get("id"))
                if target and reaction.get("consequence_id") != target:
                    reaction["consequence_id"] = target
                    report["reaction_consequence"] += 1
    return report


def run_command(repo_root: Path, args: list[str], out_file: Path) -> int:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        args,
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
    )
    out_file.write_text(proc.stdout, encoding="utf-8")
    return proc.returncode


def run_receipts(repo_root: Path, candidate: Path, out_dir: Path) -> dict[str, int]:
    receipts: dict[str, int] = {}
    receipts["validator"] = run_command(
        repo_root,
        ["python3", "codex-skills/storyworld-building/scripts/sweepweave_validator.py", "validate", str(candidate)],
        out_dir / "validator.txt",
    )
    receipts["quality_gate"] = run_command(
        repo_root,
        [
            "python3",
            "codex-skills/storyworld-building/scripts/storyworld_quality_gate.py",
            "--storyworld",
            str(candidate),
            "--strict",
            "--report-out",
            str(out_dir / "quality_gate.json"),
        ],
        out_dir / "quality_gate.txt",
    )
    receipts["acceptance_audit"] = run_command(
        repo_root,
        [
            "python3",
            "hermes-skills/storyworld-conveyor/scripts/audit_storyworld_acceptance.py",
            "--storyworld",
            str(candidate),
            "--out-json",
            str(out_dir / "acceptance_audit.json"),
        ],
        out_dir / "acceptance_audit.txt",
    )
    receipts["authoring_score"] = run_command(
        repo_root,
        [
            "python3",
            "hermes-skills/storyworld-conveyor/scripts/score_storyworld_authoring.py",
            "--storyworld",
            str(candidate),
            "--repo-root",
            ".",
            "--out-json",
            str(out_dir / "authoring_score.json"),
            "--strict",
        ],
        out_dir / "authoring_score.txt",
    )
    receipts["hilbert_pathing"] = run_command(
        repo_root,
        [
            "python3",
            "hermes-skills/storyworld-conveyor/scripts/build_hilbert_pathing_packet.py",
            "--world-json",
            str(candidate),
            "--quality-report",
            str(out_dir / "quality_gate.json"),
            "--target-turns-min",
            "18",
            "--target-turns-max",
            "30",
            "--out-dir",
            str(out_dir / "hilbert_pathing"),
        ],
        out_dir / "hilbert_pathing.txt",
    )
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--base-json", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8083")
    parser.add_argument("--model", default="Qwen3.5-27B-128K.Q4_K_M.gguf")
    parser.add_argument("--max-tokens", type=int, default=520)
    parser.add_argument("--temperature", type=float, default=0.05)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    world = read_json(args.base_json)
    model_reports = []
    sanitized_blocks = []
    for encounter_id in TARGET_ENCOUNTERS:
        encounter = encounter_by_id(world, encounter_id)
        prompt = make_prompt(encounter)
        (out_dir / f"prompt_{encounter_id}.md").write_text(prompt, encoding="utf-8")
        try:
            content, response = call_model(args.endpoint, args.model, prompt, args.max_tokens, args.temperature)
        except (urllib.error.URLError, TimeoutError) as exc:
            (out_dir / f"error_{encounter_id}.txt").write_text(repr(exc) + "\n", encoding="utf-8")
            continue
        (out_dir / f"response_{encounter_id}.json").write_text(json.dumps(response, indent=2), encoding="utf-8")
        (out_dir / f"raw_patch_{encounter_id}.swmd.md").write_text(content + "\n", encoding="utf-8")
        sanitized, sanitize_report = sanitize_patch(content, encounter)
        (out_dir / f"sanitized_patch_{encounter_id}.swmd.md").write_text(sanitized, encoding="utf-8")
        sanitized_blocks.append(sanitized)
        model_reports.append(
            {
                "encounter_id": encounter_id,
                "usage": response.get("usage", {}),
                "timings": response.get("timings", {}),
                "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
                "wall_seconds": response.get("wall_seconds"),
                "sanitize": sanitize_report,
            }
        )

    patch_text = "\n".join(sanitized_blocks)
    (out_dir / "sanitized_combined_patch.swmd.md").write_text(patch_text, encoding="utf-8")
    patch_report = apply_consequence_patch(world, patch_text)
    candidate = out_dir / "candidate.json"
    write_json(candidate, world)
    receipts = run_receipts(repo_root, candidate, out_dir)

    summary = {
        "base_json": str(args.base_json),
        "candidate": str(candidate),
        "endpoint": args.endpoint,
        "model": args.model,
        "model_reports": model_reports,
        "patch_report": patch_report,
        "receipts": receipts,
    }
    write_json(out_dir / "summary.json", summary)
    return 0 if receipts.get("validator") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
