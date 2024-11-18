# app/__init__.py

"""
This module initializes the Flask application, sets up extensions,
and registers blueprints.
"""

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .models import db

migrate = Migrate()
jwt = JWTManager()


def create_app():
    """
    Create and configure the Flask app, initialize extensions,
    and register the blueprints.

    Returns:
        Flask: The initialized Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import the main blueprint inside the function to avoid circular imports
    from .routes import (  # pylint: disable=import-outside-toplevel
        main as main_blueprint,
    )

    app.register_blueprint(main_blueprint)

    return app
