"""One-time UI-1 method integration, kept as implementation provenance."""
import ast
from pathlib import Path
from textwrap import dedent, indent

root = Path(__file__).resolve().parents[3]
path = root / 'signallens_gui.py'
source = path.read_text(encoding='utf-8')
methods = {}
def method(name, body):
    methods[name] = indent(dedent(body).strip(), '    ') + '\n'

method('update_summary', '''
def update_summary(self) -> None:
    # Rendering is a projection of the frozen analysis, never new synthesis.
    data = self.session.summary_data()
    self.summary_result = SimpleNamespace(**data) if data else None
    if data:
        self.summary_box.setHtml((data.get('full_html') or '') + annotation_appendix(self.session)[1])
    else:
        self.summary_box.clear()
    self._report_snapshot = None
    self._publish_snapshot()
''')
method('clear_analysis_state', '''
def clear_analysis_state(self) -> None:
    for name in tuple(vars(self)):
        if name.endswith('_payload'):
            setattr(self, name, None)
    self.analysis_state = self.summary_result = None
    self.osint_result = None
    self._report_snapshot = None
    self._report_paths = {}
    self.decision_trace_action.setEnabled(False)
    self.open_latest_audit_action.setEnabled(False)
    self.open_json_button.setEnabled(False)
''')
method('clear_ui', '''
def clear_ui(self) -> None:
    self.session.cancel()
    self.session = InvestigationSession()
    self.clear_analysis_state()
    self.selected_file = self.current_image_path = self.current_analysis_dir = self.output_json = None
    self._session_dir = None
    self.file_edit.clear()
    self.summary_box.clear()
    self.log_box.clear()
    for checkbox in (self.chk_natural, self.chk_decorative, self.chk_smartphone, self.chk_screen):
        checkbox.setChecked(False)
    self.drop_label.setText("Drag and drop an image here, or use 'Choose Image'")
    self.status_label.setText('Ready. Previous invocation superseded.' if self.workers.busy else 'Ready.')
    self.refresh_osint_ui()
    self._publish_snapshot()
''')
method('set_selected_file', '''
def set_selected_file(self, path: Path) -> None:
    if self._closing:
        return
    try:
        self.settings = deepcopy(load_settings())
        path = Path(path).resolve()
        if not self.is_supported_image(path):
            raise ValueError('Select an existing supported image file.')
        from PIL import Image
        with Image.open(path) as image:
            image.verify()
        from osint_reverse_search import create_empty_osint_result
        annotations = create_empty_osint_result(path)
        # Legacy stem folders may collide. Import annotations only when their
        # canonical file hash matches this source; never merge by filename alone.
        legacy = Path(self.settings['output_root']) / path.stem / 'osint_results.json'
        if legacy.is_file():
            candidate = load_osint_result(legacy)
            if candidate.image_sha256 == annotations.image_sha256:
                annotations = candidate
        session = InvestigationSession.selected(path, annotations)
    except Exception as exc:
        QMessageBox.warning(self, 'Image selection failed', str(exc))
        return
    self.session.cancel()
    self.session = session
    self.clear_analysis_state()
    self.selected_file = self.current_image_path = path
    self._session_dir = Path(self.settings['output_root']).resolve() / path.stem / session.session_id
    self.current_analysis_dir = self._session_dir
    self.output_json = None
    self.osint_result = annotations_object(json.loads(session.annotations_json))
    self.file_edit.setText(str(path))
    self.drop_label.setText(f'Selected:\\n{path.name}')
    self.summary_box.clear()
    self.log_box.clear()
    self.log(f'Selected file: {path} — investigation {session.session_id}')
    self.status_label.setText('File selected. No active result.')
    self.refresh_osint_ui()
    self._publish_snapshot()
''')
method('open_osint_engine', '''
def open_osint_engine(self, provider: str) -> None:
    if not self.ensure_osint_ready():
        return
    session_id = self.session.session_id
    draft = deepcopy(self.osint_result)
    try:
        open_reverse_search(provider, draft)
        self._commit_osint(session_id, draft)
        QMessageBox.information(self, 'Reverse Search', "Perform your search in the browser, then click 'Add Finding' to record results.")
    except Exception as exc:
        QMessageBox.critical(self, 'OSINT Error', str(exc))
''')
method('add_osint_finding', '''
def add_osint_finding(self) -> None:
    if not self.ensure_osint_ready():
        return
    session_id = self.session.session_id
    draft = deepcopy(self.osint_result)
    dialog = OSINTFindingDialog(self)
    if dialog.exec():
        add_manual_match(draft, **dialog.get_data())
        self._commit_osint(session_id, draft)
''')
method('edit_selected_osint_finding', '''
def edit_selected_osint_finding(self) -> None:
    if not self.ensure_osint_ready():
        return
    row = self.osint_findings_list.currentRow()
    if not 0 <= row < len(self.osint_result.matches):
        return
    session_id = self.session.session_id
    draft = deepcopy(self.osint_result)
    dialog = OSINTFindingDialog(self, existing_match=draft.matches[row])
    if dialog.exec():
        replace_match(draft, index=row, **dialog.get_data())
        self._commit_osint(session_id, draft)
''')
method('delete_selected_osint_finding', '''
def delete_selected_osint_finding(self) -> None:
    if not self.ensure_osint_ready():
        return
    draft = deepcopy(self.osint_result)
    row = self.osint_findings_list.currentRow()
    if 0 <= row < len(draft.matches):
        delete_match(draft, row)
        self._commit_osint(self.session.session_id, draft)
''')
method('mark_osint_reviewed_no_match', '''
def mark_osint_reviewed_no_match(self) -> None:
    if not self.ensure_osint_ready():
        return
    draft = deepcopy(self.osint_result)
    mark_reviewed_no_match(draft)
    self._commit_osint(self.session.session_id, draft)
''')
method('ensure_osint_ready', '''
def ensure_osint_ready(self) -> bool:
    if self._closing or self.current_image_path is None or self._session_dir is None:
        QMessageBox.information(self, 'OSINT', 'Load an image with an available source first.')
        return False
    self.osint_result = annotations_object(json.loads(self.session.annotations_json))
    return self.osint_result is not None
''')
method('run_analysis', '''
def run_analysis(self) -> None:
    if self._closing or not self.session.image_path:
        return
    if not Path(self.session.image_path).is_file():
        self.session.cancel()
        self.session.state = InvestigationState.FAILED
        self.session.error = 'Selected source file no longer exists.'
        self.session.summary_json = self.session.result_id = None
        self.session.analysis_result = None
        self.session.report_revision = None
        self.clear_analysis_state()
        self.update_summary()
        self.status_label.setText(self.session.error)
        return
    self.settings = deepcopy(load_settings())
    context = {'natural_repetition': self.chk_natural.isChecked(),
               'decorative_geometric': self.chk_decorative.isChecked(),
               'smartphone_computational': self.chk_smartphone.isChecked(),
               'screen_origin': self.chk_screen.isChecked()}
    invocation = self.session.begin_analysis(self.analysis_mode, context, self.settings, self.settings['output_root'])
    self.current_analysis_dir = Path(invocation.output_dir)
    self.output_json = self.current_analysis_dir / f'{Path(invocation.image_path).stem}_exif_signals.json'
    self.clear_analysis_state()
    self.osint_result = annotations_object(json.loads(self.session.annotations_json))
    self.summary_box.clear()
    self.status_label.setText('Running analysis…')
    self._publish_snapshot()
    try:
        self.workers.start(invocation)
    except Exception as exc:
        self.on_analysis_error(invocation, str(exc))
''')
method('on_analysis_finished', '''
@pyqtSlot(object, object)
def on_analysis_finished(self, invocation, state):
    if self._closing or not self.session.accepts(invocation):
        return
    try:
        if (Path(state.selected_file).resolve() != Path(invocation.image_path).resolve()
                or Path(state.output_dir).resolve() != Path(invocation.output_dir).resolve()):
            raise ValueError('Worker result does not match its invocation source/output.')
        # This is the existing, authoritative synthesis operation, invoked once
        # using launch-time context and annotations. Post-run edits do not call it.
        summary = build_summary_result(state,
            annotations_object(json.loads(invocation.annotations_json)),
            scene_context=dict(invocation.scene_context))
        if not self.session.complete(invocation, state, summary):
            return
    except Exception as exc:
        self.on_analysis_error(invocation, str(exc))
        return
    self.analysis_state = self.session.analysis_result
    for name in tuple(vars(self)):
        if name.endswith('_payload'):
            setattr(self, name, getattr(state, name, None))
    self.update_summary()
    self.status_label.setText('Analysis completed. Findings frozen to this invocation.')
    self.refresh_report_snapshot()
''')
method('on_analysis_error', '''
@pyqtSlot(object, str)
def on_analysis_error(self, invocation, message: str):
    if self._closing or not self.session.fail(invocation, message):
        return
    self.clear_analysis_state()
    self.update_summary()
    self.status_label.setText(f'Analysis failed: {message}')
    self.log(message, 'error')
''')
method('open_output_folder', '''
def open_output_folder(self) -> None:
    if self.session.state != InvestigationState.COMPLETED:
        QMessageBox.information(self, 'Results', 'No completed active result is available.')
        return
    if not self.refresh_report_snapshot():
        return
    path = Path(self._report_paths['final_summary_json']).resolve()
    try:
        system = platform.system()
        if system == 'Windows':
            subprocess.run(['explorer', '/select,', str(path)], check=False)
        elif system == 'Darwin':
            subprocess.run(['open', '-R', str(path)], check=False)
        else:
            subprocess.run(['xdg-open', str(path.parent)], check=False)
    except Exception as exc:
        QMessageBox.warning(self, 'Could not open folder', str(exc))
''')

tree = ast.parse(source)
gui = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SignalLensGui')
lines = source.splitlines(keepends=True)
for node in sorted((n for n in gui.body if isinstance(n, ast.FunctionDef) and n.name in methods), key=lambda n:n.lineno, reverse=True):
    start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
    lines[start:node.end_lineno] = [methods.pop(node.name)]
if methods:
    raise RuntimeError(f'Methods not found: {list(methods)}')
path.write_text(''.join(lines), encoding='utf-8')
