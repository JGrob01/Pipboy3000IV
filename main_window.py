import os

from PyQt5.QtWidgets import QMainWindow, QShortcut
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QCursor, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

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

        # In __init__, for the video phase:
        self.video_widget = QVideoWidget(self.ui.viewport)
        self.video_widget.setGeometry(0, 0, 720, 720)

        self.boot_video = QMediaPlayer()
        self.boot_video.setVideoOutput(self.video_widget)
        video_path = os.path.join(self.assets_dir, "boot", "boot.mp4")
        # --- Window mode ---
        if os.environ.get("PIPBOY_DEV"):
            self.resize(720, 720)
            self.boot_video.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setCursor(QCursor(Qt.BlankCursor))
            self.showFullScreen()
            self.ui.image.setScaledContents(False)
            # Pi: forced hardware decode via gstreamer
            pipeline = ("gst-pipeline: filesrc location=" + video_path +
                        " ! qtdemux ! h264parse ! v4l2h264dec ! videoconvert ! "
                        "video/x-raw ! qtvideosink")
            self.boot_video.setMedia(QMediaContent(QUrl(pipeline)))

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

        # Transition to main UI when video ends:
        self.boot_video.mediaStatusChanged.connect(self._on_video_status)

        # Chain: text scroll done → frame animation plays
        self.text_scroll.finished.connect(self.boot_video.play)
        self.boot_animation.finished.connect(self.on_boot_done)

        # --- Kick off ---
        self.start_boot()

    def start_boot(self):
        self.boot_sound.play()
        self.text_scroll.play()

    def on_boot_done(self):
        print("Boot complete.")

    def _on_video_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.on_boot_done()