"""Immutable projections of recorded metadata; no provenance classification."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from artifact_presenter import scoped_path
from explorer_presenter import identity, mapping, sequence, display
from explorer_models import ExplorerIdentity


@dataclass(frozen=True)
class MetadataField:
    field_id: str
    tag: str
    namespace: str
    value: str
    preview: str
    origins: tuple[str,...]
    interpretations: tuple[str,...]
    evidence_ids: tuple[str,...]
    trust: str
    binary: bool = False


@dataclass(frozen=True)
class ProvenancePresentation:
    identity: ExplorerIdentity
    declaration: str | None
    verification: str
    extraction: str
    limitations: tuple[str,...]
    fields: tuple[MetadataField,...]


def value_text(value):
    if isinstance(value,(bytes,bytearray)):
        return f'Binary payload: {len(value)} bytes; SHA-256 {hashlib.sha256(value).hexdigest()}; text preview unavailable',True
    return (value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2,default=str)),False


def recover_metadata(context):
    """Known persisted contract only; no directory crawling or new extraction."""
    try:
        if not context.get('root') or not context.get('source_sha256'):
            return None,'Raw metadata identity unavailable; showing recorded summary evidence.'
        root=Path(context['root']).resolve()
        manifest=json.loads(scoped_path(root,'analysis_run.json').read_text(encoding='utf-8'))
        recorded=mapping(mapping(manifest.get('artifacts')).get('investigation'))
        historical=mapping(context.get('historical'))
        expected=context if context.get('live') else historical
        expected_id = mapping(expected.get('storage')).get('forensic_result_id') or expected.get('result_id')
        if (not expected_id or recorded.get('result_id')!=expected_id
                or recorded.get('source_sha256')!=context['source_sha256']):
            raise ValueError('Stored metadata run identity does not match this investigation.')
        from investigation_storage import run_identity
        filename = ('evidence/metadata.json' if run_identity(root) else
                    Path(context.get('source_path') or '').stem+'_exif_signals.json')
        path=scoped_path(root,filename)
        if path.stat().st_size>16*1024*1024:
            raise ValueError('Recorded metadata payload exceeds the 16 MiB browsing limit.')
        payload=json.loads(path.read_text(encoding='utf-8'))
        if mapping(payload.get('file')).get('sha256')!=context['source_sha256']:
            raise ValueError('Recorded metadata source hash does not match.')
        return payload,'Recorded watchlist payload; the complete original ExifTool record is not persisted.'
    except (OSError,ValueError,TypeError,AttributeError) as error:
        return None,str(error)+' Showing recorded summary evidence only.'


def build_provenance(snapshot,data,payload=None,recovery_note=None):
    section=mapping(mapping(data.get('sections')).get('metadata'))
    signals=sequence(mapping(payload).get('signals')) or sequence(mapping(section.get('details')).get('metadata_signals'))
    stage=next((s for s in snapshot.stages if s.detector=='exif_payload'),None)
    extraction=(stage.status or 'Not recorded')+(': '+stage.reason if stage.reason else '') if stage else (
        'Execution status not recorded' if snapshot.summary.status=='completed' else 'No completed metadata analysis')
    limits=['Metadata presence and declarations do not authenticate image origin.',
            'Cryptographic provenance verification is unsupported by this backend.',
            'Missing provenance supports neither synthetic origin nor authenticity.',
            'Only recorded watchlist/signal fields are available; the full original metadata record is not retained.']
    if recovery_note:limits.append(recovery_note)
    entries={}
    observations=[]
    for assessment in sequence(mapping(data.get('reasoning_trace')).get('hypothesis_assessments')):
        for eid,detail in mapping(mapping(assessment).get('evidence_details')).items():
            if mapping(detail).get('section')=='metadata':
                for observed in sequence(mapping(detail).get('observations')):
                    observations.append((eid,mapping(observed)))

    def add(entry,origin,interpretation=None,source=False):
        if not isinstance(entry,dict):return
        tag=entry.get('raw_key')
        if not isinstance(tag,str) or not tag or 'value' not in entry:return
        value,binary=value_text(entry['value'])
        key=(tag,value)
        if key not in entries:
            namespace=entry.get('group') if isinstance(entry.get('group'),str) else tag.partition(':')[0]
            links=tuple(dict.fromkeys(eid for eid,observed in observations if observed.get('raw_key')==tag
                                     and value_text(observed.get('value'))[0]==value))
            entries[key]={'namespace':namespace,'origins':[],'interpretations':[],
                          'links':links,'binary':binary,'source':source}
        item=entries[key]
        if origin not in item['origins']:item['origins'].append(origin)
        if interpretation and interpretation not in item['interpretations']:item['interpretations'].append(str(interpretation))
    for bucket,items in mapping(mapping(payload).get('raw_watchlist_hits')).items():
        for entry in sequence(items):add(entry,'Recorded watchlist: '+str(bucket))
    for signal in signals:
        signal=mapping(signal)
        for entry in sequence(signal.get('evidence')):
            add(entry,'Recorded signal: '+str(signal.get('id','Not recorded')),signal.get('summary'))
    for key,value in mapping(mapping(payload).get('file')).items():
        add({'raw_key':'File:'+key,'group':'File identity','value':value},'Recorded source properties',source=True)
    fields=[]
    for (tag,value),item in entries.items():
        field_id=hashlib.sha256((tag+'\0'+value).encode('utf-8')).hexdigest()
        fields.append(MetadataField(field_id,tag,item['namespace'],value,
            value[:180]+('…' if len(value)>180 else ''),tuple(item['origins']),tuple(item['interpretations']),
            item['links'],'Recorded file identity' if item['source'] else 'Unverified metadata',item['binary']))
    return ProvenancePresentation(identity(snapshot),snapshot.provenance.declaration_status,
        snapshot.provenance.verification_status,extraction,tuple(limits),tuple(fields))
