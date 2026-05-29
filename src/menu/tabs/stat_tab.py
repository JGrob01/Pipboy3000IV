from src.menu.tabs.tab_base import Tab
from src.config import GREEN


class StatTab(Tab):
    name = "STAT"
    sub_tabs = ["STATUS", "SPECIAL", "PERKS"]

    def draw_content(self, surface, rect):
        label = self.sub_tabs[self.active_sub]
        text = self.font.render(f"[{label} CONTENT]", True, GREEN)
        surface.blit(text, (
            rect.centerx - text.get_width() // 2,
            rect.centery,
        ))

    def draw_footer(self, surface, rect):
        hp = self.font.render("HP  80/80", True, GREEN)
        level = self.font.render("LEVEL 1", True, GREEN)
        ap = self.font.render("AP  90/90", True, GREEN)
        y = rect.top + 5
        surface.blit(hp, (rect.left + 10, y))
        surface.blit(level, (rect.centerx - level.get_width() // 2, y))
        surface.blit(ap, (rect.right - ap.get_width() - 10, y))