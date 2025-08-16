"""
Strategic Testing Agent for User Journey Simulation
Implements realistic business leader personas for comprehensive testing.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import json
from datetime import datetime
import re

from .business_case import BusinessCase, PersonaType, PersonaCharacteristics
from ..utils.llm_client import get_llm_client
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class ConversationContext:
    """Context information for response generation."""
    coach_message: str
    conversation_history: List[Dict[str, str]]
    current_phase: str
    strategy_completeness: float
    session_metadata: Dict[str, Any]


class ContextMemory:
    """Manages progressive information disclosure and context awareness."""
    
    def __init__(self, business_case: BusinessCase):
        self.business_case = business_case
        self.disclosed_information = set()
        self.conversation_depth = 0
        self.trust_level = 0.0  # 0.0 to 1.0
        
    def should_disclose_information(self, topic: str, coach_message: str) -> bool:
        """Determine if information about a topic should be disclosed."""
        
        # Always disclose basic company information
        basic_topics = [
            "company_name", "industry", "size", "mission", 
            "current_challenges", "market_position"
        ]
        
        if topic in basic_topics:
            return True
            
        # Disclose deeper information based on trust level and conversation depth
        sensitive_topics = [
            "founder_story", "core_beliefs", "past_failures", 
            "financial_details", "competitive_concerns"
        ]
        
        if topic in sensitive_topics:
            return self.trust_level > 0.3 and self.conversation_depth > 3
            
        # Disclose strategic details when trust is established
        strategic_topics = [
            "strategic_goals", "unique_advantages", "lessons_learned",
            "future_vision", "strategic_questions"
        ]
        
        if topic in strategic_topics:
            return self.trust_level > 0.5 and self.conversation_depth > 5
            
        return True
    
    def update_context(self, coach_message: str, user_response: str):
        """Update context based on conversation progression."""
        self.conversation_depth += 1
        
        # Increase trust based on coaching quality indicators
        trust_indicators = [
            "understand", "appreciate", "hear", "sense", "feel",
            "acknowledge", "recognize", "see", "respect"
        ]
        
        if any(indicator in coach_message.lower() for indicator in trust_indicators):
            self.trust_level = min(1.0, self.trust_level + 0.1)
            
        # Track disclosed information
        self._analyze_disclosed_topics(user_response)
    
    def _analyze_disclosed_topics(self, user_response: str):
        """Analyze what topics were disclosed in user response."""
        response_lower = user_response.lower()
        
        topic_keywords = {
            "founder_story": ["founded", "started", "began", "origin"],
            "financial_details": ["revenue", "profit", "funding", "money"],
            "core_beliefs": ["believe", "value", "principle", "conviction"],
            "challenges": ["challenge", "problem", "difficult", "struggle"],
            "goals": ["goal", "aim", "target", "objective", "want to"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                self.disclosed_information.add(topic)


class ResponseGenerator:
    """Generates authentic, context-aware responses based on business case and persona."""
    
    def __init__(self, business_case: BusinessCase, context_memory: ContextMemory):
        self.business_case = business_case
        self.context_memory = context_memory
        self.llm = get_llm_client()
        self.persona = business_case.persona_characteristics
        
    def generate_response(self, context: ConversationContext) -> str:
        """Generate authentic response based on context and business case."""
        
        # Extract relevant business context
        relevant_context = self._extract_relevant_context(context.coach_message)
        
        # Apply persona filtering
        persona_guidance = self._get_persona_guidance()
        
        # Create response prompt
        prompt = self._create_response_prompt(context, relevant_context, persona_guidance)
        
        try:
            response = self.llm.invoke(prompt)
            generated_response = response.content if hasattr(response, 'content') else str(response)
            
            # Apply persona post-processing
            final_response = self._apply_persona_style(generated_response)
            
            # Update context memory
            self.context_memory.update_context(context.coach_message, final_response)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(context)
    
    def _extract_relevant_context(self, coach_message: str) -> Dict[str, Any]:
        """Extract relevant business case information based on coach message."""
        
        relevant_info = {}
        message_lower = coach_message.lower()
        
        # Always include basic company info
        relevant_info["company_profile"] = {
            "name": self.business_case.company_profile.name,
            "industry": self.business_case.company_profile.industry.value,
            "size": self.business_case.company_profile.size,
            "revenue": self.business_case.company_profile.revenue
        }
        
        # Include mission if purpose-related questions
        if any(word in message_lower for word in ["why", "purpose", "mission", "exist", "inspired"]):
            relevant_info["mission"] = self.business_case.strategic_context.mission
            if self.context_memory.should_disclose_information("founder_story", coach_message):
                relevant_info["founder_story"] = self.business_case.background_knowledge.founder_story
        
        # Include challenges if problem-focused questions
        if any(word in message_lower for word in ["challenge", "problem", "difficult", "struggle", "frustration"]):
            relevant_info["challenges"] = self.business_case.strategic_context.current_challenges
        
        # Include beliefs if values-related questions
        if any(word in message_lower for word in ["believe", "value", "principle", "conviction", "drive"]):
            if self.context_memory.should_disclose_information("core_beliefs", coach_message):
                relevant_info["core_beliefs"] = self.business_case.background_knowledge.core_beliefs
        
        # Include strategic context if strategy-focused
        if any(word in message_lower for word in ["strategy", "goal", "future", "vision", "plan"]):
            if self.context_memory.should_disclose_information("strategic_goals", coach_message):
                relevant_info["strategic_goals"] = self.business_case.strategic_goals.short_term
        
        return relevant_info
    
    def _get_persona_guidance(self) -> str:
        """Get persona-specific guidance for response generation."""
        
        persona_templates = {
            PersonaType.ANALYTICAL_CEO: """
                PERSONA: Analytical CEO
                - Communication: Data-driven, structured, asks for metrics and evidence
                - Decision-making: Requires data and analysis before decisions
                - Information sharing: Detailed, comprehensive, includes supporting data
                - Questioning: Challenges assumptions, seeks quantifiable outcomes
                - Uncertainty: Seeks validation through data and expert input
            """,
            PersonaType.VISIONARY_FOUNDER: """
                PERSONA: Visionary Founder  
                - Communication: Passionate, inspiring, focuses on purpose and impact
                - Decision-making: Mission-driven, values-based, long-term thinking
                - Information sharing: Detailed stories, emotional context, big picture
                - Questioning: Philosophical, explores deeper meaning and purpose
                - Uncertainty: Seeks deeper understanding and meaning
            """,
            PersonaType.PRAGMATIC_DIRECTOR: """
                PERSONA: Pragmatic Director
                - Communication: Implementation-focused, practical, resource-conscious
                - Decision-making: Balances vision with practical constraints
                - Information sharing: Selective, focuses on actionable information
                - Questioning: Practical, implementation-oriented, resource-aware
                - Uncertainty: Wants clear options and practical next steps
            """,
            PersonaType.TECHNICAL_CTO: """
                PERSONA: Technical CTO
                - Communication: Technology-oriented, system thinking, innovation-focused
                - Decision-making: Technical feasibility drives decisions
                - Information sharing: Technical details, system implications
                - Questioning: Technology and architecture focused
                - Uncertainty: Seeks technical validation and system implications
            """,
            PersonaType.OPERATIONS_COO: """
                PERSONA: Operations COO
                - Communication: Process-driven, efficiency-minded, execution-focused
                - Decision-making: Operational impact and efficiency prioritized
                - Information sharing: Process details, operational metrics
                - Questioning: Process and efficiency focused
                - Uncertainty: Wants operational clarity and process implications
            """
        }
        
        return persona_templates.get(self.business_case.persona_type, persona_templates[PersonaType.VISIONARY_FOUNDER])
    
    def _create_response_prompt(self, context: ConversationContext, relevant_context: Dict[str, Any], persona_guidance: str) -> str:
        """Create comprehensive prompt for response generation."""
        
        return f"""You are a business leader being coached through strategic development. You must respond authentically based on your business context and persona.

BUSINESS CONTEXT:
{json.dumps(relevant_context, indent=2)}

{persona_guidance}

CONVERSATION HISTORY:
{self._format_conversation_history(context.conversation_history)}

CURRENT SITUATION:
- Phase: {context.current_phase}
- Strategy Completeness: {context.strategy_completeness}%
- Coach Message: "{context.coach_message}"

RESPONSE GUIDELINES:
1. Stay in character as the business leader with the specified persona
2. Reference specific business context when relevant and natural
3. Show appropriate level of detail based on relationship depth (Trust Level: {self.context_memory.trust_level:.1f})
4. Include realistic business concerns, uncertainties, or strategic thinking
5. Respond naturally as if in a real coaching conversation
6. Keep response length appropriate (50-200 words typically)

Generate an authentic response that this business leader would realistically give to the coach's message."""

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for prompt context."""
        if not history:
            return "No previous conversation"
            
        # Include last 6 exchanges for context
        recent_history = history[-6:] if len(history) > 6 else history
        
        formatted = []
        for exchange in recent_history:
            role = exchange.get("role", "unknown")
            content = exchange.get("content", "")
            formatted.append(f"{role.title()}: {content}")
            
        return "\n".join(formatted)
    
    def _apply_persona_style(self, response: str) -> str:
        """Apply persona-specific style adjustments to response."""
        
        # Analytical CEO - add data focus
        if self.business_case.persona_type == PersonaType.ANALYTICAL_CEO:
            if "%" not in response and "metric" not in response.lower():
                # Occasionally add data references
                if self.context_memory.conversation_depth > 2:
                    response += " What metrics should we be tracking for this?"
        
        # Visionary Founder - add passion and purpose
        elif self.business_case.persona_type == PersonaType.VISIONARY_FOUNDER:
            # Add occasional passion indicators
            if self.context_memory.conversation_depth > 3 and "!" not in response:
                response = response.replace(".", "!", 1)  # Replace first period with exclamation
        
        # Pragmatic Director - add implementation concerns
        elif self.business_case.persona_type == PersonaType.PRAGMATIC_DIRECTOR:
            if "how" not in response.lower() and self.context_memory.conversation_depth > 2:
                response += " How would we actually implement this?"
                
        return response
    
    def _get_fallback_response(self, context: ConversationContext) -> str:
        """Provide fallback response when LLM fails."""
        
        fallback_responses = {
            PersonaType.ANALYTICAL_CEO: "I need to understand this better. Can you provide more specific details or data to help me evaluate this?",
            PersonaType.VISIONARY_FOUNDER: "That's an interesting perspective. Let me think about how this connects to our larger mission and vision.",
            PersonaType.PRAGMATIC_DIRECTOR: "I want to make sure I understand the practical implications here. Can you walk me through how this would work?",
            PersonaType.TECHNICAL_CTO: "From a technical standpoint, I need to consider the system implications. Can you help me understand the architecture?",
            PersonaType.OPERATIONS_COO: "I'm thinking about the operational impact. How would this affect our current processes and workflows?"
        }
        
        return fallback_responses.get(
            self.business_case.persona_type, 
            "That's an interesting point. Can you help me understand this better?"
        )


class StrategicTestingAgent:
    """
    Main testing agent that simulates realistic business leaders
    experiencing strategic coaching journeys.
    """
    
    def __init__(self, business_case: BusinessCase):
        """Initialize testing agent with business case and persona."""
        self.business_case = business_case
        self.context_memory = ContextMemory(business_case)
        self.response_generator = ResponseGenerator(business_case, self.context_memory)
        self.session_id = None
        self.conversation_count = 0
        
        logger.info(f"Strategic Testing Agent initialized for {business_case.company_profile.name} ({business_case.persona_type.value})")
    
    def generate_response(self, coach_message: str, conversation_context: ConversationContext) -> str:
        """Generate authentic user response to coach message."""
        
        self.conversation_count += 1
        
        logger.debug(f"Generating response {self.conversation_count} for {self.business_case.persona_type.value}")
        
        try:
            response = self.response_generator.generate_response(conversation_context)
            
            logger.info(f"Generated {len(response)} character response for {self.business_case.company_profile.name}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            return self._get_emergency_fallback(coach_message)
    
    def should_request_interactive_elements(self, coach_message: str) -> bool:
        """Determine if testing agent should explicitly request interactive elements."""
        
        # Pragmatic personas more likely to request structured choices
        if self.business_case.persona_type in [PersonaType.PRAGMATIC_DIRECTOR, PersonaType.ANALYTICAL_CEO]:
            # After several exchanges, may request structure
            if self.conversation_count > 5 and "?" in coach_message:
                return self.conversation_count % 8 == 0  # Occasionally request choices
        
        # Visionary founders less likely to request structured choices
        return False
    
    def get_persona_summary(self) -> Dict[str, str]:
        """Get summary of persona characteristics for reporting."""
        return {
            "persona_type": self.business_case.persona_type.value,
            "communication_style": self.persona.communication_style,
            "decision_making": self.persona.decision_making,
            "information_sharing": self.persona.information_sharing,
            "questioning_tendency": self.persona.questioning_tendency,
            "uncertainty_handling": self.persona.uncertainty_handling
        }
    
    def get_business_context_summary(self) -> Dict[str, Any]:
        """Get summary of business context for reporting."""
        return {
            "company_name": self.business_case.company_profile.name,
            "industry": self.business_case.company_profile.industry.value,
            "stage": self.business_case.company_profile.stage.value,
            "size": self.business_case.company_profile.size,
            "mission": self.business_case.strategic_context.mission,
            "key_challenges": self.business_case.strategic_context.current_challenges[:3],
            "strategic_questions": self.business_case.strategic_goals.strategic_questions[:2]
        }
    
    @property
    def persona(self) -> PersonaCharacteristics:
        """Get persona characteristics."""
        return self.business_case.persona_characteristics
    
    def _get_emergency_fallback(self, coach_message: str) -> str:
        """Emergency fallback when all else fails."""
        return f"I appreciate your question about {coach_message[:30]}... Let me think about that in the context of our organization."


# Convenience function for creating testing agents
def create_testing_agent(business_case_name: str) -> StrategicTestingAgent:
    """Create a testing agent from a business case in the library."""
    from .business_case import business_case_library
    
    business_case = business_case_library.get_case(business_case_name)
    if not business_case:
        raise ValueError(f"Business case '{business_case_name}' not found in library")
    
    return StrategicTestingAgent(business_case)