from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.services.image_io import load_oriented_image


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
        oriented = load_oriented_image(path)
        raw = oriented.tobytes("raw", "RGBA")
        qimage = QImage(
            raw,
            oriented.width,
            oriented.height,
            oriented.width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()
        pixmap = QPixmap.fromImage(qimage)
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
