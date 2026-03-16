from __future__ import annotations

import json
import os
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .io_utils import append_jsonl, dump_json, ensure_dir, load_json, now_iso, read_jsonl, sha256_text, stable_split, write_csv, write_jsonl
from .models import AggregateRecord, AllowedAction, CompletionRecord, EncounterRecord, EnvGradeRecord, JudgeRecord, Manifest

STAGES = ["encounter_builder", "completion_runner", "env_grader", "llm_judge", "aggregator", "trainer_export"]


def load_config(config_path: Path) -> Dict[str, Any]:
    config = load_json(config_path)
    config["_config_path"] = str(config_path)
    return config


def stage_path(run_dir: Path, stage: str) -> Path:
    return ensure_dir(run_dir / stage)


def stage_completed(run_dir: Path, stage: str) -> bool:
    manifest_path = stage_path(run_dir, stage) / "manifest.json"
    if not manifest_path.exists():
        return False
    return load_json(manifest_path).get("status") == "completed"


def build_manifest(run_id: str, stage: str, input_files: List[str], output_files: List[str], counters: Dict[str, Any], config: Dict[str, Any], notes: Optional[List[str]] = None) -> Manifest:
    now = now_iso()
    return Manifest(
        run_id=run_id,
        stage=stage,
        status="completed",
        started_at=now,
        completed_at=now,
        input_files=input_files,
        output_files=output_files,
        counters=counters,
        config_digest=sha256_text(json.dumps(config, sort_keys=True)),
        notes=notes or [],
    )


def write_stage_meta(stage_dir: Path, manifest: Manifest, progress: Dict[str, Any], event: Dict[str, Any]) -> None:
    dump_json(stage_dir / "manifest.json", manifest.to_dict())
    dump_json(stage_dir / "progress.json", progress)
    append_jsonl(stage_dir / "events.jsonl", event)


def _to_encounter(row: Dict[str, Any]) -> EncounterRecord:
    payload = dict(row)
    payload["allowed_actions"] = [AllowedAction(**item) for item in payload["allowed_actions"]]
    return EncounterRecord(**payload)


def load_encounters(encounters_file: Path) -> List[EncounterRecord]:
    return [_to_encounter(row) for row in read_jsonl(encounters_file)]


def generate_encounters(config: Dict[str, Any]) -> List[EncounterRecord]:
    builder = config["encounter_builder"]
    count = int(builder["count"])
    families = builder["thematic_families"]
    tiers = builder["difficulty_tiers"]
    templates = [
        "A coalition meeting at {location} is deadlocked over {pressure}.",
        "A field report from {location} reveals escalating {pressure}.",
        "A negotiator must respond to {pressure} at {location}.",
        "A civic hearing at {location} is fracturing over {pressure}.",
    ]
    locations = ["the river crossing", "the royal court", "the supply yard", "the chapel archive"]
    pressures = ["supply scarcity", "hostage risk", "rumor spirals", "revenge demands"]
    rows: List[EncounterRecord] = []
    for idx in range(count):
        family = families[idx % len(families)]
        tier = tiers[idx % len(tiers)]
        actions = [
            AllowedAction(id=f"act_{idx:03d}_deescalate", label="De-escalate and buy time", state_deltas={"trust": 1, "stability": 1}, tags=["deescalate"]),
            AllowedAction(id=f"act_{idx:03d}_tradeoff", label="Accept a costly compromise", state_deltas={"trust": 1, "resources": -1}, tags=["tradeoff"]),
            AllowedAction(id=f"act_{idx:03d}_coerce", label="Use coercive leverage", state_deltas={"fear": 1, "trust": -1}, tags=["risk"]),
        ]
        rows.append(
            EncounterRecord(
                encounter_id=f"enc_{idx:03d}",
                family=family,
                difficulty_tier=tier,
                title=f"{family.title()} decision {idx + 1}",
                encounter_spec=templates[idx % len(templates)].format(location=locations[idx % len(locations)], pressure=pressures[idx % len(pressures)]),
                canonical_state={"pressure": pressures[idx % len(pressures)], "location": locations[idx % len(locations)], "tier": tier},
                allowed_actions=actions,
                constraints=["Choose one allowed action only.", "Mention uncertainty explicitly.", "Mention at least one stakeholder."],
                required_mentions=["uncertain", "stakeholder"],
                forbidden_terms=["ignore the rules", "kill everyone"],
                stakeholders=["civilians", "allies", "command"],
                target_action_ids=[actions[0].id, actions[1].id],
                metadata={"generated": True},
            )
        )
    return rows


def encounter_prompt(encounter: EncounterRecord, model_cfg: Dict[str, Any]) -> str:
    actions = "\n".join(f"- {item.id}: {item.label}" for item in encounter.allowed_actions)
    return textwrap.dedent(
        f"""
        Model profile: {model_cfg['name']}
        Encounter ID: {encounter.encounter_id}
        Title: {encounter.title}
        Family: {encounter.family}
        Difficulty: {encounter.difficulty_tier}
        Encounter spec: {encounter.encounter_spec}
        Canonical state: {json.dumps(encounter.canonical_state, sort_keys=True)}
        Constraints: {'; '.join(encounter.constraints)}
        Stakeholders: {', '.join(encounter.stakeholders)}
        Allowed actions:
        {actions}

        Respond with:
        Action: <allowed action id>
        Reasoning: <2-4 short sentences>
        """
    ).strip()


def mock_completion(encounter: EncounterRecord, model_cfg: Dict[str, Any], completion_index: int) -> str:
    action = encounter.allowed_actions[(completion_index + len(model_cfg["name"])) % len(encounter.allowed_actions)]
    stakeholder = encounter.stakeholders[completion_index % len(encounter.stakeholders)]
    return (
        f"Action: {action.id}\n"
        f"Reasoning: This protects {stakeholder} while preserving room to maneuver. "
        "The situation is uncertain, so we should monitor for reversals. "
        "This is the least-bad tradeoff under pressure."
    )


def detect_action(encounter: EncounterRecord, completion_text: str) -> Optional[AllowedAction]:
    lowered = completion_text.lower()
    for action in encounter.allowed_actions:
        if action.id.lower() in lowered or action.label.lower() in lowered:
            return action
    return None


def grade_completion(encounter: EncounterRecord, completion: CompletionRecord) -> EnvGradeRecord:
    lowered = completion.completion_text.lower()
    chosen_action = detect_action(encounter, completion.completion_text)
    missing_mentions = sum(1 for token in encounter.required_mentions if token not in lowered)
    forbidden_hits = sum(1 for token in encounter.forbidden_terms if token in lowered)
    action_validity = 1 if chosen_action else 0
    target_hits = 1 if chosen_action and chosen_action.id in encounter.target_action_ids else 0
    state_delta_count = len(chosen_action.state_deltas) if chosen_action else 0
    violations = missing_mentions + forbidden_hits
    success_flag = 1 if action_validity and target_hits and violations == 0 else 0
    penalties = round(0.15 * violations + (0.1 if not action_validity else 0.0), 4)
    base_score = 0.50 * action_validity + 0.20 * target_hits + 0.15 * success_flag + 0.15 * min(state_delta_count / 2.0, 1.0) - penalties
    env_score = max(0.0, min(1.0, round(base_score, 4)))
    return EnvGradeRecord(
        run_id=completion.run_id,
        stage_id="env_grader",
        encounter_id=completion.encounter_id,
        completion_id=completion.completion_id,
        action_validity=action_validity,
        constraint_violations=violations,
        target_count=len(encounter.target_action_ids),
        target_hits=target_hits,
        state_delta_count=state_delta_count,
        success_flag=success_flag,
        penalties=penalties,
        env_score=env_score,
        normalized={"action_validity": float(action_validity), "target_hits": float(target_hits), "success_flag": float(success_flag), "state_delta": min(state_delta_count / 2.0, 1.0)},
        details={"chosen_action_id": chosen_action.id if chosen_action else None, "missing_mentions": missing_mentions, "forbidden_hits": forbidden_hits},
    )


def build_judge_prompts(encounter: EncounterRecord, completion: CompletionRecord) -> Tuple[str, str]:
    system_prompt = (
        "You are a strict auxiliary judge. Output JSON only with keys coherence, ethical_adequacy, "
        "least_bad_tradeoff_quality, stakeholder_awareness, uncertainty_handling, "
        "concise_reasoning_quality, judge_score, notes. All scores must be floats in [0,1]."
    )
    user_prompt = json.dumps({"encounter": encounter.to_dict(), "completion_text": completion.completion_text}, indent=2)
    return system_prompt, user_prompt


def mock_judge(encounter: EncounterRecord, completion: CompletionRecord, raw_output_path: Path, judge_model: str) -> JudgeRecord:
    lowered = completion.completion_text.lower()
    word_count = len(completion.completion_text.split())
    stakeholder_hits = sum(1 for item in encounter.stakeholders if item.lower() in lowered)
    chosen_action = detect_action(encounter, completion.completion_text)
    coherence = 1.0 if chosen_action else 0.35
    ethical = 0.2 if any(token in lowered for token in encounter.forbidden_terms) else 0.8
    tradeoff = 0.85 if "least-bad" in lowered or "tradeoff" in lowered else 0.45
    awareness = min(1.0, 0.2 + stakeholder_hits / max(1, len(encounter.stakeholders)))
    uncertainty = 0.9 if "uncertain" in lowered or "monitor" in lowered else 0.3
    concise = 0.85 if 12 <= word_count <= 60 else 0.45
    judge_score = round(sum([coherence, ethical, tradeoff, awareness, uncertainty, concise]) / 6.0, 4)
    record = JudgeRecord(
        run_id=completion.run_id,
        stage_id="llm_judge",
        encounter_id=completion.encounter_id,
        completion_id=completion.completion_id,
        judge_provider="mock",
        judge_model=judge_model,
        coherence=round(coherence, 4),
        ethical_adequacy=round(ethical, 4),
        least_bad_tradeoff_quality=round(tradeoff, 4),
        stakeholder_awareness=round(awareness, 4),
        uncertainty_handling=round(uncertainty, 4),
        concise_reasoning_quality=round(concise, 4),
        judge_score=judge_score,
        raw_output_path=str(raw_output_path),
        notes="mock judge output",
    )
    raw_output_path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
    return record


def openai_judge(encounter: EncounterRecord, completion: CompletionRecord, raw_output_path: Path, cfg: Dict[str, Any]) -> JudgeRecord:
    api_key = os.environ.get(cfg["api_key_env"], "")
    if not api_key:
        raise RuntimeError(f"Missing env var {cfg['api_key_env']} for OpenAI judge")
    system_prompt, user_prompt = build_judge_prompts(encounter, completion)
    schema = {
        "type": "object",
        "required": ["coherence", "ethical_adequacy", "least_bad_tradeoff_quality", "stakeholder_awareness", "uncertainty_handling", "concise_reasoning_quality", "judge_score", "notes"],
        "properties": {key: {"type": "number"} for key in ["coherence", "ethical_adequacy", "least_bad_tradeoff_quality", "stakeholder_awareness", "uncertainty_handling", "concise_reasoning_quality", "judge_score"]},
    }
    schema["properties"]["notes"] = {"type": "string"}
    payload = {
        "model": cfg["model"],
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
        "text": {"format": {"type": "json_schema", "name": "judge_result", "schema": schema}},
        "max_output_tokens": cfg.get("max_output_tokens", 800),
    }
    request = urllib.request.Request(
        cfg.get("base_url", "https://api.openai.com/v1/responses"),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=cfg.get("timeout_seconds", 60)) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI judge HTTP {exc.code}: {detail}") from exc
    raw_output_path.write_text(body + "\n", encoding="utf-8")
    parsed = json.loads(body)
    output_text = parsed.get("output_text", "")
    if not output_text:
        parts: List[str] = []
        for block in parsed.get("output", []):
            for content in block.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))
        output_text = "\n".join(parts)
    result = json.loads(output_text)
    return JudgeRecord(
        run_id=completion.run_id,
        stage_id="llm_judge",
        encounter_id=completion.encounter_id,
        completion_id=completion.completion_id,
        judge_provider="openai_responses",
        judge_model=cfg["model"],
        coherence=float(result["coherence"]),
        ethical_adequacy=float(result["ethical_adequacy"]),
        least_bad_tradeoff_quality=float(result["least_bad_tradeoff_quality"]),
        stakeholder_awareness=float(result["stakeholder_awareness"]),
        uncertainty_handling=float(result["uncertainty_handling"]),
        concise_reasoning_quality=float(result["concise_reasoning_quality"]),
        judge_score=float(result["judge_score"]),
        raw_output_path=str(raw_output_path),
        notes=result.get("notes", ""),
    )


def init_run(config: Dict[str, Any], run_root: Path, run_id: Optional[str]) -> tuple[str, Path]:
    actual_run_id = run_id or config.get("run_id") or f"run_{now_iso().replace(':', '').replace('-', '')}"
    run_dir = ensure_dir(run_root / actual_run_id)
    dump_json(run_dir / "run_config.snapshot.json", {k: v for k, v in config.items() if not k.startswith("_")})
    return actual_run_id, run_dir


def run_build_encounters(run_dir: Path, run_id: str, config: Dict[str, Any], force: bool = False) -> Path:
    stage = "encounter_builder"
    if stage_completed(run_dir, stage) and not force:
        return stage_path(run_dir, stage) / "encounters.jsonl"
    stage_dir = stage_path(run_dir, stage)
    source = config["encounter_builder"].get("input_jsonl")
    encounters = load_encounters(Path(source)) if source else generate_encounters(config)
    output = stage_dir / "encounters.jsonl"
    count = write_jsonl(output, [item.to_dict() for item in encounters])
    manifest = build_manifest(run_id, stage, [source] if source else [], [str(output)], {"encounter_count": count}, config, ["ingested jsonl" if source else "generated from deterministic templates"])
    write_stage_meta(stage_dir, manifest, {"stage": stage, "status": "completed", "encounter_count": count, "updated_at": now_iso()}, {"event": "stage_completed", "count": count, "at": now_iso()})
    return output


def run_completions(run_dir: Path, run_id: str, config: Dict[str, Any], force: bool = False) -> Path:
    stage = "completion_runner"
    if stage_completed(run_dir, stage) and not force:
        return stage_path(run_dir, stage) / "completions.jsonl"
    encounters = load_encounters(stage_path(run_dir, "encounter_builder") / "encounters.jsonl")
    stage_dir = stage_path(run_dir, stage)
    prompts_dir = ensure_dir(stage_dir / "prompts")
    rows: List[Dict[str, Any]] = []
    for model_cfg in config["completion_runner"]["models"]:
        for encounter in encounters:
            for idx in range(int(model_cfg.get("n", 1))):
                prompt = encounter_prompt(encounter, model_cfg)
                prompt_path = prompts_dir / f"{encounter.encounter_id}__{model_cfg['name']}__{idx}.txt"
                prompt_path.write_text(prompt + "\n", encoding="utf-8")
                completion_text = mock_completion(encounter, model_cfg, idx)
                rows.append(
                    CompletionRecord(
                        run_id=run_id,
                        stage_id=stage,
                        encounter_id=encounter.encounter_id,
                        completion_id=f"{encounter.encounter_id}__{model_cfg['name']}__{idx}",
                        model_name=model_cfg["name"],
                        model_provider=model_cfg.get("provider", "mock"),
                        completion_index=idx,
                        prompt_path=str(prompt_path),
                        raw_prompt=prompt,
                        completion_text=completion_text,
                        token_counts={"prompt_tokens": len(prompt.split()), "completion_tokens": len(completion_text.split())},
                        metadata={"temperature": model_cfg.get("temperature", 0.0)},
                    ).to_dict()
                )
    output = stage_dir / "completions.jsonl"
    count = write_jsonl(output, rows)
    write_csv(stage_dir / "completions.csv", rows)
    manifest = build_manifest(run_id, stage, [str(stage_path(run_dir, "encounter_builder") / "encounters.jsonl")], [str(output)], {"completion_count": count}, config)
    write_stage_meta(stage_dir, manifest, {"stage": stage, "status": "completed", "completion_count": count, "updated_at": now_iso()}, {"event": "stage_completed", "count": count, "at": now_iso()})
    return output


def run_env_grader(run_dir: Path, run_id: str, config: Dict[str, Any], force: bool = False) -> Path:
    stage = "env_grader"
    if stage_completed(run_dir, stage) and not force:
        return stage_path(run_dir, stage) / "env_grades.jsonl"
    encounters = {item.encounter_id: item for item in load_encounters(stage_path(run_dir, "encounter_builder") / "encounters.jsonl")}
    completions = [CompletionRecord(**row) for row in read_jsonl(stage_path(run_dir, "completion_runner") / "completions.jsonl")]
    stage_dir = stage_path(run_dir, stage)
    rows = [grade_completion(encounters[item.encounter_id], item).to_dict() for item in completions]
    output = stage_dir / "env_grades.jsonl"
    count = write_jsonl(output, rows)
    write_csv(stage_dir / "env_grades.csv", rows)
    manifest = build_manifest(run_id, stage, [str(stage_path(run_dir, "completion_runner") / "completions.jsonl")], [str(output)], {"graded_count": count}, config)
    write_stage_meta(stage_dir, manifest, {"stage": stage, "status": "completed", "graded_count": count, "updated_at": now_iso()}, {"event": "stage_completed", "count": count, "at": now_iso()})
    return output


def run_llm_judge(run_dir: Path, run_id: str, config: Dict[str, Any], force: bool = False) -> Path:
    stage = "llm_judge"
    if stage_completed(run_dir, stage) and not force:
        return stage_path(run_dir, stage) / "judge_outputs.jsonl"
    encounters = {item.encounter_id: item for item in load_encounters(stage_path(run_dir, "encounter_builder") / "encounters.jsonl")}
    completions = [CompletionRecord(**row) for row in read_jsonl(stage_path(run_dir, "completion_runner") / "completions.jsonl")]
    stage_dir = stage_path(run_dir, stage)
    raw_dir = ensure_dir(stage_dir / "raw")
    cfg = config["llm_judge"]
    provider = cfg.get("provider", "mock")
    rows: List[Dict[str, Any]] = []
    for item in completions:
        encounter = encounters[item.encounter_id]
        raw_output = raw_dir / f"{item.completion_id}.json"
        result = mock_judge(encounter, item, raw_output, cfg.get("model", "gpt-5-mini")) if provider == "mock" else openai_judge(encounter, item, raw_output, cfg)
        rows.append(result.to_dict())
    output = stage_dir / "judge_outputs.jsonl"
    count = write_jsonl(output, rows)
    write_csv(stage_dir / "judge_outputs.csv", rows)
    manifest = build_manifest(run_id, stage, [str(stage_path(run_dir, "completion_runner") / "completions.jsonl")], [str(output)], {"judge_count": count, "provider": provider}, config)
    write_stage_meta(stage_dir, manifest, {"stage": stage, "status": "completed", "judge_count": count, "provider": provider, "updated_at": now_iso()}, {"event": "stage_completed", "count": count, "provider": provider, "at": now_iso()})
    return output


def run_aggregator(run_dir: Path, run_id: str, config: Dict[str, Any], force: bool = False) -> Path:
    stage = "aggregator"
    if stage_completed(run_dir, stage) and not force:
        return stage_path(run_dir, stage) / "aggregate.jsonl"
    env_rows = {(row["encounter_id"], row["completion_id"]): row for row in read_jsonl(stage_path(run_dir, "env_grader") / "env_grades.jsonl")}
    judge_rows = {(row["encounter_id"], row["completion_id"]): row for row in read_jsonl(stage_path(run_dir, "llm_judge") / "judge_outputs.jsonl")}
    weights = config["aggregator"]["weights"]
    env_weight = float(weights["env_score"])
    judge_weight = float(weights["judge_score"])
    by_encounter: Dict[str, List[AggregateRecord]] = {}
    for key, env_row in env_rows.items():
        judge_row = judge_rows.get(key, {})
        final_score = round(env_weight * float(env_row["env_score"]) + judge_weight * float(judge_row.get("judge_score", 0.0)), 4)
        record = AggregateRecord(
            run_id=run_id,
            stage_id=stage,
            encounter_id=env_row["encounter_id"],
            completion_id=env_row["completion_id"],
            env_score=float(env_row["env_score"]),
            judge_score=float(judge_row.get("judge_score", 0.0)),
            final_score=final_score,
            env_weight=env_weight,
            judge_weight=judge_weight,
            rank_within_encounter=0,
            bundle={"final_formula": f"{env_weight:.2f} * env_score + {judge_weight:.2f} * judge_score", "env_details": env_row, "judge_details": judge_row},
        )
        by_encounter.setdefault(record.encounter_id, []).append(record)
    flat: List[Dict[str, Any]] = []
    leaderboard: List[Dict[str, Any]] = []
    for encounter_id, rows in by_encounter.items():
        for rank, row in enumerate(sorted(rows, key=lambda item: item.final_score, reverse=True), start=1):
            row.rank_within_encounter = rank
            flat.append(row.to_dict())
            leaderboard.append({"encounter_id": encounter_id, "completion_id": row.completion_id, "rank_within_encounter": rank, "final_score": row.final_score, "env_score": row.env_score, "judge_score": row.judge_score})
    stage_dir = stage_path(run_dir, stage)
    output = stage_dir / "aggregate.jsonl"
    count = write_jsonl(output, flat)
    write_csv(stage_dir / "aggregate.csv", flat)
    write_csv(stage_dir / "leaderboard.csv", leaderboard)
    dump_json(stage_dir / "summary.json", {"run_id": run_id, "encounter_count": len(by_encounter), "completion_count": count, "mean_final_score": round(sum(item["final_score"] for item in leaderboard) / max(1, len(leaderboard)), 4), "weights": weights})
    manifest = build_manifest(run_id, stage, [str(stage_path(run_dir, "env_grader") / "env_grades.jsonl"), str(stage_path(run_dir, "llm_judge") / "judge_outputs.jsonl")], [str(output)], {"aggregate_count": count}, config)
    write_stage_meta(stage_dir, manifest, {"stage": stage, "status": "completed", "aggregate_count": count, "updated_at": now_iso()}, {"event": "stage_completed", "count": count, "at": now_iso()})
    return output


def run_export_training(run_dir: Path, run_id: str, config: Dict[str, Any], force: bool = False) -> Path:
    stage = "trainer_export"
    if stage_completed(run_dir, stage) and not force:
        return stage_path(run_dir, stage) / "training_sft.jsonl"
    aggregate_rows = read_jsonl(stage_path(run_dir, "aggregator") / "aggregate.jsonl")
    completions = {row["completion_id"]: row for row in read_jsonl(stage_path(run_dir, "completion_runner") / "completions.jsonl")}
    stage_dir = stage_path(run_dir, stage)
    split_cfg = config["trainer_export"]["splits"]
    sft_rows: List[Dict[str, Any]] = []
    verifier_rows: List[Dict[str, Any]] = []
    critique_rows: List[Dict[str, Any]] = []
    split_index: Dict[str, str] = {}
    for row in aggregate_rows:
        completion = completions[row["completion_id"]]
        split = stable_split(row["encounter_id"], float(split_cfg["train"]), float(split_cfg["val"]))
        split_index[row["completion_id"]] = split
        base = {"split": split, "encounter_id": row["encounter_id"], "completion_id": row["completion_id"], "source_paths": {"prompt_path": completion["prompt_path"]}}
        sft_rows.append({**base, "task_type": "sft", "prompt": completion["raw_prompt"], "response": completion["completion_text"], "labels": {"final_score": row["final_score"]}})
        verifier_rows.append({**base, "task_type": "verifier", "prompt": completion["raw_prompt"], "candidate": completion["completion_text"], "labels": {"env_score": row["env_score"], "judge_score": row["judge_score"], "final_score": row["final_score"]}})
        critique_rows.append({**base, "task_type": "critique_repair", "prompt": completion["raw_prompt"], "candidate": completion["completion_text"], "critique": {"env_score": row["env_score"], "judge_score": row["judge_score"], "rank_within_encounter": row["rank_within_encounter"]}})
    sft_path = stage_dir / "training_sft.jsonl"
    verifier_path = stage_dir / "training_verifier.jsonl"
    critique_path = stage_dir / "training_critique.jsonl"
    write_jsonl(sft_path, sft_rows)
    write_jsonl(verifier_path, verifier_rows)
    write_jsonl(critique_path, critique_rows)
    dump_json(stage_dir / "splits.json", split_index)
    manifest = build_manifest(run_id, stage, [str(stage_path(run_dir, "aggregator") / "aggregate.jsonl")], [str(sft_path), str(verifier_path), str(critique_path)], {"export_count": len(sft_rows)}, config)
    write_stage_meta(stage_dir, manifest, {"stage": stage, "status": "completed", "export_count": len(sft_rows), "updated_at": now_iso()}, {"event": "stage_completed", "count": len(sft_rows), "at": now_iso()})
    return sft_path


def run_pipeline(config: Dict[str, Any], run_root: Path, run_id: Optional[str], force: bool = False, stop_after: Optional[str] = None) -> Path:
    run_id, run_dir = init_run(config, run_root, run_id)
    handlers = {
        "encounter_builder": run_build_encounters,
        "completion_runner": run_completions,
        "env_grader": run_env_grader,
        "llm_judge": run_llm_judge,
        "aggregator": run_aggregator,
        "trainer_export": run_export_training,
    }
    last_output: Path = run_dir
    for stage in STAGES:
        last_output = handlers[stage](run_dir, run_id, config, force=force)
        if stop_after == stage:
            break
    return last_output
