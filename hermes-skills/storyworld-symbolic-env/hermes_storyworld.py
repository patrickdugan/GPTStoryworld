from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Thin Hermes wrapper for the symbolic storyworld env.")
    parser.add_argument(
        "--config",
        default="",
        help="Config path. Defaults to the sample symbolic storyworld config.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    config_path = (
        Path(args.config).resolve()
        if args.config
        else repo_root / "verifiers_envs" / "storyworld-symbolic-env" / "examples" / "hermes_storyworld_config.json"
    )
    command = [
        sys.executable,
        str(
            repo_root
            / "verifiers_envs"
            / "storyworld-symbolic-env"
            / "symbolic_storyworld_env"
            / "hermes_storyworld.py"
        ),
        "--config",
        str(config_path),
    ]
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
