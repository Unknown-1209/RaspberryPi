import RPi.GPIO as GPIO
import time



import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1" 
import pygame
pygame.mixer.init()

# Pygame setup
pygame.mixer.init()
AUDIO_FILE = "/home/Hufflepuff/Music/B1_hold_it.mp3"
pygame.mixer.music.load(AUDIO_FILE)

# Define the GPIO pin for the PIR motion sensor
PIR_PIN = 26  # Change this to your PIR sensor's GPIO pin

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

def wait_for_motion():
    """Waits for motion once and then stops checking."""
    print("[SENSOR] Waiting for motion to start up...")
    # time.sleep(2)  # Small delay to not false trigger when setting up

    trigger_count = 0  # Counter for confirmed detections
    required_triggers = 5  # Number of times motion must be detected to trigger

    while trigger_count < required_triggers:
        if GPIO.input(PIR_PIN):  # Motion detected
            trigger_count += 1
        else:
            trigger_count = 0  # Reset counter if motion is lost

        time.sleep(0.01)  # Small delay to avoid rapid false positives

    pygame.mixer.music.play()  # Play audio

