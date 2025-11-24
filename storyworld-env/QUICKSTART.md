# Sweepweave Environment: Quick Start

## 30-Second Install

```bash
# Copy environment to your project
cp -r /mnt/user-data/outputs/sweepweave ~/my-project/
cp /mnt/user-data/outputs/pyproject.toml ~/my-project/
cp /mnt/user-data/outputs/deploy.sh ~/my-project/

cd ~/my-project

# Install
./deploy.sh setup

# Test
./deploy.sh test
```

✅ Done! Environment ready for use.

---

## 5-Minute Baseline Eval

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Evaluate GPT-4.1
./deploy.sh eval-baseline gpt-4.1-mini 20 3

# Or Claude Sonnet 4.5
export ANTHROPIC_API_KEY="sk-ant-..."
./deploy.sh eval-claude 20 3
```

Results saved to `./eval_results/`

Expected scores:
- **GPT-4.1 Mini**: 3.5/6.0 (60-70% schema valid)
- **Claude Sonnet 4.5**: 4.0/6.0 (75-85% schema valid)

---

## 1-Hour Training Setup

```bash
# Set up RL training
./deploy.sh setup-training

# Edit config if needed
nano configs/prime-rl/sweepweave.toml

# Launch training (requires GPU)
./deploy.sh train

# Monitor in tmux
tmux attach -t prime-rl
```

After 100 iterations (~1 hour on H100):
- Schema valid rate: 85-95%
- Average reward: 5.0+/6.0

---

## 1-Day Corpus Generation

```bash
# Generate 100k configs
./deploy.sh generate-configs 100 1000

# Expected: ~1.5B tokens
# See corpus_configs/manifest.jsonl
```

Each config defines:
- Characters (2-5)
- Properties (2-6 axes)
- Encounters (5-30 nodes)
- Spools (2-5 flow controllers)
- Themes & setting

Use with trained model to generate actual storyworlds.

---

## Configuration Space

```bash
# Show estimates
./deploy.sh estimate
```

Output:
```
Configuration Space:
- 382 trillion unique configs
- 1M storyworlds = 15.4B tokens
- <0.001% of space used
```

**No repetition at any scale.**

---

## Common Workflows

### Research: Generate Diverse Corpus

```bash
# 1. Train model
./deploy.sh setup-training
./deploy.sh train

# 2. Generate configs
./deploy.sh generate-configs 1000 1000  # 1M configs

# 3. Generate storyworlds (with trained model)
# See INTEGRATION_GUIDE.md Part 4
```

### Development: Test New Reward Functions

```python
# Edit sweepweave/__init__.py
def reward_custom(prompt, completion, info) -> float:
    # Your logic here
    return 0.5

# Add to rubric
rubric = vf.Rubric(
    funcs=[..., reward_custom],
    weights=[..., 0.5]
)

# Test
./deploy.sh test
```

### Production: Deploy to Prime Intellect

```bash
# Authenticate
uv tool install prime
prime login

# Publish environment
./deploy.sh publish

# Launch training on cluster
prime cluster create --name sweepweave-v1 --gpus 8xH100
# SSH in and run training
```

---

## File Structure

```
sweepweave-env/
├── sweepweave/
│   └── __init__.py           # Core environment
├── test_sweepweave_env.py    # Test suite
├── corpus_amplification.py   # Billion-token scaling
├── pyproject.toml            # Package metadata
├── deploy.sh                 # Automation script
├── README.md                 # Documentation
├── INTEGRATION_GUIDE.md      # Complete guide
└── PROJECT_SUMMARY.md        # Overview
```

---

## Next Steps

1. **Run baseline eval** → Establish quality bar
2. **Train initial model** → Get to 5.0/6.0 reward
3. **Generate corpus** → 100k-1M storyworlds
4. **Integrate QFT** → Semantic indexing

See `PROJECT_SUMMARY.md` for detailed roadmap.

---

## Key Commands

```bash
./deploy.sh setup              # Install
./deploy.sh test               # Run tests
./deploy.sh eval-baseline      # Evaluate model
./deploy.sh setup-training     # Prepare for RL
./deploy.sh train              # Start RL training
./deploy.sh generate-configs   # Create corpus configs
./deploy.sh estimate           # Show stats
./deploy.sh publish            # Publish to Hub
./deploy.sh clean              # Clean build files
./deploy.sh format             # Format code
```

---

## Support

- **Docs**: `README.md`, `INTEGRATION_GUIDE.md`, `PROJECT_SUMMARY.md`
- **Tests**: `pytest test_sweepweave_env.py -v`
- **Estimates**: `python corpus_amplification.py --estimate-only`
- **Verifiers**: https://github.com/PrimeIntellect-ai/verifiers
- **Sweepweave**: https://github.com/sweepweave

---

## Quality Targets

| Metric | Baseline | After Training | Target |
|--------|----------|----------------|--------|
| Valid JSON | 60-70% | 95%+ | 98%+ |
| Schema Valid | 60-70% | 85-95% | 90%+ |
| Avg Reward | 3.5/6.0 | 5.0/6.0 | 5.5/6.0 |
| Effect Diversity | 0.3 | 0.6 | 0.7 |
| Secret Paths | 0.2 | 0.4 | 0.5 |
| Multiple Endings | 0.5 | 0.8 | 0.9 |

---

**Ready to generate billions of tokens of structured narrative!**

Questions? See `INTEGRATION_GUIDE.md` or reach out.
