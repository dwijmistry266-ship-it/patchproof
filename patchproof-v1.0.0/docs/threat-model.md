# PatchProof Threat Model

## Security position

PatchProof is an evidence reporter, not a sandbox. A configured command may execute arbitrary code with the permissions of the user running PatchProof. The user must treat repository configuration and commands as code.

## Assets

The main assets are source code, test outputs, repository metadata, environment variables, credentials available to child processes, and the integrity of the generated report.

## Threats

| Threat | Example | MVP mitigation |
|---|---|---|
| Arbitrary command execution | A policy runs a destructive command | Never execute commands unless explicitly configured; document the boundary |
| Secret leakage | A test prints an environment token | Bound output, warn that output may contain secrets, never collect environment variables intentionally |
| Shell injection | A filename is interpolated into a shell string | Use argument arrays and avoid shell mode |
| Resource exhaustion | A command hangs or emits huge output | Timeout and output byte limit |
| Misleading evidence | A report calls a warning a pass | Use explicit statuses and show raw command exit state |
| Diff parser confusion | Malformed or adversarial paths alter classification | Treat paths as data, test unusual names, do not execute paths |
| False confidence | Users assume a report proves correctness | State non-goals prominently and require human review |
| Untrusted repository instructions | README text attempts to redirect the tool | Repository text is data; only local user configuration controls execution |

## Out of scope for MVP

The MVP does not provide container isolation, network isolation, privilege dropping, secret scanning, cryptographic attestation, or a complete sandbox. These may be future integrations but must not be implied by the current tool.

## Safe defaults

The first implementation should use a 30-second default command timeout, a 12,000-byte output limit, `shell=False`, and a non-zero process exit code when a configured command times out or fails. The report should show that a command was truncated or timed out.

## Responsible disclosure

Future releases should include `SECURITY.md` with a private reporting channel once the repository is public. Security reports should not be submitted as public issues when they expose an exploitable command-execution path.
