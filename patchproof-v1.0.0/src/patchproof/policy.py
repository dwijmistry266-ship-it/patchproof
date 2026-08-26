from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .coverage import CoverageError, evaluate_coverage, validate_coverage_policy
from .models import ChangeSummary, CoverageSummary, Finding

DEFAULT_POLICY: dict[str, Any] = {
    "required_evidence": {
        "source_change_requires_tests": True,
        "public_api_change_requires_docs": True,
        "dependency_change_requires_lockfile": True,
    },
    "commands": [],
    "coverage": {},
    "limits": {"command_timeout_seconds": 30, "max_output_bytes": 12000},
}


class PolicyError(ValueError):
    pass


def load_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        return json.loads(json.dumps(DEFAULT_POLICY))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PolicyError(f"policy file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PolicyError(f"invalid JSON policy: {exc}") from exc
    if not isinstance(data, dict):
        raise PolicyError("policy root must be an object")
    merged = json.loads(json.dumps(DEFAULT_POLICY))
    for section in ("required_evidence", "coverage", "limits"):
        if section in data:
            if not isinstance(data[section], dict):
                raise PolicyError(f"policy section '{section}' must be an object")
            merged[section].update(data[section])
    if "commands" in data:
        if not isinstance(data["commands"], list):
            raise PolicyError("policy commands must be a list")
        merged["commands"] = data["commands"]
    _validate_policy(merged)
    return merged


def _validate_policy(policy: dict[str, Any]) -> None:
    limits = policy["limits"]
    timeout = limits.get("command_timeout_seconds")
    max_output = limits.get("max_output_bytes")
    if not isinstance(timeout, int) or timeout <= 0 or timeout > 3600:
        raise PolicyError("command_timeout_seconds must be an integer from 1 to 3600")
    if not isinstance(max_output, int) or max_output <= 0 or max_output > 10_000_000:
        raise PolicyError("max_output_bytes must be an integer from 1 to 10000000")
    try:
        validate_coverage_policy(policy.get("coverage", {}))
    except CoverageError as exc:
        raise PolicyError(str(exc)) from exc
    for command in policy["commands"]:
        if not isinstance(command, dict) or not isinstance(command.get("name"), str) or not isinstance(command.get("command"), list):
            raise PolicyError("each command must contain a string name and a command list")
        if not command["name"].strip() or not command["command"] or not all(isinstance(item, str) and item for item in command["command"]):
            raise PolicyError("command names and argument lists must be non-empty strings")


def evaluate_policy(summary: ChangeSummary, policy: dict[str, Any], coverage_summary: CoverageSummary | None = None) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    evidence = policy["required_evidence"]
    paths = tuple(item.path for item in summary.changed_files)
    has_source = "source" in summary.categories
    has_tests = "tests" in summary.categories
    has_docs = "documentation" in summary.categories
    has_dependency = "dependencies" in summary.categories
    has_lockfile = any(path.endswith(("lock", "lock.json", "lock.yaml")) for path in paths)
    has_public_interface = "public-interface" in summary.categories

    if has_source and evidence.get("source_change_requires_tests", True):
        findings.append(Finding("tests-for-source", "error", "pass" if has_tests else "error", "Source changes include test changes." if has_tests else "Source changes do not include test changes.", paths))
    if has_public_interface and evidence.get("public_api_change_requires_docs", True):
        findings.append(Finding("docs-for-public-interface", "warning", "pass" if has_docs else "warning", "Public-interface changes include documentation changes." if has_docs else "Public-interface changes have no documentation change.", paths))
    if has_dependency and evidence.get("dependency_change_requires_lockfile", True):
        findings.append(Finding("lockfile-for-dependency", "error", "pass" if has_lockfile else "error", "Dependency changes include a lockfile." if has_lockfile else "Dependency changes do not include a lockfile.", paths))
    if coverage_summary is not None:
        findings.extend(evaluate_coverage(coverage_summary, policy))
    if not findings:
        findings.append(Finding("no-rules-triggered", "pass", "pass", "No required-evidence rules were triggered.", paths))
    return tuple(findings)
