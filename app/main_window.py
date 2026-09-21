from __future__ import annotations

from pathlib import Path
import shutil

from PIL import Image
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QComboBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import CONFIG
from app.recipes import RECIPES
from app.services.invoke_client import InvokeClient
from app.widgets.image_panel import ImagePanel
from app.workers.generation_worker import GenerationWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{CONFIG.app_name} v{CONFIG.version}")
        self.resize(1280, 820)

        self.invoke = InvokeClient()
        self.source_path: str | None = None
        self.result_path: str | None = None
        self.worker: GenerationWorker | None = None

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(14)

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

        images = QHBoxLayout()
        self.original = ImagePanel("ORIGINAL", "Choose a photo to begin.")
        self.preview = ImagePanel("PREVIEW", "Your edited result will appear here.")
        images.addWidget(self.original, 1)
        images.addWidget(self.preview, 1)
        outer.addLayout(images, 1)

        controls = QHBoxLayout()
        choose = QPushButton("Choose Photo")
        choose.clicked.connect(self.choose_photo)

        self.recipe = QComboBox()
        for item in RECIPES:
            self.recipe.addItem(item.name)

        self.identity = QLabel("Identity Protection: STRICT")
        self.identity.setObjectName("identity")

        controls.addWidget(choose)
        controls.addWidget(QLabel("Preset"))
        controls.addWidget(self.recipe)
        controls.addWidget(self.identity)
        controls.addStretch(1)
        outer.addLayout(controls)

        self.custom_prompt = QPlainTextEdit()
        self.custom_prompt.setPlaceholderText(
            "Optional instruction, e.g. make the office warmer and more cinematic"
        )
        self.custom_prompt.setMaximumHeight(90)
        outer.addWidget(self.custom_prompt)

        actions = QHBoxLayout()
        self.status = QLabel("Ready")
        self.status.setObjectName("status")

        self.generate = QPushButton("Generate Locally")
        self.generate.setObjectName("generateButton")
        self.generate.clicked.connect(self.generate_local)

        self.save = QPushButton("Save As")
        self.save.setEnabled(False)
        self.save.clicked.connect(self.save_result)

        actions.addWidget(self.status)
        actions.addStretch(1)
        actions.addWidget(self.generate)
        actions.addWidget(self.save)
        outer.addLayout(actions)

        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #101217; color: #F4F5F7; font-size: 14px; }
            #brand { font-size: 24px; font-weight: 700; }
            #tagline, #status { color: #AAB0BC; margin-left: 14px; }
            #connection { color: #AAB0BC; }
            #panelTitle { font-weight: 700; color: #DCE1E8; }
            #imageWell {
                background: #171A21;
                border: 1px solid #2D3340;
                border-radius: 14px;
                color: #7F8795;
            }
            QPushButton, QComboBox, QPlainTextEdit {
                background: #191D25;
                border: 1px solid #343B49;
                border-radius: 8px;
                padding: 9px 12px;
            }
            QPushButton:hover { border-color: #737D91; }
            QPushButton:disabled { color: #6E7480; background: #171A21; }
            #generateButton {
                background: #D7FF00;
                color: #101217;
                font-weight: 800;
                padding: 12px 22px;
            }
            #generateButton:disabled { background: #687500; color: #B7BF8A; }
            #identity {
                background: #14251E;
                color: #80F0B2;
                border: 1px solid #24573E;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 700;
            }
            """
        )

        self.check_invoke()

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
        self.original.set_image(path)
        self.preview.clear_image("Ready for local edit.")
        self.save.setEnabled(False)
        self.status.setText("Ready")

    def build_prompt(self) -> str:
        recipe = RECIPES[self.recipe.currentIndex()]
        custom = self.custom_prompt.toPlainText().strip()
        identity_guard = (
            "Use the supplied photograph as the composition reference. Keep one person only. "
            "Preserve the subject's pose, silhouette, camera angle and position. "
            "Concentrate the visual change on the background and surrounding environment. "
            "Do not add people behind or beside the subject."
        )
        parts = [identity_guard, recipe.prompt]
        if custom:
            parts.append(custom)
        return "\n\n".join(parts)

    def generate_local(self) -> None:
        if not self.source_path:
            QMessageBox.information(self, "Choose a photo", "Select a source photo first.")
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
        self.status.setText("Starting local generation...")

        self.worker = GenerationWorker(
            source_path=self.source_path,
            prompt=self.build_prompt(),
            base_url=self.invoke.base_url,
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
        self.status.setText("Done. Subject pixels preserved from the original photo.")

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
