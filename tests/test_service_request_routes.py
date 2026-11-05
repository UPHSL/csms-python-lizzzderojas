
"""Tests for the Service Request Management web routes."""

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


def create_resident(app, status="Active"):
    """Create and save a sample resident."""
    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )

    resident = Resident(
        "Liz",
        "De Rojas",
        "Biñan, Laguna",
        "09123456789",
        "liz@example.com",
        status,
    )

    return repository.save(resident)


def create_request(
    app,
    resident_id,
    service_type="Barangay Clearance",
    description="Request for barangay clearance",
    date_requested="2026-10-01",
    status="Pending",
):
    """Create and save a sample service request."""
    repository = ServiceRequestRepository(
        database_file=app.config["DATABASE"]
    )

    service_request = ServiceRequest(
        resident_id=resident_id,
        service_type=service_type,
        description=description,
        date_requested=date_requested,
        status=status,
    )

    return repository.save(service_request)


def get_request_repository(app):
    """Return the Service Request repository."""
    return ServiceRequestRepository(
        database_file=app.config["DATABASE"]
    )


# LIST AND SEARCH TESTS


def test_service_request_list_page_loads(client):
    response = client.get("/service-requests")

    assert response.status_code == 200
    assert b"Service Request Management" in response.data


def test_empty_service_request_list_displays_message(client):
    response = client.get("/service-requests")

    assert response.status_code == 200
    assert b"No Service Requests found." in response.data


def test_service_request_list_displays_saved_request(client, app):
    resident = create_resident(app)
    create_request(app, resident.id)

    response = client.get("/service-requests")

    assert response.status_code == 200
    assert b"Barangay Clearance" in response.data


def test_service_request_list_displays_required_columns(client):
    response = client.get("/service-requests")

    assert b"Resident ID" in response.data
    assert b"Service Type" in response.data
    assert b"Date Requested" in response.data
    assert b"Status" in response.data
    assert b"Actions" in response.data


def test_service_request_list_uses_newest_first_order(client, app):
    resident = create_resident(app)

    older = create_request(
        app,
        resident.id,
        service_type="Older Request",
        date_requested="2026-09-01",
    )
    newer = create_request(
        app,
        resident.id,
        service_type="Newer Request",
        date_requested="2026-10-01",
    )

    response = client.get("/service-requests")

    assert response.status_code == 200
    assert response.data.index(b"Newer Request") < response.data.index(
        b"Older Request"
    )


def test_service_request_search_finds_partial_service_type(client, app):
    resident = create_resident(app)
    create_request(app, resident.id)

    response = client.get("/service-requests?q=Clear")

    assert response.status_code == 200
    assert b"Barangay Clearance" in response.data


def test_service_request_search_finds_description(client, app):
    resident = create_resident(app)
    create_request(
        app,
        resident.id,
        description="Request for medical assistance",
    )

    response = client.get("/service-requests?q=MEDICAL")

    assert response.status_code == 200
    assert b"Barangay Clearance" in response.data


def test_blank_search_displays_all_service_requests(client, app):
    resident = create_resident(app)
    create_request(app, resident.id, service_type="Clearance")
    create_request(app, resident.id, service_type="Medical Assistance")

    response = client.get("/service-requests?q=")

    assert response.status_code == 200
    assert b"Clearance" in response.data
    assert b"Medical Assistance" in response.data


def test_service_request_status_filter_displays_matching_records(
    client,
    app,
):
    resident = create_resident(app)
    create_request(app, resident.id, status="Pending")
    create_request(
        app,
        resident.id,
        service_type="Completed Request",
        status="Completed",
    )

    response = client.get("/service-requests?status=Completed")

    assert response.status_code == 200
    assert b"Completed Request" in response.data
    assert b"Barangay Clearance" not in response.data


def test_service_request_search_and_status_filter_work_together(
    client,
    app,
):
    resident = create_resident(app)

    create_request(
        app,
        resident.id,
        service_type="Medical Assistance",
        status="Pending",
    )
    create_request(
        app,
        resident.id,
        service_type="Medical Clearance",
        status="Completed",
    )

    response = client.get(
        "/service-requests?q=Medical&status=Completed"
    )

    assert response.status_code == 200
    assert b"Medical Clearance" in response.data
    assert b"Medical Assistance" not in response.data


def test_invalid_service_request_status_filter_returns_400(client):
    response = client.get("/service-requests?status=Unknown")

    assert response.status_code == 400


# SUBMISSION FORM TESTS


def test_new_service_request_form_loads(client):
    response = client.get("/service-requests/new")

    assert response.status_code == 200
    assert b"New Service Request" in response.data


def test_submission_form_does_not_expose_id_or_status_fields(client):
    response = client.get("/service-requests/new")

    assert response.status_code == 200
    assert b'name="resident_id"' in response.data
    assert b'name="service_type"' in response.data
    assert b'name="description"' in response.data
    assert b'name="date_requested"' in response.data
    assert b'name="status"' not in response.data
    assert b'name="id"' not in response.data


def test_valid_submission_creates_pending_request(client, app):
    resident = create_resident(app)

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Medical Assistance",
            "description": "Request for medical support",
            "date_requested": "2026-10-01",
        },
    )

    assert response.status_code == 302
    assert "/service-requests/" in response.headers["Location"]

    repository = get_request_repository(app)
    requests = repository.find_all()

    assert len(requests) == 1
    assert requests[0].resident_id == resident.id
    assert requests[0].service_type == "Medical Assistance"
    assert requests[0].status == "Pending"


def test_invalid_submission_preserves_values_and_does_not_save(
    client,
    app,
):
    resident = create_resident(app)

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "",
            "description": "My submitted description",
            "date_requested": "2026-10-01",
        },
    )

    assert response.status_code == 400
    assert b"Service Type is required." in response.data
    assert b"My submitted description" in response.data

    repository = get_request_repository(app)
    assert repository.find_all() == []


def test_submission_rejects_invalid_resident_id(client, app):
    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": "invalid",
            "service_type": "Clearance",
            "description": "Request for clearance",
            "date_requested": "2026-10-01",
        },
    )

    assert response.status_code == 400
    assert b"valid positive Resident ID" in response.data
    assert get_request_repository(app).find_all() == []


def test_submission_rejects_nonexistent_resident(client, app):
    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": "999999",
            "service_type": "Clearance",
            "description": "Request for clearance",
            "date_requested": "2026-10-01",
        },
    )

    assert response.status_code == 400
    assert b"specified Resident does not exist" in response.data
    assert get_request_repository(app).find_all() == []


def test_submission_rejects_inactive_resident(client, app):
    resident = create_resident(app, status="Inactive")

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Clearance",
            "description": "Request for clearance",
            "date_requested": "2026-10-01",
        },
    )

    assert response.status_code == 400
    assert b"only be submitted for active Residents" in response.data
    assert get_request_repository(app).find_all() == []


# DETAILS PAGE TESTS


def test_service_request_details_page_displays_request(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.get(
        f"/service-requests/{service_request.id}"
    )

    assert response.status_code == 200
    assert b"Service Request Details" in response.data
    assert b"Barangay Clearance" in response.data
    assert b"Request for barangay clearance" in response.data
    assert b"Pending" in response.data


def test_unknown_service_request_details_returns_404(client):
    response = client.get("/service-requests/999999")

    assert response.status_code == 404


# STATUS WORKFLOW TESTS


def test_pending_request_can_start_processing(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "In Progress"},
    )

    assert response.status_code == 302

    saved_request = get_request_repository(app).find_by_id(
        service_request.id
    )
    assert saved_request.status == "In Progress"


def test_pending_request_can_be_cancelled(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "Cancelled"},
    )

    assert response.status_code == 302

    saved_request = get_request_repository(app).find_by_id(
        service_request.id
    )
    assert saved_request.status == "Cancelled"


def test_in_progress_request_can_be_completed(client, app):
    resident = create_resident(app)
    service_request = create_request(
        app,
        resident.id,
        status="In Progress",
    )

    response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "Completed"},
    )

    assert response.status_code == 302

    saved_request = get_request_repository(app).find_by_id(
        service_request.id
    )
    assert saved_request.status == "Completed"


def test_in_progress_request_can_be_cancelled(client, app):
    resident = create_resident(app)
    service_request = create_request(
        app,
        resident.id,
        status="In Progress",
    )

    response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "Cancelled"},
    )

    assert response.status_code == 302

    saved_request = get_request_repository(app).find_by_id(
        service_request.id
    )
    assert saved_request.status == "Cancelled"


def test_invalid_status_transition_does_not_update_request(
    client,
    app,
):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "Completed"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"That status change is not allowed." in response.data

    saved_request = get_request_repository(app).find_by_id(
        service_request.id
    )
    assert saved_request.status == "Pending"


def test_terminal_request_displays_no_status_action_buttons(
    client,
    app,
):
    resident = create_resident(app)
    service_request = create_request(
        app,
        resident.id,
        status="Completed",
    )

    response = client.get(
        f"/service-requests/{service_request.id}"
    )

    assert response.status_code == 200
    assert b"terminal status" in response.data
    assert b"Start Processing" not in response.data
    assert b"Complete Request" not in response.data
    assert b"Cancel Request" not in response.data


def test_status_update_route_does_not_allow_get(client, app):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    response = client.get(
        f"/service-requests/{service_request.id}/status"
    )

    assert response.status_code == 405


def test_status_update_for_unknown_request_returns_404(client):
    response = client.post(
        "/service-requests/999999/status",
        data={"status": "In Progress"},
    )

    assert response.status_code == 404


def test_status_update_preserves_other_request_information(
    client,
    app,
):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    original_id = service_request.id

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "In Progress"},
    )

    saved_request = get_request_repository(app).find_by_id(
        original_id
    )

    assert saved_request.id == original_id
    assert saved_request.resident_id == resident.id
    assert saved_request.service_type == "Barangay Clearance"
    assert saved_request.description == "Request for barangay clearance"
    assert saved_request.date_requested == "2026-10-01"
    assert saved_request.status == "In Progress"
