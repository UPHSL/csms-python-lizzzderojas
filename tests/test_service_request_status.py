from csms.database import initialize_database
from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.request_service import (
    ServiceRequestStatusService,
    ServiceRequestSubmissionService,
)


def create_status_service(tmp_path):
    """Create a status service that uses a temporary database."""
    database_file = tmp_path / "test.db"

    initialize_database(database_file)

    resident_repository = ResidentRepository(database_file)
    service_request_repository = ServiceRequestRepository(database_file)

    submission_service = ServiceRequestSubmissionService(
        service_request_repository=service_request_repository,
        resident_repository=resident_repository,
    )

    status_service = ServiceRequestStatusService(
        service_request_repository=service_request_repository,
    )

    return (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    )


def create_active_resident(repository):
    """Create and save an active resident for testing."""
    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Laguna",
        "09171234567",
        "juan@example.com",
        "Active",
    )

    return repository.save(resident)


def create_service_request(submission_service, resident_id):
    """Create and save a pending service request."""
    service_request = ServiceRequest(
        resident_id=resident_id,
        service_type="Barangay Clearance",
        description="Request for barangay clearance",
        date_requested="2026-10-01",
    )

    result = submission_service.submit(service_request)

    return result["service_request"]

def test_pending_can_change_to_in_progress(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    result = status_service.update_status(
        service_request.id,
        "In Progress",
    )

    assert result["success"] is True
    assert result["reason"] is None
    assert result["service_request"].status == "In Progress"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "In Progress"


def test_pending_can_change_to_cancelled(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    result = status_service.update_status(
        service_request.id,
        "Cancelled",
    )

    assert result["success"] is True
    assert result["reason"] is None
    assert result["service_request"].status == "Cancelled"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Cancelled"

def test_in_progress_can_change_to_completed_through_workflow(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    first_result = status_service.update_status(
        service_request.id,
        "In Progress",
    )

    assert first_result["success"] is True
    assert first_result["service_request"].status == "In Progress"

    second_result = status_service.update_status(
        service_request.id,
        "Completed",
    )

    assert second_result["success"] is True
    assert second_result["reason"] is None
    assert second_result["service_request"].status == "Completed"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Completed"

def test_in_progress_can_change_to_cancelled(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    first_result = status_service.update_status(
        service_request.id,
        "In Progress",
    )

    assert first_result["success"] is True
    assert first_result["service_request"].status == "In Progress"

    second_result = status_service.update_status(
        service_request.id,
        "Cancelled",
    )

    assert second_result["success"] is True
    assert second_result["reason"] is None
    assert second_result["service_request"].status == "Cancelled"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Cancelled"

def test_pending_cannot_change_directly_to_completed(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    result = status_service.update_status(
        service_request.id,
        "Completed",
    )

    assert result["success"] is False
    assert result["reason"] == "invalid_transition"
    assert result["service_request"].status == "Pending"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Pending"

def test_in_progress_cannot_change_back_to_pending(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    first_result = status_service.update_status(
        service_request.id,
        "In Progress",
    )

    assert first_result["success"] is True

    result = status_service.update_status(
        service_request.id,
        "Pending",
    )

    assert result["success"] is False
    assert result["reason"] == "invalid_transition"
    assert result["service_request"].status == "In Progress"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "In Progress"

def test_completed_status_is_terminal(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    status_service.update_status(
        service_request.id,
        "In Progress",
    )

    completed_result = status_service.update_status(
        service_request.id,
        "Completed",
    )

    assert completed_result["success"] is True
    assert completed_result["service_request"].status == "Completed"

    result = status_service.update_status(
        service_request.id,
        "Cancelled",
    )

    assert result["success"] is False
    assert result["reason"] == "invalid_transition"
    assert result["service_request"].status == "Completed"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Completed"

def test_cancelled_status_is_terminal(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    cancelled_result = status_service.update_status(
        service_request.id,
        "Cancelled",
    )

    assert cancelled_result["success"] is True
    assert cancelled_result["service_request"].status == "Cancelled"

    result = status_service.update_status(
        service_request.id,
        "In Progress",
    )

    assert result["success"] is False
    assert result["reason"] == "invalid_transition"
    assert result["service_request"].status == "Cancelled"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Cancelled"

def test_unsupported_status_is_rejected(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    result = status_service.update_status(
        service_request.id,
        "Approved",
    )

    assert result["success"] is False
    assert result["reason"] == "unsupported_status"
    assert result["service_request"].status == "Pending"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Pending"

def test_nonexistent_service_request_id_is_handled(tmp_path):
    (
        status_service,
        _,
        _,
        service_request_repository,
    ) = create_status_service(tmp_path)

    result = status_service.update_status(
        999999,
        "In Progress",
    )

    assert result["success"] is False
    assert result["reason"] == "service_request_not_found"
    assert result["service_request"] is None

    saved_request = service_request_repository.find_by_id(999999)

    assert saved_request is None

def test_valid_transition_preserves_non_status_fields(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    original_id = service_request.id
    original_resident_id = service_request.resident_id
    original_service_type = service_request.service_type
    original_description = service_request.description
    original_date_requested = service_request.date_requested

    result = status_service.update_status(
        service_request.id,
        "In Progress",
    )

    assert result["success"] is True

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.id == original_id
    assert saved_request.resident_id == original_resident_id
    assert saved_request.service_type == original_service_type
    assert saved_request.description == original_description
    assert saved_request.date_requested == original_date_requested
    assert saved_request.status == "In Progress"

def test_invalid_transition_leaves_persistence_unchanged(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    before_request = service_request_repository.find_by_id(
        service_request.id
    )

    result = status_service.update_status(
        service_request.id,
        "Completed",
    )

    after_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert result["success"] is False
    assert result["reason"] == "invalid_transition"

    assert before_request.status == "Pending"
    assert after_request.status == "Pending"
    assert after_request.id == before_request.id
    assert after_request.resident_id == before_request.resident_id
    assert after_request.service_type == before_request.service_type
    assert after_request.description == before_request.description
    assert after_request.date_requested == before_request.date_requested

def test_same_status_request_is_rejected(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        service_request_repository,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    result = status_service.update_status(
        service_request.id,
        "Pending",
    )

    assert result["success"] is False
    assert result["reason"] == "invalid_transition"
    assert result["service_request"].status == "Pending"

    saved_request = service_request_repository.find_by_id(
        service_request.id
    )

    assert saved_request.status == "Pending"

def test_status_update_persists_across_repository_instances(tmp_path):
    (
        status_service,
        submission_service,
        resident_repository,
        _,
    ) = create_status_service(tmp_path)

    resident = create_active_resident(resident_repository)
    service_request = create_service_request(
        submission_service,
        resident.id,
    )

    result = status_service.update_status(
        service_request.id,
        "In Progress",
    )

    assert result["success"] is True

    database_file = tmp_path / "test.db"
    second_repository = ServiceRequestRepository(database_file)

    saved_request = second_repository.find_by_id(
        service_request.id
    )

    assert saved_request is not None
    assert saved_request.id == service_request.id
    assert saved_request.status == "In Progress"