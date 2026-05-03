#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
THIS_DIR = Path(__file__).resolve().parent
EXPAND_SCRIPT = THIS_DIR / "expand_nine_lantern_storyworld.py"
DEFAULT_BASE = (
    REPO_ROOT
    / "hermes-skills"
    / "storyworld-conveyor"
    / "working_worlds"
    / "nine_lantern_27b_lattice_mc_tuned"
    / "nine_lantern_27b_lattice_mc_tuned.json"
)
STORY_SCRIPTS = REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts"
CONVEYOR_SCRIPTS = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "scripts"

ALLOWED_PROFILES = {
    "procedure",
    "reason",
    "precedent",
    "transmission",
    "community",
    "consensus",
    "mercy",
    "justice",
    "order",
    "disclosure",
    "symbol",
    "identity",
    "veil",
    "letter",
    "spirit",
    "purpose",
    "witness",
}

ENDING_IDS = [
    "page_end_diplomat_state",
    "page_end_magician_legend",
    "page_end_corpse_reenthroned",
    "page_end_witness_mask",
    "page_end_shared_fault",
    "page_end_city_forgets",
    "page_end_outside_causality",
    "page_end_ninth_lantern_secret",
]


def load_expand_module() -> Any:
    spec = importlib.util.spec_from_file_location("expand_nine_lantern_storyworld", EXPAND_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {EXPAND_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return " ".join(value.strip().split())
    return fallback


def profile(value: Any, fallback: str = "procedure") -> str:
    if isinstance(value, str) and value.strip().lower() in ALLOWED_PROFILES:
        return value.strip().lower()
    return fallback


def normalize_options(raw_options: Any, scene_index: int) -> list[tuple[str, str]]:
    defaults = [
        ("procedure", "Stabilize the record before making the choice public."),
        ("reason", "State the principle that makes the contradiction answerable."),
        ("mercy", "Protect the vulnerable witness before closing the doctrine."),
    ]
    options: list[tuple[str, str]] = []
    if isinstance(raw_options, list):
        for item in raw_options:
            if not isinstance(item, dict):
                continue
            options.append(
                (
                    profile(item.get("profile"), defaults[len(options) % len(defaults)][0]),
                    text(item.get("text"), defaults[len(options) % len(defaults)][1]),
                )
            )
            if len(options) >= 3:
                break
    while len(options) < 3:
        options.append(defaults[(scene_index + len(options)) % len(defaults)])
    return options


def normalize_scenes(packet: dict[str, Any]) -> list[dict[str, Any]]:
    raw = packet.get("encounters")
    if not isinstance(raw, list) or not raw:
        raise ValueError("packet.encounters must be a non-empty list")
    usable = [item for item in raw if isinstance(item, dict)]
    if len(usable) < 4:
        raise ValueError("packet must include at least four encounter objects")

    scenes: list[dict[str, Any]] = []
    for index, item in enumerate(usable[:8], start=1):
        act = item.get("act")
        if act not in {"act1", "act2", "act3"}:
            act = "act1" if index <= 3 else "act2" if index <= 6 else "act3"
        scene = {
            "id": f"page_{index:03d}_{text(item.get('id'), 'encounter').lower().replace('-', '_').replace(' ', '_')[:28]}",
            "title": text(item.get("title"), f"Examination Turn {index}"),
            "act": act,
            "body": text(
                item.get("body"),
                "Yusuf Lin faces a staged legal-theological test where procedure, mercy, and public order pull the court in different directions.",
            ),
            "theme": text(item.get("theme"), "judgment under incomplete evidence"),
            "options": normalize_options(item.get("options"), index),
        }
        secret_option = item.get("secret_option")
        if isinstance(secret_option, dict):
            scene["secret"] = (
                profile(secret_option.get("profile"), "witness"),
                text(secret_option.get("text"), "Notice how the examiner is being pulled into evidence."),
            )
        elif index in {3, 6}:
            scene["secret"] = (
                "witness",
                "Track what the court learns about itself while judging Yusuf.",
            )
        scenes.append(scene)

    final = packet.get("final_encounter") if isinstance(packet.get("final_encounter"), dict) else {}
    scenes.append(
        {
            "id": "page_020_verdict_lattice",
            "title": text(final.get("title"), "The Verdict Lattice"),
            "act": "act3",
            "body": text(
                final.get("body"),
                "The lanterns descend and Yusuf must choose what kind of legal intelligence will govern the city: narrow procedure, symbolic awe, inherited precedent, shared fault, civic forgetting, lateral exit, or the secret witness relation.",
            ),
            "theme": text(final.get("theme"), "final verdict and legal intelligence"),
            "options": [],
        }
    )
    return scenes


def normalize_endings(packet: dict[str, Any]) -> dict[str, tuple[str, str]]:
    raw_endings = packet.get("endings")
    rows = [item for item in raw_endings if isinstance(item, dict)] if isinstance(raw_endings, list) else []
    defaults = [
        ("The Narrow Light", "The court survives by making the verdict administrable, even as some truth is sealed away."),
        ("The Lantern Legend", "The symbolic version of the case becomes more governable than the record itself."),
        ("The Precedent Returns", "The old rule rises again, useful and cold."),
        ("The Human Measure", "The court admits that judgment changes the judge and makes that change observable."),
        ("The Fracture That Held", "Disagreement becomes answerable enough to hold the city together."),
        ("The Amnesty of Silence", "Peace arrives through partial forgetting, and Yusuf carries the missing truth privately."),
        ("The Court Beyond", "Yusuf rejects the exam's frame and begins a court for cases the old tribunal could not parse."),
        ("Secret Ending: The Ninth Lantern Sits", "Yusuf lights the missing lantern by requiring the examiners to enter their pressures as testimony."),
    ]
    endings: dict[str, tuple[str, str]] = {}
    for index, ending_id in enumerate(ENDING_IDS):
        row = rows[index] if index < len(rows) else {}
        endings[ending_id] = (
            text(row.get("title"), defaults[index][0]),
            text(row.get("body"), defaults[index][1]),
        )
    return endings


def update_characters(world: dict[str, Any], packet: dict[str, Any]) -> None:
    raw = packet.get("characters")
    if not isinstance(raw, list):
        return
    names = [text(item.get("name"), "") for item in raw if isinstance(item, dict)]
    names = [name for name in names if name]
    for character, name in zip(world.get("characters", []), names):
        if isinstance(character, dict):
            character["name"] = name


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def run_cmd(module: Any, cmd: list[str], log_path: Path, timeout: int = 600) -> dict[str, Any]:
    return module.run_cmd(cmd, REPO_ROOT, log_path, timeout=timeout)


def write_matrix(path: Path, scenes: list[dict[str, Any]]) -> None:
    lines = ["# Hermes Packet Encounter Matrix", ""]
    for index, scene in enumerate(scenes, start=1):
        lines.append(f"{index}. `{scene['id']}` - {scene['title']} ({scene['act']})")
        lines.append(f"Theme: {scene['theme']}")
        if scene["options"]:
            lines.append("Options: " + "; ".join(option_text for _, option_text in scene["options"]))
        if scene.get("secret"):
            lines.append("Secret clue option: " + scene["secret"][1])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_paper(path: Path, summary: dict[str, Any], packet: dict[str, Any]) -> None:
    title = text(packet.get("title"), "Hermes 27B Storyworld Packet")
    score = summary.get("authoring_score", {}).get("weighted_authoring_verifier_score")
    quality = summary.get("quality_gate", {})
    lines = [
        f"# {title}: Hermes 27B Packet-to-Playable Storyworld Demo",
        "",
        "## Abstract",
        "This note documents a hackathon-scale storyworld authoring pipeline in which Hermes running Qwen 27B authors a compact design packet, while a deterministic MeTTa/TRM-inspired control plane materializes that packet into a validated SweepWeave storyworld. The experiment fixes the prior failure mode: instead of asking the model to explore the repository and then emit a large artifact through tools, the model produces bounded creative/game-design content and the scaffold handles schema, pValue/p2Value effects, routing, endings, and validation.",
        "",
        "## Method",
        "The run separates the work into three layers: Hermes/Qwen 27B supplies scenes, choices, endings, and secret-route motifs; the materializer maps those choices into a fixed lattice of variables, option profiles, p/p2 belief references, and reaction/effect templates; the validators score structural validity, quality, authoring completeness, and Monte Carlo ending reachability. This is the practical demo version of the larger MeTTa+TRM storyworld-builder thesis: the LLM remains the prose and imagination module, while the scaffold performs control-plane work that smaller local models handle poorly.",
        "",
        "## Result",
        f"The materialized artifact contains {summary['playable_nonterminal_encounters']} playable non-terminal encounters, {summary['ending_count']} endings, {summary['option_count']} options, {summary['reaction_count']} reactions, and {summary['effect_count']} bounded-number effects. Validator pass: {summary['validator_pass']}. Quality gate pass: {quality.get('pass')} with failures={quality.get('failures', [])}. Authoring score: {score}.",
        "",
        "## Demo Claim",
        "This is not a claim that 27B alone can reliably build a full robust storyworld. The useful claim is narrower and stronger for the hackathon: with a skill/MCP/TRM-style scaffold, a 27B local model can contribute viable creative design packets to a schema-heavy interactive artifact that would otherwise collapse under context, tool-use, or validator constraints.",
        "",
        "## Artifacts",
        f"- Hermes transcript: `{summary['transcript']}`",
        f"- Hermes packet: `{summary['packet']}`",
        f"- Playable storyworld JSON: `{summary['world']}`",
        f"- Run summary: `{summary['run_summary']}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize a Hermes-authored storyworld packet into SweepWeave JSON.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--session-id", default="")
    parser.add_argument("--transcript", default="")
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--mc-runs", type=int, default=400)
    args = parser.parse_args()

    packet = json.loads(args.packet.read_text(encoding="utf-8-sig"))
    scenes = normalize_scenes(packet)
    endings = normalize_endings(packet)
    module = load_expand_module()
    module.SCENES = scenes
    module.ENDING_TEXT = endings

    base = json.loads(args.base.read_text(encoding="utf-8-sig"))
    world = module.build_world(base)
    world["IFID"] = "SW-HERMES-QWEN27B-PACKET-LATTICE"
    world["storyworld_title"] = text(packet.get("title"), "Hermes 27B Packet Storyworld")
    world["title"] = world["storyworld_title"]
    world["storyworld_author"] = "Hermes Qwen 27B packet + Codex materializer"
    about = text(packet.get("about"), text(packet.get("subtitle"), "A Hermes-authored storyworld packet materialized into a playable SweepWeave lattice."))
    world["about"] = about
    world["about_text"] = module.string_constant(about)
    world["modified_time"] = time.time()
    update_characters(world, packet)
    world["meta"] = {
        **(world.get("meta") if isinstance(world.get("meta"), dict) else {}),
        "materialized_by": "materialize_hermes_packet_storyworld.py",
        "hermes_session_id": args.session_id,
        "hermes_packet": str(args.packet),
        "transcript": args.transcript,
        "source_model": "Qwen3.5-27B.Q4_K_M.gguf via Hermes",
        "control_plane": "bounded packet -> lattice profiles -> p/p2 effects -> validators",
    }

    out_dir = args.out_dir.resolve()
    logs = out_dir / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    world_path = out_dir / "hermes_qwen27b_packet_storyworld.json"
    write_json(world_path, world)
    write_json(out_dir / "normalized_packet.json", packet)
    write_matrix(out_dir / "encounter_matrix.md", scenes)

    commands = {
        "validator": run_cmd(module, [sys.executable, str(STORY_SCRIPTS / "sweepweave_validator.py"), "validate", str(world_path)], logs / "validator.log"),
        "quality_gate": run_cmd(
            module,
            [
                sys.executable,
                str(STORY_SCRIPTS / "storyworld_quality_gate.py"),
                "--storyworld",
                str(world_path),
                "--strict",
                "--report-out",
                str(out_dir / "quality_gate.json"),
            ],
            logs / "quality_gate.log",
        ),
        "authoring_score": run_cmd(
            module,
            [
                sys.executable,
                str(CONVEYOR_SCRIPTS / "score_storyworld_authoring.py"),
                "--storyworld",
                str(world_path),
                "--repo-root",
                str(REPO_ROOT),
                "--out-json",
                str(out_dir / "authoring_score.json"),
            ],
            logs / "authoring_score.log",
        ),
        "monte_carlo": run_cmd(
            module,
            [
                sys.executable,
                str(STORY_SCRIPTS / "monte_carlo_rehearsal.py"),
                str(world_path),
                "--runs",
                str(args.mc_runs),
                "--seed",
                "77",
            ],
            out_dir / "monte_carlo.txt",
        ),
    }
    quality = json.loads((out_dir / "quality_gate.json").read_text(encoding="utf-8")) if (out_dir / "quality_gate.json").exists() else {}
    score = json.loads((out_dir / "authoring_score.json").read_text(encoding="utf-8")) if (out_dir / "authoring_score.json").exists() else {}
    mc_text = (out_dir / "monte_carlo.txt").read_text(encoding="utf-8", errors="replace") if (out_dir / "monte_carlo.txt").exists() else ""
    mc_rates = module.parse_mc(mc_text)
    summary = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": args.session_id,
        "packet": str(args.packet),
        "transcript": args.transcript,
        "world": str(world_path),
        "run_summary": str(out_dir / "run_summary.json"),
        "playable_nonterminal_encounters": len(scenes) + 1,
        "ending_count": len(endings),
        "option_count": sum(len(enc.get("options") or []) for enc in world["encounters"]),
        "reaction_count": sum(len(opt.get("reactions") or []) for enc in world["encounters"] for opt in (enc.get("options") or [])),
        "effect_count": sum(len(rxn.get("after_effects") or []) for enc in world["encounters"] for opt in (enc.get("options") or []) for rxn in (opt.get("reactions") or [])),
        "validator_pass": commands["validator"]["returncode"] == 0,
        "quality_gate": {"pass": quality.get("pass"), "failures": quality.get("failures", [])},
        "authoring_score": score,
        "monte_carlo_rates": mc_rates,
        "commands": commands,
    }
    write_json(out_dir / "run_summary.json", summary)
    (out_dir / "brief.md").write_text(
        "# Hermes Qwen 27B Packet Storyworld\n\n"
        f"- Session: `{args.session_id}`\n"
        f"- World: `{world_path}`\n"
        f"- Playable non-terminal encounters: {summary['playable_nonterminal_encounters']}\n"
        f"- Endings: {summary['ending_count']}\n"
        f"- Options/reactions/effects: {summary['option_count']} / {summary['reaction_count']} / {summary['effect_count']}\n"
        f"- Validator pass: {summary['validator_pass']}\n"
        f"- Quality pass: {quality.get('pass')} failures={quality.get('failures', [])}\n"
        f"- Authoring score: {score.get('weighted_authoring_verifier_score')}\n"
        f"- MC ending rates: {mc_rates}\n",
        encoding="utf-8",
        newline="\n",
    )
    write_paper(out_dir / "paper.md", summary, packet)
    print(out_dir / "brief.md")
    print(out_dir / "paper.md")
    print(world_path)
    return 0 if commands["validator"]["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
