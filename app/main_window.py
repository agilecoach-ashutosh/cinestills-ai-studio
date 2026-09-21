from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
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


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{CONFIG.app_name} v{CONFIG.version}")
        self.resize(1280, 820)

        self.invoke = InvokeClient()
        self.source_path: str | None = None

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
        self.connection = QLabel("InvokeAI: checking…")
        self.connection.setObjectName("connection")
        header.addWidget(brand)
        header.addWidget(tagline)
        header.addStretch(1)
        header.addWidget(self.connection)
        outer.addLayout(header)

        images = QHBoxLayout()
        self.original = ImagePanel("ORIGINAL", "Drop support comes next.\nUse Choose Photo for V0.1.")
        self.preview = ImagePanel("PREVIEW", "Your generated result will appear here.")
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
        self.generate = QPushButton("Generate Locally")
        self.generate.setObjectName("generateButton")
        self.generate.clicked.connect(self.generate_local)

        save = QPushButton("Save As")
        save.clicked.connect(self.save_result)

        actions.addStretch(1)
        actions.addWidget(self.generate)
        actions.addWidget(save)
        outer.addLayout(actions)

        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #101217; color: #F4F5F7; font-size: 14px; }
            #brand { font-size: 24px; font-weight: 700; }
            #tagline { color: #AAB0BC; margin-left: 14px; }
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
            #generateButton {
                background: #D7FF00;
                color: #101217;
                font-weight: 800;
                padding: 12px 22px;
            }
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
        self.original.set_image(path)
        self.preview.clear_image("Ready for local edit.")

    def build_prompt(self) -> str:
        recipe = RECIPES[self.recipe.currentIndex()]
        custom = self.custom_prompt.toPlainText().strip()
        identity_guard = (
            "Identity preservation is strict. Do not alter facial geometry, eyes, nose, "
            "mouth, jawline, skin tone, hairstyle, body proportions, or identifying "
            "features. Modify only the requested scene elements."
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

        prompt = self.build_prompt()
        QMessageBox.information(
            self,
            "Local engine connected",
            "The CineStills UI and InvokeAI connection are working.\n\n"
            "The next implementation step is wiring the exact Invoke workflow endpoint "
            "for masked background editing.\n\nPrompt prepared:\n\n"
            + prompt[:900],
        )

    def save_result(self) -> None:
        if not self.preview._pixmap:
            QMessageBox.information(self, "Nothing to save", "Generate an edited image first.")
            return

        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Save Edited Photo",
            str(Path.home() / "cinestills-result.png"),
            "PNG Image (*.png);;JPEG Image (*.jpg)",
        )
        if destination:
            self.preview._pixmap.save(destination)


def run_app() -> None:
    app = QApplication([])
    app.setApplicationName(CONFIG.app_name)
    window = MainWindow()
    window.show()
    app.exec()
