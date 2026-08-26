# Release and workflow hardening notes

GitHub releases are based on Git tags that mark a specific point in repository history. A release can be created from a tag, include release notes, and be marked as a pre-release when the software is not ready for production. PatchProof will use a v1.0.0 tag only after the release gate is met.

GitHub’s Actions security guidance recommends least-privilege token permissions, avoiding plaintext secrets, auditing workflow logs, and pinning third-party Actions to full-length commit SHAs when immutable references are required. PatchProof’s v1.0 repository workflows and composite Action use reviewed full SHA pins, with major-version comments for auditability. Consumer repositories should apply the same practice to their own dependencies and may pin PatchProof to a reviewed release commit SHA.

GitHub documents that actions/checkout fetches only one commit by default, so workflows comparing arbitrary revisions need `fetch-depth: 0`. GitHub also warns against using `pull_request_target` with fork-controlled code that is checked out and executed. PatchProof uses `pull_request` and defaults to skipping repository-configured commands in its reusable action.

References:

1. GitHub Docs, “Managing releases in a repository”: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
2. GitHub Docs, “About releases”: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
3. GitHub Docs, “Secure use reference”: https://docs.github.com/en/actions/reference/security/secure-use
4. actions/checkout README: https://github.com/actions/checkout
5. GitHub Docs, “Securely using pull_request_target”: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
