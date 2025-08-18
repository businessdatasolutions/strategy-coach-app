"""
LangGraph conditional edge functions for phase transitions.

These functions determine routing between agent nodes based on phase completion
and user confirmation signals.
"""

import logging
from typing import List, Literal

from langchain_core.messages import BaseMessage
from langsmith import traceable

from .state import StrategyCoachState

logger = logging.getLogger(__name__)


def route_phase_transition(
    state: StrategyCoachState,
) -> Literal["why_agent", "how_agent", "what_agent", "__end__"]:
    """
    Conditional edge function to route between phase agent nodes.

    Routes based on current phase and completion status:
    - If phase not complete: stay in current phase
    - If phase complete and transition confirmed: move to next phase
    - If all phases complete: end the graph
    """
    current_phase = state.get("current_phase", "WHY")
    phase_complete = state.get("phase_complete", False)
    methodology_stage = state.get("methodology_stage", "unknown")

    # Check if user requested transition in last message
    transition_requested = _check_user_transition_request(state.get("messages", []))

    logger.info(f"🔀 Phase Routing: {current_phase} (stage: {methodology_stage}, complete: {phase_complete}, transition_req: {transition_requested})")

    # Route based on current phase and completion status
    if current_phase == "WHY":
        if phase_complete and transition_requested:
            target = "how_agent"
            logger.info(f"🔀 Routing: WHY → HOW (phase complete & transition requested)")
            return target
        else:
            target = "why_agent"
            logger.info(f"🔀 Routing: Continue WHY (complete: {phase_complete}, req: {transition_requested})")
            return target

    elif current_phase == "HOW":
        if phase_complete and transition_requested:
            target = "what_agent"
            logger.info(f"🔀 Routing: HOW → WHAT (phase complete & transition requested)")
            return target
        else:
            target = "how_agent"
            logger.info(f"🔀 Routing: Continue HOW (complete: {phase_complete}, req: {transition_requested})")
            return target

    elif current_phase == "WHAT":
        if phase_complete:
            target = "__end__"
            logger.info(f"🔀 Routing: WHAT → END (session complete)")
            return target
        else:
            target = "what_agent"
            logger.info(f"🔀 Routing: Continue WHAT (complete: {phase_complete})")
            return target

    # Default: stay in current phase
    target = f"{current_phase.lower()}_agent"
    logger.info(f"🔀 Routing: Default to {target}")
    return target


def route_from_why(state: StrategyCoachState) -> Literal["how_agent", "__end__"]:
    """Conditional edge specifically for WHY agent transitions."""
    phase_complete = state.get("phase_complete", False)
    transition_requested = _check_user_transition_request(state.get("messages", []))
    methodology_stage = state.get("methodology_stage", "unknown")

    logger.info(f"🔀 WHY Route: stage={methodology_stage}, complete={phase_complete}, transition_req={transition_requested}")

    if phase_complete and transition_requested:
        logger.info("🔀 WHY → HOW: Phase complete with user confirmation")
        return "how_agent"
    # In LangGraph, we should end instead of looping infinitely
    logger.info("🔀 WHY → END: Continuing in WHY or ending session")
    return "__end__"


def route_from_how(state: StrategyCoachState) -> Literal["how_agent", "what_agent"]:
    """Conditional edge specifically for HOW agent transitions."""
    phase_complete = state.get("phase_complete", False)
    transition_requested = _check_user_transition_request(state.get("messages", []))

    if phase_complete and transition_requested:
        return "what_agent"
    return "how_agent"


def route_from_what(state: StrategyCoachState) -> Literal["what_agent", "__end__"]:
    """Conditional edge specifically for WHAT agent transitions."""
    phase_complete = state.get("phase_complete", False)

    if phase_complete:
        return "__end__"
    return "what_agent"


def _check_user_transition_request(messages: List[BaseMessage]) -> bool:
    """
    Check if the latest user message contains a request to transition phases.

    Looks for keywords indicating readiness to move to the next phase.
    """
    if not messages:
        return False

    # Get the last user message
    last_message = None
    for message in reversed(messages):
        if hasattr(message, "type") and message.type == "human":
            last_message = message
            break

    if not last_message:
        return False

    # Check for transition keywords
    transition_keywords = [
        "next phase",
        "move on",
        "ready to move",
        "proceed to",
        "go to next",
        "continue to",
        "ready for",
        "let's move",
        "transition to",
        "yes, i'm ready",
        "i'm ready",
        "let's proceed",
        "move forward",
    ]

    message_content = last_message.content.lower()
    return any(keyword in message_content for keyword in transition_keywords)


def determine_entry_node(
    state: StrategyCoachState,
) -> Literal["why_agent", "how_agent", "what_agent"]:
    """
    Determine which agent node to start with based on current state.

    Used when resuming from a checkpoint or starting a new session.
    """
    current_phase = state.get("current_phase", "WHY")

    # If session has completed phases, determine appropriate starting point
    if (
        state.get("why_output")
        and state.get("how_output")
        and not state.get("what_output")
    ):
        return "what_agent"
    elif state.get("why_output") and not state.get("how_output"):
        return "how_agent"
    else:
        return "why_agent"


def check_session_completion(state: StrategyCoachState) -> bool:
    """Check if the entire strategy coaching session is complete."""
    return (
        state.get("why_output") is not None
        and state.get("how_output") is not None
        and state.get("what_output") is not None
    )
