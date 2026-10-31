#signallens_controller.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Any
import json
import time
# local imports
from signallens_settings import get_patch_profile, get_subject_background_profile
from run_reporting import RunRecorder
from image_gatekeeper import prepare_analysis_images
from exiftool_backend import analyze_file_with_exiftool
from vf_ela import run_ela
from vf_noise import run_noise_analysis
from vf_fft import run_fft_analysis
from vf_cross_signal import compute_cross_signal_payload
from vf_person_subject_mask import run_person_subject_mask_analysis, derive_region_masks_from_person_mask
from vf_overlay import create_shared_boundary_overlays
from vf_patch_similarity import run_patch_similarity_analysis
from vf_sensor_origin import run_sensor_origin_analysis
from vf_subject_boundary import run_subject_boundary_analysis
from vf_compression_history import run_compression_history_analysis
from vf_cfa_demosaic import run_cfa_demosaic_analysis
from vf_region_masks import run_region_mask_analysis
from vf_region_fft import run_region_fft_analysis
from vf_boundary_focus import run_boundary_focus_analysis
from vf_patch_spatial import run_patch_spatial_analysis
from vf_subject_texture_consistency import run_subject_texture_consistency_analysis
from vf_subject_process_asymmetry import run_subject_process_asymmetry_analysis
from vf_subject_material_realism import run_subject_material_realism_analysis
from vf_region_segmentation import run_region_segmentation_analysis
from vf_segmentation_alignment import compute_segmentation_boundary_alignment

LogFn = Callable[[str], None]
StatusFn = Callable[[str], None]
PERFCOUNT = False
RUN_LEGACY_REGION_MASKS = False

@dataclass
class AnalysisState:
    selected_file: Path
    output_dir: Path
    output_json: Path | None = None
    run_recorder: Any | None = None
    prepared_images_payload: dict | None = None
    exif_payload: dict | None = None
    ela_payload: dict | None = None
    noise_payload: dict | None = None
    cross_signal_payload: dict | None = None
    fft_payload: dict | None = None
    patch_similarity_payload: dict | None = None
    sensor_origin_payload: dict | None = None
    subject_boundary_payload: dict | None = None
    compression_history_payload: dict | None = None
    cfa_demosaic_payload: dict | None = None
    region_masks_payload: dict | None = None
    region_masks_payload_old: dict | None = None
    person_subject_mask_payload: dict | None = None
    segmentation_alignment_payload: dict | None = None
    region_fft_payload: dict | None = None    
    boundary_focus_payload: dict | None = None
    patch_spatial_payload: dict | None = None
    subject_texture_consistency_payload: dict | None = None
    subject_process_asymmetry_payload: dict | None = None
    subject_material_realism_payload: dict | None = None
    analysis_mode: str = "normal"
    errors: list[str] = field(default_factory=list)
    person_mask_meta: dict | None = None
    person_mask_reliable: bool = False
    person_mask_reliability: str | None = None
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

#----------------------------------------------------------------
# The SignalLensController class manages the execution of the analysis pipeline stages, logging, status updates, and error handling. 
# It provides a structured way to run each analysis step while maintaining the state and ensuring that errors are captured without crashing the entire process.
# Each stage is defined as a function that can be executed with the run_stage method, which handles logging, status updates, and error management in a consistent way.
#----------------------------------------------------------------

class SignalLensController:
    def __init__(
        self,
        log_fn: LogFn | None = None,
        status_fn: StatusFn | None = None,
        summary_update_fn: Callable[[], None] | None = None,
    ) -> None:
        self.log_fn = log_fn or (lambda msg, level="info": None)
        self.status_fn = status_fn or (lambda msg: None)
        self.summary_update_fn = summary_update_fn
        self.perf = PERFCOUNT

    def log(self, message: str, level: str = "info") -> None:
        self.log_fn(message, level)

    def set_status(self, message: str) -> None:
        self.status_fn(message)

    def update_summary(self) -> None:
        if self.summary_update_fn:
            self.summary_update_fn()

    def run_stage(
        self,
        state: AnalysisState,
        name: str,
        func,
        assign_attr: str | None = None,
        success_log=None,
        status_success: str | None = None,
        require: list[str] | None = None,
    ):
        if require:
            for attr in require:
                if getattr(state, attr, None) is None:
                    self.log(f"Skipping {name} (missing dependency: {attr})", "warn")
                    print(f"[SignalLens] Stage skipped: {name} (missing dependency: {attr})")
                    return None
        self.log(f"Running {name}...", "info")
        if self.perf:
            print(f"[SignalLens] Stage started: {name}")
        if state.run_recorder:
            state.run_recorder.record_stage_start(name)
            state.run_recorder.log(f"Stage started: {name}", "info")                        
        stage_start = time.perf_counter()
        try:
            result = func()
            stage_duration = time.perf_counter() - stage_start
            if assign_attr:
                setattr(state, assign_attr, result)
            if success_log:
                success_log(result)
                # state.run_recorder.log(f"Result: {result}", "info")    
            self.update_summary()
            if status_success:
                self.set_status(status_success)
            self.log(f"{name} completed.", "success")
            if self.perf:
                print(f"[SignalLens] Stage completed: {name} in {stage_duration:.2f}s")
            if state.run_recorder:
                state.run_recorder.record_stage_finish(name, elapsed_seconds=stage_duration, status="success")
                state.run_recorder.log(f"Stage succeeded: {name} ({stage_duration:.3f}s)", "success")                
            return result
        except Exception as exc:
            stage_duration = time.perf_counter() - stage_start
            msg = f"{name} failed: {exc}"
            state.errors.append(msg)
            self.log(f"ERROR [{name}]: {exc}", "error")
            self.set_status(f"{name} error.")
            if state.run_recorder:
                state.run_recorder.record_stage_finish(name, elapsed_seconds=stage_duration, status="failed", error=str(exc))
                state.run_recorder.record_error(name, str(exc))
                state.run_recorder.log(f"Stage failed: {name} | {exc}", "error")                        
            print(f"[SignalLens] Stage failed: {name} after {stage_duration:.2f}s ({exc})")
            return None
               
#----------------------------------------------------------------
# The run_analysis method orchestrates the entire analysis workflow, executing each stage in sequence while managing the state and handling errors gracefully.
#  We have 4 layers of signals:
#  1. Source signals        (raw measurements)
#  2. Local structure       (ELA, noise, patches)
#  3. Cross / relational    (cross-signal, boundary, alignment)
#  4. Semantic / subject    (material realism, asymmetry, segmentation)
# Optimal sequnece:
# 1. independent: EXIF / metadata, OSINT
# 2. pixel-domain base signals: ELA, Noise / residual, Sensor-origin, CFA / demosaicing 
# 3. structural extraction: Region masks, Patch similarity, FFT / frequency
# 4. derived local signals: Cross-signal, Boundary analysis
# 5. segmentation refinement: Region segmentation, Segmentation alignment
# 6. subject-level reasoning: Subject texture consistency, Subject process asymmetry, Subject material realism
# 7. compression: Compression-history
#----------------------------------------------------------------
    def run_analysis(
        self,
        selected_file: Path,
        output_dir: Path,
        output_json: Path | None = None,
        analysis_mode: str = "normal",
    ) -> AnalysisState:
        state = AnalysisState(
            selected_file=selected_file,
            output_dir=output_dir,
            output_json=output_json,
            analysis_mode= analysis_mode            
        )
        analysis_start = time.perf_counter()
        print(f"[SignalLens] Analysis started for: {selected_file}")
        # Stage 0: Prepared image gatekeeper
        state.run_recorder = RunRecorder(
            output_dir=state.output_dir,
            selected_file=state.selected_file,
        )
        state.run_recorder.log("Analysis run started", "info")
        state.run_recorder.add_artifact("output_dir", str(state.output_dir))
        state.run_recorder.add_artifact("output_json", str(state.output_json) if state.output_json else None)        
        # Stage 1: Prepared image gatekeeper: uniform geometry        
        # use for 'heavy' stages: FFT, Patch similarity
        self.run_stage(
            state=state,
            name="Prepared image gatekeeper",
            func=lambda: prepare_analysis_images(
                image_path=state.selected_file,
                output_dir=state.output_dir,
            ),
            assign_attr="prepared_images_payload",
            success_log=lambda p: self.log(
                f"Prepared image variants ready: "
                f"{', '.join(sorted(p.get('prepared', {}).keys()))}",
                "finding",
            ),
            status_success="Prepared analysis images ready",
        )        
        # Stage 1: Metadata (Exif)
        self.run_stage(
            state=state,
            name="EXIF analysis",
            func=lambda: analyze_file_with_exiftool(
                file_path=state.selected_file,
                output_json_path=state.output_json,
            ),
            assign_attr="exif_payload",
            success_log=lambda p: self.log(json.dumps(p.get("classification", {}), indent=2, ensure_ascii=False), "finding"),
            status_success="Metadata analysis done",
        )
        # Stage 2: ELA
        self.run_stage(
            state=state,
            name="ELA analysis",
            func=lambda: run_ela(
                image_path=state.selected_file,
                output_dir=state.output_dir,
                jpeg_quality=90,
            ),
            assign_attr="ela_payload",
            success_log=lambda p: self.log(f"ELA pattern: {p.get('ela', {}).get('pattern', {}).get('ela_pattern')}", "finding"),
            status_success="ELA done",
        )
        # Stage 3: Noise
        self.run_stage(
            state=state,
            name="Noise analysis",
            func=lambda: run_noise_analysis(
                image_path=state.selected_file,
                output_dir=state.output_dir,
            ),
            assign_attr="noise_payload",
            success_log=lambda p: self.log(f"Noise pattern: {p.get('noise', {}).get('pattern', {}).get('noise_pattern')}", "finding"),
            status_success="Noise analysis done",
        )
        # Stage 4: Sensor-origin
        self.run_stage(
            state=state,
            name="Sensor-origin analysis",
            func=lambda: run_sensor_origin_analysis(
                image_path=state.selected_file,
                output_dir=state.output_dir,
            ),
            assign_attr="sensor_origin_payload",
            success_log=lambda p: self.log(
                f"Sensor-origin pattern: {p.get('sensor_origin', {}).get('pattern', {}).get('sensor_origin_pattern')}",
                "finding"
            ),
            status_success="Sensor-origin analysis done",
        )
        # Stage 5: CFA / demosaicing
        self.run_stage(
            state=state,
            name="CFA / demosaicing analysis",
            func=lambda: run_cfa_demosaic_analysis(
                image_path=state.selected_file,
                output_dir=state.output_dir,
            ),
            assign_attr="cfa_demosaic_payload",
            success_log=lambda p: self.log(
                f"CFA / demosaicing pattern: {p.get('cfa_demosaic', {}).get('pattern', {}).get('cfa_demosaic_pattern')}",
                "finding",
            ),
            status_success="CFA / demosaicing analysis done",
        )                       
        # Stage 6: Person-aware subject mask
        self.run_stage(
            state=state,
            name="Person-aware subject mask",
            func=lambda: run_person_subject_mask_analysis(
                image_path=state.prepared_images_payload["prepared"]["subject"]["path"],
                output_dir=state.output_dir,
            ),
            assign_attr="person_subject_mask_payload",
            require=["prepared_images_payload"],
            success_log=lambda p: self.log(
                "Person subject mask: "
                f"{p.get('person_subject_mask', {}).get('quality', {}).get('mask_reliability', 'unknown')} | "
                f"backend={p.get('person_subject_mask', {}).get('backend', 'unknown')} | "
                f"area={p.get('person_subject_mask', {}).get('quality', {}).get('subject_area_ratio', 0.0):.3f}",
                "finding",
            ),
            status_success="Person-aware subject mask done",
        )
        # Substage 6a: Person-derived region masks       
        def _derive_person_region_masks_if_reliable(state):
            person_block = (state.person_subject_mask_payload or {}).get("person_subject_mask", {})
            quality = person_block.get("quality", {})
            reliability = quality.get("mask_reliability", "low")

            state.person_mask_reliability = reliability
            state.person_mask_reliable = reliability in {"high", "medium"}

            if not state.person_mask_reliable:
                if state.region_masks_payload_old is not None:
                    return state.region_masks_payload_old
                raise ValueError(
                    f"Person subject mask is not reliable enough and no legacy fallback exists: {reliability}"
                )

            return derive_region_masks_from_person_mask(
                person_mask_path=person_block["mask_path"],
                image_path=state.prepared_images_payload["prepared"]["subject"]["path"],
                output_dir=state.output_dir,
                person_mask_reliability=reliability,
            )
        self.run_stage(
            state=state,
            name="Person-derived region masks",
            func=lambda: _derive_person_region_masks_if_reliable(state),
            assign_attr="region_masks_payload",
            require=["person_subject_mask_payload", "prepared_images_payload"],
            success_log=lambda p: self.log(
                "Region masks from person subject: "
                f"subject={p.get('region_masks', {}).get('subject_ratio', 0.0):.3f} | "
                f"boundary={p.get('region_masks', {}).get('boundary_ratio', 0.0):.3f} | "
                f"background={p.get('region_masks', {}).get('background_ratio', 0.0):.3f}",
                "finding",
            ),
            status_success="Person-derived region masks done",
        )
        def _update_person_mask_reliability(state):
            block = (state.person_subject_mask_payload or {}).get("person_subject_mask", {})
            quality = block.get("quality", {})
            reliability = quality.get("mask_reliability", "low")
            state.person_mask_reliability = reliability
            state.person_mask_reliable = reliability in {"high", "medium"}
            return {
                "person_mask_reliability": reliability,
                "person_mask_reliable": state.person_mask_reliable,
            }            
        self.run_stage(
            state=state,
            name="Person mask reliability",
            func=lambda: _update_person_mask_reliability(state),
            assign_attr="person_mask_meta",
            require=["person_subject_mask_payload"],
            success_log=lambda p: self.log(
                f"Person mask reliability: {p.get('person_mask_reliability')} "
                f"(usable={p.get('person_mask_reliable')})",
                "info",
            ),
            status_success="Person mask reliability evaluated",
        )
        if RUN_LEGACY_REGION_MASKS == True:            
            # Stage 7: Legacy Region masks (once needed for: subject vs background, boundary band, all subject modules )
            self.run_stage(
                state=state,
                name="Region-mask legacy",
                func=lambda: run_region_mask_analysis(
                    image_path=state.selected_file,
                    output_dir=state.output_dir,
                    boundary_width_px=18,
                ),
                assign_attr="region_masks_payload_old",
                success_log=lambda p: self.log(
                    "Region masks created: "
                    f"subject={p.get('region_masks', {}).get('ratios', {}).get('subject', 0.0):.3f}, "
                    f"boundary={p.get('region_masks', {}).get('ratios', {}).get('boundary', 0.0):.3f}, "
                    f"background={p.get('region_masks', {}).get('ratios', {}).get('background', 0.0):.3f}",
                    "finding",
                ),
                status_success="Region-mask analysis done",
            )
            if state.person_mask_reliable == False:
                state.region_masks_payload = state.region_masks_payload_old                
        # Stage 8: Subject boundary
        self.run_stage(
            state=state,
            name="Subject-boundary analysis",
            func=lambda: run_subject_boundary_analysis(
                image_path=state.selected_file,
                output_dir=state.output_dir,
            ),
            assign_attr="subject_boundary_payload",
            success_log=lambda p: self.log(
                f"Subject-boundary pattern: {p.get('subject_boundary', {}).get('pattern', {}).get('subject_boundary_pattern')}",
                "finding"
            ),
            status_success="Subject-boundary analysis done",
        )               
        # Stage 9: Region-segmentation
        self.run_stage(
            state=state,
            name="Region segmentation analysis",
            func=lambda: run_region_segmentation_analysis(
                state.region_masks_payload
            ),
            assign_attr="region_segmentation_payload",
            require=["region_masks_payload"],
        )        
        # Stage 10: FFT
        self.run_stage(
            state=state,
            name="FFT analysis",
            func=lambda: run_fft_analysis(
                image_path=Path(state.prepared_images_payload["prepared"]["global"]["path"]),
                out_dir=state.output_dir,
            ),
            assign_attr="fft_payload",
            success_log=lambda p: self.log(f"FFT pattern: {p.get('fft', {}).get('frequency_pattern')}", "finding"),
            status_success="FFT analysis done",
        )
        # Stage 11: Patch similarity 
        patch_params = get_patch_profile(state.analysis_mode)
        self.run_stage(
            state=state,
            name="Patch similarity analysis",
            func=lambda: run_patch_similarity_analysis(
                image_path=Path(state.prepared_images_payload["prepared"]["patch"]["path"]),
                output_dir=state.output_dir,
                patch_size=patch_params.get("patch_size", 24),
                stride=patch_params.get("stride", 12),
                descriptor_size=patch_params.get("descriptor_size", 8),
                similarity_threshold=patch_params.get("similarity_threshold", 0.965),
                max_pairs_to_keep=patch_params.get("max_pairs_to_keep", 300),
                max_pairs_for_overlay=patch_params.get("max_pairs_for_overlay", 60),                                
            ),
            assign_attr="patch_similarity_payload",
            success_log=lambda p: self.log(
                f"Pattern: {p.get('patch_similarity', {}).get('similarity_pattern')} | "
                f"profile={state.analysis_mode} | "
                f"Patches: {p.get('patch_similarity', {}).get('patch_count')} | "
                f"Matches: {p.get('patch_similarity', {}).get('pair_count')} | "
                f"Comparisons: {p.get('patch_similarity', {}).get('candidate_comparisons')}",
                "finding",
            ),
            status_success="Patch similarity analysis done",
        )       
        # Stage 12: Cross-signal (based on: ELA, Noise)
        def log_cross_signal_result(p):
            self.log(f"Cross-signal pattern: {p['cross_signal'].get('cross_signal_pattern')}", "info")
            self.log(f"Cross-signal note: {p['cross_signal'].get('cross_signal_note')}", "info")
            self.log(f"Boundary pattern: {p['boundary_signal'].get('boundary_pattern')}", "info")
            self.log(f"Boundary note: {p['boundary_signal'].get('boundary_note')}", "info")
        def cross_signal_func():
            ela_blocks = state.ela_payload["ela"]["blockwise"]["top_blocks"]
            noise_blocks = state.noise_payload["noise"]["blockwise"]["top_blocks"]
            ela_pattern = state.ela_payload["ela"]["pattern"]
            noise_pattern = state.noise_payload["noise"]["pattern"]
            image_shape = tuple(state.region_masks_payload["region_masks"]["shape"])
            block_size = int(state.ela_payload["ela"]["blockwise"].get("block_size", 64))
            return compute_cross_signal_payload(
                ela_blocks=ela_blocks,
                noise_blocks=noise_blocks,
                ela_pattern=ela_pattern,
                noise_pattern=noise_pattern,
                image_shape=image_shape,
                block_size=block_size,
            )
        self.run_stage(
            state=state,
            name="Cross-signal analysis",
            func=cross_signal_func,
            assign_attr="cross_signal_payload",
            require=["ela_payload", "noise_payload"],
            success_log=log_cross_signal_result,
            status_success="Cross-signal done",
        )        
        # Stage 13: Boundary-focused ELA / residual analysis depends on Cross-signal
        self.run_stage(
            state=state,
            name="Boundary-focused analysis",
            func=lambda: run_boundary_focus_analysis(
                image_path=state.selected_file,
                region_masks_payload=state.region_masks_payload,
                ela_payload=state.ela_payload,
                noise_payload=state.noise_payload,
                output_dir=state.output_dir,
            ),
            assign_attr="boundary_focus_payload",
            require=["region_masks_payload", "ela_payload", "noise_payload"],
            success_log=lambda p: self.log(
                "Boundary focus pattern: "
                f"{p.get('boundary_focus', {}).get('pattern', 'unknown')} | "
                f"combined_ratio="
                f"{p.get('boundary_focus', {}).get('comparative_features', {}).get('combined_boundary_ratio', 0.0):.3f} | "
                f"transition_score="
                f"{p.get('boundary_focus', {}).get('comparative_features', {}).get('transition_anomaly_score', 0.0):.3f}",
                "finding",
            ),
            status_success="Boundary-focused analysis done",
        )
        # Stage 14: Region-aware FFT
        self.run_stage(
            state=state,
            name="Region-aware FFT analysis",
            func=lambda: run_region_fft_analysis(
                image_path=state.prepared_images_payload["prepared"]["subject"]["path"],
                region_masks_payload=state.region_masks_payload,
                output_dir=state.output_dir,
            ),
            assign_attr="region_fft_payload",
            require=["region_masks_payload", "prepared_images_payload"],
            success_log=lambda p: self.log(
                "Region FFT pattern: "
                f"{p.get('region_fft', {}).get('pattern', 'unknown')} | "
                f"boundary_vs_background_fft_gap="
                f"{p.get('region_fft', {}).get('comparative_features', {}).get('boundary_vs_background_fft_gap', 0.0):.3f} | "
                f"subject_vs_background_fft_gap="
                f"{p.get('region_fft', {}).get('comparative_features', {}).get('subject_vs_background_fft_gap', 0.0):.3f}",
                "finding",
            ),
            status_success="Region-aware FFT analysis done",
        )
        # Stage 15: Region-segmentation-alignment
        self.run_stage(
            state=state,
            name="Segmentation alignment analysis",
            func=lambda: compute_segmentation_boundary_alignment(
                state.cross_signal_payload,
                state.region_masks_payload,
            ),
            assign_attr="segmentation_alignment_payload",
            require=["cross_signal_payload", "region_masks_payload"],
        )                
        # Stage 16: Subject-only texture 
        def _subject_prepared(state):
            prepared = state.prepared_images_payload or {}
            subject = prepared.get("prepared", {}).get("subject")
            if not subject:
                raise ValueError("Prepared subject image is missing from prepared_images_payload.")
            return subject

        self.run_stage(
            state=state,
            name="Subject texture consistency analysis",
            func=lambda: run_subject_texture_consistency_analysis(
                image_path=_subject_prepared(state)["path"],
                region_masks_payload=state.region_masks_payload,
                output_dir=state.output_dir,
                analysis_shape_hw=(
                    _subject_prepared(state)["height"],
                    _subject_prepared(state)["width"],
                ),
                analysis_scale=_subject_prepared(state).get("scale"),
            ),
            assign_attr="subject_texture_consistency_payload",
            require=["region_masks_payload", "prepared_images_payload"],
            success_log=lambda p: self.log(
                "Subject texture consistency pattern: "
                f"{p.get('subject_texture_consistency', {}).get('pattern', 'unknown')} | "
                f"soft_recurrence_score="
                f"{p.get('subject_texture_consistency', {}).get('scores', {}).get('soft_recurrence_score', 0.0):.3f} | "
                f"mean_neighbor_similarity="
                f"{p.get('subject_texture_consistency', {}).get('scores', {}).get('mean_neighbor_similarity', 0.0):.3f} | "
                f"p90_neighbor_similarity="
                f"{p.get('subject_texture_consistency', {}).get('scores', {}).get('p90_neighbor_similarity', 0.0):.3f}",
                "finding",
            ),
            status_success="Subject texture consistency analysis done",
        )
        # Stage 17: Subject-Process Asymmetry
        patch_params = get_subject_background_profile(state.analysis_mode)
        self.run_stage(
            state=state, 
            name="Subject process asymmetry analysis",
            func=lambda: run_subject_process_asymmetry_analysis(
                subject = patch_params.get("subject", 96),
                boundry = patch_params.get("boundry", 64),
                background = patch_params.get("background", 128),
                image_path=state.prepared_images_payload["prepared"]["subject"]["path"],
                subject_mask_path=state.region_masks_payload["region_masks"]["subject_mask_path"],
                boundary_band_path=state.region_masks_payload["region_masks"]["boundary_band_path"],
                background_mask_path=state.region_masks_payload["region_masks"]["background_mask_path"],
                output_dir=state.output_dir,
                analysis_shape_hw=(
                    state.prepared_images_payload["prepared"]["subject"]["height"],
                    state.prepared_images_payload["prepared"]["subject"]["width"],
                ),
                analysis_scale=state.prepared_images_payload["prepared"]["subject"].get("scale"),
                subject_texture_payload=state.subject_texture_consistency_payload,
                region_fft_payload=state.region_fft_payload,
            ),
            assign_attr="subject_process_asymmetry_payload",
            require=[
                "region_masks_payload",
                "prepared_images_payload",
            ],
            status_success="Subject process asymmetry analysis done",
        )
        # Stage 18: Subject material realism analysis
        profile = state.analysis_mode
        self.run_stage(
            state=state,
            name="Subject material realism analysis",
            func=lambda: run_subject_material_realism_analysis(
                profile=profile,
                image_path=state.prepared_images_payload["prepared"]["subject"]["path"],
                subject_mask_path=state.region_masks_payload["region_masks"]["subject_mask_path"],
                output_dir=state.output_dir,
                analysis_shape_hw=(
                    state.prepared_images_payload["prepared"]["subject"]["height"],
                    state.prepared_images_payload["prepared"]["subject"]["width"],
                ),
                analysis_scale=state.prepared_images_payload["prepared"]["subject"].get("scale"),
            ),
            assign_attr="subject_material_realism_payload",
            require=[
                "region_masks_payload",
                "prepared_images_payload",
            ],
            status_success="Subject material realism analysis done",
        )
        # 19: Patch spatial analysis (requires region masks)
        self.run_stage(
            state=state,
            name="Patch spatial analysis",
            func=lambda: run_patch_spatial_analysis(
                patch_similarity_payload=state.patch_similarity_payload,
                region_masks_payload=state.region_masks_payload,
                output_dir=state.output_dir,
            ),
            assign_attr="patch_spatial_payload",
            require=["patch_similarity_payload", "region_masks_payload"],
            success_log=lambda p: self.log(
                "Patch spatial pattern: "
                f"{p.get('patch_spatial', {}).get('pattern', 'unknown')} | "
                f"subject_ratio="
                f"{p.get('patch_spatial', {}).get('comparative_features', {}).get('subject_similarity_ratio', 0.0):.3f} | "
                f"boundary_ratio="
                f"{p.get('patch_spatial', {}).get('comparative_features', {}).get('boundary_similarity_ratio', 0.0):.3f} | "
                f"bridge_ratio="
                f"{p.get('patch_spatial', {}).get('comparative_features', {}).get('bridge_ratio', 0.0):.3f} | "
                f"bridge_weight_ratio="
                f"{p.get('patch_spatial', {}).get('comparative_features', {}).get('bridge_weight_ratio', 0.0):.3f} | "
                f"boundary_involvement_ratio="
                f"{p.get('patch_spatial', {}).get('comparative_features', {}).get('boundary_involvement_ratio', 0.0):.3f} | "
                f"boundary_correlated_ratio="
                f"{p.get('patch_spatial', {}).get('comparative_features', {}).get('boundary_correlated_ratio', 0.0):.3f} | "
                f"subject_localized_ratio="
                f"{p.get('patch_spatial', {}).get('comparative_features', {}).get('subject_localized_ratio', 0.0):.3f}",
                "finding",    
            ),
            status_success="Patch spatial analysis done",
        )
        # Stage 20: Compression history            
        self.run_stage(
            state=state,
            name="Compression-history analysis",
            func=lambda: run_compression_history_analysis(
                image_path=state.selected_file,
                output_dir=state.output_dir,
            ),
            assign_attr="compression_history_payload",
            success_log=lambda p: self.log(
                f"Compression-history pattern: {p.get('compression_history', {}).get('pattern', {}).get('compression_history_pattern')}",
                "finding"
            ),
            status_success="Compression-history analysis done",
        )                                                
        # Stage 21: Shared-boundary overlays
        if create_shared_boundary_overlays is not None:
            def overlay_func():
                paths = create_shared_boundary_overlays(
                    output_dir=state.output_dir,
                    selected_file=state.selected_file,
                    cross_signal_payload=state.cross_signal_payload,
                    ela_payload=state.ela_payload,
                    noise_payload=state.noise_payload,
                )
                if paths and state.cross_signal_payload is not None:
                    state.cross_signal_payload["shared_boundary_overlay_paths"] = paths
                return paths
            self.run_stage(
                state=state,
                name="Shared boundary overlays",
                func=overlay_func,
                require=["cross_signal_payload", "ela_payload", "noise_payload"],
                success_log=lambda p: self.log(f"Overlay paths: {p}", "finding"),
            )
        # 
        total_duration = time.perf_counter() - analysis_start
        print(f"[SignalLens] Full analysis completed in {total_duration:.2f}s")
        if state.run_recorder:
            state.run_recorder.log("Analysis run completed", "success")
            state.run_recorder.finalize(status="completed")
        return state