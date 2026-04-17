# Wiki Card Router Bench

This benchmark is a small frozen slice for testing the claim that a tiny model can recover factual QA accuracy under a tight context budget by routing over externalized knowledge cards instead of relying on closed-book recall or naive context stuffing.

It is intentionally small and auditable. The goal is not leaderboard scale. The goal is a clean systems comparison under constrained VRAM and prompt budget.

## Conditions

The benchmark runner compares three conditions:

1. `closed_book`
   - question only
   - no external evidence
2. `stuffed`
   - lexical top-k retrieval
   - multiple cards stuffed into one answer prompt
3. `mcp_routed`
   - model chooses a tool call over a short candidate list
   - only a targeted card or relation card is injected into the answer prompt

## MCP index shape

The router now sees a small namespace-aware MCP surface instead of one flat lexical index:

- `aliases`
  - title and alias surface forms that nominate entity ids
- `entities`
  - entity cards for questions whose answer is the entity itself
- `relations`
  - relation cards for questions whose answer is a fact value
- `control`
  - `ctl::escalate` fallback when the candidate actions are insufficient

The benchmark still scores the same final outcomes, but the routed condition is now trainable as an explicit `action_id` selection problem.

## Hardware motivation

This slice is designed for the exact situation where a 2B model can fit on a 4 GB VRAM card in 4-bit quantization, but full-context prompting is still severely limited by KV-cache and runtime overhead.

That makes it a useful test of:

- same model
- same hardware
- same small context budget
- different memory architecture

## Files

- `cards.jsonl`
  - frozen evidence cards
- `questions.jsonl`
  - benchmark questions, answers, and expected routes

## Suggested usage

Heuristic smoke:

```powershell
python C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\scripts\run_wiki_card_routerbench.py --backend heuristic
```

2B local model path:

```powershell
python C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\scripts\run_wiki_card_routerbench.py `
  --backend hf `
  --model-path D:\Research_Engine\models\Qwen3.5\Qwen3.5-2B-HF `
  --load-in-4bit
```

Named bench launcher:

```powershell
python C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\scripts\run_trm_bench.py --bench wiki-card-routerbench --backend heuristic
```

Router corpus build:

```powershell
python C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\scripts\build_wiki_card_router_corpus.py `
  --source C:\projects\GPTStoryworld\benchmarks\wiki_card_routerbench\questions.jsonl `
  --out C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\runs\wiki_card_router_train_qwen2b\router_messages.jsonl
```

Router training dry-run:

```powershell
python C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\scripts\run_trm_trainer_hermes.py `
  --config C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\references\wiki-card-router-training-spec.json `
  --dry-run
```

Safe capped launcher dry-run:

```powershell
powershell -ExecutionPolicy Bypass -File C:\projects\GPTStoryworld\hermes-skills\pure-trm-trainer\scripts\run_wiki_card_router_train_capped.ps1 -DryRun
```

## Notes

- This is a first scaffold, not a final paper benchmark.
- The corpus is deliberately small so routing failures are easy to inspect.
- The next optimization step is scaling the same namespace schema to a larger frozen corpus with held-out question sets and explicit token-budget accounting.
- The interrupted local QLoRA run still produced a usable `checkpoint-10`; on the fixed 13-question slice it reached `mcp_routed_accuracy = 0.923` with `closed_book_accuracy = 0.692`.
- Use the capped launcher for any follow-on training on the 4 GB laptop GPU. It applies a Windows Job Object RAM/CPU cap and emits JSONL/JSON run telemetry instead of letting the trainer run unmanaged.
