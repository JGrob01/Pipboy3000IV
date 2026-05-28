import os
import glob

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap


class FrameAnimation(QObject):
    finished = pyqtSignal()

    def __init__(self, label, frames_dir, fps=15, loop=False, repeat_section=None, repeat_count=1, parent=None):
        super().__init__(parent)
        self.label = label
        self.interval_ms = int(1000 / fps)
        self.loop = loop

        pattern = os.path.join(frames_dir, "*.png")
        self.frame_paths = sorted(glob.glob(pattern))
        if not self.frame_paths:
            raise FileNotFoundError(f"No PNG frames found in {frames_dir}")

        self.repeat_section = repeat_section
        self.repeat_count = repeat_count
        self._repeats_done = 0

        self.index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)

    def play(self):
        self.index = 0
        self._repeats_done = 0
        self.label.setPixmap(QPixmap(self.frame_paths[0]))
        self.timer.start(self.interval_ms)

    def stop(self):
        self.timer.stop()

    def _next_frame(self):
        self.index += 1

        if self.repeat_section is not None:
            section_end = self.repeat_section[1]
            if self.index > section_end and self._repeats_done < self.repeat_count:
                self._repeats_done += 1
                self.index = self.repeat_section[0]

        if self.index >= len(self.frame_paths):
            if self.loop:
                self.index = 0
            else:
                self.timer.stop()
                self.finished.emit()
                return

        self.label.setPixmap(QPixmap(self.frame_paths[self.index]))