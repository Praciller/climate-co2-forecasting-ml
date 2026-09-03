# Issue tracker: GitHub

Issues and specs for this repository live as GitHub issues. Use the `gh` CLI
for all operations.

## Conventions

- Create an issue with `gh issue create`.
- Read an issue with `gh issue view <number> --comments`.
- List issues with `gh issue list` and the appropriate state/label filters.
- Comment, label, or close issues with the corresponding `gh issue` command.

## Pull requests as a triage surface

PRs as a request surface: no.

## When a skill says to publish or fetch a ticket

Publish by creating a GitHub issue. Fetch with `gh issue view <number>
--comments`, including labels when triage state matters.

## Wayfinding

Use GitHub issues for maps and child tickets. Prefer native issue dependencies
when available; otherwise record blocking issues in the issue body.
