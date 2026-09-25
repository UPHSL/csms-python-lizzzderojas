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