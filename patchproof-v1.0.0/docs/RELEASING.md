# Releasing PatchProof

PatchProof uses semantic versioning for public releases. Alpha versions use a suffix such as `0.6.0-alpha`; the first stable release is `1.0.0`.

## Release gate

Before creating a stable release, confirm that the repository has a clean working tree, the complete test suite passes, the action harness passes, the README and changelog describe the same behavior, the security and threat-model documents are current, and at least one developer outside the author has reviewed or tried the tool.

## Version update

Update the version in these locations together:

```text
pyproject.toml
src/patchproof/__init__.py
src/patchproof/report.py
CHANGELOG.md
```

Run the complete verification locally:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
tests/test_action.sh
```

## Tag and release

Commit the release changes, then create an annotated tag:

```bash
git tag -a v1.0.0 -m "PatchProof v1.0.0"
git push origin main --follow-tags
```

The tag-triggered release workflow reruns tests, builds the Python package, and creates the GitHub release with generated notes. A release is based on a Git tag and identifies the exact source point made available to users.

## Action consumers

Consumers should reference a reviewed release tag or, for stronger immutability, a full commit SHA. They should grant only `contents: read` by default. Workflows that enable SARIF upload need `security-events: write`. Consumers should keep `skip-commands: 'true'` for untrusted pull requests unless they have reviewed the command-execution risk.

## Rollback

If a release is defective, do not silently move a stable tag. Publish a corrective patch version, document the issue, and explain the recovery path in the release notes. Security-sensitive issues should be handled through the repository security policy.
