# The Two Balconies of Sana'a

Playable storyworld generated from five Hermes/Qwen 27B packet chunks, then materialized through the MeTTa/TRM-style storyworld scaffold.

## Results

- Prompt: `Romeo and Juliet set in Sana'a between a Sunni boy and a Shia girl`
- Playable non-terminal encounters: 40
- Endings: 8
- Options/reactions/effects: 135 / 405 / 2025
- Validator: pass
- Strict quality gate: pass
- Authoring score: `0.8711246141975308`
- Secret ending Monte Carlo rate: `10.3%`

## Files

- `hermes_qwen27b_packet_storyworld.json`: playable SweepWeave storyworld.
- `paper.md`: short demo note.
- `brief.md`: metrics summary.
- `run_summary.json`: command receipts and metrics.
- `encounter_matrix.md`: route/scene matrix.

## Play

Open `C:\projects\GPTStoryworld\storyworld_reader.html` in a browser and drop in `hermes_qwen27b_packet_storyworld.json`.

One route to the secret ending prioritizes witness/disclosure/mercy choices, then at the final lattice choose:

`Find the hidden route by making the families and the court testify about their own role.`

Then choose:

`Make every authority name what it feared love would expose.`
