from csms.database import initialize_database
from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.request_service import ServiceRequestSubmissionService


def create_submission_service(tmp_path):
    """Create a submission service that uses a temporary database."""
    database_file = tmp_path / "test.db"

    initialize_database(database_file)

    resident_repository = ResidentRepository(database_file)
    service_request_repository = ServiceRequestRepository(database_file)

    submission_service = ServiceRequestSubmissionService(
        service_request_repository=service_request_repository,
        resident_repository=resident_repository,
    )

    return (
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


def test_valid_service_request_submission_succeeds(tmp_path):
    service, resident_repository, _ = create_submission_service(tmp_path)

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Barangay Clearance",
        description="Request for barangay clearance",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    assert result["success"] is True
    assert result["errors"] == []
    assert result["service_request"] is not None


def test_service_request_receives_generated_id(tmp_path):
    service, resident_repository, _ = create_submission_service(tmp_path)

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Certificate",
        description="Request for certificate",
        date_requested="2026-10-01",
    )

    assert service_request.id is None

    result = service.submit(service_request)

    assert result["service_request"].id is not None


def test_submitted_service_request_can_be_retrieved_by_id(tmp_path):
    service, resident_repository, service_request_repository = (
        create_submission_service(tmp_path)
    )

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Assistance",
        description="Request for assistance",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    saved_request = result["service_request"]

    found_request = service_request_repository.find_by_id(
        saved_request.id
    )

    assert found_request is not None
    assert found_request.id == saved_request.id


def test_service_request_information_is_preserved(tmp_path):
    service, resident_repository, service_request_repository = (
        create_submission_service(tmp_path)
    )

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Medical Assistance",
        description="Request for medical assistance",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    saved_request = service_request_repository.find_by_id(
        result["service_request"].id
    )

    assert saved_request.resident_id == resident.id
    assert saved_request.service_type == "Medical Assistance"
    assert saved_request.description == "Request for medical assistance"
    assert saved_request.date_requested == "2026-10-01"


def test_new_service_request_is_pending(tmp_path):
    service, resident_repository, _ = create_submission_service(tmp_path)

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Assistance",
        description="Request for assistance",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    assert result["service_request"].status == "Pending"


def test_blank_service_type_fails(tmp_path):
    service, resident_repository, _ = create_submission_service(tmp_path)

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="   ",
        description="Valid description",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    assert result["success"] is False
    assert "service_type" in result["errors"]
    assert result["service_request"] is None


def test_blank_description_fails(tmp_path):
    service, resident_repository, _ = create_submission_service(tmp_path)

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Assistance",
        description="   ",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    assert result["success"] is False
    assert "description" in result["errors"]
    assert result["service_request"] is None


def test_invalid_request_does_not_persist(tmp_path):
    service, resident_repository, service_request_repository = (
        create_submission_service(tmp_path)
    )

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="   ",
        description="Valid description",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    assert result["success"] is False
    assert result["service_request"] is None
    assert service_request.id is None

    saved_request = service_request_repository.find_by_id(1)

    assert saved_request is None


def test_nonexistent_resident_blocks_submission(tmp_path):
    service, _, service_request_repository = create_submission_service(
        tmp_path
    )

    service_request = ServiceRequest(
        resident_id=999999,
        service_type="Assistance",
        description="Request for assistance",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    assert result["success"] is False
    assert result["reason"] == "resident_not_found"
    assert result["service_request"] is None
    assert service_request.id is None

    saved_request = service_request_repository.find_by_id(1)

    assert saved_request is None


def test_inactive_resident_blocks_submission(tmp_path):
    service, resident_repository, service_request_repository = (
        create_submission_service(tmp_path)
    )

    resident = Resident(
        "Ana",
        "Garcia",
        "Laguna",
        "09181234567",
        "ana@example.com",
        "Inactive",
    )

    resident_repository.save(resident)

    result = service.submit(
        ServiceRequest(
            resident_id=resident.id,
            service_type="Assistance",
            description="Request for assistance",
            date_requested="2026-10-01",
        )
    )

    assert result["success"] is False
    assert result["reason"] == "resident_inactive"
    assert result["service_request"] is None

    saved_resident = resident_repository.find_by_id(resident.id)

    assert saved_resident.status == "Inactive"

    saved_request = service_request_repository.find_by_id(1)

    assert saved_request is None


def test_non_pending_status_is_rejected(tmp_path):
    service, resident_repository, service_request_repository = (
        create_submission_service(tmp_path)
    )

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Assistance",
        description="Request for assistance",
        date_requested="2026-10-01",
        status="Approved",
    )

    result = service.submit(service_request)

    assert result["success"] is False
    assert "status" in result["errors"]
    assert result["service_request"] is None

    saved_request = service_request_repository.find_by_id(1)

    assert saved_request is None


def test_service_request_persists_across_repository_access(tmp_path):
    service, resident_repository, _ = create_submission_service(tmp_path)

    resident = create_active_resident(resident_repository)

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Clearance",
        description="Request for clearance",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    saved_request = result["service_request"]

    database_file = tmp_path / "test.db"

    second_repository = ServiceRequestRepository(database_file)

    found_request = second_repository.find_by_id(saved_request.id)

    assert found_request is not None
    assert found_request.id == saved_request.id


def test_resident_remains_unchanged_after_submission(tmp_path):
    service, resident_repository, _ = create_submission_service(tmp_path)

    resident = create_active_resident(resident_repository)

    original_status = resident.status

    service_request = ServiceRequest(
        resident_id=resident.id,
        service_type="Assistance",
        description="Request for assistance",
        date_requested="2026-10-01",
    )

    result = service.submit(service_request)

    assert result["success"] is True

    saved_resident = resident_repository.find_by_id(resident.id)

    assert saved_resident.status == original_status
