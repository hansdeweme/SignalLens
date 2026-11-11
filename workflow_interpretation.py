"""Bounded interpretation of declared ComfyUI graphs, never graph execution.

Only explicit known interfaces are understood. Coherence is not authentication;
unknown nodes on a saved output's dependency path require abstention.
"""
import hashlib
import json

SAVERS = {'SaveImage', 'Image Saver'}
SAMPLERS = {'KSampler', 'KSamplerAdvanced', 'SamplerCustom', 'SamplerCustomAdvanced'}
EMPTY = {'EmptyLatentImage', 'EmptySD3LatentImage', 'EmptyFlux2LatentImage'}
ENHANCERS = {'ImageUpscaleWithModel'}
KNOWN = SAVERS | SAMPLERS | EMPTY | ENHANCERS | {
    'VAEDecode', 'VAEEncode', 'VAEEncodeForInpaint', 'InpaintModelConditioning',
    'SetLatentNoiseMask', 'LoadImage', 'LoadImageMask', 'PreviewImage',
    'CheckpointLoaderSimple', 'UNETLoader', 'UNet loader with Name (Image Saver)',
    'CLIPLoader', 'DualCLIPLoader', 'TripleCLIPLoader', 'VAELoader', 'LoraLoader',
    'CLIPTextEncode', 'CFGGuider', 'BasicGuider', 'RandomNoise', 'DisableNoise',
    'KSamplerSelect', 'BasicScheduler', 'Flux2Scheduler', 'UpscaleModelLoader',
    'Seed Generator (Image Saver)', 'Width/Height Literal (Image Saver)',
    'Cfg Literal (Image Saver)', 'Int Literal (Image Saver)',
    'Sampler Selector (Image Saver)', 'String Literal (Image Saver)',
}
PROCESS_LABELS = {
    'full_image_generation': 'full-image generation from an empty latent',
    'image_to_image': 'image-to-image processing', 'inpainting': 'masked editing or inpainting',
    'enhancement': 'enhancement or upscaling', 'mixed': 'multiple creation or processing stages',
    'indeterminate': 'an indeterminate creation process',
}


class UnsupportedWorkflow(ValueError):
    pass


def workflow_container(entry):
    """Recognize structured prompt/workflow containers, including invalid JSON.

    Do not fall back to lexical declarations inside malformed graph containers.
    Ordinary prose in unstructured metadata retains the existing matcher.
    """
    value = entry.get('value')
    structured = isinstance(value, (dict, list)) or (isinstance(value, str) and value.lstrip().startswith(('{', '[')))
    if str(entry.get('tag', '')).lower() in {'prompt', 'workflow', 'parameters', 'generationdata', 'sd-metadata'}:
        return structured
    # Some exporters place ComfyUI graphs in Description/Comment instead.
    if structured:
        try:
            graph = json.loads(value) if isinstance(value, str) and len(value) <= 2_000_000 else value
            return isinstance(graph, dict) and ('nodes' in graph or any(
                isinstance(n, dict) and 'class_type' in n for n in graph.values()))
        except (ValueError, RecursionError):
            pass
    return False


def _graph(value):
    if isinstance(value, str):
        if len(value) > 2_000_000:
            raise UnsupportedWorkflow('Workflow exceeds the supported size limit.')
        value = json.loads(value)
    if not isinstance(value, dict) or not value or len(value) > 512:
        raise UnsupportedWorkflow('Expected a bounded ComfyUI graph object.')
    ui = 'nodes' in value
    raw_nodes = value.get('nodes') if ui else list(value.values())
    if not isinstance(raw_nodes, list) or not raw_nodes or len(raw_nodes) > 512:
        raise UnsupportedWorkflow('Workflow has no supported node collection.')
    if value.get('definitions') or value.get('subgraphs'):
        raise UnsupportedWorkflow('Nested workflows are not interpreted.')
    nodes = {}
    links = {}
    if ui:
        rows = value.get('links', [])
        if not isinstance(rows, list) or len(rows) > 4096:
            raise UnsupportedWorkflow('Unsupported workflow links.')
        for row in rows:
            if not isinstance(row, list) or len(row) != 6 or str(row[0]) in links:
                raise UnsupportedWorkflow('Invalid or duplicated workflow link.')
            links[str(row[0])] = row
    ids = [n.get('id') for n in raw_nodes if isinstance(n, dict)] if ui else list(value)
    if len(ids) != len(raw_nodes):
        raise UnsupportedWorkflow('Invalid workflow node.')
    for nid, raw in zip(ids, raw_nodes):
        if not isinstance(raw, dict) or str(nid) in nodes:
            raise UnsupportedWorkflow('Invalid or duplicated workflow node.')
        inputs = raw.get('inputs', [] if ui else {})
        edges = {}
        if ui:
            if not isinstance(inputs, list):
                raise UnsupportedWorkflow('Invalid UI inputs.')
            for slot, item in enumerate(inputs):
                if not isinstance(item, dict) or not isinstance(item.get('name'), str):
                    raise UnsupportedWorkflow('Invalid named UI input.')
                if item.get('link') is None:
                    continue
                row = links.get(str(item['link']))
                if row is None or str(row[3]) != str(nid) or row[4] != slot:
                    raise UnsupportedWorkflow('Missing or inconsistent UI link.')
                edges[item['name']] = (str(row[1]), row[2])
        else:
            if not isinstance(inputs, dict):
                raise UnsupportedWorkflow('Invalid API inputs.')
            for name, v in inputs.items():
                if isinstance(v, list):
                    if len(v) != 2:
                        raise UnsupportedWorkflow('Unsupported API input array.')
                    edges[name] = (str(v[0]), v[1])
        nodes[str(nid)] = {'type': raw.get('type' if ui else 'class_type'),
                           'mode': raw.get('mode', 0), 'edges': edges}
    for node in nodes.values():
        for source, slot in node['edges'].values():
            if source not in nodes or type(slot) is not int or slot < 0:
                raise UnsupportedWorkflow('Missing source or invalid output slot.')
    return nodes


def _interpret(value, source_field):
    nodes = _graph(value)
    sinks = sorted(nid for nid, n in nodes.items() if n['type'] in SAVERS and n['mode'] == 0)
    if not sinks:
        raise UnsupportedWorkflow('No active recognized saved output.')
    active, visiting = set(), set()

    def visit(nid, depth=0):
        if depth > 64 or nid in visiting:
            raise UnsupportedWorkflow('Cyclic or excessively deep output dependencies.')
        if nid in active:
            return
        n = nodes[nid]
        if n['type'] not in KNOWN or n['mode'] != 0:
            raise UnsupportedWorkflow('Unknown, muted or bypassed node on saved-output path: ' + str(n['type']))
        required = {
            'KSampler': {'model', 'positive', 'negative', 'latent_image'},
            'KSamplerAdvanced': {'model', 'positive', 'negative', 'latent_image'},
            'SamplerCustomAdvanced': {'noise', 'guider', 'sampler', 'sigmas', 'latent_image'},
            'SamplerCustom': {'model', 'positive', 'negative', 'sampler', 'sigmas', 'latent_image'},
            'VAEDecode': {'samples', 'vae'}, 'VAEEncode': {'pixels', 'vae'},
            'VAEEncodeForInpaint': {'pixels', 'vae', 'mask'},
            'InpaintModelConditioning': {'pixels', 'vae', 'mask', 'positive', 'negative'},
            'CFGGuider': {'model', 'positive', 'negative'}, 'BasicGuider': {'model', 'conditioning'},
            'CLIPTextEncode': {'clip'}, 'LoraLoader': {'model', 'clip'},
            'ImageUpscaleWithModel': {'image', 'upscale_model'},
        }.get(n['type'], set())
        if not required.issubset(n['edges']):
            raise UnsupportedWorkflow('Required connected inputs are missing: ' + str(n['type']))
        visiting.add(nid)
        for src, _ in n['edges'].values():
            visit(src, depth + 1)
        visiting.remove(nid)
        active.add(nid)

    for sink in sinks:
        visit(sink)

    def ancestors(sink):
        found, pending = set(), [sink]
        while pending:
            nid = pending.pop()
            if nid not in found:
                found.add(nid)
                pending.extend(src for src, _ in nodes[nid]['edges'].values())
        return found

    paths = []

    def flow(nid, port, trail):
        edge = nodes[nid]['edges'].get(port)
        if edge is None:
            raise UnsupportedWorkflow('Required image/latent input is missing: ' + port)
        src, slot = edge
        kind = nodes[src]['type']
        # Output semantics for the supported image/latent path, not just names.
        allowed = {0, 1} if kind in SAMPLERS else {2} if kind == 'InpaintModelConditioning' else {0}
        if slot not in allowed:
            raise UnsupportedWorkflow('Unsupported image/latent output slot.')
        path = [src] + trail
        if kind in EMPTY:
            paths.append(path)
            return ['empty']
        if kind == 'LoadImage':
            paths.append(path)
            return ['image']
        if kind in SAMPLERS:
            return flow(src, 'latent_image', path) + ['sample']
        if kind == 'VAEDecode':
            return flow(src, 'samples', path) + ['decode']
        if kind == 'VAEEncode':
            return flow(src, 'pixels', path) + ['encode']
        if kind in {'VAEEncodeForInpaint', 'InpaintModelConditioning'}:
            if 'mask' not in nodes[src]['edges']:
                raise UnsupportedWorkflow('Masked processing lacks a connected mask.')
            return flow(src, 'pixels', path) + ['mask']
        if kind == 'SetLatentNoiseMask':
            if 'mask' not in nodes[src]['edges']:
                raise UnsupportedWorkflow('Latent mask is missing.')
            return flow(src, 'samples', path) + ['mask']
        if kind in ENHANCERS:
            return flow(src, 'image', path) + ['enhance']
        raise UnsupportedWorkflow('Unsupported image/latent source: ' + str(kind))

    processes = []
    for sink in sinks:
        sink_active = ancestors(sink)
        stages = flow(sink, 'images', [sink])
        samples = stages.count('sample')
        if samples > 1 or ('enhance' in stages and samples):
            process = 'mixed'
        elif ('mask' in stages or any(nodes[n]['type'] == 'InpaintModelConditioning' for n in sink_active)) and samples and 'decode' in stages:
            process = 'inpainting'
        elif stages[0] == 'empty' and samples == 1 and stages[-1] == 'decode' and 'encode' not in stages and not any(
            nodes[n]['type'] in {'LoadImage', 'VAEEncode', 'VAEEncodeForInpaint', 'InpaintModelConditioning', 'SetLatentNoiseMask'} for n in sink_active):
            process = 'full_image_generation'
        elif stages[0] == 'image' and 'encode' in stages and samples and stages[-1] == 'decode':
            process = 'image_to_image'
        elif stages[0] == 'image' and 'enhance' in stages and not samples:
            process = 'enhancement'
        else:
            process = 'indeterminate'
        processes.append(process)
    if 'indeterminate' in processes:
        raise UnsupportedWorkflow('Saved output has no classified creation/processing path.')
    # Canonical connected interface graph: ignores UI positions, prompts, models,
    # widget defaults and disconnected preview nodes; never an authenticity hash.
    canonical = [(nid, nodes[nid]['type'], sorted(nodes[nid]['edges'].items())) for nid in sorted(active)]
    fingerprint = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
    return {'declared_process': processes[0] if len(set(processes)) == 1 else 'mixed',
            'graph_fingerprint': fingerprint,
            'supporting_node_paths': [{'source_field': source_field, 'nodes': path, 'sink_node': path[-1]}
                                      for path in paths]}


def interpret_workflows(entries):
    """One declaration across duplicate graph representations; fail closed on conflict."""
    unique = {}
    for e in entries:
        if isinstance(e, dict) and str(e.get('group', '')).lower() not in {'system', 'exiftool', 'composite'} and workflow_container(e):
            unique[(e.get('raw_key', e.get('tag', '')), str(e.get('value')))] = e
    entries = list(unique.values())
    if not entries:
        return None
    result = {'schema_version': 1, 'declared_process': 'indeterminate',
              'graph_interpretation_status': 'unsupported', 'provenance_authenticity': 'unverified',
              'source_fields': sorted({e.get('raw_key', e.get('tag', '')) for e in entries}),
              'supporting_node_paths': [], 'declaration_count': 0,
              'interpretation_limitations': ['Embedded workflows are unauthenticated declarations, not proof of execution or pixel origin.',
                                            'Recognized node interfaces are assumed; custom implementations are not authenticated.']}
    graphs = []
    try:
        for entry in entries:
            graphs.append(_interpret(entry.get('value'), entry.get('raw_key', entry.get('tag', ''))))
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        result['interpretation_limitations'].append(str(exc)[:240])
        return result
    if len({g['graph_fingerprint'] for g in graphs}) != 1:
        result['graph_interpretation_status'] = 'conflicting'
        result['interpretation_limitations'].append('Prompt/workflow graphs disagree; no single process is inferred.')
        return result
    result.update(declared_process=graphs[0]['declared_process'], graph_interpretation_status='coherent',
                  graph_fingerprint=graphs[0]['graph_fingerprint'], declaration_count=1,
                  supporting_node_paths=[p for g in graphs for p in g['supporting_node_paths']])
    return result


def workflow_description(interpretation):
    if not interpretation:
        return ''
    label = PROCESS_LABELS.get(interpretation.get('declared_process'), 'an indeterminate creation process')
    return ('Embedded workflow declares ' + label + '; provenance authenticity is unverified.'
            if interpretation.get('graph_interpretation_status') == 'coherent' else
            'Embedded workflow process is indeterminate or unsupported; provenance authenticity is unverified.')
