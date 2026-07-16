# Activation capture contract

This contract lets a distributed inference stack produce artifacts accepted by
`scripts/analyze_activations.py` without using the reference Transformers loader.

## Prefill unit

For every record in `dataset/stories.jsonl`, construct six cumulative prefixes by
joining revealed sentences with one ASCII space. Use raw text with the target
tokenizer's ordinary special-token behavior. Do not apply a chat template, append
a question, decode a response, or capture generated reasoning.

At each prefix, capture the residual state at:

1. the embedding output;
2. the output of every transformer block.

The primary state is the last input-token vector. The robustness state is the
arithmetic mean of the last `min(4, sequence_length)` input-token vectors. Tensor-
parallel shards must be gathered into the canonical hidden dimension exactly
once; duplicated or partial shards are invalid.

## Record files

Write one compressed NPZ per story with no object arrays:

```text
hidden_states            float16/float32 [6, layers_including_embedding, hidden]
tail_mean_hidden_states  float16/float32 [6, layers_including_embedding, hidden]
sentence_indices         int16           [6]  values 1..6
token_counts             int32           [6]
last_token_ids           int32           [6]
```

## Manifest

Write `capture_manifest.json` with schema version
`moral_hysteresis_capture_manifest_v1`. It must contain:

- dataset `stories_sha256` and `story_count`;
- model ID, requested immutable revision, resolved revision, config hash,
  architecture, tokenizer, and whether remote code was trusted;
- capture backend, extraction point, layer count, hidden size, storage dtype,
  tail-token count, seed, and raw-text/no-chat-template declaration;
- software and hardware versions;
- one record per checked story with story ID, relative path, SHA-256, shape, dtype,
  and token counts;
- publication gates confirming revision pinning, full primary capture, and full
  tail-mean capture.

The checked analyzer validates dataset coverage, safe relative paths, every file
hash, and uniform shapes. External infrastructure should first validate a small
checkpoint against `harvest_activations.py` to establish tensor-point parity,
using maximum absolute error and cosine similarity thresholds fixed before the
frontier run.

## Frontier limitation

Goodfire's published Kimi K2 Thinking work used a patched high-performance
inference server. That patch is not included here. A normal text-generation API
cannot emit a conforming artifact because it does not expose internal states.
