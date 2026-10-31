SignalLens 0.0.1-beta
README_FIRST.txt

Thank you for testing SignalLens.

SignalLens is a local visual-forensics tool for analyzing images using multiple forensic signals. It is designed to help users understand whether an image shows signs of camera-origin photography, editing, synthetic generation, computational processing, or conflicting evidence.

SignalLens is not a truth machine.

Its output should be interpreted as forensic reasoning based on available signals, not as final proof that an image is real, edited, synthetic, or AI-generated.

------------------------------------------------------------
1. What SignalLens does
------------------------------------------------------------

SignalLens analyzes an image across multiple forensic domains, including:

- metadata and provenance signals
- camera/sensor-origin indicators
- compression and ELA patterns
- frequency-domain structure
- patch similarity and recurrence
- subject/background and boundary-region behavior
- texture consistency and material realism
- reasoning and decision traces

The goal is not only to produce a conclusion, but to explain why that conclusion was reached.

-------------------------------------------------------------
2. ExifTool
-------------------------------------------------------------
To disclose the metadata embedded in image files, SignalLens makes use of ExifTool.
ExifTool by Phil Harvey can be downloaded from the official website: https://exiftool.org/

For user convinience it is included in the SignalLens installation package.
Once SignalLens is unpacked, this will add ExifTool.exe and also a child folder exiftool_files, which both should remain in place. This way SignalLens after unpacking is ready to use.

------------------------------------------------------------
3. Quick start
------------------------------------------------------------

1. Start SignalLens.
2. Select (Choose Image button) or drag-and-drop an image.
3. Choose the relevant analysis/profile options (Patch Profile and/or Contextual Info).
4. Run the analysis.
5. Review the summary shown in the GUI.
6. Use Tools → Decision Trace for the reasoning path.
7. Use Tools → Open Latest Audit Folder to inspect the full evidence folder.

Supported image types include common formats such as JPG, PNG, WEBP, TIFF, BMP, HEIC and HEIF, depending on local library support.

-------------------------------------------------------------
4. Smart App Control / SmartScreen
-------------------------------------------------------------
SignalLens 0.0.1-beta is currently an unsigned early-access build. 
Windows may warn that the publisher cannot be verified, or Smart App Control may block the executable.
Only run SignalLens if you intentionally downloaded it from the official SignalLens / Code2Trade download page.

If Windows' Smart App Control blocks the app, you may need to adjust Windows Security settings. 
Do this by opening Windows Security | App & Browser Control | Smart App Control.   

------------------------------------------------------------
5. Where results are saved
------------------------------------------------------------

SignalLens creates a local audit trail for every analyzed image.
By default, results are written to:

    .\analyzed\

Each image gets its own subfolder. This folder may contain visual overlays, heatmaps, masks, FFT outputs, metadata files, JSON signal data, logs, summaries, and reasoning traces.

A single analysis can produce many files and may use considerably more storage than the original image.
You can inspect audit-trail storage usage via:

    Tools → Audit Trail Overview

You can clean older or heavy audit trails via the cleanup options in the Tools menu.

------------------------------------------------------------
6. How to interpret the result
------------------------------------------------------------

SignalLens does not simply answer “real” or “AI”.
It tries to identify the most plausible forensic reading based on the available evidence.

Important principles:

- A real image can contain suspicious-looking artifacts.
- A synthetic image can imitate photographic structure.
- Edited, generated, and camera-origin regions can coexist.
- Metadata can be helpful, missing, stripped, edited, or spoofed.
- Visual overlays are diagnostic aids, not standalone proof.
- Conflicting evidence is meaningful and should not be ignored.

Always read the summary and, where relevant, the decision trace.

------------------------------------------------------------
7. Known limitations
------------------------------------------------------------

SignalLens is currently beta software.
Current limitations include:
- No absolute authenticity guarantee.
- Hybrid images remain difficult.
- Smartphone computational photography can mimic synthetic artifacts.
- Metadata can be incomplete or misleading.
- Some forensic modules may be sensitive to image size, compression, resizing, and content type.
- Thresholds and reasoning rules may change in future versions.

Use SignalLens as an analytical support tool, not as a final authority.

------------------------------------------------------------
8. Privacy
------------------------------------------------------------

SignalLens is designed as a local-first tool.
Images are analyzed locally on your machine. 
SignalLens does not require uploading images to an external service for normal analysis.

If you choose to send feedback, only the information you submit through the feedback form is shared.
Do not send private, sensitive, or third-party images unless you have permission to do so.

------------------------------------------------------------
9. Feedback
------------------------------------------------------------

Beta feedback is very useful.
Use:

    Help → Send Feedback

Useful feedback includes:
- SignalLens version
- operating system
- image type tested
- what result you expected
- what result SignalLens produced
- what was useful
- what was confusing
- whether the audit trail helped you understand the result

If relevant, you may mention the audit folder path, but do not share private image data unless you explicitly intend to.

------------------------------------------------------------
10. Version
------------------------------------------------------------

SignalLens version:
    0.0.1-beta

When reporting bugs or unexpected results, please include the version number shown in:
    Help → About SignalLens

and, if possible, the version footer in the generated summary files.

------------------------------------------------------------
11. Disclaimer
------------------------------------------------------------

SignalLens provides forensic indicators and reasoning support. It does not provide legal, journalistic, investigative, or scientific certainty by itself.

Do not use SignalLens as the sole basis for serious accusations, publication decisions, legal claims, employment decisions, or other high-impact judgments.

Use it to inspect evidence, understand uncertainty, and support further expert review.

------------------------------------------------------------
12. Copyright and license
------------------------------------------------------------

Copyright (c) 2025, 2026 Hans De Weme.

SignalLens is part of an ongoing project exploring explainable visual forensics and synthetic media analysis.