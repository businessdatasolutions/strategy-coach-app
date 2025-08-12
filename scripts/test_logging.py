#!/usr/bin/env python3
"""
Test script to demonstrate logging functionality.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import (
    setup_logging,
    get_logger,
    log_agent_interaction,
    log_api_request,
    log_strategy_map_update,
    log_error_with_context
)


def main():
    """Demonstrate logging functionality."""
    print("🚀 Testing AI Strategic Co-pilot Logging System")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Get various loggers
    app_logger = get_logger("src.app")
    agent_logger = get_logger("src.agents", session_id="demo_session_123")
    api_logger = get_logger("src.api")
    
    # Basic logging
    app_logger.info("Application started successfully")
    app_logger.debug("This is a debug message")
    app_logger.warning("This is a warning message")
    
    # Agent interaction logging
    log_agent_interaction(
        agent_type="WHY",
        session_id="demo_session_123",
        input_data="I want to develop a strategy for my startup",
        output_data="Let's start by exploring your core purpose...",
        processing_time=0.25
    )
    
    # API request logging
    log_api_request(
        method="POST",
        path="/conversation/start",
        status_code=200,
        processing_time=0.15,
        user_id="demo_user"
    )
    
    # Strategy map update logging
    log_strategy_map_update(
        session_id="demo_session_123",
        update_type="why_section",
        fields_updated=["purpose", "belief", "values"]
    )
    
    # Error logging
    try:
        # Simulate an error
        raise ValueError("This is a simulated error for demonstration")
    except Exception as e:
        log_error_with_context(
            error=e,
            context={
                "session_id": "demo_session_123",
                "operation": "demo_operation",
                "user_input": "test input"
            },
            logger_name="src.app"
        )
    
    # Structured logging with context
    agent_logger.info(
        "Processing user message",
        extra={
            "message_length": 45,
            "user_intent": "strategy_development",
            "processing_stage": "input_analysis"
        }
    )
    
    print("\n✅ Logging test completed!")
    print("📁 Check the logs/ directory for output files")
    print("📊 Console output shows formatted logs")
    print("🔍 JSON error logs provide structured data for monitoring")


if __name__ == "__main__":
    main()