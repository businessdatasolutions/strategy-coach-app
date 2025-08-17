"""
AFAS Software Business Case Parser and User Persona Simulation.

This module parses the AFAS Software business case and creates realistic
user responses for testing the strategic coaching system.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ..core.config import settings

logger = logging.getLogger(__name__)


class AFASPersona(BaseModel):
    """AFAS Software leadership persona for testing."""
    name: str = "Bas van der Veldt"
    role: str = "CEO & Visionary Founder"
    company: str = "AFAS Software"
    company_size: str = "€324.6M revenue, 720 employees"
    industry: str = "Enterprise Software (ERP/HRM)"
    
    # Core characteristics from business case
    leadership_style: str = "Accessible, trust-based, anti-hierarchical"
    core_mission: str = "Inspire better entrepreneurship"
    key_values: List[str] = ["Do", "Trust", "Crazy", "Family"]
    
    # Strategic context
    origin_story: str = "Founded in 1996 through management buyout, built culture-first company"
    proudest_moments: str = "Becoming #1 Best Workplace in Europe, 4-day workweek initiative"
    core_beliefs: str = "Trust and empowerment drive better business outcomes"
    
    # Business details
    target_market: str = "SMEs in Benelux region (10-50 employees)"
    competitive_advantage: str = "Culture as moat, integrated all-in-one solution"
    future_vision: str = "AFAS Focus platform - automating automation with natural language"


class AFASResponseGenerator:
    """Generates realistic responses based on AFAS persona and business case."""
    
    def __init__(self, business_case_path: Optional[str] = None):
        """Initialize with business case data."""
        self.persona = AFASPersona()
        self.business_case_path = business_case_path or "testing/business-cases/business-case-for-testing.md"
        self.business_case_content = self._load_business_case()
        
        # Initialize LLM for response generation
        self.llm = init_chat_model(
            f"{settings.llm_provider}:{settings.default_model}",
            temperature=0.8,  # Higher temperature for more varied responses
            max_tokens=300
        )
    
    def _load_business_case(self) -> str:
        """Load the AFAS Software business case content."""
        try:
            case_path = Path(self.business_case_path)
            if case_path.exists():
                return case_path.read_text(encoding='utf-8')
            else:
                logger.warning(f"Business case file not found: {case_path}")
                return ""
        except Exception as e:
            logger.error(f"Error loading business case: {e}")
            return ""
    
    def generate_origin_story_response(self, agent_question: str) -> str:
        """Generate response about AFAS origin story."""
        responses = [
            f"AFAS started in 1996 when my father Ton van der Veldt and Piet Mars did a management buyout from Getronics. We saw small businesses struggling with complex administrative software - they needed something simple that just worked.",
            
            f"We founded AFAS because we believed small businesses deserved enterprise-level software without the complexity. From day one, it was about eliminating the administrative burden so entrepreneurs could focus on what they do best.",
            
            f"The origin story is simple: we saw talented business owners wasting time on administrative tasks instead of growing their companies. We wanted to change that. AFAS means 'Applications For Administrative Solutions' - that's exactly what we set out to build."
        ]
        
        # Use LLM to create contextual response
        return self._generate_contextual_response(agent_question, responses)
    
    def generate_proud_moments_response(self, agent_question: str) -> str:
        """Generate response about proudest moments."""
        responses = [
            f"Our proudest moment was becoming the #1 Best Workplace in Europe. When you see 720 employees with only 1.9% absenteeism rate, you know you've created something special. Happy employees create happy customers - that's our secret.",
            
            f"I'm most proud of our four-day workweek decision. We're giving all 700 employees a 32-hour week for full pay starting 2025. This isn't just a perk - it's proof that our efficiency technology actually works. We practice what we preach.",
            
            f"What makes me proudest is our customer satisfaction score of 9.5 out of 10. When you process payslips for 3.7 million Dutch citizens and they trust you with that responsibility, you know you're making a real impact."
        ]
        
        return self._generate_contextual_response(agent_question, responses)
    
    def generate_beliefs_response(self, agent_question: str) -> str:
        """Generate response about core beliefs."""
        responses = [
            f"I believe every entrepreneur deserves access to enterprise-level technology without the complexity. Small businesses shouldn't have to choose between powerful tools and simplicity - they should have both.",
            
            f"Our core belief is that trust creates better business outcomes than control. When you trust people completely, they exceed your expectations. That's why we have one rule: 'Use common sense in the best interest of AFAS.'",
            
            f"I believe business should be built on love as a vital force. Not soft love, but tough love - caring deeply about people's success and happiness. Happy people create better products and serve customers better."
        ]
        
        return self._generate_contextual_response(agent_question, responses)
    
    def generate_values_response(self, agent_question: str) -> str:
        """Generate response about actionable values."""
        responses = [
            f"Our values are verbs, not nouns. 'Do' means take action and make things happen. 'Trust' means give people autonomy and responsibility. 'Crazy' means challenge conventional thinking. 'Family' means create genuine community and support.",
            
            f"We don't just say 'innovation' - we 'challenge every assumption.' We don't just say 'integrity' - we 'communicate with radical transparency.' Our values guide daily behavior, not just company posters.",
            
            f"Every value must be actionable. 'Think differently about work-life balance' led to our four-day week. 'Build with love and trust' created our 1.9% absenteeism rate. Values create results when they drive real behavior."
        ]
        
        return self._generate_contextual_response(agent_question, responses)
    
    def generate_confirmation_response(self, why_statement: str) -> str:
        """Generate response confirming or refining the WHY statement."""
        confirmations = [
            f"Yes, that captures it perfectly! Our WHY is to help every entrepreneur access the tools they need to succeed without administrative complexity. That's exactly why we exist.",
            
            f"That resonates deeply. We do exist to eliminate administrative burden so entrepreneurs can focus on what matters most - building great businesses and serving customers.",
            
            f"Absolutely. When I see our software processing 3.7 million payslips, I know we're living that purpose. We're not just selling software - we're enabling entrepreneurial success."
        ]
        
        return self._generate_contextual_response(why_statement, confirmations)
    
    def _generate_contextual_response(self, agent_question: str, base_responses: List[str]) -> str:
        """Use LLM to generate contextual response based on agent question."""
        try:
            # Create context-aware prompt
            system_prompt = f"""You are {self.persona.name}, {self.persona.role} of {self.persona.company}.

Company Context: {self.persona.company} is a {self.persona.company_size} {self.persona.industry} company.
Leadership Style: {self.persona.leadership_style}
Core Mission: {self.persona.core_mission}

Respond authentically as this persona, incorporating the business context naturally."""

            user_prompt = f"""The strategic coach asked: "{agent_question}"

Choose the most appropriate response style from these examples:
{chr(10).join([f"- {resp}" for resp in base_responses])}

Generate a natural, authentic response that fits this specific question while staying true to the AFAS persona and context."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"LLM response generation failed: {e}")
            # Fallback to first base response
            return base_responses[0] if base_responses else "I need to think about that more."
    
    def get_persona_info(self) -> Dict:
        """Get structured persona information."""
        return {
            "name": self.persona.name,
            "role": self.persona.role,
            "company": self.persona.company,
            "industry": self.persona.industry,
            "mission": self.persona.core_mission,
            "key_facts": [
                f"Revenue: €324.6M (2023)",
                f"Employees: 720 with 1.9% absenteeism",
                f"Customers: 12,347+ organizations", 
                f"Market: #1 Best Workplace in Europe",
                f"Innovation: 4-day workweek starting 2025"
            ]
        }


def create_afas_response_generator() -> AFASResponseGenerator:
    """Factory function to create AFAS response generator."""
    return AFASResponseGenerator()