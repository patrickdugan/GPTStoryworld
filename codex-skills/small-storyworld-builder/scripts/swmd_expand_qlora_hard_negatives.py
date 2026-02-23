from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        try:
            rows.append(json.loads(s))
        except Exception:
            continue
    return rows


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as h:
        for r in rows:
            h.write(json.dumps(r, ensure_ascii=True) + "\n")


def _parse_micro(output: str) -> Dict[str, Any] | None:
    try:
        d = json.loads(output)
    except Exception:
        return None
    if isinstance(d, dict) and d.get("schema") == "SWMD-MICRO-0.1":
        return d
    return None


def _corrupt_duplicate_action_id(spec: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(spec))
    acts = out.get("actions", []) or []
    if len(acts) >= 2:
        acts[1]["id"] = acts[0].get("id", "act_dup")
    out["actions"] = acts
    return out


def _corrupt_blank_transition(spec: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(spec))
    acts = out.get("actions", []) or []
    if acts:
        acts[0]["transition"] = ""
    out["actions"] = acts
    return out


def _corrupt_schema_tag(spec: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(spec))
    out["schema"] = "SWMD-MICRO-BROKEN"
    return out


def _corrupt_drop_state_var(spec: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(spec))
    sv = out.get("state_vars", []) or []
    if sv:
        out["state_vars"] = sv[:-1]
    return out


def _mk_row(rid: int, operation: str, inp: Dict[str, Any], out: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    frame = {
        "schema": "SWMD-TRAIN-0.1",
        "operation": operation,
        "input_spec": inp,
        "constraints": {
            "output_schema": "SWMD-MICRO-0.1",
            "keep_ids_stable": True,
        },
    }
    instruction = {
        "repair": "Repair this broken SWMD-MICRO-0.1 spec and return canonical valid JSON.",
        "id_stability_repair": "Restore unique action IDs and valid transitions while keeping semantics.",
        "schema_normalize": "Normalize this spec to canonical SWMD-MICRO-0.1 schema and key structure.",
        "desirability_refine": "Refine desirability logic so every action uses multi-variable non-constant formulas.",
        "ore_saturation_design": "Tune options/reactions/effects saturation while preserving world semantics.",
        "spool_flow_rewrite": "Rebuild spool/act flow for coherent encounter graph progression with stable IDs.",
    }[operation]
    output_text = json.dumps(out, ensure_ascii=True, indent=2)
    input_text = json.dumps(frame, ensure_ascii=True, indent=2)
    return {
        "id": f"hn_{rid:07d}",
        "task_type": operation,
        "instruction": instruction,
        "input": input_text,
        "output": output_text,
        "messages": [
            {"role": "system", "content": "Return only valid canonical SWMD-MICRO-0.1 JSON."},
            {"role": "user", "content": f"{instruction}\n\n{input_text}"},
            {"role": "assistant", "content": output_text},
        ],
        "meta": meta,
    }


def _derive_hard_negatives(base_rows: List[Dict[str, Any]], needed: int, rid_start: int) -> List[Dict[str, Any]]:
    candidates = [r for r in base_rows if _parse_micro(str(r.get("output", ""))) is not None]
    out_rows: List[Dict[str, Any]] = []
    if not candidates:
        return out_rows
    rid = rid_start
    op_cycle = [
        ("repair", _corrupt_blank_transition),
        ("id_stability_repair", _corrupt_duplicate_action_id),
        ("schema_normalize", _corrupt_schema_tag),
        ("repair", _corrupt_drop_state_var),
        ("desirability_refine", _corrupt_drop_state_var),
        ("ore_saturation_design", _corrupt_blank_transition),
        ("spool_flow_rewrite", _corrupt_schema_tag),
    ]
    i = 0
    while len(out_rows) < needed:
        src = candidates[i % len(candidates)]
        good = _parse_micro(str(src.get("output", "")))
        if good is None:
            i += 1
            continue
        op, fn = op_cycle[i % len(op_cycle)]
        bad = fn(good)
        rid += 1
        out_rows.append(
            _mk_row(
                rid=rid,
                operation=op,
                inp=bad,
                out=good,
                meta={
                    "source_id": src.get("id"),
                    "source_task": src.get("task_type"),
                    "corruption": fn.__name__,
                },
            )
        )
        i += 1
    return out_rows


def main() -> int:
    p = argparse.ArgumentParser(description="Expand QLoRA rows with hard-negative repair/style operations.")
    p.add_argument("--in-dir", type=str, required=True)
    p.add_argument("--target-total", type=int, default=2000)
    p.add_argument("--train-file", type=str, default="train.jsonl")
    p.add_argument("--val-file", type=str, default="val.jsonl")
    p.add_argument("--out-prefix", type=str, default="aug")
    args = p.parse_args()

    in_dir = Path(args.in_dir)
    train_path = in_dir / args.train_file
    val_path = in_dir / args.val_file
    train = _read_jsonl(train_path)
    val = _read_jsonl(val_path)
    all_rows = train + val
    if not all_rows:
        raise SystemExit("no rows found")

    current = len(all_rows)
    if current >= args.target_total:
        needed = 0
    else:
        needed = args.target_total - current
    rid_start = 0
    for r in all_rows:
        sid = str(r.get("id", ""))
        if sid.startswith("hn_"):
            try:
                rid_start = max(rid_start, int(sid.split("_", 1)[1]))
            except Exception:
                pass
        elif sid.startswith("ex_"):
            try:
                rid_start = max(rid_start, int(sid.split("_", 1)[1]))
            except Exception:
                pass

    extra = _derive_hard_negatives(all_rows, needed, rid_start)
    # Keep original val unchanged; append extras to train for adapter capacity.
    train_aug = train + extra
    val_aug = val

    train_aug_path = in_dir / f"{args.out_prefix}_train.jsonl"
    val_aug_path = in_dir / f"{args.out_prefix}_val.jsonl"
    msg_train_aug_path = in_dir / f"{args.out_prefix}_train_messages.jsonl"
    msg_val_aug_path = in_dir / f"{args.out_prefix}_val_messages.jsonl"
    stats_path = in_dir / f"{args.out_prefix}_stats.json"

    _write_jsonl(train_aug_path, train_aug)
    _write_jsonl(val_aug_path, val_aug)
    _write_jsonl(msg_train_aug_path, [{"id": r["id"], "messages": r["messages"], "meta": r.get("meta", {})} for r in train_aug])
    _write_jsonl(msg_val_aug_path, [{"id": r["id"], "messages": r["messages"], "meta": r.get("meta", {})} for r in val_aug])

    hist: Dict[str, int] = {}
    for r in train_aug + val_aug:
        t = str(r.get("task_type", "unknown"))
        hist[t] = hist.get(t, 0) + 1
    stats = {
        "source_rows": current,
        "target_total": args.target_total,
        "added_rows": len(extra),
        "rows_total": len(train_aug) + len(val_aug),
        "rows_train": len(train_aug),
        "rows_val": len(val_aug),
        "task_histogram": hist,
        "files": {
            "train": str(train_aug_path),
            "val": str(val_aug_path),
            "train_messages": str(msg_train_aug_path),
            "val_messages": str(msg_val_aug_path),
        },
    }
    stats_path.write_text(json.dumps(stats, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(train_aug_path))
    print(str(val_aug_path))
    print(str(stats_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
