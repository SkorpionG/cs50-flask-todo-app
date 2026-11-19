import re
from datetime import datetime

from app.db import task_priority_options, task_status_options


def validate_password(password: str) -> tuple[bool, list[str] | str]:
    # Check for emoji and other non-ASCII characters
    errors: list[str] = []
    if not all(ord(char) < 128 for char in password):
        errors.append("Password cannot contain emoji or non-ASCII characters")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if len(password) > 40:
        errors.append("Password must not exceed 40 characters")
    if " " in password:
        errors.append("Password cannot contain spaces")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*()_\-=[\]{}|\\;:<>,.?/~+]", password):
        errors.append("Password must contain at least one special character")
    if errors:
        return False, errors
    return True, "Password is valid"


def validate_email(email: str) -> bool:
    pattern: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_tag(name: str | None, color: str | None = None) -> list[str]:
    errors: list[str] = []

    if not name or len(name.strip()) == 0:
        errors.append("Tag name is required")
        return errors
    elif len(name) > 50:
        errors.append("Tag name must be less than 50 characters")

    # Check for special characters
    if not name.replace("-", "").replace("_", "").isalnum():
        errors.append("Tag name can only contain letters, numbers, hyphens, and underscores")

    # Validate color if provided
    if color and not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
        errors.append("Invalid color format. Please use hex color (e.g., #FF0000)")

    return errors


def convert_datetime_format(datetime_string: str | None) -> str | None:
    if not datetime_string:
        return None
    try:
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Invalid datetime string")
        return datetime_string


def validate_task(
    title: str | None,
    description: str | None,
    due_date: str | None,
    priority: str | None,
    status: str | None,
) -> list[str]:
    errors: list[str] = []

    # Title validation
    if not title or len(title.strip()) == 0:
        errors.append("Title is required")
    elif len(title) > 100:
        errors.append("Title must be less than 100 characters")

    # Description validation (optional but with max length)
    if description and len(description) > 500:
        errors.append("Description must be less than 500 characters")

    # Due date validation
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%dT%H:%M")
        except ValueError:
            errors.append("Invalid due date format")

    # Priority validation
    valid_priorities = task_priority_options()
    if priority not in valid_priorities:
        errors.append("Invalid priority level")

    # Status validation
    valid_statuses = task_status_options()
    if status not in valid_statuses:
        errors.append("Invalid status")

    return errors
