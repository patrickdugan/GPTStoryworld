#!/usr/bin/env python3
"""Build Hilbert-manifold pathing packets for storyworld conveyor runs.

The packet treats each encounter as a compact vector over graph depth,
distance-to-secret-loci, gate density, branching, effect support, and
pValue/p2Value support. It is not a proof of narrative quality; it is a
bounded control-plane artifact that tells the conveyor where to add bridge
turns, where secret routes are too close/far, and which encounters should
carry stronger clue/gate support.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter, deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def _text(value: Any, limit: int = 240) -> str:
    if isinstance(value, str):
        return value.strip()[:limit]
    if isinstance(value, dict):
        for key in ("value", "description", "label", "text"):
            if isinstance(value.get(key), str):
                return value[key].strip()[:limit]
    return ""


def _is_true_script(script: Any) -> bool:
    if script is True or script is None:
        return True
    if isinstance(script, dict) and script.get("pointer_type") == "Boolean Constant":
        return bool(script.get("value", False))
    return False


def _collect_refs(node: Any, refs: Counter[str], pvalue_refs: List[str], p2value_refs: List[str]) -> None:
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Pointer":
            keyring = node.get("keyring") or []
            if isinstance(keyring, list) and keyring:
                prop = str(keyring[0])
                refs[prop] += 1
                if len(keyring) >= 2:
                    pvalue_refs.append(prop)
                if len(keyring) >= 3:
                    p2value_refs.append(prop)
        for child in node.values():
            _collect_refs(child, refs, pvalue_refs, p2value_refs)
    elif isinstance(node, list):
        for child in node:
            _collect_refs(child, refs, pvalue_refs, p2value_refs)


def _operator_count(node: Any) -> int:
    if isinstance(node, dict):
        here = 1 if node.get("operator_type") else 0
        return here + sum(_operator_count(child) for child in node.values())
    if isinstance(node, list):
        return sum(_operator_count(child) for child in node)
    return 0


def _is_terminal(encounter: Dict[str, Any]) -> bool:
    eid = str(encounter.get("id", "") or "")
    return (
        bool(encounter.get("is_ending"))
        or eid.startswith("page_end_")
        or eid.startswith("page_secret_")
        or not (encounter.get("options", []) or [])
    )


def _is_secret_locus(encounter: Dict[str, Any]) -> bool:
    eid = str(encounter.get("id", "") or "").lower()
    title = _text(encounter.get("title"), 200).lower()
    return eid.startswith("page_secret_") or bool(encounter.get("is_secret_ending")) or (
        _is_terminal(encounter) and "secret" in title
    )


def _safe_id(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in value)
    return safe or "unknown"


def build_graph(world: Dict[str, Any]) -> Dict[str, Any]:
    encounters = [enc for enc in world.get("encounters", []) or [] if isinstance(enc, dict) and enc.get("id")]
    by_id = {str(enc["id"]): enc for enc in encounters}
    adjacency: Dict[str, List[Dict[str, Any]]] = {eid: [] for eid in by_id}
    reverse: Dict[str, List[str]] = {eid: [] for eid in by_id}
    edge_count = 0
    missing_targets: List[Dict[str, Any]] = []
    for enc in encounters:
        source = str(enc["id"])
        for opt_index, opt in enumerate(enc.get("options", []) or []):
            option_id = str(opt.get("id", f"opt_{opt_index}") or f"opt_{opt_index}")
            for rxn_index, rxn in enumerate(opt.get("reactions", []) or []):
                target = str(rxn.get("consequence_id", "") or "")
                if not target or target == "wild":
                    continue
                edge = {
                    "source": source,
                    "option_id": option_id,
                    "reaction_index": rxn_index,
                    "target": target,
                }
                adjacency.setdefault(source, []).append(edge)
                edge_count += 1
                if target in reverse:
                    reverse[target].append(source)
                else:
                    missing_targets.append(edge)
    start_id = "page_0000" if "page_0000" in by_id else (str(encounters[0]["id"]) if encounters else "")
    return {
        "encounters": encounters,
        "by_id": by_id,
        "adjacency": adjacency,
        "reverse": reverse,
        "start_id": start_id,
        "edge_count": edge_count,
        "missing_targets": missing_targets,
    }


def bfs_depths(start: str, adjacency: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
    if not start:
        return {}
    depths = {start: 0}
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        for edge in adjacency.get(node, []):
            target = edge["target"]
            if target not in depths:
                depths[target] = depths[node] + 1
                queue.append(target)
    return depths


def reverse_distances(secret_id: str, reverse: Dict[str, List[str]]) -> Dict[str, int]:
    distances = {secret_id: 0}
    queue: deque[str] = deque([secret_id])
    while queue:
        node = queue.popleft()
        for parent in reverse.get(node, []):
            if parent not in distances:
                distances[parent] = distances[node] + 1
                queue.append(parent)
    return distances


def count_paths_capped(
    source: str,
    target: str,
    adjacency: Dict[str, List[Dict[str, Any]]],
    cap: int,
    max_depth: int,
) -> int:
    count = 0
    stack: List[Tuple[str, int, Set[str]]] = [(source, 0, {source})]
    while stack and count < cap:
        node, depth, seen = stack.pop()
        if node == target:
            count += 1
            continue
        if depth >= max_depth:
            continue
        for edge in adjacency.get(node, []):
            nxt = edge["target"]
            if nxt in seen:
                continue
            stack.append((nxt, depth + 1, seen | {nxt}))
    return count


def encounter_stats(encounter: Dict[str, Any]) -> Dict[str, Any]:
    refs: Counter[str] = Counter()
    pvalue_refs: List[str] = []
    p2value_refs: List[str] = []
    option_count = 0
    gated_options = 0
    reaction_count = 0
    effect_count = 0
    effect_targets: Counter[str] = Counter()
    operator_complexity = 0
    clue_text_hits = 0

    title_body = " ".join(
        [
            _text(encounter.get("title"), 400),
            _text(encounter.get("body"), 800),
            _text(encounter.get("text"), 800),
        ]
    ).lower()
    for word in ("secret", "clue", "hidden", "witness", "threshold", "reveal", "unmask", "route"):
        if word in title_body:
            clue_text_hits += 1

    for opt in encounter.get("options", []) or []:
        option_count += 1
        if not _is_true_script(opt.get("visibility_script", True)) or not _is_true_script(
            opt.get("performability_script", True)
        ):
            gated_options += 1
        _collect_refs(opt.get("visibility_script"), refs, pvalue_refs, p2value_refs)
        _collect_refs(opt.get("performability_script"), refs, pvalue_refs, p2value_refs)
        _collect_refs(opt.get("desirability_script"), refs, pvalue_refs, p2value_refs)
        operator_complexity += _operator_count(opt.get("visibility_script"))
        operator_complexity += _operator_count(opt.get("performability_script"))
        operator_complexity += _operator_count(opt.get("desirability_script"))
        for rxn in opt.get("reactions", []) or []:
            reaction_count += 1
            _collect_refs(rxn.get("desirability_script"), refs, pvalue_refs, p2value_refs)
            operator_complexity += _operator_count(rxn.get("desirability_script"))
            for eff in rxn.get("after_effects", []) or rxn.get("effects", []) or []:
                effect_count += 1
                _collect_refs(eff, refs, pvalue_refs, p2value_refs)
                operator_complexity += _operator_count(eff)
                set_obj = eff.get("Set", {}) if isinstance(eff, dict) else {}
                keyring = set_obj.get("keyring") if isinstance(set_obj, dict) else []
                if isinstance(keyring, list) and keyring:
                    effect_targets[str(keyring[0])] += 1

    return {
        "option_count": option_count,
        "gated_options": gated_options,
        "reaction_count": reaction_count,
        "effect_count": effect_count,
        "effect_targets": dict(effect_targets),
        "formula_ref_count": sum(refs.values()),
        "distinct_formula_refs": len(refs),
        "pvalue_refs": len(pvalue_refs),
        "p2value_refs": len(p2value_refs),
        "operator_complexity": operator_complexity,
        "clue_text_hits": clue_text_hits,
    }


def clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def hilbert_vector(stats: Dict[str, Any], depth: int | None, nearest_secret_distance: int | None, target_max: int) -> Dict[str, float]:
    options = max(1, int(stats.get("option_count", 0) or 0))
    reactions = max(1, int(stats.get("reaction_count", 0) or 0))
    dist = 999 if nearest_secret_distance is None else max(0, int(nearest_secret_distance))
    depth_value = target_max + 1 if depth is None else max(0, int(depth))
    return {
        "depth": round(clip01(depth_value / max(1, target_max)), 4),
        "secret_affinity": round(1.0 / (1.0 + dist), 4),
        "gate_density": round(clip01(float(stats.get("gated_options", 0) or 0) / options), 4),
        "branching": round(clip01(options / 3.2), 4),
        "reaction_support": round(clip01((float(stats.get("reaction_count", 0) or 0) / options) / 2.5), 4),
        "effect_support": round(clip01((float(stats.get("effect_count", 0) or 0) / reactions) / 4.5), 4),
        "pvalue_support": round(clip01(float(stats.get("pvalue_refs", 0) or 0) / max(1, options * 2)), 4),
        "p2value_support": round(clip01(float(stats.get("p2value_refs", 0) or 0) / max(1, options)), 4),
        "clue_signal": round(clip01(float(stats.get("clue_text_hits", 0) or 0) / 2.0), 4),
    }


def weighted_norm(vector: Dict[str, float]) -> float:
    weights = {
        "depth": 0.9,
        "secret_affinity": 1.2,
        "gate_density": 0.85,
        "branching": 0.7,
        "reaction_support": 0.7,
        "effect_support": 0.7,
        "pvalue_support": 1.0,
        "p2value_support": 1.0,
        "clue_signal": 0.8,
    }
    return round(math.sqrt(sum(weights[k] * float(vector.get(k, 0.0)) ** 2 for k in weights)), 4)


def locus_distance(vector: Dict[str, float], ideal: Dict[str, float] | None = None) -> float:
    target = ideal or {
        "depth": 0.85,
        "secret_affinity": 1.0,
        "gate_density": 0.35,
        "branching": 1.0,
        "reaction_support": 1.0,
        "effect_support": 1.0,
        "pvalue_support": 1.0,
        "p2value_support": 0.75,
        "clue_signal": 1.0,
    }
    weights = {
        "depth": 0.7,
        "secret_affinity": 1.2,
        "gate_density": 0.8,
        "branching": 0.45,
        "reaction_support": 0.45,
        "effect_support": 0.55,
        "pvalue_support": 0.9,
        "p2value_support": 0.8,
        "clue_signal": 0.7,
    }
    return round(math.sqrt(sum(weights[k] * (float(vector.get(k, 0.0)) - target[k]) ** 2 for k in weights)), 4)


def turn_band(depth: int | None, target_min: int, target_max: int) -> str:
    if depth is None:
        return "unreachable"
    if depth < max(1, target_min // 3):
        return "act1"
    if depth < max(2, (2 * target_min) // 3):
        return "act2"
    if depth <= target_max:
        return "act3"
    return "overlong"


def row_advice(
    encounter_id: str,
    depth: int | None,
    nearest_dist: int | None,
    vector: Dict[str, float],
    target_min: int,
    target_max: int,
    is_secret: bool,
) -> List[Dict[str, Any]]:
    advice: List[Dict[str, Any]] = []
    if depth is None:
        advice.append(
            {
                "action": "repair_unreachable_dag_node",
                "reason": "Encounter is not reachable from the current start node.",
                "priority": "high",
            }
        )
        return advice
    if is_secret and depth < target_min:
        advice.append(
            {
                "action": "add_bridge_turns_before_secret_locus",
                "reason": "Secret locus is reachable too early for the target turn budget.",
                "turn_deficit": target_min - depth,
                "priority": "high",
            }
        )
    if nearest_dist is None:
        advice.append(
            {
                "action": "create_route_to_secret_locus",
                "reason": "No directed path from this node to a secret ending locus.",
                "priority": "medium",
            }
        )
    elif nearest_dist <= 1 and not is_secret and depth < target_min - 2:
        advice.append(
            {
                "action": "insert_intermediate_investigation_turn",
                "reason": "Node collapses into a secret locus before enough investigation turns accrue.",
                "priority": "medium",
            }
        )
    if vector["pvalue_support"] < 0.4:
        advice.append(
            {
                "action": "add_pvalue_gate_support",
                "reason": "Secret/pathing decisions need first-order belief variables, not just structural gates.",
                "priority": "medium",
            }
        )
    if vector["p2value_support"] < 0.25 and depth >= max(2, target_min // 2):
        advice.append(
            {
                "action": "add_p2value_late_turn_support",
                "reason": "Late secret-route decisions should model what characters believe about each other's beliefs.",
                "priority": "medium",
            }
        )
    if vector["clue_signal"] < 0.5 and nearest_dist is not None and nearest_dist <= 3:
        advice.append(
            {
                "action": "foreshadow_secret_locus",
                "reason": "Near-secret encounter lacks explicit clue/hidden/witness/reveal language.",
                "priority": "low",
            }
        )
    if vector["gate_density"] > 0.9 and depth < max(3, target_min // 3):
        advice.append(
            {
                "action": "relax_early_gate_density",
                "reason": "Early turns are over-gated; reserve hard gates for late pathing control.",
                "priority": "low",
            }
        )
    return advice[:4]


def build_packet(
    world: Dict[str, Any],
    storyworld_path: Path,
    quality_report: Dict[str, Any],
    quality_vector_report: Dict[str, Any],
    target_min: int,
    target_max: int,
    route_cap: int,
) -> Dict[str, Any]:
    graph = build_graph(world)
    encounters: List[Dict[str, Any]] = graph["encounters"]
    by_id: Dict[str, Dict[str, Any]] = graph["by_id"]
    adjacency: Dict[str, List[Dict[str, Any]]] = graph["adjacency"]
    reverse: Dict[str, List[str]] = graph["reverse"]
    start_id = graph["start_id"]
    depths = bfs_depths(start_id, adjacency)
    secret_ids = [str(enc["id"]) for enc in encounters if _is_secret_locus(enc)]
    if not secret_ids:
        secret_ids = [str(enc["id"]) for enc in encounters if _is_terminal(enc) and str(enc.get("id", "")).startswith("page_end_")][-1:]
    secret_distance_maps = {secret_id: reverse_distances(secret_id, reverse) for secret_id in secret_ids}

    rows: List[Dict[str, Any]] = []
    for enc in encounters:
        eid = str(enc["id"])
        stats = encounter_stats(enc)
        dist_items = [
            (secret_id, distmap[eid])
            for secret_id, distmap in secret_distance_maps.items()
            if eid in distmap
        ]
        nearest_secret, nearest_dist = min(dist_items, key=lambda item: item[1]) if dist_items else ("", None)
        depth = depths.get(eid)
        vector = hilbert_vector(stats, depth, nearest_dist, target_max)
        is_secret = eid in secret_ids
        row = {
            "encounter_id": eid,
            "title": _text(enc.get("title"), 180),
            "is_terminal": _is_terminal(enc),
            "is_secret_locus": is_secret,
            "turn_depth": depth,
            "turn_band": turn_band(depth, target_min, target_max),
            "nearest_secret_locus": nearest_secret,
            "directed_turns_to_secret": nearest_dist,
            "hilbert_vector": vector,
            "hilbert_norm": weighted_norm(vector),
            "secret_locus_distance": locus_distance(vector),
            "stats": stats,
            "pathing_advice": row_advice(eid, depth, nearest_dist, vector, target_min, target_max, is_secret),
        }
        rows.append(row)

    route_max_depth = max(target_max + 10, len(encounters) + 3)
    secret_loci: List[Dict[str, Any]] = []
    for secret_id in secret_ids:
        distmap = secret_distance_maps.get(secret_id, {})
        depth = depths.get(secret_id)
        paths = count_paths_capped(start_id, secret_id, adjacency, route_cap, route_max_depth) if start_id else 0
        incoming = len(reverse.get(secret_id, []))
        secret_loci.append(
            {
                "secret_id": secret_id,
                "title": _text(by_id.get(secret_id, {}).get("title"), 180),
                "reachable_from_start": secret_id in depths,
                "min_turn_depth": depth,
                "turn_deficit": max(0, target_min - int(depth or 0)) if depth is not None else target_min,
                "incoming_edges": incoming,
                "upstream_encounter_count": len(distmap),
                "route_count_capped": paths,
                "route_count_cap": route_cap,
                "overexposed": bool(paths >= route_cap or (depth is not None and depth < target_min)),
            }
        )

    reachable_depths = [value for value in depths.values()]
    max_depth = max(reachable_depths) if reachable_depths else 0
    unreachable = sorted(set(by_id) - set(depths))
    rows_with_advice = [row for row in rows if row["pathing_advice"]]
    top_rows = sorted(
        rows_with_advice,
        key=lambda row: (
            0 if any(item.get("priority") == "high" for item in row["pathing_advice"]) else 1,
            row["secret_locus_distance"],
        ),
    )[:20]
    global_advice: List[Dict[str, Any]] = []
    if max_depth < target_min:
        global_advice.append(
            {
                "action": "increase_turn_depth",
                "reason": "Current reachable DAG depth is below the requested minimum turn budget.",
                "current_max_depth": max_depth,
                "target_min_turns": target_min,
                "bridge_turns_needed": target_min - max_depth,
                "priority": "high",
            }
        )
    for locus in secret_loci:
        if not locus["reachable_from_start"]:
            global_advice.append(
                {
                    "action": "repair_secret_locus_reachability",
                    "secret_id": locus["secret_id"],
                    "reason": "Secret locus has no reachable route from start.",
                    "priority": "high",
                }
            )
        elif int(locus.get("turn_deficit") or 0) > 0:
            global_advice.append(
                {
                    "action": "delay_secret_locus_with_bridge_turns",
                    "secret_id": locus["secret_id"],
                    "turn_deficit": locus["turn_deficit"],
                    "reason": "Secret locus is reachable before the target investigation depth.",
                    "priority": "high",
                }
            )
        elif int(locus.get("route_count_capped") or 0) >= int(locus.get("route_count_cap") or route_cap):
            global_advice.append(
                {
                    "action": "narrow_overexposed_secret_locus",
                    "secret_id": locus["secret_id"],
                    "reason": "Route count hit the cap; add more discriminating clue/belief gates so the secret is not just a broad default basin.",
                    "priority": "medium",
                }
            )
    if unreachable:
        global_advice.append(
            {
                "action": "repair_unreachable_encounters",
                "reason": "Some encounters are outside the reachable DAG.",
                "count": len(unreachable),
                "examples": unreachable[:12],
                "priority": "medium",
            }
        )

    qv_ranked = quality_vector_report.get("ranked", []) if isinstance(quality_vector_report, dict) else []
    qv = qv_ranked[0].get("quality_vector", {}) if qv_ranked and isinstance(qv_ranked[0], dict) else {}
    pathing_lab = qv_ranked[0].get("pathing_lab", {}) if qv_ranked and isinstance(qv_ranked[0], dict) else {}
    return {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "storyworld": str(storyworld_path),
        "title": str(world.get("storyworld_title") or world.get("title") or storyworld_path.stem),
        "target_turns": {"min": target_min, "max": target_max},
        "start_id": start_id,
        "graph_summary": {
            "encounters": len(encounters),
            "edges": graph["edge_count"],
            "reachable_encounters": len(depths),
            "unreachable_encounters": len(unreachable),
            "max_reachable_depth": max_depth,
            "missing_target_edges": len(graph["missing_targets"]),
        },
        "quality_context": {
            "quality_failures": [str(item) for item in quality_report.get("failures", []) or []],
            "quality_vector": qv,
            "pathing_lab": pathing_lab,
        },
        "secret_loci": secret_loci,
        "global_advice": global_advice,
        "top_repair_rows": top_rows,
        "rows": rows,
    }


def metta_lines(packet: Dict[str, Any]) -> List[str]:
    lines = ["; Hilbert manifold pathing facts"]
    lines.append(f"(Storyworld {_safe_id(str(packet.get('title', 'storyworld')))})")
    lines.append(f"(StartEncounter {_safe_id(str(packet.get('start_id', 'unknown')))})")
    target = packet.get("target_turns", {})
    lines.append(f"(TargetTurns {int(target.get('min', 0))} {int(target.get('max', 0))})")
    for locus in packet.get("secret_loci", []):
        sid = _safe_id(str(locus.get("secret_id", "")))
        lines.append(f"(SecretLocus {sid})")
        lines.append(f"(SecretTurnDeficit {sid} {int(locus.get('turn_deficit', 0) or 0)})")
        lines.append(f"(SecretRouteCountCapped {sid} {int(locus.get('route_count_capped', 0) or 0)})")
    for row in packet.get("rows", []):
        eid = _safe_id(str(row.get("encounter_id", "")))
        lines.append(f"(Encounter {eid})")
        lines.append(f"(TurnDepth {eid} {row.get('turn_depth') if row.get('turn_depth') is not None else -1})")
        nearest = _safe_id(str(row.get("nearest_secret_locus", "none") or "none"))
        dist = row.get("directed_turns_to_secret")
        lines.append(f"(SecretDistance {eid} {nearest} {dist if dist is not None else -1})")
        vec = row.get("hilbert_vector", {})
        for key, value in vec.items():
            lines.append(f"(HilbertCoord {eid} {key} {float(value):.4f})")
        for advice in row.get("pathing_advice", []):
            lines.append(f"(PathingRepair {eid} {advice.get('action', 'unknown')} {advice.get('priority', 'low')})")
    return lines


def write_brief(path: Path, packet: Dict[str, Any]) -> None:
    summary = packet["graph_summary"]
    lines = [
        "# Hilbert Manifold Pathing Brief",
        "",
        f"Storyworld: `{packet['title']}`",
        f"Target turns: {packet['target_turns']['min']}-{packet['target_turns']['max']}",
        f"Graph: {summary['encounters']} encounters, {summary['edges']} edges, max reachable depth {summary['max_reachable_depth']}",
        "",
        "## Secret Loci",
        "",
    ]
    for locus in packet.get("secret_loci", []):
        lines.append(
            f"- `{locus['secret_id']}`: depth={locus.get('min_turn_depth')}, "
            f"turn_deficit={locus.get('turn_deficit')}, routes_capped={locus.get('route_count_capped')}"
        )
    lines.extend(["", "## Global Advice", ""])
    if packet.get("global_advice"):
        for advice in packet["global_advice"]:
            lines.append(f"- `{advice['action']}` ({advice.get('priority', 'low')}): {advice.get('reason', '')}")
    else:
        lines.append("- No high-level pathing repair required by this packet.")
    lines.extend(["", "## Top Encounter Repairs", ""])
    for row in packet.get("top_repair_rows", [])[:10]:
        actions = ", ".join(advice["action"] for advice in row.get("pathing_advice", [])[:3])
        lines.append(
            f"- `{row['encounter_id']}` depth={row.get('turn_depth')} "
            f"nearest_secret={row.get('nearest_secret_locus')} dist={row.get('directed_turns_to_secret')}: {actions}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Hilbert-manifold pathing packet for a storyworld JSON.")
    parser.add_argument("--world-json", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--quality-report", default="")
    parser.add_argument("--quality-vector-report", default="")
    parser.add_argument("--target-turns-min", type=int, default=24)
    parser.add_argument("--target-turns-max", type=int, default=40)
    parser.add_argument("--route-cap", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    world_path = Path(args.world_json).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    quality = read_json(Path(args.quality_report).expanduser().resolve()) if args.quality_report else {}
    quality_vector = read_json(Path(args.quality_vector_report).expanduser().resolve()) if args.quality_vector_report else {}
    packet = build_packet(
        read_json(world_path),
        world_path,
        quality,
        quality_vector,
        target_min=int(args.target_turns_min),
        target_max=int(args.target_turns_max),
        route_cap=int(args.route_cap),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_path = out_dir / "hilbert_pathing_packet.json"
    rows_path = out_dir / "hilbert_pathing_rows.jsonl"
    facts_path = out_dir / "hilbert_pathing_facts.metta"
    brief_path = out_dir / "hilbert_pathing_brief.md"
    manifest_path = out_dir / "manifest.json"
    dump_json(packet_path, {key: value for key, value in packet.items() if key != "rows"})
    row_count = dump_jsonl(rows_path, packet["rows"])
    facts_path.write_text("\n".join(metta_lines(packet)) + "\n", encoding="utf-8", newline="\n")
    write_brief(brief_path, packet)
    dump_json(
        manifest_path,
        {
            "storyworld": str(world_path),
            "quality_report": str(Path(args.quality_report).expanduser().resolve()) if args.quality_report else "",
            "quality_vector_report": str(Path(args.quality_vector_report).expanduser().resolve()) if args.quality_vector_report else "",
            "target_turns": packet["target_turns"],
            "rows": row_count,
            "outputs": {
                "packet": str(packet_path),
                "rows": str(rows_path),
                "facts": str(facts_path),
                "brief": str(brief_path),
            },
        },
    )
    print(str(packet_path))
    print(str(brief_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
