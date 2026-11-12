# T16 Final Development Checkpoint

## 1. Developer Information

- **Name:** Liz Samantha V. De Rojas
- **GitHub Username:** lizzzderojas
- **Technology Stack:** Python 3.14, Flask, SQLite, Jinja2, HTML, CSS, pytest
- **T16 Branch:** feature/t16-final-release
- **Final Release Version:** 1.0.0

## 2. My Final Release Implementation

I established the authoritative application version in `src/csms/_version.py` as `__version__`. The small version module keeps release identity separate from business rules and lets both runtime configuration and package metadata consume the same value. `BaseConfig.APP_VERSION` imports that constant, so the existing health endpoint reports the configured value rather than maintaining a second literal. The setuptools version in `pyproject.toml` is dynamic and reads the same package attribute. A Flask application context processor makes the configured app name and version available to every standalone Jinja template, and each page footer displays the version as `v1.0.0`. The health response identifies both the short name CSMS and the full application name, with an `ok` status and no environment, credential, or filesystem data. This follows the existing Flask configuration and application-factory pattern instead of adding release logic to domain services.

## 3. Files I Changed

- `src/csms/_version.py` — single authoritative semantic version value used by runtime and package metadata.
- `src/csms/config.py` — wires `APP_VERSION` to the authoritative version constant.
- `pyproject.toml` — derives package version dynamically from the same constant.
- `src/csms/__init__.py` — injects app identity and version into all rendered templates.
- `src/csms/ui/routes.py` — exposes the short name, full name, version, and healthy status from `/health`.
- `src/csms/templates/index.html`, `dashboard.html`, `residents/form.html`, `residents/list.html`, `service_requests/detail.html`, `service_requests/form.html`, `service_requests/list.html` — display the shared release version.
- `tests/test_smoke.py` — verifies the health identity/version and UI version presentation.
- `tests/test_final_release_integration.py` — verifies the integrated persisted resident/request/dashboard scenario.
- `docs/release-v1.0.0.md` — official release notes.
- `docs/final-checkpoint.md` — this examination checkpoint.

## 4. My Final Examination Test

- **Test Name:** `test_registered_resident_request_completion_updates_persisted_dashboard`
- **Modules/Responsibilities Covered:** Resident registration and persistence; Service Request submission and resident eligibility; status workflow; Service Request persistence/querying; dashboard aggregation.
- **Starting State:** A fresh test database with no residents or service requests.
- **Operations Performed:** Registers an active resident through the route, submits a request for that resident, advances it from Pending to In Progress to Completed, attempts a disallowed reverse transition, re-reads the persisted request, and loads the dashboard.
- **Expected Final State:** The resident remains persisted as Active; one linked request remains persisted as Completed; the rejected transition does not change it; dashboard counts show one completed request and zero pending/open requests.
- **Why This Test Is Meaningful:** It exercises real route, service, repository, SQLite, and dashboard paths in one scenario. It verifies both a successful multi-step lifecycle and that an invalid operation leaves persisted state unchanged, which is stronger evidence than an isolated unit test or a simple successful page response.

## 5. My Final Technical Decision

- **Decision:** Store the version once in `csms._version` and have both runtime configuration and setuptools metadata read it.
- **Alternative Considered:** Keep separate literals in `config.py` and `pyproject.toml`, or read installed distribution metadata at runtime.
- **Reason for My Decision:** Separate literals can drift, while runtime package-metadata lookup can depend on installation state. A small source module is available during application startup and can also be statically read by setuptools, maintaining one clear source of truth.

## 6. Problem or Verification Issue Encountered

- **Problem:** The first packaging verification using `pip wheel --no-build-isolation` could not import `setuptools.build_meta` in the selected virtual environment.
- **Cause or Investigation:** This project declares setuptools as its PEP 517 build backend, but that build dependency was not installed in the active environment.
- **Resolution:** Installed the declared setuptools build dependency, rebuilt the wheel successfully, and confirmed its generated distribution metadata reports version `1.0.0`.

## 7. Final Regression Results

- **Test Command:** `/Users/liz/csms-python-lizzzderojas/.venv/bin/python -m pytest`
- **Final Regression Run 1:** PASS — 175 passed
- **Final Regression Run 2:** PASS — 175 passed
- **Total Passing Tests Reported:** 175 in each complete run

## 8. Tools and References Used

- Existing CSMS source code, tests, and T15 release-readiness documentation.
- Python and Flask project configuration and application-factory conventions.
- Setuptools `pyproject.toml` dynamic metadata configuration.
- VS Code, Pylance, and GitHub Copilot (AI coding assistant). I reviewed and verified the resulting changes and remain responsible for understanding and defending them.
- Git and GitHub repository workflow.

## 9. Final Release Declaration

CSMS v1.0.0 - READY FOR RELEASE
