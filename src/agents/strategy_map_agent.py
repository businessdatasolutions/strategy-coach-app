"""
Strategy Map Agent for the AI Strategic Co-pilot.

This agent manages the persistent JSON strategy map that captures the evolving
strategic insights across all conversation phases. Based on Kaplan & Norton's
Balanced Scorecard Strategy Maps with Six Value Components from Integrated Reporting.

The Strategy Map includes:
- Four Strategic Perspectives (Stakeholder/Customer, Internal Processes, Learning & Growth, Value Creation)
- Six Value Components (Financial, Manufactured, Intellectual, Human, Social & Relationship, Natural)
- Integration with insights from all specialist agents (WHY, Analogy, Logic, Open Strategy)
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.models.state import AgentState, StrategyMapState
from src.utils.llm_client import get_llm_client, LLMClientError


logger = logging.getLogger(__name__)


class StrategyMapAgent:
    """
    Agent responsible for maintaining the persistent JSON strategy map.
    
    This agent reads, analyzes, and updates the strategy map file throughout
    the conversation, integrating insights from all specialist agents into
    a cohesive strategic framework.
    """
    
    def __init__(self):
        """Initialize the Strategy Map Agent."""
        self.llm_client = get_llm_client()
        self.value_components = [
            "financial_capital",
            "manufactured_capital", 
            "intellectual_capital",
            "human_capital",
            "social_relationship_capital",
            "natural_capital"
        ]
        self.perspectives = [
            "stakeholder_customer",
            "internal_processes", 
            "learning_growth",
            "value_creation"
        ]
        logger.info("Strategy Map Agent initialized with Kaplan & Norton framework")
    
    def create_empty_strategy_map(self, session_id: str) -> StrategyMapState:
        """
        Create an empty strategy map with the full Six Value Components structure.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Empty StrategyMapState with complete structure
        """
        now = datetime.now().isoformat()
        
        return StrategyMapState(
            # Metadata
            session_id=session_id,
            created_at=now,
            updated_at=now,
            version=1,
            
            # Core strategy components
            why={
                "purpose": "",
                "beliefs": [],
                "values": [],
                "golden_circle_complete": False
            },
            
            stakeholder_customer={
                "value_propositions": [],
                "customer_segments": [],
                "stakeholder_outcomes": [],
                "financial_capital": {
                    "revenue_model": "",
                    "cost_structure": "",
                    "investment_requirements": "",
                    "financial_returns": []
                },
                "social_relationship_capital": {
                    "stakeholder_relationships": [],
                    "brand_reputation": "",
                    "community_impact": "",
                    "partnership_value": []
                }
            },
            
            internal_processes={
                "core_processes": [],
                "operational_excellence": [],
                "innovation_processes": [],
                "regulatory_compliance": [],
                "manufactured_capital": {
                    "physical_assets": [],
                    "infrastructure": "",
                    "production_capacity": "",
                    "technology_platforms": []
                },
                "natural_capital": {
                    "environmental_impact": "",
                    "resource_utilization": [],
                    "sustainability_practices": [],
                    "circular_economy_elements": []
                }
            },
            
            learning_growth={
                "strategic_capabilities": [],
                "organizational_culture": "",
                "change_readiness": "",
                "innovation_capacity": "",
                "human_capital": {
                    "competencies": [],
                    "leadership_capabilities": [],
                    "employee_engagement": "",
                    "learning_development": []
                },
                "intellectual_capital": {
                    "knowledge_assets": [],
                    "intellectual_property": [],
                    "data_analytics": "",
                    "innovation_pipeline": []
                }
            },
            
            value_creation={
                "value_creation_model": "",
                "integrated_thinking": [],
                "stakeholder_value": [],
                "long_term_sustainability": "",
                "capital_trade_offs": [],
                "value_measurement": []
            },
            
            # Analysis components from specialist agents
            analogy_analysis=None,
            logical_structure=None,
            implementation_plan=None,
            
            # Progress tracking
            completed_sections=[],
            completeness_percentage=0.0
        )
    
    def load_strategy_map(self, file_path: str) -> Optional[StrategyMapState]:
        """
        Load strategy map from JSON file.
        
        Args:
            file_path: Path to the strategy map JSON file
            
        Returns:
            StrategyMapState if file exists and is valid, None otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.debug(f"Strategy map file does not exist: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate that required fields exist
            required_fields = ['session_id', 'created_at', 'updated_at', 'version']
            if not all(field in data for field in required_fields):
                logger.error(f"Strategy map file missing required fields: {file_path}")
                return None
            
            logger.info(f"Successfully loaded strategy map: {file_path}")
            return StrategyMapState(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in strategy map file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading strategy map {file_path}: {e}")
            return None
    
    def save_strategy_map(self, strategy_map: StrategyMapState, file_path: str) -> bool:
        """
        Save strategy map to JSON file.
        
        Args:
            strategy_map: The strategy map state to save
            file_path: Path where to save the JSON file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Update metadata
            strategy_map["updated_at"] = datetime.now().isoformat()
            strategy_map["version"] = strategy_map.get("version", 1) + 1
            
            # Calculate completeness
            strategy_map["completeness_percentage"] = self._calculate_completeness(strategy_map)
            
            # Write to file with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(dict(strategy_map), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved strategy map: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving strategy map {file_path}: {e}")
            return False
    
    def get_or_create_strategy_map(self, session_id: str, file_path: str) -> StrategyMapState:
        """
        Load existing strategy map or create a new one.
        
        Args:
            session_id: Session identifier
            file_path: Path to the strategy map file
            
        Returns:
            StrategyMapState (either loaded or newly created)
        """
        # Try to load existing map
        strategy_map = self.load_strategy_map(file_path)
        
        if strategy_map is None:
            # Create new map
            logger.info(f"Creating new strategy map for session: {session_id}")
            strategy_map = self.create_empty_strategy_map(session_id)
            
            # Save the new map
            self.save_strategy_map(strategy_map, file_path)
        
        return strategy_map
    
    def update_why_insights(self, strategy_map: StrategyMapState, why_insights: Dict[str, Any]) -> StrategyMapState:
        """
        Update the strategy map with insights from the WHY Agent.
        
        Args:
            strategy_map: Current strategy map state
            why_insights: Insights from WHY Agent processing
            
        Returns:
            Updated strategy map
        """
        try:
            # Extract purpose, beliefs, and values from insights
            purpose = why_insights.get("purpose", "")
            beliefs = why_insights.get("beliefs", [])
            values = why_insights.get("values", [])
            
            # Update WHY section
            strategy_map["why"].update({
                "purpose": purpose,
                "beliefs": beliefs if isinstance(beliefs, list) else [beliefs],
                "values": values if isinstance(values, list) else [values],
                "golden_circle_complete": bool(purpose and (beliefs or values))
            })
            
            # Mark section as completed if we have substantial content
            if strategy_map["why"]["golden_circle_complete"]:
                if "why" not in strategy_map["completed_sections"]:
                    strategy_map["completed_sections"].append("why")
            
            logger.info("Updated strategy map with WHY insights")
            return strategy_map
            
        except Exception as e:
            logger.error(f"Error updating WHY insights: {e}")
            return strategy_map
    
    def update_analogy_insights(self, strategy_map: StrategyMapState, analogy_insights: Dict[str, Any]) -> StrategyMapState:
        """
        Update the strategy map with insights from the Analogy Agent.
        
        Args:
            strategy_map: Current strategy map state
            analogy_insights: Insights from Analogy Agent processing
            
        Returns:
            Updated strategy map
        """
        try:
            strategy_map["analogy_analysis"] = {
                "source_domains": analogy_insights.get("source_domains", []),
                "structural_mappings": analogy_insights.get("structural_mappings", []),
                "strategic_insights": analogy_insights.get("strategic_insights", []),
                "analogical_framework": analogy_insights.get("analogical_framework", ""),
                "completed_at": datetime.now().isoformat()
            }
            
            # Mark section as completed
            if "analogy_analysis" not in strategy_map["completed_sections"]:
                strategy_map["completed_sections"].append("analogy_analysis")
            
            logger.info("Updated strategy map with Analogy insights")
            return strategy_map
            
        except Exception as e:
            logger.error(f"Error updating Analogy insights: {e}")
            return strategy_map
    
    def update_logic_insights(self, strategy_map: StrategyMapState, logic_insights: Dict[str, Any]) -> StrategyMapState:
        """
        Update the strategy map with insights from the Logic Agent.
        
        Args:
            strategy_map: Current strategy map state
            logic_insights: Insights from Logic Agent processing
            
        Returns:
            Updated strategy map
        """
        try:
            strategy_map["logical_structure"] = {
                "argument_structure": logic_insights.get("argument_structure", ""),
                "validity_assessment": logic_insights.get("validity_assessment", ""),
                "soundness_evaluation": logic_insights.get("soundness_evaluation", ""),
                "logical_framework": logic_insights.get("logical_framework", ""),
                "completed_at": datetime.now().isoformat()
            }
            
            # Mark section as completed
            if "logical_structure" not in strategy_map["completed_sections"]:
                strategy_map["completed_sections"].append("logical_structure")
            
            logger.info("Updated strategy map with Logic insights")
            return strategy_map
            
        except Exception as e:
            logger.error(f"Error updating Logic insights: {e}")
            return strategy_map
    
    def update_implementation_insights(self, strategy_map: StrategyMapState, implementation_insights: Dict[str, Any]) -> StrategyMapState:
        """
        Update the strategy map with insights from the Open Strategy Agent.
        
        Args:
            strategy_map: Current strategy map state
            implementation_insights: Insights from Open Strategy Agent processing
            
        Returns:
            Updated strategy map
        """
        try:
            strategy_map["implementation_plan"] = {
                "stakeholder_analysis": implementation_insights.get("stakeholder_analysis", []),
                "process_design": implementation_insights.get("process_design", []),
                "resource_planning": implementation_insights.get("resource_planning", {}),
                "implementation_roadmap": implementation_insights.get("implementation_roadmap", []),
                "completed_at": datetime.now().isoformat()
            }
            
            # Mark section as completed
            if "implementation_plan" not in strategy_map["completed_sections"]:
                strategy_map["completed_sections"].append("implementation_plan")
            
            logger.info("Updated strategy map with Implementation insights")
            return strategy_map
            
        except Exception as e:
            logger.error(f"Error updating Implementation insights: {e}")
            return strategy_map
    
    def _calculate_completeness(self, strategy_map: StrategyMapState) -> float:
        """
        Calculate the completeness percentage of the strategy map.
        
        Args:
            strategy_map: Strategy map state
            
        Returns:
            Completeness percentage (0.0 to 100.0)
        """
        total_sections = 8  # why, stakeholder_customer, internal_processes, learning_growth, value_creation, analogy_analysis, logical_structure, implementation_plan
        completed_count = len(strategy_map["completed_sections"])
        
        # Add weight for core strategy map sections
        core_sections = ["stakeholder_customer", "internal_processes", "learning_growth", "value_creation"]
        core_completed = sum(1 for section in core_sections if section in strategy_map["completed_sections"])
        
        # WHY completion adds significant weight
        why_weight = 1.5 if "why" in strategy_map["completed_sections"] else 0
        
        # Calculate weighted completeness
        weighted_score = completed_count + (core_completed * 0.5) + why_weight
        max_possible = total_sections + (len(core_sections) * 0.5) + 1.5
        
        return min(100.0, (weighted_score / max_possible) * 100)
    
    def _extract_why_insights(self, agent_output: str) -> Dict[str, Any]:
        """
        Extract WHY insights from agent output using LLM analysis.
        
        Args:
            agent_output: Output text from WHY Agent
            
        Returns:
            Dictionary containing extracted purpose, beliefs, and values
        """
        try:
            prompt = f"""
            Analyze this WHY Agent output and extract the core strategic insights:
            
            {agent_output}
            
            Extract and return JSON with:
            {{
                "purpose": "core organizational purpose/mission statement",
                "beliefs": ["key belief 1", "key belief 2", ...],
                "values": ["core value 1", "core value 2", ...]
            }}
            
            Focus on concrete, actionable insights that define the organization's WHY.
            """
            
            response = self.llm_client.invoke(prompt)
            
            # Try to parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback extraction
            return {
                "purpose": self._extract_text_after(agent_output, ["purpose", "mission", "why"]),
                "beliefs": self._extract_list_items(agent_output, ["belief", "believe"]),
                "values": self._extract_list_items(agent_output, ["value", "principle"])
            }
            
        except Exception as e:
            logger.error(f"Error extracting WHY insights: {e}")
            return {"purpose": "", "beliefs": [], "values": []}
    
    def _extract_analogy_insights(self, agent_output: str) -> Dict[str, Any]:
        """
        Extract Analogy insights from agent output.
        
        Args:
            agent_output: Output text from Analogy Agent
            
        Returns:
            Dictionary containing analogical reasoning insights
        """
        try:
            return {
                "source_domains": self._extract_list_items(agent_output, ["company", "organization", "example"]),
                "structural_mappings": self._extract_list_items(agent_output, ["mapping", "relationship", "parallel"]),
                "strategic_insights": self._extract_list_items(agent_output, ["insight", "learning", "takeaway"]),
                "analogical_framework": self._extract_text_after(agent_output, ["framework", "structure", "model"])
            }
        except Exception as e:
            logger.error(f"Error extracting Analogy insights: {e}")
            return {"source_domains": [], "structural_mappings": [], "strategic_insights": [], "analogical_framework": ""}
    
    def _extract_logic_insights(self, agent_output: str) -> Dict[str, Any]:
        """
        Extract Logic insights from agent output.
        
        Args:
            agent_output: Output text from Logic Agent
            
        Returns:
            Dictionary containing logical analysis insights
        """
        try:
            return {
                "argument_structure": self._extract_text_after(agent_output, ["argument", "premise", "structure"]),
                "validity_assessment": self._extract_text_after(agent_output, ["validity", "valid", "logical"]),
                "soundness_evaluation": self._extract_text_after(agent_output, ["soundness", "sound", "evidence"]),
                "logical_framework": self._extract_text_after(agent_output, ["framework", "logic", "reasoning"])
            }
        except Exception as e:
            logger.error(f"Error extracting Logic insights: {e}")
            return {"argument_structure": "", "validity_assessment": "", "soundness_evaluation": "", "logical_framework": ""}
    
    def _extract_implementation_insights(self, agent_output: str) -> Dict[str, Any]:
        """
        Extract Implementation insights from agent output.
        
        Args:
            agent_output: Output text from Open Strategy Agent
            
        Returns:
            Dictionary containing implementation planning insights
        """
        try:
            return {
                "stakeholder_analysis": self._extract_list_items(agent_output, ["stakeholder", "people", "team"]),
                "process_design": self._extract_list_items(agent_output, ["process", "workflow", "procedure"]),
                "resource_planning": {
                    "resources": self._extract_list_items(agent_output, ["resource", "capability", "skill"]),
                    "budget": self._extract_text_after(agent_output, ["budget", "cost", "investment"]),
                    "timeline": self._extract_text_after(agent_output, ["timeline", "schedule", "phase"])
                },
                "implementation_roadmap": self._extract_list_items(agent_output, ["milestone", "phase", "step"])
            }
        except Exception as e:
            logger.error(f"Error extracting Implementation insights: {e}")
            return {"stakeholder_analysis": [], "process_design": [], "resource_planning": {}, "implementation_roadmap": []}
    
    def _extract_text_after(self, text: str, keywords: List[str]) -> str:
        """
        Extract text that appears after specified keywords.
        
        Args:
            text: Text to search
            keywords: List of keywords to search for
            
        Returns:
            Extracted text or empty string
        """
        import re
        
        for keyword in keywords:
            # Look for keyword followed by colon or other separators
            pattern = rf'{keyword}[:\-\s]+(.*?)(?:\n|$|[.!?]\s)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_list_items(self, text: str, keywords: List[str]) -> List[str]:
        """
        Extract list items related to keywords.
        
        Args:
            text: Text to search
            keywords: List of keywords to search for
            
        Returns:
            List of extracted items
        """
        import re
        
        items = []
        
        for keyword in keywords:
            # Look for bullet points, numbers, or comma-separated lists
            patterns = [
                rf'[•\-\*]\s*([^.\n]*{keyword}[^.\n]*)',
                rf'\d+\.\s*([^.\n]*{keyword}[^.\n]*)',
                rf'({keyword}[^,.\n]*)',
                rf'([^,.\n]*{keyword}[^,.\n]*)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                items.extend([match.strip() for match in matches if match.strip()])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in items:
            if item.lower() not in seen and len(item) > 5:  # Filter very short items
                seen.add(item.lower())
                unique_items.append(item)
        
        return unique_items[:10]  # Limit to top 10 items
    
    def validate_strategy_map(self, strategy_map: StrategyMapState) -> Dict[str, Any]:
        """
        Validate strategy map for consistency and completeness.
        
        Args:
            strategy_map: Strategy map state to validate
            
        Returns:
            Dictionary containing validation results and recommendations
        """
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": [],
            "consistency_score": 0.0
        }
        
        try:
            # Check required metadata
            if not strategy_map.get("session_id"):
                validation_results["errors"].append("Missing session_id")
                validation_results["is_valid"] = False
            
            if not strategy_map.get("created_at"):
                validation_results["errors"].append("Missing created_at timestamp")
                validation_results["is_valid"] = False
            
            # Validate WHY section consistency
            why_validation = self._validate_why_section(strategy_map["why"])
            validation_results["errors"].extend(why_validation["errors"])
            validation_results["warnings"].extend(why_validation["warnings"])
            
            # Validate perspective alignment
            perspectives_validation = self._validate_perspectives_alignment(strategy_map)
            validation_results["errors"].extend(perspectives_validation["errors"])
            validation_results["warnings"].extend(perspectives_validation["warnings"])
            
            # Validate value components integration
            value_validation = self._validate_value_components(strategy_map)
            validation_results["warnings"].extend(value_validation["warnings"])
            validation_results["recommendations"].extend(value_validation["recommendations"])
            
            # Calculate consistency score
            validation_results["consistency_score"] = self._calculate_consistency_score(strategy_map)
            
            # Add strategic recommendations based on completeness
            strategic_recs = self._generate_strategic_recommendations(strategy_map)
            validation_results["recommendations"].extend(strategic_recs)
            
            if validation_results["errors"]:
                validation_results["is_valid"] = False
            
            logger.info(f"Strategy map validation completed - Consistency score: {validation_results['consistency_score']:.1f}")
            
        except Exception as e:
            logger.error(f"Error validating strategy map: {e}")
            validation_results["errors"].append(f"Validation error: {str(e)}")
            validation_results["is_valid"] = False
        
        return validation_results
    
    def _validate_why_section(self, why_section: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate the WHY section for completeness and consistency."""
        result = {"errors": [], "warnings": []}
        
        purpose = why_section.get("purpose", "")
        beliefs = why_section.get("beliefs", [])
        values = why_section.get("values", [])
        
        if not purpose and why_section.get("golden_circle_complete", False):
            result["errors"].append("WHY marked complete but missing purpose statement")
        
        if not beliefs and not values and why_section.get("golden_circle_complete", False):
            result["warnings"].append("WHY section complete but missing beliefs or values")
        
        if purpose and len(purpose.split()) < 5:
            result["warnings"].append("Purpose statement seems very brief - consider elaborating")
        
        if len(beliefs) > 10:
            result["warnings"].append("Many beliefs listed - consider consolidating to core beliefs")
        
        if len(values) > 8:
            result["warnings"].append("Many values listed - consider focusing on 3-5 core values")
        
        return result
    
    def _validate_perspectives_alignment(self, strategy_map: StrategyMapState) -> Dict[str, List[str]]:
        """Validate alignment between the four strategic perspectives."""
        result = {"errors": [], "warnings": []}
        
        # Check if stakeholder outcomes align with value creation
        stakeholder_section = strategy_map.get("stakeholder_customer", {})
        value_section = strategy_map.get("value_creation", {})
        
        stakeholder_outcomes = stakeholder_section.get("stakeholder_outcomes", [])
        value_creation_model = value_section.get("value_creation_model", "")
        
        if stakeholder_outcomes and not value_creation_model:
            result["warnings"].append("Stakeholder outcomes defined but value creation model missing")
        
        # Check if internal processes support stakeholder value
        internal_section = strategy_map.get("internal_processes", {})
        core_processes = internal_section.get("core_processes", [])
        
        if not core_processes and stakeholder_outcomes:
            result["warnings"].append("Stakeholder outcomes defined but core processes not specified")
        
        # Check if learning & growth supports internal processes
        learning_section = strategy_map.get("learning_growth", {})
        capabilities = learning_section.get("strategic_capabilities", [])
        
        if core_processes and not capabilities:
            result["warnings"].append("Core processes defined but strategic capabilities not specified")
        
        return result
    
    def _validate_value_components(self, strategy_map: StrategyMapState) -> Dict[str, List[str]]:
        """Validate the Six Value Components integration."""
        result = {"warnings": [], "recommendations": []}
        
        # Check each perspective for value component integration
        perspectives = {
            "stakeholder_customer": strategy_map.get("stakeholder_customer", {}),
            "internal_processes": strategy_map.get("internal_processes", {}),
            "learning_growth": strategy_map.get("learning_growth", {})
        }
        
        for perspective_name, perspective_data in perspectives.items():
            # Check which value components are present
            present_components = []
            
            if "financial_capital" in perspective_data and perspective_data["financial_capital"]:
                present_components.append("financial")
            if "manufactured_capital" in perspective_data and perspective_data["manufactured_capital"]:
                present_components.append("manufactured")
            if "intellectual_capital" in perspective_data and perspective_data["intellectual_capital"]:
                present_components.append("intellectual")
            if "human_capital" in perspective_data and perspective_data["human_capital"]:
                present_components.append("human")
            if "social_relationship_capital" in perspective_data and perspective_data["social_relationship_capital"]:
                present_components.append("social_relationship")
            if "natural_capital" in perspective_data and perspective_data["natural_capital"]:
                present_components.append("natural")
            
            if len(present_components) < 2:
                result["recommendations"].append(
                    f"Consider integrating more value components in {perspective_name.replace('_', ' ')} perspective"
                )
        
        return result
    
    def _calculate_consistency_score(self, strategy_map: StrategyMapState) -> float:
        """Calculate a consistency score for the strategy map."""
        score = 0.0
        max_score = 100.0
        
        # WHY completeness (20 points)
        why_section = strategy_map.get("why", {})
        if why_section.get("purpose"):
            score += 10
        if why_section.get("beliefs") or why_section.get("values"):
            score += 10
        
        # Perspectives alignment (40 points)
        perspectives = ["stakeholder_customer", "internal_processes", "learning_growth", "value_creation"]
        completed_perspectives = sum(1 for p in perspectives if p in strategy_map["completed_sections"])
        score += (completed_perspectives / len(perspectives)) * 40
        
        # Specialist agent integration (30 points)
        specialist_sections = ["analogy_analysis", "logical_structure", "implementation_plan"]
        completed_specialists = sum(1 for s in specialist_sections if strategy_map.get(s))
        score += (completed_specialists / len(specialist_sections)) * 30
        
        # Value components integration (10 points)
        value_components_present = 0
        for perspective in ["stakeholder_customer", "internal_processes", "learning_growth"]:
            perspective_data = strategy_map.get(perspective, {})
            for component in self.value_components:
                if component in perspective_data and perspective_data[component]:
                    value_components_present += 1
        
        score += min(10, (value_components_present / len(self.value_components)) * 10)
        
        return min(max_score, score)
    
    def _generate_strategic_recommendations(self, strategy_map: StrategyMapState) -> List[str]:
        """Generate strategic recommendations based on current state."""
        recommendations = []
        completed_sections = strategy_map.get("completed_sections", [])
        completeness_pct = strategy_map.get("completeness_percentage", 0)
        
        # Phase-based recommendations
        if "why" not in completed_sections:
            recommendations.append("Complete the WHY discovery to establish strategic foundation")
        elif completeness_pct < 30:
            recommendations.append("Focus on stakeholder value propositions and internal processes")
        elif completeness_pct < 60:
            recommendations.append("Develop learning & growth capabilities and value creation model")
        elif completeness_pct < 80:
            recommendations.append("Integrate specialist agent insights and refine implementation plan")
        else:
            recommendations.append("Review strategy for consistency and prepare for execution")
        
        # Specific section recommendations
        if "analogy_analysis" not in completed_sections and "why" in completed_sections:
            recommendations.append("Explore analogical insights to enhance strategic thinking")
        
        if "logical_structure" not in completed_sections and len(completed_sections) >= 3:
            recommendations.append("Validate strategic logic to ensure sound reasoning")
        
        if "implementation_plan" not in completed_sections and completeness_pct > 50:
            recommendations.append("Develop implementation roadmap for strategy execution")
        
        return recommendations


def create_strategy_map_node():
    """
    Create a LangGraph node function for the Strategy Map Agent.
    
    Returns:
        Function that can be used as a node in the orchestrator workflow
    """
    
    def strategy_map_node(state: AgentState) -> AgentState:
        """
        Strategy Map Agent node function for LangGraph workflow.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state with strategy map updates
        """
        try:
            agent = StrategyMapAgent()
            
            # Load or create strategy map
            strategy_map = agent.get_or_create_strategy_map(
                session_id=state["session_id"],
                file_path=state["strategy_map_path"]
            )
            
            # Update strategy map based on current processing stage and agent output
            current_agent = state.get("current_agent")
            agent_output = state.get("agent_output")
            
            if current_agent and agent_output:
                # Parse agent output and update appropriate section
                if current_agent == "why_agent":
                    # Extract WHY insights from agent output
                    why_insights = agent._extract_why_insights(agent_output)
                    strategy_map = agent.update_why_insights(strategy_map, why_insights)
                    
                elif current_agent == "analogy_agent":
                    # Extract Analogy insights from agent output
                    analogy_insights = agent._extract_analogy_insights(agent_output)
                    strategy_map = agent.update_analogy_insights(strategy_map, analogy_insights)
                    
                elif current_agent == "logic_agent":
                    # Extract Logic insights from agent output
                    logic_insights = agent._extract_logic_insights(agent_output)
                    strategy_map = agent.update_logic_insights(strategy_map, logic_insights)
                    
                elif current_agent == "open_strategy_agent":
                    # Extract Implementation insights from agent output
                    implementation_insights = agent._extract_implementation_insights(agent_output)
                    strategy_map = agent.update_implementation_insights(strategy_map, implementation_insights)
            
            # Save updated strategy map
            agent.save_strategy_map(strategy_map, state["strategy_map_path"])
            
            # Update state with strategy map completeness
            completeness_pct = strategy_map["completeness_percentage"]
            state["conversation_summary"] = f"Strategy map {completeness_pct:.1f}% complete"
            
            # Update strategy completeness in state
            for section in strategy_map["completed_sections"]:
                state["strategy_completeness"][section] = True
            
            logger.info(f"Strategy map updated - {completeness_pct:.1f}% complete")
            return state
            
        except Exception as e:
            logger.error(f"Error in strategy map node: {e}")
            # Return state unchanged if error occurs
            return state
    
    return strategy_map_node