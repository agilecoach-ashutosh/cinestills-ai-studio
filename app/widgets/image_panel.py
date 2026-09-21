from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ImagePanel(QWidget):
    def __init__(self, title: str, placeholder: str) -> None:
        super().__init__()
        self._pixmap: QPixmap | None = None

        self.title = QLabel(title)
        self.title.setObjectName("panelTitle")

        self.image = QLabel(placeholder)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumSize(420, 420)
        self.image.setObjectName("imageWell")

        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.image, 1)

    def set_image(self, path: str) -> None:
        pixmap = QPixmap(str(Path(path)))
        if pixmap.isNull():
            return
        self._pixmap = pixmap
        self._refresh()

    def clear_image(self, text: str) -> None:
        self._pixmap = None
        self.image.setPixmap(QPixmap())
        self.image.setText(text)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self) -> None:
        if not self._pixmap:
            return
        scaled = self._pixmap.scaled(
            self.image.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image.setPixmap(scaled)
