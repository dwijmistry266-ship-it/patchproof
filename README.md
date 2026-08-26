# PatchProof

**Evidence-first pull-request quality reports.**

PatchProof checks observable repository signals and produces a Markdown and JSON report for a change. It does not decide whether code was written by a human or an AI, and it does not replace review. It answers a narrower question:

> What evidence is present, what evidence is missing, and what commands actually ran?

## Why this exists

A passing CI job is useful but incomplete. A maintainer may still need to know whether tests changed with source code, documentation changed with a public interface, dependencies have a corresponding lockfile, and the configured reproduction commands actually succeeded.

PatchProof makes those signals explicit and reviewable.

## Current status

This is an early local CLI release. It accepts a unified diff and a JSON policy file, classifies changed files, evaluates evidence rules, runs explicitly configured commands with safe bounds, and writes deterministic `report.md` and `report.json` files.

## Non-goals

PatchProof does not detect AI authorship, certify security, prove correctness, judge contributor intent, guarantee production readiness, or sandbox arbitrary code. Configured commands execute with the permissions of the user running the tool. Read `docs/threat-model.md` before using it on untrusted repositories.

## Quick start

```bash
git clone <your-repository-url>
cd patchproof
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Run the included example:

```bash
patchproof check \
  --diff examples/source-with-tests.diff \
  --config examples/patchproof.json \
  --output-dir /tmp/patchproof-report
```

The command writes:

```text
/tmp/patchproof-report/report.md
/tmp/patchproof-report/report.json
```

The CLI exits with code `1` when evidence or a configured command has an error, `0` for pass or warning, and `2` for invalid input or tool errors.

## Policy example

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

The first release uses JSON deliberately so that the project can remain dependency-light and the policy format can be validated with the standard library. YAML support may be added later if there is a concrete need.

## Report semantics

| Status | Meaning |
|---|---|
| `pass` | The observed evidence satisfies the configured rule or the command exited successfully |
| `warning` | A review concern exists, but the rule is not treated as a hard failure |
| `error` | Required evidence is missing, a configured command failed, or a command timed out |

The report includes the changed files, categories, risk flags, findings, command arguments, exit codes, bounded output, and a reminder that human review remains necessary.

## Architecture

```text
unified diff + JSON policy
            |
            v
      diff parser
            |
            v
      path classifier
            |
            +------> evidence policy evaluator
            |
            +------> bounded command runner
            |
            v
       EvidenceReport
          /     \
         v       v
   report.json  report.md
```

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The suite covers normal and malformed diffs, source/test evidence, dependency lockfile rules, deterministic reports, successful commands, timeouts, and output truncation.

## Contribution guide

The most useful early contributions are small and evidence-backed: a parser fixture, a policy rule with tests, a report rendering improvement, an adapter for a test-result format, or documentation that makes a failure easier to reproduce. Please read `CONTRIBUTING.md` and use the existing fixtures before proposing a broad feature.

## Roadmap

- Add a Git adapter that creates a diff from explicit base and head revisions.
- Add adapters for common test-result and coverage formats.
- Add SARIF output.
- Add policy examples for Python, JavaScript, Go, and Rust repositories.
- Improve renamed-file and binary-file reporting.
- Publish a GitHub Action only after the local CLI behavior is stable.

## License

MIT
