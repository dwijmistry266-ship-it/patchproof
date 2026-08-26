from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .diff import parse_unified_diff
from .policy import PolicyError, evaluate_policy, load_policy
from .report import build_report, render_json, render_markdown
from .runner import run_commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create evidence-first reports for repository changes.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="Analyze a unified diff and produce reports")
    check.add_argument("--diff", required=True, type=Path, help="Path to a unified diff fixture")
    check.add_argument("--config", type=Path, default=None, help="Path to a JSON policy")
    check.add_argument("--output-dir", type=Path, default=Path("patchproof-report"))
    check.add_argument("--cwd", type=Path, default=None, help="Working directory for evidence commands")
    return parser


def run_check(args: argparse.Namespace) -> int:
    try:
        diff_text = args.diff.read_text(encoding="utf-8")
        summary = parse_unified_diff(diff_text)
        policy = load_policy(args.config)
        findings = evaluate_policy(summary, policy)
        commands = run_commands(
            policy["commands"],
            timeout_seconds=policy["limits"]["command_timeout_seconds"],
            max_output_bytes=policy["limits"]["max_output_bytes"],
            cwd=str(args.cwd) if args.cwd else None,
        )
        report = build_report(summary, findings, commands)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "report.json").write_text(render_json(report), encoding="utf-8")
        (args.output_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")
        print(f"PatchProof status: {report.overall_status}")
        print(f"Reports written to: {args.output_dir.resolve()}")
        return 1 if report.overall_status == "error" else 0
    except (OSError, ValueError, PolicyError) as error:
        print(f"PatchProof error: {error}", file=sys.stderr)
        return 2


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "check":
        raise SystemExit(run_check(args))


if __name__ == "__main__":
    main()
