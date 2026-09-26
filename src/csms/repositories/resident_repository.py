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

    def find_all(self):
        """Find all Residents in the required order."""
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
            ORDER BY last_name ASC, first_name ASC, id ASC
            """
        )

        rows = cursor.fetchall()
        connection.close()

        residents = []

        for row in rows:
            resident = Resident(
                first_name=row[1],
                last_name=row[2],
                address=row[3],
                contact_number=row[4],
                email=row[5],
                status=row[6],
                id=row[0],
            )
            residents.append(resident)

        return residents

    def search(self, query):
        """Search Residents by first name or last name."""
        connection = self.get_connection()

        search_text = f"%{query.strip()}%"

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
            WHERE LOWER(first_name) LIKE LOWER(?)
               OR LOWER(last_name) LIKE LOWER(?)
            ORDER BY last_name ASC, first_name ASC, id ASC
            """,
            (search_text, search_text),
        )

        rows = cursor.fetchall()
        connection.close()

        residents = []

        for row in rows:
            resident = Resident(
                first_name=row[1],
                last_name=row[2],
                address=row[3],
                contact_number=row[4],
                email=row[5],
                status=row[6],
                id=row[0],
            )
            residents.append(resident)

        return residents