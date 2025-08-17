"""
Basic smoke tests to verify the test setup is working correctly.
"""

from pathlib import Path

import pytest


@pytest.mark.unit
def test_python_imports():
    """Test that basic Python imports work."""
    import asyncio
    import json
    import os
    import sys

    assert True


@pytest.mark.unit
def test_project_structure():
    """Test that the project structure is correctly set up."""
    project_root = Path(__file__).parent.parent

    # Check main directories exist
    assert (project_root / "src").exists()
    assert (project_root / "tests").exists()
    assert (project_root / "frontend").exists()
    assert (project_root / "testing").exists()

    # Check core source directories
    assert (project_root / "src" / "core").exists()
    assert (project_root / "src" / "agents").exists()
    assert (project_root / "src" / "api").exists()
    assert (project_root / "src" / "testing").exists()

    # Check configuration files
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "pytest.ini").exists()
    assert (project_root / ".env.example").exists()


@pytest.mark.unit
def test_settings_import():
    """Test that settings can be imported and initialized."""
    from src.core.config import Settings, settings

    # Test that we can create a Settings instance
    test_settings = Settings()
    assert test_settings.app_name == "AI Strategic Co-pilot"
    assert test_settings.app_version == "2.0.0"

    # Test global settings instance exists
    assert settings is not None


@pytest.mark.unit
def test_fixtures_work(test_settings, sample_session_state, business_case_content):
    """Test that pytest fixtures are working correctly."""
    # Test settings fixture
    assert test_settings.debug is True
    assert test_settings.log_level == "DEBUG"

    # Test session state fixture
    assert sample_session_state.session_id == "test-session-123"
    assert sample_session_state.current_phase.value == "WHY"

    # Test business case fixture
    assert business_case_content is not None
    assert len(business_case_content) > 0
    assert "AFAS Software" in business_case_content


@pytest.mark.unit
def test_mock_llm(mock_llm):
    """Test that the mock LLM fixture works correctly."""
    response = mock_llm.invoke("Test prompt")
    assert response.content == "Mock LLM response"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_mock_llm(async_mock_llm):
    """Test that the async mock LLM fixture works correctly."""
    response = await async_mock_llm.ainvoke("Test async prompt")
    assert "Async response to: Test async prompt" in response.content


@pytest.mark.unit
def test_business_case_file_exists():
    """Test that the business case file exists and is readable."""
    business_case_path = Path("testing/business-cases/business-case-for-testing.md")

    # File should exist
    assert (
        business_case_path.exists()
    ), f"Business case file not found at {business_case_path}"

    # File should be readable
    content = business_case_path.read_text(encoding="utf-8")
    assert len(content) > 100  # Should have substantial content
    assert "AFAS Software" in content


if __name__ == "__main__":
    pytest.main([__file__])
