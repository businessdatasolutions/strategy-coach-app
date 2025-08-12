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


class LogicAgent:
    """
    Logic Agent implementing deductive argument validation and logical structure analysis.
    
    This agent helps validate and strengthen strategic arguments through:
    1. Argument Structure Analysis - Identifying premises, conclusions, and logical flow
    2. Validity Assessment - Evaluating the logical validity of strategic arguments
    3. Soundness Evaluation - Assessing the truth and relevance of premises
    4. Logical Framework Construction - Building coherent logical structures for strategy
    
    Based on principles of formal logic, argumentation theory, and strategic reasoning.
    """
    
    def __init__(self):
        """Initialize the Logic Agent with deductive reasoning prompts."""
        self.llm = get_llm_client()
        self.methodology = "Deductive Argument Validation & Logical Structure Analysis"
        self.focus_areas = ["argument_analysis", "validity_assessment", "soundness_evaluation", "framework_construction"]
        
        # Initialize prompts for different logical analysis stages
        self._init_prompts()
        
        logger.info("Logic Agent initialized with deductive reasoning framework")
    
    def _init_prompts(self):
        """Initialize the prompts for logical analysis and validation."""
        
        # Argument Structure Analysis Prompt
        self.argument_analysis_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "strategic_content", "context_info"],
            template="""You are a strategic consultant specializing in logical argument analysis and validation for strategy development.

METHODOLOGY: Deductive Argument Validation & Logical Structure Analysis
- Argument Structure Analysis: Identify premises, conclusions, and logical connections
- Validity Assessment: Evaluate whether conclusions follow logically from premises
- Soundness Evaluation: Assess truth and relevance of premises
- Framework Construction: Build coherent logical structures for strategic reasoning

CURRENT FOCUS: ARGUMENT STRUCTURE ANALYSIS

Strategic Context:
{strategic_content}

Context Information:
{context_info}

Conversation so far:
{conversation_context}

User's latest input:
{user_input}

As a logical analysis specialist, help analyze the ARGUMENT STRUCTURE of strategic reasoning:

1. **Premise Identification**: Identify the core assumptions, beliefs, and starting points in the strategic reasoning
2. **Conclusion Mapping**: Identify what conclusions are being drawn or proposed
3. **Logical Flow Analysis**: Examine how premises connect to conclusions
4. **Assumption Validation**: Identify unstated assumptions that underlie the reasoning

Key analysis questions:
- "What are the fundamental premises underlying this strategic approach?"
- "What conclusions are being drawn from these premises?"
- "What assumptions are being made that aren't explicitly stated?"
- "How do the different elements of reasoning connect logically?"

Focus on:
- **Explicit premises** that are clearly stated
- **Implicit assumptions** that underlie the reasoning
- **Logical connections** between different elements
- **Conclusion clarity** - what exactly is being proposed or concluded

Provide clear analysis of the logical structure, identifying:
- **Core Premises**: The foundational assumptions and starting points
- **Supporting Evidence**: What supports these premises
- **Logical Connections**: How premises relate to each other and to conclusions
- **Conclusions**: What strategic directions or decisions are being proposed

Remember: Strong strategy requires sound logical foundations. Help clarify and strengthen the logical structure."""
        )
        
        # Validity Assessment Prompt
        self.validity_assessment_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "identified_structure", "strategic_context"],
            template="""You are continuing logical analysis with VALIDITY ASSESSMENT.

IDENTIFIED ARGUMENT STRUCTURE:
{identified_structure}

STRATEGIC CONTEXT:
{strategic_context}

Conversation context:
{conversation_context}

User input:
{user_input}

Now assess the LOGICAL VALIDITY of the strategic arguments:

1. **Logical Validity Check**: Do conclusions follow logically from premises?
2. **Inference Quality**: Are the logical inferences sound and well-reasoned?
3. **Consistency Analysis**: Are the arguments internally consistent?
4. **Completeness Assessment**: Are there missing logical steps or gaps?

Validity assessment criteria:
- **Deductive Validity**: If premises are true, must conclusions be true?
- **Logical Consistency**: Do different parts of the argument contradict each other?
- **Inference Quality**: Are the reasoning steps logically sound?
- **Completeness**: Are there missing premises needed to support conclusions?

Key questions:
- "If we accept these premises, do the conclusions necessarily follow?"
- "Are there any logical fallacies or errors in reasoning?"
- "What logical gaps need to be addressed?"
- "Are the arguments internally consistent?"

Provide:
- **Validity Assessment**: Clear evaluation of logical validity
- **Identified Strengths**: Where the logical reasoning is strong
- **Logical Gaps**: Where reasoning is incomplete or flawed
- **Recommendations**: How to strengthen logical validity

Focus on helping improve the logical rigor of strategic reasoning while maintaining practical applicability."""
        )
        
        # Soundness Evaluation Prompt
        self.soundness_evaluation_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "validity_assessment", "premise_analysis"],
            template="""You are continuing logical analysis with SOUNDNESS EVALUATION.

VALIDITY ASSESSMENT RESULTS:
{validity_assessment}

PREMISE ANALYSIS:
{premise_analysis}

Conversation context:
{conversation_context}

User input:
{user_input}

Now evaluate the SOUNDNESS of the strategic arguments:

1. **Premise Truth Assessment**: Are the premises actually true and well-supported?
2. **Evidence Quality**: What evidence supports the key premises?
3. **Contextual Relevance**: Are premises relevant to the strategic context?
4. **Assumption Validation**: Are underlying assumptions reasonable and defensible?

Soundness evaluation criteria:
- **Truth Value**: Are premises factually accurate and well-supported?
- **Evidence Quality**: Is there sufficient evidence for key claims?
- **Contextual Fit**: Are premises relevant to the specific strategic situation?
- **Assumption Reasonableness**: Are underlying assumptions realistic and defensible?

Key questions:
- "Are the foundational premises actually true and well-supported?"
- "What evidence do we have for key assumptions?"
- "Are these premises relevant to your specific strategic context?"
- "Which assumptions need better validation or evidence?"

Evaluation focus areas:
- **Factual Accuracy**: Are claims about markets, customers, capabilities accurate?
- **Evidence Sufficiency**: Is there enough evidence to support key premises?
- **Strategic Relevance**: Do premises address the real strategic challenges?
- **Risk Assessment**: What happens if key premises are wrong?

Provide:
- **Soundness Assessment**: Evaluation of premise truth and evidence quality
- **Evidence Gaps**: Where more evidence or validation is needed
- **Risk Analysis**: Implications if key premises are incorrect
- **Strengthening Recommendations**: How to improve argument soundness"""
        )
        
        # Logical Framework Construction Prompt
        self.framework_construction_prompt = PromptTemplate(
            input_variables=["conversation_context", "argument_analysis", "validity_results", "soundness_results", "user_input"],
            template="""You are completing logical analysis with FRAMEWORK CONSTRUCTION.

ARGUMENT ANALYSIS:
{argument_analysis}

VALIDITY ASSESSMENT:
{validity_results}

SOUNDNESS EVALUATION:
{soundness_results}

Conversation history:
{conversation_context}

User input:
{user_input}

Now construct a COHERENT LOGICAL FRAMEWORK for strategic reasoning:

1. **Logical Structure Synthesis**: Combine analysis into coherent framework
2. **Validated Reasoning Chain**: Build logically sound argument structure
3. **Strategic Logic Map**: Create clear logical flow for strategic decisions
4. **Implementation Framework**: Translate logical structure into actionable framework

Framework construction elements:
- **Core Logical Foundation**: Well-validated premises and assumptions
- **Reasoning Chain**: Clear logical flow from premises to strategic conclusions
- **Decision Framework**: Logical structure for strategic decision-making
- **Validation Mechanisms**: How to test and verify strategic reasoning

Provide a comprehensive logical framework that includes:

**STRATEGIC LOGIC FRAMEWORK:**
[Clear logical structure connecting premises to strategic conclusions]

**VALIDATED ARGUMENT STRUCTURE:**
- **Core Premises**: Well-supported foundational assumptions
- **Logical Flow**: How premises connect to strategic conclusions
- **Evidence Base**: Supporting evidence for key claims
- **Risk Factors**: What could invalidate the logical structure

**DECISION LOGIC:**
How this logical framework guides strategic decision-making

**IMPLEMENTATION REASONING:**
The logical basis for moving from strategy to implementation

**VALIDATION QUESTIONS:**
Questions to regularly test the logical soundness of strategic reasoning

**NEXT STEPS:**
"This logical framework provides the foundation for strategic implementation. The logical structure validates your strategic approach and provides clear reasoning for strategic decisions."

Ensure the framework is both logically rigorous and practically applicable for strategic development."""
        )
    
    def process_user_input(self, state: AgentState, user_input: str) -> AgentState:
        """
        Process user input through the Logic Agent's deductive reasoning framework.
        
        Args:
            state: Current agent state
            user_input: User's message content
            
        Returns:
            Updated agent state with Logic Agent response
        """
        logger.info(f"Logic Agent processing input for session {state['session_id']}")
        
        try:
            # Determine current logical analysis stage
            logic_stage = self._determine_logic_stage(state)
            logger.debug(f"Logical analysis stage: {logic_stage}")
            
            # Extract conversation context and strategic content
            conversation_context = self._extract_conversation_context(state)
            strategic_content = self._extract_strategic_content(state)
            context_info = self._format_context_info(state)
            
            # Generate response based on stage
            if logic_stage == "argument_analysis":
                response = self._analyze_arguments(conversation_context, user_input, strategic_content, context_info)
                
            elif logic_stage == "validity_assessment":
                identified_structure = self._extract_argument_structure(state)
                strategic_context = self._format_strategic_context(state)
                response = self._assess_validity(conversation_context, user_input, identified_structure, strategic_context)
                
            elif logic_stage == "soundness_evaluation":
                validity_assessment = self._extract_validity_results(state)
                premise_analysis = self._extract_premise_analysis(state)
                response = self._evaluate_soundness(conversation_context, user_input, validity_assessment, premise_analysis)
                
            elif logic_stage == "framework_construction":
                argument_analysis = self._extract_argument_analysis(state)
                validity_results = self._extract_validity_results(state)
                soundness_results = self._extract_soundness_results(state)
                response = self._construct_framework(conversation_context, argument_analysis, validity_results, soundness_results, user_input)
                
            else:
                # Default to argument analysis
                response = self._analyze_arguments(conversation_context, user_input, strategic_content, context_info)
            
            # Update state with Logic Agent insights
            state = self._update_state_with_insights(state, logic_stage, response)
            
            # Add AI response to conversation
            ai_message = AIMessage(content=response)
            state["conversation_history"].append(ai_message)
            
            # Update processing metadata
            state = set_processing_stage(state, "logic_agent_completed", "logic_agent")
            state["agent_output"] = response
            
            logger.info(f"Logic Agent completed processing for stage: {logic_stage}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in Logic Agent processing: {str(e)}")
            
            # Set error state but provide fallback response
            state["error_state"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "agent": "logic_agent"
            }
            
            fallback_response = self._get_fallback_response()
            ai_message = AIMessage(content=fallback_response)
            state["conversation_history"].append(ai_message)
            state["agent_output"] = fallback_response
            
            return state
    
    def _determine_logic_stage(self, state: AgentState) -> str:
        """Determine the current stage of logical analysis based on conversation progress."""
        
        conversation = state["conversation_history"]
        
        # Count different types of logical analysis content
        argument_indicators = 0
        validity_indicators = 0
        soundness_indicators = 0
        framework_indicators = 0
        
        # Analyze conversation for progress indicators
        for message in conversation:
            if hasattr(message, 'content') and message.content:
                content_lower = message.content.lower()
                
                # Argument analysis indicators
                if any(keyword in content_lower for keyword in [
                    "premise", "assumption", "argument", "reasoning", "logic", "conclusion"
                ]):
                    argument_indicators += 1
                
                # Validity assessment indicators
                if any(keyword in content_lower for keyword in [
                    "valid", "validity", "logical", "consistent", "follow", "inference"
                ]):
                    validity_indicators += 1
                
                # Soundness evaluation indicators
                if any(keyword in content_lower for keyword in [
                    "sound", "evidence", "true", "support", "factual", "accurate"
                ]):
                    soundness_indicators += 1
                
                # Framework construction indicators
                if any(keyword in content_lower for keyword in [
                    "framework", "structure", "synthesis", "integration", "decision logic"
                ]):
                    framework_indicators += 1
        
        # Determine stage based on conversation progress
        conversation_turns = len(conversation) // 2  # User-AI pairs
        
        if conversation_turns >= 6 and argument_indicators >= 2 and validity_indicators >= 1:
            if soundness_indicators >= 1:
                if framework_indicators >= 1:
                    return "framework_construction"
                else:
                    return "soundness_evaluation"
            else:
                return "soundness_evaluation"
        elif conversation_turns >= 3 and argument_indicators >= 1:
            return "validity_assessment"
        else:
            return "argument_analysis"
    
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
    
    def _extract_strategic_content(self, state: AgentState) -> str:
        """Extract strategic content from previous agent work."""
        
        # Look for strategic content from WHY and Analogy agents
        strategic_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "purpose", "why", "strategy", "analogy", "strategic", "framework", "approach"
                ]):
                    strategic_content.append(message.content)
        
        if strategic_content:
            # Get most relevant strategic discussions
            return "\n\n".join(strategic_content[-3:])  # Last 3 strategic discussions
        
        # Check completed strategy sections
        completed_sections = []
        if state["strategy_completeness"].get("why", False):
            completed_sections.append("Core purpose and WHY established")
        if state["strategy_completeness"].get("analogy_analysis", False):
            completed_sections.append("Analogical reasoning and insights developed")
        
        if completed_sections:
            return "Strategic development progress: " + ", ".join(completed_sections)
        
        return "Strategic content being developed through conversation"
    
    def _format_context_info(self, state: AgentState) -> str:
        """Format context information for logical analysis."""
        
        context_parts = []
        
        # Add current phase and progress
        context_parts.append(f"Current Phase: {state['current_phase']}")
        
        # Add completeness information
        completed = [k for k, v in state["strategy_completeness"].items() if v]
        if completed:
            context_parts.append(f"Completed Elements: {', '.join(completed)}")
        
        # Add user context if available
        user_context = state.get("user_context", {})
        if user_context:
            context_info = []
            for key, value in user_context.items():
                if key in ["company_name", "industry", "team_size", "revenue_stage"]:
                    context_info.append(f"{key.title()}: {value}")
            if context_info:
                context_parts.append("Organization: " + ", ".join(context_info))
        
        return "\n".join(context_parts) if context_parts else "Context information being gathered"
    
    def _analyze_arguments(self, conversation_context: str, user_input: str,
                          strategic_content: str, context_info: str) -> str:
        """Generate response for argument structure analysis stage."""
        
        prompt = self.argument_analysis_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            strategic_content=strategic_content,
            context_info=context_info
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in argument analysis: {str(e)}")
            return self._get_fallback_argument_response()
    
    def _assess_validity(self, conversation_context: str, user_input: str,
                        identified_structure: str, strategic_context: str) -> str:
        """Generate response for validity assessment stage."""
        
        prompt = self.validity_assessment_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            identified_structure=identified_structure,
            strategic_context=strategic_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in validity assessment: {str(e)}")
            return self._get_fallback_validity_response()
    
    def _evaluate_soundness(self, conversation_context: str, user_input: str,
                           validity_assessment: str, premise_analysis: str) -> str:
        """Generate response for soundness evaluation stage."""
        
        prompt = self.soundness_evaluation_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            validity_assessment=validity_assessment,
            premise_analysis=premise_analysis
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in soundness evaluation: {str(e)}")
            return self._get_fallback_soundness_response()
    
    def _construct_framework(self, conversation_context: str, argument_analysis: str,
                            validity_results: str, soundness_results: str, user_input: str) -> str:
        """Generate response for logical framework construction stage."""
        
        prompt = self.framework_construction_prompt.format(
            conversation_context=conversation_context,
            argument_analysis=argument_analysis,
            validity_results=validity_results,
            soundness_results=soundness_results,
            user_input=user_input
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in framework construction: {str(e)}")
            return self._get_fallback_framework_response()
    
    def _extract_argument_structure(self, state: AgentState) -> str:
        """Extract identified argument structure from conversation history."""
        
        structure_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "premise", "assumption", "argument", "conclusion", "structure"
                ]):
                    structure_content.append(message.content)
        
        return structure_content[-1] if structure_content else "Argument structure analysis in progress"
    
    def _extract_validity_results(self, state: AgentState) -> str:
        """Extract validity assessment results from conversation history."""
        
        validity_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "valid", "validity", "logical", "consistent", "inference"
                ]):
                    validity_content.append(message.content)
        
        return validity_content[-1] if validity_content else "Validity assessment in progress"
    
    def _extract_premise_analysis(self, state: AgentState) -> str:
        """Extract premise analysis from conversation history."""
        
        premise_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "premise", "assumption", "foundation", "basis"
                ]):
                    premise_content.append(message.content)
        
        return premise_content[-1] if premise_content else "Premise analysis in progress"
    
    def _extract_soundness_results(self, state: AgentState) -> str:
        """Extract soundness evaluation results from conversation history."""
        
        soundness_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "sound", "evidence", "support", "factual", "accurate"
                ]):
                    soundness_content.append(message.content)
        
        return soundness_content[-1] if soundness_content else "Soundness evaluation in progress"
    
    def _extract_argument_analysis(self, state: AgentState) -> str:
        """Extract argument analysis from conversation history."""
        
        analysis_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "argument", "reasoning", "logic", "analysis", "structure"
                ]):
                    analysis_content.append(message.content)
        
        return analysis_content[-1] if analysis_content else "Argument analysis in progress"
    
    def _format_strategic_context(self, state: AgentState) -> str:
        """Format strategic context for validity assessment."""
        
        context_parts = []
        
        # Add current phase
        context_parts.append(f"Strategic Phase: {state['current_phase']}")
        
        # Add completed strategy elements
        completed_sections = [k for k, v in state["strategy_completeness"].items() if v]
        if completed_sections:
            context_parts.append(f"Completed Strategy Elements: {', '.join(completed_sections)}")
        
        # Add organizational context
        user_context = state.get("user_context", {})
        if user_context and "industry" in user_context:
            context_parts.append(f"Industry Context: {user_context['industry']}")
        
        return "\n".join(context_parts)
    
    def _update_state_with_insights(self, state: AgentState, stage: str, response: str) -> AgentState:
        """Update agent state with logical insights and mark completion if appropriate."""
        
        # Track progress in strategy completeness
        if stage == "framework_construction":
            # Mark logical structure as complete after framework construction
            state = update_strategy_completeness(state, "logical_structure", True)
            logger.info("Logic Agent marked logical structure as complete")
        
        # Update identified gaps and insights
        logic_insights = self._extract_insights_from_response(response, stage)
        if "identified_gaps" not in state:
            state["identified_gaps"] = []
        
        state["identified_gaps"].extend(logic_insights)
        
        return state
    
    def _extract_insights_from_response(self, response: str, stage: str) -> List[str]:
        """Extract actionable insights from the agent's response."""
        
        insights = []
        
        if stage == "argument_analysis":
            insights.append("Strategic argument structure analysis initiated")
        elif stage == "validity_assessment":
            insights.append("Logical validity assessment in progress")
        elif stage == "soundness_evaluation":
            insights.append("Argument soundness evaluation underway")
        elif stage == "framework_construction":
            insights.append("Logical framework completed - strategic reasoning validated")
        
        return insights
    
    # Fallback responses for error conditions
    def _get_fallback_response(self) -> str:
        """Provide fallback response when LLM fails."""
        return """I'm here to help validate and strengthen the logical structure of your strategic reasoning.

Let's analyze the logical foundations of your strategic thinking by examining the key assumptions, reasoning patterns, and conclusions in your strategic approach.

What strategic reasoning or decisions would you like me to help analyze for logical consistency and strength?"""
    
    def _get_fallback_argument_response(self) -> str:
        return """Let's analyze the logical structure of your strategic arguments.

Consider these elements:
- What are the core assumptions underlying your strategic approach?
- What conclusions are you drawing from these assumptions?
- How do your premises connect to your strategic decisions?

Share your strategic reasoning so we can examine its logical foundations."""
    
    def _get_fallback_validity_response(self) -> str:
        return """Now let's assess whether your strategic conclusions follow logically from your premises.

Think about:
- Do your strategic decisions logically follow from your assumptions?
- Are there any gaps in your reasoning that need to be addressed?
- Are your arguments internally consistent?

What aspects of your strategic logic would you like to examine?"""
    
    def _get_fallback_soundness_response(self) -> str:
        return """Let's evaluate whether your strategic premises are well-supported and accurate.

Consider:
- Are your key assumptions based on solid evidence?
- What data or experience supports your strategic premises?
- Are there any assumptions that need better validation?

What evidence supports your key strategic assumptions?"""
    
    def _get_fallback_framework_response(self) -> str:
        return """Let's construct a coherent logical framework for your strategic reasoning.

This framework should include:
- Well-validated premises and assumptions
- Clear logical connections between premises and conclusions
- A sound basis for strategic decision-making

How can we integrate your logical analysis into a practical strategic framework?"""


# Integration function for orchestrator
def create_logic_agent_node():
    """Create a Logic Agent node function for use in the orchestrator."""
    
    logic_agent = LogicAgent()
    
    def logic_agent_node(state: AgentState) -> AgentState:
        """Logic Agent node function for LangGraph orchestrator."""
        
        # Extract the latest user message
        user_input = ""
        if state["conversation_history"]:
            latest_message = state["conversation_history"][-1]
            if isinstance(latest_message, HumanMessage):
                user_input = latest_message.content
        
        # Process through Logic Agent
        return logic_agent.process_user_input(state, user_input)
    
    return logic_agent_node