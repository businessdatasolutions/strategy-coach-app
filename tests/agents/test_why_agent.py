import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.why_agent import WhyAgent, create_why_agent_node
from src.models.state import initialize_agent_state
from src.utils.llm_client import LLMClientError


class TestWhyAgent:
    """Test the WHY Agent functionality."""
    
    def test_why_agent_initialization(self):
        """Test that WHY Agent initializes successfully."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            
            agent = WhyAgent()
            
            assert agent.methodology == "Simon Sinek's Golden Circle"
            assert agent.focus_areas == ["core_purpose", "core_beliefs", "organizational_values"]
            assert hasattr(agent, 'purpose_discovery_prompt')
            assert hasattr(agent, 'belief_exploration_prompt')
            assert hasattr(agent, 'values_integration_prompt')
            assert hasattr(agent, 'synthesis_prompt')
    
    def test_determine_why_stage_initial(self):
        """Test stage determination for initial conversation."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Should start with purpose discovery
            stage = agent._determine_why_stage(state)
            assert stage == "purpose_discovery"
    
    def test_determine_why_stage_purpose_discovery(self):
        """Test stage determination during purpose discovery."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with purpose indicators
            messages = [
                HumanMessage(content="What is our organizational purpose?"),
                AIMessage(content="Let's explore your core purpose and mission..."),
                HumanMessage(content="We exist to help people achieve their goals"),
                AIMessage(content="That's a great start to understanding your why...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_why_stage(state)
            assert stage == "belief_exploration"
    
    def test_determine_why_stage_belief_exploration(self):
        """Test stage determination during belief exploration."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with purpose and belief indicators
            messages = [
                HumanMessage(content="Our purpose is to empower people"),
                AIMessage(content="Let's explore your core beliefs that drive this purpose..."),
                HumanMessage(content="We believe everyone has untapped potential"),
                AIMessage(content="That belief shapes how you approach your work..."),
                HumanMessage(content="We're convinced that the right support unlocks success"),
                AIMessage(content="These convictions are powerful...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_why_stage(state)
            assert stage == "values_integration"
    
    def test_determine_why_stage_synthesis(self):
        """Test stage determination for synthesis."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add comprehensive conversation
            messages = []
            # Add purpose discovery conversation
            for i in range(4):
                messages.extend([
                    HumanMessage(content=f"Purpose discussion {i}: our core purpose is clear"),
                    AIMessage(content=f"Great insight about your purpose...")
                ])
            
            # Add belief exploration  
            for i in range(2):
                messages.extend([
                    HumanMessage(content=f"Belief discussion {i}: we believe in potential"),
                    AIMessage(content=f"These beliefs drive your organization...")
                ])
            
            # Add values discussion
            messages.extend([
                HumanMessage(content="Our values guide how we behave and make decisions"),
                AIMessage(content="Values are crucial for organizational culture...")
            ])
            
            state["conversation_history"] = messages
            
            stage = agent._determine_why_stage(state)
            assert stage == "synthesis"
    
    def test_extract_conversation_context(self):
        """Test conversation context extraction."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Hello, I need help with strategy"),
                AIMessage(content="I'm here to help you discover your WHY"),
                HumanMessage(content="What is our organizational purpose?")
            ]
            state["conversation_history"] = messages
            
            context = agent._extract_conversation_context(state)
            
            assert "User: Hello, I need help with strategy" in context
            assert "AI: I'm here to help you discover your WHY" in context
            assert "User: What is our organizational purpose?" in context
    
    def test_extract_conversation_context_long_history(self):
        """Test conversation context extraction with long history."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Create long conversation history
            messages = []
            for i in range(10):
                messages.extend([
                    HumanMessage(content=f"User message {i}"),
                    AIMessage(content=f"AI response {i}")
                ])
            
            state["conversation_history"] = messages
            
            context = agent._extract_conversation_context(state)
            
            # Should only include last 8 messages
            assert "User message 6" in context
            assert "AI response 9" in context
            assert "User message 0" not in context
    
    def test_extract_discovered_purpose(self):
        """Test extraction of discovered purpose from conversation."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What's our purpose?"),
                AIMessage(content="Your core purpose is to empower individuals to reach their potential through innovative solutions."),
                HumanMessage(content="That sounds right")
            ]
            state["conversation_history"] = messages
            
            purpose = agent._extract_discovered_purpose(state)
            
            assert "purpose" in purpose.lower()
            assert "empower" in purpose.lower()
    
    def test_extract_discovered_beliefs(self):
        """Test extraction of discovered beliefs from conversation."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What do we believe?"),
                AIMessage(content="You believe that every person has untapped potential and deserves support to succeed."),
                HumanMessage(content="Exactly")
            ]
            state["conversation_history"] = messages
            
            beliefs = agent._extract_discovered_beliefs(state)
            
            assert "believe" in beliefs.lower()
            assert "potential" in beliefs.lower()
    
    def test_extract_discovered_values(self):
        """Test extraction of discovered values from conversation."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What are our values?"),
                AIMessage(content="Your values include integrity, empowerment, and continuous learning - guiding how you behave."),
                HumanMessage(content="Those are perfect")
            ]
            state["conversation_history"] = messages
            
            values = agent._extract_discovered_values(state)
            
            assert "values" in values.lower()
            assert "behavior" in values.lower() or "behave" in values.lower()
    
    def test_format_company_context(self):
        """Test formatting of company context."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            user_context = {
                "company_name": "TechStart Inc",
                "industry": "software",
                "team_size": "10-20",
                "revenue_stage": "early-revenue"
            }
            
            formatted = agent._format_company_context(user_context)
            
            assert "Company: TechStart Inc" in formatted
            assert "Industry: software" in formatted
            assert "Team size: 10-20" in formatted
            assert "Stage: early-revenue" in formatted
    
    def test_format_company_context_empty(self):
        """Test formatting of empty company context."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            formatted = agent._format_company_context({})
            assert formatted == "No company context provided"
    
    def test_update_state_with_insights_synthesis(self):
        """Test state updates during synthesis stage."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Your WHY framework is complete..."
            
            updated_state = agent._update_state_with_insights(state, "synthesis", response)
            
            # Should mark WHY as complete during synthesis
            assert updated_state["strategy_completeness"]["why"] is True
            assert len(updated_state["identified_gaps"]) > 0
    
    def test_update_state_with_insights_other_stages(self):
        """Test state updates during non-synthesis stages."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Let's explore your purpose..."
            
            updated_state = agent._update_state_with_insights(state, "purpose_discovery", response)
            
            # Should not mark WHY as complete for non-synthesis stages
            assert updated_state["strategy_completeness"]["why"] is False
            assert len(updated_state["identified_gaps"]) > 0


class TestWhyAgentProcessing:
    """Test WHY Agent processing functionality."""
    
    @patch('src.agents.why_agent.get_llm_client')
    def test_process_user_input_purpose_discovery(self, mock_llm_client):
        """Test processing user input during purpose discovery."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's explore your organization's core purpose. Why does your organization exist?"
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = WhyAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "I need help understanding our organizational purpose"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Verify response was added to conversation
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        
        # Verify processing metadata
        assert result["processing_stage"] == "why_agent_completed"
        assert result["current_agent"] == "why_agent"
        assert result["agent_output"] is not None
    
    @patch('src.agents.why_agent.get_llm_client')
    def test_process_user_input_belief_exploration(self, mock_llm_client):
        """Test processing user input during belief exploration."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Now let's explore your core beliefs. What do you believe about your industry?"
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = WhyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for belief exploration stage
        messages = [
            HumanMessage(content="Our purpose is to help people succeed"),
            AIMessage(content="That's a meaningful purpose...")
        ]
        state["conversation_history"] = messages
        
        user_input = "We believe everyone has potential"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify processing completed successfully
        assert result["processing_stage"] == "why_agent_completed"
        assert len(result["conversation_history"]) == 3  # Original 2 + new AI response
    
    @patch('src.agents.why_agent.get_llm_client')
    def test_process_user_input_synthesis_stage(self, mock_llm_client):
        """Test processing user input during synthesis stage."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "**YOUR WHY STATEMENT:** You exist to empower people to reach their potential."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = WhyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for synthesis stage (comprehensive conversation)
        messages = []
        for i in range(8):
            messages.extend([
                HumanMessage(content=f"Purpose/belief/values discussion {i}"),
                AIMessage(content=f"Great insight about your purpose/beliefs/values...")
            ])
        
        state["conversation_history"] = messages
        
        user_input = "I think we've covered everything"
        
        result = agent.process_user_input(state, user_input)
        
        # Should mark WHY as complete during synthesis
        assert result["strategy_completeness"]["why"] is True
        assert "WHY framework completed" in str(result["identified_gaps"])
    
    @patch('src.agents.why_agent.get_llm_client')
    def test_process_user_input_llm_error(self, mock_llm_client):
        """Test handling of LLM errors during processing."""
        # Mock LLM to raise an error
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")
        mock_llm_client.return_value = mock_llm
        
        agent = WhyAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "What is our purpose?"
        
        result = agent.process_user_input(state, user_input)
        
        # Should handle error gracefully
        assert "error_state" in result
        assert result["error_state"]["error_type"] == "Exception"
        
        # Should still provide fallback response
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        assert "purpose" in result["conversation_history"][0].content.lower()
    
    def test_fallback_responses(self):
        """Test fallback responses for different scenarios."""
        with patch('src.agents.why_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = WhyAgent()
            
            # Test general fallback
            fallback = agent._get_fallback_response()
            assert "purpose" in fallback.lower()
            assert "golden circle" in fallback.lower()
            
            # Test purpose fallback
            purpose_fallback = agent._get_fallback_purpose_response()
            assert "purpose" in purpose_fallback.lower()
            
            # Test belief fallback
            belief_fallback = agent._get_fallback_belief_response()
            assert "belief" in belief_fallback.lower()
            
            # Test values fallback
            values_fallback = agent._get_fallback_values_response()
            assert "values" in values_fallback.lower()
            
            # Test synthesis fallback
            synthesis_fallback = agent._get_fallback_synthesis_response("test purpose", "test beliefs", "test values")
            assert "WHY FRAMEWORK" in synthesis_fallback
            assert "test purpose" in synthesis_fallback


class TestWhyAgentNodeCreation:
    """Test WHY Agent node creation for orchestrator."""
    
    @patch('src.agents.why_agent.get_llm_client')
    def test_create_why_agent_node(self, mock_llm_client):
        """Test creation of WHY Agent node function."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's explore your purpose..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_why_agent_node()
        
        # Test the node function
        state = initialize_agent_state("test_session", "test_path")
        user_message = HumanMessage(content="What is our purpose?")
        state["conversation_history"] = [user_message]
        
        result = node_function(state)
        
        # Should process the user input successfully
        assert result is not None
        assert len(result["conversation_history"]) >= 1
    
    @patch('src.agents.why_agent.get_llm_client')
    def test_why_agent_node_with_empty_conversation(self, mock_llm_client):
        """Test WHY Agent node with empty conversation history."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "I'm here to help discover your WHY..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_why_agent_node()
        state = initialize_agent_state("test_session", "test_path")
        # Leave conversation history empty
        
        result = node_function(state)
        
        # Should handle empty conversation gracefully
        assert result is not None
        assert len(result["conversation_history"]) >= 1


@pytest.mark.integration
class TestWhyAgentIntegration:
    """Integration tests for WHY Agent."""
    
    @patch('src.agents.why_agent.get_llm_client')
    def test_complete_why_discovery_flow(self, mock_llm_client):
        """Test complete WHY discovery flow through all stages."""
        # Mock different LLM responses for different stages
        mock_llm = MagicMock()
        mock_responses = [
            MagicMock(content="Let's explore your core purpose..."),
            MagicMock(content="Now let's examine your core beliefs..."),
            MagicMock(content="Let's define your values..."),
            MagicMock(content="**YOUR WHY STATEMENT:** Complete WHY framework...")
        ]
        mock_llm.invoke.side_effect = mock_responses
        mock_llm_client.return_value = mock_llm
        
        agent = WhyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Stage 1: Purpose Discovery
        state = agent.process_user_input(state, "What is our purpose?")
        assert len(state["conversation_history"]) == 1
        assert state["strategy_completeness"]["why"] is False
        
        # Stage 2: Belief Exploration (simulate conversation progression)
        state["conversation_history"].extend([
            HumanMessage(content="Our purpose is to empower people"),
            AIMessage(content="Great purpose discovery...")
        ])
        
        state = agent.process_user_input(state, "We believe in human potential")
        assert len(state["conversation_history"]) == 4
        
        # Stage 3: Values Integration (simulate more conversation)
        state["conversation_history"].extend([
            HumanMessage(content="We believe everyone deserves support"),
            AIMessage(content="Strong beliefs...")
        ])
        
        state = agent.process_user_input(state, "Our values are integrity and growth")
        assert len(state["conversation_history"]) == 7
        
        # Stage 4: Synthesis (simulate comprehensive conversation for synthesis trigger)
        for i in range(4):
            state["conversation_history"].extend([
                HumanMessage(content=f"Additional purpose/belief/values content {i}"),
                AIMessage(content=f"Understanding your WHY better...")
            ])
        
        state = agent.process_user_input(state, "I think we have everything")
        
        # Should complete WHY phase
        assert state["strategy_completeness"]["why"] is True
        assert "WHY framework completed" in str(state["identified_gaps"])
        
        # Verify all LLM calls were made
        assert mock_llm.invoke.call_count == 4