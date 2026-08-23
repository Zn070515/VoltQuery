"""VoltQuery command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .seed import (
    check_m0,
    check_public_gold_policy,
    validate_corpus,
    validate_documents,
    validate_problem_ir,
    validate_sources,
)
from .seed.issues import Severity, ValidationIssue

# Root is the repo directory (parent of the ``src`` layout).
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _default_paths() -> tuple[Path, Path, Path]:
    return (
        _REPO_ROOT / "data" / "sources.yaml",
        _REPO_ROOT / "benchmarks" / "seed" / "problems.jsonl",
        _REPO_ROOT / "benchmarks" / "seed",
    )


def _default_documents_path() -> Path:
    return _REPO_ROOT / "data" / "documents.yaml"


def _default_ir_path() -> Path:
    return _REPO_ROOT / "benchmarks" / "seed" / "problem_ir.jsonl"


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
    cmd.add_argument(
        "--documents",
        default=None,
        help="Path to data/documents.yaml (default: repo default).",
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


def _documents_from(args: argparse.Namespace) -> Path:
    documents_path = _default_documents_path()
    if getattr(args, "documents", None) is not None:
        documents_path = Path(args.documents)
    return documents_path


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

    policy = sub.add_parser(
        "policy",
        help="Enforce a corpus policy gate (independent of count targets).",
    )
    policy_sub = policy.add_subparsers(dest="policy_name", required=True)
    pub_gold = policy_sub.add_parser(
        "public-gold",
        help=(
            "Check every problem source is approved + verified + "
            "public_redistributable + redistribution (no count targets)."
        ),
    )
    _add_path_args(pub_gold)

    ir = sub.add_parser("ir", help="Validate the M1 problem IR corpus.")
    ir_sub = ir.add_subparsers(dest="ir_command", required=True)
    ir_validate = ir_sub.add_parser(
        "validate",
        help="Validate problem_ir.jsonl and its seed<->IR parity.",
    )
    _add_ir_args(ir_validate)
    return parser


def _add_ir_args(cmd: argparse.ArgumentParser) -> None:
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
        "--documents",
        default=None,
        help="Path to data/documents.yaml (default: repo default).",
    )
    cmd.add_argument(
        "--ir",
        default=None,
        help="Path to benchmarks/seed/problem_ir.jsonl (default: repo default).",
    )


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
    issues.extend(validate_documents(_documents_from(args)))
    issues.extend(validate_corpus(corpus_path, sources_path, assets_root, _documents_from(args)))
    return _render(issues)


def _run_milestone_m0(args: argparse.Namespace) -> int:
    sources_path, corpus_path, assets_root = _paths_from(args)
    return _render(check_m0(corpus_path, sources_path, assets_root, _documents_from(args)))


def _run_policy_public_gold(args: argparse.Namespace) -> int:
    sources_path, corpus_path, _assets_root = _paths_from(args)
    return _render(check_public_gold_policy(corpus_path, sources_path))


def _run_ir_validate(args: argparse.Namespace) -> int:
    sources_path, corpus_path, _assets_root = _paths_from(args)
    ir_path = Path(args.ir) if args.ir else None
    if ir_path is None:
        ir_path = _default_ir_path()
    return _render(
        validate_problem_ir(corpus_path, ir_path, sources_path, _documents_from(args))
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return _run_validate(args)
    if args.command == "milestone" and args.milestone_name == "m0":
        return _run_milestone_m0(args)
    if args.command == "policy" and args.policy_name == "public-gold":
        return _run_policy_public_gold(args)
    if args.command == "ir" and args.ir_command == "validate":
        return _run_ir_validate(args)

    parser.print_help()
    return 0
