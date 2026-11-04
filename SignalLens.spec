# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['signallens_gui.py'],
    pathex=[],
    binaries=[('C:\\Users\\hans\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\mediapipe\\tasks\\c\\libmediapipe.dll', 'mediapipe\\tasks\\c')],
    datas=[('selfie_segmenter.tflite', '.'), ('exif_rules.json', '.')],
    hiddenimports=['mediapipe.tasks.c', 'mediapipe.tasks.python', 'mediapipe.tasks.python.vision'] + collect_submodules('scipy._external.array_api_compat.numpy'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SignalLens',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SignalLens',
)
