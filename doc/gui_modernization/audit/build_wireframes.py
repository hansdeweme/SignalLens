"""Build static SVG/HTML UI-0 concepts; render using installed PyQt6 only."""
from html import escape
from pathlib import Path
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QImage, QPainter, QFontDatabase
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication

OUT = Path(__file__).resolve().parent / 'wireframes'
OUT.mkdir(exist_ok=True)
app = QApplication([])
QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')

SCREENS = [
    ('A_entry', 'A — Application entry / empty state', 'Overview', [
        (205, 122, 690, 350, 'Begin an investigation', ['SOURCE IMAGE — EMPTY', 'Drop a supported image here', 'or choose Open Image', '', 'No findings until analysis completes.', 'Source files remain unchanged.']),
        (915, 122, 340, 350, 'Analysis configuration', ['Profile: Standard  [v]', '', 'Optional analyst context:', '[ ] Natural repetition', '[ ] Decorative geometry', '[ ] Smartphone processing', '[ ] Display-origin candidate', '', 'Advanced settings…']),
        (205, 492, 1050, 170, 'Ready to begin', ['1  Choose image     2  Review configuration     3  Run analysis', '', 'Open Image [action]       Run [disabled]', 'Local analysis. Reports contain forensic interpretations and limitations.']),
    ]),
    ('B_overview', 'B — Investigation overview', 'Overview', [
        (205, 122, 510, 420, 'Source image · illustrative file', ['[ Source preview occupies this area ]', '', 'Fit / 100%      Dimensions / prepared scale', '', 'Image remains accessible across evidence views.', 'No fabricated image or detector output.']),
        (735, 122, 520, 205, 'Primary forensic interpretation', ['Localized-processing concern [example only]', 'Hypothesis: Localized editing', 'Confidence: [backend tier]', '', 'Why this tier → Reasoning', 'This finding does not establish generative AI.']),
        (735, 347, 520, 195, 'Separate hypothesis assessments', ['Synthetic origin       [tier / explanation]', 'Localized editing      [tier / explanation]', 'Camera acquisition     [tier / explanation]', '', 'Rows show actual returned assessments only.']),
        (205, 562, 1050, 100, 'Coverage and limitations — always visible', ['[backend stage coverage]   [unavailable reasons]', 'Camera-compatible evidence does not authenticate acquisition history.']),
    ]),
    ('C_image_forensics', 'C — Forensic image inspection', 'Image Forensics', [
        (205, 122, 225, 420, 'Existing detector artifacts', ['ELA / difference', 'Residual / noise', 'Patch pairs / recurrence', 'FFT / spectrum / profile', 'Region FFT', 'Boundary / masks', 'Texture / material', 'Sensor / CFA', 'Compression', '', 'Each entry: status + reason']),
        (450, 122, 392, 420, 'Source · fit / 100% / zoom / pan', ['[ Source image viewport ]', '', 'Coordinates: source pixel space', '', 'Link views only with validated', 'scale / crop transform.']),
        (862, 122, 393, 420, 'Selected output · named input role', ['[ Existing artifact viewport ]', '', 'Output type and dimensions', 'Baked overlay or raw map label', '', 'Spectrum views use frequency', 'coordinates, not source pixels.']),
        (205, 562, 1050, 100, 'Detector interpretation / limitations', ['[authoritative note]     Evidence details →', 'No anomaly, inconclusive and unavailable are distinct states.']),
    ]),
    ('D_evidence', 'D — Evidence Explorer', 'Evidence', [
        (205, 122, 1050, 65, 'Filter without changing forensic results', ['Hypothesis [Localized editing v]    Role [All v]    Search [                ]']),
        (205, 207, 680, 335, 'Observations · sortable, selectable, copyable', ['ROLE          OBSERVATION                    STATUS', 'Supporting    [backend label]                 [status]', 'Contradicting [backend label, if returned]    [status]', 'Moderating    [backend label]                 [status]', 'Contextual    [analyst or metadata context]  [status]', '', 'Stable evidence IDs; missing values shown as —', 'Same observation can have another role for another hypothesis.']),
        (905, 207, 350, 335, 'Selected evidence', ['[label + evidence ID]', 'Role for selected hypothesis', '', '[backend interpretation]', '[reliability limitation]', '', 'Source / detector / artifact', 'Open available visualization →']),
        (205, 562, 1050, 100, 'Available ancestry / explanation', ['[source measurement IDs] → [derived interpretation]', 'Shared ancestry is not independent corroboration. Do not count visible rows as votes.']),
    ]),
    ('E_reasoning', 'E — Reasoning inspection', 'Reasoning', [
        (205, 122, 270, 420, 'Reasoning navigation', ['Primary selection reason', 'Hypothesis assessments', 'Candidate route evaluations', 'Confidence policy', 'Corroboration gates', 'Numerical ledger', 'Available ancestry', '', 'Raw JSON / text trace →']),
        (495, 122, 760, 205, 'Confidence-policy decision · selected hypothesis', ['Assigned tier: [backend value]   Rule: [backend ID]', '', '[authoritative rationale / reliability limitations]', 'Supporting / contrary / moderating evidence IDs', '', 'No tier recalculation in the presentation layer.']),
        (495, 347, 760, 195, 'Candidate routes and corroboration', ['Route / candidate      Evaluated result      Explanation', '[existing trace row]   [recorded fields]     [recorded reason]', '', 'Gate kind: compound or distinct-source requirement', 'Ancestry / shared sources / eligibility / limitations']),
        (205, 562, 1050, 100, 'Advanced numerical details [expandable]', ['Heuristic contributions / adjustments / transforms — not probabilities', 'Optional shadow analysis labeled diagnostic; absent lineage says not recorded.']),
    ]),
    ('F_provenance', 'F — Provenance and metadata', 'Provenance', [
        (205, 122, 1050, 110, 'Provenance state: [backend declaration / missing / ambiguous state]', ['Metadata authenticity: NOT VERIFIED in current backend path', 'Presence of C2PA-related metadata is not cryptographic validation.']),
        (205, 252, 650, 290, 'Metadata fields and evidence', ['TAG / SIGNAL          VALUE                 SOURCE', '[recorded tag]         [recorded value]      [extractor]', '[generation signal]   [if recorded]         [metadata]', '[camera fields]        [if recorded]         [metadata]', '', 'Selectable raw values + controlled interpretation', 'Missing metadata is not positive synthetic evidence.']),
        (875, 252, 380, 290, 'Manual OSINT records', ['Review status: [backend record]', 'Provider / URL / first-seen estimate', 'Source type / analyst notes', '', 'Add / Edit finding', 'Open external search provider', '', 'No automatic search or upload implied.']),
        (205, 562, 1050, 100, 'Interpretive scope / report revision', ['Declarations may support one hypothesis and contextualize another.', 'OSINT changes create a visible summary/report revision; analyst input stays attributed.']),
    ]),
]

def text_at(x, y, value, size=14, weight='normal', fill='#334155'):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(value)}</text>'

for name, title, active, panels in SCREENS:
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="740" viewBox="0 0 1280 740">',
           '<rect width="1280" height="740" fill="#e9edf2"/>',
           '<g font-family="Segoe UI">',
           '<rect x="0" y="0" width="1280" height="70" fill="#d4dbe4"/>',
           text_at(22, 29, 'SignalLens Forensic Workbench', 20, 'bold'),
           text_at(22, 53, 'PROPOSED STATIC WIREFRAME • illustrative labels • no functioning replacement', 13),
           text_at(205, 101, title, 19, 'bold'),
           '<rect x="12" y="85" width="170" height="590" rx="4" fill="#f4f6f9" stroke="#8995a6"/>']
    for i, item in enumerate(['Overview', 'Image Forensics', 'Evidence', 'Reasoning', 'Provenance', 'Reports']):
        y = 128 + i * 48
        if item == active:
            svg.append(f'<rect x="22" y="{y-24}" width="150" height="36" rx="3" fill="#d7e0eb" stroke="#64748b"/>')
        svg.append(text_at(32, y, item, 14, 'bold' if item == active else 'normal'))
    svg.extend([text_at(32, 615, 'Settings / Help', 13), text_at(32, 644, 'Archive management', 12)])
    for x, y, w, h, heading, lines in panels:
        svg.extend([f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="white" stroke="#8995a6"/>',
                    text_at(x+14, y+27, heading, 15, 'bold'),
                    f'<path d="M{x+14} {y+39} H{x+w-14}" stroke="#cbd5e1"/>'])
        for i, line in enumerate(lines):
            svg.append(text_at(x+14, y+63+i*25, line, 13))
    svg.extend(['<rect x="12" y="690" width="1255" height="34" fill="#d4dbe4"/>',
                text_at(24, 712, 'Source: [identity]   Run / revision: [recorded ID]      Execution: [state]      Coverage: [recorded status]', 13), '</g></svg>'])
    svg_path = OUT / f'{name}.svg'
    svg_path.write_text('\n'.join(svg), encoding='utf-8')
    renderer = QSvgRenderer(str(svg_path))
    raster = QImage(1280, 740, QImage.Format.Format_ARGB32)
    raster.fill(0xffffffff)
    painter = QPainter(raster)
    renderer.render(painter, QRectF(0, 0, 1280, 740))
    painter.end()
    if not raster.save(str(OUT / f'{name}.png')):
        raise RuntimeError(f'Failed to render {name}')

parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>SignalLens UI-0 — proposed wireframes</title><style>body{font:16px Segoe UI,Arial,sans-serif;background:#eef1f5;color:#172033;margin:24px}main{max-width:1280px;margin:auto}nav a{margin-right:18px}section{margin:40px 0}img{width:100%;height:auto;border:1px solid #8995a6}a{color:#1d4ed8}@media print{section{break-before:page}nav{display:none}}</style><main>',
         '<h1>SignalLens Forensic Workbench</h1><p><strong>Proposed static concepts — UI-0 audit only.</strong> These six wireframes are not a functioning application. Bracketed labels are illustrative data slots, not forensic conclusions.</p><nav>']
for name, title, _, _ in SCREENS:
    parts.append(f'<a href="#{name}">{escape(title.split(" — ")[0])}</a>')
parts.append('</nav>')
for name, title, _, _ in SCREENS:
    parts.append(f'<section id="{name}"><h2>{escape(title)}</h2><img src="{name}.svg" alt="{escape(title)} proposed low fidelity layout"><p><a href="{name}.svg">Standalone SVG</a> · <a href="{name}.png">PNG preview</a></p></section>')
parts.append('<p>Design rationale: <a href="../signal_lens_design_concept.md">design concept</a>. Actual UI screenshots are stored separately in ../screenshots/.</p></main></html>')
(OUT / 'index.html').write_text('\n'.join(parts), encoding='utf-8')
print('Created six SVG wireframes, six PNG previews and static index.html.')
