# Hermes Optional Skill PR Checklist

Target upstream:
- `https://github.com/NousResearch/hermes-agent`

Target folder in upstream repo:
- `optional-skills/pure-trm-trainer/`

Recommended flow:
1. Fork `NousResearch/hermes-agent`.
2. Create a branch in the fork.
3. Copy this package into `optional-skills/pure-trm-trainer/`.
4. Keep only the skill payload and supporting docs/scripts.
5. Open a PR against upstream `main`.

What should be present:
- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`

What should not be present:
- generated run artifacts
- local caches
- `runs/`
- `__pycache__/`
- `.pyc` files

After merge:
- announce the repo slug or upstream PR in the Nous Research Discord
- users can install it with the Hermes skill install command once the upstream path is approved
