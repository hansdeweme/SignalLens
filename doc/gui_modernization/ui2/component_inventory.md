# UI-2 reusable component inventory

|Component / module|Responsibility and current use|
|---|---|
|ColorTokens / TypographyTokens / GeometryTokens; gui_design_system.py|Immutable central palette, type/spacing/geometry vocabulary. DARK/default and injectable LIGHT palettes.|
|apply_theme / stylesheet / font / indicator_style / log_color; same|Root-scoped native styling and supported shared indicator/log treatment. No forensic rule import.|
|display_html; same|GUI-only legacy rich-text projection: contrast-safe colors and neutral confidence, without changing stored/exported text or reasoning.|
|SectionHeader; gui_components.py|Heading, description, optional actions and status text. Used on every destination and Configure dialog.|
|Panel; same|Consistent bordered container, padding, optional title/toolbar and flexible body layout.|
|StatusIndicator; same|Named investigation/execution lifecycle state, accessible label and semantic color. Independent of confidence.|
|ConfidenceIndicator; same|Exact supplied tier, neutral styling for all values, explicit unavailable and non-probability tooltip.|
|EmptyState; same|Heading/reason for empty, running, missing recorded content or unavailable/error states. No negative-evidence inference.|
|NavigationItem; same|Icon/text button, checked active state, keyboard focus, hover and optional textual marker. No session/result ownership.|
|MetadataRow; same|Named copyable technical value; mouse/keyboard selection, unknown explicit. Used for provenance and report identity/validity.|
|CollapsibleSection; same|Native disclosure button and content visibility; existing execution log.|
|SourcePreview; same|Fit-only bounded thumbnail, session/invocation-keyed reset and unavailable fallback. No detector comparison/overlays.|
|StatusMessage; same|Bounded single-line status with ellipsis, full text/accessibility/tooltip retained.|
|scroll_area / label; same|Consistent scroll surfaces and plain-text label roles; avoid unintended rich-text interpretation in structured values.|
|WorkspaceShell; gui_workspace.py|One central native workspace, navigation, initial pages, retained controls and identity-checked snapshot projection.|
|restore_workspace / save_workspace / ensure_visible; gui_workspace_state.py|Content-free versioned geometry/destination/splitter preferences and off-screen recovery.|

Qt-native standard icons are reused. No image assets, web engine, chart dependency, detector-specific widget framework or application-wide stylesheet was introduced. Lifecycle/availability, confidence, provenance and evidence roles remain explicitly distinct. Existing dialogs retain their original classes and business handlers.
