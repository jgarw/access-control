import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import psycopg2

reader = SimpleMFRC522();

db_user = input("Enter DB Username: ");
db_password = input("Enter DB Password: ");

# create connection to postgres database
connection = psycopg2.connect(host='localhost', 
                              user=db_user,
                              password=db_password, 
                              dbname='access_control', 
                              port=5432)

cursor = connection.cursor();

# create a method for inserting users into database
def insert_user(rfid_tag, role):
    try:
        # create INSERT statement
        cursor.execute("INSERT INTO users (rfid_tag, role) VALUES (%s, %s) ON CONFLICT (rfid_tag) DO NOTHING", (rfid_tag, role));

        connection.commit();
        print("User successfully inserted into database!");
    except Exception as e:
        print(f"Error inserting user: {e}")
        connection.rollback()

try:
    print("Place tag near reader...");
    id, text = reader.read();
    role = input("Enter User's role...");
    print("Inserting ID: ", id, " with role: ", role);

    insert_user(id, role);
    time.sleep(5)

except KeyboardInterrupt:
    print("Program interrupted and stopped.")
finally:
    GPIO.cleanup()
    cursor.close()
    connection.close()



