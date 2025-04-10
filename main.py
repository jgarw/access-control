"""
main.py
This script enables multiple RC522 RFID readers to scan cards in rapid sequence.
"""

import RPi.GPIO as GPIO
import time
from hardware.nfc import NFC
from access.auth import check_access

# Define main method to drive program
def main():

    # Instantiate NFC manager
    nfc = NFC()

    # Register readers by providing a name and their RST GPIO pin
    nfc.addBoard("server_room", 25) 
    nfc.addBoard("maintenance_room", 23)

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