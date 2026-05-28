import os

from PyQt5.QtCore import QObject, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt


class TextScroll(QObject):
    """Scrolls a block of text from below the viewport to above it."""

    finished = pyqtSignal()

    def __init__(self, parent_widget, text, font_path,
                 viewport_size=(720, 720),
                 font_size=20,
                 color="#15ff60",
                 duration_ms=4133.33,
                 parent=None):
        super().__init__(parent)

        # Load the font
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Warning: failed to load font {font_path}")
            family = "Courier New"
        else:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Create the scrolling label as a child of parent_widget
        self.label = QLabel(parent_widget)
        self.label.setText(text)
        self.label.setStyleSheet(
            f"color: {color}; background-color: transparent; "
            f"font-family: '{family}'; font-size: {font_size}px;"
        )
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFixedWidth(viewport_size[0])
        self.label.adjustSize()   # height grows to fit text

        self.viewport_w, self.viewport_h = viewport_size
        self.duration_ms = duration_ms

        # Build the animation
        self.anim = QPropertyAnimation(self.label, b"geometry", self)
        self.anim.setDuration(duration_ms)
        self.anim.setEasingCurve(QEasingCurve.Linear)
        self.anim.finished.connect(self._on_done)

    def play(self):
        text_h = self.label.height()
        start = QRect(0, self.viewport_h, self.viewport_w, text_h)
        end = QRect(0, -text_h, self.viewport_w, text_h)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.label.setGeometry(start)
        self.label.show()
        self.anim.start()

    def _on_done(self):
        self.label.hide()
        self.label.deleteLater()
        self.finished.emit()