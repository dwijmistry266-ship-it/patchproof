# SARIF implementation notes

PatchProof targets SARIF Version 2.1.0. The OASIS specification defines SARIF as a standard format for analysis-tool output and models a log as one or more runs containing tool metadata and results. Each result can identify a rule, severity level, message, and physical artifact location.

GitHub’s SARIF support documentation states that GitHub code scanning supports SARIF 2.1.0 and uses stable `ruleId` values and consistent filepaths to track results across runs. Relative artifact URIs should be relative to the analyzed repository root. GitHub code scanning requires at least one location for a result to display it as an alert; PatchProof findings that have no related file will therefore need a deterministic repository-root fallback location or be omitted from code-scanning output with an explicit note.

For the first milestone, PatchProof will produce a valid deterministic SARIF log with one run, one driver component, stable rule descriptors, result messages, levels mapped from PatchProof status, relative artifact locations when related files exist, and partial fingerprints derived from stable rule/file/message data. It will not claim that SARIF ingestion proves correctness or security.

References:

1. OASIS, “Static Analysis Results Interchange Format (SARIF) Version 2.1.0 Plus Errata 01”: https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html
2. GitHub Docs, “SARIF support for code scanning”: https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support
3. GitHub Docs, “Uploading a SARIF file to GitHub”: https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file
