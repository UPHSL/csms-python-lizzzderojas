
"""Shared pytest fixtures for the CSMS application."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from csms import create_app


@pytest.fixture()
def app(tmp_path) -> Flask:
    """Create a configured application with a temporary database."""
    database_file = tmp_path / "test.db"

    application = create_app(
        {
            "TESTING": True,
            "DEBUG": False,
            "SECRET_KEY": "test-secret-key",
            "DATABASE": database_file,
        }
    )

    yield application


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    """Create a Flask test client."""
    return app.test_client()
