import RPi.GPIO as GPIO
import time

# GPIO Pin Setup for the Sensor
SENSOR_PIN = 20  # Replace with the GPIO pin number your sensor is connected to

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to print the sensor state
def print_sensor_state(pin):
    state = GPIO.input(pin)
    if state == GPIO.HIGH:
        print("Sensor is HIGH (not pressed)")
    else:
        print("Sensor is LOW (pressed)")

# Main loop
try:
    previous_state = GPIO.input(SENSOR_PIN)  # Get the initial state of the sensor
    print_sensor_state(SENSOR_PIN)  # Print the initial state

    while True:
        current_state = GPIO.input(SENSOR_PIN)
        if current_state != previous_state:  # Sensor state has changed
            print_sensor_state(SENSOR_PIN)  # Print the new state
            previous_state = current_state  # Update the previous state

        # Small delay to avoid excessive CPU usage
        state = GPIO.input(SENSOR_PIN)
        print(state)
        time.sleep(0.1)

except KeyboardInterrupt:
    # Clean up GPIO on exit
    GPIO.cleanup()
