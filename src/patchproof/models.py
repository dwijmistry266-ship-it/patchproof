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
class TestSummary:
    suites: int
    tests: int
    failures: int
    errors: int
    skipped: int
    duration_ms: int

    @property
    def status(self) -> Status:
        return "error" if self.failures or self.errors else "pass"


@dataclass(frozen=True)
class CoverageSummary:
    line_rate: float
    branch_rate: float | None = None
    lines_covered: int | None = None
    lines_valid: int | None = None
    branches_covered: int | None = None
    branches_valid: int | None = None

    @property
    def status(self) -> Status:
        return "pass"


@dataclass(frozen=True)
class EvidenceReport:
    schema_version: str
    tool_version: str
    change_summary: ChangeSummary
    policy_findings: tuple[Finding, ...]
    command_results: tuple[CommandResult, ...]
    overall_status: Status
    test_summary: TestSummary | None = None
    coverage_summary: CoverageSummary | None = None
    runtime_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_runtime_metadata: bool = True) -> dict[str, Any]:
        payload = asdict(self)
        if not include_runtime_metadata:
            payload.pop("runtime_metadata", None)
        return payload
