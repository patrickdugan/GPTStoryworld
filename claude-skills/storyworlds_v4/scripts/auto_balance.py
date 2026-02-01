"""
Automated iterative balancing for SweepWeave storyworlds.
Runs Monte Carlo, analyzes distribution, adjusts ending gates, repeats.

Usage:
    python auto_balance.py storyworld.json [--max-iters 10] [--runs 10000]

Targets:
    - Dead-end rate < 5%
    - No single ending > 30%
    - All endings reachable (> 0.5%)
    - Late-game blocking 10-30%

Strategy:
    - Dominant endings: raise gate thresholds by 20%
    - Unreachable endings: lower gate thresholds by 30%
    - High dead-end rate: widen fallback ending
    - CA saturation: cap CA effect magnitudes
"""
import json
import sys
import copy
from monte_carlo_rehearsal import run_monte_carlo, print_report


def analyze_distribution(result, num_runs):
    """Analyze Monte Carlo results and return tuning recommendations."""
    issues = []
    ending_counts = result["ending_counts"]
    dead_rate = result["dead_ends"] / num_runs

    if dead_rate > 0.05:
        issues.append(("HIGH_DEAD_END", dead_rate))

    for eid, count in ending_counts.items():
        if eid == "DEAD_END":
            continue
        pct = count / num_runs
        if pct > 0.30:
            issues.append(("DOMINANT", eid, pct))
        elif pct < 0.005 and pct > 0:
            issues.append(("RARE", eid, pct))

    for end in result["endings"]:
        if end["id"] not in ending_counts:
            issues.append(("UNREACHABLE", end["id"]))

    if result["late_total"] > 0:
        block_rate = result["late_blocks"] / result["late_total"]
        if block_rate > 0.30:
            issues.append(("HIGH_BLOCKING", block_rate))
        elif block_rate < 0.10:
            issues.append(("LOW_BLOCKING", block_rate))

    return issues


def adjust_gate_thresholds(data, eid, factor):
    """Multiply all numeric thresholds in an ending's acceptability_script by factor."""
    enc = None
    for e in data["encounters"]:
        if e["id"] == eid:
            enc = e
            break
    if enc is None:
        return

    def walk_and_adjust(node):
        if not isinstance(node, dict):
            return
        if (node.get("operator_type") == "Arithmetic Comparator" and
                len(node.get("operands", [])) == 2):
            threshold_op = node["operands"][1]
            if threshold_op.get("pointer_type") == "Bounded Number Constant":
                old = threshold_op["value"]
                threshold_op["value"] = round(old * factor, 6)
        for v in node.values():
            if isinstance(v, dict):
                walk_and_adjust(v)
            elif isinstance(v, list):
                for item in v:
                    walk_and_adjust(item)

    acc = enc.get("acceptability_script")
    if isinstance(acc, dict):
        walk_and_adjust(acc)


def ensure_fallback_ending(data):
    """Ensure at least one ending has acceptability_script = true."""
    for enc in data["encounters"]:
        if enc["id"].startswith("page_end_"):
            if enc.get("acceptability_script") is True:
                return  # Already have a fallback
    # Find the ending with lowest desirability or pick mosaic
    for enc in data["encounters"]:
        if enc["id"] == "page_end_mosaic":
            enc["acceptability_script"] = True
            enc["desirability_script"] = {
                "pointer_type": "Bounded Number Constant",
                "script_element_type": "Pointer",
                "value": 0.001,
            }
            return


def fix_character_ids(data):
    """Fix inconsistent character IDs (counter_archivist -> char_counter_archivist)."""
    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "character" and v == "counter_archivist":
                    obj[k] = "char_counter_archivist"
                else:
                    walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
    walk(data)


def auto_balance(path, max_iters=10, num_runs=10000):
    """Run iterative balancing loop."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Pre-flight fixes
    fix_character_ids(data)
    ensure_fallback_ending(data)

    # Ensure endgame/secrets spools are active
    for sp in data.get("spools", []):
        if sp["spool_name"] in ("Endgame", "Secrets"):
            sp["starts_active"] = True

    for iteration in range(1, max_iters + 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {iteration}")
        print(f"{'='*70}")

        result = run_monte_carlo(data, num_runs=num_runs, seed=42 + iteration)
        print_report(result)

        issues = analyze_distribution(result, num_runs)

        if not issues:
            print("\n*** BALANCED — all targets met ***")
            break

        print(f"\n--- Issues Found ({len(issues)}) ---")
        adjustments_made = False

        for issue in issues:
            if issue[0] == "HIGH_DEAD_END":
                print(f"  Dead-end rate {issue[1]:.1%} > 5% — ensuring fallback ending")
                ensure_fallback_ending(data)
                adjustments_made = True

            elif issue[0] == "DOMINANT":
                eid, pct = issue[1], issue[2]
                factor = 1.15  # Raise thresholds 15%
                print(f"  {eid} dominant at {pct:.1%} — tightening gates (×{factor})")
                adjust_gate_thresholds(data, eid, factor)
                adjustments_made = True

            elif issue[0] == "UNREACHABLE":
                eid = issue[1]
                factor = 0.70  # Lower thresholds 30%
                print(f"  {eid} unreachable — loosening gates (×{factor})")
                adjust_gate_thresholds(data, eid, factor)
                adjustments_made = True

            elif issue[0] == "RARE":
                eid, pct = issue[1], issue[2]
                factor = 0.85  # Lower thresholds 15%
                print(f"  {eid} rare at {pct:.1%} — loosening gates (×{factor})")
                adjust_gate_thresholds(data, eid, factor)
                adjustments_made = True

            elif issue[0] == "HIGH_BLOCKING":
                print(f"  Late-game blocking {issue[1]:.1%} > 30% — lowering thresholds")
                # Lower all late-game acceptability thresholds
                for enc in data["encounters"]:
                    acc = enc.get("acceptability_script")
                    if isinstance(acc, dict) and acc.get("operator_type") == "Or":
                        adjust_gate_thresholds(data, enc["id"], 0.8)
                adjustments_made = True

            else:
                print(f"  {issue}")

        if not adjustments_made:
            print("\n*** No adjustments possible — stopping ***")
            break

    # Save balanced storyworld
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved balanced storyworld to {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_balance.py storyworld.json [--max-iters N] [--runs N]")
        sys.exit(1)

    path = sys.argv[1]
    max_iters = 10
    runs = 10000
    for i, arg in enumerate(sys.argv):
        if arg == "--max-iters" and i + 1 < len(sys.argv):
            max_iters = int(sys.argv[i + 1])
        if arg == "--runs" and i + 1 < len(sys.argv):
            runs = int(sys.argv[i + 1])

    auto_balance(path, max_iters=max_iters, num_runs=runs)
