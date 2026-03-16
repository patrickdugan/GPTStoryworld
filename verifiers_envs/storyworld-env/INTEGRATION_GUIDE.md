# Sweepweave Environment Integration Guide

## Quick Reference

**382 TRILLION unique storyworld configurations possible**

Expected corpus scale with trained model:
- 1M storyworlds → **15.4B tokens** of structured narrative
- Each storyworld: 10-30k tokens with complete state transition graphs
- Quality threshold: >5.0/6.0 reward (schema valid + structurally complete)

---

## Part 1: Environment Setup & Evaluation

### Installation

```bash
# Create new project
uv init sweepweave-training && cd sweepweave-training
uv venv --python 3.12

# Install environment
uv add verifiers
uv pip install -e /path/to/sweepweave-env

# Verify installation
uv run python -c "import verifiers as vf; env = vf.load_environment('sweepweave'); print(f'Loaded: {len(env.dataset)} examples')"
```

### Quick Evaluation

```bash
# Evaluate GPT-4.1 baseline
uv run vf-eval sweepweave -m gpt-4.1-mini -n 20 -r 3 --save

# Evaluate Claude Sonnet 4.5
export ANTHROPIC_API_KEY="your-key"
uv run vf-eval sweepweave \
  -m claude-sonnet-4-5-20250929 \
  --base-url https://api.anthropic.com/v1 \
  -n 20 -r 3 --save

# Evaluate local model
uv run vf-eval sweepweave \
  -m "your-model" \
  --base-url http://localhost:8000/v1 \
  -n 100 -r 1
```

### Python API Usage

```python
import verifiers as vf
from openai import AsyncOpenAI
import json

# Load environment
env = vf.load_environment(
    "sweepweave",
    num_examples=100,
    min_characters=2,
    max_characters=5,
    min_encounters=10,
    max_encounters=30,
    seed=42
)

# Evaluate
client = AsyncOpenAI()
results = await env.evaluate(
    client=client,
    model="gpt-4.1-mini",
    num_examples=10,
    rollouts_per_example=1
)

# Analyze results
print(f"Mean reward: {results['mean_reward']:.3f} / 5.5")
print(f"Valid JSON: {sum(1 for r in results['rewards'] if r['reward_valid_json'] > 0) / len(results['rewards']):.1%}")
print(f"Schema valid: {sum(1 for r in results['rewards'] if r['reward_schema_valid'] > 0) / len(results['rewards']):.1%}")

# Save high-quality outputs
for i, rollout in enumerate(results['rollouts']):
    if rollout['total_reward'] > 5.0:
        output = rollout['completion'][-1]['content']
        # Extract JSON
        if '```json' in output:
            json_str = output.split('```json')[1].split('```')[0]
        else:
            json_str = output
        
        data = json.loads(json_str)
        
        # Save to corpus
        with open(f"corpus/storyworld_{i:04d}.json", "w") as f:
            json.dump(data, f, indent=2)
```

---

## Part 2: RL Training with prime-rl

### Setup

```bash
# Install prime-rl
uv run vf-setup

# This creates:
# - configs/prime-rl/sweepweave.toml
# - .tmux-prime-rl session manager
```

### Configuration

Edit `configs/prime-rl/sweepweave.toml`:

```toml
[run]
project_name = "sweepweave-narrative-v1"
base_model = "meta-llama/Llama-3.1-8B-Instruct"  # Or your base model
output_dir = "./outputs/sweepweave-v1"

[environment]
name = "sweepweave"
num_examples = 1000
min_characters = 2
max_characters = 5
min_encounters = 10
max_encounters = 30

[training]
num_iterations = 100
batch_size = 16
learning_rate = 1e-5
warmup_steps = 100

# RL-specific
temperature = 0.8
top_p = 0.95
max_tokens = 8000  # Storyworlds are long!

# CISPO (Conservative Importance-Sampled Policy Optimization)
kl_coef = 0.05
clip_range = 0.2

[inference]
tensor_parallel_size = 1
max_model_len = 16000  # Need large context for storyworld generation
gpu_memory_utilization = 0.8

[logging]
wandb_project = "sweepweave-rl"
log_interval = 10
eval_interval = 100
save_interval = 500
```

### Launch Training

```bash
# Single-node, single-GPU
uv run prime-rl @ configs/prime-rl/sweepweave.toml

# Multi-GPU (4x GPUs)
uv run prime-rl @ configs/prime-rl/sweepweave.toml \
  --tensor-parallel-size 1 \
  --pipeline-parallel-size 1 \
  --num-gpus 4

# Multi-node on Prime Intellect
prime cluster create \
  --name sweepweave-training \
  --gpus 8xH100 \
  --image ubuntu_22_cuda_12

# SSH into cluster and launch
prime-rl @ configs/prime-rl/sweepweave.toml
```

### Monitor Training

```bash
# Attach to tmux session
tmux attach -t prime-rl

# View logs
tail -f outputs/sweepweave-v1/logs/training.log

# Check WandB dashboard
# https://wandb.ai/your-username/sweepweave-rl
```

---

## Part 3: Alternative Training with vf.RLTrainer

For single-node experimentation:

```bash
# Create config
cat > configs/vf-rl/sweepweave.toml << 'EOF'
[run]
project_name = "sweepweave-nano"
base_model = "meta-llama/Llama-3.2-1B-Instruct"
output_dir = "./outputs/sweepweave-nano"

[environment]
name = "sweepweave"
num_examples = 100

[training]
num_train_epochs = 3
per_device_train_batch_size = 4
learning_rate = 1e-5
warmup_steps = 50
max_steps = 1000

[inference]
max_model_len = 8192
temperature = 0.8
EOF

# Launch
uv run vf-rl @ configs/vf-rl/sweepweave.toml
```

---

## Part 4: Quality Filtering & Corpus Construction

### Post-Training Evaluation

```python
import verifiers as vf
from openai import OpenAI
import json
from pathlib import Path

# Load trained model
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")

# Evaluate on large test set
env = vf.load_environment("sweepweave", num_examples=10000, seed=999)
results = env.evaluate_sync(
    client=client,
    model="your-trained-model",
    num_examples=10000,
    rollouts_per_example=1
)

# Filter high-quality outputs
quality_threshold = 5.0
corpus_dir = Path("corpus/high_quality")
corpus_dir.mkdir(parents=True, exist_ok=True)

filtered_count = 0
for i, rollout in enumerate(results['rollouts']):
    if rollout['total_reward'] >= quality_threshold:
        output = rollout['completion'][-1]['content']
        
        # Extract and validate JSON
        try:
            if '```json' in output:
                json_str = output.split('```json')[1].split('```')[0]
            else:
                json_str = output
            
            data = json.loads(json_str)
            
            # Additional validation
            from sweepweave import SweepweaveValidator
            valid, _ = SweepweaveValidator.validate_structure(data)
            
            if valid:
                # Save
                filename = f"storyworld_{data['IFID']}.json"
                with open(corpus_dir / filename, "w") as f:
                    json.dump(data, f, indent=2)
                
                filtered_count += 1
        except:
            continue

print(f"Saved {filtered_count} / {len(results['rollouts'])} high-quality storyworlds")
print(f"Quality rate: {filtered_count / len(results['rollouts']):.1%}")
```

### Batch Generation for Corpus

```python
from corpus_amplification import ConfigGenerator, BatchGenerator, CorpusInjector
from pathlib import Path

# Initialize
config_gen = ConfigGenerator(seed=42)
corpus_inj = CorpusInjector()  # Optional: provide corpus_path for semantic injection
batch_gen = BatchGenerator(Path("./corpus_configs"), config_gen, corpus_inj)

# Generate 1M configs
num_batches = 1000
batch_size = 1000

for batch_id in range(num_batches):
    configs = batch_gen.generate_batch(batch_size, batch_id)
    
    if batch_id % 10 == 0:
        print(f"Generated batch {batch_id}/{num_batches}")

print("Config generation complete!")
print(f"Total: {num_batches * batch_size:,} configs")
print(f"Estimated corpus: ~15.4B tokens")
```

---

## Part 5: QFT-MCP Integration

### State Transition Extraction

```python
import json
from pathlib import Path

def extract_transitions(storyworld_path: Path):
    """Extract state transition graph from storyworld"""
    
    with open(storyworld_path) as f:
        data = json.load(f)
    
    transitions = []
    
    for encounter in data["encounters"]:
        enc_id = encounter["id"]
        
        for option in encounter.get("options", []):
            opt_id = option["id"]
            
            for reaction in option.get("reactions", []):
                rxn_id = reaction["id"]
                cons_id = reaction["consequence_id"]
                
                # Extract property changes (Dirac operators)
                for effect in reaction.get("after_effects", []):
                    char = effect.get("Set", {}).get("character")
                    prop = effect.get("Set", {}).get("keyring", [None])[0]
                    
                    if char and prop:
                        # Compute delta from operator
                        delta = compute_effect_delta(effect)
                        
                        transitions.append({
                            "from_encounter": enc_id,
                            "via_option": opt_id,
                            "via_reaction": rxn_id,
                            "to_encounter": cons_id,
                            "operator": {
                                "type": effect["effect_type"],
                                "character": char,
                                "property": prop,
                                "delta": delta
                            }
                        })
    
    return transitions

def compute_effect_delta(effect):
    """Compute numerical delta from effect operator"""
    
    if effect["effect_type"] == "Set":
        # Parse the 'to' expression
        to_expr = effect.get("to", {})
        
        if to_expr.get("operator_type") == "Addition":
            operands = to_expr.get("operands", [])
            # Second operand is typically the delta
            if len(operands) >= 2:
                return operands[1].get("coefficient", 0)
    
    elif effect["effect_type"] == "Increment":
        return effect.get("Increment", {}).get("coefficient", 0)
    
    return 0

# Process entire corpus
corpus_dir = Path("corpus/high_quality")
transition_db = []

for storyworld_file in corpus_dir.glob("*.json"):
    transitions = extract_transitions(storyworld_file)
    transition_db.extend(transitions)

print(f"Extracted {len(transition_db):,} state transitions")

# Save for QFT processing
with open("transitions.jsonl", "w") as f:
    for t in transition_db:
        f.write(json.dumps(t) + "\n")
```

### QFT Phase Encoding (Placeholder)

```python
# TODO: Implement QFT-MCP integration
#
# The transition database provides:
# - State vectors: (character, property_values)
# - Operators: (effect_type, delta)
# - Transitions: (state_before, operator, state_after)
#
# These can be phase-encoded for quantum Fourier retrieval:
# 1. Map character states to Hilbert space
# 2. Encode operators as unitary transformations
# 3. Phase-encode transition probabilities
# 4. Build quantum circuit for retrieval
#
# This enables O(log N) retrieval of semantically similar
# narrative structures from 15B+ token corpus.
```

---

## Part 6: Scaling Strategy

### Target: 15B+ Token Corpus

**Phase 1: Model Training (1 week)**
- Train on 1k examples with prime-rl
- Validate quality threshold >5.0/6.0
- Expected: 70-80% valid schema rate

**Phase 2: Initial Generation (1 week)**
- Generate 100k storyworlds with trained model
- Filter for quality (expect 60-70k high quality)
- Corpus size: ~1B tokens

**Phase 3: Scaled Generation (2 weeks)**
- Generate 1M storyworlds using batch processing
- Multi-node deployment on Prime Intellect
- Corpus size: ~15B tokens

**Phase 4: QFT Integration (ongoing)**
- Extract transition graphs
- Build phase-encoded index
- Enable semantic retrieval for research

### Resource Requirements

**Training:**
- 1x H100 80GB: ~1 week for 8B model
- 8x H100 80GB: ~1 week for 70B model

**Generation:**
- 100k storyworlds: ~100 GPU-hours (1B tokens)
- 1M storyworlds: ~1000 GPU-hours (15B tokens)

**Storage:**
- Raw JSON: ~50GB per 100k storyworlds
- Compressed: ~10GB per 100k storyworlds
- Transition DB: ~5GB per 100k storyworlds

---

## Part 7: Expected Results

### Quality Metrics

With properly trained model:
- **Valid JSON rate**: 95%+
- **Schema valid rate**: 85%+
- **Structural completeness**: 90%+
- **Effect diversity**: 0.6+
- **Secret paths**: 0.4+
- **Multiple endings**: 0.8+
- **Overall quality**: 5.2/6.0 average

### Diversity Metrics

- Unique theme combinations: 1000+
- Unique settings: 100+
- Unique property sets: 10000+
- Total unique configs used: 1M out of 382T possible
- Effective coverage: <0.001% (still no risk of repetition)

### Corpus Characteristics

- **Structured**: Every storyworld is valid Sweepweave JSON
- **Loadable**: Can be imported into Godot Sweepweave editor
- **Interactive**: Playable as branching narratives
- **State-tracked**: Complete character property transition graphs
- **Thematically coherent**: Based on consistent philosophical themes
- **QFT-ready**: Phase-encodable for semantic indexing

---

## Troubleshooting

### Common Issues

**"Model generates invalid JSON"**
- Increase schema_valid weight in rubric
- Add few-shot examples to prompt
- Use temperature=0.7 for more consistent output

**"Training diverges"**
- Reduce learning rate to 5e-6
- Increase KL coefficient to 0.1
- Reduce clip_range to 0.1

**"Generation too slow"**
- Increase tensor_parallel_size
- Use smaller base model (8B vs 70B)
- Reduce max_tokens to 6000

**"Quality threshold not met"**
- Train for more iterations
- Use larger base model
- Increase num_examples in training set

---

## Next Steps

1. **Run baseline evaluation** on GPT-4.1/Claude Sonnet 4.5
2. **Train initial model** with prime-rl on 1k examples
3. **Validate quality** with test set of 1k examples
4. **Scale generation** to 100k storyworlds
5. **Integrate QFT** for semantic indexing
6. **Iterate** based on quality metrics

For questions or contributions, see:
- Environment repo: https://github.com/yourusername/sweepweave-env
- Sweepweave editor: https://github.com/sweepweave
- Prime Intellect docs: https://docs.primeintellect.ai
