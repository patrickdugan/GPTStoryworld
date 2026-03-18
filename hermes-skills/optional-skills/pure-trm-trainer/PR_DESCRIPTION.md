# PR Description

## Summary

Add `pure-trm-trainer` as an official optional Hermes skill for pure TRM controller workflows.

This skill is intentionally narrow:
- corpus assembly from TRM play logs and event logs
- Hermes-wrapped TRM trainer launches
- hill-climbing over generalization level
- compact scorecard evaluation
- no prose generation
- no adapter authoring

## Why this belongs in `optional-skills/`

`pure-trm-trainer` is useful for a specific class of Hermes users, but it is not universal enough to bundle in core `skills/`.

The skill is better maintained as an official optional package because it:
- stays available through Hermes
- avoids bloating the default install
- keeps the TRM workflow discoverable for advanced users

## Included files

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `PR_CHECKLIST.md`

## Runtime behavior

The skill provides:
- a hill-climb runner over generalization ladder levels
- a local scorecard evaluator fallback
- a smoke wrapper for one-command invocation
- a publish-path note for community versus official distribution

## Validation

The package has been syntax-checked locally and the smoke runner was exercised in dry-run mode.

## Upstream placement

Place this folder at:

`optional-skills/pure-trm-trainer/`

in a fork of `NousResearch/hermes-agent`, then open a PR against upstream `main`.
