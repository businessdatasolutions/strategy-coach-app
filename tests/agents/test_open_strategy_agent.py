import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.open_strategy_agent import OpenStrategyAgent, create_open_strategy_agent_node
from src.models.state import initialize_agent_state
from src.utils.llm_client import LLMClientError


class TestOpenStrategyAgent:
    """Test the Open Strategy Agent functionality."""
    
    def test_open_strategy_agent_initialization(self):
        """Test that Open Strategy Agent initializes successfully."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            
            agent = OpenStrategyAgent()
            
            assert agent.methodology == "Open Strategy Implementation Planning"
            assert agent.focus_areas == ["stakeholder_analysis", "process_design", "resource_planning", "implementation_roadmap"]
            assert hasattr(agent, 'stakeholder_analysis_prompt')
            assert hasattr(agent, 'process_design_prompt')
            assert hasattr(agent, 'resource_planning_prompt')
            assert hasattr(agent, 'implementation_roadmap_prompt')
    
    def test_determine_implementation_stage_initial(self):
        """Test stage determination for initial conversation."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Should start with stakeholder analysis
            stage = agent._determine_implementation_stage(state)
            assert stage == "stakeholder_analysis"
    
    def test_determine_implementation_stage_stakeholder_analysis(self):
        """Test stage determination during stakeholder analysis."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with stakeholder indicators
            messages = [
                HumanMessage(content="Who are our key stakeholders for implementation?"),
                AIMessage(content="Let's identify stakeholders including customers, team members, and partners..."),
                HumanMessage(content="We need to engage our employees and customers"),
                AIMessage(content="Great stakeholder identification. Now let's examine engagement approaches...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_implementation_stage(state)
            assert stage == "process_design"
    
    def test_determine_implementation_stage_process_design(self):
        """Test stage determination during process design."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add conversation with stakeholder and process indicators
            messages = [
                HumanMessage(content="Our stakeholders include employees and customers"),
                AIMessage(content="Good stakeholder analysis. Now let's design implementation processes..."),
                HumanMessage(content="What processes do we need for decision-making?"),
                AIMessage(content="Let's create governance structures and workflows for implementation..."),
                HumanMessage(content="We need clear procedures and workflow design"),
                AIMessage(content="The process design should include decision structures and communication flows...")
            ]
            state["conversation_history"] = messages
            
            stage = agent._determine_implementation_stage(state)
            assert stage == "resource_planning"
    
    def test_determine_implementation_stage_roadmap(self):
        """Test stage determination for implementation roadmap."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            # Add comprehensive conversation
            messages = []
            # Add stakeholder analysis
            for i in range(2):
                messages.extend([
                    HumanMessage(content=f"Stakeholder {i}: employees, customers, partners"),
                    AIMessage(content=f"Good stakeholder engagement planning...")
                ])
            
            # Add process discussion
            for i in range(2):
                messages.extend([
                    HumanMessage(content=f"Process {i}: governance and workflow design"),
                    AIMessage(content=f"Strong process framework development...")
                ])
            
            # Add resource and roadmap discussion
            messages.extend([
                HumanMessage(content="What resources and budget do we need?"),
                AIMessage(content="Resource planning shows budget and capability requirements..."),
                HumanMessage(content="Let's create our implementation timeline and roadmap"),
                AIMessage(content="Now we can build a comprehensive implementation roadmap...")
            ])
            
            state["conversation_history"] = messages
            
            stage = agent._determine_implementation_stage(state)
            assert stage == "implementation_roadmap"
    
    def test_extract_conversation_context(self):
        """Test conversation context extraction."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="We need to plan our implementation"),
                AIMessage(content="Let's start with stakeholder analysis"),
                HumanMessage(content="Who should be involved in execution?")
            ]
            state["conversation_history"] = messages
            
            context = agent._extract_conversation_context(state)
            
            assert "User: We need to plan our implementation" in context
            assert "AI: Let's start with stakeholder analysis" in context
            assert "User: Who should be involved in execution?" in context
    
    def test_extract_strategic_foundation_from_conversation(self):
        """Test extraction of strategic foundation from conversation."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Our strategy focuses on innovation"),
                AIMessage(content="Your strategic framework combines purpose-driven innovation with analogical insights and logical validation for customer success."),
                HumanMessage(content="That's our complete strategic foundation")
            ]
            state["conversation_history"] = messages
            
            strategic_foundation = agent._extract_strategic_foundation(state)
            
            assert "strategic" in strategic_foundation.lower()
            assert "innovation" in strategic_foundation.lower()
    
    def test_extract_strategic_foundation_from_state(self):
        """Test extraction of strategic foundation from completed state elements."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["strategy_completeness"]["why"] = True
            state["strategy_completeness"]["analogy_analysis"] = True
            state["strategy_completeness"]["logical_structure"] = True
            
            strategic_foundation = agent._extract_strategic_foundation(state)
            
            assert "Core purpose and WHY clarified" in strategic_foundation
            assert "Strategic insights from analogical reasoning" in strategic_foundation
            assert "Logical framework and argument validation" in strategic_foundation
    
    def test_format_context_info(self):
        """Test formatting of context information."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["current_phase"] = "what"
            state["strategy_completeness"]["why"] = True
            state["strategy_completeness"]["analogy_analysis"] = True
            state["user_context"] = {
                "company_name": "ImplementCorp",
                "industry": "technology",
                "team_size": "50-100",
                "revenue_stage": "growth"
            }
            
            context_info = agent._format_context_info(state)
            
            assert "Current Phase: what" in context_info
            assert "Completed Strategy Elements: why, analogy_analysis" in context_info
            assert "Company Name: ImplementCorp" in context_info
    
    def test_extract_stakeholder_analysis(self):
        """Test extraction of stakeholder analysis from conversation."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="Who are our stakeholders?"),
                AIMessage(content="Key stakeholders include employees, customers, and partners with different engagement needs and influence levels."),
                HumanMessage(content="Good stakeholder mapping")
            ]
            state["conversation_history"] = messages
            
            stakeholder_analysis = agent._extract_stakeholder_analysis(state)
            
            assert "stakeholder" in stakeholder_analysis.lower()
            assert "engagement" in stakeholder_analysis.lower()
    
    def test_extract_process_design(self):
        """Test extraction of process design from conversation."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What processes do we need?"),
                AIMessage(content="Implementation processes should include governance structures, decision workflows, and communication frameworks for effective execution."),
                HumanMessage(content="That covers our process needs")
            ]
            state["conversation_history"] = messages
            
            process_design = agent._extract_process_design(state)
            
            assert "process" in process_design.lower()
            assert "governance" in process_design.lower()
    
    def test_extract_resource_plan(self):
        """Test extraction of resource planning from conversation."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            
            messages = [
                HumanMessage(content="What resources do we need?"),
                AIMessage(content="Resource requirements include skilled personnel, budget allocation, technology infrastructure, and capability development for successful implementation."),
                HumanMessage(content="That's comprehensive resource planning")
            ]
            state["conversation_history"] = messages
            
            resource_plan = agent._extract_resource_plan(state)
            
            assert "resource" in resource_plan.lower()
            assert "capability" in resource_plan.lower()
    
    def test_format_strategic_context(self):
        """Test formatting of strategic context."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["current_phase"] = "what"
            state["strategy_completeness"]["why"] = True
            state["strategy_completeness"]["logical_structure"] = True
            state["user_context"] = {
                "company_name": "TechStart",
                "industry": "software",
                "team_size": "20-50"
            }
            
            context = agent._format_strategic_context(state)
            
            assert "Strategic Phase: what" in context
            assert "Completed Elements: why, logical_structure" in context
            assert "Company Name: TechStart" in context
    
    def test_format_implementation_scope(self):
        """Test formatting of implementation scope."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            state["current_phase"] = "what"
            state["strategy_completeness"]["why"] = True
            state["strategy_completeness"]["analogy_analysis"] = True
            state["user_context"] = {
                "team_size": "50-100",
                "revenue_stage": "growth",
                "industry": "fintech"
            }
            
            scope = agent._format_implementation_scope(state)
            
            assert "Strategic scope includes: why, analogy_analysis" in scope
            assert "Team scale: 50-100" in scope
            assert "Business stage: growth" in scope
            assert "what phase execution" in scope
    
    def test_update_state_with_insights_roadmap(self):
        """Test state updates during implementation roadmap stage."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Implementation roadmap completed with clear timeline and milestones..."
            
            updated_state = agent._update_state_with_insights(state, "implementation_roadmap", response)
            
            # Should mark implementation plan as complete during roadmap stage
            assert updated_state["strategy_completeness"]["implementation_plan"] is True
            assert len(updated_state["identified_gaps"]) > 0
    
    def test_update_state_with_insights_other_stages(self):
        """Test state updates during non-roadmap stages."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            state = initialize_agent_state("test_session", "test_path")
            response = "Stakeholder analysis in progress..."
            
            updated_state = agent._update_state_with_insights(state, "stakeholder_analysis", response)
            
            # Should not mark implementation plan as complete for non-roadmap stages
            assert updated_state["strategy_completeness"]["implementation_plan"] is False
            assert len(updated_state["identified_gaps"]) > 0


class TestOpenStrategyAgentProcessing:
    """Test Open Strategy Agent processing functionality."""
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_process_user_input_stakeholder_analysis(self, mock_llm_client):
        """Test processing user input during stakeholder analysis."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's identify key stakeholders including internal teams, customers, and external partners."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "Who should be involved in implementing our strategy?"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Verify response was added to conversation
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        
        # Verify processing metadata
        assert result["processing_stage"] == "open_strategy_agent_completed"
        assert result["current_agent"] == "open_strategy_agent"
        assert result["agent_output"] is not None
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_process_user_input_process_design(self, mock_llm_client):
        """Test processing user input during process design."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Now let's design governance processes and decision-making workflows for implementation."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for process design stage
        messages = [
            HumanMessage(content="Our stakeholders are employees and customers"),
            AIMessage(content="Good stakeholder identification and engagement planning...")
        ]
        state["conversation_history"] = messages
        
        user_input = "What processes do we need for effective implementation?"
        
        result = agent.process_user_input(state, user_input)
        
        # Verify processing completed successfully
        assert result["processing_stage"] == "open_strategy_agent_completed"
        assert len(result["conversation_history"]) == 3  # Original 2 + new AI response
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_process_user_input_roadmap_stage(self, mock_llm_client):
        """Test processing user input during implementation roadmap creation."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "**IMPLEMENTATION ROADMAP:** Complete timeline with phases, milestones, and resource deployment schedule."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up for roadmap stage (comprehensive conversation)
        messages = []
        for i in range(8):
            messages.extend([
                HumanMessage(content=f"Implementation discussion {i}: stakeholders, processes, resources"),
                AIMessage(content=f"Implementation planning shows strong foundation...")
            ])
        
        state["conversation_history"] = messages
        
        user_input = "Let's create our implementation roadmap"
        
        result = agent.process_user_input(state, user_input)
        
        # Should mark implementation plan as complete during roadmap creation
        assert result["strategy_completeness"]["implementation_plan"] is True
        assert "Implementation roadmap completed" in str(result["identified_gaps"])
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_process_user_input_with_strategic_foundation(self, mock_llm_client):
        """Test processing with established strategic foundation."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Given your strategic foundation, let's plan stakeholder engagement for implementation."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up strategic foundation
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        state["strategy_completeness"]["logical_structure"] = True
        state["conversation_history"] = [
            AIMessage(content="Your strategic approach combines purpose-driven innovation with validated logical frameworks")
        ]
        
        result = agent.process_user_input(state, "Now let's plan implementation")
        
        # Should extract strategic foundation properly
        strategic_foundation = agent._extract_strategic_foundation(state)
        assert "innovation" in strategic_foundation.lower() or "established" in strategic_foundation.lower()
        
        # Should process successfully
        assert result["processing_stage"] == "open_strategy_agent_completed"
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_process_user_input_llm_error(self, mock_llm_client):
        """Test handling of LLM errors during processing."""
        # Mock LLM to raise an error
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        user_input = "Let's plan our implementation"
        
        result = agent.process_user_input(state, user_input)
        
        # Should handle error gracefully
        assert "error_state" in result
        assert result["error_state"]["error_type"] == "Exception"
        
        # Should still provide fallback response
        assert len(result["conversation_history"]) == 1
        assert isinstance(result["conversation_history"][0], AIMessage)
        assert "implementation" in result["conversation_history"][0].content.lower()
    
    def test_fallback_responses(self):
        """Test fallback responses for different scenarios."""
        with patch('src.agents.open_strategy_agent.get_llm_client') as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = OpenStrategyAgent()
            
            # Test general fallback
            fallback = agent._get_fallback_response()
            assert "implementation" in fallback.lower()
            assert "stakeholder" in fallback.lower()
            
            # Test stakeholder fallback
            stakeholder_fallback = agent._get_fallback_stakeholder_response()
            assert "stakeholder" in stakeholder_fallback.lower()
            assert "implementation" in stakeholder_fallback.lower()
            
            # Test process fallback
            process_fallback = agent._get_fallback_process_response()
            assert "process" in process_fallback.lower()
            assert "workflow" in process_fallback.lower()
            
            # Test resource fallback
            resource_fallback = agent._get_fallback_resource_response()
            assert "resource" in resource_fallback.lower()
            assert "capability" in resource_fallback.lower()
            
            # Test roadmap fallback
            roadmap_fallback = agent._get_fallback_roadmap_response()
            assert "roadmap" in roadmap_fallback.lower()
            assert "timeline" in roadmap_fallback.lower()


class TestOpenStrategyAgentNodeCreation:
    """Test Open Strategy Agent node creation for orchestrator."""
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_create_open_strategy_agent_node(self, mock_llm_client):
        """Test creation of Open Strategy Agent node function."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Let's plan your implementation strategy..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_open_strategy_agent_node()
        
        # Test the node function
        state = initialize_agent_state("test_session", "test_path")
        user_message = HumanMessage(content="How do we implement our strategy?")
        state["conversation_history"] = [user_message]
        
        result = node_function(state)
        
        # Should process the user input successfully
        assert result is not None
        assert len(result["conversation_history"]) >= 1
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_open_strategy_agent_node_with_empty_conversation(self, mock_llm_client):
        """Test Open Strategy Agent node with empty conversation history."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "I'm here to help plan your strategy implementation..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        node_function = create_open_strategy_agent_node()
        state = initialize_agent_state("test_session", "test_path")
        # Leave conversation history empty
        
        result = node_function(state)
        
        # Should handle empty conversation gracefully
        assert result is not None
        assert len(result["conversation_history"]) >= 1


@pytest.mark.integration
class TestOpenStrategyAgentIntegration:
    """Integration tests for Open Strategy Agent."""
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_complete_implementation_planning_flow(self, mock_llm_client):
        """Test complete implementation planning flow through all stages."""
        # Mock different LLM responses for different stages
        mock_llm = MagicMock()
        mock_responses = [
            MagicMock(content="Let's identify key stakeholders for implementation..."),
            MagicMock(content="Now let's design governance processes and workflows..."),
            MagicMock(content="Let's plan resources and capabilities needed..."),
            MagicMock(content="**IMPLEMENTATION ROADMAP:** Complete execution plan...")
        ]
        mock_llm.invoke.side_effect = mock_responses
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Stage 1: Stakeholder Analysis
        state = agent.process_user_input(state, "Who should be involved in implementation?")
        assert len(state["conversation_history"]) == 1
        assert state["strategy_completeness"]["implementation_plan"] is False
        
        # Stage 2: Process Design (simulate conversation progression)
        state["conversation_history"].extend([
            HumanMessage(content="Key stakeholders are employees and customers"),
            AIMessage(content="Great stakeholder identification...")
        ])
        
        state = agent.process_user_input(state, "What processes do we need?")
        assert len(state["conversation_history"]) == 4
        
        # Stage 3: Resource Planning (simulate more conversation)
        state["conversation_history"].extend([
            HumanMessage(content="Process design looks comprehensive"),
            AIMessage(content="Strong governance framework...")
        ])
        
        state = agent.process_user_input(state, "What resources do we need?")
        assert len(state["conversation_history"]) == 7
        
        # Stage 4: Implementation Roadmap (simulate comprehensive conversation for roadmap trigger)
        for i in range(4):
            state["conversation_history"].extend([
                HumanMessage(content=f"Additional implementation planning {i}"),
                AIMessage(content=f"Building comprehensive implementation framework...")
            ])
        
        state = agent.process_user_input(state, "Let's create our roadmap")
        
        # Should complete implementation plan phase
        assert state["strategy_completeness"]["implementation_plan"] is True
        assert "Implementation roadmap completed" in str(state["identified_gaps"])
        
        # Verify all LLM calls were made
        assert mock_llm.invoke.call_count == 4
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_open_strategy_agent_with_full_strategic_context(self, mock_llm_client):
        """Test Open Strategy Agent when all previous strategic phases are completed."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Given your complete strategic foundation, let's plan comprehensive implementation..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set all strategic phases as completed
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        state["strategy_completeness"]["logical_structure"] = True
        state["current_phase"] = "what"
        state["conversation_history"] = [
            AIMessage(content="Your strategic foundation combines purpose-driven innovation with analogical insights and validated logical frameworks")
        ]
        
        result = agent.process_user_input(state, "Now let's plan implementation")
        
        # Should extract comprehensive strategic foundation
        strategic_foundation = agent._extract_strategic_foundation(state)
        assert "innovation" in strategic_foundation.lower() or "Core purpose and WHY clarified" in strategic_foundation
        
        # Should process successfully
        assert result["processing_stage"] == "open_strategy_agent_completed"
    
    @patch('src.agents.open_strategy_agent.get_llm_client')
    def test_open_strategy_agent_context_extraction_comprehensive(self, mock_llm_client):
        """Test Open Strategy Agent's comprehensive context extraction capabilities."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Planning implementation based on your rich strategic and organizational context..."
        mock_llm.invoke.return_value = mock_response
        mock_llm_client.return_value = mock_llm
        
        agent = OpenStrategyAgent()
        state = initialize_agent_state("test_session", "test_path")
        
        # Set up comprehensive context
        state["current_phase"] = "what"
        state["strategy_completeness"]["why"] = True
        state["strategy_completeness"]["analogy_analysis"] = True
        state["strategy_completeness"]["logical_structure"] = True
        state["user_context"] = {
            "company_name": "InnovateCorpStrategy",
            "industry": "technology",
            "team_size": "100-200",
            "revenue_stage": "scaling"
        }
        
        result = agent.process_user_input(state, "Let's plan comprehensive implementation")
        
        # Test context extraction methods
        context_info = agent._format_context_info(state)
        assert "Current Phase: what" in context_info
        assert "Completed Strategy Elements" in context_info
        assert "InnovateCorpStrategy" in context_info
        
        strategic_context = agent._format_strategic_context(state)
        assert "Strategic Phase: what" in strategic_context
        assert "Completed Elements" in strategic_context
        
        implementation_scope = agent._format_implementation_scope(state)
        assert "Strategic scope includes" in implementation_scope
        assert "Team scale: 100-200" in implementation_scope
        assert "Business stage: scaling" in implementation_scope
        
        assert result["processing_stage"] == "open_strategy_agent_completed"