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
    REPEAT_SECTION = (34, 57)
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
        self.boot.line = 0
        self.boot.char = 0
        self.boot.y = 0
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
    PHASE_PIP = 3
    PHASE_FRAMES = 1
    PHASE_DONE = 2

     # -------- Timing knobs (seconds) --------
    CHAR_DELAY = 0.008
    BLINK_DELAY = 0.05
    LINE_PAUSE = 0.0
    HOLD_AFTER_TYPING = 0.0
    SCROLL_PX_PER_SEC = 750   # final scroll-up speed
    SCROLL_DISTANCE = 500     # how far to scroll before advancing

    LINE_HEIGHT = 24
    FONT = None  # set lazily so settings is fully loaded

    def __init__(self, scroll_duration=6.0, frame_fps=31,
                 repeat_section=None, repeat_count=0):
        super(Boot, self).__init__()
        
        self.image = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self.image.fill(settings.black)
        self.rect = self.image.get_rect()
        
        self.text_array = [
            "▯", "▯", "▯", "~", "~", "~", "~", "~",
            "▯", "▯", "▯", "~", "~", "~", "~", "~",
            "▯", "▯", "▯", "~", "~", "~", "~", "~",
            "▯", "▯", "▯", "~", "~", "~", "~", "~",
            "▯", "▯", "▯", "~", "~", "~", "~", "~",
            "▯", "▯", "▯", "~", "~", "~", "~", "~",
            "*************** PIP-05 (R) V7 .1.0.8 ************** ",
            " ",
            " ",
            " ",
            " ",
            " COPYRIGHT 2075 ROBCO(R) ",
            " LOADER VI.1 ",
            " EXEC VERSION 41.10 ",
            " 264k RAM SYSTEM ",
            " 38911 BYTES FREE ",
            " NO HOLOTAPE FOUND ",
            " LOAD ROM(1): DEITRIX 303 ",
            "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@",
            "^", "^", "^", "^", "^", "^", "^", "^", "^", "^", "^", "^",
            "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@",
            "^", "^", "^", "^", "^", "^", "^", "^", "^", "^", "^", "^",
            "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@",
            "^", "^", "^", "^", "^", "^", "^", "^", "^", "^", "^", "^",
            "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@",
        ]
        
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
        
        # Preload all frames into memory once
        self.frames = []
        for path in self.frame_paths:
            self.frames.append(pygame.image.load(path).convert_alpha())
        print(f"Boot: preloaded {len(self.frames)} frames")

        # State
        self.phase = self.PHASE_SCROLL
        self.phase_start = None
        self.prev_time = 0.0

        # Frame cache so we don't reload from disk every render
        self._frame_index = -1
        self._frame_surface = None

        self.reset()

    def reset(self):
        self.image.fill(settings.black)
        self.rect[1] = 0
        self.top = 0
        self.line = 0
        self.char = 0
        self.y = 0
        self.pipphase = "typing"
        self.next_tick = time.time()
        self.hold_started = None
        self.scroll_started = None
        self._scroll_prev_time = None
        self._char_budget = 0.0
        self._char_prev_time = None
        
        self.phase = self.PHASE_SCROLL
        self.phase_start = None
        self.prev_time = 0.0
        self._frame_index = -1
        self._frame_surface = None
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
            self.phase = self.PHASE_PIP
            self.phase_start = now
            self.prev_time = now

    def _render_pip(self, now):
        if self.pipphase == "typing":
            # Accumulate "characters owed" based on real time
            if not hasattr(self, '_char_budget'):
                self._char_budget = 0.0
                self._char_prev_time = now
            if self._char_prev_time == None:
                self._char_prev_time = now
            dt = now - self._char_prev_time
            self._char_prev_time = now
            if dt > 0.1:
                dt = 0.1   # clamp to avoid huge catch-up after a stall
            self._char_budget += dt * 60

            safety = 600
            while self._char_budget >= 1.0 and self.pipphase == "typing" and safety > 0:
                self._advance_typing(now)
                self._char_budget -= 1.0
                safety -= 1

        elif self.pipphase == "hold":
            if now - self.hold_started >= self.HOLD_AFTER_TYPING:
                self.pipphase = "scroll"
                self.scroll_started = now
                self._scroll_prev_time = now

        elif self.pipphase == "scroll":
            dt = now - self._scroll_prev_time
            self._scroll_prev_time = now
            self.top -= self.SCROLL_PX_PER_SEC * dt
            self.rect[1] = round(self.top)
            if self.top <= -self.SCROLL_DISTANCE:
                self.pipphase = "done"
                self.top = 0
                self.rect[1] = 0
                self.image.fill(settings.black)
                self.phase = self.PHASE_FRAMES
                self.phase_start = now
                self.prev_time = now
                self._render_frames(now)

    def _blit_line(self, text, pos):
        surf = settings.TechMono[26].render(text, True, settings.bright, (0, 0, 0))
        self.image.blit(surf, pos)

    def _advance_typing(self, now):
        """Run one typing step. Returns True if we made progress."""
        if self.line >= len(self.text_array):
            self.pipphase = "hold"
            self.hold_started = now
            return False

        text = self.text_array[self.line]

        # ---- special one-shot tokens (top-of-screen blinkers) ----
        if text == "▯":
            self._blit_line("▯", (0, 0))
            self.line += 1
            self.next_tick = now + self.BLINK_DELAY
            return True
        if text == "~":
            self._blit_line(" ", (0, 0))
            self.line += 1
            self.next_tick = now + self.BLINK_DELAY
            return True
        if text == "@":
            self._blit_line("▯", (355, 264))
            self.line += 1
            self.next_tick = now + self.BLINK_DELAY
            return True
        if text == "^":
            self._blit_line(" ", (355, 264))
            self.line += 1
            self.next_tick = now + self.BLINK_DELAY
            return True
        if text == "/":
            self._blit_line(" ", (0, 0))
            self.line += 1
            self.next_tick = now + self.BLINK_DELAY
            return True

        # ---- regular line: type one character at a time ----
        if self.char < len(text):
            partial = text[:self.char + 1] + "▯"
            self._blit_line(partial, (0, self.y))
            self.char += 1
            return True

        # Wipe the line area (cursor column included) before the clean paint
        char_w = settings.TechMono[26].size(" ")[0]
        wipe_w = (len(text) + 2) * char_w
        wipe_rect = pygame.Rect(0, self.y, wipe_w, self.LINE_HEIGHT)
        self.image.fill((0, 0, 0), wipe_rect)
        self._blit_line(text, (0, self.y))
        self.y += self.LINE_HEIGHT
        self.char = 0
        self.line += 1
        return True

    def _render_frames(self, now):
        print(f"FRAMES: paths={len(self.frame_paths)} idx={self._frame_index} elapsed_frames={self._frames_elapsed}")
        
        if self.rect[1] != 0:
            self.rect[1] = 0

        if not self.frames:
            self._finish()
            return

        elapsed = now - self.phase_start
        target_count = int(elapsed / self.frame_duration)

        while self._frames_elapsed < target_count:
            self._frames_elapsed += 1
            next_index = self._frame_index + 1

            if self.repeat_section is not None:
                start, end = self.repeat_section
                if (next_index > end
                        and self._repeats_done < self.repeat_count):
                    self._repeats_done += 1
                    next_index = start

            if next_index >= len(self.frames):
                self._finish()
                return

            self._frame_index = next_index
            self._frame_surface = self.frames[next_index]
            self.image.fill(settings.black)
            self.image.blit(self._frame_surface, (0, 0))

        if self._frame_index == -1:
            self._frame_index = 0
            self._frame_surface = self.frames[0]
            self.image.fill(settings.black)
            self.image.blit(self._frame_surface, (0, 0))

        # First entry into frames phase: paint frame 0 immediately
        if self._frame_index == -1:
            self._frame_index = 0
            self._frame_surface = pygame.image.load(
                self.frame_paths[0]
            ).convert_alpha()
            print(f"  first-entry loaded frame 0 size={self._frame_surface.get_size()}")
            self.image.fill(settings.black) 
            self.image.blit(self._frame_surface, (0, 0))

    def _finish(self):
        if self.phase == self.PHASE_DONE:
            return
        self.phase = self.PHASE_DONE
        self.frames = []
        self._frame_surface = None
        self.text_surf = None
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
        elif self.phase == self.PHASE_PIP:
            self._render_pip(now)
        elif self.phase == self.PHASE_FRAMES:
            self._render_frames(now)
        
        # Debug — once per second, log state
        if not hasattr(self, '_dbg_last') or now - self._dbg_last > 1.0:
            self._dbg_last = now
            print(f"BOOT: phase={self.phase} image_size={self.image.get_size()} rect={self.rect}")