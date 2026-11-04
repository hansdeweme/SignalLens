# Historical investigation compatibility

UI-1 continues to load stored summaries/current-report pointers, validate structures, assign fresh import identity and preserve historical investigation data. UI-6 does not rewrite stored summaries or source images. Preview construction copies the current session snapshot; explicit exports and controlled validation annotations go to new directories.

Metadata comes first from recorded signals/observations in the summary. If the original raw watchlist payload can be verified against the run manifest and source hash, it supplies additional recorded fields. Missing files, mismatched identity, absent hashes, excessive payload size or unreadable JSON leave the summary evidence visible with a recovery limitation. No filename search in another run or fresh ExifTool call fills gaps.

A missing verification field remains Unknown. An unavailable extraction is distinguished from a completed extraction with missing provenance, and neither establishes authenticity or synthetic creation. Current backend cryptographic verification is unsupported. Legacy stored flags are reported as recorded flags rather than independently authenticated claims.

Narrative-only stored results retain their exact text through the existing escaped HTML fallback and the TXT/JSON exporter. Structured confidence, hypothesis, lineage or metadata records are not fabricated. Partial reasoning text uses the existing publisher's recorded-fields fallback. No unsupported format is offered, and report readiness means a valid completed snapshot can be saved, not that all optional forensic records exist.
