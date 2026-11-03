# Decoded reference artifact inventory

Actual stored production paths are in reference_validation.json. Dimensions below are decoded native width × height; D/E rows may have no raster. B/UNKNOWN rows are independently inspectable spatial candidates, not demonstrated transforms.

| Reference | Producer / field | Type | Dimensions | Registration | Evidence IDs |
|---|---|---|---|---|---|
| instagram | ela/ela_image_path | A | 720 × 1280 | REGISTERED | Not recorded |
| instagram | ela/ela_hotspot_overlay_original_path | A | 720 × 1280 | REGISTERED | Not recorded |
| instagram | ela/ela_hotspot_overlay_diff_path | A | 720 × 1280 | REGISTERED | Not recorded |
| instagram | ela/recompressed_jpeg_path | A | 720 × 1280 | REGISTERED | Not recorded |
| instagram | noise/residual_image_path | A | 720 × 1280 | REGISTERED | Not recorded |
| instagram | noise/noise_overlay_original_path | A | 720 × 1280 | REGISTERED | Not recorded |
| instagram | noise/noise_overlay_residual_path | A | 720 × 1280 | REGISTERED | Not recorded |
| instagram | sensor_origin/sensor_overlay_path | B | 720 × 1280 | UNKNOWN | sensor_origin:camera_like_acquisition_supported |
| instagram | cfa_demosaic/overlay_path | B | 720 × 1280 | UNKNOWN | cfa_demosaic:weak_camera_cfa_supported |
| instagram | person_subject_mask/structured_result | D | None × None | NOT_APPLICABLE | Not recorded |
| instagram | region_masks/subject_mask_path | B | 576 × 1024 | TRANSFORMABLE | Not recorded |
| instagram | region_masks/boundary_band_path | B | 576 × 1024 | TRANSFORMABLE | Not recorded |
| instagram | region_masks/background_mask_path | B | 576 × 1024 | TRANSFORMABLE | Not recorded |
| instagram | region_segmentation/structured_result | D | None × None | NOT_APPLICABLE | Not recorded |
| instagram | segmentation_alignment/structured_result | D | None × None | NOT_APPLICABLE | Not recorded |
| instagram | boundary_focus/boundary_focus_preview_path | B | 576 × 1024 | UNKNOWN | boundary_focus:boundary_focused_processing_mismatch |
| instagram | fft/fft_grid_overlay_path | B | 576 × 1024 | UNKNOWN | fft:possible_decoder_grid_signature |
| instagram | fft/fft_grid_response_path | B | 576 × 1024 | UNKNOWN | fft:possible_decoder_grid_signature |
| instagram | fft/fft_multi_grid_overlay_path | B | 576 × 1024 | UNKNOWN | fft:possible_decoder_grid_signature |
| instagram | fft/fft_multi_grid_response_path | B | 576 × 1024 | UNKNOWN | fft:possible_decoder_grid_signature |
| instagram | fft/fft_peakmap_image | C | 576 × 1024 | NOT_APPLICABLE | fft:possible_decoder_grid_signature |
| instagram | fft/fft_radial_profile_image | C | 1120 × 630 | NOT_APPLICABLE | fft:possible_decoder_grid_signature |
| instagram | fft/fft_spectrum_image | C | 576 × 1024 | NOT_APPLICABLE | fft:possible_decoder_grid_signature |
| instagram | region_fft/background_input | B | 576 × 1024 | UNKNOWN | Not recorded |
| instagram | region_fft/boundary_input | B | 534 × 1024 | UNKNOWN | Not recorded |
| instagram | region_fft/subject_input | B | 528 × 1024 | UNKNOWN | Not recorded |
| instagram | subject_boundary/subject_boundary_overlay_path | B | 720 × 1280 | UNKNOWN | subject_boundary:possible_subject_background_segmentation_artifact |
| instagram | subject_texture_consistency/background_texture_focus_mask_overlay | B | 576 × 1024 | UNKNOWN | subject_texture_consistency:subject_internal_stochastic_repetition |
| instagram | subject_texture_consistency/subject_texture_consistency_overlay | B | 576 × 1024 | UNKNOWN | subject_texture_consistency:subject_internal_stochastic_repetition |
| instagram | subject_texture_consistency/subject_texture_focus_mask_overlay | B | 576 × 1024 | UNKNOWN | subject_texture_consistency:subject_internal_stochastic_repetition |
| instagram | subject_process_asymmetry/structured_result | D | None × None | NOT_APPLICABLE | subject_process_asymmetry:subject_surface_regularization_dominant |
| instagram | subject_process_asymmetry/subject_process_asymmetry_overlay | B | 576 × 1024 | UNKNOWN | subject_process_asymmetry:subject_surface_regularization_dominant |
| instagram | subject_material_realism/structured_result | D | None × None | NOT_APPLICABLE | subject_material_realism:subject_material_regularization_dominant |
| instagram | subject_material_realism/subject_material_realism_overlay | B | 576 × 1024 | UNKNOWN | subject_material_realism:subject_material_regularization_dominant |
| instagram | patch_similarity/patch_similarity_heatmap | B | 432 × 768 | UNKNOWN | patch_similarity:possible_synthetic_texture_repetition |
| instagram | patch_similarity/patch_similarity_overlay | B | 432 × 768 | UNKNOWN | patch_similarity:possible_synthetic_texture_repetition |
| instagram | patch_spatial/structured_result | D | None × None | NOT_APPLICABLE | patch_spatial:subject_internal_synthetic_recurrence |
| instagram | compression_history/compression_overlay_path | B | 720 × 1280 | UNKNOWN | compression_history:localized_compression_inconsistency |
| instagram | cross_signal/ela | B | 720 × 1280 | UNKNOWN | cross_signal:partial_hotspot_convergence |
| instagram | cross_signal/noise | B | 720 × 1280 | UNKNOWN | cross_signal:partial_hotspot_convergence |
| instagram | cross_signal/original | B | 720 × 1280 | UNKNOWN | cross_signal:partial_hotspot_convergence |
| midjourney | ela/ela_image_path | A | 1232 × 928 | REGISTERED | Not recorded |
| midjourney | ela/ela_hotspot_overlay_original_path | A | 1232 × 928 | REGISTERED | Not recorded |
| midjourney | ela/ela_hotspot_overlay_diff_path | A | 1232 × 928 | REGISTERED | Not recorded |
| midjourney | ela/recompressed_jpeg_path | A | 1232 × 928 | REGISTERED | Not recorded |
| midjourney | noise/residual_image_path | A | 1232 × 928 | REGISTERED | Not recorded |
| midjourney | noise/noise_overlay_original_path | A | 1232 × 928 | REGISTERED | Not recorded |
| midjourney | noise/noise_overlay_residual_path | A | 1232 × 928 | REGISTERED | Not recorded |
| midjourney | sensor_origin/sensor_overlay_path | B | 1232 × 928 | UNKNOWN | sensor_origin:camera_like_acquisition_supported |
| midjourney | cfa_demosaic/overlay_path | B | 1232 × 928 | UNKNOWN | Not recorded |
| midjourney | person_subject_mask/structured_result | D | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | region_masks/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | region_segmentation/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | segmentation_alignment/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | boundary_focus/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | fft/fft_grid_overlay_path | B | 1024 × 771 | UNKNOWN | fft:possible_decoder_grid_signature |
| midjourney | fft/fft_grid_response_path | B | 1024 × 771 | UNKNOWN | fft:possible_decoder_grid_signature |
| midjourney | fft/fft_multi_grid_overlay_path | B | 1024 × 771 | UNKNOWN | fft:possible_decoder_grid_signature |
| midjourney | fft/fft_multi_grid_response_path | B | 1024 × 771 | UNKNOWN | fft:possible_decoder_grid_signature |
| midjourney | fft/fft_peakmap_image | C | 1024 × 771 | NOT_APPLICABLE | fft:possible_decoder_grid_signature |
| midjourney | fft/fft_radial_profile_image | C | 1120 × 630 | NOT_APPLICABLE | fft:possible_decoder_grid_signature |
| midjourney | fft/fft_spectrum_image | C | 1024 × 771 | NOT_APPLICABLE | fft:possible_decoder_grid_signature |
| midjourney | region_fft/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | subject_boundary/subject_boundary_overlay_path | B | 1232 × 928 | UNKNOWN | subject_boundary:image_edge_boundary_observation |
| midjourney | subject_texture_consistency/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | subject_process_asymmetry/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | subject_material_realism/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | patch_similarity/patch_similarity_heatmap | B | 768 × 578 | UNKNOWN | patch_similarity:possible_clone_reuse |
| midjourney | patch_similarity/patch_similarity_overlay | B | 768 × 578 | UNKNOWN | patch_similarity:possible_clone_reuse |
| midjourney | patch_spatial/structured_result | E | None × None | NOT_APPLICABLE | Not recorded |
| midjourney | compression_history/compression_overlay_path | B | 1232 × 928 | UNKNOWN | Not recorded |
| midjourney | cross_signal/ela | B | 1232 × 928 | UNKNOWN | cross_signal:strong_hotspot_convergence |
| midjourney | cross_signal/noise | B | 1232 × 928 | UNKNOWN | cross_signal:strong_hotspot_convergence |
| midjourney | cross_signal/original | B | 1232 × 928 | UNKNOWN | cross_signal:strong_hotspot_convergence |
