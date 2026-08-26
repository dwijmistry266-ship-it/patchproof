# Changelog

All notable changes to PatchProof are documented here.

## [0.1.0] — 2026-08-19

### Added

- Explicit Git base/head revision mode with validated revisions and binary-aware diff acquisition.
- Unified diff parsing for file sections, additions, deletions, renames, and binary changes.
- Path classification for source, tests, documentation, dependencies, configuration, public interfaces, and other files.
- JSON policy loading with strict validation and default evidence rules.
- Evidence findings for source changes without tests, public-interface changes without documentation, and dependency changes without lockfiles.
- Bounded command execution with `shell=False`, timeouts, exit-code capture, combined output, and output truncation.
- Deterministic JSON and Markdown reports.
- Fifteen unit tests covering normal and adversarial fixtures, including real temporary Git histories.
- Public design, threat-model, security, contribution, and code-of-conduct documentation.

### Limitations

This release can compare explicit Git revisions or accept a unified diff fixture. It is not a sandbox, does not detect AI authorship, and does not provide a GitHub Action yet.
