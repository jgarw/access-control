"""
auth.py

Overview:
This script defines functions required for interacting with the database to authorize users scanning their RFID cards.
"""

from database.connection import get_db_connection
from access.hash import hash_tag
from access.log import log_attempt
from hardware.led import access_denied, access_granted

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
