import RPi.GPIO as GPIO
import time

# GPIO Mode Setup
GPIO.setmode(GPIO.BCM)

# LED GPIO Pins
LED_PINS = {
    "LED1": {"red": 10, "green": 9, "blue": 11},  # GPIO pins for LED1
    "LED2": {"red": 5, "green": 6, "blue": 13},    # GPIO pins for LED2
    "LED3": {"red": 23, "green": 24, "blue": 25},  # GPIO pins for LED3
}

# Initialize LED GPIO pins
for led, pins in LED_PINS.items():
    for color, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Turn off all LEDs initially

try:
    while True:
        # Turn on each LED color one by one
        for led, pins in LED_PINS.items():
            for color, pin in pins.items():
                print(pin)
                print(f"Turning on {led} {color}")
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(pin, GPIO.LOW)
        time.sleep(1)  # Small delay between cycles

except KeyboardInterrupt:
    GPIO.cleanup()
