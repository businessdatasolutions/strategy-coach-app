"""
Basic tests to verify pytest configuration is working.
"""
import pytest


def test_basic_assertion():
    """Test basic assertion works."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    text = "AI Strategic Co-pilot"
    assert "Strategic" in text
    assert text.startswith("AI")


@pytest.mark.unit
def test_marked_unit():
    """Test with unit marker."""
    assert True


@pytest.mark.integration
def test_marked_integration():
    """Test with integration marker.""" 
    assert True


def test_pytest_working():
    """Test that pytest is properly configured."""
    # This test should always pass
    assert True