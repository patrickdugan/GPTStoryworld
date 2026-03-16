from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from swmd_encounter_index import parse_swmd_min


ID_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


def _extract_vars(text: str) -> List[str]:
    out: List[str] = []
    for tok in ID_RE.findall(text):
        if tok in {"ORX", "ENC", "turn", "to", "from", "and", "the"}:
            continue
        if tok.startswith("rxn_") or tok.startswith("opt_") or tok.startswith("page_"):
            continue
        if tok not in out:
            out.append(tok)
    return out


def _base_spec(world_id: str, encounter_id: str, turn_span: str, block: str, reactions: List[Any]) -> Dict[str, Any]:
    vars_seen: List[str] = []
    for r in reactions:
        vars_seen.extend(_extract_vars(f"{r.effects} {r.desirability}"))
    state_vars = [
        "reputation_field",
        "conscience_load",
        "inference_pressure",
        "trust_public",
        "trust_private",
        "leverage",
        "exposure_risk",
    ]
    for v in vars_seen:
        if len(state_vars) >= 14:
            break
        if v not in state_vars:
            state_vars.append(v)

    actions: List[Dict[str, Any]] = []
    irreversible: List[str] = []
    for r in reactions:
        aid = f"act_{r.rxn_id}"
        tgt = str(r.consequence)
        if tgt.startswith("page_end") or tgt.startswith("page_secret"):
            irreversible.append(aid)
        actions.append(
            {
                "id": aid,
                "label": r.option_text if r.option_text else r.rxn_id,
                "actor": "agent_protagonist",
                "pre": ["visibility_gate", "performability_gate"],
                "effects_expr": r.effects,
                "desirability_expr": r.desirability,
                "transition": tgt,
            }
        )

    return {
        "schema": "SWMD-MICRO-0.1",
        "world_id": world_id,
        "encounter_id": encounter_id,
        "turn_span": turn_span,
        "agents": [
            "agent_protagonist",
            "agent_counterparty",
            "agent_community",
            "agent_adversary",
            "agent_outlier",
        ],
        "state_vars": state_vars,
        "norms": [
            "public_signal_not_equal_private_truth",
            "reputation_updates_are_slow",
            "hidden_state_can_drive_actions",
            "id_stability_required",
        ],
        "actions": actions,
        "transitions": {
            "irreversible_actions": irreversible,
            "possible_targets": sorted({str(r.consequence) for r in reactions}),
        },
        "source_block": block,
    }


def _compressed_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(spec))
    out["agents"] = out.get("agents", [])[:5]
    out["state_vars"] = out.get("state_vars", [])[:10]
    # keep top actions by lexical id for deterministic compression
    actions = out.get("actions", []) or []
    out["actions"] = sorted(actions, key=lambda a: str(a.get("id", "")))[: min(6, len(actions))]
    return out


def _corrupt_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(spec))
    out["schema"] = "SWMD-MICRO-BROKEN"
    actions = out.get("actions", []) or []
    if actions:
        actions[0]["transition"] = ""
    if len(actions) > 1:
        actions[1]["id"] = actions[0]["id"]
    out["actions"] = actions
    return out


def _targeted_edit(spec: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(spec))
    # Add conflicting incentives without new agents.
    norms = out.get("norms", []) or []
    norms.extend(
        [
            "incentive_conflict:stability_vs_truth_reveal",
            "incentive_conflict:status_preservation_vs_mercy",
        ]
    )
    out["norms"] = norms
    actions = out.get("actions", []) or []
    for i, a in enumerate(actions[:2]):
        pre = a.get("pre", []) or []
        pre.append("conflict_gate")
        a["pre"] = pre
        a["effects_expr"] = f"{a.get('effects_expr','')} ; +stability -truth" if i == 0 else f"{a.get('effects_expr','')} ; +truth -status"
    out["actions"] = actions
    return out


def _json_text(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=True, indent=2)


def _task_schedule(total_rows: int) -> List[str]:
    targets = {
        "compile": int(round(total_rows * 0.40)),
        "compression": int(round(total_rows * 0.25)),
        "repair": int(round(total_rows * 0.20)),
        "targeted_edit": int(round(total_rows * 0.15)),
    }
    # Adjust rounding residue onto compile.
    residue = total_rows - sum(targets.values())
    targets["compile"] += residue
    seq: List[str] = []
    order = ["compile", "compression", "repair", "targeted_edit"]
    while len(seq) < total_rows:
        # Greedy by remaining deficit, deterministic tiebreak by order.
        remaining = [(k, targets[k]) for k in order if targets[k] > 0]
        if not remaining:
            break
        remaining.sort(key=lambda kv: (-kv[1], order.index(kv[0])))
        pick = remaining[0][0]
        seq.append(pick)
        targets[pick] -= 1
    return seq


def _mk_row(row_id: str, task_type: str, instruction: str, inp: str, out: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row_id,
        "task_type": task_type,
        "instruction": instruction,
        "input": inp,
        "output": out,
        "messages": [
            {"role": "system", "content": "You compile narrative encounters into canonical SWMD-MICRO-0.1 JSON with stable schema."},
            {"role": "user", "content": f"{instruction}\n\n{inp}"},
            {"role": "assistant", "content": out},
        ],
        "meta": meta,
    }


def build_examples(swmd_paths: List[Path], max_total_encounters: int, examples_per_encounter: int) -> List[Dict[str, Any]]:
    docs = [(p, parse_swmd_min(p)) for p in swmd_paths]
    encounter_refs: List[Tuple[str, str, Any]] = []
    for path, doc in docs:
        for eid in sorted(doc.encounters.keys()):
            encounter_refs.append((str(path), doc.world_id, doc.encounters[eid]))
    encounter_refs = encounter_refs[:max_total_encounters]

    total_rows = len(encounter_refs) * examples_per_encounter
    schedule = _task_schedule(total_rows)
    cursor = 0
    rows: List[Dict[str, Any]] = []
    rid = 0
    for src, world_id, enc in encounter_refs:
        base = _base_spec(world_id, enc.encounter_id, enc.turn_span, "\n".join(enc.block_lines), enc.reactions)
        comp = _compressed_spec(base)
        broken = _corrupt_spec(base)
        edited = _targeted_edit(comp)

        for i in range(examples_per_encounter):
            task = schedule[cursor] if cursor < len(schedule) else "compile"
            cursor += 1
            if task == "compile":
                rid += 1
                rows.append(
                    _mk_row(
                        f"ex_{rid:07d}",
                        "compile",
                        "Compile this encounter into canonical SWMD-MICRO-0.1 JSON. Keep schema identical.",
                        "\n".join(enc.block_lines),
                        _json_text(base),
                        {"source_swmd": src, "world_id": world_id, "encounter_id": enc.encounter_id, "variant": i},
                    )
                )
            elif task == "compression":
                rid += 1
                rows.append(
                    _mk_row(
                        f"ex_{rid:07d}",
                        "compression",
                        "Reduce this micro-spec to <=5 agents and <=10 state_vars while preserving core transitions.",
                        _json_text(base),
                        _json_text(comp),
                        {"source_swmd": src, "world_id": world_id, "encounter_id": enc.encounter_id, "variant": i},
                    )
                )
            elif task == "repair":
                rid += 1
                rows.append(
                    _mk_row(
                        f"ex_{rid:07d}",
                        "repair",
                        "Repair this broken micro-spec. Return valid SWMD-MICRO-0.1 JSON with unique action IDs and valid transitions.",
                        _json_text(broken),
                        _json_text(base),
                        {"source_swmd": src, "world_id": world_id, "encounter_id": enc.encounter_id, "variant": i},
                    )
                )
            else:
                rid += 1
                rows.append(
                    _mk_row(
                        f"ex_{rid:07d}",
                        "targeted_edit",
                        "Add two conflicting incentives without adding agents. Keep canonical schema.",
                        _json_text(comp),
                        _json_text(edited),
                        {"source_swmd": src, "world_id": world_id, "encounter_id": enc.encounter_id, "variant": i},
                    )
                )
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description="Build derived QLoRA examples from SWMD-0-MIN encounters.")
    p.add_argument("--swmd-glob", type=str, required=True, help="Glob pattern for input .swmd.min.md files.")
    p.add_argument("--out-dir", type=str, required=True, help="Output directory for QLoRA examples.")
    p.add_argument("--max-total-encounters", type=int, default=120)
    p.add_argument("--examples-per-encounter", type=int, default=10)
    p.add_argument("--val-ratio", type=float, default=0.05)
    args = p.parse_args()

    if any(ch in args.swmd_glob for ch in "*?[]"):
        swmd_paths = sorted(Path(p) for p in glob.glob(args.swmd_glob))
    else:
        swmd_paths = [Path(args.swmd_glob)] if Path(args.swmd_glob).exists() else []
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if not swmd_paths:
        raise SystemExit(f"no SWMD files matched: {args.swmd_glob}")

    rows = build_examples(swmd_paths, args.max_total_encounters, args.examples_per_encounter)
    n_val = max(1, int(len(rows) * max(0.0, min(0.4, args.val_ratio))))
    train = rows[:-n_val]
    val = rows[-n_val:]

    train_path = out_dir / "train.jsonl"
    val_path = out_dir / "val.jsonl"
    msg_train = out_dir / "train_messages.jsonl"
    msg_val = out_dir / "val_messages.jsonl"
    stats_path = out_dir / "stats.json"

    with train_path.open("w", encoding="utf-8", newline="\n") as h:
        for r in train:
            h.write(json.dumps(r, ensure_ascii=True) + "\n")
    with val_path.open("w", encoding="utf-8", newline="\n") as h:
        for r in val:
            h.write(json.dumps(r, ensure_ascii=True) + "\n")
    with msg_train.open("w", encoding="utf-8", newline="\n") as h:
        for r in train:
            h.write(json.dumps({"id": r["id"], "messages": r["messages"], "meta": r["meta"]}, ensure_ascii=True) + "\n")
    with msg_val.open("w", encoding="utf-8", newline="\n") as h:
        for r in val:
            h.write(json.dumps({"id": r["id"], "messages": r["messages"], "meta": r["meta"]}, ensure_ascii=True) + "\n")

    task_hist: Dict[str, int] = {}
    for r in rows:
        task_hist[r["task_type"]] = task_hist.get(r["task_type"], 0) + 1
    stats = {
        "swmd_files": [str(p) for p in swmd_paths],
        "max_total_encounters": args.max_total_encounters,
        "examples_per_encounter": args.examples_per_encounter,
        "rows_total": len(rows),
        "rows_train": len(train),
        "rows_val": len(val),
        "task_histogram": task_hist,
        "schema": "SWMD-MICRO-0.1",
    }
    stats_path.write_text(json.dumps(stats, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(str(train_path))
    print(str(val_path))
    print(str(stats_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
