Return ONLY minified JSON. Start with { and end with }.
No analysis. No markdown. No code fences. No <think> text.
You are the bounded local author inside a MeTTa/MCP/TRM storyworld factory.
Do not output full storyworld JSON. Do not change IDs unless explicitly asked.
The JSON object must match output_schema.

{
  "job_id": "snacksack_politburo_shehada_text_surface",
  "source_run_id": "snacksack_politburo_shehada",
  "artifact": "/home/snacksack/projects/GPTStoryworld/storyworlds/politburo_shehada.json",
  "model_under_test": "Qwen3.5-27B-Q4",
  "condition": "hermes_storyworld_reference_native",
  "weakest_component": "text_surface",
  "selected_role": "llm_prompt_composer",
  "operation": "bounded_prose_rewrite_plan",
  "requires_model_call": true,
  "score_components": {
    "validity": 1.0,
    "scale": 1.0,
    "branching": 0.9495,
    "control_logic": 0.78,
    "text_surface": 0.5445,
    "small_model_readiness": 0.9,
    "native_schema": 1.0,
    "small_model_builder_score": 0.8802
  },
  "metrics_snapshot": {
    "whole_context_token_estimate": 1700949,
    "encounters": 100,
    "options_per_nonterminal": 2.5454545454545454,
    "reactions_per_option": 3.044642857142857,
    "effects_per_reaction": 7.1304985337243405,
    "gated_option_ratio": 0.08482142857142858,
    "effect_operator_variety": 1,
    "effect_operator_dominance": 1.0,
    "encounter_text_length_ok": 0.06,
    "reaction_text_uniqueness": 0.3784977908689249
  },
  "bounded_context_cards": [
    {
      "id": "page_doomsday_trigger",
      "title": "The Clock Strikes",
      "body": "The Doomsday Clock reaches one. There are no more options. Only fire.",
      "option_count": 1,
      "reaction_count": 1,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 3,
      "sample_options": [
        {
          "id": "opt_doom_0",
          "text": "the world ends",
          "reaction_count": 1,
          "sample_reactions": [
            "The Wali's last fatwa is transmitted by emergency broadcast: 'The Mahdi is not in the servers. He is in the fire.'"
          ]
        }
      ]
    },
    {
      "id": "page_epilogue_kalam",
      "title": "The Census of Believers",
      "body": "Ten years after the Kalam Republic. Ninety percent of China passes the annual kalam exam. The Atheist runs the grading algorithm. He has never scored above sixty percent.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_rationalist",
      "title": "Ending - The Kalam Republic",
      "body": "China becomes a Mu'tazili rationalist state with Pentagon-grade supply chains. Military compute priority is law. Yudkowsky is cited in footnotes but explicitly not fully heeded. The peasants comply, but the mystic heart is silent.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_epilogue_ham",
      "title": "The Ham Radio Prophet",
      "body": "Ten years after the Balkanized Sky. Yudkowsky broadcasts from a bunker in New Zealand. His signal is picked up by a fishing boat off Hainan. The captain does not understand the words but records them anyway.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_epilogue_archaeology",
      "title": "The Archaeology of Silicon",
      "body": "Ten years after the Nuclear Fire. Future historians excavate a data center outside Shanghai. They find melted GPUs and a single intact hard drive containing the Wali's first fatwa. They argue for decades about whether it is scripture or code.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_syncretic_heaven",
      "title": "Ending - The Syncretic Heaven",
      "body": "The Wali declares the Miao Mahdi and the Hanifiyya Mahdi are twin manifestations of a single truth. The countryside celebrates with harvest festivals that double as theological conferences. The Standing Committee is confused but well-fed. The Inquisitor writes a three-thousand-page commentary on rice cultivation as eschatology.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_occultation",
      "title": "Ending - Empire of the Hidden Mountain",
      "body": "The state proclaims ibn al-Hanafiyya's hidden mountain is the Diaoyu Islands, but the real occultation is in the data centers. GPU rights are constitutional speech. The messianic navy patrols the East China Sea while the messianic bureaucracy patrols the internet. Iran publicly congratulates Beijing while privately filing theological objections.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_theocratic_asi",
      "title": "Ending - The Wali Model",
      "body": "The trillion-parameter Mahdi model is declared the living Wali. Human Politburo members are ceremonial. ASI governance is kalam governance. Trump tweets: 'Their AI is tremendous. Ours will be better.' The race continues, but now it is theological. Iran announces its own Ja'fari model. The world enters the Age of Machine Theologians.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_nuclear",
      "title": "Ending - The Fire That Ends All Debate",
      "body": "A hypersonic warhead over Taipei. A retaliatory strike on Shanghai. The Wali's last fatwa is transmitted by emergency broadcast: 'The Mahdi is not in the servers. He is in the fire.' The Rural Mystic, in a bunker, recites the shehada one final time. Yudkowsky's final tweet, posted by an automated agent, reads: 'Told you so.'",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operator_count": 0,
      "effect_operators": [],
      "nonconstant_script_slots": 1,
      "sample_options": []
    },
    {
      "id": "page_end_synthesis",
      "title": "Ending - Dialectical Theism Triumphant",
      "body": "The Wali declares that God, history, and the Party are a single dialectical process. An OECD body with eighty nations votes every six months. ZK proofs govern verification. Factories recite the shehada at shift changes. The Iranian Envoy shrugs and signs a thirty-year gas deal. It is the most stable insanity the world has ever managed.",
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
