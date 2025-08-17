"""
Unit tests for LangGraph conditional edge routing functions.

Tests the routing logic that determines phase transitions in the StateGraph.
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.core.models import (
    AnalogicalComparison,
    HOWStrategy,
    LogicalArgument,
    OpenStrategyPlan,
    WHATStrategy,
    WHYStatement,
)
from src.core.routing import (
    _check_user_transition_request,
    check_session_completion,
    determine_entry_node,
    route_from_how,
    route_from_what,
    route_from_why,
    route_phase_transition,
)
from src.core.state import get_final_strategy_json, is_session_complete


class TestRouting:
    """Test cases for LangGraph routing functions."""

    def test_check_user_transition_request_positive(self):
        """Test detection of transition request keywords."""
        positive_messages = [
            HumanMessage(content="I'm ready to move to the next phase"),
            HumanMessage(content="Let's proceed to HOW"),
            HumanMessage(content="Can we go to next phase?"),
            HumanMessage(content="I want to move on"),
            HumanMessage(content="Ready for the next step"),
            HumanMessage(content="Yes, I'm ready"),
            HumanMessage(content="Let's move forward"),
        ]

        for message in positive_messages:
            assert _check_user_transition_request([message]) is True

    def test_check_user_transition_request_negative(self):
        """Test that normal conversation doesn't trigger transitions."""
        negative_messages = [
            HumanMessage(content="Tell me more about this"),
            HumanMessage(content="I need help understanding"),
            HumanMessage(content="What should I do next?"),
            HumanMessage(content="Can you explain that?"),
            HumanMessage(content="I have more questions"),
            HumanMessage(content="Let me think about this"),
        ]

        for message in negative_messages:
            assert _check_user_transition_request([message]) is False

    def test_check_user_transition_request_mixed_messages(self):
        """Test transition detection with mixed message types."""
        messages = [
            AIMessage(content="AI response"),
            HumanMessage(content="Normal question"),
            AIMessage(content="AI response"),
            HumanMessage(content="I'm ready to move on"),  # This should trigger
        ]

        assert _check_user_transition_request(messages) is True

    def test_check_user_transition_request_empty(self):
        """Test transition detection with no messages."""
        assert _check_user_transition_request([]) is False
        assert (
            _check_user_transition_request([AIMessage(content="Only AI messages")])
            is False
        )

    def test_route_from_why_stay(self):
        """Test routing from WHY agent when staying in phase."""
        state = {
            "current_phase": "WHY",
            "phase_complete": False,
            "messages": [HumanMessage(content="Tell me more")],
        }

        # Updated: route_from_why now ends when not transitioning
        assert route_from_why(state) == "__end__"

    def test_route_from_why_transition(self):
        """Test routing from WHY agent when transitioning."""
        state = {
            "current_phase": "WHY",
            "phase_complete": True,
            "messages": [HumanMessage(content="I'm ready to move on")],
        }

        assert route_from_why(state) == "how_agent"

    def test_route_from_how_stay(self):
        """Test routing from HOW agent when staying in phase."""
        state = {
            "current_phase": "HOW",
            "phase_complete": False,
            "messages": [HumanMessage(content="Continue with analogy")],
        }

        # Updated: route_from_how stays in how_agent when not transitioning
        assert route_from_how(state) == "how_agent"

    def test_route_from_how_transition(self):
        """Test routing from HOW agent when transitioning."""
        state = {
            "current_phase": "HOW",
            "phase_complete": True,
            "messages": [HumanMessage(content="Ready for strategy mapping")],
        }

        assert route_from_how(state) == "what_agent"

    def test_route_from_what_stay(self):
        """Test routing from WHAT agent when staying in phase."""
        state = {
            "current_phase": "WHAT",
            "phase_complete": False,
            "messages": [HumanMessage(content="More strategy details needed")],
        }

        assert route_from_what(state) == "what_agent"

    def test_route_from_what_complete(self):
        """Test routing from WHAT agent when session complete."""
        state = {
            "current_phase": "WHAT",
            "phase_complete": True,
            "messages": [HumanMessage(content="Strategy is complete")],
        }

        assert route_from_what(state) == "__end__"

    def test_determine_entry_node_new_session(self):
        """Test entry node determination for new session."""
        new_state = {
            "current_phase": "WHY",
            "why_output": None,
            "how_output": None,
            "what_output": None,
        }

        assert determine_entry_node(new_state) == "why_agent"

    def test_determine_entry_node_why_complete(self):
        """Test entry node determination with WHY phase complete."""
        why_complete_state = {
            "current_phase": "HOW",
            "why_output": WHYStatement(
                why_statement="Test",
                golden_circle_integration="Test",
                primary_beneficiary="test",
                key_outcome="test",
            ),
            "how_output": None,
            "what_output": None,
        }

        assert determine_entry_node(why_complete_state) == "how_agent"

    def test_determine_entry_node_how_complete(self):
        """Test entry node determination with WHY and HOW complete."""
        how_complete_state = {
            "current_phase": "WHAT",
            "why_output": WHYStatement(
                why_statement="Test",
                golden_circle_integration="Test",
                primary_beneficiary="test",
                key_outcome="test",
            ),
            "how_output": HOWStrategy(
                analogical_analysis=AnalogicalComparison(
                    source_company="Test",
                    target_company="Test",
                    causal_theory="Test",
                    applied_theory="Test",
                ),
                logical_validation=LogicalArgument(
                    logical_connection="Test", deductive_reasoning="Test"
                ),
                core_strategic_theory="Test",
                strategic_approach="Test",
            ),
            "what_output": None,
        }

        assert determine_entry_node(how_complete_state) == "what_agent"

    def test_check_session_completion_incomplete(self):
        """Test session completion check when incomplete."""
        incomplete_state = {
            "why_output": WHYStatement(
                why_statement="Test",
                golden_circle_integration="Test",
                primary_beneficiary="test",
                key_outcome="test",
            ),
            "how_output": None,  # Missing
            "what_output": None,
        }

        assert check_session_completion(incomplete_state) is False

    def test_check_session_completion_complete(self):
        """Test session completion check when complete."""
        complete_state = {
            "why_output": WHYStatement(
                why_statement="Test",
                golden_circle_integration="Test",
                primary_beneficiary="test",
                key_outcome="test",
            ),
            "how_output": HOWStrategy(
                analogical_analysis=AnalogicalComparison(
                    source_company="Test",
                    target_company="Test",
                    causal_theory="Test",
                    applied_theory="Test",
                ),
                logical_validation=LogicalArgument(
                    logical_connection="Test", deductive_reasoning="Test"
                ),
                core_strategic_theory="Test",
                strategic_approach="Test",
            ),
            "what_output": WHATStrategy(
                open_strategy_plan=OpenStrategyPlan(
                    strategic_challenge="Test",
                    strategy_phase="Idea_Generation",
                    synthesis_plan="Test",
                    feedback_mechanism="Test",
                ),
                strategy_summary="Test",
            ),
        }

        assert check_session_completion(complete_state) is True

    def test_is_session_complete_function(self):
        """Test the is_session_complete utility function."""
        # Test incomplete
        incomplete = {"why_output": None, "how_output": None, "what_output": None}
        assert is_session_complete(incomplete) is False

        # Test complete with all outputs
        why_out = WHYStatement(
            why_statement="Test",
            golden_circle_integration="Test",
            primary_beneficiary="test",
            key_outcome="test",
        )
        how_out = HOWStrategy(
            analogical_analysis=AnalogicalComparison(
                source_company="Test",
                target_company="Test",
                causal_theory="Test",
                applied_theory="Test",
            ),
            logical_validation=LogicalArgument(
                logical_connection="Test", deductive_reasoning="Test"
            ),
            core_strategic_theory="Test",
            strategic_approach="Test",
        )
        what_out = WHATStrategy(
            open_strategy_plan=OpenStrategyPlan(
                strategic_challenge="Test",
                strategy_phase="Idea_Generation",
                synthesis_plan="Test",
                feedback_mechanism="Test",
            ),
            strategy_summary="Test",
        )

        complete = {
            "why_output": why_out,
            "how_output": how_out,
            "what_output": what_out,
        }
        assert is_session_complete(complete) is True

    def test_get_final_strategy_json_complete(self):
        """Test final strategy JSON generation."""
        why_out = WHYStatement(
            why_statement="To help leaders succeed",
            golden_circle_integration="Purpose drives action",
            primary_beneficiary="leaders",
            key_outcome="success",
        )

        how_out = HOWStrategy(
            analogical_analysis=AnalogicalComparison(
                source_company="Apple",
                target_company="Our Company",
                causal_theory="Design thinking drives loyalty",
                applied_theory="We use design thinking",
            ),
            logical_validation=LogicalArgument(
                logical_connection="Design connects to loyalty",
                deductive_reasoning="Better design creates better outcomes",
            ),
            core_strategic_theory="Design-driven strategy",
            strategic_approach="Design-first approach",
        )

        what_out = WHATStrategy(
            open_strategy_plan=OpenStrategyPlan(
                strategic_challenge="Implement design strategy",
                strategy_phase="Strategy_Formulation",
                synthesis_plan="Collaborative design process",
                feedback_mechanism="Design reviews",
            ),
            strategy_summary="Complete design-driven strategy",
        )

        complete_state = {
            "why_output": why_out,
            "how_output": how_out,
            "what_output": what_out,
            "interaction_count": 25,
        }

        result = get_final_strategy_json(complete_state)

        assert result is not None
        assert "strategy_map" in result
        assert "metadata" in result
        assert (
            result["strategy_map"]["why_foundation"]["why_statement"]
            == "To help leaders succeed"
        )
        assert (
            result["strategy_map"]["strategic_logic"]["core_strategic_theory"]
            == "Design-driven strategy"
        )
        assert (
            result["strategy_map"]["implementation_plan"]["strategy_summary"]
            == "Complete design-driven strategy"
        )
        assert result["metadata"]["total_interactions"] == 25
        assert result["metadata"]["completion_status"] == "complete"
