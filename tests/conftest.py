"""
Global pytest configuration and fixtures for the AI Strategic Co-pilot tests.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import Mock
from pathlib import Path

# Import core modules that will be needed across tests
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.config import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with safe defaults."""
    return Settings(
        debug=True,
        log_level="DEBUG",
        llm_provider="anthropic",
        anthropic_api_key="test-key",
        langchain_tracing_v2=False,  # Disable tracing in tests
        session_timeout_minutes=5,
        max_conversation_history=10,
        test_business_case_path="testing/business-cases/business-case-for-testing.md",
        playwright_headless=True,
        playwright_timeout=10000,
    )


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing without actual API calls."""
    mock = Mock()
    mock.invoke.return_value = Mock(content="Mock LLM response")
    mock.ainvoke.return_value = Mock(content="Mock async LLM response")
    return mock


@pytest.fixture
def sample_session_state():
    """Create a sample session state for testing."""
    from src.core.models import SessionState, Phase
    
    return SessionState(
        session_id="test-session-123",
        current_phase=Phase.WHY,
        conversation_history=[],
        why_output=None,
        how_output=None,
        what_output=None,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )


@pytest.fixture
def sample_user_message():
    """Create a sample user message for testing."""
    return {
        "content": "I want to develop a strategy for my software company",
        "timestamp": "2024-01-01T00:00:00Z",
        "type": "user"
    }


@pytest.fixture
def sample_agent_response():
    """Create a sample agent response for testing."""
    return {
        "content": "Great! Let's start by exploring your WHY. What inspired you to start this software company?",
        "timestamp": "2024-01-01T00:00:00Z",
        "type": "agent",
        "phase": "WHY",
        "agent_type": "why_agent"
    }


@pytest.fixture
def business_case_content():
    """Load the AFAS Software business case content for testing."""
    business_case_path = Path("testing/business-cases/business-case-for-testing.md")
    if business_case_path.exists():
        return business_case_path.read_text(encoding="utf-8")
    else:
        # Fallback content for tests when file doesn't exist
        return """
        # Test Business Case: AFAS Software
        
        AFAS Software is a Dutch enterprise software company specializing in ERP and HRM solutions.
        Founded in 1996, the company serves 12,347+ organizations with €324.6M in revenue.
        
        ## Strategic Context
        - Mission: "Inspire better entrepreneurship"
        - Values: Do, Trust, Crazy, Family
        - Current challenge: International expansion opportunities
        """


@pytest.fixture
async def async_mock_llm():
    """Create an async mock LLM for testing async operations."""
    mock = Mock()
    
    async def mock_ainvoke(prompt):
        await asyncio.sleep(0.01)  # Simulate async delay
        return Mock(content=f"Async response to: {prompt[:50]}...")
    
    mock.ainvoke = mock_ainvoke
    return mock


# Markers for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow