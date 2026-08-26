# Security Policy

## Scope

PatchProof executes commands explicitly configured by the user. It is not a sandbox and must not be run against an untrusted repository without appropriate isolation.

## Reporting a vulnerability

Until a private security contact is configured, do not publish sensitive exploit details in an issue. Record the issue locally and contact the repository owner through the GitHub profile. Include the affected version, reproduction steps, impact, and a proposed mitigation when possible.

## Security limitations

The MVP does not isolate processes, protect secrets printed by child commands, or provide cryptographic attestation. The threat model in `docs/threat-model.md` is part of the product contract.
