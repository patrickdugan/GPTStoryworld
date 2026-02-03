#!/usr/bin/env python3
"""Base helpers for Diplomacy Storyworld environments."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict


class StoryworldEnvBase:
    def reset(self, seed: int | None = None) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError

    def step(self, actions, messages):  # pragma: no cover - interface
        raise NotImplementedError


def load_storyworld(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def deep_copy_state(state: Dict[str, Any]) -> Dict[str, Any]:
    return copy.deepcopy(state)
