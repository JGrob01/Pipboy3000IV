from src.menu.tabs.tab_base import Tab
from src.config import GREEN


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
        weight = self.font.render("WEIGHT  42/150", True, GREEN)
        caps = self.font.render("CAPS  237", True, GREEN)
        y = rect.top + 5
        surface.blit(weight, (rect.left + 10, y))
        surface.blit(caps, (rect.right - caps.get_width() - 10, y))