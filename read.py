import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import psycopg2

# create instance of RC522 reader
reader = SimpleMFRC522();

# handle database connection
db_password = input("Enter DB Password: ");
connection = psycopg2.connect(host='localhost', 
                              user='postgres',
                              password=db_password, 
                              dbname='access_control', 
                              port=5432)
cursor = connection.cursor();

GPIO.setmode(GPIO.BOARD);
GPIO.setup(36, GPIO.OUT);
GPIO.setup(40, GPIO.OUT);
# GPIO.output(16, GPIO.LOW);

# function to retreive a cards ID from database
def check_access(rfid_tag):
    try:
        cursor.execute("SELECT role FROM users WHERE rfid_tag = %s", (rfid_tag,));
        return cursor.fetchone();
    except Exception as e:
        print(f"Error retrieving user: {e}")

# function to light led on access granted
def access_granted():
    GPIO.output(36, GPIO.HIGH);
    time.sleep(5);
    GPIO.output(36, GPIO.LOW);

# function to light led on access denied
def access_denied():
    GPIO.output(40, GPIO.HIGH);
    time.sleep(5);
    GPIO.output(40, GPIO.LOW);


try:
    while True:
        print("Please scan card.");
        id, text = reader.read();
        print("ID: ", id);

        # convert rfid tag to string for working with database
        rfid_tag = str(id);

        # get the role from the psql users table using rfid as key
        role = check_access(rfid_tag);
        role = role[0].strip();

        # check correct access level
        if role and role == 'Engineer':
            print("Access granted!");
            access_granted();
        else:
            access_denied();
        
        time.sleep(5);
except:
    GPIO.cleanup()

