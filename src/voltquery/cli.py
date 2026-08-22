"""VoltQuery command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .seed import check_m0, validate_corpus, validate_sources
from .seed.issues import Severity, ValidationIssue

# Root is the repo directory (parent of the ``src`` layout).
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _default_paths() -> tuple[Path, Path, Path]:
    return (
        _REPO_ROOT / "data" / "sources.yaml",
        _REPO_ROOT / "benchmarks" / "seed" / "problems.jsonl",
        _REPO_ROOT / "benchmarks" / "seed",
    )


def _add_path_args(cmd: argparse.ArgumentParser) -> None:
    cmd.add_argument(
        "--sources",
        default=None,
        help="Path to data/sources.yaml (default: repo default).",
    )
    cmd.add_argument(
        "--corpus",
        default=None,
        help="Path to benchmarks/seed/problems.jsonl (default: repo default).",
    )
    cmd.add_argument(
        "--assets",
        default=None,
        help="Root directory of the corpus assets (default: benchmarks/seed).",
    )


def _paths_from(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    sources_path, corpus_path, assets_root = _default_paths()
    if getattr(args, "sources", None) is not None:
        sources_path = Path(args.sources)
    if getattr(args, "corpus", None) is not None:
        corpus_path = Path(args.corpus)
    if getattr(args, "assets", None) is not None:
        assets_root = Path(args.assets)
    return sources_path, corpus_path, assets_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voltquery",
        description=(
            "VoltQuery - Electrical Engineering problem search & "
            "verification baseline tooling."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate source registry and seed corpus.")
    _add_path_args(validate)

    milestone = sub.add_parser("milestone", help="Check milestone completeness gates.")
    milestone_sub = milestone.add_subparsers(dest="milestone_name", required=True)
    m0 = milestone_sub.add_parser(
        "m0",
        help="Check the M0 seed corpus + benchmark contract gate.",
    )
    _add_path_args(m0)
    return parser


def _render(issues: list[ValidationIssue]) -> int:
    for issue in issues:
        print(
            f"[{issue.severity.value.upper():7}] {issue.code}: {issue.message}"
            f"  ({issue.path})"
        )
    errors = [issue for issue in issues if issue.severity == Severity.ERROR]
    print(f"checked: {len(issues)} issue(s), {len(errors)} error(s)")
    return 1 if errors else 0


def _run_validate(args: argparse.Namespace) -> int:
    sources_path, corpus_path, assets_root = _paths_from(args)
    issues: list[ValidationIssue] = list(validate_sources(sources_path))
    issues.extend(validate_corpus(corpus_path, sources_path, assets_root))
    return _render(issues)


def _run_milestone_m0(args: argparse.Namespace) -> int:
    sources_path, corpus_path, assets_root = _paths_from(args)
    return _render(check_m0(corpus_path, sources_path, assets_root))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return _run_validate(args)
    if args.command == "milestone" and args.milestone_name == "m0":
        return _run_milestone_m0(args)

    parser.print_help()
    return 0
