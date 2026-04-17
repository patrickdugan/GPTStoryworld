from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


RELATION_PATTERNS: List[tuple[str, str]] = [
    (r"what is the capital of", "capital"),
    (r"who wrote", "author"),
    (r"who painted", "artist"),
    (r"who discovered", "discovered_by"),
    (r"what year .* land on the moon", "moon_landing_year"),
    (r"what is the chemical symbol", "chemical_symbol"),
    (r"what language .* spoken", "primary_language"),
    (r"on what continent", "continent"),
    (r"which scientist proposed", "proposed_by"),
]

STOPWORDS = {
    "a",
    "an",
    "as",
    "at",
    "did",
    "do",
    "does",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "what",
    "which",
    "who",
}


def _tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"[A-Za-z0-9_]+", str(text).lower()) if token]


def _estimate_tokens(text: str) -> int:
    return max(1, len(_tokenize(text)))


def _excerpt(text: str, limit: int = 220) -> str:
    compact = re.sub(r"\s+", " ", str(text)).strip()
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)].rstrip() + "..."


def _normalize_surface(text: str) -> str:
    return " ".join(_tokenize(text))


def _content_tokens(text: str) -> List[str]:
    return [token for token in _tokenize(text) if token not in STOPWORDS]


def _contains_token_sequence(query_tokens: Sequence[str], surface_tokens: Sequence[str]) -> bool:
    if not query_tokens or not surface_tokens or len(surface_tokens) > len(query_tokens):
        return False
    width = len(surface_tokens)
    for idx in range(len(query_tokens) - width + 1):
        if list(query_tokens[idx : idx + width]) == list(surface_tokens):
            return True
    return False


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _score_overlap(query_tokens: Sequence[str], *texts: str) -> float:
    if not query_tokens:
        return 0.0
    bag = set()
    for text in texts:
        bag.update(_content_tokens(text))
    return float(sum(1 for token in query_tokens if token in bag))


def _score_relation_choice(question: str, key: str, value: Any) -> float:
    question_tokens = _content_tokens(question)
    key_tokens = _content_tokens(str(key).replace("_", " "))
    value_tokens = _content_tokens(str(value))
    score = 3.0 * float(sum(1 for token in question_tokens if token in key_tokens))
    score += 1.0 * float(sum(1 for token in question_tokens if token in value_tokens))
    normalized_key = " ".join(key_tokens)
    if normalized_key and normalized_key in " ".join(question_tokens):
        score += 4.0
    return score


def infer_relation_hint(question: str) -> str:
    q = str(question or "").lower()
    for pattern, relation in RELATION_PATTERNS:
        if re.search(pattern, q):
            return relation
    return ""


def question_prefers_relation(question: str) -> bool:
    return bool(infer_relation_hint(question))


@dataclass(frozen=True)
class EntityHit:
    entity_id: str
    title: str
    score: float
    summary_excerpt: str
    relation_keys: List[str]


@dataclass(frozen=True)
class AliasHit:
    entity_id: str
    title: str
    surface: str
    surface_type: str
    score: float


@dataclass(frozen=True)
class RelationHit:
    relation_id: str
    entity_id: str
    entity_title: str
    relation: str
    value: Any
    score: float


@dataclass(frozen=True)
class RouteAction:
    action_id: str
    namespace: str
    tool: str
    args: Dict[str, str]
    score: float
    label: str


class WikiCardIndex:
    def __init__(self, benchmark_root: str | Path) -> None:
        self.benchmark_root = Path(benchmark_root).expanduser().resolve()
        self.cards_path = self.benchmark_root / "cards.jsonl"
        self.questions_path = self.benchmark_root / "questions.jsonl"
        self._cards = _load_jsonl(self.cards_path)
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._aliases: List[Dict[str, Any]] = []
        self._relation_rows: List[Dict[str, Any]] = []
        for row in self._cards:
            entity_id = str(row.get("entity_id", "") or "").strip()
            if not entity_id:
                continue
            self._by_id[entity_id] = row
            title = str(row.get("title", "") or "").strip()
            if title:
                self._aliases.append(
                    {
                        "entity_id": entity_id,
                        "title": title,
                        "surface": title,
                        "surface_type": "title",
                        "normalized_surface": _normalize_surface(title),
                    }
                )
            for alias in [str(item) for item in row.get("aliases", []) if str(item).strip()]:
                self._aliases.append(
                    {
                        "entity_id": entity_id,
                        "title": title,
                        "surface": alias,
                        "surface_type": "alias",
                        "normalized_surface": _normalize_surface(alias),
                    }
                )
            relations = row.get("relations", {}) or {}
            for key, value in relations.items():
                self._relation_rows.append(
                    {
                        "relation_id": f"{entity_id}:{key}",
                        "entity_id": entity_id,
                        "entity_title": title,
                        "relation": str(key),
                        "value": value,
                    }
                )

    def describe(self) -> Dict[str, Any]:
        relation_keys = sorted({str(row.get("relation", "")) for row in self._relation_rows if row.get("relation")})
        return {
            "benchmark_root": str(self.benchmark_root),
            "cards_path": str(self.cards_path),
            "questions_path": str(self.questions_path),
            "entity_count": len(self._by_id),
            "alias_count": len(self._aliases),
            "relation_count": len(self._relation_rows),
            "question_count": len(self.load_questions()),
            "namespaces": {
                "aliases": len(self._aliases),
                "entities": len(self._by_id),
                "relations": len(self._relation_rows),
                "control": 1,
            },
            "relation_keys": relation_keys,
            "sample_entity_ids": list(sorted(self._by_id))[:8],
        }

    def load_questions(self, max_questions: int = 0) -> List[Dict[str, Any]]:
        rows = _load_jsonl(self.questions_path)
        if max_questions > 0:
            return rows[:max_questions]
        return rows

    def get_card(self, entity_id: str) -> Dict[str, Any]:
        return dict(self._by_id.get(str(entity_id).strip(), {}))

    def get_relation_row(self, entity_id: str, relation: str) -> Dict[str, Any]:
        key = f"{str(entity_id).strip()}:{str(relation).strip()}"
        for row in self._relation_rows:
            if row.get("relation_id") == key:
                return dict(row)
        return {}

    def search_entities(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        query = str(query or "").strip()
        query_tokens = _content_tokens(query)
        hits: List[EntityHit] = []
        for row in self._cards:
            entity_id = str(row.get("entity_id", "") or "").strip()
            title = str(row.get("title", "") or "").strip()
            aliases = [str(item) for item in row.get("aliases", []) if str(item).strip()]
            summary = str(row.get("summary", "") or "").strip()
            relations = row.get("relations", {}) or {}
            relation_blob = json.dumps(relations, ensure_ascii=True, sort_keys=True)
            score = 0.0
            score += 3.0 * _score_overlap(query_tokens, title)
            score += 2.0 * _score_overlap(query_tokens, " ".join(aliases))
            score += 1.5 * _score_overlap(query_tokens, summary)
            score += 1.5 * _score_overlap(query_tokens, relation_blob)
            if title and title.lower() in query.lower():
                score += 5.0
            if any(alias and alias.lower() in query.lower() for alias in aliases):
                score += 4.0
            if score <= 0.0:
                continue
            hits.append(
                EntityHit(
                    entity_id=entity_id,
                    title=title,
                    score=score,
                    summary_excerpt=_excerpt(summary, 180),
                    relation_keys=[str(key) for key in relations.keys()],
                )
            )
        hits.sort(key=lambda item: (-item.score, item.entity_id))
        return {
            "tool": "search_entities",
            "query": query,
            "hits": [
                {
                    "entity_id": hit.entity_id,
                    "title": hit.title,
                    "score": round(hit.score, 3),
                    "summary_excerpt": hit.summary_excerpt,
                    "relation_keys": hit.relation_keys,
                }
                for hit in hits[:top_k]
            ],
        }

    def search_aliases(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        query = str(query or "").strip()
        query_tokens = _content_tokens(query)
        query_surface_tokens = _tokenize(query)
        hits: List[AliasHit] = []
        for row in self._aliases:
            score = 0.0
            surface = str(row.get("surface", "") or "")
            surface_tokens = _tokenize(surface)
            score += 4.0 * _score_overlap(query_tokens, surface)
            if _contains_token_sequence(query_surface_tokens, surface_tokens):
                score += 6.0
            if surface_tokens and _contains_token_sequence(_content_tokens(query), _content_tokens(surface)):
                score += 4.0
            if score <= 0.0:
                continue
            hits.append(
                AliasHit(
                    entity_id=str(row.get("entity_id", "") or ""),
                    title=str(row.get("title", "") or ""),
                    surface=surface,
                    surface_type=str(row.get("surface_type", "") or "alias"),
                    score=score,
                )
            )
        hits.sort(key=lambda item: (-item.score, item.entity_id, item.surface))
        deduped: List[AliasHit] = []
        seen: set[tuple[str, str]] = set()
        for hit in hits:
            key = (hit.entity_id, hit.surface)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(hit)
        return {
            "tool": "search_aliases",
            "query": query,
            "hits": [
                {
                    "entity_id": hit.entity_id,
                    "title": hit.title,
                    "surface": hit.surface,
                    "surface_type": hit.surface_type,
                    "score": round(hit.score, 3),
                }
                for hit in deduped[:top_k]
            ],
        }

    def search_relation_cards(self, query: str, entity_ids: Iterable[str] | None = None, top_k: int = 6) -> Dict[str, Any]:
        query = str(query or "").strip()
        allowed = {str(item).strip() for item in (entity_ids or []) if str(item).strip()}
        hits: List[RelationHit] = []
        for row in self._relation_rows:
            entity_id = str(row.get("entity_id", "") or "")
            if allowed and entity_id not in allowed:
                continue
            relation = str(row.get("relation", "") or "")
            value = row.get("value")
            entity_title = str(row.get("entity_title", "") or "")
            score = 0.0
            score += 2.0 * _score_overlap(_tokenize(query), entity_title)
            score += _score_relation_choice(query, relation, value)
            if infer_relation_hint(query) == relation:
                score += 8.0
            if score <= 0.0:
                continue
            hits.append(
                RelationHit(
                    relation_id=str(row.get("relation_id", "") or ""),
                    entity_id=entity_id,
                    entity_title=entity_title,
                    relation=relation,
                    value=value,
                    score=score,
                )
            )
        hits.sort(key=lambda item: (-item.score, item.relation_id))
        return {
            "tool": "search_relation_cards",
            "query": query,
            "hits": [
                {
                    "relation_id": hit.relation_id,
                    "entity_id": hit.entity_id,
                    "entity_title": hit.entity_title,
                    "relation": hit.relation,
                    "value": hit.value,
                    "score": round(hit.score, 3),
                }
                for hit in hits[:top_k]
            ],
        }

    def _entity_action(self, entity_id: str, score: float) -> RouteAction:
        card = self.get_card(entity_id)
        title = str(card.get("title", "") or entity_id)
        return RouteAction(
            action_id=f"ent::{entity_id}",
            namespace="entities",
            tool="get_entity_card",
            args={"entity_id": entity_id},
            score=score,
            label=f"entity:{title}",
        )

    def _relation_action(self, entity_id: str, relation: str, score: float) -> RouteAction:
        row = self.get_relation_row(entity_id, relation)
        title = str(row.get("entity_title", "") or entity_id)
        value = _excerpt(str(row.get("value", "") or ""), 48)
        return RouteAction(
            action_id=f"rel::{entity_id}::{relation}",
            namespace="relations",
            tool="get_relation_card",
            args={"entity_id": entity_id, "relation": relation},
            score=score,
            label=f"relation:{title}.{relation}={value}",
        )

    def plan_query(
        self,
        question: str,
        candidate_top_k: int = 5,
        relation_top_k: int = 6,
        max_actions: int = 10,
    ) -> Dict[str, Any]:
        alias_hits = list(self.search_aliases(question, top_k=max(2, candidate_top_k)).get("hits", []))
        entity_hits = list(self.search_entities(question, top_k=max(2, candidate_top_k)).get("hits", []))
        entity_order: List[str] = []
        for row in alias_hits + entity_hits:
            entity_id = str(row.get("entity_id", "") or "")
            if entity_id and entity_id not in entity_order:
                entity_order.append(entity_id)
        relation_hits = list(
            self.search_relation_cards(question, entity_ids=entity_order[:candidate_top_k], top_k=max(2, relation_top_k)).get(
                "hits", []
            )
        )

        prefer_relation = question_prefers_relation(question)
        actions: List[RouteAction] = []
        entity_scores: Dict[str, float] = {}
        for row in entity_hits:
            entity_id = str(row.get("entity_id", "") or "")
            entity_scores[entity_id] = max(entity_scores.get(entity_id, 0.0), float(row.get("score", 0.0) or 0.0))
        for row in alias_hits:
            entity_id = str(row.get("entity_id", "") or "")
            entity_scores[entity_id] = max(entity_scores.get(entity_id, 0.0), float(row.get("score", 0.0) or 0.0) + 2.0)
        for entity_id in entity_order[:candidate_top_k]:
            base_score = entity_scores.get(entity_id, 0.0)
            if base_score <= 0.0:
                continue
            bias = 7.0 if not prefer_relation else -4.0
            actions.append(self._entity_action(entity_id, base_score + bias))

        for row in relation_hits[:relation_top_k]:
            entity_id = str(row.get("entity_id", "") or "")
            relation = str(row.get("relation", "") or "")
            base_score = float(row.get("score", 0.0) or 0.0)
            if not entity_id or not relation or base_score <= 0.0:
                continue
            bias = 9.0 if prefer_relation else -6.0
            actions.append(self._relation_action(entity_id, relation, base_score + bias))

        actions.append(
            RouteAction(
                action_id="ctl::escalate",
                namespace="control",
                tool="escalate",
                args={"reason": "insufficient_evidence"},
                score=0.25,
                label="control:escalate",
            )
        )
        deduped_actions: List[RouteAction] = []
        seen_action_ids: set[str] = set()
        for action in sorted(actions, key=lambda item: (-item.score, item.action_id)):
            if action.action_id in seen_action_ids:
                continue
            seen_action_ids.add(action.action_id)
            deduped_actions.append(action)
        return {
            "question": str(question or ""),
            "type_hint": "relation" if prefer_relation else "entity",
            "relation_hint": infer_relation_hint(question),
            "namespaces": ["aliases", "entities", "relations", "control"],
            "alias_hits": alias_hits[:candidate_top_k],
            "entity_hits": entity_hits[:candidate_top_k],
            "relation_hits": relation_hits[:relation_top_k],
            "actions": [
                {
                    "action_id": action.action_id,
                    "namespace": action.namespace,
                    "tool": action.tool,
                    "args": action.args,
                    "score": round(action.score, 3),
                    "label": action.label,
                }
                for action in deduped_actions[:max_actions]
            ],
        }

    def bundle_cards(self, entity_ids: Iterable[str]) -> Dict[str, Any]:
        cards: List[Dict[str, Any]] = []
        for entity_id in entity_ids:
            row = self.get_card(str(entity_id))
            if not row:
                continue
            relations = row.get("relations", {}) or {}
            cards.append(
                {
                    "entity_id": row.get("entity_id"),
                    "title": row.get("title"),
                    "aliases": row.get("aliases", []),
                    "summary": row.get("summary", ""),
                    "relations": relations,
                    "relation_keys": list(relations.keys()),
                }
            )
        return {
            "tool": "bundle_cards",
            "cards": cards,
            "retrieved_tokens_est": _estimate_tokens(json.dumps(cards, ensure_ascii=True)),
        }

    def get_entity_card(self, entity_id: str) -> Dict[str, Any]:
        entity_id = str(entity_id or "").strip()
        row = self.get_card(entity_id)
        if not row:
            return {
                "tool": "get_entity_card",
                "entity_id": entity_id,
                "found": False,
                "message": "Entity card not found.",
                "top_hits": self.search_entities(entity_id, top_k=3).get("hits", []),
            }
        relations = row.get("relations", {}) or {}
        excerpt_lines = [str(row.get("summary", "") or "").strip()]
        excerpt_lines.extend(f"{key}: {value}" for key, value in list(relations.items())[:4])
        excerpt = " | ".join(line for line in excerpt_lines if line)
        return {
            "tool": "get_entity_card",
            "entity_id": entity_id,
            "found": True,
            "entity": {
                "entity_id": row.get("entity_id"),
                "title": row.get("title"),
                "aliases": row.get("aliases", []),
                "summary": row.get("summary", ""),
                "relations": relations,
            },
            "card_excerpt": _excerpt(excerpt, 260),
            "retrieved_tokens_est": _estimate_tokens(excerpt),
        }

    def guess_best_relation(self, entity_id: str, question: str) -> str:
        row = self.get_card(entity_id)
        relations = row.get("relations", {}) or {}
        if not relations:
            return ""
        hint = infer_relation_hint(question)
        if hint and hint in relations:
            return hint
        best_key = ""
        best_score = -1.0
        for key, value in relations.items():
            score = _score_relation_choice(question, str(key), value)
            if score > best_score:
                best_key = str(key)
                best_score = score
        if best_key:
            return best_key
        return str(next(iter(relations.keys())))

    def get_relation_card(self, entity_id: str, relation: str) -> Dict[str, Any]:
        entity_id = str(entity_id or "").strip()
        requested_relation = str(relation or "").strip()
        row = self.get_card(entity_id)
        if not row:
            return {
                "tool": "get_relation_card",
                "entity_id": entity_id,
                "relation": requested_relation,
                "found": False,
                "message": "Entity card not found.",
                "top_hits": self.search_entities(entity_id, top_k=3).get("hits", []),
            }
        relations = row.get("relations", {}) or {}
        if requested_relation not in relations:
            requested_relation = self.guess_best_relation(entity_id, requested_relation)
        value = relations.get(requested_relation)
        found = value is not None
        excerpt = f"{row.get('title', '')} | {requested_relation}: {value}"
        return {
            "tool": "get_relation_card",
            "entity_id": entity_id,
            "relation": requested_relation,
            "found": found,
            "entity_title": row.get("title"),
            "value": value,
            "card_excerpt": _excerpt(excerpt, 220),
            "relation_keys": list(relations.keys()),
            "retrieved_tokens_est": _estimate_tokens(excerpt),
        }
