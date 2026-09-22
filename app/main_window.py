from __future__ import annotations

from pathlib import Path
import shutil
import time

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.config import CONFIG
from app.presets import categories_for_mode, modes, presets_for, StudioPreset
from app.prompt_engine import LookSettings, SubjectLocks, build_prompt
from app.services.invoke_client import InvokeClient
from app.widgets.image_panel import ImagePanel
from app.widgets.mask_editor import MaskEditorDialog
from app.workers.generation_worker import GenerationWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{CONFIG.app_name} v{CONFIG.version}")
        self.resize(1500, 900)

        self.invoke = InvokeClient()
        self.source_path: str | None = None
        self.result_path: str | None = None
        self.mask_path: str | None = None
        self.worker: GenerationWorker | None = None
        self.visible_presets: list[StudioPreset] = []

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        header = QHBoxLayout()
        brand = QLabel("CineStills AI Studio")
        brand.setObjectName("brand")
        tagline = QLabel("Change the scene. Keep the person.")
        tagline.setObjectName("tagline")
        self.connection = QLabel("InvokeAI: checking...")
        self.connection.setObjectName("connection")
        header.addWidget(brand)
        header.addWidget(tagline)
        header.addStretch(1)
        header.addWidget(self.connection)
        outer.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_canvas_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([285, 900, 330])
        outer.addWidget(splitter, 1)

        actions = QHBoxLayout()
        self.status = QLabel("Ready")
        self.status.setObjectName("status")

        self.generate = QPushButton("Generate Locally")
        self.generate.setObjectName("generateButton")
        self.generate.clicked.connect(self.generate_local)

        self.save = QPushButton("Save As")
        self.save.setEnabled(False)
        self.save.clicked.connect(self.save_result)

        actions.addWidget(self.status, 1)
        actions.addWidget(self.generate)
        actions.addWidget(self.save)
        outer.addLayout(actions)

        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #0F1117; color: #F3F5F7; font-size: 13px; }
            #brand { font-size: 24px; font-weight: 800; }
            #tagline, #status { color: #9CA3AF; margin-left: 12px; }
            #connection { color: #9CA3AF; }
            #panelTitle { font-weight: 800; color: #DCE1E8; letter-spacing: .5px; }
            #sectionTitle { color: #D7FF00; font-weight: 800; font-size: 12px; }
            #imageWell {
                background: #171A21;
                border: 1px solid #2B313D;
                border-radius: 14px;
                color: #7F8795;
            }
            QGroupBox {
                border: 1px solid #2B313D;
                border-radius: 12px;
                margin-top: 8px;
                padding: 10px;
                font-weight: 700;
                color: #DCE1E8;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QComboBox, QPlainTextEdit {
                background: #191D25;
                border: 1px solid #343B49;
                border-radius: 8px;
                padding: 8px 10px;
            }
            QPushButton {
                background: #191D25;
                border: 1px solid #343B49;
                border-radius: 8px;
                padding: 9px 12px;
                font-weight: 650;
            }
            QPushButton:hover { border-color: #737D91; }
            QPushButton:disabled { color: #6E7480; background: #171A21; }
            #generateButton {
                background: #D7FF00;
                color: #101217;
                font-weight: 900;
                padding: 12px 24px;
            }
            #generateButton:disabled { background: #687500; color: #B7BF8A; }
            #identityStrict {
                background: #14251E;
                color: #80F0B2;
                border: 1px solid #24573E;
                border-radius: 8px;
                padding: 8px 10px;
                font-weight: 800;
            }
            #identityGenerative {
                background: #2A2415;
                color: #FFD56A;
                border: 1px solid #5D4A1C;
                border-radius: 8px;
                padding: 8px 10px;
                font-weight: 800;
            }
            #maskActive {
                background: #24172B;
                color: #F2A7FF;
                border: 1px solid #623A70;
                border-radius: 8px;
                padding: 8px 10px;
                font-weight: 800;
            }
            #maskInactive {
                background: #171A21;
                color: #8D96A5;
                border: 1px solid #343B49;
                border-radius: 8px;
                padding: 8px 10px;
            }
            QCheckBox { spacing: 7px; }
            QScrollArea { border: none; background: transparent; }
            QFrame#sidePanel {
                background: #12151B;
                border: 1px solid #242A34;
                border-radius: 14px;
            }
            """
        )

        self.mode.currentTextChanged.connect(self._mode_changed)
        self.category.currentTextChanged.connect(self._category_changed)
        self.preset.currentTextChanged.connect(self._preset_changed)

        for combo in (self.lens, self.lighting, self.depth, self.color_grade, self.texture):
            combo.currentTextChanged.connect(self._refresh_prompt_preview)

        for checkbox in (
            self.lock_face,
            self.lock_hair,
            self.lock_body,
            self.lock_pose,
            self.lock_clothing,
            self.lock_skin,
        ):
            checkbox.toggled.connect(self._refresh_prompt_preview)

        self.custom_prompt.textChanged.connect(self._refresh_prompt_preview)

        self._populate_modes()
        self.check_invoke()

    def _build_left_panel(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("sidePanel")
        frame.setMinimumWidth(265)
        frame.setMaximumWidth(340)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        choose = QPushButton("Choose Photo")
        choose.clicked.connect(self.choose_photo)
        layout.addWidget(choose)

        title = QLabel("EDIT RECIPE")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)

        self.mode = QComboBox()
        self.category = QComboBox()
        self.preset = QComboBox()

        form.addRow("Mode", self.mode)
        form.addRow("Category", self.category)
        form.addRow("Preset", self.preset)
        layout.addLayout(form)

        self.identity_badge = QLabel("Subject Protection")
        self.identity_badge.setWordWrap(True)
        layout.addWidget(self.identity_badge)

        self.custom_prompt = QPlainTextEdit()
        self.custom_prompt.setPlaceholderText(
            "Optional instruction, e.g. add softer morning light or fewer props"
        )
        self.custom_prompt.setMaximumHeight(105)
        layout.addWidget(QLabel("Extra instruction"))
        layout.addWidget(self.custom_prompt)

        mask_title = QLabel("MAGIC BRUSH")
        mask_title.setObjectName("sectionTitle")
        layout.addWidget(mask_title)

        mask_actions = QHBoxLayout()
        paint_mask = QPushButton("Paint Edit Area")
        paint_mask.clicked.connect(self.edit_mask)
        clear_mask = QPushButton("Clear")
        clear_mask.clicked.connect(self.clear_edit_mask)
        mask_actions.addWidget(paint_mask, 1)
        mask_actions.addWidget(clear_mask)
        layout.addLayout(mask_actions)

        self.mask_badge = QLabel("No mask · generation can affect the full image")
        self.mask_badge.setWordWrap(True)
        self.mask_badge.setObjectName("maskInactive")
        layout.addWidget(self.mask_badge)

        layout.addStretch(1)
        return frame

    def _build_canvas_panel(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(10)

        self.original = ImagePanel("ORIGINAL", "Choose a photo to begin.")
        self.preview = ImagePanel("PREVIEW", "Your edited result will appear here.")
        layout.addWidget(self.original, 1)
        layout.addWidget(self.preview, 1)
        return container

    def _build_right_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(305)
        scroll.setMaximumWidth(390)

        frame = QFrame()
        frame.setObjectName("sidePanel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        subject = QGroupBox("Subject Lock")
        subject_layout = QVBoxLayout(subject)
        self.lock_face = QCheckBox("Preserve face / identity")
        self.lock_hair = QCheckBox("Preserve hair")
        self.lock_body = QCheckBox("Preserve body")
        self.lock_pose = QCheckBox("Preserve pose")
        self.lock_clothing = QCheckBox("Preserve clothing")
        self.lock_skin = QCheckBox("Preserve skin tone")

        for item in (
            self.lock_face,
            self.lock_hair,
            self.lock_body,
            self.lock_pose,
            self.lock_clothing,
            self.lock_skin,
        ):
            item.setChecked(True)
            subject_layout.addWidget(item)

        layout.addWidget(subject)

        look_group = QGroupBox("Cinematic Look")
        look_form = QFormLayout(look_group)

        self.lens = QComboBox()
        self.lens.addItems(["Natural", "35mm", "50mm", "85mm"])

        self.lighting = QComboBox()
        self.lighting.addItems(
            ["Match Source", "Golden Hour", "Soft Diffused Light", "Backlit", "Low Key"]
        )

        self.depth = QComboBox()
        self.depth.addItems(["Natural", "Shallow depth of field", "Deep focus"])

        self.color_grade = QComboBox()
        self.color_grade.addItems(
            ["Natural", "Warm Film", "Muted Editorial", "Teal-Orange", "Cool Cinematic"]
        )

        self.texture = QComboBox()
        self.texture.addItems(["Clean", "Fine film grain", "High dynamic range"])

        look_form.addRow("Lens", self.lens)
        look_form.addRow("Lighting", self.lighting)
        look_form.addRow("Depth", self.depth)
        look_form.addRow("Color", self.color_grade)
        look_form.addRow("Texture", self.texture)
        layout.addWidget(look_group)

        prompt_group = QGroupBox("Generated Prompt")
        prompt_layout = QVBoxLayout(prompt_group)
        self.prompt_preview = QPlainTextEdit()
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setMinimumHeight(210)
        prompt_layout.addWidget(self.prompt_preview)
        layout.addWidget(prompt_group)

        layout.addStretch(1)
        scroll.setWidget(frame)
        return scroll

    def _populate_modes(self) -> None:
        self.mode.blockSignals(True)
        self.mode.clear()
        self.mode.addItems(modes())
        self.mode.blockSignals(False)
        self._mode_changed(self.mode.currentText())

    def _mode_changed(self, mode: str) -> None:
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItems(categories_for_mode(mode))
        self.category.blockSignals(False)
        self._category_changed(self.category.currentText())

    def _category_changed(self, category: str) -> None:
        self.visible_presets = presets_for(self.mode.currentText(), category)
        self.preset.blockSignals(True)
        self.preset.clear()
        for item in self.visible_presets:
            self.preset.addItem(item.name)
        self.preset.blockSignals(False)
        self._preset_changed(self.preset.currentText())

    def _preset_changed(self, _name: str) -> None:
        preset = self.current_preset()
        if not preset:
            return

        if preset.strict_composite:
            self.identity_badge.setText(
                "STRICT SUBJECT LOCK\nOriginal subject pixels are composited back after generation."
            )
            self.identity_badge.setObjectName("identityStrict")
        else:
            self.identity_badge.setText(
                "GENERATIVE IDENTITY LOCK\nNeeded because this edit changes clothing, hair, product, or subject pixels."
            )
            self.identity_badge.setObjectName("identityGenerative")
        self.identity_badge.style().unpolish(self.identity_badge)
        self.identity_badge.style().polish(self.identity_badge)

        if preset.mode == "Dress & Fabric":
            self.lock_clothing.setChecked(False)
        elif preset.mode != "Retouch":
            self.lock_clothing.setChecked(True)

        self._refresh_prompt_preview()

    def current_preset(self) -> StudioPreset | None:
        index = self.preset.currentIndex()
        if index < 0 or index >= len(self.visible_presets):
            return None
        return self.visible_presets[index]

    def _locks(self) -> SubjectLocks:
        return SubjectLocks(
            face=self.lock_face.isChecked(),
            hair=self.lock_hair.isChecked(),
            body=self.lock_body.isChecked(),
            pose=self.lock_pose.isChecked(),
            clothing=self.lock_clothing.isChecked(),
            skin_tone=self.lock_skin.isChecked(),
        )

    def _look(self) -> LookSettings:
        return LookSettings(
            lens=self.lens.currentText(),
            lighting=self.lighting.currentText(),
            depth=self.depth.currentText(),
            color_grade=self.color_grade.currentText(),
            texture=self.texture.currentText(),
        )

    def build_current_prompt(self) -> str:
        preset = self.current_preset()
        if not preset:
            return ""
        return build_prompt(
            preset=preset,
            custom_instruction=self.custom_prompt.toPlainText(),
            locks=self._locks(),
            look=self._look(),
        )

    def _refresh_prompt_preview(self) -> None:
        if hasattr(self, "prompt_preview"):
            self.prompt_preview.setPlainText(self.build_current_prompt())

    def check_invoke(self) -> None:
        health = self.invoke.health()
        if health.ok:
            self.connection.setText("InvokeAI: Connected")
            self.connection.setStyleSheet("color: #80F0B2;")
        else:
            self.connection.setText("InvokeAI: Offline")
            self.connection.setToolTip(health.detail)
            self.connection.setStyleSheet("color: #FF9A9A;")

    def choose_photo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Photo",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)",
        )
        if not path:
            return

        self.source_path = path
        self.result_path = None
        self.mask_path = None
        self._update_mask_badge()
        self.original.set_image(path)
        self.preview.clear_image("Ready for local edit.")
        self.save.setEnabled(False)
        self.status.setText("Ready")

    def edit_mask(self) -> None:
        if not self.source_path:
            QMessageBox.information(self, "Choose a photo", "Select a source photo first.")
            return

        dialog = MaskEditorDialog(self.source_path, self)
        if not dialog.exec():
            return

        if not dialog.has_selection():
            QMessageBox.information(
                self,
                "No edit area selected",
                "Paint at least one area before saving the Magic Brush mask.",
            )
            return

        mask_dir = Path.cwd() / "temp" / "masks"
        mask_dir.mkdir(parents=True, exist_ok=True)
        mask_path = mask_dir / f"cinestills-mask-{int(time.time() * 1000)}.png"
        if not dialog.save_mask(mask_path):
            QMessageBox.warning(self, "Mask not saved", "CineStills could not save the edit mask.")
            return

        self.mask_path = str(mask_path)
        self._update_mask_badge()
        self.status.setText("Magic Brush active · only the painted area may change.")

    def clear_edit_mask(self) -> None:
        self.mask_path = None
        self._update_mask_badge()
        self.status.setText("Magic Brush cleared.")

    def _update_mask_badge(self) -> None:
        if not hasattr(self, "mask_badge"):
            return
        if self.mask_path:
            self.mask_badge.setText("MAGIC BRUSH ACTIVE\nOnly the painted area may change.")
            self.mask_badge.setObjectName("maskActive")
        else:
            self.mask_badge.setText("No mask · generation can affect the full image")
            self.mask_badge.setObjectName("maskInactive")
        self.mask_badge.style().unpolish(self.mask_badge)
        self.mask_badge.style().polish(self.mask_badge)

    def generate_local(self) -> None:
        if not self.source_path:
            QMessageBox.information(self, "Choose a photo", "Select a source photo first.")
            return

        preset = self.current_preset()
        if not preset:
            QMessageBox.information(self, "Choose a preset", "Select an edit preset first.")
            return

        health = self.invoke.health()
        if not health.ok:
            QMessageBox.warning(
                self,
                "InvokeAI is offline",
                "Start InvokeAI locally, then try again.\n\n" + health.detail,
            )
            return

        self.generate.setEnabled(False)
        self.save.setEnabled(False)
        self.preview.clear_image("Generating locally...")
        self.status.setText(f"Running {preset.name}...")

        self.worker = GenerationWorker(
            source_path=self.source_path,
            prompt=self.build_current_prompt(),
            base_url=self.invoke.base_url,
            strict_composite=preset.strict_composite,
            edit_mask_path=self.mask_path,
        )
        self.worker.status.connect(self.status.setText)
        self.worker.succeeded.connect(self.generation_succeeded)
        self.worker.failed.connect(self.generation_failed)
        self.worker.finished.connect(lambda: self.generate.setEnabled(True))
        self.worker.start()

    def generation_succeeded(self, path: str) -> None:
        self.result_path = path
        self.preview.set_image(path)
        self.save.setEnabled(True)

        preset = self.current_preset()
        if self.mask_path and preset and preset.strict_composite:
            self.status.setText("Done. Magic Brush edit applied with strict subject preservation.")
        elif self.mask_path:
            self.status.setText("Done. Magic Brush edit applied only inside the painted area.")
        elif preset and preset.strict_composite:
            self.status.setText("Done. Original subject pixels preserved.")
        else:
            self.status.setText("Done. Generative edit completed.")

    def generation_failed(self, message: str) -> None:
        self.result_path = None
        self.preview.clear_image("Generation failed.")
        self.status.setText("Generation failed")
        QMessageBox.critical(
            self,
            "Local generation failed",
            message
            + "\n\nIf dependencies were just updated, close CineStills and run setup.cmd once.",
        )

    def save_result(self) -> None:
        if not self.result_path:
            QMessageBox.information(self, "Nothing to save", "Generate an edited image first.")
            return

        destination, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Edited Photo",
            str(Path.home() / "cinestills-result.png"),
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)",
        )
        if not destination:
            return

        suffix = Path(destination).suffix.lower()
        if suffix in {".jpg", ".jpeg"} or "JPEG" in selected_filter:
            if suffix not in {".jpg", ".jpeg"}:
                destination += ".jpg"
            with Image.open(self.result_path) as image:
                image.convert("RGB").save(destination, quality=95)
        else:
            if not suffix:
                destination += ".png"
            shutil.copy2(self.result_path, destination)

        self.status.setText(f"Saved: {destination}")


def run_app() -> None:
    app = QApplication([])
    app.setApplicationName(CONFIG.app_name)
    window = MainWindow()
    window.show()
    app.exec()
