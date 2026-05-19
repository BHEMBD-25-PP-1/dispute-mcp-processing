FINAL_STATUSES = {"resolved"}

ALLOWED_TRANSITIONS = {
    "accepted": {"processing", "attention", "resolved"},
    "processing": {"attention", "resolved"},
    "attention": {"processing", "resolved"},
    "resolved": set(),
}


def is_final_status(status: str) -> bool:
    return status in FINAL_STATUSES


def can_transition(current_status: str, next_status: str) -> bool:
    return next_status in ALLOWED_TRANSITIONS.get(current_status, set())
