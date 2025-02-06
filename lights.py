import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD) # Sets the pin configuration to board
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW) # Sets GPIO pin 11 for output

blinks = int(input('How many blinks would you like: ')) 

for i in range(0, blinks):
    GPIO.output(11, True)
    time.sleep(0.5)
    GPIO.output(11, False)
    time.sleep(0.5)

GPIO.cleanup() # DO NOT REMOVE! Clears the pins and prevents errors

print('Process completed! ')
