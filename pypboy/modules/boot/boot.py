import os
import glob
import time

import pygame

import pypboy
import game
import settings

import cProfile
import re


# Original EFI boot text from boot_text.py
BOOT_TEXT = ("* 1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4 "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0 "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4 "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 "
            "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
            "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
            "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
            "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
            "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
            "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
            "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
            "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
            "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
            "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
            "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
            "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 END"
        )


def _word_wrap_into(surface, text, font, color):
    """Render `text` word-wrapped into `surface` using a freetype font."""
    font.origin = True
    words = text.split(' ')
    width, _ = surface.get_size()
    line_spacing = font.get_sized_height()
    x, y = 0, line_spacing
    space = font.get_rect(' ')
    for word in words:
        bounds = font.get_rect(word)
        if x + bounds.width + bounds.x >= width:
            x, y = 0, y + line_spacing
        font.render_to(surface, (x, y), word, color, None, 1)
        x += bounds.width + space.width
    return y  # total height drawn


class Module(pypboy.SubModule):
    label = ""

    SCROLL_DURATION = 4.1333  # seconds for the text to scroll across the screen
    FRAME_FPS = 31
    REPEAT_SECTION = (223, 246)
    REPEAT_COUNT = 4

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        self.boot = Boot(
            scroll_duration=self.SCROLL_DURATION,
            frame_fps=self.FRAME_FPS,
            repeat_section=self.REPEAT_SECTION,
            repeat_count=self.REPEAT_COUNT,
        )
        self.boot.rect[0] = 0
        self.boot.rect[1] = 0
        self.add(self.boot)

        self._sound_playing = False
        self.boot.parent_module = self
        self._finished = False

        self.sound = None
        if settings.SOUND_ENABLED and settings.STARTER_MODULE == "boot":
            sound_path = 'sounds/pipboy/BootSequence/UI_PipBoy_BootSequence.wav'
            if os.path.exists(sound_path):
                self.sound = pygame.mixer.Sound(sound_path)
                self.sound.set_volume(settings.VOLUME)
            else:
                print("Boot sound not found:", sound_path)

    def handle_resume(self):
        if self._finished:
            # Boot already completed this session; don't restart sound or animation
            super(Module, self).handle_resume()
            return
        self.boot.reset()
        if self.sound and not self._sound_playing:
            self.sound.play()
            self._sound_playing = True
        super(Module, self).handle_resume()
        

    def handle_pause(self):
        if self.sound and not self._finished:
            self.sound.stop()
            self._sound_playing = False
        super(Module, self).handle_pause()


class Boot(game.Entity):
    """
    Two-phase boot sequence:
      PHASE_SCROLL  - tall text surface scrolls from below screen to above it
      PHASE_FRAMES  - sequence of PNG frames plays once at FRAME_FPS, then exit
    """

    PHASE_SCROLL = 0
    PHASE_FRAMES = 1
    PHASE_DONE = 2

    def __init__(self, scroll_duration=6.0, frame_fps=31,
                 repeat_section=None, repeat_count=0):
        super(Boot, self).__init__()
        self.image = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self.image.fill(settings.black)

        self.scroll_duration = scroll_duration
        self.frame_duration = 1.0 / frame_fps
        self.repeat_section = repeat_section
        self.repeat_count = repeat_count

        # --- Pre-render the scrolling text into a tall transparent surface ---
        # Make the text surface much taller than the screen so wrapping has room.
        # Height is generous; the actual content height is measured after render.
        scratch_h = 4000
        text_surface = pygame.Surface(
            (settings.WIDTH, scratch_h), pygame.SRCALPHA
        )
        content_h = _word_wrap_into(
            text_surface, BOOT_TEXT, settings.FreeTechMono[18], settings.bright
        )
        # Crop to actual content height (plus a little padding).
        self.text_h = min(scratch_h, content_h + 40)
        self.text_surf = pygame.Surface(
            (settings.WIDTH, self.text_h), pygame.SRCALPHA
        )
        self.text_surf.blit(text_surface, (0, 0))

        # --- Load frames ---
        frames_dir = os.path.join("images", "boot")
        self.frame_paths = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
        if not self.frame_paths:
            print("WARNING: no PNG frames found in", frames_dir)

        # State
        self.phase = self.PHASE_SCROLL
        self.phase_start = None
        self.prev_time = 0.0

        # Frame cache so we don't reload from disk every render
        self._frame_index = -1
        self._frame_surface = None

    def reset(self):
        self.phase = self.PHASE_SCROLL
        self.phase_start = None
        self.prev_time = 0.0
        self._frame_index = -1
        self._frame_surface = None
        self.image.fill(settings.black)
        self._repeats_done = 0
        self._frames_elapsed = 0

    # ----- Phase logic -----

    def _render_scroll(self, now):
        elapsed = now - self.phase_start
        t = min(elapsed / self.scroll_duration, 1.0)

        start_y = settings.HEIGHT
        end_y = -self.text_h
        y = int(start_y + (end_y - start_y) * t)

        self.image.fill(settings.black)
        self.image.blit(self.text_surf, (0, y))

        if elapsed >= self.scroll_duration:
            self.phase = self.PHASE_FRAMES
            self.phase_start = now
            self.prev_time = now

    def _render_frames(self, now):
        if not self.frame_paths:
            self._finish()
            return

        # Advance one frame at a time at the target rate. Using a counter
        # rather than int(elapsed / frame_duration) so repeat logic works.
        elapsed = now - self.phase_start
        target_count = int(elapsed / self.frame_duration)

        while self._frames_elapsed < target_count:
            self._frames_elapsed += 1
            next_index = self._frame_index + 1

            # Handle repeat section
            if self.repeat_section is not None:
                start, end = self.repeat_section
                if (next_index > end
                        and self._repeats_done < self.repeat_count):
                    self._repeats_done += 1
                    next_index = start

            if next_index >= len(self.frame_paths):
                self._finish()
                return

            self._frame_index = next_index
            self._frame_surface = pygame.image.load(
                self.frame_paths[next_index]
            ).convert_alpha()
            self.image.fill(settings.black) 
            # Only blit when the frame actually changes — no fill, no flash
            self.image.blit(self._frame_surface, (0, 0))

        # First entry into frames phase: paint frame 0 immediately
        if self._frame_index == -1:
            self._frame_index = 0
            self._frame_surface = pygame.image.load(
                self.frame_paths[0]
            ).convert_alpha()
            self.image.fill(settings.black) 
            self.image.blit(self._frame_surface, (0, 0))

    def _finish(self):
        if self.phase == self.PHASE_DONE:
            return
        self.phase = self.PHASE_DONE
        self.image.fill(settings.black)
        if hasattr(self, 'parent_module'):
            self.parent_module._finished = True
            # Don't stop the sound; let it play through the transition
            self.parent_module._sound_playing = False
        settings.glitch = True
        settings.suppress_module_change_sfx = True   # <-- add
        pygame.event.post(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1)
        )

    # ----- Render -----

    def render(self, *args, **kwargs):
        now = time.time()

        if self.phase_start is None:
            self.phase_start = now
            self.prev_time = now

        if self.phase == self.PHASE_SCROLL:
            self._render_scroll(now)
        elif self.phase == self.PHASE_FRAMES:
            self._render_frames(now)
        # PHASE_DONE: do nothing; the engine will switch modules on the F1 event