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
    
    def update(self, resident_id, first_name, last_name, address, contact_number, email):
        """Update an existing Resident."""
        resident = self.repository.find_by_id(resident_id)

        if resident is None:
            return None, ["not_found"]

        resident.first_name = first_name
        resident.last_name = last_name
        resident.address = address
        resident.contact_number = contact_number
        resident.email = email

        errors = self.validator.validate(resident)

        if errors:
            return None, errors

        updated_resident = self.repository.update(resident)

        return updated_resident, []
