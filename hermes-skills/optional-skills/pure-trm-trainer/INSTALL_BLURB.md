# Install Blurb

## Short version

Install the optional TRM trainer skill from the approved Hermes source once it is published.

## Example

```bash
hermes skills install <publisher>/pure-trm-trainer
```

## What it gives you

- TRM corpus assembly guidance
- Hermes-wrapped trainer launch flow
- generalization-level hill-climbing
- compact scorecard evaluation
- smoke wrapper for quick checks

## What it does not do

- it does not bundle prose authoring
- it does not bundle adapter generation
- it does not collect hidden chain-of-thought

## Maintenance note

If the skill is installed from an external registry or GitHub tap, keep the installed source aligned with the upstream `optional-skills/pure-trm-trainer/` package so the docs and scripts stay synchronized.
