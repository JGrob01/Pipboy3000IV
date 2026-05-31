import time
import board, busio, digitalio
from adafruit_pn532.spi import PN532_SPI

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D8)
pn532 = PN532_SPI(spi, cs, debug=False)

ic, ver, rev, sup = pn532.firmware_version
print(f"PN532 firmware: {ver}.{rev}")
pn532.SAM_configuration()

print("Waiting for tags... (Ctrl+C to quit)")
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print(':'.join(f'{b:02X}' for b in uid))
    time.sleep(0.1)