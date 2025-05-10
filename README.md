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
