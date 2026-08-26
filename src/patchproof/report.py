from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from .models import ChangeSummary, CommandResult, CoverageSummary, EvidenceReport, Finding, TestSummary

TOOL_VERSION = "0.4.0-alpha"
SCHEMA_VERSION = "0.1"


def overall_status(findings: tuple[Finding, ...], commands: tuple[CommandResult, ...], test_summary: TestSummary | None = None, coverage_summary: CoverageSummary | None = None) -> str:
    if any(item.status == "error" for item in findings) or any(item.status == "error" for item in commands) or (test_summary is not None and test_summary.status == "error") or (coverage_summary is not None and coverage_summary.status == "error"):
        return "error"
    if any(item.status == "warning" for item in findings) or any(item.status == "warning" for item in commands):
        return "warning"
    return "pass"


def build_report(summary: ChangeSummary, findings: tuple[Finding, ...], commands: tuple[CommandResult, ...], *, test_summary: TestSummary | None = None, coverage_summary: CoverageSummary | None = None, runtime_metadata: dict[str, Any] | None = None) -> EvidenceReport:
    return EvidenceReport(
        schema_version=SCHEMA_VERSION,
        tool_version=TOOL_VERSION,
        change_summary=summary,
        policy_findings=findings,
        command_results=commands,
        overall_status=overall_status(findings, commands, test_summary, coverage_summary),
        test_summary=test_summary,
        coverage_summary=coverage_summary,
        runtime_metadata=runtime_metadata or {},
    )


def render_json(report: EvidenceReport, *, include_runtime_metadata: bool = False) -> str:
    return json.dumps(report.to_dict(include_runtime_metadata=include_runtime_metadata), indent=2, sort_keys=True) + "\n"


def _status_icon(status: str) -> str:
    return {"pass": "PASS", "warning": "WARN", "error": "ERROR"}[status]


def render_markdown(report: EvidenceReport) -> str:
    summary = report.change_summary
    lines = [
        "# PatchProof Evidence Report",
        "",
        f"**Overall status:** `{_status_icon(report.overall_status)}`  ",
        f"**Schema:** `{report.schema_version}`  ",
        f"**Tool:** `{report.tool_version}`",
        "",
        "## Change summary",
        "",
        f"Changed files: **{len(summary.changed_files)}**",
        "",
        "| File | Type | Categories | + | - |",
        "|---|---|---|---:|---:|",
    ]
    for item in summary.changed_files:
        lines.append(f"| `{item.path}` | {item.change_type} | {', '.join(item.categories)} | {item.additions} | {item.deletions} |")
    lines.extend(["", f"Categories: `{', '.join(summary.categories) or 'none'}`", "", f"Risk flags: `{', '.join(summary.risk_flags) or 'none'}`", "", "## Policy findings", ""])
    for finding in report.policy_findings:
        related = ", ".join(f"`{path}`" for path in finding.related_files) or "none"
        lines.append(f"- **{_status_icon(finding.status)}** `{finding.finding_id}` — {finding.message} Related files: {related}.")
    if report.test_summary is not None:
        test = report.test_summary
        lines.extend([
            "", "## Test-result evidence", "",
            f"**Status:** `{_status_icon(test.status)}`  ",
            f"Suites: **{test.suites}**  ",
            f"Tests: **{test.tests}**  ",
            f"Failures: **{test.failures}**  ",
            f"Errors: **{test.errors}**  ",
            f"Skipped: **{test.skipped}**  ",
            f"Duration: **{test.duration_ms} ms**", "",
        ])
    if report.coverage_summary is not None:
        coverage = report.coverage_summary
        line_percent = f"{coverage.line_rate:.1%}"
        branch_percent = f"{coverage.branch_rate:.1%}" if coverage.branch_rate is not None else "not reported"
        lines.extend([
            "", "## Coverage evidence", "",
            f"Line coverage: **{line_percent}**  ",
            f"Branch coverage: **{branch_percent}**  ",
            f"Lines: **{coverage.lines_covered if coverage.lines_covered is not None else 'not reported'} / {coverage.lines_valid if coverage.lines_valid is not None else 'not reported'}**  ",
            f"Branches: **{coverage.branches_covered if coverage.branches_covered is not None else 'not reported'} / {coverage.branches_valid if coverage.branches_valid is not None else 'not reported'}**", "",
        ])
    lines.extend(["", "## Command evidence", ""])
    if not report.command_results:
        lines.append("No commands were configured.")
    else:
        lines.extend(["| Command | Status | Exit code | Duration (ms) | Timed out |", "|---|---|---:|---:|---|"])
        for result in report.command_results:
            lines.append(f"| `{ ' '.join(result.command) }` | {_status_icon(result.status)} | {result.exit_code if result.exit_code is not None else '—'} | {result.duration_ms} | {'yes' if result.timed_out else 'no'} |")
            if result.output:
                lines.extend(["", "```text", result.output.rstrip(), "```", ""])
    lines.extend(["", "## Interpretation", "", "This report summarizes observable evidence. It does not prove correctness, security, authorship, or production readiness. Human review remains required.", ""])
    return "\n".join(lines)
