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

REQUIRED_CHARACTER = ["id", "name", "pronoun", "bnumber_properties"]
REQUIRED_PROPERTY = ["id", "property_name", "property_type", "default_value", "depth"]
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
        
        # Reward some gating but not over-gating
        ratio = gated_options / total_options
        return min(ratio * 2, 1.0)  # Optimal around 50% gating
    
    @staticmethod
    def compute_ending_diversity(data: Dict[str, Any]) -> float:
        """Score based on multiple distinct endings"""
        # Find terminal encounters (no consequences pointing to other encounters)
        all_consequence_ids = set()
        encounter_ids = set()
        
        for enc in data.get("encounters", []):
            encounter_ids.add(enc.get("id"))
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    cons_id = rxn.get("consequence_id")
                    if cons_id:
                        all_consequence_ids.add(cons_id)
        
        # Terminal encounters = encounters not referenced as consequences
        terminal = encounter_ids - all_consequence_ids
        num_endings = len(terminal)
        
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
        hits = sum(report["secret_hits"].values())
        return hits / total


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
    endings = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_end_")]
    secrets = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_secret_")]

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

        for sec in secrets:
            if eval_script(sec.get("acceptability_script", True), state):
                secret_hits[sec["id"]] += 1

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
        \"chain_length\": len(chain),
        \"num_endings\": len(endings),
        \"num_secrets\": len(secrets),
        \"num_runs\": num_runs,
        \"ending_counts\": ending_counts,
        \"dead_ends\": dead_ends,
        \"late_blocks\": late_blocks,
        \"late_total\": late_total,
        \"secret_hits\": secret_hits,
        \"prop_sums\": prop_sums,
        \"prop_sq\": prop_sq,
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
- {num_encounters} interconnected encounters
- {num_spools} narrative spools controlling encounter availability
- Each encounter has 2-3 options
- Each option has 1-3 reactions with different consequences
- Each reaction has after_effects modifying character properties
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
    "encounter": {num_encounters},
    "option": {num_encounters * 2},
    "reaction": {num_encounters * 4},
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
            "min_options_per_encounter": 2,
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
        return min(1.0, reach / 0.02) if reach > 0 else 0.0
    except:
        return 0.0


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
            reward_structural_completeness,  # Must meet size requirements
            reward_effect_diversity,     # Diverse Dirac operators
            reward_secret_paths,         # Gated options
            reward_multiple_endings,     # Multiple terminal states
            reward_dead_end_rate,        # Monte Carlo dead-end rate
            reward_ending_balance,       # Ending distribution balance
            reward_late_blocking,        # Late-game blocking rate
            reward_secret_reachability,  # Secret reachability
        ],
        weights=[
            1.0,   # Valid JSON is critical
            2.0,   # Schema validity is most important
            1.0,   # Structural completeness
            0.5,   # Effect diversity (nice to have)
            0.5,   # Secret paths (nice to have)
            0.5,   # Multiple endings (nice to have)
            0.5,   # Dead-end rate (should be low)
            0.5,   # Ending balance (avoid dominance)
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
