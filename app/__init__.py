import threading

from flask import Flask, current_app

from app.config import Config
from app.context import register_context
from app.db import auto_init_db, reset_database
from app.routes import register_blueprints


def _register_cli(app: Flask) -> None:
    """Register Flask CLI commands for database management."""

    @app.cli.command("db-init")
    def db_init_command() -> None:
        """Auto-initialize the database schema without wiping existing data."""
        auto_init_db(app.config["DATABASE_PATH"])

    @app.cli.command("db-reset")
    def db_reset_command() -> None:
        """Reset the database (WARNING: deletes all existing data)."""
        reset_database(app.config["DATABASE_PATH"])


def _register_db_auto_init(app: Flask) -> None:
    """Ensure the database schema is initialized once before the first HTTP request."""
    init_lock = threading.Lock()

    @app.before_request
    def ensure_db_initialized() -> None:
        if current_app.extensions.get("db_initialized"):
            return
        with init_lock:
            if not current_app.extensions.get("db_initialized"):
                auto_init_db(current_app.config["DATABASE_PATH"])
                current_app.extensions["db_initialized"] = True


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory for the Flask Todo App."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    register_blueprints(app)
    register_context(app)
    _register_db_auto_init(app)
    _register_cli(app)

    return app
