# Hermes Qwen 27B Packet Storyworld

This folder packages the hackathon demo artifact.

- `hermes_qwen27b_packet_storyworld.json` is the playable SweepWeave storyworld.
- `paper.md` is the short demo paper/note.
- `brief.md` is the one-screen metrics summary.
- `run_summary.json` records validator, quality gate, authoring score, and Monte Carlo commands.
- `encounter_matrix.md` summarizes the authored route structure.

## Results

- Hermes session: `20260503_165110_e159f6`
- Validator: pass
- Strict quality gate: pass
- Authoring score: `0.858900462962963`
- Scale: 10 playable non-terminal encounters, 8 endings, 40 options, 120 reactions, 600 effects.

## Play

Open `C:\projects\GPTStoryworld\storyworld_reader.html` in a browser and drop `hermes_qwen27b_packet_storyworld.json` into the loader.

One route that exposes the secret final option under the current scoring:

1. `The woman's statement...`
2. `The question itself is flawed...`
3. `Fast instead...`
4. `Literal translation...`
5. `Condemning the innocent violates divine justice itself...`
6. `Truth first...`
7. `The people who are judged...`
8. `I will attempt the answer...`
9. `Light the ninth lantern and make the court testify.`

The video point is the architecture, not just this route: Hermes/Qwen 27B supplies the creative packet, while the scaffold supplies schema discipline, p/p2 belief effects, routing, validation, and playable artifact generation.
