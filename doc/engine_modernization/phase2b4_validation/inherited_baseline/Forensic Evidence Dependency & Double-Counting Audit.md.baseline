# CODEX TASK — SignalLens Phase 2B.1: Forensic Evidence Dependency & Double-Counting Audit

## Mission

You are the principal Python engineer, forensic image-analysis specialist, and statistical reasoning architect for SignalLens.

SignalLens is an explainable forensic analysis system that evaluates photographic authenticity, synthetic-image generation and localized image manipulation using multiple forensic detectors.

Previous development phases established:

- **Phase 1:** Hypothesis-aware reasoning and provenance interpretation.
- **Phase 1.1:** Hypothesis-specific supporting, contradicting and moderating evidence.
- **Phase 1.2:** Failure-tolerant person segmentation and regional analysis.
- **Phase 2A:** Mathematically consistent scorecard aggregation, missing-evidence handling and reconstructable calculation traces.

The latest Phase 2A validation reported:

- 184 automated tests passed.
- Both real reference images completed without stage failures.
- Instagram suspicious score: 20.47705, High localized-editing confidence.
- Midjourney suspicious score: 6.0375, Medium synthetic-origin confidence.
- Detector thresholds and scoring coefficients remained unchanged.

We now need to investigate a more fundamental forensic question:

**Does SignalLens count several measurements derived from the same underlying image property as multiple independent pieces of evidence?**

Your task is to conduct a systematic dependency and double-counting audit of the existing forensic evidence architecture.

This is a research and code-inspection task. Do not modify production scoring or reasoning behavior.

---

## 1. Repository and baseline verification

Before proceeding:

1. Inspect the current Git branch and working-tree status.
2. Identify the latest committed baseline.
3. Verify that Phase 2A implementation is present.
4. Run the existing automated test suite.
5. Record current test counts and any pre-existing failures.

Expected previous branch:

`fix/scorecard-integrity-phase2a`

If Phase 2A remains uncommitted, do not create another implementation branch or alter existing work.

Do not stage, commit, push, merge, tag, stash or discard anything.

Read existing documentation and tests relevant to the forensic scorecard.

The `test_images/` directory must remain excluded from Git. Local reference images may be analyzed read-only when necessary.

---

## 2. Establish a complete forensic signal inventory

Inspect all active forensic analysis modules and their integration into the reasoning engine.

At minimum, investigate:

- Metadata and provenance
- OSINT
- Error Level Analysis (ELA)
- Residual/noise analysis
- Cross-signal hotspot convergence
- Boundary analysis
- Boundary-focused analysis
- Segmentation alignment
- Region-aware FFT
- Global frequency-domain analysis
- Sensor-origin analysis
- CFA/demosaicing analysis
- Compression-history analysis
- Patch similarity
- Spatial patch recurrence
- Subject texture consistency
- Subject process asymmetry
- Subject material realism
- Subject-boundary analysis

Include additional active detectors found in the current codebase.

For each detector, document:

| Property | Required information |
|---|---|
| Detector | Module/function responsible |
| Inputs | Image, masks, metadata or other detector outputs |
| Underlying measurement | Mathematical or statistical feature extracted |
| Derived signal | Pattern/status/polarity produced |
| Evidence domain | Domain used by the reasoning engine |
| Score contribution | How the scorecard weights it |
| Hypotheses | Synthetic origin, localized editing, camera acquisition |
| Dependencies | Shared measurements and upstream detectors |
| Reliability controls | Existing quality gates and caveats |
| Failure behavior | Missing, inconclusive or unavailable handling |

Distinguish direct image measurements from derived interpretations and composite indicators.

Do not assume that separate Python modules provide statistically independent evidence.

---

## 3. Construct an evidence-dependency graph

Build a directed graph of the actual forensic processing architecture.

The graph should represent:

**Level 1 — Source observations**

Examples:

- Pixel values
- Local compression behavior
- Frequency characteristics
- Sensor-like structure
- Metadata fields
- Spatial masks

**Level 2 — Extracted features**

Examples:

- ELA hotspots
- Residual hotspots
- Spectral peaks
- Patch similarity
- Boundary texture differences

**Level 3 — Derived evidence**

Examples:

- Cross-signal convergence
- Foreground/background processing mismatch
- Subject-process asymmetry
- Synthetic texture recurrence

**Level 4 — Hypothesis assessment**

Examples:

- Synthetic generation
- Localized editing
- Camera-acquisition compatibility

**Level 5 — Overall decision**

The selected primary hypothesis, dominant pattern, confidence tier and explanation.

### Graph requirements

- Use actual source-code dependencies.
- Identify shared intermediate arrays and masks.
- Identify cases where one detector consumes the output of another detector.
- Identify cases where multiple detectors independently calculate similar features.
- Identify circular dependencies, if any.
- Distinguish code dependencies from suspected statistical dependence.

Produce a Mermaid diagram or Graphviz DOT file.

The diagram must be readable and should not flatten all modules into one undifferentiated graph.

---

## 4. Audit potential double-counting

Investigate every case where multiple scoring contributions may originate from overlapping measurements.

Prioritize the following relationships.

### A. ELA, residuals, cross-signal and boundary analysis

Determine whether:

- ELA and residual hotspots measure overlapping image-processing anomalies.
- Cross-signal convergence rewards their agreement.
- Boundary analysis reuses those same hotspots.
- Boundary-focused analysis adds another contribution from substantially the same observations.
- The scorecard subsequently counts these as separate suspicious domains.

Quantify how many times the same underlying observations can influence the final suspicious score.

### B. Global FFT and region-aware FFT

Determine whether:

- Both analyses rely on overlapping spectral measurements.
- Regional FFT provides genuinely new spatial localization information.
- Global and regional frequency findings can be counted as independent support without sufficient justification.

### C. Patch similarity, patch spatial and subject texture

Determine whether:

- Patch spatial analysis reuses patch-similarity matches.
- Subject texture consistency measures related repetition phenomena.
- Multiple contributions reward the same repeated structures.
- Spatial localization provides genuinely additional information.

### D. Sensor origin, CFA and subject-process asymmetry

Investigate whether:

- Sensor and CFA analyses measure overlapping acquisition characteristics.
- Subject-process asymmetry reuses or correlates with these features.
- Camera-like support and synthetic suspicion can both originate from related measurements.
- Existing counter-evidence treatment is logically justified.

### E. Subject boundary, boundary focus and segmentation alignment

Determine whether these modules provide independent measurements or alternative interpretations of the same boundary geometry and anomalies.

### F. Metadata and provenance

Confirm whether one generation declaration can contribute through:

- Metadata polarity/status
- Derived synthetic flags
- Provenance boost
- Hypothesis assessment
- Any additional scoring or confidence mechanism

Distinguish repeated reporting of the same evidence from repeated numerical contribution. Repeated presentation is not necessarily a double-counting defect.

---

## 5. Trace every contribution into the scorecard

Use the Phase 2A calculation audit to reconstruct how evidence reaches:

- `suspicious_score`
- `benign_score`
- `local_edit_support_score`
- `synthetic_boost`
- `edit_boost`
- `provenance_boost`
- `sensor_boost`
- `compression_boost`
- `caution_penalty`
- Confidence-related signals and route conditions

For each contribution, identify its upstream evidence lineage.

Create a contribution table with:

| Field | Meaning |
|---|---|
| Evidence identifier | Unique module/signal |
| Source measurements | Original feature inputs |
| Contribution path | Exact route through the scorecard |
| Raw contribution | Before reliability adjustments |
| Adjusted contribution | After reliability adjustments |
| Shared evidence group | Potentially correlated signals |
| Dependency classification | Direct, partial, suspected or independent |
| Risk | Potential double-counting impact |

Avoid summing overlapping intermediate and final contributions as if they were all independent additions.

### Important distinction

Separate:

1. **Computational dependency** — one result is calculated from another.
2. **Measurement overlap** — detectors reuse the same features or regions.
3. **Statistical correlation** — outputs covary across samples.
4. **Forensic redundancy** — evidence does not substantially increase support for a hypothesis.

Computational dependency can be established from code inspection.

Statistical correlation requires empirical data.

Forensic redundancy requires interpretation and validation.

Do not treat all four as interchangeable.

---

## 6. Quantify the impact on reference images

Use the existing full-pipeline outputs, saved reasoning traces and Phase 2A calculation breakdowns.

If those outputs are unavailable or incompatible, rerun the two reference images using the existing pipeline.

### Reference A — Instagram

Expected baseline:

- Suspicious score: 20.47705
- Overall confidence: High
- Primary hypothesis: Localized editing

### Reference B — Midjourney

Expected baseline:

- Suspicious score: 6.0375
- Overall confidence: Medium
- Primary hypothesis: Synthetic origin, unverified declaration

For each image, produce:

- Complete score contribution breakdown.
- Contributions grouped by forensic mechanism.
- Shared measurement ancestry.
- Potential duplicate contributions.
- Hypothesis-specific evidence support.
- Coverage limitations.

### Exploratory ablation analysis

Where feasible, calculate diagnostic alternatives such as:

- Removing downstream composite contributions.
- Retaining only one representative contribution from each suspected dependency group.
- Capping contributions within a group.
- Keeping direct evidence while excluding derived corroboration bonuses.

These calculations must be performed in isolated audit scripts or test fixtures.

**Do not modify the production scorecard.**

Report how hypothetical changes affect numerical scores.

Do not claim that an alternative score is more accurate without validation.

Do not compare resulting scores to existing decision thresholds as if they were calibrated under the new formula.

If a candidate formula would require recalibration, state that explicitly.

---

## 7. Evaluate independence claims in the reasoning engine

Inspect the language generated by:

- `build_confidence_rationale()`
- Overall decision narratives
- Hypothesis assessment explanations
- Supporting and contradicting evidence lists

Identify phrases such as:

- Independent forensic domains
- Multiple independent indicators
- Converging evidence
- Strong corroboration
- Distinct forensic mechanisms

Determine whether the code actually establishes the claimed level of independence.

Classify each claim as:

- Supported by source-code separation
- Supported by distinct measurement families
- Plausible but unverified
- Unsupported or misleading

Do not automatically assume that different evidence-domain identifiers imply independence.

Recommend wording improvements where the current language overstates what has been demonstrated.

Do not change production narratives during this audit.

---

## 8. Recommend dependency-management approaches

Evaluate at least four candidate approaches.

### Approach A — Evidence-family grouping

Group related detectors into measurement families and cap each family's aggregate contribution.

Evaluate simplicity, interpretability and limitations.

### Approach B — Marginal corroboration

Allow primary evidence to contribute normally, but count downstream composite indicators only for the additional information they provide.

For example, cross-signal convergence might receive an incremental bonus rather than an independent full contribution.

### Approach C — Dependency-aware contribution allocation

Allocate contributions using an explicit dependency graph to reduce redundant weighting.

Evaluate feasibility without introducing excessive complexity.

### Approach D — Empirically calibrated weighting

Estimate evidence relationships using a labeled dataset and use empirical calibration to determine appropriate contributions.

Discuss the data requirements, risks and interpretability trade-offs.

For each approach assess:

- Implementation complexity
- Explainability
- Compatibility with the current scorecard
- Resistance to overconfidence
- Requirement for labeled training/validation data
- Risks to existing forensic sensitivity
- Suitability for a deterministic forensic application

Recommend a preferred approach, but do not implement it.

---

## 9. Define empirical validation requirements

Propose a benchmark capable of evaluating correlated evidence and false-positive risk.

The proposed dataset should distinguish:

- Authentic camera photographs
- Computational photography from smartphones
- Social-media recompressed photographs
- Conventional edited photographs
- AI-enhanced photographs
- Fully AI-generated images
- Images with locally inserted synthetic elements
- Images with explicit generation metadata
- Images with stripped metadata
- Images with forged or misleading metadata

Include multiple generators, cameras, processing pipelines, resolutions and compression histories.

Prevent train/test contamination and near-duplicate leakage.

Distinguish metadata-based and content-based results.

Recommend metrics such as:

- False-positive rate
- True-positive rate
- Precision/recall
- Calibration error, once probabilistic predictions exist
- Confidence-tier reliability
- Ablation sensitivity
- Per-generator robustness
- Performance under recompression and resizing

Do not invent measured accuracy or benchmark results.

---

## 10. Deliverables

Create the audit outputs under:

`doc/phase2b_evidence_dependency/`

Suggested deliverables:

### A. Executive audit report

`evidence_dependency_audit.md`

Include:

- Executive findings
- Identified dependencies
- Confirmed duplicate contribution paths
- Suspected correlations
- Forensic implications
- Recommended implementation strategy

### B. Signal inventory

`signal_inventory.csv`

One row per active signal or score-contributing interpretation.

### C. Dependency graph

`evidence_dependency_graph.md` or `.dot`

Show the actual code dependencies and relevant hypothesis relationships.

### D. Contribution lineage

`contribution_lineage.csv`

Map each score contribution to its original measurements.

### E. Reference-image analysis

`reference_case_analysis.md`

Include the Instagram and Midjourney contribution breakdowns and diagnostic ablations.

### F. Remediation proposal

`phase2b2_implementation_proposal.md`

Provide a bounded implementation plan for Phase 2B.2, including affected files, test strategy, risks and rollback conditions.

The remediation proposal must clearly distinguish mandatory correctness fixes from optional statistical improvements.

---

## 11. Validation and quality requirements

- Preserve all existing automated tests.
- Do not modify production detector or reasoning behavior.
- Any audit scripts must be deterministic.
- Diagnostic ablations must not overwrite production results.
- Document data limitations and unverified assumptions.
- Cite exact source functions and modules for architectural findings.
- Ensure CSV inventories reconcile with actual score-contributing signals.
- Verify that the dependency graph covers every active scoring family.
- Keep reference-image outputs out of Git unless they are explicitly sanitized and approved.
- Do not stage, commit, push, merge, tag or publish.

If a required dataset is unavailable, complete the source-code dependency analysis and clearly mark empirical findings as pending rather than inventing correlations.

---

## 12. Final response format

Report the following:

**1. Baseline:** branch, Git status and existing tests.

**2. Critical findings:** the five most important evidence-dependency or double-counting risks, ranked by severity.

**3. Dependency map:** confirmed computational relationships versus suspected statistical correlations.

**4. Score impact:** Instagram and Midjourney contribution analysis, including any diagnostic ablations.

**5. Independence claims:** identify language that overstates evidence independence.

**6. Recommended Phase 2B.2 architecture:** preferred approach and justification.

**7. Validation gaps:** what additional images or labeled data are required.

**8. Deliverables:** exact files created or modified.

**9. Git status:** confirm no staging, commits or pushes.

---

## Definition of Done

Phase 2B.1 is complete when:

1. Every active forensic scoring signal has documented measurement ancestry.
2. Confirmed computational dependencies are distinguished from suspected statistical correlations.
3. Potential double-counting paths are explicitly identified.
4. Both reference-image scores are analyzed through their contribution lineage.
5. Diagnostic ablations demonstrate the possible numerical influence of overlapping evidence.
6. Unsupported independence claims are identified.
7. A specific, testable Phase 2B.2 implementation strategy is proposed.
8. No production scoring, confidence or detector behavior has changed.

**Core principle: Multiple forensic signals are valuable only to the extent that they provide genuinely additional information. Repeated measurements of the same underlying artifact must not be mistaken for independent corroboration.**

Conduct the audit, produce the requested deliverables and report your findings. Do not implement Phase 2B.2 or commit any changes.
