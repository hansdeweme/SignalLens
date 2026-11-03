# UI-2 legacy migration map

No stateful legacy control is instantiated twice. Existing attributes/callbacks remain on SignalLensGui, with widgets placed in the shell or its single owned Configure dialog.

|Existing component|Previous location|UI-2 location / reuse|Future migration / concern|
|---|---|---|---|
|SignalLensGui QWidget|Whole vertical form|QMainWindow retaining the same class and UI-1 owner methods|UI-3 fills workspace content; class/API preserved|
|File / Tools / Help QMenuBar|Top of form|Native QMainWindow menu bar, original actions|Archive redesign later; no workflow removed|
|drop_label and local-file drag/drop|Top drop target|Source card label; top-level drop handlers unchanged|Fit thumbnail is new; no advanced viewer yet|
|file_edit / pick_button|File row|Persistent command row on every destination|Path remains read-only/copyable; native file picker retained|
|analysis_mode_combo|Main form profile row|Single Configure dialog, original normal/subject_based values|Friendly selector labels can be refined later; values/config semantics unchanged|
|context_group + four chk_*|Main form|Same single controls in Configure dialog|Inputs remain launch snapshots; modal completion handling tested|
|run_button / clear_button|Main action rows|Persistent command row|UI-1 invocation invalidation and deferred worker ownership untouched|
|summary_box|160–220px capped pane|Overview narrative panel in vertical splitter|Retained long report view until UI-3 structured overview replaces it|
|log_box|Fixed-height main log|One collapsible execution section, reachable from all destinations|Dedicated stage/diagnostic UI later|
|status_label|Main label|Bounded native status footer, full text in tooltip/accessibility|No fake processing percentages; execution remains separate from confidence|
|osint_group + findings list / seven buttons|Permanent main-form area|Single Provenance page group, buttons arranged in three columns|Focused provenance/evidence editing later; revision commits unchanged|
|OSINTFindingDialog|Main modal|Same existing add/edit modal with scoped theme|Save/cancel/session capture retained; no new source verification|
|SettingsDialog + four tabs|Tools modal|Same dialog, shared theme; first three tabs scrollable|Same output/profile/JSON settings; native pickers and save/cancel retained|
|Decision Trace QTextBrowser modal|Tools menu|Tools action plus Reasoning page action; same selected-field data|Full policy/lineage explorer deferred; display palette only|
|Metadata module notes|Inside long narrative|Original narrative plus recorded Metadata note/state on Provenance|No raw tag browser or C2PA/watermark validation invented|
|Detector files / open_latest_audit_folder|Tools / external file manager|Original Tools action plus Image Forensics artifact-directory action|Dedicated artifact viewers/comparison in later image-forensics phase|
|open_json_button / open_output_folder|Main action row|Reports page, same current-revision export/retry path|No report-layout or content changes|
|Open Stored Summary|File menu|File menu plus Reports action|UI-1 non-destructive import identity and source-directory access preserved|
|Audit overview / cleanup / old-run / visual cleanup|Tools menu|Original Tools commands retained|UI-1 all-worker deletion guard retained; archive root inconsistency remains separate work|
|About / Known Limitations / Feedback|Help menu|Original Help commands retained|No feedback sent or external search performed during validation|

Source/detector pixel coordinate registration, advanced image comparison, evidence filters/tables, reasoning graphs and redesigned report contents are intentionally not implemented. Initial Evidence/Reasoning text views display existing structured fields and preserve access to the original narrative/trace rather than replacing working functionality with empty placeholders.
