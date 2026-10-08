"""Repository for storing and retrieving ServiceRequest records."""

import sqlite3

from csms.database import get_connection
from csms.models.service_request import ServiceRequest


class ServiceRequestRepository:
    """Handle ServiceRequest persistence in the database."""

    def __init__(self, database_file=None):
        self.database_file = database_file

    def get_connection(self):
        """Create a connection to the selected database."""
        if self.database_file is None:
            return get_connection()

        return sqlite3.connect(self.database_file)

    def save(self, service_request):
        """Save a ServiceRequest and assign the generated ID."""
        connection = self.get_connection()

        cursor = connection.execute(
            """
            INSERT INTO service_requests (
                resident_id,
                service_type,
                description,
                date_requested,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                service_request.resident_id,
                service_request.service_type,
                service_request.description,
                service_request.date_requested,
                service_request.status,
            ),
        )

        connection.commit()

        service_request.id = cursor.lastrowid

        connection.close()

        return service_request

    def find_by_id(self, service_request_id):
        """Find a ServiceRequest by ID."""
        connection = self.get_connection()

        cursor = connection.execute(
            """
            SELECT
                id,
                resident_id,
                service_type,
                description,
                date_requested,
                status
            FROM service_requests
            WHERE id = ?
            """,
            (service_request_id,),
        )

        row = cursor.fetchone()

        connection.close()

        if row is None:
            return None

        service_request = ServiceRequest(
            resident_id=row[1],
            service_type=row[2],
            description=row[3],
            date_requested=row[4],
            status=row[5],
            id=row[0],
        )

        return service_request

    def update_status(self, service_request_id, status):
        """Update only the status of an existing ServiceRequest."""
        connection = self.get_connection()

        connection.execute(
            """
            UPDATE service_requests
            SET status = ?
            WHERE id = ?
            """,
            (status, service_request_id),
        )

        connection.commit()

        connection.close()
