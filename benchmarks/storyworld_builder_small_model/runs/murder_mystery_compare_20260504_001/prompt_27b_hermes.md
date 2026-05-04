Return only one JSON object. Do not use markdown, code fences, or analysis.
Mode: Hermes skill run.
Task: create a murder-mystery storyworld blueprint involving characters from the randomly selected adaptation below.
Do not output full SweepWeave JSON. Output the blueprint schema only; deterministic tools will materialize it.
The storyworld should support investigation, competing alibis, clue deltas, 12 playable encounters, 5 endings, and one secret ending.
Use the source characters by name, but adapt their social dynamics into a murder mystery.
Every encounter must have 3 options. Each option should include a reaction and variable deltas.
The secret ending should require questioning the obvious culprit frame rather than merely collecting the most evidence.

Blueprint schema:
{
  "title": "short murder-mystery storyworld title",
  "premise": "80-140 word premise",
  "detective": "character name from source",
  "victim": "character name from source",
  "culprit": "character name from source",
  "suspects": [
    {
      "name": "character name from source",
      "motive": "one sentence",
      "alibi": "one sentence",
      "secret": "one sentence"
    }
  ],
  "clue_variables": [
    "Suspicion",
    "Evidence",
    "Alibi_Strength",
    "Trust",
    "Danger",
    "Secret_Knowledge"
  ],
  "encounters": [
    {
      "title": "scene title",
      "body": "70-150 words",
      "options": [
        {
          "text": "player choice",
          "reaction": "12-50 words",
          "delta": {
            "Evidence": 0.1,
            "Suspicion": -0.05
          }
        }
      ]
    }
  ],
  "endings": [
    {
      "title": "ending title",
      "body": "45-100 words",
      "gate": "what player has learned or failed to learn"
    }
  ],
  "secret_ending": {
    "title": "secret ending title",
    "body": "45-100 words",
    "threshold_logic": "non-obvious synthesis condition"
  }
}

Selected adaptation context:
{
  "seed": 1777898498,
  "source_path": "storyworlds/2-27-2026-spooltight-batch-v1/if_institutional_deadlock_mediator_line_v1.json",
  "source_title": "First and Last Men: Escape from the Solar Cul-de-sac",
  "about": "Institutional deadlock forces a mediator faction to broker power while influence remains a conserved pool.",
  "characters": [
    {
      "id": "char_civ",
      "name": "Civilization",
      "description": "None"
    },
    {
      "id": "char_counter_archivist",
      "name": "The Counter Archivist",
      "description": "A patient anti-institution that keeps a mirror-ledger of power: it cancels quiet influence with evidence, leaks, and paradox-proof memory."
    },
    {
      "id": "char_mediator",
      "name": "The Mediator",
      "description": "A broker of uneasy settlements who tracks public sentiment and timing windows."
    }
  ],
  "sample_scenes": [
    {
      "id": "page_0000",
      "title": "Phase 1: The New Men (Thesis)",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0000 binds storyworld to artistry, recording a unique causal trace for downs",
      "option_count": 3
    },
    {
      "id": "page_0001",
      "title": "Phase 1: The New Men (Pressure)",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0001 binds artistry to storyworld, recording a unique causal trace for downs",
      "option_count": 3
    },
    {
      "id": "page_0002",
      "title": "Phase 1: The New Men (Morph)",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0002 binds storyworld to artistry, recording a unique causal trace for downs",
      "option_count": 3
    },
    {
      "id": "page_0003",
      "title": "Phase 1: The Escape Vector",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0003 binds artistry to storyworld, recording a unique causal trace for downs",
      "option_count": 3
    },
    {
      "id": "page_0004",
      "title": "Phase 1: The Counter Archivist Moves",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0004 binds storyworld to artistry, recording a unique causal trace for downs",
      "option_count": 3
    },
    {
      "id": "page_0005",
      "title": "Phase 1: The Relic That Survives",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0005 binds artistry to storyworld, recording a unique causal trace for downs",
      "option_count": 3
    },
    {
      "id": "page_0006",
      "title": "Phase 2: The New Men (Thesis)",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0006 binds storyworld to artistry, recording a unique causal trace for downs",
      "option_count": 3
    },
    {
      "id": "page_0007",
      "title": "Phase 2: The New Men (Pressure)",
      "body": "{'script_element_type': 'Pointer', 'pointer_type': 'String Constant', 'value': 'Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; every institutional move recasts trust, resentment, and the archive of prior catastrophes. Scene marker page_0007 binds artistry to storyworld, recording a unique causal trace for downs",
      "option_count": 3
    }
  ]
}
