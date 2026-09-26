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