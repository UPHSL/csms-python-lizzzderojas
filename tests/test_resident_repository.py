from csms.database import initialize_database
from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository


def create_test_repository(tmp_path):
    """Create a repository that uses a temporary database."""
    database_file = tmp_path / "test.db"

    initialize_database(database_file)

    return ResidentRepository(database_file)

def test_save_resident(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
        "Active",
    )

    saved_resident = repository.save(resident)

    assert saved_resident.id is not None

def test_resident_receives_identifier(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "LeBron",
        "James",
        "Los Angeles",
        "09181234567",
        "lebron@example.com",
        "Active",
    )

    assert resident.id is None

    repository.save(resident)

    assert resident.id is not None

def test_find_resident_by_id(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Alex",
        "Eala",
        "Laguna",
        "09192345678",
        "alex@example.com",
        "Active",
    )

    repository.save(resident)

    found_resident = repository.find_by_id(resident.id)

    assert found_resident is not None
    assert found_resident.id == resident.id

def test_resident_information_is_preserved(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Ana",
        "Garcia",
        "Cavite",
        "09171234567",
        "ana@example.com",
        "Active",
    )

    repository.save(resident)

    found_resident = repository.find_by_id(resident.id)

    assert found_resident.first_name == "Ana"
    assert found_resident.last_name == "Garcia"
    assert found_resident.address == "Cavite"
    assert found_resident.contact_number == "09171234567"
    assert found_resident.email == "ana@example.com"
    assert found_resident.status == "Active"

def test_active_status_is_preserved(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Aiah",
        "Arceta",
        "Cebu",
        "09181234567",
        "aiah@example.com",
        "Active",
    )

    repository.save(resident)

    found_resident = repository.find_by_id(resident.id)

    assert found_resident.status == "Active"

def test_missing_resident_returns_none(tmp_path):
    repository = create_test_repository(tmp_path)

    found_resident = repository.find_by_id(999999)

    assert found_resident is None

def test_resident_persists_with_new_repository(tmp_path):
    database_file = tmp_path / "test.db"

    initialize_database(database_file)

    first_repository = ResidentRepository(database_file)

    resident = Resident(
        "Carlos",
        "Mendoza",
        "Manila",
        "09191234567",
        "carlos@example.com",
        "Active",
    )

    first_repository.save(resident)

    second_repository = ResidentRepository(database_file)

    found_resident = second_repository.find_by_id(resident.id)

    assert found_resident is not None
    assert found_resident.id == resident.id
    assert found_resident.first_name == "Carlos"
    assert found_resident.last_name == "Mendoza"

def test_multiple_residents_are_stored_separately(tmp_path):
    repository = create_test_repository(tmp_path)

    resident_one = Resident(
        "Peter",
        "Parker",
        "Cavite",
        "09171234567",
        "peter@example.com",
        "Active",
    )

    resident_two = Resident(
        "Michelle Jones",
        "Watson",
        "Laguna",
        "09181234567",
        "mj@example.com",
        "Active",
    )

    repository.save(resident_one)
    repository.save(resident_two)

    found_one = repository.find_by_id(resident_one.id)
    found_two = repository.find_by_id(resident_two.id)

    assert found_one.first_name == "Peter"
    assert found_two.first_name == "Michelle Jones"
    assert found_one.id != found_two.id