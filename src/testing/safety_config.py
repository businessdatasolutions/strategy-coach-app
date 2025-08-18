"""
Safety Configuration and Stopping Mechanisms for Testing Agent.

Defines comprehensive safeguards to prevent runaway testing and ensure
controlled, bounded execution of automated tests.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TestingSafetyConfig:
    """Configuration for testing agent safety mechanisms."""
    
    # Interaction Limits
    max_total_interactions: int = 20           # Maximum total interactions per test
    max_interactions_per_stage: int = 5       # Maximum interactions per methodology stage
    max_test_duration_minutes: int = 10       # Maximum test duration
    
    # Response Timeouts
    response_timeout_seconds: int = 30         # Timeout waiting for agent response
    page_load_timeout_seconds: int = 30       # Timeout for page loading
    element_wait_timeout_seconds: int = 10    # Timeout waiting for UI elements
    
    # Error Handling
    max_consecutive_errors: int = 3           # Stop after N consecutive errors
    max_total_errors: int = 5                 # Stop after N total errors
    retry_attempts: int = 2                   # Retry failed operations N times
    
    # Emergency Stop Conditions
    emergency_stop_keywords: List[str] = None # Keywords that trigger immediate stop
    browser_crash_detection: bool = True      # Stop if browser becomes unresponsive
    api_health_check_interval: int = 5        # Check API health every N interactions
    
    # Screenshot and Logging Limits
    max_screenshots: int = 50                 # Maximum screenshots per test
    max_log_file_size_mb: int = 10           # Maximum log file size
    
    def __post_init__(self):
        """Initialize default emergency stop keywords."""
        if self.emergency_stop_keywords is None:
            self.emergency_stop_keywords = [
                "error occurred",
                "something went wrong", 
                "api error",
                "service unavailable",
                "internal server error",
                "timeout",
                "connection refused"
            ]


class TestingSafetyManager:
    """Manages safety mechanisms and stop conditions for testing agent."""
    
    def __init__(self, config: Optional[TestingSafetyConfig] = None):
        """Initialize safety manager with configuration."""
        self.config = config or TestingSafetyConfig()
        self.reset_counters()
    
    def reset_counters(self) -> None:
        """Reset all safety counters."""
        self.total_interactions = 0
        self.current_stage_interactions = 0
        self.consecutive_errors = 0
        self.total_errors = 0
        self.test_start_time = None
        self.screenshots_taken = 0
        self.current_stage = "UNKNOWN"
    
    def start_test(self, test_name: str) -> None:
        """Start a test and initialize safety monitoring."""
        from datetime import datetime
        self.test_start_time = datetime.now()
        self.reset_counters()
        print(f"🛡️ Safety Manager: Started monitoring test '{test_name}'")
        self._log_safety_config()
    
    def before_interaction(self, interaction_count: int, stage: str) -> bool:
        """
        Check safety conditions before sending an interaction.
        
        Returns:
            True if safe to proceed, False if should stop
        """
        self.total_interactions = interaction_count
        
        # Update stage and reset stage counter if changed
        if stage != self.current_stage:
            self.current_stage = stage
            self.current_stage_interactions = 0
        
        self.current_stage_interactions += 1
        
        # Check interaction limits
        if self.total_interactions >= self.config.max_total_interactions:
            print(f"🛑 STOP: Maximum total interactions ({self.config.max_total_interactions}) reached")
            return False
        
        if self.current_stage_interactions >= self.config.max_interactions_per_stage:
            print(f"🛑 STOP: Maximum interactions per stage ({self.config.max_interactions_per_stage}) reached for {stage}")
            return False
        
        # Check time limits
        if self.test_start_time:
            from datetime import datetime
            elapsed = (datetime.now() - self.test_start_time).total_seconds() / 60
            if elapsed >= self.config.max_test_duration_minutes:
                print(f"🛑 STOP: Maximum test duration ({self.config.max_test_duration_minutes} minutes) reached")
                return False
        
        # Check error limits
        if self.consecutive_errors >= self.config.max_consecutive_errors:
            print(f"🛑 STOP: Maximum consecutive errors ({self.config.max_consecutive_errors}) reached")
            return False
        
        if self.total_errors >= self.config.max_total_errors:
            print(f"🛑 STOP: Maximum total errors ({self.config.max_total_errors}) reached")
            return False
        
        return True
    
    def after_interaction(self, response: str, error: Optional[str] = None) -> bool:
        """
        Check safety conditions after receiving a response.
        
        Returns:
            True if safe to continue, False if should stop
        """
        # Handle errors
        if error:
            self.total_errors += 1
            self.consecutive_errors += 1
            print(f"⚠️ Error detected: {error}")
        else:
            self.consecutive_errors = 0  # Reset consecutive error counter
        
        # Check for emergency stop keywords in response
        if response:
            response_lower = response.lower()
            for keyword in self.config.emergency_stop_keywords:
                if keyword in response_lower:
                    print(f"🚨 EMERGENCY STOP: Detected keyword '{keyword}' in response")
                    return False
        
        return True
    
    def check_api_health(self, base_url: str) -> bool:
        """Check if API server is still responding."""
        try:
            import requests
            response = requests.get(f"{base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ API health check failed: {e}")
            return False
    
    def should_take_screenshot(self, interaction_count: int) -> bool:
        """Determine if screenshot should be taken (with limits)."""
        if self.screenshots_taken >= self.config.max_screenshots:
            print(f"📸 Screenshot limit ({self.config.max_screenshots}) reached")
            return False
        
        # Take screenshot every 3rd interaction
        return interaction_count % 3 == 0
    
    def record_screenshot(self) -> None:
        """Record that a screenshot was taken."""
        self.screenshots_taken += 1
    
    def get_safety_status(self) -> dict:
        """Get current safety status and limits."""
        return {
            "total_interactions": self.total_interactions,
            "max_total_interactions": self.config.max_total_interactions,
            "current_stage_interactions": self.current_stage_interactions,
            "max_interactions_per_stage": self.config.max_interactions_per_stage,
            "total_errors": self.total_errors,
            "consecutive_errors": self.consecutive_errors,
            "screenshots_taken": self.screenshots_taken,
            "max_screenshots": self.config.max_screenshots,
            "test_duration_minutes": self._get_test_duration(),
            "max_test_duration_minutes": self.config.max_test_duration_minutes,
            "safety_status": "SAFE" if self._is_safe() else "UNSAFE"
        }
    
    def _get_test_duration(self) -> float:
        """Get current test duration in minutes."""
        if not self.test_start_time:
            return 0.0
        
        from datetime import datetime
        return (datetime.now() - self.test_start_time).total_seconds() / 60
    
    def _is_safe(self) -> bool:
        """Check if current state is safe to continue."""
        return (
            self.total_interactions < self.config.max_total_interactions and
            self.current_stage_interactions < self.config.max_interactions_per_stage and
            self.consecutive_errors < self.config.max_consecutive_errors and
            self.total_errors < self.config.max_total_errors and
            self._get_test_duration() < self.config.max_test_duration_minutes
        )
    
    def _log_safety_config(self) -> None:
        """Log the current safety configuration."""
        print(f"🛡️ Safety Limits:")
        print(f"   • Max Total Interactions: {self.config.max_total_interactions}")
        print(f"   • Max Per Stage: {self.config.max_interactions_per_stage}")
        print(f"   • Max Duration: {self.config.max_test_duration_minutes} minutes")
        print(f"   • Max Errors: {self.config.max_total_errors} total, {self.config.max_consecutive_errors} consecutive")
        print(f"   • Max Screenshots: {self.config.max_screenshots}")
        print(f"   • Response Timeout: {self.config.response_timeout_seconds}s")


def create_safe_testing_config() -> TestingSafetyConfig:
    """Create a conservative safety configuration for testing."""
    return TestingSafetyConfig(
        max_total_interactions=15,        # Conservative limit for WHY phase
        max_interactions_per_stage=8,    # Enough for complete methodology
        max_test_duration_minutes=5,     # 5 minutes max per test
        response_timeout_seconds=30,     # 30 second response timeout
        max_consecutive_errors=2,        # Stop after 2 consecutive errors
        max_total_errors=3,              # Stop after 3 total errors
        max_screenshots=20               # Reasonable screenshot limit
    )