from gpiozero import DigitalOutputDevice

import time

# GPIO18

from gpiozero import DigitalOutputDevice
from signal import pause

input_pin = DigitalOutputDevice(18)

for i in range(1000):
    input_pin.off()  # Ensure the pin is LOW before starting
    print("Pin 18 is now LOW")
    time.sleep(1)  # Wait for 1 second
    input_pin.on()
    print("Pin 18 is now HIGH")
    time.sleep(2)  # Keep it HIGH for 2 seconds
