"""
Tests for src.utils.config module.

This file can be used to test utility-specific configuration logic
separate from the main configuration tests.
"""

import pytest
from src.utils.config import Settings


def test_config_module_import():
    """Test that the config module can be imported correctly."""
    from src.utils import config
    assert hasattr(config, 'Settings')
    assert hasattr(config, 'get_settings')
    assert hasattr(config, 'setup_environment')