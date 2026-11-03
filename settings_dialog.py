#settings_dialog.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Images
#
from __future__ import annotations
import json
import os
from   copy import deepcopy
from   pathlib import Path
from   typing import Any
from   PyQt6.QtCore import Qt
from   PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QSpinBox, QDoubleSpinBox, QTabWidget, QTextEdit, QVBoxLayout, QWidget,)
from   signallens_settings import SETTINGS_FILE, load_settings, save_settings, reset_settings_to_defaults
from gui_design_system import apply_theme
from gui_components import scroll_area


class SettingsDialog(QDialog):
    """
    GUI editor for SignalLens settings.
    Intended scope:
    - Safe user-facing settings.
    - Output directory.
    - Supported extensions.
    - Patch similarity profiles.
    - Subject/background sampling profiles.
    - Read-only JSON preview.
    Advanced decision-engine weights should stay out of this dialog for now.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        apply_theme(self)
        self.setWindowTitle("SignalLens Settings")
        self.resize(820, 720)
        self.settings: dict[str, Any] = deepcopy(load_settings())
        self.output_root_edit: QLineEdit | None = None
        self.extensions_edit: QLineEdit | None = None
        self.file_masks_edit: QLineEdit | None = None
        self.patch_widgets: dict[str, dict[str, QWidget]] = {}
        self.region_widgets: dict[str, dict[str, QWidget]] = {}
        self.json_preview: QTextEdit | None = None
        self._build_ui()
        self._load_values_into_ui()
        self._update_json_preview()

    # ---------------------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------------------
    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        description = QLabel(
            "Edit user-facing SignalLens settings. "
            "Changes are saved to signallens_settings.json and apply to the next analysis run."
        )
        description.setWordWrap(True)
        root_layout.addWidget(description)
        tabs = QTabWidget(self)
        tabs.addTab(scroll_area(self._build_general_tab()), "General")
        tabs.addTab(scroll_area(self._build_patch_profiles_tab()), "Patch Profiles")
        tabs.addTab(scroll_area(self._build_region_profiles_tab()), "Region Sampling")
        tabs.addTab(self._build_json_preview_tab(), "JSON Preview")
        root_layout.addWidget(tabs)
        button_row = QHBoxLayout()
        open_file_btn = QPushButton("Open Settings File")
        open_file_btn.clicked.connect(self._open_settings_file)
        button_row.addWidget(open_file_btn)
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_row.addWidget(reset_btn)
        button_row.addStretch(1)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._save_and_accept)
        self.button_box.rejected.connect(self.reject)
        button_row.addWidget(self.button_box)
        root_layout.addLayout(button_row)

    def _build_general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        group = QGroupBox("General")
        form = QFormLayout(group)
        self.output_root_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_root_edit)
        output_row.addWidget(browse_btn)
        browse_btn.clicked.connect(self._browse_output_root)
        form.addRow("Output folder:", output_row)
        self.extensions_edit = QLineEdit()
        self.extensions_edit.setPlaceholderText(".jpg, .jpeg, .png, .webp")
        form.addRow("Supported extensions:", self.extensions_edit)
        self.file_masks_edit = QLineEdit()
        self.file_masks_edit.setPlaceholderText("*.jpg *.jpeg *.png *.webp")
        form.addRow("File masks:", self.file_masks_edit)
        info = QLabel(
            "The output folder stores SignalLens audit trails. "
            "For heavy usage, consider placing it on a drive with enough free space."
        )
        info.setWordWrap(True)
        form.addRow("", info)
        layout.addWidget(group)
        layout.addStretch(1)
        return tab

    def _build_patch_profiles_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        explanation = QLabel(
            "Patch similarity profiles control patch size, stride and match limits. "
            "The GUI profile switch selects one of these profiles during analysis."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        profiles = self.settings.get("patch_similarity_profiles", {})
        for profile_name in sorted(profiles.keys()):
            group = QGroupBox(f"Patch profile: {profile_name}")
            form = QFormLayout(group)
            widgets: dict[str, QWidget] = {}
            widgets["patch_size"] = self._make_int_spinbox(4, 128)
            widgets["stride"] = self._make_int_spinbox(1, 128)
            widgets["descriptor_size"] = self._make_int_spinbox(4, 32)
            widgets["similarity_threshold"] = self._make_float_spinbox(0.0, 1.0, 3)
            widgets["max_pairs_to_keep"] = self._make_int_spinbox(1, 10000)
            widgets["max_pairs_for_overlay"] = self._make_int_spinbox(1, 1000)
            form.addRow("Patch size:", widgets["patch_size"])
            form.addRow("Stride:", widgets["stride"])
            form.addRow("Descriptor size:", widgets["descriptor_size"])
            form.addRow("Similarity threshold:", widgets["similarity_threshold"])
            form.addRow("Max pairs to keep:", widgets["max_pairs_to_keep"])
            form.addRow("Max pairs for overlay:", widgets["max_pairs_for_overlay"])
            self.patch_widgets[profile_name] = widgets
            layout.addWidget(group)
        layout.addStretch(1)
        return tab

    def _build_region_profiles_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        explanation = QLabel(
            "Region sampling profiles control how many subject, boundary and background "
            "samples downstream modules try to use."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        profiles = self.settings.get("subject_background_profiles", {})
        for profile_name in sorted(profiles.keys()):
            group = QGroupBox(f"Region profile: {profile_name}")
            form = QFormLayout(group)
            widgets: dict[str, QWidget] = {}
            widgets["subject"] = self._make_int_spinbox(1, 10000)
            widgets["boundary"] = self._make_int_spinbox(1, 10000)
            widgets["background"] = self._make_int_spinbox(1, 10000)
            form.addRow("Subject sample budget:", widgets["subject"])
            form.addRow("Boundary sample budget:", widgets["boundary"])
            form.addRow("Background sample budget:", widgets["background"])
            self.region_widgets[profile_name] = widgets
            layout.addWidget(group)
        layout.addStretch(1)
        return tab

    def _build_json_preview_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        label = QLabel("Preview of the settings that will be written to signallens_settings.json.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.json_preview = QTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.json_preview)
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self._refresh_from_ui_and_preview)
        layout.addWidget(refresh_btn)
        return tab

    # ---------------------------------------------------------------------
    # Widget factories
    # ---------------------------------------------------------------------
    def _make_int_spinbox(self, minimum: int, maximum: int) -> QSpinBox:
        box = QSpinBox()
        box.setRange(minimum, maximum)
        box.setAlignment(Qt.AlignmentFlag.AlignRight)
        box.valueChanged.connect(self._update_json_preview_from_ui_quietly)
        return box

    def _make_float_spinbox(self, minimum: float, maximum: float, decimals: int,) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(minimum, maximum)
        box.setDecimals(decimals)
        box.setSingleStep(0.005)
        box.setAlignment(Qt.AlignmentFlag.AlignRight)
        box.valueChanged.connect(self._update_json_preview_from_ui_quietly)
        return box

    # ---------------------------------------------------------------------
    # Loading / collecting settings
    # ---------------------------------------------------------------------
    def _load_values_into_ui(self) -> None:
        assert self.output_root_edit is not None
        assert self.extensions_edit is not None
        assert self.file_masks_edit is not None
        self.output_root_edit.setText(str(self.settings.get("output_root", "./analyzed/")))
        extensions = self.settings.get("supported_extensions", [])
        self.extensions_edit.setText(", ".join(extensions))
        file_masks = self.settings.get("file_masks", "")
        self.file_masks_edit.setText(str(file_masks))
        patch_profiles = self.settings.get("patch_similarity_profiles", {})
        for profile_name, widgets in self.patch_widgets.items():
            profile = patch_profiles.get(profile_name, {})
            self._set_spin(widgets["patch_size"], profile.get("patch_size", 24))
            self._set_spin(widgets["stride"], profile.get("stride", 12))
            self._set_spin(widgets["descriptor_size"], profile.get("descriptor_size", 8))
            self._set_spin(widgets["similarity_threshold"], profile.get("similarity_threshold", 0.965))
            self._set_spin(widgets["max_pairs_to_keep"], profile.get("max_pairs_to_keep", 300))
            self._set_spin(widgets["max_pairs_for_overlay"], profile.get("max_pairs_for_overlay", 60))
        region_profiles = self.settings.get("subject_background_profiles", {})
        for profile_name, widgets in self.region_widgets.items():
            profile = region_profiles.get(profile_name, {})
            self._set_spin(widgets["subject"], profile.get("subject", 96))
            self._set_spin(widgets["boundary"], profile.get("boundary", 64))
            self._set_spin(widgets["background"], profile.get("background", 128))
        self.output_root_edit.textChanged.connect(self._update_json_preview_from_ui_quietly)
        self.extensions_edit.textChanged.connect(self._update_json_preview_from_ui_quietly)
        self.file_masks_edit.textChanged.connect(self._update_json_preview_from_ui_quietly)

    def _set_spin(self, widget: QWidget, value: int | float) -> None:
        if isinstance(widget, QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value))

    def _collect_settings_from_ui(self) -> dict[str, Any]:
        assert self.output_root_edit is not None
        assert self.extensions_edit is not None
        assert self.file_masks_edit is not None
        settings = deepcopy(self.settings)
        output_root = self.output_root_edit.text().strip()
        if not output_root:
            output_root = "./analyzed/"
        supported_extensions = self._parse_extensions(self.extensions_edit.text())
        file_masks = self.file_masks_edit.text().strip()
        if not file_masks:
            file_masks = " ".join(f"*{ext}" for ext in supported_extensions)
        settings["output_root"] = output_root
        settings["supported_extensions"] = supported_extensions
        settings["file_masks"] = file_masks
        settings.setdefault("patch_similarity_profiles", {})
        for profile_name, widgets in self.patch_widgets.items():
            settings["patch_similarity_profiles"][profile_name] = {
                "patch_size": int(widgets["patch_size"].value()),
                "stride": int(widgets["stride"].value()),
                "descriptor_size": int(widgets["descriptor_size"].value()),
                "similarity_threshold": float(widgets["similarity_threshold"].value()),
                "max_pairs_to_keep": int(widgets["max_pairs_to_keep"].value()),
                "max_pairs_for_overlay": int(widgets["max_pairs_for_overlay"].value()),
            }
        settings.setdefault("subject_background_profiles", {})
        for profile_name, widgets in self.region_widgets.items():
            settings["subject_background_profiles"][profile_name] = {
                "subject": int(widgets["subject"].value()),
                "boundary": int(widgets["boundary"].value()),
                "background": int(widgets["background"].value()),
            }
        return settings

    def _parse_extensions(self, text: str) -> list[str]:
        raw_parts = text.replace(";", ",").replace(" ", ",").split(",")
        extensions: list[str] = []
        for part in raw_parts:
            ext = part.strip().lower()
            if not ext:
                continue
            if not ext.startswith("."):
                ext = "." + ext
            if ext not in extensions:
                extensions.append(ext)
        if not extensions:
            extensions = [".jpg", ".jpeg", ".png", ".webp"]
        return extensions

    # ---------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------
    def _validate_settings(self, settings: dict[str, Any]) -> tuple[bool, str]:
        output_root = str(settings.get("output_root", "")).strip()
        if not output_root:
            return False, "Output folder may not be empty."
        extensions = settings.get("supported_extensions", [])
        if not isinstance(extensions, list) or not extensions:
            return False, "At least one supported extension is required."
        for ext in extensions:
            if not isinstance(ext, str) or not ext.startswith("."):
                return False, f"Invalid extension: {ext}"
        patch_profiles = settings.get("patch_similarity_profiles", {})
        for profile_name, profile in patch_profiles.items():
            patch_size = int(profile.get("patch_size", 0))
            stride = int(profile.get("stride", 0))
            threshold = float(profile.get("similarity_threshold", 0.0))
            if patch_size <= 0:
                return False, f"Patch size must be positive for profile '{profile_name}'."
            if stride <= 0:
                return False, f"Stride must be positive for profile '{profile_name}'."
            if stride > patch_size:
                return False, (
                    f"Stride should not exceed patch size for profile '{profile_name}'."
                )
            if not (0.0 <= threshold <= 1.0):
                return False, (
                    f"Similarity threshold must be between 0 and 1 for profile '{profile_name}'."
                )
        region_profiles = settings.get("subject_background_profiles", {})
        for profile_name, profile in region_profiles.items():
            for key in ("subject", "boundary", "background"):
                value = int(profile.get(key, 0))
                if value <= 0:
                    return False, (
                        f"Region sample budget '{key}' must be positive "
                        f"for profile '{profile_name}'."
                    )
        return True, ""

    # ---------------------------------------------------------------------
    # Actions
    # ---------------------------------------------------------------------
    def _browse_output_root(self) -> None:
        assert self.output_root_edit is not None
        current = self.output_root_edit.text().strip() or "."
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select SignalLens Output Folder",
            current,
        )
        if folder:
            self.output_root_edit.setText(folder)

    def _refresh_from_ui_and_preview(self) -> None:
        self.settings = self._collect_settings_from_ui()
        self._update_json_preview()

    def _update_json_preview_from_ui_quietly(self) -> None:
        try:
            preview_settings = self._collect_settings_from_ui()
            self._update_json_preview(preview_settings)
        except Exception:
            # Avoid interrupting typing/spinbox edits.
            pass

    def _update_json_preview(self, settings: dict[str, Any] | None = None) -> None:
        if self.json_preview is None:
            return
        if settings is None:
            settings = self.settings
        self.json_preview.setPlainText(
            json.dumps(settings, indent=4, ensure_ascii=False)
        )

    def _save_and_accept(self) -> None:
        settings = self._collect_settings_from_ui()
        ok, message = self._validate_settings(settings)
        if not ok:
            QMessageBox.warning(self, "Invalid Settings", message)
            return
        try:
            save_settings(settings)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Could not save settings:\n\n{exc}",
            )
            return
        QMessageBox.information(self, "Settings Saved", "Settings saved. They will be used for the next analysis run.", )
        self.accept()

    def _reset_to_defaults(self) -> None:
        reply = QMessageBox.warning(
            self,
            "Reset Settings",
            "Reset all SignalLens settings to defaults?\n\n"
            "This will overwrite signallens_settings.json.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.settings = deepcopy(reset_settings_to_defaults())
            self._load_values_into_ui()
            self._update_json_preview()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Reset Failed",
                f"Could not reset settings:\n\n{exc}",
            )

    def _open_settings_file(self) -> None:
        path = Path(SETTINGS_FILE).resolve()
        if not path.exists():
            QMessageBox.warning(
                self,
                "Settings File Not Found",
                f"Settings file does not exist:\n\n{path}",
            )
            return
        try:
            os.startfile(path)  # Windows
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Open Failed",
                f"Could not open settings file:\n\n{exc}",
            )
