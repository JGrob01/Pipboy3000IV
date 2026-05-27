import sys
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QSoundEffect
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QCursor, QKeySequence

from boot import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- UI setup ---
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Black background, no padding
        self.setStyleSheet("background-color: black;")

        # --- Paths ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # --- Video player ---
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.ui.widget)

        video_path = os.path.join(self.base_dir, "boot", "boot.avi")
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))

        # --- Sound effect (example: boot chime) ---
        self.boot_sound = QSoundEffect()
        sound_path = os.path.join(self.base_dir, "sounds", "BOOT1.wav")
        self.boot_sound.setSource(QUrl.fromLocalFile(sound_path))
        self.boot_sound.setVolume(0.7)

        # --- Window mode: dev vs production ---
        if os.environ.get("PIPBOY_DEV"):
            self.resize(800, 480)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setCursor(QCursor(Qt.BlankCursor))
            self.showFullScreen()

        # --- Exit shortcut (always wire this up before fullscreen) ---
        QShortcut(QKeySequence("Esc"), self, self.close)

        # --- Kick off boot sequence ---
        self.start_boot()

    def start_boot(self):
        #self.boot_sound.play()
        self.player.play()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())