import pygame
import game
import pypboy.ui
import settings
from enum import Enum

if settings.GPIO_AVAILABLE:
    import RPi.GPIO as GPIO


class GameState(Enum):
    PASSCODE = -5
    BOOT = -4
    RADIO = -3
    MAP = -2
    DATA = -1
    INV = 0
    STATS = 1


class BaseModule(game.EntityGroup):
    submodules = []
    currentSubmodule = 0

    def __init__(self, boy, *args, **kwargs):
        super(BaseModule, self).__init__()

        # if settings.GPIO_AVAILABLE:
        # GPIO.setup(self.GPIO_LED_ID, GPIO.OUT)
        # GPIO.output(self.GPIO_LED_ID, False)
        self.active = None

        self.pypboy = boy
        self.position = (0, 50)
        #
        self.submenu = pypboy.ui.SubMenu()
        self.submenu.parent = self 
        self.submenu.menu = []
        for mod in self.submodules:
            self.submenu.menu.append(mod.label)
        print(f"BaseModule {self.__class__.__module__}: submodules = " f"{[type(m).__module__ for m in self.submodules]}")
        self.submenu.selected = self.submenu.menu[0]
        self.submenu.position = (73, 93)
        self.add(self.submenu)

        self.action_handlers = {
            "pause": self.handle_pause,
            "resume": self.handle_resume
        }

        self.switch_submodule(0)

        if settings.SOUND_ENABLED:
            self.module_change_sfx = pygame.mixer.Sound('sounds/pipboy/UI_Pipboy_OK.ogg')
            self.module_change_sfx.set_volume(settings.VOLUME)

    def move(self, x, y):
        super(BaseModule, self).move(x, y)
        if hasattr(self, 'active'):
            self.active.move(x, y)

    def switch_submodule(self, module, play_sound=False):
        if module < len(self.submodules):
            if hasattr(self, 'active') and self.active:
                self.active.handle_action("pause")
                self.remove(self.active)
            self.active = self.submodules[module]
            self.active.parent = self
            self._submodule_should_play_sound = play_sound   # set before resume
            self.active.handle_action("resume")
            self.submenu.select(self.submenu.menu[module])
            self.add(self.active)
            self.currentSubmodule = module
        else:
            print("No submodule at %d" % module)

    def handle_action(self, action, value=0):
        if action.startswith("knob_"):
            num = int(action[-1])
            self.switch_submodule(num - 1, play_sound=True)   # user-initiated
        elif action in self.action_handlers:
            self.action_handlers[action]()
        else:
            if hasattr(self, 'active') and self.active:
                self.active.handle_action(action, value)

    def handle_event(self, event):
        if hasattr(self, 'active') and self.active:
            self.active.handle_event(event)

    def handle_pause(self):
        self.paused = True
        self.currentSubmodule = 0
        self.switch_submodule(0)
        # if settings.GPIO_AVAILABLE:
        # GPIO.output(self.GPIO_LED_ID, False)

    def handle_resume(self):
        self.paused = False
        self.currentSubmodule = 0
        self.switch_submodule(0)   # play_sound=False by default → silent cascade
        self._play_module_change_sfx()

    def _play_module_change_sfx(self):
        if not settings.SOUND_ENABLED:
            return
        if not getattr(settings, 'engine_ready', False):
            return
        if getattr(settings, 'suppress_module_change_sfx', False):
            settings.suppress_module_change_sfx = False
            return
        self.module_change_sfx.stop()
        self.module_change_sfx.play()

class SubModule(game.EntityGroup):

    def __init__(self, parent, *args, **kwargs):
        super(SubModule, self).__init__()
        self.parent = parent
        self.paused = True

        self.action_handlers = {
            "pause": self.handle_pause,
            "resume": self.handle_resume
        }

        if settings.SOUND_ENABLED:
            self.submodule_change_sfx = pygame.mixer.Sound('sounds/pipboy/UI_Pipboy_OK.ogg')
            self.submodule_change_sfx.set_volume(settings.VOLUME)

    def handle_action(self, action, value=0):
        if action.startswith("dial_"):
            if hasattr(self, "menu"):
                self.menu.handle_action(action)
        elif action == "select_item":
            if hasattr(self, "menu"):
                self.menu.toggle_selection()
        elif action in self.action_handlers:
            self.action_handlers[action]()

    def handle_event(self, event):
        pass

    def handle_pause(self):
        if self.paused == False:
            self.paused = True

    def handle_resume(self):
        if self.paused == True:
            self.paused = False
            should_play = getattr(self.parent, '_submodule_should_play_sound', False)
            if should_play and settings.SOUND_ENABLED and settings.engine_ready:
                self.submodule_change_sfx.stop()
                self.submodule_change_sfx.play()
