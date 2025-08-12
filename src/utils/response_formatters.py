"""
Response formatting utilities for Strategy Coach agents.

This module provides specialized formatters for each agent type to ensure consistent,
well-structured, and methodology-appropriate responses across all specialist agents.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from . import get_logger

logger = get_logger(__name__)


class ResponseFormat(Enum):
    """Supported response formats."""
    STRUCTURED = "structured"
    CONVERSATIONAL = "conversational"
    BULLET_POINTS = "bullet_points"
    NUMBERED_LIST = "numbered_list"
    JSON = "json"
    MARKDOWN = "markdown"


@dataclass
class FormattedResponse:
    """Container for formatted agent responses."""
    content: str
    format_type: ResponseFormat
    metadata: Dict[str, Any]
    agent_type: str
    stage: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "format_type": self.format_type.value,
            "metadata": self.metadata,
            "agent_type": self.agent_type,
            "stage": self.stage,
            "timestamp": self.timestamp.isoformat()
        }


class BaseResponseFormatter:
    """Base class for agent response formatters."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.supported_formats = [ResponseFormat.CONVERSATIONAL, ResponseFormat.STRUCTURED]
    
    def format_response(self, raw_response: str, stage: str, 
                       format_type: ResponseFormat = ResponseFormat.CONVERSATIONAL,
                       metadata: Optional[Dict[str, Any]] = None) -> FormattedResponse:
        """
        Format a raw agent response according to the specified format.
        
        Args:
            raw_response: Raw response text from the agent
            stage: Current stage of the agent methodology
            format_type: Desired output format
            metadata: Additional metadata to include
            
        Returns:
            FormattedResponse with formatted content
        """
        if format_type not in self.supported_formats:
            logger.warning(f"Unsupported format {format_type} for {self.agent_type}, using conversational")
            format_type = ResponseFormat.CONVERSATIONAL
        
        formatted_content = self._format_content(raw_response, stage, format_type)
        
        return FormattedResponse(
            content=formatted_content,
            format_type=format_type,
            metadata=metadata or {},
            agent_type=self.agent_type,
            stage=stage,
            timestamp=datetime.now()
        )
    
    def _format_content(self, raw_response: str, stage: str, format_type: ResponseFormat) -> str:
        """Format the content according to the specified format type."""
        if format_type == ResponseFormat.STRUCTURED:
            return self._format_structured(raw_response, stage)
        elif format_type == ResponseFormat.BULLET_POINTS:
            return self._format_bullet_points(raw_response, stage)
        elif format_type == ResponseFormat.NUMBERED_LIST:
            return self._format_numbered_list(raw_response, stage)
        elif format_type == ResponseFormat.MARKDOWN:
            return self._format_markdown(raw_response, stage)
        else:
            return self._format_conversational(raw_response, stage)
    
    def _format_conversational(self, response: str, stage: str) -> str:
        """Format as conversational response."""
        return response.strip()
    
    def _format_structured(self, response: str, stage: str) -> str:
        """Format as structured response with clear sections."""
        # Base implementation - can be overridden by specific formatters
        lines = response.strip().split('\n')
        structured_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Add formatting for headers
                if line.isupper() or line.startswith('**') or line.endswith('**'):
                    structured_lines.append(f"\n## {line.strip('*')}\n")
                else:
                    structured_lines.append(line)
        
        return '\n'.join(structured_lines).strip()
    
    def _format_bullet_points(self, response: str, stage: str) -> str:
        """Format as bullet points."""
        lines = response.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('-') and not line.startswith('•'):
                formatted_lines.append(f"• {line}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_numbered_list(self, response: str, stage: str) -> str:
        """Format as numbered list."""
        lines = response.strip().split('\n')
        formatted_lines = []
        counter = 1
        
        for line in lines:
            line = line.strip()
            if line and not re.match(r'^\d+\.', line):
                formatted_lines.append(f"{counter}. {line}")
                counter += 1
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_markdown(self, response: str, stage: str) -> str:
        """Format as markdown."""
        # Basic markdown formatting
        response = response.strip()
        
        # Add stage header
        stage_title = stage.replace('_', ' ').title()
        return f"# {stage_title}\n\n{response}"


class WHYAgentFormatter(BaseResponseFormatter):
    """Specialized formatter for WHY Agent responses."""
    
    def __init__(self):
        super().__init__("why_agent")
        self.supported_formats.extend([
            ResponseFormat.BULLET_POINTS, 
            ResponseFormat.MARKDOWN,
            ResponseFormat.JSON
        ])
    
    def _format_structured(self, response: str, stage: str) -> str:
        """Format WHY Agent response with Golden Circle structure."""
        
        stage_templates = {
            "purpose_discovery": self._format_purpose_discovery,
            "belief_exploration": self._format_belief_exploration, 
            "values_integration": self._format_values_integration,
            "synthesis": self._format_synthesis
        }
        
        formatter = stage_templates.get(stage, self._default_structured_format)
        return formatter(response)
    
    def _format_purpose_discovery(self, response: str) -> str:
        """Format purpose discovery response."""
        sections = self._extract_sections(response, [
            "purpose", "why", "motivation", "mission", "reason", "exist"
        ])
        
        formatted = "## 🎯 Purpose Discovery - Golden Circle WHY\n\n"
        
        if "purpose" in sections:
            formatted += "### Core Purpose\n"
            formatted += sections["purpose"] + "\n\n"
        
        formatted += "### Exploration Questions\n"
        questions = self._extract_questions(response)
        for i, question in enumerate(questions, 1):
            formatted += f"{i}. {question}\n"
        
        formatted += "\n### Next Steps\n"
        formatted += "Continue exploring your core beliefs that support this purpose.\n"
        
        return formatted
    
    def _format_belief_exploration(self, response: str) -> str:
        """Format belief exploration response."""
        formatted = "## 💭 Core Beliefs Exploration\n\n"
        
        beliefs = self._extract_beliefs(response)
        if beliefs:
            formatted += "### Identified Beliefs\n"
            for belief in beliefs:
                formatted += f"• **{belief}**\n"
            formatted += "\n"
        
        formatted += "### Belief Validation Questions\n"
        questions = self._extract_questions(response)
        for question in questions:
            formatted += f"• {question}\n"
        
        return formatted
    
    def _format_values_integration(self, response: str) -> str:
        """Format values integration response."""
        formatted = "## ⚖️ Organizational Values\n\n"
        
        values = self._extract_values(response)
        if values:
            formatted += "### Core Values\n"
            for i, value in enumerate(values, 1):
                formatted += f"{i}. **{value}**\n"
            formatted += "\n"
        
        formatted += "### Values in Action\n"
        formatted += "How these values guide behavior and decisions:\n\n"
        formatted += self._extract_behavioral_guidance(response)
        
        return formatted
    
    def _format_synthesis(self, response: str) -> str:
        """Format WHY synthesis response."""
        formatted = "## 🔄 Golden Circle WHY Synthesis\n\n"
        
        # Extract WHY statement
        why_statement = self._extract_why_statement(response)
        if why_statement:
            formatted += "### Your WHY Statement\n"
            formatted += f"*{why_statement}*\n\n"
        
        # Extract components
        formatted += "### Golden Circle Components\n"
        formatted += "- **WHY**: " + self._extract_section_content(response, "why") + "\n"
        formatted += "- **Beliefs**: " + self._extract_section_content(response, "beliefs") + "\n" 
        formatted += "- **Values**: " + self._extract_section_content(response, "values") + "\n\n"
        
        formatted += "### Transition to HOW\n"
        formatted += "Now that your WHY is clear, we can explore HOW to bring this purpose to life.\n"
        
        return formatted
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from response text."""
        questions = []
        for line in text.split('\n'):
            line = line.strip()
            if '?' in line:
                # Clean up question formatting
                question = re.sub(r'^[-•\*]\s*', '', line)
                question = re.sub(r'^"([^"]*)"$', r'\1', question)
                if question:
                    questions.append(question)
        return questions[:5]  # Limit to 5 questions
    
    def _extract_beliefs(self, text: str) -> List[str]:
        """Extract core beliefs from response text."""
        beliefs = []
        belief_patterns = [
            r'believe[sd]?\s+(?:that\s+)?([^.!?]+)',
            r'conviction[s]?\s+(?:about\s+)?([^.!?]+)',
            r'principle[s]?\s+(?:of\s+)?([^.!?]+)'
        ]
        
        for pattern in belief_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                belief = match.group(1).strip()
                if len(belief) > 10:  # Filter out very short matches
                    beliefs.append(belief)
        
        return beliefs[:3]  # Limit to top 3 beliefs
    
    def _extract_values(self, text: str) -> List[str]:
        """Extract organizational values from response text."""
        values = []
        
        # Look for value-indicating patterns
        value_patterns = [
            r'value[s]?\s*:?\s*([^.!?\n]+)',
            r'important\s+to\s+([^.!?\n]+)',
            r'guide[sd]?\s+by\s+([^.!?\n]+)'
        ]
        
        for pattern in value_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1).strip()
                if len(value) > 5:
                    values.append(value)
        
        return values[:4]  # Limit to 4 values
    
    def _extract_why_statement(self, text: str) -> str:
        """Extract the main WHY statement from synthesis."""
        patterns = [
            r'why statement[:\s]*([^.!?\n]+(?:[.!?])?)',
            r'core purpose[:\s]*([^.!?\n]+(?:[.!?])?)',
            r'exists to\s+([^.!?\n]+(?:[.!?])?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_sections(self, text: str, keywords: List[str]) -> Dict[str, str]:
        """Extract sections based on keywords."""
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower()
            found_keyword = None
            
            for keyword in keywords:
                if keyword in line_lower:
                    found_keyword = keyword
                    break
            
            if found_keyword:
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = found_keyword
                current_content = [line]
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_section_content(self, text: str, section: str) -> str:
        """Extract content for a specific section."""
        pattern = rf'{section}[:\s]*([^.!?\n]+(?:[.!?])?)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else "To be defined"
    
    def _extract_behavioral_guidance(self, text: str) -> str:
        """Extract behavioral guidance from values response."""
        guidance_lines = []
        for line in text.split('\n'):
            line = line.strip()
            if any(word in line.lower() for word in ['behavior', 'act', 'decision', 'culture']):
                guidance_lines.append(line)
        
        return '\n'.join(guidance_lines) if guidance_lines else "Values guide daily decisions and behaviors."
    
    def _default_structured_format(self, response: str) -> str:
        """Default structured format for WHY Agent."""
        return f"## Golden Circle Exploration\n\n{response}"


class AnalogyAgentFormatter(BaseResponseFormatter):
    """Specialized formatter for Analogy Agent responses."""
    
    def __init__(self):
        super().__init__("analogy_agent")
        self.supported_formats.extend([
            ResponseFormat.BULLET_POINTS, 
            ResponseFormat.MARKDOWN,
            ResponseFormat.JSON
        ])
    
    def _format_structured(self, response: str, stage: str) -> str:
        """Format Analogy Agent response with analogical reasoning structure."""
        
        stage_templates = {
            "source_identification": self._format_source_identification,
            "structural_mapping": self._format_structural_mapping,
            "evaluation_adaptation": self._format_evaluation_adaptation,
            "strategic_integration": self._format_strategic_integration
        }
        
        formatter = stage_templates.get(stage, self._default_structured_format)
        return formatter(response)
    
    def _format_source_identification(self, response: str) -> str:
        """Format source identification response."""
        formatted = "## 🔍 Source Domain Identification\n\n"
        
        sources = self._extract_analogical_sources(response)
        if sources:
            formatted += "### Identified Source Domains\n"
            for i, source in enumerate(sources, 1):
                formatted += f"{i}. **{source['domain']}**: {source['description']}\n"
            formatted += "\n"
        
        formatted += "### Strategic Relevance\n"
        formatted += self._extract_relevance_explanation(response)
        
        formatted += "\n### Next Steps\n"
        formatted += "Map structural relationships between source domains and your strategic situation.\n"
        
        return formatted
    
    def _format_structural_mapping(self, response: str) -> str:
        """Format structural mapping response."""
        formatted = "## 🗺️ Structural Mapping Analysis\n\n"
        
        mappings = self._extract_mappings(response)
        if mappings:
            formatted += "### Structural Correspondences\n"
            for mapping in mappings:
                formatted += f"• **{mapping['source']}** → **{mapping['target']}**\n"
                formatted += f"  *Relationship*: {mapping['relationship']}\n\n"
        
        formatted += "### Key Patterns\n"
        patterns = self._extract_patterns(response)
        for pattern in patterns:
            formatted += f"• {pattern}\n"
        
        return formatted
    
    def _format_evaluation_adaptation(self, response: str) -> str:
        """Format evaluation and adaptation response."""
        formatted = "## ⚖️ Analogy Evaluation & Adaptation\n\n"
        
        # Extract quality assessment
        quality = self._extract_quality_assessment(response)
        if quality:
            formatted += "### Analogy Quality Assessment\n"
            for criterion, score in quality.items():
                formatted += f"• **{criterion}**: {score}\n"
            formatted += "\n"
        
        # Extract insights
        insights = self._extract_insights(response)
        if insights:
            formatted += "### Key Strategic Insights\n"
            for insight in insights:
                formatted += f"• {insight}\n"
            formatted += "\n"
        
        formatted += "### Adaptation Considerations\n"
        formatted += self._extract_adaptations(response)
        
        return formatted
    
    def _format_strategic_integration(self, response: str) -> str:
        """Format strategic integration response."""
        formatted = "## 🔄 Strategic Integration\n\n"
        
        # Extract framework
        framework = self._extract_strategic_framework(response)
        if framework:
            formatted += "### Analogical Strategic Framework\n"
            formatted += framework + "\n\n"
        
        # Extract approach
        approach = self._extract_strategic_approach(response)
        if approach:
            formatted += "### Strategic Approach\n"
            formatted += approach + "\n\n"
        
        formatted += "### Implementation Implications\n"
        formatted += self._extract_implementation_implications(response)
        
        formatted += "\n### Transition to Implementation\n"
        formatted += "These analogical insights provide the foundation for developing specific implementation strategies.\n"
        
        return formatted
    
    def _extract_analogical_sources(self, text: str) -> List[Dict[str, str]]:
        """Extract analogical source domains."""
        sources = []
        
        # Look for domain patterns
        domain_patterns = [
            r'(\w+\s+industry|\w+\s+domain|\w+\s+sector)[:\s]*([^.!?\n]+)',
            r'example[s]?\s+from\s+([^:]+)[:\s]*([^.!?\n]+)',
            r'analogy\s+to\s+([^:]+)[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in domain_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                sources.append({
                    "domain": match.group(1).strip(),
                    "description": match.group(2).strip()
                })
        
        return sources[:3]  # Limit to 3 sources
    
    def _extract_mappings(self, text: str) -> List[Dict[str, str]]:
        """Extract structural mappings."""
        mappings = []
        
        # Look for mapping patterns
        mapping_patterns = [
            r'([^→]+)→([^.!?\n]+)',
            r'([^:]+):\s*corresponds to\s+([^.!?\n]+)',
            r'([^:]+):\s*maps to\s+([^.!?\n]+)'
        ]
        
        for pattern in mapping_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mappings.append({
                    "source": match.group(1).strip(),
                    "target": match.group(2).strip(),
                    "relationship": "structural correspondence"
                })
        
        return mappings[:5]  # Limit to 5 mappings
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract key patterns from mapping analysis."""
        patterns = []
        
        pattern_indicators = ['pattern', 'structure', 'relationship', 'mechanism']
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in pattern_indicators):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 10:
                    patterns.append(clean_line)
        
        return patterns[:4]  # Limit to 4 patterns
    
    def _extract_quality_assessment(self, text: str) -> Dict[str, str]:
        """Extract quality assessment criteria and scores."""
        quality = {}
        
        criteria = ['structural similarity', 'causal relevance', 'contextual fit', 'actionability']
        
        for criterion in criteria:
            pattern = rf'{criterion}[:\s]*([^.!?\n]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                quality[criterion.title()] = match.group(1).strip()
        
        return quality
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extract strategic insights."""
        insights = []
        
        insight_patterns = [
            r'insight[s]?[:\s]*([^.!?\n]+)',
            r'implication[s]?[:\s]*([^.!?\n]+)',
            r'learning[s]?[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in insight_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                insight = match.group(1).strip()
                if len(insight) > 15:
                    insights.append(insight)
        
        return insights[:4]  # Limit to 4 insights
    
    def _extract_adaptations(self, text: str) -> str:
        """Extract adaptation considerations."""
        lines = text.split('\n')
        adaptation_lines = []
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['adapt', 'modify', 'adjust', 'customize']):
                adaptation_lines.append(line)
        
        return '\n'.join(adaptation_lines) if adaptation_lines else "Consider contextual adaptations for your specific situation."
    
    def _extract_strategic_framework(self, text: str) -> str:
        """Extract strategic framework from integration response."""
        framework_patterns = [
            r'framework[:\s]*([^.!?]*(?:[.!?])?)',
            r'strategic\s+approach[:\s]*([^.!?]*(?:[.!?])?)',
            r'integration[:\s]*([^.!?]*(?:[.!?])?)'
        ]
        
        for pattern in framework_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(1)) > 20:
                return match.group(1).strip()
        
        return ""
    
    def _extract_strategic_approach(self, text: str) -> str:
        """Extract strategic approach."""
        approach_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['approach', 'strategy', 'method', 'way']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    approach_lines.append(clean_line)
        
        return '\n'.join(approach_lines[:3]) if approach_lines else "Strategic approach based on analogical insights."
    
    def _extract_implementation_implications(self, text: str) -> str:
        """Extract implementation implications."""
        impl_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['implement', 'execution', 'action', 'practice']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 10:
                    impl_lines.append(clean_line)
        
        return '\n'.join(impl_lines[:3]) if impl_lines else "Apply analogical insights to guide implementation decisions."
    
    def _extract_relevance_explanation(self, text: str) -> str:
        """Extract relevance explanation for source domains."""
        relevance_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['relevant', 'applicable', 'similar', 'parallel']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    relevance_lines.append(clean_line)
        
        return '\n'.join(relevance_lines[:2]) if relevance_lines else "These domains share structural similarities with your strategic challenges."
    
    def _default_structured_format(self, response: str) -> str:
        """Default structured format for Analogy Agent."""
        return f"## Analogical Reasoning Analysis\n\n{response}"


class LogicAgentFormatter(BaseResponseFormatter):
    """Specialized formatter for Logic Agent responses."""
    
    def __init__(self):
        super().__init__("logic_agent")
        self.supported_formats.extend([
            ResponseFormat.BULLET_POINTS, 
            ResponseFormat.MARKDOWN,
            ResponseFormat.JSON
        ])
    
    def _format_structured(self, response: str, stage: str) -> str:
        """Format Logic Agent response with logical structure."""
        
        stage_templates = {
            "argument_analysis": self._format_argument_analysis,
            "validity_assessment": self._format_validity_assessment,
            "soundness_evaluation": self._format_soundness_evaluation,
            "framework_construction": self._format_framework_construction
        }
        
        formatter = stage_templates.get(stage, self._default_structured_format)
        return formatter(response)
    
    def _format_argument_analysis(self, response: str) -> str:
        """Format argument analysis response."""
        formatted = "## 🔍 Logical Argument Analysis\n\n"
        
        # Extract premises
        premises = self._extract_premises(response)
        if premises:
            formatted += "### Identified Premises\n"
            for i, premise in enumerate(premises, 1):
                formatted += f"{i}. {premise}\n"
            formatted += "\n"
        
        # Extract conclusions
        conclusions = self._extract_conclusions(response)
        if conclusions:
            formatted += "### Strategic Conclusions\n"
            for conclusion in conclusions:
                formatted += f"• {conclusion}\n"
            formatted += "\n"
        
        # Extract logical connections
        formatted += "### Logical Structure\n"
        formatted += self._extract_logical_structure(response)
        
        formatted += "\n### Next Steps\n"
        formatted += "Assess the validity of logical connections between premises and conclusions.\n"
        
        return formatted
    
    def _format_validity_assessment(self, response: str) -> str:
        """Format validity assessment response."""
        formatted = "## ✅ Logical Validity Assessment\n\n"
        
        # Extract validity evaluation
        validity = self._extract_validity_evaluation(response)
        if validity:
            formatted += "### Validity Analysis\n"
            for aspect, assessment in validity.items():
                formatted += f"• **{aspect}**: {assessment}\n"
            formatted += "\n"
        
        # Extract logical gaps
        gaps = self._extract_logical_gaps(response)
        if gaps:
            formatted += "### Identified Logical Gaps\n"
            for gap in gaps:
                formatted += f"• {gap}\n"
            formatted += "\n"
        
        # Extract recommendations
        formatted += "### Recommendations\n"
        formatted += self._extract_validity_recommendations(response)
        
        return formatted
    
    def _format_soundness_evaluation(self, response: str) -> str:
        """Format soundness evaluation response."""
        formatted = "## 🎯 Argument Soundness Evaluation\n\n"
        
        # Extract premise truth assessment
        truth_assessment = self._extract_truth_assessment(response)
        if truth_assessment:
            formatted += "### Premise Truth Assessment\n"
            for premise, assessment in truth_assessment.items():
                formatted += f"• **{premise}**: {assessment}\n"
            formatted += "\n"
        
        # Extract evidence quality
        evidence = self._extract_evidence_analysis(response)
        if evidence:
            formatted += "### Evidence Quality Analysis\n"
            formatted += evidence + "\n\n"
        
        # Extract risk analysis
        formatted += "### Risk Assessment\n"
        formatted += self._extract_risk_assessment(response)
        
        return formatted
    
    def _format_framework_construction(self, response: str) -> str:
        """Format framework construction response."""
        formatted = "## 🏗️ Strategic Logic Framework\n\n"
        
        # Extract logical framework
        framework = self._extract_logical_framework(response)
        if framework:
            formatted += "### Validated Logical Structure\n"
            formatted += framework + "\n\n"
        
        # Extract decision logic
        decision_logic = self._extract_decision_logic(response)
        if decision_logic:
            formatted += "### Strategic Decision Framework\n"
            formatted += decision_logic + "\n\n"
        
        # Extract validation mechanisms
        formatted += "### Validation Mechanisms\n"
        formatted += self._extract_validation_mechanisms(response)
        
        formatted += "\n### Strategic Implementation\n"
        formatted += "This logical framework provides the foundation for evidence-based strategic decisions.\n"
        
        return formatted
    
    def _extract_premises(self, text: str) -> List[str]:
        """Extract logical premises from text."""
        premises = []
        
        premise_patterns = [
            r'premise[s]?[:\s]*([^.!?\n]+)',
            r'assumption[s]?[:\s]*([^.!?\n]+)',
            r'given\s+that\s+([^.!?\n]+)',
            r'if\s+([^,]+)(?:,|then)'
        ]
        
        for pattern in premise_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                premise = match.group(1).strip()
                if len(premise) > 10:
                    premises.append(premise)
        
        return premises[:5]  # Limit to 5 premises
    
    def _extract_conclusions(self, text: str) -> List[str]:
        """Extract logical conclusions."""
        conclusions = []
        
        conclusion_patterns = [
            r'conclusion[s]?[:\s]*([^.!?\n]+)',
            r'therefore[,\s]*([^.!?\n]+)',
            r'thus[,\s]*([^.!?\n]+)',
            r'result[s]?\s+(?:in|is)\s+([^.!?\n]+)'
        ]
        
        for pattern in conclusion_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                conclusion = match.group(1).strip()
                if len(conclusion) > 10:
                    conclusions.append(conclusion)
        
        return conclusions[:4]  # Limit to 4 conclusions
    
    def _extract_logical_structure(self, text: str) -> str:
        """Extract logical structure description."""
        structure_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['structure', 'connection', 'relationship', 'flow']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    structure_lines.append(clean_line)
        
        return '\n'.join(structure_lines[:3]) if structure_lines else "Logical structure connects premises to strategic conclusions."
    
    def _extract_validity_evaluation(self, text: str) -> Dict[str, str]:
        """Extract validity evaluation results."""
        validity = {}
        
        aspects = ['deductive validity', 'logical consistency', 'inference quality', 'completeness']
        
        for aspect in aspects:
            pattern = rf'{aspect}[:\s]*([^.!?\n]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                validity[aspect.title()] = match.group(1).strip()
        
        return validity
    
    def _extract_logical_gaps(self, text: str) -> List[str]:
        """Extract identified logical gaps."""
        gaps = []
        
        gap_patterns = [
            r'gap[s]?[:\s]*([^.!?\n]+)',
            r'missing[:\s]*([^.!?\n]+)',
            r'incomplete[:\s]*([^.!?\n]+)',
            r'flaw[s]?[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in gap_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                gap = match.group(1).strip()
                if len(gap) > 10:
                    gaps.append(gap)
        
        return gaps[:4]  # Limit to 4 gaps
    
    def _extract_validity_recommendations(self, text: str) -> str:
        """Extract validity improvement recommendations."""
        rec_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['recommend', 'improve', 'strengthen', 'address']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    rec_lines.append(clean_line)
        
        return '\n'.join(rec_lines[:3]) if rec_lines else "Strengthen logical connections and address identified gaps."
    
    def _extract_truth_assessment(self, text: str) -> Dict[str, str]:
        """Extract premise truth assessments."""
        assessments = {}
        
        # Look for truth evaluation patterns
        truth_patterns = [
            r'premise\s+([^:]+):\s*([^.!?\n]+)',
            r'assumption\s+([^:]+):\s*([^.!?\n]+)'
        ]
        
        for pattern in truth_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                premise = match.group(1).strip()
                assessment = match.group(2).strip()
                if len(premise) < 50 and len(assessment) > 5:  # Reasonable lengths
                    assessments[premise] = assessment
        
        return assessments
    
    def _extract_evidence_analysis(self, text: str) -> str:
        """Extract evidence quality analysis."""
        evidence_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['evidence', 'support', 'data', 'proof']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    evidence_lines.append(clean_line)
        
        return '\n'.join(evidence_lines[:3]) if evidence_lines else "Evidence quality assessment for key premises."
    
    def _extract_risk_assessment(self, text: str) -> str:
        """Extract risk assessment for logical arguments."""
        risk_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['risk', 'wrong', 'fail', 'uncertain']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    risk_lines.append(clean_line)
        
        return '\n'.join(risk_lines[:3]) if risk_lines else "Assessment of risks if key premises are incorrect."
    
    def _extract_logical_framework(self, text: str) -> str:
        """Extract the constructed logical framework."""
        framework_patterns = [
            r'framework[:\s]*([^.!?]*(?:[.!?])?)',
            r'logical\s+structure[:\s]*([^.!?]*(?:[.!?])?)',
            r'reasoning\s+chain[:\s]*([^.!?]*(?:[.!?])?)'
        ]
        
        for pattern in framework_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(1)) > 30:
                return match.group(1).strip()
        
        return ""
    
    def _extract_decision_logic(self, text: str) -> str:
        """Extract decision-making logic."""
        decision_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['decision', 'choose', 'determine', 'logic']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    decision_lines.append(clean_line)
        
        return '\n'.join(decision_lines[:3]) if decision_lines else "Logical framework for strategic decision-making."
    
    def _extract_validation_mechanisms(self, text: str) -> str:
        """Extract validation mechanisms."""
        validation_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['validate', 'test', 'verify', 'check']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    validation_lines.append(clean_line)
        
        return '\n'.join(validation_lines[:3]) if validation_lines else "Mechanisms to test and validate strategic reasoning."
    
    def _default_structured_format(self, response: str) -> str:
        """Default structured format for Logic Agent."""
        return f"## Logical Analysis\n\n{response}"


class OpenStrategyAgentFormatter(BaseResponseFormatter):
    """Specialized formatter for Open Strategy Agent responses."""
    
    def __init__(self):
        super().__init__("open_strategy_agent")
        self.supported_formats.extend([
            ResponseFormat.BULLET_POINTS, 
            ResponseFormat.MARKDOWN,
            ResponseFormat.JSON
        ])
    
    def _format_structured(self, response: str, stage: str) -> str:
        """Format Open Strategy Agent response with implementation structure."""
        
        stage_templates = {
            "stakeholder_analysis": self._format_stakeholder_analysis,
            "process_design": self._format_process_design,
            "resource_planning": self._format_resource_planning,
            "implementation_roadmap": self._format_implementation_roadmap
        }
        
        formatter = stage_templates.get(stage, self._default_structured_format)
        return formatter(response)
    
    def _format_stakeholder_analysis(self, response: str) -> str:
        """Format stakeholder analysis response."""
        formatted = "## 👥 Stakeholder Analysis\n\n"
        
        # Extract stakeholder groups
        stakeholders = self._extract_stakeholder_groups(response)
        if stakeholders:
            formatted += "### Key Stakeholder Groups\n"
            for stakeholder in stakeholders:
                formatted += f"#### {stakeholder['group']}\n"
                formatted += f"- **Influence**: {stakeholder.get('influence', 'TBD')}\n"
                formatted += f"- **Interest**: {stakeholder.get('interest', 'TBD')}\n"
                formatted += f"- **Engagement**: {stakeholder.get('engagement', 'TBD')}\n\n"
        
        # Extract engagement strategy
        formatted += "### Engagement Strategy\n"
        formatted += self._extract_engagement_strategy(response)
        
        formatted += "\n### Next Steps\n"
        formatted += "Design implementation processes and workflows for stakeholder collaboration.\n"
        
        return formatted
    
    def _format_process_design(self, response: str) -> str:
        """Format process design response."""
        formatted = "## ⚙️ Implementation Process Design\n\n"
        
        # Extract processes
        processes = self._extract_processes(response)
        if processes:
            formatted += "### Key Implementation Processes\n"
            for process in processes:
                formatted += f"#### {process['name']}\n"
                formatted += f"{process['description']}\n\n"
        
        # Extract governance framework
        governance = self._extract_governance_framework(response)
        if governance:
            formatted += "### Governance Framework\n"
            formatted += governance + "\n\n"
        
        # Extract communication flows
        formatted += "### Communication Architecture\n"
        formatted += self._extract_communication_flows(response)
        
        return formatted
    
    def _format_resource_planning(self, response: str) -> str:
        """Format resource planning response."""
        formatted = "## 🛠️ Resource Planning\n\n"
        
        # Extract resource requirements
        resources = self._extract_resource_requirements(response)
        if resources:
            formatted += "### Resource Requirements\n"
            for category, requirements in resources.items():
                formatted += f"#### {category}\n"
                for req in requirements:
                    formatted += f"• {req}\n"
                formatted += "\n"
        
        # Extract capability gaps
        gaps = self._extract_capability_gaps(response)
        if gaps:
            formatted += "### Capability Development Needs\n"
            for gap in gaps:
                formatted += f"• {gap}\n"
            formatted += "\n"
        
        # Extract risk mitigation
        formatted += "### Resource Risk Mitigation\n"
        formatted += self._extract_resource_risks(response)
        
        return formatted
    
    def _format_implementation_roadmap(self, response: str) -> str:
        """Format implementation roadmap response."""
        formatted = "## 🛣️ Implementation Roadmap\n\n"
        
        # Extract phases
        phases = self._extract_implementation_phases(response)
        if phases:
            formatted += "### Implementation Phases\n"
            for i, phase in enumerate(phases, 1):
                formatted += f"#### Phase {i}: {phase['name']}\n"
                formatted += f"**Duration**: {phase.get('duration', 'TBD')}\n"
                formatted += f"**Objectives**: {phase.get('objectives', 'TBD')}\n"
                if phase.get('activities'):
                    formatted += "**Key Activities**:\n"
                    for activity in phase['activities']:
                        formatted += f"• {activity}\n"
                formatted += "\n"
        
        # Extract milestones
        milestones = self._extract_milestones(response)
        if milestones:
            formatted += "### Key Milestones\n"
            for milestone in milestones:
                formatted += f"• {milestone}\n"
            formatted += "\n"
        
        # Extract success metrics
        formatted += "### Success Metrics\n"
        formatted += self._extract_success_metrics(response)
        
        formatted += "\n### Strategic Implementation Ready\n"
        formatted += "This roadmap provides a practical path from strategic insight to strategic action.\n"
        
        return formatted
    
    def _extract_stakeholder_groups(self, text: str) -> List[Dict[str, str]]:
        """Extract stakeholder groups and their characteristics."""
        stakeholders = []
        
        # Look for stakeholder patterns
        stakeholder_patterns = [
            r'(\w+\s+stakeholder[s]?|\w+\s+group)[:\s]*([^.!?\n]+)',
            r'(internal|external)\s+([^:]+)[:\s]*([^.!?\n]+)',
            r'(employees?|customers?|partners?|investors?)[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in stakeholder_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                group_name = match.group(1).strip()
                description = match.group(2).strip() if len(match.groups()) > 2 else match.group(2).strip()
                
                stakeholders.append({
                    "group": group_name.title(),
                    "description": description,
                    "influence": self._extract_stakeholder_attribute(text, group_name, "influence"),
                    "interest": self._extract_stakeholder_attribute(text, group_name, "interest"),
                    "engagement": self._extract_stakeholder_attribute(text, group_name, "engagement")
                })
        
        return stakeholders[:5]  # Limit to 5 stakeholder groups
    
    def _extract_stakeholder_attribute(self, text: str, group: str, attribute: str) -> str:
        """Extract specific attribute for a stakeholder group."""
        pattern = rf'{group}.*?{attribute}[:\s]*([^.!?\n]+)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else "TBD"
    
    def _extract_engagement_strategy(self, text: str) -> str:
        """Extract stakeholder engagement strategy."""
        engagement_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['engagement', 'communicate', 'involve', 'collaborate']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    engagement_lines.append(clean_line)
        
        return '\n'.join(engagement_lines[:4]) if engagement_lines else "Develop collaborative engagement approach with key stakeholders."
    
    def _extract_processes(self, text: str) -> List[Dict[str, str]]:
        """Extract implementation processes."""
        processes = []
        
        process_patterns = [
            r'(\w+\s+process|\w+\s+workflow)[:\s]*([^.!?\n]+)',
            r'(governance|decision|communication|review)[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in process_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                processes.append({
                    "name": match.group(1).strip().title(),
                    "description": match.group(2).strip()
                })
        
        return processes[:4]  # Limit to 4 processes
    
    def _extract_governance_framework(self, text: str) -> str:
        """Extract governance framework."""
        governance_patterns = [
            r'governance[:\s]*([^.!?]*(?:[.!?])?)',
            r'decision[- ]making[:\s]*([^.!?]*(?:[.!?])?)',
            r'authority[:\s]*([^.!?]*(?:[.!?])?)'
        ]
        
        for pattern in governance_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(1)) > 20:
                return match.group(1).strip()
        
        return ""
    
    def _extract_communication_flows(self, text: str) -> str:
        """Extract communication architecture."""
        comm_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['communication', 'information', 'flow', 'report']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    comm_lines.append(clean_line)
        
        return '\n'.join(comm_lines[:3]) if comm_lines else "Design clear communication channels and information flows."
    
    def _extract_resource_requirements(self, text: str) -> Dict[str, List[str]]:
        """Extract resource requirements by category."""
        resources = {
            "Human Resources": [],
            "Financial Resources": [],
            "Technology Resources": [],
            "Knowledge Resources": []
        }
        
        categories = {
            "human": "Human Resources",
            "people": "Human Resources", 
            "financial": "Financial Resources",
            "budget": "Financial Resources",
            "technology": "Technology Resources",
            "tech": "Technology Resources",
            "knowledge": "Knowledge Resources",
            "information": "Knowledge Resources"
        }
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            for keyword, category in categories.items():
                if keyword in line.lower():
                    clean_line = re.sub(r'^[-•\*]\s*', '', line)
                    if len(clean_line) > 10:
                        resources[category].append(clean_line)
                        break
        
        # Filter out empty categories
        return {k: v for k, v in resources.items() if v}
    
    def _extract_capability_gaps(self, text: str) -> List[str]:
        """Extract capability development needs."""
        gaps = []
        
        gap_patterns = [
            r'gap[s]?[:\s]*([^.!?\n]+)',
            r'missing[:\s]*([^.!?\n]+)',
            r'need[s]?\s+to\s+develop[:\s]*([^.!?\n]+)',
            r'capability[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in gap_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                gap = match.group(1).strip()
                if len(gap) > 10:
                    gaps.append(gap)
        
        return gaps[:4]  # Limit to 4 gaps
    
    def _extract_resource_risks(self, text: str) -> str:
        """Extract resource-related risks."""
        risk_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['risk', 'constraint', 'limitation', 'bottleneck']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    risk_lines.append(clean_line)
        
        return '\n'.join(risk_lines[:3]) if risk_lines else "Identify and mitigate resource-related implementation risks."
    
    def _extract_implementation_phases(self, text: str) -> List[Dict[str, Any]]:
        """Extract implementation phases."""
        phases = []
        
        # Look for phase patterns
        phase_patterns = [
            r'phase\s+(\d+)[:\s]*([^.!?\n]+)',
            r'(phase\s+\w+)[:\s]*([^.!?\n]+)',
            r'(initial|core|full|final).*?phase[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in phase_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phase_name = match.group(1).strip() if match.group(1).isdigit() else match.group(1).strip()
                description = match.group(2).strip()
                
                phases.append({
                    "name": phase_name.title(),
                    "description": description,
                    "duration": self._extract_phase_duration(text, phase_name),
                    "objectives": self._extract_phase_objectives(text, phase_name),
                    "activities": self._extract_phase_activities(text, phase_name)
                })
        
        return phases[:4]  # Limit to 4 phases
    
    def _extract_phase_duration(self, text: str, phase_name: str) -> str:
        """Extract phase duration."""
        duration_pattern = rf'{phase_name}.*?(\d+\s+(?:weeks?|months?|days?))'
        match = re.search(duration_pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1) if match else "TBD"
    
    def _extract_phase_objectives(self, text: str, phase_name: str) -> str:
        """Extract phase objectives."""
        obj_pattern = rf'{phase_name}.*?objective[s]?[:\s]*([^.!?\n]+)'
        match = re.search(obj_pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else "TBD"
    
    def _extract_phase_activities(self, text: str, phase_name: str) -> List[str]:
        """Extract phase activities."""
        activities = []
        # This is a simplified extraction - in practice, you'd want more sophisticated parsing
        lines = text.split('\n')
        in_phase_section = False
        
        for line in lines:
            if phase_name.lower() in line.lower():
                in_phase_section = True
                continue
            elif in_phase_section and any(word in line.lower() for word in ['phase', '##', '###']):
                break
            elif in_phase_section and line.strip():
                clean_line = re.sub(r'^[-•\*]\s*', '', line.strip())
                if len(clean_line) > 10:
                    activities.append(clean_line)
        
        return activities[:3]  # Limit to 3 activities per phase
    
    def _extract_milestones(self, text: str) -> List[str]:
        """Extract key milestones."""
        milestones = []
        
        milestone_patterns = [
            r'milestone[s]?[:\s]*([^.!?\n]+)',
            r'key\s+marker[s]?[:\s]*([^.!?\n]+)',
            r'decision\s+gate[s]?[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in milestone_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                milestone = match.group(1).strip()
                if len(milestone) > 10:
                    milestones.append(milestone)
        
        return milestones[:5]  # Limit to 5 milestones
    
    def _extract_success_metrics(self, text: str) -> str:
        """Extract success metrics."""
        metrics_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['metric', 'measure', 'success', 'kpi', 'indicator']):
                clean_line = re.sub(r'^[-•\*]\s*', '', line)
                if len(clean_line) > 15:
                    metrics_lines.append(clean_line)
        
        return '\n'.join(metrics_lines[:4]) if metrics_lines else "Define specific metrics to measure implementation success."
    
    def _default_structured_format(self, response: str) -> str:
        """Default structured format for Open Strategy Agent."""
        return f"## Implementation Planning\n\n{response}"


# Factory functions for easy access
def get_response_formatter(agent_type: str) -> BaseResponseFormatter:
    """Get appropriate response formatter for agent type."""
    
    formatters = {
        "why_agent": WHYAgentFormatter,
        "analogy_agent": AnalogyAgentFormatter,
        "logic_agent": LogicAgentFormatter,
        "open_strategy_agent": OpenStrategyAgentFormatter
    }
    
    formatter_class = formatters.get(agent_type, BaseResponseFormatter)
    
    if formatter_class == BaseResponseFormatter:
        logger.warning(f"No specialized formatter for {agent_type}, using base formatter")
        return BaseResponseFormatter(agent_type)
    
    return formatter_class()


def format_agent_response(agent_type: str, raw_response: str, stage: str,
                         format_type: ResponseFormat = ResponseFormat.CONVERSATIONAL,
                         metadata: Optional[Dict[str, Any]] = None) -> FormattedResponse:
    """
    Convenience function to format an agent response.
    
    Args:
        agent_type: Type of agent (why_agent, analogy_agent, etc.)
        raw_response: Raw response text from agent
        stage: Current stage of agent methodology
        format_type: Desired output format
        metadata: Additional metadata
        
    Returns:
        FormattedResponse with formatted content
    """
    formatter = get_response_formatter(agent_type)
    return formatter.format_response(raw_response, stage, format_type, metadata)


# Export main classes and functions
__all__ = [
    "ResponseFormat",
    "FormattedResponse", 
    "BaseResponseFormatter",
    "WHYAgentFormatter",
    "AnalogyAgentFormatter", 
    "LogicAgentFormatter",
    "OpenStrategyAgentFormatter",
    "get_response_formatter",
    "format_agent_response"
]