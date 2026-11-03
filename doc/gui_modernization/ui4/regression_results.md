# Regression results

Baseline: 432 passed, 0 failed, 0 skipped (inherited baseline.json). Final suite: **468 passed, 0 failed, 0 skipped**. See regression_results.xml for individual cases and duration. Run: `py -3.13 doc/gui_modernization/ui4/run_validation.py tests -q --junitxml=doc/gui_modernization/ui4/regression_results.xml`.

The sandbox rejects pytest's Windows private-ACL temporary directories. An elevation request was declined. run_validation.py supplies only an inherited-ACL workspace temporary-directory fixture and disables pytest's inaccessible existing cache; tests and assertions are unchanged. Each run retains its own ignored directory. This permits the full suite within the sandbox.

The 36 new UI-4 cases cover affine inverse/invalid transforms; scope traversal; session/result/source identity; overlay gates/opacity; FFT and unknown geometry; wrong dimensions, corrupt/missing files and changed source; mask reliability; stale catalog delivery; source mutation while overlaid; native mapping of a bounded 4000Ã—2000 preview; synchronized scale/center; stored catalog identity and tampering; EXIF 3/6/8; closing-window rejection; and Windows read-handle relocation. Mapping tolerance is 1e-9 mathematical units and two display pixels for integer viewport centers. Existing UI-1/UI-2/UI-3 and reasoning regressions remain passing.

Reference validation reopens saved real production UI-3 reports without executing detectors. Source SHA-256, dominant pattern and confidence tier match the recorded reference baseline. Instagram remains possible_foreground_background_processing_mismatch / High; Midjourney remains provenance_supported_synthetic_context / Medium. Existing numerical/scoring modules are unchanged, and the UI-3 stored summaries are not rewritten. Detailed artifact coverage is in reference_validation.json. No new independent full analysis or native DPI run is claimed.

