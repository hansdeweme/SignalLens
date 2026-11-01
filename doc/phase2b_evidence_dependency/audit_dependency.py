"""Deterministic, read-only source/trace audit; writes only this audit directory.

Run from the repository root: py -3.13 doc/phase2b_evidence_dependency/audit_dependency.py
No image access, detector execution, production mutation or confidence rerouting.
Only sanitized identifiers, expressions and aggregate numbers leave local traces.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import json
from math import fsum, isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scorecard_integrity import COMPONENT_FIELDS, BOOST_FIELDS, reconstruct_scorecard_calculation

# key | source function | inputs | measurement | family | dependency | controls | hypotheses | scoring
CATALOG_TEXT = """
metadata|exiftool_backend.analyze_file_with_exiftool|embedded EXIF/XMP/IPTC/PNG fields|watchlist and workflow/source-type declarations; camera field richness|provenance|direct|embedded-field filtering; unverified state; sparse neutral|synthetic_origin;camera_acquisition|base status; provenance boost; camera support; prior and route flags
osint|summary_sections.build_osint_section|analyst-recorded reverse-search review|matches and dominant source category; no autonomous retrieval in headless controller|provenance|partial|review/match gate; AI gallery is context, not authentication|synthetic_origin|base status; joint metadata/OSINT provenance branch; routes
ela|vf_ela.run_ela|original pixels and JPEG recompression|absolute original/recompressed difference; 64px block means and hotspots|processing|direct|format/native JPEG caveat; recompression quality estimate; summary neutral|localized_editing|no direct base/boost; upstream of cross/boundary/focus and weak-signal gates
noise|vf_noise.run_noise_analysis|original luminance pixels|absolute luminance minus Gaussian blur radius 1.5; blockwise residual hotspots|processing|partial|texture-sensitive residual proxy; summary neutral|localized_editing|no direct base/boost; upstream of cross/boundary/focus and weak-signal gates
cross_signal|vf_cross_signal.compute_cross_signal_payload|ELA/noise top_blocks and patterns; grid geometry|neighbor-distance overlap; connected clusters; filtered shared hotspot_mask|processing|direct|matching block sizes/geometry; runs without person mask|localized_editing|base; local +1; clone +0.15; synergy/gating; confidence count
boundary|vf_cross_signal.classify_boundary_convergence|same overlap plus ELA/noise pattern dictionaries|connected contour-shape and overlap interpretation|processing|direct|supportive parents and contour/fragment rules; no independent person geometry|localized_editing|base; local +2 or +0.5; synergies; clone +0.05; confidence count
boundary_focus|vf_boundary_focus.run_boundary_focus_analysis|saved ELA/residual maps and selected masks|masked subject/boundary/background intensity means; ratios and transition differences|processing|direct|person mask required; grid resize; visual-map/overlay fallback caveat|localized_editing|base; boundary corroboration count/strength; no dedicated boost
segmentation_alignment|vf_segmentation_alignment.compute_segmentation_boundary_alignment|cross hotspot_mask and selected boundary band|hotspot overlap fraction times boundary-coverage penalty|processing|direct|person mask required; nearest-neighbor coordinate alignment|localized_editing|base; boundary alias local; edit +0.25/+0.10 and cross synergy; corroboration gate
fft|vf_fft.run_fft_analysis|prepared global grayscale pixels|Hann-window log FFT; radial features; off-center symmetric peaks; axis anisotropy; reconstructed grid response|spectral|partial|center/edge exclusions; max dimension; periodic scenes and resizing caveats|synthetic_origin;localized_editing|base; joint patch synthetic +1; boundary-stack gate; generation route
region_fft|vf_region_fft.run_region_fft_analysis|prepared subject image; selected subject/boundary/background masks|three soft mean-filled crops run through same run_fft_analysis; regional metric differences|spectral|partial|person mask; soft crop/padding and geometry alignment; not same cached global FFT|localized_editing;synthetic_origin|base; boundary safeguard; feeds asymmetry carry-forward; not an EvidenceSnapshot field
sensor_origin|vf_sensor_origin.run_sensor_origin_analysis|original grayscale pixels|sigma1.2 high-pass residual energy and 2x2 phase periodicity; block consistency|acquisition|partial|proxy for camera compatibility, not PRNU attribution; weak/inconclusive branches|camera_acquisition;localized_editing|benign/suspicious base; camera +1.25; local -0.2/+0.5; sensor +0.75 conditional; cautions and routes
cfa_demosaic|vf_cfa_demosaic.run_cfa_demosaic_analysis|original color pixels|R-G/B-G high-pass residual 2x2 phase structure and interpolation directionality|acquisition|partial|weak traces remain compatibility only; not sensor identification|camera_acquisition;localized_editing|base; camera +1; local -0.2/+0.35; sensor +0.4 conditional; cautions
compression_history|vf_compression_history.run_compression_history_analysis|original grayscale pixels|8px aligned versus off-grid boundary energy; block heterogeneity; texture-normalized double-JPEG proxy|compression|partial|heuristic history proxy, not DCT quantization-history proof|localized_editing;camera_acquisition|base; local +0.4; compression +0.75/+0.4/+0.35; consistency caution
patch_similarity|vf_patch_similarity.run_patch_similarity_analysis|prepared patch image|normalized resized patch descriptors; accelerated neighbor pairs; recurrence map and coverage|recurrence|partial|minimum image/patch size; distance/separation/retention limits; natural repetition caveat|localized_editing;synthetic_origin|base; clone score; joint FFT synthetic +1; coverage cautions; route flags
patch_spatial|vf_patch_spatial.run_patch_spatial_analysis|patch top_pairs; scale_info; selected masks|same retained pair endpoints/similarities classified by region topology and densities|recurrence|direct|person mask; coordinate remapping; no pairs -> inconclusive; retained-pair bias|localized_editing;synthetic_origin|base; clone +0.6/-0.75 conditional; route safeguards; no fresh pair search
subject_texture_consistency|vf_subject_texture_consistency.run_subject_texture_consistency_analysis|prepared subject image; subject/background masks|hybrid gradients/DCT/residual-stat descriptors; neighbor similarity; subject/background recurrence gap|surface|partial|focus-mask support; geometry/min patch count; repetitive background controls|synthetic_origin;localized_editing|base; local +0.75/+0.35; edit +0.4/+0.2; feeds asymmetry reliability and carry-forward
subject_process_asymmetry|vf_subject_process_asymmetry.run_subject_process_asymmetry_analysis|prepared subject image and masks; texture payload; regional FFT payload|patch variance/residual/entropy/gradient/DCT distributions and regional gaps; carry-forward|surface|direct|stratified rescue sampling; baseline reliability; geometry cap; subject-only/reverse fallback caveat|localized_editing;synthetic_origin|base; local +0.75/+0.4; edit +0.3/+0.15; material synergy; geometry attenuation; route flags
subject_material_realism|vf_subject_material_realism.run_subject_material_realism_analysis|prepared subject image and subject mask; shared asymmetry helper code|same patch feature extraction/aggregation; microtexture suppression; DCT stability; distribution compression|surface|partial|rescue-sampling factor; minimum patches; subject_based versus normal profile|synthetic_origin;localized_editing|base; local +1.5/+0.75/+0.35; edit +0.75/+0.4; synthetic +0.75/+0.4; multiple synergies
subject_boundary|vf_subject_boundary.run_subject_boundary_analysis|original pixels; internally generated gradient edge bands|texture/sharpness/residual/color/contrast differences across morphological edge rings|edge_transition|partial|not a person mask; summary demotes to neutral image-edge observation without reliable person mask|localized_editing|base; shared boundary alias local +0.75/+0.35; edit synergies; corroboration count/strength
region_masks|vf_person_subject_mask.derive_region_masks_from_person_mask|person mask; image geometry|morphological subject/boundary/background masks; area/support ratios|geometry|direct|central quality contract; person specificity; coverage max0.90; legacy opt-in|all hypotheses as reliability only|neutral base; alias region_segmentation supplies reliability to local/edit and aggregate geometry handling
region_segmentation|vf_region_segmentation.run_region_segmentation_analysis|selected masks|connected components; largest component; boundary density and area ratios|geometry|direct|person gate; output currently not built into summary_synthesizer sections|none currently; intended synthetic/context interpretations dormant|executed stage but no current score path; EvidenceSnapshot.region_segmentation aliases region_masks instead
person_subject_mask|vf_person_subject_mask.run_person_subject_mask_analysis|image and MediaPipe model|foreground confidence map; refined person-specific binary mask; coverage/components|geometry|direct|canonical reliability gates; rejection -> regional unavailability; fallback opt-in|all hypotheses as coverage only|no direct score; shared geometric ancestor of regional evidence
legacy_region_masks|vf_region_masks.run_region_mask_analysis|pixels and Canny edges|blurred saliency; Otsu largest-component mask; morphology|geometry|partial|explicit legacy fallback option; not independent person evidence|coverage only|disabled by default; selected-mask path only if explicitly enabled
prepared_images|image_gatekeeper.prepare_analysis_images|input pixels and analysis profiles|global/patch/subject resizes and coordinate scale records|geometry|direct|profile-specific scales; all derived from same input image|all hypotheses indirectly|no direct score; common preprocessing ancestor
overlay|vf_overlay.create_shared_boundary_overlays|cross cluster blocks; ELA/noise artifacts|presentation overlays only|presentation|direct|artifact failures handled by stage controller|none|no score; do not count display as new evidence
"""
FIELDS = ('identifier','source','inputs','measurement','family','dependency','controls','hypotheses','scoring')
CATALOG = {r[0]:dict(zip(FIELDS,r)) for line in CATALOG_TEXT.strip().splitlines() if (r:=line.split('|'))}
assert all(len(line.split('|')) == len(FIELDS) for line in CATALOG_TEXT.strip().splitlines())


def tree(name):
    return ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))


def function(module, name):
    return next(n for n in tree(module).body if isinstance(n, ast.FunctionDef) and n.name == name)


def write_csv(name, rows):
    with (OUT/name).open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


DERIVE = function('hypothesis_engine.py','derive_signals')
COMPUTE = function('hypothesis_engine.py','compute_scorecard')
ASSIGNMENTS = {}
for fn in (DERIVE, COMPUTE):
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Name): ASSIGNMENTS[t.id]=n.value


def assignments_with_guards(node, guards=()):
    if isinstance(node,ast.If):
        for child in node.body: yield from assignments_with_guards(child,guards+(node.test,))
        for child in node.orelse: yield from assignments_with_guards(child,guards+(ast.UnaryOp(op=ast.Not(),operand=node.test),))
        return
    if isinstance(node,ast.Assign): yield node,guards
    for child in ast.iter_child_nodes(node): yield from assignments_with_guards(child,guards)


DERIVED_ASSIGNMENTS={}
for node,guards in assignments_with_guards(DERIVE):
    for target in node.targets:
        if isinstance(target,ast.Attribute) and isinstance(target.value,ast.Name) and target.value.id=='d':
            DERIVED_ASSIGNMENTS.setdefault(target.attr,[]).append((node,guards))
for key,items in DERIVED_ASSIGNMENTS.items():
    ASSIGNMENTS['ds.'+key]=ast.Tuple(elts=[part for node,guards in items for part in (node.value,*guards)])


def ancestry(node, seen=frozenset()):
    """Static union of potential parents, not runtime causal attribution."""
    if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name):
        root,key=node.value.id,node.attr
        if root=='ev': return {'region_masks' if key=='region_segmentation' else key}
        if root=='ctx': return {'scene_context'}
        if root in ('d','ds'):
            token='ds.'+key
            if token not in seen and token in ASSIGNMENTS:
                return ancestry(ASSIGNMENTS[token],seen|{token})
        if root=='card': return {'component:'+key}
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='getattr' and len(node.args)>1:
        if isinstance(node.args[0],ast.Name) and node.args[0].id=='ds' and isinstance(node.args[1],ast.Constant):
            return ancestry(ast.Attribute(value=ast.Name(id='ds'),attr=node.args[1].value),seen)
    if isinstance(node,ast.Name) and node.id in ASSIGNMENTS and node.id not in seen:
        return ancestry(ASSIGNMENTS[node.id],seen|{node.id})
    result=set()
    for child in ast.iter_child_nodes(node): result |= ancestry(child,seen)
    return result


def calls_with_guards(node, guards=()):
    if isinstance(node,ast.If):
        for child in node.body: yield from calls_with_guards(child,guards+(node.test,))
        for child in node.orelse: yield from calls_with_guards(child,guards+(ast.UnaryOp(op=ast.Not(),operand=node.test),))
        return
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='ledger':
        yield node,guards
    for child in ast.iter_child_nodes(node): yield from calls_with_guards(child,guards)


def inventory():
    summary={n.name:n for n in tree('summary_sections.py').body if isinstance(n,ast.FunctionDef)}
    rows=[]
    for key,info in CATALOG.items():
        fnname='build_'+('region_mask' if key=='region_masks' else key)+'_section'
        fn=summary.get(fnname)
        vals={k:[] for k in ('domain','status','polarity','pattern')}
        if fn:
            for n in ast.walk(fn):
                if isinstance(n,ast.Assign):
                    for t in n.targets:
                        if isinstance(t,ast.Attribute) and t.attr in vals:
                            v=ast.unparse(n.value)
                            if v not in vals[t.attr]: vals[t.attr].append(v)
        srcmodule,srcfn=info['source'].rsplit('.',1) if '.' in info['source'] else ('','')
        try: citation=f'{srcmodule}.py:{function(srcmodule+".py",srcfn).lineno} {srcfn}'
        except (StopIteration,FileNotFoundError): citation='signallens_controller.py:run_analysis (method)'
        rows.append(dict(kind='detector_or_integration',evidence_identifier=key,source=citation,
            inputs=info['inputs'],underlying_measurement=info['measurement'],
            derived_signal='; '.join(vals['pattern']) or 'support/presentation only',
            status_polarity=json.dumps({k:vals[k] for k in ('status','polarity')},sort_keys=True),
            evidence_domain='; '.join(vals['domain']) or 'none',score_contribution=info['scoring'],
            hypotheses=info['hypotheses'],dependencies=info['dependency']+': '+info['inputs'],
            shared_evidence_group=info['family'],reliability_controls=info['controls'],
            failure_behavior='Controller run_stage records failed/skipped/unavailable; missing sections neutral/not_run; inactive observations weight zero',
            summary_source=f'summary_sections.py:{fn.lineno} {fnname}' if fn else 'no summary section'))
        if fn:
            patterns=set()
            for node in ast.walk(fn):
                if isinstance(node,ast.Compare) and ast.unparse(node.left) in {'pattern','metadata_status','section.pattern'}:
                    for value in node.comparators:
                        patterns |= {x.value for x in ast.walk(value) if isinstance(x,ast.Constant) and isinstance(x.value,str)}
                if isinstance(node,ast.Assign) and any(ast.unparse(t)=='section.pattern' for t in node.targets) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                    patterns.add(node.value.value)
                if key=='metadata' and isinstance(node,ast.Assign) and any(ast.unparse(t)=='metadata_map' for t in node.targets):
                    patterns |= {k.value for k in node.value.keys if isinstance(k,ast.Constant)}
            parent=rows[-1]
            for pattern in sorted(patterns):
                rows.append(dict(parent,kind='summary_pattern_contract',evidence_identifier=key+':'+pattern,
                    derived_signal=pattern,status_polarity='branch-defined in '+parent['summary_source']+'; possible values: '+parent['status_polarity'],
                    failure_behavior='Recognized contract; reachability depends on detector/profile and summary gates. Region-segmentation builder currently dormant.'))
    for key,items in DERIVED_ASSIGNMENTS.items():
        sources=sorted(ancestry(ASSIGNMENTS['ds.'+key]))
        rows.append(dict(kind='derived_interpretation',evidence_identifier='ds.'+key,
            source='; '.join(f'hypothesis_engine.py:{n.lineno} derive_signals' for n,g in items),inputs=';'.join(sources),
            underlying_measurement='; '.join(CATALOG[s]['measurement'] for s in sources if s in CATALOG),
            derived_signal='; '.join(f'{ast.unparse(n.value)} IF '+(' and '.join(ast.unparse(g) for g in guards) or 'always') for n,guards in items),status_polarity='inherits available sections; derived flag is not a new observation',
            evidence_domain='no new domain',score_contribution='see exact contribution_lineage.csv guards; also decision routes',
            hypotheses='inherits hypothesis scope; no new independent evidence',
            dependencies='direct transformation of listed parents',
            shared_evidence_group=';'.join(sorted({CATALOG[s]['family'] for s in sources if s in CATALOG})),
            reliability_controls='Phase2A active observation filtering; numeric validation; parent controls',
            failure_behavior='derived from available parents only; default values are gates, not measurements',
            summary_source='not a separate summary row'))
    write_csv('signal_inventory.csv',rows)
    return len(rows)


def lineage():
    rows=[]
    for key,info in CATALOG.items():
        if key in {'person_subject_mask','legacy_region_masks','prepared_images','overlay','region_segmentation'}: continue
        rows.append(dict(evidence_identifier='base:'+key,source='hypothesis_engine.py:compute_base_scores',
            source_measurements=info['measurement'],upstream_sections=key,contribution_path='active section status/polarity -> separate suspicious/benign base',
            raw_contribution='weak=0.5; medium=1.5; strong=3; neutral/inactive=0',
            adjusted_contribution='suspicious base enters camera-attenuated subtotal; benign base stays separate',
            shared_evidence_group=info['family'],dependency_classification=info['dependency'],
            risk='domain labels do not establish independence; ELA/noise/region_masks are neutral in current builders'))
    rows.append(dict(evidence_identifier='base:domain_bonus',source='hypothesis_engine.py:compute_base_scores',source_measurements='same active weighted section domains',upstream_sections='all active suspicious/benign sections',contribution_path='each polarity independently',raw_contribution='0.25*max(0,distinct_domains-1)',adjusted_contribution='suspicious bonus camera attenuated; benign bonus unchanged',shared_evidence_group='all families',dependency_classification='direct',risk='composite child domain may earn extra diversity credit'))
    for i,(call,guards) in enumerate(calls_with_guards(COMPUTE),1):
        field=ast.literal_eval(call.args[0]); op=call.func.attr; expr=ast.unparse(call.args[1])
        sources=ancestry(call.args[1])
        for g in guards: sources |= ancestry(g)
        sections=sorted(s for s in sources if s in CATALOG)
        family=sorted({CATALOG[s]['family'] for s in sections})
        reason=ast.literal_eval(call.args[2])
        rows.append(dict(evidence_identifier=f'operation:{i:03d}:{field}',source=f'hypothesis_engine.py:{call.lineno} compute_scorecard',
            source_measurements='; '.join(CATALOG[s]['measurement'] for s in sections) or 'component/analyst context; see upstream references',
            upstream_sections=';'.join(sorted(sources)),contribution_path=f'{op} {field}; guard={" and ".join(ast.unparse(g) for g in guards) or "always"}; reason={reason}',
            raw_contribution=expr,adjusted_contribution=('routing/intermediate only; not separately added to S' if field in {'clone_support_score','camera_counter_support','local_edit_support_score'} else 'edit reliability then camera factor for boosts; caution subtracts before geometry/photo factors; exact ledger order'),
            shared_evidence_group=';'.join(family) or 'component_or_context',
            dependency_classification='direct' if any(CATALOG[s]['dependency']=='direct' for s in sections) else 'partial' if sections else 'direct',
            risk='multiple paths are confirmed; redundant information or optimal weight is not empirically established'))
    for name,expr in (
        ('camera_attenuation','m=1/.85/.70/.55 for measured camera support <1/>=1/>=2/>=3'),
        ('suspicious_score','max(0,fsum(baseS,synthetic,edit,provenance,sensor,compression)*m-caution)*geometry*photo'),
        ('benign_score','base_benign; no inverse probability interpretation'),
        ('geometry_multiplier','.75 if unreliable geometry else1'),
        ('photo_context_multiplier','.70 if photo context prior else1')):
        rows.append(dict(evidence_identifier='aggregate:'+name,source='hypothesis_engine.py:compute_scorecard; scorecard_integrity.py:camera_attenuation',source_measurements='final ledger components and available section base',upstream_sections='see operation rows',contribution_path='final aggregation',raw_contribution=expr,adjusted_contribution=expr,shared_evidence_group='all applicable families',dependency_classification='direct',risk='nonlinear transform; do not sum upstream local/clone/camera totals again'))
    # Include every confidence/routing consumer as a guard, not an additive score.
    for fn in tree('decision_logic.py').body:
        if isinstance(fn,ast.FunctionDef) and (fn.name.startswith('route_') or fn.name in {'determine_confidence','_boundary_corroborated','evaluate_hypotheses','determine_dominant_pattern'}):
            tests=[ast.unparse(n.test) for n in ast.walk(fn) if isinstance(n,ast.If)]
            rows.append(dict(evidence_identifier='gate:'+fn.name,source=f'decision_logic.py:{fn.lineno} {fn.name}',source_measurements='same section flags, adjusted scorecard and hypothesis selection state',upstream_sections=';'.join(sorted({n.attr for n in ast.walk(fn) if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id in {'ds','ev','card'}})),contribution_path='non-additive pattern/tier/hypothesis selection',raw_contribution='; '.join(tests),adjusted_contribution='no numeric addition; can change which tier/pattern is selected',shared_evidence_group='routing',dependency_classification='direct',risk='counts/AND gates can reuse shared ancestry even when arithmetic reconciles'))
    write_csv('contribution_lineage.csv',rows)
    return len(rows),i


COMPOSITES={'cross_signal','boundary','boundary_focus','segmentation_alignment','region_fft','patch_spatial','subject_process_asymmetry'}


def adjusted_base(calc, remove=frozenset(), representatives=False):
    rows=[r for r in calc['base_evidence'] if r['polarity']=='suspicious' and r['section'] not in remove]
    if representatives:
        # Deliberately broad illustrative grouping, not a proposed calibrated formula.
        groups={}
        for r in rows:
            group=CATALOG[r['section']]['family']
            # Patch/subject texture/material/asymmetry share a deliberately broad recurrence family.
            if group in {'surface','recurrence'}: group='texture_recurrence'
            groups[group]=max(groups.get(group,0),r['weight'])
        return fsum(groups.values())+max(0,len(groups)-1)*.25
    return fsum(r['weight'] for r in rows)+max(0,len({r['domain'] for r in rows if r['domain']} )-1)*.25


def score(calc, base=None, components=None):
    c=components or calc['final_contributions']; t=calc['aggregate_transforms']
    q=fsum([calc['base_suspicious'] if base is None else base,*(c[f] for f in BOOST_FIELDS)])
    return max(0,q*t['camera_multiplier']-c['caution_penalty'])*t['geometry_multiplier']*t['photo_context_multiplier']


def no_composite_component_bonus(calc):
    # Freeze original guards, camera moderation and reliability operations.
    # Remove positive raw local/edit/clone additions tied to these derived parents.
    fields=dict.fromkeys(COMPONENT_FIELDS,0.0)
    needles=('ds.strong_local_edit','ds.fragmented_local_edit','ds.strong_cross','ds.segmentation_boundary',
             'boundary_stack','asym_strong','asym_medium','patch_spatial_supportive')
    removed=[]
    for index,op in enumerate(calc['component_operations']):
        f,operand=op['field'],op['operand']
        if op['reason']=='local_support_conversion': operand=.18*fields['local_edit_support_score']
        elif index<calc['raw_operation_count'] and f in {'local_edit_support_score','edit_boost','clone_support_score'} and op['operation']=='add' and operand>0 and any(n in op['reason'] for n in needles):
            removed.append(op['reason']); continue
        if op['operation']=='add': fields[f]+=operand
        elif op['operation']=='multiply': fields[f]*=operand
        elif op['operation']=='maximum': fields[f]=max(fields[f],operand)
    return fields,removed


def markdown_table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
        *['| '+' | '.join(str(c).replace('|','/').replace('\n',' ') for c in row)+' |' for row in rows]])


def reference_report():
    lines=['# Reference-case contribution and dependency analysis','',
        'Source: existing local Phase 2A full headless `subject_based` traces. No detector rerun was necessary. This report exports only section identifiers, arithmetic and hypothesis evidence identifiers; no images, filenames, embedded prompts, attribution values or raw detector payloads.', '',
        '## Diagnostic definitions and limits','',
        '- A: remove only downstream composite suspicious base rows (cross, boundary, focus, alignment, regional FFT, spatial patch, process asymmetry), recomputing the remaining domain bonus. Keep boosts/penalties fixed. This isolates base duplication exposure, not a full causal ablation.',
        '- B: remove positive raw local/edit/clone additions whose recorded reason depends on cross/boundary/segmentation-alignment/asymmetry/spatial corroboration; recalculate the 0.18 local-support conversion, then replay original reliability operations. Keep base rows, guards, synthetic/sensor/compression boosts and cautions fixed. Shared subject-boundary/alignment alias contributions are retained because the ledger cannot uniquely attribute their OR source.',
        '- C: keep the maximum suspicious base weight per illustrative family, with recurrence+surface combined, and replace domain diversity with family diversity. All boosts and penalties stay fixed. This deliberately broad grouping can discard new information.',
        '- D: set the five final boost fields to zero; retain all base, camera and caution terms. This isolates the additive boost layer, not evidence independence.',
        'All alternatives freeze original camera/geometry/photo transforms and penalty applicability. They do not reroute or recalculate confidence. These are conditional arithmetic diagnostics, not empirically validated replacement models. Any adopted formula needs recalibration; do not compare alternative totals to current tier thresholds.', '']
    impact=[]
    for case in ('instagram','midjourney'):
        path=ROOT/'analyzed/phase2a_validation'/case/'summary/reasoning_trace.json'
        trace=json.loads(path.read_text(encoding='utf-8')); calc=trace['scorecard_calculation']
        reconstructed=reconstruct_scorecard_calculation(calc)
        for field in (*COMPONENT_FIELDS,'suspicious_score','benign_score'):
            assert isclose(reconstructed[field],trace['scorecard'][field],rel_tol=1e-12,abs_tol=1e-12)
        assert isclose(score(calc),trace['scorecard']['suspicious_score'],rel_tol=1e-12,abs_tol=1e-12)
        altered,removed=no_composite_component_bonus(calc)
        no_boost=calc['final_contributions'].copy()
        for field in BOOST_FIELDS: no_boost[field]=0
        values=[score(calc),score(calc,base=adjusted_base(calc,COMPOSITES)),score(calc,components=altered),score(calc,base=adjusted_base(calc,representatives=True)),score(calc,components=no_boost)]
        impact.append((case,*[f'{v:.9f}' for v in values]))
        lines += ['## '+case.title(),'',f"Baseline: S={values[0]:.8f}, B={calc['base_benign']}; pattern `{trace['decision']['dominant_pattern']}`, confidence {trace['decision']['confidence_tier']}. Both serialized aggregates and all components reconstruct within 1e-12.",'',
            '### Complete base ledger','',markdown_table(('Section','Polarity','Status','Domain','Weight','Family'),[(r['section'],r['polarity'],r['status'],r['domain'],r['weight'],CATALOG[r['section']]['family']) for r in calc['base_evidence']]),'',
            f"Base S={calc['base_suspicious']} includes domain bonus; B={calc['base_benign']} includes its separate domain bonus.",'',
            '### Complete component ledger','',markdown_table(('Index','Field','Operation','Operand','Reason'),[(i+1,o['field'],o['operation'],format(o['operand'],'.15g'),o['reason']) for i,o in enumerate(calc['component_operations'])]),'',
            '### Raw and adjusted components','',markdown_table(('Field','Raw','Adjusted'),[(f,format(calc['raw_contributions'][f],'.15g'),format(calc['final_contributions'][f],'.15g')) for f in COMPONENT_FIELDS]),'',
            'Aggregate transforms: `'+json.dumps(calc['aggregate_transforms'],sort_keys=True)+'`.','',
            '### Base contributions grouped by mechanism','',markdown_table(('Family','Suspicious weights before domain bonus','Benign weights before domain bonus'),[(fam,fsum(r['weight'] for r in calc['base_evidence'] if r['polarity']=='suspicious' and CATALOG[r['section']]['family']==fam),fsum(r['weight'] for r in calc['base_evidence'] if r['polarity']=='benign' and CATALOG[r['section']]['family']==fam)) for fam in sorted({CATALOG[r['section']]['family'] for r in calc['base_evidence']})]),'',
            'B removed component reasons: '+('; '.join('`'+r+'`' for r in removed) or 'none')+'.','',
            '### Hypothesis-specific support','']
        for h in trace['hypothesis_assessments']:
            lines.append(f"- `{h['hypothesis_id']}`: {h['confidence_tier']}; supporting: "+(', '.join('`'+s+'`' for s in h['supporting_evidence']) or 'none')+'; moderating: '+(', '.join('`'+s+'`' for s in h['moderating_evidence']) or 'none')+'.')
        coverage=trace['pipeline_status']['coverage']
        lines += ['', 'Coverage status: `'+str(coverage.get('status'))+'`. Unavailable section keys: '+(', '.join(k for k,v in trace['section_snapshot'].items() if v['status'] in {'not_run','unavailable','skipped','failed'}) or 'none')+'.','']
    lines += ['## Conditional numerical ablations','',markdown_table(('Case','Baseline','A composites base removed','B corroboration components removed','C representative family bases','D boost layer removed'),impact),'',
        '## Interpretation of ancestry and numerical exposure','',
        'Instagram processing ancestry contributes base cross 0.5 + boundary 3 + focus 1.5 = 5, plus two incremental domain bonuses (0.5 relative to keeping one existing processing domain). Its boundary local +2 contributes 0.36 through conversion to edit; cross is partial so strong-cross component synergies are inactive; focus adds no dedicated boost. Holding everything else fixed, keeping only boundary of these three removes 2.5 from Q, or 2.125 from S. The broader A also removes patch spatial 1.5 and asymmetry 0.5 and their diversity credit.', '',
        'Instagram recurrence/surface base weights are patch 1.5 + spatial patch 1.5 + texture 1.5 + asymmetry 0.5 + material 1.5 = 6.5 (diversity accounted separately). Texture contributes local 0.75 -> edit 0.135 plus direct edit 0.4. Asymmetry contributes local 0.4 -> edit 0.072 plus direct edit 0.15. Material contributes local 0.75 -> edit 0.135 plus direct edit 0.4 and synthetic 0.4. Their respective additive extras in Q are 0.535, 0.222 and 0.935; these are multiple paths, not independent likelihoods. Compression contributes base 3, local 0.4 -> edit 0.072 and compression boost 0.75. Subject boundary contributes base 3 and boundary-alias local 0.75 -> edit 0.135. These explain all 1.823 edit units once camera local tempering contributes -0.036. Do not add local total 4.85 again.', '',
        'Midjourney processing base cross 1.5 + boundary 0.5 derives from the same hotspot overlap. Its raw local 0.5 + 1 - 0.2 = 1.3 and raw edit synergy 0.5 + conversion 0.234 = 0.734 are both zero after boundary reliability r=0. Base cross/boundary weights remain: reliability applies to mechanisms, not the whole base layer. Its metadata base 1.5 + provenance boost 0.75 represents one declaration family; two supporting metadata identifiers in the narrative do not add two further score terms. With five suspicious domains, attributing an incremental domain bonus to removal of metadata adds 0.25: removing that base row and boost alone reduces Q by 2.5 and S by 2.125, holding other terms fixed. Hypothesis support remains unverified, and the reference is not proof that provenance is correct.', '',
        'Camera support is reused deliberately in both cases: sensor benign base 1.5; measured camera +1.25 produces m=0.85 and caution 1.25; local tempering -0.2 propagates through edit (removed by r=0 on Midjourney). Instagram additionally receives clean-context caution 0.35, and weak benign CFA adds base 0.5 plus a 0.25 second-domain bonus but no measured-camera increment. These are separate model effects, not extra independent observations.', '',
        'Instagram has 23 completed / 0 skipped / 0 failed stages and reliable mask coverage 0.5961422390407987. Midjourney has 14 completed / 9 unavailable-or-skipped / 0 failed and unreliable coverage 0.9181777419747081 under the unchanged 0.90 limit. Cross-signal succeeds on both. No unavailable regional measurement is imputed. Two cases cannot estimate dependence, false-positive rates, accuracy or calibration.', '']
    (OUT/'reference_case_analysis.md').write_text('\n'.join(lines),encoding='utf-8')
    return impact


def main():
    protected={p:hashlib.sha256(p.read_bytes()).hexdigest() for directory in (ROOT,ROOT/'tests') for p in directory.glob('*.py')}
    n=inventory(); rows,ops=lineage(); impact=reference_report()
    # Exact coverage: every built summary section has a detector inventory record.
    builder=function('summary_synthesizer.py','build_summary_result')
    built={n.targets[0].slice.value for n in ast.walk(builder) if isinstance(n,ast.Assign)
        and isinstance(n.targets[0],ast.Subscript) and isinstance(n.targets[0].value,ast.Attribute)
        and n.targets[0].value.attr=='sections' and isinstance(n.targets[0].slice,ast.Constant)}
    assert built <= CATALOG.keys(),built-CATALOG.keys()
    assert 'region_segmentation' not in built
    for name in ('signal_inventory.csv','contribution_lineage.csv'):
        with (OUT/name).open(encoding='utf-8',newline='') as f:
            records=list(csv.DictReader(f))
        ids=[r['evidence_identifier'] for r in records]
        assert len(ids)==len(set(ids)),f'Duplicate evidence identifiers in {name}'
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==value for p,value in protected.items())
    print(json.dumps({'inventory_rows':n,'lineage_rows':rows,'ledger_operation_sites':ops,
        'summary_sections_covered':len(built),'ablation_scores':impact},indent=2))


if __name__=='__main__': main()
