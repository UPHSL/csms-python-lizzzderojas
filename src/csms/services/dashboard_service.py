"""Service for retrieving CSMS dashboard summaries."""


class DashboardService:
    """Combine Resident and Service Request dashboard data."""

    def __init__(
        self,
        resident_repository,
        service_request_repository,
    ):
        self.resident_repository = resident_repository
        self.service_request_repository = service_request_repository

    def get_dashboard_data(self):
        """Retrieve dashboard summaries and recent requests."""

        total_residents = (
            self.resident_repository.count_all_residents()
        )
        active_residents = (
            self.resident_repository.count_residents_by_status(
                "Active"
            )
        )
        inactive_residents = (
            self.resident_repository.count_residents_by_status(
                "Inactive"
            )
        )

        total_requests = (
            self.service_request_repository.count_all_service_requests()
        )
        pending_requests = (
            self.service_request_repository
            .count_service_requests_by_status("Pending")
        )
        in_progress_requests = (
            self.service_request_repository
            .count_service_requests_by_status("In Progress")
        )
        completed_requests = (
            self.service_request_repository
            .count_service_requests_by_status("Completed")
        )
        cancelled_requests = (
            self.service_request_repository
            .count_service_requests_by_status("Cancelled")
        )

        open_requests = pending_requests + in_progress_requests

        recent_requests = (
            self.service_request_repository
            .find_recent_service_requests(limit=5)
        )

        return {
            "resident_stats": {
                "total": total_residents,
                "active": active_residents,
                "inactive": inactive_residents,
            },
            "service_request_stats": {
                "total": total_requests,
                "pending": pending_requests,
                "in_progress": in_progress_requests,
                "completed": completed_requests,
                "cancelled": cancelled_requests,
                "open": open_requests,
            },
            "recent_requests": recent_requests,
        }