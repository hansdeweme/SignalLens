"""UI-4 identity, unsafe paths, coordinates, async and comparison gates."""
from gui_helpers import publish, wait_for
from dataclasses import replace
import json

import pytest
from PIL import Image
from PyQt6.QtCore import Qt

from artifact_models import Registration, SpatialTransform
from artifact_presenter import digest_file, discover_artifacts, discovery_context, scoped_path, shared_read
from investigation_presenters import build_presentation
from forensic_image_viewer import ForensicImageViewer
from presentation_models import EvidenceView
from source_image_viewer import read_preview


def catalog(window, source, detector='ela', size=(32,48), key='ela_image_path', extra=None):
    token = publish(window, source)
    path = window.analysis_state.output_dir / 'artifact.png'
    Image.new('RGB', size, 'red').save(path)
    block = {key: str(path), **(extra or {})}
    setattr(window.analysis_state, detector+'_payload', {detector:block})
    snapshot = build_presentation(window.session)
    context = discovery_context(window.session,snapshot,window.analysis_state)
    return snapshot, context, discover_artifacts(context,snapshot)


@pytest.mark.parametrize('transform', [SpatialTransform(), SpatialTransform(.5,0,0,.25,-8,12),
                                      SpatialTransform(0,1,-1,0,80,0)])
def test_coordinate_roundtrip(transform):
    for point in ((0,0),(.5,.5),(20.5,40.5),(2000,3000)):
        assert transform.inverse().map(*transform.map(*point)) == pytest.approx(point,abs=1e-9)


@pytest.mark.parametrize('values', [{'a':0},{'tx':float('nan')},{'d':float('inf')}])
def test_invalid_transform_rejected(values):
    with pytest.raises(ValueError):
        SpatialTransform(**values)


def test_paths_cannot_escape_run(tmp_path):
    for path in ('../foreign.png', str(tmp_path.parent/'foreign.png')):
        with pytest.raises(ValueError):
            scoped_path(tmp_path,path)


def test_verified_ela_can_overlay_and_is_bound(window,source):
    snapshot,context,rows = catalog(window,source)
    artifact = next(a for a in rows if a.path)
    assert artifact.can_overlay and artifact.artifact_type == 'A'
    assert (artifact.session_id,artifact.result_id,artifact.source_sha256) == (snapshot.session_id,snapshot.result_id,digest_file(source))
    workspace = window.workspace.forensics
    workspace.bind(snapshot)
    assert workspace.accept_catalog(workspace.key,rows)
    assert workspace.selected == artifact
    workspace.mode.setCurrentIndex(2)
    assert len(workspace._overlay_items) == 2
    workspace.opacity.setValue(25)
    assert workspace._overlay_items[0].opacity() == .25
    workspace.mode.setCurrentIndex(0)
    assert not workspace._overlay_items


@pytest.mark.parametrize('detector,key', [('fft','spectrum'),('region_fft','subject_spectrum'),('sensor_origin','overlay')])
def test_matching_dimensions_do_not_grant_registration(window,source,detector,key):
    snapshot,context,rows = catalog(window,source,detector,key='unused')
    context['payloads'] = {detector:{detector:{'artifacts':{key:rows[0].path or str(window.analysis_state.output_dir/'artifact.png')}}}}
    artifact = next(a for a in discover_artifacts(context,snapshot) if a.path)
    assert not artifact.can_sync and not artifact.can_overlay
    if detector in ('fft','region_fft'):
        assert artifact.artifact_type == 'C'


@pytest.mark.parametrize('failure', ['identity','dimensions','changed','missing','corrupt','escape'])
def test_bad_artifacts_fail_closed(window,source,failure):
    snapshot,context,rows = catalog(window,source)
    path = window.analysis_state.output_dir/'artifact.png'
    if failure == 'identity': context['analysis_id'] = 'old'
    elif failure == 'dimensions': Image.new('RGB',(99,30)).save(path)
    elif failure == 'changed': Image.new('RGB',(32,48),'blue').save(source)
    elif failure == 'missing': path.unlink()
    elif failure == 'corrupt': path.write_bytes(b'corrupt')
    else: context['payloads']['ela']['ela']['ela_image_path'] = str(source)
    artifact = discover_artifacts(context,snapshot)[0]
    assert not artifact.can_sync and not artifact.can_overlay
    assert artifact.reason
    if failure != 'changed': assert not artifact.available


@pytest.mark.parametrize('status', ['reliable','limited','approximate','unavailable'])
def test_mask_transform_requires_accepted_geometry(window,source,status):
    snapshot,context,rows = catalog(window,source,'person_subject_mask',(16,24),'mask_path',
        {'mask_status':status,'image_geometry':{'width':16,'height':24}})
    artifact = next(a for a in rows if a.detector_id == 'person_subject_mask')
    assert artifact.can_sync == (status in ('reliable','limited'))
    assert not artifact.can_overlay
    if artifact.can_sync:
        assert artifact.transform.map(20.5,30.5) == (10.25,15.25)


def test_catalog_and_preview_stale_after_switch(window,source,tmp_path):
    snapshot,context,rows = catalog(window,source)
    workspace = window.workspace.forensics
    workspace.bind(snapshot)
    old_key = workspace.key
    other = tmp_path/'other.png'
    Image.new('RGB',(30,20)).save(other)
    window.set_selected_file(other)
    assert not workspace.accept_catalog(old_key,rows)
    assert not workspace.artifacts and workspace.selected is None


def test_source_mutation_removes_overlay(window,source):
    snapshot,context,rows = catalog(window,source)
    workspace = window.workspace.forensics
    workspace.bind(snapshot)
    workspace.accept_catalog(workspace.key,rows)
    workspace.mode.setCurrentIndex(2)
    Image.new('RGB',(32,48),'blue').save(source)
    workspace.source.check_source()
    assert workspace.mode.currentIndex() == 0
    assert not workspace._overlay_items


def test_viewer_maps_native_pixel_centers_after_bounded_decode(app,tmp_path):
    path = tmp_path/'large.png'
    Image.new('RGB',(4000,2000),'navy').save(path)
    viewer = ForensicImageViewer('Test artifact')
    viewer.show()
    viewer.set_source(path,('test',),digest_file(path))
    wait_for(app,lambda:not viewer._image.isNull())
    viewer.configure_grid(SpatialTransform(.5,0,0,.5))
    item = viewer.canvas.scene().items()[0]
    point = item.mapToScene(1024,512)
    assert (point.x(),point.y()) == pytest.approx((4000,2000),abs=1e-9)
    viewer.close()


def test_linked_zoom_uses_source_coordinates(window,source):
    snapshot,context,rows = catalog(window,source)
    workspace = window.workspace.forensics
    workspace.bind(snapshot)
    workspace.accept_catalog(workspace.key,rows)
    window.workspace.navigate('Image Forensics')
    workspace.mode.setCurrentIndex(1)
    workspace.source.zoom(2)
    assert workspace.source.canvas.transform() == workspace.artifact.canvas.transform()
    # Integer viewport centers/scrollbar clamping limit center equality to one display pixel.
    scale = abs(workspace.source.canvas.transform().m11())
    assert workspace.artifact.point_at_center() == pytest.approx(workspace.source.point_at_center(),abs=2/scale)


def test_stored_catalog_recovery_requires_matching_manifest(window,source):
    snapshot,context,rows = catalog(window,source)
    root = window.analysis_state.output_dir
    identity = {'result_id':context['result_id'],'source_sha256':context['source_sha256']}
    (root/'analysis_run.json').write_text(json.dumps({'artifacts':{'investigation':identity}}))
    (root/'ui_artifacts_v1.json').write_text(json.dumps({'schema_version':1,**identity,'payloads':context['payloads']}))
    context.update(live=False,historical=identity,payloads={})
    assert discover_artifacts(context,snapshot)[0].can_overlay
    identity['result_id'] = 'foreign'
    context['historical'] = identity
    assert not any(a.can_sync for a in discover_artifacts(context,snapshot))


@pytest.mark.parametrize('orientation',[3,6,8])
def test_oriented_sources_cannot_gain_identity_registration(window,tmp_path,orientation):
    path = tmp_path/'oriented.jpg'
    exif = Image.Exif()
    exif[274] = orientation
    Image.new('RGB',(32,48),'gray').save(path,exif=exif)
    snapshot,context,rows = catalog(window,path)
    assert not any(a.can_sync for a in rows)
    viewer = window.workspace.forensics.source
    assert viewer.display_dimensions == ((48,32) if orientation in (6,8) else (32,48))
    bounds = viewer.canvas.sceneRect()
    assert (bounds.width(),bounds.height()) == viewer.display_dimensions


def test_background_file_reads_allow_relocation(tmp_path):
    path = tmp_path/'relocatable.bin'
    path.write_bytes(b'identity')
    with shared_read(path) as stream:
        path.unlink()
        assert stream.read() == b'identity'


def test_closing_window_rejects_catalog(window,source):
    snapshot,context,rows = catalog(window,source)
    workspace = window.workspace.forensics
    workspace.bind(snapshot)
    window._closing = True
    assert not workspace.accept_catalog(workspace.key,rows)
    window._closing = False


def test_saved_catalog_detects_artifact_replacement(window,source):
    snapshot,context,rows = catalog(window,source)
    root = window.analysis_state.output_dir
    identity = {'result_id':context['result_id'],'source_sha256':context['source_sha256']}
    (root/'analysis_run.json').write_text(json.dumps({'artifacts':{'investigation':identity}}))
    (root/'ui_artifacts_v1.json').write_text(json.dumps({'schema_version':1,**identity,'payloads':context['payloads'],
        'artifacts':[{'artifact_id':rows[0].artifact_id,'sha256':rows[0].sha256}]}))
    context.update(live=False,historical=identity,payloads={})
    Image.new('RGB',(32,48),'green').save(root/'artifact.png')
    artifact = discover_artifacts(context,snapshot)[0]
    assert not artifact.available and 'content changed' in artifact.reason


@pytest.mark.parametrize('linked',[True,False])
def test_only_recorded_evidence_relationships_are_attached(window,source,linked):
    snapshot,context,rows = catalog(window,source)
    evidence = EvidenceView('explicit:id','localized_editing','Recorded observation','supporting_evidence',
                            'limited','ela' if linked else 'unrelated',None,'Recorded interpretation')
    snapshot = replace(snapshot,evidence=(evidence,))
    artifact = discover_artifacts(context,snapshot)[0]
    assert artifact.evidence_ids == (('explicit:id',) if linked else ())
    assert artifact.hypothesis_ids == (('localized_editing',) if linked else ())
    assert artifact.reliability == ('limited' if linked else None)


def test_shared_outputs_have_one_raster_and_a_structured_reference(window,source):
    snapshot,context,rows = catalog(window,source)
    path = rows[0].path
    context['payloads']['noise'] = {'noise':{'residual_image_path':path}}
    result = discover_artifacts(context,snapshot)
    assert sum(a.path == path for a in result) == 1
    shared = next(a for a in result if a.detector_id == 'noise')
    assert shared.artifact_type == 'D' and shared.path is None
    assert 'already listed' in shared.reason


def test_late_artifact_preview_cannot_replace_new_selection(window,source):
    snapshot,context,rows = catalog(window,source)
    second = window.analysis_state.output_dir/'second.png'
    Image.new('RGB',(32,48),'green').save(second)
    context['payloads']['ela']['ela']['ela_hotspot_overlay_original_path'] = str(second)
    result = discover_artifacts(context,snapshot)
    workspace = window.workspace.forensics
    workspace.bind(snapshot)
    workspace.accept_catalog(workspace.key,result)
    late = read_preview(workspace.artifact._request,rows[0].path,rows[0].sha256)
    workspace.tree.setCurrentItem(workspace.tree.topLevelItem(0).child(1))
    cache_key = workspace.artifact._image.cacheKey()
    assert not workspace.artifact.accept_preview(late)
    assert workspace.artifact._image.cacheKey() == cache_key
