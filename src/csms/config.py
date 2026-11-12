"""Configuration settings for the CSMS Flask application."""

import os

from csms._version import __version__


class BaseConfig:
    """Settings shared by all application environments."""

    APP_NAME = "Community Services Management System"
    APP_VERSION = __version__
    CURRENT_SPRINT = "Sprint 0 - Developer Onboarding"

    SECRET_KEY = os.environ.get(
        "CSMS_SECRET_KEY",
        "development-only-secret-key",
    )


class DevelopmentConfig(BaseConfig):
    """Local development configuration."""

    DEBUG = True


class TestingConfig(BaseConfig):
    """Automated testing configuration."""

    TESTING = True
    DEBUG = False
    SECRET_KEY = "testing-secret-key"