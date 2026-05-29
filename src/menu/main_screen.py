import pygame

from src.screen import Screen
from src.config import SCREEN_SIZE, GREEN, BG
from src.menu.tabs.stat_tab import StatTab
from src.menu.tabs.inv_tab import InvTab
from src.menu.tabs.data_tab import DataTab
from src.menu.tabs.map_tab import MapTab
from src.menu.tabs.radio_tab import RadioTab


class MainScreen(Screen):
    """Top-level Pip-Boy menu — tab orchestrator with wraparound scroll-in intro."""

    HEADER_H = 40
    SUBHEADER_H = 30
    FOOTER_H = 50

    # Intro animation tuning
    PAUSE_BEFORE = 0.0
    SCROLL_UP_DURATION = 0.5
    SCROLL_BACK_DURATION = 0.25
    WRAP_COUNT = 6

    def __init__(self, app, font):
        super().__init__(app)
        self.font = font
        self.tabs = [
            StatTab(app),
            InvTab(app),
            DataTab(app),
            MapTab(app),
            RadioTab(app),
        ]
        self.active = 0

        # Intro animation state
        self.elapsed = 0.0
        self.settled = False
        self._intro_surf = pygame.Surface(SCREEN_SIZE)

    @property
    def current_tab(self):
        return self.tabs[self.active]

    def handle_event(self, event):
        # Ignore input during the intro
        if not self.settled:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.active = (self.active + 1) % len(self.tabs)
            elif event.key == pygame.K_LEFT:
                self.active = (self.active - 1) % len(self.tabs)
            else:
                self.current_tab.handle_event(event)

    def update(self, dt):
        if self.settled:
            return
        self.elapsed += dt
        total = self.PAUSE_BEFORE + self.SCROLL_UP_DURATION + self.SCROLL_BACK_DURATION
        if self.elapsed >= total:
            self.settled = True

    def _scroll_offset(self):
        """Returns current Y offset (0 = settled at final position)."""
        t = self.elapsed - self.PAUSE_BEFORE
        screen_h = SCREEN_SIZE[1]

        if t <= 0:
            return screen_h

        if t < self.SCROLL_UP_DURATION:
            p = t / self.SCROLL_UP_DURATION
            start = screen_h
            end = -self.WRAP_COUNT * screen_h
            return start + (end - start) * p

        t2 = t - self.SCROLL_UP_DURATION
        if t2 < self.SCROLL_BACK_DURATION:
            p = t2 / self.SCROLL_BACK_DURATION
            p = 1 - (1 - p) ** 2   # ease-out
            start = -self.WRAP_COUNT * screen_h
            end = 0
            return start + (end - start) * p

        return 0

    def draw(self, surface):
        if self.settled:
            # Normal draw, directly to surface
            self._draw_layout(surface)
        else:
            # Render full layout to intro surface, then tile with offset
            self._draw_layout(self._intro_surf)

            surface.fill(BG)
            offset = int(self._scroll_offset())
            screen_h = SCREEN_SIZE[1]
            y = offset % screen_h
            if y > 0:
                y -= screen_h
            while y < screen_h:
                surface.blit(self._intro_surf, (0, y))
                y += screen_h

    def _draw_layout(self, surface):
        """Draws the full Pip-Boy menu layout (header/sub-tabs/content/footer)."""
        surface.fill(BG)
        sw, sh = SCREEN_SIZE

        self._draw_header(surface, pygame.Rect(0, 0, sw, self.HEADER_H))
        self.current_tab.draw_sub_tabs(surface, self.HEADER_H + 5)

        content_rect = pygame.Rect(
            0,
            self.HEADER_H + self.SUBHEADER_H,
            sw,
            sh - self.HEADER_H - self.SUBHEADER_H - self.FOOTER_H,
        )
        self.current_tab.draw_content(surface, content_rect)

        footer_rect = pygame.Rect(0, sh - self.FOOTER_H, sw, self.FOOTER_H)
        pygame.draw.line(surface, GREEN,
            (10, footer_rect.top), (sw - 10, footer_rect.top), 1)
        self.current_tab.draw_footer(surface, footer_rect)

    def _draw_header(self, surface, rect):
        names = [t.name for t in self.tabs]
        gap = 60
        total_w = sum(self.font.size(n)[0] for n in names) + gap * (len(names) - 1)
        x = (rect.width - total_w) // 2
        y = (rect.height - self.font.get_height()) // 2

        active_x_start = None
        active_x_end = None
        cursor = x
        for i, name in enumerate(names):
            w = self.font.size(name)[0]
            if i == self.active:
                active_x_start = cursor
                active_x_end = cursor + w
            surface.blit(self.font.render(name, True, GREEN), (cursor, y))
            cursor += w + gap

        if active_x_start is not None:
            pygame.draw.line(surface, GREEN,
                (active_x_start, rect.bottom - 4),
                (active_x_end, rect.bottom - 4), 2)