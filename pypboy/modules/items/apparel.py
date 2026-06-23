import pypboy
import pygame
import game
import settings


class Module(pypboy.SubModule):

    label = "APPAREL"
    SELECTION_MODE = "multi"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)        
        self.menu = pypboy.ui.Menu(settings.ARMOR)
        self.menu.selection_key = "items.apparel"
        self.menu.selection_mode = self.SELECTION_MODE
        self.menu.rect[0] = settings.menu_x
        self.menu.rect[1] = settings.menu_y
        self.menu.image_offset_y = 0
        self.menu.description_offset_y = -10
        self.add(self.menu)

        self.topmenu = pypboy.ui.TopMenu()
        self.add(self.topmenu)
        self.topmenu.label = "INV"
        self.topmenu.title = settings.MODULE_TEXT

        self.footer = pypboy.ui.Footer(settings.FOOTER_ARMOR)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)
