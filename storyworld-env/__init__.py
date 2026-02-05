#!/usr/bin/env python3
"""
Sweepweave Narrative Environment for PrimeIntellect Verifiers

Fine-tune models to generate valid Sweepweave storyworld JSON with:
- N encounters with branching options/reactions
- Character state management via bounded properties
- Spool-based narrative flow control
- Multiple endings and secret paths
- Thematic continuity and Dirac operator effects

  Quality criteria:
  1. Valid JSON loadable by Sweepweave Godot engine
  2. Structural completeness (characters, spools, encounters)
  3. Effect diversity (Dirac operators on character properties)
  4. Narrative coherence (thematic consistency)
  5. Explorable complexity (gated options, secret paths)
  6. Ending balance and reachability (avoid unreachable endings)
"""

import json
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple
from datasets import Dataset
import verifiers as vf


# ============================================================================
# THEME AND PROPERTY GENERATORS
# ============================================================================

PROPERTY_AXES = [
    ("Pragmatic", "Idealistic"),
    ("Stable", "Volatile"),
    ("Trust", "Betrayal"),
    ("Loyal", "Treacherous"),
    ("Calm", "Explosive"),
    ("Honest", "Tricky"),
    ("Cautious", "Reckless"),
    ("Compassionate", "Ruthless"),
    ("Humble", "Arrogant"),
    ("Cooperative", "Competitive"),
]

THEMES = [
    "deception vs mercy",
    "hierarchy vs equality", 
    "sacrifice vs consent",
    "bias in training data",
    "moral agency in war",
    "surveillance capitalism",
    "epistemic cleanliness",
    "consciousness and qualia",
    "6th generation warfare",
    "storyworld coherence",
]

NARRATIVE_SETTINGS = [
    "space station negotiation",
    "post-scarcity commune",
    "quantum computing research lab",
    "decentralized protocol governance",
    "AI alignment committee",
    "underground resistance cell",
    "corporate espionage scenario",
    "diplomatic summit",
    "archaeological expedition",
    "time-loop investigation",
]


def generate_property_set(num_properties: int = 3) -> List[Tuple[str, str]]:
    """Generate unique character property axes"""
    return random.sample(PROPERTY_AXES, min(num_properties, len(PROPERTY_AXES)))


def generate_theme_set(num_themes: int = 2) -> List[str]:
    """Generate thematic focus areas"""
    return random.sample(THEMES, min(num_themes, len(THEMES)))


# ============================================================================
# SWEEPWEAVE SCHEMA VALIDATION
# ============================================================================

REQUIRED_TOP_LEVEL = [
    "IFID", "about_text", "css_theme", "debug_mode", "display_mode",
    "creation_time", "modified_time", "characters", "authored_properties",
    "spools", "encounters"
]

REQUIRED_CHARACTER = ["id", "name", "bnumber_properties"]
REQUIRED_PROPERTY = ["id", "property_name", "property_type", "default_value"]
REQUIRED_ENCOUNTER = ["id", "title", "text_script", "options", "connected_spools"]
REQUIRED_OPTION = ["id", "text_script", "reactions"]
REQUIRED_REACTION = ["id", "text_script", "consequence_id", "after_effects"]
REQUIRED_SPOOL = ["id", "spool_type"]


class SweepweaveValidator:
    """Validate Sweepweave JSON structure and compute quality scores"""
    
    @staticmethod
    def validate_structure(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if JSON has required Sweepweave structure"""
        errors = []
        
        # Top-level fields
        for field in REQUIRED_TOP_LEVEL:
            if field not in data:
                errors.append(f"Missing top-level field: {field}")
        
        if errors:
            return False, errors
            
        # Characters
        for i, char in enumerate(data.get("characters", [])):
            for field in REQUIRED_CHARACTER:
                if field not in char:
                    errors.append(f"Character {i} missing: {field}")
        
        # Authored properties
        for i, prop in enumerate(data.get("authored_properties", [])):
            for field in REQUIRED_PROPERTY:
                if field not in prop:
                    errors.append(f"Property {i} missing: {field}")
        
        # Encounters
        encounter_ids = {enc.get("id") for enc in data.get("encounters", []) if enc.get("id")}
        for i, enc in enumerate(data.get("encounters", [])):
            for field in REQUIRED_ENCOUNTER:
                if field not in enc:
                    errors.append(f"Encounter {i} missing: {field}")
            
            # Options
            for j, opt in enumerate(enc.get("options", [])):
                for field in REQUIRED_OPTION:
                    if field not in opt:
                        errors.append(f"Encounter {i} option {j} missing: {field}")
                
                # Reactions
                for k, rxn in enumerate(opt.get("reactions", [])):
                    for field in REQUIRED_REACTION:
                        if field not in rxn:
                            errors.append(f"Encounter {i} option {j} reaction {k} missing: {field}")
                    cons_id = rxn.get("consequence_id", "")
                    if not isinstance(cons_id, str) or cons_id.strip() == "":
                        errors.append(
                            f"Reaction missing consequence_id: encounter={enc.get('id','?')} option={opt.get('id','?')} reaction={rxn.get('id','?')}"
                        )
                    elif cons_id not in encounter_ids:
                        errors.append(
                            f"Reaction consequence_id not found: encounter={enc.get('id','?')} option={opt.get('id','?')} reaction={rxn.get('id','?')} -> {cons_id}"
                        )

        # Spools
        spools = data.get("spools", [])
        if not spools:
            errors.append("spools: empty")
        start_spools = [s for s in spools if s.get("starts_active")]
        if not start_spools:
            errors.append("spools: no starts_active spool")
        for sp in spools:
            encs = sp.get("encounters", None)
            if not isinstance(encs, list) or len(encs) == 0:
                errors.append(f"spools[{sp.get('id','?')}]: encounters empty")
                continue
            for eid in encs:
                if eid not in encounter_ids:
                    errors.append(f"spools[{sp.get('id','?')}]: unknown encounter id {eid}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def compute_structural_score(data: Dict[str, Any], requirements: Dict[str, int]) -> float:
        """Score based on structural requirements"""
        score = 0.0
        max_score = 0.0
        
        # Character count
        if "min_characters" in requirements:
            max_score += 1.0
            num_chars = len(data.get("characters", []))
            if num_chars >= requirements["min_characters"]:
                score += 1.0
            else:
                score += num_chars / requirements["min_characters"]
        
        # Encounter count
        if "min_encounters" in requirements:
            max_score += 1.0
            num_encs = len(data.get("encounters", []))
            if num_encs >= requirements["min_encounters"]:
                score += 1.0
            else:
                score += num_encs / requirements["min_encounters"]
        
        # Spool count
        if "min_spools" in requirements:
            max_score += 1.0
            num_spools = len(data.get("spools", []))
            if num_spools >= requirements["min_spools"]:
                score += 1.0
            else:
                score += num_spools / requirements["min_spools"]
        
        # Options per encounter
        if "min_options_per_encounter" in requirements:
            max_score += 1.0
            encs = data.get("encounters", [])
            if encs:
                avg_opts = sum(len(e.get("options", [])) for e in encs) / len(encs)
                if avg_opts >= requirements["min_options_per_encounter"]:
                    score += 1.0
                else:
                    score += avg_opts / requirements["min_options_per_encounter"]

        # Reactions per option
        if "min_reactions_per_option" in requirements:
            max_score += 1.0
            options = [o for e in data.get("encounters", []) for o in e.get("options", [])]
            if options:
                avg_rxn = sum(len(o.get("reactions", [])) for o in options) / len(options)
                if avg_rxn >= requirements["min_reactions_per_option"]:
                    score += 1.0
                else:
                    score += avg_rxn / requirements["min_reactions_per_option"]

        # Effects per reaction
        if "min_effects_per_reaction" in requirements:
            max_score += 1.0
            reactions = [r for e in data.get("encounters", []) for o in e.get("options", []) for r in o.get("reactions", [])]
            if reactions:
                avg_eff = sum(len(r.get("after_effects", []) or []) for r in reactions) / len(reactions)
                if avg_eff >= requirements["min_effects_per_reaction"]:
                    score += 1.0
                else:
                    score += avg_eff / requirements["min_effects_per_reaction"]
        
        return score / max_score if max_score > 0 else 0.0
    
    @staticmethod
    def compute_effect_diversity(data: Dict[str, Any]) -> float:
        """Score based on variety of after_effects (Dirac operators)"""
        effect_types = set()
        total_effects = 0
        
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    for eff in rxn.get("after_effects", []):
                        effect_types.add(eff.get("effect_type", "unknown"))
                        total_effects += 1
        
        if total_effects == 0:
            return 0.0
        
        # Score: (unique effect types / total effects) weighted by total count
        diversity = len(effect_types) / max(total_effects, 1)
        density = min(total_effects / 10.0, 1.0)  # Reward having effects
        
        return (diversity + density) / 2.0

    @staticmethod
    def _script_is_constant(script: Any) -> bool:
        if not isinstance(script, dict):
            return True
        if script.get("script_element_type") == "Pointer":
            return script.get("pointer_type") in (
                "Bounded Number Constant",
                "Boolean Constant",
                "String Constant",
            )
        if script.get("script_element_type") == "Operator":
            ops = script.get("operands", [])
            if not ops:
                return True
            return all(SweepweaveValidator._script_is_constant(op) for op in ops)
        return False

    @staticmethod
    def _script_has_variable_pointer(script: Any) -> bool:
        if not isinstance(script, dict):
            return False
        if script.get("pointer_type") == "Bounded Number Pointer":
            return True
        if script.get("script_element_type") == "Operator":
            return any(SweepweaveValidator._script_has_variable_pointer(op) for op in script.get("operands", []))
        return False

    @staticmethod
    def _extract_thresholds(script: Any) -> List[float]:
        found: List[float] = []
        if not isinstance(script, dict):
            return found
        if script.get("operator_type") == "Arithmetic Comparator":
            for op in script.get("operands", []):
                if isinstance(op, dict) and op.get("pointer_type") == "Bounded Number Constant":
                    try:
                        found.append(float(op.get("value", 0.0)))
                    except (TypeError, ValueError):
                        continue
        for op in script.get("operands", []):
            found.extend(SweepweaveValidator._extract_thresholds(op))
        return found

    @staticmethod
    def _collect_vars(script: Any, out: set) -> None:
        if script is None:
            return
        if isinstance(script, dict):
            if script.get("pointer_type") == "Bounded Number Pointer":
                char = script.get("character")
                keyring = script.get("keyring") or []
                if char and keyring:
                    out.add((char, keyring[0]))
            for v in script.values():
                SweepweaveValidator._collect_vars(v, out)
        elif isinstance(script, list):
            for v in script:
                SweepweaveValidator._collect_vars(v, out)

    @staticmethod
    def _count_vars(script: Any) -> int:
        out: set = set()
        SweepweaveValidator._collect_vars(script, out)
        return len(out)

    @staticmethod
    def _script_has_operator(script: Any, operator_type: str) -> bool:
        if isinstance(script, dict):
            if script.get("operator_type") == operator_type:
                return True
            for v in script.values():
                if SweepweaveValidator._script_has_operator(v, operator_type):
                    return True
        elif isinstance(script, list):
            for v in script:
                if SweepweaveValidator._script_has_operator(v, operator_type):
                    return True
        return False

    @staticmethod
    def _script_has_nonzero_constant(script: Any) -> bool:
        if isinstance(script, dict):
            if script.get("pointer_type") == "Bounded Number Constant":
                try:
                    return abs(float(script.get("value", 0.0))) > 1e-6
                except (TypeError, ValueError):
                    return False
            for v in script.values():
                if SweepweaveValidator._script_has_nonzero_constant(v):
                    return True
        elif isinstance(script, list):
            for v in script:
                if SweepweaveValidator._script_has_nonzero_constant(v):
                    return True
        return False

    @staticmethod
    def _is_visibility_gated(script: Any) -> bool:
        if script is True:
            return False
        if isinstance(script, dict) and script.get("pointer_type") == "Boolean Constant":
            return not bool(script.get("value", False)) if script.get("value") is not None else True
        return True

    @staticmethod
    def compute_secret_gate_quality(data: Dict[str, Any], min_effects: int = 3, min_threshold: float = 0.02) -> float:
        """Score secret gates that require accumulated variable thresholds."""
        gated_options = 0
        gated_ok = 0
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                vis = opt.get("visibility_script")
                if vis and isinstance(vis, dict) and vis.get("pointer_type") != "Boolean Constant":
                    gated_options += 1
                    thresholds = SweepweaveValidator._extract_thresholds(vis)
                    threshold_ok = any(t >= min_threshold for t in thresholds) if thresholds else False
                    reactions = opt.get("reactions", [])
                    all_ok = True
                    for rxn in reactions:
                        ds = rxn.get("desirability_script")
                        if not ds or SweepweaveValidator._script_is_constant(ds) or not SweepweaveValidator._script_has_variable_pointer(ds):
                            all_ok = False
                            break
                        effects = rxn.get("after_effects", [])
                        if not isinstance(effects, list) or len(effects) < min_effects:
                            all_ok = False
                            break
                    if all_ok and threshold_ok:
                        gated_ok += 1
        if gated_options == 0:
            return 0.0
        return gated_ok / gated_options

    @staticmethod
    def _reaction_has_flip_or_blend(rxn: Dict[str, Any]) -> bool:
        desirability = rxn.get("desirability_script")
        blend = False
        if isinstance(desirability, dict) and desirability.get("script_element_type") == "Operator":
            op_type = desirability.get("operator_type")
            operands = desirability.get("operands", [])
            if op_type in ("Addition", "Multiplication") and len(operands) >= 2:
                if any(SweepweaveValidator._script_has_variable_pointer(op) for op in operands):
                    blend = True

        effects = rxn.get("after_effects", [])
        deltas = []
        for eff in effects:
            to = eff.get("to", {})
            if isinstance(to, dict) and to.get("operator_type") == "Nudge":
                ops = to.get("operands", [])
                for op in ops:
                    if isinstance(op, dict) and op.get("pointer_type") == "Bounded Number Constant":
                        try:
                            deltas.append(float(op.get("value", 0.0)))
                        except (TypeError, ValueError):
                            pass
        flip = any(d >= 0.03 for d in deltas) and any(d <= -0.02 for d in deltas)
        return blend or flip

    @staticmethod
    def compute_major_turn_quality(data: Dict[str, Any]) -> float:
        """Score presence of Act II/III gated options with flip/blend reactions."""
        act2_ok = False
        act3_ok = False
        for enc in data.get("encounters", []):
            spools = enc.get("connected_spools", [])
            in_act2 = any("act2" in s for s in spools)
            in_act3 = any("act3" in s for s in spools)
            if not (in_act2 or in_act3):
                continue
            for opt in enc.get("options", []):
                vis = opt.get("visibility_script")
                if not (vis and isinstance(vis, dict) and vis.get("pointer_type") != "Boolean Constant"):
                    continue
                for rxn in opt.get("reactions", []):
                    if SweepweaveValidator._reaction_has_flip_or_blend(rxn):
                        if in_act2:
                            act2_ok = True
                        if in_act3:
                            act3_ok = True
                if act2_ok and act3_ok:
                    break
        return 1.0 if (act2_ok and act3_ok) else 0.5 if (act2_ok or act3_ok) else 0.0

    @staticmethod
    def compute_effects_per_reaction(data: Dict[str, Any]) -> float:
        total_effects = 0
        total_reactions = 0
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    total_reactions += 1
                    total_effects += len(rxn.get("after_effects", []) or [])
        return (total_effects / total_reactions) if total_reactions else 0.0

    @staticmethod
    def compute_reactions_per_option(data: Dict[str, Any]) -> float:
        total_reactions = 0
        total_options = 0
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                total_options += 1
                total_reactions += len(opt.get("reactions", []) or [])
        return (total_reactions / total_options) if total_options else 0.0

    @staticmethod
    def compute_options_per_encounter(data: Dict[str, Any]) -> float:
        encs = [e for e in data.get("encounters", []) if e.get("options")]
        if not encs:
            return 0.0
        return sum(len(e.get("options", []) or []) for e in encs) / len(encs)

    @staticmethod
    def compute_desirability_vars_per_reaction(data: Dict[str, Any]) -> float:
        counts: List[int] = []
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    counts.append(SweepweaveValidator._count_vars(rxn.get("desirability_script")))
        return (sum(counts) / len(counts)) if counts else 0.0

    @staticmethod
    def compute_pvalue_desirability_alignment(data: Dict[str, Any]) -> float:
        """Fraction of reactions with property effects whose desirability uses pValues for actors and witnesses."""
        total = 0
        ok = 0
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    effects = rxn.get("after_effects", []) or []
                    affected: List[Tuple[str, str]] = []
                    for eff in effects:
                        if eff.get("effect_type") != "Bounded Number Effect":
                            continue
                        ptr = eff.get("Set", {})
                        char = ptr.get("character")
                        keyring = ptr.get("keyring") or []
                        if not char or not keyring:
                            continue
                        prop = keyring[0]
                        if isinstance(prop, str) and not prop.startswith("p"):
                            affected.append((char, prop))
                    if not affected:
                        continue
                    total += 1
                    desirability = rxn.get("desirability_script")
                    vars_in_script: set = set()
                    SweepweaveValidator._collect_vars(desirability, vars_in_script)
                    pvalue_by_prop: Dict[str, Dict[str, set]] = {}
                    for ch, key in vars_in_script:
                        if not isinstance(key, str):
                            continue
                        pvalue_by_prop.setdefault(key, {}).setdefault(ch, set())
                    # Capture keyring chains that include perceived character ids
                    def collect_pvalue_targets(script: Any) -> None:
                        if isinstance(script, dict):
                            if script.get("pointer_type") == "Bounded Number Pointer":
                                keyring = script.get("keyring") or []
                                char = script.get("character")
                                if char and isinstance(keyring, list) and len(keyring) > 1:
                                    prop = keyring[0]
                                    target = keyring[1]
                                    if isinstance(prop, str) and isinstance(target, str):
                                        pvalue_by_prop.setdefault(prop, {}).setdefault(char, set()).add(target)
                            for v in script.values():
                                collect_pvalue_targets(v)
                        elif isinstance(script, list):
                            for v in script:
                                collect_pvalue_targets(v)
                    collect_pvalue_targets(desirability)
                    hit = False
                    for ch, prop in affected:
                        witnesses = pvalue_by_prop.get(prop) or {}
                        if not witnesses:
                            continue
                        if any(ch in targets for targets in witnesses.values()):
                            if len(witnesses.keys()) >= 2:
                                hit = True
                                break
                    if hit:
                        ok += 1
        return (ok / total) if total else 0.0

    @staticmethod
    def compute_effect_script_quality(data: Dict[str, Any]) -> float:
        """Fraction of after_effects with an operator and non-zero constant in the script."""
        total = 0
        ok = 0
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    for eff in rxn.get("after_effects", []) or []:
                        if eff.get("effect_type") != "Bounded Number Effect":
                            continue
                        total += 1
                        to = eff.get("to")
                        has_op = SweepweaveValidator._script_has_operator(to, "Nudge") or \
                            SweepweaveValidator._script_has_operator(to, "Blend") or \
                            SweepweaveValidator._script_has_operator(to, "Addition") or \
                            SweepweaveValidator._script_has_operator(to, "Multiplication") or \
                            SweepweaveValidator._script_has_operator(to, "Absolute Value") or \
                            SweepweaveValidator._script_has_operator(to, "Maximum") or \
                            SweepweaveValidator._script_has_operator(to, "Minimum")
                        has_nonzero = SweepweaveValidator._script_has_nonzero_constant(to)
                        if has_op and has_nonzero:
                            ok += 1
        return (ok / total) if total else 0.0

    @staticmethod
    def compute_act_gating_stats(data: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
        encounters = data.get("encounters", [])
        enc_by_id = {e.get("id"): e for e in encounters if e.get("id")}
        spools = data.get("spools", [])
        act2_ids = set()
        act3_ids = set()
        for sp in spools:
            name = (sp.get("spool_name") or "").lower()
            sid = (sp.get("id") or "").lower()
            ids = sp.get("encounters", []) or []
            if "act ii" in name or "act2" in sid or "act_2" in sid:
                act2_ids.update(ids)
            if "act iii" in name or "act3" in sid or "act_3" in sid:
                act3_ids.update(ids)

        def gate_stats(enc_ids):
            opts = 0
            gated = 0
            gated_vars: List[int] = []
            for eid in enc_ids:
                enc = enc_by_id.get(eid)
                if not enc:
                    continue
                for opt in enc.get("options", []) or []:
                    opts += 1
                    vis = opt.get("visibility_script", True)
                    if SweepweaveValidator._is_visibility_gated(vis):
                        gated += 1
                        gated_vars.append(SweepweaveValidator._count_vars(vis))
            pct = (gated / opts * 100.0) if opts else 0.0
            avg_vars = (sum(gated_vars) / len(gated_vars)) if gated_vars else 0.0
            return pct, avg_vars

        return {
            "act2": gate_stats(act2_ids),
            "act3": gate_stats(act3_ids),
        }

    @staticmethod
    def compute_secret_metric_distance_quality(data: Dict[str, Any]) -> float:
        secrets = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_secret_")]
        if not secrets:
            return 0.0
        ok = 0
        for enc in secrets:
            acc = enc.get("acceptability_script")
            vars_count = SweepweaveValidator._count_vars(acc)
            has_distance = SweepweaveValidator._script_has_operator(acc, "Absolute Value")
            if has_distance and vars_count >= 2:
                ok += 1
        return ok / len(secrets)

    @staticmethod
    def _is_transition_encounter(enc: Dict[str, Any]) -> bool:
        eid = (enc.get("id") or "").lower()
        title = (enc.get("title") or "").lower()
        return eid.startswith("page_transition_") or "transition" in title

    @staticmethod
    def compute_min_spec_compliance(
        data: Dict[str, Any],
        min_options: int = 3,
        min_reactions: int = 2,
        min_effects: int = 4,
    ) -> float:
        """Fraction of non-ending, non-transition encounters meeting min spec."""
        encounters = data.get("encounters", [])
        eligible = 0
        ok = 0
        for enc in encounters:
            eid = enc.get("id", "")
            if eid.startswith("page_end_") or eid.startswith("page_secret_"):
                continue
            if SweepweaveValidator._is_transition_encounter(enc):
                continue
            eligible += 1
            options = enc.get("options", []) or []
            if len(options) < min_options:
                continue
            reactions_ok = True
            effects_ok = True
            for opt in options:
                reactions = opt.get("reactions", []) or []
                if len(reactions) < min_reactions:
                    reactions_ok = False
                    break
                for rxn in reactions:
                    if len(rxn.get("after_effects", []) or []) < min_effects:
                        effects_ok = False
                        break
                if not reactions_ok or not effects_ok:
                    break
            if reactions_ok and effects_ok:
                ok += 1
        if eligible == 0:
            return 0.0
        return ok / eligible

    @staticmethod
    def compute_text_length_compliance(
        data: Dict[str, Any],
        encounter_min: int = 50,
        encounter_max: int = 300,
        reaction_min: int = 20,
        reaction_max: int = 150,
    ) -> float:
        """Fraction of encounter/reaction texts within word-count ranges."""
        def count_words(text: str) -> int:
            return len([w for w in text.split() if w.strip()])

        encounters = data.get("encounters", [])
        total = 0
        ok = 0
        for enc in encounters:
            text = enc.get("text_script", {}).get("value", "") if isinstance(enc.get("text_script"), dict) else ""
            wc = count_words(text)
            total += 1
            if encounter_min <= wc <= encounter_max:
                ok += 1
            for opt in enc.get("options", []) or []:
                for rxn in opt.get("reactions", []) or []:
                    rtext = rxn.get("text_script", {}).get("value", "") if isinstance(rxn.get("text_script"), dict) else ""
                    rwc = count_words(rtext)
                    total += 1
                    if reaction_min <= rwc <= reaction_max:
                        ok += 1
        if total == 0:
            return 0.0
        return ok / total
    
    @staticmethod
    def compute_gating_score(data: Dict[str, Any]) -> float:
        """Score based on conditional option visibility (secret paths)"""
        gated_options = 0
        total_options = 0
        
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                total_options += 1
                # Check if visibility_script is non-trivial
                vis = opt.get("visibility_script")
                if vis and isinstance(vis, dict):
                    # Non-boolean constant = conditional gating
                    if vis.get("pointer_type") != "Boolean Constant":
                        gated_options += 1
        
        if total_options == 0:
            return 0.0
        
        # Reward narrow gating ratio (3-5%)
        ratio = gated_options / total_options
        if ratio <= 0.0:
            return 0.0
        if ratio < 0.03:
            return max(0.0, ratio / 0.03)
        if ratio <= 0.05:
            return 1.0
        if ratio >= 0.12:
            return 0.0
        # Linear falloff between 5% and 12%
        return max(0.0, 1.0 - ((ratio - 0.05) / 0.07))
    
    @staticmethod
    def compute_ending_diversity(data: Dict[str, Any]) -> float:
        """Score based on multiple distinct endings"""
        endings = detect_endings(data)
        num_endings = len(endings)
        
        # Reward 2-5 endings
        if num_endings < 2:
            return num_endings / 2.0
        elif num_endings <= 5:
            return 1.0
        else:
            return max(0.5, 1.0 - (num_endings - 5) * 0.1)

    @staticmethod
    def compute_dead_end_rate(data: Dict[str, Any], runs: int = 200, seed: int = 42) -> float:
        report = run_monte_carlo(data, num_runs=runs, seed=seed)
        if report["num_runs"] == 0:
            return 1.0
        return report["dead_ends"] / report["num_runs"]

    @staticmethod
    def compute_ending_balance(data: Dict[str, Any], runs: int = 200, seed: int = 42) -> Tuple[float, float]:
        report = run_monte_carlo(data, num_runs=runs, seed=seed)
        total = report["num_runs"]
        if total == 0 or not report["ending_counts"]:
            return 1.0, 0.0
        counts = report["ending_counts"]
        max_share = max(counts.values()) / total
        min_share = min(counts.values()) / total
        return max_share, min_share

    @staticmethod
    def compute_late_block_rate(data: Dict[str, Any], runs: int = 200, seed: int = 42) -> float:
        report = run_monte_carlo(data, num_runs=runs, seed=seed)
        if report["late_total"] == 0:
            return 0.0
        return report["late_blocks"] / report["late_total"]

    @staticmethod
    def compute_secret_reachability(data: Dict[str, Any], runs: int = 200, seed: int = 42) -> float:
        report = run_monte_carlo(data, num_runs=runs, seed=seed)
        total = report["num_runs"]
        if total == 0:
            return 0.0
        return report.get("secret_any", 0) / total

    @staticmethod
    def compute_unreachable_endings_score(data: Dict[str, Any], runs: int = 200, seed: int = 42) -> float:
        """Score 1.0 if all endings are reachable, otherwise proportional to reachability."""
        report = run_monte_carlo(data, num_runs=runs, seed=seed)
        endings = [e["id"] for e in report.get("endings", [])]
        if not endings:
            return 0.0
        reachable = sum(1 for eid in endings if report.get("ending_counts", {}).get(eid, 0) > 0)
        return reachable / len(endings)


# ============================================================================
# MONTE CARLO REHEARSAL (LIGHTWEIGHT)
# ============================================================================

def eval_script(script, state):
    """Recursively evaluate a SweepWeave script expression."""
    if script is True:
        return True
    if script is False:
        return False
    if isinstance(script, (int, float)):
        return script
    if not isinstance(script, dict):
        return script

    pt = script.get("pointer_type")
    ot = script.get("operator_type")

    if pt == "Bounded Number Constant":
        return script["value"]
    if pt == "Bounded Number Pointer":
        char = script["character"]
        prop = script["keyring"][0]
        coeff = script.get("coefficient", 1.0)
        return state.get((char, prop), 0.0) * coeff
    if pt == "String Constant":
        return script.get("value", "")

    if ot == "Arithmetic Comparator":
        sub = script["operator_subtype"]
        left = eval_script(script["operands"][0], state)
        right = eval_script(script["operands"][1], state)
        ops = {
            "Greater Than or Equal To": lambda a, b: a >= b,
            "GTE": lambda a, b: a >= b,
            "Less Than or Equal To": lambda a, b: a <= b,
            "LTE": lambda a, b: a <= b,
            "Greater Than": lambda a, b: a > b,
            "GT": lambda a, b: a > b,
            "Less Than": lambda a, b: a < b,
            "LT": lambda a, b: a < b,
            "Equal To": lambda a, b: a == b,
            "EQ": lambda a, b: a == b,
            "Not Equal To": lambda a, b: a != b,
            "NEQ": lambda a, b: a != b,
        }
        return ops.get(sub, lambda a, b: False)(left, right)

    if ot == "And":
        return all(eval_script(op, state) for op in script["operands"])
    if ot == "Or":
        return any(eval_script(op, state) for op in script["operands"])
    if ot == "Addition":
        return sum(eval_script(op, state) for op in script["operands"])
    if ot == "Multiplication":
        r = 1.0
        for op in script["operands"]:
            r *= eval_script(op, state)
        return r
    if ot == "Absolute Value":
        return abs(eval_script(script["operands"][0], state))
    if ot == "Nudge":
        cur = eval_script(script["operands"][0], state)
        delta = eval_script(script["operands"][1], state)
        return max(-1.0, min(1.0, cur + delta))

    return script.get("value", 0.0)


def apply_effects(reaction, state):
    for ae in reaction.get("after_effects", []):
        if ae.get("effect_type") == "Bounded Number Effect":
            char = ae["Set"]["character"]
            prop = ae["Set"]["keyring"][0]
            new_val = eval_script(ae["to"], state)
            state[(char, prop)] = max(-1.0, min(1.0, new_val))


def select_reaction(option, state):
    best, best_d = None, -999
    for rxn in option.get("reactions", []):
        d = eval_script(rxn.get("desirability_script", 0), state)
        if d is None:
            d = 0
        if isinstance(d, bool):
            d = 1.0 if d else 0.0
        if d > best_d:
            best_d, best = d, rxn
    return best


def build_chain(data):
    """Build linear consequence chain from page_0000 onward."""
    enc_by_id = {e["id"]: e for e in data.get("encounters", [])}
    chain, visited = [], set()
    current_id = "page_0000"
    while current_id and current_id != "wild" and current_id not in visited:
        if current_id not in enc_by_id:
            break
        visited.add(current_id)
        enc = enc_by_id[current_id]
        chain.append(enc)
        next_id = None
        for opt in enc.get("options", []):
            for rxn in opt.get("reactions", []):
                cid = rxn.get("consequence_id", "")
                if cid:
                    next_id = cid
                    break
            if next_id:
                break
        current_id = next_id
    return chain


def detect_endings(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    endings = []
    encounter_ids = set()
    all_consequence_ids = set()
    for enc in data.get("encounters", []):
        eid = enc.get("id")
        if eid:
            encounter_ids.add(eid)
        if enc.get("is_ending") is True or enc.get("ending_id"):
            endings.append(enc)
    for enc in data.get("encounters", []):
        for opt in enc.get("options", []):
            for rxn in opt.get("reactions", []):
                cons_id = rxn.get("consequence_id")
                if cons_id:
                    all_consequence_ids.add(cons_id)
    terminal = encounter_ids - all_consequence_ids
    for enc in data.get("encounters", []):
        if enc.get("id") in terminal:
            endings.append(enc)
    if not endings:
        endings = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_end_")]
    # de-dup by id
    seen = set()
    uniq = []
    for enc in endings:
        eid = enc.get("id")
        if not eid or eid in seen:
            continue
        seen.add(eid)
        uniq.append(enc)
    return uniq


def detect_secrets(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    secrets = []
    for enc in data.get("encounters", []):
        if enc.get("id", "").startswith("page_secret_"):
            secrets.append(enc)
            continue
        for opt in enc.get("options", []):
            if opt.get("secret") is True:
                secrets.append(enc)
                break
            vis = opt.get("visibility_script")
            if isinstance(vis, dict) and vis.get("pointer_type") != "Boolean Constant":
                secrets.append(enc)
                break
    # de-dup by id
    seen = set()
    uniq = []
    for enc in secrets:
        eid = enc.get("id")
        if not eid or eid in seen:
            continue
        seen.add(eid)
        uniq.append(enc)
    return uniq


def run_monte_carlo(data, num_runs=200, seed=42):
    random.seed(seed)
    chain = build_chain(data)
    spool_sequence = []
    if len(chain) == 0:
        enc_by_id = {e["id"]: e for e in data.get("encounters", [])}
        spools = sorted(
            data.get("spools", []),
            key=lambda s: s.get("creation_index", 0)
        )
        for sp in spools:
            if sp.get("id") == "spool_endings" or sp.get("spool_name") == "Endings":
                continue
            ids = sp.get("encounters", [])
            spool_encs = [enc_by_id[eid] for eid in ids if eid in enc_by_id]
            if spool_encs:
                spool_sequence.append(spool_encs)
    endings = detect_endings(data)
    secrets = detect_secrets(data)

    spool_map = {}
    for sp in data.get("spools", []):
        for eid in sp.get("encounters", []):
            spool_map[eid] = sp.get("spool_name", "")

    ending_counts = Counter()
    dead_ends = 0
    prop_sums = defaultdict(float)
    prop_sq = defaultdict(float)
    late_blocks, late_total = 0, 0
    secret_hits = Counter()
    secret_any = 0

    for _ in range(num_runs):
        state = {}
        if chain:
            for enc in chain:
                eid = enc["id"]
                spool = spool_map.get(eid, "")
                if spool.startswith("Age "):
                    age_part = spool.split(" ")[1]
                    if age_part.isdigit():
                        age = int(age_part)
                        if age >= 14:
                            if not bool(eval_script(enc.get("acceptability_script", True), state)):
                                late_blocks += 1
                            late_total += 1

                visible = [(i, o) for i, o in enumerate(enc.get("options", []))
                           if eval_script(o.get("visibility_script", True), state)]
                if not visible:
                    continue
                _, chosen = random.choice(visible)
                rxn = select_reaction(chosen, state)
                if rxn:
                    apply_effects(rxn, state)
        else:
            for spool_encs in spool_sequence:
                k = min(3, len(spool_encs))
                for enc in random.sample(spool_encs, k):
                    if not bool(eval_script(enc.get("acceptability_script", True), state)):
                        continue
                    visible = [(i, o) for i, o in enumerate(enc.get("options", []))
                               if eval_script(o.get("visibility_script", True), state)]
                    if not visible:
                        continue
                    _, chosen = random.choice(visible)
                    rxn = select_reaction(chosen, state)
                    if rxn:
                        apply_effects(rxn, state)

        hit_any = False
        for sec in secrets:
            if eval_script(sec.get("acceptability_script", True), state):
                secret_hits[sec["id"]] += 1
                hit_any = True
        if hit_any:
            secret_any += 1

        best_end, best_d = None, -999
        for end in endings:
            if eval_script(end.get("acceptability_script", True), state):
                d = eval_script(end.get("desirability_script", 0), state)
                if isinstance(d, bool):
                    d = 1.0 if d else 0.0
                if d > best_d:
                    best_d, best_end = d, end

        if best_end:
            ending_counts[best_end["id"]] += 1
        else:
            dead_ends += 1
            ending_counts["DEAD_END"] += 1

        for (char, prop), val in state.items():
            key = f"{char}.{prop}"
            prop_sums[key] += val
            prop_sq[key] += val * val

    return {
        "chain_length": len(chain),
        "num_endings": len(endings),
        "num_secrets": len(secrets),
        "num_runs": num_runs,
        "ending_counts": ending_counts,
        "dead_ends": dead_ends,
        "late_blocks": late_blocks,
        "late_total": late_total,
        "secret_hits": secret_hits,
        "secret_any": secret_any,
        "prop_sums": prop_sums,
        "prop_sq": prop_sq,
    }


# ============================================================================
# DATASET GENERATION
# ============================================================================

def generate_storyworld_prompt(
    num_characters: int = 3,
    num_properties: int = 3,
    num_encounters: int = 10,
    num_spools: int = 3,
    themes: Optional[List[str]] = None,
    setting: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Generate a prompt for creating a Sweepweave storyworld"""
    
    properties = generate_property_set(num_properties)
    themes = themes or generate_theme_set(2)
    setting = setting or random.choice(NARRATIVE_SETTINGS)
    
    property_list = [f"{p[0]}_{p[1]}" for p in properties]
    
    prompt = f"""Generate a complete Sweepweave storyworld in JSON format.

SETTING: {setting}

THEMES: {', '.join(themes)}

REQUIREMENTS:
- {num_characters} characters with distinct personalities
- {num_properties} character property axes: {', '.join(property_list)}
- Infer encounter count from the setting and spools (do not state a fixed number); ensure it meets the minimum required for structural completeness
- {num_spools} narrative spools controlling encounter availability
- Each non-ending, non-transition encounter has at least 3 options
- Each option has at least 2 reactions with different consequences
- Each reaction has at least 4 after_effects modifying character properties
- Encounter descriptions are 50-300 words; reaction texts are 20-150 words
- When reactions modify character properties, desirability formulas should reference pValues using keyrings
  (property id + perceived character id) for the affected character and at least one witness character
- Every after_effect script must include at least one operator and at least one non-zero constant input
- Multiple endings (2-5 distinct terminal states)
- Some options should be gated by character property conditions

STRUCTURE TEMPLATE:
{{
  "IFID": "SW-GEN-[unique-id]",
  "storyworld_title": "[title]",
  "storyworld_author": "Generated",
  "sweepweave_version": "0.1.9",
  "creation_time": 1700000000.0,
  "modified_time": 1700000000.0,
  "debug_mode": false,
  "display_mode": 1,
  "css_theme": "lilac",
  "font_size": "16",
  "language": "en",
  "rating": "general",
  "about_text": {{
    "pointer_type": "String Constant",
    "script_element_type": "Pointer",
    "value": "[description]"
  }},
  "characters": [
    {{
      "id": "char_[name]",
      "name": "[Name]",
      "pronoun": "she/he/they",
      "bnumber_properties": {{
        "{property_list[0]}": 0,
        "p{property_list[0]}": {{}},
        ...
      }}
    }}
  ],
  "authored_properties": [
    {{
      "id": "{property_list[0]}",
      "property_name": "{property_list[0]}",
      "property_type": "bounded number",
      "default_value": 0,
      "depth": 0,
      "attribution_target": "all cast members",
      "affected_characters": [],
      "creation_index": 0,
      "creation_time": 1700000000.0,
      "modified_time": 1700000000.0
    }}
  ],
  "spools": [
    {{
      "id": "spool_[name]",
      "spool_type": "General",
      "creation_index": 0,
      "creation_time": 1700000000.0,
      "modified_time": 1700000000.0
    }}
  ],
  "encounters": [
    {{
      "id": "page_[id]",
      "title": "[Title]",
      "connected_spools": ["spool_early"],
      "earliest_turn": 0,
      "latest_turn": 999,
      "text_script": {{
        "pointer_type": "String Constant",
        "script_element_type": "Pointer",
        "value": "[narrative text]"
      }},
      "options": [
        {{
          "id": "page_[id]_option1",
          "text_script": {{
            "pointer_type": "String Constant",
            "script_element_type": "Pointer",
            "value": "[choice text]"
          }},
          "reactions": [
            {{
              "id": "page_[id]_option1_reaction1",
              "text_script": {{
                "pointer_type": "String Constant",
                "script_element_type": "Pointer",
                "value": "[consequence text]"
              }},
              "consequence_id": "page_[next_id]",
              "after_effects": [
                {{
                  "effect_type": "Set",
                  "Set": {{
                    "character": "char_[name]",
                    "keyring": ["{property_list[0]}"],
                    "coefficient": 1,
                    "pointer_type": "Bounded Number Constant",
                    "script_element_type": "Pointer"
                  }},
                  "to": {{
                    "script_element_type": "Bounded Number Operator",
                    "operator_type": "Addition",
                    "operands": [
                      {{
                        "character": "char_[name]",
                        "keyring": ["{property_list[0]}"],
                        "coefficient": 1,
                        "pointer_type": "Bounded Number Property",
                        "script_element_type": "Pointer"
                      }},
                      {{
                        "coefficient": 10,
                        "pointer_type": "Bounded Number Constant",
                        "script_element_type": "Pointer"
                      }}
                    ]
                  }}
                }}
              ]
            }}
          ]
        }}
      ],
      "acceptability_script": {{
        "pointer_type": "Boolean Constant",
        "script_element_type": "Pointer",
        "value": true
      }},
      "desirability_script": {{
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
        "value": 0
      }},
      "creation_index": 0,
      "creation_time": 1700000000.0,
      "modified_time": 1700000000.0,
      "graph_position_x": 0,
      "graph_position_y": 0,
      "word_count": 100
    }}
  ],
  "unique_id_seeds": {{
    "character": {num_characters},
    "encounter": "[auto]",
    "option": "[auto]",
    "reaction": "[auto]",
    "spool": {num_spools},
    "authored_property": {num_properties * 2}
  }}
}}

Generate ONLY valid JSON conforming to this schema. Focus on creating meaningful narrative branches that explore the themes through character property changes."""
    
    return [{"role": "user", "content": prompt}]


def create_dataset(
    num_examples: int = 100,
    min_characters: int = 2,
    max_characters: int = 5,
    min_encounters: int = 5,
    max_encounters: int = 20,
    seed: int = 42,
) -> Dataset:
    """Create dataset of Sweepweave generation prompts"""
    
    random.seed(seed)
    
    prompts = []
    requirements = []
    
    for _ in range(num_examples):
        num_chars = random.randint(min_characters, max_characters)
        num_encs = random.randint(min_encounters, max_encounters)
        num_props = random.randint(2, 4)
        num_spools = random.randint(2, 5)
        
        prompt = generate_storyworld_prompt(
            num_characters=num_chars,
            num_properties=num_props,
            num_encounters=num_encs,
            num_spools=num_spools,
        )
        
        req = {
            "min_characters": num_chars,
            "min_encounters": num_encs,
            "min_spools": num_spools,
            "min_options_per_encounter": 3,
            "min_reactions_per_option": 2,
            "min_effects_per_reaction": 4,
        }
        
        prompts.append(prompt)
        requirements.append(req)
    
    return Dataset.from_dict({
        "prompt": prompts,
        "info": [{"requirements": r} for r in requirements],
    })


# ============================================================================
# REWARD FUNCTIONS
# ============================================================================

def reward_valid_json(prompt, completion, info) -> float:
    """Reward: 1.0 if valid JSON, 0.0 otherwise"""
    try:
        # Extract JSON from completion (handle markdown code blocks)
        text = completion[-1]["content"] if completion else ""
        
        # Strip markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        json.loads(text.strip())
        return 1.0
    except:
        return 0.0


def reward_schema_valid(prompt, completion, info) -> float:
    """Reward: 1.0 if valid Sweepweave schema, 0.0 otherwise"""
    try:
        text = completion[-1]["content"] if completion else ""
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text.strip())
        valid, _ = SweepweaveValidator.validate_structure(data)
        return 1.0 if valid else 0.0
    except:
        return 0.0


def reward_structural_completeness(prompt, completion, info) -> float:
    """Reward: 0-1 based on meeting structural requirements"""
    try:
        text = completion[-1]["content"] if completion else ""
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text.strip())
        requirements = info.get("requirements", {})
        return SweepweaveValidator.compute_structural_score(data, requirements)
    except:
        return 0.0


def reward_effect_diversity(prompt, completion, info) -> float:
    """Reward: 0-1 based on variety of after_effects"""
    try:
        text = completion[-1]["content"] if completion else ""
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_effect_diversity(data)
    except:
        return 0.0


def reward_min_spec_compliance(prompt, completion, info) -> float:
    """Reward: 0-1 based on min options/reactions/effects per non-ending encounter."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_min_spec_compliance(data)
    except:
        return 0.0


def reward_text_length_compliance(prompt, completion, info) -> float:
    """Reward: 0-1 based on encounter/reaction word counts."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_text_length_compliance(data)
    except:
        return 0.0


def reward_effects_per_reaction(prompt, completion, info) -> float:
    """Reward: 0-1 based on average after-effects per reaction (target 4.5)."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        val = SweepweaveValidator.compute_effects_per_reaction(data)
        return min(1.0, val / 4.5)
    except:
        return 0.0


def reward_reactions_per_option(prompt, completion, info) -> float:
    """Reward: 0-1 based on average reactions per option (target 2.5)."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        val = SweepweaveValidator.compute_reactions_per_option(data)
        return min(1.0, val / 2.5)
    except:
        return 0.0


def reward_options_per_encounter(prompt, completion, info) -> float:
    """Reward: 0-1 based on average options per encounter (target 3.2)."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        val = SweepweaveValidator.compute_options_per_encounter(data)
        return min(1.0, val / 3.2)
    except:
        return 0.0


def reward_desirability_var_usage(prompt, completion, info) -> float:
    """Reward: 0-1 based on average variable usage per desirability formula (target 1.6)."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        val = SweepweaveValidator.compute_desirability_vars_per_reaction(data)
        return min(1.0, val / 1.6)
    except:
        return 0.0


def reward_pvalue_desirability_alignment(prompt, completion, info) -> float:
    """Reward: 0-1 based on pValues used in desirability when reactions modify properties."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_pvalue_desirability_alignment(data)
    except:
        return 0.0


def reward_effect_script_quality(prompt, completion, info) -> float:
    """Reward: 0-1 based on after_effect scripts using operators and non-zero constants."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_effect_script_quality(data)
    except:
        return 0.0


def reward_act2_gating(prompt, completion, info) -> float:
    """Reward: 0-1 based on Act II gated option ratio and variable richness."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        stats = SweepweaveValidator.compute_act_gating_stats(data)
        pct, vars_avg = stats["act2"]
        return min(1.0, (pct / 5.0 + vars_avg / 1.2) / 2.0)
    except:
        return 0.0


def reward_act3_gating(prompt, completion, info) -> float:
    """Reward: 0-1 based on Act III gated option ratio and variable richness."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        stats = SweepweaveValidator.compute_act_gating_stats(data)
        pct, vars_avg = stats["act3"]
        return min(1.0, (pct / 8.0 + vars_avg / 1.5) / 2.0)
    except:
        return 0.0


def reward_secret_metric_distance(prompt, completion, info) -> float:
    """Reward: 0-1 based on secret encounter availability using 2-var metric distance."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_secret_metric_distance_quality(data)
    except:
        return 0.0


def reward_secret_paths(prompt, completion, info) -> float:
    """Reward: 0-1 based on gated options"""
    try:
        text = completion[-1]["content"] if completion else ""
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_gating_score(data)
    except:
        return 0.0


def reward_secret_gate_quality(prompt, completion, info) -> float:
    """Reward: 0-1 based on gated options with variable desirability and strong effects."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_secret_gate_quality(data)
    except:
        return 0.0


def reward_major_turns(prompt, completion, info) -> float:
    """Reward: 0-1 based on Act II/III gated flip/blend turning points."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_major_turn_quality(data)
    except:
        return 0.0


def reward_multiple_endings(prompt, completion, info) -> float:
    """Reward: 0-1 based on number of distinct endings"""
    try:
        text = completion[-1]["content"] if completion else ""
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_ending_diversity(data)
    except:
        return 0.0


def reward_schema_soft(prompt, completion, info) -> float:
    """Reward: 0-1 penalizing missing optional-but-important fields."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        missing = 0
        total = 0
        for char in data.get("characters", []):
            total += 1
            if "pronoun" not in char:
                missing += 1
        for prop in data.get("authored_properties", []):
            total += 1
            if "depth" not in prop:
                missing += 1
        if total == 0:
            return 0.0
        return max(0.0, 1.0 - (missing / total))
    except:
        return 0.0


def reward_dead_end_rate(prompt, completion, info) -> float:
    """Reward: 0-1 based on Monte Carlo dead-end rate (<5% target)."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        dead_end_rate = SweepweaveValidator.compute_dead_end_rate(data)
        return max(0.0, 1.0 - (dead_end_rate / 0.05))
    except:
        return 0.0


def reward_ending_balance(prompt, completion, info) -> float:
    """Reward: 0-1 based on ending distribution targets."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        max_share, min_share = SweepweaveValidator.compute_ending_balance(data)
        max_score = max(0.0, 1.0 - max(0.0, (max_share - 0.30)) / 0.30)
        min_score = min(1.0, min_share / 0.01)
        return (max_score + min_score) / 2.0
    except:
        return 0.0


def reward_unreachable_endings(prompt, completion, info) -> float:
    """Reward: 0-1 based on all endings being reachable."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return SweepweaveValidator.compute_unreachable_endings_score(data)
    except:
        return 0.0


def reward_late_blocking(prompt, completion, info) -> float:
    """Reward: 0-1 based on late-game blocking rate target (10-30%)."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        rate = SweepweaveValidator.compute_late_block_rate(data)
        if rate <= 0.1:
            return max(0.0, rate / 0.1)
        if rate >= 0.3:
            return max(0.0, 1.0 - (rate - 0.3) / 0.2)
        return 1.0
    except:
        return 0.0


def reward_secret_reachability(prompt, completion, info) -> float:
    """Reward: 0-1 based on secrets being reachable at least occasionally."""
    try:
        text = completion[-1]["content"] if completion else ""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        reach = SweepweaveValidator.compute_secret_reachability(data)
        return min(1.0, reach / 0.05) if reach > 0 else 0.0
    except:
        return 0.0


def benchmark_targets() -> Dict[str, float]:
    """Targets aligned to STORYWORLD_BALANCING.md."""
    return {
        "dead_end_rate_max": 0.05,
        "max_ending_share_max": 0.30,
        "min_ending_share_min": 0.01,
        "late_block_min": 0.10,
        "late_block_max": 0.30,
        "secret_reachability_min": 0.05,
        "secret_gate_quality_min": 0.30,
        "gated_ratio_min": 0.03,
        "gated_ratio_max": 0.05,
        "major_turns_min": 1.0,
        "ending_entropy_min": 1.5,
        "ending_entropy_soft_min": 1.2,
        "secret_reachability_max": 0.12,
        "ending_effective_min": 4.0,
        "effects_per_reaction_min": 4.5,
        "reactions_per_option_min": 2.5,
        "options_per_encounter_min": 3.2,
        "desirability_vars_min": 1.6,
        "act2_gate_pct_min": 5.0,
        "act2_gate_vars_min": 1.2,
        "act3_gate_pct_min": 8.0,
        "act3_gate_vars_min": 1.5,
        "secret_metric_distance_min": 1.0,
        "min_spec_compliance_min": 1.0,
        "text_length_compliance_min": 1.0,
    }


def evaluate_benchmark(data: Dict[str, Any], runs: int = 200, seed: int = 42) -> Dict[str, float]:
    """Return benchmark metrics for a storyworld."""
    report = run_monte_carlo(data, num_runs=runs, seed=seed)
    dead_end_rate = report["dead_ends"] / report["num_runs"] if report["num_runs"] else 1.0
    total = report["num_runs"]
    if total and report["ending_counts"]:
        max_share = max(report["ending_counts"].values()) / total
        min_share = min(report["ending_counts"].values()) / total
        # Shannon entropy over ending distribution
        import math
        entropy = 0.0
        for count in report["ending_counts"].values():
            if count <= 0:
                continue
            p = count / total
            entropy -= p * math.log(p + 1e-12, 2)
        # Effective number of endings
        effective = 2 ** entropy if entropy > 0 else 0.0
    else:
        max_share, min_share = 1.0, 0.0
        entropy = 0.0
        effective = 0.0
    late_block = (report["late_blocks"] / report["late_total"]) if report["late_total"] else 0.0
    secret_reach = (report.get("secret_any", 0) / total) if total else 0.0
    secret_gate_quality = SweepweaveValidator.compute_secret_gate_quality(data)
    gating_ratio = SweepweaveValidator.compute_gating_score(data)
    major_turn_quality = SweepweaveValidator.compute_major_turn_quality(data)
    late_block_applicable = report["late_total"] > 0
    effects_per_reaction = SweepweaveValidator.compute_effects_per_reaction(data)
    reactions_per_option = SweepweaveValidator.compute_reactions_per_option(data)
    options_per_encounter = SweepweaveValidator.compute_options_per_encounter(data)
    desirability_vars = SweepweaveValidator.compute_desirability_vars_per_reaction(data)
    act_stats = SweepweaveValidator.compute_act_gating_stats(data)
    act2_pct, act2_vars = act_stats["act2"]
    act3_pct, act3_vars = act_stats["act3"]
    secret_metric_distance = SweepweaveValidator.compute_secret_metric_distance_quality(data)
    min_spec_compliance = SweepweaveValidator.compute_min_spec_compliance(data)
    text_length_compliance = SweepweaveValidator.compute_text_length_compliance(data)
    return {
        "dead_end_rate": dead_end_rate,
        "max_ending_share": max_share,
        "min_ending_share": min_share,
        "ending_entropy": entropy,
        "ending_effective": effective,
        "late_block_rate": late_block,
        "secret_reachability": secret_reach,
        "secret_gate_quality": secret_gate_quality,
        "gated_ratio_score": gating_ratio,
        "major_turn_quality": major_turn_quality,
        "late_block_applicable": 1.0 if late_block_applicable else 0.0,
        "effects_per_reaction": effects_per_reaction,
        "reactions_per_option": reactions_per_option,
        "options_per_encounter": options_per_encounter,
        "desirability_vars": desirability_vars,
        "act2_gate_pct": act2_pct,
        "act2_gate_vars": act2_vars,
        "act3_gate_pct": act3_pct,
        "act3_gate_vars": act3_vars,
        "secret_metric_distance": secret_metric_distance,
        "min_spec_compliance": min_spec_compliance,
        "text_length_compliance": text_length_compliance,
    }


def benchmark_pass(metrics: Dict[str, float]) -> bool:
    targets = benchmark_targets()
    late_applicable = metrics.get("late_block_applicable", 1.0) >= 0.5
    return (
        metrics["dead_end_rate"] <= targets["dead_end_rate_max"]
        and metrics["max_ending_share"] <= targets["max_ending_share_max"]
        and metrics["min_ending_share"] >= targets["min_ending_share_min"]
        and (not late_applicable or (targets["late_block_min"] <= metrics["late_block_rate"] <= targets["late_block_max"]))
        and metrics["secret_reachability"] >= targets["secret_reachability_min"]
        and metrics["secret_reachability"] <= targets["secret_reachability_max"]
        and metrics.get("secret_gate_quality", 0.0) >= targets["secret_gate_quality_min"]
        and metrics.get("gated_ratio_score", 0.0) >= 0.8
        and metrics.get("major_turn_quality", 0.0) >= targets["major_turns_min"]
        and metrics.get("ending_entropy", 0.0) >= targets["ending_entropy_soft_min"]
        and metrics.get("ending_effective", 0.0) >= targets["ending_effective_min"]
        and metrics.get("effects_per_reaction", 0.0) >= targets["effects_per_reaction_min"]
        and metrics.get("reactions_per_option", 0.0) >= targets["reactions_per_option_min"]
        and metrics.get("options_per_encounter", 0.0) >= targets["options_per_encounter_min"]
        and metrics.get("desirability_vars", 0.0) >= targets["desirability_vars_min"]
        and metrics.get("act2_gate_pct", 0.0) >= targets["act2_gate_pct_min"]
        and metrics.get("act2_gate_vars", 0.0) >= targets["act2_gate_vars_min"]
        and metrics.get("act3_gate_pct", 0.0) >= targets["act3_gate_pct_min"]
        and metrics.get("act3_gate_vars", 0.0) >= targets["act3_gate_vars_min"]
        and metrics.get("secret_metric_distance", 0.0) >= targets["secret_metric_distance_min"]
        and metrics.get("min_spec_compliance", 0.0) >= targets["min_spec_compliance_min"]
        and metrics.get("text_length_compliance", 0.0) >= targets["text_length_compliance_min"]
    )


# ============================================================================
# ENVIRONMENT INTERFACE
# ============================================================================

def load_environment(
    num_examples: int = 100,
    min_characters: int = 2,
    max_characters: int = 5,
    min_encounters: int = 5,
    max_encounters: int = 20,
    seed: int = 42,
) -> vf.Environment:
    """
    Load Sweepweave narrative generation environment.
    
    Args:
        num_examples: Number of training examples to generate
        min_characters: Minimum number of characters per storyworld
        max_characters: Maximum number of characters per storyworld
        min_encounters: Minimum number of encounters per storyworld
        max_encounters: Maximum number of encounters per storyworld
        seed: Random seed for reproducibility
    
    Returns:
        verifiers.Environment configured for Sweepweave generation
    """
    
    dataset = create_dataset(
        num_examples=num_examples,
        min_characters=min_characters,
        max_characters=max_characters,
        min_encounters=min_encounters,
        max_encounters=max_encounters,
        seed=seed,
    )
    
    rubric = vf.Rubric(
        funcs=[
            reward_valid_json,           # Must be valid JSON
            reward_schema_valid,         # Must match Sweepweave schema
            reward_schema_soft,          # Soft penalty for missing fields
            reward_structural_completeness,  # Must meet size requirements
            reward_effect_diversity,     # Diverse Dirac operators
            reward_min_spec_compliance,  # Min options/reactions/effects compliance
            reward_text_length_compliance, # Word-count compliance
            reward_effects_per_reaction, # Effect density per reaction
            reward_reactions_per_option, # Reaction density per option
            reward_options_per_encounter, # Options per encounter
            reward_desirability_var_usage, # Vars per desirability
            reward_pvalue_desirability_alignment, # pValues for actors/witnesses
            reward_effect_script_quality, # Non-zero operator effects
            reward_secret_paths,         # Gated options
            reward_secret_gate_quality,  # Gated options with variable desirability
            reward_major_turns,          # Act II/III flip/blend turning points
            reward_act2_gating,          # Act II gating density
            reward_act3_gating,          # Act III gating density
            reward_secret_metric_distance,  # Secret metric distance gates
            reward_multiple_endings,     # Multiple terminal states
            reward_dead_end_rate,        # Monte Carlo dead-end rate
            reward_ending_balance,       # Ending distribution balance
            reward_unreachable_endings,  # All endings reachable
            reward_late_blocking,        # Late-game blocking rate
            reward_secret_reachability,  # Secret reachability
        ],
        weights=[
            1.0,   # Valid JSON is critical
            2.0,   # Schema validity is most important
            0.3,   # Soft schema completeness
            1.0,   # Structural completeness
            0.5,   # Effect diversity (nice to have)
            0.6,   # Min spec compliance
            0.6,   # Text length compliance
            0.6,   # Effects per reaction
            0.6,   # Reactions per option
            0.6,   # Options per encounter
            0.5,   # Desirability var usage
            0.5,   # pValue desirability alignment
            0.5,   # Effect script quality
            0.5,   # Secret paths (nice to have)
            0.6,   # Secret gate quality (accumulated thresholds)
            0.6,   # Major Act II/III turn quality
            0.5,   # Act II gating density
            0.5,   # Act III gating density
            0.4,   # Secret metric distance gates
            0.5,   # Multiple endings (nice to have)
            0.5,   # Dead-end rate (should be low)
            0.5,   # Ending balance (avoid dominance)
            0.6,   # Unreachable endings
            0.5,   # Late-game blocking (target band)
            0.3,   # Secret reachability (occasional)
        ],
    )
    
    return vf.SingleTurnEnv(
        dataset=dataset,
        rubric=rubric,
    )


if __name__ == "__main__":
    # Test environment creation
    env = load_environment(num_examples=10)
    print(f"Created Sweepweave environment with {len(env.dataset)} examples")
    
    # Show sample prompt
    sample = env.dataset[0]
    print("\n=== SAMPLE PROMPT ===")
    print(sample["prompt"][0]["content"][:500] + "...")
