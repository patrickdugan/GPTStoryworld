# Narrative Feature Extraction + RL Training System

Complete training infrastructure for generating high-quality interactive narrative storyworlds using Sparse Autoencoders (SAEs) and Reinforcement Learning (RL).

## Overview

This system combines two powerful techniques:

1. **Sparse Autoencoder (SAE) Feature Discovery**: Learns interpretable narrative features from storyworld rollouts
2. **Reinforcement Learning Optimization**: Fine-tunes language models to generate better storyworlds

### Key Innovation

The system creates a **virtuous cycle**:
- SAE discovers interpretable features (character arcs, plot structures, affordance patterns)
- These features augment the RL reward signal
- Improved policy generates richer rollouts
- Re-training SAE discovers even better features
- Iterate to convergence

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATIVE TRAINING PIPELINE                   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │  SAE TRAINING  │       │  RL TRAINING   │
            │                │       │                │
            │ • State encode │       │ • Policy grad  │
            │ • L1 sparsity  │       │ • KL penalty   │
            │ • Feature disc │◄──────┤ • Verifiers    │
            └────────────────┘       └────────────────┘
                    │                         │
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │   FEATURES     │       │   STORYWORLDS  │
            │                │       │                │
            │ • Sparse z     │       │ • Valid JSON   │
            │ • I(z; a | s)  │──────►│ • Rich struct  │
            │ • Interpret    │       │ • Multi-endings│
            └────────────────┘       └────────────────┘
```

## Components

### 1. SAE Feature Extraction (`sae_narrative_features.py`)

Trains sparse autoencoders on narrative state representations.

**Key Classes:**
- `SparseAutoencoder`: PyTorch model with L1 sparsity
- `StoryWorldStateExtractor`: Converts storyworld states to vectors
- `RolloutDataset`: Dataset of (state, affordances) pairs
- `FeatureAffordanceAnalyzer`: Measures I(z; a | s)

**What it does:**
- Compresses character properties, variables, encounter history into sparse feature vectors
- Discovers interpretable dimensions (e.g., "trust crisis", "wealth accumulation", "secret revealed")
- Identifies features that predict narrative affordances (available options)

**Usage:**
```python
from sae_narrative_features import train_sae_on_rollouts

# Train on rollouts
sae, dataset, history = train_sae_on_rollouts(
    rollouts,
    latent_dim=256,
    sparsity_coef=0.05,
    n_epochs=50
)

# Analyze features
analyzer = FeatureAffordanceAnalyzer(sae, dataset)
top_features = analyzer.identify_top_features(n_top=10)
```

### 2. RL Training Infrastructure (`rl_training_infrastructure.py`)

Reinforcement learning system for fine-tuning language models.

**Key Classes:**
- `StoryWorldVerifiers`: 6-component reward function
- `StoryWorldRLTrainer`: PPO-style training with KL penalty
- `RLConfig`: Training hyperparameters

**Reward Components:**
1. **JSON Validity** (0/1): Parseable output
2. **Schema Compliance** (0-1): Required fields present
3. **Structural Completeness** (0-1): Character count, encounter count, options
4. **Effect Diversity** (0-1): Variety of Dirac operators (variable changes)
5. **Secret Paths** (0-1): Gated options creating explorable branches
6. **Multiple Endings** (0-1): Terminal encounter diversity

**Usage:**
```python
from rl_training_infrastructure import StoryWorldRLTrainer, RLConfig

config = RLConfig(
    model_name="gpt2",
    max_length=1024,
    batch_size=4,
    n_epochs=10,
    learning_rate=5e-6
)

trainer = StoryWorldRLTrainer(config)
trainer.train()
```

### 3. Integrated Pipeline (`integrated_training_pipeline.py`)

Combines SAE and RL in iterative cycles.

**Key Classes:**
- `FeatureAwareVerifiers`: Extended verifiers with 7th component (feature quality)
- `IterativeTrainingPipeline`: Orchestrates SAE ↔ RL cycle

**Training Cycle:**
```
Cycle N:
  1. Generate rollouts with current policy (100 storyworlds)
  2. Train SAE on states → discover features
  3. Update verifiers with feature quality metric
  4. Run RL training (2 epochs)
  5. Save checkpoint
  6. Repeat
```

**Usage:**
```python
from integrated_training_pipeline import IterativeTrainingPipeline, RLConfig

rl_config = RLConfig(
    model_name="gpt2",
    max_length=1024,
    batch_size=2,
    n_samples_per_epoch=20
)

pipeline = IterativeTrainingPipeline(
    rl_config=rl_config,
    sae_latent_dim=256,
    n_cycles=5,
    rollouts_per_cycle=100
)

pipeline.train()
```

## Installation

```bash
# Core dependencies
pip install torch transformers numpy matplotlib scikit-learn tqdm

# Optional: Weights & Biases for logging
pip install wandb

# Optional: Prime Intellect Verifiers framework
pip install verifiers
```

See `requirements.txt` for full list.

## Quick Start

### Train SAE Only

```python
# Generate or load rollouts
rollouts = [...]  # List[List[Dict]]

# Train SAE
from sae_narrative_features import train_sae_on_rollouts

sae, dataset, history = train_sae_on_rollouts(
    rollouts,
    latent_dim=256,
    n_epochs=50
)

# Save model
torch.save(sae.state_dict(), "sae_narrative.pt")
```

### Train RL Only

```python
from rl_training_infrastructure import StoryWorldRLTrainer, RLConfig

config = RLConfig(
    model_name="gpt2",
    n_epochs=10,
    save_dir="./checkpoints"
)

trainer = StoryWorldRLTrainer(config)
trainer.train()
```

### Full Integrated Training

```python
from integrated_training_pipeline import IterativeTrainingPipeline, RLConfig

rl_config = RLConfig(model_name="gpt2")

pipeline = IterativeTrainingPipeline(
    rl_config=rl_config,
    n_cycles=5
)

pipeline.train()
```

## Output Format

Models generate Sweepweave JSON with the following structure:

```json
{
  "characters": {
    "Alice": {"initial_trust": 0.5},
    "Bob": {"initial_trust": -0.2}
  },
  "initial_state": {
    "Alice_trust": 0.5,
    "Bob_trust": -0.2,
    "debt": 50
  },
  "properties": {
    "trust": {"min": -1.0, "max": 1.0}
  },
  "encounters": [
    {
      "id": "enc_1",
      "text": "Alice proposes a business deal...",
      "options": [
        {
          "id": "accept",
          "text": "Accept the deal",
          "gates": [],
          "reactions": [
            {
              "after_effects": [
                {"variable": "Alice_trust", "change": 0.2}
              ],
              "next_encounter": "enc_2"
            }
          ]
        }
      ]
    }
  ]
}
```

## Evaluation Metrics

### SAE Metrics
- **MSE Loss**: Reconstruction quality
- **L0 Norm**: Sparsity (lower = better)
- **L1 Penalty**: Feature activation magnitude
- **Mutual Information I(z; a | s)**: Feature-affordance coupling
- **Correlation**: Feature activation vs. option cardinality

### RL Metrics
- **Total Reward**: Weighted sum of 6-7 components
- **Valid JSON Rate**: Percentage of parseable outputs
- **KL Divergence**: Distance from reference model
- **Component Scores**: Individual verifier performance

### Integrated Metrics
- **Feature Quality**: Sparsity + reconstruction + variance
- **Cycle Improvement**: Reward delta between cycles
- **Convergence Rate**: Iterations to threshold

## Advanced Usage

### Custom Verifiers

```python
class CustomVerifier(StoryWorldVerifiers):
    def verify_custom_metric(self, data: Dict) -> float:
        # Your logic here
        return score
    
    def compute_total_reward(self, text: str, weights=None):
        rewards = super().compute_total_reward(text, weights)
        rewards['custom'] = self.verify_custom_metric(data)
        # Update total
        return rewards
```

### Custom SAE Architecture

```python
class DeepSAE(nn.Module):
    def __init__(self, input_dim, latent_dim):
        super().__init__()
        # Multi-layer encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, latent_dim),
            nn.ReLU()
        )
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 512),
            nn.ReLU(),
            nn.Linear(512, input_dim)
        )
```

### Integration with QFT-MCP

For semantic corpus retrieval:

```python
# Hypothetical integration with your QFT system
from qft_mcp import QFTRetriever

retriever = QFTRetriever(corpus_path="./40M_corpus")

# Populate encounter text with semantically relevant content
def enhance_encounter(encounter_stub, theme):
    query = f"{encounter_stub} {theme}"
    relevant_texts = retriever.query(query, k=5)
    return relevant_texts[0]  # Best match
```

## Performance

Expected training times (on GPU):

| Component | Dataset Size | Time per Epoch | Total Time |
|-----------|--------------|----------------|------------|
| SAE | 10K states | 2 min | 100 min (50 epochs) |
| RL | 100 samples | 5 min | 50 min (10 epochs) |
| Integrated | 5 cycles | 30 min/cycle | 150 min |

Memory requirements:
- SAE: ~1GB GPU memory
- RL (GPT-2): ~2GB GPU memory
- RL (GPT-2 Large): ~4GB GPU memory

## Scaling

To scale to billions of tokens:

1. **Corpus Amplification**: Use combinatorial theme/property generator
2. **Distributed Training**: Multi-GPU with DDP
3. **Batch Generation**: Generate 1000s of storyworlds in parallel
4. **QFT Integration**: Populate encounters from 40M corpus

Expected output at scale:
- 1M unique storyworlds × 15K tokens each = **15B tokens**
- Zero repetition through combinatorial explosion
- Thematic coherence via QFT retrieval

## Citation

If you use this system, please cite:

```bibtex
@software{narrative_sae_rl_2025,
  author = {Patrick},
  title = {Sparse Autoencoder + RL Training for Narrative Generation},
  year = {2025},
  note = {Storyworlds research project}
}
```

## License

MIT License - see LICENSE file

## Contact

For questions or collaboration:
- TradeLayer: [your contact]
- QFT-MCP: [your contact]
- Storyworlds research: [your contact]
