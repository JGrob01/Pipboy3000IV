import os

from PyQt5.QtWidgets import QMainWindow, QShortcut
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QCursor, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve

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
        self.ui.image.setScaledContents(True)

        # Load the image
        pixmap = QPixmap(os.path.join(self.assets_dir, "boot", "scroll_text.png"))

        # Scale width to fit (720), keep aspect ratio
        scaled = pixmap.scaledToWidth(720, Qt.SmoothTransformation)

        # Set on the label
        self.ui.image.setPixmap(scaled)
        self.ui.image.setGeometry(0, 720, scaled.width(), scaled.height())
        # ^ start position: just below the viewport

        # Animate it scrolling up
        self.scroll_anim = QPropertyAnimation(self.ui.image, b"geometry")
        self.scroll_anim.setDuration(15000)  # 15 seconds, adjust to taste
        self.scroll_anim.setStartValue(QRect(0, 720, scaled.width(), scaled.height()))
        self.scroll_anim.setEndValue(QRect(0, -scaled.height(), scaled.width(), scaled.height()))
        self.scroll_anim.setEasingCurve(QEasingCurve.Linear)
        self.scroll_anim.start()

        # --- Styling ---
        self.setStyleSheet("background-color: black;")        

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

        with open(os.path.join(self.assets_dir, "boot", "scroll_text.txt"), "r") as f:
            boot_text = f.read()

        # --- Phase 1: scrolling text ---
        self.text_scroll = TextScroll(
            parent_widget=self.ui.image,
            text=boot_text,
            font_path=os.path.join(self.assets_dir, "fonts", "Share-TechMono Regular.ttf"),  # adjust filename
            viewport_size=(720, 720),
            font_size=20,
            color="#15ff60",
            duration_ms=2500,
            parent=self,
        )

        # --- Phase 2: frame animation ---
        self.boot_animation = FrameAnimation(
            self.ui.image,
            os.path.join(self.assets_dir, "boot"),
            fps=30,
            loop=False,
            parent=self,
        )

        self.text_scroll.finished.connect(self.boot_animation.play)
        self.boot_animation.finished.connect(self.on_boot_done)

        # --- Kick off ---
        self.start_boot()

    def start_boot(self):        
        #self.boot_sound.play()
        self.text_scroll.play()
        self.boot_animation.play()

    def on_boot_done(self):
        # TODO: hide self.ui.image, swap in the main Pip-Boy UI (tabs etc.)
        print("Boot complete.")