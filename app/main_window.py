from __future__ import annotations

import json
from pathlib import Path
import shutil
import time

from PIL import Image
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import CONFIG
from app.presets import categories_for_mode, modes, presets_for, StudioPreset
from app.prompt_engine import LookSettings, SubjectLocks, build_prompt, finalize_prompt
from app.services.invoke_client import InvokeClient
from app.widgets.image_panel import ImagePanel
from app.widgets.mask_editor import MaskEditorDialog
from app.widgets.theme_card import ThemeCard
from app.workers.generation_worker import GenerationWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{CONFIG.app_name} v{CONFIG.version}")
        self.resize(1580, 940)

        self.invoke = InvokeClient()
        self.source_path: str | None = None
        self.result_path: str | None = None
        self.mask_path: str | None = None
        self.worker: GenerationWorker | None = None
        self.active_mode = modes()[0]
        self.visible_presets: list[StudioPreset] = []
        self.selected_preset_id: str | None = None
        self.theme_cards: list[ThemeCard] = []
        self.prompt_history: list[str] = []
        self._setting_prompt = False
        self._prompt_user_edited = False

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.quick_page = self._build_quick_page()
        self.pages.addWidget(self.quick_page)

        root = QWidget()
        self.pages.addWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(12)

        outer.addLayout(self._build_header())
        outer.addWidget(self._build_steps())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_action_panel())
        splitter.addWidget(self._build_workspace())
        splitter.addWidget(self._build_prompt_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([260, 920, 390])
        outer.addWidget(splitter, 1)

        outer.addLayout(self._build_bottom_actions())
        self._build_menu()
        self.setStyleSheet(self._stylesheet())

        self._select_mode(self.active_mode)
        self.check_invoke()
        self.connection_timer = QTimer(self)
        self.connection_timer.setInterval(5000)
        self.connection_timer.timeout.connect(self.check_invoke)
        self.connection_timer.start()

    def _build_menu(self) -> None:
        workspace_menu = self.menuBar().addMenu("Workspace")
        quick_action = QAction("Quick Generate", self)
        quick_action.setShortcut("Ctrl+1")
        quick_action.triggered.connect(lambda: self._show_workspace(0))
        studio_action = QAction("Portrait Studio", self)
        studio_action.setShortcut("Ctrl+2")
        studio_action.triggered.connect(lambda: self._show_workspace(1))
        workspace_menu.addAction(quick_action)
        workspace_menu.addAction(studio_action)
        workspace_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        workspace_menu.addAction(exit_action)

    def _show_workspace(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        self.statusBar().showMessage(
            "Quick Generate" if index == 0 else "Portrait Studio · themes, masks and advanced controls",
            3000,
        )

    def _build_quick_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(28, 22, 28, 24)
        outer.setSpacing(16)

        header = QHBoxLayout()
        brand_stack = QVBoxLayout()
        brand = QLabel("CineStills AI Studio")
        brand.setObjectName("brand")
        tagline = QLabel("Upload. Describe. Generate.")
        tagline.setObjectName("tagline")
        brand_stack.addWidget(brand)
        brand_stack.addWidget(tagline)
        header.addLayout(brand_stack)
        header.addStretch(1)
        studio_button = QPushButton("Open Portrait Studio")
        studio_button.clicked.connect(lambda: self._show_workspace(1))
        header.addWidget(studio_button)
        outer.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(18)
        self.quick_original = ImagePanel("SOURCE PHOTO", "Upload a photo to begin")
        self.quick_preview = ImagePanel("GENERATED RESULT", "Your result will appear here")
        content.addWidget(self.quick_original, 1)
        content.addWidget(self.quick_preview, 1)
        outer.addLayout(content, 1)

        prompt_card = QFrame()
        prompt_card.setObjectName("quickPromptCard")
        prompt_layout = QVBoxLayout(prompt_card)
        prompt_layout.setContentsMargins(18, 16, 18, 16)
        prompt_layout.setSpacing(10)
        prompt_title = QLabel("WHAT DO YOU WANT TO CREATE?")
        prompt_title.setObjectName("sectionTitle")
        prompt_layout.addWidget(prompt_title)
        self.quick_prompt = QPlainTextEdit()
        self.quick_prompt.setPlaceholderText(
            "Example: Change the background to a premium office with warm window light, "
            "keep the person and face exactly the same."
        )
        self.quick_prompt.setMinimumHeight(105)
        prompt_layout.addWidget(self.quick_prompt)

        controls = QHBoxLayout()
        self.quick_upload = QPushButton("＋  Upload Photo")
        self.quick_upload.setObjectName("uploadButton")
        self.quick_upload.clicked.connect(self.choose_photo)
        controls.addWidget(self.quick_upload)
        self.quick_identity = QLabel("PROMPT SENT AS WRITTEN")
        self.quick_identity.setObjectName("hint")
        controls.addWidget(self.quick_identity)
        controls.addStretch(1)
        self.quick_generate = QPushButton("Generate")
        self.quick_generate.setObjectName("generateButton")
        self.quick_generate.clicked.connect(self.generate_quick)
        controls.addWidget(self.quick_generate)
        self.quick_save = QPushButton("Save Result")
        self.quick_save.setEnabled(False)
        self.quick_save.clicked.connect(self.save_result)
        controls.addWidget(self.quick_save)
        prompt_layout.addLayout(controls)

        self.quick_status = QLabel("Upload a photo, enter a prompt, then select Generate.")
        self.quick_status.setObjectName("status")
        prompt_layout.addWidget(self.quick_status)
        outer.addWidget(prompt_card)
        return page

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        brand_stack = QVBoxLayout()
        brand = QLabel("CineStills AI Studio")
        brand.setObjectName("brand")
        tagline = QLabel("Upload a portrait. Choose a look. Keep the person.")
        tagline.setObjectName("tagline")
        brand_stack.addWidget(brand)
        brand_stack.addWidget(tagline)
        header.addLayout(brand_stack)
        header.addStretch(1)
        self.connection = QLabel("InvokeAI: checking…")
        self.connection.setObjectName("connection")
        header.addWidget(self.connection)
        return header

    def _build_steps(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("steps")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 8, 14, 8)
        for index, text in enumerate(("Upload", "Choose transformation", "Pick a look", "Edit prompt", "Generate"), 1):
            label = QLabel(f"{index}  {text}")
            label.setObjectName("step")
            layout.addWidget(label)
            if index < 5:
                divider = QLabel("›")
                divider.setObjectName("stepDivider")
                layout.addWidget(divider)
        layout.addStretch(1)
        return frame

    def _build_action_panel(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("sidePanel")
        frame.setMinimumWidth(240)
        frame.setMaximumWidth(290)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(9)

        self.choose_button = QPushButton("＋  Upload Portrait")
        self.choose_button.setObjectName("uploadButton")
        self.choose_button.clicked.connect(self.choose_photo)
        layout.addWidget(self.choose_button)
        self.photo_status = QLabel("No photo selected")
        self.photo_status.setObjectName("hint")
        self.photo_status.setWordWrap(True)
        layout.addWidget(self.photo_status)

        title = QLabel("WHAT DO YOU WANT TO CHANGE?")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        mode_icons = {
            "Change Background": "▣",
            "Complete Redesign": "✦",
            "Change Outfit": "♢",
            "Lighting & Mood": "◐",
            "Professional Portrait": "◉",
            "Professional Skin Retouching": "✧",
            "Enhance & Restore": "↟",
        }
        for mode in modes():
            button = QPushButton(f"{mode_icons.get(mode, '•')}   {mode}")
            button.setCheckable(True)
            button.setObjectName("modeButton")
            button.clicked.connect(lambda checked=False, value=mode: self._select_mode(value))
            self.mode_group.addButton(button)
            layout.addWidget(button)
            if mode == self.active_mode:
                button.setChecked(True)

        layout.addStretch(1)

        brush_title = QLabel("LOCAL EDIT CONTROL")
        brush_title.setObjectName("sectionTitle")
        layout.addWidget(brush_title)
        paint = QPushButton("Paint exact edit area")
        paint.clicked.connect(self.edit_mask)
        clear = QPushButton("Clear painted area")
        clear.clicked.connect(self.clear_edit_mask)
        layout.addWidget(paint)
        layout.addWidget(clear)
        self.mask_badge = QLabel("No painted area · full image may be processed")
        self.mask_badge.setWordWrap(True)
        self.mask_badge.setObjectName("maskInactive")
        layout.addWidget(self.mask_badge)
        return frame

    def _build_workspace(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(10)

        images = QHBoxLayout()
        self.original = ImagePanel("ORIGINAL", "Upload a portrait to begin")
        self.preview = ImagePanel("RESULT", "Your transformed portrait will appear here")
        images.addWidget(self.original, 1)
        images.addWidget(self.preview, 1)
        layout.addLayout(images, 3)

        gallery_header = QHBoxLayout()
        self.gallery_title = QLabel("Choose a look")
        self.gallery_title.setObjectName("galleryTitle")
        gallery_header.addWidget(self.gallery_title)
        gallery_header.addStretch(1)
        self.category = QComboBox()
        self.category.currentTextChanged.connect(self._refresh_gallery)
        gallery_header.addWidget(self.category)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search themes")
        self.search.setMaximumWidth(220)
        self.search.textChanged.connect(self._refresh_gallery)
        gallery_header.addWidget(self.search)
        layout.addLayout(gallery_header)

        self.theme_scroll = QScrollArea()
        self.theme_scroll.setWidgetResizable(True)
        self.theme_scroll.setMinimumHeight(230)
        self.theme_host = QWidget()
        self.theme_grid = QGridLayout(self.theme_host)
        self.theme_grid.setContentsMargins(0, 0, 0, 0)
        self.theme_grid.setSpacing(10)
        self.theme_scroll.setWidget(self.theme_host)
        layout.addWidget(self.theme_scroll, 2)
        return container

    def _build_prompt_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(350)
        scroll.setMaximumWidth(450)
        frame = QFrame()
        frame.setObjectName("sidePanel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("CUSTOMISE THE LOOK")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.keyword = QLineEdit()
        self.keyword.setPlaceholderText("One idea is enough — e.g. Kashmir, Diwali, Paris café")
        self.keyword.textChanged.connect(self._settings_changed)
        layout.addWidget(QLabel("Your idea or location (optional)"))
        layout.addWidget(self.keyword)

        form = QFormLayout()
        self.intensity = QComboBox()
        self.intensity.addItems(["Natural", "Creative", "Dramatic"])
        self.intensity.currentTextChanged.connect(self._settings_changed)
        self.lighting = QComboBox()
        self.lighting.addItems(["Match Source", "Golden Hour", "Soft Diffused Light", "Backlit", "Low Key"])
        self.lighting.currentTextChanged.connect(self._settings_changed)
        self.color_grade = QComboBox()
        self.color_grade.addItems(["Natural", "Warm Film", "Muted Editorial", "Teal-Orange", "Cool Cinematic"])
        self.color_grade.currentTextChanged.connect(self._settings_changed)
        form.addRow("Strength", self.intensity)
        form.addRow("Light", self.lighting)
        form.addRow("Colour", self.color_grade)
        layout.addLayout(form)

        self.custom_instruction = QPlainTextEdit()
        self.custom_instruction.setPlaceholderText("Optional extra direction")
        self.custom_instruction.setMaximumHeight(72)
        self.custom_instruction.textChanged.connect(self._settings_changed)
        layout.addWidget(self.custom_instruction)

        prompt_header = QHBoxLayout()
        prompt_label = QLabel("GENERATED PROMPT · EDITABLE")
        prompt_label.setObjectName("sectionTitle")
        prompt_header.addWidget(prompt_label)
        prompt_header.addStretch(1)
        regenerate = QPushButton("Regenerate")
        regenerate.clicked.connect(lambda: self._regenerate_prompt(force=True))
        prompt_header.addWidget(regenerate)
        layout.addLayout(prompt_header)

        self.prompt_editor = QPlainTextEdit()
        self.prompt_editor.setPlaceholderText("Choose a theme to generate an editable prompt")
        self.prompt_editor.setMinimumHeight(230)
        self.prompt_editor.textChanged.connect(self._prompt_edited)
        layout.addWidget(self.prompt_editor)
        protected_note = QLabel("The prompt shown above is sent exactly as written. CineStills adds no hidden instructions.")
        protected_note.setObjectName("hint")
        protected_note.setWordWrap(True)
        layout.addWidget(protected_note)

        prompt_actions = QHBoxLayout()
        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self.copy_prompt)
        undo_button = QPushButton("Previous")
        undo_button.clicked.connect(self.previous_prompt)
        save_preset = QPushButton("Save My Preset")
        save_preset.clicked.connect(self.save_personal_preset)
        prompt_actions.addWidget(copy_button)
        prompt_actions.addWidget(undo_button)
        prompt_actions.addWidget(save_preset)
        layout.addLayout(prompt_actions)
        layout.addStretch(1)
        scroll.setWidget(frame)
        return scroll

    def _build_bottom_actions(self) -> QHBoxLayout:
        actions = QHBoxLayout()
        self.status = QLabel("Upload a portrait to begin")
        self.status.setObjectName("status")
        self.generate = QPushButton("Generate")
        self.generate.setObjectName("generateButton")
        self.generate.clicked.connect(self.generate_local)
        self.save = QPushButton("Save Result")
        self.save.setEnabled(False)
        self.save.clicked.connect(self.save_result)
        actions.addWidget(self.status, 1)
        actions.addWidget(self.generate)
        actions.addWidget(self.save)
        return actions

    def _select_mode(self, mode: str) -> None:
        self.active_mode = mode
        self.gallery_title.setText(mode)
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItem("All themes")
        self.category.addItems(categories_for_mode(mode))
        self.category.blockSignals(False)
        self.search.clear()
        self.selected_preset_id = None
        self._refresh_gallery()

    def _clear_grid(self) -> None:
        while self.theme_grid.count():
            item = self.theme_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.theme_cards.clear()

    def _refresh_gallery(self, _value: str = "") -> None:
        if not hasattr(self, "theme_grid"):
            return
        self._clear_grid()
        category = self.category.currentText()
        self.visible_presets = presets_for(
            self.active_mode,
            None if category == "All themes" else category,
        )
        search = self.search.text().strip().lower()
        if search:
            self.visible_presets = [
                p for p in self.visible_presets
                if search in " ".join((p.name, p.category, p.summary, *p.tags)).lower()
            ]
        for index, preset in enumerate(self.visible_presets):
            card = ThemeCard(preset)
            card.selected.connect(self._select_preset)
            card.set_selected(preset.id == self.selected_preset_id)
            self.theme_cards.append(card)
            self.theme_grid.addWidget(card, index // 3, index % 3)
        self.theme_grid.setRowStretch((len(self.visible_presets) + 2) // 3, 1)
        visible_ids = {preset.id for preset in self.visible_presets}
        if self.selected_preset_id not in visible_ids and self.visible_presets:
            self._select_preset(self.visible_presets[0].id)

    def _select_preset(self, preset_id: str) -> None:
        self.selected_preset_id = preset_id
        for card in self.theme_cards:
            card.set_selected(card.preset.id == preset_id)
        preset = self.current_preset()
        if not preset:
            return

        self.status.setText(f"Selected: {preset.name}")
        self._regenerate_prompt(force=True)

    def current_preset(self) -> StudioPreset | None:
        if not self.selected_preset_id:
            return None
        for preset in presets_for(self.active_mode):
            if preset.id == self.selected_preset_id:
                return preset
        return None

    def _locks(self) -> SubjectLocks:
        return SubjectLocks(
            face=False,
            hair=False,
            body=False,
            pose=False,
            clothing=False,
            skin_tone=False,
        )

    def _look(self) -> LookSettings:
        return LookSettings(
            lighting=self.lighting.currentText(),
            color_grade=self.color_grade.currentText(),
            intensity=self.intensity.currentText(),
        )

    def _settings_changed(self, _value=None) -> None:
        if not hasattr(self, "prompt_editor"):
            return
        if self._prompt_user_edited:
            self.status.setText("Settings changed · select Regenerate to rebuild the prompt, or keep editing manually.")
        else:
            self._regenerate_prompt(force=False)

    def _prompt_edited(self) -> None:
        if not self._setting_prompt:
            self._prompt_user_edited = True

    def _regenerate_prompt(self, force: bool = False) -> None:
        preset = self.current_preset()
        if not preset or (self._prompt_user_edited and not force):
            return
        old = self.prompt_editor.toPlainText().strip()
        if old and (not self.prompt_history or self.prompt_history[-1] != old):
            self.prompt_history.append(old)
        prompt = build_prompt(
            preset=preset,
            custom_instruction=self.custom_instruction.toPlainText(),
            locks=self._locks(),
            look=self._look(),
            keyword=self.keyword.text(),
        )
        self._setting_prompt = True
        self.prompt_editor.setPlainText(prompt)
        self._setting_prompt = False
        self._prompt_user_edited = False

    def build_current_prompt(self) -> str:
        preset = self.current_preset()
        if not preset:
            return ""
        return finalize_prompt(self.prompt_editor.toPlainText(), preset, self._locks())

    def copy_prompt(self) -> None:
        QApplication.clipboard().setText(self.build_current_prompt())
        self.status.setText("Prompt copied exactly as shown.")

    def previous_prompt(self) -> None:
        if not self.prompt_history:
            self.status.setText("No earlier prompt in this session.")
            return
        previous = self.prompt_history.pop()
        self._setting_prompt = True
        self.prompt_editor.setPlainText(previous)
        self._setting_prompt = False
        self._prompt_user_edited = True
        self.status.setText("Previous prompt restored.")

    def save_personal_preset(self) -> None:
        preset = self.current_preset()
        if not preset:
            return
        storage = Path.home() / ".cinestills" / "personal-presets.json"
        storage.parent.mkdir(parents=True, exist_ok=True)
        try:
            existing = json.loads(storage.read_text("utf-8")) if storage.exists() else []
            existing.append({
                "name": f"My {preset.name}",
                "source_preset": preset.id,
                "prompt": self.build_current_prompt(),
                "saved_at": int(time.time()),
            })
            storage.write_text(json.dumps(existing, indent=2, ensure_ascii=False), "utf-8")
            self.status.setText("Personal prompt preset saved on this computer.")
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Could not save preset", str(exc))

    def _apply_connection_status(self, ok: bool, detail: str) -> None:
        if ok:
            self.connection.setText("● InvokeAI Connected")
            self.connection.setStyleSheet("color: #80F0B2;")
        else:
            self.connection.setText("● InvokeAI Offline")
            self.connection.setStyleSheet("color: #FF9A9A;")
        self.connection.setToolTip(detail)

    def check_invoke(self) -> None:
        health = self.invoke.health_quick()
        self._apply_connection_status(health.ok, health.detail)

    def choose_photo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose Portrait", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if not path:
            return
        self._remove_mask_file()
        self.source_path = path
        self.result_path = None
        self._update_mask_badge()
        self.original.set_image(path)
        self.preview.clear_image("Choose a look and generate")
        self.quick_original.set_image(path)
        self.quick_preview.clear_image("Enter a prompt and generate")
        self.photo_status.setText(Path(path).name)
        self.save.setEnabled(False)
        self.quick_save.setEnabled(False)
        self.status.setText("Portrait ready · choose a transformation and look.")
        self.quick_status.setText(f"Ready: {Path(path).name}")

    def edit_mask(self) -> None:
        if not self.source_path:
            QMessageBox.information(self, "Upload a portrait", "Select a source portrait first.")
            return
        dialog = MaskEditorDialog(self.source_path, self)
        if not dialog.exec():
            return
        if not dialog.has_selection():
            QMessageBox.information(self, "No area selected", "Paint at least one area before saving.")
            return
        mask_dir = Path.cwd() / "temp" / "masks"
        mask_dir.mkdir(parents=True, exist_ok=True)
        mask_path = mask_dir / f"cinestills-mask-{int(time.time() * 1000)}.png"
        if not dialog.save_mask(mask_path):
            QMessageBox.warning(self, "Mask not saved", "CineStills could not save the painted area.")
            return
        self._remove_mask_file()
        self.mask_path = str(mask_path)
        self._update_mask_badge()
        self.status.setText("Painted edit area active.")

    def clear_edit_mask(self) -> None:
        self._remove_mask_file()
        self._update_mask_badge()
        self.status.setText("Painted edit area cleared.")

    def _update_mask_badge(self) -> None:
        if self.mask_path:
            self.mask_badge.setText("EDIT AREA ACTIVE\nOnly the painted region may change")
            self.mask_badge.setObjectName("maskActive")
        else:
            self.mask_badge.setText("No painted area · full image may be processed")
            self.mask_badge.setObjectName("maskInactive")
        self.mask_badge.style().unpolish(self.mask_badge)
        self.mask_badge.style().polish(self.mask_badge)

    def _uses_exact_face_lock(self, preset: StudioPreset) -> bool:
        return preset.mode in {"Complete Redesign", "Change Outfit", "Professional Portrait"}

    def _set_generation_busy(self, busy: bool) -> None:
        self.generate.setEnabled(not busy)
        self.quick_generate.setEnabled(not busy)
        if busy:
            self.save.setEnabled(False)
            self.quick_save.setEnabled(False)

    def _remove_mask_file(self) -> None:
        if not self.mask_path:
            return
        try:
            mask = Path(self.mask_path)
            temp_masks = (Path.cwd() / "temp" / "masks").resolve()
            resolved = mask.resolve()
            if temp_masks in resolved.parents:
                resolved.unlink(missing_ok=True)
        except OSError:
            pass
        self.mask_path = None

    def generate_local(self) -> None:
        if not self.source_path:
            QMessageBox.information(self, "Upload a portrait", "Select a source portrait first.")
            return
        preset = self.current_preset()
        if not preset:
            QMessageBox.information(self, "Choose a look", "Select a visual theme first.")
            return
        if preset.requires_mask and not self.mask_path:
            choice = QMessageBox.question(
                self,
                "Paint the edit area?",
                "This look is safest when you paint the clothing or skin area to change. Generate without a painted area?",
            )
            if choice != QMessageBox.StandardButton.Yes:
                return
        health = self.invoke.health_quick(timeout=1.5)
        self._apply_connection_status(health.ok, health.detail)
        if not health.ok:
            QMessageBox.warning(self, "InvokeAI is offline", "Start InvokeAI locally, then try again.\n\n" + health.detail)
            return

        self._set_generation_busy(True)
        self.preview.clear_image("Creating your portrait…")
        self.status.setText(f"Applying {preset.name} with Identity Lock…")
        self.worker = GenerationWorker(
            source_path=self.source_path,
            prompt=self.build_current_prompt(),
            base_url=self.invoke.base_url,
            strict_composite=preset.strict_composite,
            exact_face_lock=self._uses_exact_face_lock(preset),
            edit_mask_path=self.mask_path,
        )
        self.worker.status.connect(self.status.setText)
        self.worker.succeeded.connect(self.generation_succeeded)
        self.worker.failed.connect(self.generation_failed)
        self.worker.finished.connect(lambda: self._set_generation_busy(False))
        self.worker.start()

    def generate_quick(self) -> None:
        if not self.source_path:
            QMessageBox.information(self, "Upload a photo", "Select a source photo first.")
            return
        creative_prompt = self.quick_prompt.toPlainText().strip()
        if not creative_prompt:
            QMessageBox.information(self, "Enter a prompt", "Describe what you want to create first.")
            self.quick_prompt.setFocus()
            return
        health = self.invoke.health_quick(timeout=1.5)
        self._apply_connection_status(health.ok, health.detail)
        if not health.ok:
            QMessageBox.warning(self, "InvokeAI is offline", "Start InvokeAI locally, then try again.\n\n" + health.detail)
            return

        self._set_generation_busy(True)
        self.quick_preview.clear_image("Creating your image…")
        self.quick_status.setText("Generating locally from your prompt…")
        self.worker = GenerationWorker(
            source_path=self.source_path,
            prompt=creative_prompt,
            base_url=self.invoke.base_url,
            strict_composite=False,
            exact_face_lock=False,
        )
        self.worker.status.connect(self.quick_status.setText)
        self.worker.succeeded.connect(self.generation_succeeded)
        self.worker.failed.connect(self.generation_failed)
        self.worker.finished.connect(lambda: self._set_generation_busy(False))
        self.worker.start()

    def generation_succeeded(self, path: str) -> None:
        self.result_path = path
        self.preview.set_image(path)
        self.quick_preview.set_image(path)
        self.save.setEnabled(True)
        self.quick_save.setEnabled(True)
        self.check_invoke()
        self.status.setText("Done · compare the result, refine the prompt or save.")
        self.quick_status.setText("Done · refine the prompt and generate again, or save the result.")

    def generation_failed(self, message: str) -> None:
        self.result_path = None
        self.preview.clear_image("Generation failed")
        self.quick_preview.clear_image("Generation failed")
        self.status.setText("Generation failed")
        self.quick_status.setText("Generation failed")
        self.check_invoke()
        lower_message = message.lower()
        if "out of memory" in lower_message or ("cuda" in lower_message and "memory" in lower_message):
            guidance = (
                "Qwen Image Edit Q8_0 is memory-heavy. If InvokeAI cannot offload it successfully, "
                "install Qwen Image Edit 2511 (Q4_K_M) and remove Q8_0, then try again."
            )
        elif "disk space" in lower_message or "no space left" in lower_message:
            guidance = "Free additional disk space on the drive used by InvokeAI, then retry."
        elif "qwen" in lower_message and ("not found" in lower_message or "no source" in lower_message):
            guidance = (
                "Check InvokeAI Model Manager for Qwen Image Edit 2511, Qwen2.5-VL Encoder and Qwen Image VAE."
            )
        else:
            guidance = (
                "No reinstall is needed for an InvokeAI generation error. "
                "Check that InvokeAI is running and the required Qwen models are installed."
            )
        QMessageBox.critical(
            self,
            "Local generation failed",
            message + "\n\n" + guidance,
        )

    def save_result(self) -> None:
        if not self.result_path:
            return
        destination, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Edited Portrait", str(Path.home() / "cinestills-result.png"),
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

    @staticmethod
    def _stylesheet() -> str:
        return """
        QMainWindow, QWidget { background: #0D0F14; color: #F4F5F7; font-size: 13px; }
        #brand { font-size: 25px; font-weight: 850; }
        #tagline, #hint, #status { color: #9097A5; }
        #connection { color: #9097A5; }
        #steps { background: #131720; border: 1px solid #242B37; border-radius: 10px; }
        #step { color: #C5CBD5; font-weight: 700; }
        #stepDivider { color: #586174; font-size: 18px; }
        #sidePanel { background: #12151B; border: 1px solid #242A34; border-radius: 14px; }
        #quickPromptCard { background: #12151B; border: 1px solid #2B313D; border-radius: 14px; }
        #sectionTitle { color: #D7FF00; font-size: 11px; font-weight: 850; letter-spacing: 1px; }
        #galleryTitle { font-size: 19px; font-weight: 850; }
        #panelTitle { color: #DCE1E8; font-weight: 800; }
        #imageWell { background: #171A21; border: 1px solid #2B313D; border-radius: 14px; color: #717A89; }
        QPushButton { background: #1A1E27; border: 1px solid #343B49; border-radius: 8px; padding: 9px 11px; font-weight: 650; text-align: left; }
        QPushButton:hover { border-color: #758096; background: #202631; }
        QPushButton:checked { background: #252D1A; border-color: #D7FF00; color: #F3FFD0; }
        QPushButton:disabled { color: #666D79; background: #171A21; }
        #uploadButton { background: #D7FF00; color: #101217; font-weight: 900; padding: 12px; text-align: center; }
        #modeButton { padding: 11px 10px; }
        #generateButton { background: #D7FF00; color: #101217; font-weight: 900; padding: 13px 24px; text-align: center; }
        QComboBox, QLineEdit, QPlainTextEdit { background: #191D25; border: 1px solid #343B49; border-radius: 8px; padding: 8px 10px; selection-background-color: #586B00; }
        QComboBox:focus, QLineEdit:focus, QPlainTextEdit:focus { border-color: #788D16; }
        QGroupBox { border: 1px solid #2B313D; border-radius: 10px; margin-top: 8px; padding: 9px; color: #DCE1E8; font-weight: 750; }
        QGroupBox::title { subcontrol-origin: margin; left: 9px; padding: 0 5px; }
        QCheckBox { spacing: 7px; }
        QScrollArea { border: none; background: transparent; }
        QFrame#themeCard { background: #151922; border: 1px solid #2A313E; border-radius: 12px; }
        QFrame#themeCard:hover { border-color: #657083; background: #191E28; }
        QFrame#themeCard[selected="true"] { border: 2px solid #D7FF00; background: #1C211A; }
        #themeName { font-size: 15px; font-weight: 850; }
        #themeSummary { color: #A0A7B4; font-size: 11px; }
        #themeChanges { color: #7F8998; font-size: 9px; font-weight: 800; }
        #applyTheme { text-align: center; padding: 5px 9px; }
        #identityStrict { background: #14251E; color: #80F0B2; border: 1px solid #24573E; border-radius: 8px; padding: 8px 10px; font-weight: 800; }
        #identityGenerative { background: #2A2415; color: #FFD56A; border: 1px solid #5D4A1C; border-radius: 8px; padding: 8px 10px; font-weight: 800; }
        #maskActive { background: #24172B; color: #F2A7FF; border: 1px solid #623A70; border-radius: 8px; padding: 8px 10px; font-weight: 800; }
        #maskInactive { background: #171A21; color: #8D96A5; border: 1px solid #343B49; border-radius: 8px; padding: 8px 10px; }
        """


def run_app() -> None:
    app = QApplication([])
    app.setApplicationName(CONFIG.app_name)
    window = MainWindow()
    window.show()
    app.exec()
