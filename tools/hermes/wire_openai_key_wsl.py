from pathlib import Path
import re

home = Path.home()
cands = [
    Path("/mnt/c/Users/patri/OneDrive/Desktop/GPTAPI.txt"),
    Path("/mnt/c/Users/patri/Desktop/GPTAPI.txt"),
]
key = None
for p in cands:
    if p.exists():
        for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = ln.strip()
            if s:
                key = s
                break
    if key:
        break
if not key:
    raise SystemExit("GPTAPI.txt key not found or empty")

env_path = home / ".hermes" / ".env"
env_path.parent.mkdir(parents=True, exist_ok=True)
lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines() if env_path.exists() else []

updates = {
    "OPENAI_API_KEY": key,
    "OPENAI_BASE_URL": "https://api.openai.com/v1",
    "OPENROUTER_API_KEY": "",
    "LLM_MODEL": "gpt-4.1-mini",
}

seen = {k: False for k in updates}
out = []
for ln in lines:
    m = re.match(r"^([A-Z0-9_]+)=(.*)$", ln)
    if m and m.group(1) in updates:
        k = m.group(1)
        out.append(f"{k}={updates[k]}")
        seen[k] = True
    else:
        out.append(ln)
for k, done in seen.items():
    if not done:
        out.append(f"{k}={updates[k]}")
env_path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

cfg_path = home / ".hermes" / "config.yaml"
cfg = cfg_path.read_text(encoding="utf-8", errors="ignore")

cfg = re.sub(
    r"(?ms)^model:\n(?:  .*\n)+",
    "model:\n  default: gpt-4.1-mini\n  provider: custom\n  base_url: https://api.openai.com/v1\n",
    cfg,
    count=1,
)

if re.search(r"(?m)^compression:\n", cfg):
    if re.search(r"(?m)^  summary_provider:\s*", cfg):
        cfg = re.sub(r"(?m)^  summary_provider:\s*.*$", "  summary_provider: main", cfg)
    else:
        cfg = cfg.replace("compression:\n", "compression:\n  summary_provider: main\n", 1)
    if re.search(r"(?m)^  summary_model:\s*", cfg):
        cfg = re.sub(r"(?m)^  summary_model:\s*.*$", "  summary_model: gpt-4.1-mini", cfg)
    else:
        cfg = cfg.replace("compression:\n", "compression:\n  summary_model: gpt-4.1-mini\n", 1)

if "auxiliary:" not in cfg:
    cfg += (
        "\nauxiliary:\n"
        "  vision:\n"
        "    provider: main\n"
        "    model: gpt-4.1-mini\n"
        "  web_extract:\n"
        "    provider: main\n"
        "    model: gpt-4.1-mini\n"
    )

cfg_path.write_text(cfg, encoding="utf-8")
