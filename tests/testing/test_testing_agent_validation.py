#!/usr/bin/env python3
"""
Comprehensive validation tests for the Testing Agent system.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.testing.business_case import business_case_library, PersonaType
from src.testing.testing_agent import StrategicTestingAgent, ConversationContext
from src.testing.journey_simulator import run_journey_test, run_multiple_journey_tests
from src.testing.journey_recorder import run_recorded_test


class TestingAgentValidation:
    """Comprehensive validation of the testing agent system."""
    
    def test_business_case_library_loading(self):
        """Test that business case library loads correctly."""
        
        # Check that cases are available
        available_cases = business_case_library.list_cases()
        assert len(available_cases) >= 3, f"Expected at least 3 business cases, got {len(available_cases)}"
        
        # Verify AFAS case exists
        assert "afas_software_enterprise" in available_cases, "AFAS Software case not found"
        
        # Verify anti-consultancy case exists
        assert "anti_consultancy_ai" in available_cases, "Anti-consultancy case not found"
        
        print(f"✅ Business case library validation passed: {len(available_cases)} cases available")
    
    def test_persona_differences(self):
        """Test that different personas produce different response patterns."""
        
        # Get AFAS case with different personas
        afas_case = business_case_library.get_case("afas_software_enterprise")
        anti_consultancy_case = business_case_library.get_case("anti_consultancy_ai")
        
        # Create agents with different personas
        visionary_agent = StrategicTestingAgent(afas_case)  # Visionary Founder
        analytical_agent = StrategicTestingAgent(anti_consultancy_case)  # Should be different
        
        # Test same question to both
        test_question = "What inspired you to start this organization?"
        
        context = ConversationContext(
            coach_message=test_question,
            conversation_history=[],
            current_phase="why",
            strategy_completeness=0.0,
            session_metadata={}
        )
        
        response1 = visionary_agent.generate_response(test_question, context)
        response2 = analytical_agent.generate_response(test_question, context)
        
        # Responses should be different
        assert response1 != response2, "Different personas should produce different responses"
        assert len(response1) > 20, "Response should be substantive"
        assert len(response2) > 20, "Response should be substantive"
        
        print(f"✅ Persona differences validation passed")
        print(f"   Visionary response: {response1[:50]}...")
        print(f"   Other response: {response2[:50]}...")
    
    def test_context_memory_progression(self):
        """Test that context memory and trust build over conversation."""
        
        afas_case = business_case_library.get_case("afas_software_enterprise")
        agent = StrategicTestingAgent(afas_case)
        
        # Initial trust should be low
        initial_trust = agent.context_memory.trust_level
        assert initial_trust == 0.0, "Initial trust should be 0.0"
        
        # Simulate positive coaching exchanges
        positive_messages = [
            "I understand your vision for the company",
            "I appreciate the culture you've built", 
            "I can see how your values drive success",
            "Your approach to employee empowerment is inspiring"
        ]
        
        for message in positive_messages:
            context = ConversationContext(
                coach_message=message,
                conversation_history=[],
                current_phase="why",
                strategy_completeness=0.0,
                session_metadata={}
            )
            agent.generate_response(message, context)
        
        # Trust should have increased
        final_trust = agent.context_memory.trust_level
        assert final_trust > initial_trust, f"Trust should increase: {initial_trust} -> {final_trust}"
        
        print(f"✅ Context memory progression validation passed: Trust {initial_trust} -> {final_trust}")
    
    async def test_journey_simulation_basic(self):
        """Test basic journey simulation functionality."""
        
        print("\n🚀 Testing basic journey simulation...")
        
        try:
            # Test AFAS journey
            result = await run_journey_test("afas_software_enterprise")
            
            # Validate result structure
            assert hasattr(result, 'success'), "Result should have success attribute"
            assert hasattr(result, 'conversation_history'), "Result should have conversation history"
            assert hasattr(result, 'performance_metrics'), "Result should have performance metrics"
            
            print(f"✅ Journey simulation validation passed")
            print(f"   Success: {result.success}")
            print(f"   Exchanges: {result.total_exchanges}")
            print(f"   Completeness: {result.final_completeness}%")
            print(f"   Duration: {result.journey_duration:.1f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Journey simulation failed: {e}")
            return None
    
    async def test_recording_functionality(self):
        """Test journey recording with screenshots."""
        
        print("\n📸 Testing journey recording functionality...")
        
        try:
            # Run recorded test
            result, html_report_path = await run_recorded_test("afas_software_enterprise")
            
            # Validate recording artifacts
            assert html_report_path.exists(), "HTML report should be generated"
            
            # Check if screenshots directory exists
            screenshots_dir = html_report_path.parent / "screenshots" / result.session_id
            if screenshots_dir.exists():
                screenshot_count = len(list(screenshots_dir.glob("*.png")))
                print(f"✅ Recording validation passed: {screenshot_count} screenshots captured")
            else:
                print("⚠️  Recording validation: No screenshots directory found")
            
            print(f"   HTML Report: {html_report_path}")
            print(f"   Session ID: {result.session_id}")
            
            return result, html_report_path
            
        except Exception as e:
            print(f"❌ Recording test failed: {e}")
            return None, None


async def run_comprehensive_validation():
    """Run all validation tests."""
    
    print("="*60)
    print("TESTING AGENT SYSTEM VALIDATION")
    print("="*60)
    
    validator = TestingAgentValidation()
    
    # Test 1: Business case library
    validator.test_business_case_library_loading()
    
    # Test 2: Persona differences
    validator.test_persona_differences()
    
    # Test 3: Context memory
    validator.test_context_memory_progression()
    
    # Test 4: Journey simulation (requires API)
    journey_result = await validator.test_journey_simulation_basic()
    
    # Test 5: Recording functionality (requires API and UI)
    recording_result, html_report = await validator.test_recording_functionality()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    tests_passed = 0
    total_tests = 5
    
    if validator:
        tests_passed += 3  # Business case, persona, context memory tests
    
    if journey_result and journey_result.success:
        tests_passed += 1
        print("✅ Journey simulation: PASSED")
    else:
        print("❌ Journey simulation: FAILED")
    
    if recording_result and html_report and html_report.exists():
        tests_passed += 1
        print("✅ Recording functionality: PASSED")
    else:
        print("❌ Recording functionality: FAILED")
    
    success_rate = (tests_passed / total_tests) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({tests_passed}/{total_tests})")
    
    if success_rate >= 80:
        print("🎉 Testing Agent system validation SUCCESSFUL!")
    else:
        print("⚠️  Testing Agent system needs additional work")
    
    return success_rate >= 80


if __name__ == "__main__":
    # Run validation
    success = asyncio.run(run_comprehensive_validation())
    sys.exit(0 if success else 1)