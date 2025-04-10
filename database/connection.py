"""
connection.py

This script defines a method for retrieving database credentials from .env file, as well as establishing a connection to postgres database.
"""

import os
from dotenv import load_dotenv
import psycopg2

# Get ENV variables from .env file
load_dotenv()


# method to get db connection (fixed cursor connection already closed errors)
def get_db_connection():
    """Create a new database connection for each request."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )