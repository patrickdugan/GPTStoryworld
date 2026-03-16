---
name: storyworld-batch-auditor
description: Audit failed or suspicious storyworld conveyor runs by checking manifests, row counts, missing files, and stage-local artifacts before rerunning only the failed stage.
---

# Storyworld Batch Auditor

Use this skill when a conveyor run failed, stalled, or produced suspicious claims.

## Audit Order
1. Locate the run directory.
2. Check every stage folder for:
   - `manifest.json`
   - `progress.json`
   - `events.jsonl`
3. Compare manifest counters to actual JSONL row counts.
4. Stop at the first broken stage and report:
   - stage name
   - missing or mismatched files
   - exact rerun command

## What To Trust
- Trust on-disk artifacts only.
- Ignore any prior narrative success claim if counts or manifests disagree.

## Canonical Audit Questions
- Is there a manifest?
- Is status `completed`?
- Do output files exist?
- Do JSONL row counts match manifest counters?
- Did a later stage start without an earlier stage completing?

## Recovery Rule
- Rerun only the failed stage unless an upstream artifact is corrupt.
