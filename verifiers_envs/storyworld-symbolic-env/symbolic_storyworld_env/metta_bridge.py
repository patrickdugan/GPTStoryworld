from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile


ENV_ROOT = Path(__file__).resolve().parents[1]
WORLD_FILES = [
    "world/ontology.metta",
    "world/initial_state.metta",
    "world/scenarios/market_square.metta",
    "world/norms.metta",
    "world/affordances.metta",
    "world/endings.metta",
    "rules/movement.metta",
    "rules/commerce.metta",
    "rules/social.metta",
    "rules/observation.metta",
    "rules/sanctions.metta",
    "engine/visibility.metta",
    "engine/scoring.metta",
    "engine/queries.metta",
    "engine/step.metta",
]


@dataclass
class MettaRunResult:
    ok: bool
    returncode: int
    stdout: str
    stderr: str
    note: str


def discover_metta_bin(explicit: str = "") -> str:
    if explicit:
        return explicit
    return shutil.which("metta") or shutil.which("metta-py") or ""


def build_world_script() -> str:
    parts: list[str] = []
    for rel_path in WORLD_FILES:
        full_path = ENV_ROOT / rel_path
        parts.append(f"; BEGIN {rel_path}")
        parts.append(full_path.read_text(encoding="utf-8").rstrip())
        parts.append(f"; END {rel_path}")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def build_episode_script(actions: list[str]) -> str:
    lines = [build_world_script(), ""]
    for action in actions:
        actor = action.split()[1]
        lines.append(f"!(step-world {actor} {action})")
    return "\n".join(lines) + "\n"


def run_script(script: str, metta_bin: str = "") -> MettaRunResult:
    resolved = discover_metta_bin(metta_bin)
    if not resolved:
        return MettaRunResult(
            ok=False,
            returncode=-1,
            stdout="",
            stderr="",
            note="No `metta` CLI found. Replay script exported only.",
        )
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".metta",
        dir=ENV_ROOT,
        encoding="utf-8",
        delete=False,
    ) as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        proc = subprocess.run(
            [resolved, str(script_path)],
            text=True,
            capture_output=True,
            cwd=ENV_ROOT,
            check=False,
        )
    finally:
        script_path.unlink(missing_ok=True)
    return MettaRunResult(
        ok=proc.returncode == 0,
        returncode=proc.returncode,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
        note="MeTTa runtime executed." if proc.returncode == 0 else "MeTTa runtime returned a nonzero exit code.",
    )
