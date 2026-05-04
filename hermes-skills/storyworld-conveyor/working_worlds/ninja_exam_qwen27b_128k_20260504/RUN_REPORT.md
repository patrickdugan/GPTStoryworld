# Qwen 27B 128k Ninja Exam Probe

## Purpose

Configure Qwen3.5-27B Q4 on Snacksack with a 128k context window and compare its behavior on the same hidden-village ninja exam storyworld design prompt used for the 9B run.

## Server Configuration

Endpoint:

- Local tunnel: `http://127.0.0.1:8083`
- Remote port: `snacksack:8083`
- Model alias: `Qwen3.5-27B-128K.Q4_K_M.gguf`
- Model path: `/home/snacksack/Qwopus_v2/models/Qwen3.5-27B.Q4_K_M.gguf`

Launch command:

```bash
/home/snacksack/llama-b8645/llama-server \
  -m /home/snacksack/Qwopus_v2/models/Qwen3.5-27B.Q4_K_M.gguf \
  --alias Qwen3.5-27B-128K.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8083 \
  -ngl 999 \
  -c 131072 \
  --threads 8 \
  --batch-size 512 \
  --ubatch-size 128 \
  --flash-attn on \
  -ctk q4_0 \
  -ctv q4_0 \
  --reasoning off \
  --reasoning-budget 0
```

Load result from llama.cpp log:

- `n_ctx = 131072`
- `n_ctx_train = 262144`
- `n_embd = 5120`
- `n_params = 26895998464`
- quantized CPU KV cache: `2304 MiB`
- recurrent state buffer: `598.5 MiB`
- model process RSS after load/run: about `30.0 GB`
- observed GPU memory: `363 MiB`

Important: despite `-ngl 999`, this build/run did not materially occupy VRAM. The run is CPU/RAM resident, so it is safe for VRAM but slow.

## Design Prompt Run

Prompt: `qwen27b_prompt.md`
Request JSON: `qwen27b_request.json`
Response: `qwen27b_design_packet.json`

Recorded timing:

- Prompt tokens: `330`
- Completion tokens: `900`
- Total tokens: `1230`
- Prompt eval: `20552.85 ms`, `16.06 tok/s`
- Generation: `545545.492 ms`, `1.65 tok/s`
- Total model time: `566098.34 ms`
- Wall time: about `567.7 s`
- Finish reason: `length`

## Qualitative Result

The 27B design packet is coherent and on-task:

- title: `Shadows of the Silent Peak`
- thesis: stealth, teamwork, moral choices, loyalty, sacrifice, compassion
- variables: `stealth_level`, `team_cohesion`, `focus_discipline`, `reputation`, `mercy_score`
- cast: Kaelen, Lira, Master Torin, Sera, Jiro
- trials: Whispering Forest, Bridge of Reflections, Shadow Duel, Silent Vault, Echo Chamber, Falling Star, Mirror Maze, Hidden Path, Trial of Bonds, etc.

It is slightly more conventionally structured than the 9B packet and better at using the requested key names. However, it still wrapped the answer in a markdown code fence and hit the token cap before finishing the full JSON. For this specific design-packet task, 27B at 128k did not show enough quality lift to justify the much slower throughput.

## Comparison To 9B Ninja Run

The 9B run generated at about `4.90 tok/s` and produced a usable but truncated design packet. The 27B 128k run generated at about `1.65 tok/s` and also truncated at the same output cap. The main difference is not storyworld capability yet; it is context capacity and slower decoding.

Current conclusion:

- 128k config works.
- It is CPU/RAM resident, not a fast 3090 VRAM run.
- It can support much larger MCP/storyworld prompts than the 9B 8k endpoint.
- For short design packets, it is not worth using over 9B unless we need deeper context or better prose after the deterministic conveyor has already narrowed the task.

Next useful test:

- Feed a 10k-30k token MCP packet containing the current storyworld, Hilbert overexposure diagnosis, quality metrics, and selected encounter text.
- Ask 27B for targeted secret-gate repair proposals only.
- Compare whether the larger active context improves repair quality enough to offset the `1.65 tok/s` generation speed.
