from flask import Flask

from app.utils.validation import (
    convert_datetime_format,
    validate_email,
    validate_password,
    validate_tag,
    validate_task,
)


def test_validate_email() -> None:
    assert validate_email("user@example.com") is True
    assert validate_email("first.last+tag@sub.domain.org") is True
    assert validate_email("not-an-email") is False
    assert validate_email("user@domain") is False


def test_validate_password() -> None:
    valid, msg = validate_password("StrongPass1!")
    assert valid is True
    assert msg == "Password is valid"

    valid, errors = validate_password("weak")
    assert valid is False
    assert isinstance(errors, list)
    assert any("at least 8 characters" in err for err in errors)
    assert any("uppercase letter" in err for err in errors)
    assert any("number" in err for err in errors)
    assert any("special character" in err for err in errors)


def test_validate_tag() -> None:
    assert validate_tag("work-1_a", "#ff00aa") == []
    assert validate_tag("", "#ff00aa") == ["Tag name is required"]
    assert validate_tag("bad tag!", "#ff00aa") == [
        "Tag name can only contain letters, numbers, hyphens, and underscores"
    ]
    assert validate_tag("work", "red") == ["Invalid color format. Please use hex color (e.g., #FF0000)"]


def test_convert_datetime_format() -> None:
    assert convert_datetime_format(None) is None
    assert convert_datetime_format("") is None
    assert convert_datetime_format("2027-01-15T14:30") == "2027-01-15 14:30:00"
    assert convert_datetime_format("invalid-date") == "invalid-date"


def test_validate_task(app: Flask) -> None:
    # Ensure the database schema exists inside the temp app before querying column constraints
    app.test_client().get("/")

    with app.app_context():
        assert validate_task("Write tests", "Add pytest suite", "2027-01-15T14:30", "High", "Pending") == []

        errors = validate_task("", None, "bad-date", "Urgent", "Unknown")
        assert "Title is required" in errors
        assert "Invalid due date format" in errors
        assert "Invalid priority level" in errors
        assert "Invalid status" in errors
