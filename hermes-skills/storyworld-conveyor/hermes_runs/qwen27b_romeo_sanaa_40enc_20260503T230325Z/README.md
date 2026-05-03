# Hermes Qwen 27B Romeo/Sana'a 40-Encounter Run

Remote host: `snacksack`

Model: `Qwen3.5-27B.Q4_K_M.gguf`

Source prompt: `Romeo and Juliet set in Sana'a between a Sunni boy and a Shia girl`

## Successful Sessions

- Chunk 1: `20260503_170510_b21881`
- Chunk 2 retry: `20260503_172340_367742`
- Chunk 3: `20260503_170928_7eb5de`
- Chunk 4: `20260503_171240_a3d688`
- Chunk 5: `20260503_171508_4ff12f`

Chunk 2 was rerun with a stricter compact schema after the first pass ended incomplete. The committed packet uses the retry output.

## Contents

- `prompt_chunk_01.txt`, `prompt_chunk_02_retry.txt`, `prompt_chunk_03.txt`, `prompt_chunk_04.txt`, `prompt_chunk_05.txt`: prompts sent to Hermes.
- `transcript_chunk_*.clean.txt`: readable Hermes logs.
- `session_export_chunk_*.jsonl`: Hermes session exports.
- `packet_chunk_*.json`: extracted Qwen-authored packets.
- `combined_packet.json`: 38 Qwen-authored scene cards combined into one packet.

The materialized playable artifact is in:
`../../working_worlds/romeo_sanaa_qwen27b_40enc/hermes_qwen27b_packet_storyworld.json`
