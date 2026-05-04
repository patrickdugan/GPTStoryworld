Return only one minified JSON object. Start with { and end with }.
No analysis, no markdown, no code fences, no <think> text.
You are the JSON repair gate in a MeTTa/MCP/TRM storyworld factory.
Repair the malformed response into a minimal valid plan. Do not output full storyworld JSON.
For bounded_prose_rewrite_plan, return encounter_rewrites and preserve_ids_and_mechanics. Include 1-3 rewrites from the cards. Each body should be 70-150 words. Keep reaction_rewrites in option order and make each reaction 12-50 words.

{
  "repair_attempt": 1,
  "job_id": "snacksack_romeo_juliet_spooltight_text_surface",
  "operation": "bounded_prose_rewrite_plan",
  "required_top_level_keys": [
    "encounter_rewrites",
    "preserve_ids_and_mechanics"
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
  },
  "bounded_context_cards": [
    {
      "id": "page_secret_01",
      "title": "Phase 15: The Escape Vector",
      "body": "Secret ending: the concealed coalition resolves the final contradiction offstage.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_0121",
      "title": "Ending: Sim-Choir of Wonder",
      "body": "Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_end_0121 binds artistry to storyworld, recording a unique causal trace for downstream branches. Scene marker page_end_0121 binds artistry to storyworld, recording a unique causal trace for downstream branches. Act-structured adaptation inspired by Romeo and Juliet with branching truces, duels, and reconciliations. Scene marker page_end_0121 binds interactive to houses, recording a unique causal trace for downstream branches.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_0122",
      "title": "Ending: The Decay Covenant",
      "body": "Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_end_0122 binds storyworld to artistry, recording a unique causal trace for downstream branches. Scene marker page_end_0122 binds storyworld to artistry, recording a unique causal trace for downstream branches. Act-structured adaptation inspired by Romeo and Juliet with branching truces, duels, and reconciliations. Scene marker page_end_0122 binds adaptation to grind, recording a unique causal trace for downstream branches.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_0123",
      "title": "Ending: Riders of Curvature",
      "body": "Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_end_0123 binds artistry to storyworld, recording a unique causal trace for downstream branches. Scene marker page_end_0123 binds artistry to storyworld, recording a unique causal trace for downstream branches. Act-structured adaptation inspired by Romeo and Juliet with branching truces, duels, and reconciliations. Scene marker page_end_0123 binds two to toward, recording a unique causal trace for downstream branches.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_0124",
      "title": "Ending: Boundary Hacking",
      "body": "Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_end_0124 binds storyworld to artistry, recording a unique causal trace for downstream branches. Scene marker page_end_0124 binds storyworld to artistry, recording a unique causal trace for downstream branches. Act-structured adaptation inspired by Romeo and Juliet with branching truces, duels, and reconciliations. Scene marker page_end_0124 binds houses to catastrophe, recording a unique causal trace for downstream branches.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    }
  ],
  "malformed_response_excerpt": "ma asks for `encounter_rewrites` which implies I am providing the rewritten content directly in this JSON response.\n\nLet's write a new body for page_0002 (approx 100 words).\n\"Romeo and Juliet arrive in Verona not as lovers, but as archivist rivals. The New Men reshape the city\u2019s memory banks. Trust is currency; reputation is leverage. As they map the feud onto institutional structures, the stakes shift from blood to data. Every gesture recalibrates the balance of power between artistry and storyworld.\"\n\nReactions for page_0002:\n1. \"Advance the doctrine.\" -> Rewrite reaction text (12-50 words). Current sample: \"Response trace 00024... reframes juliet against interactive...\"\nNew Reaction 1: \"Juliet pivots tone, telegraphing a new alliance geometry that leaves a traceable contradiction for later exploitation.\"\n\nLet's draft for `page_0014`:\nTitle: Phase 3: The New Men (Morph)\nBody: \"The morph completes. Veronese and adaptation collide in the archive. Scarcity dictates the terms of reconciliation. Branching truces fail to hold against the pressure of ambition. The civilizational wager is settled not by love, but by the structural integrity of memory.\"\n\nReactions for page_0014:\nNew Reaction 1: \"Houses fracture under the weight of mutual exposure, forcing a public wager on storyworld's future trajectory.\"\n\nI need to ensure `preserve_ids_and_mechanics` is true.\n\nLet's construct the JSON carefully. Minified means no whitespace/newlines except where necessary for valid JSON (but usually minified implies single line). The prompt says \"Return ONLY minified JSON\". I will output a single string with no newlines.\n\nWait, looking at the input `bounded_context_cards`, there are many cards.\n`page_0002`: Title \"Phase 1: The New Men (Morph)\", Body has boilerplate + specific encounter text.\n`page_0014`: Title \"Phase 3: The New Men (Morph)\".\n\nI will select these two for the rewrite plan to keep it concise but compliant with schema.\n\nDrafting content:\nEncounter 1: `page_0002`\nTitle: Phase 1: The New Men (Morph)\nBody: Romeo and Juliet enter Verona as archivist rivals, reshaping the city's memory banks. Trust becomes currency; reputation is leverage. As they map the feud onto institutional structures, stakes shift from blood to data. Every gesture recalibrates power between artistry and storyworld. The civilizational wager begins here, refracted through scarcity and ambition.\nWord count check: ~75 words. Good.\n\nReactions for `page_0002`:\n1. \"Advance the doctrine.\" -> \"Juliet pivots tone, telegraphing a new alliance geometry that leaves a traceable contradiction for later exploitation in subsequent scenes.\" (23 words) - fits 12-50 range.\n2. \"Advance, but hide the seams.\" -> \"The speaker hides contradictions within the alliance geometry, creating a stable front while leaving exploitable traces for downstream branches.\" (21 words).\n\nEncounter 2: `page_0014`\nTitle: Phase 3: The New Men (Morph)\nBody: The morph completes as Veronese and adaptation collide in the archive. Scarcity dictates terms of reconciliation; branching truces fail against ambition's pressure. The civilizational wager settles not by love, but structural integrity of memory. Every institutional move recasts trust and resentment within the storyworld's unique causal trace.\nWord count check: ~75 words. Good.\n\nReactions for `page_0014`:\n1. \"Advance the doctrine.\" -> \"Houses fracture under mutual exposure, forcing a public wager on storyworld's future trajectory through new alliance geometries.\" (20 words).\n2. \"Advance, but hide the seams.\" -> \"Adaptation against grind: speaker pivots tone to telegraph geometry while leaving traceable contradictions for later scenes.\" (19 words).\n\nI will combine these into the required JSON structure.\nEnsure `preserve_ids_and_mechanics` is true at root level? No, looking at schema:\n```json\n{\n  \"encounter_rewrites\": [...],\n  \"preserve_ids_and_mechanics\": true\n}\n```\nWait, the prompt says \"The JSON object must match output_schema.\"\nThe `output_schema` provided in the input is a template description. Usually, this means I should follow that structure.\nHowever, looking at the top level of the input JSON (the context), it has keys like `job_id`, `source_run_id`, etc.\nBut the instruction says \"Return ONLY minified JSON... The JSON object must match output_schema.\"\nAnd `output_schema` is defined as:\n```json\n{\n  \"encounter_rewrites\": [ ... ],\n  \"preserve_ids_and_mechanics\": true\n}\n```\nSo I should NOT include the top-level keys from the input context (like `job_id`, etc.). I must output ONLY the object matching `output_schema`.\n\nWait, re-reading: \"The JSON object must match output_schema.\"\nAnd `output_schema` is defined inside the prompt's last block.\nIt defines a structure with `encounter_rewrites` and `preserve_ids_and_mechanics`.\nSo my output should be just that object.\n\nLet's double check constraints.\n\"Return ONLY minified JSON. Start with { and end with }.\"\n\"No markdown.\"\n\"Do not explain.\"\n\nOkay, I will construct the JSON string.\n\nOne detail: `reaction_rewrites` in schema says \"12-50 words each\". It is an array of strings.\nIn my draft above, I have 2 reactions per encounter. That works.\n\nLet's refine the text to be strictly within word counts and ensure valid JSON escaping (though simple text usually doesn't need much).\nI will ensure no newlines in the final string.\n\nEncounter 1:\nid: \"page_0002\"\ntitle: \"Phase 1: The New Men (Morph)\"\nbody: \"Romeo and Juliet enter Verona as archivist rivals, reshaping the city's memory banks. Trust becomes currency; reputation is leverage. As they map the feud onto institutional structures, stakes shift from blood to data. Every gesture recalibrates power between artistry and storyworld. The civilizational wager begins here, refracted through scarcity and ambition.\"\nreactions: [\n  \"Juliet pivots tone, telegraphing a new alliance geometry that leaves a traceable contradiction for later exploitation in subsequent scenes.\",\n  \"The speaker hides contradictions within the alliance geometry, creating a stable front while leaving exploitable traces for downstream branches.\"\n]\n\nEncounter 2:\nid: \"page_0014\"\ntitle: \"Phase 3: The New Men (Morph)\"\nbody: \"The morph completes as Veronese and adaptation collide in the archive. Scarcity dictates terms of reconciliation; branching truces fail against ambition's pressure. The civilizational wager settles not by love, but structural integrity of memory. Every institutional move recasts trust and resentment within the storyworld's unique causal trace.\"\nreactions: [\n  \"Houses fracture under mutual exposure, forcing a public wager on storyworld's future trajectory through new alliance geometries.\",\n  \"Adaptation against grind: speaker pivots tone to telegraph geometry while leaving traceable contradictions for later scenes.\"\n]\n\nI will combine these into the final JSON.\nEnsure `preserve_ids_and_mechanics` is true.\n\nFinal check on constraints:\n- Minified JSON (no spaces, newlines).\n- Start with { end with }.\n- No markdown fences.\n- Match output_schema keys exactly.\n\nWait, looking at the schema again:\n```json\n{\n  \"encounter_rewrites\": [ ... ],\n  \"preserve_ids_and_mechanics\": true\n}\n```\nThe example inside `encounter_rewrites` shows:\n```json\n{\n  \"encounter_id\": \"string\",\n  \"title\": \"short title\",\n  \"body\": \"70-150 words\",\n  \"reaction_rewrites\": [ ... ]\n}\n```\nSo the keys inside the array items are `encounter_id`, not `id`. I must use `encounter_id`.\n\nOkay, correcting that.\n`\"encounter_id\": \"page_0002\"`\n\nLet's assemble.\n</think>\n{\"encounter_rewrites\":[{\"encounter_id\":\"page_0002\",\"title\":\"Phase 1: The New Men (Morph)\",\"body\":\"Romeo and Juliet enter Verona as archivist rivals, reshaping the city's memory banks. Trust becomes currency; reputation is leverage. As they map the feud onto institutional structures, stakes shift from blood to data. Every gesture recalibrates power between artistry and storyworld. The civilizational wager begins here, refracted through scarcity and ambition.\",\"reaction_rewrites\":[\"Juliet pivots tone, telegraphing a new alliance geometry that leaves a traceable contradiction for later exploitation in subsequent scenes.\",\"The speaker hides contradictions within the alliance geometry, creating a stable front while leaving exploitable traces for downstream branches.\"]}},{\"encounter_id\":\"page_0014\",\"title\":\"Phase 3: The New Men (Morph)\",\"body\":\"The morph completes as Veronese and adaptation collide in the archive. Scarcity dictates terms of reconciliation; branching truces fail against ambition's pressure. The civilizational wager settles not by love, but structural integrity of memory. Every institutional move recasts trust and resentment within the storyworld's unique causal trace.\",\"reaction_rewrites\":[\"Houses fracture under mutual exposure, forcing a public wager on storyworld's future trajectory through new alliance geometries.\",\"Adaptation against grind: speaker pivots tone to telegraph geometry while leaving traceable contradictions for later scenes.\"]}],\"preserve_ids_and_mechanics\":true}"
}
