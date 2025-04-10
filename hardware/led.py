import RPi.GPIO as GPIO
import time

# Setup LED pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setwarnings(False)

# Light up green LED on access granted
def access_granted():
    GPIO.output(20, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(20, GPIO.LOW)

# Light up red LED on access granted
def access_denied():
    GPIO.output(21, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(21, GPIO.LOW)