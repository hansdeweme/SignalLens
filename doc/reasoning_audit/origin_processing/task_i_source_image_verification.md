# Task I — source-image retrieval and verification

2026-11-11 (Europe/Amsterdam). Implementation on inherited `main`, HEAD
`6fbc2f930c0ac583bf6e27f4cfd8dc58bfc7c216`. No staging, commits, push, tags,
publication, builds or detector reruns. Existing work was preserved.

## Existing capability audit and cause

Read AGENTS.md, the test discipline and behavioral ownership matrix, and the
Task D, G and H implementation reports. Inspected OSINT dataclasses, add/edit
and review dialogs, SHA-256 identity, session/revision ownership, relationship
assessment, investigation synthesis, source/provenance surfaces, report
restoration and serializers. Task C's in-memory source comparison was an audit
experiment, not a reusable application verifier. The patch-similarity detector
measures internal spatial reuse, not external image identity; it was not changed.

Task H already separated claims, manual association, dependence and technical
authenticity. It deliberately rejected automated labels because no trusted
retrieval/comparison evidence existed. This implementation supplies that missing
boundary and uses the existing OSINT commit and report pipeline.

## Retrieval and security

`source_image_verification.py` uses the standard HTTP/socket/TLS libraries and
existing Pillow, NumPy and OpenCV dependencies. No new dependency or service.

* Retrieval requires the explicit **Verify source image** action on a selected
  saved OSINT finding. Ordinary loading never makes an HTTP request.
* Prefer the recorded image URL; otherwise use the page URL. Thumbnails are not
  silently substituted. A lightbox fragment is removed from the HTTP request,
  but never makes HTML an image. Requested and resolved URLs remain recorded.
* Only credential-free HTTP(S), ports 80/443. Resolve DNS with a five-second
  bound; reject non-public, reserved or multicast results, including a mixed
  public/private answer. Connect the socket directly to a validated numeric IP,
  check its peer, and use the original hostname for TLS SNI/certificate checking.
  TLS verification remains enabled. No second hostname resolution at connect.
* Every redirect repeats URL/DNS/connection checks. Maximum three redirects.
  No proxy environment, cookies, netrc, ambient credentials, retries, browser,
  script execution, login impersonation or provider scraping.
* Five-second socket operations, 30-second aggregate retrieval deadline, and a
  socket shutdown timer to stop slow header/body transfers. DNS work uses a
  bounded daemon lookup; a timed-out lookup cannot publish an image result.
* Maximum 20 MiB per response, four compared candidates, first 1 MiB of HTML
  discovery, 24 million decoded pixels, maximum dimension 12,000, one frame.
  HTTP content encoding is not expanded. Check length/truncation, image decoding
  and Pillow bomb warnings; URL extensions and Content-Type alone are not proof.
* HTML discovery is one level of explicit `og:image`, `twitter:image`, `img src`
  and direct image links. No recursive discovery. Candidate URLs/results stay
  separate; one match never verifies the other images in a publication.

Statuses distinguish download failure, unsupported response, image-decode
failure, comparison failure and completed verification. A failed download
retains `unestablished`, never a mismatch. Unsupported page layouts, inaccessible
assets and exhausted candidate limits remain limitations. The first four
discoverable references may omit the desired image; a direct URL is then needed.

## Comparison contract

Exact comparison hashes the actual downloaded bytes and the selected local file.
The local file must still match the canonical analyzed SHA-256. SHA equality
establishes `byte_identical`, after validating the downloaded image.

For unequal hashes, `aligned-tiles-orb-v1` performs conservative full-frame visual
comparison. Orient decoded RGB images, require dimensions of at least 128 and
aspect agreement within 1.5%, then normalize to a bounded comparison grid.
Acceptance requires all of:

| Measurement | Threshold |
|---|---:|
| Mean RGB absolute error, normalized by 255 | ≤ 0.035 |
| Worst mean error over a 4×4 tile grid | ≤ 0.065 |
| Mutual ORB features, Hamming distance ≤32 and displacement ≤3 normalized pixels | ≥60 |
| Occupied feature-match grid cells | ≥8 of 16 |
| Coverage of local feature-bearing cells | ≥85% |
| Spatial quadrants containing matches | all four |
| Aligned fraction of mutual features | ≥65% |

This combines normalized pixels, local agreement and distributed geometric
correspondence; no perceptual hash alone or facial identification is used. The
thresholds are conservative engineering criteria, not calibrated probabilities.
The feature-bearing-cell criterion avoids requiring artificial detail in blank
image margins; it still requires spread over the complete frame. Thresholds were
checked against deterministic textured fixtures, their JPEG/WebP transforms,
changed-central-subject controls, and three existing image references rather
than fitted solely to the Reddit example.

Insufficient detail, small images, crops, aspect changes or weak support remain
`ambiguous`. A large whole-frame difference (mean error >0.20 and fewer than eight
aligned features, after aspect eligibility) rejects full-frame correspondence.
Cropping/rotation/perspective recovery is intentionally unsupported in this
version. No claim of exhaustive false-match calibration is made, especially for
subtle local edits or adversarial near-duplicates. Visually verified means strong
whole-image correspondence, not pixel equality or authenticated history.

## Evidence, storage and integrity

Each successful result records implementation version, source-record UUID,
local/source SHA-256, selected page/image URL, requested/final asset URL, UTC
retrieval timestamp, response media type/size, association, comparison method,
measurements, thresholds and limitations. A process-local issuance MAC prevents
callers from fabricating an accepted result by changing its status, metrics or
source selection before retention.

On acceptance, retain under Task G's investigation directory:

```text
inv_001/
  verification/
    .receipt-key
    <source-sha256>.image
    <receipt-sha256>.json
```

The exact downloaded bytes are content-addressed and reused. Immutable receipts
are bound to the source record, asset selection, original investigation and
evidence revision, with a local HMAC. Creation is exclusive and flushed/fsynced;
failed writes remove only their own incomplete file. Existing artifacts are
never overwritten. The directory is capped at 256 files / 256 MiB. No HTML,
cookies, sensitive headers or unlimited cache is retained. Detector outputs and
original local images remain untouched. Failed/unaccepted attempts need not be
persisted and never supply association evidence.

OSINT stores only the receipt reference; synthesis revalidates its digest, local
MAC, binding and retained asset SHA-256. Missing/corrupt evidence, another local
hash, another source-record ID, changed image URL or explicit rejection removes
automated support. The selected page can change without rewriting the historical
downloaded-asset record. Re-running verification produces another immutable
receipt. Changing an image URL or explicitly rejecting it clears the current
reference; old report evidence remains historical.

Local receipt integrity is **not** publisher authentication and is not a defense
against an attacker who controls the application's local files and signing key.
Absolute artifact locations follow existing Task G restoration semantics. A
standalone report moved without its receipts/assets/key cannot retain automated
verification; the missing evidence is reported. No portable evidence bundle or
key recovery service was introduced.

## Task H, revisions and presentation

No new verdict engine. Task H consumes validated receipt results as
`byte_identical`, `visually_verified`, `rejected`, or unresolved evidence. Manual
assertions remain manual; accepting an ambiguous candidate records
`analyst_associated` with the explicit analyst visual-check basis. A prior
explicit analyst rejection blocks acceptance until the analyst edits it.

Compatible reviewed declarations plus established association can produce
`corroborated_declaration`. Independence stays `not_established`, metadata and
authorship remain unverified, exact workflow versions are not inferred, and
frozen detector findings/tiers/scores remain unchanged. An additional existing
path was corrected: an unassociated AI-gallery category no longer supplies an
image-specific origin heading or origin-support reference. Its source context
and claims remain visible for review.

Policy v3 retains separate `local_record_binding` and
`source_image_associations`; the former `matched` container label no longer
ambiguously means external identity. The pure synthesis receives already
validated evidence from the session. Receipt health participates in the
synthesis cache/revision key; corruption invalidates current report status even
without an annotation edit. Acceptance uses the existing annotation commit,
new synthesis revision and immutable report publisher, never a detector rerun.
Restoration recomputes validity; historical report files are not rewritten.

The existing OSINT panel gains **Verify source image**. Its modal review uses
the existing owned `InvestigationWorkers`/QThread lifecycle, queued GUI delivery,
progress and cooperative cancellation. It shows individual candidate outcomes,
local/source previews, measurements and limitations before acceptance. Cancellation
waits for bounded worker retirement, discards the result and writes no evidence.
Session/revision/hash checks reject stale completion. Dialog data is released
after closing. Source relationships, Provenance, Overview and existing TXT/HTML/
JSON report rendering all consume the canonical qualified result. No workspace
or separate report interpretation was added.

## Live and saved reference validation

Controlled validation outputs are in `.i_task_i/reference_results.json` and the
per-reference isolated report directories. The existing user's investigations
were read only. The originally named Stable Diffusion report was absent, so the
recorded Task H **unchanged-annotations** checkpoint was explicitly reused; its
source identity and frozen scorecard match the reference. No detector pipeline
was rerun. A first reference harness assertion exposed the unassociated
AI-gallery heading described above; validation was repeated after correcting it.

### Stable Diffusion / Reddit

Requested and final asset URL (no redirect):

`https://preview.redd.it/the-greatest-amateur-photo-realism-i-have-ever-achieved-v0-0c8djb2b8xyg1.png?width=1024&format=png&auto=webp&s=61f9666b438865da67fcb76a93f8d6bd3168a22b`

Source publication:
`https://www.reddit.com/r/StableDiffusion/comments/1t2kyjt/the_greatest_amateur_photo_realism_i_have_ever/`

* Actual response: `image/png`, 341,092 bytes, 1024×1024.
* Local SHA-256: `b4f305f65537010b4d2926b41e4ec092889ea0a1607075323da10f02dbf8ac5e`.
* Downloaded SHA-256: `022d3d0507be1a74ea1b4401c0dd6ce83f498ec6a524ae68fb941a7c91107ef6`.
* Bytes differ. Visual result: **visually_verified**; mean error 0.00245,
  worst tile 0.00338, 1,428 aligned features, 15 cells, all four quadrants,
  aligned fraction 0.9965.
* Reviewed generation declarations become `corroborated_declaration` in the
  isolated accepted-evidence report. Embedded v13 versus reported v14 remains
  explicit; model-family agreement does not establish exact workflow agreement.
* Frozen suspicious score remains **24.3401**; technical provenance remains
  unverified and separate edit remains unestablished.

This verifies the supplied preview asset against the local image. It does not
claim the preview is the original PNG or independently prove that every image
in the linked publication is the same asset. No authenticated publication-page
ownership/creator claim is inferred. An original-byte Reddit asset was not
established and is not required to accept this transformed correspondence.

### Midjourney

Requested/final URL:
`https://embracepresets.com/wp-content/uploads/2024/08/theart1300_httpss.mj_.runhx-xd-s5Gos_real_photo_-chaos_10_-a_33717b8b-eb01-4bd6-8719-f4b4c9d59fa8_3.png`

Actual response `image/png`, 1,958,740 bytes. Downloaded and local SHA-256 both
`b5548eb02f4a3841d0f89a3542fc743d48edfcb93253c5d848bbdd6c089fc7f1`:
**byte_identical**. A separately generated 578×768 JPEG at quality 88 is
**visually_verified**, with unequal file hash, mean error 0.00838 and 1,284
aligned features across all four quadrants. Suspicious score remains **18.04075**.
Publisher/creator attribution and provenance remain unverified.

### Conventional photograph

Nikon local SHA-256:
`aed004440af3abfde913604d0a311418da412ea85c106ff9da83b25428be8b09`.
An explicitly hypothetical generation claim paired with the unrelated Stable
Diffusion image remains **ambiguous/unestablished** (ineligible full-frame
geometry), supplies no generation corroboration, and leaves origin
`not_established`. The photo's own recompressed copy passes visual matching;
matching never itself classifies synthetic origin. Suspicious score stays **7.6**.

All three saved-reference checks preserve frozen JSON/scorecards and earlier
report bytes, create distinct evidence revisions, and reopen with equal current
synthesis. The source reports are also hash-checked unchanged. Live HTTP is not
used by automated regression tests.

## Test ownership and acceptance

Baseline independently collected: **530**. Added **10**, consolidated **0**,
removed **0**; final collection **540**, net **+10**. This exceeds the
task's preferred four-case target because four independent security boundaries,
two image codecs and two real Qt integration boundaries merit separately
diagnosable cases. It stays within the repository's ten-case review threshold;
no unrelated behaviors were merged to hide collection growth.

New coverage lives in existing contract/provenance owner modules, with one small
non-collecting helper for deterministic image bytes and controlled socket/HTTP
responses. No real network listener or DNS is used by tests:

* One retrieval/receipt/revision case covers actual HTTP parsing, pinned peer/SNI,
  exact downloaded hash, rejection of modified issuer results, receipt persistence,
  corruption invalidation and immutable report history.
* Two codec cases cover resized JPEG/WebP acceptance and counterfactual changed
  central content against the same background.
* Four security cases independently cover unsupported scheme, private DNS,
  redirect to private DNS and a peer differing from the checked destination.
* One bounded multi-candidate HTML case distinguishes successful image identity,
  decode failure, download failure and unsupported HTML without blanket matches.
* Two real GUI cases cover off-thread retrieval/accepted OSINT publication and
  cancellation/worker retirement without acceptance.

Extended the existing unsupported-assertion test to protect the unassociated
AI-gallery origin gate and updated the authoritative no-forensic-resynthesis GUI
test's heading expectation. Reused its lifecycle/report assertions, existing
source-hash and stale-dialog protections, generic owned-worker tests, report
failure/legacy import tests, and all scorecard/confidence owners. An initial
synthetic fixture had too little contrast for the deliberately conservative ORB
criterion; the positive fixture was corrected to contain distributed detail,
without lowering the feature requirement.

Focused investigation/provenance/GUI run before the last gate correction:
**71 passed**. Subsequent focused investigation/GUI/Overview run exposed the one
obsolete heading expectation; it was updated to the intended safer behavior.
Final complete command:

`py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q`

Final result: **540 passed in 24.65 seconds; 0 failed, 0 skipped; exit 0**.
One full acceptance run after the final production/test edits. Only audit
documentation and inventory capture followed; the full suite was not repeated.

## Change inventory, Git and limits

New production files: `source_image_verification.py`,
`source_verification_dialog.py`. Modified existing production files:
`osint_reverse_search.py`, `osint_dialogs.py`, `signallens_gui.py`,
`provenance_workspace.py`, `evidence_relationships.py`,
`investigation_synthesis.py`, `investigation_session.py`,
`investigation_reports.py`.

Tests: `tests/test_investigation_contracts.py`,
`tests/test_investigation_gui.py`, `tests/test_provenance_reporting.py`, plus
new helper `tests/source_verification_helpers.py`. This is the sole permanent
Task I audit document. Baseline hashes and changed-file/Git inventory are retained
under `.i_task_i/`. Inherited user documents, detector changes, previous audit
artifacts and inaccessible/deleted historical pytest paths were not repaired or
overwritten. No staging/commit/push/tag/publication occurred.
Final index diff is empty. The changed-file whitespace check reports only the
inherited `signallens_gui.py:95` startup-print trailing spaces, outside Task I's
edits; they were left untouched. Git also emits its existing LF/CRLF notices.

Remaining limits: no crop registration, JS-rendered page discovery, source
authorship or independence authentication, workflow-execution verification,
cryptographic provenance service, portable receipt bundle, population-level
false-match calibration, native/DPI visual acceptance or release packaging.
These are explicit limits; retrieval failures and unsupported visual comparisons
cannot become positive verification.

**Status: Complete** for bounded Task I, with the explicit limitations above.
