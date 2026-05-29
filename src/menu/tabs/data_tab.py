import pygame

from src.menu.tabs.tab_base import Tab
from src.config import GREEN


class DataTab(Tab):
    name = "DATA"
    sub_tabs = ["QUESTS", "WORKSHOPS", "STATS"]

    def draw_content(self, surface, rect):
        label = self.sub_tabs[self.active_sub]
        text = self.font.render(f"[{label}]", True, GREEN)
        surface.blit(text, (
            rect.centerx - text.get_width() // 2,
            rect.centery,
        ))