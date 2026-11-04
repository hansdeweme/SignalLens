# CODEX TASK — SignalLens Final Acceptance Audit: Original 10 Reasoning-Engine Corrections

## Mission

You are the independent principal software auditor, Python quality engineer and forensic reasoning specialist for SignalLens.

Over several development phases, SignalLens's reasoning engine has been substantially corrected. The objective was to address ten specific weaknesses identified during real-image testing.

Your task is to perform a **final, source-code-based acceptance audit of those original ten corrections**.

Do not assume that an implementation is correct simply because a previous Codex session reported success or because regression tests pass.

Verify the actual implementation, its integration, its behavior and its compatibility.

The result must be a defensible determination of whether the original ten-point correction roadmap can be closed.

**This is an acceptance audit, not a new implementation phase.**

---

## 1. Current project baseline

Previous phases:

| Phase | Purpose |
|---|---|
| 1 | Reasoning correctness, metadata propagation and provenance interpretation |
| 1.1 | Hypothesis-scoped supporting and contradicting evidence |
| 1.2 | Reliable masking failure handling and pipeline resilience |
| 2A | Mathematical scorecard integrity |
| 2B.1 | Evidence-dependency audit |
| 2B.2 | Evidence lineage and shadow marginal-credit analysis |
| 2B.3 | Production corroboration integrity |
| 3 | Centralized hypothesis-aware confidence policy |

Latest reported validation:

- 297 automated tests passed.
- Zero failed or skipped.
- Both real-image reference pipelines completed without failures.
- Five-element `synthesize_overall()` API preserved.
- GUI/controller integration preserved.
- Scorecard calculation traces remain mathematically consistent.
- Shadow dependency scoring remains inactive for production decisions.

### Reference results

| Reference | Suspicious | Benign | Final conclusion |
|---|---:|---:|---|
| Instagram | 20.47705 | 2.25 | High — localized editing |
| Midjourney | 6.0375 | 1.5 | Medium — unverified generation declaration |

These are reference baselines, not mandatory outputs if a genuine defect is discovered.

### Git status

Previous sessions reported:

- Several phases implemented with inherited uncommitted changes.
- Changes preserved in isolated phase-specific patches.
- No staging, commits or pushes performed for the latest phases.

Verify the current state rather than assuming those reports remain accurate.

---

## 2. Strict audit scope

Audit the following original requirements.

| # | Correction | Original priority |
|---|---|---|
| 1 | Prevent premature decision-route termination | Critical |
| 2 | Separate synthetic-origin and localized-edit hypotheses | Critical |
| 3 | Correct embedded-prompt propagation | Critical |
| 4 | Correct provenance weighting and interpretation | High |
| 5 | Remove suspicious scoring for missing metadata | High |
| 6 | Prevent double-counting correlated signals | High |
| 7 | Make contradictory evidence hypothesis-specific | High |
| 8 | Correct inconsistent scorecard calculations | High |
| 9 | Decouple confidence from route-specific hardcoding | High |
| 10 | Improve reasoning trace and regression coverage | High |

Do not expand this audit into unrelated detector improvements, performance optimization, GUI redesign, new AI models or general statistical calibration.

The original ten requirements are the sole acceptance scope.

---

## 3. Audit methodology

For each correction:

1. Locate the current implementation.
2. Identify the functions, classes and relevant conditions.
3. Compare actual behavior against the original requirement.
4. Inspect the associated automated tests.
5. Determine whether the tests exercise the actual production integration.
6. Identify untested edge cases.
7. Execute targeted tests where useful.
8. Assess whether the implementation creates contradictions elsewhere.
9. Record the evidence supporting the acceptance decision.

Do not rely exclusively on documentation or earlier Codex summaries.

### Required disposition

Assign exactly one status:

**ACCEPTED**

The original requirement is implemented, integrated and supported by appropriate tests.

**PARTIALLY ACCEPTED**

The principal defect is corrected, but a material part of the original requirement remains unresolved.

**FAILED**

The defect remains, the implementation is incorrect, or the acceptance criteria cannot be demonstrated.

Do not mark a correction accepted merely because its module exists.

Do not mark it failed solely because broader statistical calibration has not been performed, unless that calibration is necessary to satisfy the original requirement.

Every disposition must have a source-code and testing justification.

---

# Part A — Audit the ten original corrections

## 4. Correction #1 — Premature decision-route termination

### Original defect

The reasoning engine previously returned the first matching route.

An inconclusive localized-editing route could suppress stronger synthetic-origin or provenance evidence.

### Verify

- All relevant hypotheses are evaluated before final synthesis.
- An inconclusive localized-editing finding cannot terminate synthetic-origin assessment.
- Route precedence no longer suppresses unrelated evidence.
- Safety and reliability constraints remain effective.
- Hypothesis selection is deterministic.
- Unrelated route reordering does not alter equivalent conclusions.

### Required tests

Inspect and execute tests covering:

- Strong synthetic origin with weak localized editing.
- Strong localized editing with inconclusive synthetic origin.
- Multiple supported hypotheses.
- Multiple inconclusive hypotheses.
- Equivalent evidence evaluated through reordered routes.

---

## 5. Correction #2 — Separate forensic hypotheses

### Original defect

Synthetic origin and localized compositing were treated as competing interpretations within one overall decision.

### Verify

The system maintains separate assessments for:

- Synthetic origin.
- Localized editing.
- Camera-acquisition compatibility.

Confirm each assessment has:

- Supporting evidence.
- Contradicting evidence.
- Moderating or contextual evidence.
- Confidence.
- Evidence limitations.
- Explainable assessment outcome.

Ensure the primary hypothesis is selected without deleting secondary findings.

Verify that the overall narrative and structured JSON remain consistent.

---

## 6. Correction #3 — Embedded generation-prompt propagation

### Original defect

`embedded_generation_prompt_detected` could be produced by metadata extraction but was not recognized consistently by the hypothesis engine.

A subsequent real-image test revealed additional extraction issues involving embedded prompts and IPTC declarations.

### Verify the complete path

`ExifTool → metadata extraction → metadata summary → DerivedSignals → hypothesis assessment → overall conclusion`

Inspect:

- Embedded generation-prompt recognition.
- IPTC `trainedAlgorithmicMedia` interpretation.
- Generic workflow-field handling.
- Creator and author fields.
- Filename and folder-path contamination.
- Missing metadata.
- Inconsistent or conflicting metadata declarations.

Confirm that explicit generation evidence reaches the synthetic-origin assessment.

Confirm that ordinary workflow metadata does not automatically become strong generation evidence.

---

## 7. Correction #4 — Provenance weighting and interpretation

### Original defect

The provenance route required a numeric boost that an explicit synthetic declaration could not satisfy independently.

The engine also needed to distinguish trusted evidence from unverified metadata claims.

### Verify

- Explicit generation declarations can produce a provenance-related hypothesis finding.
- Provenance evaluation does not depend solely on an arbitrary boost threshold.
- Unverified metadata remains explicitly unverified.
- Generic tool attribution is not treated as proof of AI generation.
- AI enhancement remains distinguishable from full generation.
- C2PA presence is not treated as cryptographic verification.
- Conflicting evidence is preserved rather than silently discarded.

Verify that no code path can manufacture a verified provenance claim without genuine validation.

Do not implement cryptographic verification in this audit.

---

## 8. Correction #5 — Missing metadata must not imply suspicion

### Original defect

Sparse or stripped metadata contributed positive suspicious weight despite providing no substantive evidence of synthetic generation.

### Verify

- `sparse_or_stripped` is neutral.
- Missing metadata contributes zero positive suspicious score.
- Missing metadata does not create a suspicious evidence domain.
- Missing metadata does not activate synthetic-origin support.
- Missing metadata does not create artificial benign support.
- Missing metadata is still reported as a provenance limitation.

Check both the metadata builder and downstream scorecard handling.

Include test cases for social-media-style stripped metadata and absent optional metadata objects.

---

## 9. Correction #6 — Correlated evidence and false independence

### Original defect

Multiple derived signals could share the same measurements yet be treated as independent corroboration.

### Previous implementation

- Phase 2B.1 identified computational dependencies.
- Phase 2B.2 introduced evidence lineage and shadow marginal-credit diagnostics.
- Phase 2B.3 corrected a production source-diversity predicate.
- Numerical dependency-adjusted scoring remains experimental.

### Verify

1. Active scoring indicators have explicit lineage records.
2. Derived and composite evidence identify relevant ancestry.
3. The lineage registry corresponds to actual computation paths.
4. Corroboration gates requiring independent sources use appropriate lineage-aware checks.
5. Multiple descendants cannot falsely satisfy such requirements.
6. Legitimate compound mechanisms remain operational.
7. Unsupported independence claims have been corrected.
8. Shadow numerical adjustments do not influence production decisions.
9. Existing numerical scorecard integrity remains intact.

### Special acceptance requirement

**Do not automatically mark correction #6 fully accepted simply because the lineage system and corroboration gate exist.**

Determine whether the original requirement—preventing correlated-signal double-counting—is fully satisfied by the current production implementation.

Specifically distinguish:

- Duplicate numerical contributions.
- Duplicate independent-source credits.
- Legitimate compound evidence.
- Repeated narrative presentation.
- Empirically unverified statistical correlation.

If production still contains potentially redundant numerical scoring contributions, explicitly assess whether they constitute unresolved double-counting within the original correction's scope.

If so, mark the requirement **PARTIALLY ACCEPTED** and explain precisely what remains.

Do not invent new scoring weights to resolve it.

---

## 10. Correction #7 — Hypothesis-specific contradictory evidence

### Original defect

Supporting and contradicting signal lists combined evidence belonging to different hypotheses.

### Verify

- Synthetic-origin conclusions use relevant synthetic-origin evidence.
- Localized-editing conclusions use relevant editing evidence.
- Camera evidence is interpreted as acquisition compatibility.
- Evidence moderation is distinguished from contradiction.
- Boundary consistency is not incorrectly presented as disproving whole-image generation.
- Copy-move evidence is not automatically presented as proof of synthetic origin.
- Narrative and structured assessments agree.

Verify that the current evidence mapping remains extensible and deterministic.

---

## 11. Correction #8 — Mathematical scorecard integrity

### Original defect

Some aggregate scores were calculated before reliability adjustments had been completed.

### Verify

- Final contributions are computed after all applicable adjustments.
- Reliability adjustments are applied exactly once.
- Aggregate scores reconcile with their components.
- Caution penalties are correctly applied.
- Missing evidence contributes no artificial support.
- Invalid numeric values cannot produce confident conclusions.
- Repeated calculations are deterministic.
- Scorecard serialization preserves numerical integrity.
- The Phase 2A calculation ledger can independently reconstruct the final score.

Use exact mathematical reconciliation tests rather than relying only on reference classifications.

---

## 12. Correction #9 — Centralized confidence policy

### Original defect

Decision routes assigned High, Medium or Low confidence directly, creating inconsistent confidence behavior.

### Previous implementation

Phase 3 introduced centralized hypothesis-specific confidence policy.

### Verify

- Every authoritative final confidence tier is determined by the centralized policy.
- Legacy route labels are diagnostic only.
- No alternate execution path bypasses the policy.
- Primary hypothesis selection does not depend on hardcoded confidence labels.
- Reliability caps apply regardless of safeguard-route ordering.
- Lineage-aware corroboration is respected.
- Contradictions and moderation remain hypothesis-specific.
- Missing evidence is handled appropriately.
- Every final tier has an auditable policy-rule explanation.

Inspect all relevant callers and early-return paths, not only the normal successful route.

Confirm that High, Medium and Low remain qualitative heuristic tiers rather than claimed probabilities.

---

## 13. Correction #10 — Reasoning trace and regression coverage

### Original defect

The reasoning trace did not expose all relevant hypothesis findings, discarded routes, score calculations or evidence limitations.

### Verify

The current trace exposes sufficient information to reconstruct:

- Original detector observations.
- Derived evidence.
- Provenance classifications.
- Hypothesis assessments.
- Candidate decision routes.
- Primary hypothesis selection.
- Supporting evidence.
- Contradicting evidence.
- Moderating evidence.
- Scorecard calculations.
- Evidence lineage.
- Corroboration decisions.
- Confidence-policy rule.
- Reliability and coverage limitations.
- Final dominant pattern and confidence.

Check serialization, determinism and backward compatibility.

Verify that sensitive local paths and test-image contents are not unintentionally exposed through committed test fixtures.

### Regression coverage

Review the current test suite for:

- Unit-level coverage.
- Cross-module integration coverage.
- Negative and contradictory cases.
- Missing-evidence cases.
- Corrupted-data handling.
- Real-image pipeline coverage.
- Repeated-evaluation determinism.

Do not equate a large test count with comprehensive coverage.

Identify significant untested paths.

---

# Part B — Integrated validation

## 14. Run the complete regression suite

Run the established test command.

Record:

- Exact tests collected.
- Passed.
- Failed.
- Skipped.
- Warnings.
- Execution environment.
- Python version.

Compare the results with the previous reported baseline of 297 passing tests.

Investigate failures, but do not silently modify production code.

---

## 15. Perform cross-module consistency checks

Inspect and test integration across:

- Metadata extraction.
- Evidence summaries.
- Derived signals.
- Scorecard calculation.
- Evidence lineage.
- Corroboration gates.
- Hypothesis assessments.
- Centralized confidence policy.
- Decision synthesis.
- Narrative rendering.
- Reasoning-trace persistence.
- Controller and GUI consumers.

Verify that one component does not bypass safeguards established by another.

Particularly examine:

- Missing evidence reaching confidence evaluation.
- Inconclusive mechanisms reaching hypothesis selection.
- Unverified provenance reaching the final narrative.
- Unreliable segmentation reaching regional forensic assessments.
- Correlated descendants reaching corroboration gates.

---

## 16. Full reference-image validation

Run both original images through the current headless SignalLens pipeline if they are accessible.

Use `subject_based` analysis mode for both.

Do not modify the images.

### Reference A — Instagram

`test_images/insta_fake/Curvy Leggings Outfit.jpg`

Expected baseline:

- Suspicious score: 20.47705.
- Benign score: 2.25.
- High localized-editing finding.
- No pipeline-stage failures.

### Reference B — Midjourney

`test_images/midjourney/theart1300_real_portrait_full_body_of_a_real_model_with_flowe_bee230dd-b5c0-4bbb-be9a-cc1f373fd317_0.png`

Expected baseline:

- Suspicious score: 6.0375.
- Benign score: 1.5.
- Medium unverified generation declaration.
- Low-reliability person mask handled safely.
- No pipeline-stage failures.

### Required output comparison

| Metric | Instagram | Midjourney |
|---|---|---|
| Suspicious score | | |
| Benign score | | |
| Primary hypothesis | | |
| Overall confidence | | |
| Supporting evidence | | |
| Contradicting evidence | | |
| Moderating evidence | | |
| Segmentation status | | |
| Completed stages | | |
| Unavailable stages | | |
| Failed stages | | |
| Confidence-policy rule | | |

Do not change the implementation merely to force historical results.

Explain any deviations and determine whether they represent a regression, a legitimate correction or an environmental difference.

If images cannot be accessed, state that explicitly and use the existing saved traces as secondary evidence. Do not claim a full image run was performed.

---

# Part C — Git and release-baseline readiness

## 17. Review accumulated repository changes

Inspect:

- Current branch.
- Current HEAD.
- Modified tracked files.
- Untracked files.
- Ignored files.
- Staged changes.
- Changes inherited from earlier phases.
- Generated artifacts accidentally placed in source directories.

Ensure that:

- `test_images/` remains excluded.
- Generated analysis artifacts remain excluded.
- No temporary audit output is accidentally tracked.
- No local secrets or credentials are exposed.
- No unnecessary binary files are included.
- No unrelated detector or dependency changes were introduced.
- The accumulated diff is understandable and reviewable.

### Important

Do not automatically assume the entire accumulated diff belongs to the original ten corrections.

Identify unrelated changes separately.

Do not perform cleanup that could remove user data or generated research artifacts.

---

## 18. Prepare a commit plan

Provide a recommended commit structure that separates logical changes where practical.

For example:

1. Reasoning and metadata correctness.
2. Hypothesis-scoped evidence explanations.
3. Masking reliability and pipeline resilience.
4. Scorecard mathematical integrity.
5. Evidence lineage and corroboration.
6. Centralized confidence policy.
7. Documentation and regression tests.

This is illustrative. Determine the most appropriate grouping from the actual Git diff.

If the accumulated modifications cannot be cleanly separated, recommend a single reviewed baseline commit with an explicit change inventory.

**Do not execute commits.**

Do not stage, commit, push, tag, merge, stash or reset anything.

---

# Part D — Final acceptance report

## 19. Required deliverables

Create:

`doc/final_reasoning_engine_acceptance_audit.md`

The report must contain the following sections.

### A. Executive summary

State whether the original ten-point correction roadmap can be closed.

Use one of:

- **PASS — All ten corrections accepted**
- **CONDITIONAL PASS — No blocking defects, but documented partial acceptance remains**
- **FAIL — One or more original corrections remain materially incomplete**

Do not award PASS if a correction remains materially incomplete.

### B. Ten-point acceptance matrix

| # | Correction | Status | Source evidence | Test evidence | Remaining limitation |
|---|---|---|---|---|---|

Use exact source filenames and function names. Include line references where reliable.

### C. Critical findings

Describe any:

- Remaining correctness defect.
- Inconsistent behavior.
- Missing integration.
- Unsupported confidence assumption.
- Potentially misleading explanation.
- Material regression risk.

Rank findings by severity.

### D. Integrated validation

Include exact test results and both reference-image analyses.

### E. Mathematical verification

Confirm scorecard reconstruction and reliability-adjustment consistency.

### F. Confidence-policy verification

Confirm centralized authority and absence of route-specific bypasses.

### G. Corroboration verification

Explain exactly what correction #6 fixes and what numerical dependency issues, if any, remain in production.

### H. Compatibility

Report:

- Five-element synthesis API compatibility.
- JSON reasoning-trace compatibility.
- Controller and GUI integration.
- Evidence-lineage and shadow-mode isolation.
- Runtime or dependency concerns.

### I. Git readiness

Provide working-tree inventory and recommended commit sequence.

### J. Final disposition

For every outstanding issue, specify:

- Whether it blocks closure of the original roadmap.
- Why.
- Exact affected module.
- Minimal required corrective action.
- Relevant regression test.

Separate blocking correctness defects from optional future enhancements.

---

## 20. Required final Codex response

Return a concise summary containing:

**1. Overall verdict:** PASS, CONDITIONAL PASS or FAIL.

**2. Original corrections:** count accepted, partially accepted and failed.

**3. Tests:** exact passed, failed and skipped counts.

**4. Reference images:** outcomes and deviations.

**5. Blocking issues:** only issues preventing closure.

**6. Nonblocking limitations:** documented separately.

**7. Git readiness:** branch, current status and recommended commit plan.

**8. Report location:** exact path to the completed acceptance report.

Do not report successful acceptance merely because all prior development phases reported completion.

---

## Strict constraints

- Audit first; do not modify production behavior.
- Do not change detector algorithms.
- Do not change scoring coefficients.
- Do not change confidence-policy rules.
- Do not activate experimental dependency-adjusted scoring.
- Do not modify segmentation thresholds.
- Do not update dependencies.
- Do not redesign the GUI.
- Do not modify PyInstaller packaging.
- Do not delete generated artifacts or local files.
- Do not stage, commit, push, merge, tag, stash or reset.
- Keep `test_images/` excluded from Git.
- Preserve the entire existing working tree.

If a blocking defect is discovered, document the precise minimal correction and required tests. Do not implement it without authorization.

---

## Definition of Done

The audit is complete when:

1. All ten original corrections have been examined directly in the current source.
2. Every correction receives a justified acceptance disposition.
3. The complete regression suite has been executed.
4. Cross-module integration has been reviewed.
5. Both reference-image pipelines have been tested where available.
6. Mathematical scorecard integrity has been independently verified.
7. Confidence-policy authority has been independently verified.
8. Corroboration and numerical double-counting limitations are explicitly distinguished.
9. The accumulated Git diff has been reviewed.
10. A clear final acceptance verdict and commit-readiness plan have been delivered.

**Core principle: A forensic reasoning engine is not accepted because it produces plausible conclusions. It is accepted when the path from observations to conclusions is correct, consistent, reproducible and auditable.**

Complete the audit and report the findings. Do not begin another implementation phase or commit changes.
