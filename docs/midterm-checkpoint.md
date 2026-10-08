# T10 Midterm Checkpoint - Manage Service Request Status

## 1. Developer Information

- Name: Liz Samantha V. De Rojas
- GitHub Username: lizzzderojas
- Primary Technology Stack: Python, SQLite
- T10 Branch: feature/t10-service-request-status

## 2. My T10 Implementation

I added a service that manages the status of existing service requests. The service first finds the service request using its ID before making any changes. It checks if the requested status is supported and then checks if the status change is allowed based on the current status. The allowed transitions are Pending to In Progress or Cancelled, and In Progress to Completed or Cancelled. Completed and Cancelled are final statuses and cannot be changed again. If the request is missing, the status is unsupported, or the transition is not allowed, the database is not changed. When the transition is valid, only the status is updated in the database, and the updated request is retrieved and returned.

## 3. My Transition Rules

The supported statuses are:

- Pending
- In Progress
- Completed
- Cancelled

The allowed transitions are:

- Pending → In Progress
- Pending → Cancelled
- In Progress → Completed
- In Progress → Cancelled

The following transitions are not allowed:

- Pending → Completed
- In Progress → Pending
- Completed → any other status
- Cancelled → any other status
- Same status to the same status
- Unsupported statuses such as Approved, Rejected, Processing, or Done

## 4. Files I Changed

### src/csms/repositories/service_request_repository.py

Added the update_status() method to update only the status of an existing service request in the database.

### src/csms/services/request_service.py

Added the ServiceRequestStatusService to check supported statuses and allowed transitions before updating the request.

### tests/test_service_request_status.py

Added 14 tests for valid transitions, invalid transitions, terminal statuses, unsupported statuses, missing IDs, data preservation, and status persistence.

### docs/midterm-checkpoint.md

Added this documentation to explain my T10 implementation, transition rules, testing, and development experience.

## 5. Problem I Encountered

During development, I encountered a formatting issue that was detected by git diff --check. I checked the changed files and removed the extra whitespace. I also had a Git setup issue because my username and email were not configured at first. I fixed this by setting my Git username and email using the git config command. After fixing these issues, I continued the development and verified that the tests were still passing.

## 6. My Student-Designed Test

### Test Name

test_status_update_persists_across_repository_instances

### What It Verifies

This test verifies that a valid status update is actually saved in the database. After changing a request from Pending to In Progress, the test creates a new repository instance and retrieves the same request. It then checks that the status is still In Progress.

### Why I Added It

I added this test to make sure that the status change is not only updated in memory but is also properly saved in the database.

## 7. Tools and References Used

- Python
- SQLite
- Pytest
- Git and GitHub
- VS Code / Terminal
- ChatGPT
