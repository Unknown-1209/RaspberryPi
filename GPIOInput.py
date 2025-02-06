import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

PIN = 40
GPIO.setup(PIN, GPIO.IN)

try:
    while True:
        readVal = GPIO.input(PIN)
        print(readVal)
        sleep(.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print()
    print('Program exiting...')
