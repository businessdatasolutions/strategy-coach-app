from typing import TypedDict, List, Dict, Any, Optional, Literal
from langchain_core.messages import BaseMessage
from datetime import datetime


class AgentState(TypedDict):
    """
    The central state of the AI Strategic Co-pilot application.
    
    This state is passed between all agents in the LangGraph workflow and contains
    all necessary information for processing user conversations and managing
    the strategy development process.
    """
    
    # Core conversation data
    conversation_history: List[BaseMessage]
    strategy_map_path: str
    
    # Session management
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Current processing context
    current_phase: Literal["why", "how", "what", "review", "complete"]
    current_agent: Optional[str]
    agent_output: Optional[str]
    
    # Strategy development progress
    strategy_completeness: Dict[str, bool]
    identified_gaps: List[str]
    
    # User preferences and context
    user_context: Dict[str, Any]
    conversation_summary: Optional[str]
    
    # Processing metadata
    processing_stage: Optional[str]
    error_state: Optional[Dict[str, Any]]
    retry_count: int


class StrategyMapState(TypedDict):
    """
    Represents the current state of the strategy map being developed.
    This corresponds to the JSON structure maintained by the Strategy Map Agent.
    """
    
    # Metadata
    session_id: str
    created_at: str
    updated_at: str
    version: int
    
    # Core strategy components following the PRD structure
    why: Dict[str, Any]  # Purpose, belief, values from WHY Agent
    stakeholder_customer: Dict[str, Any]  # Value propositions from Strategy Map Agent
    internal_processes: Dict[str, Any]  # Core processes from Strategy Map Agent
    learning_growth: Dict[str, Any]  # Capabilities from Strategy Map Agent
    value_creation: Dict[str, Any]  # Six Value Components from Strategy Map Agent
    
    # Analysis components
    analogy_analysis: Optional[Dict[str, Any]]  # From Analogy Agent
    logical_structure: Optional[Dict[str, Any]]  # From Logic Agent
    implementation_plan: Optional[Dict[str, Any]]  # From Open Strategy Agent
    
    # Progress tracking
    completed_sections: List[str]
    completeness_percentage: float


class ConversationPhase(TypedDict):
    """
    Defines the current phase of the strategic conversation.
    Based on the three-phase journey from the PRD.
    """
    
    phase_name: Literal["why", "how", "what", "review", "complete"]
    phase_description: str
    active_agents: List[str]
    required_outputs: List[str]
    completion_criteria: Dict[str, Any]
    next_phase: Optional[str]


class AgentInput(TypedDict):
    """
    Standard input format for all specialist agents.
    """
    
    state: AgentState
    user_message: str
    conversation_context: List[BaseMessage]
    strategy_map_state: StrategyMapState
    phase_context: ConversationPhase


class AgentOutput(TypedDict):
    """
    Standard output format from all specialist agents.
    """
    
    agent_type: str
    response: str
    questions: List[str]
    topics_to_explore: List[str]
    strategy_updates: Dict[str, Any]
    confidence_score: float
    requires_followup: bool
    suggested_next_agent: Optional[str]


class RouterDecision(TypedDict):
    """
    Output from the orchestrator router to determine next action.
    """
    
    next_node: str
    reasoning: str
    priority: int
    context: Dict[str, Any]


class WorkflowConfig(TypedDict):
    """
    Configuration for the orchestrator workflow.
    """
    
    # Agent settings
    default_llm_provider: str
    default_model: str
    temperature: float
    max_tokens: int
    
    # Workflow behavior
    max_iterations: int
    conversation_timeout_minutes: int
    strategy_completion_threshold: float
    
    # Phase transitions
    phase_transition_rules: Dict[str, Any]
    agent_selection_strategy: str


# State update functions for type safety
def update_conversation_history(state: AgentState, message: BaseMessage) -> AgentState:
    """Add a message to the conversation history."""
    state["conversation_history"].append(message)
    state["updated_at"] = datetime.now()
    return state


def update_strategy_completeness(state: AgentState, section: str, completed: bool) -> AgentState:
    """Update the completeness status of a strategy section."""
    state["strategy_completeness"][section] = completed
    state["updated_at"] = datetime.now()
    return state


def transition_phase(state: AgentState, new_phase: Literal["why", "how", "what", "review", "complete"]) -> AgentState:
    """Transition to a new conversation phase."""
    state["current_phase"] = new_phase
    state["current_agent"] = None
    state["updated_at"] = datetime.now()
    return state


def set_processing_stage(state: AgentState, stage: str, agent: str = None) -> AgentState:
    """Set the current processing stage and active agent."""
    state["processing_stage"] = stage
    if agent:
        state["current_agent"] = agent
    state["updated_at"] = datetime.now()
    return state


def initialize_agent_state(
    session_id: str,
    strategy_map_path: str,
    user_id: str = None,
    user_context: Dict[str, Any] = None
) -> AgentState:
    """Initialize a new agent state for a session."""
    now = datetime.now()
    
    return AgentState(
        # Core conversation data
        conversation_history=[],
        strategy_map_path=strategy_map_path,
        
        # Session management
        session_id=session_id,
        user_id=user_id,
        created_at=now,
        updated_at=now,
        
        # Current processing context
        current_phase="why",
        current_agent=None,
        agent_output=None,
        
        # Strategy development progress
        strategy_completeness={
            "why": False,
            "stakeholder_customer": False,
            "internal_processes": False,
            "learning_growth": False,
            "value_creation": False,
            "analogy_analysis": False,
            "logical_structure": False,
            "implementation_plan": False
        },
        identified_gaps=[],
        
        # User preferences and context
        user_context=user_context or {},
        conversation_summary=None,
        
        # Processing metadata
        processing_stage="initialization",
        error_state=None,
        retry_count=0
    )


def calculate_strategy_completeness(state: AgentState) -> float:
    """Calculate the overall completeness percentage of the strategy."""
    completeness = state["strategy_completeness"]
    total_sections = len(completeness)
    completed_sections = sum(1 for completed in completeness.values() if completed)
    
    return (completed_sections / total_sections) * 100 if total_sections > 0 else 0.0