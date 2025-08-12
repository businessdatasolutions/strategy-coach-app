import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

from .config import get_settings


def setup_logging() -> None:
    """Setup logging configuration for the application."""
    settings = get_settings()
    
    # Ensure logs directory exists
    logs_dir = Path(settings.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging_config = get_logging_config(settings.log_level, settings.debug, logs_dir)
    logging.config.dictConfig(logging_config)
    
    # Set up LangChain logging if tracing is disabled
    if not settings.langchain_tracing_v2:
        logging.getLogger("langchain").setLevel(logging.WARNING)
        logging.getLogger("langgraph").setLevel(logging.WARNING)
        logging.getLogger("langsmith").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {settings.log_level}, Debug: {settings.debug}")


def get_logging_config(log_level: str, debug: bool, logs_dir: Path) -> Dict[str, Any]:
    """Get the logging configuration dictionary."""
    timestamp = datetime.now().strftime("%Y%m%d")
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "src.utils.logging_config.JSONFormatter",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed" if debug else "standard",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": logs_dir / f"app_{timestamp}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": logs_dir / f"errors_{timestamp}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8"
            }
        },
        "loggers": {
            # Root logger
            "": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            # Application loggers
            "src": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "src.agents": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "src.api": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            # Third-party loggers
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO" if debug else "WARNING",
                "handlers": ["file"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO" if debug else "WARNING",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            },
            "openai": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            },
            "anthropic": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    return config


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "session_id"):
            log_entry["session_id"] = record.session_id
        if hasattr(record, "agent_type"):
            log_entry["agent_type"] = record.agent_type
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        
        return json.dumps(log_entry, default=str)


class ContextFilter(logging.Filter):
    """Add contextual information to log records."""
    
    def __init__(self, **context):
        super().__init__()
        self.context = context
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to the log record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def get_logger(name: str, **context) -> logging.Logger:
    """Get a logger with optional context."""
    logger = logging.getLogger(name)
    
    if context:
        context_filter = ContextFilter(**context)
        logger.addFilter(context_filter)
    
    return logger


def log_agent_interaction(
    agent_type: str,
    session_id: str,
    input_data: str,
    output_data: str,
    processing_time: float
) -> None:
    """Log agent interaction with structured data."""
    logger = get_logger("src.agents", agent_type=agent_type, session_id=session_id)
    logger.info(
        f"Agent interaction completed",
        extra={
            "agent_type": agent_type,
            "session_id": session_id,
            "input_length": len(input_data),
            "output_length": len(output_data),
            "processing_time_ms": round(processing_time * 1000, 2),
            "interaction_type": "agent_response"
        }
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    processing_time: float,
    user_id: str = None
) -> None:
    """Log API request with structured data."""
    logger = get_logger("src.api")
    logger.info(
        f"{method} {path} - {status_code}",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "processing_time_ms": round(processing_time * 1000, 2),
            "user_id": user_id,
            "request_type": "api_call"
        }
    )


def log_strategy_map_update(session_id: str, update_type: str, fields_updated: list) -> None:
    """Log strategy map updates."""
    logger = get_logger("src.agents.strategy_map", session_id=session_id)
    logger.info(
        f"Strategy map updated: {update_type}",
        extra={
            "session_id": session_id,
            "update_type": update_type,
            "fields_updated": fields_updated,
            "fields_count": len(fields_updated),
            "operation_type": "strategy_map_update"
        }
    )


def log_error_with_context(
    error: Exception,
    context: Dict[str, Any] = None,
    logger_name: str = None
) -> None:
    """Log error with additional context."""
    if logger_name:
        logger = get_logger(logger_name)
    else:
        logger = logging.getLogger(__name__)
    
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "operation_type": "error"
    }
    
    if context:
        error_context.update(context)
    
    logger.error(
        f"Error occurred: {type(error).__name__}: {str(error)}",
        exc_info=True,
        extra=error_context
    )