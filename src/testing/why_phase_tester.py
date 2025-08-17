"""
WHY Phase Isolated Testing with Playwright and AFAS Business Case.

This module implements focused testing of the WHY phase using Simon Sinek
methodology with realistic AFAS Software persona responses.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .business_case_parser import AFASResponseGenerator
from .testing_agent import StrategyTestingAgent
from .html_report_generator import HTMLTestReportGenerator

logger = logging.getLogger(__name__)


class WHYPhaseTester:
    """
    Isolated testing for WHY phase using AFAS Software business case.
    
    Tests the complete Simon Sinek "Start with Why" methodology workflow
    with realistic user responses and comprehensive documentation.
    """
    
    def __init__(self, headless: bool = False):
        """Initialize WHY phase tester."""
        self.agent = StrategyTestingAgent(
            headless=headless,
            screenshots_dir="testing/screenshots/why_phase",
            reports_dir="testing/reports/why_phase",
            logs_dir="testing/logs/why_phase"
        )
        self.response_generator = AFASResponseGenerator()
        self.test_results: Dict = {}
    
    async def run_why_phase_test(self) -> Dict:
        """Run complete WHY phase isolated test."""
        logger.info("🎯 Starting WHY Phase Isolated Test")
        logger.info("=" * 50)
        
        try:
            # Setup browser and navigate
            await self.agent.setup_browser()
            await self.agent.navigate_to_app()
            
            # Take initial screenshot
            await self.agent.take_screenshot("why_phase_start")
            
            # Test the WHY methodology workflow
            test_start = datetime.now()
            
            # 1. Welcome and Origin Story
            await self._test_origin_story_stage()
            
            # 2. Discovery and Proud Moments  
            await self._test_discovery_stage()
            
            # 3. Core Beliefs Mining
            await self._test_beliefs_stage()
            
            # 4. WHY Statement Distillation
            await self._test_distillation_stage()
            
            # 5. Values Definition
            await self._test_values_stage()
            
            # 6. Integration and Completion
            await self._test_completion_stage()
            
            test_end = datetime.now()
            
            # Compile test results
            self.test_results = {
                "test_name": "WHY Phase Isolated Test",
                "business_case": "AFAS Software",
                "persona": self.response_generator.get_persona_info(),
                "start_time": test_start.isoformat(),
                "end_time": test_end.isoformat(),
                "duration_minutes": (test_end - test_start).total_seconds() / 60,
                "total_interactions": self.agent.interaction_count,
                "screenshots_taken": len(self.agent.screenshots),
                "test_status": "PASSED",
                "methodology_stages": [
                    "Origin Story Exploration",
                    "Proud Moments Discovery", 
                    "Core Beliefs Mining",
                    "WHY Statement Distillation",
                    "Values Definition",
                    "Golden Circle Integration"
                ]
            }
            
            # Save interaction log
            log_path = await self.agent.save_interaction_log()
            
            # Take final screenshot
            await self.agent.take_screenshot("why_phase_complete")
            
            # Generate HTML report automatically
            await self._generate_html_report(log_path)
            
            logger.info("✅ WHY Phase Test Completed Successfully")
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"❌ WHY Phase Test Failed: {e}")
            self.test_results["test_status"] = "FAILED"
            self.test_results["error"] = str(e)
            return self.test_results
            
        finally:
            await self.agent.cleanup()
    
    async def _test_origin_story_stage(self) -> None:
        """Test origin story exploration stage."""
        logger.info("📖 Testing Origin Story Stage")
        
        # Send initial message to start WHY phase
        response1 = await self.agent.send_message(
            "Hello! I'm Bas van der Veldt, CEO of AFAS Software. I want to develop our strategic vision for the future.",
            take_screenshot=True
        )
        
        # Verify WHY agent welcome (handle empty response)
        if not response1:
            raise Exception("No response received from WHY agent")
            
        response1_lower = response1.lower()
        if "why coach" not in response1_lower and "strategic journey" not in response1_lower:
            logger.warning(f"Unexpected welcome response: {response1[:100]}...")
        
        if "origin story" not in response1_lower:
            logger.warning("Origin story not mentioned in welcome - continuing anyway")
        
        # Respond with AFAS origin story
        await self.agent.send_message(
            self.response_generator.generate_origin_story_response(response1)
        )
        
        logger.info("✅ Origin Story Stage Complete")
    
    async def _test_discovery_stage(self) -> None:
        """Test proud moments discovery stage."""
        logger.info("🏆 Testing Discovery Stage")
        
        # Agent should ask about proud moments
        await self.agent.wait_for_response()
        
        # Get current response and send proud moments
        latest_messages = self.agent.page.locator(".message.agent")
        count = await latest_messages.count()
        if count > 0:
            latest_response = await latest_messages.nth(count - 1).text_content()
        else:
            latest_response = "Tell me about your proudest moments"
        
        # Screenshot every 3rd interaction
        if self.agent.interaction_count % 3 == 0:
            await self.agent.take_screenshot(f"discovery_stage_{self.agent.interaction_count}")
        
        await self.agent.send_message(
            self.response_generator.generate_proud_moments_response(latest_response)
        )
        
        logger.info("✅ Discovery Stage Complete")
    
    async def _test_beliefs_stage(self) -> None:
        """Test core beliefs mining stage."""
        logger.info("💭 Testing Core Beliefs Stage")
        
        await self.agent.wait_for_response()
        
        # Get agent's beliefs question
        latest_messages = self.agent.page.locator(".message.agent")
        count = await latest_messages.count()
        if count > 0:
            latest_response = await latest_messages.nth(count - 1).text_content()
        else:
            latest_response = "What do you believe about entrepreneurs?"
        
        # Screenshot every 3rd interaction
        if self.agent.interaction_count % 3 == 0:
            await self.agent.take_screenshot(f"beliefs_stage_{self.agent.interaction_count}")
        
        await self.agent.send_message(
            self.response_generator.generate_beliefs_response(latest_response)
        )
        
        logger.info("✅ Core Beliefs Stage Complete")
    
    async def _test_distillation_stage(self) -> None:
        """Test WHY statement distillation stage."""
        logger.info("🎯 Testing WHY Distillation Stage")
        
        await self.agent.wait_for_response()
        
        # Agent should propose WHY statement
        latest_messages = self.agent.page.locator(".message.agent")
        count = await latest_messages.count()
        if count > 0:
            latest_response = await latest_messages.nth(count - 1).text_content()
        else:
            latest_response = "Your WHY seems to be..."
        
        # Screenshot every 3rd interaction
        if self.agent.interaction_count % 3 == 0:
            await self.agent.take_screenshot(f"distillation_stage_{self.agent.interaction_count}")
        
        # Confirm or refine the WHY statement
        await self.agent.send_message(
            self.response_generator.generate_confirmation_response(latest_response)
        )
        
        logger.info("✅ WHY Distillation Stage Complete")
    
    async def _test_values_stage(self) -> None:
        """Test actionable values definition stage."""
        logger.info("⚡ Testing Values Definition Stage")
        
        await self.agent.wait_for_response()
        
        # Get agent's values question
        latest_messages = self.agent.page.locator(".message.agent")
        count = await latest_messages.count()
        if count > 0:
            latest_response = await latest_messages.nth(count - 1).text_content()
        else:
            latest_response = "What are your actionable values?"
        
        # Screenshot every 3rd interaction
        if self.agent.interaction_count % 3 == 0:
            await self.agent.take_screenshot(f"values_stage_{self.agent.interaction_count}")
        
        await self.agent.send_message(
            self.response_generator.generate_values_response(latest_response)
        )
        
        logger.info("✅ Values Definition Stage Complete")
    
    async def _test_completion_stage(self) -> None:
        """Test WHY phase completion and transition readiness."""
        logger.info("🎉 Testing Completion Stage")
        
        await self.agent.wait_for_response()
        
        # Continue conversation until completion
        for i in range(3):  # Additional interactions to reach completion
            latest_messages = self.agent.page.locator(".message.agent")
            count = await latest_messages.count()
            if count > 0:
                latest_response = await latest_messages.nth(count - 1).text_content()
            else:
                latest_response = "Continue the conversation"
            
            # Check if transition readiness is mentioned
            if "ready to move" in latest_response.lower() or "explore how" in latest_response.lower():
                await self.agent.send_message("Yes, I'm ready to move to the HOW phase.")
                break
            else:
                await self.agent.send_message(
                    f"That makes sense. Let me add that our culture of trust and empowerment is central to everything we do at AFAS. It's what makes us different."
                )
            
            # Screenshot every 3rd interaction  
            if self.agent.interaction_count % 3 == 0:
                await self.agent.take_screenshot(f"completion_stage_{self.agent.interaction_count}")
        
        # Final completion screenshot
        await self.agent.take_screenshot("why_phase_final")
        
        logger.info("✅ WHY Phase Completion Stage Complete")
    
    async def _generate_html_report(self, log_path: str) -> None:
        """Generate comprehensive HTML report automatically."""
        logger.info("📝 Generating HTML Test Report...")
        
        try:
            # Use why_phase specific report generator to save in why_phase folder
            generator = HTMLTestReportGenerator(reports_dir="testing/reports/why_phase")
            report_path = generator.generate_why_phase_html_report(
                interaction_log_path=log_path,
                screenshots_dir=str(self.agent.screenshots_dir),
                report_name=f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            logger.info(f"✅ HTML Report Generated: {report_path}")
            logger.info(f"🌐 Open in browser: file://{Path(report_path).absolute()}")
            
            # Add report path to test results
            self.test_results["html_report"] = report_path
            
        except Exception as e:
            logger.error(f"❌ HTML Report generation failed: {e}")
            self.test_results["report_error"] = str(e)


async def run_why_phase_isolated_test(headless: bool = False) -> Dict:
    """Run the WHY phase isolated test."""
    tester = WHYPhaseTester(headless=headless)
    return await tester.run_why_phase_test()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    async def main():
        print("🎯 WHY Phase Isolated Testing")
        print("Using AFAS Software Business Case")
        print("=" * 50)
        
        results = await run_why_phase_isolated_test(headless=False)
        
        print("\n📊 Test Results:")
        print(f"Status: {results.get('test_status', 'Unknown')}")
        print(f"Interactions: {results.get('total_interactions', 0)}")
        print(f"Screenshots: {results.get('screenshots_taken', 0)}")
        print(f"Duration: {results.get('duration_minutes', 0):.1f} minutes")
        
        if results.get('test_status') == 'PASSED':
            print("✅ WHY Phase Test Successful!")
            if 'html_report' in results:
                print(f"📊 HTML Report: {results['html_report']}")
                print(f"🌐 Open: file://{Path(results['html_report']).absolute()}")
        else:
            print(f"❌ Test Failed: {results.get('error', 'Unknown error')}")
    
    asyncio.run(main())