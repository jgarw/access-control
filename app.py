"""
app.py
This script enables multiple RC522 RFID readers to scan cards in rapid sequence.

Thanks to insights shared by Lugico and Alex Berliner in this discussion:
https://raspberrypi.stackexchange.com/questions/31773/raspberry-pi-multiple-nfc-readers/137491#137491

Overview:
This script defines an NFC class to manage multiple RC522 readers connected to a shared SPI bus.
Each reader has a dedicated RST (reset) GPIO pin and is initialized using the SimpleMFRC522 class.
Readers are polled in a loop, activating one at a time to simulate simultaneous scanning.
"""
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import spidev
import time
import os
from dotenv import load_dotenv
import psycopg2
import hashlib

# Get ENV variables from .env file
load_dotenv()
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")

# Setup LED pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

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

# Hashes ID passed as parameter using SHA256
def hash_tag(rfid_tag):
    return hashlib.sha256(rfid_tag.encode('utf-8')).hexdigest()

# method to get db connection (fixed cursor connection already closed errors)
def get_db_connection():
    """Create a new database connection for each request."""
    return psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        dbname=db_name,
        port=db_port
    )

# Gets user from database using rfid_tag from card
def get_user(rfid_tag):

    # Establish connection to database
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed = hash_tag(rfid_tag)

    try:
        # Create SELECT statement using rfid_tag scanned
        cursor.execute("SELECT role FROM users WHERE rfid_tag = %s", (hashed,))

        result = cursor.fetchone()

        if not result:
            print(f"User not found in database!")
            return False

        # Retrieve the role from the db associated with rfid_tag ID
        return result[0]
    
    finally:
        cursor.close()
        conn.close()

# Check whether user has access based on role
def check_access(rfid_tag, rid):
    
    # Get user and their role using get_user() method
    role = get_user(rfid_tag)

    # Handle case where user is not in table
    if not role:
        return False

    # Create connection to database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create SELECT statement for access_permissions table
    cursor.execute("SELECT 1 FROM access_permissions WHERE access_point_id = %s and allowed_role = %s", (rid, role))

    check_permission = cursor.fetchone()

    # Handle case where User exists but does not have required role(s)
    if not check_permission:
        print(f"User not allowed at access point {rid}")
        log_attempt(rfid_tag, rid, "failure", f"User not found or not allowed at {rid}.")
        access_denied()
        return False
    
    # User exists and has required role(s) for access point
    print(f"User with role {role} granted access to {rid}")
    log_attempt(rfid_tag, rid, "success", f"User with role {role} granted access to {rid}")
    access_granted()
    return check_permission

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

# Log attempts into database log table
def log_attempt(rfid_tag, rid, result, message):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO access_logs(rfid_tag, reader_id, result, message) VALUES(%s, %s, %s, %s)", (hash_tag(rfid_tag), rid, result, message))
        conn.commit()
    except Exception as e:
        print(f"Error creating log. {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# ------------------------ MAIN PROGRAM ------------------------

def main():

    # Instantiate NFC manager
    nfc = NFC()

    # Register readers by providing a name and their RST GPIO pin
    nfc.addBoard("server_room", 25)  # Example: Reader 1 reset pin connected to GPIO 25
    nfc.addBoard("maintenance_room", 23)  # Example: Reader 2 reset pin connected to GPIO 23

    print("Place card near reader...")

    try:
        while True:
            # Loop through each registered reader
            for rid in nfc.boards:
                # Attempt to read a card from the current reader
                card_id = nfc.read(rid)

                # If a card is detected, print the UID
                if card_id:

                    # Cast card_id to String
                    rfid_tag = str(card_id)
                    result = check_access(rfid_tag, rid)

                    print("\nPlace card near reader...")

            # Sleep briefly to avoid hammering the SPI bus and allow debounce
            time.sleep(0.5)

    except KeyboardInterrupt:
        # Cleanup GPIO pins gracefully on Ctrl+C
        GPIO.cleanup()
        print("Exiting cleanly.")

if __name__ == "__main__":
    main();