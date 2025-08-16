"""
Journey Recording System for Testing Agent
Captures multi-modal documentation of strategic coaching journeys.
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import base64

from playwright.async_api import async_playwright, Page, Browser
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class ConversationSnapshot:
    """Snapshot of a conversation exchange."""
    timestamp: str
    exchange_number: int
    user_message: str
    ai_response: str
    agent_type: str
    phase: str
    completeness: float
    interactive_elements: Optional[Dict[str, Any]]
    response_time: float


@dataclass 
class UISnapshot:
    """Snapshot of UI state."""
    timestamp: str
    description: str
    screenshot_path: str
    page_url: str
    ui_state: Dict[str, Any]
    interactive_elements_visible: bool


@dataclass
class StateSnapshot:
    """Snapshot of system state."""
    timestamp: str
    session_id: str
    current_phase: str
    active_agent: str
    strategy_completeness: float
    conversation_turn: int
    strategy_map_state: Dict[str, Any]
    agent_routing_decision: Dict[str, Any]


class JourneyRecorder:
    """
    Records complete journey with text, visual, and state snapshots.
    """
    
    def __init__(self, output_dir: Path, session_id: str):
        """Initialize recorder with output directory and session ID."""
        self.output_dir = output_dir
        self.session_id = session_id
        self.screenshots_dir = output_dir / "screenshots" / session_id
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Recording storage
        self.conversation_snapshots: List[ConversationSnapshot] = []
        self.ui_snapshots: List[UISnapshot] = []
        self.state_snapshots: List[StateSnapshot] = []
        
        # Recording metadata
        self.recording_start_time = datetime.now()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        logger.info(f"Journey recorder initialized for session {session_id}")
    
    async def initialize_browser(self):
        """Initialize Playwright browser for UI recording."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            
            # Set viewport size
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info("Playwright browser initialized for recording")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            self.browser = None
            self.page = None
    
    async def close_browser(self):
        """Close Playwright browser."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
    
    def capture_conversation_snapshot(self, user_message: str, ai_response: str, 
                                    metadata: Dict[str, Any], response_time: float):
        """Record a conversation exchange."""
        
        snapshot = ConversationSnapshot(
            timestamp=datetime.now().isoformat(),
            exchange_number=len(self.conversation_snapshots) + 1,
            user_message=user_message,
            ai_response=ai_response,
            agent_type=metadata.get("current_agent", "unknown"),
            phase=metadata.get("current_phase", "unknown"),
            completeness=metadata.get("completeness_percentage", 0.0),
            interactive_elements=metadata.get("interactive_elements"),
            response_time=response_time
        )
        
        self.conversation_snapshots.append(snapshot)
        
        logger.debug(f"Captured conversation snapshot {snapshot.exchange_number}")
    
    async def capture_ui_snapshot(self, description: str, url: str = "http://localhost:8081"):
        """Take screenshot of current UI state."""
        
        if not self.page:
            logger.warning("Browser not initialized, skipping UI snapshot")
            return
            
        try:
            # Navigate to URL if needed
            if self.page.url != url:
                await self.page.goto(url)
                await self.page.wait_for_load_state("networkidle")
            
            # Generate screenshot filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            screenshot_name = f"{timestamp}_{description.replace(' ', '_')}.png"
            screenshot_path = self.screenshots_dir / screenshot_name
            
            # Take screenshot
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            # Capture UI state information
            ui_state = await self._extract_ui_state()
            
            # Check for interactive elements
            interactive_visible = await self._check_interactive_elements()
            
            snapshot = UISnapshot(
                timestamp=datetime.now().isoformat(),
                description=description,
                screenshot_path=str(screenshot_path),
                page_url=url,
                ui_state=ui_state,
                interactive_elements_visible=interactive_visible
            )
            
            self.ui_snapshots.append(snapshot)
            
            logger.info(f"Captured UI snapshot: {screenshot_name}")
            
        except Exception as e:
            logger.error(f"Failed to capture UI snapshot: {e}")
    
    async def _extract_ui_state(self) -> Dict[str, Any]:
        """Extract current UI state information."""
        
        try:
            # Extract key UI elements
            ui_state = {}
            
            # Get current phase
            try:
                phase_element = await self.page.wait_for_selector('.text-blue-600', timeout=2000)
                if phase_element:
                    ui_state["current_phase"] = await phase_element.inner_text()
            except:
                ui_state["current_phase"] = "unknown"
            
            # Get completeness percentage
            try:
                completeness_elements = await self.page.query_selector_all('text=/\\d+%/')
                if completeness_elements:
                    completeness_text = await completeness_elements[0].inner_text()
                    ui_state["completeness"] = completeness_text
            except:
                ui_state["completeness"] = "0%"
            
            # Get message count
            try:
                message_elements = await self.page.query_selector_all('.message-fade-in')
                ui_state["message_count"] = len(message_elements)
            except:
                ui_state["message_count"] = 0
            
            # Get current agent
            try:
                agent_element = await self.page.query_selector('text=/Agent/')
                if agent_element:
                    ui_state["current_agent"] = await agent_element.inner_text()
            except:
                ui_state["current_agent"] = "unknown"
                
            return ui_state
            
        except Exception as e:
            logger.error(f"Error extracting UI state: {e}")
            return {}
    
    async def _check_interactive_elements(self) -> bool:
        """Check if interactive selection elements are visible."""
        
        try:
            # Look for interactive selection panel
            interactive_selectors = [
                'text=/Which of these/',
                '[class*="interactive"]',
                'text=/core beliefs/',
                'button:has-text("Submit Selection")'
            ]
            
            for selector in interactive_selectors:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking interactive elements: {e}")
            return False
    
    def capture_state_snapshot(self, session_id: str, agent_routing: Dict[str, Any], 
                              strategy_map: Dict[str, Any]):
        """Record system state snapshot."""
        
        snapshot = StateSnapshot(
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            current_phase=agent_routing.get("current_phase", "unknown"),
            active_agent=agent_routing.get("current_agent", "unknown"), 
            strategy_completeness=strategy_map.get("completeness_percentage", 0.0),
            conversation_turn=len(self.conversation_snapshots),
            strategy_map_state=strategy_map,
            agent_routing_decision=agent_routing
        )
        
        self.state_snapshots.append(snapshot)
        
        logger.debug(f"Captured state snapshot at {snapshot.strategy_completeness}% completeness")
    
    async def capture_phase_transition(self, from_phase: str, to_phase: str):
        """Capture special snapshot at phase transitions."""
        
        description = f"phase_transition_{from_phase}_to_{to_phase}"
        await self.capture_ui_snapshot(description)
        
        logger.info(f"Captured phase transition: {from_phase} → {to_phase}")
    
    async def capture_error_scenario(self, error_description: str, error_details: Dict[str, Any]):
        """Capture snapshot during error scenarios."""
        
        description = f"error_{error_description.replace(' ', '_')}"
        await self.capture_ui_snapshot(description)
        
        # Log error details
        logger.error(f"Captured error scenario: {error_description}")
        logger.error(f"Error details: {json.dumps(error_details, indent=2)}")
    
    def generate_journey_report(self, journey_result: Any) -> Dict[str, Any]:
        """Generate comprehensive journey report with all snapshots."""
        
        report = {
            "journey_metadata": {
                "session_id": self.session_id,
                "recording_start": self.recording_start_time.isoformat(),
                "recording_end": datetime.now().isoformat(),
                "total_duration": (datetime.now() - self.recording_start_time).total_seconds()
            },
            "journey_summary": {
                "success": getattr(journey_result, 'success', False),
                "total_exchanges": getattr(journey_result, 'total_exchanges', 0),
                "phases_completed": getattr(journey_result, 'phases_completed', []),
                "final_completeness": getattr(journey_result, 'final_completeness', 0.0),
                "errors": getattr(journey_result, 'errors', [])
            },
            "recording_stats": {
                "conversation_snapshots": len(self.conversation_snapshots),
                "ui_snapshots": len(self.ui_snapshots),
                "state_snapshots": len(self.state_snapshots),
                "screenshots_captured": len(list(self.screenshots_dir.glob("*.png")))
            },
            "snapshots": {
                "conversation": [asdict(snapshot) for snapshot in self.conversation_snapshots],
                "ui": [asdict(snapshot) for snapshot in self.ui_snapshots],
                "state": [asdict(snapshot) for snapshot in self.state_snapshots]
            }
        }
        
        # Save report to file
        report_file = self.output_dir / f"journey_report_{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Journey report generated: {report_file}")
        
        return report
    
    def save_html_report(self, journey_result: Any) -> Path:
        """Generate HTML report with embedded screenshots."""
        
        html_content = self._generate_html_report_content(journey_result)
        
        html_file = self.output_dir / f"journey_report_{self.session_id}.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
            
        logger.info(f"HTML report saved: {html_file}")
        return html_file
    
    def _generate_html_report_content(self, journey_result: Any) -> str:
        """Generate HTML content for journey report."""
        
        # Create embedded screenshots
        screenshot_embeds = []
        for ui_snapshot in self.ui_snapshots:
            try:
                with open(ui_snapshot.screenshot_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                    screenshot_embeds.append({
                        "description": ui_snapshot.description,
                        "timestamp": ui_snapshot.timestamp,
                        "data": f"data:image/png;base64,{img_data}"
                    })
            except Exception as e:
                logger.error(f"Error embedding screenshot: {e}")
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic Coaching Journey Report - {self.session_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #f0f8ff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .snapshot {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .conversation {{ background: #f9f9f9; }}
        .ui {{ background: #fff5ee; }}
        .state {{ background: #f0fff0; }}
        .screenshot {{ max-width: 800px; border: 1px solid #ccc; margin: 10px 0; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric {{ background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #007acc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Strategic Coaching Journey Report</h1>
        <p><strong>Session ID:</strong> {self.session_id}</p>
        <p><strong>Business Case:</strong> {getattr(journey_result, 'business_case_name', 'Unknown')}</p>
        <p><strong>Persona:</strong> {getattr(journey_result, 'persona_type', 'Unknown')}</p>
        <p><strong>Success:</strong> {'✅ Successful' if getattr(journey_result, 'success', False) else '❌ Failed'}</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Conversation</h3>
            <p><strong>{getattr(journey_result, 'total_exchanges', 0)}</strong> exchanges</p>
        </div>
        <div class="metric">
            <h3>Completeness</h3>
            <p><strong>{getattr(journey_result, 'final_completeness', 0):.1f}%</strong> achieved</p>
        </div>
        <div class="metric">
            <h3>Duration</h3>
            <p><strong>{getattr(journey_result, 'journey_duration', 0):.1f}s</strong> total</p>
        </div>
        <div class="metric">
            <h3>Phases</h3>
            <p><strong>{len(getattr(journey_result, 'phases_completed', []))}</strong> completed</p>
        </div>
    </div>
    
    <h2>Journey Timeline</h2>
    """
        
        # Add conversation snapshots
        for i, (conv, ui) in enumerate(zip(self.conversation_snapshots, screenshot_embeds)):
            html += f"""
    <div class="snapshot conversation">
        <h3>Exchange {conv.exchange_number} - {conv.phase.upper()} Phase</h3>
        <p><strong>Timestamp:</strong> {conv.timestamp}</p>
        <p><strong>Agent:</strong> {conv.agent_type}</p>
        <p><strong>Completeness:</strong> {conv.completeness}%</p>
        
        <div style="margin: 10px 0;">
            <strong>User ({getattr(journey_result, 'persona_type', 'Unknown')}):</strong>
            <div style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 5px 0;">
                {conv.user_message}
            </div>
        </div>
        
        <div style="margin: 10px 0;">
            <strong>AI Coach ({conv.agent_type}):</strong>
            <div style="background: #f3e5f5; padding: 10px; border-radius: 5px; margin: 5px 0;">
                {conv.ai_response[:500]}{'...' if len(conv.ai_response) > 500 else ''}
            </div>
        </div>
        
        {f'<img src="{ui["data"]}" class="screenshot" alt="{ui["description"]}">' if i < len(screenshot_embeds) else ''}
    </div>
    """
        
        html += """
    <h2>Recording Summary</h2>
    <div class="snapshot state">
        <h3>Final State</h3>
        <ul>
"""
        
        # Add final state information
        if self.state_snapshots:
            final_state = self.state_snapshots[-1]
            html += f"""
            <li><strong>Final Phase:</strong> {final_state.current_phase}</li>
            <li><strong>Final Agent:</strong> {final_state.active_agent}</li>
            <li><strong>Strategy Completeness:</strong> {final_state.strategy_completeness}%</li>
            <li><strong>Total Snapshots:</strong> {len(self.conversation_snapshots)} conversation, {len(self.ui_snapshots)} UI, {len(self.state_snapshots)} state</li>
"""
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        
        return html


# Integration with journey simulator
class RecordingJourneySimulator:
    """Journey simulator with integrated recording capabilities."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", 
                 recording_output_dir: Path = Path("tests/evaluation/recordings")):
        self.api_base_url = api_base_url
        self.recording_output_dir = recording_output_dir
        self.recording_output_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_recorded_journey(self, business_case_name: str) -> Tuple[Any, JourneyRecorder]:
        """Run journey with full recording capabilities."""
        
        from .journey_simulator import JourneySimulator
        
        # Generate session ID for recording
        session_id = f"{business_case_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize recorder
        recorder = JourneyRecorder(self.recording_output_dir, session_id)
        await recorder.initialize_browser()
        
        try:
            # Initialize simulator
            simulator = JourneySimulator(self.api_base_url)
            
            # Navigate to application and capture initial state
            if recorder.page:
                await recorder.page.goto("http://localhost:8081")
                await recorder.capture_ui_snapshot("journey_start")
            
            # Run journey with recording
            result = await simulator.run_complete_journey(business_case_name)
            
            # Enhance result with recording data
            result.session_id = session_id
            
            # Generate comprehensive report
            recorder.generate_journey_report(result)
            recorder.save_html_report(result)
            
            logger.info(f"Recorded journey completed: Success={result.success}")
            
            return result, recorder
            
        finally:
            await recorder.close_browser()


# Convenience function for recorded testing
async def run_recorded_test(business_case_name: str) -> Tuple[Any, Path]:
    """Run a recorded journey test and return result with report path."""
    
    simulator = RecordingJourneySimulator()
    result, recorder = await simulator.run_recorded_journey(business_case_name)
    
    # Return result and HTML report path
    html_report = recorder.output_dir / f"journey_report_{result.session_id}.html"
    
    return result, html_report