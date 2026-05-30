import game  #
import pygame
import settings
import time
import os
import importlib
# import cairosvg
import io
from datetime import datetime
from collections import deque

def word_wrap(surf, text, font):
    text = str(text)
    font.origin = True
    words = text.split()
    width, height = surf.get_size()
    line_spacing = font.get_sized_height()
    x, y = 0, line_spacing
    for word in words:
        word = word + str("  ")
        bounds = font.get_rect(word)
        if x + bounds.width + bounds.x >= width:
            x, y = 0, y + line_spacing
        # if x + bounds.width + bounds.x >= width:
        #    raise ValueError("word too wide for the surface")
        # if y + bounds.height - bounds.y >= height:
        #    raise ValueError("text to long for the surface")
        font.render_to(surf, (x, y), word, settings.bright, None, 1)
        x += bounds.width
    return x, y


def load_svg(filename, width, height):
    # Pygame.image now supports basic SVGs as a un-documented feature but SVG files must be flattened with a background


    # drawing = cairosvg.svg2png(url=filename) #Cairo is a pain to install.
    # byte_io = io.BytesIO(drawing)
    # image = pygame.image.load(byte_io)
    # print ("Loading svg:",filename)
    image = pygame.image.load(filename).convert_alpha()
    size = image.get_size()
    scale = min(width / size[0], height / size[1])
    if size[1] != height:
        print("Rescaling", filename, "from", size[0], "x", size[1], "to", width, "x", height)
        image = pygame.transform.smoothscale(image, (round(size[0] * scale), round(size[1] * scale)))
    image.fill(settings.bright, None, pygame.BLEND_RGBA_MULT)
    return image


class TopMenu(game.Entity):

    def __init__(self, label=None, title=[]):
        self.label = None
        self.prev_label = 0
        self.title = []
        super(TopMenu, self).__init__((settings.WIDTH, 40))
        self.rect[0] = 0
        self.rect[1] = 21
        self.saved_label = None

    def render(self):
        # super(TopMenu, self).render(*args, **kwargs)
        if settings.hide_top_menu and settings.hide_top_menu != 3:
            self.image.fill((0, 0, 0))
            settings.hide_top_menu = 3
            if self.label:
                self.saved_label = self.label
                self.prev_label = None
                self.label = None
        elif not settings.hide_top_menu:
            if self.saved_label:
                self.label = self.saved_label
                self.saved_label = None
            spacing = 40  # Set space between words
            prev_text_width = 74  # STAT width
            text_pos = 104 - spacing - prev_text_width  # Set first location
            if self.label:
                if self.label != self.prev_label:
                    self.image.fill((0, 0, 0))  # Clear text
                    for section in self.title:
                        text = settings.RobotoB[33].render(section, True, (settings.bright), (0, 0, 0))  # Setup text
                        text_pos = text_pos + prev_text_width + spacing  # Set draw location
                        self.image.blit(text, (text_pos, 0))  # Draw text
                        text_rect = text.get_rect()  # Get text dimensions
                        prev_text_width = text_rect.width

                        if section == self.label:
                            pygame.draw.line(self.image, settings.bright, (10, 35), (text_pos - 11, 35),
                                             2)  # Line from left edge of screen
                            pygame.draw.line(self.image, settings.bright, (text_pos + text_rect.width + 11, 35),
                                             (settings.WIDTH - 10, 35), 2)  # Line to the right edge of screen
                            pygame.draw.line(self.image, settings.bright, (text_pos - 12, 10), (text_pos - 12, 35),
                                             2)  # Left Vert bar
                            pygame.draw.line(self.image, settings.bright, (text_pos - 12, 10), (text_pos - 3, 10),
                                             2)  # Left Short bar
                            pygame.draw.line(self.image, settings.bright, (text_pos + text_rect.width + 2, 10),
                                             (text_pos + text_rect.width + 12, 10), 2)  # Right Short bar
                            pygame.draw.line(self.image, settings.bright, (text_pos + text_rect.width + 11, 10),
                                             (text_pos + text_rect.width + 11, 35), 2)  # Right Vert bar
                            pygame.draw.line(self.image, settings.bright, (10, 35), (10, 45),
                                             2)  # Downline line at left edge of screen
                            pygame.draw.line(self.image, settings.bright, (settings.WIDTH - 10, 35),
                                             (settings.WIDTH - 10, 45), 2)  # Downline line at right edge of screen
                        else:
                            pygame.draw.line(self.image, settings.bright, (text_pos - 10, 35),
                                             (text_pos + text_rect.width + 10, 35),
                                             2)  # Horizontal Barclass TopMenu(game.Entity):
                self.prev_label = self.label

        if settings.glitch:
            if settings.glitch_next == 1 or settings.glitch_next == 3 or settings.glitch_next == 5:
                self.rect[1] = -149
            elif settings.glitch_next == 2 or settings.glitch_next == 4 or settings.glitch_next == 6:
                self.rect[1] = 251
            elif settings.glitch_next >= 7:
                self.rect[1] = 21


class Scanlines(game.core.Entity):

    def __init__(self):
        super(Scanlines, self).__init__((settings.WIDTH, 129))
        # self.width = 720
        # self.height = 1600
        self.image = pygame.image.load('images/scanline.png').convert_alpha()
        self.rectimage = self.image.get_rect()
        self.rect[1] = 0
        self.top = -130
        self.speed = 10
        self.clock = pygame.time.Clock()
        self.animation_time = 0.05
        self.prev_time = 0
        self.dirty = 2

    def render(self, *args, **kwargs):
        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_time

        if self.delta_time >= self.animation_time:
            self.prev_time = self.current_time
            self.top = self.top + self.speed
            if self.top >= settings.HEIGHT + 130:
                self.top = -130
            self.rect[1] = self.top
        super(Scanlines, self).render(self, *args, **kwargs)


class Overlay(game.Entity):
    def __init__(self):
        super(Overlay, self).__init__()
        self.image = pygame.image.load('images/overlay.png').convert_alpha()


class SubMenu(game.Entity):

    # Layout
    ITEM_GAP = 25        # horizontal gap between submenu items, in pixels
    SLIDE_SPEED = 450         # pixels/second for the smooth scroll
    # Brightness ramp: index 0 = selected, 1 = neighbor, 2 = next out, 3+ = invisible
    BRIGHTNESS = [None, None, None]  # filled in __init__ from settings

    def __init__(self):
        super(SubMenu, self).__init__((settings.WIDTH, 36))
        self.menu = []
        self.rect[0] = 0
        self.rect[1] = settings.submenu_y if hasattr(settings, 'submenu_y') else 63

        self.selected = None
        self.saved_module = None
        self._prev_sel_idx = None

        # Animation state
        self._current_offset = 0.0   # current scroll position (pixels)
        self._target_offset = 0.0    # where we're scrolling to
        self._prev_time = time.time()

        # Cache rendered text per item per brightness tier
        # key: (text, tier) -> Surface
        self._text_cache = {}
        
        # Brightness tiers: selected, neighbor, far, then invisible
        SubMenu.BRIGHTNESS = [settings.bright, settings.mid, settings.dim]

    def select(self, module):
        if module not in self.menu:
            return
        self.selected = module
        # Selected item should land at strip position 0 (= centered)
        self._target_offset = 0.0

    def _render_text(self, text, tier):
        """Return cached text surface for a given brightness tier."""
        key = (text, tier)
        if key not in self._text_cache:
            color = self.BRIGHTNESS[tier]
            self._text_cache[key] = settings.RobotoR[30].render(
                text, True, color, settings.black
            )
        return self._text_cache[key]

    def _active_tab_center_x(self):
        if not hasattr(self, 'parent') or not hasattr(self.parent, 'pypboy'):
            print("SubMenu: no parent chain, falling back to center")
            return settings.WIDTH // 2

        active_label = None
        try:
            pypboy_engine = self.parent.pypboy
            for name, mod in pypboy_engine.modules.items():
                if mod is pypboy_engine.active:
                    mapping = {
                        "stats": "STAT",
                        "items": "INV",
                        "data": "DATA",
                        "map": "MAP",
                        "radio": "RADIO",
                    }
                    active_label = mapping.get(name)
                    break
        except Exception as e:
            print(f"SubMenu: exception finding active: {e}")
            return settings.WIDTH // 2

        if active_label is None:
            print("SubMenu: no active label matched, falling back")
            return settings.WIDTH // 2

        # Replicate TopMenu's spacing math
        spacing = 40
        prev_text_width = 74   # STAT width baseline used in TopMenu
        text_pos = 104 - spacing - prev_text_width
        for section in settings.MODULE_TEXT:
            text_surf = settings.RobotoB[33].render(section, True, settings.bright, (0, 0, 0))
            text_pos = text_pos + prev_text_width + spacing
            text_rect = text_surf.get_rect()
            prev_text_width = text_rect.width
            if section == active_label:
                return text_pos + text_rect.width // 2

        return settings.WIDTH // 2
    
    def _item_width(self, item, tier):
        return self._render_text(item, tier).get_width()

    def _item_positions(self):
        """Return a list of center-X positions in strip-space, one per item.

        Strip-space: arbitrary coordinate where item 0's center is at some
        position, item 1's center is past it, etc. We use the brightness tier
        each item *would* have at its current distance from selected to size it.
        """
        if not self.menu or self.selected is None:
            return []
        sel_idx = self.menu.index(self.selected)
        positions = [0.0] * len(self.menu)

        # Walk right from selected
        cursor = 0.0
        positions[sel_idx] = cursor
        for i in range(sel_idx + 1, len(self.menu)):
            distance = i - sel_idx
            tier = min(distance, len(self.BRIGHTNESS) - 1)
            prev_distance = (i - 1) - sel_idx
            prev_tier = min(prev_distance, len(self.BRIGHTNESS) - 1)
            half_prev = self._item_width(self.menu[i - 1], prev_tier) / 2
            half_curr = self._item_width(self.menu[i], tier) / 2
            cursor += half_prev + self.ITEM_GAP + half_curr
            positions[i] = cursor

        # Walk left from selected
        cursor = 0.0
        for i in range(sel_idx - 1, -1, -1):
            distance = sel_idx - i
            tier = min(distance, len(self.BRIGHTNESS) - 1)
            prev_distance = sel_idx - (i + 1)
            prev_tier = min(prev_distance, len(self.BRIGHTNESS) - 1)
            half_prev = self._item_width(self.menu[i + 1], prev_tier) / 2
            half_curr = self._item_width(self.menu[i], tier) / 2
            cursor -= half_prev + self.ITEM_GAP + half_curr
            positions[i] = cursor

        return positions

    def render(self):
        if settings.hide_submenu and settings.hide_submenu != 3:
            settings.hide_submenu = 3
            self.image.fill(settings.black)
            self.saved_module = self.selected
            return
        elif not settings.hide_submenu and self.saved_module:
            self.select(self.saved_module)
            self.saved_module = None

        if settings.glitch:
            if settings.glitch_next in (1, 3, 5):
                self.rect[1] = -107
            elif settings.glitch_next in (2, 4, 6):
                self.rect[1] = 293
            elif settings.glitch_next >= 7:
                self.rect[1] = settings.submenu_y if hasattr(settings, 'submenu_y') else 93

        if not self.menu or self.selected is None:
            self.image.fill(settings.black)
            return

        # Compute strip positions every frame (cheap; just summing widths)
        positions = self._item_positions()
        sel_idx = self.menu.index(self.selected)

        # Animate _current_offset toward 0 from wherever it was when selection changed.
        # When selection changes, we need to also shift _current_offset by the delta
        # so the slide is relative. Track previous selection to detect changes.
        if self._prev_sel_idx is None:
            self._prev_sel_idx = sel_idx
            self._current_offset = 0.0

        if self._prev_sel_idx != sel_idx:
            # Slide starts from where the old selected item lands in the new layout
            old_idx = self._prev_sel_idx
            self._current_offset = positions[old_idx]
            self._prev_sel_idx = sel_idx

        now = time.time()
        dt = now - self._prev_time
        self._prev_time = now
        if dt > 0.1:
            dt = 0.1
        diff = self._target_offset - self._current_offset
        if abs(diff) > 0.5:
            step = self.SLIDE_SPEED * dt
            if step >= abs(diff):
                self._current_offset = self._target_offset
            else:
                self._current_offset += step if diff > 0 else -step
        else:
            self._current_offset = self._target_offset

        self.image.fill(settings.black)
        center_x = self._active_tab_center_x()

        for idx, item in enumerate(self.menu):
            distance = abs(idx - sel_idx)
            if distance >= len(self.BRIGHTNESS):
                continue
            tier = distance

            screen_x_center = center_x + (positions[idx] - self._current_offset)
            surf = self._render_text(item, tier)
            w, h = surf.get_size()
            draw_x = int(screen_x_center - w / 2)

            if draw_x + w < 0 or draw_x > settings.WIDTH:
                continue
            self.image.blit(surf, (draw_x, 0))


class Footer(game.Entity):
    def __init__(self, sections=[]):
        super(Footer, self).__init__((settings.WIDTH, 38))
        self.sections = sections

        time_text = self.time_text()
        self.date = time_text[0]
        self.time = time_text[1]

        self.text_left = None
        self.text_middle = None
        self.text_right = None
        self.bar_graph_num = None
        self.bar_graph_centered = False
        self.line_1 = None
        self.line_2 = None
        self.current_time = 0

        self.padding = 12
        self.animation_time = 0.5
        self.delta_time = 0
        self.prev_time = 0

        # Example data sets:
        #  ["Left_text", "Right_Text", "Middle", Bar_graph_value, "Bar_graph_centered"]
        # self.sections = []
        # self.sections = ["HP 115/115", "LEVEL 66", "AP 90/90", 90, True]
        # self.sections = ["WEIGHT: 19/220", "CAPS: 1", "HP", 25, False]
        # self.sections = ["DATE", "TIME", "Commonwealth", None, False]
        # self.sections = [""DATE, "TIME"]

    def expand(self, oldValue, oldMin, oldMax, newMin, newMax):
        oldRange = oldMax - oldMin
        newRange = newMax - newMin
        newValue = ((oldValue - oldMin) * newRange / oldRange) + newMin
        return newValue

    def time_text(self):
        now = datetime.now()
        date = str(now.strftime("%m") + "/" + now.strftime("%d") + "/" + now.strftime("%Y"))
        time = now.strftime("%H:%M:%S")
        return date, time

    def render(self):
        if settings.hide_footer and settings.hide_footer != 3:
            self.image.fill((0, 0, 0))
            settings.hide_footer = 3
        elif not settings.hide_footer:
            self.current_time = time.time()
            self.delta_time = self.current_time - self.prev_time

            if self.delta_time >= self.animation_time:
                self.prev_time = self.current_time

                if self.sections:

                    self.rect[0] = settings.footer_x
                    self.rect[1] = settings.footer_y
                    self.image.fill(settings.dark)

                    self.text_width = 0
                    self.line_1 = 0
                    self.line_2 = 0

                    try:
                        self.text_left = str(self.sections[0])
                    except:
                        self.text_left = None

                    try:
                        self.text_middle = str(self.sections[1])
                    except:
                        self.text_middle = None

                    try:
                        self.text_right = str(self.sections[2])
                    except:
                        self.text_right = None

                    try:
                        self.bar_graph_num = self.sections[3]
                    except:
                        self.bar_graph_num = None

                    try:
                        self.bar_graph_centered = self.sections[4]
                    except:
                        self.bar_graph_centered = False

                    if self.text_left == "DATE" or self.text_middle == "TIME":
                        time_text = self.time_text()
                        self.date = time_text[0]
                        self.time = time_text[1]
                        self.text_left = self.date
                        self.text_middle = self.time

                    # Left Text
                    if self.text_left:
                        text = settings.RobotoB[28].render(self.text_left, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.padding, 3))
                        self.line_1 = self.text_width + self.padding * 3
                        if self.text_right != "" or self.text_middle != "":
                            pygame.draw.line(self.image, settings.black, (self.line_1, 0),
                                             (self.line_1, 38), 5)

                    # If there is a bar graph, and it is centered: Draw right text then middle with bar-graph:
                    if isinstance(self.bar_graph_num, int) and self.bar_graph_centered:
                        text = settings.RobotoB[28].render(self.text_right, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (settings.WIDTH - self.text_width - self.padding, 3))
                        self.line_2 = settings.WIDTH - self.text_width - self.padding * 3
                        pygame.draw.line(self.image, settings.black, (self.line_2, 0), (self.line_2, 38), 5)

                        text = settings.RobotoB[28].render(self.text_middle, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_1 + self.padding, 3))
                        bar_graph_start = self.line_1 + self.text_width + self.padding * 2
                        bar_graph_end = self.line_2 - self.padding

                        pygame.draw.lines(self.image, settings.light, True,
                                          [(bar_graph_start, 12), (bar_graph_end, 12),
                                           (bar_graph_end, 26), (bar_graph_start, 26)], 3)  # Level bar surround

                        bar_start = bar_graph_start + 2
                        bar_max_width = bar_graph_end - 2 - bar_start + 2
                        bar_width = int(self.expand(self.bar_graph_num, 0, 100, 0, bar_max_width))
                        pygame.draw.rect(self.image, settings.bright, (bar_start, 14, bar_width, 11))  # Level bar fill

                    # If there is a bar graph and it is NOT centered: Draw middle text then right with bar-graph
                    elif isinstance(self.bar_graph_num, int) and not self.bar_graph_centered:

                        text = settings.RobotoB[28].render(self.text_middle, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_1 + self.padding, 3))
                        self.line_2 = self.line_1 + self.text_width + self.padding * 2
                        pygame.draw.line(self.image, settings.black, (self.line_2, 0), (self.line_2, 38), 5)

                        text = settings.RobotoB[28].render(self.text_right, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_2 + self.padding, 3))

                        bar_graph_start = self.line_2 + self.text_width + self.padding * 2
                        bar_graph_end = settings.WIDTH - self.padding

                        pygame.draw.lines(self.image, settings.light, True,
                                          [(bar_graph_start, 12), (bar_graph_end, 12),
                                           (bar_graph_end, 26), (bar_graph_start, 26)], 3)  # Level bar surround

                        bar_start = bar_graph_start + 2
                        bar_max_width = bar_graph_end - 2 - bar_start + 2
                        bar_width = int(self.expand(self.bar_graph_num, 0, 100, 0, bar_max_width))
                        pygame.draw.rect(self.image, settings.bright, (bar_start, 14, bar_width, 11))  # Level bar fill

                    # If there is no bar-graph at all: Draw middle then right text
                    else:
                        text = settings.RobotoB[28].render(self.text_middle, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (self.line_1 + self.padding, 3))
                        self.line_2 = self.line_1 + self.text_width + self.padding * 2
                        if self.text_middle != "":
                            pygame.draw.line(self.image, settings.black, (self.line_2, 0), (self.line_2, 38), 5)

                        text = settings.RobotoB[28].render(self.text_right, True, settings.bright, settings.dark)
                        self.text_width = text.get_rect().width
                        self.image.blit(text, (settings.WIDTH - self.text_width - self.padding, 3))

                # #self.image.fill((0, 0, 0)) #Clear text
                # spacing = 4 #Set space between sections
                # prev_text_width = 74 # STAT width
                # text_pos = 104 - spacing - prev_text_width #Set first location

                # for section in self.sections:
                #     text = settings.RobotoB[33].render(section, True, (settings.bright), (0, 0, 0)) #Setup text
                #     text_pos = text_pos + prev_text_width + spacing #Set draw location
                #     self.image.blit(text, (text_pos, 0)) #Draw text
                #     text_rect = text.get_rect() #Get text dimensions
                #     prev_text_width = text_rect.width

                #     if section == self.label:
                #         pygame.draw.line(self.image, (settings.bright), (0, 35), (text_pos - 10, 35), 3) # Line from left edge of screen
                #         pygame.draw.line(self.image, (settings.bright), (text_pos + text_rect.width + 10, 35), (settings.WIDTH, 35), 3) # Line to the right edge of screen
                #         pygame.draw.line(self.image, (settings.bright), (text_pos - 11, 10), (text_pos - 11, 35), 3)	#Left Vert bar
                #         pygame.draw.line(self.image, (settings.bright), (text_pos - 12, 10), (text_pos - 3, 10), 3)	#Left Short bar
                #         pygame.draw.line(self.image, (settings.bright), (text_pos + text_rect.width + 2, 10), (text_pos + text_rect.width + 12, 10), 3)	#Right Short bar
                #         pygame.draw.line(self.image, (settings.bright), (text_pos + text_rect.width + 11, 10), (text_pos + text_rect.width + 11, 35), 3)	#Right Vert bar
                #     else:
                #         pygame.draw.line(self.image, (settings.bright), (text_pos - 10, 35), (text_pos + text_rect.width + 10, 35), 3) # Horizontal Bar


# Menu_array Structure: [["Menu item",Quantity,"Image (or folder for animation")","Description text","Stat Text","Stat Number"],],
# Probably not the correct way to do this.
class Menu(game.Entity):

    def __init__(self, menu_array=[], callbacks=[], selected=0):
        super(Menu, self).__init__((settings.WIDTH - settings.menu_x, 490))
        self.source_array = menu_array

        self.prev_time = 0
        self.prev_fps_time = 0
        self.clock = pygame.time.Clock()
        self.animation_time = 0.2
        self.index = 0
        self.top_of_menu = 0
        self.max_items = 10
        self.menu_array = self.source_array[self.top_of_menu:self.max_items]  # List the array for display
        self.prev_selection = 0

        self.descriptionbox = pygame.Surface((360, 300))
        self.imagebox = pygame.Surface((240, 240))

        self.saved_selection = 0

        try:
            self.callbacks = callbacks
            # print("self.callbacks = ", self.callbacks)
        except:
            self.callbacks = []

        self.arrow_img_up = load_svg("./images/inventory/arrow.svg", 26, 26)
        self.arrow_img_down = pygame.transform.flip(self.arrow_img_up, False, True)

        self.selected = selected
        self.select(self.selected)

        if settings.SOUND_ENABLED:
            self.dial_move_sfx = pygame.mixer.Sound('sounds/pipboy/RotaryVertical/UI_PipBoy_RotaryVertical_01.ogg')
            self.dial_move_sfx.set_volume(settings.VOLUME)

    def select(self, item):
        if not settings.hide_main_menu:
            self.selected = item
            self.redraw()
            if len(self.callbacks) > item and self.callbacks[item]:
                self.callbacks[item]()

    def handle_action(self, action):
        if not settings.hide_main_menu:
            if action == "dial_up":
                # print("Dial up")
                if self.selected > 0:
                    if settings.SOUND_ENABLED:
                        self.dial_move_sfx.play()
                    self.selected -= 1
                    self.select(self.selected)

            if action == "dial_down":
                # print("Dial down")
                if self.selected < len(self.source_array) - 1:
                    self.selected += 1
                    if settings.SOUND_ENABLED:
                        self.dial_move_sfx.play()
                    self.select(self.selected)

    def redraw(self):
        self.image.fill((0, 0, 0))
        offset = 38

        # print("Selected - ",self.selected)
        if self.selected > self.max_items - 1:
            self.top_of_menu = self.selected - self.max_items + 1
            self.menu_array = self.source_array[
                              self.top_of_menu:(self.top_of_menu + self.max_items)]  # List the array for display
            # print("Selection off screen")
        else:
            self.top_of_menu = 0
            self.menu_array = self.source_array[
                              self.top_of_menu:(self.top_of_menu + self.max_items)]  # List the array for display
            self.prev_selection = None
        # print("top of menu = ", self.top_of_menu)

        for i in range(len(self.menu_array)):
            if self.selected > self.max_items - 1:
                self.prev_selection = self.selected
                self.selected = self.selected - self.top_of_menu

            if i == self.selected:
                # print("Selected Index = ", i)
                text = settings.RobotoB[30].render(" %s " % self.menu_array[i][0], True, (0, 0, 0),
                                                   (settings.bright))
                try:
                    number = settings.RobotoB[30].render(" %s " % self.menu_array[i][1], True, (0, 0, 0),
                                                         (settings.bright))
                except:
                    number = ""

                selected_rect = (0, offset, settings.menu_x + 330, text.get_size()[1])
                pygame.draw.rect(self.image, (settings.bright), selected_rect)

                self.images = []
                try:  # Try loading a image if there is one
                    self.image_url = self.menu_array[i][2]
                    if os.path.isdir(self.image_url):
                        for filename in sorted(os.listdir(self.image_url)):
                            if filename.endswith(".png"):
                                filename = self.image_url + "/" + filename
                                self.images.append(pygame.image.load(filename).convert_alpha())
                                self.frameorder = []
                                # print(filename)
                            if filename.endswith(".svg"):
                                svg_surface = load_svg(self.image_url + "/" + filename, self.imagebox.get_width(),
                                                       self.imagebox.get_height())
                                self.images.append(svg_surface)
                                self.frameorder = []
                                # print(filename)
                            if filename == "frameorder.py":
                                url = self.image_url + "/" + filename
                                # print ("url =",url)
                                file = imp.load_source("frameorder.py",
                                                       os.path.join(self.image_url, "frameorder.py"))
                                self.frameorder = file.frameorder
                                self.frame = 0

                    else:
                        if self.image_url:
                            self.frameorder = []
                            # self.imagebox.fill(settings.black)
                            if self.image_url.endswith(".svg"):
                                graphic = load_svg(self.image_url, self.imagebox.get_width(),
                                                   self.imagebox.get_height())
                                self.imagebox.blit(graphic, (0, 0))
                                self.image.blit(self.imagebox, (400, 0))
                            else:
                                graphic = pygame.image.load(self.image_url).convert_alpha()
                                self.image.blit(graphic, (0, 0))



                except:
                    self.image_url = ""

                try:
                    description = self.menu_array[i][3]
                except:
                    description = ""

                if description:
                    self.descriptionbox.fill((0, 0, 0))
                    # description = settings.RobotoB[24].render(self.description[i], True, (settings.bright), (0, 0, 0))
                    word_wrap(self.descriptionbox, description, settings.FreeRobotoR[20])
                    self.image.blit(self.descriptionbox, (settings.description_box_x, settings.description_box_y))

                try:
                    stats = self.menu_array[i][4]
                except:
                    stats = ""

                if stats:
                    stat_offset = 0
                    self.descriptionbox.fill((0, 0, 0))
                    for each in stats:
                        stat_text = settings.RobotoB[30].render(" %s " % each[0], True, (settings.bright),
                                                                (settings.dark))
                        stat_number = settings.RobotoB[30].render(" %s " % each[1], True, (settings.bright),
                                                                  (settings.dark))
                        stat_rect = (0, stat_offset, 350, stat_text.get_size()[1])
                        pygame.draw.rect(self.descriptionbox, (settings.dark), stat_rect)
                        self.descriptionbox.blit(stat_text, (0, stat_offset))
                        self.descriptionbox.blit(stat_number, (350 - stat_number.get_size()[0], stat_offset))
                        stat_offset += stat_text.get_size()[1] + 6

                    self.image.blit(self.descriptionbox, (settings.description_box_x, settings.description_box_y))

            else:
                text = settings.RobotoB[30].render(" %s " % self.menu_array[i][0], True, (settings.bright),
                                                   (0, 0, 0))
                try:
                    number = settings.RobotoB[30].render(" %s " % self.menu_array[i][1], True, (settings.bright),
                                                         (0, 0, 0))
                except:
                    number = None

            if self.prev_selection:
                self.selected = self.prev_selection

            self.image.blit(text, (settings.menu_x, offset))

            if number:
                self.image.blit(number, (settings.menu_x + 330 - number.get_size()[0], offset))
            offset += text.get_size()[1] + 6

        # Handle the up/down arrows for long lists
        if len(self.source_array) > len(self.menu_array):
            if self.top_of_menu != 0:
                self.image.blit(self.arrow_img_up, (20, 6))

        if len(self.source_array) > len(self.menu_array):
            if self.top_of_menu != len(self.source_array) - self.max_items:
                self.image.blit(self.arrow_img_down, (20, 454))

    def render(self, *args, **kwargs):
        if settings.hide_main_menu and settings.hide_main_menu != 3:
            settings.hide_main_menu = 3
            self.image.fill(settings.black)
            self.saved_selection = self.selected

        elif not settings.hide_main_menu:
            if self.saved_selection:
                self.select(self.saved_selection)
                self.saved_selection = None

            self.current_time = time.time()
            self.delta_time = self.current_time - self.prev_time

            if hasattr(self, 'images') and self.images:  # If there is an animation list
                if self.delta_time >= self.animation_time:
                    self.prev_time = self.current_time

                    self.imagebox.fill((0, 0, 0))

                    if self.index >= len(self.images):
                        self.index = 0

                    if self.frameorder:  # Support non-linear frames
                        if self.frame >= len(self.frameorder):
                            self.frame = 0
                        self.index = self.frameorder[self.frame]
                        self.frame += 1

                    self.file = self.images[self.index]
                    self.imagebox.blit(self.file, (0, 0))
                    self.imagebox.fill(settings.bright, None, pygame.BLEND_RGBA_MULT)
                    self.image.blit(self.imagebox, (400, 0))

                    self.index += 1
