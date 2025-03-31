import time
from mfrc522 import SimpleMFRC522
import spidev
import spi
import RPi.GPIO as GPIO

reader = SimpleMFRC522();

text = input("New Data:")
print("Place Tag...");

try:
    reader.write(text);
    print("Written")
except:
    GPIO.cleanup()

