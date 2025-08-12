from typing import Dict, Any, List, Tuple, Optional
import re
from dataclasses import dataclass
import logging

from langchain_core.messages import BaseMessage

from ..models.state import AgentState, RouterDecision, calculate_strategy_completeness
from ..utils import get_logger


logger = get_logger(__name__)


@dataclass
class UserIntentSignals:
    """Signals extracted from user input to guide routing decisions."""
    
    # Purpose and meaning signals
    purpose_signals: List[str]
    why_signals: List[str]
    
    # Strategic thinking signals  
    strategy_signals: List[str]
    comparison_signals: List[str]
    logic_signals: List[str]
    
    # Implementation signals
    execution_signals: List[str]
    stakeholder_signals: List[str]
    process_signals: List[str]
    
    # Meta signals
    question_signals: List[str]
    clarification_signals: List[str]
    completion_signals: List[str]
    
    # Sentiment and urgency
    urgency_level: float  # 0.0 to 1.0
    confidence_level: float  # 0.0 to 1.0


class AdvancedRouter:
    """
    Advanced router with sophisticated user input analysis and agent selection logic.
    
    This router analyzes user input patterns, conversation context, and strategy
    completeness to make intelligent routing decisions between specialist agents.
    """
    
    def __init__(self):
        """Initialize the router with signal patterns and decision weights."""
        self.signal_patterns = self._build_signal_patterns()
        self.phase_transition_rules = self._build_phase_transition_rules()
        self.agent_capabilities = self._build_agent_capabilities()
        logger.info("Advanced Router initialized")
    
    def make_routing_decision(self, state: AgentState) -> RouterDecision:
        """
        Make an intelligent routing decision based on comprehensive state analysis.
        
        Args:
            state: Current agent state
            
        Returns:
            RouterDecision with next agent and reasoning
        """
        logger.info(f"Making routing decision for session {state['session_id']}")
        
        # Analyze user input and conversation context
        user_intent = self._analyze_user_intent(state)
        conversation_context = self._analyze_conversation_context(state)
        strategy_analysis = self._analyze_strategy_completeness(state)
        
        # Determine current phase and potential transitions
        current_phase = state["current_phase"]
        phase_recommendation = self._evaluate_phase_transition(
            state, user_intent, strategy_analysis
        )
        
        # Calculate agent scores based on multiple factors
        agent_scores = self._calculate_agent_scores(
            state, user_intent, conversation_context, strategy_analysis
        )
        
        # Select best agent based on scores and constraints
        selected_agent, reasoning = self._select_best_agent(
            agent_scores, current_phase, phase_recommendation, state
        )
        
        # Build final decision
        decision = RouterDecision(
            next_node=selected_agent,
            reasoning=reasoning,
            priority=self._calculate_priority(selected_agent, user_intent, strategy_analysis),
            context={
                "current_phase": current_phase,
                "recommended_phase": phase_recommendation,
                "user_intent_summary": self._summarize_user_intent(user_intent),
                "strategy_completeness": strategy_analysis["completeness_percentage"],
                "agent_scores": agent_scores,
                "conversation_turn": len(state["conversation_history"]) // 2
            }
        )
        
        logger.info(
            f"Routed to {selected_agent} (priority {decision['priority']}) - {reasoning}"
        )
        
        return decision
    
    def _analyze_user_intent(self, state: AgentState) -> UserIntentSignals:
        """Analyze user input to extract intent signals."""
        if not state["conversation_history"]:
            return self._default_user_intent()
        
        # Get recent user messages (last 3)
        user_messages = [
            msg.content for msg in state["conversation_history"][-6:]
            if hasattr(msg, 'content') and msg.content
        ][::2]  # Take every other message (user messages)
        
        if not user_messages:
            return self._default_user_intent()
        
        latest_input = user_messages[-1] if user_messages else ""
        all_input = " ".join(user_messages[-3:])  # Last 3 user inputs
        
        return UserIntentSignals(
            purpose_signals=self._extract_signals(all_input, self.signal_patterns["purpose"]),
            why_signals=self._extract_signals(all_input, self.signal_patterns["why"]),
            strategy_signals=self._extract_signals(all_input, self.signal_patterns["strategy"]),
            comparison_signals=self._extract_signals(all_input, self.signal_patterns["comparison"]),
            logic_signals=self._extract_signals(all_input, self.signal_patterns["logic"]),
            execution_signals=self._extract_signals(all_input, self.signal_patterns["execution"]),
            stakeholder_signals=self._extract_signals(all_input, self.signal_patterns["stakeholder"]),
            process_signals=self._extract_signals(all_input, self.signal_patterns["process"]),
            question_signals=self._extract_signals(latest_input, self.signal_patterns["questions"]),
            clarification_signals=self._extract_signals(latest_input, self.signal_patterns["clarification"]),
            completion_signals=self._extract_signals(all_input, self.signal_patterns["completion"]),
            urgency_level=self._calculate_urgency(latest_input),
            confidence_level=self._calculate_confidence(all_input)
        )
    
    def _analyze_conversation_context(self, state: AgentState) -> Dict[str, Any]:
        """Analyze broader conversation context and patterns."""
        conversation_history = state["conversation_history"]
        
        return {
            "turn_count": len(conversation_history) // 2,  # User-AI turn pairs
            "conversation_length": len(conversation_history),
            "recent_agent": state.get("current_agent"),
            "processing_stage": state.get("processing_stage"),
            "has_errors": state.get("error_state") is not None,
            "retry_count": state.get("retry_count", 0),
            "session_duration_estimate": self._estimate_session_duration(state),
            "conversation_momentum": self._calculate_momentum(conversation_history)
        }
    
    def _analyze_strategy_completeness(self, state: AgentState) -> Dict[str, Any]:
        """Analyze current strategy development progress."""
        completeness = state["strategy_completeness"]
        overall_percentage = calculate_strategy_completeness(state)
        
        # Identify gaps and priorities
        incomplete_sections = [k for k, v in completeness.items() if not v]
        phase_completeness = {
            "why": completeness.get("why", False),
            "how": (completeness.get("analogy_analysis", False) and 
                   completeness.get("logical_structure", False)),
            "what": (completeness.get("stakeholder_customer", False) and 
                    completeness.get("internal_processes", False) and 
                    completeness.get("learning_growth", False) and 
                    completeness.get("value_creation", False))
        }
        
        return {
            "completeness_percentage": overall_percentage,
            "incomplete_sections": incomplete_sections,
            "phase_completeness": phase_completeness,
            "identified_gaps": state.get("identified_gaps", []),
            "next_priority_section": self._identify_next_priority_section(completeness, state["current_phase"]),
            "readiness_for_next_phase": self._assess_phase_readiness(phase_completeness, state["current_phase"])
        }
    
    def _calculate_agent_scores(
        self,
        state: AgentState,
        user_intent: UserIntentSignals,
        conversation_context: Dict[str, Any],
        strategy_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate scores for each agent based on multiple factors."""
        
        scores = {}
        
        # WHY Agent scoring
        scores["why_agent"] = self._score_why_agent(
            user_intent, strategy_analysis, state["current_phase"]
        )
        
        # Analogy Agent scoring
        scores["analogy_agent"] = self._score_analogy_agent(
            user_intent, strategy_analysis, conversation_context
        )
        
        # Logic Agent scoring
        scores["logic_agent"] = self._score_logic_agent(
            user_intent, strategy_analysis, conversation_context
        )
        
        # Open Strategy Agent scoring
        scores["open_strategy_agent"] = self._score_open_strategy_agent(
            user_intent, strategy_analysis, state["current_phase"]
        )
        
        # Strategy Map Agent scoring (handled in orchestrator)
        scores["strategy_map_agent"] = self._score_strategy_map_agent(
            strategy_analysis, state["current_phase"]
        )
        
        # Synthesize/End scoring
        scores["synthesize"] = self._score_synthesis(
            strategy_analysis, conversation_context, user_intent
        )
        
        return scores
    
    def _score_why_agent(
        self, 
        user_intent: UserIntentSignals,
        strategy_analysis: Dict[str, Any],
        current_phase: str
    ) -> float:
        """Calculate score for WHY Agent."""
        score = 0.0
        
        # Strong signals for WHY Agent
        score += len(user_intent.purpose_signals) * 0.3
        score += len(user_intent.why_signals) * 0.4
        
        # Phase alignment
        if current_phase == "why":
            score += 0.5
        
        # Incompleteness bonus
        if not strategy_analysis["phase_completeness"]["why"]:
            score += 0.6
        
        # Question patterns that suggest purpose exploration
        purpose_questions = [s for s in user_intent.question_signals 
                           if any(keyword in s.lower() for keyword in ["why", "purpose", "mission", "vision"])]
        score += len(purpose_questions) * 0.2
        
        return min(score, 1.0)
    
    def _score_analogy_agent(
        self,
        user_intent: UserIntentSignals,
        strategy_analysis: Dict[str, Any],
        conversation_context: Dict[str, Any]
    ) -> float:
        """Calculate score for Analogy Agent."""
        score = 0.0
        
        # Strong signals for analogical reasoning
        score += len(user_intent.comparison_signals) * 0.4
        score += len(user_intent.strategy_signals) * 0.3
        
        # Phase alignment - strongest in "how" phase
        current_phase = strategy_analysis.get("phase_completeness", {})
        if current_phase.get("why", False) and not current_phase.get("how", False):
            score += 0.5
        
        # Look for comparison language in recent conversation
        comparison_indicators = len([s for s in user_intent.comparison_signals 
                                   if any(word in s.lower() for word in ["like", "similar", "compare", "example"])])
        score += comparison_indicators * 0.2
        
        return min(score, 1.0)
    
    def _score_logic_agent(
        self,
        user_intent: UserIntentSignals,
        strategy_analysis: Dict[str, Any],
        conversation_context: Dict[str, Any]
    ) -> float:
        """Calculate score for Logic Agent."""
        score = 0.0
        
        # Strong signals for logical validation
        score += len(user_intent.logic_signals) * 0.4
        
        # Good for validating existing strategy elements
        if strategy_analysis["completeness_percentage"] > 30:
            score += 0.3
        
        # Questions about logic, reasoning, or validation
        logic_questions = [s for s in user_intent.question_signals 
                         if any(keyword in s.lower() for keyword in ["how", "why", "logic", "reason", "validate"])]
        score += len(logic_questions) * 0.2
        
        # Useful after analogy work
        if "analogy_analysis" not in strategy_analysis["incomplete_sections"]:
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_open_strategy_agent(
        self,
        user_intent: UserIntentSignals,
        strategy_analysis: Dict[str, Any],
        current_phase: str
    ) -> float:
        """Calculate score for Open Strategy Agent."""
        score = 0.0
        
        # Strong signals for implementation planning
        score += len(user_intent.execution_signals) * 0.4
        score += len(user_intent.stakeholder_signals) * 0.3
        score += len(user_intent.process_signals) * 0.3
        
        # Most relevant in "what" phase or when strategy is well-developed
        if current_phase == "what":
            score += 0.4
        
        if strategy_analysis["completeness_percentage"] > 60:
            score += 0.3
        
        # Implementation-focused questions
        impl_questions = [s for s in user_intent.question_signals
                         if any(keyword in s.lower() for keyword in ["implement", "execute", "stakeholder", "process"])]
        score += len(impl_questions) * 0.2
        
        return min(score, 1.0)
    
    def _score_strategy_map_agent(
        self,
        strategy_analysis: Dict[str, Any],
        current_phase: str
    ) -> float:
        """Calculate score for Strategy Map Agent."""
        score = 0.0
        
        # Most relevant when building strategy structure
        if current_phase == "what":
            score += 0.4
        
        # Needed when core sections are incomplete
        incomplete_core_sections = [
            section for section in ["stakeholder_customer", "internal_processes", 
                                  "learning_growth", "value_creation"]
            if section in strategy_analysis["incomplete_sections"]
        ]
        score += len(incomplete_core_sections) * 0.2
        
        return min(score, 1.0)
    
    def _score_synthesis(
        self,
        strategy_analysis: Dict[str, Any],
        conversation_context: Dict[str, Any],
        user_intent: UserIntentSignals
    ) -> float:
        """Calculate score for synthesis/completion."""
        score = 0.0
        
        # High completeness suggests synthesis
        completeness = strategy_analysis["completeness_percentage"]
        if completeness > 70:
            score += (completeness - 70) / 30 * 0.6  # Scale from 0 to 0.6
        
        # Completion signals from user
        score += len(user_intent.completion_signals) * 0.3
        
        # Long conversation suggests need for synthesis
        if conversation_context["turn_count"] > 10:
            score += 0.2
        
        return min(score, 1.0)
    
    def _select_best_agent(
        self,
        agent_scores: Dict[str, float],
        current_phase: str,
        phase_recommendation: Optional[str],
        state: AgentState
    ) -> Tuple[str, str]:
        """Select the best agent based on scores and constraints."""
        
        # Handle error states
        if state.get("error_state"):
            return "end", "Session ended due to error state"
        
        # Handle high retry counts
        if state.get("retry_count", 0) > 5:
            return "end", "Session ended due to retry limit exceeded"
        
        # Find highest scoring agent
        best_agent = max(agent_scores, key=agent_scores.get)
        best_score = agent_scores[best_agent]
        
        # Apply constraints and fallbacks
        
        # If synthesis scores highest and strategy is sufficiently complete
        if best_agent == "synthesize" and best_score > 0.4:
            return "synthesize", f"Strategy synthesis ready (score: {best_score:.2f})"
        
        # Ensure we don't repeat the same agent too often
        recent_agent = state.get("current_agent")
        if recent_agent == best_agent and best_score < 0.8:
            # Look for second-best agent
            remaining_scores = {k: v for k, v in agent_scores.items() 
                              if k != best_agent and k != "synthesize"}
            if remaining_scores:
                second_best = max(remaining_scores, key=remaining_scores.get)
                if remaining_scores[second_best] > 0.3:
                    return second_best, f"Diversifying from {recent_agent} to {second_best} (score: {remaining_scores[second_best]:.2f})"
        
        # Default to best scoring agent
        reasoning = self._generate_reasoning(best_agent, best_score, current_phase, state)
        return best_agent, reasoning
    
    def _generate_reasoning(
        self,
        selected_agent: str,
        score: float,
        current_phase: str,
        state: AgentState
    ) -> str:
        """Generate human-readable reasoning for the routing decision."""
        
        agent_purposes = {
            "why_agent": "explore core purpose and organizational WHY",
            "analogy_agent": "develop strategic reasoning through analogies",
            "logic_agent": "validate and structure strategic arguments",
            "open_strategy_agent": "plan implementation and stakeholder engagement",
            "strategy_map_agent": "build comprehensive strategy map components"
        }
        
        purpose = agent_purposes.get(selected_agent, "process user input")
        completeness = calculate_strategy_completeness(state)
        
        return f"Selected {selected_agent} to {purpose} (score: {score:.2f}, phase: {current_phase}, {completeness:.1f}% complete)"
    
    def _calculate_priority(
        self,
        selected_agent: str,
        user_intent: UserIntentSignals,
        strategy_analysis: Dict[str, Any]
    ) -> int:
        """Calculate priority level for the routing decision."""
        
        priority = 1  # Default priority
        
        # High priority for foundational work
        if selected_agent == "why_agent" and not strategy_analysis["phase_completeness"]["why"]:
            priority = 3
        
        # High urgency from user input
        if user_intent.urgency_level > 0.7:
            priority = max(priority, 3)
        
        # Lower priority for synthesis unless strategy is very complete
        if selected_agent == "synthesize" and strategy_analysis["completeness_percentage"] < 80:
            priority = 1
        
        return priority
    
    # Helper methods for signal extraction and analysis
    
    def _build_signal_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for different types of user intent signals."""
        return {
            "purpose": [
                r"\b(purpose|mission|vision|why|meaning|goal|objective)\b",
                r"\b(what.*for|why.*exist|why.*matter)\b",
                r"\b(core.*purpose|fundamental.*goal)\b"
            ],
            "why": [
                r"\bwhy\b",
                r"\b(reason|cause|motivation|drive|inspire)\b",
                r"\b(believe.*in|passionate.*about|care.*about)\b"
            ],
            "strategy": [
                r"\b(strategy|strategic|approach|method|plan|planning)\b",
                r"\b(competitive|advantage|differentiat)\b",
                r"\b(market|position|opportunit)\b"
            ],
            "comparison": [
                r"\b(like|similar|compare|example|analogy|model)\b",
                r"\b(reminds.*of|looks.*like|works.*like)\b",
                r"\b(other.*companies|competitors|industry)\b"
            ],
            "logic": [
                r"\b(logic|logical|reason|rational|valid|argument)\b",
                r"\b(makes.*sense|sound|consistent|coherent)\b",
                r"\b(evidence|proof|support|justify)\b"
            ],
            "execution": [
                r"\b(implement|execution|execute|deploy|launch)\b",
                r"\b(action|steps|process|workflow|timeline)\b",
                r"\b(how.*do|how.*implement|how.*execute)\b"
            ],
            "stakeholder": [
                r"\b(stakeholder|customer|user|team|employee|investor)\b",
                r"\b(people|person|audience|community|partner)\b",
                r"\b(buy.in|support|engagement|involvement)\b"
            ],
            "process": [
                r"\b(process|procedure|workflow|system|method)\b",
                r"\b(step.*step|phase|stage|milestone)\b",
                r"\b(organize|structure|framework)\b"
            ],
            "questions": [
                r"\?",
                r"\b(what|how|why|when|where|who)\b",
                r"\b(should.*I|can.*I|would.*I)\b"
            ],
            "clarification": [
                r"\b(unclear|confus|understand|explain|clarify)\b",
                r"\b(what.*mean|don't.*get|not.*sure)\b",
                r"\b(help.*me|show.*me|tell.*me)\b"
            ],
            "completion": [
                r"\b(done|finished|complete|ready|final)\b",
                r"\b(summary|overview|wrap.*up)\b",
                r"\b(next.*step|what.*now|move.*forward)\b"
            ]
        }
    
    def _build_phase_transition_rules(self) -> Dict[str, Any]:
        """Build rules for phase transitions."""
        return {
            "why_to_how": {
                "required_completeness": ["why"],
                "confidence_threshold": 0.7,
                "min_purpose_clarity": 0.6
            },
            "how_to_what": {
                "required_completeness": ["why", "analogy_analysis"],
                "confidence_threshold": 0.6,
                "strategic_logic_score": 0.5
            },
            "what_to_review": {
                "required_completeness": ["stakeholder_customer", "value_creation"],
                "overall_completeness": 70
            }
        }
    
    def _build_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Build agent capability definitions."""
        return {
            "why_agent": {
                "primary_phase": "why",
                "capabilities": ["purpose_discovery", "belief_exploration", "value_identification"],
                "output_types": ["purpose_statement", "core_beliefs", "organizational_values"]
            },
            "analogy_agent": {
                "primary_phase": "how",
                "capabilities": ["analogical_reasoning", "causal_analysis", "strategic_comparison"],
                "output_types": ["strategic_analogy", "causal_theory", "success_model"]
            },
            "logic_agent": {
                "primary_phase": "how",
                "capabilities": ["logical_validation", "argument_structure", "consistency_check"],
                "output_types": ["logical_framework", "argument_map", "validation_results"]
            },
            "open_strategy_agent": {
                "primary_phase": "what",
                "capabilities": ["implementation_planning", "stakeholder_engagement", "process_design"],
                "output_types": ["implementation_plan", "stakeholder_map", "engagement_strategy"]
            }
        }
    
    def _extract_signals(self, text: str, patterns: List[str]) -> List[str]:
        """Extract signals from text using regex patterns."""
        if not text:
            return []
        
        signals = []
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            signals.extend(matches)
        
        return signals
    
    def _calculate_urgency(self, text: str) -> float:
        """Calculate urgency level from user input."""
        urgency_indicators = [
            "urgent", "asap", "quickly", "immediate", "rush", "deadline",
            "need.*now", "right.*away", "urgent", "critical", "priority"
        ]
        
        urgency_count = sum(1 for pattern in urgency_indicators 
                           if re.search(pattern, text.lower()))
        
        return min(urgency_count * 0.3, 1.0)
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence level from user input."""
        confidence_indicators = [
            "sure", "certain", "confident", "know", "clear", "obvious"
        ]
        
        uncertainty_indicators = [
            "unsure", "uncertain", "confused", "unclear", "maybe", "perhaps",
            "don't know", "not sure", "help"
        ]
        
        confidence_count = sum(1 for pattern in confidence_indicators
                              if re.search(pattern, text.lower()))
        
        uncertainty_count = sum(1 for pattern in uncertainty_indicators
                               if re.search(pattern, text.lower()))
        
        base_confidence = 0.5
        confidence_boost = confidence_count * 0.2
        uncertainty_penalty = uncertainty_count * 0.2
        
        return max(0.0, min(1.0, base_confidence + confidence_boost - uncertainty_penalty))
    
    def _default_user_intent(self) -> UserIntentSignals:
        """Return default user intent when no input is available."""
        return UserIntentSignals(
            purpose_signals=["purpose"],  # Default to purpose exploration
            why_signals=[],
            strategy_signals=[],
            comparison_signals=[],
            logic_signals=[],
            execution_signals=[],
            stakeholder_signals=[],
            process_signals=[],
            question_signals=[],
            clarification_signals=[],
            completion_signals=[],
            urgency_level=0.5,
            confidence_level=0.5
        )
    
    def _evaluate_phase_transition(
        self,
        state: AgentState,
        user_intent: UserIntentSignals,
        strategy_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """Evaluate if a phase transition is recommended."""
        current_phase = state["current_phase"]
        phase_completeness = strategy_analysis["phase_completeness"]
        
        # Why to How transition
        if (current_phase == "why" and 
            phase_completeness["why"] and 
            len(user_intent.strategy_signals) > 0):
            return "how"
        
        # How to What transition
        if (current_phase == "how" and 
            phase_completeness["how"] and
            len(user_intent.execution_signals) > 0):
            return "what"
        
        return None
    
    def _analyze_conversation_context(self, state: AgentState) -> Dict[str, Any]:
        """Analyze broader conversation context and patterns."""
        conversation_history = state["conversation_history"]
        
        return {
            "turn_count": len(conversation_history) // 2,
            "conversation_length": len(conversation_history),
            "recent_agent": state.get("current_agent"),
            "processing_stage": state.get("processing_stage"),
            "has_errors": state.get("error_state") is not None,
            "retry_count": state.get("retry_count", 0),
            "session_duration_estimate": 0,  # Simplified
            "conversation_momentum": 0.5    # Simplified
        }
    
    def _estimate_session_duration(self, state: AgentState) -> float:
        """Estimate session duration in minutes (simplified)."""
        return len(state["conversation_history"]) * 2  # 2 minutes per exchange
    
    def _calculate_momentum(self, conversation_history: List[BaseMessage]) -> float:
        """Calculate conversation momentum (simplified)."""
        if len(conversation_history) < 4:
            return 0.5
        
        # Recent activity suggests higher momentum
        return min(1.0, len(conversation_history) / 10)
    
    def _identify_next_priority_section(
        self, 
        completeness: Dict[str, bool],
        current_phase: str
    ) -> str:
        """Identify the next priority section to complete."""
        
        incomplete = [k for k, v in completeness.items() if not v]
        
        if current_phase == "why" and "why" in incomplete:
            return "why"
        elif current_phase == "how" and "analogy_analysis" in incomplete:
            return "analogy_analysis"
        elif current_phase == "what" and "stakeholder_customer" in incomplete:
            return "stakeholder_customer"
        
        return incomplete[0] if incomplete else "none"
    
    def _assess_phase_readiness(
        self,
        phase_completeness: Dict[str, bool],
        current_phase: str
    ) -> bool:
        """Assess if current phase is ready for transition."""
        
        if current_phase == "why":
            return phase_completeness["why"]
        elif current_phase == "how":
            return phase_completeness["how"]
        elif current_phase == "what":
            return phase_completeness["what"]
        
        return False
    
    def _summarize_user_intent(self, user_intent: UserIntentSignals) -> Dict[str, Any]:
        """Summarize user intent for context."""
        return {
            "primary_focus": self._identify_primary_focus(user_intent),
            "urgency": user_intent.urgency_level,
            "confidence": user_intent.confidence_level,
            "has_questions": len(user_intent.question_signals) > 0,
            "needs_clarification": len(user_intent.clarification_signals) > 0
        }
    
    def _identify_primary_focus(self, user_intent: UserIntentSignals) -> str:
        """Identify the primary focus area from user intent."""
        signal_counts = {
            "purpose": len(user_intent.purpose_signals) + len(user_intent.why_signals),
            "strategy": len(user_intent.strategy_signals) + len(user_intent.comparison_signals),
            "logic": len(user_intent.logic_signals),
            "execution": len(user_intent.execution_signals) + len(user_intent.process_signals),
            "stakeholders": len(user_intent.stakeholder_signals)
        }
        
        return max(signal_counts, key=signal_counts.get) if signal_counts else "general"