from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.presets import StudioPreset


class ThemeCard(QFrame):
    selected = Signal(str)

    def __init__(self, preset: StudioPreset) -> None:
        super().__init__()
        self.preset = preset
        self.setObjectName("themeCard")
        self.setProperty("selected", False)
        self.setMinimumWidth(210)
        self.setMaximumWidth(280)
        self.setMinimumHeight(165)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        swatch = QFrame()
        swatch.setFixedHeight(54)
        swatch.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {preset.accent}, stop:1 #202631);"
            "border-radius: 9px; border: none;"
        )
        layout.addWidget(swatch)

        name = QLabel(preset.name)
        name.setObjectName("themeName")
        name.setWordWrap(True)
        layout.addWidget(name)

        summary = QLabel(preset.summary or preset.prompt)
        summary.setObjectName("themeSummary")
        summary.setWordWrap(True)
        summary.setMaximumHeight(40)
        layout.addWidget(summary)

        footer = QHBoxLayout()
        change_text = " · ".join(preset.changes[:3]) if preset.changes else preset.category
        changes = QLabel(change_text.upper())
        changes.setObjectName("themeChanges")
        changes.setWordWrap(True)
        footer.addWidget(changes, 1)
        apply_button = QPushButton("Apply")
        apply_button.setObjectName("applyTheme")
        apply_button.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_button.clicked.connect(lambda: self.selected.emit(preset.id))
        footer.addWidget(apply_button)
        layout.addLayout(footer)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self.preset.id)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
