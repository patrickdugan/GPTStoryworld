from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = Path(__file__).resolve().parent
FIG_DIR = PAPER_DIR / "figures"
GEN_DIR = PAPER_DIR / "generated"


TRIVIA_RUNS = {
    "Base 2B": REPO_ROOT
    / "hermes-skills"
    / "pure-trm-trainer"
    / "runs"
    / "wiki_card_routerbench_qwen2b_4bit_full13_compact",
    "Router ckpt10": REPO_ROOT
    / "hermes-skills"
    / "pure-trm-trainer"
    / "runs"
    / "wiki_card_routerbench_qwen2b_ckpt10",
    "Safe adapter": REPO_ROOT
    / "hermes-skills"
    / "pure-trm-trainer"
    / "runs"
    / "wiki_card_routerbench_qwen2b_safe_final_cap13",
}

SAFE_TRIVIA_RUN = TRIVIA_RUNS["Safe adapter"]

STORYWORLD_RUNS = {
    "Post-train 6144": REPO_ROOT
    / "hermes-skills"
    / "storyworld-conveyor"
    / "context_port_runs"
    / "usual_suspects_qwen2b_4gb_posttrain"
    / "reports"
    / "phase_events.jsonl",
    "Phase-only 6144": REPO_ROOT
    / "hermes-skills"
    / "storyworld-conveyor"
    / "context_port_runs"
    / "abstract_letters_qwen2b_phase_only"
    / "reports"
    / "phase_events.jsonl",
    "Ultra-small 4096": REPO_ROOT
    / "hermes-skills"
    / "storyworld-conveyor"
    / "context_port_runs"
    / "usual_suspects_qwen2b_4gb_ultrasmall"
    / "reports"
    / "phase_events.jsonl",
}

STORYWORLD_SMOKE_SUMMARY = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "context_port_runs" / "mcp_trm_smoke_qwen35_2b" / "summary.json"

STORYWORLD_ARTIFACTS = {
    "France→Germany": REPO_ROOT / "storyworlds" / "france_to_germany_machiavellian_p.json",
    "Hive→Glam": REPO_ROOT / "storyworlds" / "hive_to_glam_machiavellian.json",
    "Shadow→Bio": REPO_ROOT / "storyworlds" / "shadow_to_bio_grudger.json",
}

PHASE_ORDER = [
    "plan",
    "characterize",
    "encounter_build",
    "act_complete",
    "recharacterize",
    "late_stage_holistic",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def ensure_dirs() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    GEN_DIR.mkdir(parents=True, exist_ok=True)


def set_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 170,
            "savefig.dpi": 220,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 8,
            "font.family": "DejaVu Sans",
        }
    )


def kb(path: Path) -> float:
    return path.stat().st_size / 1024.0


def plot_trivia_accuracy(trivia_summaries: dict[str, dict]) -> None:
    labels = list(trivia_summaries.keys())
    closed = [trivia_summaries[label]["conditions"]["closed_book"]["accuracy"] for label in labels]
    stuffed = [trivia_summaries[label]["conditions"]["stuffed"]["accuracy"] for label in labels]
    mcp = [trivia_summaries[label]["conditions"]["mcp_routed"]["accuracy"] for label in labels]
    route = [trivia_summaries[label]["conditions"]["mcp_routed"]["route_accuracy"] or 0.0 for label in labels]

    x = np.arange(len(labels))
    width = 0.18
    colors = {
        "closed": "#455A64",
        "stuffed": "#C44E52",
        "mcp": "#2E8B57",
        "route": "#DD8452",
    }

    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    bars = [
        ax.bar(x - 1.5 * width, closed, width, label="Closed-book acc.", color=colors["closed"]),
        ax.bar(x - 0.5 * width, stuffed, width, label="Stuffed acc.", color=colors["stuffed"]),
        ax.bar(x + 0.5 * width, mcp, width, label="MCP answer acc.", color=colors["mcp"]),
        ax.bar(x + 1.5 * width, route, width, label="MCP route acc.", color=colors["route"], hatch="//"),
    ]
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Accuracy")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Trivia Bench: Answer Accuracy vs. Route Fidelity")
    ax.legend(ncol=2, loc="upper center")

    for group in bars:
        for bar in group:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.02,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()
    fig.savefig(FIG_DIR / "trivia_accuracy.png", bbox_inches="tight")
    plt.close(fig)


def plot_trivia_histograms(safe_results: list[dict]) -> None:
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for row in safe_results:
        by_condition[row["condition"]].append(row)

    colors = {
        "closed_book": "#455A64",
        "stuffed": "#C44E52",
        "mcp_routed": "#2E8B57",
    }
    labels = {
        "closed_book": "Closed-book",
        "stuffed": "Stuffed",
        "mcp_routed": "MCP-routed",
    }

    fig, axes = plt.subplots(1, 3, figsize=(13.4, 3.8))

    for condition, rows in by_condition.items():
        axes[0].hist(
            [row["answer_prompt_tokens"] for row in rows],
            bins=7,
            alpha=0.55,
            label=labels[condition],
            color=colors[condition],
        )
        axes[2].hist(
            [row["answer_latency_sec"] for row in rows],
            bins=7,
            alpha=0.55,
            label=labels[condition],
            color=colors[condition],
        )

    for condition in ("stuffed", "mcp_routed"):
        rows = by_condition[condition]
        axes[1].hist(
            [row["retrieved_tokens_est"] for row in rows],
            bins=7,
            alpha=0.6,
            label=labels[condition],
            color=colors[condition],
        )

    axes[0].set_title("Answer Prompt Tokens")
    axes[0].set_xlabel("Tokens")
    axes[0].set_ylabel("Question count")
    axes[1].set_title("Retrieved Evidence Tokens")
    axes[1].set_xlabel("Tokens")
    axes[2].set_title("Answer Latency")
    axes[2].set_xlabel("Seconds")

    for ax in axes:
        ax.legend()

    fig.suptitle("Trivia Bench: Distribution Shifts Under MCP", y=1.03, fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "trivia_histograms.png", bbox_inches="tight")
    plt.close(fig)


def collect_storyworld_rows() -> tuple[list[dict], dict[str, list[dict]]]:
    all_rows: list[dict] = []
    per_run: dict[str, list[dict]] = {}
    for label, path in STORYWORLD_RUNS.items():
        rows = load_jsonl(path)
        for row in rows:
            row["_run_label"] = label
        per_run[label] = rows
        all_rows.extend(rows)
    return all_rows, per_run


def plot_storyworld_histograms(per_run: dict[str, list[dict]]) -> None:
    colors = {
        "Post-train 6144": "#4C72B0",
        "Phase-only 6144": "#8172B2",
        "Ultra-small 4096": "#55A868",
    }

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.0))
    for label, rows in per_run.items():
        prompt_tokens = [row["prompt_estimated_tokens"] for row in rows]
        latencies = [row["latency_ms"] / 1000.0 for row in rows]
        axes[0].hist(prompt_tokens, bins=7, alpha=0.6, label=f"{label} (n={len(rows)})", color=colors[label])
        axes[1].hist(latencies, bins=7, alpha=0.6, label=f"{label} (n={len(rows)})", color=colors[label])

    axes[0].set_title("Estimated Prompt Tokens")
    axes[0].set_xlabel("Tokens")
    axes[0].set_ylabel("Phase-event count")
    axes[1].set_title("Phase Latency")
    axes[1].set_xlabel("Seconds")

    for ax in axes:
        ax.legend()

    fig.suptitle("Storyworld Environment Study: Context-Bounded Phase Distributions", y=1.03, fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "storyworld_histograms.png", bbox_inches="tight")
    plt.close(fig)


def plot_storyworld_phase_breakdown(all_rows: list[dict]) -> None:
    phase_latency: dict[str, list[float]] = defaultdict(list)
    phase_fallback: dict[str, list[int]] = defaultdict(list)
    for row in all_rows:
        phase_latency[row["phase"]].append(row["latency_ms"] / 1000.0)
        phase_fallback[row["phase"]].append(1 if row.get("fallback_used") else 0)

    phases = [phase for phase in PHASE_ORDER if phase in phase_latency]
    mean_latency = [statistics.mean(phase_latency[phase]) for phase in phases]
    fallback_rate = [statistics.mean(phase_fallback[phase]) for phase in phases]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.2))
    axes[0].barh(phases, mean_latency, color="#4C72B0")
    axes[0].set_title("Mean Phase Latency")
    axes[0].set_xlabel("Seconds")

    axes[1].barh(phases, fallback_rate, color="#DD8452")
    axes[1].set_title("Fallback Rate")
    axes[1].set_xlabel("Fraction of events")
    axes[1].set_xlim(0, 1.0)

    fig.suptitle("Storyworld MCP Phases: Runtime and Fallback Profile", y=1.03, fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "storyworld_phase_breakdown.png", bbox_inches="tight")
    plt.close(fig)


def plot_storyworld_artifacts() -> None:
    labels = list(STORYWORLD_ARTIFACTS.keys())
    sizes_kb = [kb(path) for path in STORYWORLD_ARTIFACTS.values()]
    colors = ["#2E8B57", "#C44E52", "#4C72B0"]

    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    bars = ax.bar(labels, sizes_kb, color=colors)
    ax.set_ylabel("Artifact size (KB)")
    ax.set_title("Storyworld Outputs Emitted Beyond the Working Prompt Window")

    for bar, value in zip(bars, sizes_kb):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1.2,
            f"{value:.1f} KB",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(FIG_DIR / "storyworld_artifacts.png", bbox_inches="tight")
    plt.close(fig)


def fmt(value: float) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "--"
    return f"{value:.3f}"


def write_generated_tables(trivia_summaries: dict[str, dict], safe_results: list[dict], all_storyworld_rows: list[dict], per_storyworld_run: dict[str, list[dict]], smoke_summary: dict) -> None:
    trivia_lines = [
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"Run & Closed & Stuffed & MCP & Route & Avg. answer prompt & Avg. retrieved \\",
        r"\midrule",
    ]
    for label, summary in trivia_summaries.items():
        mcp = summary["conditions"]["mcp_routed"]
        trivia_lines.append(
            f"{label} & "
            f"{fmt(summary['conditions']['closed_book']['accuracy'])} & "
            f"{fmt(summary['conditions']['stuffed']['accuracy'])} & "
            f"{fmt(mcp['accuracy'])} & "
            f"{fmt(mcp['route_accuracy'] or 0.0)} & "
            f"{fmt(mcp['avg_answer_prompt_tokens'])} & "
            f"{fmt(mcp['avg_retrieved_tokens_est'])} \\\\"
        )
    trivia_lines.extend([r"\bottomrule", r"\end{tabular}"])
    (GEN_DIR / "trivia_table.tex").write_text("\n".join(trivia_lines) + "\n", encoding="utf-8")

    story_lines = [
        r"\begin{tabular}{lccccc}",
        r"\toprule",
        r"Run & Context budget & Events & Mean prompt & Mean latency (s) & Fallbacks \\",
        r"\midrule",
    ]
    for label, rows in per_storyworld_run.items():
        mean_prompt = statistics.mean(row["prompt_estimated_tokens"] for row in rows)
        mean_latency = statistics.mean(row["latency_ms"] / 1000.0 for row in rows)
        fallbacks = sum(1 for row in rows if row.get("fallback_used"))
        context_budget = rows[0]["budget"]["context_budget_tokens"]
        story_lines.append(
            f"{label} & {context_budget} & {len(rows)} & {mean_prompt:.1f} & {mean_latency:.2f} & {fallbacks} \\\\"
        )
    story_lines.extend([r"\bottomrule", r"\end{tabular}"])
    (GEN_DIR / "storyworld_table.tex").write_text("\n".join(story_lines) + "\n", encoding="utf-8")

    safe_summary = trivia_summaries["Safe adapter"]
    safe_conditions = safe_summary["conditions"]
    artifact_sizes = {label: kb(path) for label, path in STORYWORLD_ARTIFACTS.items()}
    story_counter = Counter(row["phase"] for row in all_storyworld_rows)
    mean_story_prompt = statistics.mean(row["prompt_estimated_tokens"] for row in all_storyworld_rows)
    mean_story_latency = statistics.mean(row["latency_ms"] / 1000.0 for row in all_storyworld_rows)
    story_fallback_rate = statistics.mean(1 if row.get("fallback_used") else 0 for row in all_storyworld_rows)

    metrics = {
        "title": "TRM for MCP: Context for Free",
        "trivia_safe_closed_accuracy": safe_conditions["closed_book"]["accuracy"],
        "trivia_safe_stuffed_accuracy": safe_conditions["stuffed"]["accuracy"],
        "trivia_safe_mcp_accuracy": safe_conditions["mcp_routed"]["accuracy"],
        "trivia_safe_route_accuracy": safe_conditions["mcp_routed"]["route_accuracy"],
        "trivia_safe_prompt_tokens": safe_conditions["mcp_routed"]["avg_answer_prompt_tokens"],
        "trivia_safe_retrieved_tokens": safe_conditions["mcp_routed"]["avg_retrieved_tokens_est"],
        "trivia_safe_questions": safe_summary["question_count"],
        "storyworld_smoke_tool_accuracy": smoke_summary["tool_accuracy"],
        "storyworld_smoke_queries": smoke_summary["total_queries"],
        "storyworld_phase_events": len(all_storyworld_rows),
        "storyworld_mean_prompt_tokens": mean_story_prompt,
        "storyworld_mean_latency_sec": mean_story_latency,
        "storyworld_fallback_rate": story_fallback_rate,
        "storyworld_phase_counts": dict(story_counter),
        "artifact_sizes_kb": artifact_sizes,
    }
    (GEN_DIR / "metrics_summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    macros = [
        f"\\newcommand{{\\PaperTitle}}{{{metrics['title']}}}",
        f"\\newcommand{{\\TriviaQuestionCount}}{{{safe_summary['question_count']}}}",
        f"\\newcommand{{\\TriviaClosedSafe}}{{{fmt(metrics['trivia_safe_closed_accuracy'])}}}",
        f"\\newcommand{{\\TriviaStuffedSafe}}{{{fmt(metrics['trivia_safe_stuffed_accuracy'])}}}",
        f"\\newcommand{{\\TriviaMcpSafe}}{{{fmt(metrics['trivia_safe_mcp_accuracy'])}}}",
        f"\\newcommand{{\\TriviaRouteSafe}}{{{fmt(metrics['trivia_safe_route_accuracy'])}}}",
        f"\\newcommand{{\\TriviaPromptSafe}}{{{safe_conditions['mcp_routed']['avg_answer_prompt_tokens']:.1f}}}",
        f"\\newcommand{{\\TriviaRetrievedSafe}}{{{safe_conditions['mcp_routed']['avg_retrieved_tokens_est']:.1f}}}",
        f"\\newcommand{{\\StoryworldToolAcc}}{{{fmt(metrics['storyworld_smoke_tool_accuracy'])}}}",
        f"\\newcommand{{\\StoryworldSmokeQueries}}{{{smoke_summary['total_queries']}}}",
        f"\\newcommand{{\\StoryworldEventCount}}{{{len(all_storyworld_rows)}}}",
        f"\\newcommand{{\\StoryworldMeanPrompt}}{{{mean_story_prompt:.1f}}}",
        f"\\newcommand{{\\StoryworldMeanLatency}}{{{mean_story_latency:.1f}}}",
        f"\\newcommand{{\\StoryworldFallbackRate}}{{{fmt(story_fallback_rate)}}}",
        f"\\newcommand{{\\ArtifactFranceGermanyKB}}{{{artifact_sizes['France→Germany']:.1f}}}",
        f"\\newcommand{{\\ArtifactHiveGlamKB}}{{{artifact_sizes['Hive→Glam']:.1f}}}",
        f"\\newcommand{{\\ArtifactShadowBioKB}}{{{artifact_sizes['Shadow→Bio']:.1f}}}",
    ]
    (GEN_DIR / "metrics_macros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    set_style()

    trivia_summaries = {label: load_json(path / "summary.json") for label, path in TRIVIA_RUNS.items()}
    safe_results = load_jsonl(SAFE_TRIVIA_RUN / "results.jsonl")
    storyworld_rows, per_storyworld_run = collect_storyworld_rows()
    smoke_summary = load_json(STORYWORLD_SMOKE_SUMMARY)

    plot_trivia_accuracy(trivia_summaries)
    plot_trivia_histograms(safe_results)
    plot_storyworld_histograms(per_storyworld_run)
    plot_storyworld_phase_breakdown(storyworld_rows)
    plot_storyworld_artifacts()
    write_generated_tables(trivia_summaries, safe_results, storyworld_rows, per_storyworld_run, smoke_summary)

    print(f"Wrote figures to {FIG_DIR}")
    print(f"Wrote generated tables/macros to {GEN_DIR}")


if __name__ == "__main__":
    main()
