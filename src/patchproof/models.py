from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Status = Literal["pass", "warning", "error"]


@dataclass(frozen=True)
class ChangedFile:
    path: str
    categories: tuple[str, ...]
    change_type: str = "modified"
    additions: int = 0
    deletions: int = 0


@dataclass(frozen=True)
class Finding:
    finding_id: str
    severity: Status
    status: Status
    message: str
    related_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: tuple[str, ...]
    exit_code: int | None
    duration_ms: int
    timed_out: bool
    output: str
    output_truncated: bool = False

    @property
    def status(self) -> Status:
        if self.timed_out or self.exit_code not in (0, None):
            return "error"
        return "pass"


@dataclass(frozen=True)
class ChangeSummary:
    changed_files: tuple[ChangedFile, ...]
    categories: tuple[str, ...]
    risk_flags: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceReport:
    schema_version: str
    tool_version: str
    change_summary: ChangeSummary
    policy_findings: tuple[Finding, ...]
    command_results: tuple[CommandResult, ...]
    overall_status: Status
    runtime_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_runtime_metadata: bool = True) -> dict[str, Any]:
        payload = asdict(self)
        if not include_runtime_metadata:
            payload.pop("runtime_metadata", None)
        return payload
