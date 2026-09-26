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

def test_find_all_returns_all_residents(tmp_path):
    repository = create_test_repository(tmp_path)

    resident_one = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
        "Active",
    )

    resident_two = Resident(
        "Ana",
        "Garcia",
        "Laguna",
        "09181234567",
        "ana@example.com",
        "Active",
    )

    repository.save(resident_one)
    repository.save(resident_two)

    residents = repository.find_all()

    assert len(residents) == 2


def test_find_all_returns_empty_list_when_no_residents(tmp_path):
    repository = create_test_repository(tmp_path)

    residents = repository.find_all()

    assert residents == []

def test_find_all_orders_residents_correctly(tmp_path):
    repository = create_test_repository(tmp_path)

    resident_one = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
        "Active",
    )

    resident_two = Resident(
        "Ana",
        "Garcia",
        "Laguna",
        "09181234567",
        "ana@example.com",
        "Active",
    )

    resident_three = Resident(
        "Maria",
        "Dela Cruz",
        "Cavite",
        "09191234567",
        "maria@example.com",
        "Active",
    )

    repository.save(resident_one)
    repository.save(resident_two)
    repository.save(resident_three)

    residents = repository.find_all()

    assert residents[0].last_name == "Dela Cruz"
    assert residents[0].first_name == "Juan"

    assert residents[1].last_name == "Dela Cruz"
    assert residents[1].first_name == "Maria"

    assert residents[2].last_name == "Garcia"
    assert residents[2].first_name == "Ana"

    def search(self, query):
        """Search Residents by first name or last name."""
        connection = self.get_connection()

        search_text = f"%{query.strip()}%"

        cursor = connection.execute(
            """
            SELECT
                id,
                first_name,
                last_name,
                address,
                contact_number,
                email,
                status
            FROM residents
            WHERE LOWER(first_name) LIKE LOWER(?)
               OR LOWER(last_name) LIKE LOWER(?)
            ORDER BY last_name ASC, first_name ASC, id ASC
            """,
            (search_text, search_text),
        )

        rows = cursor.fetchall()

        connection.close()

        residents = []

        for row in rows:
            resident = Resident(
                first_name=row[1],
                last_name=row[2],
                address=row[3],
                contact_number=row[4],
                email=row[5],
                status=row[6],
                id=row[0],
            )

            residents.append(resident)

        return residents

def test_search_by_first_name_is_case_insensitive_and_partial(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Jonathan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "jonathan@example.com",
        "Active",
    )

    repository.save(resident)

    residents = repository.search("jon")

    assert len(residents) == 1
    assert residents[0].first_name == "Jonathan"

def test_search_is_case_insensitive(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Jonathan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "jonathan@example.com",
        "Active",
    )

    repository.save(resident)

    residents = repository.search("JON")

    assert len(residents) == 1
    assert residents[0].first_name == "Jonathan"

def test_search_by_last_name_is_case_insensitive_and_partial(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
        "Active",
    )

    repository.save(resident)

    residents = repository.search("DELA")

    assert len(residents) == 1
    assert residents[0].last_name == "Dela Cruz"
def test_search_returns_empty_list_when_no_resident_matches(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
        "Active",
    )

    repository.save(resident)

    residents = repository.search("Zzz")

    assert residents == []

def test_search_returns_matching_residents_without_duplicates(tmp_path):
    repository = create_test_repository(tmp_path)

    resident_one = Resident(
        "Juan",
        "Dela Cruz",
        "Manila",
        "09171234567",
        "juan@example.com",
        "Active",
    )

    resident_two = Resident(
        "Juan",
        "Garcia",
        "Laguna",
        "09181234567",
        "juan2@example.com",
        "Inactive",
    )

    repository.save(resident_one)
    repository.save(resident_two)

    residents = repository.search("Juan")

    assert len(residents) == 2
    assert residents[0].id != residents[1].id

def test_search_preserves_all_resident_information(tmp_path):
    repository = create_test_repository(tmp_path)

    resident = Resident(
        "Juan",
        "Dela Cruz",
        "Brgy. Mamplasan, Binan, Laguna",
        "09171234567",
        "juan@example.com",
        "Inactive",
    )

    repository.save(resident)

    residents = repository.search("Juan")

    assert len(residents) == 1
    assert residents[0].id == resident.id
    assert residents[0].first_name == "Juan"
    assert residents[0].last_name == "Dela Cruz"
    assert residents[0].address == "Brgy. Mamplasan, Binan, Laguna"
    assert residents[0].contact_number == "09171234567"
    assert residents[0].email == "juan@example.com"
    assert residents[0].status == "Inactive"