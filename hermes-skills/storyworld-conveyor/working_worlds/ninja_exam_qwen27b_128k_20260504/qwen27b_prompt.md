You are helping design a short SweepWeave storyworld.

Task: create a 20-30 encounter storyworld design packet about passing a hidden-village ninja exam.

Important constraints:
- Do not use copyrighted Naruto names, villages, clans, bijuu, hokage, jutsu names, or canon plot events.
- Capture only the broad genre premise: young ninja candidates, stealth trials, teamwork, rival squads, chakra-like focus discipline, village politics, and a final exam with a secret synthesis route.
- The output is a design packet for a deterministic storyworld generator, not the final JSON.
- Make the exam questions/trials interesting as game design: choices should change variables, reveal character values, and create non-obvious routes to endings.

Return JSON only with these keys:
- title
- design_thesis
- core_variables: array of objects with id and meaning
- cast: array of named original characters with role and pressure
- exam_trial_bank: 12-16 trial ideas
- scene_ladder: 20-24 short scene titles with one-sentence purpose
- secret_route
- option_reaction_idioms: 8 examples of choice/reaction patterns
- balancing_notes

Design target:
- 20-30 encounters total
- 4 options per nonterminal encounter
- 3 reactions per option
- 5-7 endings
- one secret ending that rewards balancing stealth, loyalty, focus, and mercy instead of just maximizing power.
