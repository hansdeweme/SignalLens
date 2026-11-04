# CODEX TASK — SignalLens Phase 3: Hypothesis-Aware Confidence Policy Consolidation

## Mission

You are the principal Python engineer, forensic reasoning architect and software quality specialist for SignalLens.

Your task is to implement **correction #9 of the original ten-point reasoning-engine roadmap: decouple confidence assignment from route-specific hardcoding**.

Previous phases have substantially improved SignalLens:

- **Phase 1:** Hypothesis-aware routing, metadata propagation and provenance interpretation.
- **Phase 1.1:** Hypothesis-specific supporting, contradicting and moderating evidence.
- **Phase 1.2:** Failure-tolerant person segmentation and regional analysis.
- **Phase 2A:** Mathematically consistent, auditable scorecard calculations.
- **Phase 2B.1:** Forensic evidence-dependency audit.
- **Phase 2B.2:** Explicit evidence lineage and shadow marginal-corroboration diagnostics.
- **Phase 2B.3:** Production corroboration integrity and corrected independence claims.

The latest reported validation:

- **262 tests passed**, zero failed or skipped.
- Both reference images completed without pipeline failures.
- Instagram: High-confidence localized-editing finding.
- Midjourney: Medium-confidence unverified generation declaration.
- Production numerical scores remain unchanged.

One architectural weakness remains: individual decision routes may still assign `High`, `Medium` or `Low` directly, using localized conditions that are not consistently reconciled with the complete hypothesis assessment.

**Primary objective:** Centralize confidence assignment into an explicit, deterministic, hypothesis-aware policy while preserving the meaning of existing forensic findings.

This is a reasoning correctness task, not an opportunity to increase or decrease detection sensitivity.

---

## 1. Baseline and repository protection

Before making changes:

1. Inspect the current branch, HEAD and working-tree status.
2. Identify all uncommitted work inherited from previous phases.
3. Verify the Phase 2B.3 implementation is present.
4. Run the existing automated test suite.
5. Record the baseline confidence results for the reference cases.
6. Review the existing confidence-related documentation.

The previous development work contains uncommitted changes across several phases.

Preserve those changes.

Do not stage, commit, push, merge, tag, reset, stash or discard anything.

If the inherited work cannot be safely separated from this task, report the issue and avoid destructive operations.

Use an isolated, reviewable patch for Phase 3 wherever practical.

The `test_images/` directory must remain excluded from Git. Reference images may be analyzed read-only.

---

## 2. Audit all current confidence assignments

Inspect:

- `decision_logic.py`
- `hypothesis_engine.py`
- `hypothesis_evidence.py`
- The evidence-lineage and corroboration modules
- Confidence-related summary/narrative helpers
- `reasoning_persistence.py`
- Any other modules that assign or modify confidence tiers

Identify every place where the application:

- Returns a hardcoded confidence tier.
- Changes confidence based on a decision route.
- Downgrades confidence because of contradictory evidence.
- Raises confidence because of signal convergence.
- Uses suspicious-domain counts.
- Uses evidence reliability.
- Uses camera-like counterevidence.
- Uses provenance declarations.
- Uses missing evidence or detector unavailability.
- Uses route precedence to influence final confidence.
- Generates a confidence rationale.

Produce an inventory containing:

| Field | Description |
|---|---|
| Rule identifier | Stable identifier |
| Source location | File and function |
| Hypothesis | Applicable forensic hypothesis |
| Current assignment | High, Medium, Low or Inconclusive |
| Required evidence | Inputs and conditions |
| Contradictions | Relevant counterevidence |
| Reliability controls | Existing safeguards |
| Route dependency | Whether route selection determines confidence |
| Proposed policy equivalent | Centralized replacement |
| Expected behavioral impact | Unchanged or potentially different |

Distinguish deliberately mechanism-specific confidence requirements from accidental hardcoding.

Do not assume that all hardcoded labels are inherently incorrect. Some may represent valid forensic constraints that should become explicit policy rules.

---

## 3. Define confidence semantics

Before implementing a new policy, document what confidence means in SignalLens.

Confidence must refer to **the strength and reliability of support for a specific forensic interpretation**, not the probability that an image is AI-generated.

Distinguish:

### Evidence strength

How strongly an observed forensic indicator supports a hypothesis.

### Evidence reliability

Whether the measurement is technically trustworthy and satisfies applicable quality checks.

### Evidence specificity

Whether the indicator supports a particular mechanism or is compatible with several explanations.

### Evidence corroboration

Whether distinguishable sources or measurements provide additional supporting information.

Use the Phase 2B lineage model. Do not confuse multiple descendants of one measurement with independent corroboration.

### Contradictory evidence

Evidence directly challenging the hypothesis being assessed.

### Moderating evidence

Evidence that limits interpretation without directly disproving the hypothesis.

### Evidence coverage

Whether the necessary detectors ran and produced usable observations.

Missing evidence must not be treated as negative evidence.

Document these semantics before designing the final policy.

---

## 4. Introduce a centralized confidence-policy component

Implement a small, testable policy module.

A suggested name is:

`confidence_policy.py`

Use the actual project conventions when deciding filenames and interfaces.

The policy should consume existing structured hypothesis assessments, reliability information and corroboration results.

It should not independently reconstruct forensic evidence from loosely interpreted strings.

### Suggested interface

```python
@dataclass(frozen=True)
class ConfidencePolicyResult:
    hypothesis: str
    tier: str
    policy_rule: str
    supporting_evidence: tuple[str, ...]
    contradicting_evidence: tuple[str, ...]
    moderating_evidence: tuple[str, ...]
    reliability_limitations: tuple[str, ...]
    rationale: tuple[str, ...]
```

Adapt this structure to the existing dataclasses and serialization contracts.

### Required behavior

The policy must:

1. Evaluate confidence separately for each hypothesis.
2. Apply explicit, deterministic rules.
3. Respect evidence reliability and coverage.
4. Respect lineage-aware corroboration results.
5. Preserve hypothesis-specific contradictions.
6. Distinguish moderation from direct contradiction.
7. Avoid unsupported confidence upgrades from multiple related indicators.
8. Preserve provenance-verification limitations.
9. Produce an explanation identifying the policy rule responsible.
10. Never imply a calibrated probability.

### Critical requirement

Do not replace route-specific hardcoding with a different collection of arbitrary global thresholds.

The policy should consolidate existing justified rules and make their meaning explicit.

If a new threshold or coefficient appears necessary, document it as an unresolved calibration requirement rather than inventing a value.

---

## 5. Separate hypothesis selection from confidence assignment

### Current risk

The decision engine may select a hypothesis and simultaneously assign its confidence using a route-specific return value.

This can make confidence depend on which route happened to match.

### Required architecture

Separate the processing into:

**Stage A — Evidence interpretation**

Produce forensic observations and derived signals.

**Stage B — Hypothesis assessment**

Evaluate synthetic origin, localized editing and camera-acquisition compatibility.

**Stage C — Hypothesis selection**

Determine the primary interpretation using the existing deterministic synthesis rules.

**Stage D — Confidence policy**

Assign confidence to each hypothesis using the centralized policy.

**Stage E — Overall presentation**

Present the selected primary hypothesis and its confidence, together with secondary findings and limitations.

The primary hypothesis's confidence must not be determined merely by its position in the route registry.

### Important

Preserve the existing hypothesis-selection architecture unless a strictly necessary correctness issue is identified.

Do not rewrite the entire decision engine.

Do not make the hypothesis with the highest confidence automatically become the primary hypothesis.

The strongest-supported hypothesis and the most relevant forensic interpretation are related but not necessarily identical.

---

## 6. Preserve hypothesis-specific confidence behavior

The centralized policy must correctly handle three hypothesis families.

### A. Synthetic origin

Relevant considerations include:

- Explicit generation declarations.
- Verified versus unverified provenance.
- Synthetic-structure indicators.
- Evidence specificity.
- Lineage-aware corroboration.
- Camera-compatible observations.
- Evidence limitations.

A generation declaration that has not been cryptographically authenticated must not automatically receive High confidence merely because it is explicit.

### B. Localized editing

Relevant considerations include:

- Boundary-focused anomalies.
- Localized compression inconsistencies.
- Spatially supported duplication.
- Subject/background processing differences.
- Mask reliability.
- Compound mechanism evidence.
- Contradictory or moderating indicators.

Strong localized-editing evidence may justify High confidence in a processing inconsistency without justifying High confidence in AI generation.

### C. Camera-acquisition compatibility

Relevant considerations include:

- Sensor-origin structure.
- CFA/demosaicing evidence.
- Measurement reliability.
- Processing-history limitations.
- Potential compatibility with synthetic or edited content.

Camera-like evidence must not be interpreted as cryptographic proof of photographic authenticity.

### Acceptance criteria

The policy must retain the different evidentiary meanings of these three hypothesis families.

It must not force them onto an identical numerical confidence formula when their evidence semantics differ.

---

## 7. Reliability and missing-evidence safeguards

Phase 1.2 established that unreliable segmentation may legitimately prevent region-dependent analyses from executing.

Phase 2A established correct handling of unavailable evidence.

Phase 2B.3 corrected one false independence condition.

The confidence policy must preserve all three safeguards.

### Required cases

- Reliable person segmentation.
- Limited person segmentation.
- Rejected person segmentation.
- Missing regional measurements.
- Unavailable metadata.
- Unverified synthetic declaration.
- Camera-like evidence.
- One primary observation with multiple descendants.
- Multiple distinct measurement sources.
- Conflicting evidence.
- Inconclusive forensic observations.

### Required behavior

Unavailable evidence cannot increase or decrease confidence simply because the detector did not execute.

However, missing evidence may limit the maximum confidence achievable when a hypothesis specifically requires that evidence.

Such limits must be explicit and justified.

An unreliable region mask must not support a High-confidence person-boundary finding.

A collection of derived signals from one shared measurement must not manufacture strong independent corroboration.

---

## 8. Preserve route behavior where justified

Inspect the existing route-specific confidence assignments.

For each one, determine whether its conditions express:

- Genuine evidence requirements.
- Mechanism-specific reliability constraints.
- A necessary confidence cap.
- A provenance trust limitation.
- An inappropriate hardcoded shortcut.

Translate legitimate rules into centralized policy conditions.

Remove inappropriate confidence assignment from route implementations wherever possible.

If existing routes must retain a provisional tier for backward compatibility, treat it as diagnostic or legacy information rather than the authoritative confidence result.

Document every remaining route-dependent confidence assignment and why it cannot yet be removed.

### Acceptance criteria

- Centralized policy is authoritative for final hypothesis confidence.
- Route ordering does not independently determine confidence.
- Equivalent evidence produces equivalent hypothesis confidence regardless of irrelevant route ordering.
- Existing mechanism-specific constraints remain meaningful.

---

## 9. Confidence rationale and reasoning trace

Extend the reasoning trace with a clear policy audit.

Suggested structure:

```json
{
  "confidence_policy": {
    "version": "3",
    "primary_hypothesis": "synthetic_origin",
    "assessments": [
      {
        "hypothesis": "synthetic_origin",
        "tier": "Medium",
        "policy_rule": "unverified_generation_declaration",
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "moderating_evidence": [],
        "limitations": [],
        "rationale": []
      }
    ]
  }
}
```

Use the existing serialization architecture.

Preserve current reasoning-trace fields.

The following must remain consistent:

- Primary hypothesis.
- Dominant pattern.
- Overall confidence.
- Hypothesis confidence.
- Supporting signals.
- Contradicting signals.
- Moderating evidence.
- Confidence rationale.

Avoid duplicate or conflicting explanations generated independently by separate modules.

Every final confidence tier must be traceable to a named policy rule.

---

## 10. Testing requirements

Preserve all **262 existing tests**.

Add targeted tests for:

| Scenario | Expected result |
|---|---|
| Explicit unverified generation declaration | Appropriate bounded confidence |
| Verified generation assertion | Distinct treatment, only when genuinely verified |
| Ambiguous generation metadata | No unjustified High confidence |
| Metadata missing | No positive or negative inference |
| Strong localized processing with reliable evidence | High remains possible |
| Strong regional anomaly with rejected mask | Reliability limits applied |
| One primary signal and several descendants | No artificial confidence upgrade |
| Two distinct measurements | Legitimate corroboration retained |
| Strong synthetic and weak localized-edit findings | Confidence assessed separately |
| Strong localized edit and inconclusive synthetic origin | No cross-hypothesis confidence transfer |
| Camera-like signal with synthetic declaration | Coexistence preserved |
| Contradictory evidence | Hypothesis-specific adjustment |
| Moderating evidence | Not misrepresented as direct contradiction |
| Missing detector results | Coverage limitation recorded |
| Identical evidence with reordered routes | Equivalent confidence |
| Repeated evaluation | Deterministic result |
| JSON serialization | Backward compatibility |
| GUI/summary consumption | Existing interfaces preserved |
| Phase 2A calculation ledger | Unchanged |
| Phase 2B.2 shadow diagnostics | Unchanged |
| Phase 2B.3 corroboration gates | Unchanged |

Tests must validate the actual policy integration, not just isolated helper behavior.

Do not introduce new third-party dependencies.

---

## 11. Reference-image validation

Run the existing reference images through the full headless pipeline using `subject_based` mode.

### Instagram reference

Current reported baseline:

- Suspicious score: **20.47705**
- Benign score: **2.25**
- Primary interpretation: localized editing
- Confidence: High

### Midjourney reference

Current reported baseline:

- Suspicious score: **6.0375**
- Benign score: **1.5**
- Primary interpretation: unverified synthetic-generation declaration
- Confidence: Medium

### Requirements

For each image report:

- Primary hypothesis.
- Supporting evidence.
- Contradictory evidence.
- Moderating evidence.
- Evidence reliability.
- Confidence-policy rule selected.
- Previous confidence tier.
- New confidence tier.
- Production suspicious and benign scores.
- Completed, unavailable and failed pipeline stages.

Do not modify the confidence policy to force preservation of historical tiers.

If a confidence tier changes, identify the precise rule and evidence responsible.

No numerical scoring coefficients or detector thresholds may be changed.

Do not treat the two reference images as a sufficient statistical calibration dataset.

---

## 12. Compatibility requirements

Preserve:

- The five-element `synthesize_overall()` API.
- Existing hypothesis-assessment structures where practical.
- Existing reasoning-trace JSON fields.
- Current controller and GUI integration.
- Current production scorecard calculation.
- Evidence-lineage infrastructure.
- Corroboration gates.
- Mask-reliability policy.
- Metadata/provenance classification behavior.

If additional structured fields are required, add them compatibly.

Do not introduce unnecessary GUI changes.

### Scope restrictions

Do not modify:

- Detector algorithms.
- Detection thresholds.
- Score weights or coefficients.
- Numerical aggregation.
- Experimental shadow scoring.
- Provenance cryptographic validation.
- MediaPipe segmentation rules.
- Dependencies.
- PyInstaller packaging.
- GitHub workflows.

Do not undertake a general statistical calibration project.

Do not redesign the complete reasoning engine.

Do not stage, commit, push, merge, tag or publish.

---

## 13. Required deliverables

Create documentation under:

`doc/phase3_confidence_policy/`

### A. Confidence-rule inventory

`confidence_rule_inventory.md`

Document every existing route-specific confidence assignment and its proposed centralized equivalent.

### B. Policy specification

`confidence_policy_specification.md`

Define confidence semantics, rules, evidence requirements, limitations and precedence.

### C. Implementation report

`confidence_policy_implementation.md`

Describe implementation, changed files, compatibility and remaining caveats.

### D. Reference comparison

`confidence_policy_reference_comparison.md`

Compare the Instagram and Midjourney cases before and after implementation.

### E. Regression tests

Add dedicated tests for the centralized confidence policy and its integration with hypothesis synthesis.

---

## 14. Required final report

Provide:

**A. Baseline**

Branch, HEAD, working-tree status and test baseline.

**B. Confidence-rule inventory**

Number of confidence assignments inspected, consolidated and intentionally retained.

**C. Implementation**

New policy module, modified files and integration points.

**D. Behavioral changes**

Which confidence rules changed meaningfully and why.

**E. Reference-image validation**

Before/after outcomes for Instagram and Midjourney.

**F. Regression testing**

Exact test counts, failures and skips.

**G. Compatibility**

Confirm API, JSON, GUI, scorecard and shadow-scoring compatibility.

**H. Remaining limitations**

Distinguish incomplete implementation from statistical calibration limitations.

**I. Git status**

Report changed/untracked files and confirm nothing staged, committed or pushed.

---

## Definition of Done

Phase 3 is complete when:

1. Every authoritative confidence assignment is governed by an explicit, centralized policy.
2. Route-specific hardcoded confidence labels no longer determine final confidence.
3. Confidence is evaluated separately for each forensic hypothesis.
4. Confidence rules account for evidence reliability, specificity, corroboration, contradictions and coverage.
5. Shared-ancestry descendants cannot manufacture High confidence.
6. Unverified provenance remains appropriately qualified.
7. Missing evidence does not create artificial positive or negative support.
8. Every final confidence tier has an auditable policy-rule explanation.
9. Existing forensic scores and detector outputs are unchanged.
10. All regression tests pass and both reference images complete without pipeline failures.

**Core principle: Confidence must arise from the quality, relevance and reliability of evidence supporting a particular hypothesis—not from which decision route happened to match first.**

Implement the centralized confidence policy, validate its integration and deliver the requested reports. Do not commit or push.

Do not proceed to unrelated improvements or a new development phase.
