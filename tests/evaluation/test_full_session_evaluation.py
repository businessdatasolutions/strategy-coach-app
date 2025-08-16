"""
Comprehensive End-to-End Evaluation Suite for AI Strategic Co-pilot
====================================================================
This test suite simulates full coaching sessions and evaluates:
1. Complete strategy map generation
2. Agent routing accuracy
3. Conversation quality and coherence
4. UI interaction flow
5. Performance metrics

Generates detailed HTML reports with screenshots and metrics.
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import os

# Evaluation frameworks
from deepeval import evaluate, assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    GEval
)
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset

# Playwright for UI testing
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Reporting
import pytest_html
from jinja2 import Template

# Application imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.api.main import app
from src.models.state import AgentState, StrategyMapState
from src.agents.orchestrator import StrategyCoachOrchestrator
from src.utils.llm_client import LLMClientWrapper

# Test configuration
API_BASE_URL = "http://localhost:8000"
WEB_UI_URL = "http://localhost:8081"
SCREENSHOTS_DIR = Path("tests/evaluation/screenshots")
REPORTS_DIR = Path("tests/evaluation/reports")
TIMEOUT_MS = 60000  # 60 seconds for LLM responses

# Ensure directories exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class TestScenario:
    """Defines a complete test scenario for evaluation"""
    name: str
    description: str
    initial_message: str
    expected_agents: List[str]  # Expected agent routing sequence
    expected_topics: List[str]  # Key topics that should be covered
    conversation_turns: int = 10  # Number of conversation turns
    success_criteria: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Stores evaluation results for a test scenario"""
    scenario: TestScenario
    session_id: str
    strategy_map: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    agent_sequence: List[str]
    screenshots: List[str]
    metrics: Dict[str, float]
    timestamp: datetime
    duration_seconds: float
    passed: bool
    failure_reasons: List[str] = field(default_factory=list)


class StrategyCoachEvaluator:
    """Main evaluation orchestrator for the Strategy Coach application"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.results: List[EvaluationResult] = []
        
    async def setup(self):
        """Initialize browser and test environment"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        self.page = await self.context.new_page()
        
    async def teardown(self):
        """Cleanup browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def run_scenario(self, scenario: TestScenario) -> EvaluationResult:
        """Execute a complete test scenario"""
        print(f"\n🔬 Running scenario: {scenario.name}")
        start_time = time.time()
        
        # Navigate to web UI
        await self.page.goto(WEB_UI_URL, wait_until='networkidle')
        
        # Take initial screenshot
        screenshots = []
        initial_screenshot = await self.capture_screenshot(f"{scenario.name}_initial")
        screenshots.append(initial_screenshot)
        
        # Start new conversation
        await self.page.click('button:has-text("Start New Conversation")')
        await self.page.wait_for_selector('#session-info', state='visible')
        
        # Extract session ID
        session_element = await self.page.query_selector('#session-id')
        session_id = await session_element.inner_text() if session_element else "unknown"
        
        # Initialize tracking variables
        conversation_history = []
        agent_sequence = []
        
        # Send initial message
        await self.send_message(scenario.initial_message)
        conversation_history.append({
            "role": "user",
            "content": scenario.initial_message
        })
        
        # Wait for and capture AI response
        ai_response = await self.wait_for_ai_response()
        conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Detect which agent responded
        detected_agent = await self.detect_active_agent(ai_response)
        agent_sequence.append(detected_agent)
        
        # Take screenshot after first response
        screenshot = await self.capture_screenshot(f"{scenario.name}_turn_1")
        screenshots.append(screenshot)
        
        # Continue conversation for specified turns
        for turn in range(2, scenario.conversation_turns + 1):
            # Generate contextual follow-up message
            follow_up = await self.generate_follow_up_message(
                conversation_history, 
                scenario.expected_topics
            )
            
            await self.send_message(follow_up)
            conversation_history.append({
                "role": "user",
                "content": follow_up
            })
            
            # Wait for AI response
            ai_response = await self.wait_for_ai_response()
            conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Detect active agent
            detected_agent = await self.detect_active_agent(ai_response)
            agent_sequence.append(detected_agent)
            
            # Take screenshot every 3 turns
            if turn % 3 == 0:
                screenshot = await self.capture_screenshot(f"{scenario.name}_turn_{turn}")
                screenshots.append(screenshot)
        
        # Export strategy map
        strategy_map = await self.export_strategy_map(session_id)
        
        # Take final screenshot of strategy map
        await self.page.click('button:has-text("View Strategy Map")')
        await self.page.wait_for_selector('#strategy-map-view', state='visible')
        final_screenshot = await self.capture_screenshot(f"{scenario.name}_final_map")
        screenshots.append(final_screenshot)
        
        # Calculate metrics
        duration = time.time() - start_time
        metrics = await self.calculate_metrics(
            scenario,
            conversation_history,
            strategy_map,
            agent_sequence
        )
        
        # Determine pass/fail
        passed, failure_reasons = self.evaluate_success_criteria(
            scenario,
            metrics,
            strategy_map,
            agent_sequence
        )
        
        # Create result
        result = EvaluationResult(
            scenario=scenario,
            session_id=session_id,
            strategy_map=strategy_map,
            conversation_history=conversation_history,
            agent_sequence=agent_sequence,
            screenshots=screenshots,
            metrics=metrics,
            timestamp=datetime.now(),
            duration_seconds=duration,
            passed=passed,
            failure_reasons=failure_reasons
        )
        
        self.results.append(result)
        return result
    
    async def send_message(self, message: str):
        """Send a message through the UI"""
        input_field = await self.page.query_selector('#user-input')
        await input_field.fill(message)
        await self.page.press('#user-input', 'Enter')
    
    async def wait_for_ai_response(self) -> str:
        """Wait for and extract AI response"""
        # Wait for response to appear
        await self.page.wait_for_selector(
            '.message.assistant:last-child',
            state='visible',
            timeout=TIMEOUT_MS
        )
        
        # Extract response text
        response_element = await self.page.query_selector('.message.assistant:last-child')
        response_text = await response_element.inner_text()
        return response_text
    
    async def detect_active_agent(self, response: str) -> str:
        """Detect which agent generated the response"""
        agent_indicators = {
            "WHY": ["purpose", "why", "mission", "values", "golden circle"],
            "Analogy": ["similar to", "like", "compared to", "analogy", "pattern"],
            "Logic": ["therefore", "because", "if-then", "conclusion", "premise"],
            "Open Strategy": ["stakeholder", "implementation", "timeline", "resources"]
        }
        
        for agent, keywords in agent_indicators.items():
            if any(keyword.lower() in response.lower() for keyword in keywords):
                return agent
        
        return "Router"  # Default if no specific agent detected
    
    async def generate_follow_up_message(
        self, 
        history: List[Dict[str, str]], 
        topics: List[str]
    ) -> str:
        """Generate contextual follow-up message"""
        # Simple implementation - in production, use LLM for better generation
        follow_ups = [
            "Can you elaborate on that strategic point?",
            "How would we implement this in practice?",
            "What are the potential challenges?",
            "Who are the key stakeholders?",
            "What similar companies have done this?",
            "What's the logical framework here?",
            "How does this align with our mission?"
        ]
        
        # Pick follow-up based on conversation length
        index = (len(history) // 2) % len(follow_ups)
        return follow_ups[index]
    
    async def export_strategy_map(self, session_id: str) -> Dict[str, Any]:
        """Export strategy map via API"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/conversation/{session_id}/export") as response:
                return await response.json()
    
    async def capture_screenshot(self, name: str) -> str:
        """Capture screenshot and return path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        await self.page.screenshot(path=str(filepath), full_page=True)
        return str(filepath)
    
    async def calculate_metrics(
        self,
        scenario: TestScenario,
        history: List[Dict[str, str]],
        strategy_map: Dict[str, Any],
        agent_sequence: List[str]
    ) -> Dict[str, float]:
        """Calculate evaluation metrics using DeepEval"""
        metrics = {}
        
        # Create test cases for DeepEval
        test_cases = []
        for i in range(0, len(history)-1, 2):
            if i+1 < len(history):
                test_case = LLMTestCase(
                    input=history[i]["content"],
                    actual_output=history[i+1]["content"],
                    context=[json.dumps(strategy_map)]
                )
                test_cases.append(test_case)
        
        # Initialize DeepEval metrics
        relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
        faithfulness_metric = FaithfulnessMetric(threshold=0.7)
        
        # Custom metric for strategic quality
        strategic_quality = GEval(
            name="Strategic Quality",
            criteria="Evaluate if the response provides valuable strategic insights relevant to business planning",
            threshold=0.7
        )
        
        # Run evaluation
        if test_cases:
            eval_results = evaluate(
                test_cases,
                [relevancy_metric, faithfulness_metric, strategic_quality],
                run_async=True
            )
            
            # Extract scores
            metrics['answer_relevancy'] = eval_results.aggregate_scores.get('answer_relevancy', 0)
            metrics['faithfulness'] = eval_results.aggregate_scores.get('faithfulness', 0)
            metrics['strategic_quality'] = eval_results.aggregate_scores.get('strategic_quality', 0)
        
        # Calculate custom metrics
        metrics['strategy_map_completeness'] = self.calculate_completeness(strategy_map)
        metrics['agent_routing_accuracy'] = self.calculate_routing_accuracy(
            scenario.expected_agents,
            agent_sequence
        )
        metrics['conversation_coherence'] = self.calculate_coherence(history)
        
        return metrics
    
    def calculate_completeness(self, strategy_map: Dict[str, Any]) -> float:
        """Calculate strategy map completeness score"""
        total_fields = 0
        filled_fields = 0
        
        def count_fields(obj, prefix=""):
            nonlocal total_fields, filled_fields
            if isinstance(obj, dict):
                for key, value in obj.items():
                    total_fields += 1
                    if value and value != "" and value != {}:
                        filled_fields += 1
                    if isinstance(value, dict):
                        count_fields(value, f"{prefix}.{key}")
        
        count_fields(strategy_map)
        return filled_fields / total_fields if total_fields > 0 else 0
    
    def calculate_routing_accuracy(
        self, 
        expected: List[str], 
        actual: List[str]
    ) -> float:
        """Calculate agent routing accuracy"""
        if not expected or not actual:
            return 0
        
        matches = sum(1 for e, a in zip(expected, actual) if e.lower() in a.lower())
        return matches / len(expected)
    
    def calculate_coherence(self, history: List[Dict[str, str]]) -> float:
        """Calculate conversation coherence score"""
        # Simplified coherence check - in production, use semantic similarity
        if len(history) < 2:
            return 1.0
        
        coherence_score = 0
        pairs = 0
        
        for i in range(0, len(history)-1, 2):
            if i+1 < len(history):
                user_msg = history[i]["content"]
                ai_msg = history[i+1]["content"]
                
                # Check if AI response addresses user message
                user_words = set(user_msg.lower().split())
                ai_words = set(ai_msg.lower().split())
                overlap = len(user_words & ai_words) / len(user_words) if user_words else 0
                coherence_score += min(overlap * 2, 1.0)  # Cap at 1.0
                pairs += 1
        
        return coherence_score / pairs if pairs > 0 else 0
    
    def evaluate_success_criteria(
        self,
        scenario: TestScenario,
        metrics: Dict[str, float],
        strategy_map: Dict[str, Any],
        agent_sequence: List[str]
    ) -> tuple[bool, List[str]]:
        """Evaluate if scenario meets success criteria"""
        failures = []
        
        # Default success criteria
        criteria = {
            'min_relevancy': 0.6,
            'min_completeness': 0.5,
            'min_routing_accuracy': 0.5,
            'min_coherence': 0.6,
            **scenario.success_criteria
        }
        
        # Check each criterion
        if metrics.get('answer_relevancy', 0) < criteria['min_relevancy']:
            failures.append(f"Answer relevancy {metrics.get('answer_relevancy', 0):.2f} < {criteria['min_relevancy']}")
        
        if metrics.get('strategy_map_completeness', 0) < criteria['min_completeness']:
            failures.append(f"Strategy map completeness {metrics.get('strategy_map_completeness', 0):.2f} < {criteria['min_completeness']}")
        
        if metrics.get('agent_routing_accuracy', 0) < criteria['min_routing_accuracy']:
            failures.append(f"Agent routing accuracy {metrics.get('agent_routing_accuracy', 0):.2f} < {criteria['min_routing_accuracy']}")
        
        if metrics.get('conversation_coherence', 0) < criteria['min_coherence']:
            failures.append(f"Conversation coherence {metrics.get('conversation_coherence', 0):.2f} < {criteria['min_coherence']}")
        
        passed = len(failures) == 0
        return passed, failures
    
    def generate_html_report(self):
        """Generate comprehensive HTML evaluation report"""
        template = Template('''
<!DOCTYPE html>
<html>
<head>
    <title>Strategy Coach Evaluation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .summary { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .scenario { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .metric { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .passed { background: #d4edda; color: #155724; }
        .failed { background: #f8d7da; color: #721c24; }
        .screenshot { max-width: 100%; margin: 10px 0; border: 1px solid #ddd; }
        .conversation { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; }
        .assistant { background: #f3e5f5; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Strategy Coach Evaluation Report</h1>
        <p>Generated: {{ timestamp }}</p>
        <p>Total Scenarios: {{ total_scenarios }} | Passed: {{ passed_scenarios }} | Failed: {{ failed_scenarios }}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Overall Summary</h2>
        <div class="metrics">
            <div class="metric">
                <div>Success Rate</div>
                <div class="metric-value">{{ success_rate }}%</div>
            </div>
            <div class="metric">
                <div>Avg Relevancy</div>
                <div class="metric-value">{{ avg_relevancy }}</div>
            </div>
            <div class="metric">
                <div>Avg Completeness</div>
                <div class="metric-value">{{ avg_completeness }}</div>
            </div>
            <div class="metric">
                <div>Avg Duration</div>
                <div class="metric-value">{{ avg_duration }}s</div>
            </div>
        </div>
    </div>
    
    {% for result in results %}
    <div class="scenario">
        <h2>{{ result.scenario.name }} 
            <span class="{% if result.passed %}passed{% else %}failed{% endif %}">
                {% if result.passed %}✅ PASSED{% else %}❌ FAILED{% endif %}
            </span>
        </h2>
        
        <p><strong>Description:</strong> {{ result.scenario.description }}</p>
        <p><strong>Session ID:</strong> {{ result.session_id }}</p>
        <p><strong>Duration:</strong> {{ result.duration_seconds|round(2) }}s</p>
        
        {% if not result.passed %}
        <div class="failed">
            <h3>Failure Reasons:</h3>
            <ul>
            {% for reason in result.failure_reasons %}
                <li>{{ reason }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <h3>📈 Metrics</h3>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Status</th>
            </tr>
            {% for metric, value in result.metrics.items() %}
            <tr>
                <td>{{ metric }}</td>
                <td>{{ "%.2f"|format(value) }}</td>
                <td>{% if value >= 0.7 %}✅{% elif value >= 0.5 %}⚠️{% else %}❌{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h3>🤖 Agent Sequence</h3>
        <p>{{ result.agent_sequence|join(' → ') }}</p>
        
        <h3>💬 Conversation Sample</h3>
        <div class="conversation">
            {% for msg in result.conversation_history[:4] %}
            <div class="message {{ msg.role }}">
                <strong>{{ msg.role|upper }}:</strong> {{ msg.content[:200] }}...
            </div>
            {% endfor %}
        </div>
        
        <h3>📸 Screenshots</h3>
        {% for screenshot in result.screenshots[:3] %}
        <img src="{{ screenshot }}" class="screenshot" alt="Screenshot">
        {% endfor %}
        
        <h3>🗺️ Strategy Map Summary</h3>
        <pre>{{ result.strategy_map|tojson(indent=2) }}</pre>
    </div>
    {% endfor %}
</body>
</html>
        ''')
        
        # Calculate aggregate metrics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        
        avg_metrics = {}
        for metric_name in ['answer_relevancy', 'strategy_map_completeness', 'conversation_coherence']:
            values = [r.metrics.get(metric_name, 0) for r in self.results]
            avg_metrics[metric_name] = sum(values) / len(values) if values else 0
        
        # Render report
        html = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_scenarios=total,
            passed_scenarios=passed,
            failed_scenarios=total - passed,
            success_rate=round((passed / total * 100) if total > 0 else 0, 1),
            avg_relevancy=round(avg_metrics.get('answer_relevancy', 0), 2),
            avg_completeness=round(avg_metrics.get('strategy_map_completeness', 0), 2),
            avg_duration=round(sum(r.duration_seconds for r in self.results) / total if total > 0 else 0, 1),
            results=self.results
        )
        
        # Save report
        report_path = REPORTS_DIR / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path.write_text(html)
        print(f"\n📄 Report generated: {report_path}")
        return str(report_path)


# Test Scenarios Definition
TEST_SCENARIOS = [
    TestScenario(
        name="Tech Startup Strategy",
        description="Complete strategy development for a B2B SaaS startup",
        initial_message="I'm founding a B2B SaaS startup focused on AI-powered customer analytics. Help me develop a comprehensive strategy.",
        expected_agents=["WHY", "Analogy", "Logic", "Open Strategy"],
        expected_topics=["mission", "market", "competitors", "implementation", "metrics"],
        conversation_turns=12,
        success_criteria={
            'min_relevancy': 0.7,
            'min_completeness': 0.6,
            'min_routing_accuracy': 0.6,
            'min_coherence': 0.7
        }
    ),
    TestScenario(
        name="Non-Profit Mission Alignment",
        description="Strategy for a non-profit focused on education",
        initial_message="We're a non-profit working on improving STEM education in underserved communities. Need strategic guidance.",
        expected_agents=["WHY", "Open Strategy", "Logic"],
        expected_topics=["mission", "impact", "stakeholders", "funding", "partnerships"],
        conversation_turns=10,
        success_criteria={
            'min_relevancy': 0.65,
            'min_completeness': 0.55,
            'min_routing_accuracy': 0.5,
            'min_coherence': 0.65
        }
    ),
    TestScenario(
        name="Enterprise Digital Transformation",
        description="Digital transformation strategy for traditional retail",
        initial_message="We're a traditional retail chain looking to transform digitally and compete with e-commerce giants.",
        expected_agents=["Analogy", "Logic", "Open Strategy", "WHY"],
        expected_topics=["digital", "transformation", "customer", "technology", "culture"],
        conversation_turns=15,
        success_criteria={
            'min_relevancy': 0.7,
            'min_completeness': 0.65,
            'min_routing_accuracy': 0.55,
            'min_coherence': 0.7
        }
    )
]


# Pytest fixtures and test functions
@pytest.fixture(scope="module")
async def evaluator():
    """Create and setup evaluator instance"""
    eval = StrategyCoachEvaluator(headless=True)
    await eval.setup()
    yield eval
    await eval.teardown()


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", TEST_SCENARIOS)
async def test_full_coaching_session(evaluator: StrategyCoachEvaluator, scenario: TestScenario):
    """Test complete coaching session for each scenario"""
    result = await evaluator.run_scenario(scenario)
    
    # Use DeepEval's assert_test for test case validation
    for i in range(0, len(result.conversation_history)-1, 2):
        if i+1 < len(result.conversation_history):
            test_case = LLMTestCase(
                input=result.conversation_history[i]["content"],
                actual_output=result.conversation_history[i+1]["content"],
                context=[json.dumps(result.strategy_map)]
            )
            
            metrics = [
                AnswerRelevancyMetric(threshold=scenario.success_criteria.get('min_relevancy', 0.6)),
                GEval(
                    name="Strategic Value",
                    criteria="Response provides actionable strategic insights",
                    threshold=0.6
                )
            ]
            
            assert_test(test_case, metrics)
    
    # Assert scenario-specific criteria
    assert result.passed, f"Scenario failed: {', '.join(result.failure_reasons)}"
    assert result.metrics['strategy_map_completeness'] >= scenario.success_criteria['min_completeness']
    assert result.metrics['agent_routing_accuracy'] >= scenario.success_criteria['min_routing_accuracy']
    assert result.metrics['conversation_coherence'] >= scenario.success_criteria['min_coherence']


@pytest.mark.asyncio
async def test_generate_evaluation_report(evaluator: StrategyCoachEvaluator):
    """Generate comprehensive evaluation report after all tests"""
    # Run all scenarios if not already run
    if not evaluator.results:
        for scenario in TEST_SCENARIOS:
            await evaluator.run_scenario(scenario)
    
    # Generate HTML report
    report_path = evaluator.generate_html_report()
    assert Path(report_path).exists()
    
    # Generate summary metrics for CI/CD
    summary = {
        "total_scenarios": len(evaluator.results),
        "passed": sum(1 for r in evaluator.results if r.passed),
        "failed": sum(1 for r in evaluator.results if not r.passed),
        "success_rate": sum(1 for r in evaluator.results if r.passed) / len(evaluator.results) if evaluator.results else 0,
        "timestamp": datetime.now().isoformat()
    }
    
    summary_path = REPORTS_DIR / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    
    # Assert minimum success rate for CI/CD gate
    assert summary["success_rate"] >= 0.8, f"Success rate {summary['success_rate']} below threshold 0.8"


if __name__ == "__main__":
    # Run evaluation manually
    async def main():
        evaluator = StrategyCoachEvaluator(headless=False)  # Show browser for debugging
        await evaluator.setup()
        
        try:
            for scenario in TEST_SCENARIOS:
                result = await evaluator.run_scenario(scenario)
                print(f"\n✅ Completed: {scenario.name}")
                print(f"   Passed: {result.passed}")
                print(f"   Metrics: {result.metrics}")
        finally:
            report_path = evaluator.generate_html_report()
            print(f"\n📊 Full report: {report_path}")
            await evaluator.teardown()
    
    asyncio.run(main())