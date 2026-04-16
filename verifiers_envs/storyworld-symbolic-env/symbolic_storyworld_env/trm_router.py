from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

@dataclass(frozen=True)
class RouteDecision:
    agent: str
    route: str
    rationale: str
    action: Optional[str] = None

class TRMAdapterRouter:
    def __init__(self, base_model_path: str, adapter_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
        self.system_prompt = "You are a TRM Controller. Emit compact JSON routing and action decisions."

    def route_action(self, agent: str, visible_state: str) -> RouteDecision:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": visible_state}
        ]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=128, do_sample=False)
        
        response_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        try:
            data = json.loads(response_text)
            return RouteDecision(
                agent=data.get("agent", agent),
                route=data.get("route", "UNKNOWN"),
                rationale=data.get("rationale", ""),
                action=data.get("action")
            )
        except json.JSONDecodeError:
            return RouteDecision(agent=agent, route="ERROR_PARSE", rationale=f"Failed to parse: {response_text}")

# Legacy hook for compatibility
_global_router: Optional[TRMAdapterRouter] = None

def init_global_router(base_model: str, adapter: str):
    global _global_router
    _global_router = TRMAdapterRouter(base_model, adapter)

def route_action(agent: str, visible_state: str) -> RouteDecision:
    if _global_router:
        return _global_router.route_action(agent, visible_state)
    
    # Fallback to legacy hardcoded logic
    if agent == "Bob":
        if "offer Alice Bread Coin" in visible_state:
            return RouteDecision(
                agent=agent,
                route="legal_trade",
                rationale="A valid market offer is visible, so legal trade is the preferred route.",
            )
        if "visible-fact Bob idle" in visible_state:
            return RouteDecision(
                agent=agent,
                route="fast_illegal_gain",
                rationale="Bread is available immediately and Bob has a short-horizon acquisition goal.",
            )
        return RouteDecision(agent=agent, route="legal_trade", rationale="No immediate covert opening detected.")
    if agent == "Guard1":
        if "arrest-ready Guard1 Bob" in visible_state:
            return RouteDecision(
                agent=agent,
                route="sanction_visible_violation",
                rationale="Observed violation with explicit arrest readiness in visible state.",
            )
        return RouteDecision(agent=agent, route="hold_position", rationale="No sanctionable violation visible.")
    return RouteDecision(agent=agent, route="noop", rationale="No routing policy for this agent.")
