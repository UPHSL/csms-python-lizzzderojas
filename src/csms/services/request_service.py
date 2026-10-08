"""Service for validating and submitting ServiceRequest records."""

from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.service_request_validator import ServiceRequestValidator


class ServiceRequestSubmissionService:
    """Handle ServiceRequest validation and submission."""

    def __init__(
        self,
        service_request_repository=None,
        resident_repository=None,
        validator=None,
    ):
        self.service_request_repository = (
            service_request_repository
            or ServiceRequestRepository()
        )
        self.resident_repository = (
            resident_repository
            or ResidentRepository()
        )
        self.validator = (
            validator
            or ServiceRequestValidator()
        )

    def submit(self, service_request):
        """Validate and submit a ServiceRequest."""
        validation_errors = self.validator.validate(
            service_request
        )

        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "service_request": None,
                "reason": "validation_failed",
            }

        resident = self.resident_repository.find_by_id(
            service_request.resident_id
        )

        if resident is None:
            return {
                "success": False,
                "errors": ["resident_not_found"],
                "service_request": None,
                "reason": "resident_not_found",
            }

        if resident.status != "Active":
            return {
                "success": False,
                "errors": ["resident_inactive"],
                "service_request": None,
                "reason": "resident_inactive",
            }

        service_request.status = "Pending"

        saved_request = self.service_request_repository.save(
            service_request
        )

        return {
            "success": True,
            "errors": [],
            "service_request": saved_request,
            "reason": None,
        }


class ServiceRequestStatusService:
    """Handle ServiceRequest status transitions."""

    SUPPORTED_STATUSES = {
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    ALLOWED_TRANSITIONS = {
        "Pending": {"In Progress", "Cancelled"},
        "In Progress": {"Completed", "Cancelled"},
        "Completed": set(),
        "Cancelled": set(),
    }

    def __init__(self, service_request_repository=None):
        self.service_request_repository = (
            service_request_repository
            or ServiceRequestRepository()
        )

    def update_status(self, service_request_id, target_status):
        """Validate and update a ServiceRequest status."""
        service_request = self.service_request_repository.find_by_id(
            service_request_id
        )

        if service_request is None:
            return {
                "success": False,
                "errors": ["service_request_not_found"],
                "service_request": None,
                "reason": "service_request_not_found",
            }

        if target_status not in self.SUPPORTED_STATUSES:
            return {
                "success": False,
                "errors": ["unsupported_status"],
                "service_request": service_request,
                "reason": "unsupported_status",
            }

        current_status = service_request.status

        if target_status not in self.ALLOWED_TRANSITIONS[current_status]:
            return {
                "success": False,
                "errors": ["invalid_transition"],
                "service_request": service_request,
                "reason": "invalid_transition",
            }

        self.service_request_repository.update_status(
            service_request_id,
            target_status,
        )

        updated_request = self.service_request_repository.find_by_id(
            service_request_id
        )

        return {
            "success": True,
            "errors": [],
            "service_request": updated_request,
            "reason": None,
        }
