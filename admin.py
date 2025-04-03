from flask import Flask, flash, render_template, redirect, request, url_for
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import psycopg2
from dotenv import load_dotenv
import os

app = Flask(__name__)

 # Load environment variables from .env file
load_dotenv() 
app.secret_key = os.getenv("SECRET_KEY")
db_password = os.getenv("DB_PASSWORD")

# Create RFID reader instance
reader = SimpleMFRC522()

# method to get db connection (fixed cursor connection already closed errors)
def get_db_connection():
    """Create a new database connection for each request."""
    return psycopg2.connect(
        host='localhost',
        user='postgres',
        password=db_password,
        dbname='access_control',
        port=5432
    )

# index/home page of admin panel
@app.route("/")
def index():
    # create connection to database
    conn = get_db_connection()
    cursor = conn.cursor()

    # query all users from database to display in table in index.html
    cursor.execute("SELECT rfid_tag, role FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()  
    return render_template('index.html', users=users)

# route to handle admin adding new users
@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    scanned_id = 0

    if request.method == "POST":
        # if scan button pressed, read RFID tag from card
        if "scan" in request.form:
            scanned_id, _ = reader.read()
            flash(f"Card scanned successfully! ID: {scanned_id}", "success")  # New success message
            return render_template("add_user.html", scanned_id=scanned_id)

        # if "add user" button pressed, insert values into users table
        if "insert" in request.form:
            rfid_tag = request.form["rfid_tag"]
            role = request.form["role"]

            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO users (rfid_tag, role) VALUES (%s, %s) ON CONFLICT (rfid_tag) DO NOTHING",
                    (rfid_tag, role),
                )
                conn.commit()
                flash("User added successfully!", "success")
            except Exception as e:
                print(f"Error inserting user: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()  # Ensure connection is closed

            return redirect(url_for("index"))

    return render_template('add_user.html', scanned_id=scanned_id)

# handle app termination and cleanup
@app.teardown_appcontext
def cleanup(exception=None):
    """Cleanup GPIO on exit"""
    GPIO.cleanup()

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
