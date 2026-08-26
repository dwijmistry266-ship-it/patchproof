# Changelog

All notable changes to PatchProof are documented here.

## [0.5.0-alpha] — 2026-08-26

### Added

PatchProof can now render deterministic SARIF 2.1.0 output from non-passing policy findings. Results include stable rule IDs, severity levels, messages, relative artifact locations when related files exist, and partial fingerprints. Passing findings are omitted because they are evidence rather than alerts.

The milestone adds tests for top-level SARIF structure, rule and result mapping, severity conversion, relative paths, global findings, deterministic output, and CLI generation. It also documents the relationship between PatchProof’s local reports and GitHub’s supported SARIF subset.

### Limitations

Global findings are retained without fabricated source locations and may not appear as file annotations in GitHub code-scanning views. SARIF generation alone does not upload results to GitHub and does not prove correctness, security, authorship, or production readiness.

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
