import os
from typing import Type
from .base import BaseSettings
from .development import DevelopmentSettings
from .testing import TestingSettings
from .staging import StagingSettings
from .production import ProductionSettings


def get_settings() -> BaseSettings:
    """Get environment-specific settings."""
    env = os.getenv("ENVIRONMENT", "development")
    settings_map = {
        "development": DevelopmentSettings,
        "testing": TestingSettings,
        "staging": StagingSettings,
        "production": ProductionSettings,
    }
    settings_class = settings_map[env]
    return settings_class()  # Make sure to instantiate the class


# Global settings instance
Settings = get_settings
settings = get_settings()