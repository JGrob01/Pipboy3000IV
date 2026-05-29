import os
import glob

import pygame

from src.screen import Screen


class FrameScreen(Screen):
    """Plays a sequence of image frames, then transitions to the next screen."""

    def __init__(self, app, frames_dir, fps=15,
                 repeat_section=None, repeat_count=0, next_screen=None):
        super().__init__(app)
        self.next_screen = next_screen
        self.frame_duration = 1.0 / fps
        self.elapsed = 0.0

        self.frame_paths = sorted(
            glob.glob(os.path.join(frames_dir, "*.png"))
        )
        if not self.frame_paths:
            raise FileNotFoundError(f"No frames found in {frames_dir}")

        self.index = 0
        self.repeat_section = repeat_section
        self.repeat_count = repeat_count
        self._repeats_done = 0
        self._current_frame = None
        self._cached_index = -1

    def update(self, dt):
        self.elapsed += dt
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.index += 1

            if self.repeat_section is not None:
                if (self.index > self.repeat_section[1]
                        and self._repeats_done < self.repeat_count):
                    self._repeats_done += 1
                    self.index = self.repeat_section[0]

            if self.index >= len(self.frame_paths):
                if self.next_screen is not None:
                    self.app.change_screen(self.next_screen)
                else:
                    self.index = len(self.frame_paths) - 1
                return

    def draw(self, surface):
        if self._cached_index != self.index:
            self._current_frame = pygame.image.load(
                self.frame_paths[self.index]
            ).convert_alpha()
            self._cached_index = self.index
        surface.blit(self._current_frame, (0, 0))