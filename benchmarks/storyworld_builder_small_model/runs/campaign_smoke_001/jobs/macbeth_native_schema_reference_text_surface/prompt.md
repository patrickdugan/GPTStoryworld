You are the bounded local author inside a MeTTa/MCP/TRM storyworld factory.
Do not output full storyworld JSON. Do not change IDs unless explicitly asked.
Return JSON only matching output_schema.

{
  "job_id": "macbeth_native_schema_reference_text_surface",
  "source_run_id": "macbeth_native_schema_reference",
  "artifact": "C:\\projects\\GPTStoryworld\\storyworlds\\by-week\\2026-W11\\validated_macbeth.json",
  "model_under_test": "scaffold",
  "condition": "packet_author_native",
  "weakest_component": "text_surface",
  "selected_role": "llm_prompt_composer",
  "operation": "bounded_prose_rewrite_plan",
  "requires_model_call": true,
  "score_components": {
    "validity": 1.0,
    "scale": 0.85,
    "branching": 1.0,
    "control_logic": 0.866,
    "text_surface": 0.7086,
    "small_model_readiness": 0.9,
    "native_schema": 1.0,
    "small_model_builder_score": 0.9112
  },
  "metrics_snapshot": {
    "whole_context_token_estimate": 705087,
    "encounters": 16,
    "options_per_nonterminal": 4.833333333333333,
    "reactions_per_option": 3.0689655172413794,
    "effects_per_reaction": 8.657303370786517,
    "gated_option_ratio": 1.0,
    "effect_operator_variety": 2,
    "effect_operator_dominance": 0.7832576249188838,
    "encounter_text_length_ok": 0.25,
    "reaction_text_uniqueness": 0.5842696629213483
  },
  "bounded_context_cards": [
    {
      "id": "page_end_0123",
      "title": "Ending: The Canmore Settlement",
      "body": "Dunfermline, Benedictine influence, new names, and new loyalties all point to a kingdom that is no longer simply Alba of the old chronicles. The house changes, the language changes, and the realm survives by changing with them.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_0122",
      "title": "Ending: The Ashes of Dunsinane",
      "body": "The crown passes through smoke and grief, and Lulach''s brief coronation cannot stop the return of Malcolm. The story ends in dynastic loss, but it also records how much history had to happen before Malcolm could inherit it.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_0121",
      "title": "Ending: The Roman Pilgrimage",
      "body": "The kingdom does not escape violence, but it does escape the cheap version of history that reduces Macbeth to a single murderous night. Alba remains a political kingdom with a ruler who understood that legitimacy had to be built in more than one register.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    }
  ],
  "constraints": [
    "Do not output full storyworld JSON.",
    "Preserve existing IDs and mechanics unless the output schema asks for new slot IDs.",
    "Write only the local proposal needed by the selected role.",
    "Assume deterministic scaffold/verifiers will materialize and commit/veto."
  ],
  "output_schema": {
    "encounter_rewrites": [
      {
        "encounter_id": "string",
        "title": "short title",
        "body": "70-150 words",
        "reaction_rewrites": [
          "12-50 words each"
        ]
      }
    ],
    "preserve_ids_and_mechanics": true
  }
}
