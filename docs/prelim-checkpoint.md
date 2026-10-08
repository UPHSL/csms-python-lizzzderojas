## Developer Information

Name: Liz Samantha V. De Rojas
GitHub Username: lizzzderojas  
Primary Technology Stack: Python, Flask, SQLite
T03 Branch: feature/t03-resident-persistence  

## My T03 Implementation

Based on the given instructions, I implemented Resident persistence using a file-backed SQLite database. The database is used to store Resident information in a `residents` table. The `ResidentRepository` is responsible for saving Resident information and retrieving it from the database. When `save()` is called, the Resident information is inserted into the SQLite table, and SQLite automatically generates a unique ID for the new Resident. The generated ID is then assigned to the Resident object so the application can use it. The `find_by_id()` method searches for a Resident using the stored ID and converts the database row back into a Resident object. If the requested Resident does not exist, the method returns `None`. For automated testing, temporary database files are used to keep the tests separate from the development database.

## My Persistence Design Decision

One design decision I made was to allow the ResidentRepository to use a specific database file. The normal application can use the development database, while the automated tests can use a temporary database. I chose this approach to prevent test data from affecting the development database and to make the tests repeatable. I considered using the same development database for testing, but this could cause tests to depend on records created during previous runs. Using a temporary database provides a separate and clean environment for each test.

## Files I Changed

### File: `.gitignore`

Purpose: Added a database file pattern so that the local SQLite database is not committed to Git.

### File: `src/csms/__init__.py`

Purpose: Initializes the database when the Flask application is created.

### File: `src/csms/database.py`

Purpose: Provides the SQLite database connection and initializes the `residents` table when needed.

### File: `src/csms/repositories/resident_repository.py`

Purpose: Handles Resident persistence by saving Resident information to SQLite and retrieving Residents by ID.

### File: `tests/test_resident_repository.py`

Purpose: Contains the 7 required T03 persistence tests and the student-designed persistence test.

## Problem I Encountered

Problem or error: I was unsure where the database initialization should be placed because the project already had an existing database component and a defined application structure.

Cause: I was still learning how the database, Resident model, validation service, and repository should be separated.

How I resolved it: I reviewed the existing project structure and kept the database connection and table initialization in the database component. The Resident model continues to represent Resident information, while the ResidentValidator handles validation. The ResidentRepository handles database persistence. I also configured the repository to use a temporary database file during automated tests.

## My Student-Designed Test

Test name: `test_multiple_residents_are_stored_separately`

What it verifies: The test verifies that multiple Residents can be stored in the same database without one Resident replacing another. It also checks that each Resident receives a different database-generated ID and that the correct Resident can be retrieved using that ID.

Why I chose this scenario: I chose this scenario because the system is expected to store multiple Resident records. I wanted to make sure that saving a second Resident does not affect the first Resident. This test also checks that each stored Resident has its own unique identifier.

## Tools and References Used

- Visual Studio Code — used to create, edit, and test the project files.
- Git and GitHub — used for version control and the T03 feature branch.
- Python — used to implement the Resident persistence functionality.
- Flask — used to verify that the existing application continues to run.
- SQLite — used as the file-backed database.
- pytest — used to create and run the automated persistence tests.
- ChatGPT — used as a coding assistant to explain Python, SQLite, pytest, Git, and the project instructions in simple terms, help me troubleshoot errors, and guide the implementation step by step.