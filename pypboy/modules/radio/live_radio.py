import pypboy
import settings
import pygame
import os
import importlib
import glob
import time
import game
from collections import deque
import mutagen
import random
import configparser
import sys
import threading
import numpy as np

from pypboy.modules.data import entities
import pypboy.data

song = None
start_pos = 0
waveform = []
waveform_length = 0
song_length = 0
song_fileload = None

def generate_waveform():
    global waveform, waveform_length, song, song_fileload

    while True:
        if song and song.endswith(".ogg") and song_fileload and waveform == []:
            print("Generating waveform for", song)
            amplitude = pygame.sndarray.array(song_fileload)  # Load the sound file
            amplitude = amplitude.flatten()  # Load the sound file)

            # amplitude = amplitude[:, 0] + amplitude[:, 1]
            amplitude = amplitude[::settings.frame_skip]

            # scale the amplitude to fit in the frame height and translate it to height/2(central line)
            amplitude = amplitude.astype('float64')

            # Normalised [0,255] as integer: don't forget the parenthesis before astype(int)
            amplitude = (250 * (amplitude - np.min(amplitude)) / np.ptp(amplitude)).astype(int)

            waveform = [int(250 / 2)] * 250 + list(amplitude)
            waveform_length = len(waveform)
            song_fileload = None
        else:
            time.sleep(0.1)

waveform_thread = threading.Thread(target=generate_waveform)
waveform_thread.daemon = True
waveform_thread.start()

class Module(pypboy.SubModule):
    label = ""

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        self.audiofolders = 'sounds/radio/'
        self.stations = []
        self.station_menu = []
        self.station_data = self.get_station_data()
        self.station_meta_data_file = None
        self.station_files = []
        self.station_lengths = []

        self.grid = Grid()
        self.grid.rect[0] = 400
        self.grid.rect[1] = 180
        self.add(self.grid)

        self.animation = Animation()
        self.animation.rect[0] = 400
        self.animation.rect[1] = 190
        self.add(self.animation)

        for station in self.station_data:
            station_folder = station[1] + "/"
            station_name = station[0]
            self.station_menu.append([station_name])
            self.stations.append(RadioClass(station_name, station_folder, station))

        for station in self.stations:
            self.add(station)
        self.active_station = None
        settings.radio = self

        stationCallbacks = []
        for i, station in enumerate(self.stations):
            stationCallbacks.append(lambda i=i: self.select_station(i))

        self.topmenu = pypboy.ui.TopMenu()
        self.add(self.topmenu)
        self.topmenu.label = "RADIO"
        self.topmenu.title = settings.MODULE_TEXT

        self.menu = pypboy.ui.Menu(self.station_menu, stationCallbacks, settings.STATION)
        self.menu.rect[0] = settings.menu_x
        self.menu.rect[1] = settings.menu_y
        self.add(self.menu)
        self.menu.select(settings.STATION)

        self.footer = pypboy.ui.Footer(settings.FOOTER_RADIO)
        self.footer.rect[0] = settings.footer_x
        self.footer.rect[1] = settings.footer_y
        self.add(self.footer)

    def select_station(self, station):
        if hasattr(self, 'active_station') and self.active_station:
            self.active_station.stop()
        self.active_station = self.stations[station]
        settings.STATION = station
        self.active_station.tune_in()

    def handle_radio_event(self, event):
        if event.type == settings.EVENTS['SONG_END']:
            if hasattr(self, 'active_station') and self.active_station:
                # Song ended naturally; advance schedule by one track
                self.active_station.advance_naturally()

    # ---- Station data loading ----

    def get_station_data(self):
        folders = []
        stations = []
        self.station_name = None
        self.station_ordered = True

        if not os.path.isdir(self.audiofolders):
            print(f"Radio folder '{self.audiofolders}' missing — skipping station load")
            return stations

        for f in sorted(os.listdir(self.audiofolders)):
            if not f.endswith("/"):
                folders.append(self.audiofolders + f)

        for folder in folders:
            config = configparser.ConfigParser()

            folder_name = os.path.basename(folder)
            if len(glob.glob(folder + "/*.ogg")) == 0:
                print("No .ogg files in:", folder)
                continue

            song_data = self.load_files(folder)
            station_files = song_data[0]
            station_lengths = song_data[1]

            self.station_meta_data_file = ("./" + folder + "/" + "station.ini")
            station_name = folder_name
            station_ordered = True

            try:
                if os.path.exists(self.station_meta_data_file):
                    config.read(self.station_meta_data_file, encoding=None)
                    station_name = config.get('metadata', 'station_name',
                                              fallback=folder_name)
                    station_ordered = config.getboolean('metadata', 'ordered',
                                                        fallback=True)
            except Exception as e:
                print(f"Error reading {self.station_meta_data_file}: {e}")

            if not station_ordered:
                # Deterministic shuffle keyed by station name —
                # same order every session, every install
                seed = hash(station_name) & 0xFFFFFFFF
                rng = random.Random(seed)
                paired = list(zip(station_files, station_lengths))
                rng.shuffle(paired)
                station_files, station_lengths = zip(*paired)
                station_files = list(station_files)
                station_lengths = list(station_lengths)

            total_length = sum(station_lengths)
            station_data = (station_name, folder, station_files,
                            station_ordered, station_lengths, total_length)
            stations.append(station_data)

        return stations

    def load_files(self, folder):
        files = []
        song_lengths = []
        for file in sorted(os.listdir(folder)):
            if file.endswith(".ogg"):
                path = "./" + folder + "/" + file
                files.append(path)
                song_lengths.append(mutagen.File(path).info.length)
        return [files, song_lengths]


class RadioStation(game.Entity):
    """A station playing on a global wall-clock schedule.

    At any moment, the position within the station is determined by
    (now - BROADCAST_EPOCH) % total_length. Switching stations recomputes
    the position; switching away and back jumps to where the schedule
    says you should be.
    """

    STATES = {
        'stopped': 0,
        'playing': 1,
        'paused': 2,
    }

    def __init__(self, *args, **kwargs):
        super(RadioStation, self).__init__((10, 10), *args, **kwargs)
        self.state = self.STATES['stopped']
        self.filename = None
        self.static = pygame.mixer.Sound(
            "sounds/pipboy/Radio/UI_Pipboy_Radio_StaticBackground_LP.ogg"
        )
        pygame.mixer.music.set_endevent(settings.EVENTS['SONG_END'])

    # ---- Scheduling ----

    def _schedule_position(self):
        """Return (track_index, offset_within_track) based on wall-clock."""
        elapsed = (time.time() - settings.BROADCAST_EPOCH) % self.total_length
        cumulative = 0.0
        for i, length in enumerate(self.song_lengths):
            if cumulative + length > elapsed:
                return i, elapsed - cumulative
            cumulative += length
        # Fallback (shouldn't reach here due to modulo)
        return 0, 0.0

    def tune_in(self):
        """User selected this station — jump to scheduled position."""
        global song, start_pos, waveform, song_length, waveform_length, song_fileload

        if not settings.SOUND_ENABLED or not self.files:
            return

        # Silence station sentinel
        if self.files[0].endswith("Silence.ogg"):
            settings.AMPLITUDE = []
            song = None
            start_pos = 0
            waveform = []
            waveform_length = 0
            settings.FOOTER_RADIO[0] = ""
            self.stop()
            return

        track_index, offset = self._schedule_position()
        self.static.play()
        self._play_track(track_index, offset)

    def advance_naturally(self):
        """Pygame fired SONG_END — schedule says move to next track at 0."""
        if not settings.SOUND_ENABLED or not self.files:
            return
        # Re-anchor from wall clock in case the song length we had was slightly
        # off and we've drifted. Cheap and avoids accumulated error over hours.
        track_index, offset = self._schedule_position()
        self._play_track(track_index, offset)

    def _play_track(self, track_index, offset):
        global song, song_length, waveform, waveform_length, song_fileload

        self.filename = self.files[track_index]
        song = self.filename
        settings.CURRENT_SONG = song
        song_length = self.song_lengths[track_index]

        # Trigger waveform generation
        song_fileload = pygame.mixer.Sound(song)
        waveform = []
        waveform_length = 0

        # Metadata for footer
        try:
            meta = mutagen.File(self.filename, easy=True)
            artist = str(meta['artist']).strip("['").strip("']")
            title = str(meta['title']).strip("['").strip("']")
        except Exception:
            artist = ""
            title = ""
        settings.FOOTER_RADIO[0] = artist + " / " + title

        pygame.mixer.music.load(song)
        self.static.stop()
        try:
            pygame.mixer.music.play(0, offset)
        except Exception:
            pygame.mixer.music.play(0, 0)
        self.state = self.STATES['playing']

    def stop(self):
        if settings.SOUND_ENABLED:
            self.state = self.STATES['stopped']
            pygame.mixer.music.stop()
            settings.ACTIVE_SONG = None

    def __le__(self, other):
        if type(other) is not RadioStation:
            return 0
        return self.label <= other.label

    def __ge__(self, other):
        if type(other) is not RadioStation:
            return 0
        return self.label >= other.label


class RadioClass(RadioStation):
    def __init__(self, station_name, station_folder, station_data, *args, **kwargs):
        self.label = station_name
        self.directory = station_folder
        self.files = list(station_data[2])
        self.song_lengths = list(station_data[4])
        self.total_length = station_data[5]
        super(RadioClass, self).__init__(*args, **kwargs)


class Animation(game.Entity):

    def __init__(self):
        super(Animation, self).__init__()
        self.width, self.height = 250, 250
        self.center = [self.width / 2, self.height / 2]
        self.image = pygame.Surface((self.width, self.height))
        self.animation_time = 1 / settings.waveform_fps
        self.prev_time = 0
        self.index = 0
        self.prev_song = None
        self.current_time = 0
        self.delta_time = 0
        self.max_length = 0

    def expand(self, oldvalue, oldmin, oldmax, newmin, newmax):
        oldRange = oldmax - oldmin
        newRange = newmax - newmin
        return ((oldvalue - oldmin) * newRange / oldRange) + newmin

    def render(self, *args, **kwargs):
        global waveform, waveform_length, song, song_length

        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_time

        if self.delta_time >= self.animation_time:
            self.prev_time = self.current_time
            self.image.fill((0, 0, 0))

            if not song:
                pygame.draw.line(self.image, settings.bright,
                                 [0, self.height / 2],
                                 [self.width, self.height / 2], 2)
                self.prev_song = 0
                return

            if song != self.prev_song:
                self.prev_song = song
                try:
                    song_length = mutagen.File(song).info.length
                except Exception:
                    song_length = 0
                self.max_length = int(song_length * 1000)

            if waveform:
                song_time = pygame.mixer.music.get_pos()
                self.index = int(
                    self.expand(song_time, 0, self.max_length, 0, waveform_length)
                )
                if self.index >= waveform_length:
                    self.index = 0

                prev_x, prev_y = 0, waveform[self.index]
                for x, y in enumerate(
                    waveform[self.index + 1:self.index + 1 + self.width][::1]
                ):
                    pygame.draw.line(self.image, settings.bright,
                                     [prev_x, prev_y], [x, y], 2)
                    prev_x, prev_y = x, y
            else:
                pygame.draw.line(self.image, settings.bright,
                                 [0, self.height / 2],
                                 [self.width, self.height / 2], 2)
                settings.FreeRobotoB[18].render_to(
                    self.image, (53, 106),
                    "Locking onto signal...", settings.dim
                )


class Grid(game.Entity):

    def __init__(self):
        super(Grid, self).__init__()
        self.image = pygame.Surface((270, 270))
        self.image.fill((0, 0, 0))
        long_line = 14
        long_lines = 10
        short_line = 9
        short_lines = long_lines * 3
        line_start = 0
        bottom = self.image.get_rect().bottom
        right = self.image.get_rect().right

        pygame.draw.lines(self.image, settings.light, False,
                          [(0, 268), (268, 268), (268, 0)], 3)

        line_x = int(self.image.get_rect().height / long_lines)
        while long_lines >= 1:
            line_start += line_x
            pygame.draw.line(self.image, settings.light,
                             (line_start, bottom),
                             (line_start, bottom - long_line), 2)
            pygame.draw.line(self.image, settings.light,
                             (right, line_start),
                             (right - long_line, line_start), 2)
            long_lines -= 1

        line_start = 0
        line_x = int(self.image.get_rect().height / short_lines)
        while short_lines > 2:
            line_start += line_x
            pygame.draw.line(self.image, settings.light,
                             (line_start, bottom),
                             (line_start, bottom - short_line), 2)
            pygame.draw.line(self.image, settings.light,
                             (right, line_start),
                             (right - short_line, line_start), 2)
            short_lines -= 1