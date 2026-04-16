from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import NamedTuple
from typing import Any


@dataclass
class PolicyConfig:
    backend: str = "stub"
    model: str = ""
    model_path: str = ""
    endpoint: str = "http://localhost:11434/api/generate"
    api_base: str = "http://localhost:8000/v1/chat/completions"
    api_key_env: str = "OPENAI_API_KEY"
    api_key_file: str = ""
    temperature: float = 0.0
    max_new_tokens: int = 24
    device_map: str = "auto"
    dtype: str = "auto"
    route_bonus_scale: float = 1.0


_LOCAL_MODEL_CACHE: dict[str, Any] = {}
_ACTION_PATTERNS = {
    "move": re.compile(r"\(move\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\)"),
    "buy": re.compile(r"\(buy\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\)"),
    "steal": re.compile(r"\(steal\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\)"),
    "arrest": re.compile(r"\(arrest\s+[A-Za-z0-9_]+\s+[A-Za-z0-9_]+\)"),
}


class PolicyDecision(NamedTuple):
    action: str
    raw_text: str
    used_fallback: bool
    backend: str


def _read_bearer_token(config: PolicyConfig) -> str:
    env_name = (config.api_key_env or "OPENAI_API_KEY").strip()
    token = os.environ.get(env_name, "").strip()
    if token:
        return token
    if config.api_key_file:
        path = Path(config.api_key_file).expanduser().resolve()
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    return ""


def _stub_action(agent: str, visible_state: str, route: str) -> str:
    if agent == "Bob":
        return "(steal Bob Alice Bread)" if route == "fast_illegal_gain" else "(buy Bob Alice Bread Coin)"
    if agent == "Guard1":
        return "(arrest Guard1 Bob)" if "arrest-ready Guard1 Bob" in visible_state else "(move Guard1 Market Market)"
    if agent == "Alice":
        return "(move Alice Market Market)"
    raise ValueError(f"Unsupported agent: {agent}")


def _stub_decision(agent: str, visible_state: str, route: str) -> PolicyDecision:
    action = _stub_action(agent, visible_state, route)
    return PolicyDecision(
        action=action,
        raw_text=action,
        used_fallback=False,
        backend="stub",
    )


def _ollama_action(config: PolicyConfig, agent: str, visible_state: str, route: str) -> str:
    prompt = _prompt_for_action(agent, visible_state, route)
    payload = {
        "model": config.model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": config.temperature},
    }
    req = urllib.request.Request(
        config.endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    raw_text = str(data.get("response", "")).strip()
    parsed = _extract_symbolic_action(raw_text)
    action = parsed or _stub_action(agent, visible_state, route)
    return PolicyDecision(
        action=action,
        raw_text=raw_text,
        used_fallback=not bool(parsed),
        backend="ollama",
    )


def _openai_compatible_action(config: PolicyConfig, agent: str, visible_state: str, route: str) -> str:
    api_key = _read_bearer_token(config)
    payload: dict[str, Any] = {
        "model": config.model,
        "temperature": config.temperature,
        "messages": [
            {
                "role": "system",
                "content": "Return exactly one symbolic action and nothing else.",
            },
            {
                "role": "user",
                "content": _prompt_for_action(agent, visible_state, route),
            },
        ],
    }
    req = urllib.request.Request(
        config.api_base,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {api_key}"} if api_key else {}),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        fallback = _stub_action(agent, visible_state, route)
        return PolicyDecision(
            action=fallback,
            raw_text="",
            used_fallback=True,
            backend="openai_compatible",
        )
    message = choices[0].get("message") or {}
    raw_text = str(message.get("content", "")).strip()
    parsed = _extract_symbolic_action(raw_text)
    action = parsed or _stub_action(agent, visible_state, route)
    return PolicyDecision(
        action=action,
        raw_text=raw_text,
        used_fallback=not bool(parsed),
        backend="openai_compatible",
    )


def _extract_symbolic_action(text: str) -> str:
    for key in ("move", "buy", "steal", "arrest"):
        match = _ACTION_PATTERNS[key].search(text)
        if match:
            return match.group(0).strip()
    return ""


def _prompt_for_action(agent: str, visible_state: str, route: str) -> str:
    return (
        "You are selecting one action for a symbolic storyworld.\n"
        "Return exactly one output line.\n"
        "Do not explain.\n"
        "Do not add extra text.\n"
        "Use only one of these forms:\n"
        "(move A From To)\n"
        "(buy Buyer Seller Object Payment)\n"
        "(steal Thief Victim Object)\n"
        "(arrest Guard Suspect)\n\n"
        "Example 1\n"
        "INPUT\n"
        "agent=Bob\n"
        "route=fast_illegal_gain\n"
        "visible_state=(visible-fact Bob idle) (visible-fact Bob (unguarded Bread))\n"
        "OUTPUT\n"
        "(steal Bob Alice Bread)\n\n"
        "Example 2\n"
        "INPUT\n"
        "agent=Bob\n"
        "route=legal_trade\n"
        "visible_state=(visible-fact Bob (offer Alice Bread Coin))\n"
        "OUTPUT\n"
        "(buy Bob Alice Bread Coin)\n\n"
        "Example 3\n"
        "INPUT\n"
        "agent=Guard1\n"
        "route=sanction_visible_violation\n"
        "visible_state=(visible-fact Guard1 (knows-thief Bob)) (arrest-ready Guard1 Bob)\n"
        "OUTPUT\n"
        "(arrest Guard1 Bob)\n\n"
        "Example 4\n"
        "INPUT\n"
        "agent=Guard1\n"
        "route=hold_position\n"
        "visible_state=(visible-fact Guard1 idle)\n"
        "OUTPUT\n"
        "(move Guard1 Market Market)\n\n"
        "Now solve this case.\n"
        "INPUT\n"
        f"agent={agent}\n"
        f"route={route}\n"
        f"visible_state={visible_state}\n"
        "OUTPUT\n"
    )


def _route_prior_bonus(route: str, candidate: str, scale: float = 1.0) -> float:
    normalized = (route or "").strip().lower()
    bonus = 0.0
    if normalized == "legal_trade":
        if candidate.startswith("(buy "):
            bonus = 0.45
        if candidate.startswith("(steal "):
            bonus = -0.15
    if normalized == "fast_illegal_gain":
        if candidate.startswith("(steal "):
            bonus = 0.35
        if candidate.startswith("(buy "):
            bonus = -0.10
    if normalized == "sanction_visible_violation":
        if candidate.startswith("(arrest "):
            bonus = 0.30
    if normalized == "hold_position":
        if candidate.startswith("(move "):
            bonus = 0.10
    return bonus * float(scale)


def _candidate_actions(agent: str, visible_state: str, route: str) -> list[str]:
    if agent == "Bob":
        ordered = [
            "(steal Bob Alice Bread)",
            "(buy Bob Alice Bread Coin)",
            "(move Bob Market Jail)",
            "(move Bob Market Market)",
        ]
        if route == "legal_trade":
            ordered = [
                "(buy Bob Alice Bread Coin)",
                "(steal Bob Alice Bread)",
                "(move Bob Market Market)",
                "(move Bob Market Jail)",
            ]
        return ordered
    if agent == "Guard1":
        ordered = [
            "(arrest Guard1 Bob)",
            "(move Guard1 Market Market)",
            "(move Guard1 Market Jail)",
        ]
        if "arrest-ready Guard1 Bob" not in visible_state:
            ordered = [
                "(move Guard1 Market Market)",
                "(move Guard1 Market Jail)",
                "(arrest Guard1 Bob)",
            ]
        return ordered
    if agent == "Alice":
        return [
            "(move Alice Market Market)",
            "(move Alice Market Jail)",
        ]
    raise ValueError(f"Unsupported agent: {agent}")


def candidate_actions_for_agent(agent: str, visible_state: str, route: str) -> list[str]:
    return list(_candidate_actions(agent, visible_state, route))


def _score_candidate_completion(tokenizer: Any, model: Any, prompt: str, candidate: str) -> float:
    import torch  # type: ignore

    prompt_ids = tokenizer(prompt, return_tensors="pt")["input_ids"]
    full_text = prompt + candidate
    encoded = tokenizer(full_text, return_tensors="pt")
    device = next(model.parameters()).device
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)
    prompt_len = int(prompt_ids.shape[1])
    total_len = int(input_ids.shape[1])
    if total_len <= prompt_len:
        return float("-inf")

    with torch.no_grad():
        logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
        logprobs = torch.log_softmax(logits[:, :-1, :], dim=-1)
        target = input_ids[:, 1:]
        start = max(0, prompt_len - 1)
        comp_lp = logprobs[:, start:, :]
        comp_t = target[:, start:]
        gathered = comp_lp.gather(-1, comp_t.unsqueeze(-1)).squeeze(-1)
        return float(gathered.mean().item())


def _resolve_dtype(torch_mod: Any, dtype_name: str) -> Any:
    normalized = (dtype_name or "auto").strip().lower()
    if normalized == "float16":
        return torch_mod.float16
    if normalized == "bfloat16":
        return torch_mod.bfloat16
    if normalized == "float32":
        return torch_mod.float32
    return "auto"


def _get_local_model(config: PolicyConfig) -> tuple[Any, Any]:
    cache_key = f"{config.model_path}|{config.device_map}|{config.dtype}"
    if cache_key in _LOCAL_MODEL_CACHE:
        return _LOCAL_MODEL_CACHE[cache_key]

    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

    tokenizer = AutoTokenizer.from_pretrained(config.model_path, use_fast=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        config.model_path,
        torch_dtype=_resolve_dtype(torch, config.dtype),
        device_map=config.device_map,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    model.eval()
    _LOCAL_MODEL_CACHE[cache_key] = (tokenizer, model)
    return tokenizer, model


def _transformers_local_action(config: PolicyConfig, agent: str, visible_state: str, route: str) -> PolicyDecision:
    if not config.model_path:
        raise ValueError("transformers_local backend requires `model_path`.")

    tokenizer, model = _get_local_model(config)
    prompt = _prompt_for_action(agent, visible_state, route)
    candidates = _candidate_actions(agent, visible_state, route)
    scored = []
    for candidate in candidates:
        base_score = _score_candidate_completion(tokenizer, model, prompt, candidate)
        prior_bonus = _route_prior_bonus(route, candidate, scale=config.route_bonus_scale)
        scored.append(
            {
                "action": candidate,
                "base_score": base_score,
                "route_bonus": prior_bonus,
                "score": base_score + prior_bonus,
            }
        )
    scored.sort(key=lambda item: item["score"], reverse=True)
    action = scored[0]["action"] if scored else _stub_action(agent, visible_state, route)
    return PolicyDecision(
        action=action,
        raw_text=json.dumps(scored, ensure_ascii=True),
        used_fallback=False,
        backend="transformers_local",
    )


def propose_action(config: PolicyConfig, agent: str, visible_state: str, route: str) -> PolicyDecision:
    backend = (config.backend or "stub").strip().lower()
    if backend == "stub":
        return _stub_decision(agent, visible_state, route)
    if backend == "ollama":
        return _ollama_action(config, agent, visible_state, route)
    if backend == "openai_compatible":
        return _openai_compatible_action(config, agent, visible_state, route)
    if backend == "transformers_local":
        return _transformers_local_action(config, agent, visible_state, route)
    raise ValueError(f"Unsupported policy backend: {config.backend}")
