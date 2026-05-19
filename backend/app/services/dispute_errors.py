class DisputeConflictError(Exception):
    """Raised when a concurrent operator change conflicts with current state."""


class InvalidDisputeTransitionError(Exception):
    """Raised when a status transition is not allowed by the state machine."""


class DisputeNotFoundError(Exception):
    """Raised when the requested dispute does not exist."""
