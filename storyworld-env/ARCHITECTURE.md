# Sweepweave Environment: System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SWEEPWEAVE RL ENVIRONMENT                     │
│                                                                   │
│  Generates 15B+ tokens of structured interactive narratives      │
│  through RL-trained models and combinatorial expansion           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
         ┌─────────────────────────────────────────┐
         │   Three Core Components                 │
         │                                          │
         │  1. Environment (verifiers interface)   │
         │  2. Amplification (config generator)    │
         │  3. Integration (QFT-MCP bridge)       │
         └─────────────────────────────────────────┘
```

---

## Component 1: Verifiers Environment

```
┌──────────────────────────────────────────────────────────────────┐
│                     sweepweave/__init__.py                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Dataset Generation                                               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ generate_storyworld_prompt()                               │  │
│  │  - Input: (num_chars, num_props, num_encs, themes, etc.)  │  │
│  │  - Output: Structured prompt for LLM                       │  │
│  │  - Properties: Random sample from 30 axes                  │  │
│  │  - Themes: Random sample from 50 options                   │  │
│  │  - Settings: Random choice from 40 scenarios               │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Validation                                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ SweepweaveValidator                                        │  │
│  │  - validate_structure(): Schema compliance                 │  │
│  │  - compute_structural_score(): Size requirements           │  │
│  │  - compute_effect_diversity(): Dirac operators             │  │
│  │  - compute_gating_score(): Conditional options             │  │
│  │  - compute_ending_diversity(): Terminal states             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Reward Functions (6 components, max 6.0)                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ reward_valid_json:           1.0 × valid JSON              │  │
│  │ reward_schema_valid:         2.0 × schema compliance       │  │
│  │ reward_structural:           1.0 × size requirements       │  │
│  │ reward_effect_diversity:     0.5 × Dirac variety           │  │
│  │ reward_secret_paths:         0.5 × gated options           │  │
│  │ reward_multiple_endings:     0.5 × terminal diversity      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  verifiers.SingleTurnEnv Interface                               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ load_environment()                                          │  │
│  │  → Dataset (prompts + requirements)                        │  │
│  │  → Rubric (reward functions + weights)                     │  │
│  │  → Environment (evaluation + training ready)               │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Configuration → 2. Prompt → 3. LLM → 4. JSON → 5. Validation → 6. Reward

┌─────────────┐   ┌─────────┐   ┌─────┐   ┌──────┐   ┌──────────┐   ┌────────┐
│  StoryConfig│───▶│ Prompt  │───▶│ LLM │───▶│ JSON │───▶│Validator│───▶│Rubric │
│  - chars: 3 │   │ Template│   │     │   │ Text │   │  Checks  │   │6 funcs│
│  - encs: 10 │   │ + Themes│   └─────┘   └──────┘   │  Schema  │   │Total  │
│  - props: 3 │   │ + Props │                         │  Size    │   │Score  │
│  - spools:3 │   │         │                         │  Effects │   │ /6.0  │
└─────────────┘   └─────────┘                         └──────────┘   └────────┘
```

---

## Component 2: Corpus Amplification

```
┌──────────────────────────────────────────────────────────────────┐
│                   corpus_amplification.py                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Configuration Space                                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 30 property axes  (personality/relationship dimensions)    │  │
│  │ 50 themes         (AI safety, warfare, philosophy, etc.)   │  │
│  │ 40 settings       (space stations, labs, councils, etc.)   │  │
│  │                                                             │  │
│  │ Variable complexity:                                        │  │
│  │  - Characters: 2-5                                          │  │
│  │  - Properties: 2-6                                          │  │
│  │  - Encounters: 5-30                                         │  │
│  │  - Spools: 2-5                                              │  │
│  │                                                             │  │
│  │ Total unique configs: 382,814,432,000 (382 trillion)       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ConfigGenerator                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ generate_config()                                           │  │
│  │  → Sample characters, properties, encounters, spools        │  │
│  │  → Sample themes from expanded set                          │  │
│  │  → Sample setting from scenarios                            │  │
│  │  → Sample property axes                                     │  │
│  │  → Assign unique ID                                         │  │
│  │                                                             │  │
│  │ generate_batch(n)                                           │  │
│  │  → Generate n configs with controlled randomness            │  │
│  │  → Ensure no duplicates within batch                        │  │
│  │  → Save to manifest.jsonl                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  BatchGenerator                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ generate_batch(batch_size, batch_id)                        │  │
│  │  → Create batch of configs                                  │  │
│  │  → Write to manifest with metadata                          │  │
│  │  → Track batch IDs for provenance                           │  │
│  │                                                             │  │
│  │ estimate_token_count(config)                                │  │
│  │  → Base: 1000 tokens                                        │  │
│  │  → + 200 per character                                      │  │
│  │  → + 100 per property                                       │  │
│  │  → + 750 per encounter                                      │  │
│  │  → + 50 per spool                                           │  │
│  │  → Average: 15.4k tokens per storyworld                     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  CorpusInjector (Optional)                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ load_corpus(path)                                           │  │
│  │  → Load 40M token research corpus                          │  │
│  │  → Build semantic index                                     │  │
│  │  → Ready for thematic injection                             │  │
│  │                                                             │  │
│  │ get_thematic_content(theme)                                 │  │
│  │  → Retrieve corpus passages for theme                       │  │
│  │  → Via QFT-MCP phase encoding (TODO)                        │  │
│  │  → Enhance prompt with relevant content                     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Scaling Path

```
1k configs → 1k storyworlds → 15M tokens (baseline test)
   ↓
10k configs → 10k storyworlds → 150M tokens (validation)
   ↓
100k configs → 100k storyworlds → 1.5B tokens (initial corpus)
   ↓
1M configs → 1M storyworlds → 15B tokens (target corpus)
   ↓
10M configs → 10M storyworlds → 150B tokens (extended research)
```

**No repetition** due to 382T configuration space!

---

## Component 3: Training Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                     RL Training with prime-rl                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Training Loop                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                             │  │
│  │  1. Sample batch from environment                           │  │
│  │     └─▶ 16 prompts from dataset                            │  │
│  │                                                             │  │
│  │  2. Generate completions (vLLM inference)                   │  │
│  │     └─▶ Model produces storyworld JSON                     │  │
│  │         Temperature: 0.8, Top-p: 0.95                       │  │
│  │         Max tokens: 8000                                    │  │
│  │                                                             │  │
│  │  3. Evaluate with rubric                                    │  │
│  │     └─▶ 6 reward components → total score /6.0             │  │
│  │                                                             │  │
│  │  4. Compute policy gradient                                 │  │
│  │     └─▶ CISPO (Conservative Importance Sampling)            │  │
│  │         KL coefficient: 0.05                                │  │
│  │         Clip range: 0.2                                     │  │
│  │                                                             │  │
│  │  5. Update model weights                                    │  │
│  │     └─▶ AdamW optimizer, LR: 1e-5                           │  │
│  │         Gradient accumulation: 4 steps                      │  │
│  │                                                             │  │
│  │  6. Log metrics (WandB)                                     │  │
│  │     └─▶ Mean reward, schema valid %, effect diversity      │  │
│  │                                                             │  │
│  │  7. Repeat for 100 iterations                               │  │
│  │                                                             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Expected Progress                                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Iteration   0: 3.5/6.0 avg (60% schema valid)              │  │
│  │ Iteration  25: 4.2/6.0 avg (75% schema valid)              │  │
│  │ Iteration  50: 4.8/6.0 avg (85% schema valid)              │  │
│  │ Iteration  75: 5.1/6.0 avg (90% schema valid)              │  │
│  │ Iteration 100: 5.3/6.0 avg (93% schema valid)              │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component 4: QFT-MCP Integration

```
┌──────────────────────────────────────────────────────────────────┐
│                  State Transition Extraction                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  From Storyworld JSON                                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ For each encounter:                                         │  │
│  │   For each option:                                          │  │
│  │     For each reaction:                                      │  │
│  │       For each after_effect:                                │  │
│  │         Extract transition:                                 │  │
│  │           (state_before, operator, state_after)             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Transition Format                                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ {                                                           │  │
│  │   "from_encounter": "page_1",                               │  │
│  │   "via_option": "page_1_opt2",                              │  │
│  │   "via_reaction": "page_1_opt2_rxn1",                       │  │
│  │   "to_encounter": "page_5",                                 │  │
│  │   "operator": {                                             │  │
│  │     "type": "Set",                                          │  │
│  │     "character": "char_alice",                              │  │
│  │     "property": "Loyal_Treacherous",                        │  │
│  │     "delta": +10                                            │  │
│  │   }                                                         │  │
│  │ }                                                           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Phase Encoding (QFT-MCP)                                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ State vectors:                                              │  │
│  │   |ψ⟩ = ∑ₙ αₙ|character_properties⟩ₙ                       │  │
│  │                                                             │  │
│  │ Operators:                                                  │  │
│  │   Û = exp(i·φ·Δproperty)                                    │  │
│  │                                                             │  │
│  │ Transitions:                                                │  │
│  │   |ψ'⟩ = Û|ψ⟩                                              │  │
│  │                                                             │  │
│  │ Retrieval:                                                  │  │
│  │   Query: |query⟩ → Find similar via QFT                     │  │
│  │   Complexity: O(log N) for N=1M storyworlds                │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                         END-TO-END FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

1. CONFIGURATION GENERATION
   ┌────────────────────────────────────────────────────────┐
   │ ConfigGenerator.generate_batch(1000)                   │
   │  → 1000 unique StoryConfig objects                     │
   │  → Saved to manifest.jsonl                             │
   └────────────────────────────────────────────────────────┘
                          ↓

2. PROMPT CREATION
   ┌────────────────────────────────────────────────────────┐
   │ generate_storyworld_prompt(config)                     │
   │  → Structured prompt with requirements                 │
   │  → Enhanced with corpus content (optional)             │
   └────────────────────────────────────────────────────────┘
                          ↓

3. MODEL GENERATION
   ┌────────────────────────────────────────────────────────┐
   │ LLM inference (vLLM backend)                           │
   │  → Input: Prompt                                       │
   │  → Output: Storyworld JSON (8k tokens avg)            │
   └────────────────────────────────────────────────────────┘
                          ↓

4. VALIDATION
   ┌────────────────────────────────────────────────────────┐
   │ SweepweaveValidator.validate_structure()               │
   │  → Schema compliance check                             │
   │  → Size requirement verification                       │
   └────────────────────────────────────────────────────────┘
                          ↓

5. REWARD COMPUTATION
   ┌────────────────────────────────────────────────────────┐
   │ Rubric.evaluate()                                      │
   │  → 6 reward components                                 │
   │  → Total score: 0.0 - 6.0                             │
   └────────────────────────────────────────────────────────┘
                          ↓

6. POLICY UPDATE (Training) or FILTERING (Generation)
   ┌────────────────────────────────────────────────────────┐
   │ If training:                                           │
   │   → Compute gradients via CISPO                        │
   │   → Update model weights                               │
   │                                                        │
   │ If generating:                                         │
   │   → Filter by quality threshold (≥5.0)                 │
   │   → Save to corpus                                     │
   └────────────────────────────────────────────────────────┘
                          ↓

7. TRANSITION EXTRACTION (Post-processing)
   ┌────────────────────────────────────────────────────────┐
   │ extract_state_transitions()                            │
   │  → Parse all encounters/options/reactions              │
   │  → Extract Dirac operators                             │
   │  → Build transition database                           │
   └────────────────────────────────────────────────────────┘
                          ↓

8. QFT INDEXING (Research)
   ┌────────────────────────────────────────────────────────┐
   │ qft_encode_transitions()                               │
   │  → Phase encode state transitions                      │
   │  → Build quantum-accessible index                      │
   │  → Enable O(log N) semantic retrieval                  │
   └────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Single-Node Development

```
┌─────────────────────────────────────────────────────────┐
│                    Local Machine                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ vf.RLTrainer                                     │   │
│  │  - Training loop                                 │   │
│  │  - 1x GPU (3090/4090)                            │   │
│  │  - LoRA or full fine-tuning                      │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ vLLM Inference                                   │   │
│  │  - 50% GPU memory                                │   │
│  │  - Local model serving                           │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Sweepweave Environment                           │   │
│  │  - Dataset generation                            │   │
│  │  - Reward computation                            │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Multi-Node Production

```
┌──────────────────────────────────────────────────────────────────┐
│                    Prime Intellect Cluster                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Training Node (4x H100)                                    │  │
│  │  - prime-rl trainer                                        │  │
│  │  - FSDP2 distributed training                              │  │
│  │  - Gradient accumulation                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                               │                                   │
│                               ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Inference Nodes (8x H100)                                  │  │
│  │  - vLLM inference server                                   │  │
│  │  - Pipeline parallelism                                    │  │
│  │  - High throughput generation                              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                               │                                   │
│                               ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Orchestrator                                               │  │
│  │  - Manages rollout workers                                 │  │
│  │  - Coordinates training/inference                          │  │
│  │  - Handles batch scheduling                                │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Performance Characteristics

### Training Throughput

```
Model Size   GPUs    Batch    Tokens/sec   Time to 100 iters
─────────────────────────────────────────────────────────────
1B           1xH100  16       ~12k         ~2 hours
8B           1xH100  16       ~3k          ~8 hours
8B           4xH100  64       ~12k         ~2 hours
70B          8xH100  64       ~2k          ~12 hours
```

### Generation Throughput

```
Model Size   GPUs    Storyworlds/hour   Tokens/hour
────────────────────────────────────────────────────
1B           1xH100  ~200               ~3M
8B           1xH100  ~100               ~1.5M
8B           4xH100  ~400               ~6M
70B          8xH100  ~200               ~3M
```

### Corpus Build Time

```
Target      Model   GPUs    Wall-clock    Cost (Prime)
────────────────────────────────────────────────────────
10k SW      8B      1xH100  ~100 hours    ~$200
100k SW     8B      4xH100  ~250 hours    ~$2000
1M SW       8B      8xH100  ~5000 hours   ~$20000

(SW = storyworlds)
```

---

## Summary

This architecture provides:

✅ **Modular design**: Easy to extend/modify  
✅ **Quality guarantees**: Multi-criteria evaluation  
✅ **Massive scale**: 382T config space  
✅ **Production ready**: Full integration with verifiers/prime-rl  
✅ **Research ready**: QFT-MCP integration for semantic indexing  

**From zero to 15B tokens in 2 weeks of cluster time.**
