# UI-2 design system

Dark-first, native PyQt6. `gui_design_system.py` is the source of truth for semantic colors, typography, spacing, geometry, lifecycle/log colors, scoped QSS and retained-rich-text display styling. No engine module contains new visual rules. `gui_components.py` supplies the reusable widgets. No dependency or raster asset was added.

## Color tokens

|Role|Dark token|
|---|---|
|Application background|#11161e|
|Navigation|#151c26|
|Primary panel|#1b2431|
|Secondary panel|#202c3b|
|Elevated surface|#29384b|
|Border|#53647b|
|Divider|#344258|
|Primary text|#edf2f8|
|Secondary text|#b9c6d8|
|Disabled text|#8795a8|
|Accent|#8cccf2|
|Hover|#27394d|
|Selected|#233c53|
|Focus|#a3d9fa|
|Success, execution only|#9cdbb7|
|Warning / limited execution|#f1ce82|
|Error / failed execution|#f3abae|
|Neutral / unknown|#bfcbdd|
|Unavailable|#b7b3cf|

Completed is an execution state, not an authenticity verdict. ConfidenceIndicator displays the exact recorded tier with the same neutral typography/border for High, Medium, Low, Inconclusive and Unavailable. It never converts a tier to a percentage or uses a suspicious/benign color branch. Provenance verification is an explicitly named metadata value, and detector availability includes its recorded status/reason. These concepts do not share one ambiguous truth badge.

## Typography and layout

Segoe UI is the primary Windows font; Consolas is used for copyable technical metadata. Native point sizes: display 20, section 15, card 11, body/secondary 10, caption/technical 9. Bold/semibold establishes hierarchy. Existing report text is rendered using Qt-supported rich text; browser CSS variables/media queries are removed only from its GUI projection. Report files and frozen result HTML remain unchanged.

Spacing scale: 4, 8, 12, 16, 24, 32 logical pixels. Standard panel padding is 16; panel/section gaps generally 12; navigation padding/gaps 8. Geometry tokens: 6px radius, 1px border, 32px control height, 18px icons, navigation initially 208px (184–280px), minimum content window 1040×720, default 1280×900, source preview minimum 160px. Indicator 5×10px insets are centralized optical/control-metric exceptions. Root layouts remain stretchable; old main-window fixed summary/log proportions are removed.

## Component and interaction styling

Panels are flat bordered containers, not decorative cards/charts. Navigation uses native standard icons plus text, one checked destination and a visible accent edge. Hover, pressed, disabled, selection and focus rules live in centralized QSS. Ctrl+1…6 selects destinations; native Tab/Shift+Tab and button activation remain available. Focus uses a 2px visible outline. Metadata values support mouse and keyboard text selection; retained QTextEdit/QPlainTextEdit/QLineEdit controls preserve native copy/paste and context menus.

Lifecycle indicators include pending, analyzing, completed, failed, cancelled, unavailable and unknown. An indeterminate progress bar is shown only while analyzing: no fabricated percentage or stage total is displayed. Long status messages use explicit ellipsis, while text(), accessible name and tooltip retain the full UI-1 message. The footer is bounded rather than expanding with long text.

## Scope and accessibility

`apply_theme` styles a window and its owned widgets using a palette plus root-local QSS; QApplication is not globally restyled. Native file pickers and nonclient window decoration retain OS behavior. Settings and OSINT dialogs use the same theme without changing save/cancel semantics. Scrollable profile tabs prevent tall configuration forms from becoming inaccessible.

Tests calculate ≥4.5:1 contrast for primary/secondary text and active semantic text on both main background and panel surfaces. Statuses remain named, confidence remains textual, and color is supplemental. Font sizes are points; spacing/sizes are Qt logical pixels. Offscreen tests register installed Windows fonts because that platform does not enumerate them like the native Windows plugin. Native primary-monitor rendering was checked at DPR 1.0 / 96 logical DPI. Other DPI settings and screen readers remain unverified; no claim of complete accessibility certification is made.

## Future light mode

A complete LIGHT ColorTokens palette can be injected into apply_theme/stylesheet and the indicator constructors. The same semantic names and component architecture support a future light preference. UI-2 ships dark-first only: no user-facing theme switch or light-mode validation claim. A future preference should pass one palette consistently through shell/components/dialogs and verify every visual state rather than changing scattered widget colors.
