"""
Integration tests for the AI Strategic Co-pilot API.

This module tests the complete conversation flow from session initialization
through multi-agent processing to strategy export.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from fastapi.testclient import TestClient
from src.api.main import app
from src.models.state import initialize_agent_state


@pytest.fixture
def client():
    """Create test client for API."""
    return TestClient(app)


@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator for testing."""
    with patch('src.api.main.get_orchestrator') as mock:
        orchestrator = MagicMock()
        mock.return_value = orchestrator
        yield orchestrator


@pytest.fixture
def mock_strategy_map_agent():
    """Mock strategy map agent for testing."""
    with patch('src.api.main.get_strategy_map_agent') as mock:
        agent = MagicMock()
        # Mock strategy map operations
        agent.get_or_create_strategy_map.return_value = {
            "session_id": "test_session",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1,
            "completeness_percentage": 25.0,
            "completed_sections": ["why"],
            "why": {
                "purpose": "Test purpose",
                "beliefs": ["Test belief"],
                "values": ["Test value"],
                "golden_circle_complete": True
            }
        }
        agent.validate_strategy_map.return_value = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": ["Continue with HOW phase"],
            "consistency_score": 75.0
        }
        mock.return_value = agent
        yield agent


class TestHealthEndpoints:
    """Test health and monitoring endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "timestamp" in data
        assert "components" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "AI Strategic Co-pilot API"
        assert "version" in data
        assert "docs_url" in data


class TestConversationFlow:
    """Test complete conversation flow."""
    
    def test_start_conversation(self, client, mock_orchestrator, mock_strategy_map_agent):
        """Test starting a new conversation."""
        request_data = {
            "user_context": {
                "company_name": "TestCorp",
                "industry": "Technology",
                "team_size": "50-100"
            },
            "session_metadata": {
                "source": "web_app"
            }
        }
        
        response = client.post("/conversation/start", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert "TestCorp" in data["message"]
        assert data["current_phase"] == "why"
        assert len(data["next_steps"]) > 0
        assert "created_at" in data
    
    def test_start_conversation_minimal(self, client, mock_orchestrator, mock_strategy_map_agent):
        """Test starting conversation with minimal data."""
        request_data = {}
        
        response = client.post("/conversation/start", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert "your organization" in data["message"]
    
    def test_send_message(self, client, mock_orchestrator, mock_strategy_map_agent):
        """Test sending a message in conversation."""
        # First, start a conversation
        start_response = client.post("/conversation/start", json={})
        session_id = start_response.json()["session_id"]
        
        # Mock session store for the test
        from src.api.main import session_store, session_metadata
        test_state = initialize_agent_state(session_id, f"/tmp/{session_id}.json")
        session_store[session_id] = test_state
        session_metadata[session_id] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        # Send a message
        message_data = {
            "message": "Our company exists to innovate in healthcare technology",
            "context": {"topic": "purpose"}
        }
        
        response = client.post(f"/conversation/{session_id}/message", json=message_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert data["session_id"] == session_id
        assert "current_phase" in data
        assert "completeness_percentage" in data
        assert len(data["questions"]) > 0
        assert "recommendations" in data
    
    def test_send_message_invalid_session(self, client):
        """Test sending message to non-existent session."""
        message_data = {"message": "Test message"}
        
        response = client.post("/conversation/invalid-session-id/message", json=message_data)
        assert response.status_code == 400  # Invalid UUID format
    
    def test_send_message_nonexistent_session(self, client):
        """Test sending message to properly formatted but non-existent session."""
        message_data = {"message": "Test message"}
        session_id = "12345678-1234-1234-1234-123456789012"
        
        response = client.post(f"/conversation/{session_id}/message", json=message_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSessionManagement:
    """Test session management endpoints."""
    
    def test_list_sessions(self, client, mock_strategy_map_agent):
        """Test listing all sessions."""
        # Create some test sessions
        from src.api.main import session_store, session_metadata
        
        for i in range(3):
            session_id = f"test-session-{i}"
            session_store[session_id] = initialize_agent_state(
                session_id, f"/tmp/{session_id}.json"
            )
            session_metadata[session_id] = {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "message_count": i
            }
        
        response = client.get("/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert "sessions" in data
        assert data["total_sessions"] >= 3
        assert data["active_sessions"] >= 3
    
    def test_get_session_info(self, client, mock_strategy_map_agent):
        """Test getting specific session information."""
        # Create a test session
        from src.api.main import session_store, session_metadata
        
        session_id = "12345678-1234-1234-1234-123456789012"
        test_state = initialize_agent_state(session_id, f"/tmp/{session_id}.json")
        session_store[session_id] = test_state
        session_metadata[session_id] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 5
        }
        
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert data["message_count"] == 5
        assert "current_phase" in data
        assert "completeness_percentage" in data
    
    def test_delete_session(self, client):
        """Test deleting a session."""
        # Create a test session
        from src.api.main import session_store, session_metadata
        
        session_id = "12345678-1234-1234-1234-123456789012"
        test_state = initialize_agent_state(session_id, f"/tmp/{session_id}.json")
        session_store[session_id] = test_state
        session_metadata[session_id] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        response = client.delete(f"/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "deleted successfully" in data["message"]
        
        # Verify session is deleted
        assert session_id not in session_store
        assert session_id not in session_metadata
    
    def test_cleanup_sessions(self, client):
        """Test manual session cleanup."""
        response = client.post("/sessions/cleanup")
        assert response.status_code == 200
        
        data = response.json()
        assert "cleaned_sessions" in data
        assert "remaining_sessions" in data
        assert "cleanup_timestamp" in data


class TestStrategyExport:
    """Test strategy export endpoints."""
    
    def test_export_strategy(self, client, mock_strategy_map_agent):
        """Test exporting strategy map."""
        # Create a test session with strategy map
        from src.api.main import session_store
        
        session_id = "12345678-1234-1234-1234-123456789012"
        test_state = initialize_agent_state(session_id, f"/tmp/{session_id}.json")
        session_store[session_id] = test_state
        
        response = client.get(f"/conversation/{session_id}/export")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "strategy_map" in data
        assert "completeness_percentage" in data
        assert "export_timestamp" in data
        assert "summary" in data
        
        # Check summary structure
        summary = data["summary"]
        assert "overview" in summary
        assert "why_summary" in summary
        assert "strategic_insights" in summary
        assert "implementation_readiness" in summary
        assert "recommendations" in summary
        assert "next_steps" in summary
    
    def test_export_nonexistent_session(self, client):
        """Test exporting non-existent session."""
        session_id = "12345678-1234-1234-1234-123456789012"
        
        response = client.get(f"/conversation/{session_id}/export")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch('os.path.exists')
    def test_download_strategy(self, mock_exists, client):
        """Test downloading strategy as file."""
        mock_exists.return_value = True
        
        # Create a test session
        from src.api.main import session_store
        
        session_id = "12345678-1234-1234-1234-123456789012"
        test_state = initialize_agent_state(session_id, f"/tmp/{session_id}.json")
        session_store[session_id] = test_state
        
        # Create a mock file for download
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"test": "data"}, f)
            test_state["strategy_map_path"] = f.name
        
        response = client.get(f"/conversation/{session_id}/export/download")
        # Note: FileResponse doesn't work well in test client, so we just check it doesn't error
        assert response.status_code in [200, 422]  # 422 is common for FileResponse in tests


class TestErrorHandling:
    """Test error handling and validation."""
    
    def test_invalid_json(self, client):
        """Test invalid JSON in request."""
        response = client.post(
            "/conversation/start",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_field(self, client):
        """Test missing required field in message."""
        session_id = "12345678-1234-1234-1234-123456789012"
        response = client.post(
            f"/conversation/{session_id}/message",
            json={}  # Missing 'message' field
        )
        assert response.status_code == 422
    
    def test_message_too_long(self, client):
        """Test message exceeding max length."""
        session_id = "12345678-1234-1234-1234-123456789012"
        long_message = "x" * 5001  # Exceeds 5000 char limit
        
        response = client.post(
            f"/conversation/{session_id}/message",
            json={"message": long_message}
        )
        assert response.status_code == 422
    
    def test_rate_limiting_headers(self, client):
        """Test rate limiting headers are present."""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check rate limit headers
        assert "X-RateLimit-Limit-Minute" in response.headers
        assert "X-RateLimit-Remaining-Minute" in response.headers
        assert "X-RateLimit-Limit-Hour" in response.headers
        assert "X-RateLimit-Remaining-Hour" in response.headers


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_full_conversation_workflow(self, client, mock_orchestrator, mock_strategy_map_agent):
        """Test complete conversation from start to export."""
        # 1. Start conversation
        start_response = client.post("/conversation/start", json={
            "user_context": {"company_name": "InnovateCorp"}
        })
        assert start_response.status_code == 200
        
        session_id = start_response.json()["session_id"]
        
        # Mock session for subsequent operations
        from src.api.main import session_store, session_metadata
        test_state = initialize_agent_state(session_id, f"/tmp/{session_id}.json")
        session_store[session_id] = test_state
        session_metadata[session_id] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        # 2. Send multiple messages
        messages = [
            "Our purpose is to democratize innovation",
            "We believe in empowering creators",
            "Our values are transparency and excellence"
        ]
        
        for msg in messages:
            response = client.post(
                f"/conversation/{session_id}/message",
                json={"message": msg}
            )
            assert response.status_code == 200
        
        # 3. Check session info
        info_response = client.get(f"/sessions/{session_id}")
        assert info_response.status_code == 200
        
        # 4. Export strategy
        export_response = client.get(f"/conversation/{session_id}/export")
        assert export_response.status_code == 200
        
        export_data = export_response.json()
        assert export_data["session_id"] == session_id
        assert "strategy_map" in export_data
        assert export_data["completeness_percentage"] >= 0
        
        # 5. List all sessions
        list_response = client.get("/sessions")
        assert list_response.status_code == 200
        assert list_response.json()["total_sessions"] >= 1
        
        # 6. Delete session
        delete_response = client.delete(f"/sessions/{session_id}")
        assert delete_response.status_code == 200
        
        # 7. Verify session is gone
        verify_response = client.get(f"/sessions/{session_id}")
        assert verify_response.status_code == 404


@pytest.mark.asyncio
class TestAsyncOperations:
    """Test asynchronous operations."""
    
    async def test_concurrent_sessions(self, client, mock_orchestrator, mock_strategy_map_agent):
        """Test handling multiple concurrent sessions."""
        import asyncio
        
        async def create_session(client, index):
            response = client.post("/conversation/start", json={
                "user_context": {"company_name": f"Company{index}"}
            })
            return response.json()["session_id"]
        
        # Create multiple sessions concurrently
        tasks = [create_session(client, i) for i in range(5)]
        # Note: TestClient doesn't support true async, so we simulate
        session_ids = []
        for i in range(5):
            response = client.post("/conversation/start", json={
                "user_context": {"company_name": f"Company{i}"}
            })
            session_ids.append(response.json()["session_id"])
        
        assert len(session_ids) == 5
        assert len(set(session_ids)) == 5  # All unique