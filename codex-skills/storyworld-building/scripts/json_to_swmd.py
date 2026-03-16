"""
Convert SweepWeave storyworld JSON into compact SWMD markdown.

Usage:
  python json_to_swmd.py input.json output.md
  python json_to_swmd.py input.json output.md --mode minified
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_number(value: Any) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return text if text else "0"
    return str(value)


def script_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if value.get("pointer_type") == "String Constant":
            return str(value.get("value", ""))
        if "value" in value and isinstance(value["value"], str):
            return value["value"]
    return ""


def format_prop_path(keyring: Iterable[str]) -> str:
    parts = list(keyring or [])
    if not parts:
        return "Unknown"
    head = parts[0]
    if len(parts) == 1:
        return head
    tail = "".join(f"[{p}]" for p in parts[1:])
    return f"{head}{tail}"


def pointer_expr(pointer: Dict[str, Any]) -> str:
    ptype = pointer.get("pointer_type", "")
    if "Constant" in ptype:
        value = pointer.get("value", pointer.get("coefficient", 0))
        return f"C({normalize_number(value)})"
    if "Property" in ptype or "Pointer" in ptype:
        char = pointer.get("character", "unknown")
        keyring = pointer.get("keyring", [])
        coeff = pointer.get("coefficient", 1)
        base = f"P({char}.{format_prop_path(keyring)})"
        if coeff != 1:
            return f"MUL({base},{normalize_number(coeff)})"
        return base
    return "C(0)"


def expr(node: Any) -> str:
    if isinstance(node, bool):
        return "C(1)" if node else "C(0)"
    if isinstance(node, (int, float)):
        return f"C({normalize_number(node)})"
    if not isinstance(node, dict):
        return "C(0)"

    if node.get("script_element_type") in {"Bounded Number Operator", "Operator"}:
        op = str(node.get("operator_type", "UNKNOWN")).upper()
        operands = node.get("operands", [])
        rendered = ",".join(expr(o) for o in operands)
        op_map = {
            "ADDITION": "ADD",
            "SUBTRACTION": "SUB",
            "MULTIPLICATION": "MUL",
            "DIVISION": "DIV",
            "MINIMUM": "MIN",
            "MAXIMUM": "MAX",
        }
        opname = op_map.get(op, op)
        return f"{opname}({rendered})"

    if node.get("script_element_type") == "Pointer" or "pointer_type" in node:
        return pointer_expr(node)

    return "C(0)"


def target_of_set(effect: Dict[str, Any]) -> Tuple[str, List[str]]:
    target = effect.get("Set", {})
    char = target.get("character", "unknown")
    keyring = target.get("keyring", [])
    return char, keyring


def extract_additive_delta(
    to_node: Dict[str, Any], target_char: str, target_keyring: List[str]
) -> Optional[float]:
    if to_node.get("script_element_type") not in {"Bounded Number Operator", "Operator"}:
        return None
    if str(to_node.get("operator_type", "")).lower() != "addition":
        return None
    operands = to_node.get("operands", [])
    if len(operands) != 2:
        return None

    def is_target_ptr(obj: Any) -> bool:
        if not isinstance(obj, dict):
            return False
        return (
            obj.get("character") == target_char
            and list(obj.get("keyring", [])) == list(target_keyring)
            and "Property" in str(obj.get("pointer_type", ""))
        )

    def const_value(obj: Any) -> Optional[float]:
        if not isinstance(obj, dict):
            return None
        if "Constant" not in str(obj.get("pointer_type", "")):
            return None
        value = obj.get("value", obj.get("coefficient"))
        if isinstance(value, (int, float)):
            return float(value)
        return None

    if is_target_ptr(operands[0]):
        return const_value(operands[1])
    if is_target_ptr(operands[1]):
        return const_value(operands[0])
    return None


def effect_line(effect: Dict[str, Any]) -> str:
    char, keyring = target_of_set(effect)
    prop_path = format_prop_path(keyring)
    to_node = effect.get("to", {})
    delta = extract_additive_delta(to_node, char, keyring)
    if delta is not None:
        return f"SET {char}.{prop_path} += {normalize_number(delta)}"
    return f"SET {char}.{prop_path} = {expr(to_node)}"


def encounter_order(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    by_id = {e.get("id"): e for e in data.get("encounters", []) if e.get("id")}
    ordered_ids: List[str] = []
    for spool in sorted(
        data.get("spools", []),
        key=lambda s: (s.get("creation_index", 10**9), s.get("id", "")),
    ):
        for enc_id in spool.get("encounters", []) or []:
            if enc_id in by_id and enc_id not in ordered_ids:
                ordered_ids.append(enc_id)
    for enc_id in sorted(by_id.keys()):
        if enc_id not in ordered_ids:
            ordered_ids.append(enc_id)
    return [by_id[eid] for eid in ordered_ids]


def fmt_list(values: Iterable[str]) -> str:
    vals = [v for v in values if v]
    return ", ".join(vals)


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return normalize_number(value)
    text = str(value or "")
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def is_terminal(enc: Dict[str, Any]) -> bool:
    return not bool(enc.get("options") or [])


def infer_ending_type(enc: Dict[str, Any]) -> str:
    eid = str(enc.get("id", "")).lower()
    title = str(enc.get("title", "")).lower()
    text = script_text(enc.get("text_script")).lower()
    hay = " ".join([eid, title, text])
    if any(k in hay for k in ("success", "victory", "aligned", "rescued", "escape")):
        return "success"
    if any(k in hay for k in ("failure", "defeat", "captured", "collapse", "dead", "loss")):
        return "failure"
    return "terminal"


def extract_threshold_clauses(node: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(node, bool):
        return out
    if not isinstance(node, dict):
        return out
    if str(node.get("operator_type", "")) == "And":
        for operand in node.get("operands", []) or []:
            out.extend(extract_threshold_clauses(operand))
        return out
    if str(node.get("operator_type", "")) != "Arithmetic Comparator":
        return out
    operands = list(node.get("operands", []) or [])
    if len(operands) != 2:
        return out
    left, right = operands
    left_keyring = list(left.get("keyring", []) or []) if isinstance(left, dict) else []
    right_keyring = list(right.get("keyring", []) or []) if isinstance(right, dict) else []
    left_val = left.get("value") if isinstance(left, dict) else None
    right_val = right.get("value") if isinstance(right, dict) else None
    subtype = str(node.get("operator_subtype", "") or "")
    op_map = {
        "Greater Than or Equal To": ">=",
        "Greater Than": ">",
        "Less Than or Equal To": "<=",
        "Less Than": "<",
        "Equal To": "==",
    }
    op = op_map.get(subtype, "")
    if left_keyring and isinstance(right_val, (int, float)) and op:
        out.append({"var": str(left_keyring[0]), "op": op, "threshold": float(right_val)})
    elif right_keyring and isinstance(left_val, (int, float)) and op:
        invert = {">=": "<=", ">": "<", "<=": ">=", "<": ">", "==": "=="}
        out.append({"var": str(right_keyring[0]), "op": invert[op], "threshold": float(left_val)})
    return out


def ending_expected_score(ending_type: str) -> float:
    if ending_type == "success":
        return 1.0
    if ending_type == "failure":
        return -1.0
    return 0.0


def build_frontmatter_lines(data: Dict[str, Any]) -> List[str]:
    terminals = sorted(
        [e for e in data.get("encounters", []) if is_terminal(e)],
        key=lambda e: str(e.get("id", "")),
    )
    state_vars = sorted(
        [
            str(p.get("id", ""))
            for p in data.get("authored_properties", [])
            if str(p.get("id", "")) and int(p.get("depth", 0) or 0) == 0
        ]
    )
    lines: List[str] = []
    lines.append("---")
    lines.append(f'title: {yaml_scalar(data.get("storyworld_title", ""))}')
    lines.append(f'version: {yaml_scalar(data.get("sweepweave_version", ""))}')
    lines.append(f'storyworld_id: {yaml_scalar(data.get("IFID", ""))}')
    lines.append('environment_type: "SWEEPWEAVE_STORYWORLD"')
    lines.append('source_format: "SWMD-0-MIN"')
    lines.append("state_variables:")
    if state_vars:
        for p in state_vars:
            lines.append(f"  - {yaml_scalar(p)}")
    else:
        lines.append('  - "none"')
    lines.append("endings:")
    if terminals:
        for enc in terminals:
            ending_id = str(enc.get("id", ""))
            ending_type = infer_ending_type(enc)
            acceptability = enc.get("acceptability_script", True)
            condition = expr(acceptability) if isinstance(acceptability, dict) else ("true" if bool(acceptability) else "false")
            desc = script_text(enc.get("text_script")) or str(enc.get("title", "")) or ending_id
            if len(desc) > 180:
                desc = desc[:177] + "..."
            lines.append(f"  - id: {yaml_scalar(ending_id)}")
            lines.append(f"    type: {yaml_scalar(ending_type)}")
            lines.append(f"    condition: {yaml_scalar(condition)}")
            lines.append(f"    description: {yaml_scalar(desc)}")
            lines.append(f"    expected_critic_score: {normalize_number(ending_expected_score(ending_type))}")
            clauses = extract_threshold_clauses(enc.get("acceptability_script", True))
            if clauses:
                lines.append("    proximity_spec:")
                for clause in clauses:
                    lines.append(f"      - var: {yaml_scalar(clause['var'])}")
                    lines.append(f"        op: {yaml_scalar(clause['op'])}")
                    lines.append(f"        threshold: {normalize_number(clause['threshold'])}")
    else:
        lines.append('  - id: "none"')
        lines.append('    type: "terminal"')
        lines.append('    condition: "false"')
        lines.append('    description: "No terminal encounter detected."')
        lines.append("    expected_critic_score: 0")
    lines.append("---")
    return lines


def emit_full(data: Dict[str, Any]) -> str:
    characters = [c.get("id", "") for c in data.get("characters", [])]
    props = [p.get("id", "") for p in data.get("authored_properties", [])]
    spools = sorted(
        data.get("spools", []),
        key=lambda s: (s.get("creation_index", 10**9), s.get("id", "")),
    )
    spool_ids = [s.get("id", "") for s in spools]

    lines: List[str] = []
    lines.extend(build_frontmatter_lines(data))
    lines.append("")
    lines.append("# SWMD-0")
    lines.append(f"id: {data.get('IFID', '')}")
    lines.append(f"title: {data.get('storyworld_title', '')}")
    lines.append(f"theme: {data.get('css_theme', '')}")
    lines.append(f"about: {script_text(data.get('about_text'))}")
    lines.append(f"cast: {fmt_list(characters)}")
    lines.append(f"props: {fmt_list(props)}")
    lines.append("spools:")
    for spool in spools:
        sid = spool.get("id", "")
        encs = " ".join(spool.get("encounters", []) or [])
        lines.append(f"  {sid}: {encs}")
    if not spool_ids:
        lines.append("  none:")
    lines.append("")

    for enc in encounter_order(data):
        enc_id = enc.get("id", "")
        title = enc.get("title", "")
        earliest = enc.get("earliest_turn", "?")
        latest = enc.get("latest_turn", "?")
        connected = ",".join(enc.get("connected_spools", []) or [])
        lines.append(
            f"## ENC {enc_id} | {title} | turn={earliest}..{latest} | spools=[{connected}]"
        )
        lines.append(f"T: {script_text(enc.get('text_script'))}")
        lines.append("")
        options = sorted(enc.get("options", []) or [], key=lambda o: o.get("id", ""))
        for opt in options:
            opt_id = opt.get("id", "")
            lines.append(f"OPT {opt_id}: {script_text(opt.get('text_script'))}")
            reactions = sorted(opt.get("reactions", []) or [], key=lambda r: r.get("id", ""))
            for rxn in reactions:
                rxn_id = rxn.get("id", "")
                consequence = rxn.get("consequence_id", "")
                lines.append(f"  RXN {rxn_id} -> {consequence}")
                lines.append(f"    T: {script_text(rxn.get('text_script'))}")
                lines.append("    E:")
                effects = sorted(
                    rxn.get("after_effects", []) or [],
                    key=lambda e: (
                        e.get("Set", {}).get("character", ""),
                        format_prop_path(e.get("Set", {}).get("keyring", [])),
                    ),
                )
                if not effects:
                    lines.append("      SET none = C(0)")
                else:
                    for eff in effects:
                        lines.append(f"      {effect_line(eff)}")
                desirability = rxn.get("desirability_script")
                if desirability is not None:
                    lines.append(f"    D: {expr(desirability)}")
                lines.append("")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def emit_minified(data: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.extend(build_frontmatter_lines(data))
    lines.append("")
    lines.append("# SWMD-0-MIN")
    lines.append(f"id: {data.get('IFID', '')}")
    lines.append(f"title: {data.get('storyworld_title', '')}")
    lines.append("")

    for enc in encounter_order(data):
        enc_id = enc.get("id", "")
        earliest = enc.get("earliest_turn", "?")
        latest = enc.get("latest_turn", "?")
        lines.append(f"ENC {enc_id} turn={earliest}..{latest}")
        options = sorted(enc.get("options", []) or [], key=lambda o: o.get("id", ""))
        for opt in options:
            opt_id = opt.get("id", "")
            opt_text = script_text(opt.get("text_script"))
            reactions = sorted(opt.get("reactions", []) or [], key=lambda r: r.get("id", ""))
            for rxn in reactions:
                rxn_id = rxn.get("id", "")
                consequence = rxn.get("consequence_id", "")
                effects = sorted(
                    rxn.get("after_effects", []) or [],
                    key=lambda e: (
                        e.get("Set", {}).get("character", ""),
                        format_prop_path(e.get("Set", {}).get("keyring", [])),
                    ),
                )
                effect_blob = "; ".join(effect_line(eff) for eff in effects) if effects else "SET none = C(0)"
                desirability = rxn.get("desirability_script")
                d_blob = expr(desirability) if desirability is not None else "C(0)"
                lines.append(
                    f"ORX {opt_id}/{rxn_id} -> {consequence} | O:{opt_text} | E:{effect_blob} | D:{d_blob}"
                )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert SweepWeave JSON to SWMD markdown.")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_md", type=Path)
    parser.add_argument(
        "--mode",
        choices=["full", "minified"],
        default="full",
        help="Output style: full SWMD-0 blocks or minified one-liners.",
    )
    args = parser.parse_args()

    data = load_json(args.input_json)
    swmd = emit_full(data) if args.mode == "full" else emit_minified(data)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(swmd, encoding="utf-8")


if __name__ == "__main__":
    main()
