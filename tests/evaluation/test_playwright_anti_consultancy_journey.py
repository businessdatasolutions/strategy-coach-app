#!/usr/bin/env python3
"""
Playwright test for the anti-consultancy conversation journey.
Tests the exact conversation flow that revealed inappropriate interactive elements.
"""

import json
import time
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser

# Test configuration
WEB_UI_URL = "http://localhost:8081"
API_BASE_URL = "http://localhost:8000"
TEST_DATA_FILE = Path(__file__).parent / "test_data_anti_consultancy_conversation.json"


class AntiConsultancyJourneyTest:
    """Playwright test for anti-consultancy conversation journey."""
    
    def __init__(self, page: Page):
        self.page = page
        self.test_data = self._load_test_data()
        self.screenshots_dir = Path(__file__).parent / "screenshots" / "anti_consultancy_test"
        self.screenshots_dir.mkdir(exist_ok=True, parents=True)
    
    def _load_test_data(self) -> dict:
        """Load test conversation data."""
        with open(TEST_DATA_FILE, 'r') as f:
            return json.load(f)
    
    def _take_screenshot(self, name: str):
        """Take a screenshot for documentation."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.png"
        filepath = self.screenshots_dir / filename
        self.page.screenshot(path=str(filepath))
        print(f"📸 Screenshot saved: {filename}")
    
    def _wait_for_ai_response(self, timeout: int = 15000):
        """Wait for AI response to appear and typing indicator to disappear."""
        # Wait for typing indicator to disappear
        try:
            self.page.wait_for_selector('.typing-indicator', state='detached', timeout=timeout)
        except:
            pass  # Typing indicator might not appear for fast responses
        
        # Ensure messages are loaded
        self.page.wait_for_selector('.message-fade-in', timeout=timeout)
    
    def _send_message(self, message: str, turn_number: int):
        """Send a message and wait for response."""
        print(f"\n→ Turn {turn_number}: Sending message...")
        print(f"   User: {message[:60]}...")
        
        # Type message
        input_field = self.page.locator('input[type="text"]')
        input_field.fill(message)
        
        # Take screenshot before sending
        self._take_screenshot(f"turn_{turn_number}_before_send")
        
        # Send message (press Enter)
        self.page.keyboard.press('Enter')
        
        # Wait for AI response
        self._wait_for_ai_response()
        
        # Take screenshot after response
        self._take_screenshot(f"turn_{turn_number}_after_response")
        
        # Check for interactive elements
        interactive_visible = self._check_interactive_elements_visible()
        print(f"   Interactive elements visible: {interactive_visible}")
        
        return interactive_visible
    
    def _check_interactive_elements_visible(self) -> bool:
        """Check if interactive selection interface is visible."""
        try:
            # Look for the interactive selection panel
            interactive_panel = self.page.locator('div:has-text("Which of these core beliefs resonate")')
            return interactive_panel.is_visible()
        except:
            return False
    
    def _start_session(self):
        """Start a new conversation session."""
        print("\n🚀 Starting new session...")
        
        # Navigate to the application
        self.page.goto(WEB_UI_URL)
        
        # Wait for initial load and session creation
        self.page.wait_for_selector('input[type="text"]', timeout=10000)
        
        # Wait a moment for session initialization
        time.sleep(2)
        
        # Take initial screenshot
        self._take_screenshot("session_start")
        print("✅ Session started successfully")
    
    def run_conversation_test(self) -> dict:
        """Run the complete conversation test and return results."""
        
        print("\n" + "="*60)
        print("ANTI-CONSULTANCY CONVERSATION JOURNEY TEST")
        print("="*60)
        
        results = {
            "test_name": "anti_consultancy_journey",
            "total_turns": 0,
            "successful_turns": 0,
            "interactive_element_results": {},
            "critical_failures": [],
            "success": True
        }
        
        # Start session
        self._start_session()
        
        # Run through conversation turns
        conversation_flow = self.test_data["conversation_flow"]
        
        for turn_data in conversation_flow:
            turn_num = turn_data["turn"]
            user_input = turn_data["user_input"]
            expected_interactive = turn_data["interactive_elements_expected"]
            is_critical = turn_data.get("critical_test", False)
            
            results["total_turns"] += 1
            
            try:
                # Send message and check interactive elements
                interactive_appeared = self._send_message(user_input, turn_num)
                
                # Validate expectations
                if expected_interactive and not interactive_appeared:
                    failure_msg = f"Turn {turn_num}: Expected interactive elements but none appeared"
                    results["critical_failures"].append(failure_msg)
                    print(f"❌ {failure_msg}")
                    
                    if is_critical:
                        results["success"] = False
                        print(f"🚨 CRITICAL FAILURE: {turn_data.get('failure_description', '')}")
                
                elif not expected_interactive and interactive_appeared:
                    failure_msg = f"Turn {turn_num}: Unexpected interactive elements appeared"
                    results["critical_failures"].append(failure_msg)
                    print(f"⚠️  {failure_msg}")
                
                else:
                    results["successful_turns"] += 1
                    status = "✅ Interactive appeared" if interactive_appeared else "✅ No interactive (correct)"
                    print(f"   {status}")
                
                # Record interactive element results
                results["interactive_element_results"][f"turn_{turn_num}"] = {
                    "expected": expected_interactive,
                    "actual": interactive_appeared,
                    "correct": expected_interactive == interactive_appeared
                }
                
                # Brief pause between messages
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"Turn {turn_num}: Error during test - {str(e)}"
                results["critical_failures"].append(error_msg)
                print(f"💥 {error_msg}")
        
        # Final assessment
        success_rate = (results["successful_turns"] / results["total_turns"]) * 100
        results["success_rate"] = success_rate
        
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Success Rate: {success_rate:.1f}% ({results['successful_turns']}/{results['total_turns']})")
        print(f"Critical Failures: {len(results['critical_failures'])}")
        
        if results["success"]:
            print("🎉 TEST PASSED - Interactive elements behaving correctly")
        else:
            print("💥 TEST FAILED - Critical issues detected")
            for failure in results["critical_failures"]:
                print(f"   • {failure}")
        
        return results


def test_anti_consultancy_conversation_journey():
    """Run the anti-consultancy conversation journey test with Playwright."""
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Visible browser for debugging
        page = browser.new_page()
        
        try:
            # Run the test
            test_runner = AntiConsultancyJourneyTest(page)
            results = test_runner.run_conversation_test()
            
            # Assert critical test passed
            assert results["success"], f"Critical test failures: {results['critical_failures']}"
            
            # Assert the specific user request for choices worked
            turn_13_result = results["interactive_element_results"].get("turn_13", {})
            assert turn_13_result.get("correct", False), "Turn 13 (explicit choice request) failed"
            
            print(f"\n✅ Anti-consultancy conversation test completed successfully!")
            
        finally:
            browser.close()


if __name__ == "__main__":
    # Run the test directly
    test_anti_consultancy_conversation_journey()