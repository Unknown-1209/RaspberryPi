import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

PINS = [31, 29, 15, 13, 11]
GPIO.setup(PINS, GPIO.OUT, initial=GPIO.LOW)

def display_binary(num):
    for i in range(5):
        bit_value = (num >> i) & 1
        GPIO.output(PINS[4 - i], bit_value)


for num in range (32):
    display_binary(num)
    print(f"Binary: {format(num, '05b')} | Decimal: {num}")
    time.sleep(0.75)
    




GPIO.cleanup()
print('Program completed! ')
