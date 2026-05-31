# pypboy/rfid.py
import json
import os
import threading
import time

import pygame
import settings

try:
    import board
    import busio
    import digitalio
    from adafruit_pn532.spi import PN532_SPI
    PN532_AVAILABLE = True
except ImportError as e:
    print(f"[rfid] adafruit_pn532 import failed: {e}")
    PN532_AVAILABLE = False


class HolotapeReader(threading.Thread):
    """Polls the PN532 over SPI and posts HOLOTAPE_INSERTED / HOLOTAPE_REMOVED
    pygame events. Insert posts {uid, folder}; remove posts no payload."""

    POLL_INTERVAL = 0.1      # seconds between polls
    DEBOUNCE_MISSES = 3      # consecutive empty reads before declaring removal
    CS_PIN = board.D8 if PN532_AVAILABLE else None   # GPIO 8 = SPI0 CE0; change if you wired CS elsewhere

    def __init__(self, mapping_file='holotapes/holotapes.json'):
        super().__init__(daemon=True)
        self.mapping_file = mapping_file
        self.mapping = self._load_mapping()
        self.current_uid = None
        self.miss_count = 0
        self.pn532 = None
        self._stop = threading.Event()

    # ---- UID -> folder mapping ----------------------------------------
    def _load_mapping(self):
        if not os.path.exists(self.mapping_file):
            return {}
        try:
            with open(self.mapping_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"[rfid] failed to load {self.mapping_file}: {e}")
            return {}

    def save_mapping(self):
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mapping, f, indent=2)

    def register(self, uid_str, folder_name):
        """Bind a tag UID to a holotape folder; call from a 'register' UI mode."""
        self.mapping[uid_str] = folder_name
        self.save_mapping()
        print(f"[rfid] registered {uid_str} -> {folder_name}")

    # ---- Hardware -----------------------------------------------------
    def _init_pn532(self):
        if not PN532_AVAILABLE:
            return False
        try:
            spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            cs = digitalio.DigitalInOut(self.CS_PIN)
            self.pn532 = PN532_SPI(spi, cs, debug=False)
            ic, ver, rev, sup = self.pn532.firmware_version
            print(f"[rfid] PN532 fw {ver}.{rev}")
            self.pn532.SAM_configuration()
            return True
        except Exception as e:
            print(f"[rfid] PN532 init failed: {e}")
            return False

    def stop(self):
        self._stop.set()

    # ---- Main loop ----------------------------------------------------
    def run(self):
        if not self._init_pn532():
            return

        while not self._stop.is_set():
            try:
                uid = self.pn532.read_passive_target(timeout=0.1)
            except Exception as e:
                print(f"[rfid] read error: {e}")
                uid = None

            uid_str = ':'.join(f'{b:02X}' for b in uid) if uid else None

            if uid_str == self.current_uid:
                # same tape still present, or still empty
                self.miss_count = 0
            elif uid_str is None:
                # the antenna missed once — debounce before declaring removal
                self.miss_count += 1
                if self.miss_count >= self.DEBOUNCE_MISSES and self.current_uid is not None:
                    self._post_removed()
                    self.current_uid = None
                    self.miss_count = 0
            else:
                # new tape (and possibly a fast swap from another tape)
                if self.current_uid is not None:
                    self._post_removed()
                self.current_uid = uid_str
                self.miss_count = 0
                self._post_inserted(uid_str)

            time.sleep(self.POLL_INTERVAL)

    def _post_inserted(self, uid_str):
        folder = self.mapping.get(uid_str)
        pygame.event.post(pygame.event.Event(
            settings.EVENTS['HOLOTAPE_INSERTED'],
            uid=uid_str, folder=folder,
        ))
        print(f"[rfid] inserted {uid_str} -> {folder}")

    def _post_removed(self):
        pygame.event.post(pygame.event.Event(settings.EVENTS['HOLOTAPE_REMOVED']))
        print("[rfid] removed")