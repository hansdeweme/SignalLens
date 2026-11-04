# Reasoning Explorer

ReasoningWorkspace replaces the transitional Reasoning destination with six progressive-disclosure tabs: Hypotheses, Routes, Corroboration, Confidence, Scorecard and Raw trace. The primary hypothesis, primary pattern and recorded coverage remain above the tabs. A separate hypothesis selector scopes assessments and confidence; multiple families can remain supported simultaneously. No probability chart or mutually exclusive normalization is introduced.

Hypothesis rows show the recorded interpretation and final policy tier, with explanation, limitations, primary marker and role lists in the detail pane. The full duplicated evidence_details dictionary is left to the Evidence Explorer. Policy-only historical records remain accessible even when a corresponding hypothesis assessment is absent.

Routes preserve the original decision_route_trace order. Selected=True is shown as Selected; an explicit disposition is retained; Selected=False alone means Not selected. Matched, reason, legacy confidence and other available fields remain inspectable. Not selected never means disproven, and the UI never invents an ineligible/superseded reason.

Corroboration rows show the recorded gate result and explanation; selected details retain requirement_kind, conditions, witness sets, excluded sources, shared ancestry and limitations. Compound interpretation and general accumulation gates are not relabeled as independent-source tests. Confidence rows consume the final policy tier/rule/rationale, role lists and reliability constraints, falling back only to recorded assessment fields. The GUI applies no confidence thresholds and missing visualization files do not affect tiers.

The selected record's evidence-reference selector supports specific cross-navigation. Canonical section lineage references are resolved to actual hypothesis evidence only through explicit section/lineage mappings. Related visualization navigation requires an explicit catalog association. Raw trace opens on demand as copyable original JSON; the existing Decision Trace modal, narrative, Provenance and Reports remain available.
