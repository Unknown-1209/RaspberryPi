import RPi.GPIO as GPIO
from time import sleep

delay = 0.1
inPin = 40
outPin = 38

GPIO.setmode(GPIO.BOARD)

GPIO.setup(inPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(outPin, GPIO.OUT)

try:
    while True:
        readVal = GPIO.input(inPin)
        print(readVal)
        if readVal == 1:
            GPIO.output(outPin, 0)
        if readVal == 0: 
            GPIO.output(outPin, 1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print()
    print('Program exiting...')
