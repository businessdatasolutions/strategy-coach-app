import pytest
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, AIMessage

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


class TestAgentStateInitialization:
    """Test agent state initialization and basic operations."""
    
    def test_initialize_agent_state_basic(self):
        """Test basic agent state initialization."""
        session_id = "test_session_123"
        strategy_map_path = "data/sessions/test_session_123_strategy_map.json"
        
        state = initialize_agent_state(session_id, strategy_map_path)
        
        assert state["session_id"] == session_id
        assert state["strategy_map_path"] == strategy_map_path
        assert state["current_phase"] == "why"
        assert state["current_agent"] is None
        assert state["conversation_history"] == []
        assert state["retry_count"] == 0
        assert state["processing_stage"] == "initialization"
        assert isinstance(state["created_at"], datetime)
        assert isinstance(state["updated_at"], datetime)
    
    def test_initialize_agent_state_with_user_context(self):
        """Test agent state initialization with user context."""
        session_id = "test_session_123"
        strategy_map_path = "data/sessions/test_session_123_strategy_map.json"
        user_id = "user_456"
        user_context = {
            "company_type": "startup",
            "industry": "technology",
            "team_size": "5-10"
        }
        
        state = initialize_agent_state(
            session_id, 
            strategy_map_path, 
            user_id=user_id,
            user_context=user_context
        )
        
        assert state["user_id"] == user_id
        assert state["user_context"] == user_context
    
    def test_strategy_completeness_initialization(self):
        """Test that strategy completeness is properly initialized."""
        state = initialize_agent_state("test", "test_path")
        
        expected_sections = [
            "why", "stakeholder_customer", "internal_processes",
            "learning_growth", "value_creation", "analogy_analysis",
            "logical_structure", "implementation_plan"
        ]
        
        assert len(state["strategy_completeness"]) == len(expected_sections)
        for section in expected_sections:
            assert section in state["strategy_completeness"]
            assert state["strategy_completeness"][section] is False


class TestStateUpdateFunctions:
    """Test state update utility functions."""
    
    def test_update_conversation_history(self):
        """Test adding messages to conversation history."""
        state = initialize_agent_state("test", "test_path")
        original_time = state["updated_at"]
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        message = HumanMessage(content="Hello, I need help with strategy")
        updated_state = update_conversation_history(state, message)
        
        assert len(updated_state["conversation_history"]) == 1
        assert updated_state["conversation_history"][0] == message
        assert updated_state["updated_at"] > original_time
    
    def test_update_conversation_history_multiple_messages(self):
        """Test adding multiple messages to conversation history."""
        state = initialize_agent_state("test", "test_path")
        
        message1 = HumanMessage(content="Hello")
        message2 = AIMessage(content="Hi there!")
        message3 = HumanMessage(content="I need strategy help")
        
        state = update_conversation_history(state, message1)
        state = update_conversation_history(state, message2)
        state = update_conversation_history(state, message3)
        
        assert len(state["conversation_history"]) == 3
        assert state["conversation_history"][0].content == "Hello"
        assert state["conversation_history"][1].content == "Hi there!"
        assert state["conversation_history"][2].content == "I need strategy help"
    
    def test_update_strategy_completeness(self):
        """Test updating strategy section completeness."""
        state = initialize_agent_state("test", "test_path")
        original_time = state["updated_at"]
        
        import time
        time.sleep(0.01)
        
        updated_state = update_strategy_completeness(state, "why", True)
        
        assert updated_state["strategy_completeness"]["why"] is True
        assert updated_state["updated_at"] > original_time
        
        # Test updating back to false
        updated_state = update_strategy_completeness(updated_state, "why", False)
        assert updated_state["strategy_completeness"]["why"] is False
    
    def test_transition_phase(self):
        """Test phase transitions."""
        state = initialize_agent_state("test", "test_path")
        
        # Initial phase should be "why"
        assert state["current_phase"] == "why"
        
        # Transition to "how" phase
        updated_state = transition_phase(state, "how")
        assert updated_state["current_phase"] == "how"
        assert updated_state["current_agent"] is None  # Should reset agent
        
        # Transition to "what" phase
        updated_state = transition_phase(updated_state, "what")
        assert updated_state["current_phase"] == "what"
    
    def test_set_processing_stage(self):
        """Test setting processing stage and active agent."""
        state = initialize_agent_state("test", "test_path")
        
        updated_state = set_processing_stage(state, "analyzing_input", "why_agent")
        
        assert updated_state["processing_stage"] == "analyzing_input"
        assert updated_state["current_agent"] == "why_agent"
        
        # Test setting stage without agent
        updated_state = set_processing_stage(updated_state, "waiting_for_user")
        assert updated_state["processing_stage"] == "waiting_for_user"
        assert updated_state["current_agent"] == "why_agent"  # Should remain unchanged


class TestStrategyCompletenessCalculation:
    """Test strategy completeness calculation."""
    
    def test_calculate_completeness_empty(self):
        """Test completeness calculation with no completed sections."""
        state = initialize_agent_state("test", "test_path")
        
        completeness = calculate_strategy_completeness(state)
        assert completeness == 0.0
    
    def test_calculate_completeness_partial(self):
        """Test completeness calculation with some completed sections."""
        state = initialize_agent_state("test", "test_path")
        
        # Complete 2 out of 8 sections
        state = update_strategy_completeness(state, "why", True)
        state = update_strategy_completeness(state, "stakeholder_customer", True)
        
        completeness = calculate_strategy_completeness(state)
        assert completeness == 25.0  # 2/8 * 100
    
    def test_calculate_completeness_full(self):
        """Test completeness calculation with all sections completed."""
        state = initialize_agent_state("test", "test_path")
        
        # Complete all sections
        sections = [
            "why", "stakeholder_customer", "internal_processes",
            "learning_growth", "value_creation", "analogy_analysis",
            "logical_structure", "implementation_plan"
        ]
        
        for section in sections:
            state = update_strategy_completeness(state, section, True)
        
        completeness = calculate_strategy_completeness(state)
        assert completeness == 100.0


class TestTypedDictStructures:
    """Test TypedDict structures are properly defined."""
    
    def test_agent_input_structure(self):
        """Test AgentInput TypedDict structure."""
        state = initialize_agent_state("test", "test_path")
        
        strategy_map_state: StrategyMapState = {
            "session_id": "test",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "version": 1,
            "why": {},
            "stakeholder_customer": {},
            "internal_processes": {},
            "learning_growth": {},
            "value_creation": {},
            "analogy_analysis": None,
            "logical_structure": None,
            "implementation_plan": None,
            "completed_sections": [],
            "completeness_percentage": 0.0
        }
        
        phase_context: ConversationPhase = {
            "phase_name": "why",
            "phase_description": "Exploring the core purpose",
            "active_agents": ["why_agent"],
            "required_outputs": ["purpose", "belief"],
            "completion_criteria": {"min_purpose_clarity": 0.8},
            "next_phase": "how"
        }
        
        agent_input: AgentInput = {
            "state": state,
            "user_message": "I want to develop a strategy",
            "conversation_context": [],
            "strategy_map_state": strategy_map_state,
            "phase_context": phase_context
        }
        
        # Test that we can create and access the structure
        assert agent_input["user_message"] == "I want to develop a strategy"
        assert agent_input["phase_context"]["phase_name"] == "why"
        assert agent_input["strategy_map_state"]["session_id"] == "test"
    
    def test_agent_output_structure(self):
        """Test AgentOutput TypedDict structure."""
        agent_output: AgentOutput = {
            "agent_type": "why_agent",
            "response": "Let's explore your core purpose...",
            "questions": ["What problem are you solving?", "Why does this matter?"],
            "topics_to_explore": ["core_purpose", "target_audience"],
            "strategy_updates": {"purpose_clarity": 0.6},
            "confidence_score": 0.8,
            "requires_followup": True,
            "suggested_next_agent": "analogy_agent"
        }
        
        assert agent_output["agent_type"] == "why_agent"
        assert len(agent_output["questions"]) == 2
        assert agent_output["confidence_score"] == 0.8
    
    def test_router_decision_structure(self):
        """Test RouterDecision TypedDict structure."""
        router_decision: RouterDecision = {
            "next_node": "why_agent",
            "reasoning": "User needs to clarify their core purpose",
            "priority": 1,
            "context": {"current_clarity": 0.3, "missing_elements": ["purpose"]}
        }
        
        assert router_decision["next_node"] == "why_agent"
        assert router_decision["priority"] == 1
        assert "current_clarity" in router_decision["context"]


@pytest.mark.unit
class TestStateTimestamps:
    """Test timestamp handling in state updates."""
    
    def test_timestamps_are_updated(self):
        """Test that timestamps are properly updated on state changes."""
        state = initialize_agent_state("test", "test_path")
        original_time = state["updated_at"]
        
        import time
        time.sleep(0.01)
        
        # Update conversation history
        message = HumanMessage(content="Test")
        state = update_conversation_history(state, message)
        
        assert state["updated_at"] > original_time
        assert state["created_at"] <= state["updated_at"]
    
    def test_created_at_remains_constant(self):
        """Test that created_at timestamp doesn't change on updates."""
        state = initialize_agent_state("test", "test_path")
        original_created = state["created_at"]
        
        # Make several updates
        state = update_strategy_completeness(state, "why", True)
        state = transition_phase(state, "how")
        state = set_processing_stage(state, "processing")
        
        assert state["created_at"] == original_created