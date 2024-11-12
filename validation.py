import re


def validate_password(password):
    # Check for emoji and other non-ASCII characters
    errors = []
    if not all(ord(char) < 128 for char in password):
        errors.append("Password cannot contain emoji or non-ASCII characters")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if len(password) > 40:
        errors.append("Password must not exceed 40 characters")
    if ' ' in password:
        errors.append("Password cannot contain spaces")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*()_\-=[\]{}|\\;:<>,.?/~+]', password):
        errors.append("Password must contain at least one special character")
    if errors:
        return False, errors
    return True, "Password is valid"


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    return False
