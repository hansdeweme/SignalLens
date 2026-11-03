# Spatial registration

Coordinates use image edges: bounds [0,width] × [0,height], with pixel (i,j) centered at (i+.5,j+.5). The affine source-to-artifact map is `(a*x+c*y+tx, b*x+d*y+ty)`. The determinant must be finite and nonzero. The inverse maps the selected artifact into a source-coordinate scene. Preview pixels first scale to native artifact dimensions, then through this inverse. Both linked canvases therefore share source units, rather than scrollbar positions.

ELA and noise operate on PIL RGB encoded source pixels, with no crop or transpose. Only a verified source/run, orientation 1 and exact full-source dimensions permit REGISTERED identity geometry. ELA difference and absolute luminance residual have explicit display-blend legends; annotated variants can synchronize but cannot be newly overlaid.

Accepted reliable/limited person and derived region masks use a documented gatekeeper full-frame resize. Their affine scale is artifact_width/source_width and artifact_height/source_height. Recorded geometry must match decoded geometry. They permit synchronization and retain independent mask rendering; no new categorical-mask overlay semantics are asserted. Approximate/rejected masks cannot synchronize.

FFT spectra, radial plots and peak maps are NOT_APPLICABLE. Prepared regional inputs lack crop origins. Patch, sensor, CFA, compression and compound boundary outputs remain UNKNOWN. EXIF orientations other than 1 disable registration until a complete producer/viewer orientation map is implemented. Matching raster dimensions never prove spatial correspondence.

Tests verify identity, anisotropic scale/crop offsets and quarter-turn inverse mapping to 1e-9 source units, bounded-preview-to-native mapping, linked view scale equality and view centers within two display pixels (integer scrollbars and viewport centers). This is display registration validation, not detector calibration. Continuous coordinates near viewport edges are constrained by QGraphicsView bounds. Zoom remains a bounded display operation, not a full-resolution pixel sampler.
