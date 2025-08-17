"""
Unit tests for LangGraph state management.

Tests the StrategyCoachState TypedDict, reducer functions, and state utilities.
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
from src.core.state import (
    StrategyCoachState,
    get_current_phase_output,
    get_final_strategy_json,
    increment_interaction_count,
    is_session_complete,
    update_completion_status,
    update_phase_status,
)


class TestStrategyCoachState:
    """Test cases for StrategyCoachState and reducer functions."""

    def test_increment_interaction_count_reducer(self):
        """Test the interaction count reducer function."""
        assert increment_interaction_count(0, 1) == 1
        assert increment_interaction_count(5, 1) == 6
        assert increment_interaction_count(10, 0) == 10

    def test_update_phase_status_reducer(self):
        """Test the phase status reducer function."""
        assert update_phase_status("WHY", "HOW") == "HOW"
        assert update_phase_status("HOW", "WHAT") == "WHAT"
        assert update_phase_status("WHY", "") == "WHY"  # Empty string doesn't update
        assert update_phase_status("WHY", None) == "WHY"  # None doesn't update

    def test_update_completion_status_reducer(self):
        """Test the completion status reducer function."""
        assert update_completion_status(False, True) is True
        assert update_completion_status(True, False) is False
        assert update_completion_status(False, None) is False  # None doesn't update
        assert update_completion_status(True, None) is True  # None doesn't update

    def test_get_current_phase_output_why(self):
        """Test getting current phase output for WHY phase."""
        why_statement = WHYStatement(
            why_statement="Test WHY",
            golden_circle_integration="Test integration",
            primary_beneficiary="users",
            key_outcome="success",
        )

        state = {
            "current_phase": "WHY",
            "why_output": why_statement,
            "how_output": None,
            "what_output": None,
        }

        output = get_current_phase_output(state)
        assert output is not None
        assert output["why_statement"] == "Test WHY"

    def test_get_current_phase_output_how(self):
        """Test getting current phase output for HOW phase."""
        how_strategy = HOWStrategy(
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
            strategic_approach="Innovate continuously",
        )

        state = {
            "current_phase": "HOW",
            "why_output": None,
            "how_output": how_strategy,
            "what_output": None,
        }

        output = get_current_phase_output(state)
        assert output is not None
        assert output["core_strategic_theory"] == "Innovation strategy"

    def test_get_current_phase_output_what(self):
        """Test getting current phase output for WHAT phase."""
        what_strategy = WHATStrategy(
            open_strategy_plan=OpenStrategyPlan(
                strategic_challenge="Test challenge",
                strategy_phase="Idea_Generation",
                synthesis_plan="Test synthesis",
                feedback_mechanism="Test feedback",
            ),
            strategy_summary="Test strategy summary",
        )

        state = {
            "current_phase": "WHAT",
            "why_output": None,
            "how_output": None,
            "what_output": what_strategy,
        }

        output = get_current_phase_output(state)
        assert output is not None
        assert output["strategy_summary"] == "Test strategy summary"

    def test_get_current_phase_output_none(self):
        """Test getting current phase output when none exists."""
        state = {
            "current_phase": "WHY",
            "why_output": None,
            "how_output": None,
            "what_output": None,
        }

        output = get_current_phase_output(state)
        assert output is None

    def test_is_session_complete_false(self):
        """Test session completion check when incomplete."""
        incomplete_state = {
            "why_output": WHYStatement(
                why_statement="Test",
                golden_circle_integration="Test",
                primary_beneficiary="test",
                key_outcome="test",
            ),
            "how_output": None,  # Missing HOW
            "what_output": None,
        }

        assert is_session_complete(incomplete_state) is False

    def test_is_session_complete_true(self):
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

        assert is_session_complete(complete_state) is True

    def test_get_final_strategy_json_incomplete(self):
        """Test getting final strategy JSON when session incomplete."""
        incomplete_state = {
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "interaction_count": 5,
        }

        result = get_final_strategy_json(incomplete_state)
        assert result is None

    def test_get_final_strategy_json_complete(self):
        """Test getting final strategy JSON when session complete."""
        why_output = WHYStatement(
            why_statement="Test WHY",
            golden_circle_integration="Test",
            primary_beneficiary="test",
            key_outcome="test",
        )

        how_output = HOWStrategy(
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

        what_output = WHATStrategy(
            open_strategy_plan=OpenStrategyPlan(
                strategic_challenge="Test",
                strategy_phase="Idea_Generation",
                synthesis_plan="Test",
                feedback_mechanism="Test",
            ),
            strategy_summary="Test summary",
        )

        complete_state = {
            "why_output": why_output,
            "how_output": how_output,
            "what_output": what_output,
            "interaction_count": 15,
        }

        result = get_final_strategy_json(complete_state)

        assert result is not None
        assert "strategy_map" in result
        assert result["strategy_map"]["why_foundation"]["why_statement"] == "Test WHY"
        assert (
            result["strategy_map"]["strategic_logic"]["core_strategic_theory"] == "Test"
        )
        assert (
            result["strategy_map"]["implementation_plan"]["strategy_summary"]
            == "Test summary"
        )
        assert result["metadata"]["total_interactions"] == 15
        assert result["metadata"]["completion_status"] == "complete"
