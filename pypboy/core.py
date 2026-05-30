import time

import pygame
import game
import pypboy.ui
import settings
from math import atan2, pi, degrees

from pypboy.modules import data
from pypboy.modules import items
from pypboy.modules import stats
from pypboy.modules import boot
from pypboy.modules import map
from pypboy.modules import radio
from pypboy.modules import passcode

if settings.GPIO_AVAILABLE:
    import RPi.GPIO as GPIO


class Pypboy(game.core.Engine):
    currentModule = 0
    prev_fps_time = 0
    SCROLL_PAUSE_BEFORE = 0.0
    SCROLL_UP_DURATION = 0.5
    SCROLL_BACK_DURATION = 0.25
    SCROLL_WRAP_COUNT = 6

    def __init__(self, *args, **kwargs):
        # Support rescaling
        # if hasattr(settings, 'OUTPUT_WIDTH') and hasattr(settings, 'OUTPUT_HEIGHT'):
        #     self.rescale = False

        # Initialize modules
        super(Pypboy, self).__init__(*args, **kwargs)
        self.init_persitant()
        self.init_modules()

        self.gpio_actions = {}
        # if settings.GPIO_AVAILABLE:
        # self.init_gpio_controls()

        self.prev_fps_time = 0
        
        # Boot-to-stats CRT scroll-in transition
        self._scroll_active = False
        self._scroll_pending = False
        self._scroll_elapsed = 0.0
        self._scroll_prev_time = 0.0
        self._scroll_surface = None
        self._prev_glitch = settings.glitch
        self._scroll_target_module = None

    def init_persitant(self):
        # self.background = pygame.image.load('images/background.png')
        overlay = pypboy.ui.Overlay()
        self.root_persitant.add(overlay)
        scanlines = pypboy.ui.Scanlines()
        self.root_persitant.add(scanlines)
        pass

    def init_modules(self):
        self.modules = {
            "passcode": passcode.Module(self),
            "boot": boot.Module(self),            
            "stats": stats.Module(self),
            "data": data.Module(self),
            "items": items.Module(self),
            "radio": radio.Module(self),
            "map": map.Module(self)
        }
        self.switch_module(settings.STARTER_MODULE)  # Set the start screen

    def init_gpio_controls(self):
        for pin in settings.gpio_actions.keys():
            print("Initialing pin %s as action '%s'" % (pin, settings.gpio_actions[pin]))
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.gpio_actions[pin] = settings.gpio_actions[pin]

    def check_gpio_input(self):
        if not settings.GPIO_AVAILABLE:
            return
        for pin in self.gpio_actions.keys():
            if GPIO.input(pin) == False:
                self.handle_action(self.gpio_actions[pin])

    # def render(self):
    #     super(Pypboy, self).render()
    #     if hasattr(self, 'active'):
    #         self.active.render()

    def switch_module(self, module):
        # if not settings.hide_top_menu:
        if module in self.modules:
            if hasattr(self, 'active'):
                self.active.handle_action("pause")
                self.remove(self.active)
            self.active = self.modules[module]
            self.active.parent = self
            self.active.handle_action("resume")
            self.add(self.active)
        else:
            print("Module '%s' not implemented." % module)

    def handle_action(self, action):
        if action.startswith('module_'):
            self.switch_module(action[7:])
        else:
            if hasattr(self, 'active'):
                self.active.handle_action(action)

    def handle_event(self, event):
        if self._scroll_active:
            # Ignore input during the transition
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                return
            
        if event.type == pygame.KEYDOWN:  # Some key has been pressed
            # Persistent Events:
            if event.key == pygame.K_ESCAPE:  # ESC
                self.running = False

            elif event.key == pygame.K_PAGEUP:  # Volume up
                settings.radio.handle_radio_event(event)
            elif event.key == pygame.K_PAGEDOWN:  # Volume down
                settings.radio.handle_radio_event(event)
            elif event.key == pygame.K_END:  # Next Song
                settings.radio.handle_radio_event(event)
            elif event.key == pygame.K_HOME:  # Prev Song
                settings.radio.handle_radio_event(event)
            elif event.key == pygame.K_DELETE:
                settings.radio.handle_radio_event(event)
            elif event.key == pygame.K_INSERT:
                settings.radio.handle_radio_event(event)
            else:
                if event.key in settings.ACTIONS:  # Check action based on key in settings
                    self.handle_action(settings.ACTIONS[event.key])

        elif event.type == pygame.QUIT:
            self.running = False

        elif event.type == settings.EVENTS['SONG_END']:
            if settings.SOUND_ENABLED:
                if hasattr(settings, 'radio'):
                    settings.radio.handle_radio_event(event)
        elif event.type == settings.EVENTS['PLAYPAUSE']:
            if settings.SOUND_ENABLED:
                if hasattr(settings, 'radio'):
                    settings.radio.handle_radio_event(event)
        else:
            if hasattr(self, 'active'):
                self.active.handle_event(event)

    def inRange(self, angle, init, end):
        return (angle >= init) and (angle < end)

    def run(self):
        self.running = True
        while self.running:
            self.check_gpio_input()
            for event in pygame.event.get():
                self.handle_event(event)
                if hasattr(self, 'active'):
                    self.active.handle_event(event)

            # slow code debugger
            # debug_time = time.time()

            self.render()
            #
            # time_past = time.time() - debug_time
            # if time_past:
            #     max_fps = int(1 / time_past)
            #     print("self.render took:", time_past, "max fps:", max_fps)

        try:
            pygame.mixer.quit()
        except Exception as e:
            print(e)

    def render(self):
        super(Pypboy, self).render()

        # Rising edge of settings.glitch: arm the scroll, remember current module
        if settings.glitch and not self._prev_glitch and not self._scroll_active:
            self._scroll_pending = "wait_for_switch"
            self._scroll_target_module = self.active
            settings.glitch = False
        self._prev_glitch = settings.glitch

        # Snapshot once the active module has changed AND we've rendered since
        if (self._scroll_pending == "wait_for_switch"
                and self.active is not self._scroll_target_module):
            self._scroll_pending = "snapshot_next"
            self._scroll_target_module = None
        elif self._scroll_pending == "snapshot_next" and not self._scroll_active:
            self._begin_scroll()
            self._scroll_pending = False

        if self._scroll_active:
            self._render_scroll()

    def _begin_scroll(self):
        #print("SCROLL BEGIN, snapshotting active module:", self.active.__class__.__module__)
        self._scroll_surface = self.screen.copy()
        self._scroll_active = True
        self._scroll_elapsed = 0.0
        self._scroll_prev_time = time.time()

    def _scroll_offset(self):
        t = self._scroll_elapsed - self.SCROLL_PAUSE_BEFORE
        screen_h = settings.HEIGHT
        if t <= 0:
            return screen_h
        if t < self.SCROLL_UP_DURATION:
            p = t / self.SCROLL_UP_DURATION
            start = screen_h
            end = -self.SCROLL_WRAP_COUNT * screen_h
            return start + (end - start) * p
        t2 = t - self.SCROLL_UP_DURATION
        if t2 < self.SCROLL_BACK_DURATION:
            p = t2 / self.SCROLL_BACK_DURATION
            p = 1 - (1 - p) ** 2   # ease-out
            start = -self.SCROLL_WRAP_COUNT * screen_h
            end = 0
            return start + (end - start) * p
        return 0

    def _render_scroll(self):
        #print(f"SCROLL elapsed={self._scroll_elapsed:.3f} offset={self._scroll_offset():.1f}")
        now = time.time()
        dt = now - self._scroll_prev_time
        self._scroll_prev_time = now
        # Clamp dt so a slow frame doesn't skip the animation
        if dt > 0.05:
            dt = 0.05
        self._scroll_elapsed += dt

        total = (self.SCROLL_PAUSE_BEFORE
                 + self.SCROLL_UP_DURATION
                 + self.SCROLL_BACK_DURATION)

        if self._scroll_elapsed >= total:
            self._scroll_active = False
            self._scroll_surface = None
            return

        # Tile the snapshot with the scrolling offset
        self.screen.fill(settings.black)
        offset = int(self._scroll_offset())
        screen_h = settings.HEIGHT
        y = offset % screen_h
        if y > 0:
            y -= screen_h
        while y < screen_h:
            self.screen.blit(self._scroll_surface, (0, y))
            y += screen_h

        pygame.display.flip()