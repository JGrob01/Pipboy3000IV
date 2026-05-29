import pygame

from src.menu.tabs.tab_base import Tab
from src.config import GREEN, GREEN_MEDIUM, BG


class StatTab(Tab):
    name = "STAT"
    sub_tabs = ["STATUS", "SPECIAL", "PERKS"]

    # Placeholder data — wire to a real player object later
    hp = 80
    hp_max = 80
    level = 25
    level_progress = 0.6   # 0.0–1.0
    ap = 90
    ap_max = 90

    def draw_content(self, surface, rect):
        label = self.sub_tabs[self.active_sub]
        text = self.font.render(f"[{label} CONTENT]", True, GREEN)
        surface.blit(text, (
            rect.centerx - text.get_width() // 2,
            rect.centery,
        ))

    def draw_footer(self, surface, rect):
        # Layout: three boxes spanning the width with small gaps
        margin = 12
        gap = 8
        h = 28
        y = rect.top + (rect.height - h) // 2

        # Side boxes are roughly 1/4 the width each, middle box gets the rest
        side_w = (rect.width - margin * 2 - gap * 2) // 4
        mid_w = rect.width - margin * 2 - gap * 2 - side_w * 2

        # --- HP box (left, green-filled, white text) ---
        hp_rect = pygame.Rect(margin, y, side_w, h)
        pygame.draw.rect(surface, GREEN_MEDIUM, hp_rect)
        hp_text = self.font.render(f"HP  {self.hp}/{self.hp_max}", True, GREEN)
        surface.blit(hp_text, (
            hp_rect.left + 10,
            hp_rect.centery - hp_text.get_height() // 2,
        ))

        # --- LEVEL box (middle, green outline + white progress bar) ---
        level_rect = pygame.Rect(hp_rect.right + gap, y, mid_w, h)
        pygame.draw.rect(surface, GREEN_MEDIUM, level_rect, 2)   # outline only

        # "LEVEL N" text on the left side of the box
        level_text = self.font.render(f"LEVEL {self.level}", True, GREEN)
        surface.blit(level_text, (
            level_rect.left + 8,
            level_rect.centery - level_text.get_height() // 2,
        ))

        # Progress bar fills the space to the right of the label
        bar_left = level_rect.left + 8 + level_text.get_width() + 10
        bar_right = level_rect.right - 8
        bar_top = level_rect.top + 6
        bar_bottom = level_rect.bottom - 6
        bar_w = bar_right - bar_left
        bar_h = bar_bottom - bar_top
        fill_w = int(bar_w * self.level_progress)
        if fill_w > 0:
            pygame.draw.rect(surface, GREEN,
                pygame.Rect(bar_left, bar_top, fill_w, bar_h))

        # --- AP box (right, green-filled, white text) ---
        ap_rect = pygame.Rect(level_rect.right + gap, y, side_w, h)
        pygame.draw.rect(surface, GREEN_MEDIUM, ap_rect)
        ap_text = self.font.render(f"AP  {self.ap}/{self.ap_max}", True, GREEN)
        surface.blit(ap_text, (
            ap_rect.right - ap_text.get_width() - 10,
            ap_rect.centery - ap_text.get_height() // 2,
        ))