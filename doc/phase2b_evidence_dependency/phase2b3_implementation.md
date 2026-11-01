# Phase 2B.3 production corroboration integrity

## Baseline and protected scope

Branch: `fix/scorecard-integrity-phase2a`; HEAD: `f64f226` (`phase 1`). The
existing Phase 2A, 2B.1 and 2B.2 work was uncommitted. Baseline validation:
**232 passed, 0 failed, 0 skipped**. All seven requested audit/lineage references
and the current registry were reviewed. No implementation branch was created.

An exact 69-file inherited snapshot/manifest is preserved under ignored
`analyzed/phase2b3_validation/inherited_baseline/`. Python copies use a
`.py.baseline` suffix so they cannot affect test discovery. The isolated
`analyzed/phase2b3_validation/phase2b3_only.patch` records only this phase against
that snapshot, allowing review separately from inherited uncommitted work.

## Implementation

| File | Change |
| --- | --- |
| `production_corroboration.py` (new) | Frozen typed requirements; pure hypothesis/availability-aware evaluation; deterministic disjoint witness selection; compound/accumulation semantics; compact serializable audit results |
| `decision_logic.py` | Correct generic High multiplicity check; record production corroboration; preserve compound route predicates; narrow selection wording correction |
| `signal_language.py` | Replace unsupported “independent forensic signals” label with a specific ELA/residual overlap description |
| `reasoning_persistence.py` | Render the additive production corroboration audit while preserving old traces |
| `tests/test_production_corroboration.py` (new) | 30 focused unit/integration cases |
| Four `phase2b3_*.md` reports | Gate inventory, implementation, actual reference comparison and remaining limitations |

`hypothesis_engine.py`, Phase 2A integrity/aggregation, all three Phase 2B.2
lineage/shadow modules, detector modules, masking rules and existing tests remain
byte-for-byte unchanged relative to this phase's entry snapshot.

## Production rule

The generic confidence High path formerly used two strong module flags plus
S>=3. It now uses two eligible, measurement-disjoint supporting indicator
witnesses plus the same S>=3. Valid existing strong definitions are preserved:
material >=0.58; strong asymmetry; strong boundary; strong cross. Inactive or
non-supporting observations cannot supply multiplicity. Medium still uses one
valid strong observation and S>=2; Low remains S>=1.2.

This is a source-eligibility correction, not new weights or tier calibration.
No confidence probability is introduced. It is not a universal requirement for
every High mechanism-specific route: those routes can legitimately rely on
compound forensic evidence, and their definitions are unchanged.

The audit classified 20 gate groups. One source-diversity predicate is corrected;
19 retain their conditions and numerical policy. See
[phase2b3_corroboration_gate_audit.md](phase2b3_corroboration_gate_audit.md) for exact
functions, inputs, ancestry risks, classifications and expected effects.

## Helper contract

`CorroborationRequirement` declares a gate ID, hypothesis, semantics and existing
minimum counts. `evaluate_corroboration()` reuses the 2B.2 registry and immutable
lineage records; it does not change summaries or record new image measurements.

The result records considered/eligible/excluded evidence, hypothesis roles,
selected ancestry groups, shared roots, overlapping feature groups, incremental
findings, provisional limitations, satisfaction and explanation. Unknown lineage,
invalid/inactive observations and missing required ancestry cannot satisfy a
distinct-source requirement. Inconclusive parent interpretation can still have
measured upstream features, matching the existing cross-signal architecture.
Counter-evidence remains visible in its own role and is not counted as support.

The witness search finds a deterministic maximum pairwise-disjoint subset of
measurement ancestries, excluding selected-mask geometry. It is not an estimate
of independent samples, and it does not delete related observations. Identical
ancestry candidates coalesce for search, while all original indicators remain
in the audit. Optional distinct-family semantics exist for explicitly defined
requirements but are not imposed across production gates.

For compound conditions, related indicators can remain eligible; missing raw
parent summaries are disclosed as provisional and create no distinct source.
This maintains existing summary-only callers and genuine spatial interpretations.
No additional coefficient, family cap, lineage credit adjustment or detector
execution is used in production.

## Trace and API compatibility

The five-element `synthesize_overall()` API, scorecard fields, route ordering,
selection priorities and hypothesis structure remain compatible. The optional
2B.2 shadow flag/policy is unchanged. `DecisionEnv` adds a default empty gate
collection; `determine_confidence()` retains its original positional interface
and accepts an optional keyword-only audit collector.

The additive trace field is:

```json
{
  "corroboration_audit": {
    "version": "2b3",
    "evaluated_gates": [],
    "limitations": []
  }
}
```

Each evaluated gate includes `requirement_kind`, `considered_evidence`,
`eligible_evidence`, `distinct_ancestry_groups`, `shared_ancestry`,
`incremental_support_findings`, `requirement_satisfied`, `gate_passed`, an
explanation and limitations. Source satisfaction and score/strength conditions
are separate; a compound subcondition passing does not imply its entire route
matched. Compound records explicitly state that their production condition is
unchanged. No full lineage graph is copied into every record.

Results are sorted/deduplicated by gate ID. Candidate-specific audits are rebuilt
on repeated environment evaluation; the confidence audit records the condition
that established the environment tier. Text persistence supports both new and
legacy traces. The Phase 2A calculation and 2B.2 dependency sidecar retain their
separate existing purposes and fields.

The unchanged 2B.2 shadow gate descriptions remain descriptive diagnostics; the
new `corroboration_audit` is the authoritative record of the production source-
diversity predicate. No shadow assessment is used to make a production decision.

## Wording-only changes

1. `signal_language.no_meaningful_convergence`: “ELA and residual hotspot checks
   do not meaningfully overlap” replaces the unsupported independence adjective.
2. Declaration selection: “without requiring a conclusive localized-editing
   result” replaces ambiguous “independently of inconclusive localized editing.”
3. The internal variable `independent_clone` is renamed `clone_specific`, with
   identical selection behavior.

Negative caveats stating that module outputs are not assumed statistically
independent and tiers are not probabilities are retained. Unrelated forensic
descriptions and production confidence rationale policy are not rewritten.

## Verification

Final automated suite: **262 passed, 0 failed, 0 skipped**, including all original
232 and 30 new cases. Coverage includes source/descendant counts, distinct
primaries, composites, compound mechanisms, patch localization, subject overlap,
metadata/pixels, missing/unknown lineage, contradictions, ordering/repetition,
strict JSON, language, production routing and Phase 2A/2B.2 invariants. No test
dependency was added.

The controlled integration counterexample was also replayed against the exact
inherited `decision_logic.py` snapshot: `moderate_suspicious_convergence` changes
High -> Medium while S remains 4.905 and B remains 0. Its two strong indicators,
boundary and cross, share the same ELA/residual ancestry. The corrected gate
reports one witness, so its existing two-source diversity condition fails. The
production numerical ledger is exactly identical. This is an explained logical
change, not a claim that a lower tier is empirically more accurate.

Both actual references ran full headless `subject_based` pipelines. The
scorecards, complete Phase 2A calculations, section snapshots, hypothesis
assessments and normalized serialized 2B.2 sidecars match the baseline exactly.
Instagram remains High at 20.47705; Midjourney Medium at 6.0375; both have zero
failed stages. Image hashes match. Midjourney's selection wording changes only
as described above. See [phase2b3_reference_comparison.md](phase2b3_reference_comparison.md).

No detector output, scoring coefficient, numerical aggregate, shadow marginal
policy, mask/provenance rule, dependency, GUI layout, packaging or workflow was
modified. No staging, commits, pushes, merges, tags, stashes, resets or discards
were performed.
