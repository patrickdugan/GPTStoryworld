# Murder-Mystery Storyworld Builder Compare - 2026-05-04

Run directory:

- `benchmarks/storyworld_builder_small_model/runs/murder_mystery_compare_20260504_001`

Randomly selected source:

- `storyworlds/2-27-2026-spooltight-batch-v1/if_institutional_deadlock_mediator_line_v1.json`
- Title in artifact: `First and Last Men: Escape from the Solar Cul-de-sac`

## Conditions

| Condition | Model path | Harness |
|---|---|---|
| `9b_direct` | `Qwen_Qwen3.5-9B-Q4_K_M.gguf` | Direct OpenAI-compatible call, 6000-token output cap. |
| `9b_direct_long` | `Qwen_Qwen3.5-9B-Q4_K_M.gguf` | Direct OpenAI-compatible call, 12000-token output cap. |
| `27b_hermes_skill` | `Qwen3.5-27B.Q4_K_M.gguf` | Hermes one-shot with `storyworld-conveyor-runner,metta-trm-storyworld-balancer`. |

## Results

| Condition | Blueprint Extract | Validator | Builder Score | Blueprint Contract | Source Characters | Encounters | Endings |
|---|---:|---:|---:|---:|---:|---:|---:|
| `9b_direct` | partial only | `VALID OK` | `0.7575` | `0.0000` | `0` | `0` | `0` |
| `9b_direct_long` | full | `VALID OK` | `0.7727` | `0.9444` | `3` | `15` | `5` |
| `27b_hermes_skill` | full | `VALID OK` | `0.7819` | `0.9907` | `3` | `11` | `5` |

## Qualitative Notes

The short 9B run began a plausible blueprint but truncated before closing the JSON, so the materializer had to fall back. With a larger output budget, 9B produced a complete murder-mystery design: `Deadlock at the Solar Table`, with The Counter Archivist as detective, The Mediator as victim, and Civilization as culprit. It met most of the contract but used only two suspects, one of which was an invented `The New Men` role derived from the source.

Hermes 27B produced `The Mediator's Ledger`, with stronger murder-mystery casting: The Mediator as detective, Civilization as victim, The Institutional Steward as culprit, and four suspects. It still emitted reasoning/markdown before JSON, but the blueprint object was complete enough for extraction and materialization.

## Skill-Design Implication

The current structural scorecard mostly measures whether the deterministic materializer can make valid storyworld JSON, so it under-differentiates the actual blueprint quality. The better benchmark signal is the pre-materialization blueprint contract score plus qualitative checks for suspect web, source-character use, ending coverage, and secret-ending logic.

For 9B, the next skill improvement should not be a bigger one-shot prompt. It should be staged MCP generation:

- Stage 1: cast/victim/culprit/suspect web.
- Stage 2: clue-variable map and secret-ending threshold.
- Stage 3: bounded encounter cards, 3-4 at a time.
- Stage 4: deterministic materialization and verifier repair.

For Hermes 27B, the skill should suppress reasoning text less by prompt alone and more by extraction/repair gates, because even the stronger model ignored the JSON-only contract but delivered better design content.
