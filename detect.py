import RPi.GPIO as GPIO
import time

# Define the GPIO pin for the PIR motion sensor
PIR_PIN = 26  # Change this to your actual GPIO pin

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

try:
    print("Reading PIR sensor values... (Press Ctrl+C to stop)")
    while True:
        sensor_value = GPIO.input(PIR_PIN)
        print(f"PIR Sensor Value: {sensor_value}")  # 1 = Motion detected, 0 = No motion
        time.sleep(0.5)  # Adjust delay as needed
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nExiting sensor reading program...")

