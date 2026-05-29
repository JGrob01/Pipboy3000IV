import pygame
import os
import sys
import glob
import math

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
        self._started = False

        # Pre-render text as a single tall surface
        lines = text.split("\n")
        line_h = self.font.get_height() + 2
        self.text_h = line_h * len(lines)
        self.text_surf = pygame.Surface((SCREEN_SIZE[0], self.text_h), pygame.SRCALPHA)
        for i, line in enumerate(lines):
            rendered = self.font.render(line, True, GREEN)
            self.text_surf.blit(rendered, (0, i * line_h))

        # Total travel: from below the screen to above it
        self.start_y = SCREEN_SIZE[1]
        self.end_y = -self.text_h

    def update(self, dt):
        if not self._started:
            self._started = True
            return
        self.elapsed += min(dt, 0.05)   # never advance more than 50ms per frame
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
        self._started = False

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
        if not self._started:
            self._started = True
            return
        self.elapsed += min(dt, 0.05)   # never advance more than 50ms per frame

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
    """Pip-Boy main UI with a wraparound scroll-in on entry."""

    PAUSE_BEFORE = 0.0      # blank pause before menu appears
    SCROLL_UP_DURATION = .5    # time spent scrolling up (6 wraps)
    SCROLL_BACK_DURATION = 0.25  # time to come back down
    WRAP_COUNT = 6              # number of full screen-heights scrolled up

    def __init__(self, app, font):
        super().__init__(app)
        self.font = font
        self.tabs = ["STAT", "INV", "DATA", "MAP", "RADIO"]
        self.active = 0

        # Pre-render the static menu to its own surface (one screen worth)
        self.menu_surf = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self._render_menu_to(self.menu_surf)

        self.elapsed = 0.0
        self.settled = False

    def _render_menu_to(self, surface):
        """Draws the menu onto the given surface at its final layout."""
        surface.fill((0, 0, 0, 0))   # transparent
        x = 20
        base_y = 16
        for i, tab in enumerate(self.tabs):
            color = BG if i == self.active else GREEN
            tab_w = self.font.size(tab)[0]
            if i == self.active:
                pygame.draw.rect(surface, GREEN,
                    (x - 8, base_y - 4, tab_w + 16, self.font.get_height() + 8))
            surface.blit(self.font.render(tab, True, color), (x, base_y))
            x += tab_w + 40

    def handle_event(self, event):
        if not self.settled:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.active = (self.active + 1) % len(self.tabs)
                self._render_menu_to(self.menu_surf)
            elif event.key == pygame.K_LEFT:
                self.active = (self.active - 1) % len(self.tabs)
                self._render_menu_to(self.menu_surf)

    def update(self, dt):
        if self.settled:
            return
        self.elapsed += dt
        total = self.PAUSE_BEFORE + self.SCROLL_UP_DURATION + self.SCROLL_BACK_DURATION
        if self.elapsed >= total:
            self.settled = True

    def _scroll_offset(self):
        """Returns current Y offset from final position (0 = settled)."""
        t = self.elapsed - self.PAUSE_BEFORE
        screen_h = SCREEN_SIZE[1]

        if t <= 0:
            # Hasn't started yet — sit off-screen at bottom
            return screen_h

        if t < self.SCROLL_UP_DURATION:
            # Phase 1: scrolling up
            # Travel from +screen_h down to -(WRAP_COUNT * screen_h)
            p = t / self.SCROLL_UP_DURATION
            start = screen_h
            end = -self.WRAP_COUNT * screen_h
            return start + (end - start) * p

        t2 = t - self.SCROLL_UP_DURATION
        if t2 < self.SCROLL_BACK_DURATION:
            # Phase 2: scrolling back down to settle at 0
            p = t2 / self.SCROLL_BACK_DURATION
            # Ease the landing — quadratic deceleration
            p = 1 - (1 - p) ** 2
            start = -self.WRAP_COUNT * screen_h
            end = 0
            return start + (end - start) * p

        return 0

    def draw(self, surface):
        surface.fill(BG)
        offset = int(self._scroll_offset())
        screen_h = SCREEN_SIZE[1]

        # Tile the menu surface vertically so wrapping looks seamless
        # Find the topmost copy that's visible
        y = offset % screen_h
        if y > 0:
            y -= screen_h

        # Blit copies until we're past the bottom of the screen
        while y < screen_h:
            surface.blit(self.menu_surf, (0, y))
            y += screen_h


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
        self.font = pygame.font.Font(font_path if os.path.exists(font_path) else None, 18)
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
            fps=31,
            repeat_section=(223, 246),   # adjust to your indices
            repeat_count=4,
            next_screen=self.main_screen,
        )

        # Start with the scroll, which chains into boot, which chains into main
        self.current = self.scroll_screen
        self.boot_sound.play()
        #self.current = self.main_screen

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


if __name__ == "__main__":
    App().run()