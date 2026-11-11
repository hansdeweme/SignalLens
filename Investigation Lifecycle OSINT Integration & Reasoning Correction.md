# Codex Task D — SignalLens: Investigation Lifecycle OSINT Integration & Reasoning Correction

**Repository:** `D:\Coding\SignalLens`  
**Target release:** `0.1.0-beta.1`  
**Priority:** High — pre-release correctness  
**Task type:** Bounded implementation and validation  
**Authorization:** Production changes permitted within the defined scope  
**Git:** Do not stage, commit, tag, push or publish.

## 1. Mission

Implement a consistent investigation lifecycle that separates:

1. Forensic measurements and observations.
2. Image creation/origin assessment.
3. Regional processing anomalies.
4. Evidence of a distinct editing operation.
5. Technical provenance authenticity.
6. External source corroboration.

SignalLens must allow an analyst to add OSINT evidence either **before forensic analysis or afterward**, without compromising reproducibility.

The investigation conclusion must incorporate reviewed, image-associated OSINT evidence while preserving the original forensic measurements and hypothesis assessments.

At the same time, implement the specific reasoning corrections identified by Task C.

**Success is an auditable, causally defensible investigation—not a predetermined AI-generated verdict.**

## 2. Mandatory preparation

Read:

- `AGENTS.md`
- `doc/test_quality/TEST_DISCIPLINE.md`
- All reports under `doc/reasoning_audit/origin_processing/`
- `doc/reasoning_audit/causal_provenance/implementation_report.md`
- Relevant existing contracts for the six GUI workspaces
- Existing OSINT persistence, investigation snapshot, reporting and reasoning-policy implementations

Audit the current working tree before modifying anything.

Reuse existing models, adapters and lifecycle mechanisms where practical.

Do not build a parallel investigation engine or replace functioning architecture merely to satisfy this task.

## 3. Reference case

Use the existing Midjourney reference image:

`test_images/midjourney/high-quality, realistic fashion portrait of a young woman , soft hair, natural dabbled window light f 1.8.png`

Previously recorded SHA-256:

`b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`

The baseline analysis used the `normal` profile.

Its findings were:

| Field | Baseline |
|---|---|
| Primary hypothesis | `localized_editing` |
| Primary finding | Localized processing anomalies |
| Confidence | High |
| Synthetic origin | Medium |
| Suspicious score | 18.04075 |
| Benign score | 1.50 |
| Declared process | `null` |
| Separate edit | Not established |
| OSINT in reasoning trace | `not_run` |

External source:

https://embracepresets.com/best-midjourney-prompts-for-realistic-photos/

Direct image:

https://embracepresets.com/wp-content/uploads/2024/08/theart1300_httpss.mj_.runhx-xd-s5Gos_real_photo_-chaos_10_-a_33717b8b-eb01-4bd6-8719-f4b4c9d59fa8_3.png

The previous manually reviewed OSINT record contains:

```text
image_sha256:
b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1

source_type: ai_gallery
best_match_similarity: 1.0
analyst_reviewed: true
review_status: reviewed_matches_found
ai_source_context_detected: true
mode: manual
```

This is a reviewed source-match record, **not independently verified cryptographic provenance**.

The reported normalized similarity of 1.0 must not be misrepresented as byte-for-byte identity unless actual file-hash comparison has been performed.

The previous experiment demonstrated that the separate OSINT record was saved successfully while the forensic reasoning trace remained unchanged and continued to report `osint: not_run`.

## 4. Required investigation lifecycle

Implement the following logical workflow:

```text
LOAD IMAGE
    |
    v
Establish image identity (SHA-256)
    |
    v
OPTIONAL SOURCE & CONTEXT ENTRY
    |
    +--------------------------+
    |                          |
    v                          v
Source evidence provided    No source evidence
    |                          |
    +-------------+------------+
                  |
                  v
          FORENSIC ANALYSIS
                  |
                  v
       Immutable forensic result
                  |
                  v
      INVESTIGATION SYNTHESIS
                  |
                  v
       Versioned investigation
                  |
                  v
         GUI / Reports / Export
```

OSINT is optional.

The analyst must also be able to perform:

```text
Existing forensic result
          |
          v
Add or revise OSINT evidence
          |
          v
Validate image association
          |
          v
Refresh investigation synthesis
          |
          v
New investigation revision
```

**Do not rerun pixel detectors when only OSINT evidence changes.**

An explicit forensic reanalysis remains a separate operation.

## 5. Image identity and association

Associate OSINT evidence with the investigated image using the existing image-identity mechanism, preferably SHA-256.

Requirements:

- Reject or clearly flag mismatched image identities.
- Do not attach OSINT from a previously loaded image to the current image.
- Preserve image identity across saved and restored investigations.
- Ensure stale asynchronous results cannot update another investigation.
- Distinguish image-file identity from source-image similarity.
- Preserve existing behavior for investigations without OSINT evidence.

Do not introduce a second competing identity system.

## 6. Source & Context entry before analysis

Make the existing OSINT/source-entry functionality available after loading an image and before pressing Analyze.

Reuse existing controls and infrastructure wherever possible.

Support:

- Source page URL.
- Optional direct-image URL.
- Source description or claim.
- Analyst notes.
- Existing source-match information when available.

Do not make source entry mandatory.

Do not require the user to navigate through the entire Evidence workspace just to enter a source URL before analysis.

Keep the interface compact and consistent with the current PyQt6 design system.

This task does not authorize a broad GUI redesign.

If current OSINT controls already support these fields, expose or reuse them rather than recreating them.

## 7. OSINT after analysis

Allow reviewed OSINT evidence to be added, corrected or removed after the forensic analysis has completed.

When the OSINT record changes:

1. Persist the change against the correct image.
2. Create a new investigation-level revision.
3. Recompute the investigation synthesis.
4. Refresh relevant GUI views.
5. Ensure newly generated reports reflect the revision.
6. Leave the frozen forensic result unchanged.

Avoid redundant analysis execution.

The interface must make clear that the investigation conclusion has been updated without implying that pixel-based findings changed.

## 8. Separate forensic results from investigation synthesis

Preserve the existing forensic measurements, evidence lineage, scorecard and hypothesis-specific confidence tiers.

Introduce or extend a minimal investigation-level synthesis that represents:

```text
origin_assessment
regional_anomaly_assessment
separate_edit_assessment
technical_provenance_authenticity
external_source_corroboration
```

Use existing canonical names where appropriate; do not create duplicate fields unnecessarily.

Each assessment should preserve:

- Evidence references.
- Supporting observations.
- Contradictory or moderating observations.
- Evidence limitations.
- Verification/review status.
- A concise human-readable interpretation.

These dimensions must not be treated as statistically independent by default.

**Important:** Do not convert qualitative evidence into artificial probabilities.

## 9. Correct the Task C reasoning defects

### 9.1 Boundary compound eligibility

Task C established that inconclusive Boundary Focus contributes to the compound strength calculation despite being excluded from supporting indicators.

Correct the eligibility/outcome inconsistency.

An observation excluded from supporting eligibility must not silently increase support strength through another pathway unless the policy explicitly defines and audits that distinct role.

Preserve legitimate separate measurements.

Do not fix the defect by simply changing numeric thresholds.

### 9.2 Regional anomalies versus editing causality

Stop treating regional anomaly support as automatically decisive evidence of a separate editing operation.

Distinguish:

- Measured regional processing differences.
- Possible editing-related interpretations.
- Specific evidence supporting a distinct edit.
- Editing history not established.

Preserve the original observations.

A strong regional anomaly finding may remain appropriate even when a separate edit is unproven.

### 9.3 Mask and boundary reliability

Preserve the distinction between:

- Segmentation quality.
- Boundary measurement reliability.
- Evidence strength.
- Causal confidence.

Task C found that these quantities have different meanings.

Ensure their limitations influence the relevant causal interpretation and are visible in the resulting explanation.

Do not force boundary reliability to equal mask reliability.

### 9.4 Non-graph generation declarations

The Task B causal adapter currently recognizes supported connected generation workflows but does not adequately represent non-graph generation declarations.

Generalize creation-context interpretation without assuming every generator exposes a ComfyUI-style graph.

Distinguish:

- Supported structured workflow.
- Explicit non-graph generation declaration.
- Generic AI tool reference.
- Unspecified or ambiguous metadata.

Preserve authenticity safeguards.

Do not add generator-name-specific primary-selection exceptions.

## 10. External corroboration semantics

External evidence must have a distinct status from technical provenance authenticity.

Recommended concepts:

| Dimension | Example |
|---|---|
| Technical authenticity | Unverified |
| Source evidence | Reviewed manual match |
| Match strength | Normalized similarity 1.0 |
| Source claim | Published as Midjourney-generated |
| Corroboration | Generation context supported |
| Separate editing | Not established |

A user-entered URL is not automatically verified evidence.

A manually reviewed source match is not necessarily cryptographically authenticated.

A source claiming AI generation may provide meaningful corroboration without establishing the entire creation history.

Preserve dependency information when multiple sources repeat the same underlying claim.

Do not double-count the same claim merely because it appears in metadata and an article.

No general-purpose web-scraping engine, new external API or autonomous OSINT service is authorized.

## 11. GUI and reporting integration

Ensure the following workspaces use the same canonical investigation synthesis where applicable:

- Overview
- Image Forensics
- Evidence
- Reasoning
- Provenance
- Reports

The Overview should show the current investigation conclusion rather than an isolated forensic hypothesis presented as the entire verdict.

The Reasoning workspace must distinguish:

- Frozen forensic reasoning.
- Subsequent OSINT review.
- Current investigation synthesis.

The Provenance workspace must distinguish technical authenticity from external corroboration.

The Reports workspace must preserve the exact evidence and revision used in the exported conclusion.

Avoid repeating the same long explanation in every workspace.

Ensure that opening an older saved investigation remains supported where feasible.

## 12. Revision and reproducibility rules

Maintain an immutable forensic snapshot.

Investigation revisions should capture at least:

- Image identity.
- Forensic snapshot identity.
- OSINT evidence revision or fingerprint.
- Synthesis rule/policy version.
- Revision identifier.
- Revision timestamp.
- Evidence references supporting the conclusion.

Use current project mechanisms when available.

Do not create a new database solely for this feature.

Historical reports must not silently change when OSINT evidence is later edited.

New exports should reflect the currently selected investigation revision.

## 13. Test discipline — strict limits

**Excessive regression testing is expressly forbidden.**

Before writing tests:

- Inspect existing relevant tests.
- Identify actual uncovered behavior.
- Reuse existing fixtures.
- Prefer parameterized extensions.
- Avoid duplicating invariants across GUI, integration and unit tests.
- Follow `doc/test_quality/TEST_DISCIPLINE.md`.

Target **no more than four new collected test cases**, as proposed in Task C.

Four is the maximum without explicit exception justification, not a required count.

Suggested behavior coverage:

1. Boundary eligibility correction.
2. Non-graph generation declaration versus anomaly/edit interpretation.
3. OSINT added before analysis versus afterward produces equivalent investigation synthesis.
4. OSINT revision updates the investigation and reports without changing forensic measurements.

Use existing tests to cover image identity, session staleness, save/load and report consistency wherever possible.

Do not create one new test module per behavior.

Do not add GUI automation unless existing tests demonstrably cannot cover a critical new interaction.

Run focused tests during development and the complete existing suite once at the final validation gate.

Report baseline count, added tests, removed/consolidated tests and net change.

Do not regenerate golden baselines to hide unintended changes.

## 14. Required validation

### Midjourney reference

Compare:

A. Image analysis without OSINT.

B. Same image with reviewed OSINT entered before analysis.

C. Same completed forensic analysis with OSINT added afterward.

Required invariants:

- Identical image identity.
- Unchanged forensic measurements.
- Unchanged numerical scorecard unless an explicitly documented eligibility calculation correction applies.
- Consistent final investigation synthesis for equivalent reviewed evidence.
- OSINT visibly represented in the investigation conclusion.
- Technical metadata authenticity remains unverified.
- Separate editing is not asserted without specific supporting evidence.
- Historical snapshots remain reproducible.

### ComfyUI/FLUX.2 reference

Verify that the previous correction still holds:

- Full-generation workflow declaration recognized.
- `denoised_output` does not produce enhancement.
- Authenticity remains unverified.
- Regional anomalies are not automatically called subsequent editing.

### Conventional photographic reference

Use an existing representative real-photo fixture if available.

Ensure that regional anomalies alone do not automatically establish synthetic origin or an authenticated creation history.

Do not introduce new image fixtures unless essential and justified.

## 15. Deliverables

Provide:

1. Bounded production implementation.
2. Concise architecture/change summary.
3. Midjourney before/after comparison.
4. ComfyUI regression comparison.
5. Explanation of boundary eligibility correction.
6. OSINT before/after-analysis lifecycle demonstration.
7. Investigation revision and report consistency results.
8. Focused and full-suite validation results.
9. Test-count accounting.
10. Git status and confirmation that unrelated changes were preserved.

Place implementation documentation under:

`doc/reasoning_audit/origin_processing/`

Avoid creating unnecessary documentation files.

Do not stage or commit.

## 16. Acceptance criteria

The implementation is complete when:

- OSINT can be entered after image loading and before analysis.
- OSINT remains optional.
- OSINT can be added or revised after analysis.
- Updating OSINT does not rerun pixel detectors.
- Reviewed source evidence is linked to the correct image.
- The current investigation conclusion incorporates relevant OSINT evidence.
- Frozen forensic results remain reproducible.
- Technical provenance authenticity remains separate from source corroboration.
- The Boundary Focus eligibility defect is corrected.
- Regional anomalies are not automatically treated as a proven separate edit.
- Non-graph generation declarations are represented appropriately.
- GUI and exported reports use consistent investigation revisions.
- Both Midjourney and ComfyUI reference cases remain coherent.
- No arbitrary detector threshold adjustments are introduced.
- New regression coverage remains minimal and nonredundant.
- The existing full test suite passes.
- Nothing is staged, committed, pushed, tagged or published.

## 17. Final Codex response

Return a concise report structured as:

**1. Implementation summary** — What changed.

**2. Reasoning corrections** — Boundary eligibility, origin and separate-edit interpretation.

**3. OSINT lifecycle** — Before-analysis and after-analysis behavior.

**4. Data integrity** — Image identity, forensic immutability and investigation revisions.

**5. Reference cases** — Midjourney and ComfyUI before/after results.

**6. Validation** — Focused tests, full suite, baseline/additions/net test count.

**7. Remaining limitations** — Any intentionally deferred capability.

**8. Git status** — Unrelated changes preserved; nothing staged or committed.

**9. Release readiness** — Ready / Conditional / Blocked.

Do not claim improved classification accuracy without empirical validation.

**Core principle: Forensic measurements must remain independent of external claims, while the final investigation should reflect all available, appropriately qualified evidence.**