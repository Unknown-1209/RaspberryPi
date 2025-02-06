import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

PINS = [11, 13, 15, 29, 31]

GPIO.setup(PINS, GPIO.OUT, initial=GPIO.HIGH)

time.sleep(5)


GPIO.cleanup()

print('exiting proram...')
