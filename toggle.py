import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

delay = 0.05
inPin = 40
outPin = 38

GPIO.setup(inPin, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(outPin, GPIO.OUT, initial=GPIO.LOW)

LEDState = 0
buttonState = 1
buttonStateOld = 1

try:
    while True:
        buttonState = GPIO.input(inPin)
        print(buttonState)
        if buttonState == 0 and buttonStateOld == 1:
            LEDState = not LEDState
            GPIO.output(outPin, LEDState)
        buttonStateOld = buttonState

        sleep(delay)


except KeyboardInterrupt:
    GPIO.cleanup()
    print()
    print('Program exiting...')
