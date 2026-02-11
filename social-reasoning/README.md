# Social Reasoning Pack (v0, 2026-02-05)

This folder is a bounded draft pack for N-agent social reasoning in Diplomacy-style storyworlds.

It is aligned to:
- `C:\projects\GPTStoryworld\codex-chat-sessions` reasoning threads.
- `C:\projects\AI_Diplomacy` archetypes and harness context.
- The `storyworld-building` skill guidance (especially pValue/p2Value keyrings and desirability/effect coupling).

## Goals of this pack

1. Provide a concrete 3-agent pValue/p2Value manifold model.
2. Enumerate game-theory pattern structures for coalition/defection/betrayal/isolation/death-ground dynamics.
3. Bundle relevant papers locally for reuse by other agents.
4. Keep structure simple enough to map into storyworld encounter DAGs.

## Folder map

- `models/pvalue_manifold_3_agents.md`: Mathematical framing and update rules.
- `models/pvalue_3agent_sim.py`: Small executable prototype for state updates and action scoring.
- `notes/game_theory_pattern_library.md`: Pattern list and decision hooks.
- `notes/historical_alliance_lessons.md`: Historical mapping notes for alliance failure and commitment regimes.
- `notes/local_context_extract.md`: Key points extracted from local session logs and repo assets.
- `papers/arxiv/`: Downloaded open papers (PDF).
- `papers/local/`: Local PDFs copied from current repos.
- `papers/paper_index.csv`: Indexed paper metadata.
- `papers/external_links.md`: Non-mirrored external references.
- `scripts/fetch_papers.ps1`: Reproducible downloader for the arXiv subset.
- `scripts/generate_storyworld_templates.py`: Emits reusable desirability/effect template fragments for coalition, defection, and betrayal options.
- `scripts/score_pp2_snapshot.py`: Scores coalition/defection/betrayal probabilities from a p/p2 snapshot.

## Skill integration notes

From `storyworld-building` skill guidance:
- pValues are represented with keyrings of length 2: `[property_id, perceived_character_id]`.
- p2Values are represented with keyrings of length 3: `[property_id, perceived_character_id, target_character_id]`.

This pack assumes those keyring conventions directly in desirability scripts and after-effects.

## Quick usage

Generate reusable template fragments:

```powershell
python scripts\generate_storyworld_templates.py --actor power_france --target power_germany --witness power_england --out templates\france_germany_fragments.json
```

Score a p/p2 snapshot:

```powershell
python scripts\score_pp2_snapshot.py --snapshot examples\snapshot_3agents.json --out outputs\snapshot_3agents_score.json
```

Snapshot format (nested maps):

```json
{
  "agents": ["A", "B", "C"],
  "p": {
    "A": {"B": {"loyalty": 0.62, "reciprocity": 0.58, "risk_tolerance": 0.41}}
  },
  "p2": {
    "A": {"B": {"A": {"promise_keeping": 0.56}, "C": {"promise_keeping": 0.48}}}
  }
}
```

## Existing archetype compatibility

The pattern naming in this pack is intentionally compatible with existing bank entries in:
`C:\projects\AI_Diplomacy\ai_diplomacy\storyworld_bank`
(including `coalition_compact`, `backstab_first`, `common_enemy`, `deterrent_signal`, `insurance_alliance`, `tit_for_tat`, `grudger_memory`, and related variants).
