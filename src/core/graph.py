"""
Main LangGraph StateGraph implementation for the AI Strategic Co-pilot.

This module creates and compiles the StateGraph that manages the sequential
progression through WHY → HOW → WHAT phases using specialist agent nodes.
"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from .config import Settings, settings

# Routing imports removed - using simple linear progression for now
from .state import StrategyCoachState


class StrategyCoachGraph:
    """
    LangGraph-native implementation of the AI Strategic Co-pilot.

    Uses StateGraph with agent nodes and conditional edges for phase management.
    """

    def __init__(self, settings: Settings):
        """Initialize the strategy coach graph with configuration."""
        self.settings = settings

        # Initialize LLM based on configuration
        api_key = settings.get_llm_api_key()
        if not api_key:
            raise ValueError(
                f"No API key configured for LLM provider: {settings.llm_provider}"
            )

        self.llm = self._init_llm(settings)

        # Build and compile the graph
        self.graph = self._build_graph()

    def _init_llm(self, settings: Settings):
        """Initialize the LLM based on configuration."""
        provider_models = {
            "anthropic": "anthropic:claude-3-5-sonnet-latest",
            "openai": "openai:gpt-4",
            "google": "google_genai:gemini-2.0-flash",
        }

        model_name = provider_models.get(settings.llm_provider)
        if not model_name:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

        return init_chat_model(
            model_name, temperature=settings.temperature, max_tokens=settings.max_tokens
        )

    def _build_graph(self) -> StateGraph:
        """Build and compile the LangGraph StateGraph."""
        # Create the StateGraph
        graph_builder = StateGraph(StrategyCoachState)

        # Import and add agent nodes
        from ..agents.why_node import why_agent_node
        graph_builder.add_node("why_agent", why_agent_node)
        graph_builder.add_node("how_agent", self._placeholder_how_agent)
        graph_builder.add_node("what_agent", self._placeholder_what_agent)

        # Add edges and routing logic
        graph_builder.add_edge(START, "why_agent")

        # Use human-in-the-loop pattern with interrupts
        # Each agent processes one message then stops for user input
        graph_builder.add_conditional_edges(
            "why_agent",
            self._route_after_why,
            {
                "how_agent": "how_agent",    # Transition to HOW when ready
                "__end__": END               # End conversation
            }
        )
        
        graph_builder.add_conditional_edges(
            "how_agent",
            self._route_after_how,
            {
                "what_agent": "what_agent",  # Transition to WHAT when ready
                "__end__": END
            }
        )
        
        graph_builder.add_edge("what_agent", END)  # WHAT always ends

        # Configure checkpointer for session persistence
        if (
            hasattr(self.settings, "use_sqlite_checkpointer")
            and self.settings.use_sqlite_checkpointer
        ):
            # For production: use SqliteSaver
            from langgraph.checkpoint.sqlite import SqliteSaver

            checkpointer = SqliteSaver.from_conn_string("strategy_coach.db")
        else:
            # For development: use InMemorySaver
            checkpointer = InMemorySaver()

        # Compile the graph with checkpointer
        return graph_builder.compile(checkpointer=checkpointer)

    def _why_agent_node(self, state: StrategyCoachState) -> dict:
        """
        WHY Agent Node - Discovery of organizational purpose using Simon Sinek methodology.

        This is a placeholder implementation. The full implementation will be moved
        to src/agents/why_node.py following the LangGraph node pattern.
        """
        from .models import ActionableValue, CoreBelief, WHYStatement

        # Get conversation context
        messages = state.get("messages", [])
        current_phase = state.get("current_phase", "WHY")
        interaction_count = state.get("interaction_count", 0)

        # WHY agent methodology prompts
        if interaction_count == 0:
            # Welcome message for WHY phase
            response_content = """Welcome to your strategic journey! I'm here to help you discover your organization's WHY - the core purpose that drives everything you do.

Let's start with your origin story. Tell me about how your organization began. What problem were you originally trying to solve, and what motivated the founders to start this journey?"""

        elif interaction_count < 3:
            # Discovery phase - mine the past
            response_content = """That's fascinating. Let's dig deeper into your purpose. 

Think about moments when your organization felt most proud or successful. What were you doing? Who were you helping? What impact were you creating that felt most meaningful?"""

        else:
            # Synthesis phase - check for completion
            response_content = """Based on our conversation, I'm starting to see your core purpose emerging. 

It sounds like your WHY might be something like: "To give every [your beneficiary] access to [your solution], so they can [achieve their goal] without [common obstacle]."

Does this resonate with you? Are you ready to refine this into your final WHY statement and move to exploring HOW you'll achieve this purpose?"""

        # Create response message
        ai_message = AIMessage(content=response_content)

        # Update state
        state_updates = {
            "messages": [ai_message],
            "current_phase": "WHY",
            "interaction_count": interaction_count + 1,
            "phase_complete": interaction_count >= 3,  # Simple completion logic for now
        }

        # Always add structured output for WHY phase (simplified for now)
        from .models import ActionableValue, CoreBelief

        why_statement = WHYStatement(
            why_statement="To help every business leader access strategic clarity",
            core_beliefs=[
                CoreBelief(statement="Every leader deserves clear strategic direction")
            ],
            actionable_values=[
                ActionableValue(
                    value_name="Clarity",
                    action_phrase="Communicate with transparency",
                    explanation="We believe in clear, honest communication",
                )
            ],
            golden_circle_integration="Purpose drives behavior which creates results",
            primary_beneficiary="business leaders",
            key_outcome="strategic clarity",
        )
        state_updates["why_output"] = why_statement

        return state_updates

    def _placeholder_how_agent(self, state: StrategyCoachState) -> dict:
        """
        HOW Agent Node - Strategic logic development using analogical reasoning.

        Placeholder implementation combining Analogy and Logic methodologies.
        """
        why_output = state.get("why_output")
        
        response_content = f"""🚧 HOW Phase Not Yet Implemented

Excellent work completing your WHY phase! Your purpose: "{why_output.why_statement if why_output else 'Your core purpose'}" provides a strong foundation.

The HOW agent (Carroll & Sørensen analogical reasoning + logic validation) will be implemented in the next development phase.

For now, this validates your WHY phase completion. You can continue testing the WHY methodology or start a new session."""

        return {
            "messages": [AIMessage(content=response_content)],
            "current_phase": "HOW",
            "interaction_count": 1,
            "phase_complete": True
        }

    def _placeholder_what_agent(self, state: StrategyCoachState) -> dict:
        """Placeholder WHAT Agent - Not implemented yet."""
        why_output = state.get("why_output")
        
        response_content = f"""🚧 WHAT Phase Not Yet Implemented

Congratulations on completing your strategic foundation! 

Your WHY: "{why_output.why_statement if why_output else 'Your core purpose'}" is now clearly defined.

The WHAT agent (Kaplan & Norton Strategy Map + Open Strategy) will be implemented to create your complete strategy map.

This completes the current testing scope for WHY phase validation."""

        return {
            "messages": [AIMessage(content=response_content)],
            "current_phase": "WHAT",
            "interaction_count": 1,
            "phase_complete": True
        }
    
    def _route_after_why(self, state: StrategyCoachState) -> str:
        """Route after WHY agent - check if ready to transition to HOW."""
        why_output = state.get("why_output")
        messages = state.get("messages", [])
        
        # Check for explicit transition request
        if messages:
            latest_message = None
            for msg in reversed(messages):
                if hasattr(msg, 'type') and msg.type == "human":
                    latest_message = msg
                    break
            
            if latest_message:
                content = latest_message.content.lower()
                transition_keywords = [
                    "ready to move", "next phase", "move on", "proceed to",
                    "ready for how", "explore how", "transition to", "yes, i'm ready"
                ]
                
                if any(keyword in content for keyword in transition_keywords) and why_output:
                    return "how_agent"
        
        # Default: end conversation (no infinite loops)
        return "__end__"
    
    def _route_after_how(self, state: StrategyCoachState) -> str:
        """Route after HOW agent - check if ready to transition to WHAT."""
        how_output = state.get("how_output")
        messages = state.get("messages", [])
        
        # Check for explicit transition request
        if messages:
            latest_message = None
            for msg in reversed(messages):
                if hasattr(msg, 'type') and msg.type == "human":
                    latest_message = msg
                    break
            
            if latest_message and how_output:
                content = latest_message.content.lower()
                transition_keywords = [
                    "ready for what", "strategy map", "implementation", 
                    "move to what", "final phase"
                ]
                
                if any(keyword in content for keyword in transition_keywords):
                    return "what_agent"
        
        # Default: end conversation
        return "__end__"

    def invoke(self, input_data: dict, config: dict = None) -> dict:
        """Invoke the graph with input data and configuration."""
        return self.graph.invoke(input_data, config)

    def stream(self, input_data: dict, config: dict = None, **kwargs):
        """Stream the graph execution with real-time updates."""
        return self.graph.stream(input_data, config, **kwargs)

    def get_state(self, config: dict):
        """Get the current state for a given configuration."""
        return self.graph.get_state(config)

    def get_state_history(self, config: dict):
        """Get the state history for a given configuration."""
        return self.graph.get_state_history(config)


def create_strategy_coach_graph(config_settings: Settings = None) -> StrategyCoachGraph:
    """Factory function to create a configured StrategyCoachGraph."""
    if config_settings is None:
        config_settings = settings  # Use global settings instance

    return StrategyCoachGraph(config_settings)
