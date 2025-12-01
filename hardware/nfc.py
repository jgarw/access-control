"""
nfc.py

Thanks to insights shared by Lugico and Alex Berliner in this discussion:
https://raspberrypi.stackexchange.com/questions/31773/raspberry-pi-multiple-nfc-readers/137491#137491

Overview:
This script defines an NFC class to manage multiple RC522 readers connected to a shared SPI bus.
Each reader has a dedicated RST (reset) GPIO pin and is initialized using the SimpleMFRC522 class.
Readers will be polled in a loop, activating one at a time to simulate simultaneous scanning.
"""
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import spidev
import time

# Creates an NFC Class used for managing multiple RC522 readers.
class NFC:
    # Initializes the NFC class for managing multiple RC522 readers
    def __init__(self, bus=0, device=0, spd=1000000):
        # SPI bus and device (usually bus 0, device 0 for CE0)
        self.bus = bus
        self.device = device
        self.spd = spd
        
        # Dictionary to hold reader IDs and their associated RST (reset) GPIO pins
        self.boards = {}

        # Will hold the active SimpleMFRC522 reader instance
        self.reader = None

        # Use Broadcom (BCM) pin numbering, e.g., GPIO17 is pin 17
        GPIO.setmode(GPIO.BCM)

    # Reinitializes the RC522 module after switching to a new reader
    def reinit(self):
        # Create a new instance of the SimpleMFRC522 class
        self.reader = SimpleMFRC522()

        # Replace the default SPI object with a custom one
        self.reader.READER.spi = spidev.SpiDev()

        # Open the SPI bus and device (CS0 or CS1)
        self.reader.READER.spi.open(self.bus, self.device)

        # Set the SPI clock speed
        self.reader.READER.spi.max_speed_hz = self.spd

        # Re-initialize the RC522 chip (this wakes it up and resets internal state)
        self.reader.READER.MFRC522_Init()

    # Closes the SPI connection to free the bus
    def close(self):
        if self.reader:
            self.reader.READER.spi.close()  
            self.reader = None

    # Registers a new RC522 board with a reset pin
    def addBoard(self, rid, pin):
        """
        rid: Unique ID string for the reader (e.g., 'reader1')
        pin: GPIO pin number used as RST (reset) for this reader
        """
        self.boards[rid] = pin

        # Set the GPIO pin as output
        GPIO.setup(pin, GPIO.OUT)

        # Set RST to LOW initially (turns off the reader)
        GPIO.output(pin, GPIO.LOW)

    # Selects a specific reader to activate based on reader ID
    def selectBoard(self, rid):
        """
        Only one reader should be active at any time.
        This function activates the one you want and deactivates all others.
        """
        if rid not in self.boards:
            print(f"Reader ID '{rid}' not found")
            return False

        for loop_id, pin in self.boards.items():
            # Turn ON the selected reader, OFF the others
            GPIO.output(pin, GPIO.HIGH if loop_id == rid else GPIO.LOW)

        # Give the selected RC522 some time to stabilize
        time.sleep(0.1)
        return True

    # Attempts to read a card from the selected reader (non-blocking)
    def read(self, rid):
        """
        Selects the reader and tries to detect a card.
        Returns the UID of the card if found, otherwise returns None.
        """
        if not self.selectBoard(rid):
            return None

        # Activate the reader and prepare it for scanning
        self.reinit()

        # Perform a non-blocking read (returns immediately)
        cid, _ = self.reader.read_no_block()

        # Close SPI to avoid conflicts before switching to another reader
        self.close()

        return cid