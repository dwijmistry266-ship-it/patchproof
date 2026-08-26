from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .models import CoverageSummary, Finding


class CoverageError(ValueError):
    """Raised when a coverage XML report is invalid or unsupported."""


def _rate(element: ET.Element, name: str, required: bool = False) -> float | None:
    raw = element.attrib.get(name)
    if raw is None or raw == "":
        if required:
            raise CoverageError(f"coverage XML is missing required '{name}'")
        return None
    try:
        value = float(raw)
    except ValueError as exc:
        raise CoverageError(f"coverage attribute '{name}' must be a number from 0 to 1") from exc
    if not 0 <= value <= 1:
        raise CoverageError(f"coverage attribute '{name}' must be a number from 0 to 1")
    return value


def _count(element: ET.Element, name: str) -> int | None:
    raw = element.attrib.get(name)
    if raw is None or raw == "":
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise CoverageError(f"coverage attribute '{name}' must be a non-negative integer") from exc
    if value < 0:
        raise CoverageError(f"coverage attribute '{name}' must be a non-negative integer")
    return value


def parse_coverage_text(text: str) -> CoverageSummary:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise CoverageError(f"invalid coverage XML: {exc}") from exc
    if root.tag.rsplit("}", 1)[-1] != "coverage":
        raise CoverageError("coverage XML root must be 'coverage'")
    return CoverageSummary(
        line_rate=_rate(root, "line-rate", required=True) or 0.0,
        branch_rate=_rate(root, "branch-rate"),
        lines_covered=_count(root, "lines-covered"),
        lines_valid=_count(root, "lines-valid"),
        branches_covered=_count(root, "branches-covered"),
        branches_valid=_count(root, "branches-valid"),
    )


def parse_coverage_file(path: Path) -> CoverageSummary:
    try:
        return parse_coverage_text(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CoverageError(f"coverage report not found: {path}") from exc
    except UnicodeDecodeError as exc:
        raise CoverageError(f"coverage report is not valid UTF-8: {path}") from exc


def evaluate_coverage(summary: CoverageSummary, policy: dict) -> tuple[Finding, ...]:
    requirements = policy.get("coverage", {})
    findings: list[Finding] = []
    minimum_line = requirements.get("minimum_line_rate")
    minimum_branch = requirements.get("minimum_branch_rate")
    if minimum_line is not None:
        if not isinstance(minimum_line, (int, float)) or isinstance(minimum_line, bool) or not 0 <= minimum_line <= 1:
            raise CoverageError("minimum_line_rate must be a number from 0 to 1")
        line_ok = summary.line_rate >= minimum_line
        findings.append(Finding("coverage-line-threshold", "error", "pass" if line_ok else "error", f"Line coverage is {summary.line_rate:.1%}; required minimum is {minimum_line:.1%}."))
    if minimum_branch is not None:
        if not isinstance(minimum_branch, (int, float)) or isinstance(minimum_branch, bool) or not 0 <= minimum_branch <= 1:
            raise CoverageError("minimum_branch_rate must be a number from 0 to 1")
        if summary.branch_rate is None:
            findings.append(Finding("coverage-branch-threshold", "error", "error", "Branch coverage is required by policy but the report contains no branch rate."))
        else:
            branch_ok = summary.branch_rate >= minimum_branch
            findings.append(Finding("coverage-branch-threshold", "error", "pass" if branch_ok else "error", f"Branch coverage is {summary.branch_rate:.1%}; required minimum is {minimum_branch:.1%}."))
    return tuple(findings)
