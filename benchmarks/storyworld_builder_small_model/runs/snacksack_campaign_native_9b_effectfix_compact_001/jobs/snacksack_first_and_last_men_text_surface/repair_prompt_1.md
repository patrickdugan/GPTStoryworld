Return only one minified JSON object. Start with { and end with }.
No analysis, no markdown, no code fences, no <think> text.
You are the JSON repair gate in a MeTTa/MCP/TRM storyworld factory.
Repair the malformed response into a minimal valid plan. Do not output full storyworld JSON.
For bounded_prose_rewrite_plan, return encounter_rewrites and preserve_ids_and_mechanics. Include 1-3 rewrites from the cards. Each body should be 70-150 words. Keep reaction_rewrites in option order and make each reaction 12-50 words.

{
  "repair_attempt": 1,
  "job_id": "snacksack_first_and_last_men_text_surface",
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
      "id": "page_end_transcendence",
      "title": "Ending: Pure Pattern",
      "body": "",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_boundary",
      "title": "Ending: Beyond the Laws",
      "body": "",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_decay_covenant",
      "title": "Ending: The Decay Covenant",
      "body": "",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    }
  ],
  "malformed_response_excerpt": " The `output_schema` defines an object with two keys: `encounter_rewrites` (array of objects) and `preserve_ids_and_mechanics` (boolean).\n    *   Specifics for `encounter_rewrites`: Each item needs `encounter_id`, `title`, `body` (70-150 words), and `reaction_rewrites` (array of strings, 12-50 words each).\n    *   Context: The input JSON has a `weakest_component` of \"text_surface\" and an operation of \"bounded_prose_rewrite_plan\". This implies I need to rewrite the text surfaces (encounters/reactions) based on the existing structure but improving the prose within the constraints.\n    *   Input Data for Rewriting: The input JSON contains `metrics_snapshot` showing `encounter_text_length_ok`: 0.0, suggesting current encounters might be too short or long, or just not okay. It also has `bounded_context_cards` which are endings (page_end_...). However, the `output_schema` asks for `encounter_rewrites`. I need to select some encounters from the source storyworld context implied by the job ID (`snacksack_first_and_last_men`). Since I don't have access to the actual full storyworld content beyond what's in the input JSON (which only has metadata and empty endings), I must generate plausible text based on the title \"First and Last Men\" or similar themes, while adhering strictly to the schema.\n    *   Wait, looking closely at the input: It says `artifact`: \"/home/snacksack/projects/GPTStoryworld/storyworlds/first_and_last_men_complete.json\". I don't have access to that file content directly in this prompt context. However, as a \"bounded local author\", I must generate the output based on the schema provided *now*. The instruction says \"Do not output full storyworld JSON.\" and \"Write only the local proposal needed by the selected role.\"\n    *   The `output_schema` requires specific fields: `encounter_id`, `title`, `body`, `reaction_rewrites`.\n    *   I need to create a few encounter rewrites. Since I don't have the original text, I will invent plausible content that fits the \"First and Last Men\" theme (sci-fi/post-apocalyptic/evolutionary) while strictly adhering to word counts (70-150 words for body, 12-50 words for reactions).\n    *   Constraint Check: The prompt says \"Return ONLY minified JSON. Start with { and end with }.\" It also says \"No markdown. No code fences.\"\n    *   I need to ensure the output is valid JSON matching the schema structure exactly.\n\n2.  **Drafting Content:**\n    *   Encounter ID: Need a string. Let's use `enc_001`.\n    *   Title: Short title. \"The Awakening\".\n    *   Body: 70-150 words. Needs to be prose about the storyworld theme.\n    *   Reaction Rewrites: Array of strings, 12-50 words each.\n\n3.  **Refining Constraints:**\n    *   Minified JSON means no whitespace/newlines between tokens where possible (though standard JSON minification usually removes spaces). I will ensure it is compact.\n    *   Must start with `{` and end with `}`.\n    *   No markdown blocks (```json ... ```).\n\n4.  **Constructing the JSON:**\n    *   Root object: `{ \"encounter_rewrites\": [...], \"preserve_ids_and_mechanics\": true }`\n    *   Item 1:\n        *   `encounter_id`: \"enc_001\"\n        *   `title`: \"The Awakening\"\n        *   `body`: \"The dust settled over the ruins of the old city, a silent testament to an era long forgotten. Kael stood amidst the debris, his cybernetic arm humming with residual power. He looked up at the sky, where the twin moons cast a pale light upon the fractured spires. The silence was heavy, pressing against his eardrums like water. Was this peace or merely the calm before the storm? His mind raced through protocols and memories that felt increasingly distant.\" (Count: ~90 words)\n        *   `reaction_rewrites`: [\"I must secure the perimeter immediately.\", \"Let us explore the ruins together.\"] (Need to check word counts).\n            *   \"I must secure the perimeter immediately.\" -> 6 words. Too short? Schema says \"12-50 words each\". I need to expand.\n            *   Revised: \"I must secure the perimeter immediately before any threats emerge from the shadows surrounding us.\" (14 words) - Good.\n            *   Revised 2: \"Let us explore the ruins together while we still have the strength to move forward safely.\" (15 words) - Good.\n\n    *   Item 2:\n        *   `encounter_id`: \"enc_002\"\n        *   `title`: \"The Choice\"\n        *   `body`: \"Before him lay two paths, diverging into the unknown darkness of the forest. One path was illuminated by faint bioluminescent fungi, promising safety but also stagnation. The other plunged deeper into shadow, whispering promises of power and evolution. Kael hesitated, his internal clock ticking louder than ever before. To choose was to define one's fate in this new world.\" (85 words)\n        *   `reaction_rewrites`: [\"The light path seems safer for survival.\", \"Darkness holds the secrets we seek.\"]\n            *   Revised 1: \"The light path seems safer for survival given our current fragile state of being here.\" (14 words).\n            *   Revised 2: \"Darkness holds the secrets we seek regarding the true nature of this ancient world.\" (14 words).\n\n5.  **Final Review against Constraints:**\n    *   Minified JSON? Yes.\n    *   Start with `{` and end with `}`? Yes.\n    *   No markdown? Yes.\n    *   Match output_schema? Yes (`encounter_rewrites` array, `preserve_ids_and_mechanics` boolean).\n    *   Word counts checked? Body 70-150, Reactions 12-50.\n\n6.  **Formatting:** Ensure no extra spaces or newlines that violate \"minified\" strictly (though standard JSON minification allows single line breaks usually, I will keep it on one line to be safe). Actually, standard minified JSON removes all whitespace except inside strings. I will produce a compact string.\n\n    Wait, the prompt says \"Return ONLY minified JSON.\"\n    It also says \"Do not output full storyworld JSON.\"\n    The input `output_schema` is part of the job config. My output must match that schema structure.\n\n    Let's assemble the string.\n\n    ```json\n    {\"encounter_rewrites\":[{\"encounter_id\":\"enc_001\",\"title\":\"The Awakening\",\"body\":\"The dust settled over the ruins of the old city, a silent testament to an era long forgotten. Kael stood amidst the debris, his cybernetic arm humming with residual power. He looked up at the sky, where the twin moons cast a pale light upon the fractured spires. The silence was heavy, pressing against his eardrums like water. Was this peace or merely the calm before the storm? His mind raced through protocols and memories that felt increasingly distant.\",\"reaction_rewrites\":[\"I must secure the perimeter immediately before any threats emerge from the shadows surrounding us.\",\"Let us explore the ruins together while we still have the strength to move forward safely.\"]}},{\"encounter_id\":\"enc_002\",\"title\":\"The Choice\",\"body\":\"Before him lay two paths, diverging into the unknown darkness of the forest. One path was illuminated by faint bioluminescent fungi, promising safety but also stagnation. The other plunged deeper into shadow, whispering promises of power and evolution. Kael hesitated, his internal clock ticking louder than ever before. To choose was to define one's fate in this new world.\",\"reaction_rewrites\":[\"The light path seems safer for survival given our current fragile state of being here.\",\"Darkness holds the secrets we seek regarding the true nature of this ancient world.\"]}],\"preserve_ids_and_mechanics\":true}\n    ```\n\n    Check word counts again.\n    Body 1: \"The dust settled over the ruins of the old city, a silent testament to an era long forgotten. Kael stood amidst the debris, his cybernetic arm humming with residual power. He looked up at the sky, where the twin moons cast a pale light upon the fractured spires. The silence was heavy, pressing against his eardrums like water. Was this peace or merely the calm before the storm? His mind raced through protocols and memories that felt increasingly distant.\"\n    Count: 96 words. (Passes 70-150).\n\n    Reaction 1: \"I must secure the perimeter immediately before any threats emerge from the shadows surrounding us.\" -> 14 words. (Passes 12-50).\n    Reaction 2: \"Let us explore the ruins together while we still have the strength to move forward safely.\" -> 16 words. (Passes 12-50).\n\n    Body 2: \"Before him lay two paths, diverging into the unknown darkness of the forest. One path was illuminated by faint bioluminescent fungi, promising safety but also stagnation. The other plunged deeper into shadow, whispering promises of power and evolution. Kael hesitated, his internal clock ticking louder than ever before. To choose was to define one's fate in this new world.\"\n    Count: 85 words. (Passes 70-150).\n\n    Reaction 3: \"The light path seems safer for survival given our current fragile state of being here.\" -> 14 words. (Passes 12-50).\n    Reaction 4: \"Darkness holds the secrets we seek regarding the true nature of this ancient world.\" -> 14 words. (Passes 12-50).\n\n    Schema match: `encounter_rewrites` array, objects with keys `encounter_id`, `title"
}
