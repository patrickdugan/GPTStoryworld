#!/usr/bin/env python3
from __future__ import annotations

import argparse
import inspect
import json
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from wiki_card_mcp_server import WikiCardIndex, infer_relation_hint, question_prefers_relation


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"[A-Za-z0-9_]+", str(text))))


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9 ]+", " ", str(text).lower())).strip()


def compact_answer(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r'"answer"\s*:\s*"([^"]+)"', raw, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if raw.startswith("{") and raw.endswith("}"):
        try:
            payload = json.loads(raw)
        except Exception:
            payload = None
        if isinstance(payload, dict):
            value = str(payload.get("answer", "") or "").strip()
            if value:
                return value
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    answer = lines[0] if lines else raw
    answer = re.sub(r"^(answer|final answer)\s*:\s*", "", answer, flags=re.IGNORECASE)
    answer = answer.strip().strip("\"'")
    return answer


def evaluate_answer(question_row: Dict[str, Any], prediction: str) -> Dict[str, Any]:
    answer = str(question_row.get("answer", "") or "").strip()
    aliases = [answer]
    aliases.extend(str(item) for item in question_row.get("answer_aliases", []) if str(item).strip())
    normalized_prediction = normalize_text(prediction)
    for alias in aliases:
        normalized_alias = normalize_text(alias)
        if normalized_prediction and normalized_prediction == normalized_alias:
            return {"correct": True, "match_type": "exact", "normalized_prediction": normalized_prediction}
    for alias in aliases:
        normalized_alias = normalize_text(alias)
        if not normalized_alias:
            continue
        if normalized_prediction and (
            normalized_alias in normalized_prediction or normalized_prediction in normalized_alias
        ):
            return {"correct": True, "match_type": "alias_contains", "normalized_prediction": normalized_prediction}
    return {"correct": False, "match_type": "miss", "normalized_prediction": normalized_prediction}


def parse_router_json(text: str) -> Dict[str, Any]:
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first >= 0 and last >= first:
        try:
            payload = json.loads(cleaned[first : last + 1])
        except Exception:
            payload = {}
        return payload if isinstance(payload, dict) else {}
    return {}


def score_relation_choice(question_text: str, key: str, value: Any) -> float:
    question_tokens = re.findall(r"[A-Za-z0-9_]+", str(question_text).lower())
    key_tokens = re.findall(r"[A-Za-z0-9_]+", str(key).replace("_", " ").lower())
    value_tokens = re.findall(r"[A-Za-z0-9_]+", str(value).lower())
    score = 3.0 * float(sum(1 for token in question_tokens if token in key_tokens))
    score += 1.0 * float(sum(1 for token in question_tokens if token in value_tokens))
    normalized_key = " ".join(key_tokens)
    if normalized_key and normalized_key in " ".join(question_tokens):
        score += 4.0
    return score


def build_router_messages(question_row: Dict[str, Any], route_plan: Dict[str, Any]) -> List[Dict[str, str]]:
    question_text = str(question_row.get("question", "") or "")
    actions = []
    for row in route_plan.get("actions", []):
        if not isinstance(row, dict):
            continue
        actions.append(
            {
                "action_id": row.get("action_id"),
                "namespace": row.get("namespace"),
                "tool": row.get("tool"),
                "args": row.get("args"),
                "label": row.get("label"),
            }
        )
    alias_hits = []
    for row in route_plan.get("alias_hits", [])[:4]:
        if not isinstance(row, dict):
            continue
        alias_hits.append(
            {
                "entity_id": row.get("entity_id"),
                "surface": row.get("surface"),
                "surface_type": row.get("surface_type"),
            }
        )
    relation_hits = []
    for row in route_plan.get("relation_hits", [])[:4]:
        if not isinstance(row, dict):
            continue
        relation_hits.append(
            {
                "entity_id": row.get("entity_id"),
                "relation": row.get("relation"),
                "value": row.get("value"),
            }
        )
    system = (
        "You are a tiny retrieval router. Return exactly one JSON object and nothing else. "
        "Choose exactly one action_id from the provided actions. "
        "Prefer relation actions when the question asks for a fact value. "
        "Prefer entity actions when the question is identifying the entity itself from a description. "
        "Choose ctl::escalate only if the listed actions are clearly insufficient."
    )
    payload = {
        "q": question_text,
        "type_hint": route_plan.get("type_hint", "entity"),
        "relation_hint": route_plan.get("relation_hint", ""),
        "namespaces": route_plan.get("namespaces", []),
        "alias_hits": alias_hits,
        "relation_hits": relation_hits,
        "actions": actions,
        "output": {"action_id": "one_of_listed_actions"},
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, separators=(",", ":"))},
    ]


def compact_evidence_for_prompt(evidence: Dict[str, Any] | None) -> Dict[str, Any]:
    if not isinstance(evidence, dict):
        return {}
    tool = str(evidence.get("tool", "") or "")
    if tool == "get_relation_card":
        return {
            "tool": tool,
            "entity_title": evidence.get("entity_title", ""),
            "relation": evidence.get("relation", ""),
            "value": evidence.get("value", ""),
            "card_excerpt": evidence.get("card_excerpt", ""),
        }
    if tool == "get_entity_card":
        entity = evidence.get("entity", {}) if isinstance(evidence.get("entity"), dict) else {}
        return {
            "tool": tool,
            "entity_title": entity.get("title", ""),
            "aliases": entity.get("aliases", []),
            "summary": entity.get("summary", ""),
            "card_excerpt": evidence.get("card_excerpt", ""),
        }
    if tool == "bundle_cards":
        cards = evidence.get("cards", []) if isinstance(evidence.get("cards"), list) else []
        reduced = []
        for row in cards:
            if not isinstance(row, dict):
                continue
            reduced.append(
                {
                    "title": row.get("title", ""),
                    "aliases": row.get("aliases", []),
                    "summary": row.get("summary", ""),
                    "relations": row.get("relations", {}),
                }
            )
        return {"tool": tool, "cards": reduced}
    return evidence


def build_answer_messages(question_row: Dict[str, Any], evidence: Dict[str, Any] | None) -> List[Dict[str, str]]:
    answer_target = "best_grounded_span"
    answer_rule = "Return the shortest exact answer string."
    if isinstance(evidence, dict):
        tool = str(evidence.get("tool", "") or "")
        if tool == "get_entity_card":
            answer_target = "entity_title"
            answer_rule = "The answer must be the entity title, not a nickname, relation name, or copied JSON field."
        elif tool == "get_relation_card":
            answer_target = "relation_value"
            answer_rule = "The answer must be the relation value only."
    payload = {
        "question_id": question_row.get("question_id"),
        "question": question_row.get("question"),
        "evidence": compact_evidence_for_prompt(evidence),
        "answer_target": answer_target,
        "instruction": answer_rule,
        "output_contract": {"answer": "single exact answer string or unknown"},
    }
    system = (
        "You answer trivia using only the provided evidence. "
        "Return exactly one JSON object of the form {\"answer\":\"...\"}. "
        "Do not return the evidence, field names, or explanations. "
        "If the evidence is insufficient, return {\"answer\":\"unknown\"}."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, separators=(",", ":"))},
    ]


def resolve_tool_call(index: WikiCardIndex, question_row: Dict[str, Any], route_plan: Dict[str, Any], raw_payload: Dict[str, Any]) -> Dict[str, Any]:
    actions = [row for row in route_plan.get("actions", []) if isinstance(row, dict)]
    by_id = {str(row.get("action_id", "") or ""): row for row in actions if str(row.get("action_id", "") or "")}
    action_id = str(raw_payload.get("action_id") or "").strip()
    selected = by_id.get(action_id)
    if selected is None:
        tool = str(raw_payload.get("tool") or "").strip()
        args = raw_payload.get("args", {})
        if not isinstance(args, dict):
            args = {}
        for row in actions:
            if str(row.get("tool", "") or "") != tool:
                continue
            row_args = row.get("args", {}) if isinstance(row.get("args"), dict) else {}
            if tool == "get_relation_card":
                if (
                    str(row_args.get("entity_id", "") or "").strip() == str(args.get("entity_id", "") or "").strip()
                    and str(row_args.get("relation", "") or "").strip() == str(args.get("relation", "") or "").strip()
                ):
                    selected = row
                    break
            elif tool == "get_entity_card":
                if str(row_args.get("entity_id", "") or "").strip() == str(args.get("entity_id", "") or "").strip():
                    selected = row
                    break
            elif tool == "escalate":
                selected = row
                break
    if selected is None:
        actions_sorted = sorted(actions, key=lambda row: -float(row.get("score", 0.0) or 0.0))
        selected = actions_sorted[0] if actions_sorted else {"tool": "escalate", "args": {"reason": "no_action"}}
    tool = str(selected.get("tool", "") or "escalate")
    args = selected.get("args", {}) if isinstance(selected.get("args"), dict) else {}
    if tool == "get_relation_card":
        entity_id = str(args.get("entity_id", "") or "").strip()
        relation = str(args.get("relation", "") or "").strip()
        if not relation and entity_id:
            relation = infer_relation_hint(str(question_row.get("question", ""))) or index.guess_best_relation(
                entity_id, str(question_row.get("question", ""))
            )
        return {
            "action_id": str(selected.get("action_id", "") or ""),
            "namespace": str(selected.get("namespace", "") or ""),
            "tool": tool,
            "args": {"entity_id": entity_id, "relation": relation},
        }
    if tool == "get_entity_card":
        return {
            "action_id": str(selected.get("action_id", "") or ""),
            "namespace": str(selected.get("namespace", "") or ""),
            "tool": tool,
            "args": {"entity_id": str(args.get("entity_id", "") or "").strip()},
        }
    return {
        "action_id": str(selected.get("action_id", "") or "ctl::escalate"),
        "namespace": str(selected.get("namespace", "") or "control"),
        "tool": "escalate",
        "args": {"reason": str(args.get("reason") or "insufficient_evidence")},
    }


def route_is_correct(question_row: Dict[str, Any], routed: Dict[str, Any]) -> bool:
    expected_tool = str(question_row.get("expected_tool", "") or "").strip()
    expected_subject = str(question_row.get("subject_id", "") or "").strip()
    expected_relation = str(question_row.get("relation", "") or "").strip()
    tool = str(routed.get("tool", "") or "").strip()
    args = routed.get("args", {}) if isinstance(routed.get("args"), dict) else {}
    if tool != expected_tool:
        return False
    if str(args.get("entity_id", "") or "").strip() != expected_subject:
        return False
    if expected_tool == "get_relation_card":
        return str(args.get("relation", "") or "").strip() == expected_relation
    return True


class HFChatBackend:
    def __init__(
        self,
        model_path: str,
        adapter_path: str = "",
        device_map: str = "auto",
        dtype: str = "auto",
        load_in_4bit: bool = True,
        bnb_compute_dtype: str = "float16",
        gpu_max_memory_mib: int = 0,
        cpu_max_memory_mib: int = 0,
    ) -> None:
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.device_map = device_map
        self.dtype = dtype
        self.load_in_4bit = bool(load_in_4bit)
        self.bnb_compute_dtype = bnb_compute_dtype
        self.gpu_max_memory_mib = int(gpu_max_memory_mib or 0)
        self.cpu_max_memory_mib = int(cpu_max_memory_mib or 0)
        self.model = None
        self.tokenizer = None
        self._load()

    def _resolve_dtype(self, torch_mod: Any) -> Any:
        if self.dtype == "float16":
            return torch_mod.float16
        if self.dtype == "bfloat16":
            return torch_mod.bfloat16
        if self.dtype == "float32":
            return torch_mod.float32
        return "auto"

    def _load(self) -> None:
        import torch  # type: ignore
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

        tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=True)
        dtype = self._resolve_dtype(torch)
        max_memory = None
        if self.gpu_max_memory_mib > 0 or self.cpu_max_memory_mib > 0:
            max_memory = {}
            if self.gpu_max_memory_mib > 0 and torch.cuda.is_available():
                for device_idx in range(torch.cuda.device_count()):
                    max_memory[device_idx] = f"{self.gpu_max_memory_mib}MiB"
            if self.cpu_max_memory_mib > 0:
                max_memory["cpu"] = f"{self.cpu_max_memory_mib}MiB"
            if not max_memory:
                max_memory = None
        model = None
        if bool(self.load_in_4bit):
            try:
                from transformers import BitsAndBytesConfig  # type: ignore

                compute_dtype = torch.float16
                if str(self.bnb_compute_dtype).lower() == "bfloat16":
                    compute_dtype = torch.bfloat16
                qcfg = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=compute_dtype,
                )
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    quantization_config=qcfg,
                    device_map=self.device_map,
                    max_memory=max_memory,
                )
            except Exception:
                model = None
        if model is None:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=dtype,
                device_map=self.device_map,
                max_memory=max_memory,
            )
        if self.adapter_path:
            model = self._load_adapter(model)
        model.eval()
        self.model = model
        self.tokenizer = tokenizer

    def _load_adapter(self, model: Any) -> Any:
        from peft import LoraConfig, PeftModel  # type: ignore

        adapter_path = Path(self.adapter_path).expanduser().resolve()
        try:
            return PeftModel.from_pretrained(model, str(adapter_path))
        except TypeError:
            config_path = adapter_path / "adapter_config.json"
            if not config_path.exists():
                raise
            payload = json.loads(config_path.read_text(encoding="utf-8-sig"))
            allowed = set(inspect.signature(LoraConfig.__init__).parameters.keys())
            filtered = {key: value for key, value in payload.items() if key in allowed}
            with tempfile.TemporaryDirectory(prefix="peft_adapter_compat_") as temp_dir:
                temp_path = Path(temp_dir)
                for item in adapter_path.iterdir():
                    destination = temp_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, destination)
                    else:
                        shutil.copy2(item, destination)
                (temp_path / "adapter_config.json").write_text(
                    json.dumps(filtered, indent=2, ensure_ascii=True) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                return PeftModel.from_pretrained(model, str(temp_path))

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int,
        temperature: float = 0.0,
        top_p: float = 1.0,
        do_sample: bool = False,
    ) -> Dict[str, Any]:
        assert self.model is not None
        assert self.tokenizer is not None
        import torch  # type: ignore

        tok = self.tokenizer
        model = self.model
        if hasattr(tok, "apply_chat_template"):
            try:
                rendered = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            except TypeError:
                rendered = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            rendered = "\n".join(f"{item['role'].title()}: {item['content']}" for item in messages) + "\nAssistant:"
        encoded = tok(rendered, return_tensors="pt")
        device = next(model.parameters()).device
        encoded = {key: value.to(device) for key, value in encoded.items()}
        t0 = time.time()
        with torch.no_grad():
            out_ids = model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
                pad_token_id=tok.eos_token_id,
            )
        latency = time.time() - t0
        new_ids = out_ids[0][encoded["input_ids"].shape[1] :]
        text = tok.decode(new_ids, skip_special_tokens=True).strip()
        return {
            "text": text,
            "prompt_tokens": int(encoded["input_ids"].shape[1]),
            "completion_tokens": int(new_ids.shape[0]),
            "latency_sec": round(latency, 4),
        }


class HeuristicBackend:
    @staticmethod
    def _pick_bundle_card(question_text: str, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        question_tokens = re.findall(r"[A-Za-z0-9_]+", str(question_text).lower())
        best_card: Dict[str, Any] = {}
        best_score = -1.0
        for card in cards:
            relations = card.get("relations", {}) if isinstance(card.get("relations"), dict) else {}
            blob = " ".join(
                [
                    str(card.get("title", "") or ""),
                    " ".join(str(item) for item in card.get("aliases", []) if str(item).strip()),
                    str(card.get("summary", "") or ""),
                    json.dumps(relations, ensure_ascii=True, sort_keys=True),
                ]
            ).lower()
            score = float(sum(1 for token in question_tokens if token in blob))
            if str(card.get("title", "") or "").lower() in str(question_text).lower():
                score += 4.0
            if score > best_score:
                best_card = card
                best_score = score
        return best_card

    def route(self, route_plan: Dict[str, Any]) -> Dict[str, Any]:
        actions = [row for row in route_plan.get("actions", []) if isinstance(row, dict)]
        if not actions:
            return {"action_id": "ctl::escalate", "namespace": "control", "tool": "escalate", "args": {"reason": "no_action"}}
        best = max(actions, key=lambda row: float(row.get("score", 0.0) or 0.0))
        return {
            "action_id": str(best.get("action_id", "") or ""),
            "namespace": str(best.get("namespace", "") or ""),
            "tool": str(best.get("tool", "") or "escalate"),
            "args": best.get("args", {}) if isinstance(best.get("args"), dict) else {},
        }

    def answer(self, _question_row: Dict[str, Any], evidence: Dict[str, Any] | None) -> Dict[str, Any]:
        if not evidence:
            return {"text": "unknown", "prompt_tokens": 0, "completion_tokens": 1, "latency_sec": 0.0}
        tool = str(evidence.get("tool", "") or "")
        question_text = str(_question_row.get("question", "") or "")
        if tool == "bundle_cards":
            cards = evidence.get("cards", []) if isinstance(evidence.get("cards"), list) else []
            selected = self._pick_bundle_card(question_text, cards)
            if not selected:
                return {"text": "unknown", "prompt_tokens": 0, "completion_tokens": 1, "latency_sec": 0.0}
            if question_prefers_relation(question_text):
                relations = selected.get("relations", {}) if isinstance(selected.get("relations"), dict) else {}
                relation = ""
                best_score = -1.0
                for key, value in relations.items():
                    score = score_relation_choice(question_text, str(key), value)
                    if score > best_score:
                        relation = str(key)
                        best_score = score
                if relation and relation in relations:
                    value = str(relations.get(relation, "") or "unknown")
                    return {
                        "text": value,
                        "prompt_tokens": 0,
                        "completion_tokens": estimate_tokens(value),
                        "latency_sec": 0.0,
                    }
            title = str(selected.get("title", "") or "unknown")
            return {
                "text": title,
                "prompt_tokens": 0,
                "completion_tokens": estimate_tokens(title),
                "latency_sec": 0.0,
            }
        if tool == "get_relation_card" and evidence.get("found"):
            return {
                "text": str(evidence.get("value", "") or "unknown"),
                "prompt_tokens": 0,
                "completion_tokens": estimate_tokens(evidence.get("value", "")),
                "latency_sec": 0.0,
            }
        if tool == "get_entity_card" and evidence.get("found"):
            entity = evidence.get("entity", {}) if isinstance(evidence.get("entity"), dict) else {}
            return {
                "text": str(entity.get("title", "") or "unknown"),
                "prompt_tokens": 0,
                "completion_tokens": estimate_tokens(entity.get("title", "")),
                "latency_sec": 0.0,
            }
        return {"text": "unknown", "prompt_tokens": 0, "completion_tokens": 1, "latency_sec": 0.0}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the wiki-card-routerbench fixed-budget trivia benchmark.")
    parser.add_argument("--config", default="", help="Optional benchmark spec JSON path.")
    parser.add_argument("--run-id", default="", help="Override the run id.")
    parser.add_argument("--benchmark-root", default="", help="Override the benchmark root containing cards.jsonl and questions.jsonl.")
    parser.add_argument("--output-root", default="", help="Override the benchmark output root.")
    parser.add_argument("--model-path", default="", help="Local model path for HF backend.")
    parser.add_argument("--adapter-path", default="", help="Optional adapter path.")
    parser.add_argument("--backend", default="", choices=["hf", "heuristic"], help="Backend to use.")
    parser.add_argument("--max-questions", type=int, default=-1, help="Optional cap on question count.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve configuration and write a planned summary without loading a model.")
    parser.add_argument("--device-map", default="", help="Optional HF device map override.")
    parser.add_argument("--dtype", default="", help="Optional HF dtype override.")
    parser.add_argument("--load-in-4bit", action="store_true", help="Force 4-bit loading for HF backend.")
    parser.add_argument("--no-4bit", action="store_true", help="Disable 4-bit loading for HF backend.")
    parser.add_argument("--bnb-compute-dtype", default="", help="Optional bitsandbytes compute dtype override.")
    parser.add_argument("--gpu-max-memory-mib", type=int, default=0, help="Optional per-GPU max memory in MiB.")
    parser.add_argument("--cpu-max-memory-mib", type=int, default=0, help="Optional CPU placement max memory in MiB.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    repo_root = Path(__file__).resolve().parents[3]
    spec_path = Path(args.config).resolve() if args.config else skill_root / "references" / "wiki-card-routerbench-spec.json"
    spec = read_json(spec_path)

    benchmark_root = Path(args.benchmark_root).resolve() if args.benchmark_root else (
        Path(str(spec.get("benchmark_root") or "")).resolve()
        if str(spec.get("benchmark_root") or "").strip()
        else repo_root / "benchmarks" / "wiki_card_routerbench"
    )
    output_root = Path(args.output_root).resolve() if args.output_root else (
        Path(str(spec.get("output_root") or "")).resolve()
        if str(spec.get("output_root") or "").strip()
        else skill_root / "runs"
    )
    run_id = str(args.run_id or spec.get("run_id") or "wiki_card_routerbench")
    backend_name = str(args.backend or spec.get("backend") or "hf")
    model_path = str(args.model_path or spec.get("model_path") or "")
    adapter_path = str(args.adapter_path or spec.get("adapter_path") or "")
    device_map = str(args.device_map or spec.get("device_map") or "auto")
    dtype = str(args.dtype or spec.get("dtype") or "auto")
    bnb_compute_dtype = str(args.bnb_compute_dtype or spec.get("bnb_compute_dtype") or "float16")
    gpu_max_memory_mib = int(args.gpu_max_memory_mib or spec.get("gpu_max_memory_mib", 0) or 0)
    cpu_max_memory_mib = int(args.cpu_max_memory_mib or spec.get("cpu_max_memory_mib", 0) or 0)
    load_in_4bit = bool(spec.get("load_in_4bit", True))
    if args.load_in_4bit:
        load_in_4bit = True
    if args.no_4bit:
        load_in_4bit = False
    max_questions = args.max_questions if args.max_questions >= 0 else int(spec.get("max_questions", 0) or 0)
    stuffed_top_k = int(spec.get("stuffed_top_k", 3) or 3)
    candidate_top_k = int(spec.get("candidate_top_k", 5) or 5)
    router_max_new_tokens = int(spec.get("router_max_new_tokens", 64) or 64)
    answer_max_new_tokens = int(spec.get("answer_max_new_tokens", 48) or 48)
    conditions = [str(item) for item in spec.get("conditions", ["closed_book", "stuffed", "mcp_routed"]) if str(item).strip()]

    index = WikiCardIndex(benchmark_root)
    questions = index.load_questions(max_questions=max_questions)
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    resolved = {
        "run_id": run_id,
        "benchmark_root": str(benchmark_root),
        "output_root": str(output_root),
        "config_path": str(spec_path),
        "backend": backend_name,
        "model_path": model_path,
        "adapter_path": adapter_path,
        "device_map": device_map,
        "dtype": dtype,
        "load_in_4bit": load_in_4bit,
        "bnb_compute_dtype": bnb_compute_dtype,
        "gpu_max_memory_mib": gpu_max_memory_mib,
        "cpu_max_memory_mib": cpu_max_memory_mib,
        "max_questions": max_questions,
        "question_count": len(questions),
        "conditions": conditions,
        "stuffed_top_k": stuffed_top_k,
        "candidate_top_k": candidate_top_k,
        "router_max_new_tokens": router_max_new_tokens,
        "answer_max_new_tokens": answer_max_new_tokens,
        "index_summary": index.describe(),
    }
    dump_json(run_dir / "wiki_card_routerbench.resolved.json", resolved)

    if args.dry_run:
        dump_json(
            run_dir / "summary.json",
            {
                "run_id": run_id,
                "status": "planned",
                "backend": backend_name,
                "question_count": len(questions),
                "conditions": conditions,
                "benchmark_root": str(benchmark_root),
            },
        )
        print(str(run_dir / "wiki_card_routerbench.resolved.json"))
        return 0

    if backend_name == "hf":
        if not model_path:
            raise SystemExit("HF backend requires --model-path or model_path in the benchmark spec.")
        backend: Any = HFChatBackend(
            model_path=model_path,
            adapter_path=adapter_path,
            device_map=device_map,
            dtype=dtype,
            load_in_4bit=load_in_4bit,
            bnb_compute_dtype=bnb_compute_dtype,
            gpu_max_memory_mib=gpu_max_memory_mib,
            cpu_max_memory_mib=cpu_max_memory_mib,
        )
    else:
        backend = HeuristicBackend()

    rows: List[Dict[str, Any]] = []
    for condition in conditions:
        for question_row in questions:
            question_id = str(question_row.get("question_id", "") or "")
            question_text = str(question_row.get("question", "") or "")
            route_plan = index.plan_query(
                question_text,
                candidate_top_k=max(stuffed_top_k, candidate_top_k),
                relation_top_k=max(4, candidate_top_k + 1),
            )
            candidates = list(route_plan.get("entity_hits", []))
            routed: Dict[str, Any] | None = None
            route_raw = ""
            route_prompt_tokens = 0
            route_completion_tokens = 0
            route_latency_sec = 0.0
            evidence: Dict[str, Any] | None = None
            if condition == "stuffed":
                evidence = index.bundle_cards(hit.get("entity_id", "") for hit in candidates[:stuffed_top_k])
            elif condition == "mcp_routed":
                if backend_name == "heuristic":
                    routed = backend.route(route_plan)
                else:
                    router_messages = build_router_messages(question_row, route_plan)
                    route_response = backend.chat(router_messages, max_new_tokens=router_max_new_tokens)
                    route_raw = str(route_response.get("text", "") or "")
                    route_prompt_tokens = int(route_response.get("prompt_tokens", 0) or 0)
                    route_completion_tokens = int(route_response.get("completion_tokens", 0) or 0)
                    route_latency_sec = float(route_response.get("latency_sec", 0.0) or 0.0)
                    routed = resolve_tool_call(index, question_row, route_plan, parse_router_json(route_raw))
                if routed is None:
                    routed = {
                        "action_id": "ctl::escalate",
                        "namespace": "control",
                        "tool": "escalate",
                        "args": {"reason": "router_failed"},
                    }
                if routed["tool"] == "get_entity_card":
                    evidence = index.get_entity_card(str(routed["args"].get("entity_id", "") or ""))
                elif routed["tool"] == "get_relation_card":
                    evidence = index.get_relation_card(
                        str(routed["args"].get("entity_id", "") or ""),
                        str(routed["args"].get("relation", "") or ""),
                    )
                else:
                    evidence = {"tool": "escalate", "reason": routed["args"].get("reason", "insufficient_evidence")}

            if backend_name == "heuristic":
                if condition == "closed_book":
                    answer_response = {"text": "unknown", "prompt_tokens": 0, "completion_tokens": 1, "latency_sec": 0.0}
                else:
                    answer_response = backend.answer(question_row, evidence)
            else:
                answer_messages = build_answer_messages(question_row, evidence)
                answer_response = backend.chat(answer_messages, max_new_tokens=answer_max_new_tokens)

            raw_answer = str(answer_response.get("text", "") or "")
            final_answer = compact_answer(raw_answer)
            answer_eval = evaluate_answer(question_row, final_answer)
            evidence_tokens = estimate_tokens(json.dumps(evidence or {}, ensure_ascii=True))
            route_correct = route_is_correct(question_row, routed) if condition == "mcp_routed" and routed else None
            rows.append(
                {
                    "condition": condition,
                    "question_id": question_id,
                    "question": question_text,
                    "expected_answer": question_row.get("answer"),
                    "answer_aliases": question_row.get("answer_aliases", []),
                    "prediction_raw": raw_answer,
                    "prediction": final_answer,
                    "correct": bool(answer_eval["correct"]),
                    "match_type": answer_eval["match_type"],
                    "search_hits": candidates,
                    "route_plan": route_plan,
                    "routed": routed,
                    "route_raw": route_raw,
                    "route_correct": route_correct,
                    "evidence": evidence,
                    "retrieved_tokens_est": evidence_tokens if condition != "closed_book" else 0,
                    "answer_prompt_tokens": int(answer_response.get("prompt_tokens", 0) or 0),
                    "answer_completion_tokens": int(answer_response.get("completion_tokens", 0) or 0),
                    "answer_latency_sec": float(answer_response.get("latency_sec", 0.0) or 0.0),
                    "route_prompt_tokens": route_prompt_tokens,
                    "route_completion_tokens": route_completion_tokens,
                    "route_latency_sec": route_latency_sec,
                }
            )

    dump_jsonl(run_dir / "results.jsonl", rows)

    summary_conditions: Dict[str, Any] = {}
    for condition in conditions:
        condition_rows = [row for row in rows if row["condition"] == condition]
        total = len(condition_rows)
        correct = sum(1 for row in condition_rows if row["correct"])
        route_rows = [row for row in condition_rows if row["route_correct"] is not None]
        route_correct = sum(1 for row in route_rows if row["route_correct"])
        summary_conditions[condition] = {
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total, 3) if total else 0.0,
            "avg_retrieved_tokens_est": round(
                sum(float(row["retrieved_tokens_est"]) for row in condition_rows) / total, 3
            )
            if total
            else 0.0,
            "avg_answer_prompt_tokens": round(
                sum(float(row["answer_prompt_tokens"]) for row in condition_rows) / total, 3
            )
            if total
            else 0.0,
            "avg_answer_completion_tokens": round(
                sum(float(row["answer_completion_tokens"]) for row in condition_rows) / total, 3
            )
            if total
            else 0.0,
            "avg_answer_latency_sec": round(
                sum(float(row["answer_latency_sec"]) for row in condition_rows) / total, 4
            )
            if total
            else 0.0,
            "route_accuracy": round(route_correct / len(route_rows), 3) if route_rows else None,
        }

    closed_accuracy = float(summary_conditions.get("closed_book", {}).get("accuracy", 0.0) or 0.0)
    stuffed_accuracy = float(summary_conditions.get("stuffed", {}).get("accuracy", 0.0) or 0.0)
    mcp_accuracy = float(summary_conditions.get("mcp_routed", {}).get("accuracy", 0.0) or 0.0)
    scorecard = {
        "closed_book_accuracy": round(closed_accuracy, 3),
        "stuffed_accuracy": round(stuffed_accuracy, 3),
        "mcp_routed_accuracy": round(mcp_accuracy, 3),
        "mcp_minus_closed": round(mcp_accuracy - closed_accuracy, 3),
        "mcp_minus_stuffed": round(mcp_accuracy - stuffed_accuracy, 3),
        "mcp_route_accuracy": summary_conditions.get("mcp_routed", {}).get("route_accuracy"),
        "benchmark_root": str(benchmark_root),
        "run_dir": str(run_dir),
        "backend": backend_name,
    }
    dump_json(run_dir / "scorecard.json", scorecard)
    dump_json(
        run_dir / "summary.json",
        {
            "run_id": run_id,
            "status": "completed",
            "backend": backend_name,
            "model_path": model_path,
            "adapter_path": adapter_path,
            "benchmark_root": str(benchmark_root),
            "question_count": len(questions),
            "conditions": summary_conditions,
            "scorecard": scorecard,
            "results_path": str(run_dir / "results.jsonl"),
        },
    )
    print(json.dumps(scorecard, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
