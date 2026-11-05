"""Community Services Management System Flask application."""
"""Create and configure the CSMS Flask application.

    Args:
        test_config: Optional configuration overrides used during testing.

    Returns:
        A configured Flask application.
    """

from flask import Flask

from csms.config import DevelopmentConfig
from csms.database import initialize_database


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    """Create and configure the CSMS Flask application."""
    app = Flask(__name__)

    app.config.from_object(DevelopmentConfig)

    if test_config is not None:
        app.config.update(test_config)

    database_file = app.config.get("DATABASE")

    if database_file is None:
        initialize_database()
    else:
        initialize_database(database_file)

    from csms.ui.routes import main_blueprint

    app.register_blueprint(main_blueprint)

    return app
