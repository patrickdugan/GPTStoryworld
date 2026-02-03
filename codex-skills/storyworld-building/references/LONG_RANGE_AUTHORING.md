# Long-Range Authoring Loop

Use this when you want to keep iterating on a storyworld without re-prompting.
It produces a checklist and suggested edits based on Monte Carlo output and
basic structural heuristics.

## Inputs
- Storyworld JSON path
- Monte Carlo runs (>= 5000)
- Optional target distribution ranges

## Loop Outline
1. Validate JSON
2. Run Monte Carlo
3. Identify endings outside target ranges
4. Propose small tuning adjustments (gates, desirability, or effect magnitudes)
5. Re-run Monte Carlo and repeat until targets satisfied
6. Emit a short report for the work log

## Target Defaults
- Dead-end rate < 5%
- No ending > 30%
- All endings > 1%
- Late-game gate blocking 10-30%

## Output
Write a report and suggested edits to a markdown file next to the storyworld:
`<storyworld>_long_range_authoring.md`
