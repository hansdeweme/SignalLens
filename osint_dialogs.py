#osint_dialogs.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages#
#
from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLineEdit, QMessageBox, QPlainTextEdit, QVBoxLayout
from osint_reverse_search import ReverseSearchMatch
from gui_design_system import apply_theme

class OSINTFindingDialog(QDialog):
    def __init__(self, parent=None, existing_match: Optional[ReverseSearchMatch] = None) -> None:
        super().__init__(parent)
        apply_theme(self)
        self.setWindowTitle("OSINT Finding")
        self.setModal(True)
        self.resize(520, 420)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["google", "yandex", "tineye", "bing", "other"])

        self.page_url_edit = QLineEdit()
        self.title_edit = QLineEdit()
        self.image_url_edit = QLineEdit()
        self.first_seen_edit = QLineEdit()
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems([
            "unknown",
            "stock",
            "ai_gallery",
            "social",
            "news",
            "marketplace",
            "other",
        ])

        self.similarity_spin = QDoubleSpinBox()
        self.similarity_spin.setRange(0.0, 1.0)
        self.similarity_spin.setSingleStep(0.01)
        self.similarity_spin.setDecimals(2)
        self.similarity_spin.setSpecialValueText("n/a")
        self.similarity_spin.setValue(0.0)

        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText(
            "Example: Higher-resolution version found; likely original stock upload."
        )

        form = QFormLayout()
        form.addRow("Provider", self.provider_combo)
        form.addRow("Result page URL *", self.page_url_edit)
        form.addRow("Title", self.title_edit)
        form.addRow("Source image URL", self.image_url_edit)
        form.addRow("Similarity (0.00 - 1.00)", self.similarity_spin)
        form.addRow("First-seen estimate", self.first_seen_edit)
        form.addRow("Source type", self.source_type_combo)
        form.addRow("Notes", self.notes_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if existing_match is not None:
            self.set_from_match(existing_match)

    def set_from_match(self, match: ReverseSearchMatch) -> None:
        self._set_combo_value(self.provider_combo, match.provider or "other")
        self.page_url_edit.setText(match.page_url or "")
        self.title_edit.setText(match.title or "")
        self.image_url_edit.setText(match.image_url or "")
        self.first_seen_edit.setText(match.first_seen_estimate or "")
        self._set_combo_value(self.source_type_combo, match.source_type or "unknown")
        self.similarity_spin.setValue(match.similarity_score if match.similarity_score is not None else 0.0)
        self.notes_edit.setPlainText(match.notes or "")

    def _set_combo_value(self, combo: QComboBox, value: str) -> None:
        index = combo.findText(value, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentText(value)

    def _on_accept(self) -> None:
        if not self.page_url_edit.text().strip():
            QMessageBox.warning(self, "Missing URL", "Result page URL is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        sim = self.similarity_spin.value()
        similarity_score = None if sim == 0.0 else sim

        return {
            "provider": self.provider_combo.currentText().strip(),
            "page_url": self.page_url_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "image_url": self.image_url_edit.text().strip(),
            "similarity_score": similarity_score,
            "first_seen_estimate": self.first_seen_edit.text().strip() or None,
            "source_type": self.source_type_combo.currentText().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
        }
