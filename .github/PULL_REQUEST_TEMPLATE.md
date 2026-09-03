## Summary

<!-- What changed, in 1–3 sentences? -->

## Why

<!-- Link the issue/spec/ADR and state the reviewer-visible outcome. -->

Closes #

## Acceptance criteria

- [ ] The originating issue/spec acceptance criteria are satisfied.
- [ ] Scope and non-goals were respected.

## Verification evidence

<!-- Include exact commands/results relevant to this change. Do not claim checks you did not run. -->

- [ ] Backend tests / repository verification, if affected
- [ ] Frontend lint/build/tests, if affected
- [ ] Browser desktop/mobile visual verification, if UI changed
- [ ] Generated evidence regenerated and verified, if pipeline/results changed
- [ ] Docker/config integration check, if deployment/container behavior changed

### Commands / results

```text
<commands and concise results>
```

## Forecasting / data invariants

For ML/data/evaluation changes, confirm or explain:

- [ ] No temporal leakage introduced.
- [ ] Final test was not used for selection/tuning/calibration.
- [ ] One-step evaluation and fixed-origin serving semantics remain distinct.
- [ ] Interval/anomaly claims remain within documented evidence boundaries.
- [ ] Manifest/provenance/checksum behavior remains valid when affected.

## Frontend / design checklist

For UI changes:

- [ ] `DESIGN.md` was followed or updated intentionally.
- [ ] Existing components/tokens were reused where appropriate.
- [ ] Keyboard focus and non-color-only meaning are preserved.
- [ ] Loading/empty/error/API-unavailable states remain coherent.
- [ ] Charts preserve units, protocol/uncertainty labels, and methodological boundaries.

## Security / privacy

- [ ] No secrets or local credentials are committed or logged.
- [ ] New inputs/paths are bounded and validated where applicable.
- [ ] Dependency changes were justified and audited.

## Documentation / ADR

- [ ] README/docs/API docs were updated if behavior changed.
- [ ] A new/superseding ADR was added if a durable decision changed.

## Risk and rollback

<!-- What could regress? How would we revert or detect it? -->

## Generated artifacts

<!-- List generated reports/data/screenshots changed by this PR, or write "None". -->
