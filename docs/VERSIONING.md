# Versioning policy

PatchProof follows [Semantic Versioning 2.0.0](https://semver.org/).

| Version change | Meaning |
|---|---|
| Major | An intentional breaking change to the CLI contract, policy format, report schema, Action inputs/outputs, or supported Python baseline. |
| Minor | Backward-compatible functionality such as a new evidence adapter, report field, or Action input. |
| Patch | A backward-compatible bug fix, parser correction, documentation correction, or security hardening. |

Pre-1.0 releases may change more aggressively and use an explicit suffix such as `0.6.0-alpha`. The `1.0.0` release establishes the first stable contract, but it does not turn evidence into a correctness or security guarantee.

## Compatibility surfaces

The most important compatibility surfaces are the `patchproof check` arguments, JSON policy keys, report JSON fields, SARIF rule identifiers, Action inputs and outputs, and the Python version requirement. New fields should be additive. Existing fields should not change meaning silently. If a behavior must change, the changelog and migration notes must explain it.

## Release references

Users who need a reproducible Action should reference a reviewed release commit SHA. A release tag is easier to read but can be moved by a maintainer. The repository may publish a major convenience tag such as `v1` only after the stable release process is established; consumers with stricter supply-chain requirements should keep using a full SHA.

## Schema note

The report schema version is tracked separately from the package version. A package release may add optional report data without requiring a schema-major change. Any incompatible report-shape change must increment the schema major version and include migration guidance.
