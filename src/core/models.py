"""
Pydantic models for session state, phase transitions, and structured outputs.
These models define the data structures used throughout the application.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Phase(str, Enum):
    """Enumeration of the three strategic development phases."""

    WHY = "WHY"
    HOW = "HOW"
    WHAT = "WHAT"


class MessageRole(str, Enum):
    """Message roles for conversation history."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """A single message in the conversation history."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PhaseTransitionTrigger(BaseModel):
    """Represents a request to transition between phases."""

    from_phase: Phase
    to_phase: Phase
    user_confirmation: bool = False
    transition_reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("to_phase")
    @classmethod
    def validate_phase_progression(cls, v, info):
        """Ensure phases follow the correct progression: WHY → HOW → WHAT."""
        if info.data and "from_phase" in info.data:
            from_phase = info.data["from_phase"]
            valid_transitions = {
                Phase.WHY: Phase.HOW,
                Phase.HOW: Phase.WHAT,
            }
            if from_phase in valid_transitions and v != valid_transitions[from_phase]:
                raise ValueError(f"Invalid transition from {from_phase} to {v}")
        return v


# WHY Phase Structured Outputs


class CoreBelief(BaseModel):
    """A core belief that drives the organization."""

    statement: str = Field(..., description="The belief statement")
    description: Optional[str] = Field(
        None, description="Additional context for the belief"
    )


class ActionableValue(BaseModel):
    """A value expressed as an actionable verb phrase."""

    value_name: str = Field(..., description="Name of the value")
    action_phrase: str = Field(
        ..., description="Value expressed as actionable verb phrase"
    )
    explanation: str = Field(
        ..., description="Brief explanation of the value in action"
    )


class WHYStatement(BaseModel):
    """Structured output for the WHY phase following Simon Sinek methodology."""

    why_statement: str = Field(
        ...,
        description="Core purpose statement in format: 'To [action] every [beneficiary] access to [resource], so they can [goal] without [obstacle]'",
    )
    core_beliefs: List[CoreBelief] = Field(
        default_factory=list, description="Core beliefs that drive the organization"
    )
    actionable_values: List[ActionableValue] = Field(
        default_factory=list, description="Values expressed as actionable behaviors"
    )
    golden_circle_integration: str = Field(
        ..., description="Summary of how WHY, beliefs, and values integrate"
    )
    validation_questions: List[str] = Field(
        default_factory=list,
        description="Questions to validate the authenticity of the WHY",
    )
    primary_beneficiary: str = Field(
        ..., description="The primary beneficiary identified in the WHY"
    )
    key_outcome: str = Field(
        ..., description="The key outcome the organization helps achieve"
    )


# HOW Phase Structured Outputs


class AnalogicalComparison(BaseModel):
    """Structured analogy comparison using Carroll & Sørensen methodology."""

    source_company: str = Field(
        ..., description="The company being used as source of analogy"
    )
    target_company: str = Field(..., description="User's company (target of analogy)")
    positive_analogies: List[str] = Field(
        default_factory=list, description="Similarities between source and target"
    )
    negative_analogies: List[str] = Field(
        default_factory=list, description="Differences between source and target"
    )
    causal_theory: str = Field(
        ...,
        description="The theory of why the source company succeeded (vertical relations)",
    )
    applied_theory: str = Field(
        ..., description="How the causal theory applies to the target company"
    )


class LogicalArgument(BaseModel):
    """Logical validation of strategic reasoning."""

    premise_statements: List[str] = Field(
        default_factory=list, description="The logical premises underlying the strategy"
    )
    logical_connection: str = Field(
        ..., description="How the HOW logically connects to the WHY"
    )
    deductive_reasoning: str = Field(
        ..., description="The deductive logic supporting the strategic argument"
    )
    potential_weaknesses: List[str] = Field(
        default_factory=list, description="Identified logical weaknesses or assumptions"
    )


class HOWStrategy(BaseModel):
    """Structured output for the HOW phase."""

    analogical_analysis: AnalogicalComparison
    logical_validation: LogicalArgument
    core_strategic_theory: str = Field(
        ..., description="The synthesized theory of how the organization will succeed"
    )
    strategic_approach: str = Field(
        ..., description="High-level description of the strategic approach"
    )


# WHAT Phase Structured Outputs


class ValueComponent(BaseModel):
    """One of the six value components from Integrated Reporting framework."""

    component_type: Literal[
        "Financial",
        "Manufactured",
        "Intellectual",
        "Human",
        "Social_Relationship",
        "Natural",
    ]
    current_state: str = Field(..., description="Current state of this value component")
    intended_impact: Literal["increase", "decrease", "transform"] = Field(
        ..., description="Intended impact on this value component"
    )
    target_state: str = Field(..., description="Desired future state")
    success_metrics: List[str] = Field(
        default_factory=list, description="Metrics to measure progress"
    )


class StrategyMapObjective(BaseModel):
    """A strategic objective within a perspective."""

    objective_id: str = Field(..., description="Unique identifier for the objective")
    title: str = Field(..., description="Objective title")
    description: str = Field(..., description="Detailed description")
    success_metrics: List[str] = Field(
        default_factory=list, description="How success will be measured"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="IDs of objectives this depends on"
    )


class StrategyMapPerspective(BaseModel):
    """One of the four strategy map perspectives."""

    perspective_name: Literal[
        "Stakeholder_Customer", "Internal_Process", "Learning_Growth", "Value_Creation"
    ]
    objectives: List[StrategyMapObjective] = Field(
        default_factory=list, description="Strategic objectives for this perspective"
    )
    perspective_summary: str = Field(
        ..., description="Summary of this perspective's role in the strategy"
    )


class OpenStrategyPlan(BaseModel):
    """Implementation plan using Open Strategy principles."""

    strategic_challenge: str = Field(..., description="The core strategic challenge")
    strategy_phase: Literal[
        "Idea_Generation", "Strategy_Formulation", "Strategy_Mobilization"
    ]
    participant_groups: List[str] = Field(
        default_factory=list, description="Groups to involve in the strategy process"
    )
    engagement_methods: List[str] = Field(
        default_factory=list, description="Methods for engaging participants"
    )
    core_questions: List[str] = Field(
        default_factory=list, description="Key questions to pose to participants"
    )
    synthesis_plan: str = Field(
        ..., description="How contributions will be synthesized and managed"
    )
    feedback_mechanism: str = Field(
        ..., description="How participants will receive feedback on their contributions"
    )


class WHATStrategy(BaseModel):
    """Structured output for the WHAT phase - the complete strategy map."""

    strategy_map_perspectives: List[StrategyMapPerspective] = Field(
        default_factory=list, description="The four perspectives of the strategy map"
    )
    value_components: List[ValueComponent] = Field(
        default_factory=list,
        description="The six value components and intended impacts",
    )
    open_strategy_plan: OpenStrategyPlan
    strategy_summary: str = Field(
        ..., description="Executive summary of the complete strategy"
    )


# Session Management Models


class SessionPhaseData(BaseModel):
    """Data specific to each phase within a session."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    phase: Phase
    is_complete: bool = False
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completion_time: Optional[datetime] = None
    structured_output: Optional[Union[WHYStatement, HOWStrategy, WHATStrategy]] = None
    interaction_count: int = 0


class SessionState(BaseModel):
    """Complete session state tracking user progress through all phases."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}
    )

    session_id: UUID = Field(default_factory=uuid4)
    current_phase: Phase = Field(default=Phase.WHY)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Conversation history
    conversation_history: List[ConversationMessage] = Field(
        default_factory=list,
        description="Complete conversation history across all phases",
    )

    # Phase-specific data
    why_phase: SessionPhaseData = Field(
        default_factory=lambda: SessionPhaseData(phase=Phase.WHY)
    )
    how_phase: SessionPhaseData = Field(
        default_factory=lambda: SessionPhaseData(phase=Phase.HOW)
    )
    what_phase: SessionPhaseData = Field(
        default_factory=lambda: SessionPhaseData(phase=Phase.WHAT)
    )

    # Transition history
    phase_transitions: List[PhaseTransitionTrigger] = Field(
        default_factory=list, description="History of phase transitions"
    )

    # User metadata
    user_context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional user context and preferences"
    )

    def get_current_phase_data(self) -> SessionPhaseData:
        """Get the data for the current phase."""
        if self.current_phase == Phase.WHY:
            return self.why_phase
        elif self.current_phase == Phase.HOW:
            return self.how_phase
        elif self.current_phase == Phase.WHAT:
            return self.what_phase
        else:
            raise ValueError(f"Unknown phase: {self.current_phase}")

    def add_message(
        self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to the conversation history."""
        message = ConversationMessage(
            role=role, content=content, metadata=metadata or {}
        )
        self.conversation_history.append(message)
        self.last_activity = datetime.now(timezone.utc)

        # Increment interaction count for current phase
        current_phase_data = self.get_current_phase_data()
        if role == MessageRole.USER:
            current_phase_data.interaction_count += 1

    def complete_phase(
        self, structured_output: Union[WHYStatement, HOWStrategy, WHATStrategy]
    ) -> None:
        """Mark the current phase as complete with its structured output."""
        current_phase_data = self.get_current_phase_data()
        current_phase_data.is_complete = True
        current_phase_data.completion_time = datetime.now(timezone.utc)
        current_phase_data.structured_output = structured_output

    def transition_to_phase(
        self,
        new_phase: Phase,
        user_confirmation: bool = False,
        reason: Optional[str] = None,
    ) -> None:
        """Transition to a new phase."""
        # Record the transition
        transition = PhaseTransitionTrigger(
            from_phase=self.current_phase,
            to_phase=new_phase,
            user_confirmation=user_confirmation,
            transition_reason=reason,
        )
        self.phase_transitions.append(transition)

        # Update current phase
        self.current_phase = new_phase
        self.last_activity = datetime.now(timezone.utc)

    def is_session_complete(self) -> bool:
        """Check if all phases are complete."""
        return (
            self.why_phase.is_complete
            and self.how_phase.is_complete
            and self.what_phase.is_complete
        )

    def get_final_strategy_output(self) -> Optional[Dict[str, Any]]:
        """Get the complete strategy output if all phases are complete."""
        if not self.is_session_complete():
            return None

        return {
            "session_id": str(self.session_id),
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.what_phase.completion_time.isoformat()
                if self.what_phase.completion_time
                else None
            ),
            "why_statement": (
                self.why_phase.structured_output.model_dump()
                if self.why_phase.structured_output
                else None
            ),
            "how_strategy": (
                self.how_phase.structured_output.model_dump()
                if self.how_phase.structured_output
                else None
            ),
            "what_strategy": (
                self.what_phase.structured_output.model_dump()
                if self.what_phase.structured_output
                else None
            ),
            "total_interactions": sum(
                [
                    self.why_phase.interaction_count,
                    self.how_phase.interaction_count,
                    self.what_phase.interaction_count,
                ]
            ),
            "phase_transitions": [t.model_dump() for t in self.phase_transitions],
        }


# API Request/Response Models


class ChatRequest(BaseModel):
    """Request model for chat interactions."""

    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[UUID] = Field(
        None, description="Session ID for continuing conversation"
    )


class ChatResponse(BaseModel):
    """Response model for chat interactions."""

    response: str = Field(..., description="Agent response")
    session_id: UUID = Field(..., description="Session ID")
    current_phase: Phase = Field(..., description="Current phase")
    phase_complete: bool = Field(False, description="Whether current phase is complete")
    transition_available: bool = Field(
        False, description="Whether transition to next phase is available"
    )
    session_complete: bool = Field(
        False, description="Whether entire session is complete"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional response metadata"
    )


class SessionInfoResponse(BaseModel):
    """Response model for session information."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}
    )

    session_id: UUID
    current_phase: Phase
    created_at: datetime
    last_activity: datetime
    interaction_counts: Dict[str, int]
    phase_completion_status: Dict[str, bool]
    session_complete: bool


class PhaseTransitionRequest(BaseModel):
    """Request model for explicit phase transitions."""

    session_id: UUID
    target_phase: Phase
    user_confirmation: bool = True
    reason: Optional[str] = None
