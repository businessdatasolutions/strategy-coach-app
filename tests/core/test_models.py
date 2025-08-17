"""
Unit tests for core Pydantic models.
Tests model validation, serialization, and business logic.
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.core.models import (
    ActionableValue,
    AnalogicalComparison,
    ChatRequest,
    ChatResponse,
    ConversationMessage,
    CoreBelief,
    HOWStrategy,
    LogicalArgument,
    MessageRole,
    OpenStrategyPlan,
    Phase,
    PhaseTransitionRequest,
    PhaseTransitionTrigger,
    SessionInfoResponse,
    SessionPhaseData,
    SessionState,
    StrategyMapObjective,
    StrategyMapPerspective,
    ValueComponent,
    WHATStrategy,
    WHYStatement,
)


class TestEnums:
    """Test enum definitions."""

    def test_phase_enum_values(self):
        """Test Phase enum has correct values."""
        assert Phase.WHY == "WHY"
        assert Phase.HOW == "HOW"
        assert Phase.WHAT == "WHAT"
        assert len(Phase) == 3

    def test_message_role_enum_values(self):
        """Test MessageRole enum has correct values."""
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"
        assert len(MessageRole) == 3


class TestConversationMessage:
    """Test ConversationMessage model."""

    def test_create_message_minimal(self):
        """Test creating message with minimal required fields."""
        message = ConversationMessage(role=MessageRole.USER, content="Hello")
        assert message.role == MessageRole.USER
        assert message.content == "Hello"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata == {}

    def test_create_message_with_metadata(self):
        """Test creating message with metadata."""
        metadata = {"agent_type": "WHY", "confidence": 0.9}
        message = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content="Tell me about your company",
            metadata=metadata,
        )
        assert message.metadata == metadata

    def test_message_serialization(self):
        """Test message JSON serialization."""
        message = ConversationMessage(role=MessageRole.USER, content="Test content")
        data = message.model_dump()
        assert data["role"] == "user"
        assert data["content"] == "Test content"
        assert "timestamp" in data


class TestPhaseTransitionTrigger:
    """Test PhaseTransitionTrigger model and validation."""

    def test_valid_why_to_how_transition(self):
        """Test valid transition from WHY to HOW."""
        transition = PhaseTransitionTrigger(
            from_phase=Phase.WHY,
            to_phase=Phase.HOW,
            user_confirmation=True,
            transition_reason="WHY phase complete",
        )
        assert transition.from_phase == Phase.WHY
        assert transition.to_phase == Phase.HOW
        assert transition.user_confirmation is True

    def test_valid_how_to_what_transition(self):
        """Test valid transition from HOW to WHAT."""
        transition = PhaseTransitionTrigger(
            from_phase=Phase.HOW, to_phase=Phase.WHAT, user_confirmation=True
        )
        assert transition.from_phase == Phase.HOW
        assert transition.to_phase == Phase.WHAT

    def test_invalid_why_to_what_transition(self):
        """Test invalid transition from WHY to WHAT."""
        with pytest.raises(ValidationError) as exc_info:
            PhaseTransitionTrigger(
                from_phase=Phase.WHY, to_phase=Phase.WHAT, user_confirmation=True
            )
        assert "Invalid transition" in str(exc_info.value)

    def test_invalid_how_to_why_transition(self):
        """Test invalid backward transition."""
        with pytest.raises(ValidationError) as exc_info:
            PhaseTransitionTrigger(
                from_phase=Phase.HOW, to_phase=Phase.WHY, user_confirmation=True
            )
        assert "Invalid transition" in str(exc_info.value)


class TestWHYStructuredOutputs:
    """Test WHY phase structured output models."""

    def test_core_belief_creation(self):
        """Test CoreBelief model creation."""
        belief = CoreBelief(
            statement="Everyone deserves access to strategic thinking tools",
            description="Strategic thinking should be democratized",
        )
        assert (
            belief.statement == "Everyone deserves access to strategic thinking tools"
        )
        assert belief.description == "Strategic thinking should be democratized"

    def test_actionable_value_creation(self):
        """Test ActionableValue model creation."""
        value = ActionableValue(
            value_name="Transparency",
            action_phrase="Communicate openly and honestly",
            explanation="We share information transparently to build trust",
        )
        assert value.value_name == "Transparency"
        assert value.action_phrase == "Communicate openly and honestly"

    def test_why_statement_creation(self):
        """Test WHYStatement model creation."""
        beliefs = [CoreBelief(statement="Test belief", description="Test description")]
        values = [
            ActionableValue(
                value_name="Test Value",
                action_phrase="Act with integrity",
                explanation="Always do the right thing",
            )
        ]

        why_statement = WHYStatement(
            why_statement="To give every business leader access to strategic clarity",
            core_beliefs=beliefs,
            actionable_values=values,
            golden_circle_integration="Test integration",
            validation_questions=["Does this feel authentic?"],
            primary_beneficiary="business leaders",
            key_outcome="strategic clarity",
        )

        assert "strategic clarity" in why_statement.why_statement
        assert len(why_statement.core_beliefs) == 1
        assert len(why_statement.actionable_values) == 1
        assert why_statement.primary_beneficiary == "business leaders"


class TestHOWStructuredOutputs:
    """Test HOW phase structured output models."""

    def test_analogical_comparison_creation(self):
        """Test AnalogicalComparison model creation."""
        comparison = AnalogicalComparison(
            source_company="Tesla",
            target_company="Our Company",
            positive_analogies=[
                "Both focus on innovation",
                "Both disrupt traditional industries",
            ],
            negative_analogies=["Tesla is in automotive, we're in software"],
            causal_theory="Innovation-driven disruption creates market leadership",
            applied_theory="We can achieve leadership through software innovation",
        )

        assert comparison.source_company == "Tesla"
        assert comparison.target_company == "Our Company"
        assert len(comparison.positive_analogies) == 2
        assert "innovation" in comparison.causal_theory.lower()

    def test_logical_argument_creation(self):
        """Test LogicalArgument model creation."""
        argument = LogicalArgument(
            premise_statements=[
                "Market demands innovative solutions",
                "We have innovative capabilities",
                "Therefore, we can meet market demand",
            ],
            logical_connection="Innovation connects our capabilities to market needs",
            deductive_reasoning="If markets demand innovation and we provide it, we succeed",
            potential_weaknesses=["Assumes market timing is right"],
        )

        assert len(argument.premise_statements) == 3
        assert "innovation" in argument.logical_connection.lower()
        assert len(argument.potential_weaknesses) == 1

    def test_how_strategy_creation(self):
        """Test HOWStrategy model creation."""
        analogy = AnalogicalComparison(
            source_company="Tesla",
            target_company="Our Company",
            causal_theory="Innovation drives success",
            applied_theory="We apply innovation to our domain",
        )

        logic = LogicalArgument(
            logical_connection="Innovation connects to success",
            deductive_reasoning="Innovation leads to competitive advantage",
        )

        how_strategy = HOWStrategy(
            analogical_analysis=analogy,
            logical_validation=logic,
            core_strategic_theory="Innovation-based competitive advantage",
            strategic_approach="Differentiate through continuous innovation",
        )

        assert how_strategy.analogical_analysis.source_company == "Tesla"
        assert "innovation" in how_strategy.core_strategic_theory.lower()


class TestWHATStructuredOutputs:
    """Test WHAT phase structured output models."""

    def test_value_component_creation(self):
        """Test ValueComponent model creation."""
        component = ValueComponent(
            component_type="Financial",
            current_state="Breaking even",
            intended_impact="increase",
            target_state="Profitable growth",
            success_metrics=["Revenue growth %", "Profit margin"],
        )

        assert component.component_type == "Financial"
        assert component.intended_impact == "increase"
        assert len(component.success_metrics) == 2

    def test_strategy_map_objective_creation(self):
        """Test StrategyMapObjective model creation."""
        objective = StrategyMapObjective(
            objective_id="obj_001",
            title="Increase Customer Satisfaction",
            description="Improve customer satisfaction scores",
            success_metrics=["CSAT score", "NPS"],
            dependencies=["obj_002"],
        )

        assert objective.objective_id == "obj_001"
        assert "satisfaction" in objective.title.lower()
        assert len(objective.success_metrics) == 2

    def test_open_strategy_plan_creation(self):
        """Test OpenStrategyPlan model creation."""
        plan = OpenStrategyPlan(
            strategic_challenge="Increase market share",
            strategy_phase="Idea_Generation",
            participant_groups=["Employees", "Customers", "Partners"],
            engagement_methods=["Workshops", "Surveys"],
            core_questions=["How can we better serve customers?"],
            synthesis_plan="Synthesize feedback into themes",
            feedback_mechanism="Share results with participants",
        )

        assert plan.strategy_phase == "Idea_Generation"
        assert len(plan.participant_groups) == 3
        assert "customers" in plan.core_questions[0].lower()


class TestSessionState:
    """Test SessionState model and methods."""

    def test_session_state_creation(self):
        """Test SessionState model creation with defaults."""
        session = SessionState()

        assert isinstance(session.session_id, UUID)
        assert session.current_phase == Phase.WHY
        assert isinstance(session.created_at, datetime)
        assert len(session.conversation_history) == 0
        assert session.why_phase.phase == Phase.WHY
        assert not session.why_phase.is_complete

    def test_add_message(self):
        """Test adding messages to conversation history."""
        session = SessionState()
        session.add_message(MessageRole.USER, "Hello, I want to develop my strategy")

        assert len(session.conversation_history) == 1
        assert session.conversation_history[0].role == MessageRole.USER
        assert (
            session.conversation_history[0].content
            == "Hello, I want to develop my strategy"
        )
        assert session.why_phase.interaction_count == 1

    def test_add_assistant_message_no_increment(self):
        """Test that assistant messages don't increment interaction count."""
        session = SessionState()
        session.add_message(MessageRole.ASSISTANT, "Tell me about your company")

        assert len(session.conversation_history) == 1
        assert session.why_phase.interaction_count == 0

    def test_get_current_phase_data(self):
        """Test getting current phase data."""
        session = SessionState()

        # Test WHY phase (default)
        phase_data = session.get_current_phase_data()
        assert phase_data.phase == Phase.WHY
        assert not phase_data.is_complete

        # Test HOW phase
        session.current_phase = Phase.HOW
        phase_data = session.get_current_phase_data()
        assert phase_data.phase == Phase.HOW

    def test_complete_phase(self):
        """Test completing a phase with structured output."""
        session = SessionState()
        why_output = WHYStatement(
            why_statement="To help every business leader",
            golden_circle_integration="Test integration",
            primary_beneficiary="business leaders",
            key_outcome="success",
        )

        session.complete_phase(why_output)

        assert session.why_phase.is_complete
        assert session.why_phase.structured_output == why_output
        assert isinstance(session.why_phase.completion_time, datetime)

    def test_transition_to_phase(self):
        """Test phase transition."""
        session = SessionState()
        session.transition_to_phase(
            Phase.HOW, user_confirmation=True, reason="WHY phase complete"
        )

        assert session.current_phase == Phase.HOW
        assert len(session.phase_transitions) == 1
        assert session.phase_transitions[0].from_phase == Phase.WHY
        assert session.phase_transitions[0].to_phase == Phase.HOW
        assert session.phase_transitions[0].user_confirmation is True

    def test_is_session_complete(self):
        """Test session completion check."""
        session = SessionState()
        assert not session.is_session_complete()

        # Complete all phases
        why_output = WHYStatement(
            why_statement="Test",
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
            strategy_summary="Test",
        )

        session.why_phase.is_complete = True
        session.why_phase.structured_output = why_output
        session.how_phase.is_complete = True
        session.how_phase.structured_output = how_output
        session.what_phase.is_complete = True
        session.what_phase.structured_output = what_output

        assert session.is_session_complete()

    def test_get_final_strategy_output_incomplete(self):
        """Test getting final output when session is incomplete."""
        session = SessionState()
        assert session.get_final_strategy_output() is None

    def test_get_final_strategy_output_complete(self):
        """Test getting final output when session is complete."""
        session = SessionState()

        # Set up completed session (simplified)
        session.why_phase.is_complete = True
        session.how_phase.is_complete = True
        session.what_phase.is_complete = True
        session.why_phase.interaction_count = 5
        session.how_phase.interaction_count = 7
        session.what_phase.interaction_count = 8

        output = session.get_final_strategy_output()
        assert output is not None
        assert output["session_id"] == str(session.session_id)
        assert output["total_interactions"] == 20
        assert "created_at" in output


class TestAPIModels:
    """Test API request/response models."""

    def test_chat_request_validation(self):
        """Test ChatRequest validation."""
        # Valid request
        request = ChatRequest(message="Tell me about strategy")
        assert request.message == "Tell me about strategy"
        assert request.session_id is None

        # Request with session ID
        session_id = uuid4()
        request = ChatRequest(
            message="Continue our conversation", session_id=session_id
        )
        assert request.session_id == session_id

        # Invalid empty message
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_chat_response_creation(self):
        """Test ChatResponse model creation."""
        session_id = uuid4()
        response = ChatResponse(
            response="Great! Let's start with your WHY",
            session_id=session_id,
            current_phase=Phase.WHY,
            phase_complete=False,
            transition_available=False,
            session_complete=False,
            metadata={"agent": "WHY"},
        )

        assert response.session_id == session_id
        assert response.current_phase == Phase.WHY
        assert not response.phase_complete
        assert response.metadata["agent"] == "WHY"

    def test_phase_transition_request(self):
        """Test PhaseTransitionRequest model."""
        session_id = uuid4()
        request = PhaseTransitionRequest(
            session_id=session_id,
            target_phase=Phase.HOW,
            user_confirmation=True,
            reason="Ready to move forward",
        )

        assert request.session_id == session_id
        assert request.target_phase == Phase.HOW
        assert request.user_confirmation is True
        assert request.reason == "Ready to move forward"
