"""
SweepWeave JSON construction helpers.
Import these when writing patch/enrichment scripts for storyworld JSON files.

Usage:
    from sweepweave_helpers import *
    effect = make_effect("char_civ", "Embodiment_Virtuality", 0.045)
"""
import json


# ─── Text Scripts ────────────────────────────────────────────────────────────

def make_text_script(value):
    """Create a String Constant pointer for prompt_script, text_script, etc."""
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


# ─── Bounded Number Primitives ───────────────────────────────────────────────

def const(value):
    """Create a Bounded Number Constant."""
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}


def prop_pointer(character, prop, coefficient=1.0):
    """Create a Bounded Number Pointer referencing a character property."""
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": character,
        "keyring": [prop],
        "coefficient": coefficient,
    }


# ─── Operators ───────────────────────────────────────────────────────────────

def comparator(subtype, left, right):
    """Create an Arithmetic Comparator operator.

    Subtypes: "Greater Than or Equal To", "Less Than or Equal To",
              "Greater Than", "Less Than", "Equal To", "Not Equal To"
    """
    return {
        "operator_type": "Arithmetic Comparator",
        "script_element_type": "Operator",
        "operator_subtype": subtype,
        "operands": [left, right],
    }


def cmp_gte(character, prop, threshold):
    """Shortcut: character.prop >= threshold."""
    return comparator("Greater Than or Equal To", prop_pointer(character, prop), const(threshold))


def cmp_lte(character, prop, threshold):
    """Shortcut: character.prop <= threshold."""
    return comparator("Less Than or Equal To", prop_pointer(character, prop), const(threshold))


def and_gate(*operands):
    """Logical AND of multiple operands."""
    return {"operator_type": "And", "script_element_type": "Operator", "operands": list(operands)}


def or_gate(*operands):
    """Logical OR of multiple operands."""
    return {"operator_type": "Or", "script_element_type": "Operator", "operands": list(operands)}


def add(*operands):
    """Addition operator."""
    return {"operator_type": "Addition", "script_element_type": "Operator", "operands": list(operands)}


def multiply(*operands):
    """Multiplication operator."""
    return {"operator_type": "Multiplication", "script_element_type": "Operator", "operands": list(operands)}


def abs_val(operand):
    """Absolute value operator."""
    return {"operator_type": "Absolute Value", "script_element_type": "Operator", "operands": [operand]}


# ─── Effects ─────────────────────────────────────────────────────────────────

def make_effect(character, prop, delta):
    """Create a Bounded Number Effect using the Nudge operator.

    Result: character.prop = clamp(character.prop + delta, -1, 1)
    """
    return {
        "effect_type": "Bounded Number Effect",
        "Set": prop_pointer(character, prop),
        "to": {
            "operator_type": "Nudge",
            "script_element_type": "Operator",
            "operands": [
                prop_pointer(character, prop),
                const(delta),
            ],
        },
    }


def make_dual_effect(character, base_prop, base_delta, cumulative_delta=None):
    """Create both base and cumulative property effects.

    Returns a list of 1-2 effects.
    """
    effects = [make_effect(character, base_prop, base_delta)]
    if cumulative_delta is not None:
        effects.append(make_effect(character, "p" + base_prop, cumulative_delta))
    return effects


# ─── Visibility Gates ───────────────────────────────────────────────────────

def make_visibility_gate(character, prop, subtype, threshold):
    """Create a visibility_script gate (Arithmetic Comparator)."""
    return comparator(subtype, prop_pointer(character, prop), const(threshold))


def make_abs_threshold_gate(character, cumulative_prop, threshold):
    """Gate that passes if |cumulative_prop| >= threshold.

    Uses OR: prop >= threshold OR prop <= -threshold
    """
    return or_gate(
        cmp_gte(character, cumulative_prop, threshold),
        cmp_lte(character, cumulative_prop, -threshold),
    )


# ─── Structural Builders ────────────────────────────────────────────────────

def make_option(page_id, opt_index, text, visibility=True):
    """Create an option structure."""
    return {
        "id": f"opt_{page_id}_{opt_index}",
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "text_script": make_text_script(text),
        "visibility_script": visibility,
        "performability_script": True,
        "reactions": [],
    }


def make_reaction(page_id, opt_index, rxn_index, text, consequence_id, effects,
                  desirability=1.0):
    """Create a reaction structure with after_effects."""
    return {
        "id": f"opt_{page_id}_{opt_index}_r{rxn_index}",
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "text_script": make_text_script(text),
        "consequence_id": consequence_id,
        "desirability_script": const(desirability),
        "after_effects": effects if isinstance(effects, list) else [effects],
    }


# ─── Encounter Analysis ─────────────────────────────────────────────────────

def get_primary_effect(encounter):
    """Extract the primary char_civ effect from an encounter's first option.

    Returns (property_name, delta) or (None, None).
    """
    try:
        ae = encounter["options"][0]["reactions"][0]["after_effects"][0]
        char = ae["Set"]["character"]
        prop = ae["Set"]["keyring"][0]
        delta = ae["to"]["operands"][1]["value"]
        if char == "char_civ" and not prop.startswith("p"):
            return prop, delta
    except (KeyError, IndexError):
        pass
    return None, None


def build_spool_map(data):
    """Build encounter_id -> spool_name mapping."""
    spool_map = {}
    for sp in data.get("spools", []):
        for eid in sp.get("encounters", []):
            spool_map[eid] = sp["spool_name"]
    return spool_map


def get_encounter_slot(data, encounter_id, spool_name):
    """Get the slot index (0-5) of an encounter within its age spool."""
    for sp in data["spools"]:
        if sp["spool_name"] == spool_name:
            if encounter_id in sp["encounters"]:
                return sp["encounters"].index(encounter_id)
    return None


# ─── Inclination Formulas ───────────────────────────────────────────────────

def inclination_attractor(cumulative_prop, weight=0.3):
    """Desirability = weight * |cumulative_prop|.

    Creates attractor basin: encounters aligned with player trajectory preferred.
    """
    return multiply(const(weight), abs_val(prop_pointer("char_civ", cumulative_prop)))


def inclination_ca(weight=0.4):
    """Desirability = weight * Counter-Archivist Influence."""
    return multiply(const(weight), prop_pointer("char_counter_archivist", "Influence"))


def inclination_constant(value=0.5):
    """Constant desirability (for relics, secrets)."""
    return const(value)


# ─── Ending Gate Patterns ───────────────────────────────────────────────────

def gate_strong_axis(character, prop, threshold):
    """Gate: property above threshold (for positive-direction endings)."""
    return cmp_gte(character, prop, threshold)


def gate_weak_axis(character, prop, threshold):
    """Gate: property below threshold (for negative-direction endings)."""
    return cmp_lte(character, prop, threshold)


def gate_moderate_axis(character, prop, band=0.06):
    """Gate: property within ±band (for centrist/moderate endings)."""
    return and_gate(
        cmp_gte(character, prop, -band),
        cmp_lte(character, prop, band),
    )


def gate_archivist_victory(ca_countercraft=0.15, ca_influence=0.10, civ_band=0.06):
    """Gate: strong CA + uncommitted civilization.

    All 6 civ base properties must be within ±civ_band.
    """
    civ_props = [
        "Embodiment_Virtuality", "Hedonism_Austerity", "Risk_Stasis",
        "Cohesion_Fragmentation", "Transgression_Order", "Cosmic_Ambition_Humility",
    ]
    conditions = [
        cmp_gte("char_counter_archivist", "Countercraft", ca_countercraft),
        cmp_gte("char_counter_archivist", "Influence", ca_influence),
    ]
    for prop in civ_props:
        conditions.append(cmp_lte("char_civ", prop, civ_band))
        conditions.append(cmp_gte("char_civ", prop, -civ_band))
    return and_gate(*conditions)


def gate_universal_fallback():
    """Universal fallback ending: always acceptable, very low desirability."""
    return True  # acceptability_script = true


# ─── Backfire Table ──────────────────────────────────────────────────────────

BACKFIRE_TABLE = {
    "Embodiment_Virtuality":    ("Cohesion_Fragmentation",    "Less Than or Equal To",    -0.1),
    "Hedonism_Austerity":       ("Risk_Stasis",               "Greater Than or Equal To",  0.15),
    "Risk_Stasis":              ("Cohesion_Fragmentation",    "Less Than or Equal To",    -0.1),
    "Cohesion_Fragmentation":   ("Transgression_Order",       "Greater Than or Equal To",  0.15),
    "Transgression_Order":      ("Cosmic_Ambition_Humility",  "Greater Than or Equal To",  0.2),
    "Cosmic_Ambition_Humility": ("Risk_Stasis",               "Less Than or Equal To",    -0.15),
}


def get_backfire_gate(primary_prop):
    """Get the visibility gate for a backfire reaction on the given primary property.

    Returns a visibility_script dict, or None if no backfire defined.
    """
    if primary_prop not in BACKFIRE_TABLE:
        return None
    vuln_prop, comparator_type, threshold = BACKFIRE_TABLE[primary_prop]
    return make_visibility_gate("char_civ", vuln_prop, comparator_type, threshold)


# ─── Effect Magnitude Constants ──────────────────────────────────────────────

class EffectMagnitudes:
    """Calibrated effect magnitudes for ~120-encounter storyworlds (post Monte Carlo)."""
    BOLD_BASE = 0.045
    BOLD_CUMULATIVE = 0.022
    DECEPTIVE_BASE = 0.045
    DECEPTIVE_CUMULATIVE = 0.022
    DECEPTIVE_GRUDGE = 0.015
    MODERATE_BASE = 0.024
    MODERATE_CUMULATIVE = 0.012
    BACKFIRE_REVERSE = -0.030
    BACKFIRE_GRUDGE = 0.024
    CA_REVERSAL = -0.030
    CA_COUNTERCRAFT = 0.030
    SPECTACULAR_BASE = 0.060
    SPECTACULAR_CUMULATIVE = 0.030
    SPECTACULAR_GRUDGE = -0.009
    RELIC_INFLUENCE = 0.010


# ─── File I/O ────────────────────────────────────────────────────────────────

def load_storyworld(path):
    """Load a SweepWeave storyworld JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_storyworld(data, path):
    """Save a SweepWeave storyworld JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
