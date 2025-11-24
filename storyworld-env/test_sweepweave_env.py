#!/usr/bin/env python3
"""Test suite for Sweepweave environment"""

import json
import pytest
from sweepweave_env import (
    SweepweaveValidator,
    generate_storyworld_prompt,
    create_dataset,
    reward_valid_json,
    reward_schema_valid,
    reward_structural_completeness,
    reward_effect_diversity,
    reward_secret_paths,
    reward_multiple_endings,
    load_environment,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def minimal_valid_storyworld():
    """Minimal valid Sweepweave storyworld"""
    return {
        "IFID": "SW-TEST-001",
        "storyworld_title": "Test Story",
        "storyworld_author": "Test",
        "sweepweave_version": "0.1.9",
        "creation_time": 1700000000.0,
        "modified_time": 1700000000.0,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "lilac",
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": {
            "pointer_type": "String Constant",
            "script_element_type": "Pointer",
            "value": "Test storyworld"
        },
        "characters": [
            {
                "id": "char_test",
                "name": "Test",
                "pronoun": "they",
                "bnumber_properties": {
                    "Loyal_Treacherous": 0,
                    "pLoyal_Treacherous": {}
                }
            }
        ],
        "authored_properties": [
            {
                "id": "Loyal_Treacherous",
                "property_name": "Loyal_Treacherous",
                "property_type": "bounded number",
                "default_value": 0,
                "depth": 0,
                "attribution_target": "all cast members",
                "affected_characters": [],
                "creation_index": 0,
                "creation_time": 1700000000.0,
                "modified_time": 1700000000.0
            }
        ],
        "spools": [
            {
                "id": "spool_main",
                "spool_type": "General"
            }
        ],
        "encounters": [
            {
                "id": "page_start",
                "title": "Start",
                "connected_spools": ["spool_main"],
                "text_script": {
                    "pointer_type": "String Constant",
                    "script_element_type": "Pointer",
                    "value": "The story begins."
                },
                "options": [
                    {
                        "id": "page_start_opt1",
                        "text_script": {
                            "pointer_type": "String Constant",
                            "script_element_type": "Pointer",
                            "value": "Continue"
                        },
                        "reactions": [
                            {
                                "id": "page_start_opt1_rxn1",
                                "text_script": {
                                    "pointer_type": "String Constant",
                                    "script_element_type": "Pointer",
                                    "value": "You continue."
                                },
                                "consequence_id": "page_end",
                                "after_effects": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": "page_end",
                "title": "End",
                "connected_spools": ["spool_main"],
                "text_script": {
                    "pointer_type": "String Constant",
                    "script_element_type": "Pointer",
                    "value": "The end."
                },
                "options": []
            }
        ],
        "unique_id_seeds": {
            "character": 1,
            "encounter": 2,
            "option": 1,
            "reaction": 1,
            "spool": 1,
            "authored_property": 1
        }
    }


@pytest.fixture
def complex_storyworld(minimal_valid_storyworld):
    """Complex storyworld with effects and gating"""
    data = minimal_valid_storyworld.copy()
    
    # Add more characters
    data["characters"].extend([
        {
            "id": "char_alice",
            "name": "Alice",
            "pronoun": "she",
            "bnumber_properties": {
                "Loyal_Treacherous": 0,
                "Calm_Explosive": 0,
                "pLoyal_Treacherous": {},
                "pCalm_Explosive": {}
            }
        },
        {
            "id": "char_bob",
            "name": "Bob",
            "pronoun": "he",
            "bnumber_properties": {
                "Loyal_Treacherous": 0,
                "Calm_Explosive": 0,
                "pLoyal_Treacherous": {},
                "pCalm_Explosive": {}
            }
        }
    ])
    
    # Add more properties
    data["authored_properties"].append({
        "id": "Calm_Explosive",
        "property_name": "Calm_Explosive",
        "property_type": "bounded number",
        "default_value": 0,
        "depth": 0,
        "attribution_target": "all cast members",
        "affected_characters": [],
        "creation_index": 1,
        "creation_time": 1700000000.0,
        "modified_time": 1700000000.0
    })
    
    # Add effects to first encounter
    data["encounters"][0]["options"][0]["reactions"][0]["after_effects"] = [
        {
            "effect_type": "Set",
            "Set": {
                "character": "char_alice",
                "keyring": ["Loyal_Treacherous"],
                "coefficient": 1,
                "pointer_type": "Bounded Number Property",
                "script_element_type": "Pointer"
            },
            "to": {
                "script_element_type": "Bounded Number Operator",
                "operator_type": "Addition",
                "operands": [
                    {
                        "character": "char_alice",
                        "keyring": ["Loyal_Treacherous"],
                        "coefficient": 1,
                        "pointer_type": "Bounded Number Property",
                        "script_element_type": "Pointer"
                    },
                    {
                        "coefficient": 10,
                        "pointer_type": "Bounded Number Constant",
                        "script_element_type": "Pointer"
                    }
                ]
            }
        },
        {
            "effect_type": "Increment",
            "Increment": {
                "character": "char_bob",
                "keyring": ["Calm_Explosive"],
                "coefficient": 5,
                "pointer_type": "Bounded Number Property",
                "script_element_type": "Pointer"
            }
        }
    ]
    
    # Add gated option
    data["encounters"][0]["options"].append({
        "id": "page_start_opt2",
        "text_script": {
            "pointer_type": "String Constant",
            "script_element_type": "Pointer",
            "value": "Secret option"
        },
        "visibility_script": {
            "script_element_type": "Boolean Operator",
            "operator_type": "GreaterThan",
            "pointer_type": "Boolean Property",
            "operands": [
                {
                    "character": "char_alice",
                    "keyring": ["Loyal_Treacherous"],
                    "coefficient": 1,
                    "pointer_type": "Bounded Number Property",
                    "script_element_type": "Pointer"
                },
                {
                    "coefficient": 50,
                    "pointer_type": "Bounded Number Constant",
                    "script_element_type": "Pointer"
                }
            ]
        },
        "reactions": [
            {
                "id": "page_start_opt2_rxn1",
                "text_script": {
                    "pointer_type": "String Constant",
                    "script_element_type": "Pointer",
                    "value": "Secret path taken."
                },
                "consequence_id": "page_secret",
                "after_effects": []
            }
        ]
    })
    
    # Add secret ending
    data["encounters"].append({
        "id": "page_secret",
        "title": "Secret Ending",
        "connected_spools": ["spool_main"],
        "text_script": {
            "pointer_type": "String Constant",
            "script_element_type": "Pointer",
            "value": "You found the secret!"
        },
        "options": []
    })
    
    return data


# ============================================================================
# VALIDATOR TESTS
# ============================================================================

def test_validator_structure_valid(minimal_valid_storyworld):
    """Test that minimal valid storyworld passes validation"""
    valid, errors = SweepweaveValidator.validate_structure(minimal_valid_storyworld)
    assert valid, f"Validation failed: {errors}"
    assert len(errors) == 0


def test_validator_structure_missing_fields():
    """Test that missing fields are detected"""
    invalid = {"IFID": "test"}
    valid, errors = SweepweaveValidator.validate_structure(invalid)
    assert not valid
    assert len(errors) > 0
    assert any("Missing top-level field" in e for e in errors)


def test_validator_structural_score(minimal_valid_storyworld):
    """Test structural scoring"""
    requirements = {
        "min_characters": 1,
        "min_encounters": 2,
        "min_spools": 1,
        "min_options_per_encounter": 1,
    }
    score = SweepweaveValidator.compute_structural_score(minimal_valid_storyworld, requirements)
    assert score == 1.0  # Meets all requirements


def test_validator_structural_score_partial():
    """Test partial structural scoring"""
    data = {
        "characters": [{"id": "c1"}],  # 1 character
        "encounters": [{"id": "e1", "options": []}],  # 1 encounter
        "spools": [{"id": "s1"}],  # 1 spool
    }
    requirements = {
        "min_characters": 2,  # Wants 2, has 1
        "min_encounters": 2,  # Wants 2, has 1
        "min_spools": 1,      # Wants 1, has 1
    }
    score = SweepweaveValidator.compute_structural_score(data, requirements)
    # (0.5 + 0.5 + 1.0) / 3 = 0.667
    assert 0.6 < score < 0.7


def test_validator_effect_diversity(complex_storyworld):
    """Test effect diversity scoring"""
    score = SweepweaveValidator.compute_effect_diversity(complex_storyworld)
    # Has 2 effects: Set and Increment
    # diversity = 2/2 = 1.0, density = min(2/10, 1) = 0.2
    # (1.0 + 0.2) / 2 = 0.6
    assert 0.5 < score < 0.7


def test_validator_gating_score(complex_storyworld):
    """Test gating score"""
    score = SweepweaveValidator.compute_gating_score(complex_storyworld)
    # First encounter has 2 options, 1 gated
    # 1/2 = 0.5, min(0.5 * 2, 1.0) = 1.0
    assert score == 1.0


def test_validator_ending_diversity(complex_storyworld):
    """Test ending diversity scoring"""
    score = SweepweaveValidator.compute_ending_diversity(complex_storyworld)
    # Has 2 terminal encounters (page_end, page_secret)
    assert score == 1.0


# ============================================================================
# DATASET GENERATION TESTS
# ============================================================================

def test_generate_storyworld_prompt():
    """Test prompt generation"""
    prompt = generate_storyworld_prompt(
        num_characters=3,
        num_properties=3,
        num_encounters=10,
        num_spools=3,
    )
    assert isinstance(prompt, list)
    assert len(prompt) == 1
    assert prompt[0]["role"] == "user"
    assert "Sweepweave" in prompt[0]["content"]
    assert "JSON" in prompt[0]["content"]


def test_create_dataset():
    """Test dataset creation"""
    dataset = create_dataset(num_examples=10, seed=42)
    assert len(dataset) == 10
    assert "prompt" in dataset.column_names
    assert "info" in dataset.column_names
    
    # Check first example
    example = dataset[0]
    assert isinstance(example["prompt"], list)
    assert isinstance(example["info"], dict)
    assert "requirements" in example["info"]


# ============================================================================
# REWARD FUNCTION TESTS
# ============================================================================

def test_reward_valid_json(minimal_valid_storyworld):
    """Test JSON validation reward"""
    completion = [{"role": "assistant", "content": json.dumps(minimal_valid_storyworld)}]
    score = reward_valid_json(None, completion, {})
    assert score == 1.0
    
    # Invalid JSON
    completion = [{"role": "assistant", "content": "not json"}]
    score = reward_valid_json(None, completion, {})
    assert score == 0.0


def test_reward_valid_json_with_markdown(minimal_valid_storyworld):
    """Test JSON extraction from markdown"""
    json_str = json.dumps(minimal_valid_storyworld)
    content = f"```json\n{json_str}\n```"
    completion = [{"role": "assistant", "content": content}]
    score = reward_valid_json(None, completion, {})
    assert score == 1.0


def test_reward_schema_valid(minimal_valid_storyworld):
    """Test schema validation reward"""
    completion = [{"role": "assistant", "content": json.dumps(minimal_valid_storyworld)}]
    score = reward_schema_valid(None, completion, {})
    assert score == 1.0
    
    # Invalid schema
    invalid = {"IFID": "test"}
    completion = [{"role": "assistant", "content": json.dumps(invalid)}]
    score = reward_schema_valid(None, completion, {})
    assert score == 0.0


def test_reward_structural_completeness(minimal_valid_storyworld):
    """Test structural completeness reward"""
    info = {
        "requirements": {
            "min_characters": 1,
            "min_encounters": 2,
            "min_spools": 1,
        }
    }
    completion = [{"role": "assistant", "content": json.dumps(minimal_valid_storyworld)}]
    score = reward_structural_completeness(None, completion, info)
    assert score == 1.0


def test_reward_effect_diversity(complex_storyworld):
    """Test effect diversity reward"""
    completion = [{"role": "assistant", "content": json.dumps(complex_storyworld)}]
    score = reward_effect_diversity(None, completion, {})
    assert score > 0.0


def test_reward_secret_paths(complex_storyworld):
    """Test secret paths reward"""
    completion = [{"role": "assistant", "content": json.dumps(complex_storyworld)}]
    score = reward_secret_paths(None, completion, {})
    assert score > 0.0


def test_reward_multiple_endings(complex_storyworld):
    """Test multiple endings reward"""
    completion = [{"role": "assistant", "content": json.dumps(complex_storyworld)}]
    score = reward_multiple_endings(None, completion, {})
    assert score == 1.0


# ============================================================================
# ENVIRONMENT TESTS
# ============================================================================

def test_load_environment():
    """Test environment loading"""
    env = load_environment(num_examples=10)
    assert env is not None
    assert len(env.dataset) == 10
    assert env.rubric is not None


def test_environment_rubric():
    """Test rubric configuration"""
    env = load_environment(num_examples=10)
    assert len(env.rubric.funcs) == 6
    assert len(env.rubric.weights) == 6
    assert sum(env.rubric.weights) == 5.5  # 1.0 + 2.0 + 1.0 + 0.5 + 0.5 + 0.5


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_end_to_end_perfect_score(minimal_valid_storyworld):
    """Test perfect score on valid output"""
    env = load_environment(num_examples=1)
    
    # Simulate model output
    completion = [{"role": "assistant", "content": json.dumps(minimal_valid_storyworld)}]
    info = env.dataset[0]["info"]
    
    # Compute all rewards
    scores = []
    for func, weight in zip(env.rubric.funcs, env.rubric.weights):
        score = func(None, completion, info)
        scores.append(score * weight)
    
    total = sum(scores)
    # Should get high score (valid JSON + valid schema + meets requirements)
    assert total >= 4.0  # At least 4.0 out of 5.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
