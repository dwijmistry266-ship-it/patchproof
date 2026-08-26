# Changelog

All notable changes to PatchProof are documented here.

## [1.0.0] — 2026-08-26

### Added

PatchProof v1.0.0 hardens unified-diff path parsing for quoted paths and spaces, counts multiple hunks correctly, validates `a/` and `b/` path prefixes, and rejects malformed coverage thresholds during policy loading. It also adds stable package metadata, reproducible release instructions, a tag-driven release verification workflow, and issue templates for reproducible bug reports and evidence-based feedback.

### Security and scope

The reusable Action keeps command execution disabled by default, documents the trust boundary around configured commands, uses least-privilege workflow permissions, and recommends reviewed release tags or full commit SHAs for consumers. PatchProof remains an evidence summarizer rather than a correctness, security, authorship, or production-readiness certifier.

### Verification

The local release candidate passes the complete 40-test Python suite, the composite Action harness, shell syntax checks, package build checks, and clean-install smoke tests. External review and adoption are intentionally not claimed; the repository includes a feedback path for those to happen publicly.

## [0.6.0-alpha] — 2026-08-26

### Added

PatchProof now includes a reusable composite GitHub Action in `action.yml`. The action accepts explicit diff or base/head inputs, defaults to full-history checkout in the consumer workflow, generates Markdown, JSON, and SARIF reports, uploads reports as an artifact, and can optionally upload SARIF to GitHub code scanning.

The action defaults to `skip-commands: 'true'` so repository-configured evidence commands are not executed for untrusted pull requests. It fails clearly when a push event has no usable previous revision and documents why `pull_request_target` is not used for the default workflow.

### Verification

The local action harness exercises a two-commit Git repository, Git revision selection, report generation, and output propagation. The complete Python suite contains 36 passing tests.

## [0.5.0-alpha] — 2026-08-26

### Added

PatchProof can render deterministic SARIF 2.1.0 output from non-passing policy findings with stable rule IDs, severity levels, messages, relative artifact locations, and partial fingerprints.

### Limitations

Global findings are retained without fabricated source locations and may not appear as file annotations in GitHub code-scanning views. SARIF generation alone does not upload results to GitHub.

## [0.4.0-alpha] — 2026-08-26

### Added

PatchProof gained Cobertura/coverage.py-style XML parsing, line and branch coverage summaries, configurable thresholds, missing-data errors, invalid-value validation, and coverage evidence in Markdown and JSON reports.

## [0.3.0-alpha] — 2026-08-26

### Added

PatchProof gained optional JUnit XML test-result input with suite, test, failure, error, skipped, and duration summaries.

## [0.2.0-alpha] — 2026-08-19

### Added

PatchProof gained explicit Git base/head revision mode with validated revisions and binary-aware diff acquisition. It also gained unified diff classification, evidence policy evaluation, bounded command execution, deterministic Markdown and JSON reports, and public design, threat-model, security, contribution, and conduct documentation.

### Limitations

The project can compare explicit Git revisions or accept a unified diff fixture. It is not a sandbox, does not detect AI authorship, and does not provide a GitHub Action yet.

## [0.1.0-alpha] — 2026-08-18

### Added

Initial local CLI, diff parser, evidence policy, bounded command runner, deterministic reports, and public documentation.
