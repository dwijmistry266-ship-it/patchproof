# PatchProof Roadmap

PatchProof will be completed in ordered milestones. Each milestone must be implemented, tested, documented, and verified in GitHub before the next milestone begins.

## Current baseline: v1.0.0 release candidate (local; public upload pending)

The repository supports manual unified-diff input, explicit Git base/head revisions, JUnit XML test-result evidence, Cobertura/coverage.py-style XML coverage evidence with configurable thresholds, deterministic SARIF 2.1.0 output, and a reusable composite GitHub Action. It classifies changed files, evaluates evidence rules, runs explicitly configured commands with bounded output and timeouts, and writes Markdown, JSON, and SARIF reports. The local suite contains 40 tests, the local Action harness passes, and release automation and issue templates are prepared. The public v1.0.0 tag and external trial remain release gates.

## Milestone 1 — JUnit XML test-result support

**Goal:** Parse a standard test-result format and include actual test totals, failures, errors, skipped tests, and duration in the evidence report.

**Definition of done:** The parser handles a valid report, an empty report, malformed XML, multiple test suites, missing optional attributes, and unexpected elements. The report renderer includes stable test summaries. No external network or repository content is executed while parsing XML.

**Release gate:** At least 8 new fixture-driven tests, updated README usage, and a passing GitHub Actions run.

## Milestone 2 — Coverage evidence and thresholds — complete locally as `0.4.0-alpha`

**Goal:** Accept a standard coverage summary, compare it to configured thresholds, and report missing or insufficient coverage without pretending coverage proves correctness.

**Definition of done:** The implementation handles line-rate parsing, missing values, invalid percentages, thresholds, and warning/error semantics. The report explains that coverage is one signal among many.

**Release gate:** Coverage fixtures, threshold tests, documentation, and a passing CI run.

## Milestone 3 — SARIF output — complete locally as `0.5.0-alpha`

**Goal:** Produce valid SARIF for policy findings so compatible code-scanning interfaces can consume PatchProof results.

**Definition of done:** JSON output validates against the selected SARIF schema version, findings have stable rule identifiers and levels, and paths are represented consistently. The tool does not claim that SARIF output itself proves code correctness.

**Release gate:** Schema-oriented tests, an example SARIF file, documentation, and a passing CI run.

## Milestone 4 — Reusable GitHub Action — complete locally as `0.6.0-alpha`

**Goal:** Package the stable local behavior as a GitHub Action that obtains explicit event revisions, runs PatchProof, stores reports as artifacts, and optionally emits SARIF.

**Definition of done:** The Action uses pinned or versioned dependencies, has documented inputs and outputs, handles fork and shallow-checkout cases, avoids secret exposure, and has a sample workflow in the repository.

**Release gate:** A self-test workflow, documented permissions, an example consumer repository or fixture, and successful CI execution.

## Milestone 5 — Hardening and v1.0 — release candidate complete locally

**Goal:** Improve parser behavior, error messages, compatibility documentation, release process, and contributor experience.

**Definition of done:** The project has a changelog, versioning policy, security policy, contribution guide, reproducible release instructions, regression fixtures, issue templates, and a clear list of unsupported cases. The local release candidate has no known high-severity defect in its documented scope and has a full test and Action-harness pass. External review or trial is intentionally still pending.

**Release gate:** Public upload of the release candidate, green `Tests` and `Action self-test` workflows, a tagged non-prerelease `v1.0.0`, and one public feedback issue or external trial. The release notes must explain what was learned without claiming adoption or correctness guarantees.

## Publication rule

A milestone is not complete merely because code exists locally. It is complete when the repository’s README, tests, documentation, CI, changelog, and public commit history all agree about what the software does.

## Project-switch rule

Dwij should start a new flagship repository only after PatchProof v1.0 is released, one external person has tried it, and the final review identifies what engineering skills were gained. A new project should solve a different problem rather than becoming an unfinished collection of parallel experiments.
