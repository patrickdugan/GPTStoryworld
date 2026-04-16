---
name: storyworld-symbolic-env
description: Run a Hermes-style symbolic storyworld environment using a local Qwen policy adapter, MeTTa replay engine, JSONL traces, and a deferred offline judge hook.
---

# Storyworld Symbolic Env

Use this when the user wants a real environment-shaped storyworld experiment rather than a pure text grader.

## What This Skill Launches

- local Qwen policy shell: `stub`, `ollama`, or `openai_compatible`
- Hermes orchestration wrapper
- MeTTa replay engine
- JSONL trace export
- grading overlay
- offline judge placeholder

## Commands

- Smoke run:
  - `python verifiers_envs/storyworld-symbolic-env/symbolic_storyworld_env/hermes_storyworld.py --config verifiers_envs/storyworld-symbolic-env/examples/hermes_storyworld_config.json`
- Test:
  - `python -m unittest verifiers_envs/storyworld-symbolic-env/tests/test_symbolic_smoke.py`

## Notes

- Treat the storyworld as an env kernel first and a grader second.
- Keep `secret endings` as trajectory classes, not magic-phrase easter eggs.
- Use the JSONL trajectory as the handoff artifact for later offline judging and TRM corpus assembly.
