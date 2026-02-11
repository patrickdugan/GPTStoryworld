# Storyworld Text Quality Env

Judge-and-revise loop for storyworld text quality using an OpenAI model as evaluator.

## Files
- `storyworld_system_card.md`: rollout/system contract.
- `judge_system_prompt.md`: strict scoring prompt for judge model.
- `evaluate_text_quality.py`: one-shot judge run.
- `iterate_text_quality_loop.py`: iterative revise-until-threshold loop.

## Quick Start
```powershell
python storyworld-text-quality-env/evaluate_text_quality.py `
  --storyworld C:\projects\GPTStoryworld\storyworlds\gone_with_the_flux_capacitor_v6_textgate.json `
  --judge-model gpt-5-mini `
  --out C:\projects\GPTStoryworld\logs\text_quality\gone_v6_judge.json
```

Iterative loop:
```powershell
python storyworld-text-quality-env/iterate_text_quality_loop.py `
  --in-json C:\projects\GPTStoryworld\storyworlds\gone_with_the_flux_capacitor_v6_textgate.json `
  --out-json C:\projects\GPTStoryworld\storyworlds\gone_with_the_flux_capacitor_v7_textloop.json `
  --threshold 0.8 `
  --max-iters 4 `
  --judge-model gpt-5-mini `
  --writer-model gpt-5-mini `
  --work-dir C:\projects\GPTStoryworld\logs\text_quality\gone_v7_loop
```

## API Key
Lookup order:
1. `OPENAI_API_KEY`
2. `--api-key-file`
3. `%USERPROFILE%\Desktop\GPTAPI.txt`

## Notes
- Use `--dry-run` for offline smoke tests (heuristic scoring only).
- Loop only rewrites encounter/reaction text fields; IDs and mechanics are preserved.
