"""Scoped, read-only adapter for production artifact contracts.

Live raw payloads and explicitly persisted JSON fields are authoritative paths.
Never searches by image basename or walks arbitrary artifact directories.
"""
import hashlib
from dataclasses import replace
import json
import os
from pathlib import Path
from contextlib import contextmanager
from PIL import Image
from artifact_models import ForensicArtifact, Registration, SpatialTransform

DETECTORS = ('ela','noise','sensor_origin','cfa_demosaic','person_subject_mask','region_masks',
    'region_segmentation','segmentation_alignment','boundary_focus','fft','region_fft','subject_boundary',
    'subject_texture_consistency','subject_process_asymmetry','subject_material_realism','patch_similarity',
    'patch_spatial','compression_history','cross_signal')
DIRECT = {
    'ela': ('ela_image_path','ela_hotspot_overlay_original_path','ela_hotspot_overlay_diff_path','recompressed_jpeg_path'),
    'noise': ('residual_image_path','noise_overlay_original_path','noise_overlay_residual_path'),
    'person_subject_mask': ('mask_path','overlay_path'),
    'region_masks': ('subject_mask_path','boundary_band_path','background_mask_path','preview_path'),
}


@contextmanager
def shared_read(path):
    """Background inspection must not prevent source relocation on Windows."""
    if os.name != 'nt':
        with open(path, 'rb') as stream:
            yield stream
        return
    import ctypes
    from ctypes import wintypes
    import msvcrt
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,
                       wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    create.restype = wintypes.HANDLE
    handle = create(str(Path(path).resolve()),0x80000000,7,None,3,0x80,None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        fd = msvcrt.open_osfhandle(handle,os.O_RDONLY | os.O_BINARY)
    except Exception:
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        close(handle)
        raise
    with os.fdopen(fd,'rb') as stream:
        yield stream


def digest_file(path):
    digest = hashlib.sha256()
    with shared_read(path) as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            digest.update(part)
    return digest.hexdigest()


def scoped_path(root, value):
    if not isinstance(value, str) or not value:
        raise ValueError('Artifact path not recorded')
    path = Path(value)
    path = (root/path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Artifact path escapes the investigation output directory')
    return path


def output_root(session, raw_state=None):
    if raw_state is not None and session.invocation:
        root = Path(session.invocation.output_dir).resolve()
        return root if Path(raw_state.output_dir).resolve() == root else None
    if not session.imported_from:
        return None
    summary = Path(session.imported_from).resolve()
    if summary.parent.name == 'summary':
        generation = summary.parent.parent
        return generation.parent.parent if generation.parent.name == 'report_revisions' else generation
    return summary.parent


def discovery_context(session, snapshot, raw_state=None):
    """Freeze only JSON payloads/identity before dispatch; no widget in worker."""
    root = output_root(session, raw_state)
    payloads = {}
    if raw_state:
        for detector in DETECTORS:
            payload = getattr(raw_state, detector+'_payload', None)
            if isinstance(payload, dict):
                payloads[detector] = payload
    return {'root': str(root) if root else None, 'session_id': snapshot.session_id,
        'analysis_id': snapshot.analysis_id, 'result_id': snapshot.result_id,
        'analysis_revision': snapshot.analysis_revision, 'source_path': session.image_path,
        'source_sha256': session.source_sha256, 'historical': json.loads(session.historical_identity_json or '{}'),
        'summary': session.summary_data() or {}, 'payloads': payloads, 'live': bool(raw_state)}


def discover_artifacts(context, snapshot):
    """Called in preview worker pool; decoding/hash work never blocks the GUI."""
    root = Path(context['root']).resolve() if context['root'] else None
    summary, payloads = context['summary'], dict(context['payloads'])
    recorded_hashes = {}
    source_dimensions, orientation, source_ok = None, None, False
    try:
        with shared_read(context['source_path']) as stream:
            with Image.open(stream) as im:
                source_dimensions, orientation = im.size, im.getexif().get(274, 1)
        source_ok = bool(context['source_sha256'] and digest_file(context['source_path']) == context['source_sha256'])
    except (OSError, TypeError, ValueError):
        pass
    # Current UI-1 run identity is stronger than a path or matching dimensions.
    expected = context if context['live'] else context['historical']
    trusted_run = False
    try:
        manifest = json.loads((root/'analysis_run.json').read_text(encoding='utf-8'))
        recorded = manifest.get('artifacts', {}).get('investigation', {})
        trusted_run = (recorded.get('result_id') == expected.get('result_id')
            and recorded.get('source_sha256') == context['source_sha256'] and bool(context['source_sha256']))
    except (OSError, ValueError, TypeError):
        pass
    # Live state was already guarded by UI-1; do not depend on later report publication.
    trusted_run = trusted_run or bool(context['live'] and context['analysis_id'] == context['result_id'])
    if root and trusted_run and not context['live']:
        try:
            catalog = json.loads(scoped_path(root, 'ui_artifacts_v1.json').read_text(encoding='utf-8'))
            if (catalog.get('schema_version') == 1 and catalog.get('result_id') == expected.get('result_id')
                    and catalog.get('source_sha256') == context['source_sha256']
                    and isinstance(catalog.get('payloads'), dict)):
                payloads.update(catalog['payloads'])
                recorded_hashes = {a['artifact_id']:a.get('sha256') for a in catalog.get('artifacts', [])
                                   if isinstance(a,dict) and a.get('artifact_id')}
        except (OSError, ValueError, TypeError):
            pass
        stem = Path(context['source_path'] or '').stem
        contracts = {'ela': f'{stem}_ela.json', 'noise': f'{stem}_noise.json',
                     'patch_similarity': 'patch_similarity_results.json'}
        # fft_results.json is shared/overwritten by regional calls. Accept it
        # only when its recorded input equals the known global prepared input.
        contracts['fft'] = 'fft_results.json'
        for detector, filename in contracts.items():
            try:
                payload = json.loads(scoped_path(root, filename).read_text(encoding='utf-8'))
                if detector == 'fft' and Path(payload.get('fft', {}).get('input_image','')).name != stem+'_global.png':
                    continue
                payloads.setdefault(detector, payload)
            except (OSError, ValueError, TypeError):
                pass
    rows, seen = [], {}
    sections = summary.get('sections') or {}
    for detector in DETECTORS:
        payload = payloads.get(detector, {})
        block = payload.get(detector, {})
        if not isinstance(block, dict):
            block = {}
        section = sections.get(detector, {})
        if detector == 'region_masks' and not block:
            block = section.get('details', {})
        paths = {key: block.get(key) for key in DIRECT.get(detector, ()) if key in block}
        paths.update(section.get('artifacts', {}) if isinstance(section.get('artifacts'), dict) else {})
        paths.update(block.get('artifacts', {}) if isinstance(block.get('artifacts'), dict) else {})
        if detector == 'cross_signal':
            paths.update(summary.get('overlay_paths') or {})
        # Regional FFT's child spectra are scoped explicitly within their payload.
        if detector == 'region_fft':
            for region in ('subject','boundary','background'):
                child = block.get(region+'_fft', {})
                paths.update({region+'/'+k:v for k,v in child.get('fft',child).get('artifacts',{}).items()})
        if not paths:
            paths = {'structured_result': None}
        stage = next((s for s in snapshot.stages if s.detector == detector+'_payload'), None)
        evidence = tuple(e for e in snapshot.evidence if e.source_detector == detector)
        reliability = block.get('mask_reliability') or block.get('person_mask_reliability')
        if reliability is None:
            reliability = next((e.reliability for e in evidence if e.reliability), None)
        for key, raw_path in paths.items():
            spatial, transform, legend = Registration.UNKNOWN, None, None
            kind, available, reason, path, width, height, digest = 'D', True, None, None, None, None, None
            if raw_path:
                kind = 'C' if detector in ('fft','region_fft') and any(tag in key for tag in ('spectrum','radial','peakmap')) else 'B'
                try:
                    if not root or not trusted_run:
                        raise ValueError('Analysis identity cannot be verified for this artifact directory')
                    resolved = scoped_path(root, raw_path)
                    if str(resolved) in seen:
                        # Physical reuse is not an independent artifact or vote.
                        if not any(a.detector_id == detector for a in rows):
                            owner = next(a for a in rows if a.path == str(resolved))
                            rows.append(replace(owner,artifact_id=detector+'/structured_result',detector_id=detector,
                                label='Shared artifact reference',artifact_type='D',path=None,width=None,height=None,
                                sha256=None,registration=Registration.NOT_APPLICABLE,transform=None,overlay_legend=None,
                                reliability=str(reliability) if reliability else None,
                                evidence_ids=tuple(dict.fromkeys(e.evidence_id for e in evidence)),
                                hypothesis_ids=tuple(dict.fromkeys(e.hypothesis_id for e in evidence)),
                                stage_status=stage.status if stage else None,available=True,
                                reason='Visualization already listed under '+owner.detector_id,
                                description='Shared output is not independent corroboration.',
                                details_json=json.dumps(block or section,ensure_ascii=False,default=str)))
                        continue
                    path = str(resolved)
                    with shared_read(resolved) as stream:
                        with Image.open(stream) as im:
                            width,height = im.size
                            im.verify()
                    digest = digest_file(resolved)
                    recorded_hash = recorded_hashes.get(detector+'/'+key)
                    if recorded_hash and digest != recorded_hash:
                        raise ValueError('Artifact content changed since the saved catalog')
                    seen[path] = True
                    if kind == 'C':
                        spatial = Registration.NOT_APPLICABLE
                    elif source_ok and orientation == 1 and detector in ('ela','noise'):
                        if (width,height) != source_dimensions:
                            raise ValueError('Dimensions disagree with the full-source production grid')
                        kind,spatial,transform = 'A',Registration.REGISTERED,SpatialTransform()
                        if key in ('ela_image_path','residual_image_path'):
                            legend = 'Brightness-scaled RGB recompression difference' if detector == 'ela' else 'Brightness-scaled absolute luminance residual'
                    elif source_ok and orientation == 1 and detector in ('person_subject_mask','region_masks'):
                        status = block.get('mask_status')
                        if status not in ('reliable','limited'):
                            raise ValueError('Person geometry rejected, approximate or unavailable: '+str(status or 'not recorded'))
                        geometry = block.get('image_geometry', block)
                        shape = geometry.get('shape', ())
                        expected_size = (geometry.get('width'), geometry.get('height'))
                        if len(shape) == 2:
                            expected_size = (shape[1], shape[0])
                        if expected_size != (width,height):
                            raise ValueError('Mask dimensions do not match recorded geometry')
                        spatial = Registration.TRANSFORMABLE
                        transform = SpatialTransform(width/source_dimensions[0],0,0,height/source_dimensions[1])
                except (OSError, ValueError, TypeError) as error:
                    kind,available,reason,transform,legend = 'E',False,str(error),None,None
                    spatial = Registration.UNKNOWN
            elif key != 'structured_result':
                kind,available,reason = 'E',False,'Artifact path not recorded'
            else:
                spatial = Registration.NOT_APPLICABLE
                available = bool(section or block)
                if not available:
                    reason = stage.reason if stage and stage.reason else 'No structured result or visualization recorded'
            if stage and stage.status not in ('success',) and not raw_path:
                kind,available,reason = 'E',False,stage.reason or stage.status
            if raw_path and not source_ok:
                reason = (reason+'; ' if reason else '') + 'Source missing, changed or identity unrecorded; linked comparison disabled'
            aid = detector+'/'+key
            rows.append(ForensicArtifact(aid,context['session_id'],context['analysis_id'],context['result_id'],
                context['analysis_revision'],context['source_sha256'],detector,key.replace('_',' '),kind,path,width,height,digest,
                spatial,transform,source_dimensions,orientation,str(reliability) if reliability else None,
                tuple(dict.fromkeys(e.evidence_id for e in evidence)),tuple(dict.fromkeys(e.hypothesis_id for e in evidence)),
                stage.status if stage else None,available,reason,
                section.get('note') or 'Detector observation; visualization alone does not establish manipulation or generation.',
                json.dumps(block or section,ensure_ascii=False,default=str),legend))
    return tuple(rows)
