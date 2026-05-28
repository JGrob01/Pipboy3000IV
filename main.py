import pygame
import os
import sys
import glob

if sys.platform.startswith("linux"):
    os.environ.setdefault("SDL_VIDEODRIVER", "kmsdrm")

SCREEN_SIZE = (720, 720)
FPS = 30
GREEN = (26, 255, 9)
BG = (51, 51, 51)


class Screen:
    """Base class for each Pip-Boy screen/state."""
    def __init__(self, app):
        self.app = app
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surface): pass

class ScrollScreen(Screen):
    def __init__(self, app, text, font, duration_s=2.5):
        super().__init__(app)
        self.font = font
        self.duration = duration_s
        self.elapsed = 0.0

        # Pre-render text as a single tall surface
        lines = text.split("\n")
        line_h = self.font.get_height() + 2
        self.text_h = line_h * len(lines)
        self.text_surf = pygame.Surface((SCREEN_SIZE[0], self.text_h), pygame.SRCALPHA)
        for i, line in enumerate(lines):
            rendered = self.font.render(line, True, GREEN)
            self.text_surf.blit(rendered, (30, i * line_h))

        # Total travel: from below the screen to above it
        self.start_y = SCREEN_SIZE[1]
        self.end_y = -self.text_h

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.app.change_screen(self.app.frame_screen)

    def draw(self, surface):
        surface.fill(BG)
        t = min(self.elapsed / self.duration, 1.0)
        y = int(self.start_y + (self.end_y - self.start_y) * t)
        surface.blit(self.text_surf, (0, y))

class FrameScreen(Screen):
    def __init__(self, app, frames_dir, fps=15, repeat_section=None, repeat_count=0, next_screen=None):
        super().__init__(app)
        self.next_screen = next_screen
        self.frame_duration = 1.0 / fps
        self.elapsed = 0.0

        # Just store paths — don't load yet
        self.frame_paths = sorted(
            glob.glob(os.path.join(frames_dir, "*.png"))
        )
        if not self.frame_paths:
            raise FileNotFoundError(f"No frames found in {frames_dir}")

        self.index = 0
        self.repeat_section = repeat_section
        self.repeat_count = repeat_count
        self._repeats_done = 0
        self._current_frame = None
        self._cached_index = -1

    def update(self, dt):
        self.elapsed += dt
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.index += 1
            if self.repeat_section is not None:
                if (self.index > self.repeat_section[1]
                        and self._repeats_done < self.repeat_count):
                    self._repeats_done += 1
                    self.index = self.repeat_section[0]
            if self.index >= len(self.frame_paths):
                if self.next_screen is not None:
                    self.app.change_screen(self.next_screen)
                else:
                    self.index = len(self.frame_paths) - 1
                return

    def draw(self, surface):
        if self._cached_index != self.index:
            self._current_frame = pygame.image.load(
                self.frame_paths[self.index]
            ).convert_alpha()
            self._cached_index = self.index
        surface.blit(self._current_frame, (0, 0))

class MainScreen(Screen):
    """Placeholder for the STAT/INV/DATA/MAP/RADIO tabs."""
    def __init__(self, app, font):
        super().__init__(app)
        self.font = font
        self.tabs = ["STAT", "INV", "DATA", "MAP", "RADIO"]
        self.active = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.active = (self.active + 1) % len(self.tabs)
            elif event.key == pygame.K_LEFT:
                self.active = (self.active - 1) % len(self.tabs)

    def draw(self, surface):
        surface.fill(BG)
        x = 20
        for i, tab in enumerate(self.tabs):
            color = BG if i == self.active else GREEN
            if i == self.active:
                w = self.font.size(tab)[0] + 16
                pygame.draw.rect(surface, GREEN, (x - 8, 12, w, self.font.get_height() + 8))
            surface.blit(self.font.render(tab, True, color), (x, 16))
            x += self.font.size(tab)[0] + 40


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
        
        base = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base, "assets", "fonts", "Share-TechMono Regular.ttf")
        self.font = pygame.font.Font(font_path if os.path.exists(font_path) else None, 17)
        # In App.__init__, after mixer.init:
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
            fps=30,
            repeat_section=(223, 246),   # adjust to your indices
            repeat_count=5,
            next_screen=self.main_screen,
        )

        # Start with the scroll, which chains into boot, which chains into main
        self.current = self.scroll_screen
        self.boot_sound.play()

    def change_screen(self, screen):
        self.current = screen

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
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


if __name__ == "__main__":
    App().run()