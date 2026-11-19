from flask import Flask

from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.settings import settings_bp
from app.routes.tags import tags_bp
from app.routes.tasks import tasks_bp


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(settings_bp)
