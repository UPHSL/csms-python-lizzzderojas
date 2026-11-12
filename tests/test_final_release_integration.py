"""Final release integration coverage across persisted CSMS workflows."""

from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


def test_registered_resident_request_completion_updates_persisted_dashboard(
    client,
    app,
):
    """Resident registration, request workflow, persistence, and dashboard agree."""
    registration = client.post(
        "/residents/register",
        data={
            "first_name": "Mina",
            "last_name": "Santos",
            "address": "12 Mabini Street",
            "contact_number": "09928345735",
            "email": "mina@example.com",
        },
    )
    assert registration.status_code == 302

    resident_repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )
    resident = resident_repository.find_all()[0]
    assert resident.status == "Active"

    submission = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(resident.id),
            "service_type": "Community transport",
            "description": "Transport to the health center",
            "date_requested": "2026-11-12",
        },
    )
    assert submission.status_code == 302
    detail_url = submission.headers["Location"]
    request_id = int(detail_url.rstrip("/").split("/")[-1])

    request_repository = ServiceRequestRepository(
        database_file=app.config["DATABASE"]
    )
    saved_request = request_repository.find_by_id(request_id)
    assert saved_request.resident_id == resident.id
    assert saved_request.status == "Pending"
    detail_page = client.get(detail_url)
    assert detail_page.status_code == 200
    assert b"Mina Santos" in detail_page.data
    assert b"v1.0.0" in detail_page.data

    for target_status in ("In Progress", "Completed"):
        transition = client.post(
            f"/service-requests/{request_id}/status",
            data={"status": target_status},
        )
        assert transition.status_code == 302
        assert request_repository.find_by_id(request_id).status == target_status

    rejected_transition = client.post(
        f"/service-requests/{request_id}/status",
        data={"status": "In Progress"},
    )
    assert rejected_transition.status_code == 302
    assert request_repository.find_by_id(request_id).status == "Completed"

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"Completed</span><strong>1</strong>" in dashboard.data
    assert b"Pending</span><strong>0</strong>" in dashboard.data
    assert b"Open Service Requests</span><strong>0</strong>" in dashboard.data
    assert b"Community transport" in dashboard.data