import os

from PyQt5.QtWidgets import QMainWindow, QShortcut
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QCursor, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from boot import Ui_MainWindow
from frame_animation import FrameAnimation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- UI from Designer ---
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.widget.setScaledContents(True)

        # --- Styling ---
        self.setStyleSheet("background-color: black;")

        # --- Paths ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        # --- Window mode: dev vs production ---
        if os.environ.get("PIPBOY_DEV"):
            self.resize(720, 720)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setCursor(QCursor(Qt.BlankCursor))
            self.showFullScreen()

        # --- Exit shortcut (always wire up before fullscreen) ---
        QShortcut(QKeySequence("Esc"), self, self.close)

        # --- Boot sound ---
        self.boot_sound = QMediaPlayer()
        self.boot_sound.setMedia(QMediaContent(
            QUrl.fromLocalFile(os.path.join(self.assets_dir, "sounds", "boot.wav"))
        ))
        self.boot_sound.setVolume(70)  # 0-100 scale

        self.boot_animation = FrameAnimation(
            self.ui.widget,
            os.path.join(self.assets_dir, "boot"),
            fps=16,
            loop=False,
            parent=self,
        )
        self.boot_animation.finished.connect(self.on_boot_done)

        # --- Kick off ---
        self.start_boot()

    def start_boot(self):        
        self.boot_sound.play()
        self.boot_animation.play()

    def on_boot_done(self):
        # TODO: hide self.ui.widget, swap in the main Pip-Boy UI (tabs etc.)
        print("Boot complete.")