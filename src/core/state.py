"""
LangGraph state management for the AI Strategic Co-pilot.

Defines the StrategyCoachState TypedDict and reducer functions used by the StateGraph.
"""

from typing import Annotated, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from .models import HOWStrategy, WHATStrategy, WHYStatement


class StrategyCoachState(TypedDict):
    """
    LangGraph state schema for the Strategy Coach application.

    This state is passed between all nodes in the StateGraph and persisted
    via LangGraph's checkpointing system.
    """

    # Core LangGraph message handling with built-in reducer
    messages: Annotated[List[BaseMessage], add_messages]

    # Phase management
    current_phase: str  # "WHY", "HOW", or "WHAT"
    phase_complete: bool  # Whether current phase is ready for transition
    interaction_count: int  # Number of user interactions in current phase
    methodology_stage: str  # Current stage within methodology (e.g., "welcome", "discovery", "completion_check")

    # Structured outputs from each phase
    why_output: Optional[WHYStatement]  # Output from WHY phase
    how_output: Optional[HOWStrategy]  # Output from HOW phase
    what_output: Optional[WHATStrategy]  # Output from WHAT phase

    # Session metadata
    user_context: dict  # Additional user context and preferences


def increment_interaction_count(current: int, new: int) -> int:
    """Reducer function to increment interaction count."""
    return current + new


def update_phase_status(current: str, new: str) -> str:
    """Reducer function to update current phase."""
    return new if new else current


def update_completion_status(current: bool, new: bool) -> bool:
    """Reducer function to update phase completion status."""
    return new if new is not None else current


# Enhanced state with custom reducers
class StrategyCoachStateWithReducers(TypedDict):
    """Enhanced state schema with custom reducers for better state management."""

    # Core LangGraph message handling
    messages: Annotated[List[BaseMessage], add_messages]

    # Phase management with custom reducers
    current_phase: Annotated[str, update_phase_status]
    phase_complete: Annotated[bool, update_completion_status]
    interaction_count: Annotated[int, increment_interaction_count]

    # Structured outputs (these don't need reducers as they're replaced entirely)
    why_output: Optional[WHYStatement]
    how_output: Optional[HOWStrategy]
    what_output: Optional[WHATStrategy]

    # Session metadata
    user_context: dict


def get_current_phase_output(state: StrategyCoachState) -> Optional[dict]:
    """Get the structured output for the current phase."""
    current_phase = state.get("current_phase", "WHY")

    if current_phase == "WHY":
        return state.get("why_output").model_dump() if state.get("why_output") else None
    elif current_phase == "HOW":
        return state.get("how_output").model_dump() if state.get("how_output") else None
    elif current_phase == "WHAT":
        return (
            state.get("what_output").model_dump() if state.get("what_output") else None
        )

    return None


def is_session_complete(state: StrategyCoachState) -> bool:
    """Check if all phases are complete and session is finished."""
    return (
        state.get("why_output") is not None
        and state.get("how_output") is not None
        and state.get("what_output") is not None
    )


def get_final_strategy_json(state: StrategyCoachState) -> Optional[dict]:
    """Generate the final strategy_map.json if all phases are complete."""
    if not is_session_complete(state):
        return None

    return {
        "strategy_map": {
            "why_foundation": (
                state["why_output"].model_dump() if state["why_output"] else None
            ),
            "strategic_logic": (
                state["how_output"].model_dump() if state["how_output"] else None
            ),
            "implementation_plan": (
                state["what_output"].model_dump() if state["what_output"] else None
            ),
        },
        "metadata": {
            "total_interactions": state.get("interaction_count", 0),
            "completion_status": "complete",
            "phases_completed": ["WHY", "HOW", "WHAT"],
        },
    }
