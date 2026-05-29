import pygame

from src.menu.tabs.tab_base import Tab
from src.config import GREEN, GREEN_MEDIUM, BG


class InvTab(Tab):
    name = "INV"
    sub_tabs = ["WEAPONS", "APPAREL", "AID", "MISC", "AMMO"]

    def draw_content(self, surface, rect):
        label = self.sub_tabs[self.active_sub]
        text = self.font.render(f"[{label} LIST]", True, GREEN)
        surface.blit(text, (
            rect.centerx - text.get_width() // 2,
            rect.centery,
        ))

    def draw_footer(self, surface, rect):
        margin = 12
        gap = 8
        h = 28
        y = rect.top + (rect.height - h) // 2

        box_w = (rect.width - margin * 2 - gap) // 2

        weight_rect = pygame.Rect(margin, y, box_w, h)
        pygame.draw.rect(surface, GREEN_MEDIUM, weight_rect)
        wt = self.font.render("WEIGHT  42/150", True, GREEN)
        surface.blit(wt, (weight_rect.left + 10,
                        weight_rect.centery - wt.get_height() // 2))

        caps_rect = pygame.Rect(weight_rect.right + gap, y, box_w, h)
        pygame.draw.rect(surface, GREEN_MEDIUM, caps_rect)
        cp = self.font.render("CAPS  237", True, GREEN)
        surface.blit(cp, (caps_rect.right - cp.get_width() - 10,
                        caps_rect.centery - cp.get_height() // 2))