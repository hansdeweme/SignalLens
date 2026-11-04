# Phase 2B.4 production numerical evidence deduplication

Date: 2026-11-01. Classification and baseline readiness are recorded in
[phase2b4_contribution_classification.md](phase2b4_contribution_classification.md).

## Implementation

`numerical_evidence.allocate_base_evidence` allocates raw status weights before
reliability, penalty and aggregate calculations. It reuses `build_lineage` and
the existing registry; there is no parallel ancestry graph or experimental
weighting policy. `evidence_lineage.numerical_restatement_sources` adds one
pattern-specific computational contract for the shared overlap fallback.

The deterministic rules are:

1. An identical summary object supplied under multiple keys earns one base
   contribution. Prefer a registered key, then lexical order. Runtime object
   addresses are never serialized. Equal-valued separate observations retain
   credit because content equality alone does not establish source identity.
2. A suspicious `possible_boundary_fragment_convergence` (or overlap-only
   `partial_boundary_convergence`) is not another numerical measurement when
   an active suspicious cross summary already represents that same overlap.
   Keep both observations, but suppress the restated boundary base. Remove
   only domain categories that no longer contain an eligible base contribution.
   Preserve the existing 0.25 bonus coefficient and all other credited domains.
3. The same fragment restatement is withheld from its 0.5 local-support term
   and 0.5 fragment/cross edit term. `local_support_conversion` consumes corrected
   support at the unchanged 0.18 coefficient. No duplicate subtraction occurs
   after aggregation. A standalone observed fragment retains its single
   representation; unavailable/non-supporting cross evidence cannot erase it.
4. Registered pure-restatement descendants require an actually counted
   ancestor in the same hypothesis scope and polarity. No new measurements are
   inferred from missing parents. Existing compound-summary APIs may omit raw
   parent summaries; their ancestry remains explicitly provisional.
5. Contour-positive boundary findings, focus intensity measurements, spatial
   alignment and patch topology retain their existing contributions. Sharing
   ancestry, families or feature helper code alone never triggers suppression.

The two affected component sites are intercepted by `add_fragment_component`.
Their operation ledger retains the original operand as `raw_operand`, records
an eligible operand of zero, and links a category-B allocation. The later
reliability multipliers are recorded by `finalize_component_allocations`.
Other component formulas and all their numerical coefficients remain intact.

`hypothesis_engine.compute_base_scores` and `compute_scorecard` share the same
allocation helper. The latter allocates once, derives totals and domain sets
from eligible rows, computes the existing components, applies reliability and
aggregate transformations, and validates the result before decision evaluation.
No detector, confidence-policy definition, mask threshold or routing threshold
was changed. The only decision-module edit corrects an obsolete trace statement
that numerical scoring was unchanged.

## Calculation audit and compatibility

The existing version-2A calculation envelope is retained with additive fields:

- `base_evidence[].weight`: original status weight, unchanged.
- `base_evidence[].credited_weight`: eligible production weight, either the
  original value or zero; no new fractional coefficient.
- `numerical_deduplication`: version `2b4`, compact measurement ancestry,
  classifications A–D, original/eligible/suppressed contributions, credited
  representatives, missing dependencies, provisional relationships, component
  allocations and raw/eligible base/domain reconciliation.

Base allocation multipliers are 1.0 because they precede aggregate camera,
geometry and photo-context attenuation. The existing aggregate ledger records
those multipliers, penalties and floor exactly once. Base allocation rows are
not asserted to be additive final-score attributions after a nonlinear floor.
Component allocation rows record their actual later component multipliers.

`scorecard_integrity.reconstruct_scorecard_calculation` independently consumes
eligible base weights, replays eligible component operands and the existing
aggregate formula. Its allocation validator rejects missing coverage,
fractional replacements, mismatched suppression, mismatched domain accounting
and altered component allocation records. Historical 2A JSON without these
extensions still reconstructs. New consumers must use `credited_weight` when
replaying new traces; the old raw status-only formula intentionally no longer
describes corrected totals.

The five-element `synthesize_overall` API, section snapshots, hypotheses and
centralized policy interface are unchanged. Text reasoning persistence renders
the production allocation separately from shadow diagnostics. It copies no
large detector payloads. The optional shadow analyzer starts from eligible
production base weights, so a duplicate cannot regain credit in the diagnostic
comparison. Experimental overrides remain diagnostic only and cannot alter
production, routing or confidence. Production corroboration gates still use
their existing measurement-disjoint/compound semantics.

## Verification

**334 passed, 0 failed, 0 skipped** (`py -3.13 -m pytest -q --tb=short`, final run 3.67 s).
All original 297 regressions are preserved; 37 focused cases were added in
`tests/test_numerical_evidence.py`. The earlier new-test run exposed incorrect
test assumptions about the existing tuple/policy schema and fragment compound
arithmetic; those assertions were corrected after inspecting production code.
No existing test was edited to obtain a pass.

Coverage includes repeated identical observations, equal-valued distinct
measurements, primary plus restatement, multiple restatement descendants,
measured increments, provisional/unknown relationships, opposite polarities,
missing inputs, rejected geometry, provenance with visual evidence, order and
repeat determinism, controlled nonfinite inputs, source-diversity/shadow/policy
integration, JSON/text persistence, independent arithmetic reconstruction,
historical trace compatibility, and corrupted base/component ledger detection.
Tests use synthetic observations and no new dependency.

Both final full headless image runs passed independent arithmetic replay,
unchanged-image hashes, repeated-summary equality and shadow/production equality.
The reference comparison documents the score change and all unchanged decision
gates. Existing TensorFlow Lite/MediaPipe initialization diagnostics appeared;
neither image had a failed stage or recorded pipeline error.

## Isolation and limits

Entry files and Git inventory are preserved under ignored
`analyzed/phase2b4_validation/inherited_baseline/`, with a SHA-256 manifest.
The phase-only patch is `analyzed/phase2b4_validation/phase2b4_only.patch`.
New source: `numerical_evidence.py`; new regression file and four phase reports.
Changes to inherited files: `hypothesis_engine.py`, `evidence_lineage.py`,
`scorecard_integrity.py`, `evidence_dependency_analysis.py`,
`reasoning_persistence.py`, and one trace-description line in `decision_logic.py`.
No other inherited file should differ from the entry snapshot.

Uncertain surface carry-forward, camera multi-role moderation, provenance/OSINT
claim overlap and conditional value of preserved localization remain empirical
questions. Their existing coefficients are retained provisionally. The allocator
does not infer observation identity across independently copied, unregistered
payloads without a source contract. It does not establish statistical independence,
accuracy or calibrated probabilities. The acceptance audit's unrelated overflow
and malformed-input/internal-route limitations remain outside this change.

No staging, commit, push, merge, tag, stash, reset, deletion, detector change,
dependency update, packaging or GUI change was performed. `test_images/` and
validation artifacts remain ignored.
