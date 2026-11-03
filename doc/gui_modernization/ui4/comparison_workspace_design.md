# Comparison workspace

The existing Image Forensics navigation destination now hosts ImageForensicsWorkspace. It retains the single UI-1 session owner and the UI-2 shell. A detector tree, source/artifact panels and a context/details area use three adjustable splitters. Splitter sizes persist as content-free workspace preferences. Artifact selections and comparison modes do not persist across investigation changes.

Independent mode provides separate fit/reset, zoom and drag-pan controls. Synchronized mode transforms artifact scenes into source units and links center/scale with a recursion guard. Overlay adds only an eligible raster to the source scene, with adjustable opacity, a dashed extent and an explanatory legend. Opacity is a display blend, not a probability. Controls are gated by both verified metadata and successfully decoded previews.

Detector groups expose availability and registration in item labels/tooltips. Selecting a group clears the previous artifact rather than retaining misleading context. Shared physical outputs appear once; other consumers receive structured reference rows. Details show detector observation, reliability, stage status, evidence IDs and hypothesis IDs. A metadata dialog provides the full descriptor and existing stage availability. Evidence, Reasoning and Provenance buttons navigate within the active investigation; they do not imply an invented row-level association.

The UI-2 theme now includes tree selection/focus and horizontal scrollbars. Scale text occupies its own row for narrow comparison panels. Source and artifact viewers preserve aspect ratio, expose accessible control names and share UI-3's bounded preview loader. Artifact folders use the existing shell action. Overview and Reports retain their existing implementations.
