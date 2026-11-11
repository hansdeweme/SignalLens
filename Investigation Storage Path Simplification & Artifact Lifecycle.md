# Codex Task G — SignalLens: Investigation Storage Path Simplification & Artifact Lifecycle

**Repository:** `D:\Coding\SignalLens`  
**Target release:** `0.1.0-beta.1`  
**Priority:** High — pre-release storage compatibility  
**Task type:** Storage audit followed by bounded implementation  
**Scope:** Investigation directory layout, artifact naming, persistence, restoration and report revisions  
**Git:** Do not stage, commit, push, tag or publish.

## 1. Mission

Simplify the physical storage layout under `.\analyzed\` while retaining the forensic integrity and lifecycle capabilities established in Tasks D, E and F.

The current layout uses a recognizable image filename followed by multiple opaque identifier directories, repeated full-length filenames and deeply nested report revisions.

This creates unnecessary navigation complexity and excessively long Windows paths.

Implement a more understandable, compact directory structure in which:

1. The original image name is immediately recognizable.
2. Technical identifiers remain stable and unambiguous.
3. Multiple analyses of the same image remain distinguishable.
4. OSINT evidence remains associated with the correct image.
5. Frozen forensic results remain immutable.
6. Report revisions remain reproducible.
7. Existing saved investigations remain accessible.
8. Intermediate artifacts are retained only when justified by actual consumers or reproducibility requirements.

**The objective is to simplify storage without weakening evidence integrity or breaking existing workflows.**

## 2. Mandatory preparation

Read:

- `AGENTS.md`
- `doc/test_quality/TEST_DISCIPLINE.md`
- `doc/reasoning_audit/origin_processing/task_d_implementation.md`
- `doc/reasoning_audit/origin_processing/task_e_corroboration_gate.md`
- `doc/reasoning_audit/origin_processing/task_f_signal_semantics.md`

Inspect the current working tree and preserve unrelated or inherited changes.

Investigate the implementation of:

- Image identity and hashing.
- Investigation/session identifiers.
- Analysis-run identifiers.
- Output-directory creation.
- OSINT persistence.
- Evidence and artifact manifests.
- Investigation restoration.
- Report generation and export.
- Report revision snapshots.
- GUI artifact loading.
- Cleanup and temporary-file handling.
- Any existing storage-format versioning.

Do not assume the current directory structure is accidental. Establish why each layer exists before modifying it.

## 3. Current reference layout

The fresh Midjourney analysis produces a structure equivalent to:

```text
analyzed/
└── high-quality, realistic fashion portrait of a young woman .../
    └── 3162fff16c3e438b8a8302a77906ff7b/
        ├── osint_results.json
        └── ce576b6ed5c74e02a6539e562118dbc5/
            ├── analysis_run.json
            ├── current_report.json
            ├── fft_results.json
            ├── [numerous detector outputs]
            ├── logs/
            ├── prepared_images/
            ├── report_revisions/
            │   └── ce576b6e...-a2-8b1f.../
            │       ├── osint_results.json
            │       └── summary/
            │           ├── final_summary.html
            │           ├── final_summary.json
            │           ├── final_summary.txt
            │           ├── reasoning_trace.json
            │           └── reasoning_trace.txt
            └── ui_artifacts_v1.json
```

The full original filename is repeated in many detector artifact names.

Some listed paths extend far beyond traditional Windows path-length limits.

The clean listing shows one apparent investigation, one analysis run and one report revision, although the exact identifier semantics must be verified against production code.

## 4. Mandatory audit — Identify the existing storage contracts

Before implementing changes, determine the actual meaning of every directory layer.

Investigate:

| Existing layer | Questions |
|---|---|
| Image-name folder | Is it derived from the original basename? How are collisions handled? |
| First identifier | Image identity, investigation ID, session ID or another concept? |
| Second identifier | Analysis run ID or different lifecycle identifier? |
| Report revision identifier | How does it associate a revision with its frozen forensic run? |
| `osint_results.json` | Is it mutable current evidence or a historical snapshot? |
| `current_report.json` | Pointer, cached summary or authoritative report state? |
| `ui_artifacts_v1.json` | Which paths are referenced and persisted? |
| `prepared_images/` | Permanent evidence, reusable intermediate artifacts or temporary files? |
| Detector-specific outputs | Required by the GUI, report generation or forensic reproducibility? |

Trace the code that writes, discovers, loads and deletes each relevant artifact.

Identify any assumptions about directory depth, filename patterns or parent directory relationships.

Document the authoritative source of truth for image identity, run identity and revision identity.

**Do not modify the physical storage layout before completing this audit.**

## 5. Target directory architecture

Use the following as the preferred logical layout:

```text
analyzed/
└── recognizable-image-name/
    ├── manifest.json
    ├── osint_results.json
    ├── runs/
    │   ├── run_001/
    │   │   ├── analysis_run.json
    │   │   ├── current_report.json
    │   │   ├── evidence/
    │   │   │   ├── ela.png
    │   │   │   ├── fft_spectrum.png
    │   │   │   ├── boundary_overlay.png
    │   │   │   └── ...
    │   │   ├── prepared_images/
    │   │   └── logs/
    │   └── run_002/
    └── reports/
        ├── latest.json
        └── revisions/
            ├── rev_001/
            │   ├── final_summary.html
            │   ├── final_summary.json
            │   ├── reasoning_trace.json
            │   └── osint_results.json
            └── rev_002/
```

This is a target design, not a mandatory schema.

Adapt it to existing canonical models where needed.

Avoid introducing more layers than necessary.

The design must preserve the distinction between:

- Image identity.
- Investigation identity, if distinct.
- Analysis-run identity.
- Mutable current OSINT evidence.
- Immutable forensic snapshot.
- Immutable investigation/report revision.

If multiple independent investigations of the same image are supported, preserve that capability explicitly rather than merging distinct investigations accidentally.

## 6. Human-readable top-level folder

**Non-negotiable UX requirement: The highest-level directory beneath `analyzed/` must identify the image by its recognizable original filename.**

Do not replace this directory with an opaque UUID or SHA-256 hash.

Use the original filename stem, with minimal normalization necessary for filesystem safety.

Requirements:

- Preserve recognizable wording.
- Remove or replace invalid Windows filename characters.
- Handle reserved names.
- Handle trailing spaces or periods.
- Apply a reasonable length limit.
- Avoid accidental directory collisions.
- Preserve the complete original filename in metadata.
- Never rely on the folder name as cryptographic image identity.

Where two different images have the same recognizable name, use a stable short identifier suffix.

For example:

```text
analyzed/
├── fashion-portrait/
├── fashion-portrait--b5548eb0/
└── fashion-portrait--f21a906c/
```

Use full SHA-256 internally and validate any shortened identifier for collisions.

Where the same image content is analyzed repeatedly, preserve image identity without creating unnecessary duplicate top-level folders.

Do not silently merge separate user investigations if the current architecture treats them as distinct.

## 7. Shorten artifact filenames

The current layout repeats the complete original filename throughout the run output.

Within a directory already associated with a particular image, that is unnecessary.

Prefer concise descriptive names:

```text
ela.png
ela_overlay.png
noise_residual.png
fft_spectrum.png
patch_similarity.png
subject_boundary.png
```

Use meaningful namespace prefixes or subdirectories where required to prevent collisions.

Do not discard information that distinguishes:

- Global versus regional analysis.
- Subject versus background.
- Detector-specific output types.
- Different processing stages.
- Alternative resolutions or variants.

The artifact manifest must continue to identify the correct file for every GUI visualization.

Avoid duplicate copies of the same diagnostic image unless necessary.

## 8. Windows path-length robustness

Audit the maximum path lengths generated by the new layout.

Use actual generated Windows paths, including the repository root and representative longer installation/output locations.

The new format should aim to remain comfortably below traditional Windows path limits under ordinary installation conditions.

Do not solve the problem by relying exclusively on Windows long-path support.

Check:

- Standard desktop execution.
- Packaged Windows execution.
- Unicode filenames.
- Long original filenames.
- Duplicate names.
- Case-insensitive collisions.
- Reserved Windows names.
- Path traversal and unsafe separators.

Do not hardcode assumptions about the user's repository location.

## 9. Analysis-run history

Preserve the ability to analyze the same image more than once.

A new forensic analysis should create a distinct run where that is the established lifecycle behavior.

Do not overwrite frozen forensic results.

Prefer short stable run-directory identifiers, optionally combined with human-readable timestamps.

If chronological numbering is used, ensure concurrent runs cannot collide.

The manifest must retain the actual stable run ID regardless of its directory presentation.

Distinguish:

- Rerunning forensic detectors.
- Refreshing investigation synthesis.
- Adding new OSINT evidence.
- Exporting another report.

Only the first operation should require a new forensic run.

Preserve Task D's lifecycle behavior.

## 10. OSINT persistence

OSINT evidence must remain associated with the correct image identity.

Verify that:

- Current OSINT evidence can be revised independently of forensic runs.
- Adding OSINT does not rerun detectors.
- A report revision captures the exact OSINT evidence used.
- Historical revisions remain unchanged after later OSINT updates.
- Evidence from one image cannot leak into another image's investigation.
- Saved OSINT is restored correctly when reopening an investigation.

Avoid redundant copies unless needed to preserve an immutable revision.

If shared current OSINT is stored once, historical report snapshots must still preserve their source-evidence state.

## 11. Report revision history

Preserve all supported report formats and investigation revision semantics.

Requirements:

- Existing revision identifiers remain stable.
- Reports retain their forensic snapshot association.
- A new OSINT revision does not modify an earlier report.
- Historical reports remain readable.
- The current report can be found without navigating several opaque directories.
- GUI and exported reports resolve the same revision.
- Report exports continue working from restored investigations.

Consider a lightweight `latest.json` pointer or manifest entry.

If a convenience file such as `latest_report.html` is useful, it must not become a second authoritative report state.

The immutable revision remains the source of truth.

## 12. Intermediate artifacts and cleanup

Investigate the large number of outputs named:

```text
*_tmp.png
*_tmp_fft_*.png
*_mask.png
*_preview.png
```

Determine which are:

1. Required forensic evidence.
2. Required GUI visualizations.
3. Needed for reproducibility.
4. Used by later pipeline stages.
5. Purely temporary computational inputs.
6. Diagnostic/debug outputs.

Implement conservative cleanup only where safety is demonstrated.

Do not delete a file merely because its name contains `tmp`.

For required intermediates, preserve them or regenerate them deterministically where supported.

If a retention distinction already exists, reuse it.

Do not introduce a complex cache-management subsystem.

Cleanup must never break a historical report or an existing artifact reference.

## 13. Backward compatibility

Existing saved investigations must remain accessible.

Implement a compatibility strategy for the old storage layout.

Prefer:

- New analyses use the new layout.
- Existing analyses remain readable in their original locations.
- Historical evidence is not silently rewritten.
- Existing report revisions remain immutable.

Do not perform automatic destructive migration.

Do not move, rename or delete the user's existing `analyzed/` history during normal application startup.

If a migration facility is genuinely needed, document the rationale and obtain authorization before implementing destructive behavior.

Ensure that the application can distinguish legacy storage from the new format.

Use a storage-format version or existing manifest/version mechanism where appropriate.

Avoid breaking `ui_artifacts_v1.json` or saved report references.

## 14. Failure and recovery behavior

Evaluate the implications of:

- Interrupted forensic analyses.
- Partial artifact creation.
- Failed report export.
- OSINT revision failure.
- Concurrent analysis runs.
- Reopening a partially completed investigation.
- Interrupted writes to manifests or current-report pointers.

Use existing atomic-write or recovery mechanisms where available.

A failed write must not replace a valid historical revision.

Avoid creating orphaned directories when failure recovery can be handled simply.

Do not expand this task into a general transaction-management redesign.

## 15. Testing discipline

Read and follow `doc/test_quality/TEST_DISCIPLINE.md`.

**Target zero new collected tests where existing tests can be extended. Maximum two additional collected tests without explicit justification.**

The existing suite baseline is **525 passed**.

Inspect current tests for:

- Output-directory construction.
- Image identity.
- Multiple analysis runs.
- Saved-investigation restoration.
- OSINT persistence.
- Report revisions.
- Artifact manifests.
- Legacy path compatibility.

Prioritize meaningful coverage of:

**A. New layout and naming**

A long image filename produces a recognizable, collision-safe top-level directory and shorter artifact paths.

**B. Compatibility and lifecycle**

A saved legacy investigation remains readable, while a new investigation preserves distinct forensic runs, OSINT updates and immutable report revisions.

These are behavioral objectives, not instructions to create two separate tests.

Prefer extending existing integration tests.

Avoid:

- New test modules for each naming edge case.
- Redundant filesystem mocks.
- Broad fixture duplication.
- Mass golden-file regeneration.
- Artificial test proliferation.

Run focused tests during development.

Run the complete existing suite after implementation.

Report collected test counts and the net change.

## 16. Manual validation

Use the existing Midjourney reference image.

After generating a fresh analysis in a controlled temporary output location:

1. Inspect the top-level folder name.
2. Inspect the nesting depth.
3. Inspect the longest generated path.
4. Verify artifact discovery from the GUI.
5. Verify current and historical reports.
6. Add or revise OSINT evidence.
7. Confirm no forensic rerun occurs.
8. Verify that the prior report revision remains unchanged.
9. Reopen the saved investigation.
10. Confirm consistent reasoning and evidence displays.

Also validate a short-name conventional photograph.

Where practical, compare the legacy and new layouts using equivalent analysis inputs.

Do not delete or modify the existing user investigation directory to run this test.

## 17. Required deliverable

Create:

`doc/reasoning_audit/origin_processing/task_g_storage_layout.md`

The document must include:

### A. Storage architecture findings

Map every original directory layer to its actual identifier semantics.

### B. Root causes of path complexity

Explain the sources of depth, repeated filenames and unnecessary retained artifacts.

### C. Chosen target layout

Provide an example tree based on the implemented design.

### D. Compatibility strategy

Describe how legacy investigations remain readable.

### E. Artifact lifecycle

Identify which artifacts are permanent, temporary or diagnostic, and what cleanup was authorized.

### F. Before/after measurements

Report:

- Folder nesting depth.
- Longest generated path.
- File count.
- Directory count.
- Total output size, where measurable.
- Any intentionally retained duplicate artifacts.

Include the measurement scope and ensure the comparison is like-for-like.

### G. Regression results

Report the focused tests and full-suite results.

### H. Git status

List modified files and confirm unrelated changes were preserved.

Do not create additional documentation files unless essential.

## 18. Acceptance criteria

Task G is complete when:

- The highest-level folder under `analyzed/` is recognizable by image name.
- Naming is safe and collision-resistant.
- Image identity continues to rely on full SHA-256, not filenames.
- Directory depth and maximum path lengths are materially reduced.
- Artifact filenames no longer repeat unnecessary full image names.
- Multiple forensic runs remain distinguishable.
- OSINT persists independently of forensic runs.
- Immutable report revisions remain preserved.
- GUI artifact references continue to resolve correctly.
- Existing saved investigations remain readable.
- Historical investigations are not silently migrated or modified.
- Intermediate cleanup is conservative and justified.
- Current forensic scores and reasoning policies are unchanged.
- The full existing test suite passes.
- Test growth remains minimal.
- Unrelated work is preserved.
- Nothing is staged, committed, pushed, tagged or published.

## 19. Final Codex response

Return:

**1. Root cause:** Why the original layout became deeply nested.

**2. Identifier mapping:** What each original UUID represented.

**3. New layout:** Show the implemented directory tree.

**4. Path improvements:** Before/after depth and longest path.

**5. Artifact retention:** What remains, what is cleaned and why.

**6. Compatibility:** Legacy loading, image identity and report revisions.

**7. Validation:** Midjourney, conventional photograph, focused tests and full suite.

**8. Test discipline:** Previous, added, removed and net test counts.

**9. Git:** Modified files and confirmation of no staging or commits.

**10. Release status:** Complete / Conditional / Blocked.

**Guiding principle: Organize files for human navigation, identify evidence cryptographically, and preserve forensic history independently of the physical directory layout.**