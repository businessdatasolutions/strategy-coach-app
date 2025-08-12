import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.analogy_agent import AnalogyAgent, create_analogy_agent_node
from src.models.state import initialize_agent_state
from src.utils.llm_client import LLMClientError


class TestAnalogyAgent:
    """Test the Analogy Agent functionality."""
    
    def test_analogy_agent_initialization(self):
        """Test that Analogy Agent initializes successfully."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            
            agent = AnalogyAgent()
            
            assert agent.methodology == "Carroll & Sørensen's Analogical Reasoning Framework"
            assert agent.focus_areas == ["source_identification", "structural_mapping", "evaluation_adaptation", "strategic_integration"]
            assert hasattr(agent, 'source_identification_prompt')
            assert hasattr(agent, 'structural_mapping_prompt')
            assert hasattr(agent, 'evaluation_adaptation_prompt')
            assert hasattr(agent, 'strategic_integration_prompt')
    
    def test_determine_analogy_stage_initial(self):
        """Test stage determination for initial conversation."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Should start with source identification
            stage = agent._determine_analogy_stage(state)
            assert stage == "source_identification"
    
    def test_determine_analogy_stage_source_identification(self):
        """Test stage determination during source identification."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with source identification indicators
            messages = [
                HumanMessage(content="We want to be like Apple in terms of innovation"),
                AIMessage(content="Apple is an interesting analogy for innovation strategy..."),
                HumanMessage(content="What other companies have similar approaches?"),
                AIMessage(content="Let's explore industries that might offer insights...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_analogy_stage(state)
            assert stage == "structural_mapping"
    
    def test_determine_analogy_stage_structural_mapping(self):
        """Test stage determination during structural mapping."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with source and mapping indicators
            messages = [
                HumanMessage(content="We want to be like Tesla"),
                AIMessage(content="Tesla provides an interesting analogy..."),
                HumanMessage(content="How do their innovation patterns map to our situation?"),
                AIMessage(content="Let's examine the structural relationships and patterns..."),
                HumanMessage(content="What are the key mechanisms that drive their success?"),
                AIMessage(content="The mapping shows several important structural relationships...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_analogy_stage(state)
            assert stage == "evaluation_adaptation"
    
    def test_determine_analogy_stage_integration(self):
        """Test stage determination for strategic integration."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add comprehensive conversation
            messages = []
            # Add source identification
            for i in range(2):
                messages.extend([
                    HumanMessage(content=f"Source {i}: Companies like Netflix and Amazon"),
                    AIMessage(content=f"Great analogy examples from different industries...")
                ])
            
            # Add structural mapping
            for i in range(2):
                messages.extend([
                    HumanMessage(content=f"Mapping {i}: How do their patterns relate to us?"),
                    AIMessage(content=f"The structural relationships show interesting patterns...")
                ])
            
            # Add evaluation and integration discussion
            messages.extend([
                HumanMessage(content="Let's evaluate these insights and integrate them"),
                AIMessage(content="Now let's create a strategic framework based on these analogical insights...")
            ])
            
            state["conversation_history"] = messages
            
            stage = agent._determine_analogy_stage(state)
            assert stage == "strategic_integration"
    
    def test_extract_conversation_context(self):
        """Test conversation context extraction."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="We need strategic insights"),
                AIMessage(content="Let's explore analogical reasoning"),
                HumanMessage(content="What companies should we look at?")
            ]
            state["conversation_history"] = messages
            
            context = agent._extract_conversation_context(state)
            
            assert "User: We need strategic insights" in context
            assert "AI: Let's explore analogical reasoning" in context
            assert "User: What companies should we look at?" in context
    
    def test_extract_purpose_context_from_conversation(self):
        """Test extraction of purpose context from conversation."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Our purpose is innovation"),
                AIMessage(content="Your core purpose is to drive innovation and create breakthrough solutions for customers."),
                HumanMessage(content="That's exactly right")
            ]
            state["conversation_history"] = messages
            
            purpose_context = agent._extract_purpose_context(state)
            
            assert "purpose" in purpose_context.lower()
            assert "innovation" in purpose_context.lower()
    
    def test_extract_purpose_context_from_state(self):
        """Test extraction of purpose context from state completeness."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["strategy_completeness"]["why"] = True
            
            purpose_context = agent._extract_purpose_context(state)
            
            assert "clarified core purpose" in purpose_context.lower()
    
    def test_extract_identified_sources(self):
        """Test extraction of identified source domains."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What companies should we analyze?"),
                AIMessage(content="Let's look at Tesla, Apple, and Netflix as analogical examples from different industries."),
                HumanMessage(content="Those sound good")
            ]
            state["conversation_history"] = messages
            
            sources = agent._extract_identified_sources(state)
            
            assert "Tesla" in sources or "Apple" in sources or "Netflix" in sources
    
    def test_extract_mapped_analogies(self):
        """Test extraction of mapped analogies from conversation."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="How do their structures map to ours?"),
                AIMessage(content="The structural mapping shows that Tesla's innovation pattern corresponds to your R&D process."),
                HumanMessage(content="I see the relationship")
            ]
            state["conversation_history"] = messages
            
            mapped = agent._extract_mapped_analogies(state)
            
            assert "mapping" in mapped.lower()
            assert "structure" in mapped.lower() or "pattern" in mapped.lower()
    
    def test_extract_analogical_insights(self):
        """Test extraction of analogical insights from conversation."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What insights have we gained?"),
                AIMessage(content="The key strategic insight from this analogical analysis is customer-centric innovation."),
                HumanMessage(content="That's valuable")
            ]
            state["conversation_history"] = messages
            
            insights = agent._extract_analogical_insights(state)
            
            assert "insight" in insights.lower()
            assert "strategic" in insights.lower()
    
    def test_format_target_context(self):
        """Test formatting of target context."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            purpose_context = "To innovate for customers"
            user_context = {
                "company_name": "TechStart",
                "industry": "software",
                "team_size": "20-50"
            }
            
            formatted = agent._format_target_context(purpose_context, user_context)
            
            assert "Purpose: To innovate for customers" in formatted
            assert "Organization: TechStart" in formatted
            assert "Industry: software" in formatted
    
    def test_format_strategic_context(self):
        """Test formatting of strategic context."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["current_phase"] = "how"
            state["strategy_completeness"]["why"] = True
            state["user_context"] = {"industry": "tech"}
            
            formatted = agent._format_strategic_context(state)
            
            assert "Current Phase: how" in formatted
            assert "Completed: why" in formatted
            assert "Context:" in formatted
    
    def test_format_company_context(self):
        """Test formatting of company context."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            user_context = {
                "company_name": "InnovateCorp",
                "industry": "fintech",
                "team_size": "10-20",
                "revenue_stage": "growth"
            }
            
            formatted = agent._format_company_context(user_context)
            
            assert "Company: InnovateCorp" in formatted
            assert "Industry: fintech" in formatted
            assert "Team size: 10-20" in formatted
            assert "Stage: growth" in formatted
    
    def test_format_company_context_empty(self):
        """Test formatting of empty company context."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            formatted = agent._format_company_context({})
            assert formatted == "No company context provided"
    
    def test_update_state_with_insights_integration(self):
        """Test state updates during strategic integration stage."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Strategic integration complete with analogical insights..."
            
            updated_state = agent._update_state_with_insights(state, "strategic_integration", response)
            
            # Should mark analogy analysis as complete during integration
            assert updated_state["strategy_completeness"]["analogy_analysis"] is True
            assert len(updated_state["identified_gaps"]) > 0
    
    def test_update_state_with_insights_other_stages(self):
        """Test state updates during non-integration stages."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Source domain identification in progress..."
            
            updated_state = agent._update_state_with_insights(state, "source_identification", response)
            
            # Should not mark analogy analysis as complete for non-integration stages
            assert updated_state["strategy_completeness"]["analogy_analysis"] is False
            assert len(updated_state["identified_gaps"]) > 0


class TestAnalogyAgentProcessing:
    """Test Analogy Agent processing functionality."""
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_process_user_input_source_identification(self, mock_llm_client):
        """Test processing user input during source identification."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's explore companies like Tesla and Apple that might offer strategic insights."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = AnalogyAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "I want to learn from successful companies"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Verify response was added to conversation
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        
        # Verify processing metadata
        assert result["processing_stage"] == "analogy_agent_completed"
        assert result["current_agent"] == "analogy_agent"
        assert result["agent_output"] is not None
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_process_user_input_structural_mapping(self, mock_llm_client):
        """Test processing user input during structural mapping."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Now let's map how Tesla's innovation patterns relate to your strategic situation."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = AnalogyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for structural mapping stage
        messages = [
            HumanMessage(content="We should look at Tesla and Apple"),
            AIMessage(content="Great examples from different industries...")
        ]
        state["conversation_history"] = messages
        
        user_input = "How do their approaches map to our situation?"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify processing completed successfully
        assert result["processing_stage"] == "analogy_agent_completed"
        assert len(result["conversation_history"]) == 3  # Original 2 + new AI response
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_process_user_input_integration_stage(self, mock_llm_client):
        """Test processing user input during strategic integration."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "**ANALOGICAL STRATEGIC FRAMEWORK:** Your strategy should focus on customer-centric innovation."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = AnalogyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for strategic integration stage (comprehensive conversation)
        messages = []
        for i in range(8):
            messages.extend([
                HumanMessage(content=f"Analogical discussion {i}: mapping insights"),
                AIMessage(content=f"Strategic insights from analogical analysis...")
            ])
        
        state["conversation_history"] = messages
        
        user_input = "Let's integrate these insights into strategy"
        
        result = agent.process_user_input(state, user_input)
        
        # Should mark analogy analysis as complete during integration
        assert result["strategy_completeness"]["analogy_analysis"] is True
        assert "Analogical reasoning completed" in str(result["identified_gaps"])
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_process_user_input_llm_error(self, mock_llm_client):
        """Test handling of LLM errors during processing."""
        # Mock LLM to raise an error
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")
        mock_llm_client.return_value = mock_llm
        
        agent = AnalogyAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "What analogies should we explore?"
        
        result = agent.process_user_input(state, user_input)
        
        # Should handle error gracefully
        assert "error_state" in result
        assert result["error_state"]["error_type"] == "Exception"
        
        # Should still provide fallback response
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        assert "analogical reasoning" in result["conversation_history"][0].content.lower()
    
    def test_fallback_responses(self):
        """Test fallback responses for different scenarios."""
        with patch('src.agents.analogy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = AnalogyAgent()
            
            # Test general fallback
            fallback = agent._get_fallback_response()
            assert "analogical reasoning" in fallback.lower()
            assert "carroll" in fallback.lower()
            
            # Test source fallback
            source_fallback = agent._get_fallback_source_response()
            assert "source domains" in source_fallback.lower()
            
            # Test mapping fallback
            mapping_fallback = agent._get_fallback_mapping_response()
            assert "mapping" in mapping_fallback.lower()
            assert "relationship" in mapping_fallback.lower()
            
            # Test evaluation fallback
            evaluation_fallback = agent._get_fallback_evaluation_response()
            assert "evaluate" in evaluation_fallback.lower()
            assert "insight" in evaluation_fallback.lower()
            
            # Test integration fallback
            integration_fallback = agent._get_fallback_integration_response()
            assert "integrate" in integration_fallback.lower()
            assert "strategic" in integration_fallback.lower()


class TestAnalogyAgentNodeCreation:
    """Test Analogy Agent node creation for orchestrator."""
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_create_analogy_agent_node(self, mock_llm_client):
        """Test creation of Analogy Agent node function."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's explore analogical insights..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_analogy_agent_node()
        
        # Test the node function
        state = initialize_agent_state("test_session", "test_path")
        user_message = HumanMessage(content="What companies should we learn from?")
        state["conversation_history"] = [user_message]
        
        result = node_function(state)
        
        # Should process the user input successfully
        assert result is not None
        assert len(result["conversation_history"]) >= 1
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_analogy_agent_node_with_empty_conversation(self, mock_llm_client):
        """Test Analogy Agent node with empty conversation history."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "I'm here to help with analogical reasoning..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_analogy_agent_node()
        state = initialize_agent_state("test_session", "test_path")
        # Leave conversation history empty
        
        result = node_function(state)
        
        # Should handle empty conversation gracefully
        assert result is not None
        assert len(result["conversation_history"]) >= 1


@pytest.mark.integration
class TestAnalogyAgentIntegration:
    """Integration tests for Analogy Agent."""
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_complete_analogical_reasoning_flow(self, mock_llm_client):
        """Test complete analogical reasoning flow through all stages."""
        # Mock different LLM responses for different stages
        mock_llm = MagicMock()
        mock_responses = [
            MagicMock(content="Let's explore Tesla and Apple as source domains..."),
            MagicMock(content="Now let's map their innovation structures to your context..."),
            MagicMock(content="Let's evaluate these analogical insights..."),
            MagicMock(content="**ANALOGICAL STRATEGIC FRAMEWORK:** Complete integration...")
        ]
        mock_llm.invoke.side_effect = mock_responses
        mock_llm_client.return_value = mock_llm
        
        agent = AnalogyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Stage 1: Source Identification
        state = agent.process_user_input(state, "What companies should we learn from?")
        assert len(state["conversation_history"]) == 1
        assert state["strategy_completeness"]["analogy_analysis"] is False
        
        # Stage 2: Structural Mapping (simulate conversation progression)
        state["conversation_history"].extend([
            HumanMessage(content="Let's look at Tesla and Netflix"),
            AIMessage(content="Great analogical sources...")
        ])
        
        state = agent.process_user_input(state, "How do their patterns map to us?")
        assert len(state["conversation_history"]) == 4
        
        # Stage 3: Evaluation & Adaptation (simulate more conversation)
        state["conversation_history"].extend([
            HumanMessage(content="The structural mapping is interesting"),
            AIMessage(content="Key relationships identified...")
        ])
        
        state = agent.process_user_input(state, "Let's evaluate these insights")
        assert len(state["conversation_history"]) == 7
        
        # Stage 4: Strategic Integration (simulate comprehensive conversation for integration trigger)
        for i in range(4):
            state["conversation_history"].extend([
                HumanMessage(content=f"Additional analogical content {i}"),
                AIMessage(content=f"Developing strategic insights...")
            ])
        
        state = agent.process_user_input(state, "Let's integrate this into strategy")
        
        # Should complete analogy analysis phase
        assert state["strategy_completeness"]["analogy_analysis"] is True
        assert "Analogical reasoning completed" in str(state["identified_gaps"])
        
        # Verify all LLM calls were made
        assert mock_llm.invoke.call_count == 4
    
    @patch('src.agents.analogy_agent.get_llm_client')
    def test_analogy_agent_with_why_context(self, mock_llm_client):
        """Test Analogy Agent when WHY phase is already completed."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Given your purpose, let's explore relevant analogies..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = AnalogyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set WHY as completed with purpose context
        state["strategy_completeness"]["why"] = True
        state["conversation_history"] = [
            AIMessage(content="Your core purpose is to innovate for customer success")
        ]
        
        result = agent.process_user_input(state, "Now let's find strategic analogies")
        
        # Should extract purpose context properly
        purpose_context = agent._extract_purpose_context(state)
        assert "innovate" in purpose_context.lower() or "clarified core purpose" in purpose_context.lower()
        
        # Should process successfully
        assert result["processing_stage"] == "analogy_agent_completed"