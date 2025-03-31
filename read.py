import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522();

try:
    while True:
        print("Please scan card.");
        id, text = reader.read();
        print("ID: ", id);
        time.sleep(5);
except:
    GPIO.cleanup()

