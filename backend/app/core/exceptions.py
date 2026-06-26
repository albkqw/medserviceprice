class MedServicePriceError(Exception):
    """Root domain exception. Catch this to handle any app-level error."""


class NotFoundError(MedServicePriceError):
    def __init__(self, entity: str, entity_id: str | int) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with id={entity_id!r} not found")


class ConflictError(MedServicePriceError):
    """Raised when an operation would violate a uniqueness constraint."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ValidationError(MedServicePriceError):
    """Raised when input is structurally valid but violates business rules."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
