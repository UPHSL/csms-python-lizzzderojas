"""Service for registering residents."""


class ResidentService:
    """Handle Resident registration."""

    def __init__(self, repository, validator):
        self.repository = repository
        self.validator = validator

    def register(self, resident):
        """Validate and save a Resident."""
        errors = self.validator.validate(resident)

        if errors:
            return None, errors

        registered_resident = self.repository.save(resident)

        return registered_resident, []

    def search(self, query):
        """Search Residents or return all Residents for a blank query."""
        if not query.strip():
            return self.repository.find_all()

        return self.repository.search(query)