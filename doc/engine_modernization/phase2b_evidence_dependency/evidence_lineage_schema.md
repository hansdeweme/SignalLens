# Evidence lineage schema — version 2b2

## Scope and identity

Lineage is a graph of detector summaries and distinguishable feature extractions.
It is not a statistical independence graph. Family, original scorecard domain,
and hypothesis evidence role are separate concepts. No pixel arrays, masks,
metadata values, prompts, filenames or complete detector payloads are retained.

`evidence_lineage.py` defines frozen `EvidenceSpec` and `LineageRecord` dataclasses,
`Family`, `Kind`, `Addition` enums, and an immutable validated `REGISTRY`.
Registration rejects duplicate IDs/parents, unknown parents, cycles, mutable
collections and restatements that claim new measurements. Restoration from JSON
also rejects extra payload fields, unknown enums, missing parents and cycles.

| Identifier | Meaning / stability |
| --- | --- |
| `evidence:<section_key>` | Stable detector-summary identity across repeated calls and dictionary order |
| `measurement:<feature_extraction>` | Distinguishable extraction, not an independent sample; e.g. luminance residual versus chroma phase features |
| `base:<section_key>` | One weighted section base credit; status and polarity remain production inputs |
| `component:<field>:<operation>:<reason_hash>` | Stable component rule identity; SHA-256 reason prefix, checked for duplicates; independent of conditional ledger position |
| `ledger_index` | Position in the Phase 2A operation sequence; not an evidence identity |

Hypothesis roles use the existing evidence identifiers from Phase 1.1; those may
include patterns or metadata signal IDs. They are copied descriptively and are
not multiplied into new scoring records.

## Lineage record

| Field | Contract |
| --- | --- |
| `evidence_id`, `source_detector` | Stable section identity and audited responsible function |
| `family` | Registry family; never equated with statistical independence |
| `measurement_ancestry` | Sorted tuple of available original extraction IDs, including available optional parents |
| `direct_dependencies` | Required upstream detector-summary IDs, rather than copied payloads |
| `optional_dependencies` | Real payload reuse that the detector can run without, e.g. texture/regional FFT carry-forward into asymmetry |
| `missing_dependencies` | Required parents unavailable or themselves missing required ancestry |
| `hypotheses` | Potential relevant hypotheses; actual support/contradiction remains the existing scoped assessment |
| `status`, `available`, `scoring_available` | Observed status; feature availability versus active status-weight eligibility |
| `kind` | `primary`, `derived` or `composite` |
| `addition` | New measurement, localization, relationship, interpretation, restatement or control |
| `overlap_groups` | Shared feature definitions/content/geometric controls; descriptive, not measured correlation |
| `known` | False for a future unregistered section; it gets no invented ancestry |

Missing/not_run/skipped/failed/error observations are unavailable. Inconclusive
interpretation may still have measured features that feed another detector;
for example ELA/residual maps can support cross-signal despite neutral global
summaries. Such an inconclusive parent does not earn a base weight. All registry
sections appear, including unavailable ones, making absence explicit. No image
observation is inferred merely from a zero-valued default.

The normal snapshot aliases `region_segmentation` to `region_masks`. That alias
does not create a second observation. The separate executed mask-morphology
stage remains unscored and is not silently wired into the registry as new
generation evidence. Selected mask geometry is a reliability/control ancestor;
it is excluded from counts of forensic measurement extractions.

## Family assignments and rationale

| Family | Members | Rationale and boundary |
| --- | --- | --- |
| `provenance` | metadata, recorded OSINT context | Assertion/source history; may concern the same claim, not authenticated origin |
| `processing_residual` | ELA, noise, cross, boundary, focus, alignment | Cross/boundary share ELA/residual ancestry; focus/alignment add localization/interpretation |
| `spectral` | global FFT, regional FFT | Same analyzer/features on different content/crops; regional FFT is not a child of cached global FFT |
| `patch_recurrence` | patch similarity, patch spatial | Spatial analysis consumes the retained matches; location is explicit added information |
| `subject_surface` | texture, process asymmetry, material realism | Overlapping residual/gradient/DCT/entropy families; separate extractions and real optional carry-forward are distinguished |
| `camera_pipeline` | sensor origin, CFA/demosaicing | Luminance versus chroma residual/phase measurements; no independence or sensor attribution claim |
| `compression_history` | compression history | Aligned/off-grid boundary-energy proxy; related to processing artifacts but not the same map |
| `intrinsic_edge_transition` | subject boundary | Internally detected gradient rings, not the selected person contour |
| `geometry` | selected region masks | Shared spatial support and quality control, not independent origin evidence |
| `analyst_context` | scene context | Analyst-supplied moderation, not an observed forensic detector |
| `unknown` | future unregistered sections | Explicitly unattributed; positive base shadow credit withheld until registered |

These assignments cover all 20 current synthesized section keys. The registry
adds a scene-context control node. It does not arbitrarily suppress two primary
observations because they share a broad family name.

## Contribution and allocation records

Frozen `Contribution` references evidence IDs, target field, existing value,
polarity, relevant hypotheses, domain, credit role and hypothesis evidence role.
`allocate_marginal()` returns deterministic records containing:

- `existing_contribution`, `diagnostic_contribution`, `difference`;
- `marginal_contribution` (numeric for structurally established credit, null when
  a numerical incremental value has not been established);
- measurement ancestry, explicit reason and empirical-validation flag.

Primary credits retain their existing value. Positive credits with unknown or
missing required ancestry are withheld diagnostically. A declared pure
restatement is suppressed only if a credited actual ancestor covers its
measurements in the same target, polarity and hypothesis scope. Merely sharing
a family or being a sibling is insufficient. Legitimate counter/moderating
evidence remains visible in its own hypothesis role.

Localization, relationships and interpretation are recorded separately. Their
existing base value is retained **provisionally**, while `marginal_contribution`
is null. Null is not a claim of zero usefulness, nor permission to count the
child as an independent confirmation. The audit did not supply calibrated
weights for these increments.

Component records reference the unchanged Phase 2A ledger and show operand,
operation, field, condition, evidence IDs, measurement ancestry and later
component attenuation. For additive operations an adjusted value can be
reported; a later nonlinear floor makes individual attribution null. Multipliers
are operations, not additive evidence. Local-to-edit conversion, clone routing,
camera moderation, cautions and domain bonuses must not be summed again as new
independent observations. Missing-mask penalties reference a control dependency
even when that control has no available forensic measurement ancestry.

## JSON integration

```json
{
  "evidence_dependency_analysis": {
    "mode": "shadow",
    "lineage_version": "2b2",
    "status": "complete",
    "production_score_unchanged": true,
    "policy": "structural_restatement_only",
    "lineage": [],
    "families": {},
    "contributions": [],
    "component_lineage": [],
    "lineage_coverage": {},
    "domain_accounting": {},
    "shared_ancestry": {},
    "corroboration_gates": {},
    "hypothesis_evidence_roles": {},
    "shadow_aggregates": {},
    "comparison": {},
    "limitations": []
  }
}
```

The Phase 2A `scorecard_calculation` remains untouched. No shadow confidence,
primary hypothesis, route selection or probability is emitted. Unknown base
signals/rule aliases produce explicit partial coverage; invalid production
cards withhold shadow aggregation. Optional diagnostic exceptions produce an
error sidecar without affecting the production decision.

`lineage_to_json()` / `lineage_from_json()` preserve immutable graph records
through JSON. Enum values serialize as strings and tuples as lists. Output
ordering is stable; processing times are measured externally rather than
inserted into deterministic diagnostic output.

## Explicit experimental allocations

`ExperimentalCredits(name, overrides)` requires an immutable tuple of
`(base_credit_id, credit_units)` pairs. IDs must exist, values must be finite,
nonnegative and no greater than the existing supported suspicious base credit.
Counter-evidence cannot be experimentally reduced through this interface.
No default coefficient, family budget or automatic descendant-removal policy
exists. The function-level API must be called explicitly; production synthesis
does not accept an experimental policy.

Experimental base changes recompute the existing domain bonus from remaining
positive credits, retain all existing adjusted component terms and apply the
existing camera/floor/geometry/photo operations in order. This is a conditional
base-credit diagnostic, not a full causal rerun of guards or synergies. Its
formula requires validation/recalibration before any decision use.
