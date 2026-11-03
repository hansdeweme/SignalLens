"""Run pytest in the sandbox with inherited Windows temporary-directory ACLs.

Python 3.13's mkdir(mode=0o700) excludes the restricted sandbox token on this
machine. Only that temporary-directory mode is normalized; no elevation.
"""
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pytest

original_mkdir = os.mkdir
def inherited_mkdir(path, mode=0o777, *, dir_fd=None):
    return original_mkdir(path, 0o777 if mode == 0o700 else mode, dir_fd=dir_fd)
os.mkdir = inherited_mkdir
for argument in sys.argv[1:]:
    if argument.startswith('--basetemp='):
        Path(argument.partition('=')[2]).parent.mkdir(parents=True, exist_ok=True)
raise SystemExit(pytest.main(sys.argv[1:] or ['tests', '-q', '-p', 'no:cacheprovider']))
