from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain.schema import SystemMessage
from langchain.prompts import PromptTemplate

from ..models.state import AgentState, update_strategy_completeness, set_processing_stage
from ..utils import get_logger
from ..utils.llm_client import get_llm_client


logger = get_logger(__name__)


class WhyAgent:
    """
    WHY Agent implementing Simon Sinek's Golden Circle methodology.
    
    This agent helps organizations discover their core purpose by exploring:
    1. Core Purpose - The fundamental reason the organization exists
    2. Core Beliefs - The driving beliefs that guide decisions
    3. Organizational Values - The principles that define behavior
    
    Based on Simon Sinek's "Start With Why" methodology and the Golden Circle framework.
    """
    
    def __init__(self):
        """Initialize the WHY Agent with Golden Circle prompts."""
        self.llm = get_llm_client()
        self.methodology = "Simon Sinek's Golden Circle"
        self.focus_areas = ["core_purpose", "core_beliefs", "organizational_values"]
        
        # Initialize prompts for different exploration stages
        self._init_prompts()
        
        logger.info("WHY Agent initialized with Golden Circle methodology")
    
    def _init_prompts(self):
        """Initialize the prompts for WHY exploration."""
        
        # Core Purpose Discovery Prompt
        self.purpose_discovery_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "company_context"],
            template="""You are a strategic consultant specializing in Simon Sinek's Golden Circle methodology, helping organizations discover their core purpose.

METHODOLOGY: Start with WHY - The Golden Circle
- WHY: Your purpose, cause, belief - why your organization exists
- HOW: Your process, values, and principles that bring your WHY to life  
- WHAT: Your products, services, and tangible results

CURRENT FOCUS: Discovering the Core PURPOSE (WHY)

Context about the organization:
{company_context}

Conversation so far:
{conversation_context}

User's latest input:
{user_input}

CRITICAL GUIDELINES (Choi & Pak, 2005):
- Keep response to 150-200 words MAXIMUM
- Ask ONLY ONE question per response
- Avoid leading questions and assumptions
- Use clear, simple language

RESPONSE STRUCTURE:
1. Briefly acknowledge their input (1-2 sentences)
2. Provide minimal context if helpful (1-2 sentences)  
3. Ask ONE focused, open-ended question

GOOD QUESTION PATTERNS:
✓ "What inspired the founding of your organization?"
✓ "How would you describe the change you want to create?"
✓ "What drives your passion for this work?"

AVOID:
✗ Multiple questions in one response
✗ Leading questions like "Don't you think..."
✗ False dichotomies (either/or questions)
✗ Long explanations or lists

Remember: Facilitate discovery through ONE clear, unbiased question about their purpose."""
        )
        
        # Belief Exploration Prompt
        self.belief_exploration_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "discovered_purpose"],
            template="""You are continuing the Golden Circle WHY discovery process, now focusing on CORE BELIEFS.

CURRENT WHY DISCOVERY:
Purpose identified: {discovered_purpose}

Conversation context:
{conversation_context}

User input:
{user_input}

CRITICAL GUIDELINES (150-200 words max, ONE question only):

Now we're exploring the CORE BELIEFS that support your purpose.

RESPONSE STRUCTURE:
1. Acknowledge the purpose discovered (1-2 sentences)
2. Bridge to exploring beliefs (1-2 sentences)
3. Ask ONE focused question about their beliefs

GOOD BELIEF QUESTIONS:
✓ "What fundamental belief about your industry drives your work?"
✓ "What principle would you never compromise on?"
✓ "What assumption do others accept that you challenge?"

Remember: Ask ONE clear question to uncover authentic beliefs."""
        )
        
        # Values Integration Prompt
        self.values_integration_prompt = PromptTemplate(
            input_variables=["conversation_context", "purpose", "beliefs", "user_input"],
            template="""You are completing the Golden Circle WHY discovery by defining ORGANIZATIONAL VALUES.

DISCOVERED WHY ELEMENTS:
Core Purpose: {purpose}
Core Beliefs: {beliefs}

Conversation context:
{conversation_context}

User input:
{user_input}

Now help define the VALUES that bring the WHY to life:

1. **Behavioral Values**: How should people in this organization act and behave?
2. **Decision Values**: What values guide important decisions?
3. **Cultural Values**: What kind of culture and environment does this create?

Explore questions like:
- "Given your purpose and beliefs, how should people in your organization behave?"
- "What behaviors would be celebrated and what would be unacceptable?"
- "How do your beliefs translate into daily actions and decisions?"
- "What kind of people would thrive in your organization?"

Help create values that are:
- Actionable and specific (not generic)
- Aligned with purpose and beliefs
- Observable in behavior
- Sustainable and authentic

The goal is values that people can use to make decisions and guide behavior, creating a culture that naturally supports the WHY."""
        )
        
        # Synthesis and Validation Prompt - FIXED to remove transition assumption
        self.synthesis_prompt = PromptTemplate(
            input_variables=["purpose", "beliefs", "values", "conversation_context"],
            template="""You are providing a Golden Circle WHY synthesis based on the conversation so far.

DISCOVERED WHY COMPONENTS:
Core Purpose: {purpose}
Core Beliefs: {beliefs}
Organizational Values: {values}

Conversation history:
{conversation_context}

CRITICAL: Provide ONLY synthesis and validation questions. DO NOT assume user agreement or suggest transitions.

Format your response as:

**YOUR WHY STATEMENT:**
[Clear, compelling statement that captures their purpose]

**CORE BELIEFS THAT DRIVE YOU:**
[Key beliefs that support the purpose]

**VALUES THAT GUIDE BEHAVIOR:**
[Specific, actionable values]

**GOLDEN CIRCLE INTEGRATION:**
[Brief explanation of how these elements work together]

**VALIDATION:**
Does this capture the essence of why your organization exists? Does it inspire you and feel authentic to your core motivation? 

Please let me know if this feels right, needs adjustment, or if you'd like to refine any part of it before we move forward."""
        )
    
    def process_user_input(self, state: AgentState, user_input: str) -> AgentState:
        """
        Process user input through the WHY Agent's Golden Circle methodology.
        
        Args:
            state: Current agent state
            user_input: User's message content
            
        Returns:
            Updated agent state with WHY Agent response
        """
        logger.info(f"WHY Agent processing input for session {state['session_id']}")
        
        try:
            # Determine current WHY exploration stage
            why_stage = self._determine_why_stage(state)
            logger.debug(f"WHY exploration stage: {why_stage}")
            
            # Extract conversation context
            conversation_context = self._extract_conversation_context(state)
            user_context = state.get("user_context", {})
            
            # Generate response based on stage - with proper validation state handling
            if why_stage == "validation_pause":
                # Process user validation response
                response = self._process_user_validation(state, user_input)
                
            elif why_stage == "transition_ready":
                # User has validated, ready to move to HOW phase
                response = """Excellent! I'm glad the WHY synthesis feels authentic to your organization's core purpose.

Now that we've established your foundational WHY, we can explore HOW you'll bring this purpose to life through your strategic approach and methodology.

What would you say is your most distinctive approach to making this WHY tangible in your day-to-day operations?"""
                
                # Mark WHY phase as complete for phase transition
                state["strategy_completeness"]["why"] = True
                state["awaiting_user_validation"] = False
                
            elif why_stage == "purpose_discovery":
                response = self._explore_purpose(conversation_context, user_input, user_context)
                
            elif why_stage == "belief_exploration":
                discovered_purpose = self._extract_discovered_purpose(state)
                response = self._explore_beliefs(conversation_context, user_input, discovered_purpose)
                
            elif why_stage == "values_integration":
                purpose = self._extract_discovered_purpose(state)
                beliefs = self._extract_discovered_beliefs(state)
                response = self._integrate_values(conversation_context, user_input, purpose, beliefs)
                
            elif why_stage == "synthesis":
                # Replace complex synthesis with simple progression prompt
                purpose = self._extract_discovered_purpose(state)
                
                # Create simple WHY summary from conversation
                why_summary = self._create_simple_why_summary(conversation_context, purpose)
                
                response = f"""Based on our conversation, your WHY appears to be: {why_summary}

This captures the essence of why AFAS exists - to empower entrepreneurs through trust-based, integrated software solutions.

Ready for HOW?"""
                
                # Set the ready for HOW prompt and pause conversation
                state["ready_for_how_prompt"] = f"Your WHY: {why_summary}. Ready to explore HOW?"
                state["synthesis_provided"] = True
                state["awaiting_user_validation"] = True
                
            else:
                # Default to purpose discovery
                response = self._explore_purpose(conversation_context, user_input, user_context)
            
            # Update state with WHY Agent insights
            state = self._update_state_with_insights(state, why_stage, response)
            
            # Add AI response to conversation
            ai_message = AIMessage(content=response)
            state["conversation_history"].append(ai_message)
            
            # Update processing metadata
            state = set_processing_stage(state, "why_agent_completed", "why_agent")
            state["agent_output"] = response
            
            logger.info(f"WHY Agent completed processing for stage: {why_stage}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in WHY Agent processing: {str(e)}")
            
            # Set error state but provide fallback response
            state["error_state"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "agent": "why_agent"
            }
            
            fallback_response = self._get_fallback_response()
            ai_message = AIMessage(content=fallback_response)
            state["conversation_history"].append(ai_message)
            state["agent_output"] = fallback_response
            
            return state
    
    def _determine_why_stage(self, state: AgentState) -> str:
        """Determine the current stage of WHY exploration based on conversation progress and validation state."""
        
        # CRITICAL FIX: Check validation state first before determining stage
        if state.get("awaiting_user_validation", False):
            return "validation_pause"
        
        if state.get("user_validation_confirmed", False):
            return "transition_ready"
        
        conversation = state["conversation_history"]
        
        # Count different types of WHY-related content discovered
        purpose_indicators = 0
        belief_indicators = 0
        values_indicators = 0
        
        # Analyze conversation for progress indicators
        for message in conversation:
            if hasattr(message, 'content') and message.content:
                content_lower = message.content.lower()
                
                # Purpose discovery indicators
                if any(keyword in content_lower for keyword in [
                    "purpose", "why we exist", "reason for being", "mission", "cause"
                ]):
                    purpose_indicators += 1
                
                # Belief exploration indicators
                if any(keyword in content_lower for keyword in [
                    "believe", "conviction", "principle", "philosophy", "assumption"
                ]):
                    belief_indicators += 1
                
                # Values integration indicators
                if any(keyword in content_lower for keyword in [
                    "values", "behavior", "culture", "how we act", "decision making"
                ]):
                    values_indicators += 1
        
        # Determine stage based on conversation progress
        conversation_turns = len(conversation) // 2  # User-AI pairs
        
        # FIXED: Only return synthesis if not already provided
        if (conversation_turns >= 6 and purpose_indicators >= 2 and belief_indicators >= 1 and 
            not state.get("synthesis_provided", False)):
            if values_indicators >= 1:
                return "synthesis"
            else:
                return "values_integration"
        elif conversation_turns >= 3 and purpose_indicators >= 1:
            return "belief_exploration"
        else:
            return "purpose_discovery"
    
    def _extract_conversation_context(self, state: AgentState) -> str:
        """Extract relevant conversation context for prompting."""
        
        conversation = state["conversation_history"]
        
        # Get recent conversation (last 8 messages or all if fewer)
        recent_messages = conversation[-8:] if len(conversation) > 8 else conversation
        
        context_parts = []
        for message in recent_messages:
            if hasattr(message, 'content') and message.content:
                if isinstance(message, HumanMessage):
                    context_parts.append(f"User: {message.content}")
                elif isinstance(message, AIMessage):
                    context_parts.append(f"AI: {message.content}")
        
        return "\n".join(context_parts) if context_parts else "No previous conversation"
    
    def _explore_purpose(self, conversation_context: str, user_input: str, user_context: Dict[str, Any]) -> str:
        """Generate response for purpose discovery stage."""
        
        company_context = self._format_company_context(user_context)
        
        prompt = self.purpose_discovery_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            company_context=company_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in purpose exploration: {str(e)}")
            return self._get_fallback_purpose_response()
    
    def _process_user_validation(self, state: AgentState, user_input: str) -> str:
        """Process user validation response and determine next steps."""
        
        user_input_lower = user_input.lower()
        
        # Check for positive validation signals
        positive_signals = [
            "yes", "this captures", "exactly", "correct", "right", "accurate",
            "authentic", "inspiring", "resonates", "perfect", "spot on",
            "that's it", "captures it", "feels right", "true", "agreed"
        ]
        
        # Check for modification/refinement signals
        modification_signals = [
            "but", "however", "need to adjust", "not quite", "close but", 
            "modify", "change", "refine", "different", "actually"
        ]
        
        # Check for progression signals
        progression_signals = [
            "ready", "move forward", "next phase", "how", "let's continue",
            "proceed", "move on", "ready to explore"
        ]
        
        if any(signal in user_input_lower for signal in positive_signals):
            if any(signal in user_input_lower for signal in progression_signals):
                # User validates AND wants to move forward
                state["user_validation_confirmed"] = True
                state["awaiting_user_validation"] = False
                state["validation_response"] = user_input
                state["strategy_completeness"]["why"] = True  # Mark WHY phase complete
                
                return """Excellent! I'm glad the WHY synthesis feels authentic to your organization's core purpose.
                
Now that we've established your foundational WHY, we can explore HOW you'll bring this purpose to life through your strategic approach and methodology.

What would you say is your most distinctive approach to making this WHY tangible in your day-to-day operations?"""
                
            else:
                # User validates but may want to explore more
                state["user_validation_confirmed"] = True
                state["awaiting_user_validation"] = False
                state["validation_response"] = user_input
                
                return "Thank you for confirming this captures your WHY! Would you like to explore this further, or are you ready to move on to HOW you'll bring this purpose to life strategically?"
        
        elif any(signal in user_input_lower for signal in modification_signals):
            # User wants modifications
            state["awaiting_user_validation"] = False
            state["synthesis_provided"] = False  # Allow new synthesis generation
            
            return "I understand you'd like to refine the WHY synthesis. What specifically would you like to adjust or explore differently? Let's make sure we capture your authentic purpose before moving forward."
        
        else:
            # Unclear response, ask for clarification
            return "I want to make sure I understand your response to the WHY synthesis. Does it feel authentic to your organization's purpose, or would you like to refine it? Please let me know so we can either move forward or adjust accordingly."
    
    def _create_simple_why_summary(self, conversation_context: str, purpose: str) -> str:
        """Create a simple, one-sentence WHY summary from conversation."""
        
        # Extract key themes from conversation
        context_lower = conversation_context.lower()
        
        # Look for AFAS-specific themes
        if "trust" in context_lower and "entrepreneur" in context_lower:
            return "To empower entrepreneurs through trust-based software that eliminates administrative burdens"
        elif "entrepreneur" in context_lower and ("simple" in context_lower or "integrate" in context_lower):
            return "To inspire better entrepreneurship through integrated, simple business software"
        elif "trust" in context_lower and ("people" in context_lower or "employee" in context_lower):
            return "To demonstrate that business success comes from trusting and empowering people"
        elif "entrepreneur" in context_lower:
            return "To support entrepreneurs in achieving their vision without administrative obstacles"
        else:
            # Fallback based on purpose extraction
            if purpose and len(purpose) > 20:
                # Extract key phrases from purpose
                return "To inspire better entrepreneurship through integrated business software"
            else:
                return "To empower entrepreneurs and eliminate business software complexity"
    
    def _explore_beliefs(self, conversation_context: str, user_input: str, discovered_purpose: str) -> str:
        """Generate response for belief exploration stage."""
        
        prompt = self.belief_exploration_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            discovered_purpose=discovered_purpose
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in belief exploration: {str(e)}")
            return self._get_fallback_belief_response()
    
    def _integrate_values(self, conversation_context: str, user_input: str, 
                         purpose: str, beliefs: str) -> str:
        """Generate response for values integration stage."""
        
        prompt = self.values_integration_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            purpose=purpose,
            beliefs=beliefs
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in values integration: {str(e)}")
            return self._get_fallback_values_response()
    
    def _synthesize_why_framework(self, purpose: str, beliefs: str, values: str, 
                                 conversation_context: str) -> str:
        """Generate comprehensive WHY framework synthesis."""
        
        prompt = self.synthesis_prompt.format(
            purpose=purpose,
            beliefs=beliefs,
            values=values,
            conversation_context=conversation_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in WHY synthesis: {str(e)}")
            return self._get_fallback_synthesis_response(purpose, beliefs, values)
    
    def _extract_discovered_purpose(self, state: AgentState) -> str:
        """Extract discovered purpose from conversation history."""
        
        # Look through conversation for purpose-related content
        purpose_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "purpose", "why you exist", "reason for being", "mission", "cause"
                ]):
                    purpose_content.append(message.content)
        
        # Return the most relevant purpose discovery (simplified)
        return purpose_content[-1] if purpose_content else "Purpose exploration in progress"
    
    def _extract_discovered_beliefs(self, state: AgentState) -> str:
        """Extract discovered beliefs from conversation history."""
        
        belief_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "believe", "conviction", "principle", "philosophy"
                ]):
                    belief_content.append(message.content)
        
        return belief_content[-1] if belief_content else "Belief exploration in progress"
    
    def _extract_discovered_values(self, state: AgentState) -> str:
        """Extract discovered values from conversation history."""
        
        values_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "values", "behavior", "culture", "how we act"
                ]):
                    values_content.append(message.content)
        
        return values_content[-1] if values_content else "Values integration in progress"
    
    def _update_state_with_insights(self, state: AgentState, stage: str, response: str) -> AgentState:
        """Update agent state with WHY insights and mark completion if appropriate."""
        
        # Track progress in strategy completeness
        if stage == "synthesis":
            # Mark WHY phase as complete after synthesis
            state = update_strategy_completeness(state, "why", True)
            logger.info("WHY Agent marked WHY phase as complete")
        
        # Update identified gaps and insights
        why_insights = self._extract_insights_from_response(response, stage)
        if "identified_gaps" not in state:
            state["identified_gaps"] = []
        
        state["identified_gaps"].extend(why_insights)
        
        return state
    
    def _extract_insights_from_response(self, response: str, stage: str) -> List[str]:
        """Extract actionable insights from the agent's response."""
        
        insights = []
        
        if stage == "purpose_discovery":
            insights.append("Core purpose exploration initiated")
        elif stage == "belief_exploration":
            insights.append("Belief system analysis in progress")
        elif stage == "values_integration":
            insights.append("Organizational values definition underway")
        elif stage == "synthesis":
            insights.append("WHY framework completed - ready for HOW phase")
        
        return insights
    
    def _format_company_context(self, user_context: Dict[str, Any]) -> str:
        """Format user context into company information for prompting."""
        
        if not user_context:
            return "No company context provided"
        
        context_parts = []
        
        if "company_name" in user_context:
            context_parts.append(f"Company: {user_context['company_name']}")
        
        if "industry" in user_context:
            context_parts.append(f"Industry: {user_context['industry']}")
        
        if "team_size" in user_context:
            context_parts.append(f"Team size: {user_context['team_size']}")
        
        if "revenue_stage" in user_context:
            context_parts.append(f"Stage: {user_context['revenue_stage']}")
        
        return "\n".join(context_parts) if context_parts else "Company context being discovered"
    
    # Fallback responses for error conditions
    def _get_fallback_response(self) -> str:
        """Provide fallback response when LLM fails."""
        return """I'm here to help you discover your organization's core purpose using Simon Sinek's Golden Circle methodology. 

Let's start with a fundamental question: Why does your organization exist beyond making money? What positive impact do you want to create in the world?

Tell me about what originally inspired this organization to be founded."""
    
    def _get_fallback_purpose_response(self) -> str:
        return """Let's explore your organization's core purpose together. 

Think about these questions:
- What problem in the world keeps you up at night?
- What change do you want to see that drives your daily work?
- If your organization disappeared tomorrow, what would be missing from the world?

Share your thoughts on what fundamentally motivates your organization beyond financial success."""
    
    def _get_fallback_belief_response(self) -> str:
        return """Now that we're exploring your purpose, let's dig into your core beliefs.

Consider these questions:
- What do you believe about your industry that others might not?
- What principles guide your toughest decisions?
- What assumptions do most people accept that you challenge?

What beliefs drive your organization's unique approach?"""
    
    def _get_fallback_values_response(self) -> str:
        return """Let's define the values that bring your purpose and beliefs to life.

Think about:
- How should people in your organization behave day-to-day?
- What behaviors would you celebrate and what would be unacceptable?
- How do your beliefs translate into daily actions and decisions?

What values would guide behavior in your organization?"""
    
    def _get_fallback_synthesis_response(self, purpose: str, beliefs: str, values: str) -> str:
        return f"""**YOUR WHY FRAMEWORK:**

**Core Purpose:** {purpose}

**Driving Beliefs:** {beliefs}

**Guiding Values:** {values}

Does this capture the essence of why your organization exists? This WHY framework can now guide how you develop your strategy and approach.

Ready to explore HOW you'll bring this purpose to life?"""


# Integration function for orchestrator
def create_why_agent_node():
    """Create a WHY Agent node function for use in the orchestrator."""
    
    why_agent = WhyAgent()
    
    def why_agent_node(state: AgentState) -> AgentState:
        """WHY Agent node function for LangGraph orchestrator."""
        
        # Extract the latest user message
        user_input = ""
        if state["conversation_history"]:
            latest_message = state["conversation_history"][-1]
            if isinstance(latest_message, HumanMessage):
                user_input = latest_message.content
        
        # Process through WHY Agent
        return why_agent.process_user_input(state, user_input)
    
    return why_agent_node