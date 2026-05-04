Return only one minified JSON object. Start with { and end with }.
No analysis, no markdown, no code fences, no <think> text.
You are the JSON repair gate in a MeTTa/MCP/TRM storyworld factory.
Repair the malformed response into a minimal valid plan. Do not output full storyworld JSON.
For bounded_prose_rewrite_plan, return encounter_rewrites and preserve_ids_and_mechanics. Include 1-3 rewrites from the cards. Each body should be 70-150 words. Keep reaction_rewrites in option order and make each reaction 12-50 words.

{
  "repair_attempt": 1,
  "job_id": "snacksack_macbeth_validated_text_surface",
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
      "id": "page_end_0123",
      "title": "Ending: The Canmore Settlement",
      "body": "Dunfermline, Benedictine influence, new names, and new loyalties all point to a kingdom that is no longer simply Alba of the old chronicles. The house changes, the language changes, and the realm survives by changing with them.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_0122",
      "title": "Ending: The Ashes of Dunsinane",
      "body": "The crown passes through smoke and grief, and Lulach''s brief coronation cannot stop the return of Malcolm. The story ends in dynastic loss, but it also records how much history had to happen before Malcolm could inherit it.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_end_0121",
      "title": "Ending: The Roman Pilgrimage",
      "body": "The kingdom does not escape violence, but it does escape the cheap version of history that reduces Macbeth to a single murderous night. Alba remains a political kingdom with a ruler who understood that legitimacy had to be built in more than one register.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_secret_0299",
      "title": "Super Secret Ending: The Inverted Heath",
      "body": "The heath has become a chamber inside the kingdom, and the kingdom a chamber inside the prophecy. Macbeth sees that rule was never only blood and law; it was also the shape of the place that held them. In this inversion, Alba does not simply fall into history. It answers the witches and becomes the riddle that outlives the throne.",
      "option_count": 0,
      "reaction_count": 0,
      "effect_operators": [],
      "sample_options": []
    },
    {
      "id": "page_0004",
      "title": "Act II: Crinan's Rising",
      "body": "The uprising is personal, dynastic, and short. It proves that the old king's family still has reach, but not enough force to dislodge Macbeth once the new regime has hardened around him.",
      "option_count": 3,
      "reaction_count": 7,
      "effect_operators": [
        "to"
      ],
      "sample_options": [
        {
          "id": "opt_page_0004_0",
          "text": "Crush the revolt quickly and make the cost unmistakable. The court, the road, and the archive all remember it.",
          "reaction_count": 2,
          "sample_reactions": [
            "The rebellion dies fast enough to remind the court that Macbeth is not merely holding the throne; he is willing to defend it. The next claim will remember it. In Alba, the record outlives the moment.",
            "Crinan''s death turns private grievance into dynastic warning. The court will count the cost later. In Alba, the record outlives the moment."
          ]
        },
        {
          "id": "opt_page_0004_1",
          "text": "Offer terms to the old house and risk looking weak. The court, the road, and the archive all remember it.",
          "reaction_count": 3,
          "sample_reactions": [
            "Mercy might quiet one feud, but it also tells every claimant that the kingdom can be tested. The next claim will remember it. In Alba, the record outlives the moment.",
            "A generous king is only safe if his generosity is read as strength. The court will count the cost later. In Alba, the record outlives the moment."
          ]
        },
        {
          "id": "page_0004_v2_opt3",
          "text": "Turn the uprising into proof that Macbeth is defending Alba rather than merely taking it. The court, the road, and the archive all remember it.",
          "reaction_count": 2,
          "sample_reactions": [
            "The king''s defenders now have a cleaner story to tell: Macbeth is the ruler who kept Alba intact when the old house fractured. The next claim will remember it. In Alba, the record outlives the moment.",
            "Even the opposition has to admit that the revolt made the crown look more necessary, not less. The court will count the cost later. In Alba, the record outlives the moment."
          ]
        }
      ]
    }
  ],
  "malformed_response_excerpt": "s).\nLet's try: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\" (51 words).\nWait, I need 70-150.\n\"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\" (51 words).\nLet's expand: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\" (51 words).\nOkay, I will write a longer one: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\" (51 words).\nI need 70 minimum.\n\"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\" (51 words).\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nLet's add: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nI will write: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\"\nOkay: \"The uprising is deeply personal, dynastic, and remarkably short-lived in its impact on the wider realm. It proves that the old king's family still has political reach, yet lacks sufficient force to dislodge Macbeth once the new regime has fully hardened around him with iron resolve and military backing from the south.\""
}
