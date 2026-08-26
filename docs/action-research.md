# GitHub Action implementation notes

GitHub custom actions require an `action.yml` or `action.yaml` metadata file. The metadata declares the action name, description, inputs, outputs, and execution model. PatchProof uses a composite action so the implementation remains inspectable shell plus the existing Python CLI.

The consumer workflow checks out full history because actions/checkout fetches only one commit by default; `fetch-depth: 0` is required when comparing arbitrary base and head revisions. The default workflow uses `pull_request`, not `pull_request_target`, because GitHub documents that `pull_request_target` runs with the base repository token and secrets and becomes dangerous if fork-controlled code is checked out and executed.

PatchProof defaults to skipping repository-configured commands for the reusable action. This preserves the evidence-only behavior for untrusted pull requests. The action uploads Markdown, JSON, and SARIF reports as an artifact. Optional SARIF upload requires the workflow to grant `security-events: write`; the consumer example declares `contents: read` and `security-events: write` explicitly.

The first Action milestone does not promise that all event edge cases are handled automatically. A newly created branch can have an all-zero `github.event.before` value on push, so the action fails clearly and asks for an explicit base or diff input.

References:

1. GitHub Docs, “Metadata syntax reference”: https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax
2. GitHub Docs, “Securely using pull_request_target”: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
3. actions/checkout README: https://github.com/actions/checkout
4. GitHub Docs, “Uploading a SARIF file to GitHub”: https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file
