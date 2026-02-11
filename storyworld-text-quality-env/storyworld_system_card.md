# Storyworld Text Quality Env System Card

## Purpose
This environment evaluates and improves **story text quality** for SweepWeave storyworlds.
It is designed to score encounter/reaction writing quality and run iterative revision loops.

## Scope
- Input: one storyworld JSON file.
- Output: quality report JSON with dimension scores and actionable revision instructions.
- Optional loop: apply model-authored rewrites until a target score threshold is reached.

## Non-Goals
- Does not alter graph structure, consequences, or authored mechanics by default.
- Does not replace structural validators in `storyworld-env`.

## Scoring Dimensions (0-1 each)
- thematic_relevance
- stylistic_distinctiveness
- encounter_narrative_quality
- reaction_voice_quality
- specificity_and_imagery
- coherence_and_consistency
- non_repetition
- choice_consequence_clarity

## Overall Score
Weighted mean of dimensions, expected in `[0.0, 1.0]`.

## Safety and Constraints
- Preserve world intent and IDs.
- No secret leakage or policy-violating content insertion.
- Keep revisions grounded in provided world context.
- Favor minimal edits that improve quality signal.

## Intended Workflow
1. Run judge.
2. If score < threshold, generate text rewrite patch.
3. Apply rewrites.
4. Re-judge.
5. Stop when threshold reached or max iterations hit.
