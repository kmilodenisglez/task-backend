import re

from fastapi import HTTPException


def validate_password(password: str) -> None:
    """Validate password meets security requirements"""
    if len(password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters long"
        )

    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter",
        )

    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter",
        )

    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400, detail="Password must contain at least one number"
        )

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character",
        )


def validate_email(email: str) -> bool:
    # Simple regex for email validation
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))
