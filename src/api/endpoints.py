"""
FastAPI endpoints for the Strategy Coach LangGraph integration.

Provides REST and WebSocket endpoints that wrap LangGraph StateGraph
functionality for real-time strategy coaching sessions.
"""

import asyncio
import json
import logging
from typing import AsyncIterator, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from ..core.graph import create_strategy_coach_graph
from ..core.state import get_final_strategy_json, is_session_complete
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Global graph instance for this module
_graph_instance = None


def get_graph():
    """Get or create the graph instance."""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = create_strategy_coach_graph()
    return _graph_instance


# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model for API requests."""
    content: str = Field(..., min_length=1, description="Message content")
    thread_id: Optional[str] = Field(None, description="Session thread ID")


class ChatResponse(BaseModel):
    """Chat response model for API responses."""
    response: str = Field(..., description="Agent response")
    thread_id: str = Field(..., description="Session thread ID")
    current_phase: str = Field(..., description="Current strategy phase")
    phase_complete: bool = Field(..., description="Whether current phase is complete")
    session_complete: bool = Field(..., description="Whether entire session is complete")
    interaction_count: int = Field(..., description="Number of interactions in current phase")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")


class SessionInfo(BaseModel):
    """Session information model."""
    thread_id: str
    current_phase: str
    session_complete: bool
    total_messages: int
    why_complete: bool
    how_complete: bool
    what_complete: bool


class StrategyOutput(BaseModel):
    """Final strategy output model."""
    thread_id: str
    strategy_map: Dict
    metadata: Dict


# REST Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage) -> ChatResponse:
    """
    Process a chat message through the LangGraph StateGraph.
    
    This endpoint wraps graph.invoke() for single-turn interactions.
    """
    import time
    from langsmith import traceable
    
    start_time = time.time()
    
    try:
        graph = get_graph()
        
        # Generate thread_id if not provided
        thread_id = message.thread_id or f"session-{uuid4()}"
        
        # Prepare input for LangGraph
        graph_input = {
            "messages": [HumanMessage(content=message.content)],
            "current_phase": "WHY",  # Always start with WHY
            "interaction_count": 0,
            "methodology_stage": "welcome",  # Start with welcome stage
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {}
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get current state if session exists
        try:
            current_state = graph.get_state(config)
            if current_state and current_state.values:
                # Update existing state with new message
                existing_messages = current_state.values.get("messages", [])
                graph_input = {
                    **current_state.values,
                    "messages": existing_messages + [HumanMessage(content=message.content)]
                }
        except Exception:
            # New session - use initial input
            pass
        
        # Execute single step of the graph
        logger.info(f"🔍 Invoking graph with input keys: {list(graph_input.keys())}")
        result = graph.invoke(graph_input, config)
        
        # Calculate performance metrics
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        # Debug result
        logger.info(f"🔍 Graph result type: {type(result)}")
        if result:
            logger.info(f"🔍 Result keys: {list(result.keys())}")
        
        # Validate result
        if result is None:
            raise Exception("Graph returned None result")
        
        # Extract response information
        messages = result.get("messages", [])
        latest_message = messages[-1] if messages else None
        response_content = latest_message.content if latest_message else "No response generated"
        
        # Extract token usage if available
        token_usage = {}
        if latest_message and hasattr(latest_message, 'usage_metadata') and latest_message.usage_metadata:
            token_usage = {
                "input_tokens": latest_message.usage_metadata.get("input_tokens", 0),
                "output_tokens": latest_message.usage_metadata.get("output_tokens", 0),
                "total_tokens": latest_message.usage_metadata.get("total_tokens", 0)
            }
        
        # Log performance metrics for LangSmith monitoring
        logger.info(f"📊 API Performance: {response_time_ms}ms, tokens: {token_usage.get('total_tokens', 0)}, phase: {result.get('current_phase', 'WHY')}")
        
        return ChatResponse(
            response=response_content,
            thread_id=thread_id,
            current_phase=result.get("current_phase", "WHY"),
            phase_complete=result.get("phase_complete", False),
            session_complete=is_session_complete(result),
            interaction_count=result.get("interaction_count", 0),
            metadata={
                "total_messages": len(messages),
                "response_time_ms": response_time_ms,
                "token_usage": token_usage,
                "methodology_stage": result.get("methodology_stage", "unknown"),
                "phase_outputs": {
                    "why": result.get("why_output") is not None,
                    "how": result.get("how_output") is not None,
                    "what": result.get("what_output") is not None
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/session/{thread_id}", response_model=SessionInfo)
async def get_session_info(thread_id: str) -> SessionInfo:
    """Get information about a specific session."""
    try:
        graph = get_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get current state
        state = graph.get_state(config)
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Session not found")
        
        values = state.values
        
        return SessionInfo(
            thread_id=thread_id,
            current_phase=values.get("current_phase", "WHY"),
            session_complete=is_session_complete(values),
            total_messages=len(values.get("messages", [])),
            why_complete=values.get("why_output") is not None,
            how_complete=values.get("how_output") is not None,
            what_complete=values.get("what_output") is not None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session info error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")


@router.get("/session/{thread_id}/strategy", response_model=StrategyOutput)
async def get_strategy_output(thread_id: str) -> StrategyOutput:
    """Get the final strategy output for a completed session."""
    try:
        graph = get_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get current state
        state = graph.get_state(config)
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Session not found")
        
        values = state.values
        
        # Check if session is complete
        if not is_session_complete(values):
            raise HTTPException(status_code=400, detail="Session not complete")
        
        # Generate final strategy JSON
        strategy_json = get_final_strategy_json(values)
        if not strategy_json:
            raise HTTPException(status_code=500, detail="Could not generate strategy output")
        
        return StrategyOutput(
            thread_id=thread_id,
            strategy_map=strategy_json["strategy_map"],
            metadata=strategy_json["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strategy output error: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating strategy output: {str(e)}")


@router.get("/sessions", response_model=List[SessionInfo])
async def list_sessions() -> List[SessionInfo]:
    """List all active sessions (limited implementation for development)."""
    # Note: This is a simplified implementation
    # In production, you'd need to track sessions in the checkpointer
    return []


# WebSocket for Real-time Streaming

@router.websocket("/ws/{thread_id}")
async def websocket_chat(websocket: WebSocket, thread_id: str):
    """
    WebSocket endpoint for real-time streaming conversations.
    
    This endpoint wraps graph.stream() for live conversation updates.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for thread: {thread_id}")
    
    try:
        graph = get_graph()
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                await websocket.send_json({"error": "Empty message"})
                continue
            
            # Prepare input for LangGraph
            config = {"configurable": {"thread_id": thread_id}}
            
            # Get current state or create new
            try:
                current_state = graph.get_state(config)
                if current_state and current_state.values:
                    # Update existing session
                    existing_messages = current_state.values.get("messages", [])
                    graph_input = {
                        **current_state.values,
                        "messages": existing_messages + [HumanMessage(content=user_message)]
                    }
                else:
                    # New session
                    graph_input = {
                        "messages": [HumanMessage(content=user_message)],
                        "current_phase": "WHY",
                        "interaction_count": 0,
                        "phase_complete": False,
                        "why_output": None,
                        "how_output": None,
                        "what_output": None,
                        "user_context": {}
                    }
            except Exception:
                # Fallback to new session
                graph_input = {
                    "messages": [HumanMessage(content=user_message)],
                    "current_phase": "WHY",
                    "interaction_count": 0,
                    "phase_complete": False,
                    "why_output": None,
                    "how_output": None,
                    "what_output": None,
                    "user_context": {}
                }
            
            # Stream the graph execution
            try:
                async for event in graph.astream(graph_input, config, stream_mode="values"):
                    # Send real-time updates to client
                    messages = event.get("messages", [])
                    latest_message = messages[-1] if messages else None
                    
                    if latest_message and hasattr(latest_message, 'content'):
                        response_data = {
                            "type": "message",
                            "content": latest_message.content,
                            "thread_id": thread_id,
                            "current_phase": event.get("current_phase", "WHY"),
                            "phase_complete": event.get("phase_complete", False),
                            "session_complete": is_session_complete(event),
                            "interaction_count": event.get("interaction_count", 0),
                            "metadata": {
                                "why_complete": event.get("why_output") is not None,
                                "how_complete": event.get("how_output") is not None,
                                "what_complete": event.get("what_output") is not None
                            }
                        }
                        
                        await websocket.send_json(response_data)
                
                # Send completion notification if session is complete
                final_state = graph.get_state(config)
                if final_state and is_session_complete(final_state.values):
                    await websocket.send_json({
                        "type": "session_complete",
                        "thread_id": thread_id,
                        "message": "🎉 Strategy development complete! Your strategy map is ready."
                    })
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": f"Error processing message: {str(e)}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for thread: {thread_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error", 
                "error": f"WebSocket error: {str(e)}"
            })
        except:
            pass  # Client may have disconnected


# Additional utility endpoints

@router.get("/debug/graph")
async def debug_graph_structure():
    """Debug endpoint to inspect graph structure."""
    try:
        graph = get_graph()
        
        # Get graph structure information
        return {
            "nodes": list(graph.graph.nodes.keys()),
            "checkpointer_type": type(graph.graph.checkpointer).__name__,
            "configuration": {
                "llm_provider": settings.llm_provider,
                "model": settings.default_model,
                "temperature": settings.temperature
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")


@router.post("/debug/test-why-agent")
async def debug_test_why_agent(message: ChatMessage):
    """Debug endpoint to test WHY agent directly."""
    try:
        from ..agents.why_node import why_agent_node
        
        # Create test state
        test_state = {
            "messages": [HumanMessage(content=message.content)],
            "current_phase": "WHY",
            "interaction_count": 0,
            "phase_complete": False,
            "why_output": None,
            "how_output": None,
            "what_output": None,
            "user_context": {}
        }
        
        # Call WHY agent directly
        result = why_agent_node(test_state)
        
        return {
            "agent_response": result["messages"][0].content if result["messages"] else "No response",
            "phase": result["current_phase"],
            "interaction_count": result["interaction_count"],
            "phase_complete": result["phase_complete"],
            "why_output_generated": result.get("why_output") is not None
        }
        
    except Exception as e:
        logger.error(f"WHY agent test error: {e}")
        raise HTTPException(status_code=500, detail=f"WHY agent test error: {str(e)}")


# Add method to support async streaming
def _convert_to_async_iterator(sync_iterator) -> AsyncIterator:
    """Convert sync iterator to async iterator for WebSocket streaming."""
    for item in sync_iterator:
        yield item