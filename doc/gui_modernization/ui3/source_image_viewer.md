# Source-image viewer

`SourceImageViewer` uses a QGraphicsView with a single QPixmap item. It preserves aspect ratio, honors orientation, fits on initial load/resize and exposes Zoom out, Zoom in and Fit / Reset buttons. Zoom is relative to the fit scale, clamped to 0.25–8×; drag pans when zoomed. It is a display preview, not a full-resolution pixel-inspection tool. Resizing while zoomed preserves the zoomed view; reset refits to the current viewport. The caption reports encoded source dimensions, which can precede EXIF rotation.

## Loading and memory

Header inspection is synchronous. Only files at most 256 KiB **and** 262,144 pixels use the short synchronous path. Photographs/large hashes and decodes run on a dedicated two-thread QThreadPool, independent of analysis workers. Hashing streams 1 MiB chunks. QImage is created in workers; QPixmap and scene changes occur only on the GUI thread. A preview is downsampled to at most 2048 pixels on its longest edge. Sources above 100 megapixels return a clear preview-limit message. Qt's decoder allocation safeguards also remain in place.

Retained storage is one bounded image/pixmap; the scene shares Qt image storage. Some image codecs may temporarily decode at source resolution before scaling, so 2048 is a retained-preview bound, not a promise that every codec uses only preview-sized temporary memory. Only two preview jobs decode simultaneously. Pending requests can finish after supersession but cannot populate an obsolete view. No dependency is installed and no source file is written.

## Identity and failure handling

Every request includes a monotonic serial, source path, session/invocation identity and expected recorded SHA-256. Hash mismatch rejects the image instead of placing changed pixels beside historical findings. File size, modification time and creation/change timestamp are checked before/after read and again on delivery. The viewer checks the loaded file's stat fingerprint every two seconds and on snapshot rebinding; changed/missing files clear displayed pixels and disable zoom with a reselect instruction. This is change detection, not continuous adversarial file-integrity monitoring.

On new selection, the image immediately clears. Queued completion must match the current request exactly. A verified unchanged preview can be reused across invocation/annotation updates for the same path/hash/fingerprint, avoiding repeat decode. No historical hash is invented for old summaries; a preview without a recorded hash explicitly labels its historical identity unrecorded. Missing/corrupt/changed/oversized images show an error while recorded findings remain accessible.

Jobs contain values and a signal carrier, never QWidget references. Qt disconnects the receiver when a viewer is deleted. Pool jobs do not own analysis state or bypass UI-1's deferred analysis-worker close policy. Running decoder calls are not forcibly terminated; they may finish during shutdown. Full-resolution comparison, overlays, ROI and synchronized viewers remain UI-4 work.
