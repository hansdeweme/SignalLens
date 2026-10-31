py -3.13 -m PyInstaller --noconfirm --clean --onedir --windowed --name SignalLens ^
 --hidden-import mediapipe.tasks.c ^
 --hidden-import mediapipe.tasks.python ^
 --hidden-import mediapipe.tasks.python.vision ^
 --add-binary "C:\Users\hans\AppData\Local\Programs\Python\Python313\Lib\site-packages\mediapipe\tasks\c\libmediapipe.dll;mediapipe\tasks\c" ^
 --add-data "selfie_segmenter.tflite;." ^
 --add-data "exif_rules.json;." ^
 --exclude-module sounddevice ^
  --exclude-module transformers ^
 --exclude-module torch ^
 --exclude-module torchvision ^
 --exclude-module tensorboard ^
 signallens_gui.py
copy .\signallens.png .\dist\SignalLens\signallens.png
copy .\signallens_settings.json .\dist\SignalLens\signallens_settings.json
copy .\README_FIRST.txt .\dist\SignalLens\README_FIRST.txt
copy /Y .\exiftool.exe .\dist\\SignalLens\exiftool.exe
robocopy "D:\Coding\AI detectie\exiftool_files" "D:\Coding\AI detectie\dist\SignalLens\exiftool_files" /E