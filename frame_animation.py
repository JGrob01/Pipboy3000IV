import os
import glob

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap


class FrameAnimation(QObject):
    finished = pyqtSignal()

    def __init__(self, label, frames_dir, fps=15, loop=False, parent=None):
        super().__init__(parent)
        self.label = label
        self.interval_ms = int(1000 / fps)
        self.loop = loop

        pattern = os.path.join(frames_dir, "*.png")
        self.frame_paths = sorted(glob.glob(pattern))
        if not self.frame_paths:
            raise FileNotFoundError(f"No PNG frames found in {frames_dir}")

        self.index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)

    def play(self):
        self.index = 0
        self.label.setPixmap(QPixmap(self.frame_paths[0]))
        self.timer.start(self.interval_ms)

    def stop(self):
        self.timer.stop()

    def _next_frame(self):
        self.index += 1
        if self.index >= len(self.frame_paths):
            if self.loop:
                self.index = 0
            else:
                self.timer.stop()
                self.finished.emit()
                return
        self.label.setPixmap(QPixmap(self.frame_paths[self.index]))