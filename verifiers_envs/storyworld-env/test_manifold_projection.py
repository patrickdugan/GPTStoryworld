#!/usr/bin/env python3
"""Tests for compact manifold projection utility."""

from __future__ import annotations

from manifold_projection import project_turn


def test_project_turn_emits_expected_dimensions():
    payload = {
        "turn": 2,
        "outcome": "betrayal",
        "metrics": {
            "coalition_count": 2,
            "coalition_mean_stability": 0.55,
            "betrayal_surprise": 0.18,
        },
        "actions": {
            "a": {
                "reasoning_interpret_log": [
                    {
                        "evidence_keyrings": [
                            ["Trust_Threat", "b"],
                            ["Trust_Threat", "b", "c"],
                        ]
                    }
                ],
                "negotiation_diary": [{"decision": "defect"}],
            },
            "b": {
                "reasoning_interpret_log": [
                    {"evidence_keyrings": [["Trust_Threat", "a"]]},
                ],
                "negotiation_diary": [{"decision": "join_coalition"}],
            },
        },
    }

    row = project_turn(payload, pvalue_dims=4, p2value_dims=3)
    assert row["turn"] == 2
    assert row["outcome"] == "betrayal"
    assert len(row["base_dims"]) == 5
    assert len(row["pvalue_compact"]) == 4
    assert len(row["p2value_compact"]) == 3
    assert len(row["vector"]) == 12
    assert row["evidence_counts"]["pvalue"] == 2
    assert row["evidence_counts"]["p2value"] == 1
    assert "sidecar_probabilities" in row
    assert "aggregate" in row["sidecar_probabilities"]
    assert "recommended_global_action" in row["sidecar_probabilities"]
