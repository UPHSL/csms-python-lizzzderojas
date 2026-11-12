
"""Tests for the CSMS Dashboard."""

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


def create_resident(app, first_name="Liz", status="Active"):
    """Create and save a sample resident."""
    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )

    resident = Resident(
        first_name,
        "De Rojas",
        "Biñan, Laguna",
        "09123456789",
        f"{first_name.lower().replace(' ', '.')}@example.com",
        status,
    )

    return repository.save(resident)


def create_request(
    app,
    resident_id,
    service_type="Barangay Clearance",
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
        description="Sample service request",
        date_requested=date_requested,
        status=status,
    )

    return repository.save(service_request)


def get_resident_repository(app):
    """Return the Resident repository."""
    return ResidentRepository(
        database_file=app.config["DATABASE"]
    )


def get_request_repository(app):
    """Return the Service Request repository."""
    return ServiceRequestRepository(
        database_file=app.config["DATABASE"]
    )


def test_dashboard_page_loads(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Resident Summary" in response.data
    assert b"Service Request Summary" in response.data


def test_empty_dashboard_displays_zero_counts(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Total Residents" in response.data
    assert b"Active Residents" in response.data
    assert b"Inactive Residents" in response.data
    assert b"Total Service Requests" in response.data
    assert b"No Service Requests available." in response.data

    for value in [
        b">0<",
        b">0</p>",
    ]:
        assert value in response.data


def test_dashboard_displays_correct_total_residents(client, app):
    create_resident(app, "Liz")
    create_resident(app, "Kenneth")
    create_resident(app, "Miguel")

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Total Residents" in response.data
    assert b">3<" in response.data


def test_resident_status_counts_are_correct_and_reconcile(
    client,
    app,
):
    create_resident(app, "Liz", "Active")
    create_resident(app, "Kenneth", "Active")
    create_resident(app, "Miguel", "Inactive")

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b">3<" in response.data
    assert b">2<" in response.data
    assert b">1<" in response.data


def test_dashboard_displays_correct_total_service_requests(
    client,
    app,
):
    resident = create_resident(app)

    create_request(app, resident.id, "Request One")
    create_request(app, resident.id, "Request Two")
    create_request(app, resident.id, "Request Three")

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Total Service Requests" in response.data
    assert b">3<" in response.data


def test_service_request_status_counts_are_correct(client, app):
    resident = create_resident(app)

    create_request(app, resident.id, "Request One", status="Pending")
    create_request(
        app, resident.id, "Request Two", status="In Progress"
    )
    create_request(
        app, resident.id, "Request Three", status="Completed"
    )
    create_request(
        app, resident.id, "Request Four", status="Cancelled"
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Pending" in response.data
    assert b"In Progress" in response.data
    assert b"Completed" in response.data
    assert b"Cancelled" in response.data


def test_service_request_counts_reconcile_with_total(client, app):
    resident = create_resident(app)

    create_request(app, resident.id, "Request One", status="Pending")
    create_request(
        app, resident.id, "Request Two", status="In Progress"
    )
    create_request(
        app, resident.id, "Request Three", status="Completed"
    )
    create_request(
        app, resident.id, "Request Four", status="Cancelled"
    )

    repository = get_request_repository(app)

    total = repository.count_all_service_requests()
    status_total = sum(
        repository.count_service_requests_by_status(status)
        for status in [
            "Pending",
            "In Progress",
            "Completed",
            "Cancelled",
        ]
    )

    assert total == 4
    assert status_total == total


def test_open_requests_include_only_pending_and_in_progress(
    client,
    app,
):
    resident = create_resident(app)

    create_request(app, resident.id, "Pending Request", status="Pending")
    create_request(
        app, resident.id, "Processing Request", status="In Progress"
    )
    create_request(
        app, resident.id, "Completed Request", status="Completed"
    )
    create_request(
        app, resident.id, "Cancelled Request", status="Cancelled"
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Open Service Requests" in response.data
    assert b"Pending Request" in response.data
    assert b"Processing Request" in response.data


def test_dashboard_reflects_resident_deactivation(client, app):
    resident = create_resident(app, "Liz")

    client.post(f"/residents/{resident.id}/deactivate")

    response = client.get("/dashboard")

    assert response.status_code == 200

    saved_resident = get_resident_repository(app).find_by_id(
        resident.id
    )

    assert saved_resident.status == "Inactive"
    assert b"Inactive Residents" in response.data


def test_dashboard_reflects_pending_to_in_progress_transition(
    client,
    app,
):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "In Progress"},
    )

    response = client.get("/dashboard")

    saved_request = get_request_repository(app).find_by_id(
        service_request.id
    )

    assert response.status_code == 200
    assert saved_request.status == "In Progress"


def test_terminal_transition_updates_open_count_without_changing_total(
    client,
    app,
):
    resident = create_resident(app)
    service_request = create_request(app, resident.id)

    repository = get_request_repository(app)
    original_total = repository.count_all_service_requests()

    client.post(
        f"/service-requests/{service_request.id}/status",
        data={"status": "Cancelled"},
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert repository.count_all_service_requests() == original_total
    assert (
        repository.count_service_requests_by_status("Pending")
        + repository.count_service_requests_by_status("In Progress")
        == 0
    )


def test_recent_requests_display_no_more_than_five(client, app):
    resident = create_resident(app)

    for number in range(1, 8):
        create_request(
            app,
            resident.id,
            service_type=f"Request {number}",
            date_requested=f"2026-10-{number:02d}",
        )

    response = client.get("/dashboard")

    assert response.status_code == 200

    for number in range(1, 3):
        assert f"Request {number}".encode() not in response.data

    for number in range(3, 8):
        assert f"Request {number}".encode() in response.data


def test_recent_requests_use_date_then_id_descending_order(
    client,
    app,
):
    resident = create_resident(app)

    create_request(
        app, resident.id, "Older Date", date_requested="2026-09-30"
    )
    create_request(
        app, resident.id, "Same Date First", date_requested="2026-10-01"
    )
    create_request(
        app, resident.id, "Same Date Second", date_requested="2026-10-01"
    )
    create_request(
        app, resident.id, "Newer Date", date_requested="2026-10-02"
    )

    response = client.get("/dashboard")

    assert response.status_code == 200

    positions = [
        response.data.index(name)
        for name in [
            b"Newer Date",
            b"Same Date Second",
            b"Same Date First",
            b"Older Date",
        ]
    ]

    assert positions == sorted(positions)


def test_recent_requests_can_include_completed_and_cancelled(
    client,
    app,
):
    resident = create_resident(app)

    create_request(
        app, resident.id, "Completed Request", status="Completed"
    )
    create_request(
        app, resident.id, "Cancelled Request", status="Cancelled"
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Completed Request" in response.data
    assert b"Cancelled Request" in response.data


def test_dashboard_get_does_not_modify_persisted_records(client, app):
    resident = create_resident(app)
    create_request(app, resident.id)

    resident_repository = get_resident_repository(app)
    request_repository = get_request_repository(app)

    residents_before = resident_repository.find_all()
    requests_before = request_repository.find_all()

    response = client.get("/dashboard")

    residents_after = resident_repository.find_all()
    requests_after = request_repository.find_all()

    assert response.status_code == 200

    assert [
        (r.id, r.first_name, r.last_name, r.status)
        for r in residents_before
    ] == [
        (r.id, r.first_name, r.last_name, r.status)
        for r in residents_after
    ]

    assert [
        (r.id, r.resident_id, r.service_type, r.status)
        for r in requests_before
    ] == [
        (r.id, r.resident_id, r.service_type, r.status)
        for r in requests_after
    ]
