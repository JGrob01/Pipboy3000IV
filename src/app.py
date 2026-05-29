import os
import sys

import pygame

from src.config import SCREEN_SIZE, FPS, BG
from src.boot.scroll_screen import ScrollScreen
from src.boot.frame_screen import FrameScreen
from src.menu.main_screen import MainScreen


if sys.platform.startswith("linux"):
    os.environ.setdefault("SDL_VIDEODRIVER", "kmsdrm")


class App:
    def __init__(self):
        pygame.init()
        if os.environ.get("PIPBOY_DEV"):
            self.screen_surf = pygame.display.set_mode(SCREEN_SIZE)
        else:
            self.screen_surf = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.clock = pygame.time.Clock()
        self.running = True
        
        base = os.path.dirname(os.path.abspath("main.py"))
        
        # --- Fonts ---
        font_path = os.path.join(base, "assets", "fonts", "Share-TechMono Regular.ttf")
        if not os.path.exists(font_path):
            print(f"Warning: font not found at {font_path}, using default")
            font_path = None
        self.font = pygame.font.Font(font_path if os.path.exists(font_path) else None, 18)
        self.font_small = pygame.font.Font(font_path, 14)
        self.font_body = pygame.font.Font(font_path, 17)
        self.font_large = pygame.font.Font(font_path, 28)

        # --- Boot Sound ---
        boot_sound_path = os.path.join(base, "assets", "sounds", "boot.wav")
        self.boot_sound = pygame.mixer.Sound(boot_sound_path)
        self.boot_sound.set_volume(1)

        # Read scroll text
        scroll_path = os.path.join(base, "assets", "boot", "scroll_text.txt")
        with open(scroll_path, "r") as f:
            scroll_text = f.read()

        # Create all screens
        self.main_screen = MainScreen(self, self.font)
        self.scroll_screen = ScrollScreen(self, scroll_text, self.font, duration_s=4.1333)

        self.frame_screen = FrameScreen(
            self,
            frames_dir=os.path.join(base, "assets", "boot", ""),
            fps=31,
            repeat_section=(223, 246),   # adjust to your indices
            repeat_count=4,
            next_screen=self.main_screen,
        )

        # Start with the scroll, which chains into boot, which chains into main
        #self.current = self.scroll_screen
        #self.boot_sound.play()
        self.current = self.main_screen

    def change_screen(self, screen):
        self.current = screen

    def run(self):
        while self.running:
            raw_dt = self.clock.tick(FPS) / 1000.0
            dt = min(raw_dt, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.current.handle_event(event)
            self.current.update(dt)
            self.screen_surf.fill(BG)        # <-- clear here, once per frame
            self.current.draw(self.screen_surf)
            pygame.display.flip()
        pygame.quit()