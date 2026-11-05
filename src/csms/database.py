"""Database setup for the CSMS application."""

import sqlite3
from pathlib import Path


DATABASE_FILE = Path(__file__).resolve().parent / "csms.db"


def get_connection(database_file=DATABASE_FILE):
    """Create a connection to the SQLite database."""
    return sqlite3.connect(database_file)


def initialize_database(database_file=DATABASE_FILE):
    """Create the database tables if they do not already exist."""
    connection = get_connection(database_file)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            address TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            email TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_id INTEGER NOT NULL,
            service_type TEXT NOT NULL,
            description TEXT NOT NULL,
            date_requested TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    connection.commit()
    connection.close()
