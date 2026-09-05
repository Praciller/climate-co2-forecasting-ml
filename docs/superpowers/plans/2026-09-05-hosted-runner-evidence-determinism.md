# Issue #30 hosted-runner evidence determinism

## Goal

Repair the strict governed-evidence drift on protected `main` without changing
model logic, evaluation semantics, anomaly methodology, frontend behavior, or
deployment state. Establish the smallest supported numerical-runtime contract
that makes the canonical Linux evidence byte-identical across independent
GitHub-hosted jobs.

## Boundaries

- Base: failing protected-main SHA `c23085d1c63aa2e967ef997893132e24ef6563df`.
- Branch: `fix/hosted-runner-evidence-determinism`.
- Canonical generation: Ubuntu 24.04, CPython 3.11.16, committed constraints.
- Preserve the strict drift guard; normalize only `live_forecast.json.generated_at`.
- Do not change model parameters, selection, final-test usage, interval scope,
  anomaly thresholds, frontend files, visual snapshots, or production deployment.
- Remove the diagnostic workflow before the final PR.

## Evidence-driven checklist

- [x] Confirm the merged SHA, failing CI run, passing sibling jobs, CodeQL, and
      the substantive drift paths/values.
- [x] Read the domain, verification, deployment, workflow, constraints, and
      numerical implementation contracts.
- [x] Compare canonical and failing hosted-run metadata and logs; mark missing
      CPU/dispatch fields as unobserved rather than inferred.
- [ ] Add and push the branch-only three-replica diagnostic workflow.
- [ ] Capture bounded CPU, OpenBLAS, NumPy, threadpoolctl, PyTorch, package,
      hash, summary, delta, and evidence-bundle artifacts.
- [ ] Run the unmodified deterministic environment baseline and compare all
      replicas, including PNG hashes and numeric deltas.
- [ ] Test one dispatch-control hypothesis at a time: OpenBLAS, then NumPy,
      then PyTorch only if the evidence requires it.
- [ ] Require at least three independent byte-identical final candidate runs;
      attempt up to five when necessary and report CPU diversity honestly.
- [ ] Update only the proven permanent environment in `ci.yml` and
      `serving-bundle.yml`, then remove the probe workflow.
- [ ] If the proven Linux contract changes governed evidence, refresh only the
      policy-defined tracked files from a GitHub Ubuntu artifact and inspect the
      scientific invariants before committing.
- [ ] Update the narrow verification/deployment documentation and retain the
      strict exact drift policy.
- [ ] Run authoritative backend, frontend, browser, repository, container,
      notebook, and API checks; verify no source/model/UI/snapshot drift.
- [ ] Push, open the requested PR, and prove the same commit with one initial
      green CI run plus two independent green reruns. Leave it open and do not
      merge.

## Acceptance evidence

Record exact run IDs, attempts, CPU/runtime fingerprints, per-replica hash
identity, measured numeric deltas, final variables, baseline generation run,
verification commands, PR state, remote branch SHA, and remaining limitations in
the final handoff. A cross-CPU claim is `YES` only when distinct CPU/runtime
fingerprints were actually observed; otherwise report `LIMITED`.
