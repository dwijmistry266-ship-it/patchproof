# PatchProof

**Evidence-first pull-request quality reports.**

PatchProof checks observable repository signals and produces a Markdown and JSON report for a change. It does not decide whether code was written by a human or an AI, and it does not replace review. It answers a narrower question:

> What evidence is present, what evidence is missing, and what commands actually ran?

## Why this exists

A passing CI job is useful but incomplete. A maintainer may still need to know whether tests changed with source code, documentation changed with a public interface, dependencies have a corresponding lockfile, and the configured reproduction commands actually succeeded.

PatchProof makes those signals explicit and reviewable.

## Current status

PatchProof is a small, inspectable CLI and reusable GitHub Action for evidence-first pull-request reporting. It accepts either a unified diff fixture or two explicit Git revisions, optionally reads JUnit XML test-result and coverage XML reports, classifies changed files, evaluates evidence rules, runs explicitly configured commands with safe bounds, and writes deterministic Markdown, JSON, and SARIF reports. The current local release candidate is `1.0.0`.

## Non-goals

PatchProof does not detect AI authorship, certify security, prove correctness, judge contributor intent, guarantee production readiness, or sandbox arbitrary code. Configured commands execute with the permissions of the user running the tool. Read `docs/threat-model.md` before using it on untrusted repositories. See [`docs/limitations.md`](docs/limitations.md) for supported inputs and known boundaries, [`docs/VERSIONING.md`](docs/VERSIONING.md) for compatibility expectations, and [`docs/RELEASING.md`](docs/RELEASING.md) for release procedure.

## Quick start

Install from a cloned checkout with Python 3.11 or newer:

```bash
git clone <your-repository-url>
cd patchproof
python -m venv .venv
. .venv/bin/activate
python -m pip install .
patchproof --help
```

For development, install the project in editable mode and run the complete verification suite:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
tests/test_action.sh
```

The tag-driven release workflow builds a source archive and wheel after rerunning tests. See `docs/RELEASING.md` for the reproducible release procedure.

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

Produce a deterministic SARIF 2.1.0 file for compatible analysis consumers:

```bash
patchproof check \
  --diff examples/source-with-tests.diff \
  --junit examples/results.xml \
  --coverage examples/coverage.xml \
  --config examples/patchproof.json \
  --output-dir /tmp/patchproof-report \
  --sarif /tmp/patchproof-report/results.sarif
```

SARIF contains non-passing policy findings as results, stable rule IDs, relative file locations when a finding has related files, and partial fingerprints. Passing findings are omitted because they are evidence, not alerts. Global findings remain in the SARIF result without a fabricated source location; GitHub code-scanning views may not display such results as file annotations.

The command writes:

```text
/tmp/patchproof-report/report.md
/tmp/patchproof-report/report.json
/tmp/patchproof-report/results.sarif
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

The suite covers normal and malformed diffs, quoted paths, source/test evidence, dependency lockfile rules, JUnit and coverage evidence, SARIF rendering, deterministic reports, successful commands, timeouts, output truncation, and real Git histories. `tests/test_action.sh` exercises the composite Action against a temporary two-commit repository.

## Contribution guide

The most useful early contributions are small and evidence-backed: a parser fixture, a policy rule with tests, a report rendering improvement, an adapter for a test-result format, or documentation that makes a failure easier to reproduce. Please read `CONTRIBUTING.md` and use the existing fixtures before proposing a broad feature.

## Roadmap

The v1.0 release candidate is complete locally. Future work should be driven by reproducible use cases rather than feature volume:

- Improve the Git adapter with deeper rename-aware summaries and clearer revision diagnostics.
- Add adapters for additional coverage formats and richer test-result metadata.
- Improve SARIF locations for global findings and add richer rule metadata.
- Add policy examples for Python, JavaScript, Go, and Rust repositories.
- Consider YAML policy support only if a concrete maintenance need appears.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the ordered completion gates.

## Reusable GitHub Action

PatchProof includes a composite action in `action.yml`. A consumer repository can copy `examples/patchproof-action.yml` to `.github/workflows/patchproof.yml` and adjust the action reference to a reviewed release tag or commit SHA.

The action checks out full history, compares the pull request base SHA with the event SHA, generates Markdown, JSON, and SARIF reports, and uploads the reports as a workflow artifact. It defaults to `skip-commands: 'true'` so untrusted pull-request code is not executed through repository-configured evidence commands. Enable `upload-sarif: 'true'` only when the workflow has `security-events: write` permission and the repository’s code-scanning settings allow SARIF ingestion.

Use `pull_request`, not `pull_request_target`, for the default consumer workflow. GitHub documents that `pull_request_target` runs with the base repository’s token and secrets, and checking out and executing fork-controlled code in that context can create a “pwn request” vulnerability [4]. The action does not require secrets and does not check out fork head code through an elevated-trust event.

The action intentionally fails clearly when a push event has no usable previous revision, such as a newly created branch. In that case, pass an explicit `base` input or use a manual `diff` input.

## SARIF references

PatchProof targets SARIF 2.1.0 as specified by OASIS [1]. GitHub’s supported SARIF subset uses stable rule identifiers, consistent relative paths, result levels, messages, and locations where available [2]. Uploading SARIF from GitHub Actions requires the `upload-sarif` action and appropriate workflow permissions [3].

[1]: https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html
[2]: https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support
[3]: https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file
[4]: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target

## License

MIT
