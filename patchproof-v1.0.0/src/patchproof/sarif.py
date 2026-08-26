from __future__ import annotations

import hashlib
import json
from typing import Any

from .models import EvidenceReport, Finding

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"


def _level(status: str) -> str:
    return {"error": "error", "warning": "warning", "pass": "note"}[status]


def _relative_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized or "."


def _fingerprint(finding: Finding, path: str) -> str:
    seed = "\0".join((finding.finding_id, _relative_path(path), finding.message))
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32]


def _rule(finding: Finding) -> dict[str, Any]:
    return {
        "id": finding.finding_id,
        "name": finding.finding_id.replace("-", " "),
        "shortDescription": {"text": finding.message},
        "fullDescription": {"text": finding.message},
        "defaultConfiguration": {"level": _level(finding.severity)},
        "help": {"text": "See the PatchProof evidence report for the related evidence and limitations."},
    }


def _result(finding: Finding) -> dict[str, Any]:
    paths = tuple(sorted({_relative_path(path) for path in finding.related_files}))
    result: dict[str, Any] = {
        "ruleId": finding.finding_id,
        "level": _level(finding.status),
        "message": {"text": finding.message},
        "partialFingerprints": {"patchproof/v1": _fingerprint(finding, paths[0] if paths else "")},
    }
    if paths:
        result["locations"] = [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": path},
                    "region": {"startLine": 1},
                }
            }
            for path in paths[:10]
        ]
    else:
        result["properties"] = {"patchproof:global": True}
    return result


def render_sarif(report: EvidenceReport) -> str:
    """Render non-passing findings as a deterministic SARIF 2.1.0 log."""
    findings = tuple(sorted((item for item in report.policy_findings if item.status != "pass"), key=lambda item: (item.finding_id, item.message, item.related_files)))
    rules: dict[str, Finding] = {}
    for finding in findings:
        rules.setdefault(finding.finding_id, finding)
    payload = {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "PatchProof",
                        "version": report.tool_version,
                        "semanticVersion": report.tool_version.removesuffix("-alpha"),
                        "informationUri": "https://github.com/dwijmistry266-ship-it/patchproof",
                        "rules": [_rule(rules[key]) for key in sorted(rules)],
                    }
                },
                "automationDetails": {"id": "patchproof/default"},
                "results": [_result(finding) for finding in findings],
                "invocations": [{"executionSuccessful": True}],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
