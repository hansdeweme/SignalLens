"""UI-0 read-only replay of a stored SummaryResult in the real GUI.

No detectors, persistence callbacks, settings writes or production edits.
This is an audit harness, not a new application or a fixture-analysis replay.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from PyQt6.QtWidgets import QApplication
from signallens_gui import SignalLensGui

app = QApplication(sys.argv)
window = SignalLensGui()
source = ROOT / 'doc/final_acceptance_audit/instagram/summary/final_summary.json'
stored = json.loads(source.read_text(encoding='utf-8'))
window.summary_result = SimpleNamespace(**stored)
window.summary_box.setHtml(stored['full_html'])
window.decision_trace_action.setEnabled(window.has_decision_trace())
window.status_label.setText('Audit replay: stored summary; no analysis executed')
window.log('Read-only UI-0 replay of doc/final_acceptance_audit/instagram/summary/final_summary.json')
window.show()
sys.exit(app.exec())
