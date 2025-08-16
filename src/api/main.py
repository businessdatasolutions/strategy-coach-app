"""
FastAPI application for the AI Strategic Co-pilot.

This module provides the REST API endpoints for the multi-agent strategy coaching system.
It handles conversation management, session initialization, and strategy map exports.
"""

import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio
import json

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from src.utils.config import get_config
from src.utils.logging_config import setup_logging
from src.models.state import AgentState, initialize_agent_state
from src.agents.orchestrator import StrategyCoachOrchestrator
from src.agents.strategy_map_agent import StrategyMapAgent
from src.api.middleware import (
    RateLimitMiddleware,
    RequestValidationMiddleware,
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    SessionValidationMiddleware
)
from langchain_core.messages import HumanMessage


# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize configuration
config = get_config()

# Initialize FastAPI app
app = FastAPI(
    title="AI Strategic Co-pilot API",
    description="""
## AI Strategic Co-pilot API

A sophisticated multi-agent workflow system that guides business leaders through developing organizational strategy using research-backed methodologies.

### Key Features

- 🎯 **Multi-Agent Architecture**: Specialized AI agents for different aspects of strategic planning
- 🔄 **Adaptive Conversations**: Dynamic routing based on conversation context and strategic needs
- 📊 **Persistent Strategy Maps**: JSON-based strategy tracking with Six Value Components
- 🚀 **Three-Phase Journey**: WHY → HOW → WHAT strategic development process

### Specialist Agents

1. **WHY Agent**: Discovers core purpose using Simon Sinek's Golden Circle
2. **Analogy Agent**: Strategic reasoning through Carroll & Sørensen's framework
3. **Logic Agent**: Validates strategic arguments using deductive reasoning
4. **Open Strategy Agent**: Implementation planning and stakeholder engagement

### API Sections

- **Conversation**: Core endpoints for strategic conversations
- **Sessions**: Session management and tracking
- **Export**: Strategy map export and download
- **Health**: Service monitoring and status

### Authentication

Currently using session-based management. API keys coming in v2.0.

### Rate Limits

- 60 requests per minute
- 1000 requests per hour

For more information, visit [GitHub Repository](https://github.com/your-org/strategy-coach)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "conversation",
            "description": "Strategic conversation management endpoints"
        },
        {
            "name": "sessions",
            "description": "Session lifecycle management"
        },
        {
            "name": "export",
            "description": "Strategy map export and download"
        },
        {
            "name": "health",
            "description": "Service health and monitoring"
        }
    ],
    contact={
        "name": "AI Strategic Co-pilot Team",
        "email": "support@strategy-coach.ai"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add middleware in order (last added = first executed)
# CORS should be added last to be executed first
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add custom middleware
app.add_middleware(SessionValidationMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(RateLimitMiddleware)

# Global instances
orchestrator = None
strategy_map_agent = None

# In-memory session store (in production, use Redis or database)
session_store: Dict[str, AgentState] = {}

# Session metadata store for management
session_metadata: Dict[str, Dict[str, Any]] = {}

# Background task to clean up expired sessions
cleanup_task: Optional[asyncio.Task] = None


# Pydantic models for request/response validation
class ConversationStartRequest(BaseModel):
    """Request model for starting a new conversation."""
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    user_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="User context including company info, industry, etc."
    )
    session_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata"
    )


class ConversationStartResponse(BaseModel):
    """Response model for conversation start."""
    session_id: str = Field(description="Unique session identifier")
    message: str = Field(description="Welcome message")
    current_phase: str = Field(description="Current conversation phase")
    next_steps: List[str] = Field(description="Suggested next steps")
    created_at: str = Field(description="Session creation timestamp")


class ConversationMessageRequest(BaseModel):
    """Request model for sending a message."""
    message: str = Field(min_length=1, max_length=5000, description="User message")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the message"
    )


class ConversationMessageResponse(BaseModel):
    """Response model for conversation message."""
    response: str = Field(description="AI response")
    current_phase: str = Field(description="Current conversation phase")
    current_agent: Optional[str] = Field(description="Active specialist agent")
    completeness_percentage: float = Field(description="Strategy completeness percentage")
    questions: List[str] = Field(description="Follow-up questions")
    recommendations: List[str] = Field(description="Strategic recommendations")
    session_id: str = Field(description="Session identifier")
    processing_stage: str = Field(description="Current processing stage")
    interactive_elements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Interactive UI elements for user selection"
    )
    awaiting_user_validation: Optional[bool] = Field(
        default=False,
        description="Whether the AI is waiting for user validation before proceeding"
    )


class ConversationExportResponse(BaseModel):
    """Response model for strategy export."""
    session_id: str = Field(description="Session identifier")
    strategy_map: Dict[str, Any] = Field(description="Complete strategy map")
    completeness_percentage: float = Field(description="Strategy completeness")
    export_timestamp: str = Field(description="Export generation timestamp")
    summary: Dict[str, Any] = Field(description="Strategy summary")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Health check timestamp")
    components: Dict[str, str] = Field(description="Component health status")


class SessionInfoResponse(BaseModel):
    """Response model for session information."""
    session_id: str = Field(description="Session identifier")
    created_at: str = Field(description="Session creation timestamp")
    updated_at: str = Field(description="Last update timestamp")
    current_phase: str = Field(description="Current conversation phase")
    completeness_percentage: float = Field(description="Strategy completeness")
    message_count: int = Field(description="Number of messages in conversation")
    strategy_map_path: str = Field(description="Path to strategy map file")
    user_context: Dict[str, Any] = Field(description="User context information")


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionInfoResponse] = Field(description="List of active sessions")
    total_sessions: int = Field(description="Total number of sessions")
    active_sessions: int = Field(description="Number of active sessions")


class SessionCleanupResponse(BaseModel):
    """Response model for session cleanup operations."""
    cleaned_sessions: int = Field(description="Number of sessions cleaned up")
    remaining_sessions: int = Field(description="Number of remaining sessions")
    cleanup_timestamp: str = Field(description="Cleanup operation timestamp")


# Dependency injection
def get_orchestrator() -> StrategyCoachOrchestrator:
    """Get the global orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        try:
            orchestrator = StrategyCoachOrchestrator()
            logger.info("Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize AI orchestrator"
            )
    return orchestrator


def get_strategy_map_agent() -> StrategyMapAgent:
    """Get the global strategy map agent instance."""
    global strategy_map_agent
    if strategy_map_agent is None:
        try:
            strategy_map_agent = StrategyMapAgent()
            logger.info("Strategy Map Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize strategy map agent: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize strategy map agent"
            )
    return strategy_map_agent


def get_session_state(session_id: str) -> AgentState:
    """
    Get session state from store.
    
    Args:
        session_id: Session identifier
        
    Returns:
        AgentState: Current session state
        
    Raises:
        HTTPException: If session not found
    """
    if session_id not in session_store:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found. Please start a new conversation."
        )
    return session_store[session_id]


def update_session_state(session_id: str, state: AgentState) -> None:
    """Update session state in store."""
    session_store[session_id] = state
    
    # Update session metadata
    if session_id not in session_metadata:
        session_metadata[session_id] = {}
    
    session_metadata[session_id].update({
        "updated_at": datetime.now().isoformat(),
        "current_phase": state["current_phase"],
        "message_count": len(state["conversation_history"]),
        "last_activity": datetime.now().isoformat()
    })


def create_session_metadata(session_id: str, state: AgentState) -> None:
    """Create initial session metadata."""
    session_metadata[session_id] = {
        "session_id": session_id,
        "created_at": state["created_at"].isoformat(),
        "updated_at": state["updated_at"].isoformat(),
        "current_phase": state["current_phase"],
        "message_count": len(state["conversation_history"]),
        "last_activity": datetime.now().isoformat(),
        "strategy_map_path": state["strategy_map_path"],
        "user_id": state.get("user_id"),
        "user_context": state["user_context"]
    }


def get_session_info(session_id: str, strategy_map_agent: StrategyMapAgent) -> SessionInfoResponse:
    """
    Get comprehensive session information.
    
    Args:
        session_id: Session identifier
        strategy_map_agent: Strategy map agent for completeness calculation
        
    Returns:
        SessionInfoResponse with session details
        
    Raises:
        HTTPException: If session not found
    """
    if session_id not in session_store or session_id not in session_metadata:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    state = session_store[session_id]
    metadata = session_metadata[session_id]
    
    # Get strategy map completeness
    completeness = 0.0
    try:
        strategy_map = strategy_map_agent.get_or_create_strategy_map(
            session_id=session_id,
            file_path=state["strategy_map_path"]
        )
        completeness = strategy_map.get("completeness_percentage", 0.0)
    except Exception as e:
        logger.warning(f"Could not load strategy map for session {session_id}: {e}")
    
    return SessionInfoResponse(
        session_id=session_id,
        created_at=metadata["created_at"],
        updated_at=metadata["updated_at"],
        current_phase=state["current_phase"],
        completeness_percentage=completeness,
        message_count=metadata["message_count"],
        strategy_map_path=state["strategy_map_path"],
        user_context=state["user_context"]
    )


def cleanup_expired_sessions() -> int:
    """
    Clean up expired sessions based on timeout configuration.
    
    Returns:
        Number of sessions cleaned up
    """
    timeout_minutes = config.session_timeout_minutes
    cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
    
    expired_sessions = []
    
    for session_id, metadata in session_metadata.items():
        try:
            last_activity = datetime.fromisoformat(metadata["last_activity"])
            if last_activity < cutoff_time:
                expired_sessions.append(session_id)
        except (KeyError, ValueError) as e:
            logger.warning(f"Invalid session metadata for {session_id}: {e}")
            expired_sessions.append(session_id)
    
    # Remove expired sessions
    cleaned_count = 0
    for session_id in expired_sessions:
        try:
            # Clean up session state
            session_store.pop(session_id, None)
            session_metadata.pop(session_id, None)
            
            # Optionally archive or delete strategy map files
            # For now, we'll keep the files for potential recovery
            
            cleaned_count += 1
            logger.info(f"Cleaned up expired session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")
    
    return cleaned_count


async def periodic_session_cleanup():
    """Background task for periodic session cleanup."""
    while True:
        try:
            # Run cleanup every hour
            await asyncio.sleep(3600)  # 1 hour
            
            cleaned = cleanup_expired_sessions()
            if cleaned > 0:
                logger.info(f"Periodic cleanup: removed {cleaned} expired sessions")
                
        except asyncio.CancelledError:
            logger.info("Session cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in periodic session cleanup: {e}")
            # Continue despite errors


def create_session_strategy_map_path(session_id: str) -> str:
    """Create the file path for a session's strategy map."""
    data_dir = Path(config.data_directory) / "sessions"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / f"{session_id}_strategy_map.json")


# API Endpoints

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring service availability.
    
    Returns:
        HealthResponse: Service health status and component information
    """
    try:
        # Test orchestrator availability
        orchestrator_status = "healthy"
        try:
            get_orchestrator()
        except Exception:
            orchestrator_status = "unhealthy"
        
        # Test data directory access
        data_dir_status = "healthy"
        try:
            data_dir = Path(config.data_directory)
            data_dir.mkdir(parents=True, exist_ok=True)
            if not data_dir.exists() or not os.access(data_dir, os.W_OK):
                data_dir_status = "unhealthy"
        except Exception:
            data_dir_status = "unhealthy"
        
        overall_status = "healthy" if all([
            orchestrator_status == "healthy",
            data_dir_status == "healthy"
        ]) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            components={
                "orchestrator": orchestrator_status,
                "data_directory": data_dir_status,
                "api": "healthy"
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Dict: Basic API information
    """
    return {
        "name": "AI Strategic Co-pilot API",
        "version": "1.0.0",
        "description": "Multi-agent workflow system for strategic business coaching",
        "docs_url": "/docs",
        "health_url": "/health"
    }


@app.post("/conversation/start", response_model=ConversationStartResponse, tags=["conversation"],
          summary="Start a new strategic conversation",
          response_description="Session details with welcome message")
async def start_conversation(
    request: ConversationStartRequest,
    orchestrator: StrategyCoachOrchestrator = Depends(get_orchestrator)
):
    """
    Start a new strategic conversation session.
    
    This endpoint initializes a new conversation session with a unique session ID,
    creates the initial strategy map, and provides a welcome message with next steps.
    
    Args:
        request: Conversation start request with optional user context
        orchestrator: The AI orchestrator dependency
    
    Returns:
        ConversationStartResponse: Session details and welcome message
    
    Raises:
        HTTPException: If session initialization fails
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create strategy map file path
        strategy_map_path = create_session_strategy_map_path(session_id)
        
        # Initialize agent state
        agent_state = initialize_agent_state(
            session_id=session_id,
            strategy_map_path=strategy_map_path,
            user_id=request.user_id,
            user_context=request.user_context
        )
        
        # Store session metadata if provided
        if request.session_metadata:
            agent_state["user_context"].update({
                "session_metadata": request.session_metadata
            })
        
        # Generate personalized welcome message based on user context
        welcome_message = _generate_welcome_message(request.user_context)
        
        # Define initial next steps
        next_steps = [
            "Share your organization's current strategic challenges",
            "Describe what you're trying to accomplish",
            "Tell me about your company and industry context",
            "Ask about our strategic coaching process"
        ]
        
        # Store the agent state and create metadata
        update_session_state(session_id, agent_state)
        create_session_metadata(session_id, agent_state)
        
        logger.info(f"Started new conversation session: {session_id}")
        
        return ConversationStartResponse(
            session_id=session_id,
            message=welcome_message,
            current_phase=agent_state["current_phase"],
            next_steps=next_steps,
            created_at=agent_state["created_at"].isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to start conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize conversation session: {str(e)}"
        )


def _generate_welcome_message(user_context: Dict[str, Any]) -> str:
    """
    Generate a personalized welcome message based on user context.
    
    Args:
        user_context: User context information
        
    Returns:
        str: Personalized welcome message
    """
    company_name = user_context.get("company_name", "your organization")
    industry = user_context.get("industry", "")
    team_size = user_context.get("team_size", "")
    
    # Base welcome message
    welcome = "Welcome to your AI Strategic Co-pilot! 🚀\n\n"
    
    # Personalize based on context
    if company_name != "your organization":
        welcome += f"I'm excited to help {company_name} develop a comprehensive strategic framework. "
    else:
        welcome += "I'm here to guide you through developing a comprehensive strategic framework for your organization. "
    
    if industry:
        welcome += f"With your focus in the {industry} industry, "
    
    if team_size:
        welcome += f"and your team size of {team_size}, "
    
    welcome += """we'll work together to:

✨ **Discover your WHY** - Core purpose, beliefs, and values using Simon Sinek's Golden Circle
🔍 **Analyze strategic patterns** - Learn from successful analogies using research-backed frameworks  
🧠 **Validate your logic** - Ensure sound strategic reasoning and decision-making
📋 **Plan implementation** - Create actionable roadmaps for strategy execution

Our conversation will evolve through three phases:
1. **WHY Phase** - Establishing your strategic foundation
2. **HOW Phase** - Developing strategic insights and validation  
3. **WHAT Phase** - Creating implementation plans and roadmaps

I'll adapt to your needs and provide personalized guidance throughout our journey. Everything we discuss will be captured in your persistent strategy map that you can export at any time.

What strategic challenge would you like to start with today?"""
    
    return welcome


@app.post("/conversation/{session_id}/message", response_model=ConversationMessageResponse, tags=["conversation"],
          summary="Send a message in an existing conversation",
          response_description="AI response with strategic guidance")
async def send_message(
    session_id: str,
    request: ConversationMessageRequest,
    background_tasks: BackgroundTasks,
    orchestrator: StrategyCoachOrchestrator = Depends(get_orchestrator),
    strategy_map_agent: StrategyMapAgent = Depends(get_strategy_map_agent)
):
    """
    Send a message in an existing conversation session.
    
    This endpoint processes user messages through the multi-agent orchestrator,
    updates the strategy map, and returns AI responses with strategic guidance.
    
    Args:
        session_id: Unique session identifier
        request: Message request with user input and context
        background_tasks: FastAPI background tasks for async operations
        orchestrator: The AI orchestrator dependency
        strategy_map_agent: Strategy map agent for persistence
    
    Returns:
        ConversationMessageResponse: AI response with session updates
    
    Raises:
        HTTPException: If session not found or processing fails
    """
    try:
        # Get current session state
        current_state = get_session_state(session_id)
        
        # Add user message to conversation history
        user_message = HumanMessage(content=request.message)
        current_state["conversation_history"].append(user_message)
        
        # Add any additional context
        if request.context:
            current_state["user_context"].update(request.context)
        
        # Process message through orchestrator
        logger.info(f"Processing message for session {session_id}: {request.message[:100]}...")
        
        # Use orchestrator to process the conversation
        updated_state = await _process_conversation_turn(
            state=current_state,
            orchestrator=orchestrator,
            user_message=request.message
        )
        
        # Load current strategy map for completeness calculation
        strategy_map = strategy_map_agent.get_or_create_strategy_map(
            session_id=session_id,
            file_path=updated_state["strategy_map_path"]
        )
        
        # Update session state
        update_session_state(session_id, updated_state)
        
        # Extract the AI response (last message in conversation history)
        ai_response = ""
        if updated_state["conversation_history"]:
            last_message = updated_state["conversation_history"][-1]
            if hasattr(last_message, 'content'):
                ai_response = last_message.content
        
        # Generate follow-up questions based on current phase and agent
        questions = _generate_followup_questions(updated_state, strategy_map)
        
        # Generate strategic recommendations
        validation_result = strategy_map_agent.validate_strategy_map(strategy_map)
        recommendations = validation_result.get("recommendations", [])
        
        # Schedule background strategy map update
        background_tasks.add_task(
            _update_strategy_map_background,
            strategy_map_agent,
            updated_state,
            session_id
        )
        
        logger.info(f"Processed message for session {session_id} - Phase: {updated_state['current_phase']}")
        
        # Check for interactive elements from agent and validate appropriateness
        interactive_elements = updated_state.get("interactive_elements")
        
        # Additional validation to prevent inappropriate interactive elements
        if interactive_elements and ai_response:
            if not _validate_interactive_element_appropriateness(ai_response, interactive_elements):
                logger.warning("Removing inappropriate interactive element from response")
                interactive_elements = None
        
        return ConversationMessageResponse(
            response=ai_response,
            current_phase=updated_state["current_phase"],
            current_agent=updated_state.get("current_agent"),
            completeness_percentage=strategy_map.get("completeness_percentage", 0.0),
            questions=questions,
            recommendations=recommendations[:3],  # Limit to top 3 recommendations
            session_id=session_id,
            processing_stage=updated_state.get("processing_stage", "completed"),
            interactive_elements=interactive_elements,
            awaiting_user_validation=updated_state.get("awaiting_user_validation", False)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to process message for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


async def _process_conversation_turn(
    state: AgentState,
    orchestrator: StrategyCoachOrchestrator,
    user_message: str
) -> AgentState:
    """
    Process a conversation turn through the orchestrator.
    
    Args:
        state: Current agent state
        orchestrator: The orchestrator instance
        user_message: User's message content
        
    Returns:
        AgentState: Updated state after processing
    """
    try:
        # Set processing stage
        state["processing_stage"] = "processing_message"
        
        # Process through orchestrator workflow
        # Note: This would use the actual orchestrator.process_message method
        # For now, we'll simulate the orchestrator behavior
        
        # Determine which agent should handle this message based on current phase and context
        from src.agents.router import AdvancedRouter
        router = AdvancedRouter()
        
        # Make routing decision
        routing_decision = router.make_routing_decision(state)
        next_agent = routing_decision["next_node"]
        
        # Process with appropriate agent
        if next_agent == "why_agent":
            from src.agents.why_agent import create_why_agent_node
            agent_node = create_why_agent_node()
            state = agent_node(state)
        elif next_agent == "analogy_agent":
            from src.agents.analogy_agent import create_analogy_agent_node
            agent_node = create_analogy_agent_node()
            state = agent_node(state)
        elif next_agent == "logic_agent":
            from src.agents.logic_agent import create_logic_agent_node
            agent_node = create_logic_agent_node()
            state = agent_node(state)
        elif next_agent == "open_strategy_agent":
            from src.agents.open_strategy_agent import create_open_strategy_agent_node
            agent_node = create_open_strategy_agent_node()
            state = agent_node(state)
        else:
            # Default fallback - use synthesis
            from src.agents.synthesizer import ConversationSynthesizer
            synthesizer = ConversationSynthesizer()
            response = synthesizer.synthesize_response(state)
            
            # Add AI response to conversation
            from langchain_core.messages import AIMessage
            ai_message = AIMessage(content=response)
            state["conversation_history"].append(ai_message)
        
        # Update processing stage
        state["processing_stage"] = "message_processed"
        state["updated_at"] = datetime.now()
        
        return state
        
    except Exception as e:
        logger.error(f"Error processing conversation turn: {e}")
        # Return state with error information
        state["error_state"] = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "occurred_at": datetime.now().isoformat()
        }
        state["processing_stage"] = "error"
        return state


def _generate_followup_questions(state: AgentState, strategy_map: dict) -> List[str]:
    """
    Generate contextual follow-up questions based on current state.
    
    Args:
        state: Current agent state
        strategy_map: Current strategy map
        
    Returns:
        List of follow-up questions
    """
    questions = []
    current_phase = state["current_phase"]
    completeness = strategy_map.get("completeness_percentage", 0.0)
    
    if current_phase == "why":
        if completeness < 20:
            questions = [
                "What is your organization's core purpose?",
                "What do you believe about your industry or customers?",
                "What values guide your decision-making?"
            ]
        else:
            questions = [
                "How do your values show up in daily operations?",
                "What unique beliefs set you apart from competitors?",
                "How would you refine your purpose statement?"
            ]
    elif current_phase == "how":
        questions = [
            "What companies or strategies inspire you?",
            "How do you currently validate strategic decisions?",
            "What patterns do you see in successful organizations?"
        ]
    elif current_phase == "what":
        questions = [
            "Who are the key stakeholders for implementation?",
            "What processes need to be established or changed?",
            "What resources will be required for execution?"
        ]
    else:
        # Default questions
        questions = [
            "What aspect of your strategy needs the most attention?",
            "How can we dive deeper into your strategic challenges?",
            "What outcomes are you hoping to achieve?"
        ]
    
    return questions[:3]  # Limit to 3 questions


async def _update_strategy_map_background(
    strategy_map_agent: StrategyMapAgent,
    state: AgentState,
    session_id: str
) -> None:
    """
    Background task to update strategy map based on conversation.
    
    Args:
        strategy_map_agent: Strategy map agent instance
        state: Current agent state
        session_id: Session identifier
    """
    try:
        # Load current strategy map
        strategy_map = strategy_map_agent.get_or_create_strategy_map(
            session_id=session_id,
            file_path=state["strategy_map_path"]
        )
        
        # Update based on current agent output if available
        current_agent = state.get("current_agent")
        agent_output = state.get("agent_output")
        
        if current_agent and agent_output:
            if current_agent == "why_agent":
                insights = strategy_map_agent._extract_why_insights(agent_output)
                strategy_map = strategy_map_agent.update_why_insights(strategy_map, insights)
            elif current_agent == "analogy_agent":
                insights = strategy_map_agent._extract_analogy_insights(agent_output)
                strategy_map = strategy_map_agent.update_analogy_insights(strategy_map, insights)
            elif current_agent == "logic_agent":
                insights = strategy_map_agent._extract_logic_insights(agent_output)
                strategy_map = strategy_map_agent.update_logic_insights(strategy_map, insights)
            elif current_agent == "open_strategy_agent":
                insights = strategy_map_agent._extract_implementation_insights(agent_output)
                strategy_map = strategy_map_agent.update_implementation_insights(strategy_map, insights)
        
        # Save updated strategy map
        strategy_map_agent.save_strategy_map(strategy_map, state["strategy_map_path"])
        
        logger.info(f"Background strategy map update completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Background strategy map update failed for session {session_id}: {e}")


@app.get("/sessions", response_model=SessionListResponse, tags=["sessions"],
         summary="List all active sessions")
async def list_sessions(
    strategy_map_agent: StrategyMapAgent = Depends(get_strategy_map_agent)
):
    """
    List all active conversation sessions.
    
    Returns:
        SessionListResponse: List of active sessions with metadata
    """
    try:
        sessions = []
        
        for session_id in session_store.keys():
            try:
                session_info = get_session_info(session_id, strategy_map_agent)
                sessions.append(session_info)
            except Exception as e:
                logger.warning(f"Could not retrieve info for session {session_id}: {e}")
        
        # Sort sessions by last activity (most recent first)
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        
        return SessionListResponse(
            sessions=sessions,
            total_sessions=len(sessions),
            active_sessions=len(sessions)
        )
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve session list"
        )


@app.get("/sessions/{session_id}", response_model=SessionInfoResponse, tags=["sessions"],
         summary="Get detailed session information")
async def get_session(
    session_id: str,
    strategy_map_agent: StrategyMapAgent = Depends(get_strategy_map_agent)
):
    """
    Get detailed information about a specific session.
    
    Args:
        session_id: Session identifier
        strategy_map_agent: Strategy map agent dependency
    
    Returns:
        SessionInfoResponse: Detailed session information
    """
    try:
        return get_session_info(session_id, strategy_map_agent)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session information: {str(e)}"
        )


@app.delete("/sessions/{session_id}", tags=["sessions"],
            summary="Delete a session")
async def delete_session(session_id: str):
    """
    Delete a conversation session and its associated data.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    try:
        if session_id not in session_store:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Get strategy map path before deletion
        state = session_store[session_id]
        strategy_map_path = state["strategy_map_path"]
        
        # Remove from stores
        session_store.pop(session_id, None)
        session_metadata.pop(session_id, None)
        
        # Optionally delete strategy map file
        # For safety, we'll keep the file but log the deletion
        logger.info(f"Session {session_id} deleted - Strategy map preserved at: {strategy_map_path}")
        
        return {
            "message": f"Session {session_id} deleted successfully",
            "session_id": session_id,
            "strategy_map_preserved": strategy_map_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@app.post("/sessions/cleanup", response_model=SessionCleanupResponse, tags=["sessions"],
          summary="Trigger manual session cleanup")
async def cleanup_sessions():
    """
    Manually trigger cleanup of expired sessions.
    
    Returns:
        SessionCleanupResponse: Cleanup operation results
    """
    try:
        cleaned_count = cleanup_expired_sessions()
        remaining_count = len(session_store)
        
        logger.info(f"Manual session cleanup: {cleaned_count} sessions cleaned, {remaining_count} remaining")
        
        return SessionCleanupResponse(
            cleaned_sessions=cleaned_count,
            remaining_sessions=remaining_count,
            cleanup_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup sessions: {str(e)}"
        )


@app.get("/conversation/{session_id}/export", response_model=ConversationExportResponse, tags=["export"],
         summary="Export complete strategy map",
         response_description="Strategy map with summary and recommendations")
async def export_strategy(
    session_id: str,
    strategy_map_agent: StrategyMapAgent = Depends(get_strategy_map_agent)
):
    """
    Export the complete strategy map for a conversation session.
    
    This endpoint retrieves the full strategy map JSON including all insights
    from specialist agents, value components, and strategic perspectives.
    
    Args:
        session_id: Session identifier
        strategy_map_agent: Strategy map agent dependency
    
    Returns:
        ConversationExportResponse: Complete strategy map with metadata
    
    Raises:
        HTTPException: If session not found or export fails
    """
    try:
        # Verify session exists
        if session_id not in session_store:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        state = session_store[session_id]
        
        # Load strategy map
        strategy_map = strategy_map_agent.get_or_create_strategy_map(
            session_id=session_id,
            file_path=state["strategy_map_path"]
        )
        
        # Validate strategy map
        validation_result = strategy_map_agent.validate_strategy_map(strategy_map)
        
        # Generate comprehensive summary
        summary = _generate_strategy_summary(strategy_map, validation_result)
        
        logger.info(f"Exported strategy for session {session_id} - {strategy_map['completeness_percentage']:.1f}% complete")
        
        return ConversationExportResponse(
            session_id=session_id,
            strategy_map=dict(strategy_map),
            completeness_percentage=strategy_map.get("completeness_percentage", 0.0),
            export_timestamp=datetime.now().isoformat(),
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export strategy for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export strategy: {str(e)}"
        )


@app.get("/conversation/{session_id}/export/download", tags=["export"],
         summary="Download strategy map as JSON file")
async def download_strategy(
    session_id: str,
    strategy_map_agent: StrategyMapAgent = Depends(get_strategy_map_agent)
):
    """
    Download the strategy map as a JSON file.
    
    Args:
        session_id: Session identifier
        strategy_map_agent: Strategy map agent dependency
    
    Returns:
        FileResponse: JSON file download
    
    Raises:
        HTTPException: If session not found or download fails
    """
    from fastapi.responses import FileResponse
    
    try:
        # Verify session exists
        if session_id not in session_store:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        state = session_store[session_id]
        strategy_map_path = state["strategy_map_path"]
        
        # Verify file exists
        if not os.path.exists(strategy_map_path):
            raise HTTPException(
                status_code=404,
                detail=f"Strategy map file not found for session {session_id}"
            )
        
        # Generate download filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategy_map_{session_id[:8]}_{timestamp}.json"
        
        logger.info(f"Downloading strategy map for session {session_id}")
        
        return FileResponse(
            path=strategy_map_path,
            media_type="application/json",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download strategy for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download strategy: {str(e)}"
        )


def _generate_strategy_summary(strategy_map: dict, validation_result: dict) -> dict:
    """
    Generate a comprehensive summary of the strategy map.
    
    Args:
        strategy_map: Complete strategy map
        validation_result: Validation results
    
    Returns:
        Dictionary containing strategy summary
    """
    summary = {
        "overview": {
            "completeness_percentage": strategy_map.get("completeness_percentage", 0.0),
            "consistency_score": validation_result.get("consistency_score", 0.0),
            "completed_sections": strategy_map.get("completed_sections", []),
            "total_sections": 8
        },
        "why_summary": {},
        "strategic_insights": {},
        "implementation_readiness": {},
        "recommendations": [],
        "next_steps": []
    }
    
    # WHY Summary
    why_section = strategy_map.get("why", {})
    if why_section.get("purpose"):
        summary["why_summary"] = {
            "purpose": why_section.get("purpose", ""),
            "core_beliefs": why_section.get("beliefs", [])[:3],  # Top 3 beliefs
            "core_values": why_section.get("values", [])[:3],  # Top 3 values
            "golden_circle_complete": why_section.get("golden_circle_complete", False)
        }
    
    # Strategic Insights
    insights = {}
    
    # Analogy insights
    if strategy_map.get("analogy_analysis"):
        analogy = strategy_map["analogy_analysis"]
        insights["analogical_patterns"] = {
            "source_domains": analogy.get("source_domains", [])[:3],
            "key_insights": analogy.get("strategic_insights", [])[:3]
        }
    
    # Logic insights
    if strategy_map.get("logical_structure"):
        logic = strategy_map["logical_structure"]
        insights["logical_validation"] = {
            "argument_structure": logic.get("argument_structure", "")[:200],  # First 200 chars
            "validity_status": "Valid" if logic.get("validity_assessment") else "Needs Review"
        }
    
    # Implementation insights
    if strategy_map.get("implementation_plan"):
        impl = strategy_map["implementation_plan"]
        insights["implementation_overview"] = {
            "key_stakeholders": impl.get("stakeholder_analysis", [])[:3],
            "roadmap_phases": len(impl.get("implementation_roadmap", []))
        }
    
    summary["strategic_insights"] = insights
    
    # Implementation Readiness
    completeness = strategy_map.get("completeness_percentage", 0.0)
    
    if completeness < 30:
        readiness_level = "Foundation Phase"
        readiness_description = "Focus on establishing core purpose and strategic foundation"
    elif completeness < 60:
        readiness_level = "Development Phase"
        readiness_description = "Strategic framework emerging, continue developing key components"
    elif completeness < 80:
        readiness_level = "Refinement Phase"
        readiness_description = "Strategy well-developed, focus on validation and implementation planning"
    else:
        readiness_level = "Execution Ready"
        readiness_description = "Strategy comprehensive and ready for implementation"
    
    summary["implementation_readiness"] = {
        "level": readiness_level,
        "description": readiness_description,
        "completeness": completeness
    }
    
    # Recommendations from validation
    summary["recommendations"] = validation_result.get("recommendations", [])[:5]
    
    # Next Steps based on current state
    next_steps = []
    
    if "why" not in strategy_map.get("completed_sections", []):
        next_steps.append("Complete WHY discovery to establish strategic foundation")
    
    if completeness < 50:
        next_steps.append("Develop stakeholder value propositions and internal processes")
    elif completeness < 80:
        next_steps.append("Validate strategic logic and create implementation roadmap")
    else:
        next_steps.append("Review strategy with key stakeholders and begin execution")
    
    # Add specific missing components
    if not strategy_map.get("analogy_analysis"):
        next_steps.append("Explore analogical insights from successful organizations")
    
    if not strategy_map.get("implementation_plan"):
        next_steps.append("Develop detailed implementation plan with timelines")
    
    summary["next_steps"] = next_steps[:3]  # Top 3 next steps
    
    return summary


def _validate_interactive_element_appropriateness(ai_response: str, interactive_elements: Dict[str, Any]) -> bool:
    """Validate if interactive elements are appropriate for the current AI response context."""
    
    if not ai_response or not interactive_elements:
        return False
    
    response_lower = ai_response.lower()
    
    # Block interactive elements ONLY during explicit validation/confirmation requests
    strict_validation_indicators = [
        "does this capture the essence",
        "does it inspire you and would it inspire others",
        "validation:",
        "transition to how:",
        "now that we've clarified your why"
    ]
    
    if any(indicator in response_lower for indicator in strict_validation_indicators):
        return False
    
    # Allow interactive elements in most other cases - let WHY Agent logic decide
    return True


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request data validation failed",
            "details": str(exc)
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": str(exc) if config.debug else "Contact system administrator"
        }
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting AI Strategic Co-pilot API")
    
    # Initialize data directory
    try:
        data_dir = Path(config.data_directory)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure sessions subdirectory exists
        sessions_dir = data_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)
        
        logger.info(f"Data directory initialized: {data_dir}")
        logger.info(f"Sessions directory: {sessions_dir}")
    except Exception as e:
        logger.error(f"Failed to initialize data directory: {e}")
        raise
    
    # Pre-initialize orchestrator and strategy map agent
    try:
        get_orchestrator()
        logger.info("Orchestrator pre-initialized successfully")
    except Exception as e:
        logger.warning(f"Orchestrator pre-initialization failed: {e}")
    
    try:
        get_strategy_map_agent()
        logger.info("Strategy Map Agent pre-initialized successfully")
    except Exception as e:
        logger.warning(f"Strategy Map Agent pre-initialization failed: {e}")
    
    # Start background session cleanup task
    global cleanup_task
    try:
        cleanup_task = asyncio.create_task(periodic_session_cleanup())
        logger.info("Session cleanup task started")
    except Exception as e:
        logger.error(f"Failed to start session cleanup task: {e}")
    
    logger.info("API startup completed successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down AI Strategic Co-pilot API")
    
    # Stop background cleanup task
    global cleanup_task
    if cleanup_task and not cleanup_task.done():
        try:
            cleanup_task.cancel()
            await cleanup_task
            logger.info("Session cleanup task stopped")
        except asyncio.CancelledError:
            logger.info("Session cleanup task cancelled")
        except Exception as e:
            logger.error(f"Error stopping session cleanup task: {e}")
    
    # Perform final session cleanup
    try:
        cleaned = cleanup_expired_sessions()
        logger.info(f"Final cleanup: {cleaned} sessions cleaned")
    except Exception as e:
        logger.error(f"Error in final session cleanup: {e}")
    
    # Clean up orchestrator if needed
    global orchestrator
    if orchestrator:
        try:
            # Perform any necessary cleanup
            pass
        except Exception as e:
            logger.error(f"Error during orchestrator cleanup: {e}")
    
    logger.info(f"API shutdown completed - {len(session_store)} sessions preserved")


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Configuration for development
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting development server on {host}:{port}")
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["src"],
        log_level="info"
    )