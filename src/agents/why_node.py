"""
WHY Agent Node - Simon Sinek "Start with Why" methodology implementation.

This module implements the WHY phase agent as a LangGraph node function,
guiding users through discovery of their organizational core purpose using
the Golden Circle framework.
"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langsmith import traceable
from ..core.config import settings
from ..core.models import WHYStatement
from ..core.state import StrategyCoachState

import logging
logger = logging.getLogger(__name__)


class WHYAgentNode:
    """
    WHY Agent implementation using Simon Sinek's 'Start with Why' methodology.

    Guides users through the Golden Circle framework to discover authentic
    organizational purpose through Socratic questioning.
    """

    def __init__(self, llm=None):
        """Initialize the WHY agent with LLM configuration."""
        if llm:
            self.llm = llm
        else:
            # Ensure API key is available
            api_key = settings.get_llm_api_key()
            if not api_key:
                raise ValueError(f"No API key configured for {settings.llm_provider}")
            
            # Initialize with explicit API key
            if settings.llm_provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    model=settings.default_model,
                    anthropic_api_key=api_key,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens
                )
            else:
                # Fallback to init_chat_model for other providers
                self.llm = init_chat_model(
                    f"{settings.llm_provider}:{settings.default_model}",
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                )

        # Configure LLM for structured output
        self.structured_llm = self.llm.with_structured_output(WHYStatement)

        # WHY methodology prompts based on Simon Sinek framework
        self.prompts = {
            "welcome": """Welcome! I'm your WHY coach, and I'll help you discover your organization's authentic core purpose using Simon Sinek's methodology.

Your WHY isn't what you do—it's why you exist. It's your core belief that inspires others to join your cause.

Let's start with your origin story. How did your organization begin? What problem drove the founders to take action?""",
            "discovery": """Now let's explore your proudest moments—times when you felt most fulfilled by the impact you were making.

What were you doing in those moments? Who were you helping? What specific difference were you creating that felt most meaningful?""",
            "mining_beliefs": """I can sense the passion in your work. Let's explore the core beliefs driving this.

What do you believe about {primary_beneficiary} that others might not see? What keeps you motivated to do this work?

Complete this: "Every {primary_beneficiary} deserves..." What comes next for you?""",
            "distilling_why": """Based on everything you've shared, I can see a powerful WHY emerging. Let me help you distill this into Simon Sinek's WHY format.

Your WHY seems to be: "To {core_action} every {primary_beneficiary} access to {key_resource}, so they can {achieve_goal} without {common_obstacle}."

Does this capture the essence of why your organization exists? What feels authentic here, and what might need refinement?""",
            "values_definition": """Perfect! Now let's define your values as actionable verbs, not just words on a wall.

Instead of 'integrity' (noun), think 'act with integrity' (verb). Instead of 'innovation', think 'challenge conventional thinking.'

What are 3-5 actionable behaviors that guide how you operate? What verbs describe how you live your WHY daily?""",
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
        current_stage = state.get("methodology_stage", "welcome")
        interaction_count = state.get("interaction_count", 0)
        why_output = state.get("why_output")

        # Determine next stage based on current state and user input
        stage = self._determine_next_stage(current_stage, interaction_count, why_output)
        print(f"🔍 WHY Agent: current_stage='{current_stage}' → next_stage='{stage}', interaction={interaction_count}")

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
            "methodology_stage": stage,
            "phase_complete": phase_complete,
            "why_output": new_why_output,
        }

    def _determine_next_stage(
        self, current_stage: str, interaction_count: int, why_output
    ) -> str:
        """Determine the next stage using LangGraph state management."""
        
        # Stage progression logic using state instead of counting
        stage_progression = [
            "welcome",           # 0
            "discovery",         # 1
            "mining_beliefs",    # 2
            "values_definition", # 3
            "distilling_why",    # 4
            "completion_check",  # 5 - Generate template
            "integration",       # 6
            "transition_readiness" # 7+
        ]
        
        # If no current stage, start at welcome
        if not current_stage or current_stage == "welcome":
            return "welcome" if interaction_count == 0 else "discovery"
        
        # Find current stage index
        try:
            current_index = stage_progression.index(current_stage)
        except ValueError:
            current_index = 0
        
        # Progress to next stage after user input
        next_index = min(current_index + 1, len(stage_progression) - 1)
        next_stage = stage_progression[next_index]
        
        # Special case: trigger completion when ready
        if interaction_count >= 4 and why_output is None and next_stage not in ["completion_check", "integration", "transition_readiness"]:
            return "completion_check"
        
        return next_stage

    def _handle_welcome_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle the welcome stage with origin story prompting."""
        _ = state  # Suppress unused parameter warning
        return AIMessage(content=self.prompts["welcome"])

    def _handle_discovery_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle the discovery stage with deeper purpose exploration using live LLM."""
        messages = state.get("messages", [])
        user_context = self._extract_user_context(messages)
        
        # Create contextual prompt for live LLM
        user_messages_text = "\n".join([
            msg.content for msg in messages 
            if hasattr(msg, 'type') and msg.type == "human"
        ])
        
        system_prompt = """You are a WHY coach using Simon Sinek's methodology. The user shared their origin story.

Create a concise response (2-3 sentences) that:
1. Acknowledges specific details they mentioned
2. Asks about their proudest moments
3. Be conversational and reference their story

Keep it brief and focused."""

        # Get the last 200 words for context (more natural than split array)
        recent_context = " ".join(user_messages_text.split()[-100:])
        
        user_prompt = f"""The user just said: "{recent_context}"

Create a natural, contextual response that acknowledges their specific origin story and asks about their proudest moments."""

        # Use live LLM for contextual response
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            return AIMessage(content=response.content)
        except Exception as e:
            # Fallback to template if LLM fails
            logger.warning(f"LLM discovery stage failed: {e}")
            return AIMessage(content=self.prompts["discovery"])

    def _handle_beliefs_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle core beliefs mining stage using live LLM."""
        messages = state.get("messages", [])
        
        # Get user conversation context
        user_messages_text = "\n".join([
            msg.content for msg in messages 
            if hasattr(msg, 'type') and msg.type == "human"
        ])
        
        system_prompt = """You are a WHY coach using Simon Sinek's methodology. The user shared their proudest moments.

Create a concise response (2-3 sentences) that:
1. Acknowledges their specific achievements
2. Explores their core beliefs about the people they serve
3. References their actual story

Keep it brief and focused."""

        # Get recent context in clean format
        recent_context = " ".join(user_messages_text.split()[-150:])
        
        user_prompt = f"""The user has shared: "{recent_context}"

Create a natural response that acknowledges their specific achievements and explores their core beliefs about the people they serve."""

        # Use live LLM for contextual response
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            return AIMessage(content=response.content)
        except Exception as e:
            # Fallback to template if LLM fails
            logger.warning(f"LLM beliefs stage failed: {e}")
            return AIMessage(content="I can sense the passion in your work. Let's explore the core beliefs that drive you. What do you believe about the people you serve?")

    def _handle_distilling_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle WHY statement distillation stage."""
        messages = state.get("messages", [])
        user_context = self._extract_user_context(messages)
        
        # Create contextual WHY distillation based on their specific story
        company_name = user_context.get("company_name", "your organization")
        beneficiary = user_context.get("primary_beneficiary", "people")
        beliefs = user_context.get("core_beliefs", "")
        
        if company_name and beneficiary:
            contextual_prompt = f"""Based on everything you've shared about {company_name}, I can see a powerful WHY emerging. 

Your WHY seems to be: "To help every {beneficiary} access the tools and clarity they need to succeed, so they can focus on what matters most without being held back by complexity or confusion."

{f'Your belief that "{beliefs}" is clearly driving this mission.' if beliefs else ''}

Does this capture the essence of why {company_name} exists? What feels authentic here, and what might need refinement before we explore HOW you'll achieve this?"""
        else:
            # Fallback to template-based approach
            elements = self._extract_why_elements(messages)
            contextual_prompt = self.prompts["distilling_why"].format(**elements)
        
        return AIMessage(content=contextual_prompt)

    def _handle_values_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle actionable values definition stage using live LLM."""
        messages = state.get("messages", [])
        
        # Get user conversation context
        user_messages_text = "\n".join([
            msg.content for msg in messages 
            if hasattr(msg, 'type') and msg.type == "human"
        ])
        
        system_prompt = """You are a WHY coach using Simon Sinek's methodology. The user shared their beliefs.

Create a concise response (2-3 sentences) that:
1. Acknowledges their beliefs
2. Explains values as actionable verbs (not nouns)
3. Asks for their actionable behaviors

Keep it brief and encouraging."""

        # Get recent context in clean format
        recent_context = " ".join(user_messages_text.split()[-200:])
        
        user_prompt = f"""The user's complete story: "{recent_context}"

Create a response that helps them define their values as actionable verbs, referencing their specific story and beliefs."""

        # Use live LLM for contextual response
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            return AIMessage(content=response.content)
        except Exception as e:
            # Fallback to template if LLM fails
            logger.warning(f"LLM values stage failed: {e}")
            return AIMessage(content=self.prompts["values_definition"])

    def _handle_integration_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle Golden Circle integration stage."""
        elements = self._extract_integration_elements(state.get("messages", []))
        prompt_content = self.prompts["golden_circle_integration"].format(**elements)
        return AIMessage(content=prompt_content)

    def _handle_completion_stage(self, state: StrategyCoachState) -> AIMessage:
        """Handle phase completion and structured output generation with PRD template."""
        # Use structured LLM to generate final WHYStatement
        try:
            # Create synthesis prompt for structured output
            synthesis_prompt = self._create_synthesis_prompt(state)
            structured_output = self.structured_llm.invoke(synthesis_prompt)

            # Create the full WHY template output as beautiful HTML
            template_output = self._format_why_template(structured_output)
            
            response = AIMessage(content=template_output)
            response.structured_output = structured_output
            return response

        except Exception as e:
            logger.error(f"Structured output generation failed: {e}")
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
        has_structured_output = hasattr(response, "structured_output")
        existing_why_output = state.get("why_output") is not None
        current_stage = state.get("methodology_stage", "")

        # Phase is complete if we have structured output or reached transition readiness
        return has_structured_output or existing_why_output or current_stage == "transition_readiness"

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

Based on the user's responses about their organization, create a comprehensive structured WHY statement that captures their authentic purpose.

The WHY statement should:
1. Be action-oriented (start with "To...")
2. Focus on the beneficiary they serve
3. Capture their unique contribution
4. Feel authentic to their origin story
5. Inspire both internal teams and external stakeholders

Generate:
- WHY statement in format: "To [action] every [beneficiary] access to [resource], so they can [goal] without [obstacle]"
- 3-6 core beliefs that drive this WHY (what they believe about their beneficiaries and the world)
- 4-6 actionable values as verb phrases (not nouns) with explanations
- Golden circle integration paragraph showing how WHY, beliefs, and values work together
- 2-3 validation questions to test authenticity
- Identify the primary beneficiary and key outcome they help achieve"""

        user_prompt = f"""Based on this conversation about the organization:

{conversation_summary}

Please create a complete WHY statement with core beliefs and actionable values that authentically represents this organization's purpose."""

        return [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    
    def _format_why_template(self, structured_output) -> str:
        """Format the structured output as beautiful HTML."""
        
        # Format core beliefs as HTML list
        beliefs_formatted = "\n".join([
            f"<li><strong>{belief.statement}</strong></li>" 
            for belief in structured_output.core_beliefs
        ])
        
        # Format actionable values as HTML list
        values_formatted = "\n".join([
            f"<li><strong>{value.action_phrase}</strong>: {value.explanation}</li>"
            for value in structured_output.actionable_values
        ])
        
        # Format validation questions
        validation_formatted = "<br>".join(structured_output.validation_questions)
        
        # Create beautiful HTML template
        template = f"""<div class="why-statement-template">
<div class="why-section">
<h3>🎯 <strong>YOUR WHY STATEMENT</strong></h3>
<div class="why-statement-box">
<p class="why-statement-text">{structured_output.why_statement}</p>
</div>
</div>

<div class="why-section">
<h4>💭 <strong>CORE BELIEFS THAT DRIVE YOU</strong></h4>
<ul class="beliefs-list">
{beliefs_formatted}
</ul>
</div>

<div class="why-section">
<h4>⚡ <strong>VALUES THAT GUIDE BEHAVIOR</strong></h4>
<ul class="values-list">
{values_formatted}
</ul>
</div>

<div class="why-section">
<h4>🔄 <strong>GOLDEN CIRCLE INTEGRATION</strong></h4>
<div class="integration-box">
<p>{structured_output.golden_circle_integration}</p>
</div>
</div>

<div class="why-section">
<h4>✅ <strong>VALIDATION</strong></h4>
<div class="validation-box">
<p>{validation_formatted}</p>
</div>
</div>

<div class="why-section transition-section">
<h4>🚀 <strong>READY FOR HOW PHASE?</strong></h4>
<p>Now that we've clarified your WHY - <strong>{structured_output.why_statement}</strong> - we can focus on HOW you'll deliver this.</p>
<p><em>Are you ready to explore the strategic logic and methods that will bring your purpose to life?</em></p>
</div>
</div>

<style>
.why-statement-template {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    max-width: 100%;
    margin: 20px 0;
}}

.why-section {{
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #007bff;
}}

.why-section h3 {{
    color: #007bff;
    margin: 0 0 12px 0;
    font-size: 18px;
}}

.why-section h4 {{
    color: #495057;
    margin: 0 0 10px 0;
    font-size: 16px;
}}

.why-statement-box {{
    background: #e3f2fd;
    padding: 15px;
    border-radius: 6px;
    border-left: 3px solid #2196f3;
}}

.why-statement-text {{
    font-size: 18px;
    font-weight: 600;
    color: #1565c0;
    margin: 0;
    line-height: 1.4;
}}

.beliefs-list, .values-list {{
    padding-left: 20px;
    margin: 0;
}}

.beliefs-list li, .values-list li {{
    margin-bottom: 8px;
    line-height: 1.4;
}}

.integration-box, .validation-box {{
    background: #fff;
    padding: 12px;
    border-radius: 6px;
    border: 1px solid #e9ecef;
}}

.transition-section {{
    background: #d4edda;
    border-left-color: #28a745;
}}

.transition-section h4 {{
    color: #155724;
}}
</style>"""

        return template
    
    def _extract_user_context(self, messages: list) -> dict:
        """Extract specific context and information from user messages."""
        import re
        
        context = {
            "user_name": "",
            "company_name": "",
            "origin_elements": "",
            "proud_moments": "",
            "primary_beneficiary": "entrepreneurs"
        }
        
        # Get recent user messages
        user_messages = []
        for message in messages:
            if hasattr(message, 'type') and message.type == "human":
                user_messages.append(message.content)
        
        if not user_messages:
            return context
        
        latest_message = user_messages[-1] if user_messages else ""
        
        # Extract user name
        name_patterns = [
            r"i'?m ([a-za-z\s]+),",
            r"i'?m ([a-za-z\s]+) (?:and|from|at|ceo|founder)",
            r"my name is ([a-za-z\s]+)"
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, latest_message.lower())
            if name_match:
                context["user_name"] = name_match.group(1).strip().title()
                break
        
        # Extract company name  
        company_patterns = [
            r"(?:ceo|founder|leader) of ([a-za-z\s]+)",
            r"at ([a-za-z\s]+)[,.]",
            r"run ([a-za-z\s]+)",
            r"company (?:called )?([a-za-z\s]+)"
        ]
        for pattern in company_patterns:
            company_match = re.search(pattern, latest_message.lower())
            if company_match:
                company = company_match.group(1).strip()
                if len(company) > 2 and company not in ["the", "our", "my", "a", "software"]:
                    context["company_name"] = company.title()
                    break
        
        # Extract origin elements
        if "started" in latest_message.lower() or "founded" in latest_message.lower():
            context["origin_elements"] = "your founding story"
        
        # Extract proud moments - be more specific
        if "proudest" in latest_message.lower() or "best workplace" in latest_message.lower():
            # Extract the actual achievement
            if "best workplace" in latest_message.lower():
                context["proud_moments"] = "Becoming the #1 Best Workplace in Europe"
            elif "proudest" in latest_message.lower():
                context["proud_moments"] = "your proudest achievements"
        
        # Extract primary beneficiary
        if "small business" in latest_message.lower():
            context["primary_beneficiary"] = "small businesses"
        elif "entrepreneur" in latest_message.lower():
            context["primary_beneficiary"] = "entrepreneurs" 
        elif "employee" in latest_message.lower():
            context["primary_beneficiary"] = "employees"
        
        return context


def why_agent_node(state: StrategyCoachState) -> dict:
    """
    LangGraph node function for WHY phase using Simon Sinek methodology.

    This is the main entry point for the WHY agent that follows LangGraph
    node patterns and integrates with the StateGraph.
    """
    agent = WHYAgentNode()
    return agent(state)


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
