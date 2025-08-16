"""
Journey Simulator for Testing Agent
Orchestrates complete strategic coaching journeys with realistic user behavior.
"""

import asyncio
import aiohttp
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .testing_agent import StrategicTestingAgent, ConversationContext
from .business_case import BusinessCase, business_case_library
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class JourneyPhase:
    """Represents a phase in the strategic journey."""
    name: str
    expected_agent_types: List[str]
    completion_threshold: float
    max_exchanges: int


@dataclass
class JourneyResult:
    """Results from a complete journey simulation."""
    session_id: str
    business_case_name: str
    persona_type: str
    success: bool
    total_exchanges: int
    phases_completed: List[str]
    final_completeness: float
    errors: List[str]
    conversation_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    journey_duration: float


class APIClient:
    """Client for interacting with the Strategic Coaching API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def start_conversation(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation session."""
        async with self.session.post(
            f"{self.base_url}/conversation/start",
            json={"user_context": user_context}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to start conversation: {response.status}")
    
    async def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Send a message to the conversation."""
        async with self.session.post(
            f"{self.base_url}/conversation/{session_id}/message",
            json={"message": message}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Failed to send message: {response.status} - {error_text}")
    
    async def get_strategy_map(self, session_id: str) -> Dict[str, Any]:
        """Get the current strategy map."""
        async with self.session.get(
            f"{self.base_url}/conversation/{session_id}/export"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get strategy map: {response.status}")
    
    async def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except:
            return False


class JourneySimulator:
    """
    Orchestrates complete strategic coaching journeys with testing agents.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.journey_phases = self._define_journey_phases()
        
    def _define_journey_phases(self) -> List[JourneyPhase]:
        """Define the expected phases of a strategic journey."""
        return [
            JourneyPhase(
                name="why_discovery",
                expected_agent_types=["why_agent"],
                completion_threshold=30.0,
                max_exchanges=12
            ),
            JourneyPhase(
                name="how_analysis", 
                expected_agent_types=["analogy_agent", "logic_agent"],
                completion_threshold=60.0,
                max_exchanges=15
            ),
            JourneyPhase(
                name="what_planning",
                expected_agent_types=["open_strategy_agent", "strategy_map_agent"],
                completion_threshold=90.0,
                max_exchanges=10
            )
        ]
    
    async def run_complete_journey(self, business_case_name: str) -> JourneyResult:
        """Execute a complete strategic coaching journey simulation."""
        
        start_time = time.time()
        
        # Initialize testing agent
        business_case = business_case_library.get_case(business_case_name)
        if not business_case:
            raise ValueError(f"Business case '{business_case_name}' not found")
            
        testing_agent = StrategicTestingAgent(business_case)
        
        logger.info(f"Starting journey simulation for {business_case.company_profile.name} ({business_case.persona_type.value})")
        
        # Initialize result tracking
        result = JourneyResult(
            session_id="",
            business_case_name=business_case_name,
            persona_type=business_case.persona_type.value,
            success=False,
            total_exchanges=0,
            phases_completed=[],
            final_completeness=0.0,
            errors=[],
            conversation_history=[],
            performance_metrics={},
            journey_duration=0.0
        )
        
        try:
            async with APIClient(self.api_base_url) as api_client:
                
                # Health check
                if not await api_client.health_check():
                    raise Exception("API health check failed")
                
                # Start conversation
                session_data = await api_client.start_conversation({
                    "company_name": business_case.company_profile.name,
                    "industry": business_case.company_profile.industry.value
                })
                
                result.session_id = session_data["session_id"]
                
                # Add initial message to history
                result.conversation_history.append({
                    "role": "assistant",
                    "content": session_data["message"],
                    "timestamp": datetime.now().isoformat(),
                    "agent": "system",
                    "phase": session_data.get("current_phase", "why")
                })
                
                # Simulate conversation through all phases
                current_phase_index = 0
                exchanges_in_phase = 0
                
                while current_phase_index < len(self.journey_phases):
                    current_phase = self.journey_phases[current_phase_index]
                    
                    logger.info(f"Simulating {current_phase.name} phase")
                    
                    # Simulate exchanges in this phase
                    phase_successful = await self._simulate_phase(
                        api_client, testing_agent, result, current_phase
                    )
                    
                    if phase_successful:
                        result.phases_completed.append(current_phase.name)
                        current_phase_index += 1
                        exchanges_in_phase = 0
                    else:
                        # Phase failed or got stuck
                        result.errors.append(f"Failed to complete {current_phase.name} phase")
                        break
                
                # Get final strategy map
                try:
                    final_strategy = await api_client.get_strategy_map(result.session_id)
                    result.final_completeness = final_strategy.get("completeness_percentage", 0.0)
                except Exception as e:
                    result.errors.append(f"Failed to get final strategy map: {e}")
                
                # Determine overall success
                result.success = (
                    len(result.phases_completed) >= 2 and  # At least WHY and HOW phases
                    result.final_completeness >= 60.0 and  # Meaningful strategy development
                    len(result.errors) == 0  # No critical errors
                )
                
        except Exception as e:
            logger.error(f"Journey simulation failed: {e}")
            result.errors.append(str(e))
            result.success = False
        
        # Calculate final metrics
        result.journey_duration = time.time() - start_time
        result.performance_metrics = self._calculate_performance_metrics(result)
        
        logger.info(f"Journey completed: Success={result.success}, Exchanges={result.total_exchanges}, Duration={result.journey_duration:.1f}s")
        
        return result
    
    async def _simulate_phase(self, api_client: APIClient, testing_agent: StrategicTestingAgent, 
                             result: JourneyResult, phase: JourneyPhase) -> bool:
        """Simulate a single phase of the journey."""
        
        exchanges_in_phase = 0
        phase_start_completeness = result.final_completeness
        
        while exchanges_in_phase < phase.max_exchanges:
            
            # Get last coach message
            if not result.conversation_history:
                break
                
            last_message = result.conversation_history[-1]
            if last_message["role"] != "assistant":
                break
                
            coach_message = last_message["content"]
            
            # Generate user response
            conversation_context = ConversationContext(
                coach_message=coach_message,
                conversation_history=result.conversation_history,
                current_phase=last_message.get("phase", "why"),
                strategy_completeness=result.final_completeness,
                session_metadata={}
            )
            
            user_response = testing_agent.generate_response(coach_message, conversation_context)
            
            # Send user response
            try:
                response_data = await api_client.send_message(result.session_id, user_response)
                
                # Record exchange
                result.conversation_history.extend([
                    {
                        "role": "user",
                        "content": user_response,
                        "timestamp": datetime.now().isoformat(),
                        "persona": testing_agent.business_case.persona_type.value
                    },
                    {
                        "role": "assistant", 
                        "content": response_data["response"],
                        "timestamp": datetime.now().isoformat(),
                        "agent": response_data.get("current_agent", "unknown"),
                        "phase": response_data.get("current_phase", "unknown"),
                        "completeness": response_data.get("completeness_percentage", 0.0)
                    }
                ])
                
                result.total_exchanges += 1
                exchanges_in_phase += 1
                result.final_completeness = response_data.get("completeness_percentage", 0.0)
                
                # Check if phase completion threshold reached
                if result.final_completeness >= phase.completion_threshold:
                    logger.info(f"Phase {phase.name} completed at {result.final_completeness}% completeness")
                    return True
                
                # Small delay between exchanges
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error in phase simulation: {e}")
                result.errors.append(f"Phase {phase.name} error: {e}")
                return False
        
        # Phase completed by exchange limit or other criteria
        completeness_gain = result.final_completeness - phase_start_completeness
        return completeness_gain > 10.0  # At least 10% progress in phase
    
    def _calculate_performance_metrics(self, result: JourneyResult) -> Dict[str, Any]:
        """Calculate performance metrics for the journey."""
        
        if not result.conversation_history:
            return {}
            
        # Basic metrics
        total_messages = len(result.conversation_history)
        user_messages = [msg for msg in result.conversation_history if msg["role"] == "user"]
        ai_messages = [msg for msg in result.conversation_history if msg["role"] == "assistant"]
        
        # Response length analysis
        user_response_lengths = [len(msg["content"]) for msg in user_messages]
        ai_response_lengths = [len(msg["content"]) for msg in ai_messages]
        
        # Phase progression
        phases_reached = len(result.phases_completed)
        expected_phases = len(self.journey_phases)
        
        return {
            "total_messages": total_messages,
            "user_messages": len(user_messages),
            "ai_messages": len(ai_messages),
            "avg_user_response_length": sum(user_response_lengths) / len(user_response_lengths) if user_response_lengths else 0,
            "avg_ai_response_length": sum(ai_response_lengths) / len(ai_response_lengths) if ai_response_lengths else 0,
            "phases_completed_ratio": phases_reached / expected_phases,
            "completeness_per_minute": result.final_completeness / (result.journey_duration / 60) if result.journey_duration > 0 else 0,
            "exchanges_per_minute": result.total_exchanges / (result.journey_duration / 60) if result.journey_duration > 0 else 0,
            "error_rate": len(result.errors) / result.total_exchanges if result.total_exchanges > 0 else 0
        }


async def run_journey_test(business_case_name: str, output_dir: Optional[Path] = None) -> JourneyResult:
    """Convenience function to run a single journey test."""
    
    simulator = JourneySimulator()
    result = await simulator.run_complete_journey(business_case_name)
    
    # Save result if output directory provided
    if output_dir:
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = output_dir / f"journey_result_{business_case_name}_{timestamp}.json"
        
        # Convert result to dict for JSON serialization
        result_dict = {
            "session_id": result.session_id,
            "business_case_name": result.business_case_name,
            "persona_type": result.persona_type,
            "success": result.success,
            "total_exchanges": result.total_exchanges,
            "phases_completed": result.phases_completed,
            "final_completeness": result.final_completeness,
            "errors": result.errors,
            "conversation_history": result.conversation_history,
            "performance_metrics": result.performance_metrics,
            "journey_duration": result.journey_duration,
            "timestamp": timestamp
        }
        
        with open(result_file, 'w') as f:
            json.dump(result_dict, f, indent=2)
            
        logger.info(f"Journey result saved to {result_file}")
    
    return result


async def run_multiple_journey_tests(business_case_names: List[str], output_dir: Optional[Path] = None) -> List[JourneyResult]:
    """Run multiple journey tests concurrently."""
    
    tasks = []
    for case_name in business_case_names:
        task = run_journey_test(case_name, output_dir)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and log them
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Journey test {business_case_names[i]} failed: {result}")
        else:
            valid_results.append(result)
    
    return valid_results


# Integration with existing evaluation framework
class JourneySimulatorIntegration:
    """Integration point with existing evaluation framework."""
    
    @staticmethod
    def create_evaluation_dataset_from_journey(result: JourneyResult) -> Dict[str, Any]:
        """Convert journey result to evaluation dataset format."""
        
        return {
            "test_case_id": f"{result.business_case_name}_{result.session_id}",
            "scenario": {
                "business_case": result.business_case_name,
                "persona": result.persona_type,
                "expected_completion": 90.0
            },
            "conversation_data": result.conversation_history,
            "outcomes": {
                "success": result.success,
                "completeness_achieved": result.final_completeness,
                "phases_completed": result.phases_completed,
                "journey_duration": result.journey_duration
            },
            "quality_metrics": result.performance_metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_playwright_test_from_journey(result: JourneyResult, output_file: Path):
        """Generate Playwright test code from journey result."""
        
        test_code = f'''#!/usr/bin/env python3
"""
Generated Playwright test from journey simulation.
Business Case: {result.business_case_name}
Persona: {result.persona_type}
Generated: {datetime.now().isoformat()}
"""

import pytest
from playwright.sync_api import sync_playwright


def test_{result.business_case_name.replace(" ", "_").lower()}_journey():
    """Test the {result.business_case_name} strategic coaching journey."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to application
            page.goto("http://localhost:8081")
            
            # Wait for session initialization
            page.wait_for_selector('input[type="text"]', timeout=10000)
            
'''
        
        # Add conversation steps
        user_messages = [msg for msg in result.conversation_history if msg["role"] == "user"]
        
        for i, message in enumerate(user_messages[:10]):  # Limit to first 10 for test
            test_code += f'''            # Message {i+1}
            page.fill('input[type="text"]', "{message["content"][:100]}...")
            page.keyboard.press('Enter')
            page.wait_for_selector('.message-fade-in', timeout=15000)
            
'''
        
        test_code += f'''            
            # Verify journey success
            # Should reach at least {result.final_completeness}% completeness
            # Should complete {len(result.phases_completed)} phases
            
        finally:
            browser.close()


if __name__ == "__main__":
    test_{result.business_case_name.replace(" ", "_").lower()}_journey()
'''
        
        with open(output_file, 'w') as f:
            f.write(test_code)
            
        logger.info(f"Generated Playwright test: {output_file}")


# Convenience functions for common operations
async def test_afas_software_journey() -> JourneyResult:
    """Test the AFAS Software enterprise scenario."""
    return await run_journey_test("afas_software_enterprise")


async def test_anti_consultancy_journey() -> JourneyResult:
    """Test the anti-consultancy AI innovation scenario.""" 
    return await run_journey_test("anti_consultancy_ai")


async def run_regression_test_suite() -> List[JourneyResult]:
    """Run all available journey tests for regression testing."""
    available_cases = business_case_library.list_cases()
    return await run_multiple_journey_tests(available_cases)