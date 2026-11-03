"""One-time UI-2 build-method replacement; preserves all UI-1 session methods."""
import ast
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
path = ROOT / 'signallens_gui.py'
source = path.read_text(encoding='utf-8')
gui = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == 'SignalLensGui')
node = next(node for node in gui.body if isinstance(node, ast.FunctionDef) and node.name == '_build_ui')
lines = source.splitlines(keepends=True)
lines[node.lineno-1:node.end_lineno] = ['''    def _build_ui(self) -> None:
        self._create_menu_bar()
        self.setMenuBar(self.menu_bar)
        self.workspace = WorkspaceShell(self)
        self.setCentralWidget(self.workspace)
        self.snapshot_changed.connect(self.workspace.bind_snapshot)
''']
path.write_text(''.join(lines), encoding='utf-8')
