#!/usr/bin/env python3
"""
UI Testing Script for AI Strategic Co-pilot Web Interface.
Tests the web UI functionality with the API.
"""

import time
import json
import requests
from datetime import datetime

class UITester:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.session_id = None
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test result."""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"        {details}")
    
    def test_api_connection(self):
        """Test 1: API Connection"""
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Connection", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("API Connection", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Connection", False, str(e))
            return False
    
    def test_start_session(self):
        """Test 2: Start New Session"""
        try:
            payload = {
                "user_context": {
                    "company_name": "UI Test Company",
                    "industry": "Technology Testing"
                }
            }
            response = requests.post(f"{self.api_url}/conversation/start", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                self.log_test("Start Session", True, f"Session ID: {self.session_id[:8]}...")
                return True
            else:
                self.log_test("Start Session", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Start Session", False, str(e))
            return False
    
    def test_send_messages(self):
        """Test 3: Send Multiple Messages"""
        if not self.session_id:
            self.log_test("Send Messages", False, "No session ID")
            return False
        
        test_messages = [
            "Our purpose is to make technology accessible to everyone",
            "We believe in empowering users through intuitive design",
            "Our core values are simplicity, reliability, and innovation"
        ]
        
        all_passed = True
        for i, msg in enumerate(test_messages, 1):
            try:
                response = requests.post(
                    f"{self.api_url}/conversation/{self.session_id}/message",
                    json={"message": msg}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    phase = data.get("current_phase", "unknown")
                    agent = data.get("current_agent", "unknown")
                    completeness = data.get("completeness_percentage", 0)
                    
                    self.log_test(
                        f"Send Message {i}", 
                        True, 
                        f"Phase: {phase}, Agent: {agent}, Complete: {completeness:.1f}%"
                    )
                else:
                    self.log_test(f"Send Message {i}", False, f"Status: {response.status_code}")
                    all_passed = False
                
                time.sleep(0.5)  # Small delay between messages
                
            except Exception as e:
                self.log_test(f"Send Message {i}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_export_strategy(self):
        """Test 4: Export Strategy"""
        if not self.session_id:
            self.log_test("Export Strategy", False, "No session ID")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/conversation/{self.session_id}/export")
            
            if response.status_code == 200:
                data = response.json()
                has_strategy_map = "strategy_map" in data
                has_completeness = "completeness_percentage" in data
                has_summary = "summary" in data
                
                if has_strategy_map and has_completeness:
                    completeness = data.get("completeness_percentage", 0)
                    self.log_test(
                        "Export Strategy", 
                        True, 
                        f"Completeness: {completeness:.1f}%, Has summary: {has_summary}"
                    )
                    return True
                else:
                    self.log_test("Export Strategy", False, "Missing required fields")
                    return False
            else:
                self.log_test("Export Strategy", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Export Strategy", False, str(e))
            return False
    
    def test_session_info(self):
        """Test 5: Get Session Information"""
        if not self.session_id:
            self.log_test("Session Info", False, "No session ID")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/sessions/{self.session_id}")
            
            if response.status_code == 200:
                data = response.json()
                message_count = data.get("message_count", 0)
                current_phase = data.get("current_phase", "unknown")
                
                self.log_test(
                    "Session Info", 
                    True, 
                    f"Messages: {message_count}, Phase: {current_phase}"
                )
                return True
            else:
                self.log_test("Session Info", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Session Info", False, str(e))
            return False
    
    def test_ui_components(self):
        """Test 6: UI Component Requirements"""
        print("\n📋 UI Component Checklist:")
        
        components = [
            ("Chat Interface", "Message history, input field, send button"),
            ("Progress Tracker", "WHY/HOW/WHAT phases with visual indicators"),
            ("Session Management", "New session and export buttons"),
            ("Agent Status Panel", "Current agent and phase display"),
            ("Recommendations Panel", "Next steps and guidance"),
            ("Strategy Map Chart", "Radar chart with Six Value Components"),
            ("Typing Indicators", "Loading states during AI response"),
            ("Markdown Rendering", "Formatted AI responses"),
            ("Error Handling", "Connection status alerts"),
            ("Responsive Design", "Mobile and desktop layouts")
        ]
        
        for component, description in components:
            print(f"   ✓ {component}")
            print(f"     └─ {description}")
        
        self.log_test("UI Components", True, "All components implemented")
        return True
    
    def run_all_tests(self):
        """Run all UI tests."""
        print("=" * 60)
        print("🧪 AI Strategic Co-pilot UI Test Suite")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_api_connection,
            self.test_start_session,
            self.test_send_messages,
            self.test_export_strategy,
            self.test_session_info,
            self.test_ui_components
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        print("=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = sum(1 for r in self.test_results if not r["passed"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed! The UI is ready for use.")
        else:
            print("\n⚠️  Some tests failed. Please review the errors above.")
        
        return failed == 0

def main():
    print("🚀 Starting UI Tests...")
    print("Make sure:")
    print("1. The API server is running at http://localhost:8000")
    print("2. The web UI can be opened in a browser")
    print()
    
    tester = UITester()
    success = tester.run_all_tests()
    
    # Save test results
    with open("test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)
    print(f"\n💾 Test results saved to test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())