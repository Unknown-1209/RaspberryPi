import RPi.GPIO as GPIO
import time

# GPIO Pin Setup for RGB LEDs
LED_PINS = {
    "LED1": {"red": 17, "green": 27, "blue": 22},  # GPIO pins for LED1
    "LED2": {"red": 23, "green": 24, "blue": 25},  # GPIO pins for LED2
    "LED3": {"red": 5, "green": 6, "blue": 13},    # GPIO pins for LED3
}

# GPIO Pin Setup for Touch Sensors
TOUCH_SENSORS = {
    "SENSOR1": 16,  # GPIO pin for Sensor 1 (paired with LED1)
    "SENSOR2": 20,  # GPIO pin for Sensor 2 (paired with LED2)
    "SENSOR3": 21,  # GPIO pin for Sensor 3 (paired with LED3)
}

# Colors to cycle through
COLORS = [
    (1, 0, 0),  # Red
    (0, 1, 0),  # Green
    (0, 0, 1),  # Blue
    (1, 0, 1),  # Purple
]

# Initialize GPIO
GPIO.setmode(GPIO.BCM)

# Setup LED pins as outputs
for led, pins in LED_PINS.items():
    for color, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT, initial = GPIO.LOW)  # Turn off all LEDs initially

# Setup touch sensor pins as inputs with pull-up resistors
for sensor, pin in TOUCH_SENSORS.items():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to set LED color
def set_led_color(led, red, green, blue):
    GPIO.output(LED_PINS[led]["red"], red)
    GPIO.output(LED_PINS[led]["green"], green)
    GPIO.output(LED_PINS[led]["blue"], blue)

# Dictionary to track the current color state for each LED
color_states = {"LED1": -1, "LED2": -1, "LED3": -1}  # Start with all LEDs off

# Dictionary to track the previous state of each sensor
sensor_states = {sensor: GPIO.LOW for sensor in TOUCH_SENSORS}

# Function to toggle color for a specific LED
def toggle_led_color(led):
    color_states[led] = (color_states[led] + 1) % len(COLORS)
    set_led_color(led, *COLORS[color_states[led]])

# Main loop
try:
    while True:
        # Check each sensor and update its corresponding LED
        for sensor, pin in TOUCH_SENSORS.items():
            current_state = GPIO.input(pin)
            if current_state != sensor_states[sensor]:  # Sensor state has changed
                sensor_states[sensor] = current_state  # Update the sensor state
                if current_state == GPIO.LOW:  # Sensor is pressed (LOW)
                    led = f"LED{sensor[-1]}"  # Match sensor to LED (e.g., SENSOR1 -> LED1)
                    toggle_led_color(led)

        # Small delay to avoid excessive CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    # Clean up GPIO on exit
    GPIO.cleanup()
