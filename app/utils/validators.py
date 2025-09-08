import re
from fastapi import HTTPException

# Patrones de validación
PASSWORD_PATTERNS = [
    (r".{8,}", "Password must be at least 8 characters long"),
    (r"[A-Z]", "Password must contain at least one uppercase letter"),
    (r"[a-z]", "Password must contain at least one lowercase letter"),
    (r"\d", "Password must contain at least one digit"),
    (
        r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]",
        "Password must contain at least one special character",
    ),
]

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


def validate_password(password: str) -> None:
    """
    Validate password meets security requirements.
    Raises HTTPException with all failed rules for better UX.
    """
    failed_rules = []

    for pattern, message in PASSWORD_PATTERNS:
        if not re.search(pattern, password):
            failed_rules.append(message)

    if failed_rules:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Password validation failed",
                "errors": failed_rules,
            },
        )


def validate_email(email: str) -> bool:
    """
    Validate email format using RFC 5322 compliant regex.
    Returns True if valid, False otherwise.
    """
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_REGEX.fullmatch(email.strip()))
