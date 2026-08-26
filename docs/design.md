# PatchProof MVP Design

## Problem

A passing CI check does not tell a maintainer whether a pull request is easy to review, reproducible, documented, or likely to contain a change that deserves extra attention. PatchProof produces an evidence report from observable repository signals.

## MVP promise

Given a repository path, a base revision, a head revision, and a small policy file, PatchProof will:

1. Inspect changed files.
2. Classify changed areas such as source code, tests, documentation, dependencies, configuration, and public-interface files.
3. Check whether the change includes evidence expected by the policy.
4. Run explicitly configured commands with timeouts.
5. Record command exit codes, duration, and bounded output.
6. Produce deterministic Markdown and JSON reports.

## Non-goals

PatchProof does not determine who wrote the code, detect AI authorship, prove security, certify correctness, replace code review, judge a contributor’s intent, or guarantee that a project is production-ready. It does not upload repository contents or execute commands not explicitly configured by the user.

## Inputs

### Repository state

The initial implementation accepts a unified diff file rather than invoking Git internally. This keeps the first parser deterministic and makes fixtures easy to reproduce. A later adapter may create the diff from Git revisions.

### Policy file

The policy is YAML-like but the first implementation uses JSON to avoid an external dependency. Example:

```json
{
  "required_evidence": {
    "source_change_requires_tests": true,
    "public_api_change_requires_docs": true,
    "dependency_change_requires_lockfile": true
  },
  "commands": [
    {"name": "unit-tests", "command": ["python", "-m", "unittest", "discover", "-s", "tests"]}
  ],
  "limits": {
    "command_timeout_seconds": 30,
    "max_output_bytes": 12000
  }
}
```

## Evidence model

```text
EvidenceReport
├── metadata
│   ├── schema_version
│   ├── generated_at (optional/non-deterministic field)
│   └── tool_version
├── change_summary
│   ├── changed_files
│   ├── categories
│   └── risk_flags
├── policy_findings
│   ├── id
│   ├── severity
│   ├── status
│   ├── message
│   └── related_files
├── command_results
│   ├── name
│   ├── command
│   ├── exit_code
│   ├── duration_ms
│   ├── timed_out
│   └── output
└── overall_status
```

A report must distinguish **pass**, **warning**, and **error**. Missing optional evidence should not be confused with a failed test command.

## Determinism

For the same diff, policy, tool version, and command output, PatchProof should produce the same JSON apart from explicitly marked runtime metadata. Tests will compare canonical JSON with runtime metadata removed. Markdown rendering must use stable ordering for files, categories, findings, and command results.

## Security boundaries

Commands are arbitrary process execution and therefore require explicit user configuration. PatchProof should default to a short timeout, bound captured output, avoid shell interpolation, and show the exact argument vector in the report. The tool should never treat repository text as instructions to execute.

## First implementation sequence

1. Define typed internal models.
2. Parse a small, well-defined unified diff subset.
3. Classify changed paths.
4. Load and validate JSON policy.
5. Generate policy findings.
6. Run configured commands safely.
7. Render JSON and Markdown.
8. Add fixtures for malformed diffs, renamed files, binary files, dependency changes, and command timeouts.
