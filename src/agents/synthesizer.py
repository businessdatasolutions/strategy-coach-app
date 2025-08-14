from typing import Dict, Any, List, Optional, Literal
import json
from dataclasses import dataclass
from enum import Enum

from langchain_core.messages import AIMessage

from ..models.state import AgentState, calculate_strategy_completeness
from ..utils import get_logger

logger = get_logger(__name__)


class ResponseType(Enum):
    """Types of synthesized responses."""
    QUESTION = "question"
    INSIGHT = "insight" 
    GUIDANCE = "guidance"
    SUMMARY = "summary"
    COMPLETION = "completion"


@dataclass
class SynthesisContext:
    """Context information for response synthesis."""
    current_agent: str
    agent_output: str
    strategy_completeness: float
    current_phase: str
    conversation_turn: int
    user_intent_summary: Dict[str, Any]
    gaps_identified: List[str]
    next_focus_area: Optional[str] = None


class ConversationSynthesizer:
    """
    Advanced conversation synthesizer for creating coherent, contextual responses.
    
    Combines agent outputs with conversation context to create appropriate responses
    that guide users through the strategic thinking process.
    """
    
    def __init__(self):
        """Initialize the synthesizer with response templates and strategies."""
        self.response_templates = self._build_response_templates()
        self.phase_transitions = self._build_phase_transition_logic()
        self.question_strategies = self._build_question_strategies()
        logger.info("Conversation Synthesizer initialized")
    
    def synthesize_response(self, state: AgentState) -> str:
        """
        Synthesize a coherent response based on agent output and conversation context.
        Enforces bias-aware guidelines from Choi & Pak (2005).
        
        Args:
            state: Current agent state
            
        Returns:
            Synthesized response string (150-200 words max with single question)
        """
        logger.info(f"Synthesizing response for session {state['session_id']}")
        
        # Build synthesis context
        context = self._build_synthesis_context(state)
        
        # Determine response type
        response_type = self._determine_response_type(context, state)
        
        # Generate response based on type and context
        response = self._generate_response(response_type, context, state)
        
        # Apply length constraints (150-200 words target)
        response = self._enforce_length_limit(response, max_words=200)
        
        # Add ONE follow-up question if appropriate
        if self._should_add_questions(context, response_type):
            question = self._generate_single_question(context, state)
            if question:
                response += f"\n\n{question}"
        
        # Add brief progress indication only if significant milestone
        if context.strategy_completeness in [25, 50, 75, 90]:
            progress_note = self._generate_brief_progress_note(context)
            if progress_note:
                response += f"\n\n{progress_note}"
        
        logger.info(f"Response synthesized ({response_type.value}, {len(response)} chars, ~{len(response.split())} words)")
        return response
    
    def _build_synthesis_context(self, state: AgentState) -> SynthesisContext:
        """Build context for response synthesis."""
        current_agent = state.get("current_agent", "unknown")
        agent_output = state.get("agent_output", "")
        completeness = calculate_strategy_completeness(state)
        current_phase = state["current_phase"]
        conversation_turn = len(state["conversation_history"]) // 2
        
        # Extract user intent summary from routing context if available
        routing_context = state.get("routing_context", {})
        user_intent_summary = routing_context.get("user_intent_summary", {})
        
        # Identify gaps in strategy
        gaps = [k for k, v in state["strategy_completeness"].items() if not v]
        
        # Determine next focus area
        next_focus = self._identify_next_focus_area(state, gaps)
        
        return SynthesisContext(
            current_agent=current_agent,
            agent_output=agent_output,
            strategy_completeness=completeness,
            current_phase=current_phase,
            conversation_turn=conversation_turn,
            user_intent_summary=user_intent_summary,
            gaps_identified=gaps,
            next_focus_area=next_focus
        )
    
    def _determine_response_type(self, context: SynthesisContext, state: AgentState) -> ResponseType:
        """Determine the appropriate type of response to generate."""
        
        # Completion response if strategy is nearly done
        if context.strategy_completeness >= 90:
            return ResponseType.COMPLETION
        
        # Summary response if high completeness or user requested it
        if (context.strategy_completeness >= 70 or
            any("summary" in signal for signal in 
                context.user_intent_summary.get("completion_signals", []))):
            return ResponseType.SUMMARY
        
        # Question response for early conversation or when user needs clarification
        if (context.conversation_turn < 3 or
            context.user_intent_summary.get("needs_clarification", False) or
            len(context.gaps_identified) > 3):
            return ResponseType.QUESTION
        
        # Insight response when processing agent output
        if (context.current_agent in ["why_agent", "analogy_agent", "logic_agent"] and
            context.agent_output and len(context.agent_output) > 20):
            return ResponseType.INSIGHT
        
        # Default to guidance
        return ResponseType.GUIDANCE
    
    def _generate_response(self, response_type: ResponseType, context: SynthesisContext, state: AgentState) -> str:
        """Generate the core response based on type and context."""
        
        if response_type == ResponseType.COMPLETION:
            return self._generate_completion_response(context, state)
        elif response_type == ResponseType.SUMMARY:
            return self._generate_summary_response(context, state)
        elif response_type == ResponseType.QUESTION:
            return self._generate_question_response(context, state)
        elif response_type == ResponseType.INSIGHT:
            return self._generate_insight_response(context, state)
        else:  # GUIDANCE
            return self._generate_guidance_response(context, state)
    
    def _generate_completion_response(self, context: SynthesisContext, state: AgentState) -> str:
        """Generate a completion response when strategy is nearly finished."""
        templates = self.response_templates["completion"]
        
        if context.strategy_completeness >= 95:
            return ("🎉 Congratulations! We've successfully developed a comprehensive strategy for your organization. "
                   "Your strategic framework is now complete with a clear WHY (purpose and beliefs), "
                   "HOW (strategic approach and logic), and WHAT (implementation roadmap). "
                   "You're ready to move forward with confidence!")
        else:
            return ("We're very close to completing your strategic framework! "
                   f"At {context.strategy_completeness:.0f}% completion, we have most of the key elements in place. "
                   "Let's address the remaining areas to finalize your strategy.")
    
    def _generate_summary_response(self, context: SynthesisContext, state: AgentState) -> str:
        """Generate a summary response of current progress."""
        completed_areas = [k for k, v in state["strategy_completeness"].items() if v]
        
        summary = f"Here's where we stand with your strategy development:\n\n"
        
        # Progress overview
        summary += f"📈 **Overall Progress: {context.strategy_completeness:.0f}% Complete**\n\n"
        
        # Completed sections
        if completed_areas:
            summary += "✅ **Completed Areas:**\n"
            for area in completed_areas:
                area_name = area.replace("_", " ").title()
                summary += f"• {area_name}\n"
            summary += "\n"
        
        # Remaining areas
        if context.gaps_identified:
            summary += "🎯 **Next Focus Areas:**\n"
            priority_gaps = context.gaps_identified[:3]  # Top 3 priorities
            for gap in priority_gaps:
                gap_name = gap.replace("_", " ").title()
                summary += f"• {gap_name}\n"
        
        return summary
    
    def _generate_question_response(self, context: SynthesisContext, state: AgentState) -> str:
        """Generate a question-based response to gather more information."""
        
        if context.current_phase == "why" and "why" in context.gaps_identified:
            return ("Let's start by exploring your organization's core purpose. "
                   "Understanding your 'WHY' - the fundamental reason your organization exists - "
                   "will form the foundation of your entire strategy.")
        
        elif context.current_phase == "how" and not state["strategy_completeness"]["why"]:
            return ("Before we dive into strategic approaches, let's ensure we have a solid foundation. "
                   "Your organization's purpose and core beliefs will guide how you approach strategy.")
        
        elif context.next_focus_area:
            focus_area = context.next_focus_area.replace("_", " ").title()
            return f"Let's focus on developing your {focus_area}. This will help us move forward strategically."
        
        else:
            return ("I'd like to understand more about your specific situation. "
                   "What aspect of your strategy development feels most important or urgent to you right now?")
    
    def _generate_insight_response(self, context: SynthesisContext, state: AgentState) -> str:
        """Generate an insight-based response building on agent output."""
        
        if context.current_agent == "why_agent":
            return ("Excellent work on clarifying your organization's core purpose! "
                   "Having a clear WHY provides the foundation for all strategic decisions. "
                   "This purpose will help guide how you approach challenges and opportunities.")
        
        elif context.current_agent == "analogy_agent":
            return ("Great strategic thinking! By drawing analogies and examining how others have succeeded, "
                   "you're developing a clearer picture of your own strategic approach. "
                   "These insights will help shape your unique path forward.")
        
        elif context.current_agent == "logic_agent":
            return ("Your strategic reasoning is becoming more structured and logical. "
                   "This solid logical foundation ensures your strategy is not just inspiring "
                   "but also practically sound and defensible.")
        
        elif context.current_agent == "open_strategy_agent":
            return ("You're making excellent progress on the implementation aspects of your strategy. "
                   "Having clear stakeholder engagement and processes will be crucial for successful execution.")
        
        else:
            return ("We're making good progress on your strategic development. "
                   "Each piece we develop strengthens your overall strategic framework.")
    
    def _generate_guidance_response(self, context: SynthesisContext, state: AgentState) -> str:
        """Generate a guidance response to help user move forward."""
        
        if context.strategy_completeness < 25:
            return ("We're in the early stages of developing your strategy. "
                   "Let's focus on building a strong foundation by clearly establishing "
                   "your organization's core purpose and fundamental beliefs.")
        
        elif context.strategy_completeness < 50:
            return ("You've established good foundational elements. Now let's develop "
                   "the strategic reasoning and approaches that will guide your organization forward.")
        
        elif context.strategy_completeness < 75:
            return ("Your strategy is taking shape well! Let's now focus on the practical "
                   "implementation aspects - how you'll engage stakeholders and execute your vision.")
        
        else:
            return ("You're in the final stages of strategy development! "
                   "Let's ensure all elements are well-integrated and you're ready for implementation.")
    
    def _should_add_questions(self, context: SynthesisContext, response_type: ResponseType) -> bool:
        """Determine if follow-up questions should be added."""
        # Always add questions for early conversation
        if context.conversation_turn < 2:
            return True
        
        # Add questions if user needs clarification
        if context.user_intent_summary.get("needs_clarification", False):
            return True
        
        # Add questions for guidance and question response types
        if response_type in [ResponseType.QUESTION, ResponseType.GUIDANCE]:
            return True
        
        # Don't add questions for completion responses
        if response_type == ResponseType.COMPLETION:
            return False
        
        return context.strategy_completeness < 80  # Add questions until near completion
    
    def _generate_follow_up_questions(self, context: SynthesisContext, state: AgentState) -> Optional[str]:
        """Generate appropriate follow-up questions based on context."""
        
        # Questions based on current phase and gaps
        if context.current_phase == "why" and "why" in context.gaps_identified:
            questions = [
                "What is the fundamental purpose that drives your organization?",
                "What core beliefs or values are non-negotiable for your organization?",
                "What impact do you ultimately want to have in the world?"
            ]
        
        elif context.current_phase == "how":
            if "analogy_analysis" in context.gaps_identified:
                questions = [
                    "Can you think of other organizations or examples that approach challenges similarly to how you'd like to?",
                    "What successful strategies have you observed in your industry or elsewhere that resonate with you?",
                    "Are there any companies or approaches you admire that might inform your strategy?"
                ]
            elif "logical_structure" in context.gaps_identified:
                questions = [
                    "What assumptions are you making about your market or customers?",
                    "What evidence supports your strategic approach?",
                    "How do your different strategic elements connect and support each other?"
                ]
            else:
                questions = [
                    "How do you want to differentiate your approach from competitors?",
                    "What capabilities will be most important for your success?"
                ]
        
        elif context.current_phase == "what":
            remaining_what_gaps = [g for g in context.gaps_identified 
                                 if g in ["stakeholder_customer", "internal_processes", "learning_growth", "value_creation"]]
            if remaining_what_gaps:
                questions = [
                    "Who are your key stakeholders and how will you engage them?",
                    "What internal processes and capabilities need to be developed?",
                    "How will you measure success and ensure continuous improvement?"
                ]
            else:
                questions = [
                    "What would successful implementation look like in 6-12 months?",
                    "What are the biggest potential obstacles to implementing your strategy?"
                ]
        
        else:
            # General questions based on user intent
            if context.user_intent_summary.get("has_questions", False):
                questions = [
                    "What specific aspects would you like to explore further?",
                    "What questions do you have about your strategic development so far?"
                ]
            else:
                questions = [
                    "What feels most important to focus on next?",
                    "Are there any areas where you'd like to dive deeper?"
                ]
        
        if not questions:
            return None
        
        # Select the most appropriate question (simple selection for now)
        selected_question = questions[0] if questions else None
        
        if selected_question:
            return f"**Question for you:** {selected_question}"
        
        return None
    
    def _generate_progress_note(self, context: SynthesisContext) -> Optional[str]:
        """Generate a progress indication note."""
        if context.strategy_completeness < 20:
            return "🌱 **Progress:** Just getting started - building your strategic foundation"
        elif context.strategy_completeness < 40:
            return "🚀 **Progress:** Early development - core elements taking shape"  
        elif context.strategy_completeness < 60:
            return "⚡ **Progress:** Good momentum - strategic framework developing well"
        elif context.strategy_completeness < 80:
            return "🎯 **Progress:** Strong progress - strategy becoming well-defined"
        elif context.strategy_completeness < 95:
            return "✨ **Progress:** Nearly complete - finalizing your strategic framework"
        else:
            return "🏆 **Status:** Strategy development complete!"
    
    def _identify_next_focus_area(self, state: AgentState, gaps: List[str]) -> Optional[str]:
        """Identify the next logical focus area based on phase and completeness."""
        current_phase = state["current_phase"]
        
        # Priority order based on strategic development flow
        if current_phase == "why":
            if "why" in gaps:
                return "why"
        
        elif current_phase == "how":
            if "analogy_analysis" in gaps:
                return "analogy_analysis"
            elif "logical_structure" in gaps:
                return "logical_structure"
        
        elif current_phase == "what":
            # Prioritize stakeholder and value creation for what phase
            what_priorities = ["stakeholder_customer", "value_creation", "internal_processes", "learning_growth"]
            for priority in what_priorities:
                if priority in gaps:
                    return priority
        
        # Return first gap if no phase-specific priority found
        return gaps[0] if gaps else None
    
    def _build_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Build response templates for different scenarios."""
        return {
            "completion": {
                "high": "🎉 Excellent work! Your strategy is nearly complete.",
                "full": "🏆 Congratulations! Your strategic framework is now complete."
            },
            "progress": {
                "early": "We're building a strong foundation for your strategy.",
                "middle": "Your strategic framework is taking shape well.",
                "advanced": "We're in the final stages of strategy development."
            },
            "transitions": {
                "why_to_how": "With your purpose clear, let's explore strategic approaches.",
                "how_to_what": "Now that we understand your strategic reasoning, let's focus on implementation.",
                "what_to_complete": "Let's bring all the pieces together into a cohesive strategy."
            }
        }
    
    def _build_phase_transition_logic(self) -> Dict[str, Any]:
        """Build logic for managing phase transitions in responses."""
        return {
            "why_complete_threshold": 0.8,
            "how_complete_threshold": 0.6,
            "what_complete_threshold": 0.7
        }
    
    def _build_question_strategies(self) -> Dict[str, List[str]]:
        """Build question strategies for different contexts."""
        return {
            "opening": [
                "What's the most important challenge you're trying to address?",
                "What inspired you to develop or refine your strategy?",
                "What does success look like for your organization?"
            ],
            "why_phase": [
                "What drives your organization's existence?",
                "What core beliefs guide your decisions?",
                "What impact do you want to have?"
            ],
            "how_phase": [
                "What approach feels most natural for your organization?",
                "How do you want to be different from others in your space?",
                "What capabilities are your strongest assets?"
            ],
            "what_phase": [
                "Who needs to be involved for success?",
                "What processes will support your strategy?",
                "How will you measure progress?"
            ]
        }
    
    def _enforce_length_limit(self, text: str, max_words: int = 200) -> str:
        """
        Enforce word count limits on response text.
        Based on Choi & Pak (2005) guidelines to avoid response fatigue.
        
        Args:
            text: Original text
            max_words: Maximum word count (default 200)
            
        Returns:
            Truncated text if necessary
        """
        words = text.split()
        if len(words) <= max_words:
            return text
        
        # Truncate intelligently at sentence boundary
        truncated_words = words[:max_words]
        truncated_text = ' '.join(truncated_words)
        
        # Find last complete sentence
        last_period = truncated_text.rfind('.')
        last_question = truncated_text.rfind('?')
        last_exclamation = truncated_text.rfind('!')
        
        last_sentence_end = max(last_period, last_question, last_exclamation)
        if last_sentence_end > 0:
            return truncated_text[:last_sentence_end + 1]
        
        return truncated_text + "..."
    
    def _generate_single_question(self, context: SynthesisContext, state: AgentState) -> str:
        """
        Generate a single, unbiased question based on context.
        Avoids multiple questions per Choi & Pak (2005).
        
        Args:
            context: Synthesis context
            state: Agent state
            
        Returns:
            Single focused question or empty string
        """
        # Get appropriate questions for phase
        phase_questions = self._generate_phase_appropriate_questions(context, state)
        
        if not phase_questions:
            return ""
        
        # Select the most relevant single question
        selected_question = self._select_most_relevant_question(phase_questions, context)
        
        # Ensure question is not leading or biased
        return self._make_question_unbiased(selected_question)
    
    def _generate_brief_progress_note(self, context: SynthesisContext) -> str:
        """
        Generate a brief progress indicator for milestone completions.
        
        Args:
            context: Synthesis context
            
        Returns:
            Brief progress note or empty string
        """
        completeness = int(context.strategy_completeness)
        
        if completeness == 25:
            return "📊 Strategy foundation 25% complete."
        elif completeness == 50:
            return "📊 Halfway through strategy development."
        elif completeness == 75:
            return "📊 Strategy 75% complete - finalizing details."
        elif completeness == 90:
            return "📊 Nearly complete - review and refine."
        
        return ""
    
    def _generate_phase_appropriate_questions(self, context: SynthesisContext, state: AgentState) -> List[str]:
        """Generate questions appropriate for current phase."""
        questions = []
        
        if context.current_phase == "why":
            if "why" not in state["strategy_completeness"] or not state["strategy_completeness"]["why"]:
                questions = [
                    "What inspired the founding of your organization?",
                    "What change do you want to create in the world?",
                    "What drives your passion for this work?"
                ]
        elif context.current_phase == "how":
            questions = [
                "What approaches have worked well in your industry?",
                "How do you currently make strategic decisions?",
                "What patterns do you see in successful strategies?"
            ]
        elif context.current_phase == "what":
            questions = [
                "Who are the key stakeholders for implementation?",
                "What resources will be needed?",
                "How will you measure success?"
            ]
        
        return questions
    
    def _select_most_relevant_question(self, questions: List[str], context: SynthesisContext) -> str:
        """Select the most relevant question from a list."""
        if not questions:
            return ""
        
        # For now, select based on gaps identified
        # In future, could use more sophisticated relevance scoring
        if context.gaps_identified:
            # Prioritize questions related to gaps
            return questions[0]
        
        # Default to first question
        return questions[0]
    
    def _make_question_unbiased(self, question: str) -> str:
        """
        Ensure a question is unbiased and open-ended.
        Based on Choi & Pak (2005) bias catalog.
        
        Args:
            question: Original question
            
        Returns:
            Unbiased version of the question
        """
        # Remove leading phrases
        biased_starts = [
            "Don't you think",
            "Wouldn't you agree",
            "Isn't it true that",
            "Obviously",
            "Surely"
        ]
        
        for phrase in biased_starts:
            if question.lower().startswith(phrase.lower()):
                # Reframe as open question
                return "How would you describe your perspective on this?"
        
        # Check for false dichotomies
        if " or " in question and "?" in question:
            # Reframe to avoid forced choice
            topic = question.split(" or ")[0].split()[-1]
            return f"What factors influence your approach to {topic}?"
        
        # Return original if no bias detected
        return question