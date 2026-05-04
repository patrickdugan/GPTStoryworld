# MCP Retrieval TRM Curriculum

Purpose: train storyworld control-plane TRMs to pull bounded MCP context before LLM authoring stages.

This corpus was generated from a murder-mystery storyworld comparison where direct 9B generation, long-output 9B generation, and Hermes 27B skill generation were compared on the same random source adaptation.

## Outputs

- `mcp_cards.jsonl`: retrieval cards that can live behind an MCP server or file-backed memory.
- `mcp_index.json`: card-id keyed lookup table for file-backed MCP adapters.
- `retrieval_rows.jsonl`: `state/tools/action/target/meta` rows for TRM routing.
- `sft_messages.jsonl`: chat-shaped distillation rows.
- `train.jsonl` / `val.jsonl`: deterministic split of retrieval rows.
- `mcp_retrieval_facts.metta`: symbolic facts connecting stages, roles, cards, and actions.
- `train_manifest.json`: capped-training handoff; actual training must run under resource caps.

## Key Claim

The LLM should not be responsible for remembering the entire source, contract, run history, and validator behavior. A small control TRM can learn to retrieve the specific MCP cards needed for each stage, then hand a compact packet to the LLM.

## Manifest

```json
{
  "created_at": "2026-05-04T15:06:57Z",
  "run_dir": "C:\\projects\\GPTStoryworld\\benchmarks\\storyworld_builder_small_model\\runs\\murder_mystery_compare_20260504_001",
  "rows": 9,
  "train_rows": 7,
  "val_rows": 2,
  "mcp_cards": 14,
  "estimated_tokens": 6446,
  "resource_caps_required": {
    "ram_mb": 2048,
    "cpu_pct": 50,
    "io_mb_s": 50
  },
  "checkpoint_interval": "100 steps or 120 seconds",
  "chunk_strategy": "row-level shuffled minibatches; no whole-corpus tensor materialization",
  "status": "corpus_only_not_trained",
  "outputs": {
    "mcp_cards": "C:\\projects\\GPTStoryworld\\hermes-skills\\storyworld-conveyor\\trm_corpus\\mcp_retrieval_storyworld_murder_001\\mcp_cards.jsonl",
    "retrieval_rows": "C:\\projects\\GPTStoryworld\\hermes-skills\\storyworld-conveyor\\trm_corpus\\mcp_retrieval_storyworld_murder_001\\retrieval_rows.jsonl",
    "sft_messages": "C:\\projects\\GPTStoryworld\\hermes-skills\\storyworld-conveyor\\trm_corpus\\mcp_retrieval_storyworld_murder_001\\sft_messages.jsonl",
    "train": "C:\\projects\\GPTStoryworld\\hermes-skills\\storyworld-conveyor\\trm_corpus\\mcp_retrieval_storyworld_murder_001\\train.jsonl",
    "val": "C:\\projects\\GPTStoryworld\\hermes-skills\\storyworld-conveyor\\trm_corpus\\mcp_retrieval_storyworld_murder_001\\val.jsonl",
    "metta": "C:\\projects\\GPTStoryworld\\hermes-skills\\storyworld-conveyor\\trm_corpus\\mcp_retrieval_storyworld_murder_001\\mcp_retrieval_facts.metta"
  }
}
```
