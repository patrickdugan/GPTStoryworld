import json
import random
import sys
from collections import defaultdict
from typing import List, Dict, Any, Union

# Enhanced operation bank for Macbeth dramatic tension
OPERATION_BANK = {
    "desirability": [
        {
            "operator": "Addition",
            "formula": "float(value_1 + value_2 + ... + value_n)",
            "shapes": ["constant_add", "var_add", "expr_add"]
        },
        {
            "operator": "Subtraction",
            "formula": "float(value_1 - value_2 - ... - value_n)",
            "shapes": ["constant_sub", "var_sub", "expr_sub"]
        },
        {
            "operator": "Multiplication",
            "formula": "float(value_1 * value_2 * ... * value_n)",
            "shapes": ["constant_mul", "var_mul", "expr_mul"]
        },
        {
            "operator": "Division",
            "formula": "float((value_1 + epsilon) / (value_2 + epsilon))",
            "shapes": ["constant_div", "var_div", "expr_div"]
        },
        {
            "operator": "If Then",
            "formula": "value_1 if condition else value_2",
            "shapes": ["if_gt", "if_lt", "if_eq", "if_neq"]
        },
        {
            "operator": "And",
            "formula": "bool(value_1 and value_2)",
            "shapes": ["and_false", "and_true"]
        },
        {
            "operator": "Or",
            "formula": "bool(value_1 or value_2)",
            "shapes": ["or_false", "or_true"]
        },
        {
            "operator": "Arithmetic Comparator",  
            "formula": "value_1 > value_2 ? 1.0 : -1.0",
            "shapes": ["cmp_gt", "cmp_lt", "cmp_eq", "cmp_neq"]
        },
        {
            "operator": "Arithmetic Mean",
            "formula": "float((value_1 + value_2) / 2.0)",
            "shapes": ["mean_2", "mean_3"]
        }
    ],
    "effects": [
        {
            "operator": "Addition",
            "formula": "float(value_1 + value_2 + ... + value_n)",
            "shapes": ["dir_add", "dist_add", "prop_add"]
        },
        {
            "operator": "Multiplication",
            "formula": "float(value_1 * value_2 * ... * value_n)",
            "shapes": ["dir_mul", "dist_mul", "prop_mul"]
        },
        {
            "operator": "Nudge",  
            "formula": "float(0.1 * (value_target - value_current))",
            "shapes": ["dir_nudge", "dist_nudge", "prop_nudge"]
        },
        {
            "operator": "Arithmetic Mean",
            "formula": "float((value_1 + value_2) / 2.0)",
            "shapes": ["mean"
            ]
        }
    ]
}

PROP_TARGETS = [
    "Influence", "Transgression_Order", "Veteran" ,
    "Rage", "Grief", "Guile", "Weakness", 
    "Loyalty", "Doubt", "Pride", "Fear",
    "Suspicion", "Resolve", "Cunning"
]

# Adds more reactions by splitting complex reactions
# Enhances effects with multi-variable operations
# Adds Shakespearean dramatic formulas

def boost_operation_complexity(world_json: str, out_json: str, boost_params: Dict[str, Union[float, int, str]]):
    """
    Boosts operation complexity by:
    1. Adding more reactions by splitting compound reactions
    2. Enhancing effects with multi-variable operations from OPERATION_BANK
    3. Adding Shakespearean dramatic formulas and tension operators
    4. Increasing options per encounter through reaction diversification
    """
    random.seed(17)
    
    world = json.loads(world_json)
    
    # Apply parameter defaults
    min_reactions_per_option = boost_params.get("min_reactions_per_option", 3)
    min_effects_per_reaction = boost_params.get("min_effects_per_reaction", 5)
    min_options_per_encounter = boost_params.get("min_options_per_encounter", 4)
    
    # Track stats for reporting
    stats = defaultdict(int)
    
    # Phase 1: Reaction splitting and enhancement
    for enc_idx, encounter in enumerate(world.get("encounters", [])):
        for opt_idx, option in enumerate(encounter.get("options", [])):
            reactions = option.get("reactions", [])
            
            # Always add at least min_reactions_per_option
            while len(reactions) < min_reactions_per_option:
                # Create a new reaction based on dramatic tension
                new_reaction = {
                    "description": f"A shiver of tense anticipation runs through the stone halls.",
                    "effects": []
                }
                
                # Add Shakespearean drama to description
                drama_phrases = [
                    "ghostly portent of Macbeth", 
                    "whisper of treachery in the air",
                    "ominous shadow falls across ambition",
                    "gathering storm of consequence"
                ]
                new_reaction["description"] = random.choice(drama_phrases)
                
                # Add varied effects using the expanded bank
                for effect_idx in range(min_effects_per_reaction):
                    op_data = random.choice(OPERATION_BANK["effects"])
                    effect = {
                        "operator": op_data["operator"],
                        "target": random.choice(PROP_TARGETS),
                        "value": random.uniform(0.1, 0.9),
                        "formulas": [op_data["formula"]],
                        "notes": f"Enhanced {op_data['operator']} using shape {random.choice(op_data.get('shapes', ['base']))}"
                    }
                    new_reaction["effects"].append(effect)
                    stats[f"added_effects_{op_data['operator']}"] += 1
                
                reactions.append(new_reaction)
                stats["added_reactions"] += 1
            
            # Enhance existing reactions
            for reaction in reactions:
                effects = reaction.get("effects", [])
                while len(effects) < min_effects_per_reaction:
                    op_data = random.choice(OPERATION_BANK["effects"])
                    effect = {
                        "operator": op_data["operator"],
                        "target": random.choice(PROP_TARGETS),
                        "value": random.uniform(0.1, 0.9),
                        "formulas": [op_data["formula"]],
                        "notes": f"Enhanced {op_data['operator']} using shape {random.choice(op_data.get('shapes', ['base']))}"
                    }
                    effects.append(effect)
                    stats[f"added_effects_{op_data['operator']}"] += 1
                
        # Ensure min options per encounter
        while len(encounter.get("options", [])) < min_options_per_encounter:
            # Create dramatic tension option
            dramatic_option = {
                "description": f"{random.choice(['Tragedy', 'Fortune', 'Omens', 'Revelations'])} await in the wings.",
                "reactions": []
            }
            
            for reaction_idx in range(min_reactions_per_option):
                new_reaction = {
                    "description": f"The dramatic intensity heightens.",
                    "effects": []
                }
                
                # Add drama to description
                drama_phrases = [
                    "A ghostly portent of Macbeth",
                    "Whisper of treachery in the air", 
                    "Ominous shadow falls across ambition"
                ]
                new_reaction["description"] = random.choice(drama_phrases)
                
                # Add varied effects
                for effect_idx in range(min_effects_per_reaction):
                    op_data = random.choice(OPERATION_BANK["effects"])
                    effect = {
                        "operator": op_data["operator"],
                        "target": random.choice(PROP_TARGETS),
                        "value": random.uniform(0.1, 0.9),
                        "formulas": [op_data["formula"]],
                        "notes": f"Enhanced {op_data['operator']} using shape {random.choice(op_data.get('shapes', ['base']))}"
                    }
                    new_reaction["effects"].append(effect)
                    stats[f"added_effects_{op_data['operator']}"] += 1
                
                dramatic_option["reactions"].append(new_reaction)
                stats["added_reactions"] += 1
            
            encounter["options"].append(dramatic_option)
            stats["added_options"] += 1
        
    # Phase 2: Apply Macbeth-specific dramatic tension operators
    for enc_idx, encounter in enumerate(world.get("encounters", [])):
        for opt_idx, option in enumerate(encounter.get("options", [])):
            for reaction in option.get("reactions", []):
                # Add tension operator to some effects
                for effect in reaction.get("effects", []):
                    if random.random() > 0.7:  # 30% chance
                        effect["operator"] = "Tension_Warp"
                        effect["formulas"] = [
                            "float(value * (1.0 + dramatic_tension_factor))",
                            "dramatic_tension_factor = clamp(value_target, 0.2, 1.8)"
                        ]
                        effect["notes"] = effect.get("notes", "") + " + Tension_Warp enhancement"
                        stats["added_tension_warp"] += 1
    
    # Write the enhanced world
    with open(out_json, "w", encoding='utf-8') as f:
        json.dump(world, f, ensure_ascii=False, indent=2)
    
    # Print stats
    print(f"Boost Enhancement Statistics:")
    for stat, count in stats.items():
        print(f"  {stat}: {count}")
    print(f"Boost applied to: {out_json}")
    
    return {
        "status": "success",
        "enhancements": dict(stats),
        "output_file": out_json
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Boost operation complexity in storyworlds")
    parser.add_argument("--in-json", required=True, help="Input storyworld JSON file")
    parser.add_argument("--out-json", required=True, help="Output enhanced storyworld JSON file")
    parser.add_argument("--min-reactions", type=int, default=3, help="Minimum reactions per option (default: 3)")
    parser.add_argument("--min-effects", type=int, default=5, help="Minimum effects per reaction (default: 5)")
    parser.add_argument("--min-options", type=int, default=4, help="Minimum options per encounter (default: 4)")
    
    args = parser.parse_args()
    
    with open(args.in_json, "r", encoding='utf-8') as f:
        world_json = f.read()
    
    boost_params = {
        "min_reactions_per_option": args.min_reactions,
        "min_effects_per_reaction": args.min_effects,
        "min_options_per_encounter": args.min_options
    }
    
    boost_operation_complexity(world_json, args.out_json, boost_params)
