#!/usr/bin/env python3
"""
SWEEPWEAVE RL ENVIRONMENT - ALL-IN-ONE FILE
============================================

Complete implementation in a single file for easy copying.
This includes:
- Core environment (verifiers interface)
- Corpus amplification system
- All helper functions and validators

To use as a package, split into separate files as shown in the
directory structure. For quick testing, you can run this directly.

Usage:
    python ALL_IN_ONE.py --test           # Run basic tests
    python ALL_IN_ONE.py --estimate       # Show estimates
    python ALL_IN_ONE.py --generate 100   # Generate 100 configs
"""

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
    def compute_pvalue_desirability_alignment(data: Dict[str, Any]) -> float:
        """Fraction of reactions with property effects whose desirability uses pValues for actors and witnesses."""
        total = 0
        ok = 0
        for enc in data.get("encounters", []):
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    effects = rxn.get("after_effects", []) or []
                    affected = []
                    for eff in effects:
                        if eff.get("effect_type") != "Bounded Number Effect":
                            continue
                        ptr = eff.get("Set", {})
                        char = ptr.get("character")
                        keyring = ptr.get("keyring") or []
                        if not char or not keyring:
                            continue
                        prop = keyring[0]
                        if isinstance(prop, str):
                            affected.append((char, prop))
                    if not affected:
                        continue
                    total += 1
                    desirability = rxn.get("desirability_script")
                    pvalue_by_prop: Dict[str, Dict[str, set]] = {}
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
                        has_op = isinstance(to, dict) and "operator_type" in to
                        has_nonzero = SweepweaveValidator._script_has_nonzero_constant(to)
                        if has_op and has_nonzero:
                            ok += 1
        return (ok / total) if total else 0.0

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
            reward_pvalue_desirability_alignment, # pValues for actors/witnesses
            reward_effect_script_quality, # Non-zero operator effects
            reward_secret_paths,         # Gated options
            reward_unreachable_endings,  # All endings reachable
            reward_multiple_endings,     # Multiple terminal states
        ],
        weights=[
            1.0,   # Valid JSON is critical
            2.0,   # Schema validity is most important
            1.0,   # Structural completeness
            0.5,   # Effect diversity (nice to have)
            0.5,   # pValue desirability alignment
            0.5,   # Effect script quality
            0.5,   # Secret paths (nice to have)
            0.6,   # Unreachable endings
            0.5,   # Multiple endings (nice to have)
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
-e 

# ============================================================================
# CORPUS AMPLIFICATION SYSTEM
# ============================================================================

#!/usr/bin/env python3
"""
Corpus Amplification System for Sweepweave

Generates billions of tokens through:
1. Combinatorial theme/property expansion
2. Variable complexity (characters, encounters, spools)
3. Semantic injection from existing corpus
4. Quality filtering via RL-trained models

Target: 1M storyworlds × 20k tokens = 20B tokens
"""

import json
import random
import itertools
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse


@dataclass
class StoryConfig:
    """Configuration for generating a storyworld"""
    num_characters: int
    num_properties: int
    num_encounters: int
    num_spools: int
    themes: List[str]
    setting: str
    property_axes: List[Tuple[str, str]]
    unique_id: str


# ============================================================================
# EXPANDED CONFIGURATION SPACE
# ============================================================================

# Personality/relationship axes (can be combined for 100+ unique property sets)
PROPERTY_AXES = [
    # Classic psychological dimensions
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
    
    # Cognitive styles
    ("Analytical", "Intuitive"),
    ("Focused", "Scattered"),
    ("Systematic", "Improvisational"),
    ("Literal", "Metaphorical"),
    ("Skeptical", "Credulous"),
    
    # Social dynamics
    ("Reserved", "Expressive"),
    ("Diplomatic", "Confrontational"),
    ("Yielding", "Assertive"),
    ("Independent", "Conformist"),
    ("Private", "Transparent"),
    
    # Moral/ethical
    ("Consequentialist", "Deontological"),
    ("Utilitarian", "Rights_Based"),
    ("Mercy", "Justice"),
    ("Forgiveness", "Retribution"),
    ("Equality", "Hierarchy"),
    
    # Epistemic
    ("Evidence_Based", "Faith_Based"),
    ("Open_Minded", "Dogmatic"),
    ("Certain", "Uncertain"),
    ("Empirical", "Theoretical"),
    ("Inductive", "Deductive"),
    
    # Temporal
    ("Present_Focused", "Future_Oriented"),
    ("Patient", "Impulsive"),
    ("Reflective", "Reactive"),
    ("Planning", "Spontaneous"),
    ("Long_Term", "Short_Term"),
]

# Thematic dimensions (can be combined for 1000+ unique theme sets)
THEMES = [
    # AI/Technology
    "alignment problem",
    "mesa-optimization",
    "instrumental convergence",
    "value learning",
    "corrigibility",
    "interpretability",
    "mechanistic transparency",
    "epistemic cleanliness",
    
    # Warfare/Conflict
    "6th generation warfare",
    "information dominance",
    "memetic warfare",
    "asymmetric conflict",
    "deterrence theory",
    "escalation dynamics",
    
    # Philosophy
    "consciousness and qualia",
    "free will vs determinism",
    "personal identity",
    "moral realism",
    "epistemic humility",
    "wujudic logic",
    
    # Social/Political
    "surveillance capitalism",
    "consent manufacturing",
    "institutional capture",
    "principal-agent problems",
    "preference falsification",
    "Schelling points",
    
    # Economics/Game Theory
    "coordination failures",
    "tragedy of commons",
    "public goods provision",
    "mechanism design",
    "information asymmetry",
    "adverse selection",
    
    # Narrative/Meta
    "storyworld coherence",
    "narrative causality",
    "dramatic irony",
    "unreliable narration",
    "metafictional awareness",
    "recursive embedding",
]

# Settings/scenarios (100+ options)
SETTINGS = [
    # Space/Sci-fi
    "space station negotiation",
    "generation ship committee",
    "orbital habitat council",
    "asteroid mining dispute",
    "terraform project oversight",
    "first contact protocol",
    "dyson sphere construction",
    "wormhole transit authority",
    
    # Cyberpunk/Near-future
    "corporate board meeting",
    "underground hacktivist cell",
    "augmented reality courtroom",
    "neural interface clinic",
    "surveillance state resistance",
    "posthuman commune",
    "AI rights tribunal",
    "data haven negotiation",
    
    # Research/Academic
    "quantum computing lab",
    "bioethics committee",
    "particle physics collaboration",
    "archaeological expedition",
    "climate modeling team",
    "synthetic biology startup",
    "consciousness research facility",
    "prediction market consortium",
    
    # Governance/Politics
    "decentralized protocol governance",
    "diplomatic summit",
    "treaty negotiation",
    "constitutional convention",
    "regulatory hearing",
    "emergency response team",
    "disaster recovery committee",
    "referendum campaign",
    
    # Economic/Financial
    "venture capital pitch",
    "merger negotiation",
    "bankruptcy proceedings",
    "market manipulation investigation",
    "derivatives clearinghouse",
    "central bank meeting",
    "crypto protocol fork",
    "carbon credit exchange",
]


# ============================================================================
# CONFIGURATION GENERATOR
# ============================================================================

class ConfigGenerator:
    """Generate diverse storyworld configurations"""
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.config_count = 0
    
    def generate_config(
        self,
        min_chars: int = 2,
        max_chars: int = 5,
        min_props: int = 2,
        max_props: int = 6,
        min_encs: int = 5,
        max_encs: int = 30,
        min_spools: int = 2,
        max_spools: int = 5,
        num_themes: int = 2,
    ) -> StoryConfig:
        """Generate a random valid configuration"""
        
        num_characters = self.rng.randint(min_chars, max_chars)
        num_properties = self.rng.randint(min_props, max_props)
        num_encounters = self.rng.randint(min_encs, max_encs)
        num_spools = self.rng.randint(min_spools, max_spools)
        
        # Sample themes and setting
        themes = self.rng.sample(THEMES, min(num_themes, len(THEMES)))
        setting = self.rng.choice(SETTINGS)
        
        # Sample property axes
        property_axes = self.rng.sample(PROPERTY_AXES, min(num_properties, len(PROPERTY_AXES)))
        
        self.config_count += 1
        unique_id = f"SW-GEN-{self.config_count:06d}"
        
        return StoryConfig(
            num_characters=num_characters,
            num_properties=num_properties,
            num_encounters=num_encounters,
            num_spools=num_spools,
            themes=themes,
            setting=setting,
            property_axes=property_axes,
            unique_id=unique_id,
        )
    
    def generate_batch(self, num_configs: int, **kwargs) -> List[StoryConfig]:
        """Generate a batch of configurations"""
        return [self.generate_config(**kwargs) for _ in range(num_configs)]
    
    def estimate_coverage(self) -> Dict[str, int]:
        """Estimate total possible unique configurations"""
        
        # Character counts: 2-5 = 4 options
        char_options = 4
        
        # Property counts: 2-6 = 5 options
        prop_options = 5
        
        # Encounter counts: 5-30 = 26 options
        enc_options = 26
        
        # Spool counts: 2-5 = 4 options
        spool_options = 4
        
        # Theme combinations (choose 2 from ~50): C(50,2) = 1225
        theme_combinations = len(THEMES) * (len(THEMES) - 1) // 2
        
        # Settings: ~100
        setting_options = len(SETTINGS)
        
        # Property axis combinations (choose 3 from ~30): C(30,3) = 4060
        prop_combinations = len(PROPERTY_AXES) * (len(PROPERTY_AXES) - 1) * (len(PROPERTY_AXES) - 2) // 6
        
        total = (char_options * prop_options * enc_options * spool_options * 
                 theme_combinations * setting_options * prop_combinations)
        
        return {
            "character_options": char_options,
            "property_options": prop_options,
            "encounter_options": enc_options,
            "spool_options": spool_options,
            "theme_combinations": theme_combinations,
            "setting_options": setting_options,
            "property_combinations": prop_combinations,
            "total_unique_configs": total,
        }


# ============================================================================
# CORPUS INJECTION
# ============================================================================

class CorpusInjector:
    """Inject semantic content from existing corpus into storyworld generation"""
    
    def __init__(self, corpus_path: Optional[Path] = None):
        self.corpus_path = corpus_path
        self.corpus_loaded = False
        self.semantic_index = {}
    
    def load_corpus(self):
        """Load and index existing corpus (placeholder for QFT-MCP integration)"""
        if not self.corpus_path or not self.corpus_path.exists():
            print("No corpus provided, using synthetic content")
            return
        
        # TODO: Integrate with QFT-MCP for phase-based retrieval
        # For now, just load raw text
        print(f"Loading corpus from {self.corpus_path}")
        self.corpus_loaded = True
    
    def get_thematic_content(self, theme: str, max_tokens: int = 500) -> str:
        """Retrieve corpus content relevant to theme"""
        
        if not self.corpus_loaded:
            # Synthetic fallback
            return f"[Thematic content about {theme}]"
        
        # TODO: Use QFT-MCP to retrieve phase-encoded relevant passages
        # For now, placeholder
        return f"[Retrieved content about {theme}]"
    
    def enhance_prompt(self, base_prompt: str, config: StoryConfig) -> str:
        """Enhance prompt with corpus-derived content"""
        
        enhancements = []
        
        for theme in config.themes:
            content = self.get_thematic_content(theme)
            enhancements.append(f"\nThematic guidance for '{theme}':\n{content}")
        
        if enhancements:
            return base_prompt + "\n\n" + "\n".join(enhancements)
        
        return base_prompt


# ============================================================================
# BATCH GENERATION SYSTEM
# ============================================================================

class BatchGenerator:
    """Orchestrate large-scale storyworld generation"""
    
    def __init__(
        self,
        output_dir: Path,
        config_generator: ConfigGenerator,
        corpus_injector: Optional[CorpusInjector] = None,
    ):
        self.output_dir = output_dir
        self.config_generator = config_generator
        self.corpus_injector = corpus_injector
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "manifest.jsonl"
    
    def generate_batch(
        self,
        batch_size: int = 1000,
        batch_id: Optional[int] = None,
    ) -> List[StoryConfig]:
        """Generate a batch of configurations and save manifest"""
        
        configs = self.config_generator.generate_batch(batch_size)
        
        # Save manifest
        with open(self.manifest_path, "a") as f:
            for config in configs:
                entry = {
                    "unique_id": config.unique_id,
                    "batch_id": batch_id,
                    "num_characters": config.num_characters,
                    "num_properties": config.num_properties,
                    "num_encounters": config.num_encounters,
                    "num_spools": config.num_spools,
                    "themes": config.themes,
                    "setting": config.setting,
                    "property_axes": [f"{p[0]}_{p[1]}" for p in config.property_axes],
                }
                f.write(json.dumps(entry) + "\n")
        
        return configs
    
    def estimate_token_count(self, config: StoryConfig) -> int:
        """Estimate tokens in generated storyworld"""
        
        # Rough estimates:
        # - Base structure: ~1000 tokens
        # - Per character: ~200 tokens
        # - Per property: ~100 tokens
        # - Per encounter: ~500-1000 tokens (depending on options/reactions)
        # - Per spool: ~50 tokens
        
        base = 1000
        char_tokens = config.num_characters * 200
        prop_tokens = config.num_properties * 100
        enc_tokens = config.num_encounters * 750  # Average
        spool_tokens = config.num_spools * 50
        
        return base + char_tokens + prop_tokens + enc_tokens + spool_tokens
    
    def estimate_corpus_size(self, num_storyworlds: int) -> Dict[str, float]:
        """Estimate total corpus size"""
        
        # Sample configs to get average
        sample_configs = self.config_generator.generate_batch(100)
        avg_tokens = sum(self.estimate_token_count(c) for c in sample_configs) / len(sample_configs)
        
        total_tokens = num_storyworlds * avg_tokens
        
        return {
            "num_storyworlds": num_storyworlds,
            "avg_tokens_per_storyworld": avg_tokens,
            "total_tokens": total_tokens,
            "total_tokens_billions": total_tokens / 1e9,
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Sweepweave corpus amplification system")
    parser.add_argument("--output-dir", type=Path, default=Path("./corpus_output"),
                        help="Output directory for generated configs")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="Number of configs per batch")
    parser.add_argument("--num-batches", type=int, default=10,
                        help="Number of batches to generate")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--corpus-path", type=Path,
                        help="Path to existing corpus for semantic injection")
    parser.add_argument("--estimate-only", action="store_true",
                        help="Only show coverage estimates")
    
    args = parser.parse_args()
    
    # Initialize
    config_gen = ConfigGenerator(seed=args.seed)
    corpus_inj = CorpusInjector(corpus_path=args.corpus_path) if args.corpus_path else None
    batch_gen = BatchGenerator(args.output_dir, config_gen, corpus_inj)
    
    # Show coverage estimate
    coverage = config_gen.estimate_coverage()
    print("\n=== CONFIGURATION SPACE COVERAGE ===")
    for key, value in coverage.items():
        if value > 1e6:
            print(f"{key}: {value:,.0f} ({value/1e6:.1f}M)")
        else:
            print(f"{key}: {value:,}")
    
    # Estimate corpus size
    print("\n=== CORPUS SIZE ESTIMATES ===")
    for target in [1000, 10000, 100000, 1000000]:
        est = batch_gen.estimate_corpus_size(target)
        print(f"\n{target:,} storyworlds:")
        print(f"  Avg tokens/storyworld: {est['avg_tokens_per_storyworld']:,.0f}")
        print(f"  Total tokens: {est['total_tokens']:,.0f} ({est['total_tokens_billions']:.2f}B)")
    
    if args.estimate_only:
        return
    
    # Generate batches
    print(f"\n=== GENERATING {args.num_batches} BATCHES ===")
    for batch_id in range(args.num_batches):
        configs = batch_gen.generate_batch(args.batch_size, batch_id)
        print(f"Batch {batch_id}: {len(configs)} configs generated")
    
    print(f"\nManifest written to: {batch_gen.manifest_path}")
    print(f"Total configs: {args.num_batches * args.batch_size:,}")


if __name__ == "__main__":
    main()
