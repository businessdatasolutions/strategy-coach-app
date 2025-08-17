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
        graph_builder.add_node("how_agent", self._how_agent_node)
        graph_builder.add_node("what_agent", self._what_agent_node)

        # Add edges and routing logic
        graph_builder.add_edge(START, "why_agent")

        # Set up simple linear progression for now
        # This can be enhanced later with proper conversational loops
        graph_builder.add_edge("why_agent", "how_agent")
        graph_builder.add_edge("how_agent", "what_agent")
        graph_builder.add_edge("what_agent", END)

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

    def _how_agent_node(self, state: StrategyCoachState) -> dict:
        """
        HOW Agent Node - Strategic logic development using analogical reasoning.

        Placeholder implementation combining Analogy and Logic methodologies.
        """
        from .models import AnalogicalComparison, HOWStrategy, LogicalArgument

        messages = state.get("messages", [])
        interaction_count = state.get("interaction_count", 0)
        why_output = state.get("why_output")

        # Reset interaction count when entering new phase
        if state.get("current_phase") != "HOW":
            interaction_count = 0

        if interaction_count == 0:
            response_content = f"""Excellent! Now that we've clarified your WHY - "{why_output.why_statement if why_output else 'your core purpose'}" - let's explore HOW you'll deliver on this purpose.

I'd like to use analogical reasoning to develop your strategic approach. Can you think of another organization that has successfully achieved something similar to what you're trying to accomplish? Who would you consider a great example of success in your space or a related area?"""

        else:
            response_content = """Let's dive deeper into this analogy. What specifically about their approach led to their success? I want to understand not just what they did (the horizontal similarities), but WHY their approach worked (the vertical causal theory).

What's the underlying logic that made them successful? How can we apply that same causal theory to your unique situation?"""

        ai_message = AIMessage(content=response_content)

        state_updates = {
            "messages": [ai_message],
            "current_phase": "HOW",
            "interaction_count": interaction_count + 1,
            "phase_complete": interaction_count >= 3,
        }

        # Always add structured output for HOW phase (simplified for now)
        how_strategy = HOWStrategy(
            analogical_analysis=AnalogicalComparison(
                source_company="Example Company",
                target_company="User's Company",
                causal_theory="Innovation and customer focus drive market leadership",
                applied_theory="We can achieve leadership through customer-centric innovation",
            ),
            logical_validation=LogicalArgument(
                logical_connection="Customer focus connects our WHY to market success",
                deductive_reasoning="If we serve customers better than competitors, we win",
            ),
            core_strategic_theory="Customer-centric innovation strategy",
            strategic_approach="Differentiate through superior customer experience",
        )
        state_updates["how_output"] = how_strategy

        return state_updates

    def _what_agent_node(self, state: StrategyCoachState) -> dict:
        """
        WHAT Agent Node - Strategy mapping and implementation planning.

        Placeholder implementation combining Strategy Map and Open Strategy.
        """
        from .models import OpenStrategyPlan, WHATStrategy

        messages = state.get("messages", [])
        interaction_count = state.get("interaction_count", 0)
        why_output = state.get("why_output")
        how_output = state.get("how_output")

        # Reset interaction count when entering new phase
        if state.get("current_phase") != "WHAT":
            interaction_count = 0

        if interaction_count == 0:
            response_content = f"""Perfect! We've established your WHY ({why_output.why_statement if why_output else 'your purpose'}) and your HOW ({how_output.strategic_approach if how_output else 'your approach'}).

Now let's create your strategy map - the WHAT that brings everything together. We'll build this using four key perspectives:

1. **Value Creation**: What value will you create for stakeholders?
2. **Stakeholder**: Who are your key stakeholders and what do they need?
3. **Internal Processes**: What must you excel at internally?
4. **Learning & Growth**: What capabilities must you develop?

Let's start with your stakeholders. Who are the most important people or groups that your strategy must serve?"""

        else:
            response_content = """Excellent insights! Let's continue building your strategy map. 

Now let's think about implementation. Based on the Open Strategy approach, who should be involved in validating and implementing this strategy? Should we engage frontline employees, external experts, customers, or other stakeholders in the planning process?"""

        ai_message = AIMessage(content=response_content)

        state_updates = {
            "messages": [ai_message],
            "current_phase": "WHAT",
            "interaction_count": interaction_count + 1,
            "phase_complete": interaction_count >= 3,
        }

        # Always add structured output for WHAT phase (simplified for now)
        what_strategy = WHATStrategy(
            open_strategy_plan=OpenStrategyPlan(
                strategic_challenge="Implement customer-centric innovation strategy",
                strategy_phase="Strategy_Formulation",
                synthesis_plan="Synthesize stakeholder input into refined strategy",
                feedback_mechanism="Regular updates and collaborative reviews",
            ),
            strategy_summary="Complete strategy from WHY through implementation planning",
        )
        state_updates["what_output"] = what_strategy

        return state_updates

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
