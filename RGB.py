import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

rPin = 37
gPin = 35
bPin = 33

GPIO.setup(rPIN, GPIO.OUT)

# PWM1 = GPIO

try:



except KeyboardInterrupt:
    myPWM.stop()
    GPIO.cleanup()
    print()
    print('Program exiting...')
