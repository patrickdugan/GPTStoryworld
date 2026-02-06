# Sweepweave Narrative Generation Environment

A [Prime Intellect Verifiers](https://github.com/PrimeIntellect-ai/verifiers) environment for fine-tuning LLMs to generate high-quality interactive narrative storyworlds using the [Sweepweave](https://github.com/sweepweave) format.

## Overview

This environment trains models to produce complex branching narratives with:

- **Character state management** via bounded numerical properties (personality/relationship axes)
- **Branching narrative structure** with encounters, options, reactions, and consequences
- **Dynamic effects system** (Dirac operators) that modify character properties
- **Spool-based flow control** for narrative pacing and availability windows
- **Multiple endings** and secret pathable paths through conditional option gating
- **Thematic coherence** across generated content

## Quality Criteria

Models are rewarded for generating storyworlds that:

1. **Parse as valid JSON** and load in the Sweepweave Godot engine
2. **Match the schema** with all required fields (characters, properties, encounters, spools)
3. **Meet structural requirements** (N characters, N encounters, N spools, branching factor)
4. **Demonstrate effect diversity** (varied Dirac operators modifying different properties)
5. **Include secret paths** (some options gated by character property conditions)
6. **Provide multiple endings** (2-5 distinct terminal states)
7. **Keep ending gates complete** (every `page_end_*` reachable from the final gate and not blocked by acceptability fallbacks)

## Raised Polish Thresholds

Use these higher targets when running late-stage polish (`late_stage_balance.py`, `long_range_authoring.py`, `multiple_paths.py`):

- Average after-effects per reaction: **4.5**
- Reactions per option: **2.5**
- Options per encounter: **3.2**
- Variables per reaction desirability formula: **1.6**
- Act II visibility gating: **5% of total options**, gated by **1.2 variables** on average
- Act III visibility gating: **8% of total options**, gated by **1.5 variables** on average
- Secret-ending encounters must be gated by an availability script that uses a **metric distance** over **two variables**
- Monte Carlo tuning: secret ending reachable in **>5%** of runs

## Installation

### From Source

```bash
# Clone this repository
git clone https://github.com/yourusername/sweepweave-env
cd sweepweave-env

# Install with uv
uv pip install -e .
```

### From Prime Intellect Hub (once published)

```bash
prime env install yourusername/sweepweave
```

## Usage

### Quick Evaluation

Evaluate an API model on Sweepweave generation:

```bash
uv run vf-eval sweepweave -m gpt-4.1-mini -n 10 -r 1
```

### Python API

```python
import verifiers as vf
from openai import AsyncOpenAI

# Load environment
env = vf.load_environment("sweepweave", num_examples=100)

# Async evaluation
client = AsyncOpenAI()
results = await env.evaluate(
    client=client,
    model="gpt-4.1-mini",
    num_examples=10,
    rollouts_per_example=1
)

# View results
print(f"Mean reward: {results['mean_reward']:.3f}")
print(f"Schema valid: {results['schema_valid_rate']:.2%}")

# Convert to HF dataset for analysis
dataset = env.make_dataset(results)
```

### Training with prime-rl

```bash
# Set up training environment
uv run vf-setup

# Edit configs/prime-rl/sweepweave.toml with your settings

# Launch training
uv run prime-rl @ configs/prime-rl/sweepweave.toml
```

### Training with vf.RLTrainer

```bash
# Edit configs/vf-rl/sweepweave.toml

# Launch training
uv run vf-rl @ configs/vf-rl/sweepweave.toml
```

## Environment Parameters

When loading the environment, you can customize:

```python
env = vf.load_environment(
    "sweepweave",
    num_examples=100,        # Number of training prompts
    min_characters=2,        # Minimum characters per storyworld
    max_characters=5,        # Maximum characters per storyworld
    min_encounters=5,        # Minimum encounters per storyworld
    max_encounters=20,       # Maximum encounters per storyworld
    seed=42,                 # Random seed for reproducibility
)
```

## Reward Function Details

The environment uses a multi-component reward function:

| Component | Weight | Description |
|-----------|--------|-------------|
| `valid_json` | 1.0 | Output must be parseable JSON |
| `schema_valid` | 2.0 | Output must match Sweepweave schema |
| `schema_soft` | 0.3 | Penalize missing pronoun/depth |
| `structural_completeness` | 1.0 | Meets character/encounter/spool counts |
| `effect_diversity` | 0.5 | Variety of character property effects |
| `min_spec_compliance` | 0.6 | Non-ending encounters meet min options/reactions/effects |
| `text_length_compliance` | 0.6 | Encounter 50-300 words; reaction text 20-150 words |
| `effects_per_reaction` | 0.6 | Average after-effects per reaction (target 4.5) |
| `reactions_per_option` | 0.6 | Average reactions per option (target 2.5) |
| `options_per_encounter` | 0.6 | Average options per encounter (target 3.2) |
| `desirability_var_usage` | 0.5 | Variables per desirability formula (target 1.6) |
| `pvalue_desirability_alignment` | 0.5 | pValues in desirability when reactions modify properties |
| `effect_script_quality` | 0.5 | After_effect scripts use operators with non-zero constants |
| `secret_paths` | 0.5 | Options with conditional visibility |
| `secret_gate_quality` | 0.6 | Gated options with variable desirability and stronger effects |
| `major_turns` | 0.6 | Act II/III flip/blend turning points |
| `act2_gating` | 0.5 | Act II gating ratio/variable richness |
| `act3_gating` | 0.5 | Act III gating ratio/variable richness |
| `secret_metric_distance` | 0.4 | Secret encounters gated by 2-var metric distance |
| `multiple_endings` | 0.5 | 2-5 distinct terminal states |
| `dead_end_rate` | 0.5 | Monte Carlo dead-end rate (<5% target) |
| `ending_balance` | 0.5 | Ending distribution (avoid dominance) |
| `unreachable_endings` | 0.6 | Penalize endings not reachable in Monte Carlo |
| `late_blocking` | 0.5 | Late-game blocking target band (10-30%) |
| `secret_reachability` | 0.3 | Secrets reachable at least occasionally |

Total maximum reward: **15.3**

## Compact Belief Manifold

For focused diplomacy runs, project logs into a fixed-size manifold with explicit compact belief subspaces:

```bash
python manifold_projection.py \
  --log logs/diplomacy_run.jsonl \
  --pvalue-dims 8 \
  --p2value-dims 8 \
  --out logs/diplomacy_run.manifold.json
```

Dimension layout:
- Base (5): coalition count, coalition mean stability, betrayal surprise, betrayal flag, active party count.
- Compact pValue block: hash-bucket embedding of keyrings with length 2.
- Compact p2Value block: hash-bucket embedding of keyrings with length 3.
- Sidecar per turn: coalition/defection/betrayal probabilities and recommended global action.

This keeps global dimensionality stable while preserving high-cardinality belief evidence.

## Ending Gate Sanity Checklist

If you use a terminal gate encounter (for example `page_endings_gate`), ensure:

- Every `page_end_*` (and `page_secret_*`) is reachable via a reaction from the gate.
- Ending encounters use permissive `acceptability_script` (usually `True`) so the gate, not the ending, decides eligibility.
- Reaction desirability or acceptability bands, not fallback defaults, determine the ending mix.

## Sweepweave Format

The Sweepweave format represents interactive narratives as JSON with:

- **Characters**: Agents with personality/relationship properties
- **Authored Properties**: Bounded number axes like `Loyal_Treacherous`, `Calm_Explosive`
- **Encounters**: Narrative nodes with text and player choices
- **Options**: Choices available to the player
- **Reactions**: Outcomes of choices with after-effects
- **After-effects**: Dirac operators that modify character properties
- **Spools**: Control which encounters are available at different story stages

Example minimal structure:

```json
{
  "IFID": "SW-GEN-12345",
  "characters": [
    {
      "id": "char_alice",
      "name": "Alice",
      "bnumber_properties": {
        "Loyal_Treacherous": 0,
        "Calm_Explosive": 0
      }
    }
  ],
  "authored_properties": [
    {
      "id": "Loyal_Treacherous",
      "property_name": "Loyal_Treacherous",
      "property_type": "bounded number",
      "default_value": 0
    }
  ],
  "encounters": [
    {
      "id": "page_start",
      "title": "Beginning",
      "options": [
        {
          "id": "page_start_opt1",
          "reactions": [
            {
              "id": "page_start_opt1_rxn1",
              "consequence_id": "page_next",
              "after_effects": [
                {
                  "effect_type": "Set",
                  "Set": { "character": "char_alice", "keyring": ["Loyal_Treacherous"] },
                  "to": { "operator_type": "Addition", "operands": [...] }
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "spools": [
    {"id": "spool_main", "spool_type": "General"}
  ]
}
```

## Scaling to Billions of Tokens

This environment supports massive-scale corpus generation through:

1. **Combinatorial expansion**: 10 property axes × 10 themes × 10 settings = 1000+ unique prompt templates
2. **Variable complexity**: 2-5 characters × 5-20 encounters × 2-3 options = exponential narrative space
3. **Procedural themes**: Can inject from custom corpus (e.g., 40M token research library)
4. **Quality filtering**: RL training ensures only high-quality outputs contribute to corpus
5. **Phase parsing**: Generated JSON encodes state transitions perfectly for QFT analysis

Expected output with trained model:
- **Per storyworld**: 10-50k tokens of structured narrative
- **Quality threshold**: >5.0/6.0 average reward
- **Generation rate**: 100-1000 storyworlds/hour (depending on model size)
- **Corpus scale**: 1M storyworlds = 10-50B tokens

## Integration with QFT-MCP

Generated storyworlds are ideal for quantum Fourier transform corpus indexing:

```python
# Extract state transition graph
for encounter in storyworld["encounters"]:
    for option in encounter["options"]:
        for reaction in option["reactions"]:
            # Each after_effect is a Dirac operator
            for effect in reaction["after_effects"]:
                character = effect["Set"]["character"]
                property = effect["Set"]["keyring"][0]
                delta = compute_delta(effect["to"])
                
                # Store as (state_before, operator, state_after) triple
                transitions.append((encounter_id, (character, property, delta), consequence_id))

# Phase encode transition graph for QFT indexing
phase_encoded = qft_encode_transitions(transitions)
```

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check --fix .
```

## Citation

If you use this environment in your research:

```bibtex
@misc{sweepweave_env_2025,
  author = {Patrick},
  title = {Sweepweave Narrative Generation Environment},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/yourusername/sweepweave-env}
}
```

## License

Apache 2.0

## Related Projects

- [Sweepweave Editor](https://github.com/sweepweave) - Godot-based interactive fiction engine
- [Prime Intellect Verifiers](https://github.com/PrimeIntellect-ai/verifiers) - RL environment framework
- [TradeLayer](https://tradelayer.org) - Bitcoin perpetual futures DEX protocol
- [QFT-MCP](https://github.com/yourusername/qft-mcp) - Quantum Fourier transform corpus indexing
