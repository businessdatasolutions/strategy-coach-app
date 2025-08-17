"""
Integration tests for the LangGraph StateGraph implementation.

Tests the complete StateGraph functionality including agent nodes,
conditional routing, and checkpointing.
"""

from unittest.mock import Mock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.core.config import Settings
from src.core.graph import StrategyCoachGraph, create_strategy_coach_graph
from src.core.state import StrategyCoachState


class TestStrategyCoachGraph:
    """Test cases for the LangGraph StateGraph implementation."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        settings = Mock(spec=Settings)
        settings.llm_provider = "anthropic"
        settings.temperature = 0.7
        settings.max_tokens = 4000
        settings.get_llm_api_key.return_value = "test-api-key"
        settings.use_sqlite_checkpointer = False
        return settings

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        llm = Mock()
        llm.invoke.return_value = Mock(content="Test response from LLM")
        return llm

    @patch("src.core.graph.init_chat_model")
    def test_graph_initialization(self, mock_init_chat_model, mock_settings, mock_llm):
        """Test StrategyCoachGraph initialization."""
        mock_init_chat_model.return_value = mock_llm

        graph = StrategyCoachGraph(mock_settings)

        assert graph.settings == mock_settings
        assert graph.llm == mock_llm
        assert graph.graph is not None
        mock_init_chat_model.assert_called_once()

    @patch("src.core.graph.init_chat_model")
    def test_graph_initialization_no_api_key(self, mock_init_chat_model, mock_settings):
        """Test graph initialization fails without API key."""
        mock_settings.get_llm_api_key.return_value = None

        with pytest.raises(ValueError, match="No API key configured"):
            StrategyCoachGraph(mock_settings)

    @patch("src.core.graph.init_chat_model")
    def test_unsupported_llm_provider(
        self, mock_init_chat_model, mock_settings, mock_llm
    ):
        """Test handling of unsupported LLM provider."""
        mock_settings.llm_provider = "unsupported"
        mock_init_chat_model.return_value = mock_llm

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            StrategyCoachGraph(mock_settings)

    @patch("src.core.graph.init_chat_model")
    def test_why_agent_node_welcome(
        self, mock_init_chat_model, mock_settings, mock_llm
    ):
        """Test WHY agent node welcome message."""
        mock_init_chat_model.return_value = mock_llm
        graph = StrategyCoachGraph(mock_settings)

        # Test initial state
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

        result = graph._why_agent_node(initial_state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert "strategic journey" in result["messages"][0].content
        assert result["current_phase"] == "WHY"
        assert result["interaction_count"] == 1

    @patch("src.core.graph.init_chat_model")
    def test_why_agent_node_completion(
        self, mock_init_chat_model, mock_settings, mock_llm
    ):
        """Test WHY agent node phase completion."""
        mock_init_chat_model.return_value = mock_llm
        graph = StrategyCoachGraph(mock_settings)

        # Test state at completion threshold
        completion_state = {
            "messages": [
                HumanMessage(content="I've shared my story"),
                AIMessage(content="Previous response"),
                HumanMessage(content="Yes, I'm ready to move on"),
            ],
            "current_phase": "WHY",
            "interaction_count": 3,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        result = graph._why_agent_node(completion_state)

        assert result["phase_complete"] is True
        assert result["why_output"] is not None
        assert result["why_output"].why_statement is not None
        assert (
            "ready to move on" in result["messages"][0].content
            or "ready to refine" in result["messages"][0].content
        )

    @patch("src.core.graph.init_chat_model")
    def test_how_agent_node_entry(self, mock_init_chat_model, mock_settings, mock_llm):
        """Test HOW agent node entry from WHY phase."""
        mock_init_chat_model.return_value = mock_llm
        graph = StrategyCoachGraph(mock_settings)

        # Create state with completed WHY phase
        from src.core.models import CoreBelief, WHYStatement

        why_statement = WHYStatement(
            why_statement="To help every business leader access strategic clarity",
            core_beliefs=[CoreBelief(statement="Leaders deserve clarity")],
            actionable_values=[],
            golden_circle_integration="Test integration",
            primary_beneficiary="business leaders",
            key_outcome="strategic clarity",
        )

        how_entry_state = {
            "messages": [HumanMessage(content="I'm ready for the HOW phase")],
            "current_phase": "WHY",  # Transitioning from WHY
            "interaction_count": 0,
            "phase_complete": False,
            "why_output": why_statement,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        result = graph._how_agent_node(how_entry_state)

        assert result["current_phase"] == "HOW"
        assert result["interaction_count"] == 1
        assert "analogical reasoning" in result["messages"][0].content
        assert why_statement.why_statement in result["messages"][0].content

    @patch("src.core.graph.init_chat_model")
    def test_what_agent_node_final_phase(
        self, mock_init_chat_model, mock_settings, mock_llm
    ):
        """Test WHAT agent node in final phase."""
        mock_init_chat_model.return_value = mock_llm
        graph = StrategyCoachGraph(mock_settings)

        # Create state with completed WHY and HOW phases
        from src.core.models import (
            AnalogicalComparison,
            HOWStrategy,
            LogicalArgument,
            WHYStatement,
        )

        why_output = WHYStatement(
            why_statement="To help every business leader",
            golden_circle_integration="Test",
            primary_beneficiary="leaders",
            key_outcome="success",
        )

        how_output = HOWStrategy(
            analogical_analysis=AnalogicalComparison(
                source_company="Tesla",
                target_company="Our Company",
                causal_theory="Innovation drives success",
                applied_theory="We apply innovation",
            ),
            logical_validation=LogicalArgument(
                logical_connection="Innovation connects to success",
                deductive_reasoning="Innovation leads to advantage",
            ),
            core_strategic_theory="Innovation strategy",
            strategic_approach="Customer-centric innovation",
        )

        what_entry_state = {
            "messages": [HumanMessage(content="Ready for strategy mapping")],
            "current_phase": "HOW",  # Transitioning from HOW
            "interaction_count": 0,
            "phase_complete": False,
            "why_output": why_output,
            "how_output": how_output,
            "what_output": None,
            "user_context": {},
        }

        result = graph._what_agent_node(what_entry_state)

        assert result["current_phase"] == "WHAT"
        assert result["interaction_count"] == 1
        assert "strategy map" in result["messages"][0].content
        assert "four key perspectives" in result["messages"][0].content

    @patch("src.core.graph.init_chat_model")
    def test_graph_invoke_basic(self, mock_init_chat_model, mock_settings, mock_llm):
        """Test basic graph invocation."""
        mock_init_chat_model.return_value = mock_llm
        graph = StrategyCoachGraph(mock_settings)

        initial_input = {
            "messages": [HumanMessage(content="Hello, I want to develop my strategy")],
            "current_phase": "WHY",
            "interaction_count": 0,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        config = {"configurable": {"thread_id": "test-session-1"}}

        # This should run without errors
        result = graph.invoke(initial_input, config)

        assert result is not None
        assert "messages" in result
        assert (
            len(result["messages"]) >= 3
        )  # Should have messages from all three phases
        assert result["current_phase"] == "WHAT"  # Should end at final phase
        assert result.get("why_output") is not None
        assert result.get("how_output") is not None
        assert result.get("what_output") is not None

    @patch("src.core.graph.init_chat_model")
    def test_graph_streaming(self, mock_init_chat_model, mock_settings, mock_llm):
        """Test graph streaming functionality."""
        mock_init_chat_model.return_value = mock_llm
        graph = StrategyCoachGraph(mock_settings)

        initial_input = {
            "messages": [HumanMessage(content="Test streaming")],
            "current_phase": "WHY",
            "interaction_count": 0,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        config = {"configurable": {"thread_id": "test-stream-1"}}

        # Test that streaming returns an iterable
        stream_result = graph.stream(initial_input, config, stream_mode="values")
        assert stream_result is not None

        # Convert to list to test iteration
        events = list(stream_result)
        assert len(events) >= 3  # Should have events from all three phases

        # Final event should have all phases complete
        final_event = events[-1]
        assert final_event.get("current_phase") == "WHAT"

    def test_create_strategy_coach_graph_factory(self):
        """Test the factory function for creating graphs."""
        with patch("src.core.graph.init_chat_model") as mock_init:
            mock_llm = Mock()
            mock_llm.invoke.return_value = Mock(content="Test")
            mock_init.return_value = mock_llm

            # Test with default settings
            graph = create_strategy_coach_graph()
            assert isinstance(graph, StrategyCoachGraph)

            # Test with custom settings (mock the API key)
            with patch.object(
                Settings, "get_llm_api_key", return_value="test-openai-key"
            ):
                custom_settings = Settings()
                custom_settings.llm_provider = "openai"
                graph2 = create_strategy_coach_graph(custom_settings)
            assert isinstance(graph2, StrategyCoachGraph)

    @patch("src.core.graph.init_chat_model")
    def test_checkpointer_configuration(
        self, mock_init_chat_model, mock_settings, mock_llm
    ):
        """Test that checkpointer is properly configured."""
        mock_init_chat_model.return_value = mock_llm

        # Test InMemorySaver (default)
        mock_settings.use_sqlite_checkpointer = False
        graph = StrategyCoachGraph(mock_settings)

        # Graph should have checkpointer
        assert hasattr(graph.graph, "checkpointer")
        assert graph.graph.checkpointer is not None

    @patch("src.core.graph.init_chat_model")
    def test_state_persistence(self, mock_init_chat_model, mock_settings, mock_llm):
        """Test that state is persisted between invocations."""
        mock_init_chat_model.return_value = mock_llm
        graph = StrategyCoachGraph(mock_settings)

        initial_input = {
            "messages": [HumanMessage(content="Hello")],
            "current_phase": "WHY",
            "interaction_count": 0,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {},
        }

        config = {"configurable": {"thread_id": "test-persistence"}}

        # First invocation - will complete all phases
        result1 = graph.invoke(initial_input, config)

        # Get state to verify persistence
        state_snapshot = graph.get_state(config)
        assert state_snapshot is not None
        assert "messages" in state_snapshot.values
        assert len(state_snapshot.values["messages"]) >= 3  # All phases should have run

        # Verify final state has all outputs
        assert state_snapshot.values.get("why_output") is not None
        assert state_snapshot.values.get("how_output") is not None
        assert state_snapshot.values.get("what_output") is not None
