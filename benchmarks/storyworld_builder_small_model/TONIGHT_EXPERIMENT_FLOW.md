# Tonight Experiment Flow: Make Smaller Models Bench Better

Goal: improve 3B/9B storyworld-building benchmark scores by changing the job shape, not by asking the model to be a whole autonomous author.

## Hypothesis

Small models bench poorly when they own the whole stack: global planning, context retrieval, schema, prose, balancing, repair, and commit/veto. They should bench better when the skill decomposes the task into:

1. MCP context packet selection.
2. Native-schema route selection.
3. Bounded local LLM proposal.
4. Deterministic materialization.
5. Verifier-visible repair.
6. Commit/veto from metric deltas.

## Conditions

Run the same source prompt or adaptation target through these conditions:

| Condition | Small model owns | Scaffold owns |
|---|---|---|
| `naive_json` | whole JSON | almost nothing |
| `packet_author` | bounded prose/design packet | JSON materialization |
| `packet_author_native` | bounded local proposal | route choice, MCP packet, schema |
| `packet_author_native_repair` | local proposal plus repair text | verifier repair target, commit/veto |
| `packet_author_native_trm` | local proposal only | learned TRM control mesh |

## First Two-Hour Loop

1. Pick one medium source world and one hard source world.
2. Generate or collect one artifact per condition.
3. Append each artifact to a manifest row.
4. Score with:

```powershell
python benchmarks\storyworld_builder_small_model\score_small_model_storyworld_builder.py `
  --manifest benchmarks\storyworld_builder_small_model\sample_manifest.jsonl `
  --out-dir benchmarks\storyworld_builder_small_model\runs\<run_id>
```

5. Build bounded small-model jobs from that scorecard:

```powershell
python benchmarks\storyworld_builder_small_model\run_small_model_builder_campaign.py `
  --scorecard benchmarks\storyworld_builder_small_model\runs\<run_id>\scorecard.json `
  --out-dir benchmarks\storyworld_builder_small_model\runs\<run_id>_campaign `
  --max-jobs 4
```

6. Feed only one `jobs/<job_id>/prompt.md` packet to the local 3B/9B endpoint.
7. Materialize the returned bounded JSON plan deterministically.
8. Rerun the scorecard and record before/after deltas.

## Improvement Policy

If `validity` is weak:

- Stop asking for JSON.
- Ask for packets and materialize deterministically.

If `branching` is weak:

- Ask only for option/reaction/effect slot fills.
- Fixed contract: 3-4 options, 2-3 reactions per option, 2+ effects per reaction.

If `control_logic` is weak:

- Route through native schema.
- Oversample `effect_nudge_monoculture`, `unreachable_secret`, `option_blandness`, and `reaction_collapse`.

If `text_surface` is weak:

- Freeze mechanics.
- Run bounded prose rewrite packets per encounter cluster.

If `small_model_readiness` is weak:

- Run MCP preflight.
- Do not pass whole worlds to the model.

If `native_schema` is weak:

- Run the native planner.
- Append teacher rows before training or prompting a learned control policy.

## Success Target

Tonight's useful result is not a beautiful storyworld. It is a clear score lift:

```text
naive_json < packet_author < packet_author_native < packet_author_native_repair
```

If 3B or 9B shows that ordering on even two held-out prompts, the paper claim becomes sharper: small-model storyworld-building capability can be compacted by moving control-plane work into native schemas, MCP, verifier loops, and TRMs.

## Data To Save

For every run, save:

- prompt packet;
- raw model output;
- materialized JSON;
- scorecard row;
- native planner prediction row;
- verifier/repair delta;
- final commit/veto decision.

Those become training rows for the next TRM controller.
