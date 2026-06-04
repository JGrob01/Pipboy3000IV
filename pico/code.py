"""
Pip-Boy rotary encoder controller.

Rotation behavior depends on mode. Click cycles mode:
    Mode 0: rotate cycles top-level modules (Stats/Inv/Data/Map/Radio)
    Mode 1: rotate cycles the current module's submenu
    Mode 2: rotate scrolls items in the menu list

Wiring (KY-040 or similar 5-pin rotary encoder):
    GND -> GND
    +   -> 3V3
    SW  -> GP15  (button)
    DT  -> GP14
    CLK -> GP13
"""

import time
import board
import digitalio
import rotaryio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# ---------- Hardware ----------
encoder = rotaryio.IncrementalEncoder(board.GP13, board.GP14)

button = digitalio.DigitalInOut(board.GP15)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

kbd = Keyboard(usb_hid.devices)

# ---------- Tuning ----------
COUNTS_PER_DETENT = 1   # try 1 or 2 if rotation feels sluggish; 4 is typical
DEBOUNCE = 0.05         # seconds between button registers
POLL_INTERVAL = 0.005

# ---------- Mappings ----------
MODULE_KEYS = [
    Keycode.F1,   # Stats
    Keycode.F2,   # Inventory
    Keycode.F3,   # Data
    Keycode.F4,   # Map
    Keycode.F5,   # Radio
]

SUBMENU_KEYS = [
    Keycode.ONE, Keycode.TWO, Keycode.THREE,
    Keycode.FOUR, Keycode.FIVE,
]

# How many submenus each top module has
SUBMENU_COUNTS = {
    Keycode.F1: 3,   # Stats:  STATUS, SPECIAL, PERKS
    Keycode.F2: 5,   # Inv:    WEAPONS, APPAREL, AID, MISC, AMMO
    Keycode.F3: 3,   # Data:   HOLOTAPES, QUESTS, MISC
    Keycode.F4: 2,   # Map:    WORLD, LOCAL
    Keycode.F5: 1,   # Radio:  single hidden submodule
}

MODES = ["modules", "submenu", "items"]

# ---------- State ----------
mode = 0
current_module = 0
current_submenu = 0

last_position = encoder.position
last_button = True
last_press_time = 0


def blink_mode():
    """Flash the onboard LED `mode + 1` times to indicate current mode."""
    for _ in range(mode + 1):
        led.value = True
        time.sleep(0.2)
        led.value = False
        time.sleep(0.2)


def current_submenu_count():
    return SUBMENU_COUNTS.get(MODULE_KEYS[current_module], 5)


def step(direction):
    """direction: +1 = right, -1 = left."""
    global current_module, current_submenu

    name = MODES[mode]

    if name == "modules":
        current_module = (current_module + direction) % len(MODULE_KEYS)
        kbd.send(MODULE_KEYS[current_module])
        # Switching module resets submenu in the Pip-Boy engine
        current_submenu = 0

    elif name == "submenu":
        count = current_submenu_count()
        if count <= 1:
            return
        current_submenu = (current_submenu + direction) % count
        kbd.send(SUBMENU_KEYS[current_submenu])

    elif name == "items":
        if direction > 0:
            kbd.send(Keycode.DOWN_ARROW)
        else:
            kbd.send(Keycode.UP_ARROW)


# Indicate startup mode
blink_mode()

while True:
    # ----- Rotation -----
    position = encoder.position
    delta = position - last_position
    if delta != 0:
        last_position = position
        steps = delta
        for _ in range(abs(steps)):
            step(1 if steps > 0 else -1)

    # ----- Button -----
    now = time.monotonic()
    pressed = not button.value
    if pressed and last_button and (now - last_press_time) > DEBOUNCE:
        last_press_time = now
        mode = (mode + 1) % len(MODES)
        last_position = encoder.position
        blink_mode()
    last_button = not pressed

    time.sleep(POLL_INTERVAL)