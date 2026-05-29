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
        self.current_tab.draw_footer(surface, footer_rect)

    def _draw_header(self, surface, rect):
        """Draws the main tabs with the underline bar that wraps around the active tab."""
        names = [t.name for t in self.tabs]
        gap = 50
        total_w = sum(self.font.size(n)[0] for n in names) + gap * (len(names) - 1)
        x = (rect.width - total_w) // 2
        y = (rect.height - self.font.get_height()) // 2

        # Draw tab labels and record the active tab's x extent
        active_x_start = None
        active_x_end = None
        cursor = x
        for i, name in enumerate(names):
            w = self.font.size(name)[0]
            if i == self.active:
                active_x_start = cursor
                active_x_end = cursor + w
            # All header tab labels are full GREEN (white-ish per your spec)
            surface.blit(self.font.render(name, True, GREEN), (cursor, y))
            cursor += w + gap

        # The horizontal bar runs across the screen at this Y
        bar_y = rect.bottom - 4

        # Drop tics sit just inside the bar's ends, plus around the active tab
        tic_height = 10
        margin = 20  # how far from screen edges the bar starts/ends

        # Horizontal segments of the bar, broken by the active-tab gap
        # Left segment: from margin → active_x_start - small_gap
        # Right segment: from active_x_end + small_gap → screen_width - margin
        gap_around_active = 12  # how far the bar pulls back from the tab edges

        left_end = active_x_start - gap_around_active
        right_start = active_x_end + gap_around_active

        # Draw the two horizontal segments
        pygame.draw.line(surface, GREEN, (margin, bar_y), (left_end, bar_y), 2)
        pygame.draw.line(surface, GREEN, (right_start, bar_y), (rect.width - margin, bar_y), 2)

        # Vertical tics: at outer edges and on either side of the active tab
        pygame.draw.line(surface, GREEN, (margin, bar_y), (margin, bar_y + tic_height), 2)
        pygame.draw.line(surface, GREEN, (rect.width - margin, bar_y), (rect.width - margin, bar_y + tic_height), 2)
        pygame.draw.line(surface, GREEN, (left_end, bar_y), (left_end, bar_y + tic_height), 2)
        pygame.draw.line(surface, GREEN, (right_start, bar_y), (right_start, bar_y + tic_height), 2)