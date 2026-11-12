# T15 – System Hardening and Regression Testing

## 1. Developer Information

- **Name:** Liz Samantha V. De Rojas
- **GitHub Username:** lizzzderojas
- **Repository:** UPHSL/csms-python-lizzzderojas
- **Technology Stack:** Python 3.14, Flask, SQLite, HTML, CSS, Jinja2, pytest
- **T15 Branch:** feature/t15-system-hardening

## 2. Release Candidate Baseline

The application was started locally using `python -m csms.main`.

| Baseline Check | Result | Notes |
|---|---|---|
| Application startup | PASS | Flask application started locally |
| `/health` | PASS | Returned status `ok` |
| Dashboard | PASS | Dashboard loaded and displayed summary information |
| Residents | PASS | Resident list and registration interface loaded |
| Service Requests | PASS | Service Request list and submission interface loaded |
| Baseline automated tests | PASS | 168 tests passed before T15 changes |

## 3. Hardening Changes

| Area | Issue or Risk Found | Action Taken | Files Changed | Test or Evidence |
|---|---|---|---|---|
| Input validation | Impossible calendar dates must be rejected | Added a test for an invalid date without saving a record | `tests/test_service_request_routes.py` | `test_submission_rejects_impossible_calendar_date_without_saving` |
| Persistence integrity | Rejected submissions must not modify existing records | Added a test that re-fetches and compares an existing record after a rejected submission | `tests/test_service_request_routes.py` | `test_rejected_submission_does_not_modify_existing_request` |
| Read-only safety | Repeated GET requests must not change persisted records | Added a test that snapshots and checks persisted data after repeated GET requests | `tests/test_service_request_routes.py` | `test_repeated_read_only_requests_do_not_modify_persisted_data` |
| Workflow integration | Inactive residents must not submit new Service Requests | Added a test covering resident deactivation followed by a rejected submission | `tests/test_service_request_routes.py` | `test_deactivated_resident_cannot_submit_service_request` |
| Date boundary | Valid leap-day dates must be accepted | Added a test verifying that a valid leap-day submission is saved | `tests/test_service_request_routes.py` | `test_valid_leap_day_submission_is_saved` |
| Interface consistency | Service Request search and status filtering were supported by the route but missing from the list interface | Added a GET search form, status filter, and Clear Filters link | `src/csms/templates/service_requests/list.html` | Manually verified search, status filtering, and combined filtering |

No existing tests were removed or weakened.

## 4. Five New T15 Hardening Tests

| Test Name | Category | What It Verifies | Why It Adds Value |
|---|---|---|---|
| `test_submission_rejects_impossible_calendar_date_without_saving` | Invalid input | Rejects an impossible date and confirms no record is saved | Tests calendar validity, not just missing or blank input |
| `test_rejected_submission_does_not_modify_existing_request` | Persistence integrity | Confirms an existing record remains unchanged after a rejected submission | Verifies that a failed operation does not affect previously saved data |
| `test_repeated_read_only_requests_do_not_modify_persisted_data` | Read-only safety | Checks database state after repeated list, search, and detail GET requests | Verifies persistence integrity rather than relying only on HTTP responses |
| `test_deactivated_resident_cannot_submit_service_request` | Cross-feature regression | Deactivates a resident and verifies that Service Request submission is rejected | Checks integration between resident lifecycle and Service Request submission |
| `test_valid_leap_day_submission_is_saved` | Boundary condition | Accepts and saves a valid leap-day date | Complements invalid-date testing by checking a valid calendar boundary |

## 5. Full Regression Test Results

**Command:** `pytest -v`

| Run | Result |
|---|---|
| Run 1 | 173 passed |
| Run 2 | 173 passed |
| Total collected tests per run | 173 |
| Whitespace validation | `git diff --check` returned no errors |

Both consecutive full regression runs passed after the T15 changes.

## 6. Manual Release Verification

| Scenario | Status | Notes |
|---|---|---|
| 1. Valid and invalid resident registration | PASS | Valid registration was checked. Browser-native validation blocked an invalid email; server-side invalid-input handling is also covered by automated tests. |
| 2. Valid and invalid resident update | PASS* | Valid update was checked manually. Invalid-update atomicity is covered by automated tests. |
| 3. Resident deactivation and reactivation | PASS | Deactivation changes the persisted status to Inactive; the resident remains listed with a Reactivate action, and reactivation restores Active status. |
| 4. Valid Service Request submission | PASS | Submission for an active resident generated an ID and Pending status. |
| 5. Missing or inactive resident submission | PASS | Inactive-resident submission was rejected with a visible message and no additional request appeared. |
| 6. Service Request search, filters, and details | PASS | Search, individual status filters, combined filters, and detail view were checked. |
| 7. Valid and invalid status transitions | PASS* | The workflow was checked. Invalid-transition persistence protection is also covered by automated tests. |
| 8. Completed and Cancelled terminal states | PASS* | Terminal-state behavior is covered by automated tests; separate manual verification of every terminal-state list/filter combination was not recorded. |
| 9. Dashboard synchronization | PASS | Dashboard reflected resident and Service Request changes. |
| 10. Repeated read-only GET requests | PASS | Repeated page requests were checked; automated testing also verifies persisted data remains unchanged. |
| 11. Missing Resident and Service Request routes | PASS | Missing record routes returned 404 responses. |
| 12. Navigation consistency | PASS | Dashboard, Residents, Service Requests, and New Service Request navigation were checked. |

`PASS*` indicates that automated tests provide coverage for the noted behavior, but that particular subcase was not separately confirmed during manual verification.

## 7. Repository Hygiene Review

The final review for this readiness correction found only the intended documentation edit staged. `git diff --cached --check` reported no whitespace errors. A tracked-file scan found no local database, SQLite, environment, Python cache, or macOS metadata artifacts. A source scan found no debug `print()` calls, TODO/FIXME markers, or debugger statements. SQL statements remain in repository/persistence code and use bound parameters for supplied values. The configured development fallback secret remains documented as a deployment limitation; no secret value is included in release output.

## 8. Known Limitations

- The application is currently configured for local development and uses Flask's development server.
- Production deployment configuration has not been established.
- The application does not currently implement authentication, role-based access control, or CSRF protection.
- The development configuration contains a fallback development secret key; a production deployment must use a securely configured secret.
- The application uses a local SQLite database and has not been prepared for a production multi-user deployment.
- Historical and operational data are limited to the records available in the local application.

These limitations are documented and are outside the T15 feature-freeze scope.

## 9. Release Candidate Statement

**READY FOR T16 FINAL EXAM**

The T15 changes are merged into `main`; the current main commit has a clean tracked baseline before this documentation-only correction. The application passed two consecutive full regression runs with 173 tests passing each time, and the five new T15 hardening tests and recorded manual checks provide additional verification. The local release baseline was rechecked with 173 passing tests and successful HTTP 200 responses from `/health`, Dashboard, Residents, and Service Requests before the T16 work begins.
