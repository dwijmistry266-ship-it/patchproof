# Supported inputs and limitations

PatchProof is deliberately narrow. It summarizes observable repository evidence; it does not infer intent or certify the resulting code.

## Supported in v1.0.0

| Area | Supported behavior |
|---|---|
| Runtime | Python 3.11 or newer; dependency-free runtime using the standard library. |
| Change input | Unified Git diff text, or two explicit revisions from a local Git repository. |
| Paths | Ordinary paths, quoted paths, spaces in paths, additions, deletions, renames, binary markers, and multiple hunks. |
| Policy | JSON policy files with required-evidence rules, bounded configured commands, and line/branch coverage thresholds. |
| Test evidence | JUnit-style XML with multiple suites, totals, failures, errors, skipped tests, and duration. |
| Coverage evidence | Cobertura/coverage.py-style XML summary with line rate and optional branch rate/counts. |
| Reports | Deterministic Markdown and JSON reports, plus SARIF 2.1.0 for non-passing findings. |
| Automation | Composite GitHub Action with report artifact output and optional SARIF upload. |

## Known limitations

PatchProof does not sandbox configured commands. Commands run with the permissions and environment of the process invoking PatchProof. Keep `skip-commands: 'true'` for untrusted pull requests unless the repository owner has deliberately reviewed the trust boundary.

The diff parser is designed for Git-generated unified diffs, not arbitrary patch dialects. It does not reconstruct file contents, perform AST analysis, understand semantic renames, or prove that a test exercises a changed line. Binary changes and rename-heavy changes are surfaced as risk signals rather than deeply analyzed.

JUnit and coverage adapters consume report summaries. They do not rerun tests, verify that a report belongs to the current revision, or prove test quality, coverage quality, correctness, or security. A malformed, stale, or incorrectly generated report must be treated as untrusted evidence.

SARIF results with no specific source file remain global findings. GitHub code-scanning interfaces may show those results differently from file-linked annotations. SARIF output is not an upload service outside the optional GitHub Action integration.

Git revision mode requires a local repository containing both revisions. A shallow checkout, a new branch without a usable previous revision, a missing object, an unsupported revision expression, or a non-repository directory can fail before analysis. Consumers should use `fetch-depth: 0` or pass an explicit base revision.

PatchProof’s repository workflows and composite Action pin third-party Actions to reviewed full commit SHAs, with major-version comments retained for auditability. Consumers should apply the same practice to their own workflow dependencies and should pin the PatchProof Action to a reviewed release commit SHA when stronger supply-chain guarantees are required. The Action does not use `pull_request_target` and does not claim to provide a security sandbox.

PatchProof currently supports JSON policy configuration only. YAML policy support, richer language-aware rules, additional coverage formats, and deeper GitHub annotations are possible future work, not v1.0.0 capabilities.
