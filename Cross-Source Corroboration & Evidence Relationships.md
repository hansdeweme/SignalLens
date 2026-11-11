# Codex Task H — SignalLens: Cross-Source Corroboration & Evidence Relationships

**Repository:** `D:\Coding\SignalLens`  
**Target release:** Next beta candidate, subject to scope and validation  
**Priority:** High — investigation reasoning and evidential correctness  
**Task type:** Source audit followed by bounded implementation  
**Scope:** Cross-source evidence relationships, claim agreement, source-image association, investigation synthesis and presentation  
**Git:** Do not stage, commit, push, tag or publish.

## 1. Mission

Implement a defensible mechanism for evaluating agreement between embedded image metadata and external source evidence.

SignalLens currently records image-generation declarations and reviewed OSINT records, but does not clearly demonstrate how their agreement contributes to the investigation-level conclusion.

The problem is not that OSINT lacks a numerical weight.

The problem is that **evidence relationships are not adequately represented or evaluated**.

Two individually unauthenticated sources can provide useful corroboration when their claims agree and both can be associated with the investigated image.

However, agreement does not automatically establish independent verification, cryptographic authenticity or the truth of every claim.

The implementation must distinguish:

1. Individual evidence claims.
2. The association of each source with the investigated image.
3. Agreement and disagreement between claims.
4. Dependencies between evidence sources.
5. The resulting investigation-level corroboration assessment.
6. Remaining uncertainty.

**Goal: Move from collecting evidence to reasoning about relationships between evidence.**

## 2. Mandatory preparation

Read:

- `AGENTS.md`
- `doc/test_quality/TEST_DISCIPLINE.md`
- `doc/reasoning_audit/origin_processing/task_d_implementation.md`
- `doc/reasoning_audit/origin_processing/task_e_corroboration_gate.md`
- `doc/reasoning_audit/origin_processing/task_f_signal_semantics.md`
- `doc/reasoning_audit/origin_processing/task_g_storage_layout.md`
- Relevant existing provenance, OSINT and investigation-synthesis contracts.

Inspect:

- Embedded metadata extraction.
- ComfyUI workflow interpretation.
- Non-graph generation declaration handling.
- OSINT record structure and persistence.
- Analyst review status.
- Image identity and source-match handling.
- Evidence references and lineage.
- Investigation synthesis and revisions.
- GUI presentation.
- HTML/JSON/text reporting.

Before implementation, establish whether the current synthesis already evaluates agreement between technical declarations and external evidence.

Do not introduce a duplicate mechanism if one already exists.

Preserve all unrelated working-tree changes.

## 3. Primary reference case — Stable Diffusion/FLUX.2

Investigated file:

`test_images/stablediffusion/stabldiff_003.png`

SHA-256:

`b4f305f65537010b4d2926b41e4ec092889ea0a1607075323da10f02dbf8ac5e`

External source:

https://www.reddit.com/r/StableDiffusion/comments/1t2kyjt/the_greatest_amateur_photo_realism_i_have_ever/

Referenced image:

https://preview.redd.it/the-greatest-amateur-photo-realism-i-have-ever-achieved-v0-0c8djb2b8xyg1.png?width=1024&format=png&auto=webp&s=61f9666b438865da67fcb76a93f8d6bd3168a22b

The reviewed OSINT record contains:

```text
mode: manual
analyst_reviewed: true
review_status: reviewed_matches_found
dominant_source_type: ai_gallery
ai_source_context_detected: true
best_match_similarity: null
possible_original_found: false
```

The external Reddit discussion presents the images as photorealistic AI-generated work and describes a FLUX.2 Klein / photorealism LoRA workflow.

The embedded image metadata contains a coherent ComfyUI graph interpreted as full-image generation from an empty latent.

Its interpretation includes:

```text
declared_process: full_image_generation
graph_interpretation_status: coherent
provenance_authenticity: unverified
```

The graph fingerprint and supporting node paths are preserved in the existing forensic provenance record.

### Existing forensic assessment

```text
Primary hypothesis: localized_editing
Confidence: High

Synthetic origin: Medium
Declared process: full_image_generation

Separate editing:
not_established_from_regional_anomalies

Technical provenance:
unverified
```

The localized-editing hypothesis is associated with strong regional processing measurements.

It does not establish a subsequent editing operation.

**Do not alter these frozen forensic results to make the reference example produce a preferred verdict.**

The intended improvement is in the investigation synthesis, where the combined technical and external declarations should be assessed.

## 4. Investigation A — Trace the current OSINT integration

First determine the precise handling of the current OSINT record.

Trace the lifecycle:

```text
Manual source entry
        |
        v
OSINT persistence
        |
        v
Analyst review
        |
        v
Image association
        |
        v
Investigation synthesis
        |
        v
Overview / Evidence / Reasoning / Reports
```

Identify where the following information is retained, simplified or lost:

- Source page URL.
- Direct image URL.
- Source type.
- Creator attribution.
- Explicit source claim.
- Generation-model information.
- Analyst review status.
- Match status and method.
- Source-image association.
- Source dependencies.
- Relationship to embedded metadata.

Determine whether the current synthesis reduces the external evidence to:

```text
ai_source_context_detected = true
```

or another generic flag.

If so, identify what relevant evidence is lost.

Inspect the latest `final_summary.json` and investigation revision representation where available.

Do not infer missing synthesis behavior solely from the frozen forensic reasoning trace.

## 5. Evidence claims as distinct objects

Introduce or reuse a minimal representation of evidence claims.

A claim should distinguish:

- Source reference.
- Claim type.
- Claimed process or property.
- Supporting details.
- Evidence origin.
- Review status.
- Verification status.
- Limitations.

Relevant claim types may include:

```text
full_image_generation
localized_editing
camera_capture
ai_tool_usage
model_family
workflow_description
creator_attribution
```

These are illustrative categories. Reuse existing canonical terminology where possible.

Do not build an unrestricted natural-language knowledge graph.

A claim extracted from an embedded workflow should not be conflated with a claim made by a Reddit author.

A generic reference to an AI tool must not automatically be interpreted as a declaration of full-image generation.

## 6. Source-image association

Before external evidence can corroborate the investigated image's creation, SignalLens must assess whether the source refers to that image.

Distinguish at least:

| Association status | Meaning |
|---|---|
| Unestablished | A source URL was entered, but no image association was demonstrated |
| Analyst-associated | An analyst explicitly associated the source image with the investigated image |
| Visually verified | Reproducible visual matching supports the association |
| Byte-identical | A verified cryptographic hash match establishes identical image bytes |

Use existing source-match semantics where available.

The precise status names may differ.

### Requirements

- Do not treat a supplied direct-image URL as proof of identity.
- Do not treat `analyst_reviewed=true` as proof of an image match.
- Do not treat a null similarity score as a verified match.
- Do not equate visual similarity with byte identity.
- Do not infer ownership or authorship solely from a Reddit username.
- Preserve the verification method and any analyst assertion.
- Preserve the correct SHA-256 association with the local investigated image.

**Important:** The current Stable Diffusion record contains a manually reviewed source, but no verified image-match score.

Therefore, its source-image association must remain qualified unless additional evidence is established.

### Bounded verification

If existing code already supports downloading or comparing source images, reuse it.

Otherwise, implement only the minimum needed for an analyst to record an explicit, reviewable image-association claim.

Do not introduce a new general-purpose image-search service, web crawler or provider integration.

Any automated verification must be reproducible and clearly identified as such.

## 7. Cross-source agreement assessment

Implement an investigation-level assessment that compares compatible claims from different evidence sources.

For the reference case:

```text
Evidence A
----------
Source: Embedded ComfyUI workflow

Claim:
Full-image generation

Details:
Coherent generation graph from empty latent

Authenticity:
Unverified

Evidence B
----------
Source: Reddit creator-side account

Claim:
AI-generated image

Details:
FLUX.2 Klein / photorealism LoRA

Verification:
Reviewed external source

Image association:
Not independently verified in current record
```

The assessment should determine:

1. Whether the claims concern the same image.
2. Whether the claimed creation processes are compatible.
3. Whether model or workflow details agree.
4. Whether the claims contradict each other.
5. Whether the evidence sources are independent or potentially dependent.
6. Whether the agreement materially improves the investigation's interpretation.

Do not compare merely the words "AI" or "generated".

Compare substantive attributes where reliably available.

For example, a coherent full-generation workflow and an external creator account describing AI generation are compatible claims.

A claim describing an image-to-image transformation may require a more nuanced interpretation.

A camera-capture claim and a generation declaration may conflict, coexist or refer to different stages of the image's history.

Avoid binary agreement rules where the underlying processes are not mutually exclusive.

## 8. Evidence dependence and corroboration strength

This is a critical requirement.

Two sources are not necessarily independent merely because one is embedded in a PNG and another appears on Reddit.

Both may originate from the same creator.

Distinguish:

- Agreement between claims.
- Independence of evidence sources.
- Authenticity of evidence.
- Strength of source-image association.
- Corroboration strength.

Do not double-count the same creator's claim as independent confirmation.

Use qualitative corroboration levels with explicit reasons rather than invented probabilities.

Suggested conceptual states:

```text
not_assessed
insufficient_association
contextual_agreement
corroborated_declaration
conflicting_claims
```

These are suggestions, not mandatory names.

A strong corroboration state should require an appropriately established source-image association.

An unverified source should not receive a stronger status merely because it mentions a matching generative-model brand.

Preserve uncertainty as an explicit outcome.

## 9. Investigation-level interpretation

Extend the existing multidimensional investigation synthesis rather than changing the frozen forensic result.

Maintain separate assessments for:

```text
origin_assessment
regional_anomaly_assessment
separate_edit_assessment
technical_provenance_authenticity
external_source_corroboration
```

The new relationship assessment should feed into the current investigation synthesis.

### Expected behavior

If a reviewed external creator claim agrees with a coherent embedded full-generation workflow, and an appropriate image association is established, the final investigation should explicitly describe that corroboration.

The assessment may strengthen the investigation-level support for synthetic creation.

It must not automatically:

- Increase pixel-based suspicious scores.
- Change forensic detector confidence.
- Authenticate metadata.
- Establish a separate editing operation.
- Treat dependent creator claims as independent confirmations.

### Current reference-case limitation

With the current OSINT record, SignalLens may legitimately conclude:

```text
Cross-source claim agreement:
Compatible

Source-image association:
Insufficiently verified

Overall corroboration:
Conditional / limited

Technical authenticity:
Unverified
```

This is preferable to either ignoring the external evidence or treating it as conclusive proof.

## 10. Contradictory evidence

A credible evidence-relationship mechanism must also handle disagreement.

For example:

```text
Embedded metadata:
Full-image generation

External source:
Claims an unmodified camera photograph
```

Expected behavior:

- Preserve both claims.
- Identify the contradiction.
- Assess image association and source credibility.
- Avoid silently selecting whichever claim has the higher score.
- Explain why the available evidence does not resolve the conflict.

Do not infer that contradictory evidence automatically disproves synthetic origin.

Do not treat an absence of metadata as a contradiction of an external generation claim.

## 11. OSINT review workflow

Review the existing analyst interaction.

Determine whether the GUI allows the user to explicitly record:

- The relevant external claim.
- The asserted relationship to the investigated image.
- Whether the image association was visually checked.
- Whether the creator or publisher made the claim.
- Whether details match embedded metadata.
- Remaining uncertainty.

If the current controls cannot represent the relevant relationship, implement the smallest necessary enhancement using the existing OSINT review interface.

Do not create a new workspace.

Do not require the user to manually re-enter information already available in structured metadata.

Do not silently convert a manually entered claim into a system-verified claim.

## 12. GUI and reporting

Ensure the canonical investigation synthesis is used consistently.

### Overview

Present the combined investigation conclusion, including material external corroboration where applicable.

Do not allow a regional anomaly to be mistaken for a proven editing history.

### Evidence

Display the relationship between embedded metadata and reviewed external claims.

Make the source-image association status visible.

### Reasoning

Distinguish frozen forensic reasoning from subsequent cross-source corroboration.

### Provenance

Show technical provenance authenticity separately from external corroboration.

### Reports

Include:

- Evidence sources.
- Claims being compared.
- Agreement or disagreement.
- Image-association status.
- Dependence limitations.
- Resulting corroboration assessment.
- Investigation revision identifier.

Avoid repeating the same explanation throughout every workspace.

The report must allow an analyst to reconstruct why the evidence was considered mutually consistent.

## 13. Investigation revisions and reproducibility

Preserve Task D's immutability guarantees.

When an analyst:

- Adds a creator claim.
- Changes source-image association.
- Confirms or rejects a match.
- Updates review status.
- Removes an erroneous source.

SignalLens should recompute the investigation synthesis without rerunning pixel detectors.

Create a new investigation revision when the evidence materially changes.

Historical revisions must retain the evidence relationships and conclusions that existed when they were created.

Do not rewrite frozen forensic results.

The implementation must work with the new Task G storage layout and remain compatible with legacy saved investigations.

## 14. Testing discipline

Read and follow `doc/test_quality/TEST_DISCIPLINE.md`.

**Target no more than three additional collected test cases. Zero unnecessary tests.**

Baseline: **527 passed**.

Inspect existing OSINT, synthesis, lifecycle and report tests before adding coverage.

Prefer extending existing tests.

Essential behavioral scenarios:

### A. Corroborating declarations

A coherent generation workflow and an associated reviewed creator claim produce explicit cross-source agreement.

The forensic measurements remain unchanged.

### B. Insufficient image association

A relevant creator claim with only a supplied URL or unverified image association does not become strong image-specific corroboration.

### C. Contradictory or revised evidence

Contradictory claims remain visible and qualified.

An analyst revision recomputes synthesis without rerunning detectors or modifying historical reports.

These are behavioral requirements, not instructions to create three new test modules.

Avoid:

- Duplicated GUI and unit tests.
- New image fixtures without justification.
- Broad golden-output regeneration.
- Artificial probabilities.
- Arbitrary threshold tuning.
- Reimplementing OSINT providers.
- Excessive test proliferation.

Run focused tests during implementation.

Run the full suite once at the final validation gate.

Report baseline, additions, removals and net test count.

## 15. Reference validation

### Stable Diffusion / Reddit

Validate:

- The embedded full-generation workflow remains recognized.
- The Reddit claim is retained with its source reference.
- The relationship between claims is explicitly evaluated.
- The actual image-association status is disclosed.
- Source dependence is considered.
- External corroboration can influence investigation synthesis.
- Technical provenance remains unverified.
- High regional-anomaly support remains separate from editing-history certainty.
- No frozen forensic scores change.

### Midjourney / external article

Reuse the earlier Midjourney reference where possible.

Check that the external gallery's generation claim and the embedded generation declaration can be assessed consistently.

Do not assume the gallery is necessarily the original creator.

### Conventional photograph

Use an existing conventional-photo fixture if available.

Confirm that an unsupported external claim cannot override genuine measurement results or automatically establish synthetic origin.

## 16. Explicit exclusions

This task does not authorize:

- Detector changes.
- Scorecard retuning.
- Hypothesis-precedence changes.
- Broad forensic reasoning refactoring.
- Automatic Reddit scraping.
- General-purpose web-search integration.
- New machine-learning classifiers.
- Cryptographic provenance verification infrastructure.
- Storage-layout migration.
- A redesigned GUI.
- New external APIs or dependencies without clear necessity.
- Release packaging or PyInstaller builds.

Native executable validation remains a separate release activity.

## 17. Deliverables

Create:

`doc/reasoning_audit/origin_processing/task_h_cross_source_corroboration.md`

Include:

1. Current OSINT-to-synthesis data-flow audit.
2. Root cause of any lost or diluted evidence.
3. Claim and relationship semantics.
4. Source-image association model.
5. Evidence dependence and uncertainty handling.
6. Implementation changes.
7. Stable Diffusion before/after comparison.
8. Midjourney and conventional-photo regression results.
9. GUI and report consistency.
10. Investigation revision behavior.
11. Test results and test-count accounting.
12. Git status and remaining limitations.

Avoid unnecessary additional documentation.

## 18. Acceptance criteria

Task H is complete when:

- Embedded metadata and external source claims can be compared.
- Material agreement or disagreement is explicitly represented.
- Source-image association strength is evaluated separately.
- Reviewed evidence is not automatically treated as verified image identity.
- Source dependence is visible and prevents naïve double counting.
- Meaningful corroboration influences investigation-level conclusions.
- Frozen forensic measurements and confidence policies remain unchanged.
- Separate editing is not inferred from regional anomalies.
- Technical provenance authenticity remains independent of source corroboration.
- The GUI communicates combined evidence and limitations.
- Reports preserve the evidence relationship and its rationale.
- OSINT revisions update synthesis without rerunning detectors.
- Legacy and Task G investigation storage remain compatible.
- The full existing test suite passes.
- Test growth remains minimal and justified.
- Nothing is staged, committed, pushed, tagged or published.

## 19. Final Codex response

Return:

**1. Root cause:** Why the previous synthesis did not adequately reflect combined evidence.

**2. Evidence model:** Claim agreement, image association and source dependence.

**3. Implementation:** What changed and why.

**4. Stable Diffusion reference:** Before/after interpretation.

**5. Regression cases:** Midjourney and conventional photography.

**6. Investigation lifecycle:** Revision, immutability and report behavior.

**7. Validation:** Focused tests, full suite and test-count delta.

**8. Git:** Modified files, unrelated changes preserved and no commits.

**9. Limitations:** What remains unverified.

**10. Status:** Complete / Conditional / Blocked.

**Guiding principle: Corroboration is established through meaningful agreement between evidence claims, qualified by image identity, source dependence and authenticity—not by simply adding evidence scores.**