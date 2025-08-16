"""
Business Case Framework for Testing Agent
Provides comprehensive business context for realistic user journey simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import json
from pathlib import Path


class CompanyStage(Enum):
    """Company development stages."""
    STARTUP = "startup"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    GROWTH = "growth"
    MATURE = "mature"
    TRANSFORMATION = "transformation"


class Industry(Enum):
    """Industry categories."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    CONSULTING = "consulting"
    FINANCE = "finance"
    EDUCATION = "education"
    SOFTWARE = "software"
    ENTERPRISE_SOFTWARE = "enterprise_software"


class PersonaType(Enum):
    """Business leader persona types."""
    ANALYTICAL_CEO = "analytical_ceo"
    VISIONARY_FOUNDER = "visionary_founder" 
    PRAGMATIC_DIRECTOR = "pragmatic_director"
    TECHNICAL_CTO = "technical_cto"
    OPERATIONS_COO = "operations_coo"


@dataclass
class CompanyProfile:
    """Basic company information."""
    name: str
    industry: Industry
    stage: CompanyStage
    size: str  # e.g., "45 employees", "500-1000"
    founded: str  # Year or range
    revenue: str  # e.g., "$2.1M ARR", "$50M annual"
    location: str = "Unknown"
    funding: Optional[str] = None


@dataclass
class StrategicContext:
    """Strategic situation and challenges."""
    mission: str
    current_challenges: List[str]
    market_position: str
    key_stakeholders: List[str]
    competitive_pressures: List[str] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)


@dataclass
class StrategicGoals:
    """Short and long-term strategic objectives."""
    short_term: List[str]
    long_term: List[str]
    strategic_questions: List[str]
    success_metrics: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class BackgroundKnowledge:
    """Deeper context and beliefs."""
    founder_story: str
    core_beliefs: List[str]
    company_culture: str
    competitive_landscape: str
    unique_advantages: List[str] = field(default_factory=list)
    past_failures: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class PersonaCharacteristics:
    """Persona-specific traits and behaviors."""
    communication_style: str  # "analytical", "passionate", "pragmatic"
    decision_making: str  # "data-driven", "intuitive", "collaborative"
    information_sharing: str  # "detailed", "high-level", "selective"
    questioning_tendency: str  # "challenging", "supportive", "practical"
    uncertainty_handling: str  # "comfortable", "seeks_validation", "wants_options"


@dataclass
class BusinessCase:
    """Complete business case for testing agent."""
    company_profile: CompanyProfile
    strategic_context: StrategicContext
    strategic_goals: StrategicGoals
    background_knowledge: BackgroundKnowledge
    persona_type: PersonaType
    persona_characteristics: PersonaCharacteristics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "company_profile": {
                "name": self.company_profile.name,
                "industry": self.company_profile.industry.value,
                "stage": self.company_profile.stage.value,
                "size": self.company_profile.size,
                "founded": self.company_profile.founded,
                "revenue": self.company_profile.revenue,
                "location": self.company_profile.location,
                "funding": self.company_profile.funding
            },
            "strategic_context": {
                "mission": self.strategic_context.mission,
                "current_challenges": self.strategic_context.current_challenges,
                "market_position": self.strategic_context.market_position,
                "key_stakeholders": self.strategic_context.key_stakeholders,
                "competitive_pressures": self.strategic_context.competitive_pressures,
                "recent_events": self.strategic_context.recent_events
            },
            "strategic_goals": {
                "short_term": self.strategic_goals.short_term,
                "long_term": self.strategic_goals.long_term,
                "strategic_questions": self.strategic_goals.strategic_questions,
                "success_metrics": self.strategic_goals.success_metrics,
                "constraints": self.strategic_goals.constraints
            },
            "background_knowledge": {
                "founder_story": self.background_knowledge.founder_story,
                "core_beliefs": self.background_knowledge.core_beliefs,
                "company_culture": self.background_knowledge.company_culture,
                "competitive_landscape": self.background_knowledge.competitive_landscape,
                "unique_advantages": self.background_knowledge.unique_advantages,
                "past_failures": self.background_knowledge.past_failures,
                "lessons_learned": self.background_knowledge.lessons_learned
            },
            "persona_type": self.persona_type.value,
            "persona_characteristics": {
                "communication_style": self.persona_characteristics.communication_style,
                "decision_making": self.persona_characteristics.decision_making,
                "information_sharing": self.persona_characteristics.information_sharing,
                "questioning_tendency": self.persona_characteristics.questioning_tendency,
                "uncertainty_handling": self.persona_characteristics.uncertainty_handling
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessCase':
        """Create BusinessCase from dictionary."""
        return cls(
            company_profile=CompanyProfile(
                name=data["company_profile"]["name"],
                industry=Industry(data["company_profile"]["industry"]),
                stage=CompanyStage(data["company_profile"]["stage"]),
                size=data["company_profile"]["size"],
                founded=data["company_profile"]["founded"],
                revenue=data["company_profile"]["revenue"],
                location=data["company_profile"].get("location", "Unknown"),
                funding=data["company_profile"].get("funding")
            ),
            strategic_context=StrategicContext(**data["strategic_context"]),
            strategic_goals=StrategicGoals(**data["strategic_goals"]),
            background_knowledge=BackgroundKnowledge(**data["background_knowledge"]),
            persona_type=PersonaType(data["persona_type"]),
            persona_characteristics=PersonaCharacteristics(**data["persona_characteristics"])
        )


class BusinessCaseLibrary:
    """Library of predefined business cases for testing."""
    
    def __init__(self):
        self.cases = {}
        self._initialize_default_cases()
    
    def _initialize_default_cases(self):
        """Initialize library with default business cases."""
        
        # AFAS Software - Mature Enterprise Software Company (based on comprehensive case study)
        self.cases["afas_software_enterprise"] = BusinessCase(
            company_profile=CompanyProfile(
                name="AFAS Software",
                industry=Industry.ENTERPRISE_SOFTWARE,
                stage=CompanyStage.MATURE,
                size="720 employees",
                founded="1996",
                revenue="€324.6 million",
                location="Leusden, Netherlands",
                funding="Private, family-owned"
            ),
            strategic_context=StrategicContext(
                mission="Inspire better entrepreneurship through integrated business software",
                current_challenges=[
                    "Geographic concentration risk (82% Netherlands market)",
                    "International expansion strategy and execution",
                    "Maintaining culture while scaling globally", 
                    "Competition from global giants (SAP, Microsoft, Oracle)",
                    "API complexity limiting third-party ecosystem growth",
                    "Product rigidity vs customization demands"
                ],
                market_position="Market leader in Benelux SME ERP/HRM space",
                key_stakeholders=["Founding families", "720 employees", "12,347+ customers", "AFAS Foundation"],
                competitive_pressures=[
                    "Microsoft Dynamics targeting SME market",
                    "Open-source solutions like Odoo gaining traction",
                    "SAP and Oracle scaling down for SMEs",
                    "Global economic headwinds affecting SME spending"
                ],
                recent_events=[
                    "Four-day, 32-hour workweek implementation (2025)",
                    "AFAS Focus 'automating automation' platform development",
                    "#1 Best Workplace in Europe recognition",
                    "€10 million foundation commitment for 2025"
                ]
            ),
            strategic_goals=StrategicGoals(
                short_term=[
                    "Successfully implement four-day workweek without productivity loss",
                    "Launch AFAS Focus next-generation platform",
                    "Expand international presence strategically",
                    "Maintain #1 Best Workplace status"
                ],
                long_term=[
                    "Become leading European enterprise software provider",
                    "Pioneer future of work with culture-first approach",
                    "Revolutionize software development with 'automating automation'",
                    "Scale social impact through expanded foundation work"
                ],
                strategic_questions=[
                    "How do we replicate our success beyond the Netherlands?",
                    "Can we maintain our unique culture during international expansion?",
                    "How do we balance innovation with our proven integrated model?",
                    "What's our strategy for competing with global software giants?"
                ],
                success_metrics=[
                    "Revenue growth while maintaining 30%+ profit margins",
                    "Employee satisfaction and 1.9% absenteeism rate maintenance",
                    "Customer satisfaction 9.5/10 score preservation",
                    "Successful international market penetration"
                ],
                constraints=[
                    "Family business decision-making processes",
                    "Commitment to employee welfare over pure profit",
                    "Geographic concentration in Netherlands",
                    "Integrated product architecture limiting flexibility"
                ]
            ),
            background_knowledge=BackgroundKnowledge(
                founder_story="1996 management buy-out from Getronics by Piet Mars & Ton van der Veldt, built family business focused on trust and employee empowerment",
                core_beliefs=[
                    "Culture is our ultimate competitive advantage",
                    "Trust and autonomy drive superior performance",
                    "Business success should benefit all stakeholders",
                    "Integration and simplicity over complexity",
                    "Social responsibility is core business function"
                ],
                company_culture="Trust-based, family values, employee empowerment, 'Do, Trust, Crazy, Family'",
                competitive_landscape="Competing against global giants (SAP, Microsoft, Oracle) and open-source solutions (Odoo) in SME market",
                unique_advantages=[
                    "Unparalleled employee culture and satisfaction",
                    "Deep Benelux market expertise and localization",
                    "Integrated, simple all-in-one product solution",
                    "Family business stability and long-term thinking",
                    "Authentic social responsibility and sustainability"
                ],
                past_failures=[
                    "API complexity limiting developer ecosystem",
                    "Product rigidity challenges in custom requirements"
                ],
                lessons_learned=[
                    "Culture drives business results more than features",
                    "Trust-based management scales better than control",
                    "Focused market strategy beats broad global approach",
                    "Employee happiness directly correlates with customer satisfaction"
                ]
            ),
            persona_type=PersonaType.VISIONARY_FOUNDER,
            persona_characteristics=PersonaCharacteristics(
                communication_style="accessible",
                decision_making="values-driven",
                information_sharing="transparent",
                questioning_tendency="empowering",
                uncertainty_handling="seeks_collective_wisdom"
            )
        )
        
        # Tech Startup - Anti-Consultancy (based on real user conversation)
        self.cases["anti_consultancy_ai"] = BusinessCase(
            company_profile=CompanyProfile(
                name="AI Innovation Enablers",
                industry=Industry.CONSULTING,
                stage=CompanyStage.STARTUP,
                size="5-10 employees",
                founded="2024",
                revenue="Pre-revenue",
                location="University-affiliated"
            ),
            strategic_context=StrategicContext(
                mission="Help SMEs break free from endless AI pilots and achieve tangible value",
                current_challenges=[
                    "Traditional consultants leave SMEs stuck in pilot purgatory",
                    "Managers frustrated with endless projects promising 'phase 2'",
                    "Gap between AI ambitions and actual implementation",
                    "SMEs lose hope and blame others for lack of progress"
                ],
                market_position="Anti-consultancy challenging traditional approaches",
                key_stakeholders=["University researchers", "SME managers", "Business professionals"],
                competitive_pressures=["Traditional consulting firms", "Large tech consultancies"],
                recent_events=["Conducting workshops on AI Strategy", "Research on practical AI implementation"]
            ),
            strategic_goals=StrategicGoals(
                short_term=["Develop proven AI implementation methodology", "Build initial SME client base"],
                long_term=["Transform consulting industry approach to AI", "Scale growth mindset globally"],
                strategic_questions=[
                    "How do we prove tangible value vs promises?",
                    "What makes our approach truly different?",
                    "How do we scale confidence and growth mindset?"
                ],
                success_metrics=["Actual AI products deployed", "SME transformation stories", "Reduced pilot-to-production time"],
                constraints=["University time commitments", "Limited initial resources"]
            ),
            background_knowledge=BackgroundKnowledge(
                founder_story="University instructor/researcher frustrated by gap between AI potential and SME reality",
                core_beliefs=[
                    "Everyone can learn anything with right mindset",
                    "Tangible value over theoretical promises",
                    "Growth mindset can be scaled organizationally",
                    "Technology should restore hope and agency"
                ],
                company_culture="Teaching-focused, research-backed, results-oriented",
                competitive_landscape="Traditional consultancies promising but not delivering",
                unique_advantages=[
                    "Deep technical AI/Data Science expertise",
                    "Business management background", 
                    "Daily teaching and knowledge transfer practice",
                    "University credibility and research foundation"
                ],
                lessons_learned=["Endless pilots frustrate managers", "Growth mindset is key to transformation"]
            ),
            persona_type=PersonaType.VISIONARY_FOUNDER,
            persona_characteristics=PersonaCharacteristics(
                communication_style="passionate",
                decision_making="mission-driven",
                information_sharing="detailed",
                questioning_tendency="philosophical", 
                uncertainty_handling="seeks_deeper_meaning"
            )
        )
        
        # B2B SaaS Growth Stage
        self.cases["saas_scaling_growth"] = BusinessCase(
            company_profile=CompanyProfile(
                name="DataFlow Analytics",
                industry=Industry.SOFTWARE,
                stage=CompanyStage.SERIES_B,
                size="120 employees",
                founded="2020",
                revenue="$15M ARR",
                funding="$25M Series B"
            ),
            strategic_context=StrategicContext(
                mission="Democratize data analytics for mid-market companies",
                current_challenges=[
                    "Customer acquisition costs rising 40% year-over-year",
                    "Feature prioritization conflicts between enterprise and SMB needs",
                    "Engineering team scaling difficulties",
                    "Competitive pressure from Tableau, Power BI giants"
                ],
                market_position="Fast-growing challenger in business intelligence space",
                key_stakeholders=["Founder/CEO", "VP Engineering", "Head of Sales", "Series B investors"]
            ),
            strategic_goals=StrategicGoals(
                short_term=["Reach $30M ARR", "Launch enterprise tier", "Expand to 200 employees"],
                long_term=["IPO readiness", "Market leadership in mid-market BI", "International expansion"],
                strategic_questions=[
                    "How do we scale without losing product focus?",
                    "What's our sustainable competitive advantage vs giants?",
                    "How do we balance growth with profitability?"
                ]
            ),
            background_knowledge=BackgroundKnowledge(
                founder_story="Former data analyst frustrated by complex, expensive BI tools for mid-market",
                core_beliefs=[
                    "Data insights should be accessible to all companies",
                    "Simplicity beats feature bloat",
                    "Customer success drives everything"
                ],
                company_culture="Data-driven, customer-obsessed, rapid iteration",
                competitive_landscape="Competing with Tableau, Power BI, Looker in crowded market"
            ),
            persona_type=PersonaType.ANALYTICAL_CEO,
            persona_characteristics=PersonaCharacteristics(
                communication_style="analytical",
                decision_making="data-driven",
                information_sharing="detailed",
                questioning_tendency="challenging",
                uncertainty_handling="seeks_validation"
            )
        )
        
        # Healthcare Technology Company
        self.cases["healthcare_compliance"] = BusinessCase(
            company_profile=CompanyProfile(
                name="MedConnect Solutions",
                industry=Industry.HEALTHCARE,
                stage=CompanyStage.GROWTH,
                size="85 employees", 
                founded="2019",
                revenue="$8M annual",
                funding="Bootstrapped"
            ),
            strategic_context=StrategicContext(
                mission="Improve patient outcomes through secure healthcare technology",
                current_challenges=[
                    "HIPAA compliance complexity increasing with scale",
                    "Healthcare sales cycles extremely long (12-18 months)",
                    "Integration challenges with legacy hospital systems",
                    "Regulatory changes affecting product roadmap"
                ],
                market_position="Emerging player in healthcare IT integration",
                key_stakeholders=["Founder/CEO", "Chief Medical Officer", "Compliance Officer", "Hospital CIOs"]
            ),
            strategic_goals=StrategicGoals(
                short_term=["Achieve SOC 2 Type II certification", "Expand to 5 major health systems"],
                long_term=["Become leading patient data platform", "National healthcare network"],
                strategic_questions=[
                    "How do we scale while maintaining strict compliance?",
                    "What's our strategy for competing with Epic and Cerner?",
                    "How do we accelerate healthcare sales cycles?"
                ]
            ),
            background_knowledge=BackgroundKnowledge(
                founder_story="Former hospital administrator frustrated by siloed patient data systems",
                core_beliefs=[
                    "Patient data should be seamlessly accessible to authorized providers",
                    "Healthcare technology should reduce physician burden",
                    "Compliance is a competitive advantage, not just requirement"
                ],
                company_culture="Mission-driven, compliance-first, patient-focused",
                competitive_landscape="Competing with Epic, Cerner, athenahealth in entrenched market"
            ),
            persona_type=PersonaType.PRAGMATIC_DIRECTOR,
            persona_characteristics=PersonaCharacteristics(
                communication_style="cautious",
                decision_making="risk-aware",
                information_sharing="selective",
                questioning_tendency="practical",
                uncertainty_handling="wants_clear_options"
            )
        )
        
        # B2B SaaS Growth Stage
        self.cases["saas_scaling"] = BusinessCase(
            company_profile=CompanyProfile(
                name="CloudFlow Solutions",
                industry=Industry.TECHNOLOGY,
                stage=CompanyStage.SERIES_A,
                size="45 employees",
                founded="2022",
                revenue="$2.1M ARR",
                funding="$8M Series A"
            ),
            strategic_context=StrategicContext(
                mission="Democratize workflow automation for small businesses",
                current_challenges=[
                    "Increasing customer acquisition costs",
                    "Feature prioritization confusion", 
                    "Team scaling difficulties",
                    "Competitive pressure from larger players"
                ],
                market_position="Emerging player in crowded automation market",
                key_stakeholders=["Founder/CEO", "CTO", "Head of Sales", "Lead Designer"]
            ),
            strategic_goals=StrategicGoals(
                short_term=["Reach $5M ARR", "Expand team to 75", "Launch enterprise tier"],
                long_term=["Market leadership in SMB automation", "IPO readiness", "Global expansion"],
                strategic_questions=[
                    "How do we differentiate from established competitors?",
                    "What's our sustainable competitive advantage?",
                    "How do we balance growth with profitability?"
                ]
            ),
            background_knowledge=BackgroundKnowledge(
                founder_story="Former small business owner frustrated by complex automation tools",
                core_beliefs=[
                    "Small businesses deserve enterprise-level tools",
                    "Technology should empower, not complicate",
                    "Customer success drives everything"
                ],
                company_culture="Remote-first, customer-obsessed, innovation-driven",
                competitive_landscape="Zapier, Microsoft Power Automate, Nintex"
            ),
            persona_type=PersonaType.ANALYTICAL_CEO,
            persona_characteristics=PersonaCharacteristics(
                communication_style="analytical",
                decision_making="data-driven",
                information_sharing="structured",
                questioning_tendency="challenging",
                uncertainty_handling="seeks_validation"
            )
        )
    
    def get_case(self, case_name: str) -> Optional[BusinessCase]:
        """Retrieve a business case by name."""
        return self.cases.get(case_name)
    
    def list_cases(self) -> List[str]:
        """List available business case names."""
        return list(self.cases.keys())
    
    def add_case(self, name: str, business_case: BusinessCase):
        """Add a new business case to the library."""
        self.cases[name] = business_case
    
    def save_library(self, filepath: Path):
        """Save the entire library to JSON file."""
        library_data = {
            name: case.to_dict() 
            for name, case in self.cases.items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(library_data, f, indent=2)
    
    def load_library(self, filepath: Path):
        """Load library from JSON file."""
        with open(filepath, 'r') as f:
            library_data = json.load(f)
        
        for name, case_data in library_data.items():
            self.cases[name] = BusinessCase.from_dict(case_data)


# Predefined business case library
business_case_library = BusinessCaseLibrary()