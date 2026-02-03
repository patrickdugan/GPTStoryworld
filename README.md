# Storyworld Meta-Agent

A modular system for generating Sweepweave-compatible interactive storyworlds using GPT and iterative metadata analysis.

## Usage

1. Edit `raw_storyworld.json` to define your world
2. Add your OpenAI API key to `.env`
3. Run: `npm install` then `npm start`

Each run:
- Generates a prompt based on current structure
- Expands a new encounter
- Tracks balance via `meta.json`

Fully reusable for any branching-character-variable narrative project.

## Diplomacy Storyworld Lab (NEW)

This repo now includes a minimal, deterministic diplomacy storyworld subsystem for inter-agent forecasting experiments.
The code lives under `storyworld/` and is separate from SweepWeave tooling.

### Directory Layout

- `storyworld/schema/`: JSON Schemas (`storyworld.schema.json`, `agent.schema.json`, `message.schema.json`)
- `storyworld/env/`: environment implementation (`diplomacy_env.py`)
- `storyworld/generators/`: tiny world generators
- `storyworld/validators/`: validation CLI
- `storyworld/examples/`: example storyworld JSON
- `storyworld/tools/`: agent hooks (generate, play, critique)

### Commands (run from repo root)

Validate a storyworld:
```
python storyworld/validators/validate_storyworld.py storyworld/examples/diplomacy_min.json
```

Generate a tiny diplomacy world (optionally validate):
```
python storyworld/tools/generate_storyworld.py --type tiny --seed 7 --out storyworld/examples/diplomacy_min.json --validate
```

Play a world with random actions (logs JSONL):
```
python storyworld/tools/play_storyworld.py --world storyworld/examples/diplomacy_min.json --steps 5 --log logs/diplomacy_run.jsonl
```

Critique a world (heuristic scores):
```
python storyworld/tools/critique_storyworld.py --world storyworld/examples/diplomacy_min.json
```

Summarize metrics from a play log (coalition stability, betrayal surprise, forecast scores):
```
python storyworld/tools/metrics_storyworld.py --log logs/diplomacy_run.jsonl
```

Gate a storyworld with critic thresholds:
```
python storyworld/tools/gate_storyworld.py --world storyworld/examples/diplomacy_min.json --min-richness 0.3 --min-manipulability 0.3 --min-forecast 0.3
```

Agent prompt templates:
- `storyworld/tools/agent_prompts.md`

### Logging

`play_storyworld.py` emits JSONL with `reset` and `step` events, including:
- actions
- forecasts
- confidences
- outcomes
- reasoning text

This is the logging surface for future HRM training, without implementing HRM yet.
