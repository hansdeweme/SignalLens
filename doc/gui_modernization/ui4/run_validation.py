"""Run pytest in sandbox-readable workspace folders (no chmod/private ACL).

pytest's Windows mode=0o700 temp directories are unreadable to this sandbox.
Only the temporary-path fixture is replaced; assertions and tests are unchanged.
Each invocation retains a new directory for review, with inherited workspace ACLs.
"""
from pathlib import Path
import sys
import uuid
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


class WorkspaceTemps:
    _retention_policy = 'all'
    def __init__(self):
        self.root = ROOT / 'doc/gui_modernization/ui4/test_runs' / ('validation_' + uuid.uuid4().hex[:10])
        self.root.mkdir(parents=True)

    def getbasetemp(self):
        return self.root

    def mktemp(self, basename, numbered=True):
        path = self.root / (basename + ('_' + uuid.uuid4().hex[:8] if numbered else ''))
        path.mkdir()
        return path


class TempPlugin:
    @pytest.fixture(scope='session')
    def tmp_path_factory(self):
        return WorkspaceTemps()


if __name__ == '__main__':
    raise SystemExit(pytest.main(['-p', 'no:cacheprovider', *sys.argv[1:]], plugins=[TempPlugin()]))
