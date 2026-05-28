import os

from PyQt5.QtWidgets import QMainWindow, QShortcut
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QCursor, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from boot import Ui_MainWindow
from frame_animation import FrameAnimation
from text_scroll import TextScroll


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Paths ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        # --- UI from Designer ---
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Styling ---
        self.setStyleSheet("background-color: rgb(51, 51, 51);")

        # --- Window mode ---
        if os.environ.get("PIPBOY_DEV"):
            self.resize(720, 720)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setCursor(QCursor(Qt.BlankCursor))
            self.showFullScreen()

        # --- Exit shortcut ---
        QShortcut(QKeySequence("Esc"), self, self.close)

        # --- Boot sound ---
        self.boot_sound = QMediaPlayer()
        self.boot_sound.setMedia(QMediaContent(
            QUrl.fromLocalFile(os.path.join(self.assets_dir, "sounds", "boot.wav"))
        ))
        self.boot_sound.setVolume(70)

        # --- Read scroll text ---
        with open(os.path.join(self.assets_dir, "boot", "scroll_text.txt"), "r") as f:
            boot_text = f.read()

        # --- Phase 1: scrolling text ---
        self.text_scroll = TextScroll(
            parent_widget=self.ui.viewport,
            text=boot_text,
            font_path=os.path.join(self.assets_dir, "fonts", "Share-TechMono Regular.ttf"),
            viewport_size=(720, 720),
            font_size=20,
            color="#15ff60",
            duration_ms=4133,
            parent=self,
        )

        # --- Phase 2: frame animation ---
        self.boot_animation = FrameAnimation(
            self.ui.image,
            os.path.join(self.assets_dir, "boot", ""),
            fps=34,
            loop=False,
            repeat_section=(223, 246),
            repeat_count=5,
            parent=self,
        )

        # Chain: text scroll done → frame animation plays
        self.text_scroll.finished.connect(self.boot_animation.play)
        self.boot_animation.finished.connect(self.on_boot_done)

        # --- Kick off ---
        self.start_boot()

    def start_boot(self):
        self.boot_sound.play()
        self.text_scroll.play()

    def on_boot_done(self):
        print("Boot complete.")