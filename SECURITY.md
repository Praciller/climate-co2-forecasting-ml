# Security Policy

## Scope

This repository is a public portfolio/reproducibility project. It is not presented as a hosted production service or security-certified system.

Security-sensitive areas still include:

- API input/path validation and artifact containment;
- dependency and container configuration;
- accidental credential or secret exposure;
- unsafe deserialization or loading of untrusted model/artifact files;
- frontend injection or unsafe rendering;
- CI workflow and supply-chain changes.

## Reporting a vulnerability

Please **do not open a public issue** if a report would expose a credential, exploit details, or another sensitive security concern.

Use the repository's **Security** area on GitHub to submit a private vulnerability report/security advisory when that option is available. If private reporting is unavailable, open a minimal public issue that contains no exploit payloads, secrets, or sensitive data and asks the maintainer for a private reporting channel.

## Secrets

- Never commit API keys, tokens, passwords, private certificates, or real credentials.
- Use `.env.example` only for variable names and safe placeholders.
- Never paste secrets into issues, pull requests, CI logs, screenshots, or generated reports.
- If a secret is accidentally committed, treat it as compromised and rotate/revoke it; deleting the line from a later commit is not sufficient.

## Security verification

Security automation is a quality signal, not a replacement for review. Dependency audits, static/security scans, input-boundary tests, and manual review should be applied according to the risk of the change.
