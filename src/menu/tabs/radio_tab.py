import pygame

from src.menu.tabs.tab_base import Tab
from src.config import GREEN


class RadioTab(Tab):
    name = "RADIO"
    sub_tabs = ["DIAMOND CITY", "CLASSICAL", "RADIO FREEDOM"]

    def draw_content(self, surface, rect):
        text = self.font.render("[RADIO]", True, GREEN)
        surface.blit(text, (
            rect.centerx - text.get_width() // 2,
            rect.centery,
        ))