from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class MaskCanvas(QWidget):
    """Paintable edit mask. White pixels may change; black pixels stay protected."""

    def __init__(self, image_path: str) -> None:
        super().__init__()
        self._source = QPixmap(image_path)
        if self._source.isNull():
            raise ValueError(f"Could not load image: {image_path}")

        self._mask = QImage(
            self._source.width(),
            self._source.height(),
            QImage.Format.Format_Grayscale8,
        )
        self._mask.fill(0)
        self._brush_size = 70
        self._erase = False
        self._base_erase = False
        self._right_click_override = False
        self._dragging = False
        self._last_image_point: QPointF | None = None
        self.setMinimumSize(760, 560)
        self.setMouseTracking(True)

    def set_brush_size(self, size: int) -> None:
        self._brush_size = max(5, int(size))

    def set_erase(self, erase: bool) -> None:
        self._base_erase = bool(erase)
        self._erase = self._base_erase

    def clear_mask(self) -> None:
        self._mask.fill(0)
        self.update()

    def invert_mask(self) -> None:
        self._mask.invertPixels()
        self.update()

    def has_selection(self) -> bool:
        preview = self._mask.scaled(64, 64, Qt.AspectRatioMode.IgnoreAspectRatio)
        for y in range(preview.height()):
            for x in range(preview.width()):
                if preview.pixelColor(x, y).value() > 0:
                    return True
        return False

    def save_mask(self, path: str | Path) -> bool:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return self._mask.save(str(output), "PNG")

    def _image_rect(self) -> QRectF:
        widget = QRectF(self.rect())
        source_ratio = self._source.width() / self._source.height()
        widget_ratio = widget.width() / max(1.0, widget.height())
        if widget_ratio > source_ratio:
            height = widget.height()
            width = height * source_ratio
        else:
            width = widget.width()
            height = width / source_ratio
        left = (widget.width() - width) / 2.0
        top = (widget.height() - height) / 2.0
        return QRectF(left, top, width, height)

    def _to_image_point(self, point: QPointF) -> QPointF | None:
        draw_rect = self._image_rect()
        if not draw_rect.contains(point):
            return None
        x = (point.x() - draw_rect.left()) / draw_rect.width() * self._source.width()
        y = (point.y() - draw_rect.top()) / draw_rect.height() * self._source.height()
        return QPointF(x, y)

    def _paint_at(self, point: QPointF, previous: QPointF | None = None) -> None:
        painter = QPainter(self._mask)
        value = 0 if self._erase else 255
        pen = QPen(QColor(value, value, value), self._brush_size, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        if previous is None:
            painter.drawPoint(point)
        else:
            painter.drawLine(previous, point)
        painter.end()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return
        point = self._to_image_point(event.position())
        if point is None:
            return
        self._dragging = True
        if event.button() == Qt.MouseButton.RightButton:
            self._right_click_override = True
            self._erase = True
        self._last_image_point = point
        self._paint_at(point)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._dragging:
            return
        point = self._to_image_point(event.position())
        if point is None:
            return
        self._paint_at(point, self._last_image_point)
        self._last_image_point = point

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self._dragging = False
            self._last_image_point = None
            if self._right_click_override:
                self._right_click_override = False
                self._erase = self._base_erase

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#0F1117"))
        draw_rect = self._image_rect()
        painter.drawPixmap(draw_rect, self._source, QRectF(self._source.rect()))

        overlay = QImage(self._mask.size(), QImage.Format.Format_ARGB32_Premultiplied)
        overlay.fill(Qt.GlobalColor.transparent)
        overlay_painter = QPainter(overlay)
        overlay_painter.fillRect(overlay.rect(), QColor(255, 64, 96, 112))
        overlay_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        overlay_painter.drawImage(0, 0, self._mask)
        overlay_painter.end()
        painter.drawImage(draw_rect, overlay, QRectF(overlay.rect()))

        painter.setPen(QPen(QColor("#D7FF00"), 1))
        painter.drawRect(draw_rect)
        painter.end()


class MaskEditorDialog(QDialog):
    def __init__(self, image_path: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Magic Brush - Select the area to edit")
        self.resize(980, 760)
        self.canvas = MaskCanvas(image_path)

        title = QLabel(
            "Paint the area AI is allowed to change. Everything outside the red mask stays original."
        )
        title.setWordWrap(True)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 260)
        self.size_slider.setValue(70)
        self.size_slider.valueChanged.connect(self.canvas.set_brush_size)

        self.paint_button = QPushButton("Paint")
        self.paint_button.setCheckable(True)
        self.paint_button.setChecked(True)
        self.erase_button = QPushButton("Erase")
        self.erase_button.setCheckable(True)
        self.paint_button.clicked.connect(lambda: self._set_mode(False))
        self.erase_button.clicked.connect(lambda: self._set_mode(True))

        clear_button = QPushButton("Clear Mask")
        clear_button.clicked.connect(self.canvas.clear_mask)
        invert_button = QPushButton("Invert")
        invert_button.clicked.connect(self.canvas.invert_mask)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Brush"))
        controls.addWidget(self.size_slider, 1)
        controls.addWidget(self.paint_button)
        controls.addWidget(self.erase_button)
        controls.addWidget(clear_button)
        controls.addWidget(invert_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addLayout(controls)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(QLabel("Tip: left-drag paints. Right-drag temporarily erases."))
        layout.addWidget(buttons)

        self.setStyleSheet(
            """
            QDialog, QWidget { background: #0F1117; color: #F3F5F7; font-size: 13px; }
            QPushButton { background: #191D25; border: 1px solid #343B49; border-radius: 8px; padding: 8px 12px; }
            QPushButton:checked { border-color: #D7FF00; color: #D7FF00; }
            QSlider::groove:horizontal { height: 6px; background: #343B49; border-radius: 3px; }
            QSlider::handle:horizontal { width: 16px; margin: -5px 0; background: #D7FF00; border-radius: 8px; }
            """
        )

    def _set_mode(self, erase: bool) -> None:
        self.canvas.set_erase(erase)
        self.paint_button.setChecked(not erase)
        self.erase_button.setChecked(erase)

    def save_mask(self, path: str | Path) -> bool:
        return self.canvas.save_mask(path)

    def has_selection(self) -> bool:
        return self.canvas.has_selection()
