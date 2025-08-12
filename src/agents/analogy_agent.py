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


class AnalogyAgent:
    """
    Analogy Agent implementing Carroll & Sørensen's analogical reasoning framework.
    
    This agent helps develop strategic insights through analogical reasoning by:
    1. Source Domain Identification - Finding relevant analogies from other domains
    2. Structural Mapping - Identifying common relational structures
    3. Evaluation & Adaptation - Assessing analogy quality and adapting insights
    4. Strategic Integration - Applying analogical insights to strategy development
    
    Based on Carroll & Sørensen's research on analogical reasoning in strategy.
    """
    
    def __init__(self):
        """Initialize the Analogy Agent with Carroll & Sørensen framework prompts."""
        self.llm = get_llm_client()
        self.methodology = "Carroll & Sørensen's Analogical Reasoning Framework"
        self.focus_areas = ["source_identification", "structural_mapping", "evaluation_adaptation", "strategic_integration"]
        
        # Initialize prompts for different analogical reasoning stages
        self._init_prompts()
        
        logger.info("Analogy Agent initialized with Carroll & Sørensen framework")
    
    def _init_prompts(self):
        """Initialize the prompts for analogical reasoning exploration."""
        
        # Source Domain Identification Prompt
        self.source_identification_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "purpose_context", "company_context"],
            template="""You are a strategic consultant specializing in Carroll & Sørensen's analogical reasoning framework for strategy development.

METHODOLOGY: Analogical Reasoning for Strategic Insight
- Source Domain Identification: Finding relevant analogies from other domains/industries
- Structural Mapping: Identifying common relational structures and patterns
- Evaluation & Adaptation: Assessing analogy quality and adapting insights
- Strategic Integration: Applying analogical insights to develop strategy

CURRENT FOCUS: SOURCE DOMAIN IDENTIFICATION

Organization's Purpose Context:
{purpose_context}

Company Context:
{company_context}

Conversation so far:
{conversation_context}

User's latest input:
{user_input}

As an analogical reasoning specialist, help identify SOURCE DOMAINS for strategic insight:

1. **Domain Exploration**: Explore different industries, organizations, or contexts that might offer strategic insights
2. **Pattern Recognition**: Look for organizations or situations that face similar challenges or opportunities
3. **Success Model Identification**: Find examples of successful strategies that could provide analogical insight
4. **Cross-Industry Analysis**: Consider how different domains solve similar strategic problems

Key questions to explore:
- "What other industries or organizations face similar strategic challenges?"
- "Which successful companies or models might offer insights for your situation?"
- "What analogies from nature, sports, or other domains might be relevant?"
- "Which success stories resonate with your strategic context?"

Focus on identifying 2-3 promising source domains that could provide rich analogical material for strategy development. Look for domains where the underlying strategic patterns and challenges are similar, even if the surface details differ.

Remember: The best analogies often come from unexpected domains where the structural relationships mirror your strategic situation."""
        )
        
        # Structural Mapping Prompt
        self.structural_mapping_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "identified_sources", "target_context"],
            template="""You are continuing the analogical reasoning process, now focusing on STRUCTURAL MAPPING.

IDENTIFIED SOURCE DOMAINS:
{identified_sources}

TARGET DOMAIN (Your Organization):
{target_context}

Conversation context:
{conversation_context}

User input:
{user_input}

Now map the STRUCTURAL RELATIONSHIPS between source and target domains:

1. **Relational Structure Analysis**: Identify key relationships, processes, and patterns in both domains
2. **System Mapping**: Map how different elements interact in both the source and target domains
3. **Causal Pattern Identification**: Identify cause-effect relationships that exist in both domains
4. **Constraint Recognition**: Understand what limitations and enablers exist in both contexts

Key mapping questions:
- "What are the core relationships in the source domain that mirror your situation?"
- "How do the success factors in the analogy relate to your strategic context?"
- "What processes or mechanisms in the source domain could apply to your strategy?"
- "Where do the structural patterns align and where do they diverge?"

Focus on:
- **Functional relationships** (not just surface similarities)
- **Causal mechanisms** that drive success in both domains
- **Systematic patterns** that could transfer across contexts
- **Constraint patterns** that shape possibilities in both domains

Create clear mappings showing how elements in the source domain correspond to elements in your strategic situation."""
        )
        
        # Evaluation and Adaptation Prompt
        self.evaluation_adaptation_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "mapped_analogies", "strategic_context"],
            template="""You are continuing analogical reasoning with EVALUATION & ADAPTATION.

MAPPED ANALOGIES:
{mapped_analogies}

STRATEGIC CONTEXT:
{strategic_context}

Conversation context:
{conversation_context}

User input:
{user_input}

Now EVALUATE and ADAPT the analogical insights:

1. **Analogy Quality Assessment**: Evaluate how well the analogies fit your strategic situation
2. **Insight Extraction**: Extract key strategic insights from the analogical mapping
3. **Adaptation Process**: Adapt analogical insights to fit your specific context and constraints
4. **Limitation Recognition**: Identify where analogies break down or don't apply

Evaluation criteria:
- **Structural Similarity**: How well do the underlying patterns match?
- **Causal Relevance**: Do the cause-effect relationships translate meaningfully?
- **Contextual Fit**: How well does the analogy fit your industry and situation?
- **Actionability**: Can you derive concrete strategic actions from the analogy?

Key questions:
- "Which aspects of the analogy provide the strongest strategic insights?"
- "Where does the analogy work well and where does it break down?"
- "How do we need to adapt these insights for your specific context?"
- "What concrete strategic implications emerge from this analogical analysis?"

Provide:
- **Quality Assessment** of each analogy's relevance
- **Key Insights** that emerge from the analogical reasoning
- **Adapted Strategies** that fit your specific context
- **Implementation Considerations** based on analogical learning"""
        )
        
        # Strategic Integration Prompt
        self.strategic_integration_prompt = PromptTemplate(
            input_variables=["conversation_context", "purpose_context", "analogical_insights", "user_input"],
            template="""You are completing the analogical reasoning process with STRATEGIC INTEGRATION.

ORGANIZATION'S PURPOSE:
{purpose_context}

ANALOGICAL INSIGHTS DEVELOPED:
{analogical_insights}

Conversation history:
{conversation_context}

User input:
{user_input}

Now INTEGRATE analogical insights into coherent strategic approach:

1. **Strategic Synthesis**: Combine analogical insights with purpose to create strategic direction
2. **Approach Development**: Develop concrete strategic approaches based on analogical learning
3. **Implementation Framework**: Create framework for applying analogical insights
4. **Next Steps Identification**: Identify how to move from analogical insight to strategic action

Integration questions:
- "How do these analogical insights support and enhance your core purpose?"
- "What strategic approaches emerge from combining your WHY with these analogical insights?"
- "How can we integrate multiple analogical insights into a coherent strategy?"
- "What concrete next steps follow from this analogical reasoning?"

Provide a comprehensive synthesis that includes:

**ANALOGICAL STRATEGIC FRAMEWORK:**
[Clear framework showing how analogical insights inform strategy]

**KEY STRATEGIC INSIGHTS:**
[Primary insights derived from analogical reasoning]

**STRATEGIC APPROACH:**
[How your organization should approach strategy based on analogical learning]

**IMPLEMENTATION IMPLICATIONS:**
[What this means for how you execute and develop strategy]

**VALIDATION QUESTIONS:**
Ask questions to test whether the analogical insights feel authentic and applicable to their strategic context.

**TRANSITION TO WHAT:**
"Now that we've developed strategic insights through analogical reasoning, we can explore WHAT specific actions and implementation plans will bring this strategy to life."""
        )
    
    def process_user_input(self, state: AgentState, user_input: str) -> AgentState:
        """
        Process user input through the Analogy Agent's analogical reasoning framework.
        
        Args:
            state: Current agent state
            user_input: User's message content
            
        Returns:
            Updated agent state with Analogy Agent response
        """
        logger.info(f"Analogy Agent processing input for session {state['session_id']}")
        
        try:
            # Determine current analogical reasoning stage
            analogy_stage = self._determine_analogy_stage(state)
            logger.debug(f"Analogical reasoning stage: {analogy_stage}")
            
            # Extract conversation context and purpose
            conversation_context = self._extract_conversation_context(state)
            purpose_context = self._extract_purpose_context(state)
            user_context = state.get("user_context", {})
            
            # Generate response based on stage
            if analogy_stage == "source_identification":
                response = self._explore_source_domains(conversation_context, user_input, purpose_context, user_context)
                
            elif analogy_stage == "structural_mapping":
                identified_sources = self._extract_identified_sources(state)
                target_context = self._format_target_context(purpose_context, user_context)
                response = self._map_structures(conversation_context, user_input, identified_sources, target_context)
                
            elif analogy_stage == "evaluation_adaptation":
                mapped_analogies = self._extract_mapped_analogies(state)
                strategic_context = self._format_strategic_context(state)
                response = self._evaluate_and_adapt(conversation_context, user_input, mapped_analogies, strategic_context)
                
            elif analogy_stage == "strategic_integration":
                analogical_insights = self._extract_analogical_insights(state)
                response = self._integrate_strategy(conversation_context, purpose_context, analogical_insights, user_input)
                
            else:
                # Default to source identification
                response = self._explore_source_domains(conversation_context, user_input, purpose_context, user_context)
            
            # Update state with Analogy Agent insights
            state = self._update_state_with_insights(state, analogy_stage, response)
            
            # Add AI response to conversation
            ai_message = AIMessage(content=response)
            state["conversation_history"].append(ai_message)
            
            # Update processing metadata
            state = set_processing_stage(state, "analogy_agent_completed", "analogy_agent")
            state["agent_output"] = response
            
            logger.info(f"Analogy Agent completed processing for stage: {analogy_stage}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in Analogy Agent processing: {str(e)}")
            
            # Set error state but provide fallback response
            state["error_state"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "agent": "analogy_agent"
            }
            
            fallback_response = self._get_fallback_response()
            ai_message = AIMessage(content=fallback_response)
            state["conversation_history"].append(ai_message)
            state["agent_output"] = fallback_response
            
            return state
    
    def _determine_analogy_stage(self, state: AgentState) -> str:
        """Determine the current stage of analogical reasoning based on conversation progress."""
        
        conversation = state["conversation_history"]
        
        # Count different types of analogical content discovered
        source_indicators = 0
        mapping_indicators = 0
        evaluation_indicators = 0
        integration_indicators = 0
        
        # Analyze conversation for progress indicators
        for message in conversation:
            if hasattr(message, 'content') and message.content:
                content_lower = message.content.lower()
                
                # Source identification indicators
                if any(keyword in content_lower for keyword in [
                    "like", "similar to", "reminds me of", "other companies", "industry", "example", "analogy"
                ]):
                    source_indicators += 1
                
                # Structural mapping indicators
                if any(keyword in content_lower for keyword in [
                    "mapping", "relationship", "structure", "pattern", "mechanism", "process"
                ]):
                    mapping_indicators += 1
                
                # Evaluation indicators
                if any(keyword in content_lower for keyword in [
                    "evaluate", "assess", "quality", "fit", "adapt", "insight", "limitation"
                ]):
                    evaluation_indicators += 1
                
                # Integration indicators
                if any(keyword in content_lower for keyword in [
                    "integrate", "synthesis", "strategic approach", "framework", "implementation"
                ]):
                    integration_indicators += 1
        
        # Determine stage based on conversation progress
        conversation_turns = len(conversation) // 2  # User-AI pairs
        
        if conversation_turns >= 6 and source_indicators >= 2 and mapping_indicators >= 1:
            if evaluation_indicators >= 1:
                if integration_indicators >= 1:
                    return "strategic_integration"
                else:
                    return "evaluation_adaptation"
            else:
                return "evaluation_adaptation"
        elif conversation_turns >= 3 and source_indicators >= 1:
            return "structural_mapping"
        else:
            return "source_identification"
    
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
    
    def _extract_purpose_context(self, state: AgentState) -> str:
        """Extract purpose context from conversation history or state."""
        
        # Look for purpose-related content in conversation
        purpose_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "purpose", "why", "mission", "core", "exist"
                ]):
                    purpose_content.append(message.content)
        
        if purpose_content:
            return purpose_content[-1]  # Most recent purpose discussion
        
        # Check if WHY is completed in strategy completeness
        if state["strategy_completeness"].get("why", False):
            return "Organization has clarified core purpose and WHY"
        
        return "Purpose context being developed"
    
    def _explore_source_domains(self, conversation_context: str, user_input: str, 
                               purpose_context: str, user_context: Dict[str, Any]) -> str:
        """Generate response for source domain identification stage."""
        
        company_context = self._format_company_context(user_context)
        
        prompt = self.source_identification_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            purpose_context=purpose_context,
            company_context=company_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in source identification: {str(e)}")
            return self._get_fallback_source_response()
    
    def _map_structures(self, conversation_context: str, user_input: str,
                       identified_sources: str, target_context: str) -> str:
        """Generate response for structural mapping stage."""
        
        prompt = self.structural_mapping_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            identified_sources=identified_sources,
            target_context=target_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in structural mapping: {str(e)}")
            return self._get_fallback_mapping_response()
    
    def _evaluate_and_adapt(self, conversation_context: str, user_input: str,
                           mapped_analogies: str, strategic_context: str) -> str:
        """Generate response for evaluation and adaptation stage."""
        
        prompt = self.evaluation_adaptation_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            mapped_analogies=mapped_analogies,
            strategic_context=strategic_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in evaluation and adaptation: {str(e)}")
            return self._get_fallback_evaluation_response()
    
    def _integrate_strategy(self, conversation_context: str, purpose_context: str,
                           analogical_insights: str, user_input: str) -> str:
        """Generate response for strategic integration stage."""
        
        prompt = self.strategic_integration_prompt.format(
            conversation_context=conversation_context,
            purpose_context=purpose_context,
            analogical_insights=analogical_insights,
            user_input=user_input
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in strategic integration: {str(e)}")
            return self._get_fallback_integration_response()
    
    def _extract_identified_sources(self, state: AgentState) -> str:
        """Extract identified source domains from conversation history."""
        
        source_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "industry", "company", "organization", "example", "domain", "analogy"
                ]):
                    source_content.append(message.content)
        
        return source_content[-1] if source_content else "Source domains being identified"
    
    def _extract_mapped_analogies(self, state: AgentState) -> str:
        """Extract mapped analogies from conversation history."""
        
        mapping_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "mapping", "structure", "relationship", "pattern", "correspond"
                ]):
                    mapping_content.append(message.content)
        
        return mapping_content[-1] if mapping_content else "Structural mapping in progress"
    
    def _extract_analogical_insights(self, state: AgentState) -> str:
        """Extract analogical insights from conversation history."""
        
        insight_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "insight", "strategic", "approach", "learn", "adaptation"
                ]):
                    insight_content.append(message.content)
        
        return insight_content[-1] if insight_content else "Analogical insights developing"
    
    def _format_target_context(self, purpose_context: str, user_context: Dict[str, Any]) -> str:
        """Format target domain context for structural mapping."""
        
        context_parts = [f"Purpose: {purpose_context}"]
        
        if user_context:
            if "company_name" in user_context:
                context_parts.append(f"Organization: {user_context['company_name']}")
            if "industry" in user_context:
                context_parts.append(f"Industry: {user_context['industry']}")
            if "team_size" in user_context:
                context_parts.append(f"Scale: {user_context['team_size']}")
        
        return "\n".join(context_parts)
    
    def _format_strategic_context(self, state: AgentState) -> str:
        """Format strategic context for evaluation and adaptation."""
        
        context_parts = []
        
        # Add current phase and completeness
        context_parts.append(f"Current Phase: {state['current_phase']}")
        
        completed_sections = [k for k, v in state["strategy_completeness"].items() if v]
        if completed_sections:
            context_parts.append(f"Completed: {', '.join(completed_sections)}")
        
        # Add user context if available
        user_context = state.get("user_context", {})
        if user_context:
            context_parts.append(f"Context: {user_context}")
        
        return "\n".join(context_parts)
    
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
    
    def _update_state_with_insights(self, state: AgentState, stage: str, response: str) -> AgentState:
        """Update agent state with analogical insights and mark completion if appropriate."""
        
        # Track progress in strategy completeness
        if stage == "strategic_integration":
            # Mark analogy analysis as complete after strategic integration
            state = update_strategy_completeness(state, "analogy_analysis", True)
            logger.info("Analogy Agent marked analogy analysis as complete")
        
        # Update identified gaps and insights
        analogy_insights = self._extract_insights_from_response(response, stage)
        if "identified_gaps" not in state:
            state["identified_gaps"] = []
        
        state["identified_gaps"].extend(analogy_insights)
        
        return state
    
    def _extract_insights_from_response(self, response: str, stage: str) -> List[str]:
        """Extract actionable insights from the agent's response."""
        
        insights = []
        
        if stage == "source_identification":
            insights.append("Source domain identification initiated")
        elif stage == "structural_mapping":
            insights.append("Analogical structural mapping in progress")
        elif stage == "evaluation_adaptation":
            insights.append("Analogical insight evaluation and adaptation underway")
        elif stage == "strategic_integration":
            insights.append("Analogical reasoning completed - strategic insights integrated")
        
        return insights
    
    # Fallback responses for error conditions
    def _get_fallback_response(self) -> str:
        """Provide fallback response when LLM fails."""
        return """I'm here to help you develop strategic insights through analogical reasoning using Carroll & Sørensen's framework.

Let's start by exploring what other organizations or industries might offer strategic insights for your situation.

What companies, industries, or even contexts outside business (like sports, nature, or other domains) come to mind when you think about your strategic challenges?"""
    
    def _get_fallback_source_response(self) -> str:
        return """Let's explore potential source domains for strategic insight.

Think about:
- What other industries face similar challenges to yours?
- Which successful companies or models inspire you?
- Are there examples from sports, nature, or other domains that might offer insights?

Share any organizations or contexts that come to mind - even if they seem unrelated at first."""
    
    def _get_fallback_mapping_response(self) -> str:
        return """Now let's map the structural relationships between your chosen examples and your situation.

Consider:
- What are the key success factors in your chosen examples?
- How do the relationships and processes in those examples relate to your context?
- What patterns or mechanisms drive success in both domains?

What similarities do you see in how success is created?"""
    
    def _get_fallback_evaluation_response(self) -> str:
        return """Let's evaluate and adapt these analogical insights for your specific context.

Think about:
- Which aspects of the analogy provide the strongest strategic insights?
- Where does the analogy work well and where might it break down?
- How do we need to adapt these insights for your specific situation?

What strategic insights are emerging from this analogical analysis?"""
    
    def _get_fallback_integration_response(self) -> str:
        return """Let's integrate these analogical insights into a coherent strategic approach.

Consider:
- How do these insights support your core purpose?
- What strategic approaches emerge from this analogical learning?
- What concrete next steps follow from these insights?

How can we turn these analogical insights into actionable strategy?"""


# Integration function for orchestrator
def create_analogy_agent_node():
    """Create an Analogy Agent node function for use in the orchestrator."""
    
    analogy_agent = AnalogyAgent()
    
    def analogy_agent_node(state: AgentState) -> AgentState:
        """Analogy Agent node function for LangGraph orchestrator."""
        
        # Extract the latest user message
        user_input = ""
        if state["conversation_history"]:
            latest_message = state["conversation_history"][-1]
            if isinstance(latest_message, HumanMessage):
                user_input = latest_message.content
        
        # Process through Analogy Agent
        return analogy_agent.process_user_input(state, user_input)
    
    return analogy_agent_node