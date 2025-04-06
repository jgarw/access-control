"""
admin.py
Flask admin panel for managing users and access point permissions.

Overview:
This script runs a web interface that allows RFID tags to be scanned and assigned roles.
Admins can view users, assign roles, and configure which roles can access specific points.
Uses PostgreSQL for storing users and permissions.
RFID scanning is handled via the SimpleMFRC522 reader class.
"""

from flask import Flask, flash, render_template, redirect, request, url_for
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import psycopg2
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Get ENV variables from .env file
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")

# Create RFID reader instance
reader = SimpleMFRC522()

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
                flash("Error inserting user!")
                print(f"Error inserting user: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()  # Ensure connection is closed

            return redirect(url_for("index"))

    return render_template('add_user.html', scanned_id=scanned_id)

# route to handle modifying access point roles
@app.route("/access_points", methods=["GET", "POST"])
def access_points():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM access_permissions")

    access_points = cursor.fetchall()

    # cursor.execute("INSERT INTO access_permissions('access_point_id','allowed_roles') VALUES(%s, %s)", (rfid_tag, role))

    return render_template("access_points.html", access_points=access_points)

# route to handle adding access point role
@app.route("/add_point_role", methods=["GET", "POST"])
def add_point_role():

    # if form is submitted
    if request.method == "POST":
        access_point = request.form['access_point']
        role = request.form['role']

        # try inserting values from form into table
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # prepare insert statement from form values
            cursor.execute("INSERT INTO access_permissions(access_point_id, allowed_role) VALUES(%s, %s) ON CONFLICT DO NOTHING", (access_point, role))

            conn.commit()
            flash("Access permission added!", "success")

        except Exception as e:
            flash("Error adding access permission!", "danger")
            print(f"Error: {e}")
            conn.rollback()
            return render_template("add_point_role.html")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("access_points"))
            
    # on GET
    conn = get_db_connection()
    cursor = conn.cursor()

    # retrieve the access_point_id's from access_permissions to add to select list
    cursor.execute("SELECT DISTINCT access_point_id FROM access_permissions");
    access_points = cursor.fetchall()

    cursor.close()
    conn.close()

    # load page with access_point values
    return render_template("add_point_role.html", access_points=access_points)

# route to handle deleting access point role
@app.route("/delete_point_role", methods=["GET", "POST"])
def delete_point_role():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        access_point = request.form['access_point']
        role = request.form['role']

        try:
            # delete selected role from access point
            cursor.execute(
                "DELETE FROM access_permissions WHERE access_point_id = %s AND allowed_role = %s",
                (access_point, role)
            )
            conn.commit()
            flash("Access permission removed.", "success")
        except Exception as e:
            flash(f"Error deleting access permission! {e}")
            conn.rollback()
            return render_template("delete_point_role.html")
        finally:
            cursor.close()
            conn.close()
        return render_template("access_points.html")

    # On GET or pre-form POST
    cursor.execute("SELECT DISTINCT access_point_id FROM access_permissions")
    access_points = cursor.fetchall()

    selected_point = request.args.get("access_point")
    roles = []

    if selected_point:
        cursor.execute("SELECT allowed_role FROM access_permissions WHERE access_point_id = %s", (selected_point,))
        roles = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("delete_point_role.html", access_points=access_points, roles=roles, selected_point=selected_point)



# handle app termination and cleanup
@app.teardown_appcontext
def cleanup(exception=None):
    """Cleanup GPIO on exit"""
    GPIO.cleanup()

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
