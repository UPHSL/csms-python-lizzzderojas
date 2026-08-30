"""Repository for storing and retrieving Resident records."""

import sqlite3

from csms.database import get_connection
from csms.models.resident import Resident


class ResidentRepository:
    """Handle Resident persistence in the database."""

    def __init__(self, database_file=None):
        self.database_file = database_file

    def get_connection(self):
        """Create a connection to the selected database."""
        if self.database_file is None:
            return get_connection()

        return sqlite3.connect(self.database_file)

    def save(self, resident):
        """Save a Resident and assign the generated ID."""
        connection = self.get_connection()

        cursor = connection.execute(
            """
            INSERT INTO residents (
                first_name,
                last_name,
                address,
                contact_number,
                email,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                resident.first_name,
                resident.last_name,
                resident.address,
                resident.contact_number,
                resident.email,
                resident.status,
            ),
        )

        connection.commit()

        resident.id = cursor.lastrowid

        connection.close()

        return resident

    def find_by_id(self, resident_id):
        """Find a Resident by ID."""
        connection = self.get_connection()

        cursor = connection.execute(
            """
            SELECT
                id,
                first_name,
                last_name,
                address,
                contact_number,
                email,
                status
            FROM residents
            WHERE id = ?
            """,
            (resident_id,),
        )

        row = cursor.fetchone()

        connection.close()

        if row is None:
            return None

        resident = Resident(
            first_name=row[1],
            last_name=row[2],
            address=row[3],
            contact_number=row[4],
            email=row[5],
            status=row[6],
            id=row[0],
        )

        return resident