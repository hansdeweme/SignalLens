# Task I — Automated Source-Image Retrieval Identity Verification & OSINT Corroboration

**Repository:** `D:\Coding\SignalLens`  
**Application:** SignalLens 0.1.0-Beta  
**Priority:** High  
**Type:** Bounded implementation with security and forensic-integrity requirements  
**Starting test baseline:** 530 passed  
**Git:** Do not stage, commit, push, tag or publish.

## 1. Mission

Implement automated verification of external source images supplied through SignalLens's OSINT workflow.

The application must be able to retrieve an image from a user-provided source URL, compare it with the locally analyzed image, preserve the verification evidence and integrate the result with Task H's existing cross-source corroboration mechanism.

The central question is:

**Does the external source contain the same image that SignalLens analyzed?**

The answer must distinguish exact file identity, visual correspondence, ambiguity, mismatch and retrieval failure.

This task must not introduce another forensic verdict engine.

The verification result is evidence about **image identity and source association**, not direct proof of image-generation history.

## 2. Mandatory preparation

Read:

- `AGENTS.md`
- `doc/test_quality/TEST_DISCIPLINE.md`
- The behavioral test ownership matrix.
- `doc/reasoning_audit/origin_processing/task_d_implementation.md`
- `doc/reasoning_audit/origin_processing/task_h_cross_source_corroboration.md`
- `doc/reasoning_audit/origin_processing/task_g_storage_layout.md`

Inspect existing:

- OSINT URL fields and manual-review workflow.
- `ReverseSearchResult` and match records.
- Source identity and SHA-256 handling.
- Investigation session annotations.
- `evidence_relationships.py`.
- `investigation_synthesis.py`.
- Source relationships UI.
- OSINT dialogs.
- Report revisions and serializers.
- Existing HTTP/image utilities and dependencies.
- Existing image similarity methods, including any implementation inherited from Task C.

Determine which capabilities already exist.

Reuse existing trusted components and canonical evidence models before introducing new abstractions.

Do not create a parallel OSINT subsystem.

Preserve unrelated working-tree changes.

## 3. Primary reference case

Local image:

`test_images/stablediffusion/stabldiff_003.png`

SHA-256:

`b4f305f65537010b4d2926b41e4ec092889ea0a1607075323da10f02dbf8ac5e`

Source page:

https://www.reddit.com/r/StableDiffusion/comments/1t2kyjt/the_greatest_amateur_photo_realism_i_have_ever/

Current manually recorded image reference:

https://www.reddit.com/r/StableDiffusion/comments/1t2kyjt/the_greatest_amateur_photo_realism_i_have_ever/#lightbox

Previously observed Reddit image candidate:

https://preview.redd.it/the-greatest-amateur-photo-realism-i-have-ever-achieved-v0-0c8djb2b8xyg1.png?width=1024&format=png&auto=webp&s=61f9666b438865da67fcb76a93f8d6bd3168a22b

**Important:** The preview URL is a candidate, not assumed to be the original, nor assumed to identify the correct image within a multi-image post.

The analyst reports that the locally investigated PNG is a fresh download of an image from the referenced Reddit publication.

Task H currently records:

```text
Embedded creation process:
    full_image_generation

External creator claim:
    full_image_generation

Creation-process agreement:
    compatible

Model-family agreement:
    compatible

External image association:
    unestablished

Cross-source assessment:
    insufficient_association

Technical provenance:
    unverified
```

The embedded workflow contains a connected FLUX.2 Klein Base 9B LoRA with a filename referring to v13.

The external creator's publication discusses the same model family and a v14 release.

This distinction must remain visible. Model-family agreement is not exact workflow-version agreement.

### Reference objective

Demonstrate that SignalLens can acquire the intended source image and independently establish whether it corresponds to the analyzed local image.

If the original bytes are available, use cryptographic identity verification.

If only a resized/recompressed representation is available, use appropriately qualified visual matching.

Do not hardcode Reddit-specific results or expected source hashes.

## 4. Architecture

Introduce a small, reusable source-image verification component integrated with the existing OSINT record.

Conceptual flow:

```text
OSINT source record
    |
    v
URL and source validation
    |
    v
Candidate image retrieval
    |
    v
Downloaded bytes validation
    |
    v
Cryptographic comparison
    |
    +-- Same SHA-256
    |       |
    |       v
    |   Byte-identical
    |
    +-- Different SHA-256
            |
            v
    Decode and compare images
            |
            +-- Strong visual correspondence
            |       |
            |       v
            |   Visually verified
            |
            +-- Ambiguous
            |       |
            |       v
            |   Analyst review required
            |
            +-- Reliable mismatch
                    |
                    v
                Rejected association

Verification evidence
    |
    v
Task H source association
    |
    v
New investigation synthesis revision
```

Keep the retrieval, matching, evidence persistence and synthesis responsibilities separate.

A verification component should produce a structured result. Task H remains responsible for interpreting the relationship between source claims.

## 5. Source selection and URL handling

The existing OSINT records distinguish:

- Source page URL.
- Direct source-image URL.
- Thumbnail URL.
- Other provider references.

Preserve these distinctions.

### 5.1 Direct image URL

When the analyst provides a genuine direct-image URL, use it as the primary retrieval candidate.

Verify that the response actually contains an image; do not trust the filename or URL extension alone.

### 5.2 Source page URL

When the user supplies an HTML page instead of a direct image, do not attempt to decode the HTML response as an image.

Provide a bounded path to identify candidate images.

Reuse an existing provider integration if available.

If implementing page-level discovery, limit it to straightforward, explicitly present image references, such as suitable image metadata and directly linked images.

Do not introduce:

- A browser automation engine.
- General-purpose scraping.
- Recursive crawling.
- Search-engine result scraping.
- Login or session impersonation.
- Arbitrary JavaScript execution.

### 5.3 Multiple image candidates

A single publication may contain several different images.

Do not assume its first image is the investigated one.

When multiple candidates are available:

- Preserve their individual source URLs.
- Verify each permitted candidate against the local image.
- Apply a strict, bounded candidate limit.
- Distinguish verified results from ambiguous alternatives.
- Present candidate selection to the analyst if the correct image cannot be established automatically.

Do not label all images in the same Reddit post as verified simply because one matches.

### 5.4 Reddit support

The reference case should work when Reddit exposes an accessible direct image asset.

Support standard Reddit image/CDN URLs using the normal safe retrieval mechanism.

Avoid Reddit-specific scraping tricks, authentication workarounds or undocumented API assumptions.

A Reddit lightbox URL must not be treated as a direct image-file URL.

If the original image cannot be retrieved, report that limitation explicitly.

Do not downgrade a valid visually verified transformed copy merely because the original byte-identical PNG is unavailable.

## 6. Network and file security

Treat all external URLs and downloaded content as untrusted.

This is a mandatory security boundary.

Implement or reuse safe HTTP(S) retrieval with:

- Explicit user-triggered retrieval.
- HTTP and HTTPS only.
- Blocking of localhost, private, loopback, link-local, multicast, reserved and other non-public destinations.
- DNS resolution checks.
- Redirect validation at every hop.
- Bounded redirect count.
- Protections against DNS rebinding and connection to an address different from the validated destination.
- Connection and total-transfer timeouts.
- Maximum response/download size.
- Bounded image dimensions and decoded pixel count.
- No automatic use of user credentials or ambient authentication.
- No execution of downloaded content.
- No file-system paths or `file://` URLs.
- No overwriting of local source images or investigation artifacts.
- No unbounded retries.
- No persistent background monitoring.

Do not rely on a URL hostname check alone for SSRF prevention.

Ensure the validated public IP is the actual connection destination, or use an existing HTTP stack that enforces an equivalent restriction.

A redirect to a blocked address must fail safely.

Do not disable TLS verification.

Use safe image decoding and decompression-bomb protections.

Clearly distinguish:

```text
download_failed
unsupported_response
image_decode_failed
verification_failed
verification_completed
```

These are illustrative status names. Reuse existing conventions where possible.

A network failure must never be interpreted as a source-image mismatch.

### Network behavior

Verification must not freeze the GUI.

Use the application's existing worker/threading model.

Provide visible progress, cancellation and appropriate cleanup.

Cancellation must not leave a partially verified or incorrectly promoted association.

No network request should occur silently when merely opening an existing investigation.

## 7. Exact byte-identity verification

For each successfully retrieved source image:

1. Read the actual downloaded bytes.
2. Compute their SHA-256.
3. Compare with the canonical SHA-256 of the locally investigated file.
4. Record the comparison result.

If the hashes match, set the external association to the existing Task H `byte_identical` state.

Preserve:

- Analyzed image SHA-256.
- Downloaded source SHA-256.
- Requested URL.
- Final resolved URL.
- Download timestamp.
- Media type.
- Retrieved file size.
- Comparison method.
- Verification status.
- Relevant limitations.

A byte-identical result establishes the identity of the compared files.

It does not establish:

- Who created the file.
- Whether the publisher is the creator.
- Whether the metadata is truthful.
- Whether the workflow was executed.
- Whether the source was the first publication.
- Whether cryptographic provenance is authenticated.

These distinctions must remain explicit.

## 8. Robust visual matching

When the downloaded image differs at the byte level, determine whether it is visually the same image.

This must handle common distribution transformations:

- Resizing.
- Recompression.
- JPEG conversion.
- PNG-to-WebP conversion.
- Minor color or encoding changes.
- Typical metadata stripping.
- Modest cropping, where defensibly supported.

### Matching approach

Inspect existing image-comparison capabilities first.

Use a bounded, deterministic combination of image descriptors and geometric checks appropriate to the task.

A simple perceptual hash alone must not be sufficient to establish `visually_verified`.

Where relevant, use:

- Perceptual hashing for candidate screening.
- Normalized pixel/structural comparison for aligned versions.
- Feature correspondence and geometric validation when crops or transformations are involved.

Avoid unnecessary machine-learning dependencies.

### False-match protection

The matcher must not produce a strong identity conclusion from:

- Similar-looking portraits.
- Different images of the same subject.
- Images sharing a common background.
- Repeated patterns.
- Generic studio scenes.
- Different generations from the same prompt.
- Crops too small to support reliable identity.

A candidate with inconclusive coverage or geometric support must remain ambiguous.

### Thresholds

Do not select thresholds solely to pass the Stable Diffusion example.

Use existing validation data where possible.

Record the metric definitions, thresholds, applicability and known failure modes.

No output metric should be described as a probability unless it is genuinely calibrated.

### Visual result

A reproducible, sufficiently supported match may receive Task H's `visually_verified` status.

A visually verified result establishes image association, **not identical bytes or authenticated provenance**.

Preserve the specific comparison method and supporting measurements.

## 9. Analyst review

Add an action to the existing OSINT review interface:

**Verify source image**

The action should:

1. Identify the selected OSINT record.
2. Retrieve the intended source image or candidate images.
3. Display the comparison result.
4. Allow inspection of the local and retrieved images.
5. Present the verification method and limitations.
6. Save the accepted verification result into the current investigation evidence.

Use the existing GUI architecture and visual conventions.

Do not create another workspace.

### Verification statuses

Distinguish:

- Byte-identical.
- Visually verified.
- Analyst-associated.
- Ambiguous/unresolved.
- Rejected or mismatched.
- Unavailable due to retrieval or verification failure.

Manual analyst assertions must not acquire automated-verification status.

If the analyst selects an ambiguous candidate, retain the manual nature of that association.

Do not silently override an explicit analyst rejection.

Provide a reviewable way to replace, invalidate or rerun verification after a source URL changes.

## 10. Evidence persistence and chain of custody

Preserve a durable verification record linked to:

- The investigation.
- The local image SHA-256.
- The exact OSINT source record.
- The compared external asset.
- The verification method and implementation version.
- The resulting association status.
- The evidence revision.

The system must be able to explain:

**What was downloaded, from where, when, what was compared and why the association was accepted or rejected.**

### Retrieved asset retention

Use Task G's storage layout.

Choose a bounded, deterministic location for verification evidence.

Avoid the previous excessive nesting and long filename problems.

Retain enough evidence for later inspection and reproducibility.

Prefer preserving the exact downloaded bytes for a successful verification when appropriate, with SHA-256 verification on reopen.

Do not persist:

- Unlimited network caches.
- Redundant source copies.
- Arbitrary downloaded HTML.
- Sensitive response headers.
- Cookies or credentials.

Store only necessary source and verification metadata.

Keep verification artifacts separate from the immutable forensic detector outputs.

### Failed retrievals

A failed attempt may be logged, but must not be silently represented as positive association evidence.

No incomplete download may be mistaken for an accepted source image.

## 11. Integrate with Task H

Task H already supports:

```text
unestablished
analyst_associated
visually_verified
byte_identical
rejected
```

Inspect and reuse its actual canonical association model.

Do not add a second, incompatible identity system.

A successful verification should provide the structured evidence required to promote the external association.

### Expected synthesis behavior

If the source image is byte-identical or reproducibly visually verified, and its reviewed external creation claim is compatible with the embedded workflow, the canonical investigation synthesis should report image-specific corroboration.

For the Stable Diffusion reference:

```text
Embedded declaration:
    full_image_generation

External declaration:
    full_image_generation

Process agreement:
    compatible

Model family:
    compatible

Source-image identity:
    byte_identical
    OR visually_verified
    depending on the actual comparison

Corroboration:
    corroborated_declaration

Source independence:
    not_established

Technical provenance:
    unverified

Separate editing operation:
    not_established
```

Only report a verified status if its actual requirements are satisfied.

### Important implementation constraint

Task H currently reserves automated verification levels because it has no trusted verifier.

Task I should supply that missing verifier through a clear, bounded interface.

Do not promote a string field such as `image_association="byte_identical"` merely because a caller submitted it.

The synthesis must require valid verification evidence bound to the correct local image and external asset.

Unsupported or stale assertions remain unestablished.

## 12. Source dependence and causal reasoning

Do not conflate source-image identity with independent confirmation.

A creator may:

1. Generate an image.
2. Embed the ComfyUI workflow.
3. Upload that image to Reddit.
4. Describe the image-generation process in the post.

A verified image association connects these records to the same asset.

However, the workflow declaration and Reddit account may both originate from the same creator.

Therefore:

- Their creation-process claims may be mutually consistent.
- The image may be independently verified as the published asset.
- Source independence may remain unestablished.
- The workflow's actual execution may remain unauthenticated.

The investigation synthesis must preserve all four distinctions.

Do not count two creator-controlled declarations as two statistically independent confirmations.

## 13. Source changes and stale verification

Verification results must not remain valid when their underlying identity changes.

Invalidate or appropriately supersede a result when:

- The local image hash changes.
- The selected OSINT source-image URL changes.
- A different source candidate is selected.
- Verification evidence is missing or corrupted.
- A previously accepted association is explicitly rejected.
- The stored verifier result cannot be authenticated against the local verification record.

A changed source page alone should not automatically invalidate a verified historical asset record; distinguish the publication page from the exact retrieved asset.

Historical evidence must retain the URLs and hashes actually used at the time.

Do not silently reinterpret old verification records using newly retrieved bytes.

## 14. Investigation revisions

Preserve Task D/H lifecycle semantics.

Source verification is an evidence update, not a forensic rerun.

When a verified association is accepted:

- Persist the verification evidence.
- Update the relevant source association.
- Recompute the canonical investigation synthesis.
- Publish a new investigation revision when the evidence materially changes.
- Leave the forensic detector snapshot unchanged.
- Preserve previous report revisions.

When an association is removed or rejected, recompute the current synthesis accordingly.

Reopening historical reports must reproduce their original evidence and conclusions, subject to clearly reported missing artifacts.

Do not overwrite immutable report history.

## 15. GUI and reports

Update only existing appropriate surfaces.

### OSINT review

Show the verification action, status and limitations.

### Evidence / Source relationships

Present:

- Local image.
- Compared source image.
- Exact or visual match status.
- Verification method.
- Source URL.
- Evidence relationship.
- Creator claim agreement.
- Dependence qualification.

### Provenance

Separate:

- Source-image verification.
- Technical metadata authenticity.
- Creator attribution.
- Source independence.

### Overview

If a verified source association materially strengthens the investigation, communicate the new corroboration in the canonical investigation conclusion.

Do not replace the frozen forensic findings.

### Reports

Include a concise, auditable verification record with source references, hashes, comparison method, match status and limitations.

Ensure the final report does not ambiguously use `image_association="matched"` to mean both local annotation binding and verified external source identity.

Use explicit labels or descriptions for these distinct relationships.

No duplicate verdict engine.

## 16. Test discipline

Follow `doc/test_quality/TEST_DISCIPLINE.md` and the behavioral ownership matrix.

Starting baseline:

**530 passed.**

Target minimal test growth, ideally no more than **four additional collected cases**.

First inspect and extend existing tests.

Required behavioral coverage:

### A. Byte-identical retrieval

A controlled local HTTP fixture serves the same image bytes.

Expected:

- Identical SHA-256.
- Correct source-image association.
- Reproducible verification evidence.
- New synthesis revision.
- Frozen forensic scores unchanged.

### B. Transformed image

A controlled source serves a resized/recompressed copy.

Expected:

- Different file hash.
- Visual match where warranted.
- Correct visual-verification status.
- Explicit distinction from byte identity.

### C. False match and unsafe retrieval

Use existing fixtures where possible.

Expected:

- Different but visually related images are not accepted as verified.
- Unsupported schemes, private-network targets and unsafe redirects are rejected.
- Failed retrieval does not become a mismatch verdict.
- No uncontrolled network or file-system access.

### D. Persistence and stale identity

Expected:

- Verified evidence survives save/reopen.
- A URL or image-identity change invalidates the relevant current verification.
- Historical investigation reports remain immutable.
- No detector rerun occurs.

These are behavioral requirements, not instructions to introduce four large test modules.

Use mocked or local controlled HTTP transport only in tests.

Tests must not depend on live Reddit availability, external network state or DNS.

Security tests should not bind a real open network listener unless the repository's established test infrastructure safely supports it.

Avoid new heavyweight dependencies.

Run focused tests throughout implementation.

Run the full suite once at the final validation gate.

Report test-count reconciliation.

## 17. Reference validation

### Stable Diffusion / Reddit

Attempt a bounded manual verification using the real source only when accessible and appropriate.

Record:

- Requested URL.
- Final retrieved asset URL.
- Actual media type.
- Retrieved SHA-256.
- Local SHA-256.
- Byte comparison result.
- Visual comparison result, if needed.
- Final association status.

If Reddit blocks retrieval or serves an inaccessible asset, record that as a limitation.

Do not circumvent the restriction or fabricate a successful match.

The deterministic offline acceptance tests remain authoritative for implementation correctness.

### Midjourney

Use the previous Midjourney reference and its source-image URL.

Verify that a transformed source image can be associated when adequately supported.

Preserve the existing source-authorship and provenance limitations.

### Conventional photograph

Verify that a misleading external image or broadly similar image cannot manufacture synthetic-origin corroboration.

Ensure the photo's frozen forensic measurements remain unchanged.

## 18. Explicit exclusions

Do not implement:

- General-purpose reverse-image search.
- Search-engine scraping.
- Browser automation.
- Reddit authentication.
- Recursive website crawling.
- Unbounded candidate discovery.
- Facial-recognition-based identity matching.
- New generative-AI detectors.
- Detector retuning.
- Scorecard or confidence-policy changes.
- Hypothesis-precedence changes.
- A new evidence database.
- A redesigned investigation workspace.
- Cryptographic C2PA validator infrastructure.
- Automatic source-authorship authentication.
- Release packaging.
- PyInstaller builds.
- Network access during ordinary investigation loading.

Any extra dependency or major architectural change requires explicit justification in the audit report.

## 19. Deliverables

Create:

`doc/reasoning_audit/origin_processing/task_i_source_image_verification.md`

Include:

1. Existing source-verification capability audit.
2. Retrieval design and security controls.
3. Exact-byte matching method.
4. Visual matching method and limitations.
5. Verification result contract.
6. Integration with Task H association states.
7. OSINT GUI changes.
8. Evidence persistence and Task G path compatibility.
9. Investigation revision behavior.
10. Stable Diffusion reference validation.
11. Midjourney and conventional-photo regression results.
12. Security and false-match tests.
13. Full suite results and test-count delta.
14. Changed-file inventory and Git status.
15. Remaining verification limitations.

Avoid unnecessary additional documentation or duplicated test fixtures.

## 20. Acceptance criteria

Task I is complete when:

- A user can initiate verification from the existing OSINT interface.
- SignalLens can safely retrieve a supported source image.
- An HTML page is not mistaken for an image.
- Multiple-source-image ambiguity is handled explicitly.
- Byte-identical verification uses actual downloaded bytes and SHA-256 equality.
- Transformed copies can be recognized by a defensible visual matcher.
- Similar but different images are not automatically verified.
- The match method and evidence are preserved.
- Failed or unavailable retrieval cannot be misrepresented as a mismatch.
- Private-network access and unsafe redirects are blocked.
- Network operations do not freeze the GUI.
- Verification integrates with Task H's existing source-image association model.
- Automated verification cannot be forged using an unsupported status string.
- Verified associations influence the canonical investigation synthesis.
- Source dependence and metadata authenticity remain separate.
- The correct local SHA-256 remains bound throughout the workflow.
- Source URL changes and stale evidence are handled safely.
- Investigation synthesis revisions update without forensic detector reruns.
- Historical reports remain immutable.
- Task G storage and legacy loading remain compatible.
- Existing tests pass with minimal justified growth.
- Nothing is staged, committed, pushed, tagged or published.

## 21. Final Codex response

Report:

**1. Root cause:** What prevented automated source-image association previously.

**2. Retrieval:** Source selection, URL handling and security.

**3. Matching:** Exact byte identity and visual verification.

**4. Evidence model:** Hashes, association statuses and verification records.

**5. Integration:** Task H corroboration and investigation revisions.

**6. GUI:** User actions and result presentation.

**7. Reference cases:** Stable Diffusion, Midjourney and conventional photography.

**8. Validation:** Focused tests, full suite and test-count accounting.

**9. Git:** Modified files and confirmation of no staging/commits.

**10. Limitations:** What remains unverifiable.

**11. Status:** Complete / Conditional / Blocked.

### Guiding principle

**Verify the relationship between the source image and the investigated image before allowing external creation claims to provide image-specific corroboration.**

File identity, visual identity, creator attribution, creation-process agreement and technical provenance authenticity are distinct evidential questions.

SignalLens must preserve those distinctions while allowing verified source-image relationships to contribute meaningfully to its investigation conclusions.