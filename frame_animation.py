import os
import glob
import time

from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap


class FrameLoader(QThread):
    """Background thread that decodes frames into QPixmaps on demand."""

    frame_loaded = pyqtSignal(int, QPixmap)   # (index, pixmap)

    def __init__(self, frame_paths, parent=None):
        super().__init__(parent)
        self.frame_paths = frame_paths
        self._queue = []
        self._running = True
        self._seen = set()

    def request(self, index):
        if 0 <= index < len(self.frame_paths) and index not in self._seen:
            self._seen.add(index)
            self._queue.append(index)

    def run(self):
        while self._running:
            if self._queue:
                index = self._queue.pop(0)
                pixmap = QPixmap(self.frame_paths[index])
                self.frame_loaded.emit(index, pixmap)
            else:
                self.msleep(2)

    def forget(self, index):
        # allow re-requesting a dropped frame later (for repeat sections)
        self._seen.discard(index)

    def stop(self):
        self._running = False
        self.wait()


class FrameAnimation(QObject):
    finished = pyqtSignal()

    def __init__(self, label, frames_dir, fps=15, loop=False,
                 repeat_section=None, repeat_count=1,
                 buffer_ahead=20, parent=None):
        super().__init__(parent)
        self.label = label
        self.interval_ms = int(1000 / fps)
        self.loop = loop
        self.buffer_ahead = buffer_ahead

        self._last_time = None

        # accept both .jpg and .png
        paths = sorted(
            glob.glob(os.path.join(frames_dir, "*.jpg")) +
            glob.glob(os.path.join(frames_dir, "*.png"))
        )
        if not paths:
            raise FileNotFoundError(f"No frames found in {frames_dir}")
        self.frame_paths = paths

        self.repeat_section = repeat_section
        self.repeat_count = repeat_count
        self._repeats_done = 0

        self.index = 0
        self.cache = {}   # index -> QPixmap

        self.loader = FrameLoader(self.frame_paths, parent=self)
        self.loader.frame_loaded.connect(self._on_frame_loaded)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)

    @pyqtSlot(int, QPixmap)
    def _on_frame_loaded(self, index, pixmap):
        self.cache[index] = pixmap

    def _prefetch(self):
        # Request the next `buffer_ahead` frames
        for i in range(self.index, min(self.index + self.buffer_ahead,
                                       len(self.frame_paths))):
            if i not in self.cache:
                self.loader.request(i)

    def _drop_old(self):
        # Drop frames we've already passed to free memory
        for i in list(self.cache.keys()):
            if i < self.index - 2:   # keep a tiny tail just in case
                del self.cache[i]
                self.loader.forget(i)

    def play(self):
        self.index = 0
        self._repeats_done = 0
        self.cache.clear()
        self.loader.start()
        self._prefetch()
        # show first frame as soon as it's ready
        QTimer.singleShot(50, self._start_timer)

    def _start_timer(self):
        self.timer.start(self.interval_ms)

    def stop(self):
        self.timer.stop()
        self.loader.stop()

    def _next_frame(self):
        # At the very top of _next_frame:
        now = time.monotonic()
        if self._last_time is not None:
            delta = (now - self._last_time) * 1000
            print(f"Frame {self.index}: {delta:.0f}ms (target {self.interval_ms}ms)")
        self._last_time = now
        
        self.index += 1

        # Handle repeat section
        if self.repeat_section is not None:
            if (self.index > self.repeat_section[1]
                    and self._repeats_done < self.repeat_count):
                self._repeats_done += 1
                self.index = self.repeat_section[0]

        # End of animation
        if self.index >= len(self.frame_paths):
            if self.loop:
                self.index = 0
            else:
                self.timer.stop()
                self.loader.stop()
                self.finished.emit()
                return

        # Display current frame if cached; otherwise hold previous
        if self.index in self.cache:
            self.label.setPixmap(self.cache[self.index])

        # Only prefetch/drop every 5 frames instead of every frame
        if self.index % 5 == 0:
            self._prefetch()
            self._drop_old()