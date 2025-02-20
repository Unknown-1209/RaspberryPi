import RPi.GPIO as GPIO
import time

Rpin = 29
Gpin = 31
Bpin = 33

GPIO.setmode(GPIO.BOARD) # Sets the pin configuration to board
GPIO.setup(Rpin, GPIO.OUT, initial=GPIO.LOW) # Sets GPIO pin 11 for output
GPIO.setup(Gpin, GPIO.OUT, initial=GPIO.LOW) # Sets GPIO pin 11 for output
GPIO.setup(Bpin, GPIO.OUT, initial=GPIO.LOW) # Sets GPIO pin 11 for output




blinks = int(input('How many blinks would you like: ')) 

for i in range(0, blinks):
    GPIO.output(Rpin, True)
    time.sleep(0.5)
    GPIO.output(Rpin, False)
    time.sleep(0.5)

    GPIO.output(Gpin, True)
    time.sleep(0.5)
    GPIO.output(Gpin, False)
    time.sleep(0.5)

    GPIO.output(Bpin, True)
    time.sleep(0.5)
    GPIO.output(Bpin, False)
    time.sleep(0.5)

GPIO.cleanup() # DO NOT REMOVE! Clears the pins and prevents errors

print('Process completed! ')
