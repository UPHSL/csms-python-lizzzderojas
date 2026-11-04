
from csms.database import initialize_database
from csms.models.service_request import ServiceRequest
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from csms.services.service_request_query_service import (
    ServiceRequestQueryService,
)


def create_query_service(tmp_path):
    """Create a query service using a temporary database."""
    database_file = tmp_path / "test.db"
    initialize_database(database_file)

    repository = ServiceRequestRepository(database_file)
    service = ServiceRequestQueryService(repository)

    return service, repository


def add_request(
    repository,
    service_type,
    description,
    date_requested,
    status="Pending",
    resident_id=1,
):
    """Create and save a sample ServiceRequest."""
    request = ServiceRequest(
        resident_id=resident_id,
        service_type=service_type,
        description=description,
        date_requested=date_requested,
        status=status,
    )

    return repository.save(request)


def test_find_all_returns_all_persisted_requests(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Barangay Clearance",
        "Clearance application",
        "2026-10-01",
    )
    add_request(
        repository,
        "Medical Assistance",
        "Medical support request",
        "2026-10-02",
    )

    results = service.find_all()

    assert len(results) == 2


def test_find_all_returns_empty_list_when_no_requests_exist(tmp_path):
    service, _ = create_query_service(tmp_path)

    results = service.find_all()

    assert results == []


def test_find_all_uses_deterministic_ordering(tmp_path):
    service, repository = create_query_service(tmp_path)

    older = add_request(
        repository,
        "Older Request",
        "Older description",
        "2026-09-30",
    )
    first_same_date = add_request(
        repository,
        "First Same Date",
        "First description",
        "2026-10-01",
    )
    second_same_date = add_request(
        repository,
        "Second Same Date",
        "Second description",
        "2026-10-01",
    )
    newest = add_request(
        repository,
        "Newest Request",
        "Newest description",
        "2026-10-02",
    )

    results = service.find_all()

    assert [request.id for request in results] == [
        newest.id,
        second_same_date.id,
        first_same_date.id,
        older.id,
    ]


def test_find_by_id_returns_existing_request(tmp_path):
    service, repository = create_query_service(tmp_path)

    saved_request = add_request(
        repository,
        "Barangay Clearance",
        "Request for clearance",
        "2026-10-01",
    )

    result = service.find_by_id(saved_request.id)

    assert result is not None
    assert result.id == saved_request.id
    assert result.service_type == "Barangay Clearance"


def test_find_by_id_returns_none_for_unknown_id_without_inserting(
    tmp_path,
):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Medical Assistance",
        "Medical support",
        "2026-10-01",
    )

    before_count = len(repository.find_all())

    result = service.find_by_id(999999)

    after_count = len(repository.find_all())

    assert result is None
    assert before_count == after_count


def test_search_finds_partial_case_insensitive_service_type(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Barangay Clearance",
        "Clearance application",
        "2026-10-01",
    )

    results = service.search("CLEAR")

    assert len(results) == 1
    assert results[0].service_type == "Barangay Clearance"


def test_search_finds_partial_case_insensitive_description(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Medical Assistance",
        "Request for financial medical support",
        "2026-10-01",
    )

    results = service.search("MEDICAL SUPPORT")

    assert len(results) == 1
    assert results[0].description == (
        "Request for financial medical support"
    )


def test_blank_search_returns_all_requests_in_order(tmp_path):
    service, repository = create_query_service(tmp_path)

    older = add_request(
        repository,
        "Older Request",
        "Older description",
        "2026-09-30",
    )
    newer = add_request(
        repository,
        "Newer Request",
        "Newer description",
        "2026-10-01",
    )

    results = service.search("   ")

    assert [request.id for request in results] == [
        newer.id,
        older.id,
    ]


def test_search_with_no_matches_returns_empty_list(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Barangay Clearance",
        "Clearance application",
        "2026-10-01",
    )

    results = service.search("Passport")

    assert results == []


def test_status_filter_returns_only_matching_status(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Clearance",
        "Clearance request",
        "2026-10-01",
        status="Pending",
    )
    add_request(
        repository,
        "Medical Assistance",
        "Medical support",
        "2026-10-02",
        status="Completed",
    )

    results = service.search(status="Completed")

    assert len(results) == 1
    assert results[0].status == "Completed"


def test_no_status_filter_includes_all_supported_statuses(tmp_path):
    service, repository = create_query_service(tmp_path)

    statuses = [
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    ]

    for index, status in enumerate(statuses):
        add_request(
            repository,
            f"Request {index}",
            f"Description {index}",
            f"2026-10-0{index + 1}",
            status=status,
        )

    results = service.search()

    assert len(results) == 4
    assert {request.status for request in results} == set(statuses)


def test_combined_search_and_status_filter(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Medical Assistance",
        "Medical support request",
        "2026-10-01",
        status="Pending",
    )
    add_request(
        repository,
        "Medical Assistance",
        "Medical support request",
        "2026-10-02",
        status="Completed",
    )
    add_request(
        repository,
        "Barangay Clearance",
        "Clearance request",
        "2026-10-03",
        status="Completed",
    )

    results = service.search(
        query="medical",
        status="Completed",
    )

    assert len(results) == 1
    assert results[0].service_type == "Medical Assistance"
    assert results[0].status == "Completed"


def test_request_matching_both_fields_appears_only_once(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Medical Assistance",
        "Medical assistance request",
        "2026-10-01",
    )

    results = service.search("medical")

    assert len(results) == 1


def test_search_preserves_all_service_request_fields(tmp_path):
    service, repository = create_query_service(tmp_path)

    saved_request = add_request(
        repository,
        "Medical Assistance",
        "Request for medical support",
        "2026-10-01",
        status="In Progress",
        resident_id=25,
    )

    results = service.search("medical")

    assert len(results) == 1

    result = results[0]

    assert result.id == saved_request.id
    assert result.resident_id == 25
    assert result.service_type == "Medical Assistance"
    assert result.description == "Request for medical support"
    assert result.date_requested == "2026-10-01"
    assert result.status == "In Progress"


def test_unsupported_status_is_rejected(tmp_path):
    service, repository = create_query_service(tmp_path)

    add_request(
        repository,
        "Medical Assistance",
        "Medical support request",
        "2026-10-01",
    )

    try:
        service.search(status="Approved")
        assert False, "Expected ValueError for unsupported status"
    except ValueError as error:
        assert str(error) == "unsupported_status"
