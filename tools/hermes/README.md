# Hermes + Storyworld Hackathon Bootstrap

This folder sets up `hermes-agent` in WSL2 and wires your API key into WSL for storyworld scripts.

## 1) One-command bootstrap (from PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\hermes\bootstrap_hermes_wsl.ps1
```

Optional flags:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\hermes\bootstrap_hermes_wsl.ps1 `
  -KeyFile "$env:USERPROFILE\OneDrive\Desktop\Hermes.txt" `
  -Distro Ubuntu
```

The script searches key files in this order if `-KeyFile` is not provided:
- `%USERPROFILE%\Desktop\Hermes\OPENAI_API_KEY.txt`
- `%USERPROFILE%\Desktop\Hermes\api_key.txt`
- `%USERPROFILE%\Desktop\Hermes.txt`
- `%USERPROFILE%\Desktop\GPTAPI.txt`

## 2) Verify in WSL

```bash
echo "$OPENAI_API_KEY" | sed 's/./*/g'
```

## 3) Run GPTStoryworld pipeline from WSL

```bash
cd /mnt/c/projects/GPTStoryworld

python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/by-week/YYYY-Www/world.json

python codex-skills/storyworld-building/scripts/storyworld_quality_gate.py \
  --storyworld storyworlds/by-week/YYYY-Www/world.json \
  --strict \
  --report-out logs/quality_report.json

python verifiers_envs/storyworld-text-quality-env/evaluate_text_quality.py \
  --storyworld storyworlds/by-week/YYYY-Www/world.json \
  --judge-model gpt-4.1-mini \
  --out logs/text_judge.json
```

## Security notes
- Do not commit key files or generated logs that contain secrets.
- Key is stored in WSL at `~/.config/hermes/openai_api_key` with `chmod 600`.
- Auto-export is added to `~/.profile` for login-shell compatibility (`bash -lc`).
