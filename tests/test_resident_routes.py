"""Tests for the Resident Management web routes."""

from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository


def create_resident(app, first_name="Liz", last_name="De Rojas"):
    """Create a sample resident for route tests."""
    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )

    resident = Resident(
        first_name=first_name,
        last_name=last_name,
        address="Biñan, Laguna",
        contact_number="09123456789",
        email="liz@example.com",
    )

    return repository.save(resident)


def test_resident_list_page_loads(client):
    response = client.get("/residents")

    assert response.status_code == 200
    assert b"Resident Management" in response.data


def test_resident_list_displays_registered_resident(client, app):
    create_resident(app)

    response = client.get("/residents")

    assert response.status_code == 200
    assert b"Liz" in response.data
    assert b"De Rojas" in response.data


def test_resident_search_finds_partial_first_name(client, app):
    create_resident(app)

    response = client.get("/residents?q=li")

    assert response.status_code == 200
    assert b"Liz" in response.data


def test_resident_search_is_case_insensitive(client, app):
    create_resident(app)

    response = client.get("/residents?q=LIZ")

    assert response.status_code == 200
    assert b"Liz" in response.data


def test_blank_search_displays_all_residents(client, app):
    create_resident(app, "Liz", "De Rojas")
    create_resident(app, "Peter", "Parker")

    response = client.get("/residents?q=")

    assert response.status_code == 200
    assert b"Liz" in response.data
    assert b"Peter" in response.data


def test_register_page_loads(client):
    response = client.get("/residents/register")

    assert response.status_code == 200
    assert b"Register Resident" in response.data


def test_valid_registration_creates_active_resident(client, app):
    response = client.post(
        "/residents/register",
        data={
            "first_name": "Peter",
            "last_name": "Parker",
            "address": "Biñan, Laguna",
            "contact_number": "09123456789",
            "email": "peter@example.com",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/residents")

    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )
    residents = repository.find_all()

    assert len(residents) == 1
    assert residents[0].first_name == "Peter"
    assert residents[0].status == "Active"


def test_invalid_registration_preserves_form_values(client, app):
    response = client.post(
        "/residents/register",
        data={
            "first_name": "",
            "last_name": "Parker",
            "address": "Biñan, Laguna",
            "contact_number": "123",
            "email": "invalid-email",
        },
    )

    assert response.status_code == 400
    assert b"First name is required." in response.data
    assert b' value="Parker"' in response.data
    assert b"invalid-email" in response.data

    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )
    assert repository.find_all() == []


def test_edit_page_displays_resident_information(client, app):
    resident = create_resident(app)

    response = client.get(f"/residents/{resident.id}/edit")

    assert response.status_code == 200
    assert b"Liz" in response.data
    assert b"De Rojas" in response.data
    assert str(resident.id).encode() in response.data
    assert b"readonly" in response.data


def test_valid_edit_updates_allowed_fields(client, app):
    resident = create_resident(app)

    response = client.post(
        f"/residents/{resident.id}/edit",
        data={
            "first_name": "Elizabeth",
            "last_name": "Rojas",
            "address": "Santa Rosa, Laguna",
            "contact_number": "09987654321",
            "email": "elizabeth@example.com",
        },
    )

    assert response.status_code == 302

    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )
    updated = repository.find_by_id(resident.id)

    assert updated.first_name == "Elizabeth"
    assert updated.last_name == "Rojas"
    assert updated.address == "Santa Rosa, Laguna"
    assert updated.contact_number == "09987654321"
    assert updated.email == "elizabeth@example.com"
    assert updated.id == resident.id
    assert updated.status == "Active"


def test_invalid_edit_preserves_submitted_values(client, app):
    resident = create_resident(app)

    response = client.post(
        f"/residents/{resident.id}/edit",
        data={
            "first_name": "",
            "last_name": "Updated",
            "address": "Biñan, Laguna",
            "contact_number": "123",
            "email": "invalid-email",
        },
    )

    assert response.status_code == 400
    assert b"First name is required." in response.data
    assert b' value="Updated"' in response.data

    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )
    unchanged = repository.find_by_id(resident.id)

    assert unchanged.first_name == "Liz"
    assert unchanged.last_name == "De Rojas"


def test_edit_missing_resident_returns_404(client):
    response = client.get("/residents/9999/edit")

    assert response.status_code == 404


def test_deactivate_resident_changes_status_to_inactive(client, app):
    resident = create_resident(app)

    response = client.post(
        f"/residents/{resident.id}/deactivate"
    )

    assert response.status_code == 302

    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )
    deactivated = repository.find_by_id(resident.id)

    assert deactivated.status == "Inactive"


def test_inactive_resident_remains_visible_without_deactivate_action(
    client,
    app,
):
    resident = create_resident(app)

    client.post(f"/residents/{resident.id}/deactivate")

    response = client.get("/residents")

    assert response.status_code == 200
    assert b"Liz" in response.data
    assert b"Inactive" in response.data
    assert b"No action available" in response.data


def test_get_deactivation_is_not_allowed(client, app):
    resident = create_resident(app)

    response = client.get(
        f"/residents/{resident.id}/deactivate"
    )

    assert response.status_code == 405

    repository = ResidentRepository(
        database_file=app.config["DATABASE"]
    )
    unchanged = repository.find_by_id(resident.id)

    assert unchanged.status == "Active"
    