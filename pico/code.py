"""
Pip-Boy 3000 MK IV - Pico I/O Coprocessor

Acts as a USB HID keyboard + consumer-control device for the Raspberry Pi
running the Pip-Boy app. All physical controls funnel through here.

Wiring:
  GP0/GP1   I2C0 SDA/SCL  -> SparkFun ROB-15451 motor driver -> bipolar stepper (radiation gauge)
  GP2-GP6   JS5208 5-way joystick (UP, DOWN, LEFT, RIGHT, CENTER) - active low
  GP7       ESE-20C441 select button - active low
  GP8       TL1265YQSCLR power button - active low (short / long press)
  GP9       TL1265YQSCLR flashlight button - active low (not used yet)
  GP10      DHT22 humidity sensor (single-wire)
  GP13      KY-040 encoder CLK
  GP14      KY-040 encoder DT
  GP15      KY-040 encoder SW - active low
  GP16      WS2812B NeoPixel chain (not used yet)
  GP18      TL1265YQSCLR flashlight LED output (not used yet)
  GP26 ADC0 Bourns 3382G - Menu Selector pot (absolute, 5 zones -> F1..F5)
  GP27 ADC1 Bourns 3382G - SubMenu Selector pot (relative, LEFT/RIGHT arrow)
  GP28 ADC2 Bourns 3382G - Radio pot (cosmetic for now)

Keys sent to Pi:
  F1..F5         module switch (STAT / INV / DATA / MAP / RADIO)
  LEFT/RIGHT     submenu prev/next
  UP/DOWN        item scroll
  ENTER          select
  F9             power button short press (Pi handles graceful shutdown)
  Vol+/Vol-      encoder rotation  (consumer control)
  Mute           encoder click     (consumer control)
"""

import time
import board
import digitalio
import analogio
import rotaryio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# =================================================================
# CONFIG / TUNING
# =================================================================

POLL_INTERVAL = 0.005

# Button debounce
DEBOUNCE = 0.05

# Encoder: rotaryio gives 4 counts per detent on most KY-040 units
COUNTS_PER_DETENT = 4

# Pot tuning
MENU_POT_ZONES = 5
MENU_POT_HYSTERESIS = 1500          # ADC counts; stops jitter at zone boundaries
SUBMENU_POT_STEP_THRESHOLD = 4000   # ADC counts of motion to register one step
RADIO_POT_REPORT_THRESHOLD = 500    # ignore radio pot noise below this

# Power button
POWER_LONG_PRESS = 3.0  # seconds; held >= this triggers hard-off path

# DHT22
DHT_SAMPLE_PERIOD = 2.0  # DHT22 spec minimum

# Stepper / radiation gauge (CALIBRATE THESE)
GAUGE_STEPS_FULL_RANGE = 200   # steps from needle-left to needle-right
GAUGE_HUMIDITY_MIN = 20        # % humidity that pins the needle left
GAUGE_HUMIDITY_MAX = 80        # % humidity that pins the needle right

# Initial menu-pot sync delay: gives the Pi time to boot before
# we send the first F-key. If the Pi misses it, the user can just
# wiggle the Menu pot to re-sync.
INITIAL_SYNC_DELAY = 8.0

# Module mapping (matches Pi-side F1..F5 handlers)
MODULE_KEYS = [
    Keycode.F1,  # Stats
    Keycode.F2,  # Inventory
    Keycode.F3,  # Data
    Keycode.F4,  # Map
    Keycode.F5,  # Radio
]


# =================================================================
# HID DEVICES
# =================================================================
kbd = Keyboard(usb_hid.devices)
consumer = ConsumerControl(usb_hid.devices)


# =================================================================
# HARDWARE INIT
# =================================================================

def _input_pullup(pin):
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.INPUT
    p.pull = digitalio.Pull.UP
    return p

# Joystick (CENTER intentionally unused)
joy_up     = _input_pullup(board.GP2)
joy_down   = _input_pullup(board.GP3)
joy_left   = _input_pullup(board.GP4)
joy_right  = _input_pullup(board.GP5)
joy_center = _input_pullup(board.GP6)

# Buttons
select_btn     = _input_pullup(board.GP7)
power_btn      = _input_pullup(board.GP8)
flashlight_btn = _input_pullup(board.GP9)

# Flashlight LED (placeholder)
flashlight_led = digitalio.DigitalInOut(board.GP18)
flashlight_led.direction = digitalio.Direction.OUTPUT
flashlight_led.value = False

# Encoder
encoder     = rotaryio.IncrementalEncoder(board.GP13, board.GP14)
encoder_btn = _input_pullup(board.GP15)

# Pots
menu_pot    = analogio.AnalogIn(board.GP26)
submenu_pot = analogio.AnalogIn(board.GP27)
radio_pot   = analogio.AnalogIn(board.GP28)

# DHT22 (uncomment when adafruit_dht is in /lib)
# import adafruit_dht
# dht = adafruit_dht.DHT22(board.GP10)
dht = None

# Motor driver (uncomment when the SparkFun motor driver lib is in /lib)
# import busio
# from sparkfun_qwiicmotordriver import QwiicMotorDriver  # confirm exact lib name
# i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
# motor = QwiicMotorDriver(i2c)
motor = None

# Onboard LED for debug
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


# =================================================================
# STATE
# =================================================================

def _initial_zone(value, num_zones):
    z = value * num_zones // 65536
    return num_zones - 1 if z >= num_zones else z

# Menu pot - absolute
current_menu_zone = _initial_zone(menu_pot.value, MENU_POT_ZONES)
boot_time = time.monotonic()
initial_sync_sent = False

# SubMenu pot - relative; anchor moves each time we emit a step
submenu_anchor = submenu_pot.value

# Radio pot - cosmetic; track last reported value
last_radio_value = radio_pot.value

# Joystick
joy_inputs = {
    # name: (pin, keycode)
    "up":    (joy_up,    Keycode.UP_ARROW),
    "down":  (joy_down,  Keycode.DOWN_ARROW),
    "left":  (joy_left,  Keycode.LEFT_ARROW),
    "right": (joy_right, Keycode.RIGHT_ARROW),
}
joy_last_state = {name: True for name in joy_inputs}

# Buttons (debounce state)
btn_last_state = {"select": True, "encoder": True, "flashlight": True}
btn_last_press_time = {"select": 0.0, "encoder": 0.0, "flashlight": 0.0}

# Power button (special: short vs long press)
power_last_state = True
power_pressed_at = None
power_long_fired = False

# Encoder
last_encoder_position = encoder.position
encoder_accum = 0

# DHT22 / gauge
last_dht_sample = 0.0
current_humidity = None
current_gauge_target = 0
current_gauge_position = 0


# =================================================================
# HELPERS
# =================================================================

def menu_zone_with_hysteresis(value, current_zone):
    """Return new zone, but stick to current zone within deadband."""
    zone_size = 65536 // MENU_POT_ZONES
    low = current_zone * zone_size - MENU_POT_HYSTERESIS
    high = (current_zone + 1) * zone_size + MENU_POT_HYSTERESIS
    if low <= value <= high:
        return current_zone
    new_zone = value * MENU_POT_ZONES // 65536
    if new_zone < 0:
        return 0
    if new_zone >= MENU_POT_ZONES:
        return MENU_POT_ZONES - 1
    return new_zone


def humidity_to_steps(humidity_pct):
    """Map humidity % to absolute stepper position."""
    if humidity_pct is None:
        return current_gauge_position
    h = max(GAUGE_HUMIDITY_MIN, min(GAUGE_HUMIDITY_MAX, humidity_pct))
    span = GAUGE_HUMIDITY_MAX - GAUGE_HUMIDITY_MIN
    pct = (h - GAUGE_HUMIDITY_MIN) / span
    return int(pct * GAUGE_STEPS_FULL_RANGE)


def move_gauge_to(target_steps):
    """Move stepper toward target_steps. NON-BLOCKING.

    TODO: implement with the SparkFun Qwiic Motor Driver lib once it's
    installed. For a bipolar stepper, drive both motor channels in the
    standard 4-step (full) or 8-step (half) pattern, one step per call,
    walking current_gauge_position toward target_steps. Do not block —
    the main loop needs to keep responding to inputs.
    """
    global current_gauge_position
    if motor is None:
        current_gauge_position = target_steps  # pretend until lib is wired
        return
    # TODO: real stepping logic here.
    current_gauge_position = target_steps


def process_radio_pot(value):
    """Cosmetic for now.

    Future: quantize to N zones to send station-select keys, or pipe the
    raw value over USB CDC serial as a fine-tuning indicator for the Pi's
    Radio module.
    """
    pass


# =================================================================
# STARTUP
# =================================================================

print("Pip-Boy Pico controller starting…")
for _ in range(3):
    led.value = True
    time.sleep(0.1)
    led.value = False
    time.sleep(0.1)


# =================================================================
# MAIN LOOP
# =================================================================

while True:
    now = time.monotonic()

    # -------------------------------------------------------------
    # Initial Menu pot sync (once, after Pi has booted)
    # -------------------------------------------------------------
    if not initial_sync_sent and (now - boot_time) >= INITIAL_SYNC_DELAY:
        kbd.send(MODULE_KEYS[current_menu_zone])
        initial_sync_sent = True
        print("[boot] synced menu zone -> module", current_menu_zone)

    # -------------------------------------------------------------
    # Menu pot (absolute, F1..F5)
    # -------------------------------------------------------------
    new_zone = menu_zone_with_hysteresis(menu_pot.value, current_menu_zone)
    if new_zone != current_menu_zone:
        current_menu_zone = new_zone
        kbd.send(MODULE_KEYS[current_menu_zone])
        print("[menu pot] zone ->", current_menu_zone)

    # -------------------------------------------------------------
    # SubMenu pot (relative, LEFT/RIGHT arrow)
    # -------------------------------------------------------------
    submenu_now = submenu_pot.value
    delta = submenu_now - submenu_anchor
    if delta >= SUBMENU_POT_STEP_THRESHOLD:
        kbd.send(Keycode.RIGHT_ARROW)
        submenu_anchor = submenu_now
        print("[submenu pot] -> RIGHT")
    elif delta <= -SUBMENU_POT_STEP_THRESHOLD:
        kbd.send(Keycode.LEFT_ARROW)
        submenu_anchor = submenu_now
        print("[submenu pot] -> LEFT")

    # -------------------------------------------------------------
    # Radio pot (cosmetic)
    # -------------------------------------------------------------
    radio_now = radio_pot.value
    if abs(radio_now - last_radio_value) >= RADIO_POT_REPORT_THRESHOLD:
        process_radio_pot(radio_now)
        last_radio_value = radio_now

    # -------------------------------------------------------------
    # Joystick (UP/DOWN/LEFT/RIGHT) - edge-triggered, no auto-repeat
    # CENTER is intentionally not wired up.
    # -------------------------------------------------------------
    for name, (pin, keycode) in joy_inputs.items():
        pressed = not pin.value
        was_pressed = not joy_last_state[name]
        if pressed and not was_pressed:
            kbd.send(keycode)
        joy_last_state[name] = pin.value

    # -------------------------------------------------------------
    # Select button -> ENTER
    # -------------------------------------------------------------
    pressed = not select_btn.value
    if (pressed and btn_last_state["select"]
            and (now - btn_last_press_time["select"]) > DEBOUNCE):
        btn_last_press_time["select"] = now
        kbd.send(Keycode.ENTER)
        print("[select] ENTER")
    btn_last_state["select"] = not pressed

    # -------------------------------------------------------------
    # Encoder click -> MUTE
    # (consumer-control; if your Pi audio doesn't react, change this
    #  to a regular Keycode and bind it in the pygame event handler.)
    # -------------------------------------------------------------
    pressed = not encoder_btn.value
    if (pressed and btn_last_state["encoder"]
            and (now - btn_last_press_time["encoder"]) > DEBOUNCE):
        btn_last_press_time["encoder"] = now
        consumer.send(ConsumerControlCode.MUTE)
        print("[encoder click] MUTE")
    btn_last_state["encoder"] = not pressed

    # -------------------------------------------------------------
    # Flashlight button (placeholder)
    # -------------------------------------------------------------
    pressed = not flashlight_btn.value
    if (pressed and btn_last_state["flashlight"]
            and (now - btn_last_press_time["flashlight"]) > DEBOUNCE):
        btn_last_press_time["flashlight"] = now
        # TODO: toggle flashlight_led.value and notify Pi
        pass
    btn_last_state["flashlight"] = not pressed

    # -------------------------------------------------------------
    # Power button: short press -> F9 (Pi soft shutdown)
    #               long press  -> hard-off (TODO: drive EN line low)
    # -------------------------------------------------------------
    pressed = not power_btn.value
    if pressed and power_last_state:
        # rising edge
        power_pressed_at = now
        power_long_fired = False
    elif pressed and not power_last_state:
        # still held
        if (not power_long_fired and power_pressed_at is not None
                and (now - power_pressed_at) >= POWER_LONG_PRESS):
            print("[power] LONG press -> hard off (TODO: drive EN low)")
            # TODO: pull a GPIO output low to latch PowerBoost EN
            power_long_fired = True
    elif not pressed and not power_last_state:
        # released
        if (not power_long_fired and power_pressed_at is not None):
            held = now - power_pressed_at
            if held < POWER_LONG_PRESS:
                kbd.send(Keycode.F9)
                print("[power] short press -> F9 (held {:.2f}s)".format(held))
        power_pressed_at = None
        power_long_fired = False
    power_last_state = not pressed

    # -------------------------------------------------------------
    # Encoder rotation -> volume + / -
    # (consumer-control; swap to regular Keycodes if your Pi-side
    #  pygame app needs to handle volume in code.)
    # -------------------------------------------------------------
    position = encoder.position
    delta = position - last_encoder_position
    if delta != 0:
        last_encoder_position = position
        encoder_accum += delta
        while encoder_accum >= COUNTS_PER_DETENT:
            consumer.send(ConsumerControlCode.VOLUME_INCREMENT)
            encoder_accum -= COUNTS_PER_DETENT
        while encoder_accum <= -COUNTS_PER_DETENT:
            consumer.send(ConsumerControlCode.VOLUME_DECREMENT)
            encoder_accum += COUNTS_PER_DETENT

    # -------------------------------------------------------------
    # DHT22 -> radiation gauge needle
    # -------------------------------------------------------------
    if dht is not None and (now - last_dht_sample) >= DHT_SAMPLE_PERIOD:
        last_dht_sample = now
        try:
            current_humidity = dht.humidity
            if current_humidity is not None:
                target = humidity_to_steps(current_humidity)
                if target != current_gauge_target:
                    current_gauge_target = target
                    move_gauge_to(target)
        except (RuntimeError, OSError) as e:
            # DHT22 reads occasionally fail; just retry next cycle
            print("[dht] read failed:", e)

    time.sleep(POLL_INTERVAL)