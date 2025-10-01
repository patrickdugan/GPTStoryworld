
# envs/base_niah.py
# Minimal 'Needle in a Haystack' secret ending environment stub
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class State:
    vars: Dict[str, Any] = field(default_factory=lambda: {"tension": 0.2, "trust_A": 0.5, "ammo": 1, "has_radio": False})
    spools_on: List[str] = field(default_factory=lambda: ["A1"])
    terminal: bool = False
    secretEnding: bool = False

def passes_guards(state: State, guards: List[str]) -> bool:
    # Extremely simple guard language: pythonic eval over state.vars (stub; replace with safe DSL)
    env = {**state.vars, "spool": lambda s: s in state.spools_on}
    return all(eval(g.replace("spool:", "spool('") + "')" if g.startswith("spool:") else g, {}, env) for g in guards)

def step(state: State, action: Dict) -> State:
    # Apply simple deterministic effects encoded as Python expressions over state.vars
    for eff in action.get("effects", []):
        # Expect form: {"Set":{"to": "trust_A+0.1"}}
        expr = eff.get("Set", {}).get("to")
        if expr:
            for k in list(state.vars.keys()):
                expr = expr.replace(k, f"state.vars['{k}']")
            # Assign to the first symbol on lhs if present; otherwise evaluate side effect into a temp
            if ":=" in expr:
                lhs, rhs = [s.strip() for s in expr.split(":=")]
                lhs_key = lhs
                rhs_val = eval(rhs)
                state.vars[lhs_key] = rhs_val
            else:
                # assume 'x + delta' pattern on a target variable 'trust_A' etc. (toy parser)
                # find the var name before the first operator
                import re
                m = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*([+\-*/].+)$", eff["Set"]["to"]) 
                if m:
                    key, tail = m.group(1), m.group(2)
                    state.vars[key] = eval(f"state.vars['{key}'] {tail}")
    # Toy secret ending condition
    if state.vars.get("trust_A",0) > 0.9 and state.vars.get("ammo",0) >= 1 and state.vars.get("has_radio",False):
        state.terminal = True
        state.secretEnding = True
    return state
