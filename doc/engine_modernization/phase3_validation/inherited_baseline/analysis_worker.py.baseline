#analysis_worker.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#

from PyQt6.QtCore import QObject, pyqtSignal
from signallens_controller import SignalLensController

#--------------------------------------------
# multi-threaded worker to keep GUI responsive while processing
#------------------------------------------------

class AnalysisWorker(QObject):
    finished = pyqtSignal(object)        # AnalysisState
    error = pyqtSignal(str)
    log = pyqtSignal(str, str)           # message, level
    status = pyqtSignal(str)

    def __init__(self, selected_file, output_dir, output_json, analysis_mode):
        super().__init__()
        self.selected_file = selected_file
        self.output_dir = output_dir
        self.output_json = output_json
        self.analysis_mode = analysis_mode

    def run(self):
        try:
            controller = SignalLensController(
                log_fn=self.log.emit,
                status_fn=self.status.emit,
                summary_update_fn=None,
            )
            state = controller.run_analysis(
                selected_file=self.selected_file,
                output_dir=self.output_dir,
                output_json=self.output_json,
                analysis_mode=self.analysis_mode,
            )
            self.finished.emit(state)
        except Exception as e:
            self.error.emit(str(e))