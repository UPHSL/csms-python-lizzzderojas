from datetime import date

from csms.models.service_request import ServiceRequest


def test_service_request_can_be_created():
    request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Request for employment requirement",
        date_requested=date(2026, 9, 29),
    )

    assert request is not None


def test_service_request_information_is_accessible():
    request_date = date(2026, 9, 29)

    request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Request for employment requirement",
        date_requested=request_date,
    )

    assert request.resident_id == 25
    assert request.service_type == "Barangay Clearance"
    assert request.description == "Request for employment requirement"
    assert request.date_requested == request_date


def test_service_request_preserves_resident_id():
    request = ServiceRequest(
        resident_id=25,
        service_type="Certificate Request",
        description="Request for a certificate",
        date_requested=date(2026, 9, 29),
    )

    assert request.resident_id == 25


def test_new_service_request_has_unassigned_id():
    request = ServiceRequest(
        resident_id=25,
        service_type="Permit Request",
        description="Request for a permit",
        date_requested=date(2026, 9, 29),
    )

    assert request.id is None


def test_new_service_request_defaults_to_pending():
    request = ServiceRequest(
        resident_id=25,
        service_type="Community Assistance",
        description="Request for community assistance",
        date_requested=date(2026, 9, 29),
    )

    assert request.status == "Pending"


def test_service_request_objects_are_independent():
    first_request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Employment requirement",
        date_requested=date(2026, 9, 29),
    )

    second_request = ServiceRequest(
        resident_id=30,
        service_type="Certificate Request",
        description="Personal requirement",
        date_requested=date(2026, 9, 30),
    )

    assert first_request.resident_id == 25
    assert first_request.service_type == "Barangay Clearance"
    assert first_request.description == "Employment requirement"
    assert first_request.date_requested == date(2026, 9, 29)

    assert second_request.resident_id == 30
    assert second_request.service_type == "Certificate Request"
    assert second_request.description == "Personal requirement"
    assert second_request.date_requested == date(2026, 9, 30)
    