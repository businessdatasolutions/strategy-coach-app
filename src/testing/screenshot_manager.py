"""
Screenshot Manager for Automated Testing.

Handles screenshot capture, management, and organization for test reporting.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import Page


class ScreenshotManager:
    """Manages screenshot capture and organization for testing reports."""
    
    def __init__(self, screenshots_dir: str = "testing/screenshots"):
        """Initialize screenshot manager."""
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots: List[Dict] = []
    
    async def capture_screenshot(
        self, 
        page: Page, 
        name: str, 
        session_id: str,
        interaction_count: int = 0,
        description: str = ""
    ) -> str:
        """
        Capture a screenshot with metadata.
        
        Args:
            page: Playwright page instance
            name: Screenshot name identifier
            session_id: Test session identifier
            interaction_count: Current interaction number
            description: Optional description of the screenshot
            
        Returns:
            Path to the saved screenshot
        """
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{session_id}_{interaction_count:03d}_{name}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / filename
        
        # Capture full page screenshot
        await page.screenshot(path=screenshot_path, full_page=True)
        
        # Store metadata
        screenshot_data = {
            "filename": filename,
            "path": str(screenshot_path),
            "name": name,
            "session_id": session_id,
            "interaction_count": interaction_count,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "relative_path": f"screenshots/{filename}"
        }
        
        self.screenshots.append(screenshot_data)
        
        return str(screenshot_path)
    
    async def capture_phase_progression(
        self,
        page: Page,
        phase: str,
        session_id: str,
        interaction_count: int
    ) -> str:
        """Capture screenshot specifically for phase progression."""
        return await self.capture_screenshot(
            page=page,
            name=f"{phase.lower()}_phase_progress",
            session_id=session_id,
            interaction_count=interaction_count,
            description=f"Progress in {phase} phase at interaction {interaction_count}"
        )
    
    async def capture_methodology_stage(
        self,
        page: Page,
        methodology_stage: str,
        session_id: str,
        interaction_count: int
    ) -> str:
        """Capture screenshot for specific methodology stages."""
        return await self.capture_screenshot(
            page=page,
            name=f"methodology_{methodology_stage.lower().replace(' ', '_')}",
            session_id=session_id,
            interaction_count=interaction_count,
            description=f"Simon Sinek methodology: {methodology_stage}"
        )
    
    def get_screenshots_for_report(self) -> List[Dict]:
        """Get screenshot metadata formatted for report generation."""
        return [
            {
                "title": f"Interaction {shot['interaction_count']}: {shot['name'].replace('_', ' ').title()}",
                "path": shot["relative_path"],
                "description": shot["description"],
                "interaction_count": shot["interaction_count"],
                "timestamp": shot["timestamp"]
            }
            for shot in self.screenshots
        ]
    
    def get_screenshot_count(self) -> int:
        """Get total number of screenshots captured."""
        return len(self.screenshots)