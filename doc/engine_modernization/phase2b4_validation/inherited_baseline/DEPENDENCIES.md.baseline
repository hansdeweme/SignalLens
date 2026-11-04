# Dependency updates

The following versions are used with Python 3.13:

| Dependency | Previous version | Current version |
| --- | --- | --- |
| ExifTool | 13.37 | 13.60 |
| MediaPipe | 0.10.33 | 1.2.0 |

Install the pinned MediaPipe version into the Python environment used to run and
build SignalLens:

```powershell
py -3.13 -m pip install "mediapipe==1.2.0"
```

Download ExifTool 13.60 for Windows from <https://exiftool.org/> and place
`exiftool.exe` and its accompanying `exiftool_files` folder in the project root.
Keep these together when distributing SignalLens. These third-party files are
excluded from Git; cloning the repository does not install them.

Check the installed versions:

```powershell
.\exiftool.exe -ver
py -3.13 -m pip show mediapipe
```

Validation: ExifTool reports 13.60, MediaPipe reports 1.2.0, and the existing
MediaPipe Tasks segmentation function successfully processes a synthetic
128-by-128 image using `selfie_segmenter.tflite`. The packaged application has
not been rebuilt or tested as part of this update.
