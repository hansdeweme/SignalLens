"""Small explicit GUI setup helpers; no fixtures or test collection side effects."""
import json
from pathlib import Path
from PyQt6.QtTest import QTest
from signallens_controller import AnalysisState
from summary_types import SummaryResult


def publish(window,source):
    window.set_selected_file(source)
    token=window.session.begin_analysis('normal',{},window.settings,window.settings['output_root'])
    data=SummaryResult(full_text='Recorded narrative',full_html='<p>Recorded narrative</p>',
        reasoning_trace={'decision':{'primary_hypothesis':'synthetic_origin','confidence_tier':'Medium',
            'dominant_pattern':'declared_synthetic_candidate','selection_reason':'Recorded selection'},
            'hypothesis_assessments':[{'hypothesis_id':'synthetic_origin','explanation':'Unverified generation declaration.',
                'confidence_tier':'Medium','supporting_evidence':['metadata:DECLARED_SYNTHETIC'],
                'contradicting_evidence':[],'moderating_evidence':[],'contextual_evidence':[],
                'limitations':['Metadata authenticity is unverified.'],
                'evidence_details':{'metadata:DECLARED_SYNTHETIC':{'label':'Generation declaration','section':'metadata',
                    'interpretation':'An unverified declaration.'}}}],
            'provenance_evidence':{'state':'unverified_generation_declaration','metadata_authenticity_verified':False},
            'pipeline_status':{'coverage':{'status':'partial'},'stages':{'Region FFT':{'status':'unavailable','reason':'No reliable mask'}}}})
    state=AnalysisState(Path(token.image_path),Path(token.output_dir))
    state.output_dir.mkdir(parents=True)
    window.session.complete(token,state,data)
    window.analysis_state=state
    window.current_analysis_dir=state.output_dir
    window.update_summary()
    return token


def wait_for(app,predicate):
    for _ in range(200):
        app.processEvents()
        if predicate():return
        QTest.qWait(10)
    assert predicate(),'preview did not complete'


def set_trace(window,trace):
    data=window.session.summary_data()
    data['reasoning_trace']=trace
    window.session.summary_json=json.dumps(data)
    window.update_summary()
