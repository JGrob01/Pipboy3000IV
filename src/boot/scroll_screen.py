import pygame

from src.screen import Screen
from src.config import SCREEN_SIZE, GREEN, BG


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