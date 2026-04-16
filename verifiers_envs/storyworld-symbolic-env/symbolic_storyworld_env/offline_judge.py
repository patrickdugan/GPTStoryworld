from __future__ import annotations


def judge_trace_placeholder(trace_path: str) -> dict[str, object]:
    return {
        "implemented": False,
        "trace_path": trace_path,
        "note": "Offline judge intentionally deferred. Use the JSONL trajectory as the canonical later input.",
    }
