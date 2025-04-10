from database.connection import get_db_connection
from access.hash import hash_tag 

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
