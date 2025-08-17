"""
Unit tests for the WHY Agent Node implementation.

Tests the Simon Sinek methodology implementation and LangGraph node integration.
"""

from unittest.mock import Mock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.why_node import (
    WHYAgentNode,
    create_why_agent_with_custom_llm,
    why_agent_node,
)
from src.core.models import ActionableValue, CoreBelief, WHYStatement
from src.core.state import StrategyCoachState


class TestWHYAgentNode:
    """Test cases for WHY Agent Node functionality."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        llm = Mock()
        llm.with_structured_output.return_value = Mock()
        return llm

    @pytest.fixture
    def sample_why_statement(self):
        """Create a sample WHY statement for testing."""
        return WHYStatement(
            why_statement="To help every business leader access strategic clarity",
            core_beliefs=[
                CoreBelief(statement="Every leader deserves clear direction"),
                CoreBelief(statement="Strategy should be accessible, not complex"),
            ],
            actionable_values=[
                ActionableValue(
                    value_name="Clarity",
                    action_phrase="Communicate with transparency",
                    explanation="We believe in clear, honest communication",
                ),
                ActionableValue(
                    value_name="Empowerment",
                    action_phrase="Enable others to succeed",
                    explanation="We empower leaders to make confident decisions",
                ),
            ],
            golden_circle_integration="Purpose drives behavior which creates sustainable results",
            primary_beneficiary="business leaders",
            key_outcome="strategic clarity",
        )

    def test_why_agent_initialization(self, mock_llm):
        """Test WHY agent initialization."""
        agent = WHYAgentNode(llm=mock_llm)
        assert agent.llm == mock_llm
        assert agent.structured_llm is not None
        assert "welcome" in agent.prompts
        assert "discovery" in agent.prompts

    def test_why_agent_welcome_stage(self, mock_llm):
        """Test WHY agent welcome stage."""
        agent = WHYAgentNode(llm=mock_llm)

        # Initial state - first interaction
        initial_state = {
            "messages": [HumanMessage(content="Hello, I want to develop my strategy")],
            "current_phase": "WHY",
            "interaction_count": 0,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        result = agent(initial_state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert "strategic journey" in result["messages"][0].content
        assert "origin story" in result["messages"][0].content
        assert result["current_phase"] == "WHY"
        assert result["interaction_count"] == 1
        assert result["phase_complete"] is False

    def test_why_agent_discovery_stage(self, mock_llm):
        """Test WHY agent discovery stage."""
        agent = WHYAgentNode(llm=mock_llm)

        discovery_state = {
            "messages": [
                HumanMessage(content="We started because we saw leaders struggling"),
                AIMessage(content="Previous response"),
            ],
            "current_phase": "WHY",
            "interaction_count": 1,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        result = agent(discovery_state)

        assert isinstance(result["messages"][0], AIMessage)
        assert "dig deeper" in result["messages"][0].content
        assert "moments when" in result["messages"][0].content
        assert result["interaction_count"] == 2

    def test_why_agent_beliefs_mining_stage(self, mock_llm):
        """Test core beliefs mining stage."""
        agent = WHYAgentNode(llm=mock_llm)

        beliefs_state = {
            "messages": [
                HumanMessage(content="We help business leaders"),
                AIMessage(content="Previous response"),
                HumanMessage(content="Our proudest moments are when leaders succeed"),
            ],
            "current_phase": "WHY",
            "interaction_count": 3,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        result = agent(beliefs_state)

        assert "leaders deserves" in result["messages"][0].content
        assert "What do you believe about" in result["messages"][0].content
        assert result["interaction_count"] == 4

    def test_why_agent_completion_stage(self, mock_llm, sample_why_statement):
        """Test WHY agent completion with structured output."""
        # Mock the structured LLM to return our sample WHY statement
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.return_value = sample_why_statement
        mock_llm.with_structured_output.return_value = mock_structured_llm

        agent = WHYAgentNode(llm=mock_llm)

        completion_state = {
            "messages": [
                HumanMessage(content="We help leaders"),
                AIMessage(content="Previous"),
                HumanMessage(content="Leaders deserve clarity"),
                AIMessage(content="Previous"),
                HumanMessage(content="We believe in transparency"),
            ],
            "current_phase": "WHY",
            "interaction_count": 7,  # At completion threshold
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        result = agent(completion_state)

        assert result["phase_complete"] is True
        assert (
            "explore HOW" in result["messages"][0].content
            or "WHY foundation" in result["messages"][0].content
        )
        assert result["why_output"] is not None
        assert result["why_output"].why_statement == sample_why_statement.why_statement
        mock_structured_llm.invoke.assert_called_once()

    def test_extract_beneficiary(self, mock_llm):
        """Test beneficiary extraction from conversation."""
        agent = WHYAgentNode(llm=mock_llm)

        messages = [
            HumanMessage(content="We help customers succeed"),
            HumanMessage(content="Our employees love working here"),
            HumanMessage(content="Students learn better with our tools"),
        ]

        # Should find "customers" first
        beneficiary = agent._extract_beneficiary(messages)
        assert beneficiary == "customers"

        # Test with no clear beneficiary
        unclear_messages = [
            HumanMessage(content="We do good work"),
            HumanMessage(content="It's important to help"),
        ]
        beneficiary = agent._extract_beneficiary(unclear_messages)
        assert beneficiary == "people"  # Default fallback

    def test_extract_why_elements(self, mock_llm):
        """Test WHY element extraction for statement formation."""
        agent = WHYAgentNode(llm=mock_llm)

        messages = [
            HumanMessage(content="We help entrepreneurs build better businesses"),
            HumanMessage(content="Entrepreneurs struggle with strategic clarity"),
        ]

        elements = agent._extract_why_elements(messages)

        assert elements["primary_beneficiary"] == "entrepreneurs"
        assert elements["core_action"] == "empower"
        assert elements["key_resource"] == "strategic clarity"

    def test_create_synthesis_prompt(self, mock_llm):
        """Test synthesis prompt creation for structured output."""
        agent = WHYAgentNode(llm=mock_llm)

        state = {
            "messages": [
                HumanMessage(content="We started to help small businesses"),
                AIMessage(content="Tell me more"),
                HumanMessage(content="Small business owners deserve better tools"),
                AIMessage(content="What drives you?"),
                HumanMessage(content="We believe in empowering entrepreneurs"),
            ]
        }

        prompt = agent._create_synthesis_prompt(state)

        assert len(prompt) == 2  # System + Human message
        assert "Simon Sinek" in prompt[0].content
        assert "small businesses" in prompt[1].content
        assert "entrepreneurs" in prompt[1].content

    def test_determine_why_stage_progression(self, mock_llm):
        """Test WHY stage determination based on interaction count."""
        agent = WHYAgentNode(llm=mock_llm)

        # Test stage progression
        assert agent._determine_why_stage([], 0, None) == "welcome"
        assert agent._determine_why_stage([], 1, None) == "discovery"
        assert agent._determine_why_stage([], 3, None) == "mining_beliefs"
        assert agent._determine_why_stage([], 5, None) == "distilling_why"
        assert (
            agent._determine_why_stage([], 7, None) == "completion_check"
        )  # Updated: completion at 7
        assert agent._determine_why_stage([], 8, None) == "values_definition"
        assert agent._determine_why_stage([], 9, None) == "integration"
        assert agent._determine_why_stage([], 11, None) == "transition_readiness"

    def test_why_agent_node_function(self, mock_llm):
        """Test the main why_agent_node function."""
        with patch("src.agents.why_node.WHYAgentNode") as MockAgent:
            mock_instance = Mock()
            mock_instance.return_value = {"test": "result"}
            MockAgent.return_value = mock_instance

            test_state = {"current_phase": "WHY"}
            result = why_agent_node(test_state)

            MockAgent.assert_called_once()
            mock_instance.assert_called_once_with(test_state)
            assert result == {"test": "result"}

    def test_create_why_agent_with_custom_llm(self, mock_llm):
        """Test factory function for custom LLM."""
        agent = create_why_agent_with_custom_llm(mock_llm)
        assert isinstance(agent, WHYAgentNode)
        assert agent.llm == mock_llm

    def test_why_methodology_fidelity(self, mock_llm):
        """Test that WHY agent follows Simon Sinek methodology principles."""
        agent = WHYAgentNode(llm=mock_llm)

        # Test that prompts follow Golden Circle principles
        assert "WHY you exist" in agent.prompts["welcome"]
        assert "core belief" in agent.prompts["welcome"]
        assert "origin story" in agent.prompts["welcome"]

        # Test discovery focuses on authentic purpose
        assert "most proud" in agent.prompts["discovery"]
        assert "meaningful" in agent.prompts["discovery"]

        # Test beliefs mining follows Sinek approach
        assert "core beliefs" in agent.prompts["mining_beliefs"]
        assert "deserves" in agent.prompts["mining_beliefs"]

        # Test WHY format follows Sinek template
        assert "To {core_action}" in agent.prompts["distilling_why"]
        assert "so they can" in agent.prompts["distilling_why"]

    def test_error_handling_in_completion(self, mock_llm):
        """Test error handling during structured output generation."""
        # Mock structured LLM to raise an exception
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.side_effect = Exception("API Error")
        mock_llm.with_structured_output.return_value = mock_structured_llm

        agent = WHYAgentNode(llm=mock_llm)

        completion_state = {
            "messages": [HumanMessage(content="Test conversation")],
            "current_phase": "WHY",
            "interaction_count": 8,
            "phase_complete": False,
            "why_output": None,
            "user_context": {},
        }

        result = agent._handle_completion_stage(completion_state)

        # Should handle error gracefully and continue conversation
        assert isinstance(result, AIMessage)
        assert "continue refining" in result.content
        assert not hasattr(result, "structured_output")
