
"""Service for querying and viewing ServiceRequest records."""

from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


class ServiceRequestQueryService:
    """Handle read-only ServiceRequest queries."""

    SUPPORTED_STATUSES = {
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    def __init__(self, service_request_repository=None):
        self.service_request_repository = (
            service_request_repository
            or ServiceRequestRepository()
        )

    def find_all(self):
        """Return all ServiceRequests."""
        return self.service_request_repository.find_all()

    def find_by_id(self, service_request_id):
        """Return one ServiceRequest or None if it does not exist."""
        return self.service_request_repository.find_by_id(
            service_request_id
        )

    def search(self, query=None, status=None):
        """Search and filter ServiceRequests without changing records."""
        search_text = (query or "").strip()
        selected_status = (status or "").strip()

        if selected_status and selected_status not in self.SUPPORTED_STATUSES:
            raise ValueError("unsupported_status")

        if search_text and selected_status:
            return (
                self.service_request_repository.search_by_text_and_status(
                    search_text,
                    selected_status,
                )
            )

        if search_text:
            return self.service_request_repository.search(search_text)

        if selected_status:
            return self.service_request_repository.find_by_status(
                selected_status
            )

        return self.find_all()
