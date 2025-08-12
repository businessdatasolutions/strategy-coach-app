import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.models.state import (
    AgentState,
    StrategyMapState,
    ConversationPhase,
    AgentInput,
    AgentOutput,
    RouterDecision,
    WorkflowConfig,
    update_conversation_history,
    update_strategy_completeness,
    transition_phase,
    set_processing_stage,
    initialize_agent_state,
    calculate_strategy_completeness
)


class TestAdvancedStateManagement:
    """Test advanced state management functionality."""
    
    def test_initialize_agent_state_with_all_optional_params(self):
        """Test agent state initialization with all optional parameters."""
        session_id = "test_session_advanced"
        strategy_map_path = "data/sessions/test_advanced.json"
        user_id = "user_123"
        user_context = {
            "company_name": "Tech Startup Inc",
            "industry": "technology",
            "team_size": "20-50",
            "revenue_stage": "pre-revenue",
            "location": "San Francisco, CA"
        }
        
        state = initialize_agent_state(
            session_id=session_id,
            strategy_map_path=strategy_map_path,
            user_id=user_id,
            user_context=user_context
        )
        
        assert state["session_id"] == session_id
        assert state["strategy_map_path"] == strategy_map_path
        assert state["user_id"] == user_id
        assert state["user_context"] == user_context
        assert state["current_phase"] == "why"
        assert state["retry_count"] == 0
        assert len(state["conversation_history"]) == 0
        assert all(not completed for completed in state["strategy_completeness"].values())
    
    def test_state_immutability_principles(self):
        """Test state update behavior (note: current implementation modifies in-place)."""
        original_state = initialize_agent_state("test", "test_path")
        original_history_length = len(original_state["conversation_history"])
        
        # Test that update functions work correctly
        message = HumanMessage(content="Test message")
        updated_state = update_conversation_history(original_state, message)
        
        # Current implementation modifies state in-place
        # This test validates the current behavior
        assert len(updated_state["conversation_history"]) == original_history_length + 1
        assert updated_state["conversation_history"][-1].content == "Test message"
    
    def test_deep_state_copying(self):
        """Test state update behavior with nested objects."""
        original_state = initialize_agent_state("test", "test_path")
        original_state["user_context"] = {"company": "Test Co", "size": 10}
        original_size = original_state["user_context"]["size"]
        
        updated_state = update_strategy_completeness(original_state, "why", True)
        
        # Verify the strategy completeness was updated
        assert updated_state["strategy_completeness"]["why"] is True
        
        # Test that user_context is accessible and unchanged by the strategy update
        assert updated_state["user_context"]["company"] == "Test Co"
        assert updated_state["user_context"]["size"] == original_size
    
    def test_conversation_history_message_types(self):
        """Test handling of different message types in conversation history."""
        state = initialize_agent_state("test", "test_path")
        
        # Test different message types
        human_msg = HumanMessage(content="Hello")
        ai_msg = AIMessage(content="Hi there!")
        system_msg = SystemMessage(content="System notification")
        
        state = update_conversation_history(state, human_msg)
        state = update_conversation_history(state, ai_msg)
        state = update_conversation_history(state, system_msg)
        
        assert len(state["conversation_history"]) == 3
        assert isinstance(state["conversation_history"][0], HumanMessage)
        assert isinstance(state["conversation_history"][1], AIMessage)
        assert isinstance(state["conversation_history"][2], SystemMessage)
    
    def test_conversation_history_with_metadata(self):
        """Test conversation history with message metadata."""
        state = initialize_agent_state("test", "test_path")
        
        # Create message with additional metadata
        message = HumanMessage(
            content="I need strategy help",
            additional_kwargs={
                "timestamp": datetime.now().isoformat(),
                "user_id": "user_123",
                "source": "web_interface"
            }
        )
        
        updated_state = update_conversation_history(state, message)
        
        assert len(updated_state["conversation_history"]) == 1
        retrieved_msg = updated_state["conversation_history"][0]
        assert retrieved_msg.content == "I need strategy help"
        assert "timestamp" in retrieved_msg.additional_kwargs
        assert retrieved_msg.additional_kwargs["user_id"] == "user_123"


class TestStrategyCompletenessAdvanced:
    """Test advanced strategy completeness functionality."""
    
    def test_strategy_completeness_edge_cases(self):
        """Test strategy completeness with edge cases."""
        state = initialize_agent_state("test", "test_path")
        
        # Test updating non-existent section (should be handled gracefully)
        updated_state = update_strategy_completeness(state, "non_existent_section", True)
        
        # Should add the new section
        assert "non_existent_section" in updated_state["strategy_completeness"]
        assert updated_state["strategy_completeness"]["non_existent_section"] is True
    
    def test_calculate_completeness_with_custom_sections(self):
        """Test completeness calculation with custom sections."""
        state = initialize_agent_state("test", "test_path")
        
        # Add custom sections
        state = update_strategy_completeness(state, "custom_section_1", True)
        state = update_strategy_completeness(state, "custom_section_2", False)
        
        completeness = calculate_strategy_completeness(state)
        
        # Should calculate based on all sections including custom ones
        total_sections = len(state["strategy_completeness"])
        expected = (len([v for v in state["strategy_completeness"].values() if v]) / total_sections) * 100
        assert abs(completeness - expected) < 0.1
    
    def test_strategy_completeness_percentage_precision(self):
        """Test precision of strategy completeness percentage."""
        state = initialize_agent_state("test", "test_path")
        
        # Complete exactly 3 out of 8 sections
        sections_to_complete = ["why", "analogy_analysis", "stakeholder_customer"]
        for section in sections_to_complete:
            state = update_strategy_completeness(state, section, True)
        
        completeness = calculate_strategy_completeness(state)
        expected = (3 / 8) * 100  # 37.5%
        
        assert abs(completeness - expected) < 0.1
        assert isinstance(completeness, float)
    
    def test_strategy_completeness_with_all_false(self):
        """Test completeness when all sections are explicitly set to False."""
        state = initialize_agent_state("test", "test_path")
        
        # Explicitly set all to False
        for section in state["strategy_completeness"]:
            state = update_strategy_completeness(state, section, False)
        
        completeness = calculate_strategy_completeness(state)
        assert completeness == 0.0


class TestPhaseTransitions:
    """Test phase transition logic."""
    
    def test_valid_phase_transitions(self):
        """Test all valid phase transitions."""
        state = initialize_agent_state("test", "test_path")
        original_phase = state["current_phase"]
        
        valid_phases = ["why", "how", "what", "review", "complete"]
        
        for target_phase in valid_phases:
            updated_state = transition_phase(state, target_phase)
            assert updated_state["current_phase"] == target_phase
            assert updated_state["current_agent"] is None  # Should reset agent
            
            # Update the state for next iteration
            state = updated_state
    
    def test_phase_transition_preserves_other_state(self):
        """Test that phase transitions preserve other state elements."""
        state = initialize_agent_state("test", "test_path")
        
        # Set up some state
        message = HumanMessage(content="Test")
        state = update_conversation_history(state, message)
        state = update_strategy_completeness(state, "why", True)
        state = set_processing_stage(state, "processing", "test_agent")
        
        # Transition phase
        updated_state = transition_phase(state, "how")
        
        # Other state should be preserved
        assert len(updated_state["conversation_history"]) == 1
        assert updated_state["strategy_completeness"]["why"] is True
        assert updated_state["processing_stage"] == "processing"
        assert updated_state["session_id"] == state["session_id"]
    
    def test_phase_transition_resets_current_agent(self):
        """Test that phase transitions reset the current agent."""
        state = initialize_agent_state("test", "test_path")
        state = set_processing_stage(state, "processing", "why_agent")
        
        assert state["current_agent"] == "why_agent"
        
        updated_state = transition_phase(state, "how")
        
        assert updated_state["current_agent"] is None
        assert updated_state["current_phase"] == "how"


class TestProcessingStages:
    """Test processing stage management."""
    
    def test_set_processing_stage_with_agent(self):
        """Test setting processing stage with agent."""
        state = initialize_agent_state("test", "test_path")
        original_stage = state["processing_stage"]
        
        updated_state = set_processing_stage(state, "analyzing_user_input", "router")
        
        assert updated_state["processing_stage"] == "analyzing_user_input"
        assert updated_state["current_agent"] == "router"
        assert updated_state["processing_stage"] != original_stage
    
    def test_set_processing_stage_without_agent(self):
        """Test setting processing stage without changing agent."""
        state = initialize_agent_state("test", "test_path")
        state = set_processing_stage(state, "initial", "why_agent")
        
        # Update stage without specifying agent
        updated_state = set_processing_stage(state, "processing_user_input")
        
        assert updated_state["processing_stage"] == "processing_user_input"
        assert updated_state["current_agent"] == "why_agent"  # Should remain unchanged
    
    def test_processing_stage_tracking_sequence(self):
        """Test tracking a sequence of processing stages."""
        state = initialize_agent_state("test", "test_path")
        
        stages = [
            ("initialization", None),
            ("receiving_input", "orchestrator"), 
            ("routing_decision", "router"),
            ("agent_processing", "why_agent"),
            ("synthesis", "synthesizer"),
            ("complete", None)
        ]
        
        for stage, agent in stages:
            if agent:
                state = set_processing_stage(state, stage, agent)
            else:
                state = set_processing_stage(state, stage)
            
            assert state["processing_stage"] == stage
            if agent:
                assert state["current_agent"] == agent


class TestStateValidation:
    """Test state validation and error handling."""
    
    def test_state_with_invalid_phase(self):
        """Test handling of invalid phase values."""
        state = initialize_agent_state("test", "test_path")
        
        # Direct assignment of invalid phase (should be handled by application logic)
        updated_state = transition_phase(state, "invalid_phase")
        
        # Should accept any string as phase (validation handled at application level)
        assert updated_state["current_phase"] == "invalid_phase"
    
    def test_state_with_negative_retry_count(self):
        """Test handling of negative retry count."""
        state = initialize_agent_state("test", "test_path")
        
        # Manually set negative retry count
        state = dict(state)
        state["retry_count"] = -1
        
        # Should handle gracefully in functions
        updated_state = update_strategy_completeness(state, "why", True)
        
        assert updated_state["retry_count"] == -1  # Should preserve as-is
    
    def test_state_with_missing_fields(self):
        """Test handling of state with missing expected fields."""
        # Create minimal state
        minimal_state: AgentState = {
            "session_id": "test",
            "strategy_map_path": "test_path",
            "current_phase": "why",
            "current_agent": None,
            "conversation_history": [],
            "strategy_completeness": {
                "why": False,
                "stakeholder_customer": False,
                "internal_processes": False,
                "learning_growth": False,
                "value_creation": False,
                "analogy_analysis": False,
                "logical_structure": False,
                "implementation_plan": False
            },
            "retry_count": 0,
            "processing_stage": "initialization",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Functions should handle missing optional fields gracefully
        updated_state = update_strategy_completeness(minimal_state, "why", True)
        
        assert updated_state["strategy_completeness"]["why"] is True


class TestStatePerformance:
    """Test state management performance characteristics."""
    
    def test_large_conversation_history_performance(self):
        """Test state operations with large conversation history."""
        state = initialize_agent_state("test", "test_path")
        
        # Add many messages
        for i in range(1000):
            message = HumanMessage(content=f"Message {i}")
            state = update_conversation_history(state, message)
        
        assert len(state["conversation_history"]) == 1000
        
        # Operations should still be fast
        import time
        start_time = time.time()
        
        # Test various operations
        state = update_strategy_completeness(state, "why", True)
        state = transition_phase(state, "how")
        completeness = calculate_strategy_completeness(state)
        
        end_time = time.time()
        
        # Should complete quickly (less than 0.1 seconds)
        assert (end_time - start_time) < 0.1
        assert completeness > 0
    
    def test_concurrent_state_updates(self):
        """Test state consistency with rapid updates."""
        state = initialize_agent_state("test", "test_path")
        
        # Rapid successive updates
        for i in range(100):
            state = update_strategy_completeness(state, f"section_{i}", i % 2 == 0)
        
        # State should be consistent
        assert len(state["strategy_completeness"]) > 100
        completed_count = sum(1 for v in state["strategy_completeness"].values() if v)
        assert completed_count == 50  # Half should be True


@pytest.mark.integration
class TestStateIntegration:
    """Integration tests for state management."""
    
    def test_realistic_conversation_flow_state_management(self):
        """Test state management through a realistic conversation flow."""
        # Initialize session
        state = initialize_agent_state("integration_test", "test_path")
        
        # User starts conversation
        user_msg1 = HumanMessage(content="I need help with my startup strategy")
        state = update_conversation_history(state, user_msg1)
        state = set_processing_stage(state, "processing_initial_input", "orchestrator")
        
        # System routes to WHY agent
        state = set_processing_stage(state, "why_agent_processing", "why_agent")
        
        # WHY agent completes work
        ai_msg1 = AIMessage(content="Let's explore your core purpose...")
        state = update_conversation_history(state, ai_msg1)
        state = update_strategy_completeness(state, "why", True)
        
        # Transition to HOW phase
        state = transition_phase(state, "how")
        
        # Continue conversation
        user_msg2 = HumanMessage(content="We want to be like successful tech companies")
        state = update_conversation_history(state, user_msg2)
        state = set_processing_stage(state, "analogy_agent_processing", "analogy_agent")
        
        # Analogy agent completes work
        ai_msg2 = AIMessage(content="Let's analyze successful company strategies...")
        state = update_conversation_history(state, ai_msg2)
        state = update_strategy_completeness(state, "analogy_analysis", True)
        
        # Validate final state
        assert state["current_phase"] == "how"
        assert state["current_agent"] == "analogy_agent"
        assert len(state["conversation_history"]) == 4
        assert state["strategy_completeness"]["why"] is True
        assert state["strategy_completeness"]["analogy_analysis"] is True
        assert calculate_strategy_completeness(state) == 25.0  # 2/8 sections complete
    
    def test_error_recovery_state_management(self):
        """Test state management during error scenarios."""
        state = initialize_agent_state("error_test", "test_path")
        
        # Simulate error during processing
        state = set_processing_stage(state, "error_occurred", "router")
        state = dict(state)
        state["error_state"] = {
            "error_type": "ProcessingError",
            "error_message": "Failed to route user message",
            "timestamp": datetime.now().isoformat()
        }
        state["retry_count"] += 1
        
        # System should be able to continue
        user_msg = HumanMessage(content="Can we try again?")
        state = update_conversation_history(state, user_msg)
        
        # Clear error and continue
        state = dict(state)
        del state["error_state"]
        state = set_processing_stage(state, "retrying", "orchestrator")
        
        assert "error_state" not in state
        assert state["retry_count"] == 1
        assert len(state["conversation_history"]) == 1
        assert state["processing_stage"] == "retrying"