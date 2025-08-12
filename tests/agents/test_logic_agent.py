import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.logic_agent import LogicAgent, create_logic_agent_node
from src.models.state import initialize_agent_state
from src.utils.llm_client import LLMClientError


class TestLogicAgent:
    """Test the Logic Agent functionality."""
    
    def test_logic_agent_initialization(self):
        """Test that Logic Agent initializes successfully."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            
            agent = LogicAgent()
            
            assert agent.methodology == "Deductive Argument Validation & Logical Structure Analysis"
            assert agent.focus_areas == ["argument_analysis", "validity_assessment", "soundness_evaluation", "framework_construction"]
            assert hasattr(agent, 'argument_analysis_prompt')
            assert hasattr(agent, 'validity_assessment_prompt')
            assert hasattr(agent, 'soundness_evaluation_prompt')
            assert hasattr(agent, 'framework_construction_prompt')
    
    def test_determine_logic_stage_initial(self):
        """Test stage determination for initial conversation."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Should start with argument analysis
            stage = agent._determine_logic_stage(state)
            assert stage == "argument_analysis"
    
    def test_determine_logic_stage_argument_analysis(self):
        """Test stage determination during argument analysis."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with argument analysis indicators
            messages = [
                HumanMessage(content="What are the logical premises of our strategy?"),
                AIMessage(content="Let's analyze the argument structure and key assumptions..."),
                HumanMessage(content="Are our reasoning patterns sound?"),
                AIMessage(content="Let's examine the logical connections and conclusions...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_logic_stage(state)
            assert stage == "validity_assessment"
    
    def test_determine_logic_stage_validity_assessment(self):
        """Test stage determination during validity assessment."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with argument and validity indicators
            messages = [
                HumanMessage(content="Our strategic reasoning is based on these assumptions"),
                AIMessage(content="Let's examine the logical structure of these arguments..."),
                HumanMessage(content="Do these conclusions follow logically?"),
                AIMessage(content="The validity of these inferences needs assessment..."),
                HumanMessage(content="Are our arguments internally consistent?"),
                AIMessage(content="Let's check for logical consistency and validity...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_logic_stage(state)
            assert stage == "soundness_evaluation"
    
    def test_determine_logic_stage_framework_construction(self):
        """Test stage determination for framework construction."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add comprehensive conversation
            messages = []
            # Add argument analysis
            for i in range(2):
                messages.extend([
                    HumanMessage(content=f"Argument {i}: Our premises and assumptions are..."),
                    AIMessage(content=f"The logical structure shows...")
                ])
            
            # Add validity discussion
            for i in range(2):
                messages.extend([
                    HumanMessage(content=f"Validity {i}: Do these conclusions follow logically?"),
                    AIMessage(content=f"The logical validity assessment shows...")
                ])
            
            # Add soundness and framework discussion
            messages.extend([
                HumanMessage(content="Are our premises well-supported by evidence?"),
                AIMessage(content="The soundness evaluation shows strong evidence support..."),
                HumanMessage(content="Let's create a logical framework"),
                AIMessage(content="Now we can integrate this into a coherent logical framework...")
            ])
            
            state["conversation_history"] = messages
            
            stage = agent._determine_logic_stage(state)
            assert stage == "framework_construction"
    
    def test_extract_conversation_context(self):
        """Test conversation context extraction."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="We need to validate our strategic logic"),
                AIMessage(content="Let's examine the logical foundations"),
                HumanMessage(content="What are our key assumptions?")
            ]
            state["conversation_history"] = messages
            
            context = agent._extract_conversation_context(state)
            
            assert "User: We need to validate our strategic logic" in context
            assert "AI: Let's examine the logical foundations" in context
            assert "User: What are our key assumptions?" in context
    
    def test_extract_strategic_content_from_conversation(self):
        """Test extraction of strategic content from conversation."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Our strategic approach is innovation-focused"),
                AIMessage(content="Your core purpose is to drive strategic innovation for customer success through analogical insights."),
                HumanMessage(content="That captures our strategy well")
            ]
            state["conversation_history"] = messages
            
            strategic_content = agent._extract_strategic_content(state)
            
            assert "strategic" in strategic_content.lower()
            assert "innovation" in strategic_content.lower()
    
    def test_extract_strategic_content_from_state(self):
        """Test extraction of strategic content from completed state elements."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["strategy_completeness"]["why"] = True
            state["strategy_completeness"]["analogy_analysis"] = True
            
            strategic_content = agent._extract_strategic_content(state)
            
            assert "Core purpose and WHY established" in strategic_content
            assert "Analogical reasoning and insights developed" in strategic_content
    
    def test_format_context_info(self):
        """Test formatting of context information."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["current_phase"] = "how"
            state["strategy_completeness"]["why"] = True
            state["user_context"] = {
                "company_name": "LogicCorp",
                "industry": "consulting",
                "team_size": "20-50"
            }
            
            context_info = agent._format_context_info(state)
            
            assert "Current Phase: how" in context_info
            assert "Completed Elements: why" in context_info
            assert "Company_Name: LogicCorp" in context_info
    
    def test_extract_argument_structure(self):
        """Test extraction of identified argument structure."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What's our logical structure?"),
                AIMessage(content="The argument structure shows clear premises leading to strategic conclusions through valid inference patterns."),
                HumanMessage(content="Good analysis")
            ]
            state["conversation_history"] = messages
            
            structure = agent._extract_argument_structure(state)
            
            assert "argument structure" in structure.lower()
            assert "premise" in structure.lower()
    
    def test_extract_validity_results(self):
        """Test extraction of validity assessment results."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Are our arguments valid?"),
                AIMessage(content="The validity assessment shows that your conclusions follow logically from the premises with strong inferential quality."),
                HumanMessage(content="Excellent")
            ]
            state["conversation_history"] = messages
            
            validity = agent._extract_validity_results(state)
            
            assert "validity" in validity.lower()
            assert "logical" in validity.lower()
    
    def test_extract_premise_analysis(self):
        """Test extraction of premise analysis from conversation."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What are our foundational premises?"),
                AIMessage(content="The core premises include assumptions about market dynamics and customer behavior that form the foundation of your strategy."),
                HumanMessage(content="That's our foundation")
            ]
            state["conversation_history"] = messages
            
            premise_analysis = agent._extract_premise_analysis(state)
            
            assert "premise" in premise_analysis.lower()
            assert "foundation" in premise_analysis.lower()
    
    def test_extract_soundness_results(self):
        """Test extraction of soundness evaluation results."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Are our premises well-supported?"),
                AIMessage(content="The soundness evaluation shows strong evidence supporting key premises with factual accuracy."),
                HumanMessage(content="Good to know")
            ]
            state["conversation_history"] = messages
            
            soundness = agent._extract_soundness_results(state)
            
            assert "soundness" in soundness.lower()
            assert "evidence" in soundness.lower()
    
    def test_extract_argument_analysis(self):
        """Test extraction of argument analysis from conversation."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Let's analyze our arguments"),
                AIMessage(content="The argument analysis reveals clear logical structure with identifiable reasoning patterns."),
                HumanMessage(content="Helpful analysis")
            ]
            state["conversation_history"] = messages
            
            analysis = agent._extract_argument_analysis(state)
            
            assert "argument" in analysis.lower()
            assert "analysis" in analysis.lower()
    
    def test_format_strategic_context(self):
        """Test formatting of strategic context."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["current_phase"] = "how"
            state["strategy_completeness"]["why"] = True
            state["strategy_completeness"]["analogy_analysis"] = True
            state["user_context"] = {"industry": "technology"}
            
            context = agent._format_strategic_context(state)
            
            assert "Strategic Phase: how" in context
            assert "Completed Strategy Elements: why, analogy_analysis" in context
            assert "Industry Context: technology" in context
    
    def test_update_state_with_insights_framework_construction(self):
        """Test state updates during framework construction stage."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Logical framework construction complete with validated reasoning structure..."
            
            updated_state = agent._update_state_with_insights(state, "framework_construction", response)
            
            # Should mark logical structure as complete during framework construction
            assert updated_state["strategy_completeness"]["logical_structure"] is True
            assert len(updated_state["identified_gaps"]) > 0
    
    def test_update_state_with_insights_other_stages(self):
        """Test state updates during non-framework-construction stages."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Argument analysis in progress..."
            
            updated_state = agent._update_state_with_insights(state, "argument_analysis", response)
            
            # Should not mark logical structure as complete for non-framework stages
            assert updated_state["strategy_completeness"]["logical_structure"] is False
            assert len(updated_state["identified_gaps"]) > 0


class TestLogicAgentProcessing:
    """Test Logic Agent processing functionality."""
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_process_user_input_argument_analysis(self, mock_llm_client):
        """Test processing user input during argument analysis."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's examine the logical structure of your strategic premises and conclusions."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "I want to validate the logic of our strategic approach"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Verify response was added to conversation
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        
        # Verify processing metadata
        assert result["processing_stage"] == "logic_agent_completed"
        assert result["current_agent"] == "logic_agent"
        assert result["agent_output"] is not None
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_process_user_input_validity_assessment(self, mock_llm_client):
        """Test processing user input during validity assessment."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Now let's assess whether your conclusions follow logically from your premises."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for validity assessment stage
        messages = [
            HumanMessage(content="Our assumptions are based on market research"),
            AIMessage(content="Let's analyze the argument structure of these assumptions...")
        ]
        state["conversation_history"] = messages
        
        user_input = "Do our strategic conclusions follow logically?"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify processing completed successfully
        assert result["processing_stage"] == "logic_agent_completed"
        assert len(result["conversation_history"]) == 3  # Original 2 + new AI response
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_process_user_input_framework_construction_stage(self, mock_llm_client):
        """Test processing user input during framework construction."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "**STRATEGIC LOGIC FRAMEWORK:** Your validated reasoning structure provides solid foundation for strategic decisions."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for framework construction stage (comprehensive conversation)
        messages = []
        for i in range(8):
            messages.extend([
                HumanMessage(content=f"Logical discussion {i}: premises and validity"),
                AIMessage(content=f"Logical analysis shows strong reasoning structure...")
            ])
        
        state["conversation_history"] = messages
        
        user_input = "Let's create our logical framework"
        
        result = agent.process_user_input(state, user_input)
        
        # Should mark logical structure as complete during framework construction
        assert result["strategy_completeness"]["logical_structure"] is True
        assert "Logical framework completed" in str(result["identified_gaps"])
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_process_user_input_with_strategic_context(self, mock_llm_client):
        """Test processing with existing strategic context."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Given your strategic development, let's validate the logical foundations."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up strategic context
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        state["conversation_history"] = [
            AIMessage(content="Your strategic approach focuses on innovation and customer success")
        ]
        
        result = agent.process_user_input(state, "Let's validate this strategy logically")
        
        # Should extract strategic content properly
        strategic_content = agent._extract_strategic_content(state)
        assert "innovation" in strategic_content.lower() or "established" in strategic_content.lower()
        
        # Should process successfully
        assert result["processing_stage"] == "logic_agent_completed"
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_process_user_input_llm_error(self, mock_llm_client):
        """Test handling of LLM errors during processing."""
        # Mock LLM to raise an error
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "Let's analyze our strategic logic"
        
        result = agent.process_user_input(state, user_input)
        
        # Should handle error gracefully
        assert "error_state" in result
        assert result["error_state"]["error_type"] == "Exception"
        
        # Should still provide fallback response
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        assert "logical" in result["conversation_history"][0].content.lower()
    
    def test_fallback_responses(self):
        """Test fallback responses for different scenarios."""
        with patch('src.agents.logic_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = LogicAgent()
            
            # Test general fallback
            fallback = agent._get_fallback_response()
            assert "logical structure" in fallback.lower()
            assert "strategic reasoning" in fallback.lower()
            
            # Test argument fallback
            argument_fallback = agent._get_fallback_argument_response()
            assert "argument" in argument_fallback.lower()
            assert "premise" in argument_fallback.lower()
            
            # Test validity fallback
            validity_fallback = agent._get_fallback_validity_response()
            assert "validity" in validity_fallback.lower()
            assert "logical" in validity_fallback.lower()
            
            # Test soundness fallback
            soundness_fallback = agent._get_fallback_soundness_response()
            assert "soundness" in soundness_fallback.lower()
            assert "evidence" in soundness_fallback.lower()
            
            # Test framework fallback
            framework_fallback = agent._get_fallback_framework_response()
            assert "framework" in framework_fallback.lower()
            assert "logical" in framework_fallback.lower()


class TestLogicAgentNodeCreation:
    """Test Logic Agent node creation for orchestrator."""
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_create_logic_agent_node(self, mock_llm_client):
        """Test creation of Logic Agent node function."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's analyze your strategic logic..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_logic_agent_node()
        
        # Test the node function
        state = initialize_agent_state("test_session", "test_path")
        user_message = HumanMessage(content="Are our strategic arguments sound?")
        state["conversation_history"] = [user_message]
        
        result = node_function(state)
        
        # Should process the user input successfully
        assert result is not None
        assert len(result["conversation_history"]) >= 1
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_logic_agent_node_with_empty_conversation(self, mock_llm_client):
        """Test Logic Agent node with empty conversation history."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "I'm here to help validate your strategic reasoning..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_logic_agent_node()
        state = initialize_agent_state("test_session", "test_path")
        # Leave conversation history empty
        
        result = node_function(state)
        
        # Should handle empty conversation gracefully
        assert result is not None
        assert len(result["conversation_history"]) >= 1


@pytest.mark.integration
class TestLogicAgentIntegration:
    """Integration tests for Logic Agent."""
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_complete_logical_analysis_flow(self, mock_llm_client):
        """Test complete logical analysis flow through all stages."""
        # Mock different LLM responses for different stages
        mock_llm = MagicMock()
        mock_responses = [
            MagicMock(content="Let's analyze the argument structure of your strategic reasoning..."),
            MagicMock(content="Now let's assess the logical validity of these arguments..."),
            MagicMock(content="Let's evaluate the soundness of your premises..."),
            MagicMock(content="**STRATEGIC LOGIC FRAMEWORK:** Complete logical validation...")
        ]
        mock_llm.invoke.side_effect = mock_responses
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Stage 1: Argument Analysis
        state = agent.process_user_input(state, "Let's validate our strategic reasoning")
        assert len(state["conversation_history"]) == 1
        assert state["strategy_completeness"]["logical_structure"] is False
        
        # Stage 2: Validity Assessment (simulate conversation progression)
        state["conversation_history"].extend([
            HumanMessage(content="Our premises are based on market analysis"),
            AIMessage(content="Good foundational assumptions...")
        ])
        
        state = agent.process_user_input(state, "Do these conclusions follow logically?")
        assert len(state["conversation_history"]) == 4
        
        # Stage 3: Soundness Evaluation (simulate more conversation)
        state["conversation_history"].extend([
            HumanMessage(content="The logical validity looks good"),
            AIMessage(content="Now let's examine soundness...")
        ])
        
        state = agent.process_user_input(state, "Are our premises well-supported by evidence?")
        assert len(state["conversation_history"]) == 7
        
        # Stage 4: Framework Construction (simulate comprehensive conversation for framework trigger)
        for i in range(4):
            state["conversation_history"].extend([
                HumanMessage(content=f"Additional logical analysis {i}"),
                AIMessage(content=f"Strengthening logical foundations...")
            ])
        
        state = agent.process_user_input(state, "Let's create our logical framework")
        
        # Should complete logical structure phase
        assert state["strategy_completeness"]["logical_structure"] is True
        assert "Logical framework completed" in str(state["identified_gaps"])
        
        # Verify all LLM calls were made
        assert mock_llm.invoke.call_count == 4
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_logic_agent_with_strategic_context(self, mock_llm_client):
        """Test Logic Agent when WHY and Analogy phases are completed."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Given your strategic development, let's validate the logical foundations..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set WHY and Analogy as completed with strategic context
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        state["conversation_history"] = [
            AIMessage(content="Your purpose is innovation and your analogical insights focus on customer-centric approaches")
        ]
        
        result = agent.process_user_input(state, "Now let's validate our strategic logic")
        
        # Should extract strategic context properly
        strategic_content = agent._extract_strategic_content(state)
        assert "innovation" in strategic_content.lower() or "established" in strategic_content.lower()
        
        # Should process successfully
        assert result["processing_stage"] == "logic_agent_completed"
    
    @patch('src.agents.logic_agent.get_llm_client')
    def test_logic_agent_context_extraction(self, mock_llm_client):
        """Test Logic Agent's context extraction capabilities."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Analyzing logical structure based on your strategic context..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = LogicAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up rich context
        state["current_phase"] = "how"
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        state["user_context"] = {
            "company_name": "Strategic Corp",
            "industry": "consulting",
            "team_size": "50-100"
        }
        
        result = agent.process_user_input(state, "Let's validate our approach")
        
        # Test context extraction methods
        context_info = agent._format_context_info(state)
        assert "Current Phase: how" in context_info
        assert "Completed Elements" in context_info
        assert "Strategic Corp" in context_info
        
        strategic_context = agent._format_strategic_context(state)
        assert "Strategic Phase: how" in strategic_context
        assert "Completed Strategy Elements" in strategic_context
        
        assert result["processing_stage"] == "logic_agent_completed"