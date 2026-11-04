# UI-7 accessibility review

Fresh native mouse and keyboard checks used actual 100% and 150% displays. Ctrl+1 through Ctrl+6 navigate the workspace shell. Focus outlines are visible on navigation, comparison modes and command buttons. Escape cancels the configuration, OSINT Finding and Settings modals and returns control to the investigation. The file chooser accepted a full path and its Open button loaded the intended stored result. Native accessibility trees expose names for source preview/zoom, selected source path, investigation state and core commands.

State is expressed in text: Completed / No image, current result availability, result/annotation revision, Unverified metadata, unsupported cryptographic verification, unavailable fields, export saved/failure and confidence tiers. Interpretation does not depend solely on color. Source hashes and paths remain selectable/copyable in detail views. Evidence and metadata use table/selected-detail views rather than requiring truncated cells to convey full content. No new animation was introduced.

Limits: exhaustive keyboard-only traversal of every tab/control, Narrator/JAWS speech output, Windows high contrast, magnifier and reduced-motion preferences were NOT TESTED. Helper accessibility trees occasionally lagged the currently displayed stacked page or reported a different file-dialog child; screenshots and explicit mouse focus were used to recover. That is a validation-tool limitation, not proof of a product screen-reader defect. Full assistive-technology sign-off remains open.

Fresh regression coverage continues to protect accessible viewer names, keyboard navigation, dialog availability and small-window reachable controls. These checks do not replace native screen-reader review.
