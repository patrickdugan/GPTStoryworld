---
name: storyworld-building
description: Storyworld building and editing for GPTStoryworld/SweepWeave content. Use when creating or modifying storyworld JSON, spools, encounters, options, reactions, secret logic, balancing, or running the bundled SweepWeave tools/validators.
---

# Storyworld Building

## Overview
Use this skill to build, edit, and validate SweepWeave storyworld content with the bundled scripts and task prompts.

## Quick Start
- Prefer running the specific tool in `scripts/` for the task instead of manual edits.
- When editing storyworld JSON, validate with `scripts/sweepweave_validator.py` before and after changes.

## Task Prompts (references/)
Load the matching task file when the user requests one of these actions, then follow it verbatim:
- New encounter: `references/task_new_encounter.md`
- Add options: `references/task_add_options.md`
- Add reactions: `references/task_add_reactions.md`
- Add effects: `references/task_add_effects.md`
- Add secret logic: `references/task_add_secret_logic.md`
- Materialize spools: `references/task_materialize_spools.md`
- Spool sequencing: `references/task_spool_sequencing.md`
- Tune ending gates: `references/task_tune_ending_gates.md`
- Monte Carlo balance: `references/task_monte_carlo_balance.md`

## Core Scripts (scripts/)
Use these tools to make deterministic, validated edits:
- `new_encounter.py`, `add_options.py`, `add_reactions.py`, `add_effects.py`, `add_secret_logic.py`
- `materialize_spools.py`, `repair_connected_spools.py`, `spool_sequencing.py`
- `monte_carlo_rehearsal.py`
- `sweepweave_validator.py` (authoritative contract for JSON validity)

## References
- `references/STORYWORLD_BALANCING.md` for balancing targets/heuristics
- `references/Storyworld.gd` for engine-side expectations
- `references/meta-calc.js` for calculation logic

## Validation Rule
Never bypass `scripts/sweepweave_validator.py` when the task touches storyworld JSON.
