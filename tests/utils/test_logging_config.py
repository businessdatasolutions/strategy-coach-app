import pytest
import logging
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.logging_config import (
    setup_logging,
    get_logging_config,
    JSONFormatter,
    ContextFilter,
    get_logger,
    log_agent_interaction,
    log_api_request,
    log_strategy_map_update,
    log_error_with_context
)
from src.utils.config import Settings


class TestLoggingConfig:
    """Test logging configuration functionality."""
    
    def test_get_logging_config_debug_mode(self):
        """Test logging config in debug mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logs_dir = Path(temp_dir)
            config = get_logging_config("DEBUG", True, logs_dir)
            
            assert config["version"] == 1
            assert "console" in config["handlers"]
            assert "file" in config["handlers"]
            assert "error_file" in config["handlers"]
            
            # Check debug formatting
            assert config["handlers"]["console"]["formatter"] == "detailed"
    
    def test_get_logging_config_production_mode(self):
        """Test logging config in production mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logs_dir = Path(temp_dir)
            config = get_logging_config("INFO", False, logs_dir)
            
            # Check production formatting
            assert config["handlers"]["console"]["formatter"] == "standard"
            assert config["handlers"]["console"]["level"] == "INFO"


class TestJSONFormatter:
    """Test JSON formatter."""
    
    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.funcName = "test_function"
        record.module = "test_module"
        
        result = formatter.format(record)
        parsed = json.loads(result)
        
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert parsed["module"] == "test_module"
        assert parsed["function"] == "test_function"
        assert parsed["line"] == 10
        assert "timestamp" in parsed
    
    def test_format_record_with_context(self):
        """Test formatting a record with context."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py", 
            lineno=20,
            msg="Error occurred",
            args=(),
            exc_info=None
        )
        record.funcName = "error_function"
        record.module = "error_module"
        record.session_id = "test_session_123"
        record.agent_type = "WHY"
        
        result = formatter.format(record)
        parsed = json.loads(result)
        
        assert parsed["session_id"] == "test_session_123"
        assert parsed["agent_type"] == "WHY"


class TestContextFilter:
    """Test context filter."""
    
    def test_filter_adds_context(self):
        """Test that context filter adds context to records."""
        context_filter = ContextFilter(session_id="test_123", user_id="user_456")
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None
        )
        
        result = context_filter.filter(record)
        
        assert result is True
        assert hasattr(record, "session_id")
        assert hasattr(record, "user_id")
        assert record.session_id == "test_123"
        assert record.user_id == "user_456"


class TestLoggerUtilities:
    """Test logging utility functions."""
    
    @patch("src.utils.logging_config.logging.getLogger")
    def test_get_logger_with_context(self, mock_get_logger):
        """Test getting logger with context."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger = get_logger("test_logger", session_id="test_123")
        
        mock_get_logger.assert_called_once_with("test_logger")
        mock_logger.addFilter.assert_called_once()
    
    @patch("src.utils.logging_config.get_logger")
    def test_log_agent_interaction(self, mock_get_logger):
        """Test logging agent interactions."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_agent_interaction(
            agent_type="WHY",
            session_id="test_session",
            input_data="input",
            output_data="output", 
            processing_time=0.5
        )
        
        mock_get_logger.assert_called_once_with(
            "src.agents", 
            agent_type="WHY", 
            session_id="test_session"
        )
        mock_logger.info.assert_called_once()
        
        # Check the call arguments
        call_args = mock_logger.info.call_args
        assert "Agent interaction completed" in call_args[0][0]
        extra_data = call_args[1]["extra"]
        assert extra_data["agent_type"] == "WHY"
        assert extra_data["session_id"] == "test_session"
        assert extra_data["processing_time_ms"] == 500.0
    
    @patch("src.utils.logging_config.get_logger")
    def test_log_api_request(self, mock_get_logger):
        """Test logging API requests."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_api_request(
            method="POST",
            path="/conversation/start",
            status_code=200,
            processing_time=0.1,
            user_id="user_123"
        )
        
        mock_get_logger.assert_called_once_with("src.api")
        mock_logger.info.assert_called_once()
        
        call_args = mock_logger.info.call_args
        assert "POST /conversation/start - 200" in call_args[0][0]
        extra_data = call_args[1]["extra"]
        assert extra_data["method"] == "POST"
        assert extra_data["status_code"] == 200
        assert extra_data["user_id"] == "user_123"
    
    @patch("src.utils.logging_config.get_logger")
    def test_log_strategy_map_update(self, mock_get_logger):
        """Test logging strategy map updates."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_strategy_map_update(
            session_id="test_session",
            update_type="why_section",
            fields_updated=["purpose", "belief"]
        )
        
        mock_get_logger.assert_called_once_with(
            "src.agents.strategy_map", 
            session_id="test_session"
        )
        mock_logger.info.assert_called_once()
        
        call_args = mock_logger.info.call_args
        assert "Strategy map updated: why_section" in call_args[0][0]
        extra_data = call_args[1]["extra"]
        assert extra_data["update_type"] == "why_section"
        assert extra_data["fields_updated"] == ["purpose", "belief"]
        assert extra_data["fields_count"] == 2
    
    @patch("logging.getLogger")
    def test_log_error_with_context(self, mock_get_logger):
        """Test logging errors with context."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        test_error = ValueError("Test error")
        context = {"session_id": "test_123", "operation": "test_op"}
        
        log_error_with_context(test_error, context, "test_logger")
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert "ValueError: Test error" in call_args[0][0]
        assert call_args[1]["exc_info"] is True
        extra_data = call_args[1]["extra"]
        assert extra_data["error_type"] == "ValueError"
        assert extra_data["session_id"] == "test_123"
        assert extra_data["operation"] == "test_op"


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for logging setup."""
    
    def test_setup_logging_creates_directories(self, temp_dir):
        """Test that setup_logging creates necessary directories."""
        test_settings = Settings(
            logs_dir=str(temp_dir / "logs"),
            log_level="DEBUG",
            debug=True
        )
        
        with patch("src.utils.logging_config.get_settings", return_value=test_settings):
            setup_logging()
            
            logs_dir = Path(test_settings.logs_dir)
            assert logs_dir.exists()
            assert logs_dir.is_dir()