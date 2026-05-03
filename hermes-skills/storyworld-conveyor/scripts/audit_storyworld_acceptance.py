#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


ENDING_PREFIXES = ("page_end", "page_epilogue")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def text_value(script: Any) -> str:
    if isinstance(script, str):
        return script
    if isinstance(script, dict) and isinstance(script.get("value"), str):
        return script["value"]
    return ""


def starting_encounter(data: dict[str, Any], explicit: str | None) -> str | None:
    encounter_ids = {e.get("id") for e in data.get("encounters", [])}
    if explicit:
        return explicit if explicit in encounter_ids else None
    if "page_0000" in encounter_ids:
        return "page_0000"
    spools = [s for s in data.get("spools", []) if s.get("starts_active")]
    spools.sort(key=lambda s: s.get("creation_index", 0))
    for spool in spools:
        for eid in spool.get("encounters") or []:
            if eid in encounter_ids:
                return eid
    encounters = data.get("encounters", [])
    return encounters[0].get("id") if encounters else None


def collect_bounded_number_refs(node: Any, refs: list[tuple[str | None, str | None]]) -> None:
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Pointer":
            keyring = node.get("keyring") or []
            refs.append((node.get("character"), keyring[0] if keyring else None))
        for value in node.values():
            collect_bounded_number_refs(value, refs)
    elif isinstance(node, list):
        for item in node:
            collect_bounded_number_refs(item, refs)


def count_nonliteral_visibility(data: dict[str, Any]) -> int:
    count = 0
    for encounter in data.get("encounters", []):
        for option in encounter.get("options", []) or []:
            script = option.get("visibility_script", True)
            if script is not True and script is not None:
                count += 1
    return count


def audit(data: dict[str, Any], start_id: str | None, max_turns: int, reader_path: Path | None) -> dict[str, Any]:
    encounters = data.get("encounters", []) or []
    encounter_ids = [e.get("id") for e in encounters]
    encounter_set = {eid for eid in encounter_ids if isinstance(eid, str)}
    encounter_by_id = {e.get("id"): e for e in encounters if isinstance(e.get("id"), str)}
    start = starting_encounter(data, start_id)

    option_locations: dict[str, list[str]] = defaultdict(list)
    reaction_locations: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    missing_consequences: list[dict[str, str | None]] = []
    edges: dict[str, list[str]] = defaultdict(list)

    for encounter in encounters:
        eid = encounter.get("id")
        for option in encounter.get("options", []) or []:
            oid = option.get("id")
            if isinstance(oid, str):
                option_locations[oid].append(eid)
            for reaction in option.get("reactions", []) or []:
                rid = reaction.get("id")
                cid = reaction.get("consequence_id")
                if isinstance(rid, str):
                    reaction_locations[rid].append({"encounter": eid, "option": oid, "consequence": cid})
                if isinstance(cid, str) and cid:
                    edges[eid].append(cid)
                    if cid != "wild" and cid not in encounter_set:
                        missing_consequences.append(
                            {"encounter": eid, "option": oid, "reaction": rid, "consequence": cid}
                        )

    duplicate_encounters = sorted([eid for eid, count in Counter(encounter_ids).items() if count > 1])
    duplicate_options = {oid: locs for oid, locs in sorted(option_locations.items()) if len(locs) > 1}
    duplicate_reactions = {rid: locs for rid, locs in sorted(reaction_locations.items()) if len(locs) > 1}

    inbound = Counter(
        cid for targets in edges.values() for cid in targets if isinstance(cid, str) and cid in encounter_set
    )
    zero_inbound = sorted(eid for eid in encounter_set if eid != start and inbound[eid] == 0)

    reachable: set[str] = set()
    if start:
        queue: deque[str] = deque([start])
        reachable.add(start)
        while queue:
            eid = queue.popleft()
            for target in edges[eid]:
                if target in encounter_set and target not in reachable:
                    reachable.add(target)
                    queue.append(target)
    unreachable = sorted(eid for eid in encounter_set if eid not in reachable)

    reachable_turns: dict[str, set[int]] = defaultdict(set)
    if start:
        queue_turns: deque[tuple[str, int]] = deque([(start, 0)])
        reachable_turns[start].add(0)
        while queue_turns:
            eid, turn = queue_turns.popleft()
            if turn >= max_turns:
                continue
            for target in edges[eid]:
                if target not in encounter_set:
                    continue
                next_turn = turn + 1
                if next_turn not in reachable_turns[target]:
                    reachable_turns[target].add(next_turn)
                    queue_turns.append((target, next_turn))

    terminal_pages = sorted(
        eid for eid, encounter in encounter_by_id.items() if not (encounter.get("options", []) or [])
    )
    terminal_non_endings = [
        eid for eid in terminal_pages if not eid.startswith(ENDING_PREFIXES)
    ]
    terminal_window_failures: dict[str, dict[str, Any]] = {}
    for eid in terminal_pages:
        encounter = encounter_by_id[eid]
        earliest = int(encounter.get("earliest_turn", 0))
        latest = int(encounter.get("latest_turn", 999999))
        turns = sorted(reachable_turns.get(eid, set()))
        invalid_turns = [turn for turn in turns if turn < earliest or turn > latest]
        if invalid_turns:
            terminal_window_failures[eid] = {
                "reachable_turns": turns[:20],
                "invalid_turns": invalid_turns[:20],
                "earliest_turn": earliest,
                "latest_turn": latest,
            }

    character_ids = {c.get("id") for c in data.get("characters", []) or []}
    property_ids = {
        prop.get("id")
        for prop in data.get("authored_properties", []) or []
        if isinstance(prop, dict)
    } | {
        prop.get("property_name")
        for prop in data.get("authored_properties", []) or []
        if isinstance(prop, dict)
    }
    bounded_refs: list[tuple[str | None, str | None]] = []
    collect_bounded_number_refs(data, bounded_refs)
    bad_bounded_refs = sorted(
        {
            f"{char}.{prop}"
            for char, prop in bounded_refs
            if char not in character_ids or prop not in property_ids
        }
    )

    spool_ids = {s.get("id") for s in data.get("spools", []) or []}
    bad_spool_refs = []
    for encounter in encounters:
        for spool_id in encounter.get("connected_spools", []) or []:
            if spool_id not in spool_ids:
                bad_spool_refs.append({"encounter": encounter.get("id"), "spool": spool_id})
    for spool in data.get("spools", []) or []:
        for eid in spool.get("encounters", []) or []:
            if eid not in encounter_set:
                bad_spool_refs.append({"spool": spool.get("id"), "encounter": eid})

    nonliteral_visibility = count_nonliteral_visibility(data)
    reader_findings: list[str] = []
    if reader_path and reader_path.exists():
        reader_text = reader_path.read_text(encoding="utf-8", errors="replace")
        if nonliteral_visibility and "return opt.visibility_script === true || opt.visibility_script === undefined" in reader_text:
            reader_findings.append(
                "reader hides nonliteral visibility scripts; gated options will not appear in manual playtest"
            )
        if re.search(r"const\s+reaction\s*=\s*option\.reactions\[0\]", reader_text):
            multi_reaction_options = sum(
                1
                for encounter in encounters
                for option in encounter.get("options", []) or []
                if len(option.get("reactions", []) or []) > 1
            )
            if multi_reaction_options:
                reader_findings.append(
                    f"reader always selects first reaction; {multi_reaction_options} multi-reaction options are not exercised"
                )
    elif reader_path:
        reader_findings.append(f"reader file not found: {reader_path}")

    failures: list[str] = []
    if not start:
        failures.append("missing_start_encounter")
    if duplicate_encounters:
        failures.append("duplicate_encounter_ids")
    if duplicate_options:
        failures.append("duplicate_option_ids")
    if duplicate_reactions:
        failures.append("duplicate_reaction_ids")
    if missing_consequences:
        failures.append("missing_consequence_targets")
    if bad_spool_refs:
        failures.append("bad_spool_refs")
    if bad_bounded_refs:
        failures.append("bad_bounded_number_refs")
    if unreachable:
        failures.append("unreachable_encounters")
    if zero_inbound:
        failures.append("zero_inbound_encounters")
    if terminal_non_endings:
        failures.append("terminal_non_endings")
    if terminal_window_failures:
        failures.append("terminal_turn_window_failures")
    if reader_findings:
        failures.append("reader_compatibility")

    return {
        "pass": not failures,
        "failures": failures,
        "summary": {
            "encounters": len(encounters),
            "options": sum(len(e.get("options", []) or []) for e in encounters),
            "reactions": sum(
                len(o.get("reactions", []) or [])
                for e in encounters
                for o in e.get("options", []) or []
            ),
            "start_encounter": start,
            "terminal_pages": len(terminal_pages),
            "nonliteral_visibility_options": nonliteral_visibility,
        },
        "duplicate_encounter_ids": duplicate_encounters,
        "duplicate_option_ids": duplicate_options,
        "duplicate_reaction_ids": duplicate_reactions,
        "missing_consequences": missing_consequences,
        "bad_spool_refs": bad_spool_refs,
        "bad_bounded_number_refs": bad_bounded_refs,
        "unreachable_encounters": unreachable,
        "zero_inbound_encounters": zero_inbound,
        "terminal_non_endings": terminal_non_endings,
        "terminal_turn_window_failures": terminal_window_failures,
        "reader_findings": reader_findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run hard acceptance checks for a SweepWeave storyworld.")
    parser.add_argument("--storyworld", required=True, help="Path to the storyworld JSON file.")
    parser.add_argument("--reader", help="Optional path to storyworld_reader.html for compatibility checks.")
    parser.add_argument("--start-id", help="Override the inferred starting encounter id.")
    parser.add_argument("--max-turns", type=int, default=80, help="Maximum turns for route-window exploration.")
    parser.add_argument("--out-json", help="Optional path for the JSON audit report.")
    args = parser.parse_args()

    storyworld_path = Path(args.storyworld)
    data = load_json(storyworld_path)
    report = audit(
        data=data,
        start_id=args.start_id,
        max_turns=args.max_turns,
        reader_path=Path(args.reader) if args.reader else None,
    )
    report["storyworld"] = str(storyworld_path)

    rendered = json.dumps(report, indent=2, ensure_ascii=True)
    if args.out_json:
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered + "\n", encoding="utf-8", newline="\n")
        print(out)
    else:
        print(rendered)

    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
