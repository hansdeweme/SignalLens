"""Documented onedir build flags, with isolated build/spec/dist directories."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
work=OUT/'validation_output/packaging'
work.mkdir(parents=True,exist_ok=True)
import mediapipe
dll=Path(mediapipe.__file__).parent/'tasks/c/libmediapipe.dll'
cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--windowed','--name','SignalLens',
    '--distpath',str(work/'dist'),'--workpath',str(work/'work'),'--specpath',str(work),
    '--hidden-import','mediapipe.tasks.c','--hidden-import','mediapipe.tasks.python','--hidden-import','mediapipe.tasks.python.vision',
    '--collect-submodules','scipy._external.array_api_compat.numpy',
    '--add-binary',str(dll)+';mediapipe/tasks/c','--add-data',str(ROOT/'selfie_segmenter.tflite')+';.',
    '--add-data',str(ROOT/'exif_rules.json')+';.']
for name in ('sounddevice','transformers','torch','torchvision','tensorboard'):cmd+=['--exclude-module',name]
cmd.append(str(ROOT/'signallens_gui.py'))
if '--incremental' in sys.argv:cmd.remove('--clean')
start=time.perf_counter()
with (work/'build.log').open('w',encoding='utf-8') as log:
    result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
data={'command':cmd,'returncode':result.returncode,'build_seconds':time.perf_counter()-start}
if result.returncode==0:
    destination=work/'dist/SignalLens'
    for name in ('signallens.png','signallens_settings.json','README_FIRST.txt','exiftool.exe'):
        shutil.copy2(ROOT/name,destination/name)
    shutil.copytree(ROOT/'exiftool_files',destination/'exiftool_files',dirs_exist_ok=True)
    # Keep packaged acceptance outputs distinct from source runs.
    settings=json.loads((destination/'signallens_settings.json').read_text())
    settings['output_root']=str(OUT/'validation_output/packaged_runs')
    (destination/'signallens_settings.json').write_text(json.dumps(settings,indent=2))
    data['executable']=str(destination/'SignalLens.exe')
    data['resources']={name:(destination/name).exists() for name in ('exiftool.exe','exiftool_files','signallens_settings.json',
        'signallens.png','_internal/selfie_segmenter.tflite','_internal/exif_rules.json','_internal/PyQt6/Qt6/plugins/platforms/qwindows.dll')}
(OUT/'packaging_results.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data,indent=2),flush=True)
