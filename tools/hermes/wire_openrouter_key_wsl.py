from pathlib import Path
import re

home = Path.home()

def first_line(path: Path):
    if not path.exists():
        return ""
    for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = ln.strip()
        if s:
            return s
    return ""

or_key = (
    first_line(Path("/mnt/c/Users/patri/OneDrive/Desktop/Hermes.txt"))
    or first_line(Path("/mnt/c/Users/patri/Desktop/Hermes.txt"))
)
if not or_key:
    raise SystemExit("Hermes.txt key not found or empty")

env_path = home / ".hermes" / ".env"
env_path.parent.mkdir(parents=True, exist_ok=True)
lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines() if env_path.exists() else []

updates = {
    "OPENROUTER_API_KEY": or_key,
    "OPENAI_BASE_URL": "",
    "LLM_MODEL": "qwen/3.5-35b-a3b",
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
    "model:\n  default: qwen/3.5-35b-a3b\n  provider: openrouter\n  base_url: https://openrouter.ai/api/v1\n",
    cfg,
    count=1,
)

# Keep auxiliary/compression pinned to main model path to avoid Nous fallback chatter.
if re.search(r"(?m)^compression:\n", cfg):
    if re.search(r"(?m)^  summary_provider:\s*", cfg):
        cfg = re.sub(r"(?m)^  summary_provider:\s*.*$", "  summary_provider: main", cfg)
    else:
        cfg = cfg.replace("compression:\n", "compression:\n  summary_provider: main\n", 1)
    if re.search(r"(?m)^  summary_model:\s*", cfg):
        cfg = re.sub(r"(?m)^  summary_model:\s*.*$", "  summary_model: qwen/3.5-35b-a3b", cfg)
    else:
        cfg = cfg.replace("compression:\n", "compression:\n  summary_model: qwen/3.5-35b-a3b\n", 1)

if "auxiliary:" in cfg:
    cfg = re.sub(
        r"(?ms)^auxiliary:\n(?:  .*\n)+",
        "auxiliary:\n  vision:\n    provider: main\n    model: qwen/3.5-35b-a3b\n  web_extract:\n    provider: main\n    model: qwen/3.5-35b-a3b\n",
        cfg,
        count=1,
    )
else:
    cfg += (
        "\nauxiliary:\n"
        "  vision:\n"
        "    provider: main\n"
        "    model: qwen/3.5-35b-a3b\n"
        "  web_extract:\n"
        "    provider: main\n"
        "    model: qwen/3.5-35b-a3b\n"
    )

cfg_path.write_text(cfg, encoding="utf-8")
