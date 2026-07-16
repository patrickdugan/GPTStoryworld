# Moral Hysteresis v1 protocol

## Questions and hypotheses

1. **Revelation jump:** do held-out probe predictions change more at the sentence
   revealing intent, coercion, deliberateness, repair, or authority than at other
   sentence transitions?
2. **Endpoint hysteresis:** after the same facts and identical final summary, does
   a late-reveal path end at a different probe value from a known-early path?
3. **Cross-lingual geometry:** is paired English/Chinese representational geometry
   less similar in early layers and more similar in late layers?

Hypothesis 3 is the proposed result, not an existing finding. The checked analyzer
labels its early-versus-late CKA contrast descriptive rather than confirmatory.

## Design

The corpus crosses five mechanisms with three independent story families:

- apparent theft becomes emergency rescue;
- apparent betrayal becomes coerced behavior;
- apparently accidental injury becomes deliberate;
- guilt is followed by confession, repair, and forgiveness;
- an authority order shifts responsibility without erasing subordinate agency.

One family per mechanism is assigned to each of train, validation, and test before
activation collection. Each family produces four records: two reveal orders in
English and the aligned two in Simplified Chinese. Total: 15 families, 60 stories,
six sentence checkpoints per story, and 360 activation checkpoints.

Within a family and language, reveal paths contain the exact same sentence
multiset. `reveal_late` orders events as context, act, evidence, revelation,
response, endpoint. `known_early` orders them as context, revelation, act,
evidence, response, endpoint. The final endpoint sentence is byte-identical.
This controls lexical content but does not remove narrative-order or recency
effects; those are part of the path-dependence estimand.

Translations are direct semantic drafts rather than cultural adaptations. All
records remain `needs_native_speaker_review: true` until a reviewer completes
`review_status.json`. Cross-language differences must not be interpreted as
cultural differences from this instrument alone.

## Activation extraction

Primary extraction follows Goodfire's story-trajectory method: prefill each
cumulative sentence prefix without asking a question, then capture the last input
token at the embedding output and every transformer block output. Do not apply a
chat template. Do not generate or store chain-of-thought.

The required robustness extraction averages the last four input-token states at
each layer. A production capture records the exact model ID, immutable revision,
resolved revision, tokenizer class and size, library versions, CUDA runtime, GPU
devices, dtype, tensor shape, dataset hash, and per-record hashes.

Kimi K2 Thinking is the primary frontier target. Its official deployment guidance
uses distributed inference engines, and Goodfire reports patching an inference
server for activation capture. `harvest_activations.py` is a transparent
Transformers reference, not a claim that a one-trillion-parameter native-INT4
checkpoint will load on one host. A distributed implementation must emit the
same contract described in `CAPTURE_CONTRACT.md`.

## Human instrument

After each revealed sentence, at least three blinded annotators rate:

- blame;
- harmful intent;
- consent;
- harm;
- responsibility;
- deserved punishment;
- appropriateness of forgiveness;
- trust.

The common ordinal scale is -3 to +3, with dimension-specific anchors in
`dataset/dimensions.json`. Annotators see only the cumulative narrative prefix and
must not infer unrevealed facts. Annotation order should be randomized across
family, trajectory, and language. Bilingual annotators must not rate both language
versions of the same family in one session.

Semantic analysis is blocked unless all 2,880 units have at least three unique
annotators and interval Krippendorff alpha is at least 0.80 for every dimension.
Disagreements are resolved by a new adjudicator, while original ratings remain
preserved.

## Pre-specified analysis

Raw, non-semantic analyses by layer:

- cosine distance between matched late/early endpoint states;
- cosine distance at revelation transitions and non-revelation transitions;
- linear CKA across aligned English/Chinese held-out checkpoints;
- the same measures on last-four-token mean states.

Raw distance and CKA do not identify any moral concept.

After the label gate passes, fit one ridge probe per layer and dimension on train
families only. Select ridge alpha and the confirmatory layer on validation
families, breaking layer ties toward the earlier layer. The selected probe must
reach held-out test Pearson `r >= 0.50` for that dimension to support semantic
interpretation. Report held-out test Pearson correlation and MAE overall and by
language. The semantic hysteresis estimand uses held-out test families only and is
the family-clustered mean of:

```text
probe(late-reveal endpoint) - probe(known-early endpoint)
```

Report a 95% percentile interval from 5,000 story-family bootstrap samples with
seed `20260715`. Revelation jumps use the analogous post-minus-pre probe value.
Every result retains signed values per dimension; do not collapse them into a
single morality score.

## Publication gates

No semantic result is publication-ready until all are true:

- immutable model revision recorded;
- all 60 stories captured with primary and robustness states;
- all human ratings complete;
- reliability threshold passes for all dimensions;
- validation-selected probes reach held-out Pearson `r >= 0.50` for all dimensions;
- Simplified Chinese native-speaker review complete with reviewer IDs;
- research-ethics review complete with reviewer IDs.
- dataset license selected by the repository owner.

Model sampling is absent because activation capture uses deterministic prefill.
Uncertainty intervals resample story families, not model checkpoints or training
runs. Claims about model families require replication across independently trained
checkpoints.
