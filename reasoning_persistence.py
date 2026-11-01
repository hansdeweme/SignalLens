# reasoning_persistence.py
#signallens_gui.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
from __future__ import annotations
from hypothesis_evidence import ROLE_TITLES, evidence_presentation
import json
from pathlib import Path
from typing import Any

def persist_reasoning_trace(reasoning_trace: dict[str, Any] | None, output_dir: str | Path) -> str | None:
    if not reasoning_trace:
        return None
    output_dir = Path(output_dir)
    summary_dir = output_dir / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    trace_path = summary_dir / "reasoning_trace.json"
    trace_path.write_text(
        json.dumps(reasoning_trace, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(trace_path)

def _fmt_scalar(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)

def _fmt_scalar(value):
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)

def _filter_supporting_for_trace(items: list[str] | None, polarity: str | None, ) -> list[str]:
    if not items:
        return []
    benign_camera_patterns = {
        "camera_metadata_present",
        "weak_camera_pipeline_supported",
        "weak_camera_cfa_supported",
    }
    if polarity in {"neutral", "suspicious"}:
        return [p for p in items if p not in benign_camera_patterns]
    return items

#========================================================================
# # formatting helpers
#========================================================================
def _add_heading(lines: list[str], title: str) -> None:
    lines.append(title)
    lines.append("-" * len(title))

def _add_kv(lines: list[str], key: str, value, indent: int = 0) -> None:
    pad = " " * indent
    lines.append(f"{pad}- {key}: {_fmt_scalar(value)}")

def _add_list(lines: list[str], title: str, items: list[str] | None) -> None:
    if not items:
        return
    lines.append(title)
    for item in items:
        lines.append(f"- {item}")
    lines.append("")

#=========================================================================
# reasoning explanation helpers
# showing how and why the main decision was made 
#=========================================================================
def _build_decision_win_explanation(reasoning_trace: dict) -> list[str]:
    decision = reasoning_trace.get("decision", {}) or {}
    if decision.get("selection_reason"):
        return [decision["selection_reason"]]
    scorecard = reasoning_trace.get("scorecard", {}) or {}
    derived = reasoning_trace.get("derived_signals", {}) or {}

    lines: list[str] = []
    branch = decision.get("decision_branch")
    local_edit = scorecard.get("local_edit_support_score")
    clone = scorecard.get("clone_support_score")
    suspicious = scorecard.get("suspicious_score")
    camera_counter = scorecard.get("camera_counter_support")
    fp_risk = scorecard.get("contextual_false_positive_risk")
    patch_pattern = reasoning_trace["section_snapshot"].get("patch_similarity", {}).get("pattern")
    patch_spatial_pattern = reasoning_trace["section_snapshot"].get("patch_spatial", {}).get("pattern")
    # meta-rule: strong anomaly without stable localized mechanism
    if (
        suspicious is not None
        and suspicious >= 3.5
        and not derived.get("strong_local_edit")
        and not derived.get("patch_structured")
    ):
        lines.append(
            "strong anomaly signals exist, but no stable structural mechanism (localized editing or structured recurrence) is identified"
        )    
    if derived.get("boundary_reliability_score") is not None:
        br = float(derived.get("boundary_reliability_score") or 0.0)
        if br < 1.0:
            lines.append(
                f"boundary reliability is reduced ({_fmt_scalar(br)}), so boundary-driven signals are not treated as fully decisive"
            )                        
    if branch:        
        if branch == "possible_foreground_background_processing_mismatch":
            if local_edit is not None:
                lines.append(f"local_edit_support_score is elevated ({_fmt_scalar(local_edit)})")
            if clone is not None:
                lines.append(f"clone_support_score is lower ({_fmt_scalar(clone)}), so a clone-reuse explanation is weaker")
            if camera_counter is not None:
                lines.append(f"camera_counter_support remains limited ({_fmt_scalar(camera_counter)})")
            if fp_risk is not None:
                lines.append(f"contextual_false_positive_risk is {_fmt_scalar(fp_risk)}")
            elif branch == "localized_editing_multi_signal_convergence":
                if suspicious is not None:
                    lines.append(
                        f"suspicious_score is high enough for a multi-signal suspicious reading ({_fmt_scalar(suspicious)})"
                    )

                edit_boost = scorecard.get("edit_boost")
                if edit_boost is not None:
                    lines.append(
                        f"edit_boost contributes meaningfully to the final score ({_fmt_scalar(edit_boost)})"
                    )

                if derived.get("strong_cross") is not None:
                    lines.append(
                        f"strong_cross = {_fmt_scalar(derived.get('strong_cross'))}, indicating localized ELA/residual convergence"
                    )

                if derived.get("strong_local_edit") is not None:
                    lines.append(
                        f"strong_local_edit = {_fmt_scalar(derived.get('strong_local_edit'))}; localized editing is supported, but not at the strongest branch threshold"
                    )

                if local_edit is not None:
                    lines.append(
                        f"local_edit_support_score = {_fmt_scalar(local_edit)}, below the high-confidence localized-edit threshold but sufficient as moderate support"
                    )

                if camera_counter is not None:
                    lines.append(
                        f"camera_counter_support = {_fmt_scalar(camera_counter)}, so camera metadata moderates but does not overturn the suspicious reading"
                    )

                if fp_risk is not None:
                    lines.append(
                        f"contextual_false_positive_risk = {_fmt_scalar(fp_risk)}"
                    )                
                    
                if patch_pattern == "possible_clone_reuse" and clone == 0:
                    lines.append(
                        "patch similarity flagged possible clone reuse, but clone_support_score remains low after spatial/contextual moderation"                    
                    )
            elif branch == "real_photo_context_moderates_suspicion":
                lines.append(
                    "camera metadata and analyst-provided smartphone computational-photography context form a strong real-photo prior"
                )

                if derived.get("person_mask_reliable"):
                    lines.append(
                        "person-aware segmentation is reliable, so boundary and region signals are geometrically meaningful"
                    )

                if derived.get("boundary_reliability_score") is not None:
                    lines.append(
                        f"boundary_reliability_score = {_fmt_scalar(derived.get('boundary_reliability_score'))}, "
                        "so boundary-driven signals are considered but not treated as decisive"
                    )

                if scorecard is not None:
                    cam = getattr(scorecard, "camera_counter_support", None)
                    if cam is not None:
                        lines.append(
                            f"camera_counter_support = {_fmt_scalar(cam)}, materially offsetting suspicious signals"
                        )

                if local_edit is not None:
                    lines.append(
                        f"local_edit_support_score = {_fmt_scalar(local_edit)}, but interpreted as consistent with smartphone computational processing rather than compositing"
                    )
            elif branch == "localized_processing_inconclusive":
                if suspicious is not None:
                    lines.append(
                        f"suspicious_score is elevated ({_fmt_scalar(suspicious)}), but not enough to override moderating evidence decisively"
                    )
                if scorecard.get("edit_boost") is not None:
                    lines.append(
                        f"edit_boost is present ({_fmt_scalar(scorecard.get('edit_boost'))}), supporting localized differential processing"
                    )
                if derived.get("strong_cross") is not None:
                    lines.append(
                        f"strong_cross = {_fmt_scalar(derived.get('strong_cross'))}, so ELA/residual convergence supports localized processing"
                    )
                if local_edit is not None:
                    lines.append(
                        f"local_edit_support_score is moderate ({_fmt_scalar(local_edit)}), below the threshold for a strong localized-edit conclusion"
                    )
                if scorecard.get("clone_support_score") is not None:
                    lines.append(
                        f"clone_support_score is low ({_fmt_scalar(scorecard.get('clone_support_score'))}), so clone-reuse is not strongly supported despite patch similarity"
                    )                                        
                if scorecard.get("camera_counter_support") is not None:
                    lines.append(
                        f"camera_counter_support is meaningful ({_fmt_scalar(scorecard.get('camera_counter_support'))}), moderating the suspicious interpretation"
                    )
                if derived.get("strong_local_edit") is not None:
                    lines.append(
                        f"strong_local_edit = {_fmt_scalar(derived.get('strong_local_edit'))}, so the system avoids a decisive localized-edit verdict"
                    )
                if fp_risk is not None:
                    lines.append(
                        f"contextual_false_positive_risk = {_fmt_scalar(fp_risk)}"
                    )                    
                if scorecard.get("caution_penalty") is not None:
                    lines.append(
                        f"caution_penalty is applied ({_fmt_scalar(scorecard.get('caution_penalty'))}), reflecting ambiguity in mechanism attribution"
                    )                    
            elif branch == "boundary_support_limited_localized_processing":
                if derived.get("boundary_reliability_score") is not None:
                    lines.append(
                        f"boundary_reliability_score = {_fmt_scalar(derived.get('boundary_reliability_score'))}, "
                        "so boundary-dependent evidence is treated cautiously"
                    )
                if derived.get("boundary_support_ratio") is not None:
                    lines.append(
                        f"boundary_support_ratio = {_fmt_scalar(derived.get('boundary_support_ratio'))}, "
                        "indicating limited usable boundary support"
                    )
                if local_edit is not None:
                    lines.append(
                        f"local_edit_support_score = {_fmt_scalar(local_edit)}, but the score is moderated by boundary reliability"
                    )
                if camera_counter is not None:
                    lines.append(
                        f"camera_counter_support = {_fmt_scalar(camera_counter)}, further moderating the localized-processing interpretation"
                    )
        elif branch == "region_geometry_unreliable_localized_processing":
            if derived.get("region_geometry_unreliable") is not None:
                lines.append(
                    f"region_geometry_unreliable = {_fmt_scalar(derived.get('region_geometry_unreliable'))}, "
                    "so subject/boundary-dependent signals are treated cautiously"
                )
            if suspicious is not None:
                lines.append(
                    f"suspicious_score remains elevated ({_fmt_scalar(suspicious)}), but the unreliable region split prevents a strong compositing verdict"
                )
            if local_edit is not None:
                lines.append(
                    f"local_edit_support_score is elevated ({_fmt_scalar(local_edit)}), but depends on unstable subject/boundary geometry"
                )
            if scorecard.get("caution_penalty") is not None:
                lines.append(
                    f"caution_penalty is increased ({_fmt_scalar(scorecard.get('caution_penalty'))}) to reflect unreliable region geometry"
                )
            if camera_counter is not None:
                lines.append(
                    f"camera_counter_support = {_fmt_scalar(camera_counter)}, further moderating the suspicious interpretation"
                )                    
        elif branch == "possible_clone_reuse":
            if clone is not None:
                lines.append(f"clone_support_score is elevated ({_fmt_scalar(clone)})")
            if local_edit is not None:
                lines.append(f"local_edit_support_score is lower ({_fmt_scalar(local_edit)}), so localized editing is less favored")
            if camera_counter is not None:
                lines.append(f"camera_counter_support remains limited ({_fmt_scalar(camera_counter)})")
        elif branch == "synthetic_multi_signal_convergence":
            if suspicious is not None:
                lines.append(f"suspicious_score is high ({_fmt_scalar(suspicious)})")
            if derived.get("fft_structured") is not None:
                lines.append(f"fft_structured = {_fmt_scalar(derived.get('fft_structured'))}")
            if derived.get("patch_structured") is not None:
                lines.append(f"patch_structured = {_fmt_scalar(derived.get('patch_structured'))}")
            if derived.get("camera_like_support") is not None:
                lines.append(f"camera_like_support = {_fmt_scalar(derived.get('camera_like_support'))}")
        elif branch == "photo_like_consistency_supported":
            if suspicious is not None:
                lines.append(f"suspicious_score remains low ({_fmt_scalar(suspicious)})")
            if scorecard.get("benign_score") is not None:
                lines.append(f"benign_score is supportive ({_fmt_scalar(scorecard.get('benign_score'))})")
            if derived.get("camera_like_support") is not None:
                lines.append(f"camera_like_support = {_fmt_scalar(derived.get('camera_like_support'))}")
        else:
            if suspicious is not None:
                lines.append(f"suspicious_score = {_fmt_scalar(suspicious)}")
            if camera_counter is not None:
                lines.append(f"camera_counter_support = {_fmt_scalar(camera_counter)}")
            if fp_risk is not None:
                lines.append(f"contextual_false_positive_risk = {_fmt_scalar(fp_risk)}")
    return lines

def build_reasoning_trace_text(reasoning_trace: dict | None) -> str:
    if not reasoning_trace:
        return ""
    lines: list[str] = []
    lines.append("Reasoning Trace")
    lines.append("")
    analysis_mode = reasoning_trace.get("analysis_mode")
    if analysis_mode is not None:
        lines.append(f"Analysis Mode: {analysis_mode}")
        lines.append("")
    decision = reasoning_trace.get("decision", {}) or {}
    scorecard = reasoning_trace.get("scorecard", {}) or {}
    derived = reasoning_trace.get("derived_signals", {}) or {}
    sections = reasoning_trace.get("section_snapshot", {}) or {}
    pipeline = reasoning_trace.get("pipeline_status", {})
    policy = reasoning_trace.get('confidence_policy')
    if policy:
        _add_heading(lines, 'Confidence Policy')
        _add_kv(lines, 'Version', policy.get('version'))
        _add_kv(lines, 'Primary Hypothesis', policy.get('primary_hypothesis'))
        for assessment in policy.get('assessments', []):
            _add_kv(lines, assessment['hypothesis'], assessment['tier'] + ' / ' + assessment['policy_rule'])
            _add_list(lines, 'Policy Rationale', assessment['rationale'])
            _add_list(lines, 'Policy Limitations', assessment['reliability_limitations'])
        lines.append('')
    corroboration = reasoning_trace.get('corroboration_audit')
    if corroboration:
        _add_heading(lines, 'Production Corroboration Audit')
        _add_kv(lines, 'Version', corroboration.get('version'))
        for gate in corroboration.get('evaluated_gates', []):
            lines.append(f"- {gate['gate_id']}: passed={gate.get('gate_passed', gate['requirement_satisfied'])}; {gate['explanation']}")
            _add_kv(lines, '  Eligible Evidence', gate['eligible_evidence'])
            _add_kv(lines, '  Distinct Ancestry Groups', gate['distinct_ancestry_groups'])
            _add_kv(lines, '  Shared Ancestry', gate['shared_ancestry'])
        _add_list(lines, 'Corroboration Limitations', corroboration.get('limitations'))
        lines.append('')
    dependency = reasoning_trace.get('evidence_dependency_analysis')
    if dependency:
        _add_heading(lines, 'Evidence Dependency Analysis (Shadow Only)')
        for key in ('lineage_version', 'status', 'policy', 'production_score_unchanged', 'comparison', 'families', 'shared_ancestry'):
            _add_kv(lines, key, dependency.get(key))
        _add_list(lines, 'Shadow Limitations', dependency.get('limitations'))
        _add_list(lines, 'Shadow Errors', dependency.get('errors'))
        lines.append('No shadow confidence tier or forensic decision is assigned.')
        lines.append('')
    calculation = reasoning_trace.get("scorecard_calculation")
    if calculation:
        _add_heading(lines, "Scorecard Calculation")
        _add_kv(lines, "Version", calculation.get("calculation_version"))
        _add_kv(lines, "Status", calculation.get("status"))
        for key in ("base_suspicious", "base_benign", "raw_contributions", "final_contributions", "reliability_adjustments", "aggregate_transforms", "aggregate_scores"):
            if key in calculation:
                _add_kv(lines, key, calculation[key])
        _add_list(lines, "Calculation Errors", calculation.get("errors"))
        numerical = calculation.get('numerical_deduplication')
        if numerical:
            _add_heading(lines, 'Production Numerical Evidence Allocation')
            _add_kv(lines, 'Version', numerical.get('version'))
            _add_kv(lines, 'Base/domain reconciliation', numerical.get('aggregate_reconciliation'))
            for item in numerical.get('contributions', []):
                lines.append(
                    f"- {item['evidence_id']} [{item['classification']}]: "
                    f"raw={item['raw_contribution']}; credited={item['credited_contribution']}; "
                    f"suppressed={item['suppressed_contribution']}; {item['reason']}"
                )
            _add_list(lines, 'Unresolved numerical relationships', numerical.get('unresolved_relationships'))
            for item in numerical.get('component_allocations', []):
                lines.append(f"- {item['field']} / {item['evidence_id']}: raw={item['raw_contribution']}; suppressed={item['suppressed_contribution']}; multiplier={item['reliability_multiplier']}; {item['reason']}")
            lines.append('Base allocations precede aggregate attenuation, penalties and floor; shared ancestry does not establish independence.')
        for operation in calculation.get("component_operations", []):
            lines.append(f"- {operation['field']} {operation['operation']} {operation['operand']}: {operation['reason']}")
        lines.append("")
    if pipeline:
        _add_heading(lines, "Pipeline Coverage")
        _add_kv(lines, "Coverage", pipeline.get("coverage", {}).get("status"))
        _add_kv(lines, "Stage Counts", pipeline.get("coverage", {}).get("stage_counts"))
        mask = pipeline.get("mask_diagnostics", {})
        for key in ("mask_status", "mask_source", "mask_reliability", "fallback_used", "fallback_reason"):
            _add_kv(lines, key, mask.get(key))
        _add_list(lines, "Mask Rejection Reasons", mask.get("rejection_reasons"))
        _add_list(lines, "Unavailable Regional Stages", mask.get("disabled_stages"))
    _add_heading(lines, "Final Decision")
    _add_kv(lines, "Branch", decision.get("decision_branch"))
    _add_kv(lines, "Dominant Pattern", decision.get("dominant_pattern"))
    _add_kv(lines, "Confidence Tier", decision.get("confidence_tier"))
    _add_kv(lines, "Polarity", decision.get("polarity"))
    if decision.get("primary_hypothesis"):
        _add_kv(lines, "Primary Hypothesis", decision["primary_hypothesis"])
    lines.append("")
    for assessment in reasoning_trace.get("hypothesis_assessments", []):
        _add_heading(lines, assessment["hypothesis_id"])
        for key in ("polarity", "confidence_tier", "decision_branch", "explanation"):
            _add_kv(lines, key, assessment.get(key))
        presentation = evidence_presentation(assessment)
        for role, title in ROLE_TITLES.items():
            _add_list(lines, title, presentation[role.replace("_evidence", "_explanations")])
        _add_list(lines, "Limitations", assessment.get("limitations"))
    provenance = reasoning_trace.get("provenance_evidence")
    if provenance:
        _add_heading(lines, "Provenance Evidence")
        for key, value in provenance.items():
            _add_kv(lines, key, value)
    if reasoning_trace.get("decision_route_trace"):
        _add_heading(lines, "Route Candidates")
        for candidate in reasoning_trace["decision_route_trace"]:
            lines.append(
                f"- {candidate.get('route')}: matched={candidate.get('matched')}; "
                f"{candidate.get('disposition') or candidate.get('reason')}"
            )
        lines.append("")
    overall_text = decision.get("overall_text")
    if overall_text:
        _add_heading(lines, "Decision Summary")
        for raw_line in str(overall_text).splitlines():
            if raw_line.strip():
                lines.append(raw_line)
        lines.append("")
    why_lines = _build_decision_win_explanation(reasoning_trace)
    if why_lines:
        _add_heading(lines, "Why This Decision Won")
        for item in why_lines:
            lines.append(f"- {item}")
        lines.append("")
    for role, title in ROLE_TITLES.items():
        explanations = decision.get(role.replace("_evidence", "_explanations"))
        _add_list(lines, title, explanations if explanations is not None else decision.get(role.replace("_evidence", "_signals")))
    _add_list(lines, "Evidence Limitations", decision.get("limitations"))
    _add_list(lines, "Confidence Rationale", decision.get("confidence_rationale"))
    _add_heading(lines, "Scorecard Highlights")
    highlight_keys = [
        "suspicious_score",
        "benign_score",
        "local_edit_support_score",
        "clone_support_score",
        "camera_counter_support",
        "synthetic_boost",
        "edit_boost",
        "provenance_boost",
        "caution_penalty",
        "contextual_false_positive_risk",
    ]
    for key in highlight_keys:
        if key in scorecard:
            _add_kv(lines, key, scorecard[key])
    lines.append("")
    _add_heading(lines, "Derived Signals")
    derived_keys = [
        "person_mask_reliable",
        "subject_area_ratio",
        "boundary_support_ratio",
        "boundary_support_low",
        "boundary_reliability_score",        
        "strong_local_edit",
        "strong_cross",
        "region_geometry_unreliable",
        "patch_structured",
        "fft_structured",
        "camera_like_support",
        "metadata_synthetic",
        "metadata_enhancement",
        "metadata_missing",
        "provenance_state",
        "provenance_clean",
        "local_signals_weak",
    ]
    for key in derived_keys:
        if key in derived:
            _add_kv(lines, key, derived[key])
    lines.append("")
    _add_heading(lines, "Section Snapshot")
    for key, section in sections.items():
        lines.append(f"- {key}")
        if isinstance(section, dict):
            preferred_order = ["pattern", "score", "polarity", "status", "name", "note"]
            for sub_key in preferred_order:
                if sub_key in section:
                    lines.append(f"    {sub_key}: {_fmt_scalar(section[sub_key])}")
            for sub_key, sub_value in section.items():
                if sub_key not in preferred_order:
                    lines.append(f"    {sub_key}: {_fmt_scalar(sub_value)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def persist_reasoning_trace_text(reasoning_trace: dict[str, Any] | None, output_dir: str | Path) -> str | None:
    if not reasoning_trace:
        return None
    output_dir = Path(output_dir)
    summary_dir = output_dir / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    trace_txt_path = summary_dir / "reasoning_trace.txt"
    trace_txt_path.write_text(
        build_reasoning_trace_text(reasoning_trace),
        encoding="utf-8",
    )
    return str(trace_txt_path)
