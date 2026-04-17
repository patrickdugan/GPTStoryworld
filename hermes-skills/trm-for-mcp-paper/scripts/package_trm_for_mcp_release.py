from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def maybe_git_rev(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip()
    except Exception:
        return ""


def collect_manifest(root: Path, bundle_name: str) -> dict:
    paper_root = root / "papers" / "trm_for_mcp"
    generated_root = paper_root / "generated"
    metrics_path = generated_root / "metrics_summary.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}

    trivia_root = root / "hermes-skills" / "pure-trm-trainer" / "runs"
    story_root = root / "hermes-skills" / "storyworld-conveyor" / "context_port_runs"
    storyworlds_root = root / "storyworlds"

    def rel(path: Path) -> str:
        return str(path.resolve()).replace("\\", "/")

    return {
        "bundle_name": bundle_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": rel(root),
        "git_revision": maybe_git_rev(root),
        "paper_title": metrics.get("title", "TRM for MCP: Context for Free"),
        "paper_workspace": rel(paper_root),
        "manuscript": rel(paper_root / "trm_for_mcp_context_for_free.tex"),
        "included_optional_pdf": rel(paper_root / "trm_for_mcp_context_for_free.pdf")
        if (paper_root / "trm_for_mcp_context_for_free.pdf").exists()
        else "",
        "generated_assets": {
            "figures_dir": rel(paper_root / "figures"),
            "generated_dir": rel(generated_root),
            "metrics_summary": rel(metrics_path) if metrics_path.exists() else "",
        },
        "source_runs": {
            "trivia": {
                "base_compact": {
                    "summary": rel(trivia_root / "wiki_card_routerbench_qwen2b_4bit_full13_compact" / "summary.json"),
                    "scorecard": rel(trivia_root / "wiki_card_routerbench_qwen2b_4bit_full13_compact" / "scorecard.json"),
                    "results": rel(trivia_root / "wiki_card_routerbench_qwen2b_4bit_full13_compact" / "results.jsonl"),
                },
                "router_ckpt10": {
                    "summary": rel(trivia_root / "wiki_card_routerbench_qwen2b_ckpt10" / "summary.json"),
                    "scorecard": rel(trivia_root / "wiki_card_routerbench_qwen2b_ckpt10" / "scorecard.json"),
                    "results": rel(trivia_root / "wiki_card_routerbench_qwen2b_ckpt10" / "results.jsonl"),
                },
                "safe_final": {
                    "summary": rel(trivia_root / "wiki_card_routerbench_qwen2b_safe_final_cap13" / "summary.json"),
                    "scorecard": rel(trivia_root / "wiki_card_routerbench_qwen2b_safe_final_cap13" / "scorecard.json"),
                    "results": rel(trivia_root / "wiki_card_routerbench_qwen2b_safe_final_cap13" / "results.jsonl"),
                },
            },
            "storyworld": {
                "posttrain_6144": rel(story_root / "usual_suspects_qwen2b_4gb_posttrain" / "reports" / "phase_events.jsonl"),
                "phase_only_6144": rel(story_root / "abstract_letters_qwen2b_phase_only" / "reports" / "phase_events.jsonl"),
                "ultrasmall_4096": rel(story_root / "usual_suspects_qwen2b_4gb_ultrasmall" / "reports" / "phase_events.jsonl"),
                "smoke_summary": rel(story_root / "mcp_trm_smoke_qwen35_2b" / "summary.json"),
            },
            "storyworld_artifacts": {
                "france_to_germany": rel(storyworlds_root / "france_to_germany_machiavellian_p.json"),
                "hive_to_glam": rel(storyworlds_root / "hive_to_glam_machiavellian.json"),
                "shadow_to_bio": rel(storyworlds_root / "shadow_to_bio_grudger.json"),
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a release bundle for the TRM for MCP paper.")
    parser.add_argument("--bundle-name", default="", help="Optional release directory name. Defaults to a UTC-stamped bundle.")
    parser.add_argument("--skip-rebuild", action="store_true", help="Skip rebuilding paper assets before packaging.")
    parser.add_argument("--no-zip", action="store_true", help="Skip creating a zip archive alongside the release directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print the intended bundle path without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    paper_root = root / "papers" / "trm_for_mcp"
    bundle_name = args.bundle_name or f"release_{utc_stamp()}"
    release_root = paper_root / "releases" / bundle_name

    if args.dry_run:
        print(str(release_root))
        return 0

    if not args.skip_rebuild:
        build_wrapper = root / "hermes-skills" / "trm-for-mcp-paper" / "scripts" / "build_trm_for_mcp_paper.py"
        subprocess.run([sys.executable, str(build_wrapper)], cwd=str(root), check=True)

    release_root.mkdir(parents=True, exist_ok=True)

    copy_file(paper_root / "trm_for_mcp_context_for_free.tex", release_root / "trm_for_mcp_context_for_free.tex")
    copy_file(paper_root / "build_assets.py", release_root / "build_assets.py")
    copy_tree(paper_root / "figures", release_root / "figures")
    copy_tree(paper_root / "generated", release_root / "generated")

    pdf_path = paper_root / "trm_for_mcp_context_for_free.pdf"
    if pdf_path.exists():
        copy_file(pdf_path, release_root / pdf_path.name)

    manifest = collect_manifest(root, bundle_name)
    zip_path = ""
    if not args.no_zip:
        archive_base = str(release_root)
        zip_path = shutil.make_archive(archive_base, "zip", root_dir=str(release_root.parent), base_dir=release_root.name)
    manifest["bundle_dir"] = str(release_root).replace("\\", "/")
    manifest["zip_archive"] = zip_path.replace("\\", "/") if zip_path else ""
    (release_root / "release_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(str(release_root))
    if zip_path:
        print(zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
