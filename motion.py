import RPi.GPIO as GPIO
import time

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1" 
import pygame
pygame.mixer.init()

# GPIO setup
PIR_PIN = 7   # Motion sensor input pin
LED_PIN = 40  # Debugging LED output pin

GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(PIR_PIN, GPIO.IN)  # Set PIR sensor as input
GPIO.setup(LED_PIN, GPIO.OUT)  # Set LED as output

# Pygame setup
pygame.mixer.init()
AUDIO_FILE = "/home/Hufflepuff/Music/B1_hold_it.mp3"
pygame.mixer.music.load(AUDIO_FILE)

droid_on = False

def detect_motion():
    global droid_on

    if GPIO.input(PIR_PIN) and not droid_on:  # Motion detected
        droid_on = False
        print("{Sensor} Motion detected! Initiate Start up")
    else:
        print("INACTIVE")


"""try:
    print("Waiting for motion...")
    while True:
        if GPIO.input(PIR_PIN):  # Motion detected
            print("Motion detected! Turning on LED and playing sound.")
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
            pygame.mixer.music.play()  # Play audio

            # Wait until motion stops before allowing another trigger
            while GPIO.input(PIR_PIN):
                time.sleep(0.1)  # Prevent rapid retriggers

            print("Motion stopped. LED stays ON.")

        time.sleep(0.1)"""  # Small delay before checking again


try:
    while True:
        detect_motion()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()  # Reset GPIO pins

