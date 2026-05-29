import pygame

from src.config import GREEN, GREEN_MEDIUM, GREEN_DIM


class Tab:
    """Base class for a main tab. Owns its sub-tabs, content, and footer."""

    name = "TAB"
    sub_tabs = []

    def __init__(self, app):
        self.app = app
        self.font = app.font_body
        self.font_small = app.font_small
        self.active_sub = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.active_sub = (self.active_sub - 1) % len(self.sub_tabs)
            elif event.key == pygame.K_DOWN:
                self.active_sub = (self.active_sub + 1) % len(self.sub_tabs)

    def _color_for_distance(self, distance):
        if distance == 0:
            return GREEN
        if distance == 1:
            return GREEN_MEDIUM
        if distance == 2:
            return GREEN_DIM
        return None

    def draw_sub_tabs(self, surface, y):
        x = 20
        for i, name in enumerate(self.sub_tabs):
            distance = abs(i - self.active_sub)
            color = self._color_for_distance(distance)
            text_w = self.font.size(name)[0]
            if color is not None:
                text = self.font.render(name, True, color)
                surface.blit(text, (x, y))
            x += text_w + 30

    def draw_content(self, surface, rect):
        pass

    def draw_footer(self, surface, rect):
        pass