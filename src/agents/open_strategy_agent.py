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


class OpenStrategyAgent:
    """
    Open Strategy Agent implementing implementation planning and stakeholder engagement.
    
    This agent helps translate strategic insights into actionable implementation plans by:
    1. Stakeholder Analysis - Identifying key stakeholders and their engagement needs
    2. Process Design - Creating implementation processes and workflows  
    3. Resource Planning - Determining required resources and capabilities
    4. Implementation Roadmap - Building practical execution timelines and milestones
    
    Based on open strategy principles emphasizing transparency, engagement, and collaborative implementation.
    """
    
    def __init__(self):
        """Initialize the Open Strategy Agent with implementation planning prompts."""
        self.llm = get_llm_client()
        self.methodology = "Open Strategy Implementation Planning"
        self.focus_areas = ["stakeholder_analysis", "process_design", "resource_planning", "implementation_roadmap"]
        
        # Initialize prompts for different implementation planning stages
        self._init_prompts()
        
        logger.info("Open Strategy Agent initialized with implementation planning framework")
    
    def _init_prompts(self):
        """Initialize the prompts for implementation planning stages."""
        
        # Stakeholder Analysis Prompt
        self.stakeholder_analysis_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "strategic_foundation", "context_info"],
            template="""You are a strategic implementation consultant specializing in open strategy and stakeholder engagement for strategy execution.

METHODOLOGY: Open Strategy Implementation Planning
- Stakeholder Analysis: Identify key stakeholders and their engagement needs
- Process Design: Create implementation processes and workflows
- Resource Planning: Determine required resources and capabilities
- Implementation Roadmap: Build practical execution timelines and milestones

CURRENT FOCUS: STAKEHOLDER ANALYSIS

Strategic Foundation:
{strategic_foundation}

Context Information:
{context_info}

Conversation so far:
{conversation_context}

User's latest input:
{user_input}

As a stakeholder engagement specialist, help identify and analyze KEY STAKEHOLDERS for strategy implementation:

1. **Stakeholder Identification**: Identify all key stakeholders who will be involved in or affected by strategy implementation
2. **Influence Analysis**: Assess stakeholder influence on strategy success and their level of interest
3. **Engagement Needs**: Determine what each stakeholder group needs from the strategy and implementation process
4. **Communication Requirements**: Identify how different stakeholders prefer to receive and contribute information

Key stakeholder categories to consider:
- **Internal Stakeholders**: Employees, management, board members, departments
- **External Stakeholders**: Customers, partners, suppliers, investors, regulators
- **Implementation Champions**: Those who will drive strategy execution
- **Potential Resistors**: Those who might resist or be challenged by changes

Stakeholder analysis questions:
- "Who are the key people and groups that must be engaged for successful strategy implementation?"
- "What level of influence does each stakeholder have on strategy success?"
- "What are their interests, concerns, and motivations regarding this strategy?"
- "How do they prefer to be communicated with and engaged in the process?"

For each stakeholder group, consider:
- **Role in Implementation**: How they contribute to or affect strategy execution
- **Influence Level**: High/Medium/Low influence on implementation success
- **Interest Level**: High/Medium/Low interest in the strategy outcomes
- **Engagement Approach**: How to effectively involve them in implementation
- **Communication Style**: Their preferred communication methods and frequency

Focus on creating an open, transparent approach that engages stakeholders as partners in strategy execution rather than passive recipients."""
        )
        
        # Process Design Prompt
        self.process_design_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "stakeholder_analysis", "strategic_context"],
            template="""You are continuing implementation planning with PROCESS DESIGN.

STAKEHOLDER ANALYSIS RESULTS:
{stakeholder_analysis}

STRATEGIC CONTEXT:
{strategic_context}

Conversation context:
{conversation_context}

User input:
{user_input}

Now design IMPLEMENTATION PROCESSES and workflows:

1. **Process Architecture**: Design the overall implementation process structure
2. **Workflow Design**: Create specific workflows for key implementation activities
3. **Decision-Making Processes**: Establish how strategic decisions will be made during implementation
4. **Communication Flows**: Design information flow between stakeholders
5. **Feedback Mechanisms**: Create systems for collecting and responding to implementation feedback

Process design elements:
- **Governance Structure**: How implementation decisions are made and by whom
- **Implementation Workflows**: Step-by-step processes for executing strategy elements
- **Communication Protocols**: How information flows between stakeholders
- **Review Cycles**: Regular checkpoints for assessing implementation progress
- **Adaptation Mechanisms**: How processes adjust when circumstances change

Key questions:
- "What processes are needed to translate strategy into action?"
- "How will different stakeholder groups collaborate during implementation?"
- "What decision-making authorities and approval processes are needed?"
- "How will you collect feedback and make adjustments during implementation?"

Design considerations:
- **Transparency**: Make processes visible and understandable to all stakeholders
- **Flexibility**: Build in ability to adapt processes as implementation progresses
- **Efficiency**: Streamline processes to avoid bureaucratic delays
- **Accountability**: Clear ownership and responsibility for each process step
- **Scalability**: Processes that can grow with implementation scope

Provide:
- **Process Maps**: Visual or descriptive workflows for key implementation activities
- **Governance Framework**: Decision-making structure and authorities
- **Communication Architecture**: How information flows through the organization
- **Quality Assurance**: Processes to ensure implementation quality and consistency"""
        )
        
        # Resource Planning Prompt
        self.resource_planning_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_input", "process_design", "implementation_scope"],
            template="""You are continuing implementation planning with RESOURCE PLANNING.

PROCESS DESIGN RESULTS:
{process_design}

IMPLEMENTATION SCOPE:
{implementation_scope}

Conversation context:
{conversation_context}

User input:
{user_input}

Now plan RESOURCES AND CAPABILITIES needed for implementation:

1. **Resource Assessment**: Identify all resources needed for successful implementation
2. **Capability Analysis**: Assess current capabilities and identify gaps
3. **Resource Allocation**: Determine how to allocate resources across implementation activities
4. **Capability Development**: Plan how to build missing capabilities
5. **Resource Optimization**: Maximize implementation effectiveness with available resources

Resource categories:
- **Human Resources**: People, skills, roles, and responsibilities needed
- **Financial Resources**: Budget allocation for implementation activities
- **Technology Resources**: Systems, tools, and technology infrastructure needed
- **Knowledge Resources**: Information, expertise, and intellectual assets required
- **Time Resources**: Implementation timeline and scheduling considerations

Planning considerations:
- **Current State Assessment**: What resources and capabilities already exist?
- **Gap Analysis**: What's missing that must be acquired or developed?
- **Resource Constraints**: What limitations exist and how to work within them?
- **Priority Allocation**: Which activities get priority access to limited resources?
- **Risk Mitigation**: What backup plans exist if key resources become unavailable?

Key questions:
- "What people, skills, and roles are needed to execute this strategy?"
- "What financial investment is required for successful implementation?"
- "What technology or infrastructure changes are needed?"
- "How will you develop capabilities that don't currently exist?"
- "What are the critical resource bottlenecks that could delay implementation?"

Provide:
- **Resource Requirements**: Detailed breakdown of needed resources
- **Capability Gap Analysis**: What capabilities need development
- **Resource Allocation Plan**: How resources will be distributed across activities
- **Development Strategy**: How to build missing capabilities
- **Risk Assessment**: Resource-related risks and mitigation strategies"""
        )
        
        # Implementation Roadmap Prompt
        self.implementation_roadmap_prompt = PromptTemplate(
            input_variables=["conversation_context", "stakeholder_plan", "process_framework", "resource_plan", "user_input"],
            template="""You are completing implementation planning with IMPLEMENTATION ROADMAP creation.

STAKEHOLDER ENGAGEMENT PLAN:
{stakeholder_plan}

PROCESS FRAMEWORK:
{process_framework}

RESOURCE PLAN:
{resource_plan}

Conversation history:
{conversation_context}

User input:
{user_input}

Now create a comprehensive IMPLEMENTATION ROADMAP:

1. **Timeline Development**: Create realistic timeline with phases, milestones, and dependencies
2. **Priority Sequencing**: Determine optimal order for implementation activities
3. **Milestone Definition**: Establish clear success markers and checkpoints
4. **Risk Planning**: Identify implementation risks and mitigation strategies
5. **Success Metrics**: Define how implementation success will be measured

Roadmap components:
- **Implementation Phases**: Logical groupings of activities with clear objectives
- **Key Milestones**: Critical success points and decision gates
- **Activity Dependencies**: What must be completed before other activities can begin
- **Resource Scheduling**: When different resources will be needed
- **Review Points**: Regular assessment and adjustment opportunities

Provide a comprehensive implementation roadmap that includes:

**IMPLEMENTATION ROADMAP:**
[Clear timeline with phases, activities, and milestones]

**PHASE BREAKDOWN:**
- **Phase 1**: [Initial implementation focus and quick wins]
- **Phase 2**: [Core implementation activities and process establishment]  
- **Phase 3**: [Full deployment and optimization]
- **Phase 4**: [Evaluation and continuous improvement]

**KEY MILESTONES:**
[Critical success markers and decision points throughout implementation]

**SUCCESS METRICS:**
How implementation progress and success will be measured

**RISK MANAGEMENT:**
Key implementation risks and mitigation strategies

**STAKEHOLDER ENGAGEMENT TIMELINE:**
When and how stakeholders will be engaged throughout implementation

**RESOURCE DEPLOYMENT SCHEDULE:**
When different resources will be needed and deployed

**ADAPTATION MECHANISMS:**
How the roadmap will be adjusted as implementation progresses

**NEXT STEPS:**
"This implementation roadmap provides a practical path from strategic insight to strategic action. The roadmap balances ambitious goals with realistic execution timelines."

Ensure the roadmap is both comprehensive and practical, providing clear guidance for moving from strategy to successful implementation."""
        )
    
    def process_user_input(self, state: AgentState, user_input: str) -> AgentState:
        """
        Process user input through the Open Strategy Agent's implementation planning framework.
        
        Args:
            state: Current agent state
            user_input: User's message content
            
        Returns:
            Updated agent state with Open Strategy Agent response
        """
        logger.info(f"Open Strategy Agent processing input for session {state['session_id']}")
        
        try:
            # Determine current implementation planning stage
            implementation_stage = self._determine_implementation_stage(state)
            logger.debug(f"Implementation planning stage: {implementation_stage}")
            
            # Extract conversation context and strategic foundation
            conversation_context = self._extract_conversation_context(state)
            strategic_foundation = self._extract_strategic_foundation(state)
            context_info = self._format_context_info(state)
            
            # Generate response based on stage
            if implementation_stage == "stakeholder_analysis":
                response = self._analyze_stakeholders(conversation_context, user_input, strategic_foundation, context_info)
                
            elif implementation_stage == "process_design":
                stakeholder_analysis = self._extract_stakeholder_analysis(state)
                strategic_context = self._format_strategic_context(state)
                response = self._design_processes(conversation_context, user_input, stakeholder_analysis, strategic_context)
                
            elif implementation_stage == "resource_planning":
                process_design = self._extract_process_design(state)
                implementation_scope = self._format_implementation_scope(state)
                response = self._plan_resources(conversation_context, user_input, process_design, implementation_scope)
                
            elif implementation_stage == "implementation_roadmap":
                stakeholder_plan = self._extract_stakeholder_plan(state)
                process_framework = self._extract_process_framework(state)
                resource_plan = self._extract_resource_plan(state)
                response = self._create_roadmap(conversation_context, stakeholder_plan, process_framework, resource_plan, user_input)
                
            else:
                # Default to stakeholder analysis
                response = self._analyze_stakeholders(conversation_context, user_input, strategic_foundation, context_info)
            
            # Update state with Open Strategy Agent insights
            state = self._update_state_with_insights(state, implementation_stage, response)
            
            # Add AI response to conversation
            ai_message = AIMessage(content=response)
            state["conversation_history"].append(ai_message)
            
            # Update processing metadata
            state = set_processing_stage(state, "open_strategy_agent_completed", "open_strategy_agent")
            state["agent_output"] = response
            
            logger.info(f"Open Strategy Agent completed processing for stage: {implementation_stage}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in Open Strategy Agent processing: {str(e)}")
            
            # Set error state but provide fallback response
            state["error_state"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "agent": "open_strategy_agent"
            }
            
            fallback_response = self._get_fallback_response()
            ai_message = AIMessage(content=fallback_response)
            state["conversation_history"].append(ai_message)
            state["agent_output"] = fallback_response
            
            return state
    
    def _determine_implementation_stage(self, state: AgentState) -> str:
        """Determine the current stage of implementation planning based on conversation progress."""
        
        conversation = state["conversation_history"]
        
        # Count different types of implementation planning content
        stakeholder_indicators = 0
        process_indicators = 0
        resource_indicators = 0
        roadmap_indicators = 0
        
        # Analyze conversation for progress indicators
        for message in conversation:
            if hasattr(message, 'content') and message.content:
                content_lower = message.content.lower()
                
                # Stakeholder analysis indicators
                if any(keyword in content_lower for keyword in [
                    "stakeholder", "people", "team", "customer", "partner", "engagement", "communication"
                ]):
                    stakeholder_indicators += 1
                
                # Process design indicators
                if any(keyword in content_lower for keyword in [
                    "process", "workflow", "procedure", "governance", "decision", "structure"
                ]):
                    process_indicators += 1
                
                # Resource planning indicators
                if any(keyword in content_lower for keyword in [
                    "resource", "budget", "capability", "skill", "technology", "infrastructure"
                ]):
                    resource_indicators += 1
                
                # Roadmap indicators
                if any(keyword in content_lower for keyword in [
                    "roadmap", "timeline", "milestone", "phase", "implementation", "schedule"
                ]):
                    roadmap_indicators += 1
        
        # Determine stage based on conversation progress
        conversation_turns = len(conversation) // 2  # User-AI pairs
        
        if conversation_turns >= 6 and stakeholder_indicators >= 2 and process_indicators >= 1:
            if resource_indicators >= 1:
                if roadmap_indicators >= 1:
                    return "implementation_roadmap"
                else:
                    return "resource_planning"
            else:
                return "resource_planning"
        elif conversation_turns >= 3 and stakeholder_indicators >= 1:
            return "process_design"
        else:
            return "stakeholder_analysis"
    
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
    
    def _extract_strategic_foundation(self, state: AgentState) -> str:
        """Extract strategic foundation from previous agent work."""
        
        # Look for strategic content from WHY, Analogy, and Logic agents
        strategic_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "purpose", "why", "strategy", "analogy", "logical", "framework", "reasoning"
                ]):
                    strategic_content.append(message.content)
        
        if strategic_content:
            # Get most relevant strategic discussions
            return "\n\n".join(strategic_content[-3:])  # Last 3 strategic discussions
        
        # Check completed strategy sections
        completed_sections = []
        if state["strategy_completeness"].get("why", False):
            completed_sections.append("Core purpose and WHY clarified")
        if state["strategy_completeness"].get("analogy_analysis", False):
            completed_sections.append("Strategic insights from analogical reasoning")
        if state["strategy_completeness"].get("logical_structure", False):
            completed_sections.append("Logical framework and argument validation")
        
        if completed_sections:
            return "Strategic foundation established: " + ", ".join(completed_sections)
        
        return "Strategic foundation being developed through previous conversations"
    
    def _format_context_info(self, state: AgentState) -> str:
        """Format context information for implementation planning."""
        
        context_parts = []
        
        # Add current phase and progress
        context_parts.append(f"Current Phase: {state['current_phase']}")
        
        # Add completeness information
        completed = [k for k, v in state["strategy_completeness"].items() if v]
        if completed:
            context_parts.append(f"Completed Strategy Elements: {', '.join(completed)}")
        
        # Add user context if available
        user_context = state.get("user_context", {})
        if user_context:
            context_info = []
            for key, value in user_context.items():
                if key in ["company_name", "industry", "team_size", "revenue_stage"]:
                    context_info.append(f"{key.title().replace('_', ' ')}: {value}")
            if context_info:
                context_parts.append("Organization: " + ", ".join(context_info))
        
        return "\n".join(context_parts) if context_parts else "Context information being gathered"
    
    def _analyze_stakeholders(self, conversation_context: str, user_input: str,
                             strategic_foundation: str, context_info: str) -> str:
        """Generate response for stakeholder analysis stage."""
        
        prompt = self.stakeholder_analysis_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            strategic_foundation=strategic_foundation,
            context_info=context_info
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in stakeholder analysis: {str(e)}")
            return self._get_fallback_stakeholder_response()
    
    def _design_processes(self, conversation_context: str, user_input: str,
                         stakeholder_analysis: str, strategic_context: str) -> str:
        """Generate response for process design stage."""
        
        prompt = self.process_design_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            stakeholder_analysis=stakeholder_analysis,
            strategic_context=strategic_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in process design: {str(e)}")
            return self._get_fallback_process_response()
    
    def _plan_resources(self, conversation_context: str, user_input: str,
                       process_design: str, implementation_scope: str) -> str:
        """Generate response for resource planning stage."""
        
        prompt = self.resource_planning_prompt.format(
            conversation_context=conversation_context,
            user_input=user_input,
            process_design=process_design,
            implementation_scope=implementation_scope
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in resource planning: {str(e)}")
            return self._get_fallback_resource_response()
    
    def _create_roadmap(self, conversation_context: str, stakeholder_plan: str,
                       process_framework: str, resource_plan: str, user_input: str) -> str:
        """Generate response for implementation roadmap creation."""
        
        prompt = self.implementation_roadmap_prompt.format(
            conversation_context=conversation_context,
            stakeholder_plan=stakeholder_plan,
            process_framework=process_framework,
            resource_plan=resource_plan,
            user_input=user_input
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM error in roadmap creation: {str(e)}")
            return self._get_fallback_roadmap_response()
    
    def _extract_stakeholder_analysis(self, state: AgentState) -> str:
        """Extract stakeholder analysis from conversation history."""
        
        stakeholder_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "stakeholder", "engagement", "communication", "influence", "interest"
                ]):
                    stakeholder_content.append(message.content)
        
        return stakeholder_content[-1] if stakeholder_content else "Stakeholder analysis in progress"
    
    def _extract_stakeholder_plan(self, state: AgentState) -> str:
        """Extract stakeholder engagement plan from conversation history."""
        return self._extract_stakeholder_analysis(state)  # Same content for roadmap context
    
    def _extract_process_design(self, state: AgentState) -> str:
        """Extract process design from conversation history."""
        
        process_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "process", "workflow", "governance", "decision", "structure", "framework"
                ]):
                    process_content.append(message.content)
        
        return process_content[-1] if process_content else "Process design in progress"
    
    def _extract_process_framework(self, state: AgentState) -> str:
        """Extract process framework from conversation history."""
        return self._extract_process_design(state)  # Same content for roadmap context
    
    def _extract_resource_plan(self, state: AgentState) -> str:
        """Extract resource planning from conversation history."""
        
        resource_content = []
        
        for message in state["conversation_history"]:
            if isinstance(message, AIMessage) and hasattr(message, 'content'):
                content = message.content.lower()
                if any(keyword in content for keyword in [
                    "resource", "capability", "budget", "skill", "technology", "capacity"
                ]):
                    resource_content.append(message.content)
        
        return resource_content[-1] if resource_content else "Resource planning in progress"
    
    def _format_strategic_context(self, state: AgentState) -> str:
        """Format strategic context for process design."""
        
        context_parts = []
        
        # Add current phase
        context_parts.append(f"Strategic Phase: {state['current_phase']}")
        
        # Add completed strategy elements
        completed_sections = [k for k, v in state["strategy_completeness"].items() if v]
        if completed_sections:
            context_parts.append(f"Completed Elements: {', '.join(completed_sections)}")
        
        # Add organizational context
        user_context = state.get("user_context", {})
        if user_context:
            org_info = []
            for key, value in user_context.items():
                if key in ["company_name", "industry", "team_size", "revenue_stage"]:
                    org_info.append(f"{key.replace('_', ' ').title()}: {value}")
            if org_info:
                context_parts.append("Organization: " + ", ".join(org_info))
        
        return "\n".join(context_parts)
    
    def _format_implementation_scope(self, state: AgentState) -> str:
        """Format implementation scope for resource planning."""
        
        scope_parts = []
        
        # Add strategic foundation scope
        completed = [k for k, v in state["strategy_completeness"].items() if v]
        if completed:
            scope_parts.append(f"Strategic scope includes: {', '.join(completed)}")
        
        # Add organizational scope
        user_context = state.get("user_context", {})
        if user_context:
            if "team_size" in user_context:
                scope_parts.append(f"Team scale: {user_context['team_size']}")
            if "revenue_stage" in user_context:
                scope_parts.append(f"Business stage: {user_context['revenue_stage']}")
            if "industry" in user_context:
                scope_parts.append(f"Industry context: {user_context['industry']}")
        
        # Add phase context
        scope_parts.append(f"Implementation focus: {state['current_phase']} phase execution")
        
        return "\n".join(scope_parts) if scope_parts else "Implementation scope being defined"
    
    def _update_state_with_insights(self, state: AgentState, stage: str, response: str) -> AgentState:
        """Update agent state with implementation insights and mark completion if appropriate."""
        
        # Track progress in strategy completeness
        if stage == "implementation_roadmap":
            # Mark implementation plan as complete after roadmap creation
            state = update_strategy_completeness(state, "implementation_plan", True)
            logger.info("Open Strategy Agent marked implementation plan as complete")
        
        # Update identified gaps and insights
        implementation_insights = self._extract_insights_from_response(response, stage)
        if "identified_gaps" not in state:
            state["identified_gaps"] = []
        
        state["identified_gaps"].extend(implementation_insights)
        
        return state
    
    def _extract_insights_from_response(self, response: str, stage: str) -> List[str]:
        """Extract actionable insights from the agent's response."""
        
        insights = []
        
        if stage == "stakeholder_analysis":
            insights.append("Stakeholder analysis and engagement planning initiated")
        elif stage == "process_design":
            insights.append("Implementation process design and governance structure developed")
        elif stage == "resource_planning":
            insights.append("Resource requirements and capability planning completed")
        elif stage == "implementation_roadmap":
            insights.append("Implementation roadmap completed - strategy ready for execution")
        
        return insights
    
    # Fallback responses for error conditions
    def _get_fallback_response(self) -> str:
        """Provide fallback response when LLM fails."""
        return """I'm here to help you translate your strategic insights into practical implementation plans.

Let's start by identifying the key stakeholders who need to be engaged in implementing your strategy, and then design the processes and resources needed for successful execution.

Who are the key people and groups that will be involved in implementing your strategy?"""
    
    def _get_fallback_stakeholder_response(self) -> str:
        return """Let's identify and analyze your key stakeholders for strategy implementation.

Consider these stakeholder groups:
- Internal stakeholders (employees, management, departments)
- External stakeholders (customers, partners, suppliers, investors)
- Implementation champions (those who will drive execution)
- Potential resistors (those who might be challenged by changes)

Who are the key people and groups that must be engaged for your strategy to succeed?"""
    
    def _get_fallback_process_response(self) -> str:
        return """Now let's design the processes needed for effective implementation.

Think about:
- How will decisions be made during implementation?
- What workflows are needed to execute key strategy elements?
- How will different stakeholder groups collaborate?
- What communication and feedback mechanisms are needed?

What processes do you think will be most critical for successful implementation?"""
    
    def _get_fallback_resource_response(self) -> str:
        return """Let's plan the resources and capabilities needed for implementation.

Consider:
- What people and skills are needed?
- What financial resources will be required?
- What technology or infrastructure changes are needed?
- What capabilities need to be developed or acquired?

What do you see as the most critical resource requirements for your strategy implementation?"""
    
    def _get_fallback_roadmap_response(self) -> str:
        return """Let's create an implementation roadmap that brings everything together.

This should include:
- Timeline with phases and key milestones
- Priority sequencing of implementation activities
- Resource deployment schedule
- Risk mitigation strategies
- Success metrics and review points

How would you like to sequence and timeline your strategy implementation?"""


# Integration function for orchestrator
def create_open_strategy_agent_node():
    """Create an Open Strategy Agent node function for use in the orchestrator."""
    
    open_strategy_agent = OpenStrategyAgent()
    
    def open_strategy_agent_node(state: AgentState) -> AgentState:
        """Open Strategy Agent node function for LangGraph orchestrator."""
        
        # Extract the latest user message
        user_input = ""
        if state["conversation_history"]:
            latest_message = state["conversation_history"][-1]
            if isinstance(latest_message, HumanMessage):
                user_input = latest_message.content
        
        # Process through Open Strategy Agent
        return open_strategy_agent.process_user_input(state, user_input)
    
    return open_strategy_agent_node