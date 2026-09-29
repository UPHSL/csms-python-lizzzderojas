from csms.database import initialize_database
from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_service import ResidentService
from csms.services.resident_validator import ResidentValidator


def create_service(tmp_path):
    database_file = tmp_path / "test.db"

    initialize_database(database_file)

    repository = ResidentRepository(
        database_file=database_file
    )
    validator = ResidentValidator()

    return ResidentService(repository, validator), repository

def test_register_valid_resident(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)

    assert errors == []
    assert registered is not None
    assert registered.first_name == "Juan"


def test_registered_resident_receives_generated_id(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)

    assert errors == []
    assert registered.id is not None


def test_valid_resident_is_persisted(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)
    saved_resident = repository.find_by_id(registered.id)

    assert errors == []
    assert saved_resident is not None
    assert saved_resident.id == registered.id


def test_resident_fields_are_preserved(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)
    saved_resident = repository.find_by_id(registered.id)

    assert errors == []
    assert saved_resident.first_name == "Juan"
    assert saved_resident.last_name == "Dela Cruz"
    assert saved_resident.address == "Brgy. Mamplasan, Binan, Laguna"
    assert saved_resident.contact_number == "09171234567"
    assert saved_resident.email == "juan@example.com"


def test_default_status_is_active(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)
    saved_resident = repository.find_by_id(registered.id)

    assert errors == []
    assert saved_resident.status == "Active"


def test_invalid_resident_registration_fails(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)

    assert registered is None
    assert errors != []


def test_invalid_resident_is_not_persisted(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)

    assert registered is None
    assert errors != []
    assert resident.id is None


def test_validation_failure_is_identified(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        first_name="",
        last_name="Dela Cruz",
        address="Brgy. Mamplasan, Binan, Laguna",
        contact_number="09171234567",
        email="juan@example.com",
    )

    registered, errors = service.register(resident)

    assert registered is None
    assert "first_name" in errors

def test_search_with_blank_query_returns_all_residents(tmp_path):
    service, repository = create_service(tmp_path)

    resident_one = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )

    resident_two = Resident(
        "Ana",
        "Garcia",
        "Laguna",
        "09181234567",
        "ana@example.com",
    )

    repository.save(resident_one)
    repository.save(resident_two)

    residents = service.search("")

    assert len(residents) == 2

def test_search_with_whitespace_query_returns_all_residents(tmp_path):
    service, repository = create_service(tmp_path)

    resident_one = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )

    resident_two = Resident(
        "Ana",
        "Garcia",
        "Laguna",
        "09181234567",
        "ana@example.com",
    )

    repository.save(resident_one)
    repository.save(resident_two)

    residents = service.search("   ")

    assert len(residents) == 2

def test_update_valid_resident_succeeds(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    updated, errors = service.update(
        resident.id,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    assert errors == []
    assert updated is not None
    assert updated.first_name == "Spongebob"


def test_update_preserves_resident_id(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    original_id = resident.id

    updated, errors = service.update(
        original_id,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    assert errors == []
    assert updated.id == original_id


def test_update_persists_all_permitted_fields(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    updated, errors = service.update(
        resident.id,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    saved_resident = repository.find_by_id(resident.id)

    assert errors == []
    assert saved_resident.first_name == "Spongebob"
    assert saved_resident.last_name == "Squarepants"
    assert saved_resident.address == "Laguna"
    assert saved_resident.contact_number == "09181234567"
    assert saved_resident.email == "Spongebob@example.com"


def test_update_preserves_existing_status(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
        "Inactive",
    )
    repository.save(resident)

    updated, errors = service.update(
        resident.id,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    saved_resident = repository.find_by_id(resident.id)

    assert errors == []
    assert updated.status == "Inactive"
    assert saved_resident.status == "Inactive"


def test_invalid_update_fails(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    updated, errors = service.update(
        resident.id,
        "",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    assert updated is None
    assert "first_name" in errors


def test_invalid_update_does_not_modify_persisted_information(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    updated, errors = service.update(
        resident.id,
        "",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    saved_resident = repository.find_by_id(resident.id)

    assert updated is None
    assert errors != []
    assert saved_resident.first_name == "Juan"
    assert saved_resident.last_name == "Dela Cruz"
    assert saved_resident.address == "Manila"
    assert saved_resident.contact_number == "09171234567"
    assert saved_resident.email == "juan@example.com"


def test_update_nonexistent_resident_is_handled_safely(tmp_path):
    service, repository = create_service(tmp_path)

    updated, errors = service.update(
        999999,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    assert updated is None
    assert "not_found" in errors


def test_update_nonexistent_resident_does_not_create_resident(tmp_path):
    service, repository = create_service(tmp_path)

    updated, errors = service.update(
        999999,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    residents = repository.find_all()

    assert updated is None
    assert "not_found" in errors
    assert residents == []


def test_updated_resident_is_visible_through_search(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    updated, errors = service.update(
        resident.id,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09181234567",
        "Spongebob@example.com",
    )

    residents = service.search("Spongebob")

    assert errors == []
    assert updated is not None
    assert len(residents) == 1
    assert residents[0].id == resident.id
    assert residents[0].first_name == "Spongebob"
    assert residents[0].last_name == "Squarepants"


def test_updated_contact_number_preserves_leading_zero(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    updated, errors = service.update(
        resident.id,
        "Spongebob",
        "Squarepants",
        "Laguna",
        "09987654321",
        "Spongebob@example.com",
    )

    saved_resident = repository.find_by_id(resident.id)

    assert errors == []
    assert saved_resident.contact_number == "09987654321"
    assert saved_resident.contact_number.startswith("0")

def test_deactivate_active_resident_succeeds(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Brgy. Mamplasan, Binan, Laguna",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    deactivated, errors = service.deactivate(resident.id)

    assert errors == []
    assert deactivated is not None
    assert deactivated.id == resident.id
    assert deactivated.status == "Inactive"


def test_deactivate_persists_inactive_status(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Brgy. Mamplasan, Binan, Laguna",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    deactivated, errors = service.deactivate(resident.id)

    saved_resident = repository.find_by_id(resident.id)

    assert errors == []
    assert deactivated is not None
    assert saved_resident.status == "Inactive"


def test_deactivate_preserves_resident_information(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Brgy. Mamplasan, Binan, Laguna",
        "09171234567",
        "juan@example.com",
    )
    repository.save(resident)

    original_id = resident.id

    deactivated, errors = service.deactivate(original_id)

    saved_resident = repository.find_by_id(original_id)

    assert errors == []
    assert saved_resident.id == original_id
    assert saved_resident.first_name == "Juan"
    assert saved_resident.last_name == "Dela Cruz"
    assert saved_resident.address == "Brgy. Mamplasan, Binan, Laguna"
    assert saved_resident.contact_number == "09171234567"
    assert saved_resident.email == "juan@example.com"
    assert saved_resident.status == "Inactive"

def test_deactivate_already_inactive_resident_is_safe(tmp_path):
    service, repository = create_service(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Brgy. Mamplasan, Binan, Laguna",
        "09171234567",
        "juan@example.com",
        "Inactive",
    )
    repository.save(resident)

    deactivated, errors = service.deactivate(resident.id)

    assert errors == []
    assert deactivated is not None
    assert deactivated.id == resident.id
    assert deactivated.status == "Inactive"


def test_deactivate_nonexistent_resident_returns_not_found(tmp_path):
    service, repository = create_service(tmp_path)

    deactivated, errors = service.deactivate(9999)

    assert deactivated is None
    assert errors == ["not_found"]


def test_deactivate_nonexistent_resident_does_not_create_record(tmp_path):
    service, repository = create_service(tmp_path)

    before = repository.find_all()

    deactivated, errors = service.deactivate(9999)

    after = repository.find_all()

    assert deactivated is None
    assert errors == ["not_found"]
    assert len(after) == len(before)

def test_deactivate_one_resident_does_not_affect_another(tmp_path):
    service, repository = create_service(tmp_path)

    resident_one = Resident(
        "Juan",
        "Dela Cruz",
        "Brgy. Mamplasan, Binan, Laguna",
        "09171234567",
        "juan@example.com",
    )

    resident_two = Resident(
        "Maria",
        "Santos",
        "Brgy. Mamplasan, Binan, Laguna",
        "09181234567",
        "maria@example.com",
    )

    repository.save(resident_one)
    repository.save(resident_two)

    deactivated, errors = service.deactivate(resident_one.id)

    remaining_resident = repository.find_by_id(resident_two.id)

    assert errors == []
    assert deactivated.status == "Inactive"
    assert remaining_resident.status == "Active"