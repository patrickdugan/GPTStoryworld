# Hermes Storyworld 3090 Skill

Optimized for 24GB VRAM (3090) and Qwen 2.5 27B-32B class models.

## Mandates
- **Context Hard Cap:** 16,384 tokens (unless KV quantization is enabled).
- **Index Priority:** Never feed full world bibles to the 27B model. Use the TRM to fetch only the relevant "cards."
- **Model Parameters:** Q5_K_M GGUF is the preferred balance of quality and VRAM.

## Operational Workflow
1. **Routing Phase:** Small TRM (1.5B) analyzes the query and current state.
2. **Retrieval Action:** TRM calls `query_lore_index` or `get_encounter_card`.
3. **Context Injection:** MCP Server fetches the specific shard.
4. **Generation Phase:** 27B model receives a prompt containing <1,000 tokens of context.

## Local Qwen 3090 Launch Script (llama.cpp)
```bash
./llama-server \
  -m models/qwen2.5-32b-instruct-q5_k_m.gguf \
  -c 16384 \
  --n-gpu-layers 100 \
  --ctk f16 \
  --host 0.0.0.0 \
  --port 8080
```
