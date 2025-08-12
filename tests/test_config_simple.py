import pytest
import os
from unittest.mock import patch

from src.utils.config import Settings, get_settings, setup_environment


def test_settings_creation():
    """Test that Settings can be created successfully."""
    settings = Settings(openai_api_key="test_key")
    assert settings.openai_api_key == "test_key"


def test_api_key_validation_success():
    """Test that API key validation passes with a key."""
    settings = Settings(openai_api_key="test_key")
    settings.validate_api_keys()  # Should not raise


def test_api_key_validation_failure():
    """Test that API key validation fails without keys."""
    settings = Settings()
    with pytest.raises(ValueError):
        settings.validate_api_keys()


def test_get_settings():
    """Test that get_settings returns a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)