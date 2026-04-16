# Hermes Storyworld Index-Routing Skill (3090/Qwen)

This skill manages the training and deployment of Tesseract Routing Models (TRMs) used for context-efficient storyworld index lookups on 24GB VRAM hardware.

## Stack Overview
- **VRAM Budget:** 24GB (RTX 3090)
- **Primary Model:** Qwen 2.5 27B-32B (GGUF K_M ~16.15GB)
- **TRM Router:** Qwen 2.5 1.5B or 3B (QLoRA Adapter)
- **Context Budget:** 16k-20k tokens (~4-5GB VRAM)
- **Framework:** FastMCP (Python) + `storyworld-conveyor`

## TRM Index-Routing Workflow

### 1. Data Collection (Context Sharding)
Generate training examples where the "ground truth" is a specific tool call to the lore index.
```powershell
# Windows PowerShell
powershell -File hermes-skills/storyworld-conveyor/scripts/train_trm_3090_full.ps1 `
  -WorldJson storyworlds/charter_of_ashen_aegis.json `
  -OutputDir hermes-skills/pure-trm-trainer/runs/index_routing_v1
```

### 2. TRM Training (QLoRA)
The PowerShell script above runs both corpus generation and 3090-optimized training. If you want to run the training stage separately with 16k context:
```bash
python hermes-skills/storyworld-conveyor/scripts/train_qlora_3090.py \
  --model-name Qwen/Qwen2.5-1.5B-Instruct \
  --data-path hermes-skills/pure-trm-trainer/runs/index_routing_v1/train.jsonl \
  --output-dir hermes-skills/pure-trm-trainer/runs/index_routing_v1/adapter \
  --max-length 16384
```

### 3. Execution Loop
1. **TRM Call:** Input (Query + State) -> Output (Tool Action)
2. **MCP Action:** Execute `query_lore_index(namespace, query)`
3. **LLM Reasoning:** Inject *only* the retrieved shard into the 27B/32B context window.

## Resource Optimization (3090 Safe Caps)
- **`n_ctx`:** 16384 (Safe 4GB KV Cache)
- **`n_gpu_layers`:** Max (Offload all layers to VRAM)
- **`n_batch`:** 512
- **`kv_cache_type`:** `f16` or `q4_0` (if more context is needed)

## Canonical Tools
- `storyworld_mcp_server.py`: The FastMCP surface.
- `run_storyworld_conveyor.py`: The orchestrator for batch processing.
- `trm-router`: (via `trm-router-pipeline` skill) for mechanistic augmentation.

## Deployment Command
```bash
# Start the MCP server in background
python hermes-skills/storyworld-conveyor/scripts/storyworld_mcp_server.py
```
