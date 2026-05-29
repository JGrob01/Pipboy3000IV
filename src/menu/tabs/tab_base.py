import pygame

from src.config import GREEN, GREEN_DIM


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

    def draw_sub_tabs(self, surface, y):
        """Draws the sub-tab row at the given y position."""
        x = 20
        for i, name in enumerate(self.sub_tabs):
            color = GREEN if i == self.active_sub else GREEN_DIM
            text = self.font.render(name, True, color)
            surface.blit(text, (x, y))
            x += text.get_width() + 30

    def draw_content(self, surface, rect):
        """Override to draw this tab's content within the given rect."""
        pass

    def draw_footer(self, surface, rect):
        """Override to draw this tab's footer within the given rect."""
        pass