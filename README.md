# PatchProof

**Evidence-first pull-request quality reports.**

PatchProof checks observable repository signals and produces a Markdown and JSON report for a change. It does not decide whether code was written by a human or an AI, and it does not replace review. It answers a narrower question:

> What evidence is present, what evidence is missing, and what commands actually ran?

## Why this exists

A passing CI job is useful but incomplete. A maintainer may still need to know whether tests changed with source code, documentation changed with a public interface, dependencies have a corresponding lockfile, and the configured reproduction commands actually succeeded.

PatchProof makes those signals explicit and reviewable.

## Current status

This is an early local CLI release. It accepts either a unified diff fixture or two explicit Git revisions, optionally reads JUnit XML test-result and coverage XML reports, classifies changed files, evaluates evidence rules, runs explicitly configured commands with safe bounds, and writes deterministic `report.md` and `report.json` files.

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

Run the included fixture example:

```bash
patchproof check \
  --diff examples/source-with-tests.diff \
  --config examples/patchproof.json \
  --output-dir /tmp/patchproof-report
```

For a real Git repository, compare two explicit commit-ish revisions:

```bash
patchproof check \
  --repo . \
  --base main \
  --head HEAD \
  --config examples/patchproof.json \
  --output-dir patchproof-report
```

PatchProof validates both revisions before asking Git for a binary-aware diff. Revision arguments are passed without shell interpolation, and a revision beginning with `-` is rejected.

Attach JUnit test-result evidence when a test runner has produced an XML report:

```bash
patchproof check \
  --diff examples/source-with-tests.diff \
  --junit examples/results.xml \
  --config examples/patchproof.json \
  --output-dir /tmp/patchproof-report
```

JUnit parsing reports suites, tests, failures, errors, skipped tests, and duration. It treats failures or errors as an overall error and does not treat test counts as proof of correctness.

Attach coverage evidence and thresholds:

```bash
patchproof check \
  --diff examples/source-with-tests.diff \
  --junit examples/results.xml \
  --coverage examples/coverage.xml \
  --config examples/patchproof.json \
  --output-dir /tmp/patchproof-report
```

The policy may configure `minimum_line_rate` and `minimum_branch_rate` as values from `0` to `1`. Missing branch data is an error when a branch threshold is configured. Coverage is treated as one signal and never as proof of correctness.

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

- Improve the Git adapter with rename-aware summaries and clearer revision diagnostics.
- Add adapters for additional coverage formats and richer test-result metadata.
- Add SARIF output.
- Add policy examples for Python, JavaScript, Go, and Rust repositories.
- Improve renamed-file and binary-file reporting.
- Publish a GitHub Action only after the local CLI behavior is stable.

## License

MIT
