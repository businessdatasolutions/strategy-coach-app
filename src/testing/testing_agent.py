"""
Main Playwright-based Testing Agent for AI Strategic Co-pilot.

This module implements automated testing using Playwright browser automation
to simulate realistic user interactions with the strategic coaching system.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from ..core.config import settings

logger = logging.getLogger(__name__)


class StrategyTestingAgent:
    """
    Automated testing agent using Playwright for browser automation.
    
    Tests the Strategy Coach application by simulating realistic user interactions
    and recording the complete journey with screenshots and interaction logs.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        headless: bool = False,
        screenshots_dir: str = "testing/screenshots",
        reports_dir: str = "testing/reports",
        logs_dir: str = "testing/logs"
    ):
        """Initialize the testing agent with configuration."""
        self.base_url = base_url
        self.headless = headless
        self.screenshots_dir = Path(screenshots_dir)
        self.reports_dir = Path(reports_dir)
        self.logs_dir = Path(logs_dir)
        
        # Create directories
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Testing session data
        self.session_id = f"test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.interactions: List[Dict] = []
        self.screenshots: List[str] = []
        self.current_phase = "WHY"
        self.interaction_count = 0
        
        # Browser instances
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def setup_browser(self) -> None:
        """Initialize Playwright browser and context."""
        logger.info("🚀 Setting up Playwright browser...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="StrategyCoach-TestingAgent/1.0"
        )
        
        self.page = await self.context.new_page()
        
        # Enable request/response logging
        self.page.on("request", self._log_request)
        self.page.on("response", self._log_response)
        
        logger.info("✅ Browser setup complete")
    
    async def navigate_to_app(self) -> None:
        """Navigate to the Strategy Coach application."""
        logger.info(f"🌐 Navigating to {self.base_url}")
        
        await self.page.goto(self.base_url)
        await self.page.wait_for_load_state("networkidle")
        
        # Verify the application loaded
        title = await self.page.title()
        if "Strategic Co-pilot" not in title:
            raise Exception(f"Application not loaded correctly. Title: {title}")
        
        logger.info("✅ Application loaded successfully")
    
    async def send_message(self, message: str, take_screenshot: bool = False) -> str:
        """
        Send a message through the chat interface and get the response.
        
        Args:
            message: The message to send
            take_screenshot: Whether to take a screenshot after interaction
            
        Returns:
            The agent's response text
        """
        self.interaction_count += 1
        interaction_start = time.time()
        
        logger.info(f"💬 Interaction {self.interaction_count}: Sending message")
        
        # Find and fill the message input
        message_input = self.page.locator("#messageInput")
        await message_input.fill(message)
        
        # Click send button
        send_button = self.page.locator("#sendButton")
        await send_button.click()
        
        # Wait for response
        await self.page.wait_for_timeout(1000)  # Wait for processing
        
        # Get the latest agent response
        agent_messages = self.page.locator(".message.agent")
        agent_count = await agent_messages.count()
        
        if agent_count > 0:
            latest_response = agent_messages.nth(agent_count - 1)
            response_text = await latest_response.text_content()
        else:
            response_text = "No response received"
        
        interaction_end = time.time()
        
        # Log interaction
        interaction_data = {
            "interaction_id": self.interaction_count,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase,
            "user_message": message,
            "agent_response": response_text,
            "response_time_ms": int((interaction_end - interaction_start) * 1000),
            "session_id": self.session_id
        }
        
        self.interactions.append(interaction_data)
        
        # Take screenshot every 5th interaction or if explicitly requested
        if take_screenshot or (self.interaction_count % 5 == 0):
            await self.take_screenshot(f"interaction_{self.interaction_count}")
        
        logger.info(f"✅ Response received in {interaction_data['response_time_ms']}ms")
        
        return response_text
    
    async def take_screenshot(self, name: str) -> str:
        """Take a screenshot and save it."""
        screenshot_path = self.screenshots_dir / f"{self.session_id}_{name}.png"
        await self.page.screenshot(path=screenshot_path, full_page=True)
        
        self.screenshots.append(str(screenshot_path))
        logger.info(f"📸 Screenshot saved: {screenshot_path.name}")
        
        return str(screenshot_path)
    
    async def check_phase_status(self) -> Dict:
        """Check the current phase status from the UI."""
        try:
            phase_badge = self.page.locator("#currentPhase")
            phase_text = await phase_badge.text_content()
            
            phase_status = self.page.locator("#phaseStatus")
            status_text = await phase_status.text_content()
            
            interaction_count = self.page.locator("#interactionCount")
            count_text = await interaction_count.text_content()
            
            return {
                "current_phase": phase_text.replace(" Phase", "") if phase_text else "WHY",
                "status": status_text or "Unknown",
                "interaction_count": int(count_text) if count_text.isdigit() else 0
            }
        except Exception as e:
            logger.warning(f"Could not read phase status: {e}")
            return {"current_phase": "WHY", "status": "Unknown", "interaction_count": 0}
    
    async def wait_for_response(self, timeout: int = 30000) -> None:
        """Wait for the agent to finish responding."""
        # Wait for loading indicator to disappear
        loading = self.page.locator("#loadingIndicator.show")
        if await loading.count() > 0:
            await loading.wait_for(state="detached", timeout=timeout)
    
    async def save_interaction_log(self) -> str:
        """Save the complete interaction log as JSON."""
        log_path = self.logs_dir / f"{self.session_id}_interactions.json"
        
        log_data = {
            "session_id": self.session_id,
            "start_time": self.interactions[0]["timestamp"] if self.interactions else None,
            "end_time": self.interactions[-1]["timestamp"] if self.interactions else None,
            "total_interactions": len(self.interactions),
            "screenshots_taken": len(self.screenshots),
            "test_configuration": {
                "base_url": self.base_url,
                "headless": self.headless,
                "browser": "chromium"
            },
            "interactions": self.interactions,
            "screenshots": self.screenshots
        }
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Interaction log saved: {log_path}")
        return str(log_path)
    
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        logger.info("🧹 Browser cleanup complete")
    
    def _log_request(self, request) -> None:
        """Log HTTP requests for debugging."""
        if "/api/" in request.url:
            logger.debug(f"🔄 API Request: {request.method} {request.url}")
    
    def _log_response(self, response) -> None:
        """Log HTTP responses for debugging."""
        if "/api/" in response.url:
            logger.debug(f"✅ API Response: {response.status} {response.url}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("⚠️ This is the base testing agent framework.")
    print("📋 For WHY phase testing, use: python -m src.testing.why_phase_tester")
    print("🎯 For full testing suite, use dedicated phase testers.")