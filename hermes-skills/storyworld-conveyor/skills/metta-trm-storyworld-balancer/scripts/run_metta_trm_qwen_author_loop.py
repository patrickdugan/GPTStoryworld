#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
STORY_SCRIPTS = REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts"
CONVEYOR_SCRIPTS = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "scripts"
THIS_DIR = Path(__file__).resolve().parent


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, timeout: int = 600) -> dict[str, Any]:
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("$ " + " ".join(cmd) + "\n\n")
        handle.flush()
        try:
            proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            handle.write(f"\nTIMEOUT after {timeout}s\n")
            rc = 124
    return {"command": cmd, "returncode": rc, "seconds": round(time.time() - started, 3), "log": str(log_path)}


def script_text(value: Any) -> str:
    if isinstance(value, dict):
        raw = value.get("value")
        if isinstance(raw, str):
            return raw
        return " ".join(script_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(script_text(v) for v in value)
    if isinstance(value, str):
        return value
    return ""


def pointer(character: str, keyring: list[str], coefficient: float = 0.025) -> dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": character,
        "keyring": keyring,
        "coefficient": coefficient,
    }


def ensure_addition(script: Any) -> dict[str, Any]:
    if isinstance(script, dict) and script.get("script_element_type") == "Operator" and script.get("operator_type") == "Addition":
        operands = script.setdefault("operands", [])
        if isinstance(operands, list):
            return script
    return {
        "script_element_type": "Operator",
        "operator_type": "Addition",
        "operands": [script if isinstance(script, dict) else {"script_element_type": "Pointer", "pointer_type": "Bounded Number Constant", "value": 0.0}],
    }


def first_effect_target(reaction: dict[str, Any]) -> tuple[str, str] | None:
    for effect in reaction.get("after_effects", []) or []:
        if effect.get("effect_type") != "Bounded Number Effect":
            continue
        set_ptr = effect.get("Set")
        if not isinstance(set_ptr, dict):
            continue
        character = set_ptr.get("character")
        keyring = set_ptr.get("keyring") or []
        if isinstance(character, str) and isinstance(keyring, list) and keyring and isinstance(keyring[0], str):
            return character, keyring[0]
    return None


def collect_characters(world: dict[str, Any]) -> list[str]:
    chars: list[str] = []
    for char in world.get("characters", []) or []:
        char_id = char.get("id")
        if isinstance(char_id, str) and char_id:
            chars.append(char_id)
    if not chars:
        chars = ["char_player", "char_witness"]
    return chars


def add_pvalue_p2_support(world: dict[str, Any], max_reactions: int = 80) -> dict[str, Any]:
    chars = collect_characters(world)
    patched = 0
    touched: list[dict[str, Any]] = []
    for encounter in world.get("encounters", []) or []:
        encounter_id = encounter.get("id") or encounter.get("encounter_id") or "unknown_encounter"
        for option in encounter.get("options", []) or []:
            option_id = option.get("id") or option.get("option_id") or "unknown_option"
            for reaction_index, reaction in enumerate(option.get("reactions", []) or []):
                target = first_effect_target(reaction)
                if target is None:
                    continue
                affected_char, prop = target
                witnesses = [char for char in chars if char != affected_char]
                while len(witnesses) < 2:
                    witnesses.append(affected_char)
                desirability = ensure_addition(reaction.get("desirability_script"))
                operands = desirability.setdefault("operands", [])
                if not isinstance(operands, list):
                    operands = []
                    desirability["operands"] = operands
                operands.append(pointer(witnesses[0], [prop, affected_char], 0.02))
                operands.append(pointer(witnesses[1], [prop, affected_char, witnesses[0]], 0.01))
                reaction["desirability_script"] = desirability
                patched += 1
                touched.append({"encounter": encounter_id, "option": option_id, "reaction_index": reaction_index, "property": prop, "affected": affected_char})
                if patched >= max_reactions:
                    return {"patched_reactions": patched, "touched": touched}
    return {"patched_reactions": patched, "touched": touched}


def call_qwen(base_url: str, model: str, prompt: str, timeout: int) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You write concise, high-quality storyworld authoring notes. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 700,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"ok": True, "content": content, "raw": data}


def build_qwen_prompt(packet: dict[str, Any], world: dict[str, Any]) -> str:
    title = world.get("storyworld_title") or world.get("title") or "storyworld"
    sample = []
    for encounter in (world.get("encounters", []) or [])[:3]:
        sample.append({
            "id": encounter.get("id") or encounter.get("encounter_id"),
            "title": script_text(encounter.get("title_text"))[:120],
            "body": script_text(encounter.get("body_text"))[:240],
        })
    return json.dumps(
        {
            "task": "Write bounded prose/design notes for a MeTTa/TRM guided Macbeth storyworld repair. Do not output full JSON.",
            "title": title,
            "repair_targets": packet.get("repair_targets", [])[:6],
            "observations": packet.get("observations", [])[:6],
            "sample_encounters": sample,
            "output_schema": {
                "tone_notes": ["..."],
                "route_foreshadowing_lines": ["..."],
                "secret_route_clues": ["..."],
                "fallback_suppression_notes": ["..."],
            },
        },
        indent=2,
        ensure_ascii=True,
    )


def score_all(world_path: Path, out_dir: Path, python_bin: str, mc_runs: int, timeout: int) -> dict[str, Any]:
    logs = out_dir / "logs"
    reports = out_dir / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    commands = []
    commands.append(run_cmd([python_bin, str(STORY_SCRIPTS / "sweepweave_validator.py"), "validate", str(world_path)], REPO_ROOT, logs / "validator.log", timeout))
    commands.append(run_cmd([python_bin, str(STORY_SCRIPTS / "storyworld_quality_gate.py"), "--storyworld", str(world_path), "--strict", "--report-out", str(reports / "quality_gate.json")], REPO_ROOT, logs / "quality_gate.log", timeout))
    commands.append(run_cmd([python_bin, str(CONVEYOR_SCRIPTS / "score_storyworld_authoring.py"), "--storyworld", str(world_path), "--repo-root", str(REPO_ROOT), "--out-json", str(reports / "authoring_score.json")], REPO_ROOT, logs / "authoring_score.log", timeout))
    commands.append(run_cmd([python_bin, str(STORY_SCRIPTS / "monte_carlo_rehearsal.py"), str(world_path), "--runs", str(mc_runs), "--seed", "17"], REPO_ROOT, reports / "monte_carlo.txt", timeout))
    commands.append(run_cmd([python_bin, str(THIS_DIR / "build_metta_trm_balance_packet.py"), "--storyworld", str(world_path), "--out-dir", str(reports / "metta_trm_balance"), "--quality-report", str(reports / "quality_gate.json"), "--monte-carlo-report", str(reports / "monte_carlo.txt")], REPO_ROOT, logs / "metta_trm_balance.log", timeout))
    return {"reports": str(reports), "commands": commands}


def summarize_scores(label: str, reports: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"label": label}
    q = reports / "quality_gate.json"
    if q.exists():
        data = read_json(q)
        out["quality_pass"] = data.get("pass")
        out["quality_failures"] = data.get("failures", [])
        summary = data.get("summary", {})
        out["p2value_refs"] = summary.get("p2value_refs")
        out["pvalue_refs"] = summary.get("pvalue_refs")
    a = reports / "authoring_score.json"
    if a.exists():
        data = read_json(a)
        for key in ["weighted_authoring_verifier_score", "pvalue_desirability_alignment", "effect_diversity", "gating_score", "pass"]:
            out[key] = data.get(key)
    m = reports / "metta_trm_balance" / "trm_balance_packet.json"
    if m.exists():
        data = read_json(m)
        out["balance_signals"] = data.get("balance_signals", {})
        out["repair_targets"] = data.get("repair_targets", [])[:8]
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hermes hackathon runner: MeTTa/TRM deterministic repair plus bounded Qwen authoring.")
    parser.add_argument("--storyworld", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--mc-runs", type=int, default=300)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--qwen-base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--qwen-model", default="Qwen3.5-27B.Q4_K_M.gguf")
    parser.add_argument("--qwen-timeout", type=int, default=120)
    parser.add_argument("--skip-qwen", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.storyworld).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    worlds_dir = out_dir / "worlds"
    worlds_dir.mkdir(parents=True, exist_ok=True)

    baseline_world = worlds_dir / source.name
    shutil.copy2(source, baseline_world)
    candidate_world = worlds_dir / f"{source.stem}_metta_trm_p2_patch.json"
    shutil.copy2(source, candidate_world)

    baseline = score_all(baseline_world, out_dir / "baseline", args.python_bin, args.mc_runs, args.timeout)
    baseline_packet_path = Path(baseline["reports"]) / "metta_trm_balance" / "trm_balance_packet.json"
    baseline_packet = read_json(baseline_packet_path) if baseline_packet_path.exists() else {}

    candidate_data = read_json(candidate_world)
    patch_report = add_pvalue_p2_support(candidate_data)
    write_json(candidate_world, candidate_data)

    qwen_result: dict[str, Any] = {"ok": False, "skipped": True}
    if not args.skip_qwen:
        qwen_prompt = build_qwen_prompt(baseline_packet, candidate_data)
        (out_dir / "qwen_authoring_prompt.json").write_text(qwen_prompt + "\n", encoding="utf-8", newline="\n")
        qwen_result = call_qwen(args.qwen_base_url, args.qwen_model, qwen_prompt, args.qwen_timeout)
        write_json(out_dir / "qwen_authoring_suggestions.json", qwen_result)

    candidate = score_all(candidate_world, out_dir / "candidate", args.python_bin, args.mc_runs, args.timeout)
    baseline_scores = summarize_scores("baseline", Path(baseline["reports"]))
    candidate_scores = summarize_scores("candidate", Path(candidate["reports"]))

    report = {
        "storyworld": str(source),
        "candidate_world": str(candidate_world),
        "patch": patch_report,
        "qwen": {"ok": qwen_result.get("ok"), "skipped": qwen_result.get("skipped", False), "error": qwen_result.get("error")},
        "baseline": baseline_scores,
        "candidate": candidate_scores,
        "score_delta": {
            "weighted_authoring_verifier_score": (
                (candidate_scores.get("weighted_authoring_verifier_score") or 0.0)
                - (baseline_scores.get("weighted_authoring_verifier_score") or 0.0)
            ),
            "pvalue_desirability_alignment": (
                (candidate_scores.get("pvalue_desirability_alignment") or 0.0)
                - (baseline_scores.get("pvalue_desirability_alignment") or 0.0)
            ),
        },
    }
    write_json(out_dir / "run_summary.json", report)
    (out_dir / "hermes_artifact_report.md").write_text(
        "# Hermes MeTTa/TRM Qwen Author Loop\n\n"
        f"- Source: `{source}`\n"
        f"- Candidate: `{candidate_world}`\n"
        f"- Patched reactions: {patch_report.get('patched_reactions')}\n"
        f"- Qwen suggestions: {qwen_result.get('ok')}\n"
        f"- Baseline score: {baseline_scores.get('weighted_authoring_verifier_score')}\n"
        f"- Candidate score: {candidate_scores.get('weighted_authoring_verifier_score')}\n"
        f"- Score delta: {report['score_delta']['weighted_authoring_verifier_score']}\n"
        f"- Baseline quality failures: {baseline_scores.get('quality_failures')}\n"
        f"- Candidate quality failures: {candidate_scores.get('quality_failures')}\n",
        encoding="utf-8",
        newline="\n",
    )
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
