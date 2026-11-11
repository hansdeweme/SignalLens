# Task J — SignalLens Repository Housekeeping & Release Hygiene

**Repository:** `D:\Coding\SignalLens`  
**Starting point:** Approximately 1,114 pending Git changes  
**Baseline:** Task I complete; 540 passing tests  
**Objective:** Remove disposable development artifacts and prepare a reviewable repository state without losing implementation work, evidence or user data.

## Phase 1 — Inventory (mandatory)

Read `AGENTS.md` and the repository's test-discipline instructions.

Inspect:

- `git status --short --untracked-files=all`
- `git diff --stat`
- `git diff --name-status`
- `git ls-files --others --exclude-standard`
- Existing `.gitignore`
- Root-level directory structure

Identify all task-specific directories, including G, H and I validation directories.

Classify pending files as:

1. Production implementation.
2. Tests and necessary fixtures.
3. Permanent documentation.
4. Temporary validation outputs.
5. Generated or cached files.
6. User data and investigation artifacts.
7. Unrelated changes.
8. Uncertain ownership or purpose.

Distinguish tracked modifications, tracked deletions, untracked files and ignored files.

Count files by category and directory.


## Phase 2 — Conservative cleanup

Remove only files demonstrably safe to discard.

Examples include obsolete generated test outputs, redundant validation exports, temporary caches and build artifacts.

Retain the permanent G/H/I audit reports, implementation files and regression tests.

Review task-specific validation scripts individually. Preserve scripts necessary for meaningful reproducibility or ongoing acceptance checks; remove obsolete one-off scripts only when their results are adequately documented.

Do not remove an entire directory merely because its name begins with `.g_`, `.h_` or `.i_`.

Do not delete source images, investigation history, user-generated reports, unexpected files or directories with uncertain ownership.

Do not delete tracked files unless they are confirmed generated artifacts and their removal is justified.

Do not use:

- `git clean -fdx`
- `git reset --hard`
- Destructive blanket cleanup commands
- Recursive deletion of unknown directories

For ambiguous files, report the proposed action and leave them untouched.

## Phase 3 — Git hygiene

Review `.gitignore`.

Add narrow rules for reproducible temporary artifacts.

Avoid broad ignore patterns that might hide legitimate source files, task documentation, regression fixtures or investigation evidence.

Remember that `.gitignore` does not stop tracking files already under Git.

Do not rewrite Git history.

Do not stage, commit, push, tag or publish.

## Phase 4 — Integrity validation

Confirm:

- Production implementation from Tasks D–I remains intact.
- Existing automated tests and fixtures remain intact.
- Current and historical investigation storage remains readable.
- No user images or evidence were deleted.
- No unrelated tracked files were altered.
- No required dependency or packaging files were removed.

Run focused validation only when modules change and only on mondules changed.
Do NOT run the full test suite.

## Phase 5 — Report

Create a compact cleanup report:

`doc/reasoning_audit/repository_housekeeping.md`

Include:

1. Git status before cleanup.
2. Directory-by-directory inventory, with special attention to G/H/I.
3. Deleted file counts and byte totals.
4. Files deliberately retained and why.
5. `.gitignore` changes.
6. Git status after cleanup.
7. Remaining pending changes classified by category.
8. Unresolved files requiring manual review.

Report separately:

- Tracked modified files.
- Tracked deleted files.
- Untracked files.
- Ignored generated files.

A high remaining Git change count is acceptable when those files are legitimate implementation changes.

**Important:** Do not create a commit or stage anything. Leave the repository ready for review.

## Acceptance

Housekeeping is complete when temporary artifacts have been removed safely, the repository layout is understandable, the remaining pending changes can be explained, and the complete validation suite passes.

Preserve all legitimate work and historical evidence.

**Guiding principle: Clean generated clutter, not development history or forensic evidence.**