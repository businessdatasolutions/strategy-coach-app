"""
WHY Agent Node - Simon Sinek "Start with Why" methodology implementation.

This module implements the WHY phase agent as a LangGraph node function,
guiding users through discovery of their organizational core purpose using
the Golden Circle framework.
"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from ..core.config import settings
from ..core.models import WHYStatement
from ..core.state import StrategyCoachState


class WHYAgentNode:
    """
    WHY Agent implementation using Simon Sinek's 'Start with Why' methodology.

    Guides users through the Golden Circle framework to discover authentic
    organizational purpose through Socratic questioning.
    """

    def __init__(self, llm=None):
        """Initialize the WHY agent with LLM configuration."""
        self.llm = llm or init_chat_model(
            f"{settings.llm_provider}:{settings.default_model}",
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

        # Configure LLM for structured output
        self.structured_llm = self.llm.with_structured_output(WHYStatement)

        # WHY methodology prompts based on Simon Sinek framework
        self.prompts = {
            "welcome": """Welcome to your strategic journey! I'm your WHY coach, here to help you discover your organization's authentic core purpose using Simon Sinek's 'Start with Why' methodology.

The WHY is not what you do or how you do it - it's WHY you exist. It's your core belief, your purpose, your cause. It's what inspires you and should inspire others to join your cause.

Let's begin with your origin story. Tell me about how your organization started. What problem were you originally trying to solve? What drove the founders to take action?""",
            "discovery": """Thank you for sharing that. Now let's dig deeper into your authentic WHY.

Think about the moments when your organization felt most proud, most successful, or most fulfilled. These weren't necessarily your biggest revenue days, but the times when you felt you were truly making the difference you set out to make.

What were you doing in those moments? Who were you helping? What specific impact were you creating that felt most meaningful to you?""",
            "mining_beliefs": """I can sense the passion in what you're sharing. Let's explore the core beliefs that drive this passion.

What do you believe about {primary_beneficiary} that others might not see or understand? What injustice or missed opportunity in the world keeps you motivated to do this work?

Complete this sentence: "Every {primary_beneficiary} deserves..." What comes after that for you?""",
            "distilling_why": """Based on everything you've shared, I can see a powerful WHY emerging. Let me help you distill this into Simon Sinek's WHY format.

Your WHY seems to be: "To {core_action} every {primary_beneficiary} access to {key_resource}, so they can {achieve_goal} without {common_obstacle}."

Does this capture the essence of why your organization exists? What feels authentic here, and what might need refinement?""",
            "values_definition": """Perfect! Now that we have your WHY, let's define the HOWs - these are your core values, but expressed as actionable verbs, not just words on a wall.

Instead of saying 'integrity' (a noun), we say 'act with integrity' (a verb). Instead of 'innovation', we say 'challenge conventional thinking.'

Based on your WHY and what you've shared, what are 3-5 actionable behaviors that guide how you operate? What verbs describe how you live your WHY daily?""",
            "golden_circle_integration": """Excellent! Let's integrate everything into your complete Golden Circle.

Your WHY creates a clear mission: You exist to {why_statement} because you believe {core_beliefs}. This manifests in behaviors like {key_values}. This creates a business model where your own {proof_point} becomes proof that your approach works.

Does this feel authentic to your daily reality? Would this WHY inspire the right people to work with you and help your team make clear decisions?""",
            "transition_readiness": """Outstanding work! We've built a strong foundation with your WHY:

**YOUR WHY**: {why_statement}
**CORE BELIEFS**: {beliefs_summary}  
**GUIDING VALUES**: {values_summary}

This authentic purpose will be the foundation for everything we build next. 

Are you satisfied with this WHY foundation, or would you like to refine it further before we explore HOW you'll bring this purpose to life in the world?""",
        }

    def __call__(self, state: StrategyCoachState) -> dict:
        """
        Main node function following LangGraph pattern.

        Processes the current state and returns state updates following
        Simon Sinek's WHY discovery methodology.
        """
        messages = state.get("messages", [])
        interaction_count = state.get("interaction_count", 0)
        why_output = state.get("why_output")

        # Determine current stage in WHY methodology
        stage = self._determine_why_stage(messages, interaction_count, why_output)

        # Generate response based on methodology stage
        if stage == "welcome":
            response = self._handle_welcome_stage(state)
        elif stage == "discovery":
            response = self._handle_discovery_stage(state)
        elif stage == "mining_beliefs":
            response = self._handle_beliefs_stage(state)
        elif stage == "distilling_why":
            response = self._handle_distilling_stage(state)
        elif stage == "values_definition":
            response = self._handle_values_stage(state)
        elif stage == "integration":
            response = self._handle_integration_stage(state)
        elif stage == "completion_check":
            response = self._handle_completion_stage(state)
        elif stage == "transition_readiness":
            response = self._handle_completion_stage(state)  # Same as completion
        else:
            response = self._handle_continuation_stage(state)

        # Check if phase is ready for transition
        phase_complete = self._check_phase_completion(state, response)

        # Extract structured output if available
        new_why_output = why_output
        if hasattr(response, "structured_output"):
            new_why_output = response.structured_output

        return {
            "messages": [response],
            "current_phase": "WHY",
            "interaction_count": interaction_count + 1,
            "phase_complete": phase_complete,
            "why_output": new_why_output,
        }

    def _determine_why_stage(
        self, messages: list, interaction_count: int, why_output
    ) -> str:
        """Determine the current stage in the WHY discovery process."""
        if interaction_count == 0:
            return "welcome"
        elif interaction_count <= 2:
            return "discovery"
        elif interaction_count <= 4:
            return "mining_beliefs"
        elif interaction_count <= 6:
            return "distilling_why"
        elif interaction_count == 7 and why_output is None:
            return "completion_check"  # Trigger structured output generation
        elif interaction_count <= 8:
            return "values_definition"
        elif interaction_count <= 10:
            return "integration"
        else:
            return "transition_readiness"

    def _handle_welcome_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle the welcome stage with origin story prompting."""
        _ = state  # Suppress unused parameter warning
        return AIMessage(content=self.prompts["welcome"])

    def _handle_discovery_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle the discovery stage with deeper purpose exploration."""
        _ = state  # Suppress unused parameter warning
        return AIMessage(content=self.prompts["discovery"])

    def _handle_beliefs_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle core beliefs mining stage."""
        # Extract primary beneficiary from conversation
        beneficiary = self._extract_beneficiary(state.get("messages", []))
        prompt_content = self.prompts["mining_beliefs"].format(
            primary_beneficiary=beneficiary or "your customers"
        )
        return AIMessage(content=prompt_content)

    def _handle_distilling_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle WHY statement distillation stage."""
        # Extract key elements from conversation
        elements = self._extract_why_elements(state.get("messages", []))
        prompt_content = self.prompts["distilling_why"].format(**elements)
        return AIMessage(content=prompt_content)

    def _handle_values_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle actionable values definition stage."""
        _ = state  # Suppress unused parameter warning
        return AIMessage(content=self.prompts["values_definition"])

    def _handle_integration_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle Golden Circle integration stage."""
        elements = self._extract_integration_elements(state.get("messages", []))
        prompt_content = self.prompts["golden_circle_integration"].format(**elements)
        return AIMessage(content=prompt_content)

    def _handle_completion_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle phase completion and structured output generation."""
        # Use structured LLM to generate final WHYStatement
        try:
            # Create synthesis prompt for structured output
            synthesis_prompt = self._create_synthesis_prompt(state)
            structured_output = self.structured_llm.invoke(synthesis_prompt)

            # Create completion message with structured output
            elements = {
                "why_statement": structured_output.why_statement,
                "beliefs_summary": ", ".join(
                    [b.statement for b in structured_output.core_beliefs]
                ),
                "values_summary": ", ".join(
                    [v.action_phrase for v in structured_output.actionable_values]
                ),
            }

            completion_message = self.prompts["transition_readiness"].format(**elements)
            response = AIMessage(content=completion_message)
            response.structured_output = structured_output
            return response

        except Exception:
            # Fallback to manual completion if structured output fails
            return AIMessage(
                content="Let's continue refining your WHY. Tell me more about your core purpose."
            )

    def _handle_continuation_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle continuation when user needs more exploration."""
        _ = state  # Suppress unused parameter warning
        return AIMessage(
            content="""Let's continue exploring your WHY. 

What aspect of your organization's purpose would you like to dive deeper into? Is there something about your core beliefs or values that we should clarify further?"""
        )

    def _check_phase_completion(
        self, state: StrategyCoachState, response: AIMessage
    ) -> bool:
        """Check if the WHY phase is complete and ready for transition."""
        interaction_count = state.get("interaction_count", 0)
        has_structured_output = hasattr(response, "structured_output")
        existing_why_output = state.get("why_output") is not None

        # Phase is complete if we have structured output and sufficient interactions
        return interaction_count >= 7 and (has_structured_output or existing_why_output)

    def _extract_beneficiary(self, messages: list) -> str:
        """Extract primary beneficiary from conversation messages."""
        # Simple extraction - in production this would use NLP
        for message in messages:
            if hasattr(message, "type") and message.type == "human":
                content = message.content.lower()

                # Look for common beneficiary patterns
                beneficiary_patterns = [
                    "customers",
                    "clients",
                    "users",
                    "employees",
                    "students",
                    "patients",
                    "entrepreneurs",
                    "leaders",
                    "teams",
                    "organizations",
                ]

                for pattern in beneficiary_patterns:
                    if pattern in content:
                        return pattern

        return "people"

    def _extract_why_elements(self, messages: list) -> dict:
        """Extract key elements for WHY statement formation."""
        # Simplified extraction - production would use sophisticated NLP
        return {
            "core_action": "empower",
            "primary_beneficiary": self._extract_beneficiary(messages),
            "key_resource": "strategic clarity",
            "achieve_goal": "succeed",
            "common_obstacle": "confusion and uncertainty",
        }

    def _extract_integration_elements(self, messages: list) -> dict:
        """Extract elements for Golden Circle integration."""
        beneficiary = self._extract_beneficiary(messages)
        return {
            "why_statement": f"help every {beneficiary} succeed",
            "core_beliefs": f"{beneficiary} deserve clarity and support",
            "key_values": "transparency, empowerment, excellence",
            "proof_point": "organizational success and client satisfaction",
        }

    def _create_synthesis_prompt(self, state: StrategyCoachState) -> list[BaseMessage]:
        """Create a prompt for structured WHY output generation."""
        messages = state.get("messages", [])

        # Extract conversation context for synthesis
        user_inputs = [
            msg.content
            for msg in messages
            if hasattr(msg, "type") and msg.type == "human"
        ]

        conversation_summary = " ".join(user_inputs[:3])  # Use first few user responses

        system_prompt = """You are a strategic coach expert in Simon Sinek's 'Start with Why' methodology. 

Based on the user's responses about their organization, create a structured WHY statement that captures their authentic purpose.

The WHY should:
1. Be action-oriented (start with "To...")
2. Focus on the beneficiary they serve
3. Capture their unique contribution
4. Feel authentic to their origin story
5. Inspire both internal teams and external stakeholders

Generate core beliefs that drive this WHY and actionable values that manifest it."""

        user_prompt = f"""Based on this conversation about the organization:

{conversation_summary}

Please create a complete WHY statement with core beliefs and actionable values that authentically represents this organization's purpose."""

        return [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]


def why_agent_node(state: StrategyCoachState) -> dict:
    """
    LangGraph node function for WHY phase using Simon Sinek methodology.

    This is the main entry point for the WHY agent that follows LangGraph
    node patterns and integrates with the StateGraph.
    """
    agent = WHYAgentNode()
    return agent(state)


def create_why_agent_with_custom_llm(llm) -> WHYAgentNode:
    """Factory function to create WHY agent with custom LLM."""
    return WHYAgentNode(llm=llm)
