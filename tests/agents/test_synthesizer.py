import pytest
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.synthesizer import ConversationSynthesizer, ResponseType
from src.models.state import initialize_agent_state


class TestConversationSynthesizer:
    """Test the Conversation Synthesizer."""
    
    def test_synthesizer_initialization(self):
        """Test that synthesizer initializes successfully."""
        synthesizer = ConversationSynthesizer()
        
        assert synthesizer.response_templates is not None
        assert synthesizer.phase_transitions is not None
        assert synthesizer.question_strategies is not None
    
    def test_synthesize_response_basic(self):
        """Test basic response synthesis."""
        synthesizer = ConversationSynthesizer()
        state = initialize_agent_state("test_session", "test_path")
        
        response = synthesizer.synthesize_response(state)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "purpose" in response.lower() or "strategy" in response.lower()
    
    def test_synthesize_response_with_conversation(self):
        """Test response synthesis with existing conversation."""
        synthesizer = ConversationSynthesizer()
        state = initialize_agent_state("test_session", "test_path")
        
        # Add some conversation history
        user_message = HumanMessage(content="I need help with my startup strategy")
        ai_message = AIMessage(content="I'd love to help you with that!")
        state["conversation_history"] = [user_message, ai_message]
        
        response = synthesizer.synthesize_response(state)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_synthesize_response_high_completeness(self):
        """Test response synthesis with high strategy completeness."""
        synthesizer = ConversationSynthesizer()
        state = initialize_agent_state("test_session", "test_path")
        
        # Mark most sections as complete
        sections = ["why", "analogy_analysis", "logical_structure", 
                   "stakeholder_customer", "value_creation", "internal_processes"]
        for section in sections:
            state["strategy_completeness"][section] = True
        
        response = synthesizer.synthesize_response(state)
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should indicate progress or completion
        assert any(word in response.lower() for word in ["progress", "complete", "strategy", "excellent"])
    
    def test_different_response_types(self):
        """Test that synthesizer can generate different response types."""
        synthesizer = ConversationSynthesizer()
        
        # Test early conversation (should be question type)
        state_early = initialize_agent_state("test_session", "test_path")
        response_early = synthesizer.synthesize_response(state_early)
        
        # Test high completeness (should be completion or summary type)
        state_complete = initialize_agent_state("test_session", "test_path")
        for section in state_complete["strategy_completeness"]:
            state_complete["strategy_completeness"][section] = True
        response_complete = synthesizer.synthesize_response(state_complete)
        
        # Responses should be different
        assert response_early != response_complete
        assert len(response_early) > 0
        assert len(response_complete) > 0
    
    def test_follow_up_questions_generation(self):
        """Test that follow-up questions are generated appropriately."""
        synthesizer = ConversationSynthesizer()
        state = initialize_agent_state("test_session", "test_path")
        
        response = synthesizer.synthesize_response(state)
        
        # Early conversation should include questions
        assert "?" in response or "Question" in response or "question" in response
    
    def test_progress_indication(self):
        """Test progress indication in responses."""
        synthesizer = ConversationSynthesizer()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set some completion
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        
        response = synthesizer.synthesize_response(state)
        
        # Should include some progress indication
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_phase_specific_responses(self):
        """Test that responses are appropriate for different phases."""
        synthesizer = ConversationSynthesizer()
        
        # Test WHY phase
        state_why = initialize_agent_state("test_session", "test_path")
        state_why["current_phase"] = "why"
        response_why = synthesizer.synthesize_response(state_why)
        
        # Test HOW phase  
        state_how = initialize_agent_state("test_session", "test_path")
        state_how["current_phase"] = "how"
        state_how["strategy_completeness"]["why"] = True  # Complete why first
        user_message = HumanMessage(content="I want a strategy like successful companies")
        state_how["conversation_history"] = [user_message]
        response_how = synthesizer.synthesize_response(state_how)
        
        # Test WHAT phase
        state_what = initialize_agent_state("test_session", "test_path")
        state_what["current_phase"] = "what"
        state_what["strategy_completeness"]["why"] = True
        state_what["strategy_completeness"]["analogy_analysis"] = True
        response_what = synthesizer.synthesize_response(state_what)
        
        # All should be different and contextually appropriate
        assert response_why != response_how != response_what
        assert all(len(resp) > 0 for resp in [response_why, response_how, response_what])
    
    def test_error_handling_in_synthesis_context(self):
        """Test that synthesizer handles missing or invalid data gracefully."""
        synthesizer = ConversationSynthesizer()
        
        # Test with minimal state
        state = initialize_agent_state("test_session", "test_path")
        # Remove some expected fields to test robustness
        if "routing_context" in state:
            del state["routing_context"]
        
        response = synthesizer.synthesize_response(state)
        
        # Should still generate a valid response
        assert isinstance(response, str)
        assert len(response) > 0


class TestSynthesisContext:
    """Test synthesis context building and handling."""
    
    def test_context_building(self):
        """Test that synthesis context is built correctly."""
        synthesizer = ConversationSynthesizer()
        state = initialize_agent_state("test_session", "test_path")
        state["current_agent"] = "why_agent"
        state["agent_output"] = "Test output"
        
        context = synthesizer._build_synthesis_context(state)
        
        assert context.current_agent == "why_agent"
        assert context.agent_output == "Test output"
        assert context.current_phase == "why"
        assert isinstance(context.strategy_completeness, float)
        assert isinstance(context.conversation_turn, int)
        assert isinstance(context.gaps_identified, list)
    
    def test_response_type_determination(self):
        """Test response type determination logic."""
        synthesizer = ConversationSynthesizer()
        
        # Test completion type
        state_complete = initialize_agent_state("test_session", "test_path")
        for section in state_complete["strategy_completeness"]:
            state_complete["strategy_completeness"][section] = True
        
        context_complete = synthesizer._build_synthesis_context(state_complete)
        response_type_complete = synthesizer._determine_response_type(context_complete, state_complete)
        
        assert response_type_complete in [ResponseType.COMPLETION, ResponseType.SUMMARY]
        
        # Test question type for early conversation
        state_early = initialize_agent_state("test_session", "test_path")
        context_early = synthesizer._build_synthesis_context(state_early)
        response_type_early = synthesizer._determine_response_type(context_early, state_early)
        
        assert response_type_early == ResponseType.QUESTION
    
    def test_follow_up_question_generation(self):
        """Test follow-up question generation for different phases."""
        synthesizer = ConversationSynthesizer()
        
        # Test WHY phase questions
        state_why = initialize_agent_state("test_session", "test_path")
        state_why["current_phase"] = "why"
        context_why = synthesizer._build_synthesis_context(state_why)
        
        questions_why = synthesizer._generate_follow_up_questions(context_why, state_why)
        if questions_why:
            assert "purpose" in questions_why.lower() or "why" in questions_why.lower()
        
        # Test HOW phase questions
        state_how = initialize_agent_state("test_session", "test_path")
        state_how["current_phase"] = "how"
        state_how["strategy_completeness"]["why"] = True
        context_how = synthesizer._build_synthesis_context(state_how)
        
        questions_how = synthesizer._generate_follow_up_questions(context_how, state_how)
        if questions_how:
            assert any(word in questions_how.lower() for word in ["strategy", "approach", "companies", "example"])


@pytest.mark.integration
class TestSynthesizerIntegration:
    """Integration tests for synthesizer with realistic scenarios."""
    
    def test_realistic_conversation_flow(self):
        """Test synthesizer behavior in a realistic conversation flow."""
        synthesizer = ConversationSynthesizer()
        
        # Simulate conversation progression
        states = []
        
        # Initial state
        state1 = initialize_agent_state("test_session", "test_path")
        user_msg1 = HumanMessage(content="I need help developing a strategy for my tech startup")
        state1["conversation_history"] = [user_msg1]
        states.append(state1)
        
        # After some progress
        state2 = initialize_agent_state("test_session", "test_path")
        state2["strategy_completeness"]["why"] = True
        state2["current_phase"] = "how"
        user_msg2 = HumanMessage(content="I understand our purpose now, how should we approach the market?")
        state2["conversation_history"] = [user_msg1, user_msg2]
        states.append(state2)
        
        # Near completion
        state3 = initialize_agent_state("test_session", "test_path") 
        for section in ["why", "analogy_analysis", "stakeholder_customer", "value_creation"]:
            state3["strategy_completeness"][section] = True
        state3["current_phase"] = "what"
        user_msg3 = HumanMessage(content="This looks great! What are our next steps?")
        state3["conversation_history"] = [user_msg1, user_msg2, user_msg3]
        states.append(state3)
        
        responses = []
        for state in states:
            response = synthesizer.synthesize_response(state)
            responses.append(response)
            assert isinstance(response, str)
            assert len(response) > 0
        
        # Responses should show progression
        assert len(set(responses)) == len(responses)  # All different
        
        # Last response should indicate higher completion
        final_response = responses[-1]
        assert any(word in final_response.lower() for word in 
                  ["progress", "great", "excellent", "complete", "next", "implementation"])