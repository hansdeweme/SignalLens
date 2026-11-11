"""Versioned physical paths; canonical identities remain full hashes/IDs.

Legacy trees are read in place. Only newly allocated directories use format 2.
Allocation is serialized with an OS-released file lock; interrupted writers do
not leave a stale lock or replace a valid JSON record with a partial one.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import hashlib
import os
from pathlib import Path
import re
import time
from uuid import uuid4

STORAGE_VERSION = 2
_compact = ContextVar('compact_artifact_names', default=False)


def read_json(path):
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.write-' + uuid4().hex[:12] + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(10):
            try:
                temporary.replace(path)
                break
            except PermissionError:
                # Windows readers opened without FILE_SHARE_DELETE may briefly
                # hold the old manifest. Never truncate it as a fallback.
                if attempt == 9:
                    raise
                time.sleep(0.02)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def allocation_lock(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.storage.lock').open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield root
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def image_folder_name(image_path):
    # ntpath rules apply even on non-Windows validation hosts.
    import ntpath
    stem = ntpath.splitext(ntpath.basename(str(image_path)))[0]
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', stem).strip(' .')
    if not stem:
        stem = 'image'
    if re.fullmatch(r'(?i:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\..*)?', stem):
        stem = '_' + stem
    # Limit UTF-16 units, not just Python characters (Windows counts UTF-16).
    stem = stem.encode('utf-16-le')[:96].decode('utf-16-le', errors='ignore').rstrip(' .')
    return stem or 'image'


def _slot(parent, prefix):
    number = 1
    while True:
        path = parent / f'{prefix}_{number:03d}'
        try:
            path.mkdir()
            return path
        except FileExistsError:
            number += 1


def _initialize(directory, filename, record):
    try:
        atomic_json(directory / filename, record)
    except Exception:
        # Allocation has produced no evidence yet. Remove only our empty slot.
        try:
            directory.rmdir()
        except OSError:
            pass
        raise


def investigation_directory(output_root, image_path, source_sha256, session_id):
    if source_sha256 is not None and not re.fullmatch(r'[0-9a-f]{64}', source_sha256):
        raise ValueError('Storage association requires a full SHA-256 or an explicitly unknown identity.')
    with allocation_lock(output_root) as root:
        children = {p.name.casefold(): p for p in root.iterdir() if p.is_dir()}
        image = None
        for candidate in children.values():
            if candidate.resolve().parent != root:
                continue
            record = read_json(candidate / 'manifest.json')
            if (source_sha256 and record.get('storage_format') == STORAGE_VERSION
                    and record.get('source_sha256') == source_sha256):
                image = candidate
                break
            if (not source_sha256 and record.get('storage_format') == STORAGE_VERSION
                    and any(read_json(p / 'manifest.json').get('session_id') == session_id
                            for p in candidate.glob('inv_*'))):
                image = candidate
                break
        if image is None:
            base = image_folder_name(image_path)
            name = base
            suffix = source_sha256 or hashlib.sha256(session_id.encode()).hexdigest()
            length = 8
            while name.casefold() in children:
                if length > len(suffix):
                    raise ValueError('Cannot allocate an unambiguous image directory.')
                name = base + '--' + suffix[:length]
                length += 4
            image = root / name
            image.mkdir()
            _initialize(image, 'manifest.json', {'storage_format': STORAGE_VERSION,
                'source_sha256': source_sha256, 'original_filename': Path(image_path).name,
                'original_path': str(image_path)})
        for candidate in image.glob('inv_*'):
            if candidate.resolve().parent != image.resolve():
                continue
            record = read_json(candidate / 'manifest.json')
            if (record.get('session_id') == session_id
                    and record.get('source_sha256') == source_sha256):
                return candidate
        directory = _slot(image, 'inv')
        _initialize(directory, 'manifest.json', {'storage_format': STORAGE_VERSION,
            'source_sha256': source_sha256, 'original_filename': Path(image_path).name,
            'original_path': str(image_path), 'session_id': session_id})
        return directory


def allocate_run(directory, analysis_id, source_sha256, session_id):
    directory = Path(directory).resolve()
    with allocation_lock(directory):
        run = _slot(directory, 'run')
        _initialize(run, 'run_identity.json', {'storage_format': STORAGE_VERSION,
            'analysis_id': analysis_id, 'result_id': analysis_id, 'session_id': session_id,
            'source_sha256': source_sha256})
        return run


def run_identity(output_dir):
    record = read_json(Path(output_dir) / 'run_identity.json')
    return record if record.get('storage_format') == STORAGE_VERSION else {}


def evidence_directory(output_dir):
    output = Path(output_dir)
    return output / 'evidence' if run_identity(output) else output


@contextmanager
def artifact_naming(compact):
    token = _compact.set(bool(compact))
    try:
        yield
    finally:
        _compact.reset(token)


def compact_artifacts():
    return _compact.get()


def artifact_stem(image_path):
    stem = Path(image_path).stem
    if not compact_artifacts():
        return stem
    return stem if stem in {'global', 'patch', 'subject', 'ela', 'subject_input',
                            'boundary_input', 'background_input'} else 'image'


def allocate_report(output_dir):
    """Return a new exclusive generation and its single publication pointer."""
    output = Path(output_dir).resolve()
    manifest = read_json(output / 'manifest.json')
    if run_identity(output) or (manifest.get('storage_format') == STORAGE_VERSION and manifest.get('session_id')):
        directory = output.parent if run_identity(output) else output
        reports = directory / 'reports'
        reports.mkdir(exist_ok=True)
        with allocation_lock(directory):
            return _slot(reports, 'rev'), directory / 'latest.json', True
    return None, output / 'current_report.json', False


def stored_forensic_root(metadata):
    storage = (metadata or {}).get('storage') or {}
    if not isinstance(storage, dict):
        raise ValueError('Invalid stored forensic storage association.')
    if storage.get('storage_format') == STORAGE_VERSION and storage.get('forensic_run'):
        return Path(storage['forensic_run']).resolve()
    return None
