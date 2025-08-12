import os
import pytest
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient

from src.utils.config import Settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings with safe defaults."""
    return Settings(
        openai_api_key="test_openai_key",
        anthropic_api_key="test_anthropic_key",
        debug=True,
        log_level="DEBUG",
        strategy_maps_dir="test_data/sessions",
        logs_dir="test_logs",
        langchain_tracing_v2=False,
        session_timeout_minutes=5,  # Shorter for tests
        max_sessions=10,  # Smaller for tests
    )


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_strategy_maps_dir(temp_dir: Path) -> Path:
    """Create a temporary directory for strategy maps."""
    strategy_dir = temp_dir / "sessions"
    strategy_dir.mkdir(exist_ok=True)
    return strategy_dir


@pytest.fixture
def temp_logs_dir(temp_dir: Path) -> Path:
    """Create a temporary directory for logs."""
    logs_dir = temp_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch("src.utils.llm_client.OpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock chat completions
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_instance.chat.completions.create.return_value = mock_response
        
        yield mock_instance


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch("src.utils.llm_client.Anthropic") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock message creation
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response"
        mock_instance.messages.create.return_value = mock_response
        
        yield mock_instance


@pytest.fixture
def sample_conversation_history() -> list:
    """Sample conversation history for testing."""
    return [
        {"role": "user", "content": "I want to develop a strategy for my startup."},
        {"role": "assistant", "content": "I'd be happy to help you develop your strategy. Let's start by exploring the core purpose of your startup. What problem are you trying to solve?"},
        {"role": "user", "content": "We're building a platform to connect remote workers with local co-working spaces."},
    ]


@pytest.fixture
def sample_strategy_map() -> Dict[str, Any]:
    """Sample strategy map for testing."""
    return {
        "session_id": "test_session_123",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "why": {
            "purpose": "To enable remote workers to find productive workspace anywhere",
            "belief": "Productivity increases when people have access to professional environments"
        },
        "stakeholder_customer": {
            "primary_stakeholders": ["Remote workers", "Co-working space owners"],
            "value_propositions": {
                "remote_workers": "Easy access to professional workspaces",
                "space_owners": "Increased utilization and revenue"
            }
        },
        "internal_processes": {
            "core_processes": [
                "Space discovery and matching",
                "Booking and payment processing",
                "Quality assurance and reviews"
            ]
        },
        "learning_growth": {
            "human_capital": ["Tech development skills", "Community management"],
            "information_capital": ["User behavior data", "Space utilization analytics"],
            "organization_capital": ["Platform reliability", "Partner network"]
        },
        "value_creation": {
            "financial_value": {"objective": "Achieve profitability", "measure": "Monthly recurring revenue"},
            "social_value": {"objective": "Enable flexible work", "measure": "Number of successful bookings"}
        }
    }


@pytest.fixture
def test_client(test_settings: Settings) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    from src.api.main import create_app
    
    with patch("src.utils.config.get_settings", return_value=test_settings):
        app = create_app()
        with TestClient(app) as client:
            yield client


@pytest.fixture
def async_client(test_settings: Settings) -> Generator[httpx.AsyncClient, None, None]:
    """Create an async test client for the FastAPI application."""
    from src.api.main import create_app
    
    with patch("src.utils.config.get_settings", return_value=test_settings):
        app = create_app()
        with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before and after each test."""
    # Store original values
    original_env = {
        key: os.environ.get(key) 
        for key in [
            "OPENAI_API_KEY", 
            "ANTHROPIC_API_KEY", 
            "LANGCHAIN_TRACING_V2",
            "LANGSMITH_API_KEY"
        ]
    }
    
    # Set test values
    os.environ.update({
        "OPENAI_API_KEY": "test_openai_key",
        "ANTHROPIC_API_KEY": "test_anthropic_key",
        "LANGCHAIN_TRACING_V2": "false",
    })
    
    yield
    
    # Restore original values
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_strategy_map_file(temp_strategy_maps_dir: Path, sample_strategy_map: Dict[str, Any]):
    """Create a mock strategy map file for testing."""
    import json
    
    session_id = sample_strategy_map["session_id"]
    file_path = temp_strategy_maps_dir / f"{session_id}_strategy_map.json"
    
    with open(file_path, "w") as f:
        json.dump(sample_strategy_map, f, indent=2)
    
    return file_path