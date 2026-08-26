# Changelog

All notable changes to PatchProof are documented here.

## [0.4.0-alpha] — 2026-08-26

### Added

PatchProof can now parse Cobertura/coverage.py-style XML reports and include line and branch rates, covered/valid counts, and configurable threshold findings in Markdown and JSON reports. The policy supports `minimum_line_rate` and `minimum_branch_rate` values from `0` to `1`.

The milestone adds coverage fixtures and tests for valid data, malformed XML, invalid rates, missing branch data, below-threshold results, and report rendering. Coverage remains an evidence signal and is not presented as proof of correctness.

## [0.3.0-alpha] — 2026-08-26

### Added

PatchProof gained optional JUnit XML test-result input with suite, test, failure, error, skipped, and duration summaries. It added a reproducible `examples/results.xml` fixture and tests covering real and malformed reports.

## [0.2.0-alpha] — 2026-08-19

### Added

PatchProof gained explicit Git base/head revision mode with validated revisions and binary-aware diff acquisition. It also gained unified diff classification, evidence policy evaluation, bounded command execution, deterministic Markdown and JSON reports, and public design, threat-model, security, contribution, and conduct documentation.

### Limitations

The project can compare explicit Git revisions or accept a unified diff fixture. It is not a sandbox, does not detect AI authorship, and does not provide a GitHub Action yet.

## [0.1.0-alpha] — 2026-08-18

### Added

Initial local CLI, diff parser, evidence policy, bounded command runner, deterministic reports, and public documentation.
