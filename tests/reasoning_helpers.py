"""Small connected metadata declarations; no model files or detector pipeline."""
from copy import deepcopy


def comfy_graph(process='full_image_generation'):
    nodes = {
        '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'enhanced_denoised.safetensors'}},
        '2': {'class_type': 'CLIPTextEncode', 'inputs': {'clip': ['1', 1], 'text': 'a landscape'}},
        '3': {'class_type': 'EmptyLatentImage', 'inputs': {'width': 64, 'height': 64, 'batch_size': 1}},
        '4': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['2', 0],
              'negative': ['2', 0], 'latent_image': ['3', 0], 'denoise': 1.0}},
        '5': {'class_type': 'VAEDecode', 'inputs': {'samples': ['4', 0], 'vae': ['1', 2]}},
        '6': {'class_type': 'SaveImage', 'inputs': {'images': ['5', 0]}},
    }
    if process in {'image_to_image', 'inpainting', 'enhancement'}:
        nodes['7'] = {'class_type': 'LoadImage', 'inputs': {'image': 'input.png'}}
    if process in {'image_to_image', 'inpainting'}:
        nodes['3'] = {'class_type': 'VAEEncode', 'inputs': {'pixels': ['7', 0], 'vae': ['1', 2]}}
        if process == 'inpainting':
            nodes['3']['class_type'] = 'VAEEncodeForInpaint'
            nodes['3']['inputs']['mask'] = ['7', 1]
    if process == 'enhancement':
        nodes['8'] = {'class_type': 'UpscaleModelLoader', 'inputs': {'model_name': 'upscale.pth'}}
        nodes['9'] = {'class_type': 'ImageUpscaleWithModel', 'inputs': {'image': ['7', 0], 'upscale_model': ['8', 0]}}
        nodes['6']['inputs']['images'] = ['9', 0]
    if process == 'indeterminate':
        nodes['9'] = {'class_type': 'UnknownImageOperation', 'inputs': {'image': ['5', 0]}}
        nodes['6']['inputs']['images'] = ['9', 0]
    return nodes


def ui_workflow(api):
    """Represent the same declared edges in the UI schema, plus an unused port."""
    nodes, links = [], []
    for nid, n in api.items():
        inputs = []
        for name, value in n['inputs'].items():
            if isinstance(value, list):
                link = len(links) + 1
                links.append([link, int(value[0]), value[1], int(nid), len(inputs), '*'])
                inputs.append({'name': name, 'link': link})
        nodes.append({'id': int(nid), 'type': n['class_type'], 'mode': 0, 'inputs': inputs,
                      'outputs': [{'name': 'output'}, {'name': 'denoised_output', 'links': None}],
                      'widgets_values': [deepcopy(n['inputs'])]})
    return {'nodes': nodes, 'links': links}
