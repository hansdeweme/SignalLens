# CODEX TASK — SignalLens Test Suite Rationalization & Mandatory Test Discipline

## Mission

You are the principal Python test architect, software quality engineer and repository maintenance specialist for SignalLens.

Your task is to **rationalize the current 509-test suite, remove demonstrable redundancy, consolidate overlapping tests and establish mandatory test-development discipline for all future phases**.

SignalLens has completed:

- Ten-point forensic reasoning-engine modernization.
- UI-1: Investigation session integrity.
- UI-2: Design system and workspace shell.
- UI-3: Investigation Overview.
- UI-4: Forensic image comparison.
- UI-5: Evidence and Reasoning explorers.

The GUI modernization introduced substantial regression coverage, but the suite expanded from 334 to 509 tests.

That is a 52% increase.

This growth may contain legitimate coverage, but previous development tasks repeatedly required similar session, navigation, reference-image and compatibility scenarios.

We must determine how much of this growth actually protects distinct behavior.

**Primary objective: Maximize meaningful regression protection while minimizing redundant execution, duplicated fixtures and ongoing test maintenance.**

Do not optimize toward an arbitrary test count.

---

# Part A — Baseline and inventory

## 1. Verify the repository

Project:

`D:\Coding\SignalLens`

Technology:

- Python 3.13
- PyQt6
- Existing pytest-based regression suite, where applicable.

Latest reported baseline:

- Branch: `main`
- Last reported UI-5 HEAD: `656df83`
- 509 tests passing
- Zero failures or skips
- UI-5 changes may remain uncommitted

Verify the actual branch, HEAD, Git status and test count.

Preserve all inherited changes.

Do not stage, commit, push, merge, reset, stash or discard work.

Do not modify forensic production behavior.

Run the complete baseline test suite and record:

- Collected tests.
- Passed.
- Failed.
- Skipped.
- Execution duration.
- Warnings.
- Slowest tests.

---

## 2. Create a complete test inventory

Inspect every test module.

For each test or parameterized group, record:

| Field | Description |
|---|---|
| Test ID | Pytest node identifier |
| Module | Source file |
| Category | Unit, integration, GUI, regression, reference |
| Requirement | Behavior being protected |
| Production target | Function, class or workflow |
| Fixture dependencies | Shared or local |
| Execution cost | Measured runtime |
| Similar tests | Potential overlaps |
| Unique protection | What this test alone establishes |
| Recommended action | Keep, consolidate, replace or remove |

Classify tests into domains:

1. Forensic detectors and signal extraction.
2. Reasoning and hypothesis selection.
3. Scorecard calculation.
4. Evidence lineage and corroboration.
5. Confidence policy.
6. Investigation sessions.
7. Worker lifecycle.
8. GUI navigation and state.
9. Image artifact viewing.
10. Evidence and Reasoning explorers.
11. OSINT and report consistency.
12. Stored-result compatibility.

Use actual repository structure rather than assuming each category corresponds to a module.

---

# Part B — Detect redundancy

## 3. Identify duplicate coverage

Search for:

### Exact duplicates

Tests that exercise the same inputs and assertions.

### Near duplicates

Tests that exercise the same invariant through slightly different setup or naming.

### Repeated integration scenarios

For example, multiple GUI phases may independently test that an obsolete worker callback cannot replace the active result.

### Repeated compatibility assertions

Examples include:

- Confidence unchanged.
- Scores unchanged.
- Session identity preserved.
- Report export still available.
- Navigation does not mutate results.

These may be important invariants, but they do not necessarily need separate tests in every GUI module.

### Duplicated fixtures

Identify repeated construction of:

- Investigation sessions.
- Hypothesis assessments.
- Evidence records.
- Scorecards.
- Detector artifacts.
- Qt application instances.
- Mock workers.
- Reference-image result objects.

### Overly granular implementation tests

Identify tests that duplicate other assertions or verify private implementation details without protecting a meaningful behavior.

### Important

Tests sharing similar names are not necessarily redundant.

Two tests may protect the same rule at different architectural boundaries.

Preserve such coverage when the distinction is meaningful.

Do not remove integration tests merely because unit tests exist.

---

## 4. Build a redundancy and coverage matrix

Create:

`doc/test_quality/test_overlap_matrix.md`

For every proposed consolidation:

| Existing tests | Shared behavior | Unique distinctions | Proposed replacement | Coverage retained |
|---|---|---|---|---|

Every removal must have an explicit justification.

If no equivalent coverage exists, do not remove the test unless a stronger replacement is implemented.

Distinguish:

- Confirmed duplication.
- Probable duplication requiring inspection.
- Intentional multi-layer coverage.
- Unique regression protection.

Do not treat all overlap as waste.

---

# Part C — Rationalize the suite

## 5. Consolidate demonstrably redundant tests

Use the following preference order:

1. Retain a strong existing test.
2. Reuse a shared fixture.
3. Parameterize genuinely related cases.
4. Combine redundant assertions into a coherent behavior test.
5. Remove a test only after equivalent protection is demonstrated.

### Examples

**Session identity**

Maintain authoritative lifecycle tests in the session module.

Individual GUI workspaces should test their distinct reaction to a session change, not reimplement every lifecycle transition.

**Worker safety**

Keep central tests for stale completion, status, progress and error handling.

Other GUI modules should verify only the integration behavior they uniquely introduce.

**Forensic score preservation**

Use a shared integration or reference regression test.

Do not add separate full-image score-preservation tests for every GUI component.

**Navigation**

Test generic navigation mechanics centrally.

Workspace-specific tests should focus on context transfer or specialized selection behavior.

**Presentation contracts**

Maintain centralized contract-construction tests.

Avoid testing identical field mappings repeatedly in every widget.

### Do not consolidate unrelated cases merely to reduce the count.

Test readability and diagnostic quality matter.

A single enormous test with dozens of unrelated assertions is not an improvement.

---

## 6. Improve fixtures and test organization

Where justified:

- Move repeated fixtures into appropriately scoped `conftest.py` files.
- Introduce reusable deterministic test factories.
- Prefer minimal synthetic fixtures over repeated large copied dictionaries.
- Reuse shared Qt application setup.
- Avoid unnecessary filesystem writes.
- Avoid launching complete forensic pipelines for simple UI assertions.
- Keep full reference-image tests as dedicated integration coverage.

### Important

Do not construct an elaborate fixture framework.

Prefer a few simple, explicit helpers.

Preserve test independence and avoid shared mutable state.

---

# Part D — Protect coverage quality

## 7. Establish a behavioral coverage map

Create:

`doc/test_quality/behavioral_coverage_matrix.md`

Map critical requirements to their authoritative tests.

At minimum include:

### Forensic reasoning

- Separate hypotheses.
- Provenance interpretation.
- Missing metadata neutrality.
- Hypothesis-specific evidence.
- Mathematical scorecard integrity.
- Numerical deduplication.
- Lineage-aware corroboration.
- Centralized confidence.

### Session integrity

- Unique investigation identity.
- Invocation ownership.
- Stale callback rejection.
- Worker cleanup.
- Annotation revisions.
- Report snapshot consistency.

### GUI architecture

- Workspace navigation.
- Investigation Overview.
- Source-image loading.
- Artifact identity.
- Registration and overlays.
- Evidence Explorer.
- Reasoning Explorer.
- Stored-result compatibility.

### Persistence and reporting

- Serialization.
- Legacy compatibility.
- Current investigation identity.
- Annotation/report consistency.

For each requirement identify:

- Authoritative unit test.
- Authoritative integration test, if necessary.
- Remaining coverage gaps.
- Justification for layered coverage.

A requirement does not need to appear in every phase's test module.

---

## 8. Validate removed-test protection

Before deleting or consolidating a test, determine what defect it would detect.

Where practical, use controlled fault injection or mutation-style reasoning to assess whether the retained tests still detect that defect.

Do not introduce a new mutation-testing dependency unless one is already available.

### Required checks

- No loss of critical reasoning-engine regression coverage.
- No loss of worker lifecycle safety.
- No loss of session identity protection.
- No loss of report consistency.
- No loss of image-registration correctness.
- No loss of confidence/provenance semantics.

Document meaningful exceptions.

Do not claim equivalence merely because the suite remains green after deleting a test.

---

# Part E — Mandatory test-development policy

## 9. Establish a repository-wide testing policy

Create:

`doc/test_quality/TEST_DISCIPLINE.md`

This is the authoritative test-development policy for future Codex tasks.

### Rule 1 — Coverage audit first

Before adding a test, search for existing coverage of the same invariant.

### Rule 2 — Test behavioral contracts

Prefer externally observable behavior and stable interfaces.

Avoid excessive tests of private implementation details.

### Rule 3 — Reuse existing coverage

Extend existing tests or fixtures rather than duplicating scenarios.

### Rule 4 — Centralize shared invariants

Maintain common session, worker, scoring and navigation guarantees in authoritative tests.

### Rule 5 — Separate unit from integration testing

Use inexpensive unit tests for individual transformations.

Use integration tests for meaningful cross-module boundaries.

Do not substitute ten redundant unit tests for one necessary integration test.

### Rule 6 — Minimize full-pipeline repetition

Do not rerun complete reference-image pipelines separately for every GUI component.

Maintain shared end-to-end regression tests.

### Rule 7 — Parameterize responsibly

Use parameterization where cases genuinely share setup and expected behavior.

Do not combine unrelated requirements into unreadable test matrices.

### Rule 8 — Every test must have unique value

A new test must identify which previously unprotected behavior or failure mode it covers.

### Rule 9 — Growth requires justification

A net increase exceeding **10 collected tests per future GUI phase** requires explicit justification in the final Codex report.

This is a review threshold, not a hard cap.

Do not game the threshold through giant tests.

### Rule 10 — Report changes transparently

Every future phase must report:

- Baseline collected tests.
- Tests added.
- Tests consolidated.
- Tests removed.
- Final collected tests.
- Net increase or decrease.
- Newly protected behaviors.
- Existing coverage reused.

### Rule 11 — Run the complete suite once at final validation

Targeted tests should run during development.

The full regression suite must run as a final acceptance gate.

Additional full runs are permitted when justified by risk, but unnecessary repetition should be avoided.

### Rule 12 — Do not reward test count

Success is measured by defect-detection capability, maintainability and meaningful regression protection—not the number of green tests.

---

## 10. Make the policy operational

Documentation alone is insufficient.

Ensure future Codex sessions encounter the policy.

Inspect existing repository agent instructions, including:

- `AGENTS.md`, if present.
- Relevant development instructions.
- Existing coding/testing conventions.

Add or update the appropriate repository-level guidance so that future Codex tasks must:

1. Read `doc/test_quality/TEST_DISCIPLINE.md`.
2. Audit existing tests before adding new ones.
3. Use the behavioral coverage matrix.
4. Justify each new test group.
5. Report suite growth and consolidation.

Do not overwrite unrelated instructions.

Keep the guidance concise and enforceable.

### Optional lightweight automation

If compatible with the existing test setup, introduce a simple inventory/reporting script that summarizes:

- Collected test count.
- Tests by module.
- Tests by domain.
- Test-duration distribution.

Do not introduce a complex test-management platform.

Do not add third-party dependencies solely for test-count reporting.

---

# Part F — Validation

## 11. Run the final suite

After rationalization:

1. Run the complete regression suite.
2. Record test counts and duration.
3. Confirm zero failures.
4. Confirm no unexpected skips.
5. Compare with baseline.
6. Compare critical behavioral coverage.
7. Confirm unchanged forensic production results.

### Acceptance requirement

The final suite may contain fewer than 509 tests.

However, the suite must not lose meaningful coverage simply to achieve a lower number.

If the audit finds that most tests are genuinely useful, retain them and document the reasoning.

### Reference images

Do not repeatedly run both full forensic pipelines unless changes to tests or fixtures could affect reference coverage.

The rationalization task should not modify production scoring or image-processing logic.

Use existing reference regression mechanisms where sufficient.

---

# Part G — Required deliverables

Create:

`doc/test_quality/`

### 1. `test_suite_inventory.md`

Overview of test modules, domains, runtime and responsibilities.

### 2. `test_overlap_matrix.md`

Confirmed and suspected redundant coverage, with consolidation decisions.

### 3. `behavioral_coverage_matrix.md`

Authoritative tests protecting critical SignalLens requirements.

### 4. `TEST_DISCIPLINE.md`

Mandatory rules for all future Codex development phases.

### 5. `rationalization_report.md`

Document:

- Tests retained.
- Tests consolidated.
- Tests removed.
- Fixtures reused.
- Organizational changes.
- Coverage-preservation evidence.
- Unresolved redundancies.

### 6. `regression_comparison.md`

Compare baseline and final:

- Test count.
- Runtime.
- Failures.
- Skips.
- Coverage of critical invariants.

### 7. Repository agent guidance

Update `AGENTS.md` or the appropriate existing instruction file with a concise mandatory reference to the testing policy.

### 8. Optional test-inventory script

Only if it adds value without introducing unnecessary dependencies.

---

# Part H — Final report

## 12. Required Codex summary

Return:

**A. Baseline**

Branch, HEAD, Git state, initial test count and runtime.

**B. Redundancy findings**

Number of confirmed duplicate or overlapping test groups.

**C. Rationalization**

Number of tests consolidated, removed, replaced and retained.

**D. Coverage protection**

How the critical reasoning, session and GUI invariants remain protected.

**E. Fixture improvements**

Shared factories and fixture changes, if any.

**F. Final suite**

Collected tests, passed, failed, skipped and runtime.

**G. Efficiency**

Change in runtime and maintenance complexity.

**H. Test discipline**

Location of mandatory policy and repository agent instructions.

**I. Remaining concerns**

Unresolved overlaps or coverage gaps.

**J. Git status**

Changed/untracked files and confirmation that nothing was staged, committed or pushed.

---

# Definition of Done

This task is complete when:

1. All existing tests have been inventoried.
2. Confirmed redundant coverage has been identified.
3. Demonstrably redundant tests have been consolidated or removed.
4. Critical behavioral coverage has been preserved.
5. Shared fixtures are reused where appropriate.
6. The suite remains deterministic and green.
7. The test-development policy is documented.
8. Repository-level agent guidance enforces the policy.
9. Future Codex phases must justify new tests and net suite growth.
10. No forensic production behavior has changed.

**Core principle: Every test must earn its maintenance cost by protecting meaningful behavior. A growing test count is not evidence of increasing software quality.**

Rationalize the current suite, validate retained coverage and establish enforceable test discipline. Do not begin UI-6.
