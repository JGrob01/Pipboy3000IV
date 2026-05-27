import os
import glob

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap


class FrameAnimation(QObject):
    """Plays a sequence of PNG frames on a QLabel via QTimer.

    Emits `finished` when a non-looping animation reaches the last frame.
    """

    finished = pyqtSignal()

    def __init__(self, label, frames_dir, fps=15, loop=False, parent=None):
        super().__init__(parent)
        self.label = label
        self.interval_ms = int(1000 / fps)
        self.loop = loop

        pattern = os.path.join(frames_dir, "*.png")
        frame_paths = sorted(glob.glob(pattern))
        if not frame_paths:
            raise FileNotFoundError(f"No PNG frames found in {frames_dir}")
        self.pixmaps = [QPixmap(p) for p in frame_paths]

        self.index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)

    def play(self):
        self.index = 0
        self.label.setPixmap(self.pixmaps[0])
        self.timer.start(self.interval_ms)

    def stop(self):
        self.timer.stop()

    def _next_frame(self):
        self.index += 1
        if self.index >= len(self.pixmaps):
            if self.loop:
                self.index = 0
            else:
                self.timer.stop()
                self.finished.emit()
                return
        self.label.setPixmap(self.pixmaps[self.index])