# Contributing to PatchProof

Thank you for considering a contribution. PatchProof values small, reproducible improvements over large speculative features.

## Before opening an issue

Search existing issues and run the included tests. For a bug, include the smallest diff or policy fixture that reproduces it, the expected behavior, the actual behavior, and the operating environment.

## Before opening a pull request

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Add or update a fixture-driven test for behavior changes. Keep report output deterministic. Do not add claims about AI authorship detection, security certification, or correctness guarantees.

## Good first contributions

Useful early contributions include parser fixtures for unusual diffs, policy validation tests, documentation improvements, report formatting fixes, and adapters for standard test-result formats. New integrations should begin with a design issue before implementation.

## AI-assisted contributions

AI tools may be used as development aids, but contributors remain responsible for understanding, testing, and documenting their changes. Pull requests should explain what changed, how it was verified, and any limitations.
