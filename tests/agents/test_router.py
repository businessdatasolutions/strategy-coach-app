import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.router import AdvancedRouter, UserIntentSignals
from src.models.state import initialize_agent_state, RouterDecision


class TestAdvancedRouter:
    """Test the Advanced Router functionality."""
    
    def test_router_initialization(self):
        """Test that router initializes successfully."""
        router = AdvancedRouter()
        
        assert router.signal_patterns is not None
        assert router.phase_transition_rules is not None
        assert router.agent_capabilities is not None
        
        # Verify signal patterns contain expected categories
        expected_patterns = ["purpose", "why", "strategy", "comparison", "logic", 
                           "execution", "stakeholder", "process", "questions", 
                           "clarification", "completion"]
        for pattern in expected_patterns:
            assert pattern in router.signal_patterns
    
    def test_make_routing_decision_basic(self):
        """Test basic routing decision making."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        decision = router.make_routing_decision(state)
        
        assert isinstance(decision, dict)
        assert "next_node" in decision
        assert "reasoning" in decision
        assert "priority" in decision
        assert "context" in decision
        assert decision["next_node"] in ["why_agent", "analogy_agent", "logic_agent", 
                                       "open_strategy_agent", "strategy_map_agent", "synthesize"]
    
    def test_routing_decision_why_phase(self):
        """Test routing decision in WHY phase."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Should default to WHY phase with incomplete sections
        decision = router.make_routing_decision(state)
        
        assert decision["next_node"] == "why_agent"
        assert decision["context"]["current_phase"] == "why"
        assert isinstance(decision["priority"], int)
        assert decision["priority"] >= 1
    
    def test_routing_decision_how_phase(self):
        """Test routing decision in HOW phase with appropriate signals."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up HOW phase with strategic signals
        state["current_phase"] = "how"
        state["strategy_completeness"]["why"] = True
        
        # Add strategic comparison signals
        user_message = HumanMessage(content="I need a strategic approach similar to successful companies")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        assert decision["next_node"] in ["analogy_agent", "logic_agent"]
        assert decision["context"]["current_phase"] == "how"
    
    def test_routing_decision_what_phase(self):
        """Test routing decision in WHAT phase."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up WHAT phase
        state["current_phase"] = "what"
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        
        decision = router.make_routing_decision(state)
        
        assert decision["next_node"] in ["strategy_map_agent", "open_strategy_agent"]
        assert decision["context"]["current_phase"] == "what"
    
    def test_routing_decision_high_completeness(self):
        """Test routing decision when strategy is highly complete."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Mark most sections as complete
        sections = ["why", "analogy_analysis", "logical_structure", 
                   "stakeholder_customer", "value_creation", "internal_processes", "learning_growth"]
        for section in sections:
            state["strategy_completeness"][section] = True
        
        # Add completion signals
        user_message = HumanMessage(content="I think we're done and ready for a summary")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        assert decision["next_node"] == "synthesize"
        assert "synthesis" in decision["reasoning"].lower() or "complete" in decision["reasoning"].lower()
    
    def test_routing_with_error_state(self):
        """Test routing behavior with error state."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        state["error_state"] = {"error": "test error"}
        
        decision = router.make_routing_decision(state)
        
        assert decision["next_node"] == "end"
        assert "error" in decision["reasoning"].lower()
    
    def test_routing_with_retry_limit_exceeded(self):
        """Test routing behavior when retry limit is exceeded."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        state["retry_count"] = 10
        
        decision = router.make_routing_decision(state)
        
        assert decision["next_node"] == "end"
        assert "retry" in decision["reasoning"].lower()


class TestUserIntentAnalysis:
    """Test user intent analysis functionality."""
    
    def test_analyze_user_intent_empty_conversation(self):
        """Test user intent analysis with empty conversation."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Should handle empty conversation gracefully
        decision = router.make_routing_decision(state)
        assert decision is not None
    
    def test_analyze_user_intent_purpose_signals(self):
        """Test detection of purpose-related signals."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Add purpose-focused user message
        user_message = HumanMessage(content="What is our core purpose and mission?")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        # Should route to WHY agent for purpose exploration
        assert decision["next_node"] == "why_agent"
    
    def test_analyze_user_intent_strategy_signals(self):
        """Test detection of strategy-related signals."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for strategic thinking
        state["current_phase"] = "how"
        state["strategy_completeness"]["why"] = True
        
        # Add strategy-focused user message
        user_message = HumanMessage(content="How should we approach our market strategy?")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        # Should route to strategy-focused agent
        assert decision["next_node"] in ["analogy_agent", "logic_agent"]
    
    def test_analyze_user_intent_comparison_signals(self):
        """Test detection of comparison-related signals."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        state["current_phase"] = "how"
        state["strategy_completeness"]["why"] = True
        
        # Add comparison-focused user message
        user_message = HumanMessage(content="We want to be like Apple with their innovation approach")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        # Should route to analogy agent for comparison analysis
        assert decision["next_node"] == "analogy_agent"
    
    def test_analyze_user_intent_implementation_signals(self):
        """Test detection of implementation-related signals."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        state["current_phase"] = "what"
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        
        # Add implementation-focused user message
        user_message = HumanMessage(content="How do we execute this strategy with our stakeholders?")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        # Should route to implementation-focused agent
        assert decision["next_node"] in ["open_strategy_agent", "strategy_map_agent"]


class TestAgentScoring:
    """Test agent scoring logic."""
    
    def test_why_agent_scoring(self):
        """Test WHY agent scoring logic."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Add purpose signals
        user_message = HumanMessage(content="Why do we exist as an organization?")
        state["conversation_history"] = [user_message]
        
        user_intent = router._analyze_user_intent(state)
        conversation_context = router._analyze_conversation_context(state)
        strategy_analysis = router._analyze_strategy_completeness(state)
        
        scores = router._calculate_agent_scores(state, user_intent, conversation_context, strategy_analysis)
        
        # WHY agent should have high score for purpose exploration
        assert scores["why_agent"] > 0.5
        assert scores["why_agent"] >= max(scores["analogy_agent"], scores["logic_agent"])
    
    def test_analogy_agent_scoring(self):
        """Test Analogy agent scoring logic."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up conditions favorable to analogy agent
        state["current_phase"] = "how"
        state["strategy_completeness"]["why"] = True
        
        user_message = HumanMessage(content="We want to be like successful companies in our space")
        state["conversation_history"] = [user_message]
        
        user_intent = router._analyze_user_intent(state)
        conversation_context = router._analyze_conversation_context(state)
        strategy_analysis = router._analyze_strategy_completeness(state)
        
        scores = router._calculate_agent_scores(state, user_intent, conversation_context, strategy_analysis)
        
        # Analogy agent should have high score for comparison-based reasoning
        assert scores["analogy_agent"] > 0.5
    
    def test_logic_agent_scoring(self):
        """Test Logic agent scoring logic."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up conditions favorable to logic agent
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        
        user_message = HumanMessage(content="Does our strategic approach make logical sense?")
        state["conversation_history"] = [user_message]
        
        user_intent = router._analyze_user_intent(state)
        conversation_context = router._analyze_conversation_context(state)
        strategy_analysis = router._analyze_strategy_completeness(state)
        
        scores = router._calculate_agent_scores(state, user_intent, conversation_context, strategy_analysis)
        
        # Logic agent should score well for validation queries
        assert scores["logic_agent"] > 0.3
    
    def test_synthesis_scoring(self):
        """Test synthesis scoring logic."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up high completeness scenario
        sections = ["why", "analogy_analysis", "logical_structure", 
                   "stakeholder_customer", "value_creation", "internal_processes"]
        for section in sections:
            state["strategy_completeness"][section] = True
        
        # Add completion signals to trigger synthesis
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi"),
            HumanMessage(content="Let's work on strategy"),
            AIMessage(content="Sure"),
            HumanMessage(content="I think we're done and ready for the final summary"),
        ]
        state["conversation_history"] = messages
        
        user_intent = router._analyze_user_intent(state)
        conversation_context = router._analyze_conversation_context(state)
        strategy_analysis = router._analyze_strategy_completeness(state)
        
        scores = router._calculate_agent_scores(state, user_intent, conversation_context, strategy_analysis)
        
        # Synthesis should score well with high completeness and completion signals
        assert scores["synthesize"] > 0.3  # Lower threshold due to completion logic


class TestSignalExtraction:
    """Test signal extraction from user input."""
    
    def test_extract_purpose_signals(self):
        """Test extraction of purpose-related signals."""
        router = AdvancedRouter()
        text = "What is our core purpose and organizational mission?"
        patterns = router.signal_patterns["purpose"]
        
        signals = router._extract_signals(text, patterns)
        
        assert len(signals) > 0
        assert any("purpose" in signal for signal in signals)
    
    def test_extract_comparison_signals(self):
        """Test extraction of comparison-related signals."""
        router = AdvancedRouter()
        text = "We want to be like Apple, similar to their innovation approach"
        patterns = router.signal_patterns["comparison"]
        
        signals = router._extract_signals(text, patterns)
        
        assert len(signals) > 0
        assert any(signal in ["like", "similar"] for signal in signals)
    
    def test_extract_logic_signals(self):
        """Test extraction of logic-related signals."""
        router = AdvancedRouter()
        text = "Does this approach make logical sense and is it consistent?"
        patterns = router.signal_patterns["logic"]
        
        signals = router._extract_signals(text, patterns)
        
        assert len(signals) > 0
        assert any(signal in ["logical", "consistent"] for signal in signals)
    
    def test_calculate_urgency(self):
        """Test urgency level calculation."""
        router = AdvancedRouter()
        
        # High urgency text
        high_urgency = "This is urgent and critical, we need it ASAP"
        urgency_high = router._calculate_urgency(high_urgency)
        
        # Low urgency text
        low_urgency = "We can work on this when convenient"
        urgency_low = router._calculate_urgency(low_urgency)
        
        assert urgency_high > urgency_low
        assert 0.0 <= urgency_high <= 1.0
        assert 0.0 <= urgency_low <= 1.0
    
    def test_calculate_confidence(self):
        """Test confidence level calculation."""
        router = AdvancedRouter()
        
        # High confidence text
        high_confidence = "I'm certain this is the right approach, very clear"
        confidence_high = router._calculate_confidence(high_confidence)
        
        # Low confidence text
        low_confidence = "I'm not sure about this, maybe we need help"
        confidence_low = router._calculate_confidence(low_confidence)
        
        assert confidence_high > confidence_low
        assert 0.0 <= confidence_high <= 1.0
        assert 0.0 <= confidence_low <= 1.0


class TestRouterEdgeCases:
    """Test router behavior in edge cases."""
    
    def test_routing_with_empty_message_history(self):
        """Test routing with no conversation history."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Ensure conversation history is empty
        state["conversation_history"] = []
        
        decision = router.make_routing_decision(state)
        
        # Should still make a valid decision
        assert decision["next_node"] is not None
        assert decision["reasoning"] is not None
    
    def test_routing_with_long_conversation_history(self):
        """Test routing with extensive conversation history."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Create long conversation history
        messages = []
        for i in range(20):
            messages.append(HumanMessage(content=f"Message {i}"))
            messages.append(AIMessage(content=f"Response {i}"))
        
        state["conversation_history"] = messages
        
        decision = router.make_routing_decision(state)
        
        # Should handle long conversation gracefully
        assert decision["next_node"] is not None
        assert "conversation_turn" in decision["context"]
        assert decision["context"]["conversation_turn"] >= 10
    
    def test_routing_with_malformed_state(self):
        """Test routing robustness with malformed state."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Create a copy and modify it to test robustness
        import copy
        test_state = copy.deepcopy(state)
        
        # Remove expected field to test robustness
        if "why" in test_state["strategy_completeness"]:
            del test_state["strategy_completeness"]["why"]
        
        # Should handle gracefully without crashing
        decision = router.make_routing_decision(test_state)
        
        assert decision["next_node"] is not None
    
    def test_agent_selection_with_tied_scores(self):
        """Test agent selection when multiple agents have similar scores."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up scenario where multiple agents might score similarly
        state["current_phase"] = "how"
        state["strategy_completeness"]["why"] = True
        
        user_message = HumanMessage(content="strategic logical approach")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        # Should make a decision even with similar scores
        assert decision["next_node"] in ["analogy_agent", "logic_agent"]
        assert decision["priority"] >= 1


@pytest.mark.integration
class TestRouterIntegration:
    """Integration tests for router with realistic scenarios."""
    
    def test_full_conversation_flow_routing(self):
        """Test router decisions through a complete conversation flow."""
        router = AdvancedRouter()
        
        # Initial state
        state1 = initialize_agent_state("test_session", "test_path")
        user_msg1 = HumanMessage(content="I need help developing a strategy")
        state1["conversation_history"] = [user_msg1]
        
        decision1 = router.make_routing_decision(state1)
        assert decision1["next_node"] == "why_agent"
        
        # After WHY phase
        state2 = initialize_agent_state("test_session", "test_path")
        state2["current_phase"] = "how"
        state2["strategy_completeness"]["why"] = True
        user_msg2 = HumanMessage(content="Now I need a strategic approach like successful companies")
        state2["conversation_history"] = [user_msg1, user_msg2]
        
        decision2 = router.make_routing_decision(state2)
        assert decision2["next_node"] == "analogy_agent"
        
        # After HOW phase
        state3 = initialize_agent_state("test_session", "test_path")
        state3["current_phase"] = "what"
        state3["strategy_completeness"]["why"] = True
        state3["strategy_completeness"]["analogy_analysis"] = True
        user_msg3 = HumanMessage(content="How do we implement this with our stakeholders?")
        state3["conversation_history"] = [user_msg1, user_msg2, user_msg3]
        
        decision3 = router.make_routing_decision(state3)
        assert decision3["next_node"] in ["open_strategy_agent", "strategy_map_agent"]
    
    def test_router_context_preservation(self):
        """Test that router context is properly preserved and used."""
        router = AdvancedRouter()
        state = initialize_agent_state("test_session", "test_path")
        
        user_message = HumanMessage(content="I'm confused about our strategic direction")
        state["conversation_history"] = [user_message]
        
        decision = router.make_routing_decision(state)
        
        # Context should contain relevant information
        assert "current_phase" in decision["context"]
        assert "user_intent_summary" in decision["context"]
        assert "strategy_completeness" in decision["context"]
        assert "conversation_turn" in decision["context"]