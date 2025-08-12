from typing import Dict, Any, Literal
import logging

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from ..models.state import (
    AgentState,
    RouterDecision,
    calculate_strategy_completeness,
    transition_phase,
    set_processing_stage
)
from ..utils import get_logger, log_error_with_context
from .router import AdvancedRouter
from .synthesizer import ConversationSynthesizer
from .why_agent import create_why_agent_node
from .analogy_agent import create_analogy_agent_node
from .logic_agent import create_logic_agent_node
from .open_strategy_agent import create_open_strategy_agent_node


logger = get_logger(__name__)


class StrategyCoachOrchestrator:
    """
    Central orchestrator for the AI Strategic Co-pilot.
    
    Manages the workflow between different specialist agents using LangGraph,
    following the three-phase journey defined in the PRD:
    1. "Why" Phase - Core purpose discovery
    2. "How" Phase - Strategy development  
    3. "What" Phase - Implementation planning
    """
    
    def __init__(self):
        """Initialize the orchestrator with the LangGraph workflow."""
        self.router = AdvancedRouter()
        self.synthesizer = ConversationSynthesizer()
        self.why_agent_node = create_why_agent_node()
        self.analogy_agent_node = create_analogy_agent_node()
        self.logic_agent_node = create_logic_agent_node()
        self.open_strategy_agent_node = create_open_strategy_agent_node()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        logger.info("Strategy Coach Orchestrator initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph StateGraph workflow."""
        logger.info("Building orchestrator workflow")
        
        workflow = StateGraph(AgentState)
        
        # Add all nodes
        workflow.add_node("strategy_map_updater", self._strategy_map_updater_node)
        workflow.add_node("router", self._router_node)
        workflow.add_node("why_agent", self.why_agent_node)
        workflow.add_node("analogy_agent", self.analogy_agent_node)
        workflow.add_node("logic_agent", self.logic_agent_node)
        workflow.add_node("open_strategy_agent", self.open_strategy_agent_node)
        workflow.add_node("strategy_map_agent", self._strategy_map_agent_node)
        workflow.add_node("conversation_synthesizer", self._conversation_synthesizer_node)
        
        # Set entry point
        workflow.set_entry_point("strategy_map_updater")
        
        # Define the main workflow edges
        workflow.add_edge("strategy_map_updater", "router")
        
        # Router decides which specialist agent to invoke
        workflow.add_conditional_edges(
            "router",
            self._route_to_agent,
            {
                "why_agent": "why_agent",
                "analogy_agent": "analogy_agent", 
                "logic_agent": "logic_agent",
                "open_strategy_agent": "open_strategy_agent",
                "strategy_map_agent": "strategy_map_agent",
                "synthesize": "conversation_synthesizer",
                "end": END
            }
        )
        
        # All specialist agents flow to synthesizer
        workflow.add_edge("why_agent", "conversation_synthesizer")
        workflow.add_edge("analogy_agent", "conversation_synthesizer")
        workflow.add_edge("logic_agent", "conversation_synthesizer")
        workflow.add_edge("open_strategy_agent", "conversation_synthesizer")
        workflow.add_edge("strategy_map_agent", "conversation_synthesizer")
        
        # Synthesizer can loop back to strategy map updater for continued processing
        workflow.add_conditional_edges(
            "conversation_synthesizer",
            self._synthesizer_decision,
            {
                "continue": "strategy_map_updater",
                "end": END
            }
        )
        
        logger.info("Orchestrator workflow built successfully")
        return workflow
    
    async def process_user_message(self, state: AgentState, user_message: str) -> AgentState:
        """
        Process a user message through the orchestrator workflow.
        
        Args:
            state: Current agent state
            user_message: User's input message
            
        Returns:
            Updated agent state with response
        """
        logger.info(f"Processing user message for session {state['session_id']}")
        
        try:
            # Add user message to conversation history
            human_message = HumanMessage(content=user_message)
            state["conversation_history"].append(human_message)
            
            # Set processing stage
            state = set_processing_stage(state, "processing_user_input")
            
            # Run through the workflow
            result = await self.app.ainvoke(state)
            
            logger.info(f"Successfully processed message for session {result['session_id']}")
            return result
            
        except Exception as e:
            log_error_with_context(
                error=e,
                context={
                    "session_id": state["session_id"],
                    "operation": "process_user_message",
                    "user_message_length": len(user_message),
                    "current_phase": state["current_phase"]
                },
                logger_name=__name__
            )
            
            # Set error state
            state["error_state"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "retry_count": state["retry_count"] + 1
            }
            state["retry_count"] += 1
            
            return state
    
    def _strategy_map_updater_node(self, state: AgentState) -> AgentState:
        """
        Strategy Map Agent node - reads, updates, and writes strategy JSON.
        This runs at the start of each processing cycle.
        """
        logger.info(f"Updating strategy map for session {state['session_id']}")
        
        try:
            state = set_processing_stage(state, "updating_strategy_map", "strategy_map_agent")
            
            # TODO: Implement actual strategy map reading/writing
            # For now, we'll just update the processing stage
            logger.debug("Strategy map update completed (placeholder)")
            
            return state
            
        except Exception as e:
            log_error_with_context(e, {"session_id": state["session_id"], "node": "strategy_map_updater"})
            state["error_state"] = {"error": str(e), "node": "strategy_map_updater"}
            return state
    
    def _router_node(self, state: AgentState) -> AgentState:
        """
        Router node - determines which specialist agent should handle the current state.
        Uses the advanced router with sophisticated user intent analysis.
        """
        logger.info(f"Routing decision for session {state['session_id']}")
        
        try:
            state = set_processing_stage(state, "routing_decision", "router")
            
            # Use the advanced router to make the decision
            router_decision = self.router.make_routing_decision(state)
            state["agent_output"] = router_decision["next_node"]
            state["routing_context"] = router_decision["context"]
            
            logger.info(f"Advanced router decision: {router_decision['next_node']} - {router_decision['reasoning']}")
            return state
            
        except Exception as e:
            log_error_with_context(e, {"session_id": state["session_id"], "node": "router"})
            state["error_state"] = {"error": str(e), "node": "router"}
            return state
    
    def _route_to_agent(self, state: AgentState) -> str:
        """
        Conditional edge function to determine routing from router node.
        """
        if state.get("error_state"):
            return "end"
        
        # Get the routing decision stored by router_node
        next_agent = state.get("agent_output", "end")
        
        logger.debug(f"Conditional routing to: {next_agent}")
        return next_agent
    
    def _strategy_map_agent_node(self, state: AgentState) -> AgentState:
        """Placeholder for Strategy Map Agent node."""
        logger.info("Strategy Map Agent processing (placeholder)")
        state = set_processing_stage(state, "strategy_map_agent_processing", "strategy_map_agent")
        # TODO: Implement actual Strategy Map Agent logic
        return state
    
    # Placeholder specialist agent nodes - to be implemented in subsequent tasks
    
    
    
    
    def _conversation_synthesizer_node(self, state: AgentState) -> AgentState:
        """
        Synthesizer node - creates final response from agent outputs using advanced synthesis logic.
        """
        logger.info(f"Synthesizing conversation response for session {state['session_id']}")
        
        try:
            state = set_processing_stage(state, "synthesizing_response", "conversation_synthesizer")
            
            # Check if router recommended a phase transition
            routing_context = state.get("routing_context", {})
            recommended_phase = routing_context.get("recommended_phase")
            current_phase = state["current_phase"]
            
            # Apply phase transition if recommended
            if recommended_phase and recommended_phase != current_phase:
                logger.info(f"Transitioning phase from {current_phase} to {recommended_phase}")
                state = transition_phase(state, recommended_phase)
            
            # Use the advanced synthesizer to create a coherent response
            response = self.synthesizer.synthesize_response(state)
            
            # Add the AI response to conversation history
            ai_message = AIMessage(content=response)
            state["conversation_history"].append(ai_message)
            state["agent_output"] = response
            
            # Update processing metadata
            state["last_synthesis_turn"] = len(state["conversation_history"])
            state["response_length"] = len(response)
            
            logger.info(f"Advanced response synthesis completed ({len(response)} chars)")
            return state
            
        except Exception as e:
            log_error_with_context(e, {"session_id": state["session_id"], "node": "synthesizer"})
            state["error_state"] = {"error": str(e), "node": "synthesizer"}
            
            # Fallback to simple response in case of synthesis error
            fallback_response = "I'm working on your strategy development. Let me ask you some questions to better understand your needs."
            ai_message = AIMessage(content=fallback_response)
            state["conversation_history"].append(ai_message)
            state["agent_output"] = fallback_response
            
            return state
    
    def _synthesizer_decision(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Decision function for synthesizer - continue processing or end.
        """
        # Check if there are errors
        if state.get("error_state"):
            return "end"
        
        # Check if strategy is complete
        completeness = calculate_strategy_completeness(state)
        if completeness >= 95:
            logger.info(f"Strategy {completeness:.1f}% complete, ending session")
            return "end"
        
        # Check if we've exceeded retry limits
        if state["retry_count"] > 5:
            logger.warning(f"Retry limit exceeded for session {state['session_id']}")
            return "end"
        
        # Continue processing
        logger.debug("Continuing processing cycle")
        return "continue"