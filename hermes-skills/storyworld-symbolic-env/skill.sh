#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CONFIG_PATH="${1:-${REPO_ROOT}/verifiers_envs/storyworld-symbolic-env/examples/hermes_storyworld_config.json}"

python "${REPO_ROOT}/verifiers_envs/storyworld-symbolic-env/symbolic_storyworld_env/hermes_storyworld.py" --config "${CONFIG_PATH}"
