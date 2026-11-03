# Bounded reference-score diagnostic

## Verified findings

The supplied comparison mixed **different analysis profiles**. Historical reference traces under doc/final_acceptance_audit record `analysis_mode="subject_based"`; UI-1's reference runner explicitly uses `normal`. The saved patch payloads confirm patch size **16 vs 24** and retained pair counts **500 vs 300**. These are existing configured profile differences, not UI-2 coefficient changes.

|Case|Historical stored summary|Historical sections replayed through current reasoning|UI-1 normal run|UI-2 normal run|
|---|---:|---:|---:|---:|
|Instagram suspicious|20.47705|20.47705|21.32705|21.32705|
|Midjourney suspicious|6.0375|5.4|6.675|6.675|
|Instagram benign|2.25|2.25|2.25|2.25|
|Midjourney benign|1.5|1.5|1.5|1.5|

The quoted historical **5.4** is reproducible from the historical structured measurements with the **current numerical allocation logic**, while the inspected final_acceptance_audit serialized Midjourney summary still contains **6.0375**. Available historical files therefore contain different numerical-allocation snapshots; one cannot treat all saved traces as the same final revision.

## Scope and evidence

Before shell integration, the repository branch/HEAD, settings, UI-1 test suite and saved result traces were inspected. The bounded comparison examined section snapshots and score contribution ledgers, not detector thresholds. A pure call to the existing authoritative synthesis function replayed recorded ModuleSummary values. No reference configuration, image, detector, coefficient, reasoning rule, evidence-lineage rule or confidence rule was changed. Later checks completed the pixel/hash comparisons and verified final normal-profile outcomes.

Evidence files: inherited_baseline.json (entry Git state and hashes), score_diagnostic_data.json (historical/UI-1 sections and ledgers), score_profile_replay.json (profiles, patch configuration, normalized-pixel equality, coverage and replay ledger), reference_verification.json (final full pipeline vs UI-1). Utilities are inspect_baseline.py, complete_score_diagnostic.py and verify_reference_behaviour.py. Do not rerun inspect_baseline.py after edits if preserving the original inventory.

## Configuration and contribution differences

Instagram: patch similarity changes from structured_patch_recurrence to possible_synthetic_texture_repetition; subject-process asymmetry changes from weak to medium, with corresponding regional measurements. Historical base suspicious is **23**, UI-1 normal base is **24**. Other aggregate component values and operations are the same in the inspected comparison; the existing camera attenuation converts the extra base unit into **0.85**, exactly the observed 20.47705 → 21.32705 difference. Small material/spatial measurement differences are recorded, not hidden.

Midjourney: historical patch similarity is medium structured_patch_recurrence (0.6599); normal-profile output is strong possible_clone_reuse (0.9085). The current ledgers record the appropriate existing numerical allocations and clone support. Replaying historical measurements under current deduplication yields 5.4; the normal-profile run yields 6.675. The old saved 6.0375 trace includes pre-allocation restatement credit absent in the current replay. This diagnosis identifies the differing **recorded measurements/profile and ledger treatment**; it is not a new scoring correction or a claim that a suspicious score proves AI generation.

The main hypotheses/tiers are stable: Instagram High localized editing, Midjourney Medium unverified generation declaration. Profile-dependent numerical variation is not a calibration or accuracy study.

## Inputs, normalization, availability and revision limits

All four prepared-image roles for each reference—ELA, global, patch and subject—have identical dimensions and RGB-pixel SHA-256 between the inspected historical run and UI-1 run. Thus no observed input-normalization/pixel difference explains these measurement differences. The historical manifests inspected do not record raw source-file SHA-256; exact original container-byte identity cannot be retroactively proved from them. UI-1 before/after and UI-2 final source-file hashes do match exactly.

Detector coverage is also identical: Instagram 23 success; Midjourney 14 success, 8 skipped, 1 unavailable, zero failed. The existing person-mask area rejection explains Midjourney's regional unavailability in both runs. The same unavailable results remain explicit in presentation. There is no measured coverage change behind the discrepancy.

Current branch is main at 00c5eb2. UI-1 edits were uncommitted at entry. Reasoning/detector files are unchanged by UI-2, and the entry hashes are preserved. Historical manifests lack a precise Git SHA and complete dependency/environment capture, so this audit does **not** assign an exact historical commit or claim all environment effects were excluded. The concrete profile and ledger differences are sufficient to explain the observed comparison; unrecorded history remains explicitly unknown.

## Decision

Preserve the current **normal-profile** baseline, 21.32705 / 2.25 and 6.675 / 1.5. No tuning, detector change, threshold adjustment or configuration substitution was performed to force older scores. UI-2 remains a visual shell project.
