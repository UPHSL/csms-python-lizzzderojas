# CSMS v1.0.0 Release Notes

## 1. Release

- **Application:** Community Services Management System
- **Release:** v1.0.0
- **Release Type:** Final Course Release

## 2. Release Summary

CSMS v1.0.0 provides a Flask-based community services application for maintaining resident records, submitting service requests for eligible residents, advancing requests through a controlled status workflow, and viewing operational totals on a dashboard. Resident and request data are persisted in SQLite and presented through the browser interface.

## 3. Resident Management Capabilities

Application users can register residents, search and view records, update resident information, and deactivate residents. Resident fields are validated before persistence, and inactive residents are not eligible for new service requests. The current interface also exposes the existing Reactivate action; this capability predates T16 and was not introduced as part of the final-release work.

## 4. Service Request Management Capabilities

Users can submit a request for an active resident, search requests by text, filter by supported status, and view request details. The application enforces the controlled workflow Pending → In Progress → Completed or Cancelled, rejects invalid transitions, and persists valid status changes.

## 5. Dashboard Capabilities

The dashboard reports resident totals by status, total and open requests, request counts by status, and recent service requests. Its figures are calculated from persisted application data.

## 6. Quality and Hardening

T15 added regression coverage for invalid dates, persistence integrity, read-only behavior, inactive-resident eligibility, and date boundaries. T16 establishes a single authoritative 1.0.0 version source, exposes safe application identity and health information, displays the release version throughout the UI, adds an integrated persisted-workflow test, and repeats the complete regression suite.

## 7. Final Verification

- **Final Regression Run 1:** PASS — 175 passed
- **Final Regression Run 2:** PASS — 175 passed
- **Application Startup:** PASS — Flask development server started successfully
- **/health:** PASS — HTTP 200; reports CSMS, full name, version 1.0.0, and status `ok`; no sensitive configuration exposed
- **Dashboard:** PASS — resident and request metrics, open requests, and recent requests displayed
- **Resident Management:** PASS — listing, search, valid/invalid registration, update, and lifecycle actions verified
- **Service Request Management:** PASS — submission, active-resident eligibility, listing, search/filter, details, and valid/invalid workflow verified
- **Final Release Version:** 1.0.0

## 8. Known Limitations

- The application uses Flask's development server by default; production deployment configuration is not included.
- Authentication, role-based authorization, and CSRF protection are not implemented.
- Production secret management and production multi-user database deployment are outside the current release scope.
- The application uses local SQLite persistence and has no historical status/audit log.

No known release-blocking limitations remain within the defined CSMS v1.0.0 scope.
