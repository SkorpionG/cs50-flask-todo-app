from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import Config


@pytest.fixture()
def app(tmp_path: Path) -> Iterator[Flask]:
    """Create a Flask application configured with an isolated temporary SQLite database."""

    class TestConfig(Config):
        TESTING = True
        SECRET_KEY = "test-secret-key"
        DATABASE_PATH = tmp_path / "test.db"

    flask_app = create_app(TestConfig)
    yield flask_app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    """Create a Flask test client for the isolated test application."""
    return app.test_client()
